# wg-easy/wg-easy: config delivery и one-time links

## Паспорт deep-dive

- Upstream: https://github.com/wg-easy/wg-easy
- Дата анализа: 2026-05-30
- Область: client config download, QR delivery, one-time links, public-safe client views, delivery risks.
- License verdict: AGPL-3.0-only, режим `research-only`.
- Production verdict для `amn2`: переносить только самостоятельно спроектированные требования и тесты, не копировать routes, schema, UI или token-flow.

## Краткий вывод

`wg-easy` подтверждает, что config delivery - центральная функция VPN-панели, а не второстепенный download. В проекте есть authenticated config download, QR SVG endpoint и public one-time link для скачивания `.conf`. Также есть public-safe client queries, где из list responses исключаются `privateKey` и `preSharedKey`.

Главный вывод для `amn2`: наша модель [Public/Self-service Config Delivery](../../docs/superpowers/specs/2026-05-30-public-self-service-config-delivery-design.md) нужна не "на потом", а как базовый safety layer. Любой config delivery surface должен считаться `secret-read`: ownership, expiry, revoke, hash token storage, rate limit, audit и backup redaction.

## Delivery surfaces

Просмотренные surfaces:

| Surface | Upstream file | Что делает | Первичный риск |
| --- | --- | --- | --- |
| Authenticated config download | `src/server/api/client/[clientId]/configuration.get.ts` | проверяет permission, генерирует config, отдает `.conf` attachment | secret-read response, ownership, audit |
| Authenticated QR endpoint | `src/server/api/client/[clientId]/qrcode.svg.get.ts` | проверяет permission, генерирует QR SVG из config | QR payload равен secret |
| One-time link generation | `src/server/api/client/[clientId]/generateOneTimeLink.post.ts` | проверяет update permission и создает one-time link | token entropy/storage, link lifecycle |
| Public one-time download | `src/server/routes/cnf/[oneTimeLink].ts` | по token отдает config attachment и затем erases link | public secret surface, expiry validation, rate limit |
| Client list public-safe views | `client/service.ts` | возвращает client rows без `privateKey` и `preSharedKey` | нужно не забыть другие secret fields |

## Authenticated config download

Authenticated download routes используют `definePermissionEventHandler('clients', 'view', ...)`. Handler:

- валидирует `clientId`;
- получает client из базы;
- вызывает `checkPermissions(client)`;
- генерирует WireGuard config через `WireGuard.getClientConfiguration`;
- отдает response как attachment.

Полезная идея:

- route-level permission wrapper плюс resource data check;
- config generation on demand;
- filename sanitization через отдельный helper;
- отдельный QR endpoint, который не хранит QR как постоянный artifact.

Что нужно для `amn2`:

- `RoutePolicy` class `secret-read`;
- `connection-owner` или explicit support/admin policy;
- audit event на config/QR download;
- no-cache headers для secret responses;
- redaction body из logs/errors;
- тесты denied ownership.

## One-time link model

В upstream есть отдельная таблица `one_time_links_table`:

- `id` совпадает с `client.id`;
- `one_time_link` хранится как unique text;
- `expires_at` хранится как обязательное поле;
- relation привязана к client.

Generation flow:

- endpoint требует `clients:update`;
- handler валидирует `clientId`;
- получает client и вызывает `checkPermissions(client)`;
- вызывает `Database.oneTimeLinks.generate(clientId)`.

Public download flow:

- public route валидирует path token;
- ищет one-time link по token;
- если link найден, получает client;
- генерирует config;
- вызывает erase для link;
- возвращает `.conf` attachment.

## Risk findings

Это first-pass security review, не полный аудит. Но для наших целей достаточно зафиксировать blockers:

| Finding | Почему важно для `amn2` |
| --- | --- |
| Link value хранится как обычное поле `oneTimeLink` | production share/one-time token должен храниться как hash |
| Generation использует `Math.random()` и CRC32-based value | production token должен быть crypto-secure и иметь достаточную entropy |
| В просмотренном public route не видна явная проверка `expiresAt` перед выдачей config | expiry должен проверяться server-side до secret response |
| Public route не проходит permission wrapper | это нормально для public link, но нужна отдельная `public-share-token` route policy |
| Audit events в просмотренном flow не видны | config download должен оставлять audit без raw config |
| Rate limiting в просмотренном public route не виден | public token endpoints требуют abuse controls |
| Link erase происходит после генерации config | нужно определить поведение при race/retry/failure |

Решение для `amn2`: не повторять link implementation, а использовать наш spec: crypto token, hash storage, mandatory expiry check, revoke, one-time semantics, rate limit, audit, no-cache, backup redaction.

## Public-safe client views

`ClientService` имеет public-safe queries:

- `findAllPublic`;
- `findByUserId`;
- filtered variants.

В них явно исключаются `privateKey` и `preSharedKey`.

Это сильный transferable pattern как идея: internal model и API/read model должны быть разными. Для `amn2` лучше не полагаться на "не вернуть лишнее случайно", а завести:

- secret inventory для client fields;
- response DTO/read model;
- tests that private/pre-shared keys never appear in list responses;
- redacted backup checks.

## Client expiration

Client schema содержит `expiresAt`. Это усиливает идею bounded access:

- temporary access;
- support-issued temporary config;
- trial или limited-time connection;
- cleanup expired clients.

Для `amn2` expiration должен отвечать на вопросы:

- disabled ли client после expiry;
- можно ли скачать config после expiry;
- что происходит с public links;
- есть ли audit event;
- нужно ли удалять server-side peer или только блокировать delivery.

## Сравнение с нашими specs

| Наш spec | Подтверждение от wg-easy | Что усилить |
| --- | --- | --- |
| Public/Self-service Config Delivery | one-time links, QR, config attachment | mandatory server-side expiry check, audit, one-time race behavior |
| Route Policy Matrix | permission wrapper + resource check | public route policy for `public-share-token` |
| Secret Inventory + Backup Policy | private/pre-shared keys excluded from public queries | ensure link token/hash/config payload excluded from backup |
| Scoped API Tokens | metrics bearer token pattern exists separately | avoid broad bearer token for config download |
| RemoteOperationRunner | firewall and WireGuard sync are host-changing operations | config delivery must not trigger hidden host changes |

## Что полезно для `amn2`

- Public-safe read models для clients/connections.
- Config delivery as `secret-read` route class.
- QR endpoint как отдельный response policy, а не stored asset.
- One-time link UX, но с production-grade token model.
- Client expiration как часть connection lifecycle.
- Permission wrapper с обязательным resource check.

## Что полезно для будущего гибридного проекта

- One-time setup flow для временной выдачи конфигов.
- Client expiration + firewall filtering как advanced policy package.
- Metrics and delivery history как operator visibility.
- Разные delivery formats: file, QR, URI/subscription.

## Что нельзя переносить как есть

- AGPL-licensed route/schema/UI implementation.
- Plaintext one-time token storage.
- Non-cryptographic one-time token generation.
- Public config route без явной server-side expiry validation.
- Config download без audit.
- Public token route без rate limiting.
- Direct exposure of QR/config body to logs, backup or diagnostics.

## Test-plan идеи для `amn2`

Минимальные тесты:

- user/admin/support access matches `RoutePolicy`;
- user cannot download another user's config;
- disabled user cannot download config;
- expired client cannot download config, если policy так решит;
- revoked connection cannot download config;
- one-time token raw value shown only once;
- one-time token stored only as hash;
- one-time token generated with cryptographic randomness;
- expired one-time token denied before config generation;
- used one-time token cannot be reused;
- concurrent requests cannot reuse one-time token twice;
- config download emits audit event;
- config response has no-cache headers;
- config response body is not logged;
- redacted backup does not contain configs or one-time token hashes.

## Решение для lab

Статус deep-dive: `completed-first-pass`.

Этот upstream усиливает приоритет `Public/Self-service Config Delivery` и `Secret Inventory + Backup Policy` для будущего `amn2` review. Перед переносом в production нужно открыть текущий `amn2` и составить inventory всех config delivery paths.

## Источники

- Репозиторий: https://github.com/wg-easy/wg-easy
- README: https://github.com/wg-easy/wg-easy/blob/master/README.md
- `configuration.get.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/api/client/%5BclientId%5D/configuration.get.ts
- `qrcode.svg.get.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/api/client/%5BclientId%5D/qrcode.svg.get.ts
- `generateOneTimeLink.post.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/api/client/%5BclientId%5D/generateOneTimeLink.post.ts
- `cnf/[oneTimeLink].ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/routes/cnf/%5BoneTimeLink%5D.ts
- `oneTimeLink/schema.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/oneTimeLink/schema.ts
- `oneTimeLink/service.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/oneTimeLink/service.ts
- `client/service.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/client/service.ts
- `client/schema.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/client/schema.ts
- `WireGuard.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/utils/WireGuard.ts
- First-pass upstream card: [wg-easy-wg-easy.md](wg-easy-wg-easy.md)
