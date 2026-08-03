from __future__ import annotations

import base64
import hashlib
import hmac
import json
from pathlib import Path
import shutil
import shlex
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/vps/phase13_bot_web_migration_ssh_runner.ps1"
COLLECTOR = ROOT / "scripts/vps/phase13_bot_web_migration_readonly_remote.py"
MANIFEST_SCHEMA = (
    ROOT / "packaging/phase13-bot-web-migration/audit-tooling-manifest.schema.json"
)
AUDIT_SCHEMA = ROOT / "packaging/phase13-bot-web-migration/audit-evidence.schema.json"
NOW = "2026-08-03T09:00:00Z"


def powershell_executable() -> str:
    executable = shutil.which("powershell") or shutil.which("pwsh")
    if executable is None:
        pytest.skip("PowerShell is unavailable")
    return executable


def ps_literal(value: Path | str) -> str:
    return str(value).replace("'", "''")


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
        timeout=30,
    )


def materialize_package(
    output: Path,
    *,
    created_at: str = "2026-08-03T08:30:00Z",
    expires_at: str = "2026-08-03T10:30:00Z",
    collector_bytes: bytes | None = None,
) -> tuple[Path, dict[str, object]]:
    from scripts import phase13_bot_web_migration_audit_package as package

    artifacts = {
        artifact_id: f"verified-fixture:{artifact_id}\n".encode()
        for artifact_id in package.ARTIFACT_FILENAMES
    }
    artifacts.update(
        {
            "audit_evidence_schema": AUDIT_SCHEMA.read_bytes(),
            "audit_tooling_manifest_schema": MANIFEST_SCHEMA.read_bytes(),
            "readonly_collector": collector_bytes or COLLECTOR.read_bytes(),
            "ssh_runner": RUNNER.read_bytes(),
        }
    )
    inputs = package.AuditToolingPackageInputs(
        outcome_id="bot-web-audit-local-001",
        created_at=created_at,
        expires_at=expires_at,
        root_head=package.ROOT_HEAD,
        amn2_head=package.AMN2_HEAD,
        artifacts=artifacts,
    )
    package.materialize_local_audit_tooling_package(inputs, output)
    return output / "ssh-runner.ps1", json.loads((output / "manifest.json").read_bytes())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_approval(package_root: Path, manifest: dict[str, object]) -> str:
    artifacts = manifest["artifacts"]
    return (
        "УТВЕРЖДАЮ ОДИН TWO-HOST READ-ONLY USA/SPAIN BOT/WEB AUDIT "
        f"OUTCOME_{manifest['outcome_id']} "
        f"MANIFEST_SHA_{sha256(package_root / 'manifest.json')} "
        f"RUNNER_SHA_{artifacts['ssh_runner']['sha256']} "
        f"COLLECTOR_SHA_{artifacts['readonly_collector']['sha256']} "
        f"AUDIT_SCHEMA_SHA_{artifacts['audit_evidence_schema']['sha256']} "
        f"ROOT_BASE_{manifest['root_head']} AMN2_HEAD_{manifest['amn2_head']} "
        f"EXPIRES_AT_{manifest['expires_at']} MAX_ATTEMPTS_1 "
        "NO_BACKUP_NO_DATA_TRANSFER_NO_DEPLOY_NO_DB_APPLY_NO_BOT_CUTOVER_"
        "NO_USA_RELEASE_NO_MUTATION"
    )


def write_fake_ssh(path: Path) -> None:
    path.write_text(
        """from __future__ import annotations
import base64, hashlib, hmac, json, pathlib, sys
counter = pathlib.Path(sys.argv[1])
remote_command = sys.argv[-1]
role = 'usa' if remote_command.endswith(' usa') else 'spain'
counter.parent.mkdir(parents=True, exist_ok=True)
with counter.open('a', encoding='utf-8') as handle:
    handle.write(role + '\\n')
envelope = json.loads(sys.stdin.buffer.read())
key = base64.b64decode(envelope['ephemeral_hmac_key_b64'], validate=True)
collector = base64.b64decode(envelope['collector_b64'], validate=True)
if hashlib.sha256(collector).hexdigest() != envelope['collector_sha256']:
    raise SystemExit(22)
references = {
    'telegram_bot_token': 'same-token',
    'app_secret_key': role + '-app-secret',
    'web_password_hash': role + '-password',
    'web_session_secret': role + '-session',
}
proof = {name: hmac.new(key, value.encode(), hashlib.sha256).hexdigest()
         for name, value in references.items()}
audit_role = 'usa-source' if role == 'usa' else 'spain-target'
document = {
    'schema': 'amn2.phase13.bot-web-collector.v1',
    'role': role,
    'audit': {
        'schema': 'amn2.phase13.bot-web-audit.v1',
        'role': audit_role,
        'checked_at': '2026-08-03T09:00:00Z',
        'services': {'web_active': True, 'bot_active': role == 'usa',
                     'web_loopback_only': True},
        'database': {'integrity_ok': True, 'foreign_key_violations': 0,
                     'table_count': 2, 'schema_sha256': 'a' * 64,
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
    },
    'secret_reference_hmac': proof,
}
sys.stdout.write(json.dumps(document, sort_keys=True, separators=(',', ':')) + '\\n')
""",
        encoding="utf-8",
    )


def write_failing_fake_ssh(path: Path) -> None:
    path.write_text(
        """import pathlib, sys
counter = pathlib.Path(sys.argv[1])
with counter.open('a', encoding='utf-8') as handle:
    handle.write('attempt\\n')
sys.stderr.write('raw-secret-sentinel')
raise SystemExit(255)
""",
        encoding="utf-8",
    )


def test_public_entrypoint_has_only_two_parameters_and_rejects_wrong_approval(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / "package"
    packaged_runner, manifest = materialize_package(package_root)
    outcome_root = tmp_path / "outcomes"
    outcome_root.mkdir()
    invocation = f"""
. '{ps_literal(packaged_runner)}'
$names = @((Get-Command Invoke-Phase13ProductionAudit).Parameters.Keys | Sort-Object)
$message = 'not_blocked'
try {{
    $null = Test-Phase13AuditToolingBinding -PackageRoot '{ps_literal(package_root)}' -ExactApprovalPhrase 'wrong' -NowUtc ([DateTimeOffset]'{NOW}')
}} catch {{
    $message = $_.Exception.Message
}}
[Console]::Out.Write("$($names -join ',')|$message|$([IO.Directory]::GetFiles('{ps_literal(outcome_root)}').Count)")
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert result.stdout == "ExactApprovalPhrase,PackageRoot|exact approval mismatch|0"


def test_manifest_and_expiry_are_verified_before_claim_or_transport(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    packaged_runner, manifest = materialize_package(
        package_root,
        created_at="2026-08-03T07:00:00Z",
        expires_at="2026-08-03T08:00:00Z",
    )
    approval = exact_approval(package_root, manifest)
    outcome_root = tmp_path / "outcomes"
    outcome_root.mkdir()
    counter = tmp_path / "counter.txt"
    invocation = f"""
. '{ps_literal(packaged_runner)}'
$message = 'not_blocked'
try {{
    $null = Test-Phase13AuditToolingBinding -PackageRoot '{ps_literal(package_root)}' -ExactApprovalPhrase '{ps_literal(approval)}' -NowUtc ([DateTimeOffset]'{NOW}')
}} catch {{
    $message = $_.Exception.Message
}}
[Console]::Out.Write("$message|$([IO.Directory]::GetFiles('{ps_literal(outcome_root)}').Count)|$([IO.File]::Exists('{ps_literal(counter)}'))")
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert result.stdout == "audit tooling manifest expired|0|False"


def test_claim_precedes_exactly_two_fake_ssh_processes_and_success_is_sanitized(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / "package"
    packaged_runner, manifest = materialize_package(package_root)
    approval = exact_approval(package_root, manifest)
    outcome_root = tmp_path / "outcomes"
    outcome_root.mkdir()
    fake_ssh = tmp_path / "fake_ssh.py"
    counter = tmp_path / "counter.txt"
    write_fake_ssh(fake_ssh)
    invocation = f"""
. '{ps_literal(packaged_runner)}'
$binding = Test-Phase13AuditToolingBinding -PackageRoot '{ps_literal(package_root)}' -ExactApprovalPhrase '{ps_literal(approval)}' -NowUtc ([DateTimeOffset]'{NOW}')
$roles = @{{
    usa = [pscustomobject]@{{ TargetHost='usa.test'; TargetUser='operator'; KeyPath='fixed-key'; KnownHostsPath='fixed-known-hosts' }}
    spain = [pscustomobject]@{{ TargetHost='spain.test'; TargetUser='operator'; KeyPath='fixed-key'; KnownHostsPath='fixed-known-hosts' }}
}}
$first = Invoke-Phase13ProductionAuditCore -Binding $binding -OutcomeRoot '{ps_literal(outcome_root)}' -SshExecutable '{ps_literal(sys.executable)}' -SshPrefixArguments @('{ps_literal(fake_ssh)}','{ps_literal(counter)}') -RoleBindings $roles -NowUtc ([DateTimeOffset]'{NOW}')
$replay = 'not_blocked'
try {{
    $null = Invoke-Phase13ProductionAuditCore -Binding $binding -OutcomeRoot '{ps_literal(outcome_root)}' -SshExecutable '{ps_literal(sys.executable)}' -SshPrefixArguments @('{ps_literal(fake_ssh)}','{ps_literal(counter)}') -RoleBindings $roles -NowUtc ([DateTimeOffset]'{NOW}')
}} catch {{
    $replay = $_.Exception.Message
}}
$document = [IO.File]::ReadAllText($first.OutcomePath) | ConvertFrom-Json
[Console]::Out.Write((@{{
    counter = @([IO.File]::ReadAllLines('{ps_literal(counter)}'))
    decision = $document.decision
    outcome_id = $document.outcome_id
    raw_text = [IO.File]::ReadAllText($first.OutcomePath)
    replay = $replay
    ssh_processes = $document.evidence.safety_receipt.ssh_processes
    status = $first.Status
}} | ConvertTo-Json -Depth 8 -Compress))
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    document = json.loads(result.stdout)
    assert document["counter"] == ["usa", "spain"]
    assert document["decision"] == "passed"
    assert document["outcome_id"] == manifest["outcome_id"]
    assert document["replay"] == "outcome claim replay"
    assert document["ssh_processes"] == 2
    assert document["status"] == "success"
    for forbidden in (
        "secret_reference_hmac",
        "same-token",
        "app-secret",
        "TargetHost",
        "TargetUser",
    ):
        assert forbidden not in document["raw_text"]


def test_transport_failure_writes_only_create_new_sanitized_failure(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / "package"
    packaged_runner, manifest = materialize_package(package_root)
    approval = exact_approval(package_root, manifest)
    outcome_root = tmp_path / "outcomes"
    outcome_root.mkdir()
    fake_ssh = tmp_path / "failing_fake_ssh.py"
    counter = tmp_path / "counter.txt"
    write_failing_fake_ssh(fake_ssh)
    invocation = f"""
. '{ps_literal(packaged_runner)}'
$binding = Test-Phase13AuditToolingBinding -PackageRoot '{ps_literal(package_root)}' -ExactApprovalPhrase '{ps_literal(approval)}' -NowUtc ([DateTimeOffset]'{NOW}')
$roles = @{{
    usa = [pscustomobject]@{{ TargetHost='usa.test'; TargetUser='operator'; KeyPath='fixed-key'; KnownHostsPath='fixed-known-hosts' }}
    spain = [pscustomobject]@{{ TargetHost='spain.test'; TargetUser='operator'; KeyPath='fixed-key'; KnownHostsPath='fixed-known-hosts' }}
}}
$result = Invoke-Phase13ProductionAuditCore -Binding $binding -OutcomeRoot '{ps_literal(outcome_root)}' -SshExecutable '{ps_literal(sys.executable)}' -SshPrefixArguments @('{ps_literal(fake_ssh)}','{ps_literal(counter)}') -RoleBindings $roles -NowUtc ([DateTimeOffset]'{NOW}')
[Console]::Out.Write((@{{
    files = @([IO.Directory]::GetFiles('{ps_literal(outcome_root)}') | ForEach-Object {{ [IO.Path]::GetFileName($_) }} | Sort-Object)
    status = $result.Status
    text = [IO.File]::ReadAllText($result.OutcomePath)
}} | ConvertTo-Json -Depth 6 -Compress))
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    document = json.loads(result.stdout)
    assert document["status"] == "failure"
    assert document["files"] == [
        "bot-web-audit-local-001.claim.json",
        "bot-web-audit-local-001.failure.json",
    ]
    failure = json.loads(document["text"])
    assert failure == {
        "checked_at": NOW,
        "decision": "stop",
        "outcome_id": manifest["outcome_id"],
        "reason_code": "audit_incomplete",
        "safety_receipt": {
            "mutation_attempted": False,
            "raw_output_persisted": False,
            "secret_bearing_data_persisted": False,
        },
        "schema": "amn2.phase13.bot-web-migration-failure.v1",
        "stage": "audit",
    }
    assert "raw-secret-sentinel" not in document["text"]


def test_post_claim_internal_failure_still_writes_sanitized_failure(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / "package"
    packaged_runner, manifest = materialize_package(
        package_root,
        collector_bytes=b"x" * 800_000,
    )
    approval = exact_approval(package_root, manifest)
    outcome_root = tmp_path / "outcomes"
    outcome_root.mkdir()
    invocation = f"""
. '{ps_literal(packaged_runner)}'
$binding = Test-Phase13AuditToolingBinding -PackageRoot '{ps_literal(package_root)}' -ExactApprovalPhrase '{ps_literal(approval)}' -NowUtc ([DateTimeOffset]'{NOW}')
$roles = @{{
    usa = [pscustomobject]@{{ TargetHost='usa.test'; TargetUser='operator'; KeyPath='fixed-key'; KnownHostsPath='fixed-known-hosts' }}
    spain = [pscustomobject]@{{ TargetHost='spain.test'; TargetUser='operator'; KeyPath='fixed-key'; KnownHostsPath='fixed-known-hosts' }}
}}
$result = Invoke-Phase13ProductionAuditCore -Binding $binding -OutcomeRoot '{ps_literal(outcome_root)}' -SshExecutable '{ps_literal(sys.executable)}' -RoleBindings $roles -NowUtc ([DateTimeOffset]'{NOW}')
[Console]::Out.Write((@{{
    files = @([IO.Directory]::GetFiles('{ps_literal(outcome_root)}') | ForEach-Object {{ [IO.Path]::GetFileName($_) }} | Sort-Object)
    status = $result.Status
    text = [IO.File]::ReadAllText($result.OutcomePath)
}} | ConvertTo-Json -Depth 6 -Compress))
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    document = json.loads(result.stdout)
    assert document["status"] == "failure"
    assert document["files"] == [
        "bot-web-audit-local-001.claim.json",
        "bot-web-audit-local-001.failure.json",
    ]
    failure = json.loads(document["text"])
    assert failure["reason_code"] == "audit_incomplete"
    assert failure["safety_receipt"] == {
        "mutation_attempted": False,
        "raw_output_persisted": False,
        "secret_bearing_data_persisted": False,
    }
    assert "oversized" not in document["text"]


def test_public_receipt_does_not_expose_private_outcome_path(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    packaged_runner, _ = materialize_package(package_root)
    invocation = f"""
. '{ps_literal(packaged_runner)}'
$receipt = ConvertTo-Phase13PublicAuditReceipt -CoreResult ([pscustomobject]@{{ Status='success'; OutcomePath='C:\\private\\secret-path.json' }}) -OutcomeId 'bot-web-audit-local-001'
[Console]::Out.Write(($receipt | ConvertTo-Json -Compress))
"""

    result = run_powershell(invocation)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    receipt = json.loads(result.stdout)
    assert receipt == {
        "decision": "passed",
        "outcome_id": "bot-web-audit-local-001",
        "status": "success",
    }
    assert "path" not in result.stdout.lower()


def test_remote_bootstrap_rejects_collector_checksum_mismatch_before_exec(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / "package"
    packaged_runner, _ = materialize_package(package_root)
    invocation = f"""
. '{ps_literal(packaged_runner)}'
$role = [pscustomobject]@{{ TargetHost='usa.test'; TargetUser='operator'; KeyPath='fixed-key'; KnownHostsPath='fixed-known-hosts' }}
$arguments = New-Phase13AuditSshArguments -Role usa -RoleBinding $role
[Console]::Out.Write($arguments[$arguments.Count - 1])
"""
    generated = run_powershell(invocation)
    assert generated.returncode == 0, generated.stderr
    command = shlex.split(generated.stdout)
    assert command[:2] == ["python3", "-c"]
    envelope = json.dumps(
        {
            "collector_b64": base64.b64encode(
                b"print('collector-executed-sentinel')\n"
            ).decode(),
            "collector_sha256": "0" * 64,
            "ephemeral_hmac_key_b64": base64.b64encode(b"k" * 32).decode(),
        },
        separators=(",", ":"),
    ).encode()

    result = subprocess.run(
        [sys.executable, *command[1:]],
        input=envelope,
        check=False,
        capture_output=True,
        timeout=10,
    )

    assert result.returncode != 0
    assert result.stdout == b""
    assert b"collector-executed-sentinel" not in result.stdout
