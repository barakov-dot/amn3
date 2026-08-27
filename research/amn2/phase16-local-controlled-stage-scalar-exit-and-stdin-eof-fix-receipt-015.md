# Phase 16 — local scalar-exit fix and stdin/EOF diagnosis after package 015

## Result and authorization boundary

- Result: `local_tdd_pass_no_package_no_egress`.
- Code/test commit: `0e5b57a0a5b506bdea6f4b2672f6b67894f594df`.
- Approved starting commit: `07d15f09e3eb0b490c01cbbf5b05e20ba50ee0c8`.
- Bound SIGTERM receipt SHA256: `40348abd3b715cb565af5e7b2df87eeab9d3cfdb05ed39329a192342c87a0915`.
- Scope: fix controlled-stage scalar exit; diagnose stdin/frame/EOF; change transport only after local reproduction.
- Package 015 is immutable. Transaction 006 and its process-retirement approval remain consumed.
- No new package, package materialization, separate package verifier, Spain SSH, remote write, stage, install, rollback, client config, peer or issuance operation occurred.
- AWG2 configuration, runtime, freshness policy and issuance state were not changed or probed.
- The historical preflight PASS and process-retirement readback are not refreshed by this local work.
- Local regression PASS is not live stage acceptance.

## Exact local GO

Markdown underscore escaping was normalized for interpretation.

```text
/GO PHASE16 LOCAL_FIX_CONTROLLED_STAGE_SCALAR_EXIT_AND_DIAGNOSE_STDIN_EOF TDD FROM_COMMIT_07d15f09e3eb0b490c01cbbf5b05e20ba50ee0c8 SIGTERM_RECEIPT_SHA256_40348abd3b715cb565af5e7b2df87eeab9d3cfdb05ed39329a192342c87a0915 CHANGE_TRANSPORT_ONLY_IF_REPRODUCED PACKAGE_015_IMMUTABLE TRANSACTION_006_CONSUMED NO_NEW_PACKAGE NO_SPAIN_EGRESS NO_REMOTE_WRITE NO_STAGE NO_INSTALL NO_CONFIG NO_ISSUANCE AWG2_UNTOUCHED
```

## Finding 1 — scalar exit

The real runner entrypoint was exercised after a successful trust assertion, with only the external trust/package boundary replaced by local fixtures. The successful trust assertion returned the complete trust-contract object; the next package operation failed deliberately before any transport.

Before the fix, the entrypoint success stream contained the trust object followed by integer 64. Assigning that stream to the value passed to PowerShell `exit` produced process exit 0 despite the fixed STOP token. The new regression failed with `0 != 64`.

The fix captures the unused trust assertion return into `$null`. The assertion still executes, receives the expected host, and throws on rejection. No trust gate or failure artifact was removed. The same regression then returned process exit 64, empty stdout, the fixed STOP token, and a `package_validation/trust_validated` failure artifact.

## Finding 2 — reproduced local binary-stdin BOM defect

The real runner archive builder, request/header construction, bootstrap argument builder, binary writes, stdin close, outcome handling and entrypoint were exercised with a local Python child. The child imported the real coordinator and called only `_read_frame`; neither `execute_stage` nor coordinator `main` was called.

The fixture used 262144 deterministic non-secret payload bytes in an in-memory archive. It checked the received length and independent payload SHA256, not just a process exit. The synthetic result was explicitly marked `local_test_only` and existed only in the test temporary directory.

- Default local console input encoding: code page `866`, preamble length `0`; full framing/EOF passed.
- Windows PowerShell 5 / CLR `4.0.30319.42000`: `ProcessStartInfo.StandardInputEncoding` is unavailable.
- With the input encoding deliberately set to UTF-8 with a three-byte preamble, the real runner failed at `stdin_write`, last completed milestone `process_started`.
- This is the same failure-class/milestone pair recorded for transaction 006, reproduced without SSH.
- The exact historical cause of transaction 006 is still unconfirmed: its input prefix and detailed write exception were not captured. This local reproduction must not be reported as proof of that remote incident's root cause.

Microsoft's [Process reference source](https://raw.githubusercontent.com/microsoft/referencesource/main/System/services/monitoring/system/diagnosticts/Process.cs) shows that .NET Framework constructs the redirected stdin writer using the console input encoding and enables AutoFlush during process start. Its [StreamWriter reference source](https://raw.githubusercontent.com/microsoft/referencesource/main/mscorlib/system/io/streamwriter.cs) shows that this flush can emit the encoding preamble before later BaseStream writes. The [StandardInputEncoding documentation](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.standardinputencoding) documents the newer per-process encoding property; the local reflection check confirmed its absence here.

### Minimal producer-side correction

Immediately around `Process.Start`, the controlled-stage runner now saves the caller's input encoding, uses UTF-8 without a preamble, and restores the original encoding in `finally`. The process-start flag is set before restoration, preserving existing cleanup if a later operation fails.

The same UTF-8-preamble regression passed after the correction. Tests also prove restoration of code page and preamble on success and process-start failure.

Unchanged:

- SSH command/bootstrap, host checking, one connection attempt and clean child environment;
- coordinator/header length prefixes, byte hashes, binary BaseStream writes, explicit stdin close and EOF contract;
- rejection of truncation and extra bytes, including a trailing BOM;
- coordinator stage, rollback, outcome/failure schemas, milestones and AWG2 policies.

The frame parser intentionally reads one byte beyond the declared archive size to require EOF and reject trailing data. The local process test confirmed EOF delivery. Network backpressure, SSH disconnection and the historical full-size transfer were not live-tested, and no speculative timeout/retry or remote-parser change was made.

## Test record

| Run | Result |
| --- | --- |
| Existing expected-host baseline | 1 PASS |
| Scalar-exit focused RED | 1 expected FAIL, exit 0 instead of 64 |
| Scalar-exit focused GREEN | 1 PASS |
| Local binary frame/EOF characterization | 1 PASS |
| UTF-8-preamble focused RED | 1 expected FAIL, stdin_write / process_started |
| Transport/EOF focused GREEN | 4 PASS |
| One final targeted regression | 22 PASS, 0 failures/errors, 4.733 seconds |

The final regression included:

- `test_phase16_controlled_stage_runner_host_forwarding.py`: 5 tests;
- `test_phase16_controlled_stage_local_transport.py`: 4 tests;
- `test_phase16_controlled_stage_failure_locus.py`: 9 tests;
- `test_phase16_package_015_binding.py`: 4 tests.

Five malformed/trailing frame cases are subtests of the parser-preservation test. No full source/legacy tooling suite, independent reviewer, repeated final suite or package verifier was run.

Python executable: `C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`, with `-I -B`. PowerShell fixtures use `-NoProfile -NonInteractive -ExecutionPolicy Bypass`; only the test child's inherited PSModulePath is removed. No machine policy or dependency installation was changed.

The first baseline launcher selected pytest, which was unavailable before any test ran. The command was switched to the existing standard-library unittest tests. Local tool-wrapper quoting errors were corrected before shell dispatch; they did not launch tests, SSH or remote actions. The two test failures above were deliberate RED results against production behavior.

### Reproducible final suite

Run from the existing linked worktree with the child-only PSModulePath removal described above:

```python
import unittest; loader=unittest.TestLoader(); suite=unittest.TestSuite(); patterns=('test_phase16_controlled_stage_runner_host_forwarding.py','test_phase16_controlled_stage_local_transport.py','test_phase16_controlled_stage_failure_locus.py','test_phase16_package_015_binding.py'); [suite.addTests(loader.discover('tests', pattern=p)) for p in patterns]; result=unittest.TextTestRunner(verbosity=2).run(suite); raise SystemExit(0 if result.wasSuccessful() else 1)
```

## Changed-file checks and immutable evidence

Local checks UTC: `2026-08-27T19:50:19.4790144Z`.

- Exact changed code/test scope: four files.
- `git diff --check`: PASS.
- Short added-line secret scan: PASS.
- Inline changed-file review: complete; no independent reviewer/subagent used.
- Working tree was clean after the code commit.
- Frozen package-015 manifest, runner, coordinator and preflight helper hashes were rechecked.
- The bound SIGTERM receipt and local consumed-attempt marker remained unchanged.
- Package/AWG2 preservation tests passed. The mutable runner's intentional changes are behavior-tested; the frozen package-015 runner remains byte-equal to its original package-014 counterpart after package-ID normalization.

Changed artifact SHA256/bytes:

- `scripts/vps/phase16_controlled_stage_ssh_runner.ps1`: `fbdeda5f061eda91e8ca835e5b7c95b1233c4e6698ef497b33374ab353711635` / `21486`.
- `tests/test_phase16_controlled_stage_runner_host_forwarding.py`: `1b43ae2b996200549730aaae46197d2ab6f003f9ee70cdfb6e8c50c9a5b931e2` / `9262`.
- `tests/test_phase16_package_015_binding.py`: `b043e96bfc86ed1243425a372689c5e2dae31e4865fcb755ab8ea3d39c97d116` / `6938`.
- `tests/test_phase16_controlled_stage_local_transport.py`: `ef47c582d2f8c7cce3d6196c2229efdaa03cca09ddfbf05d75533151a642eb70` / `9527`.

Preserved package 015:

- Identity: `7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509`.
- Manifest: `f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74`.
- Frozen stage runner: `8eb9e2896a58c1cf70a493fcd8f00fd16764505ccdaaca940d78d6ae13a825e7`.
- Frozen coordinator: `2dccc21218ae6f6b7e28ac68f8c624aa8c9f55410638f7d9b7205a43660d2fc5`.
- Frozen preflight helper: `e5551706eb27ff8e5cb3299f7b57ad7f1f55b9d80bb88bcc7501c29f4ba2d983`.

The mutable source runner and immutable package-015 runner now intentionally differ. Do not deploy the frozen old package as though it contained these fixes, and do not substitute the mutable runner into an old checksum-bound approval.

## Closeout and next gate

The code/tests and this receipt are committed locally on `codex/phase16-awg3-family-3-1-spain-pilot-015`. The linked worktree is retained. Push was not attempted: informed approval to publish the accumulated history to the public origin is still pending.

Priority 0: this bounded local GO is complete. No further remote diagnostic or stage retry is authorized.

Priority 1: a separately approved local package-preparation step is required to update revision bindings and materialize/verify a new package. This run explicitly prohibited a new package; no package-016 claim, directory, manifest, identity or approval was created.

Priority 2: only after the new package passes its separate gate may new checksum-bound preflight and state-bound controlled-stage approvals be requested. No first pilot config before accepted stage and exact pilot approval.

## Phase 16 status

- ✅ Task 0 — baseline.
- ✅ Task 1 — immutable package 015 retained; local fixes committed but not packaged.
- ✅ Task 2 — historical preflight PASS; no fresh preflight.
- ▶️ Task 3 — local scalar-exit/BOM/EOF gate passed; new package and controlled stage still pending separate approvals.
- ⏳ Task 4 — first AWG3.1 operator config for ARM/Windows.
- ⏳ Task 4.5 — mandatory AWG2 ↔ AWG3.1 transport-quality A/B gate.
- ⏳ Task 5 — client acceptance.
- ⏳ Task 6 — closeout.

Safety state: Spain egress 0; remote writes/stage/install/config/issuance 0; no new package; AWG2 untouched. Recommended next-step profile from the plan: GPT-5.6 SOL / High. Actual active model/effort metadata is not asserted.
