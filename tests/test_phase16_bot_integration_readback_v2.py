"""Local regression coverage; no SSH, production DB or application imports."""
import contextlib
import copy
import importlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


from scripts.vps import phase16_bot_integration_readback_v2 as core
from scripts.vps import phase16_bot_integration_readback_remote_v2 as remote
from scripts import phase16_bot_integration_readback_gate_009 as legacy


class RuntimeReadbackFixTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def metadata(self, size, name='example'):
        directory = self.root / (name + '.dist-info')
        directory.mkdir(exist_ok=True)
        prefix = ('Name: ' + name + '\nVersion: 1.0\n\n').encode()
        (directory / 'METADATA').write_bytes(prefix + b'x' * (size - len(prefix)))

    def test_candidate_sized_metadata_are_accepted_without_body_disclosure(self):
        for size, name in ((109397, 'pydantic'), (103964, 'yarl')):
            self.metadata(size, name)
        try:
            result = core.collect_dependencies(self.root, {'pydantic': '1.0', 'yarl': '1.0'})
        except core.Stop as error:
            self.fail('candidate metadata rejected: ' + str(error))
        self.assertEqual(result['matched'], ['pydantic', 'yarl'])
        self.assertNotIn('xxxx', json.dumps(result))

    def test_metadata_new_boundary_accepts_exact_cap_rejects_one_more(self):
        self.metadata(262144)
        try:
            result = core.collect_dependencies(self.root, {'example': '1.0'})
        except core.Stop as error:
            self.fail('exact cap rejected: ' + str(error))
        self.assertEqual(result['matched'], ['example'])
        self.metadata(262145)
        with self.assertRaisesRegex(core.Stop, '^file_cap$'):
            core.collect_dependencies(self.root, {'example': '1.0'})

    def test_pth_limit_stays_64k(self):
        pth = self.root / 'never_execute.pth'
        pth.write_bytes(b'x' * 65536)
        self.assertEqual(core.collect_dependencies(self.root, {})['pth_count'], 1)
        pth.write_bytes(b'x' * 65537)
        with self.assertRaisesRegex(core.Stop, '^file_cap$'):
            core.collect_dependencies(self.root, {})

    def test_dependency_total_budget_still_stops(self):
        for index in range(33):
            self.metadata(262144, 'example' + str(index))
        with self.assertRaisesRegex(core.Stop, '^dependency_cap$'):
            core.collect_dependencies(self.root, {})

    def test_dependency_count_and_time_caps_still_stop(self):
        for index in range(129):
            self.metadata(64, 'example' + str(index))
        with self.assertRaisesRegex(core.Stop, '^dependency_cap$'):
            core.collect_dependencies(self.root, {})
        with patch.object(core.time, 'monotonic', side_effect=[0, 9]):
            with self.assertRaisesRegex(core.Stop, '^dependency_cap$'):
                core.collect_dependencies(self.root, {})

    def test_dependency_path_and_identity_guards_still_stop(self):
        self.metadata(64)
        with patch.object(core, 'checked_path', side_effect=core.Stop('path_link')):
            with self.assertRaisesRegex(core.Stop, '^path_link$'):
                core.collect_dependencies(self.root, {})
        real_fstat = core.os.fstat
        def changed(fd):
            result = real_fstat(fd)
            return SimpleNamespace(st_mode=result.st_mode, st_dev=result.st_dev,
                                   st_ino=result.st_ino + 1)
        with patch.object(core.os, 'fstat', side_effect=changed):
            with self.assertRaisesRegex(core.Stop, '^file_identity$'):
                core.collect_dependencies(self.root, {})

    def dependency_failure(self, error):
        fixture = legacy.base.pass_receipt_for_tests()
        output = io.StringIO()
        with contextlib.ExitStack() as stack:
            for obj, name, value in (
                (remote.sys, 'platform', 'linux'),
                (remote.sys, 'version_info', (3, 12, 0)),
                (remote.sys, 'argv', ['remote.py', remote.APPROVAL]),
                (remote.sys, 'stdin', type('Input', (), {'buffer': io.BytesIO(b'x')})()),
                (remote, 'SOURCE_ROOT', self.root), (remote, 'DEPENDENCY_ROOT', self.root),
            ):
                stack.enter_context(patch.object(obj, name, value))
            stack.enter_context(patch.object(remote.platform, 'machine', return_value='x86_64'))
            stack.enter_context(patch.object(remote, 'parse_payload', return_value={
                'core': b'', 'manifest': {'source': {}, 'runtime_pins': {}}}))
            stack.enter_context(patch.object(remote, 'load_core', return_value=core))
            stack.enter_context(patch.object(remote, 'host_receipt', return_value=fixture['host']))
            stack.enter_context(patch.object(remote, 'collect_units', return_value=fixture['units_before']))
            stack.enter_context(patch.object(core, 'collect_source', return_value=fixture['source']))
            stack.enter_context(patch.object(core, 'collect_dependencies', side_effect=error))
            child = stack.enter_context(patch.object(remote, 'collect_database'))
            stack.enter_context(patch.object(remote, 'install_deadline'))
            stack.enter_context(patch.object(remote, 'arm_finalization'))
            stack.enter_context(patch.object(remote.signal, 'setitimer', create=True))
            stack.enter_context(patch.object(remote.signal, 'ITIMER_REAL', 0, create=True))
            stack.enter_context(contextlib.redirect_stdout(output))
            self.assertEqual(remote.main(), 3)
            child.assert_not_called()
        return json.loads(output.getvalue())

    def test_core_stop_preserves_stage_and_partial_evidence_through_validator(self):
        value = self.dependency_failure(core.Stop('file_cap'))
        self.assertEqual(value['reason'], 'dependencies_file_cap')
        self.assertEqual(set(value['partial']), {'host', 'units_before', 'source'})
        self.assertEqual(legacy.validate_receipt_numeric(value, 3), value)

    def test_missing_denied_and_unknown_errors_are_fixed_and_redacted(self):
        for error, reason in ((FileNotFoundError('/SECRET'), 'path_missing'),
                              (PermissionError('/SECRET'), 'permission_denied'),
                              (OSError('/SECRET'), 'os_error'),
                              (ValueError('SECRET'), 'exception'),
                              (core.Stop('secret_lowercase'), 'core_stop')):
            with self.subTest(reason=reason):
                value = self.dependency_failure(error)
                self.assertEqual(value['reason'], 'dependencies_' + reason)
                self.assertNotIn('SECRET', json.dumps(value))
                self.assertNotIn('secret_lowercase', json.dumps(value))

    def test_timeout_remains_terminal_without_db_open(self):
        value = self.dependency_failure(remote.RemoteStop('remote_timeout'))
        self.assertEqual(value['reason'], 'remote_timeout')

    def test_remote_stop_cannot_disclose_arbitrary_lowercase_message(self):
        value = self.dependency_failure(remote.RemoteStop('secret_lowercase'))
        self.assertEqual(value['reason'], 'remote_gate')
        self.assertNotIn('secret_lowercase', json.dumps(value))

    def child(self, value, code=3, stderr=0):
        output = json.dumps(value).encode()
        with patch.object(remote.os, 'readlink', return_value='mnt:[12]'), \
             patch.object(remote, 'run_bounded', return_value=(code, output, {
                 'stdout_bytes': len(output), 'stderr_bytes': stderr, 'stderr_present': bool(stderr)})):
            return remote.collect_database(b'payload')

    def test_child_allowlisted_stop_reason_is_preserved(self):
        with self.assertRaisesRegex(remote.RemoteStop, '^database_sqlite_sidecars$'):
            self.child({'schema': 'phase16.integration-db-child.v1', 'status': 'STOP',
                        'reason': 'sqlite_sidecars'})

    def test_child_untrusted_reason_extra_fields_exit_and_stderr_are_rejected(self):
        value = {'schema': 'phase16.integration-db-child.v1', 'status': 'STOP',
                 'reason': 'secret_lowercase'}
        cases = [(value, 3, 0), ({**value, 'reason': 'sqlite_sidecars', 'extra': 'SECRET'}, 3, 0),
                 ({**value, 'reason': 'sqlite_sidecars'}, 0, 0),
                 ({**value, 'reason': 'sqlite_sidecars'}, 3, 1)]
        for item, code, stderr in cases:
            with self.subTest(code=code, stderr=stderr, item=item):
                with self.assertRaisesRegex(remote.RemoteStop, '^database_child$'):
                    self.child(item, code, stderr)

    def test_child_pass_and_invalid_json_are_distinct(self):
        database = {'status': 'SHAPE_ONLY'}
        value, _ = self.child({'schema': 'phase16.integration-db-child.v1',
                              'status': 'PASS', 'database': database}, 0)
        self.assertEqual(value, database)
        with patch.object(remote.os, 'readlink', return_value='mnt:[12]'), \
             patch.object(remote, 'run_bounded', return_value=(3, b'SECRET', {'stderr_bytes': 0})):
            with self.assertRaisesRegex(remote.RemoteStop, '^database_child$'):
                remote.collect_database(b'payload')

    def test_all_stage_core_errors_are_classified_and_unknown_stage_rejected(self):
        self.assertTrue(callable(getattr(remote, 'at_stage', None)))
        for stage in remote.STAGES:
            with self.subTest(stage=stage):
                with self.assertRaisesRegex(remote.RemoteStop, '^' + stage + '_file_identity$'):
                    remote.at_stage(core, stage, lambda: core.require(False, 'file_identity'))
        with self.assertRaisesRegex(remote.RemoteStop, '^stage_contract$'):
            remote.at_stage(core, 'SECRET', lambda: None)


class RuntimeReadbackBindingTests(unittest.TestCase):
    def gate(self):
        path = ROOT / 'scripts/phase16_bot_integration_readback_gate_v2.py'
        self.assertTrue(path.is_file(), 'versioned bound runner is missing')
        return importlib.import_module('scripts.phase16_bot_integration_readback_gate_v2')

    def test_guard_code_is_unchanged_except_metadata_cap(self):
        old = (ROOT / 'scripts/vps/phase16_bot_integration_readback.py').read_bytes()
        new = (ROOT / 'scripts/vps/phase16_bot_integration_readback_v2.py').read_bytes()
        old = old.replace(b'\r\n', b'\n')
        self.assertEqual(new.replace(b'\r\n', b'\n'), old.replace(
            b"safe_read(Path(entry.path)/'METADATA', 65536)",
            b"safe_read(Path(entry.path)/'METADATA', 262144)"))

    def test_new_payload_and_child_binding_are_consistent(self):
        gate = self.gate()
        payload = gate.build_payload(ROOT)
        self.assertEqual(remote.parse_payload(payload)['core'],
                         gate.canonical(ROOT / 'scripts/vps/phase16_bot_integration_readback_v2.py'))
        self.assertIn(remote.PAYLOAD_SHA256, remote.CHILD_BOOTSTRAP)
        self.assertIn(remote.CORE_SHA256, remote.CHILD_BOOTSTRAP)
        self.assertIn('read(' + str(len(payload) + 1) + ')', remote.CHILD_BOOTSTRAP)
        self.assertIn('len(p)!=' + str(len(payload)), remote.CHILD_BOOTSTRAP)
        with self.assertRaisesRegex(remote.RemoteStop, '^payload_binding$'):
            remote.parse_payload(payload[:-1] + bytes([payload[-1] ^ 1]))

    def test_new_manifest_binds_caps_and_all_blobs(self):
        gate = self.gate()
        manifest = gate.gate_manifest(ROOT)
        self.assertEqual(gate.validate_gate_manifest(manifest, ROOT), manifest)
        self.assertEqual(manifest['limits']['dependency_metadata_file_bytes'], 262144)
        self.assertEqual(manifest['limits']['dependency_total_bytes'], 8388608)
        self.assertFalse(manifest['limits']['retry'])
        for name in manifest['sha256_lf']:
            altered = copy.deepcopy(manifest)
            altered['sha256_lf'][name] = '0' * 64
            with self.subTest(blob=name), self.assertRaises(gate.Stop):
                gate.validate_gate_manifest(altered, ROOT)

    def test_old_approval_is_rejected_before_claim_or_trust(self):
        gate = self.gate()
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'attempt'
            for old in (legacy.APPROVAL, legacy.OLD_APPROVAL):
                with self.assertRaisesRegex(gate.Stop, '^approval_binding$'):
                    gate.execute_once(dest, approval=old, approved_remote_sha='0'*64,
                        approved_manifest_sha='0'*64, approved_gate_sha='0'*64, manifest={},
                        loader=lambda role: self.fail('trust read'),
                        transport=lambda *a, **k: self.fail('SSH'))
            self.assertFalse(dest.exists())

    def execute_fixture(self, receipt, code, transport_error=None):
        gate = self.gate()
        manifest = gate.gate_manifest(ROOT)
        calls = []
        def transport(args, **kwargs):
            calls.append(kwargs)
            kwargs['diagnostics'].update({'returncode': code, 'stdin_complete': True})
            if transport_error:
                raise transport_error
            return code, json.dumps(receipt).encode()
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(gate, 'ssh_environment', return_value={'PROGRAMDATA': 'fixture'}), \
             patch.object(gate, 'binding_digest', return_value=manifest['target_binding_sha256']):
            dest = Path(tmp) / 'attempt'
            result = gate.execute_once(dest, approval=gate.APPROVAL,
                approved_remote_sha=gate.sha(gate.remote_script()),
                approved_manifest_sha=remote.MANIFEST_SHA256,
                approved_gate_sha=gate.gate_sha(), manifest=manifest,
                loader=lambda role: SimpleNamespace(role='spain', known_hosts_path='fixture_hosts',
                    key_path='fixture_key', target_user='fixture', target_host='invalid.test'),
                transport=transport)
            self.assertEqual(json.loads((dest / 'result.json').read_text()), result)
            with self.assertRaisesRegex(gate.Stop, '^evidence_exists$'):
                gate.claim_directory(dest)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]['timeout'], 60)
        self.assertEqual(calls[0]['cap'], 65536)
        self.assertEqual(result['ssh_attempts'], 1)
        return result

    def test_pass_and_stop_survive_one_transport_and_numeric_validation(self):
        fixture = legacy.base.pass_receipt_for_tests()
        for snapshot in ('units_before', 'units_after'):
            for role in ('bot', 'web'):
                fixture[snapshot][role]['KillSignal'] = '15'
                fixture[snapshot][role]['FinalKillSignal'] = '9'
        cases = [(fixture, 0), (remote.stop_receipt('dependencies_file_cap', {
            'host': fixture['host'], 'units_before': fixture['units_before'],
            'source': fixture['source']}), 3)]
        for value, code in cases:
            with self.subTest(code=code):
                result = self.execute_fixture(value, code)
                self.assertEqual(result['remote'], value)
                self.assertEqual(result['status'], value['status'])

    def test_malformed_and_mutating_receipts_fail_without_retaining_raw_response(self):
        fixture = legacy.base.pass_receipt_for_tests()
        for value, code in (({**fixture, 'secret_extra': 'SECRET'}, 0),
                            ({**fixture, 'service_actions': 1}, 0), (fixture, 3),
                            (remote.stop_receipt('secret_lowercase'), 3)):
            with self.subTest(code=code):
                result = self.execute_fixture(value, code)
                self.assertEqual(result['status'], 'UNKNOWN_NO_RETRY')
                self.assertNotIn('remote', result)
                self.assertNotIn('SECRET', json.dumps(result))
                self.assertNotIn('secret_lowercase', json.dumps(result))

    def test_unexpected_transport_exception_is_not_reflected(self):
        result = self.execute_fixture({}, 3, ValueError('secret_lowercase'))
        self.assertEqual(result['status'], 'UNKNOWN_NO_RETRY')
        self.assertEqual(result['reason'], 'local_exception')
        self.assertNotIn('secret_lowercase', json.dumps(result))

    def test_preview_never_reads_trust_or_starts_transport(self):
        gate = self.gate()
        output = io.StringIO()
        with patch.object(gate, 'run_transport', side_effect=AssertionError('SSH')), \
             patch.object(gate, 'ssh_environment', side_effect=AssertionError('environment')), \
             contextlib.redirect_stdout(output):
            self.assertEqual(gate.main([]), 0)
        self.assertEqual(json.loads(output.getvalue())['ssh_attempts'], 0)


if __name__ == '__main__':
    unittest.main()
