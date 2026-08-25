#!/usr/bin/python3
"""Read-only, normalized prerequisite gate for Phase 16 Spain controlled stage."""

import datetime
import ipaddress
import json
import os
import pathlib
import re
import stat
import subprocess
import time


PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-011"
STATE_SHA256 = "49a128e123d323e34536f6625e7d134a5c7c8299eda468457030961ec7931dfa"
RUNTIME_IDENTITY = (
    "docker.io/amneziavpn/amneziawg-go@"
    "sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d"
)
TARGET_CONTAINER_CIDR = ipaddress.ip_network("172.29.252.0/28")
TARGET_VPN_CIDR = ipaddress.ip_network("10.212.13.0/24")
MAX_OUTPUT_BYTES = 65536


def path_type(value):
    try:
        mode = os.lstat(value).st_mode
    except FileNotFoundError:
        return "missing"
    except OSError:
        return "unknown"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISREG(mode):
        return "regular"
    if stat.S_ISDIR(mode):
        return "directory"
    return "other"


def executable(value):
    return path_type(value) == "regular" and os.access(value, os.X_OK)


def run(arguments, timeout=5):
    try:
        result = subprocess.run(
            arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout,
            env={"LANG": "C", "LC_ALL": "C", "PATH": "/usr/bin:/usr/sbin:/bin:/sbin"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return 125, b"", b""
    if len(result.stdout) + len(result.stderr) > MAX_OUTPUT_BYTES:
        return 125, b"", b""
    return result.returncode, result.stdout, result.stderr


def command_ok(arguments, timeout=5):
    code, _stdout, _stderr = run(arguments, timeout=timeout)
    return code == 0


def config_contract():
    config = "/var/lib/amn2-phase16/input/awg3.conf"
    if path_type(config) != "regular":
        return {"path_ready": False, "contract_ready": False}
    try:
        mode = stat.S_IMODE(os.stat(config, follow_symlinks=False).st_mode)
        raw = pathlib.Path(config).read_bytes()
    except OSError:
        return {"path_ready": True, "contract_ready": False}
    if len(raw) > 32768 or b"\x00" in raw:
        return {"path_ready": True, "contract_ready": False}
    try:
        lines = raw.decode("ascii", errors="strict").splitlines()
    except UnicodeError:
        return {"path_ready": True, "contract_ready": False}
    peer_present = any(re.fullmatch(r"\s*\[Peer\]\s*", line) for line in lines)
    listen_port = any(re.fullmatch(r"\s*ListenPort\s*=\s*30002\s*", line) for line in lines)
    random_trailers = any(re.fullmatch(r"\s*RandomTrailers\s*=\s*on\s*", line) for line in lines)
    disable_cookies = any(re.fullmatch(r"\s*DisableCookies\s*=\s*on\s*", line) for line in lines)
    ready = (
        mode in {0o400, 0o600}
        and not peer_present
        and listen_port
        and random_trailers
        and disable_cookies
    )
    return {"path_ready": True, "contract_ready": ready}


def system_docker_state():
    docker = "/usr/bin/docker"
    daemon_ready = command_ok([docker, "info", "--format", "{{.ServerVersion}}"], timeout=8)
    image_present = command_ok(
        [docker, "image", "inspect", "--format", "{{.Id}}", RUNTIME_IDENTITY],
        timeout=8,
    )
    container_present = command_ok(
        [docker, "container", "inspect", "--format", "{{.State.Status}}", "amn2-spain-awg3"]
    )
    network_present = command_ok(
        [docker, "network", "inspect", "--format", "{{.Name}}", "amn2sp3"]
    )
    cidr_conflicts = 0
    code, stdout, _stderr = run([docker, "network", "ls", "-q"], timeout=8)
    if code == 0:
        identifiers = [line for line in stdout.decode("ascii", errors="ignore").splitlines() if line]
        if len(identifiers) <= 256:
            for identifier in identifiers:
                code, payload, _stderr = run([docker, "network", "inspect", identifier], timeout=5)
                if code != 0:
                    cidr_conflicts += 1
                    continue
                try:
                    document = json.loads(payload.decode("utf-8", errors="strict"))
                    configs = document[0].get("IPAM", {}).get("Config") or []
                    for config in configs:
                        subnet = config.get("Subnet")
                        if isinstance(subnet, str):
                            candidate = ipaddress.ip_network(subnet, strict=False)
                            if candidate.version == 4 and candidate.overlaps(TARGET_CONTAINER_CIDR):
                                cidr_conflicts += 1
                except (IndexError, KeyError, TypeError, ValueError, UnicodeError, json.JSONDecodeError):
                    cidr_conflicts += 1
    else:
        cidr_conflicts = -1
    return {
        "container_present": container_present,
        "daemon_ready": daemon_ready,
        "image_present": image_present,
        "network_present": network_present,
        "target_cidr_conflicts": cidr_conflicts,
    }


def route_conflicts():
    code, stdout, _stderr = run(["/usr/sbin/ip", "-j", "route", "show", "table", "all"], timeout=8)
    if code != 0:
        return -1
    try:
        routes = json.loads(stdout.decode("utf-8", errors="strict"))
    except (UnicodeError, json.JSONDecodeError):
        return -1
    conflicts = 0
    for route in routes:
        destination = route.get("dst")
        if not isinstance(destination, str) or destination == "default":
            continue
        try:
            candidate = ipaddress.ip_network(destination, strict=False)
        except ValueError:
            return -1
        if candidate.version == 4 and candidate.overlaps(TARGET_VPN_CIDR):
            conflicts += 1
    return conflicts


def awg2_health():
    systemctl = "/usr/bin/systemctl"
    docker = "/opt/amn2-spain/docker/bin/docker"
    docker_host = "unix:///run/amn2-spain-docker/docker.sock"
    owner_active = command_ok([systemctl, "is-active", "--quiet", "amn2-spain-docker.service"])
    code, stdout, _stderr = run(
        [docker, "--host", docker_host, "inspect", "--format", "{{.State.Running}}|{{.State.Pid}}|{{.RestartCount}}", "amn2-spain-awg"],
        timeout=8,
    )
    running = False
    restart_count = -1
    pid = None
    if code == 0:
        parts = stdout.decode("ascii", errors="ignore").strip().split("|")
        if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
            running = parts[0] == "true" and int(parts[1]) > 0
            pid = int(parts[1])
            restart_count = int(parts[2])
    interface_present = False
    peer_count = 0
    fresh_peer_count = 0
    handshake_schema_valid = False
    if running and pid is not None:
        interface_present = command_ok(
            ["/usr/bin/nsenter", f"--net=/proc/{pid}/ns/net", "/usr/sbin/ip", "link", "show", "dev", "awgsp0"]
        )
        code, handshakes, _stderr = run(
            [
                "/usr/bin/nsenter", f"--mount=/proc/{pid}/ns/mnt", f"--net=/proc/{pid}/ns/net",
                "/usr/bin/awg", "show", "awgsp0", "latest-handshakes",
            ],
            timeout=8,
        )
        if code == 0:
            now = int(time.time())
            valid = True
            lines = handshakes.splitlines()
            for line in lines:
                fields = line.split(b"\t")
                if len(fields) != 2 or len(fields[0]) != 44 or not fields[1].isdigit():
                    valid = False
                    break
                timestamp = int(fields[1])
                peer_count += 1
                if 0 < timestamp <= now and now - timestamp <= 600:
                    fresh_peer_count += 1
            handshake_schema_valid = valid and peer_count > 0
    return {
        "container_running": running,
        "fresh_peer_count": fresh_peer_count,
        "handshake_schema_valid": handshake_schema_valid,
        "interface_present": interface_present,
        "owner_active": owner_active,
        "peer_count": peer_count,
        "restart_count": restart_count,
    }


def udp_listener_count():
    code, stdout, _stderr = run(["/usr/bin/ss", "-H", "-lun"], timeout=5)
    if code != 0:
        return -1
    count = 0
    for line in stdout.decode("ascii", errors="ignore").splitlines():
        fields = line.split()
        if len(fields) >= 5 and fields[4].rsplit(":", 1)[-1] == "30002":
            count += 1
    return count


def main():
    paths = {
        "application_database_current": path_type("/var/lib/amn2-spain/amn2.sqlite3"),
        "application_database_stage_expected": path_type("/var/lib/amn2-spain/amn2.db"),
        "application_release": path_type(f"/opt/amn2-spain/releases/{PACKAGE_ID}"),
        "application_staging": path_type(f"/opt/amn2-spain/releases/{PACKAGE_ID}.staging"),
        "application_ledger": path_type("/var/lib/amn2-phase16/stage/application.json"),
        "application_backup": path_type(f"/var/lib/amn2-phase16/rollback/application/{STATE_SHA256}.sqlite3"),
        "package_root": path_type("/var/lib/amn2-phase16/package"),
        "package_manifest": path_type("/var/lib/amn2-phase16/package/manifest.json"),
        "package_source_app": path_type("/var/lib/amn2-phase16/package/source/app"),
        "runtime_input_config": path_type("/var/lib/amn2-phase16/input/awg3.conf"),
        "runtime_ledger": path_type("/var/lib/amn2-phase16/stage/awg31-runtime.json"),
        "runtime_state_root": path_type("/var/lib/amn2-spain/awg3"),
        "runtime_config": path_type("/var/lib/amn2-spain/awg3/awg3.conf"),
        "runtime_unit": path_type("/etc/systemd/system/amn2-spain-awg3.service"),
    }
    required_executables = {
        value: executable(value)
        for value in (
            "/usr/bin/cp", "/usr/bin/docker", "/usr/bin/install", "/usr/bin/mv",
            "/usr/bin/python3", "/usr/bin/sha256sum", "/usr/bin/sqlite3",
            "/usr/bin/systemctl", "/usr/sbin/ip",
        )
    }
    docker = system_docker_state()
    awg2 = awg2_health()
    config = config_contract()
    service_load_code, service_load_stdout, _service_load_stderr = run(
        ["/usr/bin/systemctl", "show", "amn2-spain-awg3.service", "--property=LoadState", "--value"]
    )
    service_absent = service_load_code == 0 and service_load_stdout == b"not-found\n"
    bridge_absent = not command_ok(["/usr/sbin/ip", "link", "show", "dev", "amn2sp3br0"])
    interface_absent = not command_ok(["/usr/sbin/ip", "link", "show", "dev", "awg3"])
    package_ready = (
        paths["package_root"] == "directory"
        and paths["package_manifest"] == "regular"
        and paths["package_source_app"] == "directory"
    )
    database_contract_compatible = paths["application_database_stage_expected"] == "regular"
    targets_free = (
        all(paths[name] == "missing" for name in (
            "application_release", "application_staging", "application_ledger", "application_backup",
            "runtime_ledger", "runtime_state_root", "runtime_config", "runtime_unit",
        ))
        and not docker["container_present"]
        and not docker["network_present"]
        and docker["target_cidr_conflicts"] == 0
        and service_absent
        and bridge_absent
        and interface_absent
        and udp_listener_count() == 0
        and route_conflicts() == 0
    )
    awg2_pass = (
        awg2["owner_active"] and awg2["container_running"] and awg2["interface_present"]
        and awg2["handshake_schema_valid"] and awg2["fresh_peer_count"] > 0
    )
    blockers = []
    if not database_contract_compatible:
        blockers.append("application_stage_database_path_mismatch")
    if not package_ready:
        blockers.append("remote_package_not_ready")
    if not config["contract_ready"]:
        blockers.append("runtime_input_config_not_ready")
    if not all(required_executables.values()):
        blockers.append("required_executable_missing")
    if not docker["daemon_ready"]:
        blockers.append("system_docker_not_ready")
    if not targets_free:
        blockers.append("stage_target_not_free")
    if not awg2_pass:
        blockers.append("awg2_health_not_pass")
    document = {
        "awg2": awg2,
        "blockers": blockers,
        "config": config,
        "database_contract_compatible": database_contract_compatible,
        "decision": "pass" if not blockers else "stop",
        "docker": docker,
        "observed_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "package_id": PACKAGE_ID,
        "package_ready": package_ready,
        "paths": paths,
        "required_executables": required_executables,
        "safety": {"live_mutation": False, "raw_values_emitted": False, "remote_file_written": False},
        "schema": "amn2.phase16.stage-prerequisite-gate.v1",
        "stage_targets_free": targets_free,
        "state_sha256": STATE_SHA256,
    }
    raw = json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
    if len(raw) > MAX_OUTPUT_BYTES:
        raise SystemExit(70)
    os.write(1, raw)


if __name__ == "__main__":
    main()
