"""Preview by default. One exact-approved in-memory transfer probe; no stage."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.vps import phase16_bot_transfer_probe_remote as remote
from scripts.phase16_bot_transport_diagnostics import run_transport, gate as transport_gate
from scripts.phase16_bot_linux_gate import ssh_environment
from scripts.phase16_bot_readback_guard_gate import binding_digest

MANIFEST = ROOT/'research/amn2/phase16-bot-transfer-probe-manifest-2026-09-27.json'
EVIDENCE_DIRECTORY = Path('C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-transfer-probe-20260927/execution-001')
TARGET_BINDING = '87b33ab0769b0f98670289e66e230407d82caebc05c6e459baf564564789d0c6'


class GuardError(Exception):
    pass


def require(condition, reason):
    if not condition:
        raise GuardError(reason)


def canonical(path):
    return Path(path).read_bytes().replace(b'\r\n', b'\n')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2)+'\n').encode('ascii')


def remote_script():
    script = canonical(ROOT/'scripts/vps/phase16_bot_transfer_probe_remote.py')
    require(0 < len(script) <= 65536, 'remote_size')
    compile(script, '<bound-transfer-probe>', 'exec')
    return script


def payload():
    data = b'\xa5' * remote.PAYLOAD_BYTES
    require(sha(data) == remote.PAYLOAD_SHA256, 'payload_binding')
    return data


def expected_manifest():
    files = ['scripts/phase16_bot_transfer_probe_gate.py', 'scripts/vps/phase16_bot_transfer_probe_remote.py',
             'scripts/phase16_bot_transport_diagnostics.py', 'scripts/phase16_bot_linux_gate.py',
             'scripts/vps/phase16_bot_linux_gate_remote.py', 'scripts/phase16_bot_readback_guard_gate.py',
             'scripts/phase13_bot_web_migration_fresh_inputs.py']
    return dict(schema='phase16.transfer-probe-manifest.v1', approval=remote.APPROVAL,
        base_commit='9086bc3315adda79d6a7e7d46765c1ca2f6e26fb',
        status='READY_NOT_EXECUTED', remote_sha256=sha(remote_script()),
        artifacts_sha256_lf={name:sha(canonical(ROOT/name)) for name in files},
        payload_bytes=remote.PAYLOAD_BYTES, payload_sha256=remote.PAYLOAD_SHA256,
        payload_kind='SYNTHETIC_A5_IN_MEMORY_NOT_PACKAGE', target_binding_sha256=TARGET_BINDING,
        local_evidence_directory=EVIDENCE_DIRECTORY.as_posix(),
        limits=dict(remote_seconds=90, transport_seconds=110, output_bytes=65536,
                    checkpoint_bytes=1048576, attempts=1),
        scope=dict(remote_file_writes=0, app_file_reads=0, service_actions=0, database_operations=0,
                   stage=0, install=0, activation=0, remote_children=0, remote_outbound_network=0),
        ssh_options=dict(connect_timeout=10, connection_attempts=1, server_alive_interval=5,
                         server_alive_count_max=1, strict_host_key_checking=True),
        limitations=['PROGRESS_OUTPUT_DIFFERS_FROM_STAGE001','NO_INSTALL_OR_RUNTIME_ACCEPTANCE',
                     'NO_OBSERVATION_OF_STAGE001_DIRECTORY','HINTS_DO_NOT_ESTABLISH_ROOT_CAUSE'])


def validate_manifest(value):
    require(encode(value) == encode(expected_manifest()), 'manifest_binding')


def frame_request():
    script = remote_script()
    bootstrap = ('import hashlib,sys;n=int(sys.stdin.buffer.read(8));0<n<=65536 or sys.exit(70);'
                 'b=sys.stdin.buffer.read(n);len(b)==n and hashlib.sha256(b).hexdigest()=="'+sha(script)+'" or sys.exit(70);'
                 'exec(compile(b,"<bound-transfer-probe>","exec"),{"__name__":"__main__"})')
    command = '/usr/bin/python3 -I -S -B -c '+shlex.quote(bootstrap)+' '+remote.APPROVAL
    return command, f'{len(script):08d}'.encode('ascii')+script+payload()


def parse_events(data):
    require(isinstance(data, bytes) and len(data) <= 65536, 'receipt_cap')
    lines = data.split(b'\n')
    tail = lines.pop()
    require(len(tail) <= 4096 and len(lines) <= 32, 'receipt_lines')
    events = []
    confirmed = 0
    terminal = None
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'receipt_duplicate')
            result[key] = value
        return result
    try:
        for seq,line in enumerate(lines):
            require(len(line) <= 4096 and terminal is None, 'receipt_order')
            event = json.loads(line, object_pairs_hook=pairs)
            require(isinstance(event,dict), 'receipt_shape')
            kind = event.get('event')
            fields = {'schema','approval','seq','event','bytes'}
            if kind == 'COMPLETE': fields.add('sha256')
            if kind == 'STOP': fields.add('reason')
            require(set(event)==fields and event['schema']==remote.SCHEMA and
                    event['approval']==remote.APPROVAL and type(event['seq']) is int and
                    event['seq']==seq and type(event['bytes']) is int, 'receipt_binding')
            count = event['bytes']
            require(0 <= count <= remote.PAYLOAD_BYTES, 'receipt_count')
            if seq == 0:
                require(kind=='READY' and count==0, 'receipt_ready')
            elif kind == 'PROGRESS':
                require(count==confirmed+remote.CHECKPOINT, 'receipt_progress')
            elif kind == 'COMPLETE':
                require(count==remote.PAYLOAD_BYTES and confirmed==remote.PAYLOAD_BYTES//remote.CHECKPOINT*remote.CHECKPOINT
                        and event['sha256']==remote.PAYLOAD_SHA256, 'receipt_complete')
                terminal='COMPLETE'
            elif kind == 'STOP':
                require(event['reason'] in remote.REASONS and confirmed <= count < min(confirmed+remote.CHECKPOINT,remote.PAYLOAD_BYTES+1), 'receipt_stop')
                terminal='STOP'
            else:
                raise GuardError('receipt_event')
            confirmed=count
            events.append(event)
        require(not terminal or not tail, 'receipt_terminal_tail')
    except (ValueError, TypeError, UnicodeDecodeError, KeyError):
        raise GuardError('receipt_shape') from None
    return dict(status=terminal or ('PREFIX_ONLY' if events else 'ABSENT'),
                confirmed_bytes=confirmed, events=events, trailing_fragment=bool(tail))


def write_result(path,value):
    import os
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())


def execute_once(manifest, *, approval, approved_remote_sha, approved_manifest_sha,
                 loader, transport=run_transport, binding_hasher=binding_digest):
    validate_manifest(manifest)
    require(approval==remote.APPROVAL and approved_remote_sha==sha(remote_script()) and
            approved_manifest_sha==sha(encode(manifest)), 'approval_binding')
    evidence=EVIDENCE_DIRECTORY
    require(not evidence.exists() and all(not p.is_symlink() for p in (evidence,*evidence.parents)), 'evidence_directory')
    environment=ssh_environment()
    binding=loader('spain')
    require(binding.role=='spain' and binding_hasher(binding)==TARGET_BINDING, 'target_binding')
    command,frame=frame_request()
    evidence.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    evidence.mkdir(mode=0o700)
    claim=dict(approval=approval,manifest_sha256=approved_manifest_sha,remote_sha256=approved_remote_sha,
        target_binding_sha256=TARGET_BINDING,claimed_at=datetime.now(timezone.utc).isoformat(),attempts=1)
    write_result(evidence/'claim.json',claim)
    args=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-F','none','-o','BatchMode=yes','-o','IdentitiesOnly=yes',
        '-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(binding.known_hosts_path),
        '-o','ConnectTimeout=10','-o','ConnectionAttempts=1','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=1',
        '-i',str(binding.key_path),'-p','22',binding.target_user+'@'+binding.target_host,command]
    result=dict(schema='phase16.transfer-probe-local.v1',claim=claim,status='UNKNOWN_NO_RETRY',ssh_attempts=1,
                transport={},remote_observation=dict(status='ABSENT',confirmed_bytes=0,events=[],trailing_fragment=False))
    def observer(data):
        try:result['remote_observation']=parse_events(data)
        except GuardError:result['remote_observation']=dict(status='INVALID',reason='receipt_validation')
    try:
        rc,out=transport(args,cwd=evidence,env=environment,timeout=110,cap=65536,input_bytes=frame,
                         diagnostics=result['transport'],stdout_observer=observer)
        observer(out)
        observation=result['remote_observation']
        if rc==0 and result['transport'].get('stdin_complete') is True and result['transport'].get('output_complete') is True and observation['status']=='COMPLETE':
            result['status']='TRANSFER_OBSERVED_NOT_STAGE_ACCEPTANCE'
        elif rc==3 and observation['status']=='STOP':
            result['status']='REMOTE_STOP_NO_RETRY'
        else:result['reason']='incomplete_transport_or_receipt'
    except Exception as error:
        allowed={'transport_start','transport_timeout','transport_output_cap','transport_unclosed_pipe',
                 'transport_stdin_write','transport_stdin_close','transport_stdout_read','transport_stderr_read','transport_cleanup_wait'}
        result['reason']=str(error) if isinstance(error,transport_gate.GateError) and str(error) in allowed else 'local_or_transport_failure'
    finally:write_result(evidence/'result.json',result)
    return result


def preview(manifest):
    validate_manifest(manifest)
    command,frame=frame_request()
    return dict(status='OFFLINE_READY_NOT_EXECUTED',approval=remote.APPROVAL,
                manifest_sha256=sha(encode(manifest)),remote_sha256=sha(remote_script()),
                payload_bytes=remote.PAYLOAD_BYTES,frame_bytes=len(frame),
                ssh_attempts=0,remote_file_writes=0,stage=0,install=0,activation=0,
                remote_seconds=90,transport_seconds=110)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--approve')
    parser.add_argument('--approved-remote-sha256')
    parser.add_argument('--approved-manifest-sha256')
    args=parser.parse_args()
    try:
        manifest=json.loads(canonical(MANIFEST))
        result=preview(manifest)
        if args.execute:
            from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
            result=execute_once(manifest,approval=args.approve,approved_remote_sha=args.approved_remote_sha256,
                approved_manifest_sha=args.approved_manifest_sha256,loader=load_fixed_role_binding)
        print(json.dumps(result,indent=2))
        return 0 if result['status'] in ('OFFLINE_READY_NOT_EXECUTED','TRANSFER_OBSERVED_NOT_STAGE_ACCEPTANCE') else 3
    except Exception:
        print(json.dumps(dict(status='LOCAL_STOP',reason='local_guard_failed')))
        return 2


if __name__=='__main__':raise SystemExit(main())
