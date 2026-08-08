#!/usr/bin/env python3
"""Checksum-bound Spain-only bot runtime stage for AMN2 Phase 13."""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tarfile
from types import ModuleType
from typing import Callable, Mapping

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.phase13_bot_media_readonly import (
    _create_private_directory,
    _require_regular_file,
    _write_create_new,
)
from scripts.phase13_bot_web_migration_fresh_inputs import (
    FixedRoleBinding,
    MAX_TRANSPORT_INPUT_BYTES as FOUNDATION_MAX_TRANSPORT_INPUT_BYTES,
    MAX_TRANSPORT_OUTPUT_BYTES as FOUNDATION_MAX_TRANSPORT_OUTPUT_BYTES,
    MAX_TRANSPORT_TIMEOUT_SECONDS as FOUNDATION_MAX_TRANSPORT_TIMEOUT_SECONDS,
    load_fixed_role_binding,
    run_bounded_process,
)
from scripts.phase10_recovery_crypto import (
    RecoveryCryptoError,
    decrypt_hybrid,
    encrypt_hybrid,
)


UTC = timezone.utc
PACKAGE_SCHEMA = "amn2.phase13.spain-bot-runtime-stage-package.v1"
SOURCE_PROOF_SCHEMA = "amn2.phase13.spain-bot-runtime-source-proof.v1"
SOURCE_MANIFEST_SCHEMA = "amn2.phase13.spain-accepted-source-manifest.v1"
CLAIM_SCHEMA = "amn2.phase13.spain-bot-runtime-stage-claim.v1"
RECEIPT_SCHEMA = "amn2.phase13.spain-bot-runtime-stage-receipt.v1"
ACCEPTED_SPAIN_SOURCE_HEAD = "55dc243b8e6c6bdb57f8301b56326e4cd4072d19"
AMN2_MIGRATION_HEAD = "910539eaa8051cb1b59131d38b9fa27b9392744d"
CURRENT_SOURCE_OUTCOME = "bot-web-fresh-20260808-142324"
CURRENT_SOURCE_MANIFEST_SHA256 = (
    "3b20ccdf89635875f07962b5998ef613e4b03cbd272bf1ea8a7e8d1b06aff3a1"
)
EXPECTED_AWG2_FOUNDATION_SHA256 = (
    "0e5a5926821d88ae4a2515f9e95cd7c3f69db52100c1a1ec74e99fb794222281"
)
EXPECTED_FOREIGN_STABLE_SHA256 = (
    "f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8"
)
EXPECTED_MIGRATION_ONLY_DIFF = {
    "app/db/schema.py",
    "app/migration/__init__.py",
    "app/migration/bot_web.py",
}
OUTCOME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")
HEAD_PATTERN = re.compile(r"^[0-9a-f]{40}$")
ADMIN_PATTERN = re.compile(r"^[0-9]{1,32}(?:,[0-9]{1,32})*$")
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
MAX_TRANSPORT_BYTES = FOUNDATION_MAX_TRANSPORT_INPUT_BYTES
MAX_OUTPUT_BYTES = 1024 * 1024
FIXED_SSH_EXECUTABLE = r"C:\Windows\System32\OpenSSH\ssh.exe"

ARTIFACT_FILENAMES = {
    "bot_unit": "amn2-spain-bot.service",
    "foundation": "foundation.py",
    "recovery_crypto": "recovery_crypto.py",
    "remote": "remote.py",
    "runner": "runner.py",
    "runtime_delta": "runtime.env.delta.enc",
    "source_manifest": "source-manifest.json",
    "source_proof": "source-proof.json",
}
SAFETY = {
    "awg_mutation_authorized": False,
    "bot_cutover_authorized": False,
    "database_apply_authorized": False,
    "foreign_mutation_authorized": False,
    "runtime_env_update_authorized": True,
    "service_action_authorized": False,
    "source_deploy_authorized": False,
    "usa_access_authorized": False,
}


class RuntimeStageError(RuntimeError):
    """Secret-safe local package or runner failure."""


@dataclass(frozen=True)
class RuntimeStagePackageInputs:
    outcome_id: str
    expires_at: datetime
    tooling_head: str
    runner_bytes: bytes
    remote_bytes: bytes
    foundation_bytes: bytes
    recovery_crypto_bytes: bytes
    runtime_delta_encrypted: bytes
    source_proof: bytes
    source_manifest: bytes
    bot_unit_bytes: bytes


@dataclass(frozen=True)
class RuntimeStagePackageReceipt:
    package_root: Path
    manifest_sha256: str
    outcome_id: str


@dataclass(frozen=True)
class RuntimeStageBinding:
    package_root: Path
    outcome_id: str
    expires_at: datetime
    max_attempts: int
    tooling_head: str
    manifest_sha256: str
    artifact_sha256: tuple[tuple[str, str], ...]
    runner_sha256: str
    remote_sha256: str
    foundation_sha256: str
    runtime_delta_sha256: str
    source_manifest_sha256: str
    source_proof_sha256: str
    safety: Mapping[str, bool]


@dataclass(frozen=True)
class FixedSpainBinding:
    target_host: str
    target_user: str
    key_path: Path
    known_hosts_path: Path


@dataclass(frozen=True)
class RuntimeStageRunReceipt:
    status: str
    outcome_id: str
    ssh_process_count: int
    receipt_path: Path


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _format_utc(value: datetime) -> str:
    if value.tzinfo is None:
        raise RuntimeStageError("timestamp invalid")
    return value.astimezone(UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_utc(value: object) -> datetime:
    if not isinstance(value, str) or re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value
    ) is None:
        raise RuntimeStageError("timestamp invalid")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError as error:
        raise RuntimeStageError("timestamp invalid") from error
    if _format_utc(parsed) != value:
        raise RuntimeStageError("timestamp invalid")
    return parsed


def _canonical_object(value: bytes, label: str) -> dict[str, object]:
    try:
        document = json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeStageError(f"{label} invalid") from error
    if not isinstance(document, dict) or canonical_json_bytes(document) != value:
        raise RuntimeStageError(f"{label} invalid")
    return document


def _validate_source_proof(value: bytes) -> None:
    document = _canonical_object(value, "source proof")
    if (
        set(document)
        != {"accepted_source_head", "bot_web_runtime_equal", "changed_paths", "migration_head", "schema"}
        or document.get("schema") != SOURCE_PROOF_SCHEMA
        or document.get("accepted_source_head") != ACCEPTED_SPAIN_SOURCE_HEAD
        or document.get("migration_head") != AMN2_MIGRATION_HEAD
        or document.get("bot_web_runtime_equal") is not True
        or document.get("changed_paths") != sorted(EXPECTED_MIGRATION_ONLY_DIFF)
    ):
        raise RuntimeStageError("source proof invalid")


def _validate_source_manifest(value: bytes) -> None:
    document = _canonical_object(value, "source manifest")
    if (
        set(document) != {"files", "head", "schema"}
        or document.get("schema") != SOURCE_MANIFEST_SCHEMA
        or document.get("head") != ACCEPTED_SPAIN_SOURCE_HEAD
        or not isinstance(document.get("files"), dict)
        or not document["files"]
    ):
        raise RuntimeStageError("source manifest invalid")
    for name, binding in document["files"].items():
        if (
            not isinstance(name, str)
            or not name.startswith("app/")
            or not isinstance(binding, dict)
            or set(binding) != {"sha256", "size"}
            or SHA_PATTERN.fullmatch(str(binding.get("sha256", ""))) is None
            or not isinstance(binding.get("size"), int)
            or isinstance(binding.get("size"), bool)
            or int(binding["size"]) < 0
        ):
            raise RuntimeStageError("source manifest invalid")


def _validate_inputs(inputs: RuntimeStagePackageInputs) -> None:
    if (
        not isinstance(inputs, RuntimeStagePackageInputs)
        or OUTCOME_PATTERN.fullmatch(inputs.outcome_id) is None
        or HEAD_PATTERN.fullmatch(inputs.tooling_head) is None
        or inputs.expires_at.tzinfo is None
    ):
        raise RuntimeStageError("package inputs invalid")
    values = {
        "runner": inputs.runner_bytes,
        "remote": inputs.remote_bytes,
        "foundation": inputs.foundation_bytes,
        "recovery_crypto": inputs.recovery_crypto_bytes,
        "runtime_delta": inputs.runtime_delta_encrypted,
        "source_proof": inputs.source_proof,
        "source_manifest": inputs.source_manifest,
        "bot_unit": inputs.bot_unit_bytes,
    }
    if any(not isinstance(value, bytes) or not value or len(value) > MAX_ARTIFACT_BYTES for value in values.values()):
        raise RuntimeStageError("package inputs invalid")
    _validate_source_proof(inputs.source_proof)
    _validate_source_manifest(inputs.source_manifest)


def materialize_runtime_stage_package(
    inputs: RuntimeStagePackageInputs, output_parent: Path
) -> RuntimeStagePackageReceipt:
    _validate_inputs(inputs)
    parent = Path(output_parent)
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    package_root = parent / inputs.outcome_id
    if os.path.lexists(package_root):
        raise RuntimeStageError("package root exists")
    os.mkdir(package_root, 0o700)
    artifacts = {
        "bot_unit": inputs.bot_unit_bytes,
        "foundation": inputs.foundation_bytes,
        "recovery_crypto": inputs.recovery_crypto_bytes,
        "remote": inputs.remote_bytes,
        "runner": inputs.runner_bytes,
        "runtime_delta": inputs.runtime_delta_encrypted,
        "source_manifest": inputs.source_manifest,
        "source_proof": inputs.source_proof,
    }
    bindings: dict[str, dict[str, object]] = {}
    for identifier in sorted(artifacts):
        filename = ARTIFACT_FILENAMES[identifier]
        value = artifacts[identifier]
        (package_root / filename).write_bytes(value)
        bindings[identifier] = {
            "filename": filename,
            "sha256": sha256_bytes(value),
            "size": len(value),
        }
    manifest = {
        "accepted_source_head": ACCEPTED_SPAIN_SOURCE_HEAD,
        "artifacts": bindings,
        "created_at": _format_utc(inputs.expires_at - timedelta(hours=2)),
        "expires_at": _format_utc(inputs.expires_at),
        "max_attempts": 1,
        "migration_head": AMN2_MIGRATION_HEAD,
        "outcome_id": inputs.outcome_id,
        "safety": SAFETY,
        "schema": PACKAGE_SCHEMA,
        "tooling_head": inputs.tooling_head,
    }
    manifest_bytes = canonical_json_bytes(manifest)
    (package_root / "manifest.json").write_bytes(manifest_bytes)
    return RuntimeStagePackageReceipt(
        package_root=package_root,
        manifest_sha256=sha256_bytes(manifest_bytes),
        outcome_id=inputs.outcome_id,
    )


def verify_local_runtime_stage_package(
    package_root: Path, *, now: datetime
) -> RuntimeStageBinding:
    root = Path(package_root)
    if not root.is_dir() or root.is_symlink():
        raise RuntimeStageError("package root invalid")
    expected_files = set(ARTIFACT_FILENAMES.values()) | {"manifest.json"}
    actual_files = {item.name for item in root.iterdir()}
    if actual_files != expected_files:
        raise RuntimeStageError("artifact set invalid")
    manifest_bytes = (root / "manifest.json").read_bytes()
    manifest = _canonical_object(manifest_bytes, "manifest")
    if set(manifest) != {
        "accepted_source_head", "artifacts", "created_at", "expires_at",
        "max_attempts", "migration_head", "outcome_id", "safety", "schema", "tooling_head"
    }:
        raise RuntimeStageError("manifest invalid")
    expires_at = _parse_utc(manifest["expires_at"])
    if now.tzinfo is None or expires_at <= now.astimezone(UTC):
        raise RuntimeStageError("package expired")
    if (
        manifest.get("schema") != PACKAGE_SCHEMA
        or manifest.get("max_attempts") != 1
        or manifest.get("accepted_source_head") != ACCEPTED_SPAIN_SOURCE_HEAD
        or manifest.get("migration_head") != AMN2_MIGRATION_HEAD
        or manifest.get("safety") != SAFETY
        or OUTCOME_PATTERN.fullmatch(str(manifest.get("outcome_id", ""))) is None
        or HEAD_PATTERN.fullmatch(str(manifest.get("tooling_head", ""))) is None
    ):
        raise RuntimeStageError("manifest invalid")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != set(ARTIFACT_FILENAMES):
        raise RuntimeStageError("artifact set invalid")
    hashes: dict[str, str] = {}
    for identifier, filename in ARTIFACT_FILENAMES.items():
        binding = artifacts.get(identifier)
        if (
            not isinstance(binding, dict)
            or set(binding) != {"filename", "sha256", "size"}
            or binding.get("filename") != filename
            or SHA_PATTERN.fullmatch(str(binding.get("sha256", ""))) is None
            or not isinstance(binding.get("size"), int)
        ):
            raise RuntimeStageError("artifact binding invalid")
        value = _require_regular_file(root / filename, maximum=MAX_ARTIFACT_BYTES)
        if len(value) != binding["size"] or sha256_bytes(value) != binding["sha256"]:
            raise RuntimeStageError("artifact checksum mismatch")
        hashes[identifier] = str(binding["sha256"])
    _validate_source_proof((root / "source-proof.json").read_bytes())
    _validate_source_manifest((root / "source-manifest.json").read_bytes())
    return RuntimeStageBinding(
        package_root=root,
        outcome_id=str(manifest["outcome_id"]),
        expires_at=expires_at,
        max_attempts=1,
        tooling_head=str(manifest["tooling_head"]),
        manifest_sha256=sha256_bytes(manifest_bytes),
        artifact_sha256=tuple(sorted(hashes.items())),
        runner_sha256=hashes["runner"],
        remote_sha256=hashes["remote"],
        foundation_sha256=hashes["foundation"],
        runtime_delta_sha256=hashes["runtime_delta"],
        source_manifest_sha256=hashes["source_manifest"],
        source_proof_sha256=hashes["source_proof"],
        safety=dict(SAFETY),
    )


def exact_approval_phrase(binding: RuntimeStageBinding) -> str:
    return (
        "УТВЕРЖДАЮ ОДИН CHECKSUM-BOUND LIVE SPAIN BOT/WEB RUNTIME-ONLY DISABLED-STAGE "
        f"OUTCOME_{binding.outcome_id} MANIFEST_SHA_{binding.manifest_sha256} "
        f"RUNNER_SHA_{binding.runner_sha256} REMOTE_SHA_{binding.remote_sha256} "
        f"FOUNDATION_SHA_{binding.foundation_sha256} RUNTIME_DELTA_SHA_{binding.runtime_delta_sha256} "
        f"SOURCE_MANIFEST_SHA_{binding.source_manifest_sha256} SOURCE_PROOF_SHA_{binding.source_proof_sha256} "
        f"TOOLING_HEAD_{binding.tooling_head} EXPIRES_AT_{_format_utc(binding.expires_at)} "
        "MAX_ATTEMPTS_1 ONE_SSH_RUNTIME_ONLY NO_DATABASE_APPLY NO_SOURCE_DEPLOY "
        "NO_SERVICE_ACTION NO_BOT_START NO_USA_ACCESS NO_AWG_MUTATION NO_FOREIGN_MUTATION"
    )


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeStageError("bound module unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        sys.modules.pop(name, None)
        raise RuntimeStageError("bound module unavailable") from error
    return module


def _load_fixed_spain_binding() -> FixedSpainBinding:
    value = load_fixed_role_binding("spain")
    if not isinstance(value, FixedRoleBinding) or value.role != "spain":
        raise RuntimeStageError("fixed Spain binding invalid")
    return FixedSpainBinding(
        target_host=value.target_host,
        target_user=value.target_user,
        key_path=value.key_path,
        known_hosts_path=value.known_hosts_path,
    )


def _decrypt_runtime_delta(binding: RuntimeStageBinding) -> bytes:
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    key_path = (
        local / "AMN2/private-state/phase13-bot-web-migration/fresh-inputs"
        / CURRENT_SOURCE_OUTCOME / "recovery-key/recovery-private.pem"
    )
    private_key = _require_regular_file(key_path, maximum=1024 * 1024)
    encrypted = _require_regular_file(
        binding.package_root / "runtime.env.delta.enc", maximum=1024 * 1024
    )
    crypto = _load_module(
        binding.package_root / "recovery_crypto.py",
        f"phase13_runtime_stage_crypto_{binding.outcome_id.replace('-', '_')}",
    )
    try:
        plain = crypto.decrypt_hybrid(encrypted, private_key)
    except Exception as error:
        raise RuntimeStageError("runtime delta decrypt failed") from error
    if not isinstance(plain, bytes) or len(plain) > 1024 * 1024:
        raise RuntimeStageError("runtime delta invalid")
    return plain


def _parse_remote_receipt(value: bytes, outcome_id: str) -> dict[str, object]:
    receipt = _canonical_object(value, "remote receipt")
    required = {
        "awg2_equal", "bot_disabled", "database_equal", "foreign_equal",
        "marker_absent", "outcome", "outcome_id", "raw_output_persisted", "reason",
        "rolled_back", "runtime_delta_equal", "schema", "service_action_performed",
        "source_equal", "stage", "web_loopback_healthy"
    }
    if (
        set(receipt) != required
        or receipt.get("schema") != RECEIPT_SCHEMA
        or receipt.get("outcome_id") != outcome_id
        or receipt.get("outcome") not in {"success", "failure"}
        or receipt.get("raw_output_persisted") is not False
        or receipt.get("service_action_performed") is not False
    ):
        raise RuntimeStageError("remote receipt invalid")
    return receipt


def run_runtime_stage_gate(
    package_root: Path,
    exact_approval: str,
    *,
    runtime_delta_plain: bytes | None = None,
    process_runner: Callable[..., bytes] = run_bounded_process,
    binding_loader: Callable[[], FixedSpainBinding] = _load_fixed_spain_binding,
    private_root: Path | None = None,
    now: datetime | None = None,
) -> RuntimeStageRunReceipt:
    checked_at = now or datetime.now(UTC)
    binding = verify_local_runtime_stage_package(package_root, now=checked_at)
    if exact_approval != exact_approval_phrase(binding):
        raise RuntimeStageError("exact approval mismatch")
    if process_runner is run_bounded_process:
        current_runner = Path(__file__).read_bytes()
        if sha256_bytes(current_runner) != binding.runner_sha256:
            raise RuntimeStageError("runner source mismatch")
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1],
            check=True, capture_output=True, text=True
        ).stdout.strip()
        if head != binding.tooling_head:
            raise RuntimeStageError("exact head mismatch")
    root = private_root or (
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "AMN2/private-state/phase13-bot-web-migration/spain-runtime-stage"
    )
    _create_private_directory(root)
    outcomes = root / "outcomes"
    receipts = root / "receipts"
    _create_private_directory(outcomes)
    _create_private_directory(receipts)
    claim_path = outcomes / f"{binding.outcome_id}.claim.json"
    claim = {
        "manifest_sha256": binding.manifest_sha256,
        "outcome_id": binding.outcome_id,
        "schema": CLAIM_SCHEMA,
    }
    _write_create_new(claim_path, canonical_json_bytes(claim), private=True)
    delta = bytearray(runtime_delta_plain if runtime_delta_plain is not None else _decrypt_runtime_delta(binding))
    ssh_process_count = 0
    try:
        source_manifest = _require_regular_file(
            binding.package_root / "source-manifest.json", maximum=2 * 1024 * 1024
        )
        remote_bytes = _require_regular_file(binding.package_root / "remote.py", maximum=4 * 1024 * 1024)
        foundation_bytes = _require_regular_file(binding.package_root / "foundation.py", maximum=4 * 1024 * 1024)
        bot_unit = _require_regular_file(binding.package_root / "amn2-spain-bot.service", maximum=1024 * 1024)
        payload = {
            "expires_at": _format_utc(binding.expires_at),
            "expected": {
                "accepted_source_head": ACCEPTED_SPAIN_SOURCE_HEAD,
                "awg2_foundation_sha256": EXPECTED_AWG2_FOUNDATION_SHA256,
                "bot_unit_sha256": sha256_bytes(bot_unit),
                "foreign_stable_sha256": EXPECTED_FOREIGN_STABLE_SHA256,
                "source_manifest_sha256": sha256_bytes(source_manifest),
            },
            "manifest_sha256": binding.manifest_sha256,
            "max_attempts": 1,
            "outcome_id": binding.outcome_id,
            "runtime_delta_b64": base64.b64encode(bytes(delta)).decode("ascii"),
            "runtime_delta_sha256": sha256_bytes(bytes(delta)),
            "schema": "amn2.phase13.spain-bot-runtime-stage-payload.v1",
            "source_manifest_b64": base64.b64encode(source_manifest).decode("ascii"),
        }
        bound = {
            "foundation_b64": base64.b64encode(foundation_bytes).decode("ascii"),
            "foundation_sha256": sha256_bytes(foundation_bytes),
            "payload_b64": base64.b64encode(canonical_json_bytes(payload)).decode("ascii"),
        }
        envelope = canonical_json_bytes(
            {
                "bound": bound,
                "remote_b64": base64.b64encode(remote_bytes).decode("ascii"),
                "remote_sha256": sha256_bytes(remote_bytes),
            }
        )
        if len(envelope) > MAX_TRANSPORT_BYTES:
            raise RuntimeStageError("transport input oversized")
        bootstrap = (
            'import base64,hashlib,json,sys;e=json.load(sys.stdin);'
            's=base64.b64decode(e["remote_b64"],validate=True);'
            'hashlib.sha256(s).hexdigest()==e["remote_sha256"] or sys.exit(70);'
            'g={"__name__":"phase13_bound_spain_runtime_stage"};'
            'exec(compile(s,"<remote>","exec"),g);g["main_bound_envelope"](e["bound"])'
        )
        spain = binding_loader()
        arguments = (
            "-T", "-F", "none", "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=yes", "-o", f"UserKnownHostsFile={spain.known_hosts_path}",
            "-o", "ConnectTimeout=10", "-o", "ConnectionAttempts=1", "-o", "ServerAliveInterval=5",
            "-o", "ServerAliveCountMax=1", "-i", str(spain.key_path), "-p", "22",
            f"{spain.target_user}@{spain.target_host}", f"python3 -c '{bootstrap}'",
        )
        ssh_process_count = 1
        output = process_runner(
            FIXED_SSH_EXECUTABLE, arguments, envelope,
            timeout_seconds=FOUNDATION_MAX_TRANSPORT_TIMEOUT_SECONDS,
            maximum_input_bytes=MAX_TRANSPORT_BYTES, maximum_output_bytes=MAX_OUTPUT_BYTES
        )
        receipt = _parse_remote_receipt(output, binding.outcome_id)
        receipt_path = receipts / f"{binding.outcome_id}.{receipt['outcome']}.json"
        _write_create_new(receipt_path, canonical_json_bytes(receipt), private=True)
        return RuntimeStageRunReceipt(
            status=str(receipt["outcome"]), outcome_id=binding.outcome_id,
            ssh_process_count=ssh_process_count, receipt_path=receipt_path
        )
    except RuntimeStageError:
        raise
    except Exception as error:
        failure_path = receipts / f"{binding.outcome_id}.failure.json"
        failure = {
            "outcome": "failure",
            "outcome_id": binding.outcome_id,
            "raw_output_persisted": False,
            "reason": "transport_or_remote_failure",
            "schema": "amn2.phase13.spain-bot-runtime-stage-local-failure.v1",
            "ssh_process_count": ssh_process_count,
        }
        try:
            _write_create_new(failure_path, canonical_json_bytes(failure), private=True)
        except Exception:
            pass
        raise RuntimeStageError("runtime stage failed") from error
    finally:
        for index in range(len(delta)):
            delta[index] = 0


def _git(root: Path, *arguments: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", *arguments], cwd=root, check=True, capture_output=True,
        text=not binary
    )
    return result.stdout


def _source_evidence(amn2_root: Path) -> tuple[bytes, bytes]:
    head = str(_git(amn2_root, "rev-parse", "HEAD")).strip()
    tracked = str(_git(amn2_root, "status", "--porcelain", "--untracked-files=no"))
    if head != AMN2_MIGRATION_HEAD or tracked:
        raise RuntimeStageError("AMN2 worktree invalid")
    changed = set(
        str(_git(
            amn2_root, "diff", "--name-only", ACCEPTED_SPAIN_SOURCE_HEAD,
            AMN2_MIGRATION_HEAD, "--", "app"
        )).splitlines()
    )
    if changed != EXPECTED_MIGRATION_ONLY_DIFF:
        raise RuntimeStageError("AMN2 source diff invalid")
    archive_bytes = _git(
        amn2_root, "archive", "--format=tar", ACCEPTED_SPAIN_SOURCE_HEAD, "app",
        binary=True
    )
    assert isinstance(archive_bytes, bytes)
    files: dict[str, dict[str, object]] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:") as archive:
            for member in archive.getmembers():
                if member.isdir():
                    continue
                if not member.isfile() or not member.name.startswith("app/") or ".." in Path(member.name).parts:
                    raise RuntimeStageError("accepted source archive invalid")
                handle = archive.extractfile(member)
                if handle is None:
                    raise RuntimeStageError("accepted source archive invalid")
                value = handle.read()
                files[member.name] = {"sha256": sha256_bytes(value), "size": len(value)}
    except tarfile.TarError as error:
        raise RuntimeStageError("accepted source archive invalid") from error
    proof = canonical_json_bytes(
        {
            "accepted_source_head": ACCEPTED_SPAIN_SOURCE_HEAD,
            "bot_web_runtime_equal": True,
            "changed_paths": sorted(changed),
            "migration_head": AMN2_MIGRATION_HEAD,
            "schema": SOURCE_PROOF_SCHEMA,
        }
    )
    manifest = canonical_json_bytes(
        {"files": files, "head": ACCEPTED_SPAIN_SOURCE_HEAD, "schema": SOURCE_MANIFEST_SCHEMA}
    )
    _validate_source_proof(proof)
    _validate_source_manifest(manifest)
    return proof, manifest


def _role_archive_files(value: bytes) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(value), mode="r:gz") as archive:
            for member in archive.getmembers():
                name = member.name.removeprefix("./")
                if not member.isfile() or name not in {
                    "database.sqlite3", "runtime.env", "server-config.yml"
                } or name in files or member.size < 1 or member.size > MAX_ARTIFACT_BYTES:
                    raise RuntimeStageError("source archive invalid")
                handle = archive.extractfile(member)
                if handle is None:
                    raise RuntimeStageError("source archive invalid")
                files[name] = handle.read()
    except tarfile.TarError as error:
        raise RuntimeStageError("source archive invalid") from error
    if set(files) != {"database.sqlite3", "runtime.env", "server-config.yml"}:
        raise RuntimeStageError("source archive invalid")
    return files


def _runtime_values(value: bytes) -> dict[str, str]:
    try:
        lines = value.decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise RuntimeStageError("source runtime invalid") from error
    result: dict[str, str] = {}
    for line in lines:
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, item = line.split("=", 1)
        if key in result:
            raise RuntimeStageError("source runtime invalid")
        result[key] = item
    return result


def _public_pem(private_key: bytes) -> bytes:
    try:
        from cryptography.hazmat.primitives import serialization
        key = serialization.load_pem_private_key(private_key, password=None)
        return key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    except Exception as error:
        raise RuntimeStageError("recovery key invalid") from error


def materialize_current_gate(
    *, outcome_id: str, expires_at: datetime
) -> tuple[RuntimeStagePackageReceipt, str]:
    root = Path(__file__).resolve().parents[1]
    tooling_head = str(_git(root, "rev-parse", "HEAD")).strip()
    tracked = str(_git(root, "status", "--porcelain", "--untracked-files=no"))
    if HEAD_PATTERN.fullmatch(tooling_head) is None or tracked:
        raise RuntimeStageError("tooling worktree invalid")
    amn2_root = root.parent / "amn2-phase13-bot-web-migration"
    proof, source_manifest = _source_evidence(amn2_root)
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    source_state = (
        local / "AMN2/private-state/phase13-bot-web-migration/fresh-inputs"
        / CURRENT_SOURCE_OUTCOME
    )
    source_artifacts = (
        local / "AMN2/private-artifacts/phase13-bot-web-migration/fresh-inputs"
        / CURRENT_SOURCE_OUTCOME / "encrypted-inputs"
    )
    source_manifest_path = source_artifacts / "encrypted-input-manifest.json"
    source_backup_path = source_artifacts / "source-full-backup.enc"
    recovery_key_path = source_state / "recovery-key/recovery-private.pem"
    encrypted_input_manifest = _require_regular_file(source_manifest_path, maximum=2 * 1024 * 1024)
    if sha256_bytes(encrypted_input_manifest) != CURRENT_SOURCE_MANIFEST_SHA256:
        raise RuntimeStageError("accepted encrypted input manifest mismatch")
    manifest_document = _canonical_object(encrypted_input_manifest, "encrypted input manifest")
    source_binding = manifest_document.get("artifacts", {}).get("source-full-backup.enc") if isinstance(manifest_document.get("artifacts"), dict) else None
    source_encrypted = _require_regular_file(source_backup_path, maximum=MAX_ARTIFACT_BYTES)
    if (
        not isinstance(source_binding, dict)
        or source_binding.get("sha256") != sha256_bytes(source_encrypted)
        or source_binding.get("size") != len(source_encrypted)
    ):
        raise RuntimeStageError("accepted encrypted source mismatch")
    private_key = _require_regular_file(recovery_key_path, maximum=1024 * 1024)
    try:
        source_plain = bytearray(decrypt_hybrid(source_encrypted, private_key))
    except RecoveryCryptoError as error:
        raise RuntimeStageError("accepted encrypted source unavailable") from error
    delta = bytearray()
    try:
        source_files = _role_archive_files(bytes(source_plain))
        values = _runtime_values(source_files["runtime.env"])
        token = values.get("TELEGRAM_BOT_TOKEN", "")
        admins = values.get("ADMIN_TELEGRAM_IDS", "")
        if not token or "\n" in token or ADMIN_PATTERN.fullmatch(admins) is None:
            raise RuntimeStageError("allowlisted USA bot runtime unavailable")
        delta.extend(
            f"ADMIN_TELEGRAM_IDS={admins}\nTELEGRAM_BOT_TOKEN={token}\n".encode("utf-8")
        )
        encrypted_delta = encrypt_hybrid(bytes(delta), _public_pem(private_key))
        inputs = RuntimeStagePackageInputs(
            outcome_id=outcome_id,
            expires_at=expires_at,
            tooling_head=tooling_head,
            runner_bytes=Path(__file__).read_bytes(),
            remote_bytes=(root / "scripts/vps/phase13_spain_bot_runtime_stage_remote.py").read_bytes(),
            foundation_bytes=(root / "scripts/vps/phase13_bot_web_migration_production_stage_remote.py").read_bytes(),
            recovery_crypto_bytes=(root / "scripts/phase10_recovery_crypto.py").read_bytes(),
            runtime_delta_encrypted=encrypted_delta,
            source_proof=proof,
            source_manifest=source_manifest,
            bot_unit_bytes=(root / "packaging/phase12-spain/units/amn2-spain-bot.service").read_bytes(),
        )
        parent = local / "AMN2/private-artifacts/phase13-bot-web-migration/runtime-stage-packages"
        receipt = materialize_runtime_stage_package(inputs, parent)
        binding = verify_local_runtime_stage_package(receipt.package_root, now=datetime.now(UTC))
        return receipt, exact_approval_phrase(binding)
    finally:
        for buffer in (source_plain, delta):
            for index in range(len(buffer)):
                buffer[index] = 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    materialize = sub.add_parser("materialize-current")
    materialize.add_argument("--outcome-id", required=True)
    materialize.add_argument("--expires-at", required=True)
    verify = sub.add_parser("verify-local")
    verify.add_argument("package_root", type=Path)
    run = sub.add_parser("run")
    run.add_argument("--package-root", type=Path, required=True)
    run.add_argument("--exact-approval", required=True)
    args = parser.parse_args()
    if args.command == "materialize-current":
        receipt, approval = materialize_current_gate(
            outcome_id=args.outcome_id, expires_at=_parse_utc(args.expires_at)
        )
        binding = verify_local_runtime_stage_package(receipt.package_root, now=datetime.now(UTC))
        print(canonical_json_bytes({
            "approval": approval,
            "artifact_count": len(binding.artifact_sha256),
            "manifest_sha256": binding.manifest_sha256,
            "outcome_id": binding.outcome_id,
            "package_root": str(binding.package_root),
            "status": "materialized",
        }).decode("utf-8"), end="")
        return 0
    if args.command == "verify-local":
        binding = verify_local_runtime_stage_package(args.package_root, now=datetime.now(UTC))
        print(canonical_json_bytes({
            "artifact_count": len(binding.artifact_sha256),
            "manifest_sha256": binding.manifest_sha256,
            "outcome_id": binding.outcome_id,
            "status": "verified",
        }).decode("utf-8"), end="")
        return 0
    receipt = run_runtime_stage_gate(args.package_root, args.exact_approval)
    print(canonical_json_bytes({
        "outcome_id": receipt.outcome_id,
        "ssh_process_count": receipt.ssh_process_count,
        "status": receipt.status,
    }).decode("utf-8"), end="")
    return 0 if receipt.status == "success" else 75


if __name__ == "__main__":
    raise SystemExit(main())
