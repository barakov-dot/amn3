# Phase 16 Spain read-only collector error-class diagnostic receipt 006

- Diagnostic claim: `phase16-spain-collector-diagnostic-20260825-012`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-006`
- Package identity: `172aba5925719473056b8d291b8f42fc0ae54e217e11094b54b81ef588efffa4`
- Failed preflight outcome SHA-256: `7f43c8e97168b5291c1c30f41ad2908ce686874b40335cd0f0fbf8c7a77c996d`
- Destination: `root@138.124.181.246`
- Started: `2026-08-25T04:25:31Z`
- Ended: `2026-08-25T04:25:35Z`
- Timeout: `false`
- SSH/filter exit: `65`

## Checksum binding

- Manifest SHA-256: `36c79003e5b5db564380fbb4471d464e5525d2439a5cfbfd2711cd1376421fe0`
- Collector SHA-256: `ed9b645839b50de4fe7fcd0fa7572ba6cbd874c7f7222e3f0f58e5c6da1b42e3`
- Runner SHA-256: `3d96607c7d5b011da1bd7db299861098cd56705a67c41298f9bb3b14244a56ad`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`

## Normalized diagnostic evidence

- Exact collector SSH envelope attempts: `1`
- Harness attempts: `1`
- Local harness error class: `none`
- Bounded output exceeded: `false`
- SSH/filter stderr bytes: `0`
- SSH/filter stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Stderr token: `empty`
- SSH/filter stdout bytes: `0`
- SSH/filter stdout SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Output schema validation: `false`
- Normalized collector document: unavailable
- Raw stdout/stderr persisted: `false`
- Diagnostic outcome published: `false`

## Root cause

The packaged remote stdin filter has one explicit exit `65`: it requires the first three stdin bytes to be the UTF-8 BOM `EF BB BF`, strips those bytes, and only then forwards the remaining collector bytes to `/usr/bin/bash -s`.

The package 006 collector artifact starts directly with `#!/usr/bin/env bash`, and the runner's `Read-Phase16CollectorArtifact` returns those exact artifact bytes. This diagnostic reproduced exit `65` with zero stdout and zero stderr. Therefore the actual process transport supplied no leading BOM, the fail-closed filter stopped before forwarding the collector artifact, and no collector schema document could be produced.

The existing unit test proves the filter's behavior for synthetic BOM-prefixed and unprefixed inputs, but it does not cover the real producer-to-filter path used by `Process.StandardInput.BaseStream.WriteAsync`. The producer/filter contract is therefore incomplete. This receipt does not authorize removing the filter or retrying with modified input.

## Safety boundary

- Preflight retry: `false`
- Diagnostic retry: `false`
- Diagnostic claim/lifecycle/transaction/recovery artifacts: `0`
- Matching orphan SSH processes after termination: `0`
- Remote copy/write path: none
- Remote file written: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`

No additional diagnostic egress, preflight retry, production fix, package materialization, application stage, AWG3.1 runtime stage, pilot issuance, install, or AWG2 activity is authorized by this receipt.
