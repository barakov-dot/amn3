# Phase 16 Spain AWG2 health diagnostic receipt 015 V1

- Recorded: `2026-08-27T05:28:30Z`
- Started: `2026-08-27T05:26:10Z`
- Ended: `2026-08-27T05:26:14Z`
- Local observation window (Europe/Moscow): `2026-08-27 08:26:10–08:26:14`
- Command ID: `PHASE16_PACKAGE015_AWG2_HEALTH_STOP_V1`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-015`
- Package identity: `7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509`
- Manifest SHA-256: `f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74`
- Bound preflight claim: `phase16-spain-preflight-20260827-026`
- Preflight outcome SHA-256: `752ca5c954ce3092ac87a0df90a874f5f67bbaa3a628b82a264b75ed661feb80`
- Worktree HEAD before diagnosis: `5899510ff2fee9b0e357d4a5faadab238d5d250d`
- Destination: `root@138.124.181.246`
- Strict host-key checking: `true`
- SSH attempts: `1/1`
- Timeout bound: `30 seconds`
- Elapsed transport time: `3606 milliseconds`
- Timed out: `false`
- Exit: `0`
- Diagnostic program SHA-256: `185a86acc9522e20e33adc9e45e02e92e73c2d44e710be7c1de42a1a623f4280`
- Diagnostic program bytes: `5003`
- Normalized stdout SHA-256: `559fbab5aec0afda366f4232b81bdefc4cf7c71b32e0a32f98820dd9a630667b`
- Normalized stdout bytes: `585`
- Stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Stderr bytes: `0`
- Normalized schema and canonical-byte validation: `pass`

## Local preparation

The existing package-013 AWG2 health V1 diagnostic was recovered from this task's execution record and checked against its recorded source SHA-256 `d441a8e26ea7b22e5bb6174422f00faf1fc88fa47803cf8099fd54e0cb3890b6`. Only its package ID, command ID and preflight-outcome binding were changed for the remote program; the probe/classification logic was preserved.

Before the single SSH launch, local checks verified the current package identity, manifest, collector and runner hashes, the bound STOP outcome, a clean named worktree, absence of an earlier receipt for this command, and the pinned SSH trust bundle. The verified packaged runner was dot-sourced only for local trust/process helpers; its main function and collector transport were not invoked.

- Python AST: `pass`
- PowerShell AST: `pass`
- Synthetic cases: `18 passed`
- Synthetic command allowlist: `pass`
- Handshake boundary: age `600` accepted, age `601` rejected
- Local synthetic live/SSH calls: `0`

## AWG2 health classification

- Collector-equivalent health state: `stop`
- Exact current failure class: `handshake_freshness`
- Owner unit state: `pass`
- Owner unit stability: `pass`
- Container shape: `pass`
- Container stability: `pass`
- Interface `awgsp0` shape: `pass`
- Handshake command: `pass`
- Handshake record schema: `pass`
- Handshake freshness class: `stale_gt_600`

At the diagnostic observation time, the sole failing AWG2 health dimension was the unchanged 600-second handshake-recency condition. No fresh positive handshake was observed; all positive handshake timestamps belonged to the older-than-600-seconds class. Raw timestamps, keys, peer counts, container PIDs and restart counters were not returned or persisted.

This is a new diagnostic observation, not a new preflight outcome or proof of the historical substate at claim 026. It is consistent with that outcome's AWG2 health STOP. The earlier preflight remains STOP and consumed. No policy relaxation or local code fix is justified by these findings.

This health-recency classification does not establish the cause of the operator's reported slow/unstable AWG2 transport. Task 4.5 remains mandatory after the first AWG3.1 pilot configuration and before client acceptance/closeout.

## Canonical normalized output

The following JSON, encoded as UTF-8 with one terminal LF, reproduces the validated 585-byte stdout and SHA-256 above. It contains only fixed bindings and allowlisted classes.

```json
{"collector_equivalent_state":"stop","command_id":"PHASE16_PACKAGE015_AWG2_HEALTH_STOP_V1","container_shape":"pass","container_stability":"pass","failure_class":"handshake_freshness","handshake_command":"pass","handshake_freshness_class":"stale_gt_600","handshake_schema":"pass","interface_name":"awgsp0","interface_shape":"pass","owner_stability":"pass","owner_state":"pass","package_id":"phase16-awg3-family-3-1-spain-pilot-20260824-015","preflight_outcome_sha256":"752ca5c954ce3092ac87a0df90a874f5f67bbaa3a628b82a264b75ed661feb80","schema":"amn2.phase16.awg2-health-diagnostic.v1"}
```

## Safety and post-run checks

- Collector execution: `false`
- Preflight retry: `false`
- Diagnostic retry: `false`
- Raw values returned: `false`
- Raw stdout/stderr persisted: `false`
- Remote configuration/file writes issued: `false`
- Live mutation: `false`
- Stage/install/rollback attempted: `false`
- Config generation or issuance attempted: `false`
- AWG2 changed: `false`
- AWG2 freshness policy changed: `false`
- Matching Spain SSH processes before/after completion: `0/0`
- Package 014/015 tracked files changed: `false`
- Package 014 manifest and package 015 manifest/collector/runner hashes: `unchanged`
- Bound preflight outcome hash: `unchanged`
- Worktree before receipt creation: `clean`
- Package materialization/verifier repeated: `false`
- Full regression suite repeated: `false`
- Public Git push: `not attempted; separate informed publication confirmation remains pending`

The approved diagnostic allowance is consumed `1/1`. This receipt authorizes no additional SSH, preflight, stage, install, rollback, config generation, issuance or AWG2 change.

## Phase 16 status

- ✅ Task 0 — local baseline.
- ✅ Task 1 — verified package 015.
- ❌ Task 2 — preflight STOP; AWG2 handshake freshness blocks progress.
- ⏳ Task 3 — controlled stage.
- ⏳ Task 4 — first AWG3.1 operator configuration for ARM/Windows.
- ⏳ Task 4.5 — mandatory AWG2 ↔ AWG3.1 transport-quality A/B gate.
- ⏳ Task 5 — client acceptance.
- ⏳ Task 6 — closeout.

## Exact next bounded action

The operator first enables the existing Spain AWG2 client configuration and generates real traffic. Do not create a replacement configuration or mutate AWG2 to satisfy this gate.

After operator traffic, one new preflight requires this separate explicit scope decision, followed by a new exact checksum-bound `/APPROVE`. The `/GO` below alone does not authorize egress:

```text
/GO PHASE16 ONE_NEW_PREFLIGHT_AFTER_OPERATOR_AWG2_TRAFFIC PACKAGE_phase16-awg3-family-3-1-spain-pilot-20260824-015 IDENTITY_7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509 PREVIOUS_PREFLIGHT_OUTCOME_SHA256_752ca5c954ce3092ac87a0df90a874f5f67bbaa3a628b82a264b75ed661feb80 DIAGNOSTIC_STDOUT_SHA256_559fbab5aec0afda366f4232b81bdefc4cf7c71b32e0a32f98820dd9a630667b MAX_HANDSHAKE_AGE_600S ONE_NEW_PREFLIGHT NEXT_EXACT_APPROVE_REQUIRED NO_LOCAL_FIX NO_REMOTE_WRITE NO_STAGE NO_INSTALL AWG2_UNTOUCHED
```

Model per the active Phase 16 plan: `GPT-5.6 SOL High`. Recommended next gate model: `GPT-5.6 SOL High`. Model selection does not authorize live actions.
