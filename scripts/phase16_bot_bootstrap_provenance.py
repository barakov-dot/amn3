"""Bootstrap integrity against the existing trusted OS package baseline.

This is NOT publisher authentication or a host compromise audit. It relies on
root-owned OS binaries and the dpkg database, just as the runner trusts /usr/bin/
python3 and the stdlib. It never builds trust from the installed venv RECORD.
The seed wheel must match python3-pip-whl's independent package MD5 manifest;
its SHA256 becomes the exact pin for comparing retained venv content. No install,
network, app import, package changes, or CLI. Unsupported layouts STOP.
"""
import hashlib
import os
import re
from scripts.phase16_bot_runtime_content import WheelPin
from scripts.vps.phase16_bot_stage_readback_remote import BoundTree

PACKAGE='python3-pip-whl'
DIRECTORY='/usr/share/python-wheels'
QUERY=['dpkg-query','--show','--showformat=${Status}\t${Version}\t${Architecture}\n',PACKAGE]
CONTROL=['dpkg-query','--control-show',PACKAGE,'md5sums']
PATTERN=r'pip-([0-9]+(?:\.[0-9]+){1,3})-py3-none-any\.whl'

class ProvenanceError(ValueError):pass

def require(value,reason):
    if not value:raise ProvenanceError(reason)

def seed_name(names):
    require(isinstance(names,list) and len(names)<=64 and all(isinstance(n,str) for n in names),
            'bootstrap_directory')
    candidates=[n for n in names if n.startswith('pip-')]
    require(len(candidates)==1 and re.fullmatch(PATTERN,candidates[0]),'bootstrap_seed_selection')
    return DIRECTORY.lstrip('/')+'/'+candidates[0]

def pin_os_seed(path,raw,manifest,package):
    require(isinstance(path,str) and path.startswith(DIRECTORY.lstrip('/')+'/'),'bootstrap_path')
    name=path[len(DIRECTORY):]
    match=re.fullmatch(PATTERN,name)
    require(match is not None,'bootstrap_path')
    require(isinstance(raw,bytes) and 0<len(raw)<=32*1024*1024,'bootstrap_wheel_size')
    require(isinstance(manifest,bytes) and len(manifest)<=65536 and
            isinstance(package,bytes) and len(package)<=512,'bootstrap_package_shape')
    try:lines=manifest.decode('ascii').splitlines();status=package.decode('ascii')
    except UnicodeError:raise ProvenanceError('bootstrap_package_encoding') from None
    state=re.fullmatch(r'install ok installed\t([0-9][A-Za-z0-9.+:~-]{0,100})\tall\n',status)
    require(state is not None,'bootstrap_package_status')
    hits=[]
    for line in lines:
        entry=re.fullmatch(r'([0-9a-f]{32})  ([A-Za-z0-9_./+~-]+)',line)
        require(entry is not None,'bootstrap_package_manifest')
        if entry[2]==path:hits.append(entry[1])
    require(len(hits)==1 and hashlib.md5(raw).hexdigest()==hits[0],'bootstrap_package_mismatch')
    pin=WheelPin(name,len(raw),hashlib.sha256(raw).hexdigest(),'pip',match[1],role='bootstrap')
    receipt=dict(trust='EXISTING_OS_PACKAGE_BASELINE',publisher_signature_verified=False,
        package=PACKAGE,package_version=state[1],seed_wheel=pin.file,seed_sha256=pin.sha256,
        package_md5_matched=True,installed_venv_content='NOT_CHECKED_BY_THIS_COLLECTOR')
    return pin,receipt

def collect(run,names,read,stable):
    status=run(QUERY,5);manifest=run(CONTROL,5)
    before=names();path=seed_name(before);raw=read('/'+path)
    pin,receipt=pin_os_seed(path,raw,manifest,status)
    require(status==run(QUERY,5) and manifest==run(CONTROL,5) and before==names(),
            'bootstrap_evidence_changed')
    stable()
    return pin,raw,receipt

def collect_live(client):
    """Only in an exact-approved host packet; root/no-link secure OS seed reads."""
    try:
        with BoundTree(DIRECTORY) as reader:
            def names():return sorted(os.listdir(reader.root_fd))
            def read(path):
                require(path.startswith(DIRECTORY+'/'),'bootstrap_path')
                name=path[len(DIRECTORY)+1:]
                require(re.fullmatch(PATTERN,name),'bootstrap_path')
                return reader.read_file(name,32*1024*1024)
            return collect(client.run,names,read,reader.stable)
    except ProvenanceError:raise
    except Exception:raise ProvenanceError('bootstrap_collection_failed') from None
