"""Secret-safe read-only collector for Phase 13 bot/web migration evidence."""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import hmac
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from typing import Mapping, Sequence
from urllib.error import URLError
from urllib.request import urlopen


ROLE_CONTRACTS = {
    "usa": {
        "audit_role": "usa-source",
        "database": Path("/opt/amn2/data/amneziya.sqlite3"),
        "environment": Path("/opt/amn2/.env"),
        "web_unit": "amneziya-web.service",
        "bot_unit": "amneziya-bot.service",
        "web_port": 3030,
        "login_url": "http://127.0.0.1:3030/login",
        "required_paths": (
            Path("/opt/amn2/servers.yml"),
            Path("/opt/amn2/app"),
        ),
    },
    "spain": {
        "audit_role": "spain-target",
        "database": Path("/var/lib/amn2-spain/amn2.sqlite3"),
        "environment": Path("/etc/amn2-spain/runtime.env"),
        "web_unit": "amn2-spain-web.service",
        "bot_unit": "amn2-spain-bot.service",
        "web_port": 3031,
        "login_url": "http://127.0.0.1:3031/login",
        "required_paths": (
            Path("/var/lib/amn2-spain/source"),
            Path("/var/lib/amn2-spain/server-config.yml"),
        ),
    },
}

SECRET_KEY_ALIASES = {
    "telegram_bot_token": ("TELEGRAM_BOT_TOKEN", "BOT_TOKEN"),
    "app_secret_key": ("APP_SECRET_KEY",),
    "web_password_hash": ("WEB_ADMIN_PASSWORD_HASH", "ADMIN_PASSWORD_HASH"),
    "web_session_secret": ("WEB_SESSION_SECRET", "SESSION_SECRET"),
}


class CollectorError(RuntimeError):
    pass


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--role", choices=tuple(ROLE_CONTRACTS), required=True)
    return parser.parse_args(arguments)


def inspect_database(path: Path) -> dict[str, object]:
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        connection.execute("PRAGMA query_only=ON")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        foreign_key_issues = connection.execute("PRAGMA foreign_key_check").fetchall()
        tables = [
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        schema_rows = [
            tuple("" if value is None else str(value) for value in row)
            for row in connection.execute(
                "SELECT type, name, tbl_name, sql FROM sqlite_master "
                "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
            )
        ]
        counts = []
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            row_count = int(connection.execute(f"SELECT count(*) FROM {quoted}").fetchone()[0])
            counts.append((table, row_count))
    finally:
        connection.close()
    return {
        "integrity_ok": integrity == ("ok",),
        "foreign_key_violations": len(foreign_key_issues),
        "table_count": len(tables),
        "schema_sha256": hashlib.sha256(canonical_json_bytes(schema_rows)).hexdigest(),
        "counts_sha256": hashlib.sha256(canonical_json_bytes(counts)).hexdigest(),
    }


def ephemeral_reference_hmac(reference: str, key: bytes) -> str:
    if len(key) != 32 or not isinstance(reference, str):
        raise CollectorError("ephemeral proof input invalid")
    return hmac.new(key, reference.encode("utf-8"), hashlib.sha256).hexdigest()


def _read_environment(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in {alias for aliases in SECRET_KEY_ALIASES.values() for alias in aliases}:
            values[key] = value.strip()
    return values


def _secret_references(values: Mapping[str, str]) -> dict[str, str]:
    references: dict[str, str] = {}
    for secret_class, aliases in SECRET_KEY_ALIASES.items():
        references[secret_class] = next(
            (values[alias] for alias in aliases if values.get(alias)), ""
        )
    return references


def _service_state(unit: str) -> dict[str, object]:
    result = subprocess.run(
        [
            "systemctl",
            "show",
            unit,
            "--property=ActiveState,UnitFileState,NRestarts",
            "--value",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=10,
    )
    values = result.stdout.splitlines() if result.returncode == 0 else []
    return {
        "active": len(values) >= 1 and values[0] == "active",
        "enabled": len(values) >= 2 and values[1] == "enabled",
        "restart_count": int(values[2]) if len(values) >= 3 and values[2].isdigit() else 0,
    }


def _listener_loopback_only(port: int) -> bool:
    result = subprocess.run(
        ["ss", "-ltnH", f"sport = :{port}"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=10,
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return bool(lines) and all("127.0.0.1:" in line or "[::1]:" in line for line in lines)


def _login_healthy(url: str) -> bool:
    try:
        with urlopen(url, timeout=5) as response:
            return int(response.status) == 200
    except (OSError, URLError, ValueError):
        return False


def collect(role: str, ephemeral_key: bytes) -> dict[str, object]:
    if role not in ROLE_CONTRACTS:
        raise CollectorError("invalid role")
    contract = ROLE_CONTRACTS[role]
    database = Path(contract["database"])
    environment = Path(contract["environment"])
    env_values = _read_environment(environment)
    references = _secret_references(env_values)
    web_state = _service_state(str(contract["web_unit"]))
    bot_state = _service_state(str(contract["bot_unit"]))
    audit = {
        "schema": "amn2.phase13.bot-web-audit.v1",
        "role": contract["audit_role"],
        "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "services": {
            "web_active": web_state["active"],
            "bot_active": bot_state["active"],
            "web_loopback_only": _listener_loopback_only(int(contract["web_port"])),
        },
        "database": inspect_database(database),
        "environment": {
            "telegram_bot_token_present": bool(references["telegram_bot_token"]),
            "app_secret_present": bool(references["app_secret_key"]),
            "web_password_hash_present": bool(references["web_password_hash"]),
            "session_secret_present": bool(references["web_session_secret"]),
        },
        "required_artifacts": {
            "database_readable": database.is_file(),
            "environment_reference_proof_available": environment.is_file(),
        },
        "safety_receipt": {
            "mutation_attempted": False,
            "raw_output_persisted": False,
            "secret_bearing_data_persisted": False,
        },
    }
    return {
        "schema": "amn2.phase13.bot-web-collector.v1",
        "role": role,
        "audit": audit,
        "service_observation": {
            "web_enabled": web_state["enabled"],
            "web_restart_count": web_state["restart_count"],
            "bot_enabled": bot_state["enabled"],
            "bot_restart_count": bot_state["restart_count"],
            "login_healthy": _login_healthy(str(contract["login_url"])),
            "required_paths_present": all(
                Path(path).exists() for path in contract["required_paths"]
            ),
        },
        "secret_reference_hmac": {
            name: ephemeral_reference_hmac(reference, ephemeral_key)
            for name, reference in references.items()
        },
    }


def _read_ephemeral_key() -> bytes:
    encoded = sys.stdin.buffer.readline(256).strip()
    try:
        key = base64.b64decode(encoded, validate=True)
    except ValueError as error:
        raise CollectorError("ephemeral key invalid") from error
    if len(key) != 32:
        raise CollectorError("ephemeral key invalid")
    return key


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        role = parse_arguments(arguments).role
        key = bytearray(_read_ephemeral_key())
        try:
            sys.stdout.buffer.write(canonical_json_bytes(collect(role, bytes(key))))
        finally:
            for index in range(len(key)):
                key[index] = 0
        return 0
    except (CollectorError, OSError, sqlite3.Error, subprocess.SubprocessError):
        sys.stdout.write("collector_failed\n")
        return 74


if __name__ == "__main__":
    raise SystemExit(main())
