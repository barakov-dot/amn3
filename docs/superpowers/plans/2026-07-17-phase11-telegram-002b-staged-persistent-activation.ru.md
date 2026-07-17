# Phase 11 TELEGRAM-002B Staged Persistent Activation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify a local fail-closed executor that can later install
the exact `0b858c5` persistent Telegram unit/env, stage one disabled-at-boot
bot, require first-admin wide-header acceptance, and enable only after an exact
confirmation.

**Architecture:** A PowerShell trusted-transport runner performs literal
approval checking, absolute OpenSSH binding, same-byte remote-script hashing
and target redaction. A Bash executor owns production admission, root-only
snapshots, unit/env transaction, a 240-second automatic rollback watchdog and
separate `stage`/`accept` state. Static TDD tests prove ordering and prohibited
operations without contacting the VPS.

**Tech Stack:** PowerShell/.NET process APIs, Bash, systemd, Python 3.12 inline
SQLite/TOML-free helpers, pytest/unittest static contract tests, Git and Codex
Security diff review.

## Global Constraints

- Source overlay and full commit are exactly `0b858c5` and
  `0b858c5cdbc5b565cc265966a2edfe2d339d65e0`.
- Five source hashes and public expected identity are copied verbatim from the
  approved design spec.
- Runner modes are exactly `preflight`, `stage`, `accept`, `postflight`.
- `accept` requires a safe run id and exact confirmation
  `CONFIRM PHASE11_TELEGRAM_002B_FIRST_ADMIN_WIDE_HEADER_RESPONSE`.
- No local implementation/test step may resolve the production target, invoke
  SSH, call Telegram, change provider/VPS state or touch AWG.
- Remote code may inspect AWG read-only but contains no Docker/AWG/peer/config
  mutation command.
- Production database is never automatically overwritten by this executor.
- Do not read, modify, stage or commit
  `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`.

---

### Task 1: RED contract for the absent activation executors

**Files:**

- Create: `tests/test_phase11_telegram_002b_activation_executor.py`
- Expected absent: `scripts/vps/phase11_telegram_002b_persistent_remote.sh`
- Expected absent: `scripts/vps/phase11_telegram_002b_persistent_ssh_runner.ps1`

**Interfaces:**

- Consumes: paths relative to repository root.
- Produces: static contract for remote constants/modes/order/prohibitions and
  runner approval/transport/same-byte behavior.

- [x] **Step 1: Write failing tests for the remote executor**

  Define `REMOTE`, `RUNNER` and tests that first assert both files exist. For
  remote content require these literal bindings:

  ```python
  required = {
      'EXPECTED_OVERLAY="0b858c5"',
      'SOURCE_FULL_COMMIT="0b858c5cdbc5b565cc265966a2edfe2d339d65e0"',
      'EXPECTED_BOT_USERNAME="NeobyatnayaAMNZ_bot"',
      'UNIT_SOURCE_SHA="E0C6706B030775C9731CF3FC3A055CAE88512CF470BF2D6BFABDACD7F2F5F694"',
      'PERSISTENT_RUNTIME_SHA="F400FE8FDA673CA6976B698365A591CEC3A373C4284721A39AEF935DF16C5A31"',
      'APP_MAIN_SHA="C34A0F457B2242EDE138DD0B6DC1B08B860515F7BD2FADB7DF8F2B86A3F5ED31"',
      'SYSTEMD_NOTIFY_SHA="649EA2EABBD6B18C5E489D2059D08020D64914C47B15E50EA2873AEEFA99A8A3"',
      'SETTINGS_SHA="1DB81553DBCBF4DAFC710EFDD69C2DB0CC1A869F0754D7BB67C7ADFA3DCAC631"',
      'ROLLBACK_TTL_SECONDS="240"',
      'TELEGRAM_EXPECTED_BOT_USERNAME=NeobyatnayaAMNZ_bot',
      'TELEGRAM_ADMISSION_TIMEOUT_SECONDS=30',
      'TELEGRAM_POLLING_TIMEOUT_SECONDS=20',
      'TELEGRAM_RUNTIME_LOCK_PATH=/run/amn2-bot/polling.lock',
  }
  ```

  Assert mode case contains `preflight`, `stage`, `accept`, `postflight` and no
  other public mode. Assert `stage_activation` calls `systemctl start` before
  any `systemctl enable`, while `accept_activation` performs exact confirmation
  and DB-delta checks before enable.

- [x] **Step 2: Add rollback and security assertions**

  Require root-only state, unit/env/DB receipts, an automatic rollback helper,
  a transient 240-second systemd timer, safe run-id validation and exact admin
  row delta markers. Reject these patterns case-insensitively:

  ```python
  forbidden = [
      r"docker\s+(?:restart|stop|start|rm|kill|update)\b",
      r"(?:awg|wg)\s+set\b",
      r"setWebhook|deleteWebhook|drop_pending_updates",
      r"setChatPhoto|sendPhoto",
      r"sqlite3\s+.*(?:restore|\.restore)",
      r"cp\s+.*db-before.*amneziya\.sqlite3",
  ]
  ```

  Require `systemctl stop/disable "$BOT_UNIT"` only in rollback/stage cleanup,
  no web service mutation, and AWG snapshot string equality before/after.

- [x] **Step 3: Add runner assertions**

  Require:

  ```python
  '[ValidateSet("preflight", "stage", "accept", "postflight")]'
  '[string]$Approval'
  '[string]$RunId = ""'
  '[string]$Confirmation = ""'
  '[string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)'
  '[string]::Equals($Confirmation, $expectedConfirmation, [StringComparison]::Ordinal)'
  '$trustedOpenSshDir = Join-Path $env:WINDIR "System32\\OpenSSH"'
  '[IO.File]::ReadAllBytes($remoteScript)'
  '-StandardInputBytes $remoteScriptBytes'
  '-replace [regex]::Escape($target), "<target>"'
  'Convert]::ToBase64String'
  'FileMode]::CreateNew'
  'GlobalKnownHostsFile=none'
  'KnownHostsCommand=none'
  ```

  Compute `hashlib.sha256(REMOTE.read_bytes()).hexdigest().upper()` and assert
  the exact literal is present in `$expectedRemoteScriptSha` and in the live
  approval string immediately after the literal prefix
  `REMOTE_ORCHESTRATOR_SHA_`.

- [x] **Step 4: Run RED**

  Run:

  ```powershell
  python -m pytest tests/test_phase11_telegram_002b_activation_executor.py -q
  ```

  Expected: failures because both executor files are absent; no test may fail
  for an unrelated import or fixture error.

### Task 2: GREEN remote fail-closed executor

**Files:**

- Create: `scripts/vps/phase11_telegram_002b_persistent_remote.sh`
- Test: `tests/test_phase11_telegram_002b_activation_executor.py`

**Interfaces:**

- Consumes: mode plus optional run id and confirmation from verified SSH
  standard input execution.
- Produces: sanitized key/value receipts and a state root under
  `/root/amn2-telegram-002b/<run-id>`.

- [x] **Step 1: Implement constants, command gates and safe paths**

  Start with `set -Eeuo pipefail`, `umask 077`, exact design constants and:

  ```bash
  MODE="${1:-preflight}"
  RUN_ID="${2:-}"
  CONFIRMATION="${3:-}"
  STATE_BASE="/root/amn2-telegram-002b"
  BOT_UNIT="amneziya-bot.service"
  WEB_UNIT="amneziya-web.service"
  EXPECTED_CONFIRMATION="CONFIRM PHASE11_TELEGRAM_002B_FIRST_ADMIN_WIDE_HEADER_RESPONSE"
  ```

  Implement `require_cmd`, `safe_state_root`, `validate_run_id` with
  `^[0-9]{8}T[0-9]{6}Z$`, non-symlink checks and root-owned mode `0700` state.

- [x] **Step 2: Implement read-only source/runtime snapshots**

  Add functions for exact source file SHA checks, write-gate parsing, private
  web/listener health, bot active/enabled/PID state, SQLite integrity and
  application-row canonical snapshot, AWG read-only container/restart/peer
  snapshot and disk checks.

  The application snapshot helper must serialize every non-`sqlite_%` table in
  stable column/row order, support exclusion of exactly the first configured
  administrator's `users` row and emit hashes/counts without printing the ID.

  The venv interpreter may be a symlink; resolve it with `readlink -f` and
  require the final target to be a regular executable. Source/unit/env inputs
  remain strict non-symlink regular files.

- [x] **Step 3: Implement non-acknowledging Telegram preflight**

  Execute a bounded Python helper as service user with production environment.
  It imports `admit_persistent_bot`, passes the literal expected username,
  verifies `getMe`, empty webhook, pending count zero and zero-time ownership
  probe, closes the bot session and prints only:

  ```text
  telegram_preflight=pass
  identity_match=true
  webhook_configured=false
  pending_update_count=0
  ownership_probe=empty
  ```

  Never print token, proxy, numeric IDs, exception payload or webhook URL.

- [x] **Step 4: Implement root-only rollback state and helper**

  Snapshot installed unit, `.env`, metadata, SQLite online backup, canonical
  DB state, web/bot/AWG state and source receipts. Generate a mode-0700 fixed
  rollback helper inside the state root that:

  ```bash
  systemctl stop "$BOT_UNIT" || true
  systemctl disable "$BOT_UNIT" || true
  install -o root -g root -m 0644 "$STATE_ROOT/unit.before" "$UNIT_FRAGMENT"
  install -o "$ENV_UID" -g "$ENV_GID" -m "$ENV_MODE" "$STATE_ROOT/env.before" "$ENV_PATH"
  systemctl daemon-reload
  ```

  It must never restore DB, mutate web or invoke Docker/AWG. It writes a
  root-only rollback receipt and proves bot inactive/disabled afterward.

- [x] **Step 5: Implement atomic env/unit stage**

  Use a Python env updater that rejects duplicate keys, preserves unrelated
  lines and atomically replaces `.env` with the four exact values from Global
  Constraints. Install the exact source unit, daemon-reload, verify unit/env
  hashes and require bot still disabled before `systemctl start`.

  Arm a 240-second transient rollback timer and signal traps before the first
  unit/env mutation. After start wait for active/running, `NRestarts=0`, one
  cgroup PID, exact sanitized admission receipt and nonzero watchdog timestamp.
  Prove application rows are unchanged before admin traffic. Then emit
  `run_id`, `bot=active_disabled`, and
  `awaiting_admin_start=true`.

  Collect the sanitized admission receipt with a bounded 15-second retry so
  normal journald ingest latency cannot create a false negative. Every retry
  overwrites the local sanitized receipt and accepts only the exact admission,
  pending-update and allowed-update markers. If an immediate stage/accept
  rollback is required, run the exact rollback helper first and then stop and
  reset only the transient rollback timer/service derived from that run id.
  Compensation traps must then clear themselves and exit nonzero with status
  1, 129, 130 or 143; neither stage nor accept may resume after ERR, HUP, INT
  or TERM.

- [x] **Step 6: Implement exact-confirmed accept**

  `accept_activation` must validate run id/state/confirmation, require timer
  still armed, compare DB snapshots so only the selected existing admin row's
  mutable profile/timestamp fields changed, require all other application rows
  and counts unchanged, and reject service errors/restarts.

  Install a compensation rollback trap before canceling the timer; reject
  `activating`/queued rollback service states, revalidate unit/env, then run
  `systemctl enable "$BOT_UNIT"`. Clear the trap only after marking the state
  accepted root-only and emit:

  ```text
  activation=pass
  bot=active_enabled_single_instance
  first_admin_start=accepted
  wide_header_confirmation=exact
  watchdog=healthy
  database_delta=first_admin_user_row_only
  awg=unchanged
  ```

- [x] **Step 7: Implement postflight and mode dispatch**

  Postflight requires active/enabled, exact unit/env, PID one, restarts zero,
  readiness/watchdog receipts, webhook empty/backlog zero without calling
  `getUpdates`, private web, DB integrity/FK zero and unchanged AWG receipt.

  Dispatch exactly:

  ```bash
  case "$MODE" in
    preflight) preflight ;;
    stage) stage_activation ;;
    accept) accept_activation ;;
    postflight) postflight ;;
    *) die "unsupported mode" ;;
  esac
  ```

- [x] **Step 8: Run focused tests and Bash syntax**

  Run:

  ```powershell
  python -m pytest tests/test_phase11_telegram_002b_activation_executor.py -q
  & 'C:\Program Files\Git\bin\bash.exe' -n scripts/vps/phase11_telegram_002b_persistent_remote.sh
  ```

  Expected: remote tests pass; runner-existence tests remain RED until Task 3;
  Bash syntax exits zero.

### Task 3: GREEN trusted PowerShell runner and exact live phrase binding

**Files:**

- Create: `scripts/vps/phase11_telegram_002b_persistent_ssh_runner.ps1`
- Modify: `tests/test_phase11_telegram_002b_activation_executor.py`

**Interfaces:**

- Consumes: `-Mode`, exact `-Approval`, optional safe `-RunId` and exact
  `-Confirmation`.
- Produces: a same-byte SSH invocation of the remote executor with sanitized
  output.

- [x] **Step 1: Compute finalized remote SHA and construct approval**

  Run `Get-FileHash -Algorithm SHA256` on the remote script. Construct one
  literal approval containing that uppercase digest:

  ```powershell
  $remoteSha = (Get-FileHash -Algorithm SHA256 `
      scripts/vps/phase11_telegram_002b_persistent_remote.sh).Hash
  $approval = "APPROVE PHASE11_TELEGRAM_002B_REMOTE_ORCHESTRATOR_SHA_${remoteSha}_0B858C5_EXACT_UNIT_ENV_TELEGRAM_PREFLIGHT_DISABLED_FIRST_STAGE_FIRST_CONFIGURED_ADMIN_SINGLE_START_WIDE_HEADER_EXACT_CONFIRM_ACCEPT_ENABLE_POSTFLIGHT_AUTOROLLBACK240_NO_BLIND_DB_RESTORE_WEB_UNTOUCHED_AND_AWG_UNTOUCHED"
  ```

  Paste the resulting 64 digest characters into the committed runner literal;
  the committed value must not be generated at runner execution time.

- [x] **Step 2: Implement fail-closed local admission**

  Validate exact approval by ordinal full-string equality before defining
  `$sshDir` or reading known-host. Validate mode-specific arguments:

  ```powershell
  if ($Mode -eq "accept") {
      if ($RunId -notmatch '^[0-9]{8}T[0-9]{6}Z$') { throw "Safe run id required" }
      if (-not [string]::Equals($Confirmation, $expectedConfirmation,
              [StringComparison]::Ordinal)) { throw "Exact acceptance confirmation mismatch" }
  } elseif ($RunId -or $Confirmation) {
      throw "Run id and confirmation are accept-only"
  }
  ```

- [x] **Step 3: Reuse trusted same-byte transport pattern**

  Bind absolute OpenSSH `ssh.exe`, dedicated key and known-host, verify the
  remote file exists, read it once as bytes, hash those bytes against the
  literal digest, then pass the same bytes to `bash -s -- <mode> <run-id>
  <confirmation>` through `StandardInput.BaseStream.Write`.

  Redact target from combined output and fail on nonzero exit without printing
  command arguments containing private bindings.

- [x] **Step 4: Run complete focused GREEN**

  Run:

  ```powershell
  python -m pytest tests/test_phase11_telegram_002b_activation_executor.py -q
  ```

  Expected: all focused tests pass.

- [x] **Step 5: Parse-check both executors without transport**

  Run PowerShell parser AST/error checks and Bash `-n`. Expected: zero parser
  errors and exit zero. Do not invoke either runner mode.

### Task 4: Verification, diff and security review

**Files:**

- Review: new spec/plan/test/executors and later status evidence.

**Interfaces:**

- Consumes: completed local implementation.
- Produces: fresh test, syntax, diff, secret-scan and security receipts.

- [x] **Step 1: Run scoped verification**

  Run the focused executor test, markdown hygiene and existing rollout executor
  test. Expected: all pass.

- [x] **Step 2: Run full verification**

  Run:

  ```powershell
  python -m pytest tests -q
  ```

  Expected baseline: at least the previous `95 passed` plus the new focused
  tests, with zero failures.

- [x] **Step 3: Run diff and high-confidence secret checks**

  Require `git diff --check`, exact changed-file allowlist and no Telegram token,
  private-key block, credentialed URL, target literal, admin numeric ID or raw
  environment/log payload. Keep the client baseline untracked and unstaged.

- [x] **Step 4: Run Codex Security diff review**

  Threat-model approval replay, root-script substitution, command injection,
  run-id traversal, rollback helper tampering, env secret disclosure, unsafe DB
  restore, premature enable, restart loops and AWG mutation. Fix reportable
  findings, rerun affected tests and require final findings `0` before commit.

### Task 5: Status, evidence, commit and trusted-origin verification

**Files:**

- Create: `research/amn2/phase-11-telegram-002b-staged-persistent-activation-gate-2026-07-17.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`

**Interfaces:**

- Consumes: exact remote/runner hashes and all verification receipts.
- Produces: `READY-AWAITING-SEPARATE-EXACT-LIVE-APPROVAL`, one non-reusable
  phrase and origin-synced Phase 11 state.

- [x] **Step 1: Write sanitized local evidence and status override**

  Record design/plan/executor paths, exact hashes, RED/GREEN receipts, full test
  count, syntax/diff/security outcome and explicit `live_action=false`.
  Document the future operator sequence: exact approval → preflight → stage →
  first-admin `/start` → exact visual confirmation → accept → postflight.

- [x] **Step 2: Stage exact files and reverify staged content**

  Stage only TELEGRAM-002B files plus the three current-status documents. Run
  staged name allowlist, `git diff --cached --check` and high-confidence secret
  scan. Confirm the client baseline remains untracked.

- [x] **Step 3: Commit and push**

  Commit with message `Prepare Phase 11 Telegram 002B activation gate`, push
  `codex-spark-phase9-docs-sync`, fetch and require local HEAD equal
  `origin/codex-spark-phase9-docs-sync`.

- [x] **Step 4: Publish exact live phrase without consuming it**

  Output the exact literal embedded in the runner and mark it prepared,
  non-reusable and unconsumed. Do not invoke `preflight`, `stage`, `accept` or
  `postflight` in this local task.

### Journal-race correction security override

The first correction review found that a successful signal rollback could
stop the watchdog and then resume privileged execution. RED coverage requires
signal-specific rollback-and-exit traps. The same review requires the current
exact live approval literal to remain absent from authority documents until
tests, zero-reportable security rescan, commit, push and origin readback all
pass.
