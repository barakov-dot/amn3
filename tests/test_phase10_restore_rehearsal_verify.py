from __future__ import annotations

import base64
import hashlib
import io
import json
import sqlite3
import tarfile
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from scripts.phase10_recovery_crypto import encrypt_hybrid
from scripts.phase10_restore_rehearsal_verify import (
    MANIFEST_NAME,
    VerificationError,
    build_manifest,
    load_tar_files,
    validate_sanitized_files,
    validate_recovery_files,
    verify_encrypted_bundle,
    verify_hybrid_bundle,
)
from tests.test_phase11_recovery_runtime import (
    docker_image_archive,
    docker_image_diff_ids,
    docker_image_inspect,
    docker_image_runtime_config,
    docker_inspect,
    source_archive,
)
from scripts.phase11_recovery_runtime import normalize_runtime_contract


def sqlite_fixture() -> bytes:
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, token TEXT)")
        connection.execute("INSERT INTO users (token) VALUES ('database-secret')")
        connection.execute("PRAGMA user_version=7")
        connection.commit()
        return connection.serialize()
    finally:
        connection.close()


def recovery_files(*, malformed_metadata: bool = False) -> dict[str, bytes]:
    private_key = base64.b64encode(b"s" * 32)
    standalone_psk = base64.b64encode(b"g" * 32)
    peer_public_key = base64.b64encode(b"k" * 32)
    peer_psk = base64.b64encode(b"p" * 32)
    source_line = (
        "source_overlay=deadbeecontainer_name=amnezia-awg2\n"
        if malformed_metadata
        else "source_overlay=deadbee\ncontainer_name=amnezia-awg2\n"
    )
    metadata = (
        "format=amn2-full-recovery-v1\n"
        "created_utc=2026-07-13T00:00:00Z\n"
        + source_line
        + "container_image_id=sha256:test\n"
        "restore_apply_performed=false\n"
        "service_restart_performed=false\n"
    ).encode()
    unit = (
        b"[Unit]\nDescription=test\n[Service]\n"
        b"EnvironmentFile=/opt/amn2/.env\nExecStart=/bin/false\n[Install]\n"
    )
    files = {
        "container/awg/awg0.conf": (
            b"[Interface]\nPrivateKey = "
            + private_key
            + b"\n[Peer]\nPublicKey = "
            + peer_public_key
            + b"\nPresharedKey = "
            + peer_psk
            + b"\n"
        ),
        "container/awg/wireguard_psk.key": standalone_psk,
        "container/awg/wireguard_server_private_key.key": private_key,
        "container/awg/wireguard_server_public_key.key": base64.b64encode(b"u" * 32),
        "container/start.sh": b"#!/bin/sh\necho original\n",
        "host/amneziya.sqlite3": sqlite_fixture(),
        "host/app.env": b"APP_TOKEN=environment-secret\nPORT=3030\n",
        "host/servers.yml": b"password: yaml-secret\n",
        "host/source_overlay_commit": b"deadbee\n",
        "metadata.txt": metadata,
        "systemd/amneziya-bot.service": unit,
        "systemd/amneziya-web.service": unit,
    }
    files[MANIFEST_NAME] = build_manifest(files)
    return files


def runtime_complete_recovery_files() -> dict[str, bytes]:
    files = recovery_files()
    archive, image_id = docker_image_archive()
    diff_ids = docker_image_diff_ids(archive)
    inspect_bytes, _fixture_image_id = docker_inspect()
    inspect_rows = json.loads(inspect_bytes)
    inspect_rows[0]["Image"] = image_id
    source_bundle = source_archive()
    source_digest = hashlib.sha256(source_bundle).hexdigest()
    files["metadata.txt"] = files["metadata.txt"].replace(
        b"format=amn2-full-recovery-v1",
        b"format=amn2-full-recovery-v2",
    ).replace(
        b"container_image_id=sha256:test",
        f"container_image_id={image_id}".encode(),
    ) + f"source_archive_sha256={source_digest}\n".encode()
    files["container/runtime.json"] = normalize_runtime_contract(
        json.dumps(inspect_rows).encode(),
        image_id,
        docker_image_inspect(image_id, diff_ids),
    )
    files["container/image.tar"] = archive
    files["host/source.tar.gz"] = source_bundle
    files[MANIFEST_NAME] = build_manifest(
        {name: value for name, value in files.items() if name != MANIFEST_NAME}
    )
    return files


def tar_bytes(files: dict[str, bytes], *, unsafe_name: str | None = None) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as archive:
        for name, value in files.items():
            info = tarfile.TarInfo(f"./{name}")
            info.size = len(value)
            archive.addfile(info, io.BytesIO(value))
        if unsafe_name:
            info = tarfile.TarInfo(unsafe_name)
            info.size = 1
            archive.addfile(info, io.BytesIO(b"x"))
    return output.getvalue()


def encrypted_fixture(tmp_path: Path, files: dict[str, bytes]) -> tuple[Path, Path]:
    key = Fernet.generate_key()
    bundle = tmp_path / "recovery.enc"
    key_file = tmp_path / "recovery.key"
    bundle.write_bytes(Fernet(key).encrypt(tar_bytes(files)))
    key_file.write_bytes(key + b"\n")
    return bundle, key_file


def sanitized_files_fixture(tmp_path: Path) -> dict[str, bytes]:
    bundle, key_file = encrypted_fixture(tmp_path, recovery_files())
    sanitized = tmp_path / "sanitized.tar.gz"
    verify_encrypted_bundle(
        bundle, key_file, hashlib.sha256(bundle.read_bytes()).hexdigest(), sanitized
    )
    return load_tar_files(sanitized.read_bytes())


def test_verify_encrypted_builds_secret_free_schema_only_fixture(tmp_path: Path) -> None:
    bundle, key_file = encrypted_fixture(tmp_path, recovery_files())
    sanitized = tmp_path / "sanitized.tar.gz"

    report = verify_encrypted_bundle(
        bundle, key_file, hashlib.sha256(bundle.read_bytes()).hexdigest(), sanitized
    )

    assert report["verdict"] == "passed"
    assert report["production_plaintext_written"] is False
    sanitized_files = load_tar_files(sanitized.read_bytes())
    validate_sanitized_files(sanitized_files)
    combined = b"\n".join(sanitized_files.values())
    assert b"environment-secret" not in combined
    assert b"yaml-secret" not in combined
    assert b"database-secret" not in combined
    assert private_key_not_present(combined)


def test_verify_hybrid_builds_secret_free_schema_only_fixture(tmp_path: Path) -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    bundle = tmp_path / "recovery.hybrid.enc"
    private_key_file = tmp_path / "recovery-private.pem"
    bundle.write_bytes(encrypt_hybrid(tar_bytes(recovery_files()), public_pem))
    private_key_file.write_bytes(private_pem)
    sanitized = tmp_path / "sanitized.tar.gz"

    report = verify_hybrid_bundle(
        bundle,
        private_key_file,
        hashlib.sha256(bundle.read_bytes()).hexdigest(),
        sanitized,
    )

    assert report["verdict"] == "passed"
    assert report["encryption"] == "rsa-oaep-sha256+fernet"
    assert report["production_plaintext_written"] is False
    combined = b"\n".join(load_tar_files(sanitized.read_bytes()).values())
    assert b"environment-secret" not in combined
    assert b"yaml-secret" not in combined
    assert b"database-secret" not in combined
    assert private_key_not_present(combined)


def test_verify_hybrid_accepts_runtime_complete_v2_without_exporting_image(
    tmp_path: Path,
) -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    bundle = tmp_path / "recovery-v2.hybrid.enc"
    private_key_file = tmp_path / "recovery-private.pem"
    bundle.write_bytes(
        encrypt_hybrid(tar_bytes(runtime_complete_recovery_files()), public_pem)
    )
    private_key_file.write_bytes(private_pem)
    sanitized = tmp_path / "sanitized-v2.tar.gz"

    report = verify_hybrid_bundle(
        bundle,
        private_key_file,
        hashlib.sha256(bundle.read_bytes()).hexdigest(),
        sanitized,
    )

    assert report["verdict"] == "passed"
    assert report["source"]["format"] == "amn2-full-recovery-v2"
    assert report["source"]["runtime_contract"] == "passed"
    assert report["source"]["image_archive"]["layer_count"] == 1
    sanitized_files = load_tar_files(sanitized.read_bytes())
    assert "container/runtime.json" not in sanitized_files
    assert "container/image.tar" not in sanitized_files


def test_runtime_complete_v2_requires_image_archive(tmp_path: Path) -> None:
    files = runtime_complete_recovery_files()
    files.pop("container/image.tar")
    files[MANIFEST_NAME] = build_manifest(
        {name: value for name, value in files.items() if name != MANIFEST_NAME}
    )
    bundle, key_file = encrypted_fixture(tmp_path, files)

    with pytest.raises(VerificationError, match="required recovery files are missing"):
        verify_encrypted_bundle(
            bundle,
            key_file,
            hashlib.sha256(bundle.read_bytes()).hexdigest(),
            tmp_path / "sanitized.tar.gz",
        )


def test_restore_gate_can_require_runtime_complete_v2_and_source_digest() -> None:
    files = runtime_complete_recovery_files()
    source_digest = hashlib.sha256(files["host/source.tar.gz"]).hexdigest()

    report = validate_recovery_files(
        files,
        required_format="amn2-full-recovery-v2",
        expected_source_archive_sha256=source_digest,
    )

    assert report["format"] == "amn2-full-recovery-v2"
    assert report["source_archive"]["sha256"] == source_digest


def test_restore_gate_rejects_changed_executable_config_with_same_rootfs() -> None:
    files = runtime_complete_recovery_files()
    changed_config = docker_image_runtime_config()
    changed_config["Healthcheck"] = {"Test": ["CMD-SHELL", "/bin/true"]}
    changed_archive, _changed_image_id = docker_image_archive(
        runtime_config=changed_config
    )
    files["container/image.tar"] = changed_archive
    files[MANIFEST_NAME] = build_manifest(
        {name: value for name, value in files.items() if name != MANIFEST_NAME}
    )

    with pytest.raises(VerificationError, match="executable config"):
        validate_recovery_files(
            files,
            required_format="amn2-full-recovery-v2",
            expected_source_archive_sha256=hashlib.sha256(
                files["host/source.tar.gz"]
            ).hexdigest(),
        )


def test_restore_gate_required_v2_rejects_legacy_v1() -> None:
    with pytest.raises(VerificationError, match="required recovery format"):
        validate_recovery_files(
            recovery_files(), required_format="amn2-full-recovery-v2"
        )


def test_restore_gate_attests_required_v2_and_external_source_digest() -> None:
    files = runtime_complete_recovery_files()
    source_digest = hashlib.sha256(files["host/source.tar.gz"]).hexdigest()

    report = validate_recovery_files(
        files,
        required_format="amn2-full-recovery-v2",
        expected_source_archive_sha256=source_digest,
    )

    assert report["verification_policy"] == {
        "external_source_archive_sha256_verified": True,
        "gate_mode": "restore_001a_runtime_complete_v2",
        "required_format": "amn2-full-recovery-v2",
    }


def test_external_source_digest_without_required_v2_is_rejected() -> None:
    files = runtime_complete_recovery_files()
    source_digest = hashlib.sha256(files["host/source.tar.gz"]).hexdigest()

    with pytest.raises(VerificationError, match="requires required v2 format"):
        validate_recovery_files(
            files,
            expected_source_archive_sha256=source_digest,
        )


def test_generic_v2_report_is_explicitly_not_restore_gate_evidence() -> None:
    report = validate_recovery_files(runtime_complete_recovery_files())

    assert report["verification_policy"] == {
        "external_source_archive_sha256_verified": False,
        "gate_mode": "generic_bundle_consistency",
        "required_format": None,
    }


def test_metadata_line_join_is_reported_as_warning(tmp_path: Path) -> None:
    bundle, key_file = encrypted_fixture(
        tmp_path, recovery_files(malformed_metadata=True)
    )
    sanitized = tmp_path / "sanitized.tar.gz"

    report = verify_encrypted_bundle(
        bundle, key_file, hashlib.sha256(bundle.read_bytes()).hexdigest(), sanitized
    )

    assert report["verdict"] == "passed_with_warning"
    assert "metadata_missing_container_name" in report["source"]["metadata_warnings"]
    assert "metadata_source_overlay_mismatch" in report["source"]["metadata_warnings"]


def test_standalone_psk_may_differ_from_per_peer_psk(tmp_path: Path) -> None:
    files = recovery_files()
    standalone_psk = files["container/awg/wireguard_psk.key"].strip()
    assert standalone_psk not in files["container/awg/awg0.conf"]
    bundle, key_file = encrypted_fixture(tmp_path, files)

    report = verify_encrypted_bundle(
        bundle,
        key_file,
        hashlib.sha256(bundle.read_bytes()).hexdigest(),
        tmp_path / "sanitized.tar.gz",
    )

    assert report["source"]["awg_peer_count"] == 1
    assert report["source"]["awg_peer_psk_count"] == 1
    assert (
        report["source"]["awg_psk_contract"]
        == "standalone_material_and_per_peer_keys_valid"
    )


def test_invalid_peer_psk_is_rejected(tmp_path: Path) -> None:
    files = recovery_files()
    files["container/awg/awg0.conf"] = files["container/awg/awg0.conf"].replace(
        base64.b64encode(b"p" * 32), b"not-a-wireguard-key"
    )
    files[MANIFEST_NAME] = build_manifest(
        {name: value for name, value in files.items() if name != MANIFEST_NAME}
    )
    bundle, key_file = encrypted_fixture(tmp_path, files)

    with pytest.raises(VerificationError, match="AWG peer PSK is not valid base64"):
        verify_encrypted_bundle(
            bundle,
            key_file,
            hashlib.sha256(bundle.read_bytes()).hexdigest(),
            tmp_path / "sanitized.tar.gz",
        )


def test_peer_psk_validation_is_scoped_to_each_peer(tmp_path: Path) -> None:
    files = recovery_files()
    second_public_key = base64.b64encode(b"q" * 32)
    extra_psk = base64.b64encode(b"x" * 32)
    files["container/awg/awg0.conf"] += (
        b"PresharedKey = "
        + extra_psk
        + b"\n[Peer]\nPublicKey = "
        + second_public_key
        + b"\n"
    )
    files[MANIFEST_NAME] = build_manifest(
        {name: value for name, value in files.items() if name != MANIFEST_NAME}
    )
    bundle, key_file = encrypted_fixture(tmp_path, files)

    with pytest.raises(
        VerificationError, match="each have one public key and one PSK"
    ):
        verify_encrypted_bundle(
            bundle,
            key_file,
            hashlib.sha256(bundle.read_bytes()).hexdigest(),
            tmp_path / "sanitized.tar.gz",
        )


def test_manifest_mismatch_is_rejected(tmp_path: Path) -> None:
    files = recovery_files()
    files["host/app.env"] += b"changed=true\n"
    bundle, key_file = encrypted_fixture(tmp_path, files)

    with pytest.raises(VerificationError, match="manifest hash mismatch"):
        verify_encrypted_bundle(
            bundle,
            key_file,
            hashlib.sha256(bundle.read_bytes()).hexdigest(),
            tmp_path / "sanitized.tar.gz",
        )


def test_path_traversal_member_is_rejected() -> None:
    archive = tar_bytes(recovery_files(), unsafe_name="../escape")

    with pytest.raises(VerificationError, match="unsafe archive member path"):
        load_tar_files(archive)


def test_sanitized_fixture_requires_complete_file_contract(tmp_path: Path) -> None:
    sanitized_files = sanitized_files_fixture(tmp_path)
    sanitized_files.pop("systemd/amneziya-bot.service")
    sanitized_files[MANIFEST_NAME] = build_manifest(
        {name: value for name, value in sanitized_files.items() if name != MANIFEST_NAME}
    )

    with pytest.raises(
        VerificationError, match="required sanitized rehearsal files are missing"
    ):
        validate_sanitized_files(sanitized_files)


def test_sanitized_fixture_rejects_unexpected_file(tmp_path: Path) -> None:
    sanitized_files = sanitized_files_fixture(tmp_path)
    sanitized_files["unexpected.txt"] = b"must-not-be-extracted\n"
    sanitized_files[MANIFEST_NAME] = build_manifest(
        {name: value for name, value in sanitized_files.items() if name != MANIFEST_NAME}
    )

    with pytest.raises(VerificationError, match="contains unexpected files"):
        validate_sanitized_files(sanitized_files)


def test_sanitized_fixture_requires_exact_start_guard(tmp_path: Path) -> None:
    sanitized_files = sanitized_files_fixture(tmp_path)
    sanitized_files["container/start.sh"] = (
        b"#!/bin/sh\necho unsafe-command\nexit 64\n"
    )
    sanitized_files[MANIFEST_NAME] = build_manifest(
        {name: value for name, value in sanitized_files.items() if name != MANIFEST_NAME}
    )

    with pytest.raises(VerificationError, match="start guard failed"):
        validate_sanitized_files(sanitized_files)


def test_sanitized_fixture_rejects_value_bearing_env(tmp_path: Path) -> None:
    sanitized_files = sanitized_files_fixture(tmp_path)
    sanitized_files["host/app.env"] = b"TOKEN=must-not-leave-workstation\n"
    sanitized_files[MANIFEST_NAME] = build_manifest(
        {name: value for name, value in sanitized_files.items() if name != MANIFEST_NAME}
    )

    with pytest.raises(VerificationError, match="sanitized env"):
        validate_sanitized_files(sanitized_files)


def private_key_not_present(combined: bytes) -> bool:
    return base64.b64encode(b"s" * 32) not in combined
