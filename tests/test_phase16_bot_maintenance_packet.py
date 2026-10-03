"""Packet authenticity/limits/closed platform bootstrap; no SSH or host writes."""
import importlib
import json
import subprocess
import sys
import unittest
try:packet=importlib.import_module('scripts.phase16_bot_maintenance_packet')
except ModuleNotFoundError as error:
    if error.name!='scripts.phase16_bot_maintenance_packet':raise
    packet=None
class PacketTests(unittest.TestCase):
    def test_packet_module_exists(self):self.assertIsNotNone(packet)
    def test_default_preview_builds_exact_source_only_frame(self):
        result=packet.preview()
        self.assertEqual(result['status'],'READY_FOR_EXACT_APPROVAL_NOT_EXECUTED')
        self.assertEqual(result['ssh_attempts'],0)
        self.assertLessEqual(result['frame_bytes'],2*1024*1024)
        self.assertEqual(result['remote_seconds'],1560)
    def test_tampered_manifest_cannot_launch(self):
        manifest=packet.expected_manifest();manifest['request']['ownership_seconds']=3600
        with self.assertRaises(Exception):packet.validate_manifest(manifest)
    def test_packed_sources_match_inventory_and_exclude_caches_secrets(self):
        manifest=packet.expected_manifest();payload=packet.payload(manifest)
        value=packet.decode_payload(payload)
        self.assertEqual(set(value['files']),set(manifest['files_sha256_lf']))
        self.assertTrue(all(name.endswith(('.py','.txt','.json')) for name in value['files']))
        self.assertFalse(any('__pycache__' in name or '.env' in name for name in value['files']))
    def test_platform_stop_before_remote_filesystem_write(self):
        manifest=packet.expected_manifest();payload=packet.payload(manifest)
        bootstrap=packet.bootstrap(payload,manifest)
        result=subprocess.run([sys.executable,'-I','-S','-B','-c',bootstrap],input=packet.frame(payload),
            capture_output=True,timeout=10)
        self.assertEqual(result.returncode,3)
        self.assertEqual(json.loads(result.stdout)['reason'],'platform')
        self.assertEqual(result.stderr,b'')

    def test_incomplete_success_cannot_be_reported_as_complete(self):
        value={'schema':'phase16.maintenance-packet-result.v1','approval':packet.entry.APPROVAL,
            'operation_id':packet.entry.OPERATION,'manifest_sha256':'a'*64,'target_binding_sha256':packet.entry.binding.TARGET,
            'awg2':'UNTOUCHED','package016':'UNCHANGED','general_issuance':'DISABLED','automatic_replay':False,
            'result':{'status':'SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE'}}
        with self.assertRaises(packet.core.Stop):packet.validate_receipt(value,0,'a'*64)
    def test_exact_release_success_is_accepted(self):
        value={'schema':'phase16.maintenance-packet-result.v1','approval':packet.entry.APPROVAL,
            'operation_id':packet.entry.OPERATION,'manifest_sha256':'a'*64,'target_binding_sha256':packet.entry.binding.TARGET,
            'awg2':'UNTOUCHED','package016':'UNCHANGED','general_issuance':'DISABLED','automatic_replay':False,
            'result':dict(status='SEQUENCE_COMPLETE_NOT_LIVE_ACCEPTANCE',phase='release_done',
                candidate_start_requested=True,recovery_route='NOT_REQUIRED',automatic_recovery='DISABLED',
                live_acceptance='NOT_ESTABLISHED',reason='all_operations_verified')}
        self.assertTrue(packet.validate_receipt(value,0,'a'*64))
        value['secret']='not-for-output'
        with self.assertRaises(packet.core.Stop):packet.validate_receipt(value,0,'a'*64)
