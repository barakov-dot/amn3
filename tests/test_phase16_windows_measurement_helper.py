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


# Only Ping is replaced. Tasks/tokens/timers and adapter state handling are real.
# Never constructs a real Ping or opens a socket.
ICMP_FAKE = """
$script:pingCalls=0; $script:pingCreated=0; $script:pingDisposed=0
$script:pingMode='reply'; $script:pingStatus=[Net.NetworkInformation.IPStatus]::Success
$script:pingRtt=12; $script:binding=$null; $script:lastToken=$null
function New-Phase16PingClient {
    $script:pingCreated++
    $client=[pscustomobject]@{}
    $client | Add-Member ScriptMethod SendPingAsync {
        param($ip,$timeout,$buffer,$options,$token)
        $script:pingCalls++
        $script:lastToken=$token
        $script:binding=@{literal_ipv4=($ip -is [Net.IPAddress] -and
          $ip.AddressFamily -eq [Net.Sockets.AddressFamily]::InterNetwork);
          timeout_ms=$timeout.TotalMilliseconds; payload_bytes=$buffer.Length;
          binary=($buffer -is [byte[]]); df=$options.DontFragment; ttl=$options.Ttl;
          cancelable=$token.CanBeCanceled}
        switch($script:pingMode) {
            'delay' { return [Threading.Tasks.Task]::Delay(30000,$token) }
            'stuck' { return [Threading.Tasks.TaskCompletionSource[object]]::new().Task }
            'throw' { throw 'secret-fixture' }
            'fault' { return [Threading.Tasks.Task]::FromException[object]([Exception]::new('secret-fixture')) }
            'native_timeout' {
                # Simulate send/return overhead in addition to the requested wait.
                [Threading.Thread]::Sleep([int]$timeout.TotalMilliseconds + 10)
                $script:pingStatus=[Net.NetworkInformation.IPStatus]::TimedOut
            }
        }
        return [Threading.Tasks.Task]::FromResult[object]([pscustomobject]@{
          Status=$script:pingStatus; RoundtripTime=$script:pingRtt;
          Address='secret-fixture'; Buffer=[byte[]](1,2); Options=$options})
    }
    $client | Add-Member ScriptMethod Dispose { $script:pingDisposed++ }
    return $client
}
"""


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


    def http_process(self, raw, exit_code=0, suffix=""):
        program = (f"import sys,time;sys.stdout.buffer.write({raw!r});"
                   f"sys.stdout.flush();{suffix}sys.exit({exit_code})")
        return self.run_ps(
            "Invoke-Phase16BoundedProcess "
            f"-FilePath {literal(sys.executable)} "
            f"-ArgumentList @('-I','-B','-c',{literal(program)}) "
            "-MaxOutputBytes 4096 -TimeoutMs 2000 -CurlMetadata $true | ConvertTo-Json -Depth 5"
        )

    def test_http_metadata_is_numeric_bounded_and_never_raw(self):
        # Catch permissive parsing, locale decimals and accidental raw output.
        got = self.http_process(b"p16v1\t200\t1000000\t0\t1.250000\t0\t0\t0\n")
        self.assertEqual(got["status"], "completed")
        self.assertIn("http_metadata", got, "bounded HTTP metadata parser missing")
        self.assertEqual(got["http_metadata"], dict(response_code=200, size_download=1000000,
                         size_upload=0, time_total=1.25, ssl_verify_result=0,
                         num_redirects=0, proxy_used=0))
        self.assertFalse(got["raw_output_retained"])

    def test_http_metadata_rejects_injection_nonfinite_duplicates_and_overflow(self):
        valid = b"p16v1\t200\t10\t0\t1.000000\t0\t0\t0\n"
        for raw in (b"secret-fixture", valid + valid, valid.replace(b"1.000000", b"NaN"),
                    valid.replace(b"1.000000", b"1,000000"),
                    valid.replace(b"\t10\t", b"\t999999999999999999999\t"),
                    valid + b"\xff", valid.replace(b"\t200\t", b"\t0200\t")):
            with self.subTest(raw=raw):
                got = self.http_process(raw)
                self.assertEqual(got["status"], "metadata_invalid")
                self.assertIsNone(got["http_metadata"])
                self.assertNotIn("secret-fixture", json.dumps(got))
        got = self.http_process(b"x" * 10000)
        self.assertEqual(got["status"], "output_limit")
        self.assertEqual(got["stdout_bytes"], 4097)
        self.assertIsNone(got["http_metadata"])

    def test_http_error_and_timeout_cannot_publish_success_metadata(self):
        valid = b"p16v1\t200\t10\t0\t1.000000\t0\t0\t0\n"
        for exit_code, suffix, status in [(63, "", "nonzero_exit"),
                                          (0, "time.sleep(30);", "timeout")]:
            got = self.http_process(valid, exit_code, suffix)
            self.assertEqual(got["status"], status)
            self.assertIsNone(got["http_metadata"])
            self.assertTrue(got["process_exited"])

    def test_http_request_enforces_caps_and_removes_implicit_curl_behavior(self):
        got = self.run_ps("""
            @(
              (New-Phase16HttpRequest -Endpoint 'https://example.invalid/down?bytes=1000000' -Direction download -ExpectedBytes 1000000),
              (New-Phase16HttpRequest -Endpoint 'https://example.invalid/up' -Direction upload -ExpectedBytes 4 -InputBytes ([byte[]](0,255,10,13)))
            ) | ConvertTo-Json -Depth 5
        """)
        for req in got:
            args = req["arguments"]
            self.assertEqual(args[0], "-q")
            for flag, value in (("--retry", "0"), ("--max-redirs", "0"), ("--proxy", ""),
                                ("--noproxy", "*"), ("--proto", "=https")):
                self.assertEqual(args[args.index(flag) + 1], value)
            self.assertIn("--out-null", args)
            self.assertIn("--globoff", args)
            self.assertNotIn("--location", args)
            self.assertNotIn("--insecure", args)
            self.assertNotIn("--compressed", args)
            self.assertEqual(args.count("--url"), 1)
            self.assertEqual(args[args.index("--max-time") + 1], "4.5")
            self.assertEqual(args[args.index("--write-out") + 1],
                             "p16v1\t%{response_code}\t%{size_download}\t%{size_upload}\t%{time_total}"
                             "\t%{ssl_verify_result}\t%{num_redirects}\t%{proxy_used}\n")
        self.assertEqual(got[0]["arguments"][got[0]["arguments"].index("--request") + 1], "GET")
        self.assertEqual(got[1]["arguments"][got[1]["arguments"].index("--request") + 1], "POST")
        self.assertIn("Content-Type: application/octet-stream", got[1]["arguments"])
        self.assertEqual(got[0]["arguments"][got[0]["arguments"].index("--max-filesize") + 1], "1000000")
        self.assertEqual(got[1]["arguments"][got[1]["arguments"].index("--max-filesize") + 1], "65536")
        self.assertIn("@-", got[1]["arguments"])
        self.assertEqual(got[1]["input_bytes"], [0, 255, 10, 13])

    def test_http_invalid_request_is_rejected_without_process_start(self):
        got = self.run_ps("""
            $cases=@(
              @{Endpoint='http://example.invalid/'}, @{Endpoint='https://u:p@example.invalid/'},
              @{Endpoint='https://example.invalid/#fragment'}, @{ExpectedBytes=0},
              @{ExpectedBytes=8388609}, @{ExpectedBytes=1.5}, @{TimeoutMs=500},
              @{Direction='upload';ExpectedBytes=2;InputBytes=[byte[]](1)},
              @{Direction='download';InputBytes=[byte[]](1)}, @{ResponseMaxBytes=65537}
            ); @(foreach($c in $cases) {
              $p=@{Endpoint='https://example.invalid/';Direction='download';ExpectedBytes=10}
              foreach($key in $c.Keys) { $p[$key]=$c[$key] }
              Invoke-Phase16HttpMeasurement @p -CurlPath 'Z:/missing/secret-fixture.exe'
            }) | ConvertTo-Json -Depth 5
        """)
        self.assertEqual(len(got), 10)
        for row in got:
            self.assertEqual(row["status"], "invalid_request")
            self.assertIsNone(row["mbps"])
            self.assertNotIn("secret-fixture", json.dumps(row))

    def test_http_adapter_checks_binary_body_without_network(self):
        # Only substitute the external executable boundary. The real pipe runner,
        # request builder, parser and summary remain active; no curl is executed.
        program = ("import sys;body=sys.stdin.buffer.read();"
                   "ok=body==bytes([0,255,10,13]);"
                   "sys.stdout.write('p16v1\\t200\\t2\\t4\\t0.001000\\t0\\t0\\t0\\n');"
                   "sys.exit(0 if ok else 9)")
        got = self.run_ps(
            "$script:realProcess=${function:Invoke-Phase16BoundedProcess}; "
            "function Invoke-Phase16BoundedProcess { param($FilePath,$ArgumentList,$InputBytes,"
            "$MaxInputBytes,$MaxOutputBytes,$TimeoutMs,$CleanupReserveMs,$CurlMetadata); "
            f"& $script:realProcess -FilePath {literal(sys.executable)} "
            f"-ArgumentList @('-I','-B','-c',{literal(program)}) -InputBytes $InputBytes "
            "-MaxInputBytes $MaxInputBytes -MaxOutputBytes $MaxOutputBytes -TimeoutMs $TimeoutMs "
            "-CleanupReserveMs $CleanupReserveMs -CurlMetadata $CurlMetadata }; "
            "Invoke-Phase16HttpMeasurement -CurlPath 'C:/fake/curl.exe' "
            "-Endpoint 'https://example.invalid/up' -Direction upload -ExpectedBytes 4 "
            "-InputBytes ([byte[]](0,255,10,13)) | ConvertTo-Json -Depth 5"
        )
        self.assertEqual(got["status"], "measured")
        self.assertEqual(got["payload_bytes"], 4)
        self.assertGreater(got["duration_ms"], 0)
        self.assertAlmostEqual(got["mbps"], 32 / got["duration_ms"] / 1000)
        self.assertNotIn("example.invalid", json.dumps(got))

    def test_http_summary_rejects_partial_http_tls_proxy_and_cleanup_failures(self):
        got = self.run_ps("""
            $cases=@(
              @{}, @{response_code=302}, @{response_code=500}, @{ssl_verify_result=60},
              @{size_download=9}, @{size_download=11}, @{size_upload=1},
              @{num_redirects=1}, @{proxy_used=1}, @{time_total=0}, @{time_total=9}
            ); $results=@(foreach($c in $cases) {
              $m=@{response_code=200;size_download=10;size_upload=0;time_total=0.1;
                   ssl_verify_result=0;num_redirects=0;proxy_used=0}
              foreach($key in $c.Keys) { $m[$key]=$c[$key] }
              $p=@{status='completed';process_exited=$true;exit_code=0;deadline_exceeded=$false;
                   elapsed_ms=200;http_metadata=$m;stdin_bytes=0}
              Get-Phase16HttpSummary -ProcessResult $p -Direction download -ExpectedBytes 10 -ResponseMaxBytes 65536
            });
            foreach($bad in @(@{status='timeout'},@{process_exited=$false},@{deadline_exceeded=$true},@{exit_code=1})) {
              $p=@{status='completed';process_exited=$true;exit_code=0;deadline_exceeded=$false;
                   elapsed_ms=200;http_metadata=@{response_code=200;size_download=10;size_upload=0;
                   time_total=0.1;ssl_verify_result=0;num_redirects=0;proxy_used=0};stdin_bytes=0}
              foreach($key in $bad.Keys) { $p[$key]=$bad[$key] }
              $results+=Get-Phase16HttpSummary -ProcessResult $p -Direction download -ExpectedBytes 10 -ResponseMaxBytes 65536
            }; ConvertTo-Json -InputObject $results -Depth 5
        """)
        self.assertEqual(got[0]["status"], "measured")
        self.assertEqual(got[0]["mbps"], 0.0004)
        self.assertEqual(got[1]["response_code"], 302)
        self.assertEqual(got[2]["response_code"], 500)
        self.assertEqual(got[3]["ssl_verify_result"], 60)
        for row in got[1:]:
            self.assertEqual(row["readiness"], "INCOMPLETE")
            self.assertIsNone(row["mbps"])

    def test_http_child_cannot_inherit_tls_keylog_file_setting(self):
        program = "import os,sys;sys.exit(9 if 'SSLKEYLOGFILE' in os.environ else 0)"
        got = self.run_ps(
            "$env:SSLKEYLOGFILE='secret-fixture-never-written'; "
            "Invoke-Phase16BoundedProcess "
            f"-FilePath {literal(sys.executable)} "
            f"-ArgumentList @('-I','-B','-c',{literal(program)}) "
            "-MaxOutputBytes 4096 -CurlMetadata $true | ConvertTo-Json"
        )
        self.assertEqual(got["exit_code"], 0)
        self.assertEqual(got["status"], "metadata_invalid")  # No numeric record.
        self.assertNotIn("secret-fixture", json.dumps(got))

    def test_http_upload_unknown_stdin_and_oversized_ack_are_incomplete(self):
        got = self.run_ps("""
            $results=@(foreach($change in @(@{},@{stdin_bytes=$null},@{size_download=65537},@{size_upload=3})) {
              $m=@{response_code=200;size_download=0;size_upload=4;time_total=0.1;
                   ssl_verify_result=0;num_redirects=0;proxy_used=0}
              $p=@{status='completed';process_exited=$true;exit_code=0;deadline_exceeded=$false;
                   elapsed_ms=200;http_metadata=$m;stdin_bytes=4}
              foreach($key in $change.Keys) {
                if($key -eq 'stdin_bytes') { $p[$key]=$change[$key] } else { $m[$key]=$change[$key] }
              }
              Get-Phase16HttpSummary -ProcessResult $p -Direction upload -ExpectedBytes 4
            }); ConvertTo-Json -InputObject $results
        """)
        self.assertEqual(got[0]["status"], "measured")
        for row in got[1:]:
            self.assertEqual(row["readiness"], "INCOMPLETE")
            self.assertIsNone(row["mbps"])


    def icmp(self, setup="", arguments=""):
        return self.run_ps(
            ICMP_FAKE + setup +
            "; $r=Invoke-Phase16IcmpSample -Address '198.51.100.8' -Sequence 1 " + arguments +
            "; @{result=$r;calls=$script:pingCalls;created=$script:pingCreated;"
            "disposed=$script:pingDisposed;binding=$script:binding;"
            "token_canceled=($null -ne $script:lastToken -and $script:lastToken.IsCancellationRequested)}"
            " | ConvertTo-Json -Depth 5"
        )

    def test_icmp_success_preserves_rtt_and_binds_literal_ipv4_df_and_cap(self):
        for payload, df in [(32, False), (1252, True)]:
            df_ps = "$true" if df else "$false"
            got = self.icmp(arguments=f"-PayloadBytes {payload} -DontFragment {df_ps}")
            self.assertEqual(got["result"]["sample"], dict(sequence=1, status="success", rtt_ms=12))
            self.assertEqual(got["calls"], 1)
            self.assertEqual(got["disposed"], 1)
            self.assertTrue(got["result"]["cleanup_confirmed"])
            self.assertEqual(got["binding"], dict(literal_ipv4=True, timeout_ms=800,
                             payload_bytes=payload, binary=True, df=df, ttl=64, cancelable=True))
            self.assertNotIn("198.51.100.8", json.dumps(got))
            self.assertNotIn("secret-fixture", json.dumps(got))

    def test_icmp_reply_failures_do_not_become_success_or_local_error_loss(self):
        for status, want, outcome in [
            ("TimedOut", "timeout", "timeout"),
            ("DestinationHostUnreachable", "send_error", "icmp_error"),
            ("PacketTooBig", "send_error", "packet_too_big"),
        ]:
            got = self.icmp(f"$script:pingStatus=[Net.NetworkInformation.IPStatus]::{status}")
            self.assertEqual(got["result"]["sample"], dict(sequence=1, status=want, rtt_ms=None))
            self.assertEqual(got["result"]["outcome"], outcome)
            self.assertEqual(got["calls"], 1)
            self.assertTrue(got["result"]["cleanup_confirmed"])

    def test_icmp_native_timeout_has_return_margin_before_external_cancel(self):
        got = self.icmp("$script:pingMode='native_timeout'")
        self.assertEqual(got["result"]["sample"]["status"], "timeout")
        self.assertEqual(got["result"]["outcome"], "timeout")
        self.assertEqual(got["result"]["reply_timeout_ms"], 800)
        self.assertTrue(got["result"]["cleanup_confirmed"])

    def test_icmp_invalid_arguments_never_create_ping(self):
        got = self.run_ps(ICMP_FAKE + """
            $cases=@(@{Address='hostname.invalid'},@{Address='::1'},@{Address='127.1'},
              @{Address='198.51.100.999'},@{Address='198.51.100.08'},@{Sequence=0},
              @{PayloadBytes=1253},@{PayloadBytes=-1},@{TimeoutMs=1001},
              @{TimeoutMs=100},@{DontFragment='true'},@{CancellationToken='bad'})
            $results=@(foreach($c in $cases) {
              $p=@{Address='198.51.100.8';Sequence=1}
              foreach($key in $c.Keys) { $p[$key]=$c[$key] }
              Invoke-Phase16IcmpSample @p
            }); @{results=$results;created=$script:pingCreated} | ConvertTo-Json -Depth 5
        """)
        self.assertEqual(got["created"], 0)
        for row in got["results"]:
            self.assertEqual(row["outcome"], "invalid_request")
            self.assertIsNone(row["sample"])

    def test_icmp_caller_cancel_before_start_and_during_wait_is_not_timeout(self):
        early = self.icmp("$c=[Threading.CancellationTokenSource]::new();$c.Cancel()",
                          "-CancellationToken $c.Token")
        self.assertEqual(early["created"], 0)
        self.assertEqual(early["result"]["sample"]["status"], "canceled")
        during = self.icmp(
            "$script:pingMode='delay';$c=[Threading.CancellationTokenSource]::new();$c.CancelAfter(50)",
            "-CancellationToken $c.Token",
        )
        self.assertEqual(during["result"]["sample"]["status"], "canceled")
        self.assertTrue(during["result"]["cleanup_confirmed"])
        self.assertEqual(during["disposed"], 1)
        self.assertLess(during["result"]["elapsed_ms"], 1000)

    def test_icmp_work_deadline_cancels_and_unconfirmed_cleanup_blocks_sample(self):
        got = self.icmp("$script:pingMode='delay'", "-TimeoutMs 300")
        self.assertEqual(got["result"]["sample"]["status"], "canceled")
        self.assertEqual(got["result"]["outcome"], "deadline_canceled")
        self.assertTrue(got["token_canceled"])
        self.assertTrue(got["result"]["cleanup_confirmed"])
        stuck = self.icmp("$script:pingMode='stuck'", "-TimeoutMs 300")
        self.assertEqual(stuck["result"]["outcome"], "cleanup_unconfirmed")
        self.assertFalse(stuck["result"]["cleanup_confirmed"])
        self.assertNotEqual(stuck["result"]["sample"]["status"], "success")
        self.assertLess(stuck["result"]["elapsed_ms"], 1000)

    def test_icmp_fault_and_bad_rtt_are_normalized_without_raw_exception(self):
        for setup in ("$script:pingMode='throw'", "$script:pingMode='fault'",
                      "$script:pingRtt=-1", "$script:pingRtt=[double]::NaN", "$script:pingRtt=1001"):
            got = self.icmp(setup)
            self.assertEqual(got["result"]["sample"]["status"], "send_error")
            self.assertIsNone(got["result"]["sample"]["rtt_ms"])
            self.assertEqual(got["disposed"], 1)
            self.assertNotIn("secret-fixture", json.dumps(got))

    def test_icmp_sample_feeds_existing_summary_without_automatic_path_validation(self):
        got = self.run_ps(ICMP_FAKE + """
            $r=Invoke-Phase16IcmpSample -Address '198.51.100.8' -Sequence 1
            Get-Phase16RttSummary -Samples @($r.sample) | ConvertTo-Json
        """)
        self.assertEqual(got["success_count"], 1)
        self.assertEqual(got["median_ms"], 12)
        self.assertEqual(got["readiness"], "INCOMPLETE")
        self.assertIsNone(got["loss_percent"])


if __name__ == "__main__":
    unittest.main()
