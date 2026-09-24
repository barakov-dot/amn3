"""Offline preview by default. One new exact-approved runtime40 stage, no activation."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shlex
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts.vps import phase16_bot_runtime40_stage_remote as remote
from scripts.phase16_bot_linux_gate import run_transport,ssh_environment
from scripts.phase16_bot_readback_guard_gate import binding_digest

legacy=remote.legacy
MANIFEST=ROOT/'research/amn2/phase16-bot-runtime40-stage-manifest-2026-09-24.json'
EVIDENCE_DIRECTORY=Path('C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-runtime40-stage-20260924/execution-001')
TARGET_BINDING='87b33ab0769b0f98670289e66e230407d82caebc05c6e459baf564564789d0c6'
RUNTIME_LOCK_SHA='a381be185b19777b9198526e11df8dcfa0afaf7f15acccd829809e698d679fab'


def canonical(path):return Path(path).read_bytes().replace(b'\r\n',b'\n')
def sha(data):return hashlib.sha256(data).hexdigest()
def encode(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode('ascii')


def remote_script():
    helper=canonical(ROOT/'scripts/vps/phase16_bot_linux_gate_remote.py')
    body=canonical(ROOT/'scripts/vps/phase16_bot_runtime40_stage_remote.py').decode('utf-8')
    anchor='from scripts.vps import phase16_bot_linux_gate_remote as legacy'
    legacy.require(body.count(anchor)==1,'remote_render')
    replacement=('import types\nlegacy=types.ModuleType("phase16_frozen_stage_primitives")\n'
                 'exec(compile('+repr(helper)+',"<frozen-phase16-primitives>","exec"),legacy.__dict__)')
    result=body.replace(anchor,replacement).encode('utf-8')
    compile(result,'<phase16-runtime40-stage>','exec')
    legacy.require(0<len(result)<=65536,'frame_size')
    return result


def expected_manifest():
    files=['scripts/phase16_bot_runtime40_stage_gate.py','scripts/vps/phase16_bot_runtime40_stage_remote.py',
           'scripts/phase16_bot_linux_gate.py','scripts/vps/phase16_bot_linux_gate_remote.py',
           'scripts/phase16_bot_readback_guard_gate.py','scripts/phase13_bot_web_migration_fresh_inputs.py']
    return dict(schema='phase16.bot-runtime40-stage-manifest.v1',status='STAGE_READY_NOT_EXECUTED',
        amn3_base='b28749a7159e3ace59e0085aae5813fad0528fe0',approval=remote.APPROVAL,
        source_commit=legacy.SOURCE_SHA,bundle_sha256=legacy.BUNDLE_SHA,bundle_bytes=legacy.BUNDLE_SIZE,
        bundle_manifest_sha256=legacy.MANIFEST_SHA,runtime_lock_sha256=RUNTIME_LOCK_SHA,runtime_pins=40,
        destination=remote.DESTINATION.as_posix(),local_evidence_directory=EVIDENCE_DIRECTORY.as_posix(),
        target_binding_sha256=TARGET_BINDING,remote_rendered_sha256=sha(remote_script()),
        artifacts_sha256_lf={name:sha(canonical(ROOT/name)) for name in files},
        limits=dict(remote_seconds=300,work_seconds=280,transport_seconds=330,child_output_bytes=262144,
                    transport_output_bytes=65536,minimum_free_bytes=536870912,attempts=1),
        scope=dict(writes='NEW_STAGE_DIRECTORY_ONLY',children_network='UNSHARE_NET_OFFLINE',
                   service_actions=0,live_database_opened=False,telegram_polling=False,
                   runtime_activation=False,old_runtime_modified=False),
        proposed_binding=dict(source=(remote.DESTINATION/'source').as_posix(),
                              interpreter=(remote.DESTINATION/'runtime-venv/bin/python').as_posix(),
                              shared_database='/var/lib/amn2-spain/amn2.sqlite3',
                              old_source='/opt/amn2-spain/runtime/source/app',
                              old_dependencies='/opt/amn2-spain/runtime/site-packages',
                              bot_unit='amn2-spain-bot.service',web_unit='amn2-spain-web.service'),
        maintenance=dict(status='BLOCKED_UNKNOWN_PREREQUISITES',writer_inventory='UNKNOWN',
                         effective_flags='UNKNOWN',service_user_group='UNKNOWN',drain_evidence='UNKNOWN',
                         startup_budget='UNKNOWN',pending_operations='UNKNOWN',
                         target_data_rehearsal='NOT_AUTHORIZED',service_activation='NOT_AUTHORIZED'))


def validate_manifest(value):
    legacy.require(value==expected_manifest(),'manifest_binding')
    return value


def frame_request(script,bundle):
    legacy.require(0<len(script)<=65536 and len(bundle)<=legacy.MAX_BUNDLE,'frame_size')
    bootstrap=('import hashlib,sys;n=int(sys.stdin.buffer.read(8));0<n<=65536 or sys.exit(70);'
               'b=sys.stdin.buffer.read(n);len(b)==n and hashlib.sha256(b).hexdigest()=="'+sha(script)+'" or sys.exit(70);'
               'exec(compile(b,"<bound-phase16-runtime40-stage>","exec"),{"__name__":"__main__"})')
    command='/usr/bin/python3 -I -S -B -c '+shlex.quote(bootstrap)+' '+remote.APPROVAL
    return command,f'{len(script):08d}'.encode('ascii')+script+bundle


def validate_receipt(value,rc):
    base=remote.base_result()
    legacy.require(isinstance(value,dict),'receipt_binding')
    extras={'reason','seconds','runtime_pins','bootstrap_distributions','candidate_import_origins',
            'pth_count','app_python_files','runtime_lock_sha256'}
    legacy.require(set(value)<=set(base)|extras and set(base)<=set(value),'receipt_fields')
    for name,expected in base.items():
        if name in ('status','steps'):continue
        legacy.require(type(value.get(name)) is type(expected) and value[name]==expected,'receipt_binding')
    steps=value['steps']
    legacy.require(isinstance(steps,list) and len(steps)<=len(remote.STEPS),'receipt_steps')
    for index,step in enumerate(steps):
        legacy.require(isinstance(step,dict) and step.get('step')==remote.STEPS[index] and
                       type(step.get('returncode')) is int,'receipt_steps')
        fields={'step','returncode'}
        if step['step'] not in ('network_namespace','source_readback'):
            fields|={'output_bytes','output_sha256'}
            legacy.require(type(step.get('output_bytes')) is int and 0<=step['output_bytes']<=262144 and
                           isinstance(step.get('output_sha256'),str) and re.fullmatch('[0-9a-f]{64}',step['output_sha256']),'receipt_steps')
        legacy.require(set(step)==fields,'receipt_steps')
    if 'seconds' in value:
        legacy.require(type(value['seconds']) in (int,float) and math.isfinite(value['seconds']) and
                       0<=value['seconds']<=remote.REMOTE_SECONDS+5,'receipt_time')
    if value['status']==remote.SUCCESS:
        legacy.require(rc==0 and len(steps)==len(remote.STEPS) and
                       all(s['returncode']==0 for s in steps) and 'reason' not in value and 'seconds' in value,'receipt_success')
        for key,expected in dict(runtime_pins=40,app_python_files=126,pth_count=0,
                                 candidate_import_origins='MATCH_NO_APPLICATION_IMPORT',runtime_lock_sha256=RUNTIME_LOCK_SHA).items():
            legacy.require(type(value.get(key)) is type(expected) and value[key]==expected,'receipt_success')
        legacy.require(type(value.get('bootstrap_distributions')) is int and
                       0<=value['bootstrap_distributions']<=2,'receipt_success')
    else:
        legacy.require(rc==3 and value['status'] in ('STOP_RETAINED_NO_RETRY','STOP_BEFORE_STAGE_OR_UNKNOWN') and
                       value.get('reason') in remote.REASONS,'receipt_stop')
    return value


def local_reason(error):
    allowed={'manifest_binding','bundle_binding','remote_render','frame_size','approval_binding',
             'evidence_directory','target_binding','remote_binding','receipt_binding','receipt_fields',
             'receipt_steps','receipt_time','receipt_success','receipt_stop','ssh_environment_programdata',
             'transport_start','transport_timeout','transport_output_cap','transport_unclosed_pipe',
             'transport_stdin_write','transport_stdin_close','transport_stdout_read','transport_stderr_read',
             'transport_cleanup_wait'}
    if isinstance(error,legacy.GateError) and str(error) in allowed:return str(error)
    if isinstance(error,json.JSONDecodeError):return 'transport_json'
    return 'local_or_transport_failure'


def safe_evidence(path):
    legacy.require(Path(path)==EVIDENCE_DIRECTORY and not path.exists(),'evidence_directory')
    for parent in (path,*path.parents):legacy.require(not parent.is_symlink(),'evidence_directory')


def execute_once(bundle,script,manifest,evidence,*,approval,approved_remote_sha,approved_manifest_sha,
                 loader,transport,binding_hasher=binding_digest):
    legacy.require(approval==remote.APPROVAL and approved_remote_sha==sha(script) and
                   approved_manifest_sha==sha(encode(manifest)),'approval_binding')
    validate_manifest(manifest)
    legacy.require(script==remote_script(),'remote_binding')
    legacy.validate_bundle(bundle)
    safe_evidence(evidence)
    environment=ssh_environment()
    binding=loader('spain')
    legacy.require(binding.role=='spain' and binding_hasher(binding)==TARGET_BINDING,'target_binding')
    command,frame=frame_request(script,bundle)
    evidence.parent.mkdir(mode=0o700,exist_ok=True)
    legacy.claim_directory(evidence)
    claim=dict(approval=approval,attempts=1,remote_sha256=sha(script),manifest_sha256=sha(encode(manifest)),
               bundle_sha256=legacy.BUNDLE_SHA,target_binding_sha256=TARGET_BINDING,
               destination=remote.DESTINATION.as_posix(),claimed_at=datetime.now(timezone.utc).isoformat())
    remote.write_result(evidence/'claim.json',claim)
    args=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-F','none','-o','BatchMode=yes','-o','IdentitiesOnly=yes',
          '-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(binding.known_hosts_path),
          '-o','ConnectTimeout=10','-o','ConnectionAttempts=1','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=1',
          '-i',str(binding.key_path),'-p','22',binding.target_user+'@'+binding.target_host,command]
    result=dict(schema='phase16.bot-runtime40-stage-local.v1',claim=claim,status='UNKNOWN_NO_RETRY',ssh_attempts=1,transport={})
    try:
        rc,output=transport(args,cwd=evidence,env=environment,timeout=330,cap=65536,input_bytes=frame,
                            diagnostics=result['transport'])
        result['remote']=validate_receipt(json.loads(output),rc);result['status']=result['remote']['status']
    except Exception as error:
        result['reason']=local_reason(error)
    finally:remote.write_result(evidence/'result.json',result)
    return result


def preview(bundle,manifest):
    validate_manifest(manifest);legacy.validate_bundle(bundle)
    return dict(status='OFFLINE_READY_NOT_EXECUTED',approval=remote.APPROVAL,
                remote_sha256=sha(remote_script()),manifest_sha256=sha(encode(manifest)),
                bundle_sha256=legacy.BUNDLE_SHA,destination=remote.DESTINATION.as_posix(),
                runtime_pins=40,remote_seconds=300,transport_seconds=330,ssh_attempts=0,
                service_actions=0,live_database_opened=False,maintenance='BLOCKED_UNKNOWN_PREREQUISITES')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--approve')
    parser.add_argument('--approved-remote-sha256')
    parser.add_argument('--approved-manifest-sha256')
    args=parser.parse_args()
    try:
        legacy.require(args.bundle.is_file() and not args.bundle.is_symlink() and
                       args.bundle.stat().st_size==legacy.BUNDLE_SIZE,'bundle_binding')
        bundle=args.bundle.read_bytes();manifest=json.loads(canonical(MANIFEST))
        result=preview(bundle,manifest)
        if args.execute:
            from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
            result=execute_once(bundle,remote_script(),manifest,EVIDENCE_DIRECTORY,approval=args.approve,
                                approved_remote_sha=args.approved_remote_sha256,approved_manifest_sha=args.approved_manifest_sha256,
                                loader=load_fixed_role_binding,transport=run_transport)
        print(json.dumps(result,indent=2))
        return 0 if result['status'] in ('OFFLINE_READY_NOT_EXECUTED',remote.SUCCESS) else 3
    except Exception as error:
        print(json.dumps({'status':'LOCAL_STOP_NO_REMOTE_RETRY','reason':local_reason(error)}))
        return 2


if __name__=='__main__':raise SystemExit(main())
