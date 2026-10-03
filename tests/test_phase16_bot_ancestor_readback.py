"""Four fixed ancestor facts; no permission repair or candidate replay."""
import importlib.util
import json
import stat
import unittest
from unittest.mock import patch
AVAILABLE=importlib.util.find_spec('scripts.phase16_bot_ancestor_readback') is not None
if AVAILABLE:from scripts import phase16_bot_ancestor_readback as gate
class Availability(unittest.TestCase):
    def test_ancestor_facts_packet_exists(self):self.assertTrue(AVAILABLE)
@unittest.skipUnless(AVAILABLE,'availability fails first')
class AncestorTests(unittest.TestCase):
    def fixture(self):
        from tests.test_phase16_bot_stage_access import StageAccessTests
        f=StageAccessTests();f.setUp();self.addCleanup(f.doCleanups);return f
    def facts(self,f):
        env=gate.remote_definitions();return env['ancestor_facts'](gate.packet.entry.access,f.reader(),f.identity)
    def test_blocked_fixed_parent_is_reported_without_repair(self):
        f=self.fixture();before=f.ancestors[3][1].st_mode;f.ancestors[3][1].st_mode=stat.S_IFDIR|0o700
        value=self.facts(f)
        self.assertFalse(value['ancestor_ready'])
        blocked=[path for path,row in value['ancestors'].items() if not row['service_traverse']]
        self.assertEqual(blocked,['/opt/amn2-spain/bot-candidates'])
        self.assertEqual(f.ancestors[3][1].st_mode,stat.S_IFDIR|0o700)
        self.assertEqual(value['stage_root']['mode'],0o700)
        self.assertFalse(value['stage_root']['service_traverse'])
    def test_stage_private_state_is_separate_from_ancestor_readiness(self):
        value=self.facts(self.fixture());self.assertTrue(value['ancestor_ready'])
        self.assertFalse(value['stage_root']['service_traverse'])
    def test_acl_names_are_never_emitted(self):
        f=self.fixture();path,meta,_=f.ancestors[2];f.ancestors[2]=(path,meta,('PRIVATE_TOKEN_VALUE',))
        value=self.facts(f);self.assertFalse(value['ancestor_ready'])
        self.assertFalse(value['ancestors'][path]['acl_clear']);self.assertNotIn('PRIVATE_TOKEN_VALUE',json.dumps(value))
    def test_extra_or_wrong_parent_is_rejected(self):
        f=self.fixture();f.ancestors.pop()
        with self.assertRaises(ValueError):self.facts(f)
    def receipt(self,facts,identity):
        from tests.test_phase16_bot_maintenance_readback import ReadbackTests
        old=ReadbackTests().success_fixture();value=gate.platform_fixture()
        env=gate.remote_definitions()
        old['snapshot']['units_before']={u:dict(state='OBSERVED',properties={key:(u if key=='Id' else '') for key in env['FIELDS']}) for u in env['UNITS']}
        value.update(status='ANCESTOR_FACTS_COLLECTED_NOT_REPAIRED',reason='bounded_ancestor_observation',failure_boundary=None,snapshot=dict(**facts,service_identity=dict(uid=identity.uid,gid=identity.gid,supplementary_gids=[identity.gid]),units_before=old['snapshot']['units_before'],units_after=old['snapshot']['units_before']))
        return value
    def test_numeric_receipt_scope_and_derived_access_are_validated(self):
        value=gate.platform_fixture();gate.validate_receipt(value,3)
        value['permission_actions']=1
        with self.assertRaises(ValueError):gate.validate_receipt(value,3)
        f=self.fixture();facts=self.facts(f);value=self.receipt(facts,f.identity);gate.validate_receipt(value,0)
        path=gate.ANCESTORS[0];value['snapshot']['ancestors'][path]['service_traverse']=False
        with self.assertRaises(ValueError):gate.validate_receipt(value,0)
    def test_unknown_or_arbitrary_path_is_rejected(self):
        f=self.fixture();value=self.receipt(self.facts(f),f.identity)
        value['snapshot']['ancestors']['PRIVATE_PATH']=value['snapshot']['ancestors'].pop(gate.ANCESTORS[0])
        with self.assertRaises(ValueError):gate.validate_receipt(value,0)
    def test_real_collect_reads_only_native_metadata_identity_boundaries(self):
        import contextlib
        from scripts import phase16_bot_candidate_admission as candidate
        f=self.fixture();f.ancestors[3][1].st_mode=stat.S_IFDIR|0o700
        env=gate.remote_definitions();units=self.receipt(self.facts(f),f.identity)['snapshot']['units_before']
        props=dict(User='amn2-spain',Group='amn2-spain',SupplementaryGroups=[],DynamicUser=False)
        class Client:
            def bus_property(self,unit,interface,name,signature):return props[name]
        class AccountReader:
            def __call__(self,path):
                if path=='/etc/passwd':return b'amn2-spain:x:1001:1001:app:/app:/bin/false\n'
                if path=='/etc/group':return b'amn2-spain:x:1001:amn2-spain\n'
                raise AssertionError('unexpected account input')
            def stable(self):pass
        class BootPath:
            def __init__(self,path):self.asserted=path=='/proc/sys/kernel/random/boot_id';assert self.asserted
            def read_text(self):return gate.packet.entry.BOOT
        env['_phase16_import_root']=lambda *args:None;env['Path']=BootPath;env['unit_states']=lambda:units
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(gate.packet.entry.linux,'SystemdClient',lambda *a:Client()))
            stack.enter_context(patch.object(candidate.settings,'RootSettingsReader',AccountReader))
            stack.enter_context(patch.object(candidate.access,'UnixStageReader',lambda:contextlib.nullcontext(f.reader())))
            stack.enter_context(patch.object(candidate.os,'getgrouplist',lambda *a:[1001],create=True))
            stack.enter_context(patch.object(candidate,'collect_live',lambda *a:self.fail('candidate replay')))
            stack.enter_context(patch.object(candidate.settings,'collect_live',lambda *a:self.fail('effective settings scan')))
            value=env['collect']()
        self.assertFalse(value['ancestor_ready']);self.assertEqual(value['service_identity']['uid'],1001)
        self.assertEqual(value['units_before'],value['units_after'])
    def test_budget_expiry_survives_main_as_unknown(self):
        env=gate.remote_definitions();env['READBACK_STARTED']=0
        with patch.object(env['sys'],'platform','linux'),patch.object(env['os'],'geteuid',lambda:0,create=True):value=env['main'](gate.APPROVAL)
        self.assertEqual(value['status'],'UNKNOWN_NO_RETRY');self.assertEqual(value['reason'],'deadline')
        gate.validate_receipt(value,3)
    def test_wrong_approval_stops_before_protected_loader(self):
        def forbidden(_):self.fail('protected binding read')
        with self.assertRaises(ValueError):gate.execute_once(gate.expected_manifest(),approval='wrong',manifest_sha='0'*64,remote_sha='0'*64,loader=forbidden)
    def test_default_preview_never_claims_or_executes(self):
        self.assertFalse(gate.EVIDENCE.exists());value=gate.preview();self.assertEqual(value['ssh_attempts'],0)
        self.assertEqual(value['remote_seconds'],30);self.assertEqual(value['transport_seconds'],45)
        self.assertFalse(gate.EVIDENCE.exists());self.assertLessEqual(gate.base.old.command_units([gate.wire(gate.script())])+2048,30000)
if __name__=='__main__':unittest.main()
