# Spain Empty Cgroup Process List Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Исправить ложный `pid/76` failure для успешно прочитанного пустого `cgroup.procs` и подготовить новый single-use read-only run `005`.

**Architecture:** Existing collector сохраняет direct-call result variables. После успешного чтения process list он отдельно распознаёт zero rows как complete empty port set; при наличии строк каждая остаётся strict numeric PID. Runner меняет только exact remote checksum и single-use outcome binding `004 -> 005`.

**Tech Stack:** Bash, Windows PowerShell 5.1, Python `unittest`/`pytest`, Git.

## Global Constraints

- Approved spec: commit `daf4a22`.
- Source revision: `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
- Immutable trust bundle: `spain-fresh-20260720-001`.
- New outcome run: `spain-fresh-20260720-005`.
- Runs `001–004` consumed; no retry, deletion, or reuse.
- Zero process rows are success with empty `COLLECTED_UNIT_PORTS` and empty subreason.
- Any existing nonnumeric process row remains `pid` failure.
- No raw unit/PID/cgroup/FD/socket/target values in output or evidence.
- No SSH until a new exact literal approval is returned after origin readback.
- Never stop or mutate AWG; unrelated service remains untouched.
- Do not touch `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` or unrelated files.

---

### Task 1: RED zero-process collector regression

**Files:**
- Modify: `tests/test_post_release_spain_readonly_preflight.py`
- Test: `tests/test_post_release_spain_readonly_preflight.py`

**Interfaces:**
- Consumes: extracted real Bash `collect_ports_for_cgroup`.
- Produces: regression proving empty process list is complete success.

- [ ] **Step 1: Add the failing harness assertion**

In the existing collector harness, create a readable empty
`demo.service/cgroup.procs`, call the real collector, and require:

```bash
collect_ports_for_cgroup /demo.service "$cgroup_root" "$proc_root"
[[ -z "$COLLECTED_UNIT_PORTS" ]]
[[ -z "$CGROUP_PORTS_SUBREASON" ]]
```

Keep the following existing malformed-row case and require `pid` failure so
the correction cannot weaken validation.

- [ ] **Step 2: Run RED**

Run:

```powershell
python -m pytest tests/test_post_release_spain_readonly_preflight.py -q -k "ports_collector_reports" --tb=short
```

Expected: FAIL because the empty file enters one here-string iteration and the
collector returns `CGROUP_PORTS_SUBREASON=pid`.

### Task 2: GREEN explicit zero-row branch

**Files:**
- Modify: `scripts/vps/post_release_spain_readonly_preflight_remote.sh`
- Test: `tests/test_post_release_spain_readonly_preflight.py`

**Interfaces:**
- Consumes: successful `cgroup_pids` read.
- Produces: success before the PID loop only when zero rows were returned.

- [ ] **Step 1: Add the minimal branch**

Immediately after the existing successful `awk` read:

```bash
if [[ -z "$cgroup_pids" ]]; then
    return 0
fi
```

The result variables were already cleared on function entry, so this returns a
complete empty port set without adding a second output path. Do not add
`continue` for empty PID rows and do not change any later failure mapping.

- [ ] **Step 2: Run focused GREEN and parse checks**

```powershell
python -m pytest tests/test_post_release_spain_readonly_preflight.py -q --tb=short
& 'C:\Program Files\Git\bin\bash.exe' -n scripts/vps/post_release_spain_readonly_preflight_remote.sh
```

Expected: all Spain tests PASS and Bash parse exit `0`.

### Task 3: Rebind exact runner to single-use run 005

**Files:**
- Modify: `scripts/vps/post_release_spain_readonly_preflight_ssh_runner.ps1`
- Modify: `tests/test_post_release_spain_readonly_preflight.py`

**Interfaces:**
- Consumes: final exact SHA-256 of the remote Bash probe.
- Produces: checksum-bound empty-approval preview for outcome run `005`.

- [ ] **Step 1: Add RED run-binding expectations**

Update tests to require:

```text
$expectedRunId = "spain-fresh-20260720-005"
TRUST_RUN_ID_SPAIN_FRESH_20260720_005
NEW_OUTCOME_RUN_SPAIN_FRESH_20260720_005
```

Immutable trust bundle remains `001`. Old approval/run `004` must fail before
private state and SSH.

- [ ] **Step 2: Run RED binding tests**

Run the focused file. Expected: FAIL while runner is still bound to `004`.

- [ ] **Step 3: Update runner binding**

Compute exact SHA-256 of the corrected remote probe. Replace only
`$expectedRemoteScriptSha`, `$expectedRunId`, and the two run `005` fragments in
`$expectedApproval`. Do not alter SSH, ACL, host-pin, evidence, or mutation
boundaries.

- [ ] **Step 4: Run focused GREEN and PowerShell parse**

Expected: all Spain tests PASS; PowerShell parser reports zero errors.

### Task 4: Full verification, security, status, publication, and preview

**Files:**
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`
- Modify: `docs/POST_RELEASE_SPAIN_READONLY_PREFLIGHT_GATE.ru.md`
- Modify: `docs/POST_RELEASE_SPAIN_PREFLIGHT_RUN_004_FAILURE_EVIDENCE.ru.md`

**Interfaces:**
- Consumes: final SHA values and verification evidence.
- Produces: origin-verified correction commit and one exact run `005` approval.

- [ ] **Step 1: Run full verification**

```powershell
python -m pytest tests -q --tb=short
git diff --check
```

Also run Bash/PowerShell parse, exact hash assertion, and added-lines secret
scan. Expected: `203` tests plus any new test count, all PASS, secret matches `0`.

- [ ] **Step 2: Run independent diff/security review**

Review every scoped code/test/doc file. Any reportable finding must be fixed,
regression-tested, and re-reviewed before commit.

- [ ] **Step 3: Sync status**

Record run `004` as consumed, correction locally verified, run `005` not
created/not run, final hashes, tests, security result, and unchanged
AWG/Telegram/unrelated service. Fresh install remains blocked pending run `005`
success.

- [ ] **Step 4: Commit and push only scoped files**

Commit message:

```text
Fix Spain empty cgroup process handling
```

Push `codex-spark-phase9-docs-sync` and require local HEAD equals trusted origin.

- [ ] **Step 5: Print exact approval safely**

Invoke runner with empty approval and run id `spain-fresh-20260720-005`.
Expected: one fully materialized literal and failure before private state/SSH.
Stop for the operator to return that exact literal.
