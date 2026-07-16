# Phase 11 `0b858c5` combined overlay package implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Подготовить, проверить и опубликовать checksum-bound private source
overlay package exact AMN2 commit `0b858c5`, не загружая и не применяя его на
production.

**Architecture:** Внешний ZIP содержит четыре allowlisted файла: полный
`git archive` AMN2 source, его SHA-256 receipt, проверенный apply helper и
русский rollout/rollback contract. Package связывается с production baseline
`801f8c3`, exact full source commit и 31-path delta; live rollout и persistent
bot activation остаются отдельными exact gates.

**Tech Stack:** Git archive, ZIP/SHA-256, Bash, PowerShell, Python/pytest,
Markdown, Codex Security diff scan.

## Global Constraints

- AMN2 source: `codex-vps-test-prep` at
  `0b858c5cdbc5b565cc265966a2edfe2d339d65e0`, clean and origin-synced.
- Production overlay remains `801f8c3`; no upload, extraction or apply in this
  plan.
- Regular production bot remains inactive/disabled; no Telegram API or profile
  mutation.
- Never stop, restart, recreate or reconfigure production AWG.
- Preserve `.env`, `servers.yml`, `data`, `venv` and private evidence at apply
  time; no database migration or write is authorized.
- Do not touch `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`.
- Engineering order: evidence -> scoped tests -> diff/security review ->
  docs/status sync -> commit -> push.

---

### Task 1: Build the exact source-bound package

**Files:**

- Create: `dist/amn2-combined-overlay-0b858c5/amn2-codex-vps-test-prep-0b858c5-source.zip`
- Create: `dist/amn2-combined-overlay-0b858c5/amn2-codex-vps-test-prep-0b858c5-source.zip.sha256.txt`
- Create: `dist/amn2-combined-overlay-0b858c5/amn2_apply_source_zip.sh`
- Create: `dist/amn2-combined-overlay-0b858c5/AMN2_COMBINED_OVERLAY_0b858c5.ru.md`
- Create: `dist/amn2-combined-overlay-0b858c5.zip`
- Create: `dist/amn2-combined-overlay-0b858c5.zip.sha256.txt`

**Interfaces:**

- Consumes: source commit
  `0b858c5cdbc5b565cc265966a2edfe2d339d65e0`, baseline `801f8c3` and
  `scripts/vps/amn2_apply_source_zip.sh`.
- Produces: four-entry outer package whose inner archive comment, checksum and
  helper defaults bind to exact source commit and bytes.

- [x] **Step 1: Reconfirm the immutable source inputs**

  Run:

  ```powershell
  git -C worktrees/amn2-p7-c005-write-install status --short --branch
  git -C worktrees/amn2-p7-c005-write-install rev-parse HEAD
  git -C worktrees/amn2-p7-c005-write-install diff --name-status 801f8c3..0b858c5
  ```

  Expected: clean origin-synced branch, full SHA
  `0b858c5cdbc5b565cc265966a2edfe2d339d65e0`, 31-path delta with only
  `app/web/static/brand-full.jpg` deleted.

- [x] **Step 2: Create exact Git source archive**

  Run from the AMN3 repository root:

  ```powershell
  git -C worktrees/amn2-p7-c005-write-install archive --format=zip --output=../../dist/amn2-combined-overlay-0b858c5/amn2-codex-vps-test-prep-0b858c5-source.zip 0b858c5cdbc5b565cc265966a2edfe2d339d65e0
  ```

  Expected: archive comment equals the full commit and no working-tree,
  untracked, secret or runtime file is included.

- [x] **Step 3: Bind checksum and apply helper defaults**

  Compute SHA-256, copy `scripts/vps/amn2_apply_source_zip.sh`, and change only
  these defaults in the package copy:

  ```text
  AMN2_SOURCE_ZIP=/root/amn2-combined-overlay-0b858c5/amn2-codex-vps-test-prep-0b858c5-source.zip
  AMN2_EXPECTED_SOURCE_SHA=E03F13FD6A7BB5CBC5FCEE7179F395EA8C2864EBCEAB01BC351C5904F3CFF975
  AMN2_EXPECTED_SOURCE_COMMIT=0b858c5
  ```

  Expected: the helper remains otherwise byte-equivalent to the tested root
  helper and passes `bash -n`.

- [x] **Step 4: Write the inner contract and build the outer ZIP**

  The contract must state exact source/baseline/checksum/delta bindings,
  snapshot and rollback requirements, obsolete JPG removal, web-only restart,
  bot disabled state and AWG untouched invariant. Compress exactly the four
  allowlisted inner files and write the outer SHA-256 receipt.

  Expected: no upload or live mutation; outer entry count `4`.

### Task 2: Verify package integrity and behavior

**Files:**

- Test: `tests/test_amn2_apply_source_zip.py`
- Inspect: generated package files from Task 1

**Interfaces:**

- Consumes: Task 1 package and exact delta.
- Produces: package verification evidence suitable for a public gate document.

- [x] **Step 1: Run helper and markdown tests**

  Run:

  ```powershell
  python -m pytest tests/test_amn2_apply_source_zip.py tests/test_markdown_hygiene.py -q
  & 'C:\Program Files\Git\bin\bash.exe' -n dist/amn2-combined-overlay-0b858c5/amn2_apply_source_zip.sh
  ```

  Expected: all scoped tests pass and Bash syntax is valid.

- [x] **Step 2: Verify outer allowlist and both checksums**

  Inspect ZIP names and hashes without extraction.

  Expected: outer entries are exactly runbook, helper, source ZIP and source
  checksum; both recorded SHA-256 values equal computed bytes.

- [x] **Step 3: Verify inner archive binding and contents**

  Check the full Git archive comment, entry count, forbidden path/suffix rules,
  exact logo/header hashes, obsolete JPG absence and package-data declaration.

  Expected: commit binding exact, forbidden entries `0`, square logo copies
  byte-identical, wide header exact, and no secret-bearing/runtime state.

- [x] **Step 4: Run AMN2 source tests**

  Run from the AMN2 worktree:

  ```powershell
  python -m pytest tests -q
  ```

  Expected: full source suite passes with only the already known skip/warning.

### Task 3: Review security and publish the package gate

**Files:**

- Create: `research/amn2/phase-11-0b858c5-combined-overlay-package-prep-2026-07-16.md`
- Create: `docs/AMN2_PHASE_11_0B858C5_COMBINED_OVERLAY_GATE.ru.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`

**Interfaces:**

- Consumes: verified package hashes/counts and clean security scan.
- Produces: exact next live approval phrase without consuming or executing it.

- [ ] **Step 1: Run diff and security review**

  Review all tracked working-tree changes, generated ZIP contents and secret
  markers. Run `codex-security:security-diff-scan` on the Git-backed change.

  Expected: complete coverage and no unaddressed reportable finding before
  staging.

- [ ] **Step 2: Write evidence and the exact gate**

  Record hashes, entry counts, test results, scan result and the explicit
  no-live-mutation boundary. Prepare, but do not execute, this approval shape:

  ```text
  APPROVE PHASE11_0B858C5_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_TELEGRAM_PROFILE_UNCHANGED_AND_AWG_UNTOUCHED
  ```

- [ ] **Step 3: Synchronize current status and handoff**

  Mark package `prepared_local_not_uploaded_not_applied`; keep production
  `801f8c3`, bot disabled and AWG untouched; make rollout the next exact gate.

- [ ] **Step 4: Run final docs/diff verification**

  Run markdown hygiene, `git diff --check`, staged allowlist and staged
  secret-marker scan.

  Expected: tests and checks pass; `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`
  remains untracked and unstaged.

- [ ] **Step 5: Commit, push and verify origin**

  Stage only this plan, package artifacts, gate/evidence and the three status
  documents. Commit with a focused message, push
  `codex-spark-phase9-docs-sync`, and compare local/origin SHA.

  Expected: origin sync; package still not uploaded or applied to production.
