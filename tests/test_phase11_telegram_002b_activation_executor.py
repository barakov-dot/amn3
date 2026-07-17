import hashlib
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REMOTE = REPO_ROOT / "scripts" / "vps" / "phase11_telegram_002b_persistent_remote.sh"
RUNNER = REPO_ROOT / "scripts" / "vps" / "phase11_telegram_002b_persistent_ssh_runner.ps1"


def read_required(test: unittest.TestCase, path: Path, label: str) -> str:
    test.assertTrue(path.exists(), f"{label} is missing")
    return path.read_text(encoding="utf-8")


class Phase11Telegram002bActivationExecutorTests(unittest.TestCase):
    def test_remote_binds_exact_source_identity_and_runtime_inputs(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        required = {
            'EXPECTED_OVERLAY="0b858c5"',
            'SOURCE_FULL_COMMIT="0b858c5cdbc5b565cc265966a2edfe2d339d65e0"',
            'EXPECTED_BOT_USERNAME="NeobyatnayaAMNZ_bot"',
            'UNIT_SOURCE_SHA="E0C6706B030775C9731CF3FC3A055CAE88512CF470BF2D6BFABDACD7F2F5F694"',
            'PERSISTENT_RUNTIME_SHA="F400FE8FDA673CA6976B698365A591CEC3A373C4284721A39AEF935DF16C5A31"',
            'APP_MAIN_SHA="C34A0F457B2242EDE138DD0B6DC1B08B860515F7BD2FADB7DF8F2B86A3F5ED31"',
            'SYSTEMD_NOTIFY_SHA="649EA2EABBD6B18C5E489D2059D08020D64914C47B15E50EA2873AEEFA99A8A3"',
            'SETTINGS_SHA="1DB81553DBCBF4DAFC710EFDD69C2DB0CC1A869F0754D7BB67C7ADFA3DCAC631"',
            'ROLLBACK_TTL_SECONDS="240"',
            'TELEGRAM_EXPECTED_BOT_USERNAME=NeobyatnayaAMNZ_bot',
            'TELEGRAM_ADMISSION_TIMEOUT_SECONDS=30',
            'TELEGRAM_POLLING_TIMEOUT_SECONDS=20',
            'TELEGRAM_RUNTIME_LOCK_PATH=/run/amn2-bot/polling.lock',
        }
        for marker in sorted(required):
            self.assertIn(marker, script)

    def test_remote_allows_only_resolved_executable_venv_interpreter_target(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        self.assertIn("require_executable_file()", script)
        self.assertIn('readlink -f -- "$path"', script)
        self.assertIn('require_executable_file "$PYTHON_BIN"', script)
        self.assertNotIn('require_regular_file "$PYTHON_BIN"', script)

    def test_remote_exposes_only_the_reviewed_modes(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        dispatch = script.split('case "$MODE" in', 1)[1]

        self.assertRegex(dispatch, r"preflight\)\s+preflight\s+;;")
        self.assertRegex(dispatch, r"stage\)\s+stage_activation\s+;;")
        self.assertRegex(dispatch, r"accept\)\s+accept_activation\s+;;")
        self.assertRegex(dispatch, r"postflight\)\s+postflight\s+;;")
        self.assertNotRegex(dispatch, r"\b(?:apply|upload|rollback|enable)\)")

    def test_remote_orders_disabled_first_stage_and_exact_confirmed_enable(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        stage = script.split("stage_activation() {", 1)[1].split(
            "accept_activation() {", 1
        )[0]
        accept = script.split("accept_activation() {", 1)[1].split(
            "postflight() {", 1
        )[0]

        self.assertIn('systemctl is-enabled "$BOT_UNIT"', stage)
        self.assertIn('systemctl start "$BOT_UNIT"', stage)
        self.assertNotIn('systemctl enable "$BOT_UNIT"', stage)
        self.assertIn('arm_automatic_rollback "$STATE_ROOT"', stage)
        self.assertIn('awaiting_admin_start=true', stage)

        confirmation_check = (
            '[ "$CONFIRMATION" = "$EXPECTED_CONFIRMATION" ] '
            '|| die "exact wide-header confirmation mismatch"'
        )
        self.assertIn(confirmation_check, accept)
        self.assertIn('verify_first_admin_delta "$STATE_ROOT"', accept)
        self.assertIn('cancel_automatic_rollback "$STATE_ROOT"', accept)
        self.assertIn('systemctl enable "$BOT_UNIT"', accept)
        self.assertLess(accept.index(confirmation_check), accept.index("systemctl enable"))
        self.assertLess(
            accept.index('verify_first_admin_delta "$STATE_ROOT"'),
            accept.index("systemctl enable"),
        )

    def test_remote_uses_safe_root_only_state_and_bounded_autorollback(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")

        self.assertIn('STATE_BASE="/root/amn2-telegram-002b"', script)
        self.assertIn('[[ "$RUN_ID" =~ ^[0-9]{8}T[0-9]{6}Z$ ]]', script)
        self.assertIn('chmod 700 "$STATE_ROOT"', script)
        self.assertIn('rollback.sh', script)
        self.assertIn('chmod 700 "$STATE_ROOT/rollback.sh"', script)
        self.assertIn('--on-active="${ROLLBACK_TTL_SECONDS}s"', script)
        self.assertIn('rollback_timer_unit=', script)
        self.assertIn('unit.before', script)
        self.assertIn('env.before', script)
        self.assertIn('db-before.sqlite3', script)
        self.assertIn('db-before.snapshot', script)
        self.assertIn('awg-before.snapshot', script)

    def test_remote_never_blindly_restores_db_or_mutates_web_awg_or_telegram_profile(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        forbidden = [
            r"docker\s+(?:restart|stop|start|rm|kill|update)\b",
            r"(?:awg|wg)\s+set\b",
            r"setWebhook|deleteWebhook|drop_pending_updates",
            r"setChatPhoto|sendPhoto",
            r"sqlite3\s+.*(?:restore|\.restore)",
            r"cp\s+.*db-before.*amneziya\.sqlite3",
            r"systemctl\s+(?:start|stop|restart|enable|disable)\s+\"?\$WEB_UNIT",
        ]
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, script, flags=re.IGNORECASE), pattern)

        rollback = script.split("write_rollback_helper() {", 1)[1].split(
            "arm_automatic_rollback() {", 1
        )[0]
        self.assertNotIn("DB_PATH", rollback)
        self.assertNotIn("docker", rollback.lower())
        self.assertNotIn("AWG", rollback)

    def test_remote_requires_telegram_preflight_and_exact_admin_only_db_delta(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")

        self.assertIn("admit_persistent_bot", script)
        self.assertIn("get_webhook_info", script)
        self.assertIn("pending_update_count=0", script)
        self.assertIn("ownership_probe=empty", script)
        self.assertNotIn("offset=", script)
        self.assertIn("application_rows_excluding_first_admin_sha256", script)
        self.assertIn("first_admin_user_row_sha256", script)
        self.assertIn("first_admin_immutable_fields", script)
        self.assertIn("database_delta=first_admin_user_row_only", script)

    def test_remote_allows_only_plan_timestamp_bootstrap_then_freezes_staged_baseline(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        snapshot = script.split("write_db_application_snapshot() {", 1)[1].split(
            "verify_expected_startup_delta() {", 1
        )[0]
        startup = script.split("verify_expected_startup_delta() {", 1)[1].split(
            "verify_first_admin_delta() {", 1
        )[0]
        accept_delta = script.split("verify_first_admin_delta() {", 1)[1].split(
            "create_db_backup() {", 1
        )[0]
        stage = script.split("stage_activation() {", 1)[1].split(
            "accept_activation() {", 1
        )[0]

        normalized_hash = "application_rows_excluding_plan_updated_at_sha256"
        self.assertIn(normalized_hash, snapshot)
        self.assertIn('table == "plans" and key == "updated_at"', snapshot)
        self.assertIn(f'before["{normalized_hash}"]', startup)
        self.assertIn(f'current["{normalized_hash}"]', startup)
        self.assertIn('before["counts"] != current["counts"]', startup)
        self.assertIn('before["first_admin_user_row_sha256"]', startup)
        self.assertIn('current["first_admin_user_row_sha256"]', startup)
        self.assertIn('db-staged.application.json', startup)
        self.assertIn('db-staged.application.json', accept_delta)
        self.assertNotIn('db-before.application.json', accept_delta)
        self.assertIn('verify_expected_startup_delta "$STATE_ROOT"', stage)
        self.assertLess(
            stage.index('verify_expected_startup_delta "$STATE_ROOT"'),
            stage.index('printf \'staged\\n\''),
        )

    def test_remote_closes_timer_races_and_revalidates_runtime_before_enable(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        snapshot = script.split("snapshot_runtime_inputs() {", 1)[1].split(
            "install_runtime_contract() {", 1
        )[0]
        cancel = script.split("cancel_automatic_rollback() {", 1)[1].split(
            "snapshot_runtime_inputs() {", 1
        )[0]
        accept = script.split("accept_activation() {", 1)[1].split(
            "postflight() {", 1
        )[0]

        self.assertIn('[ "$fragment_path" = "$UNIT_FRAGMENT" ]', snapshot)
        self.assertIn('receipt="$state_root/rollback.receipt"', cancel)
        self.assertGreaterEqual(cancel.count('[ ! -e "$receipt" ]'), 3)
        self.assertIn('systemctl is-failed "$service_unit"', cancel)
        cancel_index = accept.index('cancel_automatic_rollback "$STATE_ROOT"')
        enable_index = accept.index('systemctl enable "$BOT_UNIT"')
        between = accept[cancel_index:enable_index]
        self.assertIn("unit_contract_check", between)
        self.assertIn("env_contract_check", between)

    def test_remote_arms_rollback_before_mutation_and_handles_session_signals(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        stage = script.split("stage_activation() {", 1)[1].split(
            "accept_activation() {", 1
        )[0]
        signal_handler = script.split("rollback_and_exit() {", 1)[1].split(
            "cancel_automatic_rollback() {", 1
        )[0]

        self.assertIn('trap \'rollback_and_exit 1\' ERR', stage)
        self.assertIn('trap \'rollback_and_exit 129\' HUP', stage)
        self.assertIn('trap \'rollback_and_exit 130\' INT', stage)
        self.assertIn('trap \'rollback_and_exit 143\' TERM', stage)
        self.assertIn("rollback_current_runtime || true", signal_handler)
        self.assertIn("trap - ERR HUP INT TERM", signal_handler)
        self.assertIn('exit "$exit_code"', signal_handler)
        self.assertLess(
            stage.index('arm_automatic_rollback "$STATE_ROOT"'),
            stage.index("install_runtime_contract"),
        )
        self.assertLess(
            stage.index('arm_automatic_rollback "$STATE_ROOT"'),
            stage.index('systemctl start "$BOT_UNIT"'),
        )
        self.assertIn("trap - ERR HUP INT TERM", stage)

    def test_current_live_approval_is_withheld_from_docs_until_origin_sync(self) -> None:
        runner = read_required(self, RUNNER, "PowerShell activation runner")
        approval_match = re.search(
            r'\$expectedApproval = "([^"]+)"',
            runner,
        )
        self.assertIsNotNone(approval_match)
        approval = approval_match.group(1)
        authority_docs = (
            REPO_ROOT
            / "research"
            / "amn2"
            / "phase-11-telegram-002b-staged-persistent-activation-gate-2026-07-17.md",
            REPO_ROOT / "docs" / "AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md",
            REPO_ROOT
            / "docs"
            / "NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md",
            REPO_ROOT / "docs" / "PROJECT_STATUS_CURRENT.ru.md",
        )

        for path in authority_docs:
            contents = read_required(self, path, "authority document")
            self.assertNotIn(approval, contents)
        self.assertIn(
            "phase11_telegram_002b_approval_phrase=WITHHELD_UNTIL_ORIGIN_SYNC",
            read_required(
                self,
                REPO_ROOT / "docs" / "PROJECT_STATUS_CURRENT.ru.md",
                "project status",
            ),
        )

    def test_remote_rejects_queued_or_running_rollback_service_states(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        cancel = script.split("cancel_automatic_rollback() {", 1)[1].split(
            "snapshot_runtime_inputs() {", 1
        )[0]

        self.assertIn('service_state="$(systemctl is-active "$service_unit"', cancel)
        self.assertRegex(cancel, r"case \"\$service_state\" in\s+inactive\|dead\)")
        self.assertIn("automatic rollback is already running", cancel)

    def test_remote_keeps_compensation_rollback_until_acceptance_is_committed(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        accept = script.split("accept_activation() {", 1)[1].split(
            "postflight() {", 1
        )[0]
        cancel_index = accept.index('cancel_automatic_rollback "$STATE_ROOT"')
        enable_index = accept.index('systemctl enable "$BOT_UNIT"')
        self.assertIn("rollback_and_exit 129", accept[:cancel_index])
        self.assertIn("rollback_and_exit 130", accept[:cancel_index])
        self.assertIn("rollback_and_exit 143", accept[:cancel_index])
        self.assertIn("rollback_and_exit", accept[:cancel_index])
        rollback = script.split("rollback_current_runtime() {", 1)[1].split(
            "cancel_automatic_rollback() {", 1
        )[0]
        self.assertIn("rollback.sh", rollback)
        self.assertIn("trap - ERR HUP INT TERM", accept)
        self.assertLess(cancel_index, enable_index)

    def test_remote_decodes_and_canonicalizes_confirmation_token(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        self.assertIn('CONFIRMATION_TOKEN="${3:-}"', script)
        self.assertIn("base64 --decode", script)
        self.assertIn("base64", script)
        self.assertIn('[ "$CONFIRMATION" = "$EXPECTED_CONFIRMATION" ]', script)

    def test_remote_sanitizes_telegram_probe_setup_failures(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        preflight = script.split("telegram_preflight() {", 1)[1].split(
            "telegram_postflight() {", 1
        )[0]
        postflight = script.split("telegram_postflight() {", 1)[1].split(
            "env_contract_check() {", 1
        )[0]

        for probe in (preflight, postflight):
            self.assertIn("bot = None", probe)
            self.assertLess(probe.index("try:"), probe.index("settings = Settings"))
            self.assertIn("if bot is not None:", probe)

    def test_remote_accepts_exact_single_line_journal_receipt_and_cleans_immediate_rollback_timer(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        journal = script.split("journal_contract_check() {", 1)[1].split(
            "preflight() {", 1
        )[0]
        stage = script.split("stage_activation() {", 1)[1].split(
            "accept_activation() {", 1
        )[0]

        self.assertIn("for attempt in $(seq 1 15)", journal)
        self.assertIn("sleep 1", journal)
        self.assertIn(
            'expected_receipt="telegram_persistent_admission=pass '
            'bot_identity=@${EXPECTED_BOT_USERNAME} webhook_configured=false '
            'pending_update_count=0 allowed_updates=message,callback_query"',
            journal,
        )
        self.assertIn('grep -Fxc -- "$expected_receipt" "$safe_log"', journal)
        self.assertNotIn("grep -c '^pending_update_count=0'", journal)
        self.assertNotIn("grep -c '^allowed_updates=message,callback_query'", journal)
        self.assertIn("rollback_current_runtime()", script)
        self.assertIn('systemctl stop "${timer_base}.timer"', script)
        self.assertIn("rollback_and_exit", stage)

    def test_remote_forces_unbuffered_python_before_journal_receipt_gate(self) -> None:
        script = read_required(self, REMOTE, "remote activation executor")
        env_check = script.split("env_contract_check() {", 1)[1].split(
            "update_env_contract() {", 1
        )[0]
        env_update = script.split("update_env_contract() {", 1)[1].split(
            "unit_contract_check() {", 1
        )[0]
        install = script.split("install_runtime_contract() {", 1)[1].split(
            "journal_contract_check() {", 1
        )[0]
        stage = script.split("stage_activation() {", 1)[1].split(
            "accept_activation() {", 1
        )[0]

        self.assertIn('ENV_PYTHONUNBUFFERED="PYTHONUNBUFFERED=1"', script)
        self.assertIn('"PYTHONUNBUFFERED": "1"', env_check)
        self.assertIn('"PYTHONUNBUFFERED": "1"', env_update)
        self.assertIn("update_env_contract", install)
        self.assertLess(
            stage.index("install_runtime_contract"),
            stage.index('systemctl start "$BOT_UNIT"'),
        )

    def test_runner_requires_literal_approval_before_private_bindings(self) -> None:
        script = read_required(self, RUNNER, "PowerShell activation runner")

        self.assertIn('[ValidateSet("preflight", "stage", "accept", "postflight")]', script)
        self.assertIn('[string]$Approval', script)
        approval_check = (
            "[string]::Equals($Approval, $expectedApproval, "
            "[StringComparison]::Ordinal)"
        )
        self.assertIn(approval_check, script)
        self.assertLess(script.index(approval_check), script.index("$sshDir ="))
        self.assertNotIn(".Contains($expectedApproval)", script)
        self.assertNotIn("-like", script)

    def test_runner_requires_accept_only_run_id_and_exact_confirmation(self) -> None:
        script = read_required(self, RUNNER, "PowerShell activation runner")

        self.assertIn('[string]$RunId = ""', script)
        self.assertIn('[string]$Confirmation = ""', script)
        self.assertIn("CONFIRM PHASE11_TELEGRAM_002B_FIRST_ADMIN_WIDE_HEADER_RESPONSE", script)
        self.assertIn("Safe run id required", script)
        self.assertIn("Exact acceptance confirmation mismatch", script)
        self.assertIn("Run id and confirmation are accept-only", script)
        self.assertIn("^[0-9]{8}T[0-9]{6}Z$", script)

    def test_runner_binds_and_transmits_the_same_remote_byte_array(self) -> None:
        remote = read_required(self, REMOTE, "remote activation executor")
        script = read_required(self, RUNNER, "PowerShell activation runner")
        remote_sha = hashlib.sha256(REMOTE.read_bytes()).hexdigest().upper()

        self.assertIn(f'$expectedRemoteScriptSha = "{remote_sha}"', script)
        self.assertIn(f"REMOTE_ORCHESTRATOR_SHA_{remote_sha}_0B858C5", script)
        self.assertEqual(script.count("[IO.File]::ReadAllBytes($remoteScript)"), 1)
        self.assertIn("ComputeHash($remoteScriptBytes)", script)
        self.assertIn("[byte[]]$StandardInputBytes = @()", script)
        self.assertIn("$process.StandardInput.BaseStream.Write(", script)
        self.assertIn("-StandardInputBytes $remoteScriptBytes", script)
        self.assertNotIn("Get-Content -LiteralPath $remoteScript -Raw", script)

    def test_runner_uses_absolute_trusted_openssh_and_redacts_target(self) -> None:
        script = read_required(self, RUNNER, "PowerShell activation runner")

        self.assertIn(
            '$trustedOpenSshDir = Join-Path $env:WINDIR "System32\\OpenSSH"',
            script,
        )
        self.assertIn('$sshExecutable = Join-Path $trustedOpenSshDir "ssh.exe"', script)
        self.assertIn("[IO.Path]::IsPathFullyQualified($FileName)", script)
        self.assertIn("Executable path is outside the trusted OpenSSH installation", script)
        self.assertIn('Invoke-CapturedProcess -FileName $sshExecutable', script)
        self.assertIn('-replace [regex]::Escape($target), "<target>"', script)
        self.assertNotIn('Invoke-CapturedProcess -FileName "ssh.exe"', script)

    def test_runner_uses_isolated_openssh_trust_sources(self) -> None:
        script = read_required(self, RUNNER, "PowerShell activation runner")
        self.assertIn('"-F", "none"', script)
        self.assertIn('"-o", "GlobalKnownHostsFile=none"', script)
        self.assertIn('"-o", "KnownHostsCommand=none"', script)

    def test_runner_transports_confirmation_as_base64_and_consumes_stage_approval(self) -> None:
        script = read_required(self, RUNNER, "PowerShell activation runner")
        self.assertIn("$confirmationToken", script)
        self.assertIn("Convert]::ToBase64String", script)
        self.assertNotIn("$sshArguments += @($RunId, $Confirmation)", script)
        self.assertIn("FileMode]::CreateNew", script)
        self.assertIn("stage-consumed", script)
        self.assertIn("Stage approval receipt missing", script)


if __name__ == "__main__":
    unittest.main()
