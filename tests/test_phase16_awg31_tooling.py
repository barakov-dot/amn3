from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-002"
RUNTIME_IDENTITY = (
    "docker.io/amneziavpn/amneziawg-go@"
    "sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d"
)
CLIENT_IDENTITY = (
    "github:amnezia-vpn/amneziawg-android/releases/v3.1.20260814/"
    "AmneziaWG-3.1.202060814.apk@"
    "sha256:74f109a948f012e8b90b4055e98bb9bee77bbb8e5d0fe7d5a057dd9698009697"
)
PACKAGE_SCRIPT = ROOT / "scripts" / "phase16_awg31_package.py"
PREFLIGHT_SCRIPT = ROOT / "scripts" / "phase16_preflight_contract.py"
CONTRACT_ROOT = ROOT / "packaging" / "phase16-awg3-family-3-1-spain-pilot-contract"
APPLICATION_STAGE = ROOT / "scripts" / "vps" / "phase16_application_stage_remote.sh"
RUNTIME_STAGE = ROOT / "scripts" / "vps" / "phase16_awg31_runtime_stage_remote.sh"
COLLECTOR = ROOT / "scripts" / "vps" / "phase16_spain_readonly_preflight_remote.sh"
RUNNER = ROOT / "scripts" / "vps" / "phase16_spain_readonly_preflight_ssh_runner.ps1"
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")


def run_powershell(body: str):
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


def load_module(path: Path, name: str):
    if not path.is_file():
        pytest.fail(f"missing Phase 16 tooling: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def test_phase16_package_and_preflight_identities_are_exact():
    package = load_module(PACKAGE_SCRIPT, "phase16_package")
    preflight = load_module(PREFLIGHT_SCRIPT, "phase16_preflight")

    assert package.PACKAGE_ID == PACKAGE_ID
    assert package.SOURCE_BRANCH == "codex/phase16-awg3-family-3-1-spain-pilot"
    assert package.TOOLING_BRANCH == package.SOURCE_BRANCH
    assert package.MANIFEST_SCHEMA == "amn2.phase16.package-manifest.v1"
    assert preflight.PACKAGE_ID == PACKAGE_ID
    assert preflight.CLAIM_SCHEMA == "amn2.phase16.readonly-preflight-claim.v1"
    assert preflight.EVIDENCE_SCHEMA == "amn2.phase16.readonly-preflight-evidence.v1"


def test_resource_plan_binds_awg31_runtime_client_capabilities_and_rollback():
    package = load_module(PACKAGE_SCRIPT, "phase16_package_resource")
    raw = (CONTRACT_ROOT / "resource-plan.json").read_bytes()
    value = json.loads(raw.decode("utf-8"))

    assert raw == canonical(value)
    assert value == package.RESOURCE_PLAN
    assert value["package_id"] == PACKAGE_ID
    assert value["protocol"] == {
        "config_revision": "amneziawg_v3_1",
        "family": "awg3",
        "revision": "3.1",
    }
    assert value["runtime"] == {
        "artifact_identity": RUNTIME_IDENTITY,
        "capabilities": ["disable_cookies", "random_trailers"],
        "source_commit": "1f50ad736ecca22a9bfc7b4606805ec9ca49fe48",
    }
    assert value["pilot_client"] == {
        "application": "amneziawg",
        "artifact_identity": CLIENT_IDENTITY,
        "build": "12",
        "platform": "android",
        "release_kind": "stable",
        "version": "v3.1.20260814",
    }
    assert value["controls"] == {
        "awg2_untouched": True,
        "general_issuance_enabled": False,
        "rollback_required": True,
        "stage_requires_separate_claim": True,
    }


def test_preflight_claim_remains_checksum_host_and_one_time_bound():
    contract = load_module(PREFLIGHT_SCRIPT, "phase16_preflight_claim")
    claim = {
        "claim_id": "phase16-preflight-test-001",
        "collector_sha256": "b" * 64,
        "consumed_at": None,
        "expected_host": "spain.test.invalid",
        "expires_at": "2026-08-24T13:00:00Z",
        "future_gate": "PREFLIGHT",
        "issued_at": "2025-08-24T12:00:00Z",
        "manifest_sha256": "a" * 64,
        "package_id": PACKAGE_ID,
        "schema": "amn2.phase16.readonly-preflight-claim.v1",
        "status": "issued",
    }

    validated = contract.validate_claim(
        claim,
        package_id=PACKAGE_ID,
        manifest_sha256="a" * 64,
        collector_sha256="b" * 64,
        expected_host="spain.test.invalid",
        now=dt.datetime(2026, 8, 24, 12, 30, tzinfo=dt.timezone.utc),
    )
    assert validated == claim
    changed = dict(claim, manifest_sha256="c" * 64)
    with pytest.raises(contract.PreflightContractError, match="checksum"):
        contract.validate_claim(
            changed,
            package_id=PACKAGE_ID,
            manifest_sha256="a" * 64,
            collector_sha256="b" * 64,
            expected_host="spain.test.invalid",
            now=dt.datetime(2026, 8, 24, 12, 30, tzinfo=dt.timezone.utc),
        )


def stage_claim(script: Path, gate: str, **overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "claim_id": "phase16-stage-test-001",
        "consumed_at": None,
        "expected_current_state_sha256": "c" * 64,
        "expires_at": "2099-08-24T13:00:00Z",
        "future_gate": gate,
        "issued_at": "2025-08-24T12:00:00Z",
        "manifest_sha256": "d" * 64,
        "package_id": PACKAGE_ID,
        "package_identity_sha256": "e" * 64,
        "rollback_scope_sha256": "f" * 64,
        "schema": "amn2.phase16.stage-claim.v1",
        "stage_script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "status": "issued",
    }
    value.update(overrides)
    return value


def local_stage(tmp_path: Path, source: Path) -> Path:
    text = source.read_text(encoding="utf-8")
    text = text.replace(
        "/usr/bin/python3 -I -B -",
        f"{shlex.quote(sys.executable.replace(chr(92), '/'))} -I -B -",
    )
    target = tmp_path / source.name
    target.write_text(text, encoding="utf-8", newline="\n")
    return target


def run_stage(tmp_path: Path, source: Path, gate: str, *, overrides: dict[str, object] | None = None):
    runtime = local_stage(tmp_path, source)
    claim_path = tmp_path / f"{gate.lower()}-claim.json"
    claim = stage_claim(runtime, gate, **(overrides or {}))
    claim_path.write_bytes(canonical(claim))
    env = os.environ.copy()
    env.update(
        {
            "PHASE16_EXPECTED_CURRENT_STATE_SHA256": "c" * 64,
            "PHASE16_FUTURE_GATE": gate,
            "PHASE16_MANIFEST_SHA256": "d" * 64,
            "PHASE16_PACKAGE_ID": PACKAGE_ID,
            "PHASE16_PACKAGE_IDENTITY_SHA256": "e" * 64,
            "PHASE16_ROLLBACK_SCOPE_SHA256": "f" * 64,
            "PHASE16_STAGE_CLAIM_FILE": str(claim_path).replace("\\", "/"),
        }
    )
    before = claim_path.read_bytes()
    result = subprocess.run(
        [str(BASH), str(runtime)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    return result, before, claim_path.read_bytes()


@pytest.mark.parametrize(
    ("script", "gate"),
    ((APPLICATION_STAGE, "APPLICATION_STAGE"), (RUNTIME_STAGE, "AWG31_RUNTIME_STAGE")),
)
def test_valid_stage_claim_reaches_input_gate_without_mutation(
    tmp_path: Path, script: Path, gate: str
):
    result, before, after = run_stage(tmp_path, script, gate)

    assert result.returncode == 66
    assert result.stdout == ""
    assert result.stderr == "stage_inputs_required\n"
    assert after == before


@pytest.mark.parametrize(
    ("script", "gate"),
    ((APPLICATION_STAGE, "APPLICATION_STAGE"), (RUNTIME_STAGE, "AWG31_RUNTIME_STAGE")),
)
def test_stage_claim_rejects_wrong_rollback_binding(
    tmp_path: Path, script: Path, gate: str
):
    result, before, after = run_stage(
        tmp_path, script, gate, overrides={"rollback_scope_sha256": "0" * 64}
    )

    assert result.returncode == 65
    assert result.stdout == ""
    assert result.stderr == "claim_invalid\n"
    assert after == before


def test_application_stage_is_backup_first_claim_bound_and_rollback_aware():
    source = APPLICATION_STAGE.read_text(encoding="utf-8")

    assert source.index("create_checksum_bound_db_backup") < source.index(
        "stage_application_snapshot"
    )
    assert "rollback_application_stage" in source
    assert "trap rollback_application_stage ERR" in source
    assert "package_identity_sha256" in source
    assert "rollback_scope_sha256" in source
    assert "ENABLE_ISSUANCE" not in source


def test_runtime_stage_is_pinned_capability_checked_and_awg2_isolated():
    source = RUNTIME_STAGE.read_text(encoding="utf-8")

    assert RUNTIME_IDENTITY in source
    assert "verify_runtime_capabilities" in source
    assert "random_trailers" in source
    assert "disable_cookies" in source
    assert "rollback_awg31_stage" in source
    assert "trap rollback_awg31_stage ERR" in source
    assert "amn2-spain-awg3" in source
    assert "amn2sp3br0" in source
    assert "30002" in source
    assert re.search(r"systemctl\s+(?:restart|stop)\s+amn2-spain-awg2", source) is None
    assert re.search(r"docker\s+rm[^\n]*amn2-spain-awg2", source) is None
    assert "ENABLE_ISSUANCE" not in source


def test_phase16_preflight_transport_assets_are_read_only_and_phase_exact():
    contract = PREFLIGHT_SCRIPT.read_text(encoding="utf-8")
    collector = COLLECTOR.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")
    combined = "\n".join((contract, collector, runner))

    assert PACKAGE_ID in collector
    assert PACKAGE_ID in runner
    assert "phase15-dual-protocol-bootstrap-20260811-001" not in combined
    assert "recovery_markers_phase14_phase15_phase16" in contract
    assert "recovery_markers_phase14_phase15_phase16" in collector
    assert "phase14_phase16_phase16" not in combined
    assert "phase16_spain_readonly_preflight_remote.sh" in runner
    assert "$script:Phase16PackageId" in runner
    for pattern in (
        r"systemctl\s+(?:restart|stop|start|enable)\b",
        r"(?:docker|podman)\s+(?:run|rm|pull)\b",
        r"iptables\s+-(?:A|D)\b",
        r"nft\s+(?:add|delete)\b",
        r"ip\s+link\s+(?:add|delete|set)\b",
        r"\bsqlite3\s",
    ):
        assert re.search(pattern, collector, flags=re.IGNORECASE) is None


def test_phase16_ssh_process_environment_keeps_windows_openssh_runnable():
    result = run_powershell(
        "$start=New-Phase16SshProcessStartInfo -Arguments @('-V');"
        "$process=[Diagnostics.Process]::new();$process.StartInfo=$start;"
        "try{if(-not $process.Start()){throw 'ssh_start_failed'};"
        "$stdoutTask=$process.StandardOutput.ReadToEndAsync();"
        "$stderrTask=$process.StandardError.ReadToEndAsync();"
        "if(-not $process.WaitForExit(5000)){$process.Kill();throw 'ssh_timeout'};"
        "$stdout=$stdoutTask.GetAwaiter().GetResult();"
        "$stderr=$stderrTask.GetAwaiter().GetResult();"
        "[Console]::Out.Write(($process.ExitCode.ToString()+'|'+$stdout.Length.ToString()+'|'+$stderr.Trim()))"
        "}finally{$process.Dispose()}"
    )

    assert result.returncode == 0, result.stderr
    exit_code, stdout_length, version = result.stdout.split("|", 2)
    assert exit_code == "0"
    assert stdout_length == "0"
    assert version.startswith("OpenSSH_for_Windows_")


@pytest.mark.parametrize("program_data", ("", r"C:\Windows"))
def test_phase16_ssh_process_environment_rejects_untrusted_programdata(program_data: str):
    escaped = program_data.replace("'", "''")
    result = run_powershell(
        f"$env:ProgramData='{escaped}';"
        "try{$null=New-Phase16SshProcessStartInfo -Arguments @('-V');"
        "[Console]::Out.Write('accepted')}"
        "catch{[Console]::Out.Write($_.Exception.Message)}"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "local_environment_invalid"


def test_existing_safe_shared_amn2_namespace_allows_managed_phase16_leaf_provisioning():
    result = run_powershell(
        "$script:events=[Collections.Generic.List[string]]::new();$script:facts=@{};"
        "$authorized='S-1-5-21-1000';$anchor='C:\\ProgramData';"
        "$root='C:\\ProgramData\\AMN2\\phase16\\readonly-preflight';"
        "$full=[int64][Security.AccessControl.FileSystemRights]::FullControl;$inherit=3;"
        "$platform=@([pscustomobject]@{Sid='S-1-3-0';Type='Allow';Rights=[int64]268435456;IsInherited=$false;Inheritance=3;Propagation=2},"
        "[pscustomobject]@{Sid='S-1-5-18';Type='Allow';Rights=[int64]2032127;IsInherited=$false;Inheritance=3;Propagation=0},"
        "[pscustomobject]@{Sid='S-1-5-32-544';Type='Allow';Rights=[int64]2032127;IsInherited=$false;Inheritance=3;Propagation=0},"
        "[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]278;IsInherited=$false;Inheritance=1;Propagation=0},"
        "[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]1179817;IsInherited=$false;Inheritance=3;Propagation=0});"
        "$shared=@($platform|ForEach-Object{$copy=$_.PSObject.Copy();$copy.IsInherited=$true;$copy});"
        "function New-ManagedFacts($path){$rules=@('S-1-5-21-1000','S-1-5-18','S-1-5-32-544'|ForEach-Object{[pscustomobject]@{Sid=$_;Type='Allow';Rights=$full;IsInherited=$false;Inheritance=$inherit;Propagation=0}});[pscustomobject]@{Exists=$true;FullName=$path;IsDirectory=$true;IsReparse=$false;OwnerSid=$authorized;Protected=$true;Rules=$rules}};"
        "$script:facts[$anchor]=[pscustomobject]@{Exists=$true;FullName=$anchor;IsDirectory=$true;IsReparse=$false;OwnerSid='S-1-5-18';Protected=$true;Rules=$platform};"
        "$amn2=Join-Path $anchor 'AMN2';$script:facts[$amn2]=[pscustomobject]@{Exists=$true;FullName=$amn2;IsDirectory=$true;IsReparse=$false;OwnerSid='S-1-5-32-544';Protected=$false;Rules=$shared};"
        "function Enter-Phase16StateRootCreationLock{$script:events.Add('lock');[pscustomobject]@{Acquired=$true}};"
        "function Exit-Phase16StateRootCreationLock{param($Lock)$script:events.Add('unlock')};"
        "function Get-Phase16StateDirectoryFacts{param($Path)if($script:facts.ContainsKey($Path)){return $script:facts[$Path]};[pscustomobject]@{Exists=$false;FullName=$Path}};"
        "function New-Phase16SecureStateDirectory{param($ParentPath,$Path,$AuthorizedSid)$script:events.Add('create:'+([IO.Path]::GetFileName($Path)));$script:facts[$Path]=New-ManagedFacts $Path};"
        "$message='';$actual='';$chain='';try{$actual=Initialize-Phase16TrustedStateRoot -AnchorPath $anchor -StateRoot $root -AuthorizedSid $authorized;$chain=Assert-Phase16TrustedManagedStateChain -StateRoot $root -AuthorizedSid $authorized -RequiredChildren @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')}catch{$message=$_.Exception.Message};"
        "$created=@($script:events|Where-Object{$_ -like 'create:*'}|ForEach-Object{$_.Substring(7)});"
        "[Console]::Out.Write(\"$message|$($actual -ceq $root)|$($chain -ceq $root)|$($created -join ',')\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "|True|True|phase16,readonly-preflight,locks,outcome-locks,claims,"
        "transactions,recovery-outcomes,outcomes"
    )


def test_shared_amn2_namespace_rejects_reparse_extra_acl_and_wrong_owner():
    result = run_powershell(
        "$rules=@([pscustomobject]@{Sid='S-1-3-0';Type='Allow';Rights=[int64]268435456;IsInherited=$true;Inheritance=3;Propagation=2},"
        "[pscustomobject]@{Sid='S-1-5-18';Type='Allow';Rights=[int64]2032127;IsInherited=$true;Inheritance=3;Propagation=0},"
        "[pscustomobject]@{Sid='S-1-5-32-544';Type='Allow';Rights=[int64]2032127;IsInherited=$true;Inheritance=3;Propagation=0},"
        "[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]278;IsInherited=$true;Inheritance=1;Propagation=0},"
        "[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]1179817;IsInherited=$true;Inheritance=3;Propagation=0});"
        "$valid=[pscustomobject]@{Exists=$true;FullName='C:\\ProgramData\\AMN2';IsDirectory=$true;IsReparse=$false;OwnerSid='S-1-5-32-544';Protected=$false;Rules=$rules};"
        "$reparse=$valid.PSObject.Copy();$reparse.IsReparse=$true;"
        "$extra=$valid.PSObject.Copy();$extra.Rules=@($rules+[pscustomobject]@{Sid='S-1-1-0';Type='Allow';Rights=[int64]2032127;IsInherited=$true;Inheritance=3;Propagation=0});"
        "$owner=$valid.PSObject.Copy();$owner.OwnerSid='S-1-5-32-545';"
        "$values=@($valid,$reparse,$extra,$owner|ForEach-Object{(Test-Phase16SharedNamespaceDirectoryFacts -Facts $_ -ExpectedPath 'C:\\ProgramData\\AMN2').ToString().ToLowerInvariant()});"
        "[Console]::Out.Write(($values -join '|'))"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false|false|false"


def test_phase16_manifest_schema_matches_closed_package_inventory():
    package = load_module(PACKAGE_SCRIPT, "phase16_package_schema")
    schema_path = CONTRACT_ROOT / "package-manifest.schema.json"
    raw = schema_path.read_bytes()
    schema = json.loads(raw.decode("utf-8"))

    assert raw == canonical(schema)
    assert schema["$id"] == "amn2.phase16.package-manifest.v1"
    assert schema["additionalProperties"] is False
    assert schema["properties"]["package_id"] == {"const": PACKAGE_ID}
    assert schema["properties"]["source"]["properties"]["branch"] == {
        "const": package.SOURCE_BRANCH
    }
    assert schema["properties"]["tooling"]["properties"]["branch"] == {
        "const": package.TOOLING_BRANCH
    }
    _entry_contract, closed_inventory = schema["properties"]["entries"]["items"][
        "allOf"
    ]
    fixed_paths = {
        branch["properties"]["path"]["const"]
        for branch in closed_inventory["oneOf"]
        if "const" in branch["properties"]["path"]
    }
    assert fixed_paths == set(package.REQUIRED_ENTRY_SPECS)
