# P4-NG: план Named Gate / Write API Readiness

> **Для agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Цель:** перейти от закрытой default local-only Phase 4 очереди к управляемому named-gate этапу для VPS/read-only baseline и будущего write API design без неявного live/write допуска.

**Архитектура:** AMN3 остается source of truth для gate charter, status, evidence и backlog. AMN2 получает только отдельные implementation/design slices после явного выбора; live VPS, public exposure, config delivery and write API остаются закрыты до named gate.

**Стек:** AMN3 Markdown docs/evidence, AMN2 Python/FastAPI/docs/tests for future local-only design slices, PowerShell/OpenSSH only after explicit read-only VPS gate approval.

---

## Текущая Граница

Default local-only Phase 4 implementation queue закрыта после:

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

Этот план открывает следующий этап:

```text
stage_id: P4-NG
stage_name: Named Gate / Write API Readiness
default_mode: docs-only gate planning
first_live_gate_candidate: NG-V001 read-only VPS baseline check
write_api_live_status: blocked until separate P4-NG-WRITE-API-LIVE-GATE
```

## Закрыто И Удалено Из Активного Плана

- [x] **NG-C001: create named gate charter**
  - Closed by `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md`.
  - Defines gate shape, allowed fields, blocked actions, go/no-go and safe evidence rules.

- [x] **NG-C002: restate safety boundary before any gate**
  - Closed by `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md`.
  - Keeps public `3040`, direct public `3030`, Caddy/HTTPS, config delivery, `/api/clients` write CRUD, Local Agent mutations, backup/import/reboot and production peer/user mutation closed.

- [x] **NG-C003: approve secrets policy for gate outputs**
  - Closed by `research/amn2/phase-4-ng-secrets-policy-go-no-go-format-2026-06-10.md`.
  - Reusable policy is present in `research/amn2/phase-4-ng-named-gate-evidence-template-2026-06-10.md`.

- [x] **NG-C004: define go/no-go format for all gates**
  - Closed by `research/amn2/phase-4-ng-secrets-policy-go-no-go-format-2026-06-10.md`.
  - `go_no_go_decision: go | no-go | defer` is present in the reusable gate evidence template.

- [x] **NG-S003: create reusable named-gate evidence template**
  - Closed by `research/amn2/phase-4-ng-named-gate-evidence-template-2026-06-10.md`.
  - Closed as supporting work required by `NG-C003` and `NG-C004`.

- [x] **NG-C005: keep write API live work blocked**
  - Closed by `research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md`.
  - The next write API slice is constrained to `live_write_authorized: no`.

- [x] **WAPI-V001: write API threat model**
  - Closed by `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`.
  - Defines threat classes and required tests before any write API route implementation.

- [x] **WAPI-V002: write API route taxonomy**
  - Closed by `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`.
  - Classifies future route groups, candidate route names, scopes, side effects, gates and required tests without adding runtime routes.

- [x] **WAPI-V003: local fake-runner contract**
  - Closed by `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`.
  - Defines future fake-runner inputs, outputs, operation intents, deterministic failure modes, audit-safe metadata and RED test requirements without adding runner code.

- [x] **WAPI-V004: idempotency, locking and partial-failure model**
  - Closed by `research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md`.
  - Defines request idempotency keys, per-target locks, retry behavior, conflict statuses and partial-failure vocabulary without adding runtime routes, runner code or live VPS/write authorization.

- [x] **WAPI-V005: write API audit/redaction requirements**
  - Closed by `research/amn2/phase-4-wapi-v005-write-api-audit-redaction-requirements-2026-06-10.md`.
  - Defines required safe audit fields, forbidden secret-bearing fields, redaction rules, event types and RED test requirements without adding runtime routes, audit schema code or live VPS/write authorization.

- [x] **WAPI-I004: operation status model**
  - Closed by `research/amn2/phase-4-wapi-i004-operation-status-model-2026-06-10.md`.
  - Defines safe operation status fields, canonical statuses, reason codes, transition rules, visibility tiers and RED test requirements without adding runtime routes, status schema code, operation queue or live VPS/write authorization.

- [x] **WAPI-I003: scoped write-token model**
  - Closed by `research/amn2/phase-4-wapi-i003-scoped-write-token-model-2026-06-10.md`.
  - Defines future minimal scope classes, proposed scoped write/config/operation permissions, forbidden broad scope patterns, token lifecycle boundaries and RED test requirements without adding runtime routes, token issue/revoke routes or live VPS/write authorization.

- [x] **WAPI-I002: decouple config delivery from client creation**
  - Closed by `research/amn2/phase-4-wapi-i002-config-delivery-decoupling-2026-06-10.md`.
  - Defines client/peer creation as safe operation metadata only and keeps `.conf`, QR, `vpn://`, archives, share/download links and public/self-service config delivery blocked behind separate config/public gates.

- [x] **WAPI-I001: `/api/clients` design without live CRUD**
  - Closed by `research/amn2/phase-4-wapi-i001-clients-design-without-live-crud-2026-06-10.md`.
  - Defines candidate `/api/clients` request/response boundaries, safe client metadata, scopes, idempotency, locks, audit/status binding and RED test requirements without adding runtime routes, write CRUD, fake-runner code or live VPS/write authorization.

- [x] **WAPI-I005: web-panel gated action labels**
  - Closed by `research/amn2/phase-4-wapi-i005-web-panel-gated-action-labels-2026-06-10.md`.
  - Defines future web-panel label vocabulary, disabled/gated action rules, status mappings and RED test requirements without changing templates, routes, behavior, config delivery, live writes or AMN2 code.

- [x] **NG-N003: operation queue design after write API contract**
  - Closed by `research/amn2/phase-4-ng-n003-operation-queue-design-2026-06-10.md`.
  - Defines future queue/cancel/retry/status semantics, lifecycle boundaries, idempotency/lock rules, visibility constraints and RED test requirements without implementing a queue, worker, runtime route, live write or config delivery.

- [x] **NG-N002: health/status polling design**
  - Closed by `research/amn2/phase-4-ng-n002-health-status-polling-design-2026-06-10.md`.
  - Defines future health/status polling tiers, safe aggregate fields, forbidden leakage fields, status vocabulary, staleness behavior, queue/status binding and RED test requirements without implementing polling, scheduling, collectors, live target checks or route changes.

- [x] **NG-N001: attach-existing-server read-only reconciliation gate design**
  - Closed by `research/amn2/phase-4-ng-n001-attach-existing-server-read-only-reconciliation-gate-design-2026-06-10.md`.
  - Defines safe read-only reconciliation phases, allowed report fields, attach/backfill boundaries, conflict handling, health/status binding and RED test requirements without implementing reconciliation, attach, import, backfill, real target detection or route changes.

- [x] **NG-N004: update candidate registry after every gate decision**
  - Closed by `research/amn2/phase-4-ng-n004-candidate-registry-update-2026-06-10.md`.
  - Synchronizes candidate registry entries for health/status polling, attach-existing-server reconciliation and operation queue boundaries without authorizing implementation, live VPS work, route changes, config delivery or production mutation.

- [x] **NG-S001: keep AMN3 status/transfer current**
  - Closed by `research/amn2/phase-4-ng-s001-status-transfer-sync-2026-06-10.md`.
  - Synchronizes AMN3 status and transfer references after the closed normal P4-NG queue without authorizing implementation, live VPS work, route changes, config delivery or production mutation.

- [x] **NG-S002: keep next-chat handoff current**
  - Closed by `research/amn2/phase-4-ng-s002-next-chat-handoff-sync-2026-06-10.md`.
  - Synchronizes the next-chat packet with the closed P4-NG normal and simple queue without authorizing implementation, live VPS work, route changes, config delivery or production mutation.

- [x] **NG-S004: maintain visible active plan**
  - Closed by `research/amn2/phase-4-ng-s004-visible-active-plan-maintenance-2026-06-10.md`.
  - Removes closed simple tasks from the visible active plan and leaves only explicit VPS-gate and cosmetic docs tasks active.

- [x] **NG-X003: stale wording cleanup**
  - Closed by `research/amn2/phase-4-ng-x003-stale-wording-cleanup-2026-06-10.md`.
  - Removes stale active-next wording that could imply implicit live/write/public/config authorization.

- [x] **NG-X001: gate naming consistency**
  - Closed by `research/amn2/phase-4-ng-x001-gate-naming-consistency-2026-06-10.md`.
  - Aligns stage-level gate labels to `P4-NG-*` in P4-NG docs/evidence.

- [x] **NG-X002: Russian-first operator wording polish**
  - Closed by `research/amn2/phase-4-ng-x002-russian-first-operator-wording-polish-2026-06-10.md`.
  - Makes active P4-NG operator-facing headings and next-step instructions Russian-first while keeping technical ids/routes/gate names unchanged.

## Активный Оставшийся План

### Критичные

Нет активных задач.

### Очень Важные

- [ ] **NG-V001: run read-only VPS baseline gate**

  Имя gate:

  ```text
  P4-NG-VPS-READONLY-BASELINE-2026-06-10
  ```

  Разрешенные действия после явного operator approval:

  - Проверка SSH transport только до operator-provided target.
  - Read-only service status для `amneziya-web` и `amneziya-bot`.
  - Read-only loopback `/login` check на `127.0.0.1:3030`.
  - Read-only listener checks для `3030`, `3040`, `80`, `443`.
  - Boolean-only проверка, что `VPS_APPLY_ENABLED=false` существует; не печатать `.env`.

  Закрытые действия:

  - package apply;
  - service restart/enable/disable;
  - firewall/reverse proxy edits;
  - peer apply/revoke/sync;
  - config delivery;
  - token issue/revoke;
  - backup/import/reboot;
  - изменения public exposure.

  Готово, когда:

  - Evidence содержит только safe summary и не содержит secret-bearing data.

### Важные

Нет активных задач.

### Нормальные

Нет активных задач.

### Простые

Нет активных задач.

### Косметические

Нет активных задач.

## Рекомендация

Очередь default docs-only cosmetic закрыта. Следующее решение: `NG-V001` read-only VPS baseline gate можно брать только после явного operator approval и target SSH alias/host вне repository secrets. Если live/read-only gate сейчас не выбирается, оставляем P4-NG в paused/docs-maintenance state или открываем отдельный local-only design boundary, например для `P4-PRVTPRO-REFRESH-003`.
