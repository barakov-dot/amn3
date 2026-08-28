"""Temporary IPv4 network integration for the existing one-peer Spain pilot.

Pure planning/ownership functions. No remote execution on import, no persistent
firewall configuration, and no modification of existing AWG2 rules.
"""
import hashlib
import json
import re

TABLE = 'amn2_p16_awg31'
PREFIX = TABLE + ':'
LOCATIONS = {
    'dnat': (TABLE, 'prerouting'), 'masq': (TABLE, 'postrouting'),
    'in': ('filter', 'FORWARD'), 'out': ('filter', 'FORWARD'),
    'return': ('filter', 'FORWARD'),
}

class FirewallError(ValueError):
    pass

class AtomicRejected(FirewallError):
    """Native nft rejected the complete batch without committing changes."""
    pass

def render(uplink):
    if not isinstance(uplink, str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,15}', uplink) or uplink in ('lo', 'amn2sp31p0'):
        raise FirewallError('invalid_uplink')
    return '\n'.join([
        f'create table ip {TABLE}',
        f'add chain ip {TABLE} prerouting {{ type nat hook prerouting priority -100; policy accept; }}',
        f'add chain ip {TABLE} postrouting {{ type nat hook postrouting priority 100; policy accept; }}',
        f'add rule ip {TABLE} prerouting iifname "{uplink}" ip daddr 138.124.181.246 udp dport 30002 counter dnat to 172.29.252.2:30002 comment "{PREFIX}dnat"',
        f'add rule ip {TABLE} postrouting ip saddr 172.29.252.2 oifname "{uplink}" counter masquerade comment "{PREFIX}masq"',
        f'insert rule ip filter FORWARD iifname "{uplink}" oifname "amn2sp31p0" ip daddr 172.29.252.2 udp dport 30002 ct status dnat counter accept comment "{PREFIX}in"',
        f'insert rule ip filter FORWARD iifname "amn2sp31p0" oifname "{uplink}" ip saddr 172.29.252.2 counter accept comment "{PREFIX}out"',
        f'insert rule ip filter FORWARD iifname "{uplink}" oifname "amn2sp31p0" ip daddr 172.29.252.2 ct state established,related counter accept comment "{PREFIX}return"',
    ]) + '\n'

def _scope(document):
    if not isinstance(document, dict) or not isinstance(document.get('nftables'), list):
        raise FirewallError('invalid_ruleset')
    owned, handles, tags, chains = set(), [], set(), set()
    table_seen = False
    for index, entry in enumerate(document['nftables']):
        if not isinstance(entry, dict) or len(entry) != 1:
            raise FirewallError('invalid_entry')
        kind, value = next(iter(entry.items()))
        if not isinstance(value, dict):
            continue
        comment = value.get('comment', '')
        labelled = isinstance(comment, str) and comment.startswith(PREFIX)
        in_table = value.get('family') == 'ip' and (value.get('table') == TABLE or kind == 'table' and value.get('name') == TABLE)
        if not labelled and not in_table:
            continue
        if kind == 'table' and in_table and not table_seen:
            table_seen = True
        elif kind == 'chain' and in_table and value.get('name') in ('prerouting','postrouting') and value['name'] not in chains:
            chains.add(value['name'])
        elif kind == 'rule' and labelled:
            tag = comment[len(PREFIX):]
            if tag not in LOCATIONS or tag in tags or value.get('family') != 'ip' or (value.get('table'),value.get('chain')) != LOCATIONS[tag]:
                raise FirewallError('foreign_or_duplicate_owned_rule')
            handle = value.get('handle')
            if type(handle) is not int or handle <= 0:
                raise FirewallError('invalid_rule_handle')
            tags.add(tag)
            if value['table'] == 'filter':
                handles.append(handle)
        else:
            raise FirewallError('foreign_object_in_owned_scope')
        owned.add(index)
    return owned, handles, tags, chains, table_seen

def complete(document):
    _, handles, tags, chains, table = _scope(document)
    return table and len(handles) == 3 and tags == set(LOCATIONS) and chains == {'prerouting','postrouting'}

def rollback(document):
    _, handles, _, _, table = _scope(document)
    commands = [f'delete rule ip filter FORWARD handle {h}' for h in handles]
    if table:
        commands.append(f'delete table ip {TABLE}')
    return '\n'.join(commands) + ('\n' if commands else '')

def baseline(document):
    owned = _scope(document)[0]
    def normalized(value):
        if isinstance(value, list):
            return [normalized(v) for v in value]
        if isinstance(value, dict):
            return {k:({field:(0 if field in ('packets','bytes') else normalized(item)) for field,item in v.items()}
                       if k == 'counter' and isinstance(v,dict) else normalized(v)) for k,v in value.items()}
        return value
    remaining = [entry for index,entry in enumerate(document['nftables']) if index not in owned]
    return hashlib.sha256(json.dumps(normalized(remaining),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def apply_rules(read_rules, execute, awg2_snapshot, verify_network, uplink):
    attempted = False
    locus = 'precheck'
    try:
        before = read_rules()
        if rollback(before):
            raise FirewallError('owned_resources_already_exist')
        targets = [entry['chain'] for entry in before['nftables'] if 'chain' in entry and entry['chain'].get('family') == 'ip' and entry['chain'].get('table') == 'filter' and entry['chain'].get('name') == 'FORWARD']
        if len(targets) != 1 or targets[0].get('hook') != 'forward' or targets[0].get('policy') != 'drop':
            raise FirewallError('unexpected_forward_chain')
        original = baseline(before)
        awg2_before = awg2_snapshot()
        batch = render(uplink)
        locus = 'native_check'
        execute(batch, True)
        locus = 'state_fence'
        fenced = read_rules()
        if rollback(fenced) or baseline(fenced) != original or awg2_snapshot() != awg2_before:
            raise FirewallError('state_changed_before_apply')
        locus = 'apply'
        attempted = True
        try:
            execute(batch, False)
        except AtomicRejected:
            attempted = False
            raise
        locus = 'readback'
        after = read_rules()
        if not complete(after) or baseline(after) != original:
            raise FirewallError('firewall_readback_failed')
        locus = 'awg2_equality'
        if awg2_snapshot() != awg2_before:
            raise FirewallError('awg2_changed')
        locus = 'network_probe'
        if verify_network() is not True:
            raise FirewallError('network_probe_failed')
        locus = 'final_readback'
        after = read_rules()
        if not complete(after) or baseline(after) != original or awg2_snapshot() != awg2_before:
            raise FirewallError('post_probe_state_changed')
        return {'result':'applied_client_test_pending', 'awg2_state_equal':True, 'existing_firewall_equal':True, 'network_probe_pass':True, 'baseline_sha256':original, 'forward_handles':_scope(after)[1]}
    except Exception as error:
        result = {'result':'stop_before_mutation', 'failure_locus':locus, 'exception_class':type(error).__name__}
        if not attempted:
            return result
        result['result'] = 'stop_requires_attention'
        try:
            cleanup = rollback(read_rules())
            if cleanup:
                execute(cleanup, True)
                execute(cleanup, False)
            final = read_rules()
            result['owned_resources_absent'] = rollback(final) == ''
            result['existing_firewall_equal'] = baseline(final) == original
            result['awg2_state_equal'] = awg2_snapshot() == awg2_before
            if result['owned_resources_absent'] and result['existing_firewall_equal'] and result['awg2_state_equal']:
                result['result'] = 'stop_rolled_back'
        except Exception as rollback_error:
            result['rollback_exception_class'] = type(rollback_error).__name__
        return result
