"""No subprocess/systemd: injected executor and disposable local filesystem only."""
import json
from pathlib import Path
import tempfile
import unittest
from scripts import phase16_bot_maintenance as m

BOT='amn2-spain-bot.service'
WEB='amn2-spain-web.service'

def manifest():
    return dict(operation_id='phase16-local-test-001',boot_id='test-boot',
                candidate_commit='6e682356ed14a62d636ee58039fd3a389e794809',
                source_archive_sha256='e19abc5c132acae035503267d41d38fdd1e272951b2ebfd0f2a73e2f7c660cb7',
                runtime_pins=40,vps_apply_enabled=False,awg3_bootstrap_enabled=False,
                admission_seconds=10,startup_budget_assessed=True,
                inventory_complete=True,exclusive_maintenance_owner=True,
                external_pollers_excluded=True,manual_cli_paused=True,
                writers=[dict(unit=BOT,role='bot'),dict(unit=WEB,role='web')],
                unit_baseline={BOT:dict(active='active',enabled='enabled',masked=False,start_seconds=40,stop_seconds=90,restart='no'),
                               WEB:dict(active='active',enabled='enabled',masked=False,start_seconds=90,stop_seconds=90,restart='on-failure')},
                other_writer_classes={'cron':'absent_verified','agent':'absent_verified',
                                      'socket':'absent_verified','timer':'absent_verified'})

class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.j=m.Journal.create(self.root/'journal',manifest())

    def advance(self, actions):
        for action in actions: self.j.perform(action,lambda:None,lambda:True)

    def test_order_and_persistent_reload(self):
        self.advance(['fence','stop','backup','rehearsal','migrate'])
        loaded=m.Journal.load(self.root/'journal',manifest())
        self.assertEqual(loaded.phase,'migrate_done')
        self.assertFalse(loaded.candidate_requested)
        self.assertEqual(m.recovery_route(loaded,fence_continuous=True,drain_proven=True,
                                         backup_verified=True,same_boot=True),'RESTORE_REQUIRES_APPROVAL')

    def test_start_intent_persisted_before_action_even_when_start_raises(self):
        self.advance(['fence','stop','backup','rehearsal','migrate'])
        def fail():
            self.assertTrue(m.Journal.load(self.root/'journal',manifest()).candidate_requested)
            raise TimeoutError('private detail')
        with self.assertRaisesRegex(m.Stop,'^action_failed$'):
            self.j.perform('candidate_start',fail,lambda:True)
        loaded=m.Journal.load(self.root/'journal',manifest())
        self.assertEqual(m.recovery_route(loaded,fence_continuous=True,drain_proven=True,
                                         backup_verified=True,same_boot=True),'PRESERVE_DB_MANUAL_RECOVERY')
        with self.assertRaises(m.Stop): loaded.perform('candidate_start',lambda:None,lambda:True)

    def test_unknown_drain_lost_fence_boot_or_backup_never_restore(self):
        self.advance(['fence','stop','backup','rehearsal','migrate'])
        good=dict(fence_continuous=True,drain_proven=True,backup_verified=True,same_boot=True)
        for field in good:
            with self.subTest(field=field):
                args=dict(good);args[field]=False
                self.assertEqual(m.recovery_route(self.j,**args),'HOLD_FENCE_MANUAL_RECOVERY')

    def test_failed_verification_retains_intent_and_blocks_progress(self):
        with self.assertRaisesRegex(m.Stop,'^verification_failed$'):
            self.j.perform('fence',lambda:None,lambda:False)
        self.assertEqual(self.j.phase,'fence_intent')
        with self.assertRaises(m.Stop): self.j.perform('stop',lambda:None,lambda:True)

    def test_out_of_order_duplicate_and_corrupt_events_stop(self):
        with self.assertRaises(m.Stop): self.j.perform('migrate',lambda:None,lambda:True)
        self.advance(['fence'])
        with self.assertRaises(m.Stop): self.j.perform('fence',lambda:None,lambda:True)
        event=sorted((self.root/'journal').glob('[0-9][0-9][0-9].json'))[-1]
        event.write_text('{}')
        with self.assertRaises(m.Stop): m.Journal.load(self.root/'journal',manifest())

    def test_stale_loaded_writer_cannot_append_after_another_writer(self):
        stale=m.Journal.load(self.root/'journal',manifest())
        self.advance(['fence'])
        called=[]
        with self.assertRaises(m.Stop): stale.perform('fence',lambda:called.append(True),lambda:True)
        self.assertEqual(called,[])

    def test_crashed_executor_claim_is_not_replayed(self):
        (self.root/'journal/execution.lock').write_bytes(b'crashed-owner')
        called=[]
        with self.assertRaises(m.Stop):self.j.perform('fence',lambda:called.append(1),lambda:True)
        self.assertEqual(called,[])
        self.assertEqual((self.root/'journal/execution.lock').read_bytes(),b'crashed-owner')

    def test_forward_action_is_blocked_during_recovery(self):
        self.advance(['fence','stop','backup','rehearsal','migrate'])
        (self.root/'journal/recovery').mkdir()
        with self.assertRaises(m.Stop):self.j.perform('candidate_start',lambda:None,lambda:True)
        self.assertFalse(self.j.candidate_requested)

    def test_manifest_baseline_is_persisted_and_cannot_drift(self):
        self.assertEqual(json.loads((self.root/'journal/manifest.json').read_text()),manifest())
        wrong=manifest();wrong['unit_baseline'][BOT]['enabled']='disabled'
        with self.assertRaises(m.Stop):m.Journal.load(self.root/'journal',wrong)

    def test_invalid_manifest_is_rejected_before_journal_creation(self):
        variants=[('inventory_complete',False),('runtime_pins',48),('vps_apply_enabled',True),
                  ('awg3_bootstrap_enabled',True),('admission_seconds',40),
                  ('external_pollers_excluded',False),('candidate_commit','bad')]
        for field,value in variants:
            with self.subTest(field=field):
                item=manifest();item[field]=value
                with self.assertRaises(m.Stop): m.Journal.create(self.root/field,item)
                self.assertFalse((self.root/field).exists())

class CoordinatorTests(unittest.TestCase):
    def test_successful_run_orders_all_actions_and_is_not_replayable(self):
        with tempfile.TemporaryDirectory() as temp:
            j=m.Journal.create(Path(temp)/'journal',manifest());calls=[]
            ops={name:(lambda n=name:calls.append(n)) for name in m.ACTIONS}
            checks={name:lambda:True for name in m.ACTIONS}
            result=m.run_prepared(j,ops,checks)
            self.assertEqual(result['status'],'PREPARED_OPERATIONS_COMPLETE')
            self.assertEqual(calls,list(m.ACTIONS))
            with self.assertRaises(m.Stop):m.run_prepared(j,ops,checks)

    def test_failure_at_each_phase_never_runs_later_actions_or_automatic_cleanup(self):
        for fail_at in m.ACTIONS:
            with self.subTest(phase=fail_at),tempfile.TemporaryDirectory() as temp:
                j=m.Journal.create(Path(temp)/'journal',manifest());calls=[]
                ops={name:(lambda n=name:calls.append(n)) for name in m.ACTIONS}
                checks={name:(lambda n=name:n!=fail_at) for name in m.ACTIONS}
                result=m.run_prepared(j,ops,checks)
                self.assertEqual(result['status'],'STOP')
                self.assertEqual(calls,list(m.ACTIONS[:m.ACTIONS.index(fail_at)+1]))
                self.assertEqual(j.phase,fail_at+'_intent')
                self.assertEqual(result['candidate_start_requested'],m.ACTIONS.index(fail_at)>=m.ACTIONS.index('candidate_start'))

class FenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.calls=[]
        def run(argv,timeout): self.calls.append((argv,timeout))
        self.f=m.SystemdFence(self.root,manifest(),run)
        self.j=m.Journal.create(self.root/'journal',manifest())

    def install(self):
        self.j.perform('fence',lambda:self.f.install(self.j),lambda:True)

    def test_own_dropins_only_and_no_mask_enable_or_timeout_changes(self):
        self.install()
        for unit in (BOT,WEB):
            content=self.f.dropin(unit).read_text()
            self.assertIn('ConditionPathExists=/run/phase16/',content)
            self.assertFalse(self.f.permit(unit).exists())
            self.assertNotIn('Timeout',content)
        for action in ('stop','backup','rehearsal','migrate','candidate_start','web_start'):
            self.j.perform(action,lambda:None,lambda:True)
        self.j.perform('release',lambda:self.f.remove(self.j),lambda:True)
        self.assertTrue(all(not self.f.dropin(u).exists() for u in (BOT,WEB)))
        self.assertEqual([c[0] for c in self.calls],[['systemctl','daemon-reload']]*2)

    def test_foreign_file_and_modified_owned_file_never_overwritten_or_removed(self):
        file=self.f.dropin(BOT);file.parent.mkdir(parents=True);file.write_text('foreign')
        with self.assertRaises(m.Stop): self.install()
        self.assertEqual(file.read_text(),'foreign')

    def test_modified_owned_file_never_removed(self):
        self.install();file=self.f.dropin(BOT);file.write_text('changed')
        for action in ('stop','backup','rehearsal','migrate','candidate_start','web_start'):
            self.j.perform(action,lambda:None,lambda:True)
        with self.assertRaises(m.Stop):self.j.perform('release',lambda:self.f.remove(self.j),lambda:True)
        self.assertEqual(file.read_text(),'changed')

    def test_direct_mutation_without_intent_is_rejected(self):
        with self.assertRaises(m.Stop):self.f.install()
        self.install()
        with self.assertRaises(m.Stop):self.f.remove()
        with self.assertRaises(m.Stop):self.f.stop(BOT)
        self.assertTrue(self.f.present())

    def test_candidate_start_requires_durable_intent_and_closes_permit_on_timeout(self):
        self.install()
        j=self.j
        with self.assertRaises(m.Stop): self.f.start(BOT,j)
        for action in ('stop','backup','rehearsal','migrate'):j.perform(action,lambda:None,lambda:True)
        def run(argv,timeout):
            if argv[1]=='start':
                self.assertEqual(timeout,40)
                self.assertTrue(self.f.permit(BOT).exists())
                raise TimeoutError()
        self.f.run=run
        with self.assertRaises(m.Stop):j.perform('candidate_start',lambda:self.f.start(BOT,j),lambda:True)
        self.assertFalse(self.f.permit(BOT).exists())
        self.assertTrue(self.f.dropin(BOT).exists())
        self.assertTrue(j.candidate_requested)

    def test_stop_uses_original_90_seconds_and_never_stops_unlisted_unit(self):
        self.install()
        self.j.perform('stop',lambda:self.f.stop(BOT,self.j),lambda:True)
        self.assertEqual(self.calls[-1],(['systemctl','stop',BOT],90))
        with self.assertRaises(m.Stop):self.f.stop('other.service',self.j)

    def test_effective_condition_requires_loaded_dropin_identity_and_reload(self):
        import copy
        self.install();obs={}
        for unit in (BOT,WEB):
            obs[unit]=dict(id=unit,need_daemon_reload=False,
                loaded_dropins=[str(self.f.dropin(unit).relative_to(self.root)).replace('\\','/')],
                conditions=[['ConditionPathExists',False,False,'/run/phase16/'+self.f.operation+'/'+unit+'.allow']])
        self.assertTrue(self.f.effective(obs))
        for field,value in [('id','alias.service'),('need_daemon_reload',True),('loaded_dropins',[]),('conditions',[])]:
            changed=copy.deepcopy(obs);changed[BOT][field]=value
            self.assertFalse(self.f.effective(changed))

    def test_incomplete_effective_fence_and_forced_kill_fail_closed(self):
        self.assertFalse(m.quiescent({'active':'inactive','main_pid':0,'cgroup_empty':True,
                                     'drain':'unknown','forced_kill':False}))
        self.assertFalse(m.quiescent({'active':'inactive','main_pid':0,'cgroup_empty':True,
                                     'drain':'complete','forced_kill':True}))

class StageTests(unittest.TestCase):
    def setUp(self):
        self.path=Path(__file__).resolve().parents[1]/'research/amn2/phase16-bot-integration-manifest-v3-6e68235.json'
        item=json.loads(self.path.read_text())
        self.obs=dict(source=item['source'],runtime_pins=item['runtime_pins'],runtime_lock_sha256=item['runtime_lock_sha256'],
                      archive_sha256=manifest()['source_archive_sha256'],isolated_venv=True,pth_count=0,system_site_packages=False)

    def test_exact_stage_binding_pass(self):
        self.assertEqual(m.verify_stage(self.path,self.obs)['status'],'STAGE_BINDING_SNAPSHOT_PASS')

    def test_test_venv_extra_dependency_source_drift_and_pth_are_rejected(self):
        import copy
        for mode in ('test_venv','source','pth','isolation'):
            obs=copy.deepcopy(self.obs)
            if mode=='test_venv':obs['runtime_pins']['pytest']='8.0'
            if mode=='source':obs['source']['__init__.py']['sha256']='0'*64
            if mode=='pth':obs['pth_count']=1
            if mode=='isolation':obs['isolated_venv']=False
            with self.subTest(mode=mode),self.assertRaises(m.Stop):m.verify_stage(self.path,obs)

if __name__=='__main__':unittest.main()
