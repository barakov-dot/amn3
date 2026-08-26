# Phase 16 Spain controlled-stage prelaunch STOP receipt 013 transaction 002

- Recorded: `2026-08-26T19:31:12Z`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-013`
- Package identity: `9cca04dd98143ff8a2dd7877d882cd53eccd09e4638ac2307cd92d0e31b3441c`
- Manifest SHA-256: `a80cd8d651b80c0fa24bbe26da3c310a7823db368093d5cc7d9f4edbb864ed47`
- Approved state SHA-256: `05cbf76023426f0f6946e549168a6e6ecd7f98a94696f68fe9bd9fec01f5cf28`
- Approval rollback-scope SHA-256: `7cd469347f8ebf5158ab66b2898d69d3054260f317bbf49c866438524219093d`
- Correct package-013 rollback-scope SHA-256: `c70437c363cc822b602d90902d095917041e78044bb299426d7fa01aa8f17d85`
- Transaction: `phase16-spain-stage-20260826-002`
- Destination: `root@138.124.181.246`
- Gate decision: `stop-before-ssh`
- Controlled-stage runner invocations: `1/1`
- Controlled-stage runner exit: `64`
- SSH transport attempts: `0`
- Retry attempted: `false`

## Exact execution evidence

- Runner stdout length: `0`
- Runner stdout SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Runner stderr length: `43`
- Runner stderr SHA-256: `9e650e4049eb870274ee7321d57cca26007736a1136ff2860ba43c9cd89aeb48`
- Exact UTF-8 stderr token: `AMN2_PHASE16_CONTROLLED_STAGE_RUNNER_STOP` followed by CRLF
- Local outcome present: `false`
- Matching SSH processes before and after stop: `0`
- Matching controlled-stage runner processes after stop: `0`

## Deterministic prelaunch root cause

The package inventory contained one unmanifested local cache artifact:
`tooling/scripts/__pycache__/phase16_preflight_contract.cpython-312.pyc`.
It was created by the prior local package-bound Python import, not by the
materializer and not by a remote action. The immutable runner correctly
rejected the package at `package_inventory_invalid` before approval comparison
or SSH process creation.

- Removed artifact SHA-256: `4c0922991b5b27e8b35a6ddc4cf65073901e658d2aee909340db6977e9228de8`
- Removed artifact size: `15341` bytes
- Removal scope: the exact generated file and its then-empty `__pycache__` directory only
- Recoverable: `false`
- Inventory after cleanup: expected `172`; actual `172`; missing `0`; extra `0`
- Package identity and manifest after cleanup: unchanged

A second local comparison then exposed a latent evidence-binding error: the
approval and three package-013 receipts carried package 012's rollback-scope
hash. The package-013 runner correctly computes
`c70437c363cc822b602d90902d095917041e78044bb299426d7fa01aa8f17d85`
because the canonical scope includes the package-specific application release.
The stale approval would therefore also have stopped locally at
`stage_approval_invalid`; SSH still would not have started.

## Remote and rollback safety outcome

- Remote transaction created: `false`
- Remote command attempted: `false`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted remotely: `false`
- Rollback required: `false`; no remote stage began
- AWG2 changed: `false`
- General AWG3 issuance enabled: `false`
- Pilot peer/config created: `false`

## Disposition

Transaction 002 is consumed and must not be reused. The next safe candidate is
`phase16-spain-stage-20260826-003`, bound to the corrected package-013
rollback-scope SHA-256. A local prelaunch with the SSH process-start boundary
replaced by a mandatory test STOP reached `stage_ssh_boundary_reached`, with
SSH process count `0` before and after, no outcome file, and the corrected
rollback-scope hash. It requires a fresh exact approval. This receipt does not
authorize Spain egress, remote write, stage, install, or pilot issuance.
