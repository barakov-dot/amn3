# Phase 16 package 015: one new preflight after operator traffic

- Recorded: `2026-08-27T16:40:28Z`
- Scope: local preparation for exactly one new Spain read-only preflight after operator-generated AWG2 traffic.
- This document is not a preflight outcome, remote-state observation, SSH authorization, or successful health result.
- Local HEAD before this receipt: `60bf5cab811053f5e9cf732428de1b78ed180118`
- Branch: `codex/phase16-awg3-family-3-1-spain-pilot-015`
- Existing isolated worktree: `worktrees/phase16-004`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-015`
- Identity: `7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509`
- Manifest SHA-256: `f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74`
- Collector SHA-256: `244601519bdb7fa003af4dcb0eb8140d946cf8239e83b1098b2242d7d22db992`
- Runner SHA-256: `e5551706eb27ff8e5cb3299f7b57ad7f1f55b9d80bb88bcc7501c29f4ba2d983`
- Previous preflight claim: `phase16-spain-preflight-20260827-026` (completed collection, STOP decision, consumed).
- Previous outcome SHA-256: `752ca5c954ce3092ac87a0df90a874f5f67bbaa3a628b82a264b75ed661feb80`
- Diagnostic receipt SHA-256: `8644f4c0296b627533d82f71a843d917da4698a3550a4de34f618475a1b936d1`
- Diagnostic normalized stdout SHA-256: `559fbab5aec0afda366f4232b81bdefc4cf7c71b32e0a32f98820dd9a630667b`

## Accepted scope decision

```text
/GO PHASE16 ONE_NEW_PREFLIGHT_AFTER_OPERATOR_AWG2_TRAFFIC PACKAGE_phase16-awg3-family-3-1-spain-pilot-20260824-015 IDENTITY_7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509 PREVIOUS_PREFLIGHT_OUTCOME_SHA256_752ca5c954ce3092ac87a0df90a874f5f67bbaa3a628b82a264b75ed661feb80 DIAGNOSTIC_STDOUT_SHA256_559fbab5aec0afda366f4232b81bdefc4cf7c71b32e0a32f98820dd9a630667b MAX_HANDSHAKE_AGE_600S ONE_NEW_PREFLIGHT NEXT_EXACT_APPROVE_REQUIRED NO_LOCAL_FIX NO_REMOTE_WRITE NO_STAGE NO_INSTALL AWG2_UNTOUCHED
```

The operator authorized the scope of one new preflight, but explicitly required the next exact approval. No code fix, freshness-policy change, package rebuild or renewed diagnostic is authorized.

The previous diagnostic observed `stale_gt_600` with all other AWG2 health dimensions passing. That historical observation is not current remote-state evidence. The previous outcome and diagnostic allowance remain immutable and consumed.

## Local preparation checks

- Named linked worktree and clean baseline: `pass`
- Package/identity/manifest/collector/runner bindings: `pass`
- Previous STOP outcome and diagnostic canonical-stdout bindings: `pass`
- Pinned local SSH trust bundle: `pass`
- Incomplete local preflight claims: `0`
- Matching Spain SSH processes: `0`
- Candidate next claim at check time: `phase16-spain-preflight-20260827-027`; absent and not reserved.
- New claim created: `false`
- New outcome created: `false`
- New preflight/SSH attempts consumed: `0/1`
- Operator traffic confirmed for this new attempt: `false`
- Exact egress approval received for this new attempt: `false`

Create a fresh short-lived claim only immediately before the separately approved execution. Revalidate claim-ID availability, package bindings and local launch conditions then; never reuse claim 026 or manufacture a PASS from diagnostic evidence.

## Operator traffic sequence

1. Complete this local preparation before asking the operator to enable the unstable VPN.
2. The operator briefly enables the existing Spain AWG2 configuration and generates real traffic; approximately 30–60 seconds is a practical target, not proof of a successful handshake.
3. The operator may disconnect the client VPN and restore stable ordinary connectivity. The unchanged health predicate requires a server-observed positive handshake aged 0–600 seconds, not continuous client connectivity.
4. The operator sends the exact approval below together with confirmation that traffic occurred and the client VPN is disconnected. If approval arrives first, wait for that operator confirmation before egress.
5. Execute one checksum-bound preflight promptly, with no automatic retry. A new STOP remains a STOP and authorizes neither correction nor staging.

## Next exact egress approval

```text
/APPROVE PHASE16 SPAIN READONLY_PREFLIGHT_EGRESS_AFTER_OPERATOR_AWG2_TRAFFIC TO_138.124.181.246 PACKAGE_phase16-awg3-family-3-1-spain-pilot-20260824-015 IDENTITY_7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509 MANIFEST_SHA256_f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74 COLLECTOR_SHA256_244601519bdb7fa003af4dcb0eb8140d946cf8239e83b1098b2242d7d22db992 RUNNER_SHA256_e5551706eb27ff8e5cb3299f7b57ad7f1f55b9d80bb88bcc7501c29f4ba2d983 PREVIOUS_PREFLIGHT_OUTCOME_SHA256_752ca5c954ce3092ac87a0df90a874f5f67bbaa3a628b82a264b75ed661feb80 DIAGNOSTIC_STDOUT_SHA256_559fbab5aec0afda366f4232b81bdefc4cf7c71b32e0a32f98820dd9a630667b ONE_NEW_PREFLIGHT MAX_HANDSHAKE_AGE_600S NO_REMOTE_WRITE NO_STAGE NO_INSTALL AWG2_UNTOUCHED
```

## Safety and phase status

No Spain egress, collector execution, remote write, stage/install/rollback, config generation, issuance, AWG2 operation or local code fix was performed by this scope-preparation step. No tests, package materialization or package verifier were repeated. Only this local scope receipt is added.

- ✅ Task 0 — local baseline.
- ✅ Task 1 — verified immutable package 015.
- ▶️ Task 2 — one new preflight pending operator traffic and exact approval; prior STOP is unchanged.
- ⏳ Task 3 — controlled stage, separate approval required.
- ⏳ Task 4 — one AWG3.1 pilot configuration for ARM/Windows, separate approval required.
- ⏳ Task 4.5 — mandatory AWG2 ↔ AWG3.1 transport-quality A/B gate.
- ⏳ Task 5 — client acceptance.
- ⏳ Task 6 — closeout.

Local receipt commit is within the authorized workflow. Public Git publication remains blocked pending the previously requested informed confirmation; this scope decision does not authorize that publication. Preserve the branch, worktree and immutable packages.

Model profile specified by the active plan: `GPT-5.6 SOL / High`. Recommended next preflight profile: `GPT-5.6 SOL / High`, because the next step is a checksum-bound live read-only gate. This records the plan, not an independently verified runtime model selection.
