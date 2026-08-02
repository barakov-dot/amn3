from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import struct

import pytest

from scripts.phase10_recovery_crypto import MAGIC


def package_module():
    try:
        return importlib.import_module("scripts.phase13_bot_web_migration_package")
    except ModuleNotFoundError as error:
        pytest.fail(f"Phase 13 bot/web package materializer is missing: {error}")


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def opaque_encrypted_fixture(label: bytes) -> bytes:
    wrapped_key = hashlib.sha384(label).digest() * 8
    return MAGIC + struct.pack(">I", len(wrapped_key)) + wrapped_key + b"cipher:" + label


def package_inputs(**overrides):
    module = package_module()
    source_audit_verified = overrides.pop("source_audit_verified", True)
    source_raw_output_persisted = overrides.pop(
        "source_raw_output_persisted", False
    )
    source_extra = overrides.pop("source_extra", {})
    rollback_schema = overrides.pop(
        "rollback_schema", "amn2.phase13.bot-web-migration-rollback-plan.v1"
    )
    source_audit_value = {
        "checked_at": "2026-08-02T12:00:00Z",
        "database": {
            "counts_sha256": "1" * 64,
            "foreign_key_violations": 0,
            "integrity_ok": source_audit_verified,
            "schema_sha256": "2" * 64,
            "table_count": 15,
        },
        "environment": {
            "app_secret_present": True,
            "session_secret_present": True,
            "telegram_bot_token_present": True,
            "web_password_hash_present": True,
        },
        "required_artifacts": {
            "database_readable": True,
            "environment_reference_proof_available": True,
        },
        "role": "usa-source",
        "safety_receipt": {
            "mutation_attempted": False,
            "raw_output_persisted": source_raw_output_persisted,
            "secret_bearing_data_persisted": False,
        },
        "schema": "amn2.phase13.bot-web-audit.v1",
        "services": {
            "bot_active": True,
            "web_active": True,
            "web_loopback_only": True,
        },
    }
    source_audit_value.update(source_extra)
    source_audit = canonical(source_audit_value)
    target_audit = canonical(
        {
            "checked_at": "2026-08-02T12:00:00Z",
            "database": {
                "counts_sha256": "3" * 64,
                "foreign_key_violations": 0,
                "integrity_ok": True,
                "schema_sha256": "4" * 64,
                "table_count": 18,
            },
            "environment": {
                "app_secret_present": True,
                "session_secret_present": True,
                "telegram_bot_token_present": True,
                "web_password_hash_present": True,
            },
            "required_artifacts": {
                "database_readable": True,
                "environment_reference_proof_available": True,
            },
            "role": "spain-target",
            "safety_receipt": {
                "mutation_attempted": False,
                "raw_output_persisted": False,
                "secret_bearing_data_persisted": False,
            },
            "schema": "amn2.phase13.bot-web-audit.v1",
            "services": {
                "bot_active": False,
                "web_active": True,
                "web_loopback_only": True,
            },
        }
    )
    migration_plan = canonical(
        {
            "api_tokens_reissue_required": 12,
            "live_mutation_authorized": False,
            "migration_id": "bot-web-migration-001",
            "preserve_target_app_secrets": True,
            "schema": "amn2.phase13.bot-web-migration-plan.v1",
            "source_audit_sha256": sha256(source_audit),
            "source_role": "usa-source",
            "target_audit_sha256": sha256(target_audit),
            "target_role": "spain-target",
            "usable_secret_records_imported": 0,
        }
    )
    reviewed_runner = b"# reviewed local fixture\nWrite-Output 'no live action'\n"
    additional = {
        "migration-plan.json": migration_plan,
        "source-audit.json": source_audit,
        "ssh-runner.ps1": reviewed_runner,
        "target-audit.json": target_audit,
    }
    rollback_plan = canonical(
        {
            "artifact_bindings": {
                name: {"sha256": sha256(value), "size": len(value)}
                for name, value in sorted(additional.items())
            },
            "live_mutation_authorized": False,
            "restore_apply_authorized": False,
            "schema": rollback_schema,
        }
    )
    values = {
        "outcome_id": "bot-web-migration-001",
        "created_at": "2026-08-02T12:00:00Z",
        "expires_at": "2099-08-03T12:00:00Z",
        "source_audit": source_audit,
        "target_audit": target_audit,
        "migration_plan": migration_plan,
        "source_full_backup": opaque_encrypted_fixture(b"source"),
        "source_backup_encrypted": True,
        "target_before_backup": opaque_encrypted_fixture(b"target-before"),
        "target_backup_encrypted": True,
        "merged_target_db": opaque_encrypted_fixture(b"merged-target"),
        "merged_target_encrypted": True,
        "merge_preview": canonical(
            {
                "apply_allowed": True,
                "live_mutation_authorized": False,
                "usable_secret_records_imported": 0,
            }
        ),
        "rollback_plan": rollback_plan,
        "reviewed_runner": reviewed_runner,
        "external_key_stored_separately": True,
    }
    values.update(overrides)
    return module.PackageInputs(**values)


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"source_backup_encrypted": False}, "encrypted source backup"),
        ({"target_backup_encrypted": False}, "encrypted target backup"),
        ({"merged_target_encrypted": False}, "encrypted merged target"),
        ({"external_key_stored_separately": False}, "external encryption key"),
        ({"source_backup_encrypted": 1}, "encrypted source backup"),
        ({"external_key_stored_separately": 1}, "external encryption key"),
    ],
)
def test_materializer_requires_encrypted_artifacts_and_external_key_boundary(
    tmp_path: Path,
    override: dict[str, bool],
    message: str,
) -> None:
    module = package_module()

    with pytest.raises(module.PackageError, match=message):
        module.materialize_local_package(package_inputs(**override), tmp_path / "out")

    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"source_audit_verified": False}, "source audit is not verified"),
        (
            {"source_raw_output_persisted": True},
            "source audit safety receipt",
        ),
    ],
)
def test_materializer_rejects_unverified_or_unsafe_audit_evidence(
    tmp_path: Path,
    override: dict[str, bool],
    message: str,
) -> None:
    module = package_module()

    with pytest.raises(module.PackageError, match=message):
        module.materialize_local_package(package_inputs(**override), tmp_path / "out")

    assert not (tmp_path / "out").exists()


def test_materializer_rejects_raw_secret_field_in_closed_audit(
    tmp_path: Path,
) -> None:
    module = package_module()
    inputs = package_inputs(source_extra={"telegram_bot_token": "forbidden"})

    with pytest.raises(module.PackageError, match="source audit keys"):
        module.materialize_local_package(inputs, tmp_path / "out")

    assert not (tmp_path / "out").exists()


def test_materializer_rejects_unknown_rollback_schema(tmp_path: Path) -> None:
    module = package_module()
    inputs = package_inputs(rollback_schema="unknown")

    with pytest.raises(module.PackageError, match="rollback schema"):
        module.materialize_local_package(inputs, tmp_path / "out")

    assert not (tmp_path / "out").exists()


def test_materializer_binds_outcome_id_to_migration_plan_id(tmp_path: Path) -> None:
    module = package_module()
    inputs = package_inputs(outcome_id="different-outcome")

    with pytest.raises(module.PackageError, match="outcome binding"):
        module.materialize_local_package(inputs, tmp_path / "out")

    assert not (tmp_path / "out").exists()


def test_package_manifest_is_canonical_secret_free_and_binds_every_file(
    tmp_path: Path,
) -> None:
    module = package_module()
    output = tmp_path / "out"

    receipt = module.materialize_local_package(package_inputs(), output)

    manifest_bytes = receipt.manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest_bytes == canonical(manifest)
    assert receipt.manifest_sha256 == sha256(manifest_bytes)
    assert receipt.live_mutation_authorized is False
    assert receipt.external_key_in_package is False
    assert receipt.plaintext_database_written is False
    assert manifest["live_mutation_authorized"] is False
    assert b"TELEGRAM_BOT_TOKEN=" not in manifest_bytes
    assert b"ADMIN_TELEGRAM_IDS=" not in manifest_bytes
    assert b"APP_SECRET_KEY=" not in manifest_bytes

    rollback = json.loads((output / "rollback-plan.json").read_bytes())
    direct = {
        item["path"] for item in manifest["artifacts"].values()
    }
    transitive = set(rollback["artifact_bindings"])
    package_files = {
        path.name for path in output.iterdir() if path.name != "manifest.json"
    }
    assert direct | transitive == package_files
    assert dict(receipt.artifact_sha256) == {
        name: sha256((output / name).read_bytes()) for name in sorted(package_files)
    }


def test_identical_inputs_produce_identical_manifest_and_artifact_hashes(
    tmp_path: Path,
) -> None:
    module = package_module()
    inputs = package_inputs()

    first = module.materialize_local_package(inputs, tmp_path / "first")
    second = module.materialize_local_package(inputs, tmp_path / "second")

    assert first.manifest_path.read_bytes() == second.manifest_path.read_bytes()
    assert first.manifest_sha256 == second.manifest_sha256
    assert first.artifact_sha256 == second.artifact_sha256


def test_materializer_is_create_new_and_never_overwrites_existing_root(
    tmp_path: Path,
) -> None:
    module = package_module()
    output = tmp_path / "out"
    output.mkdir()
    sentinel = output / "sentinel.txt"
    sentinel.write_bytes(b"preserve")

    with pytest.raises(module.PackageError, match="output root already exists"):
        module.materialize_local_package(package_inputs(), output)

    assert sentinel.read_bytes() == b"preserve"


def test_binding_failure_removes_only_incomplete_output_root(tmp_path: Path) -> None:
    module = package_module()
    inputs = package_inputs(reviewed_runner=b"different reviewed runner bytes\n")
    output = tmp_path / "out"

    with pytest.raises(module.PackageError, match="rollback artifact binding"):
        module.materialize_local_package(inputs, output)

    assert not output.exists()


def test_output_root_symlink_is_rejected_without_touching_target(tmp_path: Path) -> None:
    module = package_module()
    target = tmp_path / "target"
    target.mkdir()
    output = tmp_path / "out"
    try:
        output.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlink creation unavailable")

    with pytest.raises(module.PackageError, match="output root already exists"):
        module.materialize_local_package(package_inputs(), output)

    assert list(target.iterdir()) == []
