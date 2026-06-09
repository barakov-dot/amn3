# Phase 4 P4-X001: read-only API docs grouping polish 2026-06-09

Дата: 2026-06-09.

Назначение: закрыть `P4-X001` как AMN3 docs-only/local-only polish. Slice группирует уже существующие private/local read-only API routes для operator/integrator navigation, но не публикует OpenAPI/docs наружу и не расширяет API surface.

## Решение

```text
candidate_id: P4-X001
priority: cosmetic
gate: local-only
AMN3_scope: docs/status/registry/handoff only
AMN2_code_changed: no
live_vps_commands: no
runtime_route_changes: no
public_openapi_docs_exposure: no
route_expansion: no
config_delivery: no
write_api: no
local_agent_mutation: no
```

## Baseline

P4-X001 starts after:

- `P4-I003` read-only API/status schema implementation;
- `P4-I004` endpoint taxonomy / route-policy docs alignment;
- `P4-N003` aggregate metrics privacy boundary;
- `P4-I005` API token lifecycle boundary;
- `P4-X002` API/status/gate naming cleanup.

The implemented private/local read-only API surface remains exactly six routes:

| Group | Route | Scope | Safe meaning |
| --- | --- | --- | --- |
| Server inventory/status | `GET /api/servers` | `server:read` | server list/status metadata only |
| Server inventory/status | `GET /api/servers/{server_name}/summary` | `server:read` | aggregate server/user/device summary only |
| Integration/service boundary | `GET /api/integration/status` | `server:read` | service-mode/read-only/API/token-boundary status markers only |
| Local Agent runtime summary | `GET /api/local-agent/runtime/summary` | `server:read` | controller-safe Local Agent runtime summary only |
| Aggregate metrics | `GET /api/metrics/summary` | `metrics:read` | aggregate metrics only, no peer/user detail leakage |
| Aggregate metrics | `GET /api/users/summary` | `metrics:read` | aggregate user/device counts only |

## Grouping Boundary

This grouping is operator documentation only:

- no generated or public OpenAPI route is enabled;
- no `/docs`, Swagger UI, Redoc or public API documentation surface is authorized;
- no new `/api/*` route is added;
- no `config:read`, write scope, admin-equivalent scope or destructive scope is added;
- no `.conf`, QR, `vpn://`, token, key, PSK, endpoint, peer public key or backup data is exposed;
- public API `3040` and direct public web/admin `3030` remain absent/closed;
- service-mode remains loopback-only with SSH-tunnel operator access.

## Docs Updated

- `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`
- `docs/PROJECT_STATUS_CURRENT.ru.md`
- `docs/PROJECT_CONTEXT_IMPORT.ru.md`
- `docs/superpowers/plans/2026-06-09-amn2-phase-4-start.md`
- `research/amn2/phase-4-candidate-registry-2026-06-09.md`
- `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md`
- `research/amn2/transfer-backlog.md`

## Result

`P4-X001` is closed as docs-only/local-only. The active default-mode Phase 4 plan no longer has a cosmetic implementation item after this slice.

Remaining default-mode decision:

- run `P4-I001` only if more private-panel page-level UX evidence is needed;
- otherwise pause default local-only implementation and require an explicit named gate/decision before any VPS/live/public/write/config work.

## Safety Statement

No AMN2 code, live VPS command, package apply, route expansion, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` CRUD, Local Agent mutation, token issue/revoke/rotate route, backup/import/reboot or production peer/user mutation was performed.
