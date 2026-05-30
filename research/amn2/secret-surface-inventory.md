# `amn2`: secret surface inventory

## Паспорт

- Production repo: `C:\Users\SooL\Documents\Amneziya`
- Дата снимка: 2026-05-30
- Режим: read-only inventory, без изменений в `amn2`.
- Секреты: `.env` намеренно не читался.
- Цель: понять, какие secret-bearing surfaces уже есть, и что нужно учесть перед web-admin 2FA, scoped tokens и config delivery changes.

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

## Backup and restore model

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

- Нет explicit secret inventory table in code/docs; this lab file is the first map.
- Backup manifest excludes are fixed; adding new artifact types should update manifest and tests.
- Redaction pattern does not explicitly name TOTP/MFA/otpauth terms yet.
- No current DB schema for web-admin 2FA secrets.
- No rate limit / lockout storage found in this pass.
- No actor model decision for single web-admin versus multiple operators.

## Решение для lab

Статус: `secret-inventory-first-pass`.

2FA для web-admin сейчас не переводится к code edit. Если позже снимаем паузу, перед implementation plan нужно зафиксировать:

- actor model: single configured web-admin or multi-operator;
- recovery model: backup codes and local reset path;
- storage model: encrypted TOTP secret and hashed backup codes;
- redaction/backup tests as part of first implementation batch.

## Следующие рабочие шаги

1. Использовать этот inventory для config delivery, backup/restore и redaction review.
2. Не писать `amn2` implementation plan для 2FA, пока статус `paused`.
3. Если пауза снимается, сначала обсудить actor model и recovery model.
