"""Preflight sequencing tests; every host boundary is explicitly replaced."""
import importlib
import unittest
try:entry=importlib.import_module('scripts.phase16_bot_maintenance_entry')
except ModuleNotFoundError as error:
    if error.name!='scripts.phase16_bot_maintenance_entry':raise
    entry=None

class EntryTests(unittest.TestCase):
    def test_entry_exists(self):self.assertIsNotNone(entry)
    def test_preview_is_not_execution_or_default_approval(self):
        self.assertEqual(entry.preview()['status'],'EXACT_APPROVAL_REQUIRED')
        self.assertFalse(entry.preview()['authorized'])
    def test_incomplete_owner_declaration_refuses_before_any_collection(self):
        with self.assertRaisesRegex(entry.core.Stop,'packet_owner_declaration'):
            entry.validate_request(dict(approval=entry.APPROVAL,operation_id=entry.OPERATION,
                expected_boot_id=entry.BOOT,target_binding_sha256=entry.binding.TARGET,
                ownership_seconds=2700,accepted_owner_statement=False), 'a'*64)
    def test_boot_and_target_are_exact_packet_bindings(self):
        value=entry.request();value['expected_boot_id']='00000000-0000-0000-0000-000000000000'
        with self.assertRaises(entry.core.Stop):entry.validate_request(value,'a'*64)

    def test_pending_failure_prevents_permission_and_service_actions(self):
        import tempfile,time
        from pathlib import Path
        from unittest.mock import patch,Mock
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);inventory=root/entry.binding.BOUND['inventory'][0]
            inventory.parent.mkdir(parents=True);inventory.write_bytes(b'fixture')
            client=Mock();prior=Mock()
            with patch.object(entry.jobs,'boot_id',return_value=entry.BOOT), \
                patch.object(entry.host,'unit_facts',return_value=({},{})), \
                patch.object(entry.candidate,'collect_live',return_value=SimpleNamespace()), \
                patch.object(entry.old,'collect_live',return_value=prior), \
                patch.object(entry.pending,'collect_live',side_effect=entry.core.Stop('pending_read_failed')), \
                patch.object(entry.apply,'execute') as mutate, \
                patch.object(entry.writers,'collect_writer_admission') as writers:
                with self.assertRaisesRegex(entry.core.Stop,'pending_read_failed'):
                    entry.prepare(client,root,root,entry.request(),'a'*64)
                mutate.assert_not_called();writers.assert_not_called();prior.close.assert_called_once()
    def test_boot_change_stops_before_candidate_read_or_mutation(self):
        from unittest.mock import patch,Mock
        from pathlib import Path
        with patch.object(entry.jobs,'boot_id',return_value='changed'), \
            patch.object(entry.candidate,'collect_live') as collect,patch.object(entry.apply,'execute') as mutate:
            with self.assertRaisesRegex(entry.core.Stop,'boot_changed'):
                entry.prepare(Mock(),Path('/fixture'),Path('/fixture'),entry.request(),'a'*64)
            collect.assert_not_called();mutate.assert_not_called()

    def test_submicrosecond_clock_does_not_make_lease_start_in_future(self):
        owner,declaration=entry.owner_records(entry.request(),'a'*64,1.0000006)
        self.assertLessEqual(entry.writers.timestamp(declaration['declared_at']),1.0000006)
