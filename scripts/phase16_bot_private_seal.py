"""Separate two-file private DAC seal. No CLI, content writes, app, DB or services.

Callers supply exact approved witness, secure descriptors, durable journal and
continuity guard. Never replays consumed operations or applies an access plan.
"""
import copy
import json
import stat

OP='phase16-private-seal-20261004-001'
TARGETS=('claim.json','result.json')
NAMES=TARGETS+('payload','scratch')
STAGE_CHILDREN={'claim.json','result.json','payload','scratch','source','runtime-venv'}
ROOT_FIELDS=('mode','uid','gid','device','inode','mtime_ns','ctime_ns')

class SealError(ValueError):pass

def require(value,reason):
    if not value:raise SealError(reason)

def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()

def root_row(meta):
    return dict(mode=stat.S_IMODE(meta.st_mode),uid=meta.st_uid,gid=meta.st_gid,device=meta.st_dev,inode=meta.st_ino,mtime_ns=meta.st_mtime_ns,ctime_ns=meta.st_ctime_ns)

def object_row(meta):
    return dict(**root_row(meta),kind='directory' if stat.S_ISDIR(meta.st_mode) else 'file',size=meta.st_size,nlink=meta.st_nlink)

def session_class(reader_class,fingerprint):
    class SealSession(reader_class):
        def __init__(self,witness,ancestors,*,syscalls):
            self.filefds={};self.expected=copy.deepcopy(witness['objects']);self.witness=witness;self.expected_ancestors=ancestors
            super().__init__(syscalls=syscalls)
        def close(self):
            for name in list(self.filefds):self.os.close(self.filefds.pop(name))
            super().close()
        def check_all(self):
            values=self.ancestors()
            require(tuple(p for p,_,_ in values)==tuple(self.expected_ancestors),'seal_ancestors')
            for path,meta,attrs in values:
                require(not attrs and root_row(meta)=={k:self.expected_ancestors[path][k] for k in ROOT_FIELDS},'seal_ancestors')
            require(root_row(self.info('.'))==self.witness['stage_root'] and not self.acl_names('.'),'seal_stage')
            require(set(self.entries('.'))==STAGE_CHILDREN,'seal_inventory')
            for name in NAMES:
                meta=self.info(name);kind=stat.S_ISREG(meta.st_mode) if name in TARGETS else stat.S_ISDIR(meta.st_mode)
                require(kind and meta.st_uid==meta.st_gid==0 and not meta.st_mode&0o7022 and (name not in TARGETS or meta.st_nlink==1),'seal_metadata')
                require(not self.acl_names(name),'seal_acl')
                require(object_row(meta)=={k:self.expected[name][k] for k in object_row(meta)},'seal_preimage')
                if name in self.filefds:
                    fd=self.filefds[name];require(fingerprint(self.os.fstat(fd))==fingerprint(meta) and not self.os.listxattr(fd),'seal_fd')
            self.stable()
        def preflight(self):
            require(set(self.expected)==set(NAMES) and self.witness['blocked_objects']==list(TARGETS),'seal_scope')
            for name in NAMES:
                expected=self.expected[name];require(expected['acl_clear'] is True and expected['acl_count']==0 and expected['uid']==expected['gid']==0,'seal_scope')
                require(expected['mode']==(0o644 if name in TARGETS else 0o700),'seal_scope')
            self.check_all()
            for name in TARGETS:
                fd=self.os.open(name,self.os.O_RDONLY|self.os.O_NOFOLLOW|self.os.O_CLOEXEC|self.os.O_NONBLOCK,dir_fd=self.root_fd)
                self.filefds[name]=fd
            self.check_all()
        def seal(self,name):
            require(name in TARGETS and name in self.filefds and self.expected[name]['mode']==0o644,'seal_scope')
            self.check_all();fd=self.filefds[name];before=self.os.fstat(fd)
            self.os.fchmod(fd,0o600)
            after=self.os.fstat(fd);named=self.os.stat(name,dir_fd=self.root_fd,follow_symlinks=False)
            require(stat.S_ISREG(after.st_mode) and stat.S_IMODE(after.st_mode)==0o600 and not self.os.listxattr(fd) and fingerprint(after)==fingerprint(named),'seal_transition')
            require(all(getattr(before,k)==getattr(after,k) for k in ('st_dev','st_ino','st_uid','st_gid','st_nlink','st_size','st_mtime_ns')),'seal_transition')
            require(after.st_ctime_ns>=before.st_ctime_ns,'seal_transition')
            self.snapshots[name]=fingerprint(after)  # only this held-FD mode/ctime change
            self.expected[name]={**self.expected[name],**object_row(after),'private':True}
            self.check_all();self.os.fsync(fd);self.check_all()
        def verified(self):
            self.check_all();require(all(self.expected[n]['mode']==0o600 for n in TARGETS),'seal_transition')
            return {n:self.expected[n] for n in TARGETS}
    return SealSession

def apply(session,journal,guard,followup,binding):
    result=dict(status='STOP_NO_PERMISSION_CHANGE',reason='precondition',permission_attempted=False,completed_syscalls=0,files_verified=False,files_after=None,candidate=None,result_durable=False)
    result_started=False
    def record(kind,value):journal.create('stage-access.'+OP+'.'+kind+'.json',encoded(value))
    try:
        session.check_all()
        record('claim',dict(binding=binding,operation=OP,replay_allowed=False))
        record('plan',dict(binding=binding,files={n:session.expected[n] for n in TARGETS},desired_mode=0o600,parent_and_stage='UNCHANGED'))
        record('intent',dict(binding=binding,syscalls=['fchmod(claim_fd,0600)','fchmod(result_fd,0600)'],automatic_rollback=False))
        guard();session.check_all()
        for name in TARGETS:
            result['permission_attempted']=True;session.seal(name);result['completed_syscalls']+=1
        result['files_after']=session.verified();result['files_verified']=True
        result['candidate']=followup()
        guard();session.verified()
        result.update(status='PRIVATE_FILES_SEALED_CANDIDATE_CHECKED',reason='bounded_private_seal_candidate_readonly')
        result_started=True;record('result',{**result,'result_durable':True});result['result_durable']=True
    except BaseException as error:
        result['status']='PARTIAL_OR_UNKNOWN_NO_RETRY' if result['permission_attempted'] else 'STOP_NO_PERMISSION_CHANGE'
        result['reason']='deadline' if isinstance(error,KeyboardInterrupt) else (error.args[0] if isinstance(error,SealError) else 'operation_unverified')
        if not result_started and not isinstance(error,KeyboardInterrupt):
            try:record('result',{**result,'result_durable':True});result['result_durable']=True
            except BaseException:pass
    return result
