# Phase 16 Spain controlled-stage bootstrap-shape diagnostic receipt 013 V1

- Recorded: `2026-08-26T20:10:08Z`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-013`
- Package identity: `9cca04dd98143ff8a2dd7877d882cd53eccd09e4638ac2307cd92d0e31b3441c`
- Manifest SHA-256: `a80cd8d651b80c0fa24bbe26da3c310a7823db368093d5cc7d9f4edbb864ed47`
- Transaction-003 STOP receipt SHA-256: `bb12ad98b5faa35e273fae73b66ab7494409ca9ab13a9972dca5b3590bd61fca`
- Recovery receipt SHA-256: `ba4500201961fb0502cb5cd9f0ad2c15e6bbc2285ca36c191204202152a4ca9c`
- Recovery stdout SHA-256: `588e75e26543719f432258f12b804205ce09f1f48c0ef215b5931a46ed3eab5a`
- Destination: `root@138.124.181.246`
- Command: `PHASE16_CONTROLLED_STAGE_BOOTSTRAP_SHAPE_V1`
- SSH remote command attempts: `1/1`
- Decision: `bootstrap_shape_pass`

## Exact diagnostic binding

- Dummy source length: `196` bytes
- Dummy source SHA-256: `0635930b5e3392ba4b31aafa5e2b657c4f0d51feddc9fe7a6199c6ce4c1097b4`
- Coordinator supplied: `false`
- Package archive supplied: `false`
- Remote filesystem input/output: `false`

The diagnostic used the controlled-stage runner's exact remote Python
bootstrap shape: strict-host-key SSH, `/usr/bin/python3 -I -B -c`, the
8-byte hexadecimal source-length prefix, source SHA-256 verification, and
`compile`/`exec`. The executed source emitted only the normalized schema below
and contained no filesystem or subprocess operations.

## Exact transport evidence

- Started: `2026-08-26T20:09:59.5489980Z`
- Ended: `2026-08-26T20:10:08.2745888Z`
- Elapsed: `8.726` seconds
- Timed out: `false`
- SSH exit: `0`
- Normalized stdout length: `130`
- Normalized stdout SHA-256: `36677d68bb2f726476b347171154bd5bff5793d1358d3f470eef565396907cec`
- Stderr length: `0`
- Stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Exact output schema: `amn2.phase16.controlled-stage-bootstrap-diagnostic.v1`
- Exact result: `bootstrap_shape_pass`
- Remote write performed: `false`
- Matching target SSH processes after completion: `0`
- Raw output persisted: `false`

## Root-cause disposition

The stable bootstrap-shape PASS rules out a persistent error in the stage
runner's base remote-command quoting, source-length prefix, source checksum,
or Python compile/exec mechanism. The earlier transaction-003 STOP also left
no remote stage artifacts, as proved by the bound recovery receipt.

The exact transaction-003 failure class remains unavailable because package
013 collapses every local prelaunch, process-start, stdin-write, transport,
stderr, output-schema, and stage-result failure into one fixed token. A blind
stage retry would therefore provide no bounded diagnostic improvement.

The recommended next step is one local-only TDD correction that records an
allowlisted runner milestone/error class and transport hashes without raw
stderr or secret-bearing values, followed by one new immutable package, one
materialization, and one verifier. Package 013 remains immutable.

This receipt authorizes no further egress, rollback, stage retry, install,
config/peer issuance, general issuance, or AWG2 operation.
