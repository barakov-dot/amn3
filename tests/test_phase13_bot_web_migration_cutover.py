from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
CUTOVER = ROOT / "scripts/vps/phase13_bot_web_migration_cutover_remote.sh"
RUNNER = ROOT / "scripts/vps/phase13_bot_web_migration_ssh_runner.ps1"
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
NOW_EPOCH = 1785675600
RECEIPT_KEYS = {
    "awg2_equal",
    "database_equal",
    "foreign_equal",
    "operator_accepted",
    "outcome",
    "reason",
    "rollback_armed",
    "rolled_back",
    "schema",
    "single_owner",
    "spain_active",
    "stage",
    "usa_active",
}


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def powershell_executable() -> str:
    executable = shutil.which("powershell") or shutil.which("pwsh")
    if executable is None:
        pytest.skip("PowerShell is unavailable")
    return executable


def ps_literal(path: Path) -> str:
    return str(path).replace("'", "''")


def run_powershell(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            powershell_executable(),
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8-sig",
        errors="strict",
        timeout=20,
    )


def write_cutover_fixture(root: Path, **overrides: str) -> None:
    (root / ".amn2-phase13-local-fake-harness").write_bytes(b"task8-local-only\n")
    values = {
        "ROLLBACK_ARM_OK": "true",
        "USA_PROCESS_COUNT": "1",
        "SPAIN_PROCESS_COUNT": "0",
        "USA_STOP_RESULT_COUNT": "0",
        "SPAIN_START_RESULT_COUNT": "1",
        "SPAIN_ADMISSION_OK": "true",
        "OPERATOR_ACCEPTED": "true",
        "POSTFLIGHT_OK": "true",
        "SPAIN_WEB_DATA_ACCEPTED": "true",
        "SPAIN_WEB_LOOPBACK_ONLY": "true",
        "TELEGRAM_IDENTITY_OK": "true",
        "TELEGRAM_WEBHOOK_CLEAR": "true",
        "TELEGRAM_BACKLOG_CLEAR": "true",
        "DATABASE_EQUAL": "true",
        "AWG2_EQUAL": "true",
        "FOREIGN_EQUAL": "true",
        "RESTORE_SPAIN_NEEDED": "false",
        "ROLLBACK_RESTORE_OK": "true",
    }
    values.update(overrides)
    state = root / "observed/state"
    state.parent.mkdir(parents=True)
    state.write_text(
        "".join(f"{key}={value}\n" for key, value in values.items()),
        encoding="utf-8",
        newline="\n",
    )


def run_cutover(root: Path) -> subprocess.CompletedProcess[str]:
    assert BASH.is_file(), "Git Bash is required for the local fake harness"
    environment = os.environ.copy()
    environment.update(
        {
            "AMN2_PHASE13_LOCAL_FAKE_HARNESS": "1",
            "AMN2_PHASE13_FAKE_ROOT": root.resolve().as_posix(),
            "AMN2_PHASE13_TEST_NOW_EPOCH": str(NOW_EPOCH),
        }
    )
    return subprocess.run(
        [str(BASH), CUTOVER.resolve().as_posix(), "cutover"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
        check=False,
    )


def receipt(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert result.stdout
    document = json.loads(result.stdout)
    assert result.stdout.encode("utf-8") == canonical(document)
    assert set(document) == RECEIPT_KEYS
    return document


def events(root: Path) -> list[str]:
    return (root / "events.log").read_text(encoding="utf-8").splitlines()


def write_cutover_manifest(root: Path, *, expires_at: str = "2099-08-03T12:00:00Z", extra: dict[str, object] | None = None) -> Path:
    cutover_bytes = CUTOVER.read_bytes()
    runner_bytes = RUNNER.read_bytes()
    manifest: dict[str, object] = {
        "approval_mode": "bot_cutover",
        "artifacts": {
            "cutover_remote": {
                "sha256": sha256(cutover_bytes),
                "size": len(cutover_bytes),
            },
            "ssh_runner": {
                "sha256": sha256(runner_bytes),
                "size": len(runner_bytes),
            },
        },
        "created_at": "2026-08-02T12:00:00Z",
        "expires_at": expires_at,
        "live_mutation_authorized": False,
        "outcome_id": "bot-cutover-local-001",
        "schema": "amn2.phase13.bot-web-cutover-manifest.v1",
        "trust_bundles": {
            "spain": {
                "role": "spain",
                "trust_root": r"C:\ProgramData\AMN2\trust\spain",
            },
            "usa": {
                "role": "usa",
                "trust_root": r"C:\ProgramData\AMN2\trust\usa",
            },
        },
        "web_data_apply_authorized": False,
    }
    if extra:
        manifest.update(extra)
    path = root / "manifest.json"
    path.write_bytes(canonical(manifest))
    return path


def test_success_path_has_exact_single_owner_sequence_and_safe_receipt(
    tmp_path: Path,
) -> None:
    write_cutover_fixture(tmp_path)

    result = run_cutover(tmp_path)

    assert result.returncode == 0, result.stderr
    document = receipt(result)
    assert document == {
        "awg2_equal": True,
        "database_equal": True,
        "foreign_equal": True,
        "operator_accepted": True,
        "outcome": "passed",
        "reason": "NONE",
        "rollback_armed": True,
        "rolled_back": False,
        "schema": "amn2.phase13.bot-web-cutover-receipt.v1",
        "single_owner": True,
        "spain_active": True,
        "stage": "postflight",
        "usa_active": False,
    }
    assert events(tmp_path) == [
        "preflight",
        "arm_rollback",
        "stop_usa",
        "prove_usa_zero",
        "start_spain",
        "operator_accept",
        "postflight",
    ]
    assert (tmp_path / "etc/amn2-spain/bot-enabled").is_file()
    assert result.stderr == ""


def test_spain_start_is_impossible_before_usa_process_zero(tmp_path: Path) -> None:
    write_cutover_fixture(tmp_path, USA_STOP_RESULT_COUNT="1")

    result = run_cutover(tmp_path)

    assert result.returncode != 0
    document = receipt(result)
    assert document["reason"] == "USA_BOT_STOP_UNCONFIRMED"
    assert document["rolled_back"] is True
    assert document["usa_active"] is True
    assert document["spain_active"] is False
    assert "start_spain" not in events(tmp_path)
    assert events(tmp_path) == [
        "preflight",
        "arm_rollback",
        "stop_usa",
        "prove_usa_zero",
        "stop_spain",
        "remove_exact_marker",
        "restore_spain_if_needed",
        "start_usa",
        "prove_single_usa",
    ]


def test_failed_spain_admission_restores_single_usa_owner(tmp_path: Path) -> None:
    write_cutover_fixture(tmp_path, SPAIN_ADMISSION_OK="false")

    result = run_cutover(tmp_path)

    assert result.returncode != 0
    document = receipt(result)
    assert document["reason"] == "SPAIN_BOT_ADMISSION_FAILED"
    assert document["rolled_back"] is True
    assert document["single_owner"] is True
    assert document["usa_active"] is True
    assert document["spain_active"] is False
    assert events(tmp_path) == [
        "preflight",
        "arm_rollback",
        "stop_usa",
        "prove_usa_zero",
        "start_spain",
        "stop_spain",
        "remove_exact_marker",
        "restore_spain_if_needed",
        "start_usa",
        "prove_single_usa",
    ]
    assert not (tmp_path / "etc/amn2-spain/bot-enabled").exists()


def test_rollback_must_be_armed_before_first_service_transition(tmp_path: Path) -> None:
    write_cutover_fixture(tmp_path, ROLLBACK_ARM_OK="false")

    result = run_cutover(tmp_path)

    assert result.returncode != 0
    document = receipt(result)
    assert document["reason"] == "ROLLBACK_ARM_FAILED"
    assert document["rollback_armed"] is False
    assert document["rolled_back"] is False
    assert events(tmp_path) == ["preflight", "arm_rollback"]


@pytest.mark.parametrize(
    ("override", "reason", "last_forward_event"),
    [
        ({"OPERATOR_ACCEPTED": "false"}, "OPERATOR_ACCEPTANCE_FAILED", "operator_accept"),
        ({"POSTFLIGHT_OK": "false"}, "POSTFLIGHT_FAILED", "postflight"),
    ],
)
def test_failure_after_spain_start_runs_exact_rollback_sequence(
    tmp_path: Path,
    override: dict[str, str],
    reason: str,
    last_forward_event: str,
) -> None:
    write_cutover_fixture(tmp_path, **override)

    result = run_cutover(tmp_path)

    assert result.returncode != 0
    document = receipt(result)
    assert document["reason"] == reason
    assert document["rolled_back"] is True
    all_events = events(tmp_path)
    rollback_start = all_events.index("stop_spain")
    assert all_events[rollback_start:] == [
        "stop_spain",
        "remove_exact_marker",
        "restore_spain_if_needed",
        "start_usa",
        "prove_single_usa",
    ]
    assert all_events[rollback_start - 1] == last_forward_event
    assert not (tmp_path / "etc/amn2-spain/bot-enabled").exists()


@pytest.mark.parametrize(
    "override",
    [
        {"SPAIN_WEB_DATA_ACCEPTED": "false"},
        {"SPAIN_WEB_LOOPBACK_ONLY": "false"},
        {"TELEGRAM_IDENTITY_OK": "false"},
        {"TELEGRAM_WEBHOOK_CLEAR": "false"},
        {"TELEGRAM_BACKLOG_CLEAR": "false"},
        {"DATABASE_EQUAL": "false"},
        {"AWG2_EQUAL": "false"},
        {"FOREIGN_EQUAL": "false"},
    ],
)
def test_preflight_failure_has_no_service_transition(
    tmp_path: Path, override: dict[str, str]
) -> None:
    write_cutover_fixture(tmp_path, **override)

    result = run_cutover(tmp_path)

    assert result.returncode != 0
    document = receipt(result)
    assert document["reason"] == "PREFLIGHT_FAILED"
    assert document["rolled_back"] is False
    assert events(tmp_path) == ["preflight"]
    assert not (tmp_path / "etc/amn2-spain/bot-enabled").exists()


def test_rollback_failure_is_terminal_and_never_reports_two_active_owners(
    tmp_path: Path,
) -> None:
    write_cutover_fixture(
        tmp_path,
        SPAIN_ADMISSION_OK="false",
        ROLLBACK_RESTORE_OK="false",
    )

    result = run_cutover(tmp_path)

    assert result.returncode != 0
    document = receipt(result)
    assert document["reason"] == "ROLLBACK_FAILED"
    assert not (document["usa_active"] and document["spain_active"])


def test_receipt_never_contains_secret_identifier_target_or_raw_output(
    tmp_path: Path,
) -> None:
    write_cutover_fixture(tmp_path, OPERATOR_ACCEPTED="false")

    result = run_cutover(tmp_path)

    serialized = json.dumps(receipt(result), sort_keys=True).lower()
    for forbidden in (
        "token",
        "telegram_id",
        "admin",
        "target",
        "host",
        "path",
        "stdout",
        "stderr",
        "fingerprint",
        "private",
    ):
        assert forbidden not in serialized


def test_runner_binds_exact_bytes_expiry_two_trust_roots_and_one_claim(
    tmp_path: Path,
) -> None:
    write_cutover_fixture(tmp_path)
    manifest = write_cutover_manifest(tmp_path)
    invocation = f"""
. '{ps_literal(RUNNER)}'
$manifestBytes = [IO.File]::ReadAllBytes('{ps_literal(manifest)}')
$cutoverBytes = [IO.File]::ReadAllBytes('{ps_literal(CUTOVER)}')
$runnerBytes = [IO.File]::ReadAllBytes('{ps_literal(RUNNER)}')
$binding = Test-Phase13CutoverBinding -ManifestBytes $manifestBytes -CutoverBytes $cutoverBytes -RunnerBytes $runnerBytes -NowUtc ([DateTimeOffset]'2026-08-02T12:01:00Z')
$first = New-Phase13LocalFakeCutoverClaim -FakeRoot '{ps_literal(tmp_path)}' -Binding $binding
$replay = 'not_blocked'
try {{
    $null = New-Phase13LocalFakeCutoverClaim -FakeRoot '{ps_literal(tmp_path)}' -Binding $binding
}} catch {{
    $replay = $_.Exception.Message
}}
[Console]::Out.Write("$($binding.OutcomeId)|$($binding.TrustRoles -join ',')|$([IO.File]::Exists($first))|$replay")
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert result.stdout == "bot-cutover-local-001|usa,spain|True|outcome claim replay"
    claims = list((tmp_path / "outcomes").glob("*.claim.json"))
    assert len(claims) == 1
    claim = json.loads(claims[0].read_bytes())
    assert set(claim) == {
        "cutover_sha256",
        "expires_at",
        "manifest_sha256",
        "outcome_id",
        "runner_sha256",
        "schema",
    }


def test_runner_rejects_expired_manifest_before_outcome_claim(tmp_path: Path) -> None:
    write_cutover_fixture(tmp_path)
    manifest = write_cutover_manifest(tmp_path, expires_at="2026-08-02T11:59:00Z")
    invocation = f"""
. '{ps_literal(RUNNER)}'
try {{
    $binding = Test-Phase13CutoverBinding -ManifestBytes ([IO.File]::ReadAllBytes('{ps_literal(manifest)}')) -CutoverBytes ([IO.File]::ReadAllBytes('{ps_literal(CUTOVER)}')) -RunnerBytes ([IO.File]::ReadAllBytes('{ps_literal(RUNNER)}')) -NowUtc ([DateTimeOffset]'2026-08-02T12:01:00Z')
    $null = New-Phase13LocalFakeCutoverClaim -FakeRoot '{ps_literal(tmp_path)}' -Binding $binding
    [Console]::Out.Write('not_blocked')
}} catch {{
    [Console]::Out.Write($_.Exception.Message)
}}
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stdout == "cutover manifest expired"
    assert not (tmp_path / "outcomes").exists()


def test_runner_rechecks_expiry_when_outcome_claim_is_created(tmp_path: Path) -> None:
    write_cutover_fixture(tmp_path)
    manifest = write_cutover_manifest(tmp_path)
    invocation = f"""
. '{ps_literal(RUNNER)}'
try {{
    $binding = Test-Phase13CutoverBinding -ManifestBytes ([IO.File]::ReadAllBytes('{ps_literal(manifest)}')) -CutoverBytes ([IO.File]::ReadAllBytes('{ps_literal(CUTOVER)}')) -RunnerBytes ([IO.File]::ReadAllBytes('{ps_literal(RUNNER)}')) -NowUtc ([DateTimeOffset]'2026-08-02T12:01:00Z')
    $binding.ExpiresAt = '2020-01-01T00:00:00Z'
    $null = New-Phase13LocalFakeCutoverClaim -FakeRoot '{ps_literal(tmp_path)}' -Binding $binding
    [Console]::Out.Write('not_blocked')
}} catch {{
    [Console]::Out.Write($_.Exception.Message)
}}
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stdout == "cutover binding expired"
    assert not (tmp_path / "outcomes").exists()


def test_runner_rejects_user_overridable_target_or_path_fields(tmp_path: Path) -> None:
    write_cutover_fixture(tmp_path)
    manifest = write_cutover_manifest(
        tmp_path,
        extra={"target_host": "forbidden", "remote_path": "/forbidden"},
    )
    invocation = f"""
. '{ps_literal(RUNNER)}'
try {{
    $null = Test-Phase13CutoverBinding -ManifestBytes ([IO.File]::ReadAllBytes('{ps_literal(manifest)}')) -CutoverBytes ([IO.File]::ReadAllBytes('{ps_literal(CUTOVER)}')) -RunnerBytes ([IO.File]::ReadAllBytes('{ps_literal(RUNNER)}')) -NowUtc ([DateTimeOffset]'2026-08-02T12:01:00Z')
    [Console]::Out.Write('not_blocked')
}} catch {{
    [Console]::Out.Write($_.Exception.Message)
}}
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stdout == "cutover manifest keys invalid"
