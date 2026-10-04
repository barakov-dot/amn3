"""Proposed one-shot two-file seal plus original readonly candidate collector.

Preview has zero egress. A new exact approval binds state/checksums. Consumed
packets, original57, parent/stage DAC, app/DB/services and maintenance are retained.
"""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts import phase16_bot_private_boundary_readback as predecessor
from scripts import phase16_bot_private_seal as core
v1=predecessor.v2.v1
base=predecessor.base
packet=predecessor.packet
APPROVAL='PHASE16_CANDIDATE_PRIVATE_SEAL_20261004_001'
OP=core.OP
SCHEMA='phase16.private-seal.v1'
TRIGGER=ROOT/'research/amn2/phase16-bot-private-boundary-readback-execution-001-2026-10-04.json'
TRIGGER_SHA='b27f2fec73e69d758bbe4dd6069b3016841bbfb61510d0b8339d7a1bc35752fe'
FROZEN={**predecessor.FROZEN_HELPERS,'scripts/phase16_bot_ancestor_repair_v2_gate.py':predecessor.FROZEN_V2_SHA,'scripts/phase16_bot_private_boundary_readback.py':'58caae4e7e11a9d5defbb733af537078794287547d480b2ec33888fd81bb6551'}
MANIFEST=ROOT/'research/amn2/phase16-bot-private-seal-manifest-2026-10-04.json'
EVIDENCE=Path('C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-private-seal-20261004/execution-001')
REMOTE_SECONDS=180
TRANSPORT_SECONDS=210
REMOTE=r'''
def main(approval):
    global AUDIT_CREATION_ATTEMPTED,INSTALLED
    AUDIT_CREATION_ATTEMPTED=False;INSTALLED=None;COMPONENTS.clear()
    result=dict(schema=SCHEMA,approval=APPROVAL,original_manifest_sha256=ORIGINAL,target_binding_sha256=TARGET,trigger_execution_sha256=TRIGGER_SHA,status='STOP_NO_REMOTE_CHANGE',reason='platform',audit_creation_attempted=False,operation=None,component_steps={},runtime_installed=None,database_open=0,service_actions=0,app_imports=0,stage_install=0,activation=False,replay_allowed=False)
    previous=None
    try:
        if sys.platform!='linux' or os.geteuid()!=0:raise ValueError('platform')
        if approval!=APPROVAL:raise ValueError('approval')
        import grp,pwd
        remaining=int(READBACK_STARTED+REMOTE_SECONDS-time.monotonic())
        if remaining<1:raise ReadbackDeadline('deadline')
        previous=signal.getsignal(signal.SIGALRM)
        def alarm(*unused):raise ReadbackDeadline('deadline')
        signal.signal(signal.SIGALRM,alarm);signal.alarm(remaining)
        if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=BOOT:raise ValueError('boot_changed')
        _phase16_import_root(DIRECTORY+'/code',PINS,ORIGINAL)
        from scripts import phase16_bot_candidate_admission as candidate
        from scripts import phase16_bot_maintenance_linux as linux
        from scripts import phase16_bot_maintenance_storage as storage
        from scripts.phase16_bot_stage_access_apply import UnixJournal
        client=linux.SystemdClient(linux.BoundedCommand(maximum=65536));accounts=candidate.settings.RootSettingsReader()
        def properties():return {u:{k:client.bus_property(u,'Service',k,s) for k,s in candidate.IDENTITY_FIELDS.items()} for u in UNITS[:2]}
        initial=properties();identity=candidate.local_identity(accounts('/etc/passwd'),accounts('/etc/group'),initial[UNITS[0]])
        if initial[UNITS[0]]!=initial[UNITS[1]] or (identity.uid,identity.gid,identity.supplementary_gids)!=(61212,61212,(61212,)):raise ValueError('repair_identity')
        def guard():
            if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=BOOT or properties()!=initial or unit_states()!=EXPECTED_UNITS:raise ValueError('repair_continuity')
            candidate.local_identity(accounts('/etc/passwd'),accounts('/etc/group'),initial[UNITS[0]])
            v1_group_check(accounts('/etc/passwd'),accounts('/etc/group'))
            local=pwd.getpwnam('amn2-spain');group=grp.getgrgid(61212);all_users=pwd.getpwall()
            if len(all_users)>4096 or (local.pw_uid,local.pw_gid)!=(61212,61212) or group.gr_name!='amn2-spain' or not set(group.gr_mem)<={'amn2-spain'} or [u.pw_name for u in all_users if u.pw_gid==61212]!=['amn2-spain'] or set(os.getgrouplist('amn2-spain',61212))!={61212}:raise ValueError('group_exclusive')
            with storage.MaintenanceReader(DIRECTORY) as reader:
                for name in ('coordinator-claim.json','sequence-claim.json','stage-access.'+OP+'.claim.json'):
                    try:reader._file(name,2097152,private=True)
                    except FileNotFoundError:continue
                    raise ValueError('original_claim_present')
                reader.check_chain()
            with storage.MaintenanceReader(REPAIR_DIRECTORY) as reader:reader._file(REPAIR_RESULT_NAME,479,private=True,expected_size=479,expected_sha256=REPAIR_RESULT_SHA)
            for u in UNITS[:2]:
                for path in ('/etc/systemd/system/'+u+'.d/zz-'+OP+'.conf','/run/phase16/'+OP+'/'+u+'.allow'):
                    if metadata(path)['state']!='ABSENT':raise ValueError('original_fence_present')
            accounts.stable()
        guard()
        with storage.MaintenanceReader(DIRECTORY+'/code') as reader:inventory=reader._file('research/amn2/phase16-bot-stage-readback-inventory-2026-09-29.json',2097152)
        def candidate_readonly():
            undo=[]
            try:
                watch_installed(candidate.runtime,undo);proof=diagnose_candidate(candidate,client,inventory)
                if proof.status!='CANDIDATE_CONTENT_VERIFIED_ACCESS_NOT_APPLIED' or proof.access_plan.status!='ACCESS_PLAN_READY_NOT_APPLIED':raise ValueError('candidate_result')
                return dict(status='PASS',reason=None,proof_status=proof.status,plan_status=proof.access_plan.status,plan_sha256=proof.access_plan.digest,plan_objects=len(proof.access_plan.objects))
            except Exception as error:return dict(status='STOP',reason=safe_reason(error),proof_status=None,plan_status=None,plan_sha256=None,plan_objects=0)
            finally:restore(undo)
        with repair.session_class(candidate.access.UnixStageReader,candidate.access.fingerprint)(WITNESS_META,EXPECTED_ANCESTORS,syscalls=os) as session:
            session.preflight()
            with new_journal(storage,UnixJournal) as journal:
                result['operation']=repair.apply(session,journal,guard,candidate_readonly,dict(approval=APPROVAL,target_sha256=TARGET,original_manifest_sha256=ORIGINAL,witness_sha256=TRIGGER_SHA,remote_sha256=REMOTE_SELF_SHA))
        result['status']=result['operation']['status'];result['reason']=result['operation']['reason']
    except (Exception,ReadbackDeadline) as error:
        result['status']='PARTIAL_OR_UNKNOWN_NO_RETRY' if AUDIT_CREATION_ATTEMPTED else 'STOP_NO_REMOTE_CHANGE';result['reason']=safe_reason(error)
    finally:
        result.update(audit_creation_attempted=AUDIT_CREATION_ATTEMPTED,component_steps=dict(COMPONENTS),runtime_installed=INSTALLED)
        if previous is not None:signal.alarm(0);signal.signal(signal.SIGALRM,previous)
    return result
if __name__=='__main__':
    value=main(sys.argv[1] if len(sys.argv)==2 else '')
    print(json.dumps(value,sort_keys=True,separators=(',',':')),flush=True)
    raise SystemExit(0 if value['status']=='PRIVATE_FILES_SEALED_CANDIDATE_CHECKED' else 3)
'''

def require(value,reason):
    if not value:raise ValueError(reason)

def trigger():
    for path,digest in FROZEN.items():require(packet.sha(packet.canonical(ROOT/path))==digest,'predecessor_changed')
    require(packet.sha(packet.canonical(TRIGGER))==TRIGGER_SHA,'trigger_changed')
    value=json.loads(TRIGGER.read_bytes());local=value['local_result'];r=local['receipt'];t=local['transport']
    require(value['approval_consumed'] is True and local['status']==r['status']=='BOUNDARY_READBACK_COLLECTED_NOT_ADMITTED' and r['approval']==predecessor.APPROVAL and r['original_manifest_sha256']==base.ORIGINAL and r['target_binding_sha256']==packet.entry.binding.TARGET and t['returncode']==0 and t['output_complete'] is True and t['stdin_complete'] is True and t['stdin_bytes_accepted']==0,'trigger_state')
    require(packet.sha(packet.core.encoded(r))==t['stdout']['prefix_sha256'] and len(packet.core.encoded(r))==t['stdout']['bytes_observed'],'trigger_transport')
    require(r['snapshot']['blocked_objects']==list(core.TARGETS),'trigger_scope')
    return value

def witness():return trigger()['local_result']['receipt']['snapshot']

def ancestors():
    result=v1.witness()['ancestors'];result['/opt/amn2-spain/bot-candidates']=witness()['parent_after'];return result

def reasons():
    return sorted(set(v1.reasons())|{'seal_ancestors','seal_stage','seal_inventory','seal_metadata','seal_acl','seal_preimage','seal_fd','seal_scope','seal_transition','bounded_private_seal_candidate_readonly'})

def script():
    w=witness();source=base.source_packet();rawcore=packet.canonical(Path(core.__file__));compile(rawcore,'<private-seal-core>','exec')
    constants=dict(APPROVAL=APPROVAL,SCHEMA=SCHEMA,ORIGINAL=base.ORIGINAL,TARGET=packet.entry.binding.TARGET,BOOT=packet.entry.BOOT,PINS=source['files_sha256_lf'],REASONS=reasons(),COMPONENT_REASONS=reasons(),KINDS=v1.diagnostic.KINDS,RETURNS=v1.diagnostic.RETURNS,TRIGGER_SHA=TRIGGER_SHA,WITNESS_META=w,EXPECTED_ANCESTORS=ancestors(),EXPECTED_UNITS=w['units_before'],REMOTE_SECONDS=REMOTE_SECONDS,REPAIR_DIRECTORY='/var/lib/amn2-spain/phase16-maintenance/'+predecessor.v2.OP,REPAIR_RESULT_NAME='stage-access.'+predecessor.v2.OP+'.result.json',REPAIR_RESULT_SHA=predecessor.REPAIR_RESULT_SHA)
    load='import types\nrepair=types.ModuleType("phase16_private_seal_core")\nexec(compile('+repr(rawcore.decode())+',"<private-seal-core>","exec"),repair.__dict__)\n'
    group=__import__('inspect').getsource(v1.repair.exclusive_group).replace('def exclusive_group(', 'def v1_group_check(',1).replace('require(', 'group_require(')
    group='group_require=repair.require\nRepairError=repair.SealError\n'+group
    raw=(packet.storage.IMPORT_BOOTSTRAP+'\n'+'\n'.join(k+'='+repr(v) for k,v in constants.items())+'\n'+load+group+'\n'+base.REMOTE.split('def collect():',1)[0]+'\n'+v1.diagnostic.EXTRA.split('_readback_main=main',1)[0]+'\n'+v1.EXTRA.split('def main(approval):',1)[0]+'\n'+REMOTE).encode()
    require(len(raw)<=131072,'remote_size');compile(raw,'<private-seal>','exec');return raw

def wire(raw):
    command=v1.wire(raw);suffix=' '+v1.APPROVAL;require(command.endswith(suffix),'wire_shape');command=command[:-len(suffix)]+' '+APPROVAL;require(base.old.command_units([command])+2048<=30000,'command_length');return command

def expected_manifest():
    source=base.source_packet();raw=script()
    return dict(schema='phase16.private-seal-packet.v1',status='READY_NOT_EXECUTED',approval=APPROVAL,original_manifest_sha256=base.ORIGINAL,target_binding_sha256=packet.entry.binding.TARGET,trigger_execution_sha256_lf=TRIGGER_SHA,frozen_consumed_sources_sha256_lf=FROZEN,remote_sha256=packet.sha(raw),gate_sha256_lf=packet.sha(packet.canonical(Path(__file__))),new_core_sha256_lf=packet.sha(packet.canonical(Path(core.__file__))),original_artifacts_sha256_lf={**source['files_sha256_lf'],**source['local_artifacts_sha256_lf']},witness=witness(),ancestors=ancestors(),limits=dict(ssh_attempts=1,remote_seconds=REMOTE_SECONDS,transport_seconds=TRANSPORT_SECONDS,output_bytes=65536,stdin_bytes=0,permission_syscalls_max=2),scope=dict(files=list(core.TARGETS),before_mode=0o644,desired_mode=0o600,parent_stage_other_child_dac_changes=0,audit_directory='/var/lib/amn2-spain/phase16-maintenance/'+OP,audit_records=['stage-access.'+OP+'.'+k+'.json' for k in ('claim','plan','intent','result')],database_open=0,service_actions=0,app_imports=0,stage_install=0,activation=False),reads=['exact held parent/stage/four-boundary witness, stage direct names only, old unit/identity/NSS and fixed old claim/fence absence','pinned private repair result and original55 code/resources','after seal: original readonly candidate content/settings/bootstrap/runtime/access-plan build with safe telemetry'],prohibited=['parent/stage/source/runtime/payload/scratch DAC changes or file-content writes','access-plan apply, maintenance replay/coordinator/data-worker/SQLite','app execution or service actions, install/activation/Telegram/issuance','automatic retry/rollback/cleanup; consumed records unchanged'],rollback='Separate exact approval only; never automatic; old0644 restoration requires same files and still-private stage0700, no later access grant.',evidence_directory=EVIDENCE.as_posix())

def validate_receipt(v,rc):
    require(isinstance(v,dict) and set(v)=={'schema','approval','original_manifest_sha256','target_binding_sha256','trigger_execution_sha256','status','reason','audit_creation_attempted','operation','component_steps','runtime_installed','database_open','service_actions','app_imports','stage_install','activation','replay_allowed'},'receipt_shape')
    require(v['schema']==SCHEMA and v['approval']==APPROVAL and v['original_manifest_sha256']==base.ORIGINAL and v['target_binding_sha256']==packet.entry.binding.TARGET and v['trigger_execution_sha256']==TRIGGER_SHA,'receipt_binding')
    for n in ('database_open','service_actions','app_imports','stage_install'):require(type(v[n]) is int and v[n]==0,'receipt_scope')
    require(v['activation'] is False and v['replay_allowed'] is False and type(v['audit_creation_attempted']) is bool,'receipt_scope')
    statuses=('STOP_NO_REMOTE_CHANGE','STOP_NO_PERMISSION_CHANGE','PARTIAL_OR_UNKNOWN_NO_RETRY','PRIVATE_FILES_SEALED_CANDIDATE_CHECKED');allowed=reasons();require(v['status'] in statuses and v['reason'] in allowed,'receipt_status');op=v['operation']
    if op is not None:
        require(isinstance(op,dict) and set(op)=={'status','reason','permission_attempted','completed_syscalls','files_verified','files_after','candidate','result_durable'} and op['status']==v['status'] and op['reason'] in allowed,'receipt_operation')
        require(type(op['permission_attempted']) is type(op['files_verified']) is type(op['result_durable']) is bool and type(op['completed_syscalls']) is int and 0<=op['completed_syscalls']<=2,'receipt_effects')
        if not op['permission_attempted']:require(op['completed_syscalls']==0 and not op['files_verified'] and op['files_after'] is None and op['candidate'] is None,'receipt_no_permission')
        if op['files_verified']:
            require(op['permission_attempted'] and op['completed_syscalls']==2 and isinstance(op['files_after'],dict) and set(op['files_after'])==set(core.TARGETS),'receipt_files')
            for name,meta in op['files_after'].items():
                before=witness()['objects'][name];require(set(meta)==set(before),'receipt_files')
                for n in ('mode','uid','gid','device','inode','size','nlink','mtime_ns','ctime_ns','acl_count'):require(type(meta[n]) is int and 0<=meta[n]<2**63,'receipt_files')
                require(meta['ctime_ns']>=before['ctime_ns'] and meta['mode']==0o600 and meta['private'] is True and meta['acl_clear'] is True and all(meta[k]==before[k] for k in before if k not in ('mode','ctime_ns','private')),'receipt_files')
        else:require(op['files_after'] is None and op['candidate'] is None,'receipt_unverified')
        c=op['candidate']
        if c is not None:
            require(isinstance(c,dict) and set(c)=={'status','reason','proof_status','plan_status','plan_sha256','plan_objects'},'receipt_candidate')
            if c['status']=='PASS':require(c['reason'] is None and c['proof_status']=='CANDIDATE_CONTENT_VERIFIED_ACCESS_NOT_APPLIED' and c['plan_status']=='ACCESS_PLAN_READY_NOT_APPLIED' and isinstance(c['plan_sha256'],str) and re.fullmatch('[0-9a-f]{64}',c['plan_sha256']) and type(c['plan_objects']) is int and 0<c['plan_objects']<=43000,'receipt_candidate')
            else:require(c['status']=='STOP' and c['reason'] in allowed and c['proof_status'] is c['plan_status'] is c['plan_sha256'] is None and type(c['plan_objects']) is int and c['plan_objects']==0,'receipt_candidate')
    require(isinstance(v['component_steps'],dict) and set(v['component_steps'])<=set(v1.diagnostic.LABELS),'receipt_components')
    for m in v['component_steps'].values():require(isinstance(m,dict) and set(m)=={'calls','status','reason','exception_kind','returned_status'} and type(m['calls']) is int and 1<=m['calls']<=65536 and m['status'] in ('STARTED','PASS','STOP') and m['reason'] in [None]+allowed and m['exception_kind'] in (None,*v1.diagnostic.KINDS) and m['returned_status'] in (None,*v1.diagnostic.RETURNS),'receipt_components')
    m=v['runtime_installed']
    if m is not None:
        require(isinstance(m,dict) and set(m)=={'status','reason','runtime_status','bootstrap_status','scope','verified_files','verified_bytecode'} and m['status'] in ('STARTED','STOP','NOT_PROVEN','PASS_SITE_CONTENT_ONLY') and m['reason'] in [None]+allowed and m['runtime_status'] in ('PASS','NOT_PROVEN') and m['bootstrap_status'] in ('PASS','NOT_PROVEN') and m['scope']=='IMPORT_PATH_CONTENT','receipt_runtime')
        require(all(type(m[k]) is int and 0<=m[k]<=65536 for k in ('verified_files','verified_bytecode')),'receipt_runtime')
    if v['status']=='PRIVATE_FILES_SEALED_CANDIDATE_CHECKED':require(rc==0 and v['reason']=='bounded_private_seal_candidate_readonly' and v['audit_creation_attempted'] and op and op['reason']==v['reason'] and op['permission_attempted'] and op['completed_syscalls']==2 and op['files_verified'] and op['files_after'] and op['result_durable'] and op['candidate'] is not None,'receipt_success')
    else:require(rc==3,'receipt_rc')
    if v['status']=='STOP_NO_REMOTE_CHANGE':require(not v['audit_creation_attempted'] and op is None and v['component_steps']=={} and m is None,'receipt_no_change')
    if v['status']=='STOP_NO_PERMISSION_CHANGE':require(v['audit_creation_attempted'] and op is not None and not op['permission_attempted'],'receipt_no_permission')
    if v['status']=='PARTIAL_OR_UNKNOWN_NO_RETRY':require(v['audit_creation_attempted'],'receipt_partial')
    return v

def preview():
    m=expected_manifest();raw=script();wire(raw);return dict(status='OFFLINE_READY_NOT_EXECUTED',approval=APPROVAL,manifest_sha256=packet.core.digest(m),remote_sha256=packet.sha(raw),ssh_attempts=0,remote_seconds=REMOTE_SECONDS,transport_seconds=TRANSPORT_SECONDS,permission_syscalls_max=2)

def execute_once(manifest,*,approval,manifest_sha,remote_sha,loader):
    require(packet.core.encoded(manifest)==packet.core.encoded(expected_manifest()),'manifest_changed');require(approval==APPROVAL and manifest_sha==packet.core.digest(manifest) and remote_sha==packet.sha(script()),'approval_binding')
    require(not EVIDENCE.exists() and all(not p.is_symlink() for p in (EVIDENCE,*EVIDENCE.parents)),'claim_exists')
    target=loader('spain');require(target.role=='spain' and base.binding_digest(target)==packet.entry.binding.TARGET,'target_binding')
    argv=['C:/Windows/System32/OpenSSH/ssh.exe','-n','-T','-F','none','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(target.known_hosts_path),'-o','ConnectTimeout=10','-o','ConnectionAttempts=1','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=6','-i',str(target.key_path),'-p','22',target.target_user+'@'+target.target_host,wire(script())];require(base.old.command_units(argv)<=30000,'command_length')
    EVIDENCE.parent.mkdir(parents=True,exist_ok=True);EVIDENCE.mkdir();claim=dict(approval=APPROVAL,manifest_sha256=manifest_sha,remote_sha256=remote_sha,attempts=1,claimed_at=datetime.now(timezone.utc).isoformat());packet.core.write_new(EVIDENCE/'claim.json',packet.core.encoded(claim))
    result=dict(schema='phase16.private-seal-local.v1',status='UNKNOWN_NO_RETRY',claim=claim,transport={},receipt=None,replay_allowed=False)
    try:
        rc,out=packet.transport.run_transport(argv,cwd=EVIDENCE,env=base.ssh_environment(),timeout=TRANSPORT_SECONDS,cap=65536,input_bytes=b'',diagnostics=result['transport']);require(result['transport'].get('stdin_complete') is True and result['transport'].get('output_complete') is True,'transport_incomplete');r=validate_receipt(json.loads(out),rc);result['receipt']=r;result['status']=r['status']
    except Exception:result['reason']='TRANSPORT_OR_RECEIPT_UNVERIFIED'
    finally:packet.core.write_new(EVIDENCE/'result.json',packet.core.encoded(result))
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--approve');p.add_argument('--approved-manifest-sha256');p.add_argument('--approved-remote-sha256');a=p.parse_args()
    try:
        r=preview()
        if a.execute:
            from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
            r=execute_once(json.loads(MANIFEST.read_bytes()),approval=a.approve,manifest_sha=a.approved_manifest_sha256,remote_sha=a.approved_remote_sha256,loader=load_fixed_role_binding)
        print(json.dumps(r,indent=2));return 0 if r['status'] in ('OFFLINE_READY_NOT_EXECUTED','PRIVATE_FILES_SEALED_CANDIDATE_CHECKED') else 3
    except Exception:print('{"status":"LOCAL_STOP"}');return 2
if __name__=='__main__':raise SystemExit(main())
