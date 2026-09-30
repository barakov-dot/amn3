"""Offline contract tests; no production data, SSH or systemd execution."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
BOT='amn2-spain-bot.service';WEB='amn2-spain-web.service'
OP='phase16-maintenance-20260930-001'
TARGET='87b33ab0769b0f98670289e66e230407d82caebc05c6e459baf564564789d0c6'
BOOT='11111111-2222-3333-4444-555555555555'
NOW='2026-09-30T12:00:00+00:00'


def observations():
    from tests.test_phase16_bot_maintenance import manifest
    record=json.loads((ROOT/'research/amn2/phase16-bot-stage-readback-execution-001-2026-09-29.json').read_text())
    units={}
    for unit,baseline in manifest()['unit_baseline'].items():
        units[unit]=dict(baseline=baseline,user='root',group='root',launch_sha256='a'*64,
                         kill_mode='control-group',kill_signal=15,final_kill_signal=9)
    return dict(schema='phase16.maintenance-inputs.v1',operation_id=OP,target_binding_sha256=TARGET,
        boot_id=BOOT,observed_at=NOW,stage=record['local_result']['remote_observation']['result'],
        units=units,inventory=dict(writers=[dict(unit=BOT,role='bot'),dict(unit=WEB,role='web')],
        other_writer_classes=dict.fromkeys(('cron','agent','socket','timer'),'absent_verified'),
        process_scan='complete_bot_web_only',scan_sha256='b'*64),
        settings=dict(vps_apply_enabled=False,awg3_bootstrap_enabled=False,admission_seconds=10,
                      startup_bound_seconds=35,network_cidr='10.8.0.0/24'),
        rollback=dict(source_sha256='c'*64,dependencies_sha256='d'*64),
        pending_operations='none_observed')


def ownership():
    return dict(schema='phase16.maintenance-ownership.v1',operation_id=OP,target_binding_sha256=TARGET,
        boot_id=BOOT,valid_until='2026-09-30T12:30:00+00:00',exclusive_maintenance_owner=True,
        external_pollers_excluded=True,manual_cli_paused=True)


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('scripts.phase16_bot_maintenance_binding'),
                             'Maintenance target/stage binding is not implemented')
        from scripts import phase16_bot_maintenance_binding as binding
        self.b=binding

    def compile(self,obs=None,owner=None,**kw):
        return self.b.prepare_inputs(observations() if obs is None else obs,
            ownership() if owner is None else owner,now=kw.get('now',NOW))

    def test_actual_stage_evidence_bridges_existing_source_verifier_without_live_readiness(self):
        value=self.b.stage_snapshot()
        self.assertEqual(value['source_files'],126)
        self.assertEqual(value['content_files'],200)
        self.assertEqual(value['runtime_pins'],40)
        self.assertEqual(value['source']['__init__.py'],dict(bytes=49,sha256='e2dfdcaf386b2ee9befa8ca8c14331b63053cd4b56a7ba114c5db67b012f246e'))
        self.assertEqual(value['fresh_for_maintenance'],False)
        self.assertEqual(value['verified_at'],'2026-09-29T20:10:54.424549+00:00')

    def test_actual_draft_never_fills_unknown_inventory_from_stage_pass(self):
        value=self.b.preview()
        self.assertEqual(value['status'],'BLOCKED_UNKNOWN_PRECONDITIONS')
        self.assertFalse(value['live_executor_ready']);self.assertFalse(value['authorized'])
        self.assertIn('fresh_server_observation',value['blockers'])
        self.assertIn('operator_window_declaration',value['blockers'])
        self.assertIn('maintenance_operation_adapters',value['blockers'])
        self.assertIsNone(value['coordinator_manifest'])

    def test_binding_tamper_is_rejected_before_compiling_stage(self):
        for name in ('record','inventory','integration'):
            blobs=self.b.bound_sources()
            blobs[name]=blobs[name]+b' '
            with self.subTest(name=name),self.assertRaises(self.b.Stop):self.b.stage_snapshot(blobs=blobs)

    def test_valid_synthetic_inputs_bind_paths_identity_flags_and_budget_without_authorizing(self):
        value=self.compile();core=value['coordinator_manifest'];target=value['target_contract']
        self.assertEqual(value['status'],'PRECONDITIONS_VALIDATED_NOT_AUTHORIZED')
        self.assertFalse(value['live_executor_ready']);self.assertFalse(value['authorized'])
        self.assertEqual(target['candidate_interpreter'],'/opt/amn2-spain/bot-candidates/phase16-bot-runtime40-20260929-6e68235-001/runtime-venv/bin/python')
        self.assertEqual(target['database'],'/var/lib/amn2-spain/amn2.sqlite3')
        self.assertEqual(target['backup'],'/var/lib/amn2-spain/phase16-maintenance/'+OP+'/backup.sqlite3')
        self.assertEqual(target['service_identity'][BOT],dict(user='root',group='root'))
        self.assertEqual(core['admission_seconds'],10)
        self.assertFalse(core['vps_apply_enabled']);self.assertFalse(core['awg3_bootstrap_enabled'])
        self.b.validate_prepared(value,now=NOW)

    def test_missing_or_unknown_observation_never_compiles(self):
        for key in observations():
            obs=observations();del obs[key]
            with self.subTest(key=key),self.assertRaises(self.b.Stop):self.compile(obs)
        for key in ('inventory','stage','settings','units','rollback'):
            obs=observations();obs[key]=None
            with self.subTest(key=key),self.assertRaises(self.b.Stop):self.compile(obs)

    def test_wrong_target_operation_or_boot_is_rejected(self):
        for key,value in [('target_binding_sha256','0'*64),('operation_id','../unsafe'),('boot_id','bad')]:
            obs=observations();obs[key]=value
            with self.subTest(key=key),self.assertRaises(self.b.Stop):self.compile(obs)
        owner=ownership();owner['boot_id']='aaaaaaaa-2222-3333-4444-555555555555'
        with self.assertRaises(self.b.Stop):self.compile(owner=owner)

    def test_stale_future_naive_and_malformed_observation_times_rejected(self):
        for when in ('2026-09-30T11:54:59+00:00','2026-09-30T12:00:01+00:00','2026-09-30T12:00:00','private-secret'):
            obs=observations();obs['observed_at']=when
            with self.subTest(when=when),self.assertRaises(self.b.Stop):self.compile(obs)

    def test_old_stage_receipt_is_not_accepted_as_fresh_preconditions(self):
        record=json.loads((ROOT/'research/amn2/phase16-bot-stage-readback-execution-001-2026-09-29.json').read_text())
        with self.assertRaises(self.b.Stop):self.compile(record)
        obs=observations();obs['observed_at']=record['local_result']['claim']['claimed_at']
        with self.assertRaises(self.b.Stop):self.compile(obs)

    def test_current_stage_incomplete_or_saved_receipt_changed_stops(self):
        for key,value in [('status','INCOMPLETE'),('runtime_pins',48),('saved_receipt_sha256','0'*64),('destination','/tmp/stage'),('writes',False)]:
            obs=observations();obs['stage'][key]=value
            with self.subTest(key=key),self.assertRaises(self.b.Stop):self.compile(obs)

    def test_extra_writer_or_unknown_class_prevents_manifest(self):
        for mode in ('writer','cron','agent','socket','timer','scan'):
            obs=observations()
            if mode=='writer':obs['inventory']['writers'].append(dict(unit='other.service',role='bot'))
            elif mode=='scan':obs['inventory']['process_scan']='unknown'
            else:obs['inventory']['other_writer_classes'][mode]='unknown'
            with self.subTest(mode=mode),self.assertRaises(self.b.Stop):self.compile(obs)

    def test_operator_window_not_inferred_from_host_scan(self):
        for field in ('exclusive_maintenance_owner','external_pollers_excluded','manual_cli_paused'):
            for v in (False,None,1):
                owner=ownership();owner[field]=v
                with self.subTest(field=field,value=v),self.assertRaises(self.b.Stop):self.compile(owner=owner)
        for deadline in ('2026-09-30T12:00:00+00:00','2026-10-01T12:00:00+00:00'):
            owner=ownership();owner['valid_until']=deadline
            with self.assertRaises(self.b.Stop):self.compile(owner=owner)

    def test_pending_operations_prevent_startup_preconditions(self):
        for status in ('unknown','present',False,0):
            obs=observations();obs['pending_operations']=status
            with self.subTest(status=status),self.assertRaises(self.b.Stop):self.compile(obs)

    def test_flags_and_admission_budget_fail_closed(self):
        for field,value in [('vps_apply_enabled',True),('awg3_bootstrap_enabled',0),('admission_seconds',40),
                            ('admission_seconds',True),('startup_bound_seconds',40),('startup_bound_seconds',5)]:
            obs=observations();obs['settings'][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(self.b.Stop):self.compile(obs)

    def test_user_group_and_unit_baseline_cannot_be_guessed(self):
        for field,value in [('user',''),('group',None),('user','root\nExecStart=evil'),('kill_signal',True),('kill_mode','process')]:
            obs=observations();obs['units'][BOT][field]=value
            with self.subTest(field=field),self.assertRaises(self.b.Stop):self.compile(obs)
        obs=observations();obs['units'][BOT]['baseline']['start_seconds']=90
        with self.assertRaises(self.b.Stop):self.compile(obs)

    def test_network_invalid_hash_or_raw_extra_field_is_rejected_redacted(self):
        for mode in ('cidr','hash','extra'):
            obs=observations()
            if mode=='cidr':obs['settings']['network_cidr']='private-secret'
            if mode=='hash':obs['rollback']['source_sha256']='private-secret'
            if mode=='extra':obs['settings']['token']='private-secret'
            with self.subTest(mode=mode):
                value=self.b.safe_prepare_inputs(obs,ownership(),now=NOW)
                self.assertEqual(value['status'],'STOP_INPUTS')
                self.assertNotIn('private-secret',json.dumps(value))

    def test_prepared_target_tamper_breaks_pair_binding(self):
        for name in ('database','candidate_source','backup'):
            value=self.compile();value['target_contract'][name]='/tmp/other'
            with self.subTest(name=name),self.assertRaises(self.b.Stop):self.b.validate_prepared(value)
        value=self.compile();value['coordinator_manifest']['admission_seconds']=11
        with self.assertRaises(self.b.Stop):self.b.validate_prepared(value)

    def test_rehashed_unsafe_target_paths_still_rejected(self):
        from scripts import phase16_bot_maintenance as core
        value=self.compile();value['target_contract']['database']='/tmp/other'
        value['coordinator_manifest']['target_contract_sha256']=core.digest(value['target_contract'])
        value['prepared_sha256']=core.digest({k:v for k,v in value.items() if k!='prepared_sha256'})
        with self.assertRaises(self.b.Stop):self.b.validate_prepared(value)

    def test_rehashed_core_and_target_boot_mismatch_rejected(self):
        from scripts import phase16_bot_maintenance as core
        value=self.compile();value['coordinator_manifest']['boot_id']='other-boot'
        value['prepared_sha256']=core.digest({k:v for k,v in value.items() if k!='prepared_sha256'})
        with self.assertRaises(self.b.Stop):self.b.validate_prepared(value)

    def test_prepared_inputs_expire_before_reuse(self):
        value=self.compile()
        with self.assertRaises(self.b.Stop):self.b.validate_prepared(value,now='2026-09-30T12:05:01+00:00')
        self.b.validate_prepared(value,now='2026-09-30T12:05:00+00:00')

    def test_mutating_callers_input_does_not_change_prepared_binding(self):
        obs=observations();owner=ownership();value=self.compile(obs,owner)
        obs['units'][BOT]['baseline']['enabled']='disabled'
        obs['inventory']['writers'].clear();owner['manual_cli_paused']=False
        self.assertEqual(value['coordinator_manifest']['unit_baseline'][BOT]['enabled'],'enabled')
        self.assertEqual(len(value['coordinator_manifest']['writers']),2)
        self.b.validate_prepared(value,now=NOW)

    def test_target_binding_is_persisted_in_real_journal_and_cannot_drift(self):
        from scripts import phase16_bot_maintenance as core
        value=self.compile();manifest=value['coordinator_manifest']
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'journal';core.Journal.create(path,manifest)
            stored=json.loads((path/'manifest.json').read_text())
            self.assertEqual(stored['target_contract_sha256'],manifest['target_contract_sha256'])
            changed=copy.deepcopy(manifest);changed['target_contract_sha256']='0'*64
            with self.assertRaises(core.Stop):core.Journal.load(path,changed)
            self.assertEqual(core.Journal.load(path,manifest).phase,'prepared')

    def test_malformed_target_digest_cannot_create_coordinator_journal(self):
        from scripts import phase16_bot_maintenance as core
        from tests.test_phase16_bot_maintenance import manifest
        for v in (True,None,'short'):
            item=manifest();item['target_contract_sha256']=v
            with tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'journal'
                with self.assertRaises(core.Stop):core.Journal.create(path,item)
                self.assertFalse(path.exists())

    def test_cli_is_offline_and_execute_flag_is_not_available(self):
        script=ROOT/'scripts/phase16_bot_maintenance_binding.py'
        with tempfile.TemporaryDirectory() as folder:
            run=subprocess.run([sys.executable,'-I','-S','-B',str(script)],cwd=folder,capture_output=True,timeout=10)
            self.assertEqual(run.returncode,0,run.stderr)
            value=json.loads(run.stdout);self.assertEqual(value['status'],'BLOCKED_UNKNOWN_PRECONDITIONS')
            self.assertEqual(list(Path(folder).iterdir()),[])
            run=subprocess.run([sys.executable,'-I','-S','-B',str(script),'--execute'],cwd=folder,capture_output=True,timeout=10)
            self.assertNotEqual(run.returncode,0);self.assertEqual(list(Path(folder).iterdir()),[])

if __name__=='__main__':unittest.main()
