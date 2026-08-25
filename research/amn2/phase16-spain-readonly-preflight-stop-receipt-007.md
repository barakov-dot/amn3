# Phase 16 Spain read-only preflight pre-transport STOP receipt 007

- Recorded: `2026-08-25T04:58:33Z`
- Claim: `phase16-spain-preflight-20260825-013`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-007`
- Package identity: `5065c10c11f82356f3bcf49432512ffae66fd7ea12b61c98c38c4ff5691af5c2`
- Destination approved: `root@138.124.181.246`
- Claim issued: `2026-08-25T04:56:23Z`
- Runner exit: `64`
- Runner token: `AMN2_PHASE16_PREFLIGHT_RUNNER_STOP`
- Decision: `stop`
- Transport disposition: `not_run`

## Checksum binding

- Manifest SHA-256: `24eb848d13845b4a0abf9a8200a6c30d2bd67be28ea904c8e08e1aaf830e312b`
- Collector SHA-256: `c3ca7538c556555121da29e2b361bc3139a6b1e76f579856416259aac7bbca37`
- Runner SHA-256: `7aca3daa62d0552ef533c47cbca68a1c4fcf622156423936183069d0499a9060`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`

## Root cause and local terminal evidence

- Runner invocations: `1`
- SSH transport attempts: `0`
- The local orchestration wrapper appended the literal two-byte suffix `60-6e` instead of the canonical JSON LF suffix `0a` to the ephemeral future-claim.
- The checksum-bound runner rejected the non-canonical claim before initializing the transaction or starting SSH.
- Outcome artifact created: `false`
- Claim lifecycle artifact created: `false`
- Transaction or recovery artifact created: `false`
- Matching Spain SSH processes after STOP: `0`
- Ephemeral malformed claim removed: `true`
- Package checksums after STOP: unchanged
- Tooling worktree after STOP: clean

## Safety boundary

- Spain egress performed: `false`
- Remote command executed: `false`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Retry attempted: `false`
- Stage authorization emitted: `false`

The approved runner invocation is terminal. Package revision 007 remains unchanged and ready for a new checksum-bound approval. No retry, diagnostic egress, stage, install, pilot issuance, or AWG2 operation is authorized by this receipt.
