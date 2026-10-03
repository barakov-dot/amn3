"""Descriptor-bound reads within the fixed Phase16 maintenance subtree.

The sole non-root ancestor exception is /var/lib/amn2-spain, uid/gid 61212,
mode 0750, as installed by Phase12. It is NOT trusted to keep names stable:
all original ancestors, named entries, full metadata and ACLs are checked
again before returning bytes. A rename causes STOP. Maintenance directories
remain root:root 0700; this adapter never creates/chowns/chmods any object.

Holding this reader pins its directory FDs, not later absolute-path imports.
Callers executing verified code must retain FDs and use descriptor-bound paths.
The caller authenticates any expected digest; a fresh self-hash is no provenance.
OS/kernel/root remain the trust baseline. Native Linux acceptance is separate.
"""
import hashlib
import os
from pathlib import PurePosixPath
import re
import stat
import sys

from scripts.vps.phase16_bot_retained_stage_remote import SecureReader, fingerprint

SERVICE_PARENT = '/var/lib/amn2-spain'
MAINTENANCE_ROOT = SERVICE_PARENT + '/phase16-maintenance'
MAX_BYTES = 16 * 1024 * 1024


class StorageError(ValueError):
    pass


def require(value, reason):
    if not value:
        raise StorageError(reason)


def _canonical(path):
    value = os.fspath(path)
    require(isinstance(value, str) and 0 < len(value) <= 4096 and '\\' not in value
        and ':' not in value and all(32 <= ord(c) < 127 for c in value), 'storage_path')
    parsed = PurePosixPath(value)
    require(parsed.is_absolute() and parsed.as_posix() == value and '..' not in parsed.parts
        and len(parsed.parts) <= 40, 'storage_path')
    return value


def _subtree(path):
    value = _canonical(path)
    require(value == MAINTENANCE_ROOT or value.startswith(MAINTENANCE_ROOT + '/'), 'storage_scope')
    if value != MAINTENANCE_ROOT:
        operation = value[len(MAINTENANCE_ROOT) + 1:].split('/')[0]
        require(re.fullmatch(r'phase16-[a-z0-9-]{1,80}', operation), 'storage_operation')
    return value


def check_owned_parent(meta, path):
    """Pure directory ownership predicate; raises on failure, returns True.

    This helper alone does NOT prove no-follow traversal, ACLs or continuity.
    Supply the canonical name reconstructed from the held descriptor chain.
    """
    path = _canonical(path)
    require(stat.S_ISDIR(meta.st_mode), 'storage_directory')
    mode = stat.S_IMODE(meta.st_mode)
    if path == SERVICE_PARENT and meta.st_uid == meta.st_gid == 61212:
        require(mode == 0o750, 'storage_service_parent')
    elif path == MAINTENANCE_ROOT or path.startswith(MAINTENANCE_ROOT + '/'):
        _subtree(path)
        require(meta.st_uid == meta.st_gid == 0 and mode == 0o700, 'storage_private_directory')
    else:
        require(meta.st_uid == 0 and not mode & 0o022, 'storage_directory_owner')
    return True


class MaintenanceReader(SecureReader):
    """SecureReader-compatible fixed-subtree reader with retained chain checks.

    read(name,size) remains bounded and now also requires empty xattr names.
    Use read_private/read_owned below for explicit private mode and hash checks.
    Injected syscalls support portable tests; default native use requires Linux.
    """
    def __init__(self, root, *, syscalls=os):
        root = _subtree(root)
        require(syscalls is not os or sys.platform == 'linux', 'storage_platform')
        super().__init__(root, syscalls=syscalls)

    def _chain_path(self, fd):
        paths = {}
        for current, parent, name, _meta in self.chain:
            if parent is None:
                require(name == '/', 'storage_chain')
                paths[current] = '/'
            else:
                require(parent in paths, 'storage_chain')
                paths[current] = paths[parent].rstrip('/') + '/' + name
        require(fd in paths, 'storage_chain')
        return paths[fd]

    def directory(self, name, parent=None):
        api = self.os
        if parent is None:
            require(name == '/' and not self.chain, 'storage_chain')
            path = '/'
        else:
            require(isinstance(name, str) and name not in ('', '.', '..') and '/' not in name, 'storage_path')
            path = self._chain_path(parent).rstrip('/') + '/' + name
        # directory() is also used for nested read() parents, never an escape.
        require(path in ('/', '/var', '/var/lib', SERVICE_PARENT) or
                path == MAINTENANCE_ROOT or path.startswith(MAINTENANCE_ROOT + '/'), 'storage_scope')
        path = _canonical(path)
        fd = api.open(name, api.O_RDONLY | api.O_DIRECTORY | api.O_NOFOLLOW | api.O_CLOEXEC,
                      **({} if parent is None else {'dir_fd': parent}))
        try:
            meta = api.fstat(fd)
            check_owned_parent(meta, path)
            require(not api.listxattr(fd), 'storage_acl')
            named = api.stat(name, follow_symlinks=False, **({} if parent is None else {'dir_fd': parent}))
            require(fingerprint(meta) == fingerprint(api.fstat(fd)) == fingerprint(named), 'storage_changed')
            self.chain.append((fd, parent, name, meta))
            return fd
        except BaseException:
            api.close(fd)
            raise

    def check_chain(self):
        for fd, parent, name, before in self.chain:
            check_owned_parent(before, self._chain_path(fd))
            require(not self.os.listxattr(fd), 'storage_acl')
            after = self.os.fstat(fd)
            named = self.os.stat(name, follow_symlinks=False, **({} if parent is None else {'dir_fd': parent}))
            require(fingerprint(before) == fingerprint(after) == fingerprint(named), 'storage_changed')

    def _file(self, name, maximum, *, private=False, expected_size=None, expected_sha256=None, content=True):
        require(self.root_fd is not None and self.chain and self._chain_path(self.root_fd) == str(self.root),
                'storage_not_open')
        require(type(maximum) is int and 0 <= maximum <= MAX_BYTES, 'storage_size')
        require(isinstance(name, str) and name and not name.startswith('/') and
                all(part not in ('', '.', '..') for part in name.split('/')), 'storage_path')
        _subtree(str(self.root) + '/' + name)
        require(expected_sha256 is None or (isinstance(expected_sha256, str) and
                re.fullmatch('[0-9a-f]{64}', expected_sha256)), 'storage_hash')
        require(content or expected_sha256 is None, 'storage_hash')
        self.check_chain()
        checkpoint = len(self.chain)
        parent, fd = self.root_fd, None
        try:
            for part in name.split('/')[:-1]:
                parent = self.directory(part, parent)
            leaf = name.split('/')[-1]
            fd = self.os.open(leaf, self.os.O_RDONLY | self.os.O_NOFOLLOW | self.os.O_CLOEXEC | self.os.O_NONBLOCK,
                              dir_fd=parent)
            before = self.os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_uid == before.st_gid == 0 and before.st_nlink == 1,
                    'storage_file')
            mode = stat.S_IMODE(before.st_mode)
            require((mode == 0o600 if private else not mode & 0o7022), 'storage_file_mode')
            require(not self.os.listxattr(fd), 'storage_acl')
            require(0 <= before.st_size <= maximum and (expected_size is None or before.st_size == expected_size), 'storage_size')
            raw = bytearray()
            if content:
                while len(raw) <= before.st_size:
                    block = self.os.read(fd, min(1024 * 1024, before.st_size + 1 - len(raw)))
                    if not block:
                        break
                    raw.extend(block)
                require(len(raw) == before.st_size, 'storage_size')
            require(not self.os.listxattr(fd), 'storage_acl')
            named = self.os.stat(leaf, dir_fd=parent, follow_symlinks=False)
            require(fingerprint(before) == fingerprint(self.os.fstat(fd)) == fingerprint(named), 'storage_changed')
            self.check_chain()
            if expected_sha256 is not None:
                require(hashlib.sha256(raw).hexdigest() == expected_sha256, 'storage_hash')
            return bytes(raw) if content else fingerprint(before)
        finally:
            if fd is not None:
                self.os.close(fd)
            for extra, *_ in reversed(self.chain[checkpoint:]):
                self.os.close(extra)
            del self.chain[checkpoint:]

    def read(self, name, size):
        require(type(size) is int and 0 <= size <= MAX_BYTES, 'storage_size')
        return self._file(name, size, expected_size=size)


def read_owned(path, maximum, *, private=False, expected_sha256=None, syscalls=os):
    """Return bounded bytes only after FD, named chain, ACL and optional hash checks."""
    path = PurePosixPath(_subtree(path))
    with MaintenanceReader(str(path.parent), syscalls=syscalls) as reader:
        return reader._file(path.name, maximum, private=private, expected_sha256=expected_sha256)


def read_private(path, maximum, *, expected_sha256=None, syscalls=os):
    """Read one root:root 0600 single-link regular file; no path-based reopen."""
    return read_owned(path, maximum, private=True, expected_sha256=expected_sha256, syscalls=syscalls)


def safe_owned_path(path, private=False, *, syscalls=os):
    """Return this regular file's checked metadata tuple, not future access proof.

    No bytes are read; use read_owned/read_private to authenticate file content.
    The returned tuple does not hold a descriptor after this call finishes.
    """
    path = PurePosixPath(_subtree(path))
    with MaintenanceReader(str(path.parent), syscalls=syscalls) as reader:
        return reader._file(path.name, MAX_BYTES, private=private, content=False)

# Embed this literal before ANY project import. Its only imports are trusted
# stdlib. Windows supports local source/cache fixtures, never Linux admission.
IMPORT_BOOTSTRAP = r'''
import hashlib as _p16_hashlib, importlib.abc as _p16_abc, importlib.machinery as _p16_machinery
import importlib.util as _p16_util, os as _p16_os, pathlib as _p16_pathlib
import re as _p16_re, stat as _p16_stat, sys as _p16_sys
# Capture the -I -S interpreter search path before any project code executes.
_p16_stdlib_paths=tuple(_p16_sys.path)
_p16_stdlib_roots=tuple(_p16_os.path.normcase(_p16_os.path.realpath(p)) for p in _p16_stdlib_paths)
_p16_builtin_finder=_p16_machinery.BuiltinImporter
_p16_frozen_finder=_p16_machinery.FrozenImporter
_p16_path_finder=_p16_machinery.PathFinder
_p16_retained=[]
def _p16_need(value,reason):
    if not value: raise RuntimeError(reason)
def _p16_fp(meta):
    timestamp=meta.st_ctime_ns if _p16_sys.platform=='linux' else getattr(meta,'st_birthtime_ns',meta.st_ctime_ns)
    return (meta.st_dev,meta.st_ino,meta.st_mode,meta.st_uid,meta.st_gid,meta.st_nlink,meta.st_size,meta.st_mtime_ns,timestamp)
def _p16_platform():
    _p16_need(_p16_sys.version_info[:2]==(3,12) and _p16_sys.platform in ('linux','win32'),'bootstrap_platform')
    if _p16_sys.platform=='linux': _p16_need(_p16_os.geteuid()==0,'bootstrap_root')
def _p16_path(value):
    _p16_need(isinstance(value,str) and len(value)<=4096 and all(32<=ord(c)<127 for c in value),'bootstrap_path')
    parsed=_p16_pathlib.PurePosixPath(value)
    _p16_need(parsed.is_absolute() and parsed.as_posix()==value and '..' not in parsed.parts and len(parsed.parts)<=40 and '\\' not in value,'bootstrap_path')
    return parsed
def _p16_close(state):
    for fd,*_ in reversed(state['dirs']): _p16_os.close(fd)
    state['dirs']=[]
def _p16_check(state):
    for fd,parent,name,before,path in state['dirs']:
        named=_p16_os.stat(name,follow_symlinks=False,**({} if parent is None else {'dir_fd':parent}))
        _p16_need(not _p16_os.listxattr(fd) and _p16_fp(before)==_p16_fp(_p16_os.fstat(fd))==_p16_fp(named),'bootstrap_changed')
    for parent,name,before in state['files']:
        _p16_need(_p16_fp(before)==_p16_fp(_p16_os.stat(name,dir_fd=parent,follow_symlinks=False)),'bootstrap_changed')
def _p16_directory(state,path,parent,name):
    fd=_p16_os.open(name,_p16_os.O_RDONLY|_p16_os.O_DIRECTORY|_p16_os.O_NOFOLLOW|_p16_os.O_CLOEXEC,**({} if parent is None else {'dir_fd':parent}))
    try:
        meta=_p16_os.fstat(fd);mode=_p16_stat.S_IMODE(meta.st_mode)
        _p16_need(_p16_stat.S_ISDIR(meta.st_mode),'bootstrap_directory')
        if path=='/var/lib/amn2-spain' and meta.st_uid==meta.st_gid==61212:
            _p16_need(mode==0o750,'bootstrap_service_parent')
        elif path=='/run/phase16' or path=='/var/lib/amn2-spain/phase16-maintenance' or path.startswith('/var/lib/amn2-spain/phase16-maintenance/'):
            _p16_need(meta.st_uid==meta.st_gid==0 and mode==0o700,'bootstrap_private_directory')
        else: _p16_need(meta.st_uid==0 and not mode&0o022,'bootstrap_directory_owner')
        _p16_need(not _p16_os.listxattr(fd),'bootstrap_acl')
        named=_p16_os.stat(name,follow_symlinks=False,**({} if parent is None else {'dir_fd':parent}))
        _p16_need(_p16_fp(meta)==_p16_fp(_p16_os.fstat(fd))==_p16_fp(named),'bootstrap_changed')
        state['dirs'].append((fd,parent,name,meta,path));return fd
    except BaseException:
        _p16_os.close(fd);raise
def _p16_chain(path,cache=False):
    parsed=_p16_path(path);base='/var/lib/amn2-spain/phase16-maintenance/'
    if cache: _p16_need(path=='/run/phase16','bootstrap_scope')
    else:
        _p16_need(path.startswith(base) and _p16_re.fullmatch('phase16-[a-z0-9-]{1,80}',path[len(base):].split('/')[0]),'bootstrap_scope')
    state={'dirs':[],'files':[]}
    try:
        current=_p16_directory(state,'/',None,'/');prefix=''
        for name in parsed.parts[1:]:
            prefix+='/'+name;current=_p16_directory(state,prefix,current,name)
        state['root']=current;return state
    except BaseException:
        _p16_close(state);raise
def _p16_read_fd(state,parent,name,maximum):
    fd=_p16_os.open(name,_p16_os.O_RDONLY|_p16_os.O_NOFOLLOW|_p16_os.O_NONBLOCK|_p16_os.O_CLOEXEC,dir_fd=parent)
    try:
        before=_p16_os.fstat(fd)
        _p16_need(_p16_stat.S_ISREG(before.st_mode) and before.st_uid==before.st_gid==0 and before.st_nlink==1 and _p16_stat.S_IMODE(before.st_mode)==0o600,'bootstrap_file')
        _p16_need(not _p16_os.listxattr(fd) and 0<=before.st_size<=maximum,'bootstrap_file')
        raw=bytearray()
        while len(raw)<=before.st_size:
            block=_p16_os.read(fd,min(1048576,before.st_size+1-len(raw)))
            if not block: break
            raw.extend(block)
        named=_p16_os.stat(name,dir_fd=parent,follow_symlinks=False)
        _p16_need(len(raw)==before.st_size and not _p16_os.listxattr(fd) and _p16_fp(before)==_p16_fp(_p16_os.fstat(fd))==_p16_fp(named),'bootstrap_changed')
        state['files'].append((parent,name,before));return bytes(raw)
    finally: _p16_os.close(fd)
def _p16_absent(parent,name):
    try: _p16_os.stat(name,dir_fd=parent,follow_symlinks=False)
    except FileNotFoundError: return
    raise RuntimeError('bootstrap_unbound_path')
def _p16_windows_path(path,directory=False):
    path=_p16_pathlib.Path(path)
    _p16_need(path.is_absolute() and '..' not in path.parts,'bootstrap_path')
    for ancestor in (path,*path.parents):
        meta=ancestor.lstat()
        _p16_need(not _p16_stat.S_ISLNK(meta.st_mode) and not getattr(meta,'st_file_attributes',0)&0x400,'bootstrap_link')
        if ancestor!=path or directory: _p16_need(_p16_stat.S_ISDIR(meta.st_mode),'bootstrap_directory')
    return path
def _p16_read_windows(path,maximum):
    path=_p16_windows_path(path);before=path.lstat()
    _p16_need(_p16_stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=maximum,'bootstrap_file')
    with path.open('rb') as stream:
        _p16_need(_p16_fp(before)==_p16_fp(_p16_os.fstat(stream.fileno())),'bootstrap_changed')
        raw=stream.read(maximum+1)
        _p16_need(len(raw)==before.st_size and _p16_fp(before)==_p16_fp(_p16_os.fstat(stream.fileno()))==_p16_fp(path.lstat()),'bootstrap_changed')
    return raw
def _phase16_read_private(path,maximum,expected_sha256):
    _p16_platform()
    _p16_need(type(maximum) is int and 0<=maximum<=16777216 and isinstance(expected_sha256,str) and _p16_re.fullmatch('[0-9a-f]{64}',expected_sha256),'bootstrap_context')
    if _p16_sys.platform=='linux':
        parsed=_p16_path(path);state=_p16_chain(str(parsed.parent))
        try:
            raw=_p16_read_fd(state,state['root'],parsed.name,maximum);_p16_check(state)
        finally: _p16_close(state)
    else: raw=_p16_read_windows(path,maximum)
    _p16_need(_p16_hashlib.sha256(raw).hexdigest()==expected_sha256,'bootstrap_context_hash')
    return raw

def _phase16_import_root(code,expected_artifacts_sha256_lf,cache_key):
    _p16_platform();expected=expected_artifacts_sha256_lf
    _p16_need(type(expected) is dict and 0<len(expected)<=256 and isinstance(cache_key,str) and _p16_re.fullmatch('[0-9a-f]{64}',cache_key),'bootstrap_manifest')
    _p16_need(not any(n=='scripts' or n.startswith('scripts.') for n in _p16_sys.modules),'bootstrap_already_imported')
    modules={};packages={'scripts'};parents=set()
    for name,digest in expected.items():
        _p16_need(isinstance(name,str) and len(name)<=512 and _p16_re.fullmatch('[A-Za-z0-9_./-]+',name) and all(p not in ('','.','..') for p in name.split('/')) and len(name.split('/'))<=32 and isinstance(digest,str) and _p16_re.fullmatch('[0-9a-f]{64}',digest),'bootstrap_manifest')
        _p16_need(not name.endswith(('.pyc','.pyo')),'bootstrap_manifest')
        parent=name.rpartition('/')[0]
        while parent:
            parents.add(parent);parent=parent.rpartition('/')[0]
        if name.endswith('.py'):
            parts=name[:-3].split('/');is_package=parts[-1]=='__init__'
            if is_package: parts.pop()
            _p16_need(parts and parts[0]=='scripts' and all(p.isidentifier() for p in parts),'bootstrap_module')
            module='.'.join(parts)
            _p16_need(module not in modules,'bootstrap_module');modules[module]=(name,is_package)
            for i in range(1,len(parts)): packages.add('.'.join(parts[:i]))
            if is_package: packages.add(module)
    _p16_need(modules and all(n not in packages or package for n,(_name,package) in modules.items()),'bootstrap_module')
    states=[];bodies={};total=0
    try:
        if _p16_sys.platform=='linux':
            path=_p16_path(code);_p16_need(path.name=='code','bootstrap_code_root')
            state=_p16_chain(code);states.append(state);directories={'':state['root']}
            for parent in sorted(parents,key=lambda v:(v.count('/'),v)):
                prefix,_,leaf=parent.rpartition('/')
                directories[parent]=_p16_directory(state,code+'/'+parent,directories[prefix],leaf)
            for name,digest in sorted(expected.items()):
                parent,_,leaf=name.rpartition('/');raw=_p16_read_fd(state,directories[parent],leaf,2097152)
                total+=len(raw);_p16_need(total<=67108864,'bootstrap_size')
                _p16_need(_p16_hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()==digest,'bootstrap_hash');bodies[name]=raw
            for package in packages:
                parent=package.replace('.','/');_p16_need(parent in directories,'bootstrap_module')
                for leaf in ('__init__.py','__init__.pyc'):
                    if parent+'/'+leaf not in expected: _p16_absent(directories[parent],leaf)
            cache=_p16_chain('/run/phase16',cache=True);states.append(cache)
            _p16_absent(cache['root'],'no-bytecode-'+cache_key)
            alias='/proc/self/fd/'+str(state['root']);cache_path='/proc/self/fd/'+str(cache['root'])+'/no-bytecode-'+cache_key
            for item in states: _p16_check(item)
        else:
            root=_p16_windows_path(code,directory=True);alias=str(root)
            for parent in parents: _p16_windows_path(root/parent,directory=True)
            for name,digest in sorted(expected.items()):
                raw=_p16_read_windows(root/name,2097152);total+=len(raw);_p16_need(total<=67108864,'bootstrap_size')
                _p16_need(_p16_hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()==digest,'bootstrap_hash');bodies[name]=raw
            for package in packages:
                for leaf in ('__init__.py','__init__.pyc'):
                    name=package.replace('.','/')+'/'+leaf;entry=root/name
                    _p16_need(name in expected or (not entry.exists() and not entry.is_symlink()),'bootstrap_unbound_path')
            cache=root/('.phase16-no-bytecode-'+cache_key)
            _p16_need(not cache.exists() and not cache.is_symlink(),'bootstrap_unbound_path');cache_path=str(cache)
        class BoundLoader(_p16_abc.Loader):
            def __init__(self,name): self.name=name
            def create_module(self,spec): return None
            def exec_module(self,module):
                name,_package=modules[self.name];filename=alias+'/'+name
                module.__file__=filename;module.__cached__=None
                exec(compile(bodies[name],filename,'exec',dont_inherit=True),module.__dict__)
            def get_filename(self,fullname): return alias+'/'+modules[fullname][0]
            def get_data(self,path):
                prefix=alias+'/';_p16_need(path.startswith(prefix) and path[len(prefix):] in bodies,'bootstrap_resource')
                return bodies[path[len(prefix):]]
        class BoundFinder(_p16_abc.MetaPathFinder):
            def find_spec(self,fullname,path=None,target=None):
                if fullname!='scripts' and not fullname.startswith('scripts.'):
                    for trusted in (_p16_builtin_finder,_p16_frozen_finder):
                        spec=trusted.find_spec(fullname,path,target)
                        if spec is not None: return spec
                    search=_p16_stdlib_paths if path is None else tuple(path)
                    if path is not None:
                        for entry in search:
                            _p16_need(isinstance(entry,str) and _p16_os.path.isabs(entry),'bootstrap_stdlib_path')
                            resolved=_p16_os.path.normcase(_p16_os.path.realpath(entry));allowed=False
                            for root in _p16_stdlib_roots:
                                try: allowed=allowed or _p16_os.path.commonpath((root,resolved))==root
                                except ValueError: pass
                            _p16_need(allowed,'bootstrap_stdlib_path')
                    spec=_p16_path_finder.find_spec(fullname,search,target)
                    if spec is not None: return spec
                    raise ModuleNotFoundError('unbound non-project module',name=fullname)
                if fullname in modules:
                    name,package=modules[fullname]
                    spec=_p16_util.spec_from_loader(fullname,BoundLoader(fullname),origin=alias+'/'+name,is_package=package)
                    if package: spec.submodule_search_locations=[alias+'/'+name.rpartition('/')[0]]
                    return spec
                if fullname in packages:
                    spec=_p16_machinery.ModuleSpec(fullname,None,is_package=True)
                    spec.submodule_search_locations=[alias+'/'+fullname.replace('.','/')];return spec
                raise ModuleNotFoundError('unbound scripts module',name=fullname)
        finder=BoundFinder();_p16_sys.meta_path.insert(0,finder)
        _p16_sys.dont_write_bytecode=True;_p16_sys.pycache_prefix=cache_path;_p16_sys.path.insert(0,alias)
        _p16_retained.extend(states);return alias
    except BaseException:
        for item in reversed(states): _p16_close(item)
        raise
'''
