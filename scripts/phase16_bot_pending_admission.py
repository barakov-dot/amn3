"""Initial aggregate-only pending check inside a private read-only DB namespace.

The child reads the live DB only after validating kernel read-only mount scope.
No rows/DDL/config/token leaves it; its network namespace is separate. It neither
copies nor migrates the DB. The bounded supervisor and exact permission belong
to the complete future maintenance packet. No standalone execute CLI.
"""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
from scripts.vps import phase16_bot_integration_readback_v3 as guard
from scripts.phase16_bot_maintenance_storage import IMPORT_BOOTSTRAP

DATABASE='/var/lib/amn2-spain/amn2.sqlite3'
TABLES={'devices','admin_config_issuance_receipts','admin_config_issuance_requests'}
class PendingError(ValueError):pass

def require(value,reason):
    if not value:raise PendingError(reason)

def namespace_guard(directory,parent_mount_ns,parent_net_ns):
    require(sys.platform=='linux' and os.geteuid()==0,'pending_platform')
    require(os.readlink('/proc/self/ns/net')!=parent_net_ns and
            os.readlink('/proc/'+str(os.getppid())+'/ns/net')==parent_net_ns,'pending_network_namespace')
    guard.guard_current_namespace(directory,parent_mount_ns)

def pending_snapshot(database,*,parent_mount_ns,parent_net_ns,clock=time.monotonic):
    path=Path(database)
    namespace_guard(path.parent,parent_mount_ns,parent_net_ns)
    deadline=clock()+5
    try:
        path=guard.checked_path(path)
        before=guard.identity(path.stat())
        with contextlib.closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,timeout=1)) as conn:
            conn.execute('PRAGMA query_only=ON');conn.execute('PRAGMA trusted_schema=OFF')
            conn.set_progress_handler(lambda:int(clock()>=deadline),500)
            conn.execute('BEGIN')
            rows=conn.execute("SELECT name,type,sql FROM sqlite_master WHERE name IN ('devices','admin_config_issuance_receipts','admin_config_issuance_requests')").fetchmany(4)
            require(len(rows)==3 and {r[0] for r in rows}==TABLES and all(r[1]=='table' and
                isinstance(r[2],str) and r[2].lstrip().upper().startswith('CREATE TABLE ') for r in rows),
                'pending_table_type')
            def authorize(action,a,b,database_name,trigger):
                if action==sqlite3.SQLITE_SELECT:return sqlite3.SQLITE_OK
                if action==sqlite3.SQLITE_READ and a in TABLES and b in ('','status','request_id','item_count') and database_name=='main' and trigger is None:return sqlite3.SQLITE_OK
                if action==sqlite3.SQLITE_FUNCTION and b=='count':return sqlite3.SQLITE_OK
                if action==sqlite3.SQLITE_TRANSACTION and a=='ROLLBACK':return sqlite3.SQLITE_OK
                return sqlite3.SQLITE_DENY
            conn.set_authorizer(authorize)
            counts=dict(
                devices=conn.execute("SELECT count(*) FROM devices WHERE status='pending'").fetchone()[0],
                issuance_receipts=conn.execute("SELECT count(*) FROM admin_config_issuance_receipts WHERE status <> 'completed'").fetchone()[0],
                issuance_requests=conn.execute("SELECT count(*) FROM admin_config_issuance_requests q WHERE q.item_count <> (SELECT count(*) FROM admin_config_issuance_receipts r WHERE r.request_id=q.request_id AND r.status='completed')").fetchone()[0])
            require(all(type(n) is int and 0<=n<=2**31-1 for n in counts.values()) and clock()<deadline,'pending_limits')
            conn.rollback()
        require(guard.identity(path.stat())==before,'pending_database_changed')
        namespace_guard(path.parent,parent_mount_ns,parent_net_ns)
        return dict(schema='phase16.pending-aggregates.v1',counts=counts,
            pending_operations='none_observed' if not any(counts.values()) else 'present',
            scope='AGGREGATE_ONLY_RO_NAMESPACE',business_handler_drain='NOT_ESTABLISHED')
    except PendingError:raise
    except Exception:raise PendingError('pending_read_failed') from None

def child_entry(parent_mount_ns,parent_net_ns):
    try:
        require(sys.platform=='linux' and os.geteuid()==0,'pending_platform')
        guard.prepare_readonly_view(str(Path(DATABASE).parent),parent_mount_ns)
        result=pending_snapshot(DATABASE,parent_mount_ns=parent_mount_ns,parent_net_ns=parent_net_ns)
        print(json.dumps(result,sort_keys=True));return 0
    except Exception:
        print('{"status":"STOP","reason":"pending_read_failed"}');return 3

def child_command(code,parent_mount_ns,parent_net_ns,*,expected_artifacts):
    require(isinstance(code,str) and re.fullmatch('/[A-Za-z0-9_./-]+',code) and
            all(p not in ('','..','.') for p in code[1:].split('/')),'pending_code_path')
    require(re.fullmatch(r'mnt:\[[0-9]+\]',parent_mount_ns) and
            re.fullmatch(r'net:\[[0-9]+\]',parent_net_ns),'pending_namespace')
    require(isinstance(expected_artifacts,dict) and 0<len(expected_artifacts)<=256 and
            'scripts/phase16_bot_pending_admission.py' in expected_artifacts and
            all(isinstance(k,str) and isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v)
                for k,v in expected_artifacts.items()),'pending_artifact_pins')
    encoded=json.dumps(expected_artifacts,sort_keys=True,separators=(',',':'),ensure_ascii=True)
    require(len(encoded)<=65536,'pending_artifact_pins')
    cache_key=hashlib.sha256(encoded.encode('ascii')).hexdigest()
    bootstrap=(IMPORT_BOOTSTRAP+'\n_phase16_import_root('+repr(code)+','+repr(expected_artifacts)+','+repr(cache_key)+')\n'
        'from scripts.phase16_bot_pending_admission import child_entry\n'
        'raise SystemExit(child_entry(_p16_sys.argv[1],_p16_sys.argv[2]))\n')
    return ['/usr/bin/unshare','--mount','--net','--propagation','private',
            '/usr/bin/python3','-I','-S','-B','-c',bootstrap,parent_mount_ns,parent_net_ns]

def collect_live(client,code,*,expected_artifacts):
    """One bounded child, no retry; invoke only within approved aggregate-read scope."""
    try:
        require(sys.platform=='linux' and os.geteuid()==0,'pending_platform')
        argv=child_command(code,os.readlink('/proc/self/ns/mnt'),os.readlink('/proc/self/ns/net'),expected_artifacts=expected_artifacts)
        raw=client.run(argv,20)
        require(isinstance(raw,bytes) and len(raw)<=1024,'pending_output')
        value=json.loads(raw)
        require(isinstance(value,dict) and set(value)=={'schema','counts','pending_operations','scope','business_handler_drain'}
                and value['schema']=='phase16.pending-aggregates.v1' and value['scope']=='AGGREGATE_ONLY_RO_NAMESPACE'
                and value['business_handler_drain']=='NOT_ESTABLISHED','pending_output')
        counts=value['counts']
        require(isinstance(counts,dict) and set(counts)=={'devices','issuance_receipts','issuance_requests'} and
                all(type(n) is int and n==0 for n in counts.values()) and value['pending_operations']=='none_observed',
                'pending_operations_present')
        return value
    except PendingError:raise
    except Exception:raise PendingError('pending_collection_failed') from None
