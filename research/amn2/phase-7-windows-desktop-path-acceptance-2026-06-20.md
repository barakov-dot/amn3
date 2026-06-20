# Phase 7 P7-C010f Windows desktop path acceptance record

Date: 2026-06-20.

Status: `completed-windows-desktop-path-accepted-operator-observation-no-live-action`.

Scope: docs-only operator observation record. No live VPS/SSH, Telegram action,
config output, QR output, `.conf` publication, `vpn://` publication,
restore/import/reboot, provider mutation, write execution or secret-bearing
evidence was performed.

## Operator Observation

The operator reports that the previously issued Windows configuration works
clearly on Windows desktop.

This observation is accepted as Phase 7 desktop-path evidence:

- Windows desktop path: accepted by operator observation.
- Server/base profile viability: not globally broken, because a desktop client
  can connect and function with the issued configuration.
- Mobile blocker interpretation: still valid as a mobile/client compatibility
  problem, not as proof that the AMN2 server/config generation is unusable.

## Boundaries

This does not close mobile acceptance.

Known current state:

- Windows desktop: accepted by operator observation.
- iPhone DefaultVPN: failed functional acceptance and remains
  experimental/unreliable.
- QR: failed the tested mobile flows and remains non-primary.
- Full `vpn://` one-click copy: not practical/reliable for real payload length.
- Android AmneziaWG: still pending real-device acceptance.

## Release Posture

Phase 8 should stay paused unless the launch policy is narrowed explicitly to a
desktop-first/private operator lane.

If mobile user delivery remains required, the next exact gate is still:

```text
P7-C010e Android AmneziaWG real-device acceptance
```

If a desktop-first private RC is acceptable, the next exact gate should be a
policy/status freeze that explicitly says Windows desktop is accepted, iOS is
deferred/experimental and Android is pending.
