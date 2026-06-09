# AMN2 Phase 4 Start Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Start Phase 4 from the accepted service-mode loopback baseline, choose only local/read-only AMN2 slices by default, and keep GitHub/VPS access checks explicit and safe.

**Architecture:** AMN3 remains the coordination/evidence registry, while AMN2 receives only selected implementation slices. Live VPS access is a separate named read-only gate for access verification only; public/write/config/destructive work stays blocked until a later named gate.

**Tech Stack:** AMN3 markdown evidence/backlog, AMN2 Python/FastAPI/web templates/tests, GitHub connector/local git, OpenSSH read-only VPS preflight.

---

## Access Preflight Result 2026-06-09

- AMN3 local checkout: `C:\Users\SooL\Documents\VPS-OPS-LAB`, branch `master`, remote `https://github.com/barakov-dot/amn3.git`.
- AMN3 GitHub connector: repository visible as `barakov-dot/amn3`; connector permissions show `pull=true`, `push=false`.
- AMN3 local git: `git fetch --dry-run origin` passed; `git push --dry-run origin master` returned `Everything up-to-date`.
- AMN2 local checkout: `C:\Users\SooL\Documents\Amneziya`, branch `codex-vps-test-prep`, remote `amn2=https://github.com/barakov-dot/amn2.git`.
- AMN2 GitHub connector: repository visible as `barakov-dot/amn2`; connector permissions show `pull=true`, `push=false`.
- AMN2 local git: `git -C C:\Users\SooL\Documents\Amneziya fetch --dry-run amn2` passed; `git -C C:\Users\SooL\Documents\Amneziya push --dry-run amn2 codex-vps-test-prep` returned `Everything up-to-date`.
- Local GitHub CLI: `gh` is not installed or not on PATH.
- Local SSH client: OpenSSH for Windows is installed.
- VPS host/alias: not present in the repo by design; a live access check needs the operator-provided SSH alias or host and an explicit read-only gate.

## Named VPS Gate For Access Check

Gate name:

```text
P4-VPS-ACCESS-READONLY-2026-06-09
```

Allowed actions:

- SSH transport check to the operator-provided target only.
- Read-only service status checks for `amneziya-web` and `amneziya-bot`.
- Read-only loopback `/login` HTTP check on `127.0.0.1:3030`.
- Read-only listener checks for `3030`, `3040`, `80` and `443`.
- Boolean-only check that `/opt/amn2/.env` contains `VPS_APPLY_ENABLED=false`; do not print `.env`.

Blocked actions:

- `sed`, `tee`, config edits, package installs, service enable/start/restart, Caddy/nginx changes.
- `VPS_APPLY_ENABLED=true`.
- peer apply/revoke/sync, `/api/clients` writes, config delivery, token issue/revoke, backup/import/reboot.
- printing `.env`, `servers.yml`, tokens, hashes, keys, PSK, peer public keys, client configs, QR, `vpn://`, endpoint values or full logs.

Safe check command shape, after operator supplies `<VPS_SSH_TARGET>`:

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 <VPS_SSH_TARGET> "printf 'ssh_ok=yes\n'; printf 'amneziya_web=%s\n' \"$(systemctl is-active amneziya-web 2>/dev/null || true)\"; printf 'amneziya_bot=%s\n' \"$(systemctl is-active amneziya-bot 2>/dev/null || true)\"; printf 'login_3030_http=%s\n' \"$(curl -sS -o /dev/null -w '%{http_code}' http://127.0.0.1:3030/login 2>/dev/null || echo curl-failed)\"; printf 'tcp_3030_loopback=%s\n' \"$(ss -ltnH '( sport = :3030 )' 2>/dev/null | grep -q '127.0.0.1:3030' && echo yes || echo no)\"; printf 'tcp_3040_absent=%s\n' \"$(ss -ltnH '( sport = :3040 )' 2>/dev/null | grep -q . && echo no || echo yes)\"; printf 'tcp_80_absent=%s\n' \"$(ss -ltnH '( sport = :80 )' 2>/dev/null | grep -q . && echo no || echo yes)\"; printf 'tcp_443_absent=%s\n' \"$(ss -ltnH '( sport = :443 )' 2>/dev/null | grep -q . && echo no || echo yes)\"; printf 'vps_apply_enabled_false=%s\n' \"$(sudo grep -q '^VPS_APPLY_ENABLED=false$' /opt/amn2/.env 2>/dev/null && echo yes || echo no)\""
```

Expected safe result:

```text
ssh_ok=yes
amneziya_web=active
amneziya_bot=active
login_3030_http=200
tcp_3030_loopback=yes
tcp_3040_absent=yes
tcp_80_absent=yes
tcp_443_absent=yes
vps_apply_enabled_false=yes
```

## Активный оставшийся план после P4-C009, P4-I002, route/secret gate planning, P4-I003 design/implementation, P4-I004 endpoint taxonomy и P4-N003 metrics privacy

Закрыто и удалено из активного плана:

- access/GitHub preflight;
- first AMN2 slice selection;
- `P4-C009` web-panel user/config visibility investigation;
- AMN2 branch/worktree preparation for `P4-C009`;
- VPS access decision for `P4-C009` (`not needed`; no live commands were run);
- `P4-I002` service-mode/read-only status wording on `/integration-status`;
- route/secret gate planning for future API expansion.
- `P4-I003` candidate-specific read-only API/status schema maturity design.
- `P4-I003` AMN2 local implementation plan.
- `P4-I003` AMN2 local implementation.
- `P4-I004` endpoint taxonomy / route-policy docs alignment.
- `P4-N003` aggregate metrics privacy boundary visibility.

### Критичные

Активных default-mode critical implementation items не осталось после `P4-C009`, `P4-I002`, route/secret gate planning, `P4-I003`, `P4-I004` и `P4-N003`.
Critical live/public/write/config candidates остаются blocked или gated by the registry.

### Важные

- [ ] **Задача I1: решить, нужен ли fallback UX evidence pass `P4-I001`**

  Trigger:

  ```text
  wording cannot be inferred safely from existing AMN2 templates/tests and Phase 3 evidence
  ```

  Boundary:

  - SSH-tunnel private-panel GET/navigation review only.
  - No POST/write/config delivery/API token issue-revoke/sync/health/backup/import/reboot.

- [ ] **Задача I3: продолжить scoped API token lifecycle boundary**

  Scope:

  - refine local token lifecycle docs/tests before any future route expansion;
  - keep raw token one-time only, token hash private, revoke/rotate audit safe and owner status inherited;
  - do not issue/revoke production tokens, open public API or add write/config scopes.

### Средние

Активных medium local-only implementation items не осталось после `P4-N003`.

### Минимальные

- [ ] **Задача MIN1: обновлять AMN3 transfer note после следующего AMN2 slice**
- [ ] **Задача MIN2: поддерживать candidate registry при изменении priority/gate/recommendation**

### Косметические

- [ ] **Задача X1: полировать naming только после стабилизации behavior**
- [ ] **Задача X2: полировать operator docs links без авторизации live VPS work**

## Original Startup Breakdown

The original startup breakdown below is retained as audit context. Use the active remaining plan above for the next execution step.

## Critical Tasks

- [ ] **Task C1: Freeze Phase 4 boundaries before implementation**

  Files:

  - Read: `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`
  - Read: `research/amn2/phase-4-candidate-registry-2026-06-09.md`
  - Read: `research/amn2/transfer-backlog.md`

  Steps:

  - Confirm Phase 3 service-mode loopback is accepted and closed.
  - Confirm first implementation default is local/read-only.
  - Confirm public API `3040`, direct public web/admin `3030`, HTTPS cutover, config delivery, write CRUD, Local Agent mutations and backup/import/reboot remain closed.

- [ ] **Task C2: Select the first AMN2 local-only slice**

  Recommended slice:

  ```text
  P4-C009: web-panel user/config visibility investigation
  ```

  Steps:

  - Use `research/amn2/phase-4-candidate-registry-2026-06-09.md` as source.
  - Treat the operator observation as a data consistency issue until proven otherwise: created test accounts/configurations were not visible under web-panel users/configurations.
  - Scope the first pass to read-only evidence, local web/API/repository tests and display/empty-state behavior.
  - Do not change POST behavior, token lifecycle, config generation, peer apply/revoke, sync, backup/import/reboot or runtime state.

- [ ] **Task C4: Investigate web-panel user/config visibility gap before wording polish**

  Observation:

  ```text
  During service-mode web-panel navigation, approved test accounts/configurations were not visible in the users/configurations area.
  ```

  Working hypotheses to prove or reject:

  - Live AWG peers exist, but local AMN2 web users/config records were not created or linked.
  - The web panel lists only local users/devices, not live server peers.
  - A route/query/template filter hides approved test peers because of status, ownership or source.
  - The records are visible under another view, but labels/navigation made that unclear.
  - Showing them requires a sync/backfill operation, which is not allowed without a separate write gate.

  First pass boundaries:

  - Read local AMN2 code and tests.
  - Use existing safe evidence and counts/names only.
  - Add local failing tests once the expected read-only behavior is chosen.
  - Do not run live sync, apply, revoke, config delivery, API token issue/revoke or DB backfill.

- [ ] **Task C3: Verify AMN2 workspace state before editing**

  Commands:

  ```powershell
  git -C C:\Users\SooL\Documents\Amneziya status --short --branch
  git -C C:\Users\SooL\Documents\Amneziya fetch --dry-run amn2
  ```

  Expected:

  ```text
  branch: codex-vps-test-prep
  fetch dry-run: exit code 0
  ```

## Important Tasks

- [ ] **Task I1: Write a focused AMN2 implementation plan for P4-C009**

  Target plan file:

  ```text
  C:\Users\SooL\Documents\VPS-OPS-LAB\docs\superpowers\plans\2026-06-09-amn2-web-panel-user-config-visibility.md
  ```

  Required scope:

  - identify exact AMN2 routes/templates/repositories/tests behind users, devices, servers, config templates and integration/status views;
  - map whether test peers/configurations are expected to appear as users, devices, server peers, or not at all;
  - add failing tests first for the selected read-only behavior;
  - implement only minimal read-only display, empty-state or navigation clarification;
  - run focused tests and then the relevant local suite.

- [ ] **Task I2: Prepare AMN2 branch/worktree**

  Branch name:

  ```text
  codex/phase-4-web-panel-user-config-visibility
  ```

  Steps:

  - Start from `amn2/codex-vps-test-prep`.
  - Keep user changes if the tree is dirty.
  - Do not touch AMN3 docs in the AMN2 implementation commit except for return evidence after completion.

- [ ] **Task I3: Decide whether VPS access check is needed before implementation**

  Default:

  ```text
  not needed for P4-C009 local investigation
  ```

  Run `P4-VPS-ACCESS-READONLY-2026-06-09` only if the operator wants a fresh access proof before UX review or later live gates.

## Medium Tasks

- [ ] **Task M1: Run second detailed read-only UX pass if wording details are unclear**

  Trigger:

  ```text
  concrete page-level wording cannot be inferred safely from current evidence
  ```

  Source template:

  ```text
  docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_EVIDENCE_TEMPLATE.ru.md
  ```

  Boundary:

  - GET/navigation/labels/empty states/warnings only.
  - No POST, config delivery, token issue/revoke, sync/health actions, backup/import/reboot.

- [ ] **Task M2: Keep endpoint taxonomy and route-policy docs aligned**

  Scope:

  - OpenAPI/domain grouping only for existing read-only routes.
  - No public docs exposure decision.
  - No new route expansion.

- [ ] **Task M3: Keep aggregate metrics privacy boundary visible**

  Scope:

  - Aggregate-only labels by default.
  - No peer names, endpoint values, per-user activity labels or public metrics exposure.

## Minimal Tasks

- [ ] **Task MIN1: Update AMN3 transfer note after the next AMN2 slice**

  File:

  ```text
  research/amn2/transfer-backlog.md
  ```

  Required safe fields:

  - AMN2 branch and commit;
  - focused test result;
  - full or relevant suite result;
  - explicit statement that live VPS was not touched if the slice stays local-only.

- [ ] **Task MIN2: Keep the candidate registry current**

  File:

  ```text
  research/amn2/phase-4-candidate-registry-2026-06-09.md
  ```

  Update only when a candidate changes gate class, priority or recommendation.

## Cosmetic Tasks

- [ ] **Task X1: Polish naming only after behavior is stable**

  Allowed:

  - wording consistency for `service-mode`, `loopback-only`, `SSH tunnel`, `read-only`, `write gate`.

  Blocked:

  - renaming routes, changing API response keys or changing behavior as part of naming cleanup.

- [ ] **Task X2: Polish operator docs links**

  Scope:

  - link cleanup and stale baseline scan.
  - no new operational instruction that authorizes live VPS work.

## Стартовая рекомендация

Начинать с active decision `Task I3`: continue scoped API token lifecycle boundary from the latest read-only API and metrics privacy baseline. `P4-I001` запускать только если сначала нужен еще один private-panel read-only UX pass. VPS access check можно запускать отдельно только после того, как оператор даст SSH target alias/host и подтвердит gate `P4-VPS-ACCESS-READONLY-2026-06-09`.
