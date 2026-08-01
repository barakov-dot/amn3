from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase12_spain_client_display_package.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase12_spain_client_display_package", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_three_slot_inputs(tmp_path: Path) -> tuple[Path, Path, dict[str, bytes]]:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "request_id": "phase12-spain-sool-test-20260730-001",
                "server": "spain",
                "items": [
                    {"recipient_label": "SooL", "device_label": "Проектор", "platform": "unknown"},
                    {"recipient_label": "SooL", "device_label": "Телевизор", "platform": "unknown"},
                    {"recipient_label": "SooL", "device_label": "ARM-HOME", "platform": "unknown"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    configs = tmp_path / "configs"
    configs.mkdir()
    payloads = {
        "NEOBYATNAYA.NET-SooL-Proektor-d1.conf": b"opaque-test-config-one\n",
        "NEOBYATNAYA.NET-SooL-Televizor-d2.conf": b"opaque-test-config-two\n",
        "NEOBYATNAYA.NET-SooL-ARM-HOME-d3.conf": b"opaque-test-config-three\n",
    }
    for name, payload in payloads.items():
        (configs / name).write_bytes(payload)
    return manifest, configs, payloads


def test_builds_unique_archives_with_exact_inner_name_and_unchanged_bytes(tmp_path: Path) -> None:
    package = load_module()
    manifest, configs, payloads = sample_three_slot_inputs(tmp_path)

    receipt = package.build_packages(manifest, configs, tmp_path / "out")

    assert receipt["schema"] == "amn2.phase12-client-display-package-receipt.v1"
    assert len(receipt["items"]) == 3
    assert len({item["archive_filename"] for item in receipt["items"]}) == 3
    assert len({item["slot_identity"] for item in receipt["items"]}) == 3
    for item in receipt["items"]:
        with ZipFile(tmp_path / "out" / item["archive_filename"]) as archive:
            assert archive.namelist() == ["NEOBYATNAYA.NET.conf", "package-manifest.json"]
            assert archive.getinfo("NEOBYATNAYA.NET.conf").compress_type == ZIP_STORED
            assert archive.read("NEOBYATNAYA.NET.conf") == payloads[item["source_filename"]]
            metadata = json.loads(archive.read("package-manifest.json"))
            assert metadata["inner_filename"] == "NEOBYATNAYA.NET.conf"
            assert metadata["device_id"] == item["device_id"]


def test_rejects_duplicate_slot_identity(tmp_path: Path) -> None:
    package = load_module()
    manifest, configs, _payloads = sample_three_slot_inputs(tmp_path)
    value = json.loads(manifest.read_text(encoding="utf-8"))
    value["items"].append(dict(value["items"][0]))
    manifest.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(package.PackageError, match="duplicate slot identity"):
        package.build_packages(manifest, configs, tmp_path / "out")


def test_refuses_existing_output_directory(tmp_path: Path) -> None:
    package = load_module()
    manifest, configs, _payloads = sample_three_slot_inputs(tmp_path)
    output = tmp_path / "out"
    output.mkdir()

    with pytest.raises(FileExistsError):
        package.build_packages(manifest, configs, output)


def test_repeated_builds_are_byte_identical(tmp_path: Path) -> None:
    package = load_module()
    manifest, configs, _payloads = sample_three_slot_inputs(tmp_path)

    first = package.build_packages(manifest, configs, tmp_path / "one")
    second = package.build_packages(manifest, configs, tmp_path / "two")

    assert first == second
    for item in first["items"]:
        assert (tmp_path / "one" / item["archive_filename"]).read_bytes() == (
            tmp_path / "two" / item["archive_filename"]
        ).read_bytes()


def test_outer_manifest_contains_hash_not_config_material(tmp_path: Path) -> None:
    package = load_module()
    manifest, configs, payloads = sample_three_slot_inputs(tmp_path)
    receipt = package.build_packages(manifest, configs, tmp_path / "out")

    for item in receipt["items"]:
        with ZipFile(tmp_path / "out" / item["archive_filename"]) as archive:
            metadata = archive.read("package-manifest.json")
            assert item["config_sha256"].encode() in metadata
            assert payloads[item["source_filename"]] not in metadata
            assert b"PrivateKey" not in metadata
            assert b"PresharedKey" not in metadata


def test_verifier_rejects_source_config_drift(tmp_path: Path) -> None:
    package = load_module()
    manifest, configs, _payloads = sample_three_slot_inputs(tmp_path)
    receipt = package.build_packages(manifest, configs, tmp_path / "out")
    source = configs / receipt["items"][0]["source_filename"]
    source.write_bytes(source.read_bytes() + b"\n")

    with pytest.raises(package.PackageError, match="source config drift"):
        package.verify_packages(receipt, configs, tmp_path / "out")


def test_verifier_rejects_unexpected_archive_member(tmp_path: Path) -> None:
    package = load_module()
    manifest, configs, _payloads = sample_three_slot_inputs(tmp_path)
    receipt = package.build_packages(manifest, configs, tmp_path / "out")
    target = tmp_path / "out" / receipt["items"][0]["archive_filename"]
    with ZipFile(target, "a", compression=ZIP_STORED) as archive:
        archive.writestr("unexpected.txt", b"no")

    with pytest.raises(package.PackageError, match="archive member mismatch"):
        package.verify_packages(receipt, configs, tmp_path / "out")
