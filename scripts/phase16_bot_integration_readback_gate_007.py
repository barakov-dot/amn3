"""Offline preview; one exact production read-only integration readback if approved."""
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
from scripts import phase16_bot_integration_readback_gate as base
from scripts.phase16_bot_linux_gate import run_transport, ssh_environment
from scripts.phase16_bot_readback_guard_gate import binding_digest
from scripts.vps import phase16_bot_integration_readback as core


Stop = core.Stop
OLD_APPROVAL = "PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_004"
APPROVAL = "PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_007"
GATE_MANIFEST_RELATIVE = Path(
    "research/amn2/phase16-bot-integration-readback-gate-007-manifest-2026-09-22.json"
)
EVIDENCE_DIRECTORY = Path(
    "C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/"
    "phase16-bot-integration-readback-runner-20260922/execution-007"
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(path, *, compile_python=False):
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    if compile_python:
        compile(data, str(path), "exec")
    return data


def remote_script(root=ROOT):
    original = base.remote_script(root)
    old = OLD_APPROVAL.encode()
    core.require(original.count(old) == 1, "remote_marker_binding")
    data = original.replace(old, APPROVAL.encode())
    compile(data, "<bound-phase16-integration-readback-007>", "exec")
    return data


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
    prior = base.validate_gate_manifest(base.gate_manifest(root), root)
    payload = base.build_payload(root)
    blobs = {
        "local_runner": canonical(root / "scripts/phase16_bot_integration_readback_gate_007.py",
                                  compile_python=True),
        "base_runner": canonical(root / "scripts/phase16_bot_integration_readback_gate.py",
                                 compile_python=True),
        "remote_supervisor": remote_script(root),
        "portable_core": canonical(root / "scripts/vps/phase16_bot_integration_readback.py",
                                   compile_python=True),
        "transport_helper": canonical(root / "scripts/phase16_bot_linux_gate.py",
                                      compile_python=True),
        "integration_manifest": canonical(root / base.SOURCE_MANIFEST_RELATIVE),
        "payload": payload,
        "base_gate_manifest": base.gate_bytes(root),
    }
    expected = {
        "schema": "phase16.integration-readback-gate-manifest.v1",
        "status": "ACTUAL_READBACK_GATE_READY_NOT_EXECUTED",
        "amn3_base": "09073963f602",
        "source_commit": "6e682356ed14a62d636ee58039fd3a389e794809",
        "approval": APPROVAL,
        "local_evidence_directory": EVIDENCE_DIRECTORY.as_posix(),
        "target_binding_sha256": prior["target_binding_sha256"],
        "sha256_lf": {name: sha(data) for name, data in blobs.items()},
        "bytes_lf": {name: len(data) for name, data in blobs.items()},
        "limits": prior["limits"],
        "readback_scope": prior["readback_scope"],
        "command_contract": {
            "entrypoint": "scripts/phase16_bot_integration_readback_gate_007.py",
            "requires_execute": True,
            "requires_approval": APPROVAL,
            "requires_remote_sha256": True,
            "requires_manifest_sha256": True,
            "requires_gate_sha256": True,
            "requires_exact_evidence_directory": True,
        },
    }
    core.require(value == expected, "manifest_binding")
    return value


def frame_request(script, payload):
    core.require(0 < len(script) <= 65536 and len(payload) == base.remote.PAYLOAD_SIZE,
                 "frame_size")
    digest = sha(script)
    bootstrap = (
        "import hashlib,sys;"
        "n=int(sys.stdin.buffer.read(8));"
        "0<n<=65536 or sys.exit(70);"
        "b=sys.stdin.buffer.read(n);"
        f"len(b)==n and hashlib.sha256(b).hexdigest()=='{digest}' or sys.exit(70);"
        "exec(compile(b,'<bound-phase16-integration-readback-007>','exec'),{'__name__':'__main__'})"
    )
    command = "/usr/bin/python3 -I -S -B -c " + shlex.quote(bootstrap) + " " + APPROVAL
    return command, f"{len(script):08d}".encode() + script + payload


def claim_directory(path):
    path = Path(path)
    core.require(path.parent.is_dir() and not path.parent.is_symlink(), "evidence_directory")
    try:
        path.mkdir()
    except FileExistsError:
        raise Stop("evidence_exists") from None
    return path


def execute_once(evidence_dir, *, approval, approved_remote_sha,
                 approved_manifest_sha, approved_gate_sha, manifest, loader,
                 transport):
    script = remote_script(ROOT)
    payload = base.build_payload(ROOT)
    core.require(
        approval == APPROVAL and approved_remote_sha == sha(script) and
        approved_manifest_sha == base.remote.MANIFEST_SHA256 and
        approved_gate_sha == gate_sha(ROOT),
        "approval_binding",
    )
    core.require(manifest == gate_manifest(ROOT), "manifest_binding")
    validate_gate_manifest(manifest, ROOT)
    base.remote.parse_payload(payload)
    evidence_dir = claim_directory(evidence_dir)
    claim = {
        "schema": "phase16.integration-readback-claim.v1",
        "scope": APPROVAL,
        "attempts": 1,
        "gate_sha256": approved_gate_sha,
        "source_manifest_sha256": base.remote.MANIFEST_SHA256,
        "remote_sha256": approved_remote_sha,
        "payload_sha256": base.remote.PAYLOAD_SHA256,
        "target_binding_sha256": manifest["target_binding_sha256"],
        "evidence_directory": Path(evidence_dir).as_posix(),
        "remote_seconds": 50,
        "transport_seconds": 60,
        "claimed_at": datetime.now(timezone.utc).isoformat(),
    }
    (evidence_dir / "claim.json").write_text(
        json.dumps(claim, indent=2) + "\n", encoding="utf-8"
    )
    result = {
        "schema": "phase16.integration-readback-local.v1",
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
        command, frame = frame_request(script, payload)
        args = [
            "C:/Windows/System32/OpenSSH/ssh.exe", "-T", "-F", "none",
            "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=yes",
            "-o", "UserKnownHostsFile=" + str(binding.known_hosts_path),
            "-o", "ConnectTimeout=10", "-o", "ConnectionAttempts=1",
            "-o", "ServerAliveInterval=5", "-o", "ServerAliveCountMax=1",
            "-i", str(binding.key_path), "-p", "22",
            binding.target_user + "@" + binding.target_host, command,
        ]
        result["ssh_attempts"] = 1
        returncode, output = transport(
            args, cwd=evidence_dir, env=environment, timeout=60, cap=65536,
            input_bytes=frame, diagnostics=result["transport"],
        )
        core.require(output != b"", "transport_no_remote_receipt")
        receipt = base.validate_receipt(json.loads(output), returncode)
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
    result.add_argument("--approved-remote-sha256")
    result.add_argument("--approved-manifest-sha256")
    result.add_argument("--approved-gate-sha256")
    result.add_argument("--evidence-dir", type=Path)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        manifest = validate_gate_manifest(gate_manifest(ROOT), ROOT)
        script = remote_script(ROOT)
        preview = {
            "status": "ACTUAL_READBACK_GATE_READY_NOT_EXECUTED",
            "gate_sha256": gate_sha(ROOT),
            "remote_sha256": sha(script),
            "manifest_sha256": base.remote.MANIFEST_SHA256,
            "payload_sha256": base.remote.PAYLOAD_SHA256,
            "remote_seconds": 50,
            "transport_seconds": 60,
            "ssh_attempts": 0,
            "database_access": "READ_ONLY_PRIVATE_MOUNT",
            "database_rows": "EXCLUDED",
            "service_actions": 0,
            "requires_approval": APPROVAL,
        }
        if not args.execute:
            print(json.dumps(preview, indent=2))
            return 0
        core.require(
            args.evidence_dir is not None and args.approve == APPROVAL and
            args.approved_remote_sha256 == sha(script) and
            args.approved_manifest_sha256 == base.remote.MANIFEST_SHA256 and
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
            approved_remote_sha=args.approved_remote_sha256,
            approved_manifest_sha=args.approved_manifest_sha256,
            approved_gate_sha=args.approved_gate_sha256, manifest=manifest,
            loader=load_fixed_role_binding, transport=run_transport,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "READBACK_COMPLETE_WITH_LIMITATIONS" else 3
    except Exception as error:
        reason = str(error)
        if not re.fullmatch(r"[A-Za-z0-9_]{1,80}", reason):
            reason = type(error).__name__
        print(json.dumps({"status": "LOCAL_STOP_NO_REMOTE_RETRY", "reason": reason}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
