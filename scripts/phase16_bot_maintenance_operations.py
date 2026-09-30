"""Concrete private-data operations for the Phase16 maintenance coordinator.

No live entry point. A Linux runner must establish authorization, exclusive writer
ownership, a continuous effective fence and drain BEFORE calling these operations.
OS isolation/deadlines belong to the runner; this module never claims those facts.
Only pinned schema/repository slices execute, never application configuration.
"""
import contextlib
import ipaddress
import json
import os
from pathlib import Path
import sqlite3
import stat
import time

from scripts import phase16_bot_db_rehearsal as db
from scripts import phase16_bot_maintenance as core

Stop, require = db.Stop, db.require


def pending_counts(conn):
    """Aggregate old-schema persisted work only; NOT in-memory handler drain.

    Orders awaiting manual review/payment are business state, not active workers.
    An issuance request without all completed receipts is unresolved even when
    no individual receipt remains in 'started'. No identifiers/rows leave here.
    """
    return {
        'devices': conn.execute("SELECT count(*) FROM devices WHERE status='pending'").fetchone()[0],
        'issuance_receipts': conn.execute(
            "SELECT count(*) FROM admin_config_issuance_receipts WHERE status <> 'completed'").fetchone()[0],
        'issuance_requests': conn.execute(
            "SELECT count(*) FROM admin_config_issuance_requests q WHERE q.item_count <> "
            "(SELECT count(*) FROM admin_config_issuance_receipts r "
            "WHERE r.request_id=q.request_id AND r.status='completed')").fetchone()[0],
    }


def regular(path):
    path = db._check_path(path)
    value = path.stat()
    require(stat.S_ISREG(value.st_mode) and value.st_nlink == 1, 'data_path')
    return path


def database_fingerprint(path):
    # The WAL may contain committed pages while the main file is unchanged.
    # SHM contains coordination/read marks, not authoritative SQLite row pages.
    result = {}
    for suffix in ('', '-wal', '-journal'):
        file = db._check_path(str(path) + suffix)
        if file.exists():
            regular(file)
            # A read-only SQLite open may create a zero-byte WAL. It carries
            # no committed pages and is equivalent to absence for data binding.
            result[suffix or 'main'] = (None if suffix and file.stat().st_size == 0
                                       else db.file_sha256(file))
        else:
            result[suffix or 'main'] = None
    require(result['main'] is not None, 'data_path')
    return result


class DataOperations:
    """Real SQLite/file effects guarded by the existing durable action intent.

    The directory is private and new for this operation. All failed artifacts are
    retained. Receipts bind the journal, phase intent and predecessor, rather than
    accepting a caller's 'PASS' boolean. They contain no row data.
    """
    def __init__(self, database, directory, journal, sources, network_cidr, *, seconds=120):
        self.database = regular(database)
        self.directory = db._check_path(directory)
        require(self.directory.is_dir() and isinstance(journal, core.Journal), 'data_path')
        require(journal.directory.parent == self.directory, 'data_path')
        if os.name == 'posix':
            metadata = self.directory.stat()
            require(metadata.st_uid == os.geteuid() and not stat.S_IMODE(metadata.st_mode) & 0o077,
                    'private_directory')
        require(isinstance(seconds, int) and not isinstance(seconds, bool) and 1 <= seconds <= 120, 'deadline')
        self.seconds = seconds
        self.journal = journal
        self.sources = sources
        self.network_cidr = str(ipaddress.ip_network(network_cidr, strict=True))
        self.backup_path = self.directory / 'backup.sqlite3'
        self.clone = self.directory / 'rehearsal.sqlite3'
        self.receipts = self.directory / 'receipts'
        for path in (self.backup_path, self.clone):
            require(path != self.database, 'data_path')

    def intent(self, action):
        fresh = core.Journal.load(self.journal.directory, self.journal.manifest)
        require(fresh.events == self.journal.events and fresh.phase == action + '_intent'
                and (fresh.directory / 'execution.lock').is_file()
                and not (fresh.directory / 'recovery').exists(), 'operation_intent')
        regular(self.database)
        require(not (self.receipts / (action + '.json')).exists(), 'receipt_exists')

    def read_receipt(self, action):
        path = regular(self.receipts / (action + '.json'))
        require(path.stat().st_size <= 4096, 'receipt_size')
        try:
            raw = path.read_bytes()
            value = json.loads(raw)
            require(raw == core.encoded(value), 'receipt_encoding')
            require(set(value) == {'schema', 'action', 'binding', 'intent_sha256',
                                  'predecessor_sha256', 'details', 'sha256'}, 'receipt_shape')
            payload = {k: v for k, v in value.items() if k != 'sha256'}
            intent = next(e for e in self.journal.events if e['phase'] == action + '_intent')
            require(value['schema'] == 'phase16.maintenance-data.v1' and value['action'] == action
                    and value['binding'] == self.journal.binding
                    and value['intent_sha256'] == intent['sha256']
                    and value['sha256'] == core.digest(payload), 'receipt_binding')
            if action != 'backup':
                previous = 'backup' if action == 'rehearsal' else 'rehearsal'
                require(value['predecessor_sha256'] == self.read_receipt(previous)['sha256'], 'receipt_predecessor')
            else:
                require(value['predecessor_sha256'] is None, 'receipt_predecessor')
            return value
        except (ValueError, KeyError, TypeError, StopIteration):
            raise Stop('receipt_binding') from None

    def save(self, action, details):
        self.receipts.mkdir(mode=0o700, exist_ok=True)
        db._check_path(self.receipts)
        previous = None if action == 'backup' else self.read_receipt(
            'backup' if action == 'rehearsal' else 'rehearsal')['sha256']
        payload = dict(schema='phase16.maintenance-data.v1', action=action,
                       binding=self.journal.binding, intent_sha256=self.journal.events[-1]['sha256'],
                       predecessor_sha256=previous, details=details)
        core.write_new(self.receipts / (action + '.json'), core.encoded(dict(payload, sha256=core.digest(payload))))

    def old_state(self, path, deadline):
        with contextlib.closing(db._read(regular(path))) as conn:
            conn.set_progress_handler(lambda: int(time.monotonic() >= deadline), 1000)
            db._tick(deadline)
            require(db.shape(conn) == self.sources.old_shape, 'old_schema')
            db.check_integrity(conn)
            require(not any(pending_counts(conn).values()), 'pending_operations')
            result = db.snapshot(conn)
            db.seed_precondition(result)
            return result

    def backup(self):
        self.intent('backup')
        deadline = time.monotonic() + self.seconds
        before = self.old_state(self.database, deadline)
        backup_hash = db.online_backup(self.database, self.backup_path, deadline=deadline)
        require(self.old_state(self.backup_path, deadline) == before
                and self.old_state(self.database, deadline) == before, 'source_changed')
        db.check_backup(self.backup_path, backup_hash)
        self.save('backup', dict(backup_sha256=backup_hash, pending_counts=dict.fromkeys(pending_counts_keys(), 0)))

    def rehearsal(self):
        self.intent('rehearsal')
        receipt = self.read_receipt('backup')
        backup_hash = receipt['details']['backup_sha256']
        db.check_backup(self.backup_path, backup_hash)
        # Frozen helper creates a second private base copy and a writable clone.
        # It never reopens the production database for writing.
        result = db.rehearse(self.backup_path, self.directory / 'rehearsal-base.sqlite3',
                            self.clone, self.sources, network_cidr=self.network_cidr,
                            limit_seconds=self.seconds)
        require(result['status'] == 'LOCAL_REHEARSAL_PASS', 'rehearsal_failed')
        db.check_backup(self.backup_path, backup_hash)
        self.save('rehearsal', dict(backup_sha256=backup_hash, clone_sha256=result['clone_sha256'],
                                  old_tables=result['old_tables'], candidate_tables=result['candidate_tables']))

    def migrate(self):
        self.intent('migrate')
        rehearsal = self.read_receipt('rehearsal')['details']
        backup_hash = self.read_receipt('backup')['details']['backup_sha256']
        require(rehearsal['backup_sha256'] == backup_hash, 'receipt_binding')
        db.check_backup(self.backup_path, backup_hash)
        db.check_backup(self.clone, rehearsal['clone_sha256'])
        deadline = time.monotonic() + self.seconds
        before = self.old_state(self.backup_path, deadline)
        require(self.old_state(self.database, deadline) == before, 'source_changed')
        metadata = regular(self.database).stat()
        # mode=rw prevents accidental creation at a wrong/missing source path.
        with contextlib.closing(sqlite3.connect(self.database.as_uri() + '?mode=rw', uri=True, timeout=1)) as conn:
            conn.execute('PRAGMA foreign_keys=ON')
            conn.set_progress_handler(lambda: int(time.monotonic() >= deadline), 1000)
            require(db.shape(conn) == self.sources.old_shape and db.snapshot(conn) == before, 'source_changed')
            earliest = conn.execute("SELECT datetime('now')").fetchone()[0]
            self.sources.candidate(conn)
            conn.row_factory = sqlite3.Row
            repo = self.sources.candidate_repository(conn)
            repo.seed_default_plans()
            repo.ensure_default_server(name='local', network_cidr=self.network_cidr)
            conn.row_factory = None
            latest = conn.execute("SELECT datetime('now')").fetchone()[0]
            require(db.shape(conn) == self.sources.candidate_shape, 'candidate_schema')
            db.verify_delta(before, db.snapshot(conn), network_cidr=self.network_cidr,
                            earliest=earliest, latest=latest)
            db.check_integrity(conn)
            db._tick(deadline)
        current = regular(self.database).stat()
        require((metadata.st_uid, metadata.st_gid, stat.S_IMODE(metadata.st_mode), metadata.st_ino) ==
                (current.st_uid, current.st_gid, stat.S_IMODE(current.st_mode), current.st_ino), 'database_metadata')
        db.check_backup(self.backup_path, backup_hash)
        self.save('migrate', dict(backup_sha256=backup_hash, earliest=earliest, latest=latest,
                                  database_fingerprint=database_fingerprint(self.database)))

    def verify(self, action):
        require(action in ('backup', 'rehearsal', 'migrate'), 'data_action')
        receipt = self.read_receipt(action)['details']
        db.check_backup(self.backup_path, receipt['backup_sha256'])
        if action == 'rehearsal':
            db.check_backup(self.clone, receipt['clone_sha256'])
        if action == 'migrate':
            require(database_fingerprint(self.database) == receipt['database_fingerprint'], 'source_changed')
            with contextlib.closing(db._read(self.database)) as conn:
                require(db.shape(conn) == self.sources.candidate_shape, 'candidate_schema')
                db.check_integrity(conn)
            require(database_fingerprint(self.database) == receipt['database_fingerprint'], 'source_changed')
        return True


def pending_counts_keys():
    return ('devices', 'issuance_receipts', 'issuance_requests')
