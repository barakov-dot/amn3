"""Full exact-source schemas; local memory databases only, no application startup."""
import ast
import contextlib
import io
import tempfile
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import types
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import phase16_bot_integration_manifest_v3 as builder
from scripts.vps import phase16_bot_integration_readback_v3 as core
from scripts import phase16_bot_integration_validator_v3 as validator
from scripts import phase16_bot_integration_readback_gate_v3 as gate
from scripts import phase16_bot_integration_readback_gate as legacy
from scripts import phase16_bot_integration_readback_gate_v2 as old_gate
from scripts.vps import phase16_bot_integration_readback_remote_v3 as remote

FIXTURES = ROOT / 'tests/fixtures/phase16_schema'

def source(name):
    info = json.loads((FIXTURES / 'provenance.json').read_text())[name]
    data = (FIXTURES / (name + '.txt')).read_bytes().replace(b'\r\n', b'\n')
    assert hashlib.sha256(data).hexdigest() == info['sha256']
    for node in ast.walk(ast.parse(data)):
        if isinstance(node, ast.Import):
            assert all(a.name == 'sqlite3' for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module in ('app.db.phase14_dual_protocol', 'app.db.phase15_bootstrap')
    return data.decode()


def initializers():
    modules = {name: types.ModuleType(name) for name in (
        'app', 'app.db', 'app.db.phase14_dual_protocol', 'app.db.phase15_bootstrap')}
    with patch.dict(sys.modules, modules):
        for name, fixture in [('app.db.phase14_dual_protocol','candidate_phase14'),
                              ('app.db.phase15_bootstrap','candidate_phase15')]:
            exec(compile(source(fixture), fixture, 'exec'), modules[name].__dict__)
        candidate = types.ModuleType('candidate_schema')
        exec(compile(source('candidate_schema'), 'candidate_schema', 'exec'), candidate.__dict__)
    old = types.ModuleType('old_schema')
    exec(compile(source('old_schema'), 'old_schema', 'exec'), old.__dict__)
    return old.initialize_schema, candidate.initialize_schema


def allowlist():
    return builder.schema_allowlist([source(name) for name in
                                   ('candidate_schema','candidate_phase14','candidate_phase15')])


class FullSchemaTests(unittest.TestCase):
    def collect(self, mode):
        old, new = initializers()
        conn = sqlite3.connect(':memory:')
        self.addCleanup(conn.close)
        for init in {'old':[old], 'candidate':[new], 'transition':[old,new]}[mode]:
            init(conn)
        conn.commit()
        before = conn.serialize()
        try:
            shape = core.collect_schema(conn, allowlist())
        except core.Stop as error:
            self.fail('full schema rejected: ' + str(error))
        for sql in ('SELECT * FROM users', 'SELECT sql FROM sqlite_schema',
                    'INSERT INTO users(user_id) VALUES(1)', 'PRAGMA query_only=OFF'):
            with self.assertRaises(sqlite3.DatabaseError):
                conn.execute(sql)
        conn.set_authorizer(None)  # Only after reader, on disposable fixture, for byte comparison.
        self.assertEqual(conn.serialize(), before)
        validator.validate_database(shape, {'schema_allowlist':allowlist()})
        self.assertEqual(shape['compatibility'], 'UNKNOWN')
        self.assertNotIn('lower(trim', json.dumps(shape))
        return shape

    def test_old_full_schema(self):
        shape = self.collect('old')
        self.assertEqual(len(shape['tables']), 18)
        self.assertEqual(shape.get('triggers'), [])
        users = next(t for t in shape['tables'] if t['name']=='users')
        index = next(i for i in users['indexes'] if i['name']=='idx_users_operator_label_unique')
        self.assertEqual(index.get('terms'), [{'sequence':0,'cid':-2,'kind':'EXPRESSION','name':None}])

    def test_candidate_full_schema(self):
        shape = self.collect('candidate')
        self.assertEqual(len(shape['tables']), 29)
        self.assertEqual(len(shape.get('triggers', [])), 4)

    def test_old_to_candidate_full_schema(self):
        self.assertEqual(len(self.collect('transition')['tables']), 29)

    def test_static_allowlist_contains_literal_alters_and_trigger_owners(self):
        result = allowlist()
        self.assertIn('client_build', result['tables']['admin_config_issuance_receipts'])
        self.assertIn('release_kind', result['tables']['client_compatibility_evidence'])
        self.assertEqual(result.get('triggers', {}).get('trg_phase15_callback_owner_passport_insert'),
                         'telegram_callback_handles')

    def test_adjacent_literals_allowed_dynamic_identifiers_excluded(self):
        text = "sql = ('CREATE TABLE example(id INTEGER);')\n"
        text += "conn.execute('ALTER TABLE example ' 'ADD COLUMN added TEXT')\n"
        text += 'conn.execute(f"ALTER TABLE example ADD COLUMN {column} TEXT")\n'
        result = builder.schema_allowlist([text])
        self.assertEqual(result['tables']['example'], ['added', 'id'])

class DefensiveSchemaTests(unittest.TestCase):
    def test_dynamic_concatenation_and_format_do_not_expand_allowlist(self):
        text = "base = 'CREATE TABLE example(id INTEGER)'\n"
        text += "sql = 'ALTER TABLE example ADD COLUMN leaked TEXT ' + suffix\n"
        text += "sql = 'ALTER TABLE example ADD COLUMN formatted TEXT {}'.format(suffix)\n"
        self.assertEqual(builder.schema_allowlist([text])['tables']['example'], ['id'])

    def test_unknown_or_wrong_owner_triggers_stop_without_disclosure(self):
        for name, owner in [('SECRET_TRIGGER','example'), ('known','other')]:
            with self.subTest(name=name), sqlite3.connect(':memory:') as conn:
                conn.executescript('CREATE TABLE example(id INTEGER); CREATE TABLE other(id INTEGER);'
                                  'CREATE TRIGGER '+name+' AFTER INSERT ON '+owner+' BEGIN SELECT 1; END;')
                allowed = {'tables':{'example':['id'],'other':['id']},'indexes':[],
                           'triggers':{'known':'example'}}
                with self.assertRaisesRegex(core.Stop, '^schema_unknown$'):
                    core.collect_schema(conn, allowed)

    def test_index_info_sentinels_and_malformed_terms(self):
        class ConnectionView:
            def __init__(self, conn, rows): self.conn,self.rows=conn,rows
            def __getattr__(self, name): return getattr(self.conn,name)
            def execute(self, sql):
                cursor=self.conn.execute(sql)
                if sql.startswith('PRAGMA index_info('):
                    return SimpleNamespace(fetchmany=lambda size:self.rows)
                return cursor
        allowed={'tables':{'example':['id']},'indexes':['ix'],'triggers':{}}
        for rows,valid in [([(0,-1,None)],True), ([(0,-2,None)],True),
                           ([(0,-1,'id')],False), ([(0,-3,None)],False),
                           ([(True,0,'id')],False), ([(0,True,'id')],False),
                           ([(0,0,'id'),(0,0,'id')],False), ([],False)]:
            with self.subTest(rows=rows):
                conn=sqlite3.connect(':memory:');self.addCleanup(conn.close)
                conn.executescript('CREATE TABLE example(id INTEGER); CREATE INDEX ix ON example(id);')
                view=ConnectionView(conn,rows)
                if valid:
                    shape=core.collect_schema(view,allowed)
                    validator.validate_database(shape,{'schema_allowlist':allowed})
                    self.assertEqual(shape['tables'][0]['indexes'][0]['terms'][0]['kind'],
                                     'ROWID' if rows[0][1]==-1 else 'EXPRESSION')
                else:
                    with self.assertRaisesRegex(core.Stop,'^schema_expression_index$'):
                        core.collect_schema(view,allowed)

    def test_schema_deadline_and_object_cap_still_stop(self):
        conn=sqlite3.connect(':memory:');self.addCleanup(conn.close)
        with self.assertRaisesRegex(core.Stop,'^schema_timeout$'):
            core.collect_schema(conn,{'tables':{},'indexes':[],'triggers':{}},deadline=0)
        allowed={'tables':{},'indexes':[],'triggers':{}}
        for n in range(129):
            name='table_'+str(n);conn.execute('CREATE TABLE '+name+'(id INTEGER)')
            allowed['tables'][name]=['id']
        with self.assertRaisesRegex(core.Stop,'^schema_cap$'): core.collect_schema(conn,allowed)

    def test_mixed_expression_column_terms_preserve_order(self):
        conn = sqlite3.connect(':memory:'); self.addCleanup(conn.close)
        conn.executescript('CREATE TABLE example(a TEXT,b TEXT); CREATE INDEX ix ON example(lower(a),b);')
        allowed = {'tables':{'example':['a','b']},'indexes':['ix'],'triggers':{}}
        shape = core.collect_schema(conn, allowed)
        terms = shape['tables'][0]['indexes'][0]['terms']
        self.assertEqual(terms, [{'sequence':0,'cid':-2,'kind':'EXPRESSION','name':None},
                                {'sequence':1,'cid':1,'kind':'COLUMN','name':'b'}])
        validator.validate_database(shape, {'schema_allowlist':allowed})
        for key, val in [('cid',-3),('name','SECRET'),('sequence',4),('cid',True),('kind','COLUMN')]:
            bad = copy.deepcopy(shape);bad['tables'][0]['indexes'][0]['terms'][0][key]=val
            with self.subTest(key=key,val=val), self.assertRaises((core.Stop, legacy.core.Stop)):
                validator.validate_database(bad, {'schema_allowlist':allowed})
        for cid, name in [(0,'b'),(1,'a')]:
            bad=copy.deepcopy(shape); term=bad['tables'][0]['indexes'][0]['terms'][1]
            term.update(cid=cid,name=name)
            with self.assertRaises((core.Stop, legacy.core.Stop)): validator.validate_database(bad, {'schema_allowlist':allowed})


class BoundSchemaTests(unittest.TestCase):
    collect = FullSchemaTests.collect
    def receipt(self, shape):
        receipt = legacy.pass_receipt_for_tests()
        receipt['schema'] = 'phase16.integration-readback-remote.v2'
        receipt['database'] = shape
        for key in ('units_before','units_after'):
            for role in ('bot','web'):
                receipt[key][role]['KillSignal']='15'
                receipt[key][role]['FinalKillSignal']='9'
        return receipt

    def test_payload_parses_and_bound_core_collects_full_schemas(self):
        try:
            parsed = remote.parse_payload(gate.build_payload())
        except remote.RemoteStop as error:
            self.fail('new payload not bound: '+str(error))
        actual = remote.load_core(parsed['core'])
        old,new = initializers()
        for sequence,count in [([old],18),([new],29),([old,new],29)]:
            conn=sqlite3.connect(':memory:'); self.addCleanup(conn.close)
            for init in sequence: init(conn)
            conn.commit()
            shape=actual.collect_schema(conn,parsed['manifest']['schema_allowlist'])
            receipt=self.receipt(shape)
            gate.validate_receipt_numeric(receipt,0)
            self.assertEqual(len(shape['tables']),count)
            self.assertLessEqual(len(actual.encode_result(receipt)),65536)
        command,frame=gate.frame_request(gate.remote_script(),gate.build_payload())
        self.assertIn('-I -S -B',command)
        self.assertLessEqual(len(frame),131072)

    def test_child_bootstrap_checks_new_payload_before_platform_guard(self):
        payload=gate.build_payload()
        for data,expected in [(payload,'linux_guard_unverified'), (old_gate.build_payload(),'payload_binding'),
                              (payload[:-1]+b'!','payload_binding')]:
            output=io.StringIO()
            with self.subTest(expected=expected), \
                 patch.object(sys,'stdin',SimpleNamespace(buffer=io.BytesIO(data))), \
                 patch.object(sys,'argv',['child','mnt:[42]']), patch.object(sys,'platform','win32'), \
                 patch.object(sqlite3,'connect',side_effect=AssertionError('DB open')), \
                 patch.object(core.os,'readlink',side_effect=AssertionError('namespace access')), \
                 contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as exit_result:
                exec(compile(remote.CHILD_BOOTSTRAP,'<test-bound-child>','exec'),{})
            self.assertEqual(exit_result.exception.code,3)
            self.assertEqual(json.loads(output.getvalue())['reason'],expected)

    def test_payload_drift_and_old_payload_rejected(self):
        payload=gate.build_payload()
        for value in (payload[:-1],payload[:-1]+b'!',old_gate.build_payload()):
            with self.assertRaises(remote.RemoteStop): remote.parse_payload(value)

    def test_old_receipt_and_forged_schema_are_rejected(self):
        with self.assertRaises((core.Stop,legacy.core.Stop)):
            gate.validate_receipt_numeric(legacy.pass_receipt_for_tests(),0)
        good=self.receipt(self.collect('candidate'))
        for change in ('trigger_owner','trigger_extra','index_extra','column_id','duplicate_table','old_shape'):
            bad=copy.deepcopy(good);db=bad['database']
            if change=='trigger_owner': db['triggers'][0]['table']='users'
            elif change=='trigger_extra': db['triggers'][0]['sql']='SECRET'
            elif change=='index_extra': next(t for t in db['tables'] if t['indexes'])['indexes'][0]['sql']='SECRET'
            elif change=='column_id': db['tables'][0]['columns'][0][5]=True
            elif change=='duplicate_table': db['tables'].append(copy.deepcopy(db['tables'][0]))
            else: db.pop('schema')
            with self.subTest(change=change), self.assertRaises((core.Stop,legacy.core.Stop)):
                gate.validate_receipt_numeric(bad,0)

    def test_full_receipt_and_stop_cross_transport_fixture_once(self):
        receipt=self.receipt(self.collect('candidate'))
        stop=remote.stop_receipt('database_schema_unknown', {'database':receipt['database']})
        bad=copy.deepcopy(receipt);bad['database']['triggers'][0]['sql']='SECRET_SQL'
        for value,code,expected in [(receipt,0,'READBACK_COMPLETE_WITH_LIMITATIONS'),
                                    (stop,3,'STOP_NO_RETRY'), (bad,0,'UNKNOWN_NO_RETRY')]:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as tmp:
                calls=[];manifest=gate.gate_manifest();dest=Path(tmp)/'attempt'
                def transport(*args,**kwargs):
                    calls.append(kwargs)
                    return code,json.dumps(value).encode()
                with patch.object(gate,'ssh_environment',return_value={}), \
                     patch.object(gate,'binding_digest',return_value=manifest['target_binding_sha256']):
                    result=gate.execute_once(dest,approval=gate.APPROVAL,
                        approved_remote_sha=gate.sha(gate.remote_script()),
                        approved_manifest_sha=remote.MANIFEST_SHA256,
                        approved_gate_sha=gate.gate_sha(),manifest=manifest,
                        loader=lambda role:SimpleNamespace(role='spain',known_hosts_path='fixture',
                            key_path='fixture',target_user='fixture',target_host='invalid.test'),
                        transport=transport)
                self.assertEqual(result['status'],expected)
                self.assertEqual(len(calls),1)
                self.assertEqual(calls[0]['timeout'],60)
                self.assertEqual(calls[0]['cap'],65536)
                self.assertEqual(json.loads((dest/'result.json').read_text()),result)
                self.assertNotIn('SECRET_SQL',json.dumps(result))
                with self.assertRaisesRegex(core.Stop,'^evidence_exists$'):gate.claim_directory(dest)

    def test_previous_approval_rejected_before_claim_or_transport(self):
        manifest=gate.gate_manifest()
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'attempt'
            with self.assertRaisesRegex(core.Stop,'^approval_binding$'):
                gate.execute_once(dest,approval=old_gate.APPROVAL,
                    approved_remote_sha=gate.sha(gate.remote_script()),
                    approved_manifest_sha=remote.MANIFEST_SHA256,
                    approved_gate_sha=gate.gate_sha(),manifest=manifest,
                    loader=lambda *a:self.fail('target read'),transport=lambda *a,**k:self.fail('SSH'))
            self.assertFalse(dest.exists())

    def test_preview_without_environment_or_transport(self):
        output=io.StringIO()
        with patch.object(gate,'run_transport',side_effect=AssertionError('SSH')), \
             patch.object(gate,'ssh_environment',side_effect=AssertionError('environment')), \
             contextlib.redirect_stdout(output):
            self.assertEqual(gate.main([]),0)
        self.assertEqual(json.loads(output.getvalue())['ssh_attempts'],0)


if __name__ == '__main__':
    unittest.main()
