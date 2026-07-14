#!/usr/bin/env python
"""Validate the exact AMN2 AWG Docker runtime and an offline image archive."""

from __future__ import annotations

import gzip
import hashlib
import io
import ipaddress
import json
import re
import tarfile
from pathlib import PurePosixPath
from typing import Mapping


RUNTIME_SCHEMA = "amn2-awg-runtime-v1"
IMAGE_REFERENCE = "amnezia-awg2:local"
MAX_IMAGE_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_IMAGE_ARCHIVE_FILES = 512
MAX_SOURCE_ARCHIVE_BYTES = 32 * 1024 * 1024
MAX_SOURCE_ARCHIVE_DECOMPRESSED_BYTES = 24 * 1024 * 1024
MAX_SOURCE_ARCHIVE_FILES = 4096
EXPECTED_CAPABILITIES = ["CAP_NET_ADMIN", "CAP_SYS_MODULE"]
EXPECTED_ENVIRONMENT_KEYS = {
    "AWG_SUBNET_IP",
    "PATH",
    "WIREGUARD_SUBNET_CIDR",
}


class RuntimeContractError(RuntimeError):
    """A safe runtime-contract failure that contains no captured values."""


def _canonical_json(value: Mapping[str, object]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def _require_image_id(value: object) -> str:
    image_id = str(value or "")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", image_id):
        raise RuntimeContractError("container image ID is invalid")
    return image_id


def _parse_environment(values: object) -> dict[str, str]:
    if not isinstance(values, list):
        raise RuntimeContractError("container environment is invalid")
    environment: dict[str, str] = {}
    for item in values:
        if not isinstance(item, str) or "=" not in item:
            raise RuntimeContractError("container environment is invalid")
        key, value = item.split("=", 1)
        if key in environment or key not in EXPECTED_ENVIRONMENT_KEYS:
            raise RuntimeContractError("container environment is not allowlisted")
        environment[key] = value
    if set(environment) != EXPECTED_ENVIRONMENT_KEYS or not environment["PATH"]:
        raise RuntimeContractError("container environment contract is incomplete")
    return environment


def _validate_safe_environment(environment: object) -> dict[str, str]:
    if not isinstance(environment, dict) or set(environment) != {
        "AWG_SUBNET_IP",
        "WIREGUARD_SUBNET_CIDR",
    }:
        raise RuntimeContractError("runtime environment contract is invalid")
    subnet_ip = environment.get("AWG_SUBNET_IP")
    cidr = environment.get("WIREGUARD_SUBNET_CIDR")
    if not isinstance(subnet_ip, str) or not isinstance(cidr, str):
        raise RuntimeContractError("runtime environment values are invalid")
    try:
        ipaddress.IPv4Address(subnet_ip)
        cidr_number = int(cidr)
    except ValueError as exc:
        raise RuntimeContractError("runtime environment values are invalid") from exc
    if str(cidr_number) != cidr or not 1 <= cidr_number <= 32:
        raise RuntimeContractError("runtime environment values are invalid")
    return {"AWG_SUBNET_IP": subnet_ip, "WIREGUARD_SUBNET_CIDR": cidr}


def normalize_runtime_contract(inspect_bytes: bytes, expected_image_id: str) -> bytes:
    """Convert Docker inspect JSON into the only approved AMN2 AWG profile."""

    image_id = _require_image_id(expected_image_id)
    try:
        rows = json.loads(inspect_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeContractError("Docker inspect response is invalid") from exc
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
        raise RuntimeContractError("Docker inspect response is invalid")
    row = rows[0]
    if _require_image_id(row.get("Image")) != image_id:
        raise RuntimeContractError("Docker inspect image ID changed")
    config = row.get("Config")
    host = row.get("HostConfig")
    mounts = row.get("Mounts")
    if not isinstance(config, dict) or not isinstance(host, dict) or not isinstance(mounts, list):
        raise RuntimeContractError("Docker inspect contract is incomplete")

    environment = _parse_environment(config.get("Env"))
    if config.get("Image") != IMAGE_REFERENCE:
        raise RuntimeContractError("container image reference is unsupported")
    if config.get("Entrypoint") != ["dumb-init", "/opt/amnezia/start.sh"]:
        raise RuntimeContractError("container entrypoint is unsupported")
    if config.get("Cmd") != [""]:
        raise RuntimeContractError("container command is unsupported")
    if host.get("NetworkMode") != "bridge":
        raise RuntimeContractError("container network mode is unsupported")
    restart = host.get("RestartPolicy")
    if not isinstance(restart, dict) or restart.get("Name") != "unless-stopped" or int(
        restart.get("MaximumRetryCount") or 0
    ) != 0:
        raise RuntimeContractError("container restart policy is unsupported")
    if host.get("Privileged") is not True:
        raise RuntimeContractError("container privileged contract changed")
    if sorted(host.get("CapAdd") or []) != EXPECTED_CAPABILITIES:
        raise RuntimeContractError("container capability contract changed")
    if host.get("CapDrop") not in (None, []):
        raise RuntimeContractError("container capability drop contract changed")
    if host.get("Devices") not in (None, []):
        raise RuntimeContractError("container device contract changed")
    expected_ports = {"30001/udp": [{"HostIp": "", "HostPort": "30001"}]}
    if host.get("PortBindings") != expected_ports:
        raise RuntimeContractError("container port binding contract changed")
    if host.get("PublishAllPorts") not in (None, False):
        raise RuntimeContractError("container port publication contract changed")
    if host.get("Sysctls") != {"net.ipv4.conf.all.src_valid_mark": "1"}:
        raise RuntimeContractError("container sysctl contract changed")
    if host.get("SecurityOpt") != ["label=disable"]:
        raise RuntimeContractError("container security option contract changed")
    if host.get("ReadonlyRootfs") is not False:
        raise RuntimeContractError("container root filesystem contract changed")
    expected_mounts = [
        {
            "Type": "bind",
            "Source": "/lib/modules",
            "Destination": "/lib/modules",
            "RW": False,
        }
    ]
    relevant_mounts = [
        {
            "Type": item.get("Type"),
            "Source": item.get("Source"),
            "Destination": item.get("Destination"),
            "RW": item.get("RW"),
        }
        for item in mounts
        if isinstance(item, dict)
    ]
    if len(relevant_mounts) != len(mounts) or relevant_mounts != expected_mounts:
        raise RuntimeContractError("container mount contract changed")

    contract: dict[str, object] = {
        "schema": RUNTIME_SCHEMA,
        "image_id": image_id,
        "image_reference": IMAGE_REFERENCE,
        "network_mode": "bridge",
        "restart_policy": {"name": "unless-stopped", "maximum_retry_count": 0},
        "privileged": True,
        "cap_add": EXPECTED_CAPABILITIES,
        "port_bindings": {
            "30001/udp": [{"host_ip": "", "host_port": "30001"}]
        },
        "mounts": [
            {
                "type": "bind",
                "source": "/lib/modules",
                "target": "/lib/modules",
                "read_only": True,
            }
        ],
        "sysctls": {"net.ipv4.conf.all.src_valid_mark": "1"},
        "security_opt": ["label=disable"],
        "readonly_rootfs": False,
        "entrypoint": ["dumb-init", "/opt/amnezia/start.sh"],
        "cmd": [""],
        "environment": {
            "AWG_SUBNET_IP": environment["AWG_SUBNET_IP"],
            "WIREGUARD_SUBNET_CIDR": environment["WIREGUARD_SUBNET_CIDR"],
        },
    }
    validate_runtime_contract(_canonical_json(contract))
    return _canonical_json(contract)


def validate_runtime_contract(value: bytes) -> dict[str, object]:
    try:
        contract = json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeContractError("runtime contract JSON is invalid") from exc
    if not isinstance(contract, dict):
        raise RuntimeContractError("runtime contract JSON is invalid")
    expected_keys = {
        "schema",
        "image_id",
        "image_reference",
        "network_mode",
        "restart_policy",
        "privileged",
        "cap_add",
        "port_bindings",
        "mounts",
        "sysctls",
        "security_opt",
        "readonly_rootfs",
        "entrypoint",
        "cmd",
        "environment",
    }
    if set(contract) != expected_keys:
        raise RuntimeContractError("runtime contract keys are invalid")
    image_id = _require_image_id(contract.get("image_id"))
    fixed = {
        "schema": RUNTIME_SCHEMA,
        "image_reference": IMAGE_REFERENCE,
        "network_mode": "bridge",
        "restart_policy": {"maximum_retry_count": 0, "name": "unless-stopped"},
        "privileged": True,
        "cap_add": EXPECTED_CAPABILITIES,
        "port_bindings": {
            "30001/udp": [{"host_ip": "", "host_port": "30001"}]
        },
        "mounts": [
            {
                "read_only": True,
                "source": "/lib/modules",
                "target": "/lib/modules",
                "type": "bind",
            }
        ],
        "sysctls": {"net.ipv4.conf.all.src_valid_mark": "1"},
        "security_opt": ["label=disable"],
        "readonly_rootfs": False,
        "entrypoint": ["dumb-init", "/opt/amnezia/start.sh"],
        "cmd": [""],
    }
    for key, expected in fixed.items():
        if contract.get(key) != expected:
            raise RuntimeContractError("runtime contract value is unsupported")
    environment = _validate_safe_environment(contract.get("environment"))
    normalized = dict(contract)
    normalized["image_id"] = image_id
    normalized["environment"] = environment
    if value != _canonical_json(normalized):
        raise RuntimeContractError("runtime contract JSON is not canonical")
    return normalized


def _normalize_archive_name(value: str) -> str:
    normalized = value.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    path = PurePosixPath(normalized)
    if not normalized or path.is_absolute() or ".." in path.parts:
        raise RuntimeContractError("image archive contains an unsafe path")
    return path.as_posix()


def validate_image_archive(
    archive_bytes: bytes, expected_image_id: str, expected_reference: str
) -> dict[str, object]:
    image_id = _require_image_id(expected_image_id)
    if expected_reference != IMAGE_REFERENCE:
        raise RuntimeContractError("image archive reference is unsupported")
    if len(archive_bytes) > MAX_IMAGE_ARCHIVE_BYTES:
        raise RuntimeContractError("image archive size limit exceeded")
    try:
        archive = tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:")
    except tarfile.TarError as exc:
        raise RuntimeContractError("image archive is not a Docker tar") from exc
    files: dict[str, bytes] = {}
    total = 0
    with archive:
        members = archive.getmembers()
        if len(members) > MAX_IMAGE_ARCHIVE_FILES:
            raise RuntimeContractError("image archive member limit exceeded")
        for member in members:
            name = _normalize_archive_name(member.name)
            if member.isdir():
                continue
            if not member.isfile() or name in files:
                raise RuntimeContractError("image archive member contract is invalid")
            total += member.size
            if total > MAX_IMAGE_ARCHIVE_BYTES:
                raise RuntimeContractError("image archive expanded-size limit exceeded")
            source = archive.extractfile(member)
            if source is None:
                raise RuntimeContractError("image archive member cannot be read")
            files[name] = source.read()
    try:
        manifest = json.loads(files["manifest.json"])
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeContractError("image archive manifest is invalid") from exc
    if not isinstance(manifest, list) or len(manifest) != 1 or not isinstance(manifest[0], dict):
        raise RuntimeContractError("image archive manifest is invalid")
    row = manifest[0]
    config_name = _normalize_archive_name(str(row.get("Config") or ""))
    expected_digest = image_id.removeprefix("sha256:")
    if config_name != f"{expected_digest}.json" or config_name not in files:
        raise RuntimeContractError("image archive config digest does not match image ID")
    actual_digest = hashlib.sha256(files[config_name]).hexdigest()
    if actual_digest != expected_digest:
        raise RuntimeContractError("image archive config digest does not match image ID")
    try:
        image_config = json.loads(files[config_name])
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeContractError("image archive config JSON is invalid") from exc
    if not isinstance(image_config, dict):
        raise RuntimeContractError("image archive config JSON is invalid")
    repo_tags = row.get("RepoTags")
    if not isinstance(repo_tags, list) or expected_reference not in repo_tags:
        raise RuntimeContractError("image archive repo tag is missing")
    layers = row.get("Layers")
    if not isinstance(layers, list) or not layers:
        raise RuntimeContractError("image archive layers are missing")
    normalized_layers = [_normalize_archive_name(str(name)) for name in layers]
    if len(set(normalized_layers)) != len(normalized_layers) or any(
        name not in files for name in normalized_layers
    ):
        raise RuntimeContractError("image archive layer contract is invalid")
    rootfs = image_config.get("rootfs")
    if not isinstance(rootfs, dict) or rootfs.get("type") != "layers":
        raise RuntimeContractError("image archive rootfs contract is invalid")
    diff_ids = rootfs.get("diff_ids")
    if not isinstance(diff_ids, list) or len(diff_ids) != len(normalized_layers):
        raise RuntimeContractError("image archive layer digest contract is invalid")
    for layer_name, diff_id in zip(normalized_layers, diff_ids, strict=True):
        if not isinstance(diff_id, str) or not re.fullmatch(
            r"sha256:[0-9a-f]{64}", diff_id
        ):
            raise RuntimeContractError("image archive layer digest is invalid")
        actual_layer_digest = "sha256:" + hashlib.sha256(files[layer_name]).hexdigest()
        if actual_layer_digest != diff_id:
            raise RuntimeContractError("image archive layer digest mismatch")
    return {
        "config_digest": image_id,
        "repo_tag": expected_reference,
        "layer_count": len(normalized_layers),
        "archive_bytes": len(archive_bytes),
    }


def validate_source_archive(
    archive_bytes: bytes,
    expected_source_overlay: str,
    expected_sha256: str,
) -> dict[str, object]:
    if not re.fullmatch(r"[0-9a-f]{7,40}", expected_source_overlay):
        raise RuntimeContractError("source overlay marker is invalid")
    if len(archive_bytes) > MAX_SOURCE_ARCHIVE_BYTES:
        raise RuntimeContractError("source archive size limit exceeded")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise RuntimeContractError("source archive expected SHA-256 is invalid")
    actual_sha256 = hashlib.sha256(archive_bytes).hexdigest()
    if actual_sha256 != expected_sha256:
        raise RuntimeContractError("source archive SHA-256 mismatch")
    decompressed = io.BytesIO()
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(archive_bytes), mode="rb") as source:
            while True:
                chunk = source.read(1024 * 1024)
                if not chunk:
                    break
                if (
                    decompressed.tell() + len(chunk)
                    > MAX_SOURCE_ARCHIVE_DECOMPRESSED_BYTES
                ):
                    raise RuntimeContractError(
                        "source archive decompressed-size limit exceeded"
                    )
                decompressed.write(chunk)
        archive = tarfile.open(fileobj=io.BytesIO(decompressed.getvalue()), mode="r:")
    except RuntimeContractError:
        raise
    except (gzip.BadGzipFile, EOFError, OSError, tarfile.TarError) as exc:
        raise RuntimeContractError("source archive is not a gzip tar") from exc
    names: set[str] = set()
    total = 0
    with archive:
        member_count = 0
        while True:
            member = archive.next()
            if member is None:
                break
            member_count += 1
            if member_count > MAX_SOURCE_ARCHIVE_FILES:
                raise RuntimeContractError("source archive member limit exceeded")
            name = _normalize_archive_name(member.name)
            if member.isdir() and member.size != 0:
                raise RuntimeContractError(
                    "source archive directory member contract is invalid"
                )
            if member.isdir() and name == "source":
                continue
            if not name.startswith("source/"):
                raise RuntimeContractError("source archive top-level path is invalid")
            if member.isdir():
                continue
            if not member.isfile() or name in names:
                raise RuntimeContractError("source archive member contract is invalid")
            total += member.size
            if total > MAX_SOURCE_ARCHIVE_BYTES:
                raise RuntimeContractError("source archive expanded-size limit exceeded")
            names.add(name)
    required = {
        "source/pyproject.toml",
        "source/app/__init__.py",
        "source/app/main.py",
        "source/deploy/systemd/amneziya-web.service.example",
        "source/deploy/systemd/amneziya-bot.service.example",
    }
    if not required.issubset(names):
        raise RuntimeContractError("source archive required files are missing")
    return {
        "source_overlay": expected_source_overlay,
        "file_count": len(names),
        "expanded_bytes": total,
        "archive_bytes": len(archive_bytes),
        "sha256": actual_sha256,
        "top_level": "source",
    }
