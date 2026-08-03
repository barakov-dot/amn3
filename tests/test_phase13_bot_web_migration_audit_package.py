from __future__ import annotations

import importlib
import hashlib
import json
import os
from pathlib import Path

import pytest


EXPECTED_ARTIFACT_FILENAMES = {
    "audit_evidence_schema": "audit-evidence.schema.json",
    "audit_package": "audit-package.py",
    "audit_tooling_manifest_schema": "audit-tooling-manifest.schema.json",
    "db_schema": "db-schema.py",
    "failure_evidence_schema": "failure-evidence.schema.json",
    "merge": "merge.py",
    "migration_contract": "migration-contract.py",
    "migration_manifest_schema": "migration-manifest.schema.json",
    "migration_package": "migration-package.py",
    "migration_plan_schema": "migration-plan.schema.json",
    "readonly_collector": "readonly-collector.py",
    "remote_cutover": "remote-cutover.sh",
    "remote_stage": "remote-stage.sh",
    "ssh_runner": "ssh-runner.ps1",
}

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT
    / "packaging"
    / "phase13-bot-web-migration"
    / "audit-tooling-manifest.schema.json"
)
ROOT_HEAD = "408298982ce820b6a73c4f6721ce71e85e9c93e6"
AMN2_HEAD = "910539eaa8051cb1b59131d38b9fa27b9392744d"
SAFETY_FLAGS = {
    "backup_allowed",
    "bot_cutover_allowed",
    "data_transfer_allowed",
    "db_apply_allowed",
    "live_mutation_authorized",
    "package_build_allowed",
    "remote_write_allowed",
    "usa_release_allowed",
}


def audit_package_module():
    try:
        return importlib.import_module(
            "scripts.phase13_bot_web_migration_audit_package"
        )
    except ModuleNotFoundError as error:
        pytest.fail(f"Phase 13 audit tooling materializer is missing: {error}")


def load_manifest_schema() -> dict[str, object]:
    try:
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        pytest.fail(f"Phase 13 audit tooling manifest schema is missing: {error}")


def test_artifact_allowlist_is_exact_and_uses_fixed_flat_filenames() -> None:
    module = audit_package_module()

    assert module.ARTIFACT_FILENAMES == EXPECTED_ARTIFACT_FILENAMES
    assert len(set(module.ARTIFACT_FILENAMES.values())) == 14
    assert all("/" not in name and "\\" not in name for name in module.ARTIFACT_FILENAMES.values())


def assert_closed_object_schemas(value: object) -> None:
    if isinstance(value, dict):
        if value.get("type") == "object":
            assert value.get("additionalProperties") is False
        for nested in value.values():
            assert_closed_object_schemas(nested)
    elif isinstance(value, list):
        for nested in value:
            assert_closed_object_schemas(nested)


def test_manifest_schema_is_closed_and_pins_heads_roles_trust_and_safety() -> None:
    schema = load_manifest_schema()

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == "amn2.phase13.bot-web-audit-tooling-manifest.v1"
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert_closed_object_schemas(schema)
    properties = schema["properties"]
    assert properties["root_head"] == {"const": ROOT_HEAD}
    assert properties["amn2_head"] == {"const": AMN2_HEAD}
    assert properties["max_attempts"] == {"const": 1}
    assert properties["roles"]["properties"] == {
        "source": {"const": "usa-source"},
        "target": {"const": "spain-target"},
    }
    trust = properties["trust_bundles"]
    assert set(trust["required"]) == {"usa", "spain"}
    assert trust["properties"]["usa"]["properties"]["role"] == {
        "const": "usa-source"
    }
    assert trust["properties"]["spain"]["properties"]["role"] == {
        "const": "spain-target"
    }
    for role in ("usa", "spain"):
        assert trust["properties"][role]["properties"]["overridable"] == {
            "const": False
        }
        assert set(trust["properties"][role]["required"]) == {
            "binding_id",
            "overridable",
            "role",
            "runner_sha256",
        }
    artifacts = properties["artifacts"]
    assert set(artifacts["required"]) == set(EXPECTED_ARTIFACT_FILENAMES)
    assert set(artifacts["properties"]) == set(EXPECTED_ARTIFACT_FILENAMES)
    for artifact_id, filename in EXPECTED_ARTIFACT_FILENAMES.items():
        artifact = artifacts["properties"][artifact_id]
        assert artifact["properties"]["filename"] == {"const": filename}
        assert artifact["properties"]["size"] == {
            "type": "integer",
            "minimum": 1,
            "maximum": 4 * 1024 * 1024,
        }
        assert set(artifact["required"]) == {"filename", "sha256", "size"}
    safety = properties["safety"]
    assert set(safety["required"]) == SAFETY_FLAGS
    assert set(safety["properties"]) == SAFETY_FLAGS
    assert all(value == {"const": False} for value in safety["properties"].values())


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fixture_artifacts() -> dict[str, bytes]:
    artifacts = {
        artifact_id: f"verified-fixture:{artifact_id}\n".encode("utf-8")
        for artifact_id in EXPECTED_ARTIFACT_FILENAMES
    }
    artifacts["audit_tooling_manifest_schema"] = SCHEMA_PATH.read_bytes()
    return artifacts


def package_inputs(**overrides):
    module = audit_package_module()
    values = {
        "outcome_id": "bot-web-audit-20260803-001",
        "created_at": "2026-08-03T10:00:00Z",
        "expires_at": "2026-08-03T12:00:00Z",
        "root_head": ROOT_HEAD,
        "amn2_head": AMN2_HEAD,
        "artifacts": fixture_artifacts(),
    }
    values.update(overrides)
    return module.AuditToolingPackageInputs(**values)


def test_materializer_creates_canonical_checksum_bound_local_only_package(
    tmp_path: Path,
) -> None:
    module = audit_package_module()
    output = tmp_path / "audit-tooling"
    inputs = package_inputs()

    receipt = module.materialize_local_audit_tooling_package(inputs, output)
    verified = module.verify_local_audit_tooling_package(
        output,
        now="2026-08-03T10:30:00Z",
    )

    manifest_bytes = (output / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest_bytes == canonical(manifest)
    assert receipt.manifest_sha256 == sha256(manifest_bytes)
    assert verified == manifest
    assert manifest["schema"] == "amn2.phase13.bot-web-audit-tooling-manifest.v1"
    assert manifest["outcome_id"] == "bot-web-audit-20260803-001"
    assert manifest["root_head"] == ROOT_HEAD
    assert manifest["amn2_head"] == AMN2_HEAD
    assert manifest["roles"] == {"source": "usa-source", "target": "spain-target"}
    assert manifest["max_attempts"] == 1
    assert manifest["safety"] == {name: False for name in sorted(SAFETY_FLAGS)}
    assert set(manifest["artifacts"]) == set(EXPECTED_ARTIFACT_FILENAMES)
    expected_hashes = {}
    for artifact_id, filename in EXPECTED_ARTIFACT_FILENAMES.items():
        value = inputs.artifacts[artifact_id]
        expected_hashes[artifact_id] = sha256(value)
        assert (output / filename).read_bytes() == value
        assert manifest["artifacts"][artifact_id] == {
            "filename": filename,
            "sha256": sha256(value),
            "size": len(value),
        }
    runner_sha256 = expected_hashes["ssh_runner"]
    assert manifest["trust_bundles"] == {
        "spain": {
            "binding_id": "phase13-bot-web-runner-fixed-spain-v1",
            "overridable": False,
            "role": "spain-target",
            "runner_sha256": runner_sha256,
        },
        "usa": {
            "binding_id": "phase13-bot-web-runner-fixed-usa-v1",
            "overridable": False,
            "role": "usa-source",
            "runner_sha256": runner_sha256,
        },
    }
    assert set(path.name for path in output.iterdir()) == {
        *EXPECTED_ARTIFACT_FILENAMES.values(),
        "manifest.json",
    }
    assert receipt.artifact_sha256 == tuple(sorted(expected_hashes.items()))
    assert receipt.remote_write_allowed is False
    assert receipt.package_build_allowed is False
    assert receipt.live_mutation_authorized is False


def test_materializer_rejects_inconsistent_manifest_schema_bytes(
    tmp_path: Path,
) -> None:
    module = audit_package_module()
    artifacts = fixture_artifacts()
    artifacts["audit_tooling_manifest_schema"] = canonical(
        {
            "$id": "wrong-schema",
            "additionalProperties": True,
            "type": "object",
        }
    )

    with pytest.raises(module.AuditToolingPackageError, match="manifest schema"):
        module.materialize_local_audit_tooling_package(
            package_inputs(artifacts=artifacts),
            tmp_path / "audit-tooling",
        )

    assert not (tmp_path / "audit-tooling").exists()


def test_materializer_rejects_schema_without_strict_time_contract(
    tmp_path: Path,
) -> None:
    module = audit_package_module()
    artifacts = fixture_artifacts()
    schema = load_manifest_schema()
    schema["properties"]["expires_at"] = {"type": "string"}
    artifacts["audit_tooling_manifest_schema"] = json.dumps(
        schema,
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8") + b"\n"

    with pytest.raises(module.AuditToolingPackageError, match="manifest schema"):
        module.materialize_local_audit_tooling_package(
            package_inputs(artifacts=artifacts),
            tmp_path / "audit-tooling",
        )

    assert not (tmp_path / "audit-tooling").exists()


def test_verify_local_rejects_manifest_before_created_at(tmp_path: Path) -> None:
    module = audit_package_module()
    output = tmp_path / "audit-tooling"
    module.materialize_local_audit_tooling_package(package_inputs(), output)

    with pytest.raises(module.AuditToolingPackageError, match="not yet valid"):
        module.verify_local_audit_tooling_package(
            output,
            now="2026-08-03T09:59:59Z",
        )


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"root_head": "0" * 40}, "source head"),
        ({"amn2_head": "0" * 40}, "source head"),
        ({"outcome_id": "INVALID"}, "outcome id"),
        ({"expires_at": "2026-08-03T10:00:00Z"}, "expiry"),
    ],
)
def test_invalid_identity_head_or_time_is_rejected_before_root_creation(
    tmp_path: Path,
    override: dict[str, object],
    message: str,
) -> None:
    module = audit_package_module()
    output = tmp_path / "audit-tooling"

    with pytest.raises(module.AuditToolingPackageError, match=message):
        module.materialize_local_audit_tooling_package(
            package_inputs(**override),
            output,
        )

    assert not output.exists()


@pytest.mark.parametrize("mutation", ["missing", "extra", "empty"])
def test_artifact_input_set_and_bytes_fail_closed(
    tmp_path: Path,
    mutation: str,
) -> None:
    module = audit_package_module()
    artifacts = fixture_artifacts()
    if mutation == "missing":
        del artifacts["remote_cutover"]
    elif mutation == "extra":
        artifacts["remote_target_override"] = b"forbidden\n"
    else:
        artifacts["remote_cutover"] = b""
    output = tmp_path / "audit-tooling"

    with pytest.raises(module.AuditToolingPackageError, match="artifact"):
        module.materialize_local_audit_tooling_package(
            package_inputs(artifacts=artifacts),
            output,
        )

    assert not output.exists()


def test_identical_inputs_produce_identical_manifest_and_hashes(
    tmp_path: Path,
) -> None:
    module = audit_package_module()
    inputs = package_inputs()

    first = module.materialize_local_audit_tooling_package(inputs, tmp_path / "one")
    second = module.materialize_local_audit_tooling_package(inputs, tmp_path / "two")

    assert first.manifest_path.read_bytes() == second.manifest_path.read_bytes()
    assert first.manifest_sha256 == second.manifest_sha256
    assert first.artifact_sha256 == second.artifact_sha256


def test_output_root_is_create_new_and_preserves_existing_content(
    tmp_path: Path,
) -> None:
    module = audit_package_module()
    output = tmp_path / "audit-tooling"
    output.mkdir()
    sentinel = output / "sentinel.txt"
    sentinel.write_bytes(b"preserve")

    with pytest.raises(module.AuditToolingPackageError, match="already exists"):
        module.materialize_local_audit_tooling_package(package_inputs(), output)

    assert sentinel.read_bytes() == b"preserve"


def test_verify_rejects_artifact_tamper_and_unknown_file(tmp_path: Path) -> None:
    module = audit_package_module()
    tampered = tmp_path / "tampered"
    module.materialize_local_audit_tooling_package(package_inputs(), tampered)
    (tampered / "remote-cutover.sh").write_bytes(b"changed\n")
    with pytest.raises(module.AuditToolingPackageError, match="checksum mismatch"):
        module.verify_local_audit_tooling_package(
            tampered,
            now="2026-08-03T10:30:00Z",
        )

    unknown = tmp_path / "unknown"
    module.materialize_local_audit_tooling_package(package_inputs(), unknown)
    (unknown / "target.env").write_bytes(b"forbidden\n")
    with pytest.raises(module.AuditToolingPackageError, match="artifact set"):
        module.verify_local_audit_tooling_package(
            unknown,
            now="2026-08-03T10:30:00Z",
        )


def test_verify_rejects_checksum_valid_oversized_artifact(tmp_path: Path) -> None:
    module = audit_package_module()
    output = tmp_path / "audit-tooling"
    module.materialize_local_audit_tooling_package(package_inputs(), output)
    oversized = b"x" * (4 * 1024 * 1024 + 1)
    artifact_path = output / "remote-cutover.sh"
    artifact_path.write_bytes(oversized)
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["artifacts"]["remote_cutover"]["size"] = len(oversized)
    manifest["artifacts"]["remote_cutover"]["sha256"] = sha256(oversized)
    manifest_path.write_bytes(canonical(manifest))

    with pytest.raises(module.AuditToolingPackageError, match="artifact size"):
        module.verify_local_audit_tooling_package(
            output,
            now="2026-08-03T10:30:00Z",
        )


def test_verify_rejects_manifest_override_and_trust_rebinding(tmp_path: Path) -> None:
    module = audit_package_module()
    output = tmp_path / "audit-tooling"
    module.materialize_local_audit_tooling_package(package_inputs(), output)
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["remote_path"] = "/forbidden"
    manifest_path.write_bytes(canonical(manifest))
    with pytest.raises(module.AuditToolingPackageError, match="manifest keys"):
        module.verify_local_audit_tooling_package(
            output,
            now="2026-08-03T10:30:00Z",
        )

    trust = tmp_path / "trust"
    module.materialize_local_audit_tooling_package(package_inputs(), trust)
    trust_manifest_path = trust / "manifest.json"
    trust_manifest = json.loads(trust_manifest_path.read_bytes())
    trust_manifest["trust_bundles"]["usa"]["overridable"] = True
    trust_manifest_path.write_bytes(canonical(trust_manifest))
    with pytest.raises(module.AuditToolingPackageError, match="trust binding"):
        module.verify_local_audit_tooling_package(
            trust,
            now="2026-08-03T10:30:00Z",
        )


def test_manifest_has_no_remote_override_or_private_trust_fields(
    tmp_path: Path,
) -> None:
    module = audit_package_module()
    output = tmp_path / "audit-tooling"
    module.materialize_local_audit_tooling_package(package_inputs(), output)
    manifest = json.loads((output / "manifest.json").read_bytes())
    forbidden = {
        "fingerprint",
        "host",
        "host_key_path",
        "private_key",
        "remote_path",
        "target_host",
        "target_path",
        "user",
        "username",
    }

    def keys(value: object) -> set[str]:
        if isinstance(value, dict):
            return set(value) | set().union(*(keys(item) for item in value.values()))
        if isinstance(value, list):
            return set().union(*(keys(item) for item in value))
        return set()

    assert keys(manifest).isdisjoint(forbidden)


def test_output_root_symlink_is_rejected_without_touching_target(
    tmp_path: Path,
) -> None:
    module = audit_package_module()
    target = tmp_path / "target"
    target.mkdir()
    output = tmp_path / "audit-tooling"
    try:
        os.symlink(target, output, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlink creation unavailable")

    with pytest.raises(module.AuditToolingPackageError, match="already exists"):
        module.materialize_local_audit_tooling_package(package_inputs(), output)

    assert list(target.iterdir()) == []
