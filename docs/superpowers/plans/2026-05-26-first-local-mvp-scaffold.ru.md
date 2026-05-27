# План реализации первого локального MVP

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Цель:** создать первый локальный каркас Amneziya: Python app с конфигурацией, SQLite, генерацией AmneziaWG config, encrypted secrets, backup/restore и минимальным Telegram bot entrypoint.

**Архитектура:** проект делится на маленькие независимые слои: `config`, `db`, `security`, `vpn`, `services`, `backup`, `bot`, `cli`. Все dangerous operations защищены tests и не касаются реального VPS.

**Tech Stack:** Python 3.12+, pytest, pydantic-settings, cryptography, aiogram, qrcode, SQLite.

---

## File Structure

Созданные области:

```text
app/
  backup/
  bot/
  config/
  db/
  security/
  services/
  vpn/
    amneziawg_v2/
  cli.py
  main.py
tests/
docs/
```

## Task 1: Project Metadata and Environment

- [x] Create `pyproject.toml`.
- [x] Create `.env.example`.
- [x] Add `.gitignore` for secrets/runtime files.
- [x] Add package version in `app/__init__.py`.
- [x] Add settings loader in `app/config/settings.py`.
- [x] Test required `APP_SECRET_KEY`, Telegram token, admin IDs, notice days, and VPN port bounds.

## Task 2: Security Layer

- [x] Implement `SecretBox` for symmetric encryption.
- [x] Reject weak or repeated secrets by default.
- [x] Normalize crypto errors into public `SecretBoxError`.
- [x] Implement redaction for tokens, app secrets, private keys, PSK, configs, and payment IDs.
- [x] Add tests proving plaintext is not stored and logs are redacted.

## Task 3: Database Schema and Repositories

- [x] Add SQLite connection helper.
- [x] Add schema for users, servers, devices, plans, orders, and admin actions.
- [x] Implement repositories with transaction helpers.
- [x] Enforce device statuses and foreign keys.
- [x] Ensure fulfilled orders cannot point to another user's device.
- [x] Test IP reuse after revocation and allocated-IP filtering.

## Task 4: VPN IPAM and AmneziaWG Config

- [x] Implement CIDR-aware IP allocation.
- [x] Skip network, broadcast, server address, and used IPs.
- [x] Reject out-of-pool and family-mismatched addresses.
- [x] Implement X25519 keypair and PSK generation.
- [x] Render AmneziaWG client config with expected fields.
- [x] Test generated keys and config output.

## Task 5: Access Service

- [x] Implement admin approval workflow.
- [x] Create active device with encrypted secrets.
- [x] Enforce max devices per user.
- [x] Reject already fulfilled or non-approvable orders.
- [x] Roll back device/order if audit write fails.
- [x] Retry IP allocation on duplicate-IP race.
- [x] Return clear errors when IP allocation exhausts.

## Task 6: Backup and Restore

- [x] Implement encrypted backup archive.
- [x] Add manifest and checksum verification.
- [x] Add `backup create`, `backup verify`, `backup restore` CLI.
- [x] Reject archive with extra members.
- [x] Reject invalid SQLite.
- [x] Reject checksum mismatch.
- [x] Reject restore with incompatible `APP_SECRET_KEY`.
- [x] Avoid overwriting target DB before all verification passes.

## Task 7: Minimal Bot and CLI

- [x] Add aiogram bot factory.
- [x] Add minimal `/start` behavior.
- [x] Add `app/main.py`.
- [x] Add CLI entrypoint for backup commands.
- [x] Keep bot logic isolated from VPN generation and DB internals.

## Task 8: Documentation

- [x] Add technical specification.
- [x] Add data model.
- [x] Add server management notes.
- [x] Add beginner guide for the next stage.
- [x] Document backup and data-protection requirements.

## Verification

Final test command:

```powershell
$env:PYTHONPATH='.codex_deps;.'; python -m pytest tests -v
```

Expected result:

```text
57 passed
```

Later server-check work expanded the suite to `72 passed`.

## Deferred

- Real SSH connection.
- VPS provisioning.
- Live peer apply/revoke.
- Real payments.
- Multi-server selection.
- Production deployment packaging.

## Notes

This Russian version is a compact working equivalent of the original long English implementation plan. The exact original task snippets and test code remain available in `2026-05-26-first-local-mvp-scaffold.en.md`.
