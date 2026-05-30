# wg-easy/wg-easy: metrics surface и privacy risks

## Паспорт deep-dive

- Upstream: https://github.com/wg-easy/wg-easy
- Дата анализа: 2026-05-30
- Область: Prometheus metrics, JSON metrics, bearer guard, metrics password storage, labels, privacy, route-policy implications.
- License verdict: AGPL-3.0-only, режим `research-only`.
- Production verdict для `amn2`: переносить только требования, privacy checklist и test ideas; не копировать routes, guard, metric names, UI или storage code.

## Краткий вывод

`wg-easy` показывает полезную operator-функцию: отдельный metrics surface для WireGuard peers, traffic и handshake state. Для `amn2` это хороший product signal, но production-перенос должен быть строже, чем просмотренный upstream-паттерн.

Главные выводы:

- metrics endpoint должен быть отдельным `RoutePolicy`, а не просто read-only route;
- metrics могут раскрывать sensitive metadata даже без private keys;
- bearer password/token не должен быть опциональной защитой, если endpoint доступен извне;
- Prometheus labels должны проходить privacy review, потому что labels часто уходят в долгоживущие monitoring backends;
- JSON metrics surface обычно чувствительнее Prometheus aggregates, потому что может отдавать per-client metadata.

## Metrics surfaces

| Surface | Upstream file | Что отдает | Первичный риск |
| --- | --- | --- | --- |
| Prometheus metrics | `src/server/routes/metrics/prometheus.get.ts` | peer counts, sent/received bytes, latest handshake seconds | client names/IP as labels, cardinality, scrape retention |
| JSON metrics | `src/server/routes/metrics/json.get.ts` | counts и массив clients с metadata | endpoint/publicKey/client metadata exposure |
| Metrics guard | `src/server/utils/handler.ts` | checks enabled flag и optional bearer password | public endpoint if enabled without password |
| Admin config | `admin/general.*`, `general/*` | metricsPrometheus, metricsJson, metricsPassword | hash/secret handling, UI preservation, backup policy |
| Docs | `docs/content/advanced/metrics/prometheus.md` | describes `/metrics/prometheus` and optional Bearer Password | docs normalize optional auth for internet exposure |

## Auth и enablement

`defineMetricsHandler` делает две проверки:

- если `metricsConfig.password` задан, требует `Authorization: Bearer <value>` и проверяет value через Argon2 hash compare;
- затем проверяет, включен ли конкретный metrics type: `prometheus` или `json`.

Важный risk signal: если metrics включены, но password не задан, application-level bearer check не выполняется. Upstream docs также описывают Bearer Password как optional setting. Для локального Prometheus за firewall это может быть осознанной deployment-моделью, но для `amn2` нельзя считать это безопасным production-default.

Решение для `amn2`:

- metrics route должен иметь policy id, например `metrics.prometheus.read`;
- default exposure: disabled;
- включение требует явного choice: local-only bind, allowlist или scoped token;
- internet-exposed metrics без auth запрещены;
- bearer password заменить scoped API token с `metrics:read` или близким scope;
- metrics access должен иметь rate limit и audit для configuration changes.

## Prometheus labels

Prometheus route формирует counts:

- `wireguard_configured_peers`;
- `wireguard_enabled_peers`;
- `wireguard_connected_peers`.

Также per-client series:

- sent bytes;
- received bytes;
- latest handshake seconds.

Labels в просмотренном route включают:

- interface name;
- enabled flag;
- IPv4 address;
- IPv6 address;
- client name.

Это полезно для operator UX, но опасно как production-default. Prometheus labels обычно реплицируются, ретеншн может быть длинным, dashboards часто шарятся шире, чем сама VPN-панель. Client name может быть email, username, device name или internal department. IP addresses и latest handshake раскрывают usage metadata.

Для `amn2` default policy:

- aggregate metrics без client labels разрешать проще;
- per-client labels делать opt-in;
- client name в label не включать по умолчанию;
- использовать stable non-secret peer id или hashed id, если нужны per-peer series;
- IP labels включать только после privacy review;
- document retention implications.

## JSON metrics

JSON route возвращает:

- configured/enabled/connected peer counts;
- массив clients;
- client name;
- enabled;
- IPv4/IPv6;
- public key;
- endpoint;
- latest handshake timestamp;
- transfer Rx/Tx.

Private key и pre-shared key не возвращаются, потому что `WireGuard.getAllClients()` использует public-safe client query, где private fields исключены. Это сильный positive signal.

Но JSON metrics все равно чувствительны:

- `endpoint` может раскрывать внешний IP/port пользователя;
- `latestHandshakeAt` раскрывает активность;
- `transferRx/Tx` раскрывает usage volume;
- `publicKey` не является private key, но является stable identifier peer-а;
- client name и addresses могут быть персональными или инфраструктурными данными.

Для `amn2` JSON metrics нельзя считать обычным public health endpoint. Это integration surface с отдельным scope, privacy policy и tests.

## Metrics password и storage

В `general_table` есть поля:

- `metrics_prometheus`;
- `metrics_json`;
- `metrics_password`.

`GeneralService.update` хэширует `metricsPassword`, если значение не выглядит как валидный Argon2 PHC hash. Это полезнее plaintext storage, но для `amn2` надо разделить две вещи:

- raw metrics token/password показывается оператору только при создании или rotation;
- hash не должен считаться harmless data, потому что он участвует в auth и попадает в backup/state.

Risk signals:

- admin general endpoint возвращает `metricsPassword` вместе с config fields;
- UI может сохранять уже хэшированное значение;
- backup/export должен классифицировать metrics token hash как secret-derived material;
- rotation/revoke flow должен быть явным.

Для `amn2` лучше не заводить отдельный metrics password. Использовать scoped API token:

- raw token one-time display;
- stored hash;
- scope `metrics:read`;
- expiry;
- revoke;
- last used metadata;
- owner inheritance.

## Сравнение с нашими specs

| Наш spec | Подтверждение от wg-easy | Что усилить |
| --- | --- | --- |
| Route Policy Matrix | metrics отдельный route family с own guard | добавить risk class для observability/read-metadata |
| Scoped API Tokens | bearer для metrics подтверждает integration use case | не использовать optional broad password, нужен `metrics:read` scope |
| Secret Inventory + Backup Policy | metrics password hash хранится в app state | classify metrics token hash and scrape config secrets |
| Public/Self-service Config Delivery | не напрямую, но оба surfaces работают с sensitive outputs | не смешивать config delivery tokens и metrics tokens |
| Design Specs Transfer Checklist | metrics повторяется во втором upstream | добавить privacy and retention gate |

## Что полезно для `amn2`

- Read-only metrics surface как отдельный product candidate.
- Counts: configured/enabled/connected peers.
- Traffic counters для operator monitoring.
- Latest handshake как диагностический сигнал.
- Public-safe source query без private/pre-shared keys.
- Separate enable flags для Prometheus и JSON.
- Metrics as integration surface, связанная со scoped tokens.

## Что полезно для будущего гибридного проекта

- Observability baseline для протоколов: counts, status, traffic, handshake/last-seen.
- Prometheus-first integration для operators.
- JSON metrics для internal dashboards, но за строгим integration auth.
- Dashboard templates как product docs, если labels проходят privacy review.
- Per-protocol metrics registry с одинаковыми privacy classes.

## Что нельзя переносить как есть

- AGPL-licensed metrics route/handler/UI implementation.
- Internet-accessible metrics без required auth или network policy.
- Optional bearer password как production-default.
- Client name/IP labels без privacy review.
- JSON client metadata без scoped token и audit policy.
- Metrics password/hash как обычное config field.
- Long-lived metrics secret без expiry, revoke и rotation.

## Risk findings

| Finding | Почему важно для `amn2` |
| --- | --- |
| Metrics password optional | enabled endpoint can become public unless deployment network protects it |
| Prometheus labels include client name and IPs | labels leak metadata into monitoring storage and dashboards |
| JSON metrics include endpoint/publicKey/handshake/traffic | read-only endpoint still reveals user activity and stable identifiers |
| Separate metrics bearer is not scoped API token | cannot express owner, expiry, revoke, scopes and audit consistently |
| Metrics password hash lives in general config | backup/config export must treat it as secret-derived material |
| No visible per-route rate limit in metrics guard | public or internet-facing scrape endpoints need abuse controls |

## Test-plan идеи для `amn2`

Минимальные tests перед production-переносом похожих идей:

- metrics disabled by default;
- disabled metrics endpoint returns denied response;
- enabled metrics endpoint without approved auth/network policy is rejected by configuration validation;
- bearer/scoped token without `metrics:read` denied;
- expired/revoked metrics token denied;
- disabled owner invalidates metrics token effective access;
- Prometheus aggregate route does not include private key, pre-shared key, raw config or token material;
- default labels do not include client name, user email or public endpoint;
- IP labels require explicit opt-in policy;
- JSON metrics route denied unless separate policy allows detailed metadata;
- metrics config changes create audit event;
- metrics scrape does not log raw bearer token;
- metrics token hash is redacted from backup by default;
- rate limit or scrape allowlist is enforced for internet-facing deployments.

## Решение для lab

Статус deep-dive: `completed-first-pass`.

Для `amn2` идея metrics surface остается полезной, но переносить ее можно только после `Route Policy Matrix` и `Scoped API Tokens`. Ближайшее production-safe направление:

- aggregate Prometheus metrics first;
- no client-name labels by default;
- `metrics:read` scoped token;
- explicit privacy review for per-client labels;
- JSON metrics only for authenticated internal/integration use.

Перед реальным переносом надо открыть текущий `amn2` и составить inventory существующих status/health/metrics endpoints, labels, auth methods и backup/log behavior.

## Источники

- Репозиторий: https://github.com/wg-easy/wg-easy
- README: https://github.com/wg-easy/wg-easy/blob/master/README.md
- Prometheus docs: https://github.com/wg-easy/wg-easy/blob/master/docs/content/advanced/metrics/prometheus.md
- `prometheus.get.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/routes/metrics/prometheus.get.ts
- `json.get.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/routes/metrics/json.get.ts
- `handler.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/utils/handler.ts
- `general/schema.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/general/schema.ts
- `general/service.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/general/service.ts
- `general/types.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/general/types.ts
- `admin/general.vue`: https://github.com/wg-easy/wg-easy/blob/master/src/app/pages/admin/general.vue
- `WireGuard.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/utils/WireGuard.ts
- `client/service.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/database/repositories/client/service.ts
- First-pass upstream card: [wg-easy-wg-easy.md](wg-easy-wg-easy.md)
