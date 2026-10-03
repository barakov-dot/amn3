"""Separate one-shot parent permission repair plus readonly candidate proof.

Default preview is zero-egress. No maintenance replay, DB, app, services, install.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts import phase16_bot_maintenance_readback as base
from scripts import phase16_bot_candidate_diagnostic as diagnostic
from scripts import phase16_bot_ancestor_repair as repair
packet=base.packet
APPROVAL='PHASE16_CANDIDATE_ANCESTOR_REPAIR_20261003_001'
PREDECESSOR_SHA='b0e35c25317b94cafa2ff2b1aa6af15336b4e7e9ec57ac8997d43b600029bb0b'
DIAGNOSTIC_SHA='e000970aa2a015034204e764a6d134d3d1256893cc636a2f6f5f236891c5a57f'
WITNESS=ROOT/'research/amn2/phase16-bot-ancestor-readback-execution-001-2026-10-03.json'
WITNESS_SHA='ec7fbe1075ce5e175e2a0a04ffa873bdc15c72afec4befc25070c147b98b5e37'
MANIFEST=ROOT/'research/amn2/phase16-bot-ancestor-repair-manifest-2026-10-03.json'
EVIDENCE=Path('C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-ancestor-repair-20261003/execution-001')
REMOTE_SECONDS=180
TRANSPORT_SECONDS=210
EXTRA=r"""
from contextlib import contextmanager
INSTALLED=None
AUDIT_CREATION_ATTEMPTED=False
LABELS=('catalog','stage_observation','settings','bootstrap','identity','nss_groups','settings_file_read','secure_tree_open','secure_file_read','readonly_command','runtime_expected','venv','access_plan','collection')

def watch_installed(runtime,undo):
    original=runtime.verify_installed;own='verify_installed' in vars(runtime)
    def traced(*args,**kwargs):
        global INSTALLED
        INSTALLED=dict(status='STARTED',reason=None,runtime_status='NOT_PROVEN',bootstrap_status='NOT_PROVEN',scope='IMPORT_PATH_CONTENT',verified_files=0,verified_bytecode=0)
        value=original(*args,**kwargs)
        statuses={'STOP','NOT_PROVEN','PASS_SITE_CONTENT_ONLY'}
        if value.status not in statuses or value.runtime_status not in ('PASS','NOT_PROVEN') or value.bootstrap_status not in ('PASS','NOT_PROVEN') or value.scope!='IMPORT_PATH_CONTENT':raise ValueError('runtime_telemetry')
        if any(type(n) is not int or not 0<=n<=65536 for n in (value.verified_files,value.verified_bytecode)):raise ValueError('runtime_telemetry')
        INSTALLED=dict(status=value.status,reason=value.reason if value.reason in COMPONENT_REASONS else 'UNCLASSIFIED_ERROR',runtime_status=value.runtime_status,bootstrap_status=value.bootstrap_status,scope=value.scope,verified_files=value.verified_files,verified_bytecode=value.verified_bytecode)
        return value
    undo.append((runtime,'verify_installed',original,own));runtime.verify_installed=traced

@contextmanager
def new_journal(storage,journal_class):
    global AUDIT_CREATION_ATTEMPTED
    with storage.MaintenanceReader(storage.MAINTENANCE_ROOT) as parent:
        fd=parent.root_fd;before=os.fstat(fd);names=set(os.listdir(fd))
        if len(names)>4096 or repair.OP in names:raise ValueError('repair_claim_exists')
        parent.check_chain()
        AUDIT_CREATION_ATTEMPTED=True  # mkdir may have succeeded even if interrupted
        os.mkdir(repair.OP,0o700,dir_fd=fd)
        after=os.fstat(fd)
        if any(getattr(before,k)!=getattr(after,k) for k in ('st_dev','st_ino','st_mode','st_uid','st_gid')) or after.st_nlink!=before.st_nlink+1 or set(os.listdir(fd))!=names|{repair.OP}:raise ValueError('repair_journal_changed')
        current,ancestor,name,_=parent.chain[-1];parent.chain[-1]=(current,ancestor,name,after)
        os.fsync(fd);parent.check_chain()
        with journal_class(storage.MAINTENANCE_ROOT+'/'+repair.OP) as journal:
            meta=os.fstat(journal.root_fd);named=os.stat(repair.OP,dir_fd=fd,follow_symlinks=False)
            if (meta.st_dev,meta.st_ino)!=(named.st_dev,named.st_ino):raise ValueError('repair_journal_changed')
            yield journal
            journal.check_chain();parent.check_chain()

def main(approval):
    global AUDIT_CREATION_ATTEMPTED,INSTALLED
    AUDIT_CREATION_ATTEMPTED=False;INSTALLED=None;COMPONENTS.clear()
    result=dict(schema='phase16.ancestor-repair.v1',approval=APPROVAL,original_manifest_sha256=ORIGINAL,target_binding_sha256=TARGET,status='STOP_NO_REMOTE_CHANGE',reason='precondition',audit_creation_attempted=False,operation=None,component_steps={},runtime_installed=None,database_open=0,service_actions=0,app_imports=0,stage_install=0,activation=False,replay_allowed=False)
    previous=None
    try:
        if sys.platform!='linux' or os.geteuid()!=0:raise ValueError('platform')
        if approval!=APPROVAL:raise ValueError('approval')
        import grp,pwd
        remaining=int(READBACK_STARTED+REMOTE_SECONDS-time.monotonic())
        if remaining<1:raise ReadbackDeadline('deadline')
        previous=signal.getsignal(signal.SIGALRM)
        def deadline(*unused):raise ReadbackDeadline('deadline')
        signal.signal(signal.SIGALRM,deadline);signal.alarm(remaining)
        if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=BOOT:raise ValueError('boot_changed')
        _phase16_import_root(DIRECTORY+'/code',PINS,ORIGINAL)
        from scripts import phase16_bot_candidate_admission as candidate
        from scripts import phase16_bot_maintenance_linux as linux
        from scripts import phase16_bot_maintenance_storage as storage
        from scripts.phase16_bot_stage_access_apply import UnixJournal
        from scripts.vps.phase16_bot_retained_stage_remote import SecureReader,fingerprint
        client=linux.SystemdClient(linux.BoundedCommand(maximum=65536));accounts=candidate.settings.RootSettingsReader()
        def properties():return {u:{k:client.bus_property(u,'Service',k,s) for k,s in candidate.IDENTITY_FIELDS.items()} for u in UNITS[:2]}
        initial=properties();identity=candidate.local_identity(accounts('/etc/passwd'),accounts('/etc/group'),initial[UNITS[0]])
        if initial[UNITS[0]]!=initial[UNITS[1]] or (identity.uid,identity.gid,identity.supplementary_gids)!=(61212,61212,(61212,)):raise ValueError('repair_identity')
        def guard():
            if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=BOOT or properties()!=initial or unit_states()!=WITNESS_FACTS['units_before']:raise ValueError('repair_continuity')
            candidate.local_identity(accounts('/etc/passwd'),accounts('/etc/group'),initial[UNITS[0]])
            repair.exclusive_group(accounts('/etc/passwd'),accounts('/etc/group'))
            local=pwd.getpwnam('amn2-spain');group=grp.getgrgid(61212);all_users=pwd.getpwall()
            if len(all_users)>4096 or (local.pw_uid,local.pw_gid)!=(61212,61212) or group.gr_name!='amn2-spain' or not set(group.gr_mem)<={'amn2-spain'} or [u.pw_name for u in all_users if u.pw_gid==61212]!=['amn2-spain'] or set(os.getgrouplist('amn2-spain',61212))!={61212}:raise ValueError('group_exclusive')
            with storage.MaintenanceReader(DIRECTORY) as reader:
                for name in ('coordinator-claim.json','sequence-claim.json','stage-access.'+OP+'.claim.json'):
                    try:reader._file(name,2097152,private=True)
                    except FileNotFoundError:continue
                    raise ValueError('original_claim_present')
                reader.check_chain()
            for u in UNITS[:2]:
                for path in ('/etc/systemd/system/'+u+'.d/zz-'+OP+'.conf','/run/phase16/'+OP+'/'+u+'.allow'):
                    if metadata(path)['state']!='ABSENT':raise ValueError('original_fence_present')
            accounts.stable()
        guard()
        inventory=None
        with storage.MaintenanceReader(DIRECTORY+'/code') as reader:
            inventory=reader._file('research/amn2/phase16-bot-stage-readback-inventory-2026-09-29.json',2097152)
        def candidate_readonly():
            undo=[]
            try:
                watch_installed(candidate.runtime,undo)
                proof=diagnose_candidate(candidate,client,inventory)
                if proof.status!='CANDIDATE_CONTENT_VERIFIED_ACCESS_NOT_APPLIED' or proof.access_plan.status!='ACCESS_PLAN_READY_NOT_APPLIED':raise ValueError('candidate_result')
                return dict(status='PASS',reason=None,proof_status=proof.status,plan_status=proof.access_plan.status,plan_sha256=proof.access_plan.digest,plan_objects=len(proof.access_plan.objects))
            except Exception as error:return dict(status='STOP',reason=safe_reason(error),proof_status=None,plan_status=None,plan_sha256=None,plan_objects=0)
            finally:restore(undo)
        with repair.parent_session(SecureReader,fingerprint)(WITNESS_FACTS,syscalls=os) as session:
            session.preflight()
            with new_journal(storage,UnixJournal) as journal:
                result['operation']=repair.apply(session,journal,guard,candidate_readonly,dict(approval=APPROVAL,target_sha256=TARGET,original_manifest_sha256=ORIGINAL,witness_sha256=WITNESS_SHA,remote_sha256=REMOTE_SELF_SHA))
        result['status']=result['operation']['status'];result['reason']=result['operation']['reason']
    except (Exception,ReadbackDeadline) as error:
        result['status']='PARTIAL_OR_UNKNOWN_NO_RETRY' if AUDIT_CREATION_ATTEMPTED else 'STOP_NO_REMOTE_CHANGE'
        result['reason']=safe_reason(error)
    finally:
        result.update(audit_creation_attempted=AUDIT_CREATION_ATTEMPTED,component_steps=dict(COMPONENTS),runtime_installed=INSTALLED)
        if previous is not None:signal.alarm(0);signal.signal(signal.SIGALRM,previous)
    return result
if __name__=='__main__':
    value=main(sys.argv[1] if len(sys.argv)==2 else '')
    print(json.dumps(value,sort_keys=True,separators=(',',':')),flush=True)
    raise SystemExit(0 if value['status']=='PARENT_REPAIRED_CANDIDATE_CHECKED' else 3)
"""

def require(value,reason):
    if not value:raise ValueError(reason)

def witness():
    require(packet.sha(packet.canonical(WITNESS))==WITNESS_SHA,'witness_changed')
    value=json.loads(WITNESS.read_bytes())
    require(value['approval_consumed'] is True and value['status']=='ANCESTOR_FACTS_COLLECTED_NOT_REPAIRED','witness_binding')
    return value['local_result']['receipt']['snapshot']

def reasons():
    return sorted(set(diagnostic.component_reasons())|{'platform','precondition','bounded_parent_change_candidate_readonly','deadline','operation_unverified','parent_chain','parent_preimage','parent_acl','parent_private','sibling_inventory','sibling_private','stage_preimage','parent_transition','parent_named','group_exclusive','repair_claim_exists','repair_journal_changed','repair_identity','repair_continuity','original_claim_present','original_fence_present','runtime_telemetry','candidate_result','UNCLASSIFIED_ERROR'})

def script():
    require(packet.sha(packet.canonical(Path(base.__file__)))==PREDECESSOR_SHA,'predecessor_changed')
    require(packet.sha(packet.canonical(Path(diagnostic.__file__)))==DIAGNOSTIC_SHA,'diagnostic_changed')
    original=base.source_packet();core=packet.canonical(Path(repair.__file__)).decode()
    constants=dict(APPROVAL=APPROVAL,ORIGINAL=base.ORIGINAL,TARGET=packet.entry.binding.TARGET,BOOT=packet.entry.BOOT,PINS=original['files_sha256_lf'],REASONS=reasons(),COMPONENT_REASONS=reasons(),KINDS=diagnostic.KINDS,RETURNS=diagnostic.RETURNS,WITNESS_FACTS=witness(),WITNESS_SHA=WITNESS_SHA,REMOTE_SECONDS=REMOTE_SECONDS)
    prefix=base.REMOTE.split('def collect():',1)[0]
    helpers=diagnostic.EXTRA.split('_readback_main=main',1)[0]
    load_core='import types\nrepair=types.ModuleType("phase16_frozen_ancestor_repair")\nexec(compile('+repr(core)+',"<ancestor-repair-core>","exec"),repair.__dict__)\n'
    raw=(packet.storage.IMPORT_BOOTSTRAP+'\n'+'\n'.join(k+'='+repr(v) for k,v in constants.items())+'\n'+load_core+prefix+'\n'+helpers+'\n'+EXTRA).encode()
    require(len(raw)<=131072,'remote_size');compile(raw,'<ancestor-repair>','exec');return raw

def remote_definitions():
    env={'__name__':'repair_fixture'};exec(compile(script(),'<ancestor-repair>','exec'),env);env['READBACK_STARTED']=time.monotonic();env['REMOTE_SELF_SHA']=packet.sha(script());return env

def wire(raw):
    import shlex
    tokens=shlex.split(base.wire(raw))
    require(len(tokens)==7 and tokens[:5]==['/usr/bin/python3','-I','-S','-B','-c'],'wire_shape')
    needle='"READBACK_STARTED":READBACK_STARTED}'
    require(tokens[5].count(needle)==1,'wire_shape')
    launcher=tokens[5].replace(needle,'"READBACK_STARTED":READBACK_STARTED,"REMOTE_SELF_SHA":'+repr(packet.sha(raw))+'}')
    command='/usr/bin/python3 -I -S -B -c '+shlex.quote(launcher)+' '+APPROVAL
    require(base.old.command_units([command])+2048<=30000,'command_length');return command

def expected_manifest():
    value=base.expected_manifest()
    value.update(schema='phase16.ancestor-repair-packet.v1',approval=APPROVAL,remote_sha256=packet.sha(script()),gate_sha256_lf=packet.sha(packet.canonical(Path(__file__))),repair_core_sha256_lf=packet.sha(packet.canonical(Path(repair.__file__))),diagnostic_gate_sha256_lf=DIAGNOSTIC_SHA,predecessor_gate_sha256_lf=PREDECESSOR_SHA,witness_sha256_lf=WITNESS_SHA,evidence_directory=EVIDENCE.as_posix())
    value['limits'].update(remote_seconds=REMOTE_SECONDS,transport_seconds=TRANSPORT_SECONDS,direct_siblings=16)
    value['scope']=dict(permission_syscalls_max=2,permission_object=repair.PARENT,desired_uid=0,desired_gid=61212,desired_mode_octal='0710',audit_directory='/var/lib/amn2-spain/phase16-maintenance/'+repair.OP,audit_records=['stage-access.'+repair.OP+'.'+k+'.json' for k in ('claim','plan','intent','result')],database_open=0,service_actions=0,app_imports=0,stage_install=0,activation=0,telegram=0)
    value['reads']=['fixed boot/original authenticated code/resources and selected unit/account/NSS identity; exclusive service group','exact four-parent and retained-stage witness; at most16 known direct child directory metadata, never sibling contents','original absence claims/fence metadata; no original result/journal mutation','after parent repair: original candidate readonly collector/wheel/source/site content proof and access plan; closed telemetry for actual runtime verifier return']
    value['prohibited']=['child or other ancestor chmod/chown','stage access-plan apply','maintenance entry/replay/coordinator/data-worker/SQLite','service start/stop/reload and app import/execution','install/activation/Telegram/issuance','automatic retry/rollback/cleanup; original operation files untouched']
    value['rollback']='Separate exact approval only: if same identity/private siblings/stage unchanged, parent mode0700 first then gid0; never automatic.'
    return value

def validate_receipt(value,rc):
    fields={'schema','approval','original_manifest_sha256','target_binding_sha256','status','reason','audit_creation_attempted','operation','component_steps','runtime_installed','database_open','service_actions','app_imports','stage_install','activation','replay_allowed'}
    require(isinstance(value,dict) and set(value)==fields,'receipt_shape')
    require(value['schema']=='phase16.ancestor-repair.v1' and value['approval']==APPROVAL and value['original_manifest_sha256']==base.ORIGINAL and value['target_binding_sha256']==packet.entry.binding.TARGET,'receipt_binding')
    for name in ('database_open','service_actions','app_imports','stage_install'):require(type(value[name]) is int and value[name]==0,'receipt_scope')
    require(value['activation'] is False and value['replay_allowed'] is False and type(value['audit_creation_attempted']) is bool,'receipt_scope')
    require(value['reason'] in reasons() and value['status'] in ('STOP_NO_REMOTE_CHANGE','STOP_NO_PERMISSION_CHANGE','PARTIAL_OR_UNKNOWN_NO_RETRY','PARENT_REPAIRED_CANDIDATE_CHECKED'),'receipt_status')
    op=value['operation']
    if op is not None:
        require(isinstance(op,dict) and set(op)=={'status','reason','permission_attempted','completed_syscalls','parent_verified','parent_after','candidate','result_durable'},'receipt_operation')
        require(op['reason'] in reasons() and op['status'] in ('STOP_NO_PERMISSION_CHANGE','PARTIAL_OR_UNKNOWN_NO_RETRY','PARENT_REPAIRED_CANDIDATE_CHECKED'),'receipt_operation')
        for name in ('permission_attempted','parent_verified','result_durable'):require(type(op[name]) is bool,'receipt_operation')
        require(type(op['completed_syscalls']) is int and 0<=op['completed_syscalls']<=2,'receipt_operation')
        if op['parent_after'] is not None:
            require(set(op['parent_after'])==set(repair.FIELDS) and all(type(n) is int and n>=0 for n in op['parent_after'].values()),'receipt_parent')
            require((op['parent_after']['uid'],op['parent_after']['gid'],op['parent_after']['mode'])==(0,61212,0o710),'receipt_parent')
            before=witness()['ancestors'][repair.PARENT]
            require(all(op['parent_after'][k]==before[k] for k in ('device','inode','mtime_ns')) and op['parent_after']['ctime_ns']>=before['ctime_ns'],'receipt_parent_binding')
        c=op['candidate']
        if c is not None:
            require(set(c)=={'status','reason','proof_status','plan_status','plan_sha256','plan_objects'},'receipt_candidate')
            if c['status']=='PASS':
                import re
                require(c['reason'] is None and c['proof_status']=='CANDIDATE_CONTENT_VERIFIED_ACCESS_NOT_APPLIED' and c['plan_status']=='ACCESS_PLAN_READY_NOT_APPLIED' and re.fullmatch('[a-f0-9]{64}',c['plan_sha256']) and type(c['plan_objects']) is int and 0<c['plan_objects']<=43000,'receipt_candidate')
            else:require(c['status']=='STOP' and c['reason'] in reasons() and c['proof_status'] is c['plan_status'] is c['plan_sha256'] is None and c['plan_objects']==0,'receipt_candidate')
    if op is not None:
        require(value['audit_creation_attempted'],'receipt_audit')
        if not op['permission_attempted']:
            require(op['completed_syscalls']==0 and not op['parent_verified'] and op['parent_after'] is None and op['candidate'] is None and op['status']=='STOP_NO_PERMISSION_CHANGE','receipt_no_permission')
        if op['parent_verified']:require(op['permission_attempted'] and op['completed_syscalls']==2 and op['parent_after'] is not None,'receipt_parent_verified')
    if value['status']=='STOP_NO_PERMISSION_CHANGE':
        require(op is not None and op['status']==value['status'] and not op['permission_attempted'],'receipt_no_permission')
    if value['status']=='PARTIAL_OR_UNKNOWN_NO_RETRY':require(value['audit_creation_attempted'],'receipt_partial')
    require(isinstance(value['component_steps'],dict) and set(value['component_steps'])<=set(diagnostic.LABELS),'receipt_components')
    for item in value['component_steps'].values():
        require(set(item)=={'calls','status','reason','exception_kind','returned_status'} and type(item['calls']) is int and 1<=item['calls']<=65536 and item['status'] in ('STARTED','PASS','STOP') and item['reason'] in [None]+reasons() and item['exception_kind'] in (None,*diagnostic.KINDS) and item['returned_status'] in (None,*diagnostic.RETURNS),'receipt_components')
    inst=value['runtime_installed']
    if inst is not None:
        require(set(inst)=={'status','reason','runtime_status','bootstrap_status','scope','verified_files','verified_bytecode'} and inst['status'] in ('STARTED','STOP','NOT_PROVEN','PASS_SITE_CONTENT_ONLY') and inst['reason'] in [None]+reasons() and inst['runtime_status'] in ('PASS','NOT_PROVEN') and inst['bootstrap_status'] in ('PASS','NOT_PROVEN') and inst['scope']=='IMPORT_PATH_CONTENT','receipt_runtime')
        require(all(type(inst[k]) is int and 0<=inst[k]<=65536 for k in ('verified_files','verified_bytecode')),'receipt_runtime')
    if value['status']=='PARENT_REPAIRED_CANDIDATE_CHECKED':require(rc==0 and value['audit_creation_attempted'] and op and op['status']==value['status'] and op['permission_attempted'] and op['completed_syscalls']==2 and op['parent_verified'] and op['parent_after'] and op['result_durable'] and op['candidate'] is not None,'receipt_success')
    else:require(rc==3,'receipt_rc')
    if value['status']=='STOP_NO_REMOTE_CHANGE':require(not value['audit_creation_attempted'] and op is None,'receipt_no_change')
    return value

def preview():
    manifest=expected_manifest();raw=script();wire(raw)
    return dict(status='OFFLINE_READY_NOT_EXECUTED',approval=APPROVAL,manifest_sha256=packet.core.digest(manifest),remote_sha256=packet.sha(raw),ssh_attempts=0,remote_seconds=REMOTE_SECONDS,transport_seconds=TRANSPORT_SECONDS,permission_syscalls_max=2)

def execute_once(manifest,*,approval,manifest_sha,remote_sha,loader):
    require(packet.core.encoded(manifest)==packet.core.encoded(expected_manifest()),'manifest_changed')
    require(approval==APPROVAL and manifest_sha==packet.core.digest(manifest) and remote_sha==packet.sha(script()),'approval_binding')
    require(not EVIDENCE.exists() and all(not p.is_symlink() for p in (EVIDENCE,*EVIDENCE.parents)),'claim_exists')
    target=loader('spain');require(target.role=='spain' and base.binding_digest(target)==packet.entry.binding.TARGET,'target_binding')
    argv=['C:/Windows/System32/OpenSSH/ssh.exe','-n','-T','-F','none','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(target.known_hosts_path),'-o','ConnectTimeout=10','-o','ConnectionAttempts=1','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=6','-i',str(target.key_path),'-p','22',target.target_user+'@'+target.target_host,wire(script())]
    require(base.old.command_units(argv)<=30000,'command_length')
    EVIDENCE.parent.mkdir(parents=True,exist_ok=True);EVIDENCE.mkdir()
    claim=dict(approval=APPROVAL,manifest_sha256=manifest_sha,remote_sha256=remote_sha,attempts=1,claimed_at=datetime.now(timezone.utc).isoformat())
    packet.core.write_new(EVIDENCE/'claim.json',packet.core.encoded(claim))
    result=dict(schema='phase16.ancestor-repair-local.v1',status='UNKNOWN_NO_RETRY',claim=claim,transport={},receipt=None,replay_allowed=False)
    try:
        rc,out=packet.transport.run_transport(argv,cwd=EVIDENCE,env=base.ssh_environment(),timeout=TRANSPORT_SECONDS,cap=65536,input_bytes=b'',diagnostics=result['transport'])
        require(result['transport'].get('stdin_complete') is True and result['transport'].get('output_complete') is True,'transport_incomplete')
        value=validate_receipt(json.loads(out),rc);result['receipt']=value;result['status']=value['status']
    except Exception:result['reason']='TRANSPORT_OR_RECEIPT_UNVERIFIED'
    finally:packet.core.write_new(EVIDENCE/'result.json',packet.core.encoded(result))
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');parser.add_argument('--approve');parser.add_argument('--approved-manifest-sha256');parser.add_argument('--approved-remote-sha256');args=parser.parse_args()
    try:
        result=preview()
        if args.execute:
            from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
            result=execute_once(json.loads(MANIFEST.read_bytes()),approval=args.approve,manifest_sha=args.approved_manifest_sha256,remote_sha=args.approved_remote_sha256,loader=load_fixed_role_binding)
        print(json.dumps(result,indent=2));return 0 if result['status'] in ('OFFLINE_READY_NOT_EXECUTED','PARENT_REPAIRED_CANDIDATE_CHECKED') else 3
    except Exception:print('{"status":"LOCAL_STOP"}');return 2
if __name__=='__main__':raise SystemExit(main())
