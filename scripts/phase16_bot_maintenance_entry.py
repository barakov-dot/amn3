"""Complete preparation and manager-owned sequence entry; exact packet only.

No default execution. Called from the checksum-bound uploaded code bootstrap.
Permission changes may precede the service fence; a failure retains their claim
and plan, leaves old services alone, and never retries or restores automatically.
"""
from dataclasses import asdict
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import sys
import time
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_binding as binding
from scripts import phase16_bot_maintenance_linux as linux
from scripts import phase16_bot_maintenance_jobs as jobs
from scripts import phase16_bot_coordinator_process as coordinator
from scripts import phase16_bot_candidate_admission as candidate
from scripts import phase16_bot_effective_settings as settings
from scripts import phase16_bot_host_admission as host
from scripts import phase16_bot_legacy_runtime_proof as old
from scripts import phase16_bot_pending_admission as pending
from scripts import phase16_bot_writer_admission as writers
from scripts import phase16_bot_stage_access as access
from scripts import phase16_bot_stage_access_apply as apply
from scripts import phase16_bot_service_access_probe as probe
from scripts import phase16_bot_startup_budget as startup
from scripts import phase16_legacy_stop_policy as legacy

APPROVAL='PHASE16_BOT_MAINTENANCE_20261003_001'
OPERATION='phase16-bot-maintenance-20261003-001'
BOOT='8ae340d2-dab8-4dad-b1db-09283cc51bd9'
PREFLIGHT_SECONDS=600
REMOTE_SECONDS=1560
EXTRA=tuple('scripts/'+name+'.py' for name in (
    'phase16_bot_bootstrap_provenance','phase16_bot_candidate_admission','phase16_bot_effective_settings',
    'phase16_bot_host_admission','phase16_bot_legacy_runtime_proof','phase16_bot_pending_admission',
    'phase16_bot_runtime_content','phase16_bot_stage_access','phase16_bot_stage_access_apply',
    'phase16_bot_service_access_probe','phase16_bot_startup_budget','phase16_bot_writer_admission',
    'phase16_bot_maintenance_entry','phase16_bot_maintenance_storage'))+('scripts/vps/phase16_bot_integration_readback_v3.py',)
RESOURCES=tuple('research/amn2/'+name for name in (
    'phase16-bot-maintenance-target-manifest-2026-09-30.json',
    'phase16-bot-stage-readback-manifest-2026-09-29.json',
    'phase16-bot-stage-readback-execution-001-2026-09-29.json',
    'phase16-bot-stage-readback-inventory-2026-09-29.json',
    'phase16-bot-integration-manifest-v3-6e68235.json'))


def request():
    # This is a proposed approval declaration, never inferred from /GO or sole SSH.
    return dict(approval=APPROVAL,operation_id=OPERATION,expected_boot_id=BOOT,
        target_binding_sha256=binding.TARGET,ownership_seconds=2700,accepted_owner_statement=True)


def validate_request(value,approved_manifest_sha256):
    core.require(value.get('accepted_owner_statement') is True,'packet_owner_declaration')
    core.require(value==request() and re.fullmatch('[0-9a-f]{64}',approved_manifest_sha256),'packet_binding')


def iso(epoch):return datetime.fromtimestamp(epoch,timezone.utc).isoformat()


def owner_records(value,scope_sha,now):
    validate_request(value,scope_sha);begin=int(now);end=iso(begin+value['ownership_seconds'])
    common=dict(operation_id=OPERATION,target_binding_sha256=binding.TARGET,boot_id=BOOT)
    ownership=dict(schema='phase16.maintenance-ownership.v1',**common,valid_until=end,
        exclusive_maintenance_owner=True,external_pollers_excluded=True,manual_cli_paused=True)
    declaration=dict(schema='phase16.application-writer-declaration.v1',**common,approval_scope_sha256=scope_sha,
        declared_at=iso(begin),valid_until=end,accepted_within_maintenance_approval=True,
        application_inventory_complete=True,writers=writers.TOPOLOGY,
        other_application_writers=dict(cron='absent',agent='absent',timer='absent',socket='absent',manual_cli='paused'),
        external_application_pollers='excluded',trust_boundary='EXISTING_OS_AND_ROOT_OPERATOR',scope='APPLICATION_ONLY')
    writers.validate_declaration(declaration,**common,approval_scope_sha256=scope_sha,now=now)
    return ownership,declaration


def prepare(client,code,directory,value,scope_sha,*,utc_now=time.time,clock=time.monotonic,artifact_pins=None):
    """Only called after exact approval and code verification; no implicit reuse."""
    started=clock();deadline=started+PREFLIGHT_SECONDS
    ownership,declaration=owner_records(value,scope_sha,utc_now())
    def guard():
        core.require(clock()<deadline,'preflight_deadline')
        core.require(jobs.boot_id(client)==BOOT,'boot_changed')
        core.require(binding.timestamp(ownership['valid_until']).timestamp()-utc_now()>=1230,'ownership_window')
    guard()
    units,identities=host.unit_facts(client)
    inventory=(code/binding.BOUND['inventory'][0]).read_bytes()
    proof=candidate.collect_live(client,inventory);guard()
    original=old.collect_live()
    try:
        initial_pending=pending.collect_live(client,str(code),expected_artifacts=artifact_pins);guard()
        core.require(initial_pending['pending_operations']=='none_observed','pending_operations_present')
        initial_writers=writers.collect_writer_admission(declaration,operation_id=OPERATION,boot_id=BOOT,
            target_binding_sha256=binding.TARGET,approval_scope_sha256=scope_sha,
            unit_reader=client.show,utc_now=utc_now,clock=clock);guard()
        core.require(initial_writers['evidence']['provenance']=='LINUX_PROCFS_ROOT','host_writer_provenance')
        core.require(host.unit_facts(client)==(units,identities),'host_unit_changed')
        # All owner/pending/writer/content checks precede the first permission syscall.
        application=apply.ApplyBinding(OPERATION,binding.TARGET,BOOT,scope_sha,proof.access_plan.digest)
        with apply.UnixJournal(str(directory)) as journal:
            applied=apply.execute(proof.access_plan,application,journal=journal)
        core.require(applied.status=='APPLIED_DAC_VERIFIED_NOT_HOST_ADMITTED','stage_access_not_applied');guard()
        plan_path=directory/apply.journal_name(application,'plan')
        service_access=probe.probe_service_access(proof.access_plan,authorized_plan_sha256=proof.access_plan.digest,
            plan_record_path=plan_path,run=client.run,clock=clock);guard()
        with access.UnixStageReader() as tree:continuity=host.capture_stage(proof.access_plan,tree)
        original.check();old_record=original.record();guard()
        core.require(settings.collect_live(client)==proof.settings,'host_settings_changed')
        core.require(host.unit_facts(client)==(units,identities),'host_unit_changed')
        fresh_writers=writers.collect_writer_admission(declaration,operation_id=OPERATION,boot_id=BOOT,
            target_binding_sha256=binding.TARGET,approval_scope_sha256=scope_sha,
            unit_reader=client.show,utc_now=utc_now,clock=clock);guard()
        assessment=startup.assess_budget(admission_seconds=proof.settings['admission_seconds'],
            manager_start_seconds=units[core.BOT]['baseline']['start_seconds'])
        dossier=dict(schema='phase16.host-admission.v1',operation_id=OPERATION,boot_id=BOOT,
            target_binding_sha256=binding.TARGET,approval_scope_sha256=scope_sha,
            writer_declaration=declaration,writer_initial=fresh_writers,stage_continuity=continuity,
            legacy_runtime=old_record,effective_settings=proof.settings,units_identity=identities,
            service_access=service_access,startup_assessment=assessment,
            bootstrap_provenance=proof.bootstrap_provenance,pending_initial=initial_pending)
        selected={k:proof.settings[k] for k in ('vps_apply_enabled','awg3_bootstrap_enabled','admission_seconds','network_cidr')}
        selected['startup_bound_seconds']=assessment['startup_observation_budget_seconds']
        observation=dict(schema='phase16.maintenance-inputs.v1',operation_id=OPERATION,
            target_binding_sha256=binding.TARGET,boot_id=BOOT,observed_at=iso(utc_now()),stage=proof.stage_result,
            units=units,inventory=fresh_writers['inventory'],settings=selected,rollback=original.rollback,
            pending_operations=initial_pending['pending_operations'])
        prepared,observation=host.prepare_bound(observation,ownership,dossier,now=iso(utc_now()))
        # Old commit is the accepted policy reference; the actual two source pins
        # and complete continuity snapshot are proven, deployed Git is not guessed.
        policy=legacy.bind(prepared,packet_sha256=scope_sha,old_commit=legacy.OLD_COMMIT,
            old_handlers_sha256=legacy.OLD_HANDLERS,old_workflows_sha256=legacy.OLD_WORKFLOWS)
        for name,record in [('host-admission',dossier),('observation',observation),('ownership',ownership)]:
            core.write_new(directory/(name+'.json'),core.encoded(record))
        journal=core.Journal.create(directory/'journal',prepared['coordinator_manifest'])
        context=dict(prepared=prepared,artifacts_sha256_lf=linux.worker_artifacts(code),legacy_stop_policy=policy)
        raw=core.encoded(context);core.require(len(raw)<=16384,'worker_context_size')
        core.write_new(directory/'worker-context.json',raw)
        fence=core.SystemdFence(Path('/'),journal.manifest,client.control)
        data=jobs.DataJobSupervisor(journal,client,fence,code=str(code),context_sha256=hashlib.sha256(raw).hexdigest(),
            utc_now=utc_now,clock=clock)
        runner=coordinator.CoordinatorSupervisor(data,entry_module='scripts.phase16_bot_host_admission',extra_files=EXTRA)
        guard();runner.guard(coordinator.WAIT_SECONDS)
        return runner
    finally:original.close()


def execute(manifest,expected_sha,code,directory,*,overall_deadline):
    """Linux-only entry invoked by a verified packet; never called by preview."""
    core.require(sys.platform=='linux' and os.geteuid()==0,'linux_root_required')
    core.require(core.digest(manifest)==expected_sha,'packet_binding')
    validate_request(manifest['request'],expected_sha)
    code,directory=Path(code),Path(directory)
    core.require(str(directory)==binding.target_paths(OPERATION)['maintenance_directory'] and
        code==directory/'code' and Path(__file__).resolve().parents[1]==code,'packet_directory')
    run_parent=Path('/run/phase16')
    from scripts.phase16_bot_maintenance_storage import check_owned_parent
    for path in (run_parent,*run_parent.parents):
        core.require(not path.is_symlink(),'runtime_parent');check_owned_parent(path.lstat(),str(path))
    core.require(type(overall_deadline) in (int,float) and time.monotonic()<overall_deadline<=time.monotonic()+REMOTE_SECONDS,'packet_deadline')
    preflight_budget=min(PREFLIGHT_SECONDS,int(overall_deadline-time.monotonic()-coordinator.WAIT_SECONDS-15))
    core.require(preflight_budget>0,'packet_deadline')
    original_alarm=signal.getsignal(signal.SIGALRM)
    def alarm(*unused):raise core.Stop('packet_deadline')
    signal.signal(signal.SIGALRM,alarm);signal.alarm(preflight_budget)
    began=time.monotonic();result=None
    try:
        client=linux.SystemdClient(linux.BoundedCommand(maximum=65536))
        runner=prepare(client,code,directory,manifest['request'],expected_sha,artifact_pins=manifest['files_sha256_lf'])
        remaining=overall_deadline-time.monotonic()
        core.require(remaining>coordinator.WAIT_SECONDS,'packet_deadline')
        signal.alarm(max(1,int(remaining)))
        result=runner.execute()
    except Exception:
        result=dict(status='STOP_OR_UNKNOWN_NO_RETRY',reason='packet_precondition_or_execution_failed',
            automatic_recovery='DISABLED',live_acceptance='NOT_ESTABLISHED',
            recovery_route='INSPECT_RETAINED_INTENTS_AND_MANAGER_STATE')
    finally:
        signal.alarm(0);signal.signal(signal.SIGALRM,original_alarm)
    receipt=dict(schema='phase16.maintenance-packet-result.v1',approval=APPROVAL,operation_id=OPERATION,
        manifest_sha256=expected_sha,target_binding_sha256=binding.TARGET,result=result,
        awg2='UNTOUCHED',package016='UNCHANGED',general_issuance='DISABLED',automatic_replay=False)
    core.write_new(directory/'packet-result.json',core.encoded(receipt))
    print(core.encoded(receipt).decode('ascii'),end='',flush=True)
    return 0 if result['status']=='SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE' else 3


def preview():return dict(status='EXACT_APPROVAL_REQUIRED',authorized=False,ssh_attempts=0)
if __name__=='__main__':print(json.dumps(preview()))
