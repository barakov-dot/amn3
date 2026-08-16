#!/usr/bin/env bash
set -Eeuo pipefail

python_executable="${PHASE15_PYTHON:-python3}"
if [[ "$#" -ne 3 ]]; then
    "$python_executable" -c 'import sys; sys.stderr.buffer.write(b"collector_envelope_invalid\n")'
    exit 64
fi

exec "$python_executable" -c '
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import socket
import subprocess
import sys
import threading
import time

PACKAGE_ID = "phase15-dual-protocol-bootstrap-20260811-001"
CLAIM_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
EXPECTED_HOST_RE = re.compile(r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*$")
HANDSHAKE_RE = re.compile(rb"^[A-Za-z0-9+/]{43}=\t([0-9]+)$")
MAXIMUM_OUTPUT_BYTES = 65536
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

def command(parts, maximum_output_bytes=MAXIMUM_OUTPUT_BYTES, timeout_seconds=8):
    environment = os.environ.copy()
    environment["LC_ALL"] = "C"
    try:
        process = subprocess.Popen(parts, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment)
    except OSError:
        return 127, b"", b"", "unavailable"
    overflow = threading.Event()
    outputs = [bytearray(), bytearray()]

    def read_bounded(stream, output):
        try:
            while True:
                chunk = stream.read(4096)
                if not chunk:
                    return
                remaining = maximum_output_bytes + 1 - len(output)
                if 0 < remaining:
                    output.extend(chunk[:remaining])
                if maximum_output_bytes < len(output):
                    overflow.set()
                    return
        finally:
            stream.close()

    threads = [
        threading.Thread(target=read_bounded, args=(process.stdout, outputs[0]), daemon=True),
        threading.Thread(target=read_bounded, args=(process.stderr, outputs[1]), daemon=True),
    ]
    for thread in threads:
        thread.start()
    deadline = time.monotonic() + timeout_seconds
    disposition = "success"
    while process.poll() is None:
        if overflow.is_set():
            disposition = "output_oversized"
            process.kill()
            break
        if deadline <= time.monotonic():
            disposition = "timeout"
            process.kill()
            break
        time.sleep(0.01)
    try:
        return_code = process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        process.kill()
        return_code = process.wait()
        disposition = "timeout"
    for thread in threads:
        thread.join(timeout=1)
    if overflow.is_set():
        disposition = "output_oversized"
        if return_code == 0:
            return_code = 125
    elif disposition == "success" and return_code != 0:
        disposition = "command_failed"
    return return_code, bytes(outputs[0]), bytes(outputs[1]), disposition

def probe_ok(probe):
    return probe[0] == 0 and probe[3] == "success"

def classify_ip_link(probe, name):
    if probe_ok(probe):
        return "stop"
    expected = (f"Device \"{name}\" does not exist.\n").encode("ascii")
    if probe[0] == 1 and probe[1] == b"" and probe[2] == expected and probe[3] == "command_failed":
        return "free"
    return "stop"

def classify_container_inventory(results):
    if not results or any(not probe_ok(probe) for _engine, probe in results):
        return "stop", "stop"
    names = []
    for _engine, probe in results:
        try:
            names.extend(line for line in probe[1].decode("utf-8", errors="strict").splitlines() if line)
        except UnicodeDecodeError:
            return "stop", "stop"
    return "pass", "stop" if "amn2-spain-awg3" in names else "free"

def classify_awg2_health(unit_probe, interface_probe, handshake_probe, now_epoch):
    if not all(probe_ok(probe) for probe in (unit_probe, interface_probe, handshake_probe)):
        return "stop"
    if unit_probe[1] != b"active\n" or not interface_probe[1]:
        return "stop"
    lines = handshake_probe[1].splitlines()
    if not lines:
        return "stop"
    timestamps = []
    for line in lines:
        match = HANDSHAKE_RE.fullmatch(line)
        if match is None:
            return "stop"
        timestamps.append(int(match.group(1)))
    return "pass" if any(0 < timestamp and 0 <= now_epoch - timestamp <= 600 for timestamp in timestamps) else "stop"

def observed(state, raw):
    if state not in STATES:
        raise ValueError("invalid observation state")
    if not isinstance(raw, bytes):
        raw = str(raw).encode("utf-8", errors="replace")
    if MAXIMUM_OUTPUT_BYTES + 1 < len(raw):
        return "stop", raw[:MAXIMUM_OUTPUT_BYTES + 1]
    return state, raw

def resource_path_state(path):
    candidate = pathlib.Path(path)
    try:
        os.lstat(candidate)
    except FileNotFoundError:
        return observed("free", "absent-exact")
    except OSError as exc:
        return observed("stop", type(exc).__name__)
    return observed("stop", "present")

def production_observations():
    values = {}
    os_release = pathlib.Path("/etc/os-release")
    try:
        os_raw = os_release.read_bytes()[:MAXIMUM_OUTPUT_BYTES + 1]
        os_ok = os.name == "posix" and os_release.is_file() and len(os_raw) <= MAXIMUM_OUTPUT_BYTES
    except OSError as exc:
        os_raw, os_ok = type(exc).__name__.encode("ascii"), False
    values["os_compatibility"] = observed("pass" if os_ok else "stop", os_raw)
    machine = os.uname().machine if hasattr(os, "uname") else "unknown"
    values["architecture"] = observed("pass" if machine in {"x86_64", "amd64"} else "stop", machine)
    py_probe = command(["python3.12", "--version"])
    values["python_3_12"] = observed("pass" if probe_ok(py_probe) and py_probe[1].startswith(b"Python 3.12.") else "stop", py_probe[1] + py_probe[2])
    try:
        free_bytes = shutil.disk_usage("/var/lib").free
        disk_state, disk_raw = ("pass" if 4 * 1024 * 1024 * 1024 <= free_bytes else "stop"), f"free-bytes:{free_bytes}"
    except OSError as exc:
        disk_state, disk_raw = "stop", type(exc).__name__
    values["disk_space"] = observed(disk_state, disk_raw)
    app_root = pathlib.Path("/opt/amn2")
    database = pathlib.Path("/var/lib/amn2/amn2.db")
    backup_root = pathlib.Path("/var/backups")
    values["application_state"] = observed("present" if app_root.is_dir() else "stop", f"directory:{app_root.is_dir()}")
    database_ok = database.is_file() and os.access(database, os.R_OK)
    values["database_state"] = observed("present" if database_ok else "stop", f"file-readable:{database_ok}")
    backup_ok = backup_root.is_dir() and os.access(backup_root, os.W_OK) and database_ok
    values["backup_capability"] = observed("pass" if backup_ok else "stop", f"backup-ready:{backup_ok}")
    systemd_probe = command(["systemctl", "is-system-running"])
    systemd_ok = probe_ok(systemd_probe) or (systemd_probe[0] == 1 and systemd_probe[3] == "command_failed")
    values["service_capability"] = observed("pass" if systemd_ok else "stop", systemd_probe[1] + systemd_probe[2])
    inventories = []
    for engine in ("docker", "podman"):
        if shutil.which(engine):
            inventories.append((engine, command([engine, "ps", "-a", "--format", "{{.Names}}"])))
    container_capability, container_name = classify_container_inventory(inventories)
    inventory_raw = b"\n".join(probe[1] + probe[2] for _engine, probe in inventories) or b"no-container-engine"
    values["container_capability"] = observed(container_capability, inventory_raw)
    values["container_name"] = observed(container_name, inventory_raw)
    awg_unit = command(["systemctl", "is-active", "amn2-spain-awg2.service"])
    awg_link = command(["ip", "link", "show", "awg2"])
    awg_tool = "awg" if shutil.which("awg") else ("wg" if shutil.which("wg") else None)
    awg_handshakes = command([awg_tool, "show", "awg2", "latest-handshakes"]) if awg_tool else (127, b"", b"", "unavailable")
    values["awg2_health"] = observed(classify_awg2_health(awg_unit, awg_link, awg_handshakes, int(time.time())), awg_unit[1] + awg_unit[2] + awg_link[1] + awg_link[2] + awg_handshakes[1] + awg_handshakes[2])
    telegram_probe = command(["systemctl", "is-active", "amn2-telegram.service"])
    values["telegram_prerequisites"] = observed("pass" if probe_ok(telegram_probe) and telegram_probe[1] == b"active\n" else "stop", telegram_probe[1] + telegram_probe[2])
    awg3_probe = command(["ip", "link", "show", "awg3"])
    bridge_probe = command(["ip", "link", "show", "amn2sp3br0"])
    values["interface_awg3"] = observed(classify_ip_link(awg3_probe, "awg3"), awg3_probe[1] + awg3_probe[2])
    values["bridge_amn2sp3br0"] = observed(classify_ip_link(bridge_probe, "amn2sp3br0"), bridge_probe[1] + bridge_probe[2])
    socket_probe = command(["ss", "-H", "-lun"])
    values["udp_30002"] = observed("free" if probe_ok(socket_probe) and b":30002" not in socket_probe[1] else "stop", socket_probe[1] + socket_probe[2])
    route_probe = command(["ip", "route", "show"])
    values["routes"] = observed("pass" if probe_ok(route_probe) else "stop", route_probe[1] + route_probe[2])
    values["vpn_cidr_10_212_13_0_24"] = observed("free" if probe_ok(route_probe) and b"10.212.13.0/24" not in route_probe[1] else "stop", route_probe[1] + route_probe[2])
    values["container_cidr_172_29_252_0_28"] = observed("free" if probe_ok(route_probe) and b"172.29.252.0/28" not in route_probe[1] else "stop", route_probe[1] + route_probe[2])
    nft_probe = command(["nft", "list", "ruleset"])
    firewall_probe = nft_probe if probe_ok(nft_probe) else command(["iptables", "-S"])
    values["firewall"] = observed("pass" if probe_ok(firewall_probe) and b"30002" not in firewall_probe[1] and b"awg3" not in firewall_probe[1] else "stop", firewall_probe[1] + firewall_probe[2])
    values["config_path"] = resource_path_state("/var/lib/amn2-spain/awg3/awg3.conf")
    values["state_root"] = resource_path_state("/var/lib/amn2-spain/awg3")
    service_probe = command(["systemctl", "show", "amn2-spain-awg3.service", "--property=LoadState", "--value"])
    values["service_name"] = observed("free" if probe_ok(service_probe) and service_probe[1] == b"not-found\n" else "stop", service_probe[1] + service_probe[2])
    markers = []
    marker_error = None
    try:
        for root in (pathlib.Path("/run/amn2-spain"), pathlib.Path("/var/lib/amn2-spain")):
            if root.is_dir():
                markers.extend(path for path in root.rglob("*") if path.is_file() and any(token in path.name.casefold() for token in ("incomplete", "recovery", "pending")))
    except OSError as exc:
        marker_error = type(exc).__name__
    marker_raw = marker_error or ("\n".join(sorted(str(path) for path in markers)) or "no-markers")
    values["recovery_markers_phase14_phase15"] = observed("stop" if marker_error or markers else "absent", marker_raw)
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
    claim_id = sys.argv[2]
    expected_host = sys.argv[3]
    package_id = sys.argv[1]
    if package_id != PACKAGE_ID or CLAIM_ID_RE.fullmatch(claim_id) is None or EXPECTED_HOST_RE.fullmatch(expected_host) is None:
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
    if raw_values["recovery_markers_phase14_phase15"][0] in {"stop", "unknown"}:
        reasons.append("recovery_incomplete")
    if any(raw_values[name][0] in {"stop", "unknown"} for name in CONFLICT_NAMES):
        reasons.append("resource_conflict")
    if any(state in {"stop", "unknown"} for name, (state, _raw) in raw_values.items() if name not in CONFLICT_NAMES and name != "recovery_markers_phase14_phase15"):
        reasons.append("observation_failed")
    document = {
        "blocking_reasons": sorted(set(reasons)),
        "claim_id": claim_id,
        "decision": "stop" if reasons else "pass",
        "host_identity": host_identity,
        "observed_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "observations": observations,
        "package_id": PACKAGE_ID,
        "safety": {"live_mutation": False, "raw_output_persisted": False, "remote_file_written": False},
        "schema": "amn2.phase15.spain-readonly-collector.v1",
    }
    sys.stdout.buffer.write(json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n")
except Exception as exc:
    sys.stderr.write("collector_failed:" + type(exc).__name__ + "\n")
    raise SystemExit(71)
' "$1" "$2" "$3"
