# wg-easy/wg-easy: permissions, auth и 2FA

## Паспорт deep-dive

- Upstream: https://github.com/wg-easy/wg-easy
- Дата анализа: 2026-05-30
- Область: session auth, Basic Authorization fallback, RBAC, resource checks, setup gate, password hashing, TOTP/2FA.
- License verdict: AGPL-3.0-only, режим `research-only`.
- Production verdict для `amn2`: переносить только требования, risk signals и тестовые идеи; не копировать routes, schema, middleware, UI или permission code.

## Краткий вывод

`wg-easy` подтверждает, что даже в single-protocol WireGuard-панели auth нельзя считать маленькой деталью. В проекте есть browser session, first-run setup gate, роли `ADMIN` и `CLIENT`, enforced resource check в route wrapper, self-service account endpoints и TOTP 2FA.

Самая полезная идея для `amn2` - не сама RBAC-таблица upstream, а принцип: route wrapper должен заставлять handler выполнить ownership/resource check, если policy зависит от конкретного объекта. Это усиливает наш spec [Route Policy Matrix](../../docs/superpowers/specs/2026-05-30-route-policy-matrix-design.md).

Главный risk signal: в просмотренном `getCurrentUser` есть fallback на `Authorization: Basic`, который проверяет username/password и не проходит через TOTP-ветку login flow. Для `amn2` это нельзя переносить как production-модель. Если нужен non-browser access, он должен идти через [Scoped API Tokens](../../docs/superpowers/specs/2026-05-30-scoped-api-tokens-design.md), а не через Basic Auth с полными пользовательскими правами.

## Auth surfaces

| Surface | Upstream files | Что делает | Вывод для `amn2` |
| --- | --- | --- | --- |
| Browser session | `session.post.ts`, `session.get.ts`, `session.delete.ts`, `session.ts` | login создает session с `userId`, session get возвращает public user record, logout очищает session | нужен явный session policy: lifetime, secure cookie, rotation, revoke, audit |
| Basic Authorization fallback | `session.ts` | при отсутствии session читает `Authorization: Basic`, проверяет password и возвращает user | reject для full API; заменить scoped tokens |
| Permission wrapper | `handler.ts`, `permissions.ts` | получает current user, проверяет role/action, требует `checkPermissions` для data-dependent permissions | сильный transferable pattern как идея |
| Setup gate | `setup.ts`, `setup/2.post.ts`, `setup/4.post.ts` | до завершения setup ведет пользователя по setup steps; первый user получает admin role | полезно как forced first-run setup или bootstrap flow |
| Metrics bearer | `handler.ts` | отдельный metrics guard с bearer token, если metrics password задан | полезно только как signal; для `amn2` нужен scoped integration token |
| Account self-service | `me/*.post.ts`, `me.vue` | user обновляет profile/password/TOTP только для себя | self-service surface должен быть отдельной policy-группой |

## User model

User schema содержит:

- `username`;
- `password`;
- `email`;
- `name`;
- `role`;
- `totpKey`;
- `totpVerified`;
- `enabled`;
- timestamps.

Пароли хэшируются через Argon2. В validation schema password имеет минимум 12 символов. Session signing password хранится в `general_table.session_password`, а initial migration создает его через SQLite `hex(randomblob(256))`.

Полезный вывод для `amn2`:

- account state должен участвовать во всех auth methods;
- disabled user должен терять effective access и через session, и через token;
- session secret должен быть persistent production secret, а не случайный runtime default;
- password policy, lockout/rate limiting и audit нужно описывать отдельно, не оставлять в handlers.

## Permission model

В `shared/utils/permissions.ts` есть две роли:

- `ADMIN`;
- `CLIENT`.

Ресурсы и действия:

- `clients`: `view`, `create`, `update`, `delete`, `custom`;
- `admin`: `any`;
- `me`: `update`.

Сильный паттерн:

- `definePermissionEventHandler` вызывает `getCurrentUser`;
- строит permission object через `hasPermissionsWithData`;
- boolean permission проверяется wrapper-ом сразу;
- data-dependent permission должна быть проверена handler-ом через `checkPermissions(data)`;
- если handler не вызвал `checkPermissions`, wrapper возвращает server error.

Это хороший architectural signal для `amn2`: route guard должен доказывать, что ownership/resource check был выполнен, а не полагаться на дисциплину автора endpoint-а.

Ограничения модели upstream:

- роли очень грубые: нет `support`, `auditor`, `integration`, `public`;
- action `custom` слишком общий и требует ручной дисциплины внутри handler-а;
- нет stable policy id для audit/tests;
- permission matrix не описывает risk class endpoint-а: read-only, secret-read, state-write, remote-exec;
- Basic Authorization получает те же user permissions, что session, без отдельного scope model.

## Resource ownership

Для client routes используется resource data:

- admin получает доступ ко всем clients;
- client может видеть, обновлять и удалять clients, где `user.id === client.userId`;
- client create запрещен;
- client list route использует `custom`, а handler сам разделяет admin list и user-owned list.

Полезный вывод:

- ownership check нужен не только на detail/update/delete, но и на list/filter endpoints;
- list endpoint не должен использовать coarse action без отдельного test plan;
- missing resource и forbidden ownership должны иметь предсказуемое поведение и тесты.

## TOTP/2FA model

2FA реализован через TOTP:

- account page запускает setup;
- `me/totp.post.ts` создает secret и возвращает `key` + `otpauth` URI;
- UI генерирует QR из URI;
- user вводит код, backend валидирует TOTP и ставит `totpVerified: true`;
- login без TOTP-кода возвращает статус `TOTP_REQUIRED`;
- неверный код возвращает `INVALID_TOTP_CODE`;
- отключение TOTP требует current password;
- TOTP параметры в просмотренном коде: SHA1, 6 digits, 30 seconds, validation window 1.

Что полезно для `amn2`:

- 2FA должен быть account-level security primitive, а не UI-only feature;
- disable 2FA должен требовать re-authentication;
- login response может явно разделять `password ok, TOTP required` от `invalid credentials`, но надо проверить enumeration risks;
- TOTP secret является secret material и должен входить в secret inventory.

Что нельзя переносить как есть:

- TOTP как защита только browser login, если другие auth methods могут обходить ее;
- TOTP key в обычном state без отдельной secret/backup policy;
- 2FA без recovery codes или documented recovery flow;
- 2FA/login без rate limit, lockout и audit;
- Basic Auth fallback для API при включенной TOTP.

## Basic Authorization risk

В `getCurrentUser` просмотренный flow:

- если session содержит `userId`, user берется из session;
- иначе, если есть `Authorization`, код ожидает `Basic`;
- декодирует username/password;
- проверяет password hash;
- возвращает user, если user enabled.

В этой ветке не видно TOTP-проверки. Это означает, что account с включенной TOTP может иметь browser login с TOTP, но API request с Basic credentials потенциально пройдет только по password. Это не окончательный audit всего upstream, но для `amn2` вывод достаточно жесткий: Basic Auth не должен быть full API auth method.

Production-альтернатива:

- browser users используют session + 2FA;
- integrations используют scoped tokens;
- token scopes не могут превышать current owner permissions;
- sensitive scopes требуют audit и expiry;
- disabled/demoted owner обнуляет effective token access.

## Setup и bootstrap

Upstream имеет setup state machine:

- middleware ведет пользователя в `/setup/<step>`, пока setup не завершен;
- `setup/2.post.ts` создает user через `Database.users.create`;
- первый user получает `ADMIN`, последующие users получают `CLIENT`;
- initial env может создать пользователя и завершить setup, если заданы username, password, host и port.

Для `amn2` полезна идея forced setup/bootstrap, но production-модель должна заранее ответить:

- как создается первый admin;
- есть ли one-time bootstrap token;
- как bootstrap закрывается после первого use;
- как headless install не превращается в long-lived default secret;
- что попадает в audit и setup diagnostics.

## Сравнение с нашими specs

| Наш spec | Подтверждение от wg-easy | Что усилить |
| --- | --- | --- |
| Route Policy Matrix | permission wrapper + resource check | stable policy id, risk class, audit, support/integration/public actors |
| Scoped API Tokens | Basic fallback показывает потребность в non-browser auth | запрет full-access Basic Auth; scoped token вместо password auth |
| Secret Inventory + Backup Policy | password hash, TOTP key, session password, metrics password | TOTP secret и session secret добавить как classified secrets |
| Public/Self-service Config Delivery | user-owned client permissions | ownership tests на config/QR/link endpoints |
| RemoteOperationRunner | admin routes могут restart/save WireGuard config | admin route risk class должен отличать state-write от remote-exec |

## Что полезно для `amn2`

- Enforced resource check в route wrapper.
- Явная role/action matrix как исходный материал для `RoutePolicy`.
- User-owned client access как self-service boundary.
- `enabled` gate для пользователя.
- TOTP как account-level candidate.
- Forced setup/bootstrap flow без default credentials.
- Persistent session signing secret.

## Что полезно для будущего гибридного проекта

- Минимальная RBAC-модель как стартовая точка, но с расширением на `support`, `integration`, `public` и `system`.
- Account security page: profile, password, TOTP.
- Setup wizard, который закрывает bootstrap после initial configuration.
- Separate docs page for 2FA как часть operator maturity.

## Что нельзя переносить как есть

- AGPL-licensed auth, permission, route, schema или UI code.
- Basic Auth как full API fallback.
- Любой auth method, который обходит TOTP для account с включенной 2FA.
- Coarse `custom` action без policy id, tests и audit expectations.
- TOTP secret storage без backup/secret policy.
- Login/TOTP flow без rate limit, lockout, audit и recovery flow.
- Admin-equivalent integration access без scopes и expiry.

## Test-plan идеи для `amn2`

Минимальные tests перед production-переносом похожих идей:

- user без session/token не может читать non-public endpoint;
- disabled user denied через session;
- disabled owner invalidates scoped token effective access;
- account с включенной TOTP не может получить session без valid TOTP;
- account с включенной TOTP не получает API bypass через password-only auth;
- user не может читать, менять, удалять чужую connection;
- list endpoint возвращает только user-owned resources;
- admin может читать all resources, но secret-read все равно audit-required;
- route с data-dependent policy падает в тесте, если handler не вызвал ownership check;
- every route has stable policy id, risk class and auth method record;
- TOTP setup secret не попадает в logs/errors/backup;
- TOTP disable требует current password или stronger re-auth;
- login and TOTP failures rate-limited;
- bootstrap token или setup state нельзя использовать после completion;
- session secret rotation/revoke behavior documented and tested.

## Решение для lab

Статус deep-dive: `completed-first-pass`.

Для `amn2` переносить в ближайший design review:

- `RoutePolicy` wrapper должен уметь принуждать resource check;
- Basic Auth full API fallback должен попасть в rejected production patterns;
- TOTP можно держать как security candidate, но только после общей auth method matrix;
- disabled user gate и owner inheritance нужны для session и token access.

Перед реальным переносом в production надо открыть текущий `amn2` и составить inventory всех auth methods, route guards, user states и secret-bearing account fields.

## Источники

- Репозиторий: https://github.com/wg-easy/wg-easy
- README: https://github.com/wg-easy/wg-easy/blob/master/README.md
- `session.post.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/api/session.post.ts
- `session.get.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/api/session.get.ts
- `session.delete.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/api/session.delete.ts
- `session.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/utils/session.ts
- `handler.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/utils/handler.ts
- `permissions.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/shared/utils/permissions.ts
- `user/schema.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/user/schema.ts
- `user/service.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/user/service.ts
- `user/types.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/user/types.ts
- `password.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/utils/password.ts
- `me/totp.post.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/api/me/totp.post.ts
- `me/password.post.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/api/me/password.post.ts
- `me/index.post.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/api/me/index.post.ts
- `auth.global.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/app/middleware/auth.global.ts
- `login.vue`: https://github.com/wg-easy/wg-easy/blob/master/src/app/pages/login.vue
- `me.vue`: https://github.com/wg-easy/wg-easy/blob/master/src/app/pages/me.vue
- 2FA guide: https://github.com/wg-easy/wg-easy/blob/master/docs/content/guides/2fa.md
- `setup.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/middleware/setup.ts
- `setup/2.post.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/api/setup/2.post.ts
- `general/schema.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/general/schema.ts
- `general/service.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/general/service.ts
- First-pass upstream card: [wg-easy-wg-easy.md](wg-easy-wg-easy.md)
