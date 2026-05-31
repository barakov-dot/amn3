# Public/Self-service Config Delivery для `amn2`: design spec

## Назначение

`Public/Self-service Config Delivery` - кандидатный design artifact для `amn2`, который описывает безопасную модель выдачи VPN-конфигов пользователям через личный кабинет, API, public links и будущие delivery channels.

Spec возник из анализа `PRVTPRO/Amnezia-Web-Panel`, но не переносит upstream routes, token model, UI или код. Upstream имеет license verdict `GPL-3.0`, поэтому для `amn2` допустима только самостоятельная реализация идеи после отдельного review в репозитории `amn2`.

Цель design spec: сделать выдачу VPN-конфигов удобной, но не превращать self-service и public links в неконтролируемые secret leaks.

## Контекст и проблема

VPN config, subscription link, QR-код или client profile почти всегда являются секретом: кто получил config, часто может подключиться к VPN.

Удобные delivery flows нужны:

- пользователь сам скачивает свой config;
- support выдает config без доступа к лишним admin-функциям;
- временная public link помогает подключить устройство без входа в панель;
- automation получает config через scoped API;
- будущие каналы вроде Telegram отправляют config пользователю.

Но без отдельной модели быстро появляются проблемы:

- public link живет бессрочно;
- share token хранится в plaintext;
- user может скачать чужой config;
- link password есть, но expiry/revoke нет;
- выдача config не попадает в audit;
- backup содержит share tokens или generated configs;
- support случайно получает secret-read доступ без явного policy.

Config delivery должен считаться `secret-read` surface, а не обычным file download.

## Scope

Входит в scope:

- self-service config access;
- public share links;
- ownership rules;
- share token model;
- expiry, revoke и optional one-time mode;
- delivery package model;
- response secret policy;
- audit events;
- rate limiting;
- связь с `Route Policy Matrix`, `Scoped API Tokens` и `Secret Inventory + Backup Policy`;
- test strategy.

Не входит в scope этого spec:

- конкретный UI личного кабинета;
- Telegram bot implementation;
- mobile app pairing protocol;
- формат конкретного VPN-протокола;
- генерация ключей;
- billing/subscription lifecycle;
- копирование upstream templates или routes.

## Основные принципы

1. VPN config delivery всегда считается `secret-read`.
2. User видит только свои assigned connections.
3. Public link ограничен конкретным набором ресурсов.
4. Public token хранится только как hash.
5. Public link имеет expiry по умолчанию.
6. Revoke должен немедленно отключать дальнейшую выдачу.
7. Config download создает audit event.
8. Response не должен содержать больше secret material, чем требуется конкретному формату.
9. Backup по умолчанию не содержит usable share tokens или generated configs.
10. Delivery channel не должен обходить `Route Policy Matrix`.

## Delivery surfaces

Минимальные surfaces:

| Surface | Actor | Auth method | Risk | Назначение |
| --- | --- | --- | --- | --- |
| Self-service web/API | `user` | `user-session` | `secret-read` | пользователь получает свои configs |
| Admin/operator issue | `admin` или ограниченный `support` | `session` | `secret-read` | оператор выдает config или создает share |
| Public share link | `public` | `public-share-token` | `secret-read` | временная выдача без входа в панель |
| Integration API | `integration` | `bearer-token` | `secret-read` | automation получает config по scope |
| Future bot delivery | `user` или `system` | channel-bound auth | `secret-read` | отправка config в внешний канал |

Каждый surface должен иметь отдельную route policy. Нельзя использовать один admin endpoint и просто менять поведение по optional token.

## Resource model

Config delivery должен работать с явной моделью:

```text
ConnectionResource
  connection_id
  user_id
  server_id
  protocol
  display_name
  status
  config_version
  revoked_at
```

```text
ConfigDeliveryPackage
  package_id
  connection_id
  protocol
  format: file | qr | uri | subscription
  generated_at
  expires_at
  secret_class: client-config-secret
  response_policy: secret-download | one-time-secret | redacted-preview
```

Config package может генерироваться on-demand. Если он сохраняется, он должен быть включен в `Secret Inventory` как `client-config-secret`.

## Artifact integrity model

После PRVTPRO config delivery deep-dive важно разделять не только surfaces, но и конкретные delivery artifacts. Один и тот же VPN config может быть выдан как raw `.conf`, файл для скачивания, QR payload, `vpn://` import URI или future subscription URI. Все эти формы являются `secret-read`, но проверяются по-разному.

```text
ConfigDeliveryArtifact
  artifact_id
  package_id
  connection_id
  artifact_type: conf_text | conf_file | qr_payload | qr_image | import_uri | subscription_uri
  target_client: amnezia_android | amnezia_desktop | wireguard_android | wireguard_desktop | generic
  content_encoding: utf-8 | binary | base64-uri
  contains_secret: true
  generated_at
  expires_at
  redaction_policy
```

Rules:

- `.conf` text and `.conf` file must be byte-equivalent after UTF-8 encoding.
- QR payload must be explicitly defined: raw config text, import URI or another protocol-specific payload.
- QR image is not a harmless image; it is a secret-bearing rendering of `qr_payload`.
- `vpn://` is secret-bearing because it reversibly encodes the full config.
- Artifact generation must be deterministic enough for tests to compare payloads, even if image pixels vary by QR library.
- UI and API responses should not silently switch QR payload type by protocol without exposing this in the artifact metadata.

## Ownership rules

Self-service:

- actor `user` может видеть только connections, назначенные этому user;
- disabled user не получает configs;
- disabled/revoked connection не выдается;
- user не может выбирать arbitrary `user_id`;
- user не может скачать config по id, если connection не назначен ему.

Public share:

- share link привязан к конкретному owner/user или конкретному списку connection ids;
- public token не дает enumerate всех connections;
- public token не раскрывает, существует ли другой connection id;
- share password, если есть, не заменяет expiry и revoke;
- share link не дает access к admin metadata.

Operator:

- support access к configs должен быть отдельным policy decision;
- admin/support downloads тоже audit-required;
- operator не должен видеть private material без причины, если можно выдать пользователю ссылку.

## Share token model

Public share token:

```text
ShareTokenRecord
  id
  owner_user_id
  token_hash
  token_prefix
  bound_connection_ids
  created_by
  created_at
  expires_at
  revoked_at
  revoked_by
  max_downloads
  download_count
  password_hash
  one_time
  last_used_at
```

Не хранить:

- raw share token;
- plaintext password;
- generated config content в share record;
- Authorization-like headers;
- full user agent, если это не нужно и не прошло privacy review.

По умолчанию:

- expiry обязателен;
- password optional, но не вместо expiry;
- max downloads optional;
- one-time mode полезен для high-risk delivery;
- token prefix можно показывать в UI/audit, но он не должен быть достаточен для доступа.

## Expiry, revoke и rotation

Rules:

- public share link без expiry не создается;
- default expiry должен быть коротким, например часы или дни, а не месяцы;
- revoke прекращает доступ сразу;
- revoke не удаляет audit history;
- connection revoke делает все связанные share links unusable;
- user disable делает его self-service и public shares unusable;
- regenerate config должен invalidates старые delivery packages, если protocol это поддерживает;
- rotation private keys или client credentials должна иметь отдельный audit event.

Если protocol не поддерживает немедленный revoke, UI/API должен честно показать limitation и recovery note.

## Response secret policy

Delivery responses делятся:

| Policy | Поведение |
| --- | --- |
| `redacted-preview` | metadata без config secret |
| `secret-download` | config file/URI/QR выдается пользователю |
| `one-time-secret` | config показывается один раз, повторный доступ заблокирован |
| `delivery-started` | внешний канал получил задание, raw config в response нет |

Любой response с `secret-download` или `one-time-secret`:

- audit-required;
- no-cache headers;
- rate limited;
- не логирует body;
- не попадает в generic error traces;
- не включается в backup/export.

## Route Policy Matrix integration

Пример policy ids:

| Policy id | Surface | Auth | Risk | Ownership | Audit |
| --- | --- | --- | --- | --- | --- |
| `self.connections.list` | self-service | user-session | read-only | user-self | optional |
| `self.connection.config_download` | self-service | user-session | secret-read | connection-owner | required |
| `share.config_download` | public-share | public-share-token | secret-read | public-link-bound | required |
| `admin.share.create` | admin-api | session | state-write | user-target | required |
| `admin.share.revoke` | admin-api | session | state-write | user-target | required |
| `integration.config_download` | integration | bearer-token | secret-read | scoped resource | required |

Required scopes для bearer token:

- `connections:read` для metadata;
- `configs:read` для config download;
- дополнительные resource filters, если token ограничен конкретным user/server/project.

## Secret Inventory integration

Классы:

- generated VPN config: `client-config-secret`;
- share token hash: `token-hash`;
- share password hash: `password-hash`;
- QR code payload: `client-config-secret`;
- subscription URI: `client-config-secret`;
- delivery audit metadata: `audit-metadata`.

Backup policy:

- redacted backup не содержит usable configs;
- redacted backup не содержит share token hashes;
- redacted backup может содержать share metadata как disabled records;
- restore redacted backup не оживляет public links;
- encrypted full backup может восстановить share records только через explicit dangerous mode.

## Manager export contract

Config delivery не должен зависеть от того, что каждый protocol manager случайно реализовал совместимую сигнатуру `get_client_config`. Для `amn2` нужен единый export contract, который скрывает protocol-specific детали за нормализованным результатом.

```text
ManagerConfigExportResult
  protocol
  connection_id
  config_text
  import_uri
  supported_artifacts
  target_clients
  warnings
  unavailable_reason
```

Требования:

- каждый manager явно объявляет capability `export_config` или причину отсутствия;
- manager не возвращает raw traceback в user-facing response;
- если private key отсутствует и config нельзя восстановить, результат должен быть typed warning/error, а не runtime exception в UI;
- self-service, public share и admin UI используют один export contract;
- contract tests запускаются для каждого manager-а и каждого поддержанного artifact type.

## Audit model

Audit events:

```text
ConfigDeliveryAuditEvent
  event_type
  actor
  route_policy_id
  connection_id
  user_id
  share_token_id
  delivery_surface
  response_policy
  decision: allowed | denied
  denial_reason
  request_id
  ip_hash
  created_at
```

Event types:

- `config.self.downloaded`;
- `config.public.downloaded`;
- `config.integration.downloaded`;
- `share.created`;
- `share.revoked`;
- `share.expired_denied`;
- `share.password_failed`;
- `config.denied_wrong_owner`;
- `config.denied_revoked_connection`.

Audit не содержит raw config, share token, password, URI, QR payload или private key.

## Rate limiting и abuse controls

Нужны лимиты:

- public share token attempts by IP/prefix;
- share password failures;
- self-service config downloads per user;
- integration config downloads per token;
- admin share creation per target user;
- repeated denied ownership attempts.

Denial responses для public share не должны раскрывать, существует ли token, user или connection.

## UX requirements

Даже если UI не входит в scope, design должен требовать:

- ясный срок жизни public link;
- видимая кнопка revoke;
- предупреждение, что config дает доступ к VPN;
- список активных shares у admin/user;
- last used metadata без раскрытия secret;
- отдельное состояние "connection revoked";
- понятное сообщение, если config нужно regenerated.

Для operator-а полезнее показать "share link expires in ..." и "downloaded N times", чем raw internals.

## Test strategy

Минимальные тесты:

- user sees only own connections;
- user cannot download another user's config;
- disabled user cannot download config;
- revoked connection cannot be downloaded;
- public share token stored as hash only;
- raw share token shown only once;
- public share without expiry rejected;
- expired public share denied;
- revoked public share denied;
- public share cannot access unbound connection;
- wrong share password denied without revealing token existence;
- config download emits audit event;
- config response body is not logged;
- backup redacted does not contain generated config;
- backup redacted does not contain share token hash;
- restore redacted backup does not revive share links;
- bearer token without `configs:read` denied;
- support role cannot download config unless route policy explicitly allows it.

Artifact integrity tests:

- `.conf` file bytes equal UTF-8 encoded config text;
- `.conf` round-trip preserves non-ASCII names, включая кириллицу;
- QR payload decode equals expected raw payload byte-for-byte;
- QR tests cover at least one non-ASCII connection/user/server name;
- QR generation failure returns sanitized error and does not leak config body;
- `vpn://` decode returns the original config text without byte loss;
- `vpn://` is classified as `client-config-secret` in logs, audit, backup and metrics checks;
- target client matrix records whether QR contains raw config or import URI;
- Android/import compatibility smoke exists for each supported artifact where tooling allows it;
- no config body, QR payload, QR image bytes or import URI appears in user-visible error detail.

Manager export contract tests:

- every protocol manager with config delivery implements the same export contract;
- every manager declares supported artifact types and target clients;
- self-service, public share and admin UI use the same export path;
- missing private key returns typed `unavailable_reason`;
- signature mismatch cannot reach runtime UI/API response;
- manager errors are redacted before response/audit/log output.

Aggregate checks:

- every `secret-download` route has audit required;
- every public-share route has expiry and rate limit;
- every config payload is classified as `client-config-secret`;
- every delivery surface has route policy;
- no share token field is plaintext in storage schema;
- every artifact type has an integrity test or an explicit documented reason why it cannot be tested yet.

## Путь внедрения в `amn2`

Рекомендуемый порядок:

1. Открыть текущий `amn2` и найти все места, где config, URI, QR или subscription выдаются пользователю.
2. Классифицировать каждый route через `Route Policy Matrix`.
3. Добавить ownership tests для существующих user-owned configs.
4. Ввести audit event на config download.
5. Добавить artifact integrity tests для `.conf`, QR и `vpn://` на существующем `build_device_config_delivery()`.
6. Ввести manager export contract, если появляются новые protocol manager-ы или новый путь выдачи config.
7. Ввести share token hash model, если public links уже есть или планируются.
8. Добавить expiry и revoke как обязательные поля share link.
9. Связать config payload с `Secret Inventory`.
10. Проверить backup/export на отсутствие generated configs и share tokens.
11. Только после этого расширять delivery channels, например Telegram.

## Решение для lab

Статус: `design-candidate`.

Этот spec закрывает пятую foundational-идею из feature gap. После него стоит сделать общий index/overview по design specs и transfer checklist для решения, что позже переносить в основной Amneziya/`amn2`.

## Источники

- Auth/secrets deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md](../../../research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md)
- API surface deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-api-surface.md](../../../research/upstreams/prvtpro-amnezia-web-panel-api-surface.md)
- Feature gap: [research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md](../../../research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md)
- PRVTPRO config delivery integrity: [research/upstreams/prvtpro-amnezia-web-panel-config-delivery-integrity.md](../../../research/upstreams/prvtpro-amnezia-web-panel-config-delivery-integrity.md)
- Route Policy Matrix spec: [docs/superpowers/specs/2026-05-30-route-policy-matrix-design.md](2026-05-30-route-policy-matrix-design.md)
- Secret Inventory + Backup Policy spec: [docs/superpowers/specs/2026-05-30-secret-inventory-backup-policy-design.md](2026-05-30-secret-inventory-backup-policy-design.md)
- Scoped API Tokens spec: [docs/superpowers/specs/2026-05-30-scoped-api-tokens-design.md](2026-05-30-scoped-api-tokens-design.md)
- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
