"""Exact, read-only service-group permission planning for the retained stage.

No chmod/chown, subprocess, service start, CLI or implicit execution. A future
exact-approved executor must durably persist this plan/digest, recheck identities
and intent, seal private objects FIRST, and only then grant directory traversal.
This module deliberately supplies no mutation adapter.

The builder repeats runtime-content verification including a separately trusted
bootstrap, verifies an externally authenticated source inventory and pyvenv.cfg,
and refuses unknown ACL/xattr surfaces. Its output is NOT current access proof.
verify_access uses a fresh reader to check the complete intended final state.

Unix DAC proof does not prove service namespace, LSM, mount/noexec, OS interpreter,
unit sandbox, group-discovery provenance or manager-owned process admission.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import json
import os
from pathlib import PurePosixPath
import re
import stat
import sys
import time

from scripts import phase16_bot_runtime_content as runtime
from scripts.vps.phase16_bot_stage_readback_remote import BoundTree
from scripts.vps.phase16_bot_retained_stage_remote import fingerprint

STAGE_ROOT = '/opt/amn2-spain/bot-candidates/phase16-bot-runtime40-20260929-6e68235-001'
ANCESTOR_PATHS = ('/', '/opt', '/opt/amn2-spain', '/opt/amn2-spain/bot-candidates')
LINKS = ('python', 'python3', 'python3.12')
ACTIVATION_FILES = frozenset(('activate', 'activate.csh', 'activate.fish', 'Activate.ps1'))
OUT_OF_SCOPE = ('service_namespace_lsm_mounts', 'os_interpreter_integrity', 'external_interpreter_target_access', 'identity_lookup_provenance',
                'manager_process_admission', 'private_subtree_contents')


class AccessError(ValueError):
    """Fixed, non-sensitive admission reason."""


def _require(condition, reason):
    if not condition:
        raise AccessError(reason)


def _path(value):
    _require(isinstance(value, str) and 0 < len(value) <= 512 and '\\' not in value and ':' not in value
             and all(ord(c) >= 32 and ord(c) != 127 for c in value), 'unsafe_path')
    _require(len(value.split('/')) <= 32 and all(part not in ('', '.', '..') for part in value.split('/')), 'unsafe_path')
    return value


def _clear_acl(names):
    # Empty kernel xattr enumeration is our supported ACL/LSM-xattr subset.
    # None, unsupported enumeration, an ACL, or an unfamiliar xattr all STOP.
    _require(type(names) in (tuple, list) and not names, 'acl_not_clear')


def _identity(identity):
    _require(type(identity.uid) is int and 0 < identity.uid < 2**31
             and type(identity.gid) is int and 0 < identity.gid < 2**31
             and type(identity.supplementary_gids) is tuple
             and all(type(group) is int and group == identity.gid for group in identity.supplementary_gids), 'service_identity')


def _metadata(meta, *, link=False):
    _require(meta.st_uid == 0 and not getattr(meta, 'st_file_attributes', 0) & 0x400, 'unsafe_metadata')
    if link:
        _require(stat.S_ISLNK(meta.st_mode) and meta.st_nlink == 1, 'unsafe_metadata')
    else:
        _require((stat.S_ISREG(meta.st_mode) or stat.S_ISDIR(meta.st_mode))
                 and not meta.st_mode & 0o7022
                 and (not stat.S_ISREG(meta.st_mode) or meta.st_nlink == 1), 'unsafe_metadata')


def _allows(meta, identity, required):
    bits = (meta.st_mode >> 6 if meta.st_uid == identity.uid else
            meta.st_mode >> 3 if meta.st_gid == identity.gid else meta.st_mode)
    return bits & required == required


@dataclass(frozen=True)
class ServiceIdentity:
    uid: int
    gid: int
    supplementary_gids: tuple[int, ...] | None = None


@dataclass(frozen=True)
class AccessObject:
    path: str
    kind: str
    action: str
    device: int
    inode: int
    before_mode: int
    before_gid: int
    size: int
    desired_mode: int
    desired_gid: int
    sha256: str | None = None
    link_target: str | None = None
    children: tuple[str, ...] | None = None


@dataclass(frozen=True)
class Ancestor:
    path: str
    device: int
    inode: int
    mode: int
    gid: int


@dataclass(frozen=True)
class AccessPlan:
    identity: ServiceIdentity
    objects: tuple[AccessObject, ...]
    ancestors: tuple[Ancestor, ...]
    digest: str = ''
    stage_root: str = STAGE_ROOT
    schema: str = 'phase16.stage-access-plan.v1'
    status: str = 'ACCESS_PLAN_READY_NOT_APPLIED'
    ordering: tuple[str, ...] = ('seal_private_source_bin_and_include', 'grant_verified_files', 'grant_verified_directories', 'grant_stage_traverse_last')


@dataclass(frozen=True)
class AccessResult:
    status: str
    reason: str
    checked_objects: int = 0
    out_of_scope: tuple[str, ...] = OUT_OF_SCOPE


class UnixStageReader(BoundTree):
    """Linux descriptor-bound metadata/ACL reader, rooted at the exact stage.

    ACL enumeration never shells out. No xattr values or protected files are
    output. A platform without fd listxattr fails closed. Symlink permission
    bits/ACLs do not grant access on Linux; their exact targets and owners are
    checked, and links are never scheduled for chmod/chown.
    """
    def __init__(self, *, syscalls=os):
        _require(sys.platform == 'linux', 'unix_reader_platform')
        super().__init__(STAGE_ROOT, syscalls=syscalls)

    def info(self, name):
        if name != '.':
            return super().info(name)
        meta = self.os.fstat(self.root_fd)
        before = self.snapshots.setdefault(name, fingerprint(meta))
        _require(before == fingerprint(meta), 'reader_changed')
        self.check_chain()
        return meta

    def entries(self, name):
        if name != '.':
            return super().entries(name)
        self.info('.')
        values = self.os.listdir(self.root_fd)
        _require(len(values) <= 512 and len(values) == len(set(values)), 'stage_inventory')
        for value in values:
            _path(value)
            _require('/' not in value, 'unsafe_path')
        return sorted(values)

    def acl_names(self, name):
        before = self.info(name)
        if stat.S_ISLNK(before.st_mode):
            return ()  # Linux symlink permission checks follow the exact target.
        if name == '.':
            values = self.os.listxattr(self.root_fd)
            _require(fingerprint(before) == fingerprint(self.info('.')), 'reader_changed')
            return tuple(values)
        with self.parent_fd(name) as (parent, leaf):
            fd = self.os.open(leaf, self.os.O_RDONLY | self.os.O_NOFOLLOW | self.os.O_NONBLOCK | self.os.O_CLOEXEC, dir_fd=parent)
            try:
                _require(fingerprint(before) == fingerprint(self.os.fstat(fd)), 'reader_changed')
                values = self.os.listxattr(fd)
                after = self.os.stat(leaf, dir_fd=parent, follow_symlinks=False)
                _require(fingerprint(before) == fingerprint(self.os.fstat(fd)) == fingerprint(after), 'reader_changed')
                return tuple(values)
            finally:
                self.os.close(fd)

    def readlink(self, name):
        before = self.info(name)
        _metadata(before, link=True)
        with self.parent_fd(name) as (parent, leaf):
            result = self.os.readlink(leaf, dir_fd=parent)
        _require(fingerprint(before) == fingerprint(self.info(name)), 'reader_changed')
        return result

    def ancestors(self):
        self.check_chain()
        result = []
        current = PurePosixPath('/')
        for index, (fd, _parent, name, before) in enumerate(self.chain[:-1]):
            if index:
                current = current / name
            meta = self.os.fstat(fd)
            _require(fingerprint(meta) == fingerprint(before), 'reader_changed')
            result.append((str(current), meta, tuple(self.os.listxattr(fd))))
        self.check_chain()
        return tuple(result)


def _ancestors(reader, identity):
    values = reader.ancestors()
    _require(tuple(item[0] for item in values) == ANCESTOR_PATHS, 'ancestor_inventory')
    result = []
    for path, meta, acls in values:
        _metadata(meta)
        _require(stat.S_ISDIR(meta.st_mode), 'ancestor_access')
        _clear_acl(acls)
        _require(_allows(meta, identity, 1), 'ancestor_access')
        result.append(Ancestor(path, meta.st_dev, meta.st_ino, stat.S_IMODE(meta.st_mode), meta.st_gid))
    return tuple(result)


def _pin(data, pin, reason):
    _require(type(pin) in (tuple, list) and len(pin) == 2 and type(pin[0]) is int and pin[0] >= 0
             and isinstance(pin[1], str) and re.fullmatch('[a-f0-9]{64}', pin[1])
             and len(data) == pin[0] and hashlib.sha256(data).hexdigest() == pin[1], reason)


def _digest(plan):
    value = asdict(plan)
    value.pop('digest')
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')).hexdigest()


def _collect_tree(reader, prefix, *, maximum_nodes=40000, maximum_bytes=384 * 1024 * 1024):
    objects = {}
    total = 0
    deadline = time.monotonic() + 60
    def visit(name):
        nonlocal total
        _require(time.monotonic() < deadline, 'access_timeout')
        _path(name)
        _require(len(objects) < maximum_nodes, 'access_limit')
        meta = reader.info(name)
        _metadata(meta)
        _clear_acl(reader.acl_names(name))
        children = None
        if stat.S_ISDIR(meta.st_mode):
            children = tuple(reader.entries(name))
            _require(len(children) <= 1024 and len(children) == len(set(children)), 'access_limit')
            for child in children:
                _path(child)
                _require('/' not in child, 'unsafe_path')
        else:
            total += meta.st_size
            _require(0 <= meta.st_size <= 64 * 1024 * 1024 and total <= maximum_bytes, 'access_limit')
        objects[name] = (meta, children)
        if children is not None:
            for child in children:
                visit(name + '/' + child)
    visit(prefix)
    return objects


def _object(reader, name, *, gid, mode, action='set_mode_group', children=None, content=False, link=None):
    meta = reader.info(name)
    _metadata(meta, link=link is not None)
    _clear_acl(reader.acl_names(name))
    sha = None
    if content:
        data = reader.read_file(name, 64 * 1024 * 1024, expected_size=meta.st_size)
        _require(isinstance(data, bytes) and len(data) == meta.st_size, 'object_content')
        sha = hashlib.sha256(data).hexdigest()
    kind = 'symlink' if link is not None else ('directory' if stat.S_ISDIR(meta.st_mode) else 'file')
    return AccessObject(name, kind, action, meta.st_dev, meta.st_ino, stat.S_IMODE(meta.st_mode), meta.st_gid,
                        meta.st_size, mode, gid, sha, link, tuple(sorted(children)) if children is not None else None)


def build_access_plan(reader, runtime_expected, source_pins, identity, *, pyvenv_pin) -> AccessPlan:
    """Build an immutable object/identity-bound plan; never change permissions.

    source_pins maps the FULL source inventory to trusted (size, SHA256). Only
    app content is granted read; other source files/directories are sealed.
    source itself needs read+traverse for Python FileFinder package discovery.

    pyvenv_pin may come from an authenticated baseline OR from a separate strict
    generated-config semantic validator (trusted OS Python version, exact home,
    isolation, interpreter and original stage creation command), followed by a
    continuity hash. Merely hashing current cfg bytes is not trust. Caller must
    authenticate this provenance, source descriptors and bootstrap wheel pins.
    """
    try:
        _identity(identity)
        ancestors = _ancestors(reader, identity)
        verified = runtime.verify_installed(runtime_expected, reader)
        _require(verified.status == 'PASS_SITE_CONTENT_ONLY' and verified.runtime_status == 'PASS'
                 and verified.bootstrap_status == 'PASS' and verified.scope == 'IMPORT_PATH_CONTENT', 'runtime_not_proven')
        stage_children = tuple(reader.entries('.'))
        _require(set(stage_children) == {'claim.json', 'result.json', 'payload', 'scratch', 'source', 'runtime-venv'}, 'stage_inventory')
        objects = []
        objects.append(_object(reader, '.', gid=identity.gid, mode=0o710, children=stage_children))
        for name in ('claim.json', 'result.json', 'payload', 'scratch'):
            meta = reader.info(name)
            _metadata(meta)
            _require(not stat.S_IMODE(meta.st_mode) & 0o077
                     and (stat.S_ISDIR(meta.st_mode) if name in ('payload', 'scratch') else stat.S_ISREG(meta.st_mode)), 'private_boundary')
            objects.append(_object(reader, name, gid=meta.st_gid, mode=stat.S_IMODE(meta.st_mode), action='preserve_private'))
        _require(isinstance(source_pins, dict) and 0 < len(source_pins) <= 1000
                 and {'app/__init__.py', 'app/main.py'} <= set(source_pins), 'source_inventory')
        source_tree = _collect_tree(reader, 'source', maximum_nodes=2000, maximum_bytes=128 * 1024 * 1024)
        source_files = {name[7:] for name, (meta, _) in source_tree.items() if stat.S_ISREG(meta.st_mode)}
        _require(source_files == set(source_pins), 'source_inventory')
        permitted_dirs = {'source'} | {'source/' + str(parent) for name in source_pins for parent in PurePosixPath(name).parents if str(parent) != '.'}
        _require({name for name, (meta, _) in source_tree.items() if stat.S_ISDIR(meta.st_mode)} == permitted_dirs, 'source_inventory')
        for name, (meta, children) in source_tree.items():
            if children is None:
                relative = _path(name[7:])
                data = reader.read_file(name, 64 * 1024 * 1024, expected_size=meta.st_size)
                _pin(data, source_pins[relative], 'source_content')
            grant = name in ('source', 'source/app') or name.startswith('source/app/')
            mode = (0o750 if children is not None else 0o640) if grant else (0o700 if children is not None else 0o600)
            objects.append(_object(reader, name, gid=identity.gid if grant else 0, mode=mode,
                                   children=children, content=children is None))
        layout = {
            'runtime-venv': {'bin', 'include', 'lib', 'lib64', 'pyvenv.cfg'},
            'runtime-venv/lib': {'python3.12'},
            'runtime-venv/lib/python3.12': {'site-packages'},
        }
        for name, children in layout.items():
            actual = tuple(reader.entries(name))
            _require(set(actual) == children, 'runtime_layout')
            objects.append(_object(reader, name, gid=identity.gid, mode=0o710, children=actual))
        include = reader.info('runtime-venv/include')
        _require(stat.S_ISDIR(include.st_mode), 'runtime_layout')
        objects.append(_object(reader, 'runtime-venv/include', gid=0, mode=0o700))
        _require(reader.readlink('runtime-venv/lib64') == 'lib', 'runtime_layout')
        link_meta = reader.info('runtime-venv/lib64')
        objects.append(_object(reader, 'runtime-venv/lib64', gid=link_meta.st_gid, mode=stat.S_IMODE(link_meta.st_mode),
                               action='preserve_link', link='lib'))
        config = reader.read_file('runtime-venv/pyvenv.cfg', 16384)
        _pin(config, pyvenv_pin, 'pyvenv_binding')
        settings = {}
        for line in config.decode('utf-8').splitlines():
            if line.strip():
                _require('=' in line, 'pyvenv_binding')
                key, value = (part.strip() for part in line.split('=', 1))
                _require(key not in settings, 'pyvenv_binding')
                settings[key] = value
        _require(settings.get('include-system-site-packages') == 'false' and settings.get('home') == '/usr/bin'
                 and re.fullmatch(r'3\.12\.[0-9]+', settings.get('version', ''))
                 and settings.get('executable') in ('/usr/bin/python3', '/usr/bin/python3.12'), 'pyvenv_binding')
        objects.append(_object(reader, 'runtime-venv/pyvenv.cfg', gid=identity.gid, mode=0o640, content=True))
        bin_children = tuple(reader.entries('runtime-venv/bin'))
        wrappers = {name.rsplit('/', 1)[1] for distribution in runtime_expected.distributions for name in distribution.entrypoints}
        _require(set(LINKS) <= set(bin_children) and set(bin_children) <= set(LINKS) | wrappers | ACTIVATION_FILES
                 | {'pip', 'pip3', 'pip3.12'}, 'bin_inventory')
        objects.append(_object(reader, 'runtime-venv/bin', gid=identity.gid, mode=0o710, children=bin_children))
        links = {name: reader.readlink('runtime-venv/bin/' + name) for name in LINKS}
        for origin in LINKS:
            seen = set()
            current = origin
            while True:
                _require(current not in seen, 'interpreter_link')
                seen.add(current)
                target = links[current]
                if target in ('/usr/bin/python3', '/usr/bin/python3.12'):
                    break
                _require(target in LINKS, 'interpreter_link')
                current = target
        for name in bin_children:
            path = 'runtime-venv/bin/' + name
            if name in LINKS:
                meta = reader.info(path)
                objects.append(_object(reader, path, gid=meta.st_gid, mode=stat.S_IMODE(meta.st_mode),
                                       action='preserve_link', link=links[name]))
            else:
                _require(stat.S_ISREG(reader.info(path).st_mode), 'bin_inventory')
                objects.append(_object(reader, path, gid=0, mode=0o600))
        site_tree = _collect_tree(reader, runtime.SITE_PREFIX)
        for name, (meta, children) in site_tree.items():
            objects.append(_object(reader, name, gid=identity.gid, mode=0o750 if children is not None else 0o640,
                                   children=children, content=children is None))
        _require(len(objects) == len({item.path for item in objects}) and len(objects) <= 43000, 'access_limit')
        reader.stable()
        plan = AccessPlan(identity, tuple(sorted(objects, key=lambda item: item.path)), ancestors)
        return replace(plan, digest=_digest(plan))
    except AccessError:
        raise
    except Exception:
        raise AccessError('access_read') from None


def verify_access(plan: AccessPlan, reader) -> AccessResult:
    """Check an applied plan with a NEW reader; no mutation or host admission.

    The caller MUST authenticate plan.digest against the externally approved,
    durable packet. Internal digest consistency alone is not authorization.
    External /usr/bin interpreter target access remains a separate host check.
    """
    checked = 0
    try:
        _require(type(plan) is AccessPlan and plan.digest == _digest(plan) and plan.stage_root == STAGE_ROOT
                 and plan.schema == 'phase16.stage-access-plan.v1', 'plan_binding')
        _identity(plan.identity)
        _require(_ancestors(reader, plan.identity) == plan.ancestors, 'ancestor_changed')
        for item in plan.objects:
            meta = reader.info(item.path)
            _metadata(meta, link=item.kind == 'symlink')
            _clear_acl(reader.acl_names(item.path))
            kind = 'symlink' if stat.S_ISLNK(meta.st_mode) else ('directory' if stat.S_ISDIR(meta.st_mode) else 'file')
            _require(kind == item.kind and meta.st_dev == item.device and meta.st_ino == item.inode, 'object_identity')
            _require(stat.S_IMODE(meta.st_mode) == item.desired_mode and meta.st_gid == item.desired_gid, 'object_permissions')
            if item.children is not None:
                _require(tuple(sorted(reader.entries(item.path))) == item.children, 'object_inventory')
            if item.link_target is not None:
                _require(reader.readlink(item.path) == item.link_target, 'object_link')
            if item.sha256 is not None:
                data = reader.read_file(item.path, 64 * 1024 * 1024, expected_size=item.size)
                _require(len(data) == item.size and hashlib.sha256(data).hexdigest() == item.sha256, 'object_content')
            # Links are checked by their allowed targets; all granted files need
            # read, import directories read+traverse, spine directories traverse.
            if item.desired_gid == plan.identity.gid and item.kind != 'symlink':
                need = 4 if item.kind == 'file' else (5 if item.desired_mode == 0o750 else 1)
                _require(_allows(meta, plan.identity, need), 'object_access')
            checked += 1
        reader.stable()
        return AccessResult('DAC_ACCESS_VERIFIED_NOT_HOST_ADMITTED', 'verified', checked)
    except AccessError as error:
        return AccessResult('NOT_READY', str(error), checked)
    except Exception:
        return AccessResult('NOT_READY', 'access_read', checked)
