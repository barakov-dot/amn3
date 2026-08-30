# Phase 16 — official Windows AWG3.1 source-level status

- Recorded: `2026-08-30`
- Status: `no-official-fix-windows-engine-unchanged`
- Scope: official Amnezia GitHub repositories, source and issue metadata only
- Binary download/install/file write during upstream check: `false`
- Live Spain action/server/profile/AWG2 change: `false`

## Decision

No official supported correction for the Phase 16 Windows AWG3.1 failure was
found. AmneziaVPN `5.0.1.5` remains the current stable Windows path, and its
current `dev` branch still uses the same Windows AWG engine as the released
tag. A repeated Windows live run on that unchanged path is not justified by
this evidence.

Task 4A therefore remains failed/blocked. This source readback does not prove
the exact defective source line and does not authorize a downgrade, alternate
client installation, server/profile parameter change, application stage or
general issuance.

## Release and issue state

Official GitHub metadata still reports `5.0.1.5` as the latest non-draft,
non-prerelease release, published `2026-08-21T14:47:49Z`.

Issue `amnezia-client#3043` remains open. At readback it had:

- `13` comments;
- no assignee, milestone or labels;
- no linked branch, pull request or commit;
- no maintainer-confirmed root cause or fix;
- one timeline cross-reference, open issue `#3050`.

All 13 comments were classified by GitHub as
`author_association=NONE`. Issue `#3050` is an additional Windows AWG3.1 speed
report, but it also has no assignee, milestone or linked development. It is
corroborating user evidence, not an accepted correction.

Official sources:

- https://github.com/amnezia-vpn/amnezia-client/releases/latest
- https://github.com/amnezia-vpn/amnezia-client/issues/3043
- https://github.com/amnezia-vpn/amnezia-client/issues/3050

## Tag-to-dev source comparison

The official `5.0.1.5...dev` comparison contained `9` commits and `78` changed
files; the observed `dev` head was
`dddc18129926206a695175d6b9941c39f9c730e0`. None of the changed paths was a
Windows tunnel, daemon, route, Wintun or session implementation path. The only
AWG recipe paths in the comparison were Android and Apple recipes.

The dependency declarations confirm that the Windows data plane did not move:

- tag `5.0.1.5`: `awg-windows/3.1.20260814`, Wintun `0.14.1`,
  `win-split-tunnel/1.2.5.0`;
- current `dev`: the same three Windows dependency versions;
- current official `amneziawg-windows` `go.mod`:
  `amneziawg-go/v3 v3.1.20260814`.

The nine client commits cover Xray/mobile updates, macOS service handling,
Android logging/billing, `wg show` parsing, Linux desktop metadata,
translations and server-country UI data. None supplies a declared or
source-path-matched Windows AWG3.1 transport correction.

Official sources:

- https://github.com/amnezia-vpn/amnezia-client/compare/5.0.1.5...dev
- https://github.com/amnezia-vpn/amnezia-client/blob/5.0.1.5/conanfile.py
- https://github.com/amnezia-vpn/amnezia-client/blob/dev/conanfile.py
- https://github.com/amnezia-vpn/amnezia-client/tree/dev/client/platforms/windows
- https://github.com/amnezia-vpn/amneziawg-windows/blob/master/go.mod

## Related reports and match boundary

Issue `#3073` reports degraded Windows AWG3.1 throughput when `H1-H4` are
ranges. It does not match this pilot: the checksum-bound pilot generator uses
four fixed single values, and the recovery candidate changed only
`Jc/Jmin/Jmax/I1`. No protected profile was opened for this classification.

Issue `#3064` remains unmatched because the Phase 16 watcher proved that the
Windows interface actually received MTU `1280`. Neither report authorizes a
header, MTU, DNS, port, firewall, server or profile change.

Official sources:

- https://github.com/amnezia-vpn/amnezia-client/issues/3073
- https://github.com/amnezia-vpn/amnezia-client/issues/3064

Local classification sources:

- `scripts/vps/phase16_awg31_minimal_pilot.py`
- `scripts/vps/phase16_awg31_client_recovery.py`
- `research/amn2/phase16-arm-jc6-i1-candidate-2026-08-29.md`
- `research/amn2/phase16-windows-awg31-active-route-counter-diagnostic-2026-08-29.md`

## Gate effect

- Task 4A Windows remains `failed/blocked`; route absence is already excluded.
- A Windows retest waits for a new official supported engine/client path or a
  separately approved checksum-bound official build.
- Task 4.5 remains `quality-fail-root-cause-open-strict-ab-incomplete`.
- Task 3B, Task 5 and Task 6 remain blocked.
- General AWG3.1 issuance remains disabled.
- AWG2 remains `UNTOUCHED`.

The upstream API search endpoint reached its anonymous rate limit only after
the issue, timeline and complete compare metadata above had been returned.
Official GitHub web readback independently confirmed the compare count,
dependency declarations and issue development state. No conclusion relies on
the later rate-limited request.
