# P4-NG Named Gate / Write API Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** перейти от закрытой default local-only Phase 4 очереди к управляемому named-gate этапу для VPS/read-only baseline и будущего write API design без неявного live/write допуска.

**Architecture:** AMN3 остается source of truth для gate charter, status, evidence и backlog. AMN2 получает только отдельные implementation/design slices после явного выбора; live VPS, public exposure, config delivery and write API остаются закрыты до named gate.

**Tech Stack:** AMN3 Markdown docs/evidence, AMN2 Python/FastAPI/docs/tests for future local-only design slices, PowerShell/OpenSSH only after explicit read-only VPS gate approval.

---

## Current Boundary

Default local-only Phase 4 implementation queue is closed after:

- `P4-C009`;
- `P4-I002`;
- route/secret gate planning;
- `P4-I003` design/plan/implementation;
- `P4-I004`;
- `P4-N003`;
- `P4-I005`;
- `P4-N004`;
- `P4-N001`;
- `P4-N002`;
- `P4-X003`;
- `P4-X002`;
- `P4-X001`;
- `P4-I001` closure.

This plan starts the next stage:

```text
stage_id: P4-NG
stage_name: Named Gate / Write API Readiness
default_mode: docs-only gate planning
first_live_gate_candidate: NG-V001 read-only VPS baseline check
write_api_live_status: blocked until separate P4-WRITE-API-LIVE-GATE
```

## Closed And Removed From Active Plan

- [x] **NG-C001: create named gate charter**
  - Closed by `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md`.
  - Defines gate shape, allowed fields, blocked actions, go/no-go and safe evidence rules.

- [x] **NG-C002: restate safety boundary before any gate**
  - Closed by `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md`.
  - Keeps public `3040`, direct public `3030`, Caddy/HTTPS, config delivery, `/api/clients` write CRUD, Local Agent mutations, backup/import/reboot and production peer/user mutation closed.

## Active Remaining Plan

### Критичные

- [ ] **NG-C003: approve secrets policy for gate outputs**

  Scope:

  - Evidence may contain only boolean/status summaries.
  - Evidence must not include `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, `.conf`, QR payload, `vpn://`, backup contents, endpoint values, session cookies or full logs.

  Done when:

  - A reusable secrets policy block is present in the selected gate evidence template.

- [ ] **NG-C004: define go/no-go format for all gates**

  Scope:

  - Every gate must end with `go`, `no-go`, or `defer`.
  - Any failed preflight must default to `no-go` or `defer`, not partial execution.

  Done when:

  - `go_no_go_decision` format is present in the active gate template.

- [ ] **NG-C005: keep write API live work blocked**

  Scope:

  - `/api/clients` write CRUD, peer apply/revoke/sync, config delivery and token issue/revoke/rotate routes remain blocked.
  - Future write API work starts as local-only design/contract tests.

  Done when:

  - The selected write API slice explicitly says `live_write_authorized: no`.

### Очень Важные

- [ ] **NG-V001: run read-only VPS baseline gate**

  Gate name:

  ```text
  P4-NG-VPS-READONLY-BASELINE-2026-06-10
  ```

  Allowed actions after explicit operator approval:

  - SSH transport check to operator-provided target only.
  - Read-only service status for `amneziya-web` and `amneziya-bot`.
  - Read-only loopback `/login` check on `127.0.0.1:3030`.
  - Read-only listener checks for `3030`, `3040`, `80`, `443`.
  - Boolean-only check that `VPS_APPLY_ENABLED=false` exists; do not print `.env`.

  Blocked actions:

  - package apply;
  - service restart/enable/disable;
  - firewall/reverse proxy edits;
  - peer apply/revoke/sync;
  - config delivery;
  - token issue/revoke;
  - backup/import/reboot;
  - public exposure changes.

  Done when:

  - Evidence records safe summary only and no secret-bearing data.

- [ ] **WAPI-V001: write API threat model**

  Scope:

  - Threat model `/api/clients`, peer lifecycle, config delivery coupling, token scopes, audit, rollback, locking and partial failures.
  - No AMN2 route implementation yet.

  Done when:

  - A docs-only threat model identifies risk classes and required tests before implementation.

- [ ] **WAPI-V002: write API route taxonomy**

  Scope:

  - Split future routes into `clients`, `peers`, `configs`, `operations`, `audit/status`.
  - Mark every route as read-only, state-write, secret-read, destructive or public-exposure.

  Done when:

  - Future route names are proposed without adding runtime routes.

- [ ] **WAPI-V003: local fake-runner contract**

  Scope:

  - Design fake-runner contracts for create/revoke/sync before any live runner.
  - All tests must run locally without SSH.

  Done when:

  - AMN2 implementation plan can start with RED tests and fake runner only.

- [ ] **WAPI-V004: idempotency, locking and partial-failure model**

  Scope:

  - Define request idempotency keys, operation locks, retry behavior, partial apply/revoke failure states and rollback evidence.

  Done when:

  - Design can explain what happens if local DB write succeeds but remote mutation fails, or vice versa.

- [ ] **WAPI-V005: write API audit/redaction requirements**

  Scope:

  - Audit must include operation metadata, actor, scope, result and correlation id.
  - Audit must never include raw tokens, configs, keys, PSK, QR, `vpn://` or endpoint secrets.

  Done when:

  - Tests are specified before route implementation.

### Важные

- [ ] **WAPI-I001: `/api/clients` design without live CRUD**

  Scope:

  - Design request/response schema for future client create/list/revoke/status.
  - No runtime route expansion until a separate AMN2 local implementation plan is approved.

- [ ] **WAPI-I002: decouple config delivery from client creation**

  Scope:

  - Peer/client creation must not automatically publish `.conf`, QR or `vpn://`.
  - Config delivery requires a separate secret-read gate.

- [ ] **WAPI-I003: scoped write-token model**

  Scope:

  - Define minimal scopes such as `client:write`, `client:revoke`, `operation:read`.
  - Explicitly reject broad admin-equivalent tokens.

- [ ] **WAPI-I004: operation status model**

  Scope:

  - Define `planned`, `dry_run_passed`, `running`, `succeeded`, `failed`, `rolled_back`, `deferred`.
  - Include safe fields only.

- [ ] **WAPI-I005: web-panel gated action labels**

  Scope:

  - Future write actions must be visibly gated and require confirmation.
  - No template/route behavior changes until a selected AMN2 slice.

### Нормальные

- [ ] **NG-N001: attach-existing-server read-only reconciliation gate design**

  Scope:

  - Read-only detection only.
  - No attach/write/backfill until separate gate.

- [ ] **NG-N002: health/status polling design**

  Scope:

  - Aggregate/safe telemetry only.
  - No peer/user leakage.

- [ ] **NG-N003: operation queue design after write API contract**

  Scope:

  - Queue/cancel/retry UX only after operation model is stable.

- [ ] **NG-N004: update candidate registry after every gate decision**

  Scope:

  - Change `priority`, `required_gate`, `recommendation` or `implementation_status` only with evidence.

### Простые

- [ ] **NG-S001: keep AMN3 status/transfer current after each gate**

  Files:

  - `docs/PROJECT_STATUS_CURRENT.ru.md`
  - `research/amn2/transfer-backlog.md`

- [ ] **NG-S002: keep next-chat handoff current**

  File:

  - `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`

- [ ] **NG-S003: create reusable named-gate evidence template**

  Scope:

  - Template only; no live command.

- [ ] **NG-S004: maintain visible active plan**

  Rule:

  - When a task closes, remove it from the active plan, show the full remaining plan and give a recommendation.

### Косметические

- [ ] **NG-X001: gate naming consistency**

  Scope:

  - Use `P4-NG-*` for gate-stage docs and evidence.

- [ ] **NG-X002: Russian-first operator wording polish**

  Scope:

  - Russian headings and operator instructions; keep technical ids/routes unchanged.

- [ ] **NG-X003: stale wording cleanup**

  Scope:

  - Remove wording that sounds like implicit authorization for live/write/public/config work.

## First Recommendation

Start with `NG-C003` and `NG-C004` next. They are docs-only and make `NG-V001` safer by locking secrets policy and go/no-go format before any read-only VPS command is proposed.

Do not run `NG-V001` until the operator explicitly approves the gate and provides the target SSH alias/host outside repository secrets.
