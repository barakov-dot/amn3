"""Maintenance building blocks, not a live executor or an authorization source.

Callbacks must be supplied by a separately bound runner. No SSH/subprocess, target
paths, discovery, token/env reads or automatic recovery are performed on import.
An incomplete intent is never replayed. Recovery results are proposals, not GO.
"""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re

from scripts.phase16_bot_db_rehearsal import Stop, require, _check_path

BOT='amn2-spain-bot.service'
WEB='amn2-spain-web.service'
ACTIONS=('fence','stop','backup','rehearsal','migrate','candidate_start','web_start','release')
CANDIDATE='6e682356ed14a62d636ee58039fd3a389e794809'
ARCHIVE='e19abc5c132acae035503267d41d38fdd1e272951b2ebfd0f2a73e2f7c660cb7'


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode('ascii')


def digest(value): return hashlib.sha256(encoded(value)).hexdigest()


def validate_manifest(item):
    fields={'operation_id','boot_id','candidate_commit','source_archive_sha256','runtime_pins',
            'vps_apply_enabled','awg3_bootstrap_enabled','admission_seconds','startup_budget_assessed',
            'inventory_complete','exclusive_maintenance_owner','external_pollers_excluded',
            'manual_cli_paused','writers','other_writer_classes','unit_baseline'}
    require(isinstance(item,dict) and set(item)==fields, 'manifest_fields')
    require(isinstance(item['operation_id'],str) and re.fullmatch(r'phase16-[a-z0-9-]{1,80}',item['operation_id']), 'operation_id')
    require(isinstance(item['boot_id'],str) and re.fullmatch(r'[a-z0-9-]{1,64}',item['boot_id']), 'boot_id')
    require(item['candidate_commit']==CANDIDATE and item['source_archive_sha256']==ARCHIVE, 'candidate_binding')
    require(type(item['runtime_pins']) is int and item['runtime_pins']==40, 'runtime_binding')
    require(item['vps_apply_enabled'] is False and item['awg3_bootstrap_enabled'] is False, 'startup_flags')
    require(type(item['admission_seconds']) is int and 1<=item['admission_seconds']<40, 'admission_budget')
    for field in ('startup_budget_assessed','inventory_complete','exclusive_maintenance_owner',
                  'external_pollers_excluded','manual_cli_paused'):
        require(item[field] is True, 'inventory_or_budget_unknown')
    require(item['writers']==[{'unit':BOT,'role':'bot'},{'unit':WEB,'role':'web'}], 'writer_scope')
    require(isinstance(item['unit_baseline'],dict) and set(item['unit_baseline'])=={BOT,WEB}, 'unit_baseline')
    for unit, start, restart in ((BOT,40,'no'),(WEB,90,'on-failure')):
        baseline=item['unit_baseline'][unit]
        require(set(baseline)=={'active','enabled','masked','start_seconds','stop_seconds','restart'}, 'unit_baseline')
        require(baseline['active']=='active' and baseline['masked'] is False and
                baseline['enabled'] in ('enabled','enabled-runtime','disabled','static','indirect') and
                type(baseline['start_seconds']) is int and baseline['start_seconds']==start and
                type(baseline['stop_seconds']) is int and baseline['stop_seconds']==90 and
                baseline['restart']==restart, 'unit_baseline')
    # This first implementation accepts only the proved two-writer inventory.
    # Any additional writer needs a concrete adapter/manifest extension, not a bool.
    require(item['other_writer_classes']==dict.fromkeys(('cron','agent','socket','timer'),'absent_verified'), 'other_writers')


def sync_directory(path):
    if os.name=='posix':
        fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)


def write_new(path, data, mode=0o600):
    path=_check_path(path)
    try: fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
    except FileExistsError: raise Stop('owned_path_exists') from None
    with os.fdopen(fd,'wb') as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())
    sync_directory(path.parent)


class Journal:
    @classmethod
    def create(cls, directory, manifest):
        validate_manifest(manifest)
        path=_check_path(directory)
        require(not path.exists(), 'journal_exists')
        path.mkdir(mode=0o700)
        sync_directory(path.parent)
        obj=cls();obj.directory=path;obj.binding=digest(manifest);obj.events=[];obj.manifest=manifest
        write_new(path/'manifest.json',encoded(manifest))
        obj._append('prepared')
        return obj

    @classmethod
    def load(cls, directory, manifest):
        validate_manifest(manifest)
        obj=cls();obj.directory=_check_path(directory);obj.binding=digest(manifest);obj.events=[];obj.manifest=manifest
        try:
            require((obj.directory/'manifest.json').stat().st_size<8192,'manifest_size')
            require((obj.directory/'manifest.json').read_bytes()==encoded(manifest),'manifest_binding')
            require(not (obj.directory/'manifest.json').is_symlink(),'manifest_binding')
            files=sorted(p for p in obj.directory.iterdir() if p.name not in ('manifest.json','execution.lock','recovery'))
            require(0<len(files)<=1+2*len(ACTIONS), 'journal_shape')
            previous='0'*64
            for number,path in enumerate(files):
                require(path.name==f'{number:03d}.json' and not path.is_symlink(), 'journal_shape')
                require(path.stat().st_size<2048,'journal_shape')
                event=json.loads(path.read_text(encoding='ascii'))
                require(set(event)=={'sequence','binding','previous','phase','sha256'},'journal_shape')
                payload={k:v for k,v in event.items() if k!='sha256'}
                require(event['sequence']==number and event['binding']==obj.binding and
                        event['previous']==previous and digest(payload)==event['sha256'], 'journal_binding')
                require(event['phase']==cls._phase_at(number), 'journal_order')
                previous=event['sha256'];obj.events.append(event)
        except (OSError,ValueError,TypeError,KeyError): raise Stop('journal_unreadable') from None
        return obj

    @staticmethod
    def _phase_at(number):
        if number==0:return 'prepared'
        action=ACTIONS[(number-1)//2]
        return action+('_intent' if number%2 else '_done')

    @property
    def phase(self): return self.events[-1]['phase']

    @property
    def candidate_requested(self):
        return any(e['phase']=='candidate_start_intent' for e in self.events)

    def _append(self, phase):
        number=len(self.events)
        require(phase==self._phase_at(number),'transition')
        payload=dict(sequence=number,binding=self.binding,
                     previous=self.events[-1]['sha256'] if self.events else '0'*64,phase=phase)
        event=dict(payload,sha256=digest(payload))
        # O_EXCL is also the stale-writer guard. A torn record stays STOP on reload.
        write_new(self.directory/f'{number:03d}.json',encoded(event))
        self.events.append(event)

    @contextlib.contextmanager
    def exclusive(self):
        path=self.directory/'execution.lock'
        marker=os.urandom(16).hex().encode('ascii')
        write_new(path,marker)
        try:
            fresh=Journal.load(self.directory,self.manifest)
            require(fresh.events==self.events,'stale_journal')
            require(not (self.directory/'recovery').exists(),'recovery_started')
            yield
        finally:
            require(not path.is_symlink() and path.read_bytes()==marker,'lock_ownership')
            path.unlink();sync_directory(path.parent)

    def perform(self, action, operation, verify):
        with self.exclusive():
            require(action in ACTIONS,'transition')
            require(self.phase==('prepared' if action=='fence' else ACTIONS[ACTIONS.index(action)-1]+'_done'), 'transition')
            self._append(action+'_intent')
            try:
                operation()
                require(verify() is True, 'verification_failed')
            except Stop: raise
            except Exception: raise Stop('action_failed') from None
            self._append(action+'_done')


def recovery_route(journal, *, fence_continuous, drain_proven, backup_verified, same_boot):
    if journal.candidate_requested: return 'PRESERVE_DB_MANUAL_RECOVERY'
    if (journal.directory/'recovery').exists():return 'HOLD_FENCE_MANUAL_RECOVERY'
    if journal.phase=='prepared':return 'LEAVE_OLD_RUNTIME'
    if not all(x is True for x in (fence_continuous,drain_proven,same_boot)):
        return 'HOLD_FENCE_MANUAL_RECOVERY'
    if journal.phase in ('migrate_intent','migrate_done'):
        return 'RESTORE_REQUIRES_APPROVAL' if backup_verified is True else 'HOLD_FENCE_MANUAL_RECOVERY'
    if journal.phase in ('stop_done','backup_intent','backup_done','rehearsal_intent','rehearsal_done'):
        return 'OLD_RUNTIME_RESTART_REQUIRES_BASELINE_AND_APPROVAL'
    return 'HOLD_FENCE_MANUAL_RECOVERY'


def quiescent(observation):
    expected=dict(active='inactive',main_pid=0,cgroup_empty=True,drain='complete',forced_kill=False)
    return (isinstance(observation,dict) and set(observation)==set(expected) and
            all(type(observation[k]) is type(v) and observation[k]==v for k,v in expected.items()))


class SystemdFence:
    """Owned persistent condition drop-in + ephemeral /run permit per unit.

    root='/' only on a future approved Linux executor; tests pass a temporary root.
    run(argv, timeout_seconds) must raise on nonzero/timeout, never log raw output.
    No default executor exists. Full effective-condition/unit identity readback and
    maintenance ownership are mandatory before stop. This is not an FD-based fence.
    """
    def __init__(self,root,manifest,run):
        validate_manifest(manifest)
        self.root=_check_path(root);self.operation=manifest['operation_id'];self.run=run
        self.binding=digest(manifest)
        self.units=(BOT,WEB)

    def _unit(self,unit): require(unit in self.units,'unit_scope')

    def dropin(self,unit):
        self._unit(unit)
        return self.root/'etc/systemd/system'/(unit+'.d')/('zz-'+self.operation+'.conf')

    def permit(self,unit):
        self._unit(unit)
        return self.root/'run/phase16'/self.operation/(unit+'.allow')

    def content(self,unit):
        self._unit(unit)
        return ('# Owned by '+self.operation+'; binding '+self.binding+'\n[Unit]\n'
                'ConditionPathExists=/run/phase16/'+self.operation+'/'+unit+'.allow\n').encode('ascii')

    def _intent(self,journal,phase):
        require(isinstance(journal,Journal) and journal.binding==self.binding,'journal_binding')
        fresh=Journal.load(journal.directory,journal.manifest)
        require(fresh.phase==journal.phase==phase and
                (journal.directory/'execution.lock').is_file() and
                not (journal.directory/'recovery').exists(),'operation_intent')

    def install(self,journal=None):
        self._intent(journal,'fence_intent')
        # Check all collisions first, then retain every created artifact on failure.
        for unit in self.units:
            for path in (self.dropin(unit),self.permit(unit)):
                _check_path(path);require(not path.exists(),'owned_path_exists')
        for unit in self.units:
            file=self.dropin(unit);file.parent.mkdir(parents=True,exist_ok=True)
            write_new(file,self.content(unit),0o644)
        self.run(['systemctl','daemon-reload'],15)

    def present(self):
        try:
            return all(_check_path(self.dropin(u)).read_bytes()==self.content(u)
                       and not _check_path(self.permit(u)).exists() for u in self.units)
        except OSError:return False

    def effective(self,observations):
        if not self.present() or set(observations)!=set(self.units):return False
        for unit in self.units:
            item=observations[unit]
            condition=['ConditionPathExists',False,False,'/run/phase16/'+self.operation+'/'+unit+'.allow']
            if item.get('id')!=unit or condition not in item.get('conditions',[]):return False
            if item.get('need_daemon_reload') is not False:return False
            if str(self.dropin(unit).relative_to(self.root)).replace('\\','/') not in item.get('loaded_dropins',[]):return False
        return True

    def stop(self,unit,journal=None):
        self._unit(unit);self._intent(journal,'stop_intent');require(self.present(),'fence_lost')
        self.run(['systemctl','stop',unit],90)

    def start(self,unit,journal):
        self._unit(unit)
        self._intent(journal,'candidate_start_intent' if unit==BOT else 'web_start_intent')
        require(self.present(),'fence_lost')
        path=self.permit(unit);_check_path(path)
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        write_new(path,self.binding.encode('ascii'))
        try:self.run(['systemctl','start',unit],40 if unit==BOT else 90)
        finally:
            # A process crash can leave a permit. Reload => intent/STOP, never retry.
            # /run disappears at reboot; persistent condition remains blocking.
            require(not path.is_symlink() and path.read_bytes()==self.binding.encode('ascii'),'permit_ownership')
            path.unlink();sync_directory(path.parent)

    def remove(self,journal=None):
        self._intent(journal,'release_intent')
        require(self.present(),'fence_ownership')
        # Only exact operation-owned files; never unmask/enable or touch foreign files.
        for unit in self.units:
            file=self.dropin(unit);file.unlink();sync_directory(file.parent)
        self.run(['systemctl','daemon-reload'],15)


def verify_stage(manifest_path, observation):
    """Compare a future isolated stage snapshot against the existing pinned contract.

    This does not collect observations, install wheels, prove import origins, or
    authorize a stage. The future runner must bind snapshot provenance separately.
    """
    raw=Path(manifest_path).read_bytes().replace(b'\r\n',b'\n')
    require(hashlib.sha256(raw).hexdigest()=='faac75cf5f2d136344bdfc54fd6cfe3bab8271cc7424ca1050775634860723a4', 'stage_manifest_binding')
    expected=json.loads(raw)
    require(isinstance(observation,dict) and set(observation)=={
        'source','runtime_pins','runtime_lock_sha256','archive_sha256','isolated_venv','pth_count','system_site_packages'}, 'stage_fields')
    require(observation['archive_sha256']==ARCHIVE and observation['source']==expected['source'], 'stage_source_binding')
    require(observation['runtime_lock_sha256']==expected['runtime_lock_sha256'] and
            observation['runtime_pins']==expected['runtime_pins'], 'stage_runtime_binding')
    require(observation['isolated_venv'] is True and observation['system_site_packages'] is False and
            type(observation['pth_count']) is int and observation['pth_count']==0, 'stage_isolation')
    return {'status':'STAGE_BINDING_SNAPSHOT_PASS','source_files':len(expected['source']),
            'runtime_pins':len(expected['runtime_pins']),'import_origins':'REQUIRE_TARGET_BINDING',
            'activation':'NOT_EXECUTED'}


def run_prepared(journal, operations, checks):
    """One pass, no replay or automatic recovery. Callbacks are NOT live bindings.

    A real executor must provide checksum-bound operations, OS deadlines and typed
    fresh evidence, not blanket True checks. Local tests supply synthetic callbacks.
    Stage validation is separate and outside the maintenance window.
    """
    require(journal.phase=='prepared','run_already_started')
    require(set(operations)==set(checks)==set(ACTIONS) and
            all(callable(f) for f in list(operations.values())+list(checks.values())), 'operation_set')
    for action in ACTIONS:
        try:journal.perform(action,operations[action],checks[action])
        except Stop:
            return dict(status='STOP',phase=journal.phase,candidate_start_requested=journal.candidate_requested,
                        automatic_recovery='DISABLED',reason='operation_stopped')
    return dict(status='PREPARED_OPERATIONS_COMPLETE',phase=journal.phase,
                candidate_start_requested=journal.candidate_requested,
                live_acceptance='NOT_ESTABLISHED_BY_COORDINATOR')
