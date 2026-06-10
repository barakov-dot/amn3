# Phase 4 NG-N001: attach-existing-server read-only reconciliation gate design 2026-06-10

Purpose: close `NG-N001` as an AMN3 docs-only design for reconciling an already-existing target server without attaching it, importing it, backfilling local records or mutating production state. This document defines the safe read-only reconciliation contract before any AMN2 implementation, live target check or attach flow exists.

## Decision

```text
slice_id: NG-N001
slice_name: attach-existing-server read-only reconciliation gate design
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
reconciliation_implemented: no
attach_implemented: no
import_implemented: no
backfill_implemented: no
migration_implemented: no
server_record_created: no
server_record_updated: no
server_config_imported: no
agent_deployed: no
tunnel_created: no
polling_implemented: no
scheduler_implemented: no
collector_implemented: no
operation_queue_changed: no
write_crud_implemented: no
token_issue_route_implemented: no
token_revoke_route_implemented: no
config_delivery_route_implemented: no
generated_openapi_artifact: no
public_openapi_docs_exposure: no
public_api_3040: no
direct_public_web_admin_3030: no
caddy_https_domain_cutover: no
config_delivery: no
production_mutation: no
live_vps_commands: no
ssh_commands: no
required_gate_for_local_reconciliation_implementation: P4-ATTACH-EXISTING-SERVER-RECONCILIATION-LOCAL-IMPLEMENTATION-GATE
required_gate_for_real_target_detection: P4-NG-VPS-READONLY-BASELINE-2026-06-10
required_gate_for_attach_or_backfill: P4-ATTACH-EXISTING-SERVER-WRITE-BACKFILL-GATE
required_gate_for_live_write: P4-WRITE-API-LIVE-GATE
required_gate_for_config_delivery: P4-CONFIG-DELIVERY-GATE
selected_next_slice: NG-N004 update candidate registry after every gate decision
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
```

## Sources Reused

- `research/amn2/phase-4-ng-n002-health-status-polling-design-2026-06-10.md`;
- `research/amn2/phase-4-ng-n003-operation-queue-design-2026-06-10.md`;
- `research/amn2/phase-4-wapi-i001-clients-design-without-live-crud-2026-06-10.md`;
- `research/amn2/phase-4-wapi-i002-config-delivery-decoupling-2026-06-10.md`;
- `research/amn2/phase-4-wapi-i004-operation-status-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-i005-web-panel-gated-action-labels-2026-06-10.md`;
- `research/amn2/phase-4-candidate-registry-2026-06-09.md`;
- `research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md`;
- `research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-10.md`.

Upstream repositories remain research-only idea sources. No GPL or upstream code, templates, manager implementations, workflows, attach flows or API code were copied.

## VPS Evidence Boundary

`NG-N001` did not run SSH, open a tunnel, call live loopback endpoints, call public endpoints, inspect live systemd state, sample ports, query production peer/user data or read production configuration files.

Historical Phase 3 and service-mode evidence remains context only. It does not authorize new detection, attach, import, polling or backfill activity.

## Reconciliation Goal

Read-only reconciliation is a report, not an attach operation.

It may eventually help an operator answer:

- does a candidate target look like a known AMN/Amnezia service-mode host;
- which safe component classes are present or unknown;
- which parts require a named gate before real detection;
- whether local records would be insufficient, stale or conflicting if an attach were later proposed.

It must not:

- create or update server records;
- import raw server configs;
- normalize production peer/user state into local DB rows;
- deploy or configure a Local Agent;
- create SSH tunnels;
- write service files, firewall rules, Caddy config or package state;
- deliver configs or expose endpoints;
- infer authorization from a successful read-only report.

## Reconciliation Phases

```text
phase_0_policy_only
phase_1_local_fake_inventory
phase_2_read_only_evidence_request
phase_3_read_only_evidence_compare
phase_4_reconciliation_report
phase_blocked_attach_or_backfill
```

Current `NG-N001` scope is `phase_0_policy_only`.

Future local implementation may stop at `phase_1_local_fake_inventory` under a separate local implementation gate.

Any real target detection requires a separate named read-only VPS gate. Attach, import and backfill require a separate write/backfill gate after read-only evidence exists.

## Safe Reconciliation Fields

Future reports may expose only safe fields:

```text
reconciliation_id
candidate_ref
candidate_source_class
target_ref
target_ref_type
evidence_mode
evidence_gate_name
reconciliation_status
status_reason
component_class
component_status
component_count
matched_component_count
unknown_component_count
mismatch_count
blocked_count
data_age_seconds
staleness_state
local_record_state
attach_allowed
backfill_allowed
live_write_authorized
config_delivery_authorized
created_at
updated_at
correlation_id
audit_event_ref
```

`candidate_ref` and `target_ref` must be opaque references. They must not contain hostnames, IP addresses, ports, endpoints, peer names, user names, public keys or secrets.

## Forbidden Fields

```text
raw_token
token
token_hash
authorization_header
session_cookie
private_key
public_key
preshared_key
psk
client_config
wireguard_config
outline_config
server_config
raw_config
vpn_url
vpn_uri
qr
conf
archive
download_url
share_url
endpoint
host
hostname
ip
port
peer_name
peer_id
user_name
user_id
per_peer_traffic
per_user_traffic
client_activity
last_handshake_ip
ssh_command
shell_command
env
servers_yml
stdout
stderr
logs
traceback
```

If an evidence source cannot be summarized without forbidden fields, the report must mark that component as `blocked_secret_surface` or `redaction_failed`.

## Status Vocabulary

```text
not_started
policy_only
local_fake_ready
read_only_gate_required
evidence_collected
matched
partial_match
mismatch
unknown
stale
blocked_by_gate
blocked_secret_surface
redaction_failed
attach_deferred
backfill_blocked
```

Recommended reason codes:

```text
gate_required
local_only_design
real_target_detection_deferred
attach_requires_write_backfill_gate
config_import_blocked
secret_marker_detected
redaction_failed
local_record_missing
local_record_conflict
component_unknown
component_stale
aggregate_only
production_mutation_blocked
```

`matched` is not authorization. It only means the safe evidence report found no policy-level mismatch in the fields it was allowed to compare.

## Component Classes

Allowed future component classes:

```text
web_admin_private_loopback
bot_service
private_read_only_api
local_agent_summary
aggregate_metrics
operation_status_summary
queue_status_summary
policy_gate_status
service_mode_boundary
```

Blocked component classes:

```text
peer_detail
user_detail
config_artifact
raw_server_config
token_lifecycle_write
backup_import_reboot
public_endpoint
server_cleanup
raw_protocol_manager
```

## Attach Boundary

Read-only reconciliation may produce:

```text
safe_reconciliation_report
safe_status_summary
safe_gate_blocker_list
safe_local_record_gap_summary
```

It must not produce:

```text
server_create_request
server_update_request
server_import_payload
server_config_blob
peer_import_payload
user_import_payload
agent_deployment_plan
service_restart_plan
config_delivery_payload
write_operation
```

Attach/backfill is a separate future decision. It must not be hidden behind labels such as "accept", "claim", "sync", "repair", "adopt" or "finalize" unless a write/backfill gate exists and explicitly authorizes the behavior.

## Conflict Handling

If local records and safe read-only evidence disagree, the system must:

- mark `mismatch` or `partial_match`;
- keep local state unchanged;
- avoid automatic merge/backfill;
- avoid destructive cleanup;
- produce safe operator-facing reason codes;
- require a separate decision before any attach, import, correction or backfill.

Unknown state is acceptable. Guessing production topology from partial evidence is not.

## Health/Status Binding

`NG-N002` health/status polling may support reconciliation only through aggregate, stale-aware summaries. It must not:

- expose per-peer or per-user detail;
- run real target checks without a read-only VPS gate;
- convert a healthy component into attach permission;
- create local server records;
- trigger queue operations.

## Operation Queue Binding

`NG-N003` queue/status semantics may represent a future attach/backfill proposal as `deferred` or `blocked_by_gate`, but must not enqueue execution while `live_write_authorized: no`.

Any attach/backfill proposal must remain a plan until a separate write/backfill gate exists.

## Required RED Tests Before Implementation

Before any AMN2 reconciliation implementation, tests must prove:

- no reconciliation route, attach route, import route or backfill route exists before the implementation gate;
- no real target detection runs without a named read-only VPS gate;
- safe reports contain no raw token, token hash, Authorization header, session cookie, endpoint, host, hostname, IP, port, peer/user identifier, public key, private key, PSK, config, QR, `vpn://`, command output or logs;
- attach and backfill flags remain false in default mode;
- a matched read-only report cannot create/update local server records;
- mismatch cannot auto-repair local records;
- config import is blocked even when read-only evidence exists;
- peer/user details remain blocked or aggregate-only;
- redaction failure produces `redaction_failed`, not partial output;
- public API `3040`, direct public web/admin `3030`, TCP `80/443` and Caddy/HTTPS/domain cutover remain unchanged;
- no `/api/clients` write CRUD, token issue/revoke, config delivery, backup/import/reboot or Local Agent mutation is called.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: NG-N001 docs-only attach-existing-server read-only reconciliation gate design with live_write_authorized: no
no_go_scope: AMN2 reconciliation implementation, attach implementation, import/backfill implementation, runtime route expansion, route behavior change, real target detection, SSH/VPS commands, `/api/clients` runtime CRUD, token issue/revoke routes, config delivery routes, live write, public exposure, production mutation
defer_scope: local reconciliation implementation gate, real target read-only VPS detection gate, attach/write/backfill gate, peer/user detail visibility, config import, public/self-service status, destructive operations
```

## Handoff

`NG-N001` is closed. The recommended next docs-only slice is `NG-N004` update candidate registry after every gate decision, because the candidate registry now has multiple closed P4-NG/WAPI decisions and should be checked as its own explicit registry-maintenance slice before any live or implementation direction.

## Safety Statement

No AMN2 code, template change, route behavior change, runtime route, reconciliation route, attach route, import route, backfill route, polling scheduler, collector, background worker, `/api/clients` CRUD, operation queue implementation, config delivery route, token issue/revoke route, token storage change, live VPS command, SSH command, shell command against VPS, package apply, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config generation, config delivery, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.
