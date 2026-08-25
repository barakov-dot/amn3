# Phase 16 Spain read-only preflight STOP receipt 007 claim 014

- Recorded: `2026-08-25T05:05:15Z`
- Claim: `phase16-spain-preflight-20260825-014`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-007`
- Package identity: `5065c10c11f82356f3bcf49432512ffae66fd7ea12b61c98c38c4ff5691af5c2`
- Destination: `root@138.124.181.246`
- Started: `2026-08-25T05:03:09Z`
- Ended: `2026-08-25T05:03:18Z`
- Runner exit: `0`
- Decision: `stop`
- Stop reasons: `observation_failed`, `resource_conflict`
- Transport disposition: `read_only_completed`

## Checksum binding

- Manifest SHA-256: `24eb848d13845b4a0abf9a8200a6c30d2bd67be28ea904c8e08e1aaf830e312b`
- Collector SHA-256: `c3ca7538c556555121da29e2b361bc3139a6b1e76f579856416259aac7bbca37`
- Runner SHA-256: `7aca3daa62d0552ef533c47cbca68a1c4fcf622156423936183069d0499a9060`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`

## Terminal evidence

- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260825-014.json`
- Outcome SHA-256: `ba2aa5e9bb0d52ff9eeb0fd029052150935f2f33786f8c12c889bf1eac1cd348`
- Terminal claim SHA-256: `f3a17ad60de95821c932bf9d099b595a9cb11608089e0fa87600cc1525f55fa4`
- Canonical evidence-contract validation: `pass`
- Observation count: `23`
- Terminal claim status: `completed`
- Incomplete transaction artifacts: `0`
- Recovery outcome artifacts: `0`
- Temporary transaction artifacts: `0`
- Matching Spain SSH processes after completion: `0`
- Persistent claim lock: present as expected audit/serialization state
- Raw remote output persisted: `false`

## Blocking observations

- `awg2_health`: `stop`
- `container_capability`: `stop`
- `container_cidr_172_29_252_0_28`: `stop`
- `container_name`: `stop`
- `firewall`: `stop`
- `routes`: `stop`
- `telegram_prerequisites`: `stop`
- `vpn_cidr_10_212_13_0_24`: `stop`

The evidence also records `os_compatibility`, `python_3_12`, `backup_capability`, `disk_space`, and `service_capability` as `pass`; Phase 14/15/16 recovery markers are `absent`. Free-resource observations do not override any blocking observation.

## Safety boundary

- Actual preflight attempts: `1`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Retry attempted: `false`
- Stage authorization emitted: `false`
- Package revision 007 changed: `false`

This schema-valid read-only outcome is terminal for the approved attempt. Its outcome SHA-256 is evidence of the observed STOP state and is not a stage authorization. No diagnostic egress, server-side repair, controlled stage, install, pilot issuance, or AWG2 operation is authorized by this receipt.
