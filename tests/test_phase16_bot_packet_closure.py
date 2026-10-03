"""Saved packet closure in a genuinely isolated interpreter; no Linux actions."""
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import unittest

AVAILABLE = importlib.util.find_spec('scripts.phase16_bot_maintenance_packet') is not None
if AVAILABLE:
    from scripts import phase16_bot_maintenance_packet as packet


ISOLATED_CHECK = r'''
import ast, hashlib, importlib, json, pathlib, sys
saved=pathlib.Path(sys.argv[1]).resolve()
expected=json.loads(pathlib.Path(sys.argv[2]).read_text(encoding='utf-8'))
mode=sys.argv[3]
base=pathlib.Path(sys.base_prefix).resolve()
stdlib=[p for p in sys.path if p and pathlib.Path(p).resolve().is_relative_to(base)]
assert stdlib
sys.path[:]=[str(saved),*stdlib]
assert all(pathlib.Path(p).resolve()==saved or pathlib.Path(p).resolve().is_relative_to(base) for p in sys.path)
assert not pathlib.Path(sys.pycache_prefix).exists()
def no_live(event,args):
    if event.startswith(('subprocess.','socket.','os.exec','os.spawn')) or event in ('os.system','os.fork','os.forkpty'):
        raise AssertionError('live_call_during_import')
sys.addaudithook(no_live)
bootstrap_used=mode=='bootstrap'
poison=None;original=None;captured_name=None
if bootstrap_used:
    assert sys.platform=='win32', 'this closure test must not enter native Linux admission'
    storage_source=saved/'scripts/phase16_bot_maintenance_storage.py'
    tree=ast.parse(storage_source.read_bytes())
    assignments=[node for node in tree.body if isinstance(node,ast.Assign) and
        any(isinstance(target,ast.Name) and target.id=='IMPORT_BOOTSTRAP' for target in node.targets)]
    assert len(assignments)==1
    exact_bootstrap=ast.literal_eval(assignments[0].value)
    exec(compile(exact_bootstrap,'<exact-packet-import-bootstrap>','exec'),globals())
    alias=_phase16_import_root(str(saved),expected,'a'*64)
    assert pathlib.Path(alias)==saved
    assert type(sys.meta_path[0]).__name__=='BoundFinder'
    # Poison a real dependency AFTER immutable bytes are captured, BEFORE entry
    # imports it. This mutation is confined to this temporary copied packet.
    captured_name=saved/'scripts/phase16_bot_effective_settings.py'
    original=captured_name.read_bytes()
    captured_name.write_bytes(b"raise RuntimeError('UNBOUND_NAMED_SOURCE_EXECUTED')\n")
    poison=saved.parent/'poison-source'
    (poison/'scripts').mkdir(parents=True)
    (poison/'scripts/phase16_unbound_closure_probe.py').write_text(
        "raise RuntimeError('UNBOUND_FALLBACK_EXECUTED')\n",encoding='ascii')
    sys.path.insert(0,str(poison))
try:
    if mode=='missing_module':
        importlib.import_module('scripts.phase16_bot_maintenance_storage')
    from scripts import phase16_bot_maintenance_entry as entry
    from scripts import phase16_bot_maintenance_binding as binding
    from scripts import phase16_bot_maintenance_linux as linux
    from scripts import phase16_bot_coordinator_process as coordinator
    importlib.import_module('scripts.phase16_bot_maintenance_storage')
    if bootstrap_used:
        # Entry has exercised the frozen modules' ROOT/sys.path insertion code.
        # Existing modules must all come from captured bytes even while their
        # ordinary named source disagrees with the approved packet.
        settings=importlib.import_module('scripts.phase16_bot_effective_settings')
        assert type(settings.__loader__).__name__=='BoundLoader'
        assert captured_name.read_bytes()!=original
        captured_name.write_bytes(original)
        sys.path.insert(0,str(poison))
        try:
            importlib.import_module('scripts.phase16_unbound_closure_probe')
        except ModuleNotFoundError as error:
            assert error.name=='scripts.phase16_unbound_closure_probe'
        else:raise AssertionError('unbound scripts module escaped finder')
        sys.path[:]=[p for p in sys.path if pathlib.Path(p).resolve()!=poison]
    assert binding.ROOT.resolve()==saved
    assert binding.MANIFEST.resolve().is_relative_to(saved)
    for module in (entry,binding,linux,coordinator):
        assert pathlib.Path(module.__file__).resolve().parents[1]==saved
    if mode=='missing_module':raise AssertionError('missing module resolved outside saved code')
    target=binding.validate_packet()
    historical=binding.stage_snapshot()
    if mode=='missing_resource':raise AssertionError('missing resource resolved outside saved code')
    worker=linux.worker_artifacts(saved)
    full=coordinator.artifact_inventory(saved,'scripts.phase16_bot_host_admission',entry.EXTRA)
    assert set(worker)<=set(full)<=set(expected)
    assert all(expected[name]==digest for name,digest in full.items())
    assert set(entry.RESOURCES)<=set(expected)
    roots={}
    for name,module in list(sys.modules.items()):
        if name=='scripts' or name.startswith('scripts.'):
            filename=getattr(module,'__file__',None)
            if filename:
                source=pathlib.Path(filename).resolve()
                assert source.is_relative_to(saved)
                relative=source.relative_to(saved).as_posix()
                assert relative in expected
                roots[name]=relative
                if bootstrap_used:
                    assert type(module.__loader__).__name__=='BoundLoader'
                    assert module.__cached__ is None
            else:
                assert all(pathlib.Path(p).resolve().is_relative_to(saved) for p in module.__path__)
    assert all(pathlib.Path(p).resolve()==saved or pathlib.Path(p).resolve().is_relative_to(base) for p in sys.path)
    assert not pathlib.Path(sys.pycache_prefix).exists()
    print(json.dumps(dict(status='SAVED_CLOSURE_PASS',target=target['target_binding_sha256'],
        stage_status=historical['status'],stage_files=historical['content_files'],worker_count=len(worker),
        coordinator_count=len(full),saved_count=len(expected),imported_modules=roots,saved_root=str(saved),
        captured_bootstrap_used=bootstrap_used,named_source_poison_ignored=bootstrap_used,unbound_fallback_blocked=bootstrap_used)))
except ModuleNotFoundError as error:
    if mode!='missing_module':raise
    assert error.name=='scripts.phase16_bot_maintenance_storage'
    print(json.dumps(dict(status='SAVED_MODULE_MISSING_STOP',name=error.name)))
except FileNotFoundError:
    if mode!='missing_resource':raise
    print(json.dumps(dict(status='SAVED_RESOURCE_MISSING_STOP')))
'''


class Availability(unittest.TestCase):
    def test_saved_packet_builder_exists(self):
        self.assertTrue(AVAILABLE, 'complete maintenance packet is not available')


@unittest.skipUnless(AVAILABLE, 'builder availability fails first')
class PacketClosureTests(unittest.TestCase):
    def setUp(self):
        self.manifest = packet.expected_manifest()
        self.packed = packet.payload(self.manifest)
        self.value = packet.decode_payload(self.packed)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.saved = self.directory / 'saved-code'
        self.saved.mkdir()
        self.cwd = self.directory / 'empty-cwd'
        self.cwd.mkdir()
        self.original = Path(__file__).resolve().parents[1]
        self.assertFalse(self.directory.resolve().is_relative_to(self.original))

    def unpack(self, *, omit=None):
        for name, encoded in self.value['files'].items():
            relative = PurePosixPath(name)
            self.assertFalse(relative.is_absolute())
            self.assertNotIn('..', relative.parts)
            self.assertNotIn('\\', name)
            if name == omit:
                continue
            destination = self.saved.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(base64.b64decode(encoded, validate=True))
        self.assertFalse(list(self.saved.rglob('__pycache__')))

    def check_saved(self, mode='complete'):
        expected = self.directory / 'expected.json'
        expected.write_text(json.dumps(self.manifest['files_sha256_lf']), encoding='utf-8')
        pycache = self.directory / 'absent-pycache'
        environment = {k: os.environ[k] for k in ('SystemRoot', 'WINDIR') if k in os.environ}
        result = subprocess.run([sys.executable, '-I', '-S', '-B', '-X', 'pycache_prefix=' + str(pycache),
            '-c', ISOLATED_CHECK, str(self.saved), str(expected), mode],
            cwd=self.cwd, env=environment, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', errors='replace'))
        self.assertEqual(result.stderr, b'')
        self.assertLessEqual(len(result.stdout), 65536)
        self.assertFalse(pycache.exists())
        self.assertFalse(list(self.saved.rglob('__pycache__')))
        self.assertEqual(list(self.cwd.iterdir()), [])
        return json.loads(result.stdout)

    def test_exact_payload_source_resource_set_and_hashes(self):
        self.assertEqual(set(self.value), {'manifest', 'files'})
        self.assertEqual(self.value['manifest'], self.manifest)
        files = self.value['files']
        hashes = self.manifest['files_sha256_lf']
        self.assertEqual(set(files), set(hashes))
        self.assertGreaterEqual(len(files), 54)
        self.assertLessEqual(len(self.packed), 2 * 1024 * 1024)
        for name, encoded in files.items():
            with self.subTest(name=name):
                raw = base64.b64decode(encoded, validate=True)
                self.assertEqual(hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest(), hashes[name])
                self.assertTrue(name.endswith(('.py', '.txt', '.json')))
                self.assertFalse(any(part in name for part in ('__pycache__', '.env', '.git/', '.pyc')))
        self.assertIn('scripts/phase16_bot_maintenance_storage.py', set(files))

    def test_native_isolated_imports_and_all_saved_resource_consumers(self):
        self.unpack()
        result = self.check_saved()
        self.assertEqual(result['status'], 'SAVED_CLOSURE_PASS')
        self.assertEqual(result['saved_count'], len(self.manifest['files_sha256_lf']))
        self.assertEqual(result['stage_status'], 'HISTORICAL_STAGE_BOUND')
        self.assertEqual(result['stage_files'], 200)
        self.assertGreater(result['worker_count'], 0)
        self.assertGreaterEqual(result['coordinator_count'], result['worker_count'])
        self.assertEqual(Path(result['saved_root']), self.saved.resolve())
        self.assertIn('scripts.phase16_bot_maintenance_storage', result['imported_modules'])


    @unittest.skipUnless(sys.platform == 'win32', 'Windows source/cache branch only; Linux admission is separate')
    def test_exact_packet_import_bootstrap_closes_named_path_and_unbound_module_fallback(self):
        self.unpack()
        # The literal exercised by the child is exactly the current packet's
        # embedded implementation, read from authenticated saved storage bytes.
        self.assertTrue(packet.storage.IMPORT_BOOTSTRAP in packet.bootstrap(self.packed, self.manifest))
        result = self.check_saved('bootstrap')
        self.assertEqual(result['status'], 'SAVED_CLOSURE_PASS')
        self.assertTrue(result['captured_bootstrap_used'])
        self.assertTrue(result['named_source_poison_ignored'])
        self.assertTrue(result['unbound_fallback_blocked'])
        self.assertEqual(result['saved_count'], len(self.manifest['files_sha256_lf']))
        self.assertEqual(result['stage_status'], 'HISTORICAL_STAGE_BOUND')
        self.assertIn('scripts.phase16_bot_effective_settings', result['imported_modules'])

    def test_missing_saved_dependency_cannot_fall_back_to_original_checkout(self):
        self.unpack(omit='scripts/phase16_bot_maintenance_storage.py')
        self.assertEqual(self.check_saved('missing_module')['status'], 'SAVED_MODULE_MISSING_STOP')

    def test_missing_saved_resource_cannot_fall_back_to_original_checkout(self):
        self.unpack(omit='research/amn2/phase16-bot-maintenance-target-manifest-2026-09-30.json')
        self.assertEqual(self.check_saved('missing_resource')['status'], 'SAVED_RESOURCE_MISSING_STOP')


if __name__ == '__main__':
    unittest.main()
