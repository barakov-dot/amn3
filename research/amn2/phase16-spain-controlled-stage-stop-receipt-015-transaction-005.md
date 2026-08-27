# Phase 16 — package 015, transaction 005: local prelaunch STOP

Recorded UTC: `2026-08-27T17:49:42.9420638Z`.

## Decision

- Gate decision: `local_prelaunch_stop_no_ssh_no_remote_stage`.
- Controlled-stage runner invocation: `1/1`; exit: `64`.
- Failure class: `trust_validation`; last completed milestone: `arguments_validated`.
- SSH process creation / remote coordinator / application stage / AWG3.1 runtime stage: `0/0/0/0`.
- Remote write, install, client config, peer creation and issuance: `0`.
- AWG2 was not modified by this attempt.
- Rollback was not required or invoked: execution stopped before SSH creation.
- Transaction 005 was not created remotely by this attempt. Its local runner-failure artifact consumes the local attempt; do not reuse or overwrite it.
- No automatic or blind stage/preflight retry was performed.

This is a STOP receipt, not proof of completed server stage or current remote health.

## Exact approved bindings

- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-015`.
- Package identity: `7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509`.
- Manifest SHA256: `f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74`.
- Approved state SHA256: `e7b83199c3cef351964746a9f3a60ab665f632f8b4c4a5f8b0ad58494db44c92`.
- Rollback scope SHA256: `15d6fe8bd131a56bf4d5a6545d4cd7ecf22a785f1da916de6410cd9d9e5167b3`.
- Normalized approval SHA256: `03c4c46759e26072b9962e679ff6b13e4cf8e9c160d4fc4410fbaa4aef7d53c8`.
- Transaction: `phase16-spain-stage-20260827-005`.
- Target: `138.124.181.246`.
- Packaged stage runner SHA256: `8eb9e2896a58c1cf70a493fcd8f00fd16764505ccdaaca940d78d6ae13a825e7`.
- Imported preflight runner SHA256: `e5551706eb27ff8e5cb3299f7b57ad7f1f55b9d80bb88bcc7501c29f4ba2d983`.
- Coordinator SHA256: `2dccc21218ae6f6b7e28ac68f8c624aa8c9f55410638f7d9b7205a43660d2fc5`.
- Preflight PASS receipt SHA256: `2fe10b8d97abeca35b29ec04680a5bfbb078383e416748cb37bd51faecf1dbc4`.
- Pre-run HEAD: `6ed8fcbb030b98d52d6f57a26ce0615b9f28ddad`.
- Branch: `codex/phase16-awg3-family-3-1-spain-pilot-015`.

The approved state remains the immutable claim-027 preflight outcome. Its observation window was 2026-08-27 19:58:05–19:58:21 Europe/Moscow. This attempt collected no new remote state.

## Prelaunch and runner evidence

The separate local gate passed in Windows PowerShell 5: exact manifest/identity, eight stage-related asset hashes, inventory 172 files, state, rollback scope, approval and SSH trust. Transaction-005 local outcome/failure paths were absent.

The gate used PowerShell's native call operator. Its process exited 0; a single valid result JSON was returned together with module-preparation CLIXML progress. The orchestration JSON read initially rejected the combined text; the already returned result JSON was retained separately, without rerunning the gate.

The actual runner was then launched once using a .NET `ProcessStartInfo` child:

- Started: `2026-08-27T17:38:14.5064995Z`.
- Ended: `2026-08-27T17:38:14.9671663Z`.
- Moscow window: `2026-08-27 20:38:14`.
- Elapsed seconds: `0.461`.
- Outer timeout: `false`.
- Actual runner process exit: `64`.
- Fixed stderr token: `AMN2_PHASE16_CONTROLLED_STAGE_RUNNER_STOP`.
- Outer stdout bytes/SHA256: `0` / `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Outer stderr bytes/SHA256: `43` / `9e650e4049eb870274ee7321d57cca26007736a1136ff2860ba43c9cd89aeb48`.
- Local stage outcome: absent.
- Local runner-failure artifact: present.
- Raw stdout/stderr was not persisted.

The outer orchestration command's successful completion is not treated as a successful stage. The child exit and canonical failure artifact are authoritative.

## Canonical runner-failure artifact

Path: `C:\ProgramData\AMN2\phase16\controlled-stage\outcomes\phase16-spain-stage-20260827-005.json.runner-failure.json`.

- SHA256: `9636bece65d7f37d1702ae2e62fae7769dd730e74a852c5534016eb95bec466f`.
- Bytes: `540`.
- Canonical JSON and exact field set: pass.
- Schema: `amn2.phase16.controlled-stage-runner-failure.v1`.
- Result: `runner_stop`.
- Failure class: `trust_validation`.
- Last completed milestone: `arguments_validated`.
- Transport exit code: `null`.
- Transport stdout bytes: `0`; stderr bytes: `0`.
- Both transport stream SHA256 values: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Raw output persisted: `false`.

The packaged runner performs trust validation before package loading, archive construction and `process.Start()`. This milestone therefore establishes a local prelaunch stop, not a remote rollback or stage failure.

## Local cause investigation

Only read-only local diagnostics were performed after STOP; no stage entrypoint or SSH was invoked again.

1. A temporary trust-only probe was launched with the same Windows PowerShell 5 `-File` and `ProcessStartInfo` envelope. The probe's collection wrapper rejected the missing JSON envelope. It did not preserve raw output.
2. A second local probe invocation retained only hashes/lengths and an allowlisted error token. It returned exit 1, empty stdout, and `CommandNotFoundException`; the trust assertion had not produced a result.
3. The same command-availability script was compared through the native call operator and direct `ProcessStartInfo`. Both children were PowerShell 5; their parent was PowerShell 7:
   - Native call: `Get-Acl` and `Get-FileHash` available.
   - Direct process: both unavailable, class `command_not_found`.
4. A single-variable control reran the unchanged trust-only probe with only the child's inherited `PSModulePath` removed. Windows PowerShell 5 then initialized its own module context; the full real trust assertion passed.

Probe source SHA256/bytes: `178a2af60858ad12baff068d8af20576ff9cf3740d94fce63c466bfc02ebcfc4` / `2515`.

Second probe stderr SHA256/bytes: `071e5de17a6b8baef486e026f6754482803fff6f4c196eece383738fee9290ab` / `803`. No raw error text was retained.

Single-variable control:

- Changed variable: `child_PSModulePath_only_removed`.
- Parent environment changed: `false`; machine policy changed: `false`.
- Probe exit: `0`; normalized trust result: `pass`.
- Host and stage expected host: exact.
- Trust run-id and host-key script variables: present.
- Stdout SHA256/bytes: `cfe0f3946bf87d4ba4b1ecdda7488952b09b551e3a1154ed205a21e3553eb6a4` / `426`.
- Stderr bytes: `0`.
- Stage entrypoint invoked / remote egress: `false/false`.

Conclusion: the local launch envelope inherited an incompatible PowerShell-7 module-search context. The observed command-availability differential and unchanged-probe single-variable control explain the prelaunch trust stop. This is not evidence of an invalid SSH key, changed host key or a server-side problem.

The package, stage scripts, trust bundle, ACLs and machine execution policy were not changed. No source-code fix, new package, materialization, regression suite or separate package verifier was performed.

The temporary probe file was checksum-verified and removed after collection. Normalized evidence and the authoritative runner-failure artifact are retained.

## Final local readback and next boundary

- Manifest, runners, approved state and failure artifact unchanged.
- Matching Spain SSH processes: `0`.
- Matching controlled-stage runner processes: `0`.
- Transaction-005 stage outcome remains absent.
- Proposed transaction-006 outcome/failure paths: absent.
- No remote transaction, backup, release, service, network or container was created by attempt 005.
- No fresh AWG2 health/equality measurement was made in this attempt; AWG2 was untouched.

Next launch must retain the exact packaged runner and all trust checks, while using a PowerShell-5-compatible child module environment. The verified local correction is to remove only inherited `PSModulePath` from that child's `ProcessStartInfo.EnvironmentVariables`; do not alter the parent environment, system settings, ACLs or package.

A new exact approval is required for transaction 006. The successful local trust-only control is not authorization to retry stage 005 or launch stage 006.

```text
/APPROVE PHASE16 SPAIN APPLICATION_AND_AWG31_STAGE PACKAGE_phase16-awg3-family-3-1-spain-pilot-20260824-015 IDENTITY_7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509 MANIFEST_SHA256_f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74 STATE_e7b83199c3cef351964746a9f3a60ab665f632f8b4c4a5f8b0ad58494db44c92 ROLLBACK_SCOPE_SHA256_15d6fe8bd131a56bf4d5a6545d4cd7ecf22a785f1da916de6410cd9d9e5167b3 TRANSACTION_phase16-spain-stage-20260827-006 MANDATORY_ROLLBACK_ON_FAILURE AWG2_UNTOUCHED
```

## Phase 16 status

- ✅ Task 0 — baseline.
- ✅ Task 1 — verified package 015.
- ✅ Task 2 — Spain read-only preflight PASS, claim 027.
- ❌ Task 3 — local prelaunch STOP 005; cause identified, new exact approval 006 required.
- ⏳ Task 4 — first AWG3.1 operator config for ARM/Windows.
- ⏳ Task 4.5 — mandatory AWG2 ↔ AWG3.1 transport-quality A/B gate.
- ⏳ Task 5 — client acceptance after Task 4.5.
- ⏳ Task 6 — closeout.

Stage/install: `0/0`; client peers/configs: `0/0`; general issuance remains disabled. AWG2 untouched.

Only this evidence receipt is to be committed locally. Push remains blocked on the separate informed approval to publish the accumulated history to the public origin. The named branch and linked worktree are retained.

Next-gate model profile from the approved plan: GPT-5.6 SOL / High. This profile is not live-action authorization.
