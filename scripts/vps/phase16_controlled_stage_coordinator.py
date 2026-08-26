#!/usr/bin/python3
"""Checksum/state/rollback-bound coordinator for one controlled Phase 16 stage."""

from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile


PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-014"
REQUEST_SCHEMA = "amn2.phase16.controlled-stage-request.v1"
CLAIM_SCHEMA = "amn2.phase16.stage-claim.v1"
PACKAGE_ROOT = Path("/var/lib/amn2-phase16/package")
TRANSACTION_ROOT = Path("/var/lib/amn2-phase16/transactions")
APPLICATION_RELEASE = Path(f"/opt/amn2-spain/releases/{PACKAGE_ID}")
APPLICATION_LEDGER = Path("/var/lib/amn2-phase16/stage/application.json")
RUNTIME_LEDGER = Path("/var/lib/amn2-phase16/stage/awg31-runtime.json")
COORDINATOR_LEDGER = Path("/var/lib/amn2-phase16/stage/coordinator.json")
DATABASE_PATH = Path("/var/lib/amn2-spain/amn2.sqlite3")
DOCKER_BINARY = "/opt/amn2-spain/docker/bin/docker"
DOCKER_SOCKET = "unix:///run/amn2-spain-docker/docker.sock"
MAX_HEADER_BYTES = 65536
MAX_ARCHIVE_BYTES = 268435456
MAX_ENTRY_BYTES = 67108864
MAX_ENTRIES = 4096
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TRANSACTION_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}$")

ROLLBACK_SCOPE = {
    "application_ledger": "/var/lib/amn2-phase16/stage/application.json",
    "application_release": f"/opt/amn2-spain/releases/{PACKAGE_ID}",
    "backup_policy": "preserve_checksum_bound_sqlite_backup",
    "coordinator_ledger": "/var/lib/amn2-phase16/stage/coordinator.json",
    "package_root": "/var/lib/amn2-phase16/package",
    "runtime_ledger": "/var/lib/amn2-phase16/stage/awg31-runtime.json",
    "runtime_resources": [
        "/etc/systemd/system/amn2-spain-awg3.service",
        "/var/lib/amn2-spain/awg3",
        "container:amn2-spain-awg3",
        "network:amn2sp3",
    ],
    "schema": "amn2.phase16.controlled-stage-rollback-scope.v1",
}


class StageCoordinatorError(ValueError):
    pass


def canonical_json_bytes(value: object) -> bytes:
    try:
        return (
            json.dumps(
                value,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("ascii")
            + b"\n"
        )
    except (TypeError, ValueError) as exc:
        raise StageCoordinatorError("canonical JSON") from exc


def _load_canonical(raw: bytes, *, label: str) -> dict[str, object]:
    def exact_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise StageCoordinatorError(f"{label} duplicate key")
            result[key] = value
        return result

    try:
        value = json.loads(raw.decode("ascii"), object_pairs_hook=exact_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise StageCoordinatorError(f"{label} JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise StageCoordinatorError(f"{label} canonical form")
    return value


def rollback_scope_sha256() -> str:
    return hashlib.sha256(canonical_json_bytes(ROLLBACK_SCOPE)).hexdigest()


def _write_all(descriptor: int, body: bytes) -> None:
    offset = 0
    while offset < len(body):
        written = os.write(descriptor, body[offset:])
        if written < 1:
            raise StageCoordinatorError("short write")
        offset += written


def validate_stage_request(
    raw: bytes,
    *,
    manifest_bytes: bytes,
    approval_bytes: bytes,
    expected_rollback_scope_sha256: str | None = None,
) -> dict[str, object]:
    try:
        request = _load_canonical(raw, label="request")
        exact = {
            "approval_sha256",
            "expected_current_state_sha256",
            "manifest_sha256",
            "package_id",
            "package_identity_sha256",
            "rollback_scope_sha256",
            "schema",
            "transaction_id",
        }
        manifest = _load_canonical(manifest_bytes, label="manifest")
        valid = set(request) == exact
        valid = valid and request["schema"] == REQUEST_SCHEMA
        valid = valid and request["package_id"] == PACKAGE_ID
        valid = valid and isinstance(request["transaction_id"], str)
        valid = valid and TRANSACTION_RE.fullmatch(request["transaction_id"]) is not None
        for key in (
            "approval_sha256",
            "expected_current_state_sha256",
            "manifest_sha256",
            "package_identity_sha256",
            "rollback_scope_sha256",
        ):
            valid = valid and isinstance(request[key], str)
            valid = valid and SHA256_RE.fullmatch(request[key]) is not None
        valid = valid and request["approval_sha256"] == hashlib.sha256(
            approval_bytes
        ).hexdigest()
        valid = valid and request["manifest_sha256"] == hashlib.sha256(
            manifest_bytes
        ).hexdigest()
        valid = valid and manifest.get("package_id") == PACKAGE_ID
        valid = valid and manifest.get("package_identity_sha256") == request[
            "package_identity_sha256"
        ]
        if expected_rollback_scope_sha256 is not None:
            valid = valid and request[
                "rollback_scope_sha256"
            ] == expected_rollback_scope_sha256
    except (KeyError, TypeError, StageCoordinatorError):
        valid = False
    if not valid:
        raise StageCoordinatorError("request binding")
    return request


def build_stage_claim(
    request: dict[str, object],
    *,
    gate: str,
    script_bytes: bytes,
    issued_at: str,
    expires_at: str,
) -> dict[str, object]:
    if gate not in {"APPLICATION_STAGE", "AWG31_RUNTIME_STAGE"}:
        raise StageCoordinatorError("stage gate")
    claim_id = f"{request['transaction_id']}-{gate.lower().replace('_', '-')}"
    if len(claim_id) > 128:
        raise StageCoordinatorError("claim id")
    return {
        "claim_id": claim_id,
        "consumed_at": None,
        "expected_current_state_sha256": request["expected_current_state_sha256"],
        "expires_at": expires_at,
        "future_gate": gate,
        "issued_at": issued_at,
        "manifest_sha256": request["manifest_sha256"],
        "package_id": PACKAGE_ID,
        "package_identity_sha256": request["package_identity_sha256"],
        "rollback_scope_sha256": request["rollback_scope_sha256"],
        "schema": CLAIM_SCHEMA,
        "stage_script_sha256": hashlib.sha256(script_bytes).hexdigest(),
        "status": "issued",
    }


def _safe_archive_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise StageCoordinatorError("archive path")
    path = PurePosixPath(value)
    if path.is_absolute() or value != path.as_posix() or any(
        part in {"", ".", ".."} or ":" in part for part in path.parts
    ):
        raise StageCoordinatorError("archive path")
    return path


def _verify_manifest_identity(manifest: dict[str, object]) -> None:
    if manifest.get("package_id") != PACKAGE_ID:
        raise StageCoordinatorError("manifest package")
    identity = manifest.get("package_identity_sha256")
    if not isinstance(identity, str) or SHA256_RE.fullmatch(identity) is None:
        raise StageCoordinatorError("manifest identity")
    unsigned = dict(manifest)
    del unsigned["package_identity_sha256"]
    if hashlib.sha256(canonical_json_bytes(unsigned)).hexdigest() != identity:
        raise StageCoordinatorError("manifest identity")


def _extract_verified_package(archive_bytes: bytes, destination: Path) -> bytes:
    try:
        archive = zipfile.ZipFile(io.BytesIO(archive_bytes), mode="r")
    except zipfile.BadZipFile as exc:
        raise StageCoordinatorError("archive invalid") from exc
    with archive:
        infos = archive.infolist()
        if not infos or len(infos) > MAX_ENTRIES:
            raise StageCoordinatorError("archive inventory")
        names: list[str] = []
        by_name: dict[str, zipfile.ZipInfo] = {}
        for info in infos:
            path = _safe_archive_path(info.filename)
            mode = (info.external_attr >> 16) & 0o170000
            if info.is_dir() or info.flag_bits & 0x1 or mode == stat.S_IFLNK:
                raise StageCoordinatorError("archive member")
            if info.file_size > MAX_ENTRY_BYTES or info.compress_size > MAX_ENTRY_BYTES:
                raise StageCoordinatorError("archive member size")
            name = path.as_posix()
            if name in by_name or name.casefold() in {item.casefold() for item in names}:
                raise StageCoordinatorError("archive duplicate")
            names.append(name)
            by_name[name] = info
        manifest_info = by_name.get("manifest.json")
        if manifest_info is None:
            raise StageCoordinatorError("manifest missing")
        manifest_bytes = archive.read(manifest_info)
        manifest = _load_canonical(manifest_bytes, label="manifest")
        _verify_manifest_identity(manifest)
        entries = manifest.get("entries")
        if not isinstance(entries, list) or not entries:
            raise StageCoordinatorError("manifest entries")
        expected = {"manifest.json"}
        entry_by_path: dict[str, dict[str, object]] = {}
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {
                "gate",
                "mode",
                "path",
                "role",
                "rollback_role",
                "secret_classification",
                "sha256",
                "size",
            }:
                raise StageCoordinatorError("manifest entry")
            path = _safe_archive_path(entry["path"]).as_posix()
            if path in expected or not isinstance(entry["size"], int):
                raise StageCoordinatorError("manifest entry")
            if entry["mode"] not in {"0644", "0755"}:
                raise StageCoordinatorError("manifest entry mode")
            if not isinstance(entry["sha256"], str) or SHA256_RE.fullmatch(
                entry["sha256"]
            ) is None:
                raise StageCoordinatorError("manifest entry hash")
            expected.add(path)
            entry_by_path[path] = entry
        if set(names) != expected:
            raise StageCoordinatorError("archive inventory")
        destination.mkdir(mode=0o700)
        for name in sorted(expected):
            info = by_name[name]
            body = archive.read(info)
            if name == "manifest.json":
                mode = 0o644
            else:
                entry = entry_by_path[name]
                if len(body) != entry["size"] or hashlib.sha256(body).hexdigest() != entry[
                    "sha256"
                ]:
                    raise StageCoordinatorError("package checksum")
                mode = int(entry["mode"], 8)
            target = destination.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
            try:
                _write_all(descriptor, body)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            os.chmod(target, mode)
        return manifest_bytes


def _atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        _write_all(descriptor, canonical_json_bytes(value))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def _run(arguments: list[str], *, env: dict[str, str] | None = None, timeout: int = 180) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        arguments,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
        env=env,
    )
    if len(result.stdout) > 8192 or len(result.stderr) > 8192:
        raise StageCoordinatorError("stage output bound")
    return result


def _run_stage(script: Path, claim: Path, gate: str, request: dict[str, object]) -> None:
    environment = {
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": "/usr/bin:/usr/sbin:/bin:/sbin",
        "PHASE16_EXPECTED_CURRENT_STATE_SHA256": str(
            request["expected_current_state_sha256"]
        ),
        "PHASE16_FUTURE_GATE": gate,
        "PHASE16_MANIFEST_SHA256": str(request["manifest_sha256"]),
        "PHASE16_PACKAGE_ID": PACKAGE_ID,
        "PHASE16_PACKAGE_IDENTITY_SHA256": str(
            request["package_identity_sha256"]
        ),
        "PHASE16_PACKAGE_ROOT": str(PACKAGE_ROOT),
        "PHASE16_ROLLBACK_SCOPE_SHA256": str(request["rollback_scope_sha256"]),
        "PHASE16_STAGE_CLAIM_FILE": str(claim),
    }
    if gate == "APPLICATION_STAGE":
        environment.update(
            {
                "PHASE16_APPLICATION_RELEASE_ROOT": str(APPLICATION_RELEASE),
                "PHASE16_DATABASE_PATH": str(DATABASE_PATH),
                "PHASE16_STAGE_LEDGER": str(APPLICATION_LEDGER),
            }
        )
    else:
        environment["PHASE16_STAGE_LEDGER"] = str(RUNTIME_LEDGER)
    result = _run(["/usr/bin/bash", str(script)], env=environment)
    if result.returncode != 0 or result.stderr or not result.stdout.endswith(b"\n"):
        raise StageCoordinatorError("stage envelope failed")


def _docker(*arguments: str, timeout: int = 30) -> subprocess.CompletedProcess[bytes]:
    return _run(
        [DOCKER_BINARY, "--host", DOCKER_SOCKET, *arguments], timeout=timeout
    )


def _awg2_snapshot() -> str:
    owner = _run(
        ["/usr/bin/systemctl", "is-active", "amn2-spain-docker.service"], timeout=10
    )
    container = _docker(
        "inspect",
        "--format={{.Id}}|{{.State.Running}}|{{.RestartCount}}",
        "amn2-spain-awg",
        timeout=10,
    )
    peers = _docker(
        "exec", "amn2-spain-awg", "/usr/bin/awg", "show", "awgsp0", "peers", timeout=10
    )
    if any(result.returncode != 0 or result.stderr for result in (owner, container, peers)):
        raise StageCoordinatorError("awg2 snapshot")
    normalized = b"\x00".join(
        (owner.stdout.strip(), container.stdout.strip(), hashlib.sha256(peers.stdout).digest())
    )
    return hashlib.sha256(normalized).hexdigest()


def _rollback_runtime() -> None:
    image_created = False
    try:
        ledger = _load_canonical(RUNTIME_LEDGER.read_bytes(), label="runtime ledger")
        image_created = ledger.get("runtime_image_created") is True
    except Exception:
        pass
    _run(["/usr/bin/systemctl", "stop", "amn2-spain-awg3.service"], timeout=30)
    Path("/etc/systemd/system/amn2-spain-awg3.service").unlink(missing_ok=True)
    _run(["/usr/bin/systemctl", "daemon-reload"], timeout=30)
    _docker("rm", "-f", "amn2-spain-awg3", timeout=30)
    _docker("network", "rm", "amn2sp3", timeout=30)
    state_root = Path("/var/lib/amn2-spain/awg3")
    if state_root.is_dir() and not state_root.is_symlink():
        shutil.rmtree(state_root)
    RUNTIME_LEDGER.unlink(missing_ok=True)
    if image_created:
        _docker(
            "image",
            "rm",
            "docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d",
            timeout=30,
        )


def _approval_text(request: dict[str, object]) -> str:
    return (
        "/APPROVE PHASE16 SPAIN APPLICATION_AND_AWG31_STAGE "
        f"PACKAGE_{PACKAGE_ID} "
        f"IDENTITY_{request['package_identity_sha256']} "
        f"MANIFEST_SHA256_{request['manifest_sha256']} "
        f"STATE_{request['expected_current_state_sha256']} "
        f"ROLLBACK_SCOPE_SHA256_{request['rollback_scope_sha256']} "
        f"TRANSACTION_{request['transaction_id']} "
        "MANDATORY_ROLLBACK_ON_FAILURE AWG2_UNTOUCHED"
    )


def _read_frame() -> tuple[dict[str, object], bytes]:
    length_raw = sys.stdin.buffer.read(8)
    if len(length_raw) != 8 or re.fullmatch(rb"[0-9a-f]{8}", length_raw) is None:
        raise StageCoordinatorError("frame header")
    length = int(length_raw, 16)
    if length < 2 or length > MAX_HEADER_BYTES:
        raise StageCoordinatorError("frame header")
    header_raw = sys.stdin.buffer.read(length)
    if len(header_raw) != length:
        raise StageCoordinatorError("frame header")
    header = _load_canonical(header_raw, label="frame")
    if set(header) != {
        "approval",
        "archive_sha256",
        "archive_size",
        "coordinator_sha256",
        "request",
    }:
        raise StageCoordinatorError("frame fields")
    size = header["archive_size"]
    if not isinstance(size, int) or isinstance(size, bool) or not 1 <= size <= MAX_ARCHIVE_BYTES:
        raise StageCoordinatorError("archive size")
    archive = sys.stdin.buffer.read(size + 1)
    if len(archive) != size:
        raise StageCoordinatorError("archive frame")
    if not isinstance(header["archive_sha256"], str) or hashlib.sha256(archive).hexdigest() != header["archive_sha256"]:
        raise StageCoordinatorError("archive checksum")
    return header, archive


def _safe_base() -> None:
    for path in (Path("/var"), Path("/var/lib")):
        if path.is_symlink() or not path.is_dir():
            raise StageCoordinatorError("state parent")
    base = Path("/var/lib/amn2-phase16")
    if os.path.lexists(base):
        if base.is_symlink() or not base.is_dir():
            raise StageCoordinatorError("state root")
    else:
        base.mkdir(mode=0o700)
    TRANSACTION_ROOT.mkdir(mode=0o700, exist_ok=True)


def execute_stage(header: dict[str, object], archive: bytes) -> dict[str, object]:
    _safe_base()
    request_value = header["request"]
    if not isinstance(request_value, dict):
        raise StageCoordinatorError("request frame")
    transaction_id = request_value.get("transaction_id")
    if not isinstance(transaction_id, str) or TRANSACTION_RE.fullmatch(transaction_id) is None:
        raise StageCoordinatorError("transaction id")
    transaction = TRANSACTION_ROOT / transaction_id
    if os.path.lexists(transaction) or os.path.lexists(PACKAGE_ROOT):
        raise StageCoordinatorError("stage target exists")
    transaction.mkdir(mode=0o700)
    staged_package = transaction / "package.staging"
    package_installed = False
    application_completed = False
    runtime_completed = False
    before_awg2 = ""
    try:
        manifest_bytes = _extract_verified_package(archive, staged_package)
        request = validate_stage_request(
            canonical_json_bytes(request_value),
            manifest_bytes=manifest_bytes,
            approval_bytes=str(header["approval"]).encode("ascii"),
            expected_rollback_scope_sha256=rollback_scope_sha256(),
        )
        if header["approval"] != _approval_text(request):
            raise StageCoordinatorError("approval binding")
        coordinator_path = staged_package / "tooling/scripts/vps/phase16_controlled_stage_coordinator.py"
        coordinator_sha = hashlib.sha256(coordinator_path.read_bytes()).hexdigest()
        embedded_sha = globals().get("PHASE16_EMBEDDED_SOURCE_SHA256", "")
        if coordinator_sha != header["coordinator_sha256"] or embedded_sha != coordinator_sha:
            raise StageCoordinatorError("coordinator binding")
        before_awg2 = _awg2_snapshot()
        PACKAGE_ROOT.parent.mkdir(mode=0o700, exist_ok=True)
        staged_package.replace(PACKAGE_ROOT)
        package_installed = True
        now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
        expires = now + dt.timedelta(minutes=5)
        issued_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        expires_at = expires.strftime("%Y-%m-%dT%H:%M:%SZ")
        app_script = PACKAGE_ROOT / "tooling/scripts/vps/phase16_application_stage_remote.sh"
        runtime_script = PACKAGE_ROOT / "tooling/scripts/vps/phase16_awg31_runtime_stage_remote.sh"
        app_claim = transaction / "application-claim.json"
        runtime_claim = transaction / "runtime-claim.json"
        _atomic_json(
            app_claim,
            build_stage_claim(
                request,
                gate="APPLICATION_STAGE",
                script_bytes=app_script.read_bytes(),
                issued_at=issued_at,
                expires_at=expires_at,
            ),
        )
        _atomic_json(
            runtime_claim,
            build_stage_claim(
                request,
                gate="AWG31_RUNTIME_STAGE",
                script_bytes=runtime_script.read_bytes(),
                issued_at=issued_at,
                expires_at=expires_at,
            ),
        )
        _run_stage(app_script, app_claim, "APPLICATION_STAGE", request)
        application_completed = True
        _run_stage(runtime_script, runtime_claim, "AWG31_RUNTIME_STAGE", request)
        runtime_completed = True
        after_awg2 = _awg2_snapshot()
        if after_awg2 != before_awg2:
            raise StageCoordinatorError("awg2 state changed")
        outcome = {
            "awg2_state_equal": True,
            "general_issuance_enabled": False,
            "manifest_sha256": request["manifest_sha256"],
            "package_id": PACKAGE_ID,
            "package_identity_sha256": request["package_identity_sha256"],
            "result": "application_and_awg31_staged",
            "rollback_scope_sha256": request["rollback_scope_sha256"],
            "schema": "amn2.phase16.controlled-stage-outcome.v1",
            "state_sha256": request["expected_current_state_sha256"],
            "transaction_id": transaction_id,
        }
        _atomic_json(COORDINATOR_LEDGER, outcome)
        _atomic_json(transaction / "outcome.json", outcome)
        return outcome
    except Exception:
        if runtime_completed:
            try:
                _rollback_runtime()
            except Exception:
                pass
        if application_completed:
            if APPLICATION_RELEASE.is_dir() and not APPLICATION_RELEASE.is_symlink():
                shutil.rmtree(APPLICATION_RELEASE)
            APPLICATION_LEDGER.unlink(missing_ok=True)
        COORDINATOR_LEDGER.unlink(missing_ok=True)
        if package_installed and PACKAGE_ROOT.is_dir() and not PACKAGE_ROOT.is_symlink():
            shutil.rmtree(PACKAGE_ROOT)
        failure = {
            "awg2_state_equal": None,
            "backup_preserved": True,
            "general_issuance_enabled": False,
            "package_id": PACKAGE_ID,
            "result": "rolled_back",
            "schema": "amn2.phase16.controlled-stage-outcome.v1",
            "transaction_id": transaction_id,
        }
        try:
            _atomic_json(transaction / "outcome.json", failure)
        except Exception:
            pass
        raise


def main() -> int:
    try:
        header, archive = _read_frame()
        outcome = execute_stage(header, archive)
    except Exception:
        outcome = {
            "general_issuance_enabled": False,
            "package_id": PACKAGE_ID,
            "result": "stage_failed_and_rollback_attempted",
            "schema": "amn2.phase16.controlled-stage-outcome.v1",
        }
        sys.stdout.buffer.write(canonical_json_bytes(outcome))
        return 70
    sys.stdout.buffer.write(canonical_json_bytes(outcome))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
