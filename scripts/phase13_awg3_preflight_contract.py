from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile


class ContractError(ValueError):
    pass


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "packaging" / "phase13-awg3-preflight"
FOUNDATION_PATH = ARTIFACT_ROOT / "phase12-equality-foundation.json"

MANIFEST_SCHEMA = "amn2.phase13.awg3-readonly-preflight-manifest.v1"
SUCCESS_SCHEMA = "amn2.phase13.awg3-readonly-preflight.v1"
FAILURE_SCHEMA_V1 = "amn2.phase13.awg3-readonly-preflight-failure.v1"
FAILURE_SCHEMA_V2 = "amn2.phase13.awg3-readonly-preflight-failure.v2"
FAILURE_SCHEMA_V3 = "amn2.phase13.awg3-readonly-preflight-failure.v3"
FAILURE_SCHEMA = FAILURE_SCHEMA_V1
SOURCE_BASE = "55dc243b8e6c6bdb57f8301b56326e4cd4072d19"
SOURCE_HEAD = "ff115b63ca1329640ca13ae0a502d155f99b456b"
SPAIN_OVERLAY = "f1bf099ddb47da26a4080714376babaf5b0de92c"
PHASE12_FOUNDATION_SHA256 = "0e5a5926821d88ae4a2515f9e95cd7c3f69db52100c1a1ec74e99fb794222281"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
OUTCOME_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")

CANDIDATE = {
    "runtime_instance_id": "spain-awg3-candidate-001",
    "protocol_version": "awg3",
    "interface_name": "awg3",
    "host_bridge": "amn2sp3br0",
    "udp_port": 30002,
    "vpn_cidr": "10.212.13.0/24",
    "server_vpn_address": "10.212.13.1/24",
    "container_cidr": "172.29.252.0/28",
    "container_name": "amn2-spain-awg3",
    "service_name": "amn2-spain-awg3.service",
    "state_root": "/var/lib/amn2-spain/awg3",
    "config_path": "/var/lib/amn2-spain/awg3/awg3.conf",
}

ALLOWED_COMMAND_FAMILIES = [
    "os_kernel_capacity_observation",
    "systemd_readonly_observation",
    "socket_observation",
    "ip_json_observation",
    "docker_readonly_observation",
    "nftables_readonly_observation",
    "filesystem_readonly_observation",
    "sanitized_awg2_projection",
]

FORBIDDEN_ACTIONS = [
    "systemd_action",
    "docker_mutation",
    "ip_mutation",
    "firewall_mutation",
    "awg_mutation",
    "remote_filesystem_write",
    "package_manager",
    "reboot",
    "wildcard_operation",
]

MANIFEST_KEYS = {
    "schema",
    "outcome_id",
    "created_at",
    "expires_at",
    "target_role",
    "source_base",
    "source_head",
    "spain_overlay",
    "candidate",
    "artifacts",
    "foundation_sha256",
    "allowed_command_families",
    "forbidden_actions",
    "max_attempts",
    "remote_write_allowed",
    "package_build_allowed",
    "live_action_authorized",
}

SUCCESS_KEYS = {
    "schema",
    "outcome_id",
    "checked_at",
    "source_head",
    "manifest_sha256",
    "runner_sha256",
    "collector_sha256",
    "schema_sha256",
    "phase12_foundation_sha256",
    "candidate_resources",
    "awg2_equality",
    "foreign_equality",
    "safety_receipt",
    "decision",
    "stop_reasons",
}

FAILURE_KEYS_V1 = {
    "schema",
    "outcome_id",
    "checked_at",
    "source_head",
    "manifest_sha256",
    "stage",
    "reason_code",
    "decision",
    "safety_receipt",
}

FAILURE_KEYS_V2 = FAILURE_KEYS_V1 | {"transport_subreason"}
FAILURE_KEYS_V3 = FAILURE_KEYS_V1 | {"transport_subreason"}
FAILURE_KEYS = FAILURE_KEYS_V1

SAFETY_KEYS = {
    "mutation_attempted",
    "remote_file_written",
    "service_action_attempted",
    "container_action_attempted",
    "firewall_action_attempted",
    "secret_bearing_config_accessed",
    "raw_peer_identifiers_emitted",
    "raw_output_persisted",
}

FAILURE_STAGES = {
    "argument_validation",
    "checksum_verification",
    "approval_validation",
    "private_root_validation",
    "outcome_claim",
    "trust_binding",
    "transport",
    "collector",
    "schema_validation",
}

FAILURE_REASONS = {
    "udp_port_conflict",
    "interface_conflict",
    "vpn_cidr_overlap",
    "container_cidr_overlap",
    "container_name_conflict",
    "service_name_conflict",
    "state_path_conflict",
    "runtime_capability_unavailable",
    "awg2_equality_mismatch",
    "foreign_equality_mismatch",
    "observation_ambiguous",
    "artifact_checksum_mismatch",
    "outcome_replay",
    "schema_validation_failed",
    "secret_pattern_detected",
}

TRANSPORT_SUBREASONS_V2 = {
    "timeout",
    "output_oversized",
    "ssh_exit_unclassified",
    "local_process_failure",
    "transport_internal_failure",
}

TRANSPORT_SUBREASONS_V3 = {
    "ssh_client_failure",
    "remote_command_unavailable",
    "remote_exit_unclassified",
    "timeout",
    "output_oversized",
    "local_process_failure",
    "transport_internal_failure",
}

NOT_APPLICABLE_SUBREASON = "not_applicable"

LOCAL_ARTIFACT_NAMES = (
    "evidence.schema.json",
    "failure-evidence.schema.json",
    "failure-evidence-v2.schema.json",
    "manifest.schema.json",
    "phase12-equality-foundation.json",
    "phase13_spain_awg3_readonly_preflight_remote.sh",
    "phase13_spain_awg3_readonly_preflight_ssh_runner.ps1",
)

LOCAL_ARTIFACT_RELATIVE_PATHS = (
    "packaging/phase13-awg3-preflight/evidence.schema.json",
    "packaging/phase13-awg3-preflight/failure-evidence.schema.json",
    "packaging/phase13-awg3-preflight/failure-evidence-v2.schema.json",
    "packaging/phase13-awg3-preflight/manifest.schema.json",
    "packaging/phase13-awg3-preflight/phase12-equality-foundation.json",
    "scripts/vps/phase13_spain_awg3_readonly_preflight_remote.sh",
    "scripts/vps/phase13_spain_awg3_readonly_preflight_ssh_runner.ps1",
)

TEST_MANIFEST_CREATED_AT = datetime(2099, 8, 1, tzinfo=timezone.utc)
TEST_MANIFEST_EXPIRES_AT = datetime(2099, 8, 2, tzinfo=timezone.utc)


def canonical_json_bytes(value: object) -> bytes:
    try:
        text = json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise ContractError("value is not canonical JSON") from error
    return text.encode("utf-8") + b"\n"


def sha256_bytes(value: bytes) -> str:
    if not isinstance(value, bytes):
        raise ContractError("sha256 requires bytes")
    return hashlib.sha256(value).hexdigest()


def load_json_object_strict(raw: bytes, *, label: str) -> dict[str, object]:
    if not isinstance(raw, bytes):
        raise ContractError(f"{label} must be bytes")

    def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ContractError(f"{label} duplicate key: {key}")
            result[key] = value
        return result

    try:
        decoded = raw.decode("utf-8")
        value = json.loads(decoded, object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(f"{label} invalid JSON") from error
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    if raw != canonical_json_bytes(value):
        raise ContractError(f"{label} is not canonical")
    return value


def stable_foreign_projection(items: list[dict[str, object]]) -> list[dict[str, object]]:
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ContractError("foreign projection must be a list of objects")
    return [
        {
            key: value
            for key, value in item.items()
            if key not in {"bound_port_set", "restart_count"}
        }
        for item in items
    ]


def build_manifest(
    *,
    outcome_id: str,
    created_at: datetime,
    expires_at: datetime,
    artifact_paths: tuple[Path, ...],
) -> dict[str, object]:
    _validate_outcome_id(outcome_id)
    created = _validate_datetime(created_at, "created_at")
    expires = _validate_datetime(expires_at, "expires_at")
    if expires <= created:
        raise ContractError("expires_at must be after created_at")
    if not isinstance(artifact_paths, tuple) or not artifact_paths:
        raise ContractError("artifact_paths must be a non-empty tuple")

    artifacts: list[dict[str, object]] = []
    names: set[str] = set()
    for artifact_path in artifact_paths:
        if not isinstance(artifact_path, Path):
            raise ContractError("artifact path must be Path")
        name = artifact_path.name
        if name != str(artifact_path) and not artifact_path.is_absolute():
            raise ContractError("artifact path must not contain a parent")
        if name in names:
            raise ContractError("artifact names must be unique")
        names.add(name)
        payload = _read_regular_file(artifact_path, label="artifact")
        artifacts.append(
            {"path": name, "size": len(payload), "sha256": sha256_bytes(payload)}
        )

    foundation = _read_regular_file(FOUNDATION_PATH, label="foundation")
    return {
        "schema": MANIFEST_SCHEMA,
        "outcome_id": outcome_id,
        "created_at": _format_datetime(created),
        "expires_at": _format_datetime(expires),
        "target_role": "spain-primary",
        "source_base": SOURCE_BASE,
        "source_head": SOURCE_HEAD,
        "spain_overlay": SPAIN_OVERLAY,
        "candidate": dict(CANDIDATE),
        "artifacts": artifacts,
        "foundation_sha256": sha256_bytes(foundation),
        "allowed_command_families": list(ALLOWED_COMMAND_FAMILIES),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "max_attempts": 1,
        "remote_write_allowed": False,
        "package_build_allowed": False,
        "live_action_authorized": False,
    }


def validate_manifest(value: object, *, artifact_root: Path) -> dict[str, object]:
    manifest = _require_exact_object(value, MANIFEST_KEYS, "manifest")
    if manifest["schema"] != MANIFEST_SCHEMA:
        raise ContractError("manifest schema")
    _validate_outcome_id(manifest["outcome_id"])
    created = _parse_datetime(manifest["created_at"], "created_at")
    expires = _parse_datetime(manifest["expires_at"], "expires_at")
    if expires <= created:
        raise ContractError("manifest expiry")
    if expires <= datetime.now(timezone.utc):
        raise ContractError("manifest expired")
    if (
        manifest["target_role"] != "spain-primary"
        or manifest["source_base"] != SOURCE_BASE
        or manifest["source_head"] != SOURCE_HEAD
        or manifest["spain_overlay"] != SPAIN_OVERLAY
    ):
        raise ContractError("manifest identity")
    if manifest["candidate"] != CANDIDATE:
        raise ContractError("manifest candidate")
    if manifest["max_attempts"] != 1:
        raise ContractError("manifest max_attempts")
    for key in (
        "remote_write_allowed",
        "package_build_allowed",
        "live_action_authorized",
    ):
        if manifest[key] is not False:
            raise ContractError(f"manifest {key}")
    if manifest["allowed_command_families"] != ALLOWED_COMMAND_FAMILIES:
        raise ContractError("manifest allowed command families")
    if manifest["forbidden_actions"] != FORBIDDEN_ACTIONS:
        raise ContractError("manifest forbidden actions")

    root = _validate_artifact_root(artifact_root)
    foundation_sha256 = sha256_bytes(_read_regular_file(FOUNDATION_PATH, label="foundation"))
    if manifest["foundation_sha256"] != foundation_sha256:
        raise ContractError("manifest foundation sha256")
    artifacts = manifest["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        raise ContractError("manifest artifacts")
    names: set[str] = set()
    for item in artifacts:
        artifact = _require_exact_object(item, {"path", "size", "sha256"}, "artifact")
        path = artifact["path"]
        if not isinstance(path, str) or not _is_safe_artifact_name(path):
            raise ContractError("artifact path")
        if path in names:
            raise ContractError("artifact paths must be unique")
        names.add(path)
        if not isinstance(artifact["size"], int) or artifact["size"] < 0:
            raise ContractError("artifact size")
        _validate_sha256(artifact["sha256"], "artifact sha256")
        payload = _read_regular_file(root / path, label="artifact")
        if len(payload) != artifact["size"] or sha256_bytes(payload) != artifact["sha256"]:
            raise ContractError("artifact checksum mismatch")
    return dict(manifest)


def validate_success_evidence(
    value: object, *, manifest: Mapping[str, object]
) -> dict[str, object]:
    evidence = _require_exact_object(value, SUCCESS_KEYS, "success evidence")
    manifest_value = _require_exact_object(manifest, MANIFEST_KEYS, "manifest")
    _validate_evidence_identity(evidence, manifest_value, SUCCESS_SCHEMA)
    _validate_sha256(evidence["runner_sha256"], "runner sha256")
    _validate_sha256(evidence["collector_sha256"], "collector sha256")
    _validate_sha256(evidence["schema_sha256"], "schema sha256")
    if evidence["phase12_foundation_sha256"] != manifest_value["foundation_sha256"]:
        raise ContractError("foundation sha256")
    _validate_candidate_resources(evidence["candidate_resources"])
    awg2_equal = _validate_awg2_equality(evidence["awg2_equality"])
    foreign_equal = _validate_foreign_equality(evidence["foreign_equality"])
    _validate_safety_receipt(evidence["safety_receipt"])
    decision = evidence["decision"]
    reasons = evidence["stop_reasons"]
    if decision not in {"pass", "stop"}:
        raise ContractError("success evidence decision")
    if not isinstance(reasons, list) or any(
        not isinstance(reason, str) or not reason for reason in reasons
    ):
        raise ContractError("success evidence stop reasons")
    if reasons != sorted(reasons) or len(reasons) != len(set(reasons)):
        raise ContractError("success evidence stop reasons must be ordered")
    if decision == "pass":
        if reasons:
            raise ContractError("pass decision requires no stop reasons")
        if not awg2_equal or not foreign_equal:
            raise ContractError("pass decision requires equality")
        if any(item["state"] not in {"absent", "free"} for item in evidence["candidate_resources"]):
            raise ContractError("pass decision requires free candidate resources")
    elif not reasons:
        raise ContractError("stop decision requires stop reasons")
    return dict(evidence)


def validate_failure_evidence(
    value: object, *, manifest: Mapping[str, object]
) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ContractError("failure evidence keys")
    schema = value.get("schema")
    if schema == FAILURE_SCHEMA_V1:
        evidence = _require_exact_object(value, FAILURE_KEYS_V1, "failure evidence")
        failure_schema = FAILURE_SCHEMA_V1
    elif schema == FAILURE_SCHEMA_V2:
        evidence = _require_exact_object(value, FAILURE_KEYS_V2, "failure evidence")
        failure_schema = FAILURE_SCHEMA_V2
    elif schema == FAILURE_SCHEMA_V3:
        evidence = _require_exact_object(value, FAILURE_KEYS_V3, "failure evidence")
        failure_schema = FAILURE_SCHEMA_V3
    else:
        raise ContractError("failure evidence schema")
    manifest_value = _require_exact_object(manifest, MANIFEST_KEYS, "manifest")
    _validate_evidence_identity(evidence, manifest_value, failure_schema)
    if evidence["stage"] not in FAILURE_STAGES:
        raise ContractError("failure evidence stage")
    if evidence["reason_code"] not in FAILURE_REASONS:
        raise ContractError("failure evidence reason")
    if failure_schema in {FAILURE_SCHEMA_V2, FAILURE_SCHEMA_V3}:
        subreason = evidence["transport_subreason"]
        if evidence["stage"] == "transport":
            if evidence["reason_code"] != "observation_ambiguous":
                raise ContractError("failure evidence transport reason")
            allowed_subreasons = (
                TRANSPORT_SUBREASONS_V2
                if failure_schema == FAILURE_SCHEMA_V2
                else TRANSPORT_SUBREASONS_V3
            )
            if subreason not in allowed_subreasons:
                raise ContractError("failure evidence transport subreason")
        elif subreason != NOT_APPLICABLE_SUBREASON:
            raise ContractError("failure evidence subreason must be not applicable")
    if evidence["decision"] != "stop":
        raise ContractError("failure evidence decision")
    _validate_safety_receipt(evidence["safety_receipt"])
    return dict(evidence)


def verify_local(*, repo_root: Path = ROOT) -> dict[str, object]:
    if not isinstance(repo_root, Path) or repo_root.is_symlink() or not repo_root.is_dir():
        raise ContractError("repository root")
    artifact_payloads = tuple(
        _read_regular_file(repo_root / relative_path, label="local artifact")
        for relative_path in LOCAL_ARTIFACT_RELATIVE_PATHS
    )
    if len(artifact_payloads) != len(LOCAL_ARTIFACT_NAMES):
        raise ContractError("local artifact inventory")
    foundation_index = LOCAL_ARTIFACT_NAMES.index("phase12-equality-foundation.json")
    if sha256_bytes(artifact_payloads[foundation_index]) != PHASE12_FOUNDATION_SHA256:
        raise ContractError("foundation checksum")
    try:
        foundation = json.loads(artifact_payloads[foundation_index].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError("phase12 foundation") from error
    if foundation.get("schema") != "amn2.phase13.phase12-equality-foundation.v1":
        raise ContractError("phase12 foundation")
    return {
        "artifact_count": len(LOCAL_ARTIFACT_NAMES),
        "candidate_sha256": sha256_bytes(canonical_json_bytes(CANDIDATE)),
        "live_action_authorized": False,
        "network_attempted": False,
        "package_build_performed": False,
        "result": "passed",
    }


def prepare_test_manifest(
    *, artifact_root: Path, output_path: Path, outcome_id: str
) -> dict[str, object]:
    root = _require_temp_directory(artifact_root, "artifact root")
    output = _require_temp_output_path(output_path)
    artifact_paths = tuple(root / name for name in LOCAL_ARTIFACT_NAMES)
    manifest = build_manifest(
        outcome_id=outcome_id,
        created_at=TEST_MANIFEST_CREATED_AT,
        expires_at=TEST_MANIFEST_EXPIRES_AT,
        artifact_paths=artifact_paths,
    )
    validate_manifest(manifest, artifact_root=root)
    payload = canonical_json_bytes(manifest)
    try:
        with output.open("xb") as stream:
            stream.write(payload)
    except OSError as error:
        raise ContractError("test manifest write") from error
    return {
        "artifact_count": len(LOCAL_ARTIFACT_NAMES),
        "manifest_sha256": sha256_bytes(payload),
        "network_attempted": False,
        "package_build_performed": False,
        "result": "prepared_test_manifest",
    }


def _read_regular_file(path: Path, *, label: str) -> bytes:
    if not isinstance(path, Path) or path.is_symlink() or not path.is_file():
        raise ContractError(f"{label} must be a regular non-symlink file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ContractError(f"{label} could not be opened") from error
    try:
        file_stat = os.fstat(descriptor)
        if not stat.S_ISREG(file_stat.st_mode):
            raise ContractError(f"{label} must be a regular file")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _validate_artifact_root(value: Path) -> Path:
    if not isinstance(value, Path) or value.is_symlink() or not value.is_dir():
        raise ContractError("artifact root")
    return value


def _require_exact_object(
    value: object, expected_keys: set[str], label: str
) -> dict[str, object]:
    if not isinstance(value, Mapping) or set(value) != expected_keys:
        raise ContractError(f"{label} keys")
    return dict(value)


def _validate_outcome_id(value: object) -> None:
    if not isinstance(value, str) or OUTCOME_ID_PATTERN.fullmatch(value) is None:
        raise ContractError("outcome_id")


def _validate_datetime(value: object, label: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ContractError(label)
    return value.astimezone(timezone.utc)


def _format_datetime(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _parse_datetime(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise ContractError(label)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError(label) from error
    return _validate_datetime(parsed, label)


def _validate_sha256(value: object, label: str) -> None:
    if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
        raise ContractError(label)


def _is_safe_artifact_name(value: str) -> bool:
    return value not in {"", ".", ".."} and Path(value).name == value


def _validate_evidence_identity(
    evidence: Mapping[str, object], manifest: Mapping[str, object], schema: str
) -> None:
    if evidence["schema"] != schema:
        raise ContractError("evidence schema")
    if evidence["outcome_id"] != manifest["outcome_id"]:
        raise ContractError("evidence outcome")
    _parse_datetime(evidence["checked_at"], "checked_at")
    if evidence["source_head"] != manifest["source_head"]:
        raise ContractError("evidence source head")
    _validate_sha256(evidence["manifest_sha256"], "manifest sha256")
    if evidence["manifest_sha256"] != sha256_bytes(canonical_json_bytes(manifest)):
        raise ContractError("manifest sha256")


def _validate_candidate_resources(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise ContractError("candidate resources")
    expected = {"resource", "declared_value", "state", "observation_sha256"}
    states = {"absent", "free", "conflict", "ambiguous", "unavailable"}
    for item in value:
        resource = _require_exact_object(item, expected, "candidate resource")
        if not isinstance(resource["resource"], str) or not resource["resource"]:
            raise ContractError("candidate resource name")
        if not isinstance(resource["declared_value"], str) or not resource["declared_value"]:
            raise ContractError("candidate resource value")
        if resource["state"] not in states:
            raise ContractError("candidate resource state")
        _validate_sha256(resource["observation_sha256"], "candidate observation sha256")


def _validate_awg2_equality(value: object) -> bool:
    keys = {
        "container_equal", "service_equal", "interface_equal", "udp_port_equal",
        "vpn_cidr_route_equal", "persistent_peers", "live_peers", "peer_set_sha256",
        "restart_count", "forward_rule_count", "web_listener_equal", "bot_disabled", "equal",
    }
    equality = _require_exact_object(value, keys, "awg2 equality")
    for key in (
        "container_equal", "service_equal", "interface_equal", "udp_port_equal",
        "vpn_cidr_route_equal", "web_listener_equal", "bot_disabled", "equal",
    ):
        if not isinstance(equality[key], bool):
            raise ContractError("awg2 equality boolean")
    for key in ("persistent_peers", "live_peers", "restart_count", "forward_rule_count"):
        if not isinstance(equality[key], int) or equality[key] < 0:
            raise ContractError("awg2 equality count")
    _validate_sha256(equality["peer_set_sha256"], "awg2 peer set sha256")
    return equality["equal"]


def _validate_foreign_equality(value: object) -> bool:
    keys = {
        "persistent_entries", "stable_sha256", "changed", "equality_receipt_sha256", "equal",
    }
    equality = _require_exact_object(value, keys, "foreign equality")
    for key in ("persistent_entries", "changed"):
        if not isinstance(equality[key], int) or equality[key] < 0:
            raise ContractError("foreign equality count")
    _validate_sha256(equality["stable_sha256"], "foreign stable sha256")
    _validate_sha256(equality["equality_receipt_sha256"], "foreign receipt sha256")
    if not isinstance(equality["equal"], bool):
        raise ContractError("foreign equality boolean")
    return equality["equal"]


def _validate_safety_receipt(value: object) -> None:
    receipt = _require_exact_object(value, SAFETY_KEYS, "safety receipt")
    if any(receipt[key] is not False for key in SAFETY_KEYS):
        raise ContractError("safety receipt")


def _require_temp_directory(value: Path, label: str) -> Path:
    if not isinstance(value, Path) or value.is_symlink() or not value.is_dir():
        raise ContractError(label)
    resolved = value.resolve(strict=True)
    temporary_root = Path(tempfile.gettempdir()).resolve(strict=True)
    try:
        resolved.relative_to(temporary_root)
    except ValueError as error:
        raise ContractError(label) from error
    return resolved


def _require_temp_output_path(value: Path) -> Path:
    if not isinstance(value, Path) or value.suffix != ".json":
        raise ContractError("test manifest output")
    parent = value.parent
    if parent.is_symlink() or not parent.is_dir():
        raise ContractError("test manifest output")
    resolved = value.resolve(strict=False)
    temporary_root = Path(tempfile.gettempdir()).resolve(strict=True)
    try:
        resolved.relative_to(temporary_root)
    except ValueError as error:
        raise ContractError("test manifest output") from error
    return resolved


def _main(arguments: list[str]) -> int:
    try:
        if arguments == ["verify-local"]:
            sys.stdout.buffer.write(canonical_json_bytes(verify_local()))
            return 0
        if len(arguments) == 7 and arguments[0] == "prepare-test-manifest":
            option_values = dict(zip(arguments[1::2], arguments[2::2], strict=True))
            if set(option_values) != {"--artifact-root", "--out", "--outcome-id"}:
                raise ContractError("invocation")
            report = prepare_test_manifest(
                artifact_root=Path(option_values["--artifact-root"]),
                output_path=Path(option_values["--out"]),
                outcome_id=option_values["--outcome-id"],
            )
            sys.stdout.buffer.write(canonical_json_bytes(report))
            return 0
    except (ContractError, OSError, ValueError):
        return 64
    return 64


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
