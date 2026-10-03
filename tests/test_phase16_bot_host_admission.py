"""Composition boundaries and real-file continuity; no native host claim."""
import copy
import importlib
from dataclasses import asdict
import unittest
from tests import test_phase16_bot_stage_access as access_fixture
try:
    host=importlib.import_module('scripts.phase16_bot_host_admission')
except ModuleNotFoundError as e:
    if e.name!='scripts.phase16_bot_host_admission':raise
    host=None

class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(host,'host admission composition missing')
        self.fixture=access_fixture.StageAccessTests('test_plan_grants_only_verified_content_and_seals_wrappers')
        self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.plan=self.fixture.build();self.fixture.apply_fixture(self.plan)
    def capture(self):return host.capture_stage(self.plan,self.fixture.reader())
    def test_real_bytes_then_continuity_accepts_unchanged_tree(self):
        proof=self.capture()
        self.assertEqual(host.check_stage(proof,self.fixture.reader()),proof['source_sha256'])
        self.assertEqual(proof['scope'],'VERIFIED_CONTENT_THEN_METADATA_CONTINUITY')
    def test_same_size_content_change_is_rejected(self):
        proof=self.capture();self.fixture.write('source/app/main.py',b'VALUE = 9\n')
        with self.assertRaises(Exception):host.check_stage(proof,self.fixture.reader())
    def test_unexpected_file_is_rejected(self):
        proof=self.capture();self.fixture.write('source/app/extra.py',b'x=1\n')
        with self.assertRaises(Exception):host.check_stage(proof,self.fixture.reader())
    def test_acl_change_is_rejected(self):
        proof=self.capture();self.fixture.acls['source/app/main.py']=('system.posix_acl_access',)
        with self.assertRaises(Exception):host.check_stage(proof,self.fixture.reader())
    def test_capture_does_not_certify_tampered_bytes(self):
        self.fixture.write('source/app/main.py',b'VALUE = 9\n')
        with self.assertRaises(Exception):self.capture()
    def test_link_retarget_rejected(self):
        proof=self.capture();self.fixture.links['runtime-venv/bin/python3']='/tmp/python'
        with self.assertRaises(Exception):host.check_stage(proof,self.fixture.reader())
    def test_plan_roundtrip_and_hash_binding(self):
        self.assertEqual(host.plan_from_json(asdict(self.plan)),self.plan)
        value=asdict(self.plan);value['objects'][0]['desired_gid']=9
        with self.assertRaises(Exception):host.plan_from_json(value)

class DossierTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(host)
        from tests.test_phase16_bot_maintenance_binding import observations,ownership,NOW
        self.obs,self.owner,self.now=observations(),ownership(),NOW
        self.dossier={'schema':'phase16.host-admission.v1','operation_id':self.obs['operation_id'],
            'boot_id':self.obs['boot_id'],'target_binding_sha256':self.obs['target_binding_sha256'],
            'approval_scope_sha256':'e'*64,'writer_declaration':{'valid_until':self.owner['valid_until']},
            'writer_initial':{'inventory':self.obs['inventory'],'evidence':{'provenance':'LINUX_PROCFS_ROOT'}},
            'stage_continuity':{},'legacy_runtime':{'rollback':self.obs['rollback']},
            'effective_settings':{k:v for k,v in self.obs['settings'].items() if k!='startup_bound_seconds'},'units_identity':{},
            'service_access':{},'startup_assessment':{'startup_observation_budget_seconds':self.obs['settings']['startup_bound_seconds']}}
    def prepare(self):return host.prepare_bound(self.obs,self.owner,self.dossier,now=self.now)
    def test_dossier_hash_is_authenticated_by_prepared_observation(self):
        prepared,obs=self.prepare()
        host.validate_saved(prepared,obs,self.owner,self.dossier)
        self.assertNotEqual(obs['inventory']['scan_sha256'],self.obs['inventory']['scan_sha256'])
        self.dossier['approval_scope_sha256']='a'*64
        with self.assertRaises(host.core.Stop):host.validate_saved(prepared,obs,self.owner,self.dossier)
    def test_shorter_writer_lease_cannot_be_extended_by_ownership(self):
        self.dossier['writer_declaration']['valid_until']=self.now
        with self.assertRaises(host.core.Stop):self.prepare()
    def test_injected_proc_fixture_cannot_be_live_proof(self):
        self.dossier['writer_initial']['evidence']['provenance']='NOT_LIVE'
        with self.assertRaises(host.core.Stop):self.prepare()
    def test_wrong_operation_refused(self):
        self.dossier['operation_id']='phase16-other'
        with self.assertRaises(host.core.Stop):self.prepare()

    def test_observation_settings_cannot_diverge_from_live_dossier(self):
        self.dossier['effective_settings']['network_cidr']='10.212.12.0/24'
        with self.assertRaisesRegex(host.core.Stop,'host_cross_binding'):self.prepare()
    def test_observation_rollback_cannot_diverge(self):
        self.dossier['legacy_runtime']={'rollback':dict(source_sha256='f'*64,dependencies_sha256='d'*64)}
        with self.assertRaisesRegex(host.core.Stop,'host_cross_binding'):self.prepare()

class HostGuardTests(unittest.TestCase):
    setUp=ContinuityTests.setUp
    def test_saved_json_and_fresh_kernel_tuple_represent_same_database(self):
        import json
        from types import SimpleNamespace
        from unittest.mock import patch,Mock
        from scripts import phase16_bot_maintenance_binding as binding
        from tests.test_phase16_bot_maintenance_binding import observations,ownership,NOW
        obs,owner=observations(),ownership()
        evidence={'provenance':'LINUX_PROCFS_ROOT','units':{},'database_identities':{'database':(1,2,3),'wal':None}}
        dossier=dict(schema='phase16.host-admission.v1',operation_id=obs['operation_id'],boot_id=obs['boot_id'],
            target_binding_sha256=obs['target_binding_sha256'],approval_scope_sha256='e'*64,
            writer_declaration={'valid_until':owner['valid_until']},writer_initial={'inventory':obs['inventory'],'evidence':evidence},
            stage_continuity={'plan':asdict(self.plan)},legacy_runtime={'rollback':obs['rollback']},
            effective_settings={k:v for k,v in obs['settings'].items() if k!='startup_bound_seconds'},units_identity={},
            startup_assessment={'startup_observation_budget_seconds':obs['settings']['startup_bound_seconds']},
            service_access={'status':'KERNEL_STAGE_ACCESS_OBSERVED_NOT_HOST_ADMITTED','plan_sha256':self.plan.digest,
                'bot_identity_sha256':host.core.digest({})})
        prepared,obs=host.prepare_bound(obs,owner,dossier,now=NOW)
        records=json.loads(host.core.encoded({'host-admission':dossier,'observation':obs,'ownership':owner}))
        guard=host.HostAdmission.__new__(host.HostAdmission)
        guard.supervisor=SimpleNamespace(utc_now=lambda:binding.timestamp(NOW).timestamp(),clock=lambda:0)
        guard.client=Mock();guard.records=records;guard.prepared=prepared;guard.proof=records['host-admission'];guard.source=Mock()
        with patch.object(host,'saved_records',return_value=records),patch.object(host,'unit_facts',return_value=(obs['units'],{})), \
            patch('scripts.phase16_bot_maintenance_jobs.boot_id',return_value=obs['boot_id']), \
            patch('scripts.phase16_bot_effective_settings.collect_live',return_value=dossier['effective_settings']), \
            patch('scripts.phase16_bot_legacy_runtime_proof.check_saved'), \
            patch('scripts.phase16_bot_service_access_probe.LinuxObserver') as observer, \
            patch('scripts.phase16_bot_service_access_probe.validate_snapshot'), \
            patch('scripts.phase16_bot_writer_admission.collect_writer_admission',return_value={'evidence':evidence}):
            observer.return_value.snapshot.return_value={}
            self.assertEqual(guard(prepared),prepared['prepared_sha256'])
