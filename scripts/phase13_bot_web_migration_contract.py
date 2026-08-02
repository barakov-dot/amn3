"""Local-only integrity contract for the Phase 13 bot/web migration bundle."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat


class ContractError(ValueError):
    pass


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_PATHS = {
    "source_full_backup": "source-full-backup.enc",
    "target_before_backup": "target-before-backup.enc",
    "merged_target_db": "merged-target.sqlite3.enc",
    "merge_preview": "merge-preview.json",
    "rollback_plan": "rollback-plan.json",
}
PLAN_KEYS = {
    "schema",
    "migration_id",
    "source_role",
    "target_role",
    "source_audit_sha256",
    "target_audit_sha256",
    "preserve_target_app_secrets",
    "api_tokens_reissue_required",
    "usable_secret_records_imported",
    "live_mutation_authorized",
}
MANIFEST_KEYS = {
    "schema",
    "outcome_id",
    "created_at",
    "expires_at",
    "source_role",
    "target_role",
    "source_audit_sha256",
    "target_audit_sha256",
    "artifacts",
    "live_mutation_authorized",
}


def canonical_json_bytes(value: Mapping[str, object]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _is_reparse_point(metadata: os.stat_result) -> bool:
    attributes = getattr(metadata, "st_file_attributes", 0)
    return bool(attributes & 0x400)


def _require_safe_directory(path: Path) -> None:
    try:
        metadata = os.lstat(path)
    except OSError as error:
        raise ContractError("artifact root unavailable") from error
    if stat.S_ISLNK(metadata.st_mode) or _is_reparse_point(metadata):
        raise ContractError("artifact root symlink")
    if not stat.S_ISDIR(metadata.st_mode):
        raise ContractError("artifact root is not a directory")


def _require_regular_file(path: Path) -> os.stat_result:
    try:
        metadata = os.lstat(path)
    except OSError as error:
        raise ContractError("artifact unavailable") from error
    if stat.S_ISLNK(metadata.st_mode) or _is_reparse_point(metadata):
        raise ContractError("artifact symlink")
    if not stat.S_ISREG(metadata.st_mode):
        raise ContractError("artifact is not a regular file")
    return metadata


def sha256_file(path: Path) -> str:
    _require_regular_file(path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_exact_keys(value: Mapping[str, object], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ContractError(f"{label} keys")


def _require_sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
        raise ContractError(f"{label} sha256")
    return value


def _parse_timestamp(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise ContractError(f"{label} timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError(f"{label} timestamp") from error
    if parsed.tzinfo is None:
        raise ContractError(f"{label} timestamp")
    return parsed.astimezone(timezone.utc)


def _isoformat_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_plan(plan: Mapping[str, object]) -> None:
    _require_exact_keys(plan, PLAN_KEYS, "migration plan")
    if plan["schema"] != "amn2.phase13.bot-web-migration-plan.v1":
        raise ContractError("migration plan schema")
    if plan["source_role"] != "usa-source" or plan["target_role"] != "spain-target":
        raise ContractError("migration plan roles")
    if not isinstance(plan["migration_id"], str):
        raise ContractError("migration plan id")
    _require_sha256(plan["source_audit_sha256"], "source audit")
    _require_sha256(plan["target_audit_sha256"], "target audit")
    if plan["preserve_target_app_secrets"] is not True:
        raise ContractError("target secret preservation")
    if not isinstance(plan["api_tokens_reissue_required"], int) or plan["api_tokens_reissue_required"] < 0:
        raise ContractError("api token reissue count")
    if plan["usable_secret_records_imported"] != 0:
        raise ContractError("usable secret import")
    if plan["live_mutation_authorized"] is not False:
        raise ContractError("live mutation authorization")


def _validate_manifest(manifest: Mapping[str, object], *, now: datetime) -> None:
    _require_exact_keys(manifest, MANIFEST_KEYS, "manifest")
    if manifest["schema"] != "amn2.phase13.bot-web-migration-manifest.v1":
        raise ContractError("manifest schema")
    if manifest["source_role"] != "usa-source" or manifest["target_role"] != "spain-target":
        raise ContractError("manifest roles")
    if not isinstance(manifest["outcome_id"], str):
        raise ContractError("manifest outcome id")
    _parse_timestamp(manifest["created_at"], "created_at")
    if _parse_timestamp(manifest["expires_at"], "expires_at") <= now.astimezone(timezone.utc):
        raise ContractError("manifest expired")
    _require_sha256(manifest["source_audit_sha256"], "source audit")
    _require_sha256(manifest["target_audit_sha256"], "target audit")
    if manifest["live_mutation_authorized"] is not False:
        raise ContractError("live mutation authorization")
    artifacts = manifest["artifacts"]
    if not isinstance(artifacts, Mapping):
        raise ContractError("manifest artifacts")
    _require_exact_keys(artifacts, set(ARTIFACT_PATHS), "manifest artifacts")
    for name, expected_path in ARTIFACT_PATHS.items():
        artifact = artifacts[name]
        if not isinstance(artifact, Mapping):
            raise ContractError("artifact object")
        _require_exact_keys(artifact, {"path", "size", "sha256"}, "artifact")
        path_value = artifact["path"]
        if path_value != expected_path or not _is_safe_relative_path(path_value):
            raise ContractError("artifact path")
        if not isinstance(artifact["size"], int) or isinstance(artifact["size"], bool) or artifact["size"] < 0:
            raise ContractError("artifact size")
        _require_sha256(artifact["sha256"], "artifact")


def _is_safe_relative_path(value: object) -> bool:
    if not isinstance(value, str) or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and path.parts and all(part not in {"", ".", ".."} for part in path.parts)


def build_manifest(
    root: Path,
    plan: Mapping[str, object],
    *,
    outcome_id: str,
    expires_at: datetime,
) -> dict[str, object]:
    _validate_plan(plan)
    if not isinstance(outcome_id, str):
        raise ContractError("manifest outcome id")
    _require_safe_directory(root)
    artifacts: dict[str, object] = {}
    for name, relative_path in ARTIFACT_PATHS.items():
        path = root / relative_path
        metadata = _require_regular_file(path)
        artifacts[name] = {
            "path": relative_path,
            "size": metadata.st_size,
            "sha256": sha256_file(path),
        }
    return {
        "schema": "amn2.phase13.bot-web-migration-manifest.v1",
        "outcome_id": outcome_id,
        "created_at": _isoformat_z(datetime.now(timezone.utc)),
        "expires_at": _isoformat_z(expires_at),
        "source_role": plan["source_role"],
        "target_role": plan["target_role"],
        "source_audit_sha256": plan["source_audit_sha256"],
        "target_audit_sha256": plan["target_audit_sha256"],
        "artifacts": artifacts,
        "live_mutation_authorized": False,
    }


def verify_local(
    root: Path, manifest: Mapping[str, object], *, now: datetime
) -> Mapping[str, object]:
    _validate_manifest(manifest, now=now)
    _require_safe_directory(root)
    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, Mapping)
    for name, relative_path in ARTIFACT_PATHS.items():
        artifact = artifacts[name]
        assert isinstance(artifact, Mapping)
        path = root / relative_path
        metadata = _require_regular_file(path)
        if metadata.st_size != artifact["size"]:
            raise ContractError("artifact size")
        if sha256_file(path) != artifact["sha256"]:
            raise ContractError("artifact checksum")
    return manifest
