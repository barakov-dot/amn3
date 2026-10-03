"""Real SQLite aggregates; OS read-only namespace is explicitly substituted."""
import hashlib
import contextlib
import importlib.util
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
AVAILABLE=importlib.util.find_spec('scripts.phase16_bot_pending_admission') is not None
if AVAILABLE:from scripts import phase16_bot_pending_admission as m

class Availability(unittest.TestCase):
    def test_pending_collector_exists(self):self.assertTrue(AVAILABLE)

@unittest.skipUnless(AVAILABLE,'availability fails first')
class PendingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'fixture.sqlite3'
        with contextlib.closing(sqlite3.connect(self.path)) as c:
            c.executescript("CREATE TABLE devices(status TEXT);CREATE TABLE admin_config_issuance_receipts(request_id TEXT,status TEXT);CREATE TABLE admin_config_issuance_requests(request_id TEXT,item_count INTEGER);")
    def run_read(self):
        with patch.object(m,'namespace_guard',lambda *args:None):
            return m.pending_snapshot(self.path,parent_mount_ns='mnt:[1]',parent_net_ns='net:[1]')
    def test_empty_counts_only_and_database_unchanged(self):
        before=self.path.read_bytes();v=self.run_read()
        self.assertEqual(v['counts'],dict(devices=0,issuance_receipts=0,issuance_requests=0))
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual(v['pending_operations'],'none_observed')
    def test_unfinished_receipt_and_request_are_not_hidden_by_no_pending_device(self):
        with contextlib.closing(sqlite3.connect(self.path)) as c:
            c.execute("INSERT INTO admin_config_issuance_requests VALUES('PRIVATE_ID',2)")
            c.execute("INSERT INTO admin_config_issuance_receipts VALUES('PRIVATE_ID','completed')");c.commit()
        v=self.run_read();self.assertEqual(v['pending_operations'],'present')
        self.assertEqual(v['counts']['issuance_requests'],1);self.assertNotIn('PRIVATE_ID',str(v))
    def test_guard_failure_precedes_any_database_open(self):
        with patch.object(m,'namespace_guard',side_effect=m.PendingError('namespace')),patch.object(m.sqlite3,'connect') as connect:
            with self.assertRaises(m.PendingError):m.pending_snapshot(self.path,parent_mount_ns='mnt:[1]',parent_net_ns='net:[1]')
            connect.assert_not_called()
    def test_views_cannot_supply_forged_empty_pending_counts(self):
        with contextlib.closing(sqlite3.connect(self.path)) as c:c.executescript("DROP TABLE devices;CREATE VIEW devices AS SELECT 'pending' AS status WHERE 0;")
        with self.assertRaises(m.PendingError):self.run_read()
    def test_child_command_is_fixed_isolated_readonly_scope(self):
        argv=m.child_command('/opt/phase16/code','mnt:[1]','net:[1]',expected_artifacts={'scripts/phase16_bot_pending_admission.py':'a'*64})
        self.assertEqual(argv[:5],['/usr/bin/unshare','--mount','--net','--propagation','private'])
        self.assertIn('-S',argv);self.assertIn('-B',argv)
        self.assertNotIn('restore',' '.join(argv));self.assertNotIn('TELEGRAM',' '.join(argv))

    def test_child_import_ignores_valid_stale_source_cache(self):
        import importlib.util,marshal,struct,subprocess,sys
        code=Path(self.tmp.name)/'code';source=code/'scripts/phase16_bot_pending_admission.py'
        source.parent.mkdir(parents=True)
        raw=b'def child_entry(*args):\n print("BOUND_SOURCE");return 0\n'
        source.write_bytes(raw);cache=Path(importlib.util.cache_from_source(str(source)));cache.parent.mkdir()
        stale=compile('def child_entry(*args):\n print("STALE_CACHE");return 0\n',str(source),'exec')
        cache.write_bytes(importlib.util.MAGIC_NUMBER+struct.pack('<III',0,int(source.stat().st_mtime),len(raw))+marshal.dumps(stale))
        argv=m.child_command('/fixture/code','mnt:[1]','net:[1]',expected_artifacts={'scripts/phase16_bot_pending_admission.py':hashlib.sha256(raw).hexdigest()})
        script=argv[argv.index('-c')+1].replace(repr('/fixture/code'),repr(code.as_posix()))
        result=subprocess.run([sys.executable,'-I','-S','-B','-c',script,'mnt:[1]','net:[1]'],capture_output=True,timeout=5)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),b'BOUND_SOURCE')

    def test_child_source_hash_mismatch_prevents_import(self):
        import subprocess,sys
        code=Path(self.tmp.name)/'bad-code';source=code/'scripts/phase16_bot_pending_admission.py'
        source.parent.mkdir(parents=True)
        source.write_text('print("UNBOUND_PENDING")\ndef child_entry(*args):return 0\n')
        argv=m.child_command('/fixture/code','mnt:[1]','net:[1]',expected_artifacts={'scripts/phase16_bot_pending_admission.py':'a'*64})
        script=argv[argv.index('-c')+1].replace(repr('/fixture/code'),repr(code.as_posix()))
        result=subprocess.run([sys.executable,'-I','-S','-B','-c',script,'mnt:[1]','net:[1]'],capture_output=True,timeout=5)
        self.assertNotEqual(result.returncode,0);self.assertNotIn(b'UNBOUND_PENDING',result.stdout)
        self.assertIn(b'bootstrap_hash',result.stderr)
