# POST-RELEASE-API-001 Current-Overlay Acceptance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and locally verify a checksum-bound gate that accepts the existing private scoped API on production overlay `0b858c5` by running a transient loopback server against a private SQLite clone, without executing the live gate.

**Architecture:** A streamed Bash executor owns preflight, clone creation, transient API lifecycle, bounded watchdog, smoke assertions, cleanup, and independent postflight. A PowerShell runner binds exact reviewed bytes to trusted OpenSSH and a single-use literal approval. Static TDD tests prove the fail-closed contract without SSH or network access.

**Tech Stack:** Bash, PowerShell 7/Windows PowerShell, Python 3.12, pytest, SQLite backup API, existing AMN2 CLI/FastAPI smoke cycle, Git.

## Global Constraints

- Canonical design: AMN2 commits `3a3af86b70c21c0e5c4883839bb95d523cc242fb` and `8b28903`.
- Written approval: `APPROVE_WRITTEN_API_001_SPEC_3A3AF86`.
- Production source remains `0b858c5cdbc5b565cc265966a2edfe2d339d65e0`.
- This plan authorizes local files, tests, review, commits, pushes, and origin readback only; it authorizes no SSH or live mode.
- Never stop, restart, reconfigure, or test AWG.
- Never mutate production DB, bot, web, Telegram, provider, peer, config, or public exposure.
- Keep `VPS_APPLY_ENABLED=false` and `OPERATOR_DEVICE_CREATE_ENABLED=false`.
- Do not touch or stage `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`.
- Do not repeat Phase 10 or Phase 11 rollout, `/start`, cleanup, stage, accept, restore, or Telegram actions.
- Raw bearer token, Authorization header, token hash, SSH target, config, private key, and PSK must not enter logs or evidence.

---

### Task 1: RED static contract tests

**Files:**
- Create: `tests/test_post_release_api_001_executor.py`
- Produces: executable specification for both operational files.

**Interfaces:**
- Consumes: the approved RU/EN design in AMN2 commit `8b28903`.
- Produces: pytest assertions over `scripts/vps/post_release_api_001_remote.sh` and `scripts/vps/post_release_api_001_ssh_runner.ps1`.

- [ ] **Step 1: Write tests before operational files exist**

The test module must read the two expected paths and assert these independent groups:

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REMOTE = ROOT / "scripts/vps/post_release_api_001_remote.sh"
RUNNER = ROOT / "scripts/vps/post_release_api_001_ssh_runner.ps1"

def _read(path: Path) -> str:
    assert path.is_file(), f"required executor missing: {path.name}"
    return path.read_text(encoding="utf-8")

def test_remote_executor_has_only_preflight_and_run_modes():
    remote = _read(REMOTE)
    assert '"preflight"|"run"' in remote
    assert 'MODE="${1:-}"' in remote

def test_clone_uses_read_only_source_and_never_initializes_production_schema():
    remote = _read(REMOTE)
    assert '?mode=ro' in remote
    assert 'source.backup(destination)' in remote
    assert 'initialize_schema' not in remote

def test_transient_api_is_exact_ipv4_loopback_with_cleanup_and_watchdog():
    remote = _read(REMOTE)
    assert '--host 127.0.0.1 --port 3040' in remote
    assert 'RUN_TTL_SECONDS="180"' in remote
    assert remote.index('trap mandatory_cleanup') < remote.index('api serve')

def test_runner_uses_exact_single_use_trusted_transport():
    runner = _read(RUNNER)
    assert 'System32\\OpenSSH' in runner
    assert '[IO.FileMode]::CreateNew' in runner
    assert 'ComputeHash($remoteScriptBytes)' in runner
```

The completed module expands these seed tests into separate source-hash,
six-route/audit, postflight-invariant, exact-approval, safe-output, and
forbidden-operation tests. Each test names every required literal or ordering
relationship; it does not use broad snapshot approval.

Tests must reject public modes beyond `preflight|run`, production DB being
passed to `api serve`, any `install:write`/POST invocation, service mutation,
Docker mutation, Telegram call, AWG mutation, wildcard bind, or raw secret
output.

- [ ] **Step 2: Run RED and preserve the expected failure**

Run:

```powershell
python -m pytest tests/test_post_release_api_001_executor.py -q
```

Expected: failure because both operational files do not exist. An import or
syntax error is not an acceptable RED result.

---

### Task 2: GREEN remote fail-closed executor

**Files:**
- Create: `scripts/vps/post_release_api_001_remote.sh`
- Test: `tests/test_post_release_api_001_executor.py`

**Interfaces:**
- Consumes: mode argument `preflight` or `run` only.
- Produces: redacted key/value receipts and exit status; no secret output.

- [ ] **Step 1: Add strict shell frame and fixed constants**

The script begins with:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

MODE="${1:-}"
AMN2_DIR=/opt/amn2
DB_PATH="$AMN2_DIR/data/amneziya.sqlite3"
OVERLAY_MARKER="$AMN2_DIR/.amn2_source_overlay_commit"
PYTHON_BIN="$AMN2_DIR/venv/bin/python"
STATE_BASE=/root/amn2-post-release-api-001
BOT_UNIT=amneziya-bot.service
WEB_UNIT=amneziya-web.service
AWG_CONTAINER=amnezia-awg2
AWG_INTERFACE=awg0
EXPECTED_OVERLAY=0b858c5
RUN_TTL_SECONDS=180
```

Reject every mode except `preflight` and `run` with one generic
`api_001_gate=failed reason=gate_rejected` error.

- [ ] **Step 2: Bind the exact production source contract**

Add fixed uppercase SHA-256 constants for:

```text
app/cli.py
app/api/app.py
app/config/settings.py
app/db/schema.py
app/db/repositories.py
app/services/api_tokens.py
app/services/api_smoke.py
```

Compute each constant from AMN2 commit `0b858c5`, require regular non-symlink
files, and compare bytes before any state creation.

- [ ] **Step 3: Implement read-only preflight snapshots**

Named functions must validate tools, `.env` false write gates, production DB
integrity/FK, no listener `3040`, loopback-only healthy web, healthy
single-instance bot, disk capacity, and observation-only AWG snapshots.

AWG snapshot may use only `docker inspect "$AWG_CONTAINER"`,
`docker exec "$AWG_CONTAINER" awg show`,
`docker exec "$AWG_CONTAINER" sha256sum` over fixed existing paths, and
read-only process/interface inspection. The script must contain no Docker
lifecycle verb and no `awg set`/`wg set`.

- [ ] **Step 4: Implement clone-only database lifecycle**

Use inline Python equivalent to:

```python
source = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
destination = sqlite3.connect(clone_path)
with destination:
    source.backup(destination)
```

Create a root-only state directory and clone, run clone integrity/FK checks,
and capture deterministic production fingerprints for `api_tokens` plus only
`admin_actions.action IN ('api_read', 'api_write')`. Never call
`initialize_schema`; never delete or restore a production row.

- [ ] **Step 5: Implement transient API, watchdog, and smoke**

Arm cleanup and signal/error traps before starting a separate process group.
Start the existing API with environment `DATABASE_PATH=$CLONE_PATH` and:

```text
python -m app.cli api serve --host 127.0.0.1 --port 3040
```

Start an independent 180-second watchdog, wait for exactly one IPv4-loopback
listener, then run existing `api smoke-cycle` against the clone with a seven-day
TTL and server name resolved from the clone's existing server registry.

Run explicit missing/invalid bearer `401` and cross-scope `403` checks without
printing tokens. Inspect clone rows to prove one issued/used/revoked lifecycle,
six safe `api_read` route templates, and zero new `api_write` rows.

- [ ] **Step 6: Implement mandatory cleanup and independent postflight**

Cleanup must terminate only the recorded API process group, cancel only the
recorded watchdog, remove clone/PID/output/state, and prove listener/process
absence. Then repeat bot/web/production-DB/AWG snapshots and require equality.
An invariant mismatch fails without remediation.

- [ ] **Step 7: Run focused tests until the remote contract is green**

Run:

```powershell
python -m pytest tests/test_post_release_api_001_executor.py -q
```

Expected at this intermediate point: remote-script tests pass; runner tests
still fail because the PowerShell file does not exist.

---

### Task 3: GREEN checksum-bound trusted runner

**Files:**
- Create: `scripts/vps/post_release_api_001_ssh_runner.ps1`
- Modify: `tests/test_post_release_api_001_executor.py` only if a RED assertion exposed a specification ambiguity; do not weaken a valid test.

**Interfaces:**
- Consumes: `-Mode preflight|run` and optional exact `-Approval` for `run`.
- Produces: redacted remote receipt; a local single-use run receipt.

- [ ] **Step 1: Compute the final remote byte hash**

Run PowerShell SHA-256 over the exact Bash bytes and record the uppercase digest
as `$expectedRemoteScriptSha` in the runner. Recompute it at runtime and reject
mismatch before SSH.

- [ ] **Step 2: Implement trusted transport**

Resolve only `%WINDIR%\System32\OpenSSH\ssh.exe`, dedicated key
`amn2_private_rc_operator_ed25519`, and one-target
`codex_amn2_target_known_hosts`. Use `-F none`, `BatchMode`, `IdentitiesOnly`,
strict host checking, disabled global/command host sources, connection timeout,
and server-alive bounds. Send the already-hashed byte array through stdin to:

```text
bash -s -- preflight
bash -s -- run
```

- [ ] **Step 3: Bind exact authority and single use**

`preflight` rejects any approval. `run` requires ordinal equality with the
literal constructed from the final digest:

```powershell
$expectedApproval = "APPROVE POST_RELEASE_API_001_REMOTE_SHA_${expectedRemoteScriptSha}_SOURCE_0B858C5_TRANSIENT_LOOPBACK_3040_CLONE_DB_SCOPED_TOKEN_TTL_REVOKE_AUDIT_SIX_ROUTE_SMOKE_MANDATORY_CLEANUP_PRODUCTION_BOT_WEB_DB_AND_AWG_UNTOUCHED"
```

Before SSH, `run` creates one `CreateNew` receipt under the existing private
local AMN2 post-release state directory. A repeated run with the same executor
hash is rejected.

- [ ] **Step 4: Run the complete focused suite**

```powershell
python -m pytest tests/test_post_release_api_001_executor.py -q
```

Expected: all focused tests pass and no network process is started.

---

### Task 4: Scoped, full, and static verification

**Files:**
- Verify only; do not create evidence until all commands pass.

**Interfaces:**
- Consumes: final executor, runner, tests, and plan.
- Produces: fresh verification receipts.

- [ ] **Step 1: Run focused and root suites**

```powershell
python -m pytest tests/test_post_release_api_001_executor.py -q
python -m pytest tests -q
```

- [ ] **Step 2: Run diff and forbidden-operation scans**

```powershell
git diff --check
rg -n "sendMessage|sendPhoto|getUpdates|setChat|docker (stop|restart|rm|kill)|awg set|wg set|systemctl (stop|restart|disable|enable)|0\.0\.0\.0:3040|install:write" scripts/vps/post_release_api_001_* tests/test_post_release_api_001_executor.py
```

Every match must be either an explicit static-test forbidden marker or a
fail-closed rejection assertion; operational command paths must contain none.

- [ ] **Step 3: Verify existing protected executor bytes**

Compute SHA-256 for existing Phase 11/group-icon remote executors before and
after this slice and prove no unrelated file changed. Confirm the protected
baseline document is absent from diff and staging.

---

### Task 5: Complete security diff review

**Files:**
- Review Git diff from AMN3 commit `efb532b` through the final local patch.
- Create generated scan artifacts only in the Codex Security scan directory.

**Interfaces:**
- Consumes: exact Git-backed diff and repository threat model.
- Produces: complete coverage ledger, canonical scan JSON, generated report, and zero or explicit validated findings.

- [ ] **Step 1: Run the configured security-diff workflow**

Threat-model the repository, discover candidates over every changed source-like
file, validate each candidate, analyze attack paths when needed, and finalize
the scan contract. Do not claim coverage without a completion receipt for every
diff row.

- [ ] **Step 2: Stop on reportable finding**

If any reportable finding remains, do not write readiness evidence or commit
the executor. Fix only after a separate evidence-backed decision and repeat
tests plus the complete security scan.

---

### Task 6: Evidence, status, commits, pushes, and live stop line

**Files:**
- Create: `research/amn2/post-release-api-001-local-gate-2026-07-18.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Never modify: `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`

**Interfaces:**
- Consumes: fresh test/security receipts and final remote SHA-256.
- Produces: AMN2/AMN3 origin-synced local readiness plus the exact live phrase.

- [ ] **Step 1: Write evidence and top status override**

Record source/design commits, final remote SHA, TDD RED/GREEN counts, focused
and full counts, complete security coverage, and explicit values:

```text
post_release_api_001=local_executor_ready|live_not_run
production_api_3040_listener=unchanged_absent
production_database=not_contacted|unchanged
production_bot_web=not_contacted|unchanged
production_awg=untouched
public_write_config_peer_self_service=closed
```

- [ ] **Step 2: Commit AMN3 intentionally**

Stage only plan, executor, runner, tests, evidence, and status. Run staged
diff/check/security byte-binding verification, then commit.

- [ ] **Step 3: Push and verify both origins**

Push AMN2 `codex-vps-test-prep` and AMN3
`codex-spark-phase9-docs-sync`. Fetch/read back each exact remote ref and require
local SHA equality. Do not include the protected baseline.

- [ ] **Step 4: Emit but do not execute exact live approval**

Construct the final literal phrase from the committed runner's bound SHA. Do
not invoke `preflight` or `run`. Report that the next action requires the user
to send that exact phrase.

## Completion Criteria

```text
written_spec_approval=8b28903
tdd_red_observed=true
focused_tests=pass
root_full_tests=pass
security_diff_coverage=complete
security_reportable_findings=0
amn2_origin_sync=true
amn3_origin_sync=true
live_ssh=false
live_api_listener=false
production_db_bot_web=false
production_awg=untouched
next=SEPARATE_EXACT_LIVE_APPROVAL_ONLY
```
