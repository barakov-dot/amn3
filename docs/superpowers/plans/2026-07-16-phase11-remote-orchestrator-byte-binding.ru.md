# Phase 11 Remote Orchestrator Same-Bytes Binding and Trusted Transport Hardening Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Закрыть Medium/P2 `transport-unbound-remote-orchestrator`, закрепив exact reviewed SHA-256 над тем же `byte[]`, который передаётся production root Bash.

**Architecture:** Non-upload path один раз читает remote orchestrator через `ReadAllBytes`, вычисляет SHA-256 и ordinally сравнивает его с reviewed constant. `Invoke-CapturedProcess` принимает этот же `byte[]` и пишет его в redirected stdin через `BaseStream`, исключая повторное чтение и encoding drift. Все локальные SSH/SCP вызовы используют только абсолютные бинарники из `%WINDIR%\System32\OpenSSH`; helper fail-closed отвергает любые иные пути.

**Tech Stack:** PowerShell/.NET cryptography and process APIs, Python `unittest`/pytest static contract tests, Git diff/security scan tooling.

## Global Constraints

- Exact remote SHA: `A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72`.
- Exact approval, package SHA, pinned SSH host/key, output sanitization и allowed modes не ослабляются.
- `upload` сохраняет package-only семантику; script binding применяется к `preflight`, `postflight`, `apply` до SSH transport.
- Regular bot остаётся disabled, Telegram profile unchanged, AWG untouched.
- Не выполнять live SSH/VPS/provider/service/database/Telegram/AWG actions.
- Не изменять `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`.

---

### Task 1: Encode the byte-binding security invariant

**Files:**
- Modify: `tests/test_phase11_0b858c5_rollout_executor.py`
- Test: `tests/test_phase11_0b858c5_rollout_executor.py`

**Interfaces:**
- Consumes: current `REMOTE` and `RUNNER` paths.
- Produces: static contract for `$expectedRemoteScriptSha`, `$remoteScriptBytes`, ordinal digest comparison and byte-oriented stdin.

- [x] **Step 1: Write the failing digest-binding test**

```python
import hashlib

def test_runner_binds_remote_executor_bytes_to_reviewed_sha(self) -> None:
    script = RUNNER.read_text(encoding="utf-8")
    remote_sha = hashlib.sha256(REMOTE.read_bytes()).hexdigest().upper()
    expected = f'$expectedRemoteScriptSha = "{remote_sha}"'
    equality = (
        "[string]::Equals($actualRemoteScriptSha, $expectedRemoteScriptSha, "
        "[StringComparison]::Ordinal)"
    )
    self.assertIn(expected, script)
    self.assertIn("[IO.File]::ReadAllBytes($remoteScript)", script)
    self.assertIn("ComputeHash($remoteScriptBytes)", script)
    self.assertIn(equality, script)
    self.assertLess(script.index(equality), script.index("$sshArgs ="))
```

- [x] **Step 2: Write the failing same-byte-array transport test**

```python
def test_runner_hashes_and_transmits_the_same_byte_array(self) -> None:
    script = RUNNER.read_text(encoding="utf-8")
    self.assertEqual(script.count("[IO.File]::ReadAllBytes($remoteScript)"), 1)
    self.assertIn("[byte[]]$StandardInputBytes = @()", script)
    self.assertIn(
        "$process.StandardInput.BaseStream.Write("
        "$StandardInputBytes, 0, $StandardInputBytes.Length)",
        script,
    )
    self.assertIn("-StandardInputBytes $remoteScriptBytes", script)
    self.assertNotIn("Get-Content -LiteralPath $remoteScript -Raw", script)
    self.assertNotIn("StandardInputText", script)
```

- [x] **Step 3: Run RED**

Run: `python -m pytest tests/test_phase11_0b858c5_rollout_executor.py -q`

Expected: two new failures because digest binding and byte-oriented stdin do not yet exist; the five prior tests remain passing.

---

### Task 2: Implement one-read SHA admission and byte transport

**Files:**
- Modify: `scripts/vps/phase11_0b858c5_combined_ssh_runner.ps1:16-125`
- Test: `tests/test_phase11_0b858c5_rollout_executor.py`

**Interfaces:**
- Consumes: `$remoteScript`, reviewed SHA constant and existing `Invoke-CapturedProcess` calls.
- Produces: optional `[byte[]]$StandardInputBytes`, exact digest guard and verified byte delivery.

- [x] **Step 1: Replace text stdin with byte stdin**

```powershell
function Invoke-CapturedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$FileName,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [byte[]]$StandardInputBytes = @()
    )

    # existing ProcessStartInfo setup remains unchanged
    $process = [System.Diagnostics.Process]::Start($startInfo)
    if ($StandardInputBytes.Length -gt 0) {
        $process.StandardInput.BaseStream.Write(
            $StandardInputBytes, 0, $StandardInputBytes.Length
        )
        $process.StandardInput.BaseStream.Flush()
    }
    $process.StandardInput.Close()
    # existing stdout/stderr/exit handling remains unchanged
}
```

- [x] **Step 2: Add the reviewed same-bytes digest guard**

```powershell
$expectedRemoteScriptSha = "A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72"

$remoteScriptBytes = [IO.File]::ReadAllBytes($remoteScript)
$sha256 = [Security.Cryptography.SHA256]::Create()
try {
    $actualRemoteScriptSha = (
        [BitConverter]::ToString($sha256.ComputeHash($remoteScriptBytes))
    ).Replace("-", "")
} finally {
    $sha256.Dispose()
}
if (-not [string]::Equals(
    $actualRemoteScriptSha,
    $expectedRemoteScriptSha,
    [StringComparison]::Ordinal
)) {
    throw "Remote rollout script SHA-256 mismatch"
}
```

- [x] **Step 3: Send the verified object**

```powershell
Invoke-CapturedProcess `
    -FileName $sshExecutable `
    -Arguments $sshArgs `
    -StandardInputBytes $remoteScriptBytes
```

- [x] **Step 4: Run GREEN**

Run: `python -m pytest tests/test_phase11_0b858c5_rollout_executor.py -q`

Expected: all nine tests pass, including absolute/trusted OpenSSH path guards.

- [x] **Step 5: Bind every local transport call to the trusted OpenSSH installation**

The runner derives `$sshExecutable` and `$scpExecutable` from the absolute
system OpenSSH directory, checks both regular files before transport, and
rejects non-absolute or outside-root paths inside `Invoke-CapturedProcess`.

---

### Task 3: Verify closure and preserved behavior

**Files:**
- Verify: `scripts/vps/phase11_0b858c5_combined_ssh_runner.ps1`
- Verify: `scripts/vps/phase11_0b858c5_combined_remote_rollout.sh`
- Verify: `tests/test_phase11_0b858c5_rollout_executor.py`

**Interfaces:**
- Consumes: completed source/test patch.
- Produces: syntax, behavior, PoC and security closure receipts.

- [x] **Step 1: Run scoped and full tests**

Run: `python -m pytest tests/test_phase11_0b858c5_rollout_executor.py -q`

Run the repository-supported full test suite discovered from project metadata.

- [x] **Step 2: Run syntax and diff checks**

Run PowerShell parser validation for the runner, Git Bash `bash -n` for the remote executor, and `git diff --check` plus staged/unstaged scope inspection.

- [x] **Step 3: Re-run security closure**

Verify the current remote SHA equals the runner constant, no path reread exists, and the hashed array is the transported array. Repeat the scoped Codex Security diff scan and save a fix report under the existing scan bundle.

Expected: the original P2 source/control/sink path is suppressed with exact counterevidence and no new reportable candidate.

---

### Task 4: Sync Phase 11 evidence and publish

**Files:**
- Modify: `research/amn2/phase-11-0b858c5-combined-overlay-rollout-gate-review-2026-07-16.md`
- Modify: `docs/superpowers/plans/2026-07-16-phase11-0b858c5-combined-overlay-live-rollout.ru.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`
- Create: `research/amn2/phase-11-remote-orchestrator-byte-binding-fix-2026-07-16.md`

**Interfaces:**
- Consumes: final runner/remote hashes, tests and security receipts.
- Produces: current gate state, fresh non-reusable approval boundary and origin-synced commit.

- [x] **Step 1: Record exact evidence**

Update runner SHA, unchanged remote SHA, nine-test receipt, syntax/diff results, security disposition and explicit `live rollout not run` status. Do not edit the client release monitor baseline.

- [ ] **Step 2: Prepare a fresh approval gate**

Create a new exact phrase that includes the fixed runner identity and states bot disabled, Telegram profile unchanged and AWG untouched. Mark the previous approval as non-consumable; do not run upload/apply.

- [ ] **Step 3: Final review, commit and push**

Run final tests, `git diff --check`, secret/security scan and status review. Stage only intended Phase 11 files, commit with `Fix Phase 11 orchestrator byte binding`, push `codex-spark-phase9-docs-sync`, fetch/compare the remote branch SHA, and report the new exact approval phrase for a later user message.
