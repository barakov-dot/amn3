# wg-easy/wg-easy

## Паспорт

- Репозиторий: https://github.com/wg-easy/wg-easy
- Дата первичного анализа: 2026-05-30
- Тип проекта: all-in-one WireGuard server + web-based admin UI.
- Основной стек: Nuxt 3, TypeScript, Vue, Tailwind CSS, Drizzle ORM, SQLite/libSQL, Docker, WireGuard.
- Лицензия: AGPL-3.0-only.
- Статус для `amn2`: только исследование идей, без копирования кода.
- Статус для будущего гибридного проекта: полезный upstream для WireGuard-first UX, config delivery, metrics и client lifecycle.

## Краткое описание

`wg-easy` - сфокусированная WireGuard-панель: один контейнер совмещает WireGuard и web UI для управления clients. В отличие от `PRVTPRO/Amnezia-Web-Panel`, проект не пытается быть multi-protocol orchestrator-ом; он показывает, как выглядит зрелая single-protocol панель с удобной выдачей конфигов.

README заявляет функции: создание, редактирование, удаление, enable/disable clients, QR code, скачивание client config, statistics, Tx/Rx charts, one-time links, client expiration, Prometheus metrics, IPv6, CIDR, 2FA и per-client firewall filtering.

Для `vpn-ops-lab` это хороший второй upstream: он независимо подтверждает важность `Public/Self-service Config Delivery`, `Secret Inventory`, `Route Policy Matrix`, metrics и bounded client lifecycle.

## Лицензия и ограничения

В README указано `AGPL-3.0-only`, а `LICENSE` содержит GNU Affero General Public License v3.

Вывод для `amn2`:

- код, schema, routes, UI, Docker setup, templates и command helpers не переносить;
- AGPL-3.0-only особенно чувствительна для network server software, поэтому прямой перенос в production-направление заблокирован без отдельного юридического решения;
- изучать можно только идеи, UX-паттерны, risk signals и test requirements;
- все потенциальные реализации для `amn2` должны быть самостоятельными.

Первичный license verdict: `research-only`.

## Архитектура и стек

Проект построен как Nuxt 3 application с server routes/API, TypeScript, Drizzle ORM и SQLite/libSQL storage. В `src/package.json` видны зависимости для Nuxt, i18n, Pinia, Tailwind, Drizzle, Zod, Argon2, OTPAuth, QR generation и charts.

Docker Compose запускает `ghcr.io/wg-easy/wg-easy:15`, монтирует `/etc/wireguard`, `/lib/modules:ro`, открывает UDP `51820` и TCP `51821`, добавляет capabilities `NET_ADMIN`, `SYS_MODULE` и включает forwarding sysctls. Это подтверждает, что даже single-protocol VPN UI требует careful host/network risk review.

В коде есть несколько полезных boundary-паттернов:

- `definePermissionEventHandler` получает текущего пользователя, проверяет permission и заставляет handler вызвать `checkPermissions`, если проверка требует resource data.
- `defineSetupEventHandler` ограничивает setup routes по текущему setup step.
- `defineMetricsHandler` включает Prometheus/JSON metrics только если они включены, а при наличии password требует bearer auth.
- Database service для clients имеет public-safe queries, где не возвращаются `privateKey` и `preSharedKey`.

## Функциональные сигналы

### Client lifecycle

Полезные функции:

- list/create/edit/delete client;
- enable/disable client;
- client expiration через `expiresAt`;
- per-client allowed IPs;
- per-client firewall filtering;
- QR code и config download;
- traffic stats and latest handshake;
- one-time config link.

Для `amn2` это подтверждает, что "connection" должен быть полноценным lifecycle object: status, owner, expiration, config version, revoke/disable и delivery history.

### Config delivery

Сильный сигнал: upstream имеет one-time links и route, который отдает `.conf` как attachment. Это совпадает с нашим spec [Public/Self-service Config Delivery](../../docs/superpowers/specs/2026-05-30-public-self-service-config-delivery-design.md).

Риск-сигнал: по просмотренным `oneTimeLink` schema/service/route:

- link value хранится как поле `oneTimeLink`;
- generation использует значение на основе client id, `Math.random()` и CRC32;
- expiry сохраняется в `expiresAt`;
- в download route явная проверка `expiresAt` не видна в просмотренном фрагменте;
- после успешной выдачи route вызывает erase.

Это не финальный security verdict без полного deep-dive, но для `amn2` уже достаточно решения: production one-time/share links должны использовать crypto-secure token, hash storage, mandatory expiry check, revoke, rate limit и audit.

### Auth, permissions и users

User schema содержит username, password, email, name, role, `totpKey`, `totpVerified`, enabled timestamps. Это подтверждает полезность:

- role/permission model;
- 2FA как отдельная production-идея;
- disabled user gate;
- route wrappers вместо scattered checks.

В `definePermissionEventHandler` интересен enforced resource check: если permission требует data, handler обязан вызвать `checkPermissions`, иначе wrapper возвращает server error. Для нашего `Route Policy Matrix` это хороший подтверждающий паттерн: policy должна проверять не только роль, но и ownership/resource data.

### Metrics

Prometheus route формирует метрики:

- configured peers;
- enabled peers;
- connected peers;
- sent/received bytes;
- latest handshake seconds.

Для `amn2` это хороший кандидат после route policy: read-only metrics surface с отдельной auth/rate policy и без секретов в labels.

Риск: metrics labels включают client name и IP addresses. Для production нужно решить, считаются ли эти labels sensitive metadata.

### Firewall

Per-client firewall filtering использует собственную chain `WG_CLIENTS`, iptables/ip6tables, parsing IP/CIDR/port/proto entries и sanitization comment. Полезная идея - per-client access restrictions как future/hybrid feature.

Для `amn2` это не ближайший перенос: firewall changes являются `remote-exec` или `destructive` risk class и должны идти только через `RemoteOperationRunner`-style plan, dry-run, audit и recovery note.

## Полезные идеи для `amn2`

- Focused WireGuard client lifecycle: owner, expiration, enabled flag, config delivery, stats.
- One-time config delivery как UX-идея, но только через наш более строгий spec: hashed token, expiry, revoke, audit.
- Public-safe client queries: read models, где private key/pre-shared key исключены по умолчанию.
- Permission wrapper, который требует resource-level permission check.
- Setup state machine для first-run/migration flows.
- Metrics surface для configured/enabled/connected peers и traffic, но с privacy review labels.
- 2FA как отдельный security candidate после базовой auth модели.

## Полезные идеи для будущего гибридного проекта

- WireGuard-first UX как эталон минимальной панели.
- Client expiration как product primitive для trial, temporary access и support workflows.
- Per-client firewall filtering как advanced access-control feature.
- Prometheus metrics как operator integration.
- Multi-language UI как зрелый product signal.
- Separate docs site and migration guide как operational maturity pattern.

## Что нельзя переносить как есть

- Любой код или schema из AGPL-3.0-only upstream.
- One-time link generation/storage model без собственного security redesign.
- Plaintext share/one-time token storage.
- Weak token generation through non-cryptographic randomness/checksum.
- Public config route без явной expiry validation, rate limit и audit.
- Docker/host network settings без отдельного deployment risk review.
- Metrics labels с user/client/IP metadata без privacy policy.
- Per-client firewall changes без dry-run/plan/audit.

## Повторяющиеся сигналы после двух upstreams

После `PRVTPRO/Amnezia-Web-Panel` и `wg-easy/wg-easy` повторились идеи:

- config delivery является core product surface;
- public/share/one-time links удобны, но являются secret-read risk;
- roles/permissions должны быть централизованы;
- token/scoped access нужен для integrations и metrics;
- backup/export не должен случайно включать client configs или token material;
- remote/host changes требуют отдельного risk gate;
- metrics/status полезны, но тоже требуют policy.

Это усиливает наши foundational specs и делает их не разовой реакцией на один upstream, а повторяющимся архитектурным выводом.

## Решение

Проект стоит держать в `research/upstreams` как сильный single-protocol reference, но не как источник кода.

Первичный статус:

- для `amn2`: `candidate ideas only`;
- для гибридного проекта: `high-signal WireGuard UX reference`;
- для копирования кода: `blocked by AGPL-3.0-only until separate legal decision`.

## Следующие шаги

- Сделать отдельный deep-dive по config delivery и one-time links.
- Сделать отдельный deep-dive по permissions/auth/2FA.
- Сравнить metrics surface с будущим `amn2` route policy.
- Проверить docs/migration guide как operational maturity pattern.

## Источники

- Репозиторий: https://github.com/wg-easy/wg-easy
- README: https://github.com/wg-easy/wg-easy/blob/master/README.md
- LICENSE: https://github.com/wg-easy/wg-easy/blob/master/LICENSE
- `docker-compose.yml`: https://github.com/wg-easy/wg-easy/blob/master/docker-compose.yml
- `src/package.json`: https://github.com/wg-easy/wg-easy/blob/master/src/package.json
- `handler.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/utils/handler.ts
- `client/schema.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/client/schema.ts
- `client/service.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/client/service.ts
- `oneTimeLink/schema.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/oneTimeLink/schema.ts
- `oneTimeLink/service.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/oneTimeLink/service.ts
- `cnf/[oneTimeLink].ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/routes/cnf/%5BoneTimeLink%5D.ts
- `prometheus.get.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/routes/metrics/prometheus.get.ts
- `firewall.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/utils/firewall.ts
