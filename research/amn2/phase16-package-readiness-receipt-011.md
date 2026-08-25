# Phase 16 package revision 011 readiness receipt

- Recorded: `2026-08-25T18:48:53Z`
- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-011`
- Package identity SHA-256: `d04679e145551117ce1dcab762304cf54f6b67ea9ca028a5ffc367cdeb507e99`
- Manifest SHA-256: `7275a07be0039ef418d52791df5ee9557c5ff00e6e369d35cf80deb17ff4d0fb`
- Collector SHA-256: `60c312fa42fc34680e348927624b458eb28f0844cc1e72e33f8deb9068af426d`
- Runner SHA-256: `29edab80f7fad171078ffd51fbcddc0ded06878327919585c4fb81e790514623`
- Resource-plan SHA-256: `2b86bf4790e1daab940dc029668f9a82d02c5d03d652bc8640ff53ae93104e65`
- Source-readiness receipt SHA-256: `38cdcf865f56e9a650a4180a552bc4ba67a66fe10cb0da30bb6070ef7aba8439`

## Source and commit binding

- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-011`
- Nft metainfo-contract correction commit: `554572f909eef549fa0c4ac4f8ef997db525f896`
- Package revision binding commit: `718ea670172d26f93700f1f54b3fc2d14afa8be8`
- Source-readiness receipt commit: `3f864f465cd800c9e4e903c704c7b6b0ace9104a`
- Packaged tooling source SHA: `3f864f465cd800c9e4e903c704c7b6b0ace9104a`
- Package materialization commit: `b9e18d0d70749808df8e63dfc89c26deb9c04182`
- Package 010 blockers-differential V6 normalized stdout SHA-256: `0ce16aba1cefa13bfa0d9b7ab4e33fa39158ed555c17c419fd4395f46338a087`
- Package 010 nft-metainfo V7 normalized stdout SHA-256: `703343a0f55de97dd18c6c587b3887ccb14118abfaaa5eb4a20d3f474ad415d1`
- Package 010 nft-metainfo V7 receipt SHA-256: `9a155db4f8f0c7deb325bc204793d88684e58cec1caf771d837f53e284286d12`

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
- Focused nft metainfo-contract RED: `2 failed, 4 passed, 77 deselected in 0.18s`
- Focused nft metainfo-contract GREEN: `6 passed, 77 deselected in 0.12s`
- Package revision binding RED: `8 failed, 1 passed, 75 deselected in 0.45s`
- Package revision binding GREEN: `9 passed, 75 deselected in 0.33s`
- Complete targeted tooling regression: `83 passed in 4.65s`
- `git diff --check`: pass
- Exact parser correction scope: `2` files
- Exact local source/tooling scope before package: `13` files
- Canonical JSON and exact semantic-delta checks: pass
- Collector Bash syntax check: pass
- AWG2 resource-plan control remained exact `"awg2_untouched": true`

## Observed nft metainfo-contract correction

- The nft ruleset top-level `metainfo` object remains restricted to the exact three-key allowlist: `json_schema_version`, `release_name`, and `version`.
- `json_schema_version` admits only a JSON integer and rejects booleans and the previously admitted string form.
- `release_name` and `version` admit only JSON strings.
- Missing keys, extra keys, nulls, arrays, objects, and all other type substitutions fail closed.
- Every other existing firewall contract and target-conflict check remains active.
- AWG2 handshake freshness policy was not changed.
- Only normalized V7 key/type evidence was used; no raw metainfo values were persisted.

## Immutable history and safety boundary

- Historical package: `phase16-awg3-family-3-1-spain-pilot-20260824-010`
- Historical package identity: `0d9367c120b98d85981a8ad591870f84d5ff6544f5c1168d833f3e53a7e4d658`
- Historical manifest SHA-256: `e79ce27b34d175495ff3f5eebb3e19b1a2cbe6c51c47493fab01113fe2a63805`
- Historical collector SHA-256: `da54841074b70b1cdd0c2704ceefa23b81a79cae6c26e70722b7371e728efc45`
- Historical runner SHA-256: `70cb93f165bb4578ee8d5de3bd4cc71b8b54ed66bce34352fc074aff1468742c`
- Package 010 changed: `false`
- Package 011 staging remnants after materialization: `0`
- Matching Spain SSH processes after local verification: `0`
- Spain egress, remote write, stage, install, and AWG2 activity: none

This readiness receipt records one materialized and one separately verified local package. It does not authorize Spain preflight, stage, install, pilot issuance, or global AWG3 issuance.
