"""One exact-bound maintenance packet. Default is offline preview only.

Uploads maintenance Python/resources, never rebuilds/uploads candidate/package016.
A single approved SSH may prepare root-private records, change the retained stage
DAC, stop bot/web, back up/rehearse/migrate, switch bot, restart web and release.
No retries, automatic restore/replay, token rotation or cleanup of retained evidence.
"""
import argparse
import base64
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shlex
import sys
import zlib
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts import phase16_bot_maintenance_entry as entry
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_transport as transport
from scripts import phase16_bot_maintenance_storage as storage
from scripts import phase16_bot_stage_readback_gate as old_transport
from scripts.phase16_bot_linux_gate import ssh_environment
from scripts.phase16_bot_readback_guard_gate import binding_digest

MANIFEST=ROOT/'research/amn2/phase16-bot-maintenance-packet-2026-10-03.json'
EVIDENCE=Path('C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-maintenance-20261003/execution-001')
MAX_PAYLOAD=2*1024*1024
MAX_RAW=4*1024*1024
BOOTSTRAP=r'''import base64,hashlib,json,os,pathlib,signal,stat,sys,time,zlib
fds=[];chain=[]
def check(value,reason):
 if not value:raise ValueError(reason)
def fp(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def guard():
 for fd,parent,name,before in chain:
  check(fp(os.fstat(fd))==fp(before)==fp(os.stat(name,dir_fd=parent,follow_symlinks=False)),"path_changed")
def directory(name,parent,path,create=False,exclusive=False):
 if create:
  try:os.mkdir(name,0o700,dir_fd=parent)
  except FileExistsError:check(not exclusive,"operation_exists")
 fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
 fds.append(fd);m=os.fstat(fd)
 service=path=="/var/lib/amn2-spain" and m.st_uid==m.st_gid==61212 and stat.S_IMODE(m.st_mode)==0o750
 check(stat.S_ISDIR(m.st_mode) and (service or (m.st_uid==0 and not m.st_mode&0o022)),"directory_owner")
 if create:check(m.st_uid==m.st_gid==0 and stat.S_IMODE(m.st_mode)==0o700,"private_directory")
 chain.append((fd,parent,name,m));return fd
def refresh_owned_parent(fd):
 for i,(current,parent,name,before) in enumerate(chain):
  if current==fd:
   after=os.fstat(fd)
   check((before.st_dev,before.st_ino,before.st_mode,before.st_uid,before.st_gid)==(after.st_dev,after.st_ino,after.st_mode,after.st_uid,after.st_gid),"parent_changed")
   chain[i]=(current,parent,name,after)
def child(name,parent,path,exclusive=False):
 guard();fd=directory(name,parent,path,True,exclusive);refresh_owned_parent(parent);guard();os.fsync(parent);return fd
def put(parent,name,data):
 guard();fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=parent)
 try:
  offset=0
  while offset<len(data):
   n=os.write(fd,data[offset:]);check(n>0,"write");offset+=n
  os.fsync(fd)
 finally:os.close(fd)
 refresh_owned_parent(parent);os.fsync(parent);guard()
def alarm(*unused):raise ValueError("bootstrap_deadline")
try:
 check(sys.platform=="linux" and os.geteuid()==0,"platform")
 os.umask(0o077);signal.signal(signal.SIGALRM,alarm);signal.alarm(60)
 rawhead=sys.stdin.buffer.read(8);check(rawhead.isdigit(),"frame")
 n=int(rawhead);check(0<n<=2097152,"frame")
 packed=sys.stdin.buffer.read(n);check(len(packed)==n and sys.stdin.buffer.read(1)==b"","frame")
 check(hashlib.sha256(packed).hexdigest()==PAYLOAD_SHA,"frame_binding")
 decoder=zlib.decompressobj();raw=decoder.decompress(packed,4194305)
 check(len(raw)<=4194304 and decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data,"payload_limit")
 packet=json.loads(raw);manifest=packet["manifest"]
 encoded=lambda v:(json.dumps(v,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
 check(set(packet)=={"manifest","files"} and hashlib.sha256(encoded(manifest)).hexdigest()==MANIFEST_SHA,"manifest_binding")
 check(set(packet["files"])==set(manifest["files_sha256_lf"]),"file_inventory")
 check(pathlib.Path("/proc/sys/kernel/random/boot_id").read_text().strip()==manifest["request"]["expected_boot_id"],"boot_changed")
 contents={};total=0
 for name,body in packet["files"].items():
  check(isinstance(name,str) and not name.startswith("/") and all(p not in ("",".","..") for p in name.split("/")) and "\\" not in name and ":" not in name,"file_path")
  data=base64.b64decode(body,validate=True);total+=len(data)
  check(len(data)<=2097152 and total<=4194304 and hashlib.sha256(data).hexdigest()==manifest["files_sha256_lf"][name],"file_binding")
  contents[name]=data
 root=directory("/",None,"/")
 var=directory("var",root,"/var");lib=directory("lib",var,"/var/lib")
 app=directory("amn2-spain",lib,"/var/lib/amn2-spain")
 base=child("phase16-maintenance",app,"/var/lib/amn2-spain/phase16-maintenance")
 operation=manifest["request"]["operation_id"]
 check(operation=="phase16-bot-maintenance-20261003-001","operation")
 path="/var/lib/amn2-spain/phase16-maintenance/"+operation
 op=child(operation,base,path,True);code=child("code",op,path+"/code",True)
 put(op,"upload-claim.json",encoded({"manifest_sha256":MANIFEST_SHA,"payload_sha256":PAYLOAD_SHA,"attempts":1}))
 paths={"":code}
 for name,data in sorted(contents.items()):
  parts=name.split("/");prefix="";fd=code
  for part in parts[:-1]:
   prefix=(prefix+"/"+part).strip("/")
   if prefix not in paths:paths[prefix]=child(part,fd,path+"/code/"+prefix)
   fd=paths[prefix]
  put(fd,parts[-1],data)
 put(op,"packet-manifest.json",encoded(manifest))
 run=directory("run",root,"/run")
 # /run/phase16 is the dedicated parent required before systemd ReadWritePaths.
 try:phase=directory("phase16",run,"/run/phase16")
 except FileNotFoundError:phase=child("phase16",run,"/run/phase16",True)
 guard();signal.alarm(0)
 _phase16_import_root(path+"/code",manifest["files_sha256_lf"],MANIFEST_SHA)
 from scripts.phase16_bot_maintenance_entry import execute
 status=execute(manifest,MANIFEST_SHA,path+"/code",path,overall_deadline=STARTED+1560)
 raise SystemExit(status)
except Exception as error:
 reason="platform" if isinstance(error,ValueError) and str(error)=="platform" else "bootstrap_or_entry_failed"
 print(json.dumps({"status":"STOP_OR_UNKNOWN_NO_RETRY","reason":reason},separators=(",",":")),flush=True)
 raise SystemExit(3)
finally:
 for fd in reversed(fds):
  try:os.close(fd)
  except OSError:pass
'''


def canonical(path):return Path(path).read_bytes().replace(b'\r\n',b'\n')
def sha(raw):return hashlib.sha256(raw).hexdigest()

def expected_manifest():
    entry.binding.validate_packet()
    files=sorted(set(entry.coordinator.WORKER_FILES)|set(entry.EXTRA)|set(entry.RESOURCES))
    local=('scripts/phase16_bot_maintenance_packet.py','scripts/phase16_bot_maintenance_transport.py')
    return dict(schema='phase16.complete-maintenance-packet.v1',status='READY_NOT_EXECUTED',
        request=entry.request(),files_sha256_lf={name:sha(canonical(ROOT/name)) for name in files},
        local_artifacts_sha256_lf={name:sha(canonical(ROOT/name)) for name in local},
        limits=dict(preflight_seconds=600,coordinator_runtime_seconds=900,coordinator_wait_seconds=930,
            remote_seconds=1560,transport_seconds=1590,input_bytes=MAX_PAYLOAD,output_bytes=65536,ssh_attempts=1),
        owner_statement='Only bot/web application writers; no other application cron/agent/timer/socket; manual tasks paused; external Telegram pollers excluded for the complete 45-minute window.',
        trust_boundary='EXISTING_OS_AND_ROOT_OPERATOR',
        mutations=['new root-private maintenance code/evidence and /run/phase16 parent',
            'retained stage exact verified content group read/traverse and private wrapper sealing',
            'owned bot/web start fence; clean stop web then bot',
            'new SQLite backup and isolated rehearsal; approved live migration',
            'candidate bot drop-in/start with 39-second observation budget; original web start; fence release'],
        preserved=['AWG2','immutable package016','general issuance disabled','bot identity and token'],
        prohibited=['token rotation','automatic retry/replay/restore','candidate rebuild/reinstall','other branches/tags/force push'],
        artifacts_not_live_acceptance=True)


def validate_manifest(value):core.require(core.encoded(value)==core.encoded(expected_manifest()),'packet_manifest')
def payload(manifest):
    validate_manifest(manifest)
    value=dict(manifest=manifest,files={name:base64.b64encode(canonical(ROOT/name)).decode('ascii') for name in manifest['files_sha256_lf']})
    raw=core.encoded(value);core.require(len(raw)<=MAX_RAW,'packet_size')
    packed=zlib.compress(raw,9);core.require(0<len(packed)<=MAX_PAYLOAD-8,'packet_size');return packed

def decode_payload(packed):
    core.require(isinstance(packed,bytes) and len(packed)<=MAX_PAYLOAD,'packet_size')
    decoder=zlib.decompressobj();raw=decoder.decompress(packed,MAX_RAW+1)
    core.require(len(raw)<=MAX_RAW and decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data,'packet_size')
    return json.loads(raw)

def frame(packed):return f'{len(packed):08d}'.encode('ascii')+packed

def bootstrap(packed,manifest):
    result='import time\nSTARTED=time.monotonic()\nPAYLOAD_SHA='+repr(sha(packed))+'\nMANIFEST_SHA='+repr(core.digest(manifest))+'\n'+storage.IMPORT_BOOTSTRAP+'\n'+BOOTSTRAP
    compile(result,'<phase16-maintenance-bootstrap>','exec');return result

def preview():
    manifest=expected_manifest();packed=payload(manifest);launcher=bootstrap(packed,manifest)
    command='/usr/bin/python3 -I -S -B -c '+shlex.quote(launcher)
    core.require(old_transport.command_units([command])+2048<=30000,'packet_command_length')
    return dict(status='READY_FOR_EXACT_APPROVAL_NOT_EXECUTED',approval=entry.APPROVAL,
        manifest_sha256=core.digest(manifest),payload_sha256=sha(packed),bootstrap_sha256=sha(launcher.encode()),
        frame_bytes=len(frame(packed)),code_files=len(manifest['files_sha256_lf']),ssh_attempts=0,
        remote_seconds=1560,transport_seconds=1590,owner_statement_required=True,live_acceptance=False)


def validate_receipt(receipt,rc,manifest_sha256):
    from scripts import phase16_bot_maintenance_sequence as sequence
    require=core.require
    require(type(rc) is int and isinstance(receipt,dict),'packet_receipt')
    if set(receipt)=={'status','reason'}:
        require(rc==3 and receipt['status']=='STOP_OR_UNKNOWN_NO_RETRY' and
            receipt['reason'] in ('platform','bootstrap_or_entry_failed'),'packet_receipt')
        return False
    require(set(receipt)=={'schema','approval','operation_id','manifest_sha256','target_binding_sha256',
        'result','awg2','package016','general_issuance','automatic_replay'},'packet_receipt')
    require(receipt['schema']=='phase16.maintenance-packet-result.v1' and receipt['approval']==entry.APPROVAL and
        receipt['operation_id']==entry.OPERATION and receipt['manifest_sha256']==manifest_sha256 and
        receipt['target_binding_sha256']==entry.binding.TARGET and receipt['awg2']=='UNTOUCHED' and
        receipt['package016']=='UNCHANGED' and receipt['general_issuance']=='DISABLED' and
        receipt['automatic_replay'] is False,'packet_receipt')
    result=receipt['result'];require(isinstance(result,dict),'packet_receipt')
    require(result.get('automatic_recovery')=='DISABLED' and result.get('live_acceptance')=='NOT_ESTABLISHED','packet_receipt')
    if result.get('status')=='STOP_OR_UNKNOWN_NO_RETRY':
        require(rc==3 and result==dict(status='STOP_OR_UNKNOWN_NO_RETRY',reason='packet_precondition_or_execution_failed',
            automatic_recovery='DISABLED',live_acceptance='NOT_ESTABLISHED',
            recovery_route='INSPECT_RETAINED_INTENTS_AND_MANAGER_STATE'),'packet_receipt');return False
    require(set(result)=={'status','phase','candidate_start_requested','recovery_route','automatic_recovery','live_acceptance','reason'},'packet_receipt')
    if result['status']=='SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE':
        require(rc==0 and result['phase']=='release_done' and result['candidate_start_requested'] is True and
            result['recovery_route']=='NOT_REQUIRED' and result['reason']=='all_operations_verified','packet_receipt')
        return True
    phases=[core.Journal._phase_at(i) for i in range(17)]
    require(rc==3 and result['status']=='STOP' and result['phase'] in phases and
        type(result['candidate_start_requested']) is bool and
        result['candidate_start_requested']==(phases.index(result['phase'])>=11) and
        result['reason'] in sequence.SAFE_REASONS|{'sequence_precondition_or_operation_failed'},'packet_receipt')
    expected_route=('PRESERVE_DB_MANUAL_RECOVERY' if result['candidate_start_requested'] else
        'LEAVE_OLD_RUNTIME' if result['phase']=='prepared' else 'HOLD_FENCE_MANUAL_RECOVERY')
    require(result['recovery_route']==expected_route,'packet_receipt')
    return False


def execute_once(manifest,*,approval,approved_manifest_sha256,approved_payload_sha256,loader,run=transport.run_transport):
    validate_manifest(manifest);packed=payload(manifest)
    core.require(approval==entry.APPROVAL and approved_manifest_sha256==core.digest(manifest) and
        approved_payload_sha256==sha(packed),'packet_approval')
    core.require(not EVIDENCE.exists() and all(not p.is_symlink() for p in (EVIDENCE,*EVIDENCE.parents)),'packet_local_claim')
    target=loader('spain')
    core.require(target.role=='spain' and binding_digest(target)==entry.binding.TARGET,'packet_target')
    command='/usr/bin/python3 -I -S -B -c '+shlex.quote(bootstrap(packed,manifest))
    argv=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-F','none','-o','BatchMode=yes','-o','IdentitiesOnly=yes',
        '-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(target.known_hosts_path),
        '-o','ConnectTimeout=10','-o','ConnectionAttempts=1','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=6',
        '-i',str(target.key_path),'-p','22',target.target_user+'@'+target.target_host,command]
    core.require(old_transport.command_units(argv)<=30000,'packet_command_length')
    EVIDENCE.parent.mkdir(parents=True,exist_ok=True);EVIDENCE.mkdir()
    claim=dict(approval=approval,manifest_sha256=approved_manifest_sha256,payload_sha256=approved_payload_sha256,
        target_binding_sha256=entry.binding.TARGET,attempts=1,claimed_at=datetime.now(timezone.utc).isoformat())
    core.write_new(EVIDENCE/'claim.json',core.encoded(claim))
    result=dict(schema='phase16.maintenance-local-result.v1',status='UNKNOWN_NO_RETRY',claim=claim,
        transport={},receipt=None,replay_allowed=False)
    try:
        rc,out=run(argv,cwd=EVIDENCE,env=ssh_environment(),timeout=1590,cap=65536,input_bytes=frame(packed),diagnostics=result['transport'])
        receipt=json.loads(out)
        core.require(result['transport'].get('stdin_complete') is True and result['transport'].get('output_complete') is True,'packet_transport')
        if validate_receipt(receipt,rc,approved_manifest_sha256):result['status']='SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE'
        result['receipt']=receipt
    except Exception:result['reason']='TRANSPORT_OR_RECEIPT_UNKNOWN_REMOTE_MAY_CONTINUE'
    finally:core.write_new(EVIDENCE/'result.json',core.encoded(result))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true');parser.add_argument('--approve')
    parser.add_argument('--approved-manifest-sha256');parser.add_argument('--approved-payload-sha256')
    args=parser.parse_args()
    try:
        result=preview()
        if args.execute:
            from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
            manifest=json.loads(canonical(MANIFEST))
            result=execute_once(manifest,approval=args.approve,approved_manifest_sha256=args.approved_manifest_sha256,
                approved_payload_sha256=args.approved_payload_sha256,loader=load_fixed_role_binding)
        print(json.dumps(result,indent=2));return 0 if result['status'] in ('READY_FOR_EXACT_APPROVAL_NOT_EXECUTED','SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE') else 3
    except Exception:
        print('{"status":"LOCAL_STOP","reason":"packet_not_verified"}');return 2
if __name__=='__main__':raise SystemExit(main())
