"""Only real local Python children: no SSH, network, remote target or retries."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

AVAILABLE = importlib.util.find_spec('scripts.phase16_bot_maintenance_transport') is not None
if AVAILABLE:
    from scripts import phase16_bot_maintenance_transport as transport


class Availability(unittest.TestCase):
    def test_bounded_maintenance_transport_exists(self):
        self.assertTrue(AVAILABLE, '1590-second maintenance transport missing')


@unittest.skipUnless(AVAILABLE, 'availability fails first')
class TransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def child(self, code, *, data=b'', timeout=5, cap=65536, observer=None):
        d = {}
        try:
            rc, output = transport.run_transport([sys.executable, '-I', '-S', '-B', '-c', code],
                cwd=self.root, env=None, timeout=timeout, cap=cap, input_bytes=data,
                diagnostics=d, stdout_observer=observer)
            return rc, output, d
        except transport.TransportError as error:
            return str(error), None, d

    def test_full_two_megabyte_stdin_eof_and_extended_bound_are_supported(self):
        data = b'a' * (2 * 1024 * 1024)
        code = 'import sys,hashlib; d=sys.stdin.buffer.read(); print(len(d)); print(hashlib.sha256(d).hexdigest())'
        rc, out, d = self.child(code, data=data, timeout=1590)
        self.assertEqual(rc, 0)
        self.assertEqual(out.splitlines(), [str(len(data)).encode(), hashlib.sha256(data).hexdigest().encode()])
        self.assertTrue(d['stdin_complete'])
        self.assertTrue(d['output_complete'])
        self.assertEqual(d['stdin_bytes_accepted'], len(data))
        self.assertEqual(d['remote_coordinator_status'], 'UNKNOWN_MAY_CONTINUE')
        self.assertFalse(d['replay_allowed'])
        self.assertEqual(d['termination_scope'], 'LOCAL_TRANSPORT_ONLY')

    def test_partial_stdin_is_not_completed_or_replayed(self):
        code = 'import sys; from pathlib import Path; Path("attempts").write_text("x"); sys.stdin.buffer.read(65536); sys.stdout.buffer.write(b"PARTIAL\\n"); sys.exit(255)'
        reason, out, d = self.child(code, data=b'x' * 2097152)
        self.assertEqual(reason, 'transport_stdin_write')
        self.assertIsNone(out)
        self.assertEqual(d['returncode'], 255)
        self.assertFalse(d['stdin_complete'])
        self.assertLess(d['stdin_bytes_accepted'], 2097152)
        self.assertEqual((self.root / 'attempts').read_text(), 'x')
        self.assertEqual(d['stdout']['prefix_sha256'], hashlib.sha256(b'PARTIAL\n').hexdigest())

    def test_parallel_output_pipes_drain_without_deadlock(self):
        code = 'import sys,threading; a=threading.Thread(target=lambda:sys.stderr.buffer.write(b"e"*20000)); a.start(); sys.stdout.buffer.write(b"o"*20000); sys.stdout.flush(); a.join(); sys.stdin.buffer.read()'
        rc, out, d = self.child(code, data=b'x' * 2097152)
        self.assertEqual(rc, 0)
        self.assertEqual(out, b'o' * 20000)
        self.assertTrue(d['output_complete'])
        self.assertEqual(d['stderr']['bytes_observed'], 20000)
        self.assertEqual(d['stderr']['prefix_sha256'], hashlib.sha256(b'e' * 20000).hexdigest())

    def test_timeout_kills_and_reaps_owned_child_with_blocked_stdin(self):
        seen = []
        real = transport.subprocess.Popen
        def capture(*args, **kwargs):
            p = real(*args, **kwargs)
            seen.append(p)
            return p
        with patch.object(transport.subprocess, 'Popen', side_effect=capture):
            reason, _, d = self.child('import time; time.sleep(30)', data=b'x' * 2097152, timeout=.5)
        self.assertEqual(reason, 'transport_timeout')
        self.assertEqual(len(seen), 1)
        self.assertIsNotNone(seen[0].poll())
        self.assertEqual(d['termination_action'], 'KILL_LOCAL_CHILD')
        self.assertTrue(d['local_child_reaped'])
        self.assertFalse(d['stdin_complete'])
        self.assertLess(d['elapsed_seconds'], 3)
        self.assertFalse(d['replay_allowed'])
        self.assertEqual(d['remote_coordinator_status'], 'UNKNOWN_MAY_CONTINUE')

    def test_combined_cap_and_secret_output_never_leak_in_diagnostics(self):
        secret = 'PRIVATE_KEY=do-not-echo'
        code = 'import sys; sys.stderr.write(' + repr(secret) + '); sys.stderr.flush(); sys.stdout.buffer.write(b"x"*65537); sys.stdout.flush()'
        reason, _, d = self.child(code, cap=100)
        self.assertEqual(reason, 'transport_output_cap')
        self.assertLessEqual(sum(d[k]['bytes_retained'] for k in ('stdout', 'stderr')), 100)
        self.assertFalse(d['output_complete'])
        self.assertNotIn(secret, json.dumps(d))
        self.assertTrue(d['stderr_diagnostic']['output_cap_hit'])

    def test_secret_stderr_is_only_hash_counts_and_fixed_hints(self):
        data = b'Connection reset PRIVATE_TOKEN=secret\n'
        rc, out, d = self.child('import sys; sys.stderr.buffer.write(' + repr(data) + '); raise SystemExit(23)')
        self.assertEqual((rc, out), (23, b''))
        self.assertEqual(d['stderr']['prefix_sha256'], hashlib.sha256(data).hexdigest())
        self.assertEqual(d['stderr']['bytes_retained'], len(data))
        self.assertIn('SSH_CONNECTION_RESET_HINT', d['stderr_diagnostic']['hints'])
        self.assertNotIn('PRIVATE', json.dumps(d))
        self.assertEqual(d['stderr_diagnostic']['root_cause'], 'NOT_ESTABLISHED')

    def test_exact_output_cap_with_both_eof_is_complete(self):
        rc, out, d = self.child('import sys; sys.stdout.buffer.write(b"x"*65536)')
        self.assertEqual(rc, 0)
        self.assertEqual(len(out), 65536)
        self.assertTrue(d['output_complete'])

    def test_success_does_not_retry_or_imply_remote_maintenance_success(self):
        code = 'from pathlib import Path; p=Path("attempts"); p.write_text(p.read_text()+"x" if p.exists() else "x"); raise SystemExit(7)'
        rc, _, d = self.child(code)
        self.assertEqual(rc, 7)
        self.assertEqual((self.root / 'attempts').read_text(), 'x')
        self.assertIsNone(d['failure_stage'])
        self.assertFalse(d['automatic_retry'])
        self.assertEqual(d['remote_coordinator_status'], 'UNKNOWN_MAY_CONTINUE')


    def test_inherited_pipe_never_turns_exited_child_into_complete_receipt(self):
        # One deliberate local descendant demonstrates EOF uncertainty. It is
        # separately cleaned by the test, never presented as remotely stopped.
        grandchild = 'import time; time.sleep(4)'
        code = ('import subprocess,sys; from pathlib import Path; '
                'p=subprocess.Popen([sys.executable,"-I","-S","-B","-c",' + repr(grandchild) + '],'
                'stdin=subprocess.DEVNULL,stdout=sys.stdout,stderr=sys.stderr,cwd=sys.prefix); '
                'Path("descendant-pid").write_text(str(p.pid))')
        try:
            reason, _, d = self.child(code, timeout=1)
            self.assertEqual(reason, 'transport_timeout')
            self.assertEqual(d['returncode'], 0)
            self.assertTrue(d['local_child_reaped'])
            if os.name == 'nt':
                self.assertFalse(d['output_complete'])
            self.assertLess(d['elapsed_seconds'], 2)
        finally:
            path = self.root / 'descendant-pid'
            if path.exists():
                try: os.kill(int(path.read_text()), 15)
                except ProcessLookupError: pass
                except OSError: pass

    def test_stdout_and_stderr_overflow_with_unread_stdin_is_bounded(self):
        code = 'import sys,threading,time; a=threading.Thread(target=lambda:sys.stderr.buffer.write(b"e"*1000000)); a.start(); sys.stdout.buffer.write(b"o"*1000000); sys.stdout.flush(); time.sleep(30)'
        reason, _, d = self.child(code, data=b'x' * 2097152, timeout=2, cap=4096)
        self.assertEqual(reason, 'transport_output_cap')
        self.assertLessEqual(sum(d[k]['bytes_retained'] for k in ('stdout', 'stderr')), 4096)
        self.assertTrue(d['local_child_reaped'])
        self.assertLess(d['elapsed_seconds'], 2)

    def test_bad_limits_stop_before_any_child(self):
        bad = [{'timeout': 0}, {'timeout': 1591}, {'timeout': float('nan')}, {'timeout': float('inf')},
               {'timeout': True}, {'cap': 65537}, {'cap': True}, {'input_bytes': b'x' * 2097153},
               {'input_bytes': 'PRIVATE'}, {'command': 'PRIVATE'}, {'command': ['a\x00PRIVATE']}]
        for item in bad:
            with self.subTest(keys=sorted(item)), patch.object(transport.subprocess, 'Popen') as spawn:
                kwargs = dict(command=['PRIVATE_MUST_NOT_RUN'], cwd=self.root, env=None, timeout=1, diagnostics={})
                kwargs.update(item)
                with self.assertRaisesRegex(transport.TransportError, '^transport_limits$'):
                    transport.run_transport(**kwargs)
                spawn.assert_not_called()

    def test_start_failure_does_not_echo_path_or_exception(self):
        d = {}
        with self.assertRaisesRegex(transport.TransportError, '^transport_start$'):
            transport.run_transport([str(self.root / 'PRIVATE_MISSING')], cwd=self.root, env=None,
                                    timeout=1, diagnostics=d)
        self.assertEqual(d['termination_action'], 'NOT_STARTED')
        self.assertFalse(d['local_child_reaped'])
        self.assertNotIn('PRIVATE', json.dumps(d))

    def test_any_observer_is_rejected_before_child_or_callback(self):
        called = []
        def observer(_): called.append(True)
        for callback in (observer, 'PRIVATE_NONCALLABLE'):
            with self.subTest(callable=callable(callback)), patch.object(transport.subprocess, 'Popen') as child:
                with self.assertRaisesRegex(transport.TransportError, '^transport_observer_unsupported$'):
                    transport.run_transport([sys.executable, '-c', 'pass'], cwd=self.root, env=None,
                        timeout=1, diagnostics={}, stdout_observer=callback)
                child.assert_not_called()
        self.assertEqual(called, [])


if __name__ == '__main__':
    unittest.main()
