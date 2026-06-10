# Phase 4 WAPI-I001: /api/clients design without live CRUD 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `WAPI-I001` как AMN3 docs-only design contract для будущего `/api/clients` surface. Документ описывает безопасные request/response границы, scopes, statuses, idempotency, audit/redaction and test obligations before any AMN2 runtime route, write CRUD, fake-runner code or live runner implementation.

## Decision

```text
slice_id: WAPI-I001
slice_name: /api/clients design without live CRUD
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
runner_code_changed: no
client_routes_implemented: no
write_crud_implemented: no
fake_runner_implemented: no
operation_queue_implemented: no
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
required_gate_for_route_implementation: P4-NG-WAPI-CLIENTS-LOCAL-IMPLEMENTATION-GATE
required_gate_for_live_write: P4-NG-WRITE-API-LIVE-GATE
required_gate_for_config_delivery: P4-NG-CONFIG-DELIVERY-GATE
selected_next_slice: WAPI-I005 web-panel gated action labels
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
selected_next_slice_status: completed in research/amn2/phase-4-wapi-i005-web-panel-gated-action-labels-2026-06-10.md
```

## Sources Reused

- `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v005-write-api-audit-redaction-requirements-2026-06-10.md`;
- `research/amn2/phase-4-wapi-i004-operation-status-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-i003-scoped-write-token-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-i002-config-delivery-decoupling-2026-06-10.md`;
- `research/amn2/phase-4-web-panel-user-config-visibility-implementation-2026-06-09.md`;
- `research/amn2/transfer-backlog.md`.

KYORESUAS and PRVTPRO remain product/architecture signals only. No upstream code, route layout, command strings, service logic, UI, templates, workflows or manager implementations are copied.

## VPS Evidence Boundary

Previous VPS work remains historical evidence only:

- Phase 1 `dry_run_only_pass`;
- Phase 2 single disposable peer `verified_live_single_disposable_peer`;
- Phase 3 `service_mode_loopback_baseline`;
- current service-mode boundary `vps_apply_disabled`.

These labels do not authorize live CRUD, live peer apply/revoke/sync, config generation, config delivery, token lifecycle API routes, Local Agent mutation or public exposure. This slice did not query the VPS and did not run SSH.

Evidence, future responses, audit and status must not contain live endpoints, SSH aliases, hostnames, IPs, ports, peer keys, private keys, PSK, `.env`, `servers.yml`, command output, logs, `.conf`, QR payloads, QR images, `vpn://`, archive paths, share links or download URLs.

## Design Boundary

`/api/clients` is a future candidate surface. In this slice it is only a contract, not an implementation.

Default meaning:

- `client` means an opaque local AMN2-managed client/device/user-facing configuration record or operation target;
- `peer` means the VPN/server-side runtime object, which may exist independently from AMN2 local metadata;
- live peers created outside AMN2 must not be silently backfilled into managed `/api/clients` write state;
- config artifacts are separate `config` resources and remain blocked behind `P4-NG-CONFIG-DELIVERY-GATE`;
- remote peer mutation remains blocked behind `P4-NG-WRITE-API-LIVE-GATE`.

This keeps the earlier web-panel visibility finding intact: live VPS peers visible through read-only inventory are not automatically the same thing as local AMN2 users/devices/configurations.

## Candidate Route Contract

Candidate names are planning placeholders only:

| Candidate route | Class | Minimal scope | Default side effect | Default result boundary |
| --- | --- | --- | --- | --- |
| `GET /api/clients` | `read-only` | `client:read` | none | local safe metadata list only |
| `GET /api/clients/{client_id}` | `read-only` | `client:read` | none | one local safe metadata record only |
| `POST /api/clients` | `state-write` | `client:write` | future local operation plan only | `planned`, `deferred` or `rejected`; no config |
| `PATCH /api/clients/{client_id}` | `state-write` | `client:write` | future local metadata/status plan only | no live peer mutation |
| `POST /api/clients/{client_id}:disable` | `state-write` | `client:disable` | future local disabled-state plan only | live peer disable blocked |
| `POST /api/clients/{client_id}:revoke` | `state-write` | `client:revoke` | future revoke operation plan only | live peer revoke blocked |

No candidate route becomes runtime behavior until a later AMN2 local implementation gate is selected. A future implementation may split, rename or reduce these candidate names, but it must preserve this safety boundary.

## Safe Client Read Model

Future client read responses may include only safe metadata:

| Field | Meaning |
| --- | --- |
| `client_ref` | opaque local client reference |
| `display_name` | operator/user-facing non-secret label |
| `owner_ref` | opaque owner/user reference, not raw personal data unless separately classified |
| `device_ref` | opaque local device reference |
| `lifecycle_state` | `planned`, `active`, `disabled`, `revoked`, `expired`, `unknown` or later controlled value |
| `expires_at` | optional lifecycle timestamp |
| `created_at` | local server timestamp |
| `updated_at` | local server timestamp |
| `source_type` | `local_metadata`, `operation_plan`, `read_only_inventory_reference` or controlled later value |
| `operation_ref` | latest safe operation id, if present |
| `operation_status` | safe status from WAPI-I004 |
| `config_delivery_status` | `not_requested`, `blocked`, `deferred` or later gated value |
| `config_delivery_required_gate` | `P4-NG-CONFIG-DELIVERY-GATE` when applicable |
| `live_write_authorized` | `no` in default/local/docs mode |

Future responses must not include:

- `.conf`;
- QR payload or image;
- `vpn://`;
- private key;
- PSK;
- peer public key;
- server endpoint, hostname, IP, port or live path;
- raw peer id from live runtime;
- raw config path;
- archive path;
- share or download URL;
- raw request body;
- raw command output or logs.

## Safe Write Request Model

Future write requests must be narrow and idempotent.

Allowed request fields:

- `display_name`;
- `owner_ref` or a safe local owner reference;
- `device_ref` or a safe local device reference;
- `expires_at`;
- `lifecycle_intent: create | update | disable | revoke`;
- `dry_run`;
- `idempotency_key`;
- `correlation_id`;
- controlled non-secret labels or notes after explicit classification.

Forbidden request fields:

- private key, PSK or peer public key;
- `.conf`, QR, `vpn://` or config body;
- server endpoint, host, IP, SSH alias, username, port or live path;
- shell command, raw runner payload or raw logs;
- token, Authorization header, token hash or session secret;
- backup/import payload.

`POST /api/clients` must not be a hidden config generation route. `PATCH`, `:disable` and `:revoke` must not be hidden live peer mutation routes.

## Default Response Shapes

Future default create/update/disable/revoke responses may return:

```text
operation_id: opaque
client_ref: opaque
operation_type: client_create | client_update | client_disable | client_revoke
operation_class: state-write
status: planned | dry_run_passed | dry_run_failed | rejected | deferred | locked | conflict | idempotency_replay | idempotency_conflict
reason_code: controlled safe reason code
runner_mode: none | fake
dry_run: true | false
live_write_authorized: no
local_mutation_performed: false or future local metadata-only marker
remote_mutation_performed: false
config_delivery_status: blocked | deferred | not_requested
config_delivery_required_gate: P4-NG-CONFIG-DELIVERY-GATE
operation_status_url: optional private/local candidate link only after route implementation gate
```

Default/local/docs mode must not return `running` or `succeeded`, because no live runner is authorized. It may return `planned`, `dry_run_passed`, `dry_run_failed`, `rejected`, `deferred`, `locked`, `conflict`, `idempotency_replay` or `idempotency_conflict`.

## Scope And Gate Rules

Future scope requirements:

- `client:read` for client list/detail read metadata;
- `client:write` for create/update local planning;
- `client:disable` for disable planning;
- `client:revoke` for revoke planning;
- `operation:read` for operation status references;
- `config:read` and `config:prepare` remain separate secret-read scopes and are not implied by any client scope.

Blocked scope patterns remain blocked:

- `admin`;
- `admin:*`;
- `*`;
- `write:*`;
- `client:*`;
- `peer:*`;
- `config:*`;
- any broad token that turns `/api/clients` into admin-equivalent access.

`client:write` plus `config:read` still requires separate write/live and config gates before any sensitive output. `client:revoke` still requires live write gate before remote peer revoke.

## Idempotency And Locks

Future state-write candidate routes must require:

- `idempotency_key` for `POST /api/clients`, `PATCH /api/clients/{client_id}`, `:disable` and `:revoke`;
- request fingerprint digest from non-secret normalized fields;
- per-target lock such as `client:{client_ref}` or a safe pre-create lock derived from non-secret owner/device fields;
- `idempotency_replay` for exact replay;
- `idempotency_conflict` for same key with different fingerprint;
- `locked` for concurrent target mutation.

Idempotency data must never store raw tokens, raw request bodies, config bodies, endpoint values or live identifiers.

## Audit And Status Binding

Future `/api/clients` actions must emit safe audit/status metadata compatible with WAPI-V005 and WAPI-I004:

- `event_type: write_request_received | write_request_rejected | operation_planned | operation_deferred | config_delivery_blocked`;
- `route_group: clients`;
- `operation_type: client_create | client_update | client_disable | client_revoke`;
- `operation_class: read-only | state-write`;
- `requested_scope`;
- `required_scope`;
- `scope_decision: allowed | denied | deferred`;
- `target_ref_type: client`;
- `target_ref` as opaque local reference only;
- `gate_name` when blocked/deferred;
- `live_write_authorized: no`;
- `runner_mode: none | fake`;
- `local_mutation_performed`;
- `remote_mutation_performed: false`;
- `reason_code`.

Audit/status/error output must never include config artifacts, token material, live target identifiers, raw request bodies, raw command output or logs.

## Required Tests Before Implementation

Any future AMN2 implementation plan for `/api/clients` must start with RED tests for:

- candidate routes are absent until an explicit AMN2 local implementation gate selects them;
- `GET /api/clients` and `GET /api/clients/{client_id}` return safe metadata only;
- read-only client responses exclude `.conf`, QR, `vpn://`, private key, PSK, peer public key, endpoint, host/IP/port and live path;
- read-only `server:read` or `metrics:read` scopes cannot access client write candidates;
- `client:read` cannot create, update, disable, revoke or read config artifacts;
- read-only tokens reject every write/config/destructive client candidate;
- `POST /api/clients` requires idempotency key before any future local mutation;
- duplicate idempotency key with same fingerprint returns safe replay;
- duplicate idempotency key with different fingerprint returns `idempotency_conflict`;
- concurrent mutation of the same target returns `locked`;
- `POST /api/clients` cannot return `.conf`, QR, `vpn://`, archive, share link or download URL;
- `PATCH`, `:disable` and `:revoke` cannot perform live peer mutation while `live_write_authorized=no`;
- fake/default mode cannot produce `running` or `succeeded`;
- fake/default mode sets `remote_mutation_performed=false`;
- config delivery attempts return `deferred` or `rejected` with safe `config_delivery_blocked` or `secret_read_gate_required`;
- live peers discovered outside AMN2 are not silently backfilled as managed clients without a separate reconciliation/import gate;
- audit/status/error output excludes raw token, token hash, Authorization header, raw idempotency key, raw request body, config artifacts, endpoint data, command output and logs;
- route drift tests keep implementation, docs and policy registry aligned;
- public OpenAPI/docs exposure remains absent unless a separate public-docs gate is selected.

## WAPI-I005 Handoff

`WAPI-I005` was selected next and later closed as docs-only web-panel gated action labels:

```text
slice_id: WAPI-I005
slice_name: web-panel gated action labels
slice_mode: docs-only
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
live_vps_commands: no
config_delivery: no
```

It uses this `/api/clients` contract to define how future web/admin labels distinguish read-only metadata, local operation planning, deferred live write, blocked config delivery and separately gated destructive/public actions. `NG-N003` was then closed as docs-only operation queue design after write API contract. `NG-N002` was then closed as docs-only health/status polling design. `NG-N001` was then closed as docs-only attach-existing-server read-only reconciliation gate design. `NG-N004` was then closed as docs-only candidate registry update after every gate decision. `NG-S001` was then closed as docs-only status/transfer synchronization. `NG-S002` and `NG-S004` were then closed together as docs-only handoff and visible-plan maintenance. `NG-X003` was then closed as docs-only stale wording cleanup. `NG-X001` was then closed as docs-only gate naming consistency. Current next recommendation after `NG-X001` closure is `NG-X002` Russian-first operator wording polish with `live_write_authorized: no`.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: WAPI-I005 docs-only web-panel gated action labels with live_write_authorized: no
no_go_scope: AMN2 route implementation, `/api/clients` runtime CRUD, fake-runner code implementation, operation queue implementation, token issue/revoke route implementation, config delivery route implementation, live write, public exposure, SSH/VPS commands, production mutation
defer_scope: AMN2 local implementation gate, live peer mutation, config/read-delivery routes, public/self-service routes, destructive operations, token lifecycle API routes, OpenAPI public exposure
```

## Safety Statement

No AMN2 code, runtime route, `/api/clients` CRUD, fake-runner code, operation queue, config delivery route, token issue/revoke route, token storage change, live VPS command, SSH command, shell command, package apply, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config generation, config delivery, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.
