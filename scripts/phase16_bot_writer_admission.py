"""Bounded, read-only application writer admission; no live entry point.

An exact, separately accepted owner declaration supplies the complete APPLICATION
writer topology and excludes latent/external/manual application writers during
its bound window. Existing OS services and the root operator are explicitly
trusted, not audited here. A sole-SSH-access answer is insufficient.

The kernel scan observes DB/WAL/SHM/rollback-journal inodes in every visible
process/task FD table and file-backed mapping. PID/task/FD/mapping/cgroup churn,
inaccessible data, unknown actual holders and every incomplete scan STOP. Two
stable snapshots are observations, not proof against unobserved future opens;
the accepted owner declaration supplies that temporal/application boundary.

Default root='/' reads Linux procfs as root. Alternate roots are a filesystem
boundary for offline checks and are labelled NOT_LIVE. No DB content, proc env,
cmdline, file target content, other service inventory, SSH or mutation is read
or executed. The caller must bind this collector and declaration to its future
approved host admission; returned inventory does not authorize maintenance.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_linux as linux

Stop, require = core.Stop, core.require
UNITS = (core.BOT, core.WEB)
TOPOLOGY = [dict(unit=core.BOT, role='bot'), dict(unit=core.WEB, role='web')]
DATABASE = '/var/lib/amn2-spain/amn2.sqlite3'
SUFFIXES = dict(database='', wal='-wal', shm='-shm', rollback_journal='-journal')
UNIT_FIELDS = ('Id', 'LoadState', 'ActiveState', 'SubState', 'MainPID', 'InvocationID', 'ControlGroup')
REASONS = frozenset(('writer_declaration', 'writer_binding', 'writer_window', 'writer_deadline',
    'writer_limit', 'writer_incomplete', 'writer_proc_format', 'writer_maps_format',
    'writer_process_changed', 'writer_unit_changed', 'writer_unit_binding',
    'writer_database_changed', 'writer_database_identity', 'writer_unknown_holder',
    'writer_boot_changed', 'writer_namespace', 'writer_native_root_required'))


@dataclass(frozen=True)
class Limits:
    processes: int = 4096
    tasks: int = 16384
    fds_per_task: int = 4096
    fd_observations: int = 262144
    maps_bytes: int = 1048576
    total_maps_bytes: int = 33554432
    map_observations: int = 262144

    def validate(self):
        maximum = Limits()
        for name, value in vars(self).items():
            require(type(value) is int and 0 < value <= getattr(maximum, name), 'writer_limit')


def timestamp(value):
    require(isinstance(value, str) and len(value) <= 40, 'writer_declaration')
    try:
        parsed = datetime.fromisoformat(value)
        require(parsed.tzinfo is not None and parsed.utcoffset() is not None, 'writer_declaration')
        return parsed.timestamp()
    except (ValueError, OverflowError):
        raise Stop('writer_declaration') from None


def validate_declaration(value, *, operation_id, boot_id, target_binding_sha256,
                         approval_scope_sha256, now):
    fields = {'schema', 'operation_id', 'boot_id', 'target_binding_sha256', 'approval_scope_sha256',
        'declared_at', 'valid_until', 'accepted_within_maintenance_approval', 'application_inventory_complete',
        'writers', 'other_application_writers', 'external_application_pollers', 'trust_boundary', 'scope'}
    require(isinstance(value, dict) and set(value) == fields, 'writer_declaration')
    require(isinstance(operation_id, str) and re.fullmatch('phase16-[a-z0-9-]{1,80}', operation_id)
        and isinstance(boot_id, str) and re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', boot_id),
        'writer_binding')
    require(all(isinstance(v, str) and re.fullmatch('[0-9a-f]{64}', v)
                for v in (target_binding_sha256, approval_scope_sha256)), 'writer_binding')
    require(value['schema'] == 'phase16.application-writer-declaration.v1'
        and value['operation_id'] == operation_id and value['boot_id'] == boot_id
        and value['target_binding_sha256'] == target_binding_sha256
        and value['approval_scope_sha256'] == approval_scope_sha256, 'writer_binding')
    require(value['accepted_within_maintenance_approval'] is True
        and value['application_inventory_complete'] is True and value['writers'] == TOPOLOGY
        and value['other_application_writers'] == dict(cron='absent', agent='absent', timer='absent',
                                                       socket='absent', manual_cli='paused')
        and value['external_application_pollers'] == 'excluded'
        and value['trust_boundary'] == 'EXISTING_OS_AND_ROOT_OPERATOR'
        and value['scope'] == 'APPLICATION_ONLY', 'writer_declaration')
    begin, end = timestamp(value['declared_at']), timestamp(value['valid_until'])
    require(type(now) in (int, float) and begin <= now < end and 0 < end - begin <= 3600, 'writer_window')
    require(len(core.encoded(value)) <= 4096, 'writer_declaration')
    return core.digest(value)


def device_identity(metadata):
    # Linux dev_t layout, also deterministic for injected filesystem fixtures.
    dev = metadata.st_dev
    return ((dev >> 8) & 0xfff | (dev >> 32) & 0xfffff000,
            dev & 0xff | (dev >> 12) & 0xffffff00, metadata.st_ino)


def parse_maps(raw, maximum_lines=262144):
    require(isinstance(raw, bytes) and len(raw) <= 1048576, 'writer_limit')
    result = []
    lines = raw.splitlines()
    require(len(lines) <= maximum_lines, 'writer_limit')
    for line in lines:
        fields = line.split(None, 5)
        require(len(fields) >= 5, 'writer_maps_format')
        address, permissions, offset, device, inode = fields[:5]
        require(re.fullmatch(rb'[0-9a-f]+-[0-9a-f]+', address)
            and re.fullmatch(rb'[r-][w-][x-][ps]', permissions)
            and re.fullmatch(rb'[0-9a-f]{1,16}', offset)
            and re.fullmatch(rb'[0-9a-f]{1,8}:[0-9a-f]{1,8}', device)
            and re.fullmatch(rb'[0-9]{1,20}', inode), 'writer_maps_format')
        start, end = (int(v, 16) for v in address.split(b'-'))
        require(start < end <= 2 ** 64, 'writer_maps_format')
        major, minor = (int(v, 16) for v in device.split(b':'))
        if int(inode):
            # Ignore path text, including private names and '(deleted)'. Match
            # device+inode, retaining file-backed mapping continuity only.
            result.append((start, end, permissions.decode('ascii'), int(offset, 16), major, minor, int(inode)))
    return tuple(result)


class ProcFilesystem:
    """Scoped metadata reader. FD targets are stat'ed, never opened or read."""
    def __init__(self, root, *, tick, limits):
        self.root = Path(root)
        require(self.root.is_absolute(), 'writer_binding')
        self.proc = self.root / 'proc'
        self.database = self.root / DATABASE.lstrip('/')
        self.tick, self.limits = tick, limits
        self.fd_observations = self.maps_bytes = self.map_observations = 0
        self.provenance = 'INJECTED_ROOT_NOT_LIVE'
        if self.root == Path('/'):
            require(sys.platform == 'linux' and os.geteuid() == 0, 'writer_native_root_required')
            require(os.readlink(self.proc / 'self/ns/pid') == os.readlink(self.proc / '1/ns/pid'), 'writer_namespace')
            self.provenance = 'LINUX_PROCFS_ROOT'

    def checked(self, path):
        self.tick()
        path = Path(path)
        require(path.is_absolute() and self.root in (path, *path.parents), 'writer_binding')
        for part in (path, *path.parents):
            metadata = part.lstat()
            require(not stat.S_ISLNK(metadata.st_mode) and not getattr(metadata, 'st_file_attributes', 0) & 0x400,
                    'writer_incomplete')
            if part == self.root:
                break
        self.tick()
        return path

    def read(self, path, maximum):
        path = self.checked(path)
        before = path.stat()
        require(stat.S_ISREG(before.st_mode) and before.st_size <= maximum, 'writer_limit')
        with path.open('rb') as stream:
            opened = os.fstat(stream.fileno())
            require((opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino), 'writer_process_changed')
            raw = stream.read(maximum + 1)
        require(len(raw) <= maximum, 'writer_limit')
        self.tick()
        return raw

    def numeric_directories(self, path, maximum):
        result = []
        with os.scandir(self.checked(path)) as entries:
            for entry in entries:
                self.tick()
                if not entry.name.isdigit():
                    continue
                require(re.fullmatch('[1-9][0-9]{0,9}', entry.name) and entry.is_dir(follow_symlinks=False)
                        and not entry.is_symlink(), 'writer_proc_format')
                result.append(int(entry.name))
                require(len(result) <= maximum, 'writer_limit')
        require(len(result) == len(set(result)), 'writer_process_changed')
        return sorted(result)

    def pids(self):
        result = self.numeric_directories(self.proc, self.limits.processes)
        require(result, 'writer_incomplete')
        return result

    def tids(self, pid):
        result = self.numeric_directories(self.proc / str(pid) / 'task', self.limits.tasks)
        require(pid in result, 'writer_incomplete')
        return result

    def location(self, pid, tid=None):
        require(type(pid) is int and 0 < pid < 2 ** 31
                and (tid is None or type(tid) is int and 0 < tid < 2 ** 31), 'writer_proc_format')
        process = self.proc / str(pid)
        return process if tid is None else process / 'task' / str(tid)

    def process_identity(self, pid, tid=None):
        directory = self.location(pid, tid)
        expected = pid if tid is None else tid
        raw = self.read(directory / 'stat', 8192)
        fields = raw.rpartition(b') ')[2].split()
        require(raw.startswith(str(expected).encode() + b' (') and len(fields) >= 20
                and re.fullmatch(rb'[0-9]{1,20}', fields[19]), 'writer_proc_format')
        cgroup = self.read(directory / 'cgroup', 16384)
        require(cgroup.startswith(b'0::/') and cgroup.endswith(b'\n')
                and cgroup.count(b'\n') == 1 and len(cgroup) <= 4096, 'writer_proc_format')
        group = cgroup[3:-1].decode('ascii')
        require(all(c.isprintable() for c in group) and not any(p in ('.', '..') for p in group.split('/')),
                'writer_proc_format')
        return dict(pid=pid, tid=tid, start_ticks=int(fields[19]), cgroup=group)

    def fd_snapshot(self, pid, tid):
        result = []
        # Keep scandir open while stat'ing. The scanner's own proc FD table can
        # include this directory FD; closing the iterator first creates churn.
        with os.scandir(self.checked(self.location(pid, tid) / 'fd')) as entries:
            for entry in entries:
                self.tick()
                require(re.fullmatch('[0-9]{1,10}', entry.name), 'writer_proc_format')
                self.fd_observations += 1
                require(len(result) < self.limits.fds_per_task
                    and self.fd_observations <= self.limits.fd_observations, 'writer_limit')
                value = os.stat(entry.path)
                result.append((int(entry.name), *device_identity(value), stat.S_IFMT(value.st_mode)))
                self.tick()
        return tuple(sorted(result))

    def maps_snapshot(self, pid, tid):
        raw = self.read(self.location(pid, tid) / 'maps', self.limits.maps_bytes)
        self.maps_bytes += len(raw)
        require(self.maps_bytes <= self.limits.total_maps_bytes, 'writer_limit')
        parsed = parse_maps(raw, self.limits.map_observations)
        self.map_observations += len(parsed)
        require(self.map_observations <= self.limits.map_observations, 'writer_limit')
        self.tick()
        return parsed

    def database_identities(self):
        values = {}
        for kind, suffix in SUFFIXES.items():
            path = Path(str(self.database) + suffix)
            try:
                metadata = self.checked(path).stat()
            except FileNotFoundError:
                require(kind != 'database', 'writer_database_identity')
                values[kind] = None
                continue
            require(stat.S_ISREG(metadata.st_mode) and metadata.st_ino > 0, 'writer_database_identity')
            values[kind] = device_identity(metadata)
        present = [v for v in values.values() if v is not None]
        require(len(set(present)) == len(present), 'writer_database_identity')
        return values

    def boot_id(self):
        raw = self.read(self.proc / 'sys/kernel/random/boot_id', 64)
        require(re.fullmatch(rb'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\n?', raw), 'writer_boot_changed')
        return raw.decode('ascii').strip()


def unit_snapshot(reader, tick, remaining):
    result = {}
    for unit in UNITS:
        tick()
        value = reader(unit, min(5, remaining()))
        tick()
        require(isinstance(value, dict) and all(k in value for k in UNIT_FIELDS), 'writer_unit_binding')
        value = {k: value[k] for k in UNIT_FIELDS}
        require(value['Id'] == unit and value['LoadState'] == 'loaded' and value['ActiveState'] == 'active'
            and value['SubState'] == 'running' and isinstance(value['MainPID'], str)
            and re.fullmatch('[1-9][0-9]{0,9}', value['MainPID'])
            and isinstance(value['InvocationID'], str) and re.fullmatch('[0-9a-f]{32}', value['InvocationID'])
            and value['ControlGroup'] == '/system.slice/' + unit, 'writer_unit_binding')
        result[unit] = value
    require(len({v['MainPID'] for v in result.values()}) == 2, 'writer_unit_binding')
    return result


def collect_writer_admission(declaration, *, operation_id, boot_id, target_binding_sha256,
                             approval_scope_sha256, root=Path('/'), unit_reader=None,
                             utc_now=time.time, clock=time.monotonic, seconds=10, limits=None):
    """Return existing binding.inventory plus its explicit application evidence.

    unit_reader(unit, seconds) must be a bounded read-only show for bot/web only.
    Offline root injection remains labelled NOT_LIVE in hashed evidence. This
    function never accepts arbitrary provided holder lists or scans OS services.
    """
    try:
        require(type(seconds) in (int, float) and 0 < seconds <= 10, 'writer_limit')
        limits = Limits() if limits is None else limits
        require(isinstance(limits, Limits), 'writer_limit')
        limits.validate()
        deadline = clock() + seconds
        def tick():
            require(clock() < deadline, 'writer_deadline')
        def remaining():
            tick()
            return deadline - clock()
        bindings = dict(operation_id=operation_id, boot_id=boot_id,
                        target_binding_sha256=target_binding_sha256, approval_scope_sha256=approval_scope_sha256)
        declared_sha = validate_declaration(declaration, now=utc_now(), **bindings)
        declaration = json.loads(core.encoded(declaration))
        require(core.digest(declaration) == declared_sha, 'writer_declaration')
        require(timestamp(declaration['valid_until']) - utc_now() >= seconds, 'writer_window')
        view = ProcFilesystem(root, tick=tick, limits=limits)
        if unit_reader is None:
            require(view.provenance == 'LINUX_PROCFS_ROOT', 'writer_native_root_required')
            unit_reader = linux.SystemdClient(linux.BoundedCommand()).show
        require(view.boot_id() == boot_id, 'writer_boot_changed')
        units = unit_snapshot(unit_reader, tick, remaining)
        targets = view.database_identities()
        pids = view.pids()
        stable, tasks = {}, {}
        task_count = 0
        holder_pids = {'bot': set(), 'web': set()}
        files_seen = {'bot': set(), 'web': set()}
        snapshots = []
        for pid in pids:
            tick()
            before = view.process_identity(pid)
            tids = view.tids(pid)
            task_count += len(tids)
            require(task_count <= limits.tasks, 'writer_limit')
            thread_identities = {}
            for tid in tids:
                first = view.process_identity(pid, tid)
                fds = view.fd_snapshot(pid, tid)
                maps = view.maps_snapshot(pid, tid)
                require(view.fd_snapshot(pid, tid) == fds and view.maps_snapshot(pid, tid) == maps
                    and view.process_identity(pid, tid) == first, 'writer_process_changed')
                thread_identities[tid] = first
                identities = {item[1:4] for item in fds} | {item[4:7] for item in maps}
                matched = sorted(kind for kind, identity in targets.items() if identity is not None and identity in identities)
                if matched:
                    roles = [role for unit, role in ((core.BOT, 'bot'), (core.WEB, 'web'))
                        if first['cgroup'] == units[unit]['ControlGroup']
                        or first['cgroup'].startswith(units[unit]['ControlGroup'] + '/')]
                    require(len(roles) == 1, 'writer_unknown_holder')
                    holder_pids[roles[0]].add(pid)
                    files_seen[roles[0]].update(matched)
                snapshots.append(core.digest(dict(identity=first, fd_snapshot=fds, file_mappings=maps)))
            require(view.process_identity(pid) == before and view.tids(pid) == tids, 'writer_process_changed')
            stable[pid], tasks[pid] = before, thread_identities
        require(view.pids() == pids, 'writer_process_changed')
        for pid in pids:
            require(view.process_identity(pid) == stable[pid] and view.tids(pid) == sorted(tasks[pid]), 'writer_process_changed')
            for tid, identity in tasks[pid].items():
                require(view.process_identity(pid, tid) == identity, 'writer_process_changed')
        require(view.database_identities() == targets, 'writer_database_changed')
        require(view.boot_id() == boot_id, 'writer_boot_changed')
        require(unit_snapshot(unit_reader, tick, remaining) == units, 'writer_unit_changed')
        known = {}
        for unit in UNITS:
            pid = int(units[unit]['MainPID'])
            require(pid in stable and stable[pid]['cgroup'] == units[unit]['ControlGroup'], 'writer_unit_binding')
            known[unit] = dict(main_pid=pid, invocation=units[unit]['InvocationID'],
                start_ticks=stable[pid]['start_ticks'], cgroup_sha256=core.digest(units[unit]['ControlGroup']))
        require(validate_declaration(declaration, now=utc_now(), **bindings) == declared_sha, 'writer_declaration')
        tick()
        evidence = dict(schema='phase16.application-writer-evidence.v1', basis='OWNER_DECLARATION_AND_KERNEL_HOLDERS',
            scope='APPLICATION_ONLY', trust_boundary='EXISTING_OS_AND_ROOT_OPERATOR_NOT_AUDITED',
            provenance=view.provenance, declaration_sha256=declared_sha, **bindings,
            observed_at=datetime.fromtimestamp(utc_now(), timezone.utc).isoformat(),
            declaration_valid_until=declaration['valid_until'], units=known, database_identities=targets,
            processes_seen=len(pids), tasks_seen=task_count, fd_observations=view.fd_observations,
            map_observations=view.map_observations, holder_processes={role: len(p) for role, p in holder_pids.items()},
            files_seen={role: sorted(files) for role, files in files_seen.items()},
            kernel_snapshot_sha256=core.digest(snapshots), coverage='COMPLETE_VISIBLE_PROC_FD_AND_MAPS',
            future_opens_basis='BOUND_OWNER_DECLARATION', operating_system_audit='NOT_PERFORMED')
        require(len(core.encoded(evidence)) <= 16384, 'writer_limit')
        inventory = dict(writers=json.loads(core.encoded(TOPOLOGY)),
            other_writer_classes=dict.fromkeys(('cron', 'agent', 'socket', 'timer'), 'absent_verified'),
            process_scan='complete_bot_web_only', scan_sha256=core.digest(evidence))
        tick()
        return dict(inventory=inventory, evidence=evidence, authorized=False, live_executor_ready=False)
    except Stop as error:
        reason = error.args[0] if len(error.args) == 1 and isinstance(error.args[0], str) and error.args[0] in REASONS else 'writer_incomplete'
        raise Stop(reason) from None
    except Exception:
        raise Stop('writer_incomplete') from None
