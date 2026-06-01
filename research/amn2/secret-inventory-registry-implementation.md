# `amn2`: secret inventory registry implementation

Дата: 2026-06-01.

Статус: `implemented-pushed-local-gate-complete`.

## Production branch

```text
repo: C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-secret-inventory-registry
branch: codex/secret-inventory-registry
remote: amn2/codex/secret-inventory-registry
commit: 9ce42f4 Add secret inventory registry
base: amn2/codex/backup-import-policy-contract
```

## Что добавлено

- `app.security.secret_inventory` - machine-checkable registry для secret-bearing state.
- `SecretInventoryEntry` с `inventory_id`, `source_ref`, secret class, storage surface, backup/restore defaults, route exposure and safe metadata policy.
- Lookup/filter helpers: `get_secret_inventory_entry()`, `entries_by_secret_class()`, `entries_by_storage_surface()`.
- `build_secret_inventory_manifest()` - policy-only manifest без secret values.
- Cross-check с `app.backup.policy.secret_field_sources()`.
- `docs/SECRET_INVENTORY.ru.md` - local-only no-route boundary.

## Что намеренно не добавлено

- Чтение `.env`.
- DB access.
- `/api/*` routes.
- Web/Local Agent secret routes.
- Backup export или restore/import apply.
- Secret-bearing output.
- Live VPS calls.

## Verification

RED:

```text
tests/security/test_secret_inventory.py -q
result: 1 import error as expected
missing: app.security.secret_inventory
```

Focused:

```text
tests/security/test_secret_inventory.py
tests/security/test_redaction.py
tests/security/test_surface_policy.py
tests/backup/test_backup_policy.py
tests/services/test_api_tokens.py
tests/services/test_config_share_tokens.py
tests/services/test_email_tokens.py
result: 64 passed
```

Full local suite:

```text
pytest -q
result: 591 passed, 1 StarletteDeprecationWarning
```

`git diff --check`: clean.

Примечание: после full pytest на Windows появился ожидаемый ignored `PermissionError` от pytest temp cleanup для `pytest-current`; команда вернула exit code 0.

## Gate decision

VPS gate для этого slice не нужен. Slice не меняет peer apply/revoke/config delivery/sync/runtime behavior и не работает с live state.

Следующий главный шаг остается controlled real VPS verification gate для `codex/remote-operation-vps-gate-prep`. Если VPS все еще недоступен, новый local-only implementation slice лучше не открывать: generic route-policy/audit/rate-limit guards уже закрыты, а дальнейшая локальная работа должна быть только синхронизацией roadmap/evidence.
