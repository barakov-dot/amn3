import hashlib
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REMOTE = REPO_ROOT / "scripts" / "vps" / "post_release_api_001_remote.sh"
RUNNER = REPO_ROOT / "scripts" / "vps" / "post_release_api_001_ssh_runner.ps1"


def read_required(test: unittest.TestCase, path: Path, label: str) -> str:
    test.assertTrue(path.exists(), f"{label} is missing")
    return path.read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class PostReleaseApi001ExecutorTests(unittest.TestCase):
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

    def test_remote_exposes_only_preflight_and_run(self) -> None:
        script = read_required(self, REMOTE, "API-001 remote executor")
        self.assertIn('MODE="${1:-}"', script)
        dispatch = script.split('case "$MODE" in', 1)[1]
        self.assertRegex(dispatch, r"preflight\)\s+preflight\s+;;")
        self.assertRegex(dispatch, r"run\)\s+run_gate\s+;;")
        self.assertNotRegex(dispatch, r"\b(?:apply|rollback|cleanup|deploy|restart)\)")

    def test_remote_binds_overlay_and_exact_api_source_hashes(self) -> None:
        script = read_required(self, REMOTE, "API-001 remote executor")
        required = {
            'EXPECTED_OVERLAY="0b858c5"',
            'SOURCE_FULL_COMMIT="0b858c5cdbc5b565cc265966a2edfe2d339d65e0"',
            'CLI_SHA="D77EADBE04A8B7FD6C3F75BC21E4F5FF7937CBF258DDC648D8F9ADAE0D0E5F86"',
            'API_APP_SHA="CB2B27B476674D2396BE5867F15A857CF8DD1B4989F8AA8FDEFD4F761F7BF536"',
            'SETTINGS_SHA="1DB81553DBCBF4DAFC710EFDD69C2DB0CC1A869F0754D7BB67C7ADFA3DCAC631"',
            'SCHEMA_SHA="D2FCB0892B0233B34182206BC14B5D3257C2EDCDDC2DB884606A48C12B0A959B"',
            'REPOSITORIES_SHA="997A3F615210A57CDF993F76D144F6C47B443C1749709EEA5B034F0AD6CBD72D"',
            'API_TOKENS_SHA="B7FDFEAFD9B0621D1B6450B3C64A9E34DF3F095C5E22C5D2ED68E46EB7879A06"',
            'API_SMOKE_SHA="6F5404AD33A1C48F15405085D660CD0122F3BBCCF648801B79E58217AE8DB267"',
        }
        for marker in sorted(required):
            self.assertIn(marker, script)
        self.assertIn('require_regular_file "$OVERLAY_MARKER"', script)
        self.assertIn('source_contract_check', script)

    def test_remote_requires_closed_write_gates_and_safe_preflight(self) -> None:
        script = read_required(self, REMOTE, "API-001 remote executor")
        for marker in (
            '"VPS_APPLY_ENABLED": "false"',
            '"OPERATOR_DEVICE_CREATE_ENABLED": "false"',
            'PRAGMA integrity_check',
            'PRAGMA foreign_key_check',
            'production_api_fingerprint',
            'listener_3040_absent',
            'bot_snapshot',
            'web_snapshot',
            'awg_snapshot',
        ):
            self.assertIn(marker, script)
        common = script.split("common_preflight() {", 1)[1].split(
            "create_clone() {", 1
        )[0]
        self.assertRegex(common, r"setsid sha256sum sleep ss stat systemctl tr wc seq")

    def test_clone_is_private_read_only_source_and_never_initializes_schema(self) -> None:
        script = read_required(self, REMOTE, "API-001 remote executor")
        clone = script.split("create_clone() {", 1)[1].split(
            "start_transient_api() {", 1
        )[0]
        for marker in (
            'STATE_BASE="/root/amn2-post-release-api-001"',
            'install -d -m 0700',
            'os.chmod(clone_path, 0o600)',
            'f"file:{source_path}?mode=ro"',
            'source.backup(destination)',
            'PRAGMA integrity_check',
            'PRAGMA foreign_key_check',
        ):
            self.assertIn(marker, script if marker.startswith("STATE_BASE") else clone)
        self.assertNotIn("initialize_schema", script)
        self.assertNotRegex(script, r"(?:rm|unlink|DELETE FROM)\s+[^\n]*\$DB_PATH")

    def test_transient_api_is_clone_only_ipv4_loopback_and_bounded(self) -> None:
        script = read_required(self, REMOTE, "API-001 remote executor")
        start = script.split("start_transient_api() {", 1)[1].split(
            "run_smoke() {", 1
        )[0]
        for marker in (
            'RUN_TTL_SECONDS="180"',
            'DATABASE_PATH="$CLONE_PATH"',
            'VPS_APPLY_ENABLED=false',
            'OPERATOR_DEVICE_CREATE_ENABLED=false',
            'api serve --host 127.0.0.1 --port 3040',
            'setsid',
            'WATCHDOG_PID',
        ):
            self.assertIn(marker, script if marker == 'RUN_TTL_SECONDS="180"' else start)
        self.assertNotIn("0.0.0.0", start)
        self.assertNotIn("[::]", start)

    def test_smoke_requires_six_get_routes_scope_denials_and_clone_audit(self) -> None:
        script = read_required(self, REMOTE, "API-001 remote executor")
        smoke = script.split("run_smoke() {", 1)[1].split(
            "mandatory_cleanup() {", 1
        )[0]
        for marker in (
            "api smoke-cycle",
            "http://127.0.0.1:3040",
            "checked_routes=6",
            "missing_bearer=401",
            "invalid_bearer=401",
            "server_scope_metrics=403",
            "metrics_scope_server=403",
            "api_read_count=6",
            "api_write_count=0",
            "revoked_at",
            "last_used_at",
        ):
            self.assertIn(marker, smoke)
        self.assertNotIn("install:write", smoke)
        self.assertNotRegex(smoke, r"curl[^\n]+-X\s*(?:POST|PUT|PATCH|DELETE)")

    def test_cleanup_is_armed_before_listener_and_removes_private_state(self) -> None:
        script = read_required(self, REMOTE, "API-001 remote executor")
        gate = script.split("run_gate() {", 1)[1].split('case "$MODE" in', 1)[0]
        self.assertLess(gate.index("trap mandatory_cleanup"), gate.index("create_clone"))
        self.assertLess(gate.index("create_clone"), gate.index("start_transient_api"))
        self.assertLess(gate.index("start_transient_api"), gate.index("run_smoke"))
        self.assertLess(
            gate.index("run_smoke"), gate.rindex("\n  mandatory_cleanup\n")
        )
        self.assertIn("trap mandatory_cleanup EXIT", gate)
        self.assertIn("trap 'mandatory_cleanup; exit 129' HUP", gate)
        self.assertIn("trap 'mandatory_cleanup; exit 130' INT", gate)
        self.assertIn("trap 'mandatory_cleanup; exit 143' TERM", gate)
        cleanup = script.split("mandatory_cleanup() {", 1)[1].split(
            "postflight() {", 1
        )[0]
        for marker in (
            'kill -- "-$API_PID"',
            'kill "$WATCHDOG_PID"',
            'rm -f -- "$CLONE_PATH"',
            'rm -rf -- "$STATE_ROOT"',
            "listener_3040_absent",
        ):
            self.assertIn(marker, cleanup)
        self.assertNotIn('if [ "$cleanup_rc" -eq 0 ]', cleanup)

    def test_smoke_secret_check_allows_safe_display_marker_only(self) -> None:
        script = read_required(self, REMOTE, "API-001 remote executor")
        smoke = script.split("run_smoke() {", 1)[1].split(
            "mandatory_cleanup() {", 1
        )[0]
        self.assertIn('"raw_token" in smoke.get("token", {})', smoke)
        self.assertNotIn('"raw_token" in serialized', smoke)

    def test_postflight_compares_bot_web_database_and_awg(self) -> None:
        script = read_required(self, REMOTE, "API-001 remote executor")
        gate = script.split("run_gate() {", 1)[1].split('case "$MODE" in', 1)[0]
        for marker in (
            'bot_snapshot >"$STATE_ROOT/bot.before"',
            'web_snapshot >"$STATE_ROOT/web.before"',
            'production_api_fingerprint >"$STATE_ROOT/db.before"',
            'awg_snapshot >"$STATE_ROOT/awg.before"',
        ):
            self.assertIn(marker, gate)
        postflight = script.split("postflight() {", 1)[1].split(
            "run_gate() {", 1
        )[0]
        for marker in (
            'bot_snapshot >"$STATE_ROOT/bot.after"',
            'web_snapshot >"$STATE_ROOT/web.after"',
            'production_api_fingerprint >"$STATE_ROOT/db.after"',
            'awg_snapshot >"$STATE_ROOT/awg.after"',
            'cmp -s "$STATE_ROOT/bot.before" "$STATE_ROOT/bot.after"',
            'cmp -s "$STATE_ROOT/web.before" "$STATE_ROOT/web.after"',
            'cmp -s "$STATE_ROOT/db.before" "$STATE_ROOT/db.after"',
            'cmp -s "$STATE_ROOT/awg.before" "$STATE_ROOT/awg.after"',
        ):
            self.assertIn(marker, postflight)

    def test_remote_has_no_forbidden_mutation_or_secret_output(self) -> None:
        script = read_required(self, REMOTE, "API-001 remote executor")
        forbidden = (
            r"sendMessage|sendPhoto|getUpdates|setChat|deleteChat",
            r"systemctl\s+(?:start|stop|restart|enable|disable)",
            r"docker\s+(?:start|stop|restart|kill|rm|update)\b",
            r"(?:awg|wg)\s+set\b",
            r"api\s+(?:serve|smoke-cycle)[^\n]*\$DB_PATH",
            r"install:write",
            r"api/install/mutation-requests",
            r"print\([^\n]*(?:raw_token|authorization|token_hash)",
        )
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, script, re.IGNORECASE), pattern)

    def test_all_embedded_python_heredocs_compile(self) -> None:
        script = read_required(self, REMOTE, "API-001 remote executor")
        blocks = re.findall(r"<<'PY'\n(.*?)\nPY\n", script, flags=re.DOTALL)
        self.assertGreaterEqual(len(blocks), 5)
        for index, block in enumerate(blocks):
            compile(block, f"embedded_api_001_{index}.py", "exec")

    def test_runner_binds_remote_sha_and_exact_literal_approval(self) -> None:
        runner = read_required(self, RUNNER, "API-001 SSH runner")
        remote_hash = sha256(REMOTE)
        self.assertIn(f'$expectedRemoteScriptSha = "{remote_hash}"', runner)
        exact = (
            "APPROVE POST_RELEASE_API_001_REMOTE_SHA_"
            + remote_hash
            + "_SOURCE_0B858C5_TRANSIENT_LOOPBACK_3040_CLONE_DB_SCOPED_TOKEN_"
            "TTL_REVOKE_AUDIT_SIX_ROUTE_SMOKE_MANDATORY_CLEANUP_PRODUCTION_"
            "BOT_WEB_DB_AND_AWG_UNTOUCHED"
        )
        self.assertIn(exact, runner.replace('" +\n        "', ""))
        self.assertIn(
            "[string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)",
            runner,
        )
        self.assertIn("ComputeHash($remoteScriptBytes)", runner)
        self.assertIn("-StandardInputBytes $remoteScriptBytes", runner)

    def test_runner_separates_preflight_from_single_use_run(self) -> None:
        runner = read_required(self, RUNNER, "API-001 SSH runner")
        for marker in (
            '[ValidateSet("preflight", "run")]',
            'if ($Mode -eq "preflight")',
            "Preflight mode does not accept approval",
            "Exact live approval mismatch",
            'if ($Mode -eq "run")',
            "[IO.FileMode]::CreateNew",
            ".run-consumed",
        ):
            self.assertIn(marker, runner)

    def test_runner_uses_trusted_isolated_openssh_and_redacts_target(self) -> None:
        runner = read_required(self, RUNNER, "API-001 SSH runner")
        for marker in (
            'Join-Path $env:WINDIR "System32\\OpenSSH"',
            'Join-Path $trustedOpenSshDir "ssh.exe"',
            'Join-Path $sshDir "amn2_private_rc_operator_ed25519"',
            'Join-Path $sshDir "codex_amn2_target_known_hosts"',
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
