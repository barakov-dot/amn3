# Phase 4 WAPI-V001: write API threat model 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `WAPI-V001` как AMN3 docs-only threat model перед route taxonomy и любым будущим AMN2 local implementation plan. Этот документ не разрешает AMN2 runtime changes, new API routes, live VPS commands, SSH commands, public exposure, config delivery or production mutation.

## Decision

```text
slice_id: WAPI-V001
slice_name: write API threat model
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
config_delivery: no
production_mutation: no
live_vps_commands: no
ssh_commands: no
required_gate_for_live_write: P4-NG-WRITE-API-LIVE-GATE
selected_next_slice: WAPI-V002 write API route taxonomy
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
selected_next_slice_status: completed 2026-06-10; see research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md
```

## Sources Reused

- `research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md`
- `research/amn2/phase-4-protocol-manager-interface-checklist-2026-06-09.md`
- `research/amn2/phase-4-api-token-lifecycle-boundary-implementation-2026-06-09.md`
- `research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md`
- `research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-10.md`
- `research/upstreams/kyoresuas-amnezia-api.md`
- `docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md`

## KYORESUAS Production Signals Used

The 2026-06-10 KYORESUAS refresh is used only as product/architecture signal. No upstream code, route layout, scripts, command strings, service files or generated artifacts are copied.

Signals carried into this threat model:

- one operation lock/serialization boundary per server, protocol and write surface;
- temp/atomic config write before any future live save/apply path;
- backup-before-write, post-check and rollback/audit metadata as future write controls;
- `active | disabled` plus `expiresAt` lifecycle vocabulary for future client status design;
- QR and `vpn://` treated as secret-read/import artifacts requiring dedicated tests;
- rate-limit and Helmet-style hardening treated as future public-route gate requirements, not default private-route behavior;
- setup resilience treated as install/operator hardening signal, not permission to add package apply or service mutation.

## Protected Assets

- live VPS peer/user state;
- local AMN2 user/device/server records;
- scoped API tokens and token ownership state;
- config artifacts: `.conf`, QR, `vpn://`, share/download URLs and archives;
- operation plans, audit records and recovery notes;
- service-mode loopback/tunnel boundary;
- public exposure boundary for API `3040`, web/admin `3030`, TCP `80/443` and Caddy/HTTPS/domain cutover.

## Trust Boundaries

Future write API design must treat these boundaries as separate:

- authenticated API caller to AMN2 route handler;
- route handler to policy/scope enforcement;
- local DB mutation to remote operation planning;
- fake runner to any future live runner;
- state-write operation to secret-read config delivery;
- operation status/audit metadata to secret-bearing payloads;
- private loopback/tunnel operation to any public exposure.

No boundary may be collapsed by a convenience route. In particular, peer/client creation must not automatically return config payloads or public/self-service download links.

## Threat Classes

| ID | Threat | Risk | Required Controls Before Implementation |
| --- | --- | --- | --- |
| `WAPI-T01` | Accidental live mutation from a design/local slice | critical | Every slice states `live_write_authorized: no`; fake-runner first; marker scan rejects live-write enablement. |
| `WAPI-T02` | Scope escalation from read-only token to write action | critical | Dedicated write scopes; read scopes rejected for writes; route/auth binding tests for every route. |
| `WAPI-T03` | Config secret leakage through create/status/audit/error response | critical | Config delivery separated from client creation; secret inventory classification; forbidden-marker response/log/audit tests. |
| `WAPI-T04` | Token lifecycle bypass or owner mismatch | important | Explicit expiry, owner checks, digest-only storage, one-time display, idempotent revoke, no broad admin-equivalent tokens. |
| `WAPI-T05` | Replay or duplicate peer creation/revoke | important | Idempotency keys, stable operation IDs, duplicate request tests, safe retry semantics. |
| `WAPI-T06` | Concurrent operations racing on same client/server/peer | important | Per-target locks, conflict status, no overlapping apply/revoke/sync for the same target. |
| `WAPI-T07` | Split-brain partial failure between local DB and remote peer state | critical | Explicit consistency statuses, recovery notes, rollback/defer behavior, fake-runner partial-failure tests. |
| `WAPI-T08` | Audit/log/error includes secrets or endpoint values | critical | Redacted audit schema, safe metadata only, no raw stdout/stderr, no Authorization headers or token hashes. |
| `WAPI-T09` | Public exposure creep while adding write surfaces | critical | Public exposure remains a separate named gate; route taxonomy marks public-exposure separately from state-write. |
| `WAPI-T10` | Local Agent confused-deputy mutation/config delivery | important | Local Agent write/config routes remain blocked; controller-to-agent calls require separate gate and scopes. |
| `WAPI-T11` | Destructive operation smuggled into client lifecycle | critical | Destructive routes classified separately: backup/import/reboot, service restart, firewall/proxy edits, raw config apply. |
| `WAPI-T12` | Operation status leaks peer/user identity or config metadata | important | Operation status returns safe aggregate/opaque IDs only unless a stricter private gate explicitly allows more. |
| `WAPI-T13` | Upstream/reference implementation crosses license boundary | important | PRVTPRO/KYORESUAS remain ideas/reference; no code, templates, scripts, command strings or generated artifacts copied. |
| `WAPI-T14` | Non-atomic config write leaves remote state partially saved | critical | Future write design must require temp/atomic write semantics, post-check and rollback/recovery metadata before live apply. |
| `WAPI-T15` | Public-route hardening is assumed for private/local routes | important | Rate-limit/Helmet-style controls belong to public-route taxonomy and a separate public gate before exposure. |

## Required Test Classes

Before any AMN2 implementation plan for write API routes, require local tests for:

- route/auth/scope bindings for every proposed route;
- read-only tokens rejected for every write/config/destructive action;
- broad/admin-equivalent token scopes rejected unless a separate policy explicitly allows them;
- fake-runner execution path with no SSH and no live command construction;
- `live_write_authorized: no` marker enforced in docs/status/evidence for local slices;
- idempotency key reuse and duplicate request behavior;
- per-target lock conflict behavior;
- one-operation-at-a-time serialization per server/protocol/write surface;
- partial-failure statuses for `local_changed_remote_failed`, `remote_changed_local_failed`, `deferred` and `rolled_back`;
- future atomic-write contract tests for temp write, validation, replace, post-check and rollback metadata before any live config mutation;
- client lifecycle vocabulary tests for `active`, `disabled` and optional `expiresAt` without implying live peer mutation;
- audit redaction for tokens, configs, keys, PSK, QR, `vpn://`, endpoint values, Authorization headers and raw command output;
- config delivery decoupling: client/peer creation must not return `.conf`, QR, `vpn://`, archive, share link or download URL;
- QR and `vpn://` import compatibility tests only inside a secret-read/config gate;
- operation status safe-field contract;
- rate-limit/public hardening tests only if a route is classified as `public-exposure`;
- public exposure marker scan for API `3040`, direct public web/admin `3030`, TCP `80/443` and Caddy/HTTPS/domain cutover;
- license-boundary scan that blocks copied upstream code/templates/scripts/command strings.

## WAPI-V002 Handoff

`WAPI-V002` was selected next and later closed as docs-only route taxonomy:

```text
slice_id: WAPI-V002
slice_name: write API route taxonomy
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
live_vps_commands: no
```

`WAPI-V002` should classify future route names into:

- `clients`;
- `peers`;
- `configs`;
- `operations`;
- `audit/status`.

Each proposed route must be marked as one or more of:

- `read-only`;
- `state-write`;
- `secret-read`;
- `destructive`;
- `public-exposure`.

Route taxonomy did not add runtime routes, OpenAPI exposure, config delivery or live mutation. Current next recommendation after `WAPI-V002` closure is `WAPI-V003` local fake-runner contract with `live_write_authorized: no`.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: WAPI-V002 docs-only route taxonomy with live_write_authorized: no
no_go_scope: runtime route expansion, live write, public exposure, config delivery, SSH/VPS commands, production mutation
defer_scope: any request that requires P4-NG-WRITE-API-LIVE-GATE, NG-V001, public/config gate or destructive-operation gate
```

## Safety Statement

No AMN2 code, live VPS command, SSH command, package apply, route expansion, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` CRUD, Local Agent mutation, token issue/revoke/rotate route, backup/import/reboot or production peer/user mutation was performed.
