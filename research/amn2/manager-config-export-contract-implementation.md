# `amn2`: manager config export contract

Дата: 2026-06-01.

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/manager-config-export-contract
```

Base:

```text
codex/api-token-lifecycle-gate-stacked
```

Production commit:

```text
4d4e7a4 Add manager config export contract
```

## Что добавлено

В `amn2` добавлен local-only no-route contract layer для безопасного экспорта клиентских конфигов:

- `app/services/config_export.py`;
- `ConfigExportRequest`;
- `ConfigExportResult`;
- `ConfigExportArtifact`;
- `export_device_config_delivery()`;
- `run_config_exporter()`;
- `docs/CONFIG_EXPORT_CONTRACT.ru.md`;
- `tests/services/test_config_export.py`.

Слой адаптирует существующий `DeviceConfigDelivery` / `ConfigDeliveryPackage` в typed artifacts:

- `wireguard_conf`;
- `qr_payload`;
- `qr_png`;
- `amnezia_import_uri`;
- `delivery_message`.

Все реальные payload остаются `client-config-secret`. Для audit/log/diagnostics доступна только `safe_metadata()`.

## Граница среза

Срез не добавляет public/self-service config endpoint, `/api/*` route, API `config:read`, Local Agent `/configs`, новый QR/import behavior, live VPS calls или хранение raw config в базе.

Unsupported artifact, unsupported target client и manager signature mismatch возвращают стабильные safe categories без raw traceback, `.conf`, QR payload или `vpn://`.

## Проверка

RED:

```text
tests/services/test_config_export.py -v
result: import error for missing app.services.config_export, as expected
```

Focused:

```text
tests/services/test_config_export.py
tests/services/test_config_delivery.py
tests/bot/test_delivery.py
tests/security/test_redaction.py
tests/security/test_surface_policy.py
tests/security/test_surface_policy_bindings.py
result: 40 passed
```

Full local suite:

```text
python -m pytest -q
result: 560 passed, 1 StarletteDeprecationWarning
```

`git diff --check` прошел без замечаний.

Известное окружение Windows иногда печатает ignored pytest temp cleanup `PermissionError` после успешного exit code `0`; это не меняет результат тестов.

## Следующее решение

Следующий local-only кандидат после этого был выполнен: public/self-service config delivery policy implementation как no-route share-token/policy contract в `amn2/codex/public-config-delivery-policy-contract`, commit `2ef3af7`. Backup/import policy registry тоже выполнен в `amn2/codex/backup-import-policy-contract`, commit `d2c160b`. Если VPS еще не готов, следующий local-only кандидат должен быть меньше: machine-checkable secret inventory registry без route expansion.
