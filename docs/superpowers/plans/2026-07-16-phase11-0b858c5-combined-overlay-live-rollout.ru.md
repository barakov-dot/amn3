# Phase 11 `0b858c5` combined overlay live rollout plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** После отдельной exact approval-фразы безопасно перевести private
AMN2 production source overlay с `801f8c3` на `0b858c5`, сохранив production
database, regular bot disabled и AWG полностью нетронутым.

**Architecture:** Локальный PowerShell runner использует pinned SSH key и
known-host binding, загружает только checksum-bound package и передаёт
проверенный Bash orchestrator через stdin. Remote orchestrator выполняет
read-only preflight, создаёт уникальный root-only rollback bundle, останавливает
и запускает только private web service, применяет exact source offline и
автоматически откатывает source/marker/database при нарушении любого invariant.
Локальные `ssh.exe`/`scp.exe` разрешаются только как абсолютные файлы из
`%WINDIR%\System32\OpenSSH`; helper отвергает относительные и внешние пути до
`Process.Start`.

**Tech Stack:** PowerShell, OpenSSH/SCP, Bash, Python/SQLite backup API,
ZIP/SHA-256, systemd, Docker/AWG read-only inspection, pytest, Markdown.

## Global Constraints

- Exact approval is required before any VPS/SSH/upload/live verification.
- Production baseline before apply must be `801f8c3`.
- Candidate source is full commit
  `0b858c5cdbc5b565cc265966a2edfe2d339d65e0`.
- Package SHA-256 is
  `7866BDD9FEBE1D6EEA701B37A6E4206A8267766A56993F3C02A0C7B30C394B54`.
- Reviewed remote executor SHA-256 is
  `A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72` and
  the runner must hash and transmit the same byte array.
- The local runner must use trusted absolute `%WINDIR%\System32\OpenSSH`
  paths for both SSH and SCP and fail closed when either binary is absent.
- Source ZIP SHA-256 is
  `E03F13FD6A7BB5CBC5FCEE7179F395EA8C2864EBCEAB01BC351C5904F3CFF975`.
- Stop/start only `amneziya-web.service`; regular bot remains
  inactive/disabled and its installed unit/env are read-only evidence.
- Never stop, restart, recreate, reconfigure or mutate AWG, peers or configs.
- Do not call Telegram or mutate Telegram profile media.
- Do not initialize/migrate/write production schema or run API write smoke.
- Preserve `.env`, `servers.yml`, `data`, `venv` and private runtime evidence.
- Do not touch `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`.

---

### Task 1: Close the local gate review

**Files:**

- Inspect: `docs/AMN2_PHASE_11_0B858C5_COMBINED_OVERLAY_GATE.ru.md`
- Inspect: `dist/amn2-combined-overlay-0b858c5.zip`
- Inspect: `worktrees/amn2-p7-c005-write-install`
- Create: `research/amn2/phase-11-0b858c5-combined-overlay-rollout-gate-review-2026-07-16.md`

**Interfaces:**

- Consumes: committed package gate and exact source/baseline bindings.
- Produces: a ready-but-not-consumed live gate and exact approval phrase.

- [x] **Step 1: Recompute immutable local bindings**

  Recompute outer/inner hashes and sizes; verify the exact four-entry outer
  allowlist, inner full commit comment, 383 source entries, both asset hashes,
  obsolete JPG absence, forbidden/unsafe/symlink zero and exact 31-path Git
  delta from `801f8c3`.

- [x] **Step 2: Re-run scoped local verification**

  Run:

  ```powershell
  python -m pytest tests/test_amn2_apply_source_zip.py tests/test_markdown_hygiene.py -q
  & 'C:\Program Files\Git\bin\bash.exe' -n dist/amn2-combined-overlay-0b858c5/amn2_apply_source_zip.sh
  ```

  Expected: all tests and Bash syntax pass.

- [x] **Step 3: Record the exact approval boundary**

  Record `READY-AWAITING-EXACT-APPROVAL`; no VPS/SSH/upload/service/Telegram/
  database/provider/AWG action occurs during this task.

### Task 2: Prepare and verify the bounded live executor

**Files:**

- Create: `scripts/vps/phase11_0b858c5_combined_ssh_runner.ps1`
- Create: `scripts/vps/phase11_0b858c5_combined_remote_rollout.sh`
- Test: `tests/test_phase11_0b858c5_rollout_executor.py`

**Interfaces:**

- Consumes: the verified package, pinned SSH transport and prior successful
  `801f8c3`/logo rollout executor patterns.
- Produces: syntax-checked modes `preflight`, `upload`, `apply`, `postflight`
  with automatic rollback.

- [x] **Step 1: Bind the PowerShell runner**

  Bind only the existing dedicated production key, known-host file, exact
  package/checksum and remote script. Require ordinal full-string equality with
  the exact approval phrase before resolving the target or invoking SCP/SSH.
  Redact the target from captured output.

- [x] **Step 2: Bind the remote orchestrator**

  Require overlay `801f8c3`, exact package/source/helper/runbook hashes, full
  source commit, exact outer allowlist, asset/package-data checks and exact
  31-path post-apply delta. Capture bot unit/env hashes read-only.

- [x] **Step 3: Prove rollback completeness**

  Before apply create mode-0700 unique rollback root containing tracked source,
  marker, SQLite backup/snapshot, AWG snapshot, source manifest and bot unit/env
  hashes. On any failure restore source/marker/database as required, restart
  only web and re-prove web/bot/database/AWG invariants, including an explicit
  complete database snapshot comparison after any restore.

- [x] **Step 4: Run local syntax and secret-safety checks**

  Run PowerShell parser validation, `bash -n`, staged/local marker scans and a
  diff review against the proven `6abc620` executor template.

### Task 3: Execute only after the exact approval phrase

**Files:**

- Use: `scripts/vps/phase11_0b858c5_combined_ssh_runner.ps1`
- Use: `dist/amn2-combined-overlay-0b858c5.zip`

**Interfaces:**

- Consumes: the exact operator approval phrase and Task 2 executor; the phrase
  is passed to the runner and must match by ordinal full-string equality.
- Produces: either `rollout=pass` on `0b858c5` or verified automatic rollback
  to `801f8c3`.

- [x] **Step 1: Run secret-safe read-only preflight**

  Require exact baseline, web private health, write gates false/false, bot
  inactive/disabled/process zero, database integrity/FK zero, sufficient disk
  and unchanged running AWG snapshot. Stop before upload on any mismatch.

- [x] **Step 2: Upload exact package and checksum**

  Upload only the two bound files to `/root`, set mode `0600`, then re-run the
  remote hash and path checks.

- [x] **Step 3: Apply the exact offline source transaction**

  Freeze only web, create/verify rollback material, apply source offline,
  remove only stale tracked `app/web/static/brand-full.jpg`, start only web and
  verify served square logo plus exact wide-header source asset.

- [x] **Step 4: Run independent postflight**

  Require overlay `0b858c5`, web active/enabled/private, bot unchanged,
  database file/logical/count invariants unchanged and AWG container/restart/
  peer-set invariants unchanged.

### Task 4: Publish rollout evidence and current status

**Files:**

- Create: `research/amn2/phase-11-0b858c5-combined-overlay-rollout-2026-07-17.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`

**Interfaces:**

- Consumes: sanitized preflight/apply/postflight output.
- Produces: origin-synced rollout state and next Telegram-002B review gate.

- [x] **Step 1: Write sanitized evidence and status override**

  Record pass or rollback result, run id, package/source bindings, safe
  database/AWG summaries and exclusions. Never publish target, keys, tokens,
  secrets or raw logs.

- [x] **Step 2: Run scoped docs/diff/security review**

  Run markdown hygiene, `git diff --check`, exact staged allowlist and security
  diff review. Keep the client baseline untracked and unstaged.

- [x] **Step 3: Commit, push and verify AMN3 origin**

  Commit only plan/evidence/status files, push
  `codex-spark-phase9-docs-sync`, then require local HEAD equal origin HEAD.

### Task 5: Review the separate Telegram-002B gate

**Files:**

- Inspect: production postflight evidence.
- Create only after rollout pass: Telegram-002B gate review evidence/plan.

**Interfaces:**

- Consumes: verified production overlay `0b858c5` with regular bot still
  inactive/disabled.
- Produces: a separate exact approval proposal; it does not activate the bot.

- [ ] **Step 1: Review persistent activation admission and rollback scope**

  Require identity/webhook/backlog/single-instance/readiness/watchdog checks,
  installed unit/env binding and a bot-only rollback contract with AWG
  untouched.

- [ ] **Step 2: Stop before bot activation**

  Prepare a separate exact Telegram-002B approval phrase. Do not install,
  enable or start the bot under the source-rollout approval.
