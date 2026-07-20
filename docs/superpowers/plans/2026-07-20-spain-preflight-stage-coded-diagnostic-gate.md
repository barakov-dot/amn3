# Spain Preflight Stage-Coded Diagnostic Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a checksum-bound, read-only Spain preflight failure channel that records only an allowlisted stage and exit code, never raw SSH stderr or private target data.

**Architecture:** The Bash probe keeps its existing success JSON but installs an `ERR` handler that emits one fixed stage-coded envelope on failure. The PowerShell runner validates that envelope against a closed allowlist and the actual SSH exit code, then atomically writes either the existing success evidence or one sanitized failure receipt under a single-use private outcome claim. No live run is part of implementation.

**Tech Stack:** Bash 4+, Windows PowerShell 5.1, Windows OpenSSH, Python 3 `unittest`/`pytest`, Git, Codex Security diff scan.

## Global Constraints

- AMN2 source binding remains exactly `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
- Remote probe remains `set -Eeuo pipefail` and read-only.
- SSH uses absolute trusted Windows OpenSSH, `-F none`, dedicated Ed25519 identity, independent host pin, and strict host-key checking.
- Never persist or print raw stderr, `$BASH_COMMAND`, command output, target address, login, hostname, unit/container names, paths, environment, keys, tokens, configs, Telegram values, or AWG data.
- No install/update/remove, start/stop/restart/enable/disable, remote write, firewall mutation, Docker mutation, systemd mutation, SSH configuration mutation, Telegram action, or AWG mutation.
- A failure envelope is diagnostic only and never counts as successful preflight evidence or authority for remediation/retry/install.
- Every live approval is single-use and must bind exact runner SHA, remote probe SHA, and AMN2 source.
- The diagnostic gate accepts the existing trust directory only as exact run id `spain-fresh-20260720-001`; a nonempty approval with any other run id fails before private artifacts or SSH.
- Do not touch `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` or unrelated working-tree files.
- Implementation follows RED -> GREEN; no production change precedes its failing test.

## File Map

- Modify `scripts/vps/post_release_spain_readonly_preflight_remote.sh`: stage constants, allowlisted failure emitter, ERR trap, and stage transitions.
- Modify `scripts/vps/post_release_spain_readonly_preflight_ssh_runner.ps1`: safe envelope parser, single-use outcome claim, mutually exclusive success/failure receipt flow, and new checksum-bound approval.
- Modify `tests/test_post_release_spain_readonly_preflight.py`: Bash emitter tests, runner parser negatives, claim/no-replace tests, static safety assertions, checksum and approval tests.
- Modify `docs/POST_RELEASE_SPAIN_READONLY_PREFLIGHT_GATE.ru.md`: document stage-coded failure behavior and single-use outcome claim.
- Modify `docs/PROJECT_STATUS_CURRENT.ru.md`: record two consumed fail-closed attempts and local diagnostic-gate readiness only after verification.
- Create `docs/POST_RELEASE_SPAIN_PREFLIGHT_STAGE_DIAGNOSTIC_IMPLEMENTATION_EVIDENCE.ru.md`: sanitized TDD/test/security evidence and new digests; no live result.

---

### Task 1: Implement and verify the complete stage-coded diagnostic gate

**Files:**
- Modify: `scripts/vps/post_release_spain_readonly_preflight_remote.sh:1-238`
- Modify: `scripts/vps/post_release_spain_readonly_preflight_ssh_runner.ps1:1-271`
- Modify: `tests/test_post_release_spain_readonly_preflight.py:1-329`
- Modify: `docs/POST_RELEASE_SPAIN_READONLY_PREFLIGHT_GATE.ru.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Create: `docs/POST_RELEASE_SPAIN_PREFLIGHT_STAGE_DIAGNOSTIC_IMPLEMENTATION_EVIDENCE.ru.md`

**Interfaces:**
- Consumes: exact approval literal, existing Task 7 private binding/key/pin, remote probe bytes over SSH stdin.
- Produces: success schema `amn2.spain-readonly-preflight.v1` or failure schema `amn2.spain-readonly-preflight-failure.v1`, never both.
- Produces: remote envelope `AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=<stage>|exit=<1..255>` only on nonzero remote completion.
- Produces: persistent private claim `preflight-outcome.claim` before SSH and one of `preflight-evidence.json` or `preflight-failure-evidence.json` after SSH.

- [ ] **Step 1: Add RED tests for the Bash failure envelope**

In `tests/test_post_release_spain_readonly_preflight.py`, extend the static test and add a focused behavior test:

```python
FAILURE_STAGES = (
    "bootstrap",
    "os_kernel",
    "capacity",
    "sockets",
    "firewall",
    "ssh_policy",
    "docker_inventory",
    "systemd_inventory",
    "systemd_unit_content",
    "systemd_cgroup_ports",
    "render",
)

def test_remote_failure_envelope_is_allowlisted_and_raw_free(self) -> None:
    source = REMOTE.read_text(encoding="utf-8")
    emitter = extract_bash_function(source, "emit_failure")
    harness = (
        "set -Eeuo pipefail\n"
        + emitter
        + "\nCURRENT_STAGE=firewall\nemit_failure 23\n"
    )
    result = subprocess.run(
        [str(BASH), "-c", harness],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    self.assertEqual(result.returncode, 23)
    self.assertEqual(
        result.stdout.strip(),
        "AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=firewall|exit=23",
    )
    self.assertEqual(result.stderr, "")

    for stage in FAILURE_STAGES:
        self.assertIn(f'CURRENT_STAGE="{stage}"', source)
    self.assertIn("set -Eeuo pipefail", source)
    self.assertIn("trap 'emit_failure \"$?\"' ERR", source)
    self.assertNotIn("$BASH_COMMAND", source)
```

Add a second test that invokes `emit_failure` with an unknown stage and proves it normalizes only to `bootstrap`, never echoes the supplied value. Add static assertions forbidding `2>&1`, `tee`, remote file writes, mutation commands, and raw stderr variables.

- [ ] **Step 2: Run the Bash-envelope tests and observe RED**

Run:

```powershell
python -m pytest -q tests/test_post_release_spain_readonly_preflight.py -k "failure_envelope"
```

Expected: FAIL because `emit_failure`, `CURRENT_STAGE`, and the ERR trap do not exist.

- [ ] **Step 3: Add RED tests for strict PowerShell parsing and outcome exclusivity**

Add tests that extract a planned `Read-SafeFailureEnvelope` function and execute it in isolated Windows PowerShell. The accepted input must be exactly one line, with an allowlisted stage and an exit code equal to the SSH process exit code:

```powershell
$AllowedFailureStages = @(
    'bootstrap','os_kernel','capacity','sockets','firewall','ssh_policy',
    'docker_inventory','systemd_inventory','systemd_unit_content',
    'systemd_cgroup_ports','render'
)
$parsed = Read-SafeFailureEnvelope @(
    'AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=firewall|exit=23'
) 23
if ($parsed.Stage -cne 'firewall' -or $parsed.ExitCode -ne 23) { exit 1 }
```

For each of these inputs, assert that the parser returns `$null`:

```text
unknown stage
exit 0
exit 256
exit different from SSH exit code
additional field
leading/trailing text
duplicate valid envelopes
target-like value
raw nft/ss/systemctl stderr text
```

Extend the atomic-writer harness so `preflight-outcome.claim` is created once and a second create fails without changing its bytes. Add static control-flow assertions that:

```text
the claim is created after approval/checksum/key/pin validation
the claim is created before the SSH process
success writes only preflight-evidence.json
valid remote failure writes only preflight-failure-evidence.json
malformed/duplicate envelope writes neither outcome file
raw SSH stderr remains 2>$null and is never redirected to a file or merged
```

- [ ] **Step 4: Run parser/claim tests and observe RED**

Run:

```powershell
python -m pytest -q tests/test_post_release_spain_readonly_preflight.py -k "safe_failure or outcome_claim or mutually_exclusive"
```

Expected: FAIL because the parser, claim path, and failure receipt flow do not exist.

- [ ] **Step 5: Implement the minimal Bash stage-coded failure emitter**

At the top of `post_release_spain_readonly_preflight_remote.sh`, replace the shell mode line and add exactly this bounded emitter:

```bash
set -Eeuo pipefail

CURRENT_STAGE="bootstrap"

emit_failure() {
    local rc="${1:-1}"
    case "$CURRENT_STAGE" in
        bootstrap|os_kernel|capacity|sockets|firewall|ssh_policy|docker_inventory|systemd_inventory|systemd_unit_content|systemd_cgroup_ports|render) ;;
        *) CURRENT_STAGE="bootstrap" ;;
    esac
    if [[ ! "$rc" =~ ^[0-9]+$ ]] || (( rc < 1 || rc > 255 )); then
        rc=1
    fi
    trap - ERR
    printf 'AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=%s|exit=%s\n' "$CURRENT_STAGE" "$rc"
    exit "$rc"
}

trap 'emit_failure "$?"' ERR
```

Set `CURRENT_STAGE` immediately before each corresponding collector. Within the systemd loop, set `systemd_unit_content` immediately before `systemctl cat`, set `systemd_cgroup_ports` before `ports_for_cgroup`, and restore `systemd_inventory` before the next unit. Set `render` only after every collector has completed and before the first success JSON `printf`.

Do not add command text, line numbers, stderr capture, fallback values, `|| true`, or any remote write.

- [ ] **Step 6: Run the Bash-envelope tests and obtain GREEN**

Run:

```powershell
python -m pytest -q tests/test_post_release_spain_readonly_preflight.py -k "failure_envelope"
```

Expected: all selected tests PASS and emitted stderr is empty.

- [ ] **Step 7: Implement the minimal strict PowerShell envelope parser**

In the runner, define the closed allowlist and parser before any private-state read:

```powershell
$AllowedFailureStages = @(
    "bootstrap", "os_kernel", "capacity", "sockets", "firewall",
    "ssh_policy", "docker_inventory", "systemd_inventory",
    "systemd_unit_content", "systemd_cgroup_ports", "render"
)

function Read-SafeFailureEnvelope([string[]]$Lines, [int]$ProcessExitCode) {
    if ($ProcessExitCode -lt 1 -or $ProcessExitCode -gt 255) { return $null }
    $Pattern = '^AMN2_SPAIN_PREFLIGHT_FAILURE_V1\|stage=(?<stage>[a-z_]+)\|exit=(?<exit>[0-9]{1,3})$'
    $Matches = @($Lines | Where-Object { $_ -cmatch $Pattern })
    if ($Matches.Count -ne 1) { return $null }
    $Parsed = [regex]::Match($Matches[0], $Pattern)
    $Stage = $Parsed.Groups["stage"].Value
    $ExitCode = [int]$Parsed.Groups["exit"].Value
    if ($AllowedFailureStages -cnotcontains $Stage) { return $null }
    if ($ExitCode -ne $ProcessExitCode) { return $null }
    return [pscustomobject]@{ Stage = $Stage; ExitCode = $ExitCode }
}
```

The parser must not accept partial matches, extra fields, multiple envelopes, unknown stages, or a mismatch between envelope and OpenSSH exit code.

- [ ] **Step 8: Implement the single-use claim and mutually exclusive outcome flow**

Add private paths beside the existing success evidence path:

```powershell
$FailureEvidencePath = Join-Path $RunRoot "preflight-failure-evidence.json"
$OutcomeClaimPath = Join-Path $RunRoot "preflight-outcome.claim"
```

For a nonempty approval, require `$RunId` to equal
`spain-fresh-20260720-001` by ordinal comparison before `Read-Binding`. Keep the
empty-approval preview before this check so it can print the new literal without
private-state access. Add `TRUST_RUN_ID_SPAIN_FRESH_20260720_001` to the exact
approval literal. A test must prove that the exact approval combined with any
other run id fails before `target.env`, outcome claim creation, or SSH.

After `Assert-DedicatedKeyPair` and `Assert-VerifiedHostPin`, but before `& $SshExe`, atomically create and protect a claim containing only public digests and the source revision:

```powershell
$ClaimJson = [ordered]@{
    schema = "amn2.spain-readonly-preflight-claim.v1"
    runner_sha256 = $actualRunnerSha
    remote_probe_sha256 = $expectedRemoteScriptSha
    source_revision = "55dc243b8e6c6bdb57f8301b56326e4cd4072d19"
} | ConvertTo-Json -Compress
Write-EvidenceCreateNew $OutcomeClaimPath $ClaimJson
Protect-PrivatePath $OutcomeClaimPath
Assert-PrivatePath $OutcomeClaimPath
```

Immediately after SSH, store `$ProcessExitCode = $LASTEXITCODE`. On nonzero completion:

```powershell
$SafeFailure = Read-SafeFailureEnvelope ([string[]]$SshOutput) $ProcessExitCode
if ($null -ne $SafeFailure) {
    $FailureJson = [ordered]@{
        schema = "amn2.spain-readonly-preflight-failure.v1"
        classification = "remote_probe"
        stage = $SafeFailure.Stage
        exit_code = $SafeFailure.ExitCode
        runner_sha256 = $actualRunnerSha
        remote_probe_sha256 = $expectedRemoteScriptSha
        source_revision = "55dc243b8e6c6bdb57f8301b56326e4cd4072d19"
    } | ConvertTo-Json -Compress
    $SshOutput = $null
    $RemoteText = $null
    Write-EvidenceCreateNew $FailureEvidencePath $FailureJson
    Protect-PrivatePath $FailureEvidencePath
    Assert-PrivatePath $FailureEvidencePath
    throw "Read-only Spain preflight failed at a sanitized remote stage; failure evidence created."
}
```

If no exact envelope exists and the SSH exit code is valid, create the same schema with `classification="transport"` and `stage="unavailable"`. If output contains a malformed or duplicate string beginning with `AMN2_SPAIN_PREFLIGHT_FAILURE_V1`, clear buffers and fail without an outcome receipt. Never include the rejected bytes in an exception.

On exit code `0`, preserve the existing strict success JSON validation and create only `preflight-evidence.json`. The persistent claim prevents a second process or reused approval from reaching SSH and makes the success/failure branches mutually exclusive for a run directory.

- [ ] **Step 9: Run parser/claim tests and obtain GREEN**

Run:

```powershell
python -m pytest -q tests/test_post_release_spain_readonly_preflight.py -k "safe_failure or outcome_claim or mutually_exclusive"
```

Expected: all selected tests PASS; second claim creation fails and original bytes remain unchanged.

- [ ] **Step 10: Rebind the runner to exact remote bytes and update approval tests**

Compute the exact SHA-256 of the modified Bash file and replace only `$expectedRemoteScriptSha` in the runner. Update the empty-approval test to derive both hashes from exact bytes, retain source `55DC243B8E6C6BDB57F8301B56326E4CD4072D19`, and include `TRUST_RUN_ID_SPAIN_FRESH_20260720_001`.

Run:

```powershell
python -m pytest -q tests/test_post_release_spain_readonly_preflight.py
```

Expected: all Spain preflight tests PASS. No SSH connection occurs because test approvals are missing or empty.

- [ ] **Step 11: Run parse, focused, and full regression verification**

Run:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' -n scripts/vps/post_release_spain_readonly_preflight_remote.sh
python -m pytest -q tests/test_post_release_spain_readonly_preflight.py
python -m pytest -q tests
```

Parse the runner with `System.Management.Automation.Language.Parser::ParseFile` and require zero errors. Expected: Bash/PowerShell parse PASS, focused suite PASS, and the root `tests/` suite PASS. Do not run bare `pytest` because archived private artifacts and worktrees contain duplicate test module names.

- [ ] **Step 12: Run diff, secret, and security review before documentation sync**

Run `git diff --check`, review every changed line, and scan added lines for private keys, target IP/login, host-key lines, config payloads, tokens, passwords, and raw stderr samples. Expected matches: zero private literals.

Invoke `codex-security:security-diff-scan` over exactly:

```text
scripts/vps/post_release_spain_readonly_preflight_remote.sh
scripts/vps/post_release_spain_readonly_preflight_ssh_runner.ps1
tests/test_post_release_spain_readonly_preflight.py
```

Require full-file receipts, complete coverage, no deferred surfaces, and zero reportable findings before proceeding. If a finding survives validation, stop and fix it through a separate TDD cycle before documentation or commit.

- [ ] **Step 13: Synchronize runbook, status, and implementation evidence**

Update the three documentation files from the File Map with:

```text
two prior approvals consumed fail-closed
no trusted preflight evidence exists
stage-coded diagnostic implementation is local-only and not run
exact new runner/probe SHA-256 values
focused/full test counts
security scan id, coverage, and finding count
AWG, Telegram, Spain unrelated service, and USA production unchanged
next action is a separate exact diagnostic live approval
```

Do not include private target data or claim/failure receipt contents because no new live run has occurred. Keep Phase 11 status `completed-controlled-private-release`; this is post-release controlled operations.

- [ ] **Step 14: Re-run final verification after documentation sync**

Run:

```powershell
python -m pytest -q tests/test_post_release_spain_readonly_preflight.py
python -m pytest -q tests
git diff --check
```

Repeat Bash/PowerShell parse and added-line secret scan. Expected: all results remain green and `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` remains untracked/untouched.

- [ ] **Step 15: Commit only the reviewed implementation scope**

Stage exactly the six files in the File Map. Verify `git diff --cached --name-only` contains no unrelated file, then run `git diff --cached --check`.

Commit:

```powershell
git commit -m "Add Spain preflight failure diagnostics"
```

Expected: one commit containing code, tests, runbook, status, and sanitized implementation evidence.

- [ ] **Step 16: Push, verify origin, and preview the next exact approval locally**

Push `codex-spark-phase9-docs-sync`, compare local `HEAD` with `git ls-remote --heads origin codex-spark-phase9-docs-sync`, and require exact equality.

Invoke the runner with `-Approval ''` and an approval-preview run id. Expected: it prints one fully materialized approval and fails before private artifacts or SSH. The phrase must bind the new runner SHA, new remote probe SHA, and source `55dc243...`.

Stop after presenting that phrase. Do not run Spain SSH, diagnostic preflight, install, remediation, Telegram, or AWG actions without the operator returning the new exact literal.

---

## Implementation Completion Gate

The local implementation is complete only when every checkbox above is satisfied, all verification evidence is fresh, security coverage is complete with zero reportable findings, the exact commit is present in trusted origin, and no live Spain contact occurred during implementation.
