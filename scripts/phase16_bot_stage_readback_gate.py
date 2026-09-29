"""Offline preview by default; one exact-approved readback, no remote writes."""
from __future__ import annotations
import argparse
import ast
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
from scripts.vps import phase16_bot_stage_readback_remote as remote
from scripts import phase16_bot_retained_stage_gate as staged
from scripts.phase16_bot_transport_diagnostics import run_transport
from scripts.phase16_bot_linux_gate import ssh_environment
from scripts.phase16_bot_readback_guard_gate import binding_digest
legacy=remote.legacy
MANIFEST=ROOT/'research/amn2/phase16-bot-stage-readback-manifest-2026-09-29.json'
INVENTORY_PATH=ROOT/'research/amn2/phase16-bot-stage-readback-inventory-2026-09-29.json'
INVENTORY_SHA='647a32f7a538028a8debbe8169ade373ea08b5d1c1b0467a36a9253380852aec'
EVIDENCE_DIRECTORY=Path('C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-stage-readback-20260929/execution-001')
TARGET_BINDING=staged.TARGET_BINDING
MAX_COMMAND_UNITS=30000


def canonical(path):return Path(path).read_bytes().replace(b'\r\n',b'\n')
def sha(data):return hashlib.sha256(data).hexdigest()
def encode(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode('ascii')


def inventory():
    data=canonical(INVENTORY_PATH);legacy.require(sha(data)==INVENTORY_SHA,'inventory_binding')
    value=json.loads(data);files=value['files'];pins=value['pins']
    legacy.require(len(files)==200 and len(pins)==40 and
        sum(n.startswith('source/') for n in files)==159 and sum(n.startswith('payload/') for n in files)==41 and
        sum(v[0] for v in files.values())==29936839,'inventory_binding')
    return value


def definitions(path,names):
    text=canonical(ROOT/path).decode('utf-8');tree=ast.parse(text)
    selected=[node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names]
    legacy.require({n.name for n in selected}==set(names),'remote_render')
    return '\n\n'.join(ast.get_source_segment(text,node) for node in selected)


def remote_script():
    body=canonical(ROOT/'scripts/vps/phase16_bot_stage_readback_remote.py').decode('utf-8')
    core=definitions('scripts/vps/phase16_bot_linux_gate_remote.py',['GateError','require','sha','safe_name'])
    reader=definitions('scripts/vps/phase16_bot_retained_stage_remote.py',['fingerprint','SecureReader'])
    validator=definitions('scripts/phase16_bot_retained_stage_gate.py',['validate_receipt'])
    prefix=('import hashlib,types,math\n'+core+'\n'
        'legacy=types.SimpleNamespace(GateError=GateError,require=require,sha=sha,safe_name=safe_name,MAX_UNPACKED=134217728)\n'+reader)
    contract=staged.remote
    frozen=('staged=types.ModuleType("frozen_receipt_validator")\n'
        'staged.legacy=legacy;staged.math=math;staged.re=re\n'
        'staged.RUNTIME_LOCK_SHA='+repr(staged.RUNTIME_LOCK_SHA)+'\n'
        'staged.remote=types.SimpleNamespace(base_result=lambda:'+repr(contract.base_result())+
        ',SUCCESS='+repr(contract.SUCCESS)+',STEPS='+repr(contract.STEPS)+
        ',REMOTE_SECONDS=300,REASONS=frozenset('+repr(sorted(contract.REASONS))+'))\n'
        'exec(compile('+repr(validator)+',"<frozen-receipt-validator>","exec"),staged.__dict__)')
    replacements={
        'from scripts.vps.phase16_bot_retained_stage_remote import SecureReader, fingerprint, legacy':prefix,
        'from scripts import phase16_bot_retained_stage_gate as staged':frozen,
        'INVENTORY=None  # Rendered from the externally bound local inventory, never from VPS.':'INVENTORY='+repr(inventory())}
    for old,new in replacements.items():
        legacy.require(body.count(old)==1,'remote_render');body=body.replace(old,new)
    result=body.encode('utf-8');legacy.require(0<len(result)<=131072,'remote_size')
    compile(result,'<bound-readback>','exec');return result


def wire_request(script):
    legacy.require(0<len(script)<=131072,'remote_size')
    packed=zlib.compress(script,9);blob=base64.b64encode(packed).decode('ascii')
    bootstrap=('import base64,hashlib,sys,zlib;p=base64.b64decode("'+blob+'",validate=True);'
        'hashlib.sha256(p).hexdigest()=="'+sha(packed)+'" or sys.exit(70);s=zlib.decompress(p);'
        'len(s)=='+str(len(script))+' and hashlib.sha256(s).hexdigest()=="'+sha(script)+'" or sys.exit(70);'
        'exec(compile(s,"<bound-stage-readback>","exec"),{"__name__":"__main__"})')
    command='/usr/bin/python3 -I -S -B -c '+shlex.quote(bootstrap)+' '+remote.APPROVAL
    legacy.require(command_units([command])+2048<=MAX_COMMAND_UNITS,'command_length')
    return command,b''


def command_units(args):return len(subprocess.list2cmdline(list(map(str,args))).encode('utf-16-le'))//2+1


def expected_manifest():
    files=['scripts/phase16_bot_stage_readback_gate.py','scripts/vps/phase16_bot_stage_readback_remote.py',
        'scripts/phase16_bot_retained_stage_gate.py','scripts/vps/phase16_bot_retained_stage_remote.py',
        'scripts/vps/phase16_bot_runtime40_stage_remote.py','scripts/vps/phase16_bot_linux_gate_remote.py',
        'scripts/phase16_bot_linux_gate.py','scripts/phase16_bot_transport_diagnostics.py',
        'scripts/phase16_bot_readback_guard_gate.py','scripts/phase13_bot_web_migration_fresh_inputs.py']
    return dict(schema='phase16.stage-readback-manifest.v1',status='READY_NOT_EXECUTED',approval=remote.APPROVAL,
        base_commit='a4190c26787df604ac686fbe88a36c259b52dcb3',destination=remote.DESTINATION.as_posix(),
        stage_execution_commit='0574462dded68e2430fca93886f20d702765c3d0',
        target_binding_sha256=TARGET_BINDING,inventory_sha256_lf=INVENTORY_SHA,source_files=159,payload_files=41,runtime_pins=40,
        remote_sha256=sha(remote_script()),artifacts_sha256_lf={n:sha(canonical(ROOT/n)) for n in files},
        local_evidence_directory=EVIDENCE_DIRECTORY.as_posix(),
        delivery='COMPRESSED_BOUND_COMMAND_ARGUMENT_STDIN_NULL',
        ssh_options=dict(server_alive_interval=5,server_alive_count_max=6,connect_timeout=10,connection_attempts=1,
            strict_host_key_checking=True,stdin_null=True),
        limits=dict(remote_seconds=45,transport_seconds=60,output_bytes=65536,windows_command_units=MAX_COMMAND_UNITS,attempts=1),
        scope=dict(reads='FIXED_STAGE_DIRECTORY_AND_ANCESTORS_ONLY',remote_writes=0,remote_children=0,install=0,
            app_imports=0,candidate_interpreter_execution=0,database_operations=0,service_actions=0,activation=0),
        limitations=['STATIC_RUNTIME_METADATA_NOT_FULL_INSTALLED_BINARY_INTEGRITY','NOT_ACTIVATION_OR_MAINTENANCE_ACCEPTANCE',
            'ARGV_AND_KEEPALIVE_CHANGE_NOT_A_ROOT_CAUSE_ATTRIBUTION_EXPERIMENT'])


def validate_manifest(value):legacy.require(encode(value)==encode(expected_manifest()),'manifest_binding')


def validate_result(value,phases):
    base=remote.base_result();legacy.require(isinstance(value,dict) and set(value)==set(base),'receipt_fields')
    variable={'status','reason','verified_files','runtime_pins','bootstrap_distributions','saved_receipt_sha256'}
    for k,v in base.items():
        if k not in variable:legacy.require(type(value[k]) is type(v) and value[k]==v,'receipt_binding')
    for name,limit in [('verified_files',200),('runtime_pins',40),('bootstrap_distributions',2)]:
        legacy.require(type(value[name]) is int and 0<=value[name]<=limit,'receipt_count')
    digest=value['saved_receipt_sha256']
    legacy.require(digest is None or isinstance(digest,str) and re.fullmatch('[0-9a-f]{64}',digest),'receipt_binding')
    legacy.require(value['status'] in ('ABSENT','INCOMPLETE','VERIFIED','UNKNOWN'),'receipt_status')
    legacy.require(isinstance(value['reason'],str) and value['reason'] in remote.REASONS|{'directory_absent','receipt_content_metadata_match'},'receipt_reason')
    if not phases:legacy.require(value['verified_files']==value['runtime_pins']==value['bootstrap_distributions']==0 and digest is None,'receipt_count')
    else:legacy.require(digest is not None,'receipt_binding')
    if 'CONTENT' in phases:legacy.require(value['verified_files']==200,'receipt_count')
    if 'METADATA' in phases:legacy.require(value['runtime_pins']==40,'receipt_count')
    else:legacy.require(value['runtime_pins']==value['bootstrap_distributions']==0,'receipt_count')
    if value['status']=='VERIFIED':
        legacy.require(phases==['RECEIPT','CONTENT','METADATA'] and value['reason']=='receipt_content_metadata_match','receipt_success')
    elif value['status']=='ABSENT':legacy.require(not phases and value['reason']=='directory_absent','receipt_absent')
    elif value['status']=='INCOMPLETE':legacy.require(value['reason'] in remote.INCOMPLETE_REASONS,'receipt_reason')
    else:legacy.require(value['reason'] in remote.REASONS-remote.INCOMPLETE_REASONS,'receipt_reason')
    return value


def parse_events(data):
    legacy.require(isinstance(data,bytes) and len(data)<=65536,'receipt_cap')
    lines=data.split(b'\n');tail=lines.pop();legacy.require(len(lines)<=5 and len(tail)<=8192,'receipt_cap')
    events=[];phases=[];result=None
    for seq,line in enumerate(lines):
        legacy.require(len(line)<=8192 and result is None,'receipt_order')
        event=remote.strict_json(line)
        legacy.require(isinstance(event,dict),'receipt_fields');kind=event.get('event')
        fields={'schema','approval','seq','event'}|({'result'} if kind=='RESULT' else set())
        legacy.require(set(event)==fields and event['schema']==remote.SCHEMA and event['approval']==remote.APPROVAL and
            type(event['seq']) is int and event['seq']==seq,'receipt_binding')
        if seq==0:legacy.require(kind=='READY','receipt_order')
        elif kind=='RESULT':result=validate_result(event['result'],phases)
        else:
            legacy.require(len(phases)<3 and kind==['RECEIPT','CONTENT','METADATA'][len(phases)],'receipt_order');phases.append(kind)
        events.append(event)
    legacy.require(result is None or not tail,'receipt_tail')
    return dict(status='COMPLETE' if result is not None else 'PREFIX_ONLY' if events else 'NONE',
                events=events,trailing_fragment=bool(tail),result=result)


def execute_once(manifest,*,approval,approved_remote_sha,approved_manifest_sha,loader,transport=run_transport,binding_hasher=binding_digest):
    validate_manifest(manifest);script=remote_script()
    legacy.require(approval==remote.APPROVAL and approved_remote_sha==sha(script) and approved_manifest_sha==sha(encode(manifest)),'approval_binding')
    evidence=EVIDENCE_DIRECTORY
    legacy.require(not evidence.exists() and all(not p.is_symlink() for p in (evidence,*evidence.parents)),'evidence_directory')
    command,frame=wire_request(script);environment=ssh_environment();binding=loader('spain')
    legacy.require(binding.role=='spain' and binding_hasher(binding)==TARGET_BINDING,'target_binding')
    args=['C:/Windows/System32/OpenSSH/ssh.exe','-n','-T','-F','none','-o','BatchMode=yes','-o','IdentitiesOnly=yes',
        '-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(binding.known_hosts_path),
        '-o','ConnectTimeout=10','-o','ConnectionAttempts=1','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=6',
        '-i',str(binding.key_path),'-p','22',binding.target_user+'@'+binding.target_host,command]
    legacy.require(command_units(args)<=MAX_COMMAND_UNITS,'command_length')
    evidence.parent.mkdir(mode=0o700,parents=True,exist_ok=True);legacy.claim_directory(evidence)
    claim=dict(approval=approval,attempts=1,remote_sha256=approved_remote_sha,manifest_sha256=approved_manifest_sha,
        target_binding_sha256=TARGET_BINDING,destination=remote.DESTINATION.as_posix(),claimed_at=datetime.now(timezone.utc).isoformat())
    staged.remote.write_result(evidence/'claim.json',claim)
    result=dict(schema='phase16.stage-readback-local.v1',claim=claim,status='UNKNOWN_NO_RETRY',ssh_attempts=1,transport={},
                remote_observation=dict(status='NONE',events=[],trailing_fragment=False,result=None))
    def observer(data):
        try:result['remote_observation']=parse_events(data)
        except Exception:result['remote_observation']=dict(status='INVALID',reason='receipt_validation')
    try:
        rc,out=transport(args,cwd=evidence,env=environment,timeout=60,cap=65536,input_bytes=frame,
                         diagnostics=result['transport'],stdout_observer=observer)
        observer(out);observation=result['remote_observation']
        legacy.require(result['transport'].get('stdin_complete') is True and result['transport'].get('output_complete') is True and
                       observation['status']=='COMPLETE','incomplete_transport_or_receipt')
        status=observation['result']['status'];legacy.require(type(rc) is int and rc==(0 if status in ('ABSENT','VERIFIED') else 3),'receipt_exit')
        result['status']={'VERIFIED':'VERIFIED_NOT_ACTIVATED','ABSENT':'ABSENT_NO_INSTALL','INCOMPLETE':'INCOMPLETE_NO_RETRY','UNKNOWN':'UNKNOWN_NO_RETRY'}[status]
    except Exception as error:
        allowed={'transport_start','transport_timeout','transport_output_cap','transport_unclosed_pipe','transport_stdin_write',
            'transport_stdin_close','transport_stdout_read','transport_stderr_read','transport_cleanup_wait',
            'incomplete_transport_or_receipt','receipt_exit'}
        result['reason']=str(error) if isinstance(error,legacy.GateError) and str(error) in allowed else 'local_or_transport_failure'
    finally:staged.remote.write_result(evidence/'result.json',result)
    return result


def preview(manifest):
    validate_manifest(manifest);script=remote_script();command,frame=wire_request(script)
    return dict(status='OFFLINE_READY_NOT_EXECUTED',approval=remote.APPROVAL,remote_sha256=sha(script),
        manifest_sha256=sha(encode(manifest)),inventory_sha256=INVENTORY_SHA,remote_script_bytes=len(script),
        command_units_reserved=command_units([command])+2048,stdin_bytes=len(frame),source_files=159,payload_files=41,runtime_pins=40,
        ssh_attempts=0,stage=0,install=0,activation=0,remote_seconds=45,transport_seconds=60)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true');parser.add_argument('--approve')
    parser.add_argument('--approved-remote-sha256');parser.add_argument('--approved-manifest-sha256');args=parser.parse_args()
    try:
        manifest=remote.strict_json(canonical(MANIFEST));result=preview(manifest)
        if args.execute:
            from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
            result=execute_once(manifest,approval=args.approve,approved_remote_sha=args.approved_remote_sha256,
                approved_manifest_sha=args.approved_manifest_sha256,loader=load_fixed_role_binding)
        print(json.dumps(result,indent=2))
        return 0 if result['status'] in ('OFFLINE_READY_NOT_EXECUTED','VERIFIED_NOT_ACTIVATED','ABSENT_NO_INSTALL') else 3
    except Exception:
        print(json.dumps(dict(status='LOCAL_STOP',reason='local_guard_failed')));return 2


if __name__=='__main__':raise SystemExit(main())
