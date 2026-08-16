import importlib.util
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "scripts" / "phase15_preflight_contract.py"
PACKAGE_ID = "phase15-dual-protocol-bootstrap-20260811-001"
MANIFEST_SHA256 = "a" * 64
COLLECTOR_SHA256 = "b" * 64
EXPECTED_HOST = "spain.test.invalid"
EXPECTED_OBSERVATION_NAMES = {
    "application_state", "architecture", "awg2_health", "backup_capability",
    "bridge_amn2sp3br0", "config_path", "container_capability",
    "container_cidr_172_29_252_0_28", "container_name", "database_state",
    "disk_space", "firewall", "interface_awg3", "os_compatibility", "python_3_12",
    "recovery_markers_phase14_phase15", "routes", "service_capability", "service_name",
    "state_root", "telegram_prerequisites", "udp_30002", "vpn_cidr_10_212_13_0_24",
}


def load_contract():
    if not CONTRACT.is_file():
        pytest.fail(f"missing preflight contract: {CONTRACT}")
    spec = importlib.util.spec_from_file_location("phase15_preflight_contract", CONTRACT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_claim(**overrides: object) -> dict[str, object]:
    claim: dict[str, object] = {
        "claim_id": "phase15-preflight-test-001",
        "collector_sha256": COLLECTOR_SHA256,
        "consumed_at": None,
        "expected_host": EXPECTED_HOST,
        "expires_at": "2099-08-11T12:00:00Z",
        "future_gate": "PREFLIGHT",
        "issued_at": "2099-08-11T11:00:00Z",
        "manifest_sha256": MANIFEST_SHA256,
        "package_id": PACKAGE_ID,
        "schema": "amn2.phase15.readonly-preflight-claim.v1",
        "status": "issued",
    }
    claim.update(overrides)
    return claim


def observations(*, stopped: bool = False) -> list[dict[str, str]]:
    return [
        {"name": name, "observation_sha256": hashlib.sha256(name.encode()).hexdigest(), "state": "stop" if stopped and name == "udp_30002" else "pass"}
        for name in sorted(EXPECTED_OBSERVATION_NAMES)
    ]


def test_claim_lifecycle_is_exact_checksum_host_and_future_gate_bound():
    contract = load_contract()
    now = datetime(2099, 8, 11, 11, 30, tzinfo=timezone.utc)

    accepted = contract.validate_claim(
        valid_claim(),
        package_id=PACKAGE_ID,
        manifest_sha256=MANIFEST_SHA256,
        collector_sha256=COLLECTOR_SHA256,
        expected_host=EXPECTED_HOST,
        now=now,
    )

    assert accepted["claim_id"] == "phase15-preflight-test-001"


@pytest.mark.parametrize(
    "overrides",
    [
        {"package_id": "phase15-wrong"},
        {"manifest_sha256": "0" * 64},
        {"collector_sha256": "1" * 64},
        {"expected_host": "other.test.invalid"},
        {"future_gate": "APPLICATION_STAGE"},
        {"status": "consumed", "consumed_at": "2099-08-11T11:20:00Z"},
        {"expires_at": "2099-08-11T11:00:00Z"},
    ],
)
def test_claim_rejects_mismatch_expiry_or_reuse(overrides: dict[str, object]):
    contract = load_contract()

    with pytest.raises(contract.PreflightContractError):
        contract.validate_claim(
            valid_claim(**overrides),
            package_id=PACKAGE_ID,
            manifest_sha256=MANIFEST_SHA256,
            collector_sha256=COLLECTOR_SHA256,
            expected_host=EXPECTED_HOST,
            now=datetime(2099, 8, 11, 11, 30, tzinfo=timezone.utc),
        )


def test_consumed_claim_cannot_be_validated_twice():
    contract = load_contract()
    claim = valid_claim()

    consumed = contract.consume_claim(claim, consumed_at="2099-08-11T11:40:00Z")

    assert consumed["status"] == "consumed"
    assert consumed["consumed_at"] == "2099-08-11T11:40:00Z"
    with pytest.raises(contract.PreflightContractError):
        contract.validate_claim(
            consumed,
            package_id=PACKAGE_ID,
            manifest_sha256=MANIFEST_SHA256,
            collector_sha256=COLLECTOR_SHA256,
            expected_host=EXPECTED_HOST,
            now=datetime(2099, 8, 11, 11, 41, tzinfo=timezone.utc),
        )


def test_success_evidence_binds_claim_timestamps_transport_and_safe_observations():
    contract = load_contract()

    evidence = contract.bind_evidence(
        valid_claim(),
        observations=observations(),
        stop_reasons=[],
        started_at="2099-08-11T11:31:00Z",
        ended_at="2099-08-11T11:32:00Z",
        transport_disposition="read_only_completed",
        ssh_used=True,
    )

    assert evidence == {
        "collector_sha256": COLLECTOR_SHA256,
        "decision": "pass",
        "ended_at": "2099-08-11T11:32:00Z",
        "expected_host": EXPECTED_HOST,
        "manifest_sha256": MANIFEST_SHA256,
        "observations": observations(),
        "package_id": PACKAGE_ID,
        "safety": {
            "live_mutation": False,
            "raw_output_persisted": False,
            "remote_file_written": False,
            "ssh_used": True,
        },
        "schema": "amn2.phase15.readonly-preflight-evidence.v1",
        "started_at": "2099-08-11T11:31:00Z",
        "stop_reasons": [],
        "transport_disposition": "read_only_completed",
    }


def test_stop_evidence_requires_classified_reason_and_stop_observation():
    contract = load_contract()

    evidence = contract.bind_evidence(
        valid_claim(),
        observations=observations(stopped=True),
        stop_reasons=["resource_conflict"],
        started_at="2099-08-11T11:31:00Z",
        ended_at="2099-08-11T11:32:00Z",
        transport_disposition="read_only_completed",
        ssh_used=True,
    )

    assert evidence["decision"] == "stop"
    assert evidence["stop_reasons"] == ["resource_conflict"]


def test_failure_outcome_is_sanitized_and_binds_transport_disposition():
    contract = load_contract()

    outcome = contract.bind_failure(
        valid_claim(),
        reason_code="transport_failed",
        started_at="2099-08-11T11:31:00Z",
        ended_at="2099-08-11T11:32:00Z",
        transport_disposition="read_only_failed",
        ssh_used=True,
    )

    assert outcome["schema"] == "amn2.phase15.readonly-preflight-failure.v1"
    assert outcome["reason_code"] == "transport_failed"
    assert outcome["decision"] == "stop"
    assert outcome["safety"]["ssh_used"] is True
    assert {"stdout", "stderr", "raw", "credentials"}.isdisjoint(outcome)


@pytest.mark.parametrize(
    "unsafe_value",
    [
        "123456789:abcdefghijklmnopqrstuvwxyzABCDEFGHIJK",
        "Bearer synthetic-sensitive-value",
        "PrivateKey=synthetic-sensitive-value",
    ],
)
def test_contract_rejects_secret_or_raw_command_material(unsafe_value: str):
    contract = load_contract()
    unsafe = observations()
    unsafe[0] = dict(unsafe[0], name=unsafe_value)

    with pytest.raises(contract.PreflightContractError):
        contract.bind_evidence(
            valid_claim(),
            observations=unsafe,
            stop_reasons=[],
            started_at="2099-08-11T11:31:00Z",
            ended_at="2099-08-11T11:32:00Z",
            transport_disposition="read_only_completed",
            ssh_used=False,
        )


@pytest.mark.parametrize(
    "reason",
    ["arbitrary_reason", "transport_failed", "Bearer synthetic-sensitive-value"],
)
def test_evidence_rejects_non_collector_stop_reasons(reason: str):
    contract = load_contract()

    with pytest.raises(contract.PreflightContractError):
        contract.bind_evidence(
            valid_claim(),
            observations=observations(stopped=True),
            stop_reasons=[reason],
            started_at="2099-08-11T11:31:00Z",
            ended_at="2099-08-11T11:32:00Z",
            transport_disposition="read_only_completed",
            ssh_used=True,
        )


@pytest.mark.parametrize(
    "host",
    ["-bad", "user@spain.test.invalid", "Spain.test.invalid", "spain..test.invalid", "spain_test.invalid"],
)
def test_claim_rejects_unsafe_expected_host_grammar(host: str):
    contract = load_contract()

    with pytest.raises(contract.PreflightContractError):
        contract.validate_claim(
            valid_claim(expected_host=host),
            package_id=PACKAGE_ID,
            manifest_sha256=MANIFEST_SHA256,
            collector_sha256=COLLECTOR_SHA256,
            expected_host=host,
            now=datetime(2099, 8, 11, 11, 30, tzinfo=timezone.utc),
        )


@pytest.mark.parametrize("name", ["unknown_observation", "Bearer synthetic-sensitive-value"])
def test_evidence_requires_exact_observation_inventory(name: str):
    contract = load_contract()
    invalid = observations()
    invalid[0] = dict(invalid[0], name=name)
    invalid.sort(key=lambda item: item["name"])

    with pytest.raises(contract.PreflightContractError):
        contract.bind_evidence(
            valid_claim(),
            observations=invalid,
            stop_reasons=[],
            started_at="2099-08-11T11:31:00Z",
            ended_at="2099-08-11T11:32:00Z",
            transport_disposition="read_only_completed",
            ssh_used=True,
        )


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("name", {"unexpected": "mapping"}),
        ("name", ["application_state"]),
        ("state", {"unexpected": "mapping"}),
        ("state", ["pass"]),
    ],
)
def test_observation_wrong_container_types_raise_classified_contract_error(field: str, invalid: object):
    contract = load_contract()
    values = observations()
    values[0] = dict(values[0], **{field: invalid})

    with pytest.raises(contract.PreflightContractError):
        contract.bind_evidence(
            valid_claim(),
            observations=values,
            stop_reasons=[],
            started_at="2099-08-11T11:31:00Z",
            ended_at="2099-08-11T11:32:00Z",
            transport_disposition="read_only_completed",
            ssh_used=True,
        )


@pytest.mark.parametrize("invalid", [{"reason": "resource_conflict"}, ["resource_conflict"]])
def test_stop_reason_wrong_container_types_raise_classified_contract_error(invalid: object):
    contract = load_contract()

    with pytest.raises(contract.PreflightContractError):
        contract.bind_evidence(
            valid_claim(),
            observations=observations(stopped=True),
            stop_reasons=[invalid],
            started_at="2099-08-11T11:31:00Z",
            ended_at="2099-08-11T11:32:00Z",
            transport_disposition="read_only_completed",
            ssh_used=True,
        )


@pytest.mark.parametrize(
    ("stopped_name", "reason"),
    [
        ("udp_30002", "observation_failed"),
        ("recovery_markers_phase14_phase15", "resource_conflict"),
        ("architecture", "resource_conflict"),
        ("udp_30002", "identity_mismatch"),
    ],
)
def test_stop_reasons_must_exactly_match_runner_observation_categories(stopped_name: str, reason: str):
    contract = load_contract()
    values = observations()
    for item in values:
        if item["name"] == stopped_name:
            item["state"] = "stop"

    with pytest.raises(contract.PreflightContractError):
        contract.bind_evidence(
            valid_claim(),
            observations=values,
            stop_reasons=[reason],
            started_at="2099-08-11T11:31:00Z",
            ended_at="2099-08-11T11:32:00Z",
            transport_disposition="read_only_completed",
            ssh_used=True,
        )


@pytest.mark.parametrize(
    ("stopped_name", "reason"),
    [
        ("udp_30002", "resource_conflict"),
        ("recovery_markers_phase14_phase15", "recovery_incomplete"),
        ("architecture", "observation_failed"),
    ],
)
def test_stop_reasons_accept_exact_runner_category_mapping(stopped_name: str, reason: str):
    contract = load_contract()
    values = observations()
    for item in values:
        if item["name"] == stopped_name:
            item["state"] = "stop"

    evidence = contract.bind_evidence(
        valid_claim(),
        observations=values,
        stop_reasons=[reason],
        started_at="2099-08-11T11:31:00Z",
        ended_at="2099-08-11T11:32:00Z",
        transport_disposition="read_only_completed",
        ssh_used=True,
    )

    assert evidence["stop_reasons"] == [reason]
