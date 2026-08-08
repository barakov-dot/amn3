#!/usr/bin/env python3
"""Checksum-bound USA bot-media read-only collection gate for Phase 13."""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from types import ModuleType
from typing import Callable, Mapping

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.phase13_bot_web_migration_fresh_inputs import (
    FixedRoleBinding,
    load_fixed_role_binding,
    run_bounded_process,
)


UTC = timezone.utc
SCHEMA = "amn2.phase13.bot-media-readonly-package.v1"
CLAIM_SCHEMA = "amn2.phase13.bot-media-readonly-claim.v1"
RECEIPT_SCHEMA = "amn2.phase13.bot-media-readonly-receipt.v1"
OUTCOME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")
HEAD_PATTERN = re.compile(r"^[0-9a-f]{40}$")
ARTIFACT_FILENAMES = {
    "collector": "collector.py",
    "recovery_crypto": "recovery_crypto.py",
    "runner": "runner.py",
}
SAFETY = {
    "backup_created": False,
    "data_transfer_authorized": False,
    "live_mutation_authorized": False,
    "plaintext_persistence_authorized": False,
    "service_action_authorized": False,
    "spain_access_authorized": False,
}
MAX_PACKAGE_ARTIFACT_BYTES = 4 * 1024 * 1024
MAX_TRANSPORT_INPUT_BYTES = 1024 * 1024
MAX_TRANSPORT_OUTPUT_BYTES = 64 * 1024 * 1024
MAX_TRANSPORT_TIMEOUT_SECONDS = 60.0
FIXED_SSH_EXECUTABLE = r"C:\Windows\System32\OpenSSH\ssh.exe"


class BotMediaGateError(RuntimeError):
    """A secret-safe bot-media package or runtime failure."""


@dataclass(frozen=True)
class BotMediaPackageInputs:
    outcome_id: str
    expires_at: datetime
    root_head: str
    runner_bytes: bytes
    collector_bytes: bytes
    recovery_crypto_bytes: bytes


@dataclass(frozen=True)
class BotMediaPackageReceipt:
    package_root: Path
    manifest_sha256: str
    outcome_id: str


@dataclass(frozen=True)
class BotMediaBinding:
    package_root: Path
    outcome_id: str
    expires_at: datetime
    max_attempts: int
    root_head: str
    manifest_sha256: str
    runner_sha256: str
    collector_sha256: str
    recovery_crypto_sha256: str


@dataclass(frozen=True)
class FixedUsaBinding:
    target_host: str
    target_user: str
    key_path: Path
    known_hosts_path: Path


@dataclass(frozen=True)
class BotMediaRunReceipt:
    status: str
    outcome_id: str
    ssh_process_count: int
    remote_collection_completed: bool
    plaintext_persisted: bool
    registry_present: bool
    media_root_present: bool
    file_count: int
    total_bytes: int
    encrypted_archive_path: Path | None
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
        raise BotMediaGateError("timestamp invalid")
    return value.astimezone(UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_utc(value: object) -> datetime:
    if not isinstance(value, str) or re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value
    ) is None:
        raise BotMediaGateError("timestamp invalid")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError as error:
        raise BotMediaGateError("timestamp invalid") from error
    if _format_utc(parsed) != value:
        raise BotMediaGateError("timestamp invalid")
    return parsed


def _is_reparse_point(metadata: os.stat_result) -> bool:
    return bool(getattr(metadata, "st_file_attributes", 0) & 0x400)


def _require_safe_directory(path: Path) -> None:
    try:
        metadata = os.lstat(path)
    except OSError as error:
        raise BotMediaGateError("private directory unavailable") from error
    if (
        stat.S_ISLNK(metadata.st_mode)
        or _is_reparse_point(metadata)
        or not stat.S_ISDIR(metadata.st_mode)
    ):
        raise BotMediaGateError("private directory unsafe")


def _require_regular_file(path: Path, *, maximum: int = MAX_PACKAGE_ARTIFACT_BYTES) -> bytes:
    try:
        metadata = os.lstat(path)
    except OSError as error:
        raise BotMediaGateError("package artifact unavailable") from error
    if (
        stat.S_ISLNK(metadata.st_mode)
        or _is_reparse_point(metadata)
        or not stat.S_ISREG(metadata.st_mode)
        or metadata.st_size < 1
        or metadata.st_size > maximum
    ):
        raise BotMediaGateError("package artifact unsafe")
    try:
        value = path.read_bytes()
    except OSError as error:
        raise BotMediaGateError("package artifact unavailable") from error
    if len(value) != metadata.st_size:
        raise BotMediaGateError("package artifact changed")
    return value


def _protect_current_user_only_acl(path: Path, *, directory: bool) -> None:
    if os.name != "nt":
        os.chmod(path, 0o700 if directory else 0o600)
        return
    inheritance = (
        "[Security.AccessControl.InheritanceFlags]::ContainerInherit -bor "
        "[Security.AccessControl.InheritanceFlags]::ObjectInherit"
        if directory
        else "[Security.AccessControl.InheritanceFlags]::None"
    )
    script = (
        "$ErrorActionPreference='Stop';$p=$env:AMN2_BOT_MEDIA_ACL_PATH;"
        "$sid=[Security.Principal.WindowsIdentity]::GetCurrent().User;"
        "$info=if([IO.Directory]::Exists($p)){New-Object IO.DirectoryInfo($p)}"
        "else{New-Object IO.FileInfo($p)};"
        "$acl=$info.GetAccessControl();$acl.SetOwner($sid);"
        "$acl.SetAccessRuleProtection($true,$false);"
        "foreach($r in @($acl.Access)){[void]$acl.RemoveAccessRuleAll($r)};"
        f"$inheritance={inheritance};"
        "$rule=New-Object Security.AccessControl.FileSystemAccessRule("
        "$sid,[Security.AccessControl.FileSystemRights]::FullControl,$inheritance,"
        "[Security.AccessControl.PropagationFlags]::None,"
        "[Security.AccessControl.AccessControlType]::Allow);"
        "[void]$acl.AddAccessRule($rule);$info.SetAccessControl($acl)"
    )
    environment = os.environ.copy()
    environment["AMN2_BOT_MEDIA_ACL_PATH"] = str(path)
    try:
        result = subprocess.run(
            (
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                script,
            ),
            check=False,
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise BotMediaGateError("private ACL protection failed") from error
    if result.returncode != 0:
        raise BotMediaGateError("private ACL protection failed")


def _assert_current_user_only_acl(path: Path) -> None:
    if os.name != "nt":
        if stat.S_IMODE(os.lstat(path).st_mode) & 0o077:
            raise BotMediaGateError("private ACL invalid")
        return
    script = (
        "$ErrorActionPreference='Stop';$p=$env:AMN2_BOT_MEDIA_ACL_PATH;"
        "$sid=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value;"
        "$attrs=[IO.File]::GetAttributes($p);"
        "if(($attrs-band[IO.FileAttributes]::ReparsePoint)-ne 0){exit 3};"
        "$info=if([IO.Directory]::Exists($p)){New-Object IO.DirectoryInfo($p)}"
        "else{New-Object IO.FileInfo($p)};"
        "$a=$info.GetAccessControl();$owner=$a.Owner;"
        "try{$owner=([Security.Principal.NTAccount]$a.Owner).Translate("
        "[Security.Principal.SecurityIdentifier]).Value}catch{};"
        "if($owner-cne$sid-or-not$a.AreAccessRulesProtected){exit 4};"
        "foreach($r in $a.Access){$rs=$r.IdentityReference.Value;"
        "try{$rs=$r.IdentityReference.Translate("
        "[Security.Principal.SecurityIdentifier]).Value}catch{};"
        "if($r.IsInherited-or($r.AccessControlType-eq'Allow'-and$rs-cne$sid)){exit 5}}"
    )
    environment = os.environ.copy()
    environment["AMN2_BOT_MEDIA_ACL_PATH"] = str(path)
    try:
        result = subprocess.run(
            (
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                script,
            ),
            check=False,
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise BotMediaGateError("private ACL invalid") from error
    if result.returncode != 0:
        raise BotMediaGateError("private ACL invalid")


def _create_private_directory(path: Path) -> None:
    if os.path.lexists(path):
        _require_safe_directory(path)
        _assert_current_user_only_acl(path)
        return
    try:
        os.mkdir(path, 0o700)
        _protect_current_user_only_acl(path, directory=True)
        _assert_current_user_only_acl(path)
    except (OSError, BotMediaGateError) as error:
        raise BotMediaGateError("private directory creation failed") from error


def _write_create_new(path: Path, value: bytes, *, private: bool = True) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                descriptor = -1
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
            if private:
                _protect_current_user_only_acl(path, directory=False)
        finally:
            if descriptor >= 0:
                os.close(descriptor)
    except (OSError, BotMediaGateError) as error:
        raise BotMediaGateError("create-new write failed") from error


def _validate_inputs(inputs: BotMediaPackageInputs) -> None:
    if (
        not isinstance(inputs, BotMediaPackageInputs)
        or OUTCOME_PATTERN.fullmatch(inputs.outcome_id) is None
        or HEAD_PATTERN.fullmatch(inputs.root_head) is None
        or inputs.expires_at.tzinfo is None
    ):
        raise BotMediaGateError("package inputs invalid")
    for value in (
        inputs.runner_bytes,
        inputs.collector_bytes,
        inputs.recovery_crypto_bytes,
    ):
        if not isinstance(value, bytes) or not value or len(value) > MAX_PACKAGE_ARTIFACT_BYTES:
            raise BotMediaGateError("package inputs invalid")


def materialize_bot_media_package(
    inputs: BotMediaPackageInputs, output_parent: Path
) -> BotMediaPackageReceipt:
    _validate_inputs(inputs)
    parent = Path(output_parent)
    if not os.path.lexists(parent):
        try:
            parent.mkdir(parents=True)
        except OSError as error:
            raise BotMediaGateError("package parent unavailable") from error
    _require_safe_directory(parent)
    package_root = parent / inputs.outcome_id
    if os.path.lexists(package_root):
        raise BotMediaGateError("package root already exists")
    try:
        os.mkdir(package_root, 0o700)
        artifacts = {
            "runner": inputs.runner_bytes,
            "collector": inputs.collector_bytes,
            "recovery_crypto": inputs.recovery_crypto_bytes,
        }
        artifact_bindings: dict[str, dict[str, object]] = {}
        for identifier in sorted(artifacts):
            filename = ARTIFACT_FILENAMES[identifier]
            value = artifacts[identifier]
            _write_create_new(package_root / filename, value, private=False)
            artifact_bindings[identifier] = {
                "filename": filename,
                "sha256": sha256_bytes(value),
                "size": len(value),
            }
        manifest = {
            "artifacts": artifact_bindings,
            "expires_at": _format_utc(inputs.expires_at),
            "max_attempts": 1,
            "outcome_id": inputs.outcome_id,
            "root_head": inputs.root_head,
            "safety": SAFETY,
            "schema": SCHEMA,
        }
        manifest_bytes = canonical_json_bytes(manifest)
        _write_create_new(package_root / "manifest.json", manifest_bytes, private=False)
        binding = verify_local_bot_media_package(
            package_root,
            now=inputs.expires_at - __import__("datetime").timedelta(seconds=1),
        )
        return BotMediaPackageReceipt(
            package_root=package_root,
            manifest_sha256=binding.manifest_sha256,
            outcome_id=inputs.outcome_id,
        )
    except Exception:
        if os.path.lexists(package_root):
            for child in package_root.iterdir():
                if child.is_file() and not child.is_symlink():
                    child.unlink()
            package_root.rmdir()
        raise


def verify_local_bot_media_package(
    package_root: Path, *, now: datetime | None = None
) -> BotMediaBinding:
    root = Path(package_root)
    _require_safe_directory(root)
    if {path.name for path in root.iterdir()} != {
        "collector.py",
        "manifest.json",
        "recovery_crypto.py",
        "runner.py",
    }:
        raise BotMediaGateError("package artifact set invalid")
    manifest_bytes = _require_regular_file(root / "manifest.json")
    try:
        manifest = json.loads(manifest_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BotMediaGateError("manifest invalid") from error
    required = {
        "artifacts",
        "expires_at",
        "max_attempts",
        "outcome_id",
        "root_head",
        "safety",
        "schema",
    }
    if (
        not isinstance(manifest, dict)
        or set(manifest) != required
        or canonical_json_bytes(manifest) != manifest_bytes
        or manifest.get("schema") != SCHEMA
        or OUTCOME_PATTERN.fullmatch(str(manifest.get("outcome_id", ""))) is None
        or HEAD_PATTERN.fullmatch(str(manifest.get("root_head", ""))) is None
        or manifest.get("max_attempts") != 1
        or manifest.get("safety") != SAFETY
        or not isinstance(manifest.get("artifacts"), dict)
        or set(manifest["artifacts"]) != set(ARTIFACT_FILENAMES)
    ):
        raise BotMediaGateError("manifest invalid")
    expires_at = _parse_utc(manifest["expires_at"])
    checked_at = (now or datetime.now(UTC)).astimezone(UTC)
    if checked_at >= expires_at:
        raise BotMediaGateError("manifest expired")
    hashes: dict[str, str] = {}
    for identifier, filename in ARTIFACT_FILENAMES.items():
        binding = manifest["artifacts"].get(identifier)
        if (
            not isinstance(binding, dict)
            or set(binding) != {"filename", "sha256", "size"}
            or binding.get("filename") != filename
            or SHA_PATTERN.fullmatch(str(binding.get("sha256", ""))) is None
            or not isinstance(binding.get("size"), int)
            or binding["size"] < 1
            or binding["size"] > MAX_PACKAGE_ARTIFACT_BYTES
        ):
            raise BotMediaGateError("artifact binding invalid")
        value = _require_regular_file(root / filename)
        if len(value) != binding["size"] or sha256_bytes(value) != binding["sha256"]:
            raise BotMediaGateError("artifact checksum mismatch")
        hashes[identifier] = binding["sha256"]
    return BotMediaBinding(
        package_root=root,
        outcome_id=manifest["outcome_id"],
        expires_at=expires_at,
        max_attempts=1,
        root_head=manifest["root_head"],
        manifest_sha256=sha256_bytes(manifest_bytes),
        runner_sha256=hashes["runner"],
        collector_sha256=hashes["collector"],
        recovery_crypto_sha256=hashes["recovery_crypto"],
    )


def exact_approval_phrase(binding: BotMediaBinding) -> str:
    return (
        "УТВЕРЖДАЮ ОДИН CHECKSUM-BOUND USA BOT-MEDIA READ-ONLY COLLECTION "
        f"OUTCOME_{binding.outcome_id} MANIFEST_SHA_{binding.manifest_sha256} "
        f"RUNNER_SHA_{binding.runner_sha256} COLLECTOR_SHA_{binding.collector_sha256} "
        f"CRYPTO_SHA_{binding.recovery_crypto_sha256} "
        f"EXPIRES_AT_{_format_utc(binding.expires_at)} MAX_ATTEMPTS_1 "
        "ONE_SSH_NO_MUTATION_NO_PLAINTEXT"
    )


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BotMediaGateError("bound module unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        sys.modules.pop(name, None)
        raise BotMediaGateError("bound module unavailable") from error
    return module


def _load_fixed_usa_binding() -> FixedUsaBinding:
    value = load_fixed_role_binding("usa")
    if not isinstance(value, FixedRoleBinding) or value.role != "usa":
        raise BotMediaGateError("fixed USA binding invalid")
    return FixedUsaBinding(
        target_host=value.target_host,
        target_user=value.target_user,
        key_path=value.key_path,
        known_hosts_path=value.known_hosts_path,
    )


def _create_external_keypair(key_root: Path, *, artifact_root: Path) -> tuple[Path, bytes]:
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
    except ImportError as error:
        raise BotMediaGateError("recovery crypto unavailable") from error
    if os.path.lexists(key_root) or artifact_root == key_root or artifact_root in key_root.parents:
        raise BotMediaGateError("external key root invalid")
    _create_private_directory(key_root)
    try:
        key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
        private = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        public = key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        private_path = key_root / "recovery-private.pem"
        _write_create_new(private_path, private, private=True)
        return private_path, public
    except Exception as error:
        raise BotMediaGateError("external key creation failed") from error


def _write_sanitized_receipt(
    result_root: Path,
    *,
    binding: BotMediaBinding,
    status: str,
    ssh_process_count: int,
    evidence: Mapping[str, object] | None,
    encrypted_sha256: str | None,
    reason: str,
) -> Path:
    receipt = {
        "checked_at": _format_utc(datetime.now(UTC)),
        "encrypted_archive_sha256": encrypted_sha256,
        "evidence": dict(evidence or {}),
        "live_mutation": False,
        "outcome_id": binding.outcome_id,
        "plaintext_persisted": False,
        "reason": reason,
        "remote_collection_completed": status == "success",
        "schema": RECEIPT_SCHEMA,
        "spain_accessed": False,
        "ssh_process_count": ssh_process_count,
        "status": status,
    }
    path = result_root / f"{binding.outcome_id}.{status}.json"
    _write_create_new(path, canonical_json_bytes(receipt), private=True)
    return path


def run_bot_media_gate(
    package_root: Path,
    exact_approval: str,
    *,
    now: datetime | None = None,
    private_root: Path | None = None,
    process_runner: Callable[..., bytes] = run_bounded_process,
    binding_loader: Callable[[], FixedUsaBinding] = _load_fixed_usa_binding,
) -> BotMediaRunReceipt:
    checked_at = (now or datetime.now(UTC)).astimezone(UTC)
    binding = verify_local_bot_media_package(package_root, now=checked_at)
    if exact_approval != exact_approval_phrase(binding):
        raise BotMediaGateError("exact approval mismatch")
    try:
        current_runner = Path(__file__).read_bytes()
    except OSError as error:
        raise BotMediaGateError("runner source unavailable") from error
    if sha256_bytes(current_runner) != binding.runner_sha256:
        raise BotMediaGateError("runner source mismatch")
    if _current_head() != binding.root_head:
        raise BotMediaGateError("exact head mismatch")

    root = Path(private_root) if private_root is not None else Path(
        os.environ.get("LOCALAPPDATA", "")
    ) / "AMN2/private-artifacts/phase13-bot-web-migration/bot-media-check"
    if not str(root):
        raise BotMediaGateError("private root unavailable")
    _create_private_directory(root)
    outcomes = root / "outcomes"
    keys = root / "keys"
    results = root / "results"
    for directory in (outcomes, keys, results):
        _create_private_directory(directory)
    claim_path = outcomes / f"{binding.outcome_id}.claim.json"
    claim = {
        "collector_sha256": binding.collector_sha256,
        "expires_at": _format_utc(binding.expires_at),
        "manifest_sha256": binding.manifest_sha256,
        "outcome_id": binding.outcome_id,
        "schema": CLAIM_SCHEMA,
    }
    _write_create_new(claim_path, canonical_json_bytes(claim), private=True)

    result_root = results / binding.outcome_id
    key_root = keys / binding.outcome_id
    _create_private_directory(result_root)
    _private_key_path, public_key = _create_external_keypair(
        key_root, artifact_root=result_root
    )
    remote_module = _load_module(
        binding.package_root / "collector.py",
        f"phase13_bot_media_collector_{binding.outcome_id.replace('-', '_')}",
    )
    crypto_module = _load_module(
        binding.package_root / "recovery_crypto.py",
        f"phase13_bot_media_crypto_{binding.outcome_id.replace('-', '_')}",
    )
    if not callable(getattr(remote_module, "parse_media_frame", None)) or not callable(
        getattr(crypto_module, "encrypt_hybrid", None)
    ):
        raise BotMediaGateError("bound module contract invalid")
    collector_bytes = _require_regular_file(binding.package_root / "collector.py")
    envelope = canonical_json_bytes(
        {
            "collector_b64": base64.b64encode(collector_bytes).decode("ascii"),
            "collector_sha256": binding.collector_sha256,
        }
    )
    if len(envelope) > MAX_TRANSPORT_INPUT_BYTES:
        raise BotMediaGateError("transport input oversized")
    usa = binding_loader()
    if not isinstance(usa, FixedUsaBinding):
        raise BotMediaGateError("fixed USA binding invalid")
    bootstrap = (
        'import base64,hashlib,json,sys;e=json.load(sys.stdin);'
        's=base64.b64decode(e["collector_b64"],validate=True);'
        'hashlib.sha256(s).hexdigest()==e["collector_sha256"] or sys.exit(70);'
        'exec(compile(s,"<collector>","exec"),{"__name__":"__main__"})'
    )
    arguments = (
        "-T",
        "-F",
        "none",
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=yes",
        "-o",
        f"UserKnownHostsFile={usa.known_hosts_path}",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "ConnectionAttempts=1",
        "-o",
        "ServerAliveInterval=5",
        "-o",
        "ServerAliveCountMax=1",
        "-i",
        str(usa.key_path),
        "-p",
        "22",
        f"{usa.target_user}@{usa.target_host}",
        f"python3 -c '{bootstrap}'",
    )
    frame_buffer = bytearray()
    archive_buffer = bytearray()
    ssh_process_count = 0
    try:
        ssh_process_count = 1
        frame = process_runner(
            FIXED_SSH_EXECUTABLE,
            arguments,
            envelope,
            timeout_seconds=MAX_TRANSPORT_TIMEOUT_SECONDS,
            maximum_input_bytes=MAX_TRANSPORT_INPUT_BYTES,
            maximum_output_bytes=MAX_TRANSPORT_OUTPUT_BYTES,
        )
        if not isinstance(frame, bytes):
            raise BotMediaGateError("transport frame invalid")
        frame_buffer.extend(frame)
        parsed = remote_module.parse_media_frame(bytes(frame_buffer))
        archive_buffer.extend(parsed.archive)
        encrypted = crypto_module.encrypt_hybrid(bytes(archive_buffer), public_key)
        encrypted_path = result_root / "bot-media.tar.gz.enc"
        _write_create_new(encrypted_path, encrypted, private=True)
        sanitized_evidence = {
            "file_count": int(parsed.evidence["file_count"]),
            "media_root_present": bool(parsed.evidence["media_root_present"]),
            "registry_present": bool(parsed.evidence["registry_present"]),
            "total_bytes": int(parsed.evidence["total_bytes"]),
        }
        receipt_path = _write_sanitized_receipt(
            result_root,
            binding=binding,
            status="success",
            ssh_process_count=ssh_process_count,
            evidence=sanitized_evidence,
            encrypted_sha256=sha256_bytes(encrypted),
            reason="completed",
        )
        return BotMediaRunReceipt(
            status="success",
            outcome_id=binding.outcome_id,
            ssh_process_count=ssh_process_count,
            remote_collection_completed=True,
            plaintext_persisted=False,
            registry_present=sanitized_evidence["registry_present"],
            media_root_present=sanitized_evidence["media_root_present"],
            file_count=sanitized_evidence["file_count"],
            total_bytes=sanitized_evidence["total_bytes"],
            encrypted_archive_path=encrypted_path,
            receipt_path=receipt_path,
        )
    except BotMediaGateError:
        raise
    except Exception as error:
        try:
            _write_sanitized_receipt(
                result_root,
                binding=binding,
                status="failure",
                ssh_process_count=ssh_process_count,
                evidence=None,
                encrypted_sha256=None,
                reason="collection_failed",
            )
        except BotMediaGateError:
            pass
        raise BotMediaGateError("bot-media collection failed") from error
    finally:
        for buffer in (frame_buffer, archive_buffer):
            for index in range(len(buffer)):
                buffer[index] = 0


def _current_head() -> str:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ("git", "-C", str(root), "rev-parse", "HEAD"),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        timeout=10,
    )
    value = result.stdout.strip().lower()
    if result.returncode != 0 or HEAD_PATTERN.fullmatch(value) is None:
        raise BotMediaGateError("git head unavailable")
    return value


def _default_package_parent() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        raise BotMediaGateError("local app data unavailable")
    return Path(local) / "AMN2/private-artifacts/phase13-bot-web-migration/bot-media-packages"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    materialize = subparsers.add_parser("materialize")
    materialize.add_argument("--outcome-id", required=True)
    materialize.add_argument("--expires-at", required=True)
    materialize.add_argument("--output-parent", type=Path, default=None)
    verify = subparsers.add_parser("verify-local")
    verify.add_argument("--package-root", type=Path, required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--package-root", type=Path, required=True)
    run.add_argument("--exact-approval", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "materialize":
            inputs = BotMediaPackageInputs(
                outcome_id=args.outcome_id,
                expires_at=_parse_utc(args.expires_at),
                root_head=_current_head(),
                runner_bytes=Path(__file__).read_bytes(),
                collector_bytes=(
                    Path(__file__).parent
                    / "vps/phase13_bot_media_readonly_remote.py"
                ).read_bytes(),
                recovery_crypto_bytes=(
                    Path(__file__).parent / "phase10_recovery_crypto.py"
                ).read_bytes(),
            )
            receipt = materialize_bot_media_package(
                inputs, args.output_parent or _default_package_parent()
            )
            binding = verify_local_bot_media_package(receipt.package_root)
            print(
                json.dumps(
                    {
                        "approval": exact_approval_phrase(binding),
                        "manifest_sha256": binding.manifest_sha256,
                        "outcome_id": binding.outcome_id,
                        "package_root": str(binding.package_root),
                        "status": "materialized",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
        elif args.command == "verify-local":
            binding = verify_local_bot_media_package(args.package_root)
            print(
                json.dumps(
                    {
                        "manifest_sha256": binding.manifest_sha256,
                        "outcome_id": binding.outcome_id,
                        "status": "verified",
                    },
                    sort_keys=True,
                )
            )
        else:
            receipt = run_bot_media_gate(args.package_root, args.exact_approval)
            print(
                json.dumps(
                    {
                        "file_count": receipt.file_count,
                        "media_root_present": receipt.media_root_present,
                        "outcome_id": receipt.outcome_id,
                        "registry_present": receipt.registry_present,
                        "remote_collection_completed": receipt.remote_collection_completed,
                        "ssh_process_count": receipt.ssh_process_count,
                        "status": receipt.status,
                        "total_bytes": receipt.total_bytes,
                    },
                    sort_keys=True,
                )
            )
        return 0
    except (BotMediaGateError, OSError, ValueError):
        print('{"status":"failed"}')
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
