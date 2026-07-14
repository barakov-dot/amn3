from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile

import pytest

from scripts.phase11_recovery_runtime import (
    MAX_SOURCE_ARCHIVE_DECOMPRESSED_BYTES,
    RuntimeContractError,
    normalize_runtime_contract,
    validate_image_archive,
    validate_source_archive,
)


def docker_inspect(*, extra_env: str | None = None) -> tuple[bytes, str]:
    image_id = "sha256:" + "a" * 64
    environment = [
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "AWG_SUBNET_IP=10.8.0.0",
        "WIREGUARD_SUBNET_CIDR=24",
    ]
    if extra_env is not None:
        environment.append(extra_env)
    row = {
        "Image": image_id,
        "Config": {
            "Image": "amnezia-awg2:local",
            "Env": environment,
            "Entrypoint": ["dumb-init", "/opt/amnezia/start.sh"],
            "Cmd": [""],
        },
        "HostConfig": {
            "NetworkMode": "bridge",
            "RestartPolicy": {"Name": "unless-stopped", "MaximumRetryCount": 0},
            "Privileged": True,
            "CapAdd": ["CAP_SYS_MODULE", "CAP_NET_ADMIN"],
            "CapDrop": None,
            "Devices": [],
            "PortBindings": {
                "30001/udp": [{"HostIp": "", "HostPort": "30001"}]
            },
            "Sysctls": {"net.ipv4.conf.all.src_valid_mark": "1"},
            "SecurityOpt": ["label=disable"],
            "ReadonlyRootfs": False,
        },
        "Mounts": [
            {
                "Type": "bind",
                "Source": "/lib/modules",
                "Destination": "/lib/modules",
                "RW": False,
            }
        ],
    }
    return json.dumps([row]).encode(), image_id


def docker_image_archive() -> tuple[bytes, str]:
    layer = b"synthetic-layer"
    layer_digest = hashlib.sha256(layer).hexdigest()
    config = json.dumps(
        {
            "architecture": "amd64",
            "os": "linux",
            "rootfs": {"type": "layers", "diff_ids": [f"sha256:{layer_digest}"]},
        },
        separators=(",", ":"),
    ).encode()
    digest = hashlib.sha256(config).hexdigest()
    image_id = "sha256:" + digest
    manifest = json.dumps(
        [
            {
                "Config": f"{digest}.json",
                "RepoTags": ["amnezia-awg2:local"],
                "Layers": ["layer/layer.tar"],
            }
        ],
        separators=(",", ":"),
    ).encode()
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as archive:
        for name, value in (
            ("manifest.json", manifest),
            (f"{digest}.json", config),
            ("layer/layer.tar", layer),
        ):
            info = tarfile.TarInfo(name)
            info.size = len(value)
            archive.addfile(info, io.BytesIO(value))
    return output.getvalue(), image_id


def source_archive(*, unsafe_name: str | None = None) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as archive:
        root = tarfile.TarInfo("source/")
        root.type = tarfile.DIRTYPE
        archive.addfile(root)
        entries = (
            ("source/pyproject.toml", b"[project]\nname='amn2'\n"),
            ("source/app/__init__.py", b""),
            ("source/app/main.py", b"def main(): pass\n"),
            (
                "source/deploy/systemd/amneziya-web.service.example",
                b"[Service]\nExecStart=/bin/false\n",
            ),
            (
                "source/deploy/systemd/amneziya-bot.service.example",
                b"[Service]\nExecStart=/bin/false\n",
            ),
        )
        for name, value in entries:
            info = tarfile.TarInfo(name)
            info.size = len(value)
            archive.addfile(info, io.BytesIO(value))
        if unsafe_name:
            info = tarfile.TarInfo(unsafe_name)
            info.size = 1
            archive.addfile(info, io.BytesIO(b"x"))
    return output.getvalue()


def test_normalize_runtime_contract_emits_exact_safe_profile() -> None:
    inspect_bytes, image_id = docker_inspect()

    encoded = normalize_runtime_contract(inspect_bytes, image_id)
    contract = json.loads(encoded)

    assert contract == {
        "cap_add": ["CAP_NET_ADMIN", "CAP_SYS_MODULE"],
        "cmd": [""],
        "entrypoint": ["dumb-init", "/opt/amnezia/start.sh"],
        "environment": {
            "AWG_SUBNET_IP": "10.8.0.0",
            "WIREGUARD_SUBNET_CIDR": "24",
        },
        "image_id": image_id,
        "image_reference": "amnezia-awg2:local",
        "mounts": [
            {
                "read_only": True,
                "source": "/lib/modules",
                "target": "/lib/modules",
                "type": "bind",
            }
        ],
        "network_mode": "bridge",
        "port_bindings": {
            "30001/udp": [{"host_ip": "", "host_port": "30001"}]
        },
        "privileged": True,
        "readonly_rootfs": False,
        "restart_policy": {"maximum_retry_count": 0, "name": "unless-stopped"},
        "schema": "amn2-awg-runtime-v1",
        "security_opt": ["label=disable"],
        "sysctls": {"net.ipv4.conf.all.src_valid_mark": "1"},
    }
    assert encoded.endswith(b"\n")
    assert b"PATH=" not in encoded


def test_normalize_runtime_contract_rejects_unapproved_environment() -> None:
    inspect_bytes, image_id = docker_inspect(extra_env="TOKEN=must-not-be-captured")

    with pytest.raises(RuntimeContractError, match="environment"):
        normalize_runtime_contract(inspect_bytes, image_id)


def test_validate_image_archive_binds_config_digest_and_repo_tag() -> None:
    archive, image_id = docker_image_archive()

    report = validate_image_archive(archive, image_id, "amnezia-awg2:local")

    assert report["config_digest"] == image_id
    assert report["repo_tag"] == "amnezia-awg2:local"
    assert report["layer_count"] == 1


def test_validate_image_archive_rejects_mismatched_image_id() -> None:
    archive, _image_id = docker_image_archive()

    with pytest.raises(RuntimeContractError, match="config digest"):
        validate_image_archive(
            archive, "sha256:" + "f" * 64, "amnezia-awg2:local"
        )


def test_validate_image_archive_rejects_layer_diff_id_mismatch() -> None:
    archive, image_id = docker_image_archive()
    files: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as source:
        for member in source.getmembers():
            if member.isfile():
                files[member.name] = source.extractfile(member).read()
    files["layer/layer.tar"] = b"substituted-layer"
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as destination:
        for name, value in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(value)
            destination.addfile(info, io.BytesIO(value))

    with pytest.raises(RuntimeContractError, match="layer digest"):
        validate_image_archive(output.getvalue(), image_id, "amnezia-awg2:local")


def test_validate_source_archive_requires_safe_complete_source_tree() -> None:
    archive = source_archive()
    digest = hashlib.sha256(archive).hexdigest()
    report = validate_source_archive(archive, "801f8c3", digest)

    assert report["source_overlay"] == "801f8c3"
    assert report["file_count"] == 5
    assert report["top_level"] == "source"


def test_validate_source_archive_rejects_path_traversal() -> None:
    archive = source_archive(unsafe_name="../escape")
    with pytest.raises(RuntimeContractError, match="unsafe path"):
        validate_source_archive(archive, "801f8c3", hashlib.sha256(archive).hexdigest())


def test_validate_source_archive_rejects_unapproved_digest() -> None:
    with pytest.raises(RuntimeContractError, match="SHA-256"):
        validate_source_archive(source_archive(), "801f8c3", "f" * 64)


def test_validate_source_archive_streams_member_limit_without_getmembers(
    monkeypatch,
) -> None:
    archive = source_archive()

    def fail_getmembers(_self):
        raise AssertionError("getmembers must not materialize the nested archive")

    monkeypatch.setattr(tarfile.TarFile, "getmembers", fail_getmembers)

    report = validate_source_archive(
        archive, "801f8c3", hashlib.sha256(archive).hexdigest()
    )
    assert report["file_count"] == 5


def test_validate_source_archive_rejects_excessive_gzip_expansion() -> None:
    archive = gzip.compress(b"x" * (MAX_SOURCE_ARCHIVE_DECOMPRESSED_BYTES + 1))

    with pytest.raises(RuntimeContractError, match="decompressed-size"):
        validate_source_archive(
            archive,
            "801f8c3",
            hashlib.sha256(archive).hexdigest(),
        )
