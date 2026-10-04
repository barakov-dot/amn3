"""Read-only boundary telemetry: real bytes, portable Unix metadata; no egress."""
import copy
import importlib
import json
from pathlib import Path
import shlex
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from tests.test_phase16_bot_stage_access import StageAccessTests
try:g=importlib.import_module('scripts.phase16_bot_private_boundary_readback')
except ModuleNotFoundError:g=None

class BoundaryReadbackTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(g,'readback gate absent')
    def test_embedded_readback_helper_source_drift_rejected(self):
        original=g.packet.canonical
        def drift(path):
            raw=original(path)
            return raw+b'\n# changed helper\n' if Path(path).resolve()==Path(g.base.__file__).resolve() else raw
        with patch.object(g.packet,'canonical',side_effect=drift):
            with self.assertRaisesRegex(ValueError,'predecessor_changed'):g.script()
    def fixture(self):
        f=StageAccessTests();f.setUp();self.addCleanup(f.doCleanups);return f
    def good(self):
        t=g.trigger();s=dict(parent_after=t['local_result']['receipt']['operation']['parent_after'],stage_root=g.expected_roots()[1],objects={},blocked_objects=['claim.json','result.json'],repair_result=dict(bytes=479,sha256=g.REPAIR_RESULT_SHA),units_before=g.v2.v1.witness()['units_before'],units_after=g.v2.v1.witness()['units_before'])
        for n in g.NAMES:s['objects'][n]=dict(kind='directory' if n in ('payload','scratch') else 'file',mode=0o700 if n in ('payload','scratch') else 0o644,uid=0,gid=0,device=64770,inode=10+len(s['objects']),size=1,nlink=2 if n in ('payload','scratch') else 1,mtime_ns=1,ctime_ns=1,acl_clear=True,acl_count=0,private=n in ('payload','scratch'))
        return dict(schema=g.SCHEMA,approval=g.APPROVAL,original_manifest_sha256=g.base.ORIGINAL,target_binding_sha256=g.packet.entry.binding.TARGET,trigger_execution_sha256=g.TRIGGER_SHA,status='BOUNDARY_READBACK_COLLECTED_NOT_ADMITTED',reason='bounded_private_metadata',snapshot=s,remote_file_writes=0,permission_syscalls=0,database_open=0,service_actions=0,app_imports=0,activation=False,replay_allowed=False)
    def test_preview_and_manifest_are_zero_egress_frozen57(self):
        with patch.object(g.packet.transport,'run_transport',side_effect=AssertionError('egress')):
            m=g.expected_manifest();self.assertEqual(len(m['original_artifacts_sha256_lf']),57);self.assertEqual(g.preview()['ssh_attempts'],0)
            self.assertEqual(m,json.loads(g.MANIFEST.read_bytes()))
    def test_four_objects_and_readable_json_are_reported_without_content_read(self):
        f=self.fixture();f.attributes.update({'claim.json':(0o644,0,0),'result.json':(0o644,0,0)})
        e=g.remote_definitions();reader=f.reader()
        with patch.object(reader,'read_file',side_effect=AssertionError('private content')):
            rows,blocked=e['inspect_boundaries'](reader)
        self.assertEqual(set(rows),set(g.NAMES));self.assertEqual(blocked,['claim.json','result.json']);self.assertTrue(rows['payload']['private'])
    def test_wrong_kind_and_writable_owner_are_closed(self):
        for n,attrs in [('claim.json',(0o666,0,0)),('payload',(0o700,1001,0))]:
            f=self.fixture();f.attributes[n]=attrs
            with self.assertRaises(Exception):g.remote_definitions()['inspect_boundaries'](f.reader())
        f=self.fixture();f.links['claim.json']='private-target';f.attributes['claim.json']=(0o777,0,0)
        with self.assertRaises(Exception):g.remote_definitions()['inspect_boundaries'](f.reader())
    def test_acl_names_do_not_escape_and_continuity_failure_closes(self):
        f=self.fixture();f.acls['claim.json']=('sensitive-xattr-name',)
        rows,blocked=g.remote_definitions()['inspect_boundaries'](f.reader())
        self.assertFalse(rows['claim.json']['acl_clear']);self.assertEqual(rows['claim.json']['acl_count'],1);self.assertNotIn('sensitive-xattr-name',json.dumps(rows))
        reader=f.reader()
        with patch.object(reader,'stable',side_effect=ValueError('changed_during_read')):
            with self.assertRaises(Exception):g.remote_definitions()['inspect_boundaries'](reader)
    def test_success_receipt_binding_and_inconsistent_blocked_modes_reject(self):
        r=self.good();g.validate_receipt(r,0)
        for key,value in [('permission_syscalls',1),('approval',g.v2.APPROVAL),('remote_file_writes',True)]:
            bad=copy.deepcopy(r);bad[key]=value
            with self.assertRaises(Exception):g.validate_receipt(bad,0)
        for mutate in (lambda s:s.update(blocked_objects=[]),lambda s:s['parent_after'].update(inode=99),lambda s:s['repair_result'].update(sha256='0'*64),lambda s:s['objects']['claim.json'].update(private=True)):
            bad=copy.deepcopy(r);mutate(bad['snapshot'])
            with self.assertRaises(Exception):g.validate_receipt(bad,0)
    def test_existing_claim_and_wrong_digest_do_not_reach_loader(self):
        with tempfile.TemporaryDirectory() as d,patch.object(g,'EVIDENCE',Path(d)):
            m=g.expected_manifest()
            with self.assertRaises(Exception):g.execute_once(m,approval=g.APPROVAL,manifest_sha=g.packet.core.digest(m),remote_sha=g.packet.sha(g.script()),loader=lambda r:self.fail('loader'))
        m=g.expected_manifest()
        with self.assertRaises(Exception):g.execute_once(m,approval=g.APPROVAL,manifest_sha='0'*64,remote_sha=g.packet.sha(g.script()),loader=lambda r:self.fail('loader'))
    def test_actual_launcher_windows_fails_closed_without_mutation(self):
        tokens=shlex.split(g.wire(g.script()));self.assertEqual(tokens[-1],g.APPROVAL)
        p=subprocess.run([sys.executable,'-I','-S','-B','-c',tokens[5],g.APPROVAL],capture_output=True)
        self.assertEqual(p.returncode,3);self.assertEqual(p.stderr,b'');r=g.validate_receipt(json.loads(p.stdout),3);self.assertEqual(r['status'],'UNKNOWN_NO_RETRY');self.assertIsNone(r['snapshot'])
    def test_consumed_v2_and_private_mode_policy_preserved(self):
        m=g.expected_manifest();self.assertEqual(m['limits']['remote_seconds'],45);self.assertEqual(m['limits']['transport_seconds'],60)
        self.assertEqual(g.packet.sha(g.packet.canonical(Path(g.v2.__file__))),g.FROZEN_V2_SHA)
        f=self.fixture();f.attributes['claim.json']=(0o644,0,0)
        with self.assertRaisesRegex(Exception,'private_boundary'):f.build()
if __name__=='__main__':unittest.main()
