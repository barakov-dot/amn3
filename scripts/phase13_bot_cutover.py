#!/usr/bin/env python3
"""Checksum-bound two-host single-instance bot cutover for AMN2 Phase 13."""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable, Mapping, Protocol

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.phase13_bot_media_readonly import (
    _create_private_directory,
    _require_regular_file,
    _write_create_new,
)
from scripts.phase13_bot_web_migration_fresh_inputs import (
    FixedRoleBinding,
    load_fixed_role_binding,
    run_bounded_process,
)


UTC = timezone.utc
PACKAGE_SCHEMA = "amn2.phase13.bot-cutover-package.v1"
CLAIM_SCHEMA = "amn2.phase13.bot-cutover-claim.v1"
RECEIPT_SCHEMA = "amn2.phase13.bot-cutover-receipt.v1"
REMOTE_RECEIPT_SCHEMA = "amn2.phase13.bot-cutover-remote-receipt.v1"
RUNTIME_STAGE_RECEIPT_SCHEMA = "amn2.phase13.spain-bot-runtime-stage-receipt.v1"
CURRENT_RUNTIME_STAGE_OUTCOME = "spain-bot-runtime-stage-20260809-113453"
MAX_SSH_PROCESSES = 10
MAX_ARTIFACT_BYTES = 8 * 1024 * 1024
MAX_INPUT_BYTES = 4 * 1024 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
FIXED_SSH_EXECUTABLE = r"C:\Windows\System32\OpenSSH\ssh.exe"
OUTCOME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")
HEAD_PATTERN = re.compile(r"^[0-9a-f]{40}$")
ARTIFACT_FILENAMES = {
    "foundation": "foundation.py",
    "remote": "remote.py",
    "runner": "runner.py",
    "runtime_stage_receipt": "runtime-stage-receipt.json",
}
SAFETY = {
    "awg_mutation_authorized": False,
    "bot_cutover_authorized": True,
    "database_apply_authorized": False,
    "foreign_mutation_authorized": False,
    "spain_bot_service_action_authorized": True,
    "usa_bot_service_action_authorized": True,
    "usa_server_shutdown_authorized": False,
    "web_service_action_authorized": False,
}
REMOTE_KEYS = {
    "awg2_equal", "bot_active", "bot_enabled", "bot_process_count",
    "continuation", "database_equal", "foreign_equal", "marker_present",
    "outcome", "raw_output_persisted", "reason", "role", "runtime_equal",
    "schema", "service_action_performed", "source_equal",
    "web_loopback_healthy",
}
DIAGNOSIS_SCHEMA = "amn2.phase13.bot-cutover-preflight-diagnosis.v1"
DIAGNOSIS_REASONS = {
    "completed",
    "envelope_invalid",
    "foundation_invalid",
    "internal_failure",
    "observation_failed",
    "payload_expired",
    "payload_invalid",
    "service_action_failed",
    "transport_failure",
    "unsupported_transition",
}


class CutoverError(RuntimeError):
    """Secret-safe local cutover failure."""


class Transport(Protocol):
    def __call__(
        self, role: str, mode: str,
        continuation: dict[str, str] | None = None,
    ) -> Mapping[str, object]: ...


@dataclass(frozen=True)
class CutoverPackageInputs:
    outcome_id: str
    expires_at: datetime
    tooling_head: str
    runner_bytes: bytes
    remote_bytes: bytes
    foundation_bytes: bytes
    runtime_stage_receipt: bytes


@dataclass(frozen=True)
class CutoverPackageReceipt:
    package_root: Path
    manifest_sha256: str
    outcome_id: str


@dataclass(frozen=True)
class CutoverBinding:
    package_root: Path
    outcome_id: str
    expires_at: datetime
    tooling_head: str
    manifest_sha256: str
    artifact_sha256: tuple[tuple[str, str], ...]
    runner_sha256: str
    remote_sha256: str
    foundation_sha256: str
    runtime_stage_receipt_sha256: str


@dataclass(frozen=True)
class CutoverRunReceipt:
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
        raise CutoverError("timestamp invalid")
    return value.astimezone(UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_utc(value: object) -> datetime:
    if not isinstance(value, str) or re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value
    ) is None:
        raise CutoverError("timestamp invalid")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError as error:
        raise CutoverError("timestamp invalid") from error
    if _format_utc(parsed) != value:
        raise CutoverError("timestamp invalid")
    return parsed


def _canonical_object(value: bytes, label: str) -> dict[str, object]:
    try:
        document = json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CutoverError(f"{label} invalid") from error
    if not isinstance(document, dict) or canonical_json_bytes(document) != value:
        raise CutoverError(f"{label} invalid")
    return document


def _validate_runtime_stage_receipt(value: bytes) -> None:
    document = _canonical_object(value, "runtime stage receipt")
    required_true = {
        "awg2_equal", "bot_disabled", "database_equal", "foreign_equal",
        "marker_absent", "runtime_delta_equal", "source_equal",
        "web_loopback_healthy",
    }
    if (
        document.get("schema") != RUNTIME_STAGE_RECEIPT_SCHEMA
        or document.get("outcome_id") != CURRENT_RUNTIME_STAGE_OUTCOME
        or document.get("outcome") != "success"
        or document.get("reason") != "completed"
        or document.get("rolled_back") is not False
        or document.get("service_action_performed") is not False
        or document.get("raw_output_persisted") is not False
        or any(document.get(key) is not True for key in required_true)
    ):
        raise CutoverError("runtime stage receipt invalid")


def materialize_cutover_package(
    inputs: CutoverPackageInputs, output_parent: Path
) -> CutoverPackageReceipt:
    if (
        not isinstance(inputs, CutoverPackageInputs)
        or OUTCOME_PATTERN.fullmatch(inputs.outcome_id) is None
        or HEAD_PATTERN.fullmatch(inputs.tooling_head) is None
        or inputs.expires_at.tzinfo is None
    ):
        raise CutoverError("package inputs invalid")
    artifacts = {
        "foundation": inputs.foundation_bytes,
        "remote": inputs.remote_bytes,
        "runner": inputs.runner_bytes,
        "runtime_stage_receipt": inputs.runtime_stage_receipt,
    }
    if any(
        not isinstance(value, bytes) or not value or len(value) > MAX_ARTIFACT_BYTES
        for value in artifacts.values()
    ):
        raise CutoverError("package inputs invalid")
    _validate_runtime_stage_receipt(inputs.runtime_stage_receipt)
    parent = Path(output_parent)
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    root = parent / inputs.outcome_id
    if os.path.lexists(root):
        raise CutoverError("package root exists")
    os.mkdir(root, 0o700)
    bindings: dict[str, dict[str, object]] = {}
    for identifier in sorted(artifacts):
        filename = ARTIFACT_FILENAMES[identifier]
        value = artifacts[identifier]
        (root / filename).write_bytes(value)
        bindings[identifier] = {
            "filename": filename,
            "sha256": sha256_bytes(value),
            "size": len(value),
        }
    manifest = {
        "artifacts": bindings,
        "created_at": _format_utc(inputs.expires_at - timedelta(hours=2)),
        "expires_at": _format_utc(inputs.expires_at),
        "max_attempts": 1,
        "max_ssh_processes": MAX_SSH_PROCESSES,
        "outcome_id": inputs.outcome_id,
        "safety": SAFETY,
        "schema": PACKAGE_SCHEMA,
        "tooling_head": inputs.tooling_head,
    }
    manifest_bytes = canonical_json_bytes(manifest)
    (root / "manifest.json").write_bytes(manifest_bytes)
    return CutoverPackageReceipt(root, sha256_bytes(manifest_bytes), inputs.outcome_id)


def verify_local_cutover_package(
    package_root: Path, *, now: datetime
) -> CutoverBinding:
    root = Path(package_root)
    if not root.is_dir() or root.is_symlink():
        raise CutoverError("package root invalid")
    expected = set(ARTIFACT_FILENAMES.values()) | {"manifest.json"}
    if {item.name for item in root.iterdir()} != expected:
        raise CutoverError("artifact set invalid")
    manifest_bytes = _require_regular_file(root / "manifest.json", maximum=MAX_ARTIFACT_BYTES)
    manifest = _canonical_object(manifest_bytes, "manifest")
    if set(manifest) != {
        "artifacts", "created_at", "expires_at", "max_attempts",
        "max_ssh_processes", "outcome_id", "safety", "schema", "tooling_head",
    }:
        raise CutoverError("manifest invalid")
    expires = _parse_utc(manifest["expires_at"])
    if now.tzinfo is None or expires <= now.astimezone(UTC):
        raise CutoverError("package expired")
    if (
        manifest.get("schema") != PACKAGE_SCHEMA
        or manifest.get("max_attempts") != 1
        or manifest.get("max_ssh_processes") != MAX_SSH_PROCESSES
        or manifest.get("safety") != SAFETY
        or OUTCOME_PATTERN.fullmatch(str(manifest.get("outcome_id", ""))) is None
        or HEAD_PATTERN.fullmatch(str(manifest.get("tooling_head", ""))) is None
    ):
        raise CutoverError("manifest invalid")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != set(ARTIFACT_FILENAMES):
        raise CutoverError("artifact set invalid")
    hashes: dict[str, str] = {}
    for identifier, filename in ARTIFACT_FILENAMES.items():
        item = artifacts.get(identifier)
        if (
            not isinstance(item, dict)
            or set(item) != {"filename", "sha256", "size"}
            or item.get("filename") != filename
            or SHA_PATTERN.fullmatch(str(item.get("sha256", ""))) is None
            or not isinstance(item.get("size"), int)
            or isinstance(item.get("size"), bool)
        ):
            raise CutoverError("artifact binding invalid")
        value = _require_regular_file(root / filename, maximum=MAX_ARTIFACT_BYTES)
        if len(value) != item["size"] or sha256_bytes(value) != item["sha256"]:
            raise CutoverError("artifact checksum mismatch")
        hashes[identifier] = str(item["sha256"])
    _validate_runtime_stage_receipt((root / "runtime-stage-receipt.json").read_bytes())
    return CutoverBinding(
        package_root=root,
        outcome_id=str(manifest["outcome_id"]),
        expires_at=expires,
        tooling_head=str(manifest["tooling_head"]),
        manifest_sha256=sha256_bytes(manifest_bytes),
        artifact_sha256=tuple(sorted(hashes.items())),
        runner_sha256=hashes["runner"],
        remote_sha256=hashes["remote"],
        foundation_sha256=hashes["foundation"],
        runtime_stage_receipt_sha256=hashes["runtime_stage_receipt"],
    )


def exact_approval_phrase(binding: CutoverBinding) -> str:
    return (
        "УТВЕРЖДАЮ ОДИН CHECKSUM-BOUND TWO-HOST SINGLE-INSTANCE BOT CUTOVER "
        f"OUTCOME_{binding.outcome_id} MANIFEST_SHA_{binding.manifest_sha256} "
        f"RUNNER_SHA_{binding.runner_sha256} REMOTE_SHA_{binding.remote_sha256} "
        f"FOUNDATION_SHA_{binding.foundation_sha256} "
        f"RUNTIME_STAGE_RECEIPT_SHA_{binding.runtime_stage_receipt_sha256} "
        f"TOOLING_HEAD_{binding.tooling_head} EXPIRES_AT_{_format_utc(binding.expires_at)} "
        "MAX_ATTEMPTS_1 MAX_SSH_PROCESSES_10 USA_ALREADY_ZERO_ALLOWED "
        "STOP_USA_BOT_ONLY START_SPAIN_BOT "
        "ROLLBACK_TO_SINGLE_USA NO_USA_SERVER_SHUTDOWN NO_DATABASE_APPLY "
        "NO_WEB_ACTION NO_AWG_MUTATION NO_FOREIGN_MUTATION"
    )


def exact_diagnosis_approval_phrase(binding: CutoverBinding) -> str:
    return (
        "УТВЕРЖДАЮ ОДИН CHECKSUM-BOUND USA BOT PREFLIGHT READ-ONLY DIAGNOSIS "
        f"OUTCOME_{binding.outcome_id} MANIFEST_SHA_{binding.manifest_sha256} "
        f"RUNNER_SHA_{binding.runner_sha256} REMOTE_SHA_{binding.remote_sha256} "
        f"TOOLING_HEAD_{binding.tooling_head} EXPIRES_AT_{_format_utc(binding.expires_at)} "
        "MAX_ATTEMPTS_1 ONE_SSH_READ_ONLY NO_SERVICE_ACTION NO_SPAIN_ACCESS "
        "NO_USA_SERVER_SHUTDOWN NO_DATABASE_APPLY NO_WEB_ACTION NO_AWG_MUTATION "
        "NO_FOREIGN_MUTATION"
    )


def preflight_diagnosis_receipt(
    remote: Mapping[str, object], outcome_id: str
) -> dict[str, object]:
    raw_reason = str(remote.get("reason", "")).lower()
    reason = raw_reason if raw_reason in DIAGNOSIS_REASONS else "unclassified_failure"
    count = remote.get("bot_process_count")
    safe_count = count if isinstance(count, int) and count in {0, 1} else 0
    active = remote.get("bot_active") is True and safe_count == 1
    outcome = "success" if remote.get("outcome") == "success" else "failure"
    return {
        "bot_active": active,
        "bot_process_count": safe_count,
        "outcome": outcome,
        "outcome_id": outcome_id,
        "raw_output_persisted": False,
        "reason": reason,
        "schema": DIAGNOSIS_SCHEMA,
        "service_action_performed": False,
        "ssh_process_count": 1,
    }


def _call_ok(value: Mapping[str, object]) -> bool:
    return value.get("outcome") == "success"


def _active(value: Mapping[str, object], expected: bool) -> bool:
    return bool(
        _call_ok(value)
        and value.get("bot_active") is expected
        and value.get("bot_process_count") == (1 if expected else 0)
    )


def _result(
    *, outcome: str, reason: str, rolled_back: bool,
    usa_active: bool, spain_active: bool,
) -> dict[str, object]:
    return {
        "outcome": outcome,
        "reason": reason,
        "rolled_back": rolled_back,
        "single_owner": (int(usa_active) + int(spain_active)) == 1,
        "spain_active": spain_active,
        "usa_active": usa_active,
    }


def execute_cutover_state_machine(transport: Transport) -> dict[str, object]:
    usa = transport("usa", "preflight", {})
    usa_initially_active = _active(usa, True)
    usa_initially_zero = _active(usa, False)
    if not (usa_initially_active or usa_initially_zero):
        return _result(
            outcome="failure", reason="USA_BOT_PREFLIGHT_FAILED", rolled_back=False,
            usa_active=bool(usa.get("bot_active", False)), spain_active=False,
        )
    spain = transport("spain", "preflight", {})
    continuation = spain.get("continuation", {})
    if (
        not _active(spain, False)
        or spain.get("marker_present") is not False
        or not isinstance(continuation, dict)
    ):
        return _result(
            outcome="failure", reason="SPAIN_PREFLIGHT_FAILED", rolled_back=False,
            usa_active=True, spain_active=bool(spain.get("bot_active", False)),
        )
    stopped = (
        transport("usa", "stop", {})
        if usa_initially_active
        else usa
    )
    if not _active(stopped, False):
        reason = "USA_BOT_STOP_UNCONFIRMED"
    else:
        started = transport("spain", "start", dict(continuation))
        if _active(started, True) and started.get("marker_present") is True:
            usa_post = transport("usa", "postflight", {})
            spain_post = transport("spain", "postflight", dict(continuation))
            if _active(usa_post, False) and _active(spain_post, True):
                return _result(
                    outcome="success", reason="COMPLETED", rolled_back=False,
                    usa_active=False, spain_active=True,
                )
            reason = "POSTFLIGHT_FAILED"
        else:
            reason = "SPAIN_BOT_ADMISSION_FAILED"
    spain_rollback = transport("spain", "rollback_stop", dict(continuation))
    usa_rollback = (
        transport("usa", "rollback_start", {})
        if usa_initially_active
        else usa
    )
    usa_proof = transport("usa", "postflight", {})
    spain_proof = transport("spain", "postflight", dict(continuation))
    rolled_back = bool(
        _active(spain_rollback, False)
        and spain_rollback.get("marker_present") is False
        and _active(usa_rollback, usa_initially_active)
        and _active(usa_proof, usa_initially_active)
        and _active(spain_proof, False)
        and spain_proof.get("marker_present") is False
    )
    return _result(
        outcome="failure", reason=reason if rolled_back else "ROLLBACK_FAILED",
        rolled_back=rolled_back,
        usa_active=rolled_back and usa_initially_active,
        spain_active=False,
    )


class _ProductionTransport:
    def __init__(
        self, binding: CutoverBinding, roles: Mapping[str, FixedRoleBinding],
        process_runner: Callable[..., bytes],
    ) -> None:
        self.binding = binding
        self.roles = roles
        self.process_runner = process_runner
        self.count = 0
        self.remote = _require_regular_file(binding.package_root / "remote.py", maximum=MAX_ARTIFACT_BYTES)
        self.foundation = _require_regular_file(binding.package_root / "foundation.py", maximum=MAX_ARTIFACT_BYTES)

    def __call__(
        self, role: str, mode: str, continuation: dict[str, str] | None = None,
    ) -> Mapping[str, object]:
        if self.count >= MAX_SSH_PROCESSES:
            return {"outcome": "failure", "reason": "transport_limit"}
        payload = canonical_json_bytes(
            {
                "continuation": dict(continuation or {}),
                "expires_at": _format_utc(self.binding.expires_at),
                "manifest_sha256": self.binding.manifest_sha256,
                "max_attempts": 1,
                "mode": mode,
                "outcome_id": self.binding.outcome_id,
                "role": role,
                "schema": "amn2.phase13.bot-cutover-payload.v1",
            }
        )
        bound = canonical_json_bytes(
            {
                "foundation_b64": base64.b64encode(self.foundation).decode("ascii"),
                "foundation_sha256": sha256_bytes(self.foundation),
                "payload_b64": base64.b64encode(payload).decode("ascii"),
            }
        )
        envelope = canonical_json_bytes(
            {
                "bound_b64": base64.b64encode(bound).decode("ascii"),
                "remote_b64": base64.b64encode(self.remote).decode("ascii"),
                "remote_sha256": sha256_bytes(self.remote),
            }
        )
        if len(envelope) > MAX_INPUT_BYTES:
            return {"outcome": "failure", "reason": "transport_input_oversized"}
        bootstrap = (
            'import base64,hashlib,json,sys;e=json.load(sys.stdin);'
            's=base64.b64decode(e["remote_b64"],validate=True);'
            'hashlib.sha256(s).hexdigest()==e["remote_sha256"] or sys.exit(70);'
            'g={"__name__":"phase13_bound_bot_cutover"};'
            'exec(compile(s,"<remote>","exec"),g);'
            'g["main_bound_envelope"](json.loads(base64.b64decode(e["bound_b64"],validate=True)))'
        )
        binding = self.roles[role]
        arguments = (
            "-T", "-F", "none", "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=yes", "-o", f"UserKnownHostsFile={binding.known_hosts_path}",
            "-o", "ConnectTimeout=10", "-o", "ConnectionAttempts=1", "-o", "ServerAliveInterval=5",
            "-o", "ServerAliveCountMax=1", "-i", str(binding.key_path), "-p", "22",
            f"{binding.target_user}@{binding.target_host}", f"python3 -c '{bootstrap}'",
        )
        self.count += 1
        try:
            output = self.process_runner(
                FIXED_SSH_EXECUTABLE, arguments, envelope,
                timeout_seconds=60, maximum_input_bytes=MAX_INPUT_BYTES,
                maximum_output_bytes=MAX_OUTPUT_BYTES,
            )
            document = _canonical_object(output, "remote receipt")
            if (
                set(document) != REMOTE_KEYS
                or document.get("schema") != REMOTE_RECEIPT_SCHEMA
                or document.get("role") != role
                or document.get("raw_output_persisted") is not False
            ):
                raise CutoverError("remote receipt invalid")
            return document
        except Exception:
            return {
                "bot_active": False,
                "bot_process_count": 0,
                "continuation": {},
                "outcome": "failure",
                "reason": "TRANSPORT_FAILURE",
            }


def run_cutover_gate(
    package_root: Path, exact_approval: str, *,
    now: datetime | None = None,
    process_runner: Callable[..., bytes] = run_bounded_process,
    role_loader: Callable[[str], FixedRoleBinding] = load_fixed_role_binding,
    private_root: Path | None = None,
) -> CutoverRunReceipt:
    checked_at = now or datetime.now(UTC)
    binding = verify_local_cutover_package(package_root, now=checked_at)
    if exact_approval != exact_approval_phrase(binding):
        raise CutoverError("exact approval mismatch")
    if process_runner is run_bounded_process:
        if sha256_bytes(Path(__file__).read_bytes()) != binding.runner_sha256:
            raise CutoverError("runner source mismatch")
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        if head != binding.tooling_head:
            raise CutoverError("exact head mismatch")
    roles = {role: role_loader(role) for role in ("usa", "spain")}
    if any(value.role != role for role, value in roles.items()):
        raise CutoverError("fixed role binding invalid")
    root = private_root or (
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "AMN2/private-state/phase13-bot-web-migration/bot-cutover"
    )
    _create_private_directory(root)
    outcomes, receipts = root / "outcomes", root / "receipts"
    _create_private_directory(outcomes)
    _create_private_directory(receipts)
    _write_create_new(
        outcomes / f"{binding.outcome_id}.claim.json",
        canonical_json_bytes(
            {
                "manifest_sha256": binding.manifest_sha256,
                "outcome_id": binding.outcome_id,
                "schema": CLAIM_SCHEMA,
            }
        ),
        private=True,
    )
    transport = _ProductionTransport(binding, roles, process_runner)
    state = execute_cutover_state_machine(transport)
    terminal = {
        **state,
        "outcome_id": binding.outcome_id,
        "raw_output_persisted": False,
        "schema": RECEIPT_SCHEMA,
        "ssh_process_count": transport.count,
        "usa_server_mutated": False,
    }
    suffix = "success" if state["outcome"] == "success" else "failure"
    path = receipts / f"{binding.outcome_id}.{suffix}.json"
    _write_create_new(path, canonical_json_bytes(terminal), private=True)
    return CutoverRunReceipt(
        status=str(state["outcome"]), outcome_id=binding.outcome_id,
        ssh_process_count=transport.count, receipt_path=path,
    )


def run_preflight_diagnosis(
    package_root: Path, exact_approval: str, *,
    now: datetime | None = None,
    process_runner: Callable[..., bytes] = run_bounded_process,
    role_loader: Callable[[str], FixedRoleBinding] = load_fixed_role_binding,
    private_root: Path | None = None,
) -> CutoverRunReceipt:
    checked_at = now or datetime.now(UTC)
    binding = verify_local_cutover_package(package_root, now=checked_at)
    if exact_approval != exact_diagnosis_approval_phrase(binding):
        raise CutoverError("exact diagnosis approval mismatch")
    if process_runner is run_bounded_process:
        if sha256_bytes(Path(__file__).read_bytes()) != binding.runner_sha256:
            raise CutoverError("runner source mismatch")
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        if head != binding.tooling_head:
            raise CutoverError("exact head mismatch")
    usa = role_loader("usa")
    if usa.role != "usa":
        raise CutoverError("fixed role binding invalid")
    root = private_root or (
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "AMN2/private-state/phase13-bot-web-migration/bot-cutover-diagnosis"
    )
    _create_private_directory(root)
    outcomes, receipts = root / "outcomes", root / "receipts"
    _create_private_directory(outcomes)
    _create_private_directory(receipts)
    _write_create_new(
        outcomes / f"{binding.outcome_id}.claim.json",
        canonical_json_bytes(
            {
                "manifest_sha256": binding.manifest_sha256,
                "outcome_id": binding.outcome_id,
                "schema": CLAIM_SCHEMA,
            }
        ),
        private=True,
    )
    transport = _ProductionTransport(binding, {"usa": usa}, process_runner)
    remote = transport("usa", "preflight", {})
    receipt = preflight_diagnosis_receipt(remote, binding.outcome_id)
    suffix = "success" if receipt["outcome"] == "success" else "failure"
    path = receipts / f"{binding.outcome_id}.{suffix}.json"
    _write_create_new(path, canonical_json_bytes(receipt), private=True)
    return CutoverRunReceipt(
        status=str(receipt["outcome"]), outcome_id=binding.outcome_id,
        ssh_process_count=1, receipt_path=path,
    )


def _current_runtime_stage_receipt() -> Path:
    return (
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "AMN2/private-state/phase13-bot-web-migration/spain-runtime-stage/receipts"
        / f"{CURRENT_RUNTIME_STAGE_OUTCOME}.success.json"
    )


def materialize_current(outcome_id: str, expires_at: datetime) -> tuple[CutoverPackageReceipt, str]:
    root = Path(__file__).resolve().parents[1]
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    tracked = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=root,
        check=True, capture_output=True, text=True,
    ).stdout
    if tracked:
        raise CutoverError("tracked worktree not clean")
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    parent = local / "AMN2/private-artifacts/phase13-bot-web-migration/cutover-packages"
    inputs = CutoverPackageInputs(
        outcome_id=outcome_id,
        expires_at=expires_at,
        tooling_head=head,
        runner_bytes=Path(__file__).read_bytes(),
        remote_bytes=(root / "scripts/vps/phase13_bot_cutover_remote.py").read_bytes(),
        foundation_bytes=(root / "scripts/vps/phase13_bot_web_migration_production_stage_remote.py").read_bytes(),
        runtime_stage_receipt=_require_regular_file(
            _current_runtime_stage_receipt(), maximum=MAX_ARTIFACT_BYTES
        ),
    )
    receipt = materialize_cutover_package(inputs, parent)
    first = verify_local_cutover_package(receipt.package_root, now=datetime.now(UTC))
    second = verify_local_cutover_package(receipt.package_root, now=datetime.now(UTC))
    if first != second:
        raise CutoverError("verify_local nondeterministic")
    return receipt, exact_approval_phrase(first)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    materialize = sub.add_parser("materialize-current")
    materialize.add_argument("--outcome-id", required=True)
    materialize.add_argument("--expires-at", required=True)
    run = sub.add_parser("run")
    run.add_argument("--package-root", type=Path, required=True)
    run.add_argument("--exact-approval", required=True)
    diagnose = sub.add_parser("diagnose")
    diagnose.add_argument("--package-root", type=Path, required=True)
    diagnose.add_argument("--exact-approval", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "materialize-current":
            receipt, approval = materialize_current(
                args.outcome_id, _parse_utc(args.expires_at)
            )
            print(canonical_json_bytes(
                {
                    "approval": approval,
                    "manifest_sha256": receipt.manifest_sha256,
                    "outcome_id": receipt.outcome_id,
                    "package_root": str(receipt.package_root),
                    "status": "materialized",
                }
            ).decode("utf-8"), end="")
            return 0
        result = (
            run_preflight_diagnosis(args.package_root, args.exact_approval)
            if args.command == "diagnose"
            else run_cutover_gate(args.package_root, args.exact_approval)
        )
        print(canonical_json_bytes(
            {
                "outcome_id": result.outcome_id,
                "receipt_path": str(result.receipt_path),
                "ssh_process_count": result.ssh_process_count,
                "status": result.status,
            }
        ).decode("utf-8"), end="")
        return 0 if result.status == "success" else 1
    except CutoverError as error:
        print(canonical_json_bytes({"reason": str(error), "status": "failure"}).decode("utf-8"), end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
