# Phase 4 P4-PRVTPRO-REFRESH-004: API taxonomy/OpenAPI grouping policy support 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `P4-PRVTPRO-REFRESH-004` как AMN3 docs-only/local-only policy slice. Slice принимает PRVTPRO сигнал о группировке API как идею для auditability, но не создает OpenAPI artifact, не публикует docs наружу и не расширяет AMN2 API surface.

## Решение

```text
candidate_id: P4-PRVTPRO-REFRESH-004
priority: important
gate: local-only
AMN3_scope: docs/status/registry/handoff only
AMN2_code_changed: no
live_vps_commands: no
runtime_route_changes: no
generated_openapi_artifact: no
public_openapi_docs_exposure: no
route_expansion: no
config_delivery: no
write_api: no
local_agent_mutation: no
live_write_authorized: no
```

## Source Boundary

Inputs:

- `research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md`;
- `research/upstreams/prvtpro-amnezia-web-panel-api-surface.md`;
- `research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-10.md`;
- `research/amn2/phase-4-read-only-api-docs-grouping-polish-2026-06-09.md`;
- `research/amn2/route-policy-matrix.md`;
- `research/amn2/route-auth-surface-inventory.md`.

PRVTPRO/Amnezia-Web-Panel remains GPL-3.0 research-only. No upstream code, templates, UI, route layout, manager implementation, workflow or OpenAPI text is copied.

## Current Private/Local API Groups

The current AMN2 private/local read-only API surface remains exactly six routes:

| group_id | Route | Scope | Data class | Boundary |
| --- | --- | --- | --- | --- |
| `server_inventory_status` | `GET /api/servers` | `server:read` | safe server metadata | no config payload, no endpoint secrets, no writes |
| `server_inventory_status` | `GET /api/servers/{server_name}/summary` | `server:read` | aggregate server/user/device summary | no peer config delivery, no mutation |
| `integration_service_boundary` | `GET /api/integration/status` | `server:read` | service-mode/read-only/token-boundary markers | no token issue/revoke/rotate route |
| `local_agent_runtime_summary` | `GET /api/local-agent/runtime/summary` | `server:read` | controller-safe Local Agent runtime summary | no Local Agent mutation |
| `aggregate_metrics` | `GET /api/metrics/summary` | `metrics:read` | aggregate metrics | no per-peer or per-user leakage |
| `aggregate_metrics` | `GET /api/users/summary` | `metrics:read` | aggregate user/device counts | no config/user write behavior |

This grouping is the only active taxonomy baseline for Phase 4 docs. `checked_routes` remains six.

## Future Group Policy

Any future route taxonomy or OpenAPI grouping must classify every candidate route before implementation:

| Required field | Meaning |
| --- | --- |
| `group_id` | Stable domain group, not copied from upstream route names |
| `route` | Proposed or existing route path |
| `method` | HTTP method |
| `auth` | Session/API token/internal gate classification |
| `scope_or_role` | Minimal required scope or role |
| `data_class` | Safe metadata, aggregate data, secret-bearing config, destructive operation, etc. |
| `side_effect` | None, local mutation, remote mutation, destructive action |
| `audit_required` | Whether audit event/test is required |
| `public_exposure` | `false` unless a separate public/docs gate approves otherwise |
| `config_secret_surface` | Whether `.conf`, QR, `vpn://`, keys, PSK, endpoint values, token data or backup data can appear |
| `named_gate` | Required gate class before implementation |
| `tests_required` | Route drift, auth/scope, secret scan, audit and negative controls |

## Blocked Groups

The following route groups remain blocked until separate named gates:

| Candidate group | Status |
| --- | --- |
| client/user lifecycle write API | blocked until WAPI route taxonomy plus write gate |
| config delivery, QR and `vpn://` reads | blocked until config/read or delivery gate |
| API token issue/revoke/rotate routes | blocked until token lifecycle write gate |
| Local Agent mutation routes | blocked until Local Agent mutation gate |
| backup/import/reboot/server cleanup | blocked until destructive ops gate |
| public/self-service/share links | blocked until public/config gate |
| public OpenAPI, Swagger UI or Redoc | blocked until public-docs gate |

## Required Controls Before OpenAPI Artifacts

Before any future OpenAPI artifact, generated docs or route docs endpoint is introduced:

- route drift tests must confirm the documented surface matches runtime bindings;
- route count changes must be intentional and reviewed;
- forbidden-marker scans must reject secret-bearing examples, `.conf`, QR, `vpn://`, token values, endpoint values, keys, PSK, peer public keys, backup contents and raw logs;
- docs must not imply public API `3040`, direct public web/admin `3030`, domain/HTTPS cutover or config delivery;
- generated examples must not include production identifiers, secrets or live endpoint values;
- every write/config/destructive route must carry `live_write_authorized: no` until its own live gate says otherwise.

## Result

`P4-PRVTPRO-REFRESH-004` is closed as docs-only/local-only policy support.

Remaining PRVTPRO-derived AMN2 work:

- `P4-PRVTPRO-REFRESH-003` read-only server status/latency UX only after a separate design boundary.

Recommended next safe task:

- `WAPI-V002` write API route taxonomy, docs-only, with `live_write_authorized: no`.

## Safety Statement

No AMN2 code, live VPS command, SSH command, package apply, runtime route change, generated OpenAPI artifact, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` CRUD, Local Agent mutation, token issue/revoke/rotate route, backup/import/reboot or production peer/user mutation was performed.
