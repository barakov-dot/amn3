# Phase 11 TELEGRAM-002B Stale Start Single-Update Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a separately approved, checksum-bound one-shot executor that can acknowledge exactly one queued private `/start` from the first configured Telegram administrator without sending a response or changing production DB, web, AWG, Telegram profile, or the existing `2FDB...` activation executor.

**Architecture:** Add a standalone Bash remote executor with `preflight` and `cleanup` modes, a standalone PowerShell SSH runner with an exclusive local cleanup-approval receipt, and static contract tests. The remote executor duplicates only the already-reviewed read-only source/web/bot/DB/AWG checks from the activation gate, performs two identical non-advancing queue inspections, then makes exactly one offset advance past the validated update.

**Tech Stack:** Bash 5, PowerShell 7 parser-compatible syntax, Windows OpenSSH, Python 3.12, aiogram Bot API client, unittest/pytest, Git.

## Global Constraints

- Production source overlay is exactly `0b858c5`; full commit is `0b858c5cdbc5b565cc265966a2edfe2d339d65e0`.
- Expected public bot identity is exactly `@NeobyatnayaAMNZ_bot`; token, proxy, administrator IDs, target and update data remain private.
- `VPS_APPLY_ENABLED=false` and `OPERATOR_DEVICE_CREATE_ENABLED=false` are mandatory.
- Regular Telegram bot must remain inactive, disabled and process-free.
- Only `settings.admin_ids[0]` may own the accepted private exact `/start`.
- The executor may make one and only one advancing `getUpdates(offset=validated_update_id + 1)` call.
- No Telegram response, handler/workflow/dispatcher creation, webhook/profile mutation, production DB write/restore, web service mutation, AWG mutation or provider mutation is allowed.
- Existing `scripts/vps/phase11_telegram_002b_persistent_remote.sh` and `scripts/vps/phase11_telegram_002b_persistent_ssh_runner.ps1` bytes must not change.
- `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` remains untouched and untracked.
- Design approval and spec approval are not live cleanup authority.

---

### Task 1: Lock the standalone cleanup contract with failing tests

**Files:**
- Create: `tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py`
- Reference: `docs/superpowers/specs/2026-07-17-phase11-telegram-002b-stale-start-single-update-cleanup-design.ru.md`

**Interfaces:**
- Consumes: the approved spec at commit `d474ff6`.
- Produces: static tests for `REMOTE`, `RUNNER`, exact execution ordering, prohibited operations, sanitized output and unchanged activation-executor hashes.

- [ ] **Step 1: Record the existing activation bytes before adding cleanup files**

Run:

```powershell
Get-FileHash scripts/vps/phase11_telegram_002b_persistent_remote.sh -Algorithm SHA256
Get-FileHash scripts/vps/phase11_telegram_002b_persistent_ssh_runner.ps1 -Algorithm SHA256
```

Expected:

```text
remote=2FDBAD445F4EBDA4A94BE84CB4FF43D05AE458D68A78686490775B8F242A00E2
runner=75B210410CFE45377857A02FAA43618EE26533259B15AB348693B5292091ED53
```

- [ ] **Step 2: Write the first failing contract test file**

Create the file with these exact path bindings and test groups:

```python
import hashlib
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REMOTE = REPO_ROOT / "scripts" / "vps" / "phase11_telegram_002b_stale_start_cleanup_remote.sh"
RUNNER = REPO_ROOT / "scripts" / "vps" / "phase11_telegram_002b_stale_start_cleanup_ssh_runner.ps1"
ACTIVATION_REMOTE = REPO_ROOT / "scripts" / "vps" / "phase11_telegram_002b_persistent_remote.sh"
ACTIVATION_RUNNER = REPO_ROOT / "scripts" / "vps" / "phase11_telegram_002b_persistent_ssh_runner.ps1"


def read_required(test: unittest.TestCase, path: Path, label: str) -> str:
    test.assertTrue(path.exists(), f"{label} is missing")
    return path.read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Phase11Telegram002bStaleStartCleanupExecutorTests(unittest.TestCase):
    def test_existing_activation_executor_bytes_are_unchanged(self) -> None:
        self.assertEqual(
            sha256(ACTIVATION_REMOTE),
            "2FDBAD445F4EBDA4A94BE84CB4FF43D05AE458D68A78686490775B8F242A00E2",
        )
        self.assertEqual(
            sha256(ACTIVATION_RUNNER),
            "75B210410CFE45377857A02FAA43618EE26533259B15AB348693B5292091ED53",
        )

    def test_remote_binds_source_identity_and_only_two_modes(self) -> None:
        script = read_required(self, REMOTE, "cleanup remote executor")
        for marker in {
            'EXPECTED_OVERLAY="0b858c5"',
            'SOURCE_FULL_COMMIT="0b858c5cdbc5b565cc265966a2edfe2d339d65e0"',
            'EXPECTED_BOT_USERNAME="NeobyatnayaAMNZ_bot"',
            'MODE="${1:-}"',
        }:
            self.assertIn(marker, script)
        dispatch = script.split('case "$MODE" in', 1)[1]
        self.assertRegex(dispatch, r"preflight\)\s+preflight\s+;;")
        self.assertRegex(dispatch, r"cleanup\)\s+cleanup_stale_start\s+;;")
        self.assertNotRegex(dispatch, r"\b(?:stage|accept|enable|drain|reset)\)")

    def test_remote_validates_exact_single_private_first_admin_start_twice(self) -> None:
        script = read_required(self, REMOTE, "cleanup remote executor")
        probe = script.split("async def inspect_one", 1)[1].split("async def main", 1)[0]
        for marker in (
            "len(updates) != 1",
            "isinstance(update_id, int)",
            "message.chat.type != \"private\"",
            "int(message.from_user.id) != first_admin",
            "int(message.chat.id) != first_admin",
            "text != \"/start\"",
        ):
            self.assertIn(marker, probe)
        main = script.split("async def main", 1)[1]
        self.assertEqual(main.count("await inspect_one(bot, first_admin)"), 2)
        self.assertIn("if first_update_id != second_update_id", main)

    def test_remote_has_one_advancing_offset_after_second_recheck(self) -> None:
        script = read_required(self, REMOTE, "cleanup remote executor")
        telegram = script.split("telegram_queue_gate() {", 1)[1].split("preflight() {", 1)[0]
        advancing = re.findall(r"offset\s*=", telegram)
        self.assertEqual(len(advancing), 1)
        self.assertIn("offset=second_update_id + 1", telegram)
        self.assertLess(
            telegram.index("second_update_id = await inspect_one"),
            telegram.index("offset=second_update_id + 1"),
        )
        self.assertIn("pending_update_count != 0", telegram)

    def test_remote_never_sends_or_mutates_forbidden_surfaces(self) -> None:
        script = read_required(self, REMOTE, "cleanup remote executor")
        forbidden = (
            r"send_(?:message|photo|document)",
            r"setWebhook|deleteWebhook|drop_pending_updates|setChatPhoto",
            r"dispatcher|handle_start|create_workflow",
            r"docker\s+(?:restart|stop|start|rm|kill|update)\b",
            r"(?:awg|wg)\s+set\b",
            r"sqlite3\s+.*(?:restore|\.restore)",
            r"systemctl\s+(?:start|stop|restart|enable|disable)",
        )
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, script, re.IGNORECASE), pattern)

    def test_remote_outputs_only_closed_safe_categories(self) -> None:
        script = read_required(self, REMOTE, "cleanup remote executor")
        for category in (
            "identity_mismatch", "webhook_configured", "pending_count_not_one",
            "update_count_not_one", "actor_mismatch", "chat_not_private",
            "command_mismatch", "update_shape_invalid",
            "update_changed_before_ack", "concurrent_update_detected",
            "network_failure", "cleanup_timeout", "cleanup_rejected",
        ):
            self.assertIn(category, script)
        self.assertNotIn("raise SystemExit(str(exc))", script)
        self.assertNotRegex(script, r"print\([^\n]*(?:update_id|first_admin|message\.text)")

    def test_runner_binds_exact_remote_sha_and_single_use_cleanup_receipt(self) -> None:
        runner = read_required(self, RUNNER, "cleanup SSH runner")
        for marker in (
            '[ValidateSet("preflight", "cleanup")]',
            'if ($Mode -eq "cleanup")',
            '[IO.FileMode]::CreateNew',
            'AMN2\\phase11',
            'telegram-002b-stale-start-',
            'cleanup-consumed',
            '"-F", "none"',
            '"StrictHostKeyChecking=yes"',
            '"GlobalKnownHostsFile=none"',
            '"KnownHostsCommand=none"',
        ):
            self.assertIn(marker, runner)
```

- [ ] **Step 3: Run the focused test and verify the expected red state**

Run:

```powershell
python -m pytest tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py -q
```

Expected: failures report that both new executor files are missing; the existing-byte test passes.

- [ ] **Step 4: Commit the red test only**

```powershell
git add tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py
git commit -m "Test exact Telegram stale-start cleanup contract"
```

---

### Task 2: Implement the standalone remote preflight and exact acknowledgement

**Files:**
- Create: `scripts/vps/phase11_telegram_002b_stale_start_cleanup_remote.sh`
- Test: `tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py`
- Reference: `scripts/vps/phase11_telegram_002b_persistent_remote.sh:44-227`
- Reference: `scripts/vps/phase11_telegram_002b_persistent_remote.sh:245-282`
- Reference: `scripts/vps/phase11_telegram_002b_persistent_remote.sh:461-480`

**Interfaces:**
- Consumes: mode `preflight|cleanup` as positional argument 1; exact production env and source inputs already used by the activation executor.
- Produces: sanitized `telegram_cleanup_preflight=pass` or `telegram_cleanup=pass acknowledged_update=first_configured_admin_exact_private_start_only`, plus unchanged DB/web/AWG receipts.

- [ ] **Step 1: Create the shell boundary and duplicate reviewed read-only checks**

Create a Bash script beginning with:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

MODE="${1:-}"
EXPECTED_OVERLAY="0b858c5"
SOURCE_FULL_COMMIT="0b858c5cdbc5b565cc265966a2edfe2d339d65e0"
EXPECTED_BOT_USERNAME="NeobyatnayaAMNZ_bot"
AMN2_DIR="/opt/amn2"
ENV_PATH="/opt/amn2/.env"
OVERLAY_PATH="/opt/amn2/.amn2-source-overlay"
PYTHON_BIN="/opt/amn2/venv/bin/python"
BOT_UNIT="amneziya-bot.service"
WEB_UNIT="amneziya-web.service"

die() { printf 'cleanup_gate=failed reason=cleanup_rejected\n' >&2; exit 1; }
```

Copy the exact bodies of `require_cmd`, `sha256_upper`, `require_regular_file`,
`require_executable_file`, `source_contract_check`, `write_gate_check`,
`listener_check`, `web_check`, `bot_inactive_disabled_check`, `db_snapshot`
and `awg_snapshot` from the cited activation executor ranges. Do not copy any
stage, systemd mutation, rollback, env update, DB backup/restore or bot-health
function. Add `full_preflight` that runs those checks, stores DB/AWG snapshots
in root-owned temporary files, and emits only the existing sanitized receipts.

- [ ] **Step 2: Implement the bounded queue inspector and one offset advance**

Embed Python with this exact control flow:

```python
class CleanupRejected(RuntimeError):
    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category = category


def pending_count(webhook) -> int:
    raw = getattr(webhook, "pending_update_count", None)
    if isinstance(raw, bool):
        raise CleanupRejected("pending_count_not_one")
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise CleanupRejected("pending_count_not_one") from None
    if value != 1:
        raise CleanupRejected("pending_count_not_one")
    return value


async def inspect_one(bot, first_admin: int) -> int:
    updates = await bot.get_updates(limit=2, timeout=0)
    if len(updates) != 1:
        raise CleanupRejected("update_count_not_one")
    update = updates[0]
    update_id = getattr(update, "update_id", None)
    if not isinstance(update_id, int) or isinstance(update_id, bool) or update_id < 0:
        raise CleanupRejected("update_shape_invalid")
    message = getattr(update, "message", None)
    if message is None or getattr(message, "from_user", None) is None:
        raise CleanupRejected("update_shape_invalid")
    disallowed_update_fields = (
        "edited_message", "channel_post", "edited_channel_post",
        "business_connection", "business_message", "edited_business_message",
        "deleted_business_messages", "message_reaction", "message_reaction_count",
        "inline_query", "chosen_inline_result", "callback_query",
        "shipping_query", "pre_checkout_query", "poll", "poll_answer",
        "my_chat_member", "chat_member", "chat_join_request", "chat_boost",
        "removed_chat_boost",
    )
    if any(getattr(update, field, None) is not None for field in disallowed_update_fields):
        raise CleanupRejected("update_shape_invalid")
    if str(getattr(message, "content_type", "") or "") != "text":
        raise CleanupRejected("update_shape_invalid")
    if getattr(message, "chat", None) is None or message.chat.type != "private":
        raise CleanupRejected("chat_not_private")
    if int(message.from_user.id) != first_admin:
        raise CleanupRejected("actor_mismatch")
    if int(message.chat.id) != first_admin:
        raise CleanupRejected("actor_mismatch")
    text = str(getattr(message, "text", "") or "").strip()
    if text != "/start":
        raise CleanupRejected("command_mismatch")
    return update_id


async def main(cleanup: bool) -> None:
    bot = None
    try:
        os.environ.clear()
        settings = Settings(_env_file=env_path)
        if settings.vps_apply_enabled or settings.operator_device_create_enabled:
            raise CleanupRejected("cleanup_rejected")
        admin_ids = [int(value) for value in settings.admin_ids]
        if (
            not admin_ids
            or any(value <= 0 for value in admin_ids)
            or len(set(admin_ids)) != len(admin_ids)
        ):
            raise CleanupRejected("cleanup_rejected")
        first_admin = admin_ids[0]
        account = pwd.getpwnam(service_user)
        os.initgroups(account.pw_name, account.pw_gid)
        os.setgid(account.pw_gid)
        os.setuid(account.pw_uid)
        bot = create_bot(
            telegram_bot_token=settings.telegram_bot_token,
            telegram_proxy_url=settings.telegram_proxy_url,
        )
        me = await bot.get_me()
        actual = str(getattr(me, "username", "") or "").strip()
        if actual.casefold() != expected_username.casefold():
            raise CleanupRejected("identity_mismatch")
        webhook = await bot.get_webhook_info()
        if str(getattr(webhook, "url", "") or "").strip():
            raise CleanupRejected("webhook_configured")
        pending_count(webhook)
        first_update_id = await inspect_one(bot, first_admin)
        webhook = await bot.get_webhook_info()
        if str(getattr(webhook, "url", "") or "").strip():
            raise CleanupRejected("webhook_configured")
        pending_count(webhook)
        second_update_id = await inspect_one(bot, first_admin)
        if first_update_id != second_update_id:
            raise CleanupRejected("update_changed_before_ack")
        if not cleanup:
            print("telegram_cleanup_preflight=pass")
            return
        concurrent = await bot.get_updates(
            offset=second_update_id + 1,
            limit=1,
            timeout=0,
        )
        final_webhook = await bot.get_webhook_info()
        if str(getattr(final_webhook, "url", "") or "").strip():
            raise CleanupRejected("webhook_configured")
        final_pending = int(getattr(final_webhook, "pending_update_count", 0) or 0)
        if concurrent or final_pending != 0:
            raise CleanupRejected("concurrent_update_detected")
        print("telegram_cleanup=pass acknowledged_update=first_configured_admin_exact_private_start_only")
    except CleanupRejected as exc:
        raise SystemExit(f"telegram_cleanup=failed reason={exc.category}") from None
    except TimeoutError:
        raise SystemExit("telegram_cleanup=failed reason=cleanup_timeout") from None
    except (OSError, TelegramAPIError):
        raise SystemExit("telegram_cleanup=failed reason=network_failure") from None
    except Exception:
        raise SystemExit("telegram_cleanup=failed reason=cleanup_rejected") from None
    finally:
        if bot is not None:
            try:
                await bot.session.close()
            except Exception:
                raise SystemExit("telegram_cleanup=failed reason=cleanup_rejected") from None
```

Wrap `main()` in `asyncio.timeout(30)`. Do not print `first_admin`, update IDs,
raw updates or exception text.

- [ ] **Step 3: Add exact dispatch and post-ack immutable-surface verification**

Use:

```bash
case "$MODE" in
  preflight)
    preflight
    ;;
  cleanup)
    cleanup_stale_start
    ;;
  *)
    die
    ;;
esac
```

`preflight` runs `full_preflight`, queue inspection without offset, then removes
its root-only temporary directory. `cleanup_stale_start` runs `full_preflight`,
captures exact DB/AWG snapshots, runs the cleanup mode, reruns bot-disabled,
web, DB and AWG checks and byte-compares pre/post DB logical/count and AWG
container/restart/peer snapshots before reporting success.

- [ ] **Step 4: Run syntax and focused tests**

```powershell
bash -n scripts/vps/phase11_telegram_002b_stale_start_cleanup_remote.sh
python -m pytest tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py -q
```

Expected: runner-related test still fails because the PowerShell file is absent; all remote tests pass.

- [ ] **Step 5: Commit the remote executor**

```powershell
git add scripts/vps/phase11_telegram_002b_stale_start_cleanup_remote.sh tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py
git commit -m "Add fail-closed Telegram stale-start cleanup"
```

---

### Task 3: Add the checksum-bound single-use SSH runner

**Files:**
- Create: `scripts/vps/phase11_telegram_002b_stale_start_cleanup_ssh_runner.ps1`
- Modify: `tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py`
- Reference: `scripts/vps/phase11_telegram_002b_persistent_ssh_runner.ps1:1-189`

**Interfaces:**
- Consumes: `-Mode preflight|cleanup`, exact future live approval string and the reviewed remote script bytes.
- Produces: one trusted SSH invocation; cleanup mode atomically consumes an exclusive local receipt before remote contact.

- [ ] **Step 1: Compute the remote SHA after Task 2**

```powershell
(Get-FileHash scripts/vps/phase11_telegram_002b_stale_start_cleanup_remote.sh -Algorithm SHA256).Hash
```

Store the uppercase result as `$expectedRemoteScriptSha`. Do not invent the hash before the file bytes are final.

- [ ] **Step 2: Create the runner from the reviewed trust boundary**

Start with:

```powershell
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("preflight", "cleanup")]
    [string]$Mode,
    [Parameter(Mandatory = $true)]
    [string]$Approval
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedApproval = "APPROVE PHASE11_TELEGRAM_002B_STALE_START_CLEANUP_REMOTE_SHA_${expectedRemoteScriptSha}_0B858C5_EXACT_ONE_PRIVATE_FIRST_ADMIN_START_ACK_ONLY_NO_RESPONSE_DB_WEB_PROFILE_AND_AWG_UNTOUCHED"

if (-not [string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)) {
    throw "Exact live cleanup approval mismatch"
}
```

Immediately before `$expectedApproval`, assign `$expectedRemoteScriptSha` to
the literal 64-character uppercase result printed in Step 1. The saved runner
must contain that literal, not a runtime-computed hash. Copy the absolute
OpenSSH, pinned known-host, `Invoke-CapturedProcess`, SHA verification and
same-byte stdin transport blocks exactly from the cited activation runner.
Change only the remote filename and remote argument mode.

- [ ] **Step 3: Add the exclusive cleanup receipt before SSH contact**

```powershell
$approvalStateDir = Join-Path $env:LOCALAPPDATA "AMN2\phase11"
$approvalReceipt = Join-Path $approvalStateDir (
    "telegram-002b-stale-start-" + $expectedRemoteScriptSha + ".cleanup-consumed"
)
if ($Mode -eq "cleanup") {
    New-Item -ItemType Directory -Force -Path $approvalStateDir | Out-Null
    $receiptStream = $null
    try {
        $receiptStream = [IO.File]::Open(
            $approvalReceipt,
            [IO.FileMode]::CreateNew,
            [IO.FileAccess]::Write,
            [IO.FileShare]::None
        )
        $receiptBytes = [Text.Encoding]::UTF8.GetBytes(
            "mode=cleanup`nremote_sha=$expectedRemoteScriptSha`n"
        )
        $receiptStream.Write($receiptBytes, 0, $receiptBytes.Length)
        $receiptStream.Flush()
    } catch {
        throw "Cleanup approval already consumed or receipt unavailable"
    } finally {
        if ($null -ne $receiptStream) { $receiptStream.Dispose() }
    }
}
```

Preflight does not create a receipt. Cleanup never removes or overwrites its
receipt, including after a remote refusal.

- [ ] **Step 4: Replace the planned SHA marker in the test and run green tests**

Add exact assertions for `$expectedRemoteScriptSha`, the complete literal
approval, remote file hash equality, receipt-before-`Invoke-CapturedProcess`
ordering and absolute trusted OpenSSH resolution.

Run:

```powershell
python -m pytest tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py -q
$tokens = $null; $errors = $null
[System.Management.Automation.Language.Parser]::ParseFile(
  (Resolve-Path scripts/vps/phase11_telegram_002b_stale_start_cleanup_ssh_runner.ps1),
  [ref]$tokens,
  [ref]$errors
) | Out-Null
if ($errors.Count -ne 0) { throw ($errors | Out-String) }
```

Expected: all focused tests pass and PowerShell parser errors equal zero.

- [ ] **Step 5: Commit the runner**

```powershell
git add scripts/vps/phase11_telegram_002b_stale_start_cleanup_ssh_runner.ps1 tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py
git commit -m "Bind exact Telegram stale-start cleanup approval"
```

---

### Task 4: Verify security boundaries, synchronize status and publish

**Files:**
- Modify: `docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `research/amn2/phase-11-telegram-002b-staged-persistent-activation-gate-2026-07-17.md`
- Preserve: `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`

**Interfaces:**
- Consumes: verified cleanup remote/runner SHA values and all test/security receipts.
- Produces: origin-synchronized engineering evidence and one literal future live cleanup approval phrase.

- [ ] **Step 1: Run focused and canonical test suites**

```powershell
python -m pytest tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py -q
python -m pytest tests -q
bash -n scripts/vps/phase11_telegram_002b_stale_start_cleanup_remote.sh
git diff --check
```

Expected: focused and canonical suites pass; Bash syntax and whitespace checks pass.

- [ ] **Step 2: Run prohibited-operation and secret scans**

```powershell
rg -n -i "deleteWebhook|drop_pending_updates|setWebhook|setChatPhoto|send_(message|photo|document)|docker (restart|stop|start|rm|kill|update)|\b(awg|wg) set\b|sqlite3 .*restore" scripts/vps/phase11_telegram_002b_stale_start_cleanup_remote.sh
rg -n "[0-9]{9,}:[A-Za-z0-9_-]{20,}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|ADMIN_TELEGRAM_IDS=.*[0-9]" scripts/vps/phase11_telegram_002b_stale_start_cleanup_* tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py
```

Expected: zero forbidden operations and zero high-confidence secrets. The
literal words inside negative-test regexes are reviewed as test-only markers,
not executable operations.

- [ ] **Step 3: Run a fresh security diff scan**

Use `codex-security:security-diff-scan` on the complete diff from `f702cda` to
the current working tree. Validate acknowledgement ordering, race behavior,
exception redaction, OpenSSH trust isolation, single-use receipt timing and
the absence of DB/web/AWG/profile mutation. Required result before publication:
zero unresolved reportable findings.

- [ ] **Step 4: Synchronize Phase 11 status**

Append the same canonical receipt keys to all four status/evidence files. Set
each SHA and test-result value to the exact output already observed in Steps 1
and 2; do not use symbolic values in the saved documents:

```text
phase11_telegram_002b_backlog_blocker=pending_updates_nonzero|stage_not_run|2fdb_stage_authority_unconsumed
phase11_telegram_002b_cleanup_design=d474ff6|exact_one_private_first_admin_start|ack_only|no_response
phase11_telegram_002b_cleanup_remote_sha=64-character uppercase digest observed for the final remote bytes
phase11_telegram_002b_cleanup_runner_sha=64-character uppercase digest observed for the final runner bytes
phase11_telegram_002b_cleanup_tests=focused and canonical pass counts observed in Step 1
phase11_telegram_002b_cleanup_security=complete|reportable_findings_0|secret_matches_0
phase11_telegram_002b_cleanup_live=not_run|new_exact_approval_required
```

Replace every angle-bracket value with observed evidence before saving.

- [ ] **Step 5: Review, commit and push the implementation slice**

```powershell
git status --short
git diff --check
git diff --stat f702cda..HEAD
git add scripts/vps/phase11_telegram_002b_stale_start_cleanup_remote.sh scripts/vps/phase11_telegram_002b_stale_start_cleanup_ssh_runner.ps1 tests/test_phase11_telegram_002b_stale_start_cleanup_executor.py docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md docs/PROJECT_STATUS_CURRENT.ru.md research/amn2/phase-11-telegram-002b-staged-persistent-activation-gate-2026-07-17.md docs/superpowers/plans/2026-07-17-phase11-telegram-002b-stale-start-single-update-cleanup.ru.md
git diff --cached --check
git commit -m "Prepare exact Telegram stale-start cleanup gate"
git push origin codex-spark-phase9-docs-sync
git fetch origin codex-spark-phase9-docs-sync
```

Verify local HEAD equals `origin/codex-spark-phase9-docs-sync`. Confirm the only
remaining worktree entry is the untouched untracked
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`.

- [ ] **Step 6: Issue, but do not execute, the exact live cleanup approval**

Only after origin synchronization, copy the complete literal value of
`$expectedApproval` from the reviewed runner and present that exact value to
the user. Recompute the remote SHA first and prove it equals the runner's
constant; do not manually retype or shorten the phrase.

Do not run cleanup until the user returns that exact phrase. Do not ask the
user to send `/start`; a fresh `/start` is requested only after successful
cleanup/postflight and a new successful `2FDB...` disabled-first stage reports
`awaiting_admin_start=true`.
