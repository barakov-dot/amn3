#!/usr/bin/env python3
"""Bounded, read-only USA bot-media collector for AMN2 Phase 13."""

from __future__ import annotations

from dataclasses import dataclass
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import struct
import sys
import tarfile
from typing import Mapping


FRAME_MAGIC = b"AMN2-PHASE13-BOT-MEDIA-V1\n"
ARCHIVE_MAGIC = b"\x1f\x8b"
EVIDENCE_SCHEMA = "amn2.phase13.bot-media-readonly-evidence.v1"
MAX_REGISTRY_BYTES = 1024 * 1024
MAX_MEDIA_FILE_BYTES = 10 * 1024 * 1024
MAX_MEDIA_FILES = 256
MAX_TOTAL_BYTES = 48 * 1024 * 1024
MAX_EVIDENCE_BYTES = 4096
MAX_FRAME_BYTES = 64 * 1024 * 1024
DEFAULT_DATA_ROOT = Path("/opt/amn2/data")


class BotMediaRemoteError(RuntimeError):
    """A constant-message, secret-safe remote collection failure."""


@dataclass(frozen=True)
class ParsedMediaFrame:
    evidence: Mapping[str, object]
    archive: bytes
    files: Mapping[str, bytes]


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _is_reparse_point(metadata: os.stat_result) -> bool:
    return bool(getattr(metadata, "st_file_attributes", 0) & 0x400)


def _safe_member_name(name: str) -> bool:
    if not isinstance(name, str) or not name or "\\" in name or len(name) > 512:
        return False
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return False
    return name == "bot-media-registry.json" or (
        len(path.parts) >= 2 and path.parts[0] == "bot-media"
    )


def _read_stable_regular_file(path: Path, *, maximum_bytes: int) -> bytes:
    try:
        before = os.lstat(path)
    except OSError as error:
        raise BotMediaRemoteError("media path unavailable") from error
    if (
        stat.S_ISLNK(before.st_mode)
        or _is_reparse_point(before)
        or not stat.S_ISREG(before.st_mode)
    ):
        raise BotMediaRemoteError("media path unsafe")
    if before.st_size < 0 or before.st_size > maximum_bytes:
        raise BotMediaRemoteError("media file oversized")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            buffer = bytearray()
            while len(buffer) <= maximum_bytes:
                chunk = os.read(
                    descriptor,
                    min(64 * 1024, maximum_bytes + 1 - len(buffer)),
                )
                if not chunk:
                    break
                buffer.extend(chunk)
            value = bytes(buffer)
        finally:
            os.close(descriptor)
        after = os.lstat(path)
    except OSError as error:
        raise BotMediaRemoteError("media read failed") from error
    if len(value) > maximum_bytes:
        raise BotMediaRemoteError("media file oversized")
    identity_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    )
    identity_after = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    )
    if identity_before != identity_after or len(value) != before.st_size:
        raise BotMediaRemoteError("media file changed")
    return value


def _collect_files(data_root: Path) -> tuple[dict[str, bytes], bool, bool]:
    root = Path(data_root)
    try:
        root_metadata = os.lstat(root)
    except OSError as error:
        raise BotMediaRemoteError("data root unavailable") from error
    if (
        stat.S_ISLNK(root_metadata.st_mode)
        or _is_reparse_point(root_metadata)
        or not stat.S_ISDIR(root_metadata.st_mode)
    ):
        raise BotMediaRemoteError("data root unsafe")

    files: dict[str, bytes] = {}
    registry = root / "bot-media-registry.json"
    registry_present = os.path.lexists(registry)
    if registry_present:
        files["bot-media-registry.json"] = _read_stable_regular_file(
            registry, maximum_bytes=MAX_REGISTRY_BYTES
        )

    media_root = root / "bot-media"
    media_root_present = os.path.lexists(media_root)
    if media_root_present:
        try:
            metadata = os.lstat(media_root)
        except OSError as error:
            raise BotMediaRemoteError("media root unavailable") from error
        if (
            stat.S_ISLNK(metadata.st_mode)
            or _is_reparse_point(metadata)
            or not stat.S_ISDIR(metadata.st_mode)
        ):
            raise BotMediaRemoteError("media path unsafe")
        pending = [media_root]
        while pending:
            directory = pending.pop()
            try:
                entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
            except OSError as error:
                raise BotMediaRemoteError("media directory unavailable") from error
            for entry in entries:
                path = Path(entry.path)
                try:
                    entry_metadata = os.lstat(path)
                except OSError as error:
                    raise BotMediaRemoteError("media path unavailable") from error
                if stat.S_ISLNK(entry_metadata.st_mode) or _is_reparse_point(
                    entry_metadata
                ):
                    raise BotMediaRemoteError("media path unsafe")
                if stat.S_ISDIR(entry_metadata.st_mode):
                    pending.append(path)
                    continue
                if not stat.S_ISREG(entry_metadata.st_mode):
                    raise BotMediaRemoteError("media path unsafe")
                try:
                    relative = path.relative_to(media_root).as_posix()
                except ValueError as error:
                    raise BotMediaRemoteError("media path unsafe") from error
                member = f"bot-media/{relative}"
                if not _safe_member_name(member) or member in files:
                    raise BotMediaRemoteError("media path unsafe")
                files[member] = _read_stable_regular_file(
                    path, maximum_bytes=MAX_MEDIA_FILE_BYTES
                )
                if len(files) > MAX_MEDIA_FILES:
                    raise BotMediaRemoteError("media file count exceeded")
                if sum(len(value) for value in files.values()) > MAX_TOTAL_BYTES:
                    raise BotMediaRemoteError("media total oversized")
    if len(files) > MAX_MEDIA_FILES:
        raise BotMediaRemoteError("media file count exceeded")
    if sum(len(value) for value in files.values()) > MAX_TOTAL_BYTES:
        raise BotMediaRemoteError("media total oversized")
    return files, registry_present, media_root_present


def deterministic_archive_bytes(files: Mapping[str, bytes]) -> bytes:
    if len(files) > MAX_MEDIA_FILES or any(
        not _safe_member_name(name) or not isinstance(value, bytes)
        for name, value in files.items()
    ):
        raise BotMediaRemoteError("archive member invalid")
    if sum(len(value) for value in files.values()) > MAX_TOTAL_BYTES:
        raise BotMediaRemoteError("media total oversized")
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
            for name in sorted(files):
                value = files[name]
                maximum = (
                    MAX_REGISTRY_BYTES
                    if name == "bot-media-registry.json"
                    else MAX_MEDIA_FILE_BYTES
                )
                if len(value) > maximum:
                    raise BotMediaRemoteError("media file oversized")
                item = tarfile.TarInfo(f"./{name}")
                item.size = len(value)
                item.mode = 0o600
                item.uid = 0
                item.gid = 0
                item.mtime = 0
                archive.addfile(item, io.BytesIO(value))
    result = output.getvalue()
    if not result.startswith(ARCHIVE_MAGIC) or len(result) > MAX_FRAME_BYTES:
        raise BotMediaRemoteError("archive boundary invalid")
    return result


def member_manifest_sha256(files: Mapping[str, bytes]) -> str:
    members = [
        {
            "name": name,
            "sha256": hashlib.sha256(files[name]).hexdigest(),
            "size": len(files[name]),
        }
        for name in sorted(files)
    ]
    return hashlib.sha256(canonical_json_bytes(members)).hexdigest()


def collect_media_frame(data_root: Path = DEFAULT_DATA_ROOT) -> bytes:
    files, registry_present, media_root_present = _collect_files(Path(data_root))
    archive = deterministic_archive_bytes(files)
    evidence = {
        "content_sha256": hashlib.sha256(archive).hexdigest(),
        "file_count": len(files),
        "media_root_present": media_root_present,
        "member_manifest_sha256": member_manifest_sha256(files),
        "registry_present": registry_present,
        "schema": EVIDENCE_SCHEMA,
        "total_bytes": sum(len(value) for value in files.values()),
    }
    evidence_bytes = canonical_json_bytes(evidence)
    if len(evidence_bytes) > MAX_EVIDENCE_BYTES:
        raise BotMediaRemoteError("evidence boundary invalid")
    frame = FRAME_MAGIC + struct.pack(">I", len(evidence_bytes)) + evidence_bytes + archive
    if len(frame) > MAX_FRAME_BYTES:
        raise BotMediaRemoteError("frame oversized")
    return frame


def parse_media_frame(frame: bytes) -> ParsedMediaFrame:
    if not isinstance(frame, bytes) or not frame.startswith(FRAME_MAGIC):
        raise BotMediaRemoteError("frame format invalid")
    offset = len(FRAME_MAGIC)
    if len(frame) < offset + 4:
        raise BotMediaRemoteError("frame truncated")
    evidence_length = struct.unpack(">I", frame[offset : offset + 4])[0]
    if evidence_length < 2 or evidence_length > MAX_EVIDENCE_BYTES:
        raise BotMediaRemoteError("evidence boundary invalid")
    evidence_start = offset + 4
    evidence_end = evidence_start + evidence_length
    if evidence_end >= len(frame):
        raise BotMediaRemoteError("frame truncated")
    evidence_bytes = frame[evidence_start:evidence_end]
    try:
        evidence = json.loads(evidence_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BotMediaRemoteError("evidence invalid") from error
    required = {
        "content_sha256",
        "file_count",
        "media_root_present",
        "member_manifest_sha256",
        "registry_present",
        "schema",
        "total_bytes",
    }
    if (
        not isinstance(evidence, dict)
        or set(evidence) != required
        or canonical_json_bytes(evidence) != evidence_bytes
        or evidence.get("schema") != EVIDENCE_SCHEMA
        or not isinstance(evidence.get("registry_present"), bool)
        or not isinstance(evidence.get("media_root_present"), bool)
        or not isinstance(evidence.get("file_count"), int)
        or not isinstance(evidence.get("total_bytes"), int)
        or not isinstance(evidence.get("content_sha256"), str)
        or not isinstance(evidence.get("member_manifest_sha256"), str)
    ):
        raise BotMediaRemoteError("evidence invalid")
    archive_bytes = frame[evidence_end:]
    if (
        not archive_bytes.startswith(ARCHIVE_MAGIC)
        or len(frame) > MAX_FRAME_BYTES
        or hashlib.sha256(archive_bytes).hexdigest() != evidence["content_sha256"]
    ):
        raise BotMediaRemoteError("archive boundary invalid")
    files: dict[str, bytes] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
            for item in archive.getmembers():
                name = item.name.removeprefix("./")
                maximum = (
                    MAX_REGISTRY_BYTES
                    if name == "bot-media-registry.json"
                    else MAX_MEDIA_FILE_BYTES
                )
                if (
                    not item.isfile()
                    or not _safe_member_name(name)
                    or name in files
                    or item.size < 0
                    or item.size > maximum
                ):
                    raise BotMediaRemoteError("archive member invalid")
                handle = archive.extractfile(item)
                if handle is None:
                    raise BotMediaRemoteError("archive member unavailable")
                value = handle.read(maximum + 1)
                if len(value) != item.size or len(value) > maximum:
                    raise BotMediaRemoteError("archive member invalid")
                files[name] = value
    except (tarfile.TarError, OSError) as error:
        raise BotMediaRemoteError("archive invalid") from error
    total = sum(len(value) for value in files.values())
    if (
        len(files) > MAX_MEDIA_FILES
        or total > MAX_TOTAL_BYTES
        or evidence["file_count"] != len(files)
        or evidence["total_bytes"] != total
        or evidence["member_manifest_sha256"] != member_manifest_sha256(files)
        or evidence["registry_present"] != ("bot-media-registry.json" in files)
        or (
            not evidence["media_root_present"]
            and any(name.startswith("bot-media/") for name in files)
        )
    ):
        raise BotMediaRemoteError("archive evidence mismatch")
    return ParsedMediaFrame(evidence=evidence, archive=archive_bytes, files=files)


def main() -> int:
    try:
        if len(sys.argv) != 1:
            raise BotMediaRemoteError("arguments invalid")
        sys.stdout.buffer.write(collect_media_frame())
        return 0
    except (BotMediaRemoteError, OSError):
        sys.stdout.write("bot_media_collection_failed\n")
        return 74


if __name__ == "__main__":
    raise SystemExit(main())
