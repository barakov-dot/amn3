"""Offline contract tests. Children only emit synthetic bytes, exit or sleep.

No sockets, profiles, adapters, curl, ping, SSH or external services are used.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts/vps/phase16_windows_measurement_helper.ps1"
PWSH = shutil.which("pwsh") or str(
    Path(os.environ.get("USERPROFILE", ""))
    / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe"
)


def literal(value):
    return "'" + str(value).replace("'", "''") + "'"


class WindowsMeasurementTest(unittest.TestCase):
    def run_ps(self, body):
        self.assertTrue(HELPER.is_file(), "measurement helper not implemented")
        code = (
            "$ErrorActionPreference='Stop'; . " + literal(HELPER) + "; " + body
        )
        result = subprocess.run(
            [PWSH, "-NoLogo", "-NoProfile", "-NonInteractive", "-EncodedCommand",
             base64.b64encode(code.encode("utf-16le")).decode()],
            capture_output=True, text=True, timeout=12,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)

    def summary(self, samples, validated=True):
        encoded = base64.b64encode(json.dumps(samples).encode()).decode()
        return self.run_ps(
            f"$samples=ConvertFrom-Json ([Text.Encoding]::UTF8.GetString("
            f"[Convert]::FromBase64String('{encoded}'))); "
            "Get-Phase16RttSummary -Samples @($samples) "
            f"-ProbePathValidated ${str(validated).lower()} | ConvertTo-Json -Depth 4"
        )

    def child(self, program, *, timeout=2500, output=1024, input_body="@()", max_input=0):
        return self.run_ps(
            "$r=Invoke-Phase16BoundedProcess "
            f"-FilePath {literal(sys.executable)} "
            f"-ArgumentList @('-I','-B','-c',{literal(program)}) "
            f"-InputBytes ([byte[]]({input_body})) -MaxInputBytes {max_input} "
            f"-MaxOutputBytes {output} -TimeoutMs {timeout} -CleanupReserveMs 500; "
            "$alive=$false; if($r.process_id) { "
            "$alive=$null -ne (Get-Process -Id $r.process_id -ErrorAction SilentlyContinue) }; "
            "@{result=$r;child_alive=$alive} | ConvertTo-Json -Depth 5"
        )

    def test_rtt_nearest_rank_median_jitter_and_loss_are_hand_derived(self):
        # Catch p95 off-by-one, sorting before jitter, and denominator errors.
        rows = [dict(sequence=i + 1, status="success", rtt_ms=v)
                for i, v in enumerate(range(1, 101))]
        rows.append(dict(sequence=101, status="timeout", rtt_ms=None))
        got = self.summary(rows)
        self.assertEqual(got["median_ms"], 50.5)
        self.assertEqual(got["p95_ms"], 95)
        self.assertEqual(got["jitter_ms"], 1)
        self.assertAlmostEqual(got["loss_percent"], 100 / 101, places=6)
        self.assertEqual(got["readiness"], "MEASURED")
        self.assertNotIn("PASS", json.dumps(got))

    def test_sequence_order_not_sorted_latency_drives_jitter(self):
        got = self.summary([
            dict(sequence=1, status="success", rtt_ms=30),
            dict(sequence=2, status="success", rtt_ms=10),
            dict(sequence=3, status="success", rtt_ms=50),
        ])
        self.assertEqual(got["jitter_ms"], 30)
        self.assertEqual(got["readiness"], "INCOMPLETE")

    def test_invalid_path_and_send_errors_cannot_become_zero_loss_pass(self):
        for rows, valid in [([], True),
                            ([dict(sequence=1, status="timeout", rtt_ms=None)], False),
                            ([dict(sequence=1, status="send_error", rtt_ms=None)], True),
                            ([dict(sequence=1, status="canceled", rtt_ms=None)], True)]:
            with self.subTest(rows=rows):
                got = self.summary(rows, valid)
                self.assertIsNone(got["loss_percent"])
                self.assertIsNone(got["p95_ms"])
                self.assertEqual(got["readiness"], "INCOMPLETE")

    def test_schema_rejects_raw_fields_bad_numbers_and_bad_sequence(self):
        got = self.run_ps("""
            $cases=@(
                @{sequence=1;status='success';rtt_ms=1;endpoint='secret-fixture'},
                @{sequence=1;status='success';rtt_ms=[double]::NaN},
                @{sequence=1;status='success';rtt_ms=-1},
                @{sequence=1;status='success';rtt_ms=1e308},
                @{sequence=2;status='success';rtt_ms=1},
                @{sequence=1;status='secret-fixture';rtt_ms=$null},
                @{sequence=1;status='timeout';rtt_ms=1}
            ); $errors=@(foreach($row in $cases) {
                try { Get-Phase16RttSummary -Samples @([pscustomobject]$row) -ProbePathValidated $true }
                catch { $_.Exception.Message }
            }); ConvertTo-Json -InputObject $errors
        """)
        self.assertEqual(got, ["invalid_samples"] * 7)

    def test_completed_process_counts_binary_output_and_suppresses_content(self):
        got = self.child("import sys;sys.stdout.buffer.write(b'secret-fixture');sys.stderr.write('hidden-peer')",
                         output=14)
        self.assertEqual(got["result"]["status"], "completed")
        self.assertEqual(got["result"]["stdout_bytes"], 14)
        self.assertFalse(got["child_alive"])
        self.assertTrue(got["result"]["process_exited"])
        self.assertNotIn("secret-fixture", json.dumps(got))
        self.assertNotIn("hidden-peer", json.dumps(got))

    def test_throughput_uses_decimal_mbps_and_never_accepts_partial_body(self):
        got = self.run_ps("""
            @(
                (Get-Phase16ThroughputSummary -BodyBytes 1000000 -ExpectedBytes 1000000 -ElapsedMs 1000 -TransferCompleted $true),
                (Get-Phase16ThroughputSummary -BodyBytes 500000 -ExpectedBytes 1000000 -ElapsedMs 1000 -TransferCompleted $true),
                (Get-Phase16ThroughputSummary -BodyBytes 1000000 -ExpectedBytes 1000000 -ElapsedMs 1000 -TransferCompleted $false)
            ) | ConvertTo-Json
        """)
        self.assertEqual(got[0]["mbps"], 8)
        self.assertEqual(got[0]["readiness"], "MEASURED")
        for partial in got[1:]:
            self.assertIsNone(partial["mbps"])
            self.assertEqual(partial["readiness"], "INCOMPLETE")

    def test_invalid_transfer_and_deadline_never_start_a_child(self):
        got = self.run_ps("""
            $errors=@(foreach($duration in @(0,-1,[double]::PositiveInfinity)) {
                try { Get-Phase16ThroughputSummary -BodyBytes 1 -ExpectedBytes 1 -ElapsedMs $duration -TransferCompleted $true }
                catch { $_.Exception.Message }
            }); ConvertTo-Json -InputObject $errors
        """)
        self.assertEqual(got, ["invalid_transfer"] * 3)
        rejected = self.child("raise RuntimeError('must not execute')", timeout=500)
        self.assertEqual(rejected["result"]["status"], "invalid_request")
        self.assertIsNone(rejected["result"]["process_id"])

    def test_timeout_cancels_a_blocked_stdin_writer(self):
        got = self.child("import time;time.sleep(30)", timeout=1500,
                         input_body="[byte[]]::new(2097152)", max_input=2097152)
        self.assertEqual(got["result"]["status"], "timeout")
        self.assertFalse(got["child_alive"])
        self.assertIsNone(got["result"]["stdin_bytes"])

    def test_input_is_exact_binary_not_powershell_text_encoding(self):
        program = "import sys; x=sys.stdin.buffer.read();sys.exit(0 if x==bytes([0,255,10,13]) else 9)"
        got = self.child(program, input_body="0,255,10,13", max_input=4)
        self.assertEqual(got["result"]["status"], "completed")
        self.assertEqual(got["result"]["stdin_bytes"], 4)

    def test_input_limit_rejects_before_child_start(self):
        got = self.child("raise RuntimeError('must not execute')", input_body="1,2", max_input=1)
        self.assertEqual(got["result"]["status"], "invalid_request")
        self.assertIsNone(got["result"]["process_id"])

    def test_output_overflow_cancels_process_at_cap_plus_sentinel(self):
        got = self.child("import sys,time;sys.stdout.buffer.write(b'x'*65536);sys.stdout.flush();time.sleep(30)",
                         output=1024)
        self.assertEqual(got["result"]["status"], "output_limit")
        self.assertEqual(got["result"]["stdout_bytes"], 1025)
        self.assertFalse(got["child_alive"])

    def test_timeout_kills_silent_child_and_unblocks_pending_reads(self):
        started = time.monotonic()
        got = self.child("import time;time.sleep(30)", timeout=1500)
        self.assertEqual(got["result"]["status"], "timeout")
        self.assertTrue(got["result"]["process_exited"])
        self.assertFalse(got["child_alive"])
        self.assertLess(got["result"]["elapsed_ms"], 2500)
        self.assertLess(time.monotonic() - started, 6)

    def test_stderr_flood_does_not_deadlock_or_leak(self):
        got = self.child("import sys,time;sys.stderr.write('secret-fixture'*10000);sys.stderr.flush();time.sleep(30)")
        self.assertEqual(got["result"]["status"], "stderr_limit")
        self.assertFalse(got["child_alive"])
        self.assertNotIn("secret-fixture", json.dumps(got))

    def test_exit_failure_and_start_failure_are_normalized(self):
        got = self.child("import sys;sys.stderr.write('secret-fixture');sys.exit(7)")
        self.assertEqual(got["result"]["status"], "nonzero_exit")
        self.assertEqual(got["result"]["exit_code"], 7)
        missing = self.run_ps("Invoke-Phase16BoundedProcess -FilePath 'Z:/missing/secret-fixture.exe' "
                              "-ArgumentList @() -TimeoutMs 1500 -CleanupReserveMs 500 | ConvertTo-Json")
        self.assertEqual(missing["status"], "start_failed")
        self.assertIsNone(missing["process_id"])
        self.assertNotIn("secret-fixture", json.dumps(missing))

    def test_import_is_inert(self):
        result = subprocess.run([PWSH, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(HELPER)],
                                capture_output=True, timeout=8)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stderr, b"")


if __name__ == "__main__":
    unittest.main()
