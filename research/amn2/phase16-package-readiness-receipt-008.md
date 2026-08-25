# Phase 16 package revision 008 readiness receipt

- Recorded: `2026-08-25T08:57:18Z`
- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-008`
- Package identity SHA-256: `e1cf967208467acebdfcaaac30557436855b75a92b5154ab41fc3429f747a7c3`
- Manifest SHA-256: `065d3369b8dd11783572365f06f84c6ec3ed207e71c758dea2f1d57a02baf24e`
- Collector SHA-256: `b2e112eec77a3a6c272be8d79c7fd010a8f54ad1f6d833002f76d1fcfba03ada`
- Runner SHA-256: `dfc47725248376a0c3e816a9e8681385c615cf3a713ef7cba079fbfbd8d32828`
- Resource-plan SHA-256: `9cbb5306865c50751b38b0edd9e8f3964d1013e5e6b9a3608f2c896d471014cb`
- Source-readiness receipt SHA-256: `c254570cd63c2a1e2112b7765e2535d03dea4a817a5e7fb2151868513a6f7aec`

## Source and commit binding

- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-008`
- Observed-contract correction commit: `c22a022d1f0a9997e1458da7849d1b887bd493cd`
- Source-readiness receipt commit: `624efee8497da5bf271f51330004d72be7a19d23`
- Packaged tooling source SHA: `624efee8497da5bf271f51330004d72be7a19d23`
- Package materialization commit: `dd9daa810f79b5ac77cfa1eecc385000bcf88750`
- V1 normalized evidence SHA-256: `8b756cb0268e1dfd2293c3a90923b31cf74e119cf3327385dc4bb8702813ba86`
- V2 normalized evidence SHA-256: `75135675fbc7cd080c1b20e3882d99e36901f6620cce7e7ebe1e1789ffdbb4db`

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
- Focused observed-contract RED: `7 failed, 1 passed, 32 deselected`
- Focused observed-contract GREEN: `8 passed, 32 deselected in 0.38s`
- AWG2 classifier literal correction RED: `1 failed, 40 deselected`
- AWG2 classifier literal correction GREEN: `1 passed, 40 deselected in 0.03s`
- Complete targeted tooling regression: `40 passed in 4.07s`
- `git diff --check`: pass
- Exact local source/tooling scope: `13` files
- Added-line secret matches: `0`
- AWG2 resource-plan control remained exact `"awg2_untouched": true`

## Observed-contract correction

- AWG2 interface is exact `awgsp0`; handshake inspection enters both the container mount and network namespaces before invoking `/usr/bin/awg`.
- Docker built-in `host` and `none` networks admit exact null IPAM config as empty, while custom null-IPAM networks still fail closed.
- Route `pref` admits only exact `low`, `medium`, or `high` string values.
- A successful empty iptables backend is classified as no conflict; nonzero, stderr, malformed, and conflicting forms still stop.
- Telegram prerequisite admits only stable exact `active/enabled` before-and-after readback.

## Immutable history and safety boundary

- Historical package: `phase16-awg3-family-3-1-spain-pilot-20260824-007`
- Historical package identity: `5065c10c11f82356f3bcf49432512ffae66fd7ea12b61c98c38c4ff5691af5c2`
- Historical manifest SHA-256: `24eb848d13845b4a0abf9a8200a6c30d2bd67be28ea904c8e08e1aaf830e312b`
- Historical collector SHA-256: `c3ca7538c556555121da29e2b361bc3139a6b1e76f579856416259aac7bbca37`
- Historical runner SHA-256: `7aca3daa62d0552ef533c47cbca68a1c4fcf622156423936183069d0499a9060`
- Package 007 changed: `false`
- Matching Spain SSH processes after local verification: `0`
- Spain egress, remote write, stage, install, and AWG2 activity: none

This readiness receipt records one materialized and one separately verified local package. It does not authorize Spain preflight, stage, install, pilot issuance, or global AWG3 issuance.
