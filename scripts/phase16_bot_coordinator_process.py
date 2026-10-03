"""One manager-owned coordinator; local contract, never an implicit live approval.

The supplied, checksum-bound entry module must provide a binding function:
    bind(supervisor) -> {'admission': callable, 'sequence_factory': callable}
Admission accepts the prepared contract and returns its digest only after real
host checks. The factory accepts that admission callable and constructs the
existing MaintenanceSequence. Missing bindings STOP. main() is preview only.

900s manager runtime contains the existing 830s sequence and 70s of wrapper
checks/admission/result writes. Start10 + stop5 + readback15 fits the bounded
930s parent wait. Submission needs 1230s ownership (930+300 reserve); the child
needs 1200s (900+300). Parent timeout cannot cancel this manager-owned service.
No retry, replay, automatic recovery, SSH, config/env dump or service cleanup.
"""
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import stat
import sys

from scripts import phase16_bot_db_rehearsal as db
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_binding as binding
from scripts import phase16_bot_maintenance_jobs as jobs
from scripts import phase16_bot_maintenance_linux as linux
from scripts import phase16_bot_maintenance_sequence as sequence
from scripts.phase16_bot_maintenance_operations import regular
from scripts import phase16_bot_maintenance_storage as storage

require, Stop = core.require, core.Stop
RUNTIME_SECONDS, WAIT_SECONDS = 900, 930
SAFE_REASONS = sequence.SAFE_REASONS | frozenset(('coordinator_already_claimed',
    'coordinator_unknown_no_retry', 'coordinator_not_complete', 'coordinator_worker_already_started',
    'coordinator_sequence_started', 'coordinator_context_changed', 'coordinator_claim_binding',
    'coordinator_result_binding', 'coordinator_start_binding', 'coordinator_sequence_binding',
    'coordinator_properties', 'coordinator_policy', 'coordinator_identity', 'coordinator_cgroup',
    'coordinator_command', 'coordinator_network_namespace', 'coordinator_entry_missing',
    'coordinator_file_owner', 'coordinator_directory_owner', 'coordinator_record_size',
    'coordinator_artifacts', 'coordinator_namespace', 'coordinator_journal', 'coordinator_failed',
    'coordinator_deadline', 'coordinator_result_unverified', 'coordinator_worker_failed'))


def safe_reason(error):
    return (error.args[0] if len(error.args) == 1 and isinstance(error.args[0], str)
            and error.args[0] in SAFE_REASONS else 'coordinator_failed_closed')
# Explicit transitive Python import closure plus the pinned schema sources.
# These imported modules do not authorize calling their remote/recovery helpers.
WORKER_FILES = (
    'scripts/phase10_full_recovery_bundle.py', 'scripts/phase10_recovery_crypto.py',
    'scripts/phase11_recovery_runtime.py', 'scripts/phase13_bot_web_migration_contract.py',
    'scripts/phase13_bot_web_migration_fresh_inputs.py', 'scripts/phase13_bot_web_migration_package.py',
    'scripts/phase16_bot_coordinator_process.py', 'scripts/phase16_bot_db_rehearsal.py',
    'scripts/phase16_bot_linux_gate.py', 'scripts/phase16_bot_maintenance.py',
    'scripts/phase16_bot_maintenance_binding.py', 'scripts/phase16_bot_maintenance_jobs.py',
    'scripts/phase16_bot_maintenance_linux.py', 'scripts/phase16_bot_maintenance_operations.py',
    'scripts/phase16_bot_maintenance_sequence.py', 'scripts/phase16_bot_maintenance_storage.py', 'scripts/phase16_bot_readback_guard_gate.py',
    'scripts/phase16_bot_retained_stage_gate.py', 'scripts/phase16_bot_service_operations.py',
    'scripts/phase16_bot_stage_readback_gate.py', 'scripts/phase16_bot_transport_diagnostics.py',
    'scripts/phase16_legacy_stop_policy.py',
    'scripts/vps/phase13_bot_web_migration_fresh_input_remote.py',
    'scripts/vps/phase13_bot_web_migration_readonly_remote.py',
    'scripts/vps/phase16_bot_integration_readback.py', 'scripts/vps/phase16_bot_linux_gate_remote.py',
    'scripts/vps/phase16_bot_readback_guard_remote.py', 'scripts/vps/phase16_bot_retained_stage_remote.py',
    'scripts/vps/phase16_bot_runtime40_stage_remote.py', 'scripts/vps/phase16_bot_stage_readback_remote.py',
) + tuple('tests/fixtures/phase16_schema/' + name + '.txt' for name in db.SOURCE_HASHES)
FIELDS = ('Id', 'LoadState', 'ActiveState', 'SubState', 'MainPID', 'ExecMainPID', 'Result',
    'ExecMainCode', 'ExecMainStatus', 'InvocationID', 'NRestarts', 'Type', 'Restart',
    'RemainAfterExit', 'PrivateNetwork', 'PrivateTmp', 'ProtectSystem', 'ProtectHome',
    'NoNewPrivileges', 'KillMode', 'RuntimeMaxUSec', 'TimeoutStartUSec', 'TimeoutStopUSec',
    'Slice', 'ControlGroup', 'User', 'Group', 'UMask', 'StandardInput', 'StandardOutput',
    'StandardError', 'ReadWritePaths', 'ReadOnlyPaths', 'ExecMainStartTimestampMonotonic')


def bounded_read(path, maximum=65536, *, private=False):
    if os.name == 'posix' and str(path).startswith(storage.MAINTENANCE_ROOT+'/'):
        return storage.read_owned(path,maximum,private=private)
    path = regular(path)
    metadata = path.stat()
    require(metadata.st_size <= maximum, 'coordinator_record_size')
    if os.name == 'posix':
        require(metadata.st_uid == 0 and not metadata.st_mode & (0o077 if private else 0o022),
                'coordinator_file_owner')
        for parent in path.parents:
            metadata = parent.stat()
            require(metadata.st_uid == 0 and not metadata.st_mode & 0o022, 'coordinator_directory_owner')
    with path.open('rb') as stream:
        raw = stream.read(maximum + 1)
    require(len(raw) <= maximum, 'coordinator_record_size')
    return raw


def artifact_inventory(root, entry_module, extra_files=()):
    require(isinstance(entry_module, str) and re.fullmatch(r'scripts\.[a-z][a-z0-9_]{1,100}', entry_module),
            'coordinator_entry_missing')
    require(isinstance(extra_files, (list, tuple)) and len(extra_files) <= 32, 'coordinator_artifacts')
    for name in extra_files:
        require(isinstance(name, str) and re.fullmatch(r'scripts/(?:[a-z][a-z0-9_]*/)*[a-z][a-z0-9_]*\.py', name),
                'coordinator_artifacts')
    # Namespace package initializer/bytecode must not introduce unbound imports.
    for package in ('scripts', 'scripts/vps'):
        for name in ('__init__.py', '__init__.pyc'):
            require(not (root / package / name).exists(), 'coordinator_namespace')
    names = sorted(set(WORKER_FILES) | {entry_module.replace('.', '/') + '.py'} | set(extra_files))
    return {name: hashlib.sha256(bounded_read(root / name, 2097152).replace(b'\r\n', b'\n')).hexdigest()
            for name in names}


def parse_state(raw):
    require(isinstance(raw, bytes) and len(raw) <= 16384, 'coordinator_properties')
    try:
        result = {}
        for line in raw.decode('ascii').splitlines():
            key, value = line.split('=', 1)
            require(key in FIELDS and key not in result, 'coordinator_properties')
            result[key] = value
        require(set(result) == set(FIELDS), 'coordinator_properties')
        return result
    except (ValueError, UnicodeError):
        raise Stop('coordinator_properties') from None


class CoordinatorSupervisor:
    def __init__(self, data_supervisor, *, entry_module=None, entry_function='bind', extra_files=()):
        require(isinstance(data_supervisor, jobs.DataJobSupervisor), 'coordinator_adapters')
        self.data = data_supervisor
        self.journal, self.client = data_supervisor.journal, data_supervisor.client
        self.code, self.clock = data_supervisor.code, data_supervisor.clock
        self.utc_now, self.sleep = data_supervisor.utc_now, data_supervisor.sleep
        self.entry_module, self.entry_function = entry_module, entry_function
        self.extra_files = tuple(extra_files)
        self.directory = self.journal.directory.parent
        self.unit = self.journal.manifest['operation_id'] + '-coordinator.service'
        self.cgroup = '/system.slice/' + self.unit
        self.paths = {name: self.directory / ('coordinator-' + name + '.json')
                      for name in ('context', 'claim', 'start', 'result', 'complete')}
        self._context = None

    def context(self):
        target = self.data.context()
        require(isinstance(self.entry_function, str) and re.fullmatch('[a-z][a-z0-9_]{0,80}', self.entry_function),
                'coordinator_entry_missing')
        inventory = artifact_inventory(self.client.root / self.code.lstrip('/'), self.entry_module, self.extra_files)
        value = dict(schema='phase16.coordinator-context.v1', binding=self.journal.binding,
            worker_context_sha256=self.data.context_sha256, code=self.code, entry_module=self.entry_module,
            entry_function=self.entry_function, extra_files=list(self.extra_files), artifacts_sha256_lf=inventory)
        if self._context is None:
            self._context = value
        require(value == self._context, 'coordinator_context_changed')
        path = self.paths['context']
        if path.exists() or path.is_symlink():
            require(bounded_read(path, private=True) == core.encoded(value), 'coordinator_context_changed')
        bounded_read(self.directory / 'worker-context.json', private=True)
        return target

    @property
    def context_sha256(self):
        self.context()
        return core.digest(self._context)

    def guard(self, required_seconds):
        target = self.context()
        require(jobs.boot_id(self.client) == self.journal.manifest['boot_id'], 'boot_changed')
        require(binding.timestamp(target['ownership_valid_until']).timestamp() - self.utc_now()
                >= required_seconds + linux.RECOVERY_RESERVE, 'ownership_window')
        return target

    def worker_argv(self):
        target = self.context()
        # Pre-import validation uses stdlib only and a context checksum embedded
        # in the manager argv. Avoid importing a stale .pyc from the saved tree.
        bootstrap = storage.IMPORT_BOOTSTRAP + (
            "\nimport json\n"
            "p=_p16_pathlib.Path(_p16_sys.argv[1])\n"
            "raw=_phase16_read_private(str(p),65536,_p16_sys.argv[2])\n"
            "v=json.loads(raw)\n"
            "_phase16_import_root(v['code'],v['artifacts_sha256_lf'],_p16_sys.argv[2])\n"
            "from scripts.phase16_bot_coordinator_process import worker_entry\n"
            "raise SystemExit(worker_entry(str(p.parent),_p16_sys.argv[2]))\n"
        )
        return ['/usr/bin/python3', '-I', '-S', '-B', '-c', bootstrap,
                target['maintenance_directory'] + '/coordinator-context.json', core.digest(self._context)]

    def command(self):
        target = self.context()
        props = ['Type=exec', 'Restart=no', 'RemainAfterExit=yes', 'User=root', 'Group=root',
            'UMask=0077', 'Slice=system.slice', 'PrivateNetwork=no', 'PrivateTmp=yes',
            'ProtectSystem=strict', 'ProtectHome=yes', 'NoNewPrivileges=yes', 'KillMode=control-group',
            'RuntimeMaxSec=900s', 'TimeoutStartSec=10s', 'TimeoutStopSec=5s',
            'StandardInput=null', 'StandardOutput=null', 'StandardError=null',
            'ReadWritePaths=' + target['maintenance_directory'] + ' /etc/systemd/system /run/phase16',
            'ReadOnlyPaths=' + self.code]
        return ['systemd-run', '--quiet', '--unit=' + self.unit,
                *['--property=' + prop for prop in props], *self.worker_argv()]

    def claim(self):
        value = jobs.load_signed(self.paths['claim'])
        require(value == dict(schema='phase16.coordinator-claim.v1', unit=self.unit,
            binding=self.journal.binding, boot_id=self.journal.manifest['boot_id'],
            context_sha256=self.context_sha256, prepared_event_sha256=self.journal.events[0]['sha256'],
            argv_sha256=core.digest(self.command()), sha256=value['sha256']), 'coordinator_claim_binding')
        return value

    def query(self, seconds=5):
        target = self.context()
        state = parse_state(self.client.run(['systemctl', 'show', '--no-pager',
                            '--property=' + ','.join(FIELDS), self.unit], seconds))
        expected = dict(Id=self.unit, LoadState='loaded', Type='exec', Restart='no', NRestarts='0',
            RemainAfterExit='yes', PrivateNetwork='no', PrivateTmp='yes', ProtectSystem='strict',
            ProtectHome='yes', NoNewPrivileges='yes', KillMode='control-group', RuntimeMaxUSec='15min',
            TimeoutStartUSec='10s', TimeoutStopUSec='5s', Slice='system.slice',
            User='root', Group='root', UMask='0077', StandardInput='null', StandardOutput='null',
            StandardError='null', ReadWritePaths=target['maintenance_directory'] + ' /etc/systemd/system /run/phase16',
            ReadOnlyPaths=self.code)
        require(all(state[k] == v for k, v in expected.items()), 'coordinator_policy')
        exited = state['ActiveState'] == 'active' and state['SubState'] == 'exited' and state['MainPID'] == '0'
        # A manager may release an empty cgroup after exit. readback() still
        # checks the fixed, owned cgroup path; foreign paths never qualify.
        require(state['ControlGroup'] == self.cgroup or (exited and state['ControlGroup'] == ''),
                'coordinator_cgroup')
        require(re.fullmatch('[0-9a-f]{32}', state['InvocationID']) and
            re.fullmatch('[1-9][0-9]{0,9}', state['ExecMainPID']) and
            re.fullmatch('[1-9][0-9]{0,19}', state['ExecMainStartTimestampMonotonic']), 'coordinator_identity')
        return state

    def worker_identity(self, invocation, pid):
        require(re.fullmatch('[0-9a-f]{32}', invocation or '') and type(pid) is int and pid > 0,
                'coordinator_identity')
        state = self.query()
        require(state['InvocationID'] == invocation and state['MainPID'] == state['ExecMainPID'] == str(pid)
                and state['ActiveState'] == 'active' and state['SubState'] == 'running'
                and state['Result'] == 'success', 'coordinator_identity')
        proc = self.client.root / 'proc' / str(pid)
        require(bounded_read(proc / 'cgroup') == ('0::' + self.cgroup + '\n').encode(), 'coordinator_cgroup')
        members = bounded_read(self.client.root / ('sys/fs/cgroup' + self.cgroup) / 'cgroup.procs')
        require(members.split() == [str(pid).encode()], 'coordinator_cgroup')
        require(bounded_read(proc / 'cmdline').split(b'\0') == [s.encode() for s in self.worker_argv()] + [b''],
                'coordinator_command')
        require(os.readlink(proc / 'ns/net') == os.readlink(self.client.root / 'proc/1/ns/net'),
                'coordinator_network_namespace')
        raw = bounded_read(proc / 'stat').decode('ascii')
        parts = raw.rpartition(') ')[2].split()
        require(raw.startswith(str(pid) + ' (') and len(parts) >= 20 and parts[19].isdigit(), 'coordinator_identity')
        return dict(invocation=invocation, pid=pid, process_start_ticks=parts[19],
                    manager_start_usec=state['ExecMainStartTimestampMonotonic'])

    def execute(self):
        try:
            require(not any(p.exists() or p.is_symlink() for p in self.paths.values()), 'coordinator_already_claimed')
            fresh = core.Journal.load(self.journal.directory, self.journal.manifest)
            require(fresh.events == self.journal.events and fresh.phase == 'prepared', 'coordinator_journal')
            require(not any((self.directory / name).exists() for name in ('sequence-claim.json', 'sequence-result.json')),
                    'coordinator_already_claimed')
            self.guard(WAIT_SECONDS)
            argv = self.command()
            core.write_new(self.paths['context'], core.encoded(self._context))
            jobs.write_signed(self.paths['claim'], dict(schema='phase16.coordinator-claim.v1', unit=self.unit,
                binding=self.journal.binding, boot_id=self.journal.manifest['boot_id'],
                context_sha256=self.context_sha256, prepared_event_sha256=self.journal.events[0]['sha256'],
                argv_sha256=core.digest(argv)))
            self.guard(WAIT_SECONDS)
            deadline = self.clock() + WAIT_SECONDS
            self.client.run(argv, 15)
            invocation = None
            while self.clock() < deadline:
                state = self.query(min(5, deadline - self.clock()))
                require(self.clock() < deadline, 'coordinator_unknown_no_retry')
                if invocation is None:
                    invocation = state['InvocationID']
                require(invocation == state['InvocationID'], 'coordinator_identity')
                require(state['ActiveState'] == 'active' and state['Result'] == 'success', 'coordinator_failed')
                if state['SubState'] == 'exited':
                    return self.readback(invocation=invocation, deadline=deadline)
                require(state['SubState'] == 'running' and state['MainPID'] == state['ExecMainPID'], 'coordinator_failed')
                self.guard(max(0, deadline - self.clock()))
                self.sleep(min(1, max(0, deadline - self.clock())))
            raise Stop('coordinator_unknown_no_retry')
        except Stop as error:
            raise Stop(safe_reason(error)) from None
        except Exception:
            raise Stop('coordinator_unknown_no_retry') from None

    def sequence_receipts(self):
        claim = jobs.load_signed(self.directory / 'sequence-claim.json')
        result = jobs.load_signed(self.directory / 'sequence-result.json')
        context = jobs.read_json(self.directory / 'worker-context.json')
        fresh = core.Journal.load(self.journal.directory, self.journal.manifest)
        require(claim == dict(schema='phase16.sequence-claim.v1', binding=self.journal.binding,
            context_sha256=self.data.context_sha256, prepared_sha256=context['prepared']['prepared_sha256'],
            legacy_policy_sha256=context['legacy_stop_policy']['sha256'], sha256=claim['sha256']),
            'coordinator_sequence_binding')
        require(set(result) == {'schema', 'claim_sha256', 'binding', 'final_event_sha256', 'result', 'sha256'}
            and result['schema'] == 'phase16.sequence-result.v1' and result['claim_sha256'] == claim['sha256']
            and result['binding'] == self.journal.binding and result['final_event_sha256'] == fresh.events[-1]['sha256']
            and result['result']['phase'] == fresh.phase and result['result']['automatic_recovery'] == 'DISABLED'
            and result['result']['live_acceptance'] == 'NOT_ESTABLISHED'
            and result['result']['status'] in ('STOP', 'SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE'),
            'coordinator_sequence_binding')
        if result['result']['status'] == 'SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE':
            require(fresh.phase == 'release_done' and result['result']['candidate_start_requested'] is True,
                    'coordinator_sequence_binding')
        return claim, result

    def readback(self, *, invocation=None, deadline=None):
        """One bounded observation of existing evidence, never submission/resume."""
        try:
            limit = self.clock() + 15
            if deadline is not None:
                limit = min(limit, deadline)
            self.guard(0)
            claim = self.claim()
            require(self.clock() < limit, 'coordinator_unknown_no_retry')
            state = self.query(min(5, limit - self.clock()))
            require(self.clock() < limit, 'coordinator_unknown_no_retry')
            require(state['ActiveState'] == 'active' and state['SubState'] == 'exited' and state['MainPID'] == '0'
                and state['Result'] == 'success' and state['ExecMainCode'] == '1' and state['ExecMainStatus'] == '0'
                and (invocation is None or state['InvocationID'] == invocation), 'coordinator_not_complete')
            members = self.client.root / ('sys/fs/cgroup' + self.cgroup) / 'cgroup.procs'
            require(not (members.exists() or members.is_symlink()) or bounded_read(members).strip() == b'', 'coordinator_cgroup')
            started = jobs.load_signed(self.paths['start'])
            seqclaim, seqresult = self.sequence_receipts()
            receipt = jobs.load_signed(self.paths['result'])
            require(started['schema'] == 'phase16.coordinator-start.v1'
                and started['claim_sha256'] == claim['sha256'] and started['context_sha256'] == self.context_sha256
                and started['invocation'] == state['InvocationID'] and str(started['pid']) == state['ExecMainPID']
                and started['manager_start_usec'] == state['ExecMainStartTimestampMonotonic'], 'coordinator_start_binding')
            expected = dict(schema='phase16.coordinator-result.v1', claim_sha256=claim['sha256'],
                start_sha256=started['sha256'], context_sha256=self.context_sha256, binding=self.journal.binding,
                boot_id=self.journal.manifest['boot_id'], invocation=state['InvocationID'],
                sequence_claim_sha256=seqclaim['sha256'], sequence_result_sha256=seqresult['sha256'],
                result=seqresult['result'])
            require(receipt == dict(expected, sha256=receipt['sha256']), 'coordinator_result_binding')
            complete = dict(schema='phase16.coordinator-complete.v1', claim_sha256=claim['sha256'],
                            result_sha256=receipt['sha256'], invocation=state['InvocationID'])
            self.guard(0)
            require(self.clock() < limit, 'coordinator_unknown_no_retry')
            if self.paths['complete'].exists():
                require(jobs.load_signed(self.paths['complete']) == dict(complete, sha256=core.digest(complete)),
                        'coordinator_result_binding')
            else:
                jobs.write_signed(self.paths['complete'], complete)
            require(self.clock() < limit, 'coordinator_unknown_no_retry')
            return receipt['result']
        except Stop as error:
            raise Stop(safe_reason(error)) from None
        except Exception:
            raise Stop('coordinator_result_unverified') from None


def execute_coordinator_worker(supervisor, *, sequence_factory=None, admission=None, invocation, pid):
    """Independent child checks before any supplied host collector/factory runs."""
    try:
        require(callable(sequence_factory) and callable(admission), 'host_admission_missing')
        supervisor.guard(RUNTIME_SECONDS)
        claim = supervisor.claim()
        identity = supervisor.worker_identity(invocation, pid)
        deadline = int(identity['manager_start_usec']) / 1000000 + RUNTIME_SECONDS
        require(supervisor.clock() < deadline, 'coordinator_deadline')
        require(not any(supervisor.paths[n].exists() or supervisor.paths[n].is_symlink()
                        for n in ('start', 'result', 'complete')), 'coordinator_worker_already_started')
        require(not any((supervisor.directory / n).exists() for n in ('sequence-claim.json', 'sequence-result.json')),
                'coordinator_sequence_started')
        # O_EXCL protects worker entry even when it dies before sequence.run().
        jobs.write_signed(supervisor.paths['start'], dict(schema='phase16.coordinator-start.v1',
            claim_sha256=claim['sha256'], context_sha256=supervisor.context_sha256, **identity))
        context = jobs.read_json(supervisor.directory / 'worker-context.json')
        prepared = context['prepared']
        require(admission(json.loads(core.encoded(prepared))) == prepared['prepared_sha256'], 'host_admission_missing')
        supervisor.guard(max(0, deadline - supervisor.clock()))
        require(supervisor.worker_identity(invocation, pid) == identity, 'coordinator_identity')
        runner = sequence_factory(admission)
        require(isinstance(runner, sequence.MaintenanceSequence) and runner.host_guard is admission
            and runner.journal is supervisor.journal and runner.supervisor is supervisor.data
            and runner.total_seconds == 830 and runner.total_seconds < RUNTIME_SECONDS, 'coordinator_sequence_binding')
        supervisor.guard(max(0, deadline - supervisor.clock()))
        require(supervisor.worker_identity(invocation, pid) == identity, 'coordinator_identity')
        require(supervisor.clock() + runner.total_seconds < deadline, 'coordinator_deadline')
        result = runner.run()
        require(supervisor.clock() < deadline, 'coordinator_deadline')
        supervisor.guard(0)
        require(supervisor.worker_identity(invocation, pid) == identity, 'coordinator_identity')
        seqclaim, seqresult = supervisor.sequence_receipts()
        require(result == seqresult['result'], 'coordinator_sequence_binding')
        jobs.write_signed(supervisor.paths['result'], dict(schema='phase16.coordinator-result.v1',
            claim_sha256=claim['sha256'], start_sha256=jobs.load_signed(supervisor.paths['start'])['sha256'],
            context_sha256=supervisor.context_sha256, binding=supervisor.journal.binding,
            boot_id=supervisor.journal.manifest['boot_id'], invocation=invocation,
            sequence_claim_sha256=seqclaim['sha256'], sequence_result_sha256=seqresult['sha256'], result=result))
        return result
    except Stop as error:
        raise Stop(safe_reason(error)) from None
    except Exception:
        raise Stop('coordinator_worker_failed') from None


def worker_entry(directory, expected):
    """Called solely by the rendered, checksum-bound Linux manager bootstrap."""
    try:
        require(sys.platform == 'linux' and os.geteuid() == 0, 'linux_root_required')
        directory = db._check_path(directory)
        raw = bounded_read(directory / 'coordinator-context.json', private=True)
        require(re.fullmatch('[0-9a-f]{64}', expected) and hashlib.sha256(raw).hexdigest() == expected,
                'coordinator_context_changed')
        context = json.loads(raw)
        worker = jobs.read_json(directory / 'worker-context.json')
        target = worker['prepared']['target_contract']
        require(str(directory) == target['maintenance_directory'] and
                Path(__file__).resolve().parents[1] == Path(context['code']), 'coordinator_context_changed')
        journal = core.Journal.load(Path(target['journal']), worker['prepared']['coordinator_manifest'])
        client = linux.SystemdClient(linux.BoundedCommand(maximum=65536))
        fence = core.SystemdFence(Path('/'), journal.manifest, client.control)
        data = jobs.DataJobSupervisor(journal, client, fence, code=context['code'],
                                      context_sha256=context['worker_context_sha256'])
        supervisor = CoordinatorSupervisor(data, entry_module=context['entry_module'],
            entry_function=context['entry_function'], extra_files=context['extra_files'])
        supervisor.guard(RUNTIME_SECONDS)
        require(supervisor.context_sha256 == expected, 'coordinator_context_changed')
        invocation, pid = os.environ.get('INVOCATION_ID', ''), os.getpid()
        supervisor.claim()
        supervisor.worker_identity(invocation, pid)
        binder = getattr(importlib.import_module(context['entry_module']), context['entry_function'])
        bound = binder(supervisor)
        require(isinstance(bound, dict) and set(bound) == {'admission', 'sequence_factory'}, 'host_admission_missing')
        execute_coordinator_worker(supervisor, invocation=invocation, pid=pid, **bound)
        return 0
    except Exception:
        # Evidence is on disk; never log raw exception, process environment or data.
        return 2


def main():
    print(json.dumps(dict(status='LOCAL_COORDINATOR_CONTRACT_ONLY', live_executor_ready=False,
        authorized=False, blockers=['exact_host_admission_binding', 'approved_packet', 'linux_acceptance'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
