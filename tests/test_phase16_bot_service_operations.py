"""Real journal/drop-in artifacts and strict synthetic manager boundary."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import hashlib
import io
import tempfile
import contextlib
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_jobs as jobs
from scripts import phase16_bot_maintenance_linux as linux
from tests import test_phase16_bot_maintenance_jobs as job_tests

AVAILABLE=importlib.util.find_spec('scripts.phase16_bot_service_operations') is not None
if AVAILABLE:from scripts import phase16_bot_service_operations as services

class Availability(unittest.TestCase):
    def test_service_operations_exist(self):
        self.assertTrue(AVAILABLE,'concrete candidate/web/release operations missing')

@unittest.skipUnless(AVAILABLE,'availability fails first')
class ServiceTests(unittest.TestCase):
    def setUp(self):
        def facts():
            value=original()
            value['units'][core.WEB]['launch_sha256']=self.web_launch_hash()
            return value
        original=job_tests.observations
        with patch.object(job_tests,'observations',facts):job_tests.JobTests.setUp(self)
    @staticmethod
    def web_launch():
        return {'ExecStart':['/usr/bin/python3',['/usr/bin/python3','-m','app.web'],False],
            'WorkingDirectory':'/opt/amn2-spain/runtime/source', 'User':'root','Group':'root',
            'Environment':[], 'EnvironmentFiles':[], 'Type':'simple','Restart':'on-failure',
            'KillMode':'control-group', 'KillSignal':15, 'FinalKillSignal':9,
            'TimeoutStartUSec':90000000, 'TimeoutStopUSec':90000000}
    @classmethod
    def web_launch_hash(cls):
        value=cls.web_launch();value['ExecStart'][2]=False
        return core.digest(value)
    sleep=job_tests.JobTests.sleep
    result=job_tests.JobTests.result
    command=job_tests.JobTests.command
    real_data=job_tests.JobTests.real_data
    def setup_services(self):
        self.real_data()
        for action in ('backup','rehearsal','migrate'):
            self.journal.perform(action,lambda a=action:self.supervisor.execute(a),lambda:True)
        self.native=self.client.run
        self.running={}
        self.drop_receipt=False
        self.fail_web=False
        self.fail_health=False
        self.source_checks=0
        self.client.run=self.manager_command
        self.operations=services.ServiceOperations(self.journal,self.client,self.fence,
            self.supervisor,expected_username='fixture_bot',
            source_verifier=self.source_check,web_port=3030,clock=lambda:self.clock[0],sleep=self.sleep)
    def source_check(self):self.source_checks+=1;return 'c'*64
    def manager_command(self,argv,seconds):
        if argv[0]=='/usr/bin/python3':
            self.assertEqual(argv[-2:],[str(3030),'302'])
            self.assertGreater(seconds,0);self.assertLessEqual(seconds,5)
            if self.fail_health:raise core.Stop('synthetic_http_failure')
            return b'WEB_HTTP_READY'
        if argv[0]=='busctl' and argv[-1]!='Conditions':
            name=argv[-1]
            if 'web' in argv[4]:
                value=self.web_launch()
                if name=='ExecStart':
                    data=[value[name][:2]+[False,0,0,0,0,0,0,0]];kind='a(sasbttttuii)'
                else:data=value[name];kind=services.LAUNCH_FIELDS[name]
                return json.dumps(dict(type=kind,data=data)).encode()
            if name=='ExecStart':
                a=services.candidate_argv(self.prepared['target_contract'])
                data=[[a[0],a,False,0,0,0,0,0,0,0]];kind='a(sasbttttuii)'
            else:
                target=self.prepared['target_contract']
                data=str(Path(target['old_source']).parent).replace('\\','/') if name=='WorkingDirectory' else target['service_identity'][core.BOT][name.lower()];kind='s'
            return json.dumps(dict(type=kind,data=data)).encode()
        if argv[:2]==['journalctl','--no-pager']:
            if self.drop_receipt:return b''
            state=self.running[core.BOT]
            return (json.dumps(dict(_SYSTEMD_UNIT=core.BOT,_SYSTEMD_INVOCATION_ID=state['InvocationID'],
                _BOOT_ID=self.manifest['boot_id'].replace('-',''),_PID=state['MainPID'],
                MESSAGE='telegram_persistent_admission=pass bot_identity=@fixture_bot webhook_configured=false pending_update_count=0 allowed_updates=message,callback_query'))+'\n').encode()
        if argv[:3]==['systemctl','--no-block','start']:
            unit=argv[-1]
            self.assertTrue(self.fence.permit(unit).exists())
            if unit==core.WEB and self.fail_web:raise core.Stop('synthetic_web_failure')
            value=self.manager.properties[unit]
            value.update(ActiveState='active',SubState='running',MainPID='301' if unit==core.BOT else '302',
                InvocationID=('d' if unit==core.BOT else 'e')*32,ExecMainCode='0',ExecMainStatus='0',Type='notify' if unit==core.BOT else 'simple')
            self.running[unit]=dict(value)
            return b''
        if argv==['systemctl','daemon-reload']:
            for unit in (core.BOT,core.WEB):
                owned=self.fence.dropin(unit)
                self.manager.properties[unit]['DropInPaths']=('/'+owned.relative_to(self.root).as_posix()) if owned.exists() else ''
                if unit==core.BOT and self.operations.dropin.exists():
                    self.manager.properties[unit]['DropInPaths']+=' /'+self.operations.dropin.relative_to(self.root).as_posix()
            return b''
        return self.native(argv,seconds)
    def step(self,action):
        self.journal.perform(action,getattr(self.operations,action),lambda:self.operations.verify(action))
    def test_candidate_start_is_persisted_before_switch_and_receipt_is_bound(self):
        self.setup_services();self.step('candidate_start')
        self.assertTrue(self.journal.candidate_requested)
        self.assertEqual(self.journal.phase,'candidate_start_done')
        self.assertTrue(self.operations.dropin.exists())
        self.assertFalse(self.fence.permit(core.BOT).exists())
        self.assertTrue(self.fence.present())
        self.assertGreater(self.source_checks,0)
    def test_missing_candidate_admission_keeps_intent_and_fence(self):
        self.setup_services();self.drop_receipt=True
        with self.assertRaises(core.Stop):self.step('candidate_start')
        self.assertEqual(self.journal.phase,'candidate_start_intent')
        self.assertFalse(self.fence.permit(core.BOT).exists())
        self.assertTrue(self.fence.present())
    def test_web_failure_does_not_revert_or_restore_database(self):
        self.setup_services();self.step('candidate_start');self.fail_web=True
        before=self.actual_data.database.read_bytes()
        with self.assertRaises(core.Stop):self.step('web_start')
        self.assertTrue(self.operations.dropin.exists());self.assertTrue(self.fence.present())
        self.assertEqual(self.actual_data.database.read_bytes(),before)
    def test_complete_service_sequence_releases_only_owned_fence(self):
        self.setup_services()
        foreign=self.fence.dropin(core.WEB).parent/'50-foreign.conf';foreign.write_text('[Service]\n')
        for action in ('candidate_start','web_start','release'):self.step(action)
        self.assertEqual(self.journal.phase,'release_done')
        self.assertFalse(self.fence.present());self.assertTrue(foreign.exists());self.assertTrue(self.operations.dropin.exists())
    def test_foreign_candidate_dropin_blocks_without_overwrite(self):
        self.setup_services();self.operations.dropin.parent.mkdir(parents=True,exist_ok=True)
        self.operations.dropin.write_text('foreign')
        with self.assertRaises(core.Stop):self.step('candidate_start')
        self.assertEqual(self.operations.dropin.read_text(),'foreign')
    def test_web_active_without_application_readiness_cannot_complete(self):
        self.setup_services();self.step('candidate_start');self.fail_health=True
        with self.assertRaises(core.Stop):self.step('web_start')
        self.assertEqual(self.journal.phase,'web_start_intent')
        self.assertTrue(self.fence.present())

    def test_rehashed_predecessor_tamper_blocks_web_start(self):
        self.setup_services();self.step('candidate_start')
        path=self.operations.receipts/'candidate_start.json'
        value=jobs.load_signed(path);value['predecessor_sha256']='0'*64
        value.pop('sha256');value['sha256']=core.digest(value);path.write_bytes(core.encoded(value))
        with self.assertRaises(core.Stop):self.step('web_start')
        self.assertNotIn(core.WEB,self.running)

    def test_candidate_source_changed_between_steps_keeps_web_stopped(self):
        self.setup_services();self.step('candidate_start')
        self.operations.source_verifier=lambda:'f'*64
        with self.assertRaises(core.Stop):self.step('web_start')
        self.assertNotIn(core.WEB,self.running)

    def test_late_command_cannot_complete_candidate_step(self):
        self.setup_services();native=self.client.run
        def late(argv,seconds):
            result=native(argv,seconds)
            if argv[:2]==['journalctl','--no-pager']:self.clock[0]+=60
            return result
        self.client.run=late
        with self.assertRaises(core.Stop):self.step('candidate_start')
        self.assertEqual(self.journal.phase,'candidate_start_intent')
        self.assertFalse((self.operations.receipts/'candidate_start.json').exists())

    def test_release_health_failure_retains_fence(self):
        self.setup_services();self.step('candidate_start');self.step('web_start')
        self.fail_health=True
        with self.assertRaises(core.Stop):self.step('release')
        self.assertTrue(self.fence.present())

    def test_changed_candidate_command_blocks_web(self):
        self.setup_services();self.step('candidate_start');native=self.client.run
        def wrong(argv,seconds):
            raw=native(argv,seconds)
            if argv[-1]=='ExecStart':
                value=json.loads(raw);value['data'][0][1].append('--other')
                return json.dumps(value).encode()
            return raw
        self.client.run=wrong
        with self.assertRaises(core.Stop):self.step('web_start')
        self.assertNotIn(core.WEB,self.running)

    def test_web_environment_change_prevents_start(self):
        self.setup_services();self.step('candidate_start');native=self.client.run
        def changed(argv,seconds):
            if argv[0]=='busctl' and 'web' in argv[4] and argv[-1]=='Environment':
                return json.dumps(dict(type='as',data=['PRIVATE=fixture'])).encode()
            return native(argv,seconds)
        self.client.run=changed
        with self.assertRaisesRegex(core.Stop,'web_launch_changed'):self.step('web_start')
        self.assertNotIn(core.WEB,self.running)

    def test_broken_migration_proof_prevents_candidate_switch(self):
        self.setup_services()
        (self.directory/'jobs/migrate.complete.json').unlink()
        with self.assertRaises(core.Stop):self.step('candidate_start')
        self.assertFalse(self.operations.dropin.exists())
        self.assertNotIn(core.BOT,self.running)

    def test_direct_start_without_intent_is_rejected(self):
        self.setup_services()
        with self.assertRaises(core.Stop):self.operations.candidate_start()
        self.assertFalse(self.operations.dropin.exists())

class SourceTests(unittest.TestCase):
    def test_actual_file_bytes_extra_files_and_links_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'one.py').write_bytes(b'value=1\n')
            verifier=services.CandidateFiles.__new__(services.CandidateFiles)
            verifier.path=root;verifier.expected={'one.py':{'bytes':8,'sha256':hashlib.sha256(b'value=1\n').hexdigest()}}
            self.assertEqual(len(verifier()),64)
            (root/'extra.py').write_text('')
            with self.assertRaises(core.Stop):verifier()
            (root/'extra.py').unlink();(root/'one.py').write_bytes(b'value=2\n')
            with self.assertRaises(core.Stop):verifier()
    def test_missing_source_root_is_not_empty_success(self):
        with tempfile.TemporaryDirectory() as directory:
            verifier=services.CandidateFiles.__new__(services.CandidateFiles)
            verifier.path=Path(directory)/'missing';verifier.expected={}
            with self.assertRaises(core.Stop):verifier()


class HttpProbeTests(unittest.TestCase):
    """Execute the rendered probe with Linux procfs/network boundaries substituted."""
    def run_probe(self,*,owner=True,status=200,body=b'<html>ok</html>',network=True):
        class Response:
            def read(self,limit):return body[:limit]
            def getheader(self,*args):return 'text/html'
        Response.status=status
        class Connection:
            requested=False
            def __init__(other,host,port,timeout):
                self.assertEqual((host,port,timeout),('127.0.0.1',3030,4))
            def request(other,*args,**kw):Connection.requested=True;self.assertEqual(args,('GET','/login'))
            def getresponse(other):return Response()
            def close(other):pass
        def link(path):
            if path.endswith('/ns/net'):return 'net:[1]' if network or '/self/' in path else 'net:[2]'
            return 'socket:[123]' if owner else 'socket:[456]'
        tcp=b'header\n0: 0100007F:0BD6 00000000:0000 0A 0 0 0 0 0 123\n'
        import http.client,os,sys
        with patch.object(sys,'argv',['probe','3030','302']),patch.object(os,'readlink',link),\
             patch.object(os,'listdir',return_value=['1']),patch('builtins.open',return_value=io.BytesIO(tcp)),\
             patch.object(http.client,'HTTPConnection',Connection),contextlib.redirect_stdout(io.StringIO()) as output:
            try:exec(compile(services.WEB_HTTP_PROBE,'<probe>','exec'),{})
            except AssertionError:return False,Connection.requested
        return output.getvalue()=='WEB_HTTP_READY',Connection.requested
    def test_success_requires_owned_listener_and_expected_response(self):
        self.assertEqual(self.run_probe(),(True,True))
        self.assertEqual(self.run_probe(owner=False),(False,False))
        self.assertEqual(self.run_probe(network=False),(False,False))
        self.assertEqual(self.run_probe(status=302),(False,True))
        self.assertEqual(self.run_probe(body=b'x'*65537),(False,True))

if __name__=='__main__':unittest.main()
