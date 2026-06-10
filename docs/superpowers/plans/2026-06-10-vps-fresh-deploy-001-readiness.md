# VPS-FRESH-DEPLOY-001 Clean Server Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document whether AMN2 can be deployed from zero on a clean VPS from GitHub/source/package while keeping wipe/reinstall behind a separate explicit destructive approval.

**Architecture:** AMN3 remains the coordination and evidence repository. `VPS-FRESH-DEPLOY-001` is a docs-only readiness layer linked to `VPS-REBUILD-001`; it clarifies what can be rebuilt from repo/package and what requires operator-provided secrets or explicit data-loss acceptance.

**Tech Stack:** Markdown evidence in AMN3, AMN2 source/package references, future live execution only through a separate named gate with safe summary outputs.

---

## Current Status

```text
gate_id: VPS-FRESH-DEPLOY-001
linked_gate: VPS-REBUILD-001
status: readiness-documented
destructive_action_authorized: no
reinstall_authorized: no
delete_actions_planned: no
live_commands_run: no
ssh_commands_run: no
```

## Task 1: Readiness Evidence

**Files:**
- Create: `research/amn2/vps-fresh-deploy-001-readiness-checklist-2026-06-10.md`

- [x] **Step 1: Record the docs-only decision**

Record `fresh_deploy_possible_from_repo_package: yes-with-operator-provided-secrets`, `bare_os_deploy_smoked: no`, `current_vps_disposable_decision: not-set`, `destructive_action_authorized: no` and `delete_actions_planned: no`.

- [x] **Step 2: Split rebuildable from non-rebuildable state**

List source/package/runbook/service-mode boundaries as rebuildable, and target secrets, local DB, runtime peer/config state and provider backup history as not rebuildable without operator input.

- [x] **Step 3: Record future operator decisions**

Require target identity confirmation, data-retention decision, external secret channel, desired seed state and exact final destructive phrase before any wipe/reinstall.

## Task 2: Synchronize Existing Gate Context

**Files:**
- Modify: `research/amn2/vps-rebuild-001-fresh-vps-rebuild-gate-2026-06-10.md`
- Modify: `docs/superpowers/plans/2026-06-10-vps-rebuild-001-fresh-vps-rebuild.md`

- [x] **Step 1: Link the new readiness evidence**

Add `VPS-FRESH-DEPLOY-001` as a linked docs-only readiness clarification under the existing destructive `VPS-REBUILD-001` gate.

- [x] **Step 2: Preserve the destructive boundary**

Keep `go_no_go_decision: defer`, `destructive_action_authorized: no`, `reinstall_authorized: no`, and the exact final destructive phrase requirement.

- [x] **Step 3: Update the active remaining plan**

Replace the provider-backup-only wording with the broader retention-path decision: wait for provider backup, explicitly accept disposable target, or keep the destructive gate deferred.

## Task 3: Synchronize Handoff / Status Docs

**Files:**
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `research/amn2/transfer-backlog.md`
- Modify: `docs/PROJECT_CONTEXT_IMPORT.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`
- Modify: `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md`

- [x] **Step 1: Add the completed readiness note**

Record that `VPS-FRESH-DEPLOY-001` is closed as docs-only readiness and did not run live/SSH/provider/destructive actions.

- [x] **Step 2: Update next decision wording**

Make the remaining critical decision a retention-path choice before any destructive GO, not a general project stop while waiting for provider backup.

- [x] **Step 3: Preserve all closed boundaries**

Keep public API `3040`, direct public web/admin `3030`, Caddy/HTTPS, config delivery, write API, Local Agent mutations, backup/import/reboot and production mutation closed.

## Active Remaining Plan

### Критичные

- `VPS-REBUILD-001`: choose retention path before any destructive GO: wait for provider backup, explicitly accept disposable target, or keep gate deferred.
- `VPS-REBUILD-001`: stop-criteria review before any destructive GO.
- `VPS-REBUILD-001`: exact final destructive phrase is required only if the operator still chooses wipe/reinstall.

### Очень Важные

- None.

### Важные

- None.

### Нормальные

- None.

### Простые

- None.

### Косметические

- None.

## Recommendation

Continue non-destructive readiness work without waiting for the provider backup. Do not run wipe/reinstall until the operator chooses and records one retention path and then sends the exact final destructive phrase.
