import hashlib
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REMOTE = ROOT / "scripts" / "vps" / "post_release_spain_readonly_preflight_remote.sh"
RUNNER = ROOT / "scripts" / "vps" / "post_release_spain_readonly_preflight_ssh_runner.ps1"
DOC = ROOT / "docs" / "POST_RELEASE_SPAIN_READONLY_PREFLIGHT_GATE.ru.md"
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")


def extract_bash_function(source: str, name: str) -> str:
    match = re.search(rf"(?ms)^{re.escape(name)}\(\) \{{\n.*?^\}}\n", source)
    if match is None:
        raise AssertionError(f"missing Bash function: {name}")
    return match.group(0)


def extract_powershell_function(source: str, name: str) -> str:
    match = re.search(rf"(?ms)^function {re.escape(name)}\([^\n]*\) \{{\n.*?^\}}\n", source)
    if match is None:
        raise AssertionError(f"missing PowerShell function: {name}")
    return match.group(0)


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

    def test_mandatory_collectors_and_cgroup_reads_fail_closed(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        self.assertIn('else\n    exit 68\nfi', source)
        self.assertIn('else\n    exit 69\nfi', source)
        self.assertIn('target="$(readlink "$fd")" || return 1', source)
        self.assertIn('[[ -r "$cgroup_file" ]] || return 1', source)
        self.assertIn('[[ -r "$socket_table" ]] || return 1', source)
        self.assertNotIn('readlink "$fd")" || continue', source)

    @unittest.skipUnless(BASH.exists(), "Git Bash is required")
    def test_exact_target_allowlists_exclude_only_deployment_owned_resources(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        functions = extract_bash_function(source, "is_target_container") + extract_bash_function(source, "is_target_unit")
        harness = functions + r'''
for name in amnezia-awg2 amnezia-awg2-shadow resident-proxy; do
    if is_target_container "$name"; then printf 'container:%s:target\n' "$name"; else printf 'container:%s:retain\n' "$name"; fi
done
for name in amneziya-web.service amneziya-bot.service amneziya-web.service.backup resident.service; do
    if is_target_unit "$name"; then printf 'unit:%s:target\n' "$name"; else printf 'unit:%s:retain\n' "$name"; fi
done
'''
        result = subprocess.run([str(BASH), "-c", harness], capture_output=True, text=True, timeout=10, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "container:amnezia-awg2:target",
                "container:amnezia-awg2-shadow:retain",
                "container:resident-proxy:retain",
                "unit:amneziya-web.service:target",
                "unit:amneziya-bot.service:target",
                "unit:amneziya-web.service.backup:retain",
                "unit:resident.service:retain",
            ],
        )
        self.assertGreaterEqual(source.count('is_target_container "$container_name" && continue'), 1)
        self.assertGreaterEqual(source.count('is_target_unit "$unit_name" && continue'), 1)

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
        self.assertNotIn("if (Test-Path -LiteralPath $EvidencePath)", source)
        self.assertNotIn("[IO.File]::WriteAllText($EvidencePath", source)
        self.assertIn("[IO.FileMode]::CreateNew", source)
        self.assertIn("[IO.FileShare]::None", source)
        self.assertLess(source.index("Write-EvidenceCreateNew $EvidencePath"), source.index("Protect-PrivatePath $EvidencePath"))
        self.assertLess(source.index("Protect-PrivatePath $EvidencePath"), source.index("Assert-PrivatePath $EvidencePath"))

    def test_atomic_evidence_writer_never_replaces_existing_bytes(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        writer = extract_powershell_function(source, "Write-EvidenceCreateNew")
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            harness_path = tmp / "atomic-writer-test.ps1"
            evidence_path = tmp / "evidence.json"
            harness_path.write_text(
                writer
                + '\nWrite-EvidenceCreateNew $args[0] \'{"first":true}\'\n'
                + '$secondFailed = $false\n'
                + 'try { Write-EvidenceCreateNew $args[0] \'{"second":true}\' } catch { $secondFailed = $true }\n'
                + 'if (-not $secondFailed) { throw "second create unexpectedly succeeded" }\n'
                + 'Write-Output ([IO.File]::ReadAllText($args[0]))\n',
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    str(POWERSHELL),
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(harness_path),
                    str(evidence_path),
                ],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), '{"first":true}')
            self.assertEqual(evidence_path.read_text(encoding="utf-8"), '{"first":true}\n')

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
        self.assertIn(
            "SOURCE_F43737BDDBA353F3BFF1BA9D5AB6CB5FE1AA463E",
            approval.group(1),
        )
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
