"""Real private journals/data artifacts; synthetic systemd boundary only."""
import contextlib
import sqlite3
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_binding as binding
from scripts import phase16_bot_maintenance_linux as linux
from tests.test_phase16_bot_maintenance_binding import observations, ownership, NOW, BOOT
from tests.test_phase16_bot_maintenance_linux import Manager

AVAILABLE = importlib.util.find_spec('scripts.phase16_bot_maintenance_jobs') is not None
if AVAILABLE:
    from scripts import phase16_bot_maintenance_jobs as jobs

class Availability(unittest.TestCase):
    def test_concrete_job_supervisor_exists(self):
        self.assertTrue(AVAILABLE, 'durable manager-owned job supervisor missing')

@unittest.skipUnless(AVAILABLE, 'implementation missing; availability fails')
class JobTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.prepared = binding.prepare_inputs(observations(), ownership(), now=NOW)
        self.manifest = self.prepared['coordinator_manifest']
        self.operation = self.manifest['operation_id']
        self.directory = self.root / self.prepared['target_contract']['maintenance_directory'].lstrip('/')
        self.directory.mkdir(parents=True)
        self.journal = core.Journal.create(self.directory / 'journal', self.manifest)
        self.context = dict(prepared=self.prepared, artifacts_sha256_lf={})
        core.write_new(self.directory / 'worker-context.json', core.encoded(self.context))
        boot = self.root / 'proc/sys/kernel/random/boot_id'
        boot.parent.mkdir(parents=True); boot.write_text(BOOT + '\n')
        self.manager = Manager()
        self.clock = [0.0]
        self.request_count = 0
        self.launch_failure = False
        self.make_result = True
        self.tamper_invocation = False
        self.active_job = False
        self.actual_data = None
        self.drop_fence_at_launch = False
        self.job_overrides = {}
        self.after_worker = lambda: None
        self.lease_seconds = 1800
        self.client = linux.SystemdClient(self.command, root=self.root,
            clock=lambda: self.clock[0], sleep=self.sleep)
        self.fence = core.SystemdFence(self.root, self.manifest, self.client.control)
        self.journal.perform('fence', lambda: self.fence.install(self.journal), lambda: True)
        for unit in (core.BOT, core.WEB):
            self.manager.properties[unit]['DropInPaths'] = '/' + self.fence.dropin(unit).relative_to(self.root).as_posix()
        self.journal.perform('stop', lambda: jobs.save_stop_witness(self.journal, self.client, self.fence), lambda: True)
        self.supervisor = jobs.DataJobSupervisor(self.journal, self.client, self.fence,
            code='/opt/phase16/code', context_sha256=core.digest(self.context),
            utc_now=lambda: binding.timestamp(ownership()['valid_until']).timestamp()-self.lease_seconds, clock=lambda: self.clock[0], sleep=self.sleep)

    def sleep(self, seconds): self.clock[0] += seconds

    def result(self, action):
        receipt = dict(schema='phase16.maintenance-data.v1', action=action,
            binding=self.journal.binding, intent_sha256=self.journal.events[-1]['sha256'],
            predecessor_sha256=None, details=dict(backup_sha256='e'*64))
        receipt['sha256'] = core.digest(receipt)
        directory = self.directory / 'receipts'; directory.mkdir(exist_ok=True)
        core.write_new(directory / (action + '.json'), core.encoded(receipt))
        jobs.save_worker_result(self.journal, action, context_sha256=core.digest(self.context),
                                invocation='b'*32, boot=BOOT)

    def command(self, argv, seconds):
        if argv[0] == 'busctl':
            unit = core.BOT if 'bot' in argv[4] else core.WEB
            condition = ['ConditionPathExists', False, False,
                         '/run/phase16/' + self.operation + '/' + unit + '.allow', 0]
            return json.dumps(dict(type='a(sbbsi)', data=[condition])).encode()
        if argv[0] == 'systemd-run':
            self.request_count += 1
            action = self.journal.phase.removesuffix('_intent')
            claim = self.directory / 'jobs' / (action + '.claim.json')
            self.assertTrue(claim.is_file(), 'claim must precede manager request')
            self.assertEqual(core.Journal.load(self.journal.directory, self.manifest).phase, action + '_intent')
            if self.launch_failure: raise core.Stop('command_failed')
            if self.drop_fence_at_launch: self.fence.dropin(core.BOT).unlink()
            if self.actual_data is not None:
                self.assertTrue(callable(getattr(jobs, 'execute_data_worker', None)), 'worker-side guard missing')
                self.active_job = True
                jobs.execute_data_worker(self.supervisor, action, self.actual_data, invocation='b'*32, pid=201)
                self.active_job = False
            elif self.make_result:
                self.result(action)
            self.after_worker()
            return b''
        if argv[:2] == ['systemctl', 'show'] and argv[-1] not in (core.BOT, core.WEB):
            value = dict(Id=argv[-1], LoadState='loaded', ActiveState='active',
                SubState='running' if self.active_job else 'exited', MainPID='201' if self.active_job else '0',
                Result='success', ExecMainCode='0' if self.active_job else '1', ExecMainStatus='0',
                InvocationID=('c' if self.tamper_invocation else 'b')*32, NRestarts='0',
                Type='exec', Restart='no', RemainAfterExit='yes', PrivateNetwork='yes',
                ProtectSystem='strict', KillMode='control-group', RuntimeMaxUSec='2min',
                TimeoutStopUSec='5s', ReadWritePaths=('/var/lib/amn2-spain' if '-migrate.' in argv[-1]
                    else self.prepared['target_contract']['maintenance_directory']))
            value.update(self.job_overrides)
            return ''.join(k+'='+v+'\n' for k,v in value.items()).encode()
        return self.manager(argv, seconds)

    def execute(self, action='backup'):
        self.journal.perform(action, lambda: self.supervisor.execute(action), lambda: True)

    def real_data(self):
        from scripts import phase16_bot_db_rehearsal as db
        from scripts.phase16_bot_maintenance_operations import DataOperations
        database = self.root / self.prepared['target_contract']['database'].lstrip('/')
        sources = db.Sources(Path(__file__).parent / 'fixtures/phase16_schema')
        with contextlib.closing(sqlite3.connect(database)) as conn:
            sources.old(conn)
            conn.execute("INSERT INTO users(telegram_id,username) VALUES(1,'private-fixture')")
            conn.commit()
        self.actual_data = DataOperations(database, self.directory, self.journal, sources, '10.8.0.0/24')

    def test_real_sqlite_backup_has_worker_and_manager_bound_receipts(self):
        self.assertTrue(callable(getattr(jobs, 'execute_data_worker', None)), 'worker-side guard missing')
        self.real_data()
        self.execute()
        self.assertTrue((self.directory / 'backup.sqlite3').is_file())
        self.assertEqual(self.journal.phase, 'backup_done')
        worker = json.loads((self.directory / 'jobs/backup.result.json').read_text())
        data = json.loads((self.directory / 'receipts/backup.json').read_text())
        self.assertEqual(worker['data_receipt_sha256'], data['sha256'])

    def test_worker_checks_fence_again_after_dispatch_before_backup_content_read(self):
        self.real_data(); self.drop_fence_at_launch = True
        with self.assertRaisesRegex(core.Stop, 'fence_lost'): self.execute()
        self.assertFalse((self.directory / 'backup.sqlite3').exists())
        self.assertEqual(self.journal.phase, 'backup_intent')

    def test_real_three_job_pipeline_preserves_backup_business_rows_and_receipt_chain(self):
        from scripts import phase16_bot_db_rehearsal as db
        self.real_data()
        original = db.file_sha256(self.actual_data.database)
        for action in ('backup', 'rehearsal'):
            self.execute(action)
        self.assertEqual(db.file_sha256(self.actual_data.database), original)
        backup = db.file_sha256(self.directory / 'backup.sqlite3')
        self.execute('migrate')
        self.assertEqual(self.journal.phase, 'migrate_done')
        self.assertEqual(self.request_count, 3)
        self.assertEqual(db.file_sha256(self.directory / 'backup.sqlite3'), backup)
        with contextlib.closing(sqlite3.connect(self.actual_data.database)) as conn:
            self.assertEqual(db.shape(conn), self.actual_data.sources.candidate_shape)
            self.assertEqual(conn.execute('SELECT username FROM users').fetchall(), [('private-fixture',)])
            self.assertEqual(conn.execute('SELECT issuance_enabled FROM awg3_control_state').fetchall(), [(0,)])
        records = [p.read_text() for p in (self.directory / 'jobs').glob('*.json')]
        self.assertEqual(len(records), 9)
        self.assertNotIn('private-fixture', ''.join(records))
        previous = None
        for action in ('backup', 'rehearsal', 'migrate'):
            data = jobs.load_signed(self.directory / 'receipts' / (action + '.json'))
            self.assertEqual(data['predecessor_sha256'], previous)
            previous = data['sha256']

    def test_worker_rejects_another_process_before_reading_database(self):
        self.real_data(); self.job_overrides['MainPID'] = '202'
        with self.assertRaisesRegex(core.Stop, 'worker_identity'): self.execute()
        self.assertFalse((self.directory / 'backup.sqlite3').exists())
        self.assertEqual(self.journal.phase, 'backup_intent')

    def test_worker_rejects_missing_network_isolation_property(self):
        self.real_data(); self.job_overrides['PrivateNetwork'] = 'no'
        with self.assertRaisesRegex(core.Stop, 'job_policy'): self.execute()
        self.assertFalse((self.directory / 'backup.sqlite3').exists())

    def test_unit_change_after_worker_result_prevents_parent_acceptance(self):
        def change(): self.manager.properties[core.WEB]['NRestarts'] = '1'
        self.after_worker = change
        with self.assertRaisesRegex(core.Stop, 'stop_witness_changed'): self.execute()
        self.assertTrue((self.directory / 'jobs/backup.result.json').exists())
        self.assertFalse((self.directory / 'jobs/backup.complete.json').exists())

    def test_rehashed_data_receipt_change_does_not_match_worker_result(self):
        def change():
            path = self.directory / 'receipts/backup.json'
            data = json.loads(path.read_text())
            data['details']['backup_sha256'] = 'f'*64
            data['sha256'] = core.digest({k: v for k, v in data.items() if k != 'sha256'})
            path.write_bytes(core.encoded(data))
        self.after_worker = change
        with self.assertRaisesRegex(core.Stop, 'job_result_binding'): self.execute()
        self.assertFalse((self.directory / 'jobs/backup.complete.json').exists())

    def test_complete_receipt_and_invocation_advance_journal(self):
        self.execute()
        self.assertEqual(self.journal.phase, 'backup_done')
        self.assertEqual(self.request_count, 1)
        self.assertTrue((self.directory / 'jobs/backup.complete.json').exists())
        self.assertTrue(self.fence.present())

    def test_lost_launch_ack_leaves_one_attempt_and_never_replays(self):
        self.launch_failure = True
        with self.assertRaises(core.Stop): self.execute()
        self.assertEqual(self.journal.phase, 'backup_intent')
        self.assertTrue((self.directory / 'jobs/backup.claim.json').exists())
        with self.assertRaises(core.Stop): self.execute()
        self.assertEqual(self.request_count, 1)
        self.assertTrue(self.fence.present())

    def test_exit_zero_without_result_or_wrong_invocation_is_not_success(self):
        self.make_result = False
        with self.assertRaises(core.Stop): self.execute()
        self.assertEqual(self.journal.phase, 'backup_intent')
        self.assertFalse((self.directory / 'jobs/backup.complete.json').exists())

    def test_old_result_from_another_invocation_is_rejected(self):
        self.tamper_invocation = True
        with self.assertRaisesRegex(core.Stop, 'job_result_binding'): self.execute()
        self.assertEqual(self.journal.phase, 'backup_intent')

    def test_new_systemd_state_after_witness_stops_before_job(self):
        self.manager.properties[core.BOT]['StateChangeTimestampMonotonic'] = '101'
        with self.assertRaisesRegex(core.Stop, 'stop_witness_changed'): self.execute()
        self.assertEqual(self.request_count, 0)

    def test_lost_fence_stops_before_job(self):
        self.fence.dropin(core.BOT).write_text('foreign')
        with self.assertRaisesRegex(core.Stop, 'fence_lost'): self.execute()
        self.assertEqual(self.request_count, 0)

    def test_changed_boot_stops_before_job(self):
        (self.root / 'proc/sys/kernel/random/boot_id').write_text('a'*36)
        with self.assertRaisesRegex(core.Stop, 'boot_changed'): self.execute()
        self.assertEqual(self.request_count, 0)

    def test_unknown_drain_is_never_promoted_by_stop_witness(self):
        value = json.loads((self.directory / 'stop-witness.json').read_text())
        self.assertEqual(value['business_drain'], 'NOT_ESTABLISHED')
        self.assertFalse(value['live_authorized'])

    def test_context_tamper_or_insufficient_recovery_reserve_prevents_job(self):
        self.lease_seconds = 439
        with self.assertRaisesRegex(core.Stop, 'ownership_window'): self.execute()
        self.assertEqual(self.request_count, 0)

    def test_context_tamper_prevents_job(self):
        path = self.directory / 'worker-context.json'
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaisesRegex(core.Stop, 'job_context_binding'): self.execute()
        self.assertEqual(self.request_count, 0)

    def test_deadline_retains_running_job_and_does_not_kill_or_start_another(self):
        self.active_job = True; self.make_result = False
        with self.assertRaisesRegex(core.Stop, 'job_unknown_no_retry'): self.execute()
        self.assertEqual(self.request_count, 1)
        self.assertEqual(self.journal.phase, 'backup_intent')
        self.assertTrue(self.fence.present())
        self.assertFalse(any('kill' in call[0] or 'stop' in call[0] for call in self.manager.calls))

if __name__=='__main__': unittest.main()
