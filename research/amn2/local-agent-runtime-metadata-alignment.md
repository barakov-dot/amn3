# Local Agent Runtime Metadata Alignment

Дата: 2026-06-01.

Назначение: подготовить safety boundary для будущего controller/API слоя, который будет читать Local Agent runtime metadata без clients/configs/write lifecycle.

Это не implementation plan. Документ не меняет `amn2`, не добавляет новые `/api/*` routes и не расширяет Local Agent. Он фиксирует, какие уже существующие Local Agent поля можно считать safe для controller summary, какие требуют operator-only/opt-in policy, а какие запрещены.

## Current production baseline

В `amn2` уже есть read-only Local Agent foundation:

```text
GET /agent/health
GET /agent/version
GET /agent/runtime
GET /agent/protocols
```

Scopes:

```text
agent:health
agent:read
agent:protocols:read
```

Current production facts from `app/agent/api.py` and `app/agent/runtime.py`:

- `/agent/version` returns `runtime_contract_version`, `first_slice_routes`, `write_enabled=false`.
- `/agent/runtime` returns `server_name`, `runtime_type`, `status`.
- `/agent/protocols` returns protocol `name`, `status`, `runtime_type`, `capabilities`, `container_name`, `interface`, `client_count`.
- Local Agent docs/OpenAPI are disabled.
- Allowed read requests are audited through `local_agent_read`.
- Raw bearer token is not written to audit.

## Alignment classes

| Class | Meaning | Future controller/API default |
| --- | --- | --- |
| `public-operational` | Safe service/runtime facts without topology, client or secret detail | Allowed |
| `operator-operational` | Useful to admin/operator but may expose local naming/topology | Operator-only or internal controller only |
| `aggregate-runtime` | Counts without client identities or per-peer labels | Allowed after privacy classification |
| `topology-sensitive` | Container names, interface names, host/service names, paths | Block from public/external API by default |
| `activity-sensitive` | Per-peer online/handshake/traffic details | Block by default |
| `secret-forbidden` | Tokens, config payloads, private keys, PSK, full configs | Always forbidden |
| `write-forbidden` | Any field/action implying create/update/delete/apply/revoke | Not part of this slice |

## Current field decisions

| Field | Source | Class | Decision | Notes |
| --- | --- | --- | --- | --- |
| `status=ok` | `/agent/health` | `public-operational` | allow | Health only, no host details. |
| `service=local-amnezia-agent` | `/agent/health` | `public-operational` | allow | Static service id is fine. |
| `api` | `/agent/version` | `public-operational` | allow | Static API id. |
| `version` | `/agent/version` | `public-operational` | allow | Build version is useful for compatibility. |
| `runtime_contract_version` | `/agent/version` | `public-operational` | allow | Required for controller compatibility. |
| `first_slice_routes` | `/agent/version` | `public-operational` | allow | Helps clients verify no write routes are present. |
| `write_enabled=false` | `/agent/version` | `public-operational` | require | Must remain false for first controller slice. |
| `server_name` | `/agent/runtime` | `operator-operational` | allow internal; redact/pseudonymize externally | Server alias can reveal customer/location naming. |
| `runtime_type` | `/agent/runtime`, `/agent/protocols` | `public-operational` | allow | Example: `docker`, `host_systemd`, `fake`. |
| `status` | `/agent/runtime`, `/agent/protocols` | `public-operational` | allow | Values: running/degraded/stopped/unknown. |
| `protocol.name` | `/agent/protocols` | `public-operational` | allow | Example: `amneziawg`; not a secret. |
| `protocol.capabilities` | `/agent/protocols` | `public-operational` | allow read-only capabilities only | Must not imply write support until a separate gate. |
| `client_count` | `/agent/protocols` | `aggregate-runtime` | allow after metrics privacy policy | Count only; no client identities. |
| `container_name` | `/agent/protocols` | `topology-sensitive` | block from public/external API by default | Useful to operator, but exposes local topology. |
| `interface` | `/agent/protocols` | `topology-sensitive` | block from public/external API by default | Can expose network topology. |
| `config_path` | not currently returned | `secret-forbidden` / `topology-sensitive` | forbid | Path can reveal deployment layout and points to secret-bearing config. |
| raw command stdout/stderr | not currently returned | `secret-forbidden` | forbid | Use redacted status only. |
| peer public key | not currently returned | `activity-sensitive` / stable id | forbid by default | Belongs to detailed peer policy, not runtime metadata. |
| VPN IP / endpoint | not currently returned | `topology-sensitive` / `activity-sensitive` | forbid | Covered by metrics privacy classification. |
| `.conf`, QR, `vpn://`, private key, PSK | not currently returned | `secret-forbidden` | always forbid | Never Local Agent runtime metadata. |

## Future controller summary shape

If a controller/API route summarizes Local Agent runtime, its first slice should normalize to a smaller public-safe object:

```text
agent_status
agent_version
runtime_contract_version
write_enabled
runtime_type
runtime_status
protocols[].name
protocols[].status
protocols[].runtime_type
protocols[].capabilities
protocols[].client_count
```

It should omit by default:

```text
server_name
container_name
interface
config_path
service_name
command strings
stdout/stderr
peer public keys
VPN IPs
endpoints
latest handshakes
per-peer traffic
client names
configs
```

`server_name` can be included only when the caller is an operator-facing admin surface and the route policy says it is operator-only.

## Route and scope boundary

This alignment does not create new scopes. Existing Local Agent scopes remain:

```text
agent:health
agent:read
agent:protocols:read
```

Future controller/API routes should not forward raw Local Agent responses directly. They should map fields through this alignment table and use their own route policy:

- `server:read` for server/runtime summary;
- `metrics:read` for aggregate metrics;
- no `config:read`;
- no write scopes.

## Required tests before implementation

Future implementation plan must include tests that:

- controller summary includes `runtime_contract_version` and `write_enabled=false`;
- summary includes protocol status/capabilities but not `container_name` or `interface` by default;
- summary never includes `config_path`, command strings, stdout/stderr, `.conf`, QR, `vpn://`, private key or PSK;
- `client_count` is aggregate-only and cannot be expanded into clients through the same route;
- token without required read scope is rejected;
- Local Agent raw bearer token is not logged/audited;
- `/agent/clients`, `/agent/configs`, backup/import/reboot/write lifecycle remain unavailable.

## Decision

Status: `alignment-prepared-local-docs`.

The next Local Agent work after real VPS evidence should be an implementation plan for a controller-safe runtime summary, not `GET /agent/clients` and not config delivery.

Recommended first implementation boundary:

```text
controller-safe Local Agent runtime summary
```

Blocked until separate gates:

- client list;
- client configs;
- per-peer detailed metrics;
- backup/import/reboot;
- write lifecycle;
- real controller-to-agent mutation.
