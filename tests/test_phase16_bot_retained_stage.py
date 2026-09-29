"""Offline retained-stage controls; no SSH or real Linux install."""
import copy
import io
import json
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from scripts.vps import phase16_bot_retained_stage_remote as remote
from scripts import phase16_bot_retained_stage_gate as gate
from tests.test_phase16_bot_runtime40_stage import synthetic_bundle


class RetainedValidationTests(unittest.TestCase):
    def fixture(self):
        payload,source,manifest=synthetic_bundle()
        manifest.update(source_commit=remote.legacy.SOURCE_SHA,artifact_id=remote.legacy.ARTIFACT_ID)
        for item in [manifest['source'],*manifest['wheels']]:
            body=payload[item['file']];item.update(size=len(body),sha256=remote.legacy.sha(body))
        manifest['source']['entries']=[dict(path=n,size=len(b),sha256=remote.legacy.sha(b)) for n,b in source.items()]
        name=remote.LOCK;body=payload[name]
        manifest['auxiliary']=[dict(file=name,size=len(body),sha256=remote.legacy.sha(body))]
        raw=json.dumps(manifest).encode();payload['manifest.json']=raw
        return payload,raw

    def validate(self,payload,raw):
        calls=[]
        def read(name,size):
            calls.append(name)
            value=payload[name]
            remote.legacy.require(len(value)==size,'retained_size')
            return value
        with patch.object(remote.legacy,'MANIFEST_SHA',remote.legacy.sha(raw)),patch.object(remote,'MANIFEST_BYTES',len(raw)):
            result=remote.validate_retained(read)
        return result,calls

    def test_only_manifest_source_lock_runtime40_read(self):
        payload,raw=self.fixture();(selected,source,expected),calls=self.validate(payload,raw)
        self.assertEqual(len(calls),43);self.assertEqual(len(selected),41);self.assertEqual(len(expected),40)
        self.assertFalse(any('test-only' in n for n in calls));self.assertIn('app/main.py',source)

    def test_tamper_missing_or_truncated_stops_before_writes(self):
        for mode in ('tamper','missing','truncated'):
            payload,raw=self.fixture();name=next(n for n in payload if n.startswith('wheelhouse/runtime/'))
            if mode=='tamper':payload[name]=b'X'*len(payload[name])
            if mode=='missing':del payload[name]
            if mode=='truncated':payload[name]=payload[name][:-1]
            with self.subTest(mode=mode),self.assertRaises((remote.legacy.GateError,KeyError)):
                self.validate(payload,raw)

    def test_manifest_untrusted_before_any_payload_read(self):
        with self.assertRaises(remote.legacy.GateError):remote.validate_retained(lambda n,s:b'{}')

    def test_source_entry_mismatch_even_with_matching_tar_digest(self):
        payload,raw=self.fixture();m=json.loads(raw);m['source']['entries'][0]['sha256']='0'*64
        raw=json.dumps(m).encode();payload['manifest.json']=raw
        with self.assertRaises(remote.legacy.GateError):self.validate(payload,raw)


class DescriptorTests(unittest.TestCase):
    def metadata(self,**changes):
        values=dict(st_mode=stat.S_IFREG|0o600,st_uid=0,st_gid=0,st_nlink=1,st_size=3,
                    st_dev=1,st_ino=2,st_mtime_ns=10,st_ctime_ns=10)
        values.update(changes);return SimpleNamespace(**values)

    def fake_os(self):
        from unittest.mock import Mock
        api=Mock()
        api.O_RDONLY=0;api.O_DIRECTORY=1;api.O_NOFOLLOW=2;api.O_CLOEXEC=4;api.O_NONBLOCK=8
        api.open.return_value=20;api.fstat.return_value=self.metadata();api.stat.return_value=self.metadata()
        api.read.side_effect=[b'abc',b'']
        return api

    def test_descriptor_read_uses_nofollow_nonblock_and_exact_bytes(self):
        api=self.fake_os();reader=remote.SecureReader('/fixed',syscalls=api);reader.root_fd=10
        self.assertEqual(reader.read('file',3),b'abc')
        self.assertEqual(api.open.call_args.kwargs,{'dir_fd':10})
        self.assertEqual(api.open.call_args.args[1]&10,10)
        api.close.assert_called_once_with(20)

    def test_links_permissions_owner_types_sizes_and_race_rejected(self):
        bads=[dict(st_nlink=2),dict(st_uid=1),dict(st_mode=stat.S_IFREG|0o622),
              dict(st_mode=stat.S_IFLNK|0o777),dict(st_mode=stat.S_IFIFO|0o600),dict(st_size=4)]
        for bad in bads:
            api=self.fake_os();api.fstat.return_value=self.metadata(**bad)
            reader=remote.SecureReader('/fixed',syscalls=api);reader.root_fd=10
            with self.subTest(bad=bad),self.assertRaises(remote.legacy.GateError):reader.read('file',3)
            api.read.assert_not_called();api.close.assert_called_once_with(20)
        for mode in ('changed_fd','replaced_name','short','extra'):
            api=self.fake_os()
            if mode=='changed_fd':api.fstat.side_effect=[self.metadata(),self.metadata(st_ctime_ns=11)]
            if mode=='replaced_name':api.stat.return_value=self.metadata(st_ino=3)
            if mode=='short':api.read.side_effect=[b'ab',b'']
            if mode=='extra':api.read.side_effect=[b'abcd',b'']
            reader=remote.SecureReader('/fixed',syscalls=api);reader.root_fd=10
            with self.subTest(mode=mode),self.assertRaises(remote.legacy.GateError):reader.read('file',3)

    def test_traversal_absolute_and_backslash_rejected_without_open(self):
        for name in ('../file','/file','a/../file','a\\file','a//file'):
            api=self.fake_os();reader=remote.SecureReader('/fixed',syscalls=api);reader.root_fd=10
            with self.subTest(name=name),self.assertRaises(remote.legacy.GateError):reader.read(name,3)
            api.open.assert_not_called()


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'new-stage'
        payload,source,manifest=synthetic_bundle()
        self.selected,self.source,self.expected=remote.stage.select_runtime(payload,manifest)
        self.calls=[];self.addCleanup(patch.stopall)
        patch.object(remote,'DESTINATION',self.root).start()
        patch.object(remote,'precheck').start()
        self.read=patch.object(remote,'read_retained',return_value=(self.selected,self.source,self.expected)).start()
        patch.object(remote.legacy,'run_process',side_effect=self.child).start()

    def child(self,args,**kwargs):
        self.calls.append((list(map(str,args)),kwargs))
        if '--stage-metadata' in args:
            site=self.root/'runtime-venv/lib/python3.12/site-packages'
            return 0,json.dumps(dict(executable=str(self.root/'runtime-venv/bin/python'),site_root=str(site),
                venv_config_correct=True,pth_count=0,packages=[[n,v,True] for n,v in self.expected.items()],
                origins={'app':str(self.root/'source/app/__init__.py'),'app.main':str(self.root/'source/app/main.py')})).encode()
        return 0,b''

    def test_verified_bytes_only_new_private_stage_offline_no_services(self):
        result=remote.execute();self.assertEqual(result['status'],remote.SUCCESS)
        self.assertEqual(result['retained_files_verified'],43);self.assertFalse(result['retained_payload_modified'])
        self.assertEqual(len(self.calls),5);self.assertFalse(result['runtime_activation'])
        for args,kw in self.calls:
            self.assertEqual(args[:2],['/usr/bin/unshare','--net'])
            self.assertFalse(any(str(remote.RETAINED) in s or 'systemctl' in s for s in args))
        self.assertEqual((self.root/'source/app/main.py').read_bytes(),self.source['app/main.py'])
        with self.assertRaises(remote.legacy.GateError):remote.execute()

    def test_missing_or_drift_stops_before_claim_and_subprocess(self):
        self.read.side_effect=remote.legacy.GateError('retained_hash')
        with self.assertRaises(remote.legacy.GateError):remote.execute()
        self.assertFalse(self.root.exists());self.assertEqual(self.calls,[])

    def test_install_failure_retained_no_retry_or_later_children(self):
        original=self.child
        def fail(args,**kw):
            if 'install' in args:raise remote.legacy.GateError('process_timeout')
            return original(args,**kw)
        with patch.object(remote.legacy,'run_process',side_effect=fail):result=remote.execute()
        self.assertEqual(result['status'],'STOP_RETAINED_NO_RETRY');self.assertTrue(self.root.exists())
        self.assertEqual(len(self.calls),2)
        self.assertFalse((self.root/'runtime-venv').exists())



    def test_failure_at_every_child_stops_and_existing_directory_never_reused(self):
        original_root=self.root
        for index in range(5):
            self.root=original_root.parent/('child-failure-'+str(index));self.calls=[]
            def fail(args,**kw):
                if len(self.calls)==index:
                    self.calls.append((list(map(str,args)),kw));raise remote.legacy.GateError('process_timeout')
                return self.child(args,**kw)
            with self.subTest(index=index),patch.object(remote,'DESTINATION',self.root),patch.object(remote.legacy,'run_process',side_effect=fail):
                if index==0:
                    with self.assertRaises(remote.legacy.GateError):remote.execute()
                    self.assertFalse(self.root.exists())
                else:
                    result=remote.execute();self.assertEqual(result['status'],'STOP_RETAINED_NO_RETRY')
                    self.assertTrue((self.root/'result.json').is_file())
                    with self.assertRaises(remote.legacy.GateError):remote.execute()
                self.assertEqual(len(self.calls),index+1)

    def test_bad_metadata_dependency_or_app_origin_never_accepts_stage(self):
        original_root=self.root
        for mode in ('extra_dependency','origin','pth'):
            self.root=original_root.parent/mode;self.calls=[]
            def child(args,**kw):
                rc,out=self.child(args,**kw)
                if '--stage-metadata' in args:
                    value=json.loads(out)
                    if mode=='extra_dependency':value['packages'].append(['pytest','9',True])
                    if mode=='origin':value['origins']['app.main']='/old/app/main.py'
                    if mode=='pth':value['pth_count']=1
                    out=json.dumps(value).encode()
                return rc,out
            with self.subTest(mode=mode),patch.object(remote,'DESTINATION',self.root),patch.object(remote.legacy,'run_process',side_effect=child):
                result=remote.execute();self.assertEqual(result['status'],'STOP_RETAINED_NO_RETRY')
                self.assertNotIn('source_readback',[s['step'] for s in result['steps']])


class GateTests(unittest.TestCase):
    def receipt(self):
        value=remote.base_result();value.update(status=remote.SUCCESS,seconds=1.0,runtime_pins=40,
            app_python_files=126,pth_count=0,bootstrap_distributions=1,
            candidate_import_origins='MATCH_NO_APPLICATION_IMPORT',runtime_lock_sha256=gate.RUNTIME_LOCK_SHA,
            retained_files_verified=43)
        for step in remote.STEPS:
            item=dict(step=step,returncode=0)
            if step not in ('network_namespace','source_readback'):item.update(output_bytes=0,output_sha256=gate.sha(b''))
            value['steps'].append(item)
        return value

    def fixture(self):
        binding=SimpleNamespace(role='spain',target_user='root',target_host='fixture.invalid',
                                key_path=Path('fixture-key'),known_hosts_path=Path('fixture-hosts'))
        manifest=gate.expected_manifest();script=gate.remote_script()
        kwargs=dict(approval=remote.APPROVAL,approved_remote_sha=gate.sha(script),
                    approved_manifest_sha=gate.sha(gate.encode(manifest)),loader=lambda r:binding,
                    binding_hasher=lambda b:gate.TARGET_BINDING)
        return script,manifest,kwargs

    def test_render_has_new_bindings_and_never_invokes_frozen_entrypoints(self):
        namespace={'__name__':'offline_test'};exec(compile(gate.remote_script(),'<test>','exec'),namespace)
        self.assertEqual(namespace['APPROVAL'],remote.APPROVAL)
        self.assertNotEqual(namespace['APPROVAL'],namespace['stage'].APPROVAL)
        self.assertNotEqual(namespace['DESTINATION'],namespace['stage'].DESTINATION)
        self.assertLess(len(gate.remote_script()),65536)
        self.assertIs(namespace['stage'].legacy,namespace['legacy'])

    def test_real_local_bootstrap_exact_partial_corrupt_extra_and_wrong_approval(self):
        import shlex,subprocess,sys
        command,frame=gate.frame_request(gate.remote_script());bootstrap=shlex.split(command)[5]
        # All controls use a wrong marker or fail frame validation. No Linux execution.
        for mode,data in [('full',frame),('partial',frame[:-1]),('corrupt',frame[:20]+b'X'+frame[21:]),('extra',frame+b'x')]:
            approval=remote.APPROVAL if mode=='extra' else 'NOT_AUTHORIZED'
            run=subprocess.run([sys.executable,'-I','-S','-B','-c',bootstrap,approval],input=data,capture_output=True,timeout=10)
            with self.subTest(mode=mode):
                if mode in ('partial','corrupt'):self.assertEqual(run.returncode,70);self.assertEqual(run.stdout,b'')
                else:
                    self.assertEqual(run.returncode,3);v=json.loads(run.stdout)
                    self.assertEqual(v['reason'],'unexpected_input' if mode=='extra' else 'approval_argument')
                    self.assertEqual(v['retained_files_verified'],0)
                self.assertEqual(run.stderr,b'')

    def test_manifest_exact_type_binding(self):
        m=gate.expected_manifest();self.assertEqual(gate.validate_manifest(m),m)
        for path in ('approval','destination','target_binding_sha256'):
            bad=copy.deepcopy(m);bad[path]='changed'
            with self.assertRaises(remote.legacy.GateError):gate.validate_manifest(bad)
        bad=copy.deepcopy(m);bad['scope']['service_actions']=False
        with self.assertRaises(remote.legacy.GateError):gate.validate_manifest(bad)

    def test_false_success_duplicate_and_extra_fields_rejected(self):
        value=self.receipt();self.assertEqual(gate.validate_receipt(value,0),value)
        for key,changed in [('retained_files_verified',0),('retained_payload','/wrong'),('runtime_pins',48),
            ('service_actions',True),('retained_payload_modified',True),('steps',[]),('raw_log','secret'),('seconds',float('nan'))]:
            bad=copy.deepcopy(value);bad[key]=changed
            with self.subTest(key=key),self.assertRaises(remote.legacy.GateError):gate.validate_receipt(bad,0)
        with self.assertRaises(remote.legacy.GateError):gate.strict_json(b'{"a":1,"a":2}')

    def test_stop_receipt_claim_boundary_and_no_post_failure_steps(self):
        value=remote.base_result();value['reason']='retained_io'
        self.assertEqual(gate.validate_receipt(value,3),value)
        value['retained_files_verified']=43
        with self.assertRaises(remote.legacy.GateError):gate.validate_receipt(value,3)
        value=self.receipt();value.update(status='STOP_RETAINED_NO_RETRY',reason='offline_install_exit')
        value['steps'][2]['returncode']=1
        with self.assertRaises(remote.legacy.GateError):gate.validate_receipt(value,3)
        value['steps']=value['steps'][:3]
        self.assertEqual(gate.validate_receipt(value,3),value)

    def test_one_claim_one_ssh_and_reuse_before_target_loader(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(gate,'EVIDENCE_DIRECTORY',Path(temp)/'evidence'),patch.object(gate,'ssh_environment',return_value={}):
            script,m,kw=self.fixture();calls=[];original=kw['loader']
            def loader(role):calls.append('loader');return original(role)
            kw['loader']=loader
            def transport(*args,**kwargs):
                calls.append('ssh');self.assertTrue((gate.EVIDENCE_DIRECTORY/'claim.json').exists())
                self.assertEqual(len(kwargs['input_bytes']),len(script)+8)
                self.assertIn('ServerAliveCountMax=1',args[0])
                kwargs['diagnostics'].update(stdin_complete=True,output_complete=True)
                return 0,json.dumps(self.receipt()).encode()
            result=gate.execute_once(script,m,gate.EVIDENCE_DIRECTORY,transport=transport,**kw)
            self.assertEqual(result['status'],remote.SUCCESS);self.assertEqual(calls,['loader','ssh'])
            with self.assertRaises(remote.legacy.GateError):gate.execute_once(script,m,gate.EVIDENCE_DIRECTORY,transport=transport,**kw)
            self.assertEqual(calls,['loader','ssh'])

    def test_wrong_approval_manifest_script_target_or_path_no_ssh(self):
        for mode in ('approval','manifest','script','target','path'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as temp,patch.object(gate,'EVIDENCE_DIRECTORY',Path(temp)/'evidence'),patch.object(gate,'ssh_environment',return_value={}):
                script,m,kw=self.fixture();called=[];evidence=gate.EVIDENCE_DIRECTORY
                if mode=='approval':kw['approval']='old'
                if mode=='manifest':kw['approved_manifest_sha']='0'*64
                if mode=='script':kw['approved_remote_sha']='0'*64
                if mode=='target':kw['binding_hasher']=lambda b:'0'*64
                if mode=='path':evidence=Path(temp)/'other'
                with self.assertRaises(remote.legacy.GateError):gate.execute_once(script,m,evidence,transport=lambda *a,**k:called.append('ssh'),**kw)
                self.assertEqual(called,[]);self.assertFalse(evidence.exists())

    def test_transport_failure_or_incomplete_receipt_unknown_and_redacted(self):
        for mode in ('failure','incomplete','false_receipt'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as temp,patch.object(gate,'EVIDENCE_DIRECTORY',Path(temp)/'evidence'),patch.object(gate,'ssh_environment',return_value={}):
                script,m,kw=self.fixture()
                def transport(*a,**k):
                    if mode=='failure':raise RuntimeError('private-secret')
                    k['diagnostics'].update(stdin_complete=mode!='incomplete',output_complete=True)
                    value=self.receipt()
                    if mode=='false_receipt':value['secret']='private-secret'
                    return 0,json.dumps(value).encode()
                result=gate.execute_once(script,m,gate.EVIDENCE_DIRECTORY,transport=transport,**kw)
                self.assertEqual(result['status'],'UNKNOWN_NO_RETRY');self.assertNotIn('private-secret',json.dumps(result))
                self.assertTrue((gate.EVIDENCE_DIRECTORY/'claim.json').is_file())

    def test_preview_no_target_or_network_or_evidence(self):
        value=gate.preview(gate.expected_manifest())
        self.assertEqual(value['ssh_attempts'],0);self.assertEqual(value['bundle_upload_bytes'],0)
        self.assertEqual(value['frame_bytes'],len(gate.remote_script())+8)


class AncestorTests(unittest.TestCase):
    metadata=DescriptorTests.metadata
    fake_os=DescriptorTests.fake_os
    def test_root_and_all_ancestors_are_pinned_and_closed(self):
        api=self.fake_os();meta=self.metadata(st_mode=stat.S_IFDIR|0o755,st_nlink=2)
        api.open.side_effect=[10,11,12];api.fstat.return_value=meta;api.stat.return_value=meta
        with remote.SecureReader('/a/b',syscalls=api) as reader:self.assertEqual(reader.root_fd,12)
        self.assertEqual([call.args[0] for call in api.open.call_args_list],['/','a','b'])
        self.assertEqual([call.args[0] for call in api.close.call_args_list],[12,11,10])
        for call in api.open.call_args_list:self.assertEqual(call.args[1]&3,3)

    def test_untrusted_ancestor_or_swapped_directory_closes_all_descriptors(self):
        for mode in ('owner','permissions','link','swap'):
            api=self.fake_os();meta=self.metadata(st_mode=stat.S_IFDIR|0o755,st_nlink=2)
            bad=copy.copy(meta)
            if mode=='owner':bad.st_uid=1
            if mode=='permissions':bad.st_mode|=0o020
            if mode=='link':bad.st_mode=stat.S_IFLNK|0o777
            api.open.side_effect=[10,11];api.fstat.side_effect=[meta,bad] if mode!='swap' else None
            if mode=='swap':api.fstat.return_value=meta;api.stat.return_value=self.metadata(st_ino=9)
            with self.subTest(mode=mode),self.assertRaises(remote.legacy.GateError):
                with remote.SecureReader('/a',syscalls=api):pass
            self.assertEqual([call.args[0] for call in api.close.call_args_list],[11,10])

if __name__=='__main__':unittest.main()
