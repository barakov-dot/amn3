"""Exact-bound, one-shot future Linux permission application; no CLI.

The caller authenticates approval/target/plan bindings and exclusive maintenance
ownership BEFORE calling execute. This module does not grant live authorization.
Journal files are private, bounded (2 MiB), exclusive-created and fsynced before
stage mutations. Any partial/ambiguous outcome retains intent; no retry, restore,
cleanup, service actions, application imports or console-wrapper execution.
"""
from __future__ import annotations

from contextlib import contextmanager, nullcontext
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import os
from pathlib import PurePosixPath
import re
import stat
import sys
import time

from scripts import phase16_bot_stage_access as access
from scripts.vps.phase16_bot_retained_stage_remote import fingerprint
from scripts.phase16_bot_maintenance_storage import MaintenanceReader

MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_SECONDS = 300


class ApplyError(ValueError):
    """Fixed, non-sensitive stop reason."""


def require(condition, reason):
    if not condition:
        raise ApplyError(reason)


@dataclass(frozen=True)
class ApplyBinding:
    operation_id: str
    target_sha256: str
    boot_id: str
    approval_packet_sha256: str
    authorized_plan_sha256: str


@dataclass(frozen=True)
class ApplyResult:
    """changed_objects counts completed objects only, never proves zero writes.

    A syscall failure/interruption can leave a partial object. Retained intent
    requires manual evidence/recovery even when changed_objects is zero.
    """
    status: str
    reason: str
    changed_objects: int = 0
    host_admitted: bool = False


def encoded(value):
    data = (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode('ascii')
    require(len(data) <= MAX_JSON_BYTES, 'journal_size')
    return data


def journal_name(binding, kind):
    require(kind in ('claim', 'plan', 'intent', 'result'), 'journal_name')
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', binding.operation_id), 'approval_binding')
    return 'stage-access.' + binding.operation_id + '.' + kind + '.json'


def write_all_fsync(fd, data, *, fs=os):
    require(isinstance(data, bytes) and 0 < len(data) <= MAX_JSON_BYTES, 'journal_size')
    offset = 0
    while offset < len(data):
        count = fs.write(fd, data[offset:])
        require(type(count) is int and 0 < count <= len(data) - offset, 'journal_write')
        offset += count
    fs.fsync(fd)


class UnixJournal(MaintenanceReader):
    """Use an existing approved root-private maintenance directory via held FDs.

    The caller must bind this exact directory to target_sha256/approval packet.
    No mkdir, overwrite, symlink following, deletion or 16 KiB JSON helper.
    """
    def __init__(self, directory, *, syscalls=os):
        require(sys.platform == 'linux' and PurePosixPath(directory).is_absolute(), 'journal_platform')
        require(not str(PurePosixPath(directory)).startswith(access.STAGE_ROOT), 'journal_directory')
        super().__init__(directory, syscalls=syscalls)
        self.names = set()

    def __enter__(self):
        try:
            super().__enter__()
            meta = self.os.fstat(self.root_fd)
            require(stat.S_IMODE(meta.st_mode) == 0o700 and meta.st_uid == meta.st_gid == 0, 'journal_directory')
            require(all(not self.os.listxattr(fd) for fd, *_ in self.chain), 'acl_not_clear')
            self.names = set(self.os.listdir(self.root_fd))
            require(len(self.names) <= 4096, 'journal_directory')
            return self
        except BaseException:
            self.close()
            raise

    def create(self, name, data):
        require(re.fullmatch(r'stage-access\.[A-Za-z0-9][A-Za-z0-9_-]{0,79}\.(?:claim|plan|intent|result)\.json', name), 'journal_name')
        require(isinstance(data, bytes) and 0 < len(data) <= MAX_JSON_BYTES, 'journal_size')
        self.check_chain()
        require(set(self.os.listdir(self.root_fd)) == self.names and not self.os.listxattr(self.root_fd), 'journal_changed')
        before = self.os.fstat(self.root_fd)
        fd = self.os.open(name, self.os.O_RDWR | self.os.O_CREAT | self.os.O_EXCL | self.os.O_NOFOLLOW | self.os.O_CLOEXEC,
                          0o600, dir_fd=self.root_fd)
        try:
            meta = self.os.fstat(fd)
            require(stat.S_ISREG(meta.st_mode) and meta.st_uid == meta.st_gid == 0
                    and meta.st_nlink == 1 and stat.S_IMODE(meta.st_mode) == 0o600, 'journal_file')
            write_all_fsync(fd, data, fs=self.os)
            self.os.lseek(fd, 0, 0)
            observed = bytearray()
            while len(observed) <= len(data):
                block = self.os.read(fd, min(1024 * 1024, len(data) + 1 - len(observed)))
                if not block:
                    break
                observed.extend(block)
            require(bytes(observed) == data, 'journal_readback')
            after_file = self.os.fstat(fd)
            named = self.os.stat(name, dir_fd=self.root_fd, follow_symlinks=False)
            require(fingerprint(after_file) == fingerprint(named) and after_file.st_ino == meta.st_ino
                    and after_file.st_dev == meta.st_dev and after_file.st_uid == after_file.st_gid == 0
                    and stat.S_IMODE(after_file.st_mode) == 0o600 and after_file.st_nlink == 1, 'journal_file')
        finally:
            self.os.close(fd)
        after = self.os.fstat(self.root_fd)
        require(all(getattr(before, field) == getattr(after, field) for field in
                    ('st_dev', 'st_ino', 'st_mode', 'st_uid', 'st_gid', 'st_nlink')), 'journal_changed')
        require(set(self.os.listdir(self.root_fd)) == self.names | {name}, 'journal_changed')
        self.names.add(name)
        fd0, parent, leaf, _ = self.chain[-1]
        self.chain[-1] = (fd0, parent, leaf, after)  # only our exclusive entry creation
        self.os.fsync(self.root_fd)
        self.check_chain()


def _validate(plan, binding):
    require(type(plan) is access.AccessPlan and type(binding) is ApplyBinding, 'approval_binding')
    for value in (binding.target_sha256, binding.approval_packet_sha256, binding.authorized_plan_sha256):
        require(isinstance(value, str) and re.fullmatch('[a-f0-9]{64}', value), 'approval_binding')
    require(re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', binding.boot_id), 'approval_binding')
    journal_name(binding, 'claim')
    require(plan.stage_root == access.STAGE_ROOT and plan.schema == 'phase16.stage-access-plan.v1'
            and plan.status == 'ACCESS_PLAN_READY_NOT_APPLIED'
            and plan.digest == binding.authorized_plan_sha256 == access._digest(plan), 'plan_binding')
    access._identity(plan.identity)
    require(0 < len(plan.objects) <= 43000 and len({item.path for item in plan.objects}) == len(plan.objects), 'plan_scope')
    by_path = {item.path: item for item in plan.objects}
    require('.' in by_path and by_path['.'].kind == 'directory' and by_path['.'].before_mode & 0o077 == 0, 'stage_not_private')
    for item in plan.objects:
        if item.path != '.':
            access._path(item.path)
            require(not item.path.startswith('/') and not any(part in ('', '.', '..') for part in item.path.split('/')), 'plan_scope')
            parent = item.path.rpartition('/')[0] or '.'
            require(parent in by_path and by_path[parent].kind == 'directory', 'plan_scope')
        require(item.kind in ('directory', 'file', 'symlink') and item.action in ('set_mode_group', 'preserve_link', 'preserve_private'), 'plan_scope')
        require(type(item.before_mode) is int and type(item.desired_mode) is int and type(item.before_gid) is int
                and type(item.desired_gid) is int and item.before_gid >= 0 and item.desired_gid >= 0, 'plan_scope')
        if item.kind == 'symlink':
            require(item.action == 'preserve_link' and item.before_mode == item.desired_mode
                    and item.before_gid == item.desired_gid and item.path in
                    {'runtime-venv/lib64', *('runtime-venv/bin/' + name for name in access.LINKS)}, 'plan_scope')
        elif item.action == 'preserve_private':
            require(item.path in ('payload', 'scratch', 'claim.json', 'result.json')
                    and item.before_mode == item.desired_mode and item.before_gid == item.desired_gid
                    and not item.desired_mode & 0o077, 'plan_scope')
        else:
            require(item.action == 'set_mode_group' and not item.desired_mode & 0o7022, 'plan_scope')
            if item.path == '.' or item.path in ('runtime-venv', 'runtime-venv/bin', 'runtime-venv/lib', 'runtime-venv/lib/python3.12'):
                require(item.kind == 'directory' and item.desired_mode == 0o710 and item.desired_gid == plan.identity.gid, 'plan_scope')
            elif item.path == 'source' or item.path == 'source/app' or item.path.startswith('source/app/') or item.path == access.runtime.SITE_PREFIX or item.path.startswith(access.runtime.SITE_PREFIX + '/') or item.path == 'runtime-venv/pyvenv.cfg':
                require(item.desired_gid == plan.identity.gid and item.desired_mode == (0o750 if item.kind == 'directory' else 0o640), 'plan_scope')
                require(item.kind != 'file' or (isinstance(item.sha256, str) and re.fullmatch('[a-f0-9]{64}', item.sha256)), 'plan_scope')
            elif item.path.startswith('source/') or item.path == 'runtime-venv/include' or item.path.startswith('runtime-venv/bin/'):
                require(item.desired_gid == 0 and item.desired_mode == (0o700 if item.kind == 'directory' else 0o600), 'plan_scope')
            else:
                raise ApplyError('plan_scope')
        if item.children is not None:
            require(item.kind == 'directory' and len(item.children) == len(set(item.children)), 'plan_scope')
            prefix = '' if item.path == '.' else item.path + '/'
            require({prefix + child for child in item.children} ==
                    {name for name in by_path if name != '.' and (name.rpartition('/')[0] or '.') == item.path}, 'plan_scope')
    require(set(by_path['.'].children or ()) == {'claim.json', 'result.json', 'payload', 'scratch', 'source', 'runtime-venv'}, 'plan_scope')
    require(by_path.get('runtime-venv/lib64') is not None and by_path['runtime-venv/lib64'].link_target == 'lib', 'plan_scope')
    links = {}
    for leaf in access.LINKS:
        item = by_path.get('runtime-venv/bin/' + leaf)
        require(item is not None and item.kind == 'symlink' and item.action == 'preserve_link', 'plan_scope')
        links[leaf] = item.link_target
    for leaf in access.LINKS:
        seen = set()
        current = leaf
        while True:
            require(current not in seen, 'plan_scope')
            seen.add(current)
            target = links[current]
            if target in ('/usr/bin/python3', '/usr/bin/python3.12'):
                break
            require(target in access.LINKS, 'plan_scope')
            current = target
    return encoded({'binding': asdict(binding), 'plan': asdict(plan)})


def _preimage(plan, reader):
    require(access._ancestors(reader, plan.identity) == plan.ancestors, 'preimage_ancestors')
    for item in plan.objects:
        meta = reader.info(item.path)
        access._metadata(meta, link=item.kind == 'symlink')
        access._clear_acl(reader.acl_names(item.path))
        kind = 'symlink' if stat.S_ISLNK(meta.st_mode) else ('directory' if stat.S_ISDIR(meta.st_mode) else 'file')
        require(kind == item.kind and meta.st_dev == item.device and meta.st_ino == item.inode
                and stat.S_IMODE(meta.st_mode) == item.before_mode and meta.st_gid == item.before_gid
                and (item.kind != 'file' or meta.st_size == item.size), 'preimage_identity')
        if item.children is not None:
            require(tuple(sorted(reader.entries(item.path))) == item.children, 'preimage_inventory')
        if item.link_target is not None:
            require(reader.readlink(item.path) == item.link_target, 'preimage_link')
        if item.sha256 is not None:
            data = reader.read_file(item.path, 64 * 1024 * 1024, expected_size=item.size)
            require(len(data) == item.size and hashlib.sha256(data).hexdigest() == item.sha256, 'preimage_content')
    reader.stable()


def _ordered(plan):
    def key(item):
        if item.path == '.':
            return 3, 0, item.path
        if item.desired_gid == 0:
            return 0, item.path.count('/'), item.path
        if item.kind == 'file':
            return 1, 0, item.path
        return 2, -item.path.count('/'), item.path
    return sorted((item for item in plan.objects if item.action == 'set_mode_group'), key=key)


class UnixApplySession(access.UnixStageReader):
    """Mutate only validated no-follow descriptors and rebase exact owned changes."""
    def _named(self, item, parent, leaf):
        if item.path == '.':
            return self.os.stat(str(self.root), follow_symlinks=False)
        return self.os.stat(leaf, dir_fd=parent, follow_symlinks=False)

    def _check_fd(self, fd, item, parent, leaf, expected):
        meta = self.os.fstat(fd)
        access._metadata(meta)
        require(fingerprint(meta) == fingerprint(expected) == fingerprint(self._named(item, parent, leaf)), 'fd_identity')
        require(meta.st_dev == item.device and meta.st_ino == item.inode and not stat.S_ISLNK(meta.st_mode), 'fd_identity')
        access._clear_acl(tuple(self.os.listxattr(fd)))
        if item.sha256 is not None:
            require(meta.st_size == item.size and 0 <= item.size <= 64 * 1024 * 1024, 'fd_content')
            self.os.lseek(fd, 0, 0)
            digest = hashlib.sha256()
            total = 0
            while total <= item.size:
                chunk = self.os.read(fd, min(1024 * 1024, item.size + 1 - total))
                if not chunk:
                    break
                total += len(chunk)
                digest.update(chunk)
            require(total == item.size and digest.hexdigest() == item.sha256, 'fd_content')
            require(fingerprint(self.os.fstat(fd)) == fingerprint(meta), 'fd_identity')
        self.check_chain()
        return meta

    def _rebase(self, item, before, after, mode, gid):
        access._metadata(after)
        require(stat.S_IMODE(after.st_mode) == mode and after.st_gid == gid and after.st_uid == 0, 'metadata_transition')
        require(all(getattr(before, field) == getattr(after, field) for field in
                    ('st_dev', 'st_ino', 'st_uid', 'st_nlink', 'st_size', 'st_mtime_ns'))
                and stat.S_IFMT(before.st_mode) == stat.S_IFMT(after.st_mode), 'metadata_transition')
        # Only this object's mode/group/ctime may change because of our syscalls.
        self.snapshots[item.path] = fingerprint(after)
        if item.path == '.':
            self.chain = [(fd, parent, leaf, after if fd == self.root_fd else snapshot)
                          for fd, parent, leaf, snapshot in self.chain]

    def change(self, item, guard):
        require(item.action == 'set_mode_group' and item.kind in ('file', 'directory'), 'plan_scope')
        before = self.info(item.path)
        require(stat.S_IMODE(before.st_mode) == item.before_mode and before.st_gid == item.before_gid, 'preimage_identity')
        context = nullcontext((None, None)) if item.path == '.' else self.parent_fd(item.path)
        with context as (parent, leaf):
            flags = self.os.O_RDONLY | self.os.O_NOFOLLOW | self.os.O_NONBLOCK | self.os.O_CLOEXEC
            if item.kind == 'directory':
                flags |= self.os.O_DIRECTORY
            fd = self.os.dup(self.root_fd) if item.path == '.' else self.os.open(leaf, flags, dir_fd=parent)
            changed = False
            try:
                self._check_fd(fd, item, parent, leaf, before)
                if before.st_gid != item.desired_gid:
                    guard()
                    self._check_fd(fd, item, parent, leaf, before)
                    self.os.fchown(fd, 0, item.desired_gid)
                    after = self.os.fstat(fd)
                    self._rebase(item, before, after, stat.S_IMODE(before.st_mode), item.desired_gid)
                    before = after
                    changed = True
                if stat.S_IMODE(before.st_mode) != item.desired_mode:
                    guard()
                    self._check_fd(fd, item, parent, leaf, before)
                    self.os.fchmod(fd, item.desired_mode)
                    after = self.os.fstat(fd)
                    self._rebase(item, before, after, item.desired_mode, before.st_gid)
                    before = after
                    changed = True
                self._check_fd(fd, item, parent, leaf, before)
                if changed:
                    self.os.fsync(fd)
                self.check_chain()
                return changed
            finally:
                self.os.close(fd)


def _before_unlock(plan, reader):
    # Validate the intended post-state while the root is still private. Root
    # group may already have been changed by our first syscall; its snapshot
    # was rebased only after checking that exact transition.
    reader.stable()
    root = reader.info('.')
    require(not stat.S_IMODE(root.st_mode) & 0o077, 'stage_not_private')
    root_item = next(item for item in plan.objects if item.path == '.')
    require(root.st_uid == 0 and root.st_gid in (root_item.before_gid, root_item.desired_gid)
            and root.st_dev == root_item.device and root.st_ino == root_item.inode, 'preunlock_failed')
    access._clear_acl(reader.acl_names('.'))
    require(tuple(sorted(reader.entries('.'))) == root_item.children, 'preunlock_failed')
    # Root is intentionally NOT accessible yet. Verify every other final object;
    # its temporary group-only transition must not masquerade as root DAC proof.
    # Full final verify_access, including root, still runs after the last syscall.
    objects = tuple(item for item in plan.objects if item.path != '.')
    intermediate = replace(plan, objects=objects, digest='')
    intermediate = replace(intermediate, digest=access._digest(intermediate))
    result = access.verify_access(intermediate, reader)
    require(result.status == 'DAC_ACCESS_VERIFIED_NOT_HOST_ADMITTED', 'preunlock_failed')


def current_boot_id():
    require(sys.platform == 'linux', 'boot_binding')
    fd = os.open('/proc/sys/kernel/random/boot_id', os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        value = os.read(fd, 65).decode('ascii').strip()
        require(re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', value), 'boot_binding')
        return value
    finally:
        os.close(fd)


def execute(plan, binding, *, journal, session_factory=UnixApplySession, boot_id_reader=current_boot_id) -> ApplyResult:
    """One exact-approved future attempt; failures never authorize another attempt.

    journal is an entered UnixJournal for the approved private maintenance path.
    The caller authenticates operation/target/approval packet digests; this library
    checks consistency and actual boot continuity, not the provenance of consent.
    """
    claimed = False
    changed = 0
    deadline = time.monotonic() + MAX_SECONDS
    def guard():
        require(time.monotonic() < deadline, 'apply_timeout')
        require(boot_id_reader() == binding.boot_id, 'boot_binding')
    try:
        plan_data = _validate(plan, binding)
        guard()
        claim = encoded({'schema': 'phase16.stage-access-claim.v1', 'binding': asdict(binding), 'attempts': 1})
        try:
            journal.create(journal_name(binding, 'claim'), claim)
            claimed = True
        except FileExistsError:
            return ApplyResult('STOP_RETAINED_NO_RETRY', 'claim_exists')
        except Exception:
            return ApplyResult('CLAIM_UNKNOWN_NO_RETRY', 'claim_unpersisted')
        journal.create(journal_name(binding, 'plan'), plan_data)
        with session_factory() as reader:
            _preimage(plan, reader)
            guard()
            journal.create(journal_name(binding, 'intent'), encoded({
                'schema': 'phase16.stage-access-intent.v1', 'binding': asdict(binding),
                'plan_file_sha256': hashlib.sha256(plan_data).hexdigest(),
                'ordered_objects': [item.path for item in _ordered(plan)], 'rollback': 'NO_AUTOMATIC_RESTORE_OR_RETRY'}))
            # Own journal writes are outside the stage. Repeat all stage bytes,
            # ACLs and identities after their fsync, before any permission change.
            _preimage(plan, reader)
            guard()
            for item in _ordered(plan):
                guard()
                def syscall_guard():
                    guard()
                    if item.path == '.':
                        _before_unlock(plan, reader)
                        guard()
                changed += int(reader.change(item, syscall_guard))
            reader.stable()
        guard()
        with session_factory() as fresh_reader:
            result = access.verify_access(plan, fresh_reader)
            require(result.status == 'DAC_ACCESS_VERIFIED_NOT_HOST_ADMITTED', 'postverify_failed')
        guard()
        outcome = ApplyResult('APPLIED_DAC_VERIFIED_NOT_HOST_ADMITTED', 'verified', changed)
    except access.AccessError as error:
        safe = str(error) if str(error) in ('acl_not_clear', 'unsafe_metadata', 'unsafe_path', 'service_identity') else 'access_check'
        outcome = ApplyResult('STOP_RETAINED_NO_RETRY' if claimed else 'STOP_BEFORE_CLAIM', safe, changed)
    except ApplyError as error:
        outcome = ApplyResult('STOP_RETAINED_NO_RETRY' if claimed else 'STOP_BEFORE_CLAIM', str(error), changed)
    except Exception:
        outcome = ApplyResult('STOP_RETAINED_NO_RETRY' if claimed else 'STOP_BEFORE_CLAIM', 'apply_error', changed)
    # BaseException intentionally propagates. Its durable claim/intent remain.
    if claimed:
        try:
            journal.create(journal_name(binding, 'result'), encoded({'binding': asdict(binding), 'result': asdict(outcome)}))
        except Exception:
            return ApplyResult('RESULT_UNPERSISTED_NO_RETRY', 'result_unpersisted', changed)
    return outcome
