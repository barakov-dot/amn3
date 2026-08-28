from __future__ import annotations

import base64
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/vps/phase16_controlled_stage_ssh_runner.ps1"
COORDINATOR = ROOT / "scripts/vps/phase16_controlled_stage_coordinator.py"
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-016"
EARLY_STDOUT = b"synthetic-early-exit-stdout"
EARLY_STDERR = b"synthetic-early-exit-stderr"


def literal(value: object) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def run_local_runner(
    directory: Path, *, input_encoding: str = "default", start_failure: bool = False,
    early_exit_code: int | None = None,
):
    """Run real framing/entrypoint with local trust/package/transport boundaries."""
    payload = hashlib.shake_256(b"phase16-local-binary-frame-fixture").digest(262144)
    payload_path = directory / "payload.bin"
    payload_path.write_bytes(payload)
    outcome_path = directory / "fixture-outcome.json"
    # Importing the coordinator only defines its functions. Never call execute_stage/main.
    consumer = f"""
import importlib.util, io, hashlib, sys, zipfile
spec = importlib.util.spec_from_file_location("local_frame_fixture", {str(COORDINATOR)!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
header, archive = module._read_frame()
with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
    payload = bundle.read("fixture/payload.bin")
result = {{
    "schema": "amn2.phase16.controlled-stage-outcome.v1",
    "package_id": {PACKAGE_ID!r},
    "general_issuance_enabled": False,
    "result": "application_and_awg31_staged",
    "local_test_only": True,
    "payload_size": len(payload),
    "payload_sha256": hashlib.sha256(payload).hexdigest(),
}}
sys.stdout.buffer.write(module.canonical_json_bytes(result))
""".encode("utf-8")
    if early_exit_code is not None:
        # Consume the header, then exit without draining the larger-than-pipe archive.
        consumer = f"""
import sys
stream = sys.stdin.buffer
header_size = int(stream.read(8), 16)
assert len(stream.read(header_size)) == header_size
sys.stdout.buffer.write({EARLY_STDOUT!r})
sys.stdout.buffer.flush()
sys.stderr.buffer.write({EARLY_STDERR!r})
sys.stderr.buffer.flush()
sys.exit({early_exit_code!r})
""".encode("utf-8")
    harness = "\n".join((
        f". {literal(RUNNER)}",
        (
            "[Console]::InputEncoding=[Text.UTF8Encoding]::new($true)"
            if input_encoding == "utf8_bom" else ""
        ),
        "$script:fixtureOriginalEncoding=[Console]::InputEncoding",
        "$script:localStartFactory=(Get-Command New-Phase16SshProcessStartInfo).ScriptBlock",
        "$script:fixtureCoordinator=[Convert]::FromBase64String("
        + literal(base64.b64encode(consumer).decode()) + ")",
        "$script:fixtureFiles=[Collections.Generic.List[object]]::new()",
        "$script:fixtureFiles.Add([pscustomobject]@{Path='fixture/payload.bin';"
        + f"Bytes=[IO.File]::ReadAllBytes({literal(payload_path)})" + "})",
        "$script:fixtureFiles.Add([pscustomobject]@{"
        "Path='tooling/scripts/vps/phase16_controlled_stage_coordinator.py';"
        "Bytes=$script:fixtureCoordinator})",
        "function Assert-Phase16SpainTrustBundle {"
        "param([Parameter(Mandatory)][string]$ExpectedHost);Get-Phase16SpainTrustContract}",
        "function Read-Phase16ControlledStagePackage {"
        "param([string]$Root);"
        "return [pscustomobject]@{CoordinatorBytes=$script:fixtureCoordinator;"
        "Files=$script:fixtureFiles;Manifest=[pscustomobject]@{package_identity_sha256=('b'*64)};"
        "ManifestSha256=('c'*64)}}",
        # Reuse the actual argument builder/bootstrap and clean child environment.
        # Replace the executable before Process.Start; never start ssh.exe.
        "function New-Phase16SshProcessStartInfo {"
        "param([string[]]$Arguments);"
        "$parts=[regex]::Match($Arguments[-1],"
        + literal(r"^/usr/bin/python3 -I -B -c '([^']+)' '([0-9a-f]{64})'$") + ");"
        "if(-not $parts.Success){throw 'local_bootstrap_shape'};"
        "$start=& $script:localStartFactory -Arguments @('-I','-B','-c',"
        "$parts.Groups[1].Value,$parts.Groups[2].Value);"
        f"$start.FileName={literal(directory / 'nonexistent-child.exe' if start_failure else sys.executable)};"
        "return $start}",
        "$StagePackageRoot='unused-local-fixture'",
        "$StageExpectedCurrentStateSha256=('a'*64)",
        "$StageTransactionId='phase16-local-frame-test'",
        f"$StageOutcomePath={literal(outcome_path)}",
        "$StageExpectedHost='138.124.181.246'",
        "$script:Phase16ControlledStageTimeoutMilliseconds=3000",
        "$localRollback=Get-Phase16CanonicalJsonSha256 -Value (Get-Phase16ControlledStageRollbackScope)",
        '$StageApproval="/APPROVE PHASE16 SPAIN APPLICATION_AND_AWG31_STAGE '
        'PACKAGE_$($script:Phase16ControlledStagePackageId) IDENTITY_$(\'b\'*64) '
        'MANIFEST_SHA256_$(\'c\'*64) STATE_$StageExpectedCurrentStateSha256 '
        'ROLLBACK_SCOPE_SHA256_$localRollback TRANSACTION_$StageTransactionId '
        'MANDATORY_ROLLBACK_ON_FAILURE AWG2_UNTOUCHED"',
        "$code=Invoke-Phase16ControlledStageRunnerEntrypoint;"
        "if([Console]::InputEncoding.CodePage -ne $script:fixtureOriginalEncoding.CodePage -or "
        "[Convert]::ToBase64String([Console]::InputEncoding.GetPreamble()) -cne "
        "[Convert]::ToBase64String($script:fixtureOriginalEncoding.GetPreamble()))"
        "{throw 'local_input_encoding_not_restored'};exit $code",
    ))
    environment = dict(os.environ)
    environment.pop("PSModulePath", None)
    result = subprocess.run(
        [str(POWERSHELL), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
         "-Command", harness],
        capture_output=True, text=True, check=False, timeout=15, env=environment,
    )
    failure_path = Path(str(outcome_path) + ".runner-failure.json")
    failure = json.loads(failure_path.read_bytes()) if failure_path.exists() else None
    outcome = json.loads(outcome_path.read_bytes()) if outcome_path.exists() else None
    return result, outcome, failure, payload


class ControlledStageLocalTransportTest(unittest.TestCase):
    def test_early_exit_during_archive_write_retains_only_normalized_diagnostics(self):
        for exit_code in (0, 65):
            with self.subTest(exit_code=exit_code):
                with tempfile.TemporaryDirectory() as temporary:
                    result, outcome, failure, _ = run_local_runner(
                        Path(temporary), early_exit_code=exit_code,
                    )
                self.assertEqual(result.returncode, 64, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "AMN2_PHASE16_CONTROLLED_STAGE_RUNNER_STOP\n")
                self.assertIsNone(outcome)
                self.assertEqual(failure["failure_class"], "stdin_write")
                self.assertEqual(failure["last_completed_milestone"], "process_started")
                self.assertEqual(failure["transport_exit_code"], exit_code)
                self.assertEqual(failure["schema"], "amn2.phase16.controlled-stage-runner-failure.v2")
                self.assertEqual(failure["stdin_write_segment"], "archive")
                self.assertEqual(failure["stdin_exception_class"], "io_error")
                self.assertEqual(failure["transport_exit_class"], "zero_exit" if exit_code == 0 else "nonzero_exit")
                self.assertEqual(failure["transport_summary_state"], "complete")
                for name, raw in (("stdout", EARLY_STDOUT), ("stderr", EARLY_STDERR)):
                    self.assertEqual(failure[f"{name}_bytes"], len(raw))
                    self.assertEqual(failure[f"{name}_sha256"], hashlib.sha256(raw).hexdigest())
                    self.assertNotIn(raw.decode(), json.dumps(failure))
                self.assertFalse(failure["raw_output_persisted"])

    def test_start_failure_restores_input_encoding_and_retains_stop_contract(self):
        with tempfile.TemporaryDirectory() as temporary:
            result, outcome, failure, _ = run_local_runner(
                Path(temporary), input_encoding="utf8_bom", start_failure=True,
            )
        self.assertEqual(result.returncode, 64, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "AMN2_PHASE16_CONTROLLED_STAGE_RUNNER_STOP\n")
        self.assertIsNone(outcome)
        self.assertEqual(failure["failure_class"], "process_start")
        self.assertEqual(failure["last_completed_milestone"], "archive_built")

    def test_frame_parser_still_rejects_truncation_and_trailing_bytes(self):
        spec = importlib.util.spec_from_file_location("frame_rejection_fixture", COORDINATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        archive = b"local-archive-fixture"
        header = {
            "approval": "local-fixture", "request": {},
            "archive_size": len(archive),
            "archive_sha256": hashlib.sha256(archive).hexdigest(),
            "coordinator_sha256": "a" * 64,
        }
        header_bytes = (json.dumps(header, sort_keys=True, separators=(",", ":")) + "\n").encode()
        prefix = f"{len(header_bytes):08x}".encode()
        for body, error in (
            (prefix[:7], "frame header"),
            (prefix + header_bytes[:-1], "frame header"),
            (prefix + header_bytes + archive[:-1], "archive frame"),
            (prefix + header_bytes + archive + b"x", "archive frame"),
            (prefix + header_bytes + archive + b"\xef\xbb\xbf", "archive frame"),
        ):
            with self.subTest(error=error, size=len(body)):
                with patch.object(module.sys, "stdin", SimpleNamespace(buffer=io.BytesIO(body))):
                    with self.assertRaisesRegex(module.StageCoordinatorError, error):
                        module._read_frame()

    def test_binary_frame_stays_exact_when_console_encoding_has_utf8_preamble(self):
        # Binary framing must not inherit a text writer's UTF-8 preamble.
        with tempfile.TemporaryDirectory() as temporary:
            result, outcome, failure, payload = run_local_runner(
                Path(temporary), input_encoding="utf8_bom",
            )
        self.assertEqual(result.returncode, 0, (result.stderr, failure))
        self.assertEqual(result.stderr, "")
        self.assertIsNone(failure)
        self.assertEqual(outcome["payload_sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(outcome["payload_size"], 262144)
        self.assertTrue(outcome["local_test_only"])
        self.assertEqual(json.loads(result.stdout), outcome)

    def test_binary_frame_and_eof_reach_real_parser_without_ssh(self):
        # Catches byte/prefix corruption, incomplete writes and missing EOF.
        with tempfile.TemporaryDirectory() as temporary:
            result, outcome, failure, payload = run_local_runner(Path(temporary))
        self.assertEqual(result.returncode, 0, (result.stderr, failure))
        self.assertEqual(result.stderr, "")
        self.assertIsNone(failure)
        self.assertTrue(outcome["local_test_only"])
        self.assertFalse(outcome["general_issuance_enabled"])
        self.assertEqual(outcome["payload_size"], 262144)
        self.assertEqual(outcome["payload_sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(json.loads(result.stdout), outcome)


if __name__ == "__main__":
    unittest.main()
