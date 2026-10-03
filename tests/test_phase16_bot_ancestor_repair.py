"""Portable Unix metadata/FD model; never applies host permissions or SSH."""
import copy
import importlib
import json
import stat
from types import SimpleNamespace
import unittest
from scripts.vps.phase16_bot_retained_stage_remote import SecureReader, fingerprint

try: m=importlib.import_module('scripts.phase16_bot_ancestor_repair')
except ModuleNotFoundError: m=None

class FS:
    O_RDONLY=0;O_DIRECTORY=1;O_NOFOLLOW=2;O_CLOEXEC=4
    def __init__(self, witness):
        self.nodes={};self.handles={};self.counter=0;self.actions=[];self.fail=None;self.hook=None
        for path,row in witness['ancestors'].items():self.add(path,row)
        self.add(m.STAGE,witness['stage_root'])
    def add(self,path,row):
        self.nodes[path]=SimpleNamespace(st_mode=stat.S_IFDIR|row['mode'],st_uid=row['uid'],st_gid=row['gid'],st_dev=row['device'],st_ino=row['inode'],st_mtime_ns=row['mtime_ns'],st_ctime_ns=row['ctime_ns'],st_nlink=2,st_size=4096,attrs=())
    def name(self,name,dir_fd):return name if dir_fd is None else self.handles[dir_fd].rstrip('/')+'/'+name
    def open(self,name,flags,*,dir_fd=None):
        assert flags & self.O_NOFOLLOW and flags & self.O_CLOEXEC
        path=self.name(name,dir_fd);node=self.nodes[path]
        if not stat.S_ISDIR(node.st_mode):raise OSError('nofollow')
        self.counter+=1;self.handles[self.counter]=path;return self.counter
    def close(self,fd):del self.handles[fd]
    def stat(self,name,*,dir_fd=None,follow_symlinks=False):return copy.copy(self.nodes[self.name(name,dir_fd)])
    def fstat(self,fd):return copy.copy(self.nodes[self.handles[fd]])
    def listxattr(self,fd):return self.nodes[self.handles[fd]].attrs
    def listdir(self,fd):
        parent=self.handles[fd].rstrip('/')+'/'
        return [p[len(parent):] for p in self.nodes if p.startswith(parent) and '/' not in p[len(parent):] and p!=parent]
    def fchown(self,fd,uid,gid):
        self.actions.append(('chown',self.handles[fd],uid,gid))
        if self.fail=='chown':raise OSError('secret exception')
        node=self.nodes[self.handles[fd]];node.st_gid=gid;node.st_ctime_ns+=1
        if self.hook:self.hook()
    def fchmod(self,fd,mode):
        self.actions.append(('chmod',self.handles[fd],mode))
        if self.fail=='chmod':raise OSError('secret exception')
        node=self.nodes[self.handles[fd]];node.st_mode=stat.S_IFDIR|mode;node.st_ctime_ns+=1
    def fsync(self,fd):pass

class Journal:
    def __init__(self,fs,fail=None):self.fs=fs;self.names=[];self.fail=fail
    def create(self,name,raw):
        self.fs.actions.append(('journal',name));self.names.append(name)
        if self.fail and name.endswith('.'+self.fail+'.json'):raise OSError('secret log')
        json.loads(raw)

class RepairTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(m,'new repair module absent')
        from scripts import phase16_bot_ancestor_readback as ancestor
        self.witness=json.loads((ancestor.ROOT/'research/amn2/phase16-bot-ancestor-readback-execution-001-2026-10-03.json').read_bytes())['local_result']['receipt']['snapshot']
        self.fs=FS(self.witness);self.addCleanup(lambda:self.assertEqual(self.fs.handles,{}))
    def session(self):return m.parent_session(SecureReader,fingerprint)(self.witness,syscalls=self.fs)
    def run_repair(self,fs=None,journal=None,guard=lambda:None,followup=lambda:{'status':'PASS'}):
        s=self.session().__enter__()
        try:
            s.preflight()
            return m.apply(s,journal or Journal(self.fs),guard,followup,{'approval':'bound'})
        finally:s.close()
    def test_only_parent_two_syscalls_after_durable_intent(self):
        result=self.run_repair()
        self.assertEqual(result['status'],'PARENT_REPAIRED_CANDIDATE_CHECKED')
        events=self.fs.actions
        self.assertEqual([e for e in events if e[0] in ('chown','chmod')],[('chown',m.PARENT,-1,61212),('chmod',m.PARENT,0o710)])
        self.assertLess(next(i for i,e in enumerate(events) if e[0]=='journal' and '.intent.' in e[1]),next(i for i,e in enumerate(events) if e[0]=='chown'))
        self.assertEqual(self.fs.nodes[m.STAGE].st_mode&0o777,0o700)
    def test_before_witness_drift_fails_before_audit_or_mutation(self):
        for field in ('st_ino','st_gid','st_mtime_ns','st_ctime_ns'):
            with self.subTest(field=field):
                node=self.fs.nodes[m.PARENT];old=getattr(node,field);setattr(node,field,old+1)
                try:
                    with self.assertRaises(Exception):self.run_repair()
                finally:setattr(node,field,old)
        self.assertEqual(self.fs.actions,[])
    def test_unknown_sibling_and_nonprivate_sibling_rejected(self):
        row=self.witness['stage_root'];self.fs.add(m.PARENT+'/unknown-sensitive-name',row)
        with self.assertRaises(Exception):self.run_repair()
        del self.fs.nodes[m.PARENT+'/unknown-sensitive-name']
        self.fs.nodes[m.STAGE].st_mode=stat.S_IFDIR|0o750
        with self.assertRaises(Exception):self.run_repair()
        self.assertEqual(self.fs.actions,[])
    def test_symlink_acl_owner_failure(self):
        for field,value in (('st_mode',stat.S_IFLNK|0o700),('st_uid',61212),('attrs',('acl-secret',))):
            node=self.fs.nodes[m.STAGE];old=getattr(node,field);setattr(node,field,value)
            try:
                with self.assertRaises(Exception):self.run_repair()
            finally:setattr(node,field,old)
        self.assertEqual(self.fs.actions,[])
    def test_sibling_added_between_intent_and_chown_rejected(self):
        def guard():self.fs.add(m.PARENT+'/unexpected',self.witness['stage_root'])
        result=self.run_repair(guard=guard)
        self.assertEqual(result['status'],'STOP_NO_PERMISSION_CHANGE')
        self.assertFalse(result['permission_attempted'])
    def test_chown_failure_is_partial_even_zero_completed(self):
        self.fs.fail='chown';r=self.run_repair()
        self.assertEqual(r['status'],'PARTIAL_OR_UNKNOWN_NO_RETRY');self.assertTrue(r['permission_attempted']);self.assertEqual(r['completed_syscalls'],0)
        self.assertNotIn('secret',json.dumps(r))
    def test_chmod_failure_preserves_partial_and_no_retry(self):
        self.fs.fail='chmod';r=self.run_repair()
        self.assertEqual(r['completed_syscalls'],1);self.assertEqual(r['status'],'PARTIAL_OR_UNKNOWN_NO_RETRY')
        self.assertEqual(self.fs.nodes[m.PARENT].st_gid,61212);self.assertEqual(self.fs.nodes[m.PARENT].st_mode&0o777,0o700)
    def test_other_ancestor_drift_after_chown_not_rebased(self):
        self.fs.hook=lambda:setattr(self.fs.nodes['/opt'],'st_ctime_ns',0)
        r=self.run_repair();self.assertEqual(r['status'],'PARTIAL_OR_UNKNOWN_NO_RETRY')
        self.assertFalse(any(e[0]=='chmod' for e in self.fs.actions))
    def test_journal_intent_failure_never_grants_permission(self):
        r=self.run_repair(journal=Journal(self.fs,'intent'))
        self.assertEqual(r['status'],'STOP_NO_PERMISSION_CHANGE');self.assertFalse(r['permission_attempted'])
        self.assertFalse(any(e[0]=='chown' for e in self.fs.actions))
    def test_candidate_stop_keeps_parent_success_separate(self):
        r=self.run_repair(followup=lambda:{'status':'STOP','reason':'runtime_not_proven'})
        self.assertEqual(r['status'],'PARENT_REPAIRED_CANDIDATE_CHECKED');self.assertTrue(r['parent_verified']);self.assertEqual(r['candidate']['status'],'STOP')
    def test_deadline_during_followup_keeps_partial_unknown(self):
        def stop():raise KeyboardInterrupt('deadline')
        r=self.run_repair(followup=stop)
        self.assertEqual(r['status'],'PARTIAL_OR_UNKNOWN_NO_RETRY');self.assertTrue(r['parent_verified']);self.assertEqual(r['reason'],'deadline')
    def test_result_journal_failure_not_reported_success(self):
        r=self.run_repair(journal=Journal(self.fs,'result'));self.assertEqual(r['status'],'PARTIAL_OR_UNKNOWN_NO_RETRY')
        self.assertFalse(r['result_durable']);self.assertTrue(r['parent_verified'])
    def test_group_must_exclude_other_local_accounts(self):
        passwd=b'root:x:0:0::/:/bin/sh\namn2-spain:x:61212:61212::/:/bin/sh\n'
        group=b'root:x:0:\namn2-spain:x:61212:\n'
        self.assertTrue(m.exclusive_group(passwd,group))
        for p,g in ((passwd+b'other:x:1000:61212::/:/bin/sh\n',group),(passwd,group.replace(b'61212:',b'61212:other'))):
            with self.assertRaises(Exception):m.exclusive_group(p,g)
if __name__=='__main__':unittest.main()
