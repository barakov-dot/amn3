import hashlib
import json
import os
import re
import shlex
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
        "issued_at": "2025-08-11T11:00:00Z",
        "package_id": PACKAGE_ID,
        "schema": "amn2.phase15.stage-claim.v1",
        "stage_script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "status": "issued",
    }
    claim.update(overrides)
    path.write_bytes((json.dumps(claim, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))
    return claim


def local_stage_copy(tmp_path: Path, script: Path, *, preserve_legacy_override: bool = False) -> Path:
    source = script_source(script)
    local_python = shlex.quote(sys.executable.replace("\\", "/"))
    if "exec -c /usr/bin/python3 -I -B -" in source:
        source = source.replace("exec -c /usr/bin/python3 -I -B -", f"exec -c {local_python} -I -B -")
    elif not preserve_legacy_override:
        source = source.replace(
            'python_executable="${PHASE15_PYTHON:-python3}"',
            f"python_executable={local_python}",
        )
    runtime = tmp_path / script.name
    runtime.write_text(source, encoding="utf-8", newline="\n")
    return runtime


def stage_python_namespace(script: Path) -> dict[str, object]:
    source = script_source(script)
    match = re.search(
        r"(?ms)<<'PHASE15_STAGE_PY'\n(?P<body>.*)\nPHASE15_STAGE_PY$",
        source,
    )
    if match is None:
        pytest.fail("stage embedded Python not found")
    prefix = match.group("body").split(
        "\nclaim_path, script_path, package_id, gate, state_hash, supplied_package_id, supplied_gate = sys.argv[1:]",
        1,
    )[0]
    namespace: dict[str, object] = {"__name__": "phase15_stage_test"}
    exec(compile(prefix, str(script), "exec"), namespace)
    return namespace


def run_stage(script: Path, *, claim: Path | None, gate: str, state_hash: str = "c" * 64, extra_env: dict[str, str] | None = None):
    env = os.environ.copy()
    env.update(
        {
            "PHASE15_EXPECTED_CURRENT_STATE_SHA256": state_hash,
            "PHASE15_FUTURE_GATE": gate,
            "PHASE15_PACKAGE_ID": PACKAGE_ID,
        }
    )
    if extra_env:
        env.update(extra_env)
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
def test_stage_envelope_refuses_without_one_time_claim(tmp_path: Path, script: Path, gate: str):
    runtime = local_stage_copy(tmp_path, script)

    result = run_stage(runtime, claim=None, gate=gate)

    assert result.returncode == 64
    assert result.stdout == ""
    assert "claim_required" in result.stderr


@pytest.mark.parametrize(("script", "gate"), STAGES)
def test_checksum_bound_valid_claim_reaches_only_inert_phase15_boundary(
    tmp_path: Path, script: Path, gate: str
):
    runtime = local_stage_copy(tmp_path, script)
    claim = tmp_path / "claim.json"
    write_claim(claim, script=runtime, gate=gate)

    before = claim.read_bytes()
    result = run_stage(runtime, claim=claim, gate=gate)

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
    runtime = local_stage_copy(tmp_path, script)
    claim = tmp_path / "claim.json"
    write_claim(claim, script=runtime, gate=gate, **overrides)

    result = run_stage(runtime, claim=claim, gate=gate)

    assert result.returncode == 65
    assert result.stdout == ""
    assert expected_reason in result.stderr


@pytest.mark.parametrize(("script", "gate"), STAGES)
def test_stage_envelope_rejects_claim_issued_in_the_future(tmp_path: Path, script: Path, gate: str):
    runtime = local_stage_copy(tmp_path, script)
    claim = tmp_path / "future-claim.json"
    write_claim(
        claim,
        script=runtime,
        gate=gate,
        issued_at="2098-08-11T11:00:00Z",
        expires_at="2099-08-11T12:00:00Z",
    )

    result = run_stage(runtime, claim=claim, gate=gate)

    assert result.returncode == 65
    assert result.stdout == ""
    assert "claim_invalid" in result.stderr


@pytest.mark.parametrize(("script", "gate"), STAGES)
def test_stage_envelope_rejects_noncanonical_claim_bytes(tmp_path: Path, script: Path, gate: str):
    runtime = local_stage_copy(tmp_path, script)
    claim = tmp_path / "noncanonical-claim.json"
    value = write_claim(claim, script=runtime, gate=gate)
    claim.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    result = run_stage(runtime, claim=claim, gate=gate)

    assert result.returncode == 65
    assert result.stdout == ""
    assert "claim_invalid" in result.stderr


@pytest.mark.parametrize(("script", "gate"), STAGES)
def test_stage_envelope_requires_exact_utc_timestamp_grammar(tmp_path: Path, script: Path, gate: str):
    runtime = local_stage_copy(tmp_path, script)
    claim = tmp_path / "timestamp-claim.json"
    write_claim(claim, script=runtime, gate=gate, issued_at="2025-08-11T11:00:00+00:00")

    result = run_stage(runtime, claim=claim, gate=gate)

    assert result.returncode == 65
    assert result.stdout == ""
    assert "claim_invalid" in result.stderr


@pytest.mark.parametrize(("script", "gate"), STAGES)
def test_stage_envelope_ignores_ambient_python_and_path_before_claim_gate(tmp_path: Path, script: Path, gate: str):
    marker = tmp_path / "ambient-executed"
    attacker = tmp_path / "attacker-python"
    attacker.write_text(
        f"#!/usr/bin/env bash\nprintf ambient > {shlex.quote(str(marker).replace('\\', '/'))}\nexit 99\n",
        encoding="utf-8",
        newline="\n",
    )
    runtime = local_stage_copy(tmp_path, script, preserve_legacy_override=True)

    result = run_stage(
        runtime,
        claim=None,
        gate=gate,
        extra_env={
            "PATH": str(tmp_path).replace("\\", "/"),
            "PHASE15_PYTHON": str(attacker).replace("\\", "/"),
            "PYTHONPATH": str(tmp_path).replace("\\", "/"),
        },
    )

    assert result.returncode == 64
    assert result.stdout == ""
    assert result.stderr == "claim_required\n"
    assert not marker.exists()


@pytest.mark.parametrize(("script", "gate"), STAGES)
def test_stage_envelope_rejects_oversized_claim_before_json_parse(tmp_path: Path, script: Path, gate: str):
    runtime = local_stage_copy(tmp_path, script)
    claim = tmp_path / "oversized-claim.json"
    write_claim(claim, script=runtime, gate=gate, claim_id="x" * 5000)

    result = run_stage(runtime, claim=claim, gate=gate)

    assert result.returncode == 65
    assert result.stdout == ""
    assert result.stderr == "claim_invalid\n"


@pytest.mark.parametrize(("script", "_gate"), STAGES)
def test_stage_claim_reader_stops_at_limit_plus_one_before_json(tmp_path: Path, script: Path, _gate: str):
    namespace = stage_python_namespace(script)
    oversized = tmp_path / "oversized.json"
    oversized.write_bytes(b"x" * 4097)

    with pytest.raises(ValueError, match="regular bounded file|file size"):
        namespace["read_regular_bounded"](oversized, namespace["MAX_CLAIM_BYTES"])


@pytest.mark.parametrize(("script", "gate"), STAGES)
def test_stage_envelope_rejects_symlink_claim_artifact(tmp_path: Path, script: Path, gate: str):
    runtime = local_stage_copy(tmp_path, script)
    target = tmp_path / "claim-target.json"
    write_claim(target, script=runtime, gate=gate)
    claim = tmp_path / "claim-link.json"
    claim.symlink_to(target)

    result = run_stage(runtime, claim=claim, gate=gate)

    assert result.returncode == 65
    assert result.stdout == ""
    assert result.stderr == "claim_invalid\n"


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
