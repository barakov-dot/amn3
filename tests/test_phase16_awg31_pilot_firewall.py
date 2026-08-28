import copy
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'scripts/vps/phase16_awg31_pilot_firewall.py'

def load():
    spec = importlib.util.spec_from_file_location('pilot_firewall', SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class PilotFirewallTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SOURCE.is_file(), 'pilot host firewall integration is missing')
        self.m = load()

    def test_plan_adds_only_pilot_nat_and_three_scoped_forward_rules(self):
        lines = self.m.render('eth0').splitlines()
        self.assertEqual(len(lines), 8)
        self.assertTrue(lines[0].startswith('create table ip amn2_p16_awg31'))
        self.assertEqual(sum(line.startswith('insert rule ip filter FORWARD ') for line in lines), 3)
        self.assertEqual(sum('dnat to 172.29.252.2:30002' in line for line in lines), 1)
        self.assertEqual(sum('masquerade' in line for line in lines), 1)
        for line in lines[3:]:
            self.assertIn('172.29.252.2', line)
            self.assertIn('comment "amn2_p16_awg31:', line)
        self.assertNotIn('flush', '\n'.join(lines))
        self.assertNotIn('delete', '\n'.join(lines))

    def test_untrusted_uplink_cannot_inject_a_firewall_command(self):
        for value in ('', 'lo', 'amn2sp31p0', 'eth0; flush ruleset', 'eth0\n', '"eth0"'):
            with self.subTest(value=value), self.assertRaises(self.m.FirewallError):
                self.m.render(value)

    def fixture(self):
        entries = [{'table':{'family':'ip','name':'amn2_p16_awg31','handle':90}}]
        for name in ('prerouting','postrouting'):
            entries.append({'chain':{'family':'ip','table':'amn2_p16_awg31','name':name}})
        for tag,chain,table,handle in (('dnat','prerouting','amn2_p16_awg31',91),('masq','postrouting','amn2_p16_awg31',92),('in','FORWARD','filter',101),('out','FORWARD','filter',102),('return','FORWARD','filter',103)):
            entries.append({'rule':{'family':'ip','table':table,'chain':chain,'handle':handle,'comment':'amn2_p16_awg31:'+tag,'expr':[{'counter':{'packets':0,'bytes':0}}]}})
        return {'nftables':entries}

    def test_rollback_deletes_only_three_owned_handles_and_own_table(self):
        text = self.m.rollback(self.fixture())
        self.assertEqual(set(text.splitlines()), {'delete rule ip filter FORWARD handle 101','delete rule ip filter FORWARD handle 102','delete rule ip filter FORWARD handle 103','delete table ip amn2_p16_awg31'})

    def test_rollback_refuses_unowned_addition_in_own_namespace(self):
        doc = self.fixture()
        doc['nftables'].append({'rule':{'family':'ip','table':'amn2_p16_awg31','chain':'prerouting','handle':999,'comment':'foreign','expr':[]}})
        with self.assertRaises(self.m.FirewallError):
            self.m.rollback(doc)

    def test_rollback_refuses_forged_comment_outside_approved_location(self):
        doc = self.fixture()
        doc['nftables'][-1]['rule']['chain'] = 'INPUT'
        with self.assertRaises(self.m.FirewallError):
            self.m.rollback(doc)

    def test_baseline_ignores_counters_but_detects_existing_rule_change(self):
        original = {'nftables':[{'rule':{'family':'inet','table':'amn2_spain','chain':'forward','handle':7,'expr':[{'counter':{'packets':10,'bytes':20}},{'accept':None}]}}]}
        after = copy.deepcopy(original)
        after['nftables'][0]['rule']['expr'][0]['counter']['packets'] = 11
        after['nftables'].extend(self.fixture()['nftables'])
        self.assertEqual(self.m.baseline(original), self.m.baseline(after))
        after['nftables'][0]['rule']['expr'][1] = {'drop':None}
        self.assertNotEqual(self.m.baseline(original), self.m.baseline(after))

    def test_no_resources_means_empty_rollback(self):
        self.assertEqual(self.m.rollback({'nftables':[]}), '')

    def test_baseline_preserves_named_counter_identity(self):
        before = {'nftables':[{'counter':{'family':'ip','table':'filter','name':'existing','handle':9,'packets':1,'bytes':10}}]}
        after = copy.deepcopy(before)
        after['nftables'][0]['counter']['packets'] = 2
        self.assertEqual(self.m.baseline(before), self.m.baseline(after))
        after['nftables'][0]['counter']['name'] = 'different'
        self.assertNotEqual(self.m.baseline(before), self.m.baseline(after))

    def exercise(self, network_ok=True, native_ok=True, drift=False, atomic_rejection=False):
        self.assertTrue(callable(getattr(self.m, 'apply_rules', None)), 'guarded firewall application is missing')
        original = {'nftables':[{'chain':{'family':'ip','table':'filter','name':'FORWARD','hook':'forward','policy':'drop'}}]}
        state = {'doc':copy.deepcopy(original), 'writes':[], 'checks':0}
        def execute(batch, check):
            if check:
                state['checks'] += 1
                if not native_ok:
                    raise RuntimeError('native check failed')
                return
            state['writes'].append(batch)
            if batch.startswith('create table'):
                state['doc']['nftables'].extend(self.fixture()['nftables'])
                if atomic_rejection:
                    raise self.m.AtomicRejected('a racing writer created this namespace')
                if drift:
                    state['doc']['nftables'][0]['chain']['policy'] = 'accept'
            else:
                state['doc']['nftables'] = state['doc']['nftables'][:1]
        result = self.m.apply_rules(lambda:copy.deepcopy(state['doc']), execute, lambda:'awg2-unchanged', lambda:network_ok, 'eth0')
        return result, state, original

    def test_apply_is_native_checked_and_preserves_existing_firewall(self):
        result,state,_ = self.exercise()
        self.assertEqual(result['result'], 'applied_client_test_pending')
        self.assertEqual(len(state['writes']), 1)
        self.assertEqual(state['checks'], 1)
        self.assertTrue(result['awg2_state_equal'])
        self.assertTrue(self.m.complete(state['doc']))

    def test_failed_network_probe_rolls_back_only_added_resources(self):
        result,state,original = self.exercise(network_ok=False)
        self.assertEqual(result['result'], 'stop_rolled_back')
        self.assertEqual(state['doc'], original)
        self.assertEqual(len(state['writes']), 2)
        self.assertNotIn('flush', state['writes'][1])

    def test_failed_native_check_makes_no_real_firewall_write(self):
        result,state,original = self.exercise(native_ok=False)
        self.assertEqual(result['result'], 'stop_before_mutation')
        self.assertEqual(state['writes'], [])
        self.assertEqual(state['doc'], original)

    def test_unrelated_drift_is_not_overwritten_during_rollback(self):
        result,state,_ = self.exercise(drift=True)
        self.assertEqual(result['result'], 'stop_requires_attention')
        self.assertFalse(self.m.complete(state['doc']))
        self.assertEqual(state['doc']['nftables'][0]['chain']['policy'], 'accept')

    def test_atomic_rejection_never_deletes_a_racing_writers_resources(self):
        result,state,_ = self.exercise(atomic_rejection=True)
        self.assertEqual(result['result'], 'stop_before_mutation')
        self.assertEqual(len(state['writes']), 1)
        self.assertTrue(self.m.complete(state['doc']))

if __name__ == '__main__':
    unittest.main()
