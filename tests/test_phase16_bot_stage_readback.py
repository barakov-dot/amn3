"""Readback tests: fixtures only, no SSH or application execution."""
import copy
import importlib.util
import json
from pathlib import Path, PurePosixPath
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


def modules():
    from scripts.vps import phase16_bot_stage_readback_remote as remote
    from scripts import phase16_bot_stage_readback_gate as gate
    return remote,gate


class Fixture:
    def __init__(self,remote):
        from tests.test_phase16_bot_retained_stage import GateTests
        self.remote=remote;self.root=remote.DESTINATION
        self.files={};self.calls=[];self.missing_root=False;self.metadata_extra=False
        self.pins={f'package{n}':'1.0' for n in range(40)}
        self.files['claim.json']=json.dumps(dict(approval=remote.STAGE_APPROVAL,artifact_id=remote.ARTIFACT_ID,
            bundle_sha256=remote.BUNDLE_SHA,attempts=1)).encode()
        self.files['result.json']=json.dumps(GateTests().receipt()).encode()
        content={'source/app/__init__.py':b'raise RuntimeError("NEVER_IMPORT")',
                 'source/app/main.py':b'raise RuntimeError("NEVER_IMPORT")'}
        content.update({f'source/app/f{n}.py':b'x=1' for n in range(124)})
        content.update({f'source/doc{n}.txt':b'x' for n in range(33)})
        content['payload/requirements/phase15-runtime-py312.lock']=b'fixture lock'
        content.update({f'payload/wheelhouse/runtime/package{n}.whl':b'wheel' for n in range(40)})
        self.files.update(content)
        self.inventory={'files':{n:[len(b),remote.legacy.sha(b)] for n,b in content.items()},'pins':self.pins}
        self.files['runtime-venv/pyvenv.cfg']=b'home = /usr/bin\ninclude-system-site-packages = false\n'
        for n,v in self.pins.items():
            self.files['runtime-venv/lib/python3.12/site-packages/'+n+'-1.0.dist-info/METADATA']=f'Name: {n}\nVersion: {v}\n'.encode()
        self.links={'runtime-venv/bin/python':'python3','runtime-venv/bin/python3':'/usr/bin/python3',
                    'runtime-venv/bin/python3.12':'python3'}

    def reader(self,path):
        fixture=self
        class Reader:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def info(self,name):
                fixture.calls.append(('info',str(path),name))
                if PurePosixPath(path)==fixture.root.parent:
                    if fixture.missing_root:raise FileNotFoundError()
                    return SimpleNamespace(st_mode=stat.S_IFDIR|0o700,st_uid=0)
                raise AssertionError('unexpected info')
            def read_file(self,name,maximum,expected_size=None):
                fixture.calls.append(('read',str(path),name))
                if name not in fixture.files:raise FileNotFoundError()
                b=fixture.files[name]
                fixture.remote.legacy.require(len(b)<=maximum and (expected_size is None or len(b)==expected_size),'retained_size')
                return b
            def file_set(self,prefix):
                fixture.calls.append(('list',str(path),prefix))
                return {n for n in fixture.files if n.startswith(prefix+'/')}
            def metadata_files(self):
                return {n:self.read_file(n,1048576) for n in fixture.files if n.startswith('runtime-venv/lib/python3.12/site-packages/') and n.endswith('/METADATA')}
            def interpreter_links(self):return copy.deepcopy(fixture.links)
            def stable(self):return None
        return Reader()


class ReadbackTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('scripts.vps.phase16_bot_stage_readback_remote'),
                             'Read-only stage readback is not implemented')
        self.remote,self.gate=modules();self.fixture=Fixture(self.remote)

    def observe(self):
        self.events=[]
        return self.remote.observe(self.fixture.inventory,reader_factory=self.fixture.reader,emit=self.events.append)

    def test_verified_requires_receipt_current_content_and_metadata_without_import(self):
        result=self.observe();self.assertEqual(result['status'],'VERIFIED')
        self.assertEqual(result['verified_files'],200);self.assertEqual(result['runtime_pins'],40)
        self.assertFalse(result['activation']);self.assertEqual(result['writes'],0)
        self.assertEqual([e['event'] for e in self.events],['RECEIPT','CONTENT','METADATA'])
        self.assertFalse(any('/payload' in root and 'candidate-20260921' in root for _,root,_ in self.fixture.calls))

    def test_absent_only_after_parent_observed(self):
        self.fixture.missing_root=True;result=self.observe()
        self.assertEqual(result['status'],'ABSENT');self.assertFalse(any(c[0]=='read' for c in self.fixture.calls))

    def test_missing_receipt_or_file_incomplete_not_verified(self):
        for name in ('claim.json','result.json','source/app/main.py'):
            with self.subTest(name=name):
                self.fixture=Fixture(self.remote);del self.fixture.files[name]
                self.assertEqual(self.observe()['status'],'INCOMPLETE')

    def test_hash_drift_or_extra_source_cannot_verify(self):
        for mode in ('hash','extra'):
            self.fixture=Fixture(self.remote)
            if mode=='hash':self.fixture.files['source/app/main.py']=b'x'*len(self.fixture.files['source/app/main.py'])
            else:self.fixture.files['source/unexpected.py']=b'raise RuntimeError()'
            with self.subTest(mode=mode):self.assertEqual(self.observe()['status'],'INCOMPLETE')

    def test_false_or_duplicate_receipt_is_incomplete(self):
        for mode in ('duplicate','approval','count','stop'):
            self.fixture=Fixture(self.remote);v=json.loads(self.fixture.files['result.json'])
            if mode=='duplicate':self.fixture.files['result.json']=b'{"status":0,"status":1}'
            else:
                if mode=='approval':v['approval']='other'
                if mode=='count':v['runtime_pins']=48
                if mode=='stop':v['status']='STOP_RETAINED_NO_RETRY';v['reason']='metadata_exit'
                self.fixture.files['result.json']=json.dumps(v).encode()
            with self.subTest(mode=mode):self.assertEqual(self.observe()['status'],'INCOMPLETE')

    def test_metadata_extra_pin_bad_version_or_duplicate_name_stops(self):
        base='runtime-venv/lib/python3.12/site-packages/'
        for mode in ('extra','version','duplicate'):
            self.fixture=Fixture(self.remote)
            name=base+('pytest-9.dist-info/METADATA' if mode=='extra' else 'other.dist-info/METADATA')
            self.fixture.files[name]=b'Name: pytest\nVersion: 9\n' if mode=='extra' else b'Name: package0\nVersion: 2\n'
            if mode=='version':del self.fixture.files[base+'package0-1.0.dist-info/METADATA']
            with self.subTest(mode=mode):self.assertEqual(self.observe()['status'],'INCOMPLETE')

    def test_venv_config_or_interpreter_link_drift_stops(self):
        for mode in ('config','link'):
            self.fixture=Fixture(self.remote)
            if mode=='config':self.fixture.files['runtime-venv/pyvenv.cfg']=b'include-system-site-packages = true\n'
            else:self.fixture.links['runtime-venv/bin/python']='../../outside'
            with self.subTest(mode=mode):self.assertEqual(self.observe()['status'],'INCOMPLETE')

    def test_every_observed_outcome_roundtrips_strict_event_parser(self):
        for mode in ('verified','absent','missing','hash','metadata','unknown'):
            self.fixture=Fixture(self.remote)
            if mode=='absent':self.fixture.missing_root=True
            if mode=='missing':del self.fixture.files['result.json']
            if mode=='hash':self.fixture.files['source/app/main.py']=b'z'*len(self.fixture.files['source/app/main.py'])
            if mode=='metadata':self.fixture.files['runtime-venv/pyvenv.cfg']=b'include-system-site-packages = true'
            reader=self.fixture.reader
            if mode=='unknown':reader=lambda path:(_ for _ in ()).throw(PermissionError())
            events=[dict(schema=self.remote.SCHEMA,approval=self.remote.APPROVAL,seq=0,event='READY')]
            def emit(event):events.append(dict(schema=self.remote.SCHEMA,approval=self.remote.APPROVAL,seq=len(events),**event))
            value=self.remote.observe(self.fixture.inventory,reader_factory=reader,emit=emit)
            emit({'event':'RESULT','result':value})
            with self.subTest(mode=mode):
                parsed=self.gate.parse_events(b''.join(json.dumps(e).encode()+b'\n' for e in events))
                self.assertEqual(parsed['result'],value)

    def test_unexpected_error_redacted_unknown(self):
        def denied(path):raise PermissionError('private-secret')
        value=self.remote.observe(self.fixture.inventory,reader_factory=denied)
        self.assertEqual(value['status'],'UNKNOWN');self.assertNotIn('private-secret',json.dumps(value))



class GateTests(unittest.TestCase):
    def setUp(self):self.remote,self.gate=modules()

    def events(self,status='VERIFIED'):
        result=self.remote.base_result()
        names=['READY']
        if status=='VERIFIED':
            names+=['RECEIPT','CONTENT','METADATA'];result.update(status=status,reason='receipt_content_metadata_match',
                verified_files=200,runtime_pins=40,bootstrap_distributions=1,saved_receipt_sha256='a'*64)
        else:result.update(status='ABSENT',reason='directory_absent')
        events=[dict(schema=self.remote.SCHEMA,approval=self.remote.APPROVAL,seq=i,event=name) for i,name in enumerate(names)]
        events.append(dict(schema=self.remote.SCHEMA,approval=self.remote.APPROVAL,seq=len(events),event='RESULT',result=result))
        return events

    def wire(self,events):return b''.join(json.dumps(e).encode()+b'\n' for e in events)

    def test_real_windows_child_uses_bound_argv_with_devnull_stdin(self):
        import shlex,subprocess,sys
        script=self.gate.remote_script();command,payload=self.gate.wire_request(script)
        self.assertEqual(payload,b'');self.assertNotIn('sys.stdin',script.decode())
        bootstrap=shlex.split(command)[5]
        self.assertLess(self.gate.command_units([sys.executable,'-I','-S','-B','-c',bootstrap,self.remote.APPROVAL]),30000)
        run=subprocess.run([sys.executable,'-I','-S','-B','-c',bootstrap,self.remote.APPROVAL],stdin=subprocess.DEVNULL,capture_output=True,timeout=10)
        self.assertEqual(run.returncode,3);self.assertEqual(run.stderr,b'')
        result=self.gate.parse_events(run.stdout)
        self.assertEqual(result['status'],'COMPLETE');self.assertEqual(result['result']['reason'],'platform_python')
        self.assertEqual(result['result']['writes'],0)
        # A corrupt compressed binding must exit before executing the readback.
        import hashlib,zlib
        digest=hashlib.sha256(zlib.compress(script,9)).hexdigest()
        bad=bootstrap.replace(digest,'0'*64)
        run=subprocess.run([sys.executable,'-I','-S','-B','-c',bad,self.remote.APPROVAL],stdin=subprocess.DEVNULL,capture_output=True,timeout=10)
        self.assertEqual((run.returncode,run.stdout,run.stderr),(70,b'',b''))

    def test_render_contains_readers_and_validator_but_no_install_entrypoints(self):
        import ast
        script=self.gate.remote_script();ns={'__name__':'offline_test'};exec(compile(script,'<test>','exec'),ns)
        self.assertEqual(ns['INVENTORY'],self.gate.inventory())
        self.assertFalse(hasattr(ns['legacy'],'run_process'))
        self.assertFalse(hasattr(ns['legacy'],'write_tree'))
        self.assertFalse(hasattr(ns['staged'],'execute_once'))
        imports={a.name for node in ast.walk(ast.parse(script)) if isinstance(node,ast.Import) for a in node.names}
        self.assertFalse(imports&{'subprocess','socket','sqlite3','requests'})

    def test_command_cap_fails_closed(self):
        with patch.object(self.gate,'MAX_COMMAND_UNITS',100):
            with self.assertRaises(self.remote.legacy.GateError):self.gate.wire_request(self.gate.remote_script())

    def test_false_success_unknown_fields_boolean_and_wrong_order_rejected(self):
        good=self.events();self.assertEqual(self.gate.parse_events(self.wire(good))['result']['status'],'VERIFIED')
        for mode in ('count','boolean','extra','order','prefix','rc_fields','tail'):
            events=copy.deepcopy(good)
            if mode=='count':events[-1]['result']['verified_files']=199
            if mode=='boolean':events[-1]['result']['writes']=False
            if mode=='extra':events[-1]['result']['raw_log']='private-secret'
            if mode=='order':events[1]['event']='METADATA'
            if mode=='prefix':events=events[-1:];events[0]['seq']=0
            if mode=='rc_fields':events[0]['seq']=False
            data=self.wire(events)+(b'junk' if mode=='tail' else b'')
            with self.subTest(mode=mode),self.assertRaises(Exception):self.gate.parse_events(data)
        with self.assertRaises(Exception):self.gate.parse_events(b'{"schema":1,"schema":2}\n')

    def test_prefix_is_preserved_without_false_absent_or_verified(self):
        events=self.events();value=self.gate.parse_events(self.wire(events[:2])+b'{partial')
        self.assertEqual(value['status'],'PREFIX_ONLY');self.assertTrue(value['trailing_fragment']);self.assertIsNone(value['result'])

    def fixture(self):
        binding=SimpleNamespace(role='spain',target_user='root',target_host='fixture.invalid',key_path=Path('fixture-key'),known_hosts_path=Path('fixture-hosts'))
        m=self.gate.expected_manifest()
        return m,dict(approval=self.remote.APPROVAL,approved_remote_sha=self.gate.sha(self.gate.remote_script()),
            approved_manifest_sha=self.gate.sha(self.gate.encode(m)),loader=lambda role:binding,
            binding_hasher=lambda b:self.gate.TARGET_BINDING)

    def test_one_claim_one_ssh_zero_input_and_changed_per_command_count(self):
        with tempfile.TemporaryDirectory() as t,patch.object(self.gate,'EVIDENCE_DIRECTORY',Path(t)/'evidence'),patch.object(self.gate,'ssh_environment',return_value={}):
            m,kw=self.fixture();called=[];original=kw['loader']
            def loader(role):called.append('loader');return original(role)
            kw['loader']=loader
            def transport(args,**kwargs):
                called.append('ssh');self.assertIn('-n',args);self.assertIn('ServerAliveCountMax=6',args)
                self.assertEqual(kwargs['input_bytes'],b'');self.assertEqual(kwargs['timeout'],60)
                self.assertTrue((self.gate.EVIDENCE_DIRECTORY/'claim.json').is_file())
                kwargs['diagnostics'].update(stdin_complete=True,output_complete=True)
                return 0,self.wire(self.events())
            result=self.gate.execute_once(m,transport=transport,**kw)
            self.assertEqual(result['status'],'VERIFIED_NOT_ACTIVATED');self.assertEqual(called,['loader','ssh'])
            with self.assertRaises(self.remote.legacy.GateError):self.gate.execute_once(m,transport=transport,**kw)
            self.assertEqual(called,['loader','ssh'])

    def test_manifest_hash_target_drift_stops_before_claim_or_ssh(self):
        for mode in ('approval','script','manifest','target','inventory'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as t,patch.object(self.gate,'EVIDENCE_DIRECTORY',Path(t)/'evidence'),patch.object(self.gate,'ssh_environment',return_value={}):
                m,kw=self.fixture();called=[]
                if mode=='approval':kw['approval']='old'
                if mode=='script':kw['approved_remote_sha']='0'*64
                if mode=='manifest':m['scope']['install']=True
                if mode=='target':kw['binding_hasher']=lambda b:'0'*64
                context=patch.object(self.gate,'INVENTORY_SHA','0'*64) if mode=='inventory' else patch.object(self.gate,'TARGET_BINDING',self.gate.TARGET_BINDING)
                with context,self.assertRaises(self.remote.legacy.GateError):self.gate.execute_once(m,transport=lambda *a,**k:called.append('ssh'),**kw)
                self.assertEqual(called,[]);self.assertFalse(self.gate.EVIDENCE_DIRECTORY.exists())

    def test_transport_failure_keeps_sanitized_prefix_and_no_retry(self):
        with tempfile.TemporaryDirectory() as t,patch.object(self.gate,'EVIDENCE_DIRECTORY',Path(t)/'evidence'),patch.object(self.gate,'ssh_environment',return_value={}):
            m,kw=self.fixture()
            def transport(*args,**kwargs):
                kwargs['stdout_observer'](self.wire(self.events()[:2]))
                raise RuntimeError('private-secret')
            result=self.gate.execute_once(m,transport=transport,**kw)
            self.assertEqual(result['status'],'UNKNOWN_NO_RETRY');self.assertEqual(result['remote_observation']['status'],'PREFIX_ONLY')
            self.assertNotIn('private-secret',json.dumps(result))

    def test_incomplete_transport_or_exit_mismatch_never_accepts_terminal(self):
        for mode in ('pipe','rc'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as t,patch.object(self.gate,'EVIDENCE_DIRECTORY',Path(t)/'evidence'),patch.object(self.gate,'ssh_environment',return_value={}):
                m,kw=self.fixture()
                def transport(*args,**kwargs):
                    kwargs['diagnostics'].update(stdin_complete=True,output_complete=mode!='pipe')
                    return (255 if mode=='rc' else 0),self.wire(self.events())
                self.assertEqual(self.gate.execute_once(m,transport=transport,**kw)['status'],'UNKNOWN_NO_RETRY')


class BoundTreeTests(unittest.TestCase):
    def setUp(self):self.remote,self.gate=modules()

    def api(self):
        from tests.test_phase16_bot_retained_stage import DescriptorTests
        helper=DescriptorTests();return helper.fake_os(),helper.metadata

    def test_reader_checks_actual_flags_regular_file_and_changed_name(self):
        api,meta=self.api();tree=self.remote.BoundTree('/fixed',syscalls=api);tree.root_fd=10
        self.assertEqual(tree.read_file('file',3),b'abc')
        self.assertTrue(api.open.call_args.args[1]&api.O_NOFOLLOW);self.assertTrue(api.open.call_args.args[1]&api.O_NONBLOCK)
        api.stat.return_value=meta(st_ino=9)
        with self.assertRaises(self.remote.legacy.GateError):tree.stable()

    def test_directory_descriptor_closed_on_body_error(self):
        api,meta=self.api();directory=meta(st_mode=stat.S_IFDIR|0o755,st_nlink=2)
        api.fstat.return_value=directory;api.stat.return_value=directory
        tree=self.remote.BoundTree('/fixed',syscalls=api);tree.root_fd=10
        with self.assertRaisesRegex(RuntimeError,'fixture'):
            with tree.directory_fd('subdir'):raise RuntimeError('fixture')
        self.assertEqual(tree.chain,[]);api.close.assert_called_once_with(20)

    def test_descriptor_paths_reject_escape_before_any_open(self):
        for name in ('../outside','/outside','a/../b','a//b'):
            api,_=self.api();tree=self.remote.BoundTree('/fixed',syscalls=api);tree.root_fd=10
            with self.subTest(name=name),self.assertRaises(self.remote.legacy.GateError):
                with tree.parent_fd(name):pass
            api.open.assert_not_called()

    def test_symlink_hardlink_wrong_owner_or_mode_content_rejected(self):
        api,metadata=self.api()
        for changes in (dict(st_mode=stat.S_IFLNK|0o777),dict(st_nlink=2),dict(st_uid=1),dict(st_mode=stat.S_IFREG|0o622)):
            tree=self.remote.BoundTree('/fixed',syscalls=api)
            with self.subTest(changes=changes),patch.object(tree,'info',return_value=metadata(**changes)):
                with self.assertRaises(self.remote.legacy.GateError):tree.file_set('source')

    def test_pth_startup_customization_or_egg_metadata_rejected(self):
        for filename in ('execute.pth','sitecustomize.py','usercustomize.pyc','unknown.egg-info'):
            tree=self.remote.BoundTree('/fixed')
            with self.subTest(filename=filename),patch.object(tree,'entries',return_value=[filename]):
                with self.assertRaises(self.remote.legacy.GateError):tree.metadata_files()

    def test_recursive_walk_has_node_cap(self):
        api,meta=self.api();tree=self.remote.BoundTree('/fixed',syscalls=api)
        directory=meta(st_mode=stat.S_IFDIR|0o755,st_nlink=2)
        def info(name):return directory if name=='source' else meta()
        with patch.object(tree,'info',side_effect=info),patch.object(tree,'entries',return_value=[str(i) for i in range(801)]):
            with self.assertRaises(self.remote.legacy.GateError):tree.file_set('source')

    def test_interpreter_links_cycle_or_escape_rejected(self):
        valid=Fixture(self.remote).links
        self.remote.validate_venv(b'include-system-site-packages = false',valid)
        for target in ('python','/tmp/python','../python'):
            links=copy.deepcopy(valid);links['runtime-venv/bin/python']=target
            with self.subTest(target=target),self.assertRaises(self.remote.legacy.GateError):
                self.remote.validate_venv(b'include-system-site-packages = false',links)

    def test_metadata_rejects_multiple_name_headers(self):
        with self.assertRaises(self.remote.legacy.GateError):self.remote.validate_metadata({'x':b'Name: package0\nName: ignored\nVersion: 1.0\n'},{'package0':'1.0'})


class SnapshotTests(unittest.TestCase):
    def test_root_symlink_or_missing_parent_is_unknown_not_absent(self):
        remote,gate=modules();fixture=Fixture(remote)
        original=fixture.reader
        def unsafe(path):
            reader=original(path)
            if path==remote.DESTINATION.parent:
                reader.info=lambda name:SimpleNamespace(st_mode=stat.S_IFLNK|0o777,st_uid=0)
            return reader
        self.assertEqual(remote.observe(fixture.inventory,reader_factory=unsafe)['status'],'UNKNOWN')
        def missing_parent(path):raise FileNotFoundError()
        self.assertEqual(remote.observe(fixture.inventory,reader_factory=missing_parent)['status'],'UNKNOWN')

    def test_changed_after_verification_is_unknown_not_verified(self):
        remote,gate=modules();fixture=Fixture(remote);original=fixture.reader
        def changed(path):
            reader=original(path)
            if path==remote.DESTINATION:
                def unstable():raise remote.legacy.GateError('changed_during_read')
                reader.stable=unstable
            return reader
        value=remote.observe(fixture.inventory,reader_factory=changed)
        self.assertEqual(value['status'],'UNKNOWN');self.assertEqual(value['reason'],'changed_during_read')

if __name__=='__main__':unittest.main()
