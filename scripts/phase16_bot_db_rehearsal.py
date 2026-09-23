"""Bounded, server-local SQLite rehearsal building block; no production CLI.

Only callers with separately approved local-data scope may supply real DB paths.
Source snapshots are pinned, not application imports. No env/token/network access.
Public receipts contain fixed reasons/counts/artifact hashes, never row material.
"""
import builtins
from collections import Counter
import contextlib
import hashlib
import ipaddress
import os
from pathlib import Path
import sqlite3
import time
import types

SOURCE_HASHES = {
    'old_schema': 'f3e353f17131d0fc606ee557d752bcadf55201360b69427c4e785f074f1c72f7',
    'candidate_schema': '45105b725e22a9cdbbc07bf440502b1738134f7f2ce875b45bb27aeace7266f1',
    'candidate_phase14': '85f84dda68d77fd91805fe80b6b161d2971ec206c6a0db3895cf11873e9be1d2',
    'candidate_phase15': '76a4f579a39e94e4360abeb894f820321c11e16f0e971ce37de8e4e737a989a9',
    'old_repository_slice': 'c4c0bd43003821e4aec428f810e1cb7e2f716b483478f8ef966fc748eaa76b56',
    'candidate_repository_slice': '85981818f46cfbeff986f8d6f493f6be3f75c1c2d8b35fa449bce1fc341a50f5',
}
DAYS = (3, 7, 10, 14, 30, 60, 90, 180)
PLAN_IDS = {f'days_{n}' for n in DAYS}
NEW_COLUMNS = {
    'devices': {'protocol_version','runtime_instance_id','client_identity_evidence_status','compatibility_evidence_id'},
    'device_passports': {'protocol_version','runtime_instance_id','client_identity_evidence_status','compatibility_evidence_id'},
    'admin_config_issuance_receipts': {'config_version','protocol_version','runtime_instance_id','compatibility_evidence_id','client_application','client_platform','client_version','client_build'},
}
NEW_TABLES = {'awg3_control_state','client_build_acceptances','client_compatibility_evidence',
              'device_protocol_profiles','legacy_migration_records','protocol_config_events',
              'protocol_issuance_attempts','protocol_issuance_confirmations',
              'protocol_issuance_user_barriers','telegram_callback_handles','vpn_runtime_instances'}

class Stop(Exception):
    """Only literal, non-sensitive reason codes may cross the public boundary."""


def require(condition, reason):
    if not condition: raise Stop(reason)


class Sources:
    def __init__(self, directory):
        data = {}
        for name, expected in SOURCE_HASHES.items():
            raw = (Path(directory) / (name + '.txt')).read_bytes().replace(b'\r\n', b'\n')
            require(hashlib.sha256(raw).hexdigest() == expected, 'source_binding')
            data[name] = raw
        modules = {}
        def importer(name, globals=None, locals=None, fromlist=(), level=0):
            if name in modules: return modules[name]
            require(level == 0 and name in {'sqlite3','ipaddress','typing'}, 'source_import')
            return builtins.__import__(name, globals, locals, fromlist, level)
        for name in ('candidate_phase14','candidate_phase15','old_schema','candidate_schema',
                     'old_repository_slice','candidate_repository_slice'):
            module = types.ModuleType(name)
            module.__dict__['__builtins__'] = dict(vars(builtins), __import__=importer)
            exec(compile(data[name], name, 'exec'), module.__dict__)
            modules[name] = module
            if name.startswith('candidate_phase'):
                modules['app.db.' + name.replace('candidate_', '').replace('phase14','phase14_dual_protocol').replace('phase15','phase15_bootstrap')] = module
        self.old = modules['old_schema'].initialize_schema
        self.candidate = modules['candidate_schema'].initialize_schema
        self.old_repository = modules['old_repository_slice'].Repository
        self.candidate_repository = modules['candidate_repository_slice'].Repository
        with contextlib.closing(sqlite3.connect(':memory:')) as conn:
            self.old(conn)
            self.old_shape = shape(conn)
            self.old_tables = set(snapshot(conn))
            self.candidate(conn)
            self.candidate_shape = shape(conn)


def quote(name):
    return '"' + name.replace('"','""') + '"'


def shape(conn):
    # SQL text stays in memory; strict baseline, including constraints/triggers.
    return tuple(conn.execute("SELECT type,name,tbl_name,sql FROM sqlite_schema "
                              "WHERE name NOT GLOB 'sqlite_*' ORDER BY type,name").fetchall())


def snapshot(conn, row_cap=200000):
    result = {}; total = 0
    for (name,) in conn.execute("SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name"):
        columns = tuple(r[1] for r in conn.execute('PRAGMA table_info(' + quote(name) + ')'))
        rows = conn.execute('SELECT * FROM ' + quote(name)).fetchmany(row_cap + 1 - total)
        total += len(rows)
        require(total <= row_cap, 'row_cap')
        result[name] = {'columns':columns, 'rows':[dict(zip(columns,r)) for r in rows]}
    return result


def _typed(row, columns):
    return tuple((type(row[c]).__name__,row[c]) for c in columns)


def _multiset(rows, columns):
    return Counter(_typed(r,columns) for r in rows)


def _timestamp(value, earliest, latest):
    return isinstance(value,str) and len(value)==19 and earliest <= value <= latest


def _plan(row):
    for n in DAYS:
        if row['id']==f'days_{n}':
            return all(row[k]==v for k,v in dict(name=f'{n} days',duration_days=n,price=0,
                                                 currency='RUB',is_free=1,is_active=1).items())
    return False


def seed_precondition(before):
    require(all(_plan(r) for r in before['plans']['rows'] if r['id'] in PLAN_IDS), 'seed_policy')


def verify_delta(before, after, *, network_cidr, earliest, latest):
    """The exact 55dc -> 6e first-start delta. No general backfill allowance."""
    require(set(after)-set(before)==NEW_TABLES and set(before)<=set(after), 'table_delta')
    seed_precondition(before)
    for table, state in before.items():
        if table=='sqlite_sequence': continue
        new = after[table]
        added = set(new['columns'])-set(state['columns'])
        require(set(state['columns'])<=set(new['columns']) and added==NEW_COLUMNS.get(table,set()), 'column_delta')
        require(all(all(r[c] is None for c in added) for r in new['rows']), 'backfill_delta')
        oldrows = state['rows']; newrows = new['rows']; columns = state['columns']
        if table=='plans':
            oldids = {r['id'] for r in oldrows}
            require({r['id'] for r in newrows}==oldids|PLAN_IDS, 'plan_delta')
            for row in newrows:
                if row['id'] in PLAN_IDS:
                    require(_plan(row) and _timestamp(row['updated_at'],earliest,latest), 'seed_delta')
                    if row['id'] not in oldids:
                        require(row['max_devices'] is None and _timestamp(row['created_at'],earliest,latest), 'seed_delta')
            def normalize(rows):
                return [dict(r,updated_at=None) if r['id'] in PLAN_IDS else r for r in rows]
            require(_multiset(normalize(oldrows),columns)==_multiset(normalize([r for r in newrows if r['id'] in oldids]),columns), 'old_data_delta')
        elif table=='servers':
            oldids={r['id'] for r in oldrows}
            require(_multiset(oldrows,columns)==_multiset([r for r in newrows if r['id'] in oldids],columns), 'old_data_delta')
            extra=[r for r in newrows if r['id'] not in oldids]
            require(len(extra)==(0 if any(r['name']=='local' for r in oldrows) else 1), 'server_delta')
            if extra:
                row=extra[0]; network=ipaddress.ip_network(network_cidr,strict=False)
                expected=dict(name='local',host='local',ssh_port=22,endpoint_host='127.0.0.1',vpn_port=30001,
                              vpn_network_cidr=network_cidr,server_address=str(next(network.hosts(),network.network_address)),
                              server_public_key='local-server-public-key',runtime='host_systemd',firewall='ufw',
                              status='active',max_devices=254,current_devices=0)
                require(all(row[k]==v for k,v in expected.items()), 'server_delta')
                require(all(_timestamp(row[k],earliest,latest) for k in ('created_at','updated_at')), 'server_delta')
        else:
            require(_multiset(oldrows,columns)==_multiset(newrows,columns), 'old_data_delta')
    for table in NEW_TABLES-{'awg3_control_state'}:
        require(not after[table]['rows'], 'new_data_delta')
    control=after['awg3_control_state']['rows']
    require(len(control)==1, 'control_delta')
    expected=dict(singleton_id=1,runtime_accepted=0,global_accepted=0,issuance_enabled=0,
                  emergency_suspended=0,runtime_receipt=None,actor_id=None,reason=None)
    require(all(control[0][k]==v for k,v in expected.items()) and
            _timestamp(control[0]['updated_at'],earliest,latest), 'control_delta')
    # INSERT ... ON CONFLICT DO NOTHING still consumes a servers AUTOINCREMENT id.
    seq=lambda state: {r['name']:r['seq'] for r in state.get('sqlite_sequence',{}).get('rows',[])}
    oldseq,newseq=seq(before),seq(after)
    expectedseq=dict(oldseq)
    expectedseq['servers']=max(oldseq.get('servers',0),max((r['id'] for r in before['servers']['rows']),default=0))+1
    require(newseq==expectedseq, 'sequence_delta')


def check_integrity(conn):
    require(conn.execute('PRAGMA integrity_check').fetchall()==[('ok',)], 'integrity')
    require(not conn.execute('PRAGMA foreign_key_check').fetchone(), 'foreign_keys')


def file_sha256(path):
    digest=hashlib.sha256()
    with open(path,'rb') as stream:
        for block in iter(lambda:stream.read(1024*1024), b''): digest.update(block)
    return digest.hexdigest()


def _check_path(path):
    path=Path(path)
    require(path.is_absolute(), 'absolute_path')
    require(not path.is_symlink() and not any(p.is_symlink() for p in path.parents), 'symlink_path')
    return path


def _read(path):
    conn=sqlite3.connect(_check_path(path).as_uri()+'?mode=ro',uri=True,timeout=1)
    return conn


def _tick(deadline):
    require(time.monotonic()<deadline, 'deadline')


def online_backup(source, target, *, deadline):
    """New restricted file only; failed artifacts retained, never reused/removed."""
    _tick(deadline)
    source,target=_check_path(source),_check_path(target)
    require(source!=target and source.is_file(), 'backup_path')
    require(not any(Path(str(target)+s).exists() for s in ('','-wal','-shm','-journal')), 'destination_exists')
    try:
        fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError: raise Stop('destination_exists') from None
    os.close(fd)
    with contextlib.closing(_read(source)) as src, contextlib.closing(sqlite3.connect(target,timeout=1)) as dst:
        src.backup(dst,pages=64,progress=lambda status,remaining,total:_tick(deadline),sleep=0.05)
        dst.commit()
        # Normalize only the newly created closed snapshot, never the source.
        # A standalone artifact must not rely on WAL sidecars after API backup.
        require(dst.execute('PRAGMA journal_mode=DELETE').fetchone()==('delete',),'backup_journal')
        dst.set_progress_handler(lambda: int(time.monotonic()>=deadline),1000)
        _tick(deadline)
        check_integrity(dst)
    with open(target,'r+b') as stream: os.fsync(stream.fileno())
    return file_sha256(target)


def check_backup(path, expected):
    require(file_sha256(_check_path(path))==expected, 'backup_binding')
    require(not any(Path(str(path)+s).exists() for s in ('-wal','-shm','-journal')), 'backup_sidecar')
    with contextlib.closing(_read(path)) as conn: check_integrity(conn)


def rehearse(source, backup, clone, sources, *, network_cidr, limit_seconds=120):
    """Never mutates source; creates backup and disposable clone, both retained.

    The source must already be fenced by its owner; this function proves no fence.
    A future live runner must enforce network isolation, private parent directory,
    OS wall deadline and approval outside this in-process building block.
    """
    require(isinstance(limit_seconds,(int,float)) and 0<limit_seconds<=600, 'deadline')
    deadline=time.monotonic()+limit_seconds
    require(len({str(_check_path(p)) for p in (source,backup,clone)})==3, 'backup_path')
    require(not Path(clone).exists(), 'destination_exists')
    ipaddress.ip_network(network_cidr,strict=False)
    backup_hash=online_backup(source,backup,deadline=deadline)
    check_backup(backup,backup_hash)
    online_backup(backup,clone,deadline=deadline)
    with contextlib.closing(sqlite3.connect(clone,timeout=1)) as conn:
        conn.execute('PRAGMA foreign_keys=ON')
        conn.set_progress_handler(lambda: int(time.monotonic()>=deadline),1000)
        require(shape(conn)==sources.old_shape, 'old_schema')
        before=snapshot(conn)
        require(set(before)==sources.old_tables,'old_schema')
        seed_precondition(before)
        earliest=conn.execute("SELECT datetime('now')").fetchone()[0]
        sources.candidate(conn)
        # Exact repository methods expect sqlite3.Row; snapshots use tuple rows.
        conn.row_factory=sqlite3.Row
        repo=sources.candidate_repository(conn)
        repo.seed_default_plans();repo.ensure_default_server(name='local',network_cidr=network_cidr)
        conn.row_factory=None
        latest=conn.execute("SELECT datetime('now')").fetchone()[0]
        require(shape(conn)==sources.candidate_shape, 'candidate_schema')
        verify_delta(before,snapshot(conn),network_cidr=network_cidr,earliest=earliest,latest=latest)
        check_integrity(conn)
        candidate=snapshot(conn)
        sources.candidate(conn)
        require(snapshot(conn)==candidate and shape(conn)==sources.candidate_shape, 'repeat_delta')
        # The exact old web _open_repository path: old init + Repository.
        sources.old(conn)
        require(snapshot(conn)==candidate and shape(conn)==sources.candidate_shape, 'old_web_delta')
        conn.row_factory=sqlite3.Row
        old=sources.old_repository(conn)
        require(old.get_plan('days_3')['duration_days']==3, 'old_repository')
        smoke='phase16_rehearsal_synthetic_plan'
        require(not conn.execute('SELECT 1 FROM plans WHERE id=?',(smoke,)).fetchone(), 'smoke_collision')
        old.upsert_plan(plan_id=smoke,name='Phase16 synthetic',duration_days=1)
        require(old.get_plan(smoke)['duration_days']==1, 'old_repository')
        conn.execute('DELETE FROM plans WHERE id=?',(smoke,));conn.commit();conn.row_factory=None
        require(snapshot(conn)==candidate, 'smoke_delta')
        check_integrity(conn);_tick(deadline)
    check_backup(backup,backup_hash)
    return dict(status='LOCAL_REHEARSAL_PASS',old_tables=len(before)-1,
                candidate_tables=len(candidate)-1,backup_sha256=backup_hash,
                clone_sha256=file_sha256(clone),source_binding='PINNED',
                writer_fence='NOT_PROVEN_BY_HELPER',production_migration='NOT_EXECUTED')


def safe_rehearse(*args,**kwargs):
    try: return rehearse(*args,**kwargs)
    except Stop as exc: return {'status':'STOP','reason':str(exc)}
    except sqlite3.Error: return {'status':'STOP','reason':'sqlite_failure'}
    except (OSError,ValueError): return {'status':'STOP','reason':'input_or_io_failure'}
    except Exception: return {'status':'STOP','reason':'helper_failure'}


def _restore_locked(database, backup, backup_hash, archive, journal, *,
                         fence_continuous, drain_proven, same_boot):
    """Explicit, never automatic. Caller still needs exact live/data approval.

    Preserves all failed DB files in a new archive; any partial restore stays fenced.
    The durable recovery claim blocks forward journal progress and a second restore.
    No services are started here. Metadata comes from failed main DB, not backup.
    """
    from scripts.phase16_bot_maintenance import Journal, recovery_route, write_new, sync_directory, encoded
    import shutil
    import stat
    fresh=Journal.load(journal.directory,journal.manifest)
    require(fresh.phase==journal.phase,'journal_binding')
    check_backup(backup,backup_hash)
    require(recovery_route(fresh,fence_continuous=fence_continuous,drain_proven=drain_proven,
                           backup_verified=True,same_boot=same_boot)=='RESTORE_REQUIRES_APPROVAL','restore_forbidden')
    database,backup,archive=(_check_path(p) for p in (database,backup,archive))
    require(database!=backup and database.is_file() and not archive.exists(),'restore_path')
    metadata=database.stat()
    require(stat.S_ISREG(metadata.st_mode) and metadata.st_nlink==1,'restore_path')
    paths=[Path(str(database)+s) for s in ('','-wal','-shm','-journal')]
    for path in paths:
        _check_path(path)
        require(not path.exists() or (path.is_file() and path.stat().st_nlink==1),'restore_path')
    require(archive.parent.stat().st_dev==database.parent.stat().st_dev,'restore_filesystem')
    recovery=journal.directory/'recovery'
    require(not recovery.exists(),'recovery_started')
    recovery.mkdir(mode=0o700);sync_directory(recovery.parent)
    write_new(recovery/'intent.json',encoded(dict(phase='restore_intent',database=str(database),
                                                   backup=str(backup),backup_sha256=backup_hash,archive=str(archive))))
    archive.mkdir(mode=0o700);sync_directory(archive.parent)
    staged=archive/'restored.sqlite'
    # Backup is closed/validated with no sidecars: copying this artifact is safe.
    write_new(staged,b'')
    with open(backup,'rb') as src,open(staged,'r+b') as dst:
        shutil.copyfileobj(src,dst);dst.flush();os.fsync(dst.fileno())
        if os.name=='posix':os.fchown(dst.fileno(),metadata.st_uid,metadata.st_gid)
        os.chmod(staged,stat.S_IMODE(metadata.st_mode))
        os.fsync(dst.fileno())
    check_backup(staged,backup_hash)
    for number,path in enumerate(paths):
        if path.exists():
            destination=archive/('failed.sqlite'+str(path)[len(str(database)):])
            write_new(recovery/f'{number:02d}-intent.json',b'{"phase":"preserve_failed_file"}\n')
            path.rename(destination);sync_directory(path.parent);sync_directory(archive)
    require(not database.exists(),'restore_path')
    staged.rename(database);sync_directory(database.parent);sync_directory(archive)
    check_backup(database,backup_hash)
    write_new(recovery/'complete.json',b'{"phase":"restore_complete_no_restart"}\n')
    return {'status':'LOCAL_RESTORE_PASS','backup_sha256':backup_hash,'runtime_restart':'NOT_EXECUTED'}


def restore_before_start(database, backup, backup_hash, archive, journal, *,
                         fence_continuous, drain_proven, same_boot):
    """Serialize explicit restore against forward progress and other restore attempts."""
    with journal.exclusive():
        return _restore_locked(database,backup,backup_hash,archive,journal,
                               fence_continuous=fence_continuous,drain_proven=drain_proven,same_boot=same_boot)
