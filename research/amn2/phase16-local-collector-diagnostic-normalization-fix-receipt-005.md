# Phase 16 local collector diagnostic normalization fix receipt 005

- Recorded: `2026-08-24T20:03:01Z`
- Source fix commit: `c566c63a6ab8c114af6658d04a50103517bb2ad8`
- Source runner SHA-256 after correction: `afc3200abdd49e2ce5046427b363bd10b9523e4f5375e9cee152c16d82003684`
- Scope: local Windows PowerShell 5 diagnostic normalization only
- Spain egress: `false`
- Package materialization/verifier: `0` / `0`

## Root cause and correction

- `Get-Phase16BytesSha256` rejected a zero-length `[byte[]]` during mandatory parameter binding.
- The completed stdin write task returned `System.Threading.Tasks.VoidTaskResult` into the PowerShell output pipeline.
- The byte hashing parameter now explicitly allows an empty collection and returns the canonical SHA-256 of zero bytes.
- Stdin task completion now passes through `Complete-Phase16VoidTask`, which consumes the task result without pipeline output.

## TDD evidence

- RED command: targeted `byte_hash_accepts_empty_array` and `void_task_completion_emits_no_pipeline_output` selection
- RED result: `2 failed, 30 deselected`; failures were the expected empty-array binding error and missing suppressing helper
- GREEN result: `2 passed, 30 deselected in 0.38s`
- Complete Phase 16 tooling regression: `32 passed in 3.95s`
- Windows PowerShell parser errors: `0`
- Git diff check: `0`
- Added-line secret matches: `0`
- Added-line AWG2 matches: `0`

## Immutable package and safety boundary

- Historical package: `phase16-awg3-family-3-1-spain-pilot-20260824-005`
- Package identity: `08e39f4425f0ad433759caabc6cbb5a83fcfd57fde37c3016bde2e05bb2b8306`
- Manifest SHA-256: `0237057d79e45a129198ff15765df89319d9fa6b85366af37036dee2d44137d2`
- Collector SHA-256: `f56841cb701f8bddbe8d5f88f5d6c02d45028ee2191e70dde47f61bdcedce9be`
- Packaged runner SHA-256: `87e3809a208306898f8e5c12e7bf12f2c140ae3c4565912da74c22b101eae7ab`
- Package 005 changed: `false`
- Diagnostic claim `phase16-spain-collector-diagnostic-20260824-010` changed or retried: `false`
- Matching SSH processes after local verification: `0`
- Remote write, preflight retry, stage, install, and AWG2 activity: none

This local correction is not a materialized package and does not authorize additional Spain egress. A new exact diagnostic execution requires a separately checksum-bound artifact or source binding and a new explicit `/APPROVE`.
