# AMN2 Phase 11 Final Closeout and Controlled Private Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Закрыть `PHASE11-RELEASE-001` доказательным closeout packet, синхронизировать authoritative Phase 11 status и объявить controlled private release только после зелёных verification, security, commit, push и origin-readback gates.

**Architecture:** Изменения ограничены документацией и evidence: live VPS, Telegram runtime, provider, database, web и AWG не изменяются. Canonical packet агрегирует уже полученные Phase 11 product/operations receipts, явно отделяет release blockers от условных safety holds и переносит P1–P3 в post-release roadmap без расширения private/operator-only surface.

**Tech Stack:** Markdown contracts/evidence, Python `pytest`, `scripts/phase9_progress_harness.py`, Git, Codex Security diff scan.

## Global Constraints

- Phase 10 закрыта; её rollout и acceptance не повторять.
- Authoritative AMN2 source и production overlay: `0b858c5cdbc5b565cc265966a2edfe2d339d65e0`.
- AMN3/docs branch: `codex-spark-phase9-docs-sync`.
- Не останавливать и не изменять AWG; не повторять Telegram `/start`, cleanup, stage, accept или rollout.
- Не выполнять live VPS/SSH, Telegram API, provider, database, web или config/peer mutations.
- Не трогать `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`.
- Private/operator-only boundaries остаются закрытыми: public API/web/config delivery, config/peer generation, write gates и self-service enrollment не открываются.
- Old recovery fallback хранится sealed без open/copy/move/delete до review не позднее `2026-08-01`.
- Second VPS audit выполняется только перед фактическим пользовательским repurpose и не блокирует текущий private release.
- Каждый итоговый документ должен ясно указывать: `PHASE11-RELEASE-001` прошёл только после tests, security review, commit, push и trusted-origin readback.

---

### Task 1: Final closeout packet and evidence

**Files:**
- Create: `docs/AMN2_PHASE_11_FINAL_CLOSEOUT_PACKET.ru.md`
- Create: `research/amn2/phase-11-final-closeout-controlled-private-release-2026-07-18.md`

**Interfaces:**
- Consumes: Phase 11 status/evidence at AMN3 commit `24dde6e`, AMN2 source/overlay `0b858c5`, TELEGRAM-002B run `20260717T192602Z`, 66m13s stability receipt, recovery and second-VPS decisions.
- Produces: canonical closeout decision, invariant matrix, non-blocking holds, post-release roadmap and exact release declaration contract.

- [ ] **Step 1: Write the closeout decision and immutable baselines**

Record `phase11_status=completed-controlled-private-release`, source/overlay pins, private/operator-only boundaries, bot/web/database/AWG health receipts and prohibited repeat actions.

- [ ] **Step 2: Record release-blocker reconciliation**

Prove P0 rollout, restore, recovery decision, branding, transient Telegram smoke, persistent activation and stability gates are closed. Classify second-VPS handover and dated fallback review as conditional safety work, not launch blockers.

- [ ] **Step 3: Record verification and release declaration prerequisites**

Use the non-self-referential receipt `closeout_commit=this_commit` inside the commit and record the resolved SHA in the final operator result after origin readback; state that the declaration is invalid if tests, security coverage, branch integrity or origin synchronization fail.

- [ ] **Step 4: Write the evidence ledger**

Create the research receipt with the same facts, commands/results and no-live-mutation scope.

### Task 2: Authoritative status and handoff synchronization

**Files:**
- Modify: `docs/AMN2_PHASE_11_FIRST_MESSAGE.ru.md`
- Modify: `docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md`
- Modify: `docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`

**Interfaces:**
- Consumes: canonical packet and evidence from Task 1.
- Produces: one consistent top-level status stating that controlled private release is declared only after final origin readback, with conditional holds and post-release roadmap preserved.

- [ ] **Step 1: Add current closeout overrides**

Place new 2026-07-18 control blocks above historical state. Do not rewrite historical evidence.

- [ ] **Step 2: Close the current release recommendation**

Replace `PHASE11-RELEASE-001` as an open blocker with `completed-pass` and make the next recommendation a post-release observation/roadmap review that carries no live authority.

- [ ] **Step 3: Preserve mandatory recommendation tiers**

Keep `Одиночная`, `Двойная`, `Тройная`, `Четверная`, and `Более — рекомендовано`; every chain starts with `GPT-5.6 SOL` and does not authorize second-VPS mutation or fallback deletion.

### Task 3: Verification, security review, commit and trusted-origin readback

**Files:**
- Test: `tests/test_phase9_progress_harness.py`
- Test: `tests/`
- Review: all files changed by Tasks 1–2.

**Interfaces:**
- Consumes: complete documentation diff.
- Produces: fresh test receipts, complete security-diff artifact set, clean staged diff, trusted commit and exact origin readback.

- [ ] **Step 1: Run progress harness and scoped tests**

Run `python scripts/phase9_progress_harness.py --help` to confirm the interface, then execute its applicable Phase 11 validation mode and `python -m pytest tests/test_phase9_progress_harness.py -q`.

- [ ] **Step 2: Run the full root suite**

Run `python -m pytest tests -q`; require exit `0` and zero failures.

- [ ] **Step 3: Run diff and secret checks**

Run `git diff --check`, verify the forbidden baseline is absent from the diff, ensure no current replayable approval/rollout chain remains, and scan changed files for high-confidence secret patterns.

- [ ] **Step 4: Run canonical Codex Security diff review**

Resolve the exact working-tree diff, cover every changed file with a receipt, validate any candidate, finalize canonical JSON and generated report, and require zero reportable findings or remediate and rerun.

- [ ] **Step 5: Commit only intended files**

Stage the plan, packet, evidence and five status contracts only. Run staged name/stat/check review, then bind the index bytes to sealed scan
`24dde6e9d49c565a4beebe47ac91fddb79b990e9_20260718T050216Z` with the exact
check below. Its digest algorithm is identical to the scan snapshot algorithm:
sorted repository-relative path, NUL, byte length, NUL, SHA-256, newline.

```powershell
$scanManifest = 'C:\Users\SooL\AppData\Local\Temp\codex-security-scans\VPS-OPS-LAB\24dde6e9d49c565a4beebe47ac91fddb79b990e9_20260718T050216Z\scan-manifest.json'
$expected = (Get-Content -LiteralPath $scanManifest -Raw | ConvertFrom-Json).scan.target.snapshotDigest
$digestScript = @'
import hashlib, subprocess, sys
source = sys.argv[1]
paths = [
    "docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md",
    "docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md",
    "docs/AMN2_PHASE_11_FINAL_CLOSEOUT_PACKET.ru.md",
    "docs/AMN2_PHASE_11_FIRST_MESSAGE.ru.md",
    "docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md",
    "docs/PROJECT_STATUS_CURRENT.ru.md",
    "docs/superpowers/plans/2026-07-18-phase11-final-closeout-controlled-private-release.ru.md",
    "research/amn2/phase-11-final-closeout-controlled-private-release-2026-07-18.md",
]
h = hashlib.sha256()
for path in sorted(paths):
    spec = f":{path}" if source == "index" else f"HEAD:{path}"
    data = subprocess.check_output(["git", "show", spec])
    sha = hashlib.sha256(data).hexdigest()
    h.update(path.encode()); h.update(b"\0"); h.update(str(len(data)).encode())
    h.update(b"\0"); h.update(sha.encode()); h.update(b"\n")
print("codex-security-snapshot/v1:sha256:" + h.hexdigest())
'@
$indexDigest = ($digestScript | python - index).Trim()
if ($indexDigest -ne $expected) { throw "security snapshot/index mismatch; rescan required" }
git commit -m "Close Phase 11 controlled private release"
$commitDigest = ($digestScript | python - commit).Trim()
if ($commitDigest -ne $expected) { throw "security snapshot/commit mismatch; do not push" }
```

No `git add` is allowed after `$indexDigest` passes. Any intended-path edit or
index mutation requires a complete rescan and a new binding receipt before
commit/push.

- [ ] **Step 6: Push and verify trusted origin**

Push `codex-spark-phase9-docs-sync`, fetch/read back the remote ref and require local SHA equals origin SHA. Record the final SHA in the closeout result; if the packet used a symbolic `closeout_commit=this_commit` receipt, do not create an infinite self-referential hash cycle.

- [ ] **Step 7: Declare controlled private release**

Only after Step 6 passes, report `AMN2_PHASE11_CONTROLLED_PRIVATE_RELEASE=DECLARED`. Preserve conditional second-VPS and recovery holds and keep all public/write surfaces closed.
