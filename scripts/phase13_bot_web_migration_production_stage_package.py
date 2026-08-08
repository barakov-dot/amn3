#!/usr/bin/env python
"""Materialize and verify the bound Phase 13 Spain stage/apply package."""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import subprocess
import sys
import tarfile
from typing import Mapping, Sequence

try:
    from scripts.phase10_recovery_crypto import (
        MAGIC,
        RecoveryCryptoError,
        decrypt_hybrid,
        encrypt_hybrid,
    )
except ImportError:  # packaged execution
    from recovery_crypto import (  # type: ignore[no-redef]
        MAGIC,
        RecoveryCryptoError,
        decrypt_hybrid,
        encrypt_hybrid,
    )


MANIFEST_SCHEMA_ID = "amn2.phase13.bot-web-migration-manifest.v1"
FAILURE_SCHEMA_ID = "amn2.phase13.bot-web-migration-failure.v1"
ROLLBACK_SCHEMA_ID = "amn2.phase13.bot-web-production-stage-plan.v1"
ROOT_BASE_HEAD = "1b55f7c83c3453829e24af5dd11facedb2188447"
AMN2_HEAD = "910539eaa8051cb1b59131d38b9fa27b9392744d"

CURRENT_SOURCE_OUTCOME = "bot-web-fresh-20260808-142324"
CURRENT_MERGE_OUTCOME = "bot-web-merge-ledger-20260808-172510"
CURRENT_MERGE_CLAIM_SHA256 = (
    "055bc8126b599c20e024e5511eb7ea3851b106676b1b9c6fdddf80af871d631f"
)
CURRENT_MERGED_DATABASE_SHA256 = (
    "cbdb3d5532a83bbaf9d82c56b5b7f24e109eef3738f7fd016c5ebd706843362f"
)
CURRENT_MERGE_PREVIEW_SHA256 = (
    "d5a1da1bfde61178bd7ff27b753121fe0a8f76d48d10fb13832547abc43e0263"
)
CURRENT_MERGE_RECEIPT_SHA256 = (
    "a440b530429d1f339cc71ffc65ff8f416acfc74b37302be8d8e1189f2a2c43f0"
)
CURRENT_SOURCE_MANIFEST_SHA256 = (
    "3b20ccdf89635875f07962b5998ef613e4b03cbd272bf1ea8a7e8d1b06aff3a1"
)

EXPECTED_AWG2_FOUNDATION_SHA256 = (
    "0e5a5926821d88ae4a2515f9e95cd7c3f69db52100c1a1ec74e99fb794222281"
)
EXPECTED_FOREIGN_RECEIPT_SHA256 = (
    "bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704"
)
EXPECTED_FOREIGN_STABLE_SHA256 = (
    "f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8"
)

OUTCOME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
MAX_REMOTE_INPUT_BYTES = 1024 * 1024

DIRECT_FILES = {
    "merge_preview": "merge-preview.json",
    "merged_target_db": "merged-target.sqlite3.enc",
    "rollback_plan": "rollback-plan.json",
    "source_full_backup": "source-full-backup.enc",
    "target_before_backup": "target-before-backup.enc",
}
TOOLING_FILES = {
    "amn2-spain-bot.service",
    "audit-ssh-runner.ps1",
    "failure-evidence.schema.json",
    "manifest.schema.json",
    "production-stage-package.py",
    "production-stage-remote.py",
    "production-stage-runner.ps1",
    "readonly-collector.py",
    "recovery_crypto.py",
}
EVIDENCE_FILES = {
    "migration-plan.json",
    "runtime.env.delta.enc",
    "source-audit.json",
    "source-input-manifest.json",
    "source-merge-claim.json",
    "source-merge-receipt.json",
    "target-audit.json",
}
INDIRECT_FILES = TOOLING_FILES | EVIDENCE_FILES
PACKAGE_FILES = set(DIRECT_FILES.values()) | INDIRECT_FILES | {"manifest.json"}


class ProductionPackageError(RuntimeError):
    """A secret-safe package error."""


@dataclass(frozen=True)
class PreparedStagePackageInputs:
    amn2_head: str
    created_at: str
    expires_at: str
    merge_claim: bytes
    merge_preview: bytes
    merge_receipt: bytes
    merged_database_sha256: str
    merged_target_db: bytes
    outcome_id: str
    recovery_private_key_pem: bytes
    root_base_head: str
    runtime_delta_encrypted: bytes
    source_evidence: bytes
    source_full_backup: bytes
    source_input_manifest: bytes
    source_outcome_id: str
    spain_invariants_sha256: str
    target_before_backup: bytes
    target_before_database_sha256: str
    target_evidence: bytes
    target_runtime_env_sha256: str
    tooling_artifacts: Mapping[str, bytes]
    tooling_head: str


@dataclass(frozen=True)
class ProductionPackageReceipt:
    output_root: Path
    manifest_sha256: str
    artifact_sha256: tuple[tuple[str, str], ...]
    outcome_id: str
    expires_at: str


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _reject_duplicate_object_pairs(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ProductionPackageError("JSON object contains duplicate key")
        result[key] = value
    return result


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _parse_time(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise ProductionPackageError(f"{label} invalid")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ProductionPackageError(f"{label} invalid") from error
    if parsed.tzinfo is None:
        raise ProductionPackageError(f"{label} invalid")
    return parsed.astimezone(timezone.utc)


def _canonical_object(value: bytes, label: str) -> dict[str, object]:
    if not isinstance(value, bytes) or not value or len(value) > MAX_ARTIFACT_BYTES:
        raise ProductionPackageError(f"{label} invalid")
    try:
        parsed = json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProductionPackageError(f"{label} invalid") from error
    if not isinstance(parsed, dict) or canonical_json_bytes(parsed) != value:
        raise ProductionPackageError(f"{label} noncanonical")
    return parsed


def _require_sha(value: object, label: str) -> str:
    if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
        raise ProductionPackageError(f"{label} invalid")
    return value


def _require_encrypted(value: bytes, label: str) -> None:
    if not isinstance(value, bytes) or not value.startswith(MAGIC) or len(value) > MAX_ARTIFACT_BYTES:
        raise ProductionPackageError(f"{label} invalid")


def _is_reparse(metadata: os.stat_result) -> bool:
    return bool(getattr(metadata, "st_file_attributes", 0) & 0x400)


def _safe_regular(path: Path) -> os.stat_result:
    try:
        metadata = os.lstat(path)
    except OSError as error:
        raise ProductionPackageError("artifact unavailable") from error
    if stat.S_ISLNK(metadata.st_mode) or _is_reparse(metadata) or not stat.S_ISREG(metadata.st_mode):
        raise ProductionPackageError("artifact unsafe")
    return metadata


def _safe_directory(path: Path) -> None:
    try:
        metadata = os.lstat(path)
    except OSError as error:
        raise ProductionPackageError("artifact root unavailable") from error
    if stat.S_ISLNK(metadata.st_mode) or _is_reparse(metadata) or not stat.S_ISDIR(metadata.st_mode):
        raise ProductionPackageError("artifact root unsafe")


def _create_private_root(path: Path) -> None:
    if os.path.lexists(path):
        raise ProductionPackageError("artifact root exists")
    _safe_directory(path.parent)
    try:
        os.mkdir(path, 0o700)
        os.chmod(path, 0o700)
    except OSError as error:
        raise ProductionPackageError("artifact root create failed") from error
    _safe_directory(path)


def _write_exclusive(path: Path, value: bytes) -> None:
    if not isinstance(value, bytes) or not value or len(value) > MAX_ARTIFACT_BYTES:
        raise ProductionPackageError("artifact bytes invalid")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                descriptor = -1
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(path, 0o600)
        finally:
            if descriptor >= 0:
                os.close(descriptor)
    except OSError as error:
        raise ProductionPackageError("artifact write failed") from error


def _cleanup_incomplete(root: Path) -> None:
    if not root.exists() or root.is_symlink() or root.parent == root:
        return
    try:
        for path in root.iterdir():
            if path.is_file() and not path.is_symlink():
                path.unlink()
        root.rmdir()
    except OSError:
        pass


def _validate_existing_schema(value: bytes, expected_id: str) -> None:
    try:
        schema = json.loads(value.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProductionPackageError("existing schema contract invalid") from error
    if not isinstance(schema, dict):
        raise ProductionPackageError("existing schema contract invalid")
    if (
        schema.get("$id") != expected_id
        or schema.get("type") != "object"
        or schema.get("additionalProperties") is not False
    ):
        raise ProductionPackageError("existing schema contract invalid")


def _validate_prepared(inputs: PreparedStagePackageInputs) -> tuple[dict[str, bytes], dict[str, object]]:
    if not isinstance(inputs, PreparedStagePackageInputs):
        raise ProductionPackageError("prepared package inputs invalid")
    created = _parse_time(inputs.created_at, "created_at")
    expires = _parse_time(inputs.expires_at, "expires_at")
    if expires <= created:
        raise ProductionPackageError("package expiry invalid")
    if (
        OUTCOME_PATTERN.fullmatch(inputs.outcome_id) is None
        or OUTCOME_PATTERN.fullmatch(inputs.source_outcome_id) is None
        or re.fullmatch(r"[0-9a-f]{40}", inputs.root_base_head) is None
        or re.fullmatch(r"[0-9a-f]{40}", inputs.tooling_head) is None
        or re.fullmatch(r"[0-9a-f]{40}", inputs.amn2_head) is None
        or inputs.root_base_head != ROOT_BASE_HEAD
        or inputs.amn2_head != AMN2_HEAD
    ):
        raise ProductionPackageError("head or outcome binding invalid")
    for value, label in (
        (inputs.source_full_backup, "source backup"),
        (inputs.target_before_backup, "target backup"),
        (inputs.merged_target_db, "merged database"),
        (inputs.runtime_delta_encrypted, "runtime delta"),
    ):
        _require_encrypted(value, label)
    for value, label in (
        (inputs.merged_database_sha256, "merged database"),
        (inputs.spain_invariants_sha256, "Spain invariants"),
        (inputs.target_before_database_sha256, "target before database"),
        (inputs.target_runtime_env_sha256, "target runtime"),
    ):
        _require_sha(value, label)
    if set(inputs.tooling_artifacts) != TOOLING_FILES:
        raise ProductionPackageError("tooling artifact set invalid")
    tooling = {name: bytes(inputs.tooling_artifacts[name]) for name in TOOLING_FILES}
    if any(not value or len(value) > MAX_ARTIFACT_BYTES for value in tooling.values()):
        raise ProductionPackageError("tooling artifact invalid")
    _validate_existing_schema(tooling["manifest.schema.json"], MANIFEST_SCHEMA_ID)
    _validate_existing_schema(tooling["failure-evidence.schema.json"], FAILURE_SCHEMA_ID)
    unit = tooling["amn2-spain-bot.service"].decode("utf-8", errors="strict")
    if (
        "ConditionPathExists=/etc/amn2-spain/bot-enabled" not in unit
        or "WantedBy=multi-user.target" not in unit
    ):
        raise ProductionPackageError("bot unit contract invalid")

    source_manifest = _canonical_object(inputs.source_input_manifest, "source manifest")
    merge_claim = _canonical_object(inputs.merge_claim, "merge claim")
    merge_receipt = _canonical_object(inputs.merge_receipt, "merge receipt")
    preview = _canonical_object(inputs.merge_preview, "merge preview")
    source_evidence = _canonical_object(inputs.source_evidence, "source evidence")
    target_evidence = _canonical_object(inputs.target_evidence, "target evidence")
    source_artifacts = source_manifest.get("artifacts")
    if (
        source_manifest.get("outcome_id") != inputs.source_outcome_id
        or source_manifest.get("remote_collection_completed") is not True
        or source_manifest.get("ssh_process_count") != 2
        or not isinstance(source_artifacts, dict)
        or set(source_artifacts) != {"source-full-backup.enc", "target-before-backup.enc"}
    ):
        raise ProductionPackageError("source evidence contract invalid")
    for name, role, value in (
        ("source-full-backup.enc", "usa", inputs.source_full_backup),
        ("target-before-backup.enc", "spain", inputs.target_before_backup),
    ):
        binding = source_artifacts.get(name)
        if (
            not isinstance(binding, dict)
            or binding.get("role") != role
            or binding.get("size") != len(value)
            or binding.get("sha256") != sha256_bytes(value)
        ):
            raise ProductionPackageError("source artifact binding invalid")
    if (
        merge_claim.get("source_outcome") != inputs.source_outcome_id
        or merge_claim.get("max_attempts") != 1
        or merge_claim.get("network_authorized") is not False
        or merge_receipt.get("outcome_id") != merge_claim.get("outcome_id")
        or merge_receipt.get("source_outcome") != inputs.source_outcome_id
        or merge_receipt.get("status") != "success"
        or merge_receipt.get("live_mutation") is not False
        or merge_receipt.get("network_started") is not False
        or merge_receipt.get("plaintext_persisted") is not False
        or merge_receipt.get("integrity_ok") is not True
        or merge_receipt.get("foreign_key_issues") != 0
        or merge_receipt.get("spain_d1_d7_preserved") is not True
        or merge_receipt.get("spain_target_privileges_preserved") is not True
        or merge_receipt.get("usable_secret_records_imported") != 0
        or not isinstance(merge_receipt.get("merge_result_sha256"), str)
        or SHA256_PATTERN.fullmatch(str(merge_receipt.get("merge_result_sha256"))) is None
        or merge_receipt.get("preview_sha256") != sha256_bytes(inputs.merge_preview)
        or preview.get("apply_allowed") is not True
        or preview.get("usable_secret_records_imported") != 0
        or preview.get("stop_reasons") != []
        or source_evidence.get("role") != "usa-source"
        or target_evidence.get("role") != "spain-target"
    ):
        raise ProductionPackageError("merge evidence contract invalid")
    merge_artifacts = merge_receipt.get("artifacts")
    if not isinstance(merge_artifacts, dict):
        raise ProductionPackageError("merge artifact binding invalid")
    expected_merge_artifacts = {
        "merge-preview.json": inputs.merge_preview,
        "merged-target.sqlite3.enc": inputs.merged_target_db,
    }
    for name, value in expected_merge_artifacts.items():
        binding = merge_artifacts.get(name)
        if (
            not isinstance(binding, dict)
            or binding.get("size") != len(value)
            or binding.get("sha256") != sha256_bytes(value)
        ):
            raise ProductionPackageError("merge artifact binding invalid")

    migration_plan = canonical_json_bytes(
        {
            "api_tokens_reissue_required": int(preview.get("api_tokens_reissue_required", 0)),
            "live_mutation_authorized": False,
            "migration_id": inputs.outcome_id,
            "preserve_target_app_secrets": True,
            "schema": "amn2.phase13.bot-web-migration-plan.v1",
            "source_audit_sha256": sha256_bytes(inputs.source_evidence),
            "source_role": "usa-source",
            "target_audit_sha256": sha256_bytes(inputs.target_evidence),
            "target_role": "spain-target",
            "usable_secret_records_imported": 0,
        }
    )
    indirect = {
        **tooling,
        "migration-plan.json": migration_plan,
        "runtime.env.delta.enc": inputs.runtime_delta_encrypted,
        "source-audit.json": inputs.source_evidence,
        "source-input-manifest.json": inputs.source_input_manifest,
        "source-merge-claim.json": inputs.merge_claim,
        "source-merge-receipt.json": inputs.merge_receipt,
        "target-audit.json": inputs.target_evidence,
    }
    if set(indirect) != INDIRECT_FILES:
        raise ProductionPackageError("indirect artifact set invalid")
    rollback_plan = {
        "artifact_bindings": {
            name: {"sha256": sha256_bytes(value), "size": len(value)}
            for name, value in sorted(indirect.items())
        },
        "expected": {
            "awg2_foundation_sha256": EXPECTED_AWG2_FOUNDATION_SHA256,
            "foreign_receipt_sha256": EXPECTED_FOREIGN_RECEIPT_SHA256,
            "foreign_stable_sha256": EXPECTED_FOREIGN_STABLE_SHA256,
            "merged_database_sha256": inputs.merged_database_sha256,
            "spain_invariants_sha256": inputs.spain_invariants_sha256,
            "target_before_database_sha256": inputs.target_before_database_sha256,
            "target_runtime_env_sha256": inputs.target_runtime_env_sha256,
        },
        "heads": {
            "amn2": inputs.amn2_head,
            "root_base": inputs.root_base_head,
            "tooling": inputs.tooling_head,
        },
        "max_attempts": 1,
        "process_contract": {
            "expected_ssh_processes": 3,
            "remote_temp_package": False,
            "retries": 0,
            "roles": ["usa-readonly", "spain-readonly", "spain-stage-apply"],
            "scp": False,
        },
        "safety": {
            "awg_mutation_allowed": False,
            "bot_cutover_allowed": False,
            "foreign_service_mutation_allowed": False,
            "live_mutation_authorized": False,
            "spain_bot_start_allowed": False,
            "usa_mutation_allowed": False,
        },
        "schema": ROLLBACK_SCHEMA_ID,
        "source": {
            "merge_outcome_id": str(merge_receipt["outcome_id"]),
            "source_outcome_id": inputs.source_outcome_id,
        },
        "trust_bundles": {
            "spain": {"binding_id": "phase13-bot-web-runner-fixed-spain-v1", "overridable": False},
            "usa": {"binding_id": "phase13-bot-web-runner-fixed-usa-v1", "overridable": False},
        },
    }
    artifacts = {
        **indirect,
        "merge-preview.json": inputs.merge_preview,
        "merged-target.sqlite3.enc": inputs.merged_target_db,
        "rollback-plan.json": canonical_json_bytes(rollback_plan),
        "source-full-backup.enc": inputs.source_full_backup,
        "target-before-backup.enc": inputs.target_before_backup,
    }
    if set(artifacts) != PACKAGE_FILES - {"manifest.json"}:
        raise ProductionPackageError("package artifact set invalid")
    manifest = {
        "artifacts": {
            key: {
                "path": filename,
                "sha256": sha256_bytes(artifacts[filename]),
                "size": len(artifacts[filename]),
            }
            for key, filename in DIRECT_FILES.items()
        },
        "created_at": inputs.created_at,
        "expires_at": inputs.expires_at,
        "live_mutation_authorized": False,
        "outcome_id": inputs.outcome_id,
        "schema": MANIFEST_SCHEMA_ID,
        "source_audit_sha256": sha256_bytes(inputs.source_evidence),
        "source_role": "usa-source",
        "target_audit_sha256": sha256_bytes(inputs.target_evidence),
        "target_role": "spain-target",
    }
    return artifacts, manifest


def materialize_prepared_package(
    inputs: PreparedStagePackageInputs, output_root: Path
) -> ProductionPackageReceipt:
    artifacts, manifest = _validate_prepared(inputs)
    root = Path(output_root)
    _create_private_root(root)
    try:
        for name in sorted(artifacts):
            _write_exclusive(root / name, artifacts[name])
        manifest_bytes = canonical_json_bytes(manifest)
        _write_exclusive(root / "manifest.json", manifest_bytes)
        verify_local_package(root, now=inputs.created_at)
        hashes = tuple(
            (name, sha256_bytes((root / name).read_bytes()))
            for name in sorted(PACKAGE_FILES)
        )
        return ProductionPackageReceipt(
            output_root=root,
            manifest_sha256=sha256_bytes(manifest_bytes),
            artifact_sha256=hashes,
            outcome_id=inputs.outcome_id,
            expires_at=inputs.expires_at,
        )
    except BaseException:
        _cleanup_incomplete(root)
        raise


def verify_local_package(package_root: Path, *, now: str | datetime) -> dict[str, object]:
    root = Path(package_root)
    _safe_directory(root)
    items = list(root.iterdir())
    if {path.name for path in items} != PACKAGE_FILES:
        raise ProductionPackageError("package file set invalid")
    for path in items:
        _safe_regular(path)
    manifest_bytes = (root / "manifest.json").read_bytes()
    manifest = _canonical_object(manifest_bytes, "manifest")
    if set(manifest) != {
        "artifacts",
        "created_at",
        "expires_at",
        "live_mutation_authorized",
        "outcome_id",
        "schema",
        "source_audit_sha256",
        "source_role",
        "target_audit_sha256",
        "target_role",
    }:
        raise ProductionPackageError("manifest keys invalid")
    current = _parse_time(now, "now") if isinstance(now, str) else now.astimezone(timezone.utc)
    if (
        manifest.get("schema") != MANIFEST_SCHEMA_ID
        or manifest.get("source_role") != "usa-source"
        or manifest.get("target_role") != "spain-target"
        or manifest.get("live_mutation_authorized") is not False
        or OUTCOME_PATTERN.fullmatch(str(manifest.get("outcome_id", ""))) is None
        or _parse_time(manifest.get("expires_at"), "expires_at") <= current
    ):
        raise ProductionPackageError("manifest contract invalid")
    direct = manifest.get("artifacts")
    if not isinstance(direct, dict) or set(direct) != set(DIRECT_FILES):
        raise ProductionPackageError("manifest artifact set invalid")
    for key, filename in DIRECT_FILES.items():
        binding = direct.get(key)
        value = (root / filename).read_bytes()
        if (
            not isinstance(binding, dict)
            or set(binding) != {"path", "sha256", "size"}
            or binding.get("path") != filename
            or binding.get("size") != len(value)
            or binding.get("sha256") != sha256_bytes(value)
        ):
            raise ProductionPackageError("manifest artifact binding invalid")
    rollback = _canonical_object((root / "rollback-plan.json").read_bytes(), "rollback plan")
    if set(rollback) != {
        "artifact_bindings",
        "expected",
        "heads",
        "max_attempts",
        "process_contract",
        "safety",
        "schema",
        "source",
        "trust_bundles",
    } or rollback.get("schema") != ROLLBACK_SCHEMA_ID:
        raise ProductionPackageError("rollback plan contract invalid")
    bindings = rollback.get("artifact_bindings")
    if not isinstance(bindings, dict) or set(bindings) != INDIRECT_FILES:
        raise ProductionPackageError("indirect artifact binding invalid")
    for name in INDIRECT_FILES:
        binding = bindings.get(name)
        value = (root / name).read_bytes()
        if (
            not isinstance(binding, dict)
            or set(binding) != {"sha256", "size"}
            or binding.get("size") != len(value)
            or binding.get("sha256") != sha256_bytes(value)
        ):
            raise ProductionPackageError("indirect artifact binding invalid")
    heads = rollback.get("heads")
    process = rollback.get("process_contract")
    safety = rollback.get("safety")
    source = rollback.get("source")
    expected = rollback.get("expected")
    trust = rollback.get("trust_bundles")
    if (
        rollback.get("max_attempts") != 1
        or not isinstance(heads, dict)
        or heads.get("root_base") != ROOT_BASE_HEAD
        or heads.get("amn2") != AMN2_HEAD
        or re.fullmatch(r"[0-9a-f]{40}", str(heads.get("tooling", ""))) is None
        or not isinstance(process, dict)
        or process.get("expected_ssh_processes") != 3
        or process.get("scp") is not False
        or process.get("remote_temp_package") is not False
        or process.get("retries") != 0
        or not isinstance(safety, dict)
        or set(safety.values()) != {False}
        or not isinstance(source, dict)
        or OUTCOME_PATTERN.fullmatch(str(source.get("source_outcome_id", ""))) is None
        or not isinstance(expected, dict)
        or set(expected) != {
            "awg2_foundation_sha256",
            "foreign_receipt_sha256",
            "foreign_stable_sha256",
            "merged_database_sha256",
            "spain_invariants_sha256",
            "target_before_database_sha256",
            "target_runtime_env_sha256",
        }
        or any(SHA256_PATTERN.fullmatch(str(value)) is None for value in expected.values())
        or not isinstance(trust, dict)
        or set(trust) != {"spain", "usa"}
        or any(binding.get("overridable") is not False for binding in trust.values())
    ):
        raise ProductionPackageError("production binding invalid")
    _validate_existing_schema((root / "manifest.schema.json").read_bytes(), MANIFEST_SCHEMA_ID)
    _validate_existing_schema((root / "failure-evidence.schema.json").read_bytes(), FAILURE_SCHEMA_ID)
    return {
        "collector_sha256": sha256_bytes((root / "readonly-collector.py").read_bytes()),
        "expected": expected,
        "expected_ssh_processes": 3,
        "expires_at": str(manifest["expires_at"]),
        "live_mutation_authorized": False,
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "max_attempts": 1,
        "outcome_id": str(manifest["outcome_id"]),
        "package_builder_sha256": sha256_bytes((root / "production-stage-package.py").read_bytes()),
        "remote_sha256": sha256_bytes((root / "production-stage-remote.py").read_bytes()),
        "runner_sha256": sha256_bytes((root / "production-stage-runner.ps1").read_bytes()),
        "source_outcome_id": str(source["source_outcome_id"]),
        "tooling_head": str(heads["tooling"]),
    }


def exact_approval_phrase(package_root: Path, *, now: str | datetime) -> str:
    binding = verify_local_package(package_root, now=now)
    return (
        "УТВЕРЖДАЮ ОДИН CHECKSUM-BOUND LIVE SPAIN DISABLED-STAGE И WEB/DATA-APPLY "
        f"OUTCOME_{binding['outcome_id']} MANIFEST_SHA_{binding['manifest_sha256']} "
        f"RUNNER_SHA_{binding['runner_sha256']} REMOTE_SHA_{binding['remote_sha256']} "
        f"COLLECTOR_SHA_{binding['collector_sha256']} TOOLING_HEAD_{binding['tooling_head']} "
        f"EXPIRES_AT_{binding['expires_at']} MAX_ATTEMPTS_1 "
        "THREE_SSH_NO_BOT_START_NO_USA_MUTATION_NO_AWG_MUTATION_NO_FOREIGN_MUTATION"
    )


def _audit_for_role(audits: object, role: str) -> Mapping[str, object]:
    if not isinstance(audits, list):
        raise ProductionPackageError("audit pair invalid")
    matches = [item for item in audits if isinstance(item, dict) and item.get("role") == role]
    if len(matches) != 1:
        raise ProductionPackageError("audit pair invalid")
    return matches[0]


def _verify_sqlite_bytes(value: bytes, label: str) -> None:
    if not value.startswith(b"SQLite format 3\x00") or len(value) > MAX_ARTIFACT_BYTES:
        raise ProductionPackageError(f"{label} invalid")
    connection = sqlite3.connect(":memory:")
    try:
        connection.deserialize(value)
        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        foreign = connection.execute("PRAGMA foreign_key_check").fetchall()
    finally:
        connection.close()
    if integrity != ("ok",) or foreign:
        raise ProductionPackageError(f"{label} invalid")


def _verified_merged_database_sha256(value: bytes) -> str:
    _verify_sqlite_bytes(value, "merged database")
    return sha256_bytes(value)


def _parse_runtime_delta(value: bytes) -> None:
    try:
        lines = value.decode("utf-8", errors="strict").splitlines()
    except UnicodeError as error:
        raise ProductionPackageError("runtime delta invalid") from error
    values: dict[str, str] = {}
    for line in lines:
        if not line or "=" not in line:
            raise ProductionPackageError("runtime delta invalid")
        name, item = line.split("=", 1)
        if name in values or name not in {"ADMIN_TELEGRAM_IDS", "TELEGRAM_BOT_TOKEN"}:
            raise ProductionPackageError("runtime delta invalid")
        values[name] = item
    if set(values) != {"ADMIN_TELEGRAM_IDS", "TELEGRAM_BOT_TOKEN"}:
        raise ProductionPackageError("runtime delta invalid")
    if not values["TELEGRAM_BOT_TOKEN"] or len(values["TELEGRAM_BOT_TOKEN"]) > 4096:
        raise ProductionPackageError("runtime delta invalid")
    admins = values["ADMIN_TELEGRAM_IDS"].split(",")
    if not admins or any(not item.isdigit() or len(item) > 32 for item in admins):
        raise ProductionPackageError("runtime delta invalid")


def build_remote_envelope(
    package_root: Path,
    audit_pair_bytes: bytes,
    recovery_private_key_pem: bytes,
    *,
    now: str | datetime,
) -> bytes:
    binding = verify_local_package(package_root, now=now)
    audit_pair = _canonical_object(audit_pair_bytes, "audit pair")
    if (
        audit_pair.get("schema") != "amn2.phase13.bot-web-audit-pair.v1"
        or not isinstance(audit_pair.get("safety_receipt"), dict)
        or audit_pair["safety_receipt"].get("ssh_processes") != 2
        or audit_pair["safety_receipt"].get("raw_secret_emitted") is not False
    ):
        raise ProductionPackageError("audit pair invalid")
    usa = _audit_for_role(audit_pair.get("audits"), "usa-source")
    spain = _audit_for_role(audit_pair.get("audits"), "spain-target")
    try:
        merged_plain = bytearray(
            decrypt_hybrid(
                (Path(package_root) / "merged-target.sqlite3.enc").read_bytes(),
                recovery_private_key_pem,
            )
        )
        runtime_plain = bytearray(
            decrypt_hybrid(
                (Path(package_root) / "runtime.env.delta.enc").read_bytes(),
                recovery_private_key_pem,
            )
        )
    except RecoveryCryptoError as error:
        raise ProductionPackageError("sealed input decrypt failed") from error
    try:
        expected = binding["expected"]
        assert isinstance(expected, dict)
        if sha256_bytes(bytes(merged_plain)) != expected["merged_database_sha256"]:
            raise ProductionPackageError("merged database binding invalid")
        _verify_sqlite_bytes(bytes(merged_plain), "merged database")
        _parse_runtime_delta(bytes(runtime_plain))
        usa_services = usa.get("services")
        spain_services = spain.get("services")
        usa_database = usa.get("database")
        spain_database = spain.get("database")
        if (
            not isinstance(usa_services, dict)
            or usa_services.get("bot_active") is not True
            or not isinstance(spain_services, dict)
            or spain_services.get("bot_active") is not False
            or spain_services.get("web_active") is not True
            or spain_services.get("web_loopback_only") is not True
            or not isinstance(usa_database, dict)
            or usa_database.get("integrity_ok") is not True
            or usa_database.get("foreign_key_violations") != 0
            or not isinstance(spain_database, dict)
            or spain_database.get("integrity_ok") is not True
            or spain_database.get("foreign_key_violations") != 0
        ):
            raise ProductionPackageError("audit readiness invalid")
        root = Path(package_root)
        runtime_encrypted = (root / "runtime.env.delta.enc").read_bytes()
        bot_unit = (root / "amn2-spain-bot.service").read_bytes()
        payload = {
            "audit": {
                "spain": {
                    "bot_active": False,
                    "database_integrity_ok": True,
                    "foreign_key_violations": 0,
                    "web_active": True,
                    "web_loopback_only": True,
                },
                "usa": {"bot_active": True},
            },
            "bot_unit_b64": base64.b64encode(bot_unit).decode("ascii"),
            "bot_unit_sha256": sha256_bytes(bot_unit),
            "expires_at": binding["expires_at"],
            "expected": expected,
            "manifest_sha256": binding["manifest_sha256"],
            "max_attempts": 1,
            "merged_database_b64": base64.b64encode(merged_plain).decode("ascii"),
            "outcome_id": binding["outcome_id"],
            "runtime_delta_encrypted_b64": base64.b64encode(runtime_encrypted).decode("ascii"),
            "runtime_delta_encrypted_sha256": sha256_bytes(runtime_encrypted),
            "schema": "amn2.phase13.bot-web-production-stage-input.v1",
        }
        envelope = canonical_json_bytes(
            {
                "payload": payload,
                "payload_sha256": sha256_bytes(canonical_json_bytes(payload)),
                "schema": "amn2.phase13.bot-web-production-stage-envelope.v1",
            }
        )
        if len(envelope) > MAX_REMOTE_INPUT_BYTES:
            raise ProductionPackageError("remote input oversized")
        return envelope
    finally:
        for buffer in (merged_plain, runtime_plain):
            for index in range(len(buffer)):
                buffer[index] = 0


def _extract_role_archive(value: bytes) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(value), mode="r:gz") as archive:
            for member in archive.getmembers():
                name = member.name.removeprefix("./")
                if (
                    not member.isfile()
                    or name not in {"database.sqlite3", "runtime.env", "server-config.yml"}
                    or name in files
                    or member.size < 1
                    or member.size > MAX_ARTIFACT_BYTES
                ):
                    raise ProductionPackageError("role archive invalid")
                handle = archive.extractfile(member)
                if handle is None:
                    raise ProductionPackageError("role archive invalid")
                files[name] = handle.read()
    except (tarfile.TarError, OSError) as error:
        raise ProductionPackageError("role archive invalid") from error
    if set(files) != {"database.sqlite3", "runtime.env", "server-config.yml"}:
        raise ProductionPackageError("role archive invalid")
    return files


def _env_map(value: bytes) -> dict[str, str]:
    try:
        lines = value.decode("utf-8", errors="strict").splitlines()
    except UnicodeError as error:
        raise ProductionPackageError("runtime environment invalid") from error
    result: dict[str, str] = {}
    for line in lines:
        if not line or line.lstrip().startswith("#"):
            continue
        if "=" not in line:
            raise ProductionPackageError("runtime environment invalid")
        name, item = line.split("=", 1)
        if not name or name in result:
            raise ProductionPackageError("runtime environment invalid")
        result[name] = item
    return result


def _database_evidence(value: bytes, role: str) -> bytes:
    _verify_sqlite_bytes(value, "database evidence")
    connection = sqlite3.connect(":memory:")
    try:
        connection.deserialize(value)
        tables = [
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        counts = []
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            counts.append((table, int(connection.execute(f"SELECT count(*) FROM {quoted}").fetchone()[0])))
    finally:
        connection.close()
    return canonical_json_bytes(
        {
            "counts_sha256": sha256_bytes(canonical_json_bytes(counts)),
            "database_integrity_ok": True,
            "foreign_key_violations": 0,
            "role": role,
            "schema": "amn2.phase13.bot-web-package-evidence.v1",
        }
    )


def _private_key_public_pem(private_pem: bytes) -> bytes:
    try:
        from cryptography.hazmat.primitives import serialization

        key = serialization.load_pem_private_key(private_pem, password=None)
        return key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    except Exception as error:
        raise ProductionPackageError("recovery key invalid") from error


def materialize_current_gate(
    *,
    repository_root: Path,
    outcome_id: str,
    created_at: str,
    expires_at: str,
) -> tuple[ProductionPackageReceipt, str]:
    """Materialize the one current verified merge into a fresh fixed package."""

    root = Path(repository_root).resolve(strict=True)
    if root.name != "phase13-bot-web-fresh-inputs":
        raise ProductionPackageError("repository root invalid")
    git_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()
    tracked = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if re.fullmatch(r"[0-9a-f]{40}", git_head) is None or tracked:
        raise ProductionPackageError("committed tooling worktree invalid")
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    if not local.is_absolute():
        raise ProductionPackageError("local private root unavailable")
    source_state = (
        local
        / "AMN2/private-state/phase13-bot-web-migration/fresh-inputs"
        / CURRENT_SOURCE_OUTCOME
    )
    source_artifacts = (
        local
        / "AMN2/private-artifacts/phase13-bot-web-migration/fresh-inputs"
        / CURRENT_SOURCE_OUTCOME
        / "encrypted-inputs"
    )
    merge_state = (
        local
        / "AMN2/private-state/phase13-bot-web-migration/local-merges"
        / CURRENT_MERGE_OUTCOME
    )
    merge_artifacts = (
        local
        / "AMN2/private-artifacts/phase13-bot-web-migration/local-merges"
        / CURRENT_MERGE_OUTCOME
    )
    fixed_paths = {
        "source_manifest": source_artifacts / "encrypted-input-manifest.json",
        "source_backup": source_artifacts / "source-full-backup.enc",
        "target_backup": source_artifacts / "target-before-backup.enc",
        "recovery_key": source_state / "recovery-key/recovery-private.pem",
        "merge_claim": merge_state / "claim.json",
        "merge_preview": merge_artifacts / "merge-preview.json",
        "merge_receipt": merge_artifacts / "local-merge-receipt.json",
        "merged_database": merge_artifacts / "merged-target.sqlite3.enc",
    }
    for path in fixed_paths.values():
        _safe_regular(path)
    source_manifest = fixed_paths["source_manifest"].read_bytes()
    merge_claim = fixed_paths["merge_claim"].read_bytes()
    merge_preview = fixed_paths["merge_preview"].read_bytes()
    merge_receipt = fixed_paths["merge_receipt"].read_bytes()
    merged_encrypted = fixed_paths["merged_database"].read_bytes()
    if (
        sha256_bytes(source_manifest) != CURRENT_SOURCE_MANIFEST_SHA256
        or sha256_bytes(merge_claim) != CURRENT_MERGE_CLAIM_SHA256
        or sha256_bytes(merge_preview) != CURRENT_MERGE_PREVIEW_SHA256
        or sha256_bytes(merge_receipt) != CURRENT_MERGE_RECEIPT_SHA256
        or sha256_bytes(merged_encrypted) != CURRENT_MERGED_DATABASE_SHA256
    ):
        raise ProductionPackageError("verified merge evidence mismatch")
    private_key = fixed_paths["recovery_key"].read_bytes()
    source_encrypted = fixed_paths["source_backup"].read_bytes()
    target_encrypted = fixed_paths["target_backup"].read_bytes()
    try:
        source_plain = bytearray(decrypt_hybrid(source_encrypted, private_key))
        target_plain = bytearray(decrypt_hybrid(target_encrypted, private_key))
        merged_plain = bytearray(decrypt_hybrid(merged_encrypted, private_key))
    except RecoveryCryptoError as error:
        raise ProductionPackageError("verified input decrypt failed") from error
    try:
        source_files = _extract_role_archive(bytes(source_plain))
        target_files = _extract_role_archive(bytes(target_plain))
        source_env = _env_map(source_files["runtime.env"])
        target_env = _env_map(target_files["runtime.env"])
        token = source_env.get("TELEGRAM_BOT_TOKEN", "")
        admins = source_env.get("ADMIN_TELEGRAM_IDS", "")
        if not token or not admins:
            raise ProductionPackageError("allowlisted USA runtime data unavailable")
        if any(
            not target_env.get(name)
            for name in (
                "APP_SECRET_KEY",
                "WEB_ADMIN_PASSWORD_HASH",
                "WEB_ADMIN_SESSION_SECRET",
            )
        ):
            raise ProductionPackageError("Spain target secret preservation unavailable")
        runtime_delta_plain = bytearray(
            f"ADMIN_TELEGRAM_IDS={admins}\nTELEGRAM_BOT_TOKEN={token}\n".encode("utf-8")
        )
        try:
            _parse_runtime_delta(bytes(runtime_delta_plain))
            runtime_delta_encrypted = encrypt_hybrid(
                bytes(runtime_delta_plain), _private_key_public_pem(private_key)
            )
        finally:
            for index in range(len(runtime_delta_plain)):
                runtime_delta_plain[index] = 0
        merged_database_sha256 = _verified_merged_database_sha256(bytes(merged_plain))
        preview_value = _canonical_object(merge_preview, "merge preview")
        invariants = preview_value.get("invariant_hashes")
        if not isinstance(invariants, dict) or not invariants:
            raise ProductionPackageError("Spain invariants unavailable")
        tooling = {
            "amn2-spain-bot.service": (root / "packaging/phase12-spain/units/amn2-spain-bot.service").read_bytes(),
            "audit-ssh-runner.ps1": (root / "scripts/vps/phase13_bot_web_migration_ssh_runner.ps1").read_bytes(),
            "failure-evidence.schema.json": (root / "packaging/phase13-bot-web-migration/failure-evidence.schema.json").read_bytes(),
            "manifest.schema.json": (root / "packaging/phase13-bot-web-migration/manifest.schema.json").read_bytes(),
            "production-stage-package.py": (root / "scripts/phase13_bot_web_migration_production_stage_package.py").read_bytes(),
            "production-stage-remote.py": (root / "scripts/vps/phase13_bot_web_migration_production_stage_remote.py").read_bytes(),
            "production-stage-runner.ps1": (root / "scripts/vps/phase13_bot_web_migration_production_stage_runner.ps1").read_bytes(),
            "readonly-collector.py": (root / "scripts/vps/phase13_bot_web_migration_readonly_remote.py").read_bytes(),
            "recovery_crypto.py": (root / "scripts/phase10_recovery_crypto.py").read_bytes(),
        }
        inputs = PreparedStagePackageInputs(
            amn2_head=AMN2_HEAD,
            created_at=created_at,
            expires_at=expires_at,
            merge_claim=merge_claim,
            merge_preview=merge_preview,
            merge_receipt=merge_receipt,
            merged_database_sha256=merged_database_sha256,
            merged_target_db=merged_encrypted,
            outcome_id=outcome_id,
            recovery_private_key_pem=private_key,
            root_base_head=ROOT_BASE_HEAD,
            runtime_delta_encrypted=runtime_delta_encrypted,
            source_evidence=_database_evidence(source_files["database.sqlite3"], "usa-source"),
            source_full_backup=source_encrypted,
            source_input_manifest=source_manifest,
            source_outcome_id=CURRENT_SOURCE_OUTCOME,
            spain_invariants_sha256=sha256_bytes(canonical_json_bytes(invariants)),
            target_before_backup=target_encrypted,
            target_before_database_sha256=sha256_bytes(target_files["database.sqlite3"]),
            target_evidence=_database_evidence(target_files["database.sqlite3"], "spain-target"),
            target_runtime_env_sha256=sha256_bytes(target_files["runtime.env"]),
            tooling_artifacts=tooling,
            tooling_head=git_head,
        )
        parent = local / "AMN2/private-artifacts/phase13-bot-web-migration/stage-packages"
        parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        output = parent / outcome_id
        package_receipt = materialize_prepared_package(inputs, output)
        approval = exact_approval_phrase(output, now=created_at)
        return package_receipt, approval
    finally:
        for buffer in (source_plain, target_plain, merged_plain):
            for index in range(len(buffer)):
                buffer[index] = 0


def _fixed_recovery_key(package_root: Path, now: datetime) -> bytes:
    binding = verify_local_package(package_root, now=now)
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    if not local.is_absolute():
        raise ProductionPackageError("local private root unavailable")
    path = (
        local
        / "AMN2/private-state/phase13-bot-web-migration/fresh-inputs"
        / str(binding["source_outcome_id"])
        / "recovery-key/recovery-private.pem"
    )
    _safe_regular(path)
    return path.read_bytes()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", choices=("payload",))
    parser.add_argument("package_root")
    args = parser.parse_args(argv)
    try:
        root = Path(args.package_root)
        now = datetime.now(timezone.utc)
        audit = sys.stdin.buffer.read(MAX_REMOTE_INPUT_BYTES + 1)
        if len(audit) > MAX_REMOTE_INPUT_BYTES:
            raise ProductionPackageError("audit input oversized")
        try:
            audit_value = json.loads(
                audit.decode("utf-8", errors="strict"),
                object_pairs_hook=_reject_duplicate_object_pairs,
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ProductionPackageError("audit input invalid") from error
        if not isinstance(audit_value, dict):
            raise ProductionPackageError("audit input invalid")
        envelope = build_remote_envelope(
            root,
            canonical_json_bytes(audit_value),
            _fixed_recovery_key(root, now),
            now=now,
        )
        sys.stdout.buffer.write(envelope)
        return 0
    except (ProductionPackageError, OSError, subprocess.SubprocessError):
        sys.stdout.write("payload_failed\n")
        return 74


if __name__ == "__main__":
    raise SystemExit(main())
