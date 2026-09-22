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
import signal
import subprocess
import threading
import time

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


def run_transport(command, *, cwd, env, timeout, cap=65536, input_bytes=b'', diagnostics):
    """Local child only; bounded raw output stays in memory, receipt is metadata."""
    gate.require(0 < timeout <= 330 and 0 < cap <= 65536 and
                 len(input_bytes) <= gate.MAX_BUNDLE + 65544, 'transport_limits')
    diagnostics.update(schema='phase16.bot-transport.v1', returncode=None,
                       failure_stage=None, stdin_bytes_requested=len(input_bytes),
                       stdin_bytes_accepted=0, stdin_complete=False, output_complete=False)
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}
    observed = {'stdout': 0, 'stderr': 0}
    eof = {name: threading.Event() for name in buffers}
    failures = {name: threading.Event() for name in ('stdin_write', 'stdin_close', 'stdout_read', 'stderr_read')}
    overflow = threading.Event()
    lock = threading.Lock()

    def summarize(stage, rc):
        with lock:
            diagnostics.update(returncode=rc, failure_stage=stage,
                               output_complete=all(event.is_set() for event in eof.values()) and not overflow.is_set())
            for name, data in buffers.items():
                diagnostics[name] = {'bytes_observed': observed[name], 'bytes_retained': len(data),
                                     'prefix_sha256': gate.sha(bytes(data))}
            stderr = bytes(buffers['stderr'])
        diagnostics['pipe_failures'] = [name for name, event in failures.items() if event.is_set()]
        hints = ((b'Permission denied (publickey)', 'SSH_AUTHENTICATION_HINT'),
                 (b'Host key verification failed', 'SSH_HOST_KEY_HINT'),
                 (b'SyntaxError:', 'PYTHON_SYNTAX_HINT'),
                 (b'Connection timed out', 'SSH_TIMEOUT_HINT'),
                 (b'kex_exchange_identification:', 'SSH_KEX_HINT'),
                 (b'banner exchange:', 'SSH_BANNER_HINT'),
                 (b'Connection reset by peer', 'SSH_CONNECTION_RESET_HINT'),
                 (b'Connection closed by remote host', 'SSH_DISCONNECT_HINT'),
                 (b'Broken pipe', 'SSH_BROKEN_PIPE_HINT'))
        diagnostics['stderr_classification'] = next((label for marker, label in hints if marker in stderr),
                                                    'UNCLASSIFIED_STDERR' if stderr else 'NO_STDERR')

    try:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   bufsize=0, shell=False, start_new_session=(os.name == 'posix'))
    except OSError:
        summarize('start', None)
        raise gate.GateError('transport_start') from None

    def read(name):
        try:
            while chunk := getattr(process, name).read(4096):
                with lock:
                    observed[name] += len(chunk)
                    remaining = cap - sum(len(data) for data in buffers.values())
                    buffers[name].extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        overflow.set()
                        return
            eof[name].set()
        except (OSError, ValueError):
            failures[name+'_read'].set()

    def write():
        try:
            data = memoryview(input_bytes)
            accepted = 0
            while accepted < len(data):
                count = process.stdin.write(data[accepted:accepted+32768])
                if not count:
                    raise OSError('zero_write')
                accepted += count
                diagnostics['stdin_bytes_accepted'] = accepted
            diagnostics['stdin_complete'] = True
        except (OSError, ValueError):
            failures['stdin_write'].set()
        finally:
            try:
                process.stdin.close()
            except (OSError, ValueError):
                failures['stdin_close'].set()

    threads = [threading.Thread(target=read, args=(name,), daemon=True) for name in buffers]
    threads.append(threading.Thread(target=write, daemon=True))
    for thread in threads:
        thread.start()
    deadline = time.monotonic() + timeout
    stage = None
    try:
        while process.poll() is None:
            if overflow.is_set():
                stage = 'output_cap'
                break
            if time.monotonic() >= deadline:
                stage = 'timeout'
                break
            time.sleep(.01)
    finally:
        if process.poll() is None:
            if os.name == 'posix':
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                process.kill()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                stage = 'cleanup_wait'
        for thread in threads:
            thread.join(timeout=1)
        if stage is None:
            stage = ('output_cap' if overflow.is_set() else
                     'unclosed_pipe' if any(t.is_alive() for t in threads) else
                     next((name for name, event in failures.items() if event.is_set()), None))
        # Do not block closing a pipe still owned by a live reader thread.
        for name, thread in zip(buffers, threads):
            if not thread.is_alive():
                getattr(process, name).close()
        summarize(stage, process.returncode)
    if stage is not None:
        raise gate.GateError('transport_'+stage)
    return process.returncode, bytes(buffers['stdout'])


def ssh_environment():
    # Windows OpenSSH exits 255 even for -V when PROGRAMDATA is absent.
    allowed = {'PATH','SYSTEMROOT','WINDIR','TEMP','TMP','COMSPEC','SYSTEMDRIVE','PATHEXT','PROGRAMDATA'}
    environment = {k.upper():v for k,v in os.environ.items() if k.upper() in allowed}
    gate.require(bool(environment.get('PROGRAMDATA')), 'ssh_environment_programdata')
    return environment


def execute_once(bundle, script, evidence_dir, *, approval, approved_sha, loader, transport):
    gate.require(approval == gate.APPROVAL and approved_sha == gate.sha(script), 'approval_binding')
    gate.validate_bundle(bundle)
    command, frame = frame_request(script,bundle)
    environment = ssh_environment()
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
    result = {'schema':'phase16.bot-linux-local.v1','claim':claim,'status':'UNKNOWN_NO_RETRY','ssh_attempts':1}
    result['transport'] = {}
    try:
        rc, output = transport(args,cwd=evidence_dir,env=environment,timeout=330,cap=65536,input_bytes=frame,
                               diagnostics=result['transport'])
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
                              transport=run_transport)
        print(json.dumps(result,indent=2))
        return 0 if result['status']=='ISOLATED_LINUX_SIGNALS_PASS_NOT_DEPLOYED' else 3
    except Exception as exc:
        print(json.dumps({'status':'LOCAL_STOP_NO_REMOTE_RETRY','reason':str(exc) if isinstance(exc,gate.GateError) else type(exc).__name__}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
