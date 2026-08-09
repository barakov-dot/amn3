"""Secret-safe read-only AWG2 predicate diagnosis for AMN2 Phase 13.

The module has no command-line arguments and no mutation paths.  A local,
checksum-bound runner sends one canonical envelope through stdin and invokes
``main_bound_envelope`` over one fixed Spain SSH transport.
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
import hashlib
import json
import re
import sqlite3
import sys
from types import ModuleType
from typing import Mapping, Protocol


UTC = timezone.utc
PAYLOAD_SCHEMA = "amn2.phase13.spain-awg2-predicate-diagnosis-payload.v1"
RECEIPT_SCHEMA = "amn2.phase13.spain-awg2-predicate-diagnosis-receipt.v2"
OUTCOME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")
PEER_PATTERN = re.compile(r"^[A-Za-z0-9+/]{43}=$")
EXPECTED_RESTART_COUNT = 59
EXPECTED_PEER_COUNT = 7
EXPECTED_FORWARD_RULE_COUNT = 3

OBSERVATION_KEYS = {
    "configured_ip_forward_equal",
    "container_running",
    "forward_comments_equal",
    "forward_rule_count",
    "image_present",
    "listen_port_equal",
    "live_ip_forward_equal",
    "live_peer_count",
    "network_mode_equal",
    "peer_sets_equal",
    "persistent_peer_count",
    "restart_count_current",
    "route_equal",
    "units_active_enabled",
}
FOREIGN_DIAGNOSIS_KEYS = {
    "foreign_container_entries",
    "foreign_count_equal",
    "foreign_expected_entries",
    "foreign_expected_equal",
    "foreign_persistent_entries",
    "foreign_repeat_equal",
    "foreign_stable_sha256_after",
    "foreign_stable_sha256_before",
    "foreign_unit_entries",
}
DIRECT_PREDICATES = (
    "container_running",
    "image_present",
    "network_mode_equal",
    "configured_ip_forward_equal",
    "live_ip_forward_equal",
    "units_active_enabled",
    "peer_sets_equal",
    "listen_port_equal",
    "route_equal",
    "forward_comments_equal",
)
PREDICATE_ORDER = (
    "container_running",
    "image_present",
    "network_mode_equal",
    "restart_count_equal",
    "configured_ip_forward_equal",
    "live_ip_forward_equal",
    "units_active_enabled",
    "persistent_peer_count_equal",
    "live_peer_count_equal",
    "peer_sets_equal",
    "listen_port_equal",
    "route_equal",
    "forward_rule_count_equal",
    "forward_comments_equal",
)


class DiagnosisError(RuntimeError):
    """Allowlisted read-only diagnosis failure."""

    def __init__(self, stage: str, reason: str) -> None:
        super().__init__(reason)
        self.stage = stage
        self.reason = reason


class DiagnosisBackend(Protocol):
    def collect_awg2_observation(self) -> dict[str, object]: ...

    def collect_foreign_diagnosis(self) -> dict[str, object]: ...


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _parse_utc(value: object) -> datetime:
    if not isinstance(value, str) or re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value
    ) is None:
        raise DiagnosisError("payload", "payload_invalid")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError as error:
        raise DiagnosisError("payload", "payload_invalid") from error


def _bounded_count(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 4096:
        raise DiagnosisError("observation", "observation_invalid")
    return value


def evaluate_awg2_observation(observation: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(observation, Mapping) or set(observation) != OBSERVATION_KEYS:
        raise DiagnosisError("observation", "observation_invalid")
    booleans: dict[str, bool] = {}
    for name in DIRECT_PREDICATES:
        value = observation[name]
        if not isinstance(value, bool):
            raise DiagnosisError("observation", "observation_invalid")
        booleans[name] = value
    restart_count = _bounded_count(observation["restart_count_current"])
    persistent_count = _bounded_count(observation["persistent_peer_count"])
    live_count = _bounded_count(observation["live_peer_count"])
    forward_count = _bounded_count(observation["forward_rule_count"])
    predicates = {
        **booleans,
        "restart_count_equal": restart_count == EXPECTED_RESTART_COUNT,
        "persistent_peer_count_equal": persistent_count == EXPECTED_PEER_COUNT,
        "live_peer_count_equal": live_count == EXPECTED_PEER_COUNT,
        "forward_rule_count_equal": forward_count == EXPECTED_FORWARD_RULE_COUNT,
    }
    failed = sorted(name for name in PREDICATE_ORDER if not predicates[name])
    non_restart_failed = [name for name in failed if name != "restart_count_equal"]
    return {
        "awg2_equal": not failed,
        "awg2_equal_without_restart_count": not non_restart_failed,
        "configured_ip_forward_equal": predicates["configured_ip_forward_equal"],
        "container_running": predicates["container_running"],
        "expected_forward_rule_count": EXPECTED_FORWARD_RULE_COUNT,
        "expected_peer_count": EXPECTED_PEER_COUNT,
        "failed_predicates": failed,
        "forward_comments_equal": predicates["forward_comments_equal"],
        "forward_rule_count": forward_count,
        "forward_rule_count_equal": predicates["forward_rule_count_equal"],
        "image_present": predicates["image_present"],
        "listen_port_equal": predicates["listen_port_equal"],
        "live_ip_forward_equal": predicates["live_ip_forward_equal"],
        "live_peer_count": live_count,
        "live_peer_count_equal": predicates["live_peer_count_equal"],
        "network_mode_equal": predicates["network_mode_equal"],
        "peer_sets_equal": predicates["peer_sets_equal"],
        "persistent_peer_count": persistent_count,
        "persistent_peer_count_equal": predicates["persistent_peer_count_equal"],
        "restart_count_current": restart_count,
        "restart_count_equal": predicates["restart_count_equal"],
        "restart_count_expected": EXPECTED_RESTART_COUNT,
        "route_equal": predicates["route_equal"],
        "units_active_enabled": predicates["units_active_enabled"],
    }


def evaluate_foreign_diagnosis(observation: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(observation, Mapping) or set(observation) != FOREIGN_DIAGNOSIS_KEYS:
        raise DiagnosisError("foreign", "foreign_observation_failed")
    for key in (
        "foreign_container_entries",
        "foreign_expected_entries",
        "foreign_persistent_entries",
        "foreign_unit_entries",
    ):
        value = observation[key]
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 4096:
            raise DiagnosisError("foreign", "foreign_observation_failed")
    for key in (
        "foreign_count_equal",
        "foreign_expected_equal",
        "foreign_repeat_equal",
    ):
        if not isinstance(observation[key], bool):
            raise DiagnosisError("foreign", "foreign_observation_failed")
    for key in ("foreign_stable_sha256_after", "foreign_stable_sha256_before"):
        if not isinstance(observation[key], str) or SHA_PATTERN.fullmatch(observation[key]) is None:
            raise DiagnosisError("foreign", "foreign_observation_failed")
    if (
        observation["foreign_container_entries"] + observation["foreign_unit_entries"]
        != observation["foreign_persistent_entries"]
    ):
        raise DiagnosisError("foreign", "foreign_observation_failed")
    return dict(observation)


def _load_foundation(value: bytes) -> ModuleType:
    module = ModuleType("phase13_awg2_diagnosis_foundation")
    try:
        exec(compile(value, "<foundation>", "exec"), module.__dict__)
    except Exception as error:
        raise DiagnosisError("foundation", "foundation_invalid") from error
    if not hasattr(module, "RealSpainBackend") or not hasattr(module, "RemoteStageError"):
        raise DiagnosisError("foundation", "foundation_invalid")
    return module


class LiveDiagnosisBackend:
    """Collect the exact production AWG2 predicate inputs without mutation."""

    def __init__(self, foundation: ModuleType) -> None:
        self.foundation = foundation
        self.backend = foundation.RealSpainBackend()

    def _peer_set(self, values: list[str]) -> tuple[str, ...]:
        peers = tuple(sorted(value for value in values if value))
        if len(set(peers)) != len(peers) or any(PEER_PATTERN.fullmatch(peer) is None for peer in peers):
            raise DiagnosisError("observation", "observation_invalid")
        return peers

    def _persistent_peers(self) -> tuple[str, ...]:
        database = self.foundation.LIVE_DATABASE
        connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
        try:
            connection.execute("PRAGMA query_only=ON")
            rows = connection.execute(
                "SELECT peer_public_key FROM devices WHERE status = ? ORDER BY peer_public_key",
                ("active",),
            ).fetchall()
        except sqlite3.Error as error:
            raise DiagnosisError("observation", "observation_failed") from error
        finally:
            connection.close()
        if any(len(row) != 1 or not isinstance(row[0], str) for row in rows):
            raise DiagnosisError("observation", "observation_invalid")
        return self._peer_set([str(row[0]) for row in rows])

    def collect_awg2_observation(self) -> dict[str, object]:
        f = self.foundation
        try:
            inspect_raw = self.backend._run(
                (f.DOCKER, f"--host={f.DOCKER_HOST}", "inspect", f.AWG_CONTAINER)
            )
            item = json.loads(inspect_raw)[0]
            unit_states = {
                unit: self.backend._service_values(unit)
                for unit in f.EXPECTED_ACTIVE_ENABLED_UNITS
            }
            live_peers = self._peer_set(
                self.backend._run(
                    (
                        f.DOCKER,
                        f"--host={f.DOCKER_HOST}",
                        "exec",
                        f.AWG_CONTAINER,
                        "wg",
                        "show",
                        f.AWG_INTERFACE,
                        "peers",
                    )
                ).decode("ascii", errors="strict").splitlines()
            )
            persistent_peers = self._persistent_peers()
            listen_port = self.backend._run(
                (
                    f.DOCKER,
                    f"--host={f.DOCKER_HOST}",
                    "exec",
                    f.AWG_CONTAINER,
                    "wg",
                    "show",
                    f.AWG_INTERFACE,
                    "listen-port",
                )
            ).strip()
            forwarding = self.backend._run(
                (
                    f.DOCKER,
                    f"--host={f.DOCKER_HOST}",
                    "exec",
                    f.AWG_CONTAINER,
                    "sysctl",
                    "-n",
                    "net.ipv4.ip_forward",
                )
            ).strip()
            routes = json.loads(
                self.backend._run(
                    ("/usr/sbin/ip", "-j", "route", "show", "exact", f.EXPECTED_VPN_CIDR)
                )
            )
            nft = json.loads(
                self.backend._run(("/usr/sbin/nft", "-j", "list", "table", "inet", "amn2_spain"))
            )
            comments = [
                str(entry["rule"].get("comment", ""))
                for entry in nft.get("nftables", [])
                if isinstance(entry, dict)
                and isinstance(entry.get("rule"), dict)
                and entry["rule"].get("chain") == "forward"
                and str(entry["rule"].get("comment", "")).startswith("amn2_spain:")
            ]
            route_matches = [
                route
                for route in routes
                if isinstance(route, dict)
                and route.get("dst") == f.EXPECTED_VPN_CIDR
                and route.get("dev") == f.EXPECTED_ROUTE_DEVICE
            ] if isinstance(routes, list) else []
            restart_count = item["RestartCount"]
            if isinstance(restart_count, bool) or not isinstance(restart_count, int):
                raise DiagnosisError("observation", "observation_invalid")
            image = item["Image"]
            network_mode = item["HostConfig"]["NetworkMode"]
            running = item["State"]["Running"]
            sysctls = item["HostConfig"].get("Sysctls") or {}
        except DiagnosisError:
            raise
        except Exception as error:
            raise DiagnosisError("observation", "observation_failed") from error
        return {
            "configured_ip_forward_equal": sysctls.get("net.ipv4.ip_forward") in {None, "1"},
            "container_running": running is True,
            "forward_comments_equal": set(comments) == set(f.EXPECTED_FORWARD_COMMENTS),
            "forward_rule_count": len(comments),
            "image_present": isinstance(image, str) and bool(image),
            "listen_port_equal": listen_port == str(f.EXPECTED_UDP_PORT).encode("ascii"),
            "live_ip_forward_equal": forwarding == b"1",
            "live_peer_count": len(live_peers),
            "network_mode_equal": network_mode == f.EXPECTED_AWG_NETWORK,
            "peer_sets_equal": persistent_peers == live_peers,
            "persistent_peer_count": len(persistent_peers),
            "restart_count_current": restart_count,
            "route_equal": len(route_matches) == 1,
            "units_active_enabled": all(
                values.get("ActiveState") == "active"
                and values.get("UnitFileState") == "enabled"
                for values in unit_states.values()
            ),
        }

    def collect_foreign_diagnosis(self) -> dict[str, object]:
        try:
            before = self.backend._collect_foreign_rows()
            after = self.backend._collect_foreign_rows()
            persistent = sorted(set(before).intersection(after))
            before_rows = [before[identity] for identity in persistent]
            after_rows = [after[identity] for identity in persistent]
            before_digest = self.backend._phase12_stable_digest(before_rows)
            after_digest = self.backend._phase12_stable_digest(after_rows)
            expected_entries = self.foundation.EXPECTED_FOREIGN_PERSISTENT_ENTRIES
            expected_digest = self.foundation.EXPECTED_FOREIGN_STABLE_SHA256
            if (
                isinstance(expected_entries, bool)
                or not isinstance(expected_entries, int)
                or not isinstance(expected_digest, str)
                or SHA_PATTERN.fullmatch(expected_digest) is None
            ):
                raise DiagnosisError("foreign", "foreign_observation_failed")
        except Exception as error:
            if isinstance(error, DiagnosisError):
                raise
            raise DiagnosisError("foreign", "foreign_observation_failed") from error
        return evaluate_foreign_diagnosis(
            {
                "foreign_container_entries": sum(
                    row.get("kind") == "container" for row in before_rows
                ),
                "foreign_count_equal": len(persistent) == expected_entries,
                "foreign_expected_entries": expected_entries,
                "foreign_expected_equal": before_digest == expected_digest,
                "foreign_persistent_entries": len(persistent),
                "foreign_repeat_equal": before_digest == after_digest,
                "foreign_stable_sha256_after": after_digest,
                "foreign_stable_sha256_before": before_digest,
                "foreign_unit_entries": sum(
                    row.get("kind") == "unit" for row in before_rows
                ),
            }
        )


def _failure_receipt(outcome_id: str, stage: str, reason: str) -> dict[str, object]:
    return {
        "awg2_equal": False,
        "awg2_equal_without_restart_count": False,
        "configured_ip_forward_equal": False,
        "container_running": False,
        "expected_forward_rule_count": EXPECTED_FORWARD_RULE_COUNT,
        "expected_peer_count": EXPECTED_PEER_COUNT,
        "failed_predicates": [],
        "foreign_equal": False,
        "foreign_container_entries": 0,
        "foreign_count_equal": False,
        "foreign_expected_entries": 0,
        "foreign_expected_equal": False,
        "foreign_observed": False,
        "foreign_persistent_entries": 0,
        "foreign_repeat_equal": False,
        "foreign_stable_sha256_after": "0" * 64,
        "foreign_stable_sha256_before": "0" * 64,
        "foreign_unit_entries": 0,
        "forward_comments_equal": False,
        "forward_rule_count": 0,
        "forward_rule_count_equal": False,
        "image_present": False,
        "listen_port_equal": False,
        "live_ip_forward_equal": False,
        "live_peer_count": 0,
        "live_peer_count_equal": False,
        "mutation_performed": False,
        "network_mode_equal": False,
        "outcome": "failure",
        "outcome_id": outcome_id,
        "peer_sets_equal": False,
        "persistent_peer_count": 0,
        "persistent_peer_count_equal": False,
        "raw_output_persisted": False,
        "reason": reason,
        "restart_count_current": 0,
        "restart_count_equal": False,
        "restart_count_expected": EXPECTED_RESTART_COUNT,
        "route_equal": False,
        "schema": RECEIPT_SCHEMA,
        "stage": stage,
        "units_active_enabled": False,
    }


def execute_diagnosis(payload: dict[str, object], backend: DiagnosisBackend) -> dict[str, object]:
    outcome_id = str(payload.get("outcome_id", "invalid"))
    try:
        if set(payload) != {"expires_at", "max_attempts", "outcome_id", "schema"}:
            raise DiagnosisError("payload", "payload_invalid")
        expires_at = _parse_utc(payload["expires_at"])
        if (
            payload.get("schema") != PAYLOAD_SCHEMA
            or payload.get("max_attempts") != 1
            or OUTCOME_PATTERN.fullmatch(outcome_id) is None
            or expires_at <= datetime.now(UTC)
        ):
            raise DiagnosisError("payload", "payload_invalid")
        evaluated = evaluate_awg2_observation(backend.collect_awg2_observation())
        foreign_observed = True
        reason = "diagnosed"
        try:
            foreign = evaluate_foreign_diagnosis(backend.collect_foreign_diagnosis())
            foreign_equal = bool(
                foreign["foreign_count_equal"]
                and foreign["foreign_repeat_equal"]
                and foreign["foreign_expected_equal"]
            )
        except DiagnosisError as error:
            if error.stage != "foreign" or error.reason != "foreign_observation_failed":
                raise
            foreign_equal = False
            foreign_observed = False
            reason = "diagnosed_foreign_unavailable"
            foreign = {
                "foreign_container_entries": 0,
                "foreign_count_equal": False,
                "foreign_expected_entries": 0,
                "foreign_expected_equal": False,
                "foreign_persistent_entries": 0,
                "foreign_repeat_equal": False,
                "foreign_stable_sha256_after": "0" * 64,
                "foreign_stable_sha256_before": "0" * 64,
                "foreign_unit_entries": 0,
            }
        return {
            **evaluated,
            **foreign,
            "foreign_equal": foreign_equal,
            "foreign_observed": foreign_observed,
            "mutation_performed": False,
            "outcome": "success",
            "outcome_id": outcome_id,
            "raw_output_persisted": False,
            "reason": reason,
            "schema": RECEIPT_SCHEMA,
            "stage": "complete",
        }
    except DiagnosisError as error:
        return _failure_receipt(outcome_id, error.stage, error.reason)
    except Exception:
        return _failure_receipt(outcome_id, "internal", "internal_failure")


def main_bound_envelope(envelope: object) -> None:
    if not isinstance(envelope, dict) or set(envelope) != {
        "foundation_b64", "foundation_sha256", "payload_b64", "payload_sha256"
    }:
        raise SystemExit(70)
    try:
        foundation_bytes = base64.b64decode(str(envelope["foundation_b64"]), validate=True)
        payload_bytes = base64.b64decode(str(envelope["payload_b64"]), validate=True)
        if (
            sha256_bytes(foundation_bytes) != envelope["foundation_sha256"]
            or sha256_bytes(payload_bytes) != envelope["payload_sha256"]
            or len(foundation_bytes) > 1024 * 1024
            or len(payload_bytes) > 64 * 1024
        ):
            raise ValueError
        payload = json.loads(payload_bytes)
        if canonical_json_bytes(payload) != payload_bytes:
            raise ValueError
    except (ValueError, TypeError, json.JSONDecodeError):
        raise SystemExit(70)
    foundation = _load_foundation(foundation_bytes)
    receipt = execute_diagnosis(payload, LiveDiagnosisBackend(foundation))
    sys.stdout.buffer.write(canonical_json_bytes(receipt))
