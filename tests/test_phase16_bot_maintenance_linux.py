"""Local process and filesystem tests; systemd is a strict command-boundary double."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import time
import unittest

from scripts import phase16_bot_maintenance as core
from tests.test_phase16_bot_maintenance import manifest

NAME = 'scripts.phase16_bot_maintenance_linux'
AVAILABLE = importlib.util.find_spec(NAME) is not None
if AVAILABLE:
    from scripts import phase16_bot_maintenance_linux as linux

class Availability(unittest.TestCase):
    def test_linux_adapters_exist(self):
        self.assertTrue(AVAILABLE, 'T14c Linux adapters are missing')

@unittest.skipUnless(AVAILABLE, 'implementation missing; Availability must fail')
class CommandTests(unittest.TestCase):
    def test_child_has_eof_and_no_parent_secret_environment(self):
        os.environ['PHASE16_TEST_SECRET'] = 'private-fixture'
        self.addCleanup(os.environ.pop, 'PHASE16_TEST_SECRET', None)
        result = linux.BoundedCommand()([sys.executable, '-I', '-S', '-c',
            "import os,sys; print(len(sys.stdin.buffer.read()), 'PHASE16_TEST_SECRET' in os.environ)"], 3)
        self.assertEqual(result, b'0 False\n' if os.name != 'nt' else b'0 False\r\n')

    def test_deadline_kills_child_and_never_leaks_error_output(self):
        start = time.monotonic()
        with self.assertRaisesRegex(core.Stop, '^command_deadline$'):
            linux.BoundedCommand()([sys.executable, '-I', '-S', '-c',
                "import sys,time; print('private-fixture',file=sys.stderr,flush=True); time.sleep(20)"], .3)
        self.assertLess(time.monotonic() - start, 4)

    def test_output_cap_and_nonzero_are_closed_errors(self):
        for code, reason in [("print('x'*1000000)", 'command_output_limit'),
                             ("import sys; sys.stderr.write('private-fixture'); sys.exit(9)", 'command_failed')]:
            with self.subTest(reason=reason), self.assertRaisesRegex(core.Stop, '^' + reason + '$'):
                linux.BoundedCommand(maximum=1024)([sys.executable, '-I', '-S', '-c', code], 3)

    def test_default_cli_does_not_execute_and_data_worker_rejects_windows(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, '-B', '-m', NAME], cwd=root,
                                capture_output=True, timeout=5, check=True)
        value = json.loads(result.stdout)
        self.assertEqual(value['status'], 'LOCAL_PRIMITIVES_ONLY')
        self.assertFalse(value['authorized'])
        self.assertFalse(value['live_executor_ready'])
        if sys.platform != 'linux':
            failed = subprocess.run([sys.executable, '-B', '-m', NAME,
                '--data-worker', 'migrate', '--directory', '/does-not-exist',
                '--context-sha256', '0'*64], cwd=root, capture_output=True, timeout=5)
            self.assertEqual(failed.returncode, 2)
            self.assertEqual(failed.stdout + failed.stderr, b'')



class Manager:
    def __init__(self):
        self.properties = {u: dict(Id=u, LoadState='loaded', ActiveState='inactive',
            SubState='dead', Result='success', ExecMainCode='1', ExecMainStatus='0',
            MainPID='0', ControlGroup='', Type='notify' if u == core.BOT else 'simple',
            NeedDaemonReload='no', InvocationID='a'*32, NRestarts='0',
            ActiveEnterTimestampMonotonic='0', ExecMainExitTimestampMonotonic='100',
            StateChangeTimestampMonotonic='100', DropInPaths='') for u in (core.BOT, core.WEB)}
        self.calls = []
        self.on_start = None

    def __call__(self, argv, timeout):
        self.calls.append((argv, timeout))
        if argv[:2] == ['systemctl', 'show']:
            data = self.properties[argv[-1]]
            return ''.join(k + '=' + v + '\n' for k, v in data.items()).encode()
        if argv[:2] == ['systemctl', '--no-block']:
            action, unit = argv[2:]
            if action == 'start':
                if self.on_start:
                    self.on_start(unit)
                self.properties[unit].update(ActiveState='active', SubState='running',
                    MainPID='101', ActiveEnterTimestampMonotonic='200', InvocationID='b'*32)
            return b''
        if argv == ['systemctl', 'daemon-reload']:
            return b''
        raise AssertionError('Unexpected command boundary: ' + repr(argv))


@unittest.skipUnless(AVAILABLE, 'implementation missing; Availability must fail')
class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.manager = Manager()
        self.client = linux.SystemdClient(self.manager, root=self.root, clock=lambda: 300)
        self.journal = core.Journal.create(self.root / 'journal', manifest())
        self.fence = core.SystemdFence(self.root, manifest(), self.client.control)
        self.journal.perform('fence', lambda: self.fence.install(self.journal), lambda: True)

    def test_stop_exit_zero_is_process_quiescence_not_business_drain(self):
        result = self.client.stopped(core.BOT)
        self.assertEqual(result['process_state'], 'QUIESCENT_EXIT_ZERO')
        self.assertEqual(result['business_drain'], 'NOT_ESTABLISHED')
        self.assertFalse(core.quiescent(result))

    def test_failed_killed_or_remaining_cgroup_processes_are_not_quiescent(self):
        for field, value in [('Result', 'timeout'), ('ExecMainCode', '2'),
                             ('ExecMainStatus', '9'), ('MainPID', '101'),
                             ('ActiveState', 'failed')]:
            original = copy.deepcopy(self.manager.properties)
            self.manager.properties[core.BOT][field] = value
            with self.subTest(field=field), self.assertRaises(core.Stop):
                self.client.stopped(core.BOT)
            self.manager.properties = original
        group = self.root / 'sys/fs/cgroup/system.slice' / core.BOT
        group.mkdir(parents=True)
        (group / 'cgroup.procs').write_text('101\n')
        self.manager.properties[core.BOT]['ControlGroup'] = '/system.slice/' + core.BOT
        with self.assertRaisesRegex(core.Stop, 'processes_remain'):
            self.client.stopped(core.BOT)

    def test_start_intent_precedes_manager_request_and_permit_is_closed(self):
        for action in ('stop', 'backup', 'rehearsal', 'migrate'):
            self.journal.perform(action, lambda: None, lambda: True)
        def on_start(unit):
            self.assertEqual(core.Journal.load(self.journal.directory, manifest()).phase,
                             'candidate_start_intent')
            self.assertTrue(self.fence.permit(unit).exists())
        self.manager.on_start = on_start
        self.journal.perform('candidate_start', lambda: self.fence.start(core.BOT, self.journal), lambda: True)
        self.assertFalse(self.fence.permit(core.BOT).exists())
        self.assertTrue(self.journal.candidate_requested)
        self.assertIn((['systemctl', '--no-block', 'start', core.BOT], 5), self.manager.calls)

    def test_foreign_or_replayed_receipt_cannot_prove_new_start(self):
        receipt = dict(_SYSTEMD_UNIT=core.BOT, _SYSTEMD_INVOCATION_ID='b'*32, _BOOT_ID='c'*32,
                       _PID='101', MESSAGE='telegram_persistent_admission=pass bot_identity=@fixture_bot '
                       'webhook_configured=false pending_update_count=0 allowed_updates=message,callback_query')
        args = dict(invocation='b'*32, boot='c'*32, pid=101, expected_username='fixture_bot')
        self.assertTrue(linux.admission_receipt([receipt], **args))
        for field in ('_SYSTEMD_UNIT', '_SYSTEMD_INVOCATION_ID', '_BOOT_ID', '_PID'):
            changed = dict(receipt); changed[field] = 'wrong'
            self.assertFalse(linux.admission_receipt([changed], **args))
        self.assertFalse(linux.admission_receipt([receipt, receipt], **args))

    def test_queued_start_waits_and_timeout_keeps_fence_without_retry(self):
        ticks = [0.0]
        manager = self.manager
        original = manager.__call__
        requests = []
        def queued(argv, timeout):
            if argv[:3] == ['systemctl', '--no-block', 'start']:
                requests.append(argv)
                return b''
            return original(argv, timeout)
        client = linux.SystemdClient(queued, root=self.root, clock=lambda: ticks[0],
            sleep=lambda seconds: ticks.__setitem__(0, ticks[0] + seconds))
        with self.assertRaisesRegex(core.Stop, '^manager_job_unknown_no_retry$'):
            client.control(['systemctl', 'start', core.BOT], 40)
        self.assertEqual(len(requests), 1)
        self.assertTrue(self.fence.present())

    def test_start_response_after_deadline_never_counts_as_ready(self):
        ticks = [0.0]
        original = self.manager.__call__
        queries = [0]
        def delayed(argv, timeout):
            result = original(argv, timeout)
            if argv[:2] == ['systemctl', 'show']:
                queries[0] += 1
                if queries[0] > 1:
                    ticks[0] = 41
            return result
        client = linux.SystemdClient(delayed, root=self.root, clock=lambda: ticks[0])
        with self.assertRaisesRegex(core.Stop, '^manager_job_unknown_no_retry$'):
            client.control(['systemctl', 'start', core.BOT], 40)

    def test_effective_fence_requires_actual_manager_condition_and_loaded_file(self):
        for unit in (core.BOT, core.WEB):
            self.manager.properties[unit]['DropInPaths'] = '/' + str(self.fence.dropin(unit).relative_to(self.root)).replace('\\', '/')
        def run(argv, timeout):
            if argv[0] == 'busctl':
                unit = core.BOT if 'bot' in argv[4] else core.WEB
                condition = ['ConditionPathExists', False, False,
                             '/run/phase16/' + manifest()['operation_id'] + '/' + unit + '.allow', 0]
                return json.dumps(dict(type='a(sbbsi)', data=[condition])).encode()
            return self.manager(argv, timeout)
        client = linux.SystemdClient(run, root=self.root)
        self.assertTrue(callable(getattr(client, 'fence_effective', None)), 'effective fence collector missing')
        self.assertTrue(client.fence_effective(self.fence))
        self.manager.properties[core.WEB]['DropInPaths'] = ''
        self.assertFalse(client.fence_effective(self.fence))

    def test_launch_keeps_configuration_cwd_and_selects_only_candidate_source(self):
        target = dict(candidate_source='/opt/candidate/source', candidate_interpreter='/opt/candidate/venv/bin/python',
                      old_source='/opt/old/source/app')
        artifact = linux.candidate_dropin(target)
        self.assertIn('WorkingDirectory=/opt/old/source\n', artifact)
        self.assertIn('/opt/candidate/venv/bin/python -I -B -u -c ', artifact)
        self.assertIn("sys.path.insert(0,'/opt/candidate/source')", artifact)
        self.assertNotIn('Timeout', artifact)
        self.assertNotIn('Environment=', artifact)
        with self.assertRaises(core.Stop):
            linux.candidate_dropin(dict(target, candidate_source='/opt/evil%h'))

    def test_transient_data_worker_has_network_isolation_and_manager_deadline(self):
        argv = linux.worker_command('phase16-fixture', 'migrate', '/opt/phase16/code',
                                    '/var/lib/amn2-spain/phase16-maintenance/phase16-fixture', 'd'*64)
        self.assertIn('--property=PrivateNetwork=yes', argv)
        self.assertIn('--property=RuntimeMaxSec=120s', argv)
        self.assertIn('--property=KillMode=control-group', argv)
        self.assertIn('--property=Type=exec', argv)
        self.assertIn('--property=StandardOutput=null', argv)
        self.assertNotIn('--scope', argv)
        self.assertNotIn('--collect', argv)
        self.assertIn('--property=ReadWritePaths=/var/lib/amn2-spain', argv)

    def test_remaining_window_reserves_recovery_and_never_refreshes_old_observation(self):
        self.assertTrue(linux.window_allows(remaining=500, action='migrate'))
        self.assertFalse(linux.window_allows(remaining=419, action='migrate'))
        self.assertFalse(linux.window_allows(remaining=100, action='candidate_start'))

if __name__ == '__main__':
    unittest.main()
