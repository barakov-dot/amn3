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


def docker_image_inspect(image_id: str, diff_ids: list[str]) -> bytes:
    return json.dumps(
        [
            {
                "Id": image_id,
                "RepoTags": ["amnezia-awg2:local"],
                "Config": docker_image_runtime_config(),
                "Architecture": "amd64",
                "Os": "linux",
                "RootFS": {"Type": "layers", "Layers": diff_ids},
            }
        ]
    ).encode()


def docker_image_runtime_config() -> dict[str, object]:
    return {
        "Cmd": [""],
        "Entrypoint": ["dumb-init", "/opt/amnezia/start.sh"],
        "Env": ["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"],
        "Labels": {"org.opencontainers.image.title": "synthetic-amn2-awg"},
        "WorkingDir": "",
    }


def docker_image_config_sha256(
    config: dict[str, object] | None = None,
) -> str:
    value = docker_image_runtime_config() if config is None else config
    encoded = (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def docker_image_archive(
    *,
    repo_tags: list[str] | None = None,
    runtime_config: dict[str, object] | None = None,
    architecture: str = "amd64",
    image_os: str = "linux",
    archive_layout: str = "legacy",
) -> tuple[bytes, str]:
    layer = b"synthetic-layer"
    layer_digest = hashlib.sha256(layer).hexdigest()
    config = json.dumps(
        {
            "architecture": architecture,
            "config": (
                docker_image_runtime_config()
                if runtime_config is None
                else runtime_config
            ),
            "os": image_os,
            "rootfs": {"type": "layers", "diff_ids": [f"sha256:{layer_digest}"]},
        },
        separators=(",", ":"),
    ).encode()
    digest = hashlib.sha256(config).hexdigest()
    image_id = "sha256:" + digest
    if archive_layout == "legacy":
        config_name = f"{digest}.json"
        layer_name = "layer/layer.tar"
    elif archive_layout == "oci":
        config_name = f"blobs/sha256/{digest}"
        layer_name = f"blobs/sha256/{layer_digest}"
    else:
        raise ValueError("unsupported synthetic image archive layout")
    manifest = json.dumps(
        [
            {
                "Config": config_name,
                "RepoTags": [] if repo_tags is None else repo_tags,
                "Layers": [layer_name],
            }
        ],
        separators=(",", ":"),
    ).encode()
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as archive:
        for name, value in (
            ("manifest.json", manifest),
            (config_name, config),
            (layer_name, layer),
        ):
            info = tarfile.TarInfo(name)
            info.size = len(value)
            archive.addfile(info, io.BytesIO(value))
    return output.getvalue(), image_id


def docker_image_diff_ids(archive_bytes: bytes) -> list[str]:
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:") as archive:
        files = {
            member.name: archive.extractfile(member).read()
            for member in archive.getmembers()
            if member.isfile()
        }
    row = json.loads(files["manifest.json"])[0]
    return json.loads(files[row["Config"]])["rootfs"]["diff_ids"]


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
    diff_ids = ["sha256:" + "b" * 64]

    encoded = normalize_runtime_contract(
        inspect_bytes, image_id, docker_image_inspect(image_id, diff_ids)
    )
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
        "image_architecture": "amd64",
        "image_config_sha256": docker_image_config_sha256(),
        "image_os": "linux",
        "image_rootfs_diff_ids": diff_ids,
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
        "schema": "amn2-awg-runtime-v2",
        "security_opt": ["label=disable"],
        "sysctls": {"net.ipv4.conf.all.src_valid_mark": "1"},
    }
    assert encoded.endswith(b"\n")
    assert b"PATH=" not in encoded


def test_normalize_runtime_contract_binds_daemon_rootfs_layers() -> None:
    inspect_bytes, image_id = docker_inspect()
    diff_ids = ["sha256:" + "b" * 64, "sha256:" + "c" * 64]

    encoded = normalize_runtime_contract(
        inspect_bytes,
        image_id,
        docker_image_inspect(image_id, diff_ids),
    )

    assert json.loads(encoded)["image_rootfs_diff_ids"] == diff_ids


def test_normalize_runtime_contract_rejects_unapproved_environment() -> None:
    inspect_bytes, image_id = docker_inspect(extra_env="TOKEN=must-not-be-captured")

    with pytest.raises(RuntimeContractError, match="environment"):
        normalize_runtime_contract(
            inspect_bytes,
            image_id,
            docker_image_inspect(image_id, ["sha256:" + "b" * 64]),
        )


def test_validate_image_archive_binds_config_digest_and_rootfs() -> None:
    archive, image_id = docker_image_archive()
    diff_ids = docker_image_diff_ids(archive)

    report = validate_image_archive(
        archive,
        image_id,
        "amnezia-awg2:local",
        diff_ids,
        docker_image_config_sha256(),
        "amd64",
        "linux",
    )

    assert report["config_digest"] == image_id
    assert report["image_reference"] == "amnezia-awg2:local"
    assert report["repo_tags"] == []
    assert report["image_config_contract"] == "passed"
    assert report["layer_count"] == 1


def test_validate_image_archive_accepts_oci_blob_config_and_layer_paths() -> None:
    archive, image_id = docker_image_archive(archive_layout="oci")

    report = validate_image_archive(
        archive,
        image_id,
        "amnezia-awg2:local",
        docker_image_diff_ids(archive),
        docker_image_config_sha256(),
        "amd64",
        "linux",
    )

    assert report["config_digest"] == image_id
    assert report["layer_count"] == 1


def test_validate_image_archive_accepts_legacy_runtime_id_via_rootfs_binding() -> None:
    archive, config_image_id = docker_image_archive(repo_tags=[])
    legacy_runtime_image_id = "sha256:" + "d" * 64

    report = validate_image_archive(
        archive,
        legacy_runtime_image_id,
        "amnezia-awg2:local",
        docker_image_diff_ids(archive),
        docker_image_config_sha256(),
        "amd64",
        "linux",
    )

    assert report["runtime_image_id"] == legacy_runtime_image_id
    assert report["config_digest"] == config_image_id
    assert report["repo_tags"] == []


def test_validate_image_archive_rejects_changed_config_with_same_rootfs() -> None:
    archive, image_id = docker_image_archive()
    files: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as source:
        for member in source.getmembers():
            if member.isfile():
                files[member.name] = source.extractfile(member).read()
    manifest = json.loads(files["manifest.json"])
    old_config_name = manifest[0]["Config"]
    image_config = json.loads(files.pop(old_config_name))
    image_config["config"] = {
        "Healthcheck": {"Test": ["CMD-SHELL", "/bin/true"]}
    }
    config_bytes = json.dumps(image_config, separators=(",", ":")).encode()
    config_name = hashlib.sha256(config_bytes).hexdigest() + ".json"
    files[config_name] = config_bytes
    manifest[0]["Config"] = config_name
    files["manifest.json"] = json.dumps(manifest, separators=(",", ":")).encode()
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as destination:
        for name, value in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(value)
            destination.addfile(info, io.BytesIO(value))

    with pytest.raises(RuntimeContractError, match="config"):
        validate_image_archive(
            output.getvalue(),
            image_id,
            "amnezia-awg2:local",
            docker_image_diff_ids(archive),
            docker_image_config_sha256(),
            "amd64",
            "linux",
        )


def test_validate_image_archive_rejects_runtime_rootfs_mismatch() -> None:
    archive, image_id = docker_image_archive()

    with pytest.raises(RuntimeContractError, match="rootfs"):
        validate_image_archive(
            archive,
            image_id,
            "amnezia-awg2:local",
            ["sha256:" + "f" * 64],
            docker_image_config_sha256(),
            "amd64",
            "linux",
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
        validate_image_archive(
            output.getvalue(),
            image_id,
            "amnezia-awg2:local",
            docker_image_diff_ids(archive),
            docker_image_config_sha256(),
            "amd64",
            "linux",
        )


def test_validate_image_archive_rejects_architecture_mismatch() -> None:
    archive, image_id = docker_image_archive(architecture="arm64")

    with pytest.raises(RuntimeContractError, match="architecture"):
        validate_image_archive(
            archive,
            image_id,
            "amnezia-awg2:local",
            docker_image_diff_ids(archive),
            docker_image_config_sha256(),
            "amd64",
            "linux",
        )


def test_validate_image_archive_rejects_os_mismatch() -> None:
    archive, image_id = docker_image_archive(image_os="windows")

    with pytest.raises(RuntimeContractError, match="OS"):
        validate_image_archive(
            archive,
            image_id,
            "amnezia-awg2:local",
            docker_image_diff_ids(archive),
            docker_image_config_sha256(),
            "amd64",
            "linux",
        )


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
