# Phase 16 package revision 007 readiness receipt

- Recorded: `2026-08-25T04:47:35Z`
- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-007`
- Package identity SHA-256: `5065c10c11f82356f3bcf49432512ffae66fd7ea12b61c98c38c4ff5691af5c2`
- Manifest SHA-256: `24eb848d13845b4a0abf9a8200a6c30d2bd67be28ea904c8e08e1aaf830e312b`
- Collector SHA-256: `c3ca7538c556555121da29e2b361bc3139a6b1e76f579856416259aac7bbca37`
- Runner SHA-256: `7aca3daa62d0552ef533c47cbca68a1c4fcf622156423936183069d0499a9060`
- Resource-plan SHA-256: `ee6ad4b52d7bdf9694b671aa174e81d772f3d1789e22f8f5a6245f4ac7643c2d`
- Source-readiness receipt SHA-256: `65e1cab79090b469b3fe8b6624160a64351469078e111c8846032d345c7dc9b3`

## Source and commit binding

- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-007`
- Package 006 diagnostic receipt commit: `a541737545bd4b5963edbb048d49c10cc22a193c`
- Package revision 007 producer/filter correction commit: `4ba5d80546c55e140d08b4bf1b95d92d654c8111`
- Source-readiness receipt commit: `2cd9c1d49a1276d2708e412fac3d9b543081511f`
- Packaged tooling source SHA: `2cd9c1d49a1276d2708e412fac3d9b543081511f`
- Package materialization commit: `09717685177b7358b9a4407baf73a4c16e003388`

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
- PowerShell 5 producer/filter RED: `2 failed, 31 deselected in 0.50s`
- PowerShell 5 producer/filter GREEN: `2 passed, 31 deselected in 0.50s`
- Revision 007 focused RED: `3 failed, 1 passed, 30 deselected`; failures were stale package `006` bindings
- Revision 007 focused GREEN: `5 passed, 29 deselected in 0.52s`
- Complete targeted tooling regression: `34 passed in 3.64s`
- Python AST and canonical JSON checks: pass
- Bash syntax checks: `3` pass
- Windows PowerShell parser errors: `0`
- Git diff checks: pass
- Added-line secret matches: `0`
- AWG2 resource-plan control remained exact `"awg2_untouched": true`

## Immutable history and safety boundary

- Historical package: `phase16-awg3-family-3-1-spain-pilot-20260824-006`
- Historical package identity: `172aba5925719473056b8d291b8f42fc0ae54e217e11094b54b81ef588efffa4`
- Historical manifest SHA-256: `36c79003e5b5db564380fbb4471d464e5525d2439a5cfbfd2711cd1376421fe0`
- Historical collector SHA-256: `ed9b645839b50de4fe7fcd0fa7572ba6cbd874c7f7222e3f0f58e5c6da1b42e3`
- Historical runner SHA-256: `3d96607c7d5b011da1bd7db299861098cd56705a67c41298f9bb3b14244a56ad`
- Package 006 changed: `false`
- Matching SSH processes after local verification: `0`
- Spain egress, remote write, stage, install, and AWG2 activity: none

This readiness receipt records one materialized and one separately verified local package. It does not authorize Spain preflight, stage, install, pilot issuance, or global AWG3 issuance.
