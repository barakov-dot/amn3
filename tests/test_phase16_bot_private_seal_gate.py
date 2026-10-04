"""Separate seal gate binding/launcher/receipt tests; no network or native DAC."""
import copy
import importlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
try:g=importlib.import_module('scripts.phase16_bot_private_seal_gate')
except ModuleNotFoundError:g=None

class SealGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if g is not None:cls.raw=g.script();cls.manifest=g.expected_manifest()
    def setUp(self):self.assertIsNotNone(g,'new separate seal gate absent')
    def good(self):
        r=self.windows();r.update(status='PRIVATE_FILES_SEALED_CANDIDATE_CHECKED',reason='bounded_private_seal_candidate_readonly',audit_creation_attempted=True)
        after=copy.deepcopy(g.witness()['objects'])
        for n in g.core.TARGETS:after[n].update(mode=0o600,private=True,ctime_ns=after[n]['ctime_ns']+1)
        r['operation']=dict(status=r['status'],reason=r['reason'],permission_attempted=True,completed_syscalls=2,files_verified=True,files_after={n:after[n] for n in g.core.TARGETS},candidate=dict(status='STOP',reason='candidate_collection_failed',proof_status=None,plan_status=None,plan_sha256=None,plan_objects=0),result_durable=True)
        return r
    def windows(self):
        e={'__name__':'fixture'};exec(compile(self.raw,'<seal fixture>','exec'),e);e['READBACK_STARTED']=__import__('time').monotonic()
        with patch.object(e['sys'],'platform','win32'):return e['main'](g.APPROVAL)
    def test_manifest_frozen57_trigger_and_exact_two_changes(self):
        self.assertEqual(self.manifest,json.loads(g.MANIFEST.read_bytes()));self.assertEqual(len(self.manifest['original_artifacts_sha256_lf']),57);self.assertEqual(self.manifest['limits']['permission_syscalls_max'],2);self.assertEqual(self.manifest['scope']['files'],list(g.core.TARGETS));self.assertNotEqual(g.OP,g.predecessor.v2.OP)
    def test_preview_no_egress_and_claim_existing_no_loader(self):
        with patch.object(g.packet.transport,'run_transport',side_effect=AssertionError('egress')):self.assertEqual(g.preview()['ssh_attempts'],0)
        with tempfile.TemporaryDirectory() as d,patch.object(g,'EVIDENCE',Path(d)):
            m=g.expected_manifest()
            with self.assertRaises(Exception):g.execute_once(m,approval=g.APPROVAL,manifest_sha=g.packet.core.digest(m),remote_sha=g.packet.sha(self.raw),loader=lambda r:self.fail('loader'))
    def test_actual_authenticated_stdin0_launcher_windows_closed(self):
        tokens=shlex.split(g.wire(self.raw));self.assertEqual(tokens[-1],g.APPROVAL)
        p=subprocess.run([sys.executable,'-I','-S','-B','-c',tokens[5],g.APPROVAL],capture_output=True)
        self.assertEqual(p.returncode,3);self.assertEqual(p.stderr,b'');r=g.validate_receipt(json.loads(p.stdout),3);self.assertIsNone(r['operation']);self.assertFalse(r['audit_creation_attempted'])
    def test_mutated_consumed_source_and_trigger_reject_before_build(self):
        original=g.packet.canonical
        for target in (Path(g.predecessor.base.__file__),g.TRIGGER):
            def drift(path):return original(path)+b'\n' if Path(path).resolve()==target.resolve() else original(path)
            with patch.object(g.packet,'canonical',side_effect=drift):
                with self.assertRaises(ValueError):g.script()
    def test_candidate_stop_separate_from_verified_seal_and_false_zero_change_reject(self):
        r=self.good();g.validate_receipt(r,0)
        for modify in (lambda v:v['operation'].update(permission_attempted=False),lambda v:v['operation'].update(completed_syscalls=1),lambda v:v['operation']['files_after']['claim.json'].update(inode=9),lambda v:v['operation']['files_after']['claim.json'].update(mode=0o644),lambda v:v.update(status='STOP_NO_PERMISSION_CHANGE'),lambda v:v.update(app_imports=True)):
            bad=copy.deepcopy(r);modify(bad)
            with self.assertRaises(Exception):g.validate_receipt(bad,0)
    def test_verified_files_cannot_regress_ctime(self):
        r=self.good();r['operation']['files_after']['claim.json']['ctime_ns']=0
        with self.assertRaises(ValueError):g.validate_receipt(r,0)
    def test_success_operation_reason_must_match_exact_bounded_reason(self):
        for top,op in (('bounded_private_seal_candidate_readonly','deadline'),('deadline','deadline')):
            r=self.good();r['reason']=top;r['operation']['reason']=op
            with self.assertRaises(ValueError):g.validate_receipt(r,0)
    def test_local_fake_transport_durable_result_once_no_retry(self):
        with tempfile.TemporaryDirectory() as d,patch.object(g,'EVIDENCE',Path(d)/'one'),patch.object(g.packet.transport,'run_transport',side_effect=TimeoutError('secret')) as transport:
            m=g.expected_manifest();from types import SimpleNamespace
            target=SimpleNamespace(role='spain',known_hosts_path=Path(d)/'known',key_path=Path(d)/'key',target_user='root',target_host='fixture')
            with patch.object(g.base,'binding_digest',return_value=g.packet.entry.binding.TARGET):
                r=g.execute_once(m,approval=g.APPROVAL,manifest_sha=g.packet.core.digest(m),remote_sha=g.packet.sha(self.raw),loader=lambda role:target)
            self.assertEqual(r['status'],'UNKNOWN_NO_RETRY');self.assertEqual(transport.call_count,1);self.assertTrue((g.EVIDENCE/'claim.json').exists());self.assertTrue((g.EVIDENCE/'result.json').exists());self.assertNotIn('secret',json.dumps(r))
if __name__=='__main__':unittest.main()
