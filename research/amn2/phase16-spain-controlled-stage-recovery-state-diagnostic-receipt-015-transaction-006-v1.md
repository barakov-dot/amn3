# Phase 16 — package 015, transaction 006 recovery-state diagnostic V1

Recorded UTC: `2026-08-27T18:32:05.9933859Z`.

## Decision

- Diagnostic transport and normalized schema: `pass`.
- SSH remote-command attempts: `1/1`; no retries.
- Operational decision: `semantic_stop_matching_coordinator_process_unattributed`.
- Transaction 006, its claims/milestones/outcome/failure-locus, package/release/ledgers, state-bound backup and AWG3.1 resources were observed absent.
- A command-line pattern query returned at least one matching process: `coordinator_process=present`.
- The query does not establish that the match is a coordinator worker, belongs to transaction 006, or is safe to terminate. No PID, start identity, parent, stdin, wait class or full command line was collected.
- Do not declare remote clean, stage complete, or rollback verified from this evidence.
- No remote write, process signal, rollback, stage/preflight retry, install, client config, peer or issuance operation was performed.
- AWG2 was inspected read-only and was not changed. Its owner/container/interface checks were non-blocking; handshake freshness did not pass the unchanged 600-second policy.
- Transaction 006 remains consumed as a stage attempt and must not be reused.

## Exact approved bindings

- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-015`.
- Identity: `7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509`.
- Manifest SHA256: `f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74`.
- Approved historical state SHA256: `e7b83199c3cef351964746a9f3a60ab665f632f8b4c4a5f8b0ad58494db44c92`.
- Transaction: `phase16-spain-stage-20260827-006`.
- Bound STOP receipt SHA256: `380b48b7f319d6c4f2987148dda4e1c38eab586826ee6ad6ac2dc9390a17975d`.
- Bound runner-failure SHA256: `dd851bb7731e1e9885d63b8a12488e57d167263cc6ee9f980aacec76996c518f`.
- Normalized diagnostic approval SHA256: `e286c6da3e93780a1368cf58f4c9cb313bec25de3e64f90f00c0f91d0d298ca9`.
- Target: `138.124.181.246`; strict pinned SSH host-key checking.
- Command ID: `PHASE16_TRANSACTION006_RECOVERY_STATE_V1`.
- Pre-run HEAD: `0a58b7149c6431cfb44f9571d5aa71f91f607c9b`.
- Branch: `codex/phase16-awg3-family-3-1-spain-pilot-015`.

The state binding identifies the already accepted claim-027 preflight snapshot. This diagnostic did not publish or refresh a preflight outcome.

## Preparation and single transport

- Temporary diagnostic source SHA256/bytes: `685f109616b4f1ef5d4ff5c4a3ab683e0a61b1cc5955358d80473b3dd7426883` / `22278`.
- Temporary local driver SHA256/bytes: `822e9e70e55f3971b9e9b87ed8b91ad90cd9cf9b91a1bcc97cb791dc6b0ca947` / `16068`.
- Local Python fixtures: `30/30 pass`, including exact milestone/claim/outcome bindings, no completion inference from consumed claims, failed image-query rejection, 600-second boundary, and a fully synthetic absent-resource snapshot.
- Local PowerShell output-schema fixtures: `2/2 pass`; positive normalized shape accepted, raw-persistence flag rejected.
- Fixtures started no SSH or remote command. Their synthetic values are not server evidence.
- Prelaunch gate: `pass`; eight local checksum bindings, exact approval/identity, actual trust assertion, no existing matching local SSH process.
- Prelaunch UTC: `2026-08-27T18:28:19.5751352Z`.
- Local driver used Windows PowerShell 5 with only the child's inherited `PSModulePath` removed and process-local execution-policy bypass.
- SSH environment and trust checks came from the unchanged packaged preflight helper. No collector or stage entrypoint was invoked.
- The diagnostic source was gzip/base64-framed into a Python command, checked remotely by exact decompressed length and SHA256, and executed in memory with `-I -B`. No remote script or package file was written.
- SSH command-line length: `9951`, below the checked local bound.
- SSH started UTC: `2026-08-27T18:29:37.3758879Z`.
- SSH ended UTC: `2026-08-27T18:29:39.2273125Z`.
- Europe/Moscow window: `2026-08-27 21:29:37–21:29:39`.
- Elapsed seconds: `1.851`; timeout: `false`; SSH exit: `0`; local driver exit: `0`.
- Approved SSH timeout: `30 seconds`; internal diagnostic probe budget: `19 seconds`, with bounded read-only subprocess output.
- Normalized stdout bytes/SHA256: `1402` / `ff2d086cdf4f0eb46f7586e35c135e615661e96c51fe8290173b5bfa2aa2390b`.
- Stderr bytes/SHA256: `0` / `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Stderr class: `none`.
- Output schema: `amn2.phase16.transaction006-recovery-state.v1`; canonical JSON, exact field sets and allowlisted leaves: `pass`.
- Raw stdout/stderr persistence: `false`. Only normalized classifications and transport metadata are recorded here.

## Observed transaction and resource classes

- Transaction root and entries: `absent`.
- Transaction outcome: `absent`.
- Application and runtime claims: `absent`.
- Milestones and failure-locus artifacts: `absent`; completed milestone lists empty; last completed milestone `unavailable`.
- Transaction package-staging directory: `absent`.
- Remote package root and manifest: `absent`.
- Package-015 application release and application-staging directory: `absent`.
- Application, AWG3.1 runtime and coordinator ledgers: `absent`.
- Approved-state-bound SQLite backup: `absent`; the database and backup contents were not read.
- AWG3.1 unit file, runtime state root and config path: `absent`; config contents were not read.
- AWG3.1 service load/active state: `not-found/inactive`.
- AWG3.1 container and network: `absent`.
- Exact pinned AWG3.1 runtime image: `absent`, from a successful bounded image inventory, not an error-message inference.
- Host AWG3.1 bridge and interface: `absent`.
- Container AWG3.1 interface: `not_queryable`, because the target container is absent.
- UDP 30002 listener: `absent`.
- Coordinator command-line pattern match: `present`.

The last result came from a bounded `pgrep -f` search for the literal coordinator script-name pattern. Only its normalized presence class was emitted. A filename match alone cannot distinguish an executing coordinator from a matching shell wrapper or other process, cannot attribute the match to transaction 006, and cannot justify a kill or cleanup.

Resource absence is an observation at this diagnostic's time, not proof of historical non-execution or absence of a pending process. No automatic cleanup followed.

## AWG2 read-only health

- Owner initial/final: `active/active`.
- Container: `running`; state across the two inspections: `stable`.
- Interface: `present`.
- Handshake schema: `valid`.
- Handshake freshness class: `stale_gt_600_or_zero_or_future`.
- Overall collector-policy health: `stop`.

This combined freshness class does not distinguish an old handshake, zero timestamp or future timestamp. It must not be narrowed without new evidence. The 600-second rule was not changed. These classifications do not establish transport quality, throughput or post-stage AWG2 equality.

## Local postcheck and retained scope

- Postcheck UTC: `2026-08-27T18:32:05.9933859Z`.
- Matching local Spain SSH processes: `0`.
- Matching local stage/recovery runner processes: `0`.
- Diagnostic source/driver, package manifest, original STOP receipt and runner-failure hashes unchanged.
- Only the two exact checksum-verified temporary local diagnostic files are removed after collection; no package, evidence artifact, lock, unrelated file or remote resource is removed.
- Normalized evidence and all relevant checksums are retained in this receipt; temporary helper source remains recoverable from this task's tool history.
- No package rebuild, materialization, separate package verifier, full suite or production-code edit was performed.

## Critical next boundary

Priority 0: one separately approved read-only process-attribution diagnostic, before any new stage or source-level fix:

- Bind this receipt's final checksum and normalized stdout SHA256.
- Target the coordinator-name matches only; distinguish worker/bootstrap/shell-wrapper/other classes.
- Capture normalized match count, package/transaction attribution, parent kind, stdin kind, wait/lifecycle classes and a non-secret process-set checksum.
- Do not capture raw command lines or process environment values.
- No process signals, kill, remote write, rollback, stage/preflight retry, install, config or issuance.
- No additional AWG2 probe is needed for this process-only step.

Priority 1, only after the process/recovery boundary is resolved: a separate bounded local TDD authorization can address the already reproduced runner scalar-exit defect and investigate the original stdin-write failure. This diagnostic proves successful read-only SSH in its own window, not the cause or correction of the earlier stage transport failure.

The exact next approval is emitted after this receipt's checksum is fixed. No next approval is implied by this receipt.

## Phase 16 status

- ✅ Task 0 — baseline.
- ✅ Task 1 — verified immutable package 015.
- ✅ Task 2 — preflight PASS, claim 027.
- ❌ Task 3 — recovery STOP: matching coordinator-name process remains unattributed; no new stage.
- ⏳ Task 4 — first AWG3.1 operator config for ARM/Windows.
- ⏳ Task 4.5 — mandatory AWG2 ↔ AWG3.1 transport-quality A/B gate.
- ⏳ Task 5 — client acceptance after Task 4.5.
- ⏳ Task 6 — closeout.

This diagnostic performed no AWG2 mutation, stage, install, rollback or client issuance. General issuance remains prohibited.

Only this receipt is committed locally. The branch and linked worktree are retained. Push remains blocked on the separate informed approval for publishing the accumulated history to the public origin; no push attempt is made.

Next-gate model profile from the approved plan: GPT-5.6 SOL / High, because remote process attribution remains safety-critical.
