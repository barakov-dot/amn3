# `amn2`: Route/Auth Policy Matrix

## Паспорт

- Production repo: `C:\Users\SooL\Documents\Amneziya`
- Дата матрицы: 2026-05-31
- Режим: lab policy artifact, без изменений в `amn2`.
- Источники:
  - [Route/auth surface inventory](route-auth-surface-inventory.md)
  - [Secret surface inventory](secret-surface-inventory.md)
  - [Config delivery inventory](config-delivery-inventory.md)
  - [Remote operations inventory](remote-operations-inventory.md)
- Цель: превратить route/auth inventory в конкретную policy matrix для будущих изменений `amn2`, чтобы route guards, audit, redaction и tests не расходились между web, bot, public-token и будущими API surfaces.

## Решение

Статус: `route-policy-matrix-first-pass`.

Матрица является P0-gate для новых endpoint-ов и изменений существующих route handlers. Она не требует немедленного code edit в `amn2`, но любые следующие plans по `secret-read`, `public-token`, `remote-exec`, `backup/import`, `scoped tokens` и `Local Agent` должны ссылаться на нее.

2FA остается `paused`: эта матрица готовит почву для 2FA, но не запускает ее implementation plan.

## Actor model

| Actor | Auth source | Где используется | Ограничение |
| --- | --- | --- | --- |
| `web-admin` | web session после username/password | web-admin UI | configured actor, пока без granular web roles |
| `telegram-admin` | Telegram identity + `ADMIN_TELEGRAM_IDS` или `users.is_admin` | bot admin actions | отдельный trust channel, не равен web-admin автоматически |
| `telegram-user` | Telegram identity + DB user/device ownership | bot user actions | доступ только к owned resources |
| `public-token` | raw email/recovery token + stored hash lookup | `/email/verify`, `/email/recover` | purpose-bound, TTL, one-time |
| `cli-operator` | local shell access | CLI server/config operations | вне HTTP session, требует отдельного operational audit |
| `local-agent` | future local token/hash | Local Amnezia Agent | пока candidate, должен быть scoped и local-only |
| `scoped-token` | future bearer token hash + scopes | future integration API | не существует как production surface в текущем pass |

## Risk classes

| Risk class | Meaning | Minimum gates |
| --- | --- | --- |
| `auth-entry` | вход/выход из auth flow | CSRF для POST, rate limit, generic errors |
| `read-only` | чтение не-secret metadata | authenticated actor, ownership where relevant |
| `secret-adjacent-read` | чтение данных рядом с секретами | authenticated actor, redaction, no raw secret |
| `secret-read` | выдача артефакта, дающего доступ | strict actor gate, ownership/token gate, audit, redaction |
| `public-token-entry` | public форма с token context | generic errors, no raw token in logs |
| `public-token-state-write` | public token меняет state | TTL, one-time, purpose check, audit recommendation |
| `public-token-secret-read` | public token выдает secret | TTL, one-time, purpose, ownership binding, audit, rate limit |
| `state-write` | изменение локального состояния | authenticated actor, CSRF/confirmation where relevant, audit |
| `remote-read` | read-only remote command | authenticated actor, command allowlist, redacted output, audit |
| `remote-exec` | remote state mutation | operation contract, dry-run/plan, audit, rollback note |
| `destructive` | удаление/restore/clear/uninstall | explicit confirmation, preview/dry-run, audit before/after, recovery note |

## Default policy rules

- Все web-admin `POST` routes требуют CSRF.
- Все `secret-read` routes требуют audit без raw `.conf`, QR payload, `vpn://`, private key, PSK или raw token.
- Все public-token routes должны иметь `purpose`, TTL, one-time behavior, generic denial и no raw token in audit/logs.
- Все user-owned bot flows требуют ownership tests на чужой `device_id` или user resource.
- Любой `remote-exec` должен идти через отдельный operation contract, а не через ad hoc SSH string.
- Будущий bearer/scoped token без explicit scope не должен проходить ни один admin-equivalent route.
- Если route читает или отправляет `client-config-secret`, он автоматически получает class `secret-read`, даже если output выглядит как QR PNG или `vpn://`.

## Web policy matrix

| Policy id | Route / surface | Actor | Risk | Gates | Audit | Required tests |
| --- | --- | --- | --- | --- | --- | --- |
| `web.auth.login_form` | `GET /login` | public | `auth-entry` | redirect if authenticated, CSRF token generated | no | form renders, authenticated redirect |
| `web.auth.login_submit` | `POST /login` | public | `auth-entry` | CSRF, password hash check, secure session cookie | recommended | success, bad password denied, missing CSRF denied, generic error |
| `web.auth.logout` | `POST /logout` | `web-admin` | `auth-exit` | session + CSRF | recommended | session cleared, missing CSRF denied |
| `web.dashboard.view` | `GET /` | `web-admin` | `read-only` | session | no | anonymous redirect |
| `web.orders.list` | `GET /orders` | `web-admin` | `read-only` | session | no | anonymous redirect |
| `web.logs.view` | `GET /logs` | `web-admin` | `secret-adjacent-read` | session, redacted log tail | no | anonymous redirect, redaction assertions |
| `web.settings.view` | `GET /settings` | `web-admin` | `secret-adjacent-read` | session, redacted settings | no | anonymous redirect, secret values redacted |
| `web.config_templates.view` | `GET /config-templates` | `web-admin` | `secret-adjacent-read` | session, synthetic preview only | no | anonymous redirect, preview uses no real private/PSK |
| `web.users.list` | `GET /users` | `web-admin` | `read-only` | session | no | anonymous redirect |
| `web.users.create_form` | `GET /users/new` | `web-admin` | `read-only` | session, CSRF token generated | no | anonymous redirect |
| `web.users.create` | `POST /users/new` | `web-admin` | `state-write` | session + CSRF + validation | required | missing CSRF denied, audit `web_user_create`, no mutation on invalid |
| `web.users.detail` | `GET /users/{user_id}` | `web-admin` | `read-only` | session | no | anonymous redirect, not-found behavior |
| `web.users.edit_form` | `GET /users/{user_id}/edit` | `web-admin` | `read-only` | session, CSRF token generated | no | anonymous redirect |
| `web.users.update` | `POST /users/{user_id}/edit` | `web-admin` | `state-write` | session + CSRF + validation | required | missing CSRF denied, audit `web_user_update` |
| `web.users.block` | `POST /users/{user_id}/block` | `web-admin` | `state-write` | session + CSRF | required | missing CSRF denied, audit `web_user_block` |
| `web.users.delete` | `POST /users/{user_id}/delete` | `web-admin` | `state-write` | session + CSRF | required | missing CSRF denied, audit `web_user_delete`; future destructive confirmation review |
| `web.email.verify_start` | `POST /users/{user_id}/email/verify/start` | `web-admin` | `state-write` + `token-raw issue` | session + CSRF + verified target rules | required | raw token not in metadata, token hash stored, audit `web_email_verify_start` |
| `web.email.verify_form` | `GET /email/verify` | `public-token` | `public-token-entry` | form only, no admin session | no | token not leaked in rendered unsafe context |
| `web.email.verify_submit` | `POST /email/verify` | `public-token` | `public-token-state-write` | token hash lookup, purpose, TTL, one-time | recommended | expired/used/wrong purpose denied, generic errors, raw token not logged |
| `web.email.config_send` | `POST /users/{user_id}/devices/{device_id}/email-config` | `web-admin` | `secret-read` | session + CSRF + user/device match | required | audit `web_email_config_send`, no config/link in audit, wrong device denied |
| `web.email.recovery_start` | `POST /users/{user_id}/devices/{device_id}/email-recovery/start` | `web-admin` | `state-write` + `token-raw issue` | session + CSRF + verified email + user/device match | required | raw token not in metadata, token hash stored, audit `web_email_recovery_start` |
| `web.email.recover_form` | `GET /email/recover` | `public-token` | `public-token-entry` | email delivery enabled | no | disabled email behavior, generic form errors |
| `web.email.recover_submit` | `POST /email/recover` | `public-token` | `public-token-secret-read` | token hash lookup, purpose, TTL, one-time, user/device binding | required | expired/used/wrong purpose denied, no raw token/config/link in audit, rate-limit candidate |
| `web.servers.list` | `GET /servers` | `web-admin` | `read-only` | session | no | anonymous redirect |
| `web.servers.create_form` | `GET /servers/new` | `web-admin` | `read-only` | session, CSRF token generated | no | anonymous redirect |
| `web.servers.create` | `POST /servers/new` | `web-admin` | `state-write` | session + CSRF + validation | required | missing CSRF denied, audit `web_server_create` |
| `web.servers.detail` | `GET /servers/{server_id}` | `web-admin` | `read-only` | session | no | anonymous redirect |
| `web.servers.edit_form` | `GET /servers/{server_id}/edit` | `web-admin` | `read-only` | session, CSRF token generated | no | anonymous redirect |
| `web.servers.update` | `POST /servers/{server_id}/edit` | `web-admin` | `state-write` | session + CSRF + validation | required | missing CSRF denied, audit `web_server_update` |
| `web.servers.disable` | `POST /servers/{server_id}/disable` | `web-admin` | `state-write` | session + CSRF | required | missing CSRF denied, audit `web_server_disable`; future confirmation review |
| `web.servers.health_view` | `GET /servers/{server_id}/health` | `web-admin` | `read-only` | session | no | anonymous redirect |
| `web.servers.health_run` | `POST /servers/{server_id}/health/run` | `web-admin` | `remote-read` | session + CSRF + read-only command policy | required | missing CSRF denied, health stored, audit `web_server_health_run`, redacted errors |

## Telegram bot policy matrix

| Policy id | Surface | Actor | Risk | Gates | Audit | Required tests |
| --- | --- | --- | --- | --- | --- | --- |
| `bot.start` | `/start` | `telegram-user` / `telegram-admin` | `read-only` | Telegram identity, admin menu only if `is_admin()` | no | admin/user menu split |
| `bot.user.order_create` | user config request callbacks | `telegram-user` | `state-write` | Telegram user record, plan/config validation | recommended | creates expected order, invalid callback denied |
| `bot.user.state_read` | traffic/tariff/devices callbacks | `telegram-user` | `read-only` / `secret-adjacent-read` | Telegram user ownership | no | user sees own state only |
| `bot.user.config_resend` | user resend config callback | `telegram-user` | `secret-read` | ownership through `get_user_device()` | required | чужой device denied, `.conf`/QR/`vpn://` not logged |
| `bot.user.device_revoke` | user revoke callback | `telegram-user` | `state-write` / `remote-exec` when enabled | ownership, remote remove before local revoke | required | чужой device denied, remote failure leaves local state safe |
| `bot.user.devices_reset` | user reset callbacks | `telegram-user` | `state-write` / `remote-exec` when enabled | ownership over listed devices | required | partial remote failure plan needed before expansion |
| `bot.admin.pending_list` | admin pending callbacks | `telegram-admin` | `read-only` | `workflow.is_admin()` | no | non-admin rejected |
| `bot.admin.approve_order` | admin approve callback | `telegram-admin` | `state-write` / `remote-exec` when enabled | `workflow.is_admin()`, transaction, peer apply gate | required | non-admin rejected, apply failure rollback, no PSK in errors |
| `bot.admin.config_resend` | admin resend config callback | `telegram-admin` | `secret-read` | `workflow.is_admin()`, device lookup | required | non-admin rejected, no config/link in audit/logs |
| `bot.admin.grant` | `/admin_grant` | `telegram-admin` | `state-write` | `workflow.is_admin()` | required | non-admin rejected, audit/admin action |
| `bot.admin.user_create` | `/admin_add_user` | `telegram-admin` | `state-write` | `workflow.is_admin()` | required | non-admin rejected |
| `bot.admin.order_create` | `/admin_create_order` | `telegram-admin` | `state-write` | `workflow.is_admin()` | required | non-admin rejected |

## CLI/operator policy matrix

| Policy id | Surface | Actor | Risk | Gates | Audit | Required tests |
| --- | --- | --- | --- | --- | --- | --- |
| `cli.server.check_dry_run` | `server check --dry-run` | `cli-operator` | `read-only` preview | local shell, no remote execution | no | planned commands only |
| `cli.server.check_live` | `server check` | `cli-operator` | `remote-read` | read-only command allowlist | recommended | mutating command rejection, redacted errors |
| `cli.server.preflight` | `server preflight` | `cli-operator` | `state-write` local | config validation, fixed VPN port/server public key | recommended | local DB sync behavior, no secrets logged |
| `cli.server.collect_traffic` | `server collect-traffic` | `cli-operator` | `remote-read` + local state write | telemetry command policy, Docker blocked | recommended | command allowlist candidate, no sensitive stdout in errors |
| `cli.server.apply_peer_dry_run` | `server apply-peer --dry-run` | `cli-operator` | `remote-exec` preview | explicit dry-run | no | dry-run redacts PSK |
| `cli.server.apply_peer_live` | `server apply-peer --apply` | `cli-operator` | `remote-exec` | explicit apply, PSK via stdin, Docker blocked | recommended | no PSK in command string/stdout/stderr, failure behavior |
| `cli.server.revoke_peer_live` | `server revoke-peer --apply` | `cli-operator` | `remote-exec` | explicit apply, Docker blocked | recommended | command shape, failure behavior |

## Public-token policy

Public-token surfaces не являются admin-auth bypass. Их модель отдельная:

- token has one purpose;
- token raw value хранится только у пользователя;
- DB хранит только hash;
- token has TTL;
- token is one-time;
- denial errors are generic;
- audit/logs never include raw token;
- `public-token-secret-read` требует audit without config/link/QR payload.

Минимальные future tests:

- wrong purpose denied;
- expired token denied;
- used token denied;
- token for other device/user denied;
- raw token not present in audit metadata;
- raw token not present in application logs;
- config delivery output not present in audit metadata;
- rate-limit policy decided before public self-service expansion.

## Aggregate test gates для будущего `amn2`

Когда матрица станет machine-checkable в `amn2`, нужны aggregate tests:

- каждый registered web route имеет `policy_id`;
- каждый bot action/callback с state change или secret output имеет `policy_id`;
- каждый `secret-read` policy имеет `audit_required=true`;
- каждый `public-token-secret-read` имеет TTL, one-time и purpose check;
- каждый web `POST` admin route имеет CSRF gate;
- каждый `remote-read` route использует read-only command policy;
- каждый `remote-exec` route связан с operation contract;
- ни один future bearer/scoped-token route не разрешен без explicit scope;
- OpenAPI/docs grouping не противоречит `surface` в policy.

## Gaps

- Matrix пока текстовая, не machine-checkable.
- Login audit для success/failure не найден в первом route inventory; это не blocker для текущего web UI, но важно до 2FA/rate-limit work.
- Rate limit для password login, public token redeem и future scoped token API не найден.
- Web-admin и Telegram-admin остаются разными actor channels; объединять их нельзя без отдельного actor model design.
- CLI surfaces имеют local shell trust model; для web/API переноса им нужен `RemoteOperationRunner`.
- `CONTROL_PANEL_AUTH_METHODS` есть в settings, но runtime surface требует отдельной трассировки перед scoped-token work.

## Следующие шаги

1. Использовать эту матрицу как вход для implementation plan по route policy coverage tests.
2. До self-service/public share links добавить rate-limit и audit policy для `public-token-secret-read`.
3. До remote state-changing web/API routes продолжить `RemoteOperationRunner` read-only health slice.
4. До 2FA решить actor model: single configured web-admin или multi-operator accounts.
