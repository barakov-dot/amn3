# Phase 4 WAPI-V002: write API route taxonomy 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `WAPI-V002` как AMN3 docs-only route taxonomy для будущего write API. Документ предлагает candidate route groups and route names for planning only; он не добавляет AMN2 runtime routes, не создает OpenAPI artifact, не разрешает live write и не открывает config delivery.

## Decision

```text
slice_id: WAPI-V002
slice_name: write API route taxonomy
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
generated_openapi_artifact: no
public_openapi_docs_exposure: no
config_delivery: no
production_mutation: no
live_vps_commands: no
ssh_commands: no
required_gate_for_live_write: P4-WRITE-API-LIVE-GATE
selected_next_slice: WAPI-V003 local fake-runner contract
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
selected_next_slice_status: completed 2026-06-10; see research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md
```

## Sources Reused

- `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`;
- `research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md`;
- `research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md`;
- `research/amn2/route-policy-matrix.md`;
- `research/amn2/route-auth-surface-inventory.md`;
- `docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md`;
- `research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-10.md`.

KYORESUAS and PRVTPRO remain product/architecture signals only. No upstream code, route layout, command strings, OpenAPI text, UI, templates, workflows or manager implementations are copied.

## Baseline

Current AMN2 runtime API remains unchanged:

- existing private/local read-only `/api/*` surface remains six routes;
- no `/api/clients` write CRUD route exists or is added by this slice;
- no `config:read`, secret-read route, public route, destructive route or Local Agent mutation route is authorized;
- `live_write_authorized: no` remains required for every WAPI design slice.

## Route Classification Fields

Every future write API route proposal must include these fields before AMN2 implementation planning:

| Field | Required meaning |
| --- | --- |
| `candidate_route` | Proposed planning name only; not a runtime route until a later AMN2 implementation plan |
| `group_id` | One of `clients`, `peers`, `configs`, `operations`, `audit_status` |
| `method` | Intended HTTP method |
| `route_class` | `read-only`, `state-write`, `secret-read`, `destructive`, `public-exposure` |
| `auth_model` | Session/API token/internal gate requirement |
| `scope` | Minimal scope; no broad admin-equivalent default |
| `side_effect` | None, local metadata write, operation record write, remote mutation, destructive action |
| `live_write_authorized` | Always `no` until a separate live gate explicitly changes it |
| `named_gate` | Required gate before implementation or execution |
| `response_secret_surface` | Whether the response can contain tokens, `.conf`, QR, `vpn://`, keys, PSK, endpoint values or backup data |
| `required_tests` | Route drift, auth/scope, secret scan, fake-runner, idempotency/lock, audit/redaction or public hardening tests |

## Candidate Route Taxonomy

These names are planning placeholders, not implementation approval.

| Candidate route | Group | Class | Minimal scope | Side effect | Required gate before implementation |
| --- | --- | --- | --- | --- | --- |
| `GET /api/clients` | `clients` | `read-only` | `client:read` | none | AMN2 local read-only route plan |
| `GET /api/clients/{client_id}` | `clients` | `read-only` | `client:read` | none | AMN2 local read-only route plan |
| `POST /api/clients` | `clients` | `state-write` | `client:write` | local record plus operation plan only in first implementation | WAPI-V003 fake-runner contract, then AMN2 local write plan |
| `PATCH /api/clients/{client_id}` | `clients` | `state-write` | `client:write` | local metadata/status change only until live gate | WAPI-V003 and WAPI-V004 before any implementation |
| `POST /api/clients/{client_id}:disable` | `clients` | `state-write` | `client:disable` | future local disable state; remote peer mutation blocked | WAPI-V003 and WAPI-V004 before any implementation |
| `POST /api/clients/{client_id}:revoke` | `clients` | `state-write` | `client:revoke` | future revoke operation plan; live peer revoke blocked | WAPI-V003, WAPI-V004 and live write gate before remote execution |
| `POST /api/peers/{peer_id}:plan-apply` | `peers` | `state-write` | `peer:plan` | operation plan record only | WAPI-V003 fake-runner contract |
| `POST /api/peers/{peer_id}:apply` | `peers` | `state-write` | `peer:apply` | remote peer mutation | `P4-WRITE-API-LIVE-GATE` after fake-runner and idempotency/lock design |
| `POST /api/peers/{peer_id}:revoke` | `peers` | `state-write` | `peer:revoke` | remote peer mutation | `P4-WRITE-API-LIVE-GATE` after fake-runner and idempotency/lock design |
| `POST /api/peers:sync` | `peers` | `state-write` | `peer:sync` | remote read plus possible local reconciliation | separate sync/reconciliation gate |
| `GET /api/configs/{client_id}/metadata` | `configs` | `read-only` | `config:metadata` | none | AMN2 local read-only route plan; no secret payload |
| `POST /api/configs/{client_id}:prepare` | `configs` | `secret-read` | `config:prepare` | secret-bearing config generation | separate config/read-delivery gate |
| `GET /api/configs/{client_id}.conf` | `configs` | `secret-read` | `config:read` | secret-bearing config read | separate config/read-delivery gate |
| `GET /api/configs/{client_id}/qr` | `configs` | `secret-read` | `config:read` | secret-bearing QR read | separate config/read-delivery gate |
| `GET /api/configs/{client_id}/vpn-url` | `configs` | `secret-read` | `config:read` | secret-bearing `vpn://` read | separate config/read-delivery gate |
| `GET /api/operations/{operation_id}` | `operations` | `read-only` | `operation:read` | none | AMN2 local read-only operation-status plan |
| `POST /api/operations/{operation_id}:cancel` | `operations` | `state-write` | `operation:write` | local operation state change | WAPI-V004 before implementation |
| `POST /api/operations/{operation_id}:retry` | `operations` | `state-write` | `operation:write` | local retry plan; remote retry blocked | WAPI-V003 and WAPI-V004 before implementation |
| `GET /api/audit/events` | `audit_status` | `read-only` | `audit:read` | none | WAPI-V005 audit/redaction requirements before implementation |
| `GET /api/write-api/status` | `audit_status` | `read-only` | `operation:read` | none | AMN2 local read-only route plan |

## Blocked Route Families

The following families remain blocked outside WAPI default docs-only mode:

| Family | Class | Required named gate |
| --- | --- | --- |
| live peer apply/revoke/sync execution | `state-write` | `P4-WRITE-API-LIVE-GATE` |
| config download, QR, `vpn://`, share links and archives | `secret-read` | separate config/read-delivery gate |
| public/self-service config links | `public-exposure` + `secret-read` | separate public/config gate |
| backup/import/reboot/service restart/firewall/proxy edits | `destructive` | destructive-operation gate |
| Local Agent config/write mutation | `state-write` | Local Agent mutation gate |
| public OpenAPI, Swagger UI, Redoc or public route docs | `public-exposure` | public-docs gate |

## Scope Policy

Allowed future scopes are narrow and route-specific:

- `client:read`, `client:write`, `client:disable`, `client:revoke`;
- `peer:plan`, `peer:apply`, `peer:revoke`, `peer:sync`;
- `operation:read`, `operation:write`;
- `audit:read`;
- `config:metadata`, `config:prepare`, `config:read`.

Policy constraints:

- existing `server:read` and `metrics:read` scopes do not authorize write/config/destructive routes;
- broad admin-equivalent API tokens are rejected by default;
- `config:read` is secret-read and cannot be bundled into client creation;
- every write route must reject read-only tokens;
- every future token that can write must have explicit expiry and ownership rules from `P4-I005`.

## Test Requirements Before Implementation

Before any candidate route becomes AMN2 code:

- route/auth/scope tests must prove each route accepts only its minimal scope;
- route drift tests must prove docs and runtime bindings match;
- read-only token rejection tests must cover every write/config/destructive candidate;
- forbidden-marker scans must reject `.conf`, QR, `vpn://`, tokens, keys, PSK, peer public keys, endpoint values, Authorization headers, token hashes, backup contents and raw logs;
- fake-runner tests must exist before any live runner path;
- idempotency key and per-target lock tests must exist before create/revoke/sync implementation;
- audit/redaction tests must exist before operation/audit routes;
- config delivery tests must live under a separate config/read-delivery gate;
- public hardening tests must live under a separate public exposure gate.

## WAPI-V003 Handoff

`WAPI-V003` was selected next and later closed as docs-only fake-runner contract:

```text
slice_id: WAPI-V003
slice_name: local fake-runner contract
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
live_vps_commands: no
```

It defines fake-runner inputs/outputs for create, disable, revoke, sync and retry operation plans without SSH, live VPS commands or remote mutation. `WAPI-V004` was selected next and later closed as docs-only idempotency, locking and partial-failure model; `WAPI-V005` was then closed as write API audit/redaction requirements. Current next recommendation after `WAPI-V005` closure is `WAPI-I004` operation status model with `live_write_authorized: no`.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: WAPI-V003 docs-only local fake-runner contract with live_write_authorized: no
no_go_scope: runtime route expansion, live write, public exposure, config delivery, SSH/VPS commands, production mutation
defer_scope: AMN2 route implementation, live peer mutation, config/read-delivery routes, public/self-service routes, destructive operations
```

## Safety Statement

No AMN2 code, live VPS command, SSH command, package apply, route expansion, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` CRUD, Local Agent mutation, token issue/revoke/rotate route, backup/import/reboot or production peer/user mutation was performed.
