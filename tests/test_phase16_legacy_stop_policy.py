"""Local operation binding only; no live admission or source collection."""
import copy
import importlib.util
import tempfile
from pathlib import Path
import unittest
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_binding as binding
from tests.test_phase16_bot_maintenance_binding import observations, ownership, NOW

AVAILABLE = importlib.util.find_spec('scripts.phase16_legacy_stop_policy') is not None
if AVAILABLE:
    from scripts import phase16_legacy_stop_policy as policy

class Availability(unittest.TestCase):
    def test_approved_legacy_policy_has_operation_binding(self):
        self.assertTrue(AVAILABLE, 'approved exception has no operation-bound contract')

@unittest.skipUnless(AVAILABLE, 'availability assertion must fail first')
class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.prepared = binding.prepare_inputs(observations(), ownership(), now=NOW)
        self.value = policy.bind(self.prepared, packet_sha256='a'*64,
            old_commit=policy.OLD_COMMIT, old_handlers_sha256=policy.OLD_HANDLERS,
            old_workflows_sha256=policy.OLD_WORKFLOWS)

    def rehash(self, value):
        value['sha256'] = core.digest({k:v for k,v in value.items() if k!='sha256'})

    def test_bound_exception_never_claims_drain_or_live_authority(self):
        self.assertEqual(policy.validate(self.value, self.prepared), self.value['sha256'])
        self.assertEqual(self.value['old_handler_drain'], 'NOT_OBSERVABLE_ACCEPTED_BY_OPERATOR')
        self.assertFalse(self.value['live_authorized'])
        self.assertFalse(self.value['automatic_restore'])
        self.assertFalse(self.value['automatic_replay'])

    def test_other_source_cannot_use_exception(self):
        for field in ('old_commit','old_handlers_sha256','old_workflows_sha256'):
            v=copy.deepcopy(self.value); v[field]='0'*len(v[field]); self.rehash(v)
            with self.subTest(field=field), self.assertRaises(core.Stop): policy.validate(v,self.prepared)

    def test_rehashed_exception_cannot_expand_to_web_candidate_or_other_operation(self):
        for field,value in [('subject',core.WEB),('candidate_commit','0'*40),
                            ('operation_id','phase16-other'),('boot_id','0'*36),
                            ('journal_binding','0'*64),('target_contract_sha256','0'*64)]:
            v=copy.deepcopy(self.value); v[field]=value; self.rehash(v)
            with self.subTest(field=field), self.assertRaises(core.Stop): policy.validate(v,self.prepared)

    def test_automatic_restore_replay_and_live_authority_cannot_be_enabled(self):
        for field in ('automatic_restore','automatic_replay','live_authorized'):
            v=copy.deepcopy(self.value); v[field]=True; self.rehash(v)
            with self.subTest(field=field), self.assertRaises(core.Stop): policy.validate(v,self.prepared)

    def test_cannot_promote_unknown_drain_to_complete(self):
        v=copy.deepcopy(self.value); v['old_handler_drain']='complete'; self.rehash(v)
        with self.assertRaises(core.Stop): policy.validate(v,self.prepared)

    def test_missing_or_extra_fields_and_corrupt_digest_rejected(self):
        variants=[[],None,dict(self.value,extra=True),dict(self.value,sha256='0'*64)]
        v=copy.deepcopy(self.value); del v['packet_sha256']; variants.append(v)
        for v in variants:
            with self.subTest(value=type(v).__name__),self.assertRaises(core.Stop): policy.validate(v,self.prepared)

    def test_packet_requires_exact_checksum(self):
        v=copy.deepcopy(self.value);v['packet_sha256']='approved';self.rehash(v)
        with self.assertRaises(core.Stop): policy.validate(v,self.prepared)

    def test_recovery_preserves_database_after_candidate_intent_and_never_restores(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal=core.Journal.create(Path(tmp)/'journal',self.prepared['coordinator_manifest'])
            self.assertEqual(policy.recovery(journal,self.value,self.prepared),'LEAVE_OLD_RUNTIME')
            for action in ('fence','stop','backup','rehearsal','migrate'):
                journal.perform(action,lambda:None,lambda:True)
                self.assertEqual(policy.recovery(journal,self.value,self.prepared),'HOLD_FENCE_MANUAL_RECOVERY')
            def fail(): raise core.Stop('synthetic_candidate_start_failure')
            with self.assertRaises(core.Stop):journal.perform('candidate_start',fail,lambda:True)
            self.assertEqual(policy.recovery(journal,self.value,self.prepared),'PRESERVE_DB_MANUAL_RECOVERY')

if __name__=='__main__':unittest.main()
