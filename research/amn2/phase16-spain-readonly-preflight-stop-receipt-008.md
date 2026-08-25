# Phase 16 Spain read-only preflight pre-transport STOP receipt 008

- Recorded: `2026-08-25T10:21:52Z`
- Claim: `phase16-spain-preflight-20260825-015`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-008`
- Package identity: `e1cf967208467acebdfcaaac30557436855b75a92b5154ab41fc3429f747a7c3`
- Destination approved: `root@138.124.181.246`
- Claim issued: `2026-08-25T10:11:37Z`
- Claim expired: `2026-08-25T10:16:37Z`
- Runner exit: `64`
- Runner token: `AMN2_PHASE16_PREFLIGHT_RUNNER_STOP`
- Decision: `stop`
- Transport disposition: `not_run`

## Checksum binding

- Manifest SHA-256: `065d3369b8dd11783572365f06f84c6ec3ed207e71c758dea2f1d57a02baf24e`
- Collector SHA-256: `b2e112eec77a3a6c272be8d79c7fd010a8f54ad1f6d833002f76d1fcfba03ada`
- Runner SHA-256: `dfc47725248376a0c3e816a9e8681385c615cf3a713ef7cba079fbfbd8d32828`
- Readiness receipt SHA-256: `31a6964505498e4686f93ba2afd66cd7ea234c01dd68fcc1dbfc8f8550139c52`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`

## Terminal local evidence

- Runner invocations: `1`
- SSH transport attempts: `0`
- Outcome artifact created: `false`
- Claim lifecycle artifact created: `false`
- Transaction artifact created: `false`
- Recovery outcome artifact created: `false`
- Persistent claim or outcome lock created for claim 015: `false`
- Matching claim-owned residue after STOP: `0`
- Matching Spain SSH processes after STOP: `0`
- Ephemeral future-claim removed: `true`
- Package checksums after STOP: unchanged
- Tooling worktree after privileged verification: clean

The absence of the claim lifecycle, transaction, lock, outcome, and recovery artifacts places the STOP before the per-claim transaction boundary and before SSH startup. The runner intentionally emits only the bounded STOP token at this boundary, so the exact inner exception is not recoverable from the terminal execution.

## Local postmortem decomposition

The following gates were evaluated independently in Windows PowerShell 5 without invoking runner main and without SSH:

- packaged manifest canonical read and approved SHA-256: pass
- packaged collector read, manifest entry, and approved SHA-256: pass
- pinned Spain trust bundle, owner ACLs, and host key: pass
- reconstructed claim-015 canonical JSON, exact identity, and validity at runner start: pass
- protected production state root and exact outcome parent: pass
- outcomes namespace lock acquisition after the terminal attempt: pass

This establishes a fail-closed pre-transport STOP but does not justify assigning an unobserved specific exception or retrying the approved attempt.

## Safety boundary

- Spain egress performed: `false`
- Remote command executed: `false`
- Remote file written: `false`
- Raw remote output persisted: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Retry attempted: `false`
- Stage authorization emitted: `false`
- Package revision 008 changed: `false`

The approved runner invocation is terminal. Package revision 008 remains checksum-bound and unchanged, but any new preflight invocation requires a new exact checksum-bound approval. No diagnostic egress, controlled stage, install, pilot issuance, or AWG2 operation is authorized by this receipt.
