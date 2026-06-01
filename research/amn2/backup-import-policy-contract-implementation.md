# `amn2`: backup/import policy contract implementation

Дата: 2026-06-01.

Статус: `implemented-pushed-local-gate-complete`.

## Production branch

```text
repo: C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-backup-import-policy-contract
branch: codex/backup-import-policy-contract
remote: amn2/codex/backup-import-policy-contract
commit: d2c160b Add backup import policy contract
base: amn2/codex/public-config-delivery-policy-contract
```

## Что добавлено

- `app.backup.policy` - local-only registry для `metadata-export`, `redacted-backup` и `encrypted-full-backup`.
- Secret field policy для token hashes, peer private key, PSK, admin password hash, `.conf`, QR payload/PNG и `vpn://`.
- `build_backup_policy_manifest()` - safe policy manifest без raw secret values.
- `create_restore_preview()` и `create_import_preview()` - preview-only contracts with `apply_allowed=false`, `side_effects=[]` и safe counts/warnings.
- Blocked future `SurfacePolicy` entries для backup/export, restore preview/apply и import preview/apply.
- `docs/BACKUP_IMPORT_POLICY.ru.md` - operator-facing boundary для будущих backup/import routes.

## Что намеренно не добавлено

- `/api/*` routes.
- Web backup/download/import routes.
- Local Agent `/backup` или `/restore`.
- Public/self-service backup/import.
- Restore apply или import apply.
- Backup-before-write mutation.
- Live VPS calls.
- Копирование PRVTPRO/KYORESUAS code.

## Verification

RED:

```text
tests/backup/test_backup_policy.py tests/security/test_surface_policy.py -q
result: 1 import error as expected
missing: app.backup.policy
```

Focused:

```text
tests/backup/test_backup_policy.py
tests/backup/test_backup_service.py
tests/security/test_surface_policy.py
tests/security/test_surface_policy_bindings.py
tests/services/test_config_share_tokens.py
result: 63 passed
```

Full local suite:

```text
pytest -q
result: 583 passed, 1 StarletteDeprecationWarning
```

`git diff --check`: clean.

Примечание: после successful pytest sessions на Windows снова появился ожидаемый ignored `PermissionError` от pytest temp cleanup для `pytest-current`; команды вернули exit code 0.

## Gate decision

VPS gate для этого slice не нужен. Slice не меняет peer apply/revoke/config delivery/sync/runtime behavior и не пишет live state.

Следующий recommended step теперь зависит от готовности VPS:

- если VPS готов - выполнить controlled real VPS verification gate для `codex/remote-operation-vps-gate-prep`;
- если VPS все еще не готов - брать только маленький local-only слой вроде machine-checkable secret inventory registry, без routes и без secret-bearing output.
