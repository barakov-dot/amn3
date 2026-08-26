# Phase 16 package revision 013 readiness receipt

- Recorded: `2026-08-26T15:35:01Z`
- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-013`
- Package identity SHA-256: `9cca04dd98143ff8a2dd7877d882cd53eccd09e4638ac2307cd92d0e31b3441c`
- Manifest SHA-256: `a80cd8d651b80c0fa24bbe26da3c310a7823db368093d5cc7d9f4edbb864ed47`
- Collector SHA-256: `39da47ad8776d8c77198f306c387d26e43d70631b435a7fc50f909b855ce8a66`
- Preflight runner SHA-256: `27684b4bc33704d91f3ece34f195d1aa9aba6d6c5f811283323e3560575e366c`
- Resource-plan SHA-256: `bf41fbcdcd7fe4f34cc5cfde125fe4ce6f36804bbe8ca3e426c5dccdb0203938`
- Application stage SHA-256: `70042dc351c315fc842b2042eb984b3b7430b11e21610610471be143680905a4`
- AWG3.1 runtime stage SHA-256: `9dd153aa350b65c737de770ae7697d2fc8c59a663c9b3553c388e7a25052e0a9`
- Stage support SHA-256: `871d2e7ef3926723a35912947886828faeabb576ebfec6a5573064ae5b932098`
- Controlled stage coordinator SHA-256: `02c9c3cdf5184b0d4ed5eb1dbb381634119ab0a0b4cf2c4a2adf7f54c7b2523d`
- Controlled stage SSH runner SHA-256: `50c517f763303b9cdc5cd294fffafcf41c5121ebda74c250d55782bc625b6a8d`
- Source-readiness receipt SHA-256: `9f1156bbd430e0b68f6b7470f963fda3090eafdc5733c7f4aefb5928f09d9980`
- Canonical rollback-scope SHA-256: `7cd469347f8ebf5158ab66b2898d69d3054260f317bbf49c866438524219093d`

## Source and commit binding

- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Application source root: `C:\Users\SooL\Documents\amn2-phase15-local-package-bootstrap-readiness`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-013`
- Stage prelaunch STOP receipt commit: `f079d17fdad067b8b639667e48d49b29fa1d2933`
- Host-forwarding correction commit: `5f6a28d2583ff7b2aa7c8cd5fbaa422111157195`
- Package revision binding and packaged tooling source SHA: `610605df15091682f66942fe5575093f10be1627`
- Package materialization commit: `6cff932c9081fd914ea1aedd163d41fe0ecb01df`

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

- Host-forwarding RED: `1 failed`; the trust assertion was not called because mandatory `ExpectedHost` was omitted
- Host-forwarding GREEN: `1 passed`; exact `StageExpectedHost` reached the trust assertion
- Targeted regression: host-forwarding `1 passed`; plain Phase 16 contract tests `7 passed`
- Python AST: `6 passed`
- Bash syntax: `3 passed`
- PowerShell parser: `2 passed`
- Pre-commit `git diff --check`: pass
- Added-line secret matches: `0`
- Exact package-binding scope: `17` files
- Old active package and tooling-branch binding matches: `0`

The prior pytest runtime recorded for package 012 is no longer present. No
dependency was installed. The package-013 regression therefore used the
available standard-library runtime and the existing plain contract tests; no
claim is made that the unavailable full pytest suite was rerun.

## Controlled stage correction and safety boundary

- Root cause: the controlled-stage runner omitted mandatory `ExpectedHost` when invoking the imported trust-bundle assertion
- Correction: `Assert-Phase16SpainTrustBundle -ExpectedHost $StageExpectedHost`
- Transaction `phase16-spain-stage-20260826-001` was not created
- Stage runner stopped locally with exit `64` before SSH; SSH attempt count was `0`
- Package 012 remained checksum-immutable throughout package 013 work
- Spain egress, SSH, remote write, stage, and install during package 013 local work: none
- AWG2 mutations or service operations: none
- General AWG3 issuance: disabled
- Pilot peer/config created: false
- Push activity: none

This readiness receipt records one materialized and one separately verified
local package. It does not authorize Spain preflight, controlled stage,
install, pilot issuance, or global AWG3 issuance.
