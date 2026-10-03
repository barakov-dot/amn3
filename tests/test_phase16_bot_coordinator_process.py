"""Persistent coordinator contract: real journal/SQLite, strict systemd boundary."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_jobs as jobs
from tests import test_phase16_bot_maintenance_sequence as fixtures

AVAILABLE = importlib.util.find_spec('scripts.phase16_bot_coordinator_process') is not None
if AVAILABLE:
    from scripts import phase16_bot_coordinator_process as process


class Availability(unittest.TestCase):
    def test_persistent_coordinator_exists(self):
        self.assertTrue(AVAILABLE, 'manager-owned coordinator implementation missing')


@unittest.skipUnless(AVAILABLE, 'availability fails first')
class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.fixture = f = fixtures.SequenceTests('test_all_eight_steps_reach_release_with_real_data_and_evidence')
        f.setUp()
        self.addCleanup(f.doCleanups)
        self.root, self.directory, self.journal = f.root, f.directory, f.journal
        code = self.root / 'opt/phase16/code'
        source = Path(__file__).resolve().parents[1]
        for name in process.WORKER_FILES:
            dest = code / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, dest)
        (code / 'scripts/fixture_entry.py').write_text('def bind(supervisor):\n    raise RuntimeError("unbound")\n')
        self.entry = 'scripts.fixture_entry'
        self.process = process.CoordinatorSupervisor(f.supervisor, entry_module=self.entry)
        self.unit = f.operation + '-coordinator.service'
        self.invocation = 'd' * 32
        self.pid = 401
        self.launches = 0
        self.mode = 'success'
        self.overrides = {}
        self.worker_called = 0
        self.active = False
        self.native = f.client.run
        f.client.run = self.command
        self.prepare_proc()
        self.readlink = patch.object(process.os, 'readlink', side_effect=self.namespace)
        self.readlink.start()
        self.addCleanup(self.readlink.stop)
        self.after_worker = lambda: None

    def namespace(self, path):
        self.assertTrue(str(path).replace('\\', '/').endswith('/ns/net'))
        return 'net:[4026531840]'

    def prepare_proc(self):
        directory = self.root / 'proc' / str(self.pid)
        directory.mkdir(parents=True)
        (directory / 'cgroup').write_bytes(('0::/system.slice/' + self.unit + '\n').encode())
        (directory / 'cmdline').write_bytes(b'\0'.join(s.encode() for s in self.process.worker_argv()) + b'\0')
        fields = ['S'] + ['0'] * 18 + ['8765'] + ['0'] * 4
        (directory / 'stat').write_text(str(self.pid) + ' (python3) ' + ' '.join(fields))
        cgroup = self.root / 'sys/fs/cgroup/system.slice' / self.unit
        cgroup.mkdir(parents=True)
        (cgroup / 'cgroup.procs').write_text(str(self.pid) + '\n')

    def state(self):
        value = dict(Id=self.unit, LoadState='loaded', ActiveState='active',
            SubState='running' if self.active else 'exited', MainPID=str(self.pid) if self.active else '0',
            ExecMainPID=str(self.pid), Result='success', ExecMainCode='0' if self.active else '1',
            ExecMainStatus='0', InvocationID=self.invocation, NRestarts='0', Type='exec', Restart='no',
            RemainAfterExit='yes', PrivateNetwork='no', PrivateTmp='yes', ProtectSystem='strict',
            ProtectHome='yes', NoNewPrivileges='yes', KillMode='control-group', RuntimeMaxUSec='15min',
            TimeoutStartUSec='10s', TimeoutStopUSec='5s', Slice='system.slice',
            ControlGroup='/system.slice/' + self.unit, User='root', Group='root', UMask='0077',
            StandardInput='null', StandardOutput='null', StandardError='null',
            ReadWritePaths=self.fixture.prepared['target_contract']['maintenance_directory'] + ' /etc/systemd/system /run/phase16',
            ReadOnlyPaths='/opt/phase16/code', ExecMainStartTimestampMonotonic='1')
        value.update(self.overrides)
        return value

    def factory(self, admission):
        self.worker_called += 1
        self.fixture.runner.host_guard = admission
        return self.fixture.runner

    def worker(self, **overrides):
        args = dict(sequence_factory=self.factory, admission=self.fixture.host_guard,
                    invocation=self.invocation, pid=self.pid)
        args.update(overrides)
        return process.execute_coordinator_worker(self.process, **args)

    def command(self, argv, seconds):
        self.assertGreater(seconds, 0)
        self.assertLessEqual(seconds, 15)
        if argv[0] == 'systemd-run' and '--unit=' + self.unit in argv:
            self.launches += 1
            self.assertTrue((self.directory / 'coordinator-claim.json').is_file())
            self.assertTrue((self.directory / 'coordinator-context.json').is_file())
            self.assertEqual(self.journal.phase, 'prepared')
            props = {p[len('--property='):] for p in argv if p.startswith('--property=')}
            self.assertTrue({'Type=exec', 'Restart=no', 'RuntimeMaxSec=900s', 'TimeoutStartSec=10s',
                             'TimeoutStopSec=5s', 'PrivateNetwork=no', 'KillMode=control-group'} <= props)
            self.assertNotIn('--scope', argv)
            self.assertNotIn('--wait', argv)
            self.assertEqual(argv[-len(self.process.worker_argv()):], self.process.worker_argv())
            self.active = True
            if self.mode == 'disconnect':
                raise core.Stop('command_deadline')
            if self.mode == 'pending':
                return b''
            if self.mode != 'missing':
                self.worker()
            self.active = False
            (self.root / 'sys/fs/cgroup/system.slice' / self.unit / 'cgroup.procs').write_text('')
            self.after_worker()
            return b''
        if argv[:2] == ['systemctl', 'show'] and argv[-1] == self.unit:
            if self.mode == 'pending':
                self.fixture.clock[0] += min(30, seconds)
            self.assertEqual(argv, ['systemctl', 'show', '--no-pager',
                                  '--property=' + ','.join(process.FIELDS), self.unit])
            return ''.join(k + '=' + v + '\n' for k, v in self.state().items()).encode()
        return self.native(argv, seconds)

    def test_success_links_actual_sequence_and_manager_receipts(self):
        result = self.process.execute()
        self.assertEqual(result['status'], 'SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE')
        self.assertEqual(self.journal.phase, 'release_done')
        claim = jobs.load_signed(self.directory / 'coordinator-claim.json')
        started = jobs.load_signed(self.directory / 'coordinator-start.json')
        receipt = jobs.load_signed(self.directory / 'coordinator-result.json')
        seqclaim = jobs.load_signed(self.directory / 'sequence-claim.json')
        seqresult = jobs.load_signed(self.directory / 'sequence-result.json')
        complete = jobs.load_signed(self.directory / 'coordinator-complete.json')
        self.assertEqual(started['claim_sha256'], claim['sha256'])
        self.assertEqual(receipt['start_sha256'], started['sha256'])
        self.assertEqual(receipt['sequence_claim_sha256'], seqclaim['sha256'])
        self.assertEqual(receipt['sequence_result_sha256'], seqresult['sha256'])
        self.assertEqual(receipt['invocation'], self.invocation)
        self.assertEqual(complete['result_sha256'], receipt['sha256'])
        self.assertEqual(self.fixture.request_count, 3)
        self.assertEqual(self.worker_called, 1)

    def test_completed_service_accepts_released_control_group(self):
        self.after_worker = lambda: self.overrides.update(ControlGroup='')
        self.assertEqual(self.process.execute()['status'], 'SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE')
        members = self.root / 'sys/fs/cgroup/system.slice' / self.unit / 'cgroup.procs'
        members.unlink()
        self.assertEqual(self.process.readback()['status'], 'SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE')
        self.assertEqual(self.launches, 1)

    def test_released_control_group_still_checks_known_path_for_processes(self):
        def remaining():
            self.overrides['ControlGroup'] = ''
            (self.root / 'sys/fs/cgroup/system.slice' / self.unit / 'cgroup.procs').write_text('999\n')
        self.after_worker = remaining
        with self.assertRaisesRegex(core.Stop, 'coordinator_cgroup'):
            self.process.execute()
        self.assertFalse((self.directory / 'coordinator-complete.json').exists())

    def test_completed_service_rejects_foreign_control_group(self):
        self.after_worker = lambda: self.overrides.update(ControlGroup='/system.slice/foreign.service')
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertFalse((self.directory / 'coordinator-complete.json').exists())

    def test_running_service_requires_exact_control_group(self):
        self.overrides['ControlGroup'] = ''
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertEqual(self.worker_called, 0)

    def test_released_control_group_requires_zero_main_pid(self):
        self.overrides.update(ControlGroup='', MainPID='401')
        with self.assertRaises(core.Stop):
            self.process.query()

    def test_disconnect_retains_claim_and_rejects_second_launch(self):
        self.mode = 'disconnect'
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertTrue((self.directory / 'coordinator-claim.json').is_file())
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertEqual(self.launches, 1)
        self.assertFalse((self.directory / 'coordinator-complete.json').exists())
        # Manager-owned child can complete after initiating client disconnect.
        self.worker()
        self.active = False
        (self.root / 'sys/fs/cgroup/system.slice' / self.unit / 'cgroup.procs').write_text('')
        self.assertEqual(self.process.readback()['status'], 'SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE')
        self.assertEqual(self.launches, 1)

    def test_parent_wait_timeout_never_stops_or_relaunches_service(self):
        self.mode = 'pending'
        with self.assertRaisesRegex(core.Stop, 'coordinator_unknown_no_retry'):
            self.process.execute()
        self.assertLessEqual(self.fixture.clock[0], 930)
        self.assertTrue(self.active)
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertEqual(self.launches, 1)
        self.assertEqual(self.worker_called, 0)

    def test_expired_lease_blocks_before_claim_and_manager(self):
        self.process.utc_now = lambda: fixtures.binding.timestamp(self.fixture.prepared['target_contract']['ownership_valid_until']).timestamp() - 1199
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertEqual(self.launches, 0)
        self.assertFalse((self.directory / 'coordinator-claim.json').exists())

    def test_missing_entry_binding_blocks_launch(self):
        self.process.entry_module = None
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertEqual(self.launches, 0)

    def test_policy_drift_blocks_before_callback(self):
        for field, value in [('Restart', 'always'), ('RuntimeMaxUSec', 'infinity'), ('PrivateNetwork', 'yes'),
                             ('TimeoutStopUSec', '1min'), ('ReadOnlyPaths', ''), ('StandardError', 'journal')]:
            with self.subTest(field=field):
                self.overrides = {field: value}
                self.mode = 'disconnect'
                if not (self.directory / 'coordinator-claim.json').exists():
                    with self.assertRaises(core.Stop):
                        self.process.execute()
                with self.assertRaises(core.Stop):
                    self.worker()
        self.assertEqual(self.worker_called, 0)
        self.assertFalse((self.directory / 'sequence-claim.json').exists())

    def test_wrong_pid_or_invocation_blocks_before_callback(self):
        self.mode = 'disconnect'
        with self.assertRaises(core.Stop):
            self.process.execute()
        for args in [dict(pid=999), dict(invocation='e' * 32)]:
            with self.subTest(args=args), self.assertRaises(core.Stop):
                self.worker(**args)
        self.assertEqual(self.worker_called, 0)

    def test_wrong_cgroup_blocks_before_callback(self):
        (self.root / 'proc/401/cgroup').write_text('0::/user.slice/unrelated.service\n')
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertEqual(self.worker_called, 0)

    def test_namespace_is_checked_before_callback(self):
        self.readlink.stop()
        with patch.object(process.os, 'readlink', side_effect=lambda p: 'net:[2]' if '/401/' in str(p).replace('\\', '/') else 'net:[1]'):
            with self.assertRaises(core.Stop):
                self.process.execute()
        self.assertEqual(self.worker_called, 0)

    def test_missing_admission_never_calls_factory_or_sequence(self):
        self.mode = 'disconnect'
        with self.assertRaises(core.Stop):
            self.process.execute()
        for admission in (None, lambda _: True):
            with self.subTest(admission=admission), self.assertRaises(core.Stop):
                self.worker(admission=admission)
        self.assertEqual(self.worker_called, 0)
        self.assertFalse((self.directory / 'sequence-claim.json').exists())

    def test_worker_cannot_replay_after_started_receipt(self):
        self.process.execute()
        self.active = True
        with self.assertRaises(core.Stop):
            self.worker()
        self.assertEqual(self.worker_called, 1)

    def test_missing_result_never_becomes_complete(self):
        self.mode = 'missing'
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertFalse((self.directory / 'coordinator-complete.json').exists())
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertEqual(self.launches, 1)

    def test_resigned_result_tampering_blocks_acceptance(self):
        def corrupt():
            path = self.directory / 'coordinator-result.json'
            value = jobs.load_signed(path)
            value['sequence_result_sha256'] = '0' * 64
            value.pop('sha256')
            path.write_bytes(core.encoded(dict(value, sha256=core.digest(value))))
        self.after_worker = corrupt
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertFalse((self.directory / 'coordinator-complete.json').exists())

    def test_changed_code_or_context_blocks_factory(self):
        self.mode = 'disconnect'
        with self.assertRaises(core.Stop):
            self.process.execute()
        path = self.root / 'opt/phase16/code/scripts/fixture_entry.py'
        path.write_text('def bind(supervisor):\n    return True\n')
        with self.assertRaises(core.Stop):
            self.worker()
        self.assertEqual(self.worker_called, 0)

    def test_unknown_error_text_is_not_persisted_or_raised(self):
        self.mode = 'disconnect'
        with self.assertRaises(core.Stop):
            self.process.execute()
        def private(_):
            raise ValueError('SECRET=private-fixture')
        with self.assertRaises(core.Stop) as failure:
            self.worker(admission=private)
        self.assertNotIn('private-fixture', str(failure.exception))
        records = [p.read_text() for p in self.directory.glob('coordinator-*.json')]
        self.assertNotIn('private-fixture', ''.join(records))

    def test_admission_consumes_runtime_and_lease_together(self):
        initial_clock = self.process.utc_now
        self.process.utc_now = lambda: initial_clock() + 570
        original = self.fixture.host_guard
        calls = [0]
        def admission(prepared):
            calls[0] += 1
            if calls[0] == 1:
                self.fixture.clock[0] += 50
            return original(prepared)
        self.fixture.host_guard = admission
        self.assertEqual(self.process.execute()['status'], 'SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE')

    def test_claim_fsync_expiration_prevents_manager_submission(self):
        initial_clock = self.process.utc_now
        self.process.utc_now = lambda: initial_clock() + 570
        original = jobs.write_signed
        def slow(path, payload):
            original(path, payload)
            if path.name == 'coordinator-claim.json':
                self.fixture.clock[0] += 1
        with patch.object(jobs, 'write_signed', slow), self.assertRaises(core.Stop):
            self.process.execute()
        self.assertTrue((self.directory / 'coordinator-claim.json').is_file())
        self.assertEqual(self.launches, 0)

    def test_factory_cannot_change_manager_identity_before_sequence(self):
        original = self.factory
        def drift(admission):
            self.overrides['MainPID'] = '999'
            return original(admission)
        self.factory = drift
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertFalse((self.directory / 'sequence-claim.json').exists())

    def test_late_result_readback_cannot_exceed_parent_wait_budget(self):
        original = self.command
        observations = [0]
        def command(argv, seconds):
            if argv[:2] == ['systemctl', 'show'] and argv[-1] == self.unit and not self.active:
                observations[0] += 1
                if observations[0] == 2:
                    self.fixture.clock[0] += min(3, seconds)
            return original(argv, seconds)
        self.fixture.client.run = command
        self.after_worker = lambda: self.fixture.clock.__setitem__(0, 928)
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertFalse((self.directory / 'coordinator-complete.json').exists())

    def test_slow_factory_cannot_start_sequence_after_runtime_budget(self):
        original = self.factory
        def slow(admission):
            self.fixture.clock[0] += 71
            return original(admission)
        self.factory = slow
        with self.assertRaises(core.Stop):
            self.process.execute()
        self.assertFalse((self.directory / 'sequence-claim.json').exists())
        self.assertEqual(self.journal.phase, 'prepared')

    def test_raw_stop_reason_from_admission_is_redacted(self):
        self.mode = 'disconnect'
        with self.assertRaises(core.Stop):
            self.process.execute()
        def private(_):
            raise core.Stop('SECRET=private-fixture')
        with self.assertRaises(core.Stop) as failure:
            self.worker(admission=private)
        self.assertNotIn('private-fixture', str(failure.exception))

    def test_context_change_after_claim_blocks_worker(self):
        self.mode = 'disconnect'
        with self.assertRaises(core.Stop):
            self.process.execute()
        path = self.directory / 'worker-context.json'
        value = jobs.read_json(path)
        value['artifacts_sha256_lf'] = {'unknown.py': 'f' * 64}
        path.write_bytes(core.encoded(value))
        with self.assertRaises(core.Stop):
            self.worker()
        self.assertEqual(self.worker_called, 0)

    def test_unit_output_is_bounded_and_duplicate_properties_fail(self):
        for raw in (b'x' * 16385, b'Id=one\nId=two\n'):
            with self.subTest(length=len(raw)), self.assertRaises(core.Stop):
                process.parse_state(raw)

    def test_child_boot_change_rejects_before_factory(self):
        self.mode = 'disconnect'
        with self.assertRaises(core.Stop):
            self.process.execute()
        (self.root / 'proc/sys/kernel/random/boot_id').write_text('00000000-0000-0000-0000-000000000000')
        with self.assertRaises(core.Stop):
            self.worker()
        self.assertEqual(self.worker_called, 0)


class BootstrapWiringTests(unittest.TestCase):
    def test_authenticated_context_uses_captured_source_loader(self):
        import hashlib,subprocess,sys,tempfile
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);code=root/'code';source=code/'scripts/phase16_bot_coordinator_process.py'
            source.parent.mkdir(parents=True)
            raw=b'def worker_entry(*args):\n print("BOUND_COORDINATOR");return 0\n'
            source.write_bytes(raw)
            context=dict(code=str(code),artifacts_sha256_lf={'scripts/phase16_bot_coordinator_process.py':hashlib.sha256(raw).hexdigest()})
            saved=root/'coordinator-context.json';saved.write_bytes(core.encoded(context))
            fake=SimpleNamespace(context=lambda:dict(maintenance_directory=str(root)),_context=context)
            argv=process.CoordinatorSupervisor.worker_argv(fake)
            result=subprocess.run([sys.executable,*argv[1:]],capture_output=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),b'BOUND_COORDINATOR')
            source.write_text('print("UNBOUND_COORDINATOR")\ndef worker_entry(*args):return 0\n')
            result=subprocess.run([sys.executable,*argv[1:]],capture_output=True,timeout=5)
            self.assertNotEqual(result.returncode,0);self.assertNotIn(b'UNBOUND_COORDINATOR',result.stdout)
            self.assertIn(b'bootstrap_hash',result.stderr)

if __name__ == '__main__':
    unittest.main()
