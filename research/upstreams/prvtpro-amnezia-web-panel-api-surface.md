# PRVTPRO/Amnezia-Web-Panel: API surface и route guards

## Паспорт deep-dive

- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
- Дата анализа: 2026-05-30
- Область: endpoint taxonomy, route guards, public surfaces, risky operations, API documentation.
- License verdict: GPL-3.0, режим `research-only`.
- Production verdict для `amn2`: переносить только самостоятельно спроектированные идеи и требования, не копировать код или route layout.

## Краткий вывод

API surface у upstream полезен как продуктовая карта: Authentication, Servers, Protocols, Connections, Users, Self-service, Sharing, Settings и API Tokens. Сильная идея - заранее группировать endpoints по доменам и явно отделять admin/support, user self-service и public sharing.

Главный риск - route guards не выглядят как единая policy matrix. Часть endpoints использует `_check_admin()` и принимает session cookie или bearer token для admin/support. Часть user-management endpoints проверяет только session user и роль `admin`. Public sharing имеет отдельный token/password flow. Для production-дизайна `amn2` сначала нужна явная таблица: endpoint, роль, auth method, side effects, audit, tests.

## Endpoint groups

README и `OPENAPI_TAGS` выделяют такие группы:

| Группа | Назначение | Первичный риск |
| --- | --- | --- |
| System Templates | HTML pages: login, server detail, settings, `/share` | смешение UI route и security boundary |
| Authentication | login, captcha, session lifecycle | brute force, default credentials, session secret |
| Servers | inventory, add/edit/delete, ping, reorder, reboot, clear, stats, check | SSH secrets, destructive host operations |
| Protocols | install/uninstall, container toggle, raw config editing | sudo, container lifecycle, config corruption |
| Connections | VPN client CRUD, enable/disable, config retrieval | выдача секретных config, user ownership |
| Users | panel users, assigned connections, share setup | role escalation, account lifecycle |
| Self-service | `/api/my/*` user-owned surface | доступ к чужим config |
| Sharing | public token-protected config sharing | leakage, no expiry, public secret surface |
| Settings | appearance, sync, captcha, telegram, SSL, backup/restore | secret storage, restore attacks |
| API Tokens | bearer token create/list/revoke | broad access, no scopes/expiry |

## Auth и role guards

Основные auth patterns:

- `get_current_user(request)` читает `user_id` из session cookie.
- `_check_admin(request)` сначала проверяет session user с ролью `admin` или `support`, затем пробует `Authorization: Bearer <token>`.
- Bearer token наследует статус владельца: если владелец отключен или потерял роль `admin/support`, token не проходит.
- Обычный user получает отдельные self-service endpoints и HTML page `/my`.
- Public share не требует panel session, но использует `share_token` и optional password.

Важное отличие:

- server/protocol/settings/token endpoints в основном используют `_check_admin()`;
- некоторые user endpoints вроде create/delete/toggle проверяют именно session user и роль `admin`;
- config endpoint для connections допускает session user и вручную проверяет ownership, если роль `user`.

Вывод: модель работает как набор локальных проверок, но для production лучше иметь централизованную route policy matrix.

## Public surfaces

Public/self-service surfaces:

- `/api/my/connections` - список своих connections для session user.
- `/api/my/connections/{connection_id}/config` - получение своего config.
- `/share/{token}` - HTML page для public sharing.
- `/api/share/{token}/auth` - password auth для share link.
- `/api/share/{token}/connections` - список shared connections.
- `/api/share/{token}/config/{connection_id}` - выдача config по public token.

Эти surfaces нельзя считать второстепенными: они выдают VPN-конфиги или metadata, поэтому для production им нужны отдельные ограничения:

- expiry;
- rate limiting;
- audit;
- revoke;
- ownership tests;
- no plaintext share token storage;
- clear UX для отключения ссылки.

## Risky operations

Особо рискованные API-действия:

- `/api/servers/add` и `/api/servers/{server_id}/edit` сохраняют SSH credentials в state.
- `/api/servers/{server_id}/delete` удаляет server entry и чистит связанные connections.
- `/api/servers/{server_id}/reboot` вызывает remote reboot через SSH.
- `/api/servers/{server_id}/clear` выполняет cleanup containers/images/network и удаляет `/opt/amnezia`.
- `/api/servers/{server_id}/install` запускает установку протоколов и сервисов.
- `/api/servers/{server_id}/uninstall` удаляет protocol container.
- `/api/servers/{server_id}/container/toggle` запускает или останавливает контейнер.
- `/api/servers/{server_id}/server_config/save` сохраняет raw server-side config.
- `/api/settings/backup/download` отдает `data.json`.
- `/api/settings/backup/restore` принимает state из uploaded JSON.
- `/api/settings/sync_delete` удаляет Remnawave-linked users.

Для `amn2` такие операции должны иметь отдельный класс риска. Минимальный production gate:

- explicit confirmation;
- dry-run, где возможно;
- audit event;
- role/scope check;
- input validation;
- rollback or recovery note;
- tests for denied access and wrong ownership;
- no secret leakage in error responses or logs.

## Что полезно для `amn2`

- Endpoint taxonomy до реализации: Authentication, Servers, Protocols, Connections, Users, Self-service, Sharing, Settings, API Tokens.
- Route policy matrix: endpoint, role, auth method, side effect, audit requirement, tests.
- Separate self-service API for regular users.
- Token-backed integration API, но только со scopes и expiry.
- Public sharing как отдельный security surface, не как обычный user endpoint.
- Risk classes для API operations: read-only, secret-read, state-write, remote-exec, destructive.
- API docs как проверяемый artifact: docs должны совпадать с route guards.

## Что полезно для будущего гибридного проекта

- Full operator API для multi-protocol управления.
- Public/user/admin surfaces как разные продуктовые зоны.
- API tokens для внешних интеграций, мониторинга и CI.
- Sharing endpoints как пользовательский delivery channel.
- Settings API для Telegram, sync, SSL и backup/restore.
- OpenAPI grouping как часть operator UX, а не только developer docs.

## Что нельзя переносить как есть

- Admin-equivalent bearer tokens без scopes, expiry и per-token audit.
- Public sharing без обязательного expiry и hashed token storage.
- Raw config editing без schema validation, backup-before-write и audit.
- Destructive endpoints без dry-run/confirmation/audit.
- Backup download полного `data.json` как обычный endpoint без redaction/encryption policy.
- Разнородные route guards без единой policy matrix.
- Error responses, которые могут возвращать слишком много внутренних деталей remote operation.

## Test-plan идеи для будущего production-дизайна

Минимальный набор тестов для похожего API в `amn2`:

- unauthenticated request получает 401/403 на всех non-public endpoints;
- `user` не может вызвать admin/support endpoints;
- `support` не может выполнять admin-only destructive actions, если policy так решит;
- bearer token без нужного scope не проходит;
- disabled/demoted owner invalidates token;
- user не может получить чужой connection config;
- share link не работает после expiry/revoke;
- share password не раскрывает, существует ли token;
- raw config save валидирует формат и не пишет invalid state;
- destructive endpoint создает audit event;
- backup download redacted по умолчанию;
- restore rejects incompatible state.

## Решение для lab

Статус deep-dive: `completed-first-pass`.

Следующий логичный слой анализа - manager/SSH/protocol architecture, потому что API surface показывает, какие remote operations рискованные, но не показывает, как именно они реализованы внутри manager-слоя.

## Источники

- Репозиторий: https://github.com/PRVTPRO/Amnezia-Web-Panel
- README: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/README.md
- `app.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/app.py
- Auth/secrets deep-dive: [prvtpro-amnezia-web-panel-auth-secrets.md](prvtpro-amnezia-web-panel-auth-secrets.md)
