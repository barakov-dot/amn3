from __future__ import annotations

import copy
import hashlib
import ipaddress
import json
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.phase12_spain_package import (
        canonical_json_bytes,
        compact_json_bytes_preserving_object_order,
        sha256_canonical,
    )
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.phase12_spain_package import (
        canonical_json_bytes,
        compact_json_bytes_preserving_object_order,
        sha256_canonical,
    )


OBSERVATION_SCHEMA = "amn2.spain-precondition-observation.v1"
RECEIPT_SCHEMA = "amn2.spain-preconditions-passed.v1"
SHA256_RE = __import__("re").compile(r"^[0-9a-f]{64}$")
BOOT_ID_RE = __import__("re").compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
DEFAULT_RUN009_EVIDENCE_SHA256 = "8d8a4e155b30c4b72c564056c71b159e222c53e3bdc60018c3f6099c1979e1a8"
DEFAULT_RUN009_FINGERPRINT_SHA256 = "e15219cb5204d54a9ad11263cfba1f7c86e16dab3287c752a8b6f136ec4a5ed5"
RUN009_EVIDENCE_SHA256 = DEFAULT_RUN009_EVIDENCE_SHA256
RUN009_FINGERPRINT_SHA256 = DEFAULT_RUN009_FINGERPRINT_SHA256


class PreconditionError(ValueError):
    pass


def _fail(message: str) -> None:
    raise PreconditionError(message)


def observation_from_resource_confirmation_evidence(
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Normalize the checksum-bound one-shot collector into the precondition schema."""
    expected = {
        "schema",
        "mode",
        "host_identity",
        "platform",
        "capacity",
        "candidates",
        "listening_sockets",
        "network_state",
        "systemd",
        "cgroup_diagnostics",
        "firewall",
        "unrelated_service_fingerprint",
    }
    if (
        not isinstance(evidence, dict)
        or set(evidence) != expected
        or evidence.get("schema")
        != "amn2.phase12-spain-resource-confirmation.v1"
        or evidence.get("mode") != "read_only_resource_confirmation"
    ):
        _fail("resource confirmation evidence schema mismatch")
    platform = evidence.get("platform")
    capacity = evidence.get("capacity")
    candidates = evidence.get("candidates")
    network_state = evidence.get("network_state")
    firewall = evidence.get("firewall")
    if not all(
        isinstance(value, dict)
        for value in (platform, capacity, candidates, network_state, firewall)
    ):
        _fail("resource confirmation evidence structure invalid")
    try:
        os_release = platform["os_release"]
        python3 = platform["python3"]
        kernel = platform["kernel"]
        filesystems = capacity["filesystems"]
        if not isinstance(filesystems, list):
            _fail("resource confirmation filesystem inventory invalid")
        filesystem_map = {
            row["path"]: {
                "disk_available_bytes": row["available_bytes"],
                "inodes_available": row["available_inodes"],
            }
            for row in filesystems
            if row["path"] in {"/opt", "/etc", "/var", "/run"}
        }
        if set(filesystem_map) != {"/opt", "/etc", "/var", "/run"}:
            _fail("resource confirmation filesystem inventory invalid")
        existing_paths = [
            row["path"] for row in candidates["paths"] if row["exists"]
        ]
        audit_path = "/var/lib/amn2-spain-phase12-audit"
        package_path = "/opt/amn2-spain-package"
        identity = candidates["identities"]
        docker = candidates["docker"]
        network = candidates["network"]
        listeners: list[str] = []
        for row in evidence["listening_sockets"]:
            address = str(row["address"]).strip("[]")
            if address in {"0.0.0.0", "::", "*"}:
                scope = "wildcard"
            else:
                ip = ipaddress.ip_address(address)
                if ip.is_loopback:
                    scope = "loopback"
                elif ip.is_link_local:
                    scope = "linklocal"
                elif ip.is_private:
                    scope = "private"
                else:
                    scope = "public"
            listeners.append(f"{row['protocol']}|{scope}|{int(row['port'])}")
        listeners.sort()
        addresses = sorted(
            f"{row['address']}/{int(row['prefix_length'])}"
            for row in network_state["addresses"]
        )
        routes: list[str] = []
        for row in network_state["routes"]:
            destination = row["destination"]
            if destination == "default":
                destination = "::/0" if row["family"] == "inet6" else "0.0.0.0/0"
            routes.append(str(destination))
        routes.sort()
        structured = firewall["structured_snapshot"]
        owned_firewall = []
        for item in structured.get("nftables", []):
            if not isinstance(item, dict) or len(item) != 1:
                _fail("resource confirmation firewall structure invalid")
            _kind, body = next(iter(item.items()))
            if isinstance(body, dict) and (
                body.get("name") == "amn2_spain"
                or body.get("table") == "amn2_spain"
            ):
                owned_firewall.append("inet:amn2_spain")
        package_exists = package_path in existing_paths
        retained_exists = audit_path in existing_paths
        regular_paths = [
            path for path in existing_paths if path not in {audit_path}
        ]
        systemd_projection = evidence["unrelated_service_fingerprint"]
        if not isinstance(systemd_projection, list):
            _fail("resource confirmation fingerprint invalid")
    except (KeyError, TypeError, ValueError) as exc:
        raise PreconditionError(
            "resource confirmation evidence structure invalid"
        ) from exc
    return {
        "schema": OBSERVATION_SCHEMA,
        "os": {
            "family": str(os_release["id"]).lower(),
            "release": str(os_release["version_id"]),
            "kernel": str(kernel["release"]),
            "architecture": str(platform["architecture"]),
            "python": str(python3["version"]),
            "glibc": str(platform["glibc_version"]),
            "python_soabi": str(python3["soabi"]),
        },
        "capacity": {
            "disk_available_bytes": min(
                row["disk_available_bytes"] for row in filesystem_map.values()
            ),
            "inodes_available": min(
                row["inodes_available"] for row in filesystem_map.values()
            ),
            "memory_available_kib": int(capacity["mem_available_bytes"]) // 1024,
            "filesystems": filesystem_map,
        },
        "existing": {
            "paths": regular_paths,
            "retained_paths": [audit_path] if retained_exists else [],
            "users": [identity["user_name"]] if identity["user_exists"] else [],
            "groups": [identity["group_name"]] if identity["group_exists"] else [],
            "units": [row["name"] for row in candidates["units"] if row["exists"]],
            "containers": [docker["container_name"]] if docker["container_exists"] else [],
            "networks": [docker["network_name"]] if docker["network_exists"] else [],
            "bridges": [network["bridge_name"]] if network["bridge_exists"] else [],
            "interfaces": [network["interface_name"]] if network["interface_exists"] else [],
            "uids": [identity["user_id"]] if identity["uid_exists"] else [],
            "gids": [identity["group_id"]] if identity["gid_exists"] else [],
            "sockets": [row["path"] for row in candidates["sockets"] if row["exists"]],
            "runtime_dirs": [row["path"] for row in candidates["runtime_directories"] if row["exists"]],
            "firewall_objects": sorted(set(owned_firewall)),
            "owned_routes": [
                route for route in routes if route == "10.212.12.0/24"
            ],
            "sysctls": [],
        },
        "listeners": listeners,
        "addresses": addresses,
        "routes": routes,
        "docker_present": any(
            docker[key]
            for key in (
                "binary_present",
                "potential_socket_present",
                "daemon_process_present",
            )
        ),
        "package_root": {
            "exists": package_exists,
            "is_symlink": False,
            "owner_uid": None,
            "owner_gid": None,
            "mode": None,
        },
        "systemd_projection": copy.deepcopy(systemd_projection),
        "firewall": {
            "backend": firewall["backend"],
            "rules_sha256": firewall["raw_sha256"],
            "rule_count": firewall["raw_rule_count"],
            "nft_json": copy.deepcopy(structured),
        },
    }


def _networks(values: object, label: str) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    if not isinstance(values, list):
        _fail(f"invalid {label} list")
    result = []
    for value in values:
        try:
            if label == "address":
                result.append(ipaddress.ip_interface(value).network)
            else:
                result.append(ipaddress.ip_network(value, strict=False))
        except (TypeError, ValueError) as exc:
            raise PreconditionError(f"invalid {label} CIDR") from exc
    return result


def _persistent_foreign_projection_equal(expected: object, current: object) -> bool:
    if not isinstance(expected, list) or not isinstance(current, list):
        return False

    def by_identity(entries: list[object]) -> dict[tuple[str, str], dict[str, Any]] | None:
        result: dict[tuple[str, str], dict[str, Any]] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                return None
            kind = entry.get("kind")
            name = entry.get("name_sha256")
            if not isinstance(kind, str) or not isinstance(name, str):
                return None
            identity = (kind, name)
            if identity in result:
                return None
            stable = dict(entry)
            stable.pop("bound_port_set", None)
            result[identity] = stable
        return result

    expected_by_identity = by_identity(expected)
    current_by_identity = by_identity(current)
    if expected_by_identity is None or current_by_identity is None:
        return False
    persistent = set(expected_by_identity) & set(current_by_identity)
    return bool(persistent) and all(
        expected_by_identity[identity] == current_by_identity[identity]
        for identity in persistent
    )


def validate_preconditions(
    observation: dict[str, Any],
    resource_plan: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, object]:
    observation_fields = {
        "schema", "os", "capacity", "existing", "listeners", "addresses", "routes",
        "docker_present", "package_root", "systemd_projection", "firewall"
    }
    plan_fields = {
        "schema", "target", "capacity_minimums", "resources", "listeners", "docker_cidr",
        "container_address", "vpn_cidr", "server_vpn_address", "owned_firewall_prefix",
        "package_root", "capacity_filesystems", "runtime_invariants", "firewall_namespace"
    }
    if not isinstance(observation, dict) or set(observation) != observation_fields:
        _fail("observation has unknown/missing fields")
    if not isinstance(resource_plan, dict) or set(resource_plan) != plan_fields or resource_plan.get("schema") != "amn2.spain-resource-plan.v1":
        _fail("resource plan has unknown/missing fields or schema")
    if observation.get("schema") != OBSERVATION_SCHEMA:
        _fail("unsupported observation schema")
    if not isinstance(baseline, dict) or set(baseline) != {
        "run009_evidence_sha256",
        "fingerprint_array_sha256",
        "systemd_projection",
        "firewall",
        "run009_evidence_hex",
    }:
        _fail("baseline has unknown/missing fields")
    if (
        baseline["run009_evidence_sha256"] != RUN009_EVIDENCE_SHA256
        or baseline["fingerprint_array_sha256"] != RUN009_FINGERPRINT_SHA256
    ):
        _fail("baseline does not match authoritative run009 hashes")
    evidence_hex = baseline["run009_evidence_hex"]
    if (
        not isinstance(evidence_hex, str)
        or len(evidence_hex) > 4 * 1024 * 1024
        or len(evidence_hex) % 2
    ):
        _fail("authoritative run009 evidence envelope invalid")
    try:
        evidence_bytes = bytes.fromhex(evidence_hex)
        evidence = json.loads(evidence_bytes.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreconditionError("authoritative run009 evidence malformed") from exc
    if hashlib.sha256(evidence_bytes).hexdigest() != baseline["run009_evidence_sha256"]:
        _fail("authoritative run009 evidence hash mismatch")
    if (
        not isinstance(evidence, dict)
        or evidence.get("schema") != "amn2.spain-readonly-preflight.v1"
        or evidence.get("mode") != "preflight"
        or not isinstance(evidence.get("unrelated_service_fingerprint"), list)
        or not isinstance(evidence.get("firewall"), dict)
    ):
        _fail("authoritative run009 evidence schema mismatch")
    authoritative_fingerprint = evidence["unrelated_service_fingerprint"]
    derived_fingerprint_sha256 = hashlib.sha256(
        compact_json_bytes_preserving_object_order(authoritative_fingerprint)
    ).hexdigest()
    if (
        derived_fingerprint_sha256 != baseline["fingerprint_array_sha256"]
        or baseline["systemd_projection"] != authoritative_fingerprint
    ):
        _fail("authoritative run009 fingerprint projection mismatch")
    authoritative_firewall = evidence["firewall"]
    baseline_firewall = baseline["firewall"]
    if (
        set(authoritative_firewall) != {"backend", "rules_sha256", "rule_count"}
        or not isinstance(baseline_firewall, dict)
        or {
            key: baseline_firewall.get(key)
            for key in ("backend", "rules_sha256", "rule_count")
        }
        != authoritative_firewall
    ):
        _fail("authoritative run009 firewall baseline mismatch")
    os_data = observation.get("os", {})
    target = resource_plan.get("target", {})
    if not isinstance(os_data, dict) or set(os_data) != {
        "family", "release", "kernel", "architecture", "python", "glibc", "python_soabi"
    } or not isinstance(target, dict) or set(target) != {
        "os_family", "os_release", "kernel_prefix", "architecture", "python_major_minor",
        "glibc_minimum", "python_soabi"
    }:
        _fail("OS target/observation has unknown/missing fields")
    checks = (
        (os_data.get("family") == target.get("os_family"), "os family mismatch"),
        (os_data.get("release") == target.get("os_release"), "os release mismatch"),
        (os_data.get("kernel", "").startswith(target.get("kernel_prefix", "!")), "kernel mismatch"),
        (os_data.get("architecture") == target.get("architecture"), "architecture mismatch"),
        (
            isinstance(os_data.get("python"), str)
            and os_data["python"].split(".")[:2]
            == str(target.get("python_major_minor", "")).split("."),
            "python version mismatch",
        ),
        (os_data.get("python_soabi") == target.get("python_soabi"), "Python SOABI mismatch"),
        (
            tuple(int(part) for part in str(os_data.get("glibc", "0")).split("."))
            >= tuple(int(part) for part in str(target.get("glibc_minimum", "999")).split(".")),
            "glibc version mismatch",
        ),
    )
    for passed, message in checks:
        if not passed:
            _fail(message)
    capacity = observation.get("capacity", {})
    minimums = resource_plan.get("capacity_minimums", {})
    if not isinstance(capacity, dict) or set(capacity) != {
        "disk_available_bytes", "inodes_available", "memory_available_kib", "filesystems"
    } or not isinstance(minimums, dict) or set(minimums) != {
        "disk_available_bytes", "inodes_available", "memory_available_kib"
    }:
        _fail("capacity has unknown/missing fields")
    for key, label in (
        ("disk_available_bytes", "disk capacity shortage"),
        ("inodes_available", "inode capacity shortage"),
        ("memory_available_kib", "memory capacity shortage"),
    ):
        value = capacity.get(key)
        minimum = minimums.get(key)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or not isinstance(minimum, int)
            or isinstance(minimum, bool)
            or value < minimum
        ):
            _fail(label)
    filesystems = capacity["filesystems"]
    required_filesystems = resource_plan["capacity_filesystems"]
    if not isinstance(filesystems, dict) or not isinstance(required_filesystems, list) or set(filesystems) != set(required_filesystems):
        _fail("target filesystem capacity inventory mismatch")
    for mount, values in filesystems.items():
        if not isinstance(values, dict) or set(values) != {"disk_available_bytes", "inodes_available"} or any(
            not isinstance(values[key], int) or isinstance(values[key], bool) or values[key] <= 0
            for key in values
        ):
            _fail(f"invalid filesystem capacity: {mount}")
    if observation.get("docker_present") is not False:
        _fail("Docker presence conflicts with dedicated static runtime")
    existing = observation.get("existing")
    planned = resource_plan.get("resources")
    if not isinstance(existing, dict) or not isinstance(planned, dict):
        _fail("invalid resource inventory")
    singular = {
        "paths": "path",
        "retained_paths": "retained audit path",
        "users": "user",
        "groups": "group",
        "units": "unit",
        "containers": "container",
        "networks": "network",
        "bridges": "bridge",
        "interfaces": "interface",
        "uids": "uid",
        "gids": "gid",
        "sockets": "socket",
        "runtime_dirs": "runtime directory",
        "firewall_objects": "firewall object",
        "owned_routes": "owned route",
        "sysctls": "sysctl",
    }
    if set(existing) != set(singular) or set(planned) != set(singular):
        _fail("resource inventory has unknown/missing fields")
    for key, label in singular.items():
        observed_values = existing.get(key)
        planned_values = planned.get(key)
        if not isinstance(observed_values, list) or not isinstance(planned_values, list):
            _fail(f"invalid {label} inventory")
        collision = set(observed_values) & set(planned_values)
        if collision:
            _fail(f"{label} collision: {sorted(collision)[0]}")
    listeners = observation.get("listeners")
    planned_listeners = resource_plan.get("listeners")
    if not isinstance(listeners, list) or not isinstance(planned_listeners, list):
        _fail("invalid listener inventory")
    def parse_listener(row: object) -> tuple[str, str, int]:
        if not isinstance(row, str):
            _fail("invalid listener grammar")
        parts = row.split("|")
        if len(parts) != 3 or parts[0] not in {"tcp", "udp"} or parts[1] not in {
            "wildcard", "loopback", "private", "public", "linklocal"
        } or not parts[2].isdigit() or not (1 <= int(parts[2]) <= 65535):
            _fail("invalid listener grammar")
        return parts[0], parts[1], int(parts[2])
    occupied = {(protocol, port) for protocol, _scope, port in map(parse_listener, listeners)}
    for candidate in planned_listeners:
        protocol, _scope, port = parse_listener(candidate)
        if (protocol, port) in occupied:
            _fail(f"listener collision: {candidate}")
    try:
        docker_cidr = ipaddress.ip_network(resource_plan["docker_cidr"], strict=True)
        vpn_cidr = ipaddress.ip_network(resource_plan["vpn_cidr"], strict=True)
        container_address = ipaddress.ip_interface(resource_plan["container_address"])
        server_address = ipaddress.ip_interface(resource_plan["server_vpn_address"])
    except ValueError as exc:
        raise PreconditionError("invalid candidate CIDR/address") from exc
    if container_address.network != docker_cidr or container_address.ip == docker_cidr.network_address:
        _fail("container address is not contained by Docker CIDR")
    if server_address.network != vpn_cidr or server_address.ip == vpn_cidr.network_address:
        _fail("server VPN address is not contained by VPN CIDR")
    if docker_cidr.overlaps(vpn_cidr):
        _fail("Docker and VPN candidate CIDRs overlap")
    candidates = [docker_cidr, vpn_cidr]
    observed_networks = _networks(observation.get("addresses"), "address") + _networks(
        observation.get("routes"), "route"
    )
    for observed in observed_networks:
        if observed.prefixlen == 0:
            continue
        for candidate in candidates:
            if observed.version == candidate.version and observed.overlaps(candidate):
                _fail(f"CIDR collision: {observed} overlaps {candidate}")
    if not _persistent_foreign_projection_equal(
        baseline.get("systemd_projection"), observation.get("systemd_projection")
    ):
        _fail("systemd baseline projection mismatch")
    observed_firewall = observation.get("firewall")
    baseline_firewall = baseline.get("firewall")
    if not isinstance(observed_firewall, dict) or not isinstance(baseline_firewall, dict):
        _fail("invalid firewall baseline")
    if observed_firewall != baseline_firewall:
        _fail("firewall baseline projection mismatch")
    package_root = observation["package_root"]
    planned_root = resource_plan["package_root"]
    if not isinstance(package_root, dict) or set(package_root) != {
        "exists", "is_symlink", "owner_uid", "owner_gid", "mode"
    } or package_root != {
        "exists": False, "is_symlink": False, "owner_uid": None, "owner_gid": None, "mode": None
    }:
        _fail("package root must be absent and non-symlink before staging")
    if not isinstance(planned_root, dict) or set(planned_root) != {
        "path", "owner_uid", "owner_gid", "mode", "exclusive"
    } or planned_root != {
        "path": "/opt/amn2-spain-package", "owner_uid": 0, "owner_gid": 0,
        "mode": "0700", "exclusive": True
    }:
        _fail("package root sealed contract mismatch")
    return {
        "schema": "amn2.spain-precondition-report.v1",
        "result": "passed",
        "observation_sha256": sha256_canonical(observation),
        "baseline_sha256": sha256_canonical(baseline),
        "resource_plan_sha256": sha256_canonical(resource_plan),
        "run009_evidence_sha256": baseline.get("run009_evidence_sha256"),
        "fingerprint_array_sha256": baseline.get("fingerprint_array_sha256"),
        "checks": [
            "target_exact",
            "capacity",
            "closed_resource_delta",
            "listeners",
            "cidr",
            "systemd_projection",
            "firewall_projection",
        ],
    }


def build_precondition_receipt(
    report: dict[str, Any],
    *,
    package_manifest_sha256: str,
    resource_plan_sha256: str,
    host_identity_sha256: str,
    boot_id: str,
    collector_sha256: str,
    executor_sha256: str,
    package_archive_sha256: str,
    package_archive_size: int,
    issued_at_epoch: int,
    ttl_seconds: int,
    nonce: str,
) -> tuple[dict[str, object], str]:
    if report.get("result") != "passed" or report.get("resource_plan_sha256") != resource_plan_sha256:
        _fail("cannot issue receipt from failed or mismatched report")
    for label, digest in (
        ("package manifest", package_manifest_sha256),
        ("resource plan", resource_plan_sha256),
        ("host identity", host_identity_sha256),
        ("collector", collector_sha256),
        ("executor", executor_sha256),
        ("package archive", package_archive_sha256),
    ):
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            _fail(f"invalid {label} digest")
    if not isinstance(boot_id, str) or BOOT_ID_RE.fullmatch(boot_id) is None:
        _fail("invalid boot id")
    if (
        not isinstance(package_archive_size, int)
        or isinstance(package_archive_size, bool)
        or package_archive_size <= 0
        or package_archive_size > 2 * 1024 * 1024 * 1024
    ):
        _fail("invalid package archive size")
    if not isinstance(nonce, str) or SHA256_RE.fullmatch(nonce) is None:
        _fail("invalid receipt nonce")
    if not isinstance(issued_at_epoch, int) or isinstance(issued_at_epoch, bool) or not isinstance(ttl_seconds, int) or isinstance(ttl_seconds, bool) or ttl_seconds < 60 or ttl_seconds > 600:
        _fail("invalid receipt timestamp/TTL")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "result": "passed",
        "stage": "preconditions_passed",
        "mutation_authorized": False,
        "package_manifest_sha256": package_manifest_sha256,
        "package_archive_sha256": package_archive_sha256,
        "package_archive_size": package_archive_size,
        "resource_plan_sha256": resource_plan_sha256,
        "run009_evidence_sha256": report["run009_evidence_sha256"],
        "fingerprint_array_sha256": report["fingerprint_array_sha256"],
        "observation_sha256": report["observation_sha256"],
        "baseline_sha256": report["baseline_sha256"],
        "host_identity_sha256": host_identity_sha256,
        "boot_id": boot_id,
        "collector_sha256": collector_sha256,
        "executor_sha256": executor_sha256,
        "issued_at_epoch": issued_at_epoch,
        "expires_at_epoch": issued_at_epoch + ttl_seconds,
        "nonce": nonce,
    }
    return receipt, hashlib.sha256(canonical_json_bytes(receipt)).hexdigest()


def verify_precondition_receipt(
    receipt: dict[str, Any],
    detached_sha256: str,
    *,
    package_manifest_sha256: str,
    resource_plan_sha256: str,
    host_identity_sha256: str,
    boot_id: str,
    collector_sha256: str,
    executor_sha256: str,
    package_archive_sha256: str,
    package_archive_size: int,
) -> None:
    expected = hashlib.sha256(canonical_json_bytes(receipt)).hexdigest()
    if expected != detached_sha256:
        _fail("precondition receipt detached hash mismatch")
    if set(receipt) != {
        "schema", "result", "stage", "mutation_authorized", "package_manifest_sha256",
        "package_archive_sha256", "package_archive_size", "resource_plan_sha256", "run009_evidence_sha256",
        "fingerprint_array_sha256", "observation_sha256", "baseline_sha256",
        "host_identity_sha256", "boot_id", "collector_sha256", "executor_sha256",
        "issued_at_epoch", "expires_at_epoch", "nonce"
    } or (
        receipt.get("schema") != RECEIPT_SCHEMA
        or receipt.get("result") != "passed"
        or receipt.get("stage") != "preconditions_passed"
        or receipt.get("mutation_authorized") is not False
        or receipt.get("package_manifest_sha256") != package_manifest_sha256
        or receipt.get("resource_plan_sha256") != resource_plan_sha256
        or receipt.get("host_identity_sha256") != host_identity_sha256
        or receipt.get("boot_id") != boot_id
        or receipt.get("collector_sha256") != collector_sha256
        or receipt.get("executor_sha256") != executor_sha256
        or receipt.get("package_archive_sha256") != package_archive_sha256
        or receipt.get("package_archive_size") != package_archive_size
        or not isinstance(receipt.get("issued_at_epoch"), int)
        or not isinstance(receipt.get("expires_at_epoch"), int)
        or receipt["expires_at_epoch"] - receipt["issued_at_epoch"] < 60
        or receipt["expires_at_epoch"] - receipt["issued_at_epoch"] > 600
        or not isinstance(receipt.get("nonce"), str)
        or SHA256_RE.fullmatch(receipt["nonce"]) is None
    ):
        _fail("precondition receipt binding mismatch")


def receipt_bytes(receipt: dict[str, Any]) -> bytes:
    return canonical_json_bytes(receipt)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 5 or args[0] != "validate":
        print("precondition_inputs_required", file=sys.stderr)
        return 64
    print("live_collector_not_assembled", file=sys.stderr)
    return 78


if __name__ == "__main__":
    raise SystemExit(main())
