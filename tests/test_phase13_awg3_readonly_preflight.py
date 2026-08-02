import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT / "scripts" / "vps" / "phase13_spain_awg3_readonly_preflight_remote.sh"
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
RUNNER = ROOT / "scripts" / "vps" / "phase13_spain_awg3_readonly_preflight_ssh_runner.ps1"
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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


def prepare_runner_repo(tmp_path: Path, *, outcome_id: str, expired: bool = False) -> Path:
    if not RUNNER.is_file():
        pytest.fail(f"missing runner: {RUNNER}")
    repo = tmp_path / "repo"
    runner = repo / "scripts" / "vps" / RUNNER.name
    collector = repo / "scripts" / "vps" / COLLECTOR.name
    package = repo / "packaging" / "phase13-awg3-preflight"
    contract = repo / "scripts" / "phase13_awg3_preflight_contract.py"
    runner.parent.mkdir(parents=True)
    package.mkdir(parents=True)
    shutil.copy2(RUNNER, runner)
    shutil.copy2(COLLECTOR, collector)
    shutil.copy2(ROOT / "scripts" / contract.name, contract)
    for name in ("evidence.schema.json", "failure-evidence.schema.json", "phase12-equality-foundation.json"):
        shutil.copy2(ROOT / "packaging" / "phase13-awg3-preflight" / name, package / name)

    packaged_runner = package / runner.name
    packaged_collector = package / collector.name
    packaged_contract = package / contract.name
    shutil.copy2(runner, packaged_runner)
    shutil.copy2(collector, packaged_collector)
    shutil.copy2(contract, packaged_contract)
    artifact_paths = (packaged_runner, packaged_collector, packaged_contract, package / "evidence.schema.json", package / "failure-evidence.schema.json", package / "phase12-equality-foundation.json")
    artifacts = [
        {
            "path": path.name,
            "sha256": sha256_file(path),
            "size": path.stat().st_size,
        }
        for path in artifact_paths
    ]
    manifest = {
        "allowed_command_families": [
            "os_kernel_capacity_observation",
            "systemd_readonly_observation",
            "socket_observation",
            "ip_json_observation",
            "docker_readonly_observation",
            "nftables_readonly_observation",
            "filesystem_readonly_observation",
            "sanitized_awg2_projection",
        ],
        "artifacts": artifacts,
        "candidate": {
            "config_path": "/var/lib/amn2-spain/awg3/awg3.conf",
            "container_cidr": "172.29.252.0/28",
            "container_name": "amn2-spain-awg3",
            "host_bridge": "amn2sp3br0",
            "interface_name": "awg3",
            "protocol_version": "awg3",
            "runtime_instance_id": "spain-awg3-candidate-001",
            "server_vpn_address": "10.212.13.1/24",
            "service_name": "amn2-spain-awg3.service",
            "state_root": "/var/lib/amn2-spain/awg3",
            "udp_port": 30002,
            "vpn_cidr": "10.212.13.0/24",
        },
        "created_at": "2026-08-01T00:00:00Z",
        "expires_at": "2020-01-01T00:00:00Z" if expired else "2099-08-02T00:00:00Z",
        "forbidden_actions": [
            "systemd_action",
            "docker_mutation",
            "ip_mutation",
            "firewall_mutation",
            "awg_mutation",
            "remote_filesystem_write",
            "package_manager",
            "reboot",
            "wildcard_operation",
        ],
        "foundation_sha256": sha256_file(package / "phase12-equality-foundation.json"),
        "live_action_authorized": False,
        "max_attempts": 1,
        "outcome_id": outcome_id,
        "package_build_allowed": False,
        "remote_write_allowed": False,
        "schema": "amn2.phase13.awg3-readonly-preflight-manifest.v1",
        "source_base": "55dc243b8e6c6bdb57f8301b56326e4cd4072d19",
        "source_head": "ff115b63ca1329640ca13ae0a502d155f99b456b",
        "spain_overlay": "f1bf099ddb47da26a4080714376babaf5b0de92c",
        "target_role": "spain-primary",
    }
    (package / "phase13-awg3-preflight-manifest.json").write_bytes(canonical_json(manifest))
    return repo


def run_runner(repo: Path, outcome_id: str, *, approval: str | None = None):
    runner = repo / "scripts" / "vps" / RUNNER.name
    command = [str(POWERSHELL), "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(runner), "-Mode", "preflight", "-OutcomeId", outcome_id]
    if approval is not None:
        command.extend(("-Approval", approval))
    return subprocess.run(command, cwd=repo, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20)


def run_powershell_harness(tmp_path: Path, body: str):
    if not RUNNER.is_file():
        pytest.fail(f"missing runner: {RUNNER}")
    harness = tmp_path / "harness.ps1"
    harness.write_text(
        "$ErrorActionPreference = 'Stop'\n"
        "$utf8 = New-Object Text.UTF8Encoding($false)\n"
        "[Console]::OutputEncoding = $utf8\n"
        "[Console]::InputEncoding = $utf8\n"
        "$OutputEncoding = $utf8\n"
        f". '{RUNNER}' -Mode preflight -OutcomeId test-outcome-001\n"
        + body,
        encoding="utf-8",
    )
    return subprocess.run(
        [str(POWERSHELL), "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(harness)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
    )


def prepare_fake_trust_bundle(tmp_path: Path, *, binding_key_path: Path | None = None):
    trust_root = tmp_path / "trust"
    trust_root.mkdir()
    key_path = trust_root / "id_ed25519_spain"
    public_key_path = trust_root / "id_ed25519_spain.pub"
    known_hosts_path = trust_root / "known_hosts_spain"
    binding_path = trust_root / "target.env"
    fake_keygen = tmp_path / "fake-ssh-keygen.ps1"
    target_host = "spain.test.invalid"
    target_user = "operator"
    fingerprint = "SHA256:" + ("A" * 43)
    key_path.write_text("private-test-material\n", encoding="utf-8")
    public_key_path.write_text("ssh-ed25519 VEVTVEtFWQ== test\n", encoding="utf-8")
    known_hosts_path.write_text(
        f"{target_host} ssh-ed25519 VEVTVEtFWQ==\n", encoding="utf-8"
    )
    bound_key_path = binding_key_path or key_path
    binding_path.write_text(
        "\n".join(
            (
                f"TARGET_HOST={target_host}",
                f"TARGET_USER={target_user}",
                f"SSH_KEY_PATH={bound_key_path}",
                f"EXPECTED_HOST_KEY_SHA256={fingerprint}",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    fake_keygen.write_text(
        """if ($args[0] -ceq '-y') {
    Write-Output 'ssh-ed25519 VEVTVEtFWQ=='
    exit 0
}
if ($args[0] -ceq '-lf') {
    Write-Output '256 SHA256:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA fake (ED25519)'
    exit 0
}
exit 1
""",
        encoding="utf-8",
    )
    return {
        "root": trust_root,
        "binding": binding_path,
        "key": key_path,
        "public_key": public_key_path,
        "known_hosts": known_hosts_path,
        "keygen": fake_keygen,
        "target_host": target_host,
        "target_user": target_user,
        "fingerprint": fingerprint,
    }


def trust_bundle_acl_setup(bundle: dict[str, Path | str], *, protect_root: bool = True) -> str:
    paths = [bundle["binding"], bundle["key"], bundle["public_key"], bundle["known_hosts"]]
    if protect_root:
        paths.insert(0, bundle["root"])
    quoted_paths = ",".join(f"'{path}'" for path in paths)
    return f"""
function Protect-TestTrustPath([string]$Path) {{
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $acl = Get-Acl -LiteralPath $Path
    $acl.SetOwner($sid)
    $acl.SetAccessRuleProtection($true, $false)
    foreach ($rule in @($acl.Access)) {{ $acl.RemoveAccessRuleSpecific($rule) }}
    $allow = New-Object Security.AccessControl.FileSystemAccessRule(
        $sid,
        [Security.AccessControl.FileSystemRights]::FullControl,
        [Security.AccessControl.InheritanceFlags]::None,
        [Security.AccessControl.PropagationFlags]::None,
        [Security.AccessControl.AccessControlType]::Allow
    )
    $acl.SetAccessRule($allow)
    Set-Acl -LiteralPath $Path -AclObject $acl
}}
foreach ($path in @({quoted_paths})) {{ Protect-TestTrustPath $path }}
"""


def valid_success_evidence_for_manifest(manifest_path: Path) -> bytes:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_sha = hashlib.sha256(canonical_json(manifest)).hexdigest()
    artifact_hashes = {
        Path(artifact["path"]).name: artifact["sha256"]
        for artifact in manifest["artifacts"]
    }
    evidence = {
        "awg2_equality": {
            "bot_disabled": True,
            "container_equal": True,
            "equal": True,
            "forward_rule_count": 3,
            "interface_equal": True,
            "live_peers": 7,
            "peer_set_sha256": "5" * 64,
            "persistent_peers": 7,
            "restart_count": 59,
            "service_equal": True,
            "udp_port_equal": True,
            "vpn_cidr_route_equal": True,
            "web_listener_equal": True,
        },
        "candidate_resources": [{"declared_value": "30002", "observation_sha256": "4" * 64, "resource": "udp_port", "state": "free"}],
        "checked_at": "2026-08-01T12:00:00Z",
        "collector_sha256": artifact_hashes[
            "phase13_spain_awg3_readonly_preflight_remote.sh"
        ],
        "decision": "pass",
        "foreign_equality": {
            "changed": 0,
            "equal": True,
            "equality_receipt_sha256": FOREIGN_RECEIPT_SHA256,
            "persistent_entries": 153,
            "stable_sha256": STABLE_FOREIGN_SHA256,
        },
        "manifest_sha256": manifest_sha,
        "outcome_id": manifest["outcome_id"],
        "phase12_foundation_sha256": manifest["foundation_sha256"],
        "runner_sha256": artifact_hashes[
            "phase13_spain_awg3_readonly_preflight_ssh_runner.ps1"
        ],
        "safety_receipt": {
            "container_action_attempted": False,
            "firewall_action_attempted": False,
            "mutation_attempted": False,
            "raw_output_persisted": False,
            "raw_peer_identifiers_emitted": False,
            "remote_file_written": False,
            "secret_bearing_config_accessed": False,
            "service_action_attempted": False,
        },
        "schema": "amn2.phase13.awg3-readonly-preflight.v1",
        "schema_sha256": artifact_hashes["evidence.schema.json"],
        "source_head": manifest["source_head"],
        "stop_reasons": [],
    }
    return canonical_json(evidence)


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
    assert invalid.returncode == 70
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
    assert invalid.returncode == 69
    assert invalid.stdout == "foreign_equality_mismatch\n"


def test_collector_observes_awg2_and_foreign_state_without_projection_environment_inputs():
    source = collector_source()

    assert "AMN2_PHASE13_AWG2_" not in source
    assert "AMN2_PHASE13_FOREIGN_" not in source
    for marker in (
        'readonly SYSTEM_DOCKER="/usr/bin/docker"',
        'readonly SPAIN_DOCKER="/opt/amn2-spain/docker/bin/docker"',
        'readonly SPAIN_DOCKER_HOST="unix:///run/amn2-spain-docker/docker.sock"',
        'readonly ACCEPTED_AWG2_CONTAINER="amn2-spain-awg"',
        'readonly ACCEPTED_AWG2_INTERFACE="awg0"',
        'readonly ACCEPTED_AWG2_DB="/var/lib/amn2-spain/amn2.sqlite3"',
        "observe_awg2_projection",
        "observe_foreign_projection",
        "system_docker ps -a --format '{{.Names}}'",
        "system_docker network ls -q",
        "spain_docker ps -a --format '{{.Names}}'",
        "spain_docker network ls -q",
        '"--root=/proc/${pid}/root"',
        '"amn2_spain:compat-forward-dnat"',
        '"amn2_spain:compat-forward-outbound"',
        '"amn2_spain:compat-forward-return"',
    ):
        assert marker in source
    assert re.search(r"(?m)^\s*docker\s", source) is None


def test_peer_projection_normalizes_exact_public_key_set_without_emitting_keys():
    source = collector_source()
    peers = [f"{letter}{'A' * 42}=" for letter in "ABCDEFG"]
    expected_hash = hashlib.sha256(("\n".join(peers) + "\n").encode()).hexdigest()
    payload = "\n".join(reversed(peers))
    payload_literal = "$'" + payload.replace("'", "\\'").replace("\n", "\\n") + "'"
    result = run_harness(
        source,
        ("normalize_peer_projection",),
        f"normalize_peer_projection {payload_literal}",
    )

    assert result.returncode == 0
    assert result.stdout == f"7|{expected_hash}\n"
    assert all(peer not in result.stdout for peer in peers)


@pytest.mark.parametrize(
    "payload",
    [
        "A" * 43 + "=\n" + "A" * 43 + "=",
        "not-a-wireguard-public-key",
        "",
    ],
)
def test_peer_projection_fails_closed_on_duplicate_malformed_or_empty_input(payload):
    source = collector_source()
    payload_literal = "$'" + payload.replace("'", "\\'").replace("\n", "\\n") + "'"
    result = run_harness(
        source,
        ("normalize_peer_projection",),
        f"normalize_peer_projection {payload_literal}",
    )

    assert result.returncode == 72
    assert result.stdout == "observation_ambiguous\n"


@pytest.mark.parametrize(
    ("before", "after", "expected_rc", "expected_stdout"),
    [
        ("true|59|1234", "true|59|1234", 0, ""),
        ("true|59|1234", "true|60|1234", 72, "observation_ambiguous\n"),
        ("true|59|1234", "true|59|5678", 72, "observation_ambiguous\n"),
        ("true|59|1234", "false|59|1234", 72, "observation_ambiguous\n"),
    ],
)
def test_awg2_container_identity_must_remain_stable_across_observation(
    before, after, expected_rc, expected_stdout
):
    source = collector_source()
    result = run_harness(
        source,
        ("validate_awg2_container_stability",),
        f"validate_awg2_container_stability {before!r} {after!r}",
    )

    assert result.returncode == expected_rc
    assert result.stdout == expected_stdout


def test_foreign_projection_receipt_is_canonical_and_identity_unique():
    source = collector_source()
    container_name = "1" * 64
    container_image = "2" * 64
    unit_name = "3" * 64
    unit_content = "4" * 64
    rows = (
        f"unit|{unit_name}|{unit_content}|active:running|exact|cgroup_complete\n"
        f"container|{container_name}|{container_image}|running||"
    )
    canonical = [
        {
            "active_state": "running",
            "image_or_unit_sha256": container_image,
            "kind": "container",
            "name_sha256": container_name,
        },
        {
            "active_state": "active:running",
            "bound_port_status": "cgroup_complete",
            "image_or_unit_sha256": unit_content,
            "kind": "unit",
            "name_sha256": unit_name,
            "unit_content_status": "exact",
        },
    ]
    expected_hash = hashlib.sha256(canonical_json(canonical)).hexdigest()
    rows_literal = "$'" + rows.replace("'", "\\'").replace("\n", "\\n") + "'"
    result = run_harness(
        source,
        ("build_foreign_stable_receipt",),
        f"build_foreign_stable_receipt {rows_literal} python",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == f"2|{expected_hash}\n"

    duplicate = run_harness(
        source,
        ("build_foreign_stable_receipt",),
        "build_foreign_stable_receipt $'"
        + (rows + "\n" + rows.splitlines()[0]).replace("'", "\\'").replace("\n", "\\n")
        + "' python",
    )
    assert duplicate.returncode == 72
    assert duplicate.stdout == "observation_ambiguous\n"


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


def test_missing_approval_prints_exact_phrase_before_private_or_network_access(tmp_path):
    repo = prepare_runner_repo(tmp_path, outcome_id="test-outcome-001")
    result = run_runner(repo, "test-outcome-001")

    assert result.returncode == 64
    assert result.stdout.startswith("УТВЕРЖДАЮ ОДИН READ-ONLY SPAIN PREFLIGHT ")
    assert "NO_PACKAGE_BUILD_NO_DEPLOY_NO_MUTATION" in result.stdout
    combined = (result.stdout + result.stderr).casefold()
    assert "ssh.exe" not in combined
    assert "target.env" not in combined


def test_non_exact_approval_blocks_before_private_or_network_access(tmp_path):
    repo = prepare_runner_repo(tmp_path, outcome_id="test-outcome-approval-mismatch")
    phrase = run_runner(repo, "test-outcome-approval-mismatch").stdout.strip()

    result = run_runner(
        repo,
        "test-outcome-approval-mismatch",
        approval=phrase + " ДОПОЛНЕНИЕ",
    )

    assert result.returncode == 64
    assert "approval_validation" in result.stdout
    combined = (result.stdout + result.stderr).casefold()
    assert "ssh.exe" not in combined
    assert "target.env" not in combined


def test_runner_cannot_take_user_supplied_observed_projection_or_live_target():
    source = RUNNER.read_text(encoding="utf-8")
    public_param_block = source.split(")\n\nSet-StrictMode", 1)[0]

    assert "$env:AMN2_PHASE13_AWG2" not in source
    assert "$env:AMN2_PHASE13_FOREIGN" not in source
    assert "GetEnvironmentVariable" not in source
    assert "TargetPath" not in public_param_block
    assert "KeyPath" not in public_param_block
    assert "ManifestPath" not in public_param_block
    assert '"spain-fresh-20260720-001"' in source
    assert '"runtime_capability_unavailable"' in source


@pytest.mark.parametrize(
    "artifact_name",
    [
        RUNNER.name,
        COLLECTOR.name,
        "evidence.schema.json",
        "phase12-equality-foundation.json",
    ],
)
def test_manifest_artifact_checksum_mismatch_blocks_before_approval_and_ssh(
    tmp_path, artifact_name
):
    repo = prepare_runner_repo(tmp_path, outcome_id="test-outcome-002")
    phrase = run_runner(repo, "test-outcome-002").stdout.strip()
    artifact = repo / "packaging" / "phase13-awg3-preflight" / artifact_name
    artifact.write_bytes(artifact.read_bytes() + b"# drift\n")

    result = run_runner(repo, "test-outcome-002", approval=phrase)

    assert result.returncode == 65
    assert "artifact_checksum_mismatch" in result.stdout
    assert "ssh.exe" not in (result.stdout + result.stderr).casefold()


def test_expired_manifest_blocks_before_approval_private_state_and_ssh(tmp_path):
    repo = prepare_runner_repo(tmp_path, outcome_id="test-outcome-003", expired=True)
    result = run_runner(repo, "test-outcome-003")

    assert result.returncode == 66
    assert "outcome_replay" in result.stdout
    combined = (result.stdout + result.stderr).casefold()
    assert "ssh.exe" not in combined
    assert "target.env" not in combined


def test_create_new_writer_refuses_replacement_and_preserves_first_bytes(tmp_path):
    target = tmp_path / "claim.json"
    result = run_powershell_harness(
        tmp_path,
        f"""
$path = '{target}'
Write-BytesCreateNew -Path $path -Bytes ([Text.Encoding]::UTF8.GetBytes('{{\"first\":true}}'))
$rejected = $false
try {{ Write-BytesCreateNew -Path $path -Bytes ([Text.Encoding]::UTF8.GetBytes('{{\"second\":true}}')) }} catch {{ $rejected = $true }}
[Console]::Out.Write((Get-Content -Raw -LiteralPath $path) + '|' + $rejected.ToString().ToLowerInvariant())
""",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == '{"first":true}|true'


def test_private_outcome_claim_is_create_new_and_contains_no_target_material(tmp_path):
    outcome_root = tmp_path / "outcomes"
    result = run_powershell_harness(
        tmp_path,
        f"""
$root = '{outcome_root}'
$sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$claim = New-Phase13OutcomeClaim -OutcomeRoot $root -OutcomeId 'test-outcome-claim-001' -OwnerSid $sid -ManifestSha256 ('a' * 64) -RunnerSha256 ('b' * 64) -CollectorSha256 ('c' * 64) -TargetRole 'spain-primary'
$replayed = $false
try {{ New-Phase13OutcomeClaim -OutcomeRoot $root -OutcomeId 'test-outcome-claim-001' -OwnerSid $sid -ManifestSha256 ('a' * 64) -RunnerSha256 ('b' * 64) -CollectorSha256 ('c' * 64) -TargetRole 'spain-primary' }} catch {{ $replayed = $true }}
$document = Get-Content -Raw -LiteralPath $claim | ConvertFrom-Json
[Console]::Out.Write("$($replayed.ToString().ToLowerInvariant())|$($document.PSObject.Properties.Name -join ',')")
""",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "true|schema,outcome_id,manifest_sha256,runner_sha256,collector_sha256,"
        "target_role,created_at"
    )


def test_runner_creates_claim_before_the_one_ssh_transport():
    source = RUNNER.read_text(encoding="utf-8")
    claim_call = source.index("New-Phase13OutcomeClaim", source.index("$OutcomeRoot"))
    transport_call = source.index("Invoke-Phase13OneSshTransport", claim_call)
    assert claim_call < transport_call


def test_private_path_rejects_wrong_owner_weak_acl_and_reparse_point(tmp_path):
    private_dir = tmp_path / "private"
    private_dir.mkdir()
    junction = tmp_path / "junction"
    result = run_powershell_harness(
        tmp_path,
        f"""
$currentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$wrongOwner = $false
try {{ Assert-PrivatePath -Path '{private_dir}' -ExpectedOwnerSid 'S-1-0-0' }} catch {{ $wrongOwner = $true }}
$weakAcl = $false
try {{ Assert-PrivatePath -Path '{private_dir}' -ExpectedOwnerSid $currentSid }} catch {{ $weakAcl = $true }}
New-Item -ItemType Junction -Path '{junction}' -Target '{private_dir}' | Out-Null
$reparse = $false
try {{ Assert-PrivatePath -Path '{junction}' -ExpectedOwnerSid $currentSid }} catch {{ $reparse = $true }}
[Console]::Out.Write("$($wrongOwner.ToString().ToLowerInvariant())|$($weakAcl.ToString().ToLowerInvariant())|$($reparse.ToString().ToLowerInvariant())")
""",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|true|true"


def test_phase12_trust_bundle_adapter_accepts_exact_private_binding_without_secret_output(tmp_path):
    bundle = prepare_fake_trust_bundle(tmp_path)
    result = run_powershell_harness(
        tmp_path,
        trust_bundle_acl_setup(bundle)
        + f"""
$sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$binding = Read-Phase13TrustBinding -TrustRoot '{bundle['root']}' -BindingPath '{bundle['binding']}' -KeyPath '{bundle['key']}' -ExpectedOwnerSid $sid
Assert-Phase13DedicatedEd25519KeyPair -PrivateKeyPath '{bundle['key']}' -PublicKeyPath '{bundle['public_key']}' -SshKeygenExecutable '{bundle['keygen']}' -ExpectedOwnerSid $sid
Assert-Phase13VerifiedHostPin -KnownHostsPath '{bundle['known_hosts']}' -Binding $binding -SshKeygenExecutable '{bundle['keygen']}' -ExpectedOwnerSid $sid
[Console]::Out.Write('passed')
""",
    )

    combined = result.stdout + result.stderr
    assert result.returncode == 0, result.stderr
    assert result.stdout == "passed"
    assert bundle["target_host"] not in combined
    assert bundle["target_user"] not in combined
    assert str(bundle["key"]) not in combined
    assert bundle["fingerprint"] not in combined


@pytest.mark.parametrize("scenario", ["key_path", "key_pair", "host_pin", "fingerprint"])
def test_phase12_trust_bundle_adapter_fails_closed_on_trust_material_mismatch(
    tmp_path, scenario
):
    bundle = prepare_fake_trust_bundle(tmp_path)
    mismatched_key = tmp_path / "not-the-dedicated-key"
    mutations = {
        "key_path": f"(Get-Content -LiteralPath '{bundle['binding']}') -replace '^SSH_KEY_PATH=.*$', 'SSH_KEY_PATH={mismatched_key}' | Set-Content -LiteralPath '{bundle['binding']}' -Encoding UTF8",
        "key_pair": f"Set-Content -LiteralPath '{bundle['public_key']}' -Value 'ssh-ed25519 QUJDRA== test' -Encoding UTF8",
        "host_pin": f"Set-Content -LiteralPath '{bundle['known_hosts']}' -Value 'different.test.invalid ssh-ed25519 VEVTVEtFWQ==' -Encoding UTF8",
        "fingerprint": f"(Get-Content -LiteralPath '{bundle['binding']}') -replace '^EXPECTED_HOST_KEY_SHA256=.*$', 'EXPECTED_HOST_KEY_SHA256=SHA256:{'B' * 43}' | Set-Content -LiteralPath '{bundle['binding']}' -Encoding UTF8",
    }
    result = run_powershell_harness(
        tmp_path,
        trust_bundle_acl_setup(bundle)
        + f"""
$sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$baseline = Read-Phase13TrustBinding -TrustRoot '{bundle['root']}' -BindingPath '{bundle['binding']}' -KeyPath '{bundle['key']}' -ExpectedOwnerSid $sid
Assert-Phase13DedicatedEd25519KeyPair -PrivateKeyPath '{bundle['key']}' -PublicKeyPath '{bundle['public_key']}' -SshKeygenExecutable '{bundle['keygen']}' -ExpectedOwnerSid $sid
Assert-Phase13VerifiedHostPin -KnownHostsPath '{bundle['known_hosts']}' -Binding $baseline -SshKeygenExecutable '{bundle['keygen']}' -ExpectedOwnerSid $sid
{mutations[scenario]}
$rejected = $false
try {{
    $binding = Read-Phase13TrustBinding -TrustRoot '{bundle['root']}' -BindingPath '{bundle['binding']}' -KeyPath '{bundle['key']}' -ExpectedOwnerSid $sid
    Assert-Phase13DedicatedEd25519KeyPair -PrivateKeyPath '{bundle['key']}' -PublicKeyPath '{bundle['public_key']}' -SshKeygenExecutable '{bundle['keygen']}' -ExpectedOwnerSid $sid
    Assert-Phase13VerifiedHostPin -KnownHostsPath '{bundle['known_hosts']}' -Binding $binding -SshKeygenExecutable '{bundle['keygen']}' -ExpectedOwnerSid $sid
}} catch {{ $rejected = $true }}
[Console]::Out.Write($rejected.ToString().ToLowerInvariant())
""",
    )

    combined = result.stdout + result.stderr
    assert result.returncode == 0, result.stderr
    assert result.stdout == "true"
    assert bundle["target_host"] not in combined
    assert bundle["target_user"] not in combined
    assert str(bundle["key"]) not in combined
    assert bundle["fingerprint"] not in combined


def test_phase12_trust_bundle_adapter_rejects_unprotected_root_acl(tmp_path):
    bundle = prepare_fake_trust_bundle(tmp_path)
    result = run_powershell_harness(
        tmp_path,
        trust_bundle_acl_setup(bundle)
        + f"""
$sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$baseline = Read-Phase13TrustBinding -TrustRoot '{bundle['root']}' -BindingPath '{bundle['binding']}' -KeyPath '{bundle['key']}' -ExpectedOwnerSid $sid
$rootAcl = Get-Acl -LiteralPath '{bundle['root']}'
$rootAcl.SetAccessRuleProtection($false, $true)
Set-Acl -LiteralPath '{bundle['root']}' -AclObject $rootAcl
$rejected = $false
try {{ Read-Phase13TrustBinding -TrustRoot '{bundle['root']}' -BindingPath '{bundle['binding']}' -KeyPath '{bundle['key']}' -ExpectedOwnerSid $sid }} catch {{ $rejected = $true }}
[Console]::Out.Write($rejected.ToString().ToLowerInvariant())
""",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true"


def test_runner_binds_phase12_trust_adapter_after_claim_to_fixed_private_bundle():
    source = RUNNER.read_text(encoding="utf-8")
    claim_call = source.index("New-Phase13OutcomeClaim", source.index("$OutcomeRoot"))
    trust_call = source.index("Read-Phase13TrustBinding", claim_call)
    transport_call = source.index("Invoke-Phase13OneSshTransport", trust_call)

    assert claim_call < trust_call < transport_call
    assert '"post-release\\spain-migration\\$($script:TrustedBundleRunId)"' in source
    assert '"C:\\Windows\\System32\\OpenSSH\\ssh.exe"' in source
    assert '"C:\\Windows\\System32\\OpenSSH\\ssh-keygen.exe"' in source


def test_one_ssh_transport_starts_once_and_delivers_exact_collector_bytes(tmp_path):
    fake_ssh = tmp_path / "fake_ssh.py"
    counter = tmp_path / "counter.txt"
    captured = tmp_path / "stdin.bin"
    collector = b"#!/usr/bin/env bash\nset -Eeuo pipefail\n"
    fake_ssh.write_text(
        """from pathlib import Path
import sys
counter = Path(sys.argv[1])
captured = Path(sys.argv[2])
count = int(counter.read_text()) if counter.exists() else 0
counter.write_text(str(count + 1))
captured.write_bytes(sys.stdin.buffer.read())
sys.stdout.buffer.write(b'{}\\n')
""",
        encoding="utf-8",
    )
    collector_b64 = __import__("base64").b64encode(collector).decode("ascii")
    result = run_powershell_harness(
        tmp_path,
        f"""
$result = Invoke-Phase13OneSshTransport -SshExecutable '{sys.executable}' -SshArguments @('{fake_ssh}', '{counter}', '{captured}') -CollectorBytes ([Convert]::FromBase64String('{collector_b64}')) -TimeoutMilliseconds 2000 -MaximumOutputBytes 4096
[Console]::Out.Write("$($result.Reason)|$($result.ExitCode)|$($result.Document)|$($result.PSObject.Properties.Name -join ',')")
""",
    )

    assert result.returncode == 0, result.stderr
    assert counter.read_text() == "1"
    assert captured.read_bytes() == collector
    assert result.stdout == "success|0|{}|Reason,Document,ExitCode"


def test_one_ssh_transport_drops_raw_stderr_from_sanitized_result(tmp_path):
    fake_ssh = tmp_path / "fake_ssh.py"
    fake_ssh.write_text(
        """import sys
sys.stdin.buffer.read()
sys.stderr.buffer.write(b'private-target-material')
raise SystemExit(255)
""",
        encoding="utf-8",
    )
    result = run_powershell_harness(
        tmp_path,
        f"""
$result = Invoke-Phase13OneSshTransport -SshExecutable '{sys.executable}' -SshArguments @('{fake_ssh}') -CollectorBytes ([Text.Encoding]::UTF8.GetBytes('collector')) -TimeoutMilliseconds 2000 -MaximumOutputBytes 4096
[Console]::Out.Write("$($result.Reason)|$($result.Document)|$($result.PSObject.Properties.Name -join ',')")
""",
    )

    combined = result.stdout + result.stderr
    assert result.returncode == 0, result.stderr
    assert result.stdout == "unknown_remote_outcome||Reason,Document,ExitCode"
    assert "private-target-material" not in combined


def test_success_evidence_filter_rejects_secret_patterns_and_target_literals(tmp_path):
    result = run_powershell_harness(
        tmp_path,
        """
$safe = Test-Phase13EvidenceSecretSafe -EvidenceBytes ([Text.Encoding]::UTF8.GetBytes('{"state":"free"}`n')) -SensitiveValues @('spain.test.invalid', 'operator', 'C:\\private\\key', 'SHA256:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
$target = Test-Phase13EvidenceSecretSafe -EvidenceBytes ([Text.Encoding]::UTF8.GetBytes('{"state":"spain.test.invalid"}`n')) -SensitiveValues @('spain.test.invalid')
$secret = Test-Phase13EvidenceSecretSafe -EvidenceBytes ([Text.Encoding]::UTF8.GetBytes('{"PrivateKey":"raw"}`n')) -SensitiveValues @()
[Console]::Out.Write("$($safe.ToString().ToLowerInvariant())|$($target.ToString().ToLowerInvariant())|$($secret.ToString().ToLowerInvariant())")
""",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false|false"


@pytest.mark.parametrize(
    ("reason", "remote_exit", "expected"),
    [
        ("transport_timeout", -1, "transport|observation_ambiguous|timeout|67"),
        ("output_oversized", -1, "transport|observation_ambiguous|output_oversized|67"),
        ("unknown_remote_outcome", 255, "transport|observation_ambiguous|ssh_exit_unclassified|67"),
        ("unexpected_transport_reason", -1, "transport|observation_ambiguous|transport_internal_failure|67"),
        ("schema_validation_failed", 0, "schema_validation|schema_validation_failed|not_applicable|68"),
        ("SCHEMA_VALIDATION_FAILED", 0, "transport|observation_ambiguous|transport_internal_failure|67"),
        ("invalid_utf8", 0, "schema_validation|schema_validation_failed|not_applicable|68"),
        ("crlf_corruption", 0, "schema_validation|schema_validation_failed|not_applicable|68"),
        ("extra_output", 0, "schema_validation|schema_validation_failed|not_applicable|68"),
        ("collector_failure", 71, "collector|observation_ambiguous|not_applicable|71"),
    ],
)
def test_transport_failure_mapping_is_sanitized_and_fail_closed(
    tmp_path, reason, remote_exit, expected
):
    result = run_powershell_harness(
        tmp_path,
        f"""
$transport = [pscustomobject]@{{ Reason = '{reason}'; Document = 'raw-not-returned'; ExitCode = {remote_exit} }}
$failure = Resolve-Phase13TransportFailure -TransportResult $transport
[Console]::Out.Write("$($failure.Stage)|$($failure.ReasonCode)|$($failure.TransportSubreason)|$($failure.ExitCode)")
""",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == expected
    assert "raw-not-returned" not in result.stdout


def test_phase13_ssh_arguments_are_fixed_pinned_and_noninteractive(tmp_path):
    result = run_powershell_harness(
        tmp_path,
        f"""
$binding = @{{ TARGET_USER = 'operator'; TARGET_HOST = 'spain.test.invalid' }}
$arguments = New-Phase13SshArguments -Binding $binding -KnownHostsPath '{tmp_path / 'known hosts'}' -KeyPath '{tmp_path / 'dedicated key'}' -OutcomeId 'test-outcome-001' -ManifestSha256 ('a' * 64) -RunnerSha256 ('b' * 64) -CollectorSha256 ('c' * 64) -SchemaSha256 ('d' * 64) -FoundationSha256 ('e' * 64)
[Console]::Out.Write(($arguments | ConvertTo-Json -Compress))
""",
    )

    assert result.returncode == 0, result.stderr
    arguments = json.loads(result.stdout)
    assert arguments[:-1] == [
        "-T",
        "-F",
        "none",
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=yes",
        "-o",
        f"UserKnownHostsFile={tmp_path / 'known hosts'}",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "ConnectionAttempts=1",
        "-o",
        "ServerAliveInterval=5",
        "-o",
        "ServerAliveCountMax=1",
        "-i",
        str(tmp_path / "dedicated key"),
        "-p",
        "22",
        "operator@spain.test.invalid",
    ]
    remote_command = arguments[-1]
    assert remote_command.endswith("bash -s -- preflight")
    assert "AMN2_PHASE13_OUTCOME_ID=test-outcome-001" in remote_command
    assert "AMN2_PHASE13_MANIFEST_SHA256=" + ("a" * 64) in remote_command
    assert "accept-new" not in remote_command.casefold()


def test_runner_orders_claim_trust_and_one_ssh_without_legacy_stop():
    source = RUNNER.read_text(encoding="utf-8")
    claim_call = source.index("New-Phase13OutcomeClaim", source.index("$OutcomeRoot"))
    trust_call = source.index("Read-Phase13TrustBinding", claim_call)
    transport_call = source.index("Invoke-Phase13OneSshTransport", trust_call)

    assert claim_call < trust_call < transport_call
    assert source.count("Invoke-Phase13OneSshTransport", transport_call) == 1
    assert (
        'Write-RunnerFailureLine "trust_binding" "runtime_capability_unavailable"'
        not in source[transport_call:]
    )


@pytest.mark.parametrize(
    ("scenario", "expected_reason"),
    [
        ("success", "success"),
        ("failure", "collector_failure"),
        ("timeout", "transport_timeout"),
        ("extra", "extra_output"),
        ("crlf", "crlf_corruption"),
        ("invalid", "invalid_utf8"),
        ("oversized", "output_oversized"),
        ("unknown", "unknown_remote_outcome"),
    ],
)
def test_fake_ssh_transport_envelope_is_bounded_and_fail_closed(tmp_path, scenario, expected_reason):
    fake = tmp_path / "fake_ssh.py"
    fake.write_text(
        """import os, sys, time
scenario = sys.argv[1]
if scenario == 'success':
    sys.stdout.buffer.write(b'{}\\n')
    raise SystemExit(0)
if scenario == 'failure':
    sys.stdout.buffer.write(b'AMN2_PHASE13_AWG3_PREFLIGHT_FAILURE_V1|stage=candidate_sockets|exit=71\\n')
    raise SystemExit(71)
if scenario == 'timeout':
    time.sleep(3)
    raise SystemExit(0)
if scenario == 'extra':
    sys.stdout.buffer.write(b'{}\\n{}\\n')
    raise SystemExit(0)
if scenario == 'crlf':
    sys.stdout.buffer.write(b'{}\\r\\n')
    raise SystemExit(0)
if scenario == 'invalid':
    sys.stdout.buffer.write(b'\\xff\\xfe\\n')
    raise SystemExit(0)
if scenario == 'oversized':
    sys.stdout.buffer.write(b'x' * 70000)
    raise SystemExit(0)
sys.stdout.buffer.write(b'{}\\n')
raise SystemExit(99)
""",
        encoding="utf-8",
    )
    python_exe = ROOT / "worktrees" / "amn2-phase13-awg2-awg3-local" / ".venv" / "Scripts" / "python.exe"
    result = run_powershell_harness(
        tmp_path,
        f"""
$transport = Invoke-BoundedTransport -Executable '{python_exe}' -Arguments @('{fake}', '{scenario}') -InputBytes ([byte[]]@()) -TimeoutMilliseconds 500 -MaximumOutputBytes 65536
$envelope = ConvertFrom-BoundedCollectorEnvelope -Transport $transport
[Console]::Out.Write($envelope.Reason)
""",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == expected_reason


def test_failure_receipt_create_new_never_persists_raw_transport_output(tmp_path):
    target = tmp_path / "failure.json"
    result = run_powershell_harness(
        tmp_path,
        f"""
Write-SanitizedFailureCreateNew -Path '{target}' -OutcomeId 'test-outcome-001' -ManifestSha256 ('a' * 64) -Stage 'transport' -ReasonCode 'observation_ambiguous'
[Console]::Out.Write((Get-Content -Raw -LiteralPath '{target}'))
""",
    )
    receipt = json.loads(result.stdout)
    assert result.returncode == 0, result.stderr
    assert receipt["decision"] == "stop"
    assert receipt["reason_code"] == "observation_ambiguous"
    assert "stdout" not in receipt
    assert "stderr" not in receipt
    assert "raw" not in receipt


def test_python_contract_validation_accepts_only_exact_canonical_success_evidence(tmp_path):
    repo = prepare_runner_repo(tmp_path, outcome_id="test-outcome-004")
    package = repo / "packaging" / "phase13-awg3-preflight"
    manifest = repo / "packaging" / "phase13-awg3-preflight" / "phase13-awg3-preflight-manifest.json"
    contract = repo / "scripts" / "phase13_awg3_preflight_contract.py"
    python_exe = ROOT / "worktrees" / "amn2-phase13-awg2-awg3-local" / ".venv" / "Scripts" / "python.exe"
    valid_b64 = __import__("base64").b64encode(valid_success_evidence_for_manifest(manifest)).decode("ascii")
    invalid_b64 = __import__("base64").b64encode(b"{}").decode("ascii")
    wrong_binding = json.loads(valid_success_evidence_for_manifest(manifest))
    wrong_binding["runner_sha256"] = "0" * 64
    wrong_binding_b64 = __import__("base64").b64encode(
        canonical_json(wrong_binding)
    ).decode("ascii")

    result = run_powershell_harness(
        tmp_path,
        f"""
$valid = Test-EvidenceContract -PythonExecutable '{python_exe}' -ContractPath '{contract}' -ManifestPath '{manifest}' -RepositoryRoot '{package}' -EvidenceBytes ([Convert]::FromBase64String('{valid_b64}'))
$invalid = Test-EvidenceContract -PythonExecutable '{python_exe}' -ContractPath '{contract}' -ManifestPath '{manifest}' -RepositoryRoot '{package}' -EvidenceBytes ([Convert]::FromBase64String('{invalid_b64}'))
$wrongBinding = Test-EvidenceContract -PythonExecutable '{python_exe}' -ContractPath '{contract}' -ManifestPath '{manifest}' -RepositoryRoot '{package}' -EvidenceBytes ([Convert]::FromBase64String('{wrong_binding_b64}'))
[Console]::Out.Write("$($valid.ToString().ToLowerInvariant())|$($invalid.ToString().ToLowerInvariant())|$($wrongBinding.ToString().ToLowerInvariant())")
""",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false|false"
