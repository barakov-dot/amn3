# Phase 16 Spain read-only preflight STOP receipt 006

- Claim: `phase16-spain-preflight-20260825-011`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-006`
- Package identity: `172aba5925719473056b8d291b8f42fc0ae54e217e11094b54b81ef588efffa4`
- Destination: `root@138.124.181.246`
- Started: `2026-08-25T04:05:15Z`
- Ended: `2026-08-25T04:05:24Z`
- Runner exit: `64`
- Decision: `stop`
- Reason: `transport_failed`
- Transport disposition: `read_only_failed`

## Checksum binding

- Manifest SHA-256: `36c79003e5b5db564380fbb4471d464e5525d2439a5cfbfd2711cd1376421fe0`
- Collector SHA-256: `ed9b645839b50de4fe7fcd0fa7572ba6cbd874c7f7222e3f0f58e5c6da1b42e3`
- Runner SHA-256: `3d96607c7d5b011da1bd7db299861098cd56705a67c41298f9bb3b14244a56ad`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`

## Local terminal evidence

- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260825-011.json`
- Outcome SHA-256: `7f43c8e97168b5291c1c30f41ad2908ce686874b40335cd0f0fbf8c7a77c996d`
- Terminal claim SHA-256: `8a52aed148bb409e037bde045459c0f066a7c9c647f0edadce463bb3e706f689`
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
