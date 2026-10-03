"""Compose retained candidate checks before an exact-approved maintenance window.

No CLI, SSH, install, chmod/chown, DB access or application execution. collect_live
is an explicit read-only Linux entry for a future approved packet. Its result is
an access PLAN, never host admission: writer ownership, pending data, startup
assessment, unit sandbox and applying/verifying the plan remain separate gates.
"""
from dataclasses import dataclass
import hashlib
import os
from pathlib import PurePosixPath
import platform
import re
from types import MappingProxyType
from scripts import phase16_bot_bootstrap_provenance as bootstrap
from scripts import phase16_bot_effective_settings as settings
from scripts import phase16_bot_runtime_content as runtime
from scripts import phase16_bot_stage_access as access
from scripts import phase16_bot_maintenance as core
from scripts.vps import phase16_bot_stage_readback_remote as readback

STAGE=access.STAGE_ROOT
INVENTORY_SHA256='647a32f7a538028a8debbe8169ade373ea08b5d1c1b0467a36a9253380852aec'
SAVED_RECEIPT_SHA256='de51f2e6905ae6860eefaf455e40e4512377d92d97c6024319e01b2cbb5d1694'
IDENTITY_FIELDS={'User':'s','Group':'s','SupplementaryGroups':'as','DynamicUser':'b'}

class AdmissionError(ValueError):pass

def require(value,reason):
    if not value:raise AdmissionError(reason)

@dataclass(frozen=True)
class Catalog:
    inventory: dict
    wheels: dict
    source_pins: dict

@dataclass(frozen=True)
class CandidateProof:
    stage_result: dict
    runtime_expected: runtime.ExpectedRuntime
    access_plan: access.AccessPlan
    settings: dict
    bootstrap_provenance: dict
    status: str='CANDIDATE_CONTENT_VERIFIED_ACCESS_NOT_APPLIED'

def catalog(raw):
    require(isinstance(raw,bytes),'candidate_catalog')
    raw=raw.replace(b'\r\n',b'\n')
    require(hashlib.sha256(raw).hexdigest()==INVENTORY_SHA256,'candidate_catalog_binding')
    value=readback.strict_json(raw);wheels={};source={}
    require(set(value)=={'files','pins'} and len(value['files'])==200 and len(value['pins'])==40,'candidate_catalog')
    for path,(size,digest) in value['files'].items():
        if path.startswith('source/'):
            source[path[len('source/'):]]=(size,digest)
        elif path.startswith('payload/wheelhouse/runtime/') and path.endswith('.whl'):
            filename=PurePosixPath(path).name;parts=filename.split('-')
            name=re.sub(r'[-_.]+','-',parts[0]).lower();version=parts[1]
            require(name in value['pins'] and value['pins'][name]==version,'candidate_wheel_catalog')
            wheels[path]=runtime.WheelPin(filename,size,digest,name,version)
    require(len(source)==159 and len(wheels)==40 and len({p.name for p in wheels.values()})==40,
            'candidate_catalog')
    return Catalog(value,MappingProxyType(wheels),MappingProxyType(source))

def venv_pin(raw,*,os_python_version):
    require(isinstance(raw,bytes) and len(raw)<=8192 and re.fullmatch(r'3\.12\.[0-9]+',os_python_version),
            'candidate_venv')
    try:text=raw.decode('ascii')
    except UnicodeError:raise AdmissionError('candidate_venv') from None
    values={}
    for line in text.split('\n'):
        if not line:continue
        require(' = ' in line,'candidate_venv')
        key,value=line.split(' = ',1)
        require(key not in values and '\r' not in line,'candidate_venv');values[key]=value
    require(set(values)=={'home','include-system-site-packages','version','executable','command'},'candidate_venv')
    require(values['home']=='/usr/bin' and values['include-system-site-packages']=='false' and
            values['version']==os_python_version and values['executable']=='/usr/bin/python3.12',
            'candidate_venv')
    require(values['command'] in tuple(exe+' -m venv '+STAGE+'/runtime-venv'
             for exe in ('/usr/bin/python3','/usr/bin/python3.12')),'candidate_venv_command')
    return len(raw),hashlib.sha256(raw).hexdigest()

def local_identity(passwd,groups,properties):
    require(properties==dict(User='amn2-spain',Group='amn2-spain',SupplementaryGroups=[],DynamicUser=False),
            'candidate_identity')
    try:
        require(isinstance(passwd,bytes) and isinstance(groups,bytes) and
                len(passwd)<=262144 and len(groups)<=262144,'candidate_identity')
        users=[line.split(':') for line in passwd.decode('utf-8').splitlines() if line]
        group_rows=[line.split(':') for line in groups.decode('utf-8').splitlines() if line]
        require(all(len(row)==7 for row in users) and all(len(row)==4 for row in group_rows),'candidate_identity')
        user=[row for row in users if row[0]=='amn2-spain'];group=[row for row in group_rows if row[0]=='amn2-spain']
        require(len(user)==len(group)==1,'candidate_identity')
        uid,primary,gid=int(user[0][2]),int(user[0][3]),int(group[0][2])
        require(0<uid<2**31 and 0<gid<2**31 and gid==primary,'candidate_identity')
        memberships={gid}|{int(row[2]) for row in group_rows if 'amn2-spain' in row[3].split(',')}
        require(memberships=={gid},'candidate_identity')
        require(sum(row[2]==str(uid) for row in users)==1 and sum(row[2]==str(gid) for row in group_rows)==1,
                'candidate_identity')
        return access.ServiceIdentity(uid,gid,(gid,))
    except AdmissionError:raise
    except (ValueError,UnicodeError,TypeError):raise AdmissionError('candidate_identity') from None

def collect_live(client,inventory_raw):
    """Heavy initial proof, before permission transition; not a per-step guard.

    The OS/root-operator baseline is trusted. NSS membership is compared with the
    bounded local-account declaration; unsupported custom identities stop.
    """
    try:
        pinned=catalog(inventory_raw)
        stage=readback.observe(pinned.inventory)
        require(stage['status']=='VERIFIED' and stage['saved_receipt_sha256']==SAVED_RECEIPT_SHA256,
                'candidate_stage')
        effective=settings.collect_live(client)
        os_pin,os_wheel,provenance=bootstrap.collect_live(client)
        reader=settings.RootSettingsReader()
        def props():return {k:client.bus_property(core.BOT,'Service',k,s) for k,s in IDENTITY_FIELDS.items()}
        original=props();identity=local_identity(reader('/etc/passwd'),reader('/etc/group'),original)
        require(set(os.getgrouplist('amn2-spain',identity.gid))=={identity.gid},'candidate_identity_nss')
        with access.UnixStageReader() as tree:
            wheels={pin.file:tree.read_file(path,pin.size,expected_size=pin.size) for path,pin in pinned.wheels.items()}
            require(os_pin.file not in wheels,'candidate_bootstrap_collision');wheels[os_pin.file]=os_wheel
            expected=runtime.build_expected(wheels,(*pinned.wheels.values(),os_pin))
            cfg=tree.read_file('runtime-venv/pyvenv.cfg',8192)
            cfg_pin=venv_pin(cfg,os_python_version=platform.python_version())
            plan=access.build_access_plan(tree,expected,dict(pinned.source_pins),identity,pyvenv_pin=cfg_pin)
            tree.stable()
        require(props()==original and settings.collect_live(client)==effective,'candidate_changed')
        reader.stable()
        return CandidateProof(stage,expected,plan,effective,provenance)
    except AdmissionError:raise
    except Exception:raise AdmissionError('candidate_collection_failed') from None
