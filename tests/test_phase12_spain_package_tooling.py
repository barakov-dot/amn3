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
TRANSACTION_89C835_BUNDLED_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_89c835_bundled_recovery_ssh_runner.ps1"
)

TRANSACTION_9D2D0D_BUNDLED_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_9d2d0d_bundled_recovery_ssh_runner.ps1"
)


TRANSACTION_AD0E8B_BUNDLED_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_ad0e8b_bundled_recovery_ssh_runner.ps1"
)

TRANSACTION_8C0EB7_BUNDLED_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_8c0eb7_bundled_recovery_ssh_runner.ps1"
)
TRANSACTION_84AA1F_BUNDLED_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_84aa1f_bundled_recovery_ssh_runner.ps1"
)
TRANSACTION_EAF145_BUNDLED_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_eaf145_bundled_recovery_ssh_runner.ps1"
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
TRANSACTION_00D9DA_MANUAL_CLEANUP_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_00d9da_manual_cleanup_ssh_runner.ps1"
)
TRANSACTION_00D9DA_TERMINAL_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_00d9da_terminal_recovery_ssh_runner.ps1"
)
POST_TIMEOUT_TRANSPORT_RECOVERY_SSH_RUNNER = (
    ROOT / "scripts" / "vps" / "phase12_spain_post_timeout_transport_recovery_ssh_runner.ps1"
)
TRANSACTION_52FAB_RUNTIME_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_52fab_runtime_recovery_ssh_runner.ps1"
)
TRANSACTION_52FAB_MANUAL_CLEANUP_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_52fab_manual_cleanup_ssh_runner.ps1"
)
TRANSACTION_958E_MANUAL_CLEANUP_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_958e_manual_cleanup_ssh_runner.ps1"
)
TRANSACTION_958E_CURRENT_AUDIT_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_958e_current_audit_ssh_runner.ps1"
)
TRANSACTION_958E_TERMINAL_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_958e_terminal_recovery_ssh_runner.ps1"
)
TRANSACTION_52FAB_TERMINAL_RECOVERY_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_52fab_terminal_recovery_ssh_runner.ps1"
)
TRANSACTION_52FAB_CURRENT_AUDIT_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_52fab_current_audit_ssh_runner.ps1"
)
TRANSACTION_52FAB_CURRENT_RESUME_SSH_RUNNER = (
    ROOT
    / "scripts"
    / "vps"
    / "phase12_spain_transaction_52fab_current_resume_ssh_runner.ps1"
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
    for label in (
        "awg_bounded_readiness_timeout",
        "docker_retry_exhausted",
        "docker_retry_exhausted_container_immutable",
        "docker_retry_exhausted_container_stopped_endpoint",
        "docker_retry_exhausted_container_running_endpoint",
        "docker_retry_exhausted_container_network_membership",
        "systemd_retry_exhausted",
        "network_retry_exhausted",
        "web_retry_exhausted",
        "ledger_transition_persist_failed",
    ):
        assert installer_module._runtime_failure_message(
            live_backend.BackendError(label)
        ) == "production runtime rollback failed:" + label
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


def test_current_terminal_recovery_audit_intent_binds_current_ledger() -> None:
    payload = {
        "schema": "amn2.spain-current-terminal-recovery-audit-intent.v1",
        "audit_authorized": True,
        "approval_id": "test-current-terminal-audit",
        "executor_sha256": "1" * 64,
        "nonce": "2" * 64,
        "transaction_sha256": "3" * 64,
        "capsule_sha256": "4" * 64,
        "mutation_ledger_sha256": "5" * 64,
        "approved_at_epoch": 100,
        "expires_at_epoch": 200,
    }

    intent = installer_module._read_current_terminal_recovery_audit_intent_payload(
        canonical_json_bytes(payload) + b"\n"
    )

    assert intent.nonce == payload["nonce"]
    assert intent.transaction_sha256 == payload["transaction_sha256"]
    assert intent.capsule_sha256 == payload["capsule_sha256"]
    assert intent.mutation_ledger_sha256 == payload["mutation_ledger_sha256"]


def test_current_terminal_recovery_resume_intent_binds_audited_contour() -> None:
    payload = {
        "schema": "amn2.spain-current-terminal-recovery-resume-intent.v1",
        "recovery_authorized": True,
        "approval_id": "test-current-terminal-resume",
        "executor_sha256": "1" * 64,
        "nonce": "2" * 64,
        "transaction_sha256": "3" * 64,
        "capsule_sha256": "4" * 64,
        "mutation_ledger_sha256": "5" * 64,
        "committed_objects_sha256": "6" * 64,
        "removed_objects_sha256": "7" * 64,
        "pending_objects_sha256": "8" * 64,
        "systemd_sha256": "9" * 64,
        "owned_tree_inventories": {
            "etc": {"tree_sha256": "a" * 64, "entry_count": 4, "total_bytes": 10, "root_mode": "0750"},
            "opt": {"tree_sha256": "b" * 64, "entry_count": 5, "total_bytes": 20, "root_mode": "0755"},
            "var": {"tree_sha256": "c" * 64, "entry_count": 1, "total_bytes": 30, "root_mode": "0750"},
        },
        "docker_data_root_inventory": {
            "tree_sha256": "e" * 64,
            "entry_count": 49,
            "total_bytes": 262199,
            "root_mode": "0710",
        },
        "run_directory_identity": "sha256:" + "d" * 64,
        "approved_at_epoch": 100,
        "expires_at_epoch": 200,
    }
    intent = installer_module._read_current_terminal_recovery_resume_intent_payload(
        canonical_json_bytes(payload) + b"\n"
    )
    assert intent.mutation_ledger_sha256 == payload["mutation_ledger_sha256"]
    assert dict(intent.owned_tree_inventories["opt"]) == payload["owned_tree_inventories"]["opt"]
    assert dict(intent.docker_data_root_inventory) == payload["docker_data_root_inventory"]

    payload["run_directory_identity"] = None
    absent_run_intent = installer_module._read_current_terminal_recovery_resume_intent_payload(
        canonical_json_bytes(payload) + b"\n"
    )
    assert absent_run_intent.run_directory_identity is None

    payload["run_directory_identity"] = "not-an-identity"

    with pytest.raises(installer_module.InstallError, match="current_terminal_recovery_resume_bound_inputs_required"):
        installer_module._read_current_terminal_recovery_resume_intent_payload(
            canonical_json_bytes(payload) + b"\n"
        )
    payload["run_directory_identity"] = "sha256:" + "d" * 64

    payload["owned_tree_inventories"]["etc"] = {
        "tree_sha256": "a" * 64, "entry_count": 0, "total_bytes": 0, "root_mode": "0750"
    }
    empty_etc_intent = installer_module._read_current_terminal_recovery_resume_intent_payload(
        canonical_json_bytes(payload) + b"\n"
    )
    assert empty_etc_intent.owned_tree_inventories["etc"]["entry_count"] == 0

    payload["owned_tree_inventories"]["etc"]["total_bytes"] = 1
    with pytest.raises(installer_module.InstallError, match="current_terminal_recovery_resume_bound_inputs_required"):
        installer_module._read_current_terminal_recovery_resume_intent_payload(
            canonical_json_bytes(payload) + b"\n"
        )
    payload["owned_tree_inventories"]["etc"]["total_bytes"] = 0

    payload["owned_tree_inventories"]["opt"]["entry_count"] = 0
    with pytest.raises(installer_module.InstallError, match="current_terminal_recovery_resume_bound_inputs_required"):
        installer_module._read_current_terminal_recovery_resume_intent_payload(
            canonical_json_bytes(payload) + b"\n"
        )



def test_current_terminal_recovery_resume_skips_generic_path_check_for_docker_data_root() -> None:
    root_fs = object()
    config_fs = object()
    service_fs = object()

    assert installer_module._current_terminal_recovery_fs_for_owned_object(
        "dir:/var/lib/amn2-spain-docker", root_fs=root_fs,
        config_fs=config_fs, service_fs=service_fs,
    ) is None

def test_current_terminal_recovery_finalize_intent_binds_post_contour_state() -> None:
    payload = {
        "schema": "amn2.spain-current-terminal-recovery-finalize-intent.v1",
        "recovery_authorized": True,
        "approval_id": "test-current-terminal-finalize",
        "executor_sha256": "1" * 64,
        "nonce": "2" * 64,
        "transaction_sha256": "3" * 64,
        "capsule_sha256": "4" * 64,
        "mutation_ledger_sha256": "5" * 64,
        "committed_objects_sha256": "6" * 64,
        "removed_objects_sha256": "7" * 64,
        "pending_objects_sha256": "8" * 64,
        "systemd_sha256": "9" * 64,
        "finalize_owned_object": "group:amn2-spain",
        "approved_at_epoch": 100,
        "expires_at_epoch": 200,
    }
    intent = installer_module._read_current_terminal_recovery_finalize_intent_payload(
        canonical_json_bytes(payload) + b"\n"
    )
    assert intent.mutation_ledger_sha256 == "5" * 64
    assert intent.finalize_owned_object == "group:amn2-spain"


def test_terminal_identity_reconciliation_records_primary_group_already_removed() -> None:
    recorded: list[tuple[str, str, str]] = []

    class Ledger:
        def event_for(self, owned_object: str):
            assert owned_object == "group:amn2-spain"
            return {
                "event": "committed",
                "stage": "identity_created",
                "actual_identity": "sha256:" + "a" * 64,
            }

        def removed(self, stage: str, owned_object: str, identity: str) -> None:
            recorded.append((stage, owned_object, identity))

    class Action:
        def observe_identity(self):
            return None

        def remove_exact(self, _identity: str) -> None:
            raise AssertionError("already-absent primary group must not be removed twice")

    result = installer_module._reconcile_terminal_identity_removal(
        ledger=Ledger(), action=Action(), owned_object="group:amn2-spain"
    )
    assert result == "already_absent"
    assert recorded == [
        ("identity_created", "group:amn2-spain", "sha256:" + "a" * 64)
    ]


def test_current_terminal_recovery_finalize_seals_auto_removed_primary_group(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = {"status": "manual_recovery_required", "recovery_capsule_sha256": "c" * 64}
    transaction_sha256 = hashlib.sha256(
        installer_module.BootstrapTransactionLedger._canonical(state)
    ).hexdigest()
    ledger_before = "5" * 64
    ledger_after = "a" * 64
    events = {
        "group:amn2-spain": {
            "event": "committed", "stage": "identity_created",
            "actual_identity": "sha256:" + "b" * 64,
        },
        "user:amn2-spain": {
            "event": "removed", "stage": "identity_created",
            "actual_identity": "sha256:" + "d" * 64,
        },
    }
    actions = (
        {"owned_object": "group:amn2-spain", "stage": "identity_created"},
        {"owned_object": "user:amn2-spain", "stage": "identity_created"},
        {"owned_object": "interface:awgsp0", "stage": "network_container_started"},
    )
    capsule = types.SimpleNamespace(
        sha256="c" * 64,
        blueprint=types.SimpleNamespace(
            digest="e" * 64,
            actions=actions,
            assembly_context={"mutation_ledger_path": str(tmp_path / "ledger.json")},
        ),
    )

    class Transaction:
        def snapshot(self):
            return copy.deepcopy(state)

    class Ledger:
        def event_for(self, owned_object: str):
            return copy.deepcopy(events.get(owned_object))

        def removed(self, stage: str, owned_object: str, identity: str) -> None:
            assert (stage, owned_object, identity) == (
                "identity_created", "group:amn2-spain", "sha256:" + "b" * 64
            )
            events[owned_object]["event"] = "removed"

    ledger = Ledger()

    class Store:
        def __init__(self, *_args, **_kwargs):
            pass

        def load_or_create(self, allowed_objects):
            assert allowed_objects == {entry["owned_object"] for entry in actions}
            return ledger

    class Lease:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def assert_held(self):
            return None

    class LeaseFactory:
        def __init__(self, *_args, **_kwargs):
            pass

        def acquire(self):
            return Lease()

    class Observer:
        MAX_COLLECTOR_BYTES = 1024 * 1024
        calls = 0

        def __init__(self, **_kwargs):
            pass

        def collect_evidence(self):
            self.calls += 1
            return {"sequence": self.calls}

    class IdentityAction:
        def __init__(self, owned_object: str):
            self.operation = types.SimpleNamespace(owned_object=owned_object)

        def observe_identity(self):
            return None

        def remove_exact(self, _identity: str):
            raise AssertionError("post-contour identities must already be absent")

    monkeypatch.setattr(installer_module, "_assert_running_executor", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        installer_module,
        "_host_path",
        lambda _root, live_path: tmp_path.joinpath(*(p for p in live_path.split("/") if p)),
    )
    monkeypatch.setattr(
        installer_module.BootstrapTransactionLedger,
        "open_existing",
        classmethod(lambda _cls, **_kwargs: Transaction()),
    )
    monkeypatch.setattr(
        installer_module.RecoveryCapsuleStore,
        "open_existing",
        classmethod(lambda _cls, **_kwargs: capsule),
    )
    monkeypatch.setattr(
        installer_module,
        "_sha256_regular_file",
        lambda *_args, **_kwargs: (
            ledger_after if events["group:amn2-spain"]["event"] == "removed" else ledger_before,
            1,
        ),
    )
    monkeypatch.setattr(installer_module, "SharedInstallLockLease", LeaseFactory)
    monkeypatch.setattr(installer_module, "ChecksumBoundResourceObserver", Observer)
    monkeypatch.setattr(live_backend, "DurableMutationLedgerStore", Store)
    monkeypatch.setattr(
        live_backend,
        "build_production_identity_bundle",
        lambda: types.SimpleNamespace(
            actions=[IdentityAction("user:amn2-spain"), IdentityAction("group:amn2-spain")]
        ),
    )
    monkeypatch.setattr(live_backend, "FixedCommandRunner", lambda **_kwargs: lambda *_args, **_kwargs: b"ignored")
    monkeypatch.setattr(
        live_backend,
        "parse_systemctl_show",
        lambda _output, *, unit: {
            "LoadState": "not-found", "FragmentPath": "", "UnitFileState": "", "ActiveState": "inactive"
        },
    )
    monkeypatch.setattr(
        installer_module,
        "observation_from_resource_confirmation_evidence",
        lambda evidence: {"sequence": evidence.get("sequence", 0)},
    )
    monkeypatch.setattr(
        installer_module,
        "_terminal_run009_baseline_observation",
        lambda current: copy.deepcopy(current),
    )
    monkeypatch.setattr(
        installer_module,
        "build_terminal_recovery_equality_receipt",
        lambda **_kwargs: {
            "foreign_service_persistent_equal": True,
            "foreign_service_volatile_before_count": 0,
            "foreign_service_volatile_after_count": 0,
        },
    )
    committed = ["group:amn2-spain"]
    removed = ["user:amn2-spain"]
    pending = ["interface:awgsp0"]
    systemd = {
        unit: {"LoadState": "not-found", "FragmentPath": "", "UnitFileState": "", "ActiveState": "inactive"}
        for unit in live_backend.SYSTEMD_UNIT_ORDER
    }
    intent = installer_module.CurrentTerminalRecoveryFinalizeIntent(
        approval_id="test-finalize", executor_sha256="1" * 64, nonce="2" * 64,
        transaction_sha256=transaction_sha256, capsule_sha256="c" * 64,
        mutation_ledger_sha256=ledger_before,
        committed_objects_sha256=installer_module.package_backend.sha256_canonical(committed),
        removed_objects_sha256=installer_module.package_backend.sha256_canonical(removed),
        pending_objects_sha256=installer_module.package_backend.sha256_canonical(pending),
        systemd_sha256=installer_module.package_backend.sha256_canonical(systemd),
        finalize_owned_object="group:amn2-spain", approved_at_epoch=100, expires_at_epoch=200,
    )

    result = installer_module._production_current_terminal_recovery_finalize_bound(
        intent, host_root=tmp_path, expected_uid=None, now_epoch=150
    )

    assert result["result"] == "passed"
    assert result["removed_owned_objects"] == ["group:amn2-spain"]
    assert result["pending_owned_objects"] == ["interface:awgsp0"]
    assert result["mutation_ledger_after_sha256"] == ledger_after
    assert result["foreign_service_persistent_equal"] is True


def test_terminal_run009_projection_adapts_legacy_baseline_without_reparsing_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current = {
        "systemd_projection": [{"name_sha256": "current"}],
        "firewall": {
            "backend": "nft", "rules_sha256": "current-raw", "rule_count": 129,
            "semantic_sha256": "semantic", "nft_json": {"current": True},
        },
        "listeners": ["current"],
    }
    monkeypatch.setattr(
        installer_module,
        "_embedded_run009_baseline",
        lambda: {
            "systemd_projection": [{"name_sha256": "sealed"}],
            "firewall": {"backend": "nft", "rule_count": 129, "rules_sha256": "sealed-raw"},
            "firewall_semantic_rebaseline": {
                "backend": "nft", "rule_count": 129,
                "current_raw_sha256": "ignored", "semantic_sha256": "semantic",
            },
        },
    )

    result = installer_module._terminal_run009_baseline_observation(current)

    assert result["systemd_projection"] == [{"name_sha256": "sealed"}]
    assert result["firewall"] == {
        "backend": "nft", "rules_sha256": "sealed-raw", "rule_count": 129,
        "semantic_sha256": "semantic", "nft_json": {"current": True},
    }
    assert result["listeners"] == ["current"]
    assert current["systemd_projection"] == [{"name_sha256": "current"}]


def test_current_terminal_recovery_audit_reports_sealed_current_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = {
        "status": "manual_recovery_required",
        "recovery_capsule_sha256": "c" * 64,
    }
    transaction_sha256 = hashlib.sha256(
        installer_module.BootstrapTransactionLedger._canonical(state)
    ).hexdigest()
    actions = (
        {
            "owned_object": "dir:/opt/amn2-spain",
            "stage": "filesystem_staged",
        },
        {
            "owned_object": "dir:/etc/amn2-spain",
            "stage": "filesystem_staged",
        },
        {
            "owned_object": "dir:/var/lib/amn2-spain",
            "stage": "filesystem_staged",
        },
        {
            "owned_object": "dir:/var/lib/amn2-spain-docker",
            "stage": "filesystem_staged",
        },
        {
            "owned_object": "runtime:docker-static",
            "stage": "filesystem_staged",
        },
        {
            "owned_object": "container:amn2-spain-awg",
            "stage": "network_container_started",
        },
        {
            "owned_object": "interface:awgsp0",
            "stage": "network_container_started",
        },
    )
    capsule = types.SimpleNamespace(
        sha256="c" * 64,
        blueprint=types.SimpleNamespace(
            actions=actions,
            assembly_context={"mutation_ledger_path": str(tmp_path / "ledger.json")},
        ),
    )
    ledger_bytes = b"sealed-ledger\n"
    ledger_sha256 = hashlib.sha256(ledger_bytes).hexdigest()

    class Transaction:
        def snapshot(self):
            return copy.deepcopy(state)

    class Ledger:
        def to_bytes(self):
            return ledger_bytes

        def event_for(self, owned_object: str):
            if owned_object == "interface:awgsp0":
                return None
            if owned_object == "container:amn2-spain-awg":
                return {
                    "event": "abandoned",
                    "stage": "network_container_started",
                    "desired_identity": "sha256:" + "b" * 64,
                    "actual_identity": None,
                }
            if owned_object == "dir:/var/lib/amn2-spain-docker":
                return {
                    "event": "committed",
                    "stage": "filesystem_staged",
                    "desired_identity": "sha256:" + "a" * 64,
                    "actual_identity": "sha256:" + "a" * 64,
                }
            return {
                "event": "removed"
                if owned_object == "runtime:docker-static"
                else "committed",
                "stage": "filesystem_staged",
                "actual_identity": "sha256:" + "a" * 64,
            }

    class Store:
        def __init__(self, *_args, **_kwargs):
            pass

        def load_or_create(self, allowed_objects):
            assert allowed_objects == {entry["owned_object"] for entry in actions}
            return Ledger()

    identities = {
        "opt/amn2-spain": "sha256:" + "a" * 64,
        "etc/amn2-spain": "sha256:" + "a" * 64,
        "var/lib/amn2-spain": "sha256:" + "a" * 64,
        "run/amn2-spain-docker": "sha256:" + "a" * 64,
    }

    class Fs:
        def __init__(self, *_args, **_kwargs):
            pass

        def identity(self, relative: str):
            return identities.get(relative)

    monkeypatch.setattr(installer_module, "_assert_running_executor", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        installer_module,
        "_host_path",
        lambda _root, live_path: tmp_path.joinpath(
            *(part for part in live_path.split("/") if part)
        ),
    )
    monkeypatch.setattr(
        installer_module.BootstrapTransactionLedger,
        "open_existing",
        classmethod(lambda _cls, **_kwargs: Transaction()),
    )
    monkeypatch.setattr(
        installer_module.RecoveryCapsuleStore,
        "open_existing",
        classmethod(lambda _cls, **_kwargs: capsule),
    )
    monkeypatch.setattr(
        installer_module,
        "_sha256_regular_file",
        lambda *_args, **_kwargs: (ledger_sha256, len(ledger_bytes)),
    )
    monkeypatch.setattr(live_backend, "DurableMutationLedgerStore", Store)
    monkeypatch.setattr(live_backend, "SafeFs", Fs)
    monkeypatch.setattr(
        live_backend,
        "build_directory_action",
        lambda *_args, **_kwargs: types.SimpleNamespace(
            operation=live_backend.OwnedOperation(
                "filesystem_staged",
                "dir:/var/lib/amn2-spain-docker",
                "sha256:" + "a" * 64,
            )
        ),
    )
    monkeypatch.setattr(
        live_backend,
        "observe_terminal_docker_data_root",
        lambda **_kwargs: {
            "tree_sha256": "f" * 64,
            "entry_count": 49,
            "total_bytes": 262199,
            "root_mode": "0710",
        },
    )
    monkeypatch.setattr(
        live_backend,
        "inspect_terminal_owned_tree",
        lambda target, **_kwargs: {
            "tree_sha256": hashlib.sha256(str(target).encode("utf-8")).hexdigest(),
            "entry_count": 1,
            "total_bytes": 1,
            "root_mode": "0755"
            if str(target).endswith("opt\\amn2-spain")
            else "0750",
        },
    )
    monkeypatch.setattr(live_backend, "FixedCommandRunner", lambda **_kwargs: lambda *_args, **_kwargs: b"ignored")
    monkeypatch.setattr(
        live_backend,
        "parse_systemctl_show",
        lambda _output, *, unit: {
            "LoadState": "loaded",
            "FragmentPath": "/etc/systemd/system/" + unit,
            "UnitFileState": "disabled",
            "ActiveState": "inactive",
        },
    )
    intent = installer_module.CurrentTerminalRecoveryAuditIntent(
        approval_id="test-audit",
        executor_sha256="b" * 64,
        nonce="d" * 64,
        transaction_sha256=transaction_sha256,
        capsule_sha256="c" * 64,
        mutation_ledger_sha256=ledger_sha256,
        approved_at_epoch=100,
        expires_at_epoch=200,
    )

    result = installer_module._production_current_terminal_recovery_audit_bound(
        intent, host_root=tmp_path, expected_uid=None, now_epoch=150
    )

    assert result["result"] == "passed"
    assert result["committed_owned_objects"] == [
        "dir:/etc/amn2-spain",
        "dir:/opt/amn2-spain",
        "dir:/var/lib/amn2-spain",
        "dir:/var/lib/amn2-spain-docker",
    ]
    assert result["removed_owned_objects"] == ["runtime:docker-static"]
    assert result["pending_owned_objects"] == [
        "container:amn2-spain-awg",
        "interface:awgsp0",
    ]
    assert [row["event"] for row in result["owned_object_states"]] == [
        "abandoned",
        "committed",
        "committed",
        "committed",
        "committed",
        "unrecorded",
        "removed",
    ]
    assert result["run_directory_identity"] == "sha256:" + "a" * 64
    assert result["docker_data_root_inventory"]["tree_sha256"] == "f" * 64


def test_runtime_recovery_intent_binds_current_terminal_runtime_contour() -> None:
    payload = {
        "schema": "amn2.spain-runtime-recovery-intent.v1",
        "mutation_authorized": True,
        "approval_id": "test-runtime-recovery",
        "executor_sha256": "2" * 64,
        "nonce": "3" * 64,
        "transaction_sha256": "4" * 64,
        "capsule_sha256": "5" * 64,
        "mutation_ledger_sha256": "6" * 64,
        "approved_at_epoch": 100,
        "expires_at_epoch": 200,
    }

    intent = installer_module._read_runtime_recovery_intent_payload(
        canonical_json_bytes(payload) + b"\n"
    )

    assert intent.nonce == payload["nonce"]
    assert intent.transaction_sha256 == payload["transaction_sha256"]
    assert intent.capsule_sha256 == payload["capsule_sha256"]
    assert intent.mutation_ledger_sha256 == payload["mutation_ledger_sha256"]


def test_runtime_recovery_ledger_requires_exact_pending_container_shape() -> None:
    image = live_backend.OwnedOperation(
        "awg_image_loaded",
        "image:" + live_backend.AWG_IMAGE_CONFIG_DIGEST,
        "sha256:" + "1" * 64,
    )
    network = live_backend.OwnedOperation(
        "network_container_started",
        "network:amn2-spain-net",
        "sha256:" + "2" * 64,
    )
    container = live_backend.OwnedOperation(
        "network_container_started",
        "container:amn2-spain-awg",
        "sha256:" + "3" * 64,
    )
    interface = live_backend.OwnedOperation(
        "network_container_started",
        "interface:awgsp0",
        "sha256:" + "4" * 64,
    )

    class Ledger:
        events = {
            image.owned_object: {
                "event": "committed",
                "stage": image.stage,
                "desired_identity": image.desired_identity,
                "actual_identity": image.desired_identity,
            },
            network.owned_object: {
                "event": "committed",
                "stage": network.stage,
                "desired_identity": network.desired_identity,
                "actual_identity": network.desired_identity,
            },
            container.owned_object: {
                "event": "intent",
                "stage": container.stage,
                "desired_identity": container.desired_identity,
                "actual_identity": None,
            },
        }

        def event_for(self, name: str) -> dict[str, str] | None:
            return self.events.get(name)

    operations = (image, network, container, interface)
    assert installer_module._classify_runtime_recovery_ledger(
        ledger=Ledger(), operations=operations
    ) == "remove_exact_pending_runtime_contour"

    Ledger.events[image.owned_object] = {
        "event": "intent",
        "stage": image.stage,
        "desired_identity": image.desired_identity,
        "actual_identity": None,
    }
    with pytest.raises(InstallError, match="runtime recovery mutation ledger mismatch"):
        installer_module._classify_runtime_recovery_ledger(
            ledger=Ledger(), operations=operations
        )


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


def test_terminal_owned_tree_inventory_is_bounded_and_no_follow(
    tmp_path: Path,
) -> None:
    target = tmp_path / "opt" / "amn2-spain"
    target.mkdir(parents=True)
    (target / "runtime").mkdir()
    (target / "runtime" / "app.py").write_bytes(b"phase12\n")

    receipt = live_backend.inspect_terminal_owned_tree(target)

    assert receipt["entry_count"] == 2
    assert receipt["total_bytes"] == len(b"phase12\n")
    assert receipt["root_mode"] == "0755"
    assert re.fullmatch(r"[0-9a-f]{64}", str(receipt["tree_sha256"]))


def test_terminal_owned_tree_empty_requires_explicit_bound(
    tmp_path: Path,
) -> None:
    target = tmp_path / "etc" / "amn2-spain"
    target.mkdir(parents=True)

    with pytest.raises(live_backend.BackendError, match="owned tree is unexpectedly empty"):
        live_backend.inspect_terminal_owned_tree(target)

    receipt = live_backend.inspect_terminal_owned_tree(target, allow_empty=True)
    assert receipt["entry_count"] == 0
    assert receipt["total_bytes"] == 0
    assert live_backend.cleanup_terminal_owned_tree(
        target,
        expected_tree_sha256=str(receipt["tree_sha256"]),
        expected_entry_count=0,
        expected_total_bytes=0,
        expected_root_mode=str(receipt["root_mode"]),
        allow_empty=True,
    ) == receipt
    assert not target.exists()


def test_terminal_owned_tree_cleanup_requires_exact_double_inventory(
    tmp_path: Path,
) -> None:
    target = tmp_path / "opt" / "amn2-spain"
    target.mkdir(parents=True)
    (target / "runtime").mkdir()
    (target / "runtime" / "app.py").write_bytes(b"phase12\n")
    receipt = live_backend.inspect_terminal_owned_tree(target)

    assert live_backend.cleanup_terminal_owned_tree(
        target,
        expected_tree_sha256=str(receipt["tree_sha256"]),
        expected_entry_count=int(receipt["entry_count"]),
        expected_total_bytes=int(receipt["total_bytes"]),
        expected_root_mode=str(receipt["root_mode"]),
    ) == receipt
    assert not target.exists()

    drift = tmp_path / "etc" / "amn2-spain"
    drift.mkdir(parents=True)
    (drift / "runtime.env").write_bytes(b"drift\n")
    with pytest.raises(live_backend.BackendError, match="terminal owned tree inventory drift"):
        live_backend.cleanup_terminal_owned_tree(
            drift,
            expected_tree_sha256="0" * 64,
            expected_entry_count=1,
            expected_total_bytes=6,
            expected_root_mode="0755",
        )


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


def test_shared_install_lock_lease_preserves_backend_error_from_body() -> None:
    @contextmanager
    def lock():
        yield

    lease = SharedInstallLockLease(lock)
    with pytest.raises(live_backend.BackendError, match="terminal rollback exact removal failed"):
        with lease.acquire():
            raise live_backend.BackendError("terminal rollback exact removal failed")


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


def test_network_unit_failure_receipt_is_capsule_bound(tmp_path: Path) -> None:
    receipt = installer_module.persist_network_unit_failure_receipt(
        audit_root=tmp_path,
        nonce="a" * 64,
        capsule_sha256="b" * 64,
        stage="host_network_applied",
        status={
            "result": "exit-code",
            "exec_main_code": "exited",
            "exec_main_status": "1",
            "network_script_failure_label": "network_script_exit_1",
        },
        expected_uid=None,
    )

    assert receipt.name == "network-unit-failure-" + ("a" * 64) + ".json"
    assert json.loads(receipt.read_text(encoding="utf-8")) == {
        "capsule_sha256": "b" * 64,
        "network_script_failure_label": "network_script_exit_1",
        "nonce": "a" * 64,
        "schema": "amn2.spain-network-unit-failure-receipt.v1",
        "stage": "host_network_applied",
        "systemd": {
            "exec_main_code": "exited",
            "exec_main_status": "1",
            "result": "exit-code",
        },
    }

def test_capture_network_unit_failure_receipt_uses_exact_status_command(tmp_path: Path) -> None:
    calls: list[tuple[str, ...]] = []

    def runner(argv: tuple[str, ...], **_kwargs: object) -> bytes:
        calls.append(argv)
        return b"Result=exit-code\nExecMainCode=exited\nExecMainStatus=1\n"

    receipt = installer_module.capture_network_unit_failure_receipt(
        audit_root=tmp_path,
        nonce="a" * 64,
        capsule_sha256="b" * 64,
        systemd_runner=runner,
        expected_uid=None,
    )

    assert calls == [live_backend.NETWORK_UNIT_FAILURE_SHOW_ARGV]
    assert json.loads(receipt.read_text(encoding="utf-8"))["network_script_failure_label"] == "network_script_exit_1"

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


def test_rollback_equality_uses_semantic_firewall_projection() -> None:
    before = copy.deepcopy(OBSERVATION)
    after = copy.deepcopy(OBSERVATION)
    binding = {
        "nonce": "a" * 64,
        "transaction_sha256": "b" * 64,
        "blueprint_sha256": "c" * 64,
    }
    after["firewall"]["rules_sha256"] = "e" * 64
    after["firewall"]["nft_json"]["nftables"][1]["chain"]["handle"] = 91

    receipt = build_rollback_equality_receipt(
        baseline_observation=before,
        current_observation=after,
        binding=binding,
    )

    assert receipt["firewall_projection_equal"] is True
    after["firewall"]["semantic_sha256"] = "f" * 64
    with pytest.raises(InstallError, match="rollback firewall projection"):
        build_rollback_equality_receipt(
            baseline_observation=before,
            current_observation=after,
            binding=binding,
        )

def test_production_rollback_baseline_captures_first_observation_once() -> None:
    holder: dict[str, object] = {}
    first = copy.deepcopy(OBSERVATION)
    second = copy.deepcopy(OBSERVATION)
    second["listeners"] = [*second["listeners"], "tcp|loopback|3031"]

    installer_module._capture_production_rollback_baseline(holder, first)
    installer_module._capture_production_rollback_baseline(holder, second)
    first["listeners"].append("tcp|loopback|9999")

    assert holder == {"value": OBSERVATION}


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


def test_terminal_recovery_resumes_mixed_exact_contour() -> None:
    class Ledger:
        def event_for(self, name: str) -> dict[str, str] | None:
            return {
                "owned:retained": {"event": "committed"},
                "owned:already-removed": {"event": "removed"},
            }.get(name)

    assert installer_module._classify_terminal_recovery_ledger(
        ledger=Ledger(),
        blueprint={"owned:retained": {}, "owned:already-removed": {}},
        expected_objects={"owned:retained", "owned:already-removed"},
    ) == "removed_verified_owned_objects"


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


def test_current_terminal_recovery_audit_mode_routes_only_bound_intent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    sentinel = object()
    monkeypatch.setattr(
        installer_module,
        "_read_current_terminal_recovery_audit_intent_payload",
        lambda _payload: sentinel,
    )
    monkeypatch.setattr(
        installer_module,
        "_production_current_terminal_recovery_audit_bound",
        lambda intent, **kwargs: captured.update(intent=intent, **kwargs)
        or {"result": "passed"},
    )

    assert installer_module.run_production_command(
        ["current-terminal-recovery-audit-bound"], authorization_payload=b"{}"
    ) == {"result": "passed"}
    assert captured["intent"] is sentinel
    with pytest.raises(
        InstallError, match="current_terminal_recovery_audit_bound_inputs_required"
    ):
        installer_module.run_production_command(
            ["current-terminal-recovery-audit-bound", "unexpected"],
            authorization_payload=b"{}",
        )


def test_current_terminal_recovery_resume_mode_routes_only_bound_intent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    sentinel = object()
    monkeypatch.setattr(
        installer_module,
        "_read_current_terminal_recovery_resume_intent_payload",
        lambda _payload: sentinel,
    )
    monkeypatch.setattr(
        installer_module,
        "_production_current_terminal_recovery_resume_bound",
        lambda intent, **kwargs: captured.update(intent=intent, **kwargs)
        or {"result": "passed"},
    )
    assert installer_module.run_production_command(
        ["current-terminal-recovery-resume-bound"], authorization_payload=b"{}"
    ) == {"result": "passed"}
    assert captured["intent"] is sentinel
    with pytest.raises(
        InstallError, match="current_terminal_recovery_resume_bound_inputs_required"
    ):
        installer_module.run_production_command(
            ["current-terminal-recovery-resume-bound", "unexpected"],
            authorization_payload=b"{}",
        )


def test_current_terminal_recovery_finalize_mode_routes_only_bound_intent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    sentinel = object()
    monkeypatch.setattr(
        installer_module,
        "_read_current_terminal_recovery_finalize_intent_payload",
        lambda _payload: sentinel,
    )
    monkeypatch.setattr(
        installer_module,
        "_production_current_terminal_recovery_finalize_bound",
        lambda intent, **kwargs: captured.update(intent=intent, **kwargs)
        or {"result": "passed"},
    )
    assert installer_module.run_production_command(
        ["current-terminal-recovery-finalize-bound"], authorization_payload=b"{}"
    ) == {"result": "passed"}
    assert captured["intent"] is sentinel
    with pytest.raises(
        InstallError, match="current_terminal_recovery_finalize_bound_inputs_required"
    ):
        installer_module.run_production_command(
            ["current-terminal-recovery-finalize-bound", "unexpected"],
            authorization_payload=b"{}",
        )


def test_runtime_recovery_mode_routes_only_bound_intent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    sentinel = object()
    monkeypatch.setattr(
        installer_module,
        "_read_runtime_recovery_intent_payload",
        lambda _payload: sentinel,
    )
    monkeypatch.setattr(
        installer_module,
        "_production_runtime_recovery_bound",
        lambda intent, **kwargs: captured.update(intent=intent, **kwargs) or {"result": "passed"},
    )

    assert installer_module.run_production_command(
        ["runtime-recovery-bound"], authorization_payload=b"{}"
    ) == {"result": "passed"}
    assert captured["intent"] is sentinel
    with pytest.raises(InstallError, match="runtime_recovery_bound_inputs_required"):
        installer_module.run_production_command(
            ["runtime-recovery-bound", "unexpected"], authorization_payload=b"{}"
        )


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


def test_transaction_52fab_runtime_recovery_runner_is_executor_and_ledger_bound() -> None:
    assert TRANSACTION_52FAB_RUNTIME_RECOVERY_SSH_RUNNER.exists()
    source = TRANSACTION_52FAB_RUNTIME_RECOVERY_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert "ConnectTimeout=20" in source
    assert "ServerAliveInterval=15" in source
    assert "runtime-recovery-bound" in source
    assert "install-bound" not in source
    assert "manual-cleanup-bound" not in source
    assert "terminal-recovery-bound" not in source
    assert '$expectedExecutorSha = "4D110B0DC169BE38A65B16A89DD8A9B54AEB5840117E5F4B443CC4538939D4DC"' in source
    assert "$expectedExecutorBytes = 147586" in source
    assert '$expectedPriorExecutorSha = "04B0F5142E7D7464C7CA6555E482A17F4C3D79D1F209A0E7327CD44144AD6978"' in source
    assert '$expectedNonce = "52fab7ac3eaf2ea1d1c7bf5f21778662ddc5964a9796188d29c98b0fcafee246"' in source
    assert '$expectedTransactionSha = "7beec673258de6b4b68206f8013ab8cc9c8d1fb488e38e39340baa1c571d6e1c"' in source
    assert '$expectedCapsuleSha = "eb6b3ee6864504f724f7ac7d8839983bdec717c576871cadc7c98b95337cf088"' in source
    assert '$expectedLedgerSha = "de027712753dda4fee2fe0714550b4a1bed3d975fc17eaa4ff81351f15306b01"' in source
    assert "Invoke-BoundedSshUpload" in source
    assert '"/root/amn2-spain-phase12-runtime-recovery-executor-a.pyz"' in source
    assert "REMOVE ONLY AMN2 DEDICATED DOCKER CONTAINER NETWORK IMAGE" in source
    assert "NO FOREIGN SERVICE MUTATION" in source
    assert "NO USA DATA MUTATION" in source
    assert "scp.exe" not in source
    assert "$expectedRemovedObjects" in source
    assert "Compare-Object -ReferenceObject" in source
    assert "@($receipt[\"removed_owned_objects\"]) -cne" not in source


def test_transaction_52fab_current_audit_runner_is_read_only_and_executor_pinned() -> None:
    assert TRANSACTION_52FAB_CURRENT_AUDIT_SSH_RUNNER.exists()
    source = TRANSACTION_52FAB_CURRENT_AUDIT_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert "current-terminal-recovery-audit-bound" in source
    assert "current-terminal-recovery-audit-intent.v1" in source
    assert "mutation_ledger_sha256" in source
    assert "CopyToAsync" in source
    assert "NO INSTALL NO CLEANUP NO AMN2 START" in source
    assert "terminal-recovery-bound" not in source
    assert "manual-cleanup-bound" not in source


def test_transaction_52fab_current_resume_runner_is_audit_and_executor_bound() -> None:
    assert TRANSACTION_52FAB_CURRENT_RESUME_SSH_RUNNER.exists()
    source = TRANSACTION_52FAB_CURRENT_RESUME_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert "current-terminal-recovery-resume-bound" in source
    assert "current-terminal-recovery-resume-intent.v1" in source
    assert '$expectedExecutorSha = "07FA623C7C919A0263C738FACBC816717102526B3A126CDEDAA03E70E6DF5060"' in source
    assert '$expectedLedgerSha = "0ee87dfa762739457eafa5d6c8c81168f99da745b6ddd0f30bc60388f7e660c9"' in source
    assert "0f2f2ade8f6876dfdd65ef495f7131555caab6be6361dca2d6811ca9f3d25119" in source
    assert "CopyToAsync" in source
    assert "REMOVE EXACT AUDITED AMN2 CONTOUR" in source
    assert "install-bound" not in source
    assert "manual-cleanup-bound" not in source


def test_transaction_52fab_followup_recovery_runners_are_pinned_and_action_bound() -> None:
    assert TRANSACTION_52FAB_MANUAL_CLEANUP_SSH_RUNNER.exists()
    assert TRANSACTION_52FAB_TERMINAL_RECOVERY_SSH_RUNNER.exists()
    cleanup = TRANSACTION_52FAB_MANUAL_CLEANUP_SSH_RUNNER.read_text(encoding="utf-8")
    terminal = TRANSACTION_52FAB_TERMINAL_RECOVERY_SSH_RUNNER.read_text(encoding="utf-8")
    nonce = "52fab7ac3eaf2ea1d1c7bf5f21778662ddc5964a9796188d29c98b0fcafee246"
    transaction = "7beec673258de6b4b68206f8013ab8cc9c8d1fb488e38e39340baa1c571d6e1c"
    capsule = "eb6b3ee6864504f724f7ac7d8839983bdec717c576871cadc7c98b95337cf088"
    tree = "9aaf13904fd0738d88fe13db54527f6426f783b06664e3baf6e41ff140755aee"
    for source in (cleanup, terminal):
        assert "StrictHostKeyChecking=yes" in source
        assert "ConnectTimeout=20" in source
        assert "ServerAliveInterval=15" in source
        assert "ServerAliveCountMax=4" in source
        assert '$expectedExecutorSha = "4D110B0DC169BE38A65B16A89DD8A9B54AEB5840117E5F4B443CC4538939D4DC"' in source
        assert "$expectedExecutorBytes = 147586" in source
        assert f'$expectedNonce = "{nonce}"' in source
        assert f'$expectedTransactionSha = "{transaction}"' in source
        assert "scp.exe" not in source
        assert "install-bound" not in source
    assert "manual-cleanup-bound" in cleanup
    assert "terminal-recovery-bound" not in cleanup
    assert "REMOVE ONLY VERIFIED RETAINED PACKAGE TREE" in cleanup
    assert "terminal-recovery-bound" in terminal
    assert "terminal-recovery-receipt-bound" not in terminal
    assert f'$expectedCapsuleSha = "{capsule}"' in terminal
    assert f'$expectedDockerTreeSha = "{tree}"' in terminal
    assert "$expectedDockerTreeEntries = 49" in terminal
    assert "$expectedDockerTreeBytes = 262199" in terminal
    assert "ROOT MODE 0710" in terminal
    assert "ROLLBACK EXACT OWNED CURRENT TRANSACTION" in terminal
    assert "VERIFY FOREIGN EQUALITY" in terminal


def test_transaction_958e_manual_cleanup_runner_is_exact_and_package_only() -> None:
    assert TRANSACTION_958E_MANUAL_CLEANUP_SSH_RUNNER.exists()
    source = TRANSACTION_958E_MANUAL_CLEANUP_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert '$expectedExecutorSha = "E621C0CC23B89FB7109DDEFA665EF16B3F3A8105D31AE9B7589A102E9ED1E8D4"' in source
    assert "$expectedExecutorBytes = 153174" in source
    assert '$expectedNonce = "958e91b682d226fc1f229b1bee2592dfe6340443fb768f3e2c9a9df45f6979b8"' in source
    assert '$expectedTransactionSha = "b66e6540582fc328b89c559fda2b08263f27c56e28010aec81aff4eb28375810"' in source
    assert "manual-cleanup-bound" in source
    assert "REMOVE ONLY VERIFIED RETAINED PACKAGE TREE" in source
    assert "terminal-recovery-bound" not in source
    assert "runtime-recovery-bound" not in source
    assert "install-bound" not in source


def test_transaction_958e_current_audit_runner_is_exact_and_read_only() -> None:
    assert TRANSACTION_958E_CURRENT_AUDIT_SSH_RUNNER.exists()
    source = TRANSACTION_958E_CURRENT_AUDIT_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert '$expectedExecutorSha = "E621C0CC23B89FB7109DDEFA665EF16B3F3A8105D31AE9B7589A102E9ED1E8D4"' in source
    assert '$expectedNonce = "958e91b682d226fc1f229b1bee2592dfe6340443fb768f3e2c9a9df45f6979b8"' in source
    assert '$expectedTransactionSha = "b66e6540582fc328b89c559fda2b08263f27c56e28010aec81aff4eb28375810"' in source
    assert '$expectedCapsuleSha = "0b4890a6b9786a13145879f604924cbe4162d8d6eb94716e0f1b0f76f8e02e0f"' in source
    assert '$expectedLedgerSha = "93676697ccabe3f8de849bcbe412a81d93ba3fe33e410c0181d9e07a900f443a"' in source
    assert "current-terminal-recovery-audit-bound" in source
    assert "READ ONLY CURRENT AMN2 LEDGER SYSTEMD OWNED TREE INVENTORY" in source
    assert "manual-cleanup-bound" not in source
    assert "install-bound" not in source


def test_transaction_958e_terminal_recovery_runner_is_mixed_contour_bound() -> None:
    assert TRANSACTION_958E_TERMINAL_RECOVERY_SSH_RUNNER.exists()
    source = TRANSACTION_958E_TERMINAL_RECOVERY_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert '$expectedExecutorSha = "8196CDD272FCA5ADE5C1DBCEE036597926C6A003DC8D380985DE80EE45A41B67"' in source
    assert '$expectedPriorExecutorSha = "E621C0CC23B89FB7109DDEFA665EF16B3F3A8105D31AE9B7589A102E9ED1E8D4"' in source
    assert '$expectedNonce = "958e91b682d226fc1f229b1bee2592dfe6340443fb768f3e2c9a9df45f6979b8"' in source
    assert '$expectedTransactionSha = "b66e6540582fc328b89c559fda2b08263f27c56e28010aec81aff4eb28375810"' in source
    assert '$expectedCapsuleSha = "0b4890a6b9786a13145879f604924cbe4162d8d6eb94716e0f1b0f76f8e02e0f"' in source
    assert '$expectedDockerTreeSha = "642b64adf9cf3b5b8ec4d8f141e24603dc0723c6db544c94025d202b1aef588b"' in source
    assert "$expectedDockerTreeEntries = 49" in source
    assert "$expectedDockerTreeBytes = 262199" in source
    assert "Invoke-BoundedSshUpload" in source
    assert "terminal-recovery-bound" in source
    assert "ROLLBACK EXACT OWNED CURRENT TRANSACTION" in source
    assert "VERIFY FOREIGN EQUALITY" in source
    assert "install-bound" not in source


def test_install_ssh_runner_binds_only_artifacts_and_in_memory_install_intent() -> None:
    source = INSTALL_SSH_RUNNER.read_text(encoding="utf-8")
    assert '$expectedPackageSha = "E36421C92F1519BE391C1777171F308F57375E77885F4B104D0A899D05E0F19C"' in source
    assert '$expectedManifestSha = "BC5FCB8DECB361F3C4F41AAA9D05D87BEEA3410A766C7634538BCEE0BF29CE2C"' in source
    assert '$expectedExecutorSha = "DEDD72A206B48001A334CE9B260316D495854FCF983D3A7C12E3DB8CD5F2D75E"' in source
    assert '$expectedExecutorBytes = 157707' in source
    assert '$expectedCollectorSha = "4705B22EC68A0EA2820BDE82E41DB8D364EBD41D884A2A3D080FFE214CBC4D8D"' in source
    assert 'phase12-spain-install-network-unit-receipt-v32-a-20260727' in source
    assert 'UNIFIED BOUNDED FALLBACK LADDER EXACT CACHE OR VERIFIED 20MIB PARTS' in source
    assert 'NETWORK UNIT FAILURE RECEIPT ALLOWLISTED SYSTEMD RESULT EXECMAINCODE EXECMAINSTATUS AND SCRIPT LABEL BEFORE ROLLBACK CAPSULE BOUND AUDIT RECEIPT NO RAW JOURNAL OR SECRETS' in source
    assert 'DOCKER29 PRESTART CAPABILITY NORMALIZATION STOPPED EMPTY ENDPOINT ALLOWED RUNNING ENDPOINT STRICT' in source
    assert 'NETWORK SERVICE BOUND PREPARED LEDGER OBSERVATION RESUME THEN ONE START RETRY' in source
    assert 'amn2-spain-phase12-install-v32.tar.part-001' in source
    assert 'D459CB36D3EDD1F202CDFBD4ED8C5DB4F2D1A6BE7FA14CD50E4D4B5AE89AB43A' in source
    assert 'amn2-spain-phase12-install-v32.tar.part-007' in source
    assert '8EBA65E05EAFE72A87BCA75FB157145826AB2FC5E4E50FF2137DBCC050120022' in source
    assert 'Remote package part assembly mismatch.' in source
    assert 'LegacyName="amn2-spain-phase12-install-v31.tar.part-002"' in source
    assert '$approvedUploadDestinations' in source
    assert 'Remote package part checksum mismatch.' in source
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
    assert "[void]$copyTask.GetAwaiter().GetResult()" in source
    assert "[void][Threading.Tasks.Task]::WaitAll" in source
    assert "installResult.Stderr" in source
    assert "remoteArtifactsReady" in source
    assert "[Convert]::ToHexString" not in source
    assert "[A-Z0-9_]+" in source
    assert "resource-confirmation-evidence" not in source
    assert "precondition-receipt" not in source
    assert "baseline" not in source


def test_transaction_89c835_runner_bundles_exact_terminal_recovery() -> None:
    source = TRANSACTION_89C835_BUNDLED_RECOVERY_SSH_RUNNER.read_text(
        encoding="utf-8"
    )
    assert "StrictHostKeyChecking=yes" in source
    assert "manual-cleanup-bound" in source
    assert "terminal-recovery-bound" in source
    assert source.index("manual-cleanup-bound") < source.index(
        "terminal-recovery-bound"
    )
    assert "install-bound" not in source
    assert "scp.exe" not in source
    assert "D8E51499A4F5CF5CFDE59DF056FF0BFB074B0E251C4AD474F6AED2DE5642F072" in source
    assert "89c8359e6142f03e8ab94baa9dcf3efbff34e5e5e4bb0bdd9a3692b3383ae9c8" in source
    assert "34454708115b48218bb8ec5ef6a1edce8ab6f401e22afa1bd41f38482cbf7b5f" in source
    assert "dd6b6227349dc63aa04b1c06324a4cd51ff6a7e9cb3cc5c36fae3fb3e6396b0d" in source
    assert "b73ccebfde0aa4a21e47b3236e96f99b4c3801af2384cfd96d3b28fb161f1774" in source
    assert "$expectedDockerTreeEntries = 51" in source
    assert "$expectedDockerTreeBytes = 360503" in source
    assert "NO FOREIGN SERVICE MUTATION" in source


def test_transaction_9d2d0d_runner_bundles_exact_terminal_recovery() -> None:
    source = TRANSACTION_9D2D0D_BUNDLED_RECOVERY_SSH_RUNNER.read_text(
        encoding="utf-8"
    )
    assert "StrictHostKeyChecking=yes" in source
    assert "manual-cleanup-bound" in source
    assert "terminal-recovery-bound" in source
    assert source.index("manual-cleanup-bound") < source.index(
        "terminal-recovery-bound"
    )
    assert "install-bound" not in source
    assert "scp.exe" not in source
    assert "7DB67E85436E3530E5CF0DA0D46897353AE86182539DD9C91154CEA004D49758" in source
    assert "9d2d0d0b3bae9df38a717efd8995e4715893ec6ff861eb4824510ed9aa201889" in source
    assert "75f0f66c438d4115c0bf7640bdfbfec1c320ac8f06aac36229ad7681de0f1df2" in source
    assert "9d912bd1d9bed6dd1c2678e6b4a8ee7b26d74ed9592b4b405ded82184427fd7c" in source
    assert "db76eb0118231f1f2aab6cb679e77453293bcbdd2157e5be3df7a2f644731013" in source
    assert "$expectedDockerTreeEntries = 51" in source
    assert "$expectedDockerTreeBytes = 360503" in source
    assert "NO FOREIGN SERVICE MUTATION" in source


def test_transaction_ad0e8b_runner_bundles_exact_terminal_recovery() -> None:
    source = TRANSACTION_AD0E8B_BUNDLED_RECOVERY_SSH_RUNNER.read_text(
        encoding="utf-8"
    )
    assert "StrictHostKeyChecking=yes" in source
    assert "manual-cleanup-bound" in source
    assert "terminal-recovery-bound" in source
    assert source.index("manual-cleanup-bound") < source.index(
        "terminal-recovery-bound"
    )
    assert "install-bound" not in source
    assert "scp.exe" not in source
    assert "AE459D0779D4ECDC5C307182336B744E0E986FA893AEADED8342CAC139F04BE4" in source
    assert "ad0e8bc5f43f2cb4de3958d7ac151f5d4242ea18d0707d6e6696e0f6909b6375" in source
    assert "6dae7cd3b2d6af6534fb6b0d66269e8e961b7acf8df915c0398935098de7c0b7" in source
    assert "94e41971abb6bcc01f3105d1ce6ddf8106cd5b5e7dd6ad44770e32c274727561" in source
    assert "98af670852d8976e04592fb8a45d7349f4024de29c52f241dab052e1bc1305a7" in source
    assert "$expectedDockerTreeEntries = 51" in source
    assert "$expectedDockerTreeBytes = 360503" in source
    assert "NO FOREIGN SERVICE MUTATION" in source

def test_transaction_8c0eb7_runner_bundles_exact_terminal_recovery() -> None:
    source = TRANSACTION_8C0EB7_BUNDLED_RECOVERY_SSH_RUNNER.read_text(
        encoding="utf-8"
    )
    assert "StrictHostKeyChecking=yes" in source
    assert "manual-cleanup-bound" in source
    assert "terminal-recovery-bound" in source
    assert source.index("manual-cleanup-bound") < source.index(
        "terminal-recovery-bound"
    )
    assert "install-bound" not in source
    assert "scp.exe" not in source
    assert "22A208A638D29E785BE2881FF2390B02AD90ABE280FCDF2A71E578E24F86E479" in source
    assert "8c0eb7e9b1345f599c33de55f9b00779b553aa7b5d570b41d54da497074310c3" in source
    assert "7f0684a098ee51ec21d01f0240f91ed0e49036b9c9784028ce8212f615df016c" in source
    assert "38a07bbb54172f677883043b3c2280999ebb0305654a2fef57850576c4cc710a" in source
    assert "92f854a48f607bb29eca714bd42cceca0ca7bf14ab3533bf26596970edd29cbb" in source
    assert "$expectedDockerTreeEntries = 51" in source
    assert "$expectedDockerTreeBytes = 360503" in source
    assert "NO FOREIGN SERVICE MUTATION" in source

def test_transaction_84aa1f_runner_bundles_exact_terminal_recovery() -> None:
    source = TRANSACTION_84AA1F_BUNDLED_RECOVERY_SSH_RUNNER.read_text(
        encoding="utf-8"
    )
    assert "StrictHostKeyChecking=yes" in source
    assert "manual-cleanup-bound" in source
    assert "terminal-recovery-bound" in source
    assert source.index("manual-cleanup-bound") < source.index(
        "terminal-recovery-bound"
    )
    assert "install-bound" not in source
    assert "scp.exe" not in source
    assert "22A208A638D29E785BE2881FF2390B02AD90ABE280FCDF2A71E578E24F86E479" in source
    assert "84aa1f36cdda4af588640e527c690a98dc364091591409ab0cf03ed21519ac59" in source
    assert "663d27a5bc97fcef339aef157c118194c688ed44d9913326e6c40728c3759238" in source
    assert "b57058e9a374cebec4155a1797e316b021aa9113df262b2d90be903dca1134a2" in source
    assert "2affb8479f3fb5a465e1af48c9f30d9837e42151805f078384d443f893b4bbb7" in source
    assert "$expectedDockerTreeEntries = 51" in source
    assert "$expectedDockerTreeBytes = 360503" in source
    assert "NO FOREIGN SERVICE MUTATION" in source

def test_transaction_eaf145_runner_bundles_exact_terminal_recovery() -> None:
    source = TRANSACTION_EAF145_BUNDLED_RECOVERY_SSH_RUNNER.read_text(
        encoding="utf-8"
    )
    assert "StrictHostKeyChecking=yes" in source
    assert "manual-cleanup-bound" in source
    assert "terminal-recovery-bound" in source
    assert source.index("manual-cleanup-bound") < source.index(
        "terminal-recovery-bound"
    )
    assert "amn2.spain-terminal-recovery-intent.v1" in source
    assert "install-bound" not in source
    assert "scp.exe" not in source
    assert (
        "D8E51499A4F5CF5CFDE59DF056FF0BFB074B0E251C4AD474F6AED2DE5642F072"
        in source
    )
    assert (
        "eaf145ae2372c2dc1ce9e84ec4f0e30c4c29490b1a20bb137cd812a2b7dd355b"
        in source
    )
    assert (
        "88ca0dfc1c2ab0af972e965b515deb01f5d9fc47166985715eb4fa76284e7693"
        in source
    )
    assert (
        "5e10f9fad1ef7c19048743297f4362249cc034e9914b84bead3004fddedab3fb"
        in source
    )
    assert (
        "7e74d39018511064ae9fffaf52016c0e34504142f7105b3388b590a0a22d542e"
        in source
    )
    assert "$expectedDockerTreeEntries = 51" in source
    assert "$expectedDockerTreeBytes = 360503" in source
    assert "REMOVE ONLY VERIFIED RETAINED PACKAGE TREE" in source
    assert "ROLLBACK EXACT OWNED CURRENT TRANSACTION" in source
    assert "NO FOREIGN SERVICE MUTATION" in source


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


def test_current_manual_cleanup_runner_bundles_exact_terminal_recovery() -> None:
    source = CURRENT_MANUAL_CLEANUP_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert "ConnectTimeout=20" in source
    assert "ServerAliveInterval=15" in source
    assert "ServerAliveCountMax=4" in source
    assert "manual-cleanup-bound" in source
    assert "terminal-recovery-bound" in source
    assert "amn2.spain-terminal-recovery-intent.v1" in source
    assert "scp.exe" not in source
    assert "Remote current manual cleanup executor checksum mismatch." in source
    assert '$expectedExecutorSha = "13B55CE5B44F49AB744035810A550ED8BA0E3BD314E2288EF213C5DEF19C386A"' in source
    assert '$expectedExecutorBytes = 154002' in source
    assert '$expectedNonce = "9e425681bd5a4d71acc6209636d3c8deaa6ff903edeb779bd50b02e3b4a3c044"' in source
    assert '$expectedTransactionSha = "e63c1ac4556f568d91cde4c243c60e63a27101eaf1aed771ba19e9945c8c3e59"' in source
    assert '$expectedCapsuleSha = "7bbcfa4964e9280e405825e6973f5266616fbb180e3c665c95873b1c5c989eb2"' in source
    assert '$expectedDockerTreeSha = "d90b28b71540f2c5363d6af6254c3189407f15800f5ed92fd2ffebbee1d66bb9"' in source
    assert '$expectedDockerTreeEntries = 49' in source
    assert '$expectedDockerTreeBytes = 262199' in source
    assert "REMOVE ONLY VERIFIED RETAINED PACKAGE TREE" in source
    assert "ROLLBACK EXACT OWNED CURRENT TRANSACTION" in source


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
    assert '$expectedExecutorSha = "B2E90D67CBC9172A9C099155E4B67FBBADBB47DA1FEF6AD8A724DB79228555E9"' in source
    assert '$expectedExecutorBytes = 145873' in source
    assert '$expectedNonce = "e968810382104e77e136565b6e3b5b28987a670d314efcd9fb9b7982ef168c82"' in source
    assert '$expectedTransactionSha = "9ba96ef4766bb4905d327519eb41a4d25917ad2d084a6b1d0a066f340a859d2d"' in source
    assert '$expectedCapsuleSha = "3643dc676017de057972eb5d93be6f94a79b19a84cf6c3a352c56821c7680679"' in source
    assert '$expectedDockerTreeSha = "db16c4e758fe4d210e1f74ee0c2774a1b100fe535fa4b24c706e1fbe5a86467d"' in source
    assert '$expectedDockerTreeEntries = 2268' in source
    assert '$expectedDockerTreeBytes = 42532407' in source
    assert '$expectedBlockRdev = 64770' in source
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


def test_transaction_00d9da_recovery_runners_are_pinned_and_action_bound() -> None:
    assert TRANSACTION_00D9DA_MANUAL_CLEANUP_SSH_RUNNER.exists()
    assert TRANSACTION_00D9DA_TERMINAL_RECOVERY_SSH_RUNNER.exists()
    cleanup = TRANSACTION_00D9DA_MANUAL_CLEANUP_SSH_RUNNER.read_text(encoding="utf-8")
    terminal = TRANSACTION_00D9DA_TERMINAL_RECOVERY_SSH_RUNNER.read_text(encoding="utf-8")
    nonce = "00d9daecb6701b443d5714e7d08ec8715ad8ce6aa01712607463b572a5212972"
    transaction = "704c0c085b5f4cec40fc7a8c9e7f7c7e55f29027f4d3168393e16c26b9090ce4"
    capsule = "19add794051040ac287d6ddb842e82dc01a96322bd135f9951a1412d18597a95"
    tree = "587e6d2b0179317fdbdbb53d125b757dc53fd93e3b0cc786ec5d2d54fc010430"
    for source in (cleanup, terminal):
        assert "StrictHostKeyChecking=yes" in source
        assert '$expectedExecutorSha = "C5704E0F83FEFDAFAFC6A7EE174F29C0559E39A1B2429E30D5EA0DF955BE690E"' in source
        assert "$expectedExecutorBytes = 146011" in source
        assert f'$expectedNonce = "{nonce}"' in source
        assert f'$expectedTransactionSha = "{transaction}"' in source
        assert "scp.exe" not in source
        assert "install-bound" not in source
    assert "manual-cleanup-bound" in cleanup
    assert "terminal-recovery-bound" not in cleanup
    assert "REMOVE ONLY VERIFIED RETAINED PACKAGE TREE" in cleanup
    assert "terminal-recovery-bound" in terminal
    assert "terminal-recovery-receipt-bound" not in terminal
    assert f'$expectedCapsuleSha = "{capsule}"' in terminal
    assert f'$expectedDockerTreeSha = "{tree}"' in terminal
    assert "$expectedDockerTreeEntries = 2268" in terminal
    assert "$expectedDockerTreeBytes = 42532407" in terminal
    assert "ROOT MODE 0710" in terminal
    assert "ROLLBACK EXACT OWNED CURRENT TRANSACTION" in terminal
    assert "VERIFY FOREIGN EQUALITY" in terminal


def test_post_timeout_transport_recovery_runner_is_partial_only_and_fail_closed() -> None:
    assert POST_TIMEOUT_TRANSPORT_RECOVERY_SSH_RUNNER.exists()
    source = POST_TIMEOUT_TRANSPORT_RECOVERY_SSH_RUNNER.read_text(encoding="utf-8")
    assert "StrictHostKeyChecking=yes" in source
    assert "AUTHORIZE AMN2 PHASE12 POST-TIMEOUT TRANSPORT RECOVERY IN GO MODE" in source
    assert '$expectedPackageSha = "FF9E8FA4604C4E9F7A3EE139B1D7B96D53FA4693E4555808B7E1725BDBAD4974"' in source
    assert "$expectedPackageBytes = 139970560" in source
    assert '$expectedExecutorSha = "04B0F5142E7D7464C7CA6555E482A17F4C3D79D1F209A0E7327CD44144AD6978"' in source
    assert "$expectedExecutorBytes = 146014" in source
    assert "/root/amn2-spain-phase12-install-a.tar" in source
    assert "/root/amn2-spain-phase12-executor-a.pyz" in source
    assert "active_install_transaction" in source
    assert "amn2_units_active" in source
    assert '"partial"' in source
    assert '"complete_current"' in source
    assert 'rm -f -- "$package_path"' in source
    assert 'rm -f -- "$executor_path"' in source
    assert "[void]$writeTask.GetAwaiter().GetResult()" in source
    assert "scp.exe" not in source
    assert "phase12_spain_remote_executor.sh" not in source


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
