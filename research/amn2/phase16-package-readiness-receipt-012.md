# Phase 16 package revision 012 readiness receipt

- Recorded: `2026-08-25T20:59:34Z`
- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-012`
- Package identity SHA-256: `0db6ff252790130ab1de2cd0adabdcf42237255f8ba8f64e3d6addde1469d92c`
- Manifest SHA-256: `9e7127160ac04a91557e090e8bcbc4e76ba1225a410a2f1c026d7d97ae0478c2`
- Collector SHA-256: `1afa57ad1f9725034395bf7455f9275e5fce5e0f651e5755dbba51d71455a979`
- Preflight runner SHA-256: `83ac6857adff3acbbef13416ceb8a31db9221b98ccf86fa64b70cecdb44f3484`
- Resource-plan SHA-256: `6c1eba6a9229cd8aa715a29f3f8c58e14ecc407b4e3373c2fe59f43cd25a1f2f`
- Application stage SHA-256: `f299c112ce9206f49c82d91f4b23ca9dc00b6d83479a3d9399126a56ee7e12e3`
- AWG3.1 runtime stage SHA-256: `0e1b4e628e7f17f0085490c51e43d2a0ceceadfe73b5078c1176fc6b6b82de1f`
- Stage support SHA-256: `26716f2d490d8ada9341bd17093be2c6ae4e63cafa77af2362698a1f41be665d`
- Controlled stage coordinator SHA-256: `5807fd8b920f0967d702a15ebe2accd599738c68a833c4910b98b7b689d7086e`
- Controlled stage SSH runner SHA-256: `040c5e90fc495b38ad5c7744490aeaf67380c9c1fb2410831847c9f72a0f19c2`
- Source-readiness receipt SHA-256: `d4e40d749a82605fb1811136a82f24fac3344f36267dc283bbfaa7684058c740`
- Stage-prerequisite gate evidence SHA-256: `204b95c542bcd2cb5a754e2a0ef53495278885fa540bd9c50406fe7f16a2daac`
- Canonical rollback-scope SHA-256: `7cd469347f8ebf5158ab66b2898d69d3054260f317bbf49c866438524219093d`

## Source and commit binding

- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Application source root: `C:\Users\SooL\Documents\amn2-phase15-local-package-bootstrap-readiness`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-012`
- Approved baseline commit: `f4ad82ba97533f2fa5ee2384b943c03e9d73be13`
- Local stage-coordinator correction commit: `51855a9985499af5fa82ec1fc3a58652e8669c0d`
- Packaged tooling source SHA: `51855a9985499af5fa82ec1fc3a58652e8669c0d`
- Package materialization commit: `09c68ef795c075fb57afa2f7b7c3068cf8668b2a`

## Materialization and verification

- Actual materialization count: `1`
- Separate verifier count: `1`
- Materializer result: `materialized`
- Verifier result: `verified`
- Package identity returned by materializer and verifier: equal
- Manifest entry count: `171`
- Total package file count including manifest: `172`
- Materializer and verifier reported file count: `171`
- Materialization and verifier runtime: Python `3.12.13`; no dependency installation

## Local validation evidence

- Package revision 012 TDD RED: `1 passed, 5 failed, 84 deselected`
- Focused GREEN after the bounded SQLite lifecycle correction: `6 passed, 84 deselected in 0.08s`
- Complete targeted tooling regression on stable Python 3.12: `90 passed in 5.23s`
- Focused post-correction recheck: `6 passed, 84 deselected in 0.15s`
- Bash syntax: pass
- Python compile syntax: pass
- PowerShell parser syntax after the bounded parenthesis correction: pass
- Python coordinator and PowerShell runner rollback-scope hashes: equal
- Pre-commit `git diff --check`: pass
- Added-line secret matches: `0`
- Exact stage-coordinator correction scope: `17` files

## Controlled stage prerequisites

- Current Spain database contract: `/var/lib/amn2-spain/amn2.sqlite3`
- Backup contract: Python SQLite online backup; no `sqlite3` CLI dependency
- Dedicated Spain Docker binary: `/opt/amn2-spain/docker/bin/docker`
- Dedicated Spain Docker socket: `unix:///run/amn2-spain-docker/docker.sock`
- Stage coordinator: checksum/state/rollback bound with mandatory rollback on failure
- AWG3.1 runtime stage: server-only configuration with no peers
- Global AWG3 issuance: disabled
- AWG2 freshness policy: unchanged at `600` seconds

## Historical immutability and safety boundary

- Package 011 manifest SHA-256: `7275a07be0039ef418d52791df5ee9557c5ff00e6e369d35cf80deb17ff4d0fb`
- Package 011 collector SHA-256: `60c312fa42fc34680e348927624b458eb28f0844cc1e72e33f8deb9068af426d`
- Package 011 runner SHA-256: `29edab80f7fad171078ffd51fbcddc0ded06878327919585c4fb81e790514623`
- Package 011 identity SHA-256: `d04679e145551117ce1dcab762304cf54f6b67ea9ca028a5ffc367cdeb507e99`
- Package 011 remained immutable throughout package 012 work
- Spain egress, SSH, remote write, stage, and install during package 012 local work: none
- AWG2 mutations or service operations: none
- Push activity: none

This readiness receipt records one materialized and one separately verified local package. It does not authorize Spain preflight, controlled stage, install, pilot issuance, or global AWG3 issuance.
