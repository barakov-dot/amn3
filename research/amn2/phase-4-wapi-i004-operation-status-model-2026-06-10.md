# Phase 4 WAPI-I004: operation status model 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `WAPI-I004` как AMN3 docs-only operation status model для будущего write API. Документ собирает статусную лексику `WAPI-V004` и audit/redaction ограничения `WAPI-V005` в безопасную read model, но не добавляет AMN2 runtime routes, operation queue, audit schema, fake-runner code или live/write authorization.

## Decision

```text
slice_id: WAPI-I004
slice_name: operation status model
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
runner_code_changed: no
operation_status_schema_implemented: no
audit_schema_implemented: no
operation_queue_implemented: no
generated_openapi_artifact: no
public_openapi_docs_exposure: no
config_delivery: no
production_mutation: no
live_vps_commands: no
ssh_commands: no
required_gate_for_live_write: P4-NG-WRITE-API-LIVE-GATE
selected_next_slice: WAPI-I003 scoped write-token model
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
selected_next_slice_status: completed in research/amn2/phase-4-wapi-i003-scoped-write-token-model-2026-06-10.md
```

## Sources Reused

- `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v005-write-api-audit-redaction-requirements-2026-06-10.md`;
- `research/amn2/phase-4-ng-secrets-policy-go-no-go-format-2026-06-10.md`;
- `research/amn2/transfer-backlog.md`.

KYORESUAS and PRVTPRO remain product/architecture signals only. No upstream code, route layout, command strings, service logic, UI, templates, workflows or manager implementations are copied.

## VPS Evidence Boundary

Previous VPS work may appear only as safe status labels:

- `dry_run_only_pass`;
- `verified_live_single_disposable_peer`;
- `service_mode_loopback_baseline`;
- `live_write_blocked`;
- `vps_apply_disabled`.

Operation status must not include live VPS command output, endpoints, SSH aliases, hostnames, IPs, ports, peer keys, config paths, `.env`, `servers.yml`, full logs or secret-bearing evidence. Prior VPS success is historical proof that a status category is useful, not current authorization for live work.

## Status Model Goal

Future operation status must answer five operator/API questions safely:

| Question | Safe answer |
| --- | --- |
| What operation is this? | opaque `operation_id`, `operation_type`, `operation_class` |
| Where is it in lifecycle? | controlled `status`, `status_class`, `phase` |
| Did it mutate anything? | `local_mutation_performed`, `remote_mutation_performed` booleans |
| Why is it blocked or failed? | safe `reason_code`, `gate_name`, `recovery_required` |
| How do we correlate it? | `correlation_id`, audit event reference, safe timestamps |

The status model is not a queue implementation. It is a contract for future operation record/status responses and UI labels.

## Required Safe Status Fields

Future operation status responses may include only safe metadata:

| Field | Requirement |
| --- | --- |
| `operation_id` | opaque stable id |
| `correlation_id` | safe correlation id |
| `operation_type` | controlled vocabulary from WAPI-V003/WAPI-V004 |
| `operation_class` | `read-only`, `state-write`, `secret-read`, `destructive`, `public-exposure` as applicable |
| `status` | controlled status from this model |
| `status_class` | `terminal`, `non_terminal`, `blocked`, `attention_required` |
| `phase` | `request`, `planning`, `dry_run`, `execution`, `recovery`, `closed` |
| `reason_code` | safe controlled reason code |
| `requested_scope` | minimal scope used for authorization decision |
| `actor_ref` | safe actor reference |
| `target_ref` | opaque local target reference |
| `target_ref_type` | `client`, `peer`, `server`, `config`, `operation` or `none` |
| `runner_mode` | `none`, `fake`, `local`, `live` |
| `dry_run` | boolean |
| `gate_name` | required gate label if blocked/deferred |
| `live_write_authorized` | boolean or `no`/`yes` marker |
| `local_mutation_performed` | boolean |
| `remote_mutation_performed` | boolean |
| `recovery_required` | boolean |
| `safe_recovery_hint` | controlled safe text or reason label only |
| `created_at` | server-side timestamp |
| `updated_at` | server-side timestamp |
| `finished_at` | optional server-side timestamp |
| `audit_event_ref` | opaque audit reference |
| `redaction_policy_version` | WAPI-V005 policy/version label |

Any additional status field requires secret-surface classification and tests before implementation.

## Status Vocabulary

Canonical statuses:

| Status | Status class | Phase | Meaning |
| --- | --- | --- | --- |
| `planned` | `non_terminal` | `planning` | safe operation plan exists |
| `dry_run_passed` | `non_terminal` | `dry_run` | dry-run passed without live mutation |
| `dry_run_failed` | `terminal` | `dry_run` | dry-run failed without live mutation |
| `rejected` | `terminal` | `request` | policy/scope/idempotency/input denied |
| `deferred` | `blocked` | `planning` | missing gate or authorization |
| `running` | `non_terminal` | `execution` | future explicit gate allowed execution start |
| `succeeded` | `terminal` | `closed` | authorized operation finished successfully |
| `failed` | `terminal` | `closed` | operation failed without known partial mutation |
| `conflict` | `terminal` | `request` | request conflicts with existing target/operation |
| `idempotency_replay` | `terminal` | `request` | safe replay of earlier operation result |
| `idempotency_conflict` | `terminal` | `request` | same key with different fingerprint |
| `locked` | `blocked` | `planning` | target lock held by another operation |
| `local_changed_remote_not_started` | `attention_required` | `recovery` | local mutation happened, remote did not start |
| `local_changed_remote_failed` | `attention_required` | `recovery` | local mutation happened, remote failed |
| `remote_changed_local_failed` | `attention_required` | `recovery` | remote mutation happened, local persistence failed |
| `remote_changed_local_unknown` | `attention_required` | `recovery` | remote side effect uncertain |
| `rolled_back` | `terminal` | `closed` | safe recovery restored intended prior state |
| `rollback_failed` | `attention_required` | `recovery` | rollback failed |
| `recovery_required` | `attention_required` | `recovery` | manual safe reconciliation needed |

`running`, `succeeded`, remote partial-failure and rollback statuses are future implementation terms only. This slice does not authorize live/local execution.

## Reason Codes

Initial safe reason codes:

| Reason code | Use |
| --- | --- |
| `scope_denied` | token/scope lacks required permission |
| `read_only_token` | read-only credential attempted write/config/destructive action |
| `live_write_blocked` | live write requires named gate |
| `config_delivery_blocked` | operation would return secret-bearing config |
| `public_exposure_blocked` | operation would expose public surface |
| `destructive_operation_blocked` | backup/import/reboot/service mutation not authorized |
| `idempotency_key_missing` | required idempotency key absent |
| `idempotency_conflict` | same key with different request fingerprint |
| `target_locked` | target lock already held |
| `audit_redaction_failed` | output could not be proven safe |
| `audit_sink_failed` | audit write failed |
| `dry_run_validation_failed` | local/fake validation failed |
| `partial_failure_detected` | local/remote split-brain state detected |
| `rollback_required` | recovery/rollback needed |
| `rollback_failed` | recovery/rollback failed |

Reason codes must not embed user names, peer public keys, IPs, endpoints, command output or raw error strings.

## Transition Rules

Allowed high-level transitions:

```text
request -> rejected
request -> idempotency_replay
request -> idempotency_conflict
request -> planned
planned -> dry_run_passed
planned -> dry_run_failed
planned -> deferred
planned -> locked
dry_run_passed -> deferred
dry_run_passed -> running
running -> succeeded
running -> failed
running -> local_changed_remote_not_started
running -> local_changed_remote_failed
running -> remote_changed_local_failed
running -> remote_changed_local_unknown
attention_required -> rolled_back
attention_required -> rollback_failed
attention_required -> recovery_required
```

Default/local/docs mode must stop at `planned`, `dry_run_passed`, `dry_run_failed`, `rejected`, `deferred`, `locked`, `conflict`, `idempotency_replay` or `idempotency_conflict`. It must not move to `running` or `succeeded` without a later explicit implementation and gate.

## Visibility Tiers

Future status surfaces must classify views:

| Tier | Audience | Allowed fields |
| --- | --- | --- |
| `operator_private` | private web/admin or authenticated local API | full safe status fields |
| `api_read` | scoped API reader | safe status fields excluding actor details unless scope allows |
| `audit_internal` | local audit review | safe audit/status join, no raw payloads |
| `public` | internet/public/self-service | not allowed by this slice |

No tier may expose `.conf`, QR, `vpn://`, private key, PSK, token/hash, endpoint, host/IP/port, command output, full logs or backup contents.

## UI Label Guidance

Future web-panel labels should avoid implying live success when the operation is gated:

| Status | Label intent |
| --- | --- |
| `planned` | planned locally |
| `dry_run_passed` | dry-run passed, no live mutation |
| `deferred` | blocked by named gate |
| `locked` | waiting for target lock |
| `rejected` | rejected by policy |
| `attention_required` statuses | recovery/reconciliation needed |
| `succeeded` | only after authorized execution |

Labels must not display raw target identifiers or secret-bearing artifacts.

## Required Tests Before Implementation

Any future AMN2 implementation plan for operation records, operation status routes, web-panel status labels or operation queue must start with RED tests for:

- status response contains required safe fields only;
- `dry_run_passed` response states no live mutation occurred;
- `deferred` is returned when `live_write_authorized=no`;
- `VPS_APPLY_ENABLED=false` maps live-required operation to blocked/deferred status;
- `succeeded` cannot be produced by fake/default mode;
- partial-failure statuses set `recovery_required=true`;
- reason codes are controlled values, not raw exception text;
- status response excludes raw token, token hash and Authorization header;
- status response excludes `.conf`, QR, `vpn://`, private key, PSK and peer public key;
- status response excludes endpoint, hostname, IP, SSH alias, username, port and live path;
- status response excludes command string, stdout, stderr, full logs and backup contents;
- visibility tier tests prevent public/self-service status exposure by default;
- UI labels distinguish dry-run/deferred from live success.

## WAPI-I003 Handoff

`WAPI-I003` was selected next and later closed as docs-only scoped write-token model:

```text
slice_id: WAPI-I003
slice_name: scoped write-token model
slice_mode: docs-only
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
live_vps_commands: no
```

It defines minimal write/config/operation scopes and explicitly rejects broad admin-equivalent tokens before `/api/clients` design or route implementation planning. `WAPI-I002` was then closed as docs-only config delivery decoupling; `WAPI-I001` was then closed as docs-only `/api/clients` design without live CRUD; `WAPI-I005` was then closed as web-panel gated action labels; `NG-N003` was then closed as docs-only operation queue design after write API contract; `NG-N002` was then closed as docs-only health/status polling design; `NG-N001` was then closed as docs-only attach-existing-server read-only reconciliation gate design. `NG-N004` was then closed as docs-only candidate registry update after every gate decision. `NG-S001` was then closed as docs-only status/transfer synchronization. `NG-S002` and `NG-S004` were then closed together as docs-only handoff and visible-plan maintenance. `NG-X003` was then closed as docs-only stale wording cleanup. `NG-X001` was then closed as docs-only gate naming consistency. `NG-X002` was then closed as docs-only Russian-first operator wording polish. Очередь default docs-only cosmetic теперь закрыта.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: WAPI-I003 docs-only scoped write-token model with live_write_authorized: no
no_go_scope: write API route implementation, fake-runner code implementation, operation queue implementation, runtime route expansion, live write, public exposure, config delivery, SSH/VPS commands, production mutation
defer_scope: AMN2 route implementation, live peer mutation, config/read-delivery routes, public/self-service routes, destructive operations, audit/status schema migration
```

## Safety Statement

No AMN2 code, operation status schema implementation, operation queue implementation, audit schema implementation, fake-runner code, live VPS command, SSH command, shell command, package apply, route expansion, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` CRUD, Local Agent mutation, token issue/revoke/rotate route, backup/import/reboot or production peer/user mutation was performed.
