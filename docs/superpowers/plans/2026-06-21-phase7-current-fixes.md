# AMN2 Phase 7 Current Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the Phase 7 state-drift and mobile/client-readiness gaps from a clean `471bca8` AMN2 worktree before Phase 8 launch decisions.

**Architecture:** Keep all code fixes local-only and evidence-first. Treat live VPS/mobile diagnostics as exact named gates after the local policy and tests say what evidence is needed.

**Tech Stack:** Python, pytest, AMN2 service/status modules, AMN3 markdown evidence.

---

## File Map

- AMN2 clean worktree: `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current`
- AMN3 evidence repo: `C:\Users\SooL\Documents\VPS-OPS-LAB`
- Evidence to maintain: `research/amn2/*.md`, `docs/AMN2_PHASE_7_EVIDENCE_INDEX.ru.md`, `docs/PROJECT_STATUS_CURRENT.ru.md`, `docs/PROJECT_CONTEXT_IMPORT.ru.md`
- AMN2 compatibility code: `app/vpn/client_compatibility.py`, `tests/vpn/test_client_compatibility.py`
- AMN2 status code: `app/services/integration_status.py`, `tests/api/test_api_integration_status.py`
- AMN2 installer/status docs: `docs/FRESH_INSTALL_WIZARD.ru.md`, `docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md`, `docs/RELEASE_NOTES_RC_SKELETON.ru.md`

## Task 1: State-Drift Guard

**Files:**
- Create: `C:\Users\SooL\Documents\VPS-OPS-LAB\research\amn2\phase-7-state-drift-clean-worktree-2026-06-21.md`
- Modify: `C:\Users\SooL\Documents\VPS-OPS-LAB\docs\AMN2_PHASE_7_EVIDENCE_INDEX.ru.md`

- [x] **Step 1: Verify AMN3 state**

Run:

```powershell
git status --short --branch
git log -5 --oneline --decorate
```

Expected: `master...origin/master`, clean status, head `0122251`.

- [x] **Step 2: Verify AMN2 clean worktree state**

Run from `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current`:

```powershell
git status --short --branch
git log -5 --oneline --decorate
```

Expected: `codex/phase7-current-fixes...amn2/codex-vps-test-prep`, clean status, head `471bca8`.

- [x] **Step 3: Record dirty checkout boundary**

Run from `C:\Users\SooL\Documents\Amneziya`:

```powershell
git status --short --branch
git log -5 --oneline --decorate
```

Expected: behind by 4 commits and dirty; do not edit this checkout.

## Task 2: Android Acceptance Policy Contract

**Files:**
- Modify: `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current\app\vpn\client_compatibility.py`
- Modify: `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current\tests\vpn\test_client_compatibility.py`

- [ ] **Step 1: Add RED test for Android acceptance pending**

Add a test that asserts `amneziawg_android` is supported but not release-accepted
until a real-device `.conf` import/connect/traffic check passes. The test must
also assert QR and `vpn://` remain non-primary.

Run:

```powershell
python -m pytest tests\vpn\test_client_compatibility.py -q
```

Expected before implementation: fail because no machine-readable Android
acceptance field exists.

- [ ] **Step 2: Implement minimal compatibility fields**

Add explicit fields such as `acceptance_status` and `release_primary_allowed`
to the compatibility matrix without changing secret-bearing config generation.

- [ ] **Step 3: Verify focused tests**

Run:

```powershell
python -m pytest tests\vpn\test_client_compatibility.py -q
```

Expected: pass.

## Task 3: Integration Status Contract Audit

**Files:**
- Modify: `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current\app\services\integration_status.py`
- Modify: `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current\tests\api\test_api_integration_status.py`

- [ ] **Step 1: Add RED test for current Phase 7 status**

Assert the API status reports:

- current source head dynamically;
- latest VPS-smoked/package head as `6d5cf3e` until the next package gate;
- source policy head as `471bca8`;
- Android acceptance pending;
- DefaultVPN iOS experimental/unreliable;
- Phase 8 blocked until Android real-device acceptance or narrower launch
  policy.

- [ ] **Step 2: Implement minimal status fields**

Update integration status constants and `build_client_compatibility_boundary()`
to expose the current contract without opening live gates.

- [ ] **Step 3: Verify focused API status tests**

Run:

```powershell
python -m pytest tests\api\test_api_integration_status.py -q
```

Expected: pass.

## Task 4: Manager/Config Retrieval Contract Tests

**Files:**
- Inspect first: `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current\app\server\peer_apply.py`
- Inspect first: `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current\app\server\checks.py`
- Test: existing or new focused tests under `tests\server\`

- [ ] **Step 1: Add RED tests for PRVTPRO-inspired contracts**

Tests should assert AMN2 policy, not copy upstream GPL code:

- AWG Docker runtime requires the actual configured `runtime.config_path`;
- WireGuard/AWG show-config/read-only checks go through the existing safe
  adapter/allowlist boundary;
- Xray runtime updates remain future-gated and must not imply container restart
  or implementation copy.

- [ ] **Step 2: Implement only missing AMN2 policy/status guards**

If the current code already passes, record as no-code evidence instead of
inventing abstractions.

## Task 5: Fresh-From-Zero Launch Path Docs

**Files:**
- Modify: `C:\Users\SooL\Documents\VPS-OPS-LAB\docs\PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md`
- Modify: `C:\Users\SooL\Documents\VPS-OPS-LAB\docs\PROJECT_STATUS_CURRENT.ru.md`
- Modify: `C:\Users\SooL\Documents\VPS-OPS-LAB\docs\PROJECT_CONTEXT_IMPORT.ru.md`

- [ ] **Step 1: Document fresh-from-zero as allowed only by exact destructive gate**

Add that the current VPS is disposable, but fresh install/rebuild still requires
an exact destructive gate with final stop-line phrase.

- [ ] **Step 2: Document next exact gates**

Offer:

- local-only TDD current-fixes package preflight;
- `P7-C011f` read-only AWG handshake observation;
- fresh-from-zero clean install/package smoke for the final head;
- Android AmneziaWG 2.0.1 real-device acceptance.

## Task 6: Verification And Handoff

**Files:**
- Modify evidence/status docs as needed.

- [ ] **Step 1: Run focused tests**

Run all touched focused tests.

- [ ] **Step 2: Run broader tests if dependencies are available**

Run:

```powershell
python -m pytest tests\vpn tests\api -q
```

If unavailable, record the exact missing dependency/runtime reason.

- [ ] **Step 3: Commit and push AMN2 and AMN3 separately**

Commit AMN2 source/test changes in the clean worktree. Commit AMN3 evidence
changes in the evidence repo. Keep the old dirty checkout untouched.
