# Phase 16 package revision 009 readiness receipt

- Recorded: `2026-08-25T11:39:05Z`
- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-009`
- Package identity SHA-256: `2a4549c05daca9f3666ffe1babfa17851c93c59cc1b902efe9dca16002d9fe5d`
- Manifest SHA-256: `084302df340f4741109103dc7baf94601dd24163406d002b82756fde8d9c80c1`
- Collector SHA-256: `80b3347b8787ca1490b40f1763ccff01fb4428233ca4f240c068fd02e35cef15`
- Runner SHA-256: `f0d0843c05c341b340dce8721d30f55380b6a8493aff70da7013185875301fbf`
- Resource-plan SHA-256: `9def1aeb5ea824131ba43279ae220d49134562d3a0ee23138354acb8d9b9b26b`
- Source-readiness receipt SHA-256: `e539ca049feb27b037b98fa2ae74736ad2a61e41099432349708dccdd3f91672`

## Source and commit binding

- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-009`
- Firewall-contract correction commit: `13697d28a12678dfcd45797297d97af01b80eb0f`
- Source-readiness receipt commit: `162cccdf14fcdb1c5208a3128ed7a29a1e621eec`
- Packaged tooling source SHA: `162cccdf14fcdb1c5208a3128ed7a29a1e621eec`
- Package materialization commit: `6834743f5e391e2be101f8ce4e19bc541491f005`
- Firewall diagnostic V1 normalized stdout SHA-256: `dbffa1c71645d633423d1e05c4d0bca9d0d15bc1142131bbe83028dd99a1e4c0`
- Firewall-shape diagnostic V2 normalized stdout SHA-256: `e192f9b9f86177961644a186d2ae6a02eed10edb23831d071ef0195a4a12a05d`

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
- Focused firewall-contract RED: `5 failed, 11 passed, 41 deselected in 0.34s`
- Focused firewall-contract GREEN: `16 passed, 41 deselected in 0.16s`
- Complete targeted tooling regression: `58 passed in 4.83s`
- `git diff --check`: pass
- Exact local source/tooling scope before receipt: `13` files
- Added-line secret matches: `0`
- AWG2 resource-plan control remained exact `"awg2_untouched": true`

## Observed firewall-contract correction

- `nft` DNAT admits only exact `addr:string`, `family:string`, and `port:int`, validates IP-family consistency, and continues to stop on target CIDR or UDP `30002` references.
- `nft` limit admits only exact bounded `burst:int`, `per:string`, and `rate:int`.
- `nft` masquerade admits only exact null payload.
- `nft` xt admits only exact bounded `name:string` and `type:string`.
- Successful iptables output is admitted without conflict only when it is one bounded printable ASCII comment line.
- Missing, extra, malformed, wrong-type, out-of-range, non-comment, stderr, nonzero, unknown, or conflicting forms remain fail closed.
- AWG2 handshake freshness policy was not changed; a real fresh AWG2 client handshake is still required before the next preflight.

## Immutable history and safety boundary

- Historical package: `phase16-awg3-family-3-1-spain-pilot-20260824-008`
- Historical package identity: `e1cf967208467acebdfcaaac30557436855b75a92b5154ab41fc3429f747a7c3`
- Historical manifest SHA-256: `065d3369b8dd11783572365f06f84c6ec3ed207e71c758dea2f1d57a02baf24e`
- Historical collector SHA-256: `b2e112eec77a3a6c272be8d79c7fd010a8f54ad1f6d833002f76d1fcfba03ada`
- Historical runner SHA-256: `dfc47725248376a0c3e816a9e8681385c615cf3a713ef7cba079fbfbd8d32828`
- Package 008 changed: `false`
- Matching Spain SSH processes after local verification: `0`
- Spain egress, remote write, stage, install, and AWG2 activity: none

This readiness receipt records one materialized and one separately verified local package. It does not authorize Spain preflight, stage, install, pilot issuance, or global AWG3 issuance.
