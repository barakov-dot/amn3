import hashlib
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REMOTE = REPO_ROOT / "scripts" / "vps" / "phase11_0b858c5_combined_remote_rollout.sh"
RUNNER = REPO_ROOT / "scripts" / "vps" / "phase11_0b858c5_combined_ssh_runner.ps1"


class Phase110b858c5RolloutExecutorTests(unittest.TestCase):
    def test_remote_executor_is_exactly_bound_and_fail_closed(self) -> None:
        self.assertTrue(REMOTE.exists(), "remote rollout executor is missing")
        script = REMOTE.read_text(encoding="utf-8")

        required = {
            'EXPECTED_OVERLAY="801f8c3"',
            'CANDIDATE_COMMIT="0b858c5"',
            'PACKAGE_SHA="7866BDD9FEBE1D6EEA701B37A6E4206A8267766A56993F3C02A0C7B30C394B54"',
            'SOURCE_SHA="E03F13FD6A7BB5CBC5FCEE7179F395EA8C2864EBCEAB01BC351C5904F3CFF975"',
            'APPLY_SHA="016403379F46BA6024B0570B9EC7E757EC9055297B4B89794B871EE80C706314"',
            'RUNBOOK_SHA="1483870B8C0A1DDAAA5C2B4A69FD2650B970C95BD70654FF54FEAEF602303F8A"',
            'SOURCE_FULL_COMMIT="0b858c5cdbc5b565cc265966a2edfe2d339d65e0"',
            'SOURCE_ENTRY_COUNT="383"',
            'CANONICAL_LOGO_SHA="40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791"',
            'LANGUAGE_HEADER_SHA="BBDDFA72D1D1FC37E412D2F4A9B4124001FF91FBD641635E31A47E008FC4611F"',
            'VPS_APPLY_ENABLED=false',
            'OPERATOR_DEVICE_CREATE_ENABLED=false',
            'PIP_NO_INDEX=1',
            'ROLLBACK_ARMED=1',
            'trap on_error ERR',
            'mkdir -m 700 "$CANDIDATE_ROOT" "$ROLLBACK_ROOT"',
            'source-before.tar.gz',
            'overlay-before.txt',
            'db-before.sqlite3',
            'awg-before.snapshot',
            'bot-unit-env-before.snapshot',
            'rm -f -- "$AMN2_DIR/app/web/static/brand-full.jpg"',
            'source_delta_exact=true',
            'telegram_profile_photo=unchanged',
        }
        for marker in sorted(required):
            self.assertIn(marker, script)

        self.assertRegex(script, r'case "\$MODE" in\s+preflight\)')
        self.assertIn('postflight) EXPECTED_OVERLAY="$CANDIDATE_COMMIT"; preflight', script)

    def test_remote_executor_never_mutates_awg_or_activates_bot(self) -> None:
        self.assertTrue(REMOTE.exists(), "remote rollout executor is missing")
        script = REMOTE.read_text(encoding="utf-8")

        forbidden = [
            r"docker\s+(?:restart|stop|start|rm|kill|update)\b",
            r"systemctl\s+(?:start|restart|enable|disable|stop)\s+\"?\$BOT_UNIT",
            r"awg\s+set\b",
            r"wg\s+set\b",
            r"getUpdates",
            r"sendMessage",
            r"setWebhook",
            r"setChatPhoto",
        ]
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, script, flags=re.IGNORECASE), pattern)

        service_mutations = re.findall(
            r"systemctl\s+(?:start|stop|restart|enable|disable)\s+([^\s]+)",
            script,
        )
        self.assertTrue(service_mutations)
        self.assertEqual(set(service_mutations), {'"$WEB_UNIT"'})

    def test_rollback_reverifies_database_snapshot_after_restore(self) -> None:
        self.assertTrue(REMOTE.exists(), "remote rollout executor is missing")
        script = REMOTE.read_text(encoding="utf-8")
        rollback = script.split("rollback() {", 1)[1].split("on_error() {", 1)[0]

        self.assertIn(
            '[ "$(db_snapshot 2>/dev/null)" = "$(cat '
            '"$ROLLBACK_ROOT/db-before.snapshot")" ] || rollback_status="failed"',
            rollback,
        )

    def test_runner_uploads_only_the_bound_package_and_checksum(self) -> None:
        self.assertTrue(RUNNER.exists(), "PowerShell SSH runner is missing")
        script = RUNNER.read_text(encoding="utf-8")

        self.assertIn('[ValidateSet("preflight", "postflight", "upload", "apply")]', script)
        self.assertIn('phase11_0b858c5_combined_remote_rollout.sh', script)
        self.assertIn('dist\\amn2-combined-overlay-0b858c5.zip', script)
        self.assertIn('dist\\amn2-combined-overlay-0b858c5.zip.sha256.txt', script)
        self.assertIn('StrictHostKeyChecking=yes', script)
        self.assertIn('BatchMode=yes', script)
        self.assertIn('IdentitiesOnly=yes', script)
        self.assertIn('chmod 600 /root/amn2-combined-overlay-0b858c5.zip /root/amn2-combined-overlay-0b858c5.zip.sha256.txt', script)
        self.assertIn('-replace [regex]::Escape($target), "<target>"', script)

    def test_runner_binds_remote_executor_bytes_to_reviewed_sha(self) -> None:
        self.assertTrue(REMOTE.exists(), "remote rollout executor is missing")
        self.assertTrue(RUNNER.exists(), "PowerShell SSH runner is missing")
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

    def test_runner_hashes_and_transmits_the_same_byte_array(self) -> None:
        self.assertTrue(RUNNER.exists(), "PowerShell SSH runner is missing")
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

    def test_runner_requires_literal_exact_approval_before_any_remote_action(self) -> None:
        self.assertTrue(RUNNER.exists(), "PowerShell SSH runner is missing")
        script = RUNNER.read_text(encoding="utf-8")
        approval = (
            "APPROVE PHASE11_0B858C5_"
            "REMOTE_ORCHESTRATOR_SHA_A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72_"
            "TRUSTED_OPENSSH_ABSOLUTE_PATH_BOUND_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_"
            "AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_"
            "OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_"
            "TELEGRAM_PROFILE_UNCHANGED_AND_AWG_UNTOUCHED"
        )
        superseded_approval = (
            "APPROVE PHASE11_0B858C5_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_"
            "AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_"
            "OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_"
            "TELEGRAM_PROFILE_UNCHANGED_AND_AWG_UNTOUCHED"
        )

        self.assertIn('[string]$Approval', script)
        self.assertIn(f'$expectedApproval = "{approval}"', script)
        self.assertNotIn(f'$expectedApproval = "{superseded_approval}"', script)
        equality = (
            "[string]::Equals($Approval, $expectedApproval, "
            "[StringComparison]::Ordinal)"
        )
        self.assertIn(equality, script)
        self.assertLess(script.index(equality), script.index('$sshDir ='))
        self.assertNotIn(".Contains($expectedApproval)", script)
        self.assertNotIn("-like", script)

    def test_runner_binds_ssh_and_scp_to_trusted_absolute_openSSH_paths(self) -> None:
        self.assertTrue(RUNNER.exists(), "PowerShell SSH runner is missing")
        script = RUNNER.read_text(encoding="utf-8")

        self.assertIn(
            '$trustedOpenSshDir = Join-Path $env:WINDIR "System32\\OpenSSH"',
            script,
        )
        self.assertIn(
            '$sshExecutable = Join-Path $trustedOpenSshDir "ssh.exe"',
            script,
        )
        self.assertIn(
            '$scpExecutable = Join-Path $trustedOpenSshDir "scp.exe"',
            script,
        )
        self.assertIn('Test-Path -LiteralPath $sshExecutable -PathType Leaf', script)
        self.assertIn('Test-Path -LiteralPath $scpExecutable -PathType Leaf', script)
        self.assertIn('Invoke-CapturedProcess -FileName $scpExecutable', script)
        self.assertIn('Invoke-CapturedProcess -FileName $sshExecutable', script)
        self.assertNotIn('Invoke-CapturedProcess -FileName "scp.exe"', script)
        self.assertNotIn('Invoke-CapturedProcess -FileName "ssh.exe"', script)

    def test_runner_rejects_non_absolute_or_non_OpenSSH_process_paths(self) -> None:
        self.assertTrue(RUNNER.exists(), "PowerShell SSH runner is missing")
        script = RUNNER.read_text(encoding="utf-8")

        self.assertIn(
            'if (-not [IO.Path]::IsPathFullyQualified($FileName))',
            script,
        )
        self.assertIn(
            'Executable path must be absolute',
            script,
        )
        self.assertIn(
            'Executable path is outside the trusted OpenSSH installation',
            script,
        )


if __name__ == "__main__":
    unittest.main()
