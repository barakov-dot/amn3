"""Read-only facts packet: synthetic inputs and real local argv/child boundary only."""
import importlib.util
import unittest
class Availability(unittest.TestCase):
    def test_packet_exists(self):
        self.assertIsNotNone(importlib.util.find_spec('scripts.phase16_maintenance_facts_gate'))

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch
from pathlib import Path
from scripts import phase16_maintenance_facts_gate as gate
from scripts.vps import phase16_maintenance_facts_remote as remote
from scripts import phase16_bot_maintenance as core


def fixture_receipt():
    selected=remote.selected([])
    return dict(schema='phase16.maintenance-facts.v1',approval=remote.APPROVAL,target_binding_sha256=remote.TARGET,
        status='FACTS_COLLECTED_NOT_ADMITTED',reason='bounded_observation',completed_at='2026-10-02T12:00:00+00:00',
        remote_writes=0,database_opened=False,service_actions=0,application_imports=0,activation=False,live_admission=False,
        facts=dict(boot_id='11111111-2222-3333-4444-555555555555',units={u:{**dict.fromkeys(set(remote.FIELDS)-{'WorkingDirectory','ControlGroup'},''),'Id':u,'cwd_expected':True,'cgroup_expected':True} for u in remote.UNITS},
            launch_sha256={u:'a'*64 for u in remote.UNITS},process_environment={u:selected for u in remote.UNITS},
            dotenv_selected='ABSENT',settings_source_sha256=dict(old='1db81553dbcbf4dafc710efdd69c2db0cc1a869f0754d7bb67c7adfa3dcac631',candidate='6cb3ef9889422dc4d229ef90a5c558ddd100290253b77a8a6525f91676f5b9fe'),effective_settings='REQUIRES_SOURCE_AND_ENVIRONMENT_PRECEDENCE_REVIEW',
            startup_bound='NOT_ESTABLISHED',installed_binary_integrity='NOT_ESTABLISHED',
            inventory=dict(unit_count=2,unit_names_sha256='a'*64,related_units=list(remote.UNITS),cron_files=0,cron={},process_count=2,related_processes=[],exited_during_scan=0,writer_exclusion='NOT_ESTABLISHED_BY_STATIC_SCAN',external_pollers='REQUIRES_OPERATOR_OWNERSHIP',opaque_wrappers='REQUIRES_REVIEW')))

class FactTests(unittest.TestCase):
    def test_no_secrets_or_unvalidated_setting_values_escape(self):
        value=remote.selected([('TELEGRAM_BOT_TOKEN','PRIVATE_TOKEN'),('VPS_APPLY_ENABLED','False'),
            ('TELEGRAM_EXPECTED_BOT_USERNAME','bad PRIVATE_TOKEN'),('WEB_ADMIN_PORT','3030'),('DATABASE_PATH','PRIVATE_TOKEN')])
        self.assertNotIn('PRIVATE_TOKEN',json.dumps(value))
        self.assertIs(value['VPS_APPLY_ENABLED']['value'],False)
        self.assertEqual(value['WEB_ADMIN_PORT']['value'],3030)
        self.assertEqual(value['TELEGRAM_EXPECTED_BOT_USERNAME']['status'],'UNSUPPORTED')
        self.assertEqual(value['AWG3_BOOTSTRAP_ENABLED']['status'],'ABSENT')
    def test_duplicate_case_alias_and_unknown_bool_are_not_defaults(self):
        self.assertEqual(remote.selected([('VPS_APPLY_ENABLED','yes'),('vps_apply_enabled','no')])['VPS_APPLY_ENABLED']['status'],'AMBIGUOUS')
        self.assertEqual(remote.selected([('VPS_APPLY_ENABLED','maybe')])['VPS_APPLY_ENABLED']['status'],'UNSUPPORTED')
    def test_dotenv_parser_rejects_expansion_multiline_or_escapes(self):
        for raw in [b'VPS_APPLY_ENABLED=${X}',b'SECRET="a\nb"',b'SECRET=a\\b']:
            self.assertIsNone(remote.literal_dotenv(raw))
        value=remote.literal_dotenv(b'SECRET="private-fixture"\nVPS_APPLY_ENABLED=false\n')
        self.assertNotIn('private-fixture',json.dumps(value));self.assertIs(value['VPS_APPLY_ENABLED']['value'],False)
    def test_launch_digest_matches_existing_coordinator_encoding(self):
        self.assertEqual(remote.digest({'test':['value',False,15]}),core.digest({'test':['value',False,15]}))
    def test_late_read_command_is_rejected_without_retry(self):
        clock=[0];calls=[]
        def run(argv,seconds):calls.append(argv);clock[0]+=46;return b'{}'
        collector=remote.Collector(run,clock=lambda:clock[0])
        with self.assertRaisesRegex(remote.Stop,'deadline'):collector.run(['systemctl','show','--no-pager','--property='+','.join(remote.FIELDS),remote.UNITS[0]])
        self.assertEqual(len(calls),1)
    def test_readonly_command_scope_rejects_other_executables(self):
        calls=[];collector=remote.Collector(lambda *a:calls.append(a))
        with self.assertRaises(remote.Stop):collector.run(['bash','-c','exit 0'])
        with self.assertRaises(remote.Stop):collector.run(['systemctl','start',remote.UNITS[0]])
        self.assertEqual(calls,[])
    def test_proc_selection_uses_only_allowlisted_keys(self):
        value=remote.selected(remote.env_pairs(b'PASSWORD=hidden\0VPS_APPLY_ENABLED=0\0'))
        self.assertNotIn('hidden',json.dumps(value));self.assertIs(value['VPS_APPLY_ENABLED']['value'],False)

class PacketTests(unittest.TestCase):
    def test_rendered_wire_reaches_platform_guard_without_importing_repo_or_network(self):
        raw=gate.script();command,bootstrap=gate.wire(raw)
        self.assertNotIn(b'from scripts.',raw)
        self.assertLessEqual(gate.transport_base.command_units([command])+2048,30000)
        if sys.platform!='linux':
            result=subprocess.run([sys.executable,'-I','-S','-B','-c',bootstrap,remote.APPROVAL],
                input=b'',capture_output=True,timeout=5)
            self.assertEqual(result.returncode,3);self.assertEqual(result.stderr,b'')
            value=gate.parse(result.stdout)
            self.assertEqual(value['reason'],'platform_contract');self.assertIsNone(value['facts'])
    def test_manifest_tamper_fails_before_binding_access(self):
        value=gate.expected_manifest();value['limits']['ssh_attempts']=2;calls=[]
        with self.assertRaises(remote.Stop):gate.execute_once(value,approval=remote.APPROVAL,
            approved_manifest_sha=gate.sha(gate.encode(value)),approved_remote_sha=gate.sha(gate.script()),loader=lambda x:calls.append(x))
        self.assertEqual(calls,[])
    def test_receipt_cannot_claim_admission_mutations_or_complete_writer_exclusion(self):
        for key,value in [('live_admission',True),('remote_writes',1),('service_actions',True)]:
            receipt=fixture_receipt();receipt[key]=value
            with self.subTest(key=key),self.assertRaises(remote.Stop):gate.validate_receipt(receipt)
        receipt=fixture_receipt();receipt['facts']['inventory']['writer_exclusion']='ABSENT_VERIFIED'
        with self.assertRaises(remote.Stop):gate.validate_receipt(receipt)
    def test_truncated_duplicate_or_extra_receipt_is_rejected(self):
        raw=(json.dumps(fixture_receipt())+'\n').encode()
        self.assertEqual(gate.parse(raw)['status'],'FACTS_COLLECTED_NOT_ADMITTED')
        for bad in [raw[:-1],raw+raw,b'{"schema":"x","schema":"x"}\n']:
            with self.assertRaises((remote.Stop,ValueError)):gate.parse(bad)
    def test_one_claim_no_stdin_and_no_replay(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(gate,'EVIDENCE',Path(temp)/'attempt'):
            manifest=gate.expected_manifest();calls=[]
            binding=types.SimpleNamespace(role='spain',known_hosts_path='unused',key_path='unused',target_user='root',target_host='test.invalid')
            def transport(args,**kwargs):
                self.assertTrue((gate.EVIDENCE/'claim.json').is_file())
                self.assertEqual(kwargs['input_bytes'],b'');self.assertEqual(kwargs['timeout'],60)
                self.assertIn('-n',args);calls.append(args)
                kwargs['diagnostics'].update(stdin_complete=True,output_complete=True)
                return 0,(json.dumps(fixture_receipt())+'\n').encode()
            options=dict(approval=remote.APPROVAL,approved_manifest_sha=gate.sha(gate.encode(manifest)),
                approved_remote_sha=gate.sha(gate.script()),loader=lambda role:binding,
                binding_hasher=lambda b:remote.TARGET,transport=transport)
            value=gate.execute_once(manifest,**options)
            self.assertEqual(value['status'],'FACTS_COLLECTED_NOT_ADMITTED')
            with self.assertRaises(remote.Stop):gate.execute_once(manifest,**options)
            self.assertEqual(len(calls),1)
    def test_transport_timeout_retains_claim_as_unknown(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(gate,'EVIDENCE',Path(temp)/'attempt'):
            manifest=gate.expected_manifest()
            binding=types.SimpleNamespace(role='spain',known_hosts_path='unused',key_path='unused',target_user='root',target_host='test.invalid')
            def transport(*args,**kwargs):raise RuntimeError('PRIVATE_ERROR')
            value=gate.execute_once(manifest,approval=remote.APPROVAL,approved_manifest_sha=gate.sha(gate.encode(manifest)),
                approved_remote_sha=gate.sha(gate.script()),loader=lambda role:binding,binding_hasher=lambda b:remote.TARGET,transport=transport)
            self.assertEqual(value['status'],'UNKNOWN_NO_RETRY')
            self.assertNotIn('PRIVATE_ERROR',json.dumps(value));self.assertTrue((gate.EVIDENCE/'claim.json').exists())
