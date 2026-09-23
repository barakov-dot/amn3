"""Offline disposable SQLite tests; never opens application paths or networking."""
import contextlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from scripts import phase16_bot_db_rehearsal as db

FIXTURES = Path(__file__).parent / "fixtures/phase16_schema"

def populate_all_tables(conn):
    h='sha256:'+'a'*64
    rows={
        'devices':dict(user_id=1,server_id=1,name='fixture device',expiry_policy='indefinite',duration_days=None,vpn_ip='10.80.0.2',peer_public_key='synthetic-public',peer_private_key_encrypted=b'private-fixture-ciphertext',preshared_key_encrypted='synthetic-encrypted',config_version='amneziawg_v2'),
        'device_passports':dict(device_id='fixture-passport',local_device_id=1,owner_user_id=1,platform='windows',official_client_type='amneziawg',import_method='file',config_schema_version='2',config_fingerprint=h),
        'device_enrollment_tickets':dict(id='fixture-ticket',user_id=1,token_hash='synthetic-hash',token_prefix='fixture',platform='windows',config_schema_version='2',expires_at='2100-01-01 00:00:00',claimed_device_id='fixture-passport'),
        'device_lifecycle_events':dict(ticket_id='fixture-ticket',passport_device_id='fixture-passport',stage='claimed',status='completed',occurred_at='2026-01-01',duration_ms=1,evidence_json='{}'),
        'server_health_checks':dict(server_id=1,status='unknown'),
        'orders':dict(user_id=1,device_id=1,plan_id='days_3',payment_mode='synthetic'),
        'admin_actions':dict(admin_telegram_id=1,action='synthetic',target_user_id=1,target_device_id=1),
        'admin_config_issuance_requests':dict(request_id='fixture-request',request_fingerprint=h,item_count=1),
        'admin_config_issuance_receipts':dict(request_id='fixture-request',item_index=0,item_fingerprint=h,recipient_user_id=1,device_id=1,passport_device_id='fixture-passport',status='completed',config_filename='synthetic.conf',slot_sequence=1),
        'access_slot_assignment_requests':dict(request_id='fixture-assignment',request_fingerprint=h,local_device_id=1,passport_device_id='fixture-passport'),
        'device_traffic_snapshots':dict(device_id=1,server_id=1,peer_public_key='synthetic-public',rx_bytes=12,tx_bytes=13,source='synthetic',collected_at='2026-01-01'),
        'email_recovery_tokens':dict(user_id=1,email='fixture@example.invalid',token_hash='synthetic-hash',purpose='verify_email',device_id=1,expires_at='2100-01-01'),
        'api_tokens':dict(id='fixture-api',name='synthetic',owner_user_id=1,owner_label='fixture',token_hash='synthetic-api-hash',scopes_json='[]'),
        'ignored_remote_peers':dict(server_id=1,peer_public_key='synthetic-ignored',allowed_ips='10.80.0.3/32'),
    }
    for table,row in rows.items():
        conn.execute('INSERT INTO '+db.quote(table)+' ('+','.join(map(db.quote,row))+') VALUES ('+','.join('?' for _ in row)+')',tuple(row.values()))
    conn.commit()

class RehearsalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sources = db.Sources(FIXTURES)
        self.original = self.root / "original.sqlite"
        with contextlib.closing(sqlite3.connect(self.original)) as conn:
            conn.row_factory = sqlite3.Row
            self.sources.old(conn)
            conn.execute("INSERT INTO users(telegram_id,username) VALUES(1,'private-fixture-value')")
            repo = self.sources.old_repository(conn)
            repo.seed_default_plans()
            repo.ensure_default_server(name="local", network_cidr="10.80.0.0/24")
            conn.execute("UPDATE plans SET max_devices=7, updated_at='2000-01-01 00:00:00'")
            conn.execute("INSERT INTO message_templates(key,text) VALUES('x','private-template')")
            conn.commit()
        self.backup = self.root / "backup.sqlite"
        self.clone = self.root / "clone.sqlite"

    def run_rehearsal(self, **kw):
        return db.rehearse(self.original, self.backup, self.clone, self.sources,
                           network_cidr="10.80.0.0/24", **kw)

    def test_preserves_original_and_validates_candidate_repeat_and_old_repository(self):
        with contextlib.closing(sqlite3.connect(self.original)) as conn:
            populate_all_tables(conn)
            self.assertTrue(all(t['rows'] for t in db.snapshot(conn).values()))
        before = db.file_sha256(self.original)
        result = self.run_rehearsal()
        self.assertEqual(result["status"], "LOCAL_REHEARSAL_PASS")
        self.assertEqual(result["old_tables"], 18)
        self.assertEqual(result["candidate_tables"], 29)
        self.assertEqual(db.file_sha256(self.original), before)
        self.assertEqual(db.file_sha256(self.backup), result["backup_sha256"])
        self.assertNotIn("private-", json.dumps(result))
        with contextlib.closing(sqlite3.connect(self.clone)) as conn:
            self.assertEqual(conn.execute("SELECT max_devices FROM plans WHERE id='days_3'").fetchone()[0],7)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM awg3_control_state WHERE issuance_enabled=0").fetchone()[0],1)

    def test_missing_standard_seeds_and_local_server_are_created(self):
        with contextlib.closing(sqlite3.connect(self.original)) as conn, conn:
            conn.execute("DELETE FROM plans")
            conn.execute("DELETE FROM servers")
        self.assertEqual(self.run_rehearsal()["status"], "LOCAL_REHEARSAL_PASS")

    def test_custom_seed_stops_without_modifying_original(self):
        with contextlib.closing(sqlite3.connect(self.original)) as conn, conn:
            conn.execute("UPDATE plans SET price=9 WHERE id='days_3'")
        before=db.file_sha256(self.original)
        with self.assertRaisesRegex(db.Stop,'^seed_policy$'): self.run_rehearsal()
        self.assertEqual(before,db.file_sha256(self.original))

    def test_unknown_schema_is_rejected(self):
        with contextlib.closing(sqlite3.connect(self.original)) as conn, conn: conn.execute("CREATE TABLE extra(secret TEXT)")
        with self.assertRaisesRegex(db.Stop,'^old_schema$'): self.run_rehearsal()

    def test_sqlite_like_prefix_is_not_a_schema_exemption(self):
        with contextlib.closing(sqlite3.connect(self.original)) as conn, conn:
            conn.execute("CREATE TABLE sqliteXextra(secret TEXT)")
        with self.assertRaisesRegex(db.Stop,'^old_schema$'):self.run_rehearsal()

    def test_foreign_key_violation_is_rejected(self):
        with contextlib.closing(sqlite3.connect(self.original)) as conn, conn:
            conn.execute("INSERT INTO server_health_checks(server_id,status) VALUES(900,'unknown')")
        with self.assertRaisesRegex(db.Stop,'^foreign_keys$'): self.run_rehearsal()

    def test_backup_and_clone_paths_must_be_new(self):
        for path in (self.backup,self.clone):
            path.write_bytes(b'keep')
            with self.assertRaises(db.Stop): self.run_rehearsal()
            self.assertEqual(path.read_bytes(),b'keep')
            path.unlink()
            if self.backup.exists(): self.backup.unlink()

    def test_deadline_is_enforced(self):
        with self.assertRaisesRegex(db.Stop,'^deadline$'): self.run_rehearsal(limit_seconds=0)

    def test_wal_backup_includes_uncheckpointed_rows(self):
        with contextlib.closing(sqlite3.connect(self.original)) as writer:
            writer.execute('PRAGMA journal_mode=WAL')
            writer.execute("INSERT INTO message_templates(key,text) VALUES('wal','private-wal-fixture')");writer.commit()
            self.assertTrue(Path(str(self.original)+'-wal').exists())
            result=self.run_rehearsal()
            self.assertEqual(result['status'],'LOCAL_REHEARSAL_PASS')
            with contextlib.closing(sqlite3.connect(self.backup)) as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM message_templates WHERE key='wal'").fetchone()[0],1)

    def test_row_cap_stops_without_returning_values(self):
        with contextlib.closing(sqlite3.connect(self.original)) as conn:
            with self.assertRaisesRegex(db.Stop,'^row_cap$'):db.snapshot(conn,row_cap=1)

    def test_source_tamper_stops_before_compile(self):
        files=self.root/'sources';files.mkdir()
        for name in db.SOURCE_HASHES: (files/(name+'.txt')).write_bytes((FIXTURES/(name+'.txt')).read_bytes())
        (files/'candidate_schema.txt').write_text('raise RuntimeError("private-error")')
        with self.assertRaisesRegex(db.Stop,'^source_binding$'): db.Sources(files)

    def test_backup_hash_mismatch_stops(self):
        self.run_rehearsal()
        with self.assertRaisesRegex(db.Stop,'^backup_binding$'):
            db.check_backup(self.backup,'0'*64)

    def test_no_raw_database_error_or_rows_in_public_result(self):
        self.original.write_bytes(b'private-invalid-db')
        out=io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(out):
            result=db.safe_rehearse(self.original,self.backup,self.clone,self.sources,network_cidr='10.80.0.0/24')
        self.assertEqual(result,{'status':'STOP','reason':'sqlite_failure'})
        self.assertEqual(out.getvalue(),'')

class DeltaTests(unittest.TestCase):
    setUp = RehearsalTests.setUp
    def test_unexpected_old_value_delete_and_extra_row_are_rejected(self):
        for sql in ["UPDATE users SET username='changed'", "DELETE FROM message_templates",
                    "INSERT INTO message_templates(key,text) VALUES('new','bad')",
                    "UPDATE devices SET protocol_version='awg2'",
                    "INSERT INTO protocol_config_events(event_type,actor_kind,actor_id,reason,metadata_json) VALUES('x','system',1,'x','{}')",
                    "UPDATE awg3_control_state SET global_accepted=1"]:
            with self.subTest(sql=sql),contextlib.closing(sqlite3.connect(':memory:')) as conn:
                conn.row_factory=sqlite3.Row
                with contextlib.closing(sqlite3.connect(self.original)) as src: src.backup(conn)
                populate_all_tables(conn)
                before=db.snapshot(conn)
                self.sources.candidate(conn)
                self.sources.candidate_repository(conn).seed_default_plans()
                self.sources.candidate_repository(conn).ensure_default_server(name='local',network_cidr='10.80.0.0/24')
                conn.execute(sql);conn.commit()
                with self.assertRaises(db.Stop):
                    db.verify_delta(before,db.snapshot(conn),network_cidr='10.80.0.0/24',
                                    earliest='2000-01-01 00:00:00',latest='2100-01-01 00:00:00')

    def test_every_old_table_row_is_compared_including_encrypted_blob(self):
        import copy
        with contextlib.closing(sqlite3.connect(self.original)) as conn:
            populate_all_tables(conn);before=db.snapshot(conn)
        self.run_rehearsal = RehearsalTests.run_rehearsal.__get__(self)
        self.run_rehearsal()
        with contextlib.closing(sqlite3.connect(self.clone)) as conn:after=db.snapshot(conn)
        for table in before:
            if table=='sqlite_sequence':continue
            with self.subTest(table=table):
                changed=copy.deepcopy(after);changed[table]['rows'].pop(0)
                with self.assertRaises(db.Stop):db.verify_delta(before,changed,network_cidr='10.80.0.0/24',earliest='2000-01-01 00:00:00',latest='2100-01-01 00:00:00')

class RestoreTests(unittest.TestCase):
    setUp = RehearsalTests.setUp
    run_rehearsal = RehearsalTests.run_rehearsal

    def journal(self, start=False):
        from tests.test_phase16_bot_maintenance import manifest
        from scripts.phase16_bot_maintenance import Journal
        j=Journal.create(self.root/'journal',manifest())
        for action in ('fence','stop','backup','rehearsal','migrate'):
            j.perform(action,lambda:None,lambda:True)
        if start:
            try:j.perform('candidate_start',lambda:None,lambda:False)
            except db.Stop:pass
        return j

    def test_explicit_pre_poll_restore_preserves_failed_main_and_sidecars(self):
        result=self.run_rehearsal();j=self.journal()
        failed=self.clone.read_bytes()
        sidecar=Path(str(self.clone)+'-wal');sidecar.write_bytes(b'failed-sidecar')
        receipt=db.restore_before_start(self.clone,self.backup,result['backup_sha256'],self.root/'recovery',j,
                                       fence_continuous=True,drain_proven=True,same_boot=True)
        self.assertEqual(receipt['status'],'LOCAL_RESTORE_PASS')
        self.assertEqual((self.root/'recovery/failed.sqlite').read_bytes(),failed)
        self.assertEqual((self.root/'recovery/failed.sqlite-wal').read_bytes(),b'failed-sidecar')
        self.assertEqual(db.file_sha256(self.clone),result['backup_sha256'])
        with self.assertRaises(db.Stop):
            db.restore_before_start(self.clone,self.backup,result['backup_sha256'],self.root/'again',j,
                                    fence_continuous=True,drain_proven=True,same_boot=True)

    def test_candidate_requested_or_lost_fence_never_restore(self):
        result=self.run_rehearsal();j=self.journal(start=True);before=self.clone.read_bytes()
        with self.assertRaises(db.Stop):
            db.restore_before_start(self.clone,self.backup,result['backup_sha256'],self.root/'recovery',j,
                                    fence_continuous=True,drain_proven=True,same_boot=True)
        self.assertEqual(self.clone.read_bytes(),before)
        self.assertFalse((self.root/'recovery').exists())

if __name__=='__main__': unittest.main()
