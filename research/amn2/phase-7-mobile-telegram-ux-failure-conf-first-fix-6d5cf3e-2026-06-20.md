# Phase 7 P7-C010b mobile Telegram UX failure and conf-first fix

Date: 2026-06-20.

Status: `package-smoked-mobile-retest-failed-qr-and-ios-defaultvpn`.

AMN2 fix commit: `6d5cf3e Make Telegram config delivery conf-first`.

Scope: record real-device Telegram UX acceptance failure signals from
`P7-C010b`, root cause, AMN2 code fix, `P7-C010c` package/apply smoke, and
mobile retest result.

## Observed Failure

During `P7-C010b` operator live Telegram UX acceptance, the operator reported:

- one-click copy for the config import link was absent or not practically
  usable;
- QR did not open/import through Amnezia/DefaultVPN on iPhone or Android;
- iPhone with DefaultVPN did not connect on the first attempts, but connected on
  the fourth attempt; Windows client connectivity worked with the tested
  config/server path;
- Telegram user-facing text included test/task wording and was not polished
  enough for a user-facing release flow;
- VPN client guidance needed to be clearer and more presentable.

No QR, `.conf`, `vpn://` import link, private key, PSK, token or secret-bearing
screenshot was pasted into evidence.

## Root Cause

The current Telegram delivery treated `vpn://` and QR as stronger UX paths than
they really are:

- Telegram `copy_text` buttons are only available for short text; real AMN2
  `vpn://` import links are normally longer than the Bot API copy-text limit,
  so a true one-tap copy button cannot be promised for full config payloads.
- The QR code encoded the `vpn://` import link. Phone cameras and VPN clients
  do not reliably register or handle that custom deep link, so scanning the QR
  does not universally open Amnezia/DefaultVPN or import the profile.
- The safest currently verified user path is the attached `.conf` file.
- Windows success and eventual iPhone success mean the server/config path is not
  globally broken, but iOS DefaultVPN first-connect reliability still needs a
  separate compatibility/delivery diagnosis. Likely causes include DefaultVPN
  support limitations for the generated AmneziaWG profile, unsupported AWG
  fields, endpoint/port reachability differences from the phone network,
  client-specific import semantics, first-handshake delay, or unclear user
  feedback during initial connection.

## Code Fix

AMN2 `codex-vps-test-prep` was advanced from `c958733` to:

```text
6d5cf3e Make Telegram config delivery conf-first
```

The fix changes Telegram config delivery UX to:

- make the attached `.conf` file the primary and explicitly recommended
  installation path;
- stop implying that full `vpn://` import links always have one-click copy;
- explain that long `vpn://` links are too long for Telegram copy buttons and
  are a fallback/convenience channel;
- generate QR from the raw `.conf` payload for in-app VPN client scanners
  instead of from the custom `vpn://` deep link;
- explain that normal phone cameras may not open the VPN app from QR;
- make VPN client guidance more user-facing and presentable;
- remove test/task phrasing from the P7-C010b live helper text for future
  operator tests.

## Verification

Local verification completed:

```text
python -m py_compile app\bot\delivery.py tests\bot\test_delivery.py
status: passed
```

Full local pytest was not run in this environment because the available Windows
Python lacks project test dependencies (`pytest`, `aiogram`) and Python 3.12
launcher/runtime was not installed.

`P7-C010c` package/apply smoke was completed on disposable VPS `89.185.80.166`:

```text
package: dist/amn2-vps-update-and-smoke-kit-6d5cf3e.zip
package_sha256: 4C5AA58E44362D7BBBC7815C8F0102B5C52BAB781B7415033B19F83E3AC3C4B2
source_sha256: 19D4F480F740972B124FAC64E9A335C9753D5DCDB9FBC9C84D9BB3923B96EDA4
source_overlay_commit: 6d5cf3ea929f26b6b352ad341bff1dd4bd5a8da5
loopback_api_smoke: passed
telegram_getme_non_polling_smoke: passed
backup_create_verify: passed
backup_artifact_mode: 600
external_public_probes: 3030=000, 3040=000, 80=000, 443=000
```

`P7-C010c` operator-only Telegram live payload send also completed:

```text
telegram_send_message_intro_status=passed
telegram_send_message_import_link_status=passed
telegram_send_message_app_links_status=passed
telegram_send_document_conf_status=passed
telegram_send_photo_qr_status=passed
copy_button_enabled=no
vpn_import_link_bytes=701
qr_png_bytes=4361
secret_values_printed=false
```

Manual real-device retest result reported by the operator:

```text
iPhone network: Wi-Fi
iPhone DefaultVPN .conf import/connect: degraded/fail
iPhone first-connect: connected only after a long wait
iPhone reconnect behavior: after toggling off/on, reconnect loops were observed
iPhone functional tunnel check: failed; VPN did not provide expected connectivity, Telegram stayed unavailable
Android .conf import/connect: pending device availability
Windows same .conf connect: not checked
QR import/open: failed
copy button: not available, expected because vpn:// payload is too long for Telegram copy button
```

## Next Gate

Recommended next exact named gate:

```text
P7-C010d iOS/Android client compatibility diagnostic
```

Scope should include:

- read-only/safe diagnostic of generated config shape;
- compare `amneziawg_v2` fields against DefaultVPN/iOS expectations;
- decide whether iOS DefaultVPN should be removed as the primary iOS path,
  moved to experimental, or given a DefaultVPN-specific template;
- test Android AmneziaWG `.conf` import/connect separately;
- keep `.conf` as the primary delivery artifact only if at least one target
  mobile client passes reliably;
- record only safe error classes, attempt counts, network type and pass/fail
  statuses, never secret payloads.

Still forbidden unless separately opened:

- public web/API exposure;
- restore/import/reboot/provider mutation;
- write execution / installer executor;
- production user mutation outside the test scenario;
- Telegram profile/media mutation;
- pasting QR, `.conf`, import link, private key, PSK, token or secret-bearing
  screenshots into evidence.

## Release Posture

Phase 7 should remain paused before Phase 8 on mobile UX grounds. AMN2
`6d5cf3e` is package-smoked and deployed on the disposable VPS. iPhone
DefaultVPN is not an accepted release path: first-connect was slow, reconnect
loops were observed after toggling, the VPN tunnel did not provide expected
connectivity, and QR still failed. Android remains pending. Before Phase 8,
choose one:

- complete `P7-C010d` client compatibility diagnostic and fix/select a passing
  mobile client path; or
- explicitly ship a non-mobile/desktop-only or Android-only private RC policy,
  if that is acceptable for the product.
