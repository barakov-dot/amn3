# Phase 16 Spain read-only preflight STOP receipt 012 claim 020

- Recorded: `2026-08-26T04:32:48Z`
- Claim: `phase16-spain-preflight-20260826-020`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-012`
- Package identity: `0db6ff252790130ab1de2cd0adabdcf42237255f8ba8f64e3d6addde1469d92c`
- Destination approved: `root@138.124.181.246`
- Claim issued: `2026-08-26T04:26:28Z`
- Claim expires: `2026-08-26T04:31:28Z`
- Collector evidence started: `2026-08-26T04:26:29Z`
- Collector evidence ended: `2026-08-26T04:26:41Z`
- Runner exit: `0`
- Decision: `stop`
- Stop reasons: `observation_failed`
- Transport disposition: `read_only_completed`

## Checksum binding

- Manifest SHA-256: `9e7127160ac04a91557e090e8bcbc4e76ba1225a410a2f1c026d7d97ae0478c2`
- Collector SHA-256: `1afa57ad1f9725034395bf7455f9275e5fce5e0f651e5755dbba51d71455a979`
- Runner SHA-256: `83ac6857adff3acbbef13416ceb8a31db9221b98ccf86fa64b70cecdb44f3484`
- Ephemeral future-claim SHA-256: `2d94ae669ef29103e6c106bd6eb442d1e6e96946fdb6d94ced391bb838d913d2`

## Terminal evidence

- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260826-020.json`
- Outcome SHA-256: `509c8c78e2344d0ddb5b500824b37aa015c63aee82220f94e9c4ddc89deb09cd`
- Terminal claim SHA-256: `11c1b5123915e72914b878d118fbf94ca1c2854aa36de3d3842d434a6857b626`
- Exact package-bound Python contract validation: `pass`
- Canonical JSON byte equality: `pass`
- Exact decision binding: `pass`
- Observation count: `23`
- Terminal claim status: `completed`
- Incomplete transaction artifacts: `0`
- Recovery outcome artifacts for claim: `0`
- Matching Spain SSH processes after completion: `0`
- Matching Phase 16 runner processes after completion: `0`
- Raw remote output persisted: `false`

## Observation summary

- `stop`: `awg2_health`
- `present`: `application_state`, `database_state`
- `pass`: 10 observations
- `free`: 9 observations
- `absent`: `recovery_markers_phase14_phase15_phase16`
- Other `stop` or `unknown` observations: none

The normalized outcome identifies only the `awg2_health` observation as blocking. It does not expose which AWG2-health subcheck failed.

## Local differential diagnosis

- The package-011 and package-012 collectors use the same AWG2 owner, container, interface, and latest-handshake validation sequence.
- The freshness predicate is unchanged: at least one latest-handshake timestamp must be positive, not in the future, and no older than `600` seconds.
- Package 011 passed the same observation at `2026-08-25T19:31:03Z` through `2026-08-25T19:31:18Z`; package 012 stopped at `2026-08-26T04:26:29Z` through `2026-08-26T04:26:41Z`.
- This rules out a package-012 AWG2 freshness-policy change as the cause. The exact live subcheck failure remains undetermined from normalized evidence; a stale handshake is only one possible explanation.

## Safety boundary and stage gate

- Approved package-012 runner invocations: `1`
- SSH transport attempts: `1`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Preflight retry attempted: `false`
- Stage authorization emitted: `false`
- Package revision 012 changed: `false`

This schema-valid read-only outcome is terminal for the approved attempt. The preflight allowance is consumed `1/1`; no retry is permitted. Its outcome SHA-256 is evidence of the observed STOP state and is not a stage authorization. No diagnostic egress, server-side repair, controlled stage, install, pilot issuance, config creation, or AWG2 operation is authorized by this receipt. Any further diagnosis requires a separate exact package-, identity-, and outcome-bound read-only approval.
