# VPS-FRESH-DEPLOY-002 Clean Ubuntu Runbook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a current, no-domain fresh deploy runbook for AMN2 `1508e3c` that is safe to review before any live destructive action.

**Architecture:** AMN3 remains the evidence/runbook repository. The runbook is a docs-only operator artifact linked to `VPS-FRESH-DEPLOY-001` and `VPS-REBUILD-001`, and every command block is marked as future live run only unless it is local package verification.

**Tech Stack:** Markdown docs, AMN3 package/checksum references, PowerShell local package checks, future Ubuntu shell commands gated by `VPS-REBUILD-001`.

---

## Task 1: Create Fresh Deploy Runbook

**Files:**
- Create: `docs/AMN2_FRESH_DEPLOY_FROM_ZERO_RUNBOOK.ru.md`

- [x] **Step 1: Record baseline and boundaries**

Record `1508e3c` source/package, no-domain service-mode boundary, loopback web/admin, SSH tunnel access, `VPS_APPLY_ENABLED=false` and no public API `3040`.

- [x] **Step 2: Split rebuildable and non-rebuildable state**

Make clear that AMN2 source/app/service-mode can be recreated, while `.env`, `servers.yml`, local DB, Amnezia runtime keys, peer configs and provider backup history require operator input or separate gates.

- [x] **Step 3: Add future-run phases**

Add phases for local package checks, OS baseline, package install, private secrets, read-only smoke, service-mode loopback and SSH tunnel access.

- [x] **Step 4: Add acceptance criteria**

Require `3030` loopback-only, `3040/80/443` absent, `VPS_APPLY_ENABLED=false`, no config delivery, no write API, no Local Agent mutation, no backup/import/reboot and no secret publication.

## Task 2: Create Evidence Note

**Files:**
- Create: `research/amn2/vps-fresh-deploy-002-clean-ubuntu-runbook-2026-06-11.md`

- [x] **Step 1: Record docs-only completion**

Record `result: completed-docs-only`, no live/SSH commands, no wipe/reinstall, no package apply and no secret publication.

- [x] **Step 2: Link to active gates**

Link the runbook to `VPS-FRESH-DEPLOY-001` and `VPS-REBUILD-001`.

## Task 3: Synchronize Active Status

**Files:**
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `research/amn2/transfer-backlog.md`
- Modify: `docs/PROJECT_CONTEXT_IMPORT.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`
- Modify: `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md`
- Modify: `research/amn2/vps-rebuild-001-fresh-vps-rebuild-gate-2026-06-10.md`

- [x] **Step 1: Add runbook completion**

Record `VPS-FRESH-DEPLOY-002` as completed docs-only and remove it from the active plan.

- [x] **Step 2: Preserve remaining plan**

Keep only `VPS-REBUILD-001` retention path, stop-criteria review and final destructive phrase as active critical tasks.

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

Review the runbook now. Do not run the future live phases until `VPS-REBUILD-001` records the retention path and exact final destructive approval.
