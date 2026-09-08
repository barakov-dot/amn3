"""Pure synthetic metadata; no collectors, SSH or server resources."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/vps" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def parser():
    return load("recovery_metadata", "phase16_recovery_metadata.py")


@pytest.fixture
def evidence():
    coordinator = load("metadata_coordinator", "phase16_controlled_stage_coordinator.py")
    request = {"package_id": coordinator.PACKAGE_ID, "transaction_id": "synthetic-recovery-001",
               "manifest_sha256": "a" * 64, "package_identity_sha256": "b" * 64,
               "expected_current_state_sha256": "c" * 64, "rollback_scope_sha256": "d" * 64}
    doc = coordinator.build_milestone_document(request, list(coordinator.STAGE_MILESTONES[:7]))
    bindings = {key: doc[key] for key in ("package_id", "transaction_id", "manifest_sha256",
                "package_identity_sha256", "state_sha256", "rollback_scope_sha256")}
    doc.update(schema="amn2.phase16.controlled-stage-failure-locus.v1",
               application_claim_entry="consumed_entry_only", runtime_claim_entry="issued_not_entered",
               failure_class="timeout", failure_locus="application_stage", runtime_image="query_failed",
               rollback_status="recovery_required", rollback_milestones=[])
    outcome = {"schema": "amn2.phase16.controlled-stage-outcome.v1", "result": "recovery_required",
               "package_id": request["package_id"], "transaction_id": request["transaction_id"],
               "awg2_state_equal": None, "backup_preserved": True, "general_issuance_enabled": False}
    return bindings, outcome, doc


@pytest.mark.parametrize("result,status,steps,classification", [
    ("recovery_required", "recovery_required", [], "valid_recovery_required"),
    ("rollback_failed", "attempt_failed", ["rollback_started"], "valid_rollback_failed"),
    ("rolled_back", "attempts_completed_unverified", ["rollback_started", "rollback_attempts_completed"], "valid_rolled_back_readback_required"),
])
def test_current_failure_outcomes_are_recognized_without_authorizing_cleanup(parser, evidence, result, status, steps, classification):
    bindings, outcome, doc = evidence
    outcome["result"], doc["rollback_status"], doc["rollback_milestones"] = result, status, steps
    answer = parser.classify_metadata(outcome, doc, expected_bindings=bindings)
    assert answer == classification


@pytest.mark.parametrize("mutation", ["binding", "unknown", "rollback", "bool", "order", "empty", "stdout", "raw", "extra", "locus"])
def test_unknown_mismatched_or_incomplete_evidence_is_invalid(parser, evidence, mutation):
    bindings, outcome, doc = evidence
    if mutation == "binding": doc["state_sha256"] = "e" * 64
    if mutation == "unknown": outcome["result"] = "recovered"
    if mutation == "rollback": doc["rollback_milestones"] = ["rollback_started"]
    if mutation == "bool": outcome["backup_preserved"] = 1
    if mutation == "order": doc["completed_milestones"].reverse()
    if mutation == "empty": doc["completed_milestones"] = []
    if mutation == "stdout": outcome.pop("transaction_id")
    if mutation == "raw": doc["raw_output_persisted"] = True
    if mutation == "extra": outcome["log"] = "synthetic-sensitive-marker"
    if mutation == "locus": doc["failure_locus"] = "unknown"
    assert parser.classify_metadata(outcome, doc, expected_bindings=bindings) == "invalid"


def test_contradictory_pair_rejected(parser, evidence):
    bindings, outcome, doc = evidence
    outcome["result"] = "rolled_back"
    assert parser.classify_metadata(outcome, doc, expected_bindings=bindings) == "invalid"


def test_success_uses_full_bindings_and_complete_milestones(parser, evidence):
    bindings, _, _ = evidence
    coordinator = load("metadata_success", "phase16_controlled_stage_coordinator.py")
    request = dict(bindings, expected_current_state_sha256=bindings["state_sha256"])
    doc = coordinator.build_milestone_document(request, list(coordinator.STAGE_MILESTONES))
    outcome = dict(bindings, schema="amn2.phase16.controlled-stage-outcome.v1",
                   result="application_and_awg31_staged", awg2_state_equal=True, general_issuance_enabled=False)
    assert parser.classify_metadata(outcome, doc, expected_bindings=bindings) == "valid_staged_awg2_equal"
    outcome["manifest_sha256"] = "e" * 64
    assert parser.classify_metadata(outcome, doc, expected_bindings=bindings) == "invalid"


@pytest.mark.parametrize("raw", [b'{"x":1,"x":2}\n', b'{"x":NaN}\n', b'[]\n', b'{"x": 1}\n', b'x' * 65537], ids=['duplicate', 'nan', 'array', 'spacing', 'oversize'])
def test_bounded_canonical_parser_rejects_ambiguous_json(parser, raw):
    with pytest.raises(ValueError, match="invalid_metadata"):
        parser.parse_canonical(raw)


def test_canonical_round_trip(parser, evidence):
    _, outcome, _ = evidence
    raw = (json.dumps(outcome, sort_keys=True, separators=(",", ":")) + "\n").encode()
    assert parser.parse_canonical(raw) == outcome


def test_explicit_valid_binding_inventory_required(parser, evidence):
    bindings, outcome, doc = evidence
    bindings["state_sha256"] = "not-a-hash"
    assert parser.classify_metadata(outcome, doc, expected_bindings=bindings) == "invalid"


@pytest.mark.parametrize("scenario,expected", [
    ("application_partial_timeout", "valid_recovery_required"),
    ("runtime_partial_timeout", "valid_recovery_required"),
    ("rollback_error", "valid_rollback_failed"),
    ("awg2_after", "valid_rolled_back_readback_required"),
    ("success", "valid_staged_awg2_equal"),
])
def test_real_coordinator_offline_outputs_match_parser(parser, tmp_path, scenario, expected):
    spec = importlib.util.spec_from_file_location("existing_stage_harness", ROOT / "tests/test_phase16_controlled_stage_failure_locus.py")
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    coordinator = harness.load_coordinator()
    with harness.LocalStageHarness(coordinator, tmp_path, scenario) as run:
        request = run.header["request"]
        bindings = {key: request[key] for key in parser.BINDING_KEYS - {"state_sha256"}}
        bindings["state_sha256"] = request["expected_current_state_sha256"]
        if scenario == "success":
            run.execute()
            document_name = "milestones.json"
        else:
            with pytest.raises(Exception):
                run.execute()
            document_name = "failure-locus.json"
        outcome = parser.parse_canonical((run.transaction / "outcome.json").read_bytes())
        document = parser.parse_canonical((run.transaction / document_name).read_bytes())
        assert parser.classify_metadata(outcome, document, expected_bindings=bindings) == expected
