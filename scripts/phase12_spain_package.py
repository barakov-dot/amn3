from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import os
import re
import shutil
import stat
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


MANIFEST_NAME = "manifest.json"
PACKAGE_SCHEMA = "amn2.spain-install-package.v1"
WHEELHOUSE_SCHEMA = "amn2.spain-wheelhouse.v1"
DEFAULT_RUN009_EVIDENCE_SHA256 = "8d8a4e155b30c4b72c564056c71b159e222c53e3bdc60018c3f6099c1979e1a8"
DEFAULT_RUN009_FINGERPRINT_SHA256 = "e15219cb5204d54a9ad11263cfba1f7c86e16dab3287c752a8b6f136ec4a5ed5"
RUN009_EVIDENCE_SHA256 = DEFAULT_RUN009_EVIDENCE_SHA256
RUN009_FINGERPRINT_SHA256 = DEFAULT_RUN009_FINGERPRINT_SHA256
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
REQUIRED_KINDS = frozenset(
    {
        "source_runtime",
        "wheel_lock",
        "wheelhouse_inventory",
        "python_wheel",
        "docker_bundle",
        "awg_image_archive",
        "systemd_unit",
        "env_template",
        "server_config_template",
        "docker_daemon_template",
        "firewall_template",
        "runtime_script",
        "live_backend",
        "network_manager",
        "package_verifier",
        "precondition",
        "installer",
        "rollback",
        "resource_plan",
        "baseline_evidence",
        "fingerprint_array",
        "provenance",
    }
)
MULTIPLE_ALLOWED_KINDS = frozenset(
    {"systemd_unit", "env_template", "server_config_template", "python_wheel"}
)
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_TOTAL_UNPACKED_BYTES = 8 * 1024 * 1024 * 1024
MAX_WHEEL_ARCHIVE_BYTES = 1024 * 1024 * 1024
MAX_WHEEL_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024
MAX_WHEEL_MEMBER_BYTES = 512 * 1024 * 1024
MAX_WHEEL_COMPRESSION_RATIO = 200
BUFFERED_METADATA_KINDS = frozenset(
    {
        "wheel_lock",
        "wheelhouse_inventory",
        "python_wheel",
        "resource_plan",
        "baseline_evidence",
        "fingerprint_array",
        "provenance",
    }
)


class PackageVerificationError(ValueError):
    pass


FIXED_ARTIFACT_PATHS = {
    "wheel_lock": {"payload/python/wheelhouse/requirements-linux-x86_64-py312.lock"},
    "wheelhouse_inventory": {"payload/python/wheelhouse/wheelhouse-inventory.json"},
    "systemd_unit": {
        "units/amn2-spain-web.service",
        "units/amn2-spain-bot.service",
        "units/amn2-spain-docker.service",
        "units/amn2-spain-network.service",
    },
    "env_template": {"templates/runtime.env"},
    "server_config_template": {"templates/awgsp0.conf", "templates/servers.yml"},
    "docker_daemon_template": {"templates/docker-daemon.json"},
    "firewall_template": {"templates/nftables.conf"},
    "runtime_script": {"templates/awg-start.sh"},
    "live_backend": {"scripts/phase12_spain_live_backend.py"},
    "network_manager": {"scripts/phase12_spain_network.py"},
    "package_verifier": {"scripts/phase12_spain_package.py"},
    "precondition": {"scripts/phase12_spain_precondition.py"},
    "installer": {"scripts/phase12_spain_remote_executor.sh"},
    "rollback": {"scripts/phase12_spain_installer.py"},
    "resource_plan": {"metadata/resource-plan.json"},
    "baseline_evidence": {"metadata/run009-evidence.json"},
    "fingerprint_array": {"metadata/fingerprint-array.json"},
    "provenance": {"provenance/input-provenance.json"},
}


def _validate_artifact_path_contract(artifacts: list[dict[str, Any]]) -> None:
    actual: dict[str, set[str]] = {}
    for entry in artifacts:
        actual.setdefault(entry["kind"], set()).add(entry["path"])
    for kind, paths in FIXED_ARTIFACT_PATHS.items():
        if actual.get(kind) != paths:
            raise PackageVerificationError(f"required artifact path contract mismatch for {kind}")
    dynamic = {
        "source_runtime": r"payload/source/amn2-runtime-source-[0-9a-f]{40}\.tar\.gz",
        "docker_bundle": r"payload/docker/docker-[A-Za-z0-9._+-]+-linux-x86_64\.tgz",
        "awg_image_archive": r"payload/awg/amneziawg-go-[A-Za-z0-9._+-]+-linux-amd64\.tar",
        "python_wheel": r"payload/python/wheelhouse/[A-Za-z0-9._+-]+\.whl",
    }
    for kind, pattern in dynamic.items():
        paths = actual.get(kind, set())
        if not paths or any(re.fullmatch(pattern, path) is None for path in paths):
            raise PackageVerificationError(f"artifact path contract mismatch for {kind}")
        if kind != "python_wheel" and len(paths) != 1:
            raise PackageVerificationError(f"artifact count contract mismatch for {kind}")


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compact_json_bytes_preserving_object_order(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_canonical(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _load_json_exact(raw: bytes, label: str) -> Any:
    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise PackageVerificationError(f"{label} has duplicate key: {key}")
            result[key] = value
        return result

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageVerificationError(f"invalid {label} JSON") from exc


def _safe_relative_path(name: str, label: str) -> PurePosixPath:
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        raise PackageVerificationError(f"unsafe {label} path")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise PackageVerificationError(f"unsafe {label} path: {name}")
    if path.as_posix() != name:
        raise PackageVerificationError(f"non-canonical {label} path: {name}")
    return path


def _validate_layer_link_target(member_name: str, target: str) -> None:
    if not isinstance(target, str) or not target or "\\" in target or "\x00" in target:
        raise PackageVerificationError("unsafe AWG layer link target")
    combined = (
        PurePosixPath(target.removeprefix("/"))
        if target.startswith("/")
        else PurePosixPath(member_name).parent / target
    )
    resolved: list[str] = []
    for part in combined.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not resolved:
                raise PackageVerificationError("unsafe AWG layer link target")
            resolved.pop()
        else:
            resolved.append(part)
    if not resolved:
        raise PackageVerificationError("unsafe AWG layer link target")


def _validate_awg_layer_stream(stream) -> None:
    try:
        with tarfile.open(fileobj=stream, mode="r:*") as layer:
            seen: set[str] = set()
            for member in layer.getmembers():
                name = _safe_relative_path(member.name, "AWG layer member").as_posix()
                if name in seen:
                    raise PackageVerificationError("AWG layer duplicate member")
                seen.add(name)
                if member.issym() or member.islnk():
                    _validate_layer_link_target(member.name, member.linkname)
                elif not member.isfile() and not member.isdir():
                    raise PackageVerificationError("AWG layer special member forbidden")
    except tarfile.TarError as exc:
        raise PackageVerificationError("AWG layer archive invalid") from exc


def _validate_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise PackageVerificationError(f"invalid {label} hash")
    return value


def _validate_manifest(manifest: Any) -> list[dict[str, Any]]:
    if not isinstance(manifest, dict) or manifest.get("schema") != PACKAGE_SCHEMA:
        raise PackageVerificationError("unsupported package manifest schema")
    if set(manifest) != {
        "schema",
        "self_hash_policy",
        "target",
        "artifacts",
        "resource_plan_sha256",
        "fingerprint_array_sha256",
        "run009_evidence_sha256",
        "awg_image",
    }:
        raise PackageVerificationError("package manifest has unknown/missing fields")
    if manifest.get("self_hash_policy") != "manifest-excluded":
        raise PackageVerificationError("manifest self hash must be excluded")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise PackageVerificationError("manifest artifacts must be a non-empty array")
    seen: set[str] = set()
    kinds: set[str] = set()
    validated: list[dict[str, Any]] = []
    for entry in artifacts:
        if not isinstance(entry, dict) or set(entry) != {"path", "kind", "size", "sha256"}:
            raise PackageVerificationError("invalid artifact entry")
        path = _safe_relative_path(entry["path"], "artifact").as_posix()
        if path == MANIFEST_NAME:
            raise PackageVerificationError("manifest self hash entry is forbidden")
        if path in seen:
            raise PackageVerificationError(f"duplicate artifact path: {path}")
        seen.add(path)
        kind = entry["kind"]
        if not isinstance(kind, str) or kind not in REQUIRED_KINDS:
            raise PackageVerificationError("unknown artifact kind")
        size = entry["size"]
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise PackageVerificationError("invalid artifact size")
        _validate_digest(entry["sha256"], f"artifact {path}")
        kinds.add(kind)
        validated.append(entry)
    missing = REQUIRED_KINDS - kinds
    if missing:
        raise PackageVerificationError(
            "missing required artifact kind(s): " + ", ".join(sorted(missing))
        )
    kind_counts: dict[str, int] = {}
    for entry in validated:
        kind_counts[entry["kind"]] = kind_counts.get(entry["kind"], 0) + 1
    ambiguous = sorted(
        kind for kind, count in kind_counts.items() if count != 1 and kind not in MULTIPLE_ALLOWED_KINDS
    )
    if ambiguous:
        raise PackageVerificationError(
            "exactly one artifact is required for kind(s): " + ", ".join(ambiguous)
        )
    wheel_basenames = [
        PurePosixPath(entry["path"]).name
        for entry in validated
        if entry["kind"] == "python_wheel"
    ]
    if len(wheel_basenames) != len(set(wheel_basenames)):
        raise PackageVerificationError("duplicate wheel basename")
    _validate_artifact_path_contract(validated)
    target = manifest.get("target")
    if target != {"architecture": "x86_64", "python_major_minor": "3.12"}:
        raise PackageVerificationError("package target must be Linux x86_64 Python 3.12")
    for key in (
        "resource_plan_sha256",
        "fingerprint_array_sha256",
        "run009_evidence_sha256",
    ):
        _validate_digest(manifest.get(key), key)
    if manifest["run009_evidence_sha256"] != RUN009_EVIDENCE_SHA256:
        raise PackageVerificationError("manifest run009 evidence hash is not authoritative")
    if manifest["fingerprint_array_sha256"] != RUN009_FINGERPRINT_SHA256:
        raise PackageVerificationError("manifest fingerprint hash is not authoritative")
    image = manifest.get("awg_image")
    if not isinstance(image, dict) or set(image) != {
        "reference",
        "index_digest",
        "platform_digest",
        "config_digest",
    }:
        raise PackageVerificationError("missing AWG image binding")
    reference = image.get("reference")
    if (
        not isinstance(reference, str)
        or "@sha256:" not in reference
        or reference.endswith(":latest")
        or DIGEST_RE.fullmatch("sha256:" + reference.rsplit("@sha256:", 1)[1]) is None
    ):
        raise PackageVerificationError("AWG image must use an exact digest reference")
    for key in ("index_digest", "platform_digest", "config_digest"):
        if not isinstance(image.get(key), str) or DIGEST_RE.fullmatch(image[key]) is None:
            raise PackageVerificationError(f"invalid AWG image {key}")
    return validated


def _verify_wheel_inventory(files: dict[str, bytes], artifacts: list[dict[str, Any]]) -> None:
    inventory_entries = [e for e in artifacts if e["kind"] == "wheelhouse_inventory"]
    if len(inventory_entries) != 1:
        raise PackageVerificationError("exactly one wheelhouse inventory is required")
    inventory = _load_json_exact(files[inventory_entries[0]["path"]], "wheelhouse inventory")
    if not isinstance(inventory, dict) or set(inventory) != {"schema", "target", "wheels"} or inventory.get("schema") != WHEELHOUSE_SCHEMA:
        raise PackageVerificationError("unsupported wheelhouse inventory schema")
    if inventory.get("target") != {
        "architecture": "x86_64",
        "python_major_minor": "3.12",
    }:
        raise PackageVerificationError("wheelhouse target must be x86_64 Python 3.12")
    expected: dict[str, tuple[str, int]] = {}
    archive_total = 0
    for entry in artifacts:
        if entry["kind"] != "python_wheel":
            continue
        basename = PurePosixPath(entry["path"]).name
        if basename in expected:
            raise PackageVerificationError("duplicate wheel basename in package allowlist")
        expected[basename] = (entry["sha256"], entry["size"])
        archive_total += entry["size"]
    if archive_total > MAX_WHEEL_ARCHIVE_BYTES:
        raise PackageVerificationError("wheel archive aggregate budget exceeded")
    listed: dict[str, tuple[str, int]] = {}
    semantic_rows: dict[tuple[str, str], tuple[str, str]] = {}
    for row in inventory.get("wheels", []):
        if not isinstance(row, dict) or set(row) != {"filename", "sha256", "size"}:
            raise PackageVerificationError("invalid wheel inventory row")
        filename = _safe_relative_path(row["filename"], "wheel filename").as_posix()
        if "/" in filename or not filename.endswith(".whl"):
            raise PackageVerificationError("wheel inventory requires plain .whl filenames")
        _validate_digest(row["sha256"], f"wheel {filename}")
        if not isinstance(row["size"], int) or isinstance(row["size"], bool) or row["size"] < 0:
            raise PackageVerificationError("invalid wheel size")
        if filename in listed:
            raise PackageVerificationError("duplicate wheel inventory filename")
        listed[filename] = (row["sha256"], row["size"])
        wheel_stem = filename[:-4]
        parts = wheel_stem.split("-")
        if len(parts) < 5:
            raise PackageVerificationError("invalid wheel tag layout")
        distribution, version = parts[0], parts[1]
        normalized_name = re.sub(r"[-_.]+", "_", distribution).lower()
        identity = (normalized_name, version)
        if identity in semantic_rows:
            raise PackageVerificationError("duplicate wheel inventory distribution/version")
        semantic_rows[identity] = (filename, row["sha256"])
        python_tag, abi_tag, platform_tag = parts[-3:]
        python_tags = set(python_tag.split("."))
        if not python_tags or not python_tags <= {"py2", "py3", "cp312", "cp311"}:
            raise PackageVerificationError("wheel Python tag is incompatible")
        if "cp311" in python_tags and abi_tag != "abi3":
            raise PackageVerificationError("wheel abi tag is incompatible")
        if "cp312" in python_tags and abi_tag not in {"cp312", "abi3"}:
            raise PackageVerificationError("wheel abi tag is incompatible")
        if python_tags <= {"py2", "py3"} and abi_tag != "none":
            raise PackageVerificationError("wheel pure-Python abi tag is incompatible")
        platform_tags = set(platform_tag.split("."))
        if platform_tags != {"any"} and any(
            "x86_64" not in tag or not ("manylinux" in tag or tag.startswith("linux_"))
            for tag in platform_tags
        ):
            raise PackageVerificationError("wheel platform tag is incompatible")
    if listed != expected:
        raise PackageVerificationError("wheel inventory does not match package wheel allowlist")
    lock_entries = [entry for entry in artifacts if entry["kind"] == "wheel_lock"]
    if len(lock_entries) != 1:
        raise PackageVerificationError("exactly one wheel lock is required")
    try:
        lock_text = files[lock_entries[0]["path"]].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PackageVerificationError("wheel lock is not UTF-8") from exc
    locked: dict[tuple[str, str], str] = {}
    lock_pattern = re.compile(
        r"^([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+!-]+) --hash=sha256:([0-9a-f]{64})$"
    )
    for line in lock_text.splitlines():
        if not line or line.startswith("#"):
            continue
        match = lock_pattern.fullmatch(line)
        if match is None:
            raise PackageVerificationError("wheel lock line is invalid")
        identity = (re.sub(r"[-_.]+", "_", match.group(1)).lower(), match.group(2))
        if identity in locked:
            raise PackageVerificationError("wheel lock contains duplicate distribution/version")
        locked[identity] = match.group(3)
    expected_locked = {identity: sha for identity, (_filename, sha) in semantic_rows.items()}
    if locked != expected_locked:
        raise PackageVerificationError("wheel lock does not match wheel inventory")
    artifact_by_basename = {
        PurePosixPath(entry["path"]).name: entry["path"]
        for entry in artifacts
        if entry["kind"] == "python_wheel"
    }
    uncompressed_total = 0
    for identity, (filename, _sha) in semantic_rows.items():
        body = files[artifact_by_basename[filename]]
        try:
            with zipfile.ZipFile(io.BytesIO(body), "r") as wheel:
                metadata_rows = []
                member_names: set[str] = set()
                for info in wheel.infolist():
                    member_name = info.filename[:-1] if info.is_dir() and info.filename.endswith("/") else info.filename
                    member = _safe_relative_path(member_name, "wheel member")
                    if member.as_posix() in member_names:
                        raise PackageVerificationError("wheel contains duplicate member")
                    member_names.add(member.as_posix())
                    mode = _wheel_member_mode(info)
                    if info.is_dir():
                        if mode and not stat.S_ISDIR(mode):
                            raise PackageVerificationError("wheel directory mode mismatch")
                        continue
                    if info.file_size > MAX_WHEEL_MEMBER_BYTES:
                        raise PackageVerificationError("wheel member budget exceeded")
                    uncompressed_total += info.file_size
                    if uncompressed_total > MAX_WHEEL_UNCOMPRESSED_BYTES:
                        raise PackageVerificationError(
                            "wheel uncompressed aggregate budget exceeded"
                        )
                    if info.file_size and (
                        info.compress_size <= 0
                        or info.file_size
                        > info.compress_size * MAX_WHEEL_COMPRESSION_RATIO
                    ):
                        raise PackageVerificationError("wheel compression ratio budget exceeded")
                    if _wheel_mode_has_forbidden_type(mode):
                        raise PackageVerificationError("wheel contains non-regular member")
                    if any(part.endswith(".data") for part in member.parts):
                        raise PackageVerificationError("unsupported wheel .data layout")
                    if (
                        len(member.parts) == 2
                        and member.name == "METADATA"
                        and member.parent.name.endswith(".dist-info")
                    ):
                        metadata_rows.append(wheel.read(info).decode("utf-8"))
                if len(metadata_rows) != 1:
                    raise PackageVerificationError("wheel METADATA count mismatch")
        except (zipfile.BadZipFile, UnicodeDecodeError) as exc:
            raise PackageVerificationError("invalid wheel archive/metadata") from exc
        metadata_name = metadata_version = None
        for line in metadata_rows[0].splitlines():
            if line.startswith("Name: "):
                metadata_name = re.sub(r"[-_.]+", "_", line[6:]).lower()
            elif line.startswith("Version: "):
                metadata_version = line[9:]
        if (metadata_name, metadata_version) != identity:
            raise PackageVerificationError("wheel METADATA name/version mismatch")


def _validate_source_runtime(stream) -> dict[str, object]:
    try:
        with tarfile.open(fileobj=stream, mode="r:*") as source:
            members = source.getmembers()
            by_name: dict[str, tarfile.TarInfo] = {}
            directory_names: set[str] = set()
            for member in members:
                name = _safe_relative_path(member.name, "source runtime member").as_posix()
                if name in by_name:
                    raise PackageVerificationError("duplicate source runtime member")
                if member.isdir():
                    directory_names.add(name)
                elif not member.isfile() or member.issym() or member.islnk():
                    raise PackageVerificationError("source runtime contains forbidden member type")
                by_name[name] = member
            metadata_member = by_name.get("SOURCE-METADATA.json")
            if metadata_member is None:
                pax_commit = source.pax_headers.get("comment")
                if (
                    not isinstance(pax_commit, str)
                    or re.fullmatch(r"[0-9a-f]{40}", pax_commit) is None
                ):
                    raise PackageVerificationError(
                        "raw source runtime pax commit missing or invalid"
                    )
                forbidden_parts = {
                    ".git",
                    ".github",
                    ".pytest_cache",
                    "__pycache__",
                    "private-artifacts",
                }
                inventory: list[dict[str, object]] = []
                for name, member in by_name.items():
                    path = PurePosixPath(name)
                    if name != "source" and not name.startswith("source/"):
                        raise PackageVerificationError("source runtime root allowlist mismatch")
                    if forbidden_parts.intersection(path.parts):
                        raise PackageVerificationError("source runtime contains forbidden private/build path")
                    if member.isdir():
                        continue
                    lowered = path.name.casefold()
                    if lowered in {".env", "id_rsa", "id_ed25519"} or lowered.endswith(
                        (".pem", ".key", ".p12", ".pfx")
                    ):
                        raise PackageVerificationError("source runtime contains forbidden secret-shaped file")
                    body = source.extractfile(member)
                    if body is None:
                        raise PackageVerificationError("source runtime member is unreadable")
                    digest = hashlib.sha256()
                    while chunk := body.read(1024 * 1024):
                        digest.update(chunk)
                    inventory.append(
                        {"path": name, "sha256": digest.hexdigest(), "size": member.size}
                    )
                if not inventory or "source" not in directory_names:
                    raise PackageVerificationError("source runtime official layout is incomplete")
                inventory.sort(key=lambda row: row["path"])
                return {
                    "commit": pax_commit,
                    "tree_sha256": sha256_canonical(inventory),
                    "member_count": len(members),
                    "directory_count": len(directory_names),
                }
            if metadata_member.size > MAX_MANIFEST_BYTES or directory_names:
                raise PackageVerificationError("source runtime metadata is oversized/ambiguous")
            metadata_stream = source.extractfile(metadata_member)
            if metadata_stream is None:
                raise PackageVerificationError("source runtime metadata is unreadable")
            metadata_raw = metadata_stream.read(MAX_MANIFEST_BYTES + 1)
            metadata = _load_json_exact(metadata_raw, "source runtime metadata")
            if canonical_json_bytes(metadata) != metadata_raw:
                raise PackageVerificationError("source runtime metadata is not canonical")
            if not isinstance(metadata, dict) or set(metadata) != {
                "schema",
                "commit",
                "tree_sha256",
                "files",
            }:
                raise PackageVerificationError("source runtime metadata has unknown/missing fields")
            if metadata["schema"] != "amn2.source-runtime.v1":
                raise PackageVerificationError("unsupported source runtime schema")
            if not isinstance(metadata["commit"], str) or re.fullmatch(r"[0-9a-f]{40}", metadata["commit"]) is None:
                raise PackageVerificationError("invalid source runtime commit")
            _validate_digest(metadata["tree_sha256"], "source runtime tree")
            inventory = metadata["files"]
            if not isinstance(inventory, list) or not inventory:
                raise PackageVerificationError("source runtime inventory is empty")
            expected_names = {"SOURCE-METADATA.json"}
            seen: set[str] = set()
            for row in inventory:
                if not isinstance(row, dict) or set(row) != {"path", "sha256", "size"}:
                    raise PackageVerificationError("invalid source runtime inventory row")
                name = _safe_relative_path(row["path"], "source runtime inventory").as_posix()
                if not name.startswith("source/") or name in seen:
                    raise PackageVerificationError("invalid/duplicate source runtime inventory path")
                seen.add(name)
                expected_names.add(name)
                _validate_digest(row["sha256"], f"source runtime {name}")
                if not isinstance(row["size"], int) or isinstance(row["size"], bool) or row["size"] < 0:
                    raise PackageVerificationError("invalid source runtime inventory size")
                member = by_name.get(name)
                if member is None or member.size != row["size"]:
                    raise PackageVerificationError("source runtime inventory size/member mismatch")
                body = source.extractfile(member)
                if body is None:
                    raise PackageVerificationError("source runtime member is unreadable")
                digest = hashlib.sha256()
                while chunk := body.read(1024 * 1024):
                    digest.update(chunk)
                if digest.hexdigest() != row["sha256"]:
                    raise PackageVerificationError("source runtime member hash mismatch")
            if set(by_name) != expected_names:
                raise PackageVerificationError("source runtime member allowlist mismatch")
            if sha256_canonical(inventory) != metadata["tree_sha256"]:
                raise PackageVerificationError("source runtime tree digest mismatch")
            return {
                "commit": metadata["commit"],
                "tree_sha256": metadata["tree_sha256"],
                "member_count": len(members),
            }
    except (tarfile.TarError, OSError) as exc:
        raise PackageVerificationError("invalid source runtime archive") from exc


DOCKER_BINARY_NAMES = frozenset(
    {
        "containerd",
        "containerd-shim-runc-v2",
        "ctr",
        "docker",
        "docker-init",
        "docker-proxy",
        "dockerd",
        "runc",
    }
)


def _validate_docker_bundle(stream) -> dict[str, object]:
    try:
        with tarfile.open(fileobj=stream, mode="r:*") as bundle:
            members = bundle.getmembers()
            by_name: dict[str, tarfile.TarInfo] = {}
            directory_names: set[str] = set()
            for member in members:
                name = _safe_relative_path(member.name, "Docker bundle member").as_posix()
                if name in by_name or member.issym() or member.islnk():
                    raise PackageVerificationError("Docker bundle contains duplicate/non-regular member")
                if member.isdir():
                    directory_names.add(name)
                elif not member.isfile():
                    raise PackageVerificationError("Docker bundle contains forbidden member type")
                by_name[name] = member
            metadata_member = by_name.get("DOCKER-BUNDLE.json")
            if metadata_member is None:
                if directory_names != {"docker"} or set(by_name) != {
                    "docker",
                    *(f"docker/{name}" for name in DOCKER_BINARY_NAMES),
                }:
                    raise PackageVerificationError("Docker bundle exact official file allowlist mismatch")
                inventory: list[dict[str, object]] = []
                for binary_name in sorted(DOCKER_BINARY_NAMES):
                    path = f"docker/{binary_name}"
                    member = by_name[path]
                    if not member.isfile() or stat.S_IMODE(member.mode) & 0o111 == 0:
                        raise PackageVerificationError("Docker bundle binary mode/type mismatch")
                    binary_stream = bundle.extractfile(member)
                    if binary_stream is None:
                        raise PackageVerificationError("Docker bundle binary unreadable")
                    digest = hashlib.sha256()
                    header = binary_stream.read(20)
                    digest.update(header)
                    if header[:7] != b"\x7fELF\x02\x01\x01" or header[18:20] != b"\x3e\x00":
                        raise PackageVerificationError("Docker bundle binary is not ELF x86_64")
                    while chunk := binary_stream.read(1024 * 1024):
                        digest.update(chunk)
                    inventory.append(
                        {
                            "path": path,
                            "sha256": digest.hexdigest(),
                            "size": member.size,
                            "mode": f"{stat.S_IMODE(member.mode):04o}",
                        }
                    )
                return {
                    "inventory_sha256": sha256_canonical(inventory),
                    "binary_count": len(inventory),
                }
            if metadata_member.size > MAX_MANIFEST_BYTES or directory_names:
                raise PackageVerificationError("Docker bundle metadata is oversized/ambiguous")
            metadata_stream = bundle.extractfile(metadata_member)
            if metadata_stream is None:
                raise PackageVerificationError("Docker bundle metadata is unreadable")
            metadata_raw = metadata_stream.read(MAX_MANIFEST_BYTES + 1)
            metadata = _load_json_exact(metadata_raw, "Docker bundle metadata")
            if canonical_json_bytes(metadata) != metadata_raw or not isinstance(metadata, dict) or set(metadata) != {
                "schema",
                "architecture",
                "version",
                "source_url",
                "inventory_sha256",
                "files",
            }:
                raise PackageVerificationError("Docker bundle metadata unknown/missing fields")
            if metadata["schema"] != "amn2.docker-static-bundle.v1" or metadata["architecture"] != "x86_64":
                raise PackageVerificationError("Docker bundle target mismatch")
            if not isinstance(metadata["version"], str) or not metadata["version"]:
                raise PackageVerificationError("Docker bundle version is invalid")
            if not isinstance(metadata["source_url"], str) or not metadata["source_url"].startswith("https://download.docker.com/"):
                raise PackageVerificationError("Docker bundle provenance URL is invalid")
            _validate_digest(metadata["inventory_sha256"], "Docker bundle inventory")
            inventory = metadata["files"]
            if not isinstance(inventory, list) or len(inventory) != len(DOCKER_BINARY_NAMES):
                raise PackageVerificationError("Docker bundle file inventory count mismatch")
            expected_names = {"DOCKER-BUNDLE.json"}
            observed_binary_names: set[str] = set()
            for row in inventory:
                if not isinstance(row, dict) or set(row) != {"path", "sha256", "size", "mode"}:
                    raise PackageVerificationError("invalid Docker bundle inventory row")
                path = _safe_relative_path(row["path"], "Docker bundle inventory").as_posix()
                if not path.startswith("docker/") or "/" in path[len("docker/"):]:
                    raise PackageVerificationError("invalid Docker bundle binary path")
                binary_name = PurePosixPath(path).name
                if binary_name not in DOCKER_BINARY_NAMES or binary_name in observed_binary_names:
                    raise PackageVerificationError("Docker bundle binary allowlist mismatch")
                observed_binary_names.add(binary_name)
                expected_names.add(path)
                if row["mode"] != "0755":
                    raise PackageVerificationError("Docker bundle binary mode mismatch")
                _validate_digest(row["sha256"], f"Docker bundle {path}")
                if not isinstance(row["size"], int) or row["size"] < 20:
                    raise PackageVerificationError("Docker bundle binary size invalid")
                member = by_name.get(path)
                if member is None or member.size != row["size"] or stat.S_IMODE(member.mode) != 0o755:
                    raise PackageVerificationError("Docker bundle member binding mismatch")
                binary_stream = bundle.extractfile(member)
                if binary_stream is None:
                    raise PackageVerificationError("Docker bundle binary unreadable")
                digest = hashlib.sha256()
                header = binary_stream.read(20)
                digest.update(header)
                if header[:7] != b"\x7fELF\x02\x01\x01" or header[18:20] != b"\x3e\x00":
                    raise PackageVerificationError("Docker bundle binary is not ELF x86_64")
                while chunk := binary_stream.read(1024 * 1024):
                    digest.update(chunk)
                if digest.hexdigest() != row["sha256"]:
                    raise PackageVerificationError("Docker bundle binary hash mismatch")
            if observed_binary_names != DOCKER_BINARY_NAMES or set(by_name) != expected_names:
                raise PackageVerificationError("Docker bundle exact file allowlist mismatch")
            if sha256_canonical(inventory) != metadata["inventory_sha256"]:
                raise PackageVerificationError("Docker bundle inventory digest mismatch")
            return {
                "version": metadata["version"],
                "source_url": metadata["source_url"],
                "inventory_sha256": metadata["inventory_sha256"],
            }
    except (tarfile.TarError, OSError) as exc:
        raise PackageVerificationError("invalid Docker bundle archive") from exc


def _validate_awg_image(stream, expected: dict[str, str]) -> dict[str, str]:
    try:
        with tarfile.open(fileobj=stream, mode="r:*") as image:
            by_name: dict[str, tarfile.TarInfo] = {}
            for member in image.getmembers():
                name = _safe_relative_path(member.name, "AWG image member").as_posix()
                if name in by_name or not member.isfile() or member.issym() or member.islnk():
                    raise PackageVerificationError("AWG image contains duplicate/non-regular member")
                by_name[name] = member

            def read_small(name: str, label: str) -> bytes:
                member = by_name.get(name)
                if member is None or member.size > MAX_MANIFEST_BYTES:
                    raise PackageVerificationError(f"AWG image {label} missing/oversized")
                source = image.extractfile(member)
                if source is None:
                    raise PackageVerificationError(f"AWG image {label} unreadable")
                return source.read(MAX_MANIFEST_BYTES + 1)

            docker_manifest_raw = read_small("manifest.json", "docker manifest")
            docker_manifest = _load_json_exact(docker_manifest_raw, "AWG docker manifest")
            if not isinstance(docker_manifest, list) or len(docker_manifest) != 1:
                raise PackageVerificationError("AWG image docker manifest is ambiguous")
            docker_row = docker_manifest[0]
            if not isinstance(docker_row, dict) or set(docker_row) != {"Config", "RepoTags", "Layers"}:
                raise PackageVerificationError("AWG image docker manifest fields invalid")
            repo_tags = docker_row["RepoTags"]
            if repo_tags is not None and (
                not isinstance(repo_tags, list)
                or any(not isinstance(tag, str) or not tag for tag in repo_tags)
            ):
                raise PackageVerificationError("AWG image RepoTags informational field invalid")
            if not isinstance(docker_row["Layers"], list) or not docker_row["Layers"]:
                raise PackageVerificationError("AWG image docker manifest tags/layers invalid")

            if "AMN2-AWG-BINDING.json" not in by_name:
                config_name = expected["config_digest"].removeprefix("sha256:") + ".json"
                if docker_row["Config"] != config_name:
                    raise PackageVerificationError("AWG image docker config filename mismatch")
                config_raw = read_small(config_name, "config")
                if "sha256:" + hashlib.sha256(config_raw).hexdigest() != expected["config_digest"]:
                    raise PackageVerificationError("AWG image config digest mismatch")
                config = _load_json_exact(config_raw, "AWG image config")
                if not isinstance(config, dict) or config.get("architecture") != "amd64" or config.get("os") != "linux":
                    raise PackageVerificationError("AWG image config target mismatch")
                rootfs = config.get("rootfs")
                if not isinstance(rootfs, dict) or rootfs.get("type") != "layers" or not isinstance(rootfs.get("diff_ids"), list):
                    raise PackageVerificationError("AWG image rootfs diff_ids invalid")
                if len(rootfs["diff_ids"]) != len(docker_row["Layers"]):
                    raise PackageVerificationError("AWG image layer count mismatch")
                expected_names = {"manifest.json", "repositories", config_name}
                observed_diff_ids: list[str] = []
                previous_layer_id: str | None = None
                for layer_name in docker_row["Layers"]:
                    layer_path = _safe_relative_path(layer_name, "AWG image layer").as_posix()
                    match = re.fullmatch(r"([0-9a-f]{64})/layer\.tar", layer_path)
                    if match is None:
                        raise PackageVerificationError("AWG image layer path invalid")
                    layer_id = match.group(1)
                    layer_member = by_name.get(layer_path)
                    if layer_member is None:
                        raise PackageVerificationError("AWG image layer missing")
                    layer_stream = image.extractfile(layer_member)
                    if layer_stream is None:
                        raise PackageVerificationError("AWG image layer unreadable")
                    digest = hashlib.sha256()
                    while chunk := layer_stream.read(1024 * 1024):
                        digest.update(chunk)
                    observed_diff_ids.append("sha256:" + digest.hexdigest())
                    layer_metadata_name = f"{layer_id}/json"
                    version_name = f"{layer_id}/VERSION"
                    layer_metadata = _load_json_exact(
                        read_small(layer_metadata_name, "layer metadata"),
                        "AWG layer metadata",
                    )
                    if not isinstance(layer_metadata, dict) or layer_metadata.get("id") != layer_id:
                        raise PackageVerificationError("AWG image layer id mismatch")
                    if previous_layer_id is None:
                        if "parent" in layer_metadata:
                            raise PackageVerificationError("AWG image first layer has parent")
                    elif layer_metadata.get("parent") != previous_layer_id:
                        raise PackageVerificationError("AWG image layer parent chain mismatch")
                    if read_small(version_name, "layer VERSION") != b"1.0":
                        raise PackageVerificationError("AWG image layer VERSION mismatch")
                    previous_layer_id = layer_id
                    expected_names.update({layer_path, layer_metadata_name, version_name})
                    layer_stream = image.extractfile(layer_member)
                    if layer_stream is None:
                        raise PackageVerificationError("AWG image layer unreadable")
                    _validate_awg_layer_stream(layer_stream)
                repositories = _load_json_exact(read_small("repositories", "repositories"), "AWG repositories")
                if not isinstance(repositories, dict):
                    raise PackageVerificationError("AWG image repositories invalid")
                if rootfs["diff_ids"] != observed_diff_ids:
                    raise PackageVerificationError("AWG image diff_ids mismatch")
                if set(by_name) != expected_names:
                    raise PackageVerificationError("AWG image member allowlist mismatch")
                return {
                    "reference": expected["reference"],
                    "index_digest": expected["index_digest"],
                    "platform_digest": expected["platform_digest"],
                    "config_digest": expected["config_digest"],
                    "diff_ids": observed_diff_ids,
                    "repo_tags": repo_tags,
                }

            binding_raw = read_small("AMN2-AWG-BINDING.json", "binding")
            binding = _load_json_exact(binding_raw, "AWG image binding")
            if canonical_json_bytes(binding) != binding_raw or not isinstance(binding, dict) or set(binding) != {
                "schema",
                "reference",
                "index_digest",
                "platform_digest",
                "config_digest",
                "index",
                "platform_manifest",
            }:
                raise PackageVerificationError("AWG image binding unknown/missing fields")
            if binding["schema"] != "amn2.awg-docker-save-binding.v1":
                raise PackageVerificationError("AWG image binding schema mismatch")
            for key in ("reference", "index_digest", "platform_digest", "config_digest"):
                if binding[key] != expected[key]:
                    raise PackageVerificationError("AWG image outer/binding digest mismatch")
            if "@" + binding["index_digest"] not in binding["reference"]:
                raise PackageVerificationError("AWG image reference/index mismatch")
            if "sha256:" + hashlib.sha256(canonical_json_bytes(binding["index"])).hexdigest() != binding["index_digest"]:
                raise PackageVerificationError("AWG image index digest mismatch")
            if "sha256:" + hashlib.sha256(canonical_json_bytes(binding["platform_manifest"])).hexdigest() != binding["platform_digest"]:
                raise PackageVerificationError("AWG image platform digest mismatch")
            index = binding["index"]
            if not isinstance(index, dict) or set(index) != {"schemaVersion", "mediaType", "manifests"} or index["schemaVersion"] != 2:
                raise PackageVerificationError("AWG image index schema invalid")
            if not isinstance(index["manifests"], list) or len(index["manifests"]) != 1:
                raise PackageVerificationError("AWG image index platform count invalid")
            descriptor = index["manifests"][0]
            if not isinstance(descriptor, dict) or descriptor.get("digest") != binding["platform_digest"] or descriptor.get("platform") != {"architecture": "amd64", "os": "linux"}:
                raise PackageVerificationError("AWG image index platform binding invalid")
            platform = binding["platform_manifest"]
            if not isinstance(platform, dict) or set(platform) != {"schemaVersion", "mediaType", "config", "layers"} or platform["schemaVersion"] != 2:
                raise PackageVerificationError("AWG image platform manifest invalid")
            config_descriptor = platform["config"]
            layer_descriptors = platform["layers"]
            if not isinstance(config_descriptor, dict) or config_descriptor.get("digest") != binding["config_digest"]:
                raise PackageVerificationError("AWG image config descriptor mismatch")
            config_name = binding["config_digest"].removeprefix("sha256:") + ".json"
            if docker_row["Config"] != config_name:
                raise PackageVerificationError("AWG image docker config filename mismatch")
            config_raw = read_small(config_name, "config")
            if "sha256:" + hashlib.sha256(config_raw).hexdigest() != binding["config_digest"] or config_descriptor.get("size") != len(config_raw):
                raise PackageVerificationError("AWG image config digest/size mismatch")
            config = _load_json_exact(config_raw, "AWG image config")
            if not isinstance(config, dict) or config.get("architecture") != "amd64" or config.get("os") != "linux":
                raise PackageVerificationError("AWG image config target mismatch")
            rootfs = config.get("rootfs")
            if not isinstance(rootfs, dict) or rootfs.get("type") != "layers" or not isinstance(rootfs.get("diff_ids"), list):
                raise PackageVerificationError("AWG image rootfs diff_ids invalid")
            if not isinstance(layer_descriptors, list) or len(layer_descriptors) != len(docker_row["Layers"]) or len(layer_descriptors) != len(rootfs["diff_ids"]):
                raise PackageVerificationError("AWG image layer count mismatch")
            expected_names = {"manifest.json", "AMN2-AWG-BINDING.json", config_name}
            observed_diff_ids: list[str] = []
            for layer_name, layer_descriptor in zip(docker_row["Layers"], layer_descriptors, strict=True):
                _safe_relative_path(layer_name, "AWG image layer")
                member = by_name.get(layer_name)
                if member is None or not isinstance(layer_descriptor, dict) or layer_descriptor.get("size") != member.size:
                    raise PackageVerificationError("AWG image layer descriptor mismatch")
                layer_stream = image.extractfile(member)
                if layer_stream is None:
                    raise PackageVerificationError("AWG image layer unreadable")
                digest = hashlib.sha256()
                while chunk := layer_stream.read(1024 * 1024):
                    digest.update(chunk)
                layer_digest = "sha256:" + digest.hexdigest()
                if layer_descriptor.get("digest") != layer_digest:
                    raise PackageVerificationError("AWG image layer digest mismatch")
                observed_diff_ids.append(layer_digest)
                expected_names.add(layer_name)
                layer_stream = image.extractfile(member)
                if layer_stream is None:
                    raise PackageVerificationError("AWG image layer unreadable")
                _validate_awg_layer_stream(layer_stream)
            if rootfs["diff_ids"] != observed_diff_ids:
                raise PackageVerificationError("AWG image diff_ids mismatch")
            if set(by_name) != expected_names:
                raise PackageVerificationError("AWG image member allowlist mismatch")
            return {
                "reference": binding["reference"],
                "index_digest": binding["index_digest"],
                "platform_digest": binding["platform_digest"],
                "config_digest": binding["config_digest"],
                "diff_ids": observed_diff_ids,
                "layer_digests": [descriptor["digest"] for descriptor in layer_descriptors],
            }
    except (tarfile.TarError, OSError) as exc:
        raise PackageVerificationError("invalid AWG image docker-save archive") from exc


def _validate_run009_baseline(evidence_raw: bytes, fingerprint_raw: bytes) -> dict[str, object]:
    if hashlib.sha256(evidence_raw).hexdigest() != RUN009_EVIDENCE_SHA256:
        raise PackageVerificationError("run009 evidence does not match authoritative hash")
    evidence = _load_json_exact(evidence_raw, "run009 evidence")
    if not isinstance(evidence, dict) or evidence.get("schema") != "amn2.spain-readonly-preflight.v1":
        raise PackageVerificationError("run009 evidence schema mismatch")
    fingerprint = evidence.get("unrelated_service_fingerprint")
    if not isinstance(fingerprint, list) or len(fingerprint) != 148:
        raise PackageVerificationError("run009 fingerprint must contain exactly 148 entries")
    exact_fields = {
        "kind",
        "name_sha256",
        "image_or_unit_sha256",
        "active_state",
        "restart_count",
        "bound_port_set",
        "unit_content_status",
        "bound_port_status",
    }
    identities: set[tuple[str, str]] = set()
    for entry in fingerprint:
        if not isinstance(entry, dict) or set(entry) != exact_fields:
            raise PackageVerificationError("run009 fingerprint entry schema mismatch")
        if entry["kind"] != "unit":
            raise PackageVerificationError("run009 fingerprint kind mismatch")
        _validate_digest(entry["name_sha256"], "run009 fingerprint name")
        _validate_digest(entry["image_or_unit_sha256"], "run009 fingerprint content")
        if not isinstance(entry["active_state"], str) or not entry["active_state"]:
            raise PackageVerificationError("run009 fingerprint active state invalid")
        if not isinstance(entry["restart_count"], int) or isinstance(entry["restart_count"], bool) or entry["restart_count"] < 0:
            raise PackageVerificationError("run009 fingerprint restart count invalid")
        ports = entry["bound_port_set"]
        if not isinstance(ports, list) or any(
            not isinstance(port, int) or isinstance(port, bool) or port < 1 or port > 65535
            for port in ports
        ) or ports != sorted(set(ports)):
            raise PackageVerificationError("run009 fingerprint bound ports invalid")
        if entry["unit_content_status"] != "exact" or not isinstance(entry["bound_port_status"], str) or not entry["bound_port_status"]:
            raise PackageVerificationError("run009 fingerprint status invalid")
        identity = (entry["kind"], entry["name_sha256"])
        if identity in identities:
            raise PackageVerificationError("run009 fingerprint entries must be unique")
        identities.add(identity)
    derived = compact_json_bytes_preserving_object_order(fingerprint)
    if hashlib.sha256(derived).hexdigest() != RUN009_FINGERPRINT_SHA256:
        raise PackageVerificationError("run009 fingerprint canonical hash mismatch")
    if fingerprint_raw != derived:
        raise PackageVerificationError("fingerprint artifact must be derived from run009 evidence")
    return {
        "run009_evidence_sha256": RUN009_EVIDENCE_SHA256,
        "fingerprint_array_sha256": RUN009_FINGERPRINT_SHA256,
        "fingerprint_entry_count": 148,
    }


def _validate_provenance(
    raw: bytes,
    artifacts: list[dict[str, Any]],
    semantic_reports: dict[str, object],
    baseline_report: dict[str, object],
) -> dict[str, object]:
    provenance = _load_json_exact(raw, "input provenance")
    expected_top = {
        "schema",
        "source",
        "docker",
        "awg_image",
        "amnezia_client_provenance",
        "python",
        "baseline",
        "builder_tool",
    }
    if not isinstance(provenance, dict) or set(provenance) != expected_top or provenance.get("schema") != "amn2.phase12.spain-input-provenance.v1":
        raise PackageVerificationError("input provenance unknown/missing fields or schema")
    by_kind = {entry["kind"]: entry for entry in artifacts if entry["kind"] != "python_wheel"}

    source = provenance["source"]
    if not isinstance(source, dict) or set(source) != {
        "repository", "commit", "archive", "archive_sha256", "archive_size", "member_count"
    }:
        raise PackageVerificationError("source provenance fields invalid")
    source_entry = by_kind["source_runtime"]
    source_report = semantic_reports["source_runtime"]
    path_commit = re.fullmatch(
        r"payload/source/amn2-runtime-source-([0-9a-f]{40})\.tar\.gz",
        source_entry["path"],
    )
    if (
        source["repository"] != "AMN2"
        or path_commit is None
        or source["commit"] != path_commit.group(1)
        or source_report.get("commit", source["commit"]) != source["commit"]
        or source["archive"] != source_entry["path"]
        or source["archive_sha256"] != source_entry["sha256"]
        or source["archive_size"] != source_entry["size"]
        or source["member_count"] != source_report["member_count"]
    ):
        raise PackageVerificationError("source provenance cross-binding mismatch")
    if source["commit"] == "55dc243b8e6c6bdb57f8301b56326e4cd4072d19" and (
        source_report["member_count"] != 165
        or source_report.get("directory_count") != 24
    ):
        raise PackageVerificationError("authoritative AMN2 source member contract mismatch")

    docker = provenance["docker"]
    if not isinstance(docker, dict) or set(docker) != {
        "version", "platform", "source_url", "archive", "archive_sha256", "archive_size"
    }:
        raise PackageVerificationError("Docker provenance fields invalid")
    docker_entry = by_kind["docker_bundle"]
    docker_report = semantic_reports["docker_bundle"]
    path_version = re.fullmatch(
        r"payload/docker/docker-([A-Za-z0-9._+-]+)-linux-x86_64\.tgz",
        docker_entry["path"],
    )
    if (
        docker["platform"] != "linux/x86_64"
        or path_version is None
        or docker["version"] != path_version.group(1)
        or docker_report.get("version", docker["version"]) != docker["version"]
        or docker_report.get("source_url", docker["source_url"]) != docker["source_url"]
        or not docker["source_url"].startswith(
            "https://download.docker.com/linux/static/stable/x86_64/"
        )
        or docker["archive"] != docker_entry["path"]
        or docker["archive_sha256"] != docker_entry["sha256"]
        or docker["archive_size"] != docker_entry["size"]
    ):
        raise PackageVerificationError("Docker provenance cross-binding mismatch")

    awg = provenance["awg_image"]
    if not isinstance(awg, dict) or set(awg) != {
        "repository", "tag_observed", "index_digest", "platform", "platform_manifest_digest",
        "config_digest", "layer_blob_digests", "diff_ids", "docker_load_archive",
        "docker_load_archive_sha256", "docker_load_archive_size"
    }:
        raise PackageVerificationError("AWG provenance fields invalid")
    awg_entry = by_kind["awg_image_archive"]
    awg_report = semantic_reports["awg_image"]
    if (
        not isinstance(awg["layer_blob_digests"], list)
        or not isinstance(awg["diff_ids"], list)
        or len(awg["layer_blob_digests"]) != len(awg["diff_ids"])
        or not awg["layer_blob_digests"]
    ):
        raise PackageVerificationError("AWG provenance layer lists invalid")
    for digest in [*awg["layer_blob_digests"], *awg["diff_ids"]]:
        if not isinstance(digest, str) or DIGEST_RE.fullmatch(digest) is None:
            raise PackageVerificationError("AWG provenance layer digest invalid")
    if (
        awg["repository"] != "index.docker.io/amneziavpn/amneziawg-go"
        or not isinstance(awg["tag_observed"], str)
        or not awg["tag_observed"]
        or awg["platform"] != "linux/amd64"
        or awg_report["reference"] not in {
            f"{awg['repository']}@{awg['index_digest']}",
            f"amneziavpn/amneziawg-go@{awg['index_digest']}",
        }
        or awg["index_digest"] != awg_report["index_digest"]
        or awg["platform_manifest_digest"] != awg_report["platform_digest"]
        or awg["config_digest"] != awg_report["config_digest"]
        or awg["docker_load_archive"] != awg_entry["path"]
        or awg["docker_load_archive_sha256"] != awg_entry["sha256"]
        or awg["docker_load_archive_size"] != awg_entry["size"]
        or awg["diff_ids"] != awg_report["diff_ids"]
        or (
            "layer_digests" in awg_report
            and awg["layer_blob_digests"] != awg_report["layer_digests"]
        )
    ):
        raise PackageVerificationError("AWG provenance cross-binding mismatch")

    client = provenance["amnezia_client_provenance"]
    if not isinstance(client, dict) or set(client) != {"repository", "commit", "files"} or client["repository"] != "https://github.com/amnezia-vpn/amnezia-client" or re.fullmatch(r"[0-9a-f]{40}", client["commit"]) is None or not isinstance(client["files"], dict) or not client["files"]:
        raise PackageVerificationError("Amnezia client provenance invalid")
    for digest in client["files"].values():
        _validate_digest(digest, "Amnezia client provenance file")

    python = provenance["python"]
    if not isinstance(python, dict) or set(python) != {
        "implementation", "version", "abi", "platform", "wheel_count", "lock_sha256", "inventory_sha256"
    }:
        raise PackageVerificationError("Python provenance fields invalid")
    wheel_entries = [entry for entry in artifacts if entry["kind"] == "python_wheel"]
    if (
        {key: python[key] for key in ("implementation", "version", "abi", "platform")}
        != {"implementation": "cp", "version": "3.12", "abi": "cp312", "platform": "manylinux2014_x86_64"}
        or python["wheel_count"] != len(wheel_entries)
        or python["lock_sha256"] != by_kind["wheel_lock"]["sha256"]
        or python["inventory_sha256"] != by_kind["wheelhouse_inventory"]["sha256"]
    ):
        raise PackageVerificationError("Python provenance cross-binding mismatch")

    baseline = provenance["baseline"]
    if not isinstance(baseline, dict) or set(baseline) != {
        "run_id", "evidence_sha256", "fingerprint_entry_count", "fingerprint_array_sha256",
        "firewall_rules_sha256", "firewall_rule_count"
    }:
        raise PackageVerificationError("baseline provenance fields invalid")
    if (
        baseline["run_id"] != "spain-fresh-20260721-009"
        or baseline["evidence_sha256"] != baseline_report["run009_evidence_sha256"]
        or baseline["fingerprint_array_sha256"] != baseline_report["fingerprint_array_sha256"]
        or baseline["fingerprint_entry_count"] != 148
        or not isinstance(baseline["firewall_rule_count"], int)
    ):
        raise PackageVerificationError("baseline provenance cross-binding mismatch")
    _validate_digest(baseline["firewall_rules_sha256"], "baseline firewall")

    builder = provenance["builder_tool"]
    if not isinstance(builder, dict) or set(builder) != {"name", "version", "release_asset", "release_asset_sha256"} or not all(isinstance(builder[key], str) and builder[key] for key in ("name", "version", "release_asset")):
        raise PackageVerificationError("builder provenance invalid")
    _validate_digest(builder["release_asset_sha256"], "builder release asset")
    return {
        "source_commit": source["commit"],
        "source_tree_sha256": source_report["tree_sha256"],
        "docker_version": docker["version"],
        "wheel_count": python["wheel_count"],
    }


def verify_package(
    archive_path: Path | None,
    *,
    _descriptor: int | None = None,
) -> dict[str, object]:
    if (_descriptor is None) == (archive_path is None):
        raise PackageVerificationError("package verification input is ambiguous")
    try:
        if _descriptor is None:
            descriptor = os.open(
                Path(archive_path),
                os.O_RDONLY
                | getattr(os, "O_BINARY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
            )
        else:
            if not isinstance(_descriptor, int) or isinstance(_descriptor, bool):
                raise PackageVerificationError("package descriptor invalid")
            descriptor = os.dup(_descriptor)
        os.lseek(descriptor, 0, os.SEEK_SET)
        with os.fdopen(descriptor, "rb") as package_source, tarfile.open(
            fileobj=package_source, mode="r:*"
        ) as archive:
            initial_stat = os.fstat(package_source.fileno())
            initial_identity = (
                initial_stat.st_dev,
                initial_stat.st_ino,
                initial_stat.st_size,
                initial_stat.st_mtime_ns,
                initial_stat.st_ctime_ns,
            )
            members = archive.getmembers()
            names: set[str] = set()
            by_name: dict[str, tarfile.TarInfo] = {}
            for member in members:
                name = _safe_relative_path(member.name, "archive member").as_posix()
                if name in names:
                    raise PackageVerificationError(f"duplicate archive member: {name}")
                names.add(name)
                if not member.isfile() or member.issym() or member.islnk():
                    raise PackageVerificationError(f"archive links/non-files are forbidden: {name}")
                by_name[name] = member
            if MANIFEST_NAME not in by_name:
                raise PackageVerificationError("missing package manifest")
            manifest_member = by_name[MANIFEST_NAME]
            if manifest_member.size > MAX_MANIFEST_BYTES:
                raise PackageVerificationError("package manifest exceeds size budget")
            manifest_stream = archive.extractfile(manifest_member)
            if manifest_stream is None:
                raise PackageVerificationError("cannot read package manifest")
            manifest_raw = manifest_stream.read(MAX_MANIFEST_BYTES + 1)
            manifest = _load_json_exact(manifest_raw, "package manifest")
            if canonical_json_bytes(manifest) != manifest_raw:
                raise PackageVerificationError("package manifest is not canonical JSON")
            artifacts = _validate_manifest(manifest)
            declared_total = sum(entry["size"] for entry in artifacts)
            if declared_total > MAX_TOTAL_UNPACKED_BYTES:
                raise PackageVerificationError("package unpacked size budget exceeded")
            expected_names = {MANIFEST_NAME, *(entry["path"] for entry in artifacts)}
            if names != expected_names:
                raise PackageVerificationError("archive member allowlist mismatch")
            buffered: dict[str, bytes] = {}
            semantic_reports: dict[str, object] = {}
            for entry in artifacts:
                member = by_name[entry["path"]]
                if member.size != entry["size"]:
                    raise PackageVerificationError(f"artifact size mismatch: {entry['path']}")
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise PackageVerificationError(f"cannot read archive member: {entry['path']}")
                digest = hashlib.sha256()
                chunks: list[bytes] | None = [] if entry["kind"] in BUFFERED_METADATA_KINDS else None
                while chunk := extracted.read(1024 * 1024):
                    digest.update(chunk)
                    if chunks is not None:
                        chunks.append(chunk)
                if digest.hexdigest() != entry["sha256"]:
                    raise PackageVerificationError(f"artifact hash mismatch: {entry['path']}")
                if chunks is not None:
                    buffered[entry["path"]] = b"".join(chunks)
                if entry["kind"] == "source_runtime":
                    semantic_stream = archive.extractfile(member)
                    if semantic_stream is None:
                        raise PackageVerificationError("source runtime is unreadable")
                    semantic_reports["source_runtime"] = _validate_source_runtime(semantic_stream)
                elif entry["kind"] == "docker_bundle":
                    semantic_stream = archive.extractfile(member)
                    if semantic_stream is None:
                        raise PackageVerificationError("Docker bundle is unreadable")
                    semantic_reports["docker_bundle"] = _validate_docker_bundle(semantic_stream)
                elif entry["kind"] == "awg_image_archive":
                    semantic_stream = archive.extractfile(member)
                    if semantic_stream is None:
                        raise PackageVerificationError("AWG image is unreadable")
                    semantic_reports["awg_image"] = _validate_awg_image(
                        semantic_stream, manifest["awg_image"]
                    )
            package_source.seek(0)
            archive_digest_builder = hashlib.sha256()
            while chunk := package_source.read(1024 * 1024):
                archive_digest_builder.update(chunk)
            final_stat = os.fstat(package_source.fileno())
            final_identity = (
                final_stat.st_dev,
                final_stat.st_ino,
                final_stat.st_size,
                final_stat.st_mtime_ns,
                final_stat.st_ctime_ns,
            )
            if final_identity != initial_identity:
                raise PackageVerificationError("package descriptor changed during verification")
            archive_digest_hex = archive_digest_builder.hexdigest()
    except (tarfile.TarError, OSError) as exc:
        raise PackageVerificationError("invalid package archive") from exc
    by_kind = {entry["kind"]: entry for entry in artifacts}
    resource_plan = _load_json_exact(buffered[by_kind["resource_plan"]["path"]], "resource plan")
    if sha256_canonical(resource_plan) != manifest["resource_plan_sha256"]:
        raise PackageVerificationError("resource plan hash mismatch")
    fingerprint = buffered[by_kind["fingerprint_array"]["path"]]
    evidence = buffered[by_kind["baseline_evidence"]["path"]]
    baseline_report = _validate_run009_baseline(evidence, fingerprint)
    _verify_wheel_inventory(buffered, artifacts)
    provenance_report = _validate_provenance(
        buffered[by_kind["provenance"]["path"]],
        artifacts,
        semantic_reports,
        baseline_report,
    )
    return {
        "schema": "amn2.spain-package-verification.v1",
        "result": "passed",
        "archive_sha256": archive_digest_hex,
        "archive_size": final_stat.st_size,
        "manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "resource_plan_sha256": manifest["resource_plan_sha256"],
        "run009_evidence_sha256": baseline_report["run009_evidence_sha256"],
        "fingerprint_array_sha256": baseline_report["fingerprint_array_sha256"],
        "fingerprint_entry_count": baseline_report["fingerprint_entry_count"],
    }


def verify_package_fd(descriptor: int) -> dict[str, object]:
    if not isinstance(descriptor, int) or isinstance(descriptor, bool):
        raise PackageVerificationError("package descriptor invalid")
    try:
        before = os.fstat(descriptor)
    except OSError as exc:
        raise PackageVerificationError("package descriptor invalid") from exc
    if not stat.S_ISREG(before.st_mode):
        raise PackageVerificationError("package descriptor must be regular file")
    identity = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    report = verify_package(None, _descriptor=descriptor)
    try:
        after = os.fstat(descriptor)
    except OSError as exc:
        raise PackageVerificationError("package descriptor changed during verification") from exc
    if (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    ) != identity:
        raise PackageVerificationError("package descriptor changed during verification")
    return report


def plan_verified_package_extraction_fd(descriptor: int) -> dict[str, object]:
    """Hash the exact regular-member extraction inventory before any write."""
    report = verify_package_fd(descriptor)
    duplicate = -1
    try:
        duplicate = os.dup(descriptor)
        os.lseek(duplicate, 0, os.SEEK_SET)
        inventory: dict[str, dict[str, object]] = {}
        with os.fdopen(duplicate, "rb") as package_source, tarfile.open(
            fileobj=package_source, mode="r:*"
        ) as archive:
            duplicate = -1
            for member in archive.getmembers():
                name = _safe_relative_path(member.name, "archive member").as_posix()
                if (
                    name in inventory
                    or not member.isfile()
                    or member.issym()
                    or member.islnk()
                ):
                    raise PackageVerificationError(
                        "package extraction member allowlist invalid"
                    )
                source = archive.extractfile(member)
                if source is None:
                    raise PackageVerificationError(
                        "package extraction member unreadable"
                    )
                digest = hashlib.sha256()
                size = 0
                while chunk := source.read(1024 * 1024):
                    size += len(chunk)
                    if size > member.size:
                        raise PackageVerificationError(
                            "package extraction member size drift"
                        )
                    digest.update(chunk)
                if size != member.size:
                    raise PackageVerificationError(
                        "package extraction member size drift"
                    )
                inventory[name] = {
                    "sha256": digest.hexdigest(),
                    "size": size,
                    "mode": "0644",
                }
        if not inventory:
            raise PackageVerificationError("package extraction inventory empty")
        return {"report": report, "inventory": inventory}
    except (OSError, tarfile.TarError) as exc:
        raise PackageVerificationError("package extraction planning failed") from exc
    finally:
        if duplicate >= 0:
            os.close(duplicate)


def extract_verified_package_fd(
    descriptor: int,
    target_dir: Path,
    *,
    expected_uid: int | None = 0,
    expected_gid: int | None = 0,
    expected_inventory: Mapping[str, Mapping[str, object]] | None = None,
) -> dict[str, object]:
    if not isinstance(descriptor, int) or isinstance(descriptor, bool):
        raise PackageVerificationError("package descriptor invalid")
    for value in (expected_uid, expected_gid):
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 0
        ):
            raise PackageVerificationError("package extraction owner invalid")
    target = Path(target_dir)
    if (
        not target.is_absolute()
        or target.parent.is_symlink()
        or not target.parent.is_dir()
        or target.exists()
        or target.is_symlink()
    ):
        raise PackageVerificationError("package extraction target collision")
    plan = plan_verified_package_extraction_fd(descriptor)
    report = plan["report"]
    planned_inventory = plan["inventory"]
    if expected_inventory is not None and expected_inventory != planned_inventory:
        raise PackageVerificationError("package extraction planned inventory mismatch")
    created = False
    try:
        target.mkdir(mode=0o700)
        created = True
        if os.name != "nt" and (expected_uid is not None or expected_gid is not None):
            os.chown(
                target,
                -1 if expected_uid is None else expected_uid,
                -1 if expected_gid is None else expected_gid,
                follow_symlinks=False,
            )
        duplicate = os.dup(descriptor)
        os.lseek(duplicate, 0, os.SEEK_SET)
        inventory: dict[str, dict[str, object]] = {}
        try:
            with os.fdopen(duplicate, "rb") as package_source, tarfile.open(
                fileobj=package_source, mode="r:*"
            ) as archive:
                duplicate = -1
                members = archive.getmembers()
                names: set[str] = set()
                for member in members:
                    name = _safe_relative_path(
                        member.name, "archive member"
                    ).as_posix()
                    if (
                        name in names
                        or not member.isfile()
                        or member.issym()
                        or member.islnk()
                    ):
                        raise PackageVerificationError(
                            "package extraction member allowlist invalid"
                        )
                    names.add(name)
                    relative = PurePosixPath(name)
                    destination = target.joinpath(*relative.parts)
                    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
                    cursor = target
                    for part in relative.parts[:-1]:
                        cursor = cursor / part
                        if cursor.is_symlink() or not cursor.is_dir():
                            raise PackageVerificationError(
                                "package extraction ancestor invalid"
                            )
                    source = archive.extractfile(member)
                    if source is None:
                        raise PackageVerificationError(
                            "package extraction member unreadable"
                        )
                    output = os.open(
                        destination,
                        os.O_WRONLY
                        | os.O_CREAT
                        | os.O_EXCL
                        | getattr(os, "O_NOFOLLOW", 0)
                        | getattr(os, "O_BINARY", 0),
                        0o644,
                    )
                    digest = hashlib.sha256()
                    size = 0
                    try:
                        while chunk := source.read(1024 * 1024):
                            size += len(chunk)
                            if size > member.size:
                                raise PackageVerificationError(
                                    "package extraction member size drift"
                                )
                            digest.update(chunk)
                            offset = 0
                            while offset < len(chunk):
                                written = os.write(output, chunk[offset:])
                                if written <= 0:
                                    raise PackageVerificationError(
                                        "short package extraction write"
                                    )
                                offset += written
                        if size != member.size:
                            raise PackageVerificationError(
                                "package extraction member size drift"
                            )
                        if os.name != "nt":
                            os.fchmod(output, 0o644)
                        if os.name != "nt" and (
                            expected_uid is not None or expected_gid is not None
                        ):
                            os.fchown(
                                output,
                                -1 if expected_uid is None else expected_uid,
                                -1 if expected_gid is None else expected_gid,
                            )
                        os.fsync(output)
                    finally:
                        os.close(output)
                    inventory[name] = {
                        "sha256": digest.hexdigest(),
                        "size": size,
                        "mode": "0644",
                    }
        finally:
            if duplicate >= 0:
                os.close(duplicate)
        if set(inventory) != names:
            raise PackageVerificationError("package extraction inventory mismatch")
        if inventory != planned_inventory:
            raise PackageVerificationError("package extraction inventory drift")
        if os.name != "nt":
            target_fd = os.open(target, os.O_RDONLY)
            try:
                os.fsync(target_fd)
            finally:
                os.close(target_fd)
            parent_fd = os.open(target.parent, os.O_RDONLY)
            try:
                os.fsync(parent_fd)
            finally:
                os.close(parent_fd)
        return {"report": report, "inventory": inventory}
    except PackageVerificationError:
        if created:
            shutil.rmtree(target, ignore_errors=False)
        raise
    except (OSError, tarfile.TarError) as exc:
        if created:
            shutil.rmtree(target, ignore_errors=False)
        raise PackageVerificationError("package extraction failed") from exc


def _wheel_member_mode(info: zipfile.ZipInfo) -> int:
    return (info.external_attr >> 16) & 0xFFFF if info.create_system == 3 else 0


def _wheel_mode_has_forbidden_type(mode: int) -> bool:
    file_type = stat.S_IFMT(mode)
    return file_type not in {0, stat.S_IFREG, stat.S_IFDIR}


def _read_nofollow_bytes(path: Path) -> bytes:
    descriptor = os.open(
        path,
        os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        initial = os.fstat(descriptor)
        identity = (initial.st_dev, initial.st_ino, initial.st_size, initial.st_mtime_ns, initial.st_ctime_ns)
        chunks = []
        while chunk := os.read(descriptor, 1024 * 1024):
            chunks.append(chunk)
        final = os.fstat(descriptor)
        if (final.st_dev, final.st_ino, final.st_size, final.st_mtime_ns, final.st_ctime_ns) != identity:
            raise PackageVerificationError(f"file changed while reading: {path.name}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def expand_verified_wheelhouse(
    wheelhouse_dir: Path,
    inventory_path: Path,
    target_dir: Path,
    *,
    python_major_minor: str,
) -> dict[str, object]:
    if python_major_minor != "3.12":
        raise PackageVerificationError("wheelhouse requires Python 3.12")
    wheelhouse_dir = Path(wheelhouse_dir)
    target_dir = Path(target_dir)
    inventory_raw = _read_nofollow_bytes(Path(inventory_path))
    inventory = _load_json_exact(inventory_raw, "wheelhouse inventory")
    if not isinstance(inventory, dict) or inventory.get("schema") != WHEELHOUSE_SCHEMA:
        raise PackageVerificationError("unsupported wheelhouse inventory schema")
    if inventory.get("target") != {
        "architecture": "x86_64",
        "python_major_minor": "3.12",
    }:
        raise PackageVerificationError("wheelhouse target must be x86_64 Python 3.12")
    rows = inventory.get("wheels")
    if not isinstance(rows, list) or not rows:
        raise PackageVerificationError("wheelhouse inventory is empty")
    listed_names = {
        row.get("filename")
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("filename"), str)
    }
    all_file_names = {path.name for path in wheelhouse_dir.iterdir() if path.is_file()}
    actual_names = {name for name in all_file_names if name.endswith(".whl")}
    allowed_metadata = {
        "requirements-linux-x86_64-py312.lock",
        "wheelhouse-inventory.json",
    }
    if actual_names != listed_names or all_file_names - actual_names - allowed_metadata:
        raise PackageVerificationError("wheelhouse file allowlist mismatch")
    expected_names: set[str] = set()
    verified: list[tuple[str, bytes]] = []
    archive_total = 0
    uncompressed_total = 0
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"filename", "sha256", "size"}:
            raise PackageVerificationError("invalid wheel inventory row")
        filename = _safe_relative_path(row["filename"], "wheel filename").as_posix()
        if "/" in filename or not filename.endswith(".whl") or filename in expected_names:
            raise PackageVerificationError("invalid or duplicate wheel filename")
        expected_names.add(filename)
        wheel_path = wheelhouse_dir / filename
        body = _read_nofollow_bytes(wheel_path)
        archive_total += len(body)
        if archive_total > MAX_WHEEL_ARCHIVE_BYTES:
            raise PackageVerificationError("wheel archive aggregate budget exceeded")
        if len(body) != row["size"] or hashlib.sha256(body).hexdigest() != row["sha256"]:
            raise PackageVerificationError(f"wheel hash/size mismatch: {filename}")
        try:
            with zipfile.ZipFile(io.BytesIO(body), "r") as wheel:
                infos = wheel.infolist()
                member_names: set[str] = set()
                for info in infos:
                    member_name = info.filename[:-1] if info.is_dir() and info.filename.endswith("/") else info.filename
                    member = _safe_relative_path(member_name, "wheel member")
                    if member.as_posix() in member_names:
                        raise PackageVerificationError("wheel duplicates are forbidden")
                    member_names.add(member.as_posix())
                    mode = _wheel_member_mode(info)
                    if info.is_dir():
                        if mode and not stat.S_ISDIR(mode):
                            raise PackageVerificationError("wheel directory mode mismatch")
                        continue
                    if info.file_size > MAX_WHEEL_MEMBER_BYTES:
                        raise PackageVerificationError("wheel member budget exceeded")
                    uncompressed_total += info.file_size
                    if uncompressed_total > MAX_WHEEL_UNCOMPRESSED_BYTES:
                        raise PackageVerificationError(
                            "wheel uncompressed aggregate budget exceeded"
                        )
                    if info.file_size and (
                        info.compress_size <= 0
                        or info.file_size
                        > info.compress_size * MAX_WHEEL_COMPRESSION_RATIO
                    ):
                        raise PackageVerificationError("wheel compression ratio budget exceeded")
                    if _wheel_mode_has_forbidden_type(mode):
                        if stat.S_ISLNK(mode):
                            raise PackageVerificationError("wheel symlink is forbidden")
                        raise PackageVerificationError("wheel non-regular member is forbidden")
                    if any(part.endswith(".data") for part in member.parts):
                        raise PackageVerificationError("unsupported wheel .data layout")
                verified.append((filename, body))
        except zipfile.BadZipFile as exc:
            raise PackageVerificationError(f"invalid wheel: {filename}") from exc
    if target_dir.exists():
        raise PackageVerificationError("site-packages target already exists")
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{target_dir.name}.", dir=target_dir.parent))
    try:
        for _filename, body in verified:
            with zipfile.ZipFile(io.BytesIO(body), "r") as wheel:
                for info in wheel.infolist():
                    member_name = info.filename[:-1] if info.is_dir() and info.filename.endswith("/") else info.filename
                    relative = _safe_relative_path(member_name, "wheel member")
                    destination = staging.joinpath(*relative.parts)
                    if info.is_dir():
                        destination.mkdir(parents=True, exist_ok=True)
                        os.chmod(destination, 0o755)
                        continue
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with wheel.open(info, "r") as source, destination.open("xb") as output:
                        shutil.copyfileobj(source, output)
                    os.chmod(destination, 0o644)
        staging.replace(target_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return {
        "schema": "amn2.spain-wheelhouse-expansion.v1",
        "result": "passed",
        "wheel_count": len(verified),
        "inventory_sha256": hashlib.sha256(inventory_raw).hexdigest(),
    }


def _canonical_tree_plan(rows: list[dict[str, object]]) -> dict[str, object]:
    ordered = sorted(rows, key=lambda row: str(row["path"]))
    return {
        "schema": "amn2.spain-expanded-tree-plan.v1",
        "rows": ordered,
        "tree_sha256": sha256_canonical(ordered),
    }


def _add_tree_parents(rows: dict[str, dict[str, object]], relative: PurePosixPath) -> None:
    for parent in reversed(relative.parents):
        if parent == PurePosixPath("."):
            continue
        rows.setdefault(
            parent.as_posix(),
            {"path": parent.as_posix(), "type": "dir", "mode": "0755", "sha256": None},
        )


def plan_verified_source_tree(
    archive_path: Path,
    *,
    expected_sha256: str,
    expected_size: int,
    expected_commit: str,
) -> dict[str, object]:
    path = Path(archive_path)
    if (
        SHA256_RE.fullmatch(expected_sha256) is None
        or not isinstance(expected_size, int)
        or expected_size <= 0
        or expected_size > MAX_TOTAL_UNPACKED_BYTES
        or re.fullmatch(r"[0-9a-f]{40}", expected_commit) is None
        or path.is_symlink()
    ):
        raise PackageVerificationError("source tree planner boundary invalid")
    info = os.lstat(path)
    if not stat.S_ISREG(info.st_mode) or info.st_size != expected_size:
        raise PackageVerificationError("source archive size/type mismatch")
    raw = _read_nofollow_bytes(path)
    if len(raw) != expected_size or hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise PackageVerificationError("source archive hash/size mismatch")
    report = _validate_source_runtime(io.BytesIO(raw))
    if report.get("commit") != expected_commit:
        raise PackageVerificationError("source archive commit mismatch")
    rows: dict[str, dict[str, object]] = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:*") as source:
        for member in source.getmembers():
            archive_name = _safe_relative_path(member.name, "source runtime member")
            if archive_name.as_posix() == "SOURCE-METADATA.json":
                continue
            if not archive_name.parts or archive_name.parts[0] != "source":
                raise PackageVerificationError("source runtime root allowlist mismatch")
            stripped = PurePosixPath(*archive_name.parts[1:])
            if stripped == PurePosixPath("."):
                continue
            name = stripped.as_posix()
            if name in rows:
                raise PackageVerificationError("source expanded path duplicate")
            _add_tree_parents(rows, stripped)
            if member.isdir():
                rows[name] = {"path": name, "type": "dir", "mode": "0755", "sha256": None}
            elif member.isfile():
                stream = source.extractfile(member)
                if stream is None:
                    raise PackageVerificationError("source member unreadable")
                rows[name] = {
                    "path": name, "type": "file", "mode": "0644",
                    "sha256": hashlib.sha256(stream.read()).hexdigest(),
                    "size": member.size,
                }
            else:
                raise PackageVerificationError("source expanded member type forbidden")
    if not rows:
        raise PackageVerificationError("source expanded tree empty")
    return _canonical_tree_plan(list(rows.values()))


def expand_verified_source_tree(
    archive_path: Path,
    target_dir: Path,
    *,
    expected_plan: dict[str, object],
    expected_sha256: str,
    expected_size: int,
    expected_commit: str,
) -> None:
    actual_plan = plan_verified_source_tree(
        archive_path,
        expected_sha256=expected_sha256,
        expected_size=expected_size,
        expected_commit=expected_commit,
    )
    if actual_plan != expected_plan or Path(target_dir).exists():
        raise PackageVerificationError("source expansion plan/target mismatch")
    raw = _read_nofollow_bytes(Path(archive_path))
    target = Path(target_dir)
    target.mkdir(mode=0o755)
    try:
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:*") as source:
            for row in expected_plan["rows"]:
                relative = PurePosixPath(str(row["path"]))
                destination = target.joinpath(*relative.parts)
                if row["type"] == "dir":
                    destination.mkdir(parents=True, exist_ok=True, mode=0o755)
                    os.chmod(destination, 0o755)
                    continue
                member = source.getmember("source/" + relative.as_posix())
                stream = source.extractfile(member)
                if stream is None:
                    raise PackageVerificationError("source member unreadable")
                destination.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
                descriptor = os.open(
                    destination,
                    os.O_WRONLY
                    | os.O_CREAT
                    | os.O_EXCL
                    | getattr(os, "O_NOFOLLOW", 0)
                    | getattr(os, "O_BINARY", 0),
                    0o644,
                )
                try:
                    payload = stream.read()
                    os.write(descriptor, payload)
                    if os.name != "nt":
                        os.fchmod(descriptor, 0o644)
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
    except Exception:
        shutil.rmtree(target, ignore_errors=True)
        raise


def plan_verified_runtime_artifacts(content_root: Path) -> dict[str, object]:
    """Re-bind every runtime input needed by a fresh-process installer."""
    root = Path(content_root)
    if root.is_symlink() or not root.is_dir():
        raise PackageVerificationError("verified package content root invalid")
    manifest_raw = _read_nofollow_bytes(root / MANIFEST_NAME)
    manifest = _load_json_exact(manifest_raw, "package manifest")
    if canonical_json_bytes(manifest) != manifest_raw:
        raise PackageVerificationError("package manifest is not canonical JSON")
    artifacts = _validate_manifest(manifest)

    def one(kind: str) -> dict[str, Any]:
        matches = [entry for entry in artifacts if entry["kind"] == kind]
        if len(matches) != 1:
            raise PackageVerificationError("runtime artifact inventory ambiguous")
        return matches[0]

    def checked(entry: dict[str, Any]) -> bytes:
        relative = _safe_relative_path(entry["path"], "runtime artifact")
        payload = _read_nofollow_bytes(root.joinpath(*relative.parts))
        if (
            len(payload) != entry["size"]
            or hashlib.sha256(payload).hexdigest() != entry["sha256"]
        ):
            raise PackageVerificationError("runtime artifact content drift")
        return payload

    source_binding = plan_verified_package_source(root)
    docker_entry = one("docker_bundle")
    awg_entry = one("awg_image_archive")
    inventory_entry = one("wheelhouse_inventory")
    lock_entry = one("wheel_lock")
    provenance_entry = one("provenance")
    for entry in (
        docker_entry,
        awg_entry,
        inventory_entry,
        lock_entry,
        provenance_entry,
    ):
        checked(entry)
    wheel_entries = [entry for entry in artifacts if entry["kind"] == "python_wheel"]
    if not wheel_entries:
        raise PackageVerificationError("runtime wheel artifact inventory empty")
    for entry in wheel_entries:
        checked(entry)

    provenance = _load_json_exact(checked(provenance_entry), "input provenance")
    if (
        not isinstance(provenance, dict)
        or provenance.get("schema") != "amn2.phase12.spain-input-provenance.v1"
        or not isinstance(provenance.get("docker"), dict)
        or not isinstance(provenance.get("awg_image"), dict)
        or not isinstance(provenance.get("python"), dict)
    ):
        raise PackageVerificationError("runtime provenance schema invalid")
    docker = provenance["docker"]
    awg = provenance["awg_image"]
    python = provenance["python"]
    awg_manifest = manifest.get("awg_image")
    wheelhouse_parent = str(PurePosixPath(inventory_entry["path"]).parent)
    if (
        docker.get("archive") != docker_entry["path"]
        or docker.get("archive_sha256") != docker_entry["sha256"]
        or docker.get("archive_size") != docker_entry["size"]
        or awg.get("docker_load_archive") != awg_entry["path"]
        or awg.get("docker_load_archive_sha256") != awg_entry["sha256"]
        or awg.get("docker_load_archive_size") != awg_entry["size"]
        or not isinstance(awg_manifest, dict)
        or awg.get("index_digest") != awg_manifest.get("index_digest")
        or awg.get("platform_manifest_digest") != awg_manifest.get("platform_digest")
        or awg.get("config_digest") != awg_manifest.get("config_digest")
        or python.get("inventory_sha256") != inventory_entry["sha256"]
        or python.get("lock_sha256") != lock_entry["sha256"]
        or str(PurePosixPath(lock_entry["path"]).parent) != wheelhouse_parent
        or any(
            str(PurePosixPath(entry["path"]).parent) != wheelhouse_parent
            for entry in wheel_entries
        )
    ):
        raise PackageVerificationError("runtime provenance cross-binding mismatch")
    reference = awg_manifest.get("reference")
    if (
        not isinstance(reference, str)
        or reference
        not in {
            f"{awg.get('repository')}@{awg.get('index_digest')}",
            f"amneziavpn/amneziawg-go@{awg.get('index_digest')}",
        }
    ):
        raise PackageVerificationError("runtime AWG reference binding invalid")
    return {
        "schema": "amn2.spain-runtime-artifact-binding.v1",
        "source": {
            "path": source_binding["archive"],
            "sha256": source_binding["archive_sha256"],
            "size": source_binding["archive_size"],
            "commit": source_binding["commit"],
        },
        "wheelhouse": {
            "path": wheelhouse_parent,
            "inventory_path": inventory_entry["path"],
            "inventory_sha256": inventory_entry["sha256"],
            "lock_path": lock_entry["path"],
            "lock_sha256": lock_entry["sha256"],
        },
        "docker": {
            "path": docker_entry["path"],
            "sha256": docker_entry["sha256"],
            "size": docker_entry["size"],
        },
        "awg_image": {
            "path": awg_entry["path"],
            "sha256": awg_entry["sha256"],
            "size": awg_entry["size"],
            "reference": reference,
            "index_digest": awg_manifest["index_digest"],
            "platform_digest": awg_manifest["platform_digest"],
            "config_digest": awg_manifest["config_digest"],
        },
    }


def plan_verified_package_source(content_root: Path) -> dict[str, object]:
    root = Path(content_root)
    if root.is_symlink() or not root.is_dir():
        raise PackageVerificationError("verified package content root invalid")
    manifest = _load_json_exact(
        _read_nofollow_bytes(root / "manifest.json"), "package manifest"
    )
    artifacts = manifest.get("artifacts") if isinstance(manifest, dict) else None
    if not isinstance(artifacts, list):
        raise PackageVerificationError("package source artifact inventory invalid")
    source_entries = [
        entry
        for entry in artifacts
        if isinstance(entry, dict) and entry.get("kind") == "source_runtime"
    ]
    provenance_entries = [
        entry
        for entry in artifacts
        if isinstance(entry, dict) and entry.get("kind") == "provenance"
    ]
    if len(source_entries) != 1 or len(provenance_entries) != 1:
        raise PackageVerificationError("package source artifact inventory invalid")
    source_entry = source_entries[0]
    provenance_entry = provenance_entries[0]
    source_relative = _safe_relative_path(
        source_entry.get("path"), "package source archive"
    )
    provenance_relative = _safe_relative_path(
        provenance_entry.get("path"), "package provenance"
    )
    provenance = _load_json_exact(
        _read_nofollow_bytes(root.joinpath(*provenance_relative.parts)),
        "input provenance",
    )
    source = provenance.get("source") if isinstance(provenance, dict) else None
    if (
        not isinstance(source, dict)
        or source.get("archive") != source_relative.as_posix()
        or source.get("archive_sha256") != source_entry.get("sha256")
        or source.get("archive_size") != source_entry.get("size")
        or not isinstance(source.get("commit"), str)
        or re.fullmatch(r"[0-9a-f]{40}", source["commit"]) is None
    ):
        raise PackageVerificationError("package source provenance binding invalid")
    archive = root.joinpath(*source_relative.parts)
    expanded_plan = plan_verified_source_tree(
        archive,
        expected_sha256=source["archive_sha256"],
        expected_size=source["archive_size"],
        expected_commit=source["commit"],
    )
    inventory = {
        row["path"]: {
            "sha256": row["sha256"],
            "size": row["size"],
            "mode": "0644",
        }
        for row in expanded_plan["rows"]
        if row["type"] == "file"
    }
    if not inventory:
        raise PackageVerificationError("package prepared source inventory empty")
    return {
        "schema": "amn2.spain-package-source-binding.v1",
        "archive": source_relative.as_posix(),
        "archive_sha256": source["archive_sha256"],
        "archive_size": source["archive_size"],
        "commit": source["commit"],
        "expanded_plan": expanded_plan,
        "inventory": inventory,
        "inventory_sha256": sha256_canonical(inventory),
    }


def expand_verified_package_source(
    content_root: Path,
    target_dir: Path,
    *,
    expected_binding: dict[str, object],
) -> dict[str, object]:
    root = Path(content_root)
    target = Path(target_dir)
    actual = plan_verified_package_source(root)
    if (
        actual != expected_binding
        or target != root.parent / "prepared-source"
        or target.is_symlink()
        or target.exists()
    ):
        raise PackageVerificationError("package source expansion binding mismatch")
    archive_relative = _safe_relative_path(actual["archive"], "package source archive")
    expand_verified_source_tree(
        root.joinpath(*archive_relative.parts),
        target,
        expected_plan=actual["expanded_plan"],
        expected_sha256=actual["archive_sha256"],
        expected_size=actual["archive_size"],
        expected_commit=actual["commit"],
    )
    return {
        "schema": "amn2.spain-prepared-source.v1",
        "result": "passed",
        "commit": actual["commit"],
        "inventory": copy.deepcopy(actual["inventory"]),
        "inventory_sha256": actual["inventory_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    print(canonical_json_bytes(verify_package(args.archive)).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
