#!/usr/bin/env python
"""Materialize a deterministic Phase 13 bot/web migration fixture package."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import stat
import struct
from typing import Mapping

from scripts.phase10_full_recovery_bundle import (
    MAX_SOURCE_FILE_BYTES,
    sha256_bytes,
)
from scripts.phase10_recovery_crypto import MAGIC, WRAPPED_KEY_LENGTH_BYTES
from scripts.phase13_bot_web_migration_contract import (
    ContractError,
    build_manifest,
    canonical_json_bytes,
    verify_local,
)


OUTCOME_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
MIN_WRAPPED_KEY_BYTES = 3072 // 8
MANIFEST_NAME = "manifest.json"
ARTIFACT_FILES = {
    "merge-preview.json",
    "merged-target.sqlite3.enc",
    "migration-plan.json",
    "rollback-plan.json",
    "source-audit.json",
    "source-full-backup.enc",
    "ssh-runner.ps1",
    "target-audit.json",
    "target-before-backup.enc",
}
ADDITIONAL_BOUND_FILES = {
    "migration-plan.json",
    "source-audit.json",
    "ssh-runner.ps1",
    "target-audit.json",
}
AUDIT_KEYS = {
    "checked_at",
    "database",
    "environment",
    "required_artifacts",
    "role",
    "safety_receipt",
    "schema",
    "services",
}
FORBIDDEN_PUBLIC_KEYS = {
    "admin_telegram_ids",
    "app_secret_key",
    "config_payload",
    "peer_private_key",
    "preshared_key",
    "raw_output",
    "session_secret",
    "stderr",
    "stdout",
    "telegram_bot_token",
    "web_password_hash",
}


class PackageError(ValueError):
    """A secret-safe local materialization failure."""


@dataclass(frozen=True)
class PackageInputs:
    outcome_id: str
    created_at: str
    expires_at: str
    source_audit: bytes
    target_audit: bytes
    migration_plan: bytes
    source_full_backup: bytes
    source_backup_encrypted: bool
    target_before_backup: bytes
    target_backup_encrypted: bool
    merged_target_db: bytes
    merged_target_encrypted: bool
    merge_preview: bytes
    rollback_plan: bytes
    reviewed_runner: bytes
    external_key_stored_separately: bool


@dataclass(frozen=True)
class PackageReceipt:
    output_root: Path
    manifest_path: Path
    manifest_sha256: str
    artifact_sha256: tuple[tuple[str, str], ...]
    live_mutation_authorized: bool = False
    external_key_in_package: bool = False
    plaintext_database_written: bool = False


def materialize_local_package(
    inputs: PackageInputs,
    output_root: Path,
) -> PackageReceipt:
    """Write already-supplied fixture bytes to a new private artifact root."""

    artifacts, plan, created_at, expires_at = _validate_inputs(inputs)
    root = Path(output_root)
    _create_private_root(root)
    try:
        for name in sorted(artifacts):
            _write_exclusive_nofollow(root / name, artifacts[name])

        try:
            manifest = build_manifest(
                root,
                plan,
                outcome_id=inputs.outcome_id,
                expires_at=expires_at,
            )
        except ContractError as error:
            raise PackageError("package manifest contract failed") from error
        manifest["created_at"] = _isoformat_z(created_at)
        manifest["expires_at"] = _isoformat_z(expires_at)
        manifest_bytes = canonical_json_bytes(manifest)
        _write_exclusive_nofollow(root / MANIFEST_NAME, manifest_bytes)
        try:
            verify_local(root, manifest, now=created_at)
        except ContractError as error:
            raise PackageError("package manifest verification failed") from error

        hashes = tuple(
            (name, sha256_bytes((root / name).read_bytes()))
            for name in sorted(ARTIFACT_FILES)
        )
        return PackageReceipt(
            output_root=root,
            manifest_path=root / MANIFEST_NAME,
            manifest_sha256=sha256_bytes(manifest_bytes),
            artifact_sha256=hashes,
        )
    except BaseException as error:
        _remove_incomplete_root(root)
        if isinstance(error, PackageError):
            raise
        raise PackageError("package materialization failed") from error


def _validate_inputs(
    inputs: PackageInputs,
) -> tuple[dict[str, bytes], Mapping[str, object], datetime, datetime]:
    if not isinstance(inputs, PackageInputs):
        raise PackageError("package inputs are invalid")
    if inputs.source_backup_encrypted is not True:
        raise PackageError("encrypted source backup is required")
    if inputs.target_backup_encrypted is not True:
        raise PackageError("encrypted target backup is required")
    if inputs.merged_target_encrypted is not True:
        raise PackageError("encrypted merged target is required")
    if inputs.external_key_stored_separately is not True:
        raise PackageError("external encryption key boundary is required")
    if OUTCOME_ID_PATTERN.fullmatch(inputs.outcome_id) is None:
        raise PackageError("outcome id is invalid")

    created_at = _parse_timestamp(inputs.created_at, "created_at")
    expires_at = _parse_timestamp(inputs.expires_at, "expires_at")
    if expires_at <= created_at:
        raise PackageError("package expiry is invalid")

    encrypted = {
        "source-full-backup.enc": inputs.source_full_backup,
        "target-before-backup.enc": inputs.target_before_backup,
        "merged-target.sqlite3.enc": inputs.merged_target_db,
    }
    for label, value in encrypted.items():
        _require_encrypted_envelope(value, label)

    source_audit = _load_canonical_json(inputs.source_audit, "source audit")
    target_audit = _load_canonical_json(inputs.target_audit, "target audit")
    plan = _load_canonical_json(inputs.migration_plan, "migration plan")
    preview = _load_canonical_json(inputs.merge_preview, "merge preview")
    rollback = _load_canonical_json(inputs.rollback_plan, "rollback plan")
    if plan.get("migration_id") != inputs.outcome_id:
        raise PackageError("outcome binding to migration plan is invalid")
    _validate_safe_evidence(source_audit, target_audit, plan, preview, rollback)
    _validate_rollback_bindings(inputs, rollback)
    _require_safe_public_bytes(inputs.reviewed_runner, "reviewed runner")

    artifacts = {
        **encrypted,
        "source-audit.json": inputs.source_audit,
        "target-audit.json": inputs.target_audit,
        "migration-plan.json": inputs.migration_plan,
        "merge-preview.json": inputs.merge_preview,
        "rollback-plan.json": inputs.rollback_plan,
        "ssh-runner.ps1": inputs.reviewed_runner,
    }
    if set(artifacts) != ARTIFACT_FILES:
        raise PackageError("package artifact set is invalid")
    for value in artifacts.values():
        if len(value) > MAX_SOURCE_FILE_BYTES:
            raise PackageError("package artifact exceeds the size limit")
    return artifacts, plan, created_at, expires_at


def _validate_safe_evidence(
    source_audit: Mapping[str, object],
    target_audit: Mapping[str, object],
    plan: Mapping[str, object],
    preview: Mapping[str, object],
    rollback: Mapping[str, object],
) -> None:
    _validate_audit(source_audit, "usa-source", "source")
    _validate_audit(target_audit, "spain-target", "target")
    if plan.get("source_audit_sha256") != sha256_bytes(
        canonical_json_bytes(source_audit)
    ):
        raise PackageError("source audit binding is invalid")
    if plan.get("target_audit_sha256") != sha256_bytes(
        canonical_json_bytes(target_audit)
    ):
        raise PackageError("target audit binding is invalid")
    if plan.get("live_mutation_authorized") is not False:
        raise PackageError("migration plan live mutation boundary is invalid")
    if plan.get("usable_secret_records_imported") != 0:
        raise PackageError("migration plan secret import boundary is invalid")
    if preview.get("apply_allowed") is not True:
        raise PackageError("merge preview is not applyable")
    if preview.get("live_mutation_authorized") is not False:
        raise PackageError("merge preview live mutation boundary is invalid")
    if preview.get("usable_secret_records_imported") != 0:
        raise PackageError("merge preview secret import boundary is invalid")
    _reject_forbidden_public_keys(preview, "merge preview")
    if set(rollback) != {
        "artifact_bindings",
        "live_mutation_authorized",
        "restore_apply_authorized",
        "schema",
    }:
        raise PackageError("rollback plan keys are invalid")
    if rollback.get("schema") != "amn2.phase13.bot-web-migration-rollback-plan.v1":
        raise PackageError("rollback schema is invalid")
    if rollback.get("live_mutation_authorized") is not False:
        raise PackageError("rollback live mutation boundary is invalid")
    if rollback.get("restore_apply_authorized") is not False:
        raise PackageError("rollback apply boundary is invalid")


def _validate_audit(
    audit: Mapping[str, object],
    expected_role: str,
    label: str,
) -> None:
    if set(audit) != AUDIT_KEYS:
        raise PackageError(f"{label} audit keys are invalid")
    if audit.get("schema") != "amn2.phase13.bot-web-audit.v1":
        raise PackageError(f"{label} audit schema is invalid")
    if audit.get("role") != expected_role:
        raise PackageError(f"{label} audit role is invalid")
    _parse_timestamp(audit.get("checked_at"), f"{label} audit checked_at")
    services = audit.get("services")
    if (
        not isinstance(services, Mapping)
        or set(services) != {"web_active", "bot_active", "web_loopback_only"}
        or any(type(value) is not bool for value in services.values())
    ):
        raise PackageError(f"{label} audit services are invalid")
    database = audit.get("database")
    if (
        not isinstance(database, Mapping)
        or set(database)
        != {
            "counts_sha256",
            "foreign_key_violations",
            "integrity_ok",
            "schema_sha256",
            "table_count",
        }
    ):
        raise PackageError(f"{label} audit is not verified")
    if (
        database.get("integrity_ok") is not True
        or database.get("foreign_key_violations") != 0
        or not _is_nonnegative_int(database.get("table_count"))
        or not _is_sha256(database.get("schema_sha256"))
        or not _is_sha256(database.get("counts_sha256"))
    ):
        raise PackageError(f"{label} audit is not verified")
    environment = audit.get("environment")
    if (
        not isinstance(environment, Mapping)
        or set(environment)
        != {
            "app_secret_present",
            "session_secret_present",
            "telegram_bot_token_present",
            "web_password_hash_present",
        }
        or any(type(value) is not bool for value in environment.values())
    ):
        raise PackageError(f"{label} audit environment is invalid")
    required = audit.get("required_artifacts")
    if required != {
        "database_readable": True,
        "environment_reference_proof_available": True,
    }:
        raise PackageError(f"{label} audit required artifacts are invalid")
    expected_safety = {
        "mutation_attempted": False,
        "raw_output_persisted": False,
        "secret_bearing_data_persisted": False,
    }
    if audit.get("safety_receipt") != expected_safety:
        raise PackageError(f"{label} audit safety receipt is invalid")


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(r"[0-9a-f]{64}", value) is not None
    )


def _is_nonnegative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _reject_forbidden_public_keys(value: object, label: str) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if isinstance(key, str) and key.lower() in FORBIDDEN_PUBLIC_KEYS:
                raise PackageError(f"{label} contains a forbidden field")
            _reject_forbidden_public_keys(nested, label)
    elif isinstance(value, list):
        for nested in value:
            _reject_forbidden_public_keys(nested, label)


def _validate_rollback_bindings(
    inputs: PackageInputs,
    rollback: Mapping[str, object],
) -> None:
    bindings = rollback.get("artifact_bindings")
    if not isinstance(bindings, Mapping) or set(bindings) != ADDITIONAL_BOUND_FILES:
        raise PackageError("rollback artifact binding set is invalid")
    values = {
        "migration-plan.json": inputs.migration_plan,
        "source-audit.json": inputs.source_audit,
        "ssh-runner.ps1": inputs.reviewed_runner,
        "target-audit.json": inputs.target_audit,
    }
    for name, value in values.items():
        binding = bindings.get(name)
        if not isinstance(binding, Mapping) or set(binding) != {"sha256", "size"}:
            raise PackageError("rollback artifact binding is invalid")
        if binding.get("sha256") != sha256_bytes(value) or binding.get("size") != len(
            value
        ):
            raise PackageError("rollback artifact binding is invalid")


def _load_canonical_json(value: bytes, label: str) -> Mapping[str, object]:
    _require_safe_public_bytes(value, label)
    try:
        parsed = json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PackageError(f"{label} is not canonical JSON") from error
    if not isinstance(parsed, Mapping) or canonical_json_bytes(parsed) != value:
        raise PackageError(f"{label} is not canonical JSON")
    return parsed


def _require_safe_public_bytes(value: bytes, label: str) -> None:
    if not isinstance(value, bytes) or not value:
        raise PackageError(f"{label} bytes are invalid")
    forbidden = (
        b"TELEGRAM_BOT_TOKEN=",
        b"ADMIN_TELEGRAM_IDS=",
        b"APP_SECRET_KEY=",
        b"BEGIN PRIVATE KEY",
        b"BEGIN OPENSSH PRIVATE KEY",
    )
    if any(marker in value for marker in forbidden):
        raise PackageError(f"{label} contains forbidden secret material")


def _require_encrypted_envelope(value: bytes, label: str) -> None:
    if not isinstance(value, bytes) or not value.startswith(MAGIC):
        raise PackageError(f"{label} is not an encrypted recovery envelope")
    header_end = len(MAGIC) + WRAPPED_KEY_LENGTH_BYTES
    if len(value) <= header_end:
        raise PackageError(f"{label} encrypted envelope is truncated")
    wrapped_length = struct.unpack(">I", value[len(MAGIC) : header_end])[0]
    if wrapped_length < MIN_WRAPPED_KEY_BYTES:
        raise PackageError(f"{label} encrypted envelope key is invalid")
    if len(value) <= header_end + wrapped_length:
        raise PackageError(f"{label} encrypted envelope is truncated")


def _parse_timestamp(value: str, label: str) -> datetime:
    if not isinstance(value, str):
        raise PackageError(f"{label} is invalid")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise PackageError(f"{label} is invalid") from error
    if parsed.tzinfo is None:
        raise PackageError(f"{label} is invalid")
    return parsed.astimezone(timezone.utc)


def _isoformat_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _is_reparse_point(metadata: os.stat_result) -> bool:
    return bool(getattr(metadata, "st_file_attributes", 0) & 0x400)


def _create_private_root(root: Path) -> None:
    if os.path.lexists(root):
        raise PackageError("output root already exists")
    parent = root.parent
    try:
        metadata = os.lstat(parent)
    except OSError as error:
        raise PackageError("output parent is unavailable") from error
    if (
        stat.S_ISLNK(metadata.st_mode)
        or _is_reparse_point(metadata)
        or not stat.S_ISDIR(metadata.st_mode)
    ):
        raise PackageError("output parent is unsafe")
    try:
        os.mkdir(root, 0o700)
        created = os.lstat(root)
    except OSError as error:
        raise PackageError("output root creation failed") from error
    if (
        stat.S_ISLNK(created.st_mode)
        or _is_reparse_point(created)
        or not stat.S_ISDIR(created.st_mode)
    ):
        _remove_incomplete_root(root)
        raise PackageError("output root is unsafe")


def _write_exclusive_nofollow(path: Path, value: bytes) -> None:
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_BINARY", 0)
    )
    descriptor = os.open(path, flags, 0o600)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or _is_reparse_point(metadata):
            raise PackageError("package artifact is not a regular file")
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        if os.path.lexists(path):
            metadata = os.lstat(path)
            if stat.S_ISREG(metadata.st_mode) and not _is_reparse_point(metadata):
                path.unlink()
        raise


def _remove_incomplete_root(root: Path) -> None:
    if not os.path.lexists(root):
        return
    metadata = os.lstat(root)
    if stat.S_ISLNK(metadata.st_mode) or _is_reparse_point(metadata):
        return
    if not stat.S_ISDIR(metadata.st_mode):
        return
    for name in sorted(ARTIFACT_FILES | {MANIFEST_NAME}):
        path = root / name
        if not os.path.lexists(path):
            continue
        item = os.lstat(path)
        if stat.S_ISREG(item.st_mode) and not _is_reparse_point(item):
            path.unlink()
    try:
        root.rmdir()
    except OSError:
        pass
