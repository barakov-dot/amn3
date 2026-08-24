# Phase 16 Spain read-only collector error-class diagnostic receipt 005

- Diagnostic claim: `phase16-spain-collector-diagnostic-20260824-010`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-005`
- Package identity: `08e39f4425f0ad433759caabc6cbb5a83fcfd57fde37c3016bde2e05bb2b8306`
- Failed preflight outcome SHA-256: `29aabab7acd60a2470db305217988581c9ca42dbd2139efb53d89d806ae16b21`
- Destination: `root@138.124.181.246`
- Receipt recorded: `2026-08-24T19:54:02Z`
- Timeout bound: `60s`
- Diagnostic result: `inconclusive_local_normalization_failure`
- Harness process exit: `1`
- SSH/collector exit class: unavailable

## Checksum binding

- Manifest SHA-256: `0237057d79e45a129198ff15765df89319d9fa6b85366af37036dee2d44137d2`
- Collector SHA-256: `f56841cb701f8bddbe8d5f88f5d6c02d45028ee2191e70dde47f61bdcedce9be`
- Runner SHA-256: `87e3809a208306898f8e5c12e7bf12f2c140ae3c4565912da74c22b101eae7ab`
- Pinned host-key enforcement: enabled through the packaged trust-bundle assertion

## Normalized diagnostic evidence

- Exact collector SSH execution count: `1`
- Remote stderr bytes: `0`
- Remote stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Remote stderr token class: `empty`
- Remote stdout bytes/SHA-256/schema: unavailable after bounded-memory cleanup
- SSH/collector exit code: unavailable after bounded-memory cleanup
- Raw stdout/stderr persisted: `false`
- Diagnostic outcome published: `false`

The SSH process and exact collector execution completed before the harness attempted to construct its normalized summary. Summary construction then failed locally while evaluating `Get-Phase16BytesSha256 -Bytes $stderrResult`: Windows PowerShell 5 parameter binding rejects an empty array for the mandatory `[byte[]]` parameter. Evaluation order establishes the zero-byte remote stderr, but the summary was never emitted, and the bounded stdout/stderr arrays were cleared in `finally`. The collector error class therefore cannot be recovered or inferred from this execution.

The console also emitted the local `System.Threading.Tasks.VoidTaskResult` value from the unconsumed stdin task result. This is a harness normalization defect, not remote collector evidence.

## Safety boundary

- Preflight retry: `false`
- Diagnostic retry: `false`
- Diagnostic claim/lifecycle/transaction/recovery artifacts: `0`
- Matching orphan SSH processes after termination: `0`
- Remote copy/write path: none
- Stage/install attempted: `false`
- AWG2 changed: `false`

This receipt deliberately records an inconclusive diagnostic. A corrected diagnostic harness and any additional Spain egress require a new explicit authorization; this execution does not authorize a retry, preflight, stage, install, pilot issuance, or AWG2 activity.
