# Phase 16 Spain read-only preflight STOP receipt 004

- Claim: `phase16-spain-preflight-20260824-006`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-004`
- Package identity: `aec11e7ca78ba6f5f77c55e05506c613c582ec3c1bdb87f4a1338d9e3cac6d48`
- Destination: `root@138.124.181.246`
- Started: `2026-08-24T18:30:28Z`
- Ended: `2026-08-24T18:30:37Z`
- Runner exit: `64`
- Decision: `stop`
- Reason: `transport_failed`
- Transport disposition: `read_only_failed`

## Checksum binding

- Manifest SHA-256: `d19327ccb101febaa4d9cbb7a29cfb6101a62a67554e1c409909f49a3bd9b5c9`
- Collector SHA-256: `cb71fcfff529361c2f9c79cf65b332be884add5309703f76751ff511e36b0842`
- Runner SHA-256: `16475d543fdcf1934b51c58ad47b2f849c17af68badc41bd2313b3063dd6a62f`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`

## Local terminal evidence

- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260824-006.json`
- Outcome SHA-256: `f8710421d88ae689e8c0ab502c59abc7b2b140340e6c7888bea5eeeeb1596af8`
- Terminal claim SHA-256: `989507d1d78c601208470c6d1548afc3b99378b92f16f72bcef1d9260b903c22`
- Canonical failure-contract validation: `pass`
- Matching orphan Spain SSH processes after termination: `0`
- Incomplete transaction artifacts: `0`
- Recovery outcome artifacts: `0`
- Raw remote output persisted: `false`
- Collector document obtained: `false`

## Safety boundary

- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Retry attempted: `false`
- Stage authorization emitted: `false`

The approved single read-only attempt is terminal. The local runner started its bounded SSH transport, but no schema-valid collector document was returned. The evidence does not distinguish connection, authentication, remote command, or collector exit failure, because raw SSH stdout/stderr is intentionally not persisted.

No retry, additional diagnostic egress, server-side repair, application stage, AWG3.1 runtime stage, pilot issuance, or install is authorized by this receipt.
