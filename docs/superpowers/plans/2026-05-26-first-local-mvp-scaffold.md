# First Local MVP Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first local Amneziya Python scaffold with secure config handling, SQLite persistence, IPAM, AmneziaWG config generation, encrypted backups, guarded restore, and a minimal Telegram bot entry point.

**Architecture:** Use focused Python packages under `app/`: config, security, db, vpn, services, backup, bot, and CLI. Domain workflow lives in services; bot handlers stay thin; backup/restore is independent from Telegram and VPN rendering.

**Tech Stack:** Python 3.12+, pytest, pydantic-settings or pydantic, cryptography, qrcode, aiogram 3.x, SQLite from the standard library, argparse from the standard library.

---

## File Structure

- Create `pyproject.toml`: package metadata, dependencies, pytest config.
- Create `.gitignore`: protect env files, DBs, configs, QR files, backups, temp files.
- Create `.env.example`: placeholder-only runtime settings.
- Create `app/__init__.py`: package marker.
- Create `app/config/settings.py`: environment-backed settings and startup validation.
- Create `app/security/crypto.py`: application secret encryption/decryption.
- Create `app/security/redaction.py`: log-safe string/object redaction.
- Create `app/db/schema.py`: SQLite schema creation.
- Create `app/db/connection.py`: connection factory.
- Create `app/db/repositories.py`: small repository methods used by services and tests.
- Create `app/vpn/ipam.py`: CIDR-aware IP allocation.
- Create `app/vpn/amneziawg_v2/config.py`: config dataclasses and renderer.
- Create `app/vpn/amneziawg_v2/keys.py`: key generation interface.
- Create `app/services/access.py`: request approval workflow.
- Create `app/backup/manifest.py`: backup manifest model and checksum helpers.
- Create `app/backup/service.py`: create, verify, restore.
- Create `app/backup/storage.py`: local filesystem storage.
- Create `app/cli.py`: backup CLI.
- Create `app/bot/main.py`: minimal aiogram app factory.
- Create tests under `tests/` matching each behavior.

---

### Task 1: Project Scaffold and File Hygiene

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `app/__init__.py`
- Test: `tests/test_file_hygiene.py`

- [ ] **Step 1: Write the failing file hygiene test**

```python
# tests/test_file_hygiene.py
from pathlib import Path


def test_gitignore_excludes_sensitive_runtime_files():
    text = Path(".gitignore").read_text(encoding="utf-8")

    required = [
        ".env",
        "*.db",
        "*.sqlite",
        "*.sqlite3",
        "*.conf",
        "*.qr.png",
        "servers.yml",
        "backups/",
        "tmp/",
    ]

    for pattern in required:
        assert pattern in text


def test_env_example_uses_placeholders_only():
    text = Path(".env.example").read_text(encoding="utf-8")

    assert "TELEGRAM_BOT_TOKEN=CHANGE_ME" in text
    assert "APP_SECRET_KEY=CHANGE_ME_GENERATED_SECRET" in text
    assert "ADMIN_TELEGRAM_IDS=123456789" in text
    assert "bot" not in text.lower().replace("telegram_bot_token", "")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_file_hygiene.py -v`

Expected: FAIL because `.gitignore` and `.env.example` do not exist yet.

- [ ] **Step 3: Add scaffold files**

```toml
# pyproject.toml
[project]
name = "amneziya"
version = "0.1.0"
description = "Telegram-managed AmneziaWG access automation"
requires-python = ">=3.12"
dependencies = [
  "aiogram>=3.4,<4",
  "cryptography>=42,<46",
  "pydantic>=2,<3",
  "pydantic-settings>=2,<3",
  "qrcode[pil]>=7,<9",
]

[project.optional-dependencies]
dev = [
  "pytest>=8,<9",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

```text
# .gitignore
.env
*.db
*.sqlite
*.sqlite3
*.conf
*.qr.png
servers.yml
backups/
tmp/
__pycache__/
.pytest_cache/
.venv/
```

```env
# .env.example
TELEGRAM_BOT_TOKEN=CHANGE_ME
APP_SECRET_KEY=CHANGE_ME_GENERATED_SECRET
ADMIN_TELEGRAM_IDS=123456789
ACCESS_MODE=free_test
FREE_TEST_REQUIRES_APPROVAL=true
DEFAULT_PLAN_DAYS=7
MAX_DEVICES_PER_USER=5
CLIENT_DNS=1.1.1.1
CLIENT_ALLOWED_IPS=0.0.0.0/0
EXPIRATION_NOTICE_DAYS=7,5,3,1
VPN_PORT_MIN=30001
VPN_PORT_MAX=65535
VPN_SERVER_RUNTIME=host_systemd
DEFAULT_VPN_NETWORK_CIDR=10.8.0.0/24
DATABASE_PATH=data/amneziya.sqlite3
```

```python
# app/__init__.py
__all__ = ["__version__"]

__version__ = "0.1.0"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_file_hygiene.py -v`

Expected: PASS.

---

### Task 2: Settings Validation

**Files:**
- Create: `app/config/__init__.py`
- Create: `app/config/settings.py`
- Test: `tests/config/test_settings.py`

- [ ] **Step 1: Write failing settings tests**

```python
# tests/config/test_settings.py
import pytest
from pydantic import ValidationError

from app.config.settings import Settings


def test_settings_requires_app_secret_key_in_normal_mode():
    with pytest.raises(ValidationError):
        Settings(
            telegram_bot_token="CHANGE_ME",
            admin_telegram_ids="123",
            app_secret_key="",
        )


def test_settings_parses_admin_ids_and_notice_days():
    settings = Settings(
        telegram_bot_token="CHANGE_ME",
        admin_telegram_ids="123,456",
        app_secret_key="test-secret",
        expiration_notice_days="7,5,3,1",
    )

    assert settings.admin_ids == [123, 456]
    assert settings.notice_days == [7, 5, 3, 1]
    assert settings.default_vpn_network_cidr == "10.8.0.0/24"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/config/test_settings.py -v`

Expected: FAIL because `app.config.settings` does not exist.

- [ ] **Step 3: Implement settings**

```python
# app/config/__init__.py
from app.config.settings import Settings

__all__ = ["Settings"]
```

```python
# app/config/settings.py
from functools import cached_property

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")
    app_secret_key: str = Field(alias="APP_SECRET_KEY")
    admin_telegram_ids: str = Field(default="", alias="ADMIN_TELEGRAM_IDS")
    access_mode: str = Field(default="free_test", alias="ACCESS_MODE")
    free_test_requires_approval: bool = Field(default=True, alias="FREE_TEST_REQUIRES_APPROVAL")
    default_plan_days: int = Field(default=7, alias="DEFAULT_PLAN_DAYS")
    max_devices_per_user: int = Field(default=5, alias="MAX_DEVICES_PER_USER")
    client_dns: str = Field(default="1.1.1.1", alias="CLIENT_DNS")
    client_allowed_ips: str = Field(default="0.0.0.0/0", alias="CLIENT_ALLOWED_IPS")
    expiration_notice_days: str = Field(default="7,5,3,1", alias="EXPIRATION_NOTICE_DAYS")
    vpn_port_min: int = Field(default=30001, alias="VPN_PORT_MIN")
    vpn_port_max: int = Field(default=65535, alias="VPN_PORT_MAX")
    vpn_server_runtime: str = Field(default="host_systemd", alias="VPN_SERVER_RUNTIME")
    default_vpn_network_cidr: str = Field(default="10.8.0.0/24", alias="DEFAULT_VPN_NETWORK_CIDR")
    database_path: str = Field(default="data/amneziya.sqlite3", alias="DATABASE_PATH")

    @field_validator("app_secret_key")
    @classmethod
    def require_app_secret_key(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("APP_SECRET_KEY is required")
        return value

    @cached_property
    def admin_ids(self) -> list[int]:
        if not self.admin_telegram_ids.strip():
            return []
        return [int(part.strip()) for part in self.admin_telegram_ids.split(",") if part.strip()]

    @cached_property
    def notice_days(self) -> list[int]:
        return [int(part.strip()) for part in self.expiration_notice_days.split(",") if part.strip()]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/config/test_settings.py -v`

Expected: PASS.

---

### Task 3: Security Primitives

**Files:**
- Create: `app/security/__init__.py`
- Create: `app/security/crypto.py`
- Create: `app/security/redaction.py`
- Test: `tests/security/test_crypto.py`
- Test: `tests/security/test_redaction.py`

- [ ] **Step 1: Write failing crypto and redaction tests**

```python
# tests/security/test_crypto.py
from app.security.crypto import SecretBox


def test_secret_box_round_trips_text_without_plaintext_storage():
    box = SecretBox.from_app_secret("test-secret")

    encrypted = box.encrypt_text("private-value")

    assert encrypted != "private-value"
    assert encrypted.startswith("v1:")
    assert box.decrypt_text(encrypted) == "private-value"
```

```python
# tests/security/test_redaction.py
from app.security.redaction import redact


def test_redaction_removes_tokens_keys_and_config_markers():
    unsafe = """
    TELEGRAM_BOT_TOKEN=123:abc
    PrivateKey = secret-private
    PresharedKey = secret-psk
    [Interface]
    Address = 10.8.0.2/32
    external_payment_id=pay_123
    """

    safe = redact(unsafe)

    assert "123:abc" not in safe
    assert "secret-private" not in safe
    assert "secret-psk" not in safe
    assert "[Interface]" not in safe
    assert "pay_123" not in safe
    assert "[REDACTED" in safe
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/security -v`

Expected: FAIL because security modules do not exist.

- [ ] **Step 3: Implement crypto and redaction**

```python
# app/security/__init__.py
from app.security.crypto import SecretBox
from app.security.redaction import redact

__all__ = ["SecretBox", "redact"]
```

```python
# app/security/crypto.py
import base64
import hashlib

from cryptography.fernet import Fernet


class SecretBox:
    def __init__(self, fernet: Fernet) -> None:
        self._fernet = fernet

    @classmethod
    def from_app_secret(cls, secret: str) -> "SecretBox":
        digest = hashlib.sha256(secret.encode("utf-8")).digest()
        key = base64.urlsafe_b64encode(digest)
        return cls(Fernet(key))

    def encrypt_text(self, value: str) -> str:
        token = self._fernet.encrypt(value.encode("utf-8")).decode("ascii")
        return f"v1:{token}"

    def decrypt_text(self, value: str) -> str:
        version, token = value.split(":", 1)
        if version != "v1":
            raise ValueError(f"Unsupported secret version: {version}")
        return self._fernet.decrypt(token.encode("ascii")).decode("utf-8")
```

```python
# app/security/redaction.py
import re
from typing import Any


PATTERNS = [
    re.compile(r"(TELEGRAM_BOT_TOKEN=)[^\s]+", re.IGNORECASE),
    re.compile(r"(APP_SECRET_KEY=)[^\s]+", re.IGNORECASE),
    re.compile(r"(PrivateKey\s*=\s*)[^\s]+", re.IGNORECASE),
    re.compile(r"(PresharedKey\s*=\s*)[^\s]+", re.IGNORECASE),
    re.compile(r"(external_payment_id=)[^\s]+", re.IGNORECASE),
    re.compile(r"\[Interface\][\s\S]*?(?=\n\s*\n|\Z)", re.IGNORECASE),
]


def redact(value: Any) -> str:
    text = str(value)
    for pattern in PATTERNS:
        text = pattern.sub(lambda match: f"{match.group(1) if match.lastindex else ''}[REDACTED]", text)
    return text
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/security -v`

Expected: PASS.

---

### Task 4: SQLite Schema and Repositories

**Files:**
- Create: `app/db/__init__.py`
- Create: `app/db/connection.py`
- Create: `app/db/schema.py`
- Create: `app/db/repositories.py`
- Test: `tests/db/test_repositories.py`

- [ ] **Step 1: Write failing repository test**

```python
# tests/db/test_repositories.py
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema


def test_repository_creates_user_server_order_and_device(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)

    user_id = repo.upsert_user(telegram_id=1001, username="alice", first_name="Alice", last_name=None)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")
    device_id = repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="iPhone",
        duration_days=7,
        vpn_ip="10.8.0.2",
        peer_public_key="public",
        peer_private_key_encrypted="v1:encrypted",
        preshared_key_encrypted="v1:psk",
        config_version="amneziawg_v2",
    )

    assert repo.count_active_devices(user_id) == 1
    assert repo.get_order(order_id)["status"] == "manual_review"
    assert repo.get_device(device_id)["vpn_ip"] == "10.8.0.2"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/db/test_repositories.py -v`

Expected: FAIL because DB modules do not exist.

- [ ] **Step 3: Implement DB layer**

Implement `connect(path)` with `sqlite3.Row`, schema tables for `users`, `servers`, `devices`, `orders`, `admin_actions`, and repository methods used by the test. Use UTC timestamps from SQLite `CURRENT_TIMESTAMP`.

Key signatures:

```python
def connect(path: str | Path) -> sqlite3.Connection
def initialize_schema(conn: sqlite3.Connection) -> None
class Repository:
    def upsert_user(...) -> int
    def ensure_default_server(...) -> int
    def create_order(...) -> int
    def get_order(order_id: int) -> sqlite3.Row
    def create_device(...) -> int
    def get_device(device_id: int) -> sqlite3.Row
    def count_active_devices(user_id: int) -> int
    def list_allocated_ips(server_id: int) -> list[str]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/db/test_repositories.py -v`

Expected: PASS.

---

### Task 5: IPAM

**Files:**
- Create: `app/vpn/__init__.py`
- Create: `app/vpn/ipam.py`
- Test: `tests/vpn/test_ipam.py`

- [ ] **Step 1: Write failing IPAM tests**

```python
# tests/vpn/test_ipam.py
import pytest

from app.vpn.ipam import IpPoolExhausted, allocate_ip


def test_allocate_ip_skips_network_server_broadcast_and_used_addresses():
    ip = allocate_ip(
        cidr="10.8.0.0/29",
        server_address="10.8.0.1",
        used_ips={"10.8.0.2", "10.8.0.3"},
    )

    assert ip == "10.8.0.4"


def test_allocate_ip_reports_pool_exhaustion():
    with pytest.raises(IpPoolExhausted):
        allocate_ip(
            cidr="10.8.0.0/30",
            server_address="10.8.0.1",
            used_ips={"10.8.0.2"},
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/vpn/test_ipam.py -v`

Expected: FAIL because `app.vpn.ipam` does not exist.

- [ ] **Step 3: Implement IPAM**

```python
# app/vpn/__init__.py
__all__ = []
```

```python
# app/vpn/ipam.py
from ipaddress import ip_address, ip_network


class IpPoolExhausted(RuntimeError):
    pass


def allocate_ip(cidr: str, server_address: str, used_ips: set[str]) -> str:
    network = ip_network(cidr, strict=False)
    server_ip = ip_address(server_address.split("/", 1)[0])
    used = {ip_address(value) for value in used_ips}

    for candidate in network.hosts():
        if candidate == server_ip:
            continue
        if candidate in used:
            continue
        return str(candidate)

    raise IpPoolExhausted(f"No free IPs in {cidr}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/vpn/test_ipam.py -v`

Expected: PASS.

---

### Task 6: AmneziaWG Config Generation

**Files:**
- Create: `app/vpn/amneziawg_v2/__init__.py`
- Create: `app/vpn/amneziawg_v2/config.py`
- Create: `app/vpn/amneziawg_v2/keys.py`
- Test: `tests/vpn/test_amneziawg_config.py`

- [ ] **Step 1: Write failing config renderer test**

```python
# tests/vpn/test_amneziawg_config.py
from app.vpn.amneziawg_v2.config import ClientConfigInput, render_client_config


def test_render_client_config_contains_expected_fields():
    config = render_client_config(
        ClientConfigInput(
            private_key="client-private",
            address="10.8.0.2/32",
            dns="1.1.1.1",
            server_public_key="server-public",
            preshared_key="psk",
            endpoint="vpn.example.com:30001",
            allowed_ips="0.0.0.0/0",
            persistent_keepalive=25,
            jc=4,
            jmin=40,
            jmax=70,
            s1=0,
            s2=0,
            h1=1,
            h2=2,
            h3=3,
            h4=4,
        )
    )

    assert "[Interface]" in config
    assert "PrivateKey = client-private" in config
    assert "Address = 10.8.0.2/32" in config
    assert "DNS = 1.1.1.1" in config
    assert "[Peer]" in config
    assert "PublicKey = server-public" in config
    assert "PresharedKey = psk" in config
    assert "Endpoint = vpn.example.com:30001" in config
    assert "AllowedIPs = 0.0.0.0/0" in config
    assert "PersistentKeepalive = 25" in config
    assert "Jc = 4" in config
    assert "H4 = 4" in config
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/vpn/test_amneziawg_config.py -v`

Expected: FAIL because renderer does not exist.

- [ ] **Step 3: Implement renderer and key interface**

```python
# app/vpn/amneziawg_v2/__init__.py
from app.vpn.amneziawg_v2.config import ClientConfigInput, render_client_config

__all__ = ["ClientConfigInput", "render_client_config"]
```

```python
# app/vpn/amneziawg_v2/config.py
from dataclasses import dataclass


@dataclass(frozen=True)
class ClientConfigInput:
    private_key: str
    address: str
    dns: str
    server_public_key: str
    preshared_key: str
    endpoint: str
    allowed_ips: str
    persistent_keepalive: int
    jc: int
    jmin: int
    jmax: int
    s1: int
    s2: int
    h1: int
    h2: int
    h3: int
    h4: int


def render_client_config(data: ClientConfigInput) -> str:
    return "\n".join(
        [
            "[Interface]",
            f"PrivateKey = {data.private_key}",
            f"Address = {data.address}",
            f"DNS = {data.dns}",
            f"Jc = {data.jc}",
            f"Jmin = {data.jmin}",
            f"Jmax = {data.jmax}",
            f"S1 = {data.s1}",
            f"S2 = {data.s2}",
            f"H1 = {data.h1}",
            f"H2 = {data.h2}",
            f"H3 = {data.h3}",
            f"H4 = {data.h4}",
            "",
            "[Peer]",
            f"PublicKey = {data.server_public_key}",
            f"PresharedKey = {data.preshared_key}",
            f"Endpoint = {data.endpoint}",
            f"AllowedIPs = {data.allowed_ips}",
            f"PersistentKeepalive = {data.persistent_keepalive}",
            "",
        ]
    )
```

```python
# app/vpn/amneziawg_v2/keys.py
import base64
import secrets


def generate_key() -> str:
    return base64.b64encode(secrets.token_bytes(32)).decode("ascii")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/vpn/test_amneziawg_config.py -v`

Expected: PASS.

---

### Task 7: Backup Manifest, Create, Verify, Restore

**Files:**
- Create: `app/backup/__init__.py`
- Create: `app/backup/manifest.py`
- Create: `app/backup/storage.py`
- Create: `app/backup/service.py`
- Create: `app/cli.py`
- Test: `tests/backup/test_backup_service.py`

- [ ] **Step 1: Write failing backup tests**

```python
# tests/backup/test_backup_service.py
import os

import pytest

from app.backup.service import BackupService
from app.db.connection import connect
from app.db.schema import initialize_schema


def test_backup_create_verify_and_restore_requires_secret(tmp_path, monkeypatch):
    db_path = tmp_path / "source.sqlite3"
    conn = connect(db_path)
    initialize_schema(conn)
    conn.close()

    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    service = BackupService(app_version="0.1.0")
    backup_path = service.create(db_path=db_path, output_dir=tmp_path / "backups")

    assert backup_path.exists()
    manifest = service.verify(backup_path)
    assert manifest["database_kind"] == "sqlite"
    assert "app_secret_key" in manifest["excludes"]

    monkeypatch.delenv("APP_SECRET_KEY")
    with pytest.raises(RuntimeError, match="APP_SECRET_KEY"):
        service.restore(backup_path=backup_path, target_db_path=tmp_path / "restored.sqlite3")


def test_restore_refuses_overwrite_without_force(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    db_path = tmp_path / "source.sqlite3"
    target_path = tmp_path / "target.sqlite3"
    initialize_schema(connect(db_path))
    initialize_schema(connect(target_path))

    service = BackupService(app_version="0.1.0")
    backup_path = service.create(db_path=db_path, output_dir=tmp_path / "backups")

    with pytest.raises(FileExistsError):
        service.restore(backup_path=backup_path, target_db_path=target_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/backup/test_backup_service.py -v`

Expected: FAIL because backup modules do not exist.

- [ ] **Step 3: Implement backup service**

Use `tarfile` to package `database.sqlite3` and `manifest.json`, then encrypt archive bytes with `SecretBox` from `APP_SECRET_KEY`. Store encrypted output with suffix `.tar.enc`.

Key signatures:

```python
class BackupService:
    def __init__(self, app_version: str) -> None
    def create(self, db_path: Path, output_dir: Path) -> Path
    def verify(self, backup_path: Path) -> dict
    def restore(self, backup_path: Path, target_db_path: Path, force: bool = False) -> Path
```

Manifest must include:

```python
{
    "format_version": 1,
    "app": "amneziya",
    "app_version": self.app_version,
    "database_kind": "sqlite",
    "database_checksum_sha256": checksum,
    "includes": ["database", "manifest"],
    "excludes": ["app_secret_key", "telegram_bot_token", "qr_files", "plain_configs"],
}
```

`restore()` must:

- fail if `APP_SECRET_KEY` is missing;
- fail if target exists and `force` is false;
- verify checksum before writing the target DB;
- write only the database file to the target path.

- [ ] **Step 4: Add CLI wrapper**

```python
# app/cli.py
import argparse
from pathlib import Path

from app import __version__
from app.backup.service import BackupService


def main() -> None:
    parser = argparse.ArgumentParser(prog="amneziya")
    sub = parser.add_subparsers(dest="command", required=True)

    backup = sub.add_parser("backup")
    backup_sub = backup.add_subparsers(dest="backup_command", required=True)

    create = backup_sub.add_parser("create")
    create.add_argument("--db", default="data/amneziya.sqlite3")
    create.add_argument("--output", default="backups")

    verify = backup_sub.add_parser("verify")
    verify.add_argument("--file", required=True)

    restore = backup_sub.add_parser("restore")
    restore.add_argument("--file", required=True)
    restore.add_argument("--target-db", required=True)
    restore.add_argument("--force", action="store_true")

    args = parser.parse_args()
    service = BackupService(app_version=__version__)

    if args.command == "backup" and args.backup_command == "create":
        print(service.create(Path(args.db), Path(args.output)))
    elif args.command == "backup" and args.backup_command == "verify":
        print(service.verify(Path(args.file)))
    elif args.command == "backup" and args.backup_command == "restore":
        print(service.restore(Path(args.file), Path(args.target_db), force=args.force))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/backup/test_backup_service.py -v`

Expected: PASS.

---

### Task 8: Access Approval Service

**Files:**
- Create: `app/services/__init__.py`
- Create: `app/services/access.py`
- Test: `tests/services/test_access_service.py`

- [ ] **Step 1: Write failing service tests**

```python
# tests/services/test_access_service.py
import pytest

from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.security.crypto import SecretBox
from app.services.access import AccessService, MaxDevicesReached


def test_approve_order_creates_active_device_with_encrypted_secrets(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id = repo.upsert_user(telegram_id=1001, username="alice", first_name="Alice", last_name=None)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")

    service = AccessService(repo=repo, secret_box=SecretBox.from_app_secret("test-secret"))
    result = service.approve_order(order_id=order_id, server_id=server_id, device_name="iPhone", admin_telegram_id=999)

    device = repo.get_device(result.device_id)
    assert device["status"] == "active"
    assert device["vpn_ip"] == "10.8.0.2"
    assert device["peer_private_key_encrypted"].startswith("v1:")
    assert "PrivateKey =" in result.config_text


def test_approve_order_enforces_max_devices(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id = repo.upsert_user(telegram_id=1001, username="alice", first_name="Alice", last_name=None)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")

    service = AccessService(repo=repo, secret_box=SecretBox.from_app_secret("test-secret"), max_devices_per_user=1)
    first_order = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")
    second_order = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")
    service.approve_order(first_order, server_id, "iPhone", admin_telegram_id=999)

    with pytest.raises(MaxDevicesReached):
        service.approve_order(second_order, server_id, "Laptop", admin_telegram_id=999)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/services/test_access_service.py -v`

Expected: FAIL because service does not exist or repository lacks needed methods.

- [ ] **Step 3: Implement access service**

```python
# app/services/__init__.py
from app.services.access import AccessApprovalResult, AccessService

__all__ = ["AccessApprovalResult", "AccessService"]
```

```python
# app/services/access.py
from dataclasses import dataclass

from app.db.repositories import Repository
from app.security.crypto import SecretBox
from app.vpn.amneziawg_v2.config import ClientConfigInput, render_client_config
from app.vpn.amneziawg_v2.keys import generate_key
from app.vpn.ipam import allocate_ip


class MaxDevicesReached(RuntimeError):
    pass


@dataclass(frozen=True)
class AccessApprovalResult:
    device_id: int
    config_text: str


class AccessService:
    def __init__(self, repo: Repository, secret_box: SecretBox, max_devices_per_user: int = 5) -> None:
        self.repo = repo
        self.secret_box = secret_box
        self.max_devices_per_user = max_devices_per_user

    def approve_order(self, order_id: int, server_id: int, device_name: str, admin_telegram_id: int) -> AccessApprovalResult:
        order = self.repo.get_order(order_id)
        user_id = int(order["user_id"])
        if self.repo.count_active_devices(user_id) >= self.max_devices_per_user:
            raise MaxDevicesReached("User reached device limit")

        server = self.repo.get_server(server_id)
        vpn_ip = allocate_ip(server["vpn_network_cidr"], server["server_address"], set(self.repo.list_allocated_ips(server_id)))
        private_key = generate_key()
        public_key = generate_key()
        preshared_key = generate_key()
        config_text = render_client_config(
            ClientConfigInput(
                private_key=private_key,
                address=f"{vpn_ip}/32",
                dns="1.1.1.1",
                server_public_key=server["server_public_key"],
                preshared_key=preshared_key,
                endpoint=f"{server['endpoint_host']}:{server['vpn_port']}",
                allowed_ips="0.0.0.0/0",
                persistent_keepalive=25,
                jc=4,
                jmin=40,
                jmax=70,
                s1=0,
                s2=0,
                h1=1,
                h2=2,
                h3=3,
                h4=4,
            )
        )
        device_id = self.repo.create_device(
            user_id=user_id,
            server_id=server_id,
            name=device_name,
            duration_days=7,
            vpn_ip=vpn_ip,
            peer_public_key=public_key,
            peer_private_key_encrypted=self.secret_box.encrypt_text(private_key),
            preshared_key_encrypted=self.secret_box.encrypt_text(preshared_key),
            config_version="amneziawg_v2",
        )
        self.repo.mark_order_fulfilled(order_id)
        self.repo.record_admin_action(admin_telegram_id, "approve_order", user_id, device_id, {"order_id": order_id})
        return AccessApprovalResult(device_id=device_id, config_text=config_text)
```

Add repository methods `get_server`, `mark_order_fulfilled`, and `record_admin_action`. Ensure default server includes `server_address="10.8.0.1"` and placeholder endpoint/public key suitable for local generation.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/services/test_access_service.py -v`

Expected: PASS.

---

### Task 9: Minimal Telegram Bot Entry Point

**Files:**
- Create: `app/bot/__init__.py`
- Create: `app/bot/main.py`
- Modify: `app/main.py`
- Test: `tests/bot/test_bot_factory.py`

- [ ] **Step 1: Write failing bot factory test**

```python
# tests/bot/test_bot_factory.py
from aiogram import Dispatcher

from app.bot.main import create_dispatcher


def test_create_dispatcher_returns_dispatcher():
    dispatcher = create_dispatcher()

    assert isinstance(dispatcher, Dispatcher)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/bot/test_bot_factory.py -v`

Expected: FAIL because bot module does not exist.

- [ ] **Step 3: Implement minimal bot factory**

```python
# app/bot/__init__.py
from app.bot.main import create_dispatcher

__all__ = ["create_dispatcher"]
```

```python
# app/bot/main.py
from aiogram import Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message


def create_dispatcher() -> Dispatcher:
    router = Router()

    @router.message(CommandStart())
    async def start(message: Message) -> None:
        await message.answer("Amneziya VPN")

    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    return dispatcher
```

```python
# app/main.py
import asyncio

from aiogram import Bot

from app.bot import create_dispatcher
from app.config import Settings


async def run() -> None:
    settings = Settings()
    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = create_dispatcher()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/bot/test_bot_factory.py -v`

Expected: PASS.

---

### Task 10: Full Verification and Docs

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add local development and backup commands to README**

Add a concise section:

```markdown
## Local Development

1. Create `.env` from `.env.example`.
2. Set `TELEGRAM_BOT_TOKEN`, `APP_SECRET_KEY`, and `ADMIN_TELEGRAM_IDS`.
3. Install dependencies.
4. Run tests with `pytest`.
5. Start the bot with `python -m app.main`.

## Backup

Create a local encrypted backup:

```powershell
python -m app.cli backup create --db data/amneziya.sqlite3 --output backups
```

Verify a backup:

```powershell
python -m app.cli backup verify --file backups/<backup-file>.tar.enc
```

Restore to a new database path:

```powershell
python -m app.cli backup restore --file backups/<backup-file>.tar.enc --target-db data/restored.sqlite3
```

The same `APP_SECRET_KEY` used when creating encrypted peer secrets is required for restore validation.
```

- [ ] **Step 2: Run all tests**

Run: `pytest -v`

Expected: all tests PASS.

- [ ] **Step 3: Run a backup smoke test**

Run:

```powershell
$env:APP_SECRET_KEY='replace-with-a-generated-32-plus-character-secret'; python -m app.cli backup create --db data/amneziya.sqlite3 --output backups
```

Expected: either creates backup if DB exists, or prints a clear file-not-found error without leaking secrets.

- [ ] **Step 4: Final status check**

Run: `rg -n "BEGIN .*PRIVATE KEY|TELEGRAM_BOT_TOKEN=[^C]|UNFINISHED_MARKER" .`

Expected: no real secrets or unfinished placeholders outside approved examples.

---

## Self-Review

Spec coverage:

- First local MVP scaffold: covered by Tasks 1, 2, 4, 5, 6, 8, 9, 10.
- Security addendum: covered by Tasks 1, 2, 3, 7, 10.
- Backup/recovery addendum: covered by Tasks 1, 7, 10.
- Telegram minimal entry point: covered by Task 9.
- Tests-first execution: every implementation task starts with a failing test and verify-red step.

Known deferred items:

- Live SSH provisioning and `awg` peer application remain outside this scaffold by approved design.
- Import-link compatibility remains outside this scaffold until verified on a real AmneziaVPN client.
- Automated remote backup upload remains outside this scaffold; local encrypted backup is included.
