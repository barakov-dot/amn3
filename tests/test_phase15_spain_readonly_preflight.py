import base64
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
COLLECTOR = ROOT / "scripts" / "vps" / "phase15_spain_readonly_preflight_remote.sh"
RUNNER = ROOT / "scripts" / "vps" / "phase15_spain_readonly_preflight_ssh_runner.ps1"
PACKAGE_ID = "phase15-dual-protocol-bootstrap-20260811-001"
FIXTURES = Path(__file__).parent / "fixtures" / "phase15_spain_preflight"
EXPECTED_OBSERVATIONS = {
    "application_state",
    "architecture",
    "awg2_health",
    "backup_capability",
    "bridge_amn2sp3br0",
    "config_path",
    "container_capability",
    "container_cidr_172_29_252_0_28",
    "container_name",
    "database_state",
    "disk_space",
    "firewall",
    "interface_awg3",
    "os_compatibility",
    "python_3_12",
    "recovery_markers_phase14_phase15",
    "routes",
    "service_capability",
    "service_name",
    "state_root",
    "telegram_prerequisites",
    "udp_30002",
    "vpn_cidr_10_212_13_0_24",
}


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        pytest.fail(f"missing {label}: {path}")
    return path


def fixture_snapshot(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


def run_collector(name: str):
    require_file(COLLECTOR, "collector")
    fixture = FIXTURES / name
    before = fixture_snapshot(fixture)
    env = os.environ.copy()
    env.update(
        {
            "AMN2_PHASE15_CLAIM_ID": "environment-must-not-be-used",
            "AMN2_PHASE15_EXPECTED_HOST": "environment.invalid",
            "AMN2_PHASE15_PACKAGE_ID": "environment-package-must-not-be-used",
            "PHASE15_PREFLIGHT_FIXTURE_ROOT": str(fixture).replace("\\", "/"),
            "PHASE15_PYTHON": sys.executable.replace("\\", "/"),
        }
    )
    result = subprocess.run(
        [
            str(BASH),
            str(COLLECTOR),
            PACKAGE_ID,
            "phase15-preflight-test-001",
            "spain.test.invalid",
        ],
        check=False,
        capture_output=True,
        env=env,
        timeout=10,
    )
    after = fixture_snapshot(fixture)
    return result, before, after


def collector_python_namespace() -> dict[str, object]:
    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    match = re.search(r'(?ms)^exec "\$python_executable" -c \'\n(?P<body>.*)\n\'(?: .*)?$', source)
    if match is None:
        pytest.fail("collector embedded Python not found")
    body = match.group("body")
    prefix = body.split("\ntry:\n    claim_id", 1)[0]
    namespace: dict[str, object] = {"__name__": "phase15_collector_test"}
    exec(compile(prefix, str(COLLECTOR), "exec"), namespace)
    return namespace


def collector_helper(name: str):
    helper = collector_python_namespace().get(name)
    if not callable(helper):
        pytest.fail(f"missing collector helper: {name}")
    return helper


def test_ready_fixture_emits_one_utf8_json_document_without_writes():
    result, before, after = run_collector("ready")

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert result.stderr == b""
    assert result.stdout.endswith(b"\n") and result.stdout.count(b"\n") == 1
    document = json.loads(result.stdout.decode("utf-8"))
    assert document["schema"] == "amn2.phase15.spain-readonly-collector.v1"
    assert document["package_id"] == PACKAGE_ID
    assert document["host_identity"] == "spain.test.invalid"
    assert document["decision"] == "pass"
    assert document["blocking_reasons"] == []
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", document["observed_at"])
    assert {item["name"] for item in document["observations"]} == EXPECTED_OBSERVATIONS
    assert all(item["state"] in {"absent", "free", "pass", "present", "stop", "unknown"} for item in document["observations"])
    assert all(len(item["observation_sha256"]) == 64 for item in document["observations"])
    assert document["safety"] == {
        "live_mutation": False,
        "raw_output_persisted": False,
        "remote_file_written": False,
    }
    assert before == after


def test_conflict_fixture_reports_resource_and_recovery_stops_without_changes():
    result, before, after = run_collector("conflict")

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    document = json.loads(result.stdout.decode("utf-8"))
    states = {item["name"]: item["state"] for item in document["observations"]}
    assert document["decision"] == "stop"
    assert states["interface_awg3"] == "stop"
    assert states["bridge_amn2sp3br0"] == "stop"
    assert states["udp_30002"] == "stop"
    assert states["vpn_cidr_10_212_13_0_24"] == "stop"
    assert states["container_cidr_172_29_252_0_28"] == "stop"
    assert states["recovery_markers_phase14_phase15"] == "stop"
    assert set(document["blocking_reasons"]) >= {
        "resource_conflict",
        "recovery_incomplete",
    }
    assert before == after


def test_observation_hashes_bind_safe_states_without_returning_raw_fixture_values():
    result, _before, _after = run_collector("ready")

    document = json.loads(result.stdout.decode("utf-8"))
    fixture = json.loads((FIXTURES / "ready" / "observations.json").read_text(encoding="utf-8"))
    by_name = {item["name"]: item for item in document["observations"]}
    raw = fixture["observations"]["awg2_health"]["raw"].encode("utf-8")
    assert by_name["awg2_health"]["observation_sha256"] == hashlib.sha256(raw).hexdigest()
    assert fixture["observations"]["telegram_prerequisites"]["raw"].encode("utf-8") not in result.stdout


def test_collector_requires_exact_positional_remote_envelope():
    require_file(COLLECTOR, "collector")
    env = os.environ.copy()
    env["PHASE15_PYTHON"] = sys.executable.replace("\\", "/")

    result = subprocess.run(
        [str(BASH), str(COLLECTOR)],
        check=False,
        capture_output=True,
        env=env,
        timeout=10,
    )

    assert result.returncode == 64
    assert result.stdout == b""
    assert result.stderr == b"collector_envelope_invalid\n"


def test_collector_command_streams_and_caps_stdout_and_stderr_at_limit_plus_one():
    command = collector_helper("command")
    result = command(
        [sys.executable, "-c", "import sys;sys.stdout.buffer.write(b'x'*4096);sys.stderr.buffer.write(b'y'*4096)"],
        maximum_output_bytes=32,
        timeout_seconds=5,
    )

    return_code, stdout, stderr, disposition = result
    assert return_code != 0
    assert len(stdout) <= 33
    assert len(stderr) <= 33
    assert disposition == "output_oversized"


@pytest.mark.parametrize(
    ("return_code", "stderr", "expected"),
    [
        (1, b'Device "awg3" does not exist.\n', "free"),
        (1, b"permission denied\n", "stop"),
        (2, b'Device "awg3" does not exist.\n', "stop"),
        (0, b"", "stop"),
    ],
)
def test_interface_absence_is_exact_and_errors_fail_closed(return_code: int, stderr: bytes, expected: str):
    classify = collector_helper("classify_ip_link")
    probe = (return_code, b"", stderr, "success" if return_code == 0 else "command_failed")

    assert classify(probe, "awg3") == expected


def test_container_inventory_includes_stopped_objects_and_errors_fail_closed():
    classify = collector_helper("classify_container_inventory")

    stopped_conflict = classify([("docker", (0, b"amn2-spain-awg3\n", b"", "success"))])
    clean = classify([("podman", (0, b"other-container\n", b"", "success"))])
    errored = classify([("docker", (125, b"", b"daemon unavailable", "command_failed"))])

    assert stopped_conflict == ("pass", "stop")
    assert clean == ("pass", "free")
    assert errored == ("stop", "stop")
    assert '[engine, "ps", "-a", "--format", "{{.Names}}"]' in require_file(COLLECTOR, "collector").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("handshakes", "expected"),
    [
        (b"A" * 43 + b"=\t1699999940\n", "pass"),
        (b"A" * 43 + b"=\t0\n", "stop"),
        (b"A" * 43 + b"=\t1699999300\n", "stop"),
        (b"malformed\n", "stop"),
        (b"", "stop"),
    ],
)
def test_awg2_health_requires_active_unit_interface_and_fresh_strict_handshake(handshakes: bytes, expected: str):
    classify = collector_helper("classify_awg2_health")
    success = "success"
    unit = (0, b"active\n", b"", success)
    interface = (0, b"7: awg2: <POINTOPOINT,UP>\n", b"", success)
    peer_state = (0, handshakes, b"", success)

    assert classify(unit, interface, peer_state, now_epoch=1_700_000_000) == expected


def test_awg2_health_fails_closed_on_any_probe_error():
    classify = collector_helper("classify_awg2_health")
    failed = (1, b"", b"failed", "command_failed")
    good_unit = (0, b"active\n", b"", "success")
    good_interface = (0, b"awg2\n", b"", "success")
    fresh = (0, b"A" * 43 + b"=\t1699999940\n", b"", "success")

    assert classify(failed, good_interface, fresh, now_epoch=1_700_000_000) == "stop"
    assert classify(good_unit, failed, fresh, now_epoch=1_700_000_000) == "stop"
    assert classify(good_unit, good_interface, failed, now_epoch=1_700_000_000) == "stop"


def run_powershell(body: str):
    require_file(RUNNER, "runner")
    harness = f". '{RUNNER}'\n{body}"
    return subprocess.run(
        [
            str(POWERSHELL),
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            harness,
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_runner_rejects_missing_future_claim_before_any_acceptance():
    result = run_powershell(
        "$ok = Test-Phase15FutureClaim -ClaimPath 'Z:\\missing-phase15-claim.json' "
        f"-ExpectedPackageId '{PACKAGE_ID}' -ExpectedManifestSha256 '{'a' * 64}' "
        f"-ExpectedCollectorSha256 '{'b' * 64}' -ExpectedHost 'spain.test.invalid'; "
        "[Console]::Out.Write($ok.ToString().ToLowerInvariant())"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false"


def valid_runner_claim(tmp_path: Path, **overrides: object) -> Path:
    claim = {
        "claim_id": "phase15-preflight-test-001",
        "collector_sha256": "b" * 64,
        "consumed_at": None,
        "expected_host": "spain.test.invalid",
        "expires_at": "2099-08-11T12:00:00Z",
        "future_gate": "PREFLIGHT",
        "issued_at": "2025-08-11T11:00:00Z",
        "manifest_sha256": "a" * 64,
        "package_id": PACKAGE_ID,
        "schema": "amn2.phase15.readonly-preflight-claim.v1",
        "status": "issued",
    }
    claim.update(overrides)
    path = tmp_path / "claim.json"
    path.write_bytes((json.dumps(claim, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))
    return path


def test_runner_acceptance_requires_package_collector_host_and_schema_binding(tmp_path: Path):
    claim = valid_runner_claim(tmp_path)
    claim_path = str(claim).replace("'", "''")
    result = run_powershell(
        f"$valid = Test-Phase15FutureClaim -ClaimPath '{claim_path}' -ExpectedPackageId '{PACKAGE_ID}' "
        f"-ExpectedManifestSha256 '{'a' * 64}' -ExpectedCollectorSha256 '{'b' * 64}' "
        "-ExpectedHost 'spain.test.invalid'; "
        f"$wrongHost = Test-Phase15FutureClaim -ClaimPath '{claim_path}' -ExpectedPackageId '{PACKAGE_ID}' "
        f"-ExpectedManifestSha256 '{'a' * 64}' -ExpectedCollectorSha256 '{'b' * 64}' "
        "-ExpectedHost 'other.test.invalid'; "
        "[Console]::Out.Write(\"$($valid.ToString().ToLowerInvariant())|$($wrongHost.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false"


@pytest.mark.parametrize(
    "host",
    [
        "-oProxyCommand=bad",
        "user@spain.test.invalid",
        "spain.test.invalid;touch-bad",
        "Spain.test.invalid",
        "spain..test.invalid",
        "spain_test.invalid",
        "127.0.0.1 -v",
    ],
)
def test_runner_rejects_unsafe_expected_host_grammar(host: str):
    encoded = base64.b64encode(host.encode()).decode()
    result = run_powershell(
        f"$hostValue = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded}')); "
        "$valid = Test-Phase15ExpectedHost -ExpectedHost $hostValue; "
        "[Console]::Out.Write($valid.ToString().ToLowerInvariant())"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false"


def test_runner_rejects_future_issued_or_noncanonical_claim(tmp_path: Path):
    future = valid_runner_claim(tmp_path, issued_at="2098-08-11T11:00:00Z")
    future_path = str(future).replace("'", "''")
    pretty = tmp_path / "pretty.json"
    pretty_value = json.loads(future.read_text())
    pretty_value["issued_at"] = "2025-08-11T11:00:00Z"
    pretty.write_text(json.dumps(pretty_value, indent=2) + "\n", encoding="utf-8")
    pretty_path = str(pretty).replace("'", "''")
    call = (
        f"-ExpectedPackageId '{PACKAGE_ID}' -ExpectedManifestSha256 '{'a' * 64}' "
        f"-ExpectedCollectorSha256 '{'b' * 64}' -ExpectedHost 'spain.test.invalid'"
    )
    result = run_powershell(
        f"$future = Test-Phase15FutureClaim -ClaimPath '{future_path}' {call}; "
        f"$pretty = Test-Phase15FutureClaim -ClaimPath '{pretty_path}' {call}; "
        "[Console]::Out.Write(\"$($future.ToString().ToLowerInvariant())|$($pretty.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false|false"


def test_runner_builds_positional_remote_envelope_with_safe_option_boundary():
    result = run_powershell(
        "$arguments = New-Phase15SshArguments -ExpectedHost 'spain.test.invalid' -ClaimId 'phase15-preflight-test-001'; "
        "[Console]::Out.Write(($arguments | ConvertTo-Json -Compress))"
    )

    assert result.returncode == 0, result.stderr
    arguments = json.loads(result.stdout)
    assert arguments[-3:] == [
        "--",
        "spain.test.invalid",
        "bash -s -- 'phase15-dual-protocol-bootstrap-20260811-001' 'phase15-preflight-test-001' 'spain.test.invalid'",
    ]
    assert "$start.Environment['AMN2_PHASE15_" not in require_file(RUNNER, "runner").read_text(encoding="utf-8")


def valid_collector_document(*, stopped: bool = False) -> dict[str, object]:
    observations = [
        {
            "name": name,
            "observation_sha256": hashlib.sha256(name.encode()).hexdigest(),
            "state": "stop" if stopped and name == "udp_30002" else ("free" if name in {"interface_awg3", "bridge_amn2sp3br0", "udp_30002", "vpn_cidr_10_212_13_0_24", "container_cidr_172_29_252_0_28", "container_name", "service_name", "config_path", "state_root"} else "pass"),
        }
        for name in sorted(EXPECTED_OBSERVATIONS)
    ]
    return {
        "blocking_reasons": ["resource_conflict"] if stopped else [],
        "claim_id": "phase15-preflight-test-001",
        "decision": "stop" if stopped else "pass",
        "host_identity": "spain.test.invalid",
        "observed_at": "2026-08-16T00:00:00Z",
        "observations": observations,
        "package_id": PACKAGE_ID,
        "safety": {
            "live_mutation": False,
            "raw_output_persisted": False,
            "remote_file_written": False,
        },
        "schema": "amn2.phase15.spain-readonly-collector.v1",
    }


def runner_document_result(document: dict[str, object], expression: str):
    encoded = base64.b64encode(json.dumps(document, separators=(",", ":")).encode()).decode()
    return run_powershell(
        f"$document = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded}')) | ConvertFrom-Json; {expression}"
    )


def test_runner_collector_validation_is_exact_and_reconstructs_allowlisted_canonical_evidence():
    document = valid_collector_document()
    result = runner_document_result(
        document,
        "$valid = Test-Phase15CollectorDocument -Document $document -ExpectedHost 'spain.test.invalid' -ExpectedClaimId 'phase15-preflight-test-001'; "
        "$evidence = ConvertTo-Phase15Evidence -Document $document -ManifestSha256 ('a' * 64) -CollectorSha256 ('b' * 64) -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:01Z' -EndedAt '2026-08-16T00:00:02Z'; "
        "$json = ConvertTo-Phase15CanonicalJsonText -Value $evidence; "
        "[Console]::Out.Write(\"$($valid.ToString().ToLowerInvariant())|$json\")",
    )

    assert result.returncode == 0, result.stderr
    valid, rendered = result.stdout.split("|", 1)
    assert valid == "true"
    evidence = json.loads(rendered)
    assert list(evidence) == sorted(evidence)
    assert list(evidence["safety"]) == sorted(evidence["safety"])
    assert all(list(item) == ["name", "observation_sha256", "state"] for item in evidence["observations"])
    assert evidence["observations"] == document["observations"]
    assert "observed_at" not in evidence
    assert "claim_id" not in evidence


@pytest.mark.parametrize(
    "mutation",
    [
        "extra_top_level",
        "extra_safety",
        "unknown_reason",
        "unknown_observation",
        "unsorted_observations",
        "decision_mismatch",
        "reason_mismatch",
    ],
)
def test_runner_rejects_non_schema_equivalent_collector_documents(mutation: str):
    document = valid_collector_document(stopped=True)
    if mutation == "extra_top_level":
        document["raw"] = "not-allowed"
    elif mutation == "extra_safety":
        document["safety"]["ssh_used"] = False
    elif mutation == "unknown_reason":
        document["blocking_reasons"] = ["arbitrary_reason"]
    elif mutation == "unknown_observation":
        document["observations"][0]["name"] = "Bearer synthetic-sensitive-value"
    elif mutation == "unsorted_observations":
        document["observations"] = list(reversed(document["observations"]))
    elif mutation == "decision_mismatch":
        document["decision"] = "pass"
    elif mutation == "reason_mismatch":
        document["blocking_reasons"] = ["observation_failed"]
    result = runner_document_result(
        document,
        "$valid = Test-Phase15CollectorDocument -Document $document -ExpectedHost 'spain.test.invalid' -ExpectedClaimId 'phase15-preflight-test-001'; [Console]::Out.Write($valid.ToString().ToLowerInvariant())",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false"


def test_runner_requires_canonical_collector_json_bytes():
    document = valid_collector_document()
    canonical = (json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n").encode()
    pretty = (json.dumps(document, indent=2) + "\n").encode()
    canonical_encoded = base64.b64encode(canonical).decode()
    pretty_encoded = base64.b64encode(pretty).decode()
    result = run_powershell(
        f"$canonical = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{canonical_encoded}')); "
        f"$pretty = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{pretty_encoded}')); "
        "$accepted = $null -ne (ConvertFrom-Phase15CanonicalJsonText -Text $canonical); "
        "$rejected = $null -eq (ConvertFrom-Phase15CanonicalJsonText -Text $pretty); "
        "[Console]::Out.Write(\"$($accepted.ToString().ToLowerInvariant())|$($rejected.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|true"


def test_runner_claim_reservation_is_create_new_and_terminal_transition_is_canonical(tmp_path: Path):
    claim = valid_runner_claim(tmp_path)
    claim_path = str(claim).replace("'", "''")
    result = run_powershell(
        f"$lifecycle = Reserve-Phase15Claim -ClaimPath '{claim_path}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z'; "
        "$replayed = $false; try { Reserve-Phase15Claim -ClaimPath '"
        + claim_path
        + "' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:01Z' } catch { $replayed = $true }; "
        "$reserved = [IO.File]::ReadAllText($lifecycle); "
        "$null = Set-Phase15ClaimTerminal -LifecyclePath $lifecycle -ClaimId 'phase15-preflight-test-001' -Status 'completed' -EndedAt '2026-08-16T00:00:02Z' -ReasonCode 'not_applicable'; "
        "$terminal = [IO.File]::ReadAllText($lifecycle); "
        "[Console]::Out.Write(\"$($replayed.ToString().ToLowerInvariant())|$reserved|$terminal\")"
    )

    assert result.returncode == 0, result.stderr
    replayed, reserved_raw, terminal_raw = result.stdout.split("|", 2)
    assert replayed == "true"
    reserved = json.loads(reserved_raw)
    terminal = json.loads(terminal_raw)
    assert list(reserved) == sorted(reserved)
    assert reserved["status"] == "reserved"
    assert terminal["status"] == "completed"
    assert terminal["reason_code"] == "not_applicable"
    assert claim.read_text(encoding="utf-8") == json.dumps(json.loads(claim.read_text()), sort_keys=True, separators=(",", ":")) + "\n"


def test_runner_reserves_claim_before_transport_and_has_terminal_failure_path():
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    main = source[source.index("function Invoke-Phase15RunnerMain") :]

    assert main.index("Reserve-Phase15Claim") < main.index("Invoke-Phase15OneSshTransport")
    assert "Set-Phase15ClaimTerminal" in main
    assert "amn2.phase15.readonly-preflight-failure.v1" in source


def test_runner_bounded_buffer_keeps_only_limit_plus_one_bytes():
    payload = base64.b64encode(b"0123456789").decode()
    result = run_powershell(
        f"$buffer = [IO.MemoryStream]::new(); $bytes = [Convert]::FromBase64String('{payload}'); "
        "$overflow = Add-Phase15BoundedBytes -Buffer $buffer -Bytes $bytes -Count $bytes.Length -MaximumBytes 4; "
        "[Console]::Out.Write(\"$($overflow.ToString().ToLowerInvariant())|$($buffer.Length)\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|5"
