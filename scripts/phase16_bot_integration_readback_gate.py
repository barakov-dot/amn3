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
from scripts.phase16_bot_linux_gate import run_transport, ssh_environment
from scripts.phase16_bot_readback_guard_gate import binding_digest
from scripts.vps import phase16_bot_integration_readback as core
from scripts.vps import phase16_bot_integration_readback_remote as remote

SOURCE_MANIFEST_RELATIVE = Path("research/amn2/phase16-bot-integration-manifest-6e68235.json")
GATE_MANIFEST_RELATIVE = Path("research/amn2/phase16-bot-integration-readback-gate-manifest-2026-09-22.json")
EVIDENCE_DIRECTORY = Path(
    "C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/"
    "phase16-bot-integration-readback-runner-20260922/execution-001"
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(path, *, compile_python=False):
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    if compile_python:
        compile(data, str(path), "exec")
    return data


def build_payload(root=ROOT):
    root = Path(root)
    core_data = canonical(root / "scripts/vps/phase16_bot_integration_readback.py",
                          compile_python=True)
    manifest_data = canonical(root / SOURCE_MANIFEST_RELATIVE)
    payload = remote.MAGIC + f"{len(core_data):08d}{len(manifest_data):08d}".encode() + core_data + manifest_data
    core.require(len(core_data) == remote.CORE_SIZE and sha(core_data) == remote.CORE_SHA256 and
                 len(manifest_data) == remote.MANIFEST_SIZE and
                 sha(manifest_data) == remote.MANIFEST_SHA256 and
                 len(payload) == remote.PAYLOAD_SIZE and sha(payload) == remote.PAYLOAD_SHA256,
                 "payload_binding")
    return payload


def remote_script(root=ROOT):
    return canonical(Path(root) / "scripts/vps/phase16_bot_integration_readback_remote.py",
                     compile_python=True)


def gate_bytes(root=ROOT):
    return canonical(Path(root) / GATE_MANIFEST_RELATIVE)


def gate_sha(root=ROOT):
    return sha(gate_bytes(root))


def gate_manifest(root=ROOT):
    try:
        value = json.loads(gate_bytes(root))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise core.Stop("manifest_binding") from None
    core.require(isinstance(value, dict), "manifest_binding")
    return value


def source_manifest(root=ROOT):
    try:
        value = json.loads(canonical(Path(root) / SOURCE_MANIFEST_RELATIVE))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise core.Stop("manifest_binding") from None
    core.require(isinstance(value, dict) and value.get("schema") ==
                 "phase16.integration-manifest.v1", "manifest_binding")
    return value


def validate_gate_manifest(value, root=ROOT):
    root = Path(root)
    top = {"schema", "status", "amn3_base", "source_commit", "approval",
           "local_evidence_directory", "target_binding_sha256", "sha256_lf",
           "bytes_lf", "limits", "readback_scope", "command_contract"}
    core.require(isinstance(value, dict) and set(value) == top and
                 value.get("schema") == "phase16.integration-readback-gate-manifest.v1" and
                 value.get("status") == "ACTUAL_READBACK_GATE_READY_NOT_EXECUTED" and
                 value.get("amn3_base") == "a713d4dce8ca" and
                 value.get("source_commit") == "6e682356ed14a62d636ee58039fd3a389e794809" and
                 value.get("approval") == remote.APPROVAL and
                 value.get("local_evidence_directory") == EVIDENCE_DIRECTORY.as_posix() and
                 re.fullmatch(r"[0-9a-f]{64}", value.get("target_binding_sha256", "")),
                 "manifest_binding")
    payload = build_payload(root)
    blobs = {
        "local_runner": canonical(root / "scripts/phase16_bot_integration_readback_gate.py",
                                  compile_python=True),
        "remote_supervisor": remote_script(root),
        "portable_core": canonical(root / "scripts/vps/phase16_bot_integration_readback.py",
                                   compile_python=True),
        "integration_manifest": canonical(root / SOURCE_MANIFEST_RELATIVE),
        "payload": payload,
    }
    hashes, sizes = value.get("sha256_lf"), value.get("bytes_lf")
    core.require(isinstance(hashes, dict) and set(hashes) == set(blobs) and
                 isinstance(sizes, dict) and set(sizes) == set(blobs) and
                 all(hashes[name] == sha(data) and sizes[name] == len(data)
                     for name, data in blobs.items()), "manifest_binding")
    core.require(value.get("limits") == {
        "ssh_attempts": 1, "remote_seconds": 50, "work_seconds": 44,
        "cleanup_seconds": 4, "finalization_seconds": 2, "transport_seconds": 60,
        "remote_stdout_bytes": 65536, "remote_stderr_bytes": 8192,
        "transport_combined_output_bytes": 65536,
        "cleanup_signal_scope": "owned_collector_process_groups_only",
        "retry": False, "cleanup_ssh": False,
    }, "manifest_binding")
    core.require(value.get("readback_scope") == {
        "production_source_metadata": True, "production_unit_properties": True,
        "production_dependency_metadata": True, "production_database_schema": True,
        "production_database_rows": False, "private_mount_namespace": True,
        "private_network_namespace": True, "service_actions": False,
        "application_imports": False, "telegram": False, "runtime_activation": False,
    }, "manifest_binding")
    core.require(value.get("command_contract") == {
        "entrypoint": "scripts/phase16_bot_integration_readback_gate.py",
        "requires_execute": True, "requires_approval": remote.APPROVAL,
        "requires_remote_sha256": True, "requires_manifest_sha256": True,
        "requires_gate_sha256": True, "requires_exact_evidence_directory": True,
    }, "manifest_binding")
    return value


def frame_request(script, payload):
    core.require(0 < len(script) <= 65536 and len(payload) == remote.PAYLOAD_SIZE,
                 "frame_size")
    digest = sha(script)
    bootstrap = ("import hashlib,sys;"
                 "n=int(sys.stdin.buffer.read(8));"
                 "0<n<=65536 or sys.exit(70);"
                 "b=sys.stdin.buffer.read(n);"
                 f"len(b)==n and hashlib.sha256(b).hexdigest()=='{digest}' or sys.exit(70);"
                 "exec(compile(b,'<bound-phase16-integration-readback>','exec'),{'__name__':'__main__'})")
    command = "/usr/bin/python3 -I -S -B -c " + shlex.quote(bootstrap) + " " + remote.APPROVAL
    return command, f"{len(script):08d}".encode() + script + payload


def exact_dict(value, keys):
    core.require(isinstance(value, dict) and set(value) == set(keys), "receipt_binding")
    return value


def validate_host(value):
    exact_dict(value, {"system", "machine", "python", "sqlite", "python_device", "python_inode"})
    core.require(value["system"] == "Linux" and value["machine"] == "x86_64" and
                 re.fullmatch(r"3\.12\.[0-9]+", value["python"]) and
                 re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value["sqlite"]) and
                 type(value["python_device"]) is int and type(value["python_inode"]) is int,
                 "receipt_binding")


UNIT_KEYS = {"role", "LoadState", "ActiveState", "SubState", "Type", "Restart",
             "KillMode", "pid", "TimeoutStartUSec", "TimeoutStopUSec", "WatchdogUSec",
             "KillSignal", "FinalKillSignal", "exec_matches", "cwd_matches",
             "hooks_present", "runtime_binding", "unit_file_count", "unit_files_digest",
             "cgroup_matches", "start_ticks"}


def validate_unit(value, role):
    exact_dict(value, UNIT_KEYS)
    core.require(value["role"] == role and type(value["pid"]) is int and value["pid"] >= 0 and
                 (value["start_ticks"] is None or
                  type(value["start_ticks"]) is int and value["start_ticks"] >= 0) and
                 all(type(value[name]) is bool for name in
                     ("exec_matches", "cwd_matches", "hooks_present", "cgroup_matches")) and
                 value["runtime_binding"] == "UNKNOWN" and
                 type(value["unit_file_count"]) is int and 0 <= value["unit_file_count"] <= 9 and
                 re.fullmatch(r"[0-9a-f]{64}", value["unit_files_digest"]),
                 "receipt_binding")
    enums = {"LoadState": {"loaded", "not-found", "error", "masked", "UNKNOWN"},
             "ActiveState": {"active", "inactive", "failed", "activating", "deactivating", "reloading", "UNKNOWN"},
             "SubState": {"running", "dead", "failed", "start", "stop", "exited", "auto-restart", "UNKNOWN"},
             "Type": {"simple", "notify", "exec", "forking", "oneshot", "dbus", "idle", "UNKNOWN"},
             "Restart": {"no", "always", "on-failure", "on-abnormal", "on-abort", "on-success", "on-watchdog", "UNKNOWN"},
             "KillMode": {"control-group", "mixed", "process", "none", "UNKNOWN"}}
    core.require(all(value[name] in allowed for name, allowed in enums.items()), "receipt_binding")
    for name in ("TimeoutStartUSec", "TimeoutStopUSec", "WatchdogUSec"):
        core.require(value[name] == "UNKNOWN" or re.fullmatch(
            r"(infinity|[0-9]+|(?:[0-9.]+(?:us|ms|s|min|h|d) ?)+)", value[name]),
            "receipt_binding")
    for name in ("KillSignal", "FinalKillSignal"):
        core.require(value[name] == "UNKNOWN" or re.fullmatch(r"SIG[A-Z0-9]{1,20}", value[name]),
                     "receipt_binding")
    for name in UNIT_KEYS - {"pid", "start_ticks", "exec_matches", "cwd_matches",
                             "hooks_present", "cgroup_matches", "unit_file_count"}:
        core.require(isinstance(value[name], str) and len(value[name]) <= 80,
                     "receipt_binding")


def validate_units(value):
    exact_dict(value, {"bot", "web"})
    validate_unit(value["bot"], "bot")
    validate_unit(value["web"], "web")


def validate_source(value, manifest):
    exact_dict(value, {"status", "files", "missing", "different", "extra_count",
                       "extra_digest", "runtime_binding"})
    expected = manifest["source"]
    core.require(value["status"] in {"MATCH_IN_SCOPE", "DIFFERENT"} and
                 value["runtime_binding"] == "UNKNOWN" and isinstance(value["files"], dict) and
                 set(value["files"]) <= set(expected) and isinstance(value["missing"], list) and
                 isinstance(value["different"], list) and set(value["missing"]) <= set(expected) and
                 set(value["different"]) <= set(expected) and type(value["extra_count"]) is int and
                 0 <= value["extra_count"] <= 256 and
                 re.fullmatch(r"[0-9a-f]{64}", value["extra_digest"]), "receipt_binding")
    for name, item in value["files"].items():
        exact_dict(item, {"sha256", "bytes"})
        core.require(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) and
                     type(item["bytes"]) is int and 0 <= item["bytes"] <= 1048576,
                     "receipt_binding")


def validate_dependencies(value, manifest):
    exact_dict(value, {"status", "matched", "missing", "different", "extra_count",
                       "extra_digest", "pth_count", "pth_hashes", "runtime_binding"})
    pins = manifest["runtime_pins"]
    core.require(value["status"] == "STATIC_METADATA_ONLY" and
                 value["runtime_binding"] == "UNKNOWN" and isinstance(value["matched"], list) and
                 isinstance(value["missing"], list) and set(value["matched"]) <= set(pins) and
                 set(value["missing"]) <= set(pins) and isinstance(value["different"], dict) and
                 set(value["different"]) <= set(pins) and
                 all(re.fullmatch(r"[0-9][A-Za-z0-9.!+_-]{0,63}", item)
                     for item in value["different"].values()) and
                 type(value["extra_count"]) is int and 0 <= value["extra_count"] <= 128 and
                 re.fullmatch(r"[0-9a-f]{64}", value["extra_digest"]) and
                 type(value["pth_count"]) is int and 0 <= value["pth_count"] <= 16 and
                 isinstance(value["pth_hashes"], list) and len(value["pth_hashes"]) ==
                 value["pth_count"] and all(re.fullmatch(r"[0-9a-f]{64}", item)
                                             for item in value["pth_hashes"]),
                 "receipt_binding")


def validate_file_map(value):
    exact_dict(value, {"database", "wal", "shm", "journal"})
    for item in value.values():
        core.require(isinstance(item, dict) and item.get("present") in (True, False),
                     "receipt_binding")
        if item["present"]:
            exact_dict(item, {"present", "device", "inode", "bytes"})
            core.require(all(type(item[name]) is int and item[name] >= 0
                             for name in ("device", "inode", "bytes")), "receipt_binding")
        else:
            exact_dict(item, {"present"})


def validate_database_files(value):
    exact_dict(value, {"before", "after", "sizes_stable"})
    validate_file_map(value["before"])
    validate_file_map(value["after"])
    core.require(value["before"]["database"]["present"] is True and
                 type(value["sizes_stable"]) is bool, "receipt_binding")


def validate_database(value, manifest):
    exact_dict(value, {"status", "sqlite_version", "schema_version", "user_version",
                       "journal_mode", "tables", "compatibility"})
    allowed = manifest["schema_allowlist"]
    core.require(value["status"] == "SHAPE_ONLY" and value["compatibility"] == "UNKNOWN" and
                 re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value["sqlite_version"]) and
                 type(value["schema_version"]) is int and type(value["user_version"]) is int and
                 value["journal_mode"] in {"delete", "truncate", "persist", "memory", "wal", "off"} and
                 isinstance(value["tables"], list) and len(value["tables"]) <= 128,
                 "receipt_binding")
    for table in value["tables"]:
        exact_dict(table, {"name", "columns", "indexes", "foreign_keys"})
        name = table["name"]
        core.require(name in allowed["tables"] and isinstance(table["columns"], list) and
                     isinstance(table["indexes"], list) and isinstance(table["foreign_keys"], list),
                     "receipt_binding")
        for column in table["columns"]:
            core.require(isinstance(column, list) and len(column) == 5 and
                         column[0] in allowed["tables"][name] and
                         column[1] in {"INTEGER", "INT", "TEXT", "REAL", "BLOB", "NUMERIC", ""} and
                         all(type(item) is int for item in column[2:]), "receipt_binding")
        for index in table["indexes"]:
            exact_dict(index, {"name", "unique", "columns", "partial"})
            core.require((index["name"] in allowed["indexes"] or
                          re.fullmatch("sqlite_autoindex_" + re.escape(name) + "_[0-9]+",
                                       index["name"])) and
                         isinstance(index["columns"], list) and
                         all(item in allowed["tables"][name] for item in index["columns"]) and
                         type(index["unique"]) is int and type(index["partial"]) is int,
                         "receipt_binding")
        for foreign in table["foreign_keys"]:
            exact_dict(foreign, {"table", "from", "to", "sequence", "on_update", "on_delete"})
            core.require(foreign["table"] in allowed["tables"] and
                         foreign["from"] in allowed["tables"][name] and
                         (foreign["to"] is None or foreign["to"] in allowed["tables"][foreign["table"]]) and
                         type(foreign["sequence"]) is int and
                         foreign["on_update"] in {"NO ACTION", "RESTRICT", "SET NULL", "SET DEFAULT", "CASCADE"} and
                         foreign["on_delete"] in {"NO ACTION", "RESTRICT", "SET NULL", "SET DEFAULT", "CASCADE"},
                         "receipt_binding")


def validate_process(value):
    exact_dict(value, {"stdout_bytes", "stderr_bytes", "stderr_present"})
    core.require(type(value["stdout_bytes"]) is int and 0 <= value["stdout_bytes"] <= 65536 and
                 type(value["stderr_bytes"]) is int and 0 <= value["stderr_bytes"] <= 8192 and
                 type(value["stderr_present"]) is bool and
                 value["stderr_present"] == (value["stderr_bytes"] > 0), "receipt_binding")


def validate_holders(value):
    exact_dict(value, {"status", "holders", "pids_seen", "fds_seen", "denied", "churn",
                       "coverage_complete", "writer_completeness"})
    core.require(value["status"] in {"OBSERVED_ONLY", "UNKNOWN"} and
                 value["writer_completeness"] == "UNKNOWN" and isinstance(value["holders"], list) and
                 all(type(value[name]) is int and value[name] >= 0 for name in
                     ("pids_seen", "fds_seen", "denied", "churn")) and
                 type(value["coverage_complete"]) is bool, "receipt_binding")
    for item in value["holders"]:
        exact_dict(item, {"pid", "start_ticks", "role", "files"})
        core.require(type(item["pid"]) is int and type(item["start_ticks"]) is int and
                     item["role"] in {"bot", "web", "UNKNOWN_OWNER"} and
                     isinstance(item["files"], list) and
                     set(item["files"]) <= {"database", "wal", "shm", "journal"},
                     "receipt_binding")


def validate_partial(value, manifest):
    core.require(isinstance(value, dict) and set(value) <= {"host", "units_before", "source",
                 "dependencies", "database_files_before", "database", "database_child",
                 "holders", "units_after", "summary"}, "receipt_binding")
    validators = {"host": validate_host, "units_before": validate_units,
                  "source": lambda item: validate_source(item, manifest),
                  "dependencies": lambda item: validate_dependencies(item, manifest),
                  "database_files_before": validate_file_map,
                  "database": lambda item: validate_database(item, manifest),
                  "database_child": validate_process, "holders": validate_holders,
                  "units_after": validate_units}
    for name, item in value.items():
        if name == "summary":
            exact_dict(item, {"stages", "digests"})
            allowed = set(validators)
            core.require(isinstance(item["stages"], list) and set(item["stages"]) <= allowed and
                         isinstance(item["digests"], dict) and
                         set(item["digests"]) == set(item["stages"]) and
                         all(re.fullmatch(r"[0-9a-f]{64}", digest)
                             for digest in item["digests"].values()), "receipt_binding")
        else:
            validators[name](item)


def pass_receipt_for_tests():
    manifest = source_manifest(ROOT)
    def unit(role):
        return {"role": role, "LoadState": "loaded", "ActiveState": "active",
                "SubState": "running", "Type": "simple", "Restart": "on-failure",
                "KillMode": "control-group", "pid": 1, "TimeoutStartUSec": "30s",
                "TimeoutStopUSec": "30s", "WatchdogUSec": "0", "KillSignal": "UNKNOWN",
                "FinalKillSignal": "UNKNOWN", "exec_matches": True, "cwd_matches": True,
                "hooks_present": False, "runtime_binding": "UNKNOWN", "unit_file_count": 1,
                "unit_files_digest": "0" * 64, "cgroup_matches": True, "start_ticks": 1}
    file_map = {"database": {"present": True, "device": 1, "inode": 2, "bytes": 3},
                "wal": {"present": False}, "shm": {"present": False},
                "journal": {"present": False}}
    return {"schema": "phase16.integration-readback-remote.v1",
            "status": "READBACK_COMPLETE_WITH_LIMITATIONS",
            "host": {"system": "Linux", "machine": "x86_64", "python": "3.12.3",
                     "sqlite": "3.45.1", "python_device": 1, "python_inode": 2},
            "units_before": {"bot": unit("bot"), "web": unit("web")},
            "source": {"status": "MATCH_IN_SCOPE", "files": manifest["source"],
                       "missing": [], "different": [], "extra_count": 0,
                       "extra_digest": "0" * 64, "runtime_binding": "UNKNOWN"},
            "dependencies": {"status": "STATIC_METADATA_ONLY",
                             "matched": sorted(manifest["runtime_pins"]), "missing": [],
                             "different": {}, "extra_count": 0, "extra_digest": "0" * 64,
                             "pth_count": 0, "pth_hashes": [], "runtime_binding": "UNKNOWN"},
            "database_files": {"before": file_map, "after": json.loads(json.dumps(file_map)),
                               "sizes_stable": True},
            "database": {"status": "SHAPE_ONLY", "sqlite_version": "3.45.1",
                         "schema_version": 1, "user_version": 0, "journal_mode": "delete",
                         "tables": [], "compatibility": "UNKNOWN"},
            "database_child": {"stdout_bytes": 1, "stderr_bytes": 0, "stderr_present": False},
            "holders": {"status": "OBSERVED_ONLY", "holders": [], "pids_seen": 1,
                        "fds_seen": 1, "denied": 0, "churn": 0,
                        "coverage_complete": True, "writer_completeness": "UNKNOWN"},
            "units_after": {"bot": unit("bot"), "web": unit("web")},
            "unit_identity_stable": True, "service_actions": 0,
            "database_write_attempted": False, "application_imported": False,
            "production_source_read": True, "production_units_read": True,
            "runtime_activation": False, "completed_at": "2026-09-22T00:00:00+00:00",
            "limitations": ["STATIC_SOURCE_SCOPE_ONLY", "STATIC_DEPENDENCY_METADATA_ONLY",
                            "SCHEMA_SHAPE_ONLY", "RUNTIME_BINDING_UNKNOWN",
                            "WRITER_COMPLETENESS_UNKNOWN", "SEMANTIC_COMPATIBILITY_UNKNOWN"]}


def validate_receipt(result, returncode):
    manifest = source_manifest(ROOT)
    common = {"schema", "status", "service_actions", "database_write_attempted",
              "application_imported", "runtime_activation"}
    core.require(isinstance(result, dict) and result.get("schema") ==
                 "phase16.integration-readback-remote.v1" and
                 result.get("service_actions") == 0 and
                 result.get("database_write_attempted") is False and
                 result.get("application_imported") is False and
                 result.get("runtime_activation") is False, "receipt_binding")
    if result.get("status") == "READBACK_COMPLETE_WITH_LIMITATIONS":
        expected = common | {"host", "units_before", "source", "dependencies",
                             "database_files", "database", "database_child", "holders",
                             "units_after", "unit_identity_stable", "production_source_read",
                             "production_units_read", "completed_at", "limitations"}
        core.require(set(result) == expected and returncode == 0 and
                     result.get("production_source_read") is True and
                     result.get("production_units_read") is True and
                     result.get("unit_identity_stable") is True and
                     all(isinstance(result.get(name), dict) for name in
                         ("host", "units_before", "source", "dependencies", "database_files",
                          "database", "database_child", "holders", "units_after")) and
                     isinstance(result.get("limitations"), list) and
                     result.get("database", {}).get("status") == "SHAPE_ONLY" and
                     isinstance(result.get("completed_at"), str) and
                     len(result["completed_at"]) <= 40 and
                     re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.+\-]{8,32}",
                                  result["completed_at"]),
                     "receipt_binding")
        validate_host(result["host"])
        validate_units(result["units_before"])
        validate_source(result["source"], manifest)
        validate_dependencies(result["dependencies"], manifest)
        validate_database_files(result["database_files"])
        validate_database(result["database"], manifest)
        validate_process(result["database_child"])
        validate_holders(result["holders"])
        validate_units(result["units_after"])
        core.require(result["limitations"] == [
            "STATIC_SOURCE_SCOPE_ONLY", "STATIC_DEPENDENCY_METADATA_ONLY",
            "SCHEMA_SHAPE_ONLY", "RUNTIME_BINDING_UNKNOWN",
            "WRITER_COMPLETENESS_UNKNOWN", "SEMANTIC_COMPATIBILITY_UNKNOWN"],
            "receipt_binding")
    else:
        core.require(set(result) == common | {"reason", "partial"} and returncode == 3 and
                     result.get("status") == "STOP_NO_RETRY" and
                     re.fullmatch(r"[a-z0-9_]{1,80}", result.get("reason", "")) and
                     isinstance(result.get("partial"), dict),
                     "receipt_binding")
        validate_partial(result["partial"], manifest)
    return result


def claim_directory(path):
    path = Path(path)
    core.require(path.parent.is_dir() and not path.parent.is_symlink(), "evidence_directory")
    try:
        path.mkdir()
    except FileExistsError:
        raise core.Stop("evidence_exists") from None
    return path


def execute_once(payload, script, evidence_dir, *, approval, approved_remote_sha,
                 approved_manifest_sha, gate, approved_gate_sha, loader, transport):
    core.require(approval == remote.APPROVAL and approved_remote_sha == sha(script) and
                 approved_manifest_sha == remote.MANIFEST_SHA256 and
                 approved_gate_sha == gate_sha(ROOT), "approval_binding")
    core.require(gate == gate_manifest(ROOT), "manifest_binding")
    validate_gate_manifest(gate, ROOT)
    remote.parse_payload(payload)
    evidence_dir = claim_directory(evidence_dir)
    claim = {"schema": "phase16.integration-readback-claim.v1", "scope": remote.APPROVAL,
             "attempts": 1, "gate_sha256": approved_gate_sha,
             "source_manifest_sha256": remote.MANIFEST_SHA256,
             "remote_sha256": approved_remote_sha, "payload_sha256": remote.PAYLOAD_SHA256,
             "target_binding_sha256": gate["target_binding_sha256"],
             "evidence_directory": Path(evidence_dir).as_posix(),
             "remote_seconds": 50, "transport_seconds": 60,
             "claimed_at": datetime.now(timezone.utc).isoformat()}
    (evidence_dir / "claim.json").write_text(json.dumps(claim, indent=2) + "\n", encoding="utf-8")
    result = {"schema": "phase16.integration-readback-local.v1", "claim": claim,
              "status": "UNKNOWN_NO_RETRY", "ssh_attempts": 0, "transport": {}}
    try:
        environment = ssh_environment()
        binding = loader("spain")
        core.require(binding.role == "spain" and
                     binding_digest(binding) == gate["target_binding_sha256"],
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
    result.add_argument("--approved-gate-sha256")
    result.add_argument("--evidence-dir", type=Path)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        payload = build_payload(ROOT)
        script = remote_script(ROOT)
        gate = validate_gate_manifest(gate_manifest(ROOT), ROOT)
        preview = {"status": "ACTUAL_READBACK_GATE_READY_NOT_EXECUTED",
                   "gate_sha256": gate_sha(ROOT), "remote_sha256": sha(script),
                   "manifest_sha256": remote.MANIFEST_SHA256,
                   "payload_sha256": remote.PAYLOAD_SHA256,
                   "remote_seconds": 50, "transport_seconds": 60,
                   "ssh_attempts": 0, "database_access": "READ_ONLY_PRIVATE_MOUNT",
                   "database_rows": "EXCLUDED", "service_actions": 0,
                   "requires_approval": remote.APPROVAL}
        if not args.execute:
            print(json.dumps(preview, indent=2))
            return 0
        core.require(args.evidence_dir is not None and args.approve == remote.APPROVAL and
                     args.approved_remote_sha256 == sha(script) and
                     args.approved_manifest_sha256 == remote.MANIFEST_SHA256 and
                     args.approved_gate_sha256 == gate_sha(ROOT), "approval_binding")
        core.require(args.evidence_dir.as_posix() == gate["local_evidence_directory"],
                     "evidence_directory")
        from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
        result = execute_once(payload, script, args.evidence_dir, approval=args.approve,
                              approved_remote_sha=args.approved_remote_sha256,
                              approved_manifest_sha=args.approved_manifest_sha256,
                              gate=gate, approved_gate_sha=args.approved_gate_sha256,
                              loader=load_fixed_role_binding, transport=run_transport)
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
