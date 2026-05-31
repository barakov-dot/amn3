# `amn2`: redaction coverage plan

## Паспорт

- Production repo: `C:\Users\SooL\Documents\Amneziya`
- Дата плана: 2026-05-31
- Режим: lab policy + implementation handoff, без изменений в `amn2`.
- Секреты: `.env` и реальные runtime-секреты намеренно не читаются.
- Входные материалы:
  - [Secret surface inventory](secret-surface-inventory.md)
  - [Config delivery inventory](config-delivery-inventory.md)
  - [Route/Auth Policy Matrix](route-policy-matrix.md)
  - [Remote operations inventory](remote-operations-inventory.md)

## Решение

Статус: `redaction-coverage-first-slice-verified`.

Перед расширением `RemoteOperationRunner` на state-changing операции нужно закрыть redaction coverage как P0 gate. Это не новая пользовательская функция, а страховочный слой: он доказывает, что config artifacts, tokens, Local Agent credentials, command output и diagnostics не попадают в logs, audit metadata, error responses, backup/plain exports и debug snapshots.

План не переносит код из внешних проектов. Он использует текущую архитектуру `amn2` и расширяет собственные проверки вокруг уже существующих точек: `app/security/redaction.py`, config delivery, web email flows, peer apply/revoke, runtime diagnostics и hygiene tests.

## Обновление 2026-05-31: first slice verified

Implementation выполнен в isolated worktree:

```text
branch: codex/redaction-coverage-first-slice
head: f4bfb51 Document secret-bearing delivery artifacts
```

Локальные commits в `amn2`:

- `7151336 Expand redaction primitive coverage`
- `325d52e Add config delivery redaction coverage`
- `68184a8 Harden config email audit coverage`
- `36d3b3e Harden remote output redaction coverage`
- `f4bfb51 Document secret-bearing delivery artifacts`

Проверка:

- focused security/delivery/web/server/runtime suite: `61 passed`, `1 warning`;
- full suite: `513 passed`, `1 warning`;
- warning: прежний внешний `StarletteDeprecationWarning` из `fastapi.testclient`;
- Windows после завершения pytest иногда печатает temp cleanup `PermissionError` для `pytest-current`, но pytest возвращает exit code `0`.

Итог: P0 redaction coverage для `.conf`, QR payload/PNG, `vpn://`, bearer/agent headers, future TOTP/otpauth markers, web/email audit metadata и remote stdout/stderr закрыт первым verified slice. Следующий блок remote safety - partial-failure/rollback contract для state-changing operations.

## Главный принцип

Если значение может открыть VPN-доступ, админ-доступ, agent-доступ или восстановление config, оно считается raw secret даже тогда, когда выглядит как ссылка, QR payload, base64, hash или diagnostic text.

Минимальное правило:

- raw secret можно показывать только в явном delivery/enrollment канале;
- raw secret нельзя писать в logs, audit metadata, exceptions, diagnostics, metrics, backup manifest text, OpenAPI examples и test fixtures как реалистичный production-секрет;
- `redact()` должен быть безопасным default для любых строк, которые могут попасть в operator-facing output;
- для binary artifacts, например QR PNG, правило не "редактировать картинку", а не включать ее в diagnostics/plain backup и тестировать payload отдельно.

## Coverage matrix

| Surface | Secret class | Где может утечь | Минимальное покрытие |
| --- | --- | --- | --- |
| Raw `.conf` | `client-config-secret` | logs, audit, error text, attachments, diagnostics | config block redaction, no audit payload, `.gitignore`/backup excludes |
| QR payload text | `client-config-secret` | debug output, tests, exception text | redacts как config block; QR PNG не сохранять в diagnostics/plain backup |
| QR PNG bytes | `client-config-secret` | temp files, backup, debug snapshot | не логировать bytes/base64; хранить только как delivery artifact |
| `vpn://` import link | `client-config-secret` | message logs, email debug, audit metadata | redact entire URI; decode/round-trip tests отдельно от logs |
| Email verification/recovery raw token | `token-raw` | audit, URL logs, email sender errors | hash-only storage, no raw token in metadata, generic public errors |
| Email token hash | `token-hash` | redacted backup, admin views | не считать public metadata; показывать только purpose/status/id |
| Future scoped/share token raw | `token-raw` | API response logs, CLI output, audit | one-time display, hash-only storage, no logs |
| Local Agent raw token | `credential-secret` / `token-raw` | enrollment output, headers, diagnostics | one-time display, hash-only storage, header redaction |
| Local Agent token hash | `token-hash` | DB backup, admin detail | metadata only; raw value never restored from backup |
| `Authorization: Bearer ...` | `credential-secret` | reverse proxy/app logs, diagnostics | header value redaction |
| `X-Amneziya-Agent-Token` | `credential-secret` | Local Agent request logs | header value redaction |
| SSH/VPS password/private key path | `credential-secret` / `private-key` | CLI args, error output, diagnostics | no secret in command string; redact stdout/stderr |
| Peer PSK stdin | `remote-command-secret` | command string, stdout/stderr, Docker config write | never in command args; redact remote errors |
| Docker AmneziaWG config stdout | `client-config-secret` | peer apply/revoke errors, diagnostics | summarize stdout when possible; redact stderr/config fragments |
| Traffic/handshake metrics | `secret-adjacent` | metrics labels, long retention logs | aggregate default, detailed labels only after privacy review |
| TOTP/2FA future secrets | `credential-secret` | logs, backup, QR/provisioning URI | keep paused, but reserve redaction patterns for `otpauth://` and TOTP terms |

## Existing baseline

Сильные места в текущем `amn2` baseline:

- `app/security/redaction.py` уже редактирует WireGuard/AmneziaWG config blocks, `PrivateKey`, `PresharedKey`, common `PASSWORD`/`TOKEN`/`SECRET` settings, Telegram bot URL token fragments и payment id.
- `tests/security/test_redaction.py` проверяет realistic secret log formats, quoted values and web-admin/SMTP secret settings.
- `tests/test_file_hygiene.py` проверяет `.gitignore` для `.env`, DB, `.conf`, QR PNG, `servers.yml`, backups и runtime temp paths.
- `tests/services/test_config_delivery.py` проверяет UTF-8 `.conf`, QR payload, `vpn://` round-trip и `client-config-secret` metadata.
- `tests/web/test_email_delivery.py` проверяет hash-only email tokens, one-time behavior и отсутствие config/private key в audit metadata.
- `tests/server/test_peer_apply.py` проверяет, что PSK не попадает в command string и errors redacted.

Основные gaps:

- `vpn://` link пока не закреплен как redaction pattern, хотя является обратимым config artifact.
- Authorization/Bearer и future Local Agent token headers нужно явно закрыть, чтобы diagnostics/logging не зависели только от key/value env patterns.
- `otpauth://`, `TOTP_SECRET`, `BACKUP_CODE`, `RECOVERY_CODE` стоит закрыть заранее, хотя 2FA сейчас paused.
- Нужно добавить aggregate tests, которые показывают: если delivery message, command error или diagnostic text проходит через `redact()`, raw config/link/token не остается.
- Для binary QR PNG нужно явно зафиксировать правило: проверяется payload/round-trip, но PNG не должен попадать в debug snapshot или plain backup.

## Implementation slices

### Slice 1. Redaction primitives

Цель: расширить `app/security/redaction.py` и тесты так, чтобы `redact()` закрывал:

- entire `vpn://...` import URI;
- `otpauth://...` provisioning URI;
- `Authorization: Bearer ...`;
- `X-Amneziya-Agent-Token: ...`;
- `LOCAL_AGENT_TOKEN`, `AGENT_TOKEN`, `TOTP_SECRET`, `MFA_SECRET`, `BACKUP_CODE`, `RECOVERY_CODE`;
- quoted and unquoted values with commas/spaces, как уже сделано для текущих secret settings.

Основные тесты: `tests/security/test_redaction.py`.

### Slice 2. Config delivery redaction coverage

Цель: доказать, что config delivery artifacts остаются delivery-only secrets:

- `.conf` bytes равны UTF-8 config, но не появляются в audit metadata;
- QR payload равен config, но redacted при попадании в text output;
- `vpn://` link decodes back to config, но redacted при попадании в logs/audit/errors;
- `message_text`, где есть `{vpn_link}`, не считается safe log payload.

Основные тесты:

- `tests/bot/test_delivery.py`
- `tests/services/test_config_delivery.py`
- `tests/web/test_email_delivery.py`

### Slice 3. Remote output redaction coverage

Цель: закрыть command stdout/stderr и Docker config read/write paths до расширения state-changing операций:

- host apply/revoke errors не показывают PSK;
- Docker config read/write/restart errors не показывают config block, PSK или `vpn://`;
- dry-run output не содержит raw PSK;
- `RemoteOperationRunner` recovery note и error message остаются redacted.

Основные тесты:

- `tests/server/test_peer_apply.py`
- `tests/server/test_operation_runner.py`
- `tests/server/test_checks.py`

### Slice 4. Diagnostics and hygiene

Цель: не дать secret artifacts попасть в файлы и debug snapshots:

- `.gitignore` продолжает исключать `.env`, DB, `.conf`, QR PNG, backups, `servers.yml`, temp/runtime paths;
- runtime diagnostic scripts не печатают raw config, tokens, private key, PSK, agent token;
- docs фиксируют, что QR PNG и `vpn://` являются secret-bearing artifacts.

Основные тесты:

- `tests/test_file_hygiene.py`
- `tests/deploy/test_runtime_registry.py`
- docs review: `docs/RUNTIME_REGISTRY.ru.md`, при необходимости `docs/RUNTIME_REGISTRY.en.md`.

## Acceptance criteria

Redaction coverage считается готовым для переноса в `amn2`, когда:

1. Есть failing-first tests для новых secret formats: `vpn://`, `otpauth://`, bearer header, agent token header, TOTP/backup/recovery names.
2. `redact()` удаляет raw secret value целиком, а не только часть строки.
3. Config delivery tests доказывают две вещи одновременно: artifacts корректно формируются и те же artifacts исчезают после `redact()`.
4. Web/email audit tests не содержат `.conf`, QR payload, `vpn://`, raw token, private key или PSK.
5. Peer apply/revoke tests не содержат PSK/config block в command string, report, exception text, stdout/stderr summaries.
6. Hygiene/runtime tests запрещают checked-in secret artifacts и plain diagnostic capture.
7. Full test suite проходит после focused security/delivery/remote checks.

## Transfer gate

Перед любым следующим code edit в `amn2`, который добавляет secret-bearing output, нужно добавить строку в этот план или в machine-checkable inventory:

| Поле | Что фиксировать |
| --- | --- |
| `surface` | route, bot action, CLI command, agent endpoint, diagnostic script или background job |
| `actor` | web-admin, telegram-admin, telegram-user, public-token, scoped-token, local-agent или cli-operator |
| `secret_class` | из `secret-surface-inventory.md` |
| `raw_value_lifetime` | one-time display, runtime-only, encrypted-db, hash-only или external-ref |
| `redaction_rule` | existing pattern, new pattern или explicit no-text-output rule |
| `audit_policy` | metadata-only fields, forbidden raw fields, event id |
| `backup_policy` | exclude, redact, encrypted-full-only или metadata-only |
| `tests` | exact pytest files/functions that prove no leakage |

## Готовый implementation handoff

Подробный план реализации первого code slice подготовлен отдельно:

- [AMN2 Redaction Coverage First Slice Implementation Plan](../../docs/superpowers/plans/2026-05-31-amn2-redaction-coverage-first-slice.md)

## Следующие рабочие шаги

1. Решить, пушим ли ветку `codex/redaction-coverage-first-slice` в private `amn2` сейчас или оставляем локально до GitHub/PR-процесса.
2. Подготовить partial-failure/rollback contract для state-changing remote operations.
3. До live Docker apply/revoke отдельно описать Docker manager: persistent config path, backup, reload/apply semantics и rollback note.
