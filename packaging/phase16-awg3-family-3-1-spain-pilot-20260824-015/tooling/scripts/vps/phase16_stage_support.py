#!/usr/bin/python3
"""Secret-safe local helpers for the Phase 16 controlled Spain stage."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys


PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-015"
RUNTIME_IDENTITY = (
    "docker.io/amneziavpn/amneziawg-go@"
    "sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d"
)
DOCKER_BINARY = "/opt/amn2-spain/docker/bin/docker"
DOCKER_SOCKET = "unix:///run/amn2-spain-docker/docker.sock"
DOCKER_OWNER_SERVICE = "amn2-spain-docker.service"
MAX_PRIVATE_KEY_BYTES = 128


class StageSupportError(ValueError):
    pass


def _canonical(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("ascii")
        + b"\n"
    )


def _regular_not_symlink(path: Path, *, label: str) -> Path:
    value = Path(path)
    try:
        info = value.lstat()
    except OSError as exc:
        raise StageSupportError(f"{label} unavailable") from exc
    if value.is_symlink() or not value.is_file() or info.st_size < 1:
        raise StageSupportError(f"{label} must be a regular file")
    return value


def online_sqlite_backup(source: Path, destination: Path) -> str:
    """Create a consistent create-new SQLite backup while the source stays online."""

    source_path = _regular_not_symlink(Path(source), label="source database")
    destination_path = Path(destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(
        destination_path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0),
        0o600,
    )
    os.close(descriptor)
    sidecars = tuple(
        Path(str(destination_path) + suffix) for suffix in ("-journal", "-shm", "-wal")
    )
    try:
        source_uri = source_path.resolve().as_uri() + "?mode=ro"
        current = sqlite3.connect(source_uri, uri=True, timeout=30)
        backup = None
        try:
            current.execute("PRAGMA query_only=ON")
            backup = sqlite3.connect(destination_path, timeout=30)
            current.backup(backup)
            if backup.execute("PRAGMA integrity_check").fetchone() != ("ok",):
                raise StageSupportError("backup integrity check failed")
            backup.commit()
        finally:
            if backup is not None:
                backup.close()
            current.close()
        os.chmod(destination_path, 0o600)
        sync_descriptor = os.open(
            destination_path, os.O_RDWR | getattr(os, "O_CLOEXEC", 0)
        )
        try:
            os.fsync(sync_descriptor)
        finally:
            os.close(sync_descriptor)
        with destination_path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        return digest
    except Exception:
        for path in (*sidecars, destination_path):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        raise


def _validated_private_key(value: str) -> str:
    if not isinstance(value, str) or len(value) != 44 or "\n" in value or "\r" in value:
        raise StageSupportError("private key shape")
    try:
        decoded = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise StageSupportError("private key shape") from exc
    if len(decoded) != 32:
        raise StageSupportError("private key shape")
    return value


def render_server_only_awg31_config(private_key: str) -> str:
    key = _validated_private_key(private_key)
    return (
        "[Interface]\n"
        f"PrivateKey = {key}\n"
        "ListenPort = 30002\n"
        "RandomTrailers = on\n"
        "DisableCookies = on\n"
    )


def render_awg31_runtime_unit() -> str:
    docker = f"{DOCKER_BINARY} --host {DOCKER_SOCKET}"
    container = "amn2-spain-awg3"
    return f"""[Unit]
Description=AMN2 Spain isolated AWG 3.1 runtime
After={DOCKER_OWNER_SERVICE} network-online.target
Requires={DOCKER_OWNER_SERVICE}

[Service]
Type=simple
ExecStartPre=-{docker} rm -f {container}
ExecStart={docker} run --rm --name {container} --network amn2sp3 --ip 172.29.252.2 --cap-add NET_ADMIN --device /dev/net/tun -v /var/lib/amn2-spain/awg3/awg3.conf:/etc/amneziawg/awg3.conf:ro -p 30002:30002/udp {RUNTIME_IDENTITY} /usr/bin/amneziawg-go -f awg3
ExecStartPost={docker} exec {container} /usr/bin/awg setconf awg3 /etc/amneziawg/awg3.conf
ExecStartPost={docker} exec {container} /sbin/ip address add 10.212.13.1/24 dev awg3
ExecStartPost={docker} exec {container} /sbin/ip link set awg3 up
ExecStartPost={docker} exec {container} /sbin/iptables -t nat -A POSTROUTING -s 10.212.13.0/24 -o eth0 -j MASQUERADE
ExecStop=-{docker} stop -t 10 {container}
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
"""


def _write_create_new(path: Path, body: bytes, mode: int) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(
        destination,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0),
        mode,
    )
    try:
        offset = 0
        while offset < len(body):
            offset += os.write(descriptor, body[offset:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.chmod(destination, mode)


def _read_private_key() -> str:
    raw = sys.stdin.buffer.read(MAX_PRIVATE_KEY_BYTES + 1)
    if not raw or len(raw) > MAX_PRIVATE_KEY_BYTES or b"\x00" in raw:
        raise StageSupportError("private key input")
    try:
        return raw.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise StageSupportError("private key input") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    backup = commands.add_parser("online-sqlite-backup")
    backup.add_argument("source", type=Path)
    backup.add_argument("destination", type=Path)
    config = commands.add_parser("server-only-config")
    config.add_argument("destination", type=Path)
    unit = commands.add_parser("runtime-unit")
    unit.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "online-sqlite-backup":
            digest = online_sqlite_backup(args.source, args.destination)
            result = {"backup_sha256": digest, "result": "backup_created"}
        elif args.command == "server-only-config":
            body = render_server_only_awg31_config(_read_private_key()).encode("ascii")
            _write_create_new(args.destination, body, 0o600)
            result = {"peer_count": 0, "result": "server_only_config_created"}
        else:
            _write_create_new(
                args.destination, render_awg31_runtime_unit().encode("ascii"), 0o644
            )
            result = {"result": "runtime_unit_created"}
    except (OSError, sqlite3.Error, StageSupportError) as exc:
        parser.error(str(exc))
    sys.stdout.buffer.write(_canonical(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
