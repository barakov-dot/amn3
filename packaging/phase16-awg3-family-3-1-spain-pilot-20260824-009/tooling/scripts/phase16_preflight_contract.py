from __future__ import annotations

import copy
import datetime as dt
import json
import re
from typing import Any


PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-009"
CLAIM_SCHEMA = "amn2.phase16.readonly-preflight-claim.v1"
EVIDENCE_SCHEMA = "amn2.phase16.readonly-preflight-evidence.v1"
FAILURE_SCHEMA = "amn2.phase16.readonly-preflight-failure.v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CLAIM_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
EXPECTED_HOST_RE = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*$"
)
SECRET_PATTERNS = (
    re.compile(r"\b[0-9]{6,12}:[A-Za-z0-9_-]{30,}\b"),
    re.compile(r"(?i)\bBearer\s+\S+"),
    re.compile(r"(?i)\b(?:PrivateKey|PresharedKey)\s*="),
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
)
CLAIM_KEYS = {
    "claim_id",
    "collector_sha256",
    "consumed_at",
    "expected_host",
    "expires_at",
    "future_gate",
    "issued_at",
    "manifest_sha256",
    "package_id",
    "schema",
    "status",
}
OBSERVATION_KEYS = {"name", "observation_sha256", "state"}
OBSERVATION_STATES = {"absent", "free", "pass", "present", "stop", "unknown"}
FAILURE_REASONS = {
    "claim_invalid",
    "collector_failed",
    "identity_mismatch",
    "observation_ambiguous",
    "schema_invalid",
    "transport_failed",
}
STOP_REASONS = {
    "identity_mismatch",
    "observation_failed",
    "recovery_incomplete",
    "resource_conflict",
}
EXPECTED_OBSERVATION_NAMES = {
    "application_state", "architecture", "awg2_health", "backup_capability",
    "bridge_amn2sp3br0", "config_path", "container_capability",
    "container_cidr_172_29_252_0_28", "container_name", "database_state",
    "disk_space", "firewall", "interface_awg3", "os_compatibility", "python_3_12",
    "recovery_markers_phase14_phase15_phase16", "routes", "service_capability", "service_name",
    "state_root", "telegram_prerequisites", "udp_30002", "vpn_cidr_10_212_13_0_24",
}
CONFLICT_OBSERVATION_NAMES = {
    "bridge_amn2sp3br0",
    "config_path",
    "container_cidr_172_29_252_0_28",
    "container_name",
    "firewall",
    "interface_awg3",
    "routes",
    "service_name",
    "state_root",
    "udp_30002",
    "vpn_cidr_10_212_13_0_24",
}
RECOVERY_OBSERVATION_NAME = "recovery_markers_phase14_phase15_phase16"


class PreflightContractError(ValueError):
    pass


def canonical_json_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8") + b"\n"
    except (TypeError, ValueError) as exc:
        raise PreflightContractError("value is not canonical JSON") from exc


def load_canonical_json(raw: bytes, *, label: str) -> dict[str, object]:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        value: dict[str, object] = {}
        for key, item in pairs:
            if key in value:
                raise PreflightContractError(f"{label} duplicate key")
            value[key] = item
        return value

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreflightContractError(f"{label} invalid JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise PreflightContractError(f"{label} is not canonical JSON")
    return value


def _timestamp(value: object, *, label: str) -> dt.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise PreflightContractError(f"{label} timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise PreflightContractError(f"{label} timestamp") from exc
    if parsed.tzinfo != dt.timezone.utc or parsed.isoformat().replace("+00:00", "Z") != value:
        raise PreflightContractError(f"{label} timestamp")
    return parsed


def _sha256(value: object, *, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise PreflightContractError(f"{label} sha256")
    return value


def _secret_safe(value: object) -> None:
    def walk(item: object) -> None:
        if isinstance(item, str):
            if len(item.encode("utf-8")) > 512 or any(pattern.search(item) for pattern in SECRET_PATTERNS):
                raise PreflightContractError("secret or raw command material")
        elif isinstance(item, dict):
            for key, nested in item.items():
                walk(key)
                walk(nested)
        elif isinstance(item, list):
            for nested in item:
                walk(nested)

    walk(value)


def validate_claim(
    claim: object,
    *,
    package_id: str,
    manifest_sha256: str,
    collector_sha256: str,
    expected_host: str,
    now: dt.datetime,
) -> dict[str, object]:
    if not isinstance(claim, dict) or set(claim) != CLAIM_KEYS:
        raise PreflightContractError("claim keys")
    _secret_safe(claim)
    if package_id != PACKAGE_ID or claim["schema"] != CLAIM_SCHEMA or claim["package_id"] != PACKAGE_ID:
        raise PreflightContractError("claim package identity")
    expected_manifest = _sha256(manifest_sha256, label="expected manifest")
    expected_collector = _sha256(collector_sha256, label="expected collector")
    if claim["manifest_sha256"] != expected_manifest or claim["collector_sha256"] != expected_collector:
        raise PreflightContractError("claim checksum binding")
    if not isinstance(expected_host, str) or EXPECTED_HOST_RE.fullmatch(expected_host) is None:
        raise PreflightContractError("expected host grammar")
    if claim["expected_host"] != expected_host:
        raise PreflightContractError("claim host binding")
    if claim["future_gate"] != "PREFLIGHT":
        raise PreflightContractError("claim future gate")
    if claim["status"] != "issued" or claim["consumed_at"] is not None:
        raise PreflightContractError("claim already used")
    if not isinstance(claim["claim_id"], str) or CLAIM_ID_RE.fullmatch(claim["claim_id"]) is None:
        raise PreflightContractError("claim id")
    issued = _timestamp(claim["issued_at"], label="issued_at")
    expires = _timestamp(claim["expires_at"], label="expires_at")
    if now.tzinfo != dt.timezone.utc or now < issued or not now < expires or not issued < expires:
        raise PreflightContractError("claim lifecycle")
    return copy.deepcopy(claim)


def consume_claim(claim: object, *, consumed_at: str) -> dict[str, object]:
    consumed = _timestamp(consumed_at, label="consumed_at")
    if not isinstance(claim, dict) or set(claim) != CLAIM_KEYS:
        raise PreflightContractError("claim keys")
    validate_claim(
        claim,
        package_id=PACKAGE_ID,
        manifest_sha256=str(claim.get("manifest_sha256")),
        collector_sha256=str(claim.get("collector_sha256")),
        expected_host=str(claim.get("expected_host")),
        now=consumed,
    )
    result = copy.deepcopy(claim)
    result["status"] = "consumed"
    result["consumed_at"] = consumed_at
    return result


def _validate_observations(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise PreflightContractError("observations")
    result: list[dict[str, str]] = []
    names: set[str] = set()
    for item in value:
        if not isinstance(item, dict) or set(item) != OBSERVATION_KEYS:
            raise PreflightContractError("observation keys")
        name = item["name"]
        state = item["state"]
        if (
            not isinstance(name, str)
            or not name
            or name in names
            or not isinstance(state, str)
            or state not in OBSERVATION_STATES
        ):
            raise PreflightContractError("observation identity")
        _sha256(item["observation_sha256"], label="observation")
        names.add(name)
        result.append(dict(item))
    if [item["name"] for item in result] != sorted(names):
        raise PreflightContractError("observation order")
    if names != EXPECTED_OBSERVATION_NAMES:
        raise PreflightContractError("observation inventory")
    _secret_safe(result)
    return result


def _validated_window(claim: dict[str, object], started_at: str, ended_at: str) -> tuple[dt.datetime, dt.datetime]:
    started = _timestamp(started_at, label="started_at")
    ended = _timestamp(ended_at, label="ended_at")
    if ended < started:
        raise PreflightContractError("timestamp order")
    validate_claim(
        claim,
        package_id=PACKAGE_ID,
        manifest_sha256=str(claim.get("manifest_sha256")),
        collector_sha256=str(claim.get("collector_sha256")),
        expected_host=str(claim.get("expected_host")),
        now=started,
    )
    return started, ended


def _safety(*, ssh_used: bool) -> dict[str, bool]:
    if not isinstance(ssh_used, bool):
        raise PreflightContractError("ssh_used")
    return {
        "live_mutation": False,
        "raw_output_persisted": False,
        "remote_file_written": False,
        "ssh_used": ssh_used,
    }


def bind_evidence(
    claim: dict[str, object],
    *,
    observations: object,
    stop_reasons: object,
    started_at: str,
    ended_at: str,
    transport_disposition: str,
    ssh_used: bool,
) -> dict[str, object]:
    _validated_window(claim, started_at, ended_at)
    checked_observations = _validate_observations(observations)
    if not isinstance(stop_reasons, list) or any(
        not isinstance(reason, str) or reason not in STOP_REASONS for reason in stop_reasons
    ):
        raise PreflightContractError("stop reasons")
    if stop_reasons != sorted(set(stop_reasons)):
        raise PreflightContractError("stop reason order")
    _secret_safe(stop_reasons)
    stopped_names = {
        item["name"] for item in checked_observations if item["state"] in {"stop", "unknown"}
    }
    expected_reasons: set[str] = set()
    if stopped_names & CONFLICT_OBSERVATION_NAMES:
        expected_reasons.add("resource_conflict")
    if RECOVERY_OBSERVATION_NAME in stopped_names:
        expected_reasons.add("recovery_incomplete")
    if stopped_names - CONFLICT_OBSERVATION_NAMES - {RECOVERY_OBSERVATION_NAME}:
        expected_reasons.add("observation_failed")
    if stop_reasons != sorted(expected_reasons):
        raise PreflightContractError("decision binding")
    must_stop = bool(expected_reasons)
    if transport_disposition not in {"not_run", "read_only_completed"}:
        raise PreflightContractError("transport disposition")
    if (transport_disposition == "not_run") != (not ssh_used):
        raise PreflightContractError("transport safety binding")
    result: dict[str, object] = {
        "collector_sha256": claim["collector_sha256"],
        "decision": "stop" if must_stop else "pass",
        "ended_at": ended_at,
        "expected_host": claim["expected_host"],
        "manifest_sha256": claim["manifest_sha256"],
        "observations": checked_observations,
        "package_id": claim["package_id"],
        "safety": _safety(ssh_used=ssh_used),
        "schema": EVIDENCE_SCHEMA,
        "started_at": started_at,
        "stop_reasons": list(stop_reasons),
        "transport_disposition": transport_disposition,
    }
    _secret_safe(result)
    return result


def bind_failure(
    claim: dict[str, object],
    *,
    reason_code: str,
    started_at: str,
    ended_at: str,
    transport_disposition: str,
    ssh_used: bool,
) -> dict[str, object]:
    _validated_window(claim, started_at, ended_at)
    if not isinstance(reason_code, str) or reason_code not in FAILURE_REASONS:
        raise PreflightContractError("failure reason")
    if transport_disposition not in {"not_run", "read_only_failed"}:
        raise PreflightContractError("failure transport disposition")
    if (transport_disposition == "not_run") != (not ssh_used):
        raise PreflightContractError("failure transport safety binding")
    result: dict[str, object] = {
        "collector_sha256": claim["collector_sha256"],
        "decision": "stop",
        "ended_at": ended_at,
        "expected_host": claim["expected_host"],
        "manifest_sha256": claim["manifest_sha256"],
        "package_id": claim["package_id"],
        "reason_code": reason_code,
        "safety": _safety(ssh_used=ssh_used),
        "schema": FAILURE_SCHEMA,
        "started_at": started_at,
        "transport_disposition": transport_disposition,
    }
    _secret_safe(result)
    return result
