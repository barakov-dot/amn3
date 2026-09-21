import hashlib
import json
import sys
from types import SimpleNamespace

import pytest

from scripts import phase16_bot_linux_gate as local
from scripts.vps import phase16_bot_linux_gate_remote as gate


def child(tmp_path, code, *, data=b'', cap=65536, timeout=5):
    diagnostics = {}
    try:
        rc, output = local.run_transport([sys.executable, '-I', '-B', '-c', code],
            cwd=tmp_path, env=None, timeout=timeout, cap=cap, input_bytes=data,
            diagnostics=diagnostics)
    except gate.GateError as exc:
        return str(exc), None, diagnostics
    return rc, output, diagnostics


def test_early_exit_retains_exit_pipe_stage_and_only_redacted_metadata(tmp_path):
    reason, output, d = child(tmp_path,
        'import sys; sys.stderr.buffer.write(b"Permission denied (publickey). PRIVATE_MARKER"); sys.exit(17)',
        data=b'x' * 1048576)
    assert reason == 'transport_stdin_write' and output is None
    assert d['returncode'] == 17 and d['failure_stage'] == 'stdin_write'
    assert d['stderr']['bytes_observed'] == 45
    assert d['stderr']['prefix_sha256'] == hashlib.sha256(b'Permission denied (publickey). PRIVATE_MARKER').hexdigest()
    assert d['stderr_classification'] == 'SSH_AUTHENTICATION_HINT'
    assert not d['stdin_complete'] and d['stdin_bytes_accepted'] < 1048576
    assert 'PRIVATE_MARKER' not in json.dumps(d)


def test_stdout_json_is_separate_from_stderr_and_input_delivered(tmp_path):
    rc, output, d = child(tmp_path,
        'import sys; data=sys.stdin.buffer.read(); sys.stderr.write("PRIVATE_MARKER"); print(len(data))', data=b'abc')
    assert rc == 0 and output.strip() == b'3'
    assert d['stdin_complete'] and d['stdin_bytes_accepted'] == 3
    assert d['failure_stage'] is None and d['stderr']['bytes_observed'] == 14
    assert d['stderr_classification'] == 'UNCLASSIFIED_STDERR'
    assert 'PRIVATE_MARKER' not in json.dumps(d)


def test_timeout_has_bounded_redacted_diagnostics(tmp_path):
    reason, _, d = child(tmp_path, 'import time; time.sleep(10)', timeout=.15)
    assert reason == 'transport_timeout' and d['failure_stage'] == 'timeout'
    assert d['returncode'] is not None


def test_combined_output_cap_includes_stderr(tmp_path):
    reason, _, d = child(tmp_path,
        'import sys; sys.stdout.buffer.write(b"x"*60); sys.stdout.flush(); sys.stderr.buffer.write(b"y"*60)', cap=100)
    assert reason == 'transport_output_cap' and d['failure_stage'] == 'output_cap'
    assert sum(d[k]['bytes_retained'] for k in ('stdout', 'stderr')) <= 100
    assert d['output_complete'] is False


def test_start_error_excludes_command_and_exception_paths(tmp_path):
    d = {}
    with pytest.raises(gate.GateError, match='transport_start'):
        local.run_transport([str(tmp_path/'SECRET_EXECUTABLE_NOT_FOUND')], cwd=tmp_path,
            env=None, timeout=5, diagnostics=d)
    assert d['failure_stage'] == 'start' and d['returncode'] is None
    assert 'SECRET_EXECUTABLE' not in json.dumps(d)


@pytest.mark.parametrize('message,category', [
    ('SyntaxError: PRIVATE_MARKER', 'PYTHON_SYNTAX_HINT'),
    ('Host key verification failed. PRIVATE_MARKER', 'SSH_HOST_KEY_HINT'),
    ('Connection timed out PRIVATE_MARKER', 'SSH_TIMEOUT_HINT'),
])
def test_stderr_classification_does_not_copy_sensitive_text(tmp_path, message, category):
    rc, _, d = child(tmp_path, 'import sys; sys.stderr.write('+repr(message)+'); sys.exit(255)')
    assert rc == 255 and d['stderr_classification'] == category
    assert 'PRIVATE_MARKER' not in json.dumps(d)


@pytest.mark.parametrize('code', [
    'import sys; sys.exit(17)',
    'import sys; sys.stdin.buffer.read(); print("PRIVATE_INVALID_JSON")',
])
def test_execute_once_saves_diagnostics_on_failure_without_retry(tmp_path, monkeypatch, code):
    monkeypatch.setattr(gate, 'validate_bundle', lambda data: ({}, {}, {}))
    binding = SimpleNamespace(role='spain', target_user='synthetic', target_host='example.invalid',
                              known_hosts_path=tmp_path/'hosts', key_path=tmp_path/'key')
    calls = []
    def transport(args, **kwargs):
        calls.append(1)
        return local.run_transport([sys.executable, '-I', '-B', '-c', code], **kwargs)
    script = b'pass'
    kw = dict(approval=gate.APPROVAL, approved_sha=gate.sha(script), loader=lambda role: binding,
              transport=transport)
    result = local.execute_once(b'x'*1048576, script, tmp_path/'attempt', **kw)
    saved = json.loads((tmp_path/'attempt/result.json').read_text())
    assert saved == result and saved['status'] == 'UNKNOWN_NO_RETRY'
    assert saved['transport']['returncode'] in (0, 17)
    assert 'PRIVATE_INVALID_JSON' not in json.dumps(saved)
    with pytest.raises(gate.GateError, match='destination_exists'):
        local.execute_once(b'x'*1048576, script, tmp_path/'attempt', **kw)
    assert calls == [1]


def test_valid_remote_stop_receipt_survives_stderr_and_chunked_input(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, 'validate_bundle', lambda data: ({}, {}, {}))
    binding = SimpleNamespace(role='spain', target_user='synthetic', target_host='example.invalid',
                              known_hosts_path=tmp_path/'hosts', key_path=tmp_path/'key')
    receipt = {'schema':'phase16.bot-linux-gate.v1', 'status':'STOP_BEFORE_GATE_OR_UNKNOWN',
               'reason':'venv_unavailable'}
    def transport(args, **kwargs):
        code = ('import sys; sys.stdin.buffer.read(); sys.stderr.write("PRIVATE_MARKER"); '
                'sys.stdout.write('+repr(json.dumps(receipt))+'); sys.exit(3)')
        return local.run_transport([sys.executable, '-I', '-B', '-c', code], **kwargs)
    script = b'pass'
    result = local.execute_once(b'x'*65537, script, tmp_path/'attempt', approval=gate.APPROVAL,
        approved_sha=gate.sha(script), loader=lambda role:binding, transport=transport)
    assert result['status'] == 'STOP_BEFORE_GATE_OR_UNKNOWN' and result['remote'] == receipt
    assert result['transport']['stdin_bytes_accepted'] == 65549
    assert result['transport']['stdin_complete'] and result['transport']['returncode'] == 3
    assert 'PRIVATE_MARKER' not in json.dumps(result)


def test_ssh_environment_keeps_windows_programdata_but_drops_app_secrets(monkeypatch):
    monkeypatch.setenv('PROGRAMDATA', 'C:/synthetic-program-data')
    monkeypatch.setenv('BOT_TOKEN', 'PRIVATE_MARKER')
    monkeypatch.setenv('DATABASE_PATH', 'PRIVATE_MARKER')
    monkeypatch.setenv('PYTHONPATH', 'PRIVATE_MARKER')
    env = local.ssh_environment()
    assert env['PROGRAMDATA'] == 'C:/synthetic-program-data'
    assert not {'BOT_TOKEN', 'DATABASE_PATH', 'PYTHONPATH'} & env.keys()


def test_missing_programdata_stops_before_trust_claim_and_transport(tmp_path, monkeypatch):
    monkeypatch.delenv('PROGRAMDATA', raising=False)
    monkeypatch.setattr(gate, 'validate_bundle', lambda data: ({}, {}, {}))
    calls = []
    with pytest.raises(gate.GateError, match='ssh_environment_programdata'):
        local.execute_once(b'zip', b'pass', tmp_path/'attempt', approval=gate.APPROVAL,
            approved_sha=gate.sha(b'pass'), loader=lambda role:calls.append('trust'),
            transport=lambda *a, **k:calls.append('transport'))
    assert calls == [] and not (tmp_path/'attempt').exists()
