"""Real executor with portable Unix metadata model; no native permission writes."""
import copy
import importlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from scripts import phase16_bot_ancestor_repair_gate as v1
from scripts.vps.phase16_bot_retained_stage_remote import SecureReader,fingerprint
from tests.test_phase16_bot_ancestor_repair import FS,Journal
try:g=importlib.import_module('scripts.phase16_bot_ancestor_repair_v2_gate')
except ModuleNotFoundError:g=None

FIXTURE='phase16-readback-guard-20260922-001'
class CapturingJournal(Journal):
    def __init__(self,fs):super().__init__(fs);self.data=[]
    def create(self,name,raw):self.data.append((name,json.loads(raw)));super().create(name,raw)

class V2Tests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(g,'new v2 gate absent')
        self.witness=v1.witness();self.fs=FS(self.witness);self.addCleanup(lambda:self.assertFalse(self.fs.handles))
    def add_sibling(self,name,**changes):
        row={**self.witness['stage_root'],'inode':999};row.update(changes);self.fs.add(g.v1.repair.PARENT+'/'+name,row)
    def run_model(self,name=FIXTURE):
        self.add_sibling(name)
        env=g.remote_definitions();core=env['repair'];s=core.parent_session(SecureReader,fingerprint)(self.witness,syscalls=self.fs).__enter__()
        journal=CapturingJournal(self.fs)
        try:
            s.preflight();result=core.apply(s,journal,lambda:None,lambda:dict(status='STOP',reason='runtime_not_proven'),{'approval':g.APPROVAL})
        finally:s.close()
        return result,journal
    def test_historical_fixture_reproduces_consumed_v1_stop_before_writes(self):
        self.add_sibling(FIXTURE)
        with self.assertRaisesRegex(Exception,'sibling_inventory'):
            with v1.repair.parent_session(SecureReader,fingerprint)(self.witness,syscalls=self.fs) as session:session.preflight()
        self.assertEqual(self.fs.actions,[])
    def test_private_historical_fixture_passes_new_predicate(self):
        result,journal=self.run_model();self.assertTrue(result['parent_verified'])
        self.assertEqual(result['completed_syscalls'],2)
        self.assertEqual([e for e in self.fs.actions if e[0] in ('chown','chmod')],[('chown',v1.repair.PARENT,-1,61212),('chmod',v1.repair.PARENT,0o710)])
        self.assertEqual(self.fs.nodes[v1.repair.PARENT+'/'+FIXTURE].st_mode&0o777,0o700)
        self.assertTrue(all(g.OP in name for name,_ in journal.data))
    def test_arbitrary_private_sibling_names_never_leave_memory(self):
        name='private-sensitive-name'
        result,journal=self.run_model(name)
        self.assertTrue(result['parent_verified']);self.assertNotIn(name,json.dumps(journal.data));self.assertNotIn(name,json.dumps(result))
        plan=next(d for n,d in journal.data if '.plan.' in n)
        self.assertEqual(len(plan['siblings']),2)
        self.assertTrue(all(len(key)==64 for key in plan['siblings']))
    def test_file_link_readable_group_owned_acl_reject_before_any_audit(self):
        import stat
        for attr,value in (('st_mode',stat.S_IFREG|0o600),('st_mode',stat.S_IFLNK|0o700),('st_mode',stat.S_IFDIR|0o750),('st_gid',61212),('attrs',('acl',))):
            with self.subTest(attr=attr,value=value):
                self.add_sibling(FIXTURE);node=self.fs.nodes[v1.repair.PARENT+'/'+FIXTURE];setattr(node,attr,value)
                env=g.remote_definitions();core=env['repair']
                with self.assertRaises(Exception):
                    with core.parent_session(SecureReader,fingerprint)(self.witness,syscalls=self.fs) as session:session.preflight()
                del self.fs.nodes[v1.repair.PARENT+'/'+FIXTURE]
        self.assertEqual(self.fs.actions,[])
    def test_missing_retained_root_and_inventory_bound_remain_closed(self):
        env=g.remote_definitions();core=env['repair'];node=self.fs.nodes.pop(v1.repair.STAGE)
        with self.assertRaises(Exception):
            with core.parent_session(SecureReader,fingerprint)(self.witness,syscalls=self.fs) as session:session.preflight()
        self.fs.nodes[v1.repair.STAGE]=node
        for i in range(16):self.add_sibling('private-'+str(i),inode=1000+i)
        with self.assertRaises(Exception):
            with core.parent_session(SecureReader,fingerprint)(self.witness,syscalls=self.fs) as session:session.preflight()
        self.assertEqual(self.fs.actions,[])
    def test_claim_directory_new_frozen_predecessors_and_original57(self):
        manifest=g.expected_manifest();self.assertEqual(manifest,json.loads(g.MANIFEST.read_bytes()))
        self.assertNotEqual(g.OP,v1.repair.OP);self.assertNotEqual(g.EVIDENCE,v1.EVIDENCE);self.assertNotEqual(g.APPROVAL,v1.APPROVAL)
        self.assertEqual(len(manifest['original_artifacts_sha256_lf']),57)
        self.assertEqual(v1.expected_manifest(),json.loads(v1.MANIFEST.read_bytes()))
        self.assertIn('root:root0700 directories',manifest['sibling_policy'])
    def test_default_preview_zero_egress_and_existing_claim_no_loader(self):
        with patch.object(g.packet.transport,'run_transport',side_effect=AssertionError('egress')):self.assertEqual(g.preview()['ssh_attempts'],0)
        with tempfile.TemporaryDirectory() as d,patch.object(g,'EVIDENCE',Path(d)):
            with self.assertRaises(Exception):g.execute_once(g.expected_manifest(),approval=g.APPROVAL,manifest_sha=g.packet.core.digest(g.expected_manifest()),remote_sha=g.packet.sha(g.script()),loader=lambda r:self.fail('binding reached'))
    def test_actual_stdin0_launcher_and_windows_closed_receipt(self):
        tokens=shlex.split(g.wire(g.script()));self.assertEqual(tokens[-1],g.APPROVAL)
        self.assertLessEqual(g.base.old.command_units([g.wire(g.script())])+2048,30000)
        p=subprocess.run([sys.executable,'-I','-S','-B','-c',tokens[5],g.APPROVAL],capture_output=True)
        self.assertEqual(p.returncode,3);self.assertEqual(p.stderr,b'')
        r=g.validate_receipt(json.loads(p.stdout),3);self.assertEqual(r['status'],'STOP_NO_REMOTE_CHANGE');self.assertEqual(r['approval'],g.APPROVAL)
    def test_predecessor_receipt_and_false_no_change_rejected(self):
        env=g.remote_definitions()
        with patch.object(env['sys'],'platform','win32'):r=env['main'](g.APPROVAL)
        g.validate_receipt(r,3)
        bad=dict(r);bad['approval']=v1.APPROVAL
        with self.assertRaises(Exception):g.validate_receipt(bad,3)
        bad=dict(r);bad['status']='STOP_NO_PERMISSION_CHANGE'
        with self.assertRaises(Exception):g.validate_receipt(bad,3)
if __name__=='__main__':unittest.main()
