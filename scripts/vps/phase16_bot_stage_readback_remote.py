"""Read only the fixed retained-stage directory. No subprocess or application import."""
from __future__ import annotations
from contextlib import contextmanager
from email.parser import BytesParser
from pathlib import PurePosixPath
import json
import os
import re
import signal
import stat
import sys
from scripts.vps.phase16_bot_retained_stage_remote import SecureReader, fingerprint, legacy
from scripts import phase16_bot_retained_stage_gate as staged

APPROVAL='PHASE16_BOT_RUNTIME40_STAGE_READBACK_20260929_001'
SCHEMA='phase16.stage-readback.v1'
DESTINATION=PurePosixPath('/opt/amn2-spain/bot-candidates/phase16-bot-runtime40-20260929-6e68235-001')
ARTIFACT_ID=DESTINATION.name
STAGE_APPROVAL='PHASE16_BOT_RUNTIME40_RETAINED_STAGE_20260929_001'
BUNDLE_SHA='e19abc5c132acae035503267d41d38fdd1e272951b2ebfd0f2a73e2f7c660cb7'
REMOTE_SECONDS=45
INVENTORY=None  # Rendered from the externally bound local inventory, never from VPS.
INCOMPLETE_REASONS=frozenset({'content_inventory','content_hash','saved_claim','saved_receipt',
    'saved_stage_incomplete','metadata_shape','metadata_binding','metadata_extra','metadata_duplicate',
    'venv_config','interpreter_link','pth_present','retained_size','missing_file'})
REASONS=INCOMPLETE_REASONS|frozenset({'unsafe_path','read_error','changed_during_read','readback_error',
    'platform_python','root_required','wall_cap','approval_argument'})


class BoundTree(SecureReader):
    """Add bounded listings and final identity checks to the frozen secure reader."""
    def __init__(self,root,*,syscalls=os):
        super().__init__(root,syscalls=syscalls);self.snapshots={}

    @contextmanager
    def directory_fd(self,name):
        legacy.safe_name(name);legacy.require(len(name.split('/'))<=32,'unsafe_path')
        checkpoint=len(self.chain);fd=self.root_fd
        try:
            for part in name.split('/'):fd=self.directory(part,fd)
            yield fd
            self.check_chain()
        finally:
            for extra,*_ in reversed(self.chain[checkpoint:]):self.os.close(extra)
            del self.chain[checkpoint:]

    @contextmanager
    def parent_fd(self,name):
        legacy.safe_name(name)
        parts=name.split('/')
        if len(parts)==1:yield self.root_fd,parts[0]
        else:
            with self.directory_fd('/'.join(parts[:-1])) as fd:yield fd,parts[-1]

    def info(self,name):
        with self.parent_fd(name) as (fd,leaf):
            value=self.os.stat(leaf,dir_fd=fd,follow_symlinks=False)
            previous=self.snapshots.setdefault(name,fingerprint(value))
            legacy.require(previous==fingerprint(value),'changed_during_read')
            return value

    def read_file(self,name,maximum,expected_size=None):
        meta=self.info(name)
        legacy.require(0<=meta.st_size<=maximum and (expected_size is None or meta.st_size==expected_size),'retained_size')
        return self.read(name,meta.st_size)

    def entries(self,name):
        self.info(name)
        with self.directory_fd(name) as fd:values=self.os.listdir(fd)
        legacy.require(len(values)<=512 and len(values)==len(set(values)),'content_inventory')
        for value in values:legacy.safe_name(value);legacy.require('/' not in value,'unsafe_path')
        return sorted(values)

    def file_set(self,prefix):
        found=set();nodes=0
        def visit(name):
            nonlocal nodes
            nodes+=1;legacy.require(nodes<=800,'content_inventory')
            meta=self.info(name)
            legacy.require(meta.st_uid==0 and not meta.st_mode&0o022,'unsafe_path')
            if stat.S_ISDIR(meta.st_mode):
                for child in self.entries(name):visit(name+'/'+child)
            else:
                legacy.require(stat.S_ISREG(meta.st_mode) and meta.st_nlink==1,'unsafe_path')
                found.add(name)
        visit(prefix);return found

    def metadata_files(self):
        site='runtime-venv/lib/python3.12/site-packages';result={}
        for name in self.entries(site):
            lower=name.lower()
            legacy.require(not lower.endswith('.pth') and lower not in ('sitecustomize.py','sitecustomize.pyc',
                'usercustomize.py','usercustomize.pyc','sitecustomize','usercustomize'),'pth_present')
            legacy.require(not lower.endswith('.egg-info'),'metadata_extra')
            if lower.endswith('.dist-info'):
                path=site+'/'+name+'/METADATA';result[path]=self.read_file(path,1024*1024)
                legacy.require(len(result)<=42,'metadata_extra')
        return result

    def interpreter_links(self):
        result={}
        for leaf in ('python','python3','python3.12'):
            name='runtime-venv/bin/'+leaf;before=self.info(name)
            legacy.require(stat.S_ISLNK(before.st_mode) and before.st_uid==0,'interpreter_link')
            with self.parent_fd(name) as (fd,base):value=self.os.readlink(base,dir_fd=fd)
            self.info(name);result[name]=value
        return result

    def stable(self):
        for name in list(self.snapshots):self.info(name)
        self.check_chain()


def strict_json(data):
    def pairs(items):
        result={}
        for key,value in items:
            legacy.require(key not in result,'saved_receipt');result[key]=value
        return result
    return json.loads(data,object_pairs_hook=pairs)


def validate_metadata(files,pins):
    installed={}
    for data in files.values():
        message=BytesParser().parsebytes(data,headersonly=True)
        legacy.require(len(message.get_all('Name',[]))==1 and len(message.get_all('Version',[]))==1,'metadata_shape')
        name,version=message['Name'],message['Version']
        legacy.require(re.fullmatch('[A-Za-z0-9_.-]{1,128}',name) and len(version)<=64,'metadata_shape')
        name=re.sub('[-_.]+','-',name).lower()
        legacy.require(name not in installed,'metadata_duplicate');installed[name]=version
    legacy.require(all(installed.get(n)==v for n,v in pins.items()),'metadata_binding')
    legacy.require(set(installed)-set(pins)<={'pip','setuptools'},'metadata_extra')
    return len(installed)-len(pins)


def validate_venv(config,links):
    settings={}
    for line in config.decode('utf-8').splitlines():
        if '=' in line:
            k,v=line.split('=',1);k=k.strip()
            legacy.require(k not in settings,'venv_config');settings[k]=v.strip()
    legacy.require(settings.get('include-system-site-packages')=='false','venv_config')
    prefix='runtime-venv/bin/'
    legacy.require(set(links)=={prefix+n for n in ('python','python3','python3.12')},'interpreter_link')
    for origin in links:
        seen=set();name=origin
        while name in links:
            legacy.require(name not in seen,'interpreter_link');seen.add(name);target=links[name]
            if target in ('/usr/bin/python3','/usr/bin/python3.12'):break
            legacy.require(target in ('python','python3','python3.12'),'interpreter_link');name=prefix+target
        else:raise legacy.GateError('interpreter_link')


def base_result():
    return dict(schema=SCHEMA,approval=APPROVAL,destination=DESTINATION.as_posix(),status='UNKNOWN',
        reason='readback_error',verified_files=0,runtime_pins=0,bootstrap_distributions=0,
        saved_receipt_sha256=None,writes=0,children=0,activation=False,database_opened=False)


def observe(inventory,*,reader_factory=BoundTree,emit=lambda event:None):
    result=base_result();directory_observed=False
    try:
        with reader_factory(DESTINATION.parent) as parent:
            try:meta=parent.info(DESTINATION.name)
            except FileNotFoundError:
                result.update(status='ABSENT',reason='directory_absent');return result
            legacy.require(stat.S_ISDIR(meta.st_mode) and meta.st_uid==0 and stat.S_IMODE(meta.st_mode)==0o700,'unsafe_path')
        directory_observed=True
        with reader_factory(DESTINATION) as tree:
            expected_claim=dict(approval=STAGE_APPROVAL,artifact_id=ARTIFACT_ID,bundle_sha256=BUNDLE_SHA,attempts=1)
            claim=strict_json(tree.read_file('claim.json',4096))
            legacy.require(json.dumps(claim,sort_keys=True)==json.dumps(expected_claim,sort_keys=True),'saved_claim')
            raw=tree.read_file('result.json',65536);saved=strict_json(raw)
            try:staged.validate_receipt(saved,0 if saved.get('status')==staged.remote.SUCCESS else 3)
            except Exception:raise legacy.GateError('saved_receipt') from None
            legacy.require(saved['status']==staged.remote.SUCCESS,'saved_stage_incomplete')
            result['saved_receipt_sha256']=legacy.sha(raw);emit({'event':'RECEIPT'})
            expected=inventory['files']
            actual=tree.file_set('source')|tree.file_set('payload')
            legacy.require(actual==set(expected),'content_inventory')
            for name,(size,digest) in sorted(expected.items()):
                body=tree.read_file(name,size,expected_size=size)
                legacy.require(legacy.sha(body)==digest,'content_hash');result['verified_files']+=1
            emit({'event':'CONTENT'})
            validate_venv(tree.read_file('runtime-venv/pyvenv.cfg',8192),tree.interpreter_links())
            bootstrap=validate_metadata(tree.metadata_files(),inventory['pins'])
            tree.stable();result.update(runtime_pins=len(inventory['pins']),bootstrap_distributions=bootstrap)
            emit({'event':'METADATA'})
        result.update(status='VERIFIED',reason='receipt_content_metadata_match')
    except FileNotFoundError:
        result.update(status='INCOMPLETE' if directory_observed else 'UNKNOWN',
                      reason='missing_file' if directory_observed else 'read_error')
    except legacy.GateError as error:
        code=str(error)
        if code in INCOMPLETE_REASONS:result.update(status='INCOMPLETE',reason=code)
        elif code in ('retained_changed','changed_during_read'):result['reason']='changed_during_read'
        elif code in ('retained_directory','retained_file','archive_path','unsafe_path'):result['reason']='unsafe_path'
        else:result['reason']=code if code in REASONS else 'readback_error'
    except (UnicodeError,ValueError,TypeError,KeyError):result.update(status='INCOMPLETE',reason='saved_receipt')
    except OSError:result['reason']='read_error'
    except Exception:result['reason']='readback_error'
    return result


def main():
    seq=0
    def emit(event):
        nonlocal seq
        print(json.dumps(dict(schema=SCHEMA,approval=APPROVAL,seq=seq,**event)),flush=True);seq+=1
    def alarm(*args):raise legacy.GateError('wall_cap')
    try:
        legacy.require(sys.argv[1:]==[APPROVAL],'approval_argument')
        emit({'event':'READY'})
        legacy.require(sys.platform=='linux' and sys.version_info[:2]==(3,12),'platform_python')
        legacy.require(os.geteuid()==0,'root_required')
        signal.signal(signal.SIGALRM,alarm);signal.alarm(REMOTE_SECONDS)
        result=observe(INVENTORY,emit=emit)
    except legacy.GateError as error:
        result=base_result();result['reason']=str(error) if str(error) in REASONS else 'readback_error'
    except Exception:result=base_result()
    finally:
        if sys.platform=='linux':signal.alarm(0)
    emit({'event':'RESULT','result':result})
    return 0 if result['status'] in ('ABSENT','VERIFIED') else 3


if __name__=='__main__':raise SystemExit(main())
