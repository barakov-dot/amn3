"""Bounded evidence primitives. No SSH, service actions, mount setup or live CLI.

The DB entry point requires an already established private read-only Linux view.
Portable tests exercise schema logic, not Linux filesystem write enforcement.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
import stat
import subprocess
import sys
import time


class Stop(RuntimeError):
    """Only fixed reason codes may cross the output boundary."""


def require(condition, reason):
    if not condition:
        raise Stop(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode_result(value):
    data = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()
    require(len(data) <= 65536, 'output_cap')
    return data


def safe_relative(name):
    require(isinstance(name, str) and len(name) <= 256 and
            re.fullmatch(r'[A-Za-z0-9_./-]+', name) and
            not PurePosixPath(name).is_absolute() and
            all(p not in ('', '.', '..') for p in name.split('/')) and
            name.endswith('.py'), 'manifest_path')
    return name


def checked_path(path):
    path = Path(os.path.abspath(path))
    for part in reversed((path, *path.parents)):
        value = part.lstat()
        require(not stat.S_ISLNK(value.st_mode) and
                not (getattr(value, 'st_file_attributes', 0) & 0x400), 'path_link')
    return path


def identity(value):
    return value.st_dev, value.st_ino


def safe_read(path, cap):
    path = checked_path(path)
    before = path.stat()
    require(stat.S_ISREG(before.st_mode), 'file_type')
    require(before.st_size <= cap, 'file_cap')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    fd = os.open(path, flags)
    try:
        opened = os.fstat(fd)
        require(stat.S_ISREG(opened.st_mode) and identity(opened) == identity(before), 'file_identity')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read(cap + 1)
        after = os.fstat(fd)
        require(len(data) <= cap, 'file_cap')
        require((identity(after), after.st_size, after.st_mtime_ns) ==
                (identity(before), before.st_size, before.st_mtime_ns) and
                identity(path.stat()) == identity(after), 'file_changed')
        return data
    finally:
        os.close(fd)


def collect_source(root, expected):
    require(isinstance(expected, dict) and len(expected) <= 256, 'manifest_source')
    for name, item in expected.items():
        safe_relative(name)
        require(isinstance(item, dict) and set(item) == {'sha256', 'bytes'} and
                re.fullmatch('[0-9a-f]{64}', item['sha256']) and
                type(item['bytes']) is int and 0 <= item['bytes'] <= 1048576, 'manifest_source')
    root = checked_path(root)
    require(root.is_dir(), 'source_root')
    deadline = time.monotonic() + 10
    found, extra, entries, total = {}, [], 0, 0
    stack = [(root, 0)]
    while stack:
        directory, depth = stack.pop()
        require(depth <= 16, 'source_depth')
        with os.scandir(checked_path(directory)) as iterator:
            for entry in iterator:
                entries += 1
                require(entries <= 1024 and time.monotonic() < deadline, 'source_cap')
                path = checked_path(entry.path)
                mode = path.lstat().st_mode
                if stat.S_ISDIR(mode):
                    stack.append((path, depth + 1))
                else:
                    require(stat.S_ISREG(mode), 'file_type')
                    if path.suffix != '.py':
                        continue
                    name = path.relative_to(root).as_posix()
                    require(len(found) + len(extra) < 256, 'source_cap')
                    data = safe_read(path, 1048576)
                    total += len(data)
                    require(total <= 8388608, 'source_cap')
                    if name in expected:
                        found[name] = {'sha256': digest(data), 'bytes': len(data)}
                    else:
                        extra.append(digest(name.encode() + b'\0' + data))
    missing = sorted(set(expected) - set(found))
    different = sorted(n for n in found if found[n] != expected[n])
    return {'status': 'DIFFERENT' if missing or different or extra else 'MATCH_IN_SCOPE',
            'files': found, 'missing': missing, 'different': different,
            'extra_count': len(extra), 'extra_digest': digest(json.dumps(sorted(extra)).encode()),
            'runtime_binding': 'UNKNOWN'}


def normalize_name(name):
    require(isinstance(name, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', name), 'metadata_name')
    return re.sub(r'[-_.]+', '-', name).lower()


def metadata_headers(data):
    try:
        header = data.decode('utf-8').replace('\r\n', '\n').split('\n\n', 1)[0]
    except UnicodeError:
        raise Stop('metadata_encoding') from None
    pairs = [line.rstrip('\r').split(':', 1) for line in header.splitlines()
             if line.startswith(('Name:', 'Version:'))]
    names = [v.strip() for k, v in pairs if k == 'Name']
    versions = [v.strip() for k, v in pairs if k == 'Version']
    require(len(names) == len(versions) == 1, 'metadata_headers')
    require(re.fullmatch(r'[0-9][A-Za-z0-9.!+_-]{0,63}', versions[0]), 'metadata_version')
    return normalize_name(names[0]), versions[0]


def collect_dependencies(root, pins):
    require(all(normalize_name(n) == n and re.fullmatch(r'[0-9][A-Za-z0-9.!+_-]{0,63}', v)
                for n, v in pins.items()), 'manifest_pins')
    root = checked_path(root)
    found, extra, pth = {}, [], []
    entries = count = total = 0
    deadline = time.monotonic() + 8
    with os.scandir(root) as iterator:
        for entry in iterator:
            entries += 1
            require(entries <= 1024 and time.monotonic() < deadline, 'dependency_cap')
            if entry.name.endswith('.dist-info'):
                checked_path(entry.path)
                count += 1
                require(count <= 128, 'dependency_cap')
                data = safe_read(Path(entry.path)/'METADATA', 262144)
                total += len(data)
                require(total <= 8388608, 'dependency_cap')
                name, version = metadata_headers(data)
                require(name not in found, 'dependency_duplicate')
                found[name] = version
                if name not in pins:
                    extra.append(digest((name+'\0'+version).encode()))
            elif entry.name.endswith('.pth'):
                require(len(pth) < 16, 'dependency_cap')
                pth.append(digest(safe_read(entry.path, 65536)))
    return {'status': 'STATIC_METADATA_ONLY',
            'matched': sorted(n for n in pins if found.get(n) == pins[n]),
            'missing': sorted(set(pins) - set(found)),
            'different': {n: found[n] for n in pins if n in found and found[n] != pins[n]},
            'extra_count': len(extra), 'extra_digest': digest(json.dumps(sorted(extra)).encode()),
            'pth_count': len(pth), 'pth_hashes': sorted(pth), 'runtime_binding': 'UNKNOWN'}


def parse_unit(text, role):
    require(role in ('bot', 'web') and len(text.encode()) <= 65536, 'unit_properties')
    values = {}
    for line in text.splitlines():
        require('=' in line, 'unit_properties')
        key, value = line.split('=', 1)
        require(key not in values, 'unit_properties')
        values[key] = value
    result = {'role': role}
    enums = {'LoadState': {'loaded','not-found','error','masked'},
             'ActiveState': {'active','inactive','failed','activating','deactivating','reloading'},
             'SubState': {'running','dead','failed','start','stop','exited','auto-restart'},
             'Type': {'simple','notify','exec','forking','oneshot','dbus','idle'},
             'Restart': {'no','always','on-failure','on-abnormal','on-abort','on-success','on-watchdog'},
             'KillMode': {'control-group','mixed','process','none'}}
    for key, allowed in enums.items():
        result[key] = values.get(key) if values.get(key) in allowed else 'UNKNOWN'
    pid = values.get('MainPID', '')
    require(re.fullmatch('[0-9]{1,10}', pid), 'unit_pid')
    result['pid'] = int(pid)
    for key in ('TimeoutStartUSec','TimeoutStopUSec','WatchdogUSec','KillSignal','FinalKillSignal'):
        value = values.get(key, '')
        result[key] = (value if re.fullmatch(r'[0-9 .a-z]{1,40}', value) and
                       re.fullmatch(r'(infinity|[0-9]+|(?:[0-9.]+(?:us|ms|s|min|h|d) ?)+)',value) else 'UNKNOWN')
    target = '/usr/bin/python3 -B -m app.main' if role == 'bot' else (
        '/usr/bin/python3 -B -m app.cli web serve --host 127.0.0.1 --port 3031')
    start = values.get('ExecStart', '')
    path = re.findall(r'(?:^|[ {;])path=([^;]+) ;', start)
    argv = re.findall(r'argv\[\]=([^;]+) ;', start)
    result['exec_matches'] = path == ['/usr/bin/python3'] and argv == [target]
    result['cwd_matches'] = values.get('WorkingDirectory') == '/opt/amn2-spain/runtime/source'
    result['hooks_present'] = any(values.get(k, '').strip() for k in
                                 ('ExecStartPre','ExecStartPost','ExecStop','ExecStopPost','ExecReload','ExecCondition'))
    result['runtime_binding'] = 'UNKNOWN'
    return result


def verify_mount_guard(mountinfo, directory, own_ns, parent_ns, readonly):
    require(re.fullmatch(r'mnt:\[[0-9]+\]', own_ns) and
            re.fullmatch(r'mnt:\[[0-9]+\]', parent_ns) and own_ns != parent_ns, 'namespace_identity')
    require(readonly, 'mount_writable')
    require(len(mountinfo.encode()) <= 1048576, 'mount_cap')
    matches = []
    for line in mountinfo.splitlines():
        parts = line.split()
        require('-' in parts and len(parts) >= 10, 'mount_format')
        split = parts.index('-')
        require(split >= 6, 'mount_format')
        require(not any(p.startswith(('shared:', 'master:', 'propagate_from:')) for p in parts[6:split]),
                'mount_propagation')
        target = re.sub(r'\\([0-7]{3})', lambda m: chr(int(m[1],8)), parts[4])
        require(not target.startswith(directory.rstrip('/')+'/'), 'mount_nested')
        if target == directory:
            matches.append(parts[5].split(','))
    require(len(matches) == 1 and 'ro' in matches[0] and 'rw' not in matches[0], 'mount_writable')


def guard_current_namespace(directory, parent_ns):
    require(sys.platform == 'linux', 'linux_guard_unverified')
    directory = checked_path(directory)
    current_parent = os.readlink(f'/proc/{os.getppid()}/ns/mnt')
    require(current_parent == parent_ns, 'namespace_parent')
    # proc pseudo-file has size zero, so use a separately bounded read, not safe_read.
    with open('/proc/self/mountinfo', encoding='ascii') as stream:
        mountinfo = stream.read(1048577)
    verify_mount_guard(mountinfo, str(directory), os.readlink('/proc/self/ns/mnt'),
                       current_parent, bool(os.statvfs(directory).f_flag & os.ST_RDONLY))



def prepare_readonly_view(directory, parent_ns):
    """Child-only setup; caller must own a bounded supervisor outside this namespace."""
    require(sys.platform == 'linux', 'linux_guard_unverified')
    own_ns = os.readlink('/proc/self/ns/mnt')
    require(own_ns != parent_ns and os.readlink(f'/proc/{os.getppid()}/ns/mnt') == parent_ns,
            'namespace_identity')
    directory = checked_path(directory)
    require(directory.is_dir(), 'mount_directory')
    before = identity(directory.stat())
    with open('/proc/self/mountinfo', encoding='ascii') as stream:
        mountinfo = stream.read(1048577)
    require(len(mountinfo) <= 1048576, 'mount_cap')
    for line in mountinfo.splitlines():
        fields = line.split()
        require('-' in fields and len(fields) >= 10, 'mount_format')
        split = fields.index('-')
        require(split >= 6 and not any(x.startswith(('shared:', 'master:', 'propagate_from:'))
                                       for x in fields[6:split]), 'mount_propagation')
        target = re.sub(r'\\([0-7]{3})', lambda m: chr(int(m[1],8)), fields[4])
        require(not target.startswith(str(directory).rstrip('/')+'/'), 'mount_nested')
    for args in (['--bind',str(directory),str(directory)],
                 ['-o','remount,bind,ro',str(directory),str(directory)]):
        try:
            result = subprocess.run(['/usr/bin/mount','-n',*args], timeout=2,
                                    stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                                    env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},shell=False)
        except (OSError,subprocess.TimeoutExpired):
            raise Stop('mount_setup') from None
        require(result.returncode == 0, 'mount_setup')
    guard_current_namespace(directory,parent_ns)
    require(identity(directory.stat()) == before, 'mount_identity')


def collect_schema(conn, allowed, *, deadline=None):
    deadline = min(deadline if deadline is not None else time.monotonic()+2, time.monotonic()+2)
    def check():
        require(time.monotonic() < deadline, 'schema_timeout')
    check()
    require(not conn.in_transaction, 'schema_transaction')
    require(sqlite3.sqlite_version_info >= (3,37,0), 'sqlite_version')
    tables = allowed['tables']
    indexes = set(allowed['indexes'])
    triggers = allowed['triggers']
    require(all(re.fullmatch('[a-z_][a-z0-9_]{0,127}', name) and table in tables
                for name, table in triggers.items()), 'manifest_schema')
    for table, columns in tables.items():
        require(re.fullmatch('[a-z_][a-z0-9_]{0,127}',table) and
                all(re.fullmatch('[a-z_][a-z0-9_]{0,127}',c) for c in columns), 'manifest_schema')
    permitted_pragmas = {'journal_mode','schema_version','user_version','table_list'}
    authorized_names = set(tables) | indexes
    def authorizer(action, arg1, arg2, db, trigger):
        if action == sqlite3.SQLITE_SELECT:
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_READ and db == 'main' and arg1 in ('sqlite_master','sqlite_schema') and arg2 in ('name','type','tbl_name'):
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_TRANSACTION and arg1 in ('BEGIN','ROLLBACK'):
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_PRAGMA:
            if arg1 in permitted_pragmas and arg2 is None:
                return sqlite3.SQLITE_OK
            if arg1 in ('table_xinfo','index_list','foreign_key_list') and arg2 in tables:
                return sqlite3.SQLITE_OK
            if arg1 == 'index_info' and arg2 in authorized_names:
                return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    try:
        conn.execute('PRAGMA busy_timeout=0')
        conn.execute('PRAGMA query_only=ON')
        conn.execute('PRAGMA temp_store=MEMORY')
        conn.execute('PRAGMA trusted_schema=OFF')
        require(conn.execute('PRAGMA trusted_schema').fetchone() == (0,) and
                conn.execute('PRAGMA query_only').fetchone() == (1,), 'sqlite_guard')
        conn.enable_load_extension(False)
        conn.set_authorizer(authorizer)
        conn.set_progress_handler(lambda: int(time.monotonic() >= deadline), 100)
        conn.execute('BEGIN')
        def query(sql):
            check()
            cursor = conn.execute(sql)
            rows = cursor.fetchmany(513)
            require(len(rows) <= 512, 'schema_cap')
            check()
            return rows
        journal = query('PRAGMA journal_mode')[0][0]
        require(journal in ('delete','truncate','persist','memory','wal','off'), 'sqlite_journal')
        version = query('PRAGMA schema_version')[0][0]
        user_version = query('PRAGMA user_version')[0][0]
        table_list = query('PRAGMA table_list')
        require(not any(row[2] in ('virtual','shadow') for row in table_list), 'schema_virtual')
        objects = query("SELECT type,name,tbl_name FROM main.sqlite_schema ORDER BY type,name")
        require(len(objects) <= 128, 'schema_cap')
        names = []
        observed_triggers = []
        for kind, name, table in objects:
            require(len(name.encode()) <= 256, 'schema_cap')
            if kind == 'table' and name == 'sqlite_sequence':
                continue
            if kind == 'table' and name in tables:
                names.append(name)
            elif kind == 'index' and table in tables and (name in indexes or
                 re.fullmatch('sqlite_autoindex_'+re.escape(table)+'_[0-9]+',name)):
                authorized_names.add(name)
            elif kind == 'trigger' and name in triggers and triggers[name] == table:
                observed_triggers.append({'name':name,'table':table})
            else:
                raise Stop('schema_unknown')
        result_tables = []
        columns_count = index_count = fk_count = 0
        for table in sorted(names):
            columns = query('PRAGMA table_xinfo("'+table+'")')
            columns_count += len(columns)
            require(columns_count <= 512, 'schema_cap')
            normalized = []
            for cid, name, datatype, notnull, _default, pk, hidden in columns:
                require(name in tables[table] and datatype.upper() in ('INTEGER','INT','TEXT','REAL','BLOB','NUMERIC',''), 'schema_unknown')
                normalized.append([name,datatype.upper(),notnull,pk,hidden,cid])
            item = {'name':table,'columns':normalized,'indexes':[],'foreign_keys':[]}
            for _, name, unique, origin, partial in query('PRAGMA index_list("'+table+'")'):
                require(name in authorized_names, 'schema_unknown')
                index_count += 1
                require(index_count <= 128, 'schema_cap')
                column_ids = {c[0]:c[1] for c in columns}
                terms = []
                for sequence, cid, column in query('PRAGMA index_info("'+name+'")'):
                    require(type(sequence) is int and sequence == len(terms) and type(cid) is int,
                            'schema_expression_index')
                    if cid >= 0 and column_ids.get(cid) == column and column in tables[table]:
                        kind = 'COLUMN'
                    elif cid == -2 and column is None:
                        kind = 'EXPRESSION'
                    elif cid == -1 and column is None:
                        kind = 'ROWID'
                    else:
                        raise Stop('schema_expression_index')
                    terms.append({'sequence':sequence,'cid':cid,'kind':kind,'name':column})
                require(bool(terms), 'schema_expression_index')
                item['indexes'].append({'name':name,'unique':unique,'terms':terms,'partial':partial})
            for _, seq, target, from_col, to_col, on_update, on_delete, match in query('PRAGMA foreign_key_list("'+table+'")'):
                fk_count += 1
                require(fk_count <= 128, 'schema_cap')
                require(target in tables and from_col in tables[table] and
                        (to_col is None or to_col in tables[target]) and
                        on_update in ('NO ACTION','RESTRICT','SET NULL','SET DEFAULT','CASCADE') and
                        on_delete in ('NO ACTION','RESTRICT','SET NULL','SET DEFAULT','CASCADE') and match == 'NONE', 'schema_unknown')
                item['foreign_keys'].append({'table':target,'from':from_col,'to':to_col,'sequence':seq,
                                             'on_update':on_update,'on_delete':on_delete})
            result_tables.append(item)
        conn.execute('ROLLBACK')
        require(query('PRAGMA schema_version')[0][0] == version, 'schema_changed')
        return {'schema':'phase16.database-shape.v2','triggers':observed_triggers,
                'status':'SHAPE_ONLY','sqlite_version':sqlite3.sqlite_version,
                'schema_version':version,'user_version':user_version,'journal_mode':journal,
                'tables':result_tables,'compatibility':'UNKNOWN'}
    except sqlite3.Error:
        if time.monotonic() >= deadline:
            raise Stop('schema_timeout') from None
        raise Stop('sqlite_read') from None
    finally:
        if conn.in_transaction:
            conn.rollback()
        conn.set_progress_handler(None,0)
        # Keep the authorizer installed until the caller closes its connection.


def read_database(path, allowed, parent_namespace):
    path = Path(path)
    guard_current_namespace(path.parent, parent_namespace)  # MUST precede any DB open.
    path = checked_path(path)
    before = path.stat()
    require(stat.S_ISREG(before.st_mode), 'file_type')
    sidecars = {}
    for suffix in ('-wal','-shm','-journal'):
        sidecar = path.with_name(path.name+suffix)
        if os.path.lexists(sidecar):
            value = checked_path(sidecar).stat()
            require(stat.S_ISREG(value.st_mode), 'file_type')
            sidecars[suffix] = identity(value)
    require('-journal' not in sidecars, 'sqlite_journal_present')
    require(('-wal' in sidecars) == ('-shm' in sidecars), 'sqlite_sidecars')
    try:
        conn = sqlite3.connect(path.as_uri()+'?mode=ro', uri=True, timeout=0)
        try:
            result = collect_schema(conn, allowed)
            require(result['journal_mode'] != 'wal' or set(sidecars) == {'-wal','-shm'}, 'sqlite_sidecars')
        finally:
            conn.close()
    except sqlite3.Error:
        raise Stop('sqlite_read') from None
    guard_current_namespace(path.parent, parent_namespace)
    require(identity(path.stat()) == identity(before), 'file_changed')
    for suffix, expected in sidecars.items():
        require(identity(checked_path(path.with_name(path.name+suffix)).stat()) == expected, 'file_changed')
    return result


def start_ticks(path):
    # /proc stat size is zero; bounded plain read, never expose process comm.
    with open(path, 'rb') as stream:
        raw = stream.read(8193)
    require(len(raw) <= 8192, 'proc_cap')
    fields = raw.rsplit(b')',1)[-1].split()
    require(len(fields) >= 20 and fields[19].isdigit(), 'proc_stat')
    return int(fields[19])


def collect_holders(proc_root, identities, known):
    deadline = time.monotonic()+5
    holders, seen, denied, churn, total = [], 0, 0, 0, 0
    complete = True
    with os.scandir(proc_root) as processes:
        for process in processes:
            if not process.name.isdigit():
                continue
            seen += 1
            if seen > 512 or time.monotonic() >= deadline:
                complete = False
                break
            pid = int(process.name)
            try:
                before = start_ticks(Path(process.path)/'stat')
                files = set()
                per_pid = 0
                with os.scandir(Path(process.path)/'fd') as descriptors:
                    for fd in descriptors:
                        per_pid += 1; total += 1
                        if per_pid > 256 or total > 8192 or time.monotonic() >= deadline:
                            complete = False
                            break
                        current = identity(os.stat(fd.path))
                        files.update(kind for kind, ident in identities.items() if ident == current)
                after = start_ticks(Path(process.path)/'stat')
                if after != before or (pid in known and known[pid][1] != before):
                    churn += 1
                    continue
                if files:
                    holders.append({'pid':pid,'start_ticks':before,
                                    'role':known[pid][0] if pid in known else 'UNKNOWN_OWNER',
                                    'files':sorted(files)})
            except PermissionError:
                denied += 1
            except (FileNotFoundError, ProcessLookupError):
                churn += 1
            except (OSError, Stop):
                complete = False
            if total > 8192:
                break
    return {'status':'OBSERVED_ONLY' if complete and not denied and not churn else 'UNKNOWN',
            'holders':sorted(holders,key=lambda x:x['pid']), 'pids_seen':seen,
            'fds_seen':total,'denied':denied,'churn':churn,'coverage_complete':complete and not denied and not churn,
            'writer_completeness':'UNKNOWN'}
