# Phase 16 - local stdin-write early-exit diagnosis after package 016

## Result and scope

- Result: local_diagnostics_tdd_pass_no_package_no_egress.
- Approved baseline: e93096b72dfdd8d89a7a3306b3beacdd6f06d712.
- Code/test commit: 5d7a76b892b4c62e143ee4efc55dcbf413fabda7.
- Local check time: 2026-08-28T05:33:12Z.
- Package 016 is immutable; transaction 007 remains consumed.
- No new package, materialization or separate package verifier was run.
- Spain egress, remote writes, stage, install, config and issuance operations: zero.
- AWG2 and its freshness policy were neither changed nor probed.
- No subagent, live collector, preflight retry or stage retry was used.

## Exact local authorization

Markdown underscore escaping was normalized for interpretation.

~~~text
/GO PHASE16 LOCAL_DIAGNOSE_CONTROLLED_STAGE_STDIN_WRITE_EARLY_EXIT TDD FROM_COMMIT_e93096b72dfdd8d89a7a3306b3beacdd6f06d712 RECOVERY_RECEIPT_SHA256_50f5a29bd3e1d3608c90f02bb7de81798ac810d6fb8976562cf452f521b9da68 RECOVERY_STDOUT_SHA256_bc2549a54a7a2bd545f6ad2fedd80004365a4a9f9ee1c588f192cb170ee00eca RUNNER_FAILURE_SHA256_0f7d4168b0d5b90f3feb07fea48e6f5468f71784b5ef7de929594417faf9e50b PACKAGE_016_IMMUTABLE TRANSACTION_007_CONSUMED LOCAL_FAKE_SSH_ONLY ALLOWLISTED_WRITE_SEGMENT_EXCEPTION_AND_TRANSPORT_EXIT_CLASSES NO_RAW_STDOUT_STDERR CHANGE_TRANSPORT_ONLY_IF_REPRODUCED NO_NEW_PACKAGE NO_SPAIN_EGRESS NO_REMOTE_WRITE NO_STAGE NO_INSTALL NO_CONFIG NO_ISSUANCE AWG2_UNTOUCHED
~~~

The bound recovery receipt and runner-failure artifact were rechecked before edits.
Recovery stdout binding comes from the saved normalized recovery receipt; no new
remote observation was made. The previous readback of absent stage resources and
coordinator-name matches is historical, not refreshed by these tests.

## Reproduced finding

The real runner entrypoint, archive builder, bootstrap, binary writes and local
process plumbing were exercised. Before Process.Start, the executable is replaced
with local Python; ssh.exe is never launched. Trust and package inputs are local
synthetic fixtures. No real coordinator main or execute_stage runs in this harness.

The synthetic child consumes its bootstrap source and the complete frame header,
then exits without consuming the larger-than-pipe, 262144-byte payload archive.
Both zero and nonzero child exits cause the real archive write to fail.

- RED: the runner stops at stdin_write / process_started but records a null
  transport exit code instead of the observed synthetic exit 0 or 65.
- GREEN: the same scenarios record archive / io_error, the exact child exit code,
  and zero_exit or nonzero_exit. Both still return runner exit 64 and the fixed
  AMN2_PHASE16_CONTROLLED_STAGE_RUNNER_STOP token; no stage outcome is published.
- Only UTF-8 stream-text byte counts and SHA256 digests are retained. Synthetic
  stdout/stderr marker text is excluded from the failure artifact.

This proves an observability defect when stdin writing fails before normal
transport-result collection. It does NOT establish why transaction 007 exited:
the original failure document lacks the write segment, exception class and child
exit status. Network backpressure, real SSH termination and the full-size live
transfer were not tested. No new transport defect was demonstrated, so no
speculative transport correction was made.

## Minimal local change

The mutable runner emits failure schema v2 with closed enums for stdin write
segment, exception class, transport exit class and summary availability. Exception
messages and arbitrary runtime type names are not serialized.

On a write exception only, it observes process completion for at most 250 ms and
stream-task completion for at most another 250 ms. Missing observation remains
explicitly unavailable rather than being mistaken for observed empty output.
Observation cannot replace the original failure and performs no retry, restart,
stdin close or signal. Existing local-child cleanup remains unchanged.

SSH arguments/bootstrap, trust checks, request/rollback binding, framing bytes,
write order, EOF handling, transport timeout and remote coordinator are unchanged.
No remote failure schema, rollback behavior or AWG2 policy was changed.

The package-016 historical runner-hash test now checks the frozen packaged runner,
not mutable source. Its exact expected hash was retained; this prevents local
diagnostic edits from rewriting the historical package binding.

## Test record

| Run | Result |
| --- | --- |
| Focused RED | 1 test, 2 expected failed subtests; null != 0 and null != 65 |
| Focused GREEN | 1 test, both exit-code subtests passed, 3.125 seconds |
| One final targeted regression | 26 passed, 0 failures/errors, 11.867 seconds |

Final modules:

- test_phase16_controlled_stage_local_transport: 5 tests.
- test_phase16_controlled_stage_runner_host_forwarding: 6 tests.
- test_phase16_controlled_stage_failure_locus: 9 tests.
- test_phase16_package_016_binding: 6 tests.

The suite preserves successful binary framing/EOF, BOM handling, scalar exit,
host forwarding, fixed STOP output, allowlist rejection, package bindings and
rollback contracts. Coordinator tests replace OS commands and remote paths with
local fixtures. No SSH, Docker or systemctl command was executed.

Runtime: bundled Python 3.12.13, -B -m unittest -v, Windows PowerShell 5 fixtures
with -NoProfile -NonInteractive -ExecutionPolicy Bypass. PSModulePath removal is
process-local and restored after the final test command; no machine/user policy
or dependency installation changed.

No full legacy suite or repeated final regression was run. Tool-wrapper/patch
construction errors were corrected locally; they
did not execute live operations. The only test failures were the intended RED.

## Preservation and next boundary

- git diff --check and staged diff --check passed.
- Frozen package-016 manifest SHA256: e21c958573b093f6af7bea009cf5fbd42fda621b5b18609572ab32b8aa1ae9bc.
- Frozen stage-runner SHA256: 6364d652181cd6f522dbecd25e2c4b36e8c1d06736cb67a2e6a3e4894da7dd77.
- Both hashes were rechecked unchanged. Elevated read-only Git inspection showed no packaging changes.
- No ACL was changed; sandbox deny-read warnings were not treated as file deletions.
- Current source differs intentionally from frozen package 016. Do not substitute it into an old approval.
- Push was not attempted: informed approval for publication to the public origin remains pending.

This local GO is complete. Live stage is still blocked; transaction 007 is consumed.
A new immutable package needs separate local authorization, followed by new preflight
and controlled-stage approvals. No client config or general issuance is authorized.

Phase status: Task 0 and Task 1 complete; Task 2 historical PASS, not refreshed;
Task 3 live STOP, local diagnosis complete; Tasks 4, 4.5, 5 and 6 pending.
Task 4.5 remains the mandatory AWG2 versus AWG3.1 transport-quality A/B gate.
