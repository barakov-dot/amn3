import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import zipfile

import pytest

from scripts.vps import phase16_bot_linux_gate_remote as gate


def zip_bytes(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        for name, value in entries:
            archive.writestr(name, value)
    return buffer.getvalue()


def test_bundle_bad_hash_rejected_before_filesystem_write(tmp_path):
    with pytest.raises(gate.GateError, match='bundle_binding'):
        gate.validate_bundle(b'invalid')
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize('name', ['../escape', '/absolute', 'C:/escape', 'a\\b', 'a/../b', './a', 'a//b'])
def test_archive_member_path_rejected(name):
    with pytest.raises(gate.GateError, match='archive_path'):
        gate.safe_name(name)


def test_safe_member_path():
    assert gate.safe_name('wheelhouse/runtime/one.whl') == 'wheelhouse/runtime/one.whl'


def test_zip_duplicate_rejected():
    with pytest.warns(UserWarning):
        data = zip_bytes([('same', b'a'), ('same', b'b')])
    with pytest.raises(gate.GateError, match='archive_duplicate'):
        gate.zip_inventory(data)


def test_zip_symlink_rejected():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        member = zipfile.ZipInfo('link')
        member.create_system = 3
        member.external_attr = 0o120777 << 16
        archive.writestr(member, 'outside')
    with pytest.raises(gate.GateError, match='archive_type'):
        gate.zip_inventory(buffer.getvalue())


def test_zip_total_size_rejected():
    with pytest.raises(gate.GateError, match='archive_size'):
        gate.zip_inventory(zip_bytes([('a', b'a'*12)]), maximum=10)


def test_tar_symlink_rejected_before_extraction():
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w') as archive:
        member = tarfile.TarInfo('link'); member.type = tarfile.SYMTYPE; member.linkname = '/outside'
        archive.addfile(member)
    with pytest.raises(gate.GateError, match='archive_type'):
        gate.tar_inventory(buffer.getvalue())


def test_claim_exclusive_retains_existing_files(tmp_path):
    root = tmp_path/'claim'
    gate.claim_directory(root)
    marker = root/'retained'; marker.write_text('keep')
    with pytest.raises(gate.GateError, match='destination_exists'):
        gate.claim_directory(root)
    assert marker.read_text() == 'keep'


def test_clean_environment_drops_secrets(monkeypatch, tmp_path):
    monkeypatch.setenv('BOT_TOKEN', 'not-a-real-token')
    monkeypatch.setenv('PYTHONPATH', 'untrusted')
    monkeypatch.setenv('DATABASE_PATH', '/live/database')
    env = gate.clean_environment(tmp_path)
    assert not {'BOT_TOKEN', 'PYTHONPATH', 'DATABASE_PATH'} & env.keys()
    assert env['VPS_APPLY_ENABLED'] == env['AWG3_BOOTSTRAP_ENABLED'] == 'false'
    assert env['PIP_CONFIG_FILE'] == '/dev/null'


def test_negative_control_changes_only_synthetic_helper():
    original = '    class Controller(StopController):\n        def request_stop(self):\n            pass\n'
    changed = gate.negative_helper(original)
    assert 'self._pending = False' in changed
    assert 'super().attach(loop)' in changed
    assert 'def request_stop(self):' in changed
    with pytest.raises(gate.GateError, match='negative_anchor'):
        gate.negative_helper('different helper')


def xml_report(tmp_path, *, count=6, failures=0, skipped=0, errors=0, message=''):
    path = tmp_path/'report.xml'
    cases=''.join('<testcase name="case'+str(i)+'">'+
                  ('<failure message="'+message+'">'+message+'</failure>' if i < failures else
                   '<skipped />' if i < failures+skipped else
                   '<error />' if i < failures+skipped+errors else '')+'</testcase>' for i in range(count))
    path.write_text(f'<testsuites><testsuite tests="{count}" failures="{failures}" errors="{errors}" skipped="{skipped}">{cases}</testsuite></testsuites>')
    return path


def test_junit_accepts_six_green(tmp_path):
    assert gate.check_junit(xml_report(tmp_path), negative=False)['passed'] == 6


@pytest.mark.parametrize('counts', [dict(count=5),dict(skipped=1),dict(errors=1),dict(failures=1)])
def test_junit_rejects_missing_skipped_failed_cases(tmp_path, counts):
    with pytest.raises(gate.GateError, match='junit_counts'):
        gate.check_junit(xml_report(tmp_path, **counts), negative=False)


def test_negative_requires_specific_trace_failure(tmp_path):
    path = xml_report(tmp_path, count=1, failures=1, message='Invalid synthetic trace order')
    assert gate.check_junit(path, negative=True)['expected_failure'] is True
    path = xml_report(tmp_path, count=1, failures=1, message='unrelated failure')
    with pytest.raises(gate.GateError, match='negative_reason'):
        gate.check_junit(path, negative=True)


def test_bounded_process_output_and_timeout(tmp_path):
    result = gate.run_process([sys.executable,'-I','-B','-c','print("OK")'], cwd=tmp_path, env=None, timeout=5, cap=100)
    assert result == (0,b'OK\n') or result == (0,b'OK\r\n')
    with pytest.raises(gate.GateError, match='process_output_cap'):
        gate.run_process([sys.executable,'-I','-B','-c','print("X"*10000)'],cwd=tmp_path,env=None,timeout=5,cap=10)
    with pytest.raises(gate.GateError, match='process_timeout'):
        gate.run_process([sys.executable,'-I','-B','-c','import time; time.sleep(10)'],cwd=tmp_path,env=None,timeout=.15,cap=100)


def test_transport_default_is_offline():
    from scripts import phase16_bot_linux_gate as local
    args = local.parser().parse_args(['--bundle','candidate.zip'])
    assert args.execute is False


def test_transport_framing_binds_remote_script():
    from scripts import phase16_bot_linux_gate as local
    script = b'print("synthetic")\n'
    command, frame = local.frame_request(script,b'zip')
    assert frame == b'00000019' + script + b'zip'
    assert hashlib.sha256(script).hexdigest() in command
    assert '/usr/bin/python3 -I -B -c' in command
    assert gate.APPROVAL in command


def test_transport_requires_exact_approval_before_trust_or_claim(tmp_path):
    from scripts import phase16_bot_linux_gate as local
    calls=[]
    with pytest.raises(gate.GateError, match='approval_binding'):
        local.execute_once(b'zip',b'script',tmp_path/'attempt',approval='wrong',approved_sha='bad',
                           loader=lambda role: calls.append(role),transport=lambda *a,**kw:calls.append('ssh'))
    assert calls == [] and not (tmp_path/'attempt').exists()


def test_transport_wrong_candidate_before_trust(tmp_path):
    from scripts import phase16_bot_linux_gate as local
    calls=[]; script=b'print("synthetic")\n'
    with pytest.raises(gate.GateError, match='bundle_binding'):
        local.execute_once(b'zip',script,tmp_path/'attempt',approval=gate.APPROVAL,approved_sha=gate.sha(script),
                           loader=lambda role:calls.append(role),transport=lambda *a,**kw:calls.append('ssh'))
    assert calls == [] and not (tmp_path/'attempt').exists()


def test_transport_unknown_result_never_retries(tmp_path, monkeypatch):
    from scripts import phase16_bot_linux_gate as local
    from types import SimpleNamespace
    calls=[]; script=b'print("synthetic")\n'
    monkeypatch.setattr(gate,'validate_bundle',lambda data: ({},{},{}))
    binding=SimpleNamespace(role='spain',target_user='synthetic',target_host='example.invalid',
                            known_hosts_path=tmp_path/'known_hosts',key_path=tmp_path/'key')
    def transport(*args,**kwargs):
        calls.append('ssh');raise gate.GateError('process_timeout')
    result=local.execute_once(b'zip',script,tmp_path/'attempt',approval=gate.APPROVAL,approved_sha=gate.sha(script),
                              loader=lambda role:binding,transport=transport)
    assert result['status']=='UNKNOWN_NO_RETRY' and calls==['ssh']
    assert result['claim']['destination'].startswith('/opt/amn2-spain/')
    assert (tmp_path/'attempt/claim.json').is_file() and (tmp_path/'attempt/result.json').is_file()
    with pytest.raises(gate.GateError, match='destination_exists'):
        local.execute_once(b'zip',script,tmp_path/'attempt',approval=gate.APPROVAL,approved_sha=gate.sha(script),
                           loader=lambda role:binding,transport=transport)
    assert calls==['ssh']


def test_success_receipt_requires_all_safety_and_signal_fields():
    from scripts import phase16_bot_linux_gate as local
    result={'schema':'phase16.bot-linux-gate.v1','status':'ISOLATED_LINUX_SIGNALS_PASS_NOT_DEPLOYED'}
    with pytest.raises(gate.GateError, match='receipt_binding'):
        local.validate_receipt(result,0)


def test_archive_malformed_junit_counts_not_trusted(tmp_path):
    report=xml_report(tmp_path)
    report.write_text(report.read_text().replace('<testcase name="case0"></testcase>',''))
    with pytest.raises(gate.GateError,match='junit_counts'):
        gate.check_junit(report,negative=False)


def test_transport_bootstrap_preserves_bundle_stdin(tmp_path):
    from scripts import phase16_bot_linux_gate as local
    import shlex
    script=b'import sys; print(sys.stdin.buffer.read().decode("ascii"))\n'
    command,frame=local.frame_request(script,b'SYNTHETIC_BUNDLE')
    argv=shlex.split(command);argv[0]=sys.executable
    rc,output=gate.run_process(argv,cwd=tmp_path,env=None,timeout=5,cap=1024,input_bytes=frame)
    assert rc==0 and output.strip()==b'SYNTHETIC_BUNDLE'


def test_transport_bootstrap_rejects_changed_script(tmp_path):
    from scripts import phase16_bot_linux_gate as local
    import shlex
    script=b'print("MUST_NOT_RUN")\n'
    command,frame=local.frame_request(script,b'SYNTHETIC_BUNDLE')
    frame=frame.replace(b'MUST_NOT_RUN',b'MUST_NOT_RUx',1)
    argv=shlex.split(command);argv[0]=sys.executable
    rc,output=gate.run_process(argv,cwd=tmp_path,env=None,timeout=5,cap=1024,input_bytes=frame)
    assert rc==70 and output==b''
