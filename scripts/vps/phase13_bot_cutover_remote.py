#!/usr/bin/env python3
"""Secret-safe fixed-role remote executor for the Phase 13 bot cutover."""

from __future__ import annotations

import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import subprocess
import sys
from types import ModuleType
from typing import Mapping, Protocol


UTC = timezone.utc
PAYLOAD_SCHEMA = "amn2.phase13.bot-cutover-payload.v1"
RECEIPT_SCHEMA = "amn2.phase13.bot-cutover-remote-receipt.v1"
OUTCOME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")
USA_UNIT = "amneziya-bot.service"
SPAIN_UNIT = "amn2-spain-bot.service"
SPAIN_MARKER = Path("/etc/amn2-spain/bot-enabled")
SPAIN_UNIT_PATH = Path("/etc/systemd/system/amn2-spain-bot.service")
CUTOVER_ROOT = Path("/var/lib/amn2-phase13-bot-cutover")
SPAIN_DATABASE = Path("/var/lib/amn2-spain/amn2.sqlite3")
SPAIN_RUNTIME = Path("/etc/amn2-spain/runtime.env")
SPAIN_SOURCE = Path("/opt/amn2-spain/runtime/source")
ALLOWED_TRANSITIONS = {
    "usa": {"preflight", "stop", "postflight", "rollback_start"},
    "spain": {"preflight", "start", "postflight", "rollback_stop"},
}
MUTATION_MODES = {"stop", "start", "rollback_start", "rollback_stop"}
CONTINUATION_KEYS = {
    "awg", "database", "foreign", "runtime", "source", "unit"
}
RECEIPT_KEYS = {
    "awg2_equal",
    "bot_active",
    "bot_enabled",
    "bot_process_count",
    "continuation",
    "database_equal",
    "foreign_equal",
    "marker_present",
    "outcome",
    "raw_output_persisted",
    "reason",
    "role",
    "runtime_equal",
    "schema",
    "service_action_performed",
    "source_equal",
    "web_loopback_healthy",
}


class RemoteCutoverError(RuntimeError):
    """Allowlisted remote failure without raw process detail."""


def validate_bot_unit(value: bytes) -> bytes:
    if (
        not isinstance(value, bytes)
        or not value
        or len(value) > 1024 * 1024
        or b"ConditionPathExists=/etc/amn2-spain/bot-enabled\n" not in value
        or b"WantedBy=multi-user.target\n" not in value
        or b"ExecStart=/usr/bin/python3 -B -m app.main\n" not in value
        or b"\x00" in value
    ):
        raise RemoteCutoverError("bot_unit_invalid")
    return value


class Backend(Protocol):
    def observe(
        self, role: str, continuation: Mapping[str, str] | None = None
    ) -> Mapping[str, object]: ...

    def mutate(
        self, role: str, mode: str, continuation: Mapping[str, str] | None = None
    ) -> Mapping[str, object]: ...


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _default_state() -> dict[str, object]:
    return {
        "awg2_equal": False,
        "bot_active": False,
        "bot_enabled": False,
        "bot_process_count": 0,
        "continuation": {},
        "database_equal": False,
        "foreign_equal": False,
        "marker_present": False,
        "runtime_equal": False,
        "source_equal": False,
        "web_loopback_healthy": False,
    }


def _receipt(
    *, role: str, outcome: str, reason: str, action: bool,
    state: Mapping[str, object] | None = None,
) -> dict[str, object]:
    result = _default_state()
    if state:
        for key in result:
            if key in state:
                result[key] = state[key]
    result.update(
        {
            "outcome": outcome,
            "raw_output_persisted": False,
            "reason": reason,
            "role": role if role in ALLOWED_TRANSITIONS else "unknown",
            "schema": RECEIPT_SCHEMA,
            "service_action_performed": action,
        }
    )
    return result


def _state_valid(state: Mapping[str, object]) -> bool:
    if not isinstance(state.get("bot_process_count"), int):
        return False
    if state["bot_process_count"] not in {0, 1}:
        return False
    for key in {
        "awg2_equal", "bot_active", "bot_enabled", "database_equal",
        "foreign_equal", "marker_present", "runtime_equal", "source_equal",
        "web_loopback_healthy",
    }:
        if key in state and not isinstance(state[key], bool):
            return False
    continuation = state.get("continuation", {})
    return bool(
        isinstance(continuation, dict)
        and set(continuation).issubset(CONTINUATION_KEYS)
        and all(
            isinstance(value, str) and SHA_PATTERN.fullmatch(value)
            for value in continuation.values()
        )
    )


def execute(value: object, backend: Backend) -> dict[str, object]:
    role = value.get("role") if isinstance(value, dict) else None
    mode = value.get("mode") if isinstance(value, dict) else None
    continuation = value.get("continuation", {}) if isinstance(value, dict) else {}
    action = bool(mode in MUTATION_MODES)
    if (
        role not in ALLOWED_TRANSITIONS
        or mode not in ALLOWED_TRANSITIONS[role]
        or not isinstance(continuation, dict)
        or set(continuation) - CONTINUATION_KEYS
        or any(
            not isinstance(item, str) or SHA_PATTERN.fullmatch(item) is None
            for item in continuation.values()
        )
    ):
        return _receipt(
            role=str(role), outcome="failure", reason="unsupported_transition",
            action=False,
        )
    state: Mapping[str, object] = {}
    try:
        state = (
            backend.mutate(role, mode, continuation)
            if action
            else backend.observe(role, continuation)
        )
        if not _state_valid(state):
            raise RemoteCutoverError("observation_failed")
        count = int(state["bot_process_count"])
        active = bool(state.get("bot_active", False))
        if active != (count == 1):
            raise RemoteCutoverError("observation_failed")
        if role == "spain" and mode == "preflight" and (
            active
            or bool(state.get("marker_present", False))
            or not bool(state.get("web_loopback_healthy", False))
            or not bool(state.get("awg2_equal", False))
            or not bool(state.get("foreign_equal", False))
            or not bool(state.get("database_equal", False))
            or not bool(state.get("runtime_equal", False))
            or not bool(state.get("source_equal", False))
        ):
            raise RemoteCutoverError("spain_preflight_failed")
        if role == "usa" and mode == "stop" and active:
            raise RemoteCutoverError("usa_bot_stop_unconfirmed")
        if role == "spain" and mode == "start" and (
            not active or not bool(state.get("marker_present", False))
        ):
            raise RemoteCutoverError("spain_bot_admission_failed")
        if role == "spain" and mode == "rollback_stop" and (
            active or bool(state.get("marker_present", False))
        ):
            raise RemoteCutoverError("rollback_failed")
        if role == "usa" and mode == "rollback_start" and not active:
            raise RemoteCutoverError("rollback_failed")
        return _receipt(
            role=role, outcome="success", reason="completed", action=action,
            state=state,
        )
    except RemoteCutoverError as error:
        return _receipt(
            role=role, outcome="failure", reason=str(error), action=action,
            state=state,
        )
    except Exception:
        return _receipt(
            role=role, outcome="failure", reason="internal_failure", action=action,
        )


def _regular_sha(path: Path) -> str:
    metadata = os.lstat(path)
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise RemoteCutoverError("observation_failed")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tree_sha(root: Path) -> str:
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RemoteCutoverError("observation_failed")
        if path.is_file():
            rows.append(
                {
                    "name": path.relative_to(root).as_posix(),
                    "sha256": _regular_sha(path),
                    "size": path.stat().st_size,
                }
            )
    return sha256_bytes(canonical_json_bytes(rows))


class LiveBackend:
    def __init__(self, foundation: ModuleType, payload: Mapping[str, object]) -> None:
        self.foundation = foundation
        self.spain = foundation.RealSpainBackend()
        self.outcome_id = str(payload["outcome_id"])
        try:
            unit = base64.b64decode(str(payload["bot_unit_b64"]), validate=True)
        except Exception as error:
            raise RemoteCutoverError("bot_unit_invalid") from error
        self.bot_unit = validate_bot_unit(unit)
        self.bot_unit_sha256 = str(payload["bot_unit_sha256"])
        if sha256_bytes(self.bot_unit) != self.bot_unit_sha256:
            raise RemoteCutoverError("bot_unit_invalid")
        self.rollback_root = CUTOVER_ROOT / self.outcome_id
        self.rollback_unit = self.rollback_root / "amn2-spain-bot.service.before"

    @staticmethod
    def _run(arguments: tuple[str, ...], *, require_success: bool = True) -> bytes:
        try:
            result = subprocess.run(
                arguments, check=False, capture_output=True, timeout=20
            )
        except (OSError, subprocess.SubprocessError) as error:
            raise RemoteCutoverError("service_action_failed") from error
        if (
            len(result.stdout) + len(result.stderr) > 1024 * 1024
            or (require_success and result.returncode != 0)
        ):
            raise RemoteCutoverError("service_action_failed")
        return result.stdout

    @classmethod
    def _service(cls, role: str) -> dict[str, str]:
        unit = USA_UNIT if role == "usa" else SPAIN_UNIT
        output = cls._run(
            (
                "/usr/bin/systemctl", "show", unit,
                "--property=ActiveState,UnitFileState,MainPID,NRestarts",
            )
        ).decode("utf-8", errors="strict")
        values = dict(line.split("=", 1) for line in output.splitlines() if "=" in line)
        if set(values) != {"ActiveState", "UnitFileState", "MainPID", "NRestarts"}:
            raise RemoteCutoverError("observation_failed")
        return values

    def _foreign_sha(self) -> str:
        before = self.spain._collect_foreign_rows()
        after = self.spain._collect_foreign_rows()
        persistent = sorted(set(before).intersection(after))
        before_rows = [before[identity] for identity in persistent]
        after_rows = [after[identity] for identity in persistent]
        before_digest = self.spain._phase12_stable_digest(before_rows)
        after_digest = self.spain._phase12_stable_digest(after_rows)
        if (
            not persistent
            or len(persistent) > 4096
            or before_digest != after_digest
            or SHA_PATTERN.fullmatch(before_digest) is None
        ):
            raise RemoteCutoverError("foreign_equality_mismatch")
        return before_digest

    @staticmethod
    def _safe_directory(path: Path) -> None:
        if os.path.lexists(path):
            metadata = os.lstat(path)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                raise RemoteCutoverError("unsafe_path")
            return
        os.mkdir(path, 0o700)

    @staticmethod
    def _write_create_new(path: Path, value: bytes) -> None:
        descriptor = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        try:
            with os.fdopen(descriptor, "wb") as handle:
                descriptor = -1
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
        finally:
            if descriptor >= 0:
                os.close(descriptor)

    @staticmethod
    def _atomic_replace(path: Path, value: bytes) -> None:
        temporary = path.with_name(path.name + ".phase13-new")
        if os.path.lexists(temporary):
            raise RemoteCutoverError("unsafe_path")
        LiveBackend._write_create_new(temporary, value)
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)

    def _stage_bot_unit(self) -> None:
        _regular_sha(SPAIN_UNIT_PATH)
        current = SPAIN_UNIT_PATH.read_bytes()
        validate_bot_unit(self.bot_unit)
        if sha256_bytes(current) == self.bot_unit_sha256:
            return
        self._safe_directory(CUTOVER_ROOT)
        self._safe_directory(self.rollback_root)
        if not os.path.lexists(self.rollback_unit):
            self._write_create_new(self.rollback_unit, current)
        self._atomic_replace(SPAIN_UNIT_PATH, self.bot_unit)
        self._run(("/usr/bin/systemctl", "daemon-reload"))
        if _regular_sha(SPAIN_UNIT_PATH) != self.bot_unit_sha256:
            raise RemoteCutoverError("bot_unit_update_failed")

    def _restore_bot_unit(self) -> None:
        if not os.path.lexists(self.rollback_unit):
            return
        _regular_sha(self.rollback_unit)
        before = self.rollback_unit.read_bytes()
        self._atomic_replace(SPAIN_UNIT_PATH, before)
        self._run(("/usr/bin/systemctl", "daemon-reload"))

    def _spain_continuation(self) -> dict[str, str]:
        unit = Path("/etc/systemd/system") / SPAIN_UNIT
        return {
            "awg": self.spain._awg_snapshot(),
            "database": _regular_sha(SPAIN_DATABASE),
            "foreign": self._foreign_sha(),
            "runtime": _regular_sha(SPAIN_RUNTIME),
            "source": _tree_sha(SPAIN_SOURCE),
            "unit": _regular_sha(unit),
        }

    def observe(
        self, role: str, continuation: Mapping[str, str] | None = None
    ) -> Mapping[str, object]:
        service = self._service(role)
        count = 1 if service["ActiveState"] == "active" and service["MainPID"] not in {"", "0"} else 0
        base: dict[str, object] = {
            "bot_active": count == 1,
            "bot_enabled": service["UnitFileState"] == "enabled",
            "bot_process_count": count,
            "continuation": {},
            "marker_present": os.path.lexists(SPAIN_MARKER) if role == "spain" else False,
        }
        if role == "usa":
            return base
        current = self._spain_continuation()
        expected = dict(continuation or {})
        base.update(
            {
                "awg2_equal": not expected or current["awg"] == expected.get("awg"),
                "database_equal": not expected or current["database"] == expected.get("database"),
                "foreign_equal": not expected or current["foreign"] == expected.get("foreign"),
                "runtime_equal": not expected or current["runtime"] == expected.get("runtime"),
                "source_equal": not expected or current["source"] == expected.get("source"),
                "web_loopback_healthy": bool(self.spain._web_healthy()),
                "continuation": current if not expected else {},
            }
        )
        return base

    def mutate(
        self, role: str, mode: str, continuation: Mapping[str, str] | None = None
    ) -> Mapping[str, object]:
        if role == "usa" and mode == "stop":
            self._run(("/usr/bin/systemctl", "disable", "--now", USA_UNIT))
        elif role == "usa" and mode == "rollback_start":
            self._run(("/usr/bin/systemctl", "enable", "--now", USA_UNIT))
        elif role == "spain" and mode == "start":
            if os.path.lexists(SPAIN_MARKER):
                raise RemoteCutoverError("unsafe_marker_state")
            self._stage_bot_unit()
            descriptor = os.open(
                SPAIN_MARKER,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                0o600,
            )
            os.close(descriptor)
            self._run(("/usr/bin/systemctl", "enable", "--now", SPAIN_UNIT))
        elif role == "spain" and mode == "rollback_stop":
            self._run(
                ("/usr/bin/systemctl", "disable", "--now", SPAIN_UNIT),
                require_success=False,
            )
            if os.path.lexists(SPAIN_MARKER):
                metadata = os.lstat(SPAIN_MARKER)
                if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
                    raise RemoteCutoverError("unsafe_marker_state")
                os.unlink(SPAIN_MARKER)
            self._restore_bot_unit()
        else:
            raise RemoteCutoverError("unsupported_transition")
        return self.observe(role, continuation)


def _parse_utc(value: object) -> datetime:
    if not isinstance(value, str) or re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value
    ) is None:
        raise RemoteCutoverError("payload_invalid")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError as error:
        raise RemoteCutoverError("payload_invalid") from error
    if parsed <= datetime.now(UTC):
        raise RemoteCutoverError("payload_expired")
    return parsed


def _load_foundation(value: bytes) -> ModuleType:
    namespace: dict[str, object] = {"__name__": "phase13_cutover_bound_foundation"}
    try:
        exec(compile(value, "<foundation>", "exec"), namespace)
    except Exception as error:
        raise RemoteCutoverError("foundation_invalid") from error
    module = ModuleType("phase13_cutover_bound_foundation")
    module.__dict__.update(namespace)
    if not hasattr(module, "RealSpainBackend"):
        raise RemoteCutoverError("foundation_invalid")
    return module


def main_bound_envelope(envelope: object) -> None:
    payload: dict[str, object] = {}
    try:
        if not isinstance(envelope, dict) or set(envelope) != {
            "foundation_b64", "foundation_sha256", "payload_b64"
        }:
            raise RemoteCutoverError("envelope_invalid")
        foundation = base64.b64decode(str(envelope["foundation_b64"]), validate=True)
        if sha256_bytes(foundation) != envelope["foundation_sha256"]:
            raise RemoteCutoverError("foundation_invalid")
        payload_bytes = base64.b64decode(str(envelope["payload_b64"]), validate=True)
        payload = json.loads(payload_bytes)
        if canonical_json_bytes(payload) != payload_bytes or set(payload) != {
            "bot_unit_b64", "bot_unit_sha256", "continuation", "expires_at", "manifest_sha256", "max_attempts",
            "mode", "outcome_id", "role", "schema"
        }:
            raise RemoteCutoverError("payload_invalid")
        if (
            payload.get("schema") != PAYLOAD_SCHEMA
            or payload.get("max_attempts") != 1
            or OUTCOME_PATTERN.fullmatch(str(payload.get("outcome_id", ""))) is None
            or SHA_PATTERN.fullmatch(str(payload.get("manifest_sha256", ""))) is None
            or SHA_PATTERN.fullmatch(str(payload.get("bot_unit_sha256", ""))) is None
        ):
            raise RemoteCutoverError("payload_invalid")
        _parse_utc(payload["expires_at"])
        result = execute(payload, LiveBackend(_load_foundation(foundation), payload))
    except RemoteCutoverError as error:
        result = _receipt(
            role=str(payload.get("role", "unknown")), outcome="failure",
            reason=str(error), action=False,
        )
    except Exception:
        result = _receipt(
            role=str(payload.get("role", "unknown")), outcome="failure",
            reason="internal_failure", action=False,
        )
    sys.stdout.buffer.write(canonical_json_bytes(result))


if __name__ == "__main__":
    raw = sys.stdin.buffer.read(4 * 1024 * 1024 + 1)
    if len(raw) > 4 * 1024 * 1024:
        raise SystemExit(70)
    main_bound_envelope(json.loads(raw))
