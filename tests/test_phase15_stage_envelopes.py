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
PACKAGE_ID = "phase15-dual-protocol-bootstrap-20260811-001"
STAGES = (
    (ROOT / "scripts" / "vps" / "phase15_application_stage_remote.sh", "APPLICATION_STAGE"),
    (ROOT / "scripts" / "vps" / "phase15_awg3_runtime_stage_remote.sh", "AWG3_RUNTIME_STAGE"),
)
FORBIDDEN_MUTATION_PATTERNS = (
    r"systemctl\s+(?:restart|stop|start|enable)\b",
    r"(?:docker|podman)\s+(?:run|rm)\b",
    r"iptables\s+-(?:A|D)\b",
    r"nft\s+(?:add|delete)\b",
    r"ip\s+link\s+(?:add|delete|set)\b",
    r"\bsqlite3\s",
    r"\b(?:cp|mv|rm|chmod|chown)\s",
    r"(?<![<])>(?![>&])",
    r"\b(?:apt|apt-get|dnf|yum|apk|pacman|zypper)\s+(?:install|add)\b",
)


def script_source(path: Path) -> str:
    if not path.is_file():
        pytest.fail(f"missing stage envelope: {path}")
    return path.read_text(encoding="utf-8")


def write_claim(path: Path, *, script: Path, gate: str, **overrides: object) -> dict[str, object]:
    claim: dict[str, object] = {
        "claim_id": "phase15-stage-test-001",
        "consumed_at": None,
        "expected_current_state_sha256": "c" * 64,
        "expires_at": "2099-08-11T12:00:00Z",
        "future_gate": gate,
        "issued_at": "2099-08-11T11:00:00Z",
        "package_id": PACKAGE_ID,
        "schema": "amn2.phase15.stage-claim.v1",
        "stage_script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "status": "issued",
    }
    claim.update(overrides)
    path.write_text(json.dumps(claim, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return claim


def run_stage(script: Path, *, claim: Path | None, gate: str, state_hash: str = "c" * 64):
    env = os.environ.copy()
    env.update(
        {
            "PHASE15_EXPECTED_CURRENT_STATE_SHA256": state_hash,
            "PHASE15_FUTURE_GATE": gate,
            "PHASE15_PACKAGE_ID": PACKAGE_ID,
            "PHASE15_PYTHON": sys.executable.replace("\\", "/"),
        }
    )
    if claim is not None:
        env["PHASE15_STAGE_CLAIM_FILE"] = str(claim).replace("\\", "/")
    return subprocess.run(
        [str(BASH), str(script)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )


@pytest.mark.parametrize(("script", "gate"), STAGES)
def test_stage_envelope_refuses_without_one_time_claim(script: Path, gate: str):
    script_source(script)

    result = run_stage(script, claim=None, gate=gate)

    assert result.returncode == 64
    assert result.stdout == ""
    assert "claim_required" in result.stderr


@pytest.mark.parametrize(("script", "gate"), STAGES)
def test_checksum_bound_valid_claim_reaches_only_inert_phase15_boundary(
    tmp_path: Path, script: Path, gate: str
):
    script_source(script)
    claim = tmp_path / "claim.json"
    write_claim(claim, script=script, gate=gate)

    before = claim.read_bytes()
    result = run_stage(script, claim=claim, gate=gate)

    assert result.returncode == 78
    assert result.stdout == ""
    assert "stage_inert_in_phase15" in result.stderr
    assert claim.read_bytes() == before


@pytest.mark.parametrize(("script", "gate"), STAGES)
@pytest.mark.parametrize(
    ("overrides", "expected_reason"),
    [
        ({"package_id": "phase15-wrong"}, "claim_invalid"),
        ({"future_gate": "ENABLE_ISSUANCE"}, "claim_invalid"),
        ({"expected_current_state_sha256": "d" * 64}, "claim_invalid"),
        ({"stage_script_sha256": "e" * 64}, "claim_invalid"),
        ({"status": "consumed", "consumed_at": "2099-08-11T11:30:00Z"}, "claim_invalid"),
    ],
)
def test_stage_envelope_rejects_unbound_or_reused_claim(
    tmp_path: Path,
    script: Path,
    gate: str,
    overrides: dict[str, object],
    expected_reason: str,
):
    script_source(script)
    claim = tmp_path / "claim.json"
    write_claim(claim, script=script, gate=gate, **overrides)

    result = run_stage(script, claim=claim, gate=gate)

    assert result.returncode == 65
    assert result.stdout == ""
    assert expected_reason in result.stderr


def test_phase15_scripts_contain_no_forbidden_mutation_tokens():
    paths = [path for path, _gate in STAGES]
    paths.extend(
        [
            ROOT / "scripts" / "vps" / "phase15_spain_readonly_preflight_remote.sh",
            ROOT / "scripts" / "vps" / "phase15_spain_readonly_preflight_ssh_runner.ps1",
        ]
    )
    sources = {path: script_source(path) for path in paths}

    for path, source in sources.items():
        for pattern in FORBIDDEN_MUTATION_PATTERNS:
            assert re.search(pattern, source, flags=re.IGNORECASE) is None, (path, pattern)
