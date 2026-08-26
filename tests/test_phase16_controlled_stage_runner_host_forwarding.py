from __future__ import annotations

from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
STAGE_RUNNER = ROOT / "scripts" / "vps" / "phase16_controlled_stage_ssh_runner.ps1"
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")


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

        result = subprocess.run(
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

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            f"{expected_host}|after_trust_assertion",
        )
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
