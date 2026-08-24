#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "$#" -ne 5 ]]; then
    /usr/bin/python3 -I -B -c 'import sys; sys.stderr.buffer.write(b"collector_envelope_invalid\n")'
    exit 64
fi

exec /usr/bin/python3 -I -B - "$1" "$2" "$3" "$4" "$5" <<'PHASE16_PY'
import datetime
import hashlib
import ipaddress
import json
import os
import pathlib
import re
import shlex
import shutil
import stat
import subprocess
import sys
import threading
import time

PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-003"
CURRENT_APPLICATION_ROOT = "/opt/amn2-spain"
CURRENT_DATABASE_PATH = "/var/lib/amn2-spain/amn2.sqlite3"
CURRENT_AWG2_CONTAINER = "amn2-spain-awg"
CURRENT_AWG2_INTERFACE = "awg0"
CURRENT_AWG2_OWNER_UNIT = "amn2-spain-docker.service"
CURRENT_BOT_UNIT = "amn2-spain-bot.service"
SYSTEM_DOCKER = "/usr/bin/docker"
SYSTEM_DOCKER_HOST = "unix:///var/run/docker.sock"
SPAIN_DOCKER = "/opt/amn2-spain/docker/bin/docker"
SPAIN_DOCKER_HOST = "unix:///run/amn2-spain-docker/docker.sock"
PODMAN = "/usr/bin/podman"
PODMAN_HOST = "unix:///run/podman/podman.sock"
SYSTEMCTL = "/usr/bin/systemctl"
IP = "/usr/sbin/ip"
NSENTER = "/usr/bin/nsenter"
SS = "/usr/bin/ss"
NFT = "/usr/sbin/nft"
IPTABLES_SAVE = "/usr/sbin/iptables-save"
IPTABLES_LEGACY_SAVE = "/usr/sbin/iptables-legacy-save"
HOSTNAME = "/usr/bin/hostname"
PYTHON_3_12 = "/usr/bin/python3"
ALLOWED_COMMANDS = {
    HOSTNAME, IP, IPTABLES_LEGACY_SAVE, IPTABLES_SAVE, NFT, NSENTER, PODMAN,
    PYTHON_3_12, SPAIN_DOCKER, SS, SYSTEMCTL, SYSTEM_DOCKER,
}
CLAIM_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
EXPECTED_HOST_RE = re.compile(r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
HANDSHAKE_RE = re.compile(rb"^[A-Za-z0-9+/]{43}=\t([0-9]+)$")
MAXIMUM_OUTPUT_BYTES = 65536
MAX_CONTAINER_ROWS = 512
MAX_NETWORK_IDS = 256
MAX_RECOVERY_ENTRIES = 4096
MAX_COMMAND_INVOCATIONS = 96
COLLECTOR_WORK_SECONDS = 45
_collector_deadline = time.monotonic() + COLLECTOR_WORK_SECONDS
_command_invocations = 0
EXPECTED_NAMES = {
    "application_state", "architecture", "awg2_health", "backup_capability",
    "bridge_amn2sp3br0", "config_path", "container_capability",
    "container_cidr_172_29_252_0_28", "container_name", "database_state",
    "disk_space", "firewall", "interface_awg3", "os_compatibility", "python_3_12",
    "recovery_markers_phase14_phase15_phase16", "routes", "service_capability", "service_name",
    "state_root", "telegram_prerequisites", "udp_30002", "vpn_cidr_10_212_13_0_24",
}
STATES = {"absent", "free", "pass", "present", "stop", "unknown"}
CONFLICT_NAMES = {
    "bridge_amn2sp3br0", "config_path", "container_cidr_172_29_252_0_28",
    "container_name", "firewall", "interface_awg3", "routes", "service_name",
    "state_root", "udp_30002", "vpn_cidr_10_212_13_0_24",
}

def ensure_work_budget():
    if _collector_deadline <= time.monotonic():
        raise TimeoutError("collector work budget exceeded")

def bounded_file_bytes(path, maximum_bytes=MAXIMUM_OUTPUT_BYTES):
    ensure_work_budget()
    candidate = pathlib.Path(path)
    stat_result = candidate.lstat()
    if not stat.S_ISREG(stat_result.st_mode) or candidate.is_symlink():
        raise OSError("input is not a regular file")
    if stat_result.st_size < 1:
        raise OSError("input size rejected")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(candidate, flags)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or (stat_result.st_dev, stat_result.st_ino) != (opened.st_dev, opened.st_ino):
            raise OSError("input identity rejected")
        chunks = bytearray()
        while len(chunks) < maximum_bytes + 1:
            chunk = os.read(descriptor, min(4096, maximum_bytes + 1 - len(chunks)))
            if not chunk:
                break
            chunks.extend(chunk)
        raw = bytes(chunks)
    finally:
        os.close(descriptor)
    ensure_work_budget()
    if not raw or maximum_bytes < len(raw):
        raise OSError("input size rejected")
    return raw

def bounded_os_release_bytes(etc_path="/etc/os-release", canonical_path="/usr/lib/os-release"):
    ensure_work_budget()
    link = pathlib.Path(etc_path)
    canonical = pathlib.Path(canonical_path)
    link_stat = link.lstat()
    if not stat.S_ISLNK(link_stat.st_mode):
        raise OSError("os release link rejected")
    link_target = os.readlink(link)
    if link_target != "../usr/lib/os-release":
        raise OSError("os release target rejected")
    lexical_target = pathlib.Path(os.path.abspath(os.path.join(str(link.parent), link_target)))
    canonical_target = pathlib.Path(os.path.abspath(str(canonical)))
    if os.path.normcase(str(lexical_target)) != os.path.normcase(str(canonical_target)):
        raise OSError("os release target rejected")
    for directory in (canonical_target.parent.parent, canonical_target.parent):
        directory_stat = directory.lstat()
        if not stat.S_ISDIR(directory_stat.st_mode) or directory.is_symlink():
            raise OSError("os release parent rejected")
    target_stat = canonical_target.lstat()
    if not stat.S_ISREG(target_stat.st_mode) or canonical_target.is_symlink():
        raise OSError("os release target rejected")
    return bounded_file_bytes(canonical_target)

def command(parts, maximum_output_bytes=MAXIMUM_OUTPUT_BYTES, timeout_seconds=8):
    global _command_invocations
    remaining_budget = _collector_deadline - time.monotonic()
    if remaining_budget <= 0 or MAX_COMMAND_INVOCATIONS <= _command_invocations:
        return 124, b"", b"", "work_budget_exceeded"
    _command_invocations += 1
    timeout_seconds = min(timeout_seconds, remaining_budget)
    environment = {
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": "/root",
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": "/usr/sbin:/usr/bin",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "PYTHONSAFEPATH": "1",
    }
    try:
        if not parts or not isinstance(parts[0], str) or parts[0] not in ALLOWED_COMMANDS:
            return 126, b"", b"", "launch_failed"
        process = subprocess.Popen(parts, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment, cwd="/")
    except FileNotFoundError:
        return 127, b"", b"", "unavailable"
    except OSError:
        return 126, b"", b"", "launch_failed"
    overflow = threading.Event()
    outputs = [bytearray(), bytearray()]
    reader_errors = []
    reader_eof = [False, False]

    def read_bounded(stream, output, index):
        try:
            while True:
                chunk = stream.read(4096)
                if not chunk:
                    reader_eof[index] = True
                    return
                remaining = maximum_output_bytes + 1 - len(output)
                if 0 < remaining:
                    output.extend(chunk[:remaining])
                if maximum_output_bytes < len(output):
                    overflow.set()
                    return
        except Exception as exc:
            reader_errors.append(type(exc).__name__)
        finally:
            stream.close()

    threads = [
        threading.Thread(target=read_bounded, args=(process.stdout, outputs[0], 0), daemon=True),
        threading.Thread(target=read_bounded, args=(process.stderr, outputs[1], 1), daemon=True),
    ]
    for thread in threads:
        thread.start()
    deadline = min(time.monotonic() + timeout_seconds, _collector_deadline)
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
        try:
            return_code = process.wait(timeout=1)
            disposition = "timeout"
        except subprocess.TimeoutExpired:
            return_code = 124
            disposition = "incomplete_output"
    for thread in threads:
        thread.join(timeout=1)
    if overflow.is_set():
        disposition = "output_oversized"
        if return_code == 0:
            return_code = 125
    elif reader_errors or any(thread.is_alive() for thread in threads) or not all(reader_eof):
        disposition = "incomplete_output"
        if process.poll() is None:
            process.kill()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
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
            if MAX_CONTAINER_ROWS < len(names) + len(lines):
                return "stop", "stop"
            if any(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", line) is None for line in lines):
                return "stop", "stop"
            names.extend(lines)
        except UnicodeDecodeError:
            return "stop", "stop"
    if len(names) != len(set(names)):
        return "stop", "stop"
    return "pass", "stop" if "amn2-spain-awg3" in names else "free"

def current_spain_identity():
    return {
        "application_root": CURRENT_APPLICATION_ROOT,
        "bot_unit": CURRENT_BOT_UNIT,
        "container": CURRENT_AWG2_CONTAINER,
        "database_path": CURRENT_DATABASE_PATH,
        "docker_host": SPAIN_DOCKER_HOST,
        "interface": CURRENT_AWG2_INTERFACE,
    }

def _docker_network_ids(probe):
    if not probe_ok(probe):
        raise ValueError("docker network inventory")
    raw = probe[1]
    if raw and (not raw.endswith(b"\n") or b"\r" in raw):
        raise ValueError("docker network inventory")
    identifiers = raw.decode("ascii", errors="strict").splitlines()
    if MAX_NETWORK_IDS < len(identifiers):
        raise ValueError("network inventory limit")
    if any(re.fullmatch(r"[0-9a-f]{64}", item) is None for item in identifiers) or len(identifiers) != len(set(identifiers)):
        raise ValueError("docker network inventory")
    return identifiers

def _strict_json(text):
    def reject_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate json key")
            result[key] = value
        return result
    return json.loads(
        text,
        object_pairs_hook=reject_duplicates,
        parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite json value")),
    )

def _parse_network_inspection(probe):
    if not probe_ok(probe):
        raise ValueError("network inspection")
    raw = probe[1]
    if not raw or not raw.endswith(b"\n") or raw.count(b"\n") != 1 or b"\r" in raw:
        raise ValueError("network inspection")
    fields = raw[:-1].decode("utf-8", errors="strict").split("\t")
    if len(fields) != 3:
        raise ValueError("network inspection")
    name, driver, address_data = (_strict_json(field) for field in fields)
    if not isinstance(name, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", name) is None:
        raise ValueError("network name")
    if not isinstance(driver, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", driver) is None:
        raise ValueError("network driver")
    subnets = []
    if isinstance(address_data, dict):
        if set(address_data) != {"Config", "Driver", "Options"}:
            raise ValueError("docker ipam schema")
        if not isinstance(address_data["Driver"], str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", address_data["Driver"]) is None:
            raise ValueError("docker ipam driver")
        if address_data["Options"] is not None and (not isinstance(address_data["Options"], dict) or any(not isinstance(key, str) or not isinstance(value, str) for key, value in address_data["Options"].items())):
            raise ValueError("docker ipam options")
        config = address_data["Config"]
        if not isinstance(config, list):
            raise ValueError("docker ipam config")
        for item in config:
            allowed = {"AuxiliaryAddresses", "Gateway", "IPRange", "Subnet"}
            if not isinstance(item, dict) or "Subnet" not in item or not set(item).issubset(allowed):
                raise ValueError("docker ipam entry")
            if not isinstance(item["Subnet"], str):
                raise ValueError("docker subnet")
            subnets.append(ipaddress.ip_network(item["Subnet"], strict=False))
            for field in ("Gateway", "IPRange"):
                if field in item and not isinstance(item[field], str):
                    raise ValueError("docker ipam value")
            if "AuxiliaryAddresses" in item and (not isinstance(item["AuxiliaryAddresses"], dict) or any(not isinstance(key, str) or not isinstance(value, str) for key, value in item["AuxiliaryAddresses"].items())):
                raise ValueError("docker auxiliary addresses")
    elif isinstance(address_data, list):
        for item in address_data:
            if not isinstance(item, dict) or set(item) - {"gateway", "lease_range", "subnet"} or not isinstance(item.get("subnet"), str):
                raise ValueError("podman subnet schema")
            subnets.append(ipaddress.ip_network(item["subnet"], strict=False))
    else:
        raise ValueError("network address schema")
    if not subnets and not (name == "none" and driver == "null" and isinstance(address_data, dict)):
        raise ValueError("empty network ipam")
    return name, driver, subnets

def classify_dedicated_spain_docker(inventory_probe, network_list_probe, network_inspect_probes):
    stopped = ("stop", "stop", "stop")
    try:
        capability, candidate_name = classify_container_inventory([("spain-docker", inventory_probe)])
        identifiers = _docker_network_ids(network_list_probe)
        if capability != "pass" or len(network_inspect_probes) != len(identifiers):
            return stopped
        networks = []
        for probe in network_inspect_probes:
            _name, _driver, subnets = _parse_network_inspection(probe)
            networks.extend(subnets)
        target = ipaddress.ip_network("172.29.252.0/28")
        cidr_state = "stop" if any(network.version == target.version and network.overlaps(target) for network in networks) else "free"
        return capability, candidate_name, cidr_state
    except (UnicodeDecodeError, ValueError, TypeError):
        return stopped

def classify_spain_docker_sources(system_source, dedicated_source, podman_source):
    stopped = ("stop", "stop", "stop")
    try:
        present_sources = [system_source, dedicated_source]
        if podman_source[0][3] != "unavailable":
            present_sources.append(podman_source)
        total_containers = 0
        total_networks = 0
        for inventory_probe, network_probe, inspect_probes in present_sources:
            if network_probe is None:
                return stopped
            if not probe_ok(inventory_probe):
                return stopped
            total_containers += len(inventory_probe[1].decode("utf-8", errors="strict").splitlines())
            total_networks += len(_docker_network_ids(network_probe))
            if MAX_CONTAINER_ROWS < total_containers or MAX_NETWORK_IDS < total_networks or len(inspect_probes) != len(_docker_network_ids(network_probe)):
                return stopped
    except (UnicodeDecodeError, ValueError, TypeError):
        return stopped
    system_inventory, system_networks, system_inspects = system_source
    if system_networks is None:
        return stopped
    system_result = classify_dedicated_spain_docker(system_inventory, system_networks, system_inspects)
    dedicated_inventory, dedicated_networks, dedicated_inspects = dedicated_source
    if dedicated_networks is None:
        return stopped
    dedicated_result = classify_dedicated_spain_docker(dedicated_inventory, dedicated_networks, dedicated_inspects)
    podman_inventory, podman_networks, podman_inspects = podman_source
    if podman_inventory[3] == "unavailable":
        if podman_networks is not None or podman_inspects:
            return stopped
        podman_result = ("absent", "free", "free")
    else:
        if podman_networks is None:
            return stopped
        podman_result = classify_dedicated_spain_docker(podman_inventory, podman_networks, podman_inspects)
    if system_result[0] != "pass" or dedicated_result[0] != "pass" or podman_result[0] == "stop":
        return stopped
    return (
        "pass",
        "stop" if "stop" in {system_result[1], dedicated_result[1], podman_result[1]} else "free",
        "stop" if "stop" in {system_result[2], dedicated_result[2], podman_result[2]} else "free",
    )

def production_container_source(engine):
    if engine == "system-docker":
        prefix = [SYSTEM_DOCKER, "--host", SYSTEM_DOCKER_HOST]
        inspect_format = "{{json .Name}}\t{{json .Driver}}\t{{json .IPAM}}"
    elif engine == "spain-docker":
        prefix = [SPAIN_DOCKER, "--host", SPAIN_DOCKER_HOST]
        inspect_format = "{{json .Name}}\t{{json .Driver}}\t{{json .IPAM}}"
    elif engine == "podman":
        prefix = [PODMAN, "--url", PODMAN_HOST]
        inspect_format = "{{json .Name}}\t{{json .Driver}}\t{{json .Subnets}}"
    else:
        raise ValueError("container engine")
    inventory = command(prefix + ["ps", "-a", "--format", "{{.Names}}"])
    if inventory[3] == "unavailable":
        return inventory, None, []
    networks = command(prefix + ["network", "ls", "-q", "--no-trunc"])
    try:
        identifiers = _docker_network_ids(networks)
    except (UnicodeDecodeError, ValueError):
        return inventory, networks, []
    inspections = []
    for network_id in identifiers:
        ensure_work_budget()
        inspections.append(command(prefix + ["network", "inspect", "--format", inspect_format, network_id]))
    return inventory, networks, inspections

def classify_systemd_capability(probe):
    if probe_ok(probe) and probe[1] == b"running\n" and probe[2] == b"":
        return "pass"
    if probe[0] == 1 and probe[1] == b"degraded\n" and probe[2] == b"" and probe[3] == "command_failed":
        return "pass"
    return "stop"

def classify_phase13_bot_unit(active_probe, enabled_probe):
    return "pass" if probe_ok(active_probe) and probe_ok(enabled_probe) and active_probe[1] == b"inactive\n" and enabled_probe[1] == b"disabled\n" else "stop"

def classify_routes(probe):
    stopped = ("stop", "stop", "stop")
    if not probe_ok(probe) or probe[2] != b"":
        return stopped
    try:
        raw = probe[1]
        if not raw or not raw.endswith(b"\n") or raw.count(b"\n") != 1 or b"\r" in raw:
            return stopped
        text = raw[:-1].decode("utf-8", errors="strict")
        if text.encode("utf-8") != raw[:-1]:
            return stopped
        def reject_duplicates(pairs):
            result = {}
            for key, item in pairs:
                if key in result:
                    raise ValueError("duplicate route key")
                result[key] = item
            return result
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicates,
            parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite route value")),
        )
        if not isinstance(value, list):
            return stopped
        allowed_keys = {"dev", "dst", "flags", "gateway", "metric", "prefsrc", "protocol", "scope", "src", "table", "type"}
        routes = []
        for item in value:
            if not isinstance(item, dict) or not item or not set(item).issubset(allowed_keys) or not isinstance(item.get("dst"), str):
                return stopped
            if any(isinstance(entry, (dict, list)) for entry in item.values() if entry is not item.get("flags")):
                return stopped
            if "flags" in item and (not isinstance(item["flags"], list) or any(not isinstance(flag, str) for flag in item["flags"])):
                return stopped
            if "dev" in item and (not isinstance(item["dev"], str) or re.fullmatch(r"[A-Za-z0-9_.:+-]{1,64}", item["dev"]) is None):
                return stopped
            if "metric" in item and (isinstance(item["metric"], bool) or not isinstance(item["metric"], int) or not 0 <= item["metric"] <= 4294967295):
                return stopped
            for address_field in ("gateway", "prefsrc", "src"):
                if address_field in item:
                    if not isinstance(item[address_field], str):
                        return stopped
                    ipaddress.ip_address(item[address_field])
            if "scope" in item and item["scope"] not in {"global", "host", "link", "nowhere", "universe"}:
                return stopped
            if "type" in item and item["type"] not in {"anycast", "blackhole", "broadcast", "local", "multicast", "nat", "prohibit", "throw", "unicast", "unreachable"}:
                return stopped
            if "protocol" in item and not (
                isinstance(item["protocol"], str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,32}", item["protocol"]) is not None
                or not isinstance(item["protocol"], bool) and isinstance(item["protocol"], int) and 0 <= item["protocol"] <= 255
            ):
                return stopped
            if "table" in item and not (
                isinstance(item["table"], str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,32}", item["table"]) is not None
                or not isinstance(item["table"], bool) and isinstance(item["table"], int) and 0 <= item["table"] <= 4294967295
            ):
                return stopped
            if "flags" in item and any(re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", flag) is None for flag in item["flags"]):
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
        match = re.fullmatch(r"UNCONN[ ]+[0-9]+[ ]+[0-9]+[ ]+(\S+)[ ]+(\S+)", line)
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

def _nft_scalar_conflict(value, context):
    if context in {"dport", "sport"}:
        if isinstance(value, bool):
            raise ValueError("nft port")
        if isinstance(value, int):
            if not 0 <= value <= 65535:
                raise ValueError("nft port")
            return value == 30002
        if isinstance(value, str):
            return _port_spec_conflicts(value)
        if isinstance(value, dict) and set(value) == {"range"}:
            interval = value["range"]
            if not isinstance(interval, list) or len(interval) != 2 or any(isinstance(item, bool) or not isinstance(item, int) for item in interval):
                raise ValueError("nft port range")
            first, last = interval
            if not 0 <= first <= last <= 65535:
                raise ValueError("nft port range")
            return first <= 30002 <= last
        raise ValueError("nft port")
    if context in {"saddr", "daddr"}:
        if isinstance(value, str):
            try:
                address = ipaddress.ip_address(value)
                return any(address.version == target.version and address in target for target in TARGET_NETWORKS)
            except ValueError:
                return _network_conflicts(value)
        if isinstance(value, dict) and set(value) == {"prefix"}:
            prefix = value["prefix"]
            if not isinstance(prefix, dict) or set(prefix) != {"addr", "len"} or not isinstance(prefix["addr"], str) or isinstance(prefix["len"], bool) or not isinstance(prefix["len"], int):
                raise ValueError("nft prefix")
            return _network_conflicts(f"{prefix['addr']}/{prefix['len']}")
        raise ValueError("nft network")
    if context in {"iifname", "oifname"}:
        if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9_.+-]{1,64}", value) is None:
            raise ValueError("nft interface")
        return value in {"awg3", "amn2sp3br0"}
    if isinstance(value, (str, int, bool)) or value is None:
        return False
    raise ValueError("nft scalar")

def _parse_nft_expression(expression):
    if not isinstance(expression, dict) or len(expression) != 1:
        raise ValueError("nft expression")
    kind, payload = next(iter(expression.items()))
    if kind == "counter":
        if not isinstance(payload, dict) or set(payload) != {"bytes", "packets"}:
            raise ValueError("nft counter")
        if any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in payload.values()):
            raise ValueError("nft counter")
        return False
    if kind == "match":
        if not isinstance(payload, dict) or set(payload) != {"left", "op", "right"} or payload["op"] not in {"==", "in"}:
            raise ValueError("nft match")
        left = payload["left"]
        if not isinstance(left, dict) or len(left) != 1:
            raise ValueError("nft left")
        left_kind, descriptor = next(iter(left.items()))
        if left_kind == "payload":
            if not isinstance(descriptor, dict) or set(descriptor) != {"field", "protocol"} or not isinstance(descriptor["field"], str) or not isinstance(descriptor["protocol"], str):
                raise ValueError("nft payload")
            context = descriptor["field"]
            if context not in {"dport", "sport", "saddr", "daddr"}:
                raise ValueError("nft payload field")
            if context in {"dport", "sport"} and descriptor["protocol"] not in {"tcp", "udp"}:
                raise ValueError("nft port protocol")
            if context in {"saddr", "daddr"} and descriptor["protocol"] not in {"ip", "ip6"}:
                raise ValueError("nft network protocol")
        elif left_kind == "meta":
            if not isinstance(descriptor, dict) or set(descriptor) != {"key"} or descriptor["key"] not in {"iifname", "oifname"}:
                raise ValueError("nft meta")
            context = descriptor["key"]
        else:
            raise ValueError("nft left kind")
        return _nft_scalar_conflict(payload["right"], context)
    if kind in {"accept", "continue", "drop", "return"}:
        if payload is not None:
            raise ValueError("nft verdict")
        return False
    if kind in {"jump", "goto"}:
        if not isinstance(payload, dict) or set(payload) != {"target"} or re.fullmatch(r"[A-Za-z0-9_.+-]{1,64}", payload["target"] or "") is None:
            raise ValueError("nft jump")
        return False
    raise ValueError("nft expression kind")

def _parse_nft_entry(entry):
    if not isinstance(entry, dict) or len(entry) != 1:
        raise ValueError("nft entry")
    entry_type, payload = next(iter(entry.items()))
    if entry_type not in FIREWALL_ENTRY_TYPES or not isinstance(payload, dict):
        raise ValueError("nft entry type")
    common = {"family", "handle", "name", "table"}
    def validate_common(value, required):
        if not required.issubset(value):
            raise ValueError("nft required fields")
        if "family" in value and value["family"] not in {"arp", "bridge", "inet", "ip", "ip6", "netdev"}:
            raise ValueError("nft family")
        for field in ("name", "table", "chain"):
            if field in value and (not isinstance(value[field], str) or re.fullmatch(r"[A-Za-z0-9_.+-]{1,64}", value[field]) is None):
                raise ValueError("nft name")
        if "handle" in value and (isinstance(value["handle"], bool) or not isinstance(value["handle"], int) or value["handle"] < 0):
            raise ValueError("nft handle")
    if entry_type == "metainfo":
        if not set(payload).issubset({"json_schema_version", "release_name", "version"}):
            raise ValueError("nft metainfo")
        if any(not isinstance(item, str) for item in payload.values()):
            raise ValueError("nft metainfo")
        return False
    if entry_type == "table":
        if not set(payload).issubset(common) or not {"family", "name"}.issubset(payload):
            raise ValueError("nft table")
        validate_common(payload, {"family", "name"})
        return False
    if entry_type == "chain":
        if not set(payload).issubset(common | {"hook", "policy", "prio", "type"}) or not {"family", "name", "table"}.issubset(payload):
            raise ValueError("nft chain")
        validate_common(payload, {"family", "name", "table"})
        if "hook" in payload and payload["hook"] not in {"egress", "forward", "ingress", "input", "output", "postrouting", "prerouting"}:
            raise ValueError("nft hook")
        if "policy" in payload and payload["policy"] not in {"accept", "drop"}:
            raise ValueError("nft policy")
        if "prio" in payload and (isinstance(payload["prio"], bool) or not isinstance(payload["prio"], int)):
            raise ValueError("nft priority")
        if "type" in payload and payload["type"] not in {"filter", "nat", "route"}:
            raise ValueError("nft chain type")
        return False
    if entry_type == "rule":
        if not set(payload).issubset({"chain", "comment", "expr", "family", "handle", "table"}) or not {"chain", "expr", "family", "table"}.issubset(payload) or not isinstance(payload["expr"], list):
            raise ValueError("nft rule")
        validate_common(payload, {"chain", "family", "table"})
        if "comment" in payload and (not isinstance(payload["comment"], str) or 256 < len(payload["comment"].encode("utf-8"))):
            raise ValueError("nft comment")
        return any(_parse_nft_expression(expression) for expression in payload["expr"])
    raise ValueError("unsupported nft entry")

def _parse_iptables_save(raw):
    text = raw.decode("utf-8", errors="strict")
    if not text or "\r" in text or not text.endswith("\n"):
        raise ValueError("iptables canonical text")
    conflict = False
    in_table = False
    saw_table = False
    declared_chains = set()
    pending_rules = []
    for line in text.splitlines():
        if re.fullmatch(r"#[\x20-\x7e]*", line):
            continue
        if re.fullmatch(r"\*(?:filter|mangle|nat|raw|security)", line):
            if in_table:
                raise ValueError("iptables table nesting")
            in_table = True
            saw_table = True
            declared_chains = set()
            pending_rules = []
            continue
        chain_match = re.fullmatch(r":([A-Za-z0-9_-]+) (?:ACCEPT|DROP|REJECT|-) \[[0-9]+:[0-9]+\]", line)
        if chain_match:
            if not in_table:
                raise ValueError("iptables chain placement")
            declared_chains.add(chain_match.group(1))
            continue
        if line == "COMMIT":
            if not in_table:
                raise ValueError("iptables commit placement")
            if not declared_chains:
                raise ValueError("iptables missing chain")
            for chain, jump in pending_rules:
                if chain not in declared_chains or (jump and jump not in {"ACCEPT", "DROP", "REJECT", "RETURN", "LOG"} and jump not in declared_chains):
                    raise ValueError("iptables undeclared chain")
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
        jump = None
        while index < len(tokens):
            option = tokens[index]
            if option in zero:
                index += 1
                continue
            if option not in single or not index + 1 < len(tokens) or tokens[index + 1].startswith("-"):
                raise ValueError("iptables option")
            argument = tokens[index + 1]
            if option in {"-p", "--protocol"}:
                if argument not in {"all", "icmp", "icmpv6", "tcp", "udp"}:
                    raise ValueError("iptables protocol")
            elif option in {"-j", "--jump", "-g", "--goto"}:
                if re.fullmatch(r"[A-Za-z0-9_-]{1,64}", argument) is None:
                    raise ValueError("iptables jump")
                jump = argument
            elif option in {"-m", "--match"}:
                if argument not in {"comment", "conntrack", "icmp", "icmp6", "multiport", "state", "tcp", "udp"}:
                    raise ValueError("iptables match")
            elif option in {"--ctstate", "--state"}:
                if any(state not in {"ESTABLISHED", "INVALID", "NEW", "RELATED", "UNTRACKED"} for state in argument.split(",")):
                    raise ValueError("iptables state")
            elif option == "--icmp-type":
                if argument not in {"destination-unreachable", "echo-reply", "echo-request", "parameter-problem", "redirect", "source-quench", "time-exceeded"} and not (argument.isdigit() and 0 <= int(argument) <= 255):
                    raise ValueError("iptables icmp type")
            elif option in {"-i", "--in-interface", "-o", "--out-interface"}:
                if re.fullmatch(r"(?:[A-Za-z0-9_.-]{1,63}\+|[A-Za-z0-9_.-]{1,64})", argument) is None:
                    raise ValueError("iptables interface")
                if argument.endswith("+"):
                    prefix = argument[:-1]
                    conflict = conflict or any(name.startswith(prefix) for name in {"awg3", "amn2sp3br0"})
                else:
                    conflict = conflict or argument in {"awg3", "amn2sp3br0"}
            elif option in {"-s", "--source", "-d", "--destination"}:
                conflict = conflict or _network_conflicts(argument)
            elif option in {"--sport", "--source-port", "--dport", "--destination-port", "--sports", "--source-ports", "--dports", "--destination-ports"}:
                conflict = conflict or _port_spec_conflicts(argument)
            index += 2
        pending_rules.append((tokens[1], jump))
    if in_table:
        raise ValueError("iptables missing commit")
    if not saw_table:
        raise ValueError("iptables missing table")
    return conflict

def classify_firewall(nft_probe, iptables_probe, iptables_legacy_probe=None):
    backend_states = []
    try:
        if nft_probe[3] == "unavailable":
            backend_states.append("unavailable")
        elif not probe_ok(nft_probe):
            return "stop"
        else:
            if not nft_probe[1].endswith(b"\n") or nft_probe[1].count(b"\n") != 1 or b"\r" in nft_probe[1]:
                return "stop"
            def reject_duplicates(pairs):
                result = {}
                for key, item in pairs:
                    if key in result:
                        raise ValueError("duplicate nft key")
                    result[key] = item
                return result
            value = json.loads(
                nft_probe[1][:-1].decode("utf-8", errors="strict"),
                object_pairs_hook=reject_duplicates,
                parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite nft value")),
            )
            if not isinstance(value, dict) or set(value) != {"nftables"} or not isinstance(value["nftables"], list):
                return "stop"
            backend_states.append("conflict" if any(_parse_nft_entry(entry) for entry in value["nftables"]) else "pass")
        for probe in (iptables_probe, iptables_legacy_probe):
            if probe is None or probe[3] == "unavailable":
                backend_states.append("unavailable")
            elif not probe_ok(probe):
                return "stop"
            else:
                backend_states.append("conflict" if _parse_iptables_save(probe[1]) else "pass")
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError):
        return "stop"
    if "conflict" in backend_states:
        return "stop"
    return "pass" if "pass" in backend_states else "stop"

def parse_awg2_container_probe(probe):
    if not probe_ok(probe):
        return None
    match = re.fullmatch(rb"true\|([1-9][0-9]{0,9})\|([0-9]+)\n", probe[1])
    if match is None:
        return None
    return int(match.group(1).decode('ascii')), int(match.group(2).decode('ascii'))

def classify_awg2_health(owner_probe, initial_probe, interface_probe, handshake_probe, final_probe, final_owner_probe, now_epoch):
    if not all(probe_ok(probe) for probe in (owner_probe, initial_probe, interface_probe, handshake_probe, final_probe, final_owner_probe)):
        return "stop"
    if owner_probe[1] != b"active\n" or final_owner_probe[1] != owner_probe[1]:
        return "stop"
    container_state = parse_awg2_container_probe(initial_probe)
    if initial_probe[1] != final_probe[1]:
        return "stop"
    if container_state is None or re.fullmatch(rb"[0-9]+: awg0(?:@[^: \n]+)?: <[A-Z0-9_,]+\x3e(?: [^\r\n]*)?\n(?:    [^\r\n]+\n)*", interface_probe[1]) is None:
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

def classify_os_release(raw):
    try:
        if not isinstance(raw, bytes) or not raw or not raw.endswith(b"\n") or b"\r" in raw:
            raise ValueError("os release bytes")
        text = raw.decode("ascii", errors="strict")
        values = {}
        for line in text.splitlines():
            match = re.fullmatch(r"([A-Z][A-Z0-9_]*)=(?:\"([^\"\\]*)\"|([A-Za-z0-9._+:/() -]+))", line)
            if match is None or match.group(1) in values:
                raise ValueError("os release syntax")
            values[match.group(1)] = match.group(2) if match.group(2) is not None else match.group(3)
        if "ID" not in values or "VERSION_ID" not in values:
            raise ValueError("os release identity")
    except (UnicodeDecodeError, ValueError, TypeError):
        return "stop", b"malformed-os-release"
    if values["ID"] != "debian" or values["VERSION_ID"] != "12":
        return "stop", b"unsupported-os"
    return "pass", b"debian:12"

def local_host_identity(expected_host):
    ensure_work_budget()
    try:
        expected_address = ipaddress.ip_address(expected_host)
    except ValueError:
        expected_address = None
    probe = command([HOSTNAME, "-I"] if expected_address is not None else [HOSTNAME])
    if not probe_ok(probe) or not probe[1].endswith(b"\n") or b"\r" in probe[1]:
        raise ValueError("host identity unavailable")
    text = probe[1][:-1].decode("ascii", errors="strict")
    if expected_address is not None:
        addresses = []
        for token in text.split():
            addresses.append(ipaddress.ip_address(token))
        if expected_address not in addresses:
            raise ValueError("host identity mismatch")
        return expected_host
    if EXPECTED_HOST_RE.fullmatch(text) is None:
        raise ValueError("host identity malformed")
    return text

def observed(state, raw):
    if state not in STATES:
        raise ValueError("invalid observation state")
    if not isinstance(raw, bytes):
        raw = str(raw).encode("utf-8", errors="replace")
    if MAXIMUM_OUTPUT_BYTES + 1 < len(raw):
        return "stop", raw[:MAXIMUM_OUTPUT_BYTES + 1]
    return state, raw

def resource_path_state(path):
    try:
        ensure_work_budget()
    except TimeoutError:
        return observed("stop", "work_budget_exceeded")
    candidate = pathlib.Path(path)
    try:
        os.lstat(candidate)
    except FileNotFoundError:
        return observed("free", "absent-exact")
    except OSError as exc:
        return observed("stop", type(exc).__name__)
    return observed("stop", "present")

def scan_recovery_markers(roots):
    marker_tokens = ("incomplete", "pending", "recovery")
    markers = []
    entry_count = 0
    pending = [pathlib.Path(root) for root in roots]
    try:
        while pending:
            try:
                ensure_work_budget()
            except TimeoutError:
                return "stop", "work_budget_exceeded"
            root = pending.pop()
            try:
                iterator = os.scandir(root)
            except FileNotFoundError:
                continue
            with iterator:
                for entry in iterator:
                    try:
                        ensure_work_budget()
                    except TimeoutError:
                        return "stop", "work_budget_exceeded"
                    entry_count += 1
                    if MAX_RECOVERY_ENTRIES < entry_count:
                        return "stop", "entry_limit_exceeded"
                    stat_result = entry.stat(follow_symlinks=False)
                    mode = stat_result.st_mode
                    if entry.is_symlink():
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        pending.append(pathlib.Path(entry.path))
                    elif entry.is_file(follow_symlinks=False) and any(token in entry.name.casefold() for token in marker_tokens):
                        markers.append(entry.path)
        return ("stop", "\n".join(sorted(markers))) if markers else ("absent", "no-markers")
    except OSError as exc:
        return "stop", type(exc).__name__

def production_observations():
    ensure_work_budget()
    values = {}
    try:
        os_raw = bounded_os_release_bytes()
        os_state, os_evidence = classify_os_release(os_raw)
    except OSError as exc:
        os_state, os_evidence = "stop", type(exc).__name__.encode("ascii")
    values["os_compatibility"] = observed(os_state, os_evidence)
    machine = os.uname().machine if hasattr(os, "uname") else "unknown"
    values["architecture"] = observed("pass" if machine in {"x86_64", "amd64"} else "stop", machine)
    py_probe = command([PYTHON_3_12, "-I", "-B", "--version"])
    values["python_3_12"] = observed("pass" if probe_ok(py_probe) and py_probe[1].startswith(b"Python 3.12.") else "stop", py_probe[1] + py_probe[2])
    try:
        free_bytes = shutil.disk_usage("/var/lib").free
        disk_state, disk_raw = ("pass" if 4 * 1024 * 1024 * 1024 <= free_bytes else "stop"), f"free-bytes:{free_bytes}"
    except OSError as exc:
        disk_state, disk_raw = "stop", type(exc).__name__
    values["disk_space"] = observed(disk_state, disk_raw)
    app_root = pathlib.Path(CURRENT_APPLICATION_ROOT)
    database = pathlib.Path(CURRENT_DATABASE_PATH)
    backup_root = pathlib.Path("/var/backups")
    values["application_state"] = observed("present" if app_root.is_dir() else "stop", f"directory:{app_root.is_dir()}")
    database_ok = database.is_file() and os.access(database, os.R_OK)
    values["database_state"] = observed("present" if database_ok else "stop", f"file-readable:{database_ok}")
    backup_ok = backup_root.is_dir() and os.access(backup_root, os.W_OK) and database_ok
    values["backup_capability"] = observed("pass" if backup_ok else "stop", f"backup-ready:{backup_ok}")
    systemd_probe = command([SYSTEMCTL, "is-system-running"])
    values["service_capability"] = observed(classify_systemd_capability(systemd_probe), systemd_probe[1] + systemd_probe[2])
    system_docker_source = production_container_source("system-docker")
    dedicated_docker_source = production_container_source("spain-docker")
    podman_source = production_container_source("podman")
    container_capability, container_name, docker_cidr_state = classify_spain_docker_sources(system_docker_source, dedicated_docker_source, podman_source)
    inventory_raw = b"".join(
        probe[1] + probe[2]
        for source in (system_docker_source, dedicated_docker_source, podman_source)
        for probe in ([source[0]] + ([source[1]] if source[1] is not None else []) + source[2])
    )
    values["container_capability"] = observed(container_capability, inventory_raw)
    values["container_name"] = observed(container_name, inventory_raw)
    awg_owner = command([SYSTEMCTL, "show", CURRENT_AWG2_OWNER_UNIT, "--property=ActiveState", "--value"])
    awg_unit = command([SPAIN_DOCKER, "--host", SPAIN_DOCKER_HOST, "inspect", "--format", "{{.State.Running}}|{{.State.Pid}}|{{.RestartCount}}", CURRENT_AWG2_CONTAINER])
    awg_container_state = parse_awg2_container_probe(awg_unit)
    if awg_container_state is None:
        awg_link = (125, b"", b"", "incomplete_output")
        awg_handshakes = (125, b"", b"", "incomplete_output")
    else:
        netns = f"--net=/proc/{awg_container_state[0]}/ns/net"
        awg_link = command([NSENTER, netns, IP, "-o", "link", "show", "dev", CURRENT_AWG2_INTERFACE])
        awg_handshakes = command([NSENTER, netns, "/usr/bin/awg", "show", CURRENT_AWG2_INTERFACE, "latest-handshakes"])
    awg_final = command([SPAIN_DOCKER, "--host", SPAIN_DOCKER_HOST, "inspect", "--format", "{{.State.Running}}|{{.State.Pid}}|{{.RestartCount}}", CURRENT_AWG2_CONTAINER])
    awg_owner_final = command([SYSTEMCTL, "show", CURRENT_AWG2_OWNER_UNIT, "--property=ActiveState", "--value"])
    values["awg2_health"] = observed(classify_awg2_health(awg_owner, awg_unit, awg_link, awg_handshakes, awg_final, awg_owner_final, int(time.time())), awg_owner[1] + awg_owner[2] + awg_unit[1] + awg_unit[2] + awg_link[1] + awg_link[2] + awg_handshakes[1] + awg_handshakes[2] + awg_final[1] + awg_final[2] + awg_owner_final[1] + awg_owner_final[2])
    bot_active_probe = command([SYSTEMCTL, "show", CURRENT_BOT_UNIT, "--property=ActiveState", "--value"])
    bot_enabled_probe = command([SYSTEMCTL, "show", CURRENT_BOT_UNIT, "--property=UnitFileState", "--value"])
    values["telegram_prerequisites"] = observed(classify_phase13_bot_unit(bot_active_probe, bot_enabled_probe), bot_active_probe[1] + bot_active_probe[2] + bot_enabled_probe[1] + bot_enabled_probe[2])
    awg3_probe = command([IP, "link", "show", "awg3"])
    bridge_probe = command([IP, "link", "show", "amn2sp3br0"])
    values["interface_awg3"] = observed(classify_ip_link(awg3_probe, "awg3"), awg3_probe[1] + awg3_probe[2])
    values["bridge_amn2sp3br0"] = observed(classify_ip_link(bridge_probe, "amn2sp3br0"), bridge_probe[1] + bridge_probe[2])
    socket_probe = command([SS, "-H", "-lun"])
    values["udp_30002"] = observed(classify_udp_port(socket_probe), socket_probe[1] + socket_probe[2])
    route_probe = command([IP, "-j", "route", "show", "table", "all"])
    route_state, vpn_state, container_cidr_state = classify_routes(route_probe)
    values["routes"] = observed(route_state, route_probe[1] + route_probe[2])
    values["vpn_cidr_10_212_13_0_24"] = observed(vpn_state, route_probe[1] + route_probe[2])
    combined_container_cidr_state = "free" if container_cidr_state == "free" and docker_cidr_state == "free" else "stop"
    values["container_cidr_172_29_252_0_28"] = observed(combined_container_cidr_state, route_probe[1] + route_probe[2] + inventory_raw)
    nft_probe = command([NFT, "-j", "list", "ruleset"])
    iptables_probe = command([IPTABLES_SAVE])
    iptables_legacy_probe = command([IPTABLES_LEGACY_SAVE])
    firewall_raw = nft_probe[1] + nft_probe[2] + iptables_probe[1] + iptables_probe[2] + iptables_legacy_probe[1] + iptables_legacy_probe[2]
    values["firewall"] = observed(classify_firewall(nft_probe, iptables_probe, iptables_legacy_probe), firewall_raw)
    values["config_path"] = resource_path_state("/var/lib/amn2-spain/awg3/awg3.conf")
    values["state_root"] = resource_path_state("/var/lib/amn2-spain/awg3")
    service_probe = command([SYSTEMCTL, "show", "amn2-spain-awg3.service", "--property=LoadState", "--value"])
    values["service_name"] = observed(classify_service_absence(service_probe), service_probe[1] + service_probe[2])
    marker_state, marker_raw = scan_recovery_markers((pathlib.Path("/run/amn2-spain"), pathlib.Path("/var/lib/amn2-spain")))
    values["recovery_markers_phase14_phase15_phase16"] = observed(marker_state, marker_raw)
    ensure_work_budget()
    return values

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
    if raw_values["recovery_markers_phase14_phase15_phase16"][0] in {"stop", "unknown"}:
        reasons.append("recovery_incomplete")
    if any(raw_values[name][0] in {"stop", "unknown"} for name in CONFLICT_NAMES):
        reasons.append("resource_conflict")
    if any(state in {"stop", "unknown"} for name, (state, _raw) in raw_values.items() if name not in CONFLICT_NAMES and name != "recovery_markers_phase14_phase15_phase16"):
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
        "schema": "amn2.phase16.spain-readonly-collector.v1",
    }

try:
    claim_id = sys.argv[4]
    package_id = sys.argv[1]
    manifest_sha256 = sys.argv[2]
    collector_sha256 = sys.argv[3]
    expected_host = sys.argv[5]
    if not validate_envelope(package_id, manifest_sha256, collector_sha256, claim_id, expected_host):
        raise ValueError("preflight identity binding")
    host_identity = local_host_identity(expected_host)
    raw_values = production_observations()
    ensure_work_budget()
    document = build_document(package_id=package_id, manifest_sha256=manifest_sha256, collector_sha256=collector_sha256, claim_id=claim_id, expected_host=expected_host, host_identity=host_identity, raw_values=raw_values, observed_at=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    ensure_work_budget()
    sys.stdout.buffer.write(json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n")
except Exception as exc:
    sys.stderr.write("collector_failed:" + type(exc).__name__ + "\n")
    raise SystemExit(71)
PHASE16_PY
