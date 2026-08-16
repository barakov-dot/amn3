#!/usr/bin/env bash
set -Eeuo pipefail

python_executable="${PHASE15_PYTHON:-python3}"
exec "$python_executable" -c '
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys

PACKAGE_ID = "phase15-dual-protocol-bootstrap-20260811-001"
EXPECTED_NAMES = {
    "application_state", "architecture", "awg2_health", "backup_capability",
    "bridge_amn2sp3br0", "config_path", "container_capability",
    "container_cidr_172_29_252_0_28", "container_name", "database_state",
    "disk_space", "firewall", "interface_awg3", "os_compatibility", "python_3_12",
    "recovery_markers_phase14_phase15", "routes", "service_capability", "service_name",
    "state_root", "telegram_prerequisites", "udp_30002", "vpn_cidr_10_212_13_0_24",
}
STATES = {"absent", "free", "pass", "present", "stop", "unknown"}
CONFLICT_NAMES = {
    "bridge_amn2sp3br0", "config_path", "container_cidr_172_29_252_0_28",
    "container_name", "firewall", "interface_awg3", "routes", "service_name",
    "state_root", "udp_30002", "vpn_cidr_10_212_13_0_24",
}

def command(parts):
    try:
        result = subprocess.run(parts, check=False, capture_output=True, timeout=8)
    except (OSError, subprocess.SubprocessError):
        return 127, b"unavailable"
    return result.returncode, result.stdout + b"\n" + result.stderr

def observed(state, raw):
    if state not in STATES:
        raise ValueError("invalid observation state")
    if not isinstance(raw, bytes):
        raw = str(raw).encode("utf-8", errors="replace")
    return state, raw

def path_state(path, present_state="present"):
    candidate = pathlib.Path(path)
    return observed(present_state if candidate.exists() else "free", f"exists:{candidate.exists()}")

def production_observations():
    values = {}
    os_release = pathlib.Path("/etc/os-release")
    os_raw = os_release.read_bytes() if os_release.is_file() else b"missing"
    values["os_compatibility"] = observed("pass" if os.name == "posix" and os_release.is_file() else "stop", os_raw)
    machine = os.uname().machine if hasattr(os, "uname") else "unknown"
    values["architecture"] = observed("pass" if machine in {"x86_64", "amd64"} else "stop", machine)
    py_rc, py_raw = command(["python3.12", "--version"])
    values["python_3_12"] = observed("pass" if py_rc == 0 and b"Python 3.12" in py_raw else "stop", py_raw)
    try:
        free_bytes = shutil.disk_usage("/var/lib").free
        disk_state = "pass" if 4 * 1024 * 1024 * 1024 <= free_bytes else "stop"
        disk_raw = f"free-bytes:{free_bytes}"
    except OSError:
        disk_state, disk_raw = "unknown", "disk-unavailable"
    values["disk_space"] = observed(disk_state, disk_raw)
    app_root = pathlib.Path("/opt/amn2")
    database = pathlib.Path("/var/lib/amn2/amn2.db")
    backup_root = pathlib.Path("/var/backups")
    values["application_state"] = observed("present" if app_root.exists() else "unknown", f"exists:{app_root.exists()}")
    values["database_state"] = observed("present" if database.is_file() and os.access(database, os.R_OK) else "unknown", f"file:{database.is_file()}:readable:{os.access(database, os.R_OK)}")
    backup_ok = backup_root.is_dir() and os.access(backup_root, os.W_OK) and database.is_file() and os.access(database, os.R_OK)
    values["backup_capability"] = observed("pass" if backup_ok else "stop", f"backup-root:{backup_root.is_dir()}:{os.access(backup_root, os.W_OK)}:database:{database.is_file()}:{os.access(database, os.R_OK)}")
    systemd_rc, systemd_raw = command(["systemctl", "is-system-running"])
    values["service_capability"] = observed("pass" if systemd_rc in {0, 1} else "stop", systemd_raw)
    engine = shutil.which("docker") or shutil.which("podman")
    if engine:
        container_rc, container_raw = command([engine, "ps", "--format", "{{.Names}}"])
        values["container_capability"] = observed("pass" if container_rc == 0 else "stop", container_raw)
    else:
        container_rc, container_raw = 127, b"container-engine-unavailable"
        values["container_capability"] = observed("stop", container_raw)
    awg_unit_rc, awg_unit_raw = command(["systemctl", "is-active", "amn2-spain-awg2.service"])
    awg_link_rc, awg_link_raw = command(["ip", "link", "show", "awg2"])
    values["awg2_health"] = observed("pass" if awg_unit_rc == 0 and awg_link_rc == 0 else "stop", awg_unit_raw + awg_link_raw)
    telegram_rc, telegram_raw = command(["systemctl", "is-active", "amn2-telegram.service"])
    values["telegram_prerequisites"] = observed("pass" if telegram_rc == 0 else "stop", telegram_raw)
    awg3_rc, awg3_raw = command(["ip", "link", "show", "awg3"])
    values["interface_awg3"] = observed("free" if awg3_rc != 0 else "stop", awg3_raw)
    bridge_rc, bridge_raw = command(["ip", "link", "show", "amn2sp3br0"])
    values["bridge_amn2sp3br0"] = observed("free" if bridge_rc != 0 else "stop", bridge_raw)
    socket_rc, socket_raw = command(["ss", "-H", "-lun"])
    values["udp_30002"] = observed("free" if socket_rc == 0 and b":30002" not in socket_raw else "stop", socket_raw)
    route_rc, route_raw = command(["ip", "route", "show"])
    values["routes"] = observed("pass" if route_rc == 0 else "unknown", route_raw)
    values["vpn_cidr_10_212_13_0_24"] = observed("free" if route_rc == 0 and b"10.212.13.0/24" not in route_raw else "stop", route_raw)
    values["container_cidr_172_29_252_0_28"] = observed("free" if route_rc == 0 and b"172.29.252.0/28" not in route_raw else "stop", route_raw)
    nft_rc, nft_raw = command(["nft", "list", "ruleset"])
    if nft_rc != 0:
        nft_rc, nft_raw = command(["iptables", "-S"])
    values["firewall"] = observed("pass" if nft_rc == 0 and b"30002" not in nft_raw and b"awg3" not in nft_raw else "stop", nft_raw)
    values["config_path"] = path_state("/var/lib/amn2-spain/awg3/awg3.conf")
    values["state_root"] = path_state("/var/lib/amn2-spain/awg3")
    service_rc, service_raw = command(["systemctl", "show", "amn2-spain-awg3.service", "--property=LoadState", "--value"])
    values["service_name"] = observed("free" if service_rc != 0 or service_raw.strip() in {b"", b"not-found"} else "stop", service_raw)
    values["container_name"] = observed("free" if container_rc != 0 or b"amn2-spain-awg3" not in container_raw.splitlines() else "stop", container_raw)
    markers = []
    for root in (pathlib.Path("/run/amn2-spain"), pathlib.Path("/var/lib/amn2-spain")):
        if root.is_dir():
            markers.extend(path for path in root.rglob("*") if path.is_file() and any(token in path.name.casefold() for token in ("incomplete", "recovery", "pending")))
    marker_raw = "\n".join(sorted(str(path) for path in markers)) or "no-markers"
    values["recovery_markers_phase14_phase15"] = observed("stop" if markers else "absent", marker_raw)
    return socket.getfqdn(), values

def fixture_observations(root):
    fixture = pathlib.Path(root) / "observations.json"
    value = json.loads(fixture.read_bytes().decode("utf-8"))
    if not isinstance(value, dict) or set(value) != {"host_identity", "observations"}:
        raise ValueError("invalid fixture envelope")
    raw_observations = value["observations"]
    if not isinstance(raw_observations, dict) or set(raw_observations) != EXPECTED_NAMES:
        raise ValueError("invalid fixture inventory")
    result = {}
    for name, item in raw_observations.items():
        if not isinstance(item, dict) or set(item) != {"raw", "state"}:
            raise ValueError("invalid fixture observation")
        result[name] = observed(item["state"], item["raw"])
    return value["host_identity"], result

try:
    claim_id = os.environ["AMN2_PHASE15_CLAIM_ID"]
    expected_host = os.environ["AMN2_PHASE15_EXPECTED_HOST"]
    package_id = os.environ["AMN2_PHASE15_PACKAGE_ID"]
    if not claim_id or not expected_host or package_id != PACKAGE_ID:
        raise ValueError("preflight identity binding")
    fixture_root = os.environ.get("PHASE15_PREFLIGHT_FIXTURE_ROOT")
    host_identity, raw_values = fixture_observations(fixture_root) if fixture_root else production_observations()
    if set(raw_values) != EXPECTED_NAMES:
        raise ValueError("observation inventory")
    observations = [
        {"name": name, "observation_sha256": hashlib.sha256(raw_values[name][1]).hexdigest(), "state": raw_values[name][0]}
        for name in sorted(raw_values)
    ]
    reasons = []
    if host_identity != expected_host:
        reasons.append("identity_mismatch")
    if raw_values["recovery_markers_phase14_phase15"][0] == "stop":
        reasons.append("recovery_incomplete")
    if any(raw_values[name][0] == "stop" for name in CONFLICT_NAMES):
        reasons.append("resource_conflict")
    if any(state in {"stop", "unknown"} for name, (state, _raw) in raw_values.items() if name not in CONFLICT_NAMES and name != "recovery_markers_phase14_phase15"):
        reasons.append("observation_failed")
    document = {
        "blocking_reasons": sorted(set(reasons)),
        "claim_id": claim_id,
        "decision": "stop" if reasons else "pass",
        "host_identity": host_identity,
        "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "observations": observations,
        "package_id": PACKAGE_ID,
        "safety": {"live_mutation": False, "raw_output_persisted": False, "remote_file_written": False},
        "schema": "amn2.phase15.spain-readonly-collector.v1",
    }
    sys.stdout.buffer.write(json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n")
except Exception as exc:
    sys.stderr.write("collector_failed:" + type(exc).__name__ + "\n")
    raise SystemExit(71)
'
