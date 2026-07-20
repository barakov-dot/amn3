# Spain systemd cgroup ports subreason diagnostic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить secret-safe allowlisted subreason diagnosis для отказов `systemd_cgroup_ports` и подготовить отдельный single-use read-only run `004`.

**Architecture:** Remote collector вызывается напрямую и возвращает port set либо закрытый subreason через result variables. Caller переводит subreason в fixed exit `75–80`; PowerShell runner валидирует пару stage/exit и сохраняет только безопасное имя subreason. Existing approval, private-root, host-pin и no-mutation boundaries сохраняются.

**Tech Stack:** Bash, Windows PowerShell 5.1, Python `unittest`/`pytest`, Git.

## Global Constraints

- Source revision: `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
- Immutable trust bundle: `spain-fresh-20260720-001`.
- New outcome run: `spain-fresh-20260720-004`.
- Runs `001–003` consumed; no retry or deletion.
- No raw unit/PID/cgroup/FD/socket/target values in envelope, evidence, docs or tests.
- No SSH until a new exact literal approval is returned after origin readback.
- Never stop or mutate AWG; unrelated service remains untouched.
- Do not touch `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` or unrelated files.

---

### Task 1: RED remote collector subreason tests

**Files:**
- Modify: `tests/test_post_release_spain_readonly_preflight.py`
- Test: `tests/test_post_release_spain_readonly_preflight.py`

**Interfaces:**
- Consumes: existing Bash function extraction harness.
- Produces: expected `collect_ports_for_cgroup`, `COLLECTED_UNIT_PORTS`, `CGROUP_PORTS_SUBREASON`, exits `75–80`.

- [ ] **Step 1: Add failing static and harness tests**

Tests must require the six exact subreason names, reject raw values, prove the
collector is called directly, and simulate at least cgroup file, invalid PID,
FD directory, readlink, socket table and parser failures.

- [ ] **Step 2: Run RED tests**

Run:
`python -m pytest -q tests/test_post_release_spain_readonly_preflight.py -k "cgroup_ports_subreason or ports_collector"`

Expected: FAIL because the direct collector and allowlist do not exist.

### Task 2: GREEN direct-call Bash collector

**Files:**
- Modify: `scripts/vps/post_release_spain_readonly_preflight_remote.sh`
- Test: `tests/test_post_release_spain_readonly_preflight.py`

**Interfaces:**
- Consumes: verified cgroup path from `resolve_unit_cgroup`.
- Produces: `COLLECTED_UNIT_PORTS` and `CGROUP_PORTS_SUBREASON`.

- [ ] **Step 1: Replace command-substitution collector call**

Call `collect_ports_for_cgroup "$control_group"` directly. On nonzero result,
map only `cgroup_procs/pid/fd_directory/fd_readlink/socket_table/socket_parse`
to `emit_failure 75..80`; unknown values use sanitized failure.

- [ ] **Step 2: Keep all data local and quoted**

No function branch prints a PID, path, FD, socket row or error text. Successful
ports are assigned only to `COLLECTED_UNIT_PORTS` after complete normalization.

- [ ] **Step 3: Run focused GREEN tests and Bash parse**

Run:
`python -m pytest -q tests/test_post_release_spain_readonly_preflight.py`

Run:
`C:\Program Files\Git\bin\bash.exe -n scripts/vps/post_release_spain_readonly_preflight_remote.sh`

Expected: all PASS.

### Task 3: Runner safe subreason mapping and run 004

**Files:**
- Modify: `scripts/vps/post_release_spain_readonly_preflight_ssh_runner.ps1`
- Modify: `tests/test_post_release_spain_readonly_preflight.py`

**Interfaces:**
- Consumes: `(stage=systemd_cgroup_ports, exit=75..80)`.
- Produces: failure evidence `subreason` containing one allowlisted name.

- [ ] **Step 1: Add RED runner tests**

Require exact mapping, rejection of unknown stage/exit pairs, run id `004`,
immutable trust `001`, and empty-approval stop before private state.

- [ ] **Step 2: Implement mapping**

Extend safe failure parsing with a fixed map. No remote text becomes a key or
value. Store `subreason=unavailable` for transport and non-cgroup stages.

- [ ] **Step 3: Run focused GREEN tests and PowerShell parse**

Run:
`python -m pytest -q tests/test_post_release_spain_readonly_preflight.py`

Run:
`[scriptblock]::Create((Get-Content -Raw scripts/vps/post_release_spain_readonly_preflight_ssh_runner.ps1)) | Out-Null`

Expected: all PASS.

### Task 4: Verification, security, status and publication

**Files:**
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`
- Modify: `docs/POST_RELEASE_SPAIN_READONLY_PREFLIGHT_GATE.ru.md`
- Modify: `docs/POST_RELEASE_SPAIN_SYSTEMD_MAINPID_FALLBACK_IMPLEMENTATION_EVIDENCE.ru.md`

**Interfaces:**
- Consumes: final runner/probe SHA, test and security evidence.
- Produces: origin-verified commit and exact run `004` approval preview.

- [ ] **Step 1: Run full verification**

Run `python -m pytest -q tests`, Bash/PowerShell parse and `git diff --check`.

- [ ] **Step 2: Run diff/security and new-lines secret scan**

Review every changed code/test/doc file. Reportable findings must be fixed and
rechecked before commit.

- [ ] **Step 3: Sync docs and commit only scoped files**

Commit message: `Add Spain cgroup port subreason diagnostics`.

- [ ] **Step 4: Push and verify origin**

Push `codex-spark-phase9-docs-sync`; require local HEAD equals origin SHA.

- [ ] **Step 5: Print exact approval safely**

Invoke runner with empty approval and run id `spain-fresh-20260720-004`.
Expected: one literal approval line and exit before private state/SSH.
