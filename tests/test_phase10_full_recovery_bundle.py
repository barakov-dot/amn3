from __future__ import annotations

import base64
import sqlite3
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from scripts.phase10_full_recovery_bundle import (
    FORMAT,
    MANIFEST_NAME,
    assemble_recovery_files,
    encrypt_recovery_files,
    render_metadata,
    sqlite_backup_bytes,
    write_exclusive,
)
from scripts.phase10_recovery_crypto import decrypt_hybrid
from scripts.phase10_restore_rehearsal_verify import (
    load_tar_files,
    validate_recovery_files,
)


def sqlite_file(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        connection.execute("INSERT INTO users (name) VALUES ('operator')")
        connection.commit()
    finally:
        connection.close()


def source_files(tmp_path: Path) -> dict[str, bytes]:
    database = tmp_path / "amneziya.sqlite3"
    sqlite_file(database)
    private_key = base64.b64encode(b"s" * 32)
    peer_public_key = base64.b64encode(b"p" * 32)
    peer_psk = base64.b64encode(b"k" * 32)
    unit = (
        b"[Unit]\nDescription=test\n[Service]\n"
        b"EnvironmentFile=/opt/amn2/.env\nExecStart=/bin/false\n[Install]\n"
    )
    return {
        "container/awg/awg0.conf": (
            b"[Interface]\nPrivateKey = "
            + private_key
            + b"\n[Peer]\nPublicKey = "
            + peer_public_key
            + b"\nPresharedKey = "
            + peer_psk
            + b"\n"
        ),
        "container/awg/wireguard_psk.key": base64.b64encode(b"g" * 32),
        "container/awg/wireguard_server_private_key.key": private_key,
        "container/awg/wireguard_server_public_key.key": base64.b64encode(b"u" * 32),
        "container/start.sh": b"#!/bin/sh\nexit 0\n",
        "host/amneziya.sqlite3": sqlite_backup_bytes(database),
        "host/app.env": b"APP_SECRET=synthetic\n",
        "host/servers.yml": b"servers: []\n",
        "host/source_overlay_commit": b"deadbee\n",
        "systemd/amneziya-bot.service": unit,
        "systemd/amneziya-web.service": unit,
    }


def test_metadata_writer_emits_canonical_separate_lines() -> None:
    value = render_metadata(
        created_utc="2026-07-14T00:00:00Z",
        source_overlay="deadbee",
        container_name="amneziya-awg2",
        container_image_id="sha256:test",
    )

    assert value.splitlines() == [
        f"format={FORMAT}".encode(),
        b"created_utc=2026-07-14T00:00:00Z",
        b"source_overlay=deadbee",
        b"container_name=amneziya-awg2",
        b"container_image_id=sha256:test",
        b"restore_apply_performed=false",
        b"service_restart_performed=false",
    ]
    assert b"source_overlay=deadbee\ncontainer_name=amneziya-awg2\n" in value


def test_encrypted_writer_output_passes_recovery_verifier(tmp_path: Path) -> None:
    files = assemble_recovery_files(
        source_files(tmp_path),
        created_utc="2026-07-14T00:00:00Z",
        source_overlay="deadbee",
        container_name="amneziya-awg2",
        container_image_id="sha256:test",
    )
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    public_key_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    private_key_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    encrypted = encrypt_recovery_files(files, public_key_pem)
    decrypted = decrypt_hybrid(encrypted, private_key_pem)
    archive_files = load_tar_files(decrypted)

    report = validate_recovery_files(archive_files)

    assert report["metadata_contract"] == "passed"
    assert report["metadata_warnings"] == []
    assert report["source_overlay"] == "deadbee"
    assert report["critical_contracts"] == "passed"
    assert MANIFEST_NAME in archive_files


def test_sqlite_backup_is_consistent_and_preserves_rows(tmp_path: Path) -> None:
    database = tmp_path / "source.sqlite3"
    sqlite_file(database)

    backup = sqlite_backup_bytes(database)
    restored = sqlite3.connect(":memory:")
    try:
        restored.deserialize(backup)
        assert restored.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert restored.execute("SELECT name FROM users").fetchone()[0] == "operator"
    finally:
        restored.close()


def test_encrypted_output_is_created_exclusively_with_no_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "recovery.enc"
    write_exclusive(output, b"first")

    try:
        write_exclusive(output, b"second")
    except FileExistsError:
        pass
    else:
        raise AssertionError("exclusive writer overwrote an existing artifact")

    assert output.read_bytes() == b"first"
