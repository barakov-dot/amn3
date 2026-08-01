import re
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT / "scripts" / "vps" / "phase13_spain_awg3_readonly_preflight_remote.sh"
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
STABLE_FOREIGN_SHA256 = "f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8"
FOREIGN_RECEIPT_SHA256 = "bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704"


def collector_source() -> str:
    if not COLLECTOR.is_file():
        pytest.fail(f"missing collector: {COLLECTOR}")
    return COLLECTOR.read_text(encoding="utf-8")


def bash_function(source: str, name: str) -> str:
    match = re.search(rf"(?ms)^{re.escape(name)}\(\) \{{\n.*?^\}}\n", source)
    if not match:
        pytest.fail(f"missing standalone Bash function: {name}")
    return match.group(0)


def run_harness(source: str, function_names: tuple[str, ...], invocation: str):
    functions = "\n".join(bash_function(source, name) for name in function_names)
    script = f"set -u\n{functions}\n{invocation}\n"
    return subprocess.run(
        [str(BASH), "-c", script],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_collector_has_exact_static_contract_and_no_mutating_surface():
    source = collector_source()

    required = (
        "set -Eeuo pipefail",
        "amn2.phase13.awg3-readonly-preflight.v1",
        'readonly CANDIDATE_UDP_PORT="30002"',
        'readonly CANDIDATE_INTERFACE="awg3"',
        'readonly CANDIDATE_BRIDGE="amn2sp3br0"',
        'readonly CANDIDATE_VPN_CIDR="10.212.13.0/24"',
        'readonly CANDIDATE_CONTAINER_CIDR="172.29.252.0/28"',
        '"mutation_attempted":false',
    )
    for marker in required:
        assert marker in source

    forbidden = (
        r"\bsystemctl\s+(?:start|stop|restart|reload|enable|disable|mask|unmask)\b",
        r"\bdocker\s+(?:run|create|start|stop|restart|rm|exec)\b",
        r"\bip\s+(?:address|addr|link|route)\s+(?:add|del|delete|replace|set)\b",
        r"\bnft\s+(?:add|delete|flush|insert|replace)\b",
        r"\b(?:wg|awg)\s+(?:set|setconf|addconf|syncconf)\b",
        r"(?:^|\s)>+\s*[^&]",
        r"\btee\b",
        r"\|\|\s*true\b",
        r"2>&1",
    )
    for pattern in forbidden:
        assert not re.search(pattern, source, flags=re.MULTILINE), pattern

    assert not re.search(
        r"(?:cat|sed|awk|head|tail)\s+[^\n]*(?:runtime\.env|servers\.ya?ml|\.conf\b|private|preshared)",
        source,
        flags=re.IGNORECASE,
    )


def test_failure_envelope_accepts_only_allowlisted_stages():
    source = collector_source()
    expected = {
        "bootstrap",
        "candidate_sockets",
        "candidate_links",
        "candidate_addresses_routes",
        "candidate_docker",
        "candidate_systemd",
        "candidate_paths",
        "awg2_projection",
        "foreign_projection",
        "render",
    }
    match = re.search(r"(?ms)^readonly FAILURE_STAGES='([^']+)'$", source)
    assert match
    assert set(match.group(1).split()) == expected
    assert "AMN2_PHASE13_AWG3_PREFLIGHT_FAILURE_V1|stage=%s|exit=%s" in source


@pytest.mark.parametrize(
    ("ports", "status", "expected_rc", "expected_stdout"),
    [
        ("53,443,30002", "exact", 71, "udp_port_conflict\n"),
        ("53,443", "exact", 0, ""),
        ("", "exact", 0, ""),
        ("53,443", "partial", 72, "observation_ambiguous\n"),
    ],
)
def test_udp_port_conflict_taxonomy(ports, status, expected_rc, expected_stdout):
    source = collector_source()
    result = run_harness(
        source,
        ("classify_udp_port",),
        f"classify_udp_port 30002 {ports!r} {status!r}",
    )
    assert result.returncode == expected_rc
    assert result.stdout == expected_stdout


@pytest.mark.parametrize(
    ("reason", "candidate", "names", "status", "expected_rc", "expected_stdout"),
    [
        ("interface_conflict", "awg3", "awg0,awg3", "exact", 71, "interface_conflict\n"),
        ("bridge_conflict", "amn2sp3br0", "docker0,amn2sp3br0", "exact", 71, "bridge_conflict\n"),
        ("interface_conflict", "awg3", "awg0", "exact", 0, ""),
        ("interface_conflict", "awg3", "awg0", "partial", 72, "observation_ambiguous\n"),
    ],
)
def test_interface_and_bridge_conflict_taxonomy(
    reason, candidate, names, status, expected_rc, expected_stdout
):
    source = collector_source()
    result = run_harness(
        source,
        ("classify_name_collision",),
        f"classify_name_collision {reason!r} {candidate!r} {names!r} {status!r}",
    )
    assert result.returncode == expected_rc
    assert result.stdout == expected_stdout


@pytest.mark.parametrize(
    ("reason", "candidate", "observed", "status", "expected_rc", "expected_stdout"),
    [
        ("vpn_cidr_conflict", "10.212.13.0/24", "10.212.13.128/25", "exact", 71, "vpn_cidr_conflict\n"),
        ("container_cidr_conflict", "172.29.252.0/28", "172.29.252.8/29", "exact", 71, "container_cidr_conflict\n"),
        ("vpn_cidr_conflict", "10.212.13.0/24", "10.212.12.0/24,192.168.1.0/24", "exact", 0, ""),
        ("vpn_cidr_conflict", "10.212.13.0/24", "invalid", "exact", 72, "observation_ambiguous\n"),
        ("vpn_cidr_conflict", "10.212.13.0/24", "", "partial", 72, "observation_ambiguous\n"),
    ],
)
def test_ipv4_cidr_conflict_taxonomy(
    reason, candidate, observed, status, expected_rc, expected_stdout
):
    source = collector_source()
    result = run_harness(
        source,
        ("ipv4_to_int", "cidr_bounds", "cidr_overlap", "classify_cidr_set"),
        f"classify_cidr_set {reason!r} {candidate!r} {observed!r} {status!r}",
    )
    assert result.returncode == expected_rc
    assert result.stdout == expected_stdout


@pytest.mark.parametrize(
    ("reason", "state", "expected_rc", "expected_stdout"),
    [
        ("container_conflict", "absent", 0, ""),
        ("service_conflict", "present", 71, "service_conflict\n"),
        ("path_conflict", "symlink", 71, "path_conflict\n"),
        ("path_conflict", "unreadable", 72, "observation_ambiguous\n"),
        ("container_conflict", "unknown", 72, "observation_ambiguous\n"),
    ],
)
def test_existence_and_permission_taxonomy(reason, state, expected_rc, expected_stdout):
    source = collector_source()
    result = run_harness(
        source,
        ("classify_existence",),
        f"classify_existence {reason!r} {state!r}",
    )
    assert result.returncode == expected_rc
    assert result.stdout == expected_stdout


def test_awg2_projection_requires_the_accepted_phase13_baseline():
    source = collector_source()
    peer_hash = "a" * 64
    valid = run_harness(
        source,
        ("validate_awg2_projection",),
        "validate_awg2_projection 30001 10.212.12.0/24 amn2spbr0 "
        f"7 7 59 3 true true {peer_hash} {peer_hash}",
    )
    assert valid.returncode == 0
    assert valid.stdout == ""

    invalid = run_harness(
        source,
        ("validate_awg2_projection",),
        "validate_awg2_projection 30001 10.212.12.0/24 amn2spbr0 "
        f"7 6 59 3 true true {peer_hash} {'b' * 64}",
    )
    assert invalid.returncode == 73
    assert invalid.stdout == "awg2_equality_mismatch\n"


def test_foreign_projection_requires_the_immutable_phase12_foundation():
    source = collector_source()
    valid = run_harness(
        source,
        ("validate_foreign_projection",),
        f"validate_foreign_projection 153 {STABLE_FOREIGN_SHA256} 0 true {FOREIGN_RECEIPT_SHA256}",
    )
    assert valid.returncode == 0
    assert valid.stdout == ""

    invalid = run_harness(
        source,
        ("validate_foreign_projection",),
        f"validate_foreign_projection 152 {STABLE_FOREIGN_SHA256} 1 false {FOREIGN_RECEIPT_SHA256}",
    )
    assert invalid.returncode == 74
    assert invalid.stdout == "foreign_equality_mismatch\n"


def test_render_contract_is_secret_free_and_marks_all_observations_read_only():
    source = collector_source()
    assert '"schema":"amn2.phase13.awg3-readonly-preflight.v1"' in source
    assert '"mutation_attempted":false' in source
    assert '"remote_file_written":false' in source
    assert '"service_action_attempted":false' in source
    assert '"container_action_attempted":false' in source
    assert '"firewall_action_attempted":false' in source
    assert '"secret_bearing_config_accessed":false' in source
    assert '"raw_peer_identifiers_emitted":false' in source
    assert '"raw_output_persisted":false' in source
    assert '"declared_value":"30002"' in source
    assert '"declared_value":"awg3"' in source
    assert '"declared_value":"amn2sp3br0"' in source
    assert '"declared_value":"10.212.13.0/24"' in source
    assert '"declared_value":"172.29.252.0/28"' in source
    assert '"peer_set_sha256":"%s"' in source
    assert '"private_key"' not in source.lower()
    assert '"preshared_key"' not in source.lower()
