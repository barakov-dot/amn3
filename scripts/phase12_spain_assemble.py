from __future__ import annotations

import argparse
from contextlib import ExitStack
from dataclasses import dataclass
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tarfile
from typing import BinaryIO

from scripts.phase12_spain_package import (
    RUN009_EVIDENCE_SHA256,
    RUN009_FINGERPRINT_SHA256,
    canonical_json_bytes,
    sha256_canonical,
    verify_package,
)


AWG_INDEX_DIGEST = "sha256:acef5ae84808a9568448e9d8c7a96f640a5ccc590b0f8dfbc2df9f9dc0e848c9"
AWG_PLATFORM_DIGEST = "sha256:3c78eb57ef5cb44f63aed185e79c104593c854a5ebde3e1075470301bcc77c44"
AWG_CONFIG_DIGEST = "sha256:0f21ddfb3313affe3a336693886ced918301335815e4b7db3d15b5a0a5da6afb"
AWG_REFERENCE = f"amneziavpn/amneziawg-go@{AWG_INDEX_DIGEST}"


@dataclass(frozen=True)
class ArtifactSource:
    kind: str
    path: Path | None = None
    data: bytes | None = None

    def __post_init__(self) -> None:
        if not self.kind or (self.path is None) == (self.data is None):
            raise ValueError("artifact source must contain exactly one byte source")


def _safe_archive_path(value: str) -> None:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or "\\" in value or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError("artifact path is unsafe")


def _one(directory: Path, pattern: str, context: str) -> Path:
    matches = sorted(directory.glob(pattern))
    if len(matches) != 1:
        raise ValueError(f"{context} must resolve to exactly one file")
    return matches[0]


def _path_source(kind: str, path: Path) -> ArtifactSource:
    return ArtifactSource(kind=kind, path=path)


def collect_production_artifacts(
    workspace_root: Path,
    staging_root: Path,
) -> tuple[dict[str, ArtifactSource], dict[str, object]]:
    workspace_root = Path(workspace_root).resolve()
    staging_root = Path(staging_root).resolve()
    package_root = workspace_root / "packaging" / "phase12-spain"
    source = _one(staging_root / "payload" / "source", "amn2-runtime-source-*.tar.gz", "source archive")
    docker = _one(staging_root / "payload" / "docker", "docker-*-linux-x86_64.tgz", "Docker archive")
    awg = _one(staging_root / "payload" / "awg", "amneziawg-go-*-linux-amd64.tar", "AWG archive")
    wheelhouse = staging_root / "payload" / "python" / "wheelhouse"
    wheels = sorted(wheelhouse.glob("*.whl"))
    if len(wheels) != 43:
        raise ValueError("production wheelhouse must contain exactly 43 wheels")

    artifacts: dict[str, ArtifactSource] = {
        f"payload/source/{source.name}": _path_source("source_runtime", source),
        "payload/python/wheelhouse/requirements-linux-x86_64-py312.lock": _path_source(
            "wheel_lock", staging_root / "payload" / "python" / "requirements.lock"
        ),
        "payload/python/wheelhouse/wheelhouse-inventory.json": _path_source(
            "wheelhouse_inventory", staging_root / "payload" / "python" / "wheelhouse-inventory.json"
        ),
        f"payload/docker/{docker.name}": _path_source("docker_bundle", docker),
        f"payload/awg/{awg.name}": _path_source("awg_image_archive", awg),
        "units/amn2-spain-web.service": _path_source("systemd_unit", package_root / "units" / "amn2-spain-web.service"),
        "units/amn2-spain-bot.service": _path_source("systemd_unit", package_root / "units" / "amn2-spain-bot.service"),
        "units/amn2-spain-docker.service": _path_source("systemd_unit", package_root / "units" / "amn2-spain-docker.service"),
        "units/amn2-spain-network.service": _path_source("systemd_unit", package_root / "units" / "amn2-spain-network.service"),
        "templates/runtime.env": _path_source("env_template", package_root / "templates" / "runtime.env"),
        "templates/awgsp0.conf": _path_source("server_config_template", package_root / "templates" / "awgsp0.conf"),
        "templates/servers.yml": _path_source("server_config_template", package_root / "templates" / "servers.yml"),
        "templates/docker-daemon.json": _path_source("docker_daemon_template", package_root / "templates" / "docker-daemon.json"),
        "templates/nftables.conf": _path_source("firewall_template", package_root / "templates" / "nftables.conf"),
        "templates/awg-start.sh": _path_source("runtime_script", package_root / "templates" / "awg-start.sh"),
        "scripts/phase12_spain_remote_executor.sh": _path_source(
            "installer", workspace_root / "scripts" / "vps" / "phase12_spain_remote_executor.sh"
        ),
        "scripts/phase12_spain_package.py": _path_source(
            "package_verifier", workspace_root / "scripts" / "phase12_spain_package.py"
        ),
        "scripts/phase12_spain_precondition.py": _path_source(
            "precondition", workspace_root / "scripts" / "phase12_spain_precondition.py"
        ),
        "scripts/phase12_spain_installer.py": _path_source(
            "rollback", workspace_root / "scripts" / "phase12_spain_installer.py"
        ),
        "scripts/phase12_spain_live_backend.py": _path_source(
            "live_backend", workspace_root / "scripts" / "phase12_spain_live_backend.py"
        ),
        "scripts/phase12_spain_network.py": _path_source(
            "network_manager", workspace_root / "scripts" / "phase12_spain_network.py"
        ),
        "metadata/run009-evidence.json": _path_source(
            "baseline_evidence", staging_root / "evidence" / "run009-preflight-evidence.json"
        ),
        "metadata/fingerprint-array.json": _path_source(
            "fingerprint_array", staging_root / "evidence" / "run009-fingerprint-array.json"
        ),
        "provenance/input-provenance.json": _path_source(
            "provenance", staging_root / "provenance" / "input-provenance.json"
        ),
    }
    for wheel in wheels:
        artifacts[f"payload/python/wheelhouse/{wheel.name}"] = _path_source("python_wheel", wheel)

    resource_plan = json.loads((package_root / "resource-plan.json").read_text(encoding="utf-8"))
    artifacts["metadata/resource-plan.json"] = ArtifactSource(
        "resource_plan", data=canonical_json_bytes(resource_plan)
    )
    metadata: dict[str, object] = {
        "schema": "amn2.spain-install-package.v1",
        "self_hash_policy": "manifest-excluded",
        "target": {"architecture": "x86_64", "python_major_minor": "3.12"},
        "resource_plan_sha256": sha256_canonical(resource_plan),
        "fingerprint_array_sha256": RUN009_FINGERPRINT_SHA256,
        "run009_evidence_sha256": RUN009_EVIDENCE_SHA256,
        "awg_image": {
            "reference": AWG_REFERENCE,
            "index_digest": AWG_INDEX_DIGEST,
            "platform_digest": AWG_PLATFORM_DIGEST,
            "config_digest": AWG_CONFIG_DIGEST,
        },
    }
    return artifacts, metadata


def _hash_stream(stream: BinaryIO) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
        total += len(chunk)
    return digest.hexdigest(), total


def assemble_archive(
    artifacts: dict[str, ArtifactSource],
    manifest_metadata: dict[str, object],
    output_path: Path,
) -> dict[str, object]:
    if "artifacts" in manifest_metadata:
        raise ValueError("manifest metadata must exclude artifacts")
    for name in artifacts:
        _safe_archive_path(name)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with ExitStack() as stack:
        opened: dict[str, tuple[ArtifactSource, BinaryIO | None, tuple[int, int, int, int] | None]] = {}
        entries: list[dict[str, object]] = []
        for name, source in sorted(artifacts.items()):
            if source.path is not None:
                path = Path(source.path)
                if path.is_symlink():
                    raise ValueError("artifact source must be a regular non-symlink file")
                handle = stack.enter_context(path.open("rb"))
                info = os.fstat(handle.fileno())
                if not stat.S_ISREG(info.st_mode):
                    raise ValueError("artifact source must be a regular non-symlink file")
                identity = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
                digest, size = _hash_stream(handle)
                handle.seek(0)
                opened[name] = (source, handle, identity)
            else:
                assert source.data is not None
                digest = hashlib.sha256(source.data).hexdigest()
                size = len(source.data)
                opened[name] = (source, None, None)
            entries.append({"path": name, "kind": source.kind, "size": size, "sha256": digest})

        manifest = dict(manifest_metadata)
        manifest["artifacts"] = entries
        manifest_raw = canonical_json_bytes(manifest)
        output = stack.enter_context(output_path.open("xb+"))
        with tarfile.open(fileobj=output, mode="w", format=tarfile.PAX_FORMAT) as archive:
            members: list[tuple[str, ArtifactSource, BinaryIO | None]] = [
                ("manifest.json", ArtifactSource("manifest", data=manifest_raw), None)
            ]
            members.extend((name, source, handle) for name, (source, handle, _identity) in opened.items())
            for name, source, handle in members:
                data = source.data
                info = tarfile.TarInfo(name)
                info.size = len(data) if data is not None else int(os.fstat(handle.fileno()).st_size)  # type: ignore[union-attr]
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                info.mode = 0o644
                stream = io.BytesIO(data) if data is not None else handle
                if handle is not None:
                    handle.seek(0)
                archive.addfile(info, stream)

        for name, (_source, handle, identity) in opened.items():
            if handle is None or identity is None:
                continue
            current = os.fstat(handle.fileno())
            if (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns) != identity:
                raise ValueError(f"artifact changed during assembly: {name}")
            handle.seek(0)
            digest, size = _hash_stream(handle)
            expected = next(entry for entry in entries if entry["path"] == name)
            if digest != expected["sha256"] or size != expected["size"]:
                raise ValueError(f"artifact bytes changed during assembly: {name}")

        output.flush()
        os.fsync(output.fileno())
        output.seek(0)
        archive_sha256, archive_size = _hash_stream(output)
    return {
        "schema": "amn2.spain-assembly-receipt.v1",
        "archive_sha256": archive_sha256,
        "archive_size": archive_size,
        "manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "artifact_count": len(entries),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    artifacts, metadata = collect_production_artifacts(args.workspace, args.staging)
    receipt = assemble_archive(artifacts, metadata, args.output)
    verification = verify_package(args.output)
    receipt["verification"] = verification
    print(canonical_json_bytes(receipt).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
