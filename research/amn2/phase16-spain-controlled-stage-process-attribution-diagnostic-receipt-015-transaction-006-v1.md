# Phase 16 — package 015, transaction 006 coordinator process attribution V1

Recorded after the single diagnostic and local postcheck on `2026-08-27`.

## Decision

- Diagnostic transport and normalized output schema: `pass`.
- SSH remote-command attempts: `1/1`; no retry.
- Operational decision: `stop_waiting_package015_bootstrap_transaction_unproven`.
- One coordinator-name match was observed with the exact packaged bootstrap argument shape and expected coordinator source hash for package 015.
- Its normalized parent kind was `sshd`; stdin kind `pipe`; wait class `pipe_read`; lifecycle `sleeping`.
- Transaction binding was `not_available_from_argv`. The transaction identifier is supplied in the stage input frame, not in the bootstrap arguments.
- This is evidence of a process waiting for pipe input at the observation time. It is not proof of transaction-006 ownership, coordinator entry/completion, the exact blocked frame boundary, or the cause of the earlier local `stdin_write` failure.
- No process signal, kill, rollback, stage/preflight retry, install, config, peer or issuance operation was performed.
- No AWG2 probe or mutation was performed.
- Remote clean, stage accepted and rollback verified remain unproven. Stage transaction 006 remains consumed and must not be reused.

## Exact approved bindings

- Target: `138.124.181.246`; strict pinned SSH host-key checking.
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-015`.
- Package identity: `7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509`.
- Manifest SHA256: `f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74`.
- Approved historical state SHA256: `e7b83199c3cef351964746a9f3a60ab665f632f8b4c4a5f8b0ad58494db44c92`.
- Transaction context: `phase16-spain-stage-20260827-006`.
- Recovery receipt SHA256: `7c3d9b7125af7bb38cc32f1938e3afe1e75cd59421efe1e049320c4147e27c46`.
- Recovery normalized stdout SHA256: `ff2d086cdf4f0eb46f7586e35c135e615661e96c51fe8290173b5bfa2aa2390b`.
- Bound stage STOP receipt SHA256: `380b48b7f319d6c4f2987148dda4e1c38eab586826ee6ad6ac2dc9390a17975d`.
- Bound runner-failure SHA256: `dd851bb7731e1e9885d63b8a12488e57d167263cc6ee9f980aacec76996c518f`.
- Normalized current diagnostic approval SHA256: `e66adef172844347b99bfc64328905b71744e54f906f92d6077a29b9ed754f04`.
- Command ID: `PHASE16_TRANSACTION006_COORDINATOR_PROCESS_ATTRIBUTION_V1`.
- Pre-run HEAD: `a2be212cd366d0a75ed8c4e5dd82f1af5b28e84b`.
- Branch: `codex/phase16-awg3-family-3-1-spain-pilot-015`.

The top-level transaction ID binds the approved investigation context; it does not override the observed `transaction_binding` class. The historical state binding does not refresh preflight or health evidence.

## Preparation and bounded collection

- Temporary Python diagnostic source SHA256/bytes: `862b3a423c0ca90908b2a62f002a28e536f4519fb17ad0650815e1dd18fa27da` / `11029`.
- Temporary PowerShell driver SHA256/bytes: `d6260d2dfdb83f0fe1c3c301571b30ba902ad67a524dcfbfa0c378c5ea355d4a` / `16025`.
- Local Python fixtures: `38/38 pass`; exact bootstrap versus token-only classification, parent/stdin/wait/lifecycle classes, vanished/changed candidates, incomplete discovery and process-set hashing were covered.
- Local PowerShell output-schema fixtures: `11/11 pass`; extra/raw fields, PID, bad count/type/hash, unknown class, false transaction attribution and contradictory completeness were rejected.
- These fixtures used synthetic inputs and started no SSH. Their values are not server evidence.
- Prelaunch: `pass`; nine local checksum bindings, exact approval and manifest identity, actual pinned trust assertion, no existing matching local SSH.
- Prelaunch UTC: `2026-08-27T19:00:28.7548689Z`.
- Windows PowerShell 5 was launched with only the child's inherited `PSModulePath` removed and process-local execution-policy bypass. Parent/global environment, machine policy and ACLs were unchanged.
- The unchanged packaged preflight helper supplied trust and SSH environment functions only; no collector or stage entrypoint was called.
- Diagnostic source was gzip/base64-framed into an isolated Python command, verified by exact decompressed length/SHA256, and executed in memory with `-I -B`.
- No script, package, marker or other remote file was written.
- Remote collection used bounded read-only `/proc` enumeration and metadata reads. Command-line bytes were used in memory only to select literal coordinator-name matches, classify candidate/parent argument shapes and hash stable identity records.
- The diagnostic's own process was excluded. Nonmatching command-line bytes were discarded; process environments, stdin contents, process memory and raw traffic were not read.
- Remote limits: `8 seconds` internal budget, `8192` numeric process entries, `16` matches, `65536` bytes per command line, bounded stat/wait/link metadata and `16384` output bytes.
- Candidate start identity, parent identity field, owner and command-line bytes were checked before/after candidate inspection; changed or vanished candidates cannot produce a complete process-set hash.
- Parent-kind classification was guarded by a parent start-identity check. It is a normalized process-name/argument class, not a claim of connection ownership.
- The remote helper launched no subprocess and contains no signal/kill action.
- Canonical process-set SHA256 is computed over sorted internal identity records containing PID, start ticks, owner UID, parent PID and command-line SHA256. Only the final process-set hash was emitted; individual identity values were neither emitted nor persisted.
- A complete enumeration is a bounded observation, not an atomic snapshot of all future server state.

## Single SSH result

- Started UTC: `2026-08-27T19:01:12.1703396Z`.
- Ended UTC: `2026-08-27T19:01:17.0080885Z`.
- Europe/Moscow window: `2026-08-27 22:01:12–22:01:17`.
- Elapsed seconds: `4.838`.
- Approved SSH timeout: `20 seconds`; timeout observed: `false`.
- SSH exit: `0`; local driver exit: `0`.
- SSH command-line length: `5704`, below the checked local bound.
- Normalized stdout bytes/SHA256: `614` / `01c9a9f017887107ac5085399be75a461f18b8eb305c8371a1111091b5819bb4`.
- Stderr bytes/SHA256: `0` / `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Stderr class: `none`.
- Output schema: `amn2.phase16.transaction006-process-attribution.v1`; canonical JSON, exact field sets and allowlisted values: `pass`.
- Discovery class: `complete`.
- Match count: `1`.
- Process-set SHA256: `53c5a6edf66d80aa73ed07a4694072d13a6aaca4b2dd00fde490467735f047fd`.
- Raw stdout/stderr/command-line/environment/PID persistence: `false`.

## Observed process classes

- Process kind: `exact_coordinator_bootstrap`.
- Package binding: `expected_coordinator_hash_package015`.
- Transaction binding: `not_available_from_argv`.
- Parent kind: `sshd`.
- Stdin kind: `pipe`.
- Wait class: `pipe_read`.
- Lifecycle: `sleeping`.

The exact bootstrap argument shape binds the expected coordinator source hash. It does not prove that all coordinator bytes or the request/archive frame were received, that the embedded code executed, or that the full package was installed.

The parent class is `sshd`, not `init`; do not describe the process as proven orphaned/reparented. The earlier recovery receipt's resource-absence observations remain historical. This process-only diagnostic did not repeat resource, service, Docker, application, backup or AWG2 probes.

## Local closeout

- Postcheck UTC: `2026-08-27T19:03:01.0428768Z`.
- Matching local Spain SSH processes: `0`.
- Matching local diagnostic drivers: `0`.
- Original package manifest, recovery receipt, runner-failure and temporary helper hashes remained unchanged.
- Stage-006 outcome remained absent locally.
- Removed only the two exact checksum-verified temporary local diagnostic helper files under this worktree's `tmp` directory.
- Helper source remains recoverable from this task's tool history; normalized evidence and checksums are retained here.
- No immutable package, existing receipt, claim, lock, unrelated file or remote resource was removed.
- No production-code fix, new package, package materialization, separate package verifier or full suite was performed.
- Only this receipt is committed locally. Branch and linked worktree are retained.
- Push is not attempted: separate informed approval for publication of accumulated history to the public origin remains pending.

## Critical next boundary — not authorized by this diagnostic

Priority 0: resolve the waiting-process boundary before another stage. A possible next operation is separately approved, process-set-bound graceful retirement of this exact waiting bootstrap, not transaction rollback:

- Bind this receipt's final SHA256, normalized stdout SHA256 and observed process-set SHA256.
- In one fresh SSH operation, require the same single-process identity hash, exact package-015 bootstrap arguments, root owner, `sshd` parent, `pipe` stdin, `pipe_read` wait and sleeping lifecycle immediately before any signal.
- Require fresh normalized absence checks for package-015/transaction-006 stage resources; any mismatch, resource presence, ambiguous read or changed process identity stops before signaling.
- Permit at most one `SIGTERM` to that exact matched process only, followed by bounded read-only process/resource readback.
- No parent/process-group signal, SIGKILL, automatic retry, rollback, AWG2 probe, stage/preflight retry, install, config or issuance.
- Do not infer transaction-006 ownership. The operator would be explicitly authorizing retirement of the fingerprint-bound package-015 bootstrap as a separate process-level action.
- If the process is already absent, record that fact without signaling; if it survives the bounded wait, stop without escalation.

This is a proposal requiring a new exact approval. No signal or retirement was authorized or executed in the present turn.

Priority 1: a separate bounded local TDD gate can then address the already reproduced scalar-exit defect and investigate the stage stdin/frame/EOF contract. The observed waiting read does not by itself establish which local transport change is correct. Package 015 remains immutable.

Priority 2: only after the process/recovery and local-fix gates are resolved, obtain the required new checksum/state-bound preflight and stage approvals. No first client config may precede accepted controlled stage and exact pilot approval.

## Phase 16 status

- ✅ Task 0 — baseline.
- ✅ Task 1 — verified immutable package 015.
- ✅ Task 2 — prior preflight PASS, claim 027.
- ❌ Task 3 — waiting package-015 bootstrap remains; transaction attribution unproven; stage not accepted.
- ⏳ Task 4 — first AWG3.1 operator config for ARM/Windows.
- ⏳ Task 4.5 — mandatory AWG2 ↔ AWG3.1 transport-quality A/B gate.
- ⏳ Task 5 — client acceptance after Task 4.5.
- ⏳ Task 6 — closeout.

Current diagnostic safety state: AWG2 untouched and not probed; zero remote writes/signals/kill/rollback/stage/install/config/issuance actions. General issuance remains prohibited.

Next-gate model profile from the approved plan: GPT-5.6 SOL / High, because process identity, recovery and signal boundaries are safety-critical. Actual active model/effort metadata is not asserted by this receipt.
