# AMN2 Read-only API Status Design Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare the P4-I003 candidate-specific design for read-only API/status schema maturity without changing AMN2 runtime behavior.

**Architecture:** Keep the slice in AMN3 evidence and planning docs. Use the existing AMN2 read-only API route shell, scoped token policy, service-mode integration status and Phase 4 route/secret gate plan as source material, then update registry/backlog/status/handoff so the next slice can become an AMN2 local implementation plan.

**Tech Stack:** AMN3 markdown evidence/backlog/status files; AMN2 files are read-only references.

---

### Task 1: Record P4-I003 Candidate-specific Design

**Files:**

- Create: `research/amn2/phase-4-read-only-api-status-design-2026-06-09.md`

- [ ] **Step 1: Bind the design to the existing AMN2 API surface**

Record the six current read-only API routes:

```text
GET /api/servers -> server:read
GET /api/servers/{server_name}/summary -> server:read
GET /api/integration/status -> server:read
GET /api/local-agent/runtime/summary -> server:read
GET /api/metrics/summary -> metrics:read
GET /api/users/summary -> metrics:read
```

- [ ] **Step 2: Fill the route/secret proposal template**

Use the mandatory proposal fields from `research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md` and classify this candidate as:

```text
risk_class: read-only aggregate API
remote_write_surface: none
public_exposure: none
vps_gate_required: no for local schema/docs/tests
```

- [ ] **Step 3: Define the next AMN2 local-only implementation scope**

Allow only schema/docs/tests for the existing read-only API/status surface. Block new routes, public API exposure, config delivery, write CRUD, Local Agent mutations, token lifecycle operations and live VPS commands.

### Task 2: Sync AMN3 Status Documents

**Files:**

- Modify: `research/amn2/transfer-backlog.md`
- Modify: `research/amn2/phase-4-candidate-registry-2026-06-09.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`
- Modify: `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md`
- Modify: `docs/superpowers/plans/2026-06-09-amn2-phase-4-start.md`

- [ ] **Step 1: Mark P4-I003 design as completed**

State explicitly that this is a docs-only design and did not touch AMN2 code, live VPS, public listeners, config delivery, write routes or token lifecycle.

- [ ] **Step 2: Remove P4-I003 design from the active plan**

The remaining active plan should recommend either an AMN2 local implementation plan for the approved P4-I003 design or `P4-I001` if more private-panel UX evidence is needed first.

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
  "public API 3040" + " enabled",
  "config delivery" + " enabled",
  "/api/clients write CRUD" + " enabled"
)
Select-String -Path research\amn2\phase-4-read-only-api-status-design-2026-06-09.md -Pattern $patterns
```

Expected:

```text
git diff --check exits 0
marker scan returns no unsafe placeholder/enablement markers
```

- [ ] **Step 2: Commit AMN3 docs**

Commit message:

```text
Record Phase 4 read-only API status design
```
