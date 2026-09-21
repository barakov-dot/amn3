"""Offline preview by default; explicit, hash-bound single Spain test attempt."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shlex
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.vps import phase16_bot_linux_gate_remote as gate


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument('--bundle', type=Path, required=True)
    result.add_argument('--execute', action='store_true')
    result.add_argument('--approve')
    result.add_argument('--approved-remote-sha256')
    result.add_argument('--evidence-dir', type=Path)
    return result


def frame_request(script, bundle):
    gate.require(0 < len(script) <= 65536 and len(bundle) <= gate.MAX_BUNDLE, 'frame_size')
    digest = gate.sha(script)
    bootstrap = (
        'import hashlib,sys;'
        'n=int(sys.stdin.buffer.read(8));'
        '0<n<=65536 or sys.exit(70);'
        'b=sys.stdin.buffer.read(n);'
        f'len(b)==n and hashlib.sha256(b).hexdigest()=="{digest}" or sys.exit(70);'
        'exec(compile(b,"<bound-phase16-linux-gate>","exec"),{"__name__":"__main__"})'
    )
    command = '/usr/bin/python3 -I -B -c ' + shlex.quote(bootstrap) + ' ' + gate.APPROVAL
    return command, f'{len(script):08d}'.encode('ascii') + script + bundle


def validate_receipt(result, returncode):
    gate.require(isinstance(result,dict) and result.get('schema') == 'phase16.bot-linux-gate.v1', 'receipt_binding')
    status = result.get('status')
    if status == 'ISOLATED_LINUX_SIGNALS_PASS_NOT_DEPLOYED':
        gate.require(returncode == 0 and result.get('artifact_id') == gate.ARTIFACT_ID and
                     result.get('bundle_sha256') == gate.BUNDLE_SHA and result.get('source_commit') == gate.SOURCE_SHA,
                     'receipt_binding')
        gate.require(type(result.get('service_actions')) is int and result['service_actions'] == 0 and
                     all(result.get(key) is False for key in ('live_database_opened','telegram_polling','runtime_activation')),
                     'receipt_binding')
        gate.require(result.get('negative') == {'passed':0,'expected_failure':True} and
                     result.get('green') == {'passed':6,'expected_failure':False}, 'receipt_binding')
        gate.require([s.get('step') for s in result.get('steps',[])] ==
                     ['venv','offline_install','pip_check','metadata','negative','green'], 'receipt_binding')
    else:
        gate.require(status in ('STOP_RETAINED_NO_RETRY','STOP_BEFORE_GATE_OR_UNKNOWN') and returncode == 3,
                     'receipt_binding')
        gate.require(isinstance(result.get('reason'),str) and re.fullmatch(r'[A-Za-z0-9_]{1,80}',result['reason']),
                     'receipt_binding')
    return result


def execute_once(bundle, script, evidence_dir, *, approval, approved_sha, loader, transport):
    gate.require(approval == gate.APPROVAL and approved_sha == gate.sha(script), 'approval_binding')
    gate.validate_bundle(bundle)
    command, frame = frame_request(script,bundle)
    binding = loader('spain')
    gate.require(binding.role == 'spain', 'target_role')
    gate.claim_directory(evidence_dir)
    claim = {'scope':gate.APPROVAL,'attempts':1,'remote_sha256':gate.sha(script),'bundle_sha256':gate.BUNDLE_SHA,
             'destination':gate.DESTINATION.as_posix(),'claimed_at':datetime.now(timezone.utc).isoformat()}
    with (evidence_dir/'claim.json').open('x',encoding='utf-8') as stream:
        json.dump(claim,stream,indent=2)
    args = ['C:/Windows/System32/OpenSSH/ssh.exe','-T','-F','none','-o','BatchMode=yes',
            '-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(binding.known_hosts_path),
            '-o','ConnectTimeout=10','-o','ConnectionAttempts=1','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=1',
            '-i',str(binding.key_path),'-p','22',binding.target_user+'@'+binding.target_host,command]
    environment = {k:v for k,v in os.environ.items() if k.upper() in
                   {'PATH','SYSTEMROOT','WINDIR','TEMP','TMP','COMSPEC','SYSTEMDRIVE','PATHEXT'}}
    result = {'schema':'phase16.bot-linux-local.v1','claim':claim,'status':'UNKNOWN_NO_RETRY','ssh_attempts':1}
    try:
        rc, output = transport(args,cwd=evidence_dir,env=environment,timeout=330,cap=65536,input_bytes=frame)
        remote = validate_receipt(json.loads(output),rc)
        result['remote'] = remote
        result['status'] = remote['status']
    except Exception as exc:
        result['reason'] = str(exc) if isinstance(exc,gate.GateError) else type(exc).__name__
    finally:
        with (evidence_dir/'result.json').open('x',encoding='utf-8') as stream:
            json.dump(result,stream,indent=2)
    return result


def main():
    args = parser().parse_args()
    try:
        gate.require(args.bundle.is_file() and not args.bundle.is_symlink() and args.bundle.stat().st_size == gate.BUNDLE_SIZE,
                     'bundle_binding')
        bundle = args.bundle.read_bytes()
        _, _, manifest = gate.validate_bundle(bundle)
        # Canonical LF payload is stable across Windows Git autocrlf checkouts.
        script = (ROOT/'scripts/vps/phase16_bot_linux_gate_remote.py').read_bytes().replace(b'\r\n',b'\n')
        compile(script,'<bound-phase16-linux-gate>','exec')
        preview = {'status':'OFFLINE_READY_NOT_EXECUTED','bundle_sha256':gate.BUNDLE_SHA,
                   'remote_sha256':gate.sha(script),'source_commit':gate.SOURCE_SHA,'destination':gate.DESTINATION.as_posix(),
                   'bundle_bytes':len(bundle),'runtime_wheels':40,'test_only_wheels':8,'remote_seconds':300,
                   'transport_seconds':330,'network':'offline wheels; children in new unshare --net namespace',
                   'ssh_attempts':0,'requires_approval':gate.APPROVAL}
        if not args.execute:
            print(json.dumps(preview,indent=2)); return 0
        gate.require(args.evidence_dir is not None and args.evidence_dir.parent.is_dir(), 'evidence_directory')
        gate.require(args.approve == gate.APPROVAL and args.approved_remote_sha256 == gate.sha(script), 'approval_binding')
        from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
        result = execute_once(bundle,script,args.evidence_dir,approval=args.approve,
                              approved_sha=args.approved_remote_sha256,loader=load_fixed_role_binding,
                              transport=gate.run_process)
        print(json.dumps(result,indent=2))
        return 0 if result['status']=='ISOLATED_LINUX_SIGNALS_PASS_NOT_DEPLOYED' else 3
    except Exception as exc:
        print(json.dumps({'status':'LOCAL_STOP_NO_REMOTE_RETRY','reason':str(exc) if isinstance(exc,gate.GateError) else type(exc).__name__}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
