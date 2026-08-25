# Phase 16 package revision 010 readiness receipt

- Recorded: `2026-08-25T17:06:08Z`
- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-010`
- Package identity SHA-256: `0d9367c120b98d85981a8ad591870f84d5ff6544f5c1168d833f3e53a7e4d658`
- Manifest SHA-256: `e79ce27b34d175495ff3f5eebb3e19b1a2cbe6c51c47493fab01113fe2a63805`
- Collector SHA-256: `da54841074b70b1cdd0c2704ceefa23b81a79cae6c26e70722b7371e728efc45`
- Runner SHA-256: `70cb93f165bb4578ee8d5de3bd4cc71b8b54ed66bce34352fc074aff1468742c`
- Resource-plan SHA-256: `f35d4f61b69460e337008f51693d38a2bc0926b535492e1969b0de9cdb695f4b`
- Source-readiness receipt SHA-256: `7e4c635c74b7d2357212deb0f1ccedfdf5e1dfcecc0d5399e451839c89dfc7c5`

## Source and commit binding

- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-010`
- Nft match-contract correction commit: `333b8f377b16b7171fd2974b6f52adaefe181f33`
- Source-readiness receipt commit: `d21cc257079ab8b0afcd29bca85598223750a8b8`
- Packaged tooling source SHA: `d21cc257079ab8b0afcd29bca85598223750a8b8`
- Package materialization commit: `094343c35ed2e1b53d82e76f685df215579e7e1a`
- Firewall diagnostic V1 normalized stdout SHA-256: `c33af70389833140b3bed2a335e5486af6a506c330d235ba79dcf9f28b2a4dce`
- Firewall-shape diagnostic V2 normalized stdout SHA-256: `f18812daa9499c90bc0f9bf0a7a06b041c03d4c07613efeede54dc4d08aab3b3`
- Match-selector diagnostic V3 normalized stdout SHA-256: `0ffff73e7f300f6f32ee4c05714f2bd2a853bab510e577bcee4ee9c807b43063`
- Match-value-class diagnostic V4 normalized stdout SHA-256: `85d82743e7c352f986f3a0619a46b10e787d96644ff1ddb88364114cdd8b3303`
- L4-token-shape diagnostic V5 normalized stdout SHA-256: `379f2bdf5ce224f2761b88edaae61f951335abcc456263c2720fd84c312916d1`

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
- Focused nft match-contract RED: `8 failed, 21 passed, 47 deselected in 0.44s`
- Focused nft match-contract GREEN: `29 passed, 47 deselected in 0.29s`
- Package binding RED: `4 failed, 1 passed, 72 deselected in 0.38s`
- Package binding GREEN: `5 passed, 72 deselected in 0.32s`
- Complete targeted tooling regression: `77 passed in 4.51s`
- `git diff --check`: pass
- Exact local source/tooling scope before receipt: `13` files
- Correction added-line secret-like matches: `0`
- Collector Bash syntax check: pass
- AWG2 resource-plan control remained exact `"awg2_untouched": true`

## Observed nft match-contract correction

- `payload / protocol / ip / == / string` admits only bounded lowercase L4 protocol tokens matching `[a-z][a-z0-9+.-]{0,15}`.
- `meta / l4proto / == / string` admits the same bounded token grammar.
- `ct / state / in / array[string]` admits only a nonempty duplicate-free finite connection-state allowlist.
- `ct / status / in / string` admits only a finite connection-status allowlist.
- `meta / oifname / != / string` is admitted while references to `awg3` or `amn2sp3br0` still stop as target-interface conflicts.
- Existing target UDP port, CIDR, and interface conflict checks remain active.
- Unknown selectors, operators, value types, malformed tokens, extra keys, and out-of-bound forms remain fail closed.
- AWG2 handshake freshness policy was not changed.

## Immutable history and safety boundary

- Historical package: `phase16-awg3-family-3-1-spain-pilot-20260824-009`
- Historical package identity: `2a4549c05daca9f3666ffe1babfa17851c93c59cc1b902efe9dca16002d9fe5d`
- Historical manifest SHA-256: `084302df340f4741109103dc7baf94601dd24163406d002b82756fde8d9c80c1`
- Historical collector SHA-256: `80b3347b8787ca1490b40f1763ccff01fb4428233ca4f240c068fd02e35cef15`
- Historical runner SHA-256: `f0d0843c05c341b340dce8721d30f55380b6a8493aff70da7013185875301fbf`
- Package 009 changed: `false`
- Package 010 staging remnants after materialization: `0`
- Matching Spain SSH processes after local verification: `0`
- Spain egress, remote write, stage, install, and AWG2 activity: none

This readiness receipt records one materialized and one separately verified local package. It does not authorize Spain preflight, stage, install, pilot issuance, or global AWG3 issuance.
