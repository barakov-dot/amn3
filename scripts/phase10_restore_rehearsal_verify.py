#!/usr/bin/env python
"""Verify an encrypted AMN2 recovery bundle and build a safe rehearsal fixture."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import io
import json
import re
import sqlite3
import sys
import tarfile
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence

try:
    from scripts.phase10_recovery_crypto import (
        RecoveryCryptoError,
        decrypt_hybrid,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from phase10_recovery_crypto import RecoveryCryptoError, decrypt_hybrid


MAX_ARCHIVE_FILES = 256
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_ENCRYPTED_BYTES = 128 * 1024 * 1024
MAX_PRIVATE_KEY_BYTES = 64 * 1024
MANIFEST_NAME = "manifest.sha256"
SANITIZED_SENTINEL = "SANITIZED_REHEARSAL_ONLY"
SANITIZED_ENV_HEADER = (
    "# Sanitized AMN2 restore rehearsal fixture. No values are retained."
)
SANITIZED_AWG_CONFIG = (
    "[Interface]\n"
    "PrivateKey = REDACTED_FOR_REHEARSAL\n"
    "Address = 10.255.255.1/24\n"
    "ListenPort = 51820\n\n"
    "[Peer]\n"
    "PublicKey = REDACTED_FOR_REHEARSAL\n"
    "PresharedKey = REDACTED_FOR_REHEARSAL\n"
    "AllowedIPs = 10.255.255.2/32\n"
).encode("ascii")
SANITIZED_BLOCKED_START = (
    "#!/bin/sh\n"
    "echo 'sanitized restore rehearsal fixture: service start blocked' >&2\n"
    "exit 64\n"
).encode("ascii")

REQUIRED_RECOVERY_FILES = {
    "container/awg/awg0.conf",
    "container/awg/wireguard_psk.key",
    "container/awg/wireguard_server_private_key.key",
    "container/awg/wireguard_server_public_key.key",
    "container/start.sh",
    "host/amneziya.sqlite3",
    "host/app.env",
    "host/servers.yml",
    "host/source_overlay_commit",
    "metadata.txt",
    "systemd/amneziya-bot.service",
    "systemd/amneziya-web.service",
    MANIFEST_NAME,
}
REQUIRED_SANITIZED_FILES = REQUIRED_RECOVERY_FILES | {SANITIZED_SENTINEL}


class VerificationError(RuntimeError):
    """A safe, non-secret recovery verification failure."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_member_name(name: str) -> str:
    normalized = name.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or ".." in path.parts
        or (path.parts and ":" in path.parts[0])
    ):
        raise VerificationError("unsafe archive member path")
    return path.as_posix()


def load_tar_files(archive_bytes: bytes) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    total_bytes = 0
    try:
        archive = tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz")
    except tarfile.TarError as exc:
        raise VerificationError("bundle is not a valid gzip tar archive") from exc

    with archive:
        members = archive.getmembers()
        if len(members) > MAX_ARCHIVE_FILES:
            raise VerificationError("archive member limit exceeded")
        for member in members:
            name = normalize_member_name(member.name)
            if member.isdir():
                continue
            if not member.isfile():
                raise VerificationError("archive contains a non-regular member")
            if name in files:
                raise VerificationError("archive contains duplicate member paths")
            total_bytes += member.size
            if total_bytes > MAX_ARCHIVE_BYTES:
                raise VerificationError("archive expanded-size limit exceeded")
            source = archive.extractfile(member)
            if source is None:
                raise VerificationError("archive member cannot be read")
            files[name] = source.read()
    return files


def parse_manifest(value: bytes) -> dict[str, str]:
    entries: dict[str, str] = {}
    try:
        lines = value.decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        raise VerificationError("manifest is not ASCII") from exc
    for line in lines:
        match = re.fullmatch(r"([0-9a-fA-F]{64})  (.+)", line)
        if not match:
            raise VerificationError("manifest contains a malformed entry")
        name = normalize_member_name(match.group(2))
        if name in entries:
            raise VerificationError("manifest contains duplicate paths")
        entries[name] = match.group(1).lower()
    return entries


def verify_manifest(files: Mapping[str, bytes]) -> int:
    manifest_bytes = files.get(MANIFEST_NAME)
    if manifest_bytes is None:
        raise VerificationError("manifest is missing")
    entries = parse_manifest(manifest_bytes)
    expected_paths = set(files) - {MANIFEST_NAME}
    if set(entries) != expected_paths:
        raise VerificationError("manifest coverage does not match archive files")
    for name, expected_hash in entries.items():
        if sha256_bytes(files[name]) != expected_hash:
            raise VerificationError("manifest hash mismatch")
    return len(entries)


def parse_metadata(value: bytes) -> dict[str, str]:
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise VerificationError("metadata is not UTF-8") from exc
    result: dict[str, str] = {}
    for line in text.splitlines():
        if not line:
            continue
        if "=" not in line:
            raise VerificationError("metadata contains a malformed line")
        key, item = line.split("=", 1)
        if not key or key in result:
            raise VerificationError("metadata contains an invalid key")
        result[key] = item
    return result


def validate_sqlite(value: bytes, *, require_empty: bool = False) -> dict[str, object]:
    connection = sqlite3.connect(":memory:")
    try:
        connection.deserialize(value)
        integrity_rows = [row[0] for row in connection.execute("PRAGMA integrity_check")]
        if integrity_rows != ["ok"]:
            raise VerificationError("SQLite integrity_check failed")
        foreign_key_rows = list(connection.execute("PRAGMA foreign_key_check"))
        if foreign_key_rows:
            raise VerificationError("SQLite foreign_key_check failed")
        tables = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        if not tables:
            raise VerificationError("SQLite schema has no application tables")
        total_rows = 0
        if require_empty:
            for table in tables:
                escaped = table.replace('"', '""')
                total_rows += connection.execute(
                    f'SELECT COUNT(*) FROM "{escaped}"'
                ).fetchone()[0]
            if total_rows:
                raise VerificationError("sanitized SQLite fixture contains rows")
        user_version = connection.execute("PRAGMA user_version").fetchone()[0]
        return {
            "integrity": "ok",
            "foreign_keys": "ok",
            "table_count": len(tables),
            "total_rows": total_rows if require_empty else "not_exported",
            "user_version": user_version,
        }
    except sqlite3.DatabaseError as exc:
        raise VerificationError("SQLite bundle cannot be opened") from exc
    finally:
        connection.close()


def schema_only_sqlite(value: bytes) -> bytes:
    source = sqlite3.connect(":memory:")
    destination = sqlite3.connect(":memory:")
    try:
        source.deserialize(value)
        schema_rows = list(
            source.execute(
                "SELECT type, name, sql FROM sqlite_master "
                "WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' "
                "ORDER BY CASE type WHEN 'table' THEN 0 WHEN 'index' THEN 1 "
                "WHEN 'view' THEN 2 ELSE 3 END, name"
            )
        )
        for _kind, _name, statement in schema_rows:
            destination.execute(statement)
        user_version = source.execute("PRAGMA user_version").fetchone()[0]
        destination.execute(f"PRAGMA user_version={int(user_version)}")
        destination.commit()
        return destination.serialize()
    except sqlite3.DatabaseError as exc:
        raise VerificationError("SQLite schema-only fixture cannot be built") from exc
    finally:
        source.close()
        destination.close()


def require_text_sections(value: bytes, sections: Sequence[str], label: str) -> None:
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise VerificationError(f"{label} is not UTF-8") from exc
    for section in sections:
        if section not in text:
            raise VerificationError(f"{label} is missing a required section")


def validate_wireguard_key(encoded: str, label: str) -> None:
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise VerificationError(f"{label} is not valid base64") from exc
    if len(decoded) != 32:
        raise VerificationError(f"{label} does not encode 32 bytes")


def parse_awg_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    current_name: str | None = None
    current_lines: list[str] = []
    for raw_line in text.splitlines():
        match = re.fullmatch(r"\s*\[([^]]+)]\s*", raw_line)
        if match:
            if current_name is not None:
                sections.append((current_name, "\n".join(current_lines)))
            current_name = match.group(1)
            current_lines = []
            continue
        if current_name is None:
            stripped = raw_line.strip()
            if stripped and not stripped.startswith(("#", ";")):
                raise VerificationError("AWG config has content before its first section")
            continue
        current_lines.append(raw_line)
    if current_name is not None:
        sections.append((current_name, "\n".join(current_lines)))
    return sections


def awg_directive_values(section: str, directive: str) -> list[str]:
    return re.findall(
        rf"(?m)^\s*{re.escape(directive)}\s*=\s*(\S+)\s*$",
        section,
    )


def validate_recovery_files(files: Mapping[str, bytes]) -> dict[str, object]:
    missing = sorted(REQUIRED_RECOVERY_FILES - set(files))
    if missing:
        raise VerificationError("required recovery files are missing")
    manifest_entries = verify_manifest(files)
    metadata = parse_metadata(files["metadata.txt"])
    if metadata.get("format") != "amn2-full-recovery-v1":
        raise VerificationError("recovery format is unsupported")
    if metadata.get("restore_apply_performed") != "false":
        raise VerificationError("bundle metadata does not prove no restore apply")
    if metadata.get("service_restart_performed") != "false":
        raise VerificationError("bundle metadata does not prove no service restart")

    try:
        source_overlay = files["host/source_overlay_commit"].decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise VerificationError("source overlay marker is not ASCII") from exc
    if not re.fullmatch(r"[0-9a-f]{7,40}", source_overlay):
        raise VerificationError("source overlay marker is invalid")

    warnings: list[str] = []
    for key in ("created_utc", "source_overlay", "container_name", "container_image_id"):
        if not metadata.get(key):
            warnings.append(f"metadata_missing_{key}")
    if metadata.get("source_overlay") != source_overlay:
        warnings.append("metadata_source_overlay_mismatch")

    awg = files["container/awg/awg0.conf"]
    require_text_sections(awg, ("[Interface]", "[Peer]"), "AWG config")
    try:
        awg_text = awg.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise VerificationError("AWG config is not UTF-8") from exc
    sections = parse_awg_sections(awg_text)
    if any(name not in {"Interface", "Peer"} for name, _body in sections):
        raise VerificationError("AWG config contains an unsupported section")
    interfaces = [body for name, body in sections if name == "Interface"]
    peers = [body for name, body in sections if name == "Peer"]
    if len(interfaces) != 1:
        raise VerificationError("AWG config must have exactly one interface")
    if not peers:
        raise VerificationError("AWG config has no peers")
    encoded_keys: dict[str, str] = {}
    for name in (
        "container/awg/wireguard_psk.key",
        "container/awg/wireguard_server_private_key.key",
        "container/awg/wireguard_server_public_key.key",
    ):
        try:
            encoded = files[name].decode("ascii").strip()
        except UnicodeDecodeError as exc:
            raise VerificationError("AWG key material is not ASCII") from exc
        validate_wireguard_key(encoded, "AWG key material")
        encoded_keys[name] = encoded
    private_values = awg_directive_values(interfaces[0], "PrivateKey")
    if private_values != [
        encoded_keys["container/awg/wireguard_server_private_key.key"]
    ]:
        raise VerificationError("AWG server private key does not match config")
    peer_psks: list[str] = []
    for peer in peers:
        public_keys = awg_directive_values(peer, "PublicKey")
        psk_values = awg_directive_values(peer, "PresharedKey")
        if len(public_keys) != 1 or len(psk_values) != 1:
            raise VerificationError("AWG peers must each have one public key and one PSK")
        validate_wireguard_key(public_keys[0], "AWG peer public key")
        validate_wireguard_key(psk_values[0], "AWG peer PSK")
        peer_psks.append(psk_values[0])

    for name in ("systemd/amneziya-web.service", "systemd/amneziya-bot.service"):
        require_text_sections(
            files[name],
            ("[Unit]", "[Service]", "[Install]", "EnvironmentFile=", "ExecStart="),
            "systemd unit",
        )
    sqlite_report = validate_sqlite(files["host/amneziya.sqlite3"])
    return {
        "archive_file_count": len(files),
        "manifest_entries": manifest_entries,
        "metadata_contract": "warning" if warnings else "passed",
        "metadata_warnings": warnings,
        "source_overlay": source_overlay,
        "awg_peer_count": len(peers),
        "awg_peer_psk_count": len(peer_psks),
        "awg_psk_contract": "standalone_material_and_per_peer_keys_valid",
        "sqlite": sqlite_report,
        "systemd_contract": "passed",
        "critical_contracts": "passed",
    }


def build_manifest(files: Mapping[str, bytes]) -> bytes:
    lines = [f"{sha256_bytes(files[name])}  ./{name}" for name in sorted(files)]
    return ("\n".join(lines) + "\n").encode("ascii")


def safe_env_inventory(value: bytes) -> bytes:
    keys: set[str] = set()
    for raw_line in value.decode("utf-8", "replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            keys.add(key)
    inventory = "\n".join(f"# key_present={key}" for key in sorted(keys))
    return (SANITIZED_ENV_HEADER + "\n" + inventory + "\n").encode("utf-8")


def sanitized_systemd_unit(label: str) -> bytes:
    return (
        "[Unit]\n"
        f"Description=Sanitized AMN2 {label} restore rehearsal fixture\n"
        "\n"
        "[Service]\n"
        "Type=oneshot\n"
        "ExecStart=/bin/false\n"
        "\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n"
    ).encode("utf-8")


def build_sanitized_files(
    source_files: Mapping[str, bytes], source_report: Mapping[str, object]
) -> dict[str, bytes]:
    metadata = (
        "format=amn2-full-recovery-v1-sanitized\n"
        "source_format=amn2-full-recovery-v1\n"
        f"source_overlay={source_report['source_overlay']}\n"
        "sanitized_fixture=true\n"
        "production_secrets=false\n"
        "service_start_allowed=false\n"
        "network_listener_allowed=false\n"
    ).encode("utf-8")
    files = {
        SANITIZED_SENTINEL: (
            b"production_secrets=false\nservice_start_allowed=false\n"
        ),
        "container/awg/awg0.conf": SANITIZED_AWG_CONFIG,
        "container/awg/wireguard_psk.key": b"REDACTED_FOR_REHEARSAL\n",
        "container/awg/wireguard_server_private_key.key": (
            b"REDACTED_FOR_REHEARSAL\n"
        ),
        "container/awg/wireguard_server_public_key.key": (
            b"REDACTED_FOR_REHEARSAL\n"
        ),
        "container/start.sh": SANITIZED_BLOCKED_START,
        "host/amneziya.sqlite3": schema_only_sqlite(
            source_files["host/amneziya.sqlite3"]
        ),
        "host/app.env": safe_env_inventory(source_files["host/app.env"]),
        "host/servers.yml": b"servers: []\n",
        "host/source_overlay_commit": (
            str(source_report["source_overlay"]) + "\n"
        ).encode("ascii"),
        "metadata.txt": metadata,
        "systemd/amneziya-bot.service": sanitized_systemd_unit("bot"),
        "systemd/amneziya-web.service": sanitized_systemd_unit("web"),
    }
    files[MANIFEST_NAME] = build_manifest(files)
    return files


def write_tar(files: Mapping[str, bytes], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as output:
        with tarfile.open(fileobj=output, mode="w:gz", format=tarfile.PAX_FORMAT) as archive:
            for name in sorted(files):
                value = files[name]
                info = tarfile.TarInfo(f"./{name}")
                info.size = len(value)
                info.mode = 0o700 if name == "container/start.sh" else 0o600
                info.uid = 0
                info.gid = 0
                info.mtime = 0
                archive.addfile(info, io.BytesIO(value))


def verify_decrypted_recovery_bundle(
    decrypted: bytes,
    actual_hash: str,
    sanitized_output: Path,
    *,
    mode: str,
) -> dict[str, object]:
    files = load_tar_files(decrypted)
    source_report = validate_recovery_files(files)
    sanitized_files = build_sanitized_files(files, source_report)
    sanitized_report = validate_sanitized_files(sanitized_files)
    write_tar(sanitized_files, sanitized_output)
    written_report = validate_sanitized_files(
        load_tar_files(sanitized_output.read_bytes())
    )
    if written_report != sanitized_report:
        raise VerificationError("written sanitized fixture report is inconsistent")
    return {
        "mode": mode,
        "bundle_sha256": actual_hash,
        "decrypt": "passed",
        "production_plaintext_written": False,
        "source": source_report,
        "sanitized_fixture": {
            **sanitized_report,
            "sha256": sha256_path(sanitized_output),
            "bytes": sanitized_output.stat().st_size,
        },
        "verdict": "passed_with_warning"
        if source_report["metadata_warnings"]
        else "passed",
    }


def verify_encrypted_bundle(
    bundle_path: Path,
    key_path: Path,
    expected_sha256: str,
    sanitized_output: Path,
) -> dict[str, object]:
    bundle_bytes = bundle_path.read_bytes()
    if len(bundle_bytes) > MAX_ENCRYPTED_BYTES:
        raise VerificationError("encrypted bundle size limit exceeded")
    actual_hash = sha256_bytes(bundle_bytes)
    if actual_hash != expected_sha256.lower():
        raise VerificationError("encrypted bundle SHA-256 mismatch")
    try:
        from cryptography.fernet import Fernet, InvalidToken
    except ImportError as exc:
        raise VerificationError("cryptography dependency is unavailable") from exc
    try:
        decrypted = Fernet(key_path.read_bytes().strip()).decrypt(bundle_bytes)
    except (ValueError, InvalidToken) as exc:
        raise VerificationError("encrypted bundle authentication failed") from exc
    return verify_decrypted_recovery_bundle(
        decrypted,
        actual_hash,
        sanitized_output,
        mode="encrypted-production-local-memory-only",
    )


def verify_hybrid_bundle(
    bundle_path: Path,
    private_key_path: Path,
    expected_sha256: str,
    sanitized_output: Path,
) -> dict[str, object]:
    bundle_bytes = bundle_path.read_bytes()
    if len(bundle_bytes) > MAX_ENCRYPTED_BYTES:
        raise VerificationError("encrypted bundle size limit exceeded")
    actual_hash = sha256_bytes(bundle_bytes)
    if actual_hash != expected_sha256.lower():
        raise VerificationError("encrypted bundle SHA-256 mismatch")
    if private_key_path.stat().st_size > MAX_PRIVATE_KEY_BYTES:
        raise VerificationError("recovery private key exceeds the size limit")
    try:
        decrypted = decrypt_hybrid(bundle_bytes, private_key_path.read_bytes())
    except RecoveryCryptoError as exc:
        raise VerificationError(str(exc)) from exc
    report = verify_decrypted_recovery_bundle(
        decrypted,
        actual_hash,
        sanitized_output,
        mode="hybrid-encrypted-production-local-memory-only",
    )
    report["encryption"] = "rsa-oaep-sha256+fernet"
    return report


def validate_sanitized_files(files: Mapping[str, bytes]) -> dict[str, object]:
    actual_files = set(files)
    missing = sorted(REQUIRED_SANITIZED_FILES - actual_files)
    if missing:
        raise VerificationError("required sanitized rehearsal files are missing")
    unexpected = sorted(actual_files - REQUIRED_SANITIZED_FILES)
    if unexpected:
        raise VerificationError("sanitized rehearsal contains unexpected files")
    manifest_entries = verify_manifest(files)
    metadata = parse_metadata(files.get("metadata.txt", b""))
    required_metadata = {
        "format": "amn2-full-recovery-v1-sanitized",
        "source_format": "amn2-full-recovery-v1",
        "sanitized_fixture": "true",
        "production_secrets": "false",
        "service_start_allowed": "false",
        "network_listener_allowed": "false",
    }
    expected_metadata_keys = set(required_metadata) | {"source_overlay"}
    if set(metadata) != expected_metadata_keys or any(
        metadata.get(key) != value for key, value in required_metadata.items()
    ):
        raise VerificationError("sanitized fixture metadata guard failed")
    source_overlay = metadata["source_overlay"]
    if not re.fullmatch(r"[0-9a-f]{7,40}", source_overlay):
        raise VerificationError("sanitized source overlay marker is invalid")
    if files["host/source_overlay_commit"] != (source_overlay + "\n").encode("ascii"):
        raise VerificationError("sanitized source overlay markers do not match")
    if files[SANITIZED_SENTINEL] != (
        b"production_secrets=false\nservice_start_allowed=false\n"
    ):
        raise VerificationError("sanitized rehearsal sentinel is invalid")
    if files["container/start.sh"] != SANITIZED_BLOCKED_START:
        raise VerificationError("sanitized fixture start guard failed")
    try:
        env_text = files["host/app.env"].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise VerificationError("sanitized env is not UTF-8") from exc
    env_lines = [line for line in env_text.splitlines() if line]
    if not env_lines or env_lines[0] != SANITIZED_ENV_HEADER:
        raise VerificationError("sanitized env header is invalid")
    env_keys: list[str] = []
    for line in env_lines[1:]:
        match = re.fullmatch(r"# key_present=([A-Za-z_][A-Za-z0-9_]*)", line)
        if not match:
            raise VerificationError("sanitized env inventory is invalid")
        env_keys.append(match.group(1))
    expected_env = (
        SANITIZED_ENV_HEADER
        + "\n"
        + "\n".join(
            f"# key_present={key}" for key in sorted(set(env_keys))
        )
        + "\n"
    )
    if env_text != expected_env:
        raise VerificationError("sanitized env inventory is not canonical")
    if files["host/servers.yml"] != b"servers: []\n":
        raise VerificationError("sanitized servers fixture is not empty")
    redacted = b"REDACTED_FOR_REHEARSAL\n"
    for name in (
        "container/awg/wireguard_psk.key",
        "container/awg/wireguard_server_private_key.key",
        "container/awg/wireguard_server_public_key.key",
    ):
        if files[name] != redacted:
            raise VerificationError("sanitized AWG key file is not redacted")
    if files["container/awg/awg0.conf"] != SANITIZED_AWG_CONFIG:
        raise VerificationError("sanitized AWG config is not the exact safe fixture")
    expected_units = {
        "systemd/amneziya-web.service": sanitized_systemd_unit("web"),
        "systemd/amneziya-bot.service": sanitized_systemd_unit("bot"),
    }
    for name, expected_unit in expected_units.items():
        if files[name] != expected_unit:
            raise VerificationError("sanitized systemd unit is not the exact safe fixture")
    sqlite_report = validate_sqlite(
        files.get("host/amneziya.sqlite3", b""), require_empty=True
    )
    return {
        "archive_file_count": len(files),
        "manifest_entries": manifest_entries,
        "sqlite": sqlite_report,
        "production_secrets": False,
        "service_start_allowed": False,
        "contract": "passed",
    }


def verify_sanitized_bundle(
    bundle_path: Path, expected_sha256: str, extract_dir: Path
) -> dict[str, object]:
    bundle_bytes = bundle_path.read_bytes()
    if len(bundle_bytes) > MAX_ENCRYPTED_BYTES:
        raise VerificationError("sanitized fixture size limit exceeded")
    actual_hash = sha256_bytes(bundle_bytes)
    if actual_hash != expected_sha256.lower():
        raise VerificationError("sanitized fixture SHA-256 mismatch")
    files = load_tar_files(bundle_bytes)
    report = validate_sanitized_files(files)
    if extract_dir.exists() and any(extract_dir.iterdir()):
        raise VerificationError("sanitized extraction directory is not empty")
    extract_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    for name, value in files.items():
        target = extract_dir / Path(*PurePosixPath(name).parts)
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with target.open("xb") as output:
            output.write(value)
        target.chmod(0o700 if name == "container/start.sh" else 0o600)
    return {
        "mode": "sanitized-staging-extraction",
        "bundle_sha256": actual_hash,
        **report,
        "extract_dir": str(extract_dir),
        "verdict": "passed",
    }


def write_report(report: Mapping[str, object], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    encrypted = subparsers.add_parser("verify-encrypted")
    encrypted.add_argument("--bundle", type=Path, required=True)
    encrypted.add_argument("--key-file", type=Path, required=True)
    encrypted.add_argument("--expected-sha256", required=True)
    encrypted.add_argument("--sanitized-output", type=Path, required=True)
    encrypted.add_argument("--report-output", type=Path, required=True)

    hybrid = subparsers.add_parser("verify-hybrid")
    hybrid.add_argument("--bundle", type=Path, required=True)
    hybrid.add_argument("--private-key-file", type=Path, required=True)
    hybrid.add_argument("--expected-sha256", required=True)
    hybrid.add_argument("--sanitized-output", type=Path, required=True)
    hybrid.add_argument("--report-output", type=Path, required=True)

    sanitized = subparsers.add_parser("verify-sanitized")
    sanitized.add_argument("--bundle", type=Path, required=True)
    sanitized.add_argument("--expected-sha256", required=True)
    sanitized.add_argument("--extract-dir", type=Path, required=True)
    sanitized.add_argument("--report-output", type=Path, required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "verify-encrypted":
            report = verify_encrypted_bundle(
                args.bundle,
                args.key_file,
                args.expected_sha256,
                args.sanitized_output,
            )
        elif args.command == "verify-hybrid":
            report = verify_hybrid_bundle(
                args.bundle,
                args.private_key_file,
                args.expected_sha256,
                args.sanitized_output,
            )
        else:
            report = verify_sanitized_bundle(
                args.bundle, args.expected_sha256, args.extract_dir
            )
        write_report(report, args.report_output)
    except (OSError, VerificationError) as exc:
        print(f"restore rehearsal verification: FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"restore rehearsal verification: {report['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
