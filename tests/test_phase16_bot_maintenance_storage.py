"""Real temporary bytes, with explicit portable Unix FD/metadata semantics."""
import copy
import hashlib
import importlib
import os
from pathlib import Path, PurePosixPath
import stat
import tempfile
from types import SimpleNamespace
import unittest

try:
    storage = importlib.import_module('scripts.phase16_bot_maintenance_storage')
except ModuleNotFoundError as error:
    if error.name != 'scripts.phase16_bot_maintenance_storage':
        raise
    storage = None

SERVICE = '/var/lib/amn2-spain'
BASE = SERVICE + '/phase16-maintenance'
OP = BASE + '/phase16-storage-test'
RECORD = OP + '/context.json'


class ModelOS:
    """Read actual files; model only unavailable Unix ownership/dirfd features."""
    O_RDONLY, O_DIRECTORY, O_NOFOLLOW, O_CLOEXEC, O_NONBLOCK = 0, 1 << 20, 1 << 21, 1 << 22, 1 << 23

    def __init__(self, root):
        self.root, self.nodes, self.handles, self.counter = root, {}, {}, 0
        self.read_hook = None
        self.read_sizes = []
        for path in ('/', '/var', '/var/lib', SERVICE, BASE, OP, OP + '/code', OP + '/code/scripts'):
            self.add(path, directory=True)
        self.nodes[SERVICE].uid = self.nodes[SERVICE].gid = 61212
        self.nodes[SERVICE].mode = 0o750
        self.add(RECORD, data=b'{"bounded":"bytes"}\n')
        self.add(OP + '/code/scripts/worker.py', data=b'VALUE = 1\n', mode=0o644)

    def add(self, name, *, directory=False, data=b'', mode=None):
        path = self.root / name.lstrip('/')
        if directory:
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        node = SimpleNamespace(path=path, kind=stat.S_IFDIR if directory else stat.S_IFREG,
            mode=mode if mode is not None else (0o700 if name.startswith(BASE) else 0o755) if directory else 0o600,
            uid=0, gid=0, nlink=None, inode=None, ctime=path.stat().st_ctime_ns, attrs=())
        self.nodes[name] = node
        return node

    def name(self, name, dir_fd):
        if dir_fd is None:
            return name
        base = self.handles[dir_fd][0]
        return str(PurePosixPath(base) / name)

    def meta(self, node, actual_fd=None):
        value = node.path.stat() if actual_fd is None else os.fstat(actual_fd)
        return SimpleNamespace(st_dev=value.st_dev, st_ino=node.inode or value.st_ino,
            st_mode=node.kind | node.mode, st_uid=node.uid, st_gid=node.gid,
            st_nlink=value.st_nlink if node.nlink is None else node.nlink, st_size=value.st_size,
            st_mtime_ns=value.st_mtime_ns, st_ctime_ns=value.st_ctime_ns if node.ctime is None else node.ctime)

    def open(self, name, flags, *, dir_fd=None):
        assert flags & self.O_NOFOLLOW and flags & self.O_CLOEXEC
        key = self.name(name, dir_fd)
        node = self.nodes[key]
        if node.kind == stat.S_IFLNK or ((flags & self.O_DIRECTORY) and node.kind != stat.S_IFDIR):
            raise OSError('nofollow')
        actual_fd = None if node.kind != stat.S_IFREG else os.open(node.path, os.O_RDONLY | getattr(os, 'O_BINARY', 0))
        self.counter += 1
        self.handles[self.counter] = (key, node, actual_fd)
        return self.counter

    def fstat(self, fd):
        _, node, actual_fd = self.handles[fd]
        return self.meta(node, actual_fd)

    def stat(self, name, *, dir_fd=None, follow_symlinks=False):
        assert not follow_symlinks
        return self.meta(self.nodes[self.name(name, dir_fd)])

    def listxattr(self, fd):
        return self.handles[fd][1].attrs

    def read(self, fd, maximum):
        self.read_sizes.append(maximum)
        data = os.read(self.handles[fd][2], maximum)
        if self.read_hook:
            hook, self.read_hook = self.read_hook, None
            hook()
        return data

    def close(self, fd):
        _, _, actual_fd = self.handles.pop(fd)
        if actual_fd is not None:
            os.close(actual_fd)


class MaintenanceStorageTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(storage, 'maintenance storage module is missing')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fs = ModelOS(Path(self.temp.name))
        self.addCleanup(lambda: self.assertEqual(self.fs.handles, {}))

    def read(self, path=RECORD, maximum=1024, **kwargs):
        return storage.read_private(path, maximum, syscalls=self.fs, **kwargs)

    def test_exact_service_ancestor_allows_real_private_read(self):
        expected = self.fs.nodes[RECORD].path.read_bytes()
        self.assertEqual(self.read(expected_sha256=hashlib.sha256(expected).hexdigest()), expected)
        self.assertTrue(self.fs.read_sizes)

    def test_held_reader_compatible_read_and_full_chain(self):
        with storage.MaintenanceReader(OP, syscalls=self.fs) as reader:
            self.assertEqual(reader.read('context.json', 20), b'{"bounded":"bytes"}\n')
            self.assertEqual(len(reader.chain), 6)
            reader.check_chain()

    def test_exception_requires_exact_uid_gid_and_mode(self):
        for field, value in (('uid', 1), ('gid', 0), ('mode', 0o755), ('mode', 0o770), ('mode', 0o1750)):
            with self.subTest(field=field, value=value):
                node = self.fs.nodes[SERVICE]; before = getattr(node, field); setattr(node, field, value)
                try:
                    with self.assertRaises(Exception): self.read()
                finally: setattr(node, field, before)

    def test_root_owned_service_ancestor_still_supported(self):
        self.fs.nodes[SERVICE].uid = self.fs.nodes[SERVICE].gid = 0
        self.assertEqual(self.read(), self.fs.nodes[RECORD].path.read_bytes())

    def test_no_service_owner_exception_on_any_other_ancestor(self):
        for name in ('/var/lib', BASE, OP, OP + '/code'):
            with self.subTest(name=name):
                node = self.fs.nodes[name]; node.uid = node.gid = 61212
                try:
                    path = RECORD if name != OP + '/code' else OP + '/code/scripts/worker.py'
                    with self.assertRaises(Exception): storage.read_owned(path, 1024, syscalls=self.fs)
                finally: node.uid = node.gid = 0

    def test_operation_and_code_dirs_must_be_private_root_group(self):
        for name in (BASE, OP, OP + '/code', OP + '/code/scripts'):
            for field, value in (('mode', 0o750), ('gid', 61212)):
                with self.subTest(name=name, field=field):
                    node = self.fs.nodes[name]; before = getattr(node, field); setattr(node, field, value)
                    try:
                        with self.assertRaises(Exception): storage.read_owned(OP + '/code/scripts/worker.py', 1024, syscalls=self.fs)
                    finally: setattr(node, field, before)

    def test_paths_outside_fixed_subtree_or_noncanonical_rejected(self):
        for path in ('/etc/passwd', SERVICE, BASE + '-other/op', BASE + '/other-op',
                     OP + '/../phase16-other', OP + '//context.json', OP + '/./context.json', OP + '/x\\y'):
            with self.subTest(path=path), self.assertRaises(Exception): storage.MaintenanceReader(path, syscalls=self.fs)
        self.assertFalse(self.fs.handles)

    def test_symlink_directories_and_file_rejected(self):
        for path in (SERVICE, OP, RECORD):
            with self.subTest(path=path):
                node = self.fs.nodes[path]; old = node.kind; node.kind = stat.S_IFLNK
                try:
                    with self.assertRaises(Exception): self.read()
                finally: node.kind = old

    def test_acl_unknown_or_present_rejects_any_object(self):
        for path in ('/var', SERVICE, BASE, OP, RECORD):
            with self.subTest(path=path):
                self.fs.nodes[path].attrs = ('system.posix_acl_access',)
                try:
                    with self.assertRaises(Exception): self.read()
                finally: self.fs.nodes[path].attrs = ()
        self.fs.listxattr = lambda fd: (_ for _ in ()).throw(OSError('unsupported ACL check'))
        with self.assertRaises(Exception): self.read()

    def test_replaced_named_maintenance_parent_is_detected(self):
        with self.assertRaises(Exception):
            with storage.MaintenanceReader(OP, syscalls=self.fs) as reader:
                changed = copy.copy(self.fs.nodes[BASE]); changed.inode = self.fs.meta(changed).st_ino + 1
                self.fs.nodes[BASE] = changed
                reader.check_chain()

    def test_same_inode_ancestor_ctime_change_is_detected(self):
        with self.assertRaises(Exception):
            with storage.MaintenanceReader(OP, syscalls=self.fs) as reader:
                self.fs.nodes[SERVICE].ctime = self.fs.meta(self.fs.nodes[SERVICE]).st_ctime_ns + 1
                reader.check_chain()

    def test_replaced_file_during_fd_read_rejected(self):
        def replace():
            changed = copy.copy(self.fs.nodes[RECORD]); changed.inode = self.fs.meta(changed).st_ino + 1
            self.fs.nodes[RECORD] = changed
        self.fs.read_hook = replace
        with self.assertRaises(Exception): self.read()

    def test_file_content_change_during_read_rejected(self):
        def change(): self.fs.nodes[RECORD].ctime = self.fs.meta(self.fs.nodes[RECORD]).st_ctime_ns + 1
        self.fs.read_hook = change
        with self.assertRaises(Exception): self.read()

    def test_private_files_reject_group_modes_hardlinks_and_owner(self):
        for field, value in (('mode', 0o640), ('uid', 61212), ('gid', 61212), ('nlink', 2), ('kind', stat.S_IFIFO)):
            with self.subTest(field=field):
                node = self.fs.nodes[RECORD]; old = getattr(node, field); setattr(node, field, value)
                try:
                    with self.assertRaises(Exception): self.read()
                finally: setattr(node, field, old)

    def test_hash_mismatch_and_bounds_reject_without_unbounded_read(self):
        with self.assertRaises(Exception): self.read(expected_sha256='0' * 64)
        self.fs.read_sizes.clear()
        with self.assertRaises(Exception): self.read(maximum=3)
        self.assertEqual(self.fs.read_sizes, [])
        for maximum in (-1, True, 16 * 1024 * 1024 + 1):
            with self.subTest(maximum=maximum), self.assertRaises(Exception): self.read(maximum=maximum)

    def test_public_root_code_is_read_but_private_record_is_stricter(self):
        path = OP + '/code/scripts/worker.py'
        self.assertEqual(storage.read_owned(path, 1024, syscalls=self.fs), b'VALUE = 1\n')
        with self.assertRaises(Exception): self.read(path)
        snapshot = storage.safe_owned_path(path, syscalls=self.fs)
        self.assertEqual(tuple(snapshot), storage.fingerprint(self.fs.meta(self.fs.nodes[path])))

    def test_reader_before_enter_or_after_close_cannot_open_relative_cwd_file(self):
        reader = storage.MaintenanceReader(OP, syscalls=self.fs)
        with self.assertRaises(Exception) as caught:
            reader.read('context.json', 20)
        self.assertIsInstance(caught.exception, storage.StorageError)
        self.assertEqual(str(caught.exception), 'storage_not_open')
        with reader:
            pass
        with self.assertRaisesRegex(storage.StorageError, 'storage_not_open'):
            reader.read('context.json', 20)
        self.assertEqual(self.fs.read_sizes, [])

    def test_large_record_and_nested_compatible_read(self):
        raw = b'x' * 32768
        self.fs.nodes[RECORD].path.write_bytes(raw)
        self.assertEqual(self.read(maximum=len(raw)), raw)
        with storage.MaintenanceReader(OP, syscalls=self.fs) as reader:
            self.assertEqual(reader.read('code/scripts/worker.py', 10), b'VALUE = 1\n')
            self.assertEqual(len(reader.chain), 6)
            with self.assertRaises(Exception): reader.read('../context.json', 20)

    def test_ancestor_replacement_during_read_is_rejected(self):
        def replace():
            changed = copy.copy(self.fs.nodes[BASE]); changed.inode = self.fs.meta(changed).st_ino + 1
            self.fs.nodes[BASE] = changed
        self.fs.read_hook = replace
        with self.assertRaises(Exception): self.read()

    def test_parent_predicate_cannot_generalize_service_exception(self):
        meta = self.fs.meta(self.fs.nodes[SERVICE])
        self.assertTrue(storage.check_owned_parent(meta, SERVICE))
        for path in ('/opt/amn2-spain', SERVICE + '-other', BASE, SERVICE + '/../amn2-spain'):
            with self.subTest(path=path), self.assertRaises(Exception): storage.check_owned_parent(meta, path)


class LinuxImportModelTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(hasattr(storage, 'IMPORT_BOOTSTRAP'))
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.fs = ModelOS(Path(self.temp.name))
        self.fs.nodes[OP+'/code/scripts/worker.py'].mode=0o600
        self.fs.add('/run',directory=True);self.fs.add('/run/phase16',directory=True,mode=0o700)
        real_stat=self.fs.stat
        def bounded_stat(*args,**kwargs):
            try:return real_stat(*args,**kwargs)
            except KeyError:raise FileNotFoundError from None
        self.fs.stat=bounded_stat;self.fs.geteuid=lambda:0
        self.ns={};exec(storage.IMPORT_BOOTSTRAP,self.ns)
        self.ns['_p16_os']=self.fs
        self.ns['_p16_sys']=SimpleNamespace(platform='linux',version_info=(3,12),modules={},meta_path=[],path=[])
        self.pins={'scripts/worker.py':hashlib.sha256(b'VALUE = 1\n').hexdigest()}
        def cleanup():
            for state in self.ns['_p16_retained']:self.ns['_p16_close'](state)
            self.assertEqual(self.fs.handles,{})
        self.addCleanup(cleanup)

    def bind(self):return self.ns['_phase16_import_root'](OP+'/code',self.pins,'a'*64)

    def test_linux_fd_chain_retained_and_loader_uses_original_bytes(self):
        from types import ModuleType
        alias=self.bind();self.assertTrue(alias.startswith('/proc/self/fd/'));self.assertTrue(self.fs.handles)
        self.fs.nodes[OP+'/code/scripts/worker.py'].path.write_bytes(b'VALUE = 9\n')
        spec=self.ns['_p16_sys'].meta_path[0].find_spec('scripts.worker')
        module=ModuleType('scripts.worker');spec.loader.exec_module(module)
        self.assertEqual(module.VALUE,1);self.assertTrue(module.__file__.startswith(alias))

    def test_linux_wrong_owner_mode_and_symlinks_fail_before_import(self):
        for path,field,value in ((SERVICE,'uid',1),(OP+'/code','mode',0o750),
                                 (OP+'/code/scripts/worker.py','mode',0o640),
                                 (OP+'/code/scripts','kind',stat.S_IFLNK)):
            with self.subTest(path=path,field=field):
                node=self.fs.nodes[path];old=getattr(node,field);setattr(node,field,value)
                try:
                    with self.assertRaises(Exception):self.bind()
                    self.assertFalse(self.fs.handles);self.assertFalse(self.ns['_p16_sys'].meta_path)
                finally:setattr(node,field,old)

    def test_linux_changed_named_chain_during_read_blocks_loader(self):
        def replace():
            node=copy.copy(self.fs.nodes[BASE]);node.inode=self.fs.meta(node).st_ino+1;self.fs.nodes[BASE]=node
        self.fs.read_hook=replace
        with self.assertRaisesRegex(RuntimeError,'bootstrap_changed'):self.bind()
        self.assertFalse(self.ns['_p16_sys'].meta_path)

    def test_linux_cache_parent_private_and_prefix_absent(self):
        self.fs.nodes['/run/phase16'].mode=0o755
        with self.assertRaisesRegex(RuntimeError,'bootstrap_private_directory'):self.bind()
        self.fs.nodes['/run/phase16'].mode=0o700
        self.fs.add('/run/phase16/no-bytecode-'+'a'*64,directory=True,mode=0o700)
        with self.assertRaisesRegex(RuntimeError,'bootstrap_unbound_path'):self.bind()
        self.assertFalse(self.ns['_p16_sys'].meta_path)

class ImportBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(hasattr(storage, 'IMPORT_BOOTSTRAP'), 'pinned import bootstrap is missing')
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.code = Path(self.temp.name) / 'code'; (self.code / 'scripts').mkdir(parents=True)
        self.source = self.code / 'scripts/worker.py'; self.raw = b'VALUE = "BOUND_SOURCE"\n'
        self.source.write_bytes(self.raw)
        self.pins = {'scripts/worker.py': hashlib.sha256(self.raw).hexdigest()}

    def child(self, tail='from scripts.worker import VALUE; print(VALUE)', *, pins=None):
        import subprocess, sys
        script = storage.IMPORT_BOOTSTRAP + '\n'
        # This branch tests source/cache/import behavior only, never Linux ownership.
        if sys.platform != 'win32': script += '_p16_sys.platform="win32"\n'
        script += '_phase16_import_root(' + repr(str(self.code)) + ',' + repr(self.pins if pins is None else pins) + ',"a"*64)\n' + tail
        return subprocess.run([sys.executable, '-I', '-S', '-B', '-c', script], capture_output=True, timeout=5)

    def test_hash_mismatch_stops_before_project_execution(self):
        self.source.write_bytes(b'print("UNBOUND_EXECUTION")\nVALUE="BAD"\n')
        result = self.child()
        self.assertNotEqual(result.returncode, 0); self.assertNotIn(b'UNBOUND_EXECUTION', result.stdout)
        self.assertIn(b'bootstrap_hash', result.stderr)

    def test_captured_source_cannot_be_replaced_after_binding(self):
        tail = 'import pathlib\npathlib.Path(' + repr(str(self.source)) + ').write_text(' + repr('VALUE="REPLACED"\n') + ')\nfrom scripts.worker import VALUE; print(VALUE)'
        result = self.child(tail)
        self.assertEqual(result.returncode, 0, result.stderr); self.assertEqual(result.stdout.strip(), b'BOUND_SOURCE')

    def test_later_sys_path_shadow_cannot_replace_namespace_or_module(self):
        evil = Path(self.temp.name) / 'evil'; (evil / 'scripts').mkdir(parents=True)
        (evil / 'scripts/__init__.py').write_text('print("MALICIOUS_PACKAGE")\n')
        (evil / 'scripts/worker.py').write_text('VALUE="MALICIOUS_MODULE"\n')
        result = self.child('import sys\nsys.path.insert(0,' + repr(str(evil)) + ')\nfrom scripts.worker import VALUE; print(VALUE)')
        self.assertEqual(result.returncode, 0, result.stderr); self.assertEqual(result.stdout.strip(), b'BOUND_SOURCE')

    def test_bound_module_cannot_redirect_later_stdlib_import(self):
        evil = Path(self.temp.name) / 'evil-stdlib'; evil.mkdir()
        (evil / 'subprocess.py').write_text('print("MALICIOUS_STDLIB")\nVALUE="UNBOUND"\n')
        raw = ('import sys\nsys.path.insert(0,' + repr(str(evil)) + ')\nimport subprocess\nVALUE="BOUND_STDLIB" if hasattr(subprocess,"Popen") else "UNBOUND"\n').encode()
        self.source.write_bytes(raw);self.pins['scripts/worker.py']=hashlib.sha256(raw).hexdigest()
        result=self.child()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),b'BOUND_STDLIB')

    def test_stdlib_subpackage_path_cannot_leave_initial_trusted_roots(self):
        evil=Path(self.temp.name)/'evil-subpackage';evil.mkdir()
        (evil/'bound_evil.py').write_text('print("MALICIOUS_SUBPACKAGE")\n')
        raw=('import xml\nxml.__path__=['+repr(str(evil))+']\nimport xml.bound_evil\n').encode()
        self.source.write_bytes(raw);self.pins['scripts/worker.py']=hashlib.sha256(raw).hexdigest()
        result=self.child()
        self.assertNotIn(b'MALICIOUS_SUBPACKAGE',result.stdout)
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'bootstrap_stdlib_path',result.stderr)

    def test_unknown_scripts_module_has_no_path_fallback(self):
        (self.code / 'scripts/unbound.py').write_text('print("UNBOUND_MODULE")\n')
        result = self.child('import scripts.unbound')
        self.assertNotEqual(result.returncode, 0); self.assertNotIn(b'UNBOUND_MODULE', result.stdout)

    def test_unbound_initializer_is_rejected(self):
        (self.code / 'scripts/__init__.py').write_text('print("UNBOUND_INIT")\n')
        result = self.child()
        self.assertNotEqual(result.returncode, 0); self.assertNotIn(b'UNBOUND_INIT', result.stdout)

    def test_valid_stale_pyc_is_never_deserialized(self):
        import importlib.util, marshal, struct
        cache = Path(importlib.util.cache_from_source(str(self.source))); cache.parent.mkdir()
        stale = compile('VALUE="STALE_CACHE"\n', str(self.source), 'exec')
        cache.write_bytes(importlib.util.MAGIC_NUMBER + struct.pack('<III', 0, int(self.source.stat().st_mtime), len(self.raw)) + marshal.dumps(stale))
        result = self.child()
        self.assertEqual(result.returncode, 0, result.stderr); self.assertEqual(result.stdout.strip(), b'BOUND_SOURCE')

    def test_manifest_path_traversal_refused_before_project_execution(self):
        result = self.child(pins={'../worker.py': 'a'*64})
        self.assertNotEqual(result.returncode, 0); self.assertEqual(result.stdout, b'')

if __name__ == '__main__':
    unittest.main()
