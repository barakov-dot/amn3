"""Only disposable SQLite/files and local child processes; never the VPS."""
import contextlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from scripts import phase16_bot_db_rehearsal as db
from scripts import phase16_bot_maintenance as core
from tests.test_phase16_bot_maintenance import manifest
from tests.test_phase16_bot_db_rehearsal import populate_all_tables

NAME = "scripts.phase16_bot_maintenance_operations"
AVAILABLE = importlib.util.find_spec(NAME) is not None
if AVAILABLE:
    from scripts import phase16_bot_maintenance_operations as ops


class Availability(unittest.TestCase):
    def test_real_operations_exist(self):
        self.assertTrue(AVAILABLE, "T14c concrete data/service operations are missing")


@unittest.skipUnless(AVAILABLE, "implementation missing; Availability must fail")
class DataOperationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sources = db.Sources(Path(__file__).parent / "fixtures/phase16_schema")
        self.database = self.root / "live.sqlite3"
        with contextlib.closing(sqlite3.connect(self.database)) as conn:
            self.sources.old(conn)
            conn.row_factory = sqlite3.Row
            repo = self.sources.old_repository(conn)
            repo.seed_default_plans()
            repo.ensure_default_server(name="local", network_cidr="10.80.0.0/24")
            conn.execute("INSERT INTO users(telegram_id,username) VALUES(1,'private-fixture')")
            conn.commit()
            populate_all_tables(conn)
        self.journal = core.Journal.create(self.root / "journal", manifest())
        self.data = ops.DataOperations(self.database, self.root, self.journal,
                                       self.sources, "10.80.0.0/24")
        for action in ("fence", "stop"):
            self.journal.perform(action, lambda: None, lambda: True)

    def step(self, action):
        self.journal.perform(action, getattr(self.data, action),
                             lambda: self.data.verify(action))

    def ready_to_migrate(self):
        self.step("backup")
        self.step("rehearsal")

    def test_real_backup_rehearsal_and_migration_preserve_old_rows(self):
        original = db.file_sha256(self.database)
        self.ready_to_migrate()
        self.assertEqual(db.file_sha256(self.database), original)
        backup = db.file_sha256(self.root / "backup.sqlite3")
        self.step("migrate")
        with contextlib.closing(sqlite3.connect(self.database)) as conn:
            self.assertEqual(db.shape(conn), self.sources.candidate_shape)
            self.assertEqual(conn.execute("SELECT username FROM users").fetchall(), [("private-fixture",)])
            self.assertEqual(conn.execute("SELECT issuance_enabled FROM awg3_control_state").fetchall(), [(0,)])
        self.assertEqual(db.file_sha256(self.root / "backup.sqlite3"), backup)
        receipts = [json.loads(p.read_text()) for p in (self.root / "receipts").glob("*.json")]
        self.assertEqual(len(receipts), 3)
        self.assertNotIn("private-fixture", json.dumps(receipts))

    def test_direct_data_operation_without_durable_intent_is_rejected(self):
        with self.assertRaisesRegex(db.Stop, "operation_intent"):
            self.data.backup()
        self.assertFalse((self.root / "backup.sqlite3").exists())

    def test_changed_source_after_backup_blocks_migration_before_write(self):
        self.ready_to_migrate()
        with contextlib.closing(sqlite3.connect(self.database)) as conn, conn:
            conn.execute("UPDATE users SET username='concurrent-fixture'")
        changed = db.file_sha256(self.database)
        with self.assertRaisesRegex(db.Stop, "source_changed"):
            self.step("migrate")
        self.assertEqual(db.file_sha256(self.database), changed)
        self.assertEqual(self.journal.phase, "migrate_intent")

    def test_partial_issuance_blocks_backup_without_mutation(self):
        with contextlib.closing(sqlite3.connect(self.database)) as conn, conn:
            conn.execute("UPDATE admin_config_issuance_receipts SET status='partial_failure', error_code='synthetic'")
        original = db.file_sha256(self.database)
        with self.assertRaisesRegex(db.Stop, "pending_operations"):
            self.step("backup")
        self.assertEqual(db.file_sha256(self.database), original)
        self.assertFalse((self.root / "backup.sqlite3").exists())

    def test_request_with_missing_receipt_is_not_complete(self):
        with contextlib.closing(sqlite3.connect(self.database)) as conn, conn:
            conn.execute("DELETE FROM admin_config_issuance_receipts")
        with self.assertRaisesRegex(db.Stop, "pending_operations"):
            self.step("backup")

    def test_pending_device_is_not_complete(self):
        with contextlib.closing(sqlite3.connect(self.database)) as conn, conn:
            conn.execute("UPDATE devices SET status='pending'")
        with self.assertRaisesRegex(db.Stop, "pending_operations"):
            self.step("backup")

    def test_corrupt_backup_or_receipt_never_migrates(self):
        for artifact in ("backup.sqlite3", "receipts/rehearsal.json"):
            with self.subTest(artifact=artifact):
                # A new private operation per case, never reset/replay a live journal.
                if artifact != "backup.sqlite3":
                    self.tearDown()
                    self.setUp()
                self.ready_to_migrate()
                path = self.root / artifact
                path.write_bytes(path.read_bytes() + b"tamper")
                original = db.file_sha256(self.database)
                with self.assertRaises(db.Stop):
                    self.step("migrate")
                self.assertEqual(db.file_sha256(self.database), original)

    def test_failed_migration_retains_database_backup_and_manual_route(self):
        self.ready_to_migrate()
        original_candidate = self.sources.candidate
        def fail_after_schema(conn):
            original_candidate(conn)
            raise RuntimeError("private-error")
        self.sources.candidate = fail_after_schema
        with self.assertRaisesRegex(db.Stop, "action_failed"):
            self.step("migrate")
        self.assertEqual(self.journal.phase, "migrate_intent")
        self.assertTrue(self.database.exists())
        self.assertTrue((self.root / "backup.sqlite3").exists())
        self.assertFalse((self.root / "receipts/migrate.json").exists())
        self.assertEqual(core.recovery_route(self.journal, fence_continuous=True,
            drain_proven=True, backup_verified=True, same_boot=True), "RESTORE_REQUIRES_APPROVAL")

    def test_wal_only_change_after_migration_is_detected(self):
        with contextlib.closing(sqlite3.connect(self.database)) as keeper:
            keeper.execute('PRAGMA journal_mode=WAL')
            self.ready_to_migrate()
            self.step('migrate')
            main_hash = db.file_sha256(self.database)
            keeper.execute("UPDATE users SET username='later-wal-fixture'")
            keeper.commit()
            self.assertEqual(db.file_sha256(self.database), main_hash)
            with self.assertRaisesRegex(db.Stop, 'source_changed'):
                self.data.verify('migrate')

    def test_wrong_phase_receipt_is_rejected(self):
        self.ready_to_migrate()
        path = self.root / "receipts/rehearsal.json"
        value = json.loads(path.read_text())
        value["action"] = "backup"
        path.write_bytes(core.encoded(value))
        with self.assertRaises(db.Stop):
            self.step("migrate")

if __name__ == "__main__":
    unittest.main()
