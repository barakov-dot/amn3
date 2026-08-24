# Phase 16 Spain read-only preflight STOP receipt 005

- Claim: `phase16-spain-preflight-20260824-009`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-005`
- Package identity: `08e39f4425f0ad433759caabc6cbb5a83fcfd57fde37c3016bde2e05bb2b8306`
- Destination: `root@138.124.181.246`
- Started: `2026-08-24T19:39:50Z`
- Ended: `2026-08-24T19:39:57Z`
- Runner exit: `64`
- Decision: `stop`
- Reason: `transport_failed`
- Transport disposition: `read_only_failed`

## Checksum binding

- Manifest SHA-256: `0237057d79e45a129198ff15765df89319d9fa6b85366af37036dee2d44137d2`
- Collector SHA-256: `f56841cb701f8bddbe8d5f88f5d6c02d45028ee2191e70dde47f61bdcedce9be`
- Runner SHA-256: `87e3809a208306898f8e5c12e7bf12f2c140ae3c4565912da74c22b101eae7ab`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`

## Local terminal evidence

- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260824-009.json`
- Outcome SHA-256: `29aabab7acd60a2470db305217988581c9ca42dbd2139efb53d89d806ae16b21`
- Terminal claim SHA-256: `908a8a8c2e5475bae051968b1bcd92bb4a3566d194c6e03107c71a798c66bbde`
- Canonical failure-contract validation: `pass`
- Matching orphan Spain SSH processes after termination: `0`
- Incomplete transaction artifacts: `0`
- Recovery outcome artifacts: `0`
- Raw remote output persisted: `false`
- Collector document obtained: `false`

## Safety boundary

- Actual preflight attempts: `1`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Retry attempted: `false`
- Stage authorization emitted: `false`

The approved single read-only attempt is terminal. The local runner started its bounded SSH transport, but no schema-valid collector document was returned. The terminal evidence intentionally does not persist raw SSH stdout or stderr and therefore does not distinguish connection, authentication, remote-command, or collector-exit failure.

No retry, additional diagnostic egress, server-side repair, application stage, AWG3.1 runtime stage, pilot issuance, or install is authorized by this receipt.
