"""Linux maintenance primitives; default invocation is an offline blocked preview.

The full host admission/ownership/drain collector and launch packet are NOT yet
assembled. These primitives do not turn T14b JSON into live authorization.
Data workers can only run inside a separately prepared isolated systemd unit.
"""
import argparse
import contextlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import sys
import threading
import time

from scripts import phase16_bot_db_rehearsal as db
from scripts import phase16_bot_maintenance as core

Stop, require = db.Stop, db.require
UNITS = (core.BOT, core.WEB)
PROPERTIES = ('Id', 'LoadState', 'ActiveState', 'SubState', 'Result', 'ExecMainCode',
              'ExecMainStatus', 'MainPID', 'ControlGroup', 'Type', 'NeedDaemonReload',
              'InvocationID', 'NRestarts', 'ActiveEnterTimestampMonotonic',
              'ExecMainExitTimestampMonotonic', 'StateChangeTimestampMonotonic', 'DropInPaths')
ACTION_SECONDS = dict(fence=30, stop=190, backup=120, rehearsal=120, migrate=120,
                      candidate_start=55, web_start=105, release=30)
RECOVERY_RESERVE = 300


class BoundedCommand:
    """No shell, no inherited application environment, EOF input, capped pipes.

    On POSIX the entire owned process group is killed on timeout/overflow. Killing
    a systemctl client does NOT cancel a manager job; SystemdClient deliberately
    uses no-block requests and leaves an ambiguous job fenced for manual review.
    Windows support is only for local direct-child validation, never a live runner.
    """
    def __init__(self, maximum=65536):
        require(type(maximum) is int and 1 <= maximum <= 1048576, 'command_limit')
        self.maximum = maximum

    def __call__(self, argv, seconds):
        require(isinstance(argv, list) and argv and all(isinstance(x, str) and '\x00' not in x for x in argv), 'command_argv')
        require(type(seconds) in (int, float) and 0 < seconds <= 900, 'command_deadline')
        env = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C', 'LANG': 'C'}
        if os.name == 'nt':
            env = {k: os.environ[k] for k in ('SystemRoot', 'WINDIR') if k in os.environ}
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=env, shell=False, close_fds=True,
                                start_new_session=os.name == 'posix')
        buffers = [bytearray(), bytearray()]
        overflow = threading.Event()
        def drain(stream, index):
            try:
                while True:
                    block = stream.read(4096)
                    if not block:
                        break
                    remaining = self.maximum - len(buffers[index])
                    buffers[index].extend(block[:max(0, remaining)])
                    if len(block) > remaining:
                        overflow.set()
            except (OSError, ValueError):
                overflow.set()
        threads = [threading.Thread(target=drain, args=(stream, i), daemon=True)
                   for i, stream in enumerate((proc.stdout, proc.stderr))]
        for thread in threads:
            thread.start()
        deadline = time.monotonic() + seconds
        failure = None
        try:
            while proc.poll() is None or any(t.is_alive() for t in threads):
                if overflow.is_set():
                    failure = 'command_output_limit'
                    break
                if time.monotonic() >= deadline:
                    failure = 'command_deadline'
                    break
                time.sleep(.01)
            if failure:
                if os.name == 'posix':
                    with contextlib.suppress(ProcessLookupError):
                        os.killpg(proc.pid, signal.SIGKILL)
                elif proc.poll() is None:
                    proc.kill()
                proc.wait(timeout=2)
            for thread in threads:
                thread.join(timeout=1)
            require(not any(t.is_alive() for t in threads), 'command_pipe_incomplete')
            require(not overflow.is_set(), 'command_output_limit')
            require(failure is None, failure or 'command_failed')
            require(proc.returncode == 0, 'command_failed')
            require(not buffers[1], 'command_stderr')
            return bytes(buffers[0])
        finally:
            if proc.poll() is None:
                if os.name == 'posix':
                    with contextlib.suppress(ProcessLookupError):
                        os.killpg(proc.pid, signal.SIGKILL)
                else:
                    proc.kill()
                proc.wait(timeout=2)
            # Pipes of a surviving foreign descendant are an incomplete result,
            # never a reason to wait indefinitely in the supervising thread.
            if not any(t.is_alive() for t in threads):
                proc.stdout.close()
                proc.stderr.close()


def parse_properties(raw):
    require(isinstance(raw, bytes) and len(raw) <= 65536, 'unit_output')
    try:
        result = {}
        for line in raw.decode('utf-8', errors='strict').splitlines():
            key, value = line.split('=', 1)
            require(key in PROPERTIES and key not in result, 'unit_properties')
            result[key] = value
        require(set(result) == set(PROPERTIES), 'unit_properties')
        return result
    except (ValueError, UnicodeError):
        raise Stop('unit_properties') from None


class SystemdClient:
    def __init__(self, run, *, root=Path('/'), clock=time.monotonic, sleep=time.sleep):
        self.run, self.root, self.clock, self.sleep = run, Path(root), clock, sleep

    def show(self, unit, seconds=5):
        require(unit in UNITS, 'unit_scope')
        result = parse_properties(self.run(['systemctl', 'show', '--no-pager',
            '--property=' + ','.join(PROPERTIES), unit], seconds))
        require(result['Id'] == unit and result['LoadState'] == 'loaded'
                and result['NeedDaemonReload'] == 'no', 'unit_identity')
        return result

    def bus_property(self, unit, interface, name, signature):
        require(unit in UNITS and interface in ('Unit', 'Service'), 'unit_scope')
        encoded = ''.join(c if c.isascii() and c.isalnum() else '_' + format(ord(c), '02x') for c in unit)
        path = '/org/freedesktop/systemd1/unit/' + encoded
        raw = self.run(['busctl', '--json=short', 'get-property', 'org.freedesktop.systemd1',
                        path, 'org.freedesktop.systemd1.' + interface, name], 5)
        try:
            value = json.loads(raw)
            require(set(value) == {'type', 'data'} and value['type'] == signature, 'bus_property')
            return value['data']
        except (ValueError, TypeError):
            raise Stop('bus_property') from None

    def fence_effective(self, fence):
        observations = {}
        for unit in UNITS:
            value = self.show(unit)
            conditions = self.bus_property(unit, 'Unit', 'Conditions', 'a(sbbsi)')
            require(isinstance(conditions, list) and len(conditions) <= 64, 'unit_conditions')
            for item in conditions:
                require(isinstance(item, list) and len(item) == 5 and type(item[1]) is bool
                        and type(item[2]) is bool and type(item[4]) is int, 'unit_conditions')
            observations[unit] = dict(id=value['Id'], need_daemon_reload=False,
                loaded_dropins=[path.lstrip('/') for path in value['DropInPaths'].split()],
                conditions=[item[:4] for item in conditions])
        return fence.effective(observations)

    def cgroup_empty(self, unit, group):
        require(group in ('', '/system.slice/' + unit), 'cgroup_scope')
        # systemd may clear ControlGroup after exit. Inspect the known path too,
        # and fail on unexpected files/symlinks rather than assume no descendants.
        path = db._check_path(self.root / 'sys/fs/cgroup/system.slice' / unit)
        if not path.exists():
            require(group == '', 'cgroup_missing')
            return True
        require(path.is_dir(), 'cgroup_scope')
        nodes = list(path.rglob('cgroup.procs'))
        require(0 < len(nodes) <= 256, 'cgroup_inventory')
        for node in nodes:
            db._check_path(node)
            require(node.stat().st_size <= 65536, 'cgroup_inventory')
            # procfs/cgroup stat size may be zero: bound the read itself.
            with node.open('rb') as stream:
                raw = stream.read(65537)
            require(len(raw) <= 65536, 'cgroup_inventory')
            if raw.strip():
                return False
        return True

    def stopped(self, unit):
        value = self.show(unit)
        require(value['ActiveState'] == 'inactive' and value['SubState'] == 'dead'
                and value['MainPID'] == '0' and value['Result'] == 'success'
                and value['ExecMainCode'] == '1' and value['ExecMainStatus'] == '0', 'unclean_stop')
        require(self.cgroup_empty(unit, value['ControlGroup']), 'processes_remain')
        # The old 55dc main cancels polling; it does not emit a business drain
        # receipt. Process exit/pending SQL cannot establish handler completion.
        return dict(process_state='QUIESCENT_EXIT_ZERO', business_drain='NOT_ESTABLISHED')

    def control(self, argv, seconds):
        if argv == ['systemctl', 'daemon-reload']:
            return self.run(argv, min(seconds, 15))
        require(len(argv) == 3 and argv[0] == 'systemctl'
                and argv[1] in ('start', 'stop') and argv[2] in UNITS, 'unit_scope')
        action, unit = argv[1:]
        expected = 90 if action == 'stop' or unit == core.WEB else 40
        require(seconds == expected, 'unit_budget')
        before = self.show(unit)
        require(before['ActiveState'] == ('inactive' if action == 'start' else 'active'), 'unit_state')
        deadline = self.clock() + seconds
        self.run(['systemctl', '--no-block', action, unit], 5)
        while self.clock() < deadline:
            value = self.show(unit, min(5, deadline - self.clock()))
            require(self.clock() < deadline, 'manager_job_unknown_no_retry')
            if action == 'stop' and value['ActiveState'] == 'inactive':
                result = self.stopped(unit)
                require(self.clock() < deadline, 'manager_job_unknown_no_retry')
                return result
            if action == 'start' and value['ActiveState'] == 'active':
                require(value['SubState'] == 'running' and value['MainPID'].isdigit()
                        and int(value['MainPID']) > 0 and value['Result'] == 'success'
                        and value['Type'] == ('notify' if unit == core.BOT else 'simple')
                        and re.fullmatch('[0-9a-f]{32}', value['InvocationID'])
                        and value['InvocationID'] != before['InvocationID'], 'startup_identity')
                return value
            require(value['ActiveState'] in ('activating', 'deactivating', before['ActiveState']), 'unit_transition')
            self.sleep(min(.1, max(0, deadline - self.clock())))
        raise Stop('manager_job_unknown_no_retry')


def admission_receipt(records, *, invocation, boot, pid, expected_username):
    if not re.fullmatch('[a-zA-Z0-9_]{5,32}', expected_username):
        return False
    message = ('telegram_persistent_admission=pass bot_identity=@' + expected_username
               + ' webhook_configured=false pending_update_count=0 allowed_updates=message,callback_query')
    matches = [record for record in records if isinstance(record, dict)
               and record.get('_SYSTEMD_UNIT') == core.BOT
               and record.get('_SYSTEMD_INVOCATION_ID') == invocation
               and record.get('_BOOT_ID') == boot and record.get('_PID') == str(pid)
               and record.get('MESSAGE') == message]
    return len(matches) == 1


def safe_linux_path(value):
    require(isinstance(value, str) and re.fullmatch('/[a-zA-Z0-9_./-]+', value)
            and not value.startswith('//') and '..' not in value.split('/') and str(PurePosixPath(value)) == value, 'linux_path')
    return value


def candidate_dropin(target):
    source = safe_linux_path(target['candidate_source'])
    interpreter = safe_linux_path(target['candidate_interpreter'])
    old = safe_linux_path(target['old_source'])
    require(PurePosixPath(old).name == 'app', 'old_source')
    # Keep .env/relative configuration paths at their original working directory.
    # -I excludes old cwd/PYTHONPATH/PYTHONHOME; prepend only the verified candidate.
    # -u makes the source-bound admission receipt visible before READY verification.
    bootstrap = "import runpy,sys; sys.path.insert(0,'" + source + "'); runpy.run_module('app.main',run_name='__main__')"
    return ('[Service]\nWorkingDirectory=' + str(PurePosixPath(old).parent)
            + '\nExecStart=\nExecStart=' + interpreter + ' -I -B -u -c "' + bootstrap + '"\n')


def window_allows(*, remaining, action):
    require(action in ACTION_SECONDS, 'action')
    return type(remaining) in (int, float) and remaining >= ACTION_SECONDS[action] + RECOVERY_RESERVE


def worker_command(operation, action, code, directory, context_sha256):
    require(re.fullmatch('phase16-[a-z0-9-]{1,80}', operation) and action in ('backup', 'rehearsal', 'migrate'), 'worker_scope')
    code, directory = safe_linux_path(code), safe_linux_path(directory)
    require(directory == '/var/lib/amn2-spain/phase16-maintenance/' + operation
            and re.fullmatch('[0-9a-f]{64}', context_sha256), 'worker_binding')
    bootstrap = "import sys;sys.path.insert(0,'" + code + "');from scripts.phase16_bot_maintenance_linux import main;raise SystemExit(main())"
    # A SERVICE (not --scope) belongs to the manager and survives SSH disconnect.
    # RuntimeMaxSec does not limit Type=oneshot, so use Type=exec explicitly.
    properties = ['Type=exec', 'Restart=no', 'RemainAfterExit=yes', 'UMask=0077',
        'PrivateNetwork=yes', 'PrivateTmp=yes', 'ProtectSystem=strict', 'ProtectHome=yes',
        'NoNewPrivileges=yes', 'KillMode=control-group', 'RuntimeMaxSec=120s',
        'TimeoutStartSec=10s', 'TimeoutStopSec=5s', 'MemoryMax=512M', 'LimitFSIZE=268435456',
        'StandardInput=null', 'StandardOutput=null', 'StandardError=null',
        'ReadWritePaths=' + ('/var/lib/amn2-spain' if action == 'migrate' else directory)]
    if action != 'backup':
        properties += ['ReadOnlyPaths=' + directory + '/backup.sqlite3']
    return ['systemd-run', '--quiet', '--unit=' + operation + '-' + action + '.service',
            *['--property=' + prop for prop in properties], '/usr/bin/python3', '-I', '-S', '-B',
            '-c', bootstrap, '--data-worker', action, '--directory', directory,
            '--context-sha256', context_sha256]


def data_worker(action, directory, expected):
    """A separate OS-contained worker, not the forward coordinator/approval gate.

    The coordinator retains execution.lock while it waits for this service. A
    worker receives an existing action intent, never creates one or advances it.
    """
    require(sys.platform == 'linux' and os.geteuid() == 0, 'linux_root_required')
    require(os.readlink('/proc/self/ns/net') != os.readlink('/proc/1/ns/net'), 'network_isolation')
    require(re.fullmatch('[0-9a-f]{32}', os.environ.get('INVOCATION_ID', '')), 'manager_required')
    directory = db._check_path(directory)
    from scripts.phase16_bot_maintenance_operations import regular
    context = regular(directory / 'worker-context.json')
    require(re.fullmatch('[0-9a-f]{64}', expected) and context.stat().st_size <= 16384
            and db.file_sha256(context) == expected, 'worker_binding')
    raw = context.read_bytes()
    value = json.loads(raw)
    require(raw == core.encoded(value) and set(value) == {'prepared', 'artifacts_sha256_lf'}, 'worker_binding')
    from scripts import phase16_bot_maintenance_binding as binding
    prepared = value['prepared']
    # Historical 5-minute observation is checked at initial admission, not
    # dishonestly refreshed during a longer maintenance run. Per-action live
    # provenance and business drain belong to the future coordinator. The worker
    # below rechecks lease, unit identity and fence around each data action.
    binding.validate_prepared(prepared, now=prepared['target_contract']['observed_at'])
    target = prepared['target_contract']
    require(str(directory) == target['maintenance_directory'], 'worker_binding')
    require(binding.timestamp(target['ownership_valid_until']).timestamp() - time.time() >= 120 + RECOVERY_RESERVE,
            'ownership_expired')
    require(Path('/proc/sys/kernel/random/boot_id').read_text().strip() == target['boot_id'], 'boot_changed')
    root = Path(__file__).resolve().parents[1]
    require(value['artifacts_sha256_lf'] == worker_artifacts(root), 'worker_artifacts')
    journal = core.Journal.load(Path(target['journal']), prepared['coordinator_manifest'])
    require(action in ('backup', 'rehearsal', 'migrate'), 'worker_scope')
    from scripts.phase16_bot_maintenance_operations import DataOperations
    data = DataOperations(Path(target['database']), directory, journal,
                          db.Sources(root / 'tests/fixtures/phase16_schema'), target['network_cidr'])
    from scripts.phase16_bot_maintenance_jobs import DataJobSupervisor, execute_data_worker
    client = SystemdClient(BoundedCommand())
    fence = core.SystemdFence(Path('/'), journal.manifest, client.control)
    supervisor = DataJobSupervisor(journal, client, fence, code=str(root), context_sha256=expected)
    execute_data_worker(supervisor, action, data, invocation=os.environ['INVOCATION_ID'], pid=os.getpid())
    return 0


def worker_artifacts(root):
    import hashlib
    files = ['scripts/phase16_bot_maintenance_linux.py', 'scripts/phase16_bot_maintenance_operations.py',
             'scripts/phase16_bot_maintenance.py', 'scripts/phase16_bot_db_rehearsal.py',
             'scripts/phase16_bot_maintenance_binding.py', 'scripts/phase16_bot_maintenance_jobs.py']
    files += ['tests/fixtures/phase16_schema/' + name + '.txt' for name in db.SOURCE_HASHES]
    return {name: hashlib.sha256((Path(root) / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
            for name in files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-worker', choices=('backup', 'rehearsal', 'migrate'))
    parser.add_argument('--directory')
    parser.add_argument('--context-sha256')
    args = parser.parse_args()
    if not args.data_worker:
        print(json.dumps(dict(status='LOCAL_PRIMITIVES_ONLY', live_executor_ready=False,
            authorized=False, blockers=['host_admission_provenance', 'old_runtime_business_drain',
                                        'sustained_coordinator_and_packet_acceptance'])))
        return 0
    try:
        require(args.directory and args.context_sha256, 'worker_arguments')
        return data_worker(args.data_worker, args.directory, args.context_sha256)
    except Exception:
        # The persistent intent is the recovery evidence. No raw errors or data.
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
