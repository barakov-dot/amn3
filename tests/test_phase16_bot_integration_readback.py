import hashlib
import importlib.util
import io
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
from scripts.vps import phase16_bot_readback_guard_smoke as guard_smoke
from scripts import phase16_bot_integration_readback as runner
from scripts import phase16_bot_readback_guard_gate as guard_gate
from scripts.vps import phase16_bot_readback_guard_remote as guard_remote
from scripts import phase16_bot_integration_readback_gate as live_gate
from scripts.vps import phase16_bot_integration_readback_remote as live_remote


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

    def test_guard_payload_is_exact_and_tamper_rejected(self):
        payload = guard_gate.build_payload(ROOT)
        parts = guard_remote.parse_payload(payload)
        self.assertEqual(set(parts), {'phase16_bot_integration_readback.py',
                                      'phase16_bot_readback_guard_smoke.py'})
        self.assertEqual(hashlib.sha256(payload).hexdigest(), guard_remote.PAYLOAD_SHA256)
        with self.assertRaisesRegex(guard_remote.RemoteStop, '^payload_binding$'):
            guard_remote.parse_payload(payload[:-1] + bytes([payload[-1] ^ 1]))

    def test_guard_frame_bootstrap_roundtrip_uses_exact_approval(self):
        script = b'import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())'
        payload = guard_gate.build_payload(ROOT)
        command, frame = guard_gate.frame_request(script, payload)
        import shlex
        argv = shlex.split(command); argv[0] = sys.executable
        process = subprocess.run(argv, input=frame, capture_output=True, timeout=5)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout.strip().decode(), hashlib.sha256(payload).hexdigest())

    def test_guard_receipt_accepts_only_exact_synthetic_result(self):
        receipt = guard_remote.pass_receipt_for_tests()
        self.assertEqual(guard_gate.validate_receipt(receipt, 0)['status'],
                         'SYNTHETIC_LINUX_GUARD_PASS_NOT_LIVE')
        for key, value in [('live_database_opened', True), ('service_actions', 1),
                           ('destination', '/tmp/other')]:
            changed = json.loads(json.dumps(receipt)); changed[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(core.Stop, '^receipt_binding$'):
                guard_gate.validate_receipt(changed, 0)

    def test_guard_remote_bounded_process_caps_output_and_timeout(self):
        with self.assertRaisesRegex(guard_remote.RemoteStop, '^process_output_cap$'):
            guard_remote.run_bounded([sys.executable, '-I', '-S', '-B', '-c',
                                      'print("x"*9000)'], timeout=3, cap=1024)
        with self.assertRaisesRegex(guard_remote.RemoteStop, '^process_timeout$'):
            guard_remote.run_bounded([sys.executable, '-I', '-S', '-B', '-c',
                                      'import time;time.sleep(3)'], timeout=.05, cap=1024)

    def test_guard_execute_rejects_wrong_approval_before_loader_or_transport(self):
        called = []
        with self.assertRaisesRegex(core.Stop, '^approval_binding$'):
            guard_gate.execute_once(b'x', b'pass', self.root/'attempt', approval='wrong',
                                    approved_sha='bad', manifest={}, approved_manifest_sha='bad',
                                    loader=lambda role: called.append('loader'),
                                    transport=lambda *a, **k: called.append('transport'))
        self.assertEqual(called, [])
        self.assertFalse((self.root/'attempt').exists())

    def test_guard_execute_one_failed_transport_retains_redacted_result_no_retry(self):
        payload = guard_gate.build_payload(ROOT)
        script = guard_gate.remote_script(ROOT)
        class Binding:
            role='spain'; target_host='example.invalid'; target_user='tester'
            key_path=Path('key'); known_hosts_path=Path('known_hosts')
        calls=[]
        def transport(*args, **kwargs):
            calls.append(1); kwargs['diagnostics'].update(failure_stage='timeout')
            raise core.Stop('transport_timeout')
        manifest=guard_gate.gate_manifest(ROOT)
        with patch.object(guard_gate, 'ssh_environment', return_value={'PROGRAMDATA':'x'}):
          with patch.object(guard_gate,'binding_digest',return_value=manifest['target_binding_sha256']):
            result=guard_gate.execute_once(payload,script,self.root/'attempt',manifest=manifest,
                approval=guard_remote.APPROVAL,approved_sha=hashlib.sha256(script).hexdigest(),
                approved_manifest_sha=guard_gate.manifest_sha(ROOT),
                loader=lambda role: Binding(),transport=transport)
        self.assertEqual(len(calls),1)
        self.assertEqual(result['status'],'UNKNOWN_NO_RETRY')
        self.assertEqual(result['reason'],'transport_timeout')
        saved=json.loads((self.root/'attempt'/'result.json').read_text())
        self.assertEqual(saved,result)
        self.assertNotIn('example.invalid',json.dumps(saved))

    def test_guard_cli_preview_has_no_ssh_and_execute_requires_exact_binding(self):
        script=ROOT/'scripts/phase16_bot_readback_guard_gate.py'
        preview=subprocess.run([sys.executable,'-I','-S','-B',str(script)],
                               capture_output=True,timeout=8)
        self.assertEqual(preview.returncode,0)
        value=json.loads(preview.stdout)
        self.assertEqual(value['status'],'SYNTHETIC_GATE_READY_NOT_EXECUTED')
        self.assertEqual(value['ssh_attempts'],0)
        self.assertEqual(value['destination'],guard_remote.DESTINATION)
        rejected=subprocess.run([sys.executable,'-I','-S','-B',str(script),'--execute',
                                 '--approve','wrong','--approved-remote-sha256','0'*64,
                                 '--approved-manifest-sha256','0'*64,
                                 '--evidence-dir',str(self.root/'attempt')],
                                capture_output=True,timeout=8)
        self.assertEqual(rejected.returncode,2)
        self.assertEqual(json.loads(rejected.stdout)['reason'],'approval_binding')
        self.assertFalse((self.root/'attempt').exists())

    def test_guard_synthetic_child_is_mount_and_network_isolated(self):
        command = guard_smoke.child_command(Path('/synthetic/root'), 'wal', 'mnt:[1]')
        self.assertEqual(command[:5], ['/usr/bin/unshare', '--mount', '--net',
                                      '--propagation', 'private'])
        self.assertEqual(command.count('--scratch-root'), 1)
        self.assertNotIn('/var/lib/amn2-spain', command)

    def test_guard_claim_precedes_binding_read_and_binding_drift_stops_without_transport(self):
        payload=guard_gate.build_payload(ROOT); script=guard_gate.remote_script(ROOT)
        manifest=guard_gate.gate_manifest(ROOT); events=[]
        class Binding:
            role='spain'; target_host='changed.invalid'; target_user='tester'
            key_path=Path('key'); known_hosts_path=Path('known_hosts')
        def loader(role):
            self.assertTrue((self.root/'attempt'/'claim.json').is_file())
            events.append('loader'); return Binding()
        with patch.object(guard_gate,'ssh_environment',return_value={'PROGRAMDATA':'x'}), \
             patch.object(guard_gate,'binding_digest',return_value='0'*64):
            result=guard_gate.execute_once(payload,script,self.root/'attempt',manifest=manifest,
                approval=guard_remote.APPROVAL,approved_sha=hashlib.sha256(script).hexdigest(),
                approved_manifest_sha=guard_gate.manifest_sha(ROOT),loader=loader,
                transport=lambda *a,**k: events.append('transport'))
        self.assertEqual(events,['loader'])
        self.assertEqual(result['reason'],'target_binding')
        self.assertEqual(result['status'],'UNKNOWN_NO_RETRY')

    def test_guard_manifest_binds_runner_remote_payload_evidence_and_caps(self):
        manifest=guard_gate.gate_manifest(ROOT)
        self.assertEqual(guard_gate.validate_manifest(manifest,ROOT),manifest)
        for path in ('local_runner','remote_supervisor','payload'):
            changed=json.loads(json.dumps(manifest)); changed['sha256_lf'][path]='0'*64
            with self.subTest(path=path), self.assertRaisesRegex(core.Stop,'^manifest_binding$'):
                guard_gate.validate_manifest(changed,ROOT)
        changed=json.loads(json.dumps(manifest)); changed['limits']['transport_seconds']=61
        with self.assertRaisesRegex(core.Stop,'^manifest_binding$'):
            guard_gate.validate_manifest(changed,ROOT)

    def test_guard_stop_receipts_distinguish_retention_and_persist_exact_reason(self):
        before=guard_remote.stop_receipt('platform_contract',retained=False,persisted=False)
        self.assertEqual(before['status'],'STOP_BEFORE_DESTINATION_NO_RETRY')
        self.assertFalse(before['scratch_retained'])
        destination=self.root/'retained'; destination.mkdir()
        retained=guard_remote.stop_receipt('synthetic_timeout',retained=True,persisted=True)
        guard_remote.persist_receipt(destination,retained)
        self.assertEqual(json.loads((destination/'remote-result.json').read_text()),retained)
        self.assertEqual(retained['reason'],'synthetic_timeout')

    def test_guard_receipt_rejects_unknown_top_level_and_case_fields(self):
        receipt=guard_remote.pass_receipt_for_tests(); receipt['unexpected']='data'
        with self.assertRaisesRegex(core.Stop,'^receipt_binding$'):
            guard_gate.validate_receipt(receipt,0)
        receipt=guard_remote.pass_receipt_for_tests(); receipt['cases'][0]['unexpected']='data'
        with self.assertRaisesRegex(core.Stop,'^receipt_binding$'):
            guard_gate.validate_receipt(receipt,0)

    def test_guard_smoke_children_remain_in_outer_process_group(self):
        class Process:
            returncode=0; pid=123
            def communicate(self,timeout): return (b'{"case":"wal"}',b'')
            def poll(self): return 0
        with patch.object(guard_smoke.subprocess,'Popen',return_value=Process()) as popen:
            result=guard_smoke.bounded_child(Path('/synthetic/root'),'wal','mnt:[1]')
        self.assertEqual(result,{'case':'wal'})
        self.assertFalse(popen.call_args.kwargs['start_new_session'])

    def test_guard_remote_main_pre_destination_stop_is_not_claimed_retained(self):
        fake_in=type('Input',(),{'buffer':io.BytesIO(guard_gate.build_payload(ROOT))})()
        fake_out=io.StringIO()
        with patch.object(guard_remote.sys,'argv',['remote',guard_remote.APPROVAL]), \
             patch.object(guard_remote.sys,'stdin',fake_in), patch.object(guard_remote.sys,'stdout',fake_out), \
             patch.object(guard_remote,'execute',side_effect=guard_remote.RemoteStop('platform_contract')), \
             patch.object(guard_remote,'destination_exists',return_value=False), \
             patch.object(guard_remote,'install_deadline'), patch.object(guard_remote,'clear_deadline'):
            self.assertEqual(guard_remote.main(),3)
        value=json.loads(fake_out.getvalue())
        self.assertEqual(value['status'],'STOP_BEFORE_DESTINATION_NO_RETRY')
        self.assertFalse(value['scratch_retained'])

    def test_live_payload_is_exact_and_tamper_rejected(self):
        payload=live_gate.build_payload(ROOT)
        parts=live_remote.parse_payload(payload)
        self.assertEqual(set(parts),{'core','manifest'})
        with self.assertRaisesRegex(live_remote.RemoteStop,'^payload_binding$'):
            live_remote.parse_payload(payload[:-1]+bytes([payload[-1]^1]))

    def test_live_unit_command_is_fixed_property_allowlist(self):
        command=live_remote.unit_command('amn2-spain-bot.service','LoadState')
        self.assertEqual(command,['/usr/bin/systemctl','show','--no-pager','--value',
                                  '--property=LoadState','amn2-spain-bot.service'])
        self.assertNotIn('Environment',','.join(command))
        self.assertEqual(sum(item.startswith('--property=') for item in command),1)
        with self.assertRaisesRegex(live_remote.RemoteStop,'^unit_role$'):
            live_remote.unit_command('other.service','LoadState')
        with self.assertRaisesRegex(live_remote.RemoteStop,'^unit_property$'):
            live_remote.unit_command('amn2-spain-bot.service','Environment')

    def test_live_unit_collection_reads_each_property_separately(self):
        values={name:'' for name in live_remote.UNIT_PROPERTIES}
        values.update({'LoadState':'loaded','ActiveState':'active','SubState':'running',
                       'Type':'notify','Restart':'no','KillMode':'control-group',
                       'MainPID':'0','TimeoutStartUSec':'40s',
                       'TimeoutStopUSec':'1min 30s','WatchdogUSec':'0',
                       'KillSignal':'15','FinalKillSignal':'9',
                       'ExecStart':'{ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 -B -m app.main ; }',
                       'WorkingDirectory':'/opt/amn2-spain/runtime/source',
                       'ControlGroup':'/system.slice/amn2-spain-bot.service'})
        calls=[]
        def run(command,**_kwargs):
            calls.append(command)
            key=command[-2].split('=',1)[1]
            output=b'' if values[key]=='' else (values[key]+'\n').encode()
            return 0,output,{'stdout_bytes':len(output),'stderr_bytes':0,
                             'stderr_present':False}
        live_remote.PARTIAL={}
        with patch.object(live_remote,'run_bounded',side_effect=run):
            result=live_remote.collect_unit(core,'bot')
        self.assertEqual(len(calls),len(live_remote.UNIT_PROPERTIES))
        self.assertTrue(all(sum(item.startswith('--property=') for item in command)==1
                            for command in calls))
        self.assertTrue(result['exec_matches'])
        self.assertEqual(result['pid'],0)
        self.assertNotIn('unit_probe',live_remote.PARTIAL)
        self.assertGreater(sum(command[-2].split('=',1)[1].startswith('Exec')
                               for command in calls),0)

    def test_live_unit_failure_preserves_only_bounded_property_diagnostic(self):
        live_remote.PARTIAL={}
        diagnostics={'stdout_bytes':0,'stderr_bytes':17,'stderr_present':True}
        with patch.object(live_remote,'run_bounded',return_value=(1,b'',diagnostics)), \
             self.assertRaisesRegex(live_remote.RemoteStop,'^unit_property$'):
            live_remote.collect_unit(core,'bot')
        self.assertEqual(live_remote.PARTIAL['unit_probe'],{
            'role':'bot','property':'LoadState','stage':'command','returncode':1,
            'stdout_bytes':0,'stderr_bytes':17})
        host=live_gate.pass_receipt_for_tests()['host']
        receipt=live_remote.stop_receipt('unit_property',{
            'host':host,'unit_probe':live_remote.PARTIAL['unit_probe']})
        self.assertEqual(live_gate.validate_receipt(receipt,3),receipt)
        changed=json.loads(json.dumps(receipt));changed['partial']['unit_probe']['raw']='secret'
        with self.assertRaisesRegex(core.Stop,'^receipt_binding$'):
            live_gate.validate_receipt(changed,3)

    def test_live_db_child_is_mount_and_network_isolated(self):
        command=live_remote.db_child_command('mnt:[1]')
        self.assertEqual(command[:5],['/usr/bin/unshare','--mount','--net',
                                      '--propagation','private'])
        self.assertNotIn('--service',command)

    def test_live_receipt_rejects_unknown_or_mutating_claims(self):
        receipt=live_gate.pass_receipt_for_tests()
        self.assertEqual(live_gate.validate_receipt(receipt,0)['status'],
                         'READBACK_COMPLETE_WITH_LIMITATIONS')
        for key,value in [('service_actions',1),('database_write_attempted',True)]:
            changed=json.loads(json.dumps(receipt));changed[key]=value
            with self.subTest(key=key),self.assertRaisesRegex(core.Stop,'^receipt_binding$'):
                live_gate.validate_receipt(changed,0)
        changed=json.loads(json.dumps(receipt));changed['unexpected']='x'
        with self.assertRaisesRegex(core.Stop,'^receipt_binding$'):
            live_gate.validate_receipt(changed,0)
        changed=json.loads(json.dumps(receipt));changed['database']['rows']=[]
        with self.assertRaisesRegex(core.Stop,'^receipt_binding$'):
            live_gate.validate_receipt(changed,0)
        changed=json.loads(json.dumps(receipt));changed['units_before']['bot']['Environment']='secret'
        with self.assertRaisesRegex(core.Stop,'^receipt_binding$'):
            live_gate.validate_receipt(changed,0)

    def test_live_execute_wrong_approval_stops_before_claim_or_trust(self):
        called=[]
        self.assertEqual(live_remote.APPROVAL,
                         'PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_004')
        with self.assertRaisesRegex(core.Stop,'^approval_binding$'):
            live_gate.execute_once(b'x',b'pass',self.root/'attempt',
                approval='PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_003',
                approved_remote_sha='bad',approved_manifest_sha='bad',gate={},
                approved_gate_sha='bad',loader=lambda role:called.append('loader'),
                transport=lambda *a,**k:called.append('transport'))
        self.assertEqual(called,[])
        self.assertFalse((self.root/'attempt').exists())

    def test_live_execute_classifies_empty_transport_before_json_parse(self):
        gate=live_gate.gate_manifest(ROOT)
        payload=live_gate.build_payload(ROOT)
        script=live_gate.remote_script(ROOT)
        binding=type('Binding',(),{'role':'spain','known_hosts_path':self.root/'hosts',
                     'key_path':self.root/'key','target_user':'root',
                     'target_host':'example.invalid'})()
        def transport(*_args,**kwargs):
            kwargs['diagnostics'].update(returncode=255,stderr_classification='SSH_DISCONNECT_HINT')
            return 255,b''
        with patch.object(live_gate,'ssh_environment',return_value={}), \
             patch.object(live_gate,'binding_digest',return_value=gate['target_binding_sha256']):
            result=live_gate.execute_once(payload,script,self.root/'attempt',
                approval=live_remote.APPROVAL,
                approved_remote_sha=live_gate.sha(script),
                approved_manifest_sha=live_remote.MANIFEST_SHA256,gate=gate,
                approved_gate_sha=live_gate.gate_sha(ROOT),loader=lambda _role:binding,
                transport=transport)
        self.assertEqual(result['status'],'UNKNOWN_NO_RETRY')
        self.assertEqual(result['reason'],'transport_no_remote_receipt')
        self.assertNotIn('remote',result)

    def test_shared_transport_classifies_disconnects_without_raw_stderr(self):
        cases=(('Connection reset by peer PRIVATE_MARKER','SSH_CONNECTION_RESET_HINT'),
               ('Connection closed by remote host PRIVATE_MARKER','SSH_DISCONNECT_HINT'),
               ('client_loop: send disconnect: Broken pipe PRIVATE_MARKER','SSH_BROKEN_PIPE_HINT'),
               ('kex_exchange_identification: Connection closed by remote host PRIVATE_MARKER',
                'SSH_KEX_HINT'),
               ('banner exchange: Connection to host port 22: invalid format PRIVATE_MARKER',
                'SSH_BANNER_HINT'))
        for message,expected in cases:
            diagnostics={}
            with self.subTest(expected=expected):
                returncode,_output=live_gate.run_transport(
                    [sys.executable,'-I','-S','-B','-c',
                     'import sys;sys.stderr.write('+repr(message)+');sys.exit(255)'],
                    cwd=self.root,env=None,timeout=3,cap=65536,input_bytes=b'',
                    diagnostics=diagnostics)
                self.assertEqual(returncode,255)
                self.assertEqual(diagnostics['stderr_classification'],expected)
                self.assertNotIn('PRIVATE_MARKER',json.dumps(diagnostics))

    def test_live_gate_manifest_binds_caps_target_payload_and_evidence(self):
        gate=live_gate.gate_manifest(ROOT)
        self.assertEqual(live_gate.validate_gate_manifest(gate,ROOT),gate)
        for key in ('remote_supervisor','portable_core','transport_helper',
                    'integration_manifest','payload'):
            changed=json.loads(json.dumps(gate));changed['sha256_lf'][key]='0'*64
            with self.subTest(key=key),self.assertRaisesRegex(core.Stop,'^manifest_binding$'):
                live_gate.validate_gate_manifest(changed,ROOT)

    def test_live_preview_has_no_ssh_and_exact_scope(self):
        script=ROOT/'scripts/phase16_bot_integration_readback_gate.py'
        result=subprocess.run([sys.executable,'-I','-S','-B',str(script)],
                              capture_output=True,timeout=8)
        self.assertEqual(result.returncode,0)
        value=json.loads(result.stdout)
        self.assertEqual(value['status'],'ACTUAL_READBACK_GATE_READY_NOT_EXECUTED')
        self.assertEqual(value['ssh_attempts'],0)
        self.assertEqual(value['database_access'],'READ_ONLY_PRIVATE_MOUNT')
        self.assertEqual(value['service_actions'],0)

    def test_live_stop_receipt_preserves_only_normalized_partial_evidence(self):
        host=live_gate.pass_receipt_for_tests()['host']
        receipt=live_remote.stop_receipt('unit_show',{'host':host})
        self.assertEqual(live_gate.validate_receipt(receipt,3),receipt)
        self.assertEqual(receipt['partial'],{'host':host})
        receipt=live_remote.stop_receipt('unit_show',{'host':{'machine':'x86_64'}})
        with self.assertRaisesRegex(core.Stop,'^receipt_binding$'):
            live_gate.validate_receipt(receipt,3)
        summary=live_remote.partial_summary({'host':host})
        receipt=live_remote.stop_receipt('partial_output_cap',{'summary':summary})
        self.assertEqual(live_gate.validate_receipt(receipt,3),receipt)

    def test_live_database_file_size_drift_is_reported_not_misattributed(self):
        before={'database':{'present':True,'device':1,'inode':2,'bytes':10},
                'wal':{'present':False}}
        after=json.loads(json.dumps(before));after['database']['bytes']=11
        self.assertFalse(live_remote.stable_roots(before,after))
        changed=json.loads(json.dumps(after));changed['database']['inode']=3
        with self.assertRaisesRegex(live_remote.RemoteStop,'^database_file_changed$'):
            live_remote.stable_roots(before,changed)

    def test_live_worst_case_normalized_receipt_stays_under_transport_cap(self):
        manifest=json.loads((ROOT/'research/amn2/phase16-bot-integration-manifest-6e68235.json').read_text())
        receipt=live_remote.pass_receipt_for_tests()
        receipt['source']={'status':'MATCH_IN_SCOPE','files':manifest['source'],
                           'missing':[],'different':[],'extra_count':0,
                           'extra_digest':'0'*64,'runtime_binding':'UNKNOWN'}
        receipt['dependencies']={'status':'STATIC_METADATA_ONLY',
            'matched':sorted(manifest['runtime_pins']),'missing':[],'different':{},
            'extra_count':0,'extra_digest':'0'*64,'pth_count':0,'pth_hashes':[],
            'runtime_binding':'UNKNOWN'}
        receipt['database']={'status':'SHAPE_ONLY','sqlite_version':'3.50.0',
            'schema_version':1,'user_version':1,'journal_mode':'wal','compatibility':'UNKNOWN',
            'tables':[{'name':name,'columns':[[column,'TEXT',0,0,0] for column in columns],
                       'indexes':[],'foreign_keys':[]}
                      for name,columns in manifest['schema_allowlist']['tables'].items()]}
        self.assertLessEqual(len(json.dumps(receipt,separators=(',',':')).encode()),65536)

    def test_live_subprocess_stderr_has_independent_8k_cap(self):
        with self.assertRaisesRegex(live_remote.RemoteStop,'^process_stderr_cap$'):
            live_remote.run_bounded([sys.executable,'-I','-S','-B','-c',
                                     'import sys;sys.stderr.write("x"*9000)'],
                                    timeout=3,cap=65536)

    def test_live_remote_budget_reserves_cleanup_inside_50_seconds(self):
        self.assertEqual(live_remote.WORK_SECONDS+live_remote.CLEANUP_SECONDS+
                         live_remote.FINALIZATION_SECONDS,
                         live_remote.REMOTE_SECONDS)
        self.assertEqual(live_remote.WORK_SECONDS,44)
        gate=live_gate.gate_manifest(ROOT)
        self.assertEqual(gate['limits']['work_seconds'],44)
        self.assertEqual(gate['limits']['cleanup_seconds'],4)
        self.assertEqual(gate['limits']['finalization_seconds'],2)

    def test_live_remote_flushes_receipt_before_disarming_deadline(self):
        events=[]
        fake_stdin=type('FakeStdin',(),{'buffer':io.BytesIO(b'payload')})()
        def record_print(*args,**kwargs):
            events.append(('print',kwargs.get('flush')))
        def record_timer(_which,seconds):
            events.append(('timer',seconds))
        with patch.object(sys,'argv',['remote.py',live_remote.APPROVAL]), \
             patch.object(sys,'stdin',fake_stdin), \
             patch.object(live_remote,'install_deadline'), \
             patch.object(live_remote,'execute',return_value={}), \
             patch.object(live_remote,'arm_finalization',
                          side_effect=lambda:events.append(('arm',True))), \
             patch.object(live_remote.signal,'ITIMER_REAL',0,create=True), \
             patch.object(live_remote.signal,'setitimer',side_effect=record_timer,
                          create=True), \
             patch('builtins.print',side_effect=record_print):
            self.assertEqual(live_remote.main(),0)
        self.assertEqual(events,[('arm',True),('print',True),('timer',0)])


if __name__ == '__main__': unittest.main()
