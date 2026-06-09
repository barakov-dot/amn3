# Phase 4 P4-N002 Protocol Manager Interface Checklist - 2026-06-09

Status: completed as AMN3 docs-only/local-only design checklist.

AMN3 baseline before this checklist:

```text
3577bc6 Record Phase 4 docs status drift sync
```

## Decision

```text
candidate_id: P4-N002
priority: normal
gate: local-only
status: completed-docs-only
AMN2 code changes: none
live VPS commands: none
```

`P4-N002` converts PRVTPRO manager-architecture ideas and existing AMN2 remote-operation/export contracts into a safe interface checklist for future protocol-manager work. It does not create a manager implementation, route, API scope, config delivery flow, Local Agent route, background job runner or VPS operation.

## Sources Reviewed

- `research/upstreams/prvtpro-amnezia-web-panel-manager-architecture.md`
- `research/amn2/manager-config-export-contract.md`
- `research/amn2/manager-config-export-contract-implementation.md`
- `research/amn2/remote-operations-inventory.md`
- `research/amn2/remote-partial-failure-contract-2026-06-06.md`
- `research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md`
- `docs/superpowers/specs/2026-05-30-remote-operation-runner-design.md`
- AMN2 read-only source inspection: `app/server/operations.py`, `app/server/operation_runner.py`, `tests/server/test_operation_runner.py`, `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`, `app/security/surface_policy.py`

## Existing AMN2 Baselines To Reuse

- `RemoteOperation` / `OperationPlan` already model risk class, secret refs, side effects, consistency status, safe metadata and rollback note.
- `RemoteOperationRunner` first slice applies only `read-only-remote` operations; state-changing plans stay dry-run until a separate gate.
- Partial-failure metadata exists for remote-changed/local-failed and local-changed/remote-failed outcomes.
- `ConfigExportResult` / `ConfigExportArtifact` exists as a typed no-route export adapter for secret-bearing config artifacts.
- Route/auth/secret policy docs already block `config:read`, `/api/clients` write CRUD, public config delivery, Local Agent configs/mutations, backup/import/reboot and public exposure until separate gates.

## License Boundary

PRVTPRO/Amnezia-Web-Panel remains GPL-3.0 research-only. Allowed transfer:

- domain ideas;
- risk taxonomy;
- interface questions;
- capability checklist language.

Blocked transfer:

- code;
- UI/templates;
- shell flows;
- Dockerfiles;
- command strings;
- protocol manager implementation details;
- config templates or generated artifacts.

## Protocol Manager Interface Checklist

Any future protocol manager proposal must define these fields before implementation:

```text
ProtocolManagerDescriptor
  protocol_id
  display_name
  runtime_modes
  supported_capabilities
  default_risk_classes
  secret_surfaces
  local_side_effects
  remote_side_effects
  required_route_policy_entries
  required_scopes
  required_gates
  test_double_strategy
```

Capabilities must be explicit, not inferred from method names:

- `detect.read_only`
- `status.read_only`
- `traffic.aggregate_read`
- `config.export`
- `peer.plan_apply`
- `peer.plan_revoke`
- `service.plan_install`
- `service.plan_uninstall`
- `service.plan_restart`
- `backup.preview`
- `backup.apply_restore`

Unsupported capabilities must return stable categories such as `unsupported_capability`, `unsupported_runtime_mode`, `unsupported_target_client` or `blocked_by_gate`, not raw exceptions.

## Required Method Boundaries

Read-only methods:

- may return safe status, capability and aggregate telemetry fields only;
- must use read-only command policy or an equivalent allowlist for live sampling;
- must not return `.env`, `servers.yml`, endpoint values, peer public keys, raw configs, QR payloads, `vpn://`, tokens, hashes or full logs;
- require a named VPS read-only gate if they sample fresh live runtime state.

Config export methods:

- must go through `ConfigExportRequest` / `ConfigExportResult` or a compatible typed artifact contract;
- must classify every payload as `client-config-secret` or safer;
- must keep payload out of audit, logs, errors and safe metadata;
- must not create `config:read`, public/self-service delivery, Local Agent `/configs` or new download routes without a separate config/public gate.

State-changing methods:

- must build a `RemoteOperation` and `OperationPlan` before any apply path exists;
- must expose dry-run metadata with risk class, side effects, idempotency/recovery notes and redacted audit summary;
- must use fake-runner tests before any real VPS gate;
- must prove partial-failure behavior and recovery-note redaction;
- must keep `VPS_APPLY_ENABLED=false` outside an explicitly named live gate.

Destructive methods:

- include uninstall, clear server, raw config save/apply, firewall rewrite, service restart/reboot, restore/import and backup apply;
- require plan preview, explicit confirmation, destructive audit, backup/recovery note and a separate dangerous-operation gate;
- are not part of Phase 4 default mode.

## Gate Classification

Local-only allowed now:

- this checklist;
- synthetic capability registry docs/tests;
- fake-runner contract tests;
- no-route config export adapters;
- static read-only status wording;
- surface-policy documentation.

Requires a named VPS gate:

- attach-existing-server live detection;
- fresh service status polling;
- real remote telemetry sampling;
- any deployment or controller-to-agent connectivity check.

Blocked until separate write/config/public gate:

- `/api/clients` write CRUD;
- peer apply/revoke/sync from API/web/bot/default mode;
- secret-bearing config delivery routes;
- public/self-service config delivery;
- Local Agent mutation/config routes;
- raw server config save/apply;
- backup/import/reboot;
- public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover.

## Minimum Future Test Checklist

Before an AMN2 implementation slice can introduce or extend protocol manager behavior, it must include local tests for:

- capability registry entries and unsupported capability categories;
- route/auth/scope policy entries for every new surface;
- risk class and secret class binding;
- fake runner plan generation without real SSH;
- no raw command strings reaching UI/API safe metadata;
- no secrets in command preview, stdout/stderr, exceptions, audit or docs;
- dry-run metadata for state-changing operations;
- partial-failure consistency status and recovery note;
- config export artifact typing and safe metadata, if config artifacts are involved;
- marker scan proving no public/write/config/live gate is accidentally enabled.

## Non-actions

No AMN2 code was changed.

No live VPS command was run.

No public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` write CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was authorized.

No upstream PRVTPRO/KYORESUAS code, UI, templates, scripts, command strings, Dockerfiles or manager implementations were copied.

## Verification

```text
git diff --check: passed; CRLF normalization warnings only
active next-step stale scan for P4-N002: no matches
unsafe enabled-marker scan on changed files: no matches
```

## Result

`P4-N002` is closed as a protocol-manager interface checklist. The next safest default item is cosmetic/docs-only polish, with `P4-X003` as the preferred candidate because it keeps operator handoff language Russian-first and reduces drift. `P4-I001` remains available only if another private-panel read-only UX evidence pass is needed.
