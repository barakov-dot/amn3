import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

AVAILABLE=importlib.util.find_spec('scripts.phase16_bot_candidate_diagnostic') is not None
if AVAILABLE:from scripts import phase16_bot_candidate_diagnostic as gate

class Availability(unittest.TestCase):
    def test_component_diagnostic_exists(self):self.assertTrue(AVAILABLE)

@unittest.skipUnless(AVAILABLE,'availability fails first')
class DiagnosticTests(unittest.TestCase):
    def test_real_candidate_wrapper_keeps_inner_settings_reason_without_secret(self):
        from scripts import phase16_bot_candidate_admission as candidate
        env=gate.remote_definitions()
        inventory=Path('research/amn2/phase16-bot-stage-readback-inventory-2026-09-29.json').read_bytes()
        class Client:
            def bus_property(self,*args):raise RuntimeError('PRIVATE_TOKEN_VALUE')
        stage=lambda raw:dict(status='VERIFIED',saved_receipt_sha256=candidate.SAVED_RECEIPT_SHA256)
        with patch.object(candidate.readback,'observe',stage),patch.object(candidate.os,'getgrouplist',lambda *a:[],create=True):
            original_settings=candidate.settings.collect_live
            with self.assertRaises(candidate.AdmissionError) as caught:
                env['diagnose_candidate'](candidate,Client(),inventory)
            self.assertIs(candidate.settings.collect_live,original_settings)
            self.assertIs(candidate.readback.observe,stage)
        self.assertEqual(str(caught.exception),'candidate_collection_failed')
        self.assertEqual(env['COMPONENTS']['settings']['status'],'STOP')
        self.assertEqual(env['COMPONENTS']['settings']['reason'],'settings_collection_failed')
        self.assertNotIn('PRIVATE_TOKEN_VALUE',json.dumps(env['COMPONENTS']))
        self.assertNotIn('bootstrap',env['COMPONENTS'])
    def test_deadline_propagates_and_hooks_restore(self):
        from scripts import phase16_bot_candidate_admission as candidate
        env=gate.remote_definitions()
        inventory=Path('research/amn2/phase16-bot-stage-readback-inventory-2026-09-29.json').read_bytes()
        def settings(client):raise env['ReadbackDeadline']('deadline')
        with patch.object(candidate.readback,'observe',lambda raw:dict(status='VERIFIED',saved_receipt_sha256=candidate.SAVED_RECEIPT_SHA256)),patch.object(candidate.settings,'collect_live',settings),patch.object(candidate.os,'getgrouplist',lambda *a:[],create=True):
            with self.assertRaises(KeyboardInterrupt):env['diagnose_candidate'](candidate,object(),inventory)
            self.assertIs(candidate.settings.collect_live,settings)
        self.assertEqual(env['COMPONENTS']['settings']['status'],'STARTED')
    def test_command_failure_is_visible_inside_bootstrap_wrapper(self):
        from scripts import phase16_bot_candidate_admission as candidate
        env=gate.remote_definitions()
        inventory=Path('research/amn2/phase16-bot-stage-readback-inventory-2026-09-29.json').read_bytes()
        class Client:
            def run(self,*args):raise gate.packet.core.Stop('command_failed')
        class NativeTreeFixture:
            def __init__(self,*args):pass
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def stable(self):pass
        with patch.object(candidate.readback,'observe',lambda raw:dict(status='VERIFIED',saved_receipt_sha256=candidate.SAVED_RECEIPT_SHA256)),patch.object(candidate.settings,'collect_live',lambda client:{}),patch.object(candidate.bootstrap,'BoundTree',NativeTreeFixture),patch.object(candidate.os,'getgrouplist',lambda *a:[],create=True):
            with self.assertRaises(candidate.AdmissionError):env['diagnose_candidate'](candidate,Client(),inventory)
        self.assertIn('readonly_command',env['COMPONENTS'])
        self.assertEqual(env['COMPONENTS']['readonly_command']['reason'],'command_failed')
        self.assertEqual(env['COMPONENTS']['bootstrap']['reason'],'bootstrap_collection_failed')
    def test_success_keeps_real_runtime_access_proof_unchanged(self):
        import contextlib
        from types import MappingProxyType
        from scripts import phase16_bot_candidate_admission as m
        from tests.test_phase16_bot_stage_access import StageAccessTests
        fixture=StageAccessTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        cfg=('home = /usr/bin\ninclude-system-site-packages = false\nversion = 3.12.3\nexecutable = /usr/bin/python3.12\ncommand = /usr/bin/python3 -m venv '+m.STAGE+'/runtime-venv\n').encode()
        fixture.write('runtime-venv/pyvenv.cfg',cfg)
        runtime_pin,bootstrap_pin=fixture.pins;path='payload/wheelhouse/runtime/'+runtime_pin.file
        fixture.write(path,fixture.wheels[runtime_pin.file])
        cat=m.Catalog({},MappingProxyType({path:runtime_pin}),MappingProxyType(fixture.source_pins))
        props=dict(User='amn2-spain',Group='amn2-spain',SupplementaryGroups=[],DynamicUser=False)
        class Client:
            def bus_property(self,unit,interface,name,signature):return props[name]
        class IdentityReader:
            def __call__(self,path):return b'amn2-spain:x:1001:1001:app:/app:/bin/false\n' if path=='/etc/passwd' else b'amn2-spain:x:1001:\n'
            def stable(self):pass
        class StageContext:
            def __enter__(self):self.reader=fixture.reader();return self
            def __exit__(self,*args):pass
            def read_file(self,*args,**kwargs):return self.reader.read_file(*args,**kwargs)
            def __getattr__(self,name):return getattr(self.reader,name)
        env=gate.remote_definitions()
        with contextlib.ExitStack() as stack:
            for target,value in [('catalog',lambda raw:cat),('readback.observe',lambda inv:dict(status='VERIFIED',saved_receipt_sha256=m.SAVED_RECEIPT_SHA256)),('settings.collect_live',lambda client:dict(vps_apply_enabled=False)),('settings.RootSettingsReader',IdentityReader),('bootstrap.collect_live',lambda client:(bootstrap_pin,fixture.wheels[bootstrap_pin.file],{})),('access.UnixStageReader',StageContext),('os.getgrouplist',lambda name,gid:[1001]),('platform.python_version',lambda:'3.12.3')]:stack.enter_context(patch('scripts.phase16_bot_candidate_admission.'+target,value,create=True))
            proof=env['diagnose_candidate'](m,Client(),b'bound fixture')
        self.assertEqual(proof.status,'CANDIDATE_CONTENT_VERIFIED_ACCESS_NOT_APPLIED')
        self.assertEqual(proof.access_plan.status,'ACCESS_PLAN_READY_NOT_APPLIED')
        self.assertEqual(env['COMPONENTS']['access_plan']['status'],'PASS')
        self.assertEqual(env['COMPONENTS']['collection']['status'],'PASS')

    def test_actual_content_access_reasons_keep_parent_allowlist_unchanged(self):
        from scripts import phase16_bot_stage_access as access
        from scripts import phase16_bot_runtime_content as runtime
        env=gate.remote_definitions()
        for label,operation,reason,kind in (
            ('access_plan',lambda:access._require(False,'ancestor_access'),'ancestor_access',access.AccessError),
            ('runtime_expected',lambda:runtime.build_expected({},()),'wheel_inventory',runtime.ContentError)):
            with self.subTest(reason=reason):
                owner=SimpleNamespace(run=operation);undo=[]
                env['watch'](owner,'run',label,undo)
                try:
                    with self.assertRaises(kind) as caught:owner.run()
                finally:env['restore'](undo)
                self.assertEqual(env['COMPONENTS'][label]['reason'],reason)
                self.assertEqual(env['safe_reason'](caught.exception),'UNCLASSIFIED_ERROR')
                self.assertIsNone(env['summary'](json.dumps({'reason':reason}))['reason'])
                receipt=self.fixture();receipt['component_steps']={label:env['COMPONENTS'][label]}
                gate.validate_receipt(receipt,0)

    def test_unknown_exception_text_is_never_telemetry(self):
        env=gate.remote_definitions()
        def operation():raise ValueError('PRIVATE_TOKEN_VALUE')
        owner=SimpleNamespace(run=operation);undo=[]
        env['watch'](owner,'run','settings',undo)
        with self.assertRaises(ValueError):owner.run()
        env['restore'](undo)
        self.assertIs(owner.run,operation)
        self.assertEqual(env['COMPONENTS']['settings']['reason'],'UNCLASSIFIED_ERROR')
        self.assertNotIn('PRIVATE_TOKEN_VALUE',json.dumps(env['COMPONENTS']))
    def fixture(self):
        from tests.test_phase16_bot_maintenance_readback import ReadbackTests
        value=ReadbackTests().success_fixture()
        value.update(schema='phase16.candidate-component-diagnostic.v1',approval=gate.APPROVAL,status='DIAGNOSTIC_COLLECTED_NOT_ADMITTED',reason='bounded_component_observation',component_steps={'settings':{'calls':1,'status':'STOP','reason':'settings_collection_failed','exception_kind':'SettingsError','returned_status':None}})
        return value
    def test_receipt_accepts_diagnostic_but_never_admission(self):gate.validate_receipt(self.fixture(),0)
    def test_receipt_rejects_secret_or_arbitrary_component(self):
        for key,value in [('reason','PRIVATE_TOKEN_VALUE'),('exception_kind','PRIVATE_TOKEN_VALUE'),('status','ADMITTED')]:
            obj=self.fixture();obj['component_steps']['settings'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):gate.validate_receipt(obj,0)
        obj=self.fixture();obj['component_steps']['PRIVATE_PATH']=obj['component_steps'].pop('settings')
        with self.assertRaises(ValueError):gate.validate_receipt(obj,0)
    def test_remote_scope_and_unknown_exit_are_strict(self):
        obj=self.fixture();obj['database_open']=1
        with self.assertRaises(ValueError):gate.validate_receipt(obj,0)
        env=gate.remote_definitions()
        with patch.object(env['sys'],'platform','win32'):value=env['main'](gate.APPROVAL)
        self.assertEqual(value['status'],'UNKNOWN_NO_RETRY');gate.validate_receipt(value,3)
        with self.assertRaises(ValueError):gate.validate_receipt(value,0)
    def test_wrong_approval_never_loads_protected_binding(self):
        def forbidden(_):self.fail('protected binding loaded before exact approval validation')
        with self.assertRaises(ValueError):gate.execute_once(gate.expected_manifest(),approval='wrong',manifest_sha='0'*64,remote_sha='0'*64,loader=forbidden)
    def test_default_preview_keeps_new_claim_absent_and_wire_bounded(self):
        self.assertFalse(gate.EVIDENCE.exists());value=gate.preview()
        self.assertEqual(value['ssh_attempts'],0)
        self.assertEqual(value['database_open'],0)
        self.assertEqual(value['service_actions'],0)
        self.assertFalse(gate.EVIDENCE.exists())
        self.assertLessEqual(gate.base.old.command_units([gate.wire(gate.script())])+2048,30000)

if __name__=='__main__':unittest.main()
