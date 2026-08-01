import copy
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "packaging" / "phase13-awg3-preflight"
FOUNDATION_PATH = ARTIFACT_ROOT / "phase12-equality-foundation.json"
MANIFEST_SCHEMA = ARTIFACT_ROOT / "manifest.schema.json"
EVIDENCE_SCHEMA = ARTIFACT_ROOT / "evidence.schema.json"
FAILURE_SCHEMA = ARTIFACT_ROOT / "failure-evidence.schema.json"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def contract_module():
    try:
        return importlib.import_module("scripts.phase13_awg3_preflight_contract")
    except ModuleNotFoundError as error:
        pytest.fail(f"Phase 13 contract module is missing: {error}")


def assert_every_object_is_closed(value: object) -> None:
    if isinstance(value, dict):
        if value.get("type") == "object":
            assert value["additionalProperties"] is False
        for nested in value.values():
            assert_every_object_is_closed(nested)
    elif isinstance(value, list):
        for nested in value:
            assert_every_object_is_closed(nested)


def test_phase12_foundation_contains_exact_accepted_safe_facts():
    foundation = load_json(FOUNDATION_PATH)

    assert foundation == {
        "schema": "amn2.phase13.phase12-equality-foundation.v1",
        "source_head": "ff115b63ca1329640ca13ae0a502d155f99b456b",
        "foreign": {
            "persistent_entries": 153,
            "stable_sha256": (
                "f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8"
            ),
            "equality_receipt_sha256": (
                "bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704"
            ),
        },
        "awg2": {
            "udp_port": 30001,
            "vpn_cidr": "10.212.12.0/24",
            "route_device": "amn2spbr0",
            "persistent_peers": 7,
            "live_peers": 7,
            "restart_count": 59,
            "forward_rule_count": 3,
            "web_listener": "127.0.0.1:3031",
            "bot_enabled": False,
        },
    }


def test_all_phase13_schemas_are_recursively_closed_objects():
    for path in (MANIFEST_SCHEMA, EVIDENCE_SCHEMA, FAILURE_SCHEMA):
        schema = load_json(path)

        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert schema["required"]
        assert_every_object_is_closed(schema)


def test_manifest_schema_requires_exact_fail_closed_contract():
    schema = load_json(MANIFEST_SCHEMA)

    assert set(schema["required"]) == {
        "schema",
        "outcome_id",
        "created_at",
        "expires_at",
        "target_role",
        "source_base",
        "source_head",
        "spain_overlay",
        "candidate",
        "artifacts",
        "foundation_sha256",
        "allowed_command_families",
        "forbidden_actions",
        "max_attempts",
        "remote_write_allowed",
        "package_build_allowed",
        "live_action_authorized",
    }
    assert schema["properties"]["schema"] == {
        "const": "amn2.phase13.awg3-readonly-preflight-manifest.v1"
    }
    assert schema["properties"]["target_role"] == {"const": "spain-primary"}
    assert schema["properties"]["source_base"] == {
        "const": "55dc243b8e6c6bdb57f8301b56326e4cd4072d19"
    }
    assert schema["properties"]["source_head"] == {
        "const": "ff115b63ca1329640ca13ae0a502d155f99b456b"
    }
    assert schema["properties"]["spain_overlay"] == {
        "const": "f1bf099ddb47da26a4080714376babaf5b0de92c"
    }
    assert schema["properties"]["max_attempts"] == {"const": 1}
    assert schema["properties"]["remote_write_allowed"] == {"const": False}
    assert schema["properties"]["package_build_allowed"] == {"const": False}
    assert schema["properties"]["live_action_authorized"] == {"const": False}


def build_test_manifest(contract, tmp_path: Path) -> tuple[Path, dict[str, object]]:
    collector = tmp_path / "collector.sh"
    collector.write_bytes(b"#!/bin/sh\nexit 0\n")
    manifest = contract.build_manifest(
        outcome_id="test-outcome-001",
        created_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        expires_at=datetime(2026, 8, 2, tzinfo=timezone.utc),
        artifact_paths=(collector,),
    )
    return collector, manifest


def valid_success_evidence(contract, manifest: dict[str, object]) -> dict[str, object]:
    return {
        "schema": "amn2.phase13.awg3-readonly-preflight.v1",
        "outcome_id": manifest["outcome_id"],
        "checked_at": "2026-08-01T12:00:00Z",
        "source_head": manifest["source_head"],
        "manifest_sha256": contract.sha256_bytes(contract.canonical_json_bytes(manifest)),
        "runner_sha256": "1" * 64,
        "collector_sha256": "2" * 64,
        "schema_sha256": "3" * 64,
        "phase12_foundation_sha256": manifest["foundation_sha256"],
        "candidate_resources": [
            {
                "resource": "udp_port",
                "declared_value": "30002",
                "state": "free",
                "observation_sha256": "4" * 64,
            }
        ],
        "awg2_equality": {
            "container_equal": True,
            "service_equal": True,
            "interface_equal": True,
            "udp_port_equal": True,
            "vpn_cidr_route_equal": True,
            "persistent_peers": 7,
            "live_peers": 7,
            "peer_set_sha256": "5" * 64,
            "restart_count": 59,
            "forward_rule_count": 3,
            "web_listener_equal": True,
            "bot_disabled": True,
            "equal": True,
        },
        "foreign_equality": {
            "persistent_entries": 153,
            "stable_sha256": (
                "f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8"
            ),
            "changed": 0,
            "equality_receipt_sha256": (
                "bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704"
            ),
            "equal": True,
        },
        "safety_receipt": {
            "mutation_attempted": False,
            "remote_file_written": False,
            "service_action_attempted": False,
            "container_action_attempted": False,
            "firewall_action_attempted": False,
            "secret_bearing_config_accessed": False,
            "raw_peer_identifiers_emitted": False,
            "raw_output_persisted": False,
        },
        "decision": "pass",
        "stop_reasons": [],
    }


def test_strict_json_rejects_duplicate_keys_and_noncanonical_bytes():
    contract = contract_module()

    with pytest.raises(contract.ContractError, match="duplicate key"):
        contract.load_json_object_strict(
            b'{"schema":"a","schema":"b"}', label="manifest"
        )
    with pytest.raises(contract.ContractError, match="canonical"):
        contract.load_json_object_strict(b'{"b":2,"a":1}', label="manifest")

    assert contract.canonical_json_bytes({"b": 2, "a": 1}) == b'{"a":1,"b":2}\n'
    assert contract.sha256_bytes(b"abc") == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_stable_foreign_projection_removes_only_phase12_volatile_fields():
    contract = contract_module()
    rows = [
        {
            "name_sha256": "a" * 64,
            "image_or_unit_sha256": "b" * 64,
            "active_state": "active",
            "restart_count": 59,
            "bound_port_set": [443],
        }
    ]

    assert contract.stable_foreign_projection(rows) == [
        {
            "name_sha256": "a" * 64,
            "image_or_unit_sha256": "b" * 64,
            "active_state": "active",
        }
    ]


def test_manifest_binds_exact_candidate_and_artifact_bytes(tmp_path: Path):
    contract = contract_module()
    collector, manifest = build_test_manifest(contract, tmp_path)

    assert manifest["candidate"]["udp_port"] == 30002
    assert manifest["candidate"]["vpn_cidr"] == "10.212.13.0/24"
    assert manifest["artifacts"] == [
        {
            "path": "collector.sh",
            "size": len(collector.read_bytes()),
            "sha256": hashlib.sha256(collector.read_bytes()).hexdigest(),
        }
    ]
    assert contract.validate_manifest(manifest, artifact_root=tmp_path) == manifest


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("max_attempts", 2),
        ("remote_write_allowed", True),
        ("package_build_allowed", True),
        ("live_action_authorized", True),
    ],
)
def test_manifest_rejects_fail_closed_root_mutations(
    tmp_path: Path, field: str, value: object
):
    contract = contract_module()
    _, manifest = build_test_manifest(contract, tmp_path)
    invalid = copy.deepcopy(manifest)
    invalid[field] = value

    with pytest.raises(contract.ContractError):
        contract.validate_manifest(invalid, artifact_root=tmp_path)


def test_manifest_rejects_unknown_field_wrong_candidate_invalid_hash_and_replacement(
    tmp_path: Path,
):
    contract = contract_module()
    collector, manifest = build_test_manifest(contract, tmp_path)

    unknown = {**manifest, "unknown": True}
    with pytest.raises(contract.ContractError, match="keys"):
        contract.validate_manifest(unknown, artifact_root=tmp_path)

    wrong_candidate = copy.deepcopy(manifest)
    wrong_candidate["candidate"]["udp_port"] = 30003
    with pytest.raises(contract.ContractError, match="candidate"):
        contract.validate_manifest(wrong_candidate, artifact_root=tmp_path)

    invalid_hash = copy.deepcopy(manifest)
    invalid_hash["artifacts"][0]["sha256"] = "not-a-sha256"
    with pytest.raises(contract.ContractError, match="sha256"):
        contract.validate_manifest(invalid_hash, artifact_root=tmp_path)

    collector.write_bytes(b"changed")
    with pytest.raises(contract.ContractError, match="artifact"):
        contract.validate_manifest(manifest, artifact_root=tmp_path)


def test_manifest_rejects_symlink_and_expired_outcome(tmp_path: Path):
    contract = contract_module()
    collector, manifest = build_test_manifest(contract, tmp_path)
    target = tmp_path / "target.sh"
    target.write_bytes(collector.read_bytes())
    collector.unlink()
    try:
        collector.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation unavailable")
    with pytest.raises(contract.ContractError, match="symlink"):
        contract.validate_manifest(manifest, artifact_root=tmp_path)

    expired_collector = tmp_path / "expired.sh"
    expired_collector.write_bytes(b"expired")
    expired = contract.build_manifest(
        outcome_id="expired-outcome-001",
        created_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
        expires_at=datetime(2020, 1, 2, tzinfo=timezone.utc),
        artifact_paths=(expired_collector,),
    )
    with pytest.raises(contract.ContractError, match="expired"):
        contract.validate_manifest(expired, artifact_root=tmp_path)


def test_success_and_failure_evidence_fail_closed_on_inconsistent_decision_and_order(
    tmp_path: Path,
):
    contract = contract_module()
    _, manifest = build_test_manifest(contract, tmp_path)
    success = valid_success_evidence(contract, manifest)

    assert contract.validate_success_evidence(success, manifest=manifest) == success

    inconsistent = copy.deepcopy(success)
    inconsistent["stop_reasons"] = ["foreign_equality_mismatch"]
    with pytest.raises(contract.ContractError, match="pass"):
        contract.validate_success_evidence(inconsistent, manifest=manifest)

    unordered = copy.deepcopy(success)
    unordered["decision"] = "stop"
    unordered["stop_reasons"] = ["z_reason", "a_reason"]
    with pytest.raises(contract.ContractError, match="ordered"):
        contract.validate_success_evidence(unordered, manifest=manifest)

    failure = {
        "schema": "amn2.phase13.awg3-readonly-preflight-failure.v1",
        "outcome_id": manifest["outcome_id"],
        "checked_at": "2026-08-01T12:00:00Z",
        "source_head": manifest["source_head"],
        "manifest_sha256": contract.sha256_bytes(contract.canonical_json_bytes(manifest)),
        "stage": "schema_validation",
        "reason_code": "schema_validation_failed",
        "decision": "stop",
        "safety_receipt": success["safety_receipt"],
    }
    assert contract.validate_failure_evidence(failure, manifest=manifest) == failure
