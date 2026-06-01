# `amn2`: secret surface inventory

## Паспорт

- Production repo: `C:\Users\SooL\Documents\Amneziya`
- Дата снимка: 2026-05-30
- Режим: read-only inventory, без изменений в `amn2`.
- Секреты: `.env` намеренно не читался.
- Цель: понять, какие secret-bearing surfaces уже есть, и что нужно учесть перед web-admin 2FA, scoped tokens и config delivery changes.

## Обновление 2026-05-31: P0 secret inventory expansion

Этот файл повышен из справочного снимка по 2FA до P0-карты секретов для переноса идей из lab в `amn2`.

Главный принцип: любое изменение, которое читает, создает, экспортирует, отправляет, восстанавливает или логирует secret-bearing данные, должно сначала пройти эту карту. Это относится не только к 2FA, но и к config delivery, public/self-service links, backup/import, scoped tokens, Local Agent, SSH/VPS operations, metrics и audit.

Рабочий статус после обновления: `implemented-pushed-local-gate-complete` для первого machine-checkable registry.

Implementation evidence:

```text
branch: amn2/codex/secret-inventory-registry
commit: 9ce42f4 Add secret inventory registry
evidence: research/amn2/secret-inventory-registry-implementation.md
focused: 64 passed
full: 591 passed, 1 warning
```

Ближайшее применение:

- route/auth policy matrix для `secret-read`, `state-write`, `remote-exec` и `public-token-secret-read` surfaces;
- redaction test plan для `.conf`, QR, `vpn://`, tokens, command output и diagnostics;
- backup/import policy, где redacted backup остается default, а full backup считается dangerous explicit mode;
- public/self-service config delivery policy, где share tokens hash-only, TTL/one-time/revoke обязательны, а public route остается заблокирован до no-secret audit/rate-limit tests;
- Local Agent hardening, где agent token, operation payload и runtime outputs не должны попадать в logs/audit plain text.

## Текущее решение

2026-05-30: 2FA для web-admin поставлена на паузу. Требования по TOTP storage/redaction/backup остаются справочными, но не запускают implementation plan.

## Краткий вывод

В `amn2` уже есть сильная база для secret handling:

- `SecretBox` шифрует peer private key и preshared key через Fernet key, derived from `APP_SECRET_KEY`.
- Email verification/recovery tokens хранятся как SHA-256 hash, raw token используется только для отправки пользователю.
- Redaction закрывает config blocks, Telegram bot token URLs, settings с `PASSWORD`, `TOKEN`, `SECRET`, `PRIVATE_KEY`, `PrivateKey` и `PresharedKey`.
- Backup архивируется как encrypted `.tar.enc`, включает SQLite database и manifest, но исключает app secret, Telegram token, QR files и plain configs.
- Restore валидирует schema, checksum, device rows и decryptability encrypted device secrets до записи target database.

Если позже вернемся к web-admin 2FA, этот фундамент полезен, но TOTP нельзя добавлять как обычное поле без расширения secret inventory: TOTP secret должен быть encrypted, backup codes должны быть hashed, provisioning URI и raw backup codes не должны попадать в logs, email, audit metadata, backup manifest text или diagnostics.

## Secret classes

### Рабочая классификация P0

| Class | Что означает | Примеры в `amn2` | Backup default | Audit/log default |
| --- | --- | --- | --- | --- |
| `credential-secret` | Дает доступ к внешнему сервису или панели | `TELEGRAM_BOT_TOKEN`, SMTP password, VPS password, будущие external API keys | exclude/redact | redact |
| `password-hash` | Hash, который нельзя раскрывать как metadata | `WEB_ADMIN_PASSWORD_HASH`, `CONTROL_PANEL_PASSWORD_HASH` | redact by default | redact |
| `session-secret` | Материал подписи или проверки session/token | `WEB_ADMIN_SESSION_SECRET`, `APP_SECRET_KEY` | exclude | redact |
| `private-key` | Приватный ключ или материал peer/server доступа | peer private key, SSH private key, TLS/private key candidates | encrypted-full-only или exclude | redact |
| `preshared-key` | VPN peer PSK или аналог | peer preshared key | encrypted-full-only или exclude | redact |
| `client-config-secret` | Артефакт, который дает VPN-доступ | raw `.conf`, QR payload/PNG, `vpn://` import link | exclude unless explicit encrypted full | redact; audit read only by metadata |
| `token-raw` | Raw token, показывается или отправляется один раз | email verify/recovery token, future API/share token raw value | never store/never backup | never log |
| `token-hash` | Hash token-а, usable for validation | email recovery token hash, future scoped token/share token hash | redact by default | metadata only |
| `remote-command-secret` | Секрет, передаваемый remote operation | peer PSK stdin, future sudo password/token refs | never include in command string | redact command output |
| `secret-adjacent` | Не секрет сам по себе, но раскрывает sensitive context | client IP, endpoint, traffic/handshake metadata, server host, token prefix | include only after privacy review | aggregate or pseudonymous preferred |
| `audit-safe-metadata` | Безопасная metadata без secret value | actor id, event type, resource id, risk class | include | include |

Если поле попадает сразу в несколько классов, выбирается самый строгий класс.

### Обязательная запись для новых secret-bearing полей

Каждый новый secret-bearing элемент должен получить запись:

```text
field_path:
owner_domain:
secret_class:
source: generated | user-provided | imported | external
storage_policy: env-only | encrypted-db | hash-only | runtime-only | external-ref
read_policy: admin-only | owner-only | scoped-token | public-token | internal-only
backup_policy: exclude | redact | encrypted-full-only | metadata-only
restore_policy: never-restore | restore-disabled | restore-with-rotation | restore-as-is
redaction_label:
rotation_or_revoke:
tests_required:
```

Без такой записи изменение должно считаться неготовым к переносу в `amn2`.

| Secret / surface | Где найдено | Storage сейчас | Exposure surface | Current controls |
| --- | --- | --- | --- | --- |
| `APP_SECRET_KEY` | settings/env, backup storage, `SecretBox` | env only | process env, backup encryption key | required non-blank, weak secret rejection in `SecretBox`, redaction tests |
| `TELEGRAM_BOT_TOKEN` | settings/env, bot startup | env only | Telegram API URL/log risk | required non-blank, redaction tests, backup excludes |
| `TELEGRAM_PROXY_URL` | settings/env, bot proxy session | env only | may contain proxy credentials | redaction tests |
| `VPS_SSH_PASSWORD` | settings/env | env only | remote SSH auth, logs | redaction tests; live password SSH backend not enabled in first pass |
| `CONTROL_PANEL_PASSWORD_HASH` | settings/env | env only | auth config | redaction tests |
| `WEB_ADMIN_PASSWORD_HASH` | settings/env | env only | web admin auth | required when enabled, hash validation in `app/web/auth.py`, redaction tests |
| `WEB_ADMIN_SESSION_SECRET` | settings/env | env only | session signing | required when enabled, length check, secure cookie default, redaction tests |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | settings/env, email sender | env only | SMTP auth | redaction tests |
| Peer private key | `devices.peer_private_key_encrypted` | encrypted DB field | config rendering, QR, import link, email attachment | `SecretBox`, backup decryptability checks, config redaction |
| Peer preshared key | `devices.preshared_key_encrypted` | encrypted DB field | config rendering, remote peer apply, QR, import link | `SecretBox`, stdin for remote apply, redaction in errors/reports |
| Email verification token | `email_recovery_tokens.token_hash` | hashed DB field | raw token sent by email | TTL, `used_at`, one-time tests, raw token not in metadata |
| Config recovery token | `email_recovery_tokens.token_hash` | hashed DB field | raw token sent by email | TTL, `used_at`, one-time tests, raw token not in URL |
| VPN config text | generated runtime | not stored as plain config in checked files | email attachment, QR PNG, `vpn://` import link | config block redaction, backup excludes plain configs and QR files |
| Remote peer apply PSK | `app/server/peer_apply.py` runtime input | stdin to SSH command | remote command errors/logs | command avoids raw PSK, stdout/stderr redaction tests |

## P0 secret surfaces для ближайших решений

| Surface | Класс | Что уже видно | Что нельзя делать | Обязательные тесты перед переносом |
| --- | --- | --- | --- | --- |
| `.conf` attachment | `client-config-secret` | генерируется runtime из encrypted device secrets | писать в audit/logs, сохранять как plain diagnostics, отдавать без gate | UTF-8 bytes, ownership/token denial, redaction, no logs |
| QR payload / QR PNG | `client-config-secret` | QR строится из raw config | считать картинкой без секрета, складывать в backup plain | payload round-trip, non-ASCII, no diagnostics leakage |
| `vpn://` import link | `client-config-secret` | reversibly encodes полный config | считать безопасным из-за отсутствия literal `PrivateKey` | decode round-trip, no raw link in audit/logs |
| Email recovery raw token | `token-raw` | отправляется пользователю, hash хранится в DB | писать raw token в URL logs/audit metadata | one-time, TTL, generic errors, no raw token in metadata |
| Email recovery token hash | `token-hash` | используется для проверки token | включать в redacted backup как обычное поле | backup redaction, restore-disabled или explicit policy |
| Peer private key | `private-key` | encrypted DB field | показывать в list/detail/read-model endpoints | decrypt only in delivery/apply path, backup decryptability |
| Peer preshared key | `preshared-key` | encrypted DB field, PSK stdin для remote apply | передавать через command arg или shell history | no command string leakage, stdout/stderr redaction |
| Web-admin session secret | `session-secret` | env-only | включать в backup или settings output | required length, redaction |
| Telegram bot token | `credential-secret` | env-only | попадание в logs, diagnostics, backup | URL token redaction, backup exclude |
| VPS SSH password/private key | `credential-secret` / `private-key` | env/settings/runtime candidates | shell command string, process list, diagnostic bundle | no command arg leakage, redaction, host key policy; enrollment design prepared in `ssh-host-key-enrollment-design.md` |
| Local Agent token/hash | `credential-secret` / `token-hash` | design/branch candidate | хранить raw token после enrollment | hash-only storage, rotation, audit without raw token |
| Metrics labels | `secret-adjacent` | future candidate | раскрывать client names/IP/activity по умолчанию | aggregate default, scoped token, privacy class tests |

## Transfer checklist для secret-bearing изменений

Перед code edit в `amn2` по любой secret-bearing функции нужно ответить:

1. Какой actor получает доступ: web-admin, Telegram admin, Telegram user, public token, scoped token, local agent или CLI operator?
2. Какой risk class: `secret-read`, `state-write`, `remote-exec`, `destructive`, `public-token-secret-read`?
3. Где секрет хранится: env-only, encrypted DB, hash-only, runtime-only или external-ref?
4. Может ли секрет попасть в logs, audit, diagnostics, backup, error response, OpenAPI example или test fixture?
5. Как revoke/rotation работает после утечки?
6. Что происходит при restore: secret исчезает, восстанавливается disabled, требует rotation или восстанавливается как есть?
7. Какие negative tests доказывают, что чужой actor не получает secret?
8. Какие redaction tests доказывают, что raw secret не попадает в строки ошибок и diagnostic output?
9. Есть ли recovery note для оператора, если secret restore/import/remote apply частично не сработал?

## Backup and restore model

Update 2026-06-01: dangerous API boundary for future web/API backup/import is prepared in `backup-import-dangerous-api-design.md`. Current CLI encrypted backup remains an operator recovery baseline; it is not a permission slip for ordinary backup/import endpoints.

| Area | Current behavior | 2FA impact |
| --- | --- | --- |
| Archive content | database + manifest | TOTP state in DB would be included in encrypted full backup. |
| Archive encryption | encrypted with key derived from `APP_SECRET_KEY` | TOTP restore would depend on same `APP_SECRET_KEY`, same as peer secrets. |
| Excludes | `app_secret_key`, `telegram_bot_token`, `qr_files`, `plain_configs` | Add TOTP provisioning URI and raw backup codes to explicit diagnostics/export excludes if such exports appear. |
| Restore validation | checksum, required tables/columns, active device fields, encrypted peer secret decryptability | Add decryptability/shape validation for encrypted TOTP secret if stored in DB. |
| Failure behavior | target DB is not written before validation succeeds | Keep this property for new secret-bearing columns. |

## Redaction model

Current `app/security/redaction.py` covers:

- full `[Interface] ... [Peer]` config blocks;
- Telegram bot API URL token fragments;
- key/value names containing `PASSWORD_HASH`, `PASSWORD`, `TOKEN`, `SECRET`, `PRIVATE_KEY`;
- `TELEGRAM_PROXY_URL`, `SMTP_USERNAME`, `external_payment_id`;
- explicit `PrivateKey` and `PresharedKey` lines.

For 2FA, redaction should be expanded before or with implementation:

- `TOTP_SECRET`;
- `MFA_SECRET`;
- `OTP_SECRET`;
- `OTPAUTH_URI`;
- `BACKUP_CODE`;
- `RECOVERY_CODE`, if reused outside email recovery tokens;
- QR/provisioning payloads that contain `otpauth://`.

## TOTP/2FA storage implication

TOTP verification needs the original secret, so the TOTP secret cannot be stored as a simple hash. It should be encrypted with the same secret-handling discipline as peer private keys, or placed in a dedicated encrypted admin secret table.

Backup codes are different: they are one-time passwords and should be stored as hashes, following the email token pattern.

Recommended split:

| 2FA data | Storage | Display rule | Backup rule |
| --- | --- | --- | --- |
| TOTP secret | encrypted DB field | provisioning URI shown once during enrollment | included only in encrypted full backup |
| TOTP provisioning URI / QR | generated runtime | shown once, never persisted as plain text | excluded from diagnostics/plain export |
| Backup codes | hashed DB rows | shown once during generation | hashes can be in DB backup; raw codes never stored |
| 2FA enabled flag | DB/config depending on actor model | visible in admin settings | safe to backup |
| Failed attempts/lockout | DB/runtime state | no raw code | safe with retention policy |

## Decision point for web-admin 2FA

There are two possible models:

| Model | Fit now | Tradeoff |
| --- | --- | --- |
| Single configured web-admin 2FA | Fits current `WEB_ADMIN_USERNAME` model | Faster, but keeps web-admin separate from DB users. |
| Multi-operator account 2FA | Fits future role model better | Requires actor model redesign before implementation. |

For `amn2`, conservative first step is single configured web-admin 2FA, but only if we explicitly accept that web-admin remains a separate configured actor for now.

## Required tests before production implementation

- Redaction removes `TOTP_SECRET`, `OTPAUTH_URI`, backup codes and TOTP QR payload text.
- Encrypted TOTP secret can be decrypted with current `APP_SECRET_KEY` and fails safely with the wrong key.
- Backup restore rejects malformed encrypted TOTP secret before writing target DB.
- Backup codes are stored as hashes and are one-time.
- Logs/audit metadata never include raw TOTP code, TOTP secret, otpauth URI or raw backup codes.
- Diagnostic/settings pages do not display TOTP secret or provisioning URI.
- Existing email recovery tokens remain separate from 2FA recovery codes.

## Gaps

- Первый machine-checkable secret inventory добавлен в `amn2/codex/secret-inventory-registry`, commit `9ce42f4`; будущие поля все еще должны расширять registry и tests.
- Backup manifest excludes are fixed; adding new artifact types should update manifest and tests.
- Config delivery уже признан `client-config-secret`, но audit/logging/read-model policy пока не оформлена как route-level matrix.
- `vpn://` link теперь тестируется как reversible UTF-8 artifact в первом срезе, но QR decode round-trip без новой dependency еще не закрыт.
- Для Local Agent token/hash нужна связь с этим inventory: raw token one-time display, hash-only storage, rotation, no audit raw value.
- Для scoped API/share tokens нужна restore policy: redacted backup не должен оживлять usable tokens.
- Для metrics labels нужна privacy classification до появления detailed Prometheus/JSON surfaces.
- Redaction pattern does not explicitly name TOTP/MFA/otpauth terms yet.
- No current DB schema for web-admin 2FA secrets.
- No rate limit / lockout storage found in this pass.
- No actor model decision for single web-admin versus multiple operators.

## Решение для lab

Статус: `secret-inventory-p0-expanded`.

Этот inventory теперь является P0-gate для secret-bearing изменений в `amn2`. Он не означает автоматическую реализацию backup/import, 2FA, scoped tokens или public links; он задает обязательную проверку перед такими изменениями.

2FA для web-admin сейчас не переводится к code edit. Если позже снимаем паузу, перед implementation plan нужно зафиксировать:

- actor model: single configured web-admin or multi-operator;
- recovery model: backup codes and local reset path;
- storage model: encrypted TOTP secret and hashed backup codes;
- redaction/backup tests as part of first implementation batch.

## Следующие рабочие шаги

1. Подготовить `Route/Auth policy matrix` для текущих web/API/bot surfaces, опираясь на классы `secret-read`, `public-token-secret-read`, `remote-exec` и `destructive`.
2. Добавить отдельный design/plan для redaction coverage: `.conf`, QR payload, `vpn://`, token raw/hash, Local Agent token, command stdout/stderr и diagnostics.
3. Использовать `backup-import-dangerous-api-design.md` как вход для backup/import policy: metadata export/redacted backup default, encrypted full backup только explicit dangerous mode, restore/import только через preview и audit.
4. Не писать `amn2` implementation plan для 2FA, пока статус `paused`.
5. Если пауза снимается, сначала обсудить actor model и recovery model.
