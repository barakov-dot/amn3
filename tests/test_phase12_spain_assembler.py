import hashlib
import io
import json
from pathlib import Path
import tarfile

import pytest

from scripts.phase12_spain_assemble import (
    ArtifactSource,
    assemble_archive,
    collect_production_artifacts,
)


ROOT = Path(__file__).resolve().parents[1]


def _metadata() -> dict[str, object]:
    return {
        "schema": "amn2.spain-install-package.v1",
        "self_hash_policy": "manifest-excluded",
        "target": {"architecture": "x86_64", "python_major_minor": "3.12"},
        "resource_plan_sha256": "1" * 64,
        "fingerprint_array_sha256": "2" * 64,
        "run009_evidence_sha256": "3" * 64,
        "awg_image": {
            "reference": "repo@sha256:" + "4" * 64,
            "index_digest": "sha256:" + "4" * 64,
            "platform_digest": "sha256:" + "5" * 64,
            "config_digest": "sha256:" + "6" * 64,
        },
    }


def test_deterministic_archive_is_byte_identical_and_manifest_excludes_self(tmp_path: Path) -> None:
    left = tmp_path / "left.bin"
    right = tmp_path / "right.bin"
    left.write_bytes(b"left")
    right.write_bytes(b"right")
    artifacts = {
        "z/right.bin": ArtifactSource("runtime_script", right),
        "a/left.bin": ArtifactSource("env_template", left),
    }
    first = tmp_path / "first.tar"
    second = tmp_path / "second.tar"
    one = assemble_archive(artifacts, _metadata(), first)
    two = assemble_archive(dict(reversed(list(artifacts.items()))), _metadata(), second)
    assert first.read_bytes() == second.read_bytes()
    assert one == two
    assert one["archive_sha256"] == hashlib.sha256(first.read_bytes()).hexdigest()
    with tarfile.open(first, "r:") as archive:
        members = archive.getmembers()
        assert [member.name for member in members] == ["manifest.json", "a/left.bin", "z/right.bin"]
        assert all(member.uid == 0 and member.gid == 0 and member.mtime == 0 for member in members)
        manifest = json.load(archive.extractfile("manifest.json"))
    assert [entry["path"] for entry in manifest["artifacts"]] == ["a/left.bin", "z/right.bin"]
    assert all(entry["path"] != "manifest.json" for entry in manifest["artifacts"])


def test_assembler_refuses_unsafe_paths_symlinks_and_overwrite(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.write_bytes(b"x")
    with pytest.raises(ValueError, match="artifact path"):
        assemble_archive({"../escape": ArtifactSource("env_template", source)}, _metadata(), tmp_path / "bad.tar")
    link = tmp_path / "link"
    try:
        link.symlink_to(source)
    except OSError:
        pytest.skip("symlink creation unavailable")
    with pytest.raises(ValueError, match="regular non-symlink"):
        assemble_archive({"safe": ArtifactSource("env_template", link)}, _metadata(), tmp_path / "link.tar")
    output = tmp_path / "existing.tar"
    output.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        assemble_archive({"safe": ArtifactSource("env_template", source)}, _metadata(), output)
    assert output.read_bytes() == b"keep"


def test_production_collection_maps_exact_reviewed_inputs_when_available() -> None:
    staging = ROOT / "private-artifacts" / "phase12-spain-install-package-inputs-20260721"
    if not staging.is_dir():
        pytest.skip("private Phase 12 staging unavailable")
    artifacts, metadata = collect_production_artifacts(ROOT, staging)
    assert sum(item.kind == "python_wheel" for item in artifacts.values()) == 43
    for required in (
        "units/amn2-spain-network.service",
        "templates/nftables.conf",
        "templates/docker-daemon.json",
        "templates/awg-start.sh",
        "templates/servers.yml",
        "scripts/phase12_spain_live_backend.py",
        "scripts/phase12_spain_network.py",
        "scripts/phase12_spain_package.py",
        "scripts/phase12_spain_precondition.py",
        "metadata/resource-plan.json",
        "metadata/run009-evidence.json",
        "metadata/fingerprint-array.json",
        "provenance/input-provenance.json",
    ):
        assert required in artifacts
    assert metadata["resource_plan_sha256"]
