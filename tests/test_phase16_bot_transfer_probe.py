"""Offline transfer probe contracts; real local receiver, synthetic data only."""
import copy
import importlib
import importlib.util
import io
import json
from pathlib import Path
import shlex
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


class ProbeTests(unittest.TestCase):
    def setUp(self):
        name = 'scripts.phase16_bot_transfer_probe_gate'
        self.assertIsNotNone(importlib.util.find_spec(name), 'transfer probe gate missing')
        self.g = importlib.import_module(name)
        self.r = self.g.remote
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def encoded(self, events):
        return b''.join((json.dumps(e)+'\n').encode() for e in events)

    def events(self, body):
        events=[]
        rc=self.r.receive(io.BytesIO(body), events.append)
        return rc,events

    def test_receiver_full_payload_has_bounded_progress_and_complete_hash(self):
        rc,events=self.events(self.g.payload())
        self.assertEqual(rc,0)
        self.assertEqual(events[0]['event'],'READY')
        self.assertEqual(events[-1]['event'],'COMPLETE')
        self.assertEqual(events[-1]['bytes'],30485208)
        self.assertEqual(len(events),31)
        parsed=self.g.parse_events(self.encoded(events))
        self.assertEqual(parsed['status'],'COMPLETE')
        self.assertEqual(parsed['confirmed_bytes'],30485208)

    def test_receiver_rejects_truncated_corrupt_and_extra_input(self):
        for body,reason in [(b'x'*123,'INPUT_EOF'),(b'x'*30485208,'PAYLOAD_HASH'),(self.g.payload()+b'x','INPUT_EXTRA')]:
            with self.subTest(reason=reason):
                rc,events=self.events(body)
                self.assertEqual(rc,3)
                self.assertEqual(events[-1]['reason'],reason)
                self.assertEqual(self.g.parse_events(self.encoded(events))['status'],'STOP')

    def test_receiver_timeout_returns_bounded_stop_without_exception_text(self):
        class TimedOut:
            def read(self,n):raise TimeoutError('PRIVATE_SECRET')
        events=[]
        self.assertEqual(self.r.receive(TimedOut(),events.append),3)
        result=self.g.parse_events(self.encoded(events))
        self.assertEqual(result['status'],'STOP')
        self.assertEqual(result['events'][-1]['reason'],'TIME_LIMIT')
        self.assertNotIn('PRIVATE_SECRET',json.dumps(result))

    def test_manifest_scope_or_boolean_type_drift_is_rejected(self):
        for value in [1,False]:
            manifest=self.g.expected_manifest()
            manifest['scope']['remote_file_writes']=value
            with self.assertRaises(self.g.GuardError):self.g.validate_manifest(manifest)

    def test_receipt_rejects_false_pass_extra_fields_boolean_count_reorder_and_duplicate_keys(self):
        _,events=self.events(self.g.payload())
        variants=[]
        bad=copy.deepcopy(events);bad[-1]['sha256']='0'*64;variants.append(bad)
        bad=copy.deepcopy(events);bad[0]['raw']='PRIVATE_SECRET';variants.append(bad)
        bad=copy.deepcopy(events);bad[0]['bytes']=False;variants.append(bad)
        bad=copy.deepcopy(events);bad[1],bad[2]=bad[2],bad[1];variants.append(bad)
        bad=copy.deepcopy(events);bad.append(bad[-1]);variants.append(bad)
        for value in variants:
            with self.assertRaises(self.g.GuardError):self.g.parse_events(self.encoded(value))
        with self.assertRaises(self.g.GuardError):
            self.g.parse_events(b'{"event":"READY","event":"COMPLETE"}\n')

    def test_partial_event_line_preserves_only_validated_prefix(self):
        _,events=self.events(self.g.payload())
        parsed=self.g.parse_events(self.encoded(events[:2])+b'{"PRIVATE_SECRET":')
        self.assertEqual(parsed['status'],'PREFIX_ONLY')
        self.assertEqual(parsed['confirmed_bytes'],1048576)
        self.assertTrue(parsed['trailing_fragment'])
        self.assertNotIn('PRIVATE_SECRET',json.dumps(parsed))
        with self.assertRaises(self.g.GuardError):self.g.parse_events(b'x'*65537)

    def test_exact_receiver_frame_runs_locally_without_files(self):
        command,frame=self.g.frame_request()
        from scripts.phase16_bot_transport_diagnostics import run_transport
        d={}
        rc,out=run_transport([sys.executable,*shlex.split(command)[1:]],cwd=self.root,
            env=None,timeout=10,input_bytes=frame,diagnostics=d)
        self.assertEqual(rc,0)
        self.assertEqual(self.g.parse_events(out)['status'],'COMPLETE')
        self.assertEqual(list(self.root.iterdir()),[])
        self.assertTrue(d['stdin_complete'])

    def test_default_preview_never_loads_target_or_creates_evidence(self):
        manifest=self.g.expected_manifest()
        result=self.g.preview(manifest)
        self.assertEqual(result['status'],'OFFLINE_READY_NOT_EXECUTED')
        self.assertEqual(result['ssh_attempts'],0)
        self.assertEqual(result['remote_file_writes'],0)

    def execute(self,transport,**overrides):
        g=self.g
        binding=SimpleNamespace(role='spain',target_host='fixture.invalid',target_user='synthetic',key_path=self.root/'key',known_hosts_path=self.root/'hosts')
        manifest=g.expected_manifest()
        args=dict(approval=g.remote.APPROVAL,approved_remote_sha=g.sha(g.remote_script()),
            approved_manifest_sha=g.sha(g.encode(manifest)),loader=lambda role:binding,
            transport=transport,binding_hasher=lambda b:g.TARGET_BINDING)
        args.update(overrides)
        return g.execute_once(manifest,**args)

    def test_success_once_and_reuse_stops_before_target_loading(self):
        calls=[]
        def transport(*args,**kw):
            calls.append(1)
            _,events=self.events(self.g.payload());out=self.encoded(events)
            kw['diagnostics'].update(stdin_complete=True,output_complete=True,returncode=0)
            kw['stdout_observer'](out)
            return 0,out
        with patch.object(self.g,'EVIDENCE_DIRECTORY',self.root/'once'),patch.object(self.g,'ssh_environment',return_value={}):
            result=self.execute(transport)
            self.assertEqual(result['status'],'TRANSFER_OBSERVED_NOT_STAGE_ACCEPTANCE')
            with self.assertRaises(self.g.GuardError):
                self.execute(transport,loader=lambda role:self.fail('stale claim loaded target'))
            self.assertEqual(calls,[1])

    def test_hash_target_and_approval_drift_stop_without_claim_or_transport(self):
        variants=[{'approval':'OLD'},{'approved_remote_sha':'0'*64},{'approved_manifest_sha':'0'*64},
                  {'binding_hasher':lambda b:'0'*64}]
        with patch.object(self.g,'EVIDENCE_DIRECTORY',self.root/'once'),patch.object(self.g,'ssh_environment',return_value={}):
            for kw in variants:
                with self.subTest(fields=list(kw)),self.assertRaises(self.g.GuardError):
                    self.execute(lambda *a,**k:self.fail('unexpected transport'),**kw)
                self.assertFalse((self.root/'once').exists())

    def test_observer_retains_safe_progress_on_transport_failure_without_retry(self):
        def transport(*args,**kw):
            _,events=self.events(self.g.payload())
            kw['stdout_observer'](self.encoded(events[:3])+b'{"PRIVATE_SECRET":')
            raise self.g.transport_gate.GateError('transport_stdin_write')
        with patch.object(self.g,'EVIDENCE_DIRECTORY',self.root/'once'),patch.object(self.g,'ssh_environment',return_value={}):
            result=self.execute(transport)
            self.assertEqual(result['status'],'UNKNOWN_NO_RETRY')
            self.assertEqual(result['remote_observation']['confirmed_bytes'],2097152)
            self.assertNotIn('PRIVATE_SECRET',json.dumps(result))
            self.assertTrue((self.root/'once/result.json').exists())

    def test_false_complete_cannot_override_incomplete_transport_or_rc(self):
        for rc,complete in [(255,True),(0,False)]:
            def transport(*args,**kw):
                _,events=self.events(self.g.payload());out=self.encoded(events)
                kw['stdout_observer'](out)
                kw['diagnostics'].update(stdin_complete=complete,output_complete=True,returncode=rc)
                return rc,out
            with self.subTest(rc=rc),patch.object(self.g,'EVIDENCE_DIRECTORY',self.root/f'case{rc}'),patch.object(self.g,'ssh_environment',return_value={}):
                self.assertEqual(self.execute(transport)['status'],'UNKNOWN_NO_RETRY')

    def test_invalid_observer_output_redacted(self):
        def transport(*args,**kw):
            out=b'{"raw":"PRIVATE_SECRET"}\n'
            kw['stdout_observer'](out)
            return 0,out
        with patch.object(self.g,'EVIDENCE_DIRECTORY',self.root/'once'),patch.object(self.g,'ssh_environment',return_value={}):
            result=self.execute(transport)
            self.assertEqual(result['status'],'UNKNOWN_NO_RETRY')
            self.assertEqual(result['remote_observation']['status'],'INVALID')
            self.assertNotIn('PRIVATE_SECRET',json.dumps(result))


if __name__=='__main__':unittest.main()
