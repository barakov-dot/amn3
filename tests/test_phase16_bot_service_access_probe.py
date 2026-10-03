"""Service access probe contract with a strict Linux boundary double."""
from dataclasses import asdict, replace
import base64
import copy
import importlib.util
import importlib.machinery
import io
import builtins
import posixpath
import stat
from types import SimpleNamespace
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import zlib
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_linux as linux
from tests import test_phase16_bot_stage_access as fixtures

AVAILABLE = importlib.util.find_spec('scripts.phase16_bot_service_access_probe') is not None
if AVAILABLE:
    from scripts import phase16_bot_service_access_probe as probe


class Availability(unittest.TestCase):
    def test_kernel_access_probe_exists(self):
        self.assertTrue(AVAILABLE, 'service UID/GID mount/net namespace probe missing')


class LinuxSyscalls:
    """Strict Linux syscall model around durable fixture bytes; never a live probe."""
    O_RDONLY, O_PATH, O_DIRECTORY, O_NOFOLLOW, O_CLOEXEC, O_NONBLOCK = 0, 1, 2, 4, 8, 16
    X_OK, R_OK = 1, 4
    path = posixpath

    def __init__(self, fixture, plan):
        self.fixture, self.plan = fixture, plan
        fixture.apply_fixture(plan)
        self.reader = fixture.reader()
        self.fds = {}
        self.next_fd = 100
        self.uid, self.gid, self.groups = 1001, 1001, []
        self.net, self.mount = 'net:[300]', 'mnt:[100]'
        self.supports_effective_ids = {self.access}
        self.deny_dir = self.deny_mmap = False
        self.maps = self.closed_maps = self.finders = 0
        self.opened = []

    def getuid(self): return self.uid
    def geteuid(self): return self.uid
    def getgid(self): return self.gid
    def getegid(self): return self.gid
    def getgroups(self): return self.groups

    def resolve(self, name, dir_fd=None):
        assert isinstance(name, str)
        if not name.startswith('/'):
            assert dir_fd in self.fds
            name = posixpath.join(self.fds[dir_fd][0], name)
        name = posixpath.normpath(name)
        assert name in dict((v[0], v[1]) for v in self.fixture.ancestors) or name == self.plan.stage_root or name.startswith(self.plan.stage_root + '/')
        return name

    def relative(self, name):
        return '.' if name == self.plan.stage_root else name[len(self.plan.stage_root) + 1:]

    def stat(self, name, *, dir_fd=None, follow_symlinks=False):
        assert not follow_symlinks
        name = self.resolve(name, dir_fd)
        ancestors = {v[0]: v[1] for v in self.fixture.ancestors}
        return ancestors[name] if name in ancestors else self.reader.info(self.relative(name))

    def open(self, name, flags, *, dir_fd=None):
        name = self.resolve(name, dir_fd)
        meta = self.stat(name)
        assert flags & self.O_NOFOLLOW and flags & self.O_CLOEXEC
        assert not stat.S_ISLNK(meta.st_mode)
        if flags & self.O_DIRECTORY:
            assert stat.S_ISDIR(meta.st_mode)
        stream = None
        if not flags & self.O_PATH and stat.S_ISREG(meta.st_mode):
            assert flags & self.O_NONBLOCK
            stream = (self.fixture.root / self.relative(name)).open('rb')
        self.next_fd += 1
        self.fds[self.next_fd] = (name, stream)
        self.opened.append(name)
        return self.next_fd

    def dup(self, fd):
        assert self.fds[fd][1] is None
        self.next_fd += 1
        self.fds[self.next_fd] = self.fds[fd]
        return self.next_fd

    def fstat(self, fd): return self.stat(self.fds[fd][0])

    def close(self, fd):
        _, stream = self.fds.pop(fd)
        if stream is not None: stream.close()

    def read(self, fd, size):
        assert 0 <= size <= 1048576
        return self.fds[fd][1].read(size)

    def listdir(self, fd):
        return self.reader.entries(self.relative(self.fds[fd][0]))

    def access(self, name, bits, *, effective_ids):
        assert effective_ids
        meta = self.stat(name)
        if self.deny_dir and name.endswith('/source'):
            return False
        allowed = meta.st_mode >> 3 if meta.st_gid == self.gid else meta.st_mode
        return allowed & bits == bits

    def readlink(self, name, *, dir_fd=None):
        if name == '/proc/self/ns/mnt': return self.mount
        if name == '/proc/self/ns/net': return self.net
        return self.reader.readlink(self.relative(self.resolve(name, dir_fd)))

    def mapping(self, fd, size, *, flags, prot):
        assert self.fds[fd][0].endswith('.so') and self.fds[fd][1] is not None
        assert 0 < size <= 4096 and flags == 2 and prot == 5
        if self.deny_mmap: raise PermissionError('PRIVATE kernel error')
        self.maps += 1
        def close(): self.closed_maps += 1
        return SimpleNamespace(close=close)

    def filefinder(self, path, *loaders):
        assert path == self.plan.stage_root + '/source'
        self.finders += 1
        real = importlib.machinery.FileFinder(str(self.fixture.root / 'source'), *loaders)
        def find_spec(name):
            assert name == 'app'
            spec = real.find_spec(name)
            if spec is not None: spec.origin = path + '/app/__init__.py'
            return spec
        return SimpleNamespace(find_spec=find_spec)

    def execute(self, request):
        output = io.BytesIO()
        fake_sys = SimpleNamespace(platform='linux', version_info=(3, 12),
            argv=['probe', probe.pack_request(request)], executable=self.plan.stage_root + '/runtime-venv/bin/python',
            modules={}, stdout=SimpleNamespace(buffer=output))
        machinery = SimpleNamespace(FileFinder=self.filefinder,
            SourceFileLoader=importlib.machinery.SourceFileLoader, SOURCE_SUFFIXES=importlib.machinery.SOURCE_SUFFIXES)
        modules = {'os': self, 'sys': fake_sys, 'importlib.machinery': SimpleNamespace(machinery=machinery),
            'mmap': SimpleNamespace(MAP_PRIVATE=2, PROT_READ=1, PROT_EXEC=4, mmap=self.mapping)}
        def importing(name, *args, **kwargs):
            return modules[name] if name in modules else builtins.__import__(name, *args, **kwargs)
        def opening(path, mode):
            assert path == '/proc/self/status' and mode == 'rb'
            return io.BytesIO(b'CapInh:\t0000000000000000\nCapPrm:\t0000000000000000\nCapEff:\t0000000000000000\nCapBnd:\t0000000000000000\nCapAmb:\t0000000000000000\nNoNewPrivs:\t1\n')
        builtin = dict(vars(builtins), __import__=importing, open=opening)
        exec(compile(probe.BOOTSTRAP, '<bound-kernel-probe>', 'exec'), {'__builtins__': builtin})
        assert not self.fds, 'bootstrap leaked descriptors'
        return json.loads(output.getvalue())


@unittest.skipUnless(AVAILABLE, 'availability fails first')
class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = f = fixtures.StageAccessTests('test_readonly_verification_distinguishes_plan_from_applied_dac')
        f.setUp()
        self.addCleanup(f.doCleanups)
        f.source['app/native.so'] = b'\x7fELF' + b'kernel-mapping-only'
        f.source_pins['app/native.so'] = (len(f.source['app/native.so']), fixtures.digest(f.source['app/native.so']))
        f.write('source/app/native.so', f.source['app/native.so'])
        self.plan = f.build()
        self.path = f.root / 'approved-plan.json'
        self.path.write_bytes(core.encoded(dict(plan=asdict(self.plan), binding=dict(authorized_plan_sha256=self.plan.digest))))
        self.clock = 0
        self.calls = []
        self.snapshots = 0
        self.loads = 0
        self.state = dict(pid=101, start_ticks=12345, invocation='a' * 32,
            boot_id='11111111-2222-3333-4444-555555555555', mount_ns='mnt:[100]', net_ns='net:[200]', parent_net_ns='net:[200]',
            uid=1001, gid=1001, groups=[1001], caps={'CapInh': 0, 'CapPrm': 0, 'CapEff': 0, 'CapAmb': 0},
            properties={name: '' for name in probe.PROPERTIES})
        self.state['properties'].update(Id=core.BOT, LoadState='loaded', ActiveState='active', SubState='running',
            MainPID='101', InvocationID='a' * 32, ControlGroup='/system.slice/' + core.BOT,
            PrivateUsers='no', DynamicUser='no', NoNewPrivileges='no', PrivateTmp='no', ProtectSystem='no', ProtectHome='no')
        self.mode = 'success'
        self.after_child = lambda: None
        self.observer = self

    def read_plan_record(self, path):
        self.loads += 1
        self.assertEqual(path, self.path)
        return path.read_bytes()

    def snapshot(self, seconds):
        self.assertTrue(0 < seconds <= 5)
        self.snapshots += 1
        return copy.deepcopy(self.state)

    def command(self, argv, seconds):
        self.calls.append(argv)
        self.assertTrue(0 < seconds <= 20)
        self.assertEqual(argv[:10], ['/usr/bin/unshare', '--net', '/usr/bin/nsenter', '--target', '101', '--mount',
            '/usr/bin/setpriv', '--reuid=1001', '--regid=1001', '--clear-groups'])
        for flag in ('--inh-caps=-all', '--ambient-caps=-all', '--bounding-set=-all', '--no-new-privs'):
            self.assertIn(flag, argv)
        self.assertIn(self.plan.stage_root + '/runtime-venv/bin/python', argv)
        self.assertEqual(argv[-5:-2], ['-S', '-B', '-c'])
        self.assertEqual(argv[-2], probe.BOOTSTRAP)
        payload = probe.unpack_request(argv[-1])
        self.assertEqual(payload['plan_sha256'], self.plan.digest)
        self.assertEqual(payload['mount_ns'], 'mnt:[100]')
        self.assertEqual(payload['uid'], 1001)
        self.assertEqual(payload['gid'], 1001)
        self.assertLessEqual(len(base64.b64decode(argv[-1])), 65536)
        paths = {row[0] for row in payload['files']}
        self.assertIn('source/app/main.py', paths)
        self.assertIn('runtime-venv/pyvenv.cfg', paths)
        self.assertFalse(any(p in paths for p in ('claim.json', 'result.json', 'payload', 'scratch')))
        self.assertFalse(any(p.startswith('runtime-venv/bin/') for p in paths))
        if self.mode == 'timeout':
            raise core.Stop('command_deadline')
        result = dict(status='KERNEL_ACCESS_OBSERVED', request_sha256=probe.request_digest(payload),
            plan_sha256=self.plan.digest, nonce=payload['nonce'], uid=1001, gid=1001,
            directories=len(payload['directories']), files=len(payload['files']),
            executable_mappings=sum(row[0].endswith('.so') for row in payload['files']),
            filefinder='APP_SPEC_FOUND_NO_IMPORT', private_network=True, capabilities_cleared=True)
        if self.mode == 'denied':
            result = dict(status='STOP', reason='kernel_access')
        elif self.mode == 'tamper':
            result['nonce'] = 'f' * 32
        elif self.mode == 'overflow':
            return b'x' * 16385
        self.after_child()
        return core.encoded(result)

    def execute(self):
        return probe.probe_service_access(self.plan, authorized_plan_sha256=self.plan.digest,
            plan_record_path=self.path, observer=self.observer, run=self.command, clock=lambda: self.clock)


    def kernel(self):
        request = probe.build_request(self.plan, self.plan.digest, self.state, nonce='d' * 32)
        return LinuxSyscalls(self.fixture, self.plan), request

    def test_linux_bootstrap_reads_real_bytes_finds_app_and_rx_maps_without_import(self):
        kernel, request = self.kernel()
        result = kernel.execute(request)
        self.assertEqual(result['status'], 'KERNEL_ACCESS_OBSERVED', result)
        self.assertEqual(result['request_sha256'], probe.request_digest(request))
        self.assertEqual((kernel.maps, kernel.closed_maps, kernel.finders), (1, 1, 1))
        self.assertNotIn('app', sys.modules)
        self.assertEqual(result['files'], len(request['files']))

    def test_linux_bootstrap_denied_directory_read_or_native_rx_closes_every_fd(self):
        for mode in ('deny_dir', 'deny_mmap'):
            with self.subTest(mode=mode):
                kernel, request = self.kernel()
                setattr(kernel, mode, True)
                result = kernel.execute(request)
                self.assertEqual(result['status'], 'STOP')
                self.assertNotIn('PRIVATE', str(result))
                self.assertEqual(kernel.fds, {})
                self.assertEqual(kernel.finders, 0)

    def test_linux_bootstrap_credentials_and_namespace_fail_before_stage_open(self):
        for field, value in [('uid', 0), ('groups', [1001]), ('mount', 'mnt:[999]'), ('net', 'net:[200]')]:
            with self.subTest(field=field):
                kernel, request = self.kernel()
                setattr(kernel, field, value)
                self.assertEqual(kernel.execute(request)['status'], 'STOP')
                self.assertEqual(kernel.opened, [])

    def test_linux_bootstrap_inode_and_size_drift_are_not_success(self):
        for position in (2, 3):
            with self.subTest(position=position):
                kernel, request = self.kernel()
                request['files'][0][position] += 1
                result = kernel.execute(request)
                self.assertEqual(result['status'], 'STOP')
                self.assertEqual(kernel.fds, {})

    def test_success_binds_plan_identity_and_one_isolated_child(self):
        result = self.execute()
        self.assertEqual(result['status'], 'KERNEL_STAGE_ACCESS_OBSERVED_NOT_HOST_ADMITTED')
        self.assertEqual(result['plan_sha256'], self.plan.digest)
        self.assertEqual(len(self.calls), 1)
        self.assertGreaterEqual(self.snapshots, 2)
        self.assertEqual(self.loads, 2)
        self.assertFalse(result['host_admitted'])
        self.assertEqual(result['content_authentication'], 'PRIOR_APPROVED_PLAN_REQUIRED')

    def test_plan_digest_or_persisted_record_tamper_blocks_child(self):
        self.path.write_bytes(core.encoded(dict(plan=asdict(replace(self.plan, digest='0' * 64)), binding={})))
        with self.assertRaises(probe.ProbeError):
            self.execute()
        self.assertEqual(self.calls, [])

    def test_unknown_user_namespace_root_and_lsm_settings_stop(self):
        for field, value in [('PrivateUsers', 'yes'), ('RootDirectory', '/rootfs'), ('RootImage', '/image'),
            ('AppArmorProfile', 'private-profile'), ('SELinuxContext', 'private-context'),
            ('SmackProcessLabel', 'private-label'), ('DynamicUser', 'yes'), ('SystemCallFilter', '@system-service')]:
            with self.subTest(field=field):
                old = self.state['properties'][field]
                self.state['properties'][field] = value
                with self.assertRaises(probe.ProbeError):
                    self.execute()
                self.state['properties'][field] = old
        self.assertEqual(self.calls, [])

    def test_unknown_properties_are_not_guessed(self):
        del self.state['properties']['PrivateUsers']
        with self.assertRaises(probe.ProbeError):
            self.execute()
        self.assertEqual(self.calls, [])

    def test_uid_gid_supplementary_groups_or_caps_mismatch_blocks_child(self):
        for field, value in [('uid', 1002), ('gid', 1002), ('groups', [0]), ('caps', {'CapEff': 1})]:
            with self.subTest(field=field):
                old = self.state[field]
                self.state[field] = value
                with self.assertRaises(probe.ProbeError):
                    self.execute()
                self.state[field] = old
        self.assertEqual(self.calls, [])

    def test_pid_invocation_mount_namespace_drift_blocks_receipt(self):
        for field, value in [('pid', 202), ('start_ticks', 54321), ('invocation', 'b' * 32), ('mount_ns', 'mnt:[999]')]:
            with self.subTest(field=field):
                initial = copy.deepcopy(self.state)
                self.after_child = lambda k=field, v=value: self.state.__setitem__(k, v)
                with self.assertRaises(probe.ProbeError):
                    self.execute()
                self.state = initial

    def test_plan_changed_during_child_blocks_receipt(self):
        self.after_child = lambda: self.path.write_bytes(b'{"private":"tampered"}\n')
        with self.assertRaises(probe.ProbeError):
            self.execute()
        self.assertEqual(len(self.calls), 1)

    def test_timeout_permission_denial_or_tampered_result_is_not_success(self):
        for mode in ('timeout', 'denied', 'tamper', 'overflow'):
            with self.subTest(mode=mode):
                self.mode = mode
                with self.assertRaises(probe.ProbeError):
                    self.execute()
        self.assertEqual(len(self.calls), 4)

    def test_late_child_cannot_create_success_receipt(self):
        self.after_child = lambda: setattr(self, 'clock', 31)
        with self.assertRaises(probe.ProbeError):
            self.execute()

    def test_private_source_and_bin_wrappers_are_not_probe_inputs(self):
        request = probe.build_request(self.plan, self.plan.digest, self.state, nonce='d' * 32)
        self.assertEqual({v[0] for v in request['links']}, {'runtime-venv/lib64',
            'runtime-venv/bin/python', 'runtime-venv/bin/python3', 'runtime-venv/bin/python3.12'})
        self.assertNotIn('runtime-venv/bin/pip', {v[0] for v in request['files']})
        self.assertEqual(next(v[3] for v in request['directories'] if v[0] == 'source'), 0o750)

    def test_request_decode_rejects_bombs_trailing_data_and_bad_encoding(self):
        inputs = [base64.b64encode(zlib.compress(b'x' * (2097152 + 1))).decode(),
            base64.b64encode(zlib.compress(b'{}') + b'trailing').decode(), 'not base64']
        for value in inputs:
            with self.subTest(length=len(value)), self.assertRaises(probe.ProbeError):
                probe.unpack_request(value)

    def test_real_bounded_bootstrap_on_windows_stops_before_payload_or_files(self):
        if sys.platform == 'linux':
            self.skipTest('Windows platform-stop boundary only')
        raw = linux.BoundedCommand(maximum=4096)([sys.executable, '-I', '-S', '-B', '-c', probe.BOOTSTRAP, 'invalid'], 5)
        self.assertEqual(json.loads(raw), {'status': 'STOP', 'reason': 'platform'})


    def test_native_observer_parses_only_selected_proc_identity_and_unit_fields(self):
        observer = object.__new__(probe.LinuxObserver)
        observed = []
        def command(argv, seconds):
            observed.append(argv)
            return ''.join(k + '=' + v + '\n' for k, v in self.state['properties'].items()).encode()
        observer.run = command
        def read(path, maximum):
            if path.endswith('/stat'):
                return b'101 (bot worker) ' + b' '.join([b'S'] + [b'0'] * 18 + [b'12345'])
            if path.endswith('/status'):
                return b'Uid:\t1001 1001 1001 1001\nGid:\t1001 1001 1001 1001\nGroups:\t1001\n' + b''.join(k.encode() + b':\t0000000000000000\n' for k in probe.CAPS)
            self.assertEqual(path, '/proc/sys/kernel/random/boot_id')
            return (self.state['boot_id'] + '\n').encode()
        observer.read = read
        with patch.object(probe.os, 'readlink', side_effect=lambda p: 'mnt:[100]' if p.endswith('/mnt') else 'net:[200]'):
            self.assertEqual(observer.snapshot(5), self.state)
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0], ['systemctl', 'show', '--no-pager', '--property=' + ','.join(probe.PROPERTIES), core.BOT])

    def test_raw_exception_and_command_output_are_not_exposed(self):
        def private(argv, seconds):
            raise RuntimeError('PRIVATE-TOKEN=secret')
        for error_type in (RuntimeError, probe.ProbeError):
            def private(argv, seconds):
                raise error_type('PRIVATE-TOKEN=secret')
            with self.assertRaises(probe.ProbeError) as result:
                probe.probe_service_access(self.plan, authorized_plan_sha256=self.plan.digest,
                    plan_record_path=self.path, observer=self, run=private)
            self.assertNotIn('PRIVATE', str(result.exception))


if __name__ == '__main__':
    unittest.main()
