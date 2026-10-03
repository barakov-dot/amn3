"""One absolute start observation deadline across manager and admission checks."""
import importlib.util
import json
import unittest
from scripts import phase16_bot_maintenance as core
from tests import test_phase16_bot_service_operations as service_tests
AVAILABLE=importlib.util.find_spec('scripts.phase16_bot_startup_budget') is not None
if AVAILABLE:from scripts import phase16_bot_startup_budget as m

class Availability(unittest.TestCase):
    def test_startup_budget_exists(self):self.assertTrue(AVAILABLE)

@unittest.skipUnless(AVAILABLE,'availability fails first')
class BudgetTests(unittest.TestCase):
    def fixture(self):
        f=service_tests.ServiceTests();f.setUp();self.addCleanup(f.doCleanups);f.setup_services()
        native=f.client.run
        def run(argv,seconds):
            if argv[0]=='busctl' and argv[-1]=='TimeoutStartUSec' and 'bot' in argv[4]:
                return json.dumps(dict(type='t',data=40000000)).encode()
            return native(argv,seconds)
        f.client.run=run
        old=f.operations
        f.operations=m.BudgetedServiceOperations(old.journal,old.client,old.fence,old.supervisor,
            expected_username=old.username,source_verifier=old.source_verifier,
            web_port=old.web_port,clock=old.clock,sleep=old.sleep,startup_observation_budget_seconds=39)
        return f
    def test_ready_and_admission_within39_pass_and_baseline_remains40(self):
        f=self.fixture();f.step('candidate_start')
        self.assertEqual(f.journal.phase,'candidate_start_done')
        self.assertEqual(f.journal.manifest['unit_baseline'][core.BOT]['start_seconds'],40)
        self.assertLess(f.operations.startup_observation['elapsed_seconds'],39)
        self.assertEqual(f.operations.startup_observation['scope'],'ENFORCED_OBSERVATION_BUDGET')
    def test_late_ready_cannot_use_manager40_seconds_as_observation_budget(self):
        f=self.fixture();native=f.client.run
        def run(argv,seconds):
            value=native(argv,seconds)
            if argv[:3]==['systemctl','--no-block','start']:f.clock[0]+=39.1
            return value
        f.client.run=run
        with self.assertRaises(core.Stop):f.step('candidate_start')
        self.assertEqual(f.journal.phase,'candidate_start_intent')
        self.assertTrue(f.fence.present())
    def test_admission_must_fit_same_deadline_and_late_receipt_stops(self):
        f=self.fixture();native=f.client.run;after_start=[False]
        def run(argv,seconds):
            value=native(argv,seconds)
            if argv[:3]==['systemctl','--no-block','start']:
                f.clock[0]+=38.8;after_start[0]=True
            if after_start[0] and argv[:2]==['journalctl','--no-pager']:
                self.assertLessEqual(seconds,.21);f.clock[0]+=.3
            return value
        f.client.run=run
        with self.assertRaises(core.Stop):f.step('candidate_start')
        self.assertEqual(f.journal.phase,'candidate_start_intent')
    def test_assessment_is_allocated_budget_not_a_rehearsal_latency_claim(self):
        value=m.assess_budget(admission_seconds=30,manager_start_seconds=40,observation_seconds=39)
        self.assertEqual(value['unallocated_seconds'],9)
        self.assertIs(value['startup_success_guaranteed'],False)
        for args in ((40,40,39),(30,40,40),(30,39,39)):
            with self.assertRaises(core.Stop):m.assess_budget(admission_seconds=args[0],manager_start_seconds=args[1],observation_seconds=args[2])
