"""Offline preview; one exact-approved facts read, never a maintenance execution."""
import argparse
import base64
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import zlib
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts import phase16_bot_stage_readback_gate as transport_base
from scripts.vps import phase16_maintenance_facts_remote as remote
from scripts.phase16_bot_transport_diagnostics import run_transport
from scripts.phase16_bot_linux_gate import ssh_environment
from scripts.phase16_bot_readback_guard_gate import binding_digest
require=remote.require
MANIFEST=ROOT/'research/amn2/phase16-maintenance-facts-manifest-2026-10-02.json'
EVIDENCE=Path('C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-maintenance-facts-20261002/execution-001')

def canonical(path):return Path(path).read_bytes().replace(b'\r\n',b'\n')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode('ascii')
def script():
    body=canonical(ROOT/'scripts/vps/phase16_maintenance_facts_remote.py').decode('utf-8')
    replacements={
        'from scripts.phase16_bot_maintenance_linux import BoundedCommand':
            transport_base.definitions('scripts/phase16_bot_maintenance_linux.py',['BoundedCommand']),
        'from scripts.phase16_bot_service_operations import LAUNCH_FIELDS, launch_fingerprint':
            'LAUNCH_FIELDS='+repr(remote.LAUNCH_FIELDS)+'\n'+
            transport_base.definitions('scripts/phase16_bot_service_operations.py',['launch_fingerprint'])}
    for old,new in replacements.items():require(body.count(old)==1,'render');body=body.replace(old,new)
    raw=body.encode('utf-8');require(0<len(raw)<=131072,'render');compile(raw,'<maintenance-facts>','exec');return raw

def wire(raw):
    packed=zlib.compress(raw,9)
    bootstrap=('import base64,hashlib,sys,zlib;p=base64.b64decode("'+base64.b64encode(packed).decode()+'",validate=True);'
        'hashlib.sha256(p).hexdigest()=="'+sha(packed)+'" or sys.exit(70);s=zlib.decompress(p);'
        'len(s)=='+str(len(raw))+' and hashlib.sha256(s).hexdigest()=="'+sha(raw)+'" or sys.exit(70);'
        'exec(compile(s,"<maintenance-facts>","exec"),{"__name__":"__main__"})')
    command='/usr/bin/python3 -I -S -B -c '+shlex.quote(bootstrap)+' '+remote.APPROVAL
    require(transport_base.command_units([command])+2048<=30000,'command_length')
    return command,bootstrap

def expected_manifest():
    paths=set(transport_base.expected_manifest()['artifacts_sha256_lf'])|{
        'scripts/phase16_maintenance_facts_gate.py','scripts/vps/phase16_maintenance_facts_remote.py',
        'scripts/phase16_bot_maintenance_linux.py','scripts/phase16_bot_service_operations.py',
        'scripts/phase16_bot_maintenance.py','scripts/phase16_bot_maintenance_jobs.py',
        'scripts/phase16_bot_maintenance_binding.py','scripts/phase16_legacy_stop_policy.py',
        'scripts/phase16_bot_maintenance_operations.py','scripts/phase16_bot_db_rehearsal.py'}
    return dict(schema='phase16.maintenance-facts-packet.v1',status='READY_NOT_EXECUTED',
        approval=remote.APPROVAL,base_commit='b8a2900e2cf2857240fde83c120704ba917abf07',
        target_binding_sha256=remote.TARGET,remote_sha256=sha(script()),
        artifacts_sha256_lf={p:sha(canonical(ROOT/p)) for p in sorted(paths)},
        limits=dict(ssh_attempts=1,remote_seconds=45,transport_seconds=60,output_bytes=65536,windows_command_units=30000),
        evidence_directory=EVIDENCE.as_posix(),
        reads=['bot/web systemd properties and launch hashes','selected process environment fields, values allowlisted',
            'fixed old-source .env: literal selected fields only; unsupported syntax UNKNOWN',
            'old/candidate settings.py hashes','unit-file names, cron file hashes/reference flags, process command hashes','boot identity'],
        scope=dict(remote_file_writes=0,database_open=0,service_actions=0,app_imports=0,
            candidate_execution=0,stage=0,install=0,activation=0,telegram=0),
        boundaries=['NOT_HOST_ADMISSION','NO_SETTINGS_DEFAULT_GUESS','NO_WRITER_ABSENCE_FROM_STATIC_SCAN',
            'NO_INSTALLED_BINARY_INTEGRITY_CLAIM','NO_STARTUP_BOUND_CLAIM','NO_RETRY'],
        ssh=dict(stdin='DEVNULL',connection_attempts=1,connect_timeout=10,server_alive_interval=5,server_alive_count_max=6,
            host_key='STRICT_PINNED',port=22,config='none'))

def validate_manifest(value):require(encode(value)==encode(expected_manifest()),'manifest_binding')
def validate_receipt(value):
    require(isinstance(value,dict),'receipt')
    fields={'schema','approval','target_binding_sha256','status','reason','facts','remote_writes',
        'database_opened','service_actions','application_imports','activation','live_admission'}
    success=value.get('status')=='FACTS_COLLECTED_NOT_ADMITTED'
    require(set(value)==fields|({'completed_at'} if success else set()),'receipt')
    require(value['schema']=='phase16.maintenance-facts.v1' and value['approval']==remote.APPROVAL
            and value['target_binding_sha256']==remote.TARGET,'receipt_binding')
    for name in ('remote_writes','service_actions','application_imports'):require(type(value[name]) is int and value[name]==0,'receipt_scope')
    for name in ('database_opened','activation','live_admission'):require(value[name] is False,'receipt_scope')
    if not success:
        require(value['status']=='UNKNOWN' and value['facts'] is None and value['reason'] in remote.REASONS,'receipt_unknown');return value
    require(value['reason']=='bounded_observation' and isinstance(value['facts'],dict),'receipt')
    datetime.fromisoformat(value['completed_at'])
    f=value['facts']
    require(set(f)=={'boot_id','units','launch_sha256','process_environment','dotenv_selected','settings_source_sha256','inventory',
        'effective_settings','startup_bound','installed_binary_integrity'},'receipt_facts')
    require(f['effective_settings']=='REQUIRES_SOURCE_AND_ENVIRONMENT_PRECEDENCE_REVIEW'
        and f['startup_bound']==f['installed_binary_integrity']=='NOT_ESTABLISHED','receipt_claim')
    require(set(f['units'])==set(f['launch_sha256'])==set(f['process_environment'])==set(remote.UNITS),'receipt_units')
    require(re.fullmatch('[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',f['boot_id']),'receipt_boot')
    for digest in f['launch_sha256'].values():require(isinstance(digest,str) and re.fullmatch('[0-9a-f]{64}',digest),'receipt_hash')
    require(f['inventory']['writer_exclusion']=='NOT_ESTABLISHED_BY_STATIC_SCAN'
        and f['inventory']['external_pollers']=='REQUIRES_OPERATOR_OWNERSHIP'
        and f['inventory']['opaque_wrappers']=='REQUIRES_REVIEW','receipt_inventory')
    for unit,v in f['units'].items():
        require(isinstance(v,dict) and set(v)==set(remote.FIELDS)-{'WorkingDirectory','ControlGroup'}|{'cwd_expected','cgroup_expected'},'receipt_unit_shape')
        require(v['Id']==unit and type(v['cwd_expected']) is bool and type(v['cgroup_expected']) is bool,'receipt_units')
        for key,item in v.items():
            if key in ('cwd_expected','cgroup_expected'):continue
            require(isinstance(item,str) and re.fullmatch('[A-Za-z0-9_.$ /-]{0,128}',item),'receipt_unit_value')
    def settings(v):
        require(isinstance(v,dict) and set(v)==remote.KEYS,'receipt_settings')
        for key,item in v.items():
            require(isinstance(item,dict) and item.get('status') in ('ABSENT','AMBIGUOUS','UNSUPPORTED','VALID'),'receipt_settings')
            if item['status']!='VALID':require(set(item)=={'status'},'receipt_settings');continue
            require(set(item)=={'status','value'},'receipt_settings')
            value=item['value']
            if key in ('VPS_APPLY_ENABLED','AWG3_BOOTSTRAP_ENABLED','DATABASE_PATH'):require(type(value) is bool,'receipt_settings')
            elif key in ('WEB_ADMIN_PORT','TELEGRAM_ADMISSION_TIMEOUT_SECONDS'):
                require(type(value) is int and 1<=value<=(65535 if key=='WEB_ADMIN_PORT' else 120),'receipt_settings')
            else:
                require(isinstance(value,str) and remote.selected([(key,value)])[key]==item,'receipt_settings')
    for setting in f['process_environment'].values():settings(setting)
    if f['dotenv_selected'] is not None and f['dotenv_selected']!='ABSENT':settings(f['dotenv_selected'])
    require(f['settings_source_sha256']==dict(old='1db81553dbcbf4dafc710efdd69c2db0cc1a869f0754d7bb67c7adfa3dcac631',
        candidate='6cb3ef9889422dc4d229ef90a5c558ddd100290253b77a8a6525f91676f5b9fe'),'receipt_source')
    inv=f['inventory']
    require(set(inv)=={'unit_count','unit_names_sha256','related_units','cron_files','cron','process_count','related_processes',
        'exited_during_scan','writer_exclusion','external_pollers','opaque_wrappers'},'receipt_inventory')
    for key,maximum in [('unit_count',1024),('cron_files',256),('process_count',4096),('exited_during_scan',4096)]:
        require(type(inv[key]) is int and 0<=inv[key]<=maximum,'receipt_inventory')
    hex64=lambda v:isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v)
    require(hex64(inv['unit_names_sha256']) and isinstance(inv['cron'],dict) and len(inv['cron'])==inv['cron_files'],'receipt_inventory')
    for path,v in inv['cron'].items():
        require(hex64(path) and set(v)=={'sha256','amn2_reference'} and hex64(v['sha256']) and type(v['amn2_reference']) is bool,'receipt_inventory')
    require(isinstance(inv['related_units'],list) and len(inv['related_units'])<=64,'receipt_inventory')
    for unit in inv['related_units']:
        require(isinstance(unit,str) and re.fullmatch(r'[A-Za-z0-9_.:@\\-]+\.(service|timer|socket)',unit),'receipt_inventory')
    require(isinstance(inv['related_processes'],list) and len(inv['related_processes'])<=128,'receipt_inventory')
    for v in inv['related_processes']:
        require(set(v)=={'pid','command_sha256'} and type(v['pid']) is int and v['pid']>0 and hex64(v['command_sha256']),'receipt_inventory')
    return value

def parse(raw):
    require(isinstance(raw,bytes) and len(raw)<=65536 and raw.endswith(b'\n') and len(raw.splitlines())==1,'receipt_transport')
    def pairs(items):
        value={}
        for k,v in items:require(k not in value,'receipt_duplicate');value[k]=v
        return value
    return validate_receipt(json.loads(raw,object_pairs_hook=pairs))

def execute_once(manifest,*,approval,approved_manifest_sha,approved_remote_sha,loader,
                 transport=run_transport,binding_hasher=binding_digest):
    validate_manifest(manifest);raw=script()
    require(approval==remote.APPROVAL and approved_manifest_sha==sha(encode(manifest))
            and approved_remote_sha==sha(raw),'approval_binding')
    require(not EVIDENCE.exists() and all(not p.is_symlink() for p in (EVIDENCE,*EVIDENCE.parents)),'evidence_exists')
    command,unused=wire(raw);binding=loader('spain')
    require(binding.role=='spain' and binding_hasher(binding)==remote.TARGET,'target_binding')
    args=['C:/Windows/System32/OpenSSH/ssh.exe','-n','-T','-F','none','-o','BatchMode=yes','-o','IdentitiesOnly=yes',
        '-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(binding.known_hosts_path),
        '-o','ConnectTimeout=10','-o','ConnectionAttempts=1','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=6',
        '-i',str(binding.key_path),'-p','22',binding.target_user+'@'+binding.target_host,command]
    require(transport_base.command_units(args)<=30000,'command_length')
    EVIDENCE.parent.mkdir(parents=True,exist_ok=True);transport_base.legacy.claim_directory(EVIDENCE)
    save=transport_base.staged.remote.write_result
    claim=dict(approval=approval,manifest_sha256=approved_manifest_sha,remote_sha256=approved_remote_sha,
        target_binding_sha256=remote.TARGET,attempts=1,claimed_at=datetime.now(timezone.utc).isoformat())
    save(EVIDENCE/'claim.json',claim)
    result=dict(schema='phase16.maintenance-facts-local.v1',status='UNKNOWN_NO_RETRY',claim=claim,transport={},receipt=None)
    try:
        rc,out=transport(args,cwd=EVIDENCE,env=ssh_environment(),timeout=60,cap=65536,input_bytes=b'',diagnostics=result['transport'])
        require(result['transport'].get('stdin_complete') is True and result['transport'].get('output_complete') is True,'transport_incomplete')
        value=parse(out);require(type(rc) is int and rc==(0 if value['status']=='FACTS_COLLECTED_NOT_ADMITTED' else 3),'receipt_exit')
        result['receipt']=value
        if rc==0:result['status']='FACTS_COLLECTED_NOT_ADMITTED'
    except Exception:result['reason']='transport_or_receipt_unverified'
    finally:save(EVIDENCE/'result.json',result)
    return result

def preview(manifest):
    validate_manifest(manifest);raw=script();command,unused=wire(raw)
    return dict(status='OFFLINE_READY_NOT_EXECUTED',approval=remote.APPROVAL,manifest_sha256=sha(encode(manifest)),
        remote_sha256=sha(raw),remote_script_bytes=len(raw),command_units_reserved=transport_base.command_units([command])+2048,
        ssh_attempts=0,remote_seconds=45,transport_seconds=60,live_admission=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true');parser.add_argument('--approve')
    parser.add_argument('--approved-manifest-sha256');parser.add_argument('--approved-remote-sha256');args=parser.parse_args()
    try:
        manifest=json.loads(canonical(MANIFEST));result=preview(manifest)
        if args.execute:
            from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
            result=execute_once(manifest,approval=args.approve,approved_manifest_sha=args.approved_manifest_sha256,
                approved_remote_sha=args.approved_remote_sha256,loader=load_fixed_role_binding)
        print(json.dumps(result,indent=2));return 0 if result['status'] in ('OFFLINE_READY_NOT_EXECUTED','FACTS_COLLECTED_NOT_ADMITTED') else 3
    except Exception:
        print(json.dumps(dict(status='LOCAL_STOP',reason='local_guard_failed')));return 2
if __name__=='__main__':raise SystemExit(main())
