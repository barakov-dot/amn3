import hashlib
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REMOTE = ROOT / "scripts" / "vps" / "post_release_spain_readonly_preflight_remote.sh"
RUNNER = ROOT / "scripts" / "vps" / "post_release_spain_readonly_preflight_ssh_runner.ps1"
DOC = ROOT / "docs" / "POST_RELEASE_SPAIN_READONLY_PREFLIGHT_GATE.ru.md"
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")


class SpainReadonlyPreflightStaticTests(unittest.TestCase):
    def test_remote_probe_is_normalized_read_only_inventory(self) -> None:
        self.assertTrue(REMOTE.exists(), "read-only Spain remote probe is missing")
        source = REMOTE.read_text(encoding="utf-8")
        for marker in (
            "set -euo pipefail",
            'readonly MODE="${1:-}"',
            '[[ "$MODE" == "preflight" ]]',
            '"schema":"amn2.spain-readonly-preflight.v1"',
            '"os_kernel"',
            '"capacity"',
            '"listening_sockets"',
            '"docker"',
            '"systemd"',
            '"firewall"',
            '"ssh_effective_policy"',
            '"clock"',
            '"package_presence"',
            '"unrelated_service_fingerprint"',
            '"name_sha256"',
            '"image_or_unit_sha256"',
            '"active_state"',
            '"restart_count"',
            '"bound_port_set"',
            "{{.RestartCount}}",
            '--property=NRestarts --value',
            'systemctl cat "$unit_name" --no-pager',
            '--property=ControlGroup --value',
            '/sys/fs/cgroup',
            '/cgroup.procs',
            '/proc/$pid/net/tcp',
            'unit_content_status',
            'bound_port_status',
        ):
            self.assertIn(marker, source)

        lowered = source.casefold()
        forbidden = (
            r"\bsystemctl\s+(?:stop|restart|enable|disable|start|mask|unmask)\b",
            r"\bdocker\s+(?:stop|restart|rm|kill|exec|run|compose)\b",
            r"\b(?:apt|apt-get|dnf|yum|apk|pacman|zypper)\s+(?:install|update|upgrade|remove)\b",
            r"\b(?:iptables|ip6tables|nft|ufw|firewall-cmd)\s+(?:-[afidrx]|--add|--remove|enable|disable|reset|reload)\b",
            r"\b(?:curl|wget|telegram|sendmessage)\b",
            r"\b(?:wg|awg|wg-quick)\s+(?:set|setconf|addconf|syncconf|up|down)\b",
            r"(?m)^\s*(?:printenv|env)\b",
            r"(?:^|\s)(?:cat|sed|awk)\s+[^\n]*(?:\.env|/etc/ssh/sshd_config|\.conf)\b",
            r"(?m)(?:^|\s)[0-9]*>>?\s*(?!&)(?:/|[\"'$a-z._])",
            r"\btee\b",
        )
        for pattern in forbidden:
            self.assertNotRegex(lowered, pattern)

        self.assertNotRegex(source, r"(?i)\b(?:password|passwd|token|private[_-]?key|secret|credential)s?\b")
        self.assertNotIn("ss -H -lntup", source)
        self.assertNotIn(" /proc/net/tcp ", source)
        self.assertIn('unit_content="$(systemctl cat "$unit_name" --no-pager)"', source)
        self.assertNotIn('if unit_content="$(systemctl cat', source)
        self.assertIn('|exact|$bound_port_status', source)
        self.assertIn('"unit_content_status":"%s"', source)
        self.assertIn('bound_port_status="cgroup_complete"', source)
        self.assertNotRegex(lowered, r"docker\s+inspect(?!\s+--format\s+'\{\{\.restartcount\}\}')")
        self.assertNotIn("2>&1", source)
        self.assertNotIn("|| true", source)

    def test_runner_reuses_task7_trust_state_and_checks_it_before_ssh(self) -> None:
        self.assertTrue(RUNNER.exists(), "Spain preflight SSH runner is missing")
        source = RUNNER.read_text(encoding="utf-8")
        for marker in (
            '[ValidateSet("preflight")]',
            '[string]$Approval',
            '[string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)',
            'Get-FileHash -InputStream $RemoteScriptStream -Algorithm SHA256',
            '[IO.FileShare]::Read',
            '$RemoteReader.ReadToEnd()',
            'target.env',
            'id_ed25519_spain',
            'known_hosts_spain',
            'TARGET_HOST',
            'TARGET_USER',
            'SSH_KEY_PATH',
            'EXPECTED_HOST_KEY_SHA256',
            r'C:\Windows\System32\OpenSSH\ssh.exe',
            r'C:\Windows\System32\OpenSSH\ssh-keygen.exe',
            '"-F", "none"',
            '"BatchMode=yes"',
            '"IdentitiesOnly=yes"',
            '"StrictHostKeyChecking=yes"',
            '"UserKnownHostsFile=$KnownHostsPath"',
            '"-i", $KeyPath',
            '"-p", "22"',
            'ConvertFrom-Json',
            'preflight-evidence.json',
            'SetAccessRuleProtection($true, $false)',
            'Protect-PrivatePath $EvidencePath',
        ):
            self.assertIn(marker, source)

        approval_check = '[string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)'
        self.assertLess(source.index(approval_check), source.index("Get-FileHash -InputStream $RemoteScriptStream"))
        self.assertLess(source.index("Get-FileHash -InputStream $RemoteScriptStream"), source.index("Read-Binding"))
        self.assertLess(source.rindex("\nAssert-VerifiedHostPin $Binding\n"), source.index("& $SshExe"))
        self.assertLess(source.rindex("\nAssert-DedicatedKeyPair\n"), source.index("& $SshExe"))
        self.assertRegex(source, r'\$expectedRemoteScriptSha\s*=\s*"[A-F0-9]{64}"')
        self.assertNotRegex(source, r"(?i)password|sshpass|plink|putty|accept-new|stricthostkeychecking=no")
        self.assertNotIn("known_hosts\"", source)
        self.assertNotIn('id_ed25519"', source)
        self.assertNotIn("Invoke-Expression", source)
        self.assertNotIn("[IO.File]::ReadAllText($RemoteScriptPath", source)
        self.assertIn("& $SshExe @SshArguments 2>$null", source)
        self.assertNotIn("& $SshExe @SshArguments 2>&1", source)
        self.assertGreaterEqual(source.count("$SshOutput = $null"), 2)
        no_overwrite = "if (Test-Path -LiteralPath $EvidencePath)"
        self.assertIn(no_overwrite, source)
        self.assertLess(source.index(no_overwrite), source.index("& $SshExe"))
        self.assertLess(source.index("[IO.File]::WriteAllText($EvidencePath"), source.index("Protect-PrivatePath $EvidencePath"))
        self.assertLess(source.index("Protect-PrivatePath $EvidencePath"), source.index("Assert-PrivatePath $EvidencePath"))

    def test_embedded_remote_checksum_matches_exact_bytes(self) -> None:
        self.assertTrue(REMOTE.exists())
        self.assertTrue(RUNNER.exists())
        source = RUNNER.read_text(encoding="utf-8")
        match = re.search(r'\$expectedRemoteScriptSha\s*=\s*"([A-F0-9]{64})"', source)
        self.assertIsNotNone(match)
        actual = hashlib.sha256(REMOTE.read_bytes()).hexdigest().upper()
        self.assertEqual(match.group(1), actual)
        approval = re.search(r'\$expectedApproval\s*=\s*"([^"]+)"', source)
        self.assertIsNotNone(approval)
        self.assertIn(actual, approval.group(1))
        self.assertNotRegex(approval.group(1), r"\$\{|<|>|PLACEHOLDER|TBD")

    def test_runbook_keeps_preflight_separate_and_withholds_execution(self) -> None:
        self.assertTrue(DOC.exists(), "Spain preflight gate runbook is missing")
        doc = DOC.read_text(encoding="utf-8")
        for marker in (
            "read-only",
            "Task 7",
            "id_ed25519_spain",
            "known_hosts_spain",
            "точного approval",
            "не выполнялся",
            "не устанавливает",
            "не изменяет",
            "unrelated_service_fingerprint",
        ):
            self.assertIn(marker, doc)
        self.assertNotRegex(doc, r"(?i)\b(?:password|token|secret|private key)\s*[:=]")


@unittest.skipUnless(POWERSHELL.exists(), "Windows PowerShell is required")
class SpainReadonlyPreflightFailClosedTests(unittest.TestCase):
    def test_missing_approval_fails_before_artifact_or_network_access(self) -> None:
        result = subprocess.run(
            [
                str(POWERSHELL),
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(RUNNER),
                "-Mode",
                "preflight",
                "-RunId",
                "test-run",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Exact read-only preflight approval mismatch", result.stderr)
        combined = result.stdout + result.stderr
        self.assertNotIn("ssh.exe", combined.casefold())
        self.assertNotIn("target.env", combined)


if __name__ == "__main__":
    unittest.main()
