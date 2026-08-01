from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts.phase12_spain_precondition import (
    observation_from_resource_confirmation_evidence,
)
from scripts.phase12_spain_installer import ChecksumBoundResourceObserver


ROOT = Path(__file__).resolve().parents[1]
REMOTE = ROOT / "scripts" / "vps" / "phase12_spain_resource_confirmation_remote.sh"
RUNNER = ROOT / "scripts" / "vps" / "phase12_spain_resource_confirmation_ssh_runner.ps1"
PACKAGE_RESOURCE_PLAN = ROOT / "packaging" / "phase12-spain" / "resource-plan.json"
OLD_REMOTE = ROOT / "scripts" / "vps" / "post_release_spain_readonly_preflight_remote.sh"
REFERENCE = (
    ROOT
    / "tests"
    / "fixtures"
    / "phase12_spain_resource_confirmation"
    / "run009_reference.json"
)
BASH = shutil.which("bash") or (
    r"C:\Program Files\Git\bin\bash.exe"
    if Path(r"C:\Program Files\Git\bin\bash.exe").is_file()
    else None
)
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")


def extract_shell_function(source: str, name: str) -> str:
    start = source.index(f"{name}() {{")
    depth = 0
    for match in re.finditer(r"\{|\}", source[start:]):
        depth += 1 if match.group() == "{" else -1
        if depth == 0:
            return source[start : start + match.end()] + "\n"
    raise AssertionError(f"unterminated shell function: {name}")


def extract_powershell_function(source: str, name: str) -> str:
    match = re.search(rf"(?m)^function {re.escape(name)}\b[^\n]*\{{", source)
    if not match:
        raise AssertionError(f"missing PowerShell function: {name}")
    depth = 0
    for index in range(match.start(), len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[match.start() : index + 1] + "\n"
    raise AssertionError(f"unterminated PowerShell function: {name}")


def sample_evidence() -> dict[str, object]:
    fingerprint = []
    for index in range(148):
        fingerprint.append(
            {
                "kind": "unit",
                "name_sha256": hashlib.sha256(f"unit-{index}".encode()).hexdigest(),
                "image_or_unit_sha256": hashlib.sha256(f"content-{index}".encode()).hexdigest(),
                "active_state": "active:running",
                "restart_count": 0,
                "bound_port_set": [],
                "unit_content_status": "exact",
                "bound_port_status": "cgroup_complete",
            }
        )
    return {
        "schema": "amn2.phase12-spain-resource-confirmation.v1",
        "mode": "read_only_resource_confirmation",
        "host_identity": {
            "machine_id_sha256": "c" * 64,
            "boot_id_sha256": "d" * 64,
        },
        "platform": {
            "kernel": {"system": "Linux", "release": "6.8.0-124-generic"},
            "os_release": {"id": "ubuntu", "version_id": "24.04"},
            "architecture": "x86_64",
            "python3": {"version": "3.12.3", "soabi": "cpython-312-x86_64-linux-gnu"},
            "glibc_version": "2.39",
        },
        "capacity": {
            "mem_available_bytes": 536870912,
            "filesystems": [
                {"path": path, "available_bytes": 8589934592, "available_inodes": 500000}
                for path in ("/", "/opt", "/etc", "/var", "/run")
            ],
        },
        "candidates": {
            "paths": [
                {"path": path, "exists": False}
                for path in (
                    "/opt/amn2-spain-package",
                    "/opt/amn2-spain",
                    "/etc/amn2-spain",
                    "/var/lib/amn2-spain",
                    "/var/lib/amn2-spain-docker",
                    "/var/lib/amn2-spain-phase12-audit",
                )
            ],
            "identities": {
                "user_name": "amn2-spain",
                "user_exists": False,
                "user_id": 61212,
                "uid_exists": False,
                "group_name": "amn2-spain",
                "group_exists": False,
                "group_id": 61212,
                "gid_exists": False,
            },
            "units": [
                {"name": name, "exists": False}
                for name in (
                    "amn2-spain-web.service",
                    "amn2-spain-bot.service",
                    "amn2-spain-docker.service",
                    "amn2-spain-network.service",
                    "amn2-spain-forward-compat.service",
                )
            ],
            "docker": {
                "binary_present": False,
                "potential_socket_present": False,
                "daemon_process_present": False,
                "observation_safe": True,
                "container_name": "amn2-spain-awg",
                "container_exists": False,
                "container_collision_unknown": False,
                "network_name": "amn2-spain-net",
                "network_exists": False,
                "network_collision_unknown": False,
            },
            "network": {
                "bridge_name": "amn2spbr0",
                "bridge_exists": False,
                "interface_name": "awgsp0",
                "interface_exists": False,
            },
            "sockets": [{"path": "/run/amn2-spain-docker/docker.sock", "exists": False}],
            "runtime_directories": [
                {"path": "/run/amn2-spain-docker", "exists": False}
            ],
        },
        "listening_sockets": [{"protocol": "tcp", "address": "0.0.0.0", "port": 22}],
        "network_state": {
            "addresses": [
                {
                    "interface": "eth0",
                    "family": "inet",
                    "address": "192.0.2.2",
                    "prefix_length": 24,
                    "scope": "global",
                }
            ],
            "routes": [
                {
                    "family": "inet",
                    "destination": "default",
                    "gateway": "192.0.2.1",
                    "interface": "eth0",
                    "table": "main",
                    "protocol": "static",
                    "scope": "global",
                    "type": "unicast",
                    "multipath": [],
                }
            ],
        },
        "systemd": {"present": True, "unit_count": 148},
        "cgroup_diagnostics": [
            {
                "unit_sha256": item["name_sha256"],
                "descendant_pid_count": 1,
                "pid_set_stable": True,
            }
            for item in fingerprint
        ],
        "firewall": {
            "backend": "nft",
            "raw_sha256": "e" * 64,
            "raw_rule_count": 7,
            "structured_snapshot_sha256": "f" * 64,
            "semantic_sha256": "1" * 64,
            "stability_observations": 2,
            "stable": True,
            "structured_snapshot": {"nftables": []},
        },
        "unrelated_service_fingerprint": fingerprint,
    }


class Phase12RemoteCollectorContractTests(unittest.TestCase):
    def test_resource_evidence_has_one_canonical_precondition_observation_adapter(self) -> None:
        observation = observation_from_resource_confirmation_evidence(sample_evidence())
        self.assertEqual(
            observation["schema"], "amn2.spain-precondition-observation.v1"
        )
        self.assertEqual(observation["listeners"], ["tcp|wildcard|22"])
        self.assertEqual(observation["addresses"], ["192.0.2.2/24"])
        self.assertEqual(observation["routes"], ["0.0.0.0/0"])
        self.assertFalse(observation["docker_present"])
        self.assertEqual(
            observation["systemd_projection"],
            sample_evidence()["unrelated_service_fingerprint"],
        )
        self.assertEqual(
            observation["firewall"],
            {
                "backend": "nft",
                "rules_sha256": "e" * 64,
                "rule_count": 7,
                "semantic_sha256": "1" * 64,
                "nft_json": {"nftables": []},
            },
        )

    def test_resource_evidence_adapter_accepts_listener_zone_suffix(self) -> None:
        evidence = sample_evidence()
        evidence["listening_sockets"] = [
            {"protocol": "udp", "address": "127.0.0.53%lo", "port": 53}
        ]
        observation = observation_from_resource_confirmation_evidence(evidence)
        self.assertEqual(observation["listeners"], ["udp|loopback|53"])

    def test_checksum_bound_resource_observer_executes_exact_reviewed_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            collector = Path(raw) / "collector.sh"
            collector.write_bytes(b"#!/usr/bin/env bash\nexit 0\n")
            evidence = sample_evidence()
            payload = (
                json.dumps(evidence, separators=(",", ":"), ensure_ascii=True).encode(
                    "ascii"
                )
                + b"\n"
            )
            calls = []

            def runner(argv, **kwargs):
                if os.name != "nt":
                    replacement = collector.with_suffix(".replacement")
                    replacement.write_bytes(b"replacement-after-verification\n")
                    os.replace(replacement, collector)
                pinned = os.read(kwargs["input_fd"], kwargs["input_size"])
                calls.append((argv, kwargs))
                self.assertEqual(pinned, b"#!/usr/bin/env bash\nexit 0\n")
                return payload

            observer = ChecksumBoundResourceObserver(
                collector_path=collector,
                collector_sha256=hashlib.sha256(collector.read_bytes()).hexdigest(),
                runner=runner,
                expected_uid=None,
            )
            observation = observer.collect_observation()
            self.assertEqual(observation["listeners"], ["tcp|wildcard|22"])
            self.assertEqual(calls[0][0], ("/usr/bin/bash", "-s"))
            self.assertNotIn(str(collector), calls[0][0])
            collector.write_bytes(b"drift\n")
            with self.assertRaisesRegex(Exception, "checksum"):
                observer.collect_observation()

    def test_remote_is_one_read_only_mode_with_no_arguments(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        self.assertTrue(source.startswith("#!/usr/bin/env bash\nset -Eeuo pipefail\n"))
        self.assertIn('[[ "$#" -eq 0 ]]', source)
        self.assertIn('"mode":"read_only_resource_confirmation"', source)
        self.assertNotRegex(source, r"(?m)^\s*(?:sudo\s+)?(?:mkdir|install|cp|mv|rm)\b")
        self.assertNotRegex(source, r"(?m)^\s*systemctl\s+(?:start|stop|restart|enable|disable)\b")
        self.assertNotRegex(source, r"(?m)^\s*docker\s+(?:run|create|start|stop|restart|rm|network\s+(?:create|rm))\b")
        self.assertNotRegex(source, r"(?m)^\s*nft\s+(?:add|delete|flush)\b")
        self.assertNotRegex(source, r"(?i)\b(?:curl|wget|apt(?:-get)?)\b")
        self.assertNotIn("<<", source)
        self.assertNotIn(">>>", source)
        self.assertNotRegex(source, r"(?m)(?:^|\|)\s*sort\b")
        self.assertNotRegex(source, r"(?i)\b(?:mktemp|tempfile)\b")
        for invocation in re.findall(r"(?m)^\s*python3\b[^\n]*", source):
            self.assertIn("python3 -I -B", invocation)
        self.assertNotRegex(
            source,
            r"(?m)>\s*(?!/dev/null\b)[/~A-Za-z_.][^\s;]*",
        )

    def test_remote_declares_complete_required_observation(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        for marker in (
            "machine_id_sha256",
            "boot_id_sha256",
            "/etc/os-release",
            "VERSION_ID",
            "x86_64",
            "SOABI",
            "MemAvailable",
            "available_inodes",
            "/opt/amn2-spain",
            "/opt/amn2-spain-package",
            "61212",
            "amn2-spain-web.service",
            "amn2-spain-awg",
            "amn2-spain-net",
            "amn2spbr0",
            "awgsp0",
            "/run/amn2-spain-docker/docker.sock",
            "ip -j address show",
            "ip -j -4 route show table all",
            "ip -j -6 route show table all",
            "nft -j list ruleset",
            "structured_snapshot_sha256",
            "semantic_sha256",
            "stability_observations",
            "unrelated_service_fingerprint",
            "collect_descendant_pid_diagnostic",
            "descendant_pid_count",
            "pid_set_stable",
        ):
            self.assertIn(marker, source)

    def test_expected_negative_candidate_probes_do_not_leak_stderr(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        for marker in (
            "' /etc/passwd; then user_exists=true",
            "' /etc/group; then group_exists=true",
            "silent_probe ip link show dev amn2spbr0",
            "silent_probe ip link show dev awgsp0",
        ):
            self.assertIn(marker, source)

    @unittest.skipUnless(BASH, "bash is required")
    def test_positive_collision_probe_is_stdout_and_stderr_silent(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        function = extract_shell_function(source, "silent_probe")
        with tempfile.TemporaryDirectory() as raw_tmp:
            harness = Path(raw_tmp) / "silent-probe.sh"
            harness.write_text(
                "#!/usr/bin/env bash\nset -Eeuo pipefail\n"
                + function
                + "\nnoisy_success(){ printf 'private-out\\n'; printf 'private-err\\n' >&2; return 0; }\n"
                + "silent_probe noisy_success\n",
                encoding="utf-8",
                newline="\n",
            )
            result = subprocess.run(
                [BASH, str(harness)], capture_output=True, text=True, check=False
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_remote_never_executes_docker_cli_or_daemon_socket_api(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        self.assertNotRegex(source, r"(?m)^\s*docker\b")
        self.assertNotRegex(source, r"\$\(docker\b")
        self.assertNotIn("docker inspect", source)
        self.assertNotIn("docker ps", source)
        for marker in (
            "docker_binary_present",
            "potential_socket_present",
            "daemon_process_present",
            "docker_observation_safe",
            "container_collision_unknown",
            "network_collision_unknown",
        ):
            self.assertIn(marker, source)

    def test_run009_cgroup_fingerprint_primitives_are_reused_exactly(self) -> None:
        new = REMOTE.read_text(encoding="utf-8")
        old = OLD_REMOTE.read_text(encoding="utf-8")
        for name in (
            "safe_cgroup_path",
            "parse_proc_cgroup_path",
            "read_proc_starttime",
            "resolve_unit_cgroup",
            "collect_ports_for_cgroup",
        ):
            self.assertIn(f"{name}() {{", new)
            self.assertIn(f"{name}() {{", old)
        for marker in (
            'RESOLVED_BOUND_PORT_STATUS="cgroup_complete"',
            'RESOLVED_BOUND_PORT_STATUS="mainpid_cgroup_complete"',
            'CGROUP_PORTS_SUBREASON="cgroup_procs"',
            'CGROUP_PORTS_SUBREASON="socket_parse"',
        ):
            self.assertIn(marker, new)

    def test_remote_uses_direct_identity_files_and_dual_nft_stability(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        self.assertNotIn("getent", source)
        self.assertIn("/etc/passwd", source)
        self.assertIn("/etc/group", source)
        self.assertGreaterEqual(source.count("nft -j list ruleset"), 2)
        self.assertIn("nft_semantic_sha256_first", source)
        self.assertIn("nft_semantic_sha256_second", source)
        self.assertIn('[[ "$nft_semantic_sha256_first" == "$nft_semantic_sha256_second" ]]', source)

    def test_remote_capacity_and_port_attribution_cover_run_and_descendant_cgroups(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        self.assertIn("for filesystem_path in / /opt /etc /var /run", source)
        self.assertIn("collect_stable_cgroup_pids()", source)
        ports = extract_shell_function(source, "collect_ports_for_cgroup_once")
        self.assertIn("collect_stable_cgroup_pids", ports)
        self.assertNotIn('local cgroup_file="${cgroup_root}${control_group}/cgroup.procs"', ports)
        wrapper = extract_shell_function(source, "collect_ports_for_cgroup")
        self.assertIn("for fd_readlink_attempt in 1 2", wrapper)
        self.assertIn('"$CGROUP_PORTS_SUBREASON" != "fd_readlink"', wrapper)

    @unittest.skipUnless(BASH, "bash is required")
    def test_cgroup_fd_readlink_retries_one_full_snapshot_then_fails_closed(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        functions = "\n".join(
            extract_shell_function(source, name)
            for name in (
                "collect_stable_cgroup_pids",
                "collect_ports_for_cgroup_once",
                "collect_ports_for_cgroup",
            )
        )
        with tempfile.TemporaryDirectory() as raw_tmp:
            root = Path(raw_tmp)
            cgroup_root = root / "cgroup"
            proc_root = root / "proc"
            fd_root = proc_root / "321" / "fd"
            net_root = proc_root / "321" / "net"
            (cgroup_root / "demo.service" / "delegated").mkdir(parents=True)
            fd_root.mkdir(parents=True)
            net_root.mkdir(parents=True)
            (cgroup_root / "demo.service" / "cgroup.procs").write_bytes(b"321\n")
            (cgroup_root / "demo.service" / "delegated" / "cgroup.procs").write_bytes(b"321\n")
            (fd_root / "socket-entry").write_text("", encoding="ascii")
            for name in ("tcp", "tcp6", "udp", "udp6"):
                (net_root / name).write_text("", encoding="ascii")
            def bash_path(path: Path) -> str:
                if os.name != "nt":
                    return str(path)
                conversion = subprocess.run(
                    [str(BASH), "-c", 'cygpath -u -- "$1"', "bash", str(path)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )
                self.assertEqual(conversion.returncode, 0, conversion.stderr)
                return conversion.stdout.strip()

            cgroup_root_bash = bash_path(cgroup_root)
            proc_root_bash = bash_path(proc_root)
            retry_marker_bash = bash_path(root / "readlink-retry-marker")
            harness = rf'''set -Eeuo pipefail
COLLECTED_UNIT_PORTS=""
CGROUP_PORTS_SUBREASON=""
STABLE_CGROUP_PID_COUNT=0
declare -A STABLE_CGROUP_PID_SET=()
{functions}
readlink() {{
    if [[ ! -e '{retry_marker_bash}' ]]; then : > '{retry_marker_bash}'; return 1; fi
    printf 'socket:[123]\n'
}}
collect_ports_for_cgroup /demo.service '{cgroup_root_bash}' '{proc_root_bash}' || {{ printf 'reason=%s\n' "$CGROUP_PORTS_SUBREASON" >&2; exit 90; }}
[[ -e '{retry_marker_bash}' ]] || exit 91
[[ -z "$CGROUP_PORTS_SUBREASON" ]] || exit 92
readlink() {{ return 1; }}
if collect_ports_for_cgroup /demo.service '{cgroup_root_bash}' '{proc_root_bash}'; then exit 93; fi
[[ "$CGROUP_PORTS_SUBREASON" == "fd_readlink" ]] || exit 94
'''
            result = subprocess.run(
                [str(BASH), "-c", harness,
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(BASH, "bash is required")
    def test_failure_stage_envelope_is_sanitized_and_fail_closed(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        prefix = source.split("# === COLLECTOR MAIN ===", 1)[0]
        cases = (("systemd_cgroup_ports", 75), ("network_state", 91), ("unknown", 9))
        for stage, code in cases:
            with tempfile.TemporaryDirectory() as raw_tmp:
                harness = Path(raw_tmp) / "failure-envelope.sh"
                harness.write_text(
                    prefix + f"\nCURRENT_STAGE={stage!r}; emit_failure {code}\n",
                    encoding="utf-8",
                    newline="\n",
                )
                result = subprocess.run(
                    [BASH, str(harness)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
            self.assertNotEqual(result.returncode, 0)
            expected_stage = stage if stage != "unknown" else "bootstrap"
            self.assertEqual(
                result.stdout,
                f"AMN2_PHASE12_RESOURCE_CONFIRMATION_FAILURE_V1|stage={expected_stage}|exit={code}\n",
            )
            self.assertEqual(result.stderr, "")

    def test_capacity_probe_uses_compatible_df_options(self) -> None:
        source = REMOTE.read_text(encoding="utf-8")
        self.assertNotIn("df -P -B1 --output=avail,iavail", source)


@unittest.skipUnless(POWERSHELL.exists(), "Windows PowerShell is required")
class Phase12RunnerContractTests(unittest.TestCase):
    def test_resource_plan_declares_root_private_retained_authorization_audit_path(self) -> None:
        plan = json.loads(PACKAGE_RESOURCE_PLAN.read_text(encoding="utf-8"))
        retained = ["/var/lib/amn2-spain-phase12-audit"]
        self.assertEqual(plan["resources"]["retained_paths"], retained)
        remote = REMOTE.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn(retained[0], remote)
        self.assertIn(retained[0], runner)
        self.assertIn(
            '"retained_paths=$(@($Plan.resources.retained_paths) -join \',\')"',
            runner,
        )

    def _validate(self, evidence: dict[str, object]) -> subprocess.CompletedProcess[str]:
        source = RUNNER.read_text(encoding="utf-8")
        functions = (
            extract_powershell_function(source, "Assert-ExactProperties")
            + extract_powershell_function(source, "Assert-ResourceConfirmationSchema")
        )
        with tempfile.TemporaryDirectory() as raw_tmp:
            path = Path(raw_tmp) / "validate.ps1"
            path.write_text(
                "Set-StrictMode -Version Latest\n$ErrorActionPreference='Stop'\n"
                + functions
                + "\n$e=[Console]::In.ReadToEnd() | ConvertFrom-Json\n"
                + "Assert-ResourceConfirmationSchema $e\n",
                encoding="utf-8",
            )
            return subprocess.run(
                [
                    str(POWERSHELL),
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(path),
                ],
                input=json.dumps(evidence, separators=(",", ":")),
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )

    def _assert_changed_fingerprint_rejected(self) -> subprocess.CompletedProcess[str]:
        source = RUNNER.read_text(encoding="utf-8")
        functions = (
            extract_powershell_function(source, "Assert-ExactProperties")
            + extract_powershell_function(source, "Assert-ResourceConfirmationSchema")
            + extract_powershell_function(source, "Get-FingerprintSetReceipt")
            + extract_powershell_function(source, "Assert-FingerprintBaseline")
        )
        original = sample_evidence()["unrelated_service_fingerprint"]
        changed = copy.deepcopy(original)
        changed[0]["restart_count"] = 1
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            original_path = tmp / "original.json"
            changed_path = tmp / "changed.json"
            script_path = tmp / "baseline.ps1"
            original_path.write_text(json.dumps(original), encoding="utf-8")
            changed_path.write_text(json.dumps(changed), encoding="utf-8")
            script_path.write_text(
                "Set-StrictMode -Version Latest\n$ErrorActionPreference='Stop'\n"
                + functions
                + "\n$o=Get-Content -Raw -LiteralPath $args[0] | ConvertFrom-Json\n"
                + "$c=Get-Content -Raw -LiteralPath $args[1] | ConvertFrom-Json\n"
                + "$r=Get-FingerprintSetReceipt @($o)\n"
                + "Assert-FingerprintBaseline @($c) $r.Sha256 $r.ByteLength\n",
                encoding="utf-8",
            )
            return subprocess.run(
                [
                    str(POWERSHELL),
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script_path),
                    str(original_path),
                    str(changed_path),
                ],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )

    def test_schema_accepts_aligned_dynamic_foreign_entry_shape(self) -> None:
        good = self._validate(sample_evidence())
        self.assertEqual(good.returncode, 0, good.stderr)
        bad = sample_evidence()
        bad["unexpected"] = True
        self.assertNotEqual(self._validate(bad).returncode, 0)
        nested = sample_evidence()
        nested["platform"]["python3"]["secret"] = "x"  # type: ignore[index]
        self.assertNotEqual(self._validate(nested).returncode, 0)
        short = sample_evidence()
        short["unrelated_service_fingerprint"] = short["unrelated_service_fingerprint"][:-1]  # type: ignore[index]
        short["cgroup_diagnostics"] = short["cgroup_diagnostics"][:-1]  # type: ignore[index]
        short["systemd"]["unit_count"] = 147  # type: ignore[index]
        self.assertEqual(self._validate(short).returncode, 0)
        unaligned = sample_evidence()
        unaligned["unrelated_service_fingerprint"] = unaligned["unrelated_service_fingerprint"][:-1]  # type: ignore[index]
        self.assertNotEqual(self._validate(unaligned).returncode, 0)
        wrong_path = sample_evidence()
        wrong_path["candidates"]["paths"][0]["path"] = "/opt/not-amn2"  # type: ignore[index]
        self.assertNotEqual(self._validate(wrong_path).returncode, 0)
        unsafe_docker = sample_evidence()
        unsafe_docker["candidates"]["docker"]["observation_safe"] = False  # type: ignore[index]
        unsafe_docker["candidates"]["docker"]["container_collision_unknown"] = True  # type: ignore[index]
        self.assertEqual(self._validate(unsafe_docker).returncode, 0)

    def test_dynamic_receipt_allows_only_membership_volatility(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        functions = (
            extract_powershell_function(source, "Get-FingerprintSetReceipt")
            + extract_powershell_function(source, "Get-StableFingerprintSetReceipt")
            + extract_powershell_function(source, "Get-PersistentFingerprintReceipt")
        )
        before = sample_evidence()["unrelated_service_fingerprint"]
        after = copy.deepcopy(before[:-1])
        changed = copy.deepcopy(after)
        changed[0]["restart_count"] = 1
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            before_path = tmp / "before.json"
            after_path = tmp / "after.json"
            changed_path = tmp / "changed.json"
            script_path = tmp / "dynamic.ps1"
            before_path.write_text(json.dumps(before), encoding="utf-8")
            after_path.write_text(json.dumps(after), encoding="utf-8")
            changed_path.write_text(json.dumps(changed), encoding="utf-8")
            script_path.write_text(
                "Set-StrictMode -Version Latest\n$ErrorActionPreference='Stop'\n"
                + functions
                + "\n$b=Get-Content -Raw -LiteralPath $args[0] | ConvertFrom-Json\n"
                + "$a=Get-Content -Raw -LiteralPath $args[1] | ConvertFrom-Json\n"
                + "$r=Get-PersistentFingerprintReceipt @($b) @($a)\n"
                + "if ($r.volatile_before_count -ne 1 -or $r.volatile_after_count -ne 0) { throw 'volatility receipt mismatch' }\n"
                + "$c=Get-Content -Raw -LiteralPath $args[2] | ConvertFrom-Json\n"
                + "Get-PersistentFingerprintReceipt @($b) @($c)\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [str(POWERSHELL), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(script_path), str(before_path), str(after_path), str(changed_path)],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)

    def test_duplicate_fingerprint_identity_is_rejected(self) -> None:
        duplicate = sample_evidence()
        duplicate["unrelated_service_fingerprint"][1] = copy.deepcopy(  # type: ignore[index]
            duplicate["unrelated_service_fingerprint"][0]  # type: ignore[index]
        )
        self.assertNotEqual(self._validate(duplicate).returncode, 0)

    def test_duplicate_json_key_is_rejected_before_schema_use(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        function = extract_powershell_function(source, "Assert-CanonicalJsonEncoding")
        harness = (
            "$ErrorActionPreference='Stop'\n"
            + function
            + "\nAssert-CanonicalJsonEncoding '{\"schema\":\"a\",\"schema\":\"b\"}'\n"
        )
        with tempfile.TemporaryDirectory() as raw_tmp:
            path = Path(raw_tmp) / "duplicate-json.ps1"
            path.write_text(harness, encoding="utf-8")
            result = subprocess.run(
                [
                    str(POWERSHELL),
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)

    def test_canonical_json_accepts_exact_single_key_encoding(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        function = extract_powershell_function(source, "Assert-CanonicalJsonEncoding")
        harness = (
            "$ErrorActionPreference='Stop'\n"
            + function
            + "\n$null=Assert-CanonicalJsonEncoding ([Console]::In.ReadToEnd())\n"
        )
        with tempfile.TemporaryDirectory() as raw_tmp:
            path = Path(raw_tmp) / "canonical-json.ps1"
            path.write_text(harness, encoding="utf-8")
            result = subprocess.run(
                [
                    str(POWERSHELL), "-NoProfile", "-NonInteractive",
                    "-ExecutionPolicy", "Bypass", "-File", str(path),
                ],
                input='{"a":[1,true,false,null,"x"]}',
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_resource_observer_accepts_checksum_bound_in_memory_collector(self) -> None:
        collector = b"#!/usr/bin/env bash\nprintf '%s\\n' collector\n"
        expected = json.dumps(
            sample_evidence(), separators=(",", ":"), ensure_ascii=True
        ).encode("ascii") + b"\n"
        seen: dict[str, bytes] = {}

        def runner(argv: tuple[str, ...], **kwargs: object) -> bytes:
            self.assertEqual(argv, ("/usr/bin/bash", "-s"))
            descriptor = int(kwargs["input_fd"])
            seen["collector"] = os.read(descriptor, 1024)
            return expected

        with tempfile.TemporaryFile() as backing, mock.patch.object(
            os, "memfd_create", return_value=os.dup(backing.fileno()), create=True
        ), mock.patch.object(os, "fchmod", create=True):
            observer = ChecksumBoundResourceObserver(
                collector_bytes=collector,
                collector_sha256=hashlib.sha256(collector).hexdigest(),
                runner=runner,
                expected_uid=None,
            )
            self.assertEqual(observer.collect_evidence(), sample_evidence())
        self.assertEqual(seen["collector"], collector)

    def test_evidence_file_receives_private_acl_at_create(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        functions = (
            extract_powershell_function(source, "Assert-CurrentUserOwner")
            + extract_powershell_function(source, "Assert-NotReparseFile")
            + extract_powershell_function(source, "Assert-PrivatePath")
            + extract_powershell_function(source, "New-PrivateFileSecurity")
            + extract_powershell_function(source, "Write-BytesCreateNew")
        )
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            path = tmp / "private-create.ps1"
            evidence = tmp / "evidence.json"
            path.write_text(
                "$ErrorActionPreference='Stop'\n"
                + "Import-Module (Join-Path $PSHOME 'Modules\\Microsoft.PowerShell.Security') -ErrorAction Stop\n"
                + functions
                + "\nWrite-BytesCreateNew $args[0] ([byte[]](0x7B,0x7D,0x0A))\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    str(POWERSHELL), "-NoProfile", "-NonInteractive",
                    "-ExecutionPolicy", "Bypass", "-File", str(path), str(evidence),
                ],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            data = evidence.read_bytes() if evidence.exists() else b""
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(data, b"{}\n")

    def test_changed_fingerprint_field_is_rejected_order_independently(self) -> None:
        result = self._assert_changed_fingerprint_rejected()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not equal run009", result.stderr)

    def test_runner_is_checksum_target_pin_and_single_use_bound(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for marker in (
            "$expectedRemoteScriptSha",
            "Get-FileHash -LiteralPath $PSCommandPath",
            "TARGET_HOST",
            "TARGET_USER",
            "EXPECTED_HOST_KEY_SHA256",
            "StrictHostKeyChecking=yes",
            "UserKnownHostsFile=$KnownHostsPath",
            "IdentitiesOnly=yes",
            "bash -s --",
            "resource-confirmation-outcome.claim",
            "[IO.FileMode]::CreateNew",
            "raw_stdout_sha256",
            "canonical_evidence_sha256",
            "resource-confirmation-evidence.json",
            "Protect-PrivatePath",
            "Get-FileHash -LiteralPath $ReceiptPath",
            "New-PrivateFileSecurity",
            "[Security.AccessControl.FileSecurity]",
            "Assert-NotReparseFile",
            "ssh-ed25519",
            "approval_sha256",
            "host_pin_sha256",
            "known_hosts_sha256",
            "auth_public_key_sha256",
            "35ED9383AE9E73268E3D1AB7F57612BC60EA59C0531D6A96372E5F3731883D00",
            "$run009FirewallRuleCount = 129",
            "Assert-CanonicalJsonEncoding",
        ):
            self.assertIn(marker, source)
        self.assertNotIn("PENDING_LOCAL_DOC_SYNC", source)
        self.assertNotIn("bash -s -- preflight", source)
        self.assertNotRegex(source, r"(?i)(password|token|secret|private[_ -]?key)\s*[:=]")
        self.assertLess(source.index("New-PrivateFileSecurity"), source.index("Write-BytesCreateNew"))

    def test_runner_embeds_exact_remote_checksum_and_preview_never_uses_ssh(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        expected = re.search(r'\$expectedRemoteScriptSha\s*=\s*"([A-F0-9]{64})"', source)
        self.assertIsNotNone(expected)
        self.assertEqual(expected.group(1), hashlib.sha256(REMOTE.read_bytes()).hexdigest().upper())
        result = subprocess.run(
            [
                str(POWERSHELL),
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(RUNNER),
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("APPROVE PHASE12 SPAIN READ ONLY RESOURCE CONFIRMATION", result.stdout)
        self.assertNotIn("ssh.exe", (result.stdout + result.stderr).casefold())

    def test_approval_binds_revalidated_private_trust_bundle_without_printing_values(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for marker in (
            "function Get-TrustBundleReceipt",
            "target_host_sha256",
            "target_user_sha256",
            "host_key_fingerprint_sha256",
            "known_hosts_sha256",
            "auth_public_key_sha256",
            "$PreviewTrust = Get-TrustBundleReceipt",
            "TRUST BUNDLE SHA256 $($PreviewTrust.BundleSha256)",
            "$ExecutionTrust = Get-TrustBundleReceipt",
            "Trust bundle changed after approval preview",
        ):
            self.assertIn(marker, source)
        self.assertLess(source.index("$PreviewTrust = Get-TrustBundleReceipt"), source.index("if ([string]::IsNullOrEmpty($Approval))"))
        self.assertLess(source.index("$ExecutionTrust = Get-TrustBundleReceipt"), source.index("Initialize-OutcomeDirectory $RunDirectory"))
        self.assertLess(source.index("Trust bundle changed after approval preview"), source.index("Initialize-OutcomeDirectory $RunDirectory"))

        trust = (
            Path(os.environ["LOCALAPPDATA"])
            / "AMN2"
            / "private-artifacts"
            / "post-release"
            / "spain-migration"
            / "spain-fresh-20260720-001"
        )
        if not trust.is_dir():
            self.skipTest("private Spain trust bundle is unavailable")
        private_values = []
        binding = (trust / "target.env").read_text(encoding="utf-8").splitlines()
        private_values.extend(line.split("=", 1)[1] for line in binding if "=" in line)
        private_values.append((trust / "known_hosts_spain").read_text(encoding="utf-8").strip())
        private_values.append((trust / "id_ed25519_spain.pub").read_text(encoding="utf-8").strip())
        result = subprocess.run(
            [
                str(POWERSHELL),
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(RUNNER),
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stdout, r"TRUST BUNDLE SHA256 [A-F0-9]{64}")
        combined = result.stdout + result.stderr
        for value in private_values:
            if value:
                self.assertNotIn(value, combined)

    def test_windows_command_line_quoting_preserves_special_values(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        quoting = extract_powershell_function(source, "ConvertTo-WindowsCommandLineArgument")
        harness = quoting + r'''
$cases = @(
    [pscustomobject]@{ Value='plain'; Expected='"plain"' },
    [pscustomobject]@{ Value='two words'; Expected='"two words"' },
    [pscustomobject]@{ Value='C:\path\'; Expected='"C:\path\\"' },
    [pscustomobject]@{ Value='a"b'; Expected='"a\"b"' },
    [pscustomobject]@{ Value=''; Expected='""' }
)
foreach ($case in $cases) {
    if ((ConvertTo-WindowsCommandLineArgument $case.Value) -cne $case.Expected) { exit 9 }
}
'''
        with tempfile.TemporaryDirectory() as raw_tmp:
            path = Path(raw_tmp) / "quote.ps1"
            path.write_text(harness, encoding="utf-8")
            result = subprocess.run(
                [
                    str(POWERSHELL),
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(POWERSHELL.exists(), "Windows PowerShell is required")
    def test_process_boundary_returns_one_result_object_with_byte_properties(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        harness = (
            extract_powershell_function(source, "ConvertTo-WindowsCommandLineArgument")
            + extract_powershell_function(source, "Invoke-SshWithExactInput")
            + r'''
$SshExe = (Get-Command powershell.exe).Source
$payload = [byte[]](0x41)
$result = Invoke-SshWithExactInput $SshExe @('-NoLogo','-NoProfile','-NonInteractive','-Command','[Console]::Out.Write("ok")') $payload
if ($result -is [array]) { exit 10 }
if ($result.ExitCode -ne 0) { exit 11 }
if ($result.StdoutBytes.Length -ne 2) { exit 12 }
if ([Text.Encoding]::ASCII.GetString($result.StdoutBytes) -cne 'ok') { exit 13 }
'''
        )
        with tempfile.TemporaryDirectory() as raw_tmp:
            path = Path(raw_tmp) / "result-object.ps1"
            path.write_text(harness, encoding="utf-8")
            result = subprocess.run(
                [
                    str(POWERSHELL), "-NoProfile", "-NonInteractive",
                    "-ExecutionPolicy", "Bypass", "-File", str(path),
                ],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(POWERSHELL.exists(), "Windows PowerShell is required")
    def test_atomic_receipt_creation_checks_both_paths_as_separate_expressions(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        harness = extract_powershell_function(source, "Write-AtomicPrivateJsonCreateNew") + r'''
function Write-BytesCreateNew([string]$Path, [byte[]]$Bytes) {
    [IO.File]::WriteAllBytes($Path, $Bytes)
}
function Protect-PrivatePath([string]$Path) {}
$path = Join-Path $env:TEMP 'phase12-resource-confirmation-receipt.json'
Write-AtomicPrivateJsonCreateNew $path '{"status":"passed"}'
if (-not (Test-Path -LiteralPath $path)) { exit 10 }
Remove-Item -LiteralPath $path -Force
'''
        with tempfile.TemporaryDirectory() as raw_tmp:
            path = Path(raw_tmp) / "atomic-receipt.ps1"
            harness = harness.replace("$env:TEMP", f"'{raw_tmp.replace(chr(92), chr(92) * 2)}'")
            path.write_text(harness, encoding="utf-8")
            result = subprocess.run(
                [
                    str(POWERSHELL), "-NoProfile", "-NonInteractive",
                    "-ExecutionPolicy", "Bypass", "-File", str(path),
                ],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(POWERSHELL.exists(), "Windows PowerShell is required")
    def test_conflict_decision_is_recomputed_from_exact_resource_plan(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        functions = "".join(
            extract_powershell_function(source, name)
            for name in (
                "Get-TextSha256",
                "ConvertTo-IPv4UInt32",
                "Test-IPv4NetworkOverlap",
                "Get-ResourcePlanReceipt",
                "Test-VersionAtLeast",
                "Get-ConflictDecision",
            )
        )

        def decide(evidence: dict[str, object]) -> subprocess.CompletedProcess[str]:
            with tempfile.TemporaryDirectory() as raw_tmp:
                script = Path(raw_tmp) / "conflict.ps1"
                script.write_text(
                    "$ErrorActionPreference='Stop'\n"
                    + "Import-Module (Join-Path $PSHOME 'Modules\\Microsoft.PowerShell.Utility') -ErrorAction Stop\n"
                    + functions
                    + "\n$PackageResourcePlanPath=$args[0]\n"
                    + "$expectedPackageResourcePlanSha=(Get-FileHash -LiteralPath $PackageResourcePlanPath -Algorithm SHA256).Hash.ToUpperInvariant()\n"
                    + "\n$e=[Console]::In.ReadToEnd() | ConvertFrom-Json\n"
                    + "$d=Get-ConflictDecision $e\n"
                    + "$d | ConvertTo-Json -Depth 8 -Compress\n",
                    encoding="utf-8",
                )
                return subprocess.run(
                    [
                        str(POWERSHELL), "-NoProfile", "-NonInteractive",
                        "-ExecutionPolicy", "Bypass", "-File", str(script),
                        str(PACKAGE_RESOURCE_PLAN),
                    ],
                    input=json.dumps(evidence, separators=(",", ":")),
                    capture_output=True,
                    text=True,
                    timeout=20,
                    check=False,
                )

        clean = decide(sample_evidence())
        self.assertEqual(clean.returncode, 0, clean.stderr)
        clean_decision = json.loads(clean.stdout)
        self.assertTrue(clean_decision["conflict_free"])
        self.assertEqual(clean_decision["conflict_codes"], [])
        self.assertRegex(clean_decision["resource_plan_sha256"], r"^[A-F0-9]{64}$")

        blocked_evidence = sample_evidence()
        blocked_evidence["listening_sockets"] = [  # type: ignore[index]
            {"protocol": "tcp", "address": "::", "port": 3031},
            {"protocol": "udp", "address": "0.0.0.0", "port": 30001},
        ]
        blocked_evidence["network_state"]["addresses"] = [  # type: ignore[index]
            {
                "interface": "eth0", "family": "inet", "address": "172.29.251.9",
                "prefix_length": 24, "scope": "global",
            }
        ]
        blocked_evidence["network_state"]["routes"] = [  # type: ignore[index]
            {
                "family": "inet", "destination": "10.212.12.0/24", "gateway": None,
                "interface": "eth0", "table": "main", "protocol": "kernel",
                "scope": "link", "type": "unicast", "multipath": [],
            }
        ]
        blocked_evidence["candidates"]["paths"][0]["exists"] = True  # type: ignore[index]
        blocked = decide(blocked_evidence)
        self.assertEqual(blocked.returncode, 0, blocked.stderr)
        blocked_decision = json.loads(blocked.stdout)
        self.assertFalse(blocked_decision["conflict_free"])
        self.assertEqual(
            set(blocked_decision["conflict_codes"]),
            {
                "TCP_3031_BIND_CONFLICT",
                "UDP_30001_BIND_CONFLICT",
                "ADDRESS_OVERLAP_172_29_251_0_28",
                "ROUTE_OVERLAP_10_212_12_0_24",
                "CANDIDATE_PATH_PRESENT",
            },
        )
        rendered = json.dumps(blocked_decision, separators=(",", ":"))
        self.assertNotIn("172.29.251.9", rendered)
        self.assertNotIn("eth0", rendered)

        incompatible = sample_evidence()
        incompatible["platform"]["kernel"]["release"] = "5.15.0"  # type: ignore[index]
        incompatible["platform"]["os_release"] = {"id": "debian", "version_id": "12"}  # type: ignore[index]
        incompatible["platform"]["python3"] = {"version": "3.11.9", "soabi": "cpython-311-x86_64-linux-gnu"}  # type: ignore[index]
        incompatible["platform"]["glibc_version"] = "2.36"  # type: ignore[index]
        incompatible["capacity"]["mem_available_bytes"] = 1024  # type: ignore[index]
        incompatible["capacity"]["filesystems"][-1]["available_bytes"] = 1024  # type: ignore[index]
        incompatible["capacity"]["filesystems"][-1]["available_inodes"] = 1  # type: ignore[index]
        incompatible["firewall"]["structured_snapshot"] = {  # type: ignore[index]
            "nftables": [{"table": {"family": "inet", "name": "amn2_spain"}}]
        }
        result = decide(incompatible)
        self.assertEqual(result.returncode, 0, result.stderr)
        decision = json.loads(result.stdout)
        self.assertFalse(decision["conflict_free"])
        self.assertEqual(
            set(decision["conflict_codes"]),
            {
                "PLATFORM_OS_INCOMPATIBLE",
                "PLATFORM_KERNEL_INCOMPATIBLE",
                "PLATFORM_PYTHON_INCOMPATIBLE",
                "PLATFORM_GLIBC_INCOMPATIBLE",
                "CAPACITY_MEMORY_INSUFFICIENT",
                "CAPACITY_DISK_INSUFFICIENT",
                "CAPACITY_INODES_INSUFFICIENT",
                "FIREWALL_NAMESPACE_PRESENT",
            },
        )

    def test_conflict_decision_covers_every_owned_candidate_class(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for code in (
            "CANDIDATE_PATH_PRESENT",
            "CANDIDATE_IDENTITY_PRESENT",
            "CANDIDATE_UNIT_PRESENT",
            "DOCKER_PRESENCE_OR_UNKNOWN",
            "CANDIDATE_NETWORK_LINK_PRESENT",
            "CANDIDATE_SOCKET_PRESENT",
            "CANDIDATE_RUNTIME_DIRECTORY_PRESENT",
            "TCP_3031_BIND_CONFLICT",
            "UDP_30001_BIND_CONFLICT",
            "ADDRESS_OVERLAP_172_29_251_0_28",
            "ADDRESS_OVERLAP_10_212_12_0_24",
            "ROUTE_OVERLAP_172_29_251_0_28",
            "ROUTE_OVERLAP_10_212_12_0_24",
            "PLATFORM_OS_INCOMPATIBLE",
            "PLATFORM_KERNEL_INCOMPATIBLE",
            "PLATFORM_PYTHON_INCOMPATIBLE",
            "PLATFORM_GLIBC_INCOMPATIBLE",
            "CAPACITY_MEMORY_INSUFFICIENT",
            "CAPACITY_DISK_INSUFFICIENT",
            "CAPACITY_INODES_INSUFFICIENT",
            "FIREWALL_NAMESPACE_PRESENT",
        ):
            self.assertIn(code, source)
        self.assertIn("Get-ConflictDecision", source)
        self.assertIn("resource_plan_sha256", source)
        self.assertIn("$PreviewResourcePlan = Get-ResourcePlanReceipt", source)
        self.assertIn("RESOURCE PLAN SHA256 $($PreviewResourcePlan.Sha256)", source)
        self.assertIn("resource_plan_sha256 = $PreviewResourcePlan.Sha256", source)
        self.assertIn("/opt/amn2-spain-package", source)
        self.assertIn("Plan.resources.uids", source)
        self.assertIn("Plan.resources.gids", source)
        self.assertIn("Plan.resources.owned_routes", source)
        self.assertIn("Plan.resources.sysctls", source)
        expected_plan = re.search(
            r'\$expectedPackageResourcePlanSha\s*=\s*"([A-F0-9]{64})"', source
        )
        self.assertIsNotNone(expected_plan)
        self.assertEqual(
            expected_plan.group(1),
            hashlib.sha256(PACKAGE_RESOURCE_PLAN.read_bytes()).hexdigest().upper(),
        )
        self.assertIn("conflict_free", source)
        self.assertIn("conflict_codes", source)

    def test_runner_verifies_protected_run009_firewall_before_approval_preview(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for marker in (
            "function Get-Run009EvidenceReceipt",
            "spain-fresh-20260721-009",
            "preflight-evidence.json",
            "$run009EvidenceSha",
            "$run009FirewallBackend",
            "$run009FirewallRulesSha",
            "$run009FirewallRuleCount",
            "$PreviewRun009 = Get-Run009EvidenceReceipt",
            "RUN009 REFERENCE SHA256 $($PreviewRun009.EvidenceSha256)",
        ):
            self.assertIn(marker, source)
        self.assertLess(
            source.index("$PreviewRun009 = Get-Run009EvidenceReceipt"),
            source.index("if ([string]::IsNullOrEmpty($Approval))"),
        )

    def test_ssh_is_public_key_only_noninteractive_and_bounded(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for option in (
            "PreferredAuthentications=publickey",
            "PasswordAuthentication=no",
            "KbdInteractiveAuthentication=no",
            "GSSAPIAuthentication=no",
            "ForwardAgent=no",
            "ClearAllForwardings=yes",
            "RequestTTY=no",
            "ConnectTimeout=10",
            "ServerAliveInterval=10",
            "ServerAliveCountMax=2",
        ):
            self.assertIn(option, source)

    def test_post_claim_outcomes_are_atomic_sanitized_and_single_use(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for marker in (
            "function Write-AtomicPrivateJsonCreateNew",
            "[IO.FileMode]::CreateNew",
            "[IO.File]::Move",
            "function Write-SanitizedOutcomeReceipt",
            "claim_sha256",
            "USE_NEW_RUN_ID_AND_NEW_EXACT_APPROVAL",
            "resource-confirmation-failure-receipt.v1",
            "resource-confirmation-blocked-receipt.v1",
            "resource-confirmation-receipt.v2",
            "dynamic-persistent-v1",
            "resource-confirmation-evidence-second.json",
            "CONFLICT_FREE_REQUIRED",
            "AMN2_PHASE12_RESOURCE_CONFIRMATION_FAILURE_V1",
        ):
            self.assertIn(marker, source)

    def test_validated_snapshots_are_persisted_before_conflict_decision(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertLess(
            source.index("Convert-RemoteSnapshot $Result $EvidencePath"),
            source.index("$ConflictDecision = Get-ConflictDecision $Evidence"),
        )
        self.assertLess(
            source.index("Convert-RemoteSnapshot $SecondResult $EvidenceSecondPath"),
            source.index("$ConflictDecision = Get-ConflictDecision $Evidence"),
        )
        self.assertRegex(source, r"(?s)try\s*\{.*Invoke-SshWithExactInput.*\}\s*catch\s*\{")
        self.assertNotIn("$_.Exception.Message", source)
        self.assertIn("$ClaimSha", source)
        self.assertRegex(source, r"if \(\$Result\.ExitCode -ne 0\) \{\s*\$OutcomeStage = Get-SafeRemoteFailureStage")

    def test_fixture_binds_historical_run009_firewall_observation(self) -> None:
        reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
        self.assertEqual(reference["firewall_backend"], "nft")
        self.assertEqual(
            reference["firewall_raw_sha256"],
            "35ED9383AE9E73268E3D1AB7F57612BC60EA59C0531D6A96372E5F3731883D00",
        )
        self.assertEqual(reference["firewall_raw_rule_count"], 129)


class Run009CompatibilityReferenceTests(unittest.TestCase):
    def test_reference_matches_protected_run009_when_available(self) -> None:
        reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
        protected = (
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "AMN2"
            / "private-artifacts"
            / "post-release"
            / "spain-migration"
            / "spain-fresh-20260721-009"
            / "preflight-evidence.json"
        )
        if not protected.is_file():
            self.skipTest("protected run009 evidence is not present")
        raw = protected.read_bytes()
        evidence = json.loads(raw)
        fingerprint = evidence["unrelated_service_fingerprint"]
        preserved = json.dumps(fingerprint, separators=(",", ":"), ensure_ascii=False).encode()
        canonical = json.dumps(
            fingerprint, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
        fingerprint_set = json.dumps(
            sorted(fingerprint, key=lambda item: (item["kind"], item["name_sha256"])),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest().upper(), reference["evidence_sha256"])
        self.assertEqual(len(fingerprint), reference["fingerprint_count"])
        self.assertEqual(
            hashlib.sha256(preserved).hexdigest().upper(),
            reference["fingerprint_preserved_key_order_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest().upper(),
            reference["fingerprint_sorted_key_canonical_sha256"],
        )
        self.assertEqual(len(fingerprint_set), reference["fingerprint_set_bytes"])
        self.assertEqual(
            hashlib.sha256(fingerprint_set).hexdigest().upper(),
            reference["fingerprint_set_sha256"],
        )
        self.assertEqual(evidence["firewall"]["backend"], reference["firewall_backend"])
        self.assertEqual(
            evidence["firewall"]["rules_sha256"].upper(),
            reference["firewall_raw_sha256"],
        )
        self.assertEqual(
            evidence["firewall"]["rule_count"],
            reference["firewall_raw_rule_count"],
        )

    @unittest.skipUnless(POWERSHELL.exists(), "Windows PowerShell is required")
    def test_runner_set_receipt_matches_authoritative_run009_when_available(self) -> None:
        reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
        protected = (
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "AMN2"
            / "private-artifacts"
            / "post-release"
            / "spain-migration"
            / "spain-fresh-20260721-009"
            / "preflight-evidence.json"
        )
        if not protected.is_file():
            self.skipTest("protected run009 evidence is not present")
        source = RUNNER.read_text(encoding="utf-8")
        functions = (
            extract_powershell_function(source, "Get-FingerprintSetReceipt")
            + extract_powershell_function(source, "Assert-FingerprintBaseline")
        )
        with tempfile.TemporaryDirectory() as raw_tmp:
            script = Path(raw_tmp) / "authoritative-set.ps1"
            script.write_text(
                "$ErrorActionPreference='Stop'\n"
                + functions
                + "\n$e=Get-Content -Raw -LiteralPath $args[0] | ConvertFrom-Json\n"
                + "$r=Assert-FingerprintBaseline @($e.unrelated_service_fingerprint) $args[1] ([int]$args[2])\n"
                + "Write-Output \"$($r.Sha256)|$($r.ByteLength)\"\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    str(POWERSHELL),
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                    str(protected),
                    reference["fingerprint_set_sha256"],
                    str(reference["fingerprint_set_bytes"]),
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            f'{reference["fingerprint_set_sha256"]}|{reference["fingerprint_set_bytes"]}',
        )


if __name__ == "__main__":
    unittest.main()
