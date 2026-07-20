# Spain transport-stage subreason diagnostic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Классифицировать будущий OpenSSH transport failure в безопасный allowlisted subreason без сохранения raw output.

**Architecture:** PowerShell runner временно объединяет native output в память, сначала сохраняет приоритет remote probe envelope, затем для transport `exit=255` вызывает pure allowlist classifier. До записи sanitized evidence все raw variables очищаются. Remote Bash probe не меняется.

**Tech Stack:** PowerShell, OpenSSH, Python unittest/pytest, Git.

## Global Constraints

- Outcome `spain-fresh-20260720-007`; trust bundle `spain-fresh-20260720-001`.
- Allowlist: `connect_timeout`, `connection_refused`, `no_route`, `name_resolution`, `host_key`, `authentication`, `remote_closed`, `remote_reset`.
- Unknown/ambiguous/non-255 input maps only to `unavailable`.
- No raw OpenSSH output persistence; no SSH before a new literal approval.
- No Spain/AWG/Telegram/web/service mutation.
- Do not touch `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` or unrelated files.

---

### Task 1: RED classifier contract

**Files:**
- Modify: `tests/test_post_release_spain_readonly_preflight.py`

**Interfaces:**
- Produces: expected PowerShell function `Get-SafeTransportSubreason([object[]]$Lines, [int]$ProcessExitCode) -> string`.

- [ ] **Step 1: Add a real PowerShell harness test**

The harness extracts the production classifier, passes representative OpenSSH
lines for all eight categories, and asserts exact safe names. Add negative
cases for unknown text, two categories, and exit other than `255`.

- [ ] **Step 2: Run RED**

Run: `python -m pytest tests/test_post_release_spain_readonly_preflight.py -q`
Expected: FAIL because `Get-SafeTransportSubreason` does not exist.

### Task 2: Minimal in-memory classifier and run binding

**Files:**
- Modify: `scripts/vps/post_release_spain_readonly_preflight_ssh_runner.ps1`
- Modify: `tests/test_post_release_spain_readonly_preflight.py`

**Interfaces:**
- Consumes: OpenSSH combined in-memory objects and process exit code.
- Produces: one allowlisted safe string only.

- [ ] **Step 1: Implement anchored rules with distinct-category counting**

Use an ordinal HashSet of safe names; return its only member only when
`exit=255` and distinct match count equals one, else return `unavailable`.

- [ ] **Step 2: Capture only in memory and clear before evidence write**

Replace discarded stderr with assigned combined output, call the classifier
only when no safe remote envelope exists, and set raw variables to `$null`
before constructing/persisting failure evidence.

- [ ] **Step 3: Bind the new single-use outcome**

Change exact run/approval fields from `006` to `007`. Keep remote script SHA,
source revision and immutable trust bundle unchanged.

- [ ] **Step 4: Run GREEN**

Run: `python -m pytest tests/test_post_release_spain_readonly_preflight.py -q`.
Expected: all focused tests pass.

### Task 3: Status, verification and approval

**Files:**
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`
- Modify: `docs/POST_RELEASE_SPAIN_READONLY_PREFLIGHT_GATE.ru.md`
- Create: `docs/POST_RELEASE_SPAIN_PREFLIGHT_007_APPROVAL.ru.md`

- [ ] **Step 1: Record local readiness only**

Document `run_007=not_created|not_run|approval_required`, new runner SHA and
unchanged remote probe SHA. Do not claim live verification.

- [ ] **Step 2: Verify**

Run focused/full tests, PowerShell parse/approval preview match,
`git diff --check`, staged secret scan and security diff review.

- [ ] **Step 3: Commit, push and verify origin**

Stage only scoped files, commit, push the current branch, fetch/read back exact
HEAD, then issue the exact literal approval. Do not execute run 007.
