# Phase 16 — official Windows AWG3.1 upstream status

- Recorded: `2026-08-29`
- Status: `latest-release-no-fix-windows-blocker-open`
- Scope: official GitHub metadata and issue status only
- Download/install/live Spain action: `false`
- Server/profile/AWG2 changed: `false`

## Official release path

The official `amnezia-vpn/amnezia-client` `releases/latest` endpoint resolves
to `5.0.1.5`. GitHub release metadata reports:

- tag/name: `5.0.1.5`;
- `draft=false`;
- `prerelease=false`;
- published: `2026-08-21T14:47:49Z`;
- Windows x64 asset: `AmneziaVPN_5.0.1.5_windows_x64.exe`.

No asset was downloaded. The installed Windows 11 client is already this exact
version. Canonical Phase 16 documents must therefore record
`release_kind=stable`, not `prerelease`. This metadata correction does not turn
failed client compatibility evidence into a PASS and does not permit general
acceptance.

Official sources:

- https://github.com/amnezia-vpn/amnezia-client/releases/latest
- https://github.com/amnezia-vpn/amnezia-client/releases/tag/5.0.1.5
- https://api.github.com/repos/amnezia-vpn/amnezia-client/releases/latest

## Issue and development status

Official issue `amnezia-client#3043` remains open. At readback it had 13
comments, no assignee, milestone, linked branch or pull request, and no
maintainer-confirmed root cause or fix. All 13 comments had GitHub
`author_association=NONE`; they are corroborating user reports, not maintainer
acceptance evidence.

The official compare from `5.0.1.5` to `dev` remains nine commits ahead. The
published commit messages contain `wg show` parsing and unrelated platform/app
changes, but no declared Windows AWG3.1 data-plane or MTU correction. Commit
message inspection alone cannot prove that no internal line changed; the
supported conclusion is narrower: upstream has published no newer release,
linked fix or supported remediated Windows path.

Official sources:

- https://github.com/amnezia-vpn/amnezia-client/issues/3043
- https://api.github.com/repos/amnezia-vpn/amnezia-client/issues/3043
- https://github.com/amnezia-vpn/amnezia-client/compare/5.0.1.5...dev
- https://api.github.com/repos/amnezia-vpn/amnezia-client/compare/5.0.1.5...dev

## MTU report does not match this pilot

A user comment on issue `#3043` links issue `#3064`, which reports a desktop
fallback MTU of `1376` and recovery after forcing `1280`. Issue `#3064` is also
open and has no assignee, milestone or linked pull request.

That failure class does not match the Phase 16 Windows evidence: the AmneziaVPN
service log established that the actual Wintun interface received MTU `1280`,
yet IPv4/DNS/HTTPS application traffic still failed and disabling kill switch
did not restore it. Therefore issue `#3064` is not a bounded correction for this
pilot and does not authorize another MTU, profile or server change.

Official source:

- https://github.com/amnezia-vpn/amnezia-client/issues/3064

Local evidence:

- `research/amn2/phase16-windows-awg31-data-plane-regression-2026-08-29.md`

## Decision

- Keep the installed AmneziaVPN `5.0.1.5`; no downgrade is indicated.
- Do not download or install the standalone native client as a substitute for
  the supported AmneziaVPN path.
- Keep Task 4A failed/blocked until an official upstream fix or separately
  approved checksum-bound supported build passes a bounded retest.
- Keep Task 3B, Task 5 and Task 6 blocked; Task 4.5 remains failed/incomplete.
- Keep general AWG3 issuance disabled and AWG2 untouched.

Immutable package copies preserve their historical text and are not rewritten
by this receipt-only correction. Canonical plan/spec documents carry the
current release classification and gate.
