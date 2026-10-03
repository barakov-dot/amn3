"""One future kernel access probe; no CLI, app imports, service action or grant.

A caller must authenticate the persisted, root-private AccessPlan digest within
an exact approval permitting one <=20s child. This adapter observes current
bot mount namespace access under the planned service UID/GID and a fresh net
namespace. It does not reproduce every service sandbox or prove future startup,
OS integrity, application behavior, or content authenticity. Prior authenticated
plan/content verification remains mandatory. Root/kernel baseline is trusted.
"""
import base64
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
import zlib
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_linux as linux
from scripts import phase16_bot_stage_access as access
from scripts.vps.phase16_bot_retained_stage_remote import fingerprint
from scripts.phase16_bot_maintenance_storage import MaintenanceReader

MAX_COMPRESSED, MAX_DECODED = 65536, 2 * 1024 * 1024
CHILD_SECONDS, TOTAL_SECONDS = 20, 30
PROPERTIES = ('Id', 'LoadState', 'ActiveState', 'SubState', 'MainPID', 'InvocationID', 'ControlGroup',
    'PrivateUsers', 'DynamicUser', 'RootDirectory', 'RootImage', 'AppArmorProfile', 'SELinuxContext',
    'SmackProcessLabel', 'SystemCallFilter', 'NoNewPrivileges', 'PrivateTmp', 'ProtectSystem', 'ProtectHome')
CAPS = ('CapInh', 'CapPrm', 'CapEff', 'CapAmb')


class ProbeError(ValueError):
    """Closed, non-sensitive reason, including failures from injected adapters."""
    CODES = frozenset(('probe_payload_limit', 'probe_payload', 'probe_identity', 'probe_sandbox',
        'probe_credentials', 'probe_namespace', 'probe_plan_binding', 'probe_plan_scope', 'probe_nonce',
        'probe_private_plan', 'probe_platform', 'probe_plan_record', 'probe_proc_limit',
        'probe_identity_changed', 'probe_deadline', 'probe_result', 'probe_child_rejected',
        'probe_plan_changed', 'probe_incomplete'))

    def __init__(self, reason):
        super().__init__(reason if type(reason) is str and reason in self.CODES else 'probe_incomplete')


def require(value, reason):
    if not value:
        raise ProbeError(reason)


def request_digest(value):
    return hashlib.sha256(core.encoded(value)).hexdigest()


def pack_request(value):
    raw = core.encoded(value)
    require(len(raw) <= MAX_DECODED, 'probe_payload_limit')
    packed = zlib.compress(raw, 9)
    require(len(packed) <= MAX_COMPRESSED, 'probe_payload_limit')
    return base64.b64encode(packed).decode('ascii')


def unpack_request(value):
    try:
        require(isinstance(value, str) and len(value) <= 87384, 'probe_payload_limit')
        packed = base64.b64decode(value, validate=True)
        require(len(packed) <= MAX_COMPRESSED, 'probe_payload_limit')
        decoder = zlib.decompressobj()
        raw = decoder.decompress(packed, MAX_DECODED + 1)
        require(len(raw) <= MAX_DECODED and decoder.eof and not decoder.unconsumed_tail
                and not decoder.unused_data, 'probe_payload_limit')
        result = json.loads(raw)
        require(isinstance(result, dict) and raw == core.encoded(result), 'probe_payload')
        return result
    except ProbeError:
        raise
    except Exception:
        raise ProbeError('probe_payload') from None


def validate_snapshot(value, identity):
    fields = {'pid', 'start_ticks', 'invocation', 'boot_id', 'mount_ns', 'net_ns', 'parent_net_ns',
              'uid', 'gid', 'groups', 'caps', 'properties'}
    require(isinstance(value, dict) and set(value) == fields, 'probe_identity')
    props = value['properties']
    require(isinstance(props, dict) and set(props) == set(PROPERTIES)
            and all(isinstance(v, str) and len(v) <= 8192 for v in props.values()), 'probe_sandbox')
    require(type(value['pid']) is int and 0 < value['pid'] < 2 ** 31
        and type(value['start_ticks']) is int and value['start_ticks'] > 0
        and re.fullmatch('[0-9a-f]{32}', value['invocation'])
        and re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', value['boot_id']), 'probe_identity')
    require(props['Id'] == core.BOT and props['LoadState'] == 'loaded'
        and props['ActiveState'] == 'active' and props['SubState'] == 'running'
        and props['MainPID'] == str(value['pid']) and props['InvocationID'] == value['invocation']
        and props['ControlGroup'] == '/system.slice/' + core.BOT, 'probe_identity')
    require(props['PrivateUsers'] == props['DynamicUser'] == 'no'
        and all(props[name] == '' for name in ('RootDirectory', 'RootImage', 'AppArmorProfile',
            'SELinuxContext', 'SmackProcessLabel', 'SystemCallFilter'))
        and props['NoNewPrivileges'] in ('yes', 'no') and props['PrivateTmp'] in ('yes', 'no')
        and props['ProtectSystem'] in ('no', 'yes', 'full', 'strict')
        and props['ProtectHome'] in ('no', 'yes', 'read-only', 'tmpfs'), 'probe_sandbox')
    require(value['uid'] == identity.uid and value['gid'] == identity.gid
        and isinstance(value['groups'], list) and len(value['groups']) <= 1
        and all(type(g) is int and g == identity.gid for g in value['groups'])
        and value['caps'] == dict.fromkeys(CAPS, 0), 'probe_credentials')
    require(re.fullmatch(r'mnt:\[[0-9]+\]', value['mount_ns'])
        and all(re.fullmatch(r'net:\[[0-9]+\]', value[name]) for name in ('net_ns', 'parent_net_ns')), 'probe_namespace')


def validate_plan(plan, authorized):
    require(type(plan) is access.AccessPlan and isinstance(authorized, str)
        and re.fullmatch('[a-f0-9]{64}', authorized) and plan.digest == authorized == access._digest(plan)
        and plan.stage_root == access.STAGE_ROOT and plan.schema == 'phase16.stage-access-plan.v1'
        and plan.status == 'ACCESS_PLAN_READY_NOT_APPLIED', 'probe_plan_binding')
    access._identity(plan.identity)
    require(tuple(a.path for a in plan.ancestors) == access.ANCESTOR_PATHS, 'probe_plan_scope')
    require(0 < len(plan.objects) <= 43000 and len({v.path for v in plan.objects}) == len(plan.objects), 'probe_plan_scope')
    by_path = {v.path: v for v in plan.objects}
    require('.' in by_path, 'probe_plan_scope')
    for item in plan.objects:
        if item.path != '.':
            access._path(item.path)
            parent = item.path.rpartition('/')[0] or '.'
            require(parent in by_path and by_path[parent].kind == 'directory', 'probe_plan_scope')
        require(item.kind in ('file', 'directory', 'symlink') and type(item.device) is int and item.device >= 0
            and type(item.inode) is int and item.inode > 0 and type(item.size) is int and item.size >= 0,
            'probe_plan_scope')
    return by_path


def build_request(plan, authorized, state, *, nonce):
    by_path = validate_plan(plan, authorized)
    validate_snapshot(state, plan.identity)
    require(isinstance(nonce, str) and re.fullmatch('[a-f0-9]{32}', nonce), 'probe_nonce')
    directories, files, links = [], [], []
    spine = {'.', 'runtime-venv', 'runtime-venv/bin', 'runtime-venv/lib', 'runtime-venv/lib/python3.12'}
    site = access.runtime.SITE_PREFIX
    link_names = {'runtime-venv/lib64', *('runtime-venv/bin/' + name for name in access.LINKS)}
    total = 0
    for name, item in sorted(by_path.items()):
        if name in link_names:
            require(item.kind == 'symlink' and item.action == 'preserve_link' and
                item.before_mode == item.desired_mode and item.before_gid == item.desired_gid, 'probe_plan_scope')
            allowed = ('lib',) if name.endswith('/lib64') else (*access.LINKS, '/usr/bin/python3', '/usr/bin/python3.12')
            require(item.link_target in allowed, 'probe_plan_scope')
            links.append([name, item.device, item.inode, item.link_target])
            continue
        public = name == 'source' or name == 'source/app' or name.startswith('source/app/') or name == site or name.startswith(site + '/') or name == 'runtime-venv/pyvenv.cfg'
        if name not in spine and not public:
            require(item.desired_gid == 0 and not item.desired_mode & 0o077, 'probe_private_plan')
            continue
        require(item.kind in ('file', 'directory') and item.desired_gid == plan.identity.gid
            and item.action == 'set_mode_group', 'probe_plan_scope')
        if item.kind == 'directory':
            require(item.desired_mode == (0o710 if name in spine else 0o750), 'probe_plan_scope')
            directories.append([name, item.device, item.inode, item.desired_mode, item.desired_gid])
        else:
            require(item.desired_mode == 0o640 and isinstance(item.sha256, str)
                and re.fullmatch('[a-f0-9]{64}', item.sha256) and item.size <= 64 * 1024 * 1024, 'probe_plan_scope')
            total += item.size
            files.append([name, item.device, item.inode, item.size, item.desired_gid])
    require(total <= 512 * 1024 * 1024 and {v[0] for v in links} == link_names
        and {'source/app/__init__.py', 'source/app/main.py', 'runtime-venv/pyvenv.cfg'} <= {v[0] for v in files}
        and spine | {'source', 'source/app', site} <= {v[0] for v in directories}, 'probe_plan_scope')
    value = dict(schema='phase16.service-access-request.v1', plan_sha256=authorized, nonce=nonce,
        uid=plan.identity.uid, gid=plan.identity.gid, mount_ns=state['mount_ns'], net_ns=state['net_ns'],
        parent_net_ns=state['parent_net_ns'], stage_root=plan.stage_root,
        ancestors=[[a.path, a.device, a.inode, a.mode, a.gid] for a in plan.ancestors],
        directories=directories, files=files, links=links)
    pack_request(value)  # Enforce both transport and expansion caps before any child.
    return value


# Standalone stdlib only. Never import app/native wheel code; FileFinder merely
# returns a source package spec. Failure emits one fixed JSON record, no traceback.
BOOTSTRAP = r'''
import base64, hashlib, importlib.machinery, json, mmap, os, re, stat, sys, zlib
class ProbeStop(Exception): pass
def need(value, reason):
    if not value: raise ProbeStop(reason)
def encode(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n').encode('ascii')
def digest(value): return hashlib.sha256(encode(value)).hexdigest()
def main():
    need(sys.platform=='linux','platform')
    need(sys.version_info[:2]==(3,12),'python_version')
    need(all(hasattr(os,k) for k in ('O_PATH','O_NOFOLLOW','O_CLOEXEC','O_DIRECTORY')) and
         os.access in os.supports_effective_ids and hasattr(mmap,'PROT_EXEC'),'kernel_capability')
    need(len(sys.argv)==2 and len(sys.argv[1])<=87384,'payload')
    packed=base64.b64decode(sys.argv[1],validate=True)
    need(len(packed)<=65536,'payload')
    decoder=zlib.decompressobj();raw=decoder.decompress(packed,2097153)
    need(len(raw)<=2097152 and decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data,'payload')
    value=json.loads(raw)
    need(raw==encode(value) and set(value)=={'schema','plan_sha256','nonce','uid','gid','mount_ns','net_ns','parent_net_ns','stage_root','ancestors','directories','files','links'},'payload')
    need(value['schema']=='phase16.service-access-request.v1' and re.fullmatch('[a-f0-9]{64}',value['plan_sha256']) and re.fullmatch('[a-f0-9]{32}',value['nonce']),'payload')
    uid,gid=value['uid'],value['gid']
    need(type(uid) is int and type(gid) is int and 0<uid<2**31 and 0<gid<2**31,'credentials')
    need(os.getuid()==os.geteuid()==uid and os.getgid()==os.getegid()==gid and os.getgroups()==[],'credentials')
    with open('/proc/self/status','rb') as stream: status=stream.read(65537)
    need(len(status)<=65536,'credentials')
    fields={line.split(b':',1)[0]:line.split(b':',1)[1].strip() for line in status.splitlines() if b':' in line}
    need(all(fields.get(k)==b'0000000000000000' for k in (b'CapInh',b'CapPrm',b'CapEff',b'CapBnd',b'CapAmb')) and fields.get(b'NoNewPrivs')==b'1','credentials')
    need(os.readlink('/proc/self/ns/mnt')==value['mount_ns'],'mount_namespace')
    net=os.readlink('/proc/self/ns/net')
    need(re.fullmatch(r'net:\[[0-9]+\]',net) and net not in (value['net_ns'],value['parent_net_ns']),'network_namespace')
    root='/opt/amn2-spain/bot-candidates/phase16-bot-runtime40-20260929-6e68235-001'
    need(value['stage_root']==root and os.path.normpath(sys.executable)==root+'/runtime-venv/bin/python','interpreter')
    need(len(value['directories'])+len(value['files'])+len(value['links'])<=43000,'payload')
    def relative(path):
        need(isinstance(path,str) and len(path)<=512 and '\\' not in path and ':' not in path and
             all(ord(c)>=32 and ord(c)!=127 for c in path) and
             (path=='.' or all(p not in ('','.','..') for p in path.split('/'))),'path')
        return path
    names=[relative(v[0]) for kind in ('directories','files','links') for v in value[kind]]
    need(len(names)==len(set(names)),'payload')
    def stable(meta):
        return (meta.st_dev,meta.st_ino,meta.st_mode,meta.st_uid,meta.st_gid,meta.st_nlink,meta.st_size,meta.st_mtime_ns,meta.st_ctime_ns)
    def check(meta,dev,ino,mode,gid,kind):
        need(meta.st_dev==dev and meta.st_ino==ino and meta.st_uid==0 and meta.st_gid==gid and
             stat.S_IFMT(meta.st_mode)==kind and stat.S_IMODE(meta.st_mode)==mode and
             (kind!=stat.S_IFREG or meta.st_nlink==1),'object_metadata')
    flags=os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
    chain=[];rootfd=None
    try:
        current=os.open('/',flags);chain.append((current,None,None,os.fstat(current)))
        expected=value['ancestors']
        need([v[0] for v in expected]==['/','/opt','/opt/amn2-spain','/opt/amn2-spain/bot-candidates'],'ancestors')
        for index,part in enumerate(root.split('/')[1:]):
            if index<len(expected):
                _,dev,ino,mode,agid=expected[index]
                check(os.fstat(current),dev,ino,mode,agid,stat.S_IFDIR)
            parent=current;current=os.open(part,flags,dir_fd=parent)
            chain.append((current,parent,part,os.fstat(current)))
        rootfd=current
        def parent_fd(path):
            fd=os.dup(rootfd)
            try:
                for part in path.split('/')[:-1]:
                    nxt=os.open(part,flags,dir_fd=fd);os.close(fd);fd=nxt
                return fd
            except BaseException:
                os.close(fd);raise
        def named(meta,parent,leaf):
            need(stable(meta)==stable(os.stat(leaf,dir_fd=parent,follow_symlinks=False)),'object_changed')
        for path,dev,ino,mode,agid in value['directories']:
            need(mode in (0o710,0o750) and agid==gid,'directory_scope')
            parent=parent_fd(path)
            try:
                leaf=path.rsplit('/',1)[-1];meta=os.stat(leaf,dir_fd=parent,follow_symlinks=False)
                check(meta,dev,ino,mode,agid,stat.S_IFDIR)
                need(os.access(root if path=='.' else root+'/'+path,os.X_OK|(os.R_OK if mode==0o750 else 0),effective_ids=True),'directory_access')
                if mode==0o750:
                    fd=os.open(leaf,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
                    try:
                        need(stable(meta)==stable(os.fstat(fd)) and len(os.listdir(fd))<=4096,'directory_access')
                    finally:os.close(fd)
                named(meta,parent,leaf)
            finally:os.close(parent)
        total=0;native=0
        for path,dev,ino,size,agid in value['files']:
            need((path.startswith('source/app/') or path.startswith('runtime-venv/lib/python3.12/site-packages/') or path=='runtime-venv/pyvenv.cfg') and type(size) is int and 0<=size<=67108864 and agid==gid,'file_scope')
            total+=size;need(total<=536870912,'file_limit')
            parent=parent_fd(path)
            try:
                leaf=path.rsplit('/',1)[-1]
                fd=os.open(leaf,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,dir_fd=parent)
                try:
                    meta=os.fstat(fd);check(meta,dev,ino,0o640,agid,stat.S_IFREG)
                    need(meta.st_size==size,'file_size');seen=0
                    while True:
                        chunk=os.read(fd,min(1048576,size+1-seen))
                        if not chunk:break
                        seen+=len(chunk);need(seen<=size,'file_size')
                    need(seen==size,'file_size')
                    if path.endswith('.so'):
                        need(size>0,'executable_mapping')
                        region=mmap.mmap(fd,min(size,4096),flags=mmap.MAP_PRIVATE,prot=mmap.PROT_READ|mmap.PROT_EXEC)
                        region.close();native+=1
                    need(stable(meta)==stable(os.fstat(fd)),'object_changed');named(meta,parent,leaf)
                finally:os.close(fd)
            finally:os.close(parent)
        for path,dev,ino,target in value['links']:
            need(path in ('runtime-venv/lib64','runtime-venv/bin/python','runtime-venv/bin/python3','runtime-venv/bin/python3.12'),'link_scope')
            parent=parent_fd(path)
            try:
                leaf=path.rsplit('/',1)[-1];meta=os.stat(leaf,dir_fd=parent,follow_symlinks=False)
                need(stat.S_ISLNK(meta.st_mode) and meta.st_uid==0 and meta.st_nlink==1 and meta.st_dev==dev and meta.st_ino==ino and os.readlink(leaf,dir_fd=parent)==target,'link_identity')
                named(meta,parent,leaf)
            finally:os.close(parent)
        finder=importlib.machinery.FileFinder(root+'/source',(importlib.machinery.SourceFileLoader,importlib.machinery.SOURCE_SUFFIXES))
        found=finder.find_spec('app')
        need(found is not None and found.origin==root+'/source/app/__init__.py' and 'app' not in sys.modules,'filefinder')
        for fd,parent,leaf,meta in chain:
            need(stable(meta)==stable(os.fstat(fd)),'ancestor_changed')
            if parent is not None:named(meta,parent,leaf)
        need(os.readlink('/proc/self/ns/mnt')==value['mount_ns'] and os.readlink('/proc/self/ns/net')==net,'namespace_changed')
        return dict(status='KERNEL_ACCESS_OBSERVED',request_sha256=digest(value),plan_sha256=value['plan_sha256'],nonce=value['nonce'],uid=uid,gid=gid,directories=len(value['directories']),files=len(value['files']),executable_mappings=native,filefinder='APP_SPEC_FOUND_NO_IMPORT',private_network=True,capabilities_cleared=True)
    finally:
        for fd,*_ in reversed(chain):os.close(fd)
try: result=main()
except ProbeStop as error: result={'status':'STOP','reason':str(error)}
except BaseException: result={'status':'STOP','reason':'kernel_access'}
sys.stdout.buffer.write(encode(result))
'''


class LinuxObserver:
    """Native scoped reader; no discovery of unrelated services or profiles."""
    def __init__(self, run):
        require(sys.platform == 'linux' and os.geteuid() == 0, 'probe_platform')
        self.run = run

    def read_plan_record(self, path):
        path = Path(path)
        require(path.is_absolute() and re.fullmatch(r'stage-access\.[A-Za-z0-9][A-Za-z0-9_-]{0,79}\.plan\.json', path.name)
            and str(path.parent).startswith('/var/lib/amn2-spain/phase16-maintenance/'), 'probe_plan_record')
        with MaintenanceReader(str(path.parent)) as reader:
            directory = os.fstat(reader.root_fd)
            require(directory.st_uid == directory.st_gid == 0 and stat.S_IMODE(directory.st_mode) == 0o700,
                    'probe_plan_record')
            fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK, dir_fd=reader.root_fd)
            try:
                before = os.fstat(fd)
                require(stat.S_ISREG(before.st_mode) and before.st_uid == before.st_gid == 0 and before.st_nlink == 1
                    and stat.S_IMODE(before.st_mode) == 0o600 and before.st_size <= MAX_DECODED
                    and not os.listxattr(fd), 'probe_plan_record')
                raw = bytearray()
                while len(raw) <= MAX_DECODED:
                    block = os.read(fd, min(1048576, MAX_DECODED + 1 - len(raw)))
                    if not block:
                        break
                    raw.extend(block)
                require(len(raw) == before.st_size and len(raw) <= MAX_DECODED and
                    fingerprint(before) == fingerprint(os.fstat(fd)) == fingerprint(os.stat(path.name, dir_fd=reader.root_fd, follow_symlinks=False)), 'probe_plan_record')
                reader.check_chain()
                return bytes(raw)
            finally:
                os.close(fd)

    def read(self, path, maximum):
        with Path(path).open('rb') as stream:
            raw = stream.read(maximum + 1)
        require(len(raw) <= maximum, 'probe_proc_limit')
        return raw

    def start_ticks(self, pid):
        raw = self.read('/proc/' + str(pid) + '/stat', 8192)
        fields = raw.rpartition(b') ')[2].split()
        require(raw.startswith(str(pid).encode() + b' (') and len(fields) >= 20 and fields[19].isdigit(), 'probe_identity')
        return int(fields[19])

    def snapshot(self, seconds):
        raw = self.run(['systemctl', 'show', '--no-pager', '--property=' + ','.join(PROPERTIES), core.BOT], seconds)
        require(isinstance(raw, bytes) and len(raw) <= 65536, 'probe_sandbox')
        props = {}
        for line in raw.decode('ascii').splitlines():
            key, value = line.split('=', 1)
            require(key in PROPERTIES and key not in props, 'probe_sandbox')
            props[key] = value
        require(set(props) == set(PROPERTIES) and re.fullmatch('[1-9][0-9]{0,9}', props['MainPID']), 'probe_sandbox')
        pid = int(props['MainPID']); start = self.start_ticks(pid)
        status = self.read('/proc/' + str(pid) + '/status', 65536)
        fields = {}
        for line in status.splitlines():
            if b':' in line:
                key, value = line.split(b':', 1)
                if key in (b'Uid', b'Gid', b'Groups', *(name.encode() for name in CAPS)):
                    require(key not in fields, 'probe_identity')
                    fields[key] = value.split()
        uid, gid = fields[b'Uid'], fields[b'Gid']
        require(len(uid) == len(gid) == 4 and len(set(uid)) == len(set(gid)) == 1, 'probe_credentials')
        groups = [int(v) for v in fields[b'Groups']]
        caps = {name: int(fields[name.encode()][0], 16) for name in CAPS}
        mount = os.readlink('/proc/' + str(pid) + '/ns/mnt')
        net = os.readlink('/proc/' + str(pid) + '/ns/net')
        parent_net = os.readlink('/proc/self/ns/net')
        boot = self.read('/proc/sys/kernel/random/boot_id', 64).decode('ascii').strip()
        require(self.start_ticks(pid) == start and os.readlink('/proc/' + str(pid) + '/ns/mnt') == mount
                and os.readlink('/proc/' + str(pid) + '/ns/net') == net, 'probe_identity_changed')
        return dict(pid=pid, start_ticks=start, invocation=props['InvocationID'], boot_id=boot,
            mount_ns=mount, net_ns=net, parent_net_ns=parent_net, uid=int(uid[0]), gid=int(gid[0]),
            groups=groups, caps=caps, properties=props)


def check_record(raw, plan):
    require(isinstance(raw, bytes) and len(raw) <= MAX_DECODED, 'probe_plan_record')
    value = json.loads(raw)
    require(isinstance(value, dict) and set(value) == {'plan', 'binding'} and raw == core.encoded(value)
        and value['plan'] == json.loads(core.encoded(asdict(plan))) and isinstance(value['binding'], dict)
        and value['binding'].get('authorized_plan_sha256') == plan.digest, 'probe_plan_record')
    return hashlib.sha256(raw).hexdigest()


def probe_service_access(plan, *, authorized_plan_sha256, plan_record_path, observer=None,
                         run=None, clock=time.monotonic):
    """One probe per call, no retry. Default run is bounded and environment-clean.

    This read-only helper is not a one-shot mutation claim or permission grant.
    Its caller must own and record exact approval for the single child request.
    """
    try:
        deadline = clock() + TOTAL_SECONDS
        def remaining():
            require(clock() < deadline, 'probe_deadline')
            return deadline - clock()
        validate_plan(plan, authorized_plan_sha256)
        run = linux.BoundedCommand(maximum=16384) if run is None else run
        observer = LinuxObserver(run) if observer is None else observer
        record = observer.read_plan_record(Path(plan_record_path))
        record_sha = check_record(record, plan)
        before = observer.snapshot(min(5, remaining()))
        validate_snapshot(before, plan.identity)
        request = build_request(plan, authorized_plan_sha256, before, nonce=os.urandom(16).hex())
        packed = pack_request(request)
        argv = ['/usr/bin/unshare', '--net', '/usr/bin/nsenter', '--target', str(before['pid']), '--mount',
            '/usr/bin/setpriv', '--reuid=' + str(plan.identity.uid), '--regid=' + str(plan.identity.gid),
            '--clear-groups', '--inh-caps=-all', '--ambient-caps=-all', '--bounding-set=-all', '--no-new-privs',
            plan.stage_root + '/runtime-venv/bin/python', '-I', '-S', '-B', '-c', BOOTSTRAP, packed]
        require(sum(len(v.encode()) + 1 for v in argv) <= 131072, 'probe_payload_limit')
        raw = run(argv, min(CHILD_SECONDS, remaining()))
        remaining()
        require(isinstance(raw, bytes) and len(raw) <= 16384, 'probe_result')
        result = json.loads(raw)
        expected = dict(status='KERNEL_ACCESS_OBSERVED', request_sha256=request_digest(request),
            plan_sha256=plan.digest, nonce=request['nonce'], uid=plan.identity.uid, gid=plan.identity.gid,
            directories=len(request['directories']), files=len(request['files']),
            executable_mappings=sum(v[0].endswith('.so') for v in request['files']),
            filefinder='APP_SPEC_FOUND_NO_IMPORT', private_network=True, capabilities_cleared=True)
        require(raw == core.encoded(result) and result == expected, 'probe_child_rejected')
        after = observer.snapshot(min(5, remaining()))
        validate_snapshot(after, plan.identity)
        require(before == after, 'probe_identity_changed')
        require(observer.read_plan_record(Path(plan_record_path)) == record, 'probe_plan_changed')
        remaining()
        return dict(status='KERNEL_STAGE_ACCESS_OBSERVED_NOT_HOST_ADMITTED', host_admitted=False,
            plan_sha256=plan.digest, plan_record_sha256=record_sha, request_sha256=request_digest(request),
            bootstrap_sha256=hashlib.sha256(BOOTSTRAP.encode()).hexdigest(), bot_identity_sha256=core.digest(before),
            service_uid=plan.identity.uid, service_gid=plan.identity.gid, checked_files=result['files'],
            checked_directories=result['directories'], executable_mappings=result['executable_mappings'],
            content_authentication='PRIOR_APPROVED_PLAN_REQUIRED', application_imported=False,
            database_opened=False, telegram_contacted=False, full_service_sandbox_proven=False,
            future_access_guaranteed=False)
    except ProbeError:
        raise
    except Exception:
        raise ProbeError('probe_incomplete') from None
