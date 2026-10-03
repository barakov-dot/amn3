"""Actual filesystem metadata and fake procfs; no DB content or real host scan."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import phase16_bot_maintenance as core
from tests.test_phase16_bot_maintenance_binding import BOOT, NOW, OP, TARGET

AVAILABLE = importlib.util.find_spec('scripts.phase16_bot_writer_admission') is not None
if AVAILABLE:
    from scripts import phase16_bot_writer_admission as writers


class Availability(unittest.TestCase):
    def test_writer_collector_exists(self):
        self.assertTrue(AVAILABLE, 'actual application writer admission collector missing')


@unittest.skipUnless(AVAILABLE, 'availability fails first')
class WriterTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.proc = self.root / 'proc'
        self.proc.mkdir()
        boot = self.proc / 'sys/kernel/random/boot_id'
        boot.parent.mkdir(parents=True)
        boot.write_bytes((BOOT + '\n').encode())
        self.database = self.root / 'var/lib/amn2-spain/amn2.sqlite3'
        self.database.parent.mkdir(parents=True)
        self.database.write_bytes(b'PRIVATE DATABASE CONTENT MUST NOT BE READ')
        for suffix in ('-wal', '-shm', '-journal'):
            Path(str(self.database) + suffix).write_bytes(b'PRIVATE SIDECAR')
        self.elapsed = 0
        self.units = {}
        for pid, unit in ((101, core.BOT), (102, core.WEB)):
            cgroup = '/system.slice/' + unit
            self.make_process(pid, cgroup)
            self.units[unit] = dict(Id=unit, LoadState='loaded', ActiveState='active', SubState='running',
                MainPID=str(pid), InvocationID=('a' if pid == 101 else 'b') * 32, ControlGroup=cgroup)
        self.fd(101, 3, self.database)
        self.fd(102, 4, Path(str(self.database) + '-wal'))
        self.declaration = dict(schema='phase16.application-writer-declaration.v1', operation_id=OP,
            boot_id=BOOT, target_binding_sha256=TARGET, approval_scope_sha256='c' * 64,
            declared_at=NOW, valid_until='2026-09-30T12:30:00+00:00',
            accepted_within_maintenance_approval=True, application_inventory_complete=True,
            writers=[dict(unit=core.BOT, role='bot'), dict(unit=core.WEB, role='web')],
            other_application_writers=dict(cron='absent', agent='absent', timer='absent', socket='absent', manual_cli='paused'),
            external_application_pollers='excluded', trust_boundary='EXISTING_OS_AND_ROOT_OPERATOR',
            scope='APPLICATION_ONLY')
        self.calls = []

    def make_process(self, pid, cgroup, *, thread=None):
        process = self.proc / str(pid)
        process.mkdir(exist_ok=True)
        self.identity_files(process, pid, cgroup)
        task = process / 'task' / str(pid if thread is None else thread)
        task.mkdir(parents=True, exist_ok=True)
        self.identity_files(task, pid if thread is None else thread, cgroup)
        (task / 'fd').mkdir(exist_ok=True)
        (task / 'maps').write_bytes(b'1000-2000 rw-p 00000000 00:00 0 [heap]\n')
        return task

    def identity_files(self, directory, pid, cgroup):
        fields = ['S'] + ['0'] * 18 + [str(pid * 11)] + ['0'] * 4
        (directory / 'stat').write_bytes((str(pid) + ' (private process title) ' + ' '.join(fields)).encode())
        (directory / 'cgroup').write_bytes(('0::' + cgroup + '\n').encode())

    def fd(self, pid, number, target, *, thread=None):
        task = self.proc / str(pid) / 'task' / str(pid if thread is None else thread)
        os.link(target, task / 'fd' / str(number))

    def mapping(self, pid, target, *, thread=None):
        metadata = target.stat()
        # Windows supplies a synthetic dev_t; Linux's bit layout is documented.
        major = (metadata.st_dev >> 8) & 0xfff | (metadata.st_dev >> 32) & 0xfffff000
        minor = metadata.st_dev & 0xff | (metadata.st_dev >> 12) & 0xffffff00
        line = f'1000-2000 rw-s 00000000 {major:x}:{minor:x} {metadata.st_ino} /PRIVATE/path (deleted)\n'
        task = self.proc / str(pid) / 'task' / str(pid if thread is None else thread)
        (task / 'maps').write_bytes(line.encode())

    def unit_reader(self, unit, seconds):
        self.assertIn(unit, (core.BOT, core.WEB))
        self.assertTrue(0 < seconds <= 5)
        self.calls.append(unit)
        return dict(self.units[unit])

    def collect(self, **override):
        args = dict(operation_id=OP, boot_id=BOOT, target_binding_sha256=TARGET,
            approval_scope_sha256='c' * 64, root=self.root, unit_reader=self.unit_reader,
            utc_now=lambda: 1790769600.0, clock=lambda: self.elapsed)
        args.update(override)
        return writers.collect_writer_admission(self.declaration, **args)

    def test_declared_bot_web_and_kernel_holders_produce_bound_inventory(self):
        result = self.collect()
        self.assertEqual(result['inventory']['writers'], [dict(unit=core.BOT, role='bot'), dict(unit=core.WEB, role='web')])
        self.assertEqual(result['inventory']['other_writer_classes'], dict.fromkeys(('cron', 'agent', 'socket', 'timer'), 'absent_verified'))
        self.assertEqual(result['inventory']['process_scan'], 'complete_bot_web_only')
        self.assertEqual(result['inventory']['scan_sha256'], core.digest(result['evidence']))
        self.assertEqual(result['evidence']['basis'], 'OWNER_DECLARATION_AND_KERNEL_HOLDERS')
        self.assertEqual(result['evidence']['trust_boundary'], 'EXISTING_OS_AND_ROOT_OPERATOR_NOT_AUDITED')
        self.assertEqual(result['evidence']['holder_processes'], {'bot': 1, 'web': 1})
        self.assertEqual(result['evidence']['declaration_sha256'], core.digest(self.declaration))
        self.assertEqual(self.calls, [core.BOT, core.WEB, core.BOT, core.WEB])
        self.assertFalse(result['authorized'])
        text = json.dumps(result)
        for secret in ('PRIVATE', 'private process title', str(self.root)):
            self.assertNotIn(secret, text)

    def test_sole_ssh_owner_answer_is_not_application_inventory(self):
        self.declaration = {'sole_ssh_access': True}
        with self.assertRaises(core.Stop):
            self.collect()
        self.assertEqual(self.calls, [])

    def test_declared_unknown_or_extra_writer_classes_stop_before_scan(self):
        for key in ('cron', 'agent', 'timer', 'socket', 'manual_cli'):
            with self.subTest(key=key):
                declaration = copy.deepcopy(self.declaration)
                declaration['other_application_writers'][key] = 'unknown'
                with self.assertRaises(core.Stop):
                    writers.validate_declaration(declaration, operation_id=OP, boot_id=BOOT,
                        target_binding_sha256=TARGET, approval_scope_sha256='c' * 64, now=1790769600.0)

    def test_operation_boot_target_approval_and_expiry_are_required(self):
        changes = dict(operation_id='phase16-wrong', boot_id='00000000-0000-0000-0000-000000000000',
            target_binding_sha256='0' * 64, approval_scope_sha256='0' * 64,
            valid_until='2026-09-30T11:59:59+00:00', application_inventory_complete=False,
            accepted_within_maintenance_approval=False, external_application_pollers='unknown')
        for key, value in changes.items():
            with self.subTest(key=key):
                original = self.declaration[key]
                self.declaration[key] = value
                with self.assertRaises(core.Stop):
                    self.collect()
                self.declaration[key] = original
        self.assertEqual(self.calls, [])

    def test_unknown_fd_holder_stops_without_emitting_identity_or_path(self):
        self.make_process(201, '/system.slice/unrelated.service')
        self.fd(201, 7, self.database)
        with self.assertRaisesRegex(core.Stop, '^writer_unknown_holder$'):
            self.collect()

    def test_maps_only_holder_of_each_database_sidecar_is_detected(self):
        self.make_process(201, '/system.slice/unrelated.service')
        for suffix in ('', '-wal', '-shm', '-journal'):
            with self.subTest(suffix=suffix):
                self.mapping(201, Path(str(self.database) + suffix))
                with self.assertRaisesRegex(core.Stop, '^writer_unknown_holder$'):
                    self.collect()

    def test_known_cgroup_child_holder_has_continuous_identity(self):
        self.make_process(201, '/system.slice/' + core.BOT + '/worker')
        self.mapping(201, Path(str(self.database) + '-journal'))
        result = self.collect()
        self.assertEqual(result['evidence']['holder_processes'], {'bot': 2, 'web': 1})
        self.assertIn('rollback_journal', result['evidence']['files_seen']['bot'])

    def test_cgroup_prefix_lookalike_is_not_known_application(self):
        self.make_process(201, '/system.slice/' + core.BOT + '-foreign')
        self.fd(201, 1, self.database)
        with self.assertRaisesRegex(core.Stop, '^writer_unknown_holder$'):
            self.collect()

    def test_thread_local_fd_table_is_scanned(self):
        self.make_process(201, '/system.slice/unrelated.service')
        self.make_process(201, '/system.slice/unrelated.service', thread=202)
        self.fd(201, 7, self.database, thread=202)
        with self.assertRaisesRegex(core.Stop, '^writer_unknown_holder$'):
            self.collect()

    def test_unrelated_nonholder_process_is_not_os_service_audit(self):
        self.make_process(201, '/system.slice/trusted-os.service')
        result = self.collect()
        self.assertEqual(result['evidence']['processes_seen'], 3)
        self.assertEqual(result['evidence']['holder_processes'], {'bot': 1, 'web': 1})
        self.assertNotIn('trusted-os', json.dumps(result))

    def test_unit_invocation_churn_stops(self):
        original = self.unit_reader
        def reader(unit, seconds):
            if len(self.calls) >= 2:
                self.units[unit]['InvocationID'] = 'f' * 32
            return original(unit, seconds)
        with self.assertRaisesRegex(core.Stop, '^writer_unit_changed$'):
            self.collect(unit_reader=reader)

    def test_unit_main_pid_cgroup_mismatch_stops(self):
        self.identity_files(self.proc / '101', 101, '/system.slice/unrelated.service')
        with self.assertRaises(core.Stop):
            self.collect()

    def test_inaccessible_maps_fail_closed_without_raw_exception(self):
        original = Path.open
        def denied(path, *args, **kwargs):
            if path.name == 'maps':
                raise PermissionError('PRIVATE token in arbitrary exception')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'open', denied), self.assertRaisesRegex(core.Stop, '^writer_incomplete$'):
            self.collect()

    def test_missing_maps_or_thread_directory_never_means_absence(self):
        (self.proc / '102/task/102/maps').unlink()
        with self.assertRaisesRegex(core.Stop, '^writer_incomplete$'):
            self.collect()

    def test_budget_expiry_stops_without_inventory(self):
        original = self.unit_reader
        def slow(unit, seconds):
            self.elapsed += 6
            return original(unit, seconds)
        with self.assertRaisesRegex(core.Stop, '^writer_deadline$'):
            self.collect(unit_reader=slow)

    def test_target_inode_replacement_is_detected(self):
        original = writers.ProcFilesystem.database_identities
        calls = [0]
        def changed(view):
            calls[0] += 1
            if calls[0] == 2:
                self.database.unlink()
                self.database.write_bytes(b'NEW PRIVATE DB')
            return original(view)
        with patch.object(writers.ProcFilesystem, 'database_identities', changed), self.assertRaisesRegex(core.Stop, '^writer_database_changed$'):
            self.collect()

    def test_pid_start_ticks_churn_is_detected(self):
        original = writers.ProcFilesystem.process_identity
        calls = [0]
        def changed(view, pid, tid=None):
            result = original(view, pid, tid)
            if pid == 101 and tid is None:
                calls[0] += 1
                if calls[0] > 1:
                    result = dict(result, start_ticks=result['start_ticks'] + 1)
            return result
        with patch.object(writers.ProcFilesystem, 'process_identity', changed), self.assertRaisesRegex(core.Stop, '^writer_process_changed$'):
            self.collect()

    def test_pid_list_churn_and_caps_are_stop_conditions(self):
        original = writers.ProcFilesystem.pids
        calls = [0]
        def changed(view):
            result = original(view)
            calls[0] += 1
            return result + ([999] if calls[0] > 1 else [])
        with patch.object(writers.ProcFilesystem, 'pids', changed), self.assertRaisesRegex(core.Stop, '^writer_process_changed$'):
            self.collect()
        with self.assertRaisesRegex(core.Stop, '^writer_limit$'):
            self.collect(limits=writers.Limits(processes=1))

    def test_declaration_mutation_cannot_retain_another_declaration_hash(self):
        original = writers.validate_declaration
        calls = [0]
        def changed(value, **kwargs):
            digest = original(value, **kwargs)
            calls[0] += 1
            if calls[0] == 1:
                value['declared_at'] = '2026-09-30T11:59:00+00:00'
            return digest
        with patch.object(writers, 'validate_declaration', changed), self.assertRaises(core.Stop):
            self.collect()

    def test_database_fd_env_and_cmdline_content_are_never_opened(self):
        original = Path.open
        def restricted(path, *args, **kwargs):
            self.assertIn(path.name, ('stat', 'cgroup', 'maps', 'boot_id'))
            return original(path, *args, **kwargs)
        with patch.object(Path, 'open', restricted):
            self.assertEqual(self.collect()['evidence']['holder_processes'], {'bot': 1, 'web': 1})

    def test_fd_and_mapping_churn_stop_complete_inventory(self):
        for method in ('fd_snapshot', 'maps_snapshot'):
            original = getattr(writers.ProcFilesystem, method)
            calls = [0]
            def changed(view, pid, tid):
                result = original(view, pid, tid)
                calls[0] += 1
                return result + ((999,),) if calls[0] == 2 else result
            with self.subTest(method=method), patch.object(writers.ProcFilesystem, method, changed):
                with self.assertRaisesRegex(core.Stop, '^writer_process_changed$'):
                    self.collect()

    def test_boot_and_task_cgroup_change_stop_complete_inventory(self):
        original = writers.ProcFilesystem.process_identity
        calls = [0]
        def changed(view, pid, tid=None):
            result = original(view, pid, tid)
            if tid == 101:
                calls[0] += 1
                if calls[0] > 1:
                    result = dict(result, cgroup='/system.slice/another.service')
            return result
        with patch.object(writers.ProcFilesystem, 'process_identity', changed), self.assertRaisesRegex(core.Stop, '^writer_process_changed$'):
            self.collect()
        (self.proc / 'sys/kernel/random/boot_id').write_bytes(b'00000000-0000-0000-0000-000000000000\n')
        with self.assertRaisesRegex(core.Stop, '^writer_boot_changed$'):
            self.collect()

    def test_maps_parser_uses_inode_and_device_not_private_path_text(self):
        raw = b'1000-2000 rw-s 00000000 08:01 123 /PRIVATE/name (deleted)\n'
        self.assertEqual(writers.parse_maps(raw), ((4096, 8192, 'rw-s', 0, 8, 1, 123),))
        for raw in (b'PRIVATE malformed\n', b'1000-2000 rw-s 0 zz:01 123 secret\n'):
            with self.assertRaises(core.Stop):
                writers.parse_maps(raw)


if __name__ == '__main__':
    unittest.main()
