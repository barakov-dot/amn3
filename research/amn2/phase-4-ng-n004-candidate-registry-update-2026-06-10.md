# Phase 4 NG-N004: candidate registry update after gate decisions 2026-06-10

Purpose: close `NG-N004` as an AMN3 docs-only candidate registry maintenance slice after the recent P4-NG/WAPI decisions. This document records that the registry was reviewed and synchronized with closed evidence for operation queue design, health/status polling design and attach-existing-server reconciliation design.

## Decision

```text
slice_id: NG-N004
slice_name: update candidate registry after every gate decision
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
candidate_registry_updated: yes
implementation_started: no
route_behavior_changed: no
runtime_route_added: no
polling_implemented: no
reconciliation_implemented: no
operation_queue_implemented: no
attach_implemented: no
import_implemented: no
backfill_implemented: no
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
selected_next_slice: NG-S001 keep AMN3 status/transfer current
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
selected_next_slice_status: completed in research/amn2/phase-4-ng-s001-status-transfer-sync-2026-06-10.md
```

## Registry Maintenance Scope

Allowed changes:

- update `implementation_status` when a docs-only boundary was closed with evidence;
- update `recommendation` when a candidate now has a safer next boundary;
- update `required_gate` wording only when the evidence clarifies an existing gate class;
- add source/evidence notes for closed gate decisions.

Blocked changes:

- no candidate can become implementation-ready without a separate selected implementation plan;
- no candidate can move from `requires VPS gate` to live action without explicit gate approval;
- no candidate can move from `blocked until separate write/config/public gate` to allowed work in this slice;
- no GPL/upstream code, templates, manager implementations or workflows can be copied.

## Registry Updates Applied

`P4-I007` health/status polling against real target services:

- already linked to `NG-N002`;
- remains `requires VPS gate` for real service polling/sampling;
- recommendation remains aggregate-only/stale-aware boundary first.

`P4-N005` attach existing server reconciliation:

- already linked to `NG-N001`;
- remains `requires VPS gate` for real target detection;
- attach/import/backfill remains behind a separate write/backfill gate.

`P4-N006` background jobs, cancellation and operation queue:

- updated in `research/amn2/phase-4-candidate-registry-2026-06-09.md`;
- now references `NG-N003` as the closed docs-only operation queue design boundary;
- remains `requires VPS gate` for real operations and separate implementation/write gates before any runner, queue or live execution.

## Registry Audit Result

The active registry now records the recent design boundaries:

```text
NG-N003 -> P4-N006 operation queue / background jobs boundary
NG-N002 -> P4-I007 health/status polling boundary
NG-N001 -> P4-N005 attach-existing-server reconciliation boundary
```

These boundaries do not authorize AMN2 code changes, runtime route changes, queue/scheduler/collector/reconciliation implementations, real target polling, attach/import/backfill, public exposure, config delivery or production mutation.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: NG-N004 docs-only candidate registry maintenance with live_write_authorized: no
no_go_scope: AMN2 implementation, runtime route expansion, route behavior change, real target polling, reconciliation implementation, operation queue implementation, attach/import/backfill, SSH/VPS commands, `/api/clients` runtime CRUD, token issue/revoke routes, config delivery routes, live write, public exposure, production mutation
defer_scope: local implementation gates, real target read-only VPS detection gate, live write gate, attach/write/backfill gate, config delivery gate, public exposure gate
```

## Handoff

`NG-N004` is closed. `NG-S001` was selected next and later closed in `research/amn2/phase-4-ng-s001-status-transfer-sync-2026-06-10.md`, because registry maintenance was recorded and the remaining safe work was status/transfer synchronization before any live gate discussion. `NG-S002` and `NG-S004` were then closed together as docs-only handoff and visible-plan maintenance. `NG-X003` was then closed as docs-only stale wording cleanup. Current next recommendation after `NG-X003` closure is `NG-X001` gate naming consistency with `live_write_authorized: no`.

## Safety Statement

No AMN2 code, template change, route behavior change, runtime route, candidate implementation, reconciliation route, attach route, import route, backfill route, polling scheduler, collector, background worker, operation queue implementation, `/api/clients` CRUD, config delivery route, token issue/revoke route, token storage change, live VPS command, SSH command, shell command against VPS, package apply, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config generation, config delivery, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.
