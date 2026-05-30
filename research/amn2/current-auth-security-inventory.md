# `amn2`: auth/security inventory snapshot

## Паспорт

- Production repo: `C:\Users\SooL\Documents\Amneziya`
- Дата снимка: 2026-05-30
- Режим: read-only inventory, без изменений в `amn2`.
- Секреты: `.env` намеренно не читался.
- Цель: понять, что уже есть в `amn2` перед решением о 2FA, route policy, secret inventory, config delivery и token work.

## Проверенные файлы

- `app/web/auth.py`
- `app/web/app.py` - только auth/session/CSRF/admin-action фрагменты.
- `app/config/settings.py`
- `app/services/config_delivery.py`
- `app/db/schema.py`
- `app/db/repositories.py`
- `tests/web/test_auth.py`
- `tests/config/test_settings.py`
- `tests/security/test_redaction.py`
- `tests/backup/test_backup_service.py`

## Краткий вывод

`amn2` уже не пустой с точки зрения security foundation. В нем есть password hashing для web-admin, session auth, CSRF, настройки web-admin с обязательными секретами при включении, admin model через Telegram/user flags, audit table для admin actions, hashed email recovery tokens, encrypted device secrets, redaction tests и encrypted backup/restore checks.

Поэтому 2FA для админов выглядит правильным кандидатом, но не первым коммитом в production. Перед ней нужны две короткие карты:

1. route/auth surface inventory, чтобы 2FA не обходилась через другой auth method;
2. secret surface inventory, чтобы TOTP secret и backup codes сразу попали в redaction, backup, restore и audit policy.

## Что уже есть

| Область | Найдено | Значение для переноса идей |
| --- | --- | --- |
| Web-admin password | `create_password_hash`, `check_password`, `pbkdf2_sha256`, `hmac.compare_digest` | Есть базовый password layer, на который можно навесить второй фактор после проверки login flow. |
| Web-admin config gate | `WEB_ADMIN_ENABLED`, `WEB_ADMIN_PASSWORD_HASH`, `WEB_ADMIN_SESSION_SECRET`, `WEB_ADMIN_SESSION_COOKIE_SECURE` | При включенном web-admin уже требуется password hash и session secret. |
| Session auth | `SESSION_AUTH_KEY`, `web_admin_username`, `_is_authenticated()` | Сейчас full-auth состояние выглядит бинарным; для 2FA понадобится промежуточное состояние до TOTP. |
| CSRF | `generate_csrf_token`, `verify_csrf_token`, проверки в login/logout и POST routes | Хорошая основа, но route inventory должен подтвердить покрытие всех state-changing routes. |
| Admin actors | `ADMIN_TELEGRAM_IDS`, `users.is_admin`, `set_user_admin()` | Есть Telegram/admin модель, но web-admin сейчас выглядит как отдельный configured actor. |
| Control panel auth methods | `telegram_admin`, `password`, `key` в настройках | Нужно отдельно проверить runtime, чтобы 2FA не имела обхода через password/key flow. |
| Audit | `admin_actions`, `record_admin_action()`, web action metadata | Есть место для будущих событий enrollment/reset/failed login без записи секретов. |
| Email recovery tokens | `email_recovery_tokens.token_hash`, TTL, `used_at` | Есть хороший pattern: raw token показывается/отправляется, в БД хранится hash. |
| Generic API tokens | В первом проходе не найден отдельный production API-token layer | Scoped API Tokens пока остаются design candidate, не quick patch. |
| Device secrets | `SecretBox`, encrypted peer private key and preshared key | Config delivery уже работает с secret-read surface. |
| Redaction | tests закрывают web-admin secrets, SMTP, VPS password, control panel hash, custom tokens | Secret inventory можно развивать от уже существующих redaction tests. |
| Backup/restore | encrypted archive, excludes, schema checks, decryptability checks | Для новых secret fields нужно сразу добавить backup/restore expectations. |

## 2FA: применимость к `amn2`

| Поверхность | Рекомендация | Условия |
| --- | --- | --- |
| Web-admin login | Подходит как первый production-кандидат для 2FA | Сначала route/auth inventory, затем TOTP enrollment/login/recovery design. |
| Telegram admins | Не смешивать с первым 2FA шагом | Telegram уже отдельный канал идентичности; надо сначала описать actor model. |
| Control panel password/key | Проверить до реализации | Если это admin-equivalent access, 2FA не должна легко обходиться альтернативным методом. |
| Email recovery tokens | Оставить отдельным flow | Это не второй фактор, а recovery/config-delivery surface с собственными рисками. |
| Обычные пользователи | Позже или для гибридного продукта | Для `amn2` первым делом важнее защитить admin/operator доступ. |

## Минимальные design gates для 2FA

- Storage: encrypted TOTP secret или отдельная секретная таблица; backup codes хранить только как hashes.
- Enrollment: секрет считается активным только после успешной проверки первого кода.
- Login flow: после правильного пароля сессия получает только `pending_2fa`, а `web_admin_authenticated` ставится после TOTP.
- Recovery: backup codes, admin reset или documented local recovery; без “магического” обхода в UI.
- Rate limit: ограничение попыток password и TOTP, чтобы 2FA не стала brute-force endpoint.
- Audit: enrollment, disable, recovery, failed login и successful login без записи TOTP secret, raw code, QR URI или backup codes.
- Redaction: TOTP secret, otpauth URI и backup codes должны попадать под redaction tests.
- Backup/restore: full encrypted backup должен восстанавливать 2FA state; diagnostic/redacted export не должен раскрывать секреты.
- Tests: password-only denied when 2FA enabled, wrong TOTP denied, valid TOTP accepted, backup code one-time, reset audited, disabled admin loses effective access.

## Связка с lab specs

| Lab spec | Текущий сигнал в `amn2` | Следующий artifact |
| --- | --- | --- |
| Route Policy Matrix | Guards сейчас видны как `_is_authenticated()` плюс CSRF checks в routes | Первый проход создан: [Route/auth surface inventory](route-auth-surface-inventory.md). |
| Secret Inventory + Backup Policy | Redaction и encrypted backup уже есть, но inventory по всем secret fields еще нужен | Первый проход создан: [Secret surface inventory](secret-surface-inventory.md). |
| Scoped API Tokens | Есть hashed email recovery tokens, но не найден generic scoped token layer | Token/auth inventory после route matrix. |
| Public/Self-service Config Delivery | `build_device_config_delivery()` decrypts peer secrets and renders config | Config delivery inventory как `secret-read` surface. |
| RemoteOperationRunner | В этом снимке не разбирался | Отдельный remote operations inventory. |

## Следующие рабочие шаги

1. Решить actor model для web-admin 2FA: single configured admin или multi-operator accounts.
2. После actor decision решить: 2FA для web-admin становится `ready-for-implementation-plan` или требует redesign actor model.
3. Если 2FA подтверждается, писать отдельный implementation plan для `amn2`, а не править production-код из lab.

## Вопросы для совместного разбора

1. Подтверждаем ли, что `C:\Users\SooL\Documents\Amneziya` - актуальный `amn2`, относительно которого принимаем решения?
2. 2FA должна быть обязательной для включенного web-admin или сначала opt-in через настройку?
3. Нужен ли web-admin как один configured actor или пора думать о нескольких operator accounts?
4. Должен ли Telegram admin влиять на reset/enrollment web-admin 2FA или это отдельные каналы доверия?
5. Какой recovery flow приемлем для VPS-сценария без потери доступа администратора?
