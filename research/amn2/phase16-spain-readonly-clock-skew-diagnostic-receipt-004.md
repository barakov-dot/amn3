# Phase 16 Spain read-only clock-skew diagnostic receipt 004

- Diagnostic record: `phase16-spain-clock-skew-diagnostic-20260824-009`
- Approved command ID: `DATE_UTC_EPOCH_AND_TIMESYNC_STATUS`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-004`
- Package identity: `aec11e7ca78ba6f5f77c55e05506c613c582ec3c1bdb87f4a1338d9e3cac6d48`
- Failed preflight outcome SHA-256: `f8710421d88ae689e8c0ab502c59abc7b2b140340e6c7888bea5eeeeb1596af8`
- Collector differential stdout SHA-256: `775efff370150d568c664d500f7d30dc64aeeeef42b9bd3e8a0188bebee15a2b`
- Destination: `root@138.124.181.246`
- Local started: `2026-08-24T18:59:37.587Z`
- Local ended: `2026-08-24T18:59:40.477Z`
- Remote UTC: `2026-08-24T18:59:42Z`
- Remote epoch: `1787597982`
- Remote NTP synchronized: `yes`
- SSH exit: `0`
- Timeout: `false`
- Stdout bytes: `77`
- Stderr bytes: `0`

## Checksum and trust binding

- Manifest SHA-256: `d19327ccb101febaa4d9cbb7a29cfb6101a62a67554e1c409909f49a3bd9b5c9`
- Collector SHA-256: `cb71fcfff529361c2f9c79cf65b332be884add5309703f76751ff511e36b0842`
- Runner SHA-256: `16475d543fdcf1934b51c58ad47b2f849c17af68badc41bd2313b3063dd6a62f`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`
- Local package verifier: `verified`; manifest entries: `168`
- Local checksum/identity/trust dry gate: `pass`
- SSH processes before the approved attempt: `0`
- Actual SSH remote-command attempts: `1`
- Collector executions: `0`

## Clock evidence

The SSH round trip was `2.890` seconds. Accounting conservatively for the full local request window and the remote clock's one-second output granularity, the Spain clock was ahead of the local runner clock by an interval of `1.523` to `5.413` seconds. The midpoint estimate is `+3.468` seconds.

The production validator admits `observed_at` only when it is greater than or equal to the local runner `started_at` and less than or equal to its local `ended_at`; it has no clock-skew allowance. The measured positive lower bound is therefore sufficient to make a fresh remote `observed_at` later than the local `ended_at` and fail `observed_at_window`, even though the remote host reports `NTPSynchronized=yes`.

This confirms a relative cross-host clock-skew/validator-tolerance incompatibility. It does not prove that the Spain clock itself requires repair: the diagnostic compares the Spain host with the local Windows runner, and either clock may contribute to the relative offset.

## Safety boundary

- Normalized output only: `true`
- Raw remote output persisted: `false`
- Remote file written: `false`
- Live mutation: `false`
- Preflight retry: `false`
- Diagnostic outcome publication: `false`
- Diagnostic transaction/recovery artifacts: `0`
- Matching orphan SSH processes after termination: `0`
- Stage/install attempted: `false`
- AWG2 changed: `false`

No additional diagnostic egress, clock repair, preflight retry, local production fix, application stage, AWG3.1 runtime stage, pilot issuance, or install is authorized by this receipt. The independent Windows PowerShell 5 stdin BOM transport defect and the collector's real `observation_failed` / `resource_conflict` STOP decision remain separate blockers.
