# Phase 6 iOS AmneziaWG Field Diagnostic

Date: 2026-06-13.

Scope: local-only review of user-provided iPhone AmneziaWG screenshots and local
phone app log. No live VPS command, SSH command, deploy/restart/package apply,
public exposure, config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive VPS/provider
action, Telegram token use, live bot send, Telegram profile mutation,
secret-bearing evidence publication or upstream/GPL code copy was performed.

## Inputs

- iPhone AmneziaWG app log:
  `C:\Users\SooL\Downloads\amneziawg-log-2026-06-13T125738Z.txt`
- iPhone screenshots showing an existing `usa` profile, handshake wait and a
  `timed out after 12 seconds` connection error.
- Telegram-delivered QR screenshot captioned as a `vpn://` import-link QR.

## Safe Findings

- The existing iPhone AmneziaWG profile is syntactically accepted by the app and
  starts the tunnel.
- On 2026-06-13 the log contains repeated tunnel activation attempts for the
  same profile and no fresh successful handshake.
- The client sends handshake packets; transmitted byte counters increase.
- The receive byte counter remains zero during the attempts.
- `last_handshake_time_sec` remains `0`.
- Each observed connection attempt fails with `timedOut(12.0)`.
- The log shows a resolved endpoint and peer setup, but this evidence file does
  not publish the endpoint, peer key, QR payload, `.conf` or `vpn://` content.

Interpretation: the old imported profile failure looks more like a reachability,
live server, UDP/firewall, endpoint/port, server public key, or peer-applied-state
problem than a local config syntax error. It is not proven without a named live
diagnostic gate.

## Separate Issue: New Import

The user also reported that a newly created config does not add/import into the
AmneziaWG iPhone app. That is separate from the old profile handshake timeout:

- the old profile imports and starts, then fails handshake;
- the new QR/`vpn://` import may be a payload format, app compatibility, QR scan
  path, link length, or client-version issue.

AMN2 currently treats `.conf` delivery as the canonical fallback and does not
promise that every QR/`vpn://` importer accepts the payload.

## Bot Copy Button Note

Local AMN2 code has a one-tap Telegram copy button for `vpn://` import links, but
it is intentionally bounded. The button is only included when the exact link
fits the Telegram copy-text length limit. A missing copy button can therefore be
expected for long import links and does not by itself prove that the live VPS bot
is stale.

The current local AMN2 head is newer than the latest VPS-smoked/package head; a
final VPS update gate should still verify the actual live bot package/source head
before applying any package or restart.

## Compatibility Matrix To Add

`P6-M004` should document and test separate client paths:

- iOS DefaultVPN: primary RF-available iOS path.
- iOS AmneziaWG: installed/legacy-client path for users who already have it.
- Android AmneziaWG: separate supported-client path.
- Fallback hierarchy: `.conf` first, then QR/`vpn://` where verified for that
  client/version.

## Added Plan Item

Added to active Phase 6 plan:

- `P6-M004` iOS AmneziaWG import/connectivity diagnostic boundary, important
  priority, carried from Phase 6 field evidence on 2026-06-13.

Default allowed scope: local-only logs, docs, tests and compatibility policy.

Still gated: live VPS reachability probes, SSH, service restart, package
apply/rebuild, public exposure, config delivery, production peer/user mutation,
firewall/provider changes, Telegram live sends and raw QR/`vpn://`/`.conf`
publication.
