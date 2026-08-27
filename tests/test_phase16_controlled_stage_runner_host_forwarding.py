from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
STAGE_RUNNER = ROOT / "scripts" / "vps" / "phase16_controlled_stage_ssh_runner.ps1"
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-015"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def ps_literal(value: Path | str) -> str:
    return str(value).replace("'", "''")


def run_powershell(harness: str) -> subprocess.CompletedProcess[str]:
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


class ControlledStageRunnerHostForwardingTest(unittest.TestCase):
    def test_forwards_expected_host_to_trust_assertion(self) -> None:
        expected_host = "138.124.181.246"
        harness = (
            f". '{STAGE_RUNNER}'\n"
            "$script:ObservedExpectedHost='not-called';"
            "function Assert-Phase16SpainTrustBundle {"
            "param([Parameter(Mandatory)][string]$ExpectedHost);"
            "$script:ObservedExpectedHost=$ExpectedHost;"
            "throw 'after_trust_assertion'"
            "};"
            "$StagePackageRoot='unused-after-trust-assertion';"
            "$StageApproval='unused-after-trust-assertion';"
            f"$StageExpectedCurrentStateSha256='{'a' * 64}';"
            "$StageTransactionId='phase16-stage-host-forwarding-test';"
            "$StageOutcomePath='unused-after-trust-assertion.json';"
            f"$StageExpectedHost='{expected_host}';"
            "try{Invoke-Phase16ControlledStageRunnerMain}"
            "catch{[Console]::Out.Write(($script:ObservedExpectedHost+'|'+$_.Exception.Message))}"
        )

        result = run_powershell(harness)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            f"{expected_host}|after_trust_assertion",
        )
        self.assertEqual(result.stderr, "")

    def test_failure_entrypoint_writes_allowlisted_artifact_and_fixed_stop_token(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            outcome_path = Path(temporary) / "outcome.json"
            failure_path = Path(str(outcome_path) + ".runner-failure.json")
            transaction_id = "phase16-stage-observability-test"
            harness = (
                f". '{ps_literal(STAGE_RUNNER)}'\n"
                "function Assert-Phase16SpainTrustBundle {"
                "param([Parameter(Mandatory)][string]$ExpectedHost);"
                "throw 'raw-sensitive-trust-detail'"
                "};"
                "$StagePackageRoot='unused-after-trust';"
                "$StageApproval='unused-after-trust';"
                f"$StageExpectedCurrentStateSha256='{'a' * 64}';"
                f"$StageTransactionId='{transaction_id}';"
                f"$StageOutcomePath='{ps_literal(outcome_path)}';"
                "$StageExpectedHost='138.124.181.246';"
                "$code=Invoke-Phase16ControlledStageRunnerEntrypoint;"
                "[Console]::Out.Write([string]$code)"
            )

            result = run_powershell(harness)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "64")
            self.assertEqual(
                result.stderr,
                "AMN2_PHASE16_CONTROLLED_STAGE_RUNNER_STOP\n",
            )
            failure = json.loads(failure_path.read_text(encoding="utf-8"))
            self.assertEqual(
                failure,
                {
                    "failure_class": "trust_validation",
                    "last_completed_milestone": "arguments_validated",
                    "package_id": PACKAGE_ID,
                    "raw_output_persisted": False,
                    "result": "runner_stop",
                    "schema": "amn2.phase16.controlled-stage-runner-failure.v1",
                    "stderr_bytes": 0,
                    "stderr_sha256": EMPTY_SHA256,
                    "stdout_bytes": 0,
                    "stdout_sha256": EMPTY_SHA256,
                    "transaction_id": transaction_id,
                    "transport_exit_code": None,
                },
            )
            serialized = failure_path.read_text(encoding="utf-8")
            self.assertNotIn("raw-sensitive-trust-detail", serialized)

    def test_failure_after_successful_trust_has_scalar_nonzero_process_exit(self) -> None:
        # A successful trust assertion must not turn the later exit 64 into an array.
        with tempfile.TemporaryDirectory() as temporary:
            outcome_path = Path(temporary) / "outcome.json"
            failure_path = Path(str(outcome_path) + ".runner-failure.json")
            harness = (
                f". '{ps_literal(STAGE_RUNNER)}'\n"
                "function Assert-Phase16SpainTrustBundle {"
                "param([Parameter(Mandatory)][string]$ExpectedHost);"
                "Get-Phase16SpainTrustContract"
                "};"
                "function Read-Phase16ControlledStagePackage {"
                "param([string]$Root);throw 'synthetic-package-rejection'"
                "};"
                "$StagePackageRoot='unused-local-fixture';"
                "$StageApproval='unused-local-fixture';"
                f"$StageExpectedCurrentStateSha256='{'a' * 64}';"
                "$StageTransactionId='phase16-local-scalar-exit-test';"
                f"$StageOutcomePath='{ps_literal(outcome_path)}';"
                "$StageExpectedHost='138.124.181.246';"
                "$code=Invoke-Phase16ControlledStageRunnerEntrypoint;exit $code"
            )

            result = run_powershell(harness)

            self.assertEqual(result.returncode, 64, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "AMN2_PHASE16_CONTROLLED_STAGE_RUNNER_STOP\n")
            self.assertFalse(outcome_path.exists())
            failure = json.loads(failure_path.read_bytes())
            self.assertEqual(failure["failure_class"], "package_validation")
            self.assertEqual(failure["last_completed_milestone"], "trust_validated")
            self.assertEqual(failure["transport_exit_code"], None)
            self.assertNotIn("synthetic-package-rejection", failure_path.read_text())

    def test_transport_failure_document_keeps_only_hashes_lengths_and_allowlists(
        self,
    ) -> None:
        stdout_text = "raw-sensitive-stdout"
        stderr_text = "raw-sensitive-stderr"
        harness = (
            f". '{ps_literal(STAGE_RUNNER)}'\n"
            "Reset-Phase16ControlledStageRunState;"
            "Set-Phase16ControlledStageFailureBoundary "
            "-FailureClass 'transport_output' "
            "-LastCompletedMilestone 'transport_completed';"
            "Set-Phase16ControlledStageTransportSummary "
            f"-StdoutText '{stdout_text}' -StderrText '{stderr_text}' -ExitCode 255;"
            "$document=New-Phase16ControlledStageFailureDocument "
            "-TransactionId 'phase16-stage-transport-test';"
            "[Console]::Out.Write((ConvertTo-Phase16CanonicalJsonText -Value $document))"
        )

        result = run_powershell(harness)

        self.assertEqual(result.returncode, 0, result.stderr)
        document = json.loads(result.stdout)
        self.assertEqual(document["failure_class"], "transport_output")
        self.assertEqual(document["last_completed_milestone"], "transport_completed")
        self.assertEqual(document["transport_exit_code"], 255)
        self.assertEqual(document["stdout_bytes"], len(stdout_text.encode("utf-8")))
        self.assertEqual(document["stderr_bytes"], len(stderr_text.encode("utf-8")))
        self.assertEqual(
            document["stdout_sha256"],
            hashlib.sha256(stdout_text.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            document["stderr_sha256"],
            hashlib.sha256(stderr_text.encode("utf-8")).hexdigest(),
        )
        self.assertNotIn(stdout_text, result.stdout)
        self.assertNotIn(stderr_text, result.stdout)

    def test_failure_document_rejects_unallowlisted_state(self) -> None:
        harness = (
            f". '{ps_literal(STAGE_RUNNER)}'\n"
            "Reset-Phase16ControlledStageRunState;"
            "$script:Phase16ControlledStageRunState.FailureClass='raw-detail';"
            "try {"
            "New-Phase16ControlledStageFailureDocument "
            "-TransactionId 'phase16-stage-invalid-state-test' | Out-Null;"
            "[Console]::Out.Write('accepted')"
            "} catch {[Console]::Out.Write($_.Exception.Message)}"
        )

        result = run_powershell(harness)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "failure_state_invalid")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
