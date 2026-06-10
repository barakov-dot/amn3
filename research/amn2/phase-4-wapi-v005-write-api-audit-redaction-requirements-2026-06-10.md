# Phase 4 WAPI-V005: write API audit/redaction requirements 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `WAPI-V005` как AMN3 docs-only audit/redaction contract для будущего write API. Документ фиксирует, какие safe metadata будущие write/config/operation routes обязаны писать в audit, какие secret-bearing поля запрещены, и какие RED tests должны появиться до любой AMN2 route, fake-runner или live-runner implementation.

## Decision

```text
slice_id: WAPI-V005
slice_name: write API audit/redaction requirements
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
runner_code_changed: no
audit_schema_implemented: no
generated_openapi_artifact: no
public_openapi_docs_exposure: no
config_delivery: no
production_mutation: no
live_vps_commands: no
ssh_commands: no
required_gate_for_live_write: P4-WRITE-API-LIVE-GATE
selected_next_slice: WAPI-I004 operation status model
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
selected_next_slice_status: completed in research/amn2/phase-4-wapi-i004-operation-status-model-2026-06-10.md
```

## Sources Reused

- `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`;
- `research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md`;
- `research/amn2/phase-4-ng-secrets-policy-go-no-go-format-2026-06-10.md`;
- `research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md`;
- `research/amn2/transfer-backlog.md`;
- `research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-10.md`.

KYORESUAS and PRVTPRO remain product/architecture signals only. No upstream code, route layout, command strings, service logic, UI, templates, workflows or manager implementations are copied.

## VPS Evidence Boundary

Previous VPS work may be referenced only as safe evidence labels and status vocabulary:

- Phase 1 `dry-run-only-pass`;
- Phase 2 single disposable peer `verified-live`;
- Phase 3 service-mode loopback baseline with `VPS_APPLY_ENABLED=false`.

Audit requirements must not quote live command output, endpoints, SSH aliases, hostnames, IPs, ports, peer keys, config paths, `.env`, `servers.yml` or full logs from those VPS sessions. The fact that prior VPS gates passed does not authorize current live/write work.

## Audit Goal

Future write API audit must answer five questions without secrets:

| Question | Required safe answer |
| --- | --- |
| Who requested it? | safe actor reference and actor type |
| What was requested? | route group, operation type and operation class |
| Under which authority? | requested scope, token class and gate state |
| What happened? | result status, reason code and mutation booleans |
| How can it be correlated? | correlation id, operation id and safe request fingerprint digest |

Audit is mandatory for future state-write, secret-read, config-delivery, destructive, retry and cancel candidates. Read-only aggregate/status routes may use lighter `api_read` audit, but they must still avoid secret-bearing metadata.

## Required Safe Audit Fields

Future write API audit event schema must include only safe metadata:

| Field | Requirement |
| --- | --- |
| `event_id` | opaque audit event id |
| `timestamp` | server-side timestamp |
| `correlation_id` | safe request correlation id |
| `operation_id` | stable opaque operation id when operation exists |
| `event_type` | controlled vocabulary, not free-form raw input |
| `route_group` | one of `clients`, `peers`, `configs`, `operations`, `audit_status` |
| `operation_type` | controlled WAPI operation type |
| `operation_class` | `read-only`, `state-write`, `secret-read`, `destructive`, `public-exposure` as applicable |
| `actor_ref` | safe actor id or stable internal reference |
| `actor_type` | `operator`, `api_token`, `system` or later approved value |
| `requested_scope` | minimal scope used for the decision |
| `token_class` | safe class such as `read-only`, `write-scoped`, `blocked`, not raw token/hash |
| `target_ref` | opaque local reference only |
| `target_ref_type` | `client`, `peer`, `server`, `config`, `operation` or `none` |
| `request_fingerprint_digest` | digest of normalized non-secret request fields |
| `idempotency_key_digest` | digest only; raw idempotency key is forbidden |
| `lock_scope` | opaque lock scope from WAPI-V004 |
| `gate_name` | named gate label when a gate is required |
| `live_write_authorized` | boolean or `no`/`yes` marker |
| `runner_mode` | `none`, `fake`, `local`, `live` |
| `dry_run` | boolean |
| `result_status` | status from WAPI-V004 vocabulary |
| `reason_code` | controlled safe reason code |
| `local_mutation_performed` | boolean |
| `remote_mutation_performed` | boolean |
| `recovery_required` | boolean |
| `redaction_policy_version` | version/label of the redaction contract |

Any implementation may add fields only if a route/auth/secret review classifies them as non-secret and tests assert they do not contain forbidden markers.

## Forbidden Audit/Error/Status Fields

Audit, operation status, API errors, safe summaries and evidence must never contain:

- raw token;
- token hash;
- Authorization header;
- raw idempotency key;
- session cookie;
- web password hash;
- session secret;
- `.env` or `.env` values;
- raw `servers.yml`;
- client `.conf`;
- QR payload or QR image;
- `vpn://`;
- private key;
- PSK;
- peer public key;
- server endpoint, hostname, IP, SSH alias, username, port or live path;
- command string;
- stdout, stderr or log excerpt;
- backup contents or generated archive path;
- raw request body when the route can receive secret-bearing fields;
- public endpoint values;
- generated config archive, share link or download URL.

Redaction must be deny-by-default. If a value is not explicitly classified as safe metadata, it must not enter audit/status/error output.

## Redaction Rules

Future implementation must use structured safe fields instead of partial masking whenever possible.

Allowed patterns:

- store opaque internal references instead of live identifiers;
- store digests for idempotency keys and request fingerprints;
- store boolean markers such as `remote_mutation_performed=false`;
- store controlled reason codes such as `scope_denied` or `live_write_blocked`;
- store aggregate counts only when a count is needed.

Disallowed patterns:

- "mask most of the token" and keep a prefix/suffix;
- "show first chars" of keys, PSK, peer public key, endpoint or host;
- store raw command output then rely on a later UI redaction layer;
- store raw request/response bodies for write/config/destructive routes;
- copy live VPS evidence logs into audit;
- treat `vpn://`, QR or `.conf` as display-safe because they are user-facing artifacts.

## Event Types

Initial future event vocabulary:

| Event type | Use |
| --- | --- |
| `write_request_received` | request accepted for policy/idempotency evaluation |
| `write_request_rejected` | request denied before planning |
| `operation_planned` | safe operation plan created |
| `operation_deferred` | valid intent blocked by missing gate/live authorization |
| `operation_dry_run_passed` | local/fake dry-run passed |
| `operation_dry_run_failed` | local/fake dry-run failed |
| `operation_started` | future explicit gate allowed execution start |
| `operation_succeeded` | authorized operation succeeded |
| `operation_failed` | operation failed without known partial mutation |
| `operation_partial_failure` | split-brain/partial state occurred |
| `operation_rollback_recorded` | rollback/recovery metadata recorded safely |
| `operation_retry_requested` | retry requested under WAPI-V004 rules |
| `config_delivery_blocked` | config/QR/`vpn://` output attempt was blocked |
| `redaction_failure` | output could not be proven safe |
| `audit_write_failed` | audit sink failed |

`operation_started`, `operation_succeeded`, `operation_partial_failure` and `operation_rollback_recorded` are future live/local implementation terms only. This docs-only slice does not authorize them.

## Failure Behavior

Before any local or remote mutation:

- audit redaction failure must reject or defer the operation;
- audit sink failure must return safe `dry_run_failed`, `rejected` or `deferred`;
- write/config/destructive operation must not proceed unaudited.

After a future authorized mutation:

- audit failure must not cause a false success claim;
- operation status must move to a safe failure or recovery-required state;
- fallback evidence must contain only safe metadata.

## Required Tests Before Implementation

Any future AMN2 implementation plan for write API routes, fake runner, operation records or audit storage must start with RED tests for:

- audit event contains required safe fields for planned write operation;
- audit event contains correlation id, operation id and actor/scope metadata;
- audit event records `live_write_authorized=no` for docs/local/default mode;
- audit event stores raw idempotency key only as digest;
- audit event stores request fingerprint only as digest of non-secret fields;
- read-only token attempting write produces safe `write_request_rejected`;
- config delivery attempt produces safe `config_delivery_blocked` without payload;
- audit/error/status output excludes raw token, token hash and Authorization header;
- audit/error/status output excludes `.conf`, QR, `vpn://`, private key, PSK and peer public key;
- audit/error/status output excludes endpoint, hostname, IP, SSH alias, username, port and live path;
- audit/error/status output excludes command string, stdout, stderr, full logs and backup contents;
- redaction failure prevents pre-mutation write execution;
- audit sink failure does not produce unredacted fallback output;
- partial-failure and recovery-required events contain safe metadata only;
- route-specific tests fail if a new audit field is not classified by secret policy.

## WAPI-I004 Handoff

`WAPI-I004` was selected next and later closed as docs-only operation status model:

```text
slice_id: WAPI-I004
slice_name: operation status model
slice_mode: docs-only
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
live_vps_commands: no
```

It consolidates WAPI-V004 status vocabulary and WAPI-V005 audit/redaction requirements into the safe operation status read model before `/api/clients` design or route implementation planning. `WAPI-I003` was then closed as scoped write-token model. Current next recommendation after `WAPI-I003` closure is `WAPI-I002` decouple config delivery from client creation with `live_write_authorized: no`.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: WAPI-I004 docs-only operation status model with live_write_authorized: no
no_go_scope: write API route implementation, fake-runner code implementation, runtime route expansion, live write, public exposure, config delivery, SSH/VPS commands, production mutation
defer_scope: AMN2 route implementation, live peer mutation, config/read-delivery routes, public/self-service routes, destructive operations, audit schema migration
```

## Safety Statement

No AMN2 code, audit schema implementation, fake-runner code, live VPS command, SSH command, shell command, package apply, route expansion, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` CRUD, Local Agent mutation, token issue/revoke/rotate route, backup/import/reboot or production peer/user mutation was performed.
