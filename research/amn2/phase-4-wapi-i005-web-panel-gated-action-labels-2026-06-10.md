# Phase 4 WAPI-I005: web-panel gated action labels 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `WAPI-I005` как AMN3 docs-only label/UX contract для будущей web-panel поверхности write/config/live действий. Документ фиксирует, как панель должна различать read-only metadata, local operation planning, dry-run, blocked/deferred named gates, config delivery gates, live write gates and destructive/public gates before any AMN2 template, route, behavior or runtime implementation.

## Decision

```text
slice_id: WAPI-I005
slice_name: web-panel gated action labels
slice_mode: docs-only
result: closed
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
template_changed: no
route_behavior_changed: no
ui_implementation_changed: no
fake_runner_implemented: no
operation_queue_implemented: no
client_routes_implemented: no
write_crud_implemented: no
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
required_gate_for_template_implementation: P4-NG-WAPI-PANEL-LABELS-LOCAL-IMPLEMENTATION-GATE
required_gate_for_live_write: P4-NG-WRITE-API-LIVE-GATE
required_gate_for_config_delivery: P4-NG-CONFIG-DELIVERY-GATE
required_gate_for_public_exposure: P4-NG-PUBLIC-EXPOSURE-GATE
selected_next_slice: NG-N003 operation queue design after write API contract
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
selected_next_slice_status: completed in research/amn2/phase-4-ng-n003-operation-queue-design-2026-06-10.md
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
- `research/amn2/phase-4-service-mode-status-wording-implementation-2026-06-09.md`;
- `research/amn2/phase-4-bot-admin-read-only-labels-implementation-2026-06-09.md`.

KYORESUAS and PRVTPRO remain product/architecture signals only. No upstream code, route layout, command strings, service logic, UI, templates, workflows or manager implementations are copied.

## VPS Evidence Boundary

Previous VPS work remains historical evidence only. Accepted labels such as `dry_run_only_pass`, `verified_live_single_disposable_peer`, `service_mode_loopback_baseline` and `vps_apply_disabled` may inform wording, but they do not authorize live write, config delivery, public exposure, token lifecycle routes, Local Agent mutation or destructive operations.

This slice did not run SSH, did not query VPS state, did not open a tunnel and did not change AMN2 templates or routes.

Future labels, tooltips, warnings, empty states and status text must not expose endpoints, SSH aliases, hostnames, IPs, ports, peer keys, private keys, PSK, `.env`, `servers.yml`, command output, logs, `.conf`, QR payloads, QR images, `vpn://`, archive paths, share links or download URLs.

## Labeling Goal

Future web-panel labels must make the operation class visible before an operator can mistake a gated action for a completed live action.

The panel should distinguish:

- existing read-only metadata;
- local operation planning;
- dry-run result with no live mutation;
- blocked/deferred write because a named live gate is missing;
- blocked config delivery because a secret-read/config gate is missing;
- blocked public exposure because a public gate is missing;
- blocked destructive/server operations;
- recovery/attention states after future authorized operation failure;
- authorized live success only after an explicit gate and actual execution.

Labels are not authorization. A disabled label, badge or tooltip must not unlock an action by itself.

## Label Vocabulary

Future web-panel labels should use controlled wording:

| State or class | Label intent | Must imply | Must not imply |
| --- | --- | --- | --- |
| `read-only` | read-only metadata | view/list/status only | write, sync, config delivery |
| `local_plan` | planned locally | operation intent recorded or proposed locally | live server changed |
| `dry_run_passed` | dry-run passed, no live mutation | validation passed without live write | peer/config was applied |
| `dry_run_failed` | dry-run failed, no live mutation | validation failed safely | partial live change |
| `deferred` | blocked by named gate | operator decision/gate needed | action is queued for live execution |
| `locked` | waiting for target lock | another operation holds safe lock | failure or success |
| `rejected` | rejected by policy | scope/policy/input denied | retry will succeed without changes |
| `config_delivery_blocked` | config delivery blocked | `.conf`, QR, `vpn://` require config gate | config is available |
| `live_write_blocked` | live write requires gate | remote mutation is blocked | VPS was touched |
| `public_exposure_blocked` | public exposure blocked | public/API/domain change requires gate | listener/domain exists |
| `destructive_operation_blocked` | destructive action blocked | backup/import/reboot/service mutation requires gate | action can be confirmed now |
| `attention_required` | recovery/reconciliation needed | safe follow-up required | secrets or raw logs are visible |
| `succeeded` | authorized execution succeeded | only after selected implementation and gate | default/fake/local success |

`succeeded` must not appear for fake/default/local planning mode. In default mode, prefer `planned locally`, `dry-run passed, no live mutation`, `blocked by named gate` or `rejected by policy`.

## Surface-Specific Guidance

### Clients And Configurations

Future `/api/clients`-adjacent panel views should show:

- client list/detail as `read-only metadata` until implementation gate exists;
- create/update/disable/revoke as `local plan only` or `blocked by named gate` in default mode;
- live peer apply/revoke/sync as `live write requires gate`;
- `.conf`, QR, `vpn://`, archives and share/download links as `config delivery blocked`;
- live peers discovered outside AMN2 as `read-only inventory reference`, not managed local clients.

The panel must not show a download/share/config action as available merely because a client exists.

### Operations

Future operation surfaces should map WAPI-I004 statuses directly:

- `planned` -> `planned locally`;
- `dry_run_passed` -> `dry-run passed, no live mutation`;
- `dry_run_failed` -> `dry-run failed, no live mutation`;
- `deferred` -> `blocked by named gate`;
- `locked` -> `waiting for target lock`;
- `rejected` -> `rejected by policy`;
- `attention_required` statuses -> `recovery/reconciliation needed`;
- `succeeded` -> `authorized execution succeeded`.

Operation labels must include safe gate names or reason codes when they explain a blocked state, but must not include raw target identifiers or secret-bearing output.

### Server, Public Exposure And Destructive Actions

Future server-management labels should keep these lanes separate:

- read-only service/listener/status checks;
- public exposure changes such as public API `3040`, direct public web/admin `3030`, domain/Caddy/HTTPS;
- service/firewall/reverse proxy mutation;
- backup/import/reboot/destructive actions.

Public/destructive labels must be blocked by default and must not be rendered as normal confirmation buttons before their separate named gates exist.

## Interaction Rules

Future implementation should follow these rules:

- read-only actions may be normal links/buttons only when they stay within existing read-only scope;
- gated write/config/public/destructive candidates should be disabled or non-submitting controls until their implementation gate exists;
- a disabled control must show a short label and, when useful, a tooltip or adjacent status that names the required gate;
- confirmation text is required only after an implementation gate selects the behavior; this docs-only slice does not design final confirmation copy;
- labels must not include secrets, endpoints, command output, raw route payloads or full logs;
- labels must not say `applied`, `synced`, `delivered`, `download ready`, `public`, `enabled`, `rebooted` or `succeeded` unless the corresponding operation actually completed under an approved gate.

## Required Tests Before Implementation

Any future AMN2 implementation plan for web-panel gated action labels must start with RED tests for:

- write/config/public/destructive candidate controls are not active submit controls before an implementation gate;
- create/update/disable/revoke labels distinguish `local plan only` from live mutation;
- live-required actions show `live write requires gate` or equivalent safe controlled wording;
- config actions show `config delivery blocked` or equivalent safe controlled wording and do not show `.conf`, QR, `vpn://`, archive, share link or download URL;
- public exposure actions show blocked public gate wording and do not imply public API `3040`, direct web/admin `3030`, domain/Caddy/HTTPS are active;
- destructive actions show blocked destructive gate wording and do not render normal confirmation controls by default;
- `dry_run_passed` labels include `no live mutation`;
- `deferred` labels mention named gate/blocked state;
- `succeeded` labels cannot appear in fake/default/local mode;
- operation labels use controlled status/reason vocabulary from WAPI-I004;
- UI text excludes raw token, token hash, Authorization header, endpoint, host/IP/port, peer public key, private key, PSK, command output, logs, `.env`, `servers.yml`, `.conf`, QR and `vpn://`;
- route/template drift tests keep labels aligned with policy docs and candidate route contracts;
- no POST/write/config delivery behavior changes are introduced by label-only implementation.

## NG-N003 Handoff

`NG-N003` was the recommended next docs-only slice and was later closed in `research/amn2/phase-4-ng-n003-operation-queue-design-2026-06-10.md`:

```text
slice_id: NG-N003
slice_name: operation queue design after write API contract
slice_mode: docs-only
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
live_vps_commands: no
config_delivery: no
```

Reason: the WAPI contract chain now defines route taxonomy, fake-runner expectations, idempotency/locks, audit/redaction, operation statuses, scoped tokens, config decoupling, `/api/clients` boundaries and panel labels. `NG-N003` captured queue/cancel/retry semantics as docs-only planning, not implementation. `NG-N002` was then closed as docs-only health/status polling design. `NG-N001` was then closed as docs-only attach-existing-server read-only reconciliation gate design. `NG-N004` was then closed as docs-only candidate registry update after every gate decision. `NG-S001` was then closed as docs-only status/transfer synchronization. `NG-S002` and `NG-S004` were then closed together as docs-only handoff and visible-plan maintenance. `NG-X003` was then closed as docs-only stale wording cleanup. `NG-X001` was then closed as docs-only gate naming consistency. `NG-X002` was then closed as docs-only Russian-first operator wording polish. Очередь default docs-only cosmetic теперь закрыта.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: NG-N003 docs-only operation queue design after write API contract with live_write_authorized: no
no_go_scope: AMN2 template implementation, route implementation, `/api/clients` runtime CRUD, fake-runner code implementation, operation queue implementation, token issue/revoke route implementation, config delivery route implementation, live write, public exposure, SSH/VPS commands, production mutation
defer_scope: AMN2 local implementation gate, live peer mutation, config/read-delivery routes, public/self-service routes, destructive operations, token lifecycle API routes, OpenAPI public exposure
```

## Safety Statement

No AMN2 code, template change, route behavior change, runtime route, `/api/clients` CRUD, fake-runner code, operation queue, config delivery route, token issue/revoke route, token storage change, live VPS command, SSH command, shell command, package apply, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config generation, config delivery, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.
