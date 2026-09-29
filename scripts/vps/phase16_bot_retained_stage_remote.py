"""Stage runtime40 from hash-bound retained payload. No bulk upload or activation.

Only used files are read, through Linux no-follow descriptors. All bytes are
verified in memory before claiming a new directory. The old candidate, including
its test-venv, is never used as an interpreter or modified.
"""
from __future__ import annotations
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import signal
import stat
import sys
import time
from scripts.vps import phase16_bot_linux_gate_remote as legacy
from scripts.vps import phase16_bot_runtime40_stage_remote as stage

APPROVAL='PHASE16_BOT_RUNTIME40_RETAINED_STAGE_20260929_001'
ARTIFACT_ID='phase16-bot-runtime40-20260929-6e68235-001'
DESTINATION=Path('/opt/amn2-spain/bot-candidates')/ARTIFACT_ID
RETAINED=PurePosixPath('/opt/amn2-spain/bot-candidates')/legacy.ARTIFACT_ID/'payload'
MANIFEST_BYTES=74676
REMOTE_SECONDS=300
WORK_SECONDS=280
SCHEMA='phase16.bot-runtime40-retained-stage.v1'
SUCCESS=stage.SUCCESS
STEPS=stage.STEPS
LOCK=stage.LOCK
METADATA_CODE=stage.METADATA_CODE
validate_metadata=stage.validate_metadata
write_result=stage.write_result
REASONS=stage.REASONS|frozenset({'retained_io','retained_directory','retained_file',
    'retained_size','retained_hash','retained_changed','retained_inventory','unexpected_input'})


def reason(error):
    value=str(error) if isinstance(error,legacy.GateError) else None
    return value if value in REASONS else 'stage_exception'


def fingerprint(meta):
    return tuple(getattr(meta,name) for name in ('st_dev','st_ino','st_mode','st_uid','st_gid',
                 'st_nlink','st_size','st_mtime_ns','st_ctime_ns'))


class SecureReader:
    """Pin every ancestor from /, reject symlinks and writable/unowned paths.

    Descriptor-relative opens prevent path substitution from redirecting reads.
    Directory and file identity are checked again before releasing descriptors.
    Reading stops at the trusted size + 1; a FIFO cannot block open().
    """
    def __init__(self,root,*,syscalls=os):
        self.root=PurePosixPath(root);self.os=syscalls;self.root_fd=None;self.chain=[]
        legacy.require(self.root.is_absolute() and '..' not in self.root.parts,'archive_path')

    def directory(self,name,parent=None):
        api=self.os
        flags=api.O_RDONLY|api.O_DIRECTORY|api.O_NOFOLLOW|api.O_CLOEXEC
        fd=api.open(name,flags,**({} if parent is None else {'dir_fd':parent}))
        try:
            meta=api.fstat(fd)
            legacy.require(stat.S_ISDIR(meta.st_mode) and meta.st_uid==0 and not meta.st_mode&0o022,
                           'retained_directory')
            self.chain.append((fd,parent,name,meta))
            return fd
        except BaseException:
            api.close(fd);raise

    def __enter__(self):
        try:
            self.root_fd=self.directory('/')
            for part in self.root.parts[1:]:self.root_fd=self.directory(part,self.root_fd)
            return self
        except BaseException:
            self.close();raise

    def check_chain(self):
        for fd,parent,name,before in self.chain:
            after=self.os.fstat(fd)
            named=self.os.stat(name,follow_symlinks=False,**({} if parent is None else {'dir_fd':parent}))
            legacy.require(fingerprint(before)==fingerprint(after)==fingerprint(named),'retained_changed')

    def close(self):
        for fd,*_ in reversed(self.chain):self.os.close(fd)
        self.chain=[];self.root_fd=None

    def __exit__(self,kind,error,tb):
        try:
            if kind is None:self.check_chain()
        finally:self.close()

    def read(self,name,size):
        legacy.safe_name(name)
        legacy.require(type(size) is int and 0<=size<=legacy.MAX_UNPACKED,'retained_size')
        api=self.os;parent=self.root_fd;checkpoint=len(self.chain);fd=None
        try:
            for part in name.split('/')[:-1]:parent=self.directory(part,parent)
            leaf=name.split('/')[-1]
            fd=api.open(leaf,api.O_RDONLY|api.O_NOFOLLOW|api.O_CLOEXEC|api.O_NONBLOCK,dir_fd=parent)
            before=api.fstat(fd)
            legacy.require(stat.S_ISREG(before.st_mode) and before.st_uid==0 and
                           before.st_nlink==1 and not before.st_mode&0o022,'retained_file')
            legacy.require(before.st_size==size,'retained_size')
            data=bytearray()
            while len(data)<=size:
                chunk=api.read(fd,min(1024*1024,size+1-len(data)))
                if not chunk:break
                data.extend(chunk)
            legacy.require(len(data)==size,'retained_size')
            after=api.fstat(fd);named=api.stat(leaf,dir_fd=parent,follow_symlinks=False)
            legacy.require(fingerprint(before)==fingerprint(after)==fingerprint(named),'retained_changed')
            self.check_chain()
            return bytes(data)
        finally:
            if fd is not None:api.close(fd)
            for extra,*_ in reversed(self.chain[checkpoint:]):api.close(extra)
            del self.chain[checkpoint:]


def validate_retained(read):
    raw=read('manifest.json',MANIFEST_BYTES)
    legacy.require(len(raw)==MANIFEST_BYTES and legacy.sha(raw)==legacy.MANIFEST_SHA,'manifest_binding')
    manifest=json.loads(raw)
    legacy.require(manifest['source_commit']==legacy.SOURCE_SHA and
                   manifest['artifact_id']==legacy.ARTIFACT_ID,'source_binding')
    wheels=manifest['wheels']
    runtime=[w for w in wheels if w['scope']=='runtime']
    locks=[item for item in manifest['auxiliary'] if item['file']==LOCK]
    legacy.require(len(runtime)==40 and len(wheels)==48 and len(locks)==1,'retained_inventory')
    items=[manifest['source'],locks[0],*runtime]
    payload={};total=0
    for item in items:
        name=legacy.safe_name(item['file'])
        legacy.require(name!='manifest.json' and name not in payload,'retained_inventory')
        size=item['size'];legacy.require(type(size) is int and 0<=size<=legacy.MAX_UNPACKED,'retained_size')
        total+=size;legacy.require(total<=legacy.MAX_UNPACKED,'retained_size')
        body=read(name,size)
        legacy.require(len(body)==size and legacy.sha(body)==item['sha256'],'retained_hash')
        payload[name]=body
    selected,source,expected=stage.select_runtime(payload,manifest)
    entries=manifest['source']['entries'];index={e['path']:e for e in entries}
    legacy.require(len(entries)==len(index) and set(source)==set(index),'source_inventory')
    for name,body in source.items():
        legacy.require(len(body)==index[name]['size'] and legacy.sha(body)==index[name]['sha256'],'source_binding')
    return selected,source,expected


def read_retained():
    try:
        with SecureReader(RETAINED) as reader:return validate_retained(reader.read)
    except OSError:raise legacy.GateError('retained_io') from None


def precheck():
    legacy.require(sys.platform=='linux' and sys.version_info[:2]==(3,12),'platform_python')
    legacy.require(platform.machine()=='x86_64' and platform.libc_ver()==('glibc','2.39'),'platform_abi')
    legacy.require(os.geteuid()==0,'root_required')
    for parent in (Path('/opt'),Path('/opt/amn2-spain'),DESTINATION.parent):
        metadata=parent.lstat()
        legacy.require(stat.S_ISDIR(metadata.st_mode) and metadata.st_uid==0 and
                       not metadata.st_mode & 0o022,'unsafe_parent')
    legacy.require(not DESTINATION.exists() and not DESTINATION.is_symlink(),'destination_exists')
    legacy.require(shutil.disk_usage(DESTINATION.parent).free>=512*1024*1024,'disk_space')
    legacy.require(Path('/usr/bin/unshare').is_file(),'network_namespace_unavailable')


def base_result():
    return dict(schema=SCHEMA,artifact_id=ARTIFACT_ID,approval=APPROVAL,
                bundle_sha256=legacy.BUNDLE_SHA,source_commit=legacy.SOURCE_SHA,
                destination=DESTINATION.as_posix(),status='STOP_BEFORE_STAGE_OR_UNKNOWN',
                service_actions=0,live_database_opened=False,telegram_polling=False,
                runtime_activation=False,old_runtime_modified=False,steps=[],
                retained_payload=RETAINED.as_posix(),retained_files_verified=0,
                retained_manifest_sha256=legacy.MANIFEST_SHA,retained_payload_modified=False)


def execute():
    started=time.monotonic();deadline=started+WORK_SECONDS
    precheck()
    selected,source,expected=read_retained()
    # Repeat claim check even when a test substitutes the platform precheck.
    legacy.require(not DESTINATION.exists() and not DESTINATION.is_symlink(),'destination_exists')
    rc,_=legacy.run_process(['/usr/bin/unshare','--net','/usr/bin/true'],cwd=str(DESTINATION.parent),
                            env=legacy.clean_environment(Path('/nonexistent')),timeout=5)
    legacy.require(rc==0,'network_namespace_unavailable')
    legacy.claim_directory(DESTINATION)
    result=base_result();result['status']='STOP_RETAINED_NO_RETRY'
    result['retained_files_verified']=43
    result['steps'].append({'step':'network_namespace','returncode':0})
    try:
        write_result(DESTINATION/'claim.json',dict(approval=APPROVAL,artifact_id=ARTIFACT_ID,
                                                 bundle_sha256=legacy.BUNDLE_SHA,attempts=1))
        legacy.write_tree(DESTINATION/'payload',selected)
        legacy.write_tree(DESTINATION/'source',source)
        scratch=DESTINATION/'scratch';scratch.mkdir(mode=0o700)
        env=legacy.clean_environment(scratch);venv=DESTINATION/'runtime-venv';python=venv/'bin/python'
        def run(label,args,seconds):
            remaining=deadline-time.monotonic();legacy.require(remaining>0,'wall_cap')
            rc,output=legacy.run_process(['/usr/bin/unshare','--net',*map(str,args)],cwd=str(scratch),env=env,
                                         timeout=min(seconds,remaining))
            result['steps'].append(dict(step=label,returncode=rc,output_bytes=len(output),output_sha256=legacy.sha(output)))
            legacy.require(rc==0,label+'_exit')
            return output
        run('venv',['/usr/bin/python3','-I','-B','-m','venv',venv],45)
        run('offline_install',[python,'-I','-B','-m','pip','--isolated','--disable-pip-version-check',
            '--no-cache-dir','install','--no-index','--no-deps','--require-hashes','--only-binary=:all:',
            '--find-links',DESTINATION/'payload/wheelhouse/runtime','-r',DESTINATION/'payload'/LOCK],120)
        run('pip_check',[python,'-I','-B','-m','pip','--isolated','check'],20)
        metadata=json.loads(run('metadata',[python,'-I','-S','-B','-c',METADATA_CODE,'--stage-metadata',
                                            venv,DESTINATION/'source'],20))
        result.update(validate_metadata(metadata,expected,DESTINATION))
        legacy.verify_tree(DESTINATION/'source',source)
        legacy.verify_tree(DESTINATION/'payload',selected)
        legacy.require(time.monotonic()<deadline,'wall_cap')
        result['steps'].append({'step':'source_readback','returncode':0})
        result['app_python_files']=126
        result['runtime_lock_sha256']=legacy.sha(selected[LOCK])
        result['status']=SUCCESS
    except BaseException as error:
        result['reason']=reason(error)
    finally:
        result['seconds']=round(time.monotonic()-started,3)
        try:write_result(DESTINATION/'result.json',result)
        except BaseException:
            result['status']='STOP_RETAINED_NO_RETRY';result['reason']='result_write_failed'
    return result


def main():
    def alarm(signum,frame):raise legacy.GateError('wall_cap')
    if sys.platform=='linux':signal.signal(signal.SIGALRM,alarm);signal.alarm(REMOTE_SECONDS)
    try:
        legacy.require(sys.argv[1:]==[APPROVAL],'approval_argument')
        legacy.require(sys.stdin.buffer.read(1)==b'','unexpected_input')
        result=execute()
    except BaseException as error:
        result=base_result();result['reason']=reason(error)
    finally:
        if sys.platform=='linux':signal.alarm(0)
    print(json.dumps(result),flush=True)
    return 0 if result['status']==SUCCESS else 3


if __name__=='__main__':raise SystemExit(main())
