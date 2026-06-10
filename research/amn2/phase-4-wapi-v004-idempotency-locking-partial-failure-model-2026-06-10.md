# Phase 4 WAPI-V004: idempotency, locking and partial-failure model 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `WAPI-V004` как AMN3 docs-only model для будущего write API. Документ фиксирует идемпотентность запросов, lock boundaries, retry/conflict behavior и partial-failure vocabulary до любого fake-runner code, runtime route expansion или live VPS/write gate.

## Decision

```text
slice_id: WAPI-V004
slice_name: idempotency, locking and partial-failure model
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
selected_next_slice: WAPI-V005 write API audit/redaction requirements
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
```

## Sources Reused

- `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`;
- `research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md`;
- `research/amn2/phase-4-protocol-manager-interface-checklist-2026-06-09.md`;
- `research/amn2/transfer-backlog.md`;
- `research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md`;
- `research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md`;
- `research/amn2/post-dry-run-read-only-integration-implementation.md`;
- `docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md`;
- `research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-10.md`.

KYORESUAS and PRVTPRO remain product/architecture signals only. No upstream code, route layout, command strings, service logic, UI, templates, workflows or manager implementations are copied.

## VPS Evidence Boundary

Previous VPS work is accepted as historical evidence and architecture input, not as current permission.

Safe status vocabulary may reuse these proven baselines:

| Evidence | Safe meaning for WAPI |
| --- | --- |
| Phase 1 `dry-run-only-pass` | dry-run success is distinct from live success |
| Phase 2 `verified-live` for exactly one disposable peer | live apply/revoke can be modeled, but broad write lifecycle remains blocked |
| Phase 3 service-mode loopback baseline | loopback/tunnel-only service state with `VPS_APPLY_ENABLED=false` maps to blocked/deferred live write |

This slice does not run SSH, does not sample the VPS, does not unlock `/api/clients` write CRUD, and does not authorize config delivery or production peer/user mutation.

## Idempotency Model

Future state-write, secret-read, config-preparation, config-delivery, retry and cancel requests must carry an idempotency key before implementation.

Required behavior:

| Case | Required result |
| --- | --- |
| Missing key for write/config/retry/cancel candidate | `rejected` |
| Same key and same request fingerprint | `idempotency_replay`; return the same `operation_id` and safe result summary |
| Same key and different request fingerprint | `idempotency_conflict`; do not run or enqueue the new intent |
| Read-only aggregate/status route | idempotency key is not required |
| Live-required operation while `live_write_authorized=no` | `deferred` with `live_write_blocked` reason |

The request fingerprint must be safe and deterministic:

- include actor reference, operation type, target reference, declared scope and normalized non-secret request fields;
- exclude raw token, token hash, `.conf`, QR, `vpn://`, private key, PSK, endpoint, hostname, IP, SSH alias, username, port, command string, stdout, stderr and live path;
- store digest/fingerprint metadata only, not raw secret-bearing request bodies.

The idempotency retention period is an implementation decision for a later AMN2 plan. The contract requirement is that replay and conflict tests exist before any route implementation.

## Locking Model

Future write-capable operation planning must acquire an explicit safe lock before local or remote mutation.

Recommended lock scopes:

| Lock scope | Applies to | Required behavior |
| --- | --- | --- |
| `client:{client_ref}` | client create/update/disable/revoke | no overlapping lifecycle mutation for the same local client |
| `peer:{server_ref}:{peer_ref}` | peer apply/revoke/sync | no overlapping apply/revoke/sync for the same peer target |
| `server:{server_ref}` | sync/reconciliation/live apply group | no concurrent server-wide reconciliation and peer writes |
| `config:{client_ref}` | config prepare/read/delivery gate | no config delivery coupled implicitly to client write |
| `operation:{operation_id}` | retry/cancel | no duplicate retry/cancel mutation for the same operation |

Lock identifiers must be opaque local references. They must not contain live endpoints, SSH aliases, hostnames, IPs, ports, peer public keys, config paths, command strings or secret values.

In local/fake/default mode, lock conflicts must return `locked`, `conflict` or `deferred`, never simulated live success.

## Status Vocabulary

The future operation status model must distinguish planning, dry-run, live execution, local-only effects and recovery.

Allowed status vocabulary:

| Status | Meaning |
| --- | --- |
| `planned` | request accepted as a safe operation plan |
| `dry_run_passed` | local/fake validation passed without live mutation |
| `dry_run_failed` | local/fake validation failed without live mutation |
| `rejected` | request denied by policy, scope, idempotency or malformed input |
| `deferred` | valid intent blocked by missing gate or live authorization |
| `running` | live/local execution started under a future explicit gate |
| `succeeded` | operation finished in the authorized execution context |
| `failed` | operation failed without known partial mutation |
| `conflict` | target state or request conflicts with existing operation |
| `idempotency_replay` | duplicate safe replay of a previous request |
| `idempotency_conflict` | same key attempted with a different request fingerprint |
| `locked` | target lock is held by another operation |
| `local_changed_remote_not_started` | local mutation happened, remote mutation did not start |
| `local_changed_remote_failed` | local mutation happened, remote mutation failed |
| `remote_changed_local_failed` | remote mutation happened, local persistence failed |
| `remote_changed_local_unknown` | remote side effect is uncertain and needs reconciliation |
| `rolled_back` | recovery action restored the intended prior state |
| `rollback_failed` | rollback was attempted and failed |
| `recovery_required` | operator-safe recovery or reconciliation is required |

Status output must be safe summary only. It must not include raw secrets, live endpoints, command output or full logs.

## Partial-Failure Model

Future write API design must answer both split-brain cases before implementation:

| Scenario | Required state |
| --- | --- |
| Local DB write succeeds, remote mutation does not start | `local_changed_remote_not_started` with safe rollback/retry note |
| Local DB write succeeds, remote mutation fails | `local_changed_remote_failed` with safe reconciliation note |
| Remote mutation succeeds, local DB write fails | `remote_changed_local_failed` with recovery-required evidence |
| Remote result cannot be confirmed | `remote_changed_local_unknown` and no automatic success claim |

The model must preserve these rules:

- dry-run success is not live success;
- `VPS_APPLY_ENABLED=false` or missing live gate maps to `deferred`, not `succeeded`;
- future rollback evidence must be safe and must not paste command output, config payloads, peer keys, endpoints or logs;
- a retry may not change operation intent, target reference, actor scope or request fingerprint.

## Retry Rules

`operation_retry` is allowed only as a safe plan until a later implementation plan exists.

Required retry behavior:

- retry references an existing `operation_id`;
- retry keeps the original operation type, target reference, actor/scope boundary and request fingerprint;
- retry must check idempotency before lock acquisition;
- retry must acquire `operation:{operation_id}` and the original target lock;
- retry cannot bypass `live_write_authorized=no`;
- retry cannot trigger config delivery or secret-read side effects unless a separate secret-read gate exists;
- duplicate retry with the same idempotency key returns a safe replay result.

## Test Requirements Before Implementation

Any future AMN2 implementation plan for write API operation records, fake runner or routes must start with RED tests for:

- missing idempotency key rejects write/config/retry/cancel candidates;
- same idempotency key and same request fingerprint returns the same `operation_id` and safe result;
- same idempotency key and different fingerprint returns `idempotency_conflict`;
- per-target lock conflict prevents concurrent apply/revoke/sync for the same target;
- fake runner never returns live success while `live_write_authorized=no`;
- `VPS_APPLY_ENABLED=false` maps live-required operation to `deferred`;
- partial-failure statuses contain no secret-bearing fields;
- retry cannot bypass idempotency, target locks or live gate;
- rollback/recovery evidence is safe metadata only;
- audit/error output excludes raw tokens, token hashes, `.conf`, QR, `vpn://`, private keys, PSK, endpoints, SSH aliases, command strings and full logs.

## WAPI-V005 Handoff

`WAPI-V005` is the recommended next docs-only slice:

```text
slice_id: WAPI-V005
slice_name: write API audit/redaction requirements
slice_mode: docs-only
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
live_vps_commands: no
```

It should define safe audit fields, correlation IDs, actor/scope/result metadata, forbidden secret markers and required tests before any write API route or fake-runner implementation.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: WAPI-V005 docs-only write API audit/redaction requirements with live_write_authorized: no
no_go_scope: write API route implementation, fake-runner code implementation, runtime route expansion, live write, public exposure, config delivery, SSH/VPS commands, production mutation
defer_scope: AMN2 route implementation, live peer mutation, config/read-delivery routes, public/self-service routes, destructive operations
```

## Safety Statement

No AMN2 code, fake-runner code, live VPS command, SSH command, shell command, package apply, route expansion, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` CRUD, Local Agent mutation, token issue/revoke/rotate route, backup/import/reboot or production peer/user mutation was performed.
