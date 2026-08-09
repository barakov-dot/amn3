"""Runtime-only Spain bot stage for AMN2 Phase 13.

The executor changes only two allowlisted runtime.env keys.  It never starts
or stops a service and delegates the accepted AWG2/foreign observations to the
checksum-bound Phase 13 production-stage foundation module.
"""

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
import sys
from types import ModuleType
from typing import Mapping, Protocol


PAYLOAD_SCHEMA = "amn2.phase13.spain-bot-runtime-stage-payload.v1"
RECEIPT_SCHEMA = "amn2.phase13.spain-bot-runtime-stage-receipt.v1"
SOURCE_MANIFEST_SCHEMA = "amn2.phase13.spain-accepted-source-manifest.v1"
EXPECTED_FOREIGN_STABLE_SHA256 = (
    "28f77ae21c1f91c26d8bba49bd93a054b671c5682f3688a66efe1a7045b38e4d"
)
EXPECTED_FOREIGN_PERSISTENT_ENTRIES = 149
EXPECTED_AWG2_FOUNDATION_SHA256 = (
    "0e5a5926821d88ae4a2515f9e95cd7c3f69db52100c1a1ec74e99fb794222281"
)
ACCEPTED_PHASE12_BOT_UNIT_SHA256 = (
    "389792d871cc980d8972bfe6a9b3f18ebebd4500c1bfadc92477b3382e0135f9"
)
OUTCOME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ADMIN_PATTERN = re.compile(r"^[0-9]{1,32}(?:,[0-9]{1,32})*$")
MAX_RUNTIME_BYTES = 1024 * 1024
MAX_SOURCE_FILES = 512
MAX_SOURCE_FILE_BYTES = 16 * 1024 * 1024
MAX_SOURCE_TOTAL_BYTES = 64 * 1024 * 1024

LIVE_DATABASE = Path("/var/lib/amn2-spain/amn2.sqlite3")
RUNTIME_ENVIRONMENT = Path("/etc/amn2-spain/runtime.env")
BOT_ENABLE_MARKER = Path("/etc/amn2-spain/bot-enabled")
BOT_UNIT_PATH = Path("/etc/systemd/system/amn2-spain-bot.service")
SOURCE_ROOT = Path("/opt/amn2-spain/runtime/source")
PROTECTED_ROOT = Path("/var/lib/amn2-phase13-bot-runtime-stage")
WEB_UNIT = "amn2-spain-web.service"

PAYLOAD_KEYS = {
    "expires_at",
    "expected",
    "manifest_sha256",
    "max_attempts",
    "outcome_id",
    "runtime_delta_b64",
    "runtime_delta_sha256",
    "schema",
    "source_manifest_b64",
}
EXPECTED_KEYS = {
    "accepted_source_head",
    "awg2_foundation_sha256",
    "bot_unit_sha256",
    "foreign_stable_sha256",
    "source_manifest_sha256",
}
TERMINAL_KEYS = {
    "awg2_equal",
    "bot_disabled",
    "database_equal",
    "foreign_equal",
    "marker_absent",
    "runtime_delta_equal",
    "source_equal",
    "web_loopback_healthy",
}
FOUNDATION_SNAPSHOT_REASONS = {
    "awg2": {"awg2_observation_failed", "awg2_equality_mismatch"},
    "foreign": {"foreign_observation_failed", "foreign_equality_mismatch"},
}
FOUNDATION_SNAPSHOT_METHODS = {
    "awg2": "_awg_snapshot",
    "foreign": "_foreign_snapshot",
}


class RemoteRuntimeStageError(RuntimeError):
    def __init__(self, stage: str, reason: str) -> None:
        super().__init__(reason)
        self.stage = stage
        self.reason = reason


class RuntimeStageBackend(Protocol):
    def preflight(self, payload: dict[str, object]) -> None: ...
    def apply_runtime_delta(self, delta: bytes) -> None: ...
    def post_verify(self, payload: dict[str, object]) -> None: ...
    def rollback(self, payload: dict[str, object]) -> None: ...
    def terminal_state(self, payload: dict[str, object]) -> Mapping[str, bool]: ...


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _bot_unit_hash_accepted(actual: str, hardened: str) -> bool:
    return actual in {ACCEPTED_PHASE12_BOT_UNIT_SHA256, hardened}


def _parse_utc(value: object) -> datetime:
    if not isinstance(value, str) or re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value
    ) is None:
        raise RemoteRuntimeStageError("package_verify", "schema_validation_failed")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError as error:
        raise RemoteRuntimeStageError(
            "package_verify", "schema_validation_failed"
        ) from error
    if parsed <= datetime.now(timezone.utc):
        raise RemoteRuntimeStageError("package_verify", "package_expired")
    return parsed


def _decode_b64(value: object, *, maximum: int, label: str) -> bytes:
    if not isinstance(value, str):
        raise RemoteRuntimeStageError("package_verify", "schema_validation_failed")
    try:
        decoded = base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as error:
        raise RemoteRuntimeStageError("package_verify", f"{label}_invalid") from error
    if not decoded or len(decoded) > maximum:
        raise RemoteRuntimeStageError("package_verify", f"{label}_invalid")
    return decoded


def _parse_env(value: bytes, *, required_exact: set[str] | None = None) -> dict[str, str]:
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RemoteRuntimeStageError("runtime_apply", "runtime_environment_invalid") from error
    if not text.endswith("\n") or "\r" in text or "\x00" in text:
        raise RemoteRuntimeStageError("runtime_apply", "runtime_environment_invalid")
    result: dict[str, str] = {}
    for line in text.splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, item = line.split("=", 1)
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", key) or key in result:
            raise RemoteRuntimeStageError("runtime_apply", "runtime_environment_invalid")
        result[key] = item
    if required_exact is not None and set(result) != required_exact:
        raise RemoteRuntimeStageError("runtime_apply", "runtime_delta_invalid")
    return result


def merge_runtime_environment(current: bytes, delta: bytes) -> bytes:
    if not current or len(current) > MAX_RUNTIME_BYTES:
        raise RemoteRuntimeStageError("runtime_apply", "runtime_environment_invalid")
    current_values = _parse_env(current)
    delta_values = _parse_env(
        delta, required_exact={"ADMIN_TELEGRAM_IDS", "TELEGRAM_BOT_TOKEN"}
    )
    if (
        not delta_values["TELEGRAM_BOT_TOKEN"]
        or "\n" in delta_values["TELEGRAM_BOT_TOKEN"]
        or ADMIN_PATTERN.fullmatch(delta_values["ADMIN_TELEGRAM_IDS"]) is None
        or "TELEGRAM_BOT_TOKEN" not in current_values
    ):
        raise RemoteRuntimeStageError("runtime_apply", "runtime_delta_invalid")
    lines = current.decode("utf-8").splitlines()
    replaced: set[str] = set()
    output: list[str] = []
    for line in lines:
        key = line.split("=", 1)[0] if "=" in line else ""
        if key in delta_values:
            if key in replaced:
                raise RemoteRuntimeStageError("runtime_apply", "runtime_environment_invalid")
            output.append(f"{key}={delta_values[key]}")
            replaced.add(key)
        else:
            output.append(line)
    for key in ("ADMIN_TELEGRAM_IDS", "TELEGRAM_BOT_TOKEN"):
        if key not in replaced:
            output.append(f"{key}={delta_values[key]}")
    merged = ("\n".join(output) + "\n").encode("utf-8")
    if len(merged) > MAX_RUNTIME_BYTES:
        raise RemoteRuntimeStageError("runtime_apply", "runtime_environment_invalid")
    before_other = {k: v for k, v in current_values.items() if k not in delta_values}
    after_other = {k: v for k, v in _parse_env(merged).items() if k not in delta_values}
    if before_other != after_other:
        raise RemoteRuntimeStageError("runtime_apply", "runtime_preservation_failed")
    return merged


def _validate_source_manifest(value: bytes, expected_sha256: str) -> dict[str, object]:
    if sha256_bytes(value) != expected_sha256:
        raise RemoteRuntimeStageError("package_verify", "checksum_mismatch")
    try:
        document = json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RemoteRuntimeStageError("package_verify", "source_manifest_invalid") from error
    if canonical_json_bytes(document) != value or not isinstance(document, dict):
        raise RemoteRuntimeStageError("package_verify", "source_manifest_invalid")
    if set(document) != {"files", "head", "schema"} or document.get("schema") != SOURCE_MANIFEST_SCHEMA:
        raise RemoteRuntimeStageError("package_verify", "source_manifest_invalid")
    files = document.get("files")
    if not isinstance(files, dict) or not files or len(files) > MAX_SOURCE_FILES:
        raise RemoteRuntimeStageError("package_verify", "source_manifest_invalid")
    total = 0
    for name, binding in files.items():
        if (
            not isinstance(name, str)
            or not name.startswith("app/")
            or ".." in Path(name).parts
            or not isinstance(binding, dict)
            or set(binding) != {"sha256", "size"}
            or SHA_PATTERN.fullmatch(str(binding.get("sha256", ""))) is None
            or not isinstance(binding.get("size"), int)
            or isinstance(binding.get("size"), bool)
            or not 0 <= int(binding["size"]) <= MAX_SOURCE_FILE_BYTES
        ):
            raise RemoteRuntimeStageError("package_verify", "source_manifest_invalid")
        total += int(binding["size"])
    if total > MAX_SOURCE_TOTAL_BYTES:
        raise RemoteRuntimeStageError("package_verify", "source_manifest_invalid")
    return document


def _validate_payload(value: object) -> tuple[dict[str, object], bytes, dict[str, object]]:
    if not isinstance(value, dict) or set(value) != PAYLOAD_KEYS:
        raise RemoteRuntimeStageError("package_verify", "schema_validation_failed")
    if (
        value.get("schema") != PAYLOAD_SCHEMA
        or value.get("max_attempts") != 1
        or OUTCOME_PATTERN.fullmatch(str(value.get("outcome_id", ""))) is None
        or SHA_PATTERN.fullmatch(str(value.get("manifest_sha256", ""))) is None
        or SHA_PATTERN.fullmatch(str(value.get("runtime_delta_sha256", ""))) is None
    ):
        raise RemoteRuntimeStageError("package_verify", "schema_validation_failed")
    _parse_utc(value["expires_at"])
    expected = value.get("expected")
    if not isinstance(expected, dict) or set(expected) != EXPECTED_KEYS:
        raise RemoteRuntimeStageError("package_verify", "schema_validation_failed")
    for key in EXPECTED_KEYS - {"accepted_source_head"}:
        if SHA_PATTERN.fullmatch(str(expected.get(key, ""))) is None:
            raise RemoteRuntimeStageError("package_verify", "schema_validation_failed")
    if not re.fullmatch(r"[0-9a-f]{40}", str(expected.get("accepted_source_head", ""))):
        raise RemoteRuntimeStageError("package_verify", "schema_validation_failed")
    if (
        expected["awg2_foundation_sha256"] != EXPECTED_AWG2_FOUNDATION_SHA256
        or expected["foreign_stable_sha256"] != EXPECTED_FOREIGN_STABLE_SHA256
    ):
        raise RemoteRuntimeStageError("package_verify", "foundation_mismatch")
    delta = _decode_b64(value["runtime_delta_b64"], maximum=MAX_RUNTIME_BYTES, label="runtime_delta")
    if sha256_bytes(delta) != value["runtime_delta_sha256"]:
        raise RemoteRuntimeStageError("package_verify", "checksum_mismatch")
    _parse_env(delta, required_exact={"ADMIN_TELEGRAM_IDS", "TELEGRAM_BOT_TOKEN"})
    manifest_bytes = _decode_b64(
        value["source_manifest_b64"], maximum=2 * 1024 * 1024, label="source_manifest"
    )
    manifest = _validate_source_manifest(
        manifest_bytes, str(expected["source_manifest_sha256"])
    )
    if manifest["head"] != expected["accepted_source_head"]:
        raise RemoteRuntimeStageError("package_verify", "source_manifest_invalid")
    return dict(value), delta, manifest


def _safe_terminal(backend: RuntimeStageBackend, payload: dict[str, object]) -> dict[str, bool]:
    defaults = {key: False for key in TERMINAL_KEYS}
    try:
        state = backend.terminal_state(payload)
    except Exception:
        return defaults
    if set(state) != TERMINAL_KEYS or any(not isinstance(item, bool) for item in state.values()):
        return defaults
    return dict(state)


def _receipt(
    payload: Mapping[str, object], *, outcome: str, stage: str, reason: str,
    rolled_back: bool, state: Mapping[str, bool]
) -> dict[str, object]:
    return {
        **state,
        "outcome": outcome,
        "outcome_id": payload.get("outcome_id", "unknown"),
        "raw_output_persisted": False,
        "reason": reason,
        "rolled_back": rolled_back,
        "schema": RECEIPT_SCHEMA,
        "service_action_performed": False,
        "stage": stage,
    }


def execute_runtime_stage(value: object, backend: RuntimeStageBackend) -> dict[str, object]:
    payload: dict[str, object] = value if isinstance(value, dict) else {}
    stage = "package_verify"
    attempted_apply = False
    rolled_back = False
    try:
        payload, delta, _manifest = _validate_payload(value)
        stage = "preflight"
        backend.preflight(payload)
        stage = "runtime_apply"
        attempted_apply = True
        backend.apply_runtime_delta(delta)
        stage = "post_verify"
        backend.post_verify(payload)
        state = _safe_terminal(backend, payload)
        if not all(state.values()):
            raise RemoteRuntimeStageError("post_verify", "terminal_state_invalid")
        return _receipt(
            payload, outcome="success", stage="post_verify", reason="completed",
            rolled_back=False, state=state
        )
    except RemoteRuntimeStageError as error:
        stage, reason = error.stage, error.reason
    except Exception:
        reason = "internal_failure"
    if attempted_apply:
        try:
            backend.rollback(payload)
            rolled_back = True
        except Exception:
            stage, reason = "rollback", "rollback_failed"
    state = _safe_terminal(backend, payload)
    return _receipt(
        payload, outcome="failure", stage=stage, reason=reason,
        rolled_back=rolled_back, state=state
    )


def _regular_file(path: Path, maximum: int = MAX_SOURCE_FILE_BYTES) -> os.stat_result:
    try:
        metadata = os.lstat(path)
    except OSError as error:
        raise RemoteRuntimeStageError("preflight", "required_file_unavailable") from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode) or metadata.st_size > maximum:
        raise RemoteRuntimeStageError("preflight", "required_file_invalid")
    return metadata


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


class LiveSpainRuntimeBackend:
    def __init__(self, foundation: ModuleType, source_manifest: Mapping[str, object]) -> None:
        self.foundation = foundation
        self.foundation_backend = foundation.RealSpainBackend()
        self.source_manifest = source_manifest
        self.runtime_before = b""
        self.database_sha = ""
        self.awg_before = ""
        self.foreign_before = ""
        self.outcome_root: Path | None = None
        self.rollback_path: Path | None = None
        self.expected_runtime = b""

    def _source_equal(self) -> bool:
        files = self.source_manifest["files"]
        assert isinstance(files, dict)
        for name, binding in files.items():
            assert isinstance(name, str) and isinstance(binding, dict)
            path = SOURCE_ROOT.joinpath(*Path(name).parts)
            metadata = _regular_file(path)
            if metadata.st_size != binding["size"] or _sha256_file(path) != binding["sha256"]:
                return False
        return True

    def _bot_disabled(self) -> bool:
        try:
            bot = self.foundation_backend._service_values(BOT_UNIT_PATH.name)
        except Exception:
            return False
        return bool(
            bot["ActiveState"] == "inactive"
            and bot["MainPID"] in {"", "0"}
            and bot["UnitFileState"] in {"disabled", "static"}
            and not os.path.lexists(BOT_ENABLE_MARKER)
        )

    def _web_healthy(self) -> bool:
        try:
            web = self.foundation_backend._service_values(WEB_UNIT)
            return bool(
                web["ActiveState"] == "active"
                and web["UnitFileState"] == "enabled"
                and self.foundation_backend._web_healthy()
            )
        except Exception:
            return False

    def _capture_foundation_snapshot(self, kind: str, *, stage: str) -> str:
        if kind not in FOUNDATION_SNAPSHOT_REASONS:
            raise RemoteRuntimeStageError(stage, "observation_failed")
        fallback = f"{kind}_observation_failed"
        if kind == "foreign":
            try:
                before = self.foundation_backend._collect_foreign_rows()
                after = self.foundation_backend._collect_foreign_rows()
                persistent = sorted(set(before).intersection(after))
                before_rows = [before[identity] for identity in persistent]
                after_rows = [after[identity] for identity in persistent]
                before_digest = self.foundation_backend._phase12_stable_digest(
                    before_rows
                )
                after_digest = self.foundation_backend._phase12_stable_digest(
                    after_rows
                )
            except self.foundation.RemoteStageError as error:
                raise RemoteRuntimeStageError(stage, fallback) from error
            except Exception as error:
                raise RemoteRuntimeStageError(stage, fallback) from error
            if (
                len(persistent) != EXPECTED_FOREIGN_PERSISTENT_ENTRIES
                or before_digest != after_digest
                or before_digest != EXPECTED_FOREIGN_STABLE_SHA256
            ):
                raise RemoteRuntimeStageError(
                    stage, "foreign_equality_mismatch"
                )
            return before_digest
        try:
            snapshot = getattr(
                self.foundation_backend, FOUNDATION_SNAPSHOT_METHODS[kind]
            )()
        except self.foundation.RemoteStageError as error:
            reason = str(getattr(error, "reason", ""))
            if reason not in FOUNDATION_SNAPSHOT_REASONS[kind]:
                reason = fallback
            raise RemoteRuntimeStageError(stage, reason) from error
        except Exception as error:
            raise RemoteRuntimeStageError(stage, fallback) from error
        if not isinstance(snapshot, str) or SHA_PATTERN.fullmatch(snapshot) is None:
            raise RemoteRuntimeStageError(stage, fallback)
        return snapshot

    def preflight(self, payload: dict[str, object]) -> None:
        expected = payload["expected"]
        assert isinstance(expected, dict)
        _regular_file(LIVE_DATABASE, 64 * 1024 * 1024)
        runtime_metadata = _regular_file(RUNTIME_ENVIRONMENT, MAX_RUNTIME_BYTES)
        _regular_file(BOT_UNIT_PATH, 1024 * 1024)
        if not _bot_unit_hash_accepted(
            _sha256_file(BOT_UNIT_PATH), str(expected["bot_unit_sha256"])
        ):
            raise RemoteRuntimeStageError("preflight", "bot_unit_mismatch")
        if not self._bot_disabled() or not self._web_healthy():
            raise RemoteRuntimeStageError("preflight", "service_state_invalid")
        try:
            connection = sqlite3.connect(f"file:{LIVE_DATABASE}?mode=ro", uri=True)
            connection.execute("PRAGMA query_only=ON")
            integrity = connection.execute("PRAGMA integrity_check").fetchone()
            foreign = connection.execute("PRAGMA foreign_key_check").fetchall()
        except sqlite3.Error as error:
            raise RemoteRuntimeStageError("preflight", "database_invalid") from error
        finally:
            try:
                connection.close()
            except UnboundLocalError:
                pass
        if integrity != ("ok",) or foreign:
            raise RemoteRuntimeStageError("preflight", "database_invalid")
        if not self._source_equal():
            raise RemoteRuntimeStageError("preflight", "source_mismatch")
        self.runtime_before = RUNTIME_ENVIRONMENT.read_bytes()
        if len(self.runtime_before) != runtime_metadata.st_size:
            raise RemoteRuntimeStageError("preflight", "runtime_environment_invalid")
        self.database_sha = _sha256_file(LIVE_DATABASE)
        self.awg_before = self._capture_foundation_snapshot("awg2", stage="preflight")
        self.foreign_before = self._capture_foundation_snapshot("foreign", stage="preflight")
        outcome_root = PROTECTED_ROOT / str(payload["outcome_id"])
        if os.path.lexists(outcome_root):
            raise RemoteRuntimeStageError("preflight", "stage_replay")
        self.outcome_root = outcome_root

    def apply_runtime_delta(self, delta: bytes) -> None:
        self.expected_runtime = merge_runtime_environment(self.runtime_before, delta)
        metadata = _regular_file(RUNTIME_ENVIRONMENT, MAX_RUNTIME_BYTES)
        try:
            _ensure_private_root(PROTECTED_ROOT)
            if self.outcome_root is None:
                raise RemoteRuntimeStageError("runtime_apply", "outcome_state_missing")
            root = self.outcome_root
            root.mkdir(mode=0o700, exist_ok=False)
            rollback = root / "runtime.env.before"
            _write_create_new(rollback, self.runtime_before, metadata)
            os.chmod(rollback, 0o600)
            temporary = RUNTIME_ENVIRONMENT.parent / ".phase13-bot-runtime.env.tmp"
            if os.path.lexists(temporary):
                raise RemoteRuntimeStageError("runtime_apply", "temporary_path_exists")
            _write_create_new(temporary, self.expected_runtime, metadata)
            os.replace(temporary, RUNTIME_ENVIRONMENT)
            directory = os.open(RUNTIME_ENVIRONMENT.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
            self.outcome_root = root
            self.rollback_path = rollback
        except RemoteRuntimeStageError:
            raise
        except OSError as error:
            raise RemoteRuntimeStageError("runtime_apply", "runtime_write_failed") from error

    def post_verify(self, payload: dict[str, object]) -> None:
        if RUNTIME_ENVIRONMENT.read_bytes() != self.expected_runtime:
            raise RemoteRuntimeStageError("post_verify", "runtime_delta_mismatch")
        if _sha256_file(LIVE_DATABASE) != self.database_sha or not self._source_equal():
            raise RemoteRuntimeStageError("post_verify", "preservation_failed")
        if not self._bot_disabled() or not self._web_healthy():
            raise RemoteRuntimeStageError("post_verify", "service_state_invalid")
        if self._capture_foundation_snapshot("awg2", stage="post_verify") != self.awg_before:
            raise RemoteRuntimeStageError("post_verify", "awg2_equality_mismatch")
        if self._capture_foundation_snapshot("foreign", stage="post_verify") != self.foreign_before:
            raise RemoteRuntimeStageError("post_verify", "foreign_equality_mismatch")

    def rollback(self, payload: dict[str, object]) -> None:
        if self.rollback_path is None:
            raise RemoteRuntimeStageError("rollback", "rollback_state_missing")
        metadata = _regular_file(RUNTIME_ENVIRONMENT, MAX_RUNTIME_BYTES)
        temporary = RUNTIME_ENVIRONMENT.parent / ".phase13-bot-runtime.rollback.tmp"
        if os.path.lexists(temporary):
            raise RemoteRuntimeStageError("rollback", "temporary_path_exists")
        _write_create_new(temporary, self.runtime_before, metadata)
        os.replace(temporary, RUNTIME_ENVIRONMENT)
        if RUNTIME_ENVIRONMENT.read_bytes() != self.runtime_before:
            raise RemoteRuntimeStageError("rollback", "rollback_mismatch")

    def terminal_state(self, payload: dict[str, object]) -> Mapping[str, bool]:
        state = {key: False for key in TERMINAL_KEYS}
        try:
            state["bot_disabled"] = self._bot_disabled()
            state["marker_absent"] = not os.path.lexists(BOT_ENABLE_MARKER)
            state["web_loopback_healthy"] = self._web_healthy()
            state["database_equal"] = bool(self.database_sha and _sha256_file(LIVE_DATABASE) == self.database_sha)
            state["source_equal"] = self._source_equal()
            state["runtime_delta_equal"] = bool(self.expected_runtime and RUNTIME_ENVIRONMENT.read_bytes() == self.expected_runtime)
            state["awg2_equal"] = bool(self.awg_before and self.foundation_backend._awg_snapshot() == self.awg_before)
            state["foreign_equal"] = bool(self.foreign_before and self.foundation_backend._foreign_snapshot() == self.foreign_before)
        except Exception:
            pass
        return state


def _write_create_new(path: Path, value: bytes, source_metadata: os.stat_result) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, stat.S_IMODE(source_metadata.st_mode))
    try:
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.chown(path, source_metadata.st_uid, source_metadata.st_gid)
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _ensure_private_root(path: Path) -> None:
    if not os.path.lexists(path):
        os.mkdir(path, 0o700)
    metadata = os.lstat(path)
    if (
        stat.S_ISLNK(metadata.st_mode)
        or not stat.S_ISDIR(metadata.st_mode)
        or metadata.st_uid != os.geteuid()
        or stat.S_IMODE(metadata.st_mode) & 0o077
    ):
        raise RemoteRuntimeStageError("runtime_apply", "protected_root_invalid")


def _load_foundation(value: bytes) -> ModuleType:
    module = ModuleType("phase13_bound_runtime_stage_foundation")
    module.__file__ = "<foundation>"
    sys.modules[module.__name__] = module
    try:
        exec(compile(value, "<foundation>", "exec"), module.__dict__)
    except Exception as error:
        sys.modules.pop(module.__name__, None)
        raise RemoteRuntimeStageError("package_verify", "foundation_invalid") from error
    if not hasattr(module, "RealSpainBackend"):
        raise RemoteRuntimeStageError("package_verify", "foundation_invalid")
    return module


def main_bound_envelope(envelope: object) -> None:
    if not isinstance(envelope, dict) or set(envelope) != {
        "foundation_b64", "foundation_sha256", "payload_b64"
    }:
        raise SystemExit(64)
    try:
        foundation_bytes = base64.b64decode(envelope["foundation_b64"], validate=True)
        payload_bytes = base64.b64decode(envelope["payload_b64"], validate=True)
        if sha256_bytes(foundation_bytes) != envelope["foundation_sha256"]:
            raise ValueError
        payload = json.loads(payload_bytes)
    except Exception:
        raise SystemExit(65)
    try:
        validated, _delta, manifest = _validate_payload(payload)
        foundation = _load_foundation(foundation_bytes)
        backend = LiveSpainRuntimeBackend(foundation, manifest)
        receipt = execute_runtime_stage(validated, backend)
    except RemoteRuntimeStageError as error:
        receipt = _receipt(
            payload if isinstance(payload, dict) else {},
            outcome="failure",
            stage=error.stage,
            reason=error.reason,
            rolled_back=False,
            state={key: False for key in TERMINAL_KEYS},
        )
    except Exception:
        receipt = _receipt(
            payload if isinstance(payload, dict) else {},
            outcome="failure",
            stage="package_verify",
            reason="internal_failure",
            rolled_back=False,
            state={key: False for key in TERMINAL_KEYS},
        )
    sys.stdout.buffer.write(canonical_json_bytes(receipt))
    # A valid failure receipt is intentionally returned with exit 0 so the
    # local runner can persist its allowlisted stage/reason without raw output.
    raise SystemExit(0)
