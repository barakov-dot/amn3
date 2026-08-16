#!/usr/bin/env bash
set -Eeuo pipefail

python_executable="${PHASE15_PYTHON:-python3}"
if [[ "$#" -ne 5 ]]; then
    "$python_executable" -c 'import sys; sys.stderr.buffer.write(b"collector_envelope_invalid\n")'
    exit 64
fi

exec "$python_executable" -c '
import datetime
import hashlib
import ipaddress
import json
import os
import pathlib
import re
import shlex
import shutil
import socket
import subprocess
import sys
import threading
import time

PACKAGE_ID = "phase15-dual-protocol-bootstrap-20260811-001"
CLAIM_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
EXPECTED_HOST_RE = re.compile(r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
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
    return probe[0] == 0 and probe[2] == b"" and probe[3] == "success"

def validate_envelope(package_id, manifest_sha256, collector_sha256, claim_id, expected_host):
    return (
        package_id == PACKAGE_ID
        and SHA256_RE.fullmatch(manifest_sha256) is not None
        and SHA256_RE.fullmatch(collector_sha256) is not None
        and CLAIM_ID_RE.fullmatch(claim_id) is not None
        and EXPECTED_HOST_RE.fullmatch(expected_host) is not None
    )

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
            raw = probe[1]
            if raw and (not raw.endswith(b"\n") or b"\r" in raw):
                return "stop", "stop"
            lines = raw.decode("utf-8", errors="strict").splitlines()
            if any(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", line) is None for line in lines):
                return "stop", "stop"
            names.extend(lines)
        except UnicodeDecodeError:
            return "stop", "stop"
    if len(names) != len(set(names)):
        return "stop", "stop"
    return "pass", "stop" if "amn2-spain-awg3" in names else "free"

def classify_systemd_capability(probe):
    if probe_ok(probe) and probe[1] == b"running\n" and probe[2] == b"":
        return "pass"
    if probe[0] == 1 and probe[1] == b"degraded\n" and probe[2] == b"" and probe[3] == "command_failed":
        return "pass"
    return "stop"

def classify_routes(probe):
    stopped = ("stop", "stop", "stop")
    if not probe_ok(probe) or probe[2] != b"":
        return stopped
    try:
        value = json.loads(probe[1].decode("utf-8", errors="strict"))
        if not isinstance(value, list):
            return stopped
        routes = []
        for item in value:
            if not isinstance(item, dict) or not isinstance(item.get("dst"), str):
                return stopped
            if item["dst"] != "default":
                routes.append(ipaddress.ip_network(item["dst"], strict=False))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError):
        return stopped
    vpn = ipaddress.ip_network("10.212.13.0/24")
    container = ipaddress.ip_network("172.29.252.0/28")
    return (
        "pass",
        "stop" if any(route.overlaps(vpn) for route in routes) else "free",
        "stop" if any(route.overlaps(container) for route in routes) else "free",
    )

def classify_udp_port(probe):
    if not probe_ok(probe) or probe[2] != b"":
        return "stop"
    try:
        lines = probe[1].decode("utf-8", errors="strict").splitlines()
    except UnicodeDecodeError:
        return "stop"
    if probe[1] and (not probe[1].endswith(b"\n") or b"\r" in probe[1]):
        return "stop"

    def endpoint_port(value, allow_wildcard):
        if value.startswith("["):
            closing = value.rfind("]:")
            if closing < 0:
                raise ValueError("endpoint")
            host, port_text = value[1:closing], value[closing + 2:]
            ipaddress.ip_address(host.split("%", 1)[0])
        else:
            host, separator, port_text = value.rpartition(":")
            if not separator or not host:
                raise ValueError("endpoint")
            if host != "*":
                ipaddress.ip_address(host.split("%", 1)[0])
        if allow_wildcard and port_text == "*":
            return None
        if re.fullmatch(r"[0-9]{1,5}", port_text) is None:
            raise ValueError("port")
        port = int(port_text)
        if not 0 <= port <= 65535:
            raise ValueError("port")
        return port

    for line in lines:
        match = re.fullmatch(r"UNCONN [0-9]+ [0-9]+ (\S+) (\S+)", line)
        if match is None:
            return "stop"
        try:
            port = endpoint_port(match.group(1), False)
            endpoint_port(match.group(2), True)
        except ValueError:
            return "stop"
        if port == 30002:
            return "stop"
    return "free"

FIREWALL_ENTRY_TYPES = {
    "chain", "counter", "ct helper", "element", "flowtable", "limit", "map",
    "metainfo", "quota", "rule", "set", "synproxy", "table",
}
TARGET_NETWORKS = (
    ipaddress.ip_network("10.212.13.0/24"),
    ipaddress.ip_network("172.29.252.0/28"),
)

def _port_spec_conflicts(value):
    if not isinstance(value, str) or not value:
        raise ValueError("port specification")
    for part in value.split(","):
        match = re.fullmatch(r"([0-9]{1,5})(?:[:-]([0-9]{1,5}))?", part)
        if match is None:
            raise ValueError("port specification")
        first = int(match.group(1))
        last = int(match.group(2) or match.group(1))
        if not (0 <= first <= last <= 65535):
            raise ValueError("port specification")
        if first <= 30002 <= last:
            return True
    return False

def _network_conflicts(value):
    try:
        network = ipaddress.ip_network(value, strict=False)
    except ValueError as exc:
        raise ValueError("network specification") from exc
    return any(network.version == target.version and network.overlaps(target) for target in TARGET_NETWORKS)

def _has_firewall_conflict(value, context=None):
    if isinstance(value, bool) or value is None:
        return False
    if isinstance(value, int):
        if not 0 <= value <= 65535:
            raise ValueError("integer range")
        return value == 30002
    if isinstance(value, str):
        if value in {"awg3", "amn2sp3br0"}:
            return True
        if context in {"dport", "sport", "port", "range"} or re.fullmatch(r"[0-9]{1,5}(?:[:-][0-9]{1,5})?(?:,[0-9]{1,5}(?:[:-][0-9]{1,5})?)*", value):
            return _port_spec_conflicts(value)
        if "/" in value:
            return _network_conflicts(value)
        return False
    if isinstance(value, list):
        if context == "range":
            if len(value) != 2 or any(isinstance(item, bool) or not isinstance(item, int) for item in value):
                raise ValueError("firewall range")
            first, last = value
            if not 0 <= first <= last <= 65535:
                raise ValueError("firewall range")
            return first <= 30002 <= last
        return any(_has_firewall_conflict(item) for item in value)
    if isinstance(value, dict):
        if "prefix" in value:
            if set(value) != {"prefix"} or not isinstance(value["prefix"], dict) or set(value["prefix"]) != {"addr", "len"}:
                raise ValueError("firewall prefix")
            address = value["prefix"]["addr"]
            length = value["prefix"]["len"]
            if not isinstance(address, str) or isinstance(length, bool) or not isinstance(length, int):
                raise ValueError("firewall prefix")
            return _network_conflicts(f"{address}/{length}")
        return any(isinstance(key, str) and _has_firewall_conflict(item, key) for key, item in value.items())
    raise ValueError("firewall value")

def _parse_iptables_save(raw):
    text = raw.decode("utf-8", errors="strict")
    if not text or "\r" in text or not text.endswith("\n"):
        raise ValueError("iptables canonical text")
    conflict = False
    in_table = False
    for line in text.splitlines():
        if re.fullmatch(r"#[\x20-\x7e]*", line):
            continue
        if re.fullmatch(r"\*[a-z0-9_-]+", line):
            if in_table:
                raise ValueError("iptables table nesting")
            in_table = True
            continue
        if re.fullmatch(r":[A-Za-z0-9_-]+ (?:ACCEPT|DROP|REJECT|-) \[[0-9]+:[0-9]+\]", line):
            if not in_table:
                raise ValueError("iptables chain placement")
            continue
        if line == "COMMIT":
            if not in_table:
                raise ValueError("iptables commit placement")
            in_table = False
            continue
        if not line.startswith("-A ") or not in_table:
            raise ValueError("iptables syntax")
        tokens = shlex.split(line, posix=True)
        if len(tokens) < 2 or tokens[0] != "-A" or re.fullmatch(r"[A-Za-z0-9_-]+", tokens[1]) is None:
            raise ValueError("iptables rule")
        single = {
            "-p", "--protocol", "-s", "--source", "-d", "--destination", "-i", "--in-interface",
            "-o", "--out-interface", "-j", "--jump", "-g", "--goto", "-m", "--match", "--sport",
            "--source-port", "--dport", "--destination-port", "--sports", "--source-ports", "--dports",
            "--destination-ports", "--ctstate", "--state", "--comment", "--icmp-type",
        }
        zero = {"!", "-f", "--fragment", "--syn"}
        index = 2
        while index < len(tokens):
            option = tokens[index]
            if option in zero:
                index += 1
                continue
            if option not in single or not index + 1 < len(tokens) or tokens[index + 1].startswith("-"):
                raise ValueError("iptables option")
            argument = tokens[index + 1]
            if option in {"-i", "--in-interface", "-o", "--out-interface"}:
                if re.fullmatch(r"[A-Za-z0-9_.+-]{1,64}", argument) is None:
                    raise ValueError("iptables interface")
                conflict = conflict or argument in {"awg3", "amn2sp3br0"}
            elif option in {"-s", "--source", "-d", "--destination"}:
                conflict = conflict or _network_conflicts(argument)
            elif option in {"--sport", "--source-port", "--dport", "--destination-port", "--sports", "--source-ports", "--dports", "--destination-ports"}:
                conflict = conflict or _port_spec_conflicts(argument)
            index += 2
    if in_table:
        raise ValueError("iptables missing commit")
    return conflict

def classify_firewall(nft_probe, iptables_probe):
    if nft_probe[3] == "unavailable":
        if iptables_probe is None or not probe_ok(iptables_probe) or iptables_probe[2] != b"":
            return "stop"
        try:
            return "stop" if _parse_iptables_save(iptables_probe[1]) else "pass"
        except (UnicodeDecodeError, ValueError):
            return "stop"
    if not probe_ok(nft_probe) or nft_probe[2] != b"":
        return "stop"
    try:
        if not nft_probe[1].endswith(b"\n") or b"\r" in nft_probe[1]:
            return "stop"
        def reject_duplicates(pairs):
            result = {}
            for key, item in pairs:
                if key in result:
                    raise ValueError("duplicate nft key")
                result[key] = item
            return result
        value = json.loads(nft_probe[1].decode("utf-8", errors="strict"), object_pairs_hook=reject_duplicates)
        if not isinstance(value, dict) or set(value) != {"nftables"} or not isinstance(value["nftables"], list):
            return "stop"
        for entry in value["nftables"]:
            if not isinstance(entry, dict) or len(entry) != 1:
                return "stop"
            entry_type, payload = next(iter(entry.items()))
            if entry_type not in FIREWALL_ENTRY_TYPES or not isinstance(payload, dict):
                return "stop"
        return "stop" if _has_firewall_conflict(value["nftables"]) else "pass"
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError):
        return "stop"

def classify_awg2_health(unit_probe, interface_probe, handshake_probe, now_epoch):
    if not all(probe_ok(probe) for probe in (unit_probe, interface_probe, handshake_probe)):
        return "stop"
    if unit_probe[1] != b"active\n" or re.fullmatch(rb"[0-9]+: awg2(?:@[^: \n]+)?: <[A-Z0-9_,]+\x3e(?: [^\r\n]*)?\n(?:    [^\r\n]+\n)*", interface_probe[1]) is None:
        return "stop"
    if not handshake_probe[1].endswith(b"\n") or b"\r" in handshake_probe[1]:
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

def classify_service_absence(probe):
    return "free" if probe_ok(probe) and probe[1] == b"not-found\n" else "stop"

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
    values["service_capability"] = observed(classify_systemd_capability(systemd_probe), systemd_probe[1] + systemd_probe[2])
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
    values["udp_30002"] = observed(classify_udp_port(socket_probe), socket_probe[1] + socket_probe[2])
    route_probe = command(["ip", "-j", "route", "show", "table", "all"])
    route_state, vpn_state, container_cidr_state = classify_routes(route_probe)
    values["routes"] = observed(route_state, route_probe[1] + route_probe[2])
    values["vpn_cidr_10_212_13_0_24"] = observed(vpn_state, route_probe[1] + route_probe[2])
    values["container_cidr_172_29_252_0_28"] = observed(container_cidr_state, route_probe[1] + route_probe[2])
    nft_probe = command(["nft", "-j", "list", "ruleset"])
    iptables_probe = command(["iptables-save"]) if nft_probe[3] == "unavailable" else None
    firewall_raw = nft_probe[1] + nft_probe[2] + ((iptables_probe[1] + iptables_probe[2]) if iptables_probe else b"")
    values["firewall"] = observed(classify_firewall(nft_probe, iptables_probe), firewall_raw)
    values["config_path"] = resource_path_state("/var/lib/amn2-spain/awg3/awg3.conf")
    values["state_root"] = resource_path_state("/var/lib/amn2-spain/awg3")
    service_probe = command(["systemctl", "show", "amn2-spain-awg3.service", "--property=LoadState", "--value"])
    values["service_name"] = observed(classify_service_absence(service_probe), service_probe[1] + service_probe[2])
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

def build_document(*, package_id, manifest_sha256, collector_sha256, claim_id, expected_host, host_identity, raw_values, observed_at):
    if not validate_envelope(package_id, manifest_sha256, collector_sha256, claim_id, expected_host):
        raise ValueError("preflight identity binding")
    if not isinstance(host_identity, str) or set(raw_values) != EXPECTED_NAMES:
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
    return {
        "blocking_reasons": sorted(set(reasons)),
        "claim_id": claim_id,
        "collector_sha256": collector_sha256,
        "decision": "stop" if reasons else "pass",
        "host_identity": host_identity,
        "manifest_sha256": manifest_sha256,
        "observed_at": observed_at,
        "observations": observations,
        "package_id": package_id,
        "safety": {"live_mutation": False, "raw_output_persisted": False, "remote_file_written": False},
        "schema": "amn2.phase15.spain-readonly-collector.v1",
    }

try:
    claim_id = sys.argv[4]
    package_id = sys.argv[1]
    manifest_sha256 = sys.argv[2]
    collector_sha256 = sys.argv[3]
    expected_host = sys.argv[5]
    if not validate_envelope(package_id, manifest_sha256, collector_sha256, claim_id, expected_host):
        raise ValueError("preflight identity binding")
    host_identity, raw_values = production_observations()
    document = build_document(package_id=package_id, manifest_sha256=manifest_sha256, collector_sha256=collector_sha256, claim_id=claim_id, expected_host=expected_host, host_identity=host_identity, raw_values=raw_values, observed_at=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    sys.stdout.buffer.write(json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n")
except Exception as exc:
    sys.stderr.write("collector_failed:" + type(exc).__name__ + "\n")
    raise SystemExit(71)
' "$1" "$2" "$3" "$4" "$5"
