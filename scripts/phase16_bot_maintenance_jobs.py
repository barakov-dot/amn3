"""One-shot manager-owned data jobs; not host admission or live authorization.

The caller must already own an approved operation and have established writer
inventory, effective settings and an accepted drain policy. This module proves
only journal/context/job provenance and observed systemd-fence continuity. Root
bypasses and external writers remain the explicit maintenance owner's boundary.
No CLI, SSH, cleanup, retry, service recovery or automatic database restore.
"""
import json
from pathlib import Path
import re
import time

from scripts import phase16_bot_db_rehearsal as db
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_binding as binding
from scripts import phase16_bot_maintenance_linux as linux
from scripts.phase16_bot_maintenance_operations import regular

require, Stop = db.require, db.Stop
ACTIONS = ('backup', 'rehearsal', 'migrate')
JOB_SECONDS = 140  # 120 runtime + startup/stop/readback; never a bot/web timeout.
WITNESS_FIELDS = ('Id', 'Type', 'InvocationID', 'NRestarts', 'StateChangeTimestampMonotonic',
                  'ExecMainExitTimestampMonotonic')
JOB_FIELDS = ('Id', 'LoadState', 'ActiveState', 'SubState', 'MainPID', 'Result',
              'ExecMainCode', 'ExecMainStatus', 'InvocationID', 'NRestarts', 'Type',
              'Restart', 'RemainAfterExit', 'PrivateNetwork', 'ProtectSystem', 'KillMode',
              'RuntimeMaxUSec', 'TimeoutStopUSec', 'ReadWritePaths')


def read_json(path, maximum=16384):
    path = regular(path)
    require(path.stat().st_size <= maximum, 'job_record_size')
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
        require(raw == core.encoded(value), 'job_record_encoding')
        return value
    except (ValueError, UnicodeError):
        raise Stop('job_record_encoding') from None


def load_signed(path):
    value = read_json(path)
    require(isinstance(value, dict) and value.get('sha256') == core.digest(
        {k: v for k, v in value.items() if k != 'sha256'}), 'job_record_binding')
    return value


def write_signed(path, payload):
    core.write_new(path, core.encoded(dict(payload, sha256=core.digest(payload))))


def boot_id(client):
    path = db._check_path(client.root / 'proc/sys/kernel/random/boot_id')
    with path.open('r', encoding='ascii') as stream:
        value = stream.read(65).strip()
    require(re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', value), 'boot_changed')
    return value


def stopped_units(client):
    result = {}
    for unit in linux.UNITS:
        before = client.show(unit)
        client.stopped(unit)
        after = client.show(unit)
        require(before == after, 'stop_witness_changed')
        require(re.fullmatch('[0-9a-f]{32}', after['InvocationID']), 'stop_witness_identity')
        for key in ('NRestarts', 'StateChangeTimestampMonotonic', 'ExecMainExitTimestampMonotonic'):
            require(re.fullmatch('[0-9]{1,20}', after[key]), 'stop_witness_identity')
        require(int(after['ExecMainExitTimestampMonotonic']) > 0, 'stop_witness_identity')
        result[unit] = {key: after[key] for key in WITNESS_FIELDS}
    return result


def save_stop_witness(journal, client, fence):
    fence._intent(journal, 'stop_intent')
    require(boot_id(client) == journal.manifest['boot_id'], 'boot_changed')
    require(client.fence_effective(fence), 'fence_lost')
    units = stopped_units(client)
    require(client.fence_effective(fence), 'fence_lost')
    write_signed(journal.directory.parent / 'stop-witness.json', dict(
        schema='phase16.stop-witness.v1', binding=journal.binding,
        stop_intent_sha256=journal.events[-1]['sha256'], boot_id=journal.manifest['boot_id'],
        units=units, business_drain='NOT_ESTABLISHED', live_authorized=False))


def check_stop_witness(journal, client, fence):
    require(boot_id(client) == journal.manifest['boot_id'], 'boot_changed')
    value = load_signed(journal.directory.parent / 'stop-witness.json')
    expected_keys = {'schema', 'binding', 'stop_intent_sha256', 'boot_id', 'units',
                     'business_drain', 'live_authorized', 'sha256'}
    intent = next((e for e in journal.events if e['phase'] == 'stop_intent'), None)
    require(set(value) == expected_keys and intent is not None
            and value['schema'] == 'phase16.stop-witness.v1' and value['binding'] == journal.binding
            and value['stop_intent_sha256'] == intent['sha256']
            and value['boot_id'] == journal.manifest['boot_id']
            and value['business_drain'] == 'NOT_ESTABLISHED'
            and value['live_authorized'] is False, 'stop_witness_binding')
    require(client.fence_effective(fence), 'fence_lost')
    require(stopped_units(client) == value['units'], 'stop_witness_changed')
    require(client.fence_effective(fence), 'fence_lost')
    return value['sha256']


def unit_name(journal, action):
    require(action in ACTIONS, 'job_action')
    return journal.manifest['operation_id'] + '-' + action + '.service'


def job_paths(journal, action):
    require(action in ACTIONS, 'job_action')
    root = db._check_path(journal.directory.parent / 'jobs')
    return {key: root / (action + '.' + key + '.json') for key in ('claim', 'result', 'complete')}


def validate_claim(journal, action, context_sha256):
    claim = load_signed(job_paths(journal, action)['claim'])
    require(set(claim) == {'schema', 'unit', 'action', 'binding', 'intent_sha256',
                          'context_sha256', 'argv_sha256', 'stop_witness_sha256', 'sha256'}
            and claim['schema'] == 'phase16.job-claim.v1'
            and claim['unit'] == unit_name(journal, action) and claim['action'] == action
            and claim['binding'] == journal.binding and claim['intent_sha256'] == journal.events[-1]['sha256']
            and claim['context_sha256'] == context_sha256, 'job_claim_binding')
    return claim


def save_worker_result(journal, action, *, context_sha256, invocation, boot):
    """Called inside the worker only after its actual DataOperations.verify PASS."""
    require(re.fullmatch('[0-9a-f]{32}', invocation) and boot == journal.manifest['boot_id'], 'job_result_binding')
    require(journal.phase == action + '_intent' and (journal.directory / 'execution.lock').is_file(), 'operation_intent')
    claim = validate_claim(journal, action, context_sha256)
    data = load_signed(journal.directory.parent / 'receipts' / (action + '.json'))
    require(data['binding'] == journal.binding and data['action'] == action
            and data['intent_sha256'] == journal.events[-1]['sha256'], 'job_result_binding')
    write_signed(job_paths(journal, action)['result'], dict(schema='phase16.job-result.v1',
        claim_sha256=claim['sha256'], invocation=invocation, boot_id=boot,
        data_receipt_sha256=data['sha256'], result='DATA_VERIFIED'))


def execute_data_worker(supervisor, action, data, *, invocation, pid):
    """Checks run inside the isolated worker, independently of its parent process."""
    journal = supervisor.journal
    target, witness = supervisor.guard(action, required_seconds=120)
    claim = validate_claim(journal, action, supervisor.context_sha256)
    expected_argv = linux.worker_command(journal.manifest['operation_id'], action, supervisor.code,
                                        target['maintenance_directory'], supervisor.context_sha256)
    require(claim['argv_sha256'] == core.digest(expected_argv)
            and claim['stop_witness_sha256'] == witness, 'job_claim_binding')
    def check_worker():
        state = supervisor.query(action, 5)
        require(state['InvocationID'] == invocation and state['ActiveState'] == 'active'
                and state['SubState'] == 'running' and state['MainPID'] == str(pid)
                and state['Result'] == 'success', 'worker_identity')
    check_worker()
    require(data.journal.binding == journal.binding and data.journal.phase == journal.phase
            and data.directory == journal.directory.parent
            and data.database == supervisor.client.root / target['database'].lstrip('/'), 'worker_data_binding')
    getattr(data, action)()
    require(data.verify(action) is True, 'data_verification')
    check_worker()
    supervisor.guard(action, required_seconds=0)
    save_worker_result(journal, action, context_sha256=supervisor.context_sha256,
                       invocation=invocation, boot=journal.manifest['boot_id'])


class DataJobSupervisor:
    """Runs one concrete worker_command; retains evidence for every ambiguous exit.

    Manager-owned services survive the initiating SSH/process. The caller keeps
    Journal.exclusive while waiting. A crash leaves intent+claim; neither this
    object nor a later invocation resumes/replays an interrupted action.
    """
    def __init__(self, journal, client, fence, *, code, context_sha256,
                 utc_now=time.time, clock=time.monotonic, sleep=time.sleep):
        self.journal, self.client, self.fence = journal, client, fence
        self.code = linux.safe_linux_path(code)
        require(re.fullmatch('[0-9a-f]{64}', context_sha256), 'job_context_binding')
        self.context_sha256 = context_sha256
        self.utc_now, self.clock, self.sleep = utc_now, clock, sleep

    def context(self):
        path = regular(self.journal.directory.parent / 'worker-context.json')
        require(db.file_sha256(path) == self.context_sha256, 'job_context_binding')
        context = read_json(path)
        require(set(context) == {'prepared', 'artifacts_sha256_lf'}, 'job_context_binding')
        prepared = context['prepared']
        # Structural validation at its recorded time only; not a fresh admission.
        # The separate host-admission policy is mandatory before first fence.
        binding.validate_prepared(prepared, now=prepared['target_contract']['observed_at'])
        require(prepared['coordinator_manifest'] == self.journal.manifest, 'job_context_binding')
        target = prepared['target_contract']
        actual = self.client.root / target['maintenance_directory'].lstrip('/')
        require(actual == self.journal.directory.parent, 'job_context_binding')
        return target

    def guard(self, action, *, required_seconds):
        self.fence._intent(self.journal, action + '_intent')
        target = self.context()
        require(binding.timestamp(target['ownership_valid_until']).timestamp() - self.utc_now()
                >= required_seconds + linux.RECOVERY_RESERVE, 'ownership_window')
        witness = check_stop_witness(self.journal, self.client, self.fence)
        return target, witness

    def query(self, action, seconds):
        raw = self.client.run(['systemctl', 'show', '--no-pager',
                              '--property=' + ','.join(JOB_FIELDS), unit_name(self.journal, action)], seconds)
        try:
            value = {}
            for line in raw.decode('utf-8').splitlines():
                key, item = line.split('=', 1)
                require(key in JOB_FIELDS and key not in value, 'job_properties')
                value[key] = item
            require(set(value) == set(JOB_FIELDS), 'job_properties')
        except (ValueError, UnicodeError):
            raise Stop('job_properties') from None
        target = self.context()
        rw = '/var/lib/amn2-spain' if action == 'migrate' else target['maintenance_directory']
        expected = dict(Id=unit_name(self.journal, action), LoadState='loaded', Type='exec',
            Restart='no', NRestarts='0', RemainAfterExit='yes', PrivateNetwork='yes',
            ProtectSystem='strict', KillMode='control-group', RuntimeMaxUSec='2min',
            TimeoutStopUSec='5s', ReadWritePaths=rw)
        require(all(value[k] == v for k, v in expected.items()), 'job_policy')
        require(re.fullmatch('[0-9a-f]{32}', value['InvocationID']), 'job_invocation')
        return value

    def accept_result(self, action, invocation):
        paths = job_paths(self.journal, action)
        claim = validate_claim(self.journal, action, self.context_sha256)
        result = load_signed(paths['result'])
        data = load_signed(self.journal.directory.parent / 'receipts' / (action + '.json'))
        require(set(result) == {'schema', 'claim_sha256', 'invocation', 'boot_id',
                               'data_receipt_sha256', 'result', 'sha256'}
                and result['schema'] == 'phase16.job-result.v1' and result['result'] == 'DATA_VERIFIED'
                and result['claim_sha256'] == claim['sha256'] and result['invocation'] == invocation
                and result['boot_id'] == self.journal.manifest['boot_id']
                and result['data_receipt_sha256'] == data['sha256']
                and data['binding'] == self.journal.binding and data['action'] == action
                and data['intent_sha256'] == self.journal.events[-1]['sha256'], 'job_result_binding')
        write_signed(paths['complete'], dict(schema='phase16.job-complete.v1',
            claim_sha256=claim['sha256'], result_sha256=result['sha256'], invocation=invocation))
        return True

    def execute(self, action):
        require(action in ACTIONS, 'job_action')
        target, witness = self.guard(action, required_seconds=JOB_SECONDS)
        paths = job_paths(self.journal, action)
        require(not any(p.exists() or p.is_symlink() for p in paths.values()), 'job_already_claimed')
        require(not (self.journal.directory.parent / 'receipts' / (action + '.json')).exists(), 'job_result_exists')
        paths['claim'].parent.mkdir(mode=0o700, exist_ok=True)
        argv = linux.worker_command(self.journal.manifest['operation_id'], action, self.code,
                                    target['maintenance_directory'], self.context_sha256)
        write_signed(paths['claim'], dict(schema='phase16.job-claim.v1', unit=unit_name(self.journal, action),
            action=action, binding=self.journal.binding, intent_sha256=self.journal.events[-1]['sha256'],
            context_sha256=self.context_sha256, argv_sha256=core.digest(argv), stop_witness_sha256=witness))
        deadline = self.clock() + JOB_SECONDS
        self.client.run(argv, 15)
        invocation = None
        while self.clock() < deadline:
            state = self.query(action, min(5, deadline - self.clock()))
            require(self.clock() < deadline, 'job_unknown_no_retry')
            if invocation is None:
                invocation = state['InvocationID']
            require(state['InvocationID'] == invocation, 'job_invocation_changed')
            require(state['Result'] == 'success' and state['ActiveState'] == 'active', 'job_failed')
            if state['SubState'] == 'exited':
                require(state['MainPID'] == '0' and state['ExecMainCode'] == '1'
                        and state['ExecMainStatus'] == '0', 'job_failed')
                self.guard(action, required_seconds=0)
                require(self.clock() < deadline, 'job_unknown_no_retry')
                return self.accept_result(action, invocation)
            require(state['SubState'] == 'running' and state['MainPID'].isdigit()
                    and int(state['MainPID']) > 0, 'job_failed')
            self.guard(action, required_seconds=max(0, deadline - self.clock()))
            self.sleep(min(1, max(0, deadline - self.clock())))
        raise Stop('job_unknown_no_retry')
