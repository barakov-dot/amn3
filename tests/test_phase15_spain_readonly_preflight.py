import hashlib
import json
import os
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
            "AMN2_PHASE15_CLAIM_ID": "phase15-preflight-test-001",
            "AMN2_PHASE15_EXPECTED_HOST": "spain.test.invalid",
            "AMN2_PHASE15_PACKAGE_ID": PACKAGE_ID,
            "PHASE15_PREFLIGHT_FIXTURE_ROOT": str(fixture).replace("\\", "/"),
            "PHASE15_PYTHON": sys.executable.replace("\\", "/"),
        }
    )
    result = subprocess.run(
        [str(BASH), str(COLLECTOR)],
        check=False,
        capture_output=True,
        env=env,
        timeout=10,
    )
    after = fixture_snapshot(fixture)
    return result, before, after


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


def test_runner_acceptance_requires_package_collector_host_and_schema_binding(tmp_path: Path):
    claim = tmp_path / "claim.json"
    claim.write_text(
        json.dumps(
            {
                "claim_id": "phase15-preflight-test-001",
                "collector_sha256": "b" * 64,
                "consumed_at": None,
                "expected_host": "spain.test.invalid",
                "expires_at": "2099-08-11T12:00:00Z",
                "future_gate": "PREFLIGHT",
                "issued_at": "2099-08-11T11:00:00Z",
                "manifest_sha256": "a" * 64,
                "package_id": PACKAGE_ID,
                "schema": "amn2.phase15.readonly-preflight-claim.v1",
                "status": "issued",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )
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
