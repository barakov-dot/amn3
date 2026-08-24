# Phase 16 Spain read-only collector differential diagnostic receipt 004

- Diagnostic claim: `phase16-spain-collector-diagnostic-20260824-008`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-004`
- Package identity: `aec11e7ca78ba6f5f77c55e05506c613c582ec3c1bdb87f4a1338d9e3cac6d48`
- Failed preflight outcome SHA-256: `f8710421d88ae689e8c0ab502c59abc7b2b140340e6c7888bea5eeeeb1596af8`
- Destination: `root@138.124.181.246`
- Started: `2026-08-24T18:48:48Z`
- Ended: `2026-08-24T18:48:57Z`
- Timeout: `false`
- SSH/collector exit: `0`

## Checksum binding

- Manifest SHA-256: `d19327ccb101febaa4d9cbb7a29cfb6101a62a67554e1c409909f49a3bd9b5c9`
- Collector SHA-256: `cb71fcfff529361c2f9c79cf65b332be884add5309703f76751ff511e36b0842`
- Runner SHA-256: `16475d543fdcf1934b51c58ad47b2f849c17af68badc41bd2313b3063dd6a62f`
- Previous collector stdout SHA-256: `0e601fad5aabc20f0f1572a46279cb8f2dfbacc13c99dcd69282497775d22469`
- Previous collector stderr SHA-256: `f0c9d9ab158289f1374a50bbd6707619e42dfcf94fcbb455c636081ff6f3859a`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`

## Differential evidence

- Collector stdout bytes: `3623`
- Collector stdout SHA-256: `775efff370150d568c664d500f7d30dc64aeeeef42b9bd3e8a0188bebee15a2b`
- Canonical JSON parse: `pass`
- Collector stderr bytes: `68`
- Collector stderr SHA-256: `f0c9d9ab158289f1374a50bbd6707619e42dfcf94fcbb455c636081ff6f3859a`
- Redacted stderr: `/usr/bin/bash: line 1: ﻿#!/usr/bin/env: No such file or directory\n`
- Blocking reasons: `observation_failed`, `resource_conflict`
- Observation count/order/properties/hashes/states: `pass`; count `23`
- Exact identities, schema, decision enum, and false safety fields: `pass`
- Failed schema checks: `observed_at_window`, `production_validator`
- Raw stdout/stderr persisted: `false`

Observation states in manifest order:

`present,pass,stop,pass,free,free,stop,stop,stop,present,pass,stop,free,pass,pass,absent,stop,pass,free,free,stop,free,stop`

## Root cause

The collector source and packaged artifact both begin with bytes `23212f7573722f62` (`#!/usr/b`) and contain no UTF-8 BOM. A local Windows PowerShell 5 echo probe using the production `Process.StandardInput.BaseStream` pattern returned length `23` for a `20` byte payload and prefix `efbbbf23212f7573`. Therefore Windows PowerShell 5/.NET Framework injects a UTF-8 BOM into the redirected stdin stream before the exact collector bytes.

Remote `/usr/bin/bash -s` interprets the BOM-prefixed shebang as a command, emits the stable 68-byte stderr line, then continues and exits `0`. The production runner requires both exit `0` and stderr length `0`, so it deterministically returns `transport_failed` before parsing the otherwise canonical collector JSON.

`ProcessStartInfo.StandardInputEncoding` is unavailable in the installed Windows PowerShell 5/.NET Framework runtime, so that property cannot be used as a direct local correction.

The collector document also failed only the `observed_at_window` portion of the production schema validator. The approved schema-diff output did not retain the exact remote timestamp, so the magnitude and cause of the apparent clock difference remain unproven.

## Safety boundary

- Actual collector SSH execution count: `1`
- Preflight retry: `false`
- Diagnostic outcome publication: `false`
- Diagnostic claim/lifecycle/transaction/recovery artifacts: `0`
- Matching orphan Spain SSH processes after termination: `0`
- Remote copy/write path: none
- Stage/install attempted: `false`
- AWG2 changed: `false`

No further diagnostic egress, preflight retry, local production fix, application stage, AWG3.1 runtime stage, pilot issuance, or install is authorized by this receipt.
