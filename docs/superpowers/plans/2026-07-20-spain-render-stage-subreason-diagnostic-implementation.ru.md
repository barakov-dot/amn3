# Spain render-stage subreason diagnostic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Безопасно различать отсутствие allowlisted render dependencies в новом Spain preflight outcome без раскрытия удалённых данных.

**Architecture:** Bash probe выполняет dependency checks непосредственно до render. PowerShell runner сопоставляет ровно шесть `render/exit` пар с нейтральными subreason и сохраняет только уже разрешённый failure envelope. Новый checksum-bound runner использует outcome `spain-fresh-20260720-006`.

**Tech Stack:** Bash, PowerShell, Python unittest/pytest, Git.

## Global Constraints

- Только локальные code/docs/tests до отдельного literal approval.
- No SSH/VPS install/restart/stop/config/secret/Telegram/AWG mutation.
- Allowlist: `81=sha256sum`, `82=cut`, `83=tr`, `84=awk`, `85=sort`, `86=paste`.
- Do not modify `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` or unrelated untracked files.

---

### Task 1: RED contract tests

**Files:**
- Modify: `tests/test_post_release_spain_readonly_preflight.py`

- [ ] **Step 1: Add exact failing assertions**

```python
for code, reason in enumerate(
    ("sha256sum", "cut", "tr", "awk", "sort", "paste"), start=81
):
    self.assertIn(f'{code} = "{reason}"', parser)
```

- [ ] **Step 2: Run focused test and verify RED**

Run: `python -m pytest tests/test_post_release_spain_readonly_preflight.py -q`
Expected: FAIL because the runner lacks the six `render/exit` mappings.

### Task 2: Minimal Bash and PowerShell implementation

**Files:**
- Modify: `scripts/vps/post_release_spain_readonly_preflight_remote.sh`
- Modify: `scripts/vps/post_release_spain_readonly_preflight_ssh_runner.ps1`

- [ ] **Step 1: Add Bash check helper and exact render checks**

```bash
assert_render_dependency() {
    command -v "$1" >/dev/null 2>&1 || emit_failure "$2"
}
```

Call it for the six global dependency/code pairs immediately after
`CURRENT_STAGE="render"` and before the first JSON `printf`.

- [ ] **Step 2: Map exact pairs in runner**

```powershell
if ($Stage -ceq "render") {
    $RenderSubreasons = @{ 81 = "sha256sum"; 82 = "cut"; 83 = "tr"; 84 = "awk"; 85 = "sort"; 86 = "paste" }
    if (-not $RenderSubreasons.ContainsKey($ExitCode)) { return $null }
    $Subreason = $RenderSubreasons[$ExitCode]
}
```

- [ ] **Step 3: Advance only new outcome binding**

Set `$expectedRunId` and approval literal fields to `spain-fresh-20260720-006`.
Do not change immutable trust run id or source revision.

### Task 3: GREEN tests, docs, verification and handoff

**Files:**
- Modify: `tests/test_post_release_spain_readonly_preflight.py`
- Modify: `docs/POST_RELEASE_SPAIN_READONLY_PREFLIGHT_GATE.ru.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`
- Create: `docs/POST_RELEASE_SPAIN_PREFLIGHT_006_APPROVAL.ru.md`

- [ ] **Step 1: Run focused and full test suites**

Run: `python -m pytest tests/test_post_release_spain_readonly_preflight.py -q` then `python -m pytest tests -q`.
Expected: all pass.

- [ ] **Step 2: Update status without recording run 006 as executed**

Record local implementation/verification and state `006=not_run|approval_required`.

- [ ] **Step 3: Verify, review, commit and push**

Run `git diff --check`, staged secret scan, security diff review, commit, push,
and origin readback. Calculate fresh script/runner SHA-256, then write the
separate exact single-use approval. Do not run it.
