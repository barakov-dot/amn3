# Phase 16 package 015 local STOP receipt

- Recorded: `2026-08-27T04:27:03Z`
- Decision: `STOP_SECOND_UNEXPECTED_TEST_FAILURE`
- Worktree: `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\phase16-004`
- Branch: `codex/phase16-awg3-family-3-1-spain-pilot-015`
- HEAD and approved starting commit: `b255bf3d48ea491ea9067be3e4320b5dcb5398c8`
- Intended package: `phase16-awg3-family-3-1-spain-pilot-20260824-015`
- Package 015 directory: absent
- Materialization count: `0/1`
- Separate verifier count: `0/1`
- Local commits in this run: `0`
- Implementation and test changes: retained, uncommitted

## Approved evidence preserved

- Recovery receipt SHA-256: `7c10849f3b6d2a1544c407e9c01c6c1757ae9ee4d1b278b703add65703b97936`
- Recovery normalized stdout SHA-256: `dfc4e42185c440d24bb9e8f93396fa71998669ab891a1bbf55a87dacbe79832c`
- Recovery diagnostic source SHA-256: `dd502db08c30f1b7378edfd4aa13a5f4fdd3296ceec9a6b9daba4b4f2dc61fa8`
- Package 014 identity: `d741006c3b0d788700020a93ac02a3bb5f35a1ec89d9497902ef7c8ac5726f19`
- Package 014 manifest SHA-256: `844499afb51ca4cd5eacc8a395c003aabba39ffd02723ae4e95e4d28105b6cb1`
- Immutable package 014 check: all `171` manifest entries and exact `172`-file inventory passed
- Transaction `phase16-spain-stage-20260827-004`: consumed; no retry

## Local test evidence and stop rule

1. The first RED run exposed missing feature contracts plus an unexpected
   Windows test-fixture issue: text-mode `os.open` writes expanded every LF to
   CRLF. The fixture coordinator changed from `23728` to `24329` bytes, solely
   by LF expansion. The one bounded correction was confined to the test OS
   boundary, which now emulates POSIX binary writes. Production transport was
   not changed for this issue.
2. Corrected RED: `13` methods; `28` expected missing-helper/artifact subtest
   errors and `1` expected missing-checkpoint failure. Five existing/fixed
   envelope methods passed.
3. Functional GREEN: `13 passed in 2.142s`. This exercises the real coordinator
   and temporary files with simulated OS commands. It covers consumed-is-entry
   semantics, application/runtime milestones, post-runtime snapshot/equality,
   outcome and milestone publication, rollback errors, no-raw failure artifacts,
   successful stage ordering and transaction-reuse rejection.
4. Binding RED: `1` expected revision-014 versus revision-015 mismatch.
5. Binding GREEN attempt: `3 passed, 1 failed in 0.466s`. The new PowerShell
   test invocation omitted `-ExecutionPolicy Bypass`, unlike the established
   runner test harness. Windows rejected dot-sourcing the local runner before
   rollback-scope comparison. No runner main or SSH process was invoked.
6. This is the second unexpected test failure in the run. The user's stop rule
   applies. The invocation has not been corrected or rerun.

Failed test: `Package015BindingTest.test_python_and_powershell_bind_the_same_exact_rollback_scope`

Test source: `tests/test_phase16_package_015_binding.py`

Test source SHA-256: `47d0141a5af70971e2d1288730f34bdd9a7915b5ef0da7ba36339722d18120b2`

`git diff --check` passed before recording this receipt. No final targeted
regression, package materialization, verifier or readiness claim was made.

## Retained implementation and next boundary

The working tree contains the additive coordinator milestone/failure-locus
implementation, its behavioral tests, revision-015 bindings, and updated local
plan/source evidence. The application source, AWG2 policy, preflight behavior,
runtime-stage behavior and fixed runner outcome/STOP contract are unchanged
apart from package identity bindings. Rollback still targets only the original
approved resources and preserves backup/audit data; attempted cleanup is not
misreported as a clean-resource readback.

A new local `/GO` is required to correct only the new test harness invocation,
perform one targeted regression, finish local commits and then use the still
unused one materialization and one separate verifier. No machine/user-wide
PowerShell execution-policy change is needed or authorized. Do not modify
package 014, retry transaction 004 or discard the existing uncommitted work.

Spain egress, SSH, remote write, rollback, stage, install, config/peer issuance,
global issuance and AWG2 operations performed by this local run: `0`.
