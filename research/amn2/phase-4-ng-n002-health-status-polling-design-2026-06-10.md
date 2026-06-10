# Phase 4 NG-N002: health/status polling design 2026-06-10

Purpose: close `NG-N002` as an AMN3 docs-only health/status polling contract. This document defines the safe shape of future polling, refresh and status surfaces before any AMN2 scheduler, collector, route expansion, live VPS polling or write/config behavior exists.

## Decision

```text
slice_id: NG-N002
slice_name: health/status polling design
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
polling_implemented: no
scheduler_implemented: no
collector_implemented: no
background_worker_implemented: no
route_behavior_changed: no
runtime_route_added: no
operation_queue_changed: no
write_crud_implemented: no
fake_runner_implemented: no
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
required_gate_for_local_polling_implementation: P4-NG-HEALTH-POLLING-LOCAL-IMPLEMENTATION-GATE
required_gate_for_real_target_polling: P4-NG-VPS-READONLY-BASELINE-2026-06-10
required_gate_for_live_write: P4-NG-WRITE-API-LIVE-GATE
required_gate_for_config_delivery: P4-NG-CONFIG-DELIVERY-GATE
selected_next_slice: NG-N001 attach-existing-server read-only reconciliation gate design
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
selected_next_slice_status: completed in research/amn2/phase-4-ng-n001-attach-existing-server-read-only-reconciliation-gate-design-2026-06-10.md
```

## Sources Reused

- `research/amn2/phase-4-read-only-api-status-design-2026-06-09.md`;
- `research/amn2/phase-4-read-only-api-status-schema-implementation-2026-06-09.md`;
- `research/amn2/phase-4-endpoint-taxonomy-route-policy-docs-implementation-2026-06-09.md`;
- `research/amn2/phase-4-aggregate-metrics-privacy-boundary-implementation-2026-06-09.md`;
- `research/amn2/phase-4-wapi-i004-operation-status-model-2026-06-10.md`;
- `research/amn2/phase-4-wapi-i005-web-panel-gated-action-labels-2026-06-10.md`;
- `research/amn2/phase-4-ng-n003-operation-queue-design-2026-06-10.md`;
- `research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-10.md`;
- `research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md`.

Upstream repositories remain research-only idea sources. No GPL or upstream code, templates, manager implementations, workflows, polling loops or API code were copied.

## VPS Evidence Boundary

`NG-N002` did not poll real target services, run SSH, open a tunnel, call live loopback endpoints, call public endpoints, inspect live systemd state, sample ports or query production peer/user data.

Past accepted Phase 3 and service-mode evidence remains historical context only. It does not authorize new polling, new live checks or any background worker in this slice.

## Polling Goal

Future health/status polling must answer operator questions with aggregate, safe and stale-aware status:

- is the private/local product surface healthy enough for read-only navigation;
- are known components in a safe summarized state;
- is a status value fresh, stale, blocked by gate or unknown;
- is further action blocked by a named gate rather than by an implementation error.

It must not:

- expose peer/user identities, endpoints, hostnames, IP addresses, ports, keys, tokens, configs, QR, `vpn://`, command output or logs;
- create, update, disable, revoke, sync, apply, restart, reload or mutate anything;
- convert read-only telemetry into write authorization;
- mark unavailable or unpolled systems as healthy by default;
- run real target polling before a named read-only VPS gate.

## Polling Tiers

```text
tier_0_policy_static
tier_1_local_private_api_summary
tier_2_local_loopback_service_summary
tier_3_real_target_read_only_summary
tier_blocked_secret_or_high_cardinality
```

Tier meanings:

- `tier_0_policy_static`: static docs/config-policy status only; allowed as docs/local metadata.
- `tier_1_local_private_api_summary`: future local-only reads from existing private read-only summaries, after local implementation gate.
- `tier_2_local_loopback_service_summary`: future loopback-only service health, after local implementation gate and without public exposure.
- `tier_3_real_target_read_only_summary`: future live target read-only sampling, only after `NG-V001` or another explicit read-only VPS named gate.
- `tier_blocked_secret_or_high_cardinality`: peer/user/config/endpoint/detail polling is blocked unless a later design proves safe aggregation and a gate approves it.

## Safe Status Fields

Future status/polling records may expose only safe fields:

```text
health_status
status_reason
poll_source_class
poll_mode
poll_tier
component
component_ref
component_class
last_checked_at
data_age_seconds
staleness_state
sample_window_seconds
aggregate_count
healthy_count
degraded_count
unavailable_count
unknown_count
blocked_count
gate_name
live_write_authorized
correlation_id
audit_event_ref
```

`component_ref` must be opaque. It must not contain peer names, user names, hostnames, IP addresses, ports, endpoints, public keys or secrets.

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

If a source can only provide forbidden fields, the poller must either aggregate/redact before exposure or mark the source as blocked.

## Status Vocabulary

```text
healthy
degraded
unavailable
unknown
stale
blocked_by_gate
not_implemented
redaction_failed
```

Recommended reason codes:

```text
aggregate_only
gate_required
poll_not_implemented
source_not_configured
source_stale
local_loopback_unreachable
read_scope_denied
timeout
service_unavailable
redaction_failed
secret_marker_detected
public_exposure_blocked
live_write_blocked
config_delivery_blocked
```

`unknown`, `stale`, `blocked_by_gate` and `not_implemented` are safe states. They must not be collapsed into `healthy`.

## Polling Modes

```text
manual_refresh_only
cached_summary
scheduled_local_polling
read_only_vps_gate_polling
disabled_by_gate
```

Current mode for this slice is `manual_refresh_only` as a design term only. No manual refresh route or collector is implemented here.

Future scheduled polling must define:

- minimum poll interval;
- timeout;
- retry and backoff rules;
- staleness TTL;
- cache invalidation rules;
- audit-safe failure behavior;
- rate limits for any public-adjacent surface.

Those values are implementation-gate decisions, not `NG-N002` runtime changes.

## Component Classes

Allowed component classes:

```text
web_admin_private_loopback
bot_service
private_read_only_api
local_agent_summary
aggregate_metrics
operation_status_summary
queue_status_summary
target_server_read_only_summary
policy_gate_status
```

Blocked component classes:

```text
peer_detail
user_detail
config_artifact
token_lifecycle_write
backup_import_reboot
public_endpoint
server_cleanup
raw_protocol_manager
```

## Route Boundary

`NG-N002` does not add routes or change existing responses.

Current private/local read-only grouping remains:

```text
GET /api/servers
GET /api/servers/{server_name}/summary
GET /api/integration/status
GET /api/local-agent/runtime/summary
GET /api/metrics/summary
GET /api/users/summary
```

Future polling may reuse existing safe summary surfaces or propose a local-only status summary route, but only under a separate implementation gate with drift tests. No public OpenAPI/docs exposure is authorized.

## UI And Operator Semantics

Future web/admin UI should distinguish:

- `Healthy`: fresh aggregate status from an allowed source;
- `Degraded`: fresh aggregate status with safe degraded reason;
- `Unavailable`: allowed source could not be reached or returned safe failure;
- `Unknown`: no safe data exists yet;
- `Stale`: data exists but exceeded TTL;
- `Named gate required`: polling source requires a gate;
- `Not implemented`: design exists but local implementation does not.

UI text must avoid implying that a gated, stale, unknown or not implemented source is healthy.

## Operation Queue Binding

`NG-N003` queue/status design can consume polling summaries only as safe aggregate status. Polling must not:

- trigger queue execution;
- retry operations;
- cancel operations;
- promote `deferred` to `running`;
- change `live_write_authorized`;
- infer successful live mutation from read-only health.

Queue-related polling may expose counts by safe status class, but not per-peer/per-user operation details.

## Required RED Tests Before Implementation

Before any AMN2 health/status polling implementation, tests must prove:

- no polling scheduler, collector, worker or route exists before an implementation gate;
- no real target service polling runs without `NG-V001` or another explicit read-only VPS gate;
- status payloads contain no raw token, token hash, Authorization header, session cookie, endpoint, host, hostname, IP, port, peer/user identifier, public key, private key, PSK, config, QR, `vpn://`, command output or logs;
- stale, unknown and blocked states are not converted to healthy;
- a redaction failure produces `redaction_failed`, not a partially leaked payload;
- failed polling cannot restart/reload services or mutate state;
- polling cannot call `/api/clients` write CRUD, token issue/revoke, config delivery, backup/import/reboot or Local Agent mutations;
- public API `3040`, direct public web/admin `3030`, TCP `80/443` and Caddy/HTTPS/domain cutover remain unchanged;
- aggregate counts cannot be used to reconstruct peer/user identity;
- rate-limit/backoff behavior is tested before any scheduled polling;
- route drift tests keep the current six private/local read-only routes unchanged unless a separate route gate approves expansion.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: NG-N002 docs-only health/status polling design with live_write_authorized: no
no_go_scope: AMN2 polling implementation, scheduler implementation, collector implementation, route implementation, route behavior change, live target polling, SSH/VPS commands, `/api/clients` runtime CRUD, token issue/revoke routes, config delivery routes, live write, public exposure, production mutation
defer_scope: local polling implementation gate, real target read-only VPS polling gate, peer/user detail visibility, public/self-service status, config/read-delivery routes, write API live gate, destructive operations
```

## Handoff

`NG-N002` is closed. `NG-N001` was selected next and later closed in `research/amn2/phase-4-ng-n001-attach-existing-server-read-only-reconciliation-gate-design-2026-06-10.md`, because safe health/status vocabulary existed and the next planning gap was how to reconcile an already-existing target server without attach/write/backfill behavior. `NG-N004` was then closed as docs-only candidate registry update after every gate decision. `NG-S001` was then closed as docs-only status/transfer synchronization. `NG-S002` and `NG-S004` were then closed together as docs-only handoff and visible-plan maintenance. `NG-X003` was then closed as docs-only stale wording cleanup. `NG-X001` was then closed as docs-only gate naming consistency. `NG-X002` was then closed as docs-only Russian-first operator wording polish. Очередь default docs-only cosmetic теперь закрыта.

## Safety Statement

No AMN2 code, template change, route behavior change, runtime route, polling scheduler, collector, background worker, `/api/clients` CRUD, fake-runner code, operation queue implementation, config delivery route, token issue/revoke route, token storage change, live VPS command, SSH command, shell command against VPS, package apply, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config generation, config delivery, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.
