"""Fixed-path Spain disabled-stage and web/data-apply executor.

The file deliberately has no command-line mode or path arguments.  The bound
PowerShell orchestrator appends one call to ``main_bound_payload`` and sends the
combined bytes through the third and final SSH stdin stream.
"""

from __future__ import annotations

import base64
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import sqlite3
import stat
import subprocess
from typing import Iterator, Mapping, Protocol
from urllib.error import URLError
from urllib.request import urlopen


MAX_INPUT_BYTES = 1024 * 1024
MAX_DATABASE_BYTES = 64 * 1024 * 1024
OUTCOME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

LIVE_DATABASE = Path("/var/lib/amn2-spain/amn2.sqlite3")
RUNTIME_ENVIRONMENT = Path("/etc/amn2-spain/runtime.env")
BOT_ENABLE_MARKER = Path("/etc/amn2-spain/bot-enabled")
PROTECTED_ROOT = Path("/var/lib/amn2-phase13-bot-web-migration")
WEB_UNIT = "amn2-spain-web.service"
BOT_UNIT = "amn2-spain-bot.service"
DOCKER = "/opt/amn2-spain/docker/bin/docker"
DOCKER_HOST = "unix:///run/amn2-spain-docker/docker.sock"
SYSTEM_DOCKER = "/usr/bin/docker"
AWG_CONTAINER = "amn2-spain-awg"
AWG_INTERFACE = "awgsp0"
EXPECTED_AWG_NETWORK = "amn2-spain-net"
EXPECTED_UDP_PORT = 30001
EXPECTED_VPN_CIDR = "10.212.12.0/24"
EXPECTED_ROUTE_DEVICE = "amn2spbr0"
EXPECTED_RESTART_COUNT = 59
EXPECTED_PEER_COUNT = 7
EXPECTED_FOREIGN_PERSISTENT_ENTRIES = 153
PEER_PUBLIC_KEY_PATTERN = re.compile(r"^[A-Za-z0-9+/]{43}=$")
EXPECTED_FORWARD_COMMENTS = {
    "amn2_spain:forward-dnat",
    "amn2_spain:forward-outbound",
    "amn2_spain:forward-return",
}
EXPECTED_ACTIVE_ENABLED_UNITS = (
    "amn2-spain-docker.service",
    "amn2-spain-network.service",
    "amn2-spain-forward-compat.service",
)
FOREIGN_EXCLUDED_CONTAINERS = {
    "amnezia-awg2",
    "amn2-spain-awg",
    "amn2-spain-awg3",
}
FOREIGN_EXCLUDED_UNITS = {
    "amneziya-web.service",
    "amneziya-bot.service",
    "amn2-spain-web.service",
    "amn2-spain-bot.service",
    "amn2-spain-docker.service",
    "amn2-spain-network.service",
    "amn2-spain-forward-compat.service",
    "amn2-spain-awg3.service",
}

EXPECTED_AWG2_FOUNDATION_SHA256 = (
    "0e5a5926821d88ae4a2515f9e95cd7c3f69db52100c1a1ec74e99fb794222281"
)
EXPECTED_FOREIGN_RECEIPT_SHA256 = (
    "bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704"
)
EXPECTED_FOREIGN_STABLE_SHA256 = (
    "f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8"
)

PAYLOAD_KEYS = {
    "audit",
    "bot_unit_b64",
    "bot_unit_sha256",
    "expires_at",
    "expected",
    "manifest_sha256",
    "max_attempts",
    "merged_database_b64",
    "outcome_id",
    "runtime_delta_encrypted_b64",
    "runtime_delta_encrypted_sha256",
    "schema",
}
EXPECTED_KEYS = {
    "awg2_foundation_sha256",
    "foreign_receipt_sha256",
    "foreign_stable_sha256",
    "merged_database_sha256",
    "spain_invariants_sha256",
    "target_before_database_sha256",
    "target_runtime_env_sha256",
}
AUDIT_KEYS = {"spain", "usa"}
SPAIN_AUDIT_KEYS = {
    "bot_active",
    "database_integrity_ok",
    "foreign_key_violations",
    "web_active",
    "web_loopback_only",
}


class RemoteStageError(RuntimeError):
    """A safe failure with an allowlisted stage and reason."""

    def __init__(self, stage: str, reason: str) -> None:
        super().__init__(reason)
        self.stage = stage
        self.reason = reason


class StageBackend(Protocol):
    def preflight(self, payload: dict[str, object]) -> None: ...

    def stage(self, payload: dict[str, object]) -> None: ...

    def stop_web(self) -> None: ...

    def apply_database(self, merged: bytes) -> None: ...

    def start_web(self) -> None: ...

    def post_apply_verify(self, payload: dict[str, object]) -> None: ...

    def rollback(self, payload: dict[str, object]) -> None: ...

    def emergency_restore(self, payload: dict[str, object]) -> None: ...

    def cleanup_pre_web_failure(self) -> None: ...

    def terminal_state(
        self, payload: dict[str, object], expected_database_sha256: str
    ) -> Mapping[str, bool]: ...


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _safe_receipt(
    *,
    outcome_id: str,
    outcome: str,
    stage: str,
    reason: str,
    rolled_back: bool,
    awg2_equal: bool,
    database_equal: bool,
    foreign_equal: bool,
    bot_active: bool,
    marker_present: bool,
    web_active: bool,
) -> dict[str, object]:
    return {
        "awg2_equal": awg2_equal,
        "bot_active": bot_active,
        "database_equal": database_equal,
        "foreign_equal": foreign_equal,
        "marker_present": marker_present,
        "outcome": outcome,
        "outcome_id": outcome_id,
        "raw_output_persisted": False,
        "reason": reason,
        "rolled_back": rolled_back,
        "schema": "amn2.phase13.bot-web-production-stage-receipt.v1",
        "stage": stage,
        "web_active": web_active,
    }


def _terminal_state(
    backend: StageBackend,
    payload: dict[str, object],
    expected_database_sha256: str,
) -> dict[str, bool]:
    defaults = {
        "awg2_equal": False,
        "bot_active": False,
        "database_equal": False,
        "foreign_equal": False,
        "marker_present": False,
        "web_active": False,
    }
    try:
        observed = backend.terminal_state(payload, expected_database_sha256)
    except Exception:
        return defaults
    if set(observed) != set(defaults) or any(
        not isinstance(value, bool) for value in observed.values()
    ):
        return defaults
    return dict(observed)


def _terminal_safe(state: Mapping[str, bool]) -> bool:
    return bool(
        state["database_equal"]
        and state["web_active"]
        and not state["bot_active"]
        and not state["marker_present"]
        and state["awg2_equal"]
        and state["foreign_equal"]
    )


def _parse_expiry(value: object) -> datetime:
    if not isinstance(value, str):
        raise RemoteStageError("package_verify", "schema_validation_failed")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise RemoteStageError("package_verify", "schema_validation_failed") from error
    if parsed.tzinfo is None or parsed.astimezone(timezone.utc) <= datetime.now(timezone.utc):
        raise RemoteStageError("package_verify", "package_expired")
    return parsed.astimezone(timezone.utc)


def _decode_b64(value: object, *, maximum: int) -> bytes:
    if not isinstance(value, str):
        raise RemoteStageError("package_verify", "schema_validation_failed")
    try:
        decoded = base64.b64decode(value, validate=True)
    except ValueError as error:
        raise RemoteStageError("package_verify", "checksum_mismatch") from error
    if not decoded or len(decoded) > maximum:
        raise RemoteStageError("package_verify", "bounded_input_invalid")
    return decoded


def _verify_sqlite_bytes(value: bytes) -> None:
    if not value.startswith(b"SQLite format 3\x00") or len(value) > MAX_DATABASE_BYTES:
        raise RemoteStageError("package_verify", "database_invalid")
    connection = sqlite3.connect(":memory:")
    try:
        connection.deserialize(value)
        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        foreign = connection.execute("PRAGMA foreign_key_check").fetchall()
    except sqlite3.Error as error:
        raise RemoteStageError("package_verify", "database_invalid") from error
    finally:
        connection.close()
    if integrity != ("ok",) or foreign:
        raise RemoteStageError("package_verify", "database_invalid")


def _validate_payload(envelope_bytes: bytes) -> tuple[dict[str, object], bytes]:
    if not isinstance(envelope_bytes, bytes) or not envelope_bytes or len(envelope_bytes) > MAX_INPUT_BYTES:
        raise RemoteStageError("package_verify", "bounded_input_invalid")
    try:
        envelope = json.loads(envelope_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RemoteStageError("package_verify", "schema_validation_failed") from error
    if (
        not isinstance(envelope, dict)
        or set(envelope) != {"payload", "payload_sha256", "schema"}
        or envelope.get("schema")
        != "amn2.phase13.bot-web-production-stage-envelope.v1"
        or canonical_json_bytes(envelope) != envelope_bytes
    ):
        raise RemoteStageError("package_verify", "schema_validation_failed")
    payload = envelope.get("payload")
    if not isinstance(payload, dict) or set(payload) != PAYLOAD_KEYS:
        raise RemoteStageError("package_verify", "schema_validation_failed")
    if envelope.get("payload_sha256") != sha256_bytes(canonical_json_bytes(payload)):
        raise RemoteStageError("package_verify", "checksum_mismatch")
    if (
        payload.get("schema") != "amn2.phase13.bot-web-production-stage-input.v1"
        or payload.get("max_attempts") != 1
        or not isinstance(payload.get("outcome_id"), str)
        or OUTCOME_PATTERN.fullmatch(str(payload["outcome_id"])) is None
        or not isinstance(payload.get("manifest_sha256"), str)
        or SHA256_PATTERN.fullmatch(str(payload["manifest_sha256"])) is None
    ):
        raise RemoteStageError("package_verify", "schema_validation_failed")
    _parse_expiry(payload.get("expires_at"))
    expected = payload.get("expected")
    audit = payload.get("audit")
    if (
        not isinstance(expected, dict)
        or set(expected) != EXPECTED_KEYS
        or any(
            not isinstance(expected[name], str)
            or SHA256_PATTERN.fullmatch(str(expected[name])) is None
            for name in EXPECTED_KEYS
        )
        or expected["awg2_foundation_sha256"] != EXPECTED_AWG2_FOUNDATION_SHA256
        or expected["foreign_receipt_sha256"] != EXPECTED_FOREIGN_RECEIPT_SHA256
        or expected["foreign_stable_sha256"] != EXPECTED_FOREIGN_STABLE_SHA256
        or not isinstance(audit, dict)
        or set(audit) != AUDIT_KEYS
        or not isinstance(audit.get("usa"), dict)
        or set(audit["usa"]) != {"bot_active"}
        or audit["usa"]["bot_active"] is not True
        or not isinstance(audit.get("spain"), dict)
        or set(audit["spain"]) != SPAIN_AUDIT_KEYS
        or audit["spain"]["bot_active"] is not False
        or audit["spain"]["web_active"] is not True
        or audit["spain"]["web_loopback_only"] is not True
        or audit["spain"]["database_integrity_ok"] is not True
        or audit["spain"]["foreign_key_violations"] != 0
    ):
        raise RemoteStageError("package_verify", "audit_incomplete")
    merged = _decode_b64(payload.get("merged_database_b64"), maximum=MAX_DATABASE_BYTES)
    if sha256_bytes(merged) != expected["merged_database_sha256"]:
        raise RemoteStageError("package_verify", "checksum_mismatch")
    _verify_sqlite_bytes(merged)
    runtime_delta = _decode_b64(
        payload.get("runtime_delta_encrypted_b64"), maximum=1024 * 1024
    )
    if sha256_bytes(runtime_delta) != payload.get("runtime_delta_encrypted_sha256"):
        raise RemoteStageError("package_verify", "checksum_mismatch")
    bot_unit = _decode_b64(payload.get("bot_unit_b64"), maximum=1024 * 1024)
    if sha256_bytes(bot_unit) != payload.get("bot_unit_sha256"):
        raise RemoteStageError("package_verify", "checksum_mismatch")
    unit_text = bot_unit.decode("utf-8", errors="strict")
    if (
        "ConditionPathExists=/etc/amn2-spain/bot-enabled" not in unit_text
        or "WantedBy=multi-user.target" not in unit_text
    ):
        raise RemoteStageError("package_verify", "bot_unit_invalid")
    return payload, merged


def execute_stage_web_data_apply(
    envelope_bytes: bytes, backend: StageBackend
) -> dict[str, object]:
    """Execute one bound attempt and return an allowlisted terminal receipt."""

    outcome_id = "invalid-outcome"
    try:
        payload, merged = _validate_payload(envelope_bytes)
        outcome_id = str(payload["outcome_id"])
    except RemoteStageError as error:
        return _safe_receipt(
            outcome_id=outcome_id,
            outcome="failed",
            stage=error.stage,
            reason=error.reason,
            rolled_back=False,
            awg2_equal=False,
            database_equal=False,
            foreign_equal=False,
            bot_active=False,
            marker_present=False,
            web_active=False,
        )

    stage = "preflight"
    live_boundary_started = False
    try:
        backend.preflight(payload)
        stage = "stage"
        backend.stage(payload)
        stage = "web_stop"
        live_boundary_started = True
        backend.stop_web()
        stage = "atomic_db_apply"
        backend.apply_database(merged)
        stage = "web_start"
        backend.start_web()
        stage = "post_apply_verify"
        backend.post_apply_verify(payload)
        expected = payload["expected"]
        assert isinstance(expected, dict)
        state = _terminal_state(backend, payload, str(expected["merged_database_sha256"]))
        if not _terminal_safe(state):
            raise RuntimeError("terminal state unverified")
        return _safe_receipt(
            outcome_id=outcome_id,
            outcome="passed",
            stage="post_apply_verify",
            reason="none",
            rolled_back=False,
            **state,
        )
    except Exception:
        expected = payload["expected"]
        assert isinstance(expected, dict)
        target_before_sha256 = str(expected["target_before_database_sha256"])
        if not live_boundary_started:
            try:
                backend.cleanup_pre_web_failure()
            except Exception:
                pass
            state = _terminal_state(backend, payload, target_before_sha256)
            return _safe_receipt(
                outcome_id=outcome_id,
                outcome="failed",
                stage=stage,
                reason="operation_failed" if _terminal_safe(state) else "terminal_state_unverified",
                rolled_back=False,
                **state,
            )
        try:
            backend.rollback(payload)
            state = _terminal_state(backend, payload, target_before_sha256)
            if not _terminal_safe(state):
                raise RuntimeError("primary rollback unverified")
            rolled_back = True
            reason = "operation_failed"
        except Exception:
            try:
                backend.emergency_restore(payload)
                state = _terminal_state(backend, payload, target_before_sha256)
                rolled_back = _terminal_safe(state)
                reason = "primary_rollback_failed"
            except Exception:
                state = _terminal_state(backend, payload, target_before_sha256)
                rolled_back = False
                reason = "rollback_failed"
            if not rolled_back:
                reason = "rollback_failed"
        return _safe_receipt(
            outcome_id=outcome_id,
            outcome="failed",
            stage=stage if rolled_back else "rollback",
            reason=reason,
            rolled_back=rolled_back,
            **state,
        )
    finally:
        merged_buffer = bytearray(merged)
        for index in range(len(merged_buffer)):
            merged_buffer[index] = 0


def _is_reparse(metadata: os.stat_result) -> bool:
    return bool(getattr(metadata, "st_file_attributes", 0) & 0x400)


def _regular_file(path: Path) -> os.stat_result:
    metadata = os.lstat(path)
    if stat.S_ISLNK(metadata.st_mode) or _is_reparse(metadata) or not stat.S_ISREG(metadata.st_mode):
        raise RemoteStageError("preflight", "unsafe_path")
    return metadata


def _sha256_file(path: Path) -> str:
    _regular_file(path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_create_new(path: Path, value: bytes, mode: int = 0o600) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, mode)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(path, mode)
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _sqlite_check_path(path: Path) -> None:
    _regular_file(path)
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        connection.execute("PRAGMA query_only=ON")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        foreign = connection.execute("PRAGMA foreign_key_check").fetchall()
    finally:
        connection.close()
    if integrity != ("ok",) or foreign:
        raise RemoteStageError("post_apply_verify", "database_invalid")


class RealSpainBackend:
    """Production backend with fixed files, units, socket and service actions."""

    def __init__(self) -> None:
        self.outcome_root: Path | None = None
        self.rollback_database: Path | None = None
        self.runtime_sha_before = ""
        self.awg_before = ""
        self.foreign_before = ""
        self.expected_target_sha = ""

    @staticmethod
    def _run(arguments: tuple[str, ...], *, timeout: int = 15) -> bytes:
        try:
            result = subprocess.run(
                arguments,
                check=False,
                capture_output=True,
                timeout=timeout,
            )
        except (OSError, subprocess.SubprocessError) as error:
            raise RemoteStageError("preflight", "observation_failed") from error
        if result.returncode != 0 or len(result.stdout) + len(result.stderr) > 1024 * 1024:
            raise RemoteStageError("preflight", "observation_failed")
        return result.stdout

    @classmethod
    def _service_values(cls, unit: str) -> dict[str, str]:
        output = cls._run(
            (
                "/usr/bin/systemctl",
                "show",
                unit,
                "--property=ActiveState,UnitFileState,MainPID,NRestarts",
            )
        ).decode("utf-8", errors="strict")
        values: dict[str, str] = {}
        for line in output.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values[key] = value
        if set(values) != {"ActiveState", "UnitFileState", "MainPID", "NRestarts"}:
            raise RemoteStageError("preflight", "service_observation_failed")
        return values

    @classmethod
    def _web_healthy(cls) -> bool:
        listener = cls._run(("/usr/bin/ss", "-ltnH", "sport = :3031")).decode(
            "utf-8", errors="strict"
        )
        lines = [line for line in listener.splitlines() if line.strip()]
        loopback = bool(lines) and all(
            "127.0.0.1:3031" in line or "[::1]:3031" in line for line in lines
        )
        if not loopback:
            return False
        try:
            with urlopen("http://127.0.0.1:3031/login", timeout=5) as response:
                return int(response.status) == 200
        except (OSError, URLError, ValueError):
            return False

    @staticmethod
    def _normalize_peer_set(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
        peers = tuple(sorted(value for value in values if value))
        if (
            len(peers) != EXPECTED_PEER_COUNT
            or len(set(peers)) != len(peers)
            or any(PEER_PUBLIC_KEY_PATTERN.fullmatch(peer) is None for peer in peers)
        ):
            raise RemoteStageError("preflight", "awg2_observation_failed")
        return peers

    @classmethod
    def _persistent_peer_set(cls) -> tuple[str, ...]:
        _regular_file(LIVE_DATABASE)
        connection = sqlite3.connect(f"file:{LIVE_DATABASE}?mode=ro", uri=True)
        try:
            connection.execute("PRAGMA query_only=ON")
            rows = connection.execute(
                "SELECT peer_public_key FROM devices "
                "WHERE status = ? ORDER BY peer_public_key",
                ("active",),
            ).fetchall()
        except sqlite3.Error as error:
            raise RemoteStageError("preflight", "awg2_observation_failed") from error
        finally:
            connection.close()
        if any(
            len(row) != 1 or not isinstance(row[0], str)
            for row in rows
        ):
            raise RemoteStageError("preflight", "awg2_observation_failed")
        return cls._normalize_peer_set([str(row[0]) for row in rows])

    @classmethod
    def _awg_snapshot(cls) -> str:
        inspect_raw = cls._run(
            (DOCKER, f"--host={DOCKER_HOST}", "inspect", AWG_CONTAINER)
        )
        try:
            document = json.loads(inspect_raw)
            item = document[0]
            unit_states = {
                unit: cls._service_values(unit)
                for unit in EXPECTED_ACTIVE_ENABLED_UNITS
            }
            selected = {
                "image": item["Image"],
                "network_mode": item["HostConfig"]["NetworkMode"],
                "restart_count": item["RestartCount"],
                "running": item["State"]["Running"],
                "sysctls": item["HostConfig"].get("Sysctls") or {},
                "units": {
                    unit: {
                        "active": values["ActiveState"],
                        "enabled": values["UnitFileState"],
                        "restart_count": values["NRestarts"],
                    }
                    for unit, values in unit_states.items()
                },
            }
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise RemoteStageError("preflight", "awg2_observation_failed") from error
        live_peers = cls._normalize_peer_set(cls._run(
            (
                DOCKER,
                f"--host={DOCKER_HOST}",
                "exec",
                AWG_CONTAINER,
                "wg",
                "show",
                AWG_INTERFACE,
                "peers",
            )
        ).decode("ascii", errors="strict").splitlines())
        persistent_peers = cls._persistent_peer_set()
        listen_port = cls._run(
            (
                DOCKER,
                f"--host={DOCKER_HOST}",
                "exec",
                AWG_CONTAINER,
                "wg",
                "show",
                AWG_INTERFACE,
                "listen-port",
            )
        ).strip()
        forwarding = cls._run(
            (
                DOCKER,
                f"--host={DOCKER_HOST}",
                "exec",
                AWG_CONTAINER,
                "sysctl",
                "-n",
                "net.ipv4.ip_forward",
            )
        ).strip()
        route_raw = cls._run(
            (
                "/usr/sbin/ip",
                "-j",
                "route",
                "show",
                "exact",
                EXPECTED_VPN_CIDR,
            )
        )
        nft_raw = cls._run(("/usr/sbin/nft", "-j", "list", "table", "inet", "amn2_spain"))
        try:
            routes = json.loads(route_raw)
            nft = json.loads(nft_raw)
            tagged_forward_comments = [
                str(entry["rule"].get("comment", ""))
                for entry in nft.get("nftables", [])
                if isinstance(entry, dict)
                and isinstance(entry.get("rule"), dict)
                and entry["rule"].get("chain") == "forward"
                and str(entry["rule"].get("comment", "")).startswith("amn2_spain:")
            ]
        except (TypeError, json.JSONDecodeError) as error:
            raise RemoteStageError("preflight", "awg2_observation_failed") from error
        route_matches = [
            route
            for route in routes
            if isinstance(route, dict)
            and route.get("dst") == EXPECTED_VPN_CIDR
            and route.get("dev") == EXPECTED_ROUTE_DEVICE
        ] if isinstance(routes, list) else []
        if (
            selected["running"] is not True
            or not isinstance(selected["image"], str)
            or not selected["image"]
            or selected["network_mode"] != EXPECTED_AWG_NETWORK
            or selected["restart_count"] != EXPECTED_RESTART_COUNT
            or selected["sysctls"].get("net.ipv4.ip_forward") not in {None, "1"}
            or any(
                values["ActiveState"] != "active"
                or values["UnitFileState"] != "enabled"
                for values in unit_states.values()
            )
            or forwarding != b"1"
            or listen_port != str(EXPECTED_UDP_PORT).encode("ascii")
            or persistent_peers != live_peers
            or len(route_matches) != 1
            or len(tagged_forward_comments) != len(EXPECTED_FORWARD_COMMENTS)
            or set(tagged_forward_comments) != EXPECTED_FORWARD_COMMENTS
        ):
            raise RemoteStageError("preflight", "awg2_equality_mismatch")
        selected["peer_set_sha256"] = sha256_bytes(
            canonical_json_bytes(list(live_peers))
        )
        selected["forward_comments"] = sorted(tagged_forward_comments)
        selected["listen_port"] = EXPECTED_UDP_PORT
        selected["route"] = f"{EXPECTED_VPN_CIDR}|{EXPECTED_ROUTE_DEVICE}"
        return sha256_bytes(canonical_json_bytes(selected))

    @classmethod
    def _foreign_unit_bound_status(cls, unit: str, active_state: str) -> str:
        control_group = cls._run(
            (
                "/usr/bin/systemctl",
                "show",
                unit,
                "--property=ControlGroup",
                "--value",
            )
        ).decode("utf-8", errors="strict").rstrip("\n")
        if control_group:
            return "cgroup_complete"
        main_pid = cls._run(
            (
                "/usr/bin/systemctl",
                "show",
                unit,
                "--property=MainPID",
                "--value",
            )
        ).decode("ascii", errors="strict").strip()
        if not main_pid.isdigit():
            raise RemoteStageError("preflight", "foreign_observation_failed")
        if main_pid == "0":
            return "active_exited_no_live_process" if active_state == "active" else "no_cgroup"
        canonical_id = cls._run(
            (
                "/usr/bin/systemctl",
                "show",
                unit,
                "--property=Id",
                "--value",
            )
        ).decode("utf-8", errors="strict").strip()
        cgroup = cls._run(("/usr/bin/cat", f"/proc/{main_pid}/cgroup")).decode(
            "utf-8", errors="strict"
        )
        if not canonical_id or (
            f"/{canonical_id}" not in cgroup
            and f"/{canonical_id}/" not in cgroup
        ):
            raise RemoteStageError("preflight", "foreign_observation_failed")
        return "mainpid_cgroup_complete"

    @classmethod
    def _system_docker_available(cls) -> bool:
        return os.path.isfile(SYSTEM_DOCKER) and os.access(SYSTEM_DOCKER, os.X_OK)

    @classmethod
    def _collect_foreign_rows(cls) -> dict[tuple[str, str], dict[str, object]]:
        rows: list[dict[str, object]] = []
        docker_output = b""
        if cls._system_docker_available():
            docker_output = cls._run(
                (
                    SYSTEM_DOCKER,
                    "ps",
                    "-a",
                    "--format",
                    "{{.Names}}|{{.Image}}|{{.State}}",
                )
            )
        docker_text = docker_output.decode("utf-8", errors="strict")
        for line in docker_text.splitlines():
            if not line:
                continue
            parts = line.split("|")
            if len(parts) != 3:
                raise RemoteStageError("preflight", "foreign_observation_failed")
            name, image, state_value = parts
            if name in FOREIGN_EXCLUDED_CONTAINERS:
                continue
            if (
                not name
                or not image
                or re.fullmatch(r"[A-Za-z0-9_.:+-]+", state_value) is None
            ):
                raise RemoteStageError("preflight", "foreign_observation_failed")
            restart_text = cls._run(
                (SYSTEM_DOCKER, "inspect", "--format", "{{.RestartCount}}", name)
            ).decode("ascii", errors="strict").strip()
            if not restart_text.isdigit():
                raise RemoteStageError("preflight", "foreign_observation_failed")
            rows.append(
                {
                    "active_state": state_value,
                    "image_or_unit_sha256": sha256_bytes(image.encode("utf-8")),
                    "kind": "container",
                    "name_sha256": sha256_bytes(name.encode("utf-8")),
                    "restart_count": int(restart_text),
                }
            )

        systemd_output = cls._run(
            (
                "/usr/bin/systemctl",
                "list-units",
                "--type=service",
                "--all",
                "--no-legend",
                "--no-pager",
            ),
            timeout=30,
        ).decode("utf-8", errors="strict")
        for line in systemd_output.splitlines():
            parts = line.split(maxsplit=4)
            if not parts:
                continue
            unit = parts[0]
            if not unit.endswith(".service"):
                continue
            if unit in FOREIGN_EXCLUDED_UNITS:
                continue
            if len(parts) < 4:
                raise RemoteStageError("preflight", "foreign_observation_failed")
            active_state, sub_state = parts[2], parts[3]
            combined_state = f"{active_state}:{sub_state}"
            if re.fullmatch(r"[A-Za-z0-9_.:+-]+", combined_state) is None:
                raise RemoteStageError("preflight", "foreign_observation_failed")
            unit_content = cls._run(
                ("/usr/bin/systemctl", "cat", unit, "--no-pager")
            ).rstrip(b"\n")
            restart_text = cls._run(
                (
                    "/usr/bin/systemctl",
                    "show",
                    unit,
                    "--property=NRestarts",
                    "--value",
                )
            ).decode("ascii", errors="strict").strip()
            if not restart_text.isdigit():
                raise RemoteStageError("preflight", "foreign_observation_failed")
            bound_status = cls._foreign_unit_bound_status(unit, active_state)
            if re.fullmatch(r"[A-Za-z0-9_.:+-]+", bound_status) is None:
                raise RemoteStageError("preflight", "foreign_observation_failed")
            rows.append(
                {
                    "active_state": combined_state,
                    "bound_port_status": bound_status,
                    "image_or_unit_sha256": sha256_bytes(unit_content),
                    "kind": "unit",
                    "name_sha256": sha256_bytes(unit.encode("utf-8")),
                    "restart_count": int(restart_text),
                    "unit_content_status": "exact",
                }
            )
        by_identity: dict[tuple[str, str], dict[str, object]] = {}
        for row in rows:
            identity = (str(row["kind"]), str(row["name_sha256"]))
            if identity in by_identity:
                raise RemoteStageError("preflight", "foreign_observation_failed")
            by_identity[identity] = row
        return by_identity

    @staticmethod
    def _phase12_stable_digest(rows: list[dict[str, object]]) -> str:
        stable = []
        for row in rows:
            item = dict(row)
            item.pop("bound_port_set", None)
            item.pop("restart_count", None)
            stable.append(item)
        stable.sort(key=lambda row: (str(row["kind"]), str(row["name_sha256"])))
        encoded = json.dumps(
            stable,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return sha256_bytes(encoded)

    @classmethod
    def _foreign_snapshot(cls) -> str:
        before = cls._collect_foreign_rows()
        after = cls._collect_foreign_rows()
        persistent = sorted(set(before).intersection(after))
        before_rows = [before[identity] for identity in persistent]
        after_rows = [after[identity] for identity in persistent]
        before_digest = cls._phase12_stable_digest(before_rows)
        after_digest = cls._phase12_stable_digest(after_rows)
        if (
            len(persistent) != EXPECTED_FOREIGN_PERSISTENT_ENTRIES
            or before_digest != after_digest
            or before_digest != EXPECTED_FOREIGN_STABLE_SHA256
        ):
            raise RemoteStageError("preflight", "foreign_equality_mismatch")
        return before_digest

    def _assert_bot_disabled(self) -> None:
        bot = self._service_values(BOT_UNIT)
        if (
            bot["ActiveState"] == "active"
            or bot["MainPID"] not in {"", "0"}
            or bot["UnitFileState"] != "disabled"
        ):
            raise RemoteStageError("preflight", "bot_not_disabled")
        if os.path.lexists(BOT_ENABLE_MARKER):
            raise RemoteStageError("preflight", "bot_marker_present")

    def preflight(self, payload: dict[str, object]) -> None:
        expected = payload["expected"]
        assert isinstance(expected, dict)
        _regular_file(LIVE_DATABASE)
        _regular_file(RUNTIME_ENVIRONMENT)
        self._assert_bot_disabled()
        web = self._service_values(WEB_UNIT)
        if (
            web["ActiveState"] != "active"
            or web["UnitFileState"] != "enabled"
            or not self._web_healthy()
        ):
            raise RemoteStageError("preflight", "web_not_healthy")
        if _sha256_file(LIVE_DATABASE) != expected["target_before_database_sha256"]:
            raise RemoteStageError("preflight", "target_database_changed")
        if _sha256_file(RUNTIME_ENVIRONMENT) != expected["target_runtime_env_sha256"]:
            raise RemoteStageError("preflight", "target_runtime_changed")
        _sqlite_check_path(LIVE_DATABASE)
        outcome_root = PROTECTED_ROOT / str(payload["outcome_id"])
        if os.path.lexists(outcome_root):
            raise RemoteStageError("preflight", "stage_replay")
        self.expected_target_sha = str(expected["target_before_database_sha256"])
        self.runtime_sha_before = str(expected["target_runtime_env_sha256"])
        self.awg_before = self._awg_snapshot()
        self.foreign_before = self._foreign_snapshot()

    def stage(self, payload: dict[str, object]) -> None:
        expected = payload["expected"]
        assert isinstance(expected, dict)
        merged = base64.b64decode(str(payload["merged_database_b64"]), validate=True)
        runtime_delta = base64.b64decode(
            str(payload["runtime_delta_encrypted_b64"]), validate=True
        )
        bot_unit = base64.b64decode(str(payload["bot_unit_b64"]), validate=True)
        try:
            PROTECTED_ROOT.mkdir(mode=0o700, parents=False, exist_ok=True)
            root = PROTECTED_ROOT / str(payload["outcome_id"])
            root.mkdir(mode=0o700, exist_ok=False)
            staged = root / "staged"
            rollback = root / "rollback"
            staged.mkdir(mode=0o700)
            rollback.mkdir(mode=0o700)
            _write_create_new(staged / "merged-target.sqlite3", merged)
            _write_create_new(staged / "runtime.env.delta.enc", runtime_delta)
            _write_create_new(staged / "amn2-spain-bot.service", bot_unit)
            rollback_database = rollback / "target-before.sqlite3"
            source = sqlite3.connect(f"file:{LIVE_DATABASE}?mode=ro", uri=True)
            target = sqlite3.connect(rollback_database)
            try:
                source.backup(target)
                target.commit()
            finally:
                target.close()
                source.close()
            os.chmod(rollback_database, 0o600)
            if _sha256_file(rollback_database) != self.expected_target_sha:
                raise RemoteStageError("stage", "rollback_copy_mismatch")
            state = {
                "bot_disabled": True,
                "live_database_applied": False,
                "manifest_sha256": payload["manifest_sha256"],
                "outcome_id": payload["outcome_id"],
                "schema": "amn2.phase13.bot-web-production-stage-state.v1",
                "web_active": True,
            }
            _write_create_new(root / "state.json", canonical_json_bytes(state))
            self.outcome_root = root
            self.rollback_database = rollback_database
        finally:
            for value in (merged, runtime_delta):
                buffer = bytearray(value)
                for index in range(len(buffer)):
                    buffer[index] = 0

    def stop_web(self) -> None:
        self._run(("/usr/bin/systemctl", "stop", WEB_UNIT), timeout=30)
        if self._service_values(WEB_UNIT)["ActiveState"] == "active":
            raise RemoteStageError("web_stop", "web_stop_failed")

    def apply_database(self, merged: bytes) -> None:
        metadata = _regular_file(LIVE_DATABASE)
        temporary = LIVE_DATABASE.parent / ".phase13-merged.sqlite3.tmp"
        if os.path.lexists(temporary):
            raise RemoteStageError("atomic_db_apply", "temporary_path_exists")
        try:
            _write_create_new(temporary, merged, stat.S_IMODE(metadata.st_mode))
            os.chown(temporary, metadata.st_uid, metadata.st_gid)
            if _sha256_file(temporary) != sha256_bytes(merged):
                raise RemoteStageError("atomic_db_apply", "checksum_mismatch")
            os.replace(temporary, LIVE_DATABASE)
            directory = os.open(LIVE_DATABASE.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.lexists(temporary):
                try:
                    temporary.unlink()
                except OSError:
                    pass

    def start_web(self) -> None:
        self._run(("/usr/bin/systemctl", "start", WEB_UNIT), timeout=30)
        if self._service_values(WEB_UNIT)["ActiveState"] != "active":
            raise RemoteStageError("web_start", "web_start_failed")

    def post_apply_verify(self, payload: dict[str, object]) -> None:
        expected = payload["expected"]
        assert isinstance(expected, dict)
        if _sha256_file(LIVE_DATABASE) != expected["merged_database_sha256"]:
            raise RemoteStageError("post_apply_verify", "database_mismatch")
        _sqlite_check_path(LIVE_DATABASE)
        if _sha256_file(RUNTIME_ENVIRONMENT) != self.runtime_sha_before:
            raise RemoteStageError("post_apply_verify", "target_runtime_changed")
        self._assert_bot_disabled()
        if not self._web_healthy():
            raise RemoteStageError("post_apply_verify", "web_not_healthy")
        if self._awg_snapshot() != self.awg_before:
            raise RemoteStageError("post_apply_verify", "awg2_equality_mismatch")
        if self._foreign_snapshot() != self.foreign_before:
            raise RemoteStageError("post_apply_verify", "foreign_equality_mismatch")

    def rollback(self, payload: dict[str, object]) -> None:
        if self.rollback_database is None:
            raise RemoteStageError("rollback", "rollback_state_missing")
        self._run(("/usr/bin/systemctl", "stop", WEB_UNIT), timeout=30)
        rollback = self.rollback_database.read_bytes()
        self.apply_database(rollback)
        self.start_web()
        if _sha256_file(LIVE_DATABASE) != self.expected_target_sha:
            raise RemoteStageError("rollback", "rollback_database_mismatch")
        _sqlite_check_path(LIVE_DATABASE)
        if _sha256_file(RUNTIME_ENVIRONMENT) != self.runtime_sha_before:
            raise RemoteStageError("rollback", "target_runtime_changed")
        self._assert_bot_disabled()
        if not self._web_healthy():
            raise RemoteStageError("rollback", "web_not_healthy")
        if self._awg_snapshot() != self.awg_before:
            raise RemoteStageError("rollback", "awg2_equality_mismatch")
        if self._foreign_snapshot() != self.foreign_before:
            raise RemoteStageError("rollback", "foreign_equality_mismatch")

    def emergency_restore(self, payload: dict[str, object]) -> None:
        self.rollback(payload)

    def terminal_state(
        self, payload: dict[str, object], expected_database_sha256: str
    ) -> Mapping[str, bool]:
        state = {
            "awg2_equal": False,
            "bot_active": False,
            "database_equal": False,
            "foreign_equal": False,
            "marker_present": bool(os.path.lexists(BOT_ENABLE_MARKER)),
            "web_active": False,
        }
        try:
            bot = self._service_values(BOT_UNIT)
            state["bot_active"] = bool(
                bot["ActiveState"] == "active"
                or bot["MainPID"] not in {"", "0"}
                or bot["UnitFileState"] != "disabled"
            )
        except Exception:
            state["bot_active"] = True
        try:
            state["database_equal"] = bool(
                _sha256_file(LIVE_DATABASE) == expected_database_sha256
            )
            if state["database_equal"]:
                _sqlite_check_path(LIVE_DATABASE)
        except Exception:
            state["database_equal"] = False
        try:
            web = self._service_values(WEB_UNIT)
            state["web_active"] = bool(
                web["ActiveState"] == "active"
                and web["UnitFileState"] == "enabled"
                and self._web_healthy()
            )
        except Exception:
            state["web_active"] = False
        try:
            state["awg2_equal"] = bool(
                self.awg_before and self._awg_snapshot() == self.awg_before
            )
        except Exception:
            state["awg2_equal"] = False
        try:
            state["foreign_equal"] = bool(
                self.foreign_before and self._foreign_snapshot() == self.foreign_before
            )
        except Exception:
            state["foreign_equal"] = False
        return state

    def cleanup_pre_web_failure(self) -> None:
        root = self.outcome_root
        if root is None or root.parent != PROTECTED_ROOT or not root.is_dir() or root.is_symlink():
            return
        expected = {
            root / "staged" / "merged-target.sqlite3",
            root / "staged" / "runtime.env.delta.enc",
            root / "staged" / "amn2-spain-bot.service",
            root / "rollback" / "target-before.sqlite3",
            root / "state.json",
        }
        observed = {path for path in root.rglob("*") if path.is_file()}
        if observed - expected:
            return
        for path in sorted(observed, key=lambda value: len(value.parts), reverse=True):
            if not path.is_symlink():
                path.unlink()
        for directory in (root / "staged", root / "rollback", root):
            if directory.exists() and not directory.is_symlink():
                directory.rmdir()


@contextmanager
def _fail_closed_signal_guard() -> Iterator[None]:
    """Convert transport termination into the normal rollback path."""

    previous = {
        signal.SIGHUP: signal.getsignal(signal.SIGHUP),
        signal.SIGTERM: signal.getsignal(signal.SIGTERM),
    }

    def fail_closed(_signum: int, _frame: object) -> None:
        raise RuntimeError("bounded transport interrupted")

    try:
        for signal_number in previous:
            signal.signal(signal_number, fail_closed)
        yield
    finally:
        for signal_number, handler in previous.items():
            signal.signal(signal_number, handler)


def main_bound_payload(encoded_envelope: str) -> int:
    """Decode one bounded payload and emit exactly one sanitized receipt."""

    try:
        envelope = base64.b64decode(encoded_envelope, validate=True)
        if len(envelope) > MAX_INPUT_BYTES:
            raise ValueError("oversized")
        with _fail_closed_signal_guard():
            receipt = execute_stage_web_data_apply(envelope, RealSpainBackend())
    except Exception:
        receipt = _safe_receipt(
            outcome_id="invalid-outcome",
            outcome="failed",
            stage="package_verify",
            reason="schema_validation_failed",
            rolled_back=False,
            awg2_equal=False,
            database_equal=False,
            foreign_equal=False,
            bot_active=False,
            marker_present=False,
            web_active=False,
        )
    print(canonical_json_bytes(receipt).decode("utf-8"), end="")
    return 0
