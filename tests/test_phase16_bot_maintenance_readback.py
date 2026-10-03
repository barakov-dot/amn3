import json
import unittest
from unittest.mock import patch
from scripts import phase16_bot_maintenance_readback as gate

class ReadbackTests(unittest.TestCase):
    def test_original_packet_is_bound_and_readback_has_no_mutations(self):
        value=gate.expected_manifest()
        self.assertEqual(value['original_manifest_sha256'],gate.ORIGINAL)
        self.assertEqual(value['scope']['service_actions'],0)
        self.assertEqual(value['scope']['database_open'],0)
        self.assertEqual(value['scope']['remote_file_writes'],0)
        self.assertEqual(value['scope']['app_imports'],0)
        self.assertEqual(gate.preview()['ssh_attempts'],0)
    def test_mutated_original_pin_rejected(self):
        value=gate.packet.expected_manifest();value['request']['expected_boot_id']='changed'
        with patch.object(gate.packet,'expected_manifest',return_value=value):
            with self.assertRaises(ValueError):gate.expected_manifest()
    def test_errors_redacted_unless_literal_pinned_reason(self):
        env=gate.remote_definitions()
        self.assertEqual(env['safe_reason'](ValueError('token=secret')),'UNCLASSIFIED_ERROR')
        self.assertEqual(env['safe_reason'](ValueError('host_unit_state')),'host_unit_state')
        self.assertEqual(env['safe_reason'](ValueError('candidate_collection_failed')),'candidate_collection_failed')
    def test_record_values_never_pass_arbitrary_secret_text(self):
        env=gate.remote_definitions()
        record=env['summary'](b'{"status":"secret_token","reason":"secret_token","phase":"secret_token"}')
        self.assertEqual(record,dict(status=None,reason=None,phase=None))
    def test_remote_platform_stop_is_closed(self):
        result=gate.platform_fixture()
        self.assertEqual(result['status'],'UNKNOWN_NO_RETRY')
        self.assertEqual(result['reason'],'platform_or_precondition')
        gate.validate_receipt(result,3)
    def test_receipt_rejects_unexpected_field(self):
        value=gate.platform_fixture();value['raw']='secret'
        with self.assertRaises(ValueError):gate.validate_receipt(value,3)
    def test_deadline_includes_bootstrap_and_is_not_swallowed_by_probe(self):
        env=gate.remote_definitions();env['READBACK_STARTED']=env['time'].monotonic()-118
        handlers={};delays=[]
        def install(number,handler):handlers['callback']=handler
        def collected():return env['probe'](lambda:handlers['callback']())
        env['collect']=collected
        with patch.object(env['sys'],'platform','linux'),patch.object(env['os'],'geteuid',return_value=0,create=True),patch.object(env['signal'],'SIGALRM',14,create=True),patch.object(env['signal'],'signal',side_effect=install),patch.object(env['signal'],'getsignal',return_value='previous'),patch.object(env['signal'],'alarm',side_effect=lambda delay:delays.append(delay),create=True):
            value=env['main'](gate.APPROVAL)
        self.assertEqual(value['status'],'UNKNOWN_NO_RETRY')
        self.assertEqual(value['reason'],'deadline')
        self.assertLessEqual(delays[0],2)

    def test_deadline_survives_actual_legacy_collector_wrapper(self):
        from scripts import phase16_bot_legacy_runtime_proof as legacy
        env=gate.remote_definitions();handlers={}
        def install(number,handler):handlers['callback']=handler
        def reader_factory(root):handlers['callback']()
        env['collect']=lambda:env['probe'](lambda:legacy.collect_live(reader_factory=reader_factory))
        with patch.object(env['sys'],'platform','linux'),patch.object(env['os'],'geteuid',return_value=0,create=True),patch.object(env['signal'],'SIGALRM',14,create=True),patch.object(env['signal'],'signal',side_effect=install),patch.object(env['signal'],'getsignal',return_value='previous'),patch.object(env['signal'],'alarm',create=True):
            value=env['main'](gate.APPROVAL)
        self.assertEqual(value['status'],'UNKNOWN_NO_RETRY')
        self.assertEqual(value['reason'],'deadline')
        self.assertIsNone(value['snapshot'])

    def success_fixture(self):
        env=gate.remote_definitions();value=gate.platform_fixture()
        units={u:dict(state='UNAVAILABLE',properties={}) for u in env['UNITS']}
        value.update(status='READBACK_COLLECTED_NOT_RECOVERY',reason='bounded_observation',failure_boundary=None,snapshot=dict(units_before=units,units_after=units,records={n:dict(state='ABSENT') for n in env['NAMES']},journal=dict(state='ABSENT'),fences={u:dict(dropin=dict(state='ABSENT'),permit=dict(state='ABSENT')) for u in env['UNITS'][:2]},readonly_probes=dict(unit_facts=dict(status='STOP',reason='host_unit_state')),probe_scope='NO_APPLY_NO_DB_NO_APP_NO_SERVICE_ACTION',unobserved=['original exception detail','database migration correctness','pending/writer admission','live acceptance']))
        return value
    def test_success_snapshot_is_closed_and_not_recovery(self):
        gate.validate_receipt(self.success_fixture(),0)
    def test_success_snapshot_rejects_secret_in_nested_reason(self):
        value=self.success_fixture();value['snapshot']['readonly_probes']['unit_facts']['reason']='token_secret'
        with self.assertRaises(ValueError):gate.validate_receipt(value,0)
    def test_scope_and_exit_code_cannot_be_changed(self):
        value=self.success_fixture()
        with self.assertRaises(ValueError):gate.validate_receipt(value,3)
        value['database_open']=True
        with self.assertRaises(ValueError):gate.validate_receipt(value,0)

    def test_wire_is_bounded_and_compilable(self):
        raw=gate.script();compile(raw,'<readback>','exec')
        command=gate.wire(raw)
        self.assertLessEqual(gate.old.command_units([command])+2048,30000)
        self.assertNotIn('systemctl start',raw.decode())
        self.assertNotIn('systemctl stop',raw.decode())
    def test_execute_wrong_approval_does_not_load_binding(self):
        def forbidden(_):self.fail('protected binding loaded before approval validation')
        with self.assertRaises(ValueError):gate.execute_once(gate.expected_manifest(),approval='bad',manifest_sha='0'*64,remote_sha='0'*64,loader=forbidden)
if __name__=='__main__':unittest.main()
