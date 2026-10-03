"""Concrete host proof composition for one separately approved maintenance packet.

Heavy content checks precede preparation. The private dossier is bound through
observation.inventory.scan_sha256, then observation_sha256 in prepared inputs.
The independent coordinator rechecks original metadata, application ownership,
kernel holders, launch identities and effective settings before fence and stop.
No application imports, automatic recovery, implicit approval, or execute CLI.
OS/root operator are trusted; this is not an audit against compromised root.
"""
from dataclasses import asdict
from datetime import datetime, timezone
import json
import re
import time
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_stage_access as access
from scripts.vps.phase16_bot_retained_stage_remote import fingerprint

require=core.require
MAX_RECORD=16*1024*1024


def plan_from_json(value):
    try:
        value=json.loads(core.encoded(value))
        identity=dict(value.pop('identity'))
        identity['supplementary_gids']=tuple(identity['supplementary_gids'])
        objects=[]
        for item in value.pop('objects'):
            if item['children'] is not None:item['children']=tuple(item['children'])
            objects.append(access.AccessObject(**item))
        ancestors=tuple(access.Ancestor(**item) for item in value.pop('ancestors'))
        value['ordering']=tuple(value['ordering'])
        plan=access.AccessPlan(identity=access.ServiceIdentity(**identity),objects=tuple(objects),ancestors=ancestors,**value)
        require(plan.stage_root==access.STAGE_ROOT and plan.digest==access._digest(plan),'host_access_plan')
        require(0<len(plan.objects)<=40000 and len({i.path for i in plan.objects})==len(plan.objects),'host_access_plan')
        return plan
    except Exception:raise core.Stop('host_access_plan') from None


def _metadata(reader,plan):
    found={}
    for item in plan.objects:
        meta=reader.info(item.path)
        access._clear_acl(reader.acl_names(item.path))
        if item.children is not None:
            require(tuple(sorted(reader.entries(item.path)))==item.children,'host_stage_changed')
        if item.kind=='symlink':require(reader.readlink(item.path)==item.link_target,'host_stage_changed')
        found[item.path]=list(fingerprint(meta))
    ancestors=[]
    for name,meta,acl in reader.ancestors():
        access._clear_acl(acl);ancestors.append([name,list(fingerprint(meta))])
    reader.stable()
    return dict(objects=found,ancestors=ancestors)


def capture_stage(plan,reader):
    # Capture before content verification, compare after: no post-hash snapshot reset.
    before=_metadata(reader,plan)
    result=access.verify_access(plan,reader)
    require(result.status=='DAC_ACCESS_VERIFIED_NOT_HOST_ADMITTED','host_access_not_verified')
    require(_metadata(reader,plan)==before,'host_stage_changed')
    source={item.path:item.sha256 for item in plan.objects
            if item.path.startswith('source/app/') and item.kind=='file'}
    require(source and all(re.fullmatch('[0-9a-f]{64}',v or '') for v in source.values()),'host_stage_source')
    value=dict(schema='phase16.stage-continuity.v1',scope='VERIFIED_CONTENT_THEN_METADATA_CONTINUITY',
        plan=asdict(plan),metadata=before,source_sha256=core.digest(source))
    require(len(core.encoded(value))<=MAX_RECORD,'host_record_size')
    return value


def check_stage(record,reader):
    require(set(record)=={'schema','scope','plan','metadata','source_sha256'} and
        record['schema']=='phase16.stage-continuity.v1' and
        record['scope']=='VERIFIED_CONTENT_THEN_METADATA_CONTINUITY','host_stage_record')
    plan=plan_from_json(record['plan'])
    require(_metadata(reader,plan)==record['metadata'],'host_stage_changed')
    source={item.path:item.sha256 for item in plan.objects
            if item.path.startswith('source/app/') and item.kind=='file'}
    require(source and core.digest(source)==record['source_sha256'],'host_stage_record')
    return record['source_sha256']


def dossier_binding(observation,ownership,dossier):
    from scripts import phase16_bot_maintenance_binding as binding
    require(isinstance(dossier,dict) and dossier.get('schema')=='phase16.host-admission.v1','host_dossier')
    require(len(core.encoded(dossier))<=MAX_RECORD,'host_record_size')
    for field in ('operation_id','boot_id','target_binding_sha256'):
        require(dossier.get(field)==observation.get(field)==ownership.get(field),'host_dossier_binding')
    require(re.fullmatch('[0-9a-f]{64}',dossier.get('approval_scope_sha256','')),'host_dossier_binding')
    require(dossier['writer_initial']['evidence']['provenance']=='LINUX_PROCFS_ROOT','host_writer_provenance')
    require(binding.timestamp(dossier['writer_declaration']['valid_until'])>=binding.timestamp(ownership['valid_until']),
        'host_writer_window')
    selected={k:dossier['effective_settings'][k] for k in
        ('vps_apply_enabled','awg3_bootstrap_enabled','admission_seconds','network_cidr')}
    selected['startup_bound_seconds']=dossier['startup_assessment']['startup_observation_budget_seconds']
    require(core.encoded(selected)==core.encoded(observation['settings']) and
        core.encoded(observation['rollback'])==core.encoded(dossier['legacy_runtime']['rollback']), 'host_cross_binding')
    for field in ('writers','other_writer_classes','process_scan'):
        require(observation['inventory'][field]==dossier['writer_initial']['inventory'][field],'host_cross_binding')
    return core.digest(dict(application_writer_evidence=dossier['writer_initial']['evidence'],
                            host_dossier_sha256=core.digest(dossier)))


def prepare_bound(observation,ownership,dossier,*,now):
    from scripts import phase16_bot_maintenance_binding as binding
    observation=json.loads(core.encoded(observation))
    observation['inventory']['scan_sha256']=dossier_binding(observation,ownership,dossier)
    prepared=binding.prepare_inputs(observation,ownership,now=now)
    validate_saved(prepared,observation,ownership,dossier)
    return prepared,observation


def validate_saved(prepared,observation,ownership,dossier):
    from scripts import phase16_bot_maintenance_binding as binding
    target=prepared['target_contract']
    binding.validate_prepared(prepared,now=target['observed_at'])
    require(core.digest(observation)==target['observation_sha256'] and
            core.digest(ownership)==target['ownership_sha256'],'host_saved_binding')
    require(observation['inventory']['scan_sha256']==dossier_binding(observation,ownership,dossier),'host_saved_binding')


def unit_facts(client):
    from scripts import phase16_bot_service_operations as services
    result={};identities={}
    for unit in (core.BOT,core.WEB):
        before=client.show(unit)
        require(before['LoadState']=='loaded' and before['ActiveState']=='active' and
            before['SubState']=='running' and before['Result']=='success' and
            before['NeedDaemonReload']=='no' and before['Type']==('notify' if unit==core.BOT else 'simple'),
            'host_unit_state')
        require(before['MainPID'].isdigit() and int(before['MainPID'])>0 and
                re.fullmatch('[0-9a-f]{32}',before['InvocationID']),'host_unit_identity')
        def prop(name,kind):return client.bus_property(unit,'Service',name,kind)
        start,stop=prop('TimeoutStartUSec','t'),prop('TimeoutStopUSec','t')
        require(type(start) is int and type(stop) is int and start%1000000==stop%1000000==0,'host_unit_budget')
        enabled=client.bus_property(unit,'Unit','UnitFileState','s')
        result[unit]=dict(baseline=dict(active='active',enabled=enabled,masked=False,
            start_seconds=start//1000000,stop_seconds=stop//1000000,restart=prop('Restart','s')),
            user=prop('User','s'),group=prop('Group','s'),launch_sha256=services.launch_fingerprint(client,unit),
            kill_mode=prop('KillMode','s'),kill_signal=prop('KillSignal','i'),final_kill_signal=prop('FinalKillSignal','i'))
        require(result[unit]['user']==result[unit]['group']=='amn2-spain','host_unit_identity')
        require(client.show(unit)==before,'host_unit_changed')
        identities[unit]={k:before[k] for k in ('Id','MainPID','InvocationID','Type','NRestarts','ControlGroup')}
    return result,identities


def saved_records(supervisor):
    from scripts.phase16_bot_coordinator_process import bounded_read
    records={}
    for name in ('host-admission','observation','ownership'):
        raw=bounded_read(supervisor.directory/(name+'.json'),MAX_RECORD,private=True)
        value=json.loads(raw)
        require(raw==core.encoded(value),'host_record_encoding');records[name]=value
    return records


class HostAdmission:
    def __init__(self,supervisor):
        from scripts import phase16_bot_maintenance_jobs as jobs
        self.supervisor=supervisor;self.client=supervisor.client
        self.records=saved_records(supervisor)
        self.prepared=jobs.read_json(supervisor.directory/'worker-context.json')['prepared']
        validate_saved(self.prepared,self.records['observation'],self.records['ownership'],self.records['host-admission'])
        self.proof=self.records['host-admission']
    def source(self):
        with access.UnixStageReader() as reader:
            return check_stage(self.proof['stage_continuity'],reader)
    def __call__(self,prepared):
        from scripts import phase16_bot_effective_settings as settings
        from scripts import phase16_bot_legacy_runtime_proof as old
        from scripts import phase16_bot_writer_admission as writers
        from scripts import phase16_bot_maintenance_binding as binding
        from scripts import phase16_bot_maintenance_jobs as jobs
        require(prepared==self.prepared and saved_records(self.supervisor)==self.records,'host_saved_changed')
        binding.validate_prepared(prepared,now=datetime.fromtimestamp(self.supervisor.utc_now(),timezone.utc).isoformat())
        require(jobs.boot_id(self.client)==prepared['target_contract']['boot_id'],'boot_changed')
        require(settings.collect_live(self.client)==self.proof['effective_settings'],'host_settings_changed')
        units,identities=unit_facts(self.client)
        require(units==self.records['observation']['units'] and identities==self.proof['units_identity'],'host_unit_changed')
        self.source();old.check_saved(self.proof['legacy_runtime'])
        from scripts import phase16_bot_service_access_probe as probe
        current=probe.LinuxObserver(self.client.run).snapshot(5)
        plan=plan_from_json(self.proof['stage_continuity']['plan'])
        probe.validate_snapshot(current,plan.identity)
        require(self.proof['service_access']['status']=='KERNEL_STAGE_ACCESS_OBSERVED_NOT_HOST_ADMITTED' and
                self.proof['service_access']['plan_sha256']==plan.digest and
                core.digest(current)==self.proof['service_access']['bot_identity_sha256'],'host_access_context_changed')
        writer=writers.collect_writer_admission(self.proof['writer_declaration'],
            operation_id=prepared['target_contract']['operation_id'],boot_id=prepared['target_contract']['boot_id'],
            target_binding_sha256=binding.TARGET,approval_scope_sha256=self.proof['approval_scope_sha256'],
            unit_reader=self.client.show,utc_now=self.supervisor.utc_now,clock=self.supervisor.clock)
        require(writer['evidence']['provenance']=='LINUX_PROCFS_ROOT' and
                writer['evidence']['units']==self.proof['writer_initial']['evidence']['units'],'host_writer_changed')
        require(core.encoded(writer['evidence']['database_identities'])==core.encoded(self.proof['writer_initial']['evidence']['database_identities']),
                'host_database_identity_changed')
        # Pending work is checked initially in a private RO namespace and again by
        # old_state after BOTH services stop. It is never inferred from no FD holder.
        require(saved_records(self.supervisor)==self.records,'host_saved_changed')
        return prepared['prepared_sha256']


def bind(supervisor):
    from scripts import phase16_bot_startup_budget as startup
    from scripts import phase16_bot_maintenance_sequence as sequence
    admission=HostAdmission(supervisor)
    def factory(guard):
        require(guard is admission,'host_guard_binding')
        data=supervisor.data;proof=admission.proof
        operations=startup.BudgetedServiceOperations(data.journal,data.client,data.fence,data,
            expected_username=proof['effective_settings']['expected_username'],source_verifier=admission.source,
            web_port=proof['effective_settings']['web_port'],clock=data.clock,sleep=data.sleep,
            startup_observation_budget_seconds=proof['startup_assessment']['startup_observation_budget_seconds'])
        return sequence.MaintenanceSequence(operations,host_guard=guard)
    return dict(admission=admission,sequence_factory=factory)
