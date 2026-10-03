"""Frozen new packet, default zero-egress, safe telemetry and one-attempt claim."""
import importlib
import json
from pathlib import Path
import tempfile
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
try:g=importlib.import_module('scripts.phase16_bot_ancestor_repair_gate')
except ModuleNotFoundError:g=None

class GateTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(g,'new gate absent')
    def test_preview_never_loads_binding_or_runs_transport(self):
        with patch.object(g.packet.transport,'run_transport',side_effect=AssertionError('egress')):
            p=g.preview()
        self.assertEqual(p['ssh_attempts'],0);self.assertEqual(p['status'],'OFFLINE_READY_NOT_EXECUTED')
    def test_render_frozen_closure_wire_limits_and_manifest(self):
        manifest=g.expected_manifest();self.assertEqual(json.loads(g.MANIFEST.read_bytes()),manifest)
        self.assertEqual(manifest['scope']['permission_syscalls_max'],2)
        self.assertEqual(len(manifest['original_artifacts_sha256_lf']),57)
        self.assertLessEqual(g.base.old.command_units([g.wire(g.script())])+2048,30000)
    def test_bad_approval_stops_before_loader(self):
        with self.assertRaises(Exception):g.execute_once(g.expected_manifest(),approval='bad',manifest_sha='0'*64,remote_sha='0'*64,loader=lambda r:self.fail('loader reached'))
    def test_existing_local_claim_rejects_without_loader(self):
        with tempfile.TemporaryDirectory() as d,patch.object(g,'EVIDENCE',Path(d)):
            with self.assertRaises(Exception):g.execute_once(g.expected_manifest(),approval=g.APPROVAL,manifest_sha=g.packet.core.digest(g.expected_manifest()),remote_sha=g.packet.sha(g.script()),loader=lambda r:self.fail('loader reached'))
    def test_windows_remote_fails_closed_without_writes(self):
        env=g.remote_definitions()
        with patch.object(env['sys'],'platform','win32'):
            r=env['main'](g.APPROVAL)
        self.assertEqual(r['status'],'STOP_NO_REMOTE_CHANGE');self.assertFalse(r['audit_creation_attempted']);self.assertIsNone(r['operation'])
        g.validate_receipt(r,3)
    def test_runtime_return_stop_captured_and_wrappers_restored(self):
        env=g.remote_definitions();runtime=SimpleNamespace(verify_installed=lambda *a,**k:SimpleNamespace(status='STOP',reason='wheel_inventory',runtime_status='NOT_PROVEN',bootstrap_status='NOT_PROVEN',scope='IMPORT_PATH_CONTENT',verified_files=0,verified_bytecode=0))
        undo=[];original=runtime.verify_installed
        env['watch_installed'](runtime,undo)
        runtime.verify_installed(None,None)
        self.assertEqual(env['INSTALLED']['reason'],'wheel_inventory');self.assertEqual(env['INSTALLED']['status'],'STOP')
        env['restore'](undo);self.assertIs(runtime.verify_installed,original)
    def test_runtime_reason_unknown_value_redacted(self):
        env=g.remote_definitions();runtime=SimpleNamespace(verify_installed=lambda *a,**k:SimpleNamespace(status='STOP',reason='secret-path',runtime_status='NOT_PROVEN',bootstrap_status='NOT_PROVEN',scope='IMPORT_PATH_CONTENT',verified_files=0,verified_bytecode=0))
        undo=[];env['watch_installed'](runtime,undo);runtime.verify_installed(None,None)
        self.assertNotIn('secret-path',json.dumps(env['INSTALLED']));self.assertEqual(env['INSTALLED']['reason'],'UNCLASSIFIED_ERROR');env['restore'](undo)
    def test_receipt_rejects_raw_extra_and_impossible_success(self):
        env=g.remote_definitions()
        with patch.object(env['sys'],'platform','win32'):r=env['main'](g.APPROVAL)
        for key,value in (('raw','secret'),('status','PARENT_REPAIRED_CANDIDATE_CHECKED')):
            bad=dict(r);bad[key]=value
            with self.assertRaises(Exception):g.validate_receipt(bad,0)
    def test_remote_audit_mkdir_is_exclusive_and_rebases_only_own_entry(self):
        from tests.test_phase16_bot_ancestor_repair import FS
        from scripts import phase16_bot_maintenance_storage as storage
        from scripts.phase16_bot_stage_access_apply import UnixJournal
        env=g.remote_definitions();base=storage.MAINTENANCE_ROOT
        meta=dict(mode=0o755,uid=0,gid=0,device=1,inode=1,mtime_ns=1,ctime_ns=1)
        fs=FS({'ancestors':{},'stage_root':meta})
        fs.nodes.clear()
        for i,path in enumerate(('/', '/var','/var/lib',storage.SERVICE_PARENT,base)):
            row={**meta,'inode':i+1}
            if path==storage.SERVICE_PARENT:row.update(uid=61212,gid=61212,mode=0o750)
            if path==base:row.update(mode=0o700)
            fs.add(path,row)
        def mkdir(name,mode,*,dir_fd):
            path=fs.name(name,dir_fd)
            if path in fs.nodes:raise FileExistsError('existing operation')
            fs.add(path,{**meta,'mode':mode,'inode':90})
            parent=fs.nodes[fs.handles[dir_fd]];parent.st_nlink+=1;parent.st_mtime_ns+=1;parent.st_ctime_ns+=1
        fs.mkdir=mkdir
        adapter=SimpleNamespace(MAINTENANCE_ROOT=base,MaintenanceReader=lambda path:storage.MaintenanceReader(path,syscalls=fs))
        journal=lambda path:UnixJournal(path,syscalls=fs)
        env['os']=fs
        with patch('sys.platform','linux'):
            with env['new_journal'](adapter,journal) as j:
                self.assertEqual(j.os.fstat(j.root_fd).st_mode&0o777,0o700)
                self.assertTrue(env['AUDIT_CREATION_ATTEMPTED'])
            self.assertFalse(fs.handles)
            env['AUDIT_CREATION_ATTEMPTED']=False
            with self.assertRaises(Exception):
                with env['new_journal'](adapter,journal):self.fail('duplicate op accepted')
            self.assertFalse(env['AUDIT_CREATION_ATTEMPTED']);self.assertFalse(fs.handles)
    def test_authenticated_launcher_passes_digest_without_shell_corruption(self):
        import shlex,subprocess
        raw=g.script();tokens=shlex.split(g.wire(raw))
        result=subprocess.run([sys.executable,'-I','-S','-B','-c',tokens[5],g.APPROVAL],capture_output=True,check=False)
        self.assertEqual(result.returncode,3);self.assertEqual(result.stderr,b'')
        g.validate_receipt(json.loads(result.stdout),3)
    def repaired_receipt(self):
        env=g.remote_definitions()
        with patch.object(env['sys'],'platform','win32'):r=env['main'](g.APPROVAL)
        after={k:g.witness()['ancestors'][g.repair.PARENT][k] for k in g.repair.FIELDS}
        after.update(mode=0o710,gid=61212,ctime_ns=after['ctime_ns']+10)
        r.update(status='PARENT_REPAIRED_CANDIDATE_CHECKED',reason='bounded_parent_change_candidate_readonly',audit_creation_attempted=True,operation=dict(status='PARENT_REPAIRED_CANDIDATE_CHECKED',reason='bounded_parent_change_candidate_readonly',permission_attempted=True,completed_syscalls=2,parent_verified=True,parent_after=after,candidate=dict(status='STOP',reason='runtime_not_proven',proof_status=None,plan_status=None,plan_sha256=None,plan_objects=0),result_durable=True))
        return r
    def test_receipt_rejects_false_no_permission_change(self):
        r=self.repaired_receipt();g.validate_receipt(r,0)
        r['status']='STOP_NO_PERMISSION_CHANGE'
        r['operation']['status']='PARTIAL_OR_UNKNOWN_NO_RETRY'
        with self.assertRaises(Exception):g.validate_receipt(r,3)
    def test_parent_after_must_retain_exact_witness_identity(self):
        import copy
        r=self.repaired_receipt();g.validate_receipt(r,0)
        for field in ('device','inode','mtime_ns'):
            bad=copy.deepcopy(r);bad['operation']['parent_after'][field]=1
            with self.subTest(field=field),self.assertRaises(Exception):g.validate_receipt(bad,0)
if __name__=='__main__':unittest.main()
