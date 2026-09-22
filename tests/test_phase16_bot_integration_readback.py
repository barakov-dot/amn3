import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.vps import phase16_bot_integration_readback as core
from scripts import phase16_bot_integration_readback as runner


class ReadbackTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)

    def test_source_change_missing_and_unknown_name_are_distinct_without_name_leak(self):
        (self.root/'main.py').write_bytes(b'changed')
        (self.root/'private_customer_name.py').write_bytes(b'x')
        result = core.collect_source(self.root, {'main.py': {'sha256': '0'*64, 'bytes': 3},
                                               'gone.py': {'sha256': '0'*64, 'bytes': 1}})
        self.assertEqual(result['status'], 'DIFFERENT')
        self.assertEqual(result['missing'], ['gone.py'])
        self.assertEqual(result['different'], ['main.py'])
        self.assertEqual(result['extra_count'], 1)
        self.assertNotIn('private_customer', json.dumps(result))

    def test_source_exact_match_does_not_claim_loaded_modules(self):
        (self.root/'main.py').write_bytes(b'hello')
        result = core.collect_source(self.root, {'main.py': {'sha256':
            '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824', 'bytes':5}})
        self.assertEqual(result['status'], 'MATCH_IN_SCOPE')
        self.assertEqual(result['runtime_binding'], 'UNKNOWN')

    def test_read_rejects_size_cap_and_directory(self):
        p=self.root/'x'; p.write_bytes(b'12345')
        with self.assertRaisesRegex(core.Stop, 'file_cap'): core.safe_read(p, 4)
        with self.assertRaisesRegex(core.Stop, 'file_type'): core.safe_read(self.root, 100)

    def test_source_rejects_path_escape_in_expected_manifest(self):
        with self.assertRaisesRegex(core.Stop, 'manifest_path'):
            core.collect_source(self.root, {'../outside.py': {'sha256':'0'*64,'bytes':0}})

    def metadata(self, directory, name='Example', version='1.2'):
        p=self.root/directory; p.mkdir()
        (p/'METADATA').write_text('Metadata-Version: 2.1\nName: '+name+'\nVersion: '+version+
                                '\n\nsecret-in-description', encoding='utf-8')

    def test_dependencies_do_not_execute_pth_or_emit_unknown_package_names(self):
        self.metadata('example-1.2.dist-info')
        self.metadata('private-client.dist-info', 'Private-Client')
        (self.root/'danger.pth').write_text('import sys; raise RuntimeError("DO_NOT_RUN")')
        result=core.collect_dependencies(self.root, {'example':'1.2','missing':'2.0'})
        self.assertEqual(result['matched'], ['example'])
        self.assertEqual(result['missing'], ['missing'])
        self.assertEqual(result['extra_count'], 1)
        self.assertEqual(result['pth_count'], 1)
        self.assertEqual(result['runtime_binding'], 'UNKNOWN')
        self.assertNotIn('Private', json.dumps(result))
        self.assertNotIn('description', json.dumps(result))

    def test_duplicate_distribution_names_fail(self):
        self.metadata('a.dist-info', 'A_B'); self.metadata('b.dist-info', 'a-b')
        with self.assertRaisesRegex(core.Stop, 'dependency_duplicate'):
            core.collect_dependencies(self.root, {'a-b':'1.2'})

    def test_metadata_duplicate_header_and_secret_version_fail_without_leak(self):
        self.metadata('a.dist-info', 'Example', '1.2\nVersion: secret')
        with self.assertRaisesRegex(core.Stop, '^metadata_headers$'):
            core.collect_dependencies(self.root, {'example':'1.2'})

    def test_unit_normalization_redacts_unknown_exec_environment_and_paths(self):
        result=core.parse_unit('LoadState=loaded\nActiveState=active\nSubState=running\n'
            'MainPID=123\nType=notify\nRestart=no\nWorkingDirectory=/secret/customer\n'
            'ExecStart={ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 --token SECRET ; }\n'
            'Environment=TOKEN=SECRET\nExecStartPre=/private/SECRET\n', 'bot')
        self.assertFalse(result['exec_matches'])
        self.assertFalse(result['cwd_matches'])
        self.assertTrue(result['hooks_present'])
        self.assertEqual(result['pid'],123)
        self.assertNotIn('SECRET',json.dumps(result)); self.assertNotIn('customer',json.dumps(result))

    def test_duplicate_unit_property_rejected(self):
        with self.assertRaisesRegex(core.Stop, 'unit_properties'):
            core.parse_unit('MainPID=1\nMainPID=2\n', 'bot')

    def mount(self, options='ro', optional=''):
        return '40 1 8:1 /var/lib/amn2-spain /var/lib/amn2-spain '+options+' '+optional+' - ext4 /dev/x rw\n'

    def test_namespace_guard_rejects_same_namespace_writable_or_shared_view(self):
        for text, own, flags in [(self.mount(), 'mnt:[1]',True),
                                 (self.mount('rw'),'mnt:[2]',True),
                                 (self.mount(optional='shared:1'),'mnt:[2]',True),
                                 (self.mount(),'mnt:[2]',False)]:
            with self.subTest(text=text,own=own,flags=flags):
                with self.assertRaises(core.Stop):
                    core.verify_mount_guard(text, '/var/lib/amn2-spain', own, 'mnt:[1]', flags)

    def test_namespace_guard_rejects_nested_mount_even_if_parent_readonly(self):
        text=self.mount()+'41 40 8:2 / /var/lib/amn2-spain/nested rw - tmpfs tmpfs rw\n'
        with self.assertRaisesRegex(core.Stop,'mount_nested'):
            core.verify_mount_guard(text,'/var/lib/amn2-spain','mnt:[2]','mnt:[1]',True)

    def test_namespace_guard_accepts_only_distinct_private_readonly_view(self):
        core.verify_mount_guard(self.mount(),'/var/lib/amn2-spain','mnt:[2]','mnt:[1]',True)

    def test_failed_os_guard_prevents_sqlite_open(self):
        with patch.object(core,'guard_current_namespace',side_effect=core.Stop('guard')), \
             patch.object(sqlite3,'connect',side_effect=AssertionError('DB MUST NOT OPEN')):
            with self.assertRaisesRegex(core.Stop,'^guard$'):
                core.read_database(self.root/'db.sqlite3', {'tables':{},'indexes':[]}, 'mnt:[1]')

    def database(self, ddl='CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT DEFAULT \'SECRET_DEFAULT\')'):
        p=self.root/'test.sqlite3'
        conn=sqlite3.connect(p); conn.execute(ddl); conn.commit()
        self.addCleanup(conn.close)
        return p,conn

    def schema(self, path, allowed=None, **kwargs):
        conn=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
        try:
            return core.collect_schema(conn, allowed or {'tables':{'users':['id','name']},'indexes':[]}, **kwargs)
        finally: conn.close()

    def test_schema_reads_shape_and_never_emits_defaults_or_rows(self):
        p,writer=self.database(); writer.execute('INSERT INTO users VALUES(1,?)',('SECRET_ROW',)); writer.commit()
        before=p.read_bytes()
        result=self.schema(p)
        self.assertEqual(result['tables'][0]['name'],'users')
        self.assertEqual(result['tables'][0]['columns'][1],['name','TEXT',0,0,0])
        self.assertEqual(result['compatibility'],'UNKNOWN')
        self.assertNotIn('SECRET',json.dumps(result))
        self.assertEqual(p.read_bytes(),before)
        self.assertEqual(writer.execute('SELECT name FROM users').fetchone(),('SECRET_ROW',))

    def test_unknown_table_name_is_not_reflected_in_error(self):
        p,_=self.database('CREATE TABLE private_customer_name(id INTEGER)')
        with self.assertRaisesRegex(core.Stop,'^schema_unknown$'): self.schema(p)

    def test_schema_virtual_table_rejected_before_introspection(self):
        p,c=self.database(); c.execute('CREATE VIRTUAL TABLE secret_fts USING fts5(body)'); c.commit()
        with self.assertRaisesRegex(core.Stop,'^schema_virtual$'): self.schema(p)

    def test_schema_authorizer_blocks_user_reads_writes_attach_and_checkpoint(self):
        p,_=self.database(); conn=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
        self.addCleanup(conn.close)
        core.collect_schema(conn, {'tables':{'users':['id','name']},'indexes':[]})
        for sql in ['SELECT * FROM users', 'UPDATE users SET name="x"',
                    'ATTACH DATABASE ":memory:" AS other', 'PRAGMA wal_checkpoint',
                    'PRAGMA query_only=OFF', 'PRAGMA writable_schema=ON']:
            with self.subTest(sql=sql), self.assertRaises(sqlite3.DatabaseError): conn.execute(sql)

    def test_expired_schema_budget_fails_before_read(self):
        p,_=self.database()
        with self.assertRaisesRegex(core.Stop,'^schema_timeout$'): self.schema(p,deadline=time.monotonic()-1)

    def test_busy_database_stops_without_retry_or_repair(self):
        p,writer=self.database(); writer.execute('BEGIN EXCLUSIVE')
        with self.assertRaisesRegex(core.Stop,'^sqlite_read$'): self.schema(p)
        self.assertTrue(writer.in_transaction)

    def test_wal_reader_retains_committed_snapshot_and_writer_rows(self):
        p,writer=self.database(); writer.execute('PRAGMA journal_mode=WAL')
        writer.execute('INSERT INTO users VALUES(1,"committed")'); writer.commit()
        writer.execute('INSERT INTO users VALUES(2,"uncommitted")')
        self.assertEqual(self.schema(p)['journal_mode'],'wal')
        self.assertEqual(writer.execute('SELECT COUNT(*) FROM users').fetchone()[0],2)
        self.assertTrue(writer.in_transaction)

    def test_schema_indexes_and_foreign_keys_are_metadata_only(self):
        p,c=self.database()
        c.execute('CREATE TABLE child(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id))')
        c.execute('CREATE INDEX child_user ON child(user_id)'); c.commit()
        result=self.schema(p,{'tables':{'users':['id','name'],'child':['id','user_id']},'indexes':['child_user']})
        child=next(t for t in result['tables'] if t['name']=='child')
        self.assertEqual(child['indexes'][0]['columns'],['user_id'])
        self.assertEqual(child['foreign_keys'][0]['table'],'users')

    def test_holders_are_partial_evidence_and_pid_churn_is_unknown(self):
        db=self.root/'db'; db.write_bytes(b'fixture'); st=db.stat()
        proc=self.root/'proc'; (proc/'123'/'fd').mkdir(parents=True)
        (proc/'123'/'fd'/'4').hardlink_to(db)
        (proc/'123'/'stat').write_text('123 (name with spaces) '+' '.join(['S']+['0']*18+['456']+['0']*5))
        result=core.collect_holders(proc, {'db':(st.st_dev,st.st_ino)}, {123:('bot',456)})
        self.assertEqual(result['holders'],[{'pid':123,'start_ticks':456,'role':'bot','files':['db']}])
        self.assertEqual(result['writer_completeness'],'UNKNOWN')
        self.assertNotIn('name with spaces',json.dumps(result))
        result=core.collect_holders(proc, {'db':(st.st_dev,st.st_ino)}, {123:('bot',457)})
        self.assertEqual(result['status'],'UNKNOWN')

    def test_json_cap_fails_not_truncates(self):
        with self.assertRaisesRegex(core.Stop,'output_cap'): core.encode_result({'x':'a'*65536})

    def test_static_schema_manifest_never_executes_source(self):
        text='''raise RuntimeError("DO_NOT_EXECUTE")
DDL = "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT); CREATE INDEX users_name ON users(name);"
_ensure_column(conn, "users", "status", "TEXT")
'''
        result=runner.schema_allowlist([text])
        self.assertEqual(result,{'tables':{'users':['id','name','status']},'indexes':['users_name']})

    def test_lock_parser_rejects_unpinned_and_duplicate_requirements(self):
        self.assertEqual(runner.parse_lock('a-b==1.2 \\\n --hash=sha256:'+'a'*64), {'a-b':'1.2'})
        for text in ['name>=1','a==1\na==2','--index-url https://secret.invalid']:
            with self.subTest(text=text), self.assertRaises(core.Stop): runner.parse_lock(text)

    def test_cli_execute_is_unavailable_and_cannot_open_database(self):
        p=subprocess.run([sys.executable,'-I','-S','-B',str(ROOT/'scripts/phase16_bot_integration_readback.py'),
                          '--execute'],capture_output=True,timeout=5)
        self.assertNotEqual(p.returncode,0)
        self.assertIn(b'LIVE_EXECUTION_DISABLED',p.stdout)



    def test_static_manifest_ignores_fragmented_fstring_ddl_without_execution(self):
        text = 'DDL="CREATE TABLE users(id INTEGER);"\n' + 'dynamic=f"CREATE TABLE users_new (id INTEGER, {dangerous()})"'
        self.assertEqual(runner.schema_allowlist([text]), {'tables':{'users':['id']},'indexes':[]})

    def test_crlf_metadata_description_cannot_inject_version_header(self):
        data=b'Name: Example\r\nVersion: 1.2\r\n\r\nVersion: 99.0\r\n'
        self.assertEqual(core.metadata_headers(data), ('example','1.2'))

    def test_missing_wal_sidecar_prevents_open_even_with_namespace_guard(self):
        p=self.root/'db'; p.write_bytes(b'sentinel'); (self.root/'db-wal').write_bytes(b'sentinel-wal')
        with patch.object(core,'guard_current_namespace'), \
             patch.object(sqlite3,'connect',side_effect=AssertionError('MUST NOT OPEN')):
            with self.assertRaisesRegex(core.Stop,'sqlite_sidecars'):
                core.read_database(p,{'tables':{},'indexes':[]},'mnt:[1]')
        self.assertEqual(p.read_bytes(),b'sentinel')

    def test_any_rollback_journal_stops_before_sqlite_open(self):
        p=self.root/'db'; p.write_bytes(b'sentinel'); (self.root/'db-journal').write_bytes(b'journal')
        with patch.object(core,'guard_current_namespace'), \
             patch.object(sqlite3,'connect',side_effect=AssertionError('MUST NOT OPEN')):
            with self.assertRaisesRegex(core.Stop,'sqlite_journal_present'):
                core.read_database(p,{'tables':{},'indexes':[]},'mnt:[1]')
        self.assertEqual((self.root/'db-journal').read_bytes(),b'journal')

    def test_source_total_file_count_cap_stops_instead_of_truncation(self):
        for i in range(257): (self.root/('x'+str(i)+'.py')).write_bytes(b'')
        with self.assertRaisesRegex(core.Stop,'source_cap'): core.collect_source(self.root,{})

    def test_metadata_pth_cap_stops_instead_of_truncation(self):
        for i in range(17): (self.root/(str(i)+'.pth')).write_bytes(b'')
        with self.assertRaisesRegex(core.Stop,'dependency_cap'): core.collect_dependencies(self.root,{})

    def test_schema_column_cap_stops_before_output(self):
        cols=[f'c{i}' for i in range(513)]
        p,_=self.database('CREATE TABLE users('+','.join(c+' TEXT' for c in cols)+')')
        with self.assertRaisesRegex(core.Stop,'schema_cap'):
            self.schema(p,{'tables':{'users':cols},'indexes':[]})

    def test_proc_fd_cap_reports_unknown_and_no_completeness_claim(self):
        proc=self.root/'proc'; (proc/'123'/'fd').mkdir(parents=True)
        (proc/'123'/'stat').write_text('123 (private) '+' '.join(['S']+['0']*18+['456']))
        for i in range(257): (proc/'123'/'fd'/str(i)).write_bytes(b'')
        result=core.collect_holders(proc,{}, {})
        self.assertEqual(result['status'],'UNKNOWN')
        self.assertFalse(result['coverage_complete'])
        self.assertEqual(result['writer_completeness'],'UNKNOWN')

    def test_missing_proc_stat_is_churn_not_no_writers(self):
        (self.root/'123'/'fd').mkdir(parents=True)
        result=core.collect_holders(self.root,{}, {})
        self.assertEqual(result['churn'],1)
        self.assertEqual(result['status'],'UNKNOWN')

    def test_permission_denied_proc_is_unknown(self):
        (self.root/'123'/'fd').mkdir(parents=True)
        with patch.object(core,'start_ticks',side_effect=PermissionError):
            result=core.collect_holders(self.root,{}, {})
        self.assertEqual(result['denied'],1)
        self.assertEqual(result['status'],'UNKNOWN')

    def test_expression_index_is_unknown_not_false_compatibility(self):
        p,c=self.database(); c.execute('CREATE INDEX expr ON users(lower(name))'); c.commit()
        with self.assertRaisesRegex(core.Stop,'schema_expression_index'):
            self.schema(p,{'tables':{'users':['id','name']},'indexes':['expr']})

    def test_unit_expected_entrypoint_matches_but_does_not_prove_binding(self):
        text='MainPID=123\nWorkingDirectory=/opt/amn2-spain/runtime/source\n'
        text+='ExecStart={ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 -B -m app.main ; ignore_errors=no ; }'
        result=core.parse_unit(text,'bot')
        self.assertTrue(result['exec_matches']); self.assertTrue(result['cwd_matches'])
        self.assertEqual(result['runtime_binding'],'UNKNOWN')

    def test_stale_file_identity_rejects_replacement(self):
        p=self.root/'x'; p.write_bytes(b'x')
        actual=os.fstat
        def swapped(fd):
            value=actual(fd)
            return type('Changed',(),{'st_dev':value.st_dev,'st_ino':value.st_ino+1,'st_mode':value.st_mode})()
        with patch.object(os,'fstat',side_effect=swapped):
            with self.assertRaisesRegex(core.Stop,'file_identity'): core.safe_read(p,100)

    def test_manifest_wrong_commit_fails_before_source_materialization(self):
        with patch.object(runner,'git',return_value=b'0'*40+b'\n'):
            with self.assertRaisesRegex(core.Stop,'source_commit'): runner.build_manifest(self.root)



    def test_linux_smoke_refuses_non_linux_before_creating_scratch(self):
        spec=importlib.util.spec_from_file_location('guard_smoke',ROOT/'scripts/vps/phase16_bot_readback_guard_smoke.py')
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with patch.object(module.sys,'platform','win32'):
            result=module.run_smoke(self.root/'new-smoke')
        self.assertEqual(result,{'status':'NOT_RUN','reason':'linux_required'})
        self.assertFalse((self.root/'new-smoke').exists())

    def test_mount_setup_cannot_run_inside_host_namespace(self):
        with patch.object(core.sys,'platform','linux'), \
             patch.object(os,'readlink',return_value='mnt:[1]'), \
             patch.object(subprocess,'run',side_effect=AssertionError('MUST NOT MOUNT')):
            with self.assertRaisesRegex(core.Stop,'namespace_identity'):
                core.prepare_readonly_view(self.root,'mnt:[1]')


if __name__ == '__main__': unittest.main()
