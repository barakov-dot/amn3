"""Access policy tests: real file bytes, explicit portable Unix metadata model."""
from dataclasses import replace
import hashlib
import importlib
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest

from scripts import phase16_bot_runtime_content as runtime
from tests.test_phase16_bot_runtime_content import DiskReader, wheel_files, zipped, digest, record_bytes, SITE, DIST

try:
    access = importlib.import_module('scripts.phase16_bot_stage_access')
except ModuleNotFoundError as error:
    if error.name != 'scripts.phase16_bot_stage_access':
        raise
    access = None


class UnixFixtureReader(DiskReader):
    """Windows cannot model root/group/ACL semantics with its permission bits.

    Content, directory enumeration, inode and timestamps are real. Only Unix
    permissions, link type/target and kernel ACL observations are modeled.
    """
    def __init__(self, root, attributes, links, acls, ancestors):
        super().__init__(root)
        self.attributes = attributes
        self.links = links
        self.acls = acls
        self.ancestor_values = ancestors

    def info(self, name):
        path = self.root if name == '.' else self.root.joinpath(*name.split('/'))
        actual = path.lstat()
        mode, uid, gid = self.attributes.get(name, (0o700 if path.is_dir() else 0o600, 0, 0))
        kind = stat.S_IFLNK if name in self.links else (stat.S_IFDIR if path.is_dir() else stat.S_IFREG)
        return SimpleNamespace(st_mode=kind | mode, st_uid=uid, st_gid=gid,
                               st_dev=actual.st_dev, st_ino=actual.st_ino,
                               st_nlink=actual.st_nlink, st_size=actual.st_size,
                               st_mtime=actual.st_mtime, st_mtime_ns=actual.st_mtime_ns,
                               st_ctime_ns=actual.st_ctime_ns, st_file_attributes=0)

    def entries(self, name):
        return sorted(p.name for p in (self.root if name == '.' else self.root / name).iterdir())

    def acl_names(self, name):
        return self.acls.get(name, ())

    def readlink(self, name):
        return self.links[name]

    def ancestors(self):
        return self.ancestor_values

    def stable(self):
        return None


class StageAccessTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(access, 'stage-access policy library is missing')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.attributes = {}
        self.links = {}
        self.acls = {}
        self.ancestors = []
        for index, name in enumerate(('/', '/opt', '/opt/amn2-spain', '/opt/amn2-spain/bot-candidates')):
            self.ancestors.append((name, SimpleNamespace(st_uid=0, st_gid=0, st_mode=stat.S_IFDIR | 0o755,
                                                       st_dev=1, st_ino=index + 1, st_nlink=1, st_size=0,
                                                       st_mtime_ns=0, st_ctime_ns=0), ()))
        self.identity = access.ServiceIdentity(1001, 1001, ())
        self.source = {'app/__init__.py': b'', 'app/main.py': b'VALUE = 7\n'}
        self.source_pins = {name: (len(data), digest(data)) for name, data in self.source.items()}
        self.wheels = {}
        self.pins = []
        for name, version, role in [('demo_pkg', '1.0', 'runtime'), ('pip', '24.0', 'bootstrap')]:
            extras = {f'{name}-{version}.dist-info/entry_points.txt':
                      b'[console_scripts]\ndemo = demo_pkg:main\n'} if role == 'runtime' else None
            files = wheel_files(name, version, extras)
            data = zipped(files)
            filename = f'{name}-{version}-py3-none-any.whl'
            self.wheels[filename] = data
            self.pins.append(runtime.WheelPin(filename, len(data), digest(data), name, version, role))
            for path, body in files.items():
                self.write(SITE + '/' + path, body)
        self.expected = runtime.build_expected(self.wheels, self.pins)
        for name, data in self.source.items():
            self.write('source/' + name, data)
        for name in ('payload', 'scratch', 'runtime-venv/include'):
            (self.root / name).mkdir(parents=True)
        self.write('claim.json', b'{}\n')
        self.write('result.json', b'{}\n')
        self.config = b'home = /usr/bin\ninclude-system-site-packages = false\nversion = 3.12.3\nexecutable = /usr/bin/python3.12\n'
        self.config_pin = (len(self.config), digest(self.config))
        self.write('runtime-venv/pyvenv.cfg', self.config)
        for name in ('activate', 'activate.csh', 'activate.fish', 'Activate.ps1', 'demo', 'pip', 'pip3', 'pip3.12'):
            path = 'runtime-venv/bin/' + name
            self.write(path, b'unverified-wrapper-content\n')
            self.attributes[path] = (0o755, 0, 0)
        for leaf, target in [('python', 'python3'), ('python3', '/usr/bin/python3'), ('python3.12', 'python3')]:
            self.link('runtime-venv/bin/' + leaf, target)
        self.link('runtime-venv/lib64', 'lib')

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def link(self, name, target):
        self.write(name, target.encode())
        self.links[name] = target
        self.attributes[name] = (0o777, 0, 0)

    def reader(self):
        return UnixFixtureReader(self.root, self.attributes, self.links, self.acls, self.ancestors)

    def build(self, **kwargs):
        return access.build_access_plan(self.reader(), self.expected, self.source_pins, self.identity,
                                        pyvenv_pin=self.config_pin, **kwargs)

    def apply_fixture(self, plan):
        for item in plan.objects:
            if item.action == 'set_mode_group':
                self.attributes[item.path] = (item.desired_mode, 0, item.desired_gid)

    def test_plan_grants_only_verified_content_and_seals_wrappers(self):
        plan = self.build()
        by_path = {item.path: item for item in plan.objects}
        self.assertEqual((by_path['.'].desired_mode, by_path['.'].desired_gid), (0o710, 1001))
        self.assertEqual(by_path['source/app'].desired_mode, 0o750)
        self.assertEqual(by_path['source/app/main.py'].desired_mode, 0o640)
        self.assertEqual(by_path['runtime-venv/bin/demo'].desired_mode, 0o600)
        self.assertEqual(by_path['runtime-venv/bin/python'].action, 'preserve_link')
        self.assertEqual(by_path['payload'].action, 'preserve_private')
        self.assertEqual(len(plan.digest), 64)
        self.assertEqual(plan.status, 'ACCESS_PLAN_READY_NOT_APPLIED')

    def test_missing_separately_trusted_bootstrap_blocks_plan(self):
        self.expected = runtime.build_expected({self.pins[0].file: self.wheels[self.pins[0].file]}, [self.pins[0]])
        with self.assertRaisesRegex(access.AccessError, 'runtime_not_proven'):
            self.build()

    def test_rehashed_tampered_runtime_blocks_plan(self):
        self.write(SITE + '/demo_pkg/__init__.py', b'VALUE = 9\n')
        with self.assertRaisesRegex(access.AccessError, 'runtime_not_proven'):
            self.build()

    def test_source_hash_or_extra_source_file_blocks_plan(self):
        self.write('source/app/main.py', b'VALUE = 9\n')
        with self.assertRaisesRegex(access.AccessError, 'source_content'):
            self.build()
        self.write('source/app/main.py', self.source['app/main.py'])
        self.write('source/app/unknown.py', b'')
        with self.assertRaisesRegex(access.AccessError, 'source_inventory'):
            self.build()

    def test_unknown_acl_or_existing_acl_blocks_plan(self):
        for value in (None, ('system.posix_acl_access',), ('security.selinux',)):
            with self.subTest(value=value):
                self.acls['source/app/main.py'] = value
                with self.assertRaisesRegex(access.AccessError, 'acl_not_clear'):
                    self.build()

    def test_private_payload_acl_is_not_ignored(self):
        self.acls['payload'] = ('system.posix_acl_default',)
        with self.assertRaisesRegex(access.AccessError, 'acl_not_clear'):
            self.build()

    def test_nonroot_owner_and_group_writable_surface_block(self):
        for value in ((0o640, 1001, 0), (0o660, 0, 1001), (0o4640, 0, 0)):
            with self.subTest(value=value):
                self.attributes['source/app/main.py'] = value
                with self.assertRaisesRegex(access.AccessError, 'unsafe_metadata'):
                    self.build()

    def test_unprotected_payload_or_receipts_block_plan(self):
        for name, mode in [('payload', 0o755), ('claim.json', 0o644)]:
            with self.subTest(name=name):
                self.attributes[name] = (mode, 0, 0)
                with self.assertRaisesRegex(access.AccessError, 'private_boundary'):
                    self.build()
                del self.attributes[name]

    def test_unknown_stage_or_bin_entry_blocks_plan(self):
        for name in ('unknown', 'runtime-venv/bin/unknown'):
            with self.subTest(name=name):
                self.write(name, b'x')
                with self.assertRaisesRegex(access.AccessError, 'stage_inventory|bin_inventory'):
                    self.build()
                (self.root / name).unlink()

    def test_interpreter_link_escape_or_cycle_blocks_plan(self):
        for target in ('/tmp/python', '../../other/python', 'python'):
            with self.subTest(target=target):
                self.links['runtime-venv/bin/python'] = target
                with self.assertRaisesRegex(access.AccessError, 'interpreter_link'):
                    self.build()

    def test_lib64_alias_is_exact_and_preserved(self):
        self.links['runtime-venv/lib64'] = '/tmp/lib'
        with self.assertRaisesRegex(access.AccessError, 'runtime_layout'):
            self.build()

    def test_pyvenv_config_requires_external_pin_and_isolation(self):
        self.write('runtime-venv/pyvenv.cfg', self.config.replace(b'false', b'true'))
        with self.assertRaisesRegex(access.AccessError, 'pyvenv_binding'):
            self.build()

    def test_shared_ancestors_are_never_mutation_objects(self):
        plan = self.build()
        self.assertEqual(tuple(item.path for item in plan.ancestors), ('/', '/opt', '/opt/amn2-spain', '/opt/amn2-spain/bot-candidates'))
        self.assertFalse(any(item.path.startswith('/') for item in plan.objects))
        self.ancestors[1][1].st_mode = stat.S_IFDIR | 0o700
        with self.assertRaisesRegex(access.AccessError, 'ancestor_access'):
            self.build()

    def test_unknown_or_extra_service_groups_block_plan(self):
        for identity in (access.ServiceIdentity(1001, 1001, None), access.ServiceIdentity(1001, 1001, (0,)), access.ServiceIdentity(0, 1001, ())):
            with self.subTest(identity=identity):
                self.identity = identity
                with self.assertRaisesRegex(access.AccessError, 'service_identity'):
                    self.build()

    def test_readonly_verification_distinguishes_plan_from_applied_dac(self):
        plan = self.build()
        self.assertEqual(access.verify_access(plan, self.reader()).status, 'NOT_READY')
        self.apply_fixture(plan)
        result = access.verify_access(plan, self.reader())
        self.assertEqual(result.status, 'DAC_ACCESS_VERIFIED_NOT_HOST_ADMITTED')
        self.assertIn('service_namespace_lsm_mounts', result.out_of_scope)

    def test_after_plan_tamper_new_file_and_metadata_drift_stop(self):
        plan = self.build()
        self.apply_fixture(plan)
        self.write('source/app/main.py', b'VALUE = 9\n')
        self.assertEqual(access.verify_access(plan, self.reader()).reason, 'object_content')
        self.write('source/app/main.py', self.source['app/main.py'])
        self.write('source/app/new.py', b'')
        self.assertEqual(access.verify_access(plan, self.reader()).reason, 'object_inventory')

    def test_plan_digest_rejects_changed_authorization_list(self):
        plan = self.build()
        changed = replace(plan, objects=plan.objects[1:])
        self.assertEqual(access.verify_access(changed, self.reader()).reason, 'plan_binding')

    def test_fresh_acl_failure_is_not_mode_only_pass(self):
        plan = self.build()
        self.apply_fixture(plan)
        self.acls['source/app/main.py'] = None
        self.assertEqual(access.verify_access(plan, self.reader()).reason, 'acl_not_clear')


    def test_only_app_source_content_receives_service_group_read(self):
        for name, body in {'README.md': b'private docs', 'tests/test_fixture.py': b'private tests'}.items():
            self.write('source/' + name, body)
            self.source_pins[name] = (len(body), digest(body))
        plan = self.build()
        entries = {item.path: item for item in plan.objects}
        self.assertEqual((entries['source'].desired_mode, entries['source'].desired_gid), (0o750, 1001))
        self.assertEqual((entries['source/README.md'].desired_mode, entries['source/README.md'].desired_gid), (0o600, 0))
        self.assertEqual((entries['source/tests'].desired_mode, entries['source/tests'].desired_gid), (0o700, 0))
        self.assertEqual((entries['source/app/main.py'].desired_mode, entries['source/app/main.py'].desired_gid), (0o640, 1001))


if __name__ == '__main__':
    unittest.main()
