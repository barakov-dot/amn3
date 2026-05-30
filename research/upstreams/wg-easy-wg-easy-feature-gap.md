# wg-easy/wg-easy: feature gap для `amn2` и гибридного проекта

## Паспорт

- Upstream: https://github.com/wg-easy/wg-easy
- Дата анализа: 2026-05-30
- Основа: first-pass upstream card и deep-dive по config delivery, auth/permissions/2FA, metrics, operational docs/migration.
- License verdict: AGPL-3.0-only, режим `research-only`.
- Production verdict для `amn2`: переносить только самостоятельно спроектированные идеи после проверки текущего `amn2`; код, schema, UI, routes, docs text и migration logic не копировать.

## Краткий вывод

`wg-easy` полезен для нас не как источник кода, а как эталон focused WireGuard UX и как проверка наших foundational specs. Он показывает, что даже “простая” WireGuard-панель быстро упирается в те же классы задач, которые мы уже выделили для `amn2`:

- config delivery как secret surface;
- user/client lifecycle;
- route policy and ownership checks;
- 2FA and account state;
- metrics with privacy policy;
- setup, migration and operational docs;
- firewall/host changes как high-risk operations.

Практический вывод: в `amn2` рано тащить большой feature pack. Правильный порядок - сначала inventory текущего `amn2`, затем маленький перенос foundational behavior: policy, secrets, delivery, tests. Для будущего гибридного проекта `wg-easy` остается high-signal reference по WireGuard-first product experience.

## Feature gap matrix

| Feature / signal | Что есть в wg-easy | Для `amn2` | Для гибридного проекта | Transfer gate |
| --- | --- | --- | --- | --- |
| WireGuard client lifecycle | clients, enable/disable, expiration, stats, config delivery | `candidate-for-review`: connection lifecycle model | `high-signal`: базовый protocol UX | открыть `amn2`, сверить текущий object model |
| Public-safe read models | list queries без private/pre-shared keys | `candidate-for-amn2`: DTO/read models + tests | `useful baseline` | Secret Inventory + response tests |
| Config download | authenticated `.conf` и QR endpoint | `candidate-for-amn2`: secret-read route class | `core delivery UX` | Public/Self-service Config Delivery spec |
| One-time links | public one-time config link | `idea-only`: перепроектировать token model | `useful UX` | crypto token, hash storage, expiry, revoke, audit |
| Client expiration | `expiresAt` and cron disable | `candidate-for-review`: bounded access | `strong product primitive` | policy for config download after expiry |
| Permission wrapper | wrapper требует resource check | `candidate-for-amn2`: enforced ownership check | `core auth pattern` | Route Policy Matrix + tests |
| Roles | `ADMIN` / `CLIENT` | `partial fit`: нужен support/integration/public/system | `starter model only` | role/actor model review |
| 2FA | account-level TOTP | `security candidate` | `account security baseline` | recovery/rate limit/audit/secret inventory |
| Basic Auth API | API password auth; 2FA users cannot use API | `rejected` | `rejected` | use Scoped API Tokens |
| Metrics | Prometheus/JSON peers, traffic, handshake | `candidate-after-policy`: aggregate first | `observability baseline` | `metrics:read` token + privacy labels |
| Metrics labels | client name/IP in labels | `rejected by default` | opt-in only | privacy review and retention policy |
| Per-client firewall | iptables/ip6tables rules | not near-term | `hybrid-only` advanced access control | RemoteOperationRunner, dry-run, recovery |
| Setup wizard | first-run setup and migration branch | `candidate`: hardened bootstrap | `useful install UX` | bootstrap token, secret cleanup |
| Migration import | v14 backup import | `idea-only`: needs safe import design | `high-signal onboarding` | preflight, redacted preview, rollback |
| Operational docs | install/setup/API/CLI/metrics/migration/update docs | `transfer gate`: docs with behavior | `product surface` | docs tests and versioned guides |
| CLI | password reset, clients list, QR display | `policy-needed`: CLI is not bypass | `operator tool` | CLI risk class and secret-output policy |

## Приоритет для `amn2`

### Сейчас полезно как ближайший design review

1. Public-safe read models for clients/connections.
2. Enforced resource/ownership check in route policy.
3. Config/QR/download as `secret-read`.
4. Disabled/expired connection access rules.
5. Metrics as scoped, privacy-reviewed read surface.
6. Operational docs as transfer gate.

Эти идеи не требуют копировать upstream. Они хорошо ложатся на уже созданные specs:

- [Route Policy Matrix](../../docs/superpowers/specs/2026-05-30-route-policy-matrix-design.md)
- [Secret Inventory + Backup Policy](../../docs/superpowers/specs/2026-05-30-secret-inventory-backup-policy-design.md)
- [Scoped API Tokens](../../docs/superpowers/specs/2026-05-30-scoped-api-tokens-design.md)
- [Public/Self-service Config Delivery](../../docs/superpowers/specs/2026-05-30-public-self-service-config-delivery-design.md)
- [RemoteOperationRunner](../../docs/superpowers/specs/2026-05-30-remote-operation-runner-design.md)

### После проверки текущего `amn2`

Эти идеи требуют открыть production repo и посмотреть фактическую архитектуру:

- connection lifecycle: owner, enabled, revoked, expires_at, config_version;
- current auth methods and route guards;
- config delivery paths;
- metrics/status endpoints;
- backup/import behavior;
- CLI or admin tooling;
- deployment docs.

Без этого они остаются research candidates, не backlog tasks.

### Не переносить в `amn2` сейчас

- AGPL-licensed implementation details.
- One-time link generation/storage model.
- Basic Auth as API auth.
- Metrics labels with client names/IPs by default.
- JSON metrics with client metadata as public/read-only endpoint.
- Per-client firewall changes without operation runner.
- Migration import without preflight/rollback.
- CLI QR/config output without secret-read policy.

## Приоритет для будущего гибридного проекта

`wg-easy` особенно полезен как WireGuard-first reference:

- single-protocol UX before multi-protocol complexity;
- client lifecycle as product primitive;
- config delivery formats: file, QR, one-time link;
- account security page;
- observability baseline;
- migration/import wizard;
- operational docs system.

Для гибридного проекта это не значит “скопировать wg-easy”. Это значит: сначала сделать один protocol UX действительно ясным, а уже потом расширять в multi-protocol platform.

## Что нужно проверить в текущем `amn2`

Перед переносом любой идеи открыть production repo и составить inventory:

| Area | Что проверить | Почему |
| --- | --- | --- |
| Connection model | есть ли owner, enabled, revoked, expiration, config version | понять, куда ложится lifecycle |
| Config delivery | все места выдачи config/QR/link/API | найти secret-read surfaces |
| Auth methods | session, token, CLI, public links, bot | исключить обход policy |
| Route guards | где role check, где ownership check | найти scattered checks |
| Secrets | private keys, pre-shared keys, tokens, TOTP, backups | построить secret inventory |
| Metrics/status | labels, endpoint auth, retention | не утечь metadata |
| Remote operations | install/restart/firewall/docker | привязать к operation runner |
| Docs | install/update/migration/API/CLI/recovery | сделать docs частью transfer gate |

## Вопросы для совместного разбора

Ты прав, тут уже пора остановиться и разобрать несколько вещей на человеческом языке. Я бы вынес в отдельный разговор такие вопросы:

1. Чем отличается `amn2` от будущего гибридного проекта?
   Нужно договориться, что `amn2` получает только компактные production-улучшения, а гибридный проект забирает широкие platform-идеи.

2. Что такое `secret-read` и почему config/QR/metrics не “просто чтение”?
   Это ключ к пониманию, почему мы так осторожно относимся к download, QR, public links, backup и logs.

3. Почему лицензия AGPL/GPL не мешает учиться, но мешает копировать?
   Важно отделить идею, UX-паттерн и test requirement от конкретного кода и структуры upstream.

4. Почему route policy matrix должна идти раньше новых функций?
   Без нее каждая новая фича добавляет свой маленький guard, и потом сложно доказать безопасность доступа.

5. Что нам реально нужно перенести в `amn2` первым?
   Моя текущая рекомендация: inventory текущего `amn2`, затем public-safe read models + config delivery policy + ownership tests.

6. Когда research достаточно и пора открывать `amn2`?
   По `wg-easy` уже достаточно для feature gap. Следующий большой шаг - смотреть фактический код `amn2`, иначе lab начнет повторяться.

## Предлагаемая повестка разговора

Если будем разбирать это вместе, я бы предложил 40 минут:

- 10 минут: карта `amn2` vs lab vs hybrid.
- 10 минут: почему config delivery, tokens, metrics и backup считаются security surface.
- 10 минут: что из `wg-easy` реально полезно, а что только для гибрида.
- 10 минут: решение, открываем ли текущий `amn2` для inventory и в каком порядке.

## Решение для lab

Статус feature gap: `completed-first-pass`.

`wg-easy` как upstream можно считать достаточно разобранным для первого цикла. Остались возможные узкие deep-dive темы, но они уже менее важны, чем проверка текущего `amn2`.

Рекомендация:

- следующий research artifact делать только если нужен конкретный вопрос;
- иначе перейти к `amn2` inventory;
- отдельно обсудить вопросы из блока выше, чтобы у тебя было ясное понимание, зачем эти gates нужны.

## Источники

- First-pass upstream card: [wg-easy-wg-easy.md](wg-easy-wg-easy.md)
- Config delivery deep-dive: [wg-easy-wg-easy-config-delivery.md](wg-easy-wg-easy-config-delivery.md)
- Auth/permissions/2FA deep-dive: [wg-easy-wg-easy-auth-permissions-2fa.md](wg-easy-wg-easy-auth-permissions-2fa.md)
- Metrics deep-dive: [wg-easy-wg-easy-metrics-surface.md](wg-easy-wg-easy-metrics-surface.md)
- Operational docs/migration deep-dive: [wg-easy-wg-easy-operational-docs-migration.md](wg-easy-wg-easy-operational-docs-migration.md)
- Repository: https://github.com/wg-easy/wg-easy
