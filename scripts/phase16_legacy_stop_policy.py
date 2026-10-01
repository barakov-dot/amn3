"""Operator-approved 2026-10-01 policy, NOT an approved live operation.

The exception is only old55dc -> candidate6e68235 for the bot. A future
checksum-bound packet must include this contract and independently prove current
source provenance, clean stop, writer ownership and zero persisted pending work.
Hashes here constrain caller-supplied facts; they do not collect those facts.
No CLI, service calls, restore, replay, SSH or approval consumption occurs here.
"""
import re
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_binding as binding

require = core.require
OLD_COMMIT = '55dc243b8e6c6bdb57f8301b56326e4cd4072d19'
OLD_HANDLERS = '31987a5fb46c9cee35c16817e805da76eef8fde178a7ce8cf86a5c9a6adf7d39'
OLD_WORKFLOWS = 'b2debc222f2b820a71b75b03e42a5afec3f923ff9f740f49619f22ee2e9355b4'
POLICY = 'PHASE16_LEGACY_STOP_POLICY_20261001'
DRAIN = 'NOT_OBSERVABLE_ACCEPTED_BY_OPERATOR'


def bind(prepared, *, packet_sha256, old_commit, old_handlers_sha256, old_workflows_sha256):
    # Structural validation at the recorded time; freshness is host admission's
    # responsibility, never silently refreshed by this local policy constructor.
    try:
        binding.validate_prepared(prepared, now=prepared['target_contract']['observed_at'])
    except (KeyError, TypeError):
        raise core.Stop('legacy_policy_inputs') from None
    require(isinstance(packet_sha256,str) and re.fullmatch('[0-9a-f]{64}',packet_sha256), 'legacy_policy_packet')
    require(old_commit==OLD_COMMIT and old_handlers_sha256==OLD_HANDLERS
            and old_workflows_sha256==OLD_WORKFLOWS, 'legacy_policy_source')
    manifest=prepared['coordinator_manifest']
    value=dict(schema='phase16.legacy-stop-policy.v1',policy_id=POLICY,policy_approved_on='2026-10-01',
        operation_id=manifest['operation_id'],boot_id=manifest['boot_id'],
        journal_binding=core.digest(manifest),target_contract_sha256=manifest['target_contract_sha256'],
        packet_sha256=packet_sha256,subject=core.BOT,old_commit=OLD_COMMIT,
        old_handlers_sha256=OLD_HANDLERS,old_workflows_sha256=OLD_WORKFLOWS,
        candidate_commit=core.CANDIDATE,old_handler_drain=DRAIN,automatic_restore=False,
        automatic_replay=False,live_authorized=False)
    return dict(value,sha256=core.digest(value))


def validate(value, prepared):
    require(isinstance(value,dict), 'legacy_policy_shape')
    try:
        expected=bind(prepared,packet_sha256=value['packet_sha256'],old_commit=value['old_commit'],
            old_handlers_sha256=value['old_handlers_sha256'],old_workflows_sha256=value['old_workflows_sha256'])
        # Canonical bytes also reject false -> 0 / true -> 1 type substitutions.
        require(core.encoded(value)==core.encoded(expected), 'legacy_policy_binding')
    except (KeyError,TypeError,ValueError):
        raise core.Stop('legacy_policy_shape') from None
    return value['sha256']


def recovery(journal, value, prepared):
    validate(value,prepared)
    require(isinstance(journal,core.Journal) and journal.binding==value['journal_binding'], 'legacy_policy_journal')
    fresh=core.Journal.load(journal.directory,journal.manifest)
    require(fresh.events==journal.events, 'legacy_policy_journal')
    if fresh.candidate_requested:return 'PRESERVE_DB_MANUAL_RECOVERY'
    if fresh.phase=='prepared':return 'LEAVE_OLD_RUNTIME'
    # Accepted uncertainty must never be converted into drain_proven=True for
    # the core recovery router. Even pre-start DB restore requires new evidence
    # about external effects and a separate operator decision.
    return 'HOLD_FENCE_MANUAL_RECOVERY'
