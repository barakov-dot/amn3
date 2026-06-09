# AMN2 Route/Secret Gate Planning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a Phase 4 route/secret gate plan that future AMN2 API expansion must satisfy before exposing write, config, public, Local Agent mutation or dangerous routes.

**Architecture:** Keep this as an AMN3 docs-only governance slice. Reuse the existing AMN2 local-gate baselines as prerequisites, define route classes and required evidence, then update Phase 4 handoff/backlog/status so the next chat does not treat planning as implementation authorization.

**Tech Stack:** AMN3 markdown evidence and backlog files; no AMN2 code, no VPS commands.

---

### Task 1: Create Route/Secret Gate Plan

**Files:**

- Create: `research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md`

- [ ] **Step 1: Record the source baselines**

Include these existing AMN2 baselines as prerequisites:

```text
route/auth binding: f9d2c79
secret inventory registry: 9ce42f4
api token lifecycle gate: 256d0c0
public/self-service config delivery policy: 2ef3af7
manager config export contract: 4d4e7a4
backup/import policy contract: afb2702
service-mode status boundary: 83f6d28
```

- [ ] **Step 2: Define route classes**

Define at least:

```text
read-only aggregate API
read-only operational status
write peer/user lifecycle
secret-read config delivery
public/self-service config delivery
Local Agent mutation/configs
backup/import/reboot dangerous operations
public exposure/cutover
```

- [ ] **Step 3: Define gate acceptance rules**

Each future route-expansion proposal must include route policy, auth scopes, secret classification, audit metadata, redaction tests, fake-runner tests, rollback/recovery notes and the required named gate class.

### Task 2: Sync Phase 4 Status Docs

**Files:**

- Modify: `research/amn2/transfer-backlog.md`
- Modify: `research/amn2/phase-4-candidate-registry-2026-06-09.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`
- Modify: `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md`
- Modify: `docs/superpowers/plans/2026-06-09-amn2-phase-4-start.md`

- [ ] **Step 1: Mark route/secret planning as docs-only completed**

State explicitly that no AMN2 code, no live VPS command and no route/API exposure changed.

- [ ] **Step 2: Remove it from the active plan**

The remaining active plan should require operator choice before any future implementation: either a second read-only UX pass or a specific named API route-expansion design.

### Task 3: Verify And Commit

**Files:**

- All changed AMN3 files.

- [ ] **Step 1: Run static checks**

Run:

```powershell
git diff --check
$patterns = @(
  "TO" + "DO",
  "TB" + "D",
  "VPS_APPLY_ENABLED" + "=true",
  "public API 3040" + " enabled",
  "config delivery" + " enabled"
)
Select-String -Path research\amn2\phase-4-route-secret-gate-plan-2026-06-09.md -Pattern $patterns
```

Expected:

```text
git diff --check exits 0
marker scan returns no unsafe placeholder/enablement markers
```

- [ ] **Step 2: Commit AMN3 docs**

Commit message:

```text
Record Phase 4 route secret gate plan
```
