# Read-only Metrics and Client Privacy Classification

Дата: 2026-06-01.

Назначение: подготовить privacy gate для будущего read-only metrics/API route shell после real VPS evidence.

Это не implementation plan. Документ не добавляет `/api/*` routes, не меняет `amn2` production-код и не разрешает write lifecycle. Он фиксирует, какие поля можно отдавать по умолчанию, какие требуют opt-in detailed policy, а какие запрещены для metrics/read-only API.

## Why this exists

После VPS gate следующий безопасный integration slice, вероятно, будет read-only server/client status или metrics. Даже read-only surface может раскрыть:

- client/device names;
- Telegram/user identity;
- VPN IP, endpoint IP/port;
- latest handshake и activity pattern;
- per-peer traffic volume;
- public key как stable identifier;
- topology/capacity metadata.

Поэтому `server:read` и `metrics:read` scopes нельзя считать автоматическим разрешением на любые client fields.

## Privacy classes

| Class | Meaning | Default policy |
| --- | --- | --- |
| `aggregate-operational` | Counts/totals without user, peer, IP or endpoint labels | Allowed for first read-only metrics slice |
| `server-operational` | Server alias/status/runtime health without secrets | Allowed with `server:read` after route policy |
| `pseudonymous-peer` | Stable non-secret peer id not directly reversible to user/device | Opt-in detailed metrics only |
| `personal-identity` | User name, Telegram id, email, device/client display name | Forbidden in default metrics |
| `network-address` | VPN IP, endpoint IP/port, interface address labels | Forbidden in default metrics |
| `activity-metadata` | Latest handshake, online state, per-peer transfer volume | Aggregate allowed; per-peer requires opt-in detailed policy |
| `secret-derived` | Token hash, config hash, backup id, scrape token hash | Forbidden in metrics output; safe metadata only in admin/audit |
| `client-config-secret` | `.conf`, QR payload, `vpn://`, private key, PSK | Always forbidden in metrics/read-only API |

## Default route candidates

The first route shell should stay aggregate-only:

| Candidate surface | Scope | Default allowed fields | Default forbidden fields |
| --- | --- | --- | --- |
| `GET /api/servers` | `server:read` | server id/alias, status, runtime kind, latest health status, aggregate device counts | config paths, host secrets, command output, peer public keys |
| `GET /api/servers/{id}/summary` | `server:read` | configured/enabled/disabled/unknown counts, latest sync timestamp, readiness flags | user names, device names, VPN IPs, endpoints |
| `GET /api/metrics/summary` | `metrics:read` | aggregate peer counts, aggregate traffic totals, scrape timestamp | per-peer labels, public keys, IPs, latest handshake per peer |
| Prometheus-style metrics | `metrics:read` | aggregate series with low-cardinality labels like runtime/server pseudonym | labels with client name, user id, public key, VPN IP, endpoint |

No JSON per-client metrics route should be part of the first slice.

## Field classification

| Field | Class | Default decision | Notes |
| --- | --- | --- | --- |
| `server_id` | `server-operational` | allow | Prefer internal id or alias already visible to admin. |
| `server_alias` | `server-operational` | allow | Avoid public exposure; still admin/integration only. |
| `runtime_kind` | `server-operational` | allow | Example: Docker/systemd/unknown. |
| `health_status` | `server-operational` | allow | No raw stderr/stdout. |
| `latency_ms` | `server-operational` | allow | Aggregate server health only. |
| `configured_peer_count` | `aggregate-operational` | allow | Count only. |
| `enabled_peer_count` | `aggregate-operational` | allow | Count only. |
| `disabled_peer_count` | `aggregate-operational` | allow | Count only. |
| `connected_peer_count` | `aggregate-operational` | allow | Count only; define connection window in docs. |
| `aggregate_rx_bytes` | `aggregate-operational` | allow | Server-level total only. |
| `aggregate_tx_bytes` | `aggregate-operational` | allow | Server-level total only. |
| `last_sync_at` | `server-operational` | allow | Server sync timestamp, not per-peer activity. |
| `peer_public_key` | `pseudonymous-peer` | deny by default | Stable identifier; never a Prometheus label by default. |
| `peer_hash_id` | `pseudonymous-peer` | opt-in later | Only if salted/non-secret and documented. |
| `user_id` | `personal-identity` | deny | Internal id can become identifying when joined. |
| `telegram_id` | `personal-identity` | deny | Never metrics label. |
| `email` | `personal-identity` | deny | Never metrics/read-only summary. |
| `device_name` | `personal-identity` | deny | Can contain real names. |
| `vpn_ip` | `network-address` | deny | Detailed route only after privacy review. |
| `endpoint` | `network-address` | deny | Exposes user network location. |
| `latest_handshake_at` | `activity-metadata` | deny by default | Aggregate connected count is safer. |
| `peer_rx_bytes` | `activity-metadata` | deny by default | Reveals per-user usage pattern. |
| `peer_tx_bytes` | `activity-metadata` | deny by default | Reveals per-user usage pattern. |
| `expires_at` | `activity-metadata` | deny by default | Lifecycle state belongs in a separate user/device API design. |
| `client_config_version` | `server-operational` | deny by default | Could be allowed later if it cannot reveal template state. |
| `api_token_hash` | `secret-derived` | deny | Audit/admin only; never metrics. |
| `metrics_token_hash` | `secret-derived` | deny | Backup/audit policy, not output. |
| `.conf` / QR / `vpn://` | `client-config-secret` | deny | Always forbidden. |

## Prometheus label policy

Default labels allowed:

- deployment/environment only if non-sensitive;
- server pseudonym or internal id;
- runtime kind;
- status class.

Default labels forbidden:

- client/device/user names;
- Telegram id or email;
- public key;
- VPN IP;
- endpoint IP/port;
- exact per-peer latest handshake;
- per-peer traffic labels.

Prometheus retention note: labels often live longer and spread wider than application logs. Treat a forbidden label as a data leak even if the endpoint is authenticated.

## Auth and enablement

First slice rules:

- metrics disabled by default;
- no internet-exposed metrics without auth/network policy;
- no optional broad password;
- use scoped token contract with `metrics:read`;
- raw token shown once at issue time only;
- token hash is `secret-derived`;
- enabling metrics is an admin action and must be auditable.

Existing first-slice scopes remain:

```text
server:read
metrics:read
```

Do not add write scopes or `config:read` as part of metrics work.

## Tests required before route implementation

Future implementation plan must include tests that:

- aggregate metrics response contains no `peer_public_key`, `vpn_ip`, `endpoint`, `device_name`, `telegram_id`, `email`;
- Prometheus labels exclude all default-forbidden fields;
- `.conf`, QR payload, `vpn://`, private key and PSK never appear in metrics output;
- unauthenticated metrics request is rejected unless explicitly local-only in a documented test mode;
- token with `server:read` cannot access `metrics:read` route;
- token with `metrics:read` cannot access config or write routes;
- audit/log metadata does not store raw metrics token.

## Decision

Status: `classification-prepared-local-docs`.

The next implementation slice after real VPS evidence should be:

```text
read-only API route shell with aggregate metrics only
```

Detailed per-peer/client metrics remain blocked until there is a separate opt-in detailed metrics policy, retention note and test plan.
