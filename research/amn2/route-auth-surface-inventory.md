# `amn2`: route/auth surface inventory

## Паспорт

- Production repo: `C:\Users\SooL\Documents\Amneziya`
- Дата снимка: 2026-05-30
- Режим: read-only inventory, без изменений в `amn2`.
- Секреты: `.env` намеренно не читался.
- Цель: зафиксировать текущую auth surface перед решением о 2FA, route policy matrix и scoped tokens.

## Текущее решение

2026-05-30: 2FA для web-admin поставлена на паузу. Этот route inventory нужен для будущей route policy и security review, но сейчас не запускает 2FA implementation plan.

## Краткий вывод

Основная HTTP-поверхность сейчас сосредоточена в `app/web/app.py`. Почти все admin/read/write web routes используют ручную проверку `_is_authenticated()`, а state-changing admin routes дополнительно проверяют CSRF через `verify_csrf_token()`.

Отдельно существуют public email token endpoints: `/email/verify` и `/email/recover`. Они не используют web-admin session и должны считаться отдельной public-token surface. Это не делает их плохими, но для 2FA и token policy важно не смешивать их с admin-login flow.

Telegram bot surface живет отдельно в `app/bot/main.py` и `app/bot/workflows.py`: admin actions проверяются через `workflow.is_admin()`, который учитывает `ADMIN_TELEGRAM_IDS` и `users.is_admin`.

## HTTP routes

| Route | Auth сейчас | CSRF | Risk class | Audit / state |
| --- | --- | --- | --- | --- |
| `GET /login` | public, redirect if authenticated | form token generated | `auth-entry` | no audit observed |
| `POST /login` | public username/password | yes | `auth-entry` | sets `web_admin_authenticated`; no login audit observed |
| `GET /` | web-admin session | not needed | `read-only` | dashboard counts |
| `GET /orders` | web-admin session | not needed | `read-only` | order listing |
| `GET /logs` | web-admin session | not needed | `secret-adjacent-read` | uses redacted log tail |
| `GET /settings` | web-admin session | not needed | `secret-adjacent-read` | displays redacted settings |
| `GET /config-templates` | web-admin session | not needed | `secret-adjacent-read` | renders safe config previews |
| `GET /users` | web-admin session | not needed | `read-only` | user listing |
| `GET /users/new` | web-admin session | form token generated | `read-only` | create form |
| `POST /users/new` | web-admin session | yes | `state-write` | `web_user_create` |
| `GET /users/{user_id}` | web-admin session | not needed | `read-only` | user detail |
| `POST /users/{user_id}/email/verify/start` | web-admin session | yes | `state-write` + token issue | `web_email_verify_start` |
| `GET /email/verify` | public token form | no admin session | `public-token-entry` | no state |
| `POST /email/verify` | public raw token, stored hash lookup | no | `public-token-state-write` | marks email verified and token used |
| `POST /users/{user_id}/devices/{device_id}/email-config` | web-admin session | yes | `secret-read` | `web_email_config_send` |
| `POST /users/{user_id}/devices/{device_id}/email-recovery/start` | web-admin session | yes | `state-write` + token issue | `web_email_recovery_start` |
| `GET /email/recover` | public token form when email delivery enabled | no admin session | `public-token-entry` | no state |
| `POST /email/recover` | public raw token, stored hash lookup | no | `public-token-secret-read` | sends config email and marks token used |
| `GET /users/{user_id}/edit` | web-admin session | form token generated | `read-only` | edit form |
| `POST /users/{user_id}/edit` | web-admin session | yes | `state-write` | `web_user_update` |
| `POST /users/{user_id}/block` | web-admin session | yes | `state-write` | `web_user_block` |
| `POST /users/{user_id}/delete` | web-admin session | yes | `state-write` | `web_user_delete` |
| `GET /servers` | web-admin session | not needed | `read-only` | server listing |
| `GET /servers/new` | web-admin session | form token generated | `read-only` | create form |
| `POST /servers/new` | web-admin session | yes | `state-write` | `web_server_create` |
| `GET /servers/{server_id}` | web-admin session | not needed | `read-only` | server detail |
| `GET /servers/{server_id}/edit` | web-admin session | form token generated | `read-only` | edit form |
| `POST /servers/{server_id}/edit` | web-admin session | yes | `state-write` | `web_server_update` |
| `POST /servers/{server_id}/disable` | web-admin session | yes | `state-write` | `web_server_disable` |
| `GET /servers/{server_id}/health` | web-admin session | not needed | `read-only` | health listing |
| `POST /servers/{server_id}/health/run` | web-admin session | yes | `remote-read` | `web_server_health_run`, stores health summary |
| `POST /logout` | session CSRF token | yes | `auth-exit` | clears session |

## Telegram bot surface

| Surface | Auth сейчас | Risk class | Notes |
| --- | --- | --- | --- |
| `/start` | Telegram identity; admin entry depends on `is_admin()` | `read-only` | Main menu differs for admin/user. |
| User config request callbacks | Telegram identity | `state-write` | Creates access/order flow. |
| User traffic/tariff/devices callbacks | Telegram identity | `read-only` / `secret-adjacent-read` | Reads user-owned state. |
| User resend config callback | Telegram identity + ownership in workflow | `secret-read` | Tests cover owned device resend. |
| User revoke/reset callbacks | Telegram identity + ownership in workflow | `state-write` / `remote-exec` when peer removal applies | Tests cover owned revoke/reset and peer remove failures. |
| Admin pending/users/templates callbacks | `workflow.is_admin()` | `read-only` / `state-write` | Tests cover non-admin rejection. |
| Admin approve callback | `workflow.is_admin()` | `state-write` / `remote-exec` when peer apply enabled | Tests cover non-admin rejection and apply failure. |
| Admin resend config callback | `workflow.is_admin()` | `secret-read` | Sends config delivery to user. |
| `/admin_grant` | `workflow.is_admin()` | `state-write` | Delegates admin role by Telegram id. |
| `/admin_add_user` | `workflow.is_admin()` | `state-write` | Creates manual user. |
| `/admin_create_order` | `workflow.is_admin()` | `state-write` | Creates manual access request. |

## Existing test signals

- `tests/web/test_app.py`: login success/failure, missing CSRF, logout, session cookie flags, invalid web-admin config.
- `tests/web/test_users.py`: unauthenticated redirect, create/edit/block/delete, audit, invalid CSRF no mutation.
- `tests/web/test_servers.py`: unauthenticated redirect, create/edit/disable/health run, audit, invalid CSRF no mutation.
- `tests/web/test_email_delivery.py`: hashed email tokens, one-time verify/recovery, no token in metadata, email disabled behavior.
- `tests/web/test_logs_settings_orders.py`: unauthenticated redirects, log/settings redaction.
- `tests/web/test_config_templates.py`: unauthenticated redirect and safe preview.
- `tests/bot/test_bot_handlers.py`: admin handlers reject non-admin and user flows call expected workflow methods.
- `tests/bot/test_bot_workflows.py`: DB-backed admin role, non-admin rejection, owned config resend/revoke/reset.

## Gaps before 2FA or scoped tokens

- Нет единой route policy matrix рядом с routes; guards сейчас manual per handler.
- Не найден login audit для success/failure в первом проходе.
- Не найден rate limit для password, public token redeem или будущего TOTP endpoint.
- Public email token endpoints являются отдельной auth surface и должны попасть в route policy с risk class `public-token-state-write` и `public-token-secret-read`.
- Web-admin сейчас выглядит как один configured actor; granular web roles не найдены.
- `CONTROL_PANEL_AUTH_METHODS` присутствует в settings, но runtime-поверхность этого механизма надо трассировать отдельно.
- Bot admin и web-admin используют разные identity channels; перед 2FA нужно решить, считаем ли их одним actor model или двумя независимыми trust channels.

## Решение для lab

Статус: `route-inventory-first-pass`.

2FA для web-admin остается возможным будущим кандидатом, но сейчас имеет статус `paused`. Если позже вернем ее в работу, implementation plan должен опираться на эту матрицу:

- password-only login становится `pending_2fa`, если 2FA включена;
- public email token endpoints не становятся обходом web-admin 2FA, потому что у них другой purpose и другой risk class;
- admin-equivalent routes после `pending_2fa` должны оставаться недоступны до полного подтверждения;
- тесты должны проверять не только `/`, но и state-changing routes, secret-read routes и logout.

## Следующие рабочие шаги

1. Сверить этот route inventory с [Secret surface inventory](secret-surface-inventory.md).
2. Использовать route inventory для Route Policy Matrix, config delivery и remote operations review.
3. Вернуться к 2FA только после отдельного решения о необходимости этой доработки.
