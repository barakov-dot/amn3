import hashlib
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REMOTE = (
    REPO_ROOT
    / "scripts"
    / "vps"
    / "post_release_telegram_group_icon_001_remote.sh"
)
RUNNER = (
    REPO_ROOT
    / "scripts"
    / "vps"
    / "post_release_telegram_group_icon_001_ssh_runner.ps1"
)


def read_required(test: unittest.TestCase, path: Path, label: str) -> str:
    test.assertTrue(path.exists(), f"{label} is missing")
    return path.read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class PostReleaseTelegramGroupIcon001ExecutorTests(unittest.TestCase):
    def test_existing_phase11_telegram_executors_are_unchanged(self) -> None:
        expected = {
            "phase11_telegram_002b_persistent_remote.sh": (
                "2FDBAD445F4EBDA4A94BE84CB4FF43D05AE458D68A78686490775B8F242A00E2"
            ),
            "phase11_telegram_002b_persistent_ssh_runner.ps1": (
                "75B210410CFE45377857A02FAA43618EE26533259B15AB348693B5292091ED53"
            ),
            "phase11_telegram_002b_stale_start_cleanup_remote.sh": (
                "41F69F945F74647B441173B682277E0568DA81CC7F0B12EADD9BD534DB225242"
            ),
            "phase11_telegram_002b_stale_start_cleanup_ssh_runner.ps1": (
                "D3BD76119B35155AAB922E54C2E59F50B7D9D0B23C9B5AC2268887D8ADB70A1F"
            ),
        }
        for name, digest in expected.items():
            self.assertEqual(sha256(REPO_ROOT / "scripts" / "vps" / name), digest)

    def test_remote_exposes_only_fingerprint_preflight_and_apply(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        self.assertIn('MODE="${1:-}"', script)
        dispatch = script.split('case "$MODE" in', 1)[1]
        self.assertRegex(dispatch, r"fingerprint\)\s+fingerprint_target\s+;;")
        self.assertRegex(dispatch, r"preflight\)\s+preflight\s+;;")
        self.assertRegex(dispatch, r"apply\)\s+apply_group_icon\s+;;")
        self.assertNotRegex(dispatch, r"\b(?:rollback|delete|message|profile)\)")

    def test_remote_binds_source_runtime_and_canonical_asset(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        required = {
            'EXPECTED_OVERLAY="0b858c5"',
            'SOURCE_FULL_COMMIT="0b858c5cdbc5b565cc265966a2edfe2d339d65e0"',
            'EXPECTED_BOT_USERNAME="NeobyatnayaAMNZ_bot"',
            'ASSET_SHA="40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791"',
            'ASSET_WIDTH="1254"',
            'ASSET_HEIGHT="1254"',
            'APP_MAIN_SHA="C34A0F457B2242EDE138DD0B6DC1B08B860515F7BD2FADB7DF8F2B86A3F5ED31"',
            'SETTINGS_SHA="1DB81553DBCBF4DAFC710EFDD69C2DB0CC1A869F0754D7BB67C7ADFA3DCAC631"',
        }
        for marker in sorted(required):
            self.assertIn(marker, script)
        self.assertIn('require_regular_file "$ASSET_PATH"', script)
        self.assertIn('PNG signature or IHDR mismatch', script)

    def test_remote_requires_private_exact_target_contract(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        for marker in (
            'TARGET_PATH="/root/.config/amn2/telegram-group-icon-001/target.json"',
            'stat -c \'%U:%G:%a\' "$TARGET_PATH"',
            'root:root:600',
            'set(payload) != {"chat_id", "expected_title", "expected_type"}',
            'expected_type not in {"group", "supergroup"}',
            'TELEGRAM-GROUP-ICON-001\\0',
            'target_chat_fingerprint=',
        ):
            self.assertIn(marker, script)
        self.assertNotRegex(script, r"print\([^\n]*(?:chat_id|expected_title)")

    def test_remote_preflight_binds_identity_chat_permission_and_queue(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        telegram = script.split("async def telegram_contract", 1)[1].split(
            "async def snapshot_current_photo", 1
        )[0]
        for marker in (
            "await bot.get_me()",
            "await bot.get_webhook_info()",
            "pending_update_count",
            "await bot.get_chat(chat_id)",
            "await bot.get_chat_member(chat_id, me.id)",
            "identity_mismatch",
            "webhook_configured",
            "pending_updates_nonzero",
            "target_mismatch",
            "title_mismatch",
            "type_mismatch",
            "permission_denied",
        ):
            self.assertIn(marker, telegram)
        self.assertIn('getattr(member, "can_change_info", False) is not True', telegram)

    def test_remote_never_consumes_updates_sends_messages_or_changes_profile(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        forbidden = (
            r"get_updates|deleteWebhook|setWebhook|drop_pending_updates",
            r"send_(?:message|photo|document|video|media_group)",
            r"setMyProfilePhoto|set_my_profile_photo",
            r"systemctl\s+(?:start|stop|restart|enable|disable)\s+\"?\$BOT_UNIT",
            r"systemctl\s+(?:start|stop|restart|enable|disable)\s+\"?\$WEB_UNIT",
            r"docker\s+(?:restart|stop|start|rm|kill|update)\b",
            r"(?:awg|wg)\s+set\b",
            r"sqlite3\s+.*(?:restore|\.restore)",
        )
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, script, re.IGNORECASE), pattern)

    def test_remote_snapshots_previous_photo_or_no_photo_receipt(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        snapshot = script.split("async def snapshot_current_photo", 1)[1].split(
            "async def apply_photo", 1
        )[0]
        for marker in (
            "big_file_id",
            "await bot.get_file",
            "await bot.download_file",
            'os.chmod(snapshot_path, 0o600)',
            'snapshot_status = "existing_photo"',
            'snapshot_status = "no_existing_photo"',
        ):
            self.assertIn(marker, snapshot)
        self.assertNotIn("file_path)", re.sub(r"await bot\.download_file\([^\n]+", "", snapshot))

    def test_remote_has_exactly_one_apply_mutation_and_bounded_rollback(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        apply_photo = script.split("async def apply_photo", 1)[1].split(
            "async def rollback_photo", 1
        )[0]
        rollback = script.split("async def rollback_photo", 1)[1].split(
            "async def main", 1
        )[0]
        self.assertEqual(apply_photo.count("set_chat_photo"), 1)
        self.assertIn("FSInputFile(asset_path)", apply_photo)
        self.assertIn("set_chat_photo", rollback)
        self.assertIn("delete_chat_photo", rollback)
        self.assertIn('ROLLBACK_TTL_SECONDS="240"', script)
        self.assertIn("write_rollback_helper", script)
        self.assertIn("arm_automatic_rollback", script)
        self.assertIn("cancel_automatic_rollback", script)

    def test_remote_orders_rollback_before_mutation_and_cleanup_after_postflight(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        apply_gate = script.split("apply_group_icon() {", 1)[1].split(
            'case "$MODE" in', 1
        )[0]
        arm = apply_gate.index('arm_automatic_rollback "$state_root"')
        mutate = apply_gate.index("telegram_action apply")
        postflight = apply_gate.index("telegram_action postflight")
        cancel = apply_gate.index('cancel_automatic_rollback "$state_root"')
        cleanup = apply_gate.index('cleanup_private_state "$state_root"')
        self.assertLess(arm, mutate)
        self.assertLess(mutate, postflight)
        self.assertLess(postflight, cancel)
        self.assertLess(cancel, cleanup)
        for signal in ("ERR", "HUP", "INT", "TERM"):
            self.assertIn(f"trap 'rollback_and_exit", apply_gate)

    def test_remote_freezes_target_for_apply_and_rollback(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        apply_gate = script.split("apply_group_icon() {", 1)[1].split(
            'case "$MODE" in', 1
        )[0]
        helper = script.split("write_rollback_helper() {", 1)[1].split(
            "arm_automatic_rollback() {", 1
        )[0]
        self.assertIn('cp -- "$TARGET_PATH" "$state_root/target.json"', apply_gate)
        self.assertLess(
            apply_gate.index('cp -- "$TARGET_PATH" "$state_root/target.json"'),
            apply_gate.index('telegram_action snapshot "$state_root"'),
        )
        self.assertIn('target_path = state_root / "target.json"', helper)
        self.assertNotIn(
            'Path("/root/.config/amn2/telegram-group-icon-001/target.json")',
            helper,
        )
        self.assertIn('"$state_root/target.json"', script)

    def test_remote_disarms_timer_before_emergency_restore_and_cleanup(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        rollback_exit = script.split("rollback_and_exit() {", 1)[1].split(
            "common_preflight() {", 1
        )[0]
        self.assertIn("disarm_rollback_timer", script)
        self.assertIn('disarm_rollback_timer "$CURRENT_STATE_ROOT"', rollback_exit)
        self.assertLess(
            rollback_exit.index('disarm_rollback_timer "$CURRENT_STATE_ROOT"'),
            rollback_exit.index("rollback_current"),
        )
        self.assertLess(
            rollback_exit.index('disarm_rollback_timer "$CURRENT_STATE_ROOT"'),
            rollback_exit.index('cleanup_private_state "$CURRENT_STATE_ROOT"'),
        )

    def test_success_cancel_rechecks_service_after_timer_stop(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        cancel = script.split("cancel_automatic_rollback() {", 1)[1].split(
            "disarm_rollback_timer() {", 1
        )[0]
        timer_stop = cancel.index('systemctl stop "${timer_base}.timer"')
        after_stop = cancel[timer_stop:]
        self.assertIn(
            'service_state="$(systemctl is-active "${timer_base}.service"',
            after_stop,
        )
        self.assertRegex(after_stop, r'case "\$service_state" in\s+inactive\|dead\|unknown\)')
        self.assertLess(
            after_stop.index('case "$service_state" in'),
            after_stop.rindex('[ ! -e "$state_root/rollback.receipt" ]'),
        )

    def test_automatic_rollback_helper_has_explicit_timeout(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        helper = script.split("write_rollback_helper() {", 1)[1].split(
            "arm_automatic_rollback() {", 1
        )[0]
        self.assertIn("async with asyncio.timeout(60):", helper)
        self.assertIn("await restore()", helper)

    def test_rollback_helper_revalidates_target_and_sanitizes_all_failures(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        helper = script.split("write_rollback_helper() {", 1)[1].split(
            "arm_automatic_rollback() {", 1
        )[0]
        for marker in (
            'expected_username = "NeobyatnayaAMNZ_bot"',
            "await bot.get_me()",
            "await bot.get_chat(payload[\"chat_id\"])",
            "await bot.get_chat_member(payload[\"chat_id\"], me.id)",
            'getattr(member, "can_change_info", False) is not True',
            'if str(getattr(chat, "title", "") or "") != payload["expected_title"]',
            "except Exception:",
            'telegram_group_icon_rollback=failed reason=photo_rollback_failed',
        ):
            self.assertIn(marker, helper)
        self.assertIn("from None", helper)
        self.assertNotIn("raise SystemExit(str(exc))", helper)

    def test_all_embedded_python_heredocs_compile(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        blocks = re.findall(r"<<'PY'\n(.*?)\nPY\n", script, flags=re.DOTALL)
        self.assertGreaterEqual(len(blocks), 6)
        for index, block in enumerate(blocks):
            compile(block, f"embedded_python_{index}.py", "exec")

    def test_remote_proves_bot_db_web_and_awg_invariants(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        apply_gate = script.split("apply_group_icon() {", 1)[1].split(
            'case "$MODE" in', 1
        )[0]
        for marker in (
            'bot_snapshot >"$state_root/bot.before"',
            'db_snapshot >"$state_root/db.before"',
            'awg_snapshot >"$state_root/awg.before"',
            'bot_snapshot >"$state_root/bot.after"',
            'db_snapshot >"$state_root/db.after"',
            'awg_snapshot >"$state_root/awg.after"',
            'cmp -s "$state_root/bot.before" "$state_root/bot.after"',
            'cmp -s "$state_root/db.before" "$state_root/db.after"',
            'cmp -s "$state_root/awg.before" "$state_root/awg.after"',
            "web_check",
        ):
            self.assertIn(marker, apply_gate)

    def test_remote_outputs_only_safe_closed_categories(self) -> None:
        script = read_required(self, REMOTE, "group icon remote executor")
        for category in (
            "identity_mismatch",
            "webhook_configured",
            "pending_updates_nonzero",
            "target_mismatch",
            "title_mismatch",
            "type_mismatch",
            "permission_denied",
            "photo_snapshot_failed",
            "photo_apply_failed",
            "photo_postflight_failed",
            "photo_rollback_failed",
            "network_failure",
            "operation_timeout",
            "gate_rejected",
        ):
            self.assertIn(category, script)
        self.assertNotIn("raise SystemExit(str(exc))", script)
        self.assertNotRegex(script, r"print\([^\n]*(?:token|file_path|expected_title)")

    def test_runner_binds_dynamic_target_exact_approval_and_remote_sha(self) -> None:
        runner = read_required(self, RUNNER, "group icon SSH runner")
        remote_hash = sha256(REMOTE)
        self.assertIn(f'$expectedRemoteScriptSha = "{remote_hash}"', runner)
        for marker in (
            "POST_RELEASE_TELEGRAM_GROUP_ICON_001_REMOTE_SHA_",
            "_SOURCE_0B858C5_TARGET_SHA256_",
            "_EXACT_GROUP_PHOTO_SINGLE_SETCHATPHOTO_POSTFLIGHT_OR_ROLLBACK_",
            "NO_MESSAGES_BOT_DB_WEB_AND_AWG_UNTOUCHED",
            "[string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)",
            "ComputeHash($remoteScriptBytes)",
            "-StandardInputBytes $remoteScriptBytes",
        ):
            self.assertIn(marker, runner)

    def test_runner_fingerprint_is_non_live_and_approval_is_required_otherwise(self) -> None:
        runner = read_required(self, RUNNER, "group icon SSH runner")
        self.assertIn('[ValidateSet("fingerprint", "preflight", "apply")]', runner)
        self.assertIn('if ($Mode -eq "fingerprint")', runner)
        self.assertIn("Fingerprint mode does not accept approval", runner)
        self.assertIn("Exact live approval mismatch", runner)
        self.assertIn("Target fingerprint required", runner)
        self.assertIn('if ($Mode -eq "apply")', runner)
        self.assertIn("[IO.FileMode]::CreateNew", runner)
        self.assertIn(".apply-consumed", runner)

    def test_runner_uses_trusted_isolated_openssh_and_redacts_target(self) -> None:
        runner = read_required(self, RUNNER, "group icon SSH runner")
        for marker in (
            'Join-Path $env:WINDIR "System32\\OpenSSH"',
            'Join-Path $trustedOpenSshDir "ssh.exe"',
            '"-F", "none"',
            '"StrictHostKeyChecking=yes"',
            '"GlobalKnownHostsFile=none"',
            '"KnownHostsCommand=none"',
            '-replace [regex]::Escape($target), "<target>"',
            "[IO.Path]::IsPathFullyQualified($FileName)",
        ):
            self.assertIn(marker, runner)


if __name__ == "__main__":
    unittest.main()
