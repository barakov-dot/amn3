# Phase 4 P4-PRVTPRO-REFRESH-002: expiration contract tests implementation 2026-06-10

Назначение: закрыть `P4-PRVTPRO-REFRESH-002` как AMN2 local-only product slice после PRVTPRO refresh 2026-06-10. Slice добавляет regression coverage и read-only отображение срока действия устройства в web-admin user detail.

## Gate Summary

```text
task_id: P4-PRVTPRO-REFRESH-002
source_signal: research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md
source_license_boundary: PRVTPRO/Amnezia-Web-Panel GPL-3.0 research-only
amn2_branch: codex/phase-4-prvtpro-expiration-contracts
amn2_commit: b2eceeb111a0a27e41daf7b9ae7c79b5a0195e51 Show device expiration in web admin
implementation_class: local-only
live_vps_commands: no
ssh_commands: no
public_exposure_changed: no
api_routes_added_or_changed: no
write_api_added_or_changed: no
config_delivery_changed: no
local_agent_mutation_changed: no
backup_import_reboot_changed: no
production_peer_or_user_mutation: no
gpl_code_copied: no
go_no_go_decision: go
```

## AMN2 Changes

- `app/db/repositories.py`: `list_user_devices_for_admin()` now selects `devices.expires_at` for existing local admin detail rendering.
- `app/web/templates/user_detail.html`: the Devices table now has a read-only `Expires` column and displays `device.expires_at` or `-`.
- `tests/web/test_users.py`: added `test_user_detail_shows_device_expiration_contract`, which pins that a synthetic device expiration value reaches the web-admin user detail page.

The change does not add routes, POST handlers, write API, config delivery, token issue/revoke flow, live peer sync, backup/import/reboot behavior, public listeners or Local Agent mutations.

## TDD Evidence

RED:

```text
python -m pytest tests\web\test_users.py::test_user_detail_shows_device_expiration_contract -q
result: failed as expected
failure: expected 2026-06-27 12:00:00 to appear in /users/{user_id}
```

GREEN:

```text
python -m pytest tests\web\test_users.py::test_user_detail_shows_device_expiration_contract -q
result: 1 passed, 1 warning
```

Regression scope:

```text
python -m pytest tests\web\test_users.py -q
result: 23 passed, 1 warning
warning: existing StarletteDeprecationWarning from fastapi.testclient/httpx
```

Hygiene:

```text
git diff --check
result: passed
git diff --cached --check
result: passed before AMN2 commit
```

## Safety Notes

This slice uses the PRVTPRO refresh only as a regression signal. No GPL code, templates, UI implementation, manager implementation or workflow was copied. The AMN2 UI text and tests are native AMN2 changes.

The expiration field is shown only inside the already-authenticated local web-admin user detail view. It does not expose config contents, QR, `vpn://`, private keys, PSK, raw endpoint values, tokens, Authorization headers, token hashes, `.env`, `servers.yml`, backups or full logs.

## Closure

`P4-PRVTPRO-REFRESH-002` is closed. The remaining PRVTPRO-derived local-only queue now starts with `P4-PRVTPRO-REFRESH-001` read-only About/Version/Build status, followed by `P4-PRVTPRO-REFRESH-003` after design boundary and `P4-PRVTPRO-REFRESH-004` as docs/policy support.
