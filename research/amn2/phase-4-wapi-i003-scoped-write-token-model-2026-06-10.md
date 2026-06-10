# Phase 4 WAPI-I003: scoped write-token model 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `WAPI-I003` как AMN3 docs-only scoped write-token model для будущего write API. Документ определяет минимальные future scopes, запрет broad admin-equivalent tokens, связь scope-ов с operation status/audit и тестовые требования до любой AMN2 route, token issue/revoke implementation, fake-runner code или live/write gate.

## Decision

```text
slice_id: WAPI-I003
slice_name: scoped write-token model
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
runner_code_changed: no
token_issue_route_implemented: no
token_revoke_route_implemented: no
token_storage_changed: no
generated_openapi_artifact: no
public_openapi_docs_exposure: no
config_delivery: no
production_mutation: no
live_vps_commands: no
ssh_commands: no
required_gate_for_live_write: P4-WRITE-API-LIVE-GATE
selected_next_slice: WAPI-I002 decouple config delivery from client creation
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
selected_next_slice_status: completed in research/amn2/phase-4-wapi-i002-config-delivery-decoupling-2026-06-10.md
```

## Sources Reused

- `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v005-write-api-audit-redaction-requirements-2026-06-10.md`;
- `research/amn2/phase-4-wapi-i004-operation-status-model-2026-06-10.md`;
- `research/amn2/phase-4-api-token-lifecycle-boundary-implementation-2026-06-09.md`;
- `research/amn2/transfer-backlog.md`.

KYORESUAS and PRVTPRO remain product/architecture signals only. No upstream code, route layout, command strings, service logic, UI, templates, workflows or manager implementations are copied.

## VPS Evidence Boundary

Previous VPS work does not change token authority. Historical labels such as `dry_run_only_pass`, `verified_live_single_disposable_peer` and `service_mode_loopback_baseline` may inform audit/status wording, but they do not grant write scopes, config scopes or live-runner permission.

Scoped tokens must not embed or expose live endpoints, SSH aliases, hostnames, IPs, ports, peer keys, `.env`, `servers.yml`, configs, QR payloads, `vpn://`, command output or logs.

## Token Model Goal

Future write API tokens must be:

- scope-minimal;
- owner/actor-bound;
- expiry-bound;
- hash/digest-only at rest;
- one-time raw display only at issue time;
- explicit about write/config/destructive boundaries;
- blocked from acting as broad admin-equivalent access;
- auditable with safe metadata only.

This slice does not create token issue/revoke routes and does not change existing token storage.

## Scope Classes

Future scopes are classified into five groups:

| Scope class | Purpose | Default status |
| --- | --- | --- |
| `read` | current safe aggregate/status read access | existing/current baseline for `server:read`, `metrics:read` |
| `write-plan` | create local operation plans without live mutation | future docs/local implementation only |
| `write-live` | perform remote/live mutation | blocked until `P4-WRITE-API-LIVE-GATE` |
| `secret-read` | return `.conf`, QR, `vpn://` or config artifacts | blocked until separate secret-read/config gate |
| `destructive` | backup/import/reboot/service/proxy/firewall mutation | blocked until separate destructive gate |

No token may silently combine these classes into admin-equivalent behavior.

## Proposed Minimal Scopes

Future candidate scopes:

| Scope | Class | Allows | Does not allow |
| --- | --- | --- | --- |
| `server:read` | `read` | current server/status/integration/local-agent read routes | write, config, peer mutation |
| `metrics:read` | `read` | current aggregate metrics/users summary | per-peer/per-user secrets or writes |
| `client:plan` | `write-plan` | validate client request and create safe operation plan | live peer apply, config output |
| `client:write` | `write-plan` | future local client metadata/status planning | live peer mutation, config output |
| `client:disable` | `write-plan` | future local disable operation plan | live revoke/apply without gate |
| `client:revoke` | `write-plan` | future local revoke operation plan | live peer revoke without gate |
| `peer:plan` | `write-plan` | future peer apply/revoke dry-run/plan | live peer mutation |
| `peer:apply` | `write-live` | future live apply only under named gate | default/local execution |
| `peer:revoke` | `write-live` | future live revoke only under named gate | default/local execution |
| `peer:sync` | `write-live` or gated read-reconcile | future sync only after explicit design | backfill/delete/mutate by default |
| `config:prepare` | `secret-read` | future prepare config artifact inside secret gate | return secret payload by default |
| `config:read` | `secret-read` | future read/download config inside secret gate | public/self-service exposure by default |
| `operation:read` | `read` | read safe operation status | raw audit, secrets, command output |
| `operation:retry` | `write-plan` | future retry plan under idempotency/lock rules | bypass live gate |
| `operation:cancel` | `write-plan` | future local cancel plan/status change | cancel live operation without queue design |
| `audit:read` | `read` | future safe audit/status read model | raw audit payloads or secret-bearing fields |
| `token:issue` | `destructive` by policy | not enabled by this slice | creating tokens via API route |
| `token:revoke` | `destructive` by policy | not enabled by this slice | revoking production tokens via API route |

`token:issue` and `token:revoke` remain design placeholders only. A future token lifecycle API must be its own gate and must not be bundled into `/api/clients`.

## Forbidden Scope Patterns

Future implementation must reject:

- `admin`;
- `admin:*`;
- `*`;
- `write:*`;
- `client:*`;
- `peer:*`;
- `config:*`;
- `operation:*`;
- any scope that combines read, write, secret-read, public-exposure and destructive permissions without explicit per-scope listing;
- any scope that grants config delivery as a side effect of client creation;
- any scope that grants live peer mutation while `live_write_authorized=no`;
- any scope that grants backup/import/reboot/service/firewall/proxy mutation from write API token.

## Scope Combination Rules

Allowed in future local/default planning mode:

- `server:read` plus `metrics:read`;
- `client:plan` plus `operation:read`;
- `client:write` plus `operation:read`;
- `client:disable` plus `operation:read`;
- `client:revoke` plus `operation:read`;
- `peer:plan` plus `operation:read`;
- `operation:retry` plus `operation:read` only when idempotency and lock rules pass.

Blocked in default planning mode:

- any `write-live` scope with actual live execution;
- any `secret-read` scope returning payload;
- any destructive scope;
- public/self-service scope combinations;
- token lifecycle scope combinations.

If a token has more scopes than an operation requires, the operation must still evaluate the minimal required scope and audit that exact scope. Extra scopes must not cause implicit side effects.

## Token Lifecycle Requirements

Future scoped write tokens must inherit existing lifecycle boundaries:

- explicit expiry required;
- digest/hash-only storage;
- raw token displayed once only;
- owner/actor binding required;
- revoke must be idempotent;
- rotation means create-new-then-revoke-old;
- no raw token, token hash, Authorization header or token prefix/suffix in audit/status/error output.

This slice does not issue, revoke, rotate or store any token.

## Binding To WAPI Status And Audit

Future audit/status must record:

- `requested_scope`;
- `required_scope`;
- `scope_class`;
- `token_class`;
- `scope_decision: allowed | denied | deferred`;
- `reason_code` such as `scope_denied`, `read_only_token`, `live_write_blocked`, `config_delivery_blocked` or `destructive_operation_blocked`;
- `live_write_authorized=no` in docs/local/default mode.

Audit/status must not record raw tokens, token hashes, Authorization headers or raw request bodies.

## Required Tests Before Implementation

Any future AMN2 implementation plan for write API auth, token checks, routes or operation planning must start with RED tests for:

- read-only scopes reject write/config/destructive actions;
- `client:write` cannot return `.conf`, QR, `vpn://` or config download link;
- `client:revoke` cannot execute live peer revoke while `live_write_authorized=no`;
- `peer:apply` and `peer:revoke` are blocked/deferred without named live gate;
- `operation:retry` cannot bypass idempotency, target lock or live gate;
- `config:read` and `config:prepare` remain blocked without secret-read/config gate;
- broad scopes such as `admin`, `admin:*`, `*`, `client:*`, `peer:*`, `config:*` and `write:*` are rejected;
- token audit records `required_scope`, `requested_scope`, `scope_class` and safe reason code;
- audit/status/error output excludes raw token, token hash, Authorization header and raw request body;
- token issue/revoke API routes are absent unless a separate token lifecycle gate is selected;
- live/write scopes cannot produce `succeeded` status in fake/default mode;
- destructive scopes cannot be used for backup/import/reboot/service/firewall/proxy mutation.

## WAPI-I002 Handoff

`WAPI-I002` was selected next and later closed as docs-only config delivery decoupling:

```text
slice_id: WAPI-I002
slice_name: decouple config delivery from client creation
slice_mode: docs-only
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
live_vps_commands: no
```

It makes the config-delivery boundary explicit before `/api/clients` design: client/peer creation may create a safe operation plan, but `.conf`, QR, `vpn://`, archives, share links and downloads require a separate secret-read/config gate. `WAPI-I001` was then closed as docs-only `/api/clients` design without live CRUD; `WAPI-I005` was then closed as web-panel gated action labels; `NG-N003` was then closed as docs-only operation queue design after write API contract; `NG-N002` was then closed as docs-only health/status polling design; `NG-N001` was then closed as docs-only attach-existing-server read-only reconciliation gate design. `NG-N004` was then closed as docs-only candidate registry update after every gate decision. `NG-S001` was then closed as docs-only status/transfer synchronization. `NG-S002` and `NG-S004` were then closed together as docs-only handoff and visible-plan maintenance. Current next recommendation after `NG-S002`/`NG-S004` closure is `NG-X003` stale wording cleanup with `live_write_authorized: no`.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: WAPI-I002 docs-only config-delivery decoupling model with live_write_authorized: no
no_go_scope: write API route implementation, token issue/revoke route implementation, fake-runner code implementation, runtime route expansion, live write, public exposure, config delivery, SSH/VPS commands, production mutation
defer_scope: AMN2 route implementation, live peer mutation, config/read-delivery routes, public/self-service routes, destructive operations, token lifecycle API routes
```

## Safety Statement

No AMN2 code, token issue/revoke route, token storage change, fake-runner code, live VPS command, SSH command, shell command, package apply, route expansion, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.
