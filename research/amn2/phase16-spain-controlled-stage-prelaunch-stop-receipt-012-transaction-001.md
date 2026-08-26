# Phase 16 Spain controlled-stage prelaunch STOP receipt 012 transaction 001

- Recorded: `2026-08-26T12:50:51Z`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-012`
- Package identity: `0db6ff252790130ab1de2cd0adabdcf42237255f8ba8f64e3d6addde1469d92c`
- Manifest SHA-256: `9e7127160ac04a91557e090e8bcbc4e76ba1225a410a2f1c026d7d97ae0478c2`
- Approved state SHA-256: `eeda9be15b1adfb6b07f97911c5ee5de00914e1228a843bc2406f4f66c7a2361`
- Rollback scope SHA-256: `7cd469347f8ebf5158ab66b2898d69d3054260f317bbf49c866438524219093d`
- Transaction: `phase16-spain-stage-20260826-001`
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
- Expected local outcome: `C:\ProgramData\AMN2\phase16\controlled-stage\outcomes\phase16-spain-stage-20260826-001.json`
- Local outcome present: `false`
- Matching SSH processes after stop: `0`
- Matching controlled-stage runner processes after stop: `0`

The SHA-256 of the exact 43-byte UTF-8 stderr token, including its trailing
CRLF, is identical to the observed stderr SHA-256 above.

## Deterministic prelaunch root cause

The immutable package-012 controlled-stage runner dot-sources the preflight
runner. The imported `Assert-Phase16SpainTrustBundle` function requires the
mandatory `ExpectedHost` parameter. At line 146, the controlled-stage runner
invokes only:

```powershell
Assert-Phase16SpainTrustBundle
```

PowerShell parameter binding therefore terminates the runner locally before the
SSH argument builder or SSH process launch is reached. The required forwarding
call is:

```powershell
Assert-Phase16SpainTrustBundle -ExpectedHost $StageExpectedHost
```

This receipt records the defect and does not modify immutable package 012.

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

The only new runtime artifacts are the local protected directories
`C:\ProgramData\AMN2\phase16\controlled-stage` and its `outcomes` child. The
expected outcome file is absent.

## Disposition

The transaction approval is consumed and is not reusable. Package 012 must not
be retried. The next safe action is a new explicit local `/GO` for a TDD
regression and the one-line `ExpectedHost` forwarding fix, followed by one
materialization and one verifier for immutable package 013. No Spain egress,
remote write, stage, or install is authorized by this receipt.
