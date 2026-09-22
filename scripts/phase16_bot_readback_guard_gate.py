"""Offline preview by default; one exact synthetic Linux guard attempt if approved."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.phase16_bot_linux_gate import run_transport, ssh_environment
from scripts.vps import phase16_bot_integration_readback as core
from scripts.vps import phase16_bot_readback_guard_remote as remote

MANIFEST_RELATIVE = Path("research/amn2/phase16-bot-readback-guard-gate-manifest-2026-09-22.json")
EVIDENCE_DIRECTORY = Path(
    "C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/"
    "phase16-bot-readback-guard-runner-20260922/execution-001"
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(path):
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    compile(data, str(path), "exec")
    return data


def manifest_bytes(root=ROOT):
    return (Path(root) / MANIFEST_RELATIVE).read_bytes().replace(b"\r\n", b"\n")


def manifest_sha(root=ROOT):
    return sha(manifest_bytes(root))


def gate_manifest(root=ROOT):
    try:
        value = json.loads(manifest_bytes(root))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise core.Stop("manifest_binding") from None
    core.require(isinstance(value, dict), "manifest_binding")
    return value


def build_payload(root=ROOT):
    root = Path(root)
    core_data = canonical(root / "scripts/vps" / remote.CORE_NAME)
    smoke_data = canonical(root / "scripts/vps" / remote.SMOKE_NAME)
    payload = remote.MAGIC + f"{len(core_data):08d}{len(smoke_data):08d}".encode() + core_data + smoke_data
    core.require(len(core_data) == remote.CORE_SIZE and sha(core_data) == remote.CORE_SHA256 and
                 len(smoke_data) == remote.SMOKE_SIZE and sha(smoke_data) == remote.SMOKE_SHA256 and
                 len(payload) == remote.PAYLOAD_SIZE and sha(payload) == remote.PAYLOAD_SHA256,
                 "payload_binding")
    return payload


def remote_script(root=ROOT):
    return canonical(Path(root) / "scripts/vps/phase16_bot_readback_guard_remote.py")


def validate_manifest(value, root=ROOT):
    root = Path(root)
    top = {"schema", "status", "amn3_base", "approval", "remote_destination",
           "local_evidence_directory", "target_binding_sha256", "sha256_lf", "bytes_lf",
           "limits", "synthetic_scope", "command_contract"}
    core.require(isinstance(value, dict) and set(value) == top and
                 value.get("schema") == "phase16.readback-guard-gate-manifest.v1" and
                 value.get("status") == "SYNTHETIC_GATE_READY_NOT_EXECUTED" and
                 value.get("amn3_base") == "96b3187d71df980b4d54a7cd8d3a8b0f2842c090" and
                 value.get("approval") == remote.APPROVAL and
                 value.get("remote_destination") == remote.DESTINATION and
                 value.get("local_evidence_directory") == EVIDENCE_DIRECTORY.as_posix() and
                 re.fullmatch(r"[0-9a-f]{64}", value.get("target_binding_sha256", "")),
                 "manifest_binding")
    payload = build_payload(root)
    blobs = {
        "local_runner": canonical(root / "scripts/phase16_bot_readback_guard_gate.py"),
        "remote_supervisor": remote_script(root),
        "portable_core": canonical(root / "scripts/vps" / remote.CORE_NAME),
        "synthetic_smoke": canonical(root / "scripts/vps" / remote.SMOKE_NAME),
        "payload": payload,
    }
    hashes = value.get("sha256_lf")
    sizes = value.get("bytes_lf")
    core.require(isinstance(hashes, dict) and set(hashes) == set(blobs) and
                 isinstance(sizes, dict) and set(sizes) == set(blobs) and
                 all(hashes[name] == sha(data) and sizes[name] == len(data)
                     for name, data in blobs.items()), "manifest_binding")
    core.require(value.get("limits") == {
        "ssh_attempts": 1, "remote_seconds": 45, "transport_seconds": 60,
        "combined_remote_output_bytes": 65536,
        "cleanup_signal_scope": "owned_remote_process_group_including_namespaces",
        "retry": False, "cleanup_ssh": False,
    }, "manifest_binding")
    core.require(value.get("synthetic_scope") == {
        "new_database_only": True, "private_mount_namespace": True,
        "private_network_namespace": True, "retained_after_destination_creation": True,
        "production_database": False, "production_source": False,
        "production_units": False, "service_actions": False, "telegram": False,
        "runtime_activation": False,
    }, "manifest_binding")
    core.require(value.get("command_contract") == {
        "entrypoint": "scripts/phase16_bot_readback_guard_gate.py",
        "requires_execute": True,
        "requires_approval": remote.APPROVAL,
        "requires_remote_sha256": True,
        "requires_manifest_sha256": True,
        "requires_exact_evidence_directory": True,
    }, "manifest_binding")
    return value


def file_sha(path, cap=65536):
    path = Path(path)
    try:
        metadata = path.lstat()
        core.require(stat.S_ISREG(metadata.st_mode) and not path.is_symlink() and
                     0 < metadata.st_size <= cap, "target_binding")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        try:
            current = os.fstat(descriptor)
            core.require((current.st_dev, current.st_ino, current.st_size) ==
                         (metadata.st_dev, metadata.st_ino, metadata.st_size), "target_binding")
            with os.fdopen(descriptor, "rb", closefd=False) as stream:
                data = stream.read(cap + 1)
            core.require(len(data) == metadata.st_size, "target_binding")
        finally:
            os.close(descriptor)
    except core.Stop:
        raise
    except OSError:
        raise core.Stop("target_binding") from None
    return sha(data)


def binding_digest(binding):
    core.require(binding.role == "spain" and
                 re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.:-]{0,252}[A-Za-z0-9])?",
                              binding.target_host) and
                 re.fullmatch(r"[a-z_][a-z0-9_-]{0,31}", binding.target_user),
                 "target_binding")
    value = {
        "role": binding.role,
        "target_host": binding.target_host,
        "target_user": binding.target_user,
        "key_path": str(binding.key_path),
        "key_sha256": file_sha(binding.key_path),
        "known_hosts_path": str(binding.known_hosts_path),
        "known_hosts_sha256": file_sha(binding.known_hosts_path),
    }
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def frame_request(script, payload):
    core.require(0 < len(script) <= 65536 and len(payload) == remote.PAYLOAD_SIZE,
                 "frame_size")
    digest = sha(script)
    bootstrap = ("import hashlib,sys;"
                 "n=int(sys.stdin.buffer.read(8));"
                 "0<n<=65536 or sys.exit(70);"
                 "b=sys.stdin.buffer.read(n);"
                 f"len(b)==n and hashlib.sha256(b).hexdigest()=='{digest}' or sys.exit(70);"
                 "exec(compile(b,'<bound-phase16-readback-guard>','exec'),{'__name__':'__main__'})")
    command = "/usr/bin/python3 -I -S -B -c " + shlex.quote(bootstrap) + " " + remote.APPROVAL
    return command, f"{len(script):08d}".encode() + script + payload


def validate_cases(cases):
    core.require(isinstance(cases, list) and len(cases) == 3, "receipt_binding")
    expected = [("wal", "SHAPE_READ_WRITE_BLOCKED", {"case", "status", "table_count"}),
                ("missing_shm", "EXPECTED_STOP", {"case", "status", "reason"}),
                ("journal", "EXPECTED_STOP", {"case", "status", "reason"})]
    for item, (name, status_name, keys) in zip(cases, expected, strict=True):
        core.require(isinstance(item, dict) and set(item) == keys and
                     item.get("case") == name and item.get("status") == status_name,
                     "receipt_binding")
    remote.validate_smoke({"status": "SYNTHETIC_LINUX_GUARD_PASS",
                           "production_db_opened": False, "services_touched": False,
                           "scratch_retained": True, "cases": cases})


def validate_receipt(result, returncode):
    common = {"schema", "status", "destination", "service_actions",
              "live_database_opened", "production_source_read", "production_units_read",
              "runtime_activation", "scratch_retained", "result_persisted"}
    core.require(isinstance(result, dict) and result.get("schema") ==
                 "phase16.readback-guard-remote.v1" and
                 result.get("destination") == remote.DESTINATION and
                 result.get("service_actions") == 0 and result.get("live_database_opened") is False and
                 result.get("production_source_read") is False and
                 result.get("production_units_read") is False and
                 result.get("runtime_activation") is False, "receipt_binding")
    if result.get("status") == "SYNTHETIC_LINUX_GUARD_PASS_NOT_LIVE":
        core.require(set(result) == common | {"payload_sha256", "core_sha256", "smoke_sha256",
                                             "cases", "process", "completed_at"} and
                     returncode == 0 and result.get("payload_sha256") == remote.PAYLOAD_SHA256 and
                     result.get("core_sha256") == remote.CORE_SHA256 and
                     result.get("smoke_sha256") == remote.SMOKE_SHA256 and
                     result.get("scratch_retained") is True and
                     result.get("result_persisted") is True and
                     isinstance(result.get("completed_at"), str) and
                     isinstance(result.get("process"), dict) and
                     set(result["process"]) == {"stdout_bytes", "stderr_bytes", "stderr_present"},
                     "receipt_binding")
        validate_cases(result.get("cases"))
    else:
        core.require(set(result) == common | {"reason"} and returncode == 3 and
                     re.fullmatch(r"[a-z0-9_]{1,80}", result.get("reason", "")),
                     "receipt_binding")
        expected = {
            "STOP_BEFORE_DESTINATION_NO_RETRY": (False, False),
            "STOP_RETAINED_NO_RETRY": (True, True),
            "STOP_RETAINED_NO_RECEIPT": (True, False),
        }
        core.require(result.get("status") in expected and
                     (result.get("scratch_retained"), result.get("result_persisted")) ==
                     expected[result["status"]], "receipt_binding")
    return result


def claim_directory(path):
    path = Path(path)
    core.require(path.parent.is_dir() and not path.parent.is_symlink(), "evidence_directory")
    try:
        path.mkdir()
    except FileExistsError:
        raise core.Stop("evidence_exists") from None
    return path


def execute_once(payload, script, evidence_dir, *, approval, approved_sha, manifest,
                 approved_manifest_sha, loader, transport):
    current_manifest_sha = manifest_sha(ROOT)
    core.require(approval == remote.APPROVAL and approved_sha == sha(script) and
                 approved_manifest_sha == current_manifest_sha, "approval_binding")
    core.require(manifest == gate_manifest(ROOT), "manifest_binding")
    validate_manifest(manifest, ROOT)
    remote.parse_payload(payload)
    evidence_dir = claim_directory(evidence_dir)
    claim = {"schema": "phase16.readback-guard-claim.v1", "scope": remote.APPROVAL,
             "attempts": 1, "manifest_sha256": current_manifest_sha,
             "local_runner_sha256": manifest["sha256_lf"]["local_runner"],
             "remote_sha256": sha(script), "payload_sha256": remote.PAYLOAD_SHA256,
             "target_binding_sha256": manifest["target_binding_sha256"],
             "destination": remote.DESTINATION,
             "evidence_directory": Path(evidence_dir).as_posix(),
             "remote_seconds": 45, "transport_seconds": 60,
             "claimed_at": datetime.now(timezone.utc).isoformat()}
    (evidence_dir / "claim.json").write_text(json.dumps(claim, indent=2) + "\n", encoding="utf-8")
    result = {"schema": "phase16.readback-guard-local.v1", "claim": claim,
              "status": "UNKNOWN_NO_RETRY", "ssh_attempts": 0, "transport": {}}
    try:
        environment = ssh_environment()
        binding = loader("spain")
        core.require(binding.role == "spain" and
                     binding_digest(binding) == manifest["target_binding_sha256"],
                     "target_binding")
        command, frame = frame_request(script, payload)
        args = ["C:/Windows/System32/OpenSSH/ssh.exe", "-T", "-F", "none",
                "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes",
                "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=" + str(binding.known_hosts_path),
                "-o", "ConnectTimeout=10", "-o", "ConnectionAttempts=1",
                "-o", "ServerAliveInterval=5", "-o", "ServerAliveCountMax=1",
                "-i", str(binding.key_path), "-p", "22",
                binding.target_user + "@" + binding.target_host, command]
        result["ssh_attempts"] = 1
        returncode, output = transport(args, cwd=evidence_dir, env=environment, timeout=60,
                                       cap=65536, input_bytes=frame,
                                       diagnostics=result["transport"])
        received = validate_receipt(json.loads(output), returncode)
        result["remote"] = received
        result["status"] = received["status"]
    except Exception as error:
        reason = str(error)
        result["reason"] = reason if re.fullmatch(r"[A-Za-z0-9_]{1,80}", reason) else type(error).__name__
    finally:
        (evidence_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--execute", action="store_true")
    result.add_argument("--approve")
    result.add_argument("--approved-remote-sha256")
    result.add_argument("--approved-manifest-sha256")
    result.add_argument("--evidence-dir", type=Path)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        payload = build_payload(ROOT)
        script = remote_script(ROOT)
        manifest = validate_manifest(gate_manifest(ROOT), ROOT)
        preview = {"status": "SYNTHETIC_GATE_READY_NOT_EXECUTED",
                   "manifest_sha256": manifest_sha(ROOT),
                   "remote_sha256": sha(script), "payload_sha256": remote.PAYLOAD_SHA256,
                   "destination": remote.DESTINATION, "remote_seconds": 45,
                   "transport_seconds": 60, "ssh_attempts": 0,
                   "live_database": "EXCLUDED", "services": "EXCLUDED",
                   "requires_approval": remote.APPROVAL}
        if not args.execute:
            print(json.dumps(preview, indent=2))
            return 0
        core.require(args.evidence_dir is not None and args.approve == remote.APPROVAL and
                     args.approved_remote_sha256 == sha(script) and
                     args.approved_manifest_sha256 == manifest_sha(ROOT), "approval_binding")
        core.require(args.evidence_dir.as_posix() == manifest["local_evidence_directory"],
                     "evidence_directory")
        from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
        result = execute_once(payload, script, args.evidence_dir, approval=args.approve,
                              approved_sha=args.approved_remote_sha256, manifest=manifest,
                              approved_manifest_sha=args.approved_manifest_sha256,
                              loader=load_fixed_role_binding, transport=run_transport)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "SYNTHETIC_LINUX_GUARD_PASS_NOT_LIVE" else 3
    except Exception as error:
        reason = str(error)
        if not re.fullmatch(r"[A-Za-z0-9_]{1,80}", reason):
            reason = type(error).__name__
        print(json.dumps({"status": "LOCAL_STOP_NO_REMOTE_RETRY", "reason": reason}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
