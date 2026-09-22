"""Offline preview; one exact synthetic bound-frame SSH diagnostic if approved."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.phase16_bot_linux_gate import run_transport, ssh_environment
from scripts.phase16_bot_readback_guard_gate import binding_digest
from scripts.vps import phase16_bot_integration_readback as core


Stop = core.Stop
APPROVAL = "PHASE16_SSH_BOUND_FRAME_PREFLIGHT_20260922_006"
FRAME_SIZE = 68077
FRAME_PATTERN = b"PHASE16_BOUND_FRAME_PREFLIGHT_006\n"
GATE_MANIFEST_RELATIVE = Path(
    "research/amn2/phase16-bot-frame-preflight-gate-006-manifest-2026-09-22.json"
)
EVIDENCE_DIRECTORY = Path(
    "C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/"
    "phase16-bot-integration-readback-runner-20260922/execution-006"
)


def canonical(path):
    return Path(path).read_bytes().replace(b"\r\n", b"\n")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def frame_bytes():
    return (FRAME_PATTERN * ((FRAME_SIZE // len(FRAME_PATTERN)) + 1))[:FRAME_SIZE]


def pass_receipt():
    return {
        "schema": "phase16.ssh-bound-frame-preflight-remote.v1",
        "status": "SSH_BOUND_FRAME_PREFLIGHT_PASS",
        "approval": APPROVAL,
        "input_bytes": FRAME_SIZE,
        "frame_sha256": sha(frame_bytes()),
        "production_reads": 0,
        "service_actions": 0,
        "database_access": False,
        "application_imported": False,
        "runtime_activation": False,
    }


def stop_receipt():
    return {
        "schema": "phase16.ssh-bound-frame-preflight-remote.v1",
        "status": "STOP_NO_RETRY",
        "approval": APPROVAL,
        "reason": "frame_binding",
        "production_reads": 0,
        "service_actions": 0,
        "database_access": False,
        "application_imported": False,
        "runtime_activation": False,
    }


def remote_command():
    passed = json.dumps(pass_receipt(), sort_keys=True, separators=(",", ":"))
    stopped = json.dumps(stop_receipt(), sort_keys=True, separators=(",", ":"))
    code = (
        "import hashlib,sys\n"
        f"sys.argv==['-c','{APPROVAL}'] or sys.exit(70)\n"
        f"data=sys.stdin.buffer.read({FRAME_SIZE + 1})\n"
        f"valid=len(data)=={FRAME_SIZE} and hashlib.sha256(data).hexdigest()=='{sha(frame_bytes())}'\n"
        f"sys.stdout.write(({passed!r} if valid else {stopped!r})+'\\n')\n"
        "sys.stdout.flush()\n"
        "sys.exit(0 if valid else 3)\n"
    )
    return "/usr/bin/python3 -I -S -B -c " + shlex.quote(code) + " " + APPROVAL


def validate_receipt(value, returncode):
    if returncode == 0:
        core.require(value == pass_receipt(), "receipt_binding")
    elif returncode == 3:
        core.require(value == stop_receipt(), "receipt_binding")
    else:
        raise Stop("receipt_binding")
    return value


def gate_bytes(root=ROOT):
    return canonical(Path(root) / GATE_MANIFEST_RELATIVE)


def gate_sha(root=ROOT):
    return sha(gate_bytes(root))


def gate_manifest(root=ROOT):
    try:
        value = json.loads(gate_bytes(root))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise Stop("manifest_binding") from None
    core.require(isinstance(value, dict), "manifest_binding")
    return value


def validate_gate_manifest(value, root=ROOT):
    root = Path(root)
    expected_top = {
        "schema", "status", "amn3_base", "approval", "local_evidence_directory",
        "target_binding_sha256", "sha256_lf", "bytes_lf", "limits", "scope",
        "command_contract",
    }
    core.require(
        isinstance(value, dict) and set(value) == expected_top and
        value.get("schema") == "phase16.ssh-bound-frame-preflight-gate-manifest.v1" and
        value.get("status") == "BOUND_FRAME_PREFLIGHT_READY_NOT_EXECUTED" and
        value.get("amn3_base") == "13ccb2e836d2" and
        value.get("approval") == APPROVAL and
        value.get("local_evidence_directory") == EVIDENCE_DIRECTORY.as_posix() and
        re.fullmatch(r"[0-9a-f]{64}", value.get("target_binding_sha256", "")),
        "manifest_binding",
    )
    blobs = {
        "local_runner": canonical(root / "scripts/phase16_bot_frame_preflight_gate.py"),
        "transport_helper": canonical(root / "scripts/phase16_bot_linux_gate.py"),
        "frame": frame_bytes(),
    }
    hashes = value.get("sha256_lf")
    sizes = value.get("bytes_lf")
    core.require(
        isinstance(hashes, dict) and set(hashes) == set(blobs) and
        isinstance(sizes, dict) and set(sizes) == set(blobs) and
        all(hashes[name] == sha(data) and sizes[name] == len(data)
            for name, data in blobs.items()),
        "manifest_binding",
    )
    core.require(value.get("limits") == {
        "ssh_attempts": 1,
        "transport_seconds": 25,
        "transport_combined_output_bytes": 8192,
        "input_bytes": FRAME_SIZE,
        "retry": False,
        "cleanup_ssh": False,
    }, "manifest_binding")
    core.require(value.get("scope") == {
        "production_source_metadata": False,
        "production_unit_properties": False,
        "production_dependency_metadata": False,
        "production_database_schema": False,
        "production_database_rows": False,
        "service_actions": False,
        "application_imports": False,
        "telegram": False,
        "runtime_activation": False,
    }, "manifest_binding")
    core.require(value.get("command_contract") == {
        "entrypoint": "scripts/phase16_bot_frame_preflight_gate.py",
        "requires_execute": True,
        "requires_approval": APPROVAL,
        "requires_gate_sha256": True,
        "requires_exact_evidence_directory": True,
        "remote_program": "/usr/bin/python3",
        "remote_input_bytes": FRAME_SIZE,
        "remote_input_sha256": sha(frame_bytes()),
    }, "manifest_binding")
    return value


def claim_directory(path):
    path = Path(path)
    core.require(path.parent.is_dir() and not path.parent.is_symlink(), "evidence_directory")
    try:
        path.mkdir()
    except FileExistsError:
        raise Stop("evidence_exists") from None
    return path


def execute_once(evidence_dir, *, approval, approved_gate_sha, manifest, loader,
                 transport):
    core.require(
        approval == APPROVAL and approved_gate_sha == gate_sha(ROOT),
        "approval_binding",
    )
    core.require(manifest == gate_manifest(ROOT), "manifest_binding")
    validate_gate_manifest(manifest, ROOT)
    evidence_dir = claim_directory(evidence_dir)
    claim = {
        "schema": "phase16.ssh-bound-frame-preflight-claim.v1",
        "scope": APPROVAL,
        "attempts": 1,
        "gate_sha256": approved_gate_sha,
        "target_binding_sha256": manifest["target_binding_sha256"],
        "remote_command_sha256": sha(remote_command().encode()),
        "frame_sha256": sha(frame_bytes()),
        "input_bytes": FRAME_SIZE,
        "transport_seconds": 25,
        "evidence_directory": Path(evidence_dir).as_posix(),
        "claimed_at": datetime.now(timezone.utc).isoformat(),
    }
    (evidence_dir / "claim.json").write_text(
        json.dumps(claim, indent=2) + "\n", encoding="utf-8"
    )
    result = {
        "schema": "phase16.ssh-bound-frame-preflight-local.v1",
        "claim": claim,
        "status": "UNKNOWN_NO_RETRY",
        "ssh_attempts": 0,
        "transport": {},
    }
    try:
        environment = ssh_environment()
        binding = loader("spain")
        core.require(
            binding.role == "spain" and
            binding_digest(binding) == manifest["target_binding_sha256"],
            "target_binding",
        )
        args = [
            "C:/Windows/System32/OpenSSH/ssh.exe", "-T", "-F", "none",
            "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=yes",
            "-o", "UserKnownHostsFile=" + str(binding.known_hosts_path),
            "-o", "ConnectTimeout=10", "-o", "ConnectionAttempts=1",
            "-o", "ServerAliveInterval=5", "-o", "ServerAliveCountMax=1",
            "-i", str(binding.key_path), "-p", "22",
            binding.target_user + "@" + binding.target_host,
            remote_command(),
        ]
        result["ssh_attempts"] = 1
        returncode, output = transport(
            args, cwd=evidence_dir, env=environment, timeout=25, cap=8192,
            input_bytes=frame_bytes(), diagnostics=result["transport"],
        )
        core.require(output != b"", "transport_no_remote_receipt")
        receipt = validate_receipt(json.loads(output), returncode)
        result["remote"] = receipt
        result["status"] = receipt["status"]
    except Exception as error:
        reason = str(error)
        result["reason"] = (
            reason if re.fullmatch(r"[A-Za-z0-9_]{1,80}", reason)
            else type(error).__name__
        )
    finally:
        (evidence_dir / "result.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
    return result


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--execute", action="store_true")
    result.add_argument("--approve")
    result.add_argument("--approved-gate-sha256")
    result.add_argument("--evidence-dir", type=Path)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        manifest = validate_gate_manifest(gate_manifest(ROOT), ROOT)
        preview = {
            "status": "BOUND_FRAME_PREFLIGHT_READY_NOT_EXECUTED",
            "gate_sha256": gate_sha(ROOT),
            "remote_command_sha256": sha(remote_command().encode()),
            "frame_sha256": sha(frame_bytes()),
            "input_bytes": FRAME_SIZE,
            "transport_seconds": 25,
            "ssh_attempts": 0,
            "production_reads": 0,
            "service_actions": 0,
            "requires_approval": APPROVAL,
        }
        if not args.execute:
            print(json.dumps(preview, indent=2))
            return 0
        core.require(
            args.evidence_dir is not None and args.approve == APPROVAL and
            args.approved_gate_sha256 == gate_sha(ROOT),
            "approval_binding",
        )
        core.require(
            args.evidence_dir.as_posix() == manifest["local_evidence_directory"],
            "evidence_directory",
        )
        from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
        result = execute_once(
            args.evidence_dir, approval=args.approve,
            approved_gate_sha=args.approved_gate_sha256, manifest=manifest,
            loader=load_fixed_role_binding, transport=run_transport,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "SSH_BOUND_FRAME_PREFLIGHT_PASS" else 3
    except Exception as error:
        reason = str(error)
        if not re.fullmatch(r"[A-Za-z0-9_]{1,80}", reason):
            reason = type(error).__name__
        print(json.dumps({"status": "LOCAL_STOP_NO_REMOTE_RETRY", "reason": reason}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
