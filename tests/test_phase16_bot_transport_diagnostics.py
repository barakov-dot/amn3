"""Real local children and bound partial frames; no SSH or target access."""
import importlib
import importlib.util
import json
from pathlib import Path
import shlex
import sys
import tempfile
import unittest

from scripts import phase16_bot_runtime40_stage_gate as stage


class DiagnosticsTests(unittest.TestCase):
    def setUp(self):
        name = 'scripts.phase16_bot_transport_diagnostics'
        self.assertIsNotNone(importlib.util.find_spec(name), 'new diagnostic transport missing')
        self.transport = importlib.import_module(name)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def child(self, code, data=b'', timeout=5, cap=65536):
        d = {}
        try:
            rc, output = self.transport.run_transport(
                [sys.executable, '-I', '-S', '-B', '-c', code],
                cwd=self.root, env=None, timeout=timeout, cap=cap,
                input_bytes=data, diagnostics=d)
            return rc, output, d
        except self.transport.gate.GateError as error:
            return str(error), None, d

    def test_early_exit_preserves_multiple_hints_and_no_raw_text(self):
        message = "Timeout, server PRIVATE_HOST not responding.\nclient_loop: send disconnect: Connection reset PRIVATE_SECRET\n"
        code = 'import sys; sys.stdin.buffer.read(65536); sys.stderr.write(' + repr(message) + '); sys.exit(255)'
        reason, output, d = self.child(code, data=b'x' * 1048576)
        self.assertEqual(reason, 'transport_stdin_write')
        self.assertIsNone(output)
        self.assertEqual(d['returncode'], 255)
        self.assertFalse(d['stdin_complete'])
        self.assertLess(d['stdin_bytes_accepted'], 1048576)
        self.assertIn('SSH_SERVER_ALIVE_TIMEOUT_HINT', d['stderr_diagnostic']['hints'])
        self.assertIn('SSH_SEND_DISCONNECT_HINT', d['stderr_diagnostic']['hints'])
        self.assertIn('SSH_CONNECTION_RESET_HINT', d['stderr_diagnostic']['hints'])
        self.assertNotIn('PRIVATE_', json.dumps(d))
        self.assertEqual(d['termination_action'], 'NONE')
        self.assertGreaterEqual(d['elapsed_seconds'], 0)
        self.assertLessEqual(d['last_stdin_progress_seconds'], d['elapsed_seconds'])

    def test_unknown_stderr_remains_unknown_without_echoing_it(self):
        rc, _, d = self.child('import sys; sys.stderr.write("PRIVATE_UNKNOWN"); sys.exit(23)')
        self.assertEqual(rc, 23)
        self.assertEqual(d['stderr_diagnostic']['hints'], [])
        self.assertEqual(d['stderr_diagnostic']['status'], 'UNCLASSIFIED')
        self.assertNotIn('PRIVATE_UNKNOWN', json.dumps(d))

    def test_stderr_hint_never_overrides_exit_or_proves_root_cause(self):
        rc, out, d = self.child('import sys; sys.stdin.buffer.read(); sys.stderr.write("Connection reset"); print("ok")', b'abc')
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), b'ok')
        self.assertTrue(d['stdin_complete'])
        self.assertIsNone(d['failure_stage'])
        self.assertEqual(d['stderr_diagnostic']['root_cause'], 'NOT_ESTABLISHED')

    def test_timeout_terminates_local_child_and_retains_progress_timing(self):
        reason, _, d = self.child('import time; time.sleep(10)', timeout=.15)
        self.assertEqual(reason, 'transport_timeout')
        self.assertEqual(d['termination_action'], 'KILL_LOCAL_CHILD')
        self.assertIsNotNone(d['returncode'])
        self.assertLess(d['elapsed_seconds'], 5)
        self.assertIsNone(d['last_stdin_progress_seconds'])

    def test_combined_cap_is_preserved_and_classification_marks_truncation(self):
        reason, _, d = self.child('import sys; sys.stdout.buffer.write(b"x"*60); sys.stdout.flush(); sys.stderr.buffer.write(b"y"*60)', cap=100)
        self.assertEqual(reason, 'transport_output_cap')
        self.assertLessEqual(sum(d[k]['bytes_retained'] for k in ('stdout','stderr')), 100)
        self.assertFalse(d['output_complete'])
        self.assertTrue(d['stderr_diagnostic']['output_cap_hit'])

    def test_start_failure_redacts_executable_and_error_message(self):
        d = {}
        with self.assertRaisesRegex(self.transport.gate.GateError, '^transport_start$'):
            self.transport.run_transport([str(self.root/'PRIVATE_MISSING_EXE')], cwd=self.root,
                env=None, timeout=1, diagnostics=d)
        self.assertEqual(d['failure_stage'], 'start')
        self.assertEqual(d['termination_action'], 'NOT_STARTED')
        self.assertNotIn('PRIVATE_', json.dumps(d))

    def test_single_child_has_no_retry_on_failure(self):
        code = 'from pathlib import Path; p=Path("attempts"); p.write_text(p.read_text()+"x" if p.exists() else "x"); raise SystemExit(7)'
        rc, _, _ = self.child(code)
        self.assertEqual(rc, 7)
        self.assertEqual((self.root/'attempts').read_text(), 'x')

    def test_classifier_is_bounded_and_handles_invalid_utf8(self):
        d = self.transport.classify_stderr(b'\xffPRIVATE_UNKNOWN\x1b[31m', output_cap_hit=False)
        self.assertEqual(d['hints'], [])
        self.assertFalse(d['utf8_valid'])
        self.assertNotIn('PRIVATE_', json.dumps(d))
        with self.assertRaises(ValueError):
            self.transport.classify_stderr(b'x' * 65537, output_cap_hit=False)

    def test_bad_limits_stop_before_child_creation(self):
        for limits in ({'timeout':0}, {'timeout':331}, {'timeout':1,'cap':65537}):
            with self.subTest(limits=limits), self.assertRaises(self.transport.gate.GateError):
                self.transport.run_transport(['PRIVATE_MUST_NOT_RUN'], cwd=self.root, env=None,
                    diagnostics={}, **limits)

    def test_exact_stage_bootstrap_rejects_partial_bundle_before_stage(self):
        script = stage.remote_script()
        # Same accepted frame length as failed001, synthetic body deliberately not a zip.
        command, frame = stage.frame_request(script, b'x' * (3702784 - 8 - len(script)))
        args = shlex.split(command)
        d = {}
        rc, output = self.transport.run_transport([sys.executable, *args[1:]],
            cwd=self.root, env=None, timeout=5, input_bytes=frame, diagnostics=d)
        receipt = stage.validate_receipt(json.loads(output), rc)
        self.assertEqual(receipt['reason'], 'bundle_binding')
        self.assertEqual(receipt['status'], 'STOP_BEFORE_STAGE_OR_UNKNOWN')
        self.assertEqual(receipt['steps'], [])
        self.assertEqual(receipt['service_actions'], 0)
        self.assertFalse(receipt['live_database_opened'])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_script_tamper_rejected_before_remote_main(self):
        script = stage.remote_script()
        command, frame = stage.frame_request(script, b'')
        frame = frame[:8] + bytes([frame[8] ^ 1]) + frame[9:]
        d = {}
        rc, output = self.transport.run_transport([sys.executable, *shlex.split(command)[1:]],
            cwd=self.root, env=None, timeout=5, input_bytes=frame, diagnostics=d)
        self.assertEqual(rc, 70)
        self.assertEqual(output, b'')
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
