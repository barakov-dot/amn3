"""Local-only Phase 13 bot/web two-host audit tooling package contract."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat


ARTIFACT_FILENAMES = {
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

ROOT_HEAD = "408298982ce820b6a73c4f6721ce71e85e9c93e6"
AMN2_HEAD = "910539eaa8051cb1b59131d38b9fa27b9392744d"
MANIFEST_NAME = "manifest.json"
MANIFEST_SCHEMA = "amn2.phase13.bot-web-audit-tooling-manifest.v1"
OUTCOME_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
MAX_ARTIFACT_BYTES = 4 * 1024 * 1024
SAFETY = {
    "backup_allowed": False,
    "bot_cutover_allowed": False,
    "data_transfer_allowed": False,
    "db_apply_allowed": False,
    "live_mutation_authorized": False,
    "package_build_allowed": False,
    "remote_write_allowed": False,
    "usa_release_allowed": False,
}
TRUST_BINDING_IDS = {
    "usa": "phase13-bot-web-runner-fixed-usa-v1",
    "spain": "phase13-bot-web-runner-fixed-spain-v1",
}


class AuditToolingPackageError(ValueError):
    """A secret-safe local audit tooling package failure."""


@dataclass(frozen=True)
class AuditToolingPackageInputs:
    outcome_id: str
    created_at: str
    expires_at: str
    root_head: str
    amn2_head: str
    artifacts: Mapping[str, bytes]


@dataclass(frozen=True)
class AuditToolingPackageReceipt:
    output_root: Path
    manifest_path: Path
    manifest_sha256: str
    artifact_sha256: tuple[tuple[str, str], ...]
    remote_write_allowed: bool = False
    package_build_allowed: bool = False
    live_mutation_authorized: bool = False


def canonical_json_bytes(value: Mapping[str, object]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def materialize_local_audit_tooling_package(
    inputs: AuditToolingPackageInputs,
    output_root: Path,
) -> AuditToolingPackageReceipt:
    """Write supplied, already-reviewed tooling bytes to a new local root."""

    artifacts, created_at, expires_at = _validate_inputs(inputs)
    root = Path(output_root)
    _create_private_root(root)
    try:
        for artifact_id in sorted(ARTIFACT_FILENAMES):
            filename = ARTIFACT_FILENAMES[artifact_id]
            _write_exclusive_nofollow(root / filename, artifacts[artifact_id])

        manifest_artifacts = {
            artifact_id: {
                "filename": ARTIFACT_FILENAMES[artifact_id],
                "sha256": sha256_bytes(artifacts[artifact_id]),
                "size": len(artifacts[artifact_id]),
            }
            for artifact_id in sorted(ARTIFACT_FILENAMES)
        }
        runner_sha256 = manifest_artifacts["ssh_runner"]["sha256"]
        manifest: dict[str, object] = {
            "amn2_head": AMN2_HEAD,
            "artifacts": manifest_artifacts,
            "created_at": _isoformat_z(created_at),
            "expires_at": _isoformat_z(expires_at),
            "max_attempts": 1,
            "outcome_id": inputs.outcome_id,
            "roles": {"source": "usa-source", "target": "spain-target"},
            "root_head": ROOT_HEAD,
            "safety": dict(SAFETY),
            "schema": MANIFEST_SCHEMA,
            "trust_bundles": {
                "spain": {
                    "binding_id": TRUST_BINDING_IDS["spain"],
                    "overridable": False,
                    "role": "spain-target",
                    "runner_sha256": runner_sha256,
                },
                "usa": {
                    "binding_id": TRUST_BINDING_IDS["usa"],
                    "overridable": False,
                    "role": "usa-source",
                    "runner_sha256": runner_sha256,
                },
            },
        }
        manifest_bytes = canonical_json_bytes(manifest)
        _write_exclusive_nofollow(root / MANIFEST_NAME, manifest_bytes)
        verify_local_audit_tooling_package(root, now=created_at)
        hashes = tuple(
            (artifact_id, sha256_bytes(artifacts[artifact_id]))
            for artifact_id in sorted(ARTIFACT_FILENAMES)
        )
        return AuditToolingPackageReceipt(
            output_root=root,
            manifest_path=root / MANIFEST_NAME,
            manifest_sha256=sha256_bytes(manifest_bytes),
            artifact_sha256=hashes,
        )
    except BaseException as error:
        _remove_incomplete_root(root)
        if isinstance(error, AuditToolingPackageError):
            raise
        raise AuditToolingPackageError("audit tooling materialization failed") from error


def verify_local_audit_tooling_package(
    root: Path,
    *,
    now: str | datetime,
) -> Mapping[str, object]:
    """Verify the complete local package without network or process execution."""

    package_root = Path(root)
    _require_safe_directory(package_root)
    expected_files = set(ARTIFACT_FILENAMES.values()) | {MANIFEST_NAME}
    actual_files = set()
    try:
        for entry in os.scandir(package_root):
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                raise AuditToolingPackageError("audit tooling artifact is unsafe")
            actual_files.add(entry.name)
    except OSError as error:
        raise AuditToolingPackageError("audit tooling root is unreadable") from error
    if actual_files != expected_files:
        raise AuditToolingPackageError("audit tooling artifact set is invalid")

    manifest_path = package_root / MANIFEST_NAME
    manifest_bytes = _read_regular_file(manifest_path)
    try:
        manifest = json.loads(manifest_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AuditToolingPackageError("audit tooling manifest is invalid") from error
    if not isinstance(manifest, Mapping) or canonical_json_bytes(manifest) != manifest_bytes:
        raise AuditToolingPackageError("audit tooling manifest is not canonical")
    _validate_manifest(manifest, now=_parse_timestamp(now, "now"))

    artifact_bindings = manifest["artifacts"]
    assert isinstance(artifact_bindings, Mapping)
    for artifact_id, filename in ARTIFACT_FILENAMES.items():
        binding = artifact_bindings[artifact_id]
        assert isinstance(binding, Mapping)
        value = _read_regular_file(package_root / filename)
        if len(value) != binding["size"] or sha256_bytes(value) != binding["sha256"]:
            raise AuditToolingPackageError("audit tooling artifact checksum mismatch")
    return manifest


def _validate_inputs(
    inputs: AuditToolingPackageInputs,
) -> tuple[dict[str, bytes], datetime, datetime]:
    if not isinstance(inputs, AuditToolingPackageInputs):
        raise AuditToolingPackageError("audit tooling inputs are invalid")
    if inputs.root_head != ROOT_HEAD or inputs.amn2_head != AMN2_HEAD:
        raise AuditToolingPackageError("audit tooling source head mismatch")
    if OUTCOME_ID_PATTERN.fullmatch(inputs.outcome_id) is None:
        raise AuditToolingPackageError("audit tooling outcome id is invalid")
    created_at = _parse_timestamp(inputs.created_at, "created_at")
    expires_at = _parse_timestamp(inputs.expires_at, "expires_at")
    if expires_at <= created_at:
        raise AuditToolingPackageError("audit tooling expiry is invalid")
    if not isinstance(inputs.artifacts, Mapping) or set(inputs.artifacts) != set(
        ARTIFACT_FILENAMES
    ):
        raise AuditToolingPackageError("audit tooling artifact set is invalid")
    artifacts: dict[str, bytes] = {}
    for artifact_id in ARTIFACT_FILENAMES:
        value = inputs.artifacts[artifact_id]
        if not isinstance(value, bytes) or not value or len(value) > MAX_ARTIFACT_BYTES:
            raise AuditToolingPackageError("audit tooling artifact bytes are invalid")
        artifacts[artifact_id] = value
    _validate_manifest_schema_bytes(artifacts["audit_tooling_manifest_schema"])
    return artifacts, created_at, expires_at


def _validate_manifest_schema_bytes(value: bytes) -> None:
    try:
        schema = json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AuditToolingPackageError("audit tooling manifest schema is invalid") from error
    manifest_keys = {
        "amn2_head",
        "artifacts",
        "created_at",
        "expires_at",
        "max_attempts",
        "outcome_id",
        "roles",
        "root_head",
        "safety",
        "schema",
        "trust_bundles",
    }
    if (
        not isinstance(schema, Mapping)
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id") != MANIFEST_SCHEMA
        or schema.get("type") != "object"
        or schema.get("additionalProperties") is not False
        or set(schema.get("required", ())) != manifest_keys
        or not isinstance(schema.get("properties"), Mapping)
    ):
        raise AuditToolingPackageError("audit tooling manifest schema is invalid")
    properties = schema["properties"]
    assert isinstance(properties, Mapping)
    if (
        set(properties) != manifest_keys
        or properties.get("schema") != {"const": MANIFEST_SCHEMA}
        or properties.get("root_head") != {"const": ROOT_HEAD}
        or properties.get("amn2_head") != {"const": AMN2_HEAD}
        or properties.get("max_attempts") != {"const": 1}
        or properties.get("outcome_id")
        != {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{2,63}$"}
        or properties.get("created_at")
        != {"type": "string", "format": "date-time"}
        or properties.get("expires_at")
        != {"type": "string", "format": "date-time"}
    ):
        raise AuditToolingPackageError("audit tooling manifest schema is invalid")

    roles = properties.get("roles")
    if (
        not _is_closed_object_schema(roles, {"source", "target"})
        or roles["properties"]
        != {"source": {"const": "usa-source"}, "target": {"const": "spain-target"}}
    ):
        raise AuditToolingPackageError("audit tooling manifest schema is invalid")

    artifacts = properties.get("artifacts")
    if not _is_closed_object_schema(artifacts, set(ARTIFACT_FILENAMES)):
        raise AuditToolingPackageError("audit tooling manifest schema is invalid")
    artifact_schemas = artifacts["properties"]
    for artifact_id, filename in ARTIFACT_FILENAMES.items():
        binding = artifact_schemas.get(artifact_id)
        if (
            not _is_closed_object_schema(binding, {"filename", "sha256", "size"})
            or binding["properties"].get("filename") != {"const": filename}
            or binding["properties"].get("sha256")
            != {"type": "string", "pattern": "^[0-9a-f]{64}$"}
            or binding["properties"].get("size")
            != {
                "type": "integer",
                "minimum": 1,
                "maximum": MAX_ARTIFACT_BYTES,
            }
        ):
            raise AuditToolingPackageError("audit tooling manifest schema is invalid")

    trust = properties.get("trust_bundles")
    if not _is_closed_object_schema(trust, {"usa", "spain"}):
        raise AuditToolingPackageError("audit tooling manifest schema is invalid")
    for role, expected_role in (("usa", "usa-source"), ("spain", "spain-target")):
        binding = trust["properties"].get(role)
        if (
            not _is_closed_object_schema(
                binding, {"binding_id", "overridable", "role", "runner_sha256"}
            )
            or binding["properties"].get("binding_id")
            != {"const": TRUST_BINDING_IDS[role]}
            or binding["properties"].get("overridable") != {"const": False}
            or binding["properties"].get("role") != {"const": expected_role}
            or binding["properties"].get("runner_sha256")
            != {"type": "string", "pattern": "^[0-9a-f]{64}$"}
        ):
            raise AuditToolingPackageError("audit tooling manifest schema is invalid")

    safety = properties.get("safety")
    if (
        not _is_closed_object_schema(safety, set(SAFETY))
        or safety["properties"] != {name: {"const": False} for name in SAFETY}
    ):
        raise AuditToolingPackageError("audit tooling manifest schema is invalid")


def _is_closed_object_schema(value: object, required: set[str]) -> bool:
    return (
        isinstance(value, Mapping)
        and value.get("type") == "object"
        and value.get("additionalProperties") is False
        and set(value.get("required", ())) == required
        and isinstance(value.get("properties"), Mapping)
        and set(value["properties"]) == required
    )


def _validate_manifest(manifest: Mapping[str, object], *, now: datetime) -> None:
    expected_keys = {
        "amn2_head",
        "artifacts",
        "created_at",
        "expires_at",
        "max_attempts",
        "outcome_id",
        "roles",
        "root_head",
        "safety",
        "schema",
        "trust_bundles",
    }
    if set(manifest) != expected_keys:
        raise AuditToolingPackageError("audit tooling manifest keys are invalid")
    if (
        manifest["schema"] != MANIFEST_SCHEMA
        or manifest["root_head"] != ROOT_HEAD
        or manifest["amn2_head"] != AMN2_HEAD
        or manifest["max_attempts"] != 1
        or not isinstance(manifest["outcome_id"], str)
        or OUTCOME_ID_PATTERN.fullmatch(manifest["outcome_id"]) is None
        or manifest["roles"] != {"source": "usa-source", "target": "spain-target"}
        or manifest["safety"] != SAFETY
    ):
        raise AuditToolingPackageError("audit tooling manifest contract is invalid")
    created_at = _parse_timestamp(manifest["created_at"], "created_at")
    expires_at = _parse_timestamp(manifest["expires_at"], "expires_at")
    if created_at >= expires_at:
        raise AuditToolingPackageError("audit tooling manifest time is invalid")
    if created_at > now:
        raise AuditToolingPackageError("audit tooling manifest is not yet valid")
    if expires_at <= now:
        raise AuditToolingPackageError("audit tooling manifest expired")

    artifacts = manifest["artifacts"]
    if not isinstance(artifacts, Mapping) or set(artifacts) != set(ARTIFACT_FILENAMES):
        raise AuditToolingPackageError("audit tooling artifact set is invalid")
    for artifact_id, filename in ARTIFACT_FILENAMES.items():
        binding = artifacts[artifact_id]
        if (
            isinstance(binding, Mapping)
            and isinstance(binding.get("size"), int)
            and not isinstance(binding.get("size"), bool)
            and binding["size"] > MAX_ARTIFACT_BYTES
        ):
            raise AuditToolingPackageError("audit tooling artifact size is invalid")
        if (
            not isinstance(binding, Mapping)
            or set(binding) != {"filename", "sha256", "size"}
            or binding["filename"] != filename
            or not isinstance(binding["sha256"], str)
            or SHA256_PATTERN.fullmatch(binding["sha256"]) is None
            or not isinstance(binding["size"], int)
            or isinstance(binding["size"], bool)
            or binding["size"] < 1
        ):
            raise AuditToolingPackageError("audit tooling artifact binding is invalid")

    runner_sha256 = artifacts["ssh_runner"]["sha256"]
    expected_trust = {
        "spain": {
            "binding_id": TRUST_BINDING_IDS["spain"],
            "overridable": False,
            "role": "spain-target",
            "runner_sha256": runner_sha256,
        },
        "usa": {
            "binding_id": TRUST_BINDING_IDS["usa"],
            "overridable": False,
            "role": "usa-source",
            "runner_sha256": runner_sha256,
        },
    }
    if manifest["trust_bundles"] != expected_trust:
        raise AuditToolingPackageError("audit tooling trust binding is invalid")


def _parse_timestamp(value: object, label: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise AuditToolingPackageError(f"{label} is invalid") from error
    else:
        raise AuditToolingPackageError(f"{label} is invalid")
    if parsed.tzinfo is None:
        raise AuditToolingPackageError(f"{label} is invalid")
    return parsed.astimezone(timezone.utc)


def _isoformat_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _is_reparse_point(metadata: os.stat_result) -> bool:
    return bool(getattr(metadata, "st_file_attributes", 0) & 0x400)


def _require_safe_directory(path: Path) -> None:
    try:
        metadata = os.lstat(path)
    except OSError as error:
        raise AuditToolingPackageError("audit tooling root is unavailable") from error
    if (
        stat.S_ISLNK(metadata.st_mode)
        or _is_reparse_point(metadata)
        or not stat.S_ISDIR(metadata.st_mode)
    ):
        raise AuditToolingPackageError("audit tooling root is unsafe")


def _create_private_root(root: Path) -> None:
    if os.path.lexists(root):
        raise AuditToolingPackageError("audit tooling output root already exists")
    _require_safe_directory(root.parent)
    try:
        os.mkdir(root, 0o700)
    except OSError as error:
        raise AuditToolingPackageError("audit tooling output root creation failed") from error
    _require_safe_directory(root)


def _write_exclusive_nofollow(path: Path, value: bytes) -> None:
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_BINARY", 0)
    )
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise AuditToolingPackageError("audit tooling artifact creation failed") from error
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or _is_reparse_point(metadata):
            raise AuditToolingPackageError("audit tooling artifact is unsafe")
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _read_regular_file(path: Path) -> bytes:
    try:
        metadata = os.lstat(path)
        if (
            stat.S_ISLNK(metadata.st_mode)
            or _is_reparse_point(metadata)
            or not stat.S_ISREG(metadata.st_mode)
        ):
            raise AuditToolingPackageError("audit tooling artifact is unsafe")
        return path.read_bytes()
    except AuditToolingPackageError:
        raise
    except OSError as error:
        raise AuditToolingPackageError("audit tooling artifact is unavailable") from error


def _remove_incomplete_root(root: Path) -> None:
    if not os.path.lexists(root):
        return
    try:
        metadata = os.lstat(root)
    except OSError:
        return
    if (
        stat.S_ISLNK(metadata.st_mode)
        or _is_reparse_point(metadata)
        or not stat.S_ISDIR(metadata.st_mode)
    ):
        return
    for filename in sorted(set(ARTIFACT_FILENAMES.values()) | {MANIFEST_NAME}):
        path = root / filename
        if not os.path.lexists(path):
            continue
        try:
            item = os.lstat(path)
            if stat.S_ISREG(item.st_mode) and not _is_reparse_point(item):
                path.unlink()
        except OSError:
            pass
    try:
        root.rmdir()
    except OSError:
        pass
