import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
REMOTE = ROOT / "scripts" / "vps" / "phase13_bot_web_migration_readonly_remote.py"
RUNNER = ROOT / "scripts" / "vps" / "phase13_bot_web_migration_ssh_runner.ps1"


def collector_module():
    try:
        return importlib.import_module(
            "scripts.vps.phase13_bot_web_migration_readonly_remote"
        )
    except ModuleNotFoundError as error:
        pytest.fail(f"Phase 13 bot/web read-only collector is missing: {error}")


def authoritative_spain_server_config_path() -> Path:
    runtime_environment = (
        ROOT / "packaging" / "phase12-spain" / "templates" / "runtime.env"
    )
    prefix = "SERVER_CONFIG_PATH="
    matches = [
        line.removeprefix(prefix)
        for line in runtime_environment.read_text(encoding="utf-8").splitlines()
        if line.startswith(prefix)
    ]
    assert len(matches) == 1
    return Path(matches[0])


def powershell_executable() -> str:
    executable = shutil.which("powershell") or shutil.which("pwsh")
    if executable is None:
        pytest.skip("PowerShell is unavailable")
    return executable


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


def make_sqlite(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.executescript(
            "CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT);"
            "CREATE TABLE plans(id INTEGER PRIMARY KEY, title TEXT);"
            "INSERT INTO users(name) VALUES ('one'), ('two');"
            "INSERT INTO plans(title) VALUES ('basic');"
        )
        connection.commit()
    finally:
        connection.close()


def test_remote_collector_is_read_only_and_sqlite_mode_ro() -> None:
    source = REMOTE.read_text(encoding="utf-8")

    assert "mode=ro" in source
    assert "PRAGMA query_only=ON" in source
    for forbidden in (
        "systemctl start",
        "systemctl stop",
        "systemctl restart",
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
        'open("w',
        "write_text(",
        "write_bytes(",
    ):
        assert forbidden not in source


def test_collector_accepts_only_fixed_roles_and_no_path_arguments() -> None:
    collector = collector_module()

    assert set(collector.ROLE_CONTRACTS) == {"usa", "spain"}
    assert collector.parse_arguments(["--role", "usa"]).role == "usa"
    with pytest.raises(SystemExit):
        collector.parse_arguments(["--role", "other"])
    with pytest.raises(SystemExit):
        collector.parse_arguments(["--role", "usa", "--database", "elsewhere"])


def test_spain_audit_collector_uses_authoritative_phase12_server_config_path() -> None:
    collector = collector_module()

    assert authoritative_spain_server_config_path() in collector.ROLE_CONTRACTS[
        "spain"
    ]["required_paths"]


def test_sqlite_projection_is_exact_and_does_not_change_database(tmp_path: Path) -> None:
    collector = collector_module()
    database = tmp_path / "audit.sqlite3"
    make_sqlite(database)
    before = hashlib.sha256(database.read_bytes()).hexdigest()

    projection = collector.inspect_database(database)

    assert projection == {
        "integrity_ok": True,
        "foreign_key_violations": 0,
        "table_count": 2,
        "schema_sha256": projection["schema_sha256"],
        "counts_sha256": projection["counts_sha256"],
    }
    assert len(projection["schema_sha256"]) == 64
    assert len(projection["counts_sha256"]) == 64
    assert hashlib.sha256(database.read_bytes()).hexdigest() == before


def test_ephemeral_hmac_proof_never_returns_raw_reference() -> None:
    collector = collector_module()
    key = bytes(range(32))

    digest = collector.ephemeral_reference_hmac("test-reference", key)

    assert len(digest) == 64
    assert digest != "test-reference"
    assert "test-reference" not in json.dumps({"digest": digest})


def test_runner_fake_pair_uses_one_process_per_role_and_emits_only_booleans(
    tmp_path: Path,
) -> None:
    fake = tmp_path / "fake_collector.py"
    counter = tmp_path / "counter.txt"
    fake.write_text(
        """import base64, hashlib, hmac, json, pathlib, sys
counter = pathlib.Path(sys.argv[1])
role = sys.argv[2]
with counter.open('a', encoding='utf-8') as handle:
    handle.write(role + '\\n')
key = base64.b64decode(sys.stdin.buffer.readline().strip(), validate=True)
references = {
    'telegram_bot_token': 'same-token',
    'app_secret_key': role + '-app-secret',
    'web_password_hash': role + '-password',
    'web_session_secret': role + '-session',
}
proof = {name: hmac.new(key, value.encode(), hashlib.sha256).hexdigest()
         for name, value in references.items()}
document = {
    'schema': 'amn2.phase13.bot-web-collector.v1',
    'role': role,
    'audit': {
        'schema': 'amn2.phase13.bot-web-audit.v1',
        'role': 'usa-source' if role == 'usa' else 'spain-target',
        'checked_at': '2026-08-02T12:00:00Z',
        'services': {'web_active': True, 'bot_active': role == 'usa',
                     'web_loopback_only': True},
        'database': {'integrity_ok': True, 'foreign_key_violations': 0,
                     'table_count': 1, 'schema_sha256': 'a' * 64,
                     'counts_sha256': 'b' * 64},
        'environment': {'telegram_bot_token_present': True,
                        'app_secret_present': True,
                        'web_password_hash_present': True,
                        'session_secret_present': True},
        'required_artifacts': {'database_readable': True,
                               'environment_reference_proof_available': True},
        'safety_receipt': {'mutation_attempted': False,
                           'raw_output_persisted': False,
                           'secret_bearing_data_persisted': False},
        'telegram_bot_token': 'raw-secret-sentinel',
    },
    'secret_reference_hmac': proof,
}
sys.stdout.write(json.dumps(document, sort_keys=True, separators=(',', ':')) + '\\n')
""",
        encoding="utf-8",
    )
    invocation = f"""
. '{RUNNER}'
$json = Invoke-Phase13LocalFakeAuditPair -Executable '{sys.executable}' -HarnessPath '{fake}' -CounterPath '{counter}'
[Console]::Out.Write($json)
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert counter.read_text(encoding="utf-8").splitlines() == ["usa", "spain"]
    document = json.loads(result.stdout)
    assert document["secret_reference_equal"] == {
        "telegram_bot_token": True,
        "app_secret_key": False,
        "web_password_hash": False,
        "web_session_secret": False,
    }
    assert document["stable_fingerprints_persisted"] is False
    serialized = json.dumps(document, sort_keys=True)
    assert "secret_reference_hmac" not in serialized
    assert "same-token" not in serialized
    assert "app-secret" not in serialized
    assert "raw-secret-sentinel" not in serialized


def test_runner_enforces_timeout_and_output_cap_with_local_process(tmp_path: Path) -> None:
    fake = tmp_path / "bounded.py"
    fake.write_text(
        """import sys, time
mode = sys.argv[1]
if mode == 'oversized':
    sys.stdout.write('x' * 65)
else:
    time.sleep(2)
""",
        encoding="utf-8",
    )
    invocation = f"""
. '{RUNNER}'
$empty = [byte[]]::new(0)
$original = [Console]::InputEncoding
$hostile = New-Object Text.UTF8Encoding($true)
try {{
    [Console]::InputEncoding = $hostile
    $oversized = Invoke-Phase13BoundedProcess -Executable '{sys.executable}' -Arguments @('{fake}', 'oversized') -InputBytes $empty -TimeoutMilliseconds 2000 -MaximumOutputBytes 64
    $timeout = Invoke-Phase13BoundedProcess -Executable '{sys.executable}' -Arguments @('{fake}', 'timeout') -InputBytes $empty -TimeoutMilliseconds 50 -MaximumOutputBytes 64
    $preamble = (([Console]::InputEncoding.GetPreamble() | ForEach-Object {{ $_.ToString('X2') }}) -join '')
    [Console]::Out.Write("$($oversized.Reason)|$($timeout.Reason)|$($oversized.PSObject.Properties.Name -join ',')|$preamble")
}} finally {{
    [Console]::InputEncoding = $original
}}
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert result.stdout == "output_oversized|timeout|Reason,Document,ExitCode|EFBBBF"


def test_runner_resolves_only_fixed_private_trust_roots() -> None:
    invocation = f"""
. '{RUNNER}'
$usa = Get-Phase13RoleTransportContract -Role usa
$spain = Get-Phase13RoleTransportContract -Role spain
[Console]::Out.Write("$($usa.Role)|$($usa.TrustRoot)|$($usa.BindingPath)|$($usa.KeyPath)|$($usa.KnownHostsPath)`n")
[Console]::Out.Write("$($spain.Role)|$($spain.TrustRoot)|$($spain.BindingPath)|$($spain.KeyPath)|$($spain.KnownHostsPath)")
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert result.stdout.splitlines() == [
        "usa|C:\\ProgramData\\AMN2\\trust\\usa|C:\\ProgramData\\AMN2\\trust\\usa\\target.env|C:\\ProgramData\\AMN2\\trust\\usa\\id_ed25519|C:\\ProgramData\\AMN2\\trust\\usa\\known_hosts",
        "spain|C:\\ProgramData\\AMN2\\trust\\spain|C:\\ProgramData\\AMN2\\trust\\spain\\target.env|C:\\ProgramData\\AMN2\\trust\\spain\\id_ed25519|C:\\ProgramData\\AMN2\\trust\\spain\\known_hosts",
    ]


def test_runner_contract_has_fixed_bounds_and_no_stable_secret_output() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert "RandomNumberGenerator" in source
    assert "$script:MaximumTimeoutMilliseconds = 60000" in source
    assert "$script:MaximumOutputBytes = 1048576" in source
    assert "stable_fingerprints_persisted = $false" in source
    assert "ReadToEndAsync" not in source
    assert "ReadAsync" in source
    assert set(("usa", "spain")) <= set(
        value for value in ("usa" if '"usa"' in source else "", "spain" if '"spain"' in source else "") if value
    )
    for forbidden in ("Write-Host", "Write-Verbose", "Write-Debug", "Write-Warning"):
        assert forbidden not in source
