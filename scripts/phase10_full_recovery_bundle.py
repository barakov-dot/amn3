#!/usr/bin/env python
"""Build an encrypted AMN2 full-recovery bundle without stopping services."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import sqlite3
import subprocess
import sys
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence


FORMAT = "amn2-full-recovery-v1"
MANIFEST_NAME = "manifest.sha256"
MAX_SOURCE_FILE_BYTES = 32 * 1024 * 1024
MAX_PLAINTEXT_BUNDLE_BYTES = 64 * 1024 * 1024
DOCKER_TIMEOUT_SECONDS = 30

PAYLOAD_NAMES = {
    "container/awg/awg0.conf",
    "container/awg/wireguard_psk.key",
    "container/awg/wireguard_server_private_key.key",
    "container/awg/wireguard_server_public_key.key",
    "container/start.sh",
    "host/amneziya.sqlite3",
    "host/app.env",
    "host/servers.yml",
    "host/source_overlay_commit",
    "systemd/amneziya-bot.service",
    "systemd/amneziya-web.service",
}


class RecoveryWriterError(RuntimeError):
    """A safe recovery-writer failure that contains no source content."""


@dataclass(frozen=True)
class ContainerState:
    running: bool
    restart_count: int
    image_id: str


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def render_metadata(
    *,
    created_utc: str,
    source_overlay: str,
    container_name: str,
    container_image_id: str,
) -> bytes:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", created_utc):
        raise RecoveryWriterError("created UTC timestamp is invalid")
    if not re.fullmatch(r"[0-9a-f]{7,40}", source_overlay):
        raise RecoveryWriterError("source overlay marker is invalid")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", container_name):
        raise RecoveryWriterError("container name is invalid")
    if (
        not container_image_id
        or len(container_image_id) > 256
        or any(character in container_image_id for character in "\r\n")
    ):
        raise RecoveryWriterError("container image ID is invalid")
    return (
        f"format={FORMAT}\n"
        f"created_utc={created_utc}\n"
        f"source_overlay={source_overlay}\n"
        f"container_name={container_name}\n"
        f"container_image_id={container_image_id}\n"
        "restore_apply_performed=false\n"
        "service_restart_performed=false\n"
    ).encode("utf-8")


def build_manifest(files: Mapping[str, bytes]) -> bytes:
    lines = [f"{sha256_bytes(files[name])}  ./{name}" for name in sorted(files)]
    return ("\n".join(lines) + "\n").encode("ascii")


def assemble_recovery_files(
    source_files: Mapping[str, bytes],
    *,
    created_utc: str,
    source_overlay: str,
    container_name: str,
    container_image_id: str,
) -> dict[str, bytes]:
    if set(source_files) != PAYLOAD_NAMES:
        raise RecoveryWriterError("source file contract does not match recovery format")
    files = dict(source_files)
    expected_overlay = (source_overlay + "\n").encode("ascii")
    if files["host/source_overlay_commit"] != expected_overlay:
        raise RecoveryWriterError("source overlay file is not canonical")
    for name, value in files.items():
        if not isinstance(value, bytes):
            raise RecoveryWriterError("source file content is not bytes")
        if len(value) > MAX_SOURCE_FILE_BYTES:
            raise RecoveryWriterError("source file size limit exceeded")
        if not value:
            raise RecoveryWriterError("required source file is empty")
    files["metadata.txt"] = render_metadata(
        created_utc=created_utc,
        source_overlay=source_overlay,
        container_name=container_name,
        container_image_id=container_image_id,
    )
    files[MANIFEST_NAME] = build_manifest(files)
    return files


def tar_bytes(files: Mapping[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as compressed:
        with tarfile.open(
            fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT
        ) as archive:
            for name in sorted(files):
                value = files[name]
                info = tarfile.TarInfo(f"./{name}")
                info.size = len(value)
                info.mode = 0o700 if name == "container/start.sh" else 0o600
                info.uid = 0
                info.gid = 0
                info.mtime = 0
                archive.addfile(info, io.BytesIO(value))
    result = output.getvalue()
    if len(result) > MAX_PLAINTEXT_BUNDLE_BYTES:
        raise RecoveryWriterError("plaintext bundle size limit exceeded")
    return result


def encrypt_recovery_files(files: Mapping[str, bytes], key: bytes) -> bytes:
    try:
        from cryptography.fernet import Fernet
    except ImportError as exc:
        raise RecoveryWriterError("cryptography dependency is unavailable") from exc
    try:
        cipher = Fernet(key)
    except (TypeError, ValueError) as exc:
        raise RecoveryWriterError("recovery encryption key is invalid") from exc
    return cipher.encrypt(tar_bytes(files))


def write_exclusive(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(value)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def read_limited_file(path: Path, label: str) -> bytes:
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise RecoveryWriterError(f"{label} is unavailable") from exc
    if not resolved.is_file():
        raise RecoveryWriterError(f"{label} is not a regular file")
    if resolved.stat().st_size > MAX_SOURCE_FILE_BYTES:
        raise RecoveryWriterError(f"{label} exceeds the size limit")
    value = resolved.read_bytes()
    if not value:
        raise RecoveryWriterError(f"{label} is empty")
    return value


def sqlite_backup_bytes(path: Path) -> bytes:
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise RecoveryWriterError("SQLite source is unavailable") from exc
    if not resolved.is_file() or resolved.stat().st_size > MAX_SOURCE_FILE_BYTES:
        raise RecoveryWriterError("SQLite source is not a supported regular file")
    source = sqlite3.connect(resolved.as_uri() + "?mode=ro", uri=True)
    destination = sqlite3.connect(":memory:")
    try:
        source.backup(destination)
        integrity = [row[0] for row in destination.execute("PRAGMA integrity_check")]
        if integrity != ["ok"]:
            raise RecoveryWriterError("SQLite backup integrity check failed")
        if list(destination.execute("PRAGMA foreign_key_check")):
            raise RecoveryWriterError("SQLite backup foreign key check failed")
        return destination.serialize()
    except sqlite3.DatabaseError as exc:
        raise RecoveryWriterError("SQLite consistent backup failed") from exc
    finally:
        source.close()
        destination.close()


def run_docker(arguments: Sequence[str], label: str) -> bytes:
    try:
        result = subprocess.run(
            ["docker", *arguments],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=DOCKER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise RecoveryWriterError(f"Docker {label} timed out") from exc
    if result.returncode != 0:
        raise RecoveryWriterError(f"Docker {label} failed")
    return result.stdout


def inspect_container(container_name: str) -> ContainerState:
    value = run_docker(
        [
            "inspect",
            "--format",
            "{{.State.Running}}|{{.RestartCount}}|{{.Image}}",
            container_name,
        ],
        "container inspection",
    )
    try:
        running_text, restart_text, image_id = value.decode("ascii").strip().split("|", 2)
        restart_count = int(restart_text)
    except (UnicodeDecodeError, ValueError) as exc:
        raise RecoveryWriterError("Docker inspection response is invalid") from exc
    if running_text not in {"true", "false"}:
        raise RecoveryWriterError("Docker running state is invalid")
    return ContainerState(
        running=running_text == "true",
        restart_count=restart_count,
        image_id=image_id,
    )


def read_container_file(container_name: str, path: str, label: str) -> bytes:
    if not path.startswith("/") or any(character in path for character in "\r\n"):
        raise RecoveryWriterError(f"{label} container path is invalid")
    value = run_docker(["exec", container_name, "cat", path], label)
    if not value:
        raise RecoveryWriterError(f"{label} is empty")
    if len(value) > MAX_SOURCE_FILE_BYTES:
        raise RecoveryWriterError(f"{label} exceeds the size limit")
    return value


def read_key_from_stdin() -> bytes:
    value = sys.stdin.buffer.read(4097)
    if len(value) > 4096:
        raise RecoveryWriterError("recovery key input is too large")
    lines = value.splitlines()
    if len(lines) != 1 or not lines[0]:
        raise RecoveryWriterError("recovery key input must contain exactly one line")
    return lines[0]


def collect_source_files(args: argparse.Namespace, source_overlay: str) -> dict[str, bytes]:
    return {
        "container/awg/awg0.conf": read_container_file(
            args.container_name, args.awg_config_path, "AWG config read"
        ),
        "container/awg/wireguard_psk.key": read_container_file(
            args.container_name, args.awg_psk_path, "AWG PSK read"
        ),
        "container/awg/wireguard_server_private_key.key": read_container_file(
            args.container_name,
            args.awg_server_private_key_path,
            "AWG server private key read",
        ),
        "container/awg/wireguard_server_public_key.key": read_container_file(
            args.container_name,
            args.awg_server_public_key_path,
            "AWG server public key read",
        ),
        "container/start.sh": read_container_file(
            args.container_name, args.container_start_path, "container start read"
        ),
        "host/amneziya.sqlite3": sqlite_backup_bytes(args.database),
        "host/app.env": read_limited_file(args.app_env, "app env"),
        "host/servers.yml": read_limited_file(args.servers_yml, "servers registry"),
        "host/source_overlay_commit": (source_overlay + "\n").encode("ascii"),
        "systemd/amneziya-bot.service": read_limited_file(
            args.bot_unit, "bot systemd unit"
        ),
        "systemd/amneziya-web.service": read_limited_file(
            args.web_unit, "web systemd unit"
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--app-env", type=Path, required=True)
    parser.add_argument("--servers-yml", type=Path, required=True)
    parser.add_argument("--source-overlay", type=Path, required=True)
    parser.add_argument("--web-unit", type=Path, required=True)
    parser.add_argument("--bot-unit", type=Path, required=True)
    parser.add_argument("--container-name", required=True)
    parser.add_argument("--awg-config-path", required=True)
    parser.add_argument("--awg-psk-path", required=True)
    parser.add_argument("--awg-server-private-key-path", required=True)
    parser.add_argument("--awg-server-public-key-path", required=True)
    parser.add_argument("--container-start-path", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", args.container_name):
            raise RecoveryWriterError("container name is invalid")
        source_overlay = read_limited_file(
            args.source_overlay, "source overlay marker"
        ).decode("ascii").strip()
        if not re.fullmatch(r"[0-9a-f]{7,40}", source_overlay):
            raise RecoveryWriterError("source overlay marker is invalid")
        before = inspect_container(args.container_name)
        if not before.running:
            raise RecoveryWriterError("AWG container is not running")
        source_files = collect_source_files(args, source_overlay)
        files = assemble_recovery_files(
            source_files,
            created_utc=utc_timestamp(),
            source_overlay=source_overlay,
            container_name=args.container_name,
            container_image_id=before.image_id,
        )
        encrypted = encrypt_recovery_files(files, read_key_from_stdin())
        write_exclusive(args.output, encrypted)
        try:
            after = inspect_container(args.container_name)
        except Exception:
            args.output.unlink(missing_ok=True)
            raise
        if not after.running or after.restart_count != before.restart_count:
            args.output.unlink(missing_ok=True)
            raise RecoveryWriterError("AWG runtime changed during backup")
        report = {
            "artifact_bytes": len(encrypted),
            "artifact_sha256": sha256_bytes(encrypted),
            "container_running": after.running,
            "manifest_entries": len(files) - 1,
            "member_files": len(files),
            "production_plaintext_written": False,
            "service_restart_performed": False,
            "verdict": "passed",
        }
    except (OSError, UnicodeDecodeError, RecoveryWriterError, sqlite3.DatabaseError) as exc:
        print(f"full recovery writer: FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
