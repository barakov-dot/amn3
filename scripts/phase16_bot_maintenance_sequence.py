"""One pass through concrete maintenance adapters; no CLI or live admission.

A separately approved, manager-owned runner must supply a real host_guard which
collects current provenance/settings/access/writer/ownership evidence and returns
this exact prepared-input digest. A digest or caller-supplied flags alone are not
host proof. This module supplies sequencing, durable claims and failure routing;
it neither implements that collector nor creates the persistent Linux process.
"""
import contextlib
from datetime import datetime, timezone
import json
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_binding as binding
from scripts import phase16_bot_maintenance_jobs as jobs
from scripts import phase16_bot_maintenance_linux as linux
from scripts import phase16_bot_service_operations as services
from scripts import phase16_legacy_stop_policy as legacy

require=core.require
BUDGETS={action:(jobs.JOB_SECONDS if action in jobs.ACTIONS else linux.ACTION_SECONDS[action])
         for action in core.ACTIONS}
# Only literal internal reason codes are retained; raw exception text is secret.
SAFE_REASONS=frozenset(('sequence_context','boot_changed','sequence_deadline','ownership_window',
    'sequence_step_deadline','host_admission_missing','original_launch_changed','candidate_source',
    'admission_changed','old_process_changed','fence_lost','unclean_stop','processes_remain',
    'data_job_not_complete','data_completion_binding','service_verification','service_action_deadline',
    'candidate_source_changed','candidate_changed','service_changed','web_readiness','admission_missing',
    'migration_receipt','service_receipt_chain','job_context_binding','stop_witness_changed',
    'command_deadline','command_failed','command_output_limit','manager_job_unknown_no_retry',
    'job_unknown_no_retry','job_policy','job_result_binding','inputs_window','inputs_ownership',
    'candidate_dropin','candidate_not_loaded','candidate_command','candidate_identity','web_launch_changed'))


class MaintenanceSequence:
    def __init__(self, operations, *, host_guard):
        require(isinstance(operations,services.ServiceOperations) and callable(host_guard),'sequence_adapters')
        self.services=operations
        self.journal,self.client,self.fence=operations.journal,operations.client,operations.fence
        self.supervisor=operations.supervisor
        self.clock,self.utc_now=operations.clock,self.supervisor.utc_now
        self.host_guard=host_guard
        self.target=self.supervisor.context()
        context=jobs.read_json(self.journal.directory.parent/'worker-context.json')
        self.prepared=json.loads(core.encoded(context['prepared']))
        self.policy=json.loads(core.encoded(context['legacy_stop_policy']))
        require(self.target==self.prepared['target_contract'],'sequence_context')
        self.total_seconds=sum(BUDGETS.values())
        self.directory=self.journal.directory.parent
        self.claim_path=self.directory/'sequence-claim.json'
        self.result_path=self.directory/'sequence-result.json'
        self.initial_identity=None
        self.initial_source=None

    def common(self):
        require(self.supervisor.context()==self.target,'sequence_context')
        require(jobs.boot_id(self.client)==self.journal.manifest['boot_id'],'boot_changed')
        require(self.clock()<self.deadline,'sequence_deadline')
        remaining=binding.timestamp(self.target['ownership_valid_until']).timestamp()-self.utc_now()
        require(remaining>=linux.RECOVERY_RESERVE,'ownership_window')
        return remaining

    @contextlib.contextmanager
    def step_budget(self,action):
        deadline=min(self.deadline,self.clock()+BUDGETS[action])
        original=self.client.run
        def run(argv,seconds):
            remaining=deadline-self.clock()
            require(remaining>0,'sequence_step_deadline')
            value=original(argv,min(seconds,remaining))
            require(self.clock()<deadline,'sequence_step_deadline')
            return value
        self.client.run=run
        try:
            self.common()
            yield
            require(self.clock()<deadline,'sequence_step_deadline')
        finally:self.client.run=original

    def admission(self):
        now=datetime.fromtimestamp(self.utc_now(),timezone.utc).isoformat()
        binding.validate_prepared(self.prepared,now=now)
        # No boolean shortcut: the independent collector must bind this context.
        require(self.host_guard(json.loads(core.encoded(self.prepared)))==self.prepared['prepared_sha256'],
                'host_admission_missing')
        self.common()
        identities={unit:self.services.identity(unit) for unit in linux.UNITS}
        for unit in linux.UNITS:
            require(services.launch_fingerprint(self.client,unit)==self.target['original_launch_sha256'][unit],
                    'original_launch_changed')
        fingerprint=self.services.source_verifier()
        require(isinstance(fingerprint,str) and len(fingerprint)==64
                and all(c in '0123456789abcdef' for c in fingerprint),'candidate_source')
        if self.initial_identity is None:
            self.initial_identity,self.initial_source=identities,fingerprint
        else:
            require(identities==self.initial_identity and fingerprint==self.initial_source,'admission_changed')

    def stop(self):
        # Web first closes the second application writer before stopping polling.
        for unit in (core.WEB,core.BOT):
            self.common()
            require(self.client.fence_effective(self.fence),'fence_lost')
            require(self.services.identity(unit)==self.initial_identity[unit],'old_process_changed')
            require(services.launch_fingerprint(self.client,unit)==self.target['original_launch_sha256'][unit],
                    'original_launch_changed')
            self.fence.stop(unit,self.journal)
        jobs.save_stop_witness(self.journal,self.client,self.fence)

    def verify_data(self,action):
        jobs.check_stop_witness(self.journal,self.client,self.fence)
        claim=jobs.validate_claim(self.journal,action,self.supervisor.context_sha256)
        paths=jobs.job_paths(self.journal,action)
        result=jobs.load_signed(paths['result']);complete=jobs.load_signed(paths['complete'])
        data=jobs.load_signed(self.directory/'receipts'/(action+'.json'))
        state=self.supervisor.query(action,5)
        require(state['ActiveState']=='active' and state['SubState']=='exited' and state['MainPID']=='0'
                and state['Result']=='success' and state['ExecMainCode']=='1' and state['ExecMainStatus']=='0',
                'data_job_not_complete')
        require(result.get('schema')=='phase16.job-result.v1' and result.get('result')=='DATA_VERIFIED'
                and result.get('claim_sha256')==claim['sha256']
                and result.get('boot_id')==self.journal.manifest['boot_id']
                and result.get('invocation')==state['InvocationID']
                and result.get('data_receipt_sha256')==data['sha256']
                and data.get('binding')==self.journal.binding and data.get('action')==action
                and data.get('intent_sha256')==self.journal.events[-1]['sha256']
                and complete==dict(schema='phase16.job-complete.v1',claim_sha256=claim['sha256'],
                    result_sha256=result['sha256'],invocation=state['InvocationID'],sha256=complete['sha256']),
                'data_completion_binding')
        return True

    def before_mutation(self):
        self.common()
        require(self.clock()<self.step_deadline,'sequence_step_deadline')

    def operation(self,action):
        # Recheck after durable intent fsync as well as after potentially slow admission.
        self.before_mutation()
        if action=='fence':self.fence.install(self.journal)
        elif action=='stop':self.stop()
        elif action in jobs.ACTIONS:self.supervisor.execute(action)
        else:getattr(self.services,action)()

    def verify(self,action):
        self.common()
        if action=='fence':
            require(self.client.fence_effective(self.fence),'fence_lost')
            require({unit:self.services.identity(unit) for unit in linux.UNITS}==self.initial_identity,
                    'old_process_changed')
        elif action=='stop':jobs.check_stop_witness(self.journal,self.client,self.fence)
        elif action in jobs.ACTIONS:self.verify_data(action)
        else:require(self.services.verify(action) is True,'service_verification')
        # Included before the durable action_done, not merely after it.
        self.common()
        require(self.clock()<self.step_deadline,'sequence_step_deadline')
        return True

    def run(self):
        fresh=core.Journal.load(self.journal.directory,self.journal.manifest)
        require(fresh.events==self.journal.events and fresh.phase=='prepared','sequence_already_started')
        require(not any(p.exists() or p.is_symlink() for p in (self.claim_path,self.result_path)),'sequence_already_claimed')
        # This durable claim precedes any manager request. It survives interrupts
        # even before fence_intent, and prohibits a new run under the same identity.
        jobs.write_signed(self.claim_path,dict(schema='phase16.sequence-claim.v1',
            binding=self.journal.binding,context_sha256=self.supervisor.context_sha256,
            prepared_sha256=self.prepared['prepared_sha256'],legacy_policy_sha256=self.policy['sha256']))
        self.deadline=self.clock()+self.total_seconds
        try:
            require(self.common()>=self.total_seconds+linux.RECOVERY_RESERVE,'ownership_window')
            for action in core.ACTIONS:
                self.step_deadline=min(self.deadline,self.clock()+BUDGETS[action])
                with self.step_budget(action):
                    if action in ('fence','stop'):self.admission()
                    self.before_mutation()
                    self.journal.perform(action,lambda a=action:self.operation(a),lambda a=action:self.verify(a))
            result=dict(status='SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE',phase=self.journal.phase,
                candidate_start_requested=True,recovery_route='NOT_REQUIRED',automatic_recovery='DISABLED',
                live_acceptance='NOT_ESTABLISHED',reason='all_operations_verified')
        except Exception as error:
            # Never emit subprocess exception text, environment or application logs.
            # KeyboardInterrupt/SystemExit deliberately propagate, leaving intent.
            try:route=legacy.recovery(self.journal,self.policy,self.prepared)
            except Exception:route='PRESERVE_DB_MANUAL_RECOVERY' if self.journal.candidate_requested else 'HOLD_FENCE_MANUAL_RECOVERY'
            reason=(error.args[0] if isinstance(error,core.Stop) and len(error.args)==1
                    and isinstance(error.args[0],str) and error.args[0] in SAFE_REASONS
                    else 'sequence_precondition_or_operation_failed')
            result=dict(status='STOP',phase=self.journal.phase,candidate_start_requested=self.journal.candidate_requested,
                recovery_route=route,automatic_recovery='DISABLED',live_acceptance='NOT_ESTABLISHED',
                reason=reason)
        try:
            jobs.write_signed(self.result_path,dict(schema='phase16.sequence-result.v1',
                claim_sha256=jobs.load_signed(self.claim_path)['sha256'],binding=self.journal.binding,
                final_event_sha256=self.journal.events[-1]['sha256'],result=result))
        except Exception:raise core.Stop('sequence_result_unpersisted') from None
        return result
