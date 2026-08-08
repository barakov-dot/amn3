#!/usr/bin/env python3
"""Checksum-bound one-SSH read-only AWG2 predicate diagnosis for Phase 13."""

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
    load_fixed_role_binding,
    run_bounded_process,
)


UTC = timezone.utc
PACKAGE_SCHEMA = "amn2.phase13.spain-awg2-predicate-diagnosis-package.v1"
PAYLOAD_SCHEMA = "amn2.phase13.spain-awg2-predicate-diagnosis-payload.v1"
CLAIM_SCHEMA = "amn2.phase13.spain-awg2-predicate-diagnosis-claim.v1"
RECEIPT_SCHEMA = "amn2.phase13.spain-awg2-predicate-diagnosis-receipt.v1"
OUTCOME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")
HEAD_PATTERN = re.compile(r"^[0-9a-f]{40}$")
MAX_ARTIFACT_BYTES = 1024 * 1024
MAX_TRANSPORT_BYTES = 1024 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
MAX_TIMEOUT_SECONDS = 60.0
FIXED_SSH_EXECUTABLE = r"C:\Windows\System32\OpenSSH\ssh.exe"
ARTIFACT_FILENAMES = {
    "foundation": "foundation.py",
    "remote": "remote.py",
    "runner": "runner.py",
}
SAFETY = {
    "awg_mutation_authorized": False,
    "bot_runtime_update_authorized": False,
    "database_apply_authorized": False,
    "foreign_mutation_authorized": False,
    "network_mutation_authorized": False,
    "service_action_authorized": False,
    "usa_access_authorized": False,
}
REMOTE_RECEIPT_KEYS = {
    "awg2_equal",
    "awg2_equal_without_restart_count",
    "configured_ip_forward_equal",
    "container_running",
    "expected_forward_rule_count",
    "expected_peer_count",
    "failed_predicates",
    "foreign_equal",
    "foreign_observed",
    "forward_comments_equal",
    "forward_rule_count",
    "forward_rule_count_equal",
    "image_present",
    "listen_port_equal",
    "live_ip_forward_equal",
    "live_peer_count",
    "live_peer_count_equal",
    "mutation_performed",
    "network_mode_equal",
    "outcome",
    "outcome_id",
    "peer_sets_equal",
    "persistent_peer_count",
    "persistent_peer_count_equal",
    "raw_output_persisted",
    "reason",
    "restart_count_current",
    "restart_count_equal",
    "restart_count_expected",
    "route_equal",
    "schema",
    "stage",
    "units_active_enabled",
}
FAILED_PREDICATE_ALLOWLIST = {
    "configured_ip_forward_equal",
    "container_running",
    "forward_comments_equal",
    "forward_rule_count_equal",
    "image_present",
    "listen_port_equal",
    "live_ip_forward_equal",
    "live_peer_count_equal",
    "network_mode_equal",
    "peer_sets_equal",
    "persistent_peer_count_equal",
    "restart_count_equal",
    "route_equal",
    "units_active_enabled",
}


class DiagnosticError(RuntimeError):
    """Secret-safe local package or runner failure."""


@dataclass(frozen=True)
class DiagnosticPackageInputs:
    outcome_id: str
    expires_at: datetime
    tooling_head: str
    runner_bytes: bytes
    remote_bytes: bytes
    foundation_bytes: bytes


@dataclass(frozen=True)
class DiagnosticPackageReceipt:
    package_root: Path
    manifest_sha256: str
    outcome_id: str


@dataclass(frozen=True)
class DiagnosticBinding:
    package_root: Path
    outcome_id: str
    expires_at: datetime
    tooling_head: str
    manifest_sha256: str
    artifact_sha256: tuple[tuple[str, str], ...]
    runner_sha256: str
    remote_sha256: str
    foundation_sha256: str
    safety: Mapping[str, bool]


@dataclass(frozen=True)
class FixedSpainBinding:
    target_host: str
    target_user: str
    key_path: Path
    known_hosts_path: Path


@dataclass(frozen=True)
class DiagnosticRunReceipt:
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
        raise DiagnosticError("timestamp invalid")
    return value.astimezone(UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_utc(value: object) -> datetime:
    if not isinstance(value, str) or re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value
    ) is None:
        raise DiagnosticError("timestamp invalid")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError as error:
        raise DiagnosticError("timestamp invalid") from error


def _canonical_object(value: bytes, label: str) -> dict[str, object]:
    try:
        document = json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DiagnosticError(f"{label} invalid") from error
    if not isinstance(document, dict) or canonical_json_bytes(document) != value:
        raise DiagnosticError(f"{label} invalid")
    return document


def _validate_inputs(inputs: DiagnosticPackageInputs) -> None:
    if (
        not isinstance(inputs, DiagnosticPackageInputs)
        or OUTCOME_PATTERN.fullmatch(inputs.outcome_id) is None
        or HEAD_PATTERN.fullmatch(inputs.tooling_head) is None
        or inputs.expires_at.tzinfo is None
    ):
        raise DiagnosticError("package inputs invalid")
    for value in (inputs.runner_bytes, inputs.remote_bytes, inputs.foundation_bytes):
        if not isinstance(value, bytes) or not value or len(value) > MAX_ARTIFACT_BYTES:
            raise DiagnosticError("package inputs invalid")


def materialize_diagnostic_package(
    inputs: DiagnosticPackageInputs, output_parent: Path
) -> DiagnosticPackageReceipt:
    _validate_inputs(inputs)
    parent = Path(output_parent)
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    package_root = parent / inputs.outcome_id
    if os.path.lexists(package_root):
        raise DiagnosticError("package root exists")
    os.mkdir(package_root, 0o700)
    artifacts = {
        "foundation": inputs.foundation_bytes,
        "remote": inputs.remote_bytes,
        "runner": inputs.runner_bytes,
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
        "artifacts": bindings,
        "created_at": _format_utc(inputs.expires_at - timedelta(hours=2)),
        "expires_at": _format_utc(inputs.expires_at),
        "max_attempts": 1,
        "outcome_id": inputs.outcome_id,
        "safety": SAFETY,
        "schema": PACKAGE_SCHEMA,
        "tooling_head": inputs.tooling_head,
    }
    manifest_bytes = canonical_json_bytes(manifest)
    (package_root / "manifest.json").write_bytes(manifest_bytes)
    return DiagnosticPackageReceipt(
        package_root=package_root,
        manifest_sha256=sha256_bytes(manifest_bytes),
        outcome_id=inputs.outcome_id,
    )


def verify_local_diagnostic_package(
    package_root: Path, *, now: datetime
) -> DiagnosticBinding:
    root = Path(package_root)
    if not root.is_dir() or root.is_symlink():
        raise DiagnosticError("package root invalid")
    expected_files = set(ARTIFACT_FILENAMES.values()) | {"manifest.json"}
    if {item.name for item in root.iterdir()} != expected_files:
        raise DiagnosticError("artifact set invalid")
    manifest_bytes = _require_regular_file(root / "manifest.json", maximum=MAX_ARTIFACT_BYTES)
    manifest = _canonical_object(manifest_bytes, "manifest")
    if set(manifest) != {
        "artifacts", "created_at", "expires_at", "max_attempts", "outcome_id",
        "safety", "schema", "tooling_head"
    }:
        raise DiagnosticError("manifest invalid")
    expires_at = _parse_utc(manifest["expires_at"])
    if now.tzinfo is None or expires_at <= now.astimezone(UTC):
        raise DiagnosticError("package expired")
    if (
        manifest.get("schema") != PACKAGE_SCHEMA
        or manifest.get("max_attempts") != 1
        or manifest.get("safety") != SAFETY
        or OUTCOME_PATTERN.fullmatch(str(manifest.get("outcome_id", ""))) is None
        or HEAD_PATTERN.fullmatch(str(manifest.get("tooling_head", ""))) is None
    ):
        raise DiagnosticError("manifest invalid")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != set(ARTIFACT_FILENAMES):
        raise DiagnosticError("artifact set invalid")
    hashes: dict[str, str] = {}
    for identifier, filename in ARTIFACT_FILENAMES.items():
        binding = artifacts.get(identifier)
        if (
            not isinstance(binding, dict)
            or set(binding) != {"filename", "sha256", "size"}
            or binding.get("filename") != filename
            or SHA_PATTERN.fullmatch(str(binding.get("sha256", ""))) is None
            or isinstance(binding.get("size"), bool)
            or not isinstance(binding.get("size"), int)
        ):
            raise DiagnosticError("artifact binding invalid")
        value = _require_regular_file(root / filename, maximum=MAX_ARTIFACT_BYTES)
        if len(value) != binding["size"] or sha256_bytes(value) != binding["sha256"]:
            raise DiagnosticError("artifact checksum mismatch")
        hashes[identifier] = str(binding["sha256"])
    return DiagnosticBinding(
        package_root=root,
        outcome_id=str(manifest["outcome_id"]),
        expires_at=expires_at,
        tooling_head=str(manifest["tooling_head"]),
        manifest_sha256=sha256_bytes(manifest_bytes),
        artifact_sha256=tuple(sorted(hashes.items())),
        runner_sha256=hashes["runner"],
        remote_sha256=hashes["remote"],
        foundation_sha256=hashes["foundation"],
        safety=dict(SAFETY),
    )


def exact_approval_phrase(binding: DiagnosticBinding) -> str:
    return (
        "УТВЕРЖДАЮ ОДИН CHECKSUM-BOUND SPAIN AWG2 PREDICATE READ-ONLY DIAGNOSIS "
        f"OUTCOME_{binding.outcome_id} MANIFEST_SHA_{binding.manifest_sha256} "
        f"RUNNER_SHA_{binding.runner_sha256} REMOTE_SHA_{binding.remote_sha256} "
        f"FOUNDATION_SHA_{binding.foundation_sha256} TOOLING_HEAD_{binding.tooling_head} "
        f"EXPIRES_AT_{_format_utc(binding.expires_at)} MAX_ATTEMPTS_1 "
        "ONE_SSH_READ_ONLY NO_SERVICE_ACTION NO_BOT_RUNTIME_UPDATE NO_DATABASE_APPLY "
        "NO_AWG_MUTATION NO_FOREIGN_MUTATION NO_USA_ACCESS"
    )


def _load_fixed_spain_binding() -> FixedSpainBinding:
    value = load_fixed_role_binding("spain")
    if not isinstance(value, FixedRoleBinding) or value.role != "spain":
        raise DiagnosticError("fixed Spain binding invalid")
    return FixedSpainBinding(
        target_host=value.target_host,
        target_user=value.target_user,
        key_path=value.key_path,
        known_hosts_path=value.known_hosts_path,
    )


def safe_success_receipt(outcome_id: str) -> dict[str, object]:
    return {
        "awg2_equal": True,
        "awg2_equal_without_restart_count": True,
        "configured_ip_forward_equal": True,
        "container_running": True,
        "expected_forward_rule_count": 3,
        "expected_peer_count": 7,
        "failed_predicates": [],
        "foreign_equal": True,
        "foreign_observed": True,
        "forward_comments_equal": True,
        "forward_rule_count": 3,
        "forward_rule_count_equal": True,
        "image_present": True,
        "listen_port_equal": True,
        "live_ip_forward_equal": True,
        "live_peer_count": 7,
        "live_peer_count_equal": True,
        "mutation_performed": False,
        "network_mode_equal": True,
        "outcome": "success",
        "outcome_id": outcome_id,
        "peer_sets_equal": True,
        "persistent_peer_count": 7,
        "persistent_peer_count_equal": True,
        "raw_output_persisted": False,
        "reason": "diagnosed",
        "restart_count_current": 59,
        "restart_count_equal": True,
        "restart_count_expected": 59,
        "route_equal": True,
        "schema": RECEIPT_SCHEMA,
        "stage": "complete",
        "units_active_enabled": True,
    }


def _parse_remote_receipt(value: bytes, outcome_id: str) -> dict[str, object]:
    receipt = _canonical_object(value, "remote receipt")
    failed = receipt.get("failed_predicates")
    count_keys = {
        "expected_forward_rule_count", "expected_peer_count", "forward_rule_count",
        "live_peer_count", "persistent_peer_count", "restart_count_current",
        "restart_count_expected",
    }
    boolean_keys = REMOTE_RECEIPT_KEYS - count_keys - {
        "failed_predicates", "outcome", "outcome_id", "reason", "schema", "stage"
    }
    reason_allowlist = {
        "diagnosed", "diagnosed_foreign_unavailable", "foundation_invalid", "foreign_observation_failed",
        "internal_failure", "observation_failed", "observation_invalid",
        "payload_invalid",
    }
    stage_allowlist = {
        "complete", "foreign", "foundation", "internal", "observation", "payload"
    }
    if (
        set(receipt) != REMOTE_RECEIPT_KEYS
        or receipt.get("schema") != RECEIPT_SCHEMA
        or receipt.get("outcome_id") != outcome_id
        or receipt.get("outcome") not in {"success", "failure"}
        or receipt.get("raw_output_persisted") is not False
        or receipt.get("mutation_performed") is not False
        or not isinstance(failed, list)
        or any(not isinstance(item, str) or item not in FAILED_PREDICATE_ALLOWLIST for item in failed)
        or failed != sorted(set(failed))
        or any(
            isinstance(receipt.get(key), bool) or not isinstance(receipt.get(key), int)
            for key in count_keys
        )
        or any(not isinstance(receipt.get(key), bool) for key in boolean_keys)
        or receipt.get("reason") not in reason_allowlist
        or receipt.get("stage") not in stage_allowlist
    ):
        raise DiagnosticError("remote receipt invalid")
    return receipt


def run_diagnostic_gate(
    package_root: Path,
    exact_approval: str,
    *,
    process_runner: Callable[..., bytes] = run_bounded_process,
    binding_loader: Callable[[], FixedSpainBinding] = _load_fixed_spain_binding,
    private_root: Path | None = None,
    now: datetime | None = None,
) -> DiagnosticRunReceipt:
    checked_at = now or datetime.now(UTC)
    binding = verify_local_diagnostic_package(package_root, now=checked_at)
    if exact_approval != exact_approval_phrase(binding):
        raise DiagnosticError("exact approval mismatch")
    if process_runner is run_bounded_process:
        if sha256_bytes(Path(__file__).read_bytes()) != binding.runner_sha256:
            raise DiagnosticError("runner source mismatch")
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        if head != binding.tooling_head:
            raise DiagnosticError("exact head mismatch")
    root = private_root or (
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "AMN2/private-state/phase13-bot-web-migration/awg2-diagnosis"
    )
    _create_private_directory(root)
    outcomes = root / "outcomes"
    receipts = root / "receipts"
    _create_private_directory(outcomes)
    _create_private_directory(receipts)
    claim_path = outcomes / f"{binding.outcome_id}.claim.json"
    _write_create_new(
        claim_path,
        canonical_json_bytes({
            "manifest_sha256": binding.manifest_sha256,
            "outcome_id": binding.outcome_id,
            "schema": CLAIM_SCHEMA,
        }),
        private=True,
    )
    ssh_process_count = 0
    try:
        remote_bytes = _require_regular_file(binding.package_root / "remote.py", maximum=MAX_ARTIFACT_BYTES)
        foundation_bytes = _require_regular_file(binding.package_root / "foundation.py", maximum=MAX_ARTIFACT_BYTES)
        payload_bytes = canonical_json_bytes({
            "expires_at": _format_utc(binding.expires_at),
            "max_attempts": 1,
            "outcome_id": binding.outcome_id,
            "schema": PAYLOAD_SCHEMA,
        })
        bound = {
            "foundation_b64": base64.b64encode(foundation_bytes).decode("ascii"),
            "foundation_sha256": sha256_bytes(foundation_bytes),
            "payload_b64": base64.b64encode(payload_bytes).decode("ascii"),
            "payload_sha256": sha256_bytes(payload_bytes),
        }
        envelope = canonical_json_bytes({
            "bound": bound,
            "remote_b64": base64.b64encode(remote_bytes).decode("ascii"),
            "remote_sha256": sha256_bytes(remote_bytes),
        })
        if len(envelope) > MAX_TRANSPORT_BYTES:
            raise DiagnosticError("transport input oversized")
        bootstrap = (
            'import base64,hashlib,json,sys;e=json.load(sys.stdin);'
            's=base64.b64decode(e["remote_b64"],validate=True);'
            'hashlib.sha256(s).hexdigest()==e["remote_sha256"] or sys.exit(70);'
            'g={"__name__":"phase13_bound_spain_awg2_diagnosis"};'
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
            FIXED_SSH_EXECUTABLE,
            arguments,
            envelope,
            timeout_seconds=MAX_TIMEOUT_SECONDS,
            maximum_input_bytes=MAX_TRANSPORT_BYTES,
            maximum_output_bytes=MAX_OUTPUT_BYTES,
        )
        receipt = _parse_remote_receipt(output, binding.outcome_id)
        receipt_path = receipts / f"{binding.outcome_id}.{receipt['outcome']}.json"
        _write_create_new(receipt_path, canonical_json_bytes(receipt), private=True)
        return DiagnosticRunReceipt(
            status=str(receipt["outcome"]),
            outcome_id=binding.outcome_id,
            ssh_process_count=ssh_process_count,
            receipt_path=receipt_path,
        )
    except DiagnosticError:
        raise
    except Exception as error:
        failure_path = receipts / f"{binding.outcome_id}.failure.json"
        failure = {
            "outcome": "failure",
            "outcome_id": binding.outcome_id,
            "raw_output_persisted": False,
            "reason": "transport_or_remote_failure",
            "schema": "amn2.phase13.spain-awg2-predicate-diagnosis-local-failure.v1",
            "ssh_process_count": ssh_process_count,
        }
        try:
            _write_create_new(failure_path, canonical_json_bytes(failure), private=True)
        except Exception:
            pass
        raise DiagnosticError("diagnosis failed") from error


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=True, capture_output=True, text=True
    ).stdout


def materialize_current_gate(
    *, outcome_id: str, expires_at: datetime
) -> tuple[DiagnosticPackageReceipt, str]:
    root = Path(__file__).resolve().parents[1]
    tooling_head = _git(root, "rev-parse", "HEAD").strip()
    tracked = _git(root, "status", "--porcelain", "--untracked-files=no")
    if HEAD_PATTERN.fullmatch(tooling_head) is None or tracked:
        raise DiagnosticError("tooling worktree invalid")
    inputs = DiagnosticPackageInputs(
        outcome_id=outcome_id,
        expires_at=expires_at,
        tooling_head=tooling_head,
        runner_bytes=Path(__file__).read_bytes(),
        remote_bytes=(root / "scripts/vps/phase13_spain_awg2_predicate_diagnosis_remote.py").read_bytes(),
        foundation_bytes=(root / "scripts/vps/phase13_bot_web_migration_production_stage_remote.py").read_bytes(),
    )
    parent = (
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "AMN2/private-artifacts/phase13-bot-web-migration/awg2-diagnosis-packages"
    )
    package = materialize_diagnostic_package(inputs, parent)
    binding = verify_local_diagnostic_package(package.package_root, now=datetime.now(UTC))
    return package, exact_approval_phrase(binding)


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
        package, approval = materialize_current_gate(
            outcome_id=args.outcome_id, expires_at=_parse_utc(args.expires_at)
        )
        binding = verify_local_diagnostic_package(package.package_root, now=datetime.now(UTC))
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
        binding = verify_local_diagnostic_package(args.package_root, now=datetime.now(UTC))
        print(canonical_json_bytes({
            "artifact_count": len(binding.artifact_sha256),
            "manifest_sha256": binding.manifest_sha256,
            "outcome_id": binding.outcome_id,
            "status": "verified",
        }).decode("utf-8"), end="")
        return 0
    receipt = run_diagnostic_gate(args.package_root, args.exact_approval)
    print(canonical_json_bytes({
        "outcome_id": receipt.outcome_id,
        "ssh_process_count": receipt.ssh_process_count,
        "status": receipt.status,
    }).decode("utf-8"), end="")
    return 0 if receipt.status == "success" else 75


if __name__ == "__main__":
    raise SystemExit(main())
