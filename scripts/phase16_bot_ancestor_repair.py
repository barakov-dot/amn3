"""One separately authorized parent DAC change. No CLI, app, DB or services.

Inject a frozen secure reader and journal. Exact live witness is external input;
this module is never an authorization source. Partial effects cannot be replayed.
"""
import json
import stat

PARENT='/opt/amn2-spain/bot-candidates'
STAGE=PARENT+'/phase16-bot-runtime40-20260929-6e68235-001'
OP='phase16-ancestor-traverse-20261003-001'
KNOWN=('phase16-bot-candidate-20260921-6e68235-001','phase16-bot-runtime40-20260924-6e68235-001','phase16-bot-runtime40-20260929-6e68235-001')
FIELDS={'mode':'st_mode','uid':'st_uid','gid':'st_gid','device':'st_dev','inode':'st_ino','mtime_ns':'st_mtime_ns','ctime_ns':'st_ctime_ns'}

class RepairError(ValueError):pass

def require(value,reason):
    if not value:raise RepairError(reason)

def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()

def exclusive_group(passwd,groups):
    try:
        users=[r.split(':') for r in passwd.decode('utf-8').splitlines() if r]
        rows=[r.split(':') for r in groups.decode('utf-8').splitlines() if r]
        require(all(len(r)==7 for r in users) and all(len(r)==4 for r in rows),'group_exclusive')
        require([r[0] for r in users if int(r[3])==61212]==['amn2-spain'],'group_exclusive')
        own=[r for r in rows if int(r[2])==61212]
        require(len(own)==1 and own[0][0]=='amn2-spain' and set(own[0][3].split(','))<={'','amn2-spain'},'group_exclusive')
        return True
    except RepairError:raise
    except Exception:raise RepairError('group_exclusive') from None

def row(meta):
    return {key:stat.S_IMODE(meta.st_mode) if key=='mode' else getattr(meta,field) for key,field in FIELDS.items()}

def matches(meta,expected):return row(meta)=={key:expected[key] for key in FIELDS}

def parent_session(reader_class,fingerprint):
    class ParentSession(reader_class):
        def __init__(self,witness,*,syscalls):
            super().__init__(PARENT,syscalls=syscalls);self.witness=witness;self.siblings={};self.parent_index=3;self.after=None
        def check_chain(self):
            super().check_chain()
            require(all(not self.os.listxattr(fd) for fd,*_ in self.chain),'parent_acl')
        def preflight(self):
            require(len(self.chain)==4,'parent_chain')
            paths=('/', '/opt', '/opt/amn2-spain',PARENT)
            for path,entry in zip(paths,self.chain):
                fd=entry[0];meta=self.os.fstat(fd)
                require(stat.S_ISDIR(meta.st_mode) and matches(meta,self.witness['ancestors'][path]),'parent_preimage')
                require(not self.os.listxattr(fd),'parent_acl')
            parent=self.os.fstat(self.root_fd)
            require(parent.st_uid==parent.st_gid==0 and stat.S_IMODE(parent.st_mode)==0o700,'parent_private')
            names=self.os.listdir(self.root_fd)
            require(len(names)<=16 and len(names)==len(set(names)) and set(names)<=set(KNOWN) and STAGE.rsplit('/',1)[1] in names,'sibling_inventory')
            for name in sorted(names):
                fd=self.directory(name,self.root_fd);meta=self.os.fstat(fd)
                require(stat.S_ISDIR(meta.st_mode) and meta.st_uid==meta.st_gid==0 and stat.S_IMODE(meta.st_mode)==0o700 and not self.os.listxattr(fd),'sibling_private')
                if PARENT+'/'+name==STAGE:require(matches(meta,self.witness['stage_root']),'stage_preimage')
                self.siblings[name]=fingerprint(meta)
            self.check_before()
        def _siblings(self):
            require(set(self.os.listdir(self.root_fd))==set(self.siblings),'sibling_inventory')
            self.check_chain()
        def check_before(self):
            self._siblings()
            require(matches(self.os.fstat(self.root_fd),self.witness['ancestors'][PARENT]),'parent_preimage')
        def _change(self,kind):
            self._siblings()
            before=self.os.fstat(self.root_fd)
            if kind=='group':
                require(before.st_uid==before.st_gid==0 and stat.S_IMODE(before.st_mode)==0o700,'parent_preimage')
                self.os.fchown(self.root_fd,-1,61212);mode=0o700
            else:
                require(before.st_uid==0 and before.st_gid==61212 and stat.S_IMODE(before.st_mode)==0o700,'parent_transition')
                self.os.fchmod(self.root_fd,0o710);mode=0o710
            after=self.os.fstat(self.root_fd)
            require(all(getattr(before,k)==getattr(after,k) for k in ('st_dev','st_ino','st_uid','st_nlink','st_size','st_mtime_ns')) and stat.S_ISDIR(after.st_mode) and stat.S_IMODE(after.st_mode)==mode and after.st_gid==61212 and not self.os.listxattr(self.root_fd),'parent_transition')
            fd,parent,name,_=self.chain[self.parent_index]
            require(fingerprint(after)==fingerprint(self.os.stat(name,dir_fd=parent,follow_symlinks=False)),'parent_named')
            self.chain[self.parent_index]=(fd,parent,name,after)  # only our fixed FD change; no other rebase
            self._siblings()
        def change_group(self):self._change('group')
        def change_mode(self):self._change('mode')
        def check_after(self):
            self._siblings();meta=self.os.fstat(self.root_fd)
            require(meta.st_uid==0 and meta.st_gid==61212 and stat.S_IMODE(meta.st_mode)==0o710,'parent_transition')
            self.after=row(meta);return self.after
    return ParentSession

def apply(session,journal,guard,followup,binding):
    result=dict(status='STOP_NO_PERMISSION_CHANGE',reason='precondition',permission_attempted=False,completed_syscalls=0,parent_verified=False,parent_after=None,candidate=None,result_durable=False)
    result_started=False
    def record(kind,value):journal.create('stage-access.'+OP+'.'+kind+'.json',encoded(value))
    try:
        session.check_before()
        record('claim',dict(binding=binding,operation=OP,replay_allowed=False))
        record('plan',dict(binding=binding,parent=PARENT,before=session.witness['ancestors'][PARENT],desired=dict(uid=0,gid=61212,mode=0o710),siblings={n:list(v) for n,v in session.siblings.items()}))
        record('intent',dict(binding=binding,syscalls=['fchown(parent_fd,-1,61212)','fchmod(parent_fd,0710)'],automatic_rollback=False))
        guard();session.check_before()
        result['permission_attempted']=True
        session.change_group();result['completed_syscalls']=1
        session.change_mode();result['completed_syscalls']=2
        session.os.fsync(session.root_fd)
        result['parent_after']=session.check_after();result['parent_verified']=True
        result['candidate']=followup()
        guard();session.check_after()
        result.update(status='PARENT_REPAIRED_CANDIDATE_CHECKED',reason='bounded_parent_change_candidate_readonly')
        result_started=True;record('result',{**result,'result_durable':True});result['result_durable']=True
    except BaseException as error:
        result['status']='PARTIAL_OR_UNKNOWN_NO_RETRY' if result['permission_attempted'] else 'STOP_NO_PERMISSION_CHANGE'
        result['reason']='deadline' if isinstance(error,KeyboardInterrupt) else (error.args[0] if isinstance(error,RepairError) else 'operation_unverified')
        if not result_started and not isinstance(error,KeyboardInterrupt):
            try:record('result',{**result,'result_durable':True});result['result_durable']=True
            except BaseException:pass
    return result
