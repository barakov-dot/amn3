# Phase 4 NG-N003: operation queue design after write API contract 2026-06-10

Purpose: close `NG-N003` as an AMN3 docs-only operation queue contract after the WAPI write API design chain. This document defines how a future queue/cancel/retry/status layer must behave before any AMN2 route, worker, queue runner or live operation implementation exists.

## Decision

```text
slice_id: NG-N003
slice_name: operation queue design after write API contract
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
queue_implemented: no
worker_implemented: no
runner_code_changed: no
operation_status_schema_implemented: no
client_routes_implemented: no
write_crud_implemented: no
fake_runner_implemented: no
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
required_gate_for_queue_implementation: P4-WAPI-OPERATION-QUEUE-LOCAL-IMPLEMENTATION-GATE
required_gate_for_live_write: P4-WRITE-API-LIVE-GATE
required_gate_for_config_delivery: P4-CONFIG-DELIVERY-GATE
selected_next_slice: NG-N002 health/status polling design
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
selected_next_slice_status: completed in research/amn2/phase-4-ng-n002-health-status-polling-design-2026-06-10.md
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
- `research/amn2/phase-4-wapi-i001-clients-design-without-live-crud-2026-06-10.md`;
- `research/amn2/phase-4-wapi-i005-web-panel-gated-action-labels-2026-06-10.md`;
- `research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-10.md`;
- `research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md`.

Upstream repositories remain research-only idea sources. No GPL or upstream code, templates, manager implementations, workflows or service code were copied.

## VPS Evidence Boundary

Historical Phase 3 service-mode and VPS smoke evidence may be referenced only as previously accepted safety context. `NG-N003` did not run SSH, VPS shell commands, package commands, service commands, firewall commands, tunnel commands or API calls against the live host.

The current operation queue contract is local/docs-only. It cannot be interpreted as approval to create, revoke, disable, sync, apply or deliver production peer configuration.

## Queue Goal

The future queue is an intent scheduling and status layer, not authorization by itself.

It must:

- preserve the WAPI operation model based on `operation_id`, `correlation_id`, idempotency, locks, safe status, reason codes and redacted audit events;
- represent local plans, dry-run outcomes and deferred gated work without pretending that live work happened;
- keep config delivery, public exposure, token issue/revoke and destructive operations behind separate gates;
- make "blocked by gate" and "queued for future execution" visibly different states.

It must not:

- execute live writes in default mode;
- expose secret-bearing artifacts;
- bypass named gates through retry/cancel paths;
- convert panel labels into authorization;
- infer production state from stale local queue entries.

## Queue Entity Contract

Future queue records should use safe fields only:

```text
operation_id
queue_item_id
correlation_id
operation_type
operation_class
target_ref
target_ref_type
actor_ref
requested_scope
required_scope
idempotency_key_digest
request_fingerprint_digest
lock_scope
status
reason_code
gate_name
runner_mode
dry_run
live_write_authorized
local_mutation_performed
remote_mutation_performed
created_at
updated_at
not_before
attempt_count
max_attempts
parent_operation_id
audit_event_ref
```

Forbidden fields:

```text
raw_token
token
token_hash
authorization_header
private_key
public_key
preshared_key
psk
client_config
wireguard_config
outline_config
vpn_url
vpn_uri
qr
conf
archive
download_url
share_url
endpoint
host
ip
port
ssh_command
shell_command
env
servers_yml
stdout
stderr
traceback
```

`target_ref` and `actor_ref` must be opaque references. They must not leak peer public keys, user identifiers, raw hostnames, IP addresses, ports or secrets.

## Queue Lifecycle

Default docs/local-only lifecycle:

```text
received -> rejected
received -> accepted
accepted -> planned
planned -> dry_run_passed
planned -> dry_run_failed
planned -> deferred
planned -> locked
locked -> planned
locked -> deferred
deferred -> planned
```

Future implementation-only lifecycle, blocked until a separate queue implementation gate:

```text
dry_run_passed -> queued_for_execution
queued_for_execution -> running
running -> succeeded
running -> failed
running -> partial
partial -> recovery_planned
recovery_planned -> recovery_succeeded
recovery_planned -> recovery_failed
```

In the current default mode:

- `queued_for_execution`, `running`, `succeeded`, `partial` and recovery statuses are forbidden as real outcomes;
- a live-write candidate must stop at `deferred` with a gate reason;
- a config delivery candidate must stop at `deferred` or `rejected`;
- a destructive candidate must stop at `rejected` unless a future named gate explicitly changes the policy.

## Operation Classes

```text
read_only_status_query
local_plan
dry_run_plan
live_write_blocked
config_delivery_blocked
public_exposure_blocked
destructive_blocked
```

Read-only status queries should generally not be queued. They can produce safe aggregate status, but they must not create mutable operation records unless a future implementation explicitly needs audit-only tracking.

## Enqueue Rules

An enqueue request for mutable work must:

- require a valid idempotency key;
- compute a request fingerprint digest and reject conflicting duplicate keys;
- identify the lock scope before planning mutable work;
- record `live_write_authorized: no` unless a separate live-write gate is open;
- return `deferred` or `rejected`, not `queued_for_execution`, when the required gate is missing;
- emit a redacted audit event with operation id, correlation id, status and reason code only.

An enqueue request must not:

- deliver `.conf`, QR, `vpn://`, archive, share/download URL or any secret-bearing payload;
- issue or revoke tokens;
- start a live worker;
- call Local Agent mutation functions;
- run SSH/VPS commands;
- open public routes or public OpenAPI/docs exposure.

## Retry Rules

Retry must attach to an existing operation and preserve:

- original target reference;
- original operation type and operation class;
- original request fingerprint digest;
- original required gate;
- original idempotency boundary;
- original lock scope.

Retry must reject:

- scope escalation;
- target change;
- request body drift under the same idempotency key;
- attempts to retry a blocked config/public/destructive action into a live action;
- attempts to turn `deferred` into `running` while `live_write_authorized: no`.

In default mode, retry can at most produce a refreshed plan, refreshed dry-run result or renewed `deferred` status.

## Cancel Rules

Cancel can apply only to safe pending states:

```text
planned
dry_run_passed
dry_run_failed
deferred
locked
```

Future `queued_for_execution` cancel semantics require a separate queue implementation gate.

Default cancel must not:

- race a live worker;
- stop remote processes;
- revoke peers;
- revoke tokens;
- delete configs;
- clean up servers;
- mark a live result as successful.

Cancel should produce a safe operation status with a reason such as `cancelled_by_operator` or `cancel_rejected_state_not_cancelable`.

## Ordering And Concurrency

Mutable queue planning must respect locks before execution exists:

- one mutable operation per peer/client target lock;
- one config-generation lock per target when config output is ever introduced by a separate gate;
- one server-level live-apply lock per server when live apply is ever introduced by a separate gate;
- no parallel create/update/disable/revoke against the same target;
- no config delivery racing with lifecycle changes;
- no retry/cancel bypass of the same lock scope.

Queue order is not a permission signal. A blocked item cannot become permitted because it is older, first in queue or repeatedly retried.

## Visibility

Queue visibility is private/local only:

- operator UI/API may show safe status, reason, timestamps, gate name and operation class;
- public exposure is absent;
- peer/user secret identifiers are absent;
- raw request bodies are absent;
- command output and logs are absent;
- only aggregate/safe counts may be used for dashboard summaries.

## Web Panel Label Binding

The label vocabulary from `WAPI-I005` maps to queue states as follows:

```text
planned -> Local plan
dry_run_passed -> Dry-run passed
dry_run_failed -> Dry-run failed
deferred -> Named gate required
locked -> Waiting for lock
rejected -> Blocked
cancelled -> Cancelled
```

Panel labels must not claim that an operation is queued, running or successful in default mode. If a future implementation adds those states, labels must be introduced under a separate implementation gate with RED tests.

## Required RED Tests Before Implementation

Before any AMN2 queue implementation, tests must prove:

- no queue routes exist before the implementation gate;
- missing idempotency key rejects mutable enqueue;
- duplicate idempotency key with same fingerprint replays safely;
- duplicate idempotency key with different fingerprint rejects;
- lock conflict prevents mutable enqueue or returns a safe locked/deferred status;
- `live_write_authorized: no` cannot return `queued_for_execution`, `running` or `succeeded`;
- config delivery candidates cannot return `.conf`, QR, `vpn://`, archive, share/download URL or any secret-bearing artifact;
- retry cannot change target, scope, operation class, fingerprint or gate;
- retry cannot bypass `deferred` gate state;
- cancel cannot cancel a live running operation in default mode;
- cancel cannot perform remote action in default mode;
- status output contains no raw token, token hash, Authorization header, endpoint, host/IP/port, peer public key, private key, PSK, command output, logs, `.env`, `servers.yml`, `.conf`, QR or `vpn://`;
- `succeeded` is impossible in fake/default mode;
- public exposure remains absent.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: NG-N003 docs-only operation queue design after write API contract with live_write_authorized: no
no_go_scope: AMN2 queue implementation, worker implementation, runtime route expansion, `/api/clients` runtime CRUD, token issue/revoke routes, config delivery route, live write, public exposure, SSH/VPS commands, production mutation
defer_scope: AMN2 local queue implementation gate, live peer mutation, config/read-delivery routes, public/self-service routes, destructive operations, token lifecycle API routes, public OpenAPI/docs exposure
```

## Handoff

`NG-N003` is closed. `NG-N002` was selected next and later closed in `research/amn2/phase-4-ng-n002-health-status-polling-design-2026-06-10.md`, because queue/status UX needed a safe polling contract that remains aggregate-only, avoids peer/user leakage and does not call live VPS or write/config surfaces. `NG-N001` was then closed as docs-only attach-existing-server read-only reconciliation gate design. `NG-N004` was then closed as docs-only candidate registry update after every gate decision. `NG-S001` was then closed as docs-only status/transfer synchronization. Current next recommendation after `NG-S001` closure is `NG-S002` keep next-chat handoff current with `live_write_authorized: no`.

## Safety Statement

No AMN2 code, template change, route behavior change, runtime route, `/api/clients` CRUD, fake-runner code, operation queue implementation, worker implementation, config delivery route, token issue/revoke route, token storage change, live VPS command, SSH command, shell command against VPS, package apply, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config generation, config delivery, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.
