# Phase 4 WAPI-V003: local fake-runner contract 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `WAPI-V003` как AMN3 docs-only contract для будущего local fake-runner слоя. Документ определяет безопасный тестовый runner для future write API operation plans, но не добавляет AMN2 runtime routes, не создает runner code, не выполняет SSH/VPS commands и не разрешает live mutation.

## Decision

```text
slice_id: WAPI-V003
slice_name: local fake-runner contract
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
runner_code_changed: no
live_runner_authorized: no
generated_openapi_artifact: no
public_openapi_docs_exposure: no
config_delivery: no
production_mutation: no
live_vps_commands: no
ssh_commands: no
required_gate_for_live_write: P4-WRITE-API-LIVE-GATE
selected_next_slice: WAPI-V004 idempotency, locking and partial-failure model
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
selected_next_slice_status: completed in research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md
```

## Sources Reused

- `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`;
- `research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md`;
- `research/amn2/phase-4-protocol-manager-interface-checklist-2026-06-09.md`;
- `research/amn2/route-policy-matrix.md`;
- `research/amn2/route-auth-surface-inventory.md`;
- `docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md`;
- `research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-10.md`.

KYORESUAS and PRVTPRO remain product/architecture signals only. No upstream code, route layout, command strings, service logic, UI, templates, workflows or manager implementations are copied.

## Baseline

The fake runner is a future local test contract, not an execution path:

- no SSH transport;
- no shell command construction;
- no live VPS hostname, endpoint, username, port or path values;
- no Docker, systemd, firewall, reverse proxy or file writes;
- no peer apply/revoke/sync mutation;
- no config generation or delivery;
- no `.conf`, QR, `vpn://`, key, PSK, token or backup payload in input, output, audit or error messages.

## Contract Shape

Future fake-runner implementations must expose a single bounded interface:

```text
FakeOperationRunner.run(plan, context) -> FakeOperationResult
```

Required `plan` fields:

| Field | Meaning |
| --- | --- |
| `operation_id` | Stable opaque id generated before execution |
| `operation_type` | One of `client_create`, `client_disable`, `client_revoke`, `peer_plan_apply`, `peer_apply`, `peer_revoke`, `peer_sync`, `operation_retry` |
| `target_ref` | Opaque local reference; no live endpoint, peer public key, IP, hostname or config path |
| `requested_by` | Actor id or safe actor label |
| `requested_scope` | Minimal scope from WAPI-V002 |
| `live_write_authorized` | Must be `no` in local/default mode |
| `dry_run` | Must be `true` for fake runner |
| `idempotency_key` | Optional now; required after `WAPI-V004` |
| `metadata` | Safe non-secret labels only |

Required `context` fields:

| Field | Meaning |
| --- | --- |
| `runner_mode` | Must be `fake` |
| `allowed_operations` | Explicit allowlist for this fake runner instance |
| `clock` | Injectable test clock or timestamp provider |
| `failure_mode` | Optional deterministic failure injection |
| `audit_sink` | Test/local sink that records safe metadata only |

Required `FakeOperationResult` fields:

| Field | Meaning |
| --- | --- |
| `operation_id` | Same opaque id from plan |
| `runner_mode` | Always `fake` |
| `status` | `planned`, `dry_run_passed`, `dry_run_failed`, `rejected`, `deferred` |
| `remote_mutation_performed` | Always `false` |
| `local_mutation_performed` | `false` for pure dry-run; future local implementation may use operation record only |
| `safe_summary` | Human-readable safe result, no secrets or endpoints |
| `audit_event` | Safe event metadata only |
| `recovery_hint` | Safe operator hint when status is `failed`, `rejected` or `deferred` |

## Operation Intents

Fake runner must support only these operation intents before any AMN2 implementation plan:

| operation_type | Allowed fake behavior | Forbidden behavior |
| --- | --- | --- |
| `client_create` | Validate safe request shape, return planned local record plus operation metadata | return `.conf`, QR, `vpn://`, endpoint or peer key |
| `client_disable` | Return safe disabled-state plan | touch live peer, service, server file or config |
| `client_revoke` | Return safe revoke operation plan | remove live peer, sync server or delete config artifact |
| `peer_plan_apply` | Return dry-run plan metadata only | build shell command or read live server paths |
| `peer_apply` | Return `deferred` unless live gate exists | execute or simulate live success as if applied |
| `peer_revoke` | Return `deferred` unless live gate exists | execute or simulate live success as if revoked |
| `peer_sync` | Return safe reconciliation plan only | read live inventory, backfill users or mutate local/live state |
| `operation_retry` | Return retry plan metadata only | re-run live command or bypass idempotency |

## Failure Modes

Fake runner must be able to produce deterministic failures for tests:

| failure_mode | Required status | Safe meaning |
| --- | --- | --- |
| `scope_denied` | `rejected` | caller lacks required minimal scope |
| `read_only_token` | `rejected` | read-only token attempted write/config/destructive action |
| `live_write_blocked` | `deferred` | operation requires live gate |
| `config_delivery_blocked` | `deferred` | operation would return secret-bearing config |
| `unsupported_operation` | `rejected` | operation not in allowlist |
| `duplicate_request` | `deferred` until WAPI-V004 | idempotency model required |
| `target_locked` | `deferred` until WAPI-V004 | lock model required |
| `audit_sink_failure` | `dry_run_failed` | safe audit write failed without secrets |

## Audit Contract

Fake-runner audit events must include:

- `operation_id`;
- `operation_type`;
- `runner_mode=fake`;
- `actor_ref`;
- `requested_scope`;
- `status`;
- `remote_mutation_performed=false`;
- `correlation_id` or equivalent safe id;
- safe `reason_code`.

Audit events must not include:

- raw token or token hash;
- Authorization header;
- `.env`;
- `.conf`;
- QR payload or image;
- `vpn://`;
- private key, PSK or peer public key;
- server endpoint, hostname, IP, SSH alias, username, port or live path;
- command string, stdout, stderr or log excerpt;
- backup contents or generated archive path.

## Test Requirements Before Implementation

Any future AMN2 fake-runner implementation plan must start with RED tests for:

- no SSH module/function is called in fake-runner mode;
- no shell command is constructed in fake-runner mode;
- all fake results carry `runner_mode=fake`;
- all fake results carry `remote_mutation_performed=false`;
- `live_write_authorized=no` rejects or defers live-required operations;
- read-only scopes cannot run write/config/destructive operation types;
- config delivery operation attempts are deferred with no secret payload;
- failure injection returns deterministic statuses;
- audit event contains required safe fields;
- audit/event/error output excludes forbidden secret markers;
- operation retry requires the later `WAPI-V004` idempotency model.

## WAPI-V004 Handoff

`WAPI-V004` was selected next and later closed as docs-only idempotency, locking and partial-failure model:

```text
slice_id: WAPI-V004
slice_name: idempotency, locking and partial-failure model
slice_mode: docs-only
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
live_vps_commands: no
```

It defines idempotency keys, per-target lock boundaries, retry behavior, conflict statuses and partial-failure vocabulary before any fake-runner code or write API route implementation. `WAPI-V005` was selected later and closed as write API audit/redaction requirements; `WAPI-I004` was then closed as operation status model; `WAPI-I003` was then closed as scoped write-token model; `WAPI-I002` was then closed as config delivery decoupling. Current next recommendation after `WAPI-I002` closure is `WAPI-I001` `/api/clients` design without live CRUD with `live_write_authorized: no`.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: WAPI-V004 docs-only idempotency, locking and partial-failure model with live_write_authorized: no
no_go_scope: fake-runner code implementation, runtime route expansion, live write, public exposure, config delivery, SSH/VPS commands, production mutation
defer_scope: AMN2 route implementation, live peer mutation, config/read-delivery routes, public/self-service routes, destructive operations
```

## Safety Statement

No AMN2 code, fake-runner code, live VPS command, SSH command, shell command, package apply, route expansion, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` CRUD, Local Agent mutation, token issue/revoke/rotate route, backup/import/reboot or production peer/user mutation was performed.
