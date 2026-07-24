from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import tarfile
import types
import zipfile
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

import pytest
import scripts.phase12_spain_package as package_module
import scripts.phase12_spain_installer as installer_module
import scripts.phase12_spain_executor_bundle as executor_bundle_module
import scripts.phase12_spain_precondition as precondition_module
import scripts.phase12_spain_network as network_module
import scripts.phase12_spain_live_backend as live_backend

from scripts.phase12_spain_installer import (
    FsyncLedger,
    InstallError,
    InstallStateMachine,
    InstallAuthorization,
    InstallBoundaryIntent,
    MemoryBackend,
    PackageVerificationReport,
    ProductionPostinstallObserver,
    ProductionRecoveryCoordinator,
    ProductionBackend,
    RetainedAuthorizationStore,
    SharedInstallLockLease,
    BootstrapTransactionLedger,
    InstallActionBlueprint,
    RecoveryCapsuleStore,
    ChecksumBoundPackageStager,
    ChecksumBoundBootstrap,
    assert_firewall_projection,
    assert_systemd_projection,
    validate_rollback_equality_receipt,
    finalize_rolled_back_recovery,
    build_rollback_equality_receipt,
    build_terminal_recovery_equality_receipt,
    prepare_production_installation,
    reconstruct_production_installation,
)
from scripts.phase12_spain_package import (
    PackageVerificationError,
    canonical_json_bytes,
    expand_verified_wheelhouse,
    expand_verified_source_tree,
    extract_verified_package_fd,
    plan_verified_package_extraction_fd,
    plan_verified_package_source,
    expand_verified_package_source,
    plan_verified_source_tree,
    sha256_canonical,
    verify_package,
    verify_package_fd,
)
from scripts.phase12_spain_precondition import (
    PreconditionError,
    build_precondition_receipt,
    validate_preconditions,
    verify_precondition_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "phase12_spain"
RESOURCE_PLAN = json.loads((FIXTURES / "resource_plan.json").read_text(encoding="utf-8"))
OBSERVATION = json.loads((FIXTURES / "observation_ok.json").read_text(encoding="utf-8"))
REMOTE_EXECUTOR = ROOT / "scripts" / "vps" / "phase12_spain_remote_executor.sh"
INSTALL_SSH_RUNNER = ROOT / "scripts" / "vps" / "phase12_spain_install_ssh_runner.ps1"
SSH_DATA_PATH_DIAGNOSTIC_RUNNER = (
    ROOT / "scripts" / "vps" / "phase12_spain_ssh_data_path_diagnostic_runner.ps1"
)
CLEANUP_SSH_RUNNER = ROOT / "scripts" / "vps" / "phase12_spain_manual_cleanup_ssh_runner.ps1"
TERMINAL_RECOVERY_SSH_RUNNER = (
    ROOT / "scripts" / "vps" / "phase12_spain_terminal_recovery_ssh_runner.ps1"
)
CURRENT_MANUAL_CLEANUP_SSH_RUNNER = (
    ROOT / "scripts" / "vps" / "phase12_spain_current_manual_cleanup_ssh_runner.ps1"
)
CURRENT_TERMINAL_RECOVERY_SSH_RUNNER = (
    ROOT / "scripts" / "vps" / "phase12_spain_current_terminal_recovery_ssh_runner.ps1"
)
TRANSACTION_2F647_MANUAL_CLEANUP_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_2f647_manual_cleanup_ssh_runner.ps1"
)
TRANSACTION_2F647_TERMINAL_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_2f647_terminal_recovery_ssh_runner.ps1"
)
TRANSACTION_2315_MANUAL_CLEANUP_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_2315_manual_cleanup_ssh_runner.ps1"
)
TRANSACTION_2315_TERMINAL_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_2315_terminal_recovery_ssh_runner.ps1"
)
TRANSACTION_544DB_MANUAL_CLEANUP_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_544db_manual_cleanup_ssh_runner.ps1"
)
TRANSACTION_544DB_TERMINAL_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_544db_terminal_recovery_ssh_runner.ps1"
)
TRACKED_PACKAGE_ROOT = ROOT / "packaging" / "phase12-spain"
HOST_IDENTITY_SHA256 = "7" * 64
BOOT_ID = "12345678-1234-1234-1234-123456789abc"
COLLECTOR_SHA256 = "8" * 64
EXECUTOR_SHA256 = "9" * 64
RECEIPT_NOW = 1784581200
RECEIPT_NONCE = "a" * 64

SYNTHETIC_FINGERPRINT = [
    {
        "kind": "unit",
        "name_sha256": hashlib.sha256(f"unit-{index}".encode()).hexdigest(),
        "image_or_unit_sha256": hashlib.sha256(f"content-{index}".encode()).hexdigest(),
        "active_state": "active:running",
        "restart_count": 0,
        "bound_port_set": [] if index else [443],
        "unit_content_status": "exact",
        "bound_port_status": "cgroup_complete",
    }
    for index in range(148)
]
SYNTHETIC_FINGERPRINT_BYTES = canonical_json_bytes(SYNTHETIC_FINGERPRINT)
SYNTHETIC_EVIDENCE_BYTES = canonical_json_bytes(
    {
        "schema": "amn2.spain-readonly-preflight.v1",
        "mode": "preflight",
        "firewall": {
            "backend": "nft",
            "rules_sha256": "c" * 64,
            "rule_count": 2,
        },
        "unrelated_service_fingerprint": SYNTHETIC_FINGERPRINT,
    }
)


@pytest.fixture(autouse=True)
def synthetic_baseline_policy(monkeypatch):
    monkeypatch.setitem(
        OBSERVATION, "systemd_projection", copy.deepcopy(SYNTHETIC_FINGERPRINT)
    )
    monkeypatch.setattr(
        package_module,
        "RUN009_EVIDENCE_SHA256",
        hashlib.sha256(SYNTHETIC_EVIDENCE_BYTES).hexdigest(),
    )
    monkeypatch.setattr(
        package_module,
        "RUN009_FINGERPRINT_SHA256",
        hashlib.sha256(SYNTHETIC_FINGERPRINT_BYTES).hexdigest(),
    )
    monkeypatch.setattr(
        precondition_module,
        "RUN009_EVIDENCE_SHA256",
        hashlib.sha256(SYNTHETIC_EVIDENCE_BYTES).hexdigest(),
    )
    monkeypatch.setattr(
        precondition_module,
        "RUN009_FINGERPRINT_SHA256",
        hashlib.sha256(SYNTHETIC_FINGERPRINT_BYTES).hexdigest(),
    )
    monkeypatch.setattr(
        precondition_module,
        "FIREWALL_SEMANTIC_REBASELINE",
        {
            "backend": "nft",
            "rule_count": 2,
            "semantic_sha256": "d" * 64,
            "current_raw_sha256": "c" * 64,
        },
    )

WHEEL_BYTES_STREAM = io.BytesIO()
with zipfile.ZipFile(WHEEL_BYTES_STREAM, "w") as wheel:
    wheel.writestr("demo/__init__.py", "VALUE = 1\n")
    wheel.writestr("demo-1.0.dist-info/METADATA", "Name: demo\nVersion: 1.0\n")
WHEEL_BYTES = WHEEL_BYTES_STREAM.getvalue()
WHEEL_INVENTORY = canonical_json_bytes(
    {
        "schema": "amn2.spain-wheelhouse.v1",
        "target": {"architecture": "x86_64", "python_major_minor": "3.12"},
        "wheels": [
            {
                "filename": "demo-1.0-py3-none-any.whl",
                "sha256": hashlib.sha256(WHEEL_BYTES).hexdigest(),
                "size": len(WHEEL_BYTES),
            }
        ],
    }
)
WHEEL_LOCK = (
    "# Target: CPython 3.12 / Linux x86_64 / manylinux2014\n"
    "demo==1.0 --hash=sha256:" + hashlib.sha256(WHEEL_BYTES).hexdigest() + "\n"
).encode()

SOURCE_COMMIT = "1" * 40
SOURCE_FILE = b"print('phase12')\n"
SOURCE_INVENTORY = [
    {
        "path": "source/app.py",
        "sha256": hashlib.sha256(SOURCE_FILE).hexdigest(),
        "size": len(SOURCE_FILE),
    }
]
SOURCE_METADATA = canonical_json_bytes(
    {
        "schema": "amn2.source-runtime.v1",
        "commit": SOURCE_COMMIT,
        "tree_sha256": sha256_canonical(SOURCE_INVENTORY),
        "files": SOURCE_INVENTORY,
    }
)
SOURCE_STREAM = io.BytesIO()
with tarfile.open(fileobj=SOURCE_STREAM, mode="w") as source_tar:
    for source_name, source_body in (
        ("SOURCE-METADATA.json", SOURCE_METADATA),
        ("source/app.py", SOURCE_FILE),
    ):
        source_info = tarfile.TarInfo(source_name)
        source_info.size = len(source_body)
        source_info.mtime = 0
        source_tar.addfile(source_info, io.BytesIO(source_body))
SOURCE_ARCHIVE = SOURCE_STREAM.getvalue()

ELF_X86_64 = b"\x7fELF\x02\x01\x01" + b"\x00" * 11 + b"\x3e\x00" + b"\x00" * 46
DOCKER_BINARY_NAMES = (
    "containerd",
    "containerd-shim-runc-v2",
    "ctr",
    "docker",
    "docker-init",
    "docker-proxy",
    "dockerd",
    "runc",
)
DOCKER_INVENTORY = [
    {
        "path": f"docker/{name}",
        "sha256": hashlib.sha256(ELF_X86_64 + name.encode()).hexdigest(),
        "size": len(ELF_X86_64 + name.encode()),
        "mode": "0755",
    }
    for name in DOCKER_BINARY_NAMES
]
DOCKER_METADATA = canonical_json_bytes(
    {
        "schema": "amn2.docker-static-bundle.v1",
        "architecture": "x86_64",
        "version": "synthetic-test",
        "source_url": "https://download.docker.com/linux/static/stable/x86_64/docker-test.tgz",
        "inventory_sha256": sha256_canonical(DOCKER_INVENTORY),
        "files": DOCKER_INVENTORY,
    }
)
DOCKER_STREAM = io.BytesIO()
with tarfile.open(fileobj=DOCKER_STREAM, mode="w") as docker_tar:
    for docker_name, docker_body, docker_mode in [
        ("DOCKER-BUNDLE.json", DOCKER_METADATA, 0o644),
        *[
            (f"docker/{name}", ELF_X86_64 + name.encode(), 0o755)
            for name in DOCKER_BINARY_NAMES
        ],
    ]:
        docker_info = tarfile.TarInfo(docker_name)
        docker_info.size = len(docker_body)
        docker_info.mode = docker_mode
        docker_info.mtime = 0
        docker_tar.addfile(docker_info, io.BytesIO(docker_body))
DOCKER_ARCHIVE = DOCKER_STREAM.getvalue()

AWG_LAYER_STREAM = io.BytesIO()
with tarfile.open(fileobj=AWG_LAYER_STREAM, mode="w") as layer_tar:
    layer_body = b"synthetic awg executable\n"
    layer_info = tarfile.TarInfo("usr/bin/awg")
    layer_info.size = len(layer_body)
    layer_info.mode = 0o755
    layer_info.mtime = 0
    layer_tar.addfile(layer_info, io.BytesIO(layer_body))
AWG_LAYER = AWG_LAYER_STREAM.getvalue()
AWG_LAYER_DIGEST = "sha256:" + hashlib.sha256(AWG_LAYER).hexdigest()
AWG_CONFIG = canonical_json_bytes(
    {
        "architecture": "amd64",
        "os": "linux",
        "config": {"Entrypoint": ["/usr/bin/awg"]},
        "rootfs": {"type": "layers", "diff_ids": [AWG_LAYER_DIGEST]},
    }
)
AWG_CONFIG_DIGEST = "sha256:" + hashlib.sha256(AWG_CONFIG).hexdigest()
AWG_PLATFORM_MANIFEST = {
    "schemaVersion": 2,
    "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
    "config": {
        "mediaType": "application/vnd.docker.container.image.v1+json",
        "digest": AWG_CONFIG_DIGEST,
        "size": len(AWG_CONFIG),
    },
    "layers": [
        {
            "mediaType": "application/vnd.docker.image.rootfs.diff.tar",
            "digest": AWG_LAYER_DIGEST,
            "size": len(AWG_LAYER),
        }
    ],
}
AWG_PLATFORM_DIGEST = "sha256:" + hashlib.sha256(
    canonical_json_bytes(AWG_PLATFORM_MANIFEST)
).hexdigest()
AWG_INDEX = {
    "schemaVersion": 2,
    "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
    "manifests": [
        {
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "digest": AWG_PLATFORM_DIGEST,
            "size": len(canonical_json_bytes(AWG_PLATFORM_MANIFEST)),
            "platform": {"architecture": "amd64", "os": "linux"},
        }
    ],
}
AWG_INDEX_DIGEST = "sha256:" + hashlib.sha256(canonical_json_bytes(AWG_INDEX)).hexdigest()
AWG_REFERENCE = "amneziavpn/amneziawg-go@" + AWG_INDEX_DIGEST
AWG_BINDING = canonical_json_bytes(
    {
        "schema": "amn2.awg-docker-save-binding.v1",
        "reference": AWG_REFERENCE,
        "index_digest": AWG_INDEX_DIGEST,
        "platform_digest": AWG_PLATFORM_DIGEST,
        "config_digest": AWG_CONFIG_DIGEST,
        "index": AWG_INDEX,
        "platform_manifest": AWG_PLATFORM_MANIFEST,
    }
)
AWG_DOCKER_MANIFEST = canonical_json_bytes(
    [
        {
            "Config": AWG_CONFIG_DIGEST.removeprefix("sha256:") + ".json",
            "RepoTags": [],
            "Layers": [AWG_LAYER_DIGEST.removeprefix("sha256:") + "/layer.tar"],
        }
    ]
)
AWG_STREAM = io.BytesIO()
with tarfile.open(fileobj=AWG_STREAM, mode="w") as awg_tar:
    for awg_name, awg_body in (
        ("manifest.json", AWG_DOCKER_MANIFEST),
        ("AMN2-AWG-BINDING.json", AWG_BINDING),
        (AWG_CONFIG_DIGEST.removeprefix("sha256:") + ".json", AWG_CONFIG),
        (AWG_LAYER_DIGEST.removeprefix("sha256:") + "/layer.tar", AWG_LAYER),
    ):
        awg_info = tarfile.TarInfo(awg_name)
        awg_info.size = len(awg_body)
        awg_info.mtime = 0
        awg_tar.addfile(awg_info, io.BytesIO(awg_body))
AWG_ARCHIVE = AWG_STREAM.getvalue()
PROVENANCE = canonical_json_bytes(
    {
        "schema": "amn2.phase12.spain-input-provenance.v1",
        "source": {
            "repository": "AMN2",
            "commit": SOURCE_COMMIT,
            "archive": f"payload/source/amn2-runtime-source-{SOURCE_COMMIT}.tar.gz",
            "archive_sha256": hashlib.sha256(SOURCE_ARCHIVE).hexdigest(),
            "archive_size": len(SOURCE_ARCHIVE),
            "member_count": 2,
        },
        "docker": {
            "version": "synthetic-test",
            "platform": "linux/x86_64",
            "source_url": "https://download.docker.com/linux/static/stable/x86_64/docker-test.tgz",
            "archive": "payload/docker/docker-synthetic-test-linux-x86_64.tgz",
            "archive_sha256": hashlib.sha256(DOCKER_ARCHIVE).hexdigest(),
            "archive_size": len(DOCKER_ARCHIVE),
        },
        "awg_image": {
            "repository": "index.docker.io/amneziavpn/amneziawg-go",
            "tag_observed": "latest",
            "index_digest": AWG_INDEX_DIGEST,
            "platform": "linux/amd64",
            "platform_manifest_digest": AWG_PLATFORM_DIGEST,
            "config_digest": AWG_CONFIG_DIGEST,
            "layer_blob_digests": [AWG_LAYER_DIGEST],
            "diff_ids": [AWG_LAYER_DIGEST],
            "docker_load_archive": "payload/awg/amneziawg-go-test-linux-amd64.tar",
            "docker_load_archive_sha256": hashlib.sha256(AWG_ARCHIVE).hexdigest(),
            "docker_load_archive_size": len(AWG_ARCHIVE),
        },
        "amnezia_client_provenance": {
            "repository": "https://github.com/amnezia-vpn/amnezia-client",
            "commit": "2" * 40,
            "files": {"template.conf": "3" * 64},
        },
        "python": {
            "implementation": "cp",
            "version": "3.12",
            "abi": "cp312",
            "platform": "manylinux2014_x86_64",
            "wheel_count": 1,
            "lock_sha256": hashlib.sha256(WHEEL_LOCK).hexdigest(),
            "inventory_sha256": hashlib.sha256(WHEEL_INVENTORY).hexdigest(),
        },
        "baseline": {
            "run_id": "spain-fresh-20260721-009",
            "evidence_sha256": hashlib.sha256(SYNTHETIC_EVIDENCE_BYTES).hexdigest(),
            "fingerprint_entry_count": 148,
            "fingerprint_array_sha256": hashlib.sha256(SYNTHETIC_FINGERPRINT_BYTES).hexdigest(),
            "firewall_rules_sha256": "4" * 64,
            "firewall_rule_count": 129,
        },
        "builder_tool": {
            "name": "synthetic",
            "version": "1",
            "release_asset": "none",
            "release_asset_sha256": "5" * 64,
        },
    }
)

REQUIRED_ARTIFACTS = {
    f"payload/source/amn2-runtime-source-{SOURCE_COMMIT}.tar.gz": ("source_runtime", SOURCE_ARCHIVE),
    "payload/python/wheelhouse/requirements-linux-x86_64-py312.lock": ("wheel_lock", WHEEL_LOCK),
    "payload/python/wheelhouse/wheelhouse-inventory.json": ("wheelhouse_inventory", WHEEL_INVENTORY),
    "payload/python/wheelhouse/demo-1.0-py3-none-any.whl": ("python_wheel", WHEEL_BYTES),
    "payload/docker/docker-synthetic-test-linux-x86_64.tgz": ("docker_bundle", DOCKER_ARCHIVE),
    "payload/awg/amneziawg-go-test-linux-amd64.tar": ("awg_image_archive", AWG_ARCHIVE),
    "units/amn2-spain-web.service": ("systemd_unit", b"web"),
    "units/amn2-spain-bot.service": ("systemd_unit", b"bot"),
    "units/amn2-spain-docker.service": ("systemd_unit", b"docker-unit"),
    "units/amn2-spain-network.service": ("systemd_unit", b"network-unit"),
    "templates/runtime.env": ("env_template", b"env"),
    "templates/docker-daemon.json": ("docker_daemon_template", b"{}"),
    "templates/awgsp0.conf": ("server_config_template", b"awg"),
    "templates/servers.yml": ("server_config_template", b"servers"),
    "templates/nftables.conf": ("firewall_template", network_module.NFT_CONFIG.encode()),
    "templates/awg-start.sh": ("runtime_script", b"#!/bin/sh\n"),
    "scripts/phase12_spain_remote_executor.sh": ("installer", b"install"),
    "scripts/phase12_spain_package.py": ("package_verifier", b"package-verifier"),
    "scripts/phase12_spain_precondition.py": ("precondition", b"precondition"),
    "scripts/phase12_spain_installer.py": ("rollback", b"rollback"),
    "scripts/phase12_spain_live_backend.py": ("live_backend", b"backend"),
    "scripts/phase12_spain_network.py": ("network_manager", b"network"),
    "metadata/resource-plan.json": ("resource_plan", canonical_json_bytes(RESOURCE_PLAN)),
    "metadata/run009-evidence.json": ("baseline_evidence", SYNTHETIC_EVIDENCE_BYTES),
    "metadata/fingerprint-array.json": ("fingerprint_array", SYNTHETIC_FINGERPRINT_BYTES),
    "provenance/input-provenance.json": ("provenance", PROVENANCE),
}


def package_manifest(
    files: dict[str, tuple[str, bytes]],
    *,
    awg_image: dict[str, str] | None = None,
) -> dict[str, object]:
    entries = [
        {
            "path": path,
            "kind": kind,
            "size": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        }
        for path, (kind, content) in sorted(files.items())
    ]
    evidence_body = next(body for kind, body in files.values() if kind == "baseline_evidence")
    fingerprint_body = next(body for kind, body in files.values() if kind == "fingerprint_array")
    return {
        "schema": "amn2.spain-install-package.v1",
        "self_hash_policy": "manifest-excluded",
        "target": {"architecture": "x86_64", "python_major_minor": "3.12"},
        "artifacts": entries,
        "resource_plan_sha256": sha256_canonical(RESOURCE_PLAN),
        "fingerprint_array_sha256": package_module.RUN009_FINGERPRINT_SHA256,
        "run009_evidence_sha256": package_module.RUN009_EVIDENCE_SHA256,
        "awg_image": awg_image or {
            "reference": AWG_REFERENCE,
            "index_digest": AWG_INDEX_DIGEST,
            "platform_digest": AWG_PLATFORM_DIGEST,
            "config_digest": AWG_CONFIG_DIGEST,
        },
    }


def package_tar(
    files: dict[str, tuple[str, bytes]] | None = None,
    *,
    manifest_mutator=None,
    extra: tuple[str, bytes, str] | None = None,
    awg_image: dict[str, str] | None = None,
) -> bytes:
    selected = dict(REQUIRED_ARTIFACTS if files is None else files)
    manifest = package_manifest(selected, awg_image=awg_image)
    if manifest_mutator is not None:
        manifest_mutator(manifest)
    members: list[tuple[str, bytes, str]] = [
        ("manifest.json", canonical_json_bytes(manifest), "file")
    ]
    members.extend((path, body, "file") for path, (_kind, body) in selected.items())
    if extra is not None:
        members.append(extra)
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as archive:
        for name, body, member_type in members:
            info = tarfile.TarInfo(name)
            info.mtime = 0
            if member_type == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = body.decode()
                archive.addfile(info)
            else:
                info.size = len(body)
                archive.addfile(info, io.BytesIO(body))
    return stream.getvalue()


def test_canonical_digest_is_reproducible_and_order_independent() -> None:
    left = {"z": [3, 2, 1], "a": {"b": True, "a": None}}
    right = {"a": {"a": None, "b": True}, "z": [3, 2, 1]}
    assert canonical_json_bytes(left) == canonical_json_bytes(right)
    assert sha256_canonical(left) == sha256_canonical(right)


def test_package_verifier_accepts_exact_allowlisted_package(tmp_path: Path) -> None:
    archive = tmp_path / "package.tar"
    archive.write_bytes(package_tar())
    report = verify_package(archive)
    assert set(report) == {
        "schema",
        "result",
        "archive_sha256",
        "archive_size",
        "manifest_sha256",
        "resource_plan_sha256",
        "run009_evidence_sha256",
        "fingerprint_array_sha256",
        "fingerprint_entry_count",
    }
    immutable_report = PackageVerificationReport.from_mapping(report)
    assert immutable_report.fingerprint_entry_count == 148
    assert report["resource_plan_sha256"] == sha256_canonical(RESOURCE_PLAN)


def test_payload_preparation_defers_settings_import_until_runtime_site_packages(
    tmp_path: Path, monkeypatch
) -> None:
    source_archive = (
        ROOT
        / "private-artifacts"
        / "phase12-spain-install-boundary-stable-critical-v6-20260722"
        / "offline-verify-extract"
        / "payload"
        / "source"
        / "amn2-runtime-source-55dc243b8e6c6bdb57f8301b56326e4cd4072d19.tar.gz"
    )
    if not source_archive.is_file():
        pytest.skip("official Phase 12 source archive unavailable")
    with tarfile.open(source_archive, "r:gz") as archive:
        archive.extractall(tmp_path, filter="data")
    source_root = tmp_path / "source"
    monkeypatch.setattr(
        live_backend,
        "_validate_authoritative_runtime_settings",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            live_backend.BackendError("system-site pydantic unavailable")
        ),
    )

    prepared = live_backend.prepare_production_filesystem_payloads(
        source_root=source_root,
        endpoint_host="spain.example",
        package_content_root=(
            ROOT
            / "private-artifacts"
            / "phase12-spain-install-boundary-stable-critical-v6-20260722"
            / "offline-verify-extract"
        ),
    )

    assert prepared.endpoint_host == "spain.example"
    assert "etc/amn2-spain/runtime.env" in prepared.rendered_payloads


def test_package_verifier_can_bind_the_callers_already_open_descriptor(
    tmp_path: Path, monkeypatch
) -> None:
    archive = tmp_path / "package.tar"
    archive.write_bytes(package_tar())
    descriptor = package_module.os.open(archive, package_module.os.O_RDONLY)
    try:
        monkeypatch.setattr(
            package_module.os,
            "open",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(
                AssertionError("descriptor verifier reopened a pathname")
            ),
        )
        report = verify_package_fd(descriptor)
        assert report["archive_sha256"] == hashlib.sha256(archive.read_bytes()).hexdigest()
        package_module.os.fstat(descriptor)
    finally:
        package_module.os.close(descriptor)


def test_verified_package_fd_extracts_exact_regular_allowlist_without_reopening_source(
    tmp_path: Path,
) -> None:
    archive = tmp_path / "package.tar"
    archive.write_bytes(package_tar())
    descriptor = os.open(archive, os.O_RDONLY)
    try:
        target = tmp_path / "content"
        plan = plan_verified_package_extraction_fd(descriptor)
        result = extract_verified_package_fd(
            descriptor,
            target,
            expected_uid=None,
            expected_gid=None,
            expected_inventory=plan["inventory"],
        )
    finally:
        os.close(descriptor)
    assert result["report"]["result"] == "passed"
    assert result["inventory"] == plan["inventory"]
    assert set(result["inventory"]) == {"manifest.json", *REQUIRED_ARTIFACTS}
    assert (target / "manifest.json").is_file()
    assert (target / "scripts" / "phase12_spain_installer.py").is_file()
    source_plan = plan_verified_package_source(target)
    prepared_source = tmp_path / "prepared-source"
    source_result = expand_verified_package_source(
        target,
        prepared_source,
        expected_binding=source_plan,
    )
    assert source_result["inventory"] == {
        "app.py": {
            "sha256": hashlib.sha256(SOURCE_FILE).hexdigest(),
            "size": len(SOURCE_FILE),
            "mode": "0644",
        }
    }
    assert (prepared_source / "app.py").read_bytes() == SOURCE_FILE


def test_package_verifier_accepts_faithful_staged_official_raw_inputs(
    tmp_path: Path, monkeypatch
) -> None:
    staged = ROOT / "private-artifacts" / "phase12-spain-install-package-inputs-20260721"
    if not staged.is_dir():
        pytest.skip("private official Phase 12 package inputs unavailable")
    monkeypatch.setattr(
        package_module,
        "RUN009_EVIDENCE_SHA256",
        package_module.DEFAULT_RUN009_EVIDENCE_SHA256,
    )
    monkeypatch.setattr(
        package_module,
        "RUN009_FINGERPRINT_SHA256",
        package_module.DEFAULT_RUN009_FINGERPRINT_SHA256,
    )
    source_name = "amn2-runtime-source-55dc243b8e6c6bdb57f8301b56326e4cd4072d19.tar.gz"
    docker_name = "docker-29.6.2-linux-x86_64.tgz"
    awg_name = "amneziawg-go-3c78eb57-linux-amd64.tar"
    files: dict[str, tuple[str, bytes]] = {
        f"payload/source/{source_name}": (
            "source_runtime",
            (staged / "payload" / "source" / source_name).read_bytes(),
        ),
        "payload/python/wheelhouse/requirements-linux-x86_64-py312.lock": (
            "wheel_lock",
            (staged / "payload" / "python" / "requirements.lock").read_bytes(),
        ),
        "payload/python/wheelhouse/wheelhouse-inventory.json": (
            "wheelhouse_inventory",
            (staged / "payload" / "python" / "wheelhouse-inventory.json").read_bytes(),
        ),
        f"payload/docker/{docker_name}": (
            "docker_bundle",
            (staged / "payload" / "docker" / docker_name).read_bytes(),
        ),
        f"payload/awg/{awg_name}": (
            "awg_image_archive",
            (staged / "payload" / "awg" / awg_name).read_bytes(),
        ),
        "units/amn2-spain-web.service": (
            "systemd_unit",
            (TRACKED_PACKAGE_ROOT / "units" / "amn2-spain-web.service").read_bytes(),
        ),
        "units/amn2-spain-bot.service": (
            "systemd_unit",
            (TRACKED_PACKAGE_ROOT / "units" / "amn2-spain-bot.service").read_bytes(),
        ),
        "units/amn2-spain-docker.service": (
            "systemd_unit",
            (TRACKED_PACKAGE_ROOT / "units" / "amn2-spain-docker.service").read_bytes(),
        ),
        "units/amn2-spain-network.service": (
            "systemd_unit",
            (TRACKED_PACKAGE_ROOT / "units" / "amn2-spain-network.service").read_bytes(),
        ),
        "templates/runtime.env": (
            "env_template",
            (TRACKED_PACKAGE_ROOT / "templates" / "runtime.env").read_bytes(),
        ),
        "templates/awgsp0.conf": (
            "server_config_template",
            (TRACKED_PACKAGE_ROOT / "templates" / "awgsp0.conf").read_bytes(),
        ),
        "templates/servers.yml": (
            "server_config_template",
            (TRACKED_PACKAGE_ROOT / "templates" / "servers.yml").read_bytes(),
        ),
        "templates/docker-daemon.json": (
            "docker_daemon_template",
            (TRACKED_PACKAGE_ROOT / "templates" / "docker-daemon.json").read_bytes(),
        ),
        "templates/nftables.conf": (
            "firewall_template",
            (TRACKED_PACKAGE_ROOT / "templates" / "nftables.conf").read_bytes(),
        ),
        "templates/awg-start.sh": (
            "runtime_script",
            (TRACKED_PACKAGE_ROOT / "templates" / "awg-start.sh").read_bytes(),
        ),
        "scripts/phase12_spain_remote_executor.sh": (
            "installer",
            REMOTE_EXECUTOR.read_bytes(),
        ),
        "scripts/phase12_spain_package.py": (
            "package_verifier",
            (ROOT / "scripts" / "phase12_spain_package.py").read_bytes(),
        ),
        "scripts/phase12_spain_precondition.py": (
            "precondition",
            (ROOT / "scripts" / "phase12_spain_precondition.py").read_bytes(),
        ),
        "scripts/phase12_spain_installer.py": (
            "rollback",
            (ROOT / "scripts" / "phase12_spain_installer.py").read_bytes(),
        ),
        "scripts/phase12_spain_live_backend.py": (
            "live_backend",
            (ROOT / "scripts" / "phase12_spain_live_backend.py").read_bytes(),
        ),
        "scripts/phase12_spain_network.py": (
            "network_manager",
            (ROOT / "scripts" / "phase12_spain_network.py").read_bytes(),
        ),
        "metadata/resource-plan.json": (
            "resource_plan",
            canonical_json_bytes(RESOURCE_PLAN),
        ),
        "metadata/run009-evidence.json": (
            "baseline_evidence",
            (staged / "evidence" / "run009-preflight-evidence.json").read_bytes(),
        ),
        "metadata/fingerprint-array.json": (
            "fingerprint_array",
            (staged / "evidence" / "run009-fingerprint-array.json").read_bytes(),
        ),
        "provenance/input-provenance.json": (
            "provenance",
            (staged / "provenance" / "input-provenance.json").read_bytes(),
        ),
    }
    for wheel in sorted((staged / "payload" / "python" / "wheelhouse").glob("*.whl")):
        files[f"payload/python/wheelhouse/{wheel.name}"] = ("python_wheel", wheel.read_bytes())
    archive = tmp_path / "official-inputs-package.tar"
    archive.write_bytes(
        package_tar(
            files,
            awg_image={
                "reference": "amneziavpn/amneziawg-go@sha256:acef5ae84808a9568448e9d8c7a96f640a5ccc590b0f8dfbc2df9f9dc0e848c9",
                "index_digest": "sha256:acef5ae84808a9568448e9d8c7a96f640a5ccc590b0f8dfbc2df9f9dc0e848c9",
                "platform_digest": "sha256:3c78eb57ef5cb44f63aed185e79c104593c854a5ebde3e1075470301bcc77c44",
                "config_digest": "sha256:0f21ddfb3313affe3a336693886ced918301335815e4b7db3d15b5a0a5da6afb",
            },
        )
    )
    report = verify_package(archive)
    assert PackageVerificationReport.from_mapping(report).fingerprint_entry_count == 148
    expansion = expand_verified_wheelhouse(
        staged / "payload" / "python" / "wheelhouse",
        staged / "payload" / "python" / "wheelhouse-inventory.json",
        tmp_path / "site-packages",
        python_major_minor="3.12",
    )
    assert expansion["wheel_count"] == 43


def test_package_verifier_uses_one_nofollow_fd_for_verify_and_archive_hash(
    tmp_path: Path, monkeypatch
) -> None:
    archive = tmp_path / "package.tar"
    archive.write_bytes(package_tar())
    original_path_open = Path.open

    def forbid_reopen(path: Path, *args, **kwargs):
        if path == archive:
            raise AssertionError("package pathname reopened after initial verification")
        return original_path_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", forbid_reopen)
    report = verify_package(archive)
    assert report["archive_sha256"] == hashlib.sha256(package_tar()).hexdigest()


def test_production_baseline_policy_constants_are_authoritative() -> None:
    assert package_module.DEFAULT_RUN009_EVIDENCE_SHA256.upper() == (
        "8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8"
    )
    assert package_module.DEFAULT_RUN009_FINGERPRINT_SHA256.upper() == (
        "E15219CB5204D54A9AD11263CFBA1F7C86E16DAB3287C752A8B6F136EC4A5ED5"
    )
    assert precondition_module.DEFAULT_RUN009_EVIDENCE_SHA256 == (
        package_module.DEFAULT_RUN009_EVIDENCE_SHA256
    )
    assert precondition_module.DEFAULT_RUN009_FINGERPRINT_SHA256 == (
        package_module.DEFAULT_RUN009_FINGERPRINT_SHA256
    )


def test_fingerprint_must_be_derived_from_evidence_and_have_148_unique_entries(
    tmp_path: Path,
) -> None:
    files = dict(REQUIRED_ARTIFACTS)
    forged = copy.deepcopy(SYNTHETIC_FINGERPRINT)
    forged[0]["restart_count"] = 99
    forged_bytes = canonical_json_bytes(forged)
    files["metadata/fingerprint-array.json"] = ("fingerprint_array", forged_bytes)
    archive = tmp_path / "forged-fingerprint.tar"
    archive.write_bytes(package_tar(files))
    with pytest.raises(PackageVerificationError, match="derived from run009 evidence"):
        verify_package(archive)

    duplicate_evidence = json.loads(SYNTHETIC_EVIDENCE_BYTES)
    duplicate_evidence["unrelated_service_fingerprint"][-1] = copy.deepcopy(
        duplicate_evidence["unrelated_service_fingerprint"][0]
    )
    duplicate_bytes = canonical_json_bytes(duplicate_evidence)
    monkeypatch_sha = hashlib.sha256(duplicate_bytes).hexdigest()
    duplicate_fp_bytes = canonical_json_bytes(
        duplicate_evidence["unrelated_service_fingerprint"]
    )
    duplicate_fp_sha = hashlib.sha256(duplicate_fp_bytes).hexdigest()
    original = package_module.RUN009_EVIDENCE_SHA256
    original_fp = package_module.RUN009_FINGERPRINT_SHA256
    package_module.RUN009_EVIDENCE_SHA256 = monkeypatch_sha
    package_module.RUN009_FINGERPRINT_SHA256 = duplicate_fp_sha
    try:
        files = dict(REQUIRED_ARTIFACTS)
        files["metadata/run009-evidence.json"] = ("baseline_evidence", duplicate_bytes)
        files["metadata/fingerprint-array.json"] = (
            "fingerprint_array",
            duplicate_fp_bytes,
        )
        archive = tmp_path / "duplicate-fingerprint.tar"
        archive.write_bytes(package_tar(files))
        with pytest.raises(PackageVerificationError, match="unique"):
            verify_package(archive)
    finally:
        package_module.RUN009_EVIDENCE_SHA256 = original
        package_module.RUN009_FINGERPRINT_SHA256 = original_fp


def test_package_verifier_rejects_valid_outer_hashes_with_invalid_inner_payloads(
    tmp_path: Path,
) -> None:
    files = dict(REQUIRED_ARTIFACTS)
    source_path = next(path for path, (kind, _body) in files.items() if kind == "source_runtime")
    files[source_path] = ("source_runtime", b"source")
    archive = tmp_path / "opaque-inner-payloads.tar"
    archive.write_bytes(package_tar(files))
    with pytest.raises(PackageVerificationError, match="source runtime"):
        verify_package(archive)


def test_package_verifier_rejects_valid_outer_hash_with_invalid_docker_bundle(
    tmp_path: Path,
) -> None:
    files = dict(REQUIRED_ARTIFACTS)
    docker_path = next(path for path, (kind, _body) in files.items() if kind == "docker_bundle")
    files[docker_path] = ("docker_bundle", b"docker")
    archive = tmp_path / "opaque-docker.tar"
    archive.write_bytes(package_tar(files))
    with pytest.raises(PackageVerificationError, match="Docker bundle"):
        verify_package(archive)


def test_package_verifier_rejects_valid_outer_hash_with_invalid_awg_docker_save(
    tmp_path: Path,
) -> None:
    files = dict(REQUIRED_ARTIFACTS)
    awg_path = next(path for path, (kind, _body) in files.items() if kind == "awg_image_archive")
    files[awg_path] = ("awg_image_archive", b"image")
    archive = tmp_path / "opaque-awg.tar"
    archive.write_bytes(package_tar(files))
    with pytest.raises(PackageVerificationError, match="AWG image"):
        verify_package(archive)


def test_package_verifier_rejects_wheel_lock_inventory_or_tag_mismatch(tmp_path: Path) -> None:
    files = dict(REQUIRED_ARTIFACTS)
    lock_path = next(path for path, (kind, _body) in files.items() if kind == "wheel_lock")
    files[lock_path] = ("wheel_lock", b"demo==1.0 --hash=sha256:" + b"0" * 64 + b"\n")
    archive = tmp_path / "bad-wheel-lock.tar"
    archive.write_bytes(package_tar(files))
    with pytest.raises(PackageVerificationError, match="wheel lock"):
        verify_package(archive)


def test_package_verifier_rejects_provenance_cross_binding_mismatch(tmp_path: Path) -> None:
    files = dict(REQUIRED_ARTIFACTS)
    provenance = json.loads(PROVENANCE)
    provenance["source"]["commit"] = "9" * 40
    files["provenance/input-provenance.json"] = (
        "provenance",
        canonical_json_bytes(provenance),
    )
    archive = tmp_path / "bad-provenance.tar"
    archive.write_bytes(package_tar(files))
    with pytest.raises(PackageVerificationError, match="provenance"):
        verify_package(archive)


def test_offline_wheelhouse_expands_hash_bound_regular_files_without_pip(
    tmp_path: Path,
) -> None:
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    (wheelhouse / "demo-1.0-py3-none-any.whl").write_bytes(WHEEL_BYTES)
    inventory = tmp_path / "inventory.json"
    inventory.write_bytes(WHEEL_INVENTORY)
    target = tmp_path / "site-packages"
    report = expand_verified_wheelhouse(
        wheelhouse, inventory, target, python_major_minor="3.12"
    )
    assert report["wheel_count"] == 1
    assert (target / "demo" / "__init__.py").read_text(encoding="utf-8") == "VALUE = 1\n"


def test_wheel_inspect_and_extract_use_same_immutable_bytes(tmp_path: Path, monkeypatch) -> None:
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    wheel_path = wheelhouse / "demo-1.0-py3-none-any.whl"
    wheel_path.write_bytes(WHEEL_BYTES)
    inventory = tmp_path / "inventory.json"
    inventory.write_bytes(WHEEL_INVENTORY)
    original_zip = zipfile.ZipFile

    def swap_if_path(file, *args, **kwargs):
        if isinstance(file, (str, Path)) and Path(file) == wheel_path:
            wheel_path.write_bytes(b"swapped")
        return original_zip(file, *args, **kwargs)

    monkeypatch.setattr(zipfile, "ZipFile", swap_if_path)
    report = expand_verified_wheelhouse(
        wheelhouse, inventory, tmp_path / "target", python_major_minor="3.12"
    )
    assert report["wheel_count"] == 1


@pytest.mark.parametrize("member", ["../escape.py", "demo-1.0.data/scripts/run"])
def test_offline_wheelhouse_rejects_traversal_and_unsupported_data_layout(
    tmp_path: Path, member: str
) -> None:
    bad_stream = io.BytesIO()
    with zipfile.ZipFile(bad_stream, "w") as wheel:
        wheel.writestr(member, "bad")
    body = bad_stream.getvalue()
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    filename = "bad-1.0-py3-none-any.whl"
    (wheelhouse / filename).write_bytes(body)
    inventory = tmp_path / "inventory.json"
    inventory.write_bytes(
        canonical_json_bytes(
            {
                "schema": "amn2.spain-wheelhouse.v1",
                "target": {"architecture": "x86_64", "python_major_minor": "3.12"},
                "wheels": [
                    {
                        "filename": filename,
                        "sha256": hashlib.sha256(body).hexdigest(),
                        "size": len(body),
                    }
                ],
            }
        )
    )
    with pytest.raises(PackageVerificationError):
        expand_verified_wheelhouse(
            wheelhouse, inventory, tmp_path / "target", python_major_minor="3.12"
        )


def test_offline_wheelhouse_rejects_symlinks_wrong_python_and_extra_wheels(
    tmp_path: Path,
) -> None:
    symlink_stream = io.BytesIO()
    with zipfile.ZipFile(symlink_stream, "w") as wheel:
        info = zipfile.ZipInfo("demo/link")
        info.create_system = 3
        info.external_attr = 0o120777 << 16
        wheel.writestr(info, "../../escape")
    body = symlink_stream.getvalue()
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    filename = "bad-1.0-py3-none-any.whl"
    (wheelhouse / filename).write_bytes(body)
    inventory = tmp_path / "inventory.json"
    inventory_body = {
        "schema": "amn2.spain-wheelhouse.v1",
        "target": {"architecture": "x86_64", "python_major_minor": "3.12"},
        "wheels": [
            {
                "filename": filename,
                "sha256": hashlib.sha256(body).hexdigest(),
                "size": len(body),
            }
        ],
    }
    inventory.write_bytes(canonical_json_bytes(inventory_body))
    with pytest.raises(PackageVerificationError, match="symlink"):
        expand_verified_wheelhouse(
            wheelhouse, inventory, tmp_path / "target", python_major_minor="3.12"
        )
    with pytest.raises(PackageVerificationError, match="Python"):
        expand_verified_wheelhouse(
            wheelhouse, inventory, tmp_path / "target", python_major_minor="3.11"
        )
    (wheelhouse / "extra.whl").write_bytes(b"extra")
    with pytest.raises(PackageVerificationError, match="allowlist"):
        expand_verified_wheelhouse(
            wheelhouse, inventory, tmp_path / "target", python_major_minor="3.12"
        )


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (lambda manifest: manifest["artifacts"][0].update(sha256="0" * 64), "hash"),
        (lambda manifest: manifest["artifacts"].pop(), "required artifact"),
        (lambda manifest: manifest.update(self_hash_policy="manifest-sha256"), "self hash"),
        (
            lambda manifest: manifest["awg_image"].update(reference="amneziavpn/amneziawg-go:latest"),
            "digest reference",
        ),
    ],
)
def test_package_verifier_fails_closed_on_invalid_manifest(
    tmp_path: Path, mutate, match: str
) -> None:
    archive = tmp_path / "package.tar"
    archive.write_bytes(package_tar(manifest_mutator=mutate))
    with pytest.raises(PackageVerificationError, match=match):
        verify_package(archive)


@pytest.mark.parametrize(
    "missing_kind", ["docker_bundle", "package_verifier", "precondition"]
)
def test_package_verifier_rejects_missing_required_artifact_kind(
    tmp_path: Path, missing_kind: str
) -> None:
    files = dict(REQUIRED_ARTIFACTS)
    files.pop(next(path for path, (kind, _body) in files.items() if kind == missing_kind))
    archive = tmp_path / "package.tar"
    archive.write_bytes(package_tar(files))
    with pytest.raises(PackageVerificationError, match="required artifact"):
        verify_package(archive)


def test_package_verifier_rejects_unbounded_declared_unpacked_size(tmp_path: Path) -> None:
    def mutate(manifest: dict[str, object]) -> None:
        manifest["artifacts"][0]["size"] = 9 * 1024 * 1024 * 1024

    archive = tmp_path / "oversized.tar"
    archive.write_bytes(package_tar(manifest_mutator=mutate))
    with pytest.raises(PackageVerificationError, match="size budget"):
        verify_package(archive)


def test_package_verifier_rejects_duplicate_singleton_kind_and_wheel_basename(
    tmp_path: Path,
) -> None:
    files = dict(REQUIRED_ARTIFACTS)
    files["alternate/remote_executor.sh"] = ("installer", b"other")
    archive = tmp_path / "duplicate-singleton.tar"
    archive.write_bytes(package_tar(files))
    with pytest.raises(PackageVerificationError, match="exactly one"):
        verify_package(archive)

    files = dict(REQUIRED_ARTIFACTS)
    files["alternate/demo-1.0-py3-none-any.whl"] = ("python_wheel", WHEEL_BYTES)
    archive = tmp_path / "duplicate-wheel.tar"
    archive.write_bytes(package_tar(files))
    with pytest.raises(PackageVerificationError, match="wheel basename"):
        verify_package(archive)


def test_package_verifier_rejects_known_kind_at_unsealed_path(tmp_path: Path) -> None:
    files = dict(REQUIRED_ARTIFACTS)
    source_path = next(path for path, (kind, _body) in files.items() if kind == "source_runtime")
    source_entry = files.pop(source_path)
    files["payload/source/alternate.tar.gz"] = source_entry
    archive = tmp_path / "unsealed-path.tar"
    archive.write_bytes(package_tar(files))
    with pytest.raises(PackageVerificationError, match="path contract"):
        verify_package(archive)


@pytest.mark.parametrize(
    "extra",
    [
        ("unexpected.txt", b"extra", "file"),
        ("../escape", b"escape", "file"),
        ("payload/link", b"../../escape", "symlink"),
    ],
)
def test_package_verifier_rejects_extra_traversal_and_links(
    tmp_path: Path, extra: tuple[str, bytes, str]
) -> None:
    archive = tmp_path / "package.tar"
    archive.write_bytes(package_tar(extra=extra))
    with pytest.raises(PackageVerificationError):
        verify_package(archive)


def test_wheel_verifier_enforces_aggregate_uncompressed_budget(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(package_module, "MAX_WHEEL_UNCOMPRESSED_BYTES", 1)
    archive = tmp_path / "wheel-budget.tar"
    archive.write_bytes(package_tar())
    with pytest.raises(PackageVerificationError, match="wheel.*budget"):
        verify_package(archive)


@pytest.mark.parametrize("variant", ["duplicate", "fifo", "device", "unsafe_link"])
def test_awg_layer_rejects_duplicate_special_and_unsafe_link_members(variant: str) -> None:
    layer = io.BytesIO()
    with tarfile.open(fileobj=layer, mode="w") as archive:
        first = tarfile.TarInfo("usr/bin/awg")
        first.size = 1
        archive.addfile(first, io.BytesIO(b"x"))
        if variant == "duplicate":
            duplicate = tarfile.TarInfo("usr/bin/awg")
            duplicate.size = 1
            archive.addfile(duplicate, io.BytesIO(b"y"))
        elif variant == "fifo":
            special = tarfile.TarInfo("run/pipe")
            special.type = tarfile.FIFOTYPE
            archive.addfile(special)
        elif variant == "device":
            special = tarfile.TarInfo("dev/fake")
            special.type = tarfile.CHRTYPE
            archive.addfile(special)
        else:
            link = tarfile.TarInfo("usr/bin/escape")
            link.type = tarfile.SYMTYPE
            link.linkname = "../../../outside"
            archive.addfile(link)
    with pytest.raises(PackageVerificationError, match="AWG layer"):
        package_module._validate_awg_layer_stream(io.BytesIO(layer.getvalue()))


def test_raw_source_runtime_requires_hash_bound_pax_commit() -> None:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as archive:
        directory = tarfile.TarInfo("source")
        directory.type = tarfile.DIRTYPE
        archive.addfile(directory)
        body = b"print('x')\n"
        member = tarfile.TarInfo("source/app.py")
        member.size = len(body)
        archive.addfile(member, io.BytesIO(body))
    with pytest.raises(PackageVerificationError, match="pax.*commit"):
        package_module._validate_source_runtime(io.BytesIO(raw.getvalue()))


def test_source_tree_planner_precedes_nofollow_exact_expansion(tmp_path: Path) -> None:
    archive = tmp_path / f"amn2-runtime-source-{SOURCE_COMMIT}.tar.gz"
    archive.write_bytes(SOURCE_ARCHIVE)
    digest = hashlib.sha256(SOURCE_ARCHIVE).hexdigest()
    plan = plan_verified_source_tree(
        archive,
        expected_sha256=digest,
        expected_size=len(SOURCE_ARCHIVE),
        expected_commit=SOURCE_COMMIT,
    )
    assert plan["rows"] == [{
        "path": "app.py", "type": "file", "mode": "0644",
        "sha256": hashlib.sha256(SOURCE_FILE).hexdigest(), "size": len(SOURCE_FILE),
    }]
    target = tmp_path / "source"
    expand_verified_source_tree(
        archive,
        target,
        expected_plan=plan,
        expected_sha256=digest,
        expected_size=len(SOURCE_ARCHIVE),
        expected_commit=SOURCE_COMMIT,
    )
    assert (target / "app.py").read_bytes() == SOURCE_FILE


def baseline() -> dict[str, object]:
    return {
        "run009_evidence_sha256": package_module.RUN009_EVIDENCE_SHA256,
        "fingerprint_array_sha256": package_module.RUN009_FINGERPRINT_SHA256,
        "systemd_projection": copy.deepcopy(OBSERVATION["systemd_projection"]),
        "firewall": copy.deepcopy(OBSERVATION["firewall"]),
        "firewall_semantic_rebaseline": copy.deepcopy(
            precondition_module.FIREWALL_SEMANTIC_REBASELINE
        ),
        "run009_evidence_hex": SYNTHETIC_EVIDENCE_BYTES.hex(),
    }


def test_precondition_rejects_baseline_hashes_outside_authoritative_policy() -> None:
    forged = baseline()
    forged["run009_evidence_sha256"] = "0" * 64
    with pytest.raises(PreconditionError, match="authoritative run009"):
        validate_preconditions(OBSERVATION, RESOURCE_PLAN, forged)


def test_precondition_receipt_is_canonical_detached_and_verifiable() -> None:
    report = validate_preconditions(OBSERVATION, RESOURCE_PLAN, baseline())
    receipt, detached_sha256 = build_precondition_receipt(
        report,
        package_manifest_sha256="1" * 64,
        resource_plan_sha256=sha256_canonical(RESOURCE_PLAN),
        host_identity_sha256=HOST_IDENTITY_SHA256,
        boot_id=BOOT_ID,
        collector_sha256=COLLECTOR_SHA256,
        executor_sha256=EXECUTOR_SHA256,
        package_archive_sha256="6" * 64,
        package_archive_size=123456,
        issued_at_epoch=RECEIPT_NOW,
        ttl_seconds=300,
        nonce=RECEIPT_NONCE,
    )
    assert receipt["result"] == "passed"
    assert receipt["mutation_authorized"] is False
    assert receipt["foreign_service_persistent_equal"] is True
    assert receipt["foreign_service_volatile_before_count"] == 0
    assert receipt["foreign_service_volatile_after_count"] == 0
    verify_precondition_receipt(
        receipt,
        detached_sha256,
        package_manifest_sha256="1" * 64,
        resource_plan_sha256=sha256_canonical(RESOURCE_PLAN),
        host_identity_sha256=HOST_IDENTITY_SHA256,
        boot_id=BOOT_ID,
        collector_sha256=COLLECTOR_SHA256,
        executor_sha256=EXECUTOR_SHA256,
        package_archive_sha256="6" * 64,
        package_archive_size=123456,
    )
    tampered = copy.deepcopy(receipt)
    tampered["foreign_service_volatile_after_count"] = True
    with pytest.raises(PreconditionError, match="binding"):
        verify_precondition_receipt(
            tampered,
            hashlib.sha256(canonical_json_bytes(tampered)).hexdigest(),
            package_manifest_sha256="1" * 64,
            resource_plan_sha256=sha256_canonical(RESOURCE_PLAN),
            host_identity_sha256=HOST_IDENTITY_SHA256,
            boot_id=BOOT_ID,
            collector_sha256=COLLECTOR_SHA256,
            executor_sha256=EXECUTOR_SHA256,
            package_archive_sha256="6" * 64,
            package_archive_size=123456,
        )


@pytest.mark.parametrize(
    ("field", "value", "match"),
    [
        (("os", "family"), "debian", "os family"),
        (("os", "architecture"), "aarch64", "architecture"),
        (("os", "python"), "3.11.9", "python"),
        (("capacity", "disk_available_bytes"), 1, "disk"),
        (("capacity", "inodes_available"), 1, "inode"),
        (("capacity", "memory_available_kib"), 1, "memory"),
        (("existing", "paths"), ["/opt/amn2-spain"], "path"),
        (("existing", "users"), ["amn2-spain"], "user"),
        (("existing", "groups"), ["amn2-spain"], "group"),
        (("existing", "units"), ["amn2-spain-web.service"], "unit"),
        (("existing", "containers"), ["amn2-spain-awg"], "container"),
        (("existing", "networks"), ["amn2-spain-net"], "network"),
        (("existing", "bridges"), ["amn2spbr0"], "bridge"),
        (("existing", "interfaces"), ["awgsp0"], "interface"),
        (("listeners",), ["tcp|loopback|3031"], "listener"),
        (("addresses",), ["10.212.12.99/24"], "CIDR"),
        (("routes",), ["172.29.251.0/28"], "CIDR"),
        (("docker_present",), True, "Docker"),
    ],
)
def test_precondition_rejects_target_and_resource_conflicts(field, value, match: str) -> None:
    observation = copy.deepcopy(OBSERVATION)
    cursor = observation
    for key in field[:-1]:
        cursor = cursor[key]
    cursor[field[-1]] = value
    with pytest.raises(PreconditionError, match=match):
        validate_preconditions(observation, RESOURCE_PLAN, baseline())


def test_precondition_allows_declared_retained_audit_receipts() -> None:
    observation = copy.deepcopy(OBSERVATION)
    observation["existing"]["retained_paths"] = copy.deepcopy(
        RESOURCE_PLAN["resources"]["retained_paths"]
    )

    report = validate_preconditions(observation, RESOURCE_PLAN, baseline())

    assert report["result"] == "passed"
    observation["existing"]["retained_paths"].append("/var/lib/foreign-audit")
    with pytest.raises(PreconditionError, match="retained audit path collision"):
        validate_preconditions(observation, RESOURCE_PLAN, baseline())


def test_preparation_failure_message_keeps_only_safe_cause_labels() -> None:
    assert installer_module._preparation_failure_message(
        live_backend.BackendError("authoritative runtime credential preparation failed")
    ) == (
        "production installation preparation failed:"
        "authoritative runtime credential preparation failed"
    )
    assert installer_module._preparation_failure_message(
        live_backend.BackendError("token=secret")
    ) == "production installation preparation failed:backend_error"
    assert installer_module._runtime_failure_message(
        live_backend.BackendError("docker_image_load_no_space")
    ) == "production runtime rollback failed:docker_image_load_no_space"
    assert installer_module._runtime_failure_message(
        live_backend.BackendError("docker_image_load_timeout")
    ) == "production runtime rollback failed:docker_image_load_timeout"
    assert installer_module._runtime_failure_message(
        live_backend.BackendError("token=secret")
    ) == "production runtime rollback failed"


def test_runtime_failure_message_preserves_allowlisted_docker_cause_through_rollback_wrapper() -> None:
    try:
        try:
            raise live_backend.BackendError("docker_image_load_layer_apply")
        except live_backend.BackendError as cause:
            raise InstallError("partial rollback failure after production_runtime") from cause
    except InstallError as wrapped:
        assert installer_module._runtime_failure_message(wrapped) == (
            "production runtime rollback failed:docker_image_load_layer_apply"
        )

    try:
        try:
            try:
                raise live_backend.BackendError("docker_image_load_archive")
            except live_backend.BackendError as cause:
                raise InstallError("partial rollback failure after production_runtime") from cause
        except InstallError:
            raise live_backend.BackendError("package recovery failed")
    except live_backend.BackendError as recovery_error:
        assert installer_module._runtime_failure_message(recovery_error) == (
            "production runtime rollback failed:docker_image_load_archive"
        )


def test_systemd_bundle_reads_units_from_package_content_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    observed: list[tuple[str, Path | None]] = []

    def read_unit(relative: str, *, content_root: Path | None = None, **_kwargs: object) -> bytes:
        observed.append((relative, content_root))
        return b"[Unit]\nDescription=AMN2\n"

    monkeypatch.setattr(live_backend, "_read_package_bound_bytes", read_unit)

    live_backend.build_production_systemd_bundle(
        root=tmp_path,
        runner=lambda *_args, **_kwargs: b"LoadState=not-found\n",
        root_uid=None,
        root_gid=None,
        package_content_root=tmp_path / "content",
    )

    assert observed
    assert {content for _relative, content in observed} == {tmp_path / "content"}
    assert {relative for relative, _content in observed} == {
        "units/" + unit for unit in live_backend.SYSTEMD_UNIT_ORDER
    }


def test_precondition_allows_volatile_restart_count_and_rejects_stable_systemd_drift() -> None:
    observation = copy.deepcopy(OBSERVATION)
    observation["systemd_projection"][0]["restart_count"] = 1
    report = validate_preconditions(observation, RESOURCE_PLAN, baseline())
    assert report["result"] == "passed"
    observation["systemd_projection"][0]["active_state"] = "inactive:dead"
    with pytest.raises(PreconditionError, match="systemd baseline"):
        validate_preconditions(observation, RESOURCE_PLAN, baseline())


def test_precondition_allows_raw_firewall_counter_drift_and_rejects_semantic_drift() -> None:
    observation = copy.deepcopy(OBSERVATION)
    observation["firewall"]["rules_sha256"] = "e" * 64
    report = validate_preconditions(observation, RESOURCE_PLAN, baseline())
    assert report["result"] == "passed"
    observation["firewall"]["semantic_sha256"] = "f" * 64
    with pytest.raises(PreconditionError, match="firewall semantic"):
        validate_preconditions(observation, RESOURCE_PLAN, baseline())


def test_precondition_allows_only_volatile_foreign_service_membership() -> None:
    observation = copy.deepcopy(OBSERVATION)
    observation["systemd_projection"] = []
    report = validate_preconditions(observation, RESOURCE_PLAN, baseline())
    assert report["result"] == "passed"
    assert report["foreign_service_persistent_equal"] is True
    assert report["foreign_service_volatile_before_count"] == len(
        baseline()["systemd_projection"]
    )
    assert report["foreign_service_volatile_after_count"] == 0


def test_precondition_uses_separate_approved_run_capacity_policy() -> None:
    observation = copy.deepcopy(OBSERVATION)
    observation["capacity"]["filesystems"]["/run"] = {
        "disk_available_bytes": 64 * 1024 * 1024,
        "inodes_available": 100000,
    }
    plan = copy.deepcopy(RESOURCE_PLAN)
    plan["run_capacity_minimums"] = {
        "disk_available_bytes": 64 * 1024 * 1024,
        "inodes_available": 100000,
    }
    report = validate_preconditions(observation, plan, baseline())
    assert report["result"] == "passed"


def test_precondition_derives_projection_and_firewall_from_bound_run009_bytes() -> None:
    observation = copy.deepcopy(OBSERVATION)
    forged = baseline()
    forged_projection = copy.deepcopy(observation["systemd_projection"])
    forged_projection[0]["restart_count"] = 99
    observation["systemd_projection"] = forged_projection
    forged["systemd_projection"] = copy.deepcopy(forged_projection)
    with pytest.raises(PreconditionError, match="fingerprint"):
        validate_preconditions(observation, RESOURCE_PLAN, forged)

    observation = copy.deepcopy(OBSERVATION)
    forged = baseline()
    observation["firewall"]["rule_count"] = 3
    forged["firewall"]["rule_count"] = 3
    with pytest.raises(PreconditionError, match="authoritative.*firewall"):
        validate_preconditions(observation, RESOURCE_PLAN, forged)


def test_precondition_rejects_unknown_fields_and_inconsistent_candidate_contract() -> None:
    observation = copy.deepcopy(OBSERVATION)
    observation["unexpected"] = True
    with pytest.raises(PreconditionError, match="unknown"):
        validate_preconditions(observation, RESOURCE_PLAN, baseline())
    observation = copy.deepcopy(OBSERVATION)
    observation["os"]["python_soabi"] = "cpython-311-x86_64-linux-gnu"
    with pytest.raises(PreconditionError, match="SOABI"):
        validate_preconditions(observation, RESOURCE_PLAN, baseline())
    plan = copy.deepcopy(RESOURCE_PLAN)
    plan["container_address"] = "10.0.0.2/24"
    with pytest.raises(PreconditionError, match="container address"):
        validate_preconditions(OBSERVATION, plan, baseline())


def test_precondition_requires_capacity_on_every_target_filesystem_and_all_owned_objects() -> None:
    observation = copy.deepcopy(OBSERVATION)
    observation["capacity"]["filesystems"].pop("/run")
    with pytest.raises(PreconditionError, match="filesystem"):
        validate_preconditions(observation, RESOURCE_PLAN, baseline())
    observation = copy.deepcopy(OBSERVATION)
    observation["existing"]["uids"] = [61212]
    with pytest.raises(PreconditionError, match="uid"):
        validate_preconditions(observation, RESOURCE_PLAN, baseline())
    observation = copy.deepcopy(OBSERVATION)
    observation["firewall"]["semantic_sha256"] = "0" * 64
    with pytest.raises(PreconditionError, match="firewall semantic"):
        validate_preconditions(observation, RESOURCE_PLAN, baseline())


def valid_receipt() -> tuple[dict[str, object], str]:
    report = validate_preconditions(OBSERVATION, RESOURCE_PLAN, baseline())
    return build_precondition_receipt(
        report,
        package_manifest_sha256="1" * 64,
        resource_plan_sha256=sha256_canonical(RESOURCE_PLAN),
        host_identity_sha256=HOST_IDENTITY_SHA256,
        boot_id=BOOT_ID,
        collector_sha256=COLLECTOR_SHA256,
        executor_sha256=EXECUTOR_SHA256,
        package_archive_sha256="6" * 64,
        package_archive_size=123456,
        issued_at_epoch=RECEIPT_NOW,
        ttl_seconds=300,
        nonce=RECEIPT_NONCE,
    )


def valid_authorization(receipt_sha256: str) -> InstallAuthorization:
    return InstallAuthorization.from_mapping(
        {
            "schema": "amn2.spain-install-authorization.v1",
            "mutation_authorized": True,
            "approval_id": "phase12-test-approval",
            "precondition_receipt_sha256": receipt_sha256,
            "package_archive_sha256": "6" * 64,
            "package_archive_size": 123456,
            "package_manifest_sha256": "1" * 64,
            "resource_plan_sha256": sha256_canonical(RESOURCE_PLAN),
            "collector_sha256": COLLECTOR_SHA256,
            "executor_sha256": EXECUTOR_SHA256,
            "run009_evidence_sha256": package_module.RUN009_EVIDENCE_SHA256,
            "fingerprint_array_sha256": package_module.RUN009_FINGERPRINT_SHA256,
            "host_identity_sha256": HOST_IDENTITY_SHA256,
            "endpoint_host": "198.51.100.12",
            "boot_id": BOOT_ID,
            "nonce": RECEIPT_NONCE,
            "approved_at_epoch": RECEIPT_NOW - 1,
            "expires_at_epoch": RECEIPT_NOW + 300,
        }
    )


def test_install_boundary_intent_accepts_only_hashed_host_and_boot_bindings() -> None:
    value = {
        "schema": "amn2.spain-install-boundary-intent.v1",
        "mutation_authorized": True,
        "approval_id": "phase12-test-approval",
        "package_archive_sha256": "6" * 64,
        "package_archive_size": 123456,
        "package_manifest_sha256": "1" * 64,
        "resource_plan_sha256": sha256_canonical(RESOURCE_PLAN),
        "collector_sha256": COLLECTOR_SHA256,
        "executor_sha256": EXECUTOR_SHA256,
        "run009_evidence_sha256": package_module.RUN009_EVIDENCE_SHA256,
        "fingerprint_array_sha256": package_module.RUN009_FINGERPRINT_SHA256,
        "expected_host_identity_sha256": HOST_IDENTITY_SHA256,
        "expected_boot_id_sha256": hashlib.sha256(BOOT_ID.encode("ascii")).hexdigest(),
        "endpoint_host": "198.51.100.12",
        "nonce": RECEIPT_NONCE,
        "approved_at_epoch": RECEIPT_NOW + 1,
        "expires_at_epoch": RECEIPT_NOW + 300,
    }
    intent = InstallBoundaryIntent.from_mapping(value)
    assert intent.expected_host_identity_sha256 == HOST_IDENTITY_SHA256
    assert intent.expected_boot_id_sha256 != BOOT_ID
    value["boot_id"] = BOOT_ID
    with pytest.raises(InstallError, match="schema/result"):
        InstallBoundaryIntent.from_mapping(value)


def test_embedded_run009_baseline_is_hash_bound() -> None:
    baseline = installer_module._embedded_run009_baseline()
    assert baseline["run009_evidence_sha256"] == package_module.DEFAULT_RUN009_EVIDENCE_SHA256
    assert baseline["fingerprint_array_sha256"] == package_module.DEFAULT_RUN009_FINGERPRINT_SHA256
    assert hashlib.sha256(bytes.fromhex(baseline["run009_evidence_hex"])).hexdigest() == (
        package_module.DEFAULT_RUN009_EVIDENCE_SHA256
    )


def test_embedded_resource_plan_is_canonical_and_hash_bound() -> None:
    plan = installer_module._embedded_resource_plan()
    assert plan == RESOURCE_PLAN
    assert sha256_canonical(plan) == sha256_canonical(RESOURCE_PLAN)


def test_executor_rejects_incomplete_install_bound_input_before_mutation() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "phase12_spain_installer.py"), "install-bound"],
        cwd=ROOT,
        input=b"{}\n",
        capture_output=True,
        check=False,
    )
    assert result.returncode == 64
    assert result.stderr.replace(b"\r\n", b"\n") == b"install_bound_inputs_required\n"


def test_executor_accepts_canonical_install_bound_intent_but_is_fail_closed() -> None:
    value = {
        "schema": "amn2.spain-install-boundary-intent.v1",
        "mutation_authorized": True,
        "approval_id": "phase12-test-approval",
        "package_archive_sha256": "6" * 64,
        "package_archive_size": 123456,
        "package_manifest_sha256": "1" * 64,
        "resource_plan_sha256": sha256_canonical(RESOURCE_PLAN),
        "collector_sha256": COLLECTOR_SHA256,
        "executor_sha256": EXECUTOR_SHA256,
        "run009_evidence_sha256": package_module.RUN009_EVIDENCE_SHA256,
        "fingerprint_array_sha256": package_module.RUN009_FINGERPRINT_SHA256,
        "expected_host_identity_sha256": HOST_IDENTITY_SHA256,
        "expected_boot_id_sha256": hashlib.sha256(BOOT_ID.encode("ascii")).hexdigest(),
        "endpoint_host": "198.51.100.12",
        "nonce": RECEIPT_NONCE,
        "approved_at_epoch": RECEIPT_NOW + 1,
        "expires_at_epoch": RECEIPT_NOW + 300,
    }
    payload = canonical_json_bytes(value) + b"\n"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "phase12_spain_installer.py"), "install-bound"],
        cwd=ROOT,
        input=payload,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 78
    assert result.stderr.replace(b"\r\n", b"\n") == b"install_bound_precondition_failed\n"


def test_boot_id_reader_returns_only_valid_uuid_from_exact_file(tmp_path: Path) -> None:
    path = tmp_path / "boot_id"
    path.write_text(BOOT_ID + "\n", encoding="ascii")
    assert installer_module._read_boot_id(path, expected_uid=None) == BOOT_ID
    path.write_text("not-a-boot-id\n", encoding="ascii")
    with pytest.raises(InstallError, match="boot identity"):
        installer_module._read_boot_id(path, expected_uid=None)


def test_install_boundary_intent_builds_authorization_only_for_matching_boot_hash() -> None:
    intent = InstallBoundaryIntent.from_mapping(
        {
            "schema": "amn2.spain-install-boundary-intent.v1",
            "mutation_authorized": True,
            "approval_id": "phase12-test-approval",
            "package_archive_sha256": "6" * 64,
            "package_archive_size": 123456,
            "package_manifest_sha256": "1" * 64,
            "resource_plan_sha256": sha256_canonical(RESOURCE_PLAN),
            "collector_sha256": COLLECTOR_SHA256,
            "executor_sha256": EXECUTOR_SHA256,
            "run009_evidence_sha256": package_module.RUN009_EVIDENCE_SHA256,
            "fingerprint_array_sha256": package_module.RUN009_FINGERPRINT_SHA256,
            "expected_host_identity_sha256": HOST_IDENTITY_SHA256,
            "expected_boot_id_sha256": hashlib.sha256(BOOT_ID.encode("ascii")).hexdigest(),
            "endpoint_host": "198.51.100.12",
            "nonce": RECEIPT_NONCE,
            "approved_at_epoch": RECEIPT_NOW + 1,
            "expires_at_epoch": RECEIPT_NOW + 300,
        }
    )
    authorization = intent.to_authorization("5" * 64, BOOT_ID)
    assert authorization.precondition_receipt_sha256 == "5" * 64
    with pytest.raises(InstallError, match="boot identity"):
        intent.to_authorization("5" * 64, "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def test_in_memory_install_inputs_bind_observation_without_paths() -> None:
    intent = InstallBoundaryIntent.from_mapping(
        {
            "schema": "amn2.spain-install-boundary-intent.v1",
            "mutation_authorized": True,
            "approval_id": "phase12-test-approval",
            "package_archive_sha256": "6" * 64,
            "package_archive_size": 123456,
            "package_manifest_sha256": "1" * 64,
            "resource_plan_sha256": sha256_canonical(RESOURCE_PLAN),
            "collector_sha256": COLLECTOR_SHA256,
            "executor_sha256": EXECUTOR_SHA256,
            "run009_evidence_sha256": package_module.RUN009_EVIDENCE_SHA256,
            "fingerprint_array_sha256": package_module.RUN009_FINGERPRINT_SHA256,
            "expected_host_identity_sha256": HOST_IDENTITY_SHA256,
            "expected_boot_id_sha256": hashlib.sha256(BOOT_ID.encode("ascii")).hexdigest(),
            "endpoint_host": "198.51.100.12",
            "nonce": RECEIPT_NONCE,
            "approved_at_epoch": RECEIPT_NOW + 1,
            "expires_at_epoch": RECEIPT_NOW + 300,
        }
    )
    receipt, detached, baseline_value, authorization = installer_module._build_in_memory_install_inputs(
        intent=intent,
        observation=OBSERVATION,
        host_identity_sha256=HOST_IDENTITY_SHA256,
        boot_id=BOOT_ID,
        resource_plan=RESOURCE_PLAN,
        baseline_value=baseline(),
        now_epoch=RECEIPT_NOW + 2,
    )
    assert receipt["mutation_authorized"] is False
    assert detached == authorization.precondition_receipt_sha256
    assert baseline_value == baseline()


def test_production_install_accepts_in_memory_inputs_without_json_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    receipt, detached = valid_receipt()
    authorization = valid_authorization(detached)
    monkeypatch.setattr(
        installer_module,
        "_read_json_file",
        lambda *_args, **_kwargs: pytest.fail("path-based JSON reader was called"),
    )
    monkeypatch.setattr(
        installer_module,
        "_sha256_regular_file",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("in-memory-path-reached")),
    )
    with pytest.raises(RuntimeError, match="in-memory-path-reached"):
        installer_module._production_install(
            ["/unreadable/receipt", detached, "/unreadable/baseline", "/unused/collector", "/unused/executor", "/unused/package", str(RECEIPT_NOW + 2)],
            authorization_payload=b"",
            expected_uid=None,
            receipt_override=receipt,
            baseline_override=baseline(),
            authorization_override=authorization,
        )


def test_current_evidence_builds_in_memory_install_inputs_before_mutation(monkeypatch: pytest.MonkeyPatch) -> None:
    intent = InstallBoundaryIntent.from_mapping(
        {
            "schema": "amn2.spain-install-boundary-intent.v1", "mutation_authorized": True,
            "approval_id": "phase12-test-approval", "package_archive_sha256": "6" * 64,
            "package_archive_size": 123456, "package_manifest_sha256": "1" * 64,
            "resource_plan_sha256": sha256_canonical(RESOURCE_PLAN), "collector_sha256": COLLECTOR_SHA256,
            "executor_sha256": EXECUTOR_SHA256, "run009_evidence_sha256": package_module.RUN009_EVIDENCE_SHA256,
            "fingerprint_array_sha256": package_module.RUN009_FINGERPRINT_SHA256,
            "expected_host_identity_sha256": HOST_IDENTITY_SHA256,
            "expected_boot_id_sha256": hashlib.sha256(BOOT_ID.encode("ascii")).hexdigest(),
            "endpoint_host": "198.51.100.12", "nonce": RECEIPT_NONCE,
            "approved_at_epoch": RECEIPT_NOW + 1, "expires_at_epoch": RECEIPT_NOW + 300,
        }
    )
    monkeypatch.setattr(installer_module, "observation_from_resource_confirmation_evidence", lambda _value: OBSERVATION)
    monkeypatch.setattr(installer_module, "_embedded_resource_plan", lambda: RESOURCE_PLAN)
    monkeypatch.setattr(installer_module, "_embedded_run009_baseline", baseline)
    receipt, detached, _baseline, authorization = installer_module._build_in_memory_install_inputs_from_evidence(
        intent=intent,
        evidence={"host_identity": {"machine_id_sha256": HOST_IDENTITY_SHA256, "boot_id_sha256": hashlib.sha256(BOOT_ID.encode("ascii")).hexdigest()}},
        boot_id=BOOT_ID,
        now_epoch=RECEIPT_NOW + 2,
    )
    assert receipt["result"] == "passed"
    assert authorization.precondition_receipt_sha256 == detached


def test_install_bound_mode_passes_only_in_memory_inputs_to_production(monkeypatch: pytest.MonkeyPatch) -> None:
    intent = {
        "schema": "amn2.spain-install-boundary-intent.v1", "mutation_authorized": True,
        "approval_id": "phase12-test-approval", "package_archive_sha256": "6" * 64,
        "package_archive_size": 123456, "package_manifest_sha256": "1" * 64,
        "resource_plan_sha256": sha256_canonical(RESOURCE_PLAN), "collector_sha256": COLLECTOR_SHA256,
        "executor_sha256": EXECUTOR_SHA256, "run009_evidence_sha256": package_module.RUN009_EVIDENCE_SHA256,
        "fingerprint_array_sha256": package_module.RUN009_FINGERPRINT_SHA256,
        "expected_host_identity_sha256": HOST_IDENTITY_SHA256,
        "expected_boot_id_sha256": hashlib.sha256(BOOT_ID.encode("ascii")).hexdigest(),
        "endpoint_host": "198.51.100.12", "nonce": RECEIPT_NONCE,
        "approved_at_epoch": RECEIPT_NOW + 1, "expires_at_epoch": RECEIPT_NOW + 300,
    }
    evidence = {"host_identity": {"machine_id_sha256": HOST_IDENTITY_SHA256, "boot_id_sha256": hashlib.sha256(BOOT_ID.encode("ascii")).hexdigest()}}
    monkeypatch.setattr(installer_module, "_read_install_boundary_intent_payload", lambda _payload: InstallBoundaryIntent.from_mapping(intent))
    monkeypatch.setattr(installer_module, "_read_boot_id", lambda **_kwargs: BOOT_ID)
    monkeypatch.setattr(installer_module, "_build_in_memory_install_inputs_from_evidence", lambda **_kwargs: (valid_receipt()[0], valid_receipt()[1], baseline(), valid_authorization(valid_receipt()[1])))
    class FakeObserver:
        MAX_COLLECTOR_BYTES = 1024 * 1024

        def __init__(self, **_kwargs):
            pass

        def collect_evidence(self):
            return evidence

    monkeypatch.setattr(installer_module, "ChecksumBoundResourceObserver", FakeObserver)
    captured = {}
    monkeypatch.setattr(installer_module, "_production_install", lambda args, **kwargs: captured.update(args=args, kwargs=kwargs) or {"result": "passed"})
    assert installer_module.run_production_command(["install-bound"], authorization_payload=b"ignored\n", expected_uid=None) == {"result": "passed"}
    assert captured["kwargs"]["receipt_override"]["result"] == "passed"
    assert captured["kwargs"]["baseline_override"] == baseline()


def test_retained_authorization_tombstone_is_atomic_canonical_and_one_time(tmp_path: Path) -> None:
    store = RetainedAuthorizationStore(
        tmp_path / "phase12-audit",
        expected_uid=None,
    )
    assert not (tmp_path / "phase12-audit").exists()
    authorization = valid_authorization("1" * 64)
    tombstone = store.consume(authorization)
    raw = tombstone.read_bytes()
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    assert json.dumps(
        json.loads(raw), sort_keys=True, separators=(",", ":")
    ).encode("utf-8") + b"\n" == raw
    assert json.loads(raw)["nonce"] == authorization.nonce
    assert json.loads(raw)["package_archive_sha256"] == authorization.package_archive_sha256
    assert json.loads(raw)["endpoint_host"] == authorization.endpoint_host
    with pytest.raises(InstallError, match="already consumed"):
        store.consume(authorization)
    assert tombstone.read_bytes() == raw


def test_retained_authorization_reconciles_deterministic_temp_after_crash(
    tmp_path: Path,
) -> None:
    store = RetainedAuthorizationStore(tmp_path / "phase12-audit", expected_uid=None)
    authorization = valid_authorization("1" * 64)
    tombstone = store.consume(authorization)
    raw = tombstone.read_bytes()
    temporary = tombstone.parent / ("." + tombstone.name + ".tmp")
    os.replace(tombstone, temporary)
    recovered = RetainedAuthorizationStore(
        store.root, expected_uid=None
    ).consume(authorization)
    assert recovered.read_bytes() == raw
    assert not temporary.exists()
    temporary.write_bytes(raw)
    with pytest.raises(InstallError, match="already consumed"):
        RetainedAuthorizationStore(store.root, expected_uid=None).consume(authorization)
    assert not temporary.exists()
    assert recovered.read_bytes() == raw


def test_consumed_tombstone_without_transaction_opens_recovery_not_new_authorization(
    tmp_path: Path,
) -> None:
    (tmp_path / "opt").mkdir()
    store = RetainedAuthorizationStore(tmp_path / "phase12-audit", expected_uid=None)
    authorization = valid_authorization("1" * 64)
    tombstone = store.consume(authorization)
    @contextmanager
    def lock():
        yield

    lease = SharedInstallLockLease(lock)
    with lease.acquire():
        recovered_tombstone, ledger, already_existed = (
            BootstrapTransactionLedger.open_or_create_for_authorization(
                authorization_store=store,
                authorization=authorization,
                package_root=tmp_path / "opt" / "amn2-spain-package",
                lock_lease=lease,
            )
        )
    assert recovered_tombstone == tombstone
    assert already_existed is False
    assert ledger.snapshot()["status"] == "package_root_intent"
    with lease.acquire():
        same_tombstone, reopened, already_existed = (
            BootstrapTransactionLedger.open_or_create_for_authorization(
                authorization_store=store,
                authorization=authorization,
                package_root=tmp_path / "opt" / "amn2-spain-package",
                lock_lease=lease,
            )
        )
    assert same_tombstone == tombstone
    assert already_existed is True
    assert reopened.snapshot() == ledger.snapshot()


def test_bootstrap_transaction_ledger_is_durable_canonical_and_reopenable(
    tmp_path: Path,
) -> None:
    store = RetainedAuthorizationStore(
        tmp_path / "phase12-audit",
        expected_uid=None,
    )
    authorization = valid_authorization("1" * 64)
    tombstone = store.consume(authorization)
    package_root = tmp_path / "opt" / "amn2-spain-package"
    ledger = BootstrapTransactionLedger.create(
        authorization=authorization,
        tombstone=tombstone,
        package_root=package_root,
        expected_uid=None,
    )
    assert ledger.snapshot()["status"] == "package_root_intent"
    ledger.record_package_root((11, 12))
    ledger.record_package_file_intent()
    ledger.record_package_file((13, 14))
    ledger.record_package_bytes(
        observed_size=authorization.package_archive_size,
        observed_sha256=authorization.package_archive_sha256,
    )
    report = verified_package_report()
    ledger.record_package_verified(report)
    inventory = {"manifest.json": {"sha256": "f" * 64, "size": 42, "mode": "0644"}}
    ledger.record_extraction_plan(inventory)
    ledger.record_package_extracted()
    raw = ledger.path.read_bytes()
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    assert json.dumps(
        json.loads(raw), sort_keys=True, separators=(",", ":")
    ).encode("utf-8") + b"\n" == raw
    reopened = BootstrapTransactionLedger.open_existing(
        audit_root=store.root,
        nonce=authorization.nonce,
        expected_uid=None,
    )
    assert reopened.snapshot() == ledger.snapshot()
    assert reopened.snapshot()["package"]["root_identity"] == [11, 12]
    assert reopened.snapshot()["package"]["file_identity"] == [13, 14]
    assert reopened.snapshot()["package"]["extraction_inventory"] == inventory


def test_bootstrap_transaction_ledger_reconciles_atomic_temp_after_crash(
    tmp_path: Path,
) -> None:
    store = RetainedAuthorizationStore(tmp_path / "phase12-audit", expected_uid=None)
    authorization = valid_authorization("1" * 64)
    tombstone = store.consume(authorization)
    ledger = BootstrapTransactionLedger.create(
        authorization=authorization,
        tombstone=tombstone,
        package_root=tmp_path / "opt" / "amn2-spain-package",
        expected_uid=None,
    )
    temporary = ledger.path.parent / ("." + ledger.path.name + ".tmp")
    temporary.write_bytes(ledger.path.read_bytes())
    ledger.path.unlink()
    promoted = BootstrapTransactionLedger.open_existing(
        audit_root=store.root,
        nonce=authorization.nonce,
        expected_uid=None,
    )
    assert promoted.path.is_file()
    assert not temporary.exists()
    temporary.write_bytes(promoted.path.read_bytes())
    reopened = BootstrapTransactionLedger.open_existing(
        audit_root=store.root,
        nonce=authorization.nonce,
        expected_uid=None,
    )
    assert reopened.snapshot() == promoted.snapshot()
    assert not temporary.exists()


@pytest.mark.parametrize(
    "crash_point",
    [
        "root_syscall_before_commit",
        "root_committed",
        "file_syscall_before_commit",
        "file_committed_partial",
        "bytes_committed",
        "extraction_planned_partial",
    ],
)
def test_bootstrap_package_recovery_crash_matrix(
    tmp_path: Path,
    crash_point: str,
) -> None:
    (tmp_path / "opt").mkdir()
    payload = b"approved-package-bytes"
    package_hash = hashlib.sha256(payload).hexdigest()
    authorization = replace(
        valid_authorization("1" * 64),
        package_archive_sha256=package_hash,
        package_archive_size=len(payload),
    )
    store = RetainedAuthorizationStore(tmp_path / "phase12-audit", expected_uid=None)
    tombstone = store.consume(authorization)
    stager = ChecksumBoundPackageStager(
        host_root=tmp_path,
        expected_uid=None,
        expected_gid=None,
    )
    ledger = BootstrapTransactionLedger.create(
        authorization=authorization,
        tombstone=tombstone,
        package_root=stager.package_root,
        expected_uid=None,
    )
    os.mkdir(stager.package_root, 0o700)
    if crash_point != "root_syscall_before_commit":
        root_info = os.lstat(stager.package_root)
        ledger.record_package_root((int(root_info.st_dev), int(root_info.st_ino)))
    if crash_point not in {"root_syscall_before_commit", "root_committed"}:
        ledger.record_package_file_intent()
        descriptor = os.open(stager.package_path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
        try:
            if crash_point != "file_syscall_before_commit":
                file_info = os.fstat(descriptor)
                ledger.record_package_file((int(file_info.st_dev), int(file_info.st_ino)))
                if crash_point == "file_committed_partial":
                    os.write(descriptor, payload[:5])
                else:
                    os.write(descriptor, payload)
                    os.fsync(descriptor)
                    ledger.record_package_bytes(
                        observed_size=len(payload),
                        observed_sha256=package_hash,
                    )
        finally:
            os.close(descriptor)
    if crash_point == "extraction_planned_partial":
        report = PackageVerificationReport.from_mapping(
            {
                "schema": "amn2.spain-package-verification.v1",
                "result": "passed",
                "archive_sha256": package_hash,
                "archive_size": len(payload),
                "manifest_sha256": "1" * 64,
                "resource_plan_sha256": sha256_canonical(RESOURCE_PLAN),
                "run009_evidence_sha256": package_module.RUN009_EVIDENCE_SHA256,
                "fingerprint_array_sha256": package_module.RUN009_FINGERPRINT_SHA256,
                "fingerprint_entry_count": 148,
            }
        )
        ledger.record_package_verified(report)
        expected_content = b"complete-content"
        inventory = {
            "manifest.json": {
                "sha256": hashlib.sha256(expected_content).hexdigest(),
                "size": len(expected_content),
                "mode": "0644",
            }
        }
        ledger.record_extraction_plan(inventory)
        content = stager.package_root / "content"
        content.mkdir(mode=0o700)
        (content / "manifest.json").write_bytes(expected_content[:4])

    @contextmanager
    def lock():
        yield

    lease = SharedInstallLockLease(lock)
    reopened = BootstrapTransactionLedger.open_existing(
        audit_root=store.root,
        nonce=authorization.nonce,
        expected_uid=None,
    )
    with lease.acquire():
        stager.recover_or_rollback(reopened, lease)
    assert reopened.snapshot()["status"] == "rolled_back"
    assert not stager.package_root.exists()
    assert tombstone.is_file()
    assert reopened.path.is_file()


def test_manual_cleanup_removes_only_verified_terminal_package(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "opt").mkdir()
    source = tmp_path / "incoming.tar"
    source.write_bytes(package_tar())
    report = PackageVerificationReport.from_mapping(verify_package(source))
    authorization = replace(
        valid_authorization("1" * 64),
        package_archive_sha256=report.archive_sha256,
        package_archive_size=report.archive_size,
        package_manifest_sha256=report.manifest_sha256,
        resource_plan_sha256=report.resource_plan_sha256,
    )
    store = RetainedAuthorizationStore(tmp_path / "phase12-audit", expected_uid=None)
    stager = ChecksumBoundPackageStager(
        host_root=tmp_path, expected_uid=None, expected_gid=None
    )

    @contextmanager
    def lock():
        yield

    lease = SharedInstallLockLease(lock)
    with lease.acquire():
        _tombstone, transaction, existed = (
            BootstrapTransactionLedger.open_or_create_for_authorization(
                authorization_store=store,
                authorization=authorization,
                package_root=stager.package_root,
                lock_lease=lease,
            )
        )
        assert existed is False
        descriptor = os.open(source, os.O_RDONLY)
        try:
            stager.stage(
                descriptor,
                expected_sha256=report.archive_sha256,
                expected_size=report.archive_size,
                transaction_ledger=transaction,
            )
        finally:
            os.close(descriptor)
        transaction.record_manual_recovery_required()

    monkeypatch.setattr(
        installer_module,
        "_existing_opt_directory_lock",
        lambda _host_root: lock(),
    )
    monkeypatch.setattr(
        installer_module,
        "_host_path",
        lambda _host_root, live_path: store.root
        if live_path == "/var/lib/amn2-spain-phase12-audit"
        else tmp_path / live_path.lstrip("/"),
    )
    monkeypatch.setattr(
        installer_module,
        "_assert_running_executor",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(installer_module.time, "time", lambda: 150)
    intent = {
        "schema": "amn2.spain-manual-cleanup-intent.v1",
        "mutation_authorized": True,
        "approval_id": "test-manual-cleanup",
        "executor_sha256": "2" * 64,
        "nonce": authorization.nonce,
        "approved_at_epoch": 100,
        "expires_at_epoch": 200,
    }

    result = installer_module.run_production_command(
        ["manual-cleanup-bound"],
        authorization_payload=canonical_json_bytes(intent) + b"\n",
        host_root=tmp_path,
        expected_uid=None,
    )

    assert result["schema"] == "amn2.spain-manual-cleanup-receipt.v1"
    assert result["result"] == "passed"
    assert result["approval_id"] == "test-manual-cleanup"
    assert result["nonce"] == authorization.nonce
    assert result["transaction_status"] == "manual_recovery_required"
    assert re.fullmatch(r"[0-9a-f]{64}", result["transaction_sha256"])
    assert not stager.package_root.exists()
    assert transaction.snapshot()["status"] == "manual_recovery_required"
    assert transaction.path.is_file()


def test_terminal_recovery_intent_binds_transaction_capsule_and_docker_tree() -> None:
    payload = {
        "schema": "amn2.spain-terminal-recovery-intent.v1",
        "mutation_authorized": True,
        "approval_id": "test-terminal-recovery",
        "executor_sha256": "2" * 64,
        "nonce": "3" * 64,
        "transaction_sha256": "4" * 64,
        "capsule_sha256": "5" * 64,
        "docker_tree_sha256": "6" * 64,
        "docker_tree_entry_count": 916,
        "docker_tree_total_bytes": 123456,
        "approved_at_epoch": 100,
        "expires_at_epoch": 200,
    }

    intent = installer_module._read_terminal_recovery_intent_payload(
        canonical_json_bytes(payload) + b"\n"
    )

    assert intent.nonce == payload["nonce"]
    assert intent.transaction_sha256 == payload["transaction_sha256"]
    assert intent.capsule_sha256 == payload["capsule_sha256"]
    assert intent.docker_tree_sha256 == payload["docker_tree_sha256"]
    assert intent.docker_tree_entry_count == 916
    assert intent.docker_tree_total_bytes == 123456


def test_terminal_docker_data_root_cleanup_allows_recorded_0710_tree(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "var" / "lib" / "amn2-spain-docker"
    target.mkdir(parents=True)
    (target / "image").mkdir()
    payload = target / "image" / "layer.json"
    payload.write_bytes(b"terminal-docker-layer\n")
    fs = live_backend.SafeFs(root=tmp_path, expected_uid=None, expected_gid=None)
    operation = live_backend.build_directory_action(
        fs, "filesystem_staged", "var/lib/amn2-spain-docker", 0o700
    ).operation
    tree = live_backend._scan_tree(target)
    assert tree is not None
    monkeypatch.setattr(live_backend, "_tree_root_mode", lambda _target: "0710")

    receipt = live_backend.cleanup_terminal_docker_data_root(
        fs=fs,
        relative="var/lib/amn2-spain-docker",
        expected_identity=operation.desired_identity,
        expected_tree_sha256=tree["tree_sha256"],
        expected_tree_entry_count=len(tree["rows"]),
        expected_tree_total_bytes=len(b"terminal-docker-layer\n"),
    )

    assert receipt["tree_sha256"] == tree["tree_sha256"]
    assert receipt["entry_count"] == len(tree["rows"])
    assert not target.exists()


def test_terminal_docker_tree_allows_only_overlay_whiteout_block_device() -> None:
    assert (
        live_backend._terminal_docker_data_root_entry_kind(stat.S_IFBLK, 0)
        == "whiteout"
    )
    with pytest.raises(live_backend.BackendError, match="special file"):
        live_backend._terminal_docker_data_root_entry_kind(stat.S_IFCHR, 0)


def test_terminal_docker_tree_allows_recorded_regular_block_inode() -> None:
    assert (
        live_backend._terminal_docker_data_root_entry_kind(
            stat.S_IFBLK | 0o600, 64770
        )
        == "block"
    )


def test_terminal_docker_tree_requires_single_filesystem_exact_block_inode() -> None:
    entry = types.SimpleNamespace(
        st_mode=stat.S_IFBLK | 0o600,
        st_rdev=64770,
        st_uid=0,
        st_gid=0,
        st_nlink=1,
        st_dev=64770,
    )
    assert (
        live_backend._validate_terminal_docker_data_root_entry(
            entry, root_device=64770
        )
        == "block"
    )
    entry.st_dev = 42
    with pytest.raises(live_backend.BackendError, match="mount collision"):
        live_backend._validate_terminal_docker_data_root_entry(
            entry, root_device=64770
        )


def test_terminal_docker_tree_digest_is_plain_sha256_hex() -> None:
    rows = [{"path": "layer", "type": "dir", "mode": "0700", "uid": 0, "gid": 0}]
    expected = hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert live_backend._terminal_docker_tree_digest(rows) == expected


def test_recovery_capsule_seals_rendered_payloads_and_callback_free_blueprint(
    tmp_path: Path, monkeypatch
) -> None:
    store = RetainedAuthorizationStore(tmp_path / "phase12-audit", expected_uid=None)
    authorization = valid_authorization("1" * 64)
    tombstone = store.consume(authorization)
    ledger = BootstrapTransactionLedger.create(
        authorization=authorization,
        tombstone=tombstone,
        package_root=tmp_path / "opt" / "amn2-spain-package",
        expected_uid=None,
    )
    ledger.record_package_root((11, 12))
    ledger.record_package_file_intent()
    ledger.record_package_file((13, 14))
    ledger.record_package_bytes(
        observed_size=authorization.package_archive_size,
        observed_sha256=authorization.package_archive_sha256,
    )
    ledger.record_package_verified(verified_package_report())
    ledger.record_extraction_plan(
        {"manifest.json": {"sha256": "f" * 64, "size": 42, "mode": "0644"}}
    )
    ledger.record_package_extracted()
    prepared_source = {
        "app.py": {"sha256": "e" * 64, "size": 9, "mode": "0644"}
    }
    ledger.record_source_preparation_plan(
        source_binding_sha256="d" * 64,
        inventory=prepared_source,
    )
    ledger.record_source_prepared()
    blueprint = InstallActionBlueprint.from_mapping(
        {
            "schema": "amn2.spain-install-action-blueprint.v1",
            "assembly_context": {
                "schema": "amn2.spain-production-assembly-context.v1",
                "host_root": "/",
            },
            "actions": [
                {
                    "stage": stage,
                    "owned_object": "logical:" + stage,
                    "desired_identity": hashlib.sha256(stage.encode()).hexdigest(),
                    "builder": "deferred_exact_action",
                    "parameters": {"payload_ref": "capsule:" + stage},
                }
                for stage in live_backend.PRODUCTION_INSTALL_MUTATING_STAGES
            ],
        }
    )
    rendered = {
        "etc/amn2-spain/runtime.env": {
            "payload": b"APP_SECRET_KEY=durable-secret-value-1234567890\n",
            "mode": "0600",
            "uid_role": "root",
            "gid_role": "root",
        },
        "etc/amn2-spain/awgsp0.conf": {
            "payload": b"[Interface]\nPrivateKey = durable-private-key\n",
            "mode": "0600",
            "uid_role": "root",
            "gid_role": "root",
        },
        "etc/amn2-spain/servers.yml": {
            "payload": b"servers: []\n",
            "mode": "0640",
            "uid_role": "root",
            "gid_role": "service",
        },
        "etc/amn2-spain/docker-daemon.json": {
            "payload": b'{"bridge":"none"}\n',
            "mode": "0644",
            "uid_role": "root",
            "gid_role": "root",
        },
        "opt/amn2-spain/runtime/awg-start.sh": {
            "payload": b"#!/bin/sh\nexit 0\n",
            "mode": "0755",
            "uid_role": "root",
            "gid_role": "root",
        },
    }

    @contextmanager
    def rollback_lock():
        yield

    lease = SharedInstallLockLease(rollback_lock)
    original_record_capsule = ledger.record_capsule_committed

    def crash_before_transaction_commit(**_kwargs) -> None:
        raise InstallError("simulated capsule precommit crash")

    monkeypatch.setattr(
        ledger, "record_capsule_committed", crash_before_transaction_commit
    )
    with pytest.raises(InstallError, match="simulated capsule precommit crash"):
        RecoveryCapsuleStore.create(
            transaction_ledger=ledger,
            blueprint=blueprint,
            rendered_payloads=rendered,
            prepared_source_inventory=prepared_source,
            expected_uid=None,
        )
    orphan = store.root / f"recovery-capsule-{authorization.nonce}.json"
    assert orphan.is_file()
    with lease.acquire():
        assert RecoveryCapsuleStore.remove_uncommitted(
            transaction_ledger=ledger,
            lock_lease=lease,
        )
    assert not orphan.exists()

    with pytest.raises(InstallError, match="simulated capsule precommit crash"):
        RecoveryCapsuleStore.create(
            transaction_ledger=ledger,
            blueprint=blueprint,
            rendered_payloads=rendered,
            prepared_source_inventory=prepared_source,
            expected_uid=None,
        )
    temporary_orphan = orphan.parent / ("." + orphan.name + ".tmp")
    os.replace(orphan, temporary_orphan)
    with lease.acquire():
        assert RecoveryCapsuleStore.remove_uncommitted(
            transaction_ledger=ledger,
            lock_lease=lease,
        )
    assert not temporary_orphan.exists()
    monkeypatch.setattr(ledger, "record_capsule_committed", original_record_capsule)

    capsule = RecoveryCapsuleStore.create(
        transaction_ledger=ledger,
        blueprint=blueprint,
        rendered_payloads=rendered,
        prepared_source_inventory=prepared_source,
        expected_uid=None,
    )
    raw = capsule.path.read_bytes()
    assert b"temporary_password" not in raw
    assert b"durable-secret-value" not in raw
    reopened = RecoveryCapsuleStore.open_existing(
        audit_root=store.root,
        nonce=authorization.nonce,
        expected_uid=None,
    )
    assert reopened.sha256 == capsule.sha256
    assert reopened.blueprint.digest == blueprint.digest
    assert reopened.rendered_payloads() == {
        path: spec["payload"] for path, spec in rendered.items()
    }
    assert ledger.snapshot()["status"] == "capsule_committed"
    assert ledger.snapshot()["action_blueprint_sha256"] == blueprint.digest
    assert ledger.snapshot()["recovery_capsule_sha256"] == capsule.sha256
    temporary = capsule.path.parent / ("." + capsule.path.name + ".tmp")
    temporary.write_bytes(capsule.path.read_bytes())
    capsule.path.unlink()
    promoted = RecoveryCapsuleStore.open_existing(
        audit_root=store.root,
        nonce=authorization.nonce,
        expected_uid=None,
    )
    assert promoted.sha256 == capsule.sha256
    assert not temporary.exists()
    temporary.write_bytes(promoted.path.read_bytes())
    stale_reconciled = RecoveryCapsuleStore.open_existing(
        audit_root=store.root,
        nonce=authorization.nonce,
        expected_uid=None,
    )
    assert stale_reconciled.sha256 == capsule.sha256
    assert not temporary.exists()
    ledger.record_rolled_back()
    current_transaction_sha256 = hashlib.sha256(
        BootstrapTransactionLedger._canonical(ledger.snapshot())
    ).hexdigest()
    equality = {
        "schema": "amn2.spain-rollback-equality.v1",
        "result": "passed",
        "baseline_projection_equal": True,
        "firewall_projection_equal": True,
        "listeners_routes_addresses_equal": True,
        "nonce": authorization.nonce,
        "transaction_sha256": current_transaction_sha256,
        "blueprint_sha256": blueprint.digest,
        "foreign_service_fingerprint_before_sha256": "f" * 64,
        "foreign_service_fingerprint_after_sha256": "f" * 64,
        "foreign_service_persistent_equal": True,
        "foreign_service_volatile_before_count": 0,
        "foreign_service_volatile_after_count": 0,
    }
    equality_path = store.root / f"rollback-equality-{authorization.nonce}.json"
    equality_path.write_bytes(
        json.dumps(equality, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
    )
    stale_equality = copy.deepcopy(equality)
    stale_equality["transaction_sha256"] = ledger.snapshot()[
        "previous_state_sha256"
    ]
    equality_path.write_bytes(
        json.dumps(stale_equality, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
        + b"\n"
    )
    with pytest.raises(InstallError, match="equality binding mismatch"):
        finalize_rolled_back_recovery(
            audit_root=store.root,
            nonce=authorization.nonce,
            lock_lease=lease,
            expected_uid=None,
        )
    assert stale_reconciled.path.exists()
    equality_path.write_bytes(
        json.dumps(equality, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
    )
    finalized = finalize_rolled_back_recovery(
        audit_root=store.root,
        nonce=authorization.nonce,
        lock_lease=lease,
        expected_uid=None,
    )
    assert finalized == equality
    assert not stale_reconciled.path.exists()


def test_running_executor_identity_is_the_authorized_file(
    tmp_path: Path, monkeypatch
) -> None:
    executor = (tmp_path / "phase12-executor.pyz").resolve()
    executor.write_bytes(b"authorized executor bytes")
    digest = hashlib.sha256(executor.read_bytes()).hexdigest()
    monkeypatch.setattr(sys, "argv", [str(executor)])
    installer_module._assert_running_executor(
        executor,
        digest,
        expected_uid=None,
    )

    other = (tmp_path / "other-executor.pyz").resolve()
    other.write_bytes(executor.read_bytes())
    monkeypatch.setattr(sys, "argv", [str(other)])
    with pytest.raises(InstallError, match="path mismatch"):
        installer_module._assert_running_executor(
            executor,
            digest,
            expected_uid=None,
        )


def test_uncommitted_capsule_mismatch_enters_manual_recovery(tmp_path: Path) -> None:
    store = RetainedAuthorizationStore(tmp_path / "phase12-audit", expected_uid=None)
    authorization = valid_authorization("1" * 64)
    ledger = BootstrapTransactionLedger.create(
        authorization=authorization,
        tombstone=store.consume(authorization),
        package_root=tmp_path / "opt" / "amn2-spain-package",
        expected_uid=None,
    )
    ledger.record_package_root((11, 12))
    ledger.record_package_file_intent()
    ledger.record_package_file((13, 14))
    ledger.record_package_bytes(
        observed_size=authorization.package_archive_size,
        observed_sha256=authorization.package_archive_sha256,
    )
    ledger.record_package_verified(verified_package_report())
    ledger.record_extraction_plan(
        {"manifest.json": {"sha256": "f" * 64, "size": 42, "mode": "0644"}}
    )
    ledger.record_package_extracted()
    prepared_source = {
        "app.py": {"sha256": "e" * 64, "size": 9, "mode": "0644"}
    }
    ledger.record_source_preparation_plan(
        source_binding_sha256="d" * 64,
        inventory=prepared_source,
    )
    ledger.record_source_prepared()
    orphan = store.root / f"recovery-capsule-{authorization.nonce}.json"
    orphan.write_bytes(b"{}\n")

    @contextmanager
    def rollback_lock():
        yield

    lease = SharedInstallLockLease(rollback_lock)
    with lease.acquire(), pytest.raises(InstallError, match="capsule schema invalid"):
        RecoveryCapsuleStore.remove_uncommitted(
            transaction_ledger=ledger,
            lock_lease=lease,
        )
    assert ledger.snapshot()["status"] == "manual_recovery_required"
    assert orphan.exists()


def test_production_prepare_reconstruct_and_recovery_coordinator_roundtrip(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "opt").mkdir()
    payload = package_tar()
    source = tmp_path / "incoming.tar"
    source.write_bytes(payload)
    report = PackageVerificationReport.from_mapping(verify_package(source))
    authorization = replace(
        valid_authorization("1" * 64),
        package_archive_sha256=report.archive_sha256,
        package_archive_size=report.archive_size,
        package_manifest_sha256=report.manifest_sha256,
        resource_plan_sha256=report.resource_plan_sha256,
    )
    store = RetainedAuthorizationStore(
        tmp_path / "phase12-audit", expected_uid=None
    )
    stager = ChecksumBoundPackageStager(
        host_root=tmp_path,
        expected_uid=None,
        expected_gid=None,
    )

    @contextmanager
    def lock():
        yield

    lease = SharedInstallLockLease(lock)
    with lease.acquire():
        _tombstone, transaction, existed = (
            BootstrapTransactionLedger.open_or_create_for_authorization(
                authorization_store=store,
                authorization=authorization,
                package_root=stager.package_root,
                lock_lease=lease,
            )
        )
        assert existed is False
        descriptor = os.open(source, os.O_RDONLY)
        try:
            staged = stager.stage(
                descriptor,
                expected_sha256=report.archive_sha256,
                expected_size=report.archive_size,
                transaction_ledger=transaction,
            )
        finally:
            os.close(descriptor)
    prepared_payloads = live_backend.PreparedProductionFilesystemPayloads(
        source_tree_identity=live_backend.source_tree_identity(
            staged.prepared_source_path
        ),
        endpoint_host=authorization.endpoint_host,
        rendered_payloads={
            "etc/amn2-spain/runtime.env": b"VPS_APPLY_ENABLED=false\n",
            "etc/amn2-spain/awgsp0.conf": b"[Interface]\nPrivateKey = test\n",
            "etc/amn2-spain/servers.yml": b"servers: []\n",
            "etc/amn2-spain/docker-daemon.json": b"{}\n",
            "opt/amn2-spain/runtime/awg-start.sh": b"#!/bin/sh\n",
        },
        package_bound_payloads={
            "opt/amn2-spain/current/scripts/phase12_spain_network.py": b"# network\n",
            "opt/amn2-spain/current/packaging/phase12-spain/templates/nftables.conf": network_module.NFT_CONFIG.encode(),
        },
    )
    monkeypatch.setattr(
        live_backend,
        "prepare_production_filesystem_payloads",
        lambda **_kwargs: prepared_payloads,
    )
    monkeypatch.setattr(
        live_backend,
        "recover_production_filesystem_payloads",
        lambda **_kwargs: prepared_payloads,
    )
    monkeypatch.setattr(
        live_backend,
        "_authoritative_clean_database_schema_identity",
        lambda _source: "sha256:" + "9" * 64,
    )
    monkeypatch.setattr(
        live_backend,
        "_validate_live_awg_archive_contract",
        lambda *_args, **_kwargs: None,
    )
    if os.name == "nt":
        monkeypatch.setattr(
            live_backend.FixedCommandRunner,
            "_validate_argv",
            staticmethod(lambda _argv: None),
        )
        group_identity = "sha256:" + "7" * 64
        user_identity = "sha256:" + "8" * 64
        monkeypatch.setattr(
            live_backend,
            "build_production_identity_bundle",
            lambda: live_backend.FixedIdentityBundle(
                actions=(
                    live_backend.SystemAction(
                        operation=live_backend.OwnedOperation(
                            "identity_created", "group:amn2-spain", group_identity
                        ),
                        observe_identity=lambda: None,
                        create_exact=lambda: None,
                        remove_exact=lambda _identity: None,
                    ),
                    live_backend.SystemAction(
                        operation=live_backend.OwnedOperation(
                            "identity_created", "user:amn2-spain", user_identity
                        ),
                        observe_identity=lambda: None,
                        create_exact=lambda: None,
                        remove_exact=lambda _identity: None,
                    ),
                ),
                logical_receipt={
                    "group:amn2-spain": group_identity,
                    "gid:61212": group_identity,
                    "user:amn2-spain": user_identity,
                    "uid:61212": user_identity,
                },
            ),
        )
    prepared = prepare_production_installation(
        staged_package=staged,
        transaction_ledger=transaction,
        authorization=authorization,
        host_root=tmp_path,
        expected_uid=None,
    )
    reopened = RecoveryCapsuleStore.open_existing(
        audit_root=store.root,
        nonce=authorization.nonce,
        expected_uid=None,
    )
    reconstructed = reconstruct_production_installation(
        capsule=reopened,
        transaction_ledger=transaction,
        authorization=authorization,
    )
    assert reconstructed.capsule.blueprint.digest == prepared.capsule.blueprint.digest
    assert (
        reconstructed.assembly.action_plan.operations
        == prepared.assembly.action_plan.operations
    )

    def equality(binding):
        return {
            "schema": "amn2.spain-rollback-equality.v1",
            "result": "passed",
            "baseline_projection_equal": True,
            "firewall_projection_equal": True,
            "listeners_routes_addresses_equal": True,
            **binding,
            "foreign_service_fingerprint_before_sha256": "f" * 64,
            "foreign_service_fingerprint_after_sha256": "f" * 64,
            "foreign_service_persistent_equal": True,
            "foreign_service_volatile_before_count": 0,
            "foreign_service_volatile_after_count": 0,
        }

    receipt = ProductionRecoveryCoordinator(
        prepared=reconstructed,
        transaction_ledger=transaction,
        package_stager=stager,
        lock_lease=lease,
        equality_observer=equality,
    ).rollback()
    assert receipt["result"] == "passed"
    assert transaction.snapshot()["status"] == "rolled_back"
    assert not stager.package_root.exists()
    assert not reopened.path.exists()


def test_checksum_bound_stager_streams_and_verifies_the_same_open_file(tmp_path: Path) -> None:
    (tmp_path / "opt").mkdir()
    source = tmp_path / "incoming.tar"
    payload = package_tar()
    source.write_bytes(payload)
    descriptor = os.open(source, os.O_RDONLY)
    try:
        stager = ChecksumBoundPackageStager(
            host_root=tmp_path,
            expected_uid=None,
            expected_gid=None,
        )
        staged = stager.stage(
            descriptor,
            expected_sha256=hashlib.sha256(payload).hexdigest(),
            expected_size=len(payload),
        )
    finally:
        os.close(descriptor)
    assert staged.path.read_bytes() == payload
    assert staged.report.archive_sha256 == hashlib.sha256(payload).hexdigest()
    assert staged.size == len(payload)
    runtime_binding = package_module.plan_verified_runtime_artifacts(
        staged.path.parent / "content"
    )
    assert runtime_binding == {
        "schema": "amn2.spain-runtime-artifact-binding.v1",
        "source": {
            "path": f"payload/source/amn2-runtime-source-{SOURCE_COMMIT}.tar.gz",
            "sha256": hashlib.sha256(SOURCE_ARCHIVE).hexdigest(),
            "size": len(SOURCE_ARCHIVE),
            "commit": SOURCE_COMMIT,
        },
        "wheelhouse": {
            "path": "payload/python/wheelhouse",
            "inventory_path": "payload/python/wheelhouse/wheelhouse-inventory.json",
            "inventory_sha256": hashlib.sha256(WHEEL_INVENTORY).hexdigest(),
            "lock_path": "payload/python/wheelhouse/requirements-linux-x86_64-py312.lock",
            "lock_sha256": hashlib.sha256(WHEEL_LOCK).hexdigest(),
        },
        "docker": {
            "path": "payload/docker/docker-synthetic-test-linux-x86_64.tgz",
            "sha256": hashlib.sha256(DOCKER_ARCHIVE).hexdigest(),
            "size": len(DOCKER_ARCHIVE),
        },
        "awg_image": {
            "path": "payload/awg/amneziawg-go-test-linux-amd64.tar",
            "sha256": hashlib.sha256(AWG_ARCHIVE).hexdigest(),
            "size": len(AWG_ARCHIVE),
            "reference": AWG_REFERENCE,
            "index_digest": AWG_INDEX_DIGEST,
            "platform_digest": AWG_PLATFORM_DIGEST,
            "config_digest": AWG_CONFIG_DIGEST,
        },
    }
    assert (
        staged.path.parent / "content" / "scripts" / "phase12_spain_installer.py"
    ).is_file()
    collision_descriptor = os.open(source, os.O_RDONLY)
    try:
        with pytest.raises(InstallError, match="collision"):
            stager.stage(
                collision_descriptor,
                expected_sha256=staged.report.archive_sha256,
                expected_size=len(payload),
            )
    finally:
        os.close(collision_descriptor)
    stager.rollback(staged)
    assert not (tmp_path / "opt" / "amn2-spain-package").exists()


def test_critical_binding_revalidates_current_observation_without_raw_snapshot_equality(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed = copy.deepcopy(OBSERVATION)

    class FakeObserver:
        def collect_evidence(self):
            return {
                "host_identity": {
                    "machine_id_sha256": HOST_IDENTITY_SHA256,
                    "boot_id_sha256": hashlib.sha256(BOOT_ID.encode("ascii")).hexdigest(),
                }
            }

    captured: dict[str, object] = {}
    monkeypatch.setattr(
        installer_module,
        "observation_from_resource_confirmation_evidence",
        lambda _evidence: observed,
    )
    monkeypatch.setattr(
        installer_module,
        "validate_preconditions",
        lambda observation, resource_plan, baseline_value: captured.update(
            observation=observation,
            resource_plan=resource_plan,
            baseline=baseline_value,
        ) or {"result": "passed"},
    )
    binding, returned = installer_module._critical_resource_binding(
        FakeObserver(),
        valid_authorization("1" * 64),
        resource_plan=RESOURCE_PLAN,
        baseline=baseline(),
    )
    assert binding == {
        "host_identity_sha256": HOST_IDENTITY_SHA256,
        "boot_id": BOOT_ID,
    }
    assert returned == observed
    assert captured == {
        "observation": observed,
        "resource_plan": RESOURCE_PLAN,
        "baseline": baseline(),
    }


def test_checksum_bound_bootstrap_accepts_approval_before_in_memory_receipt_and_binds_report(tmp_path: Path) -> None:
    (tmp_path / "opt").mkdir()
    source = tmp_path / "incoming.tar"
    payload = package_tar()
    source.write_bytes(payload)
    package_hash = hashlib.sha256(payload).hexdigest()
    package_report = PackageVerificationReport.from_mapping(verify_package(source))
    receipt, detached = build_precondition_receipt(
        validate_preconditions(OBSERVATION, RESOURCE_PLAN, baseline()),
        resource_plan_sha256=sha256_canonical(RESOURCE_PLAN),
        host_identity_sha256=HOST_IDENTITY_SHA256,
        boot_id=BOOT_ID,
        collector_sha256=COLLECTOR_SHA256,
        executor_sha256=EXECUTOR_SHA256,
        package_archive_sha256=package_hash,
        package_archive_size=len(payload),
        package_manifest_sha256=package_report.manifest_sha256,
        issued_at_epoch=RECEIPT_NOW,
        ttl_seconds=300,
        nonce=RECEIPT_NONCE,
    )
    authorization = replace(
        valid_authorization(detached),
        package_archive_sha256=package_hash,
        package_archive_size=len(payload),
        package_manifest_sha256=package_report.manifest_sha256,
        resource_plan_sha256=package_report.resource_plan_sha256,
        approved_at_epoch=RECEIPT_NOW - 1,
        expires_at_epoch=RECEIPT_NOW + 299,
    )
    store = RetainedAuthorizationStore(tmp_path / "phase12-audit", expected_uid=None)
    stager = ChecksumBoundPackageStager(
        host_root=tmp_path,
        expected_uid=None,
        expected_gid=None,
    )
    backend = observed_backend(
        critical_observation={
            "host_identity_sha256": HOST_IDENTITY_SHA256,
            "boot_id": BOOT_ID,
        }
    )
    captured_bootstrap: list[object] = []

    def lock():
        return backend.install_lock()

    def append_stage(stage: str) -> None:
        assert (tmp_path / "phase12-audit" / f"authorization-{RECEIPT_NONCE}.json").is_file()
        backend.append_journal(stage)

    lock_lease = SharedInstallLockLease(lock)
    bootstrap = ChecksumBoundBootstrap(
        authorization=authorization,
        receipt=receipt,
        detached_receipt_sha256=detached,
        now_epoch=RECEIPT_NOW + 2,
        lock_lease=lock_lease,
        critical_observer=backend.observe_critical,
        authorization_store=store,
        package_stager=stager,
        append_stage=append_stage,
    )
    assert not (tmp_path / "phase12-audit").exists()
    descriptor = os.open(source, os.O_RDONLY)
    try:
        result = bootstrap.execute(
            descriptor,
            continuation=lambda bootstrap_result: (
                captured_bootstrap.append(bootstrap_result),
                InstallStateMachine(backend, RESOURCE_PLAN, baseline()).install_after_bootstrap(
                    bootstrap_result,
                    authorization=authorization,
                ),
            )[1],
        )
    finally:
        os.close(descriptor)
    assert result["result"] == "passed"
    assert captured_bootstrap[0].staged_package.report == package_report
    assert captured_bootstrap[0].tombstone.is_file()
    assert captured_bootstrap[0].transaction_ledger.snapshot()["status"] == "source_prepared"
    assert backend.journal == list(InstallStateMachine.STAGES)
    with lock_lease.acquire():
        backend.rollback()
        stager.recover_or_rollback(
            captured_bootstrap[0].transaction_ledger,
            lock_lease,
        )
    assert captured_bootstrap[0].transaction_ledger.snapshot()["status"] == "rolled_back"
    mismatch_descriptor = os.open(source, os.O_RDONLY)
    try:
        with pytest.raises(InstallError, match="checksum"):
            stager.stage(
                mismatch_descriptor,
                expected_sha256="0" * 64,
                expected_size=len(payload),
            )
    finally:
        os.close(mismatch_descriptor)
    assert not (tmp_path / "opt" / "amn2-spain-package").exists()


def test_installer_binds_authorized_collector_executor_and_receipt_evidence() -> None:
    receipt, _detached = valid_receipt()
    receipt["run009_evidence_sha256"] = "f" * 64
    forged_detached = hashlib.sha256(canonical_json_bytes(receipt)).hexdigest()
    backend = observed_backend()
    with pytest.raises(InstallError, match="binding"):
        InstallStateMachine(backend, RESOURCE_PLAN, baseline()).install(
            receipt,
            forged_detached,
            package_manifest_sha256="1" * 64,
            package_report=verified_package_report(),
            authorization=valid_authorization(forged_detached),
            now_epoch=RECEIPT_NOW + 2,
        )
    assert backend.mutations == []


def test_state_machine_accepts_approval_before_in_memory_receipt() -> None:
    receipt, detached = valid_receipt()
    authorization = replace(
        valid_authorization(detached),
        approved_at_epoch=RECEIPT_NOW - 1,
        expires_at_epoch=RECEIPT_NOW + 299,
    )
    backend = observed_backend(
        critical_observation={
            "host_identity_sha256": HOST_IDENTITY_SHA256,
            "boot_id": BOOT_ID,
            "observation_sha256": receipt["observation_sha256"],
        }
    )
    result = InstallStateMachine(backend, RESOURCE_PLAN, baseline()).install(
        receipt,
        detached,
        package_manifest_sha256="1" * 64,
        package_report=verified_package_report(),
        authorization=authorization,
        now_epoch=RECEIPT_NOW + 2,
    )
    assert result["result"] == "passed"


def test_readonly_receipt_is_not_authorization_and_approval_is_one_time_under_lock() -> None:
    receipt, detached = valid_receipt()
    backend = observed_backend(
        critical_observation={
            "host_identity_sha256": HOST_IDENTITY_SHA256,
            "boot_id": BOOT_ID,
            "observation_sha256": receipt["observation_sha256"],
        }
    )
    machine = InstallStateMachine(backend, RESOURCE_PLAN, baseline())
    with pytest.raises(InstallError, match="authorization"):
        machine.install(
            receipt,
            detached,
            package_manifest_sha256="1" * 64,
            package_report=verified_package_report(),
            authorization=None,
            now_epoch=RECEIPT_NOW + 2,
        )
    authorization = valid_authorization(detached)
    machine.install(
        receipt,
        detached,
        package_manifest_sha256="1" * 64,
        package_report=verified_package_report(),
        authorization=authorization,
        now_epoch=RECEIPT_NOW + 2,
    )
    second = observed_backend(
        critical_observation={
            "host_identity_sha256": HOST_IDENTITY_SHA256,
            "boot_id": BOOT_ID,
            "observation_sha256": receipt["observation_sha256"],
        },
        consumed_nonces=backend.consumed_nonces,
    )
    with pytest.raises(InstallError, match="consumed"):
        InstallStateMachine(second, RESOURCE_PLAN, baseline()).install(
            receipt,
            detached,
            package_manifest_sha256="1" * 64,
            package_report=verified_package_report(),
            authorization=authorization,
            now_epoch=RECEIPT_NOW + 3,
        )
    assert second.mutations == []


def test_install_authorization_reconstructs_only_from_exact_retained_tombstone() -> None:
    authorization = valid_authorization("1" * 64)
    assert InstallAuthorization.from_tombstone_mapping(
        authorization.tombstone_mapping()
    ) == authorization
    forged = authorization.tombstone_mapping()
    forged["mutation_authorized"] = False
    with pytest.raises(InstallError, match="tombstone"):
        InstallAuthorization.from_tombstone_mapping(forged)


def verified_package_report() -> PackageVerificationReport:
    return PackageVerificationReport.from_mapping(
        {
            "schema": "amn2.spain-package-verification.v1",
            "result": "passed",
            "archive_sha256": "6" * 64,
            "archive_size": 123456,
            "manifest_sha256": "1" * 64,
            "resource_plan_sha256": sha256_canonical(RESOURCE_PLAN),
            "run009_evidence_sha256": package_module.RUN009_EVIDENCE_SHA256,
            "fingerprint_array_sha256": package_module.RUN009_FINGERPRINT_SHA256,
            "fingerprint_entry_count": 148,
        }
    )


def observed_backend(**kwargs) -> MemoryBackend:
    if "critical_observation" not in kwargs:
        report = validate_preconditions(OBSERVATION, RESOURCE_PLAN, baseline())
        kwargs["critical_observation"] = {
            "host_identity_sha256": HOST_IDENTITY_SHA256,
            "boot_id": BOOT_ID,
            "observation_sha256": report["observation_sha256"],
        }
    current_nft = copy.deepcopy(baseline()["firewall"]["nft_json"])
    current_nft["nftables"].extend(
        copy.deepcopy(network_module.expected_table_document()["nftables"])
    )
    return MemoryBackend(
        systemd_projection=copy.deepcopy(baseline()["systemd_projection"]),
        foreign_firewall=current_nft,
        **kwargs,
    )


def test_production_backend_applies_only_immutable_plan_stage_operations() -> None:
    state: dict[str, str] = {}

    def action(stage: str, owned_object: str, digit: str) -> live_backend.SystemAction:
        identity = "sha256:" + digit * 64
        operation = live_backend.OwnedOperation(stage, owned_object, identity)
        return live_backend.SystemAction(
            operation=operation,
            observe_identity=lambda: state.get(owned_object),
            create_exact=lambda: state.__setitem__(owned_object, identity),
            remove_exact=lambda expected: (
                state.pop(owned_object)
                if state.get(owned_object) == expected
                else (_ for _ in ()).throw(live_backend.BackendError("CAS drift"))
            ),
        )

    actions = {
        "identity": action("identity_created", "group:amn2-spain", "1"),
        "filesystem": action("filesystem_staged", "runtime:docker-static", "2"),
        "secrets": action("secrets_configs_rendered", "secret:app-runtime", "3"),
        "database": action("clean_db_initialized", "database:/var/lib/amn2-spain/amn2.sqlite3", "4"),
        "unit": action("units_installed", "file:/etc/systemd/system/amn2-spain-network.service", "5"),
        "docker": action("docker_started", "systemd-active:amn2-spain-docker.service", "6"),
        "image": action("awg_image_loaded", "image:awg", "7"),
        "container": action("network_container_started", "container:amn2-spain-awg", "8"),
        "network_enabled": action("host_network_applied", "systemd-enabled:amn2-spain-network.service", "9"),
        "network_active": action("host_network_applied", "systemd-active:amn2-spain-network.service", "a"),
        "network_composite": action("host_network_applied", "network-contour:amn2-spain", "b"),
        "web": action("web_started", "systemd-active:amn2-spain-web.service", "c"),
    }
    plan = live_backend.compose_production_install_actions(
        identity_actions=(actions["identity"],),
        filesystem_actions=(actions["filesystem"], actions["secrets"]),
        database_action=actions["database"],
        systemd_actions=(
            actions["unit"], actions["docker"], actions["network_enabled"],
            actions["network_active"], actions["web"],
        ),
        docker_actions=(actions["image"], actions["container"]),
        network_service_contour_action=actions["network_composite"],
    )
    adapter = live_backend.SystemOwnedAdapter(
        actions={action.operation.owned_object: action for action in plan.actions}
    )
    mutation_ledger = live_backend.MutationLedger(
        allowed_objects={operation.owned_object for operation in plan.operations}
    )
    linux = live_backend.LinuxBackend(adapter=adapter, ledger=mutation_ledger)
    stage_contract = {
        stage: ["logical:" + stage]
        for stage in live_backend.PRODUCTION_INSTALL_MUTATING_STAGES
    }
    blueprint = InstallActionBlueprint.from_production_action_plan(
        plan,
        assembly_context={
            "schema": "amn2.spain-production-assembly-context.v1",
            "host_root": "/",
            "package_content_root": "/opt/amn2-spain-package/content",
        },
        operation_logical_contract={
            operation.owned_object: "logical:" + operation.stage
            for operation in plan.operations
        },
    )
    assert blueprint.assembly_context == {
        "schema": "amn2.spain-production-assembly-context.v1",
        "host_root": "/",
        "package_content_root": "/opt/amn2-spain-package/content",
    }
    assert InstallActionBlueprint.from_mapping(blueprint.mapping()).digest == blueprint.digest
    journal: list[str] = []
    consumed: list[str] = []

    @contextmanager
    def lock():
        yield

    lock_lease = SharedInstallLockLease(lock)
    backend = ProductionBackend(
        action_plan=plan,
        blueprint=blueprint,
        linux_backend=linux,
        stage_object_contract=stage_contract,
        append_stage=journal.append,
        lock_lease=lock_lease,
        critical_observer=lambda: {"host_identity_sha256": "1" * 64},
        authorization_consumer=consumed.append,
        postinstall_observer=lambda: {"runtime": {}},
    )
    with lock_lease.acquire():
        backend.append_journal("adopted-shared-lease")
        with pytest.raises(InstallError, match="already held"):
            with backend.install_lock():
                pass
    with backend.install_lock():
        backend.consume_authorization("2" * 64)
        with pytest.raises(InstallError, match="stage object contract"):
            backend.apply_stage("identity_created", ["forged"])
        assert state == {}
        for stage in live_backend.PRODUCTION_INSTALL_MUTATING_STAGES:
            backend.apply_stage(stage, stage_contract[stage])
    assert consumed == ["2" * 64]
    assert journal == ["adopted-shared-lease"]
    assert set(backend.created_objects) == {
        operation.owned_object for operation in plan.operations
    }
    with backend.install_lock():
        backend.rollback()
    assert state == {}


def test_production_postinstall_observer_proves_clean_runtime_without_awg_restart(
    tmp_path: Path, monkeypatch
) -> None:
    database = tmp_path / "amn2.sqlite3"
    import sqlite3

    connection = sqlite3.connect(database)
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY)")
    connection.commit()
    connection.close()
    runtime_env = tmp_path / "runtime.env"
    runtime_env.write_text("VPS_APPLY_ENABLED=false\n", encoding="utf-8")
    resource_observer = object.__new__(installer_module.ChecksumBoundResourceObserver)
    observation = copy.deepcopy(OBSERVATION)
    observation["existing"] = {
        "paths": [
            value for value in RESOURCE_PLAN["resources"]["paths"]
            if value != "/run/amn2-spain-docker"
        ],
        "retained_paths": RESOURCE_PLAN["resources"]["retained_paths"],
        "users": RESOURCE_PLAN["resources"]["users"],
        "groups": RESOURCE_PLAN["resources"]["groups"],
        "units": RESOURCE_PLAN["resources"]["units"],
        "containers": [],
        "networks": [],
        "bridges": RESOURCE_PLAN["resources"]["bridges"],
        "interfaces": RESOURCE_PLAN["resources"]["interfaces"],
        "uids": RESOURCE_PLAN["resources"]["uids"],
        "gids": RESOURCE_PLAN["resources"]["gids"],
        "sockets": RESOURCE_PLAN["resources"]["sockets"],
        "runtime_dirs": RESOURCE_PLAN["resources"]["runtime_dirs"],
        "firewall_objects": ["inet:amn2_spain"],
        "owned_routes": ["10.212.12.0/24"],
        "sysctls": [],
    }
    observation["listeners"] = sorted(
        set(OBSERVATION["listeners"]) | set(RESOURCE_PLAN["listeners"])
    )
    observation["addresses"] = sorted(
        set(OBSERVATION["addresses"])
        | {"172.29.251.1/28", "10.212.12.1/24"}
    )
    observation["routes"] = sorted(
        set(OBSERVATION["routes"])
        | {"172.29.251.0/28", "10.212.12.0/24"}
    )
    observation["systemd_projection"] = [
        *copy.deepcopy(OBSERVATION["systemd_projection"]),
        {
            "name_sha256": hashlib.sha256(
                b"amn2-spain-web.service"
            ).hexdigest()
        },
    ]
    monkeypatch.setattr(
        resource_observer,
        "collect_observation",
        lambda: copy.deepcopy(observation),
    )
    called: list[tuple[str, ...]] = []

    def runner(argv, **_kwargs):
        called.append(argv)
        if "inspect" in argv:
            if "network" in argv:
                return b"amn2-spain-net\n"
            return b"0\n"
        if "exec" in argv:
            return b"\n"
        if "--property=UnitFileState" in argv:
            return b"disabled\n"
        if "--property=ActiveState" in argv:
            return b"inactive\n"
        raise AssertionError(argv)

    observer = ProductionPostinstallObserver(
        resource_observer=resource_observer,
        resource_plan=RESOURCE_PLAN,
        baseline_observation=OBSERVATION,
        created_objects=lambda: ["unit:amn2-spain-web.service"],
        runner=runner,
        database_path=database,
        runtime_env_path=runtime_env,
    )
    result = observer.observe()
    assert result["runtime"]["peer_count"] == 0
    assert result["runtime"]["container_restart_count"] == 0
    assert result["systemd_projection"] == OBSERVATION["systemd_projection"]
    assert result["unexpected_objects"] == []
    assert all("restart" not in item and "stop" not in item for item in called)

    def peers_present(argv, **kwargs):
        if "exec" in argv:
            return b"peer-public-key\n"
        return runner(argv, **kwargs)

    observer.runner = peers_present
    with pytest.raises(InstallError, match="runtime state"):
        observer.observe()

    def restarted(argv, **kwargs):
        if "--format={{.RestartCount}}" in argv:
            return b"1\n"
        return runner(argv, **kwargs)

    observer.runner = restarted
    with pytest.raises(InstallError, match="runtime state"):
        observer.observe()


def test_shared_install_lock_lease_is_single_owner_and_non_reentrant() -> None:
    events: list[str] = []

    @contextmanager
    def lock():
        events.append("enter")
        try:
            yield
        finally:
            events.append("exit")

    lease = SharedInstallLockLease(lock)
    with pytest.raises(InstallError, match="not held"):
        lease.assert_held()
    with lease.acquire():
        lease.assert_held()
        with pytest.raises(InstallError, match="already held"):
            with lease.acquire():
                pass
        lease.assert_held()
    with pytest.raises(InstallError, match="not held"):
        lease.assert_held()
    assert events == ["enter", "exit"]


def test_state_machine_requires_immutable_verified_package_and_real_observation() -> None:
    receipt, detached = valid_receipt()
    backend = observed_backend(runtime_overrides={"peer_count": 1})
    machine = InstallStateMachine(backend, RESOURCE_PLAN, baseline())
    with pytest.raises(InstallError, match="verified package report"):
        machine.install(
            receipt,
            detached,
            package_manifest_sha256="1" * 64,
            package_report=None,
            authorization=valid_authorization(detached),
            now_epoch=RECEIPT_NOW + 2,
        )
    assert backend.mutations == []
    with pytest.raises(InstallError, match="peer_count"):
        machine.install(
            receipt,
            detached,
            package_manifest_sha256="1" * 64,
            package_report=verified_package_report(),
            authorization=valid_authorization(detached),
            now_epoch=RECEIPT_NOW + 2,
        )
    assert backend.journal[-1] == "rolled_back"


def test_installer_refuses_missing_or_tampered_precondition_receipt() -> None:
    backend = observed_backend()
    machine = InstallStateMachine(backend, RESOURCE_PLAN, baseline())
    receipt, detached = valid_receipt()
    with pytest.raises(InstallError, match="precondition receipt"):
        machine.install(None, None, package_manifest_sha256="1" * 64, package_report=verified_package_report(), authorization=valid_authorization(detached), now_epoch=RECEIPT_NOW + 2)
    receipt["observation_sha256"] = "0" * 64
    with pytest.raises(InstallError, match="precondition receipt"):
        machine.install(receipt, detached, package_manifest_sha256="1" * 64, package_report=verified_package_report(), authorization=valid_authorization(detached), now_epoch=RECEIPT_NOW + 2)
    assert backend.mutations == []


def test_installer_journals_monotonic_stages_and_safe_runtime_result() -> None:
    backend = observed_backend()
    receipt, detached = valid_receipt()
    machine = InstallStateMachine(backend, RESOURCE_PLAN, baseline())
    report = machine.install(receipt, detached, package_manifest_sha256="1" * 64, package_report=verified_package_report(), authorization=valid_authorization(detached), now_epoch=RECEIPT_NOW + 2)
    assert report["stage"] == "postinstall_verified"
    assert backend.journal == list(InstallStateMachine.STAGES)
    assert backend.runtime_state == RESOURCE_PLAN["runtime_invariants"]
    assert backend.runtime_state["peer_count"] == 0
    assert backend.runtime_state["vps_apply_enabled"] is False
    assert backend.runtime_state["bot_enabled"] is False
    assert backend.runtime_state["bot_running"] is False
    assert backend.runtime_state["web_listener"] == "127.0.0.1:3031"


def test_installer_stage_order_respects_docker_and_network_dependencies() -> None:
    assert InstallStateMachine.STAGES == (
        "authorization_validated",
        "critical_recheck_passed",
        "authorization_consumed",
        "package_staged",
        "package_verified_remote",
        "identity_created",
        "filesystem_staged",
        "secrets_configs_rendered",
        "clean_db_initialized",
        "units_installed",
        "docker_started",
        "awg_image_loaded",
        "network_container_started",
        "host_network_applied",
        "web_started",
        "postinstall_verified",
    )
    stages = InstallStateMachine(observed_backend(), RESOURCE_PLAN, baseline())._stage_objects()
    assert stages["host_network_applied"][0] == "network-contour:amn2-spain"
    assert "network-contour:amn2-spain" not in {
        item for stage, items in stages.items() if stage != "host_network_applied" for item in items
    }


def test_installer_stage_delta_includes_every_plan_owned_runtime_object() -> None:
    stages = InstallStateMachine(observed_backend(), RESOURCE_PLAN, baseline())._stage_objects()
    flattened = {owned for values in stages.values() for owned in values}
    expected = {
        "uid:61212",
        "gid:61212",
        "socket:/run/amn2-spain-docker/docker.sock",
        "runtime-dir:/run/amn2-spain-docker",
        "runtime:docker-static",
        "image:sha256:0f21ddfb3313affe3a336693886ced918301335815e4b7db3d15b5a0a5da6afb",
        "unit:amn2-spain-network.service",
        "firewall:inet:amn2_spain:chain:prerouting",
        "route:10.212.12.0/24|via|172.29.251.2|dev|amn2spbr0",
        "sysctl:net.ipv4.ip_forward=1",
        "listener:udp|wildcard|30001",
        "listener:tcp|loopback|3031",
    }
    assert expected <= flattened


@pytest.mark.parametrize("fault_stage", list(InstallStateMachine.MUTATING_STAGES))
def test_fault_injection_rolls_back_only_owned_objects_in_reverse_order(fault_stage: str) -> None:
    backend = observed_backend(fault_stage=fault_stage, preexisting={"unrelated:service"})
    receipt, detached = valid_receipt()
    machine = InstallStateMachine(backend, RESOURCE_PLAN, baseline())
    with pytest.raises(InstallError, match=fault_stage):
        machine.install(receipt, detached, package_manifest_sha256="1" * 64, package_report=verified_package_report(), authorization=valid_authorization(detached), now_epoch=RECEIPT_NOW + 2)
    assert backend.rollback_objects == list(reversed(backend.created_objects))
    assert backend.objects == {"unrelated:service"}
    assert "unrelated:service" not in backend.rollback_objects
    assert backend.journal[-1] == "rolled_back"


def test_installer_refuses_preexisting_collision_without_claiming_it() -> None:
    backend = observed_backend(preexisting={"path:/opt/amn2-spain"})
    receipt, detached = valid_receipt()
    machine = InstallStateMachine(backend, RESOURCE_PLAN, baseline())
    with pytest.raises(InstallError, match="collision"):
        machine.install(receipt, detached, package_manifest_sha256="1" * 64, package_report=verified_package_report(), authorization=valid_authorization(detached), now_epoch=RECEIPT_NOW + 2)
    assert backend.mutations == []


def append_bootstrap_journal_stages(ledger: FsyncLedger) -> None:
    for stage in InstallStateMachine.STAGES[:5]:
        ledger.append_stage(stage)


def test_fsync_ledger_is_monotonic_and_rolls_back_exact_owned_objects(tmp_path: Path) -> None:
    allowlist = {
        "path:/opt/amn2-spain",
        "group:amn2-spain",
        "user:amn2-spain",
    }
    ledger = FsyncLedger(
        tmp_path / "ledger.jsonl", InstallStateMachine.STAGES, sealed_allowlist=allowlist
    )
    append_bootstrap_journal_stages(ledger)
    ledger.record_pending("identity_created", "group:amn2-spain", "gid:202")
    ledger.record_created("identity_created", "group:amn2-spain", "gid:202")
    ledger.record_pending("identity_created", "user:amn2-spain", "uid:203")
    ledger.record_created("identity_created", "user:amn2-spain", "uid:203")
    ledger.append_stage("identity_created")
    ledger.record_pending("filesystem_staged", "path:/opt/amn2-spain", "inode:101")
    ledger.record_created("filesystem_staged", "path:/opt/amn2-spain", "inode:101")
    ledger.append_stage("filesystem_staged")
    removed: list[str] = []
    identities = {
        "path:/opt/amn2-spain": "inode:101",
        "group:amn2-spain": "gid:202",
        "user:amn2-spain": "uid:203",
    }
    ledger.rollback(
        lambda owned: identities.get(owned),
        lambda owned, identity: (removed.append(owned), identities.pop(owned)),
    )
    assert removed == ["path:/opt/amn2-spain", "user:amn2-spain", "group:amn2-spain"]
    assert ledger.events()[-1] == {"event": "stage", "stage": "rolled_back"}
    ledger.rollback(lambda owned: identities.get(owned), lambda *_: pytest.fail("double remove"))
    with pytest.raises(InstallError, match="monotonic"):
        ledger.append_stage("authorization_validated")


def test_fsync_ledger_rejects_forged_object_and_cas_identity_drift(tmp_path: Path) -> None:
    ledger = FsyncLedger(
        tmp_path / "ledger.jsonl",
        InstallStateMachine.STAGES,
        sealed_allowlist={"path:/opt/amn2-spain"},
    )
    append_bootstrap_journal_stages(ledger)
    ledger.append_stage("identity_created")
    with pytest.raises(InstallError, match="sealed allowlist"):
        ledger.record_pending("filesystem_staged", "path:/etc/unrelated", "inode:9")
    ledger.record_pending("filesystem_staged", "path:/opt/amn2-spain", "inode:1")
    ledger.record_created("filesystem_staged", "path:/opt/amn2-spain", "inode:1")
    with pytest.raises(InstallError, match="identity drift"):
        ledger.rollback(lambda _owned: "inode:2", lambda *_: None)


def test_fsync_ledger_adopts_exact_pending_object_after_crash_before_commit(tmp_path: Path) -> None:
    owned = "path:/opt/amn2-spain"
    ledger = FsyncLedger(
        tmp_path / "ledger.jsonl",
        InstallStateMachine.STAGES,
        sealed_allowlist={owned},
    )
    append_bootstrap_journal_stages(ledger)
    ledger.append_stage("identity_created")
    ledger.record_pending("filesystem_staged", owned, "sha256:" + "1" * 64)
    identities = {owned: "sha256:" + "1" * 64}
    removed: list[str] = []
    ledger.rollback(
        lambda value: identities.get(value),
        lambda value, _identity: (removed.append(value), identities.pop(value)),
    )
    assert removed == [owned]
    object_events = [event for event in ledger.events() if event.get("event") == "object"]
    assert [event["state"] for event in object_events] == ["pending", "created", "removed"]
    assert all(event["expected_identity"] == "sha256:" + "1" * 64 for event in object_events)
    ledger.rollback(lambda value: identities.get(value), lambda *_: pytest.fail("double remove"))


def test_fsync_ledger_handles_truncated_tail_and_exclusive_lock(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    ledger = FsyncLedger(path, InstallStateMachine.STAGES, sealed_allowlist=set())
    ledger.append_stage("authorization_validated")
    with path.open("ab") as output:
        output.write(b'{"event":"stage"')
    ledger.append_stage("critical_recheck_passed")
    assert ledger.events()[-1] == {"event": "stage", "stage": "critical_recheck_passed"}
    other = FsyncLedger(path, InstallStateMachine.STAGES, sealed_allowlist=set())
    with ledger.exclusive():
        with pytest.raises(InstallError, match="lock"):
            other.append_stage("authorization_consumed")


def test_tracked_resource_plan_units_and_templates_are_install_safe() -> None:
    plan = json.loads((TRACKED_PACKAGE_ROOT / "resource-plan.json").read_text(encoding="utf-8"))
    assert plan == RESOURCE_PLAN
    schema = json.loads(
        (TRACKED_PACKAGE_ROOT / "package-manifest.schema.json").read_text(encoding="utf-8")
    )
    assert schema["$id"] == "amn2.spain-install-package.v1"
    assert schema["additionalProperties"] is False
    assert "index_digest" in schema["properties"]["awg_image"]["required"]
    assert schema["properties"]["awg_image"]["properties"]["index_digest"]["pattern"] == (
        "^sha256:[0-9a-f]{64}$"
    )

    docker_unit = (TRACKED_PACKAGE_ROOT / "units" / "amn2-spain-docker.service").read_text(
        encoding="utf-8"
    )
    assert "--config-file=/etc/amn2-spain/docker-daemon.json" in docker_unit
    assert "--host=tcp" not in docker_unit
    assert "/usr/bin/dockerd" not in docker_unit
    assert "Delegate=yes" in docker_unit
    for duplicated_flag in (
        "--host=",
        "--data-root=",
        "--exec-root=/run/amn2-spain-docker/exec",
        "--pidfile=/run/amn2-spain-docker/docker.pid",
        "--bridge=none",
        "--iptables=false",
        "--ip6tables=false",
        "--ip-forward=false",
        "--ip-masq=false",
        "--userland-proxy=false",
    ):
        assert duplicated_flag not in docker_unit
    assert (
        "Environment=PATH=/opt/amn2-spain/docker/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        in docker_unit
    )
    assert "NoNewPrivileges=true" not in docker_unit
    assert "ProtectSystem=strict" not in docker_unit
    docker_daemon = json.loads(
        (TRACKED_PACKAGE_ROOT / "templates" / "docker-daemon.json").read_text(
            encoding="utf-8"
        )
    )
    assert docker_daemon["group"] == "root"

    web_unit = (TRACKED_PACKAGE_ROOT / "units" / "amn2-spain-web.service").read_text(
        encoding="utf-8"
    )
    assert (
        "ExecStart=/usr/bin/python3 -B -m app.cli web serve --host 127.0.0.1 --port 3031"
        in web_unit
    )
    bot_unit = (TRACKED_PACKAGE_ROOT / "units" / "amn2-spain-bot.service").read_text(
        encoding="utf-8"
    )
    assert "Type=notify" in bot_unit
    assert "NotifyAccess=main" in bot_unit
    assert "RuntimeDirectory=amn2-spain-bot" in bot_unit
    assert "ExecStart=/usr/bin/python3 -B -m app.main" in bot_unit
    assert "ConditionPathExists=/etc/amn2-spain/bot-enabled" in bot_unit
    assert "WantedBy=" not in bot_unit

    environment = (TRACKED_PACKAGE_ROOT / "templates" / "runtime.env").read_text(
        encoding="utf-8"
    )
    assert "VPS_APPLY_ENABLED=false" in environment
    assert "WEB_ADMIN_ENABLED=true" in environment
    assert "WEB_ADMIN_HOST=127.0.0.1" in environment
    assert "WEB_ADMIN_PORT=3031" in environment
    assert "WEB_ADMIN_SESSION_COOKIE_SECURE=false" in environment
    assert "APP_LOG_LEVEL=INFO" in environment
    assert "APP_LOG_PATH=/var/lib/amn2-spain/logs/app.log" in environment
    assert not any(line.startswith("LOG_LEVEL=") for line in environment.splitlines())
    assert "CLIENT_CONFIG_TEMPLATE_DIR=/var/lib/amn2-spain/config-templates" in environment
    assert "SERVER_NAME=spain" in environment
    assert "VPN_SERVER_RUNTIME=docker" in environment
    assert "DEFAULT_VPN_NETWORK_CIDR=10.212.12.0/24" in environment
    assert "VPN_PORT_MIN=30001" in environment
    assert "VPN_PORT_MAX=30001" in environment
    assert "CLIENT_ALLOWED_IPS=0.0.0.0/0" in environment
    assert "TELEGRAM_RUNTIME_LOCK_PATH=/run/amn2-spain-bot/polling.lock" in environment
    assert "PYTHONPATH=/opt/amn2-spain/runtime/site-packages:/opt/amn2-spain/runtime/source" in environment
    assert "SERVER_CONFIG_PATH=/etc/amn2-spain/servers.yml" in environment
    assert "SERVERS_CONFIG_PATH=" not in environment
    assert "TELEGRAM_BOT_TOKEN=__AMN2_GENERATED_TELEGRAM_BOT_TOKEN__" in environment
    assert "APP_SECRET_KEY=__AMN2_GENERATED_APP_SECRET_KEY__" in environment
    assert (
        "WEB_ADMIN_PASSWORD_HASH=__AMN2_GENERATED_WEB_ADMIN_PASSWORD_HASH__" in environment
    )
    assert (
        "WEB_ADMIN_SESSION_SECRET=__AMN2_GENERATED_WEB_ADMIN_SESSION_SECRET__"
        in environment
    )
    assert "CHANGE_ME" not in environment

    awg = (TRACKED_PACKAGE_ROOT / "templates" / "awgsp0.conf").read_text(encoding="utf-8")
    assert "ListenPort = 30001" in awg
    assert "PrivateKey = __AMN2_GENERATED_SERVER_PRIVATE_KEY__" in awg
    assert "S3 = 20" in awg
    assert "S4 = 23" in awg
    assert "[Peer]" not in awg


def test_tracked_remote_primitives_forbid_package_managers_and_network_downloads() -> None:
    paths = [
        ROOT / "scripts" / "phase12_spain_package.py",
        ROOT / "scripts" / "phase12_spain_precondition.py",
        ROOT / "scripts" / "phase12_spain_installer.py",
        REMOTE_EXECUTOR,
    ]
    combined = "\n".join(path.read_text(encoding="utf-8").casefold() for path in paths)
    for forbidden in ("curl ", "wget ", "apt-get ", "apt ", "dnf ", "yum ", "pip install", "venv"):
        assert forbidden not in combined


def test_projection_helpers_allow_only_closed_owned_firewall_delta() -> None:
    assert_systemd_projection(
        baseline()["systemd_projection"], OBSERVATION["systemd_projection"]
    )
    assert_systemd_projection(
        baseline()["systemd_projection"], OBSERVATION["systemd_projection"][:-1]
    )
    changed_foreign = copy.deepcopy(OBSERVATION["systemd_projection"])
    changed_foreign[0]["restart_count"] = 1
    assert_systemd_projection(baseline()["systemd_projection"], changed_foreign)
    changed_foreign[0]["active_state"] = "inactive:dead"
    with pytest.raises(InstallError, match="systemd projection"):
        assert_systemd_projection(baseline()["systemd_projection"], changed_foreign)
    baseline_nft = OBSERVATION["firewall"]["nft_json"]
    expected_owned = network_module.expected_table_document()
    current_nft = {
        "nftables": list(baseline_nft["nftables"])
        + copy.deepcopy(expected_owned["nftables"])
    }
    assert_firewall_projection(
        baseline_nft,
        current_nft,
        sealed_namespace=RESOURCE_PLAN["firewall_namespace"],
        expected_owned_nft=expected_owned,
    )
    owned_injection = copy.deepcopy(current_nft)
    owned_injection["nftables"].append(
        {
            "rule": {
                "family": "inet",
                "table": "amn2_spain",
                "chain": "forward",
                "comment": "amn2_spain:extra-but-prefixed",
                "expr": [{"accept": None}],
            }
        }
    )
    with pytest.raises(InstallError, match="exact owned"):
        assert_firewall_projection(
            baseline_nft,
            owned_injection,
            sealed_namespace=RESOURCE_PLAN["firewall_namespace"],
            expected_owned_nft=expected_owned,
        )
    foreign_injection = copy.deepcopy(current_nft)
    foreign_injection["nftables"].append(
        {
            "rule": {
                "family": "inet",
                "table": "unrelated",
                "chain": "input",
                "comment": "amn2_spain:injected",
                "expr": [{"accept": None}],
            }
        }
    )
    with pytest.raises(InstallError, match="firewall projection"):
        assert_firewall_projection(
            baseline_nft,
            foreign_injection,
            sealed_namespace=RESOURCE_PLAN["firewall_namespace"],
            expected_owned_nft=expected_owned,
        )


def test_rollback_equality_receipt_requires_exact_foreign_fingerprint_equality() -> None:
    fingerprint = "f" * 64
    receipt = {
        "schema": "amn2.spain-rollback-equality.v1",
        "result": "passed",
        "baseline_projection_equal": True,
        "firewall_projection_equal": True,
        "listeners_routes_addresses_equal": True,
        "nonce": "a" * 64,
        "transaction_sha256": "b" * 64,
        "blueprint_sha256": "c" * 64,
        "foreign_service_fingerprint_before_sha256": fingerprint,
        "foreign_service_fingerprint_after_sha256": fingerprint,
        "foreign_service_persistent_equal": True,
        "foreign_service_volatile_before_count": 0,
        "foreign_service_volatile_after_count": 0,
    }
    assert validate_rollback_equality_receipt(receipt) == receipt
    receipt["foreign_service_fingerprint_after_sha256"] = "e" * 64
    with pytest.raises(InstallError, match="foreign service"):
        validate_rollback_equality_receipt(receipt)


def test_rollback_equality_observer_compares_stable_foreign_projections() -> None:
    before = copy.deepcopy(OBSERVATION)
    after = copy.deepcopy(OBSERVATION)
    binding = {
        "nonce": "a" * 64,
        "transaction_sha256": "b" * 64,
        "blueprint_sha256": "c" * 64,
    }
    receipt = build_rollback_equality_receipt(
        baseline_observation=before,
        current_observation=after,
        binding=binding,
    )
    assert receipt["result"] == "passed"
    assert (
        receipt["foreign_service_fingerprint_before_sha256"]
        == receipt["foreign_service_fingerprint_after_sha256"]
    )
    after["systemd_projection"][0]["restart_count"] = 1
    restart_receipt = build_rollback_equality_receipt(
        baseline_observation=before,
        current_observation=after,
        binding=binding,
    )
    assert restart_receipt["foreign_service_persistent_equal"] is True
    after["systemd_projection"][0]["active_state"] = "inactive:dead"
    with pytest.raises(InstallError, match="persistent foreign projection"):
        build_rollback_equality_receipt(
            baseline_observation=before,
            current_observation=after,
            binding=binding,
        )
    after["listeners"].append("tcp|wildcard|9999")
    with pytest.raises(InstallError, match="listeners/routes/addresses"):
        build_rollback_equality_receipt(
            baseline_observation=before,
            current_observation=after,
            binding=binding,
        )


def test_rollback_equality_receipt_records_volatile_foreign_entries() -> None:
    before = copy.deepcopy(OBSERVATION)
    after = copy.deepcopy(OBSERVATION)
    after["systemd_projection"].append({"name_sha256": "f" * 64})
    receipt = build_rollback_equality_receipt(
        baseline_observation=before,
        current_observation=after,
        binding={"nonce": "a" * 64, "transaction_sha256": "b" * 64, "blueprint_sha256": "c" * 64},
    )
    assert receipt["foreign_service_persistent_equal"] is True
    assert receipt["foreign_service_volatile_after_count"] == 1


def test_terminal_recovery_equality_allows_only_owned_inventory_removal() -> None:
    before = copy.deepcopy(OBSERVATION)
    before["existing"] = {
        "paths": [
            "/opt/amn2-spain",
            "/etc/amn2-spain",
            "/var/lib/amn2-spain",
            "/var/lib/amn2-spain-docker",
        ],
        "retained_paths": ["/var/lib/amn2-spain-phase12-audit"],
        "users": ["amn2-spain"],
        "groups": ["amn2-spain"],
        "units": ["amn2-spain-web.service"],
        "containers": [],
        "networks": [],
        "bridges": [],
        "interfaces": [],
        "uids": [61212],
        "gids": [61212],
        "sockets": [],
        "runtime_dirs": [],
        "firewall_objects": [],
        "owned_routes": [],
        "sysctls": [],
    }
    after = copy.deepcopy(OBSERVATION)
    after["existing"]["retained_paths"] = ["/var/lib/amn2-spain-phase12-audit"]
    binding = {
        "nonce": "a" * 64,
        "transaction_sha256": "b" * 64,
        "blueprint_sha256": "c" * 64,
    }

    receipt = build_terminal_recovery_equality_receipt(
        baseline_observation=before,
        current_observation=after,
        binding=binding,
    )

    assert receipt["result"] == "passed"
    after["firewall"]["rules_sha256"] = "e" * 64
    raw_counter_receipt = build_terminal_recovery_equality_receipt(
        baseline_observation=before,
        current_observation=after,
        binding=binding,
    )
    assert raw_counter_receipt["firewall_projection_equal"] is True
    after["firewall"]["semantic_sha256"] = "f" * 64
    with pytest.raises(InstallError, match="terminal recovery firewall semantic"):
        build_terminal_recovery_equality_receipt(
            baseline_observation=before,
            current_observation=after,
            binding=binding,
        )
    after["firewall"] = copy.deepcopy(before["firewall"])
    after["systemd_projection"][0]["active_state"] = "inactive:dead"
    with pytest.raises(InstallError, match="persistent foreign projection"):
        build_terminal_recovery_equality_receipt(
            baseline_observation=before,
            current_observation=after,
            binding=binding,
        )


def test_terminal_recovery_resume_ignores_removed_events_outside_exact_contour() -> None:
    class Ledger:
        def event_for(self, name: str) -> dict[str, str] | None:
            return {
                "owned:docker-root": {"event": "removed"},
                "already-rolled-back": {"event": "removed"},
            }.get(name)

    assert installer_module._classify_terminal_recovery_ledger(
        ledger=Ledger(),
        blueprint={"owned:docker-root": {}, "already-rolled-back": {}},
        expected_objects={"owned:docker-root"},
    ) == "verified_previously_removed_owned_objects"


def test_terminal_recovery_receipt_mode_is_verify_only(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}
    sentinel = object()
    monkeypatch.setattr(
        installer_module,
        "_read_terminal_recovery_intent_payload",
        lambda _payload: sentinel,
    )
    monkeypatch.setattr(
        installer_module,
        "_production_terminal_recovery_bound",
        lambda intent, **kwargs: captured.update(intent=intent, **kwargs) or {"result": "passed"},
    )

    assert installer_module.run_production_command(
        ["terminal-recovery-receipt-bound"],
        authorization_payload=b"{}",
    ) == {"result": "passed"}
    assert captured["intent"] is sentinel
    assert captured["receipt_only"] is True


def test_remote_executor_is_closed_mode_wrapper_without_network_fetches() -> None:
    source = REMOTE_EXECUTOR.read_text(encoding="utf-8")
    assert "set -Eeuo pipefail" in source
    assert 'install|install-bound|manual-cleanup|manual-cleanup-bound|terminal-recovery-bound|terminal-recovery-receipt-bound|recover|rollback|verify)' in source
    assert 'readonly EXECUTOR_BUNDLE="/root/amn2-spain-phase12-executor.pyz"' in source
    assert 'exec "$PYTHON_BIN" -I -B "$EXECUTOR_BUNDLE"' in source
    assert "PYTHONPATH" not in source
    lowered = source.casefold()
    for forbidden in ("curl ", "wget ", "apt ", "apt-get ", "dnf ", "yum ", ":latest"):
        assert forbidden not in lowered


def test_remote_executor_rejects_unknown_mode_without_mutation() -> None:
    bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    if not bash.exists():
        pytest.skip("Git Bash unavailable")
    result = subprocess.run(
        [str(bash), str(REMOTE_EXECUTOR), "unexpected"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 64
    assert "unsupported_mode" in result.stderr


def test_install_ssh_runner_binds_only_artifacts_and_in_memory_install_intent() -> None:
    source = INSTALL_SSH_RUNNER.read_text(encoding="utf-8")
    assert '$expectedPackageSha = "DAA40D48B88B2AFB0FC4A57A1E5313D8B2851BCED89AEC655B628CB859AEA585"' in source
    assert '$expectedManifestSha = "F13A7C4A02F7B9233629AD06DF06265BB1FC84B69478B4BDB03F1484515C79F2"' in source
    assert '$expectedExecutorSha = "07E066F15FA671DBF9B9F74ECAD2373C00D4A7551972E316F51BCB8265B630CC"' in source
    assert '$expectedExecutorBytes = 145791' in source
    assert 'phase12-spain-install-boundary-bounded-load-v15-20260724' in source
    assert "StrictHostKeyChecking=yes" in source
    assert "install-bound" in source
    assert "Invoke-BoundedSshUpload" in source
    assert "scp.exe" not in source
    assert 'cat > "$destination"' in source
    assert '"-p", "22"' in source
    assert "ConnectTimeout=20" in source
    assert "ServerAliveInterval=15" in source
    assert "ServerAliveCountMax=4" in source
    assert "$uploadTimeoutMilliseconds = 900000" in source
    assert "Approved artifact upload exceeded 900 seconds." in source
    assert "UPLOAD TIMEOUT SECONDS 900" in source
    assert '"/root/amn2-spain-phase12-install-a.tar"' in source
    assert '"/root/amn2-spain-phase12-executor-a.pyz"' in source
    assert "CopyToAsync" in source
    assert "[void][Threading.Tasks.Task]::WaitAll" in source
    assert "installResult.Stderr" in source
    assert "remoteArtifactsReady" in source
    assert "[Convert]::ToHexString" not in source
    assert "[A-Z0-9_]+" in source
    assert "resource-confirmation-evidence" not in source
    assert "precondition-receipt" not in source
    assert "baseline" not in source


def test_ssh_data_path_diagnostic_runner_is_pinned_bounded_and_nonpersistent() -> None:
    source = SSH_DATA_PATH_DIAGNOSTIC_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert "Compression=no" in source
    assert 'exec /bin/cat > /dev/null' in source
    assert "16777216" in source
    assert "Invoke-BoundedSshProbe" in source
    assert "Approved data-path diagnostic exceeded 60 seconds." in source
    assert "RedirectStandardInput" in source
    assert "RedirectStandardOutput" in source
    assert "RedirectStandardError" in source
    assert "CopyToAsync" in source
    assert "$probeResults = @(Invoke-BoundedSshProbe" in source
    assert "Approved data-path diagnostic result invalid." in source
    assert "scp.exe" not in source
    assert "install-bound" not in source
    assert "manual-cleanup" not in source
    assert "terminal-recovery" not in source
    assert "/root/amn2-spain" not in source


def test_manual_cleanup_ssh_runner_is_executor_only_and_stdin_bound() -> None:
    source = CLEANUP_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert "manual-cleanup-bound" in source
    assert "scp.exe" in source
    assert '"-P", "22"' in source
    assert "CopyToAsync" in source
    assert "manual-cleanup-intent.v1" in source
    assert "/opt/amn2-spain-package" in source
    assert "phase12-install-a.tar" not in source
    assert "install-bound" not in source


def test_terminal_recovery_ssh_runner_is_executor_only_and_tree_bound() -> None:
    source = TERMINAL_RECOVERY_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert "terminal-recovery-receipt-bound" in source
    assert "terminal-recovery-intent.v1" in source
    assert "docker_tree_sha256" in source
    assert "VERIFY RECORDED REMOVAL ONLY" in source
    assert "CopyToAsync" in source
    assert "phase12-install-a.tar" not in source
    assert "install-bound" not in source


def test_current_manual_cleanup_runner_is_remote_executor_pinned_and_action_bound() -> None:
    source = CURRENT_MANUAL_CLEANUP_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert "ConnectTimeout=20" in source
    assert "ServerAliveInterval=15" in source
    assert "ServerAliveCountMax=4" in source
    assert "manual-cleanup-bound" in source
    assert "terminal-recovery-bound" not in source
    assert "scp.exe" not in source
    assert "Remote current manual cleanup executor checksum mismatch." in source
    assert '$expectedNonce = "1d7511ed51cb2d908b329386dcb8eb7fd5c727abc93346452ed35a66342204b4"' in source
    assert '$expectedTransactionSha = "08f1c860652fb561e3c1c921756549d3aaccaf86543ceb6c7fea4ef845930883"' in source
    assert "REMOVE ONLY VERIFIED RETAINED PACKAGE TREE" in source


def test_current_terminal_recovery_runner_is_remote_executor_pinned_and_action_bound() -> None:
    source = CURRENT_TERMINAL_RECOVERY_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert "ConnectTimeout=20" in source
    assert "ServerAliveInterval=15" in source
    assert "ServerAliveCountMax=4" in source
    assert "terminal-recovery-bound" in source
    assert "terminal-recovery-receipt-bound" not in source
    assert "scp.exe" not in source
    assert "Remote current terminal recovery executor checksum mismatch." in source
    assert '$expectedNonce = "1d7511ed51cb2d908b329386dcb8eb7fd5c727abc93346452ed35a66342204b4"' in source
    assert '$expectedTransactionSha = "08f1c860652fb561e3c1c921756549d3aaccaf86543ceb6c7fea4ef845930883"' in source
    assert '$expectedCapsuleSha = "2e146365a29c89e9466a8e54e174a3d4d2c969b2bfaeedc9531a59ec4f756a18"' in source
    assert '$expectedDockerTreeSha = "6051924206a20bab41384c9def68cb7d09ab02756515a0dcc05c7e290e3f3248"' in source
    assert "ROLLBACK EXACT OWNED CURRENT TRANSACTION" in source
    assert "VERIFY FOREIGN EQUALITY" in source


def test_transaction_2f647_manual_cleanup_runner_is_pinned_and_action_bound() -> None:
    assert TRANSACTION_2F647_MANUAL_CLEANUP_SSH_RUNNER.exists()
    source = TRANSACTION_2F647_MANUAL_CLEANUP_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert "manual-cleanup-bound" in source
    assert "terminal-recovery-bound" not in source
    assert '$expectedExecutorSha = "D792D9CABB6B7FE3FABD7BC4B07D833D27549FE1484900770B54214D38FEAC29"' in source
    assert '$expectedNonce = "2f647f44976725fc569b045f923452b523db75c5edc86d651197875e1be887ed"' in source
    assert '$expectedTransactionSha = "44ed0fc0273854100a6cccdf44230081ea90051b29c94d64bffe221614337f28"' in source
    assert "REMOVE ONLY VERIFIED RETAINED PACKAGE TREE" in source


def test_transaction_2f647_terminal_recovery_runner_is_pinned_and_action_bound() -> None:
    assert TRANSACTION_2F647_TERMINAL_RECOVERY_SSH_RUNNER.exists()
    source = TRANSACTION_2F647_TERMINAL_RECOVERY_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert "terminal-recovery-bound" in source
    assert "terminal-recovery-receipt-bound" not in source
    assert '$expectedExecutorSha = "D792D9CABB6B7FE3FABD7BC4B07D833D27549FE1484900770B54214D38FEAC29"' in source
    assert '$expectedNonce = "2f647f44976725fc569b045f923452b523db75c5edc86d651197875e1be887ed"' in source
    assert '$expectedTransactionSha = "44ed0fc0273854100a6cccdf44230081ea90051b29c94d64bffe221614337f28"' in source
    assert '$expectedCapsuleSha = "b0470aa26f836b78cfbc961bda7d12457e08bebe9cf981e1df404093cc42fb93"' in source
    assert '$expectedDockerTreeSha = "41b0b3b43e5177a03ad7e75e2efa3655d4464988485b576a87803ae2564bea65"' in source
    assert "$expectedDockerTreeEntries = 916" in source
    assert "$expectedDockerTreeBytes = 41902300" in source
    assert "$expectedBlockRdev = 64770" in source
    assert "stat -c %d /var/lib/amn2-spain-docker" in source
    assert "ROLLBACK EXACT OWNED CURRENT TRANSACTION" in source
    assert "VERIFY FOREIGN EQUALITY" in source


def test_transaction_2315_recovery_runners_are_pinned_and_action_bound() -> None:
    cleanup = TRANSACTION_2315_MANUAL_CLEANUP_SSH_RUNNER.read_text(encoding="utf-8")
    terminal = TRANSACTION_2315_TERMINAL_RECOVERY_SSH_RUNNER.read_text(encoding="utf-8")
    nonce = "2315caba94df97a4a34c665fb58401f0bd56e1721a7cea59af20c38f23b8046c"
    transaction = "e4507cd1483d9b6aeb89da825ffed9b18bba8239ce7aacbba97e1b9e36aedc74"
    capsule = "e9e2b849a8afa296cad980396f5bec81dc5fe15913a99d5df738fa15cb4cef12"
    tree = "067776d5cff3b28c7404ff9f9a6494ea2bd7c7fb473b410dcc62f37282a419e4"
    for source in (cleanup, terminal):
        assert "StrictHostKeyChecking=yes" in source
        assert '$expectedExecutorSha = "D792D9CABB6B7FE3FABD7BC4B07D833D27549FE1484900770B54214D38FEAC29"' in source
        assert f'$expectedNonce = "{nonce}"' in source
        assert f'$expectedTransactionSha = "{transaction}"' in source
        assert "scp.exe" not in source
        assert "install-bound" not in source
    assert "manual-cleanup-bound" in cleanup
    assert "terminal-recovery-bound" not in cleanup
    assert "REMOVE ONLY VERIFIED RETAINED PACKAGE TREE" in cleanup
    assert "terminal-recovery-bound" in terminal
    assert f'$expectedCapsuleSha = "{capsule}"' in terminal
    assert f'$expectedDockerTreeSha = "{tree}"' in terminal
    assert "$expectedDockerTreeEntries = 2268" in terminal
    assert "$expectedDockerTreeBytes = 42532407" in terminal
    assert "$expectedRegularBlockDevices = 2" in terminal
    assert "$expectedRegularBlockRdev = 64770" in terminal
    assert "$expectedWhiteoutCount = 0" in terminal
    assert "ROLLBACK EXACT OWNED CURRENT TRANSACTION" in terminal
    assert "VERIFY FOREIGN EQUALITY" in terminal


def test_transaction_544db_recovery_runners_are_pinned_and_action_bound() -> None:
    cleanup = TRANSACTION_544DB_MANUAL_CLEANUP_SSH_RUNNER.read_text(encoding="utf-8")
    terminal = TRANSACTION_544DB_TERMINAL_RECOVERY_SSH_RUNNER.read_text(encoding="utf-8")
    nonce = "544db99ee620bc0139914c75db98c9a2e16797aadffa6c106923825fc17a6b54"
    transaction = "89a9bec68c026ff6aa2865ab65f1a91333046e458746499ee29738b3a663c5cf"
    capsule = "6411c3a47d8055cf70dc4a2082d4fd23752c94698f6dcfde96da4ff3026af723"
    tree = "0a086299782791b40464cf51087c9e72cbfbac254200cd4e39191f395e06c331"
    for source in (cleanup, terminal):
        assert "StrictHostKeyChecking=yes" in source
        assert '$expectedExecutorSha = "D792D9CABB6B7FE3FABD7BC4B07D833D27549FE1484900770B54214D38FEAC29"' in source
        assert f'$expectedNonce = "{nonce}"' in source
        assert f'$expectedTransactionSha = "{transaction}"' in source
        assert "scp.exe" not in source
        assert "install-bound" not in source
    assert "manual-cleanup-bound" in cleanup
    assert "terminal-recovery-bound" not in cleanup
    assert "REMOVE ONLY VERIFIED RETAINED PACKAGE TREE" in cleanup
    assert "terminal-recovery-bound" in terminal
    assert f'$expectedCapsuleSha = "{capsule}"' in terminal
    assert f'$expectedDockerTreeSha = "{tree}"' in terminal
    assert "$expectedDockerTreeEntries = 2268" in terminal
    assert "$expectedDockerTreeBytes = 42532407" in terminal
    assert "$expectedRegularBlockDevices = 2" in terminal
    assert "$expectedRegularBlockRdev = 64770" in terminal
    assert "$expectedWhiteoutCount = 0" in terminal
    assert "ROOT MODE 0710" in terminal
    assert "ROLLBACK EXACT OWNED CURRENT TRANSACTION" in terminal
    assert "VERIFY FOREIGN EQUALITY" in terminal


def test_standalone_executor_bundle_build_is_deterministic_and_fail_closed(
    tmp_path: Path,
) -> None:
    first = tmp_path / "executor-a.pyz"
    second = tmp_path / "executor-b.pyz"
    first_receipt = executor_bundle_module.build_executor_bundle(
        workspace_root=ROOT,
        output_path=first,
    )
    second_receipt = executor_bundle_module.build_executor_bundle(
        workspace_root=ROOT,
        output_path=second,
    )
    assert first.read_bytes() == second.read_bytes()
    assert first_receipt == second_receipt
    assert first_receipt["sha256"] == hashlib.sha256(first.read_bytes()).hexdigest()
    with zipfile.ZipFile(first) as archive:
        assert set(archive.namelist()) == {
            "__main__.py",
            "scripts/__init__.py",
            "scripts/phase12_spain_installer.py",
            "scripts/phase12_spain_live_backend.py",
            "scripts/phase12_spain_network.py",
            "scripts/phase12_spain_package.py",
            "scripts/phase12_spain_precondition.py",
            "scripts/phase12_spain_resource_confirmation_remote.sh",
            "scripts/phase12_spain_run009_preflight_evidence.json",
            "scripts/phase12_spain_resource_plan.json",
        }
    result = subprocess.run(
        [sys.executable, str(first), "unexpected"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 64
    assert result.stderr == "unsupported_mode\n"


def test_python_entrypoints_reject_incomplete_live_inputs_without_mutation() -> None:
    precondition = subprocess.run(
        ["python", str(ROOT / "scripts" / "phase12_spain_precondition.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert precondition.returncode == 64
    assert "precondition_inputs_required" in precondition.stderr
    unwired_precondition = subprocess.run(
        [
            "python",
            str(ROOT / "scripts" / "phase12_spain_precondition.py"),
            "validate",
            "observation.json",
            "resource-plan.json",
            "baseline.json",
            "1" * 64,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert unwired_precondition.returncode == 78
    assert "live_collector_not_assembled" in unwired_precondition.stderr
    installer = subprocess.run(
        ["python", str(ROOT / "scripts" / "phase12_spain_installer.py"), "install"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert installer.returncode == 64
    assert "install_inputs_required" in installer.stderr
