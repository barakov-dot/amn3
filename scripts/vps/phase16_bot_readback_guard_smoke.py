"""Synthetic Linux guard smoke. Exclusive scratch only; never opens production DB.

Not executed on Linux yet. Requires an explicit future synthetic-only approval;
this helper is not the production readback runner and contains no SSH code.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
import phase16_bot_integration_readback as core

APPROVAL = 'PHASE16_SYNTHETIC_READBACK_GUARD_ONLY'
ALLOWED = {'tables':{'guard_sentinel':['id','value']},'indexes':[]}


def child(root, parent_ns, case):
    core.require(case in ('wal','missing_shm','journal'), 'synthetic_case')
    directory = core.checked_path(root/case)
    core.prepare_readonly_view(directory, parent_ns)
    db = directory/'synthetic.sqlite3'
    if case != 'wal':
        expected = 'sqlite_sidecars' if case == 'missing_shm' else 'sqlite_journal_present'
        try:
            core.read_database(db,ALLOWED,parent_ns)
        except core.Stop as error:
            core.require(str(error) == expected, 'synthetic_negative')
            return {'case':case,'status':'EXPECTED_STOP','reason':expected}
        raise core.Stop('synthetic_negative')
    result = core.read_database(db,ALLOWED,parent_ns)
    core.require(result['journal_mode'] == 'wal', 'synthetic_wal')
    # Deliberately omit query_only and use mode=rw to test the OS mount boundary.
    blocked = False
    connection = None
    try:
        connection = sqlite3.connect(db.as_uri()+'?mode=rw',uri=True,timeout=0)
        connection.execute("UPDATE guard_sentinel SET value='must_not_write'")
        connection.rollback()
    except sqlite3.Error as error:
        blocked = (getattr(error, "sqlite_errorcode", -1) & 255) == sqlite3.SQLITE_READONLY
    finally:
        if connection is not None:
            connection.close()
    core.require(blocked, 'synthetic_write_not_blocked')
    return {'case':case,'status':'SHAPE_READ_WRITE_BLOCKED','table_count':len(result['tables'])}


def bounded_child(root, case, parent_ns):
    command = ['/usr/bin/unshare','--mount','--propagation','private',sys.executable,
               '-I','-S','-B',str(Path(__file__).resolve()),'--child',case,
               '--scratch-root',str(root),'--parent-namespace',parent_ns]
    process = subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL,start_new_session=True,
                               env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'})
    try:
        output,_ = process.communicate(timeout=8)
        core.require(process.returncode == 0 and len(output) <= 4096, 'synthetic_child')
        result = json.loads(output)
        core.require(result.get('case') == case, 'synthetic_receipt')
        return result
    except subprocess.TimeoutExpired:
        raise core.Stop('synthetic_timeout') from None
    finally:
        if process.poll() is None:
            os.killpg(process.pid,signal.SIGKILL)  # only this newly owned process group
            process.wait(timeout=2)


def run_smoke(root):
    if sys.platform != 'linux':
        return {'status':'NOT_RUN','reason':'linux_required'}
    core.require(Path('/usr/bin/unshare').is_file() and Path('/usr/bin/mount').is_file(), 'synthetic_prerequisites')
    root = Path(os.path.abspath(root))
    core.checked_path(root.parent)
    core.require(root.name.startswith('phase16-readback-guard-'), 'synthetic_scratch_name')
    # Exclusive creation. Never reuse, remove, or overwrite a previous run.
    root.mkdir(mode=0o700)
    started = time.monotonic()
    writer = None
    try:
        for case in ('wal','missing_shm','journal'):
            directory = root/case; directory.mkdir(mode=0o700)
            db = directory/'synthetic.sqlite3'
            connection = sqlite3.connect(db)
            try:
                connection.execute('CREATE TABLE guard_sentinel(id INTEGER PRIMARY KEY,value TEXT)')
                connection.execute("INSERT INTO guard_sentinel VALUES(1,'preserve')")
                connection.commit()
            finally:
                connection.close()
        writer = sqlite3.connect(root/'wal'/'synthetic.sqlite3')
        writer.execute('PRAGMA journal_mode=WAL')
        writer.execute("INSERT INTO guard_sentinel VALUES(2,'committed')"); writer.commit()
        # Retain the WAL through an open connection; no active write lock that could
        # itself make the child's write fail and falsely validate read-only mounts.
        (root/'missing_shm'/'synthetic.sqlite3-wal').write_bytes(b'synthetic-not-a-real-wal')
        (root/'journal'/'synthetic.sqlite3-journal').write_bytes(b'synthetic-journal')
        parent_ns = os.readlink('/proc/self/ns/mnt')
        cases=[]
        for case in ('wal','missing_shm','journal'):
            core.require(time.monotonic()-started < 30, 'synthetic_timeout')
            cases.append(bounded_child(root,case,parent_ns))
        core.require(writer.execute('SELECT id,value FROM guard_sentinel ORDER BY id').fetchall() ==
                     [(1,'preserve'),(2,'committed')], 'synthetic_preservation')
        # Parent keeps its writable view after the child-only read-only bind.
        writer.execute("INSERT INTO guard_sentinel VALUES(3,'parent_still_writable')"); writer.commit()
        result = {'status':'SYNTHETIC_LINUX_GUARD_PASS','cases':cases,
                  'production_db_opened':False,'services_touched':False,'scratch_retained':True}
        (root/'result.json').write_bytes(core.encode_result(result)+b'\n')
        return result
    finally:
        if writer is not None:
            writer.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch-root',type=Path,required=True)
    parser.add_argument('--approve')
    parser.add_argument('--child',choices=('wal','missing_shm','journal'))
    parser.add_argument('--parent-namespace')
    args=parser.parse_args()
    try:
        if args.child:
            # This path only reads synthetic fixtures and requires a distinct RO namespace.
            core.require(args.scratch_root.name.startswith('phase16-readback-guard-'), 'synthetic_scratch_name')
            result=child(args.scratch_root,args.parent_namespace,args.child)
        else:
            core.require(args.approve == APPROVAL, 'synthetic_approval')
            result=run_smoke(args.scratch_root)
        print(core.encode_result(result).decode())
        return 0 if result.get('status') != 'NOT_RUN' else 3
    except core.Stop as error:
        print(json.dumps({'status':'STOP','reason':str(error)}))
    except (OSError,ValueError,TypeError,sqlite3.Error,subprocess.SubprocessError):
        print('{"status":"STOP","reason":"synthetic_failure"}')
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
