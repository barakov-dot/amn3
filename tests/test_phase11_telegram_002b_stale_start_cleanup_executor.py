import hashlib
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REMOTE = (
    REPO_ROOT
    / "scripts"
    / "vps"
    / "phase11_telegram_002b_stale_start_cleanup_remote.sh"
)
RUNNER = (
    REPO_ROOT
    / "scripts"
    / "vps"
    / "phase11_telegram_002b_stale_start_cleanup_ssh_runner.ps1"
)
ACTIVATION_REMOTE = (
    REPO_ROOT / "scripts" / "vps" / "phase11_telegram_002b_persistent_remote.sh"
)
ACTIVATION_RUNNER = (
    REPO_ROOT
    / "scripts"
    / "vps"
    / "phase11_telegram_002b_persistent_ssh_runner.ps1"
)


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

    def test_remote_requires_exact_read_only_runtime_preflight(self) -> None:
        script = read_required(self, REMOTE, "cleanup remote executor")
        for marker in (
            "source_contract_check",
            "write_gate_check",
            "listener_check",
            "web_check",
            "bot_inactive_disabled_check",
            "db_snapshot",
            "awg_snapshot",
            'readlink -f -- "$path"',
            'require_executable_file "$PYTHON_BIN"',
        ):
            self.assertIn(marker, script)
        self.assertIn('os.environ.clear()', script)
        self.assertIn('os.setuid(account.pw_uid)', script)

    def test_remote_validates_single_private_first_admin_start_twice(self) -> None:
        script = read_required(self, REMOTE, "cleanup remote executor")
        probe = script.split("async def inspect_one", 1)[1].split(
            "async def main", 1
        )[0]
        for marker in (
            "len(updates) != 1",
            "isinstance(update_id, int)",
            'message.chat.type != "private"',
            "sender_id = int(message.from_user.id)",
            "chat_id = int(message.chat.id)",
            "if sender_id != first_admin",
            "if chat_id != first_admin",
            'text != "/start"',
            'message, "content_type"',
            '"callback_query"',
            '"edited_message"',
            '"business_message"',
        ):
            self.assertIn(marker, probe)
        main = script.split("async def main", 1)[1]
        self.assertEqual(main.count("await inspect_one(bot, first_admin)"), 2)
        self.assertIn("if first_update_id != second_update_id", main)
        self.assertIn("len(set(admin_ids)) != len(admin_ids)", main)

    def test_remote_has_one_advancing_offset_after_second_recheck(self) -> None:
        script = read_required(self, REMOTE, "cleanup remote executor")
        telegram = script.split("telegram_queue_gate() {", 1)[1].split(
            "preflight() {", 1
        )[0]
        self.assertEqual(len(re.findall(r"\boffset\s*=", telegram)), 1)
        self.assertIn("offset=second_update_id + 1", telegram)
        self.assertLess(
            telegram.index("second_update_id = await inspect_one"),
            telegram.index("offset=second_update_id + 1"),
        )
        self.assertIn("if concurrent or final_pending != 0", telegram)
        self.assertIn("final_webhook", telegram)
        self.assertIn("webhook_configured", telegram)

    def test_remote_preserves_db_web_awg_and_rechecks_bot_disabled(self) -> None:
        script = read_required(self, REMOTE, "cleanup remote executor")
        cleanup = script.split("cleanup_stale_start() {", 1)[1].split(
            'case "$MODE" in', 1
        )[0]
        for marker in (
            'db_snapshot >"$state_root/db.before"',
            'awg_snapshot >"$state_root/awg.before"',
            'db_snapshot >"$state_root/db.after"',
            'awg_snapshot >"$state_root/awg.after"',
            'cmp -s "$state_root/db.before" "$state_root/db.after"',
            'cmp -s "$state_root/awg.before" "$state_root/awg.after"',
            "bot_inactive_disabled_check",
            "web_check",
        ):
            self.assertIn(marker, cleanup)

    def test_remote_never_sends_or_mutates_forbidden_surfaces(self) -> None:
        script = read_required(self, REMOTE, "cleanup remote executor")
        forbidden = (
            r"send_(?:message|photo|document)",
            r"setWebhook|deleteWebhook|drop_pending_updates|setChatPhoto",
            r"dispatcher|handle_start|create_workflow",
            r"docker\s+(?:restart|stop|start|rm|kill|update)\b",
            r"(?:awg|wg)\s+set\b",
            r"sqlite3\s+.*(?:restore|\.restore)",
            r"systemctl\s+(?:start|stop|restart|enable|disable)\b",
        )
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, script, re.IGNORECASE), pattern)

    def test_remote_outputs_only_closed_safe_categories(self) -> None:
        script = read_required(self, REMOTE, "cleanup remote executor")
        for category in (
            "identity_mismatch",
            "webhook_configured",
            "pending_count_not_one",
            "update_count_not_one",
            "actor_mismatch",
            "chat_not_private",
            "command_mismatch",
            "update_shape_invalid",
            "update_changed_before_ack",
            "concurrent_update_detected",
            "network_failure",
            "cleanup_timeout",
            "cleanup_rejected",
        ):
            self.assertIn(category, script)
        self.assertNotIn("raise SystemExit(str(exc))", script)
        self.assertNotRegex(
            script,
            r"print\([^\n]*(?:update_id|first_admin|message\.text)",
        )

    def test_runner_binds_remote_sha_exact_approval_and_same_bytes(self) -> None:
        runner = read_required(self, RUNNER, "cleanup SSH runner")
        remote_hash = sha256(REMOTE)
        match = re.search(
            r'\$expectedRemoteScriptSha = "([A-F0-9]{64})"', runner
        )
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), remote_hash)
        exact = (
            "APPROVE PHASE11_TELEGRAM_002B_STALE_START_CLEANUP_REMOTE_SHA_"
            f"{remote_hash}_0B858C5_EXACT_ONE_PRIVATE_FIRST_ADMIN_START_ACK_ONLY_"
            "NO_RESPONSE_DB_WEB_PROFILE_AND_AWG_UNTOUCHED"
        )
        self.assertIn(f'$expectedApproval = "{exact}"', runner)
        self.assertIn("ComputeHash($remoteScriptBytes)", runner)
        self.assertIn("-StandardInputBytes $remoteScriptBytes", runner)

    def test_runner_uses_trusted_openssh_and_single_use_cleanup_receipt(self) -> None:
        runner = read_required(self, RUNNER, "cleanup SSH runner")
        for marker in (
            '[ValidateSet("preflight", "cleanup")]',
            'if ($Mode -eq "cleanup")',
            "[IO.FileMode]::CreateNew",
            'Join-Path $env:LOCALAPPDATA "AMN2\\phase11"',
            "telegram-002b-stale-start-",
            ".cleanup-consumed",
            'Join-Path $env:WINDIR "System32\\OpenSSH"',
            '"-F", "none"',
            '"StrictHostKeyChecking=yes"',
            '"GlobalKnownHostsFile=none"',
            '"KnownHostsCommand=none"',
        ):
            self.assertIn(marker, runner)
        receipt_index = runner.index("[IO.FileMode]::CreateNew")
        invoke_index = runner.rindex("Invoke-CapturedProcess")
        self.assertLess(receipt_index, invoke_index)


if __name__ == "__main__":
    unittest.main()
