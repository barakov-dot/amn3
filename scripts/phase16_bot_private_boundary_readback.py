"""One proposed metadata readback after repaired parent/runtime PASS. Preview only.

Frozen consumed packets and access policy remain immutable. No candidate rerun,
private contents, sibling listing, chmod/chown, app, SQLite, services or replay.
"""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts import phase16_bot_ancestor_repair_v2_gate as v2
base=v2.base
packet=v2.packet
APPROVAL='PHASE16_CANDIDATE_PRIVATE_BOUNDARY_READBACK_20261004_001'
SCHEMA='phase16.private-boundary-readback.v1'
MANIFEST=ROOT/'research/amn2/phase16-bot-private-boundary-readback-manifest-2026-10-04.json'
EVIDENCE=Path('C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-private-boundary-readback-20261004/execution-001')
TRIGGER=ROOT/'research/amn2/phase16-bot-ancestor-repair-v2-execution-001-2026-10-04.json'
TRIGGER_SHA='1f7aff1633b76897422416ce3f9d22e2f40e14db226be2b1f8f2ba668692b42a'
FROZEN_V2_SHA='20d73c573a74fdaaa248484421618ab504acfae74f61562e2355e24ebf7bca8e'
REPAIR_RESULT_SHA='2431ea8e2adce727d0974acb14f81675462c976f1d4c6b3fddcbc9317e64e91d'
FROZEN_HELPERS={**v2.FROZEN,'scripts/phase16_bot_maintenance_readback.py':v2.v1.PREDECESSOR_SHA,'scripts/phase16_bot_candidate_diagnostic.py':v2.v1.DIAGNOSTIC_SHA}
NAMES=('claim.json','result.json','payload','scratch')
REMOTE_SECONDS=45
TRANSPORT_SECONDS=60
REMOTE=r'''
def row(meta):
    return dict(mode=stat.S_IMODE(meta.st_mode),uid=meta.st_uid,gid=meta.st_gid,device=meta.st_dev,inode=meta.st_ino,mtime_ns=meta.st_mtime_ns,ctime_ns=meta.st_ctime_ns)

def inspect_boundaries(reader):
    from scripts import phase16_bot_stage_access as access
    result={}
    for name in PRIVATE_NAMES:
        meta=reader.info(name);access._metadata(meta)
        directory=name in ('payload','scratch')
        if not (stat.S_ISDIR(meta.st_mode) if directory else stat.S_ISREG(meta.st_mode)):raise ValueError('boundary_kind')
        acls=reader.acl_names(name)
        if type(acls) not in (tuple,list) or len(acls)>64:raise ValueError('boundary_acl')
        result[name]=dict(**row(meta),kind='directory' if directory else 'file',size=meta.st_size,nlink=meta.st_nlink,acl_clear=not acls,acl_count=len(acls),private=not (stat.S_IMODE(meta.st_mode)&0o077) and not acls)
    reader.stable()
    return result,sorted(n for n,m in result.items() if not m['private'])

def collect():
    if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=BOOT:raise ValueError('boot_changed')
    _phase16_import_root(DIRECTORY+'/code',PINS,ORIGINAL)
    from scripts.phase16_bot_stage_access import UnixStageReader
    from scripts.phase16_bot_maintenance_storage import MaintenanceReader
    before=unit_states()
    if before!=EXPECTED_UNITS:raise ValueError('unit_changed')
    with UnixStageReader() as reader,MaintenanceReader(REPAIR_DIRECTORY) as audit:
        parent=reader.ancestors()[-1]
        if parent[0]!='/opt/amn2-spain/bot-candidates' or parent[2] or row(parent[1])!=EXPECTED_PARENT:raise ValueError('parent_changed')
        if row(reader.info('.'))!=EXPECTED_STAGE or reader.acl_names('.'):raise ValueError('stage_changed')
        raw=audit._file(REPAIR_RESULT_NAME,479,private=True,expected_size=479,expected_sha256=REPAIR_RESULT_SHA)
        objects,blocked=inspect_boundaries(reader)
        after=unit_states()
        if before!=after or Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=BOOT:raise ValueError('unit_changed')
        if row(reader.ancestors()[-1][1])!=EXPECTED_PARENT:raise ValueError('parent_changed')
        reader.stable();audit.check_chain()
        return dict(parent_after=EXPECTED_PARENT,stage_root=EXPECTED_STAGE,objects=objects,blocked_objects=blocked,repair_result=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()),units_before=before,units_after=after)

def main(approval):
    result=dict(schema=SCHEMA,approval=APPROVAL,original_manifest_sha256=ORIGINAL,target_binding_sha256=TARGET,trigger_execution_sha256=TRIGGER_SHA,status='UNKNOWN_NO_RETRY',reason='platform',snapshot=None,remote_file_writes=0,permission_syscalls=0,database_open=0,service_actions=0,app_imports=0,activation=False,replay_allowed=False)
    previous=None
    try:
        if sys.platform!='linux' or os.geteuid()!=0:raise ValueError('platform')
        if approval!=APPROVAL:raise ValueError('approval')
        remaining=int(READBACK_STARTED+REMOTE_SECONDS-time.monotonic())
        if remaining<1:raise ReadbackDeadline('deadline')
        previous=signal.getsignal(signal.SIGALRM)
        def alarm(*unused):raise ReadbackDeadline('deadline')
        signal.signal(signal.SIGALRM,alarm);signal.alarm(remaining)
        result['snapshot']=collect();result['status']='BOUNDARY_READBACK_COLLECTED_NOT_ADMITTED';result['reason']='bounded_private_metadata'
    except (Exception,ReadbackDeadline) as error:
        reason=error.args[0] if len(error.args)==1 else None
        result['reason']=reason if reason in SAFE_REASONS else 'UNCLASSIFIED_ERROR'
    finally:
        if previous is not None:signal.alarm(0);signal.signal(signal.SIGALRM,previous)
    return result
if __name__=='__main__':
    value=main(sys.argv[1] if len(sys.argv)==2 else '')
    print(json.dumps(value,sort_keys=True,separators=(',',':')),flush=True)
    raise SystemExit(0 if value['status']=='BOUNDARY_READBACK_COLLECTED_NOT_ADMITTED' else 3)
'''
REASONS=('platform','approval','deadline','boot_changed','unit_changed','parent_changed','stage_changed','boundary_kind','boundary_acl','UNCLASSIFIED_ERROR')

def require(value,reason):
    if not value:raise ValueError(reason)

def trigger():
    for name,digest in FROZEN_HELPERS.items():require(packet.sha(packet.canonical(ROOT/name))==digest,'predecessor_changed')
    require(packet.sha(packet.canonical(Path(v2.__file__)))==FROZEN_V2_SHA,'predecessor_changed')
    require(packet.sha(packet.canonical(TRIGGER))==TRIGGER_SHA,'trigger_changed')
    value=json.loads(TRIGGER.read_bytes());local=value['local_result'];v2.validate_receipt(local['receipt'],local['transport']['returncode'])
    r=local['receipt']
    require(value['approval_consumed'] is True and r['status']=='PARENT_REPAIRED_CANDIDATE_CHECKED' and r['operation']['candidate']['status']=='STOP' and r['component_steps']['access_plan']['reason']=='private_boundary' and r['runtime_installed']['status']=='PASS_SITE_CONTENT_ONLY','trigger_state')
    require(packet.sha(packet.core.encoded(r['operation']))==REPAIR_RESULT_SHA,'repair_result_binding')
    return value

def expected_roots():
    return trigger()['local_result']['receipt']['operation']['parent_after'],{k:v for k,v in v2.v1.witness()['stage_root'].items() if k in v2.v1.repair.FIELDS}

def script():
    parent,stage=expected_roots();original=base.source_packet()
    constants=dict(APPROVAL=APPROVAL,SCHEMA=SCHEMA,ORIGINAL=base.ORIGINAL,TARGET=packet.entry.binding.TARGET,BOOT=packet.entry.BOOT,PINS=original['files_sha256_lf'],TRIGGER_SHA=TRIGGER_SHA,PRIVATE_NAMES=NAMES,REMOTE_SECONDS=REMOTE_SECONDS,SAFE_REASONS=REASONS,EXPECTED_PARENT=parent,EXPECTED_STAGE=stage,EXPECTED_UNITS=v2.v1.witness()['units_before'],REPAIR_DIRECTORY='/var/lib/amn2-spain/phase16-maintenance/'+v2.OP,REPAIR_RESULT_NAME='stage-access.'+v2.OP+'.result.json',REPAIR_RESULT_SHA=REPAIR_RESULT_SHA)
    raw=(packet.storage.IMPORT_BOOTSTRAP+'\n'+'\n'.join(k+'='+repr(v) for k,v in constants.items())+'\n'+base.REMOTE.split('def collect():',1)[0]+'\n'+REMOTE).encode()
    require(len(raw)<=131072,'remote_size');compile(raw,'<private-boundary-readback>','exec');return raw

def remote_definitions():
    env={'__name__':'private_boundary_fixture'};exec(compile(script(),'<private-boundary-readback>','exec'),env);env['READBACK_STARTED']=time.monotonic();return env

def wire(raw):
    command=base.wire(raw);suffix=' '+base.APPROVAL;require(command.endswith(suffix),'wire_shape');return command[:-len(suffix)]+' '+APPROVAL

def expected_manifest():
    source=base.source_packet();parent,stage=expected_roots()
    return dict(schema='phase16.private-boundary-readback-packet.v1',status='READY_NOT_EXECUTED',approval=APPROVAL,original_manifest_sha256=base.ORIGINAL,target_binding_sha256=packet.entry.binding.TARGET,trigger_execution_sha256_lf=TRIGGER_SHA,frozen_v2_gate_sha256_lf=FROZEN_V2_SHA,frozen_helpers_sha256_lf=FROZEN_HELPERS,remote_sha256=packet.sha(script()),gate_sha256_lf=packet.sha(packet.canonical(Path(__file__))),original_artifacts_sha256_lf={**source['files_sha256_lf'],**source['local_artifacts_sha256_lf']},expected_parent=parent,expected_stage=stage,repair_result_sha256=REPAIR_RESULT_SHA,private_objects=list(NAMES),limits=dict(ssh_attempts=1,remote_seconds=REMOTE_SECONDS,transport_seconds=TRANSPORT_SECONDS,output_bytes=65536,stdin_bytes=0),scope=dict(remote_file_writes=0,permission_syscalls=0,database_open=0,service_actions=0,app_imports=0,activation=False),reads=['metadata/ACL count only of four fixed private boundary objects; no bytes','held stage and parent identities matching actual repair; old bot/web/coordinator selected properties','one bounded private repair result, only bytes/hash output'],prohibited=['private boundary contents and sibling listing','candidate/runtime verification rerun','permission changes, upload, DB, app, service actions, maintenance replay, retry, rollback, cleanup, Telegram, issuance'],evidence_directory=EVIDENCE.as_posix())

def validate_receipt(value,rc):
    require(isinstance(value,dict) and set(value)=={'schema','approval','original_manifest_sha256','target_binding_sha256','trigger_execution_sha256','status','reason','snapshot','remote_file_writes','permission_syscalls','database_open','service_actions','app_imports','activation','replay_allowed'},'receipt_shape')
    require(value['schema']==SCHEMA and value['approval']==APPROVAL and value['original_manifest_sha256']==base.ORIGINAL and value['target_binding_sha256']==packet.entry.binding.TARGET and value['trigger_execution_sha256']==TRIGGER_SHA,'receipt_binding')
    for n in ('remote_file_writes','permission_syscalls','database_open','service_actions','app_imports'):require(type(value[n]) is int and value[n]==0,'receipt_scope')
    require(value['activation'] is False and value['replay_allowed'] is False,'receipt_scope')
    if value['status']=='UNKNOWN_NO_RETRY':require(rc==3 and value['snapshot'] is None and value['reason'] in REASONS,'receipt_unknown');return value
    require(rc==0 and value['status']=='BOUNDARY_READBACK_COLLECTED_NOT_ADMITTED' and value['reason']=='bounded_private_metadata','receipt_status')
    s=value['snapshot'];require(isinstance(s,dict) and set(s)=={'parent_after','stage_root','objects','blocked_objects','repair_result','units_before','units_after'},'receipt_snapshot')
    parent,stage=expected_roots();require(s['parent_after']==parent and s['stage_root']==stage,'receipt_roots')
    require(s['units_before']==s['units_after']==v2.v1.witness()['units_before'],'receipt_units')
    require(s['repair_result']==dict(bytes=479,sha256=REPAIR_RESULT_SHA),'receipt_repair_result')
    require(isinstance(s['objects'],dict) and set(s['objects'])==set(NAMES),'receipt_objects')
    for name,m in s['objects'].items():
        require(isinstance(m,dict) and set(m)=={'kind','mode','uid','gid','device','inode','size','nlink','mtime_ns','ctime_ns','acl_clear','acl_count','private'},'receipt_object')
        for n in ('mode','uid','gid','device','inode','size','nlink','mtime_ns','ctime_ns','acl_count'):require(type(m[n]) is int and 0<=m[n]<2**63,'receipt_metadata')
        require(m['kind']==('directory' if name in ('payload','scratch') else 'file') and m['uid']==0 and m['mode']<=0o777 and not m['mode']&0o022 and (m['kind']=='directory' or m['nlink']==1) and 0<=m['acl_count']<=64,'receipt_metadata')
        require(type(m['acl_clear']) is bool and m['acl_clear']==(m['acl_count']==0) and type(m['private']) is bool and m['private']==(not m['mode']&0o077 and m['acl_clear']),'receipt_private')
    require(s['blocked_objects']==sorted(n for n,m in s['objects'].items() if not m['private']),'receipt_blocked')
    return value

def preview():
    m=expected_manifest();raw=script();wire(raw)
    return dict(status='OFFLINE_READY_NOT_EXECUTED',approval=APPROVAL,manifest_sha256=packet.core.digest(m),remote_sha256=packet.sha(raw),ssh_attempts=0,remote_seconds=REMOTE_SECONDS,transport_seconds=TRANSPORT_SECONDS,permission_syscalls=0,remote_file_writes=0)

def execute_once(manifest,*,approval,manifest_sha,remote_sha,loader):
    require(packet.core.encoded(manifest)==packet.core.encoded(expected_manifest()),'manifest_changed')
    require(approval==APPROVAL and manifest_sha==packet.core.digest(manifest) and remote_sha==packet.sha(script()),'approval_binding')
    require(not EVIDENCE.exists() and all(not p.is_symlink() for p in (EVIDENCE,*EVIDENCE.parents)),'claim_exists')
    target=loader('spain');require(target.role=='spain' and base.binding_digest(target)==packet.entry.binding.TARGET,'target_binding')
    argv=['C:/Windows/System32/OpenSSH/ssh.exe','-n','-T','-F','none','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(target.known_hosts_path),'-o','ConnectTimeout=10','-o','ConnectionAttempts=1','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=6','-i',str(target.key_path),'-p','22',target.target_user+'@'+target.target_host,wire(script())]
    require(base.old.command_units(argv)<=30000,'command_length')
    EVIDENCE.parent.mkdir(parents=True,exist_ok=True);EVIDENCE.mkdir()
    claim=dict(approval=APPROVAL,manifest_sha256=manifest_sha,remote_sha256=remote_sha,attempts=1,claimed_at=datetime.now(timezone.utc).isoformat());packet.core.write_new(EVIDENCE/'claim.json',packet.core.encoded(claim))
    result=dict(schema='phase16.private-boundary-readback-local.v1',status='UNKNOWN_NO_RETRY',claim=claim,transport={},receipt=None,replay_allowed=False)
    try:
        rc,out=packet.transport.run_transport(argv,cwd=EVIDENCE,env=base.ssh_environment(),timeout=TRANSPORT_SECONDS,cap=65536,input_bytes=b'',diagnostics=result['transport'])
        require(result['transport'].get('stdin_complete') is True and result['transport'].get('output_complete') is True,'transport_incomplete')
        value=validate_receipt(json.loads(out),rc);result['receipt']=value;result['status']=value['status']
    except Exception:result['reason']='TRANSPORT_OR_RECEIPT_UNVERIFIED'
    finally:packet.core.write_new(EVIDENCE/'result.json',packet.core.encoded(result))
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--approve');p.add_argument('--approved-manifest-sha256');p.add_argument('--approved-remote-sha256');a=p.parse_args()
    try:
        result=preview()
        if a.execute:
            from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
            result=execute_once(json.loads(MANIFEST.read_bytes()),approval=a.approve,manifest_sha=a.approved_manifest_sha256,remote_sha=a.approved_remote_sha256,loader=load_fixed_role_binding)
        print(json.dumps(result,indent=2));return 0 if result['status'] in ('OFFLINE_READY_NOT_EXECUTED','BOUNDARY_READBACK_COLLECTED_NOT_ADMITTED') else 3
    except Exception:print('{"status":"LOCAL_STOP"}');return 2
if __name__=='__main__':raise SystemExit(main())
