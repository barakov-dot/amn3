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


def run_bash_harness(source: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(BASH), "-c", source],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


class SpainReadonlyPreflightStaticTests(unittest.TestCase):
    def test_remote_probe_is_normalized_read_only_inventory(self) -> None:
        self.assertTrue(REMOTE.exists(), "read-only Spain remote probe is missing")
        source = REMOTE.read_text(encoding="utf-8")
        for marker in (
            "set -Eeuo pipefail",
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
        forbidden_source = lowered.replace("nft list ruleset 2>/dev/null", "nft list ruleset")
        for pattern in forbidden:
            self.assertNotRegex(forbidden_source, pattern)

        self.assertNotRegex(source, r"(?i)\b(?:password|passwd|token|private[_-]?key|secret|credential)s?\b")
        self.assertNotIn("ss -H -lntup", source)
        self.assertNotIn(" /proc/net/tcp ", source)
        self.assertIn('unit_content="$(systemctl cat "$unit_name" --no-pager)"', source)
        self.assertNotIn('if unit_content="$(systemctl cat', source)
        self.assertIn('|exact|$bound_port_status', source)
        self.assertIn('"unit_content_status":"%s"', source)
        self.assertIn('RESOLVED_BOUND_PORT_STATUS="cgroup_complete"', source)
        self.assertNotRegex(lowered, r"docker\s+inspect(?!\s+--format\s+'\{\{\.restartcount\}\}')")
        self.assertNotIn("2>&1", source)
        self.assertNotIn("|| true", source)
        self.assertIn('firewall_view="$(nft list ruleset 2>/dev/null)"', source)
        self.assertNotIn('firewall_view="$(nft list ruleset)"', source)

    def test_mandatory_collectors_and_cgroup_reads_fail_closed(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        for exit_code in (65, 66, 68, 69, 70, 71, 72, 73):
            self.assertIn(f"emit_failure {exit_code}", source)
            self.assertNotRegex(source, rf"(?m)^\s*exit {exit_code}$")
        self.assertIn('target="$(readlink "$fd")" || return 1', source)
        self.assertIn('[[ -r "$cgroup_file" ]] || return 1', source)
        self.assertIn('[[ -r "$socket_table" ]] || return 1', source)
        self.assertNotIn('readlink "$fd")" || continue', source)

    @unittest.skipUnless(BASH.exists(), "Git Bash is required")
    def test_proc_cgroup_parser_accepts_one_v2_or_systemd_v1_path_and_rejects_unsafe_input(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        functions = extract_bash_function(source, "safe_cgroup_path") + extract_bash_function(
            source, "parse_proc_cgroup_path"
        )
        harness = functions + r'''
[[ "$(parse_proc_cgroup_path $'0::/system.slice/demo.service\n')" == "/system.slice/demo.service" ]] || exit 10
[[ "$(parse_proc_cgroup_path $'2:cpu:/legacy\n1:name=systemd:/system.slice/legacy.service\n')" == "/system.slice/legacy.service" ]] || exit 11
for bad in $'0::/ok\n0::/duplicate\n' $'1:cpu:/not-systemd\n' $'0::/../../escape\n'; do
    if parse_proc_cgroup_path "$bad" >/dev/null 2>&1; then exit 12; fi
done
'''
        result = run_bash_harness(harness)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(BASH.exists(), "Git Bash is required")
    def test_unit_cgroup_resolver_distinguishes_active_exited_and_live_mainpid(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        functions = "".join(
            extract_bash_function(source, name)
            for name in (
                "emit_failure",
                "safe_cgroup_path",
                "parse_proc_cgroup_path",
                "read_proc_starttime",
                "resolve_unit_cgroup",
            )
        )
        with tempfile.TemporaryDirectory() as raw_tmp:
            proc_root = Path(raw_tmp)
            (proc_root / "321").mkdir()
            (proc_root / "321" / "cgroup").write_text(
                "0::/system.slice/live.service\n", encoding="utf-8"
            )
            (proc_root / "321" / "stat").write_text(
                "321 (live worker) S 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 424242 20\n",
                encoding="utf-8",
            )
            proc_root_bash = str(proc_root).replace("\\", "/")
            harness = functions + rf'''
systemctl() {{
    if [[ "$*" == *"ControlGroup"* ]]; then printf '\n';
    elif [[ "$*" == *"MainPID"* && "$1" == "show" && "$2" == "exited.service" ]]; then printf '0\n';
    elif [[ "$*" == *"MainPID"* ]]; then printf '321\n';
    elif [[ "$*" == *"Id"* ]]; then printf 'live.service\n';
    else return 90; fi
}}
resolve_unit_cgroup exited.service active '{proc_root_bash}'
[[ "$RESOLVED_BOUND_PORT_STATUS|$RESOLVED_CONTROL_GROUP" == "active_exited_no_live_process|" ]] || exit 20
resolve_unit_cgroup live.service active '{proc_root_bash}'
[[ "$RESOLVED_BOUND_PORT_STATUS|$RESOLVED_CONTROL_GROUP" == "mainpid_cgroup_complete|/system.slice/live.service" ]] || exit 21
'''
            result = run_bash_harness(harness)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(BASH.exists(), "Git Bash is required")
    def test_mainpid_fallback_rejects_process_identity_change(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        functions = "".join(
            extract_bash_function(source, name)
            for name in (
                "emit_failure",
                "safe_cgroup_path",
                "parse_proc_cgroup_path",
                "read_proc_starttime",
                "resolve_unit_cgroup",
            )
        )
        with tempfile.TemporaryDirectory() as raw_tmp:
            proc_root = Path(raw_tmp)
            (proc_root / "321").mkdir()
            (proc_root / "321" / "cgroup").write_text(
                "0::/system.slice/demo.service\n", encoding="utf-8"
            )
            (proc_root / "321" / "stat").write_text(
                "321 (replacement) S 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 999999 20\n",
                encoding="utf-8",
            )
            proc_root_bash = str(proc_root).replace("\\", "/")
            counter_file = proc_root / "mainpid-reads"
            counter_file.write_text("0\n", encoding="utf-8")
            counter_file_bash = str(counter_file).replace("\\", "/")
            harness = functions + rf'''
systemctl() {{
    if [[ "$*" == *"ControlGroup"* ]]; then printf '\n';
    elif [[ "$*" == *"MainPID"* ]]; then
        mainpid_reads="$(<'{counter_file_bash}')"
        ((mainpid_reads += 1))
        printf '%s\n' "$mainpid_reads" > '{counter_file_bash}'
        if (( mainpid_reads == 1 )); then printf '321\n'; else printf '654\n'; fi
    elif [[ "$*" == *"Id"* ]]; then printf 'demo.service\n';
    else return 90; fi
}}
resolve_unit_cgroup demo.service active '{proc_root_bash}'
'''
            result = run_bash_harness(harness)
        self.assertEqual(result.returncode, 74, result.stderr)
        self.assertNotIn("mainpid_cgroup_complete", result.stdout)

    @unittest.skipUnless(BASH.exists(), "Git Bash is required")
    def test_mainpid_fallback_rejects_cgroup_from_another_unit(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        functions = "".join(
            extract_bash_function(source, name)
            for name in (
                "emit_failure",
                "safe_cgroup_path",
                "parse_proc_cgroup_path",
                "read_proc_starttime",
                "resolve_unit_cgroup",
            )
        )
        with tempfile.TemporaryDirectory() as raw_tmp:
            proc_root = Path(raw_tmp)
            (proc_root / "321").mkdir()
            (proc_root / "321" / "cgroup").write_text(
                "0::/system.slice/unrelated.service\n", encoding="utf-8"
            )
            (proc_root / "321" / "stat").write_text(
                "321 (unrelated) S 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 777777 20\n",
                encoding="utf-8",
            )
            proc_root_bash = str(proc_root).replace("\\", "/")
            harness = functions + rf'''
systemctl() {{
    if [[ "$*" == *"ControlGroup"* ]]; then printf '\n';
    elif [[ "$*" == *"MainPID"* ]]; then printf '321\n';
    elif [[ "$*" == *"Id"* ]]; then printf 'demo.service\n';
    else return 90; fi
}}
resolve_unit_cgroup demo.service active '{proc_root_bash}'
'''
            result = run_bash_harness(harness)
        self.assertEqual(result.returncode, 74, result.stderr)
        self.assertNotIn("mainpid_cgroup_complete", result.stdout)

    def test_mainpid_fallback_is_fail_closed_and_raw_free(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        for code in (71, 72, 73, 74):
            self.assertIn(f"emit_failure {code}", source)
            self.assertNotRegex(source, rf"(?m)^\s*exit {code}$")
        self.assertNotIn('printf "$main_pid"', source)
        self.assertNotIn('printf "$proc_cgroup_text"', source)
        self.assertNotIn('resolution="$(resolve_unit_cgroup', source)

    @unittest.skipUnless(BASH.exists(), "Git Bash is required")
    def test_remote_failure_envelope_is_allowlisted_and_raw_free(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        emitter = extract_bash_function(source, "emit_failure")
        harness = (
            "set -Eeuo pipefail\n"
            + emitter
            + '\nCURRENT_STAGE="firewall"\nemit_failure 23\n'
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

    @unittest.skipUnless(BASH.exists(), "Git Bash is required")
    def test_remote_failure_envelope_normalizes_unknown_stage(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        emitter = extract_bash_function(source, "emit_failure")
        harness = (
            "set -Eeuo pipefail\n"
            + emitter
            + '\nCURRENT_STAGE="private:target:value"\nemit_failure 17\n'
        )
        result = subprocess.run(
            [str(BASH), "-c", harness],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 17)
        self.assertEqual(
            result.stdout.strip(),
            "AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=bootstrap|exit=17",
        )
        self.assertNotIn("private", result.stdout)

    @unittest.skipUnless(BASH.exists(), "Git Bash is required")
    def test_remote_err_trap_emits_one_external_envelope_for_substitution_failure(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        emitter = extract_bash_function(source, "emit_failure")
        harness = (
            "set -Eeuo pipefail\n"
            + emitter
            + '\ntrap \'emit_failure "$?"\' ERR\n'
            + 'CURRENT_STAGE="sockets"\ncaptured="$(false)"\nprintf "unexpected:%s\\n" "$captured"\n'
        )
        result = subprocess.run(
            [str(BASH), "-c", harness],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stdout.splitlines(),
            ["AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=sockets|exit=1"],
        )
        self.assertEqual(result.stderr, "")

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
        self.assertGreaterEqual(source.count(r"(?: [^\r\n]+)?$"), 2)
        self.assertIn("& $SshExe @SshArguments 2>$null", source)
        self.assertNotIn("& $SshExe @SshArguments 2>&1", source)
        self.assertGreaterEqual(source.count("$SshOutput = $null"), 2)
        self.assertNotIn("if (Test-Path -LiteralPath $EvidencePath)", source)
        self.assertNotIn("[IO.File]::WriteAllText($EvidencePath", source)
        self.assertIn("[IO.FileMode]::CreateNew", source)
        self.assertIn("[IO.FileShare]::None", source)
        self.assertLess(source.index("Write-EvidenceCreateNew $EvidencePath"), source.index("Protect-PrivatePath $EvidencePath"))
        self.assertLess(source.index("Protect-PrivatePath $EvidencePath"), source.index("Assert-PrivatePath $EvidencePath"))

    @unittest.skipUnless(POWERSHELL.exists(), "Windows PowerShell is required")
    def test_safe_failure_envelope_parser_accepts_exact_allowlisted_stage(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        parser = extract_powershell_function(source, "Read-SafeFailureEnvelope")
        allowed = "$AllowedFailureStages = @('" + "','".join(FAILURE_STAGES) + "')\n"
        harness = (
            allowed
            + parser
            + "\n$result = Read-SafeFailureEnvelope "
            + "@('AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=firewall|exit=23') 23\n"
            + "if ($null -eq $result) { exit 2 }\n"
            + "if ($result.Stage -cne 'firewall' -or $result.ExitCode -ne 23) { exit 3 }\n"
        )
        with tempfile.TemporaryDirectory() as raw_tmp:
            harness_path = Path(raw_tmp) / "safe-failure-parser-pass.ps1"
            harness_path.write_text(harness, encoding="utf-8")
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
                ],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    @unittest.skipUnless(POWERSHELL.exists(), "Windows PowerShell is required")
    def test_safe_failure_envelope_parser_rejects_unsafe_variants(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        parser = extract_powershell_function(source, "Read-SafeFailureEnvelope")
        allowed = "$AllowedFailureStages = @('" + "','".join(FAILURE_STAGES) + "')\n"
        harness = (
            allowed
            + parser
            + r'''
$cases = @(
    [pscustomobject]@{ Lines=@('AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=unknown|exit=23'); ExitCode=23 },
    [pscustomobject]@{ Lines=@('AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=firewall|exit=0'); ExitCode=0 },
    [pscustomobject]@{ Lines=@('AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=firewall|exit=256'); ExitCode=256 },
    [pscustomobject]@{ Lines=@('AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=firewall|exit=23'); ExitCode=24 },
    [pscustomobject]@{ Lines=@('AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=firewall|exit=23|target=private'); ExitCode=23 },
    [pscustomobject]@{ Lines=@('prefix AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=firewall|exit=23'); ExitCode=23 },
    [pscustomobject]@{ Lines=@('AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=firewall|exit=23','AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=firewall|exit=23'); ExitCode=23 },
    [pscustomobject]@{ Lines=@('AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=firewall|exit=23','AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=firewall|exit=23|extra=1'); ExitCode=23 },
    [pscustomobject]@{ Lines=@('nft warning: private target'); ExitCode=1 }
)
foreach ($case in $cases) {
    if ($null -ne (Read-SafeFailureEnvelope $case.Lines $case.ExitCode)) { exit 4 }
}
'''
        )
        with tempfile.TemporaryDirectory() as raw_tmp:
            harness_path = Path(raw_tmp) / "safe-failure-parser-reject.ps1"
            harness_path.write_text(harness, encoding="utf-8")
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
                ],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_runner_claims_exact_run_before_ssh_and_separates_outcomes(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for marker in (
            '$expectedRunId = "spain-fresh-20260720-003"',
            "Exact Spain trust run id mismatch",
            'Join-Path $RunRoot "preflight-outcome.claim"',
            'Join-Path $RunRoot "preflight-failure-evidence.json"',
            '"amn2.spain-readonly-preflight-claim.v1"',
            '"amn2.spain-readonly-preflight-failure.v1"',
            '$FailureClassification = "remote_probe"',
            '$FailureClassification = "transport"',
            '$FailureStage = "unavailable"',
        ):
            self.assertIn(marker, source)
        self.assertLess(source.index("Exact Spain trust run id mismatch"), source.index("Read-Binding"))
        self.assertLess(source.index("Write-EvidenceCreateNew $OutcomeClaimPath"), source.index("& $SshExe"))
        self.assertIn("Read-SafeFailureEnvelope ([string[]]$SshOutput) $ProcessExitCode", source)
        self.assertNotIn("2>&1", source)
        self.assertNotRegex(source, r"(?i)(?:stderr|ssherror).*(?:write|out-file|set-content)")

    def test_runner_reuses_immutable_trust_bundle_but_claims_new_outcome_run(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn('$trustedBundleRunId = "spain-fresh-20260720-001"', source)
        self.assertIn('$expectedRunId = "spain-fresh-20260720-003"', source)
        self.assertIn('$TrustDirectory = Join-Path $ArtifactRoot $trustedBundleRunId', source)
        self.assertIn('$RunDirectory = Join-Path $ArtifactRoot $RunId', source)
        self.assertIn("[Environment]::GetFolderPath('LocalApplicationData')", source)
        self.assertNotIn('Join-Path $RepoRoot "private-artifacts', source)
        self.assertIn('function Initialize-OutcomeDirectory([string]$Path)', source)
        self.assertLess(
            source.index("Initialize-OutcomeDirectory $RunDirectory"),
            source.index("Write-EvidenceCreateNew $OutcomeClaimPath"),
        )
        self.assertNotIn("Remove-Item", source)

    def test_runner_hardens_non_reparse_outcome_root_before_child_creation(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        initializer = extract_powershell_function(source, "Initialize-OutcomeDirectory")
        self.assertIn(
            "Assert-PrivateRootChain",
            initializer,
        )
        self.assertNotIn("Protect-PrivatePath $ArtifactRoot", initializer)
        self.assertLess(
            initializer.index("Assert-PrivateRootChain"),
            initializer.index("[IO.Directory]::CreateDirectory($Path)"),
        )
        self.assertIn("Assert-NotReparsePoint $Path", initializer)

    def test_runner_verifies_private_root_and_trust_before_any_trust_read(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        verifier = extract_powershell_function(source, "Assert-PrivateRootChain")
        self.assertIn("Assert-NotReparsePoint $LocalAppDataRoot", verifier)
        self.assertIn("Assert-CurrentUserOwner $LocalAppDataRoot", verifier)
        self.assertIn("Assert-NotReparsePoint $PrivateRoot", verifier)
        self.assertIn("Assert-PrivatePath $PrivateRoot", verifier)
        self.assertLess(source.index("Assert-PrivateRootChain\n"), source.index("$Binding = Read-Binding"))

        private_path = extract_powershell_function(source, "Assert-PrivatePath")
        self.assertIn("Assert-CurrentUserOwner $Path", private_path)

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
        self.assertIn("Get-FileHash -LiteralPath $PSCommandPath", source)
        self.assertIn("RUNNER_SHA_$actualRunnerSha", source)
        self.assertIn("REMOTE_SCRIPT_SHA_$expectedRemoteScriptSha", source)
        self.assertIn(
            "SOURCE_55DC243B8E6C6BDB57F8301B56326E4CD4072D19",
            source,
        )

    def test_empty_approval_prints_checksum_bound_literal_without_private_state(self) -> None:
        runner_sha = hashlib.sha256(RUNNER.read_bytes()).hexdigest().upper()
        remote_sha = hashlib.sha256(REMOTE.read_bytes()).hexdigest().upper()
        expected = (
            "APPROVE POST_RELEASE_SPAIN_READ_ONLY_PREFLIGHT_"
            f"RUNNER_SHA_{runner_sha}_REMOTE_SCRIPT_SHA_{remote_sha}_"
            "SOURCE_55DC243B8E6C6BDB57F8301B56326E4CD4072D19_"
            "TRUST_RUN_ID_SPAIN_FRESH_20260720_003_"
            "IMMUTABLE_TRUST_BUNDLE_SPAIN_FRESH_20260720_001_"
            "NEW_OUTCOME_RUN_SPAIN_FRESH_20260720_003_"
            "DEDICATED_ED25519_EXACT_PRIVATE_TARGET_AND_INDEPENDENT_HOST_KEY_PIN_"
            "READ_ONLY_OS_CAPACITY_PORT_SERVICE_DOCKER_SYSTEMD_FIREWALL_SSH_CLOCK_"
            "AND_UNRELATED_SERVICE_FINGERPRINT_NO_INSTALL_NO_RESTART_NO_STOP_NO_"
            "CONFIG_SECRET_TELEGRAM_OR_AWG_MUTATION"
        )
        result = subprocess.run(
            [
                str(POWERSHELL),
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(RUNNER),
                "-Mode",
                "preflight",
                "-RunId",
                "approval-preview",
                "-Approval",
                "",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), expected)

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

    def test_exact_approval_with_wrong_run_id_fails_before_private_state(self) -> None:
        runner_sha = hashlib.sha256(RUNNER.read_bytes()).hexdigest().upper()
        remote_sha = hashlib.sha256(REMOTE.read_bytes()).hexdigest().upper()
        approval = (
            "APPROVE POST_RELEASE_SPAIN_READ_ONLY_PREFLIGHT_"
            f"RUNNER_SHA_{runner_sha}_REMOTE_SCRIPT_SHA_{remote_sha}_"
            "SOURCE_55DC243B8E6C6BDB57F8301B56326E4CD4072D19_"
            "TRUST_RUN_ID_SPAIN_FRESH_20260720_003_"
            "IMMUTABLE_TRUST_BUNDLE_SPAIN_FRESH_20260720_001_"
            "NEW_OUTCOME_RUN_SPAIN_FRESH_20260720_003_"
            "DEDICATED_ED25519_EXACT_PRIVATE_TARGET_AND_INDEPENDENT_HOST_KEY_PIN_"
            "READ_ONLY_OS_CAPACITY_PORT_SERVICE_DOCKER_SYSTEMD_FIREWALL_SSH_CLOCK_"
            "AND_UNRELATED_SERVICE_FINGERPRINT_NO_INSTALL_NO_RESTART_NO_STOP_NO_"
            "CONFIG_SECRET_TELEGRAM_OR_AWG_MUTATION"
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
                str(RUNNER),
                "-Mode",
                "preflight",
                "-RunId",
                "wrong-run",
                "-Approval",
                approval,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Exact Spain trust run id mismatch", result.stderr)
        combined = result.stdout + result.stderr
        self.assertNotIn("target.env", combined)
        self.assertNotIn("ssh.exe", combined.casefold())


if __name__ == "__main__":
    unittest.main()
