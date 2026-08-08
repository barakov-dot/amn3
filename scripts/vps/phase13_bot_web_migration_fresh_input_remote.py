#!/usr/bin/env python3
"""Fixed-role, read-only fresh-input collector for Phase 13 bot/web migration."""

from __future__ import annotations

from dataclasses import dataclass
import base64
import gzip
import io
import json
from pathlib import Path
import sqlite3
import struct
import sys
import tarfile
from typing import Mapping


FRAME_MAGIC = b"AMN2-PHASE13-FRESH-INPUT-V1\n"
FRAME_ARCHIVE_MAGIC = b"\x1f\x8b"
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_FRAME_BYTES = 64 * 1024 * 1024
MAX_AUDIT_BYTES = 256 * 1024
MAX_ARCHIVE_PLAINTEXT_BYTES = 64 * 1024 * 1024
EXPECTED_ARCHIVE_MEMBERS = {
    "database.sqlite3",
    "runtime.env",
    "server-config.yml",
}

ROLE_CONTRACTS: dict[str, dict[str, object]] = {
    "usa": {
        "database": Path("/opt/amn2/data/amneziya.sqlite3"),
        "application_files": (
            ("runtime.env", Path("/opt/amn2/.env")),
            ("server-config.yml", Path("/opt/amn2/servers.yml")),
        ),
    },
    "spain": {
        "database": Path("/var/lib/amn2-spain/amn2.sqlite3"),
        "application_files": (
            ("runtime.env", Path("/etc/amn2-spain/runtime.env")),
            ("server-config.yml", Path("/var/lib/amn2-spain/server-config.yml")),
        ),
    },
}


class FreshRemoteError(RuntimeError):
    """A secret-safe remote collection failure."""


@dataclass(frozen=True)
class ParsedRoleFrame:
    audit: bytes
    archive: bytes
    files: Mapping[str, bytes]


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sqlite_snapshot_bytes(path: Path) -> bytes:
    try:
        resolved = Path(path).resolve(strict=True)
    except OSError as error:
        raise FreshRemoteError("database unavailable") from error
    if not resolved.is_file() or resolved.stat().st_size > MAX_FILE_BYTES:
        raise FreshRemoteError("database boundary invalid")
    source = sqlite3.connect(resolved.as_uri() + "?mode=ro", uri=True)
    destination = sqlite3.connect(":memory:")
    try:
        source.execute("PRAGMA query_only=ON")
        source.backup(destination)
        if tuple(row[0] for row in destination.execute("PRAGMA integrity_check")) != (
            "ok",
        ):
            raise FreshRemoteError("database integrity failed")
        if destination.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise FreshRemoteError("database foreign keys failed")
        snapshot = destination.serialize()
        if not snapshot or len(snapshot) > MAX_FILE_BYTES:
            raise FreshRemoteError("database snapshot boundary invalid")
        return snapshot
    except sqlite3.DatabaseError as error:
        raise FreshRemoteError("database snapshot failed") from error
    finally:
        source.close()
        destination.close()


def read_fixed_application_file(path: Path) -> bytes:
    try:
        resolved = Path(path).resolve(strict=True)
    except OSError as error:
        raise FreshRemoteError("application data unavailable") from error
    if not resolved.is_file() or resolved.stat().st_size > MAX_FILE_BYTES:
        raise FreshRemoteError("application data boundary invalid")
    value = resolved.read_bytes()
    if not value:
        raise FreshRemoteError("application data empty")
    return value


def deterministic_archive_bytes(files: Mapping[str, bytes]) -> bytes:
    expected = set(files)
    if expected != EXPECTED_ARCHIVE_MEMBERS:
        raise FreshRemoteError("archive member set invalid")
    if any(
        not isinstance(name, str)
        or not name
        or "/" in name
        or "\\" in name
        or name in {".", ".."}
        for name in expected
    ):
        raise FreshRemoteError("archive member invalid")
    if sum(len(value) for value in files.values()) > MAX_ARCHIVE_PLAINTEXT_BYTES:
        raise FreshRemoteError("archive plaintext oversized")
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
            for name in sorted(files):
                value = files[name]
                if not isinstance(value, bytes) or len(value) > MAX_FILE_BYTES:
                    raise FreshRemoteError("archive value invalid")
                item = tarfile.TarInfo(f"./{name}")
                item.size = len(value)
                item.mode = 0o600
                item.uid = 0
                item.gid = 0
                item.mtime = 0
                archive.addfile(item, io.BytesIO(value))
    result = output.getvalue()
    if not result.startswith(FRAME_ARCHIVE_MAGIC) or len(result) > MAX_FRAME_BYTES:
        raise FreshRemoteError("archive boundary invalid")
    return result


def build_role_frame(audit: Mapping[str, object], files: Mapping[str, bytes]) -> bytes:
    audit_bytes = canonical_json_bytes(audit)
    if len(audit_bytes) > MAX_AUDIT_BYTES:
        raise FreshRemoteError("audit boundary invalid")
    archive = deterministic_archive_bytes(files)
    frame = FRAME_MAGIC + struct.pack(">I", len(audit_bytes)) + audit_bytes + archive
    if len(frame) > MAX_FRAME_BYTES:
        raise FreshRemoteError("frame oversized")
    return frame


def parse_role_frame(frame: bytes) -> ParsedRoleFrame:
    if not isinstance(frame, bytes) or not frame.startswith(FRAME_MAGIC):
        raise FreshRemoteError("frame format invalid")
    length_offset = len(FRAME_MAGIC)
    if len(frame) < length_offset + 4:
        raise FreshRemoteError("frame truncated")
    audit_length = struct.unpack(">I", frame[length_offset : length_offset + 4])[0]
    if audit_length < 2 or audit_length > MAX_AUDIT_BYTES:
        raise FreshRemoteError("audit boundary invalid")
    audit_start = length_offset + 4
    audit_end = audit_start + audit_length
    if audit_end >= len(frame):
        raise FreshRemoteError("frame truncated")
    audit_bytes = frame[audit_start:audit_end]
    try:
        audit = json.loads(audit_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FreshRemoteError("audit invalid") from error
    if not isinstance(audit, dict) or canonical_json_bytes(audit) != audit_bytes:
        raise FreshRemoteError("audit noncanonical")
    archive_bytes = frame[audit_end:]
    if not archive_bytes.startswith(FRAME_ARCHIVE_MAGIC):
        raise FreshRemoteError("archive format invalid")
    files: dict[str, bytes] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
            for item in archive.getmembers():
                name = item.name.removeprefix("./")
                if (
                    not item.isfile()
                    or not name
                    or "/" in name
                    or "\\" in name
                    or name in files
                    or item.size > MAX_FILE_BYTES
                ):
                    raise FreshRemoteError("archive member invalid")
                handle = archive.extractfile(item)
                if handle is None:
                    raise FreshRemoteError("archive member unavailable")
                value = handle.read(MAX_FILE_BYTES + 1)
                if len(value) != item.size or len(value) > MAX_FILE_BYTES:
                    raise FreshRemoteError("archive member boundary invalid")
                files[name] = value
    except (tarfile.TarError, OSError) as error:
        raise FreshRemoteError("archive invalid") from error
    if set(files) != EXPECTED_ARCHIVE_MEMBERS:
        raise FreshRemoteError("archive member set invalid")
    if sum(len(value) for value in files.values()) > MAX_ARCHIVE_PLAINTEXT_BYTES:
        raise FreshRemoteError("archive plaintext oversized")
    return ParsedRoleFrame(audit=audit_bytes, archive=archive_bytes, files=files)


def collect_role_frame(role: str, audit: Mapping[str, object]) -> bytes:
    if role not in ROLE_CONTRACTS:
        raise FreshRemoteError("role invalid")
    contract = ROLE_CONTRACTS[role]
    files = {"database.sqlite3": sqlite_snapshot_bytes(Path(contract["database"]))}
    application_files = contract["application_files"]
    if not isinstance(application_files, tuple):
        raise FreshRemoteError("role application contract invalid")
    for name, path in application_files:
        files[str(name)] = read_fixed_application_file(Path(path))
    return build_role_frame(audit, files)


def _read_ephemeral_key() -> bytes:
    encoded = sys.stdin.buffer.readline(256).strip()
    try:
        key = base64.b64decode(encoded, validate=True)
    except ValueError as error:
        raise FreshRemoteError("ephemeral key invalid") from error
    if len(key) != 32:
        raise FreshRemoteError("ephemeral key invalid")
    return key


def main() -> int:
    try:
        if len(sys.argv) != 3 or sys.argv[1] != "--role":
            raise FreshRemoteError("arguments invalid")
        role = sys.argv[2]
        key = bytearray(_read_ephemeral_key())
        try:
            try:
                from phase13_bot_web_migration_readonly_remote import collect
            except ImportError:
                from scripts.vps.phase13_bot_web_migration_readonly_remote import collect
            document = collect(role, bytes(key))
            sys.stdout.buffer.write(collect_role_frame(role, document["audit"]))
        finally:
            for index in range(len(key)):
                key[index] = 0
        return 0
    except (FreshRemoteError, OSError, sqlite3.Error):
        sys.stdout.write("fresh_input_failed\n")
        return 74


if __name__ == "__main__":
    raise SystemExit(main())
