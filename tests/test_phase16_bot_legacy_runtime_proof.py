"""Legacy snapshot controls with real file bytes and portable Unix observations."""
import copy
from dataclasses import replace
import hashlib
import importlib
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

try:
    legacy = importlib.import_module('scripts.phase16_bot_legacy_runtime_proof')
except ModuleNotFoundError as error:
    if error.name != 'scripts.phase16_bot_legacy_runtime_proof':
        raise
    legacy = None


def sha(data):
    return hashlib.sha256(data).hexdigest()


class FileReader:
    def __init__(self, root, state):
        self.root, self.state = root, state
        self.reads = 0
        self.snapshots = {}
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, kind, error, traceback):
        self.closed = True

    def info(self, name):
        path = self.root if name == '.' else self.root / name
        meta = path.lstat()
        mode, uid, gid = self.state.get((self.root.name, name), (0o755 if path.is_dir() else 0o644, 0, 0))
        kind = stat.S_IFDIR if path.is_dir() else stat.S_IFREG
        if self.state.get(('link', self.root.name, name)):
            kind = stat.S_IFLNK
        return SimpleNamespace(st_dev=meta.st_dev, st_ino=meta.st_ino, st_mode=kind | mode,
                               st_uid=uid, st_gid=gid, st_nlink=meta.st_nlink, st_size=meta.st_size,
                               st_mtime_ns=meta.st_mtime_ns, st_ctime_ns=self.state.get(('ctime', self.root.name, name), meta.st_ctime_ns),
                               st_file_attributes=0)

    def entries(self, name):
        path = self.root if name == '.' else self.root / name
        return sorted(child.name for child in path.iterdir())

    def acl_names(self, name):
        return self.state.get(('acl', self.root.name, name), ())

    def ancestors(self):
        return (('/', SimpleNamespace(st_dev=1, st_ino=1, st_mode=stat.S_IFDIR | 0o755,
                                     st_uid=0, st_gid=0, st_nlink=1, st_size=1,
                                     st_mtime_ns=1, st_ctime_ns=1, st_file_attributes=0), ()),)

    def read_file(self, name, maximum, expected_size=None):
        self.reads += 1
        data = (self.root / name).read_bytes()
        if len(data) > maximum or (expected_size is not None and len(data) != expected_size):
            raise ValueError('bounded file read')
        hook = self.state.get('read_hook')
        if hook:
            hook(self, name)
        return data

    def stable(self):
        return None


class LegacyRuntimeProofTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(legacy, 'legacy runtime proof library is missing')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.deps = self.root / 'dependencies'
        self.source.mkdir()
        self.deps.mkdir()
        self.files = {'bot/handlers.py': b'handler fixture\n', 'bot/workflows.py': b'workflow fixture\n',
                      '__init__.py': b'', 'bot/__pycache__/handlers.cpython-312.pyc': b'opaque old cache'}
        for name, data in self.files.items():
            self.write(self.source, name, data)
        self.write(self.deps, 'package/__init__.py', b'package fixture\n')
        self.write(self.deps, 'package-1.dist-info/METADATA', b'Name: package\nVersion: 1\n')
        self.state = {}
        self.readers = []
        pins = {'bot/handlers.py': sha(self.files['bot/handlers.py']), 'bot/workflows.py': sha(self.files['bot/workflows.py'])}
        self.pin_patch = patch.object(legacy, 'POLICY_PINS', pins)
        self.pin_patch.start()
        self.addCleanup(self.pin_patch.stop)

    def write(self, root, name, data):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def factory(self, root):
        folder = self.source if root == legacy.SOURCE_ROOT else self.deps
        reader = FileReader(folder, self.state)
        self.readers.append(reader)
        return reader

    def collect(self, **kwargs):
        proof = legacy.collect_live(reader_factory=self.factory, **kwargs)
        self.addCleanup(proof.close)
        return proof

    def test_full_content_snapshot_binds_both_roots_without_git_claim(self):
        proof = self.collect()
        self.assertEqual(set(proof.rollback), {'source_sha256', 'dependencies_sha256'})
        self.assertTrue(all(len(value) == 64 for value in proof.rollback.values()))
        self.assertFalse(proof.policy_source['deployed_git_verified'])
        self.assertEqual(proof.policy_source['old_commit'], legacy.policy.OLD_COMMIT)
        self.assertEqual(proof.record()['scope'], 'OBSERVED_CONTENT_SNAPSHOT_NOT_PACKAGE_PROVENANCE')
        self.assertEqual(proof.check(), proof.rollback)

    def test_policy_file_wrong_bytes_block_collection(self):
        self.write(self.source, 'bot/handlers.py', b'wrong handler\n')
        with self.assertRaisesRegex(legacy.LegacyProofError, 'policy_source'):
            self.collect()
        self.assertTrue(all(reader.closed for reader in self.readers))

    def test_missing_policy_file_blocks_collection(self):
        (self.source / 'bot/workflows.py').unlink()
        with self.assertRaisesRegex(legacy.LegacyProofError, 'policy_source'):
            self.collect()

    def test_existing_pycache_is_included_not_skipped_or_deserialized(self):
        proof = self.collect()
        record = proof.record()
        node = record['roots']['source']['nodes']['bot/__pycache__/handlers.cpython-312.pyc']
        self.assertEqual(node['sha256'], sha(b'opaque old cache'))
        self.assertIn('bytecode_execution_safety', record['not_proven'])

    def test_saved_check_and_retained_check_do_not_rehash_file_bytes(self):
        proof = self.collect()
        reads = sum(reader.reads for reader in self.readers)
        self.assertEqual(proof.check(), proof.rollback)
        self.assertEqual(sum(reader.reads for reader in self.readers), reads)
        self.assertEqual(legacy.check_saved(proof.record(), reader_factory=self.factory), proof.rollback)
        self.assertEqual(sum(reader.reads for reader in self.readers), reads)

    def test_changed_source_after_snapshot_stops_retained_and_saved_checks(self):
        proof = self.collect()
        self.write(self.source, '__init__.py', b'new code')
        with self.assertRaisesRegex(legacy.LegacyProofError, 'continuity_changed'):
            proof.check()
        with self.assertRaisesRegex(legacy.LegacyProofError, 'continuity_changed'):
            legacy.check_saved(proof.record(), reader_factory=self.factory)

    def test_exact_directory_children_include_new_empty_directories(self):
        proof = self.collect()
        (self.deps / 'new_namespace').mkdir()
        with self.assertRaisesRegex(legacy.LegacyProofError, 'continuity_changed'):
            proof.check()

    def test_new_cache_after_snapshot_requires_fresh_admission(self):
        proof = self.collect()
        self.write(self.source, 'bot/__pycache__/new.cpython-312.pyc', b'new')
        with self.assertRaisesRegex(legacy.LegacyProofError, 'continuity_changed'):
            proof.check()

    def test_metadata_change_is_not_masked_by_unchanged_bytes(self):
        proof = self.collect()
        self.state[('source', 'bot/handlers.py')] = (0o640, 0, 1001)
        with self.assertRaisesRegex(legacy.LegacyProofError, 'continuity_changed'):
            proof.check()

    def test_nonroot_writable_symlink_and_acl_surfaces_stop(self):
        variants = [
            {('source', '__init__.py'): (0o644, 1001, 0)},
            {('source', '__init__.py'): (0o666, 0, 0)},
            {('link', 'source', '__init__.py'): True},
            {('acl', 'source', '__init__.py'): None},
            {('acl', 'source', '__init__.py'): ('system.posix_acl_access',)},
        ]
        for change in variants:
            with self.subTest(change=change):
                self.state.clear()
                self.state.update(change)
                with self.assertRaises(legacy.LegacyProofError):
                    self.collect()

    def test_hardlink_is_rejected(self):
        os.link(self.source / '__init__.py', self.root / 'outside-link')
        with self.assertRaisesRegex(legacy.LegacyProofError, 'unsafe_metadata'):
            self.collect()

    def test_capture_during_hash_not_later_toc_tou_reset(self):
        fired = False
        def change(reader, name):
            nonlocal fired
            if reader.root == self.source and name == 'bot/handlers.py' and not fired:
                fired = True
                self.write(self.source, name, b'altered during read\n')
        self.state['read_hook'] = change
        with self.assertRaisesRegex(legacy.LegacyProofError, 'continuity_changed'):
            self.collect()

    def test_digest_and_original_root_replacement_are_detected(self):
        proof = self.collect()
        record = proof.record()
        tampered = copy.deepcopy(record)
        tampered['roots']['source']['nodes']['__init__.py']['sha256'] = 'f' * 64
        with self.assertRaisesRegex(legacy.LegacyProofError, 'record_binding'):
            legacy.check_saved(tampered, reader_factory=self.factory)
        old = self.root / 'source-old'
        self.source.rename(old)
        self.source.mkdir()
        for name, data in self.files.items():
            self.write(self.source, name, data)
        with self.assertRaisesRegex(legacy.LegacyProofError, 'continuity_changed'):
            legacy.check_saved(record, reader_factory=self.factory)

    def test_record_returns_detached_json_safe_data(self):
        proof = self.collect()
        record = proof.record()
        record['rollback']['source_sha256'] = 'f' * 64
        self.assertNotEqual(proof.rollback['source_sha256'], 'f' * 64)
        proof.close()
        with self.assertRaisesRegex(legacy.LegacyProofError, 'proof_closed'):
            proof.check()

    def test_node_file_and_total_byte_bounds(self):
        for limits in (replace(legacy.Limits(), max_nodes=2), replace(legacy.Limits(), max_file_bytes=2),
                       replace(legacy.Limits(), max_total_bytes=5)):
            with self.subTest(limits=limits):
                with self.assertRaisesRegex(legacy.LegacyProofError, 'proof_limit'):
                    self.collect(limits=limits)


    def test_ctime_only_change_cannot_hide_behind_same_mtime_and_size(self):
        proof = self.collect()
        previous = proof.record()['roots']['dependencies']['nodes']['package/__init__.py']['fingerprint'][8]
        self.state[('ctime', 'dependencies', 'package/__init__.py')] = previous + 1
        with self.assertRaisesRegex(legacy.LegacyProofError, 'continuity_changed'):
            legacy.check_saved(proof.record(), reader_factory=self.factory)

    def test_env_surface_stops_before_content_read(self):
        self.write(self.source, '.env', b'synthetic protected fixture')
        with self.assertRaisesRegex(legacy.LegacyProofError, 'protected_surface'):
            self.collect()
        self.assertEqual(sum(reader.reads for reader in self.readers), 0)


if __name__ == '__main__':
    unittest.main()
