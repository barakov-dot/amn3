"""Pure Phase16 metadata compatibility parser; never recovery execution.

Callers supply independently verified bindings and bounded metadata. A valid
shape does not establish ownership, quiescence, backup integrity or rollback.
Historical collector/driver are deliberately neither imported nor modified.
"""
import json
import re

MILESTONES = (
    "transaction_created", "package_verified", "request_bound", "awg2_before_captured",
    "package_installed", "claims_issued", "application_entry", "application_complete",
    "runtime_entry", "runtime_complete", "awg2_after_captured", "awg2_equality_confirmed",
    "coordinator_outcome_written", "transaction_outcome_written",
)
FAILURE_LOCI = frozenset({
    "package_verification", "request_binding", "awg2_before_snapshot", "package_installation",
    "claim_publication", "application_stage", "runtime_stage", "awg2_after_snapshot",
    "awg2_equality", "coordinator_outcome_publication", "transaction_outcome_publication",
    "milestone_publication",
})
FAILURE_CLASSES = frozenset({"contract", "process_exit", "stderr_not_empty", "stdout_shape", "output_bound", "timeout", "os_error", "internal"})
CLAIM_CLASSES = frozenset({"issued_not_entered", "consumed_entry_only", "unavailable", "invalid"})
BINDING_KEYS = frozenset({"package_id", "transaction_id", "package_identity_sha256", "manifest_sha256", "state_sha256", "rollback_scope_sha256"})
BASE_KEYS = BINDING_KEYS | {"completed_milestones", "last_completed_milestone", "general_issuance_enabled", "raw_output_persisted", "schema"}
FAILURE_KEYS = frozenset({"application_claim_entry", "runtime_claim_entry", "failure_class", "failure_locus", "rollback_milestones", "rollback_status", "runtime_image"})
OUTCOME_FAILURE_KEYS = frozenset({"schema", "result", "package_id", "transaction_id", "awg2_state_equal", "general_issuance_enabled", "backup_preserved"})
FAILURE_RESULTS = {
    "recovery_required": ("recovery_required", [], "valid_recovery_required"),
    "rollback_failed": ("attempt_failed", ["rollback_started"], "valid_rollback_failed"),
    "rolled_back": ("attempts_completed_unverified", ["rollback_started", "rollback_attempts_completed"], "valid_rolled_back_readback_required"),
}


def parse_canonical(raw):
    """Decode canonical coordinator JSON only; fixed error never echoes input."""
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError
            result[key] = value
        return result

    def reject_constant(_):
        raise ValueError

    try:
        if not isinstance(raw, bytes) or not 1 <= len(raw) <= 65536:
            raise ValueError
        value = json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=reject_constant)
        encoded = (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")
        if not isinstance(value, dict) or encoded != raw:
            raise ValueError
        return value
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise ValueError("invalid_metadata") from None


def _bindings_valid(bindings):
    if not isinstance(bindings, dict) or set(bindings) != BINDING_KEYS:
        return False
    for key, value in bindings.items():
        pattern = r"[0-9a-f]{64}" if key.endswith("sha256") else r"[a-z0-9][a-z0-9._-]{0,99}"
        if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
            return False
    return True


def _milestone_shape(doc, bindings, failure):
    keys = BASE_KEYS | (FAILURE_KEYS if failure else set())
    schema = "amn2.phase16.controlled-stage-" + ("failure-locus" if failure else "milestones") + ".v1"
    if not isinstance(doc, dict) or set(doc) != keys or doc["schema"] != schema:
        return False
    if any(doc[key] != value for key, value in bindings.items()):
        return False
    if doc["general_issuance_enabled"] is not False or doc["raw_output_persisted"] is not False:
        return False
    completed = doc["completed_milestones"]
    if (not isinstance(completed, list) or not 1 <= len(completed) <= len(MILESTONES)
            or tuple(completed) != MILESTONES[:len(completed)] or doc["last_completed_milestone"] != completed[-1]):
        return False
    if failure:
        if any(not isinstance(doc[key], str) for key in FAILURE_KEYS - {"rollback_milestones"}):
            return False
        if doc["failure_class"] not in FAILURE_CLASSES or doc["failure_locus"] not in FAILURE_LOCI:
            return False
        if doc["application_claim_entry"] not in CLAIM_CLASSES or doc["runtime_claim_entry"] not in CLAIM_CLASSES:
            return False
        if doc["runtime_image"] not in {"absent", "present_baseline_unknown", "query_failed"}:
            return False
    return True


def classify_metadata(outcome, milestone_document, *, expected_bindings):
    """Classify a matched pair; 'valid' means schema/bindings only, never cleanup GO.

    Failure outcome files have fewer bindings; their companion failure-locus
    document is mandatory. The shortened stdout outcome is intentionally invalid.
    """
    try:
        if not _bindings_valid(expected_bindings) or not isinstance(outcome, dict):
            return "invalid"
        if outcome.get("schema") != "amn2.phase16.controlled-stage-outcome.v1" or outcome.get("general_issuance_enabled") is not False:
            return "invalid"
        if any(outcome.get(key) != expected_bindings[key] for key in ("package_id", "transaction_id")):
            return "invalid"
        result = outcome.get("result")
        if result == "application_and_awg31_staged":
            keys = BINDING_KEYS | {"schema", "result", "awg2_state_equal", "general_issuance_enabled"}
            if (set(outcome) != keys or outcome["awg2_state_equal"] is not True
                    or any(outcome[key] != value for key, value in expected_bindings.items())
                    or not _milestone_shape(milestone_document, expected_bindings, False)
                    or tuple(milestone_document["completed_milestones"]) != MILESTONES):
                return "invalid"
            return "valid_staged_awg2_equal"
        if result not in FAILURE_RESULTS or set(outcome) != OUTCOME_FAILURE_KEYS:
            return "invalid"
        if outcome["awg2_state_equal"] is not None or outcome["backup_preserved"] is not True:
            return "invalid"
        if not _milestone_shape(milestone_document, expected_bindings, True):
            return "invalid"
        status, steps, classification = FAILURE_RESULTS[result]
        if milestone_document["rollback_status"] != status or milestone_document["rollback_milestones"] != steps:
            return "invalid"
        return classification
    except (TypeError, KeyError, ValueError):
        return "invalid"
