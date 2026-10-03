"""One proposed read-only readback after maintenance STOP. Default preview only.

Never executes the maintenance entry, permission apply, data jobs, app, DB,
service changes, replay or recovery. The original packet remains immutable.
"""
import argparse
import ast
import base64
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys
import time
import zlib
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts import phase16_bot_maintenance_packet as packet
from scripts import phase16_bot_stage_readback_gate as old
from scripts.phase16_bot_linux_gate import ssh_environment
from scripts.phase16_bot_readback_guard_gate import binding_digest
APPROVAL='PHASE16_BOT_MAINTENANCE_READBACK_20261003_001'
ORIGINAL='431bd0f93411651d6e604542e31aac40b55182dc2c947ef4c68ac7fe3c723eff'
MANIFEST=ROOT/'research/amn2/phase16-bot-maintenance-readback-manifest-2026-10-03.json'
EVIDENCE=Path('C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-maintenance-readback-20261003/execution-001')
REMOTE=r'''import hashlib,json,os,re,signal,stat,subprocess,sys,time
from pathlib import Path
OP='phase16-bot-maintenance-20261003-001'
DIRECTORY='/var/lib/amn2-spain/phase16-maintenance/'+OP
UNITS=('amn2-spain-bot.service','amn2-spain-web.service',OP+'-coordinator.service')
FIELDS=('Id','LoadState','ActiveState','SubState','MainPID','InvocationID','Result','ExecMainCode','ExecMainStatus','NRestarts')
NAMES=('upload-claim.json','packet-manifest.json','packet-result.json','host-admission.json','observation.json','ownership.json','worker-context.json','stop-witness.json','coordinator-context.json','coordinator-claim.json','coordinator-start.json','coordinator-result.json','coordinator-complete.json','sequence-claim.json','sequence-result.json','journal/manifest.json')+tuple('stage-access.'+OP+'.'+kind+'.json' for kind in ('claim','plan','intent','result'))
BOUNDARY='platform'
BOUNDARIES=('platform','boot','code_binding','unit_states','records','fences','readonly_probes')
# Frozen legacy collector preserves KeyboardInterrupt through BaseException cleanup.
class ReadbackDeadline(KeyboardInterrupt):pass
STATUSES=frozenset(('STOP','STOP_OR_UNKNOWN_NO_RETRY','SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE','APPLIED_DAC_VERIFIED_NOT_HOST_ADMITTED','PARTIAL_OR_UNKNOWN_NO_RETRY','NOT_APPLIED','PASS','FAIL'))

def safe_reason(error):
    return error.args[0] if len(error.args)==1 and isinstance(error.args[0],str) and error.args[0] in REASONS else 'UNCLASSIFIED_ERROR'

def summary(raw):
    value=json.loads(raw)
    if not isinstance(value,dict):raise ValueError('record_shape')
    result=value.get('result') if isinstance(value.get('result'),dict) else value
    return dict(status=result.get('status') if result.get('status') in STATUSES else None,
        reason=result.get('reason') if result.get('reason') in REASONS else None,
        phase=result.get('phase') if result.get('phase') in PHASES else None)

def unit_states():
    result={}
    for unit in UNITS:
        try:
            p=subprocess.run(['systemctl','show',unit,'--no-pager','--property='+','.join(FIELDS)],capture_output=True,timeout=5,check=True)
            if len(p.stdout)>16384:raise ValueError('unit_output')
            rows={}
            for line in p.stdout.decode('ascii').splitlines():
                key,value=line.split('=',1)
                if key not in FIELDS or key in rows or not re.fullmatch('[A-Za-z0-9_.:@/-]{0,128}',value):raise ValueError('unit_output')
                rows[key]=value
            if set(rows)!=set(FIELDS) or rows['Id'] not in ('',unit):raise ValueError('unit_output')
            result[unit]=dict(state='OBSERVED',properties=rows)
        except Exception:result[unit]=dict(state='UNAVAILABLE',properties={})
    return result

def probe(function):
    try:function();return dict(status='PASS',reason=None)
    except Exception as error:return dict(status='STOP',reason=safe_reason(error))

def metadata(path):
    # No bytes, DB open, link traversal, chown/chmod or creation.
    parsed=Path(path);fds=[];chain=[]
    try:
        fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);fds.append(fd)
        for part in parsed.parts[1:-1]:
            before=os.fstat(fd)
            new=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);fds.append(new)
            m=os.fstat(new)
            if m.st_uid!=0 or m.st_mode&0o022:raise ValueError('metadata_owner')
            chain.append((new,fd,part,m));fd=new
        m=os.stat(parsed.name,dir_fd=fd,follow_symlinks=False)
        for current,parent,name,before in chain:
            a=os.fstat(current);b=os.stat(name,dir_fd=parent,follow_symlinks=False)
            if (a.st_dev,a.st_ino,a.st_mode,a.st_uid,a.st_gid,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(before.st_dev,before.st_ino,before.st_mode,before.st_uid,before.st_gid,before.st_size,before.st_mtime_ns,before.st_ctime_ns) or a!=b:raise ValueError('metadata_changed')
        return dict(state='PRESENT',regular=stat.S_ISREG(m.st_mode),symlink=stat.S_ISLNK(m.st_mode),mode=stat.S_IMODE(m.st_mode),uid=m.st_uid,gid=m.st_gid,size=m.st_size)
    except FileNotFoundError:return dict(state='ABSENT')
    except Exception:return dict(state='UNREADABLE_OR_UNSUPPORTED')
    finally:
        for fd in reversed(fds):os.close(fd)

def collect():
    global BOUNDARY
    if sys.platform!='linux' or os.geteuid()!=0:raise ValueError('platform')
    BOUNDARY='boot'
    if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=BOOT:raise ValueError('boot_changed')
    BOUNDARY='code_binding'
    _phase16_import_root(DIRECTORY+'/code',PINS,ORIGINAL)
    from scripts.phase16_bot_maintenance_storage import MaintenanceReader
    from scripts import phase16_bot_maintenance_linux as linux
    from scripts import phase16_bot_host_admission as host
    from scripts import phase16_bot_candidate_admission as candidate
    from scripts import phase16_bot_legacy_runtime_proof as legacy
    BOUNDARY='unit_states'
    before=unit_states();records={};total=0
    BOUNDARY='records'
    with MaintenanceReader(DIRECTORY) as reader:
        for name in NAMES:
            try:
                raw=reader._file(name,16777216 if name=='host-admission.json' else 2097152,private=True)
                total+=len(raw)
                if total>41943040:raise ValueError('records_limit')
                if name=='packet-manifest.json' and hashlib.sha256(raw).hexdigest()!=ORIGINAL:raise ValueError('original_manifest')
                records[name]=dict(state='PRESENT',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),selected=summary(raw))
            except FileNotFoundError:records[name]=dict(state='ABSENT')
        # Only names/count/hash of the operation journal, no event body or DB rows.
        try:
            fd=reader.directory('journal',reader.root_fd)
            entries=os.listdir(fd)
            if len(entries)>64 or any(not isinstance(n,str) or len(n)>160 for n in entries):raise ValueError('journal_limit')
            journal=dict(state='PRESENT',entries=len(entries),names_sha256=hashlib.sha256(json.dumps(sorted(entries),ensure_ascii=True).encode()).hexdigest())
        except FileNotFoundError:journal=dict(state='ABSENT')
        reader.check_chain()
    BOUNDARY='fences'
    fences={u:dict(dropin=metadata('/etc/systemd/system/'+u+'.d/zz-'+OP+'.conf'),permit=metadata('/run/phase16/'+OP+'/'+u+'.allow')) for u in UNITS[:2]}
    BOUNDARY='readonly_probes'
    client=linux.SystemdClient(linux.BoundedCommand(maximum=65536))
    steps={}
    # Do not invoke the original root0700 stage observer after any access claim.
    early=records['stage-access.'+OP+'.claim.json']['state']=='ABSENT' and records['coordinator-claim.json']['state']=='ABSENT'
    if early:
        steps['unit_facts']=probe(lambda:host.unit_facts(client))
        if steps['unit_facts']['status']=='PASS':
            inventory=Path(DIRECTORY+'/code/research/amn2/phase16-bot-stage-readback-inventory-2026-09-29.json').read_bytes()
            steps['candidate_content']=probe(lambda:candidate.collect_live(client,inventory))
            if steps['candidate_content']['status']=='PASS':
                def old_proof():
                    proof=legacy.collect_live()
                    try:proof.check()
                    finally:proof.close()
                steps['legacy_content']=probe(old_proof)
    return dict(units_before=before,units_after=unit_states(),records=records,journal=journal,fences=fences,
        readonly_probes=steps,probe_scope='NO_APPLY_NO_DB_NO_APP_NO_SERVICE_ACTION',
        unobserved=['original exception detail','database migration correctness','pending/writer admission','live acceptance'])

def main(approval):
    result=dict(schema='phase16.maintenance-readback.v1',approval=APPROVAL,original_manifest_sha256=ORIGINAL,
        target_binding_sha256=TARGET,status='UNKNOWN_NO_RETRY',reason='platform_or_precondition',snapshot=None,
        failure_boundary=None,remote_file_writes=0,database_open=0,service_actions=0,app_imports=0,activation=False,replay_allowed=False)
    original_alarm=None
    try:
        if sys.platform!='linux' or os.geteuid()!=0:raise ValueError('platform')
        if approval!=APPROVAL:raise ValueError('approval')
        remaining=int(READBACK_STARTED+120-time.monotonic())
        if remaining<1:raise ReadbackDeadline('deadline')
        def alarm(*unused):raise ReadbackDeadline('deadline')
        original_alarm=signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM,alarm);signal.alarm(remaining)
        result['snapshot']=collect();result['status']='READBACK_COLLECTED_NOT_RECOVERY';result['reason']='bounded_observation'
    except (Exception,ReadbackDeadline) as error:
        reason=safe_reason(error)
        if reason!='UNCLASSIFIED_ERROR':result['reason']=reason
        result['failure_boundary']=BOUNDARY
    finally:
        if original_alarm is not None:
            signal.alarm(0);signal.signal(signal.SIGALRM,original_alarm)
    return result
if __name__=='__main__':
    value=main(sys.argv[1] if len(sys.argv)==2 else '')
    print(json.dumps(value,sort_keys=True,separators=(',',':')),flush=True)
    raise SystemExit(0 if value['status']=='READBACK_COLLECTED_NOT_RECOVERY' else 3)
'''

def require(value,reason):
    if not value:raise ValueError(reason)

def source_packet():
    value=packet.expected_manifest()
    require(packet.core.digest(value)==ORIGINAL,'original_packet_changed')
    return value

def literal_reasons():
    found={'host_unit_state','deadline','approval','boot_changed','original_manifest','records_limit','journal_limit','unit_output'}
    for name in source_packet()['files_sha256_lf']:
        if not name.endswith('.py'):continue
        for node in ast.walk(ast.parse(packet.canonical(ROOT/name))):
            if isinstance(node,ast.Raise) and isinstance(node.exc,ast.Call) and node.exc.args:
                value=node.exc.args[0]
                if isinstance(value,ast.Constant) and isinstance(value.value,str) and re.fullmatch('[a-z][a-z0-9_]{0,80}',value.value):found.add(value.value)
            if isinstance(node,ast.Call) and node.args and (getattr(node.func,'id',None)=='require' or getattr(node.func,'attr',None)=='require'):
                value=node.args[-1]
                if isinstance(value,ast.Constant) and isinstance(value.value,str) and re.fullmatch('[a-z][a-z0-9_]{0,80}',value.value):found.add(value.value)
    return sorted(found)

def script():
    value=source_packet()
    constants='\n'.join(name+'='+repr(value) for name,value in dict(APPROVAL=APPROVAL,ORIGINAL=ORIGINAL,TARGET=packet.entry.binding.TARGET,BOOT=packet.entry.BOOT,PINS=value['files_sha256_lf'],REASONS=literal_reasons(),PHASES=[packet.core.Journal._phase_at(i) for i in range(17)]).items())
    raw=(packet.storage.IMPORT_BOOTSTRAP+'\n'+constants+'\n'+REMOTE).encode()
    require(len(raw)<=131072,'remote_size');compile(raw,'<maintenance-readback>','exec');return raw

def remote_definitions():
    env={'__name__':'readback_fixture'};exec(compile(script(),'<maintenance-readback>','exec'),env);env['READBACK_STARTED']=time.monotonic();return env

def platform_fixture():
    from unittest.mock import patch
    env=remote_definitions()
    with patch.object(env['sys'],'platform','win32'):
        return env['main'](APPROVAL)

def wire(raw):
    compressed=zlib.compress(raw,9)
    launcher='import base64,hashlib,zlib,time;READBACK_STARTED=time.monotonic();data=base64.b64decode('+repr(base64.b64encode(compressed).decode())+',validate=True);assert hashlib.sha256(data).hexdigest()=='+repr(packet.sha(compressed))+';raw=zlib.decompress(data);assert len(raw)=='+str(len(raw))+' and hashlib.sha256(raw).hexdigest()=='+repr(packet.sha(raw))+';exec(compile(raw,"<maintenance-readback>","exec"),{"__name__":"__main__","READBACK_STARTED":READBACK_STARTED})'
    command='/usr/bin/python3 -I -S -B -c '+shlex.quote(launcher)+' '+APPROVAL
    require(old.command_units([command])+2048<=30000,'command_length');return command

def expected_manifest():
    value=source_packet();raw=script()
    return dict(schema='phase16.maintenance-readback-packet.v1',status='READY_NOT_EXECUTED',approval=APPROVAL,
        original_manifest_sha256=ORIGINAL,target_binding_sha256=packet.entry.binding.TARGET,remote_sha256=packet.sha(raw),
        gate_sha256_lf=packet.sha(packet.canonical(Path(__file__))),original_artifacts_sha256_lf={**value['files_sha256_lf'],**value['local_artifacts_sha256_lf']},
        limits=dict(ssh_attempts=1,remote_seconds=120,transport_seconds=150,output_bytes=65536),
        scope=dict(remote_file_writes=0,database_open=0,service_actions=0,app_imports=0,stage_install=0,activation=0,telegram=0),
        reads=['fixed saved operation JSON hashes and selected closed-schema status/phase/reason','operation journal names/count/hash','fixed fence/permit metadata','selected properties of bot/web/coordinator','when no access/coordinator claim exists: authenticated unit/candidate/legacy read-only proof steps'],
        prohibited=['maintenance entry execution','permission apply','data-worker or SQLite open','service start/stop/reload','candidate app import/execution','retry/replay/recovery/cleanup'],
        evidence_directory=EVIDENCE.as_posix())

def validate_receipt(value,rc):
    keys={'schema','approval','original_manifest_sha256','target_binding_sha256','status','reason','snapshot','failure_boundary','remote_file_writes','database_open','service_actions','app_imports','activation','replay_allowed'}
    require(isinstance(value,dict) and set(value)==keys,'receipt_shape')
    require(value['schema']=='phase16.maintenance-readback.v1' and value['approval']==APPROVAL and value['original_manifest_sha256']==ORIGINAL and value['target_binding_sha256']==packet.entry.binding.TARGET,'receipt_binding')
    for key in ('remote_file_writes','database_open','service_actions','app_imports'):require(type(value[key]) is int and value[key]==0,'receipt_scope')
    require(value['activation'] is False and value['replay_allowed'] is False,'receipt_scope')
    if value['status']=='UNKNOWN_NO_RETRY':require(rc==3 and value['reason'] in set(literal_reasons())|{'platform_or_precondition'} and value['failure_boundary'] in remote_definitions()['BOUNDARIES'] and value['snapshot'] is None,'receipt_unknown');return value
    require(value['failure_boundary'] is None,'receipt_boundary')
    require(rc==0 and value['status']=='READBACK_COLLECTED_NOT_RECOVERY' and value['reason']=='bounded_observation','receipt_status')
    s=value['snapshot'];env=remote_definitions()
    require(isinstance(s,dict) and set(s)=={'units_before','units_after','records','journal','fences','readonly_probes','probe_scope','unobserved'},'receipt_snapshot')
    require(s['probe_scope']=='NO_APPLY_NO_DB_NO_APP_NO_SERVICE_ACTION' and s['unobserved']==['original exception detail','database migration correctness','pending/writer admission','live acceptance'],'receipt_claims')
    for field in ('units_before','units_after'):
        require(set(s[field])==set(env['UNITS']),'receipt_units')
        for unit,item in s[field].items():
            require(set(item)=={'state','properties'} and item['state'] in ('OBSERVED','UNAVAILABLE'),'receipt_units')
            require(item['properties']=={} if item['state']=='UNAVAILABLE' else set(item['properties'])==set(env['FIELDS']),'receipt_units')
            for val in item['properties'].values():require(isinstance(val,str) and re.fullmatch('[A-Za-z0-9_.:@/-]{0,128}',val),'receipt_units')
    require(set(s['records'])==set(env['NAMES']),'receipt_records')
    for item in s['records'].values():
        if item.get('state')=='ABSENT':require(item=={'state':'ABSENT'},'receipt_record');continue
        require(set(item)=={'state','bytes','sha256','selected'} and item['state']=='PRESENT' and type(item['bytes']) is int and 0<=item['bytes']<=16777216 and re.fullmatch('[0-9a-f]{64}',item['sha256']),'receipt_record')
        selected=item['selected'];require(set(selected)=={'status','reason','phase'},'receipt_record')
        require(selected['status'] is None or selected['status'] in env['STATUSES'],'receipt_record')
        require(selected['reason'] is None or selected['reason'] in env['REASONS'],'receipt_record')
        require(selected['phase'] is None or selected['phase'] in env['PHASES'],'receipt_record')
    require(set(s['readonly_probes'])<= {'unit_facts','candidate_content','legacy_content'},'receipt_probes')
    for item in s['readonly_probes'].values():require(set(item)=={'status','reason'} and (item==dict(status='PASS',reason=None) or item['status']=='STOP' and item['reason'] in set(env['REASONS'])|{'UNCLASSIFIED_ERROR'}),'receipt_probes')
    require(s['journal']=={'state':'ABSENT'} or set(s['journal'])=={'state','entries','names_sha256'} and s['journal']['state']=='PRESENT' and type(s['journal']['entries']) is int and 0<=s['journal']['entries']<=64 and re.fullmatch('[0-9a-f]{64}',s['journal']['names_sha256']),'receipt_journal')
    require(set(s['fences'])==set(env['UNITS'][:2]),'receipt_fences')
    for item in s['fences'].values():
        require(set(item)=={'dropin','permit'},'receipt_fences')
        for meta in item.values():
            if meta.get('state')!='PRESENT':require(meta in ({'state':'ABSENT'},{'state':'UNREADABLE_OR_UNSUPPORTED'}),'receipt_metadata');continue
            require(set(meta)=={'state','regular','symlink','mode','uid','gid','size'} and type(meta['regular']) is type(meta['symlink']) is bool,'receipt_metadata')
            for key in ('mode','uid','gid','size'):require(type(meta[key]) is int and 0<=meta[key]<2**63,'receipt_metadata')
    return value

def preview():
    value=expected_manifest();raw=script();wire(raw)
    return dict(status='OFFLINE_READY_NOT_EXECUTED',approval=APPROVAL,manifest_sha256=packet.core.digest(value),remote_sha256=packet.sha(raw),ssh_attempts=0,remote_seconds=120,transport_seconds=150,database_open=0,remote_file_writes=0,service_actions=0)

def execute_once(manifest,*,approval,manifest_sha,remote_sha,loader):
    require(packet.core.encoded(manifest)==packet.core.encoded(expected_manifest()),'manifest_changed')
    require(approval==APPROVAL and manifest_sha==packet.core.digest(manifest) and remote_sha==packet.sha(script()),'approval_binding')
    require(not EVIDENCE.exists() and all(not p.is_symlink() for p in (EVIDENCE,*EVIDENCE.parents)),'claim_exists')
    target=loader('spain');require(target.role=='spain' and binding_digest(target)==packet.entry.binding.TARGET,'target_binding')
    argv=['C:/Windows/System32/OpenSSH/ssh.exe','-n','-T','-F','none','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(target.known_hosts_path),'-o','ConnectTimeout=10','-o','ConnectionAttempts=1','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=6','-i',str(target.key_path),'-p','22',target.target_user+'@'+target.target_host,wire(script())]
    require(old.command_units(argv)<=30000,'command_length')
    EVIDENCE.parent.mkdir(parents=True,exist_ok=True);EVIDENCE.mkdir()
    claim=dict(approval=APPROVAL,manifest_sha256=manifest_sha,remote_sha256=remote_sha,attempts=1,claimed_at=datetime.now(timezone.utc).isoformat())
    packet.core.write_new(EVIDENCE/'claim.json',packet.core.encoded(claim))
    result=dict(schema='phase16.maintenance-readback-local.v1',status='UNKNOWN_NO_RETRY',claim=claim,transport={},receipt=None,replay_allowed=False)
    try:
        rc,out=packet.transport.run_transport(argv,cwd=EVIDENCE,env=ssh_environment(),timeout=150,cap=65536,input_bytes=b'',diagnostics=result['transport'])
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
        print(json.dumps(result,indent=2));return 0 if result['status'] in ('OFFLINE_READY_NOT_EXECUTED','READBACK_COLLECTED_NOT_RECOVERY') else 3
    except Exception:print('{"status":"LOCAL_STOP"}');return 2
if __name__=='__main__':raise SystemExit(main())
