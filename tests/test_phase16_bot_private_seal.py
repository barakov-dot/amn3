"""Portable descriptor/DAC model: exact two JSON files, no real host mutation."""
import copy
import importlib
import json
from pathlib import Path
import stat
import unittest
from scripts import phase16_bot_stage_access as access
from scripts.vps.phase16_bot_stage_readback_remote import BoundTree
from tests.test_phase16_bot_ancestor_repair import FS,Journal
try:m=importlib.import_module('scripts.phase16_bot_private_seal')
except ModuleNotFoundError:m=None

class Reader(access.UnixStageReader):
    def __init__(self,*,syscalls):BoundTree.__init__(self,access.STAGE_ROOT,syscalls=syscalls)

class FileFS(FS):
    O_NONBLOCK=8
    def __init__(self,witness):
        parent=Path(__file__).resolve().parents[1]
        ancestors=json.loads((parent/'research/amn2/phase16-bot-ancestor-readback-execution-001-2026-10-03.json').read_bytes())['local_result']['receipt']['snapshot']['ancestors']
        ancestors['/opt/amn2-spain/bot-candidates']=witness['parent_after']
        super().__init__(dict(ancestors=ancestors,stage_root=witness['stage_root']))
        for name,row in witness['objects'].items():
            self.add(access.STAGE_ROOT+'/'+name,row);n=self.nodes[access.STAGE_ROOT+'/'+name];n.st_mode=(stat.S_IFREG if row['kind']=='file' else stat.S_IFDIR)|row['mode'];n.st_nlink=row['nlink'];n.st_size=row['size']
        for i,name in enumerate(('source','runtime-venv')):self.add(access.STAGE_ROOT+'/'+name,{**witness['stage_root'],'inode':900+i})
    def open(self,name,flags,*,dir_fd=None):
        assert flags&self.O_NOFOLLOW and flags&self.O_CLOEXEC
        path=self.name(name,dir_fd);node=self.nodes[path]
        if not (stat.S_ISDIR(node.st_mode) if flags&self.O_DIRECTORY else (stat.S_ISREG(node.st_mode) or stat.S_ISDIR(node.st_mode))):raise OSError('nofollow')
        self.counter+=1;self.handles[self.counter]=path;return self.counter
    def fchmod(self,fd,mode):
        self.actions.append(('chmod',self.handles[fd],mode));n=self.nodes[self.handles[fd]]
        if self.fail=='before_chmod':raise OSError('sensitive-exception')
        n.st_mode=stat.S_IFMT(n.st_mode)|mode;n.st_ctime_ns+=1
        if self.hook:self.hook()
        if self.fail=='after_chmod':raise OSError('sensitive-exception')
    def fsync(self,fd):
        if self.fail=='fsync':raise OSError('sensitive-exception')

class SealTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(m,'separate seal core absent')
        root=Path(__file__).resolve().parents[1]
        self.w=json.loads((root/'research/amn2/phase16-bot-private-boundary-readback-execution-001-2026-10-04.json').read_bytes())['local_result']['receipt']['snapshot']
        self.ancestors=json.loads((root/'research/amn2/phase16-bot-ancestor-readback-execution-001-2026-10-03.json').read_bytes())['local_result']['receipt']['snapshot']['ancestors'];self.ancestors['/opt/amn2-spain/bot-candidates']=self.w['parent_after'];self.fs=FileFS(self.w);self.addCleanup(lambda:self.assertEqual(self.fs.handles,{}))
    def session(self):return m.session_class(Reader,access.fingerprint)(self.w,self.ancestors,syscalls=self.fs)
    def run_seal(self,guard=lambda:None,followup=lambda:dict(status='PASS'),journal=None):
        with self.session() as s:s.preflight();return m.apply(s,journal or Journal(self.fs),guard,followup,dict(approval='bound'))
    def test_only_two_file_chmod_after_durable_intent(self):
        r=self.run_seal();self.assertEqual(r['status'],'PRIVATE_FILES_SEALED_CANDIDATE_CHECKED');self.assertTrue(r['files_verified']);self.assertTrue(r['result_durable']);self.assertEqual(r['completed_syscalls'],2)
        changes=[e for e in self.fs.actions if e[0] in ('chmod','chown')];self.assertEqual(changes,[('chmod',access.STAGE_ROOT+'/claim.json',0o600),('chmod',access.STAGE_ROOT+'/result.json',0o600)])
        intent=next(i for i,e in enumerate(self.fs.actions) if e[0]=='journal' and '.intent.' in e[1]);first=next(i for i,e in enumerate(self.fs.actions) if e[0]=='chmod');self.assertLess(intent,first)
        for path in (access.STAGE_ROOT,access.STAGE_ROOT+'/payload',access.STAGE_ROOT+'/scratch'):self.assertEqual(self.fs.nodes[path].st_mode&0o777,0o700)
        self.assertEqual(self.fs.nodes['/opt/amn2-spain/bot-candidates'].st_mode&0o777,0o710)
    def test_exact_file_preimage_drift_fails_before_audit(self):
        for field in ('st_ino','st_gid','st_size','st_mtime_ns','st_ctime_ns','st_nlink'):
            n=self.fs.nodes[access.STAGE_ROOT+'/claim.json'];before=getattr(n,field);setattr(n,field,before+1)
            try:
                with self.assertRaises(Exception):self.run_seal()
            finally:setattr(n,field,before)
        self.assertEqual(self.fs.actions,[])
    def test_acl_link_wrong_mode_or_root_owner_closed(self):
        for field,value in (('st_mode',stat.S_IFLNK|0o644),('st_mode',stat.S_IFREG|0o600),('st_uid',61212),('attrs',('sensitive-xattr',))):
            n=self.fs.nodes[access.STAGE_ROOT+'/claim.json'];before=getattr(n,field);setattr(n,field,value)
            try:
                with self.assertRaises(Exception):self.run_seal()
            finally:setattr(n,field,before)
        self.assertEqual(self.fs.actions,[])
    def test_parent_stage_and_private_directory_drift_closed(self):
        for path in ('/opt',access.STAGE_ROOT,access.STAGE_ROOT+'/payload',access.STAGE_ROOT+'/scratch'):
            n=self.fs.nodes[path];before=n.st_ctime_ns;n.st_ctime_ns+=1
            try:
                with self.assertRaises(Exception):self.run_seal()
            finally:n.st_ctime_ns=before
        self.assertEqual(self.fs.actions,[])
    def test_guard_drift_after_intent_never_attempts_permission(self):
        def guard():self.fs.nodes[access.STAGE_ROOT+'/result.json'].st_ctime_ns+=1
        r=self.run_seal(guard=guard);self.assertEqual(r['status'],'STOP_NO_PERMISSION_CHANGE');self.assertFalse(r['permission_attempted']);self.assertFalse(any(e[0]=='chmod' for e in self.fs.actions))
    def test_before_and_after_syscall_failure_are_partial_even_count0(self):
        for fail in ('before_chmod','after_chmod','fsync'):
            self.fs=FileFS(self.w);self.fs.fail=fail;r=self.run_seal();self.assertEqual(r['status'],'PARTIAL_OR_UNKNOWN_NO_RETRY');self.assertTrue(r['permission_attempted']);self.assertEqual(r['completed_syscalls'],0);self.assertNotIn('sensitive-exception',json.dumps(r))
    def test_collateral_change_after_first_syscall_is_not_rebased(self):
        self.fs.hook=lambda:setattr(self.fs.nodes[access.STAGE_ROOT+'/payload'],'st_ctime_ns',0)
        r=self.run_seal();self.assertEqual(r['status'],'PARTIAL_OR_UNKNOWN_NO_RETRY');self.assertEqual(len([e for e in self.fs.actions if e[0]=='chmod']),1)
    def test_ctime_regression_after_chmod_is_partial_no_followup(self):
        self.fs.hook=lambda:setattr(self.fs.nodes[access.STAGE_ROOT+'/claim.json'],'st_ctime_ns',0)
        r=self.run_seal(followup=lambda:self.fail('unverified followup'))
        self.assertEqual(r['status'],'PARTIAL_OR_UNKNOWN_NO_RETRY');self.assertEqual(r['reason'],'seal_transition');self.assertEqual(r['completed_syscalls'],0);self.assertFalse(r['files_verified']);self.assertTrue(r['permission_attempted'])
    def test_intent_failure_cannot_change_files(self):
        r=self.run_seal(journal=Journal(self.fs,'intent'));self.assertEqual(r['status'],'STOP_NO_PERMISSION_CHANGE');self.assertFalse(r['permission_attempted'])
    def test_candidate_stop_is_distinct_from_verified_two_file_seal(self):
        r=self.run_seal(followup=lambda:dict(status='STOP',reason='candidate_collection_failed'));self.assertEqual(r['status'],'PRIVATE_FILES_SEALED_CANDIDATE_CHECKED');self.assertEqual(r['candidate']['status'],'STOP');self.assertTrue(r['files_verified'])
    def test_deadline_during_followup_retains_partial_no_replay(self):
        def deadline():raise KeyboardInterrupt('deadline')
        r=self.run_seal(followup=deadline);self.assertEqual(r['status'],'PARTIAL_OR_UNKNOWN_NO_RETRY');self.assertTrue(r['files_verified']);self.assertEqual(r['reason'],'deadline')
    def test_result_journal_failure_not_success(self):
        r=self.run_seal(journal=Journal(self.fs,'result'));self.assertEqual(r['status'],'PARTIAL_OR_UNKNOWN_NO_RETRY');self.assertFalse(r['result_durable']);self.assertTrue(r['files_verified'])
if __name__=='__main__':unittest.main()
