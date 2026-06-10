# Phase 4 WAPI-I002: config delivery decoupling 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `WAPI-I002` как AMN3 docs-only контракт, который отделяет future client/peer creation от выдачи `.conf`, QR, `vpn://`, архивов, share/download links и любых secret-bearing config artifacts. Документ нужен перед будущим `/api/clients` design, чтобы client creation не стал скрытым config delivery endpoint.

## Decision

```text
slice_id: WAPI-I002
slice_name: decouple config delivery from client creation
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
runner_code_changed: no
token_issue_route_implemented: no
token_revoke_route_implemented: no
config_delivery_route_implemented: no
config_generation_changed: no
generated_openapi_artifact: no
public_openapi_docs_exposure: no
config_delivery: no
production_mutation: no
live_vps_commands: no
ssh_commands: no
required_gate_for_config_delivery: P4-CONFIG-DELIVERY-GATE
required_gate_for_live_write: P4-WRITE-API-LIVE-GATE
selected_next_slice: WAPI-I001 /api/clients design without live CRUD
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
selected_next_slice_status: completed in research/amn2/phase-4-wapi-i001-clients-design-without-live-crud-2026-06-10.md
```

## Sources Reused

- `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v005-write-api-audit-redaction-requirements-2026-06-10.md`;
- `research/amn2/phase-4-wapi-i004-operation-status-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-i003-scoped-write-token-model-2026-06-10.md`;
- `research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md`;
- `research/amn2/public-config-delivery-policy-contract-implementation.md`;
- `research/amn2/transfer-backlog.md`.

KYORESUAS and PRVTPRO remain product/architecture signals only. No upstream code, route layout, command strings, service logic, UI, templates, workflows or manager implementations are copied.

## VPS Evidence Boundary

Previous VPS work may be referenced only as historical safe evidence labels:

- `dry_run_only_pass`;
- `verified_live_single_disposable_peer`;
- `service_mode_loopback_baseline`;
- `vps_apply_disabled`;
- `live_write_blocked`.

These labels do not grant client write scope, config-read scope, live-runner permission, public exposure or config delivery permission. This slice did not run SSH, did not query VPS state and did not fetch or generate config artifacts.

Evidence, audit, status and docs must not contain live endpoints, SSH aliases, hostnames, IPs, ports, peer keys, private keys, PSK, `.env`, `servers.yml`, command output, logs, `.conf`, QR payloads, QR images, `vpn://`, archive paths, share links or download URLs.

## Core Rule

Future client/peer creation must create only a safe local operation record or operation plan. It must not automatically publish or return any secret-bearing config artifact.

Allowed by future client/peer creation design:

- opaque `operation_id`;
- opaque `client_ref` or `target_ref`;
- safe operation status such as `planned`, `dry_run_passed`, `deferred`, `rejected`, `locked` or `conflict`;
- safe reason codes from WAPI-I004;
- safe audit correlation metadata from WAPI-V005;
- explicit marker that config delivery is blocked or requires a separate gate.

Forbidden as a side effect of client/peer creation:

- client `.conf`;
- QR payload or QR image;
- `vpn://`;
- private key;
- PSK;
- peer public key;
- server endpoint, hostname, IP, port or live path;
- generated archive;
- public share link;
- download URL;
- raw file path;
- raw command output or logs.

## Route And Scope Separation

| Future action | Minimal scope class | Allowed output in default mode | Blocked output/action |
| --- | --- | --- | --- |
| `client_create` | `client:write` or `client:plan` | safe operation/client metadata only | `.conf`, QR, `vpn://`, live peer mutation |
| `client_revoke` | `client:revoke` | safe operation metadata only | live revoke without gate, config artifact |
| `peer_plan_apply` | `peer:plan` | dry-run/plan metadata only | live apply, config artifact |
| `peer_apply` | `peer:apply` | blocked/deferred until live gate | live mutation in default mode |
| `config_prepare` | `config:prepare` | blocked/deferred until config gate | config generation/delivery by default |
| `config_read` | `config:read` | blocked/deferred until config gate | `.conf`, QR, `vpn://` by default |
| public/self-service config share | separate public/config gate | not allowed by this slice | public endpoint, share link, download URL |

`client:write`, `client:revoke`, `peer:plan` or `peer:apply` must not imply `config:read`. `config:read` or `config:prepare` must not imply client write, peer write or destructive capability. A token that has both write and config scopes must still pass both the write/live gate and the secret-read/config gate before any sensitive output.

## Future Response Contract

A future local/default `POST /api/clients` design may return a safe shape like:

```text
operation_id: opaque
client_ref: opaque
status: planned | deferred | rejected | locked | conflict | dry_run_passed | dry_run_failed
operation_class: state-write
live_write_authorized: no
config_available: false
config_delivery_status: blocked | deferred
config_delivery_required_gate: P4-CONFIG-DELIVERY-GATE
reason_code: config_delivery_blocked | live_write_blocked | scope_denied | ...
```

It must not return:

- `config`;
- `conf`;
- `qr`;
- `qr_png`;
- `vpn_url`;
- `vpn://`;
- `private_key`;
- `preshared_key`;
- `public_key`;
- `endpoint`;
- `host`;
- `port`;
- `download_url`;
- `share_url`;
- `archive_path`;
- raw request or runner output.

The exact field names can change during future AMN2 implementation design, but the boundary cannot: client creation response must be non-secret by default.

## Audit And Status Binding

Future audit/status for a blocked config output attempt must use safe metadata only:

- `event_type: config_delivery_blocked`;
- `operation_class: secret-read` or `state-write` plus blocked config marker;
- `requested_scope`;
- `required_scope: config:read` or `config:prepare`;
- `scope_decision: denied | deferred`;
- `reason_code: config_delivery_blocked | secret_read_gate_required | public_config_blocked | ownership_required | expiry_required`;
- `gate_name: P4-CONFIG-DELIVERY-GATE`;
- `live_write_authorized: no`;
- `local_mutation_performed: false` unless a later approved local planning implementation explicitly records local metadata;
- `remote_mutation_performed: false`.

Audit/status/error output must never include secret-bearing config artifacts or live target identifiers.

## Required Tests Before Implementation

Any future AMN2 implementation plan for `/api/clients`, config routes, scoped token checks or operation planning must start with RED tests for:

- `POST /api/clients` cannot return `.conf`, QR, `vpn://`, config archive, share link or download URL;
- `client:write` alone cannot read, prepare or deliver config artifacts;
- `client:revoke` alone cannot read, prepare or deliver config artifacts;
- `config:read` alone cannot create, revoke, sync or mutate a client/peer;
- a blocked config delivery attempt returns safe `deferred` or `rejected` status with `config_delivery_blocked` or `secret_read_gate_required`;
- public/self-service config route remains absent or blocked until a separate public/config gate;
- audit/status/error output excludes raw token, token hash, Authorization header, `.conf`, QR, `vpn://`, private key, PSK, peer public key, endpoint, host/IP/port, command output and logs;
- fake/default mode cannot trigger config generation or live VPS operations;
- combined write/config scopes still require explicit gate checks and safe audit metadata;
- OpenAPI/docs generation, if later added, does not expose public config delivery by default.

## WAPI-I001 Handoff

`WAPI-I001` was selected next and later closed as docs-only `/api/clients` design without live CRUD:

```text
slice_id: WAPI-I001
slice_name: /api/clients design without live CRUD
slice_mode: docs-only
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
live_vps_commands: no
config_delivery: no
```

It uses this `WAPI-I002` boundary as an invariant: future `/api/clients` may describe safe request/response shapes and operation planning states, but must not implement runtime routes, write CRUD, live runner calls or config delivery unless a separate selected implementation gate exists. `WAPI-I005` was then closed as web-panel gated action labels. Current next recommendation after `WAPI-I005` closure is `NG-N003` operation queue design after write API contract with `live_write_authorized: no`.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: WAPI-I001 docs-only /api/clients design without live CRUD, preserving config-delivery decoupling and live_write_authorized: no
no_go_scope: write API route implementation, config delivery route implementation, token issue/revoke route implementation, fake-runner code implementation, runtime route expansion, live write, public exposure, SSH/VPS commands, production mutation
defer_scope: AMN2 route implementation, live peer mutation, config/read-delivery routes, public/self-service routes, destructive operations, token lifecycle API routes, OpenAPI public exposure
```

## Safety Statement

No AMN2 code, runtime route, config delivery route, token issue/revoke route, token storage change, fake-runner code, live VPS command, SSH command, shell command, package apply, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config generation, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.
