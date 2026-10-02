"""Whole sequence with real SQLite/artifacts; manager and host admission are doubles."""
import importlib.util
import json
import unittest
from unittest.mock import patch
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_binding as binding
from scripts import phase16_bot_maintenance_jobs as jobs
from scripts import phase16_bot_service_operations as services
from tests import test_phase16_bot_maintenance_jobs as jt
from tests import test_phase16_bot_service_operations as st

AVAILABLE=importlib.util.find_spec('scripts.phase16_bot_maintenance_sequence') is not None
if AVAILABLE:from scripts import phase16_bot_maintenance_sequence as sequence

class Availability(unittest.TestCase):
    def test_full_sequence_exists(self):
        self.assertTrue(AVAILABLE,'fence-to-release sequence is not connected')

@unittest.skipUnless(AVAILABLE,'availability fails first')
class SequenceTests(unittest.TestCase):
    sleep=jt.JobTests.sleep
    command=jt.JobTests.command
    result=jt.JobTests.result
    real_data=jt.JobTests.real_data
    source_check=st.ServiceTests.source_check
    web_launch=staticmethod(st.ServiceTests.web_launch)
    def bot_launch(self):
        value=self.web_launch()
        value.update(Type='notify',Restart='no',TimeoutStartUSec=40000000,
                     ExecStart=['/usr/bin/python3',['/usr/bin/python3','-m','app.main'],False])
        return value
    def setUp(self):
        original=jt.observations
        def facts():
            value=original()
            for unit,launch in ((core.BOT,self.bot_launch()),(core.WEB,self.web_launch())):
                value['units'][unit]['launch_sha256']=core.digest(launch)
            return value
        # Reuse only fixture construction, not its already-completed fence/stop.
        with patch.object(jt,'observations',facts),patch.object(core.Journal,'perform'):
            jt.JobTests.setUp(self)
        for unit in (core.BOT,core.WEB):
            self.manager.properties[unit].update(ActiveState='active',SubState='running',
                MainPID='101' if unit==core.BOT else '102',ExecMainCode='0',DropInPaths='')
        self.native=self.client.run
        self.running={};self.drop_receipt=False;self.fail_web=False;self.fail_health=False
        self.source_checks=0;self.calls=[];self.host_calls=0;self.host_failure_at=None
        self.interrupt_stop=False;self.kill_stop=False;self.expire_after_fence=False
        self.client.run=self.sequence_command
        epoch=binding.timestamp(jt.NOW).timestamp()
        self.supervisor.utc_now=lambda:epoch+self.clock[0]
        self.real_data()
        self.operations=services.ServiceOperations(self.journal,self.client,self.fence,self.supervisor,
            expected_username='fixture_bot',source_verifier=self.source_check,web_port=3030,
            clock=lambda:self.clock[0],sleep=self.sleep)
        self.runner=sequence.MaintenanceSequence(self.operations,host_guard=self.host_guard)
    def host_guard(self,prepared):
        self.host_calls+=1
        if self.host_calls==self.host_failure_at:raise core.Stop('synthetic_host_unknown')
        return prepared['prepared_sha256']
    def sequence_command(self,argv,seconds):
        self.calls.append(list(argv))
        if argv[0]=='busctl' and 'bot' in argv[4] and argv[-1]!='Conditions' and not self.operations.dropin.exists():
            name=argv[-1];value=self.bot_launch()
            data=[value[name][:2]+[False,0,0,0,0,0,0,0]] if name=='ExecStart' else value[name]
            kind='a(sasbttttuii)' if name=='ExecStart' else services.LAUNCH_FIELDS[name]
            return json.dumps(dict(type=kind,data=data)).encode()
        if argv[:3]==['systemctl','--no-block','stop']:
            self.assertTrue(self.fence.present())
            self.assertEqual(self.journal.phase,'stop_intent')
            if self.interrupt_stop:raise KeyboardInterrupt()
            unit=argv[-1]
            self.manager.properties[unit].update(ActiveState='inactive',SubState='dead',MainPID='0',
                ExecMainCode='2' if self.kill_stop else '1',ExecMainStatus='9' if self.kill_stop else '0')
            return b''
        value=st.ServiceTests.manager_command(self,argv,seconds)
        if self.expire_after_fence and argv==['systemctl','daemon-reload']:
            self.clock[0]+=40
        return value
    def requests(self,verb):
        return [v[-1] for v in self.calls if v[:3]==['systemctl','--no-block',verb]]
    def test_all_eight_steps_reach_release_with_real_data_and_evidence(self):
        result=self.runner.run()
        self.assertEqual(result['status'],'SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE')
        self.assertEqual(self.journal.phase,'release_done')
        self.assertEqual(self.requests('stop'),[core.WEB,core.BOT])
        self.assertEqual(self.requests('start'),[core.BOT,core.WEB])
        self.assertEqual(self.request_count,3)
        self.assertFalse(self.fence.present())
        self.assertEqual(jobs.load_signed(self.directory/'sequence-result.json')['result'],result)
        self.assertEqual(len(self.journal.events),17)
    def test_unknown_host_stops_before_first_fence_or_service_write(self):
        self.host_failure_at=1
        result=self.runner.run()
        self.assertEqual(result['status'],'STOP')
        self.assertEqual(result['recovery_route'],'LEAVE_OLD_RUNTIME')
        self.assertEqual(self.journal.phase,'prepared')
        self.assertFalse(self.fence.dropin(core.BOT).exists())
        self.assertEqual(self.requests('stop'),[])
    def test_boolean_host_guard_is_not_evidence(self):
        self.runner.host_guard=lambda prepared:True
        self.assertEqual(self.runner.run()['status'],'STOP')
        self.assertEqual(self.journal.phase,'prepared')
    def test_host_change_after_fence_does_not_stop_services(self):
        self.host_failure_at=2
        result=self.runner.run()
        self.assertEqual(result['status'],'STOP')
        self.assertEqual(result['recovery_route'],'HOLD_FENCE_MANUAL_RECOVERY')
        self.assertTrue(self.fence.present())
        self.assertEqual(self.requests('stop'),[])
    def test_forced_stop_never_starts_backup(self):
        self.kill_stop=True
        result=self.runner.run()
        self.assertEqual(result['status'],'STOP')
        self.assertEqual(self.request_count,0)
        self.assertTrue(self.fence.present())
        self.assertFalse((self.directory/'backup.sqlite3').exists())
    def test_web_failure_preserves_migrated_database_and_no_restore(self):
        self.fail_health=True
        result=self.runner.run()
        self.assertEqual(result['recovery_route'],'PRESERVE_DB_MANUAL_RECOVERY')
        self.assertEqual(self.journal.phase,'web_start_intent')
        self.assertTrue(self.fence.present())
        self.assertTrue((self.directory/'receipts/migrate.json').exists())
        self.assertEqual(self.requests('start'),[core.BOT,core.WEB])
    def test_no_second_run_after_even_precondition_stop(self):
        self.host_failure_at=1;self.runner.run();before=list(self.calls)
        with self.assertRaises(core.Stop):self.runner.run()
        self.assertEqual(self.calls,before)
    def test_interrupt_keeps_intent_and_rerun_refuses(self):
        self.interrupt_stop=True
        with self.assertRaises(KeyboardInterrupt):self.runner.run()
        self.assertEqual(self.journal.phase,'stop_intent')
        self.assertTrue((self.directory/'sequence-claim.json').exists())
        self.assertFalse((self.directory/'sequence-result.json').exists())
        before=list(self.calls)
        with self.assertRaises(core.Stop):self.runner.run()
        self.assertEqual(before,self.calls)
    def test_expired_step_cannot_be_marked_complete(self):
        self.expire_after_fence=True
        result=self.runner.run()
        self.assertEqual(result['status'],'STOP')
        self.assertEqual(self.journal.phase,'fence_intent')
        self.assertEqual(self.requests('stop'),[])
    def test_insufficient_total_window_stops_before_fence(self):
        self.runner.total_seconds=1801
        result=self.runner.run()
        self.assertEqual(result['status'],'STOP')
        self.assertEqual(self.journal.phase,'prepared')
    def test_reboot_blocks_before_any_service_action(self):
        (self.root/'proc/sys/kernel/random/boot_id').write_text('00000000-0000-0000-0000-000000000000')
        self.assertEqual(self.runner.run()['status'],'STOP')
        self.assertEqual(self.requests('stop'),[])
    def test_late_source_read_cannot_create_fence_dropins(self):
        def slow():
            self.clock[0]+=31
            return self.source_check()
        self.operations.source_verifier=slow
        result=self.runner.run()
        self.assertEqual(result['status'],'STOP')
        self.assertEqual(self.journal.phase,'prepared')
        self.assertFalse(any(self.fence.dropin(u).exists() for u in (core.BOT,core.WEB)))
        self.assertNotIn(['systemctl','daemon-reload'],self.calls)

    def test_slow_intent_write_stops_before_operation_mutation(self):
        original=core.Journal._append
        def append(journal,phase):
            original(journal,phase)
            if phase=='fence_intent':self.clock[0]+=31
        with patch.object(core.Journal,'_append',append):result=self.runner.run()
        self.assertEqual(result['status'],'STOP')
        self.assertEqual(self.journal.phase,'fence_intent')
        self.assertFalse(any(self.fence.dropin(u).exists() for u in (core.BOT,core.WEB)))
        self.assertNotIn(['systemctl','daemon-reload'],self.calls)

    def test_failure_keeps_closed_reason_without_raw_error(self):
        self.expire_after_fence=True
        result=self.runner.run()
        self.assertEqual(result['reason'],'sequence_step_deadline')

    def test_unknown_exception_message_is_never_saved(self):
        def private(prepared):raise RuntimeError('SECRET=private-fixture')
        self.runner.host_guard=private
        result=self.runner.run()
        self.assertEqual(result['reason'],'sequence_precondition_or_operation_failed')
        self.assertNotIn('private-fixture',(self.directory/'sequence-result.json').read_text())

    def test_corrupt_job_completion_prevents_next_job_and_start(self):
        original=self.supervisor.execute
        def execute(action):
            original(action)
            path=jobs.job_paths(self.journal,action)['complete']
            value=jobs.load_signed(path);value['claim_sha256']='0'*64;value.pop('sha256')
            value['sha256']=core.digest(value);path.write_bytes(core.encoded(value))
        self.supervisor.execute=execute
        result=self.runner.run()
        self.assertEqual(result['status'],'STOP')
        self.assertEqual(self.journal.phase,'backup_intent')
        self.assertEqual(self.request_count,1)
        self.assertEqual(self.requests('start'),[])

    def test_process_restart_between_fence_and_stop_blocks_stop(self):
        def guard(prepared):
            value=self.host_guard(prepared)
            if self.host_calls==2:self.manager.properties[core.BOT]['InvocationID']='f'*32
            return value
        self.runner.host_guard=guard
        self.assertEqual(self.runner.run()['status'],'STOP')
        self.assertEqual(self.requests('stop'),[])
        self.assertTrue(self.fence.present())

    def test_final_result_write_failure_cannot_report_completion(self):
        original=jobs.write_signed
        def write(path,payload):
            if path.name=='sequence-result.json':raise OSError('private-fixture')
            return original(path,payload)
        with patch.object(jobs,'write_signed',write),self.assertRaisesRegex(core.Stop,'sequence_result_unpersisted'):
            self.runner.run()
        self.assertEqual(self.journal.phase,'release_done')
        self.assertTrue((self.directory/'sequence-claim.json').exists())
        self.assertFalse((self.directory/'sequence-result.json').exists())

if __name__=='__main__':unittest.main()
