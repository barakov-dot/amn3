"""Portable stage tests: synthetic bundle contents, fake Linux process executor.
No real SSH, venv, pip, application imports or systemd actions.
"""
import copy
import io
import json
from pathlib import Path
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from scripts.vps import phase16_bot_runtime40_stage_remote as remote
from scripts import phase16_bot_runtime40_stage_gate as gate


def synthetic_bundle():
    source={'app/__init__.py':b'"synthetic"\n','app/main.py':b'raise RuntimeError("must never import")\n'}
    source.update({f'app/fixture{n:03d}.py':b'' for n in range(124)})
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w') as tar:
        for name,body in source.items():
            info=tarfile.TarInfo(name);info.size=len(body);tar.addfile(info,io.BytesIO(body))
    payload={'source.tar':stream.getvalue(),'requirements/phase15-runtime-py312.lock':b'synthetic lock'}
    wheels=[]
    for n in range(48):
        scope='runtime' if n<40 else 'test-only'
        name=f'package{n}';file=f'wheelhouse/{scope}/{name}-1.0-py3-none-any.whl'
        payload[file]=b'synthetic wheel'
        wheels.append(dict(file=file,name=name,version='1.0',scope=scope))
    manifest=dict(source={'file':'source.tar'},wheels=wheels,runtime_wheels=40,test_only_wheels=8)
    return payload,source,manifest


class StageSelectionTests(unittest.TestCase):
    def test_only_runtime_lock_and_wheels_selected_without_test_support(self):
        payload,source,manifest=synthetic_bundle()
        selected,actual,expected=remote.select_runtime(payload,manifest)
        self.assertEqual(actual,source)
        self.assertEqual(len(expected),40)
        self.assertEqual(len(selected),41)
        self.assertFalse(any('test-only' in p or 'test-py312' in p for p in selected))

    def test_runtime48_duplicate_or_unknown_scope_stops(self):
        for mode in ('48','duplicate','scope'):
            payload,source,manifest=synthetic_bundle()
            if mode=='48':
                for w in manifest['wheels']:w['scope']='runtime'
            if mode=='duplicate':manifest['wheels'][1]['name']=manifest['wheels'][0]['name']
            if mode=='scope':manifest['wheels'][0]['scope']='other'
            with self.subTest(mode=mode),self.assertRaises(remote.legacy.GateError):remote.select_runtime(payload,manifest)


class RemoteExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'stage'
        self.payload,self.source,self.manifest=synthetic_bundle()
        self.calls=[]
        self.addCleanup(patch.stopall)
        patch.object(remote,'DESTINATION',self.root).start()
        patch.object(remote,'precheck',return_value=None).start()
        patch.object(remote.legacy,'validate_bundle',return_value=(self.payload,self.source,self.manifest)).start()
        patch.object(remote.legacy,'run_process',side_effect=self.run_child).start()

    def metadata(self):
        site=self.root/'runtime-venv/lib/python3.12/site-packages'
        return dict(executable=str(self.root/'runtime-venv/bin/python'),site_root=str(site),
                    venv_config_correct=True,pth_count=0,
                    packages=[[w['name'],w['version'],True] for w in self.manifest['wheels'] if w['scope']=='runtime']+[['pip','26.0',True]],
                    origins={'app':str(self.root/'source/app/__init__.py'),'app.main':str(self.root/'source/app/main.py')})

    def run_child(self,args,**kw):
        self.calls.append((list(map(str,args)),kw))
        if '--stage-metadata' in args:return 0,json.dumps(self.metadata()).encode()
        return 0,b''

    def test_stage_creates_only_new_tree_and_runs_children_offline(self):
        result=remote.execute(b'fake bundle')
        self.assertEqual(result['status'],'RUNTIME40_STAGED_NOT_ACTIVATED')
        self.assertEqual(result['runtime_pins'],40)
        self.assertEqual(result['app_python_files'],126)
        self.assertEqual([s['step'] for s in result['steps']],remote.STEPS)
        self.assertEqual(result['service_actions'],0)
        self.assertFalse(result['live_database_opened'])
        self.assertTrue((self.root/'claim.json').is_file())
        self.assertTrue((self.root/'result.json').is_file())
        for args,kw in self.calls:
            self.assertEqual(args[:2],['/usr/bin/unshare','--net'])
            self.assertNotIn('TELEGRAM_BOT_TOKEN',kw['env'])
            self.assertNotIn('systemctl',args)
        install=next(args for args,_ in self.calls if 'install' in args)
        self.assertIn('--require-hashes',install)
        self.assertFalse(any('test-only' in a for a in install))
        with self.assertRaises(remote.legacy.GateError):remote.execute(b'fake bundle')

    def test_failure_at_every_child_stops_without_later_commands_or_cleanup(self):
        # Each attempt has its own disposable stage, as a retry may not reuse a claim.
        original_root=self.root
        for index in range(5):
            root=original_root.parent/('failure'+str(index));self.calls=[]
            def failing(args,**kw):
                if len(self.calls)==index:
                    self.calls.append((list(map(str,args)),kw));raise remote.legacy.GateError('process_timeout')
                return self.run_child(args,**kw)
            with self.subTest(index=index),patch.object(remote,'DESTINATION',root),patch.object(remote.legacy,'run_process',side_effect=failing):
                self.root=root
                if index==0:
                    with self.assertRaises(remote.legacy.GateError):remote.execute(b'fake')
                    self.assertFalse(root.exists())
                else:
                    result=remote.execute(b'fake')
                    self.assertEqual(result['status'],'STOP_RETAINED_NO_RETRY')
                    self.assertTrue(root.exists())
                self.assertEqual(len(self.calls),index+1)

    def test_metadata_extra_test_pin_or_bad_origin_never_reports_pass(self):
        for mode in ('test_pin','origin','pth','site','config'):
            self.root=Path(self.temp.name)/mode;self.calls=[]
            good=self.metadata()
            if mode=='test_pin':good['packages'].append(['pytest','9.0',True])
            if mode=='origin':good['origins']['app.main']='/old/runtime/app/main.py'
            if mode=='pth':good['pth_count']=1
            if mode=='site':good['packages'][0][2]=False
            if mode=='config':good['venv_config_correct']=False
            with self.subTest(mode=mode),patch.object(remote,'DESTINATION',self.root),patch.object(self,'metadata',return_value=good):
                result=remote.execute(b'fake')
                self.assertEqual(result['status'],'STOP_RETAINED_NO_RETRY')


class MetadataChildTests(unittest.TestCase):
    def test_exact_metadata_program_uses_pathfinder_without_running_app(self):
        import subprocess,sys
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);venv=root/'venv';site=venv/'lib/python3.12/site-packages';site.mkdir(parents=True)
            (venv/'pyvenv.cfg').write_text('include-system-site-packages = false\n')
            dist=site/'fixture-1.0.dist-info';dist.mkdir();(dist/'METADATA').write_text('Name: fixture\nVersion: 1.0\n')
            source=root/'source';(source/'app').mkdir(parents=True)
            for name in ('__init__.py','main.py'):(source/'app'/name).write_text('raise RuntimeError("APP_MUST_NOT_RUN")\n')
            run=subprocess.run([sys.executable,'-I','-S','-B','-c',remote.METADATA_CODE,'--stage-metadata',str(venv),str(source)],capture_output=True,timeout=10,check=True)
            result=json.loads(run.stdout)
            self.assertEqual(result['origins'],{'app':str(source/'app/__init__.py'),'app.main':str(source/'app/main.py')})
            self.assertEqual(result['packages'],[['fixture','1.0',True]])
            self.assertTrue(result['venv_config_correct'])
            self.assertEqual(run.stderr,b'')

class LocalGateTests(unittest.TestCase):
    def test_render_is_standalone_and_cannot_invoke_old_gate(self):
        script=gate.remote_script()
        compile(script,'<stage-test>','exec')
        namespace={'__name__':'stage_test'}
        exec(compile(script,'<stage-test>','exec'),namespace)
        self.assertEqual(namespace['APPROVAL'],remote.APPROVAL)
        self.assertNotEqual(namespace['APPROVAL'],namespace['legacy'].APPROVAL)

    def test_manifest_is_exact_and_maintenance_stays_blocked(self):
        manifest=gate.expected_manifest()
        self.assertEqual(manifest['maintenance']['status'],'BLOCKED_UNKNOWN_PREREQUISITES')
        self.assertEqual(manifest['maintenance']['writer_inventory'],'UNKNOWN')
        self.assertEqual(manifest['destination'],remote.DESTINATION.as_posix())
        self.assertEqual(gate.validate_manifest(manifest),manifest)
        for key in ('destination','approval','source_commit'):
            bad=copy.deepcopy(manifest);bad[key]='changed'
            with self.assertRaises(remote.legacy.GateError):gate.validate_manifest(bad)

    def test_wire_destination_is_posix_even_on_windows(self):
        self.assertEqual(remote.base_result()['destination'],'/opt/amn2-spain/bot-candidates/'+remote.ARTIFACT_ID)
        self.assertEqual(gate.expected_manifest()['destination'],remote.base_result()['destination'])

    def good_receipt(self):
        result=remote.base_result()
        result.update(status=remote.SUCCESS,seconds=1.0,runtime_pins=40,app_python_files=126,
                      pth_count=0,bootstrap_distributions=1,candidate_import_origins='MATCH_NO_APPLICATION_IMPORT',
                      runtime_lock_sha256=gate.RUNTIME_LOCK_SHA)
        result['steps']=[]
        for name in remote.STEPS:
            step=dict(step=name,returncode=0)
            if name not in ('network_namespace','source_readback'):step.update(output_bytes=0,output_sha256=gate.sha(b''))
            result['steps'].append(step)
        return result

    def test_false_pass_and_extra_output_fields_are_rejected(self):
        value=self.good_receipt();self.assertEqual(gate.validate_receipt(value,0),value)
        variants=[('runtime_pins',48),('service_actions',True),('live_database_opened',True),
                  ('seconds',float('inf')),('status','UNRECOGNIZED'),('raw_log','private-secret'),('steps',[])]
        for key,val in variants:
            bad=copy.deepcopy(value);bad[key]=val
            with self.subTest(field=key),self.assertRaises(remote.legacy.GateError):gate.validate_receipt(bad,0)
        with self.assertRaises(remote.legacy.GateError):gate.validate_receipt(value,3)

    def test_one_claim_one_transport_and_reuse_stops_before_target_loader(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(gate,'EVIDENCE_DIRECTORY',Path(temp)/'execution'),patch.object(gate,'ssh_environment',return_value={}),patch.object(gate.legacy,'validate_bundle'):
            calls=[];binding=SimpleNamespace(role='spain',target_user='root',target_host='fixture.invalid',key_path=Path('fixture-key'),known_hosts_path=Path('fixture-hosts'))
            manifest=gate.expected_manifest();script=gate.remote_script()
            def loader(role):calls.append('loader');return binding
            def transport(*args,**kw):
                self.assertTrue((gate.EVIDENCE_DIRECTORY/'claim.json').is_file())
                calls.append('ssh');return 0,json.dumps(self.good_receipt()).encode()
            kwargs=dict(approval=remote.APPROVAL,approved_remote_sha=gate.sha(script),approved_manifest_sha=gate.sha(gate.encode(manifest)),loader=loader,transport=transport,binding_hasher=lambda b:gate.TARGET_BINDING)
            result=gate.execute_once(b'x',script,manifest,gate.EVIDENCE_DIRECTORY,**kwargs)
            self.assertEqual(result['status'],remote.SUCCESS)
            self.assertEqual(calls,['loader','ssh'])
            with self.assertRaises(remote.legacy.GateError):gate.execute_once(b'x',script,manifest,gate.EVIDENCE_DIRECTORY,**kwargs)
            self.assertEqual(calls,['loader','ssh'])

    def test_approval_hash_and_target_drift_stop_before_ssh_or_claim(self):
        for drift in ('script','manifest','target'):
            with self.subTest(drift=drift),tempfile.TemporaryDirectory() as temp,patch.object(gate,'EVIDENCE_DIRECTORY',Path(temp)/'execution'),patch.object(gate,'ssh_environment',return_value={}),patch.object(gate.legacy,'validate_bundle'):
                calls=[];manifest=gate.expected_manifest();script=gate.remote_script()
                binding=SimpleNamespace(role='spain')
                with self.assertRaises(remote.legacy.GateError):
                    gate.execute_once(b'x',script,manifest,gate.EVIDENCE_DIRECTORY,approval=remote.APPROVAL,
                        approved_remote_sha='0'*64 if drift=='script' else gate.sha(script),
                        approved_manifest_sha='0'*64 if drift=='manifest' else gate.sha(gate.encode(manifest)),
                        loader=lambda role:binding,transport=lambda *a,**kw:calls.append('ssh'),
                        binding_hasher=lambda b:'0'*64 if drift=='target' else gate.TARGET_BINDING)
                self.assertEqual(calls,[])
                self.assertFalse(gate.EVIDENCE_DIRECTORY.exists())

    def test_unsafe_transport_error_is_redacted_and_claim_retained(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(gate,'EVIDENCE_DIRECTORY',Path(temp)/'execution'),patch.object(gate,'ssh_environment',return_value={}),patch.object(gate.legacy,'validate_bundle'):
            binding=SimpleNamespace(role='spain',target_user='root',target_host='fixture.invalid',key_path=Path('fixture-key'),known_hosts_path=Path('fixture-hosts'))
            manifest=gate.expected_manifest();script=gate.remote_script()
            def fail(*args,**kw):raise RuntimeError('private-secret')
            result=gate.execute_once(b'x',script,manifest,gate.EVIDENCE_DIRECTORY,approval=remote.APPROVAL,
                approved_remote_sha=gate.sha(script),approved_manifest_sha=gate.sha(gate.encode(manifest)),
                loader=lambda role:binding,transport=fail,binding_hasher=lambda b:gate.TARGET_BINDING)
            self.assertEqual(result['status'],'UNKNOWN_NO_RETRY')
            self.assertNotIn('private-secret',json.dumps(result))
            self.assertTrue((gate.EVIDENCE_DIRECTORY/'claim.json').exists())

    def test_frame_binds_new_script_approval_and_bundle(self):
        script=gate.remote_script();command,frame=gate.frame_request(script,b'x')
        self.assertIn(remote.APPROVAL,command)
        self.assertEqual(int(frame[:8]),len(script))
        self.assertEqual(frame[8:8+len(script)],script)
        self.assertEqual(frame[-1:],b'x')

    def test_wrong_approval_stops_before_target_loader_or_transport(self):
        with tempfile.TemporaryDirectory() as temp:
            called=[]
            with self.assertRaises(remote.legacy.GateError):
                gate.execute_once(b'x',gate.remote_script(),gate.expected_manifest(),Path(temp)/'evidence',
                                  approval='old approval',approved_remote_sha='0'*64,approved_manifest_sha='0'*64,
                                  loader=lambda role:called.append('loader'),transport=lambda *a,**k:called.append('ssh'))
            self.assertEqual(called,[])

if __name__=='__main__':unittest.main()
