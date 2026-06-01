# `amn2`: контракт public/self-service выдачи конфигов

Дата: 2026-06-01.

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Base:

```text
codex/manager-config-export-contract
```

Production commit:

```text
2ef3af7 Add config share policy contract
```

## Что добавлено

В `amn2` добавлен local-only no-route contract layer для будущей public/self-service выдачи client config artifacts:

- `app/services/config_share_tokens.py`;
- `config_share_tokens` SQLite table;
- repository lifecycle methods для create/auth lookup/use/revoke;
- blocked `SurfacePolicy` entries:
  - `self.device.config_download.blocked`;
  - `public_token.config_share_download.blocked`;
- `docs/CONFIG_SHARE_POLICY.ru.md`;
- `tests/services/test_config_share_tokens.py`.

Контракт покрывает:

- hash-only raw share token discipline;
- required expiry;
- token prefix as display-only metadata;
- purpose `config_share`;
- owner/user/device/server binding;
- allowed artifact kinds;
- target client policy;
- one-time/max-download denial;
- revoke;
- generic public denial;
- safe audit metadata;
- redacted backup metadata with `restore-disabled`.

## Граница среза

Срез не добавляет public download route, self-service config download route, `/api/*`, API `config:read`, Local Agent `/configs`, generated config persistence, new QR/import behavior, live VPS calls или copied upstream implementation.

`evaluate_config_share_download()` возвращает только allow/deny decision and safe audit metadata. Он не возвращает `.conf`, QR, `vpn://` или rendered delivery message.

## Проверка

RED:

```text
tests/services/test_config_share_tokens.py
result: ModuleNotFoundError: No module named 'app.services.config_share_tokens'
```

Дополнительный RED:

```text
tests/services/test_config_share_tokens.py::test_evaluate_config_share_download_denies_unbound_or_unallowed_request
result: empty requested artifacts were incorrectly allowed
```

Focused:

```text
tests/services/test_config_share_tokens.py
tests/services/test_config_export.py
tests/services/test_api_tokens.py
tests/services/test_email_tokens.py
tests/db/test_repositories.py
tests/security/test_redaction.py
tests/security/test_surface_policy.py
tests/security/test_surface_policy_bindings.py
tests/bot/test_delivery.py
tests/services/test_config_delivery.py
result: 94 passed
```

Full local suite:

```text
python -m pytest -q
result: 577 passed, 1 StarletteDeprecationWarning
```

`git diff --check` прошел без замечаний.

Известное окружение Windows иногда печатает ignored pytest temp cleanup `PermissionError` после успешного exit code `0`; это не меняет результат тестов.

## Следующее решение

Backup/import policy registry and restore-preview contract уже выполнен в `amn2/codex/backup-import-policy-contract`, head `afb2702` with foundation commit `d2c160b`; secret inventory registry выполнен в `amn2/codex/secret-inventory-registry`, commit `9ce42f4`. Generic route-policy/audit/rate-limit guards уже закрыты, поэтому если VPS еще не готов, дальнейшая local-only работа должна быть только синхронизацией roadmap/evidence, без route expansion, secret-bearing output или live VPS.
