# Phase 7 P7-C010d iOS/Android client compatibility diagnostic

Date: 2026-06-20.

Status: `completed-compatibility-policy-update-no-live-apply`.

AMN2 compatibility policy commit:
`471bca8 Downgrade DefaultVPN iOS compatibility`.

Scope: local/code/docs diagnostic after `P7-C010c` mobile UX retest. No new
VPS package apply, Telegram live send, config payload output, public exposure,
restore/import/reboot, provider mutation or write execution was performed.

## Inputs

`P7-C010c` established:

- AMN2 `6d5cf3e` package/apply smoke passed on disposable VPS `89.185.80.166`.
- Telegram operator-only test payload send passed.
- Full `vpn://` one-click copy is unavailable for real payload length.
- QR did not pass the tested mobile flows.
- iPhone DefaultVPN failed functional acceptance:
  - first-connect was slow;
  - after toggling VPN off/on, reconnect loops appeared;
  - the tunnel did not provide expected connectivity; Telegram stayed
    unavailable.
- Android device testing is still pending.

## Decision

DefaultVPN iOS is no longer treated as the primary/recommended iOS path for
AMN2 private RC.

AMN2 compatibility matrix was changed to:

- mark DefaultVPN iOS as `experimental_ios`;
- mark DefaultVPN `.conf`, `vpn://` and QR artifacts as `unreliable`;
- add explicit constraints that DefaultVPN was not accepted as primary after
  `P7-C010c` real-device retest;
- update Russian install guidance so users are not told that DefaultVPN is the
  main iOS route.

## Verification

Local syntax verification:

```text
python -m py_compile app\vpn\client_compatibility.py tests\vpn\test_client_compatibility.py
status: passed
```

Full local pytest was not run because the current local Windows Python
environment lacks AMN2 test dependencies. No live VPS action was performed in
this diagnostic step.

## Current Release Posture

Phase 8 remains blocked on mobile client acceptance.

Known state:

- Windows path: previously observed working, but latest `6d5cf3e` test-only
  profile was not rechecked on Windows.
- iPhone DefaultVPN: failed functional acceptance; not a release path.
- iOS AmneziaWG Apple: potential path only if already installed; not RF App
  Store default.
- Android AmneziaWG: intended next mobile candidate; test pending.
- `.conf` remains the primary delivery artifact, but it needs a passing mobile
  client to be release-accepted.
- QR remains non-primary; do not promise QR or phone-camera import.
- `vpn://` remains fallback/convenience only; do not promise one-tap copy for
  full payloads.

## Next Gate

Recommended next exact gate:

```text
P7-C010e Android AmneziaWG real-device acceptance
```

Scope:

- use the already-applied AMN2 `6d5cf3e` or later package-smoked head;
- send operator-only test payload only if needed;
- test Android AmneziaWG `.conf` import and tunnel connectivity;
- test QR only inside the VPN client scanner, if available;
- record safe pass/fail, attempt count, network type and client version if
  available;
- do not paste QR, `.conf`, `vpn://`, keys, PSK, tokens or screenshots with
  secret-bearing payload.

If Android passes, the private RC can proceed as Android/Windows-first with iOS
explicitly experimental/deferred. If Android fails, Phase 7 needs a deeper
client/template compatibility slice before Phase 8.
