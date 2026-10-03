"""Real durable files and portable Unix syscall model for future permission apply."""
from contextlib import contextmanager
from dataclasses import asdict, replace
import importlib
import json
import io
import os
from pathlib import Path
import stat
import tempfile
import unittest

from scripts import phase16_bot_stage_access as access
from scripts.vps.phase16_bot_retained_stage_remote import fingerprint
from tests import test_phase16_bot_stage_access as access_tests

try:
    apply = importlib.import_module('scripts.phase16_bot_stage_access_apply')
except ModuleNotFoundError as error:
    if error.name != 'scripts.phase16_bot_stage_access_apply':
        raise
    apply = None

BOOT = '11111111-2222-3333-4444-555555555555'


class PortableJournal:
    """Production durable-write primitive with temporary Windows-safe opens."""
    def __init__(self, root, events):
        self.root, self.events, self.fail = root, events, None

    def create(self, name, data):
        if self.fail == name:
            raise OSError('journal failure secret detail')
        path = self.root / name
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            apply.write_all_fsync(fd, data)
        finally:
            os.close(fd)
        self.events.append(('journal', name))


def model_factory(fixture, events, hook=None):
    class ModelOS:
        O_RDONLY, O_NOFOLLOW, O_NONBLOCK, O_CLOEXEC, O_DIRECTORY = 0, 1, 2, 4, 8
        def __init__(self):
            self.handles = {1: ('.', None)}
            self.counter = 1

        def open(self, leaf, flags, dir_fd=None):
            parent = self.handles[dir_fd][0]
            name = leaf if parent == '.' else parent + '/' + leaf
            self.counter += 1
            path = fixture.root / name
            stream = None if path.is_dir() else io.BytesIO(path.read_bytes())
            if stream is not None:
                stream.opened_inode = path.stat().st_ino
                stream.opened_device = path.stat().st_dev
            self.handles[self.counter] = (name, stream)
            if hook:
                hook('open', name)
            return self.counter

        def dup(self, fd):
            self.counter += 1
            self.handles[self.counter] = self.handles[fd]
            return self.counter

        def close(self, fd):
            name, stream = self.handles.pop(fd)
            if stream:
                stream.close()

        def fstat(self, fd):
            name, stream = self.handles[fd]
            value = fixture.reader().info(name)
            if stream:
                value.st_ino, value.st_dev = stream.opened_inode, stream.opened_device
            return value

        def stat(self, leaf, dir_fd=None, follow_symlinks=False):
            if dir_fd is None:
                return fixture.reader().info('.')
            parent = self.handles[dir_fd][0]
            return fixture.reader().info(leaf if parent == '.' else parent + '/' + leaf)

        def listxattr(self, fd):
            return fixture.reader().acl_names(self.handles[fd][0])

        def lseek(self, fd, offset, whence):
            stream = self.handles[fd][1]
            return stream.seek(offset, whence)

        def read(self, fd, maximum):
            return self.handles[fd][1].read(maximum)

        def fchown(self, fd, uid, gid):
            name, _ = self.handles[fd]
            assert uid == 0
            assert name not in fixture.links
            meta = fixture.reader().info(name)
            fixture.attributes[name] = (stat.S_IMODE(meta.st_mode), uid, gid)
            events.append(('chown', name))
            if hook:
                hook('chown', name)

        def fchmod(self, fd, mode):
            name, _ = self.handles[fd]
            assert name not in fixture.links
            meta = fixture.reader().info(name)
            fixture.attributes[name] = (mode, 0, meta.st_gid)
            events.append(('chmod', name))
            if hook:
                hook('chmod', name)

        def fsync(self, fd):
            if hook:
                hook('fsync', self.handles[fd][0])

    class ModelSession(apply.UnixApplySession):
        def __init__(self):
            self.os = ModelOS()
            self.root_fd = 1
            self.snapshots = {}
            self.root = Path(access.STAGE_ROOT)
            self.chain = [(1, None, '.', fixture.reader().info('.'))]

        def __enter__(self):
            return self

        def __exit__(self, kind, error, traceback):
            if kind is None:
                self.stable()
            return False

        def info(self, name):
            meta = fixture.reader().info(name)
            before = self.snapshots.setdefault(name, fingerprint(meta))
            if before != fingerprint(meta):
                raise apply.ApplyError('unexpected_metadata_change')
            return meta

        def entries(self, name):
            self.info(name)
            return fixture.reader().entries(name)

        def read_file(self, name, maximum, expected_size=None):
            self.info(name)
            return fixture.reader().read_file(name, maximum, expected_size)

        def acl_names(self, name):
            return fixture.reader().acl_names(name)

        def readlink(self, name):
            self.info(name)
            return fixture.reader().readlink(name)

        def ancestors(self):
            return fixture.reader().ancestors()

        @contextmanager
        def parent_fd(self, name):
            parent, _, leaf = name.rpartition('/')
            self.os.counter += 1
            fd = self.os.counter
            self.os.handles[fd] = (parent or '.', None)
            try:
                yield fd, leaf or name
            finally:
                self.os.close(fd)

        def check_chain(self):
            for fd, _, _, before in self.chain:
                if fingerprint(before) != fingerprint(self.os.fstat(fd)):
                    raise apply.ApplyError('unexpected_chain_change')

        def stable(self):
            for name, value in self.snapshots.items():
                if value != fingerprint(fixture.reader().info(name)):
                    raise apply.ApplyError('unexpected_metadata_change')
            self.check_chain()

    return ModelSession


class StageAccessApplyTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(apply, 'stage-access apply library is missing')
        self.fixture = access_tests.StageAccessTests(methodName='runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.plan = self.fixture.build()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.events = []
        self.journal = PortableJournal(Path(self.temp.name), self.events)
        self.binding = apply.ApplyBinding('access-operation-001', 'a' * 64, BOOT, 'b' * 64, self.plan.digest)

    def run_apply(self, *, hook=None, boot=None, binding=None, plan=None):
        return apply.execute(plan or self.plan, binding or self.binding, journal=self.journal,
                             session_factory=model_factory(self.fixture, self.events, hook),
                             boot_id_reader=boot or (lambda: BOOT))

    def test_durable_intent_precedes_mutations_and_stage_traverse_is_last(self):
        result = self.run_apply()
        self.assertEqual(result.status, 'APPLIED_DAC_VERIFIED_NOT_HOST_ADMITTED')
        mutation_indexes = [i for i, event in enumerate(self.events) if event[0] in ('chmod', 'chown')]
        intent_index = next(i for i, event in enumerate(self.events) if event[0] == 'journal' and '.intent.' in event[1])
        self.assertLess(intent_index, min(mutation_indexes))
        self.assertEqual(self.events[max(mutation_indexes)][1], '.')
        self.assertFalse(any(event[1] in self.fixture.links for event in self.events if event[0] in ('chmod', 'chown')))
        self.assertEqual(access.verify_access(self.plan, self.fixture.reader()).status, 'DAC_ACCESS_VERIFIED_NOT_HOST_ADMITTED')

    def test_private_wrappers_are_sealed_before_any_service_group_grant(self):
        self.run_apply()
        mutations = [event for event in self.events if event[0] in ('chmod', 'chown')]
        seals = [i for i, event in enumerate(mutations) if event[0] == 'chmod' and event[1].startswith('runtime-venv/bin/')]
        first_grant = next(i for i, event in enumerate(mutations) if event[0] == 'chown' and event[1] == 'source/app/main.py')
        self.assertLess(max(seals), first_grant)

    def test_wrong_authorized_plan_digest_has_no_claim_or_mutation(self):
        result = self.run_apply(binding=replace(self.binding, authorized_plan_sha256='f' * 64))
        self.assertEqual(result.status, 'STOP_BEFORE_CLAIM')
        self.assertEqual(self.events, [])

    def test_existing_claim_prevents_replay_even_after_success(self):
        self.run_apply()
        before = list(self.events)
        result = self.run_apply()
        self.assertEqual(result.reason, 'claim_exists')
        self.assertEqual(self.events, before)

    def test_intent_failure_performs_no_stage_change_and_retains_claim(self):
        self.journal.fail = apply.journal_name(self.binding, 'intent')
        result = self.run_apply()
        self.assertEqual(result.status, 'STOP_RETAINED_NO_RETRY')
        self.assertFalse(any(event[0] in ('chmod', 'chown') for event in self.events))
        self.assertTrue((self.journal.root / apply.journal_name(self.binding, 'claim')).exists())

    def test_changed_bytes_or_acl_fail_full_preimage_before_intent(self):
        self.fixture.write('source/app/main.py', b'VALUE = 9\n')
        result = self.run_apply()
        self.assertEqual(result.reason, 'preimage_content')
        self.assertFalse(any('.intent.' in event[1] for event in self.events))
        self.assertFalse(any(event[0] in ('chmod', 'chown') for event in self.events))

    def test_acl_unknown_stops_before_any_change(self):
        self.fixture.acls['source/app/main.py'] = None
        result = self.run_apply()
        self.assertEqual(result.reason, 'acl_not_clear')
        self.assertFalse(any(event[0] in ('chmod', 'chown') for event in self.events))

    def test_partial_syscall_failure_retains_intent_without_restore(self):
        def fail(event, name):
            if event == 'chown' and name == 'source/app/main.py':
                raise OSError('simulated failure after syscall')
        result = self.run_apply(hook=fail)
        self.assertEqual(result.status, 'STOP_RETAINED_NO_RETRY')
        self.assertTrue((self.journal.root / apply.journal_name(self.binding, 'intent')).exists())
        self.assertEqual(self.fixture.attributes['source/app/main.py'][2], 1001)
        self.assertEqual(self.fixture.reader().info('.').st_mode & 0o777, 0o700)
        self.assertNotIn('simulated', repr(result))

    def test_process_interrupt_leaves_claim_and_intent_without_result(self):
        def interrupt(event, name):
            if event == 'chmod':
                raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            self.run_apply(hook=interrupt)
        self.assertTrue((self.journal.root / apply.journal_name(self.binding, 'intent')).exists())
        self.assertFalse((self.journal.root / apply.journal_name(self.binding, 'result')).exists())

    def test_fd_identity_race_stops_before_mutating_replacement(self):
        fired = False
        def race(event, name):
            nonlocal fired
            if event == 'open' and name == 'source/app/main.py' and not fired:
                fired = True
                path = self.fixture.root / name
                path.rename(path.with_suffix('.old'))
                path.write_bytes(b'VALUE = 7\n')
        result = self.run_apply(hook=race)
        self.assertEqual(result.status, 'STOP_RETAINED_NO_RETRY')
        self.assertFalse(any(event == ('chown', 'source/app/main.py') for event in self.events))

    def test_external_content_change_after_chown_is_not_rebased(self):
        def change(event, name):
            if event == 'chown' and name == 'source/app/main.py':
                self.fixture.write(name, b'VALUE = 9\n')
        result = self.run_apply(hook=change)
        self.assertEqual(result.status, 'STOP_RETAINED_NO_RETRY')
        self.assertFalse(any(event == ('chmod', 'source/app/main.py') for event in self.events))

    def test_boot_change_during_apply_stops_before_stage_opening(self):
        def boot():
            return '99999999-2222-3333-4444-555555555555' if any(e[0] == 'chmod' for e in self.events) else BOOT
        result = self.run_apply(boot=boot)
        self.assertEqual(result.reason, 'boot_binding')
        self.assertEqual(self.fixture.reader().info('.').st_mode & 0o777, 0o700)

    def test_result_persist_failure_never_returns_success(self):
        self.journal.fail = apply.journal_name(self.binding, 'result')
        result = self.run_apply()
        self.assertEqual(result.status, 'RESULT_UNPERSISTED_NO_RETRY')
        self.assertTrue((self.journal.root / apply.journal_name(self.binding, 'intent')).exists())

    def test_path_escape_and_symlink_mutation_are_rejected_even_if_rehashed(self):
        original = next(item for item in self.plan.objects if item.path == 'source/app/main.py')
        for malicious in (replace(original, path='../outside'), replace(original, path='/tmp/outside'),
                          replace(original, kind='symlink', link_target='/tmp/outside')):
            with self.subTest(path=malicious.path, kind=malicious.kind):
                objects = tuple(malicious if item.path == original.path else item for item in self.plan.objects)
                changed = replace(self.plan, objects=objects, digest='')
                changed = replace(changed, digest=access._digest(changed))
                binding = replace(self.binding, authorized_plan_sha256=changed.digest)
                result = self.run_apply(plan=changed, binding=binding)
                self.assertEqual(result.status, 'STOP_BEFORE_CLAIM')
        self.assertEqual(self.events, [])

    def test_plan_larger_than_16k_is_durably_bound(self):
        for index in range(50):
            name = f'app/module_{index}.py'
            self.fixture.write('source/' + name, b'VALUE = 7\n')
            self.fixture.source_pins[name] = (10, __import__('hashlib').sha256(b'VALUE = 7\n').hexdigest())
        self.plan = self.fixture.build()
        self.binding = replace(self.binding, authorized_plan_sha256=self.plan.digest)
        result = self.run_apply()
        self.assertEqual(result.status, 'APPLIED_DAC_VERIFIED_NOT_HOST_ADMITTED')
        saved = self.journal.root / apply.journal_name(self.binding, 'plan')
        self.assertGreater(saved.stat().st_size, 16384)
        self.assertLessEqual(saved.stat().st_size, 2 * 1024 * 1024)
        self.assertEqual(json.loads(saved.read_bytes())['plan']['digest'], self.plan.digest)


    def test_preserved_interpreter_escape_is_rejected_even_when_bound(self):
        path = 'runtime-venv/bin/python3'
        self.fixture.links[path] = '/tmp/untrusted-python'
        objects = tuple(replace(item, link_target='/tmp/untrusted-python') if item.path == path else item for item in self.plan.objects)
        plan = replace(self.plan, objects=objects, digest='')
        plan = replace(plan, digest=access._digest(plan))
        binding = replace(self.binding, authorized_plan_sha256=plan.digest)
        result = self.run_apply(plan=plan, binding=binding)
        self.assertEqual(result.status, 'STOP_BEFORE_CLAIM')
        self.assertEqual(self.events, [])

    def test_private_wrapper_size_change_invalidates_original_preimage(self):
        self.fixture.write('runtime-venv/bin/demo', b'changed wrapper with another size')
        result = self.run_apply()
        self.assertEqual(result.reason, 'preimage_identity')
        self.assertFalse(any(event[0] in ('chmod', 'chown') for event in self.events))


    def test_change_during_intent_fsync_is_caught_before_first_mutation(self):
        original = self.journal.create
        def create(name, data):
            original(name, data)
            if '.intent.' in name:
                self.fixture.write('source/app/main.py', b'VALUE = 9\n')
        self.journal.create = create
        result = self.run_apply()
        self.assertEqual(result.status, 'STOP_RETAINED_NO_RETRY')
        self.assertFalse(any(event[0] in ('chown', 'chmod') for event in self.events))

    def test_exclusive_durable_writer_handles_partial_writes(self):
        filename = self.journal.root / 'partial-write.bin'
        body = b'exact durable bytes' * 300
        class PartialFS:
            def write(self, fd, data):
                return os.write(fd, data[:7])
            def fsync(self, fd):
                return os.fsync(fd)
        fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            apply.write_all_fsync(fd, body, fs=PartialFS())
        finally:
            os.close(fd)
        self.assertEqual(filename.read_bytes(), body)

    def test_oversized_journal_payload_is_rejected(self):
        with self.assertRaisesRegex(apply.ApplyError, 'journal_size'):
            apply.encoded({'value': 'x' * (2 * 1024 * 1024)})


if __name__ == '__main__':
    unittest.main()
