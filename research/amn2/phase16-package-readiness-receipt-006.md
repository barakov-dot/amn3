# Phase 16 package revision 006 readiness receipt

- Recorded: `2026-08-25T03:43:19Z`
- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-006`
- Package identity SHA-256: `172aba5925719473056b8d291b8f42fc0ae54e217e11094b54b81ef588efffa4`
- Manifest SHA-256: `36c79003e5b5db564380fbb4471d464e5525d2439a5cfbfd2711cd1376421fe0`
- Collector SHA-256: `ed9b645839b50de4fe7fcd0fa7572ba6cbd874c7f7222e3f0f58e5c6da1b42e3`
- Runner SHA-256: `3d96607c7d5b011da1bd7db299861098cd56705a67c41298f9bb3b14244a56ad`
- Resource-plan SHA-256: `4f665e19a529cb2d507c10acdaf41244f6269a4831ab970c5bc164a95dabfae9`
- Source-readiness receipt SHA-256: `f14042a9b0de6db7a6a1b8b0f11fad53477b3b754057854cf82a28c9c7453141`

## Source and commit binding

- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-006`
- Packaged tooling source SHA: `6237c068f88cd64dc9d1d73a4ea0029c42898b2d`
- Diagnostic normalization correction commit: `c566c63a6ab8c114af6658d04a50103517bb2ad8`
- Diagnostic normalization receipt commit: `4b039658ee09636e914af084aee3d8b094f1fdde`
- Package revision binding commit: `4e3c5647faa02df3c2cda889f17a22776ab81e48`
- Source-readiness receipt commit: `6237c068f88cd64dc9d1d73a4ea0029c42898b2d`
- Package materialization commit: `976147d5e789f70c283ee4932a83297e8e2bcdc9`

## Runtime and client identities

- Runtime artifact: `docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d`
- Runtime capabilities: `disable_cookies`, `random_trailers`
- Pilot client artifact: `github:amnezia-vpn/amneziawg-android/releases/v3.1.20260814/AmneziaWG-3.1.202060814.apk@sha256:74f109a948f012e8b90b4055e98bb9bee77bbb8e5d0fe7d5a057dd9698009697`

## Verification evidence

- Materialized manifest entry count: `168`
- Total package file count including manifest: `169`
- Actual materialization count: `1`
- Separate verifier count: `1`
- Verifier result: `verified`
- Package identity returned by materializer and verifier: equal
- Revision 006 focused RED: `6 failed, 1 passed, 26 deselected`; all failures were stale package `005` bindings
- Revision 006 focused GREEN: `7 passed, 26 deselected in 0.30s`
- Complete targeted tooling regression: `33 passed in 3.96s`
- Python AST checks: `3` pass
- Canonical JSON contracts: `4` pass
- Bash syntax checks: `3` pass
- Windows PowerShell parser errors: `0`
- Git diff check: pass
- Added-line secret matches: `0`
- AWG2 resource-plan control remained exact `"awg2_untouched": true`

## Immutable history and safety boundary

- Historical package: `phase16-awg3-family-3-1-spain-pilot-20260824-005`
- Historical package identity: `08e39f4425f0ad433759caabc6cbb5a83fcfd57fde37c3016bde2e05bb2b8306`
- Historical manifest SHA-256: `0237057d79e45a129198ff15765df89319d9fa6b85366af37036dee2d44137d2`
- Historical collector SHA-256: `f56841cb701f8bddbe8d5f88f5d6c02d45028ee2191e70dde47f61bdcedce9be`
- Historical runner SHA-256: `87e3809a208306898f8e5c12e7bf12f2c140ae3c4565912da74c22b101eae7ab`
- Package 005 changed: `false`
- Matching SSH processes after local verification: `0`
- Spain egress, remote write, stage, install, and AWG2 activity: none

This readiness receipt records one materialized and one separately verified local package. It does not authorize Spain preflight, stage, install, pilot issuance, or global AWG3 issuance.
