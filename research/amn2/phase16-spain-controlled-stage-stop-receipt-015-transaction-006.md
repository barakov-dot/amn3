# Phase 16 — package 015, transaction 006: runner STOP during stdin write

Recorded UTC: `2026-08-27T18:08:16.1915587Z`.

## Decision and safety boundary

- Decision: `runner_stop_stdin_write_remote_state_unconfirmed`.
- Controlled-stage runner invocation: `1/1`; SSH process creation: `1/1`.
- Last completed runner milestone: `process_started`; failure class: `stdin_write`.
- A successful stage outcome was not created or received.
- The Windows PowerShell 5 runner process exited `0`, but emitted the fixed STOP token and wrote a canonical runner-failure artifact. Exit 0 is not stage acceptance.
- Authentication, remote coordinator entry, application/runtime completion and rollback completion are unconfirmed.
- Transaction 006 is consumed as a local attempt. Do not reuse it or overwrite its failure evidence.
- No automatic stage retry, preflight retry, extra SSH, separate rollback or remote cleanup was performed.
- No client peer/config/QR or issuance operation was requested or launched.
- No AWG2 mutation was requested or performed by the local runner; no post-attempt AWG2 equality or health result was received.
- General issuance remains prohibited. This receipt is not proof of current remote health or a clean rollback.

The approved stage includes its bounded mandatory rollback path. Because transport did not return a coordinator outcome, neither that path's execution nor its completion is established by the available local evidence.

## Exact approved bindings

- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-015`.
- Package identity: `7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509`.
- Manifest SHA256: `f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74`.
- Approved state SHA256: `e7b83199c3cef351964746a9f3a60ab665f632f8b4c4a5f8b0ad58494db44c92`.
- Rollback scope SHA256: `15d6fe8bd131a56bf4d5a6545d4cd7ecf22a785f1da916de6410cd9d9e5167b3`.
- Normalized approval SHA256: `a45fb14a8bfac714645aed7649684b310d32e024472b85490242a02cb990f714`.
- Transaction: `phase16-spain-stage-20260827-006`.
- Target: `138.124.181.246`.
- Stage runner SHA256: `8eb9e2896a58c1cf70a493fcd8f00fd16764505ccdaaca940d78d6ae13a825e7`.
- Imported preflight runner SHA256: `e5551706eb27ff8e5cb3299f7b57ad7f1f55b9d80bb88bcc7501c29f4ba2d983`.
- Coordinator SHA256: `2dccc21218ae6f6b7e28ac68f8c624aa8c9f55410638f7d9b7205a43660d2fc5`.
- Prior transaction-005 STOP receipt SHA256: `3f6168ba01f742032714e988fd517f588a74f923a7a7034230cff4c98788b181`.
- Prior transaction-005 runner-failure SHA256: `9636bece65d7f37d1702ae2e62fae7769dd730e74a852c5534016eb95bec466f`.
- Pre-run HEAD: `a32e246126f619dcbf82ae3892ab09765bdf1942`.
- Branch: `codex/phase16-awg3-family-3-1-spain-pilot-015`.
- Worktree: `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\phase16-004`.

The approved state remains the immutable claim-027 preflight PASS outcome, observed 2026-08-27 19:58:05–19:58:21 Europe/Moscow. It is a historical snapshot, not a continuous-health assertion. No preflight was repeated.

## Local prelaunch gate

The first read-only gate invocation stopped locally before trust/SSH with exit 1 and no stdout. Its stderr length was 937 bytes; raw text was not retained.

A bounded read-only control established two defects in the assistant's inline gate, not in package 015:

1. Dot-sourcing the packaged helper resets its `PackageRoot` parameter in the caller scope; PowerShell variable names are case-insensitive. The gate's `$packageRoot` was present before dot-source and absent afterward.
2. The saved canonical preflight enum is lowercase `pass`; the gate incorrectly used a case-sensitive comparison to uppercase `PASS`.

One local correction used a distinct `$phasePackageRoot` variable and the exact lowercase enum. The corrected gate passed at `2026-08-27T18:02:33.4961083Z`:

- Exact manifest/identity, eight critical asset hashes, inventory 172 files, no unexpected files or reparse entries.
- Exact approved state, 23 observations, zero stop reasons, terminal claim checksum.
- Exact approval and canonical rollback-scope checksum.
- Full SSH trust assertion for the exact host.
- Transaction-006 outcome/failure paths absent; no matching Spain SSH or stage runner processes.
- Existing linked worktree clean; HEAD and named branch exact.
- PowerShell major version 5; only the child's inherited `PSModulePath` removed.
- No SSH, stage entrypoint, package materialization or separate verifier invoked by these gates.

The package, trust bundle, ACLs, parent environment and machine execution policy were not changed.

## Single stage invocation

The frozen packaged runner was launched through Windows PowerShell 5 `-File`, with process-local `-ExecutionPolicy Bypass` and the previously verified child-only `PSModulePath` removal. No entrypoint or trust check was replaced.

- Started UTC: `2026-08-27T18:03:35.4049598Z`.
- Ended UTC: `2026-08-27T18:05:38.4356760Z`.
- Europe/Moscow window: `2026-08-27 21:03:35–21:05:38`.
- Elapsed seconds: `123.031`.
- Outer timeout: `false`.
- Actual runner process exit: `0`.
- Outer stdout bytes/SHA256: `0` / `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Outer stderr bytes/SHA256: `43` / `9e650e4049eb870274ee7321d57cca26007736a1136ff2860ba43c9cd89aeb48`.
- Fixed stderr token: `AMN2_PHASE16_CONTROLLED_STAGE_RUNNER_STOP`.
- Local stage outcome: absent.
- Local runner-failure artifact: present.
- Raw stdout/stderr persistence: `false`.

## Canonical runner-failure artifact

Path: `C:\ProgramData\AMN2\phase16\controlled-stage\outcomes\phase16-spain-stage-20260827-006.json.runner-failure.json`.

- SHA256: `dd851bb7731e1e9885d63b8a12488e57d167263cc6ee9f980aacec76996c518f`.
- Bytes: `531`.
- Canonical JSON and exact field set: pass.
- Schema: `amn2.phase16.controlled-stage-runner-failure.v1`.
- Result: `runner_stop`.
- Failure class: `stdin_write`.
- Last completed milestone: `process_started`.
- Transport exit code: `null`.
- Recorded transport stdout/stderr byte counts: `0/0`.
- Both recorded transport stream hashes: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Raw output persisted: `false`.

Important: at this failure boundary, the runner has not called its transport-summary collector. The zero counts and empty hashes are initialized placeholders, not proof that SSH produced empty streams. No transport stderr text or remote error class is available.

Code order proves that arguments, trust, package, approval and archive construction completed and the SSH process started. It does not prove authentication, complete frame delivery or remote execution. The underlying reason for the stdin-write exception remains unresolved.

## Exit-code discrepancy: bounded local control

A no-file, no-SSH Windows PowerShell 5 control compared two synthetic functions captured into `$exitCode` before `exit $exitCode`:

- A function returning only integer 64 produced process exit `64`.
- The same pattern with one preceding synthetic object followed by integer 64 produced process exit `0`.
- Both controls produced empty stdout/stderr and invoked no packaged runner.

The packaged trust assertion emits an object into the entrypoint's success stream; the entrypoint result is assigned to `$exitCode`. This code path and the control explain why the numeric process exit is not a trustworthy success signal after trust has passed. The STOP token and canonical outcome/failure artifacts remain authoritative.

No runner fix or package revision was made. Any source-level correction requires a separate bounded local TDD authorization; recovery-state verification takes priority.

## Terminal local readback

Readback UTC: `2026-08-27T18:06:44.4690291Z`.

- Manifest, stage runner, approved state and transaction-005 failure checksum unchanged.
- Transaction-006 outcome still absent; canonical failure artifact verified.
- Matching Spain SSH processes: `0`.
- Matching controlled-stage runner processes: `0`.
- No local orphan process observed. Remote process/resource absence is not established.
- No additional remote diagnostic, rollback, retry, installation or issuance was executed.

## Next exact boundary

STOP before all further Spain egress. The next requested action is one separately approved read-only recovery-state diagnostic:

- Command ID: `PHASE16_TRANSACTION006_RECOVERY_STATE_V1`.
- Target/package/identity/manifest/state/transaction: the exact bindings above.
- Bind both this completed STOP receipt's computed SHA256 and the runner-failure artifact SHA256.
- One SSH remote-command attempt, timeout 30 seconds, strict host-key checking.
- Capture normalized transaction presence, milestones/failure-locus classes, application/runtime/coordinator/package/release/service/container/network/interface/listener/backup state and AWG2 health classes only.
- No raw values or raw persistence; no remote write, rollback, stage/preflight retry, install, client config or issuance.
- An absent transaction must be reported as observed absence, not inferred from this stdin failure.
- A present transaction must be interpreted using completion milestones, not claim consumption alone.

The exact approval is emitted only after this receipt's checksum is fixed, avoiding a self-referential receipt hash. This receipt itself grants no new egress.

## Phase 16 status

- ✅ Task 0 — baseline.
- ✅ Task 1 — verified immutable package 015.
- ✅ Task 2 — Spain read-only preflight PASS, claim 027.
- ❌ Task 3 — transaction 006 STOP; remote stage and rollback state unconfirmed.
- ⏳ Task 4 — first AWG3.1 operator config for ARM/Windows.
- ⏳ Task 4.5 — mandatory AWG2 ↔ AWG3.1 transport-quality A/B gate.
- ⏳ Task 5 — client acceptance after Task 4.5.
- ⏳ Task 6 — closeout.

Client config/peer issuance: `0`. AWG2 mutation not authorized or requested; post-attempt equality is unconfirmed. General issuance remains prohibited.

Only this receipt is to be committed locally. No implementation, immutable package or unrelated file is changed. No regression suite, materialization or separate package verifier is repeated.

Push remains blocked on the separate informed approval to publish the accumulated history to the public origin. No push attempt is made by this step. The named branch and linked worktree are retained.

Next-gate model profile from the approved plan: GPT-5.6 SOL / High. This profile is not live-action authorization.
