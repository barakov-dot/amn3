# Phase 7 P7-C010b mobile Telegram UX failure and conf-first fix

Date: 2026-06-20.

Status: `completed-code-fix-pending-package-apply-real-device-retest`.

AMN2 fix commit: `6d5cf3e Make Telegram config delivery conf-first`.

Scope: record real-device Telegram UX acceptance failure signals from
`P7-C010b`, root cause, and the AMN2 code fix. No new VPS/package apply was
performed in this evidence step.

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
launcher/runtime was not installed. The next meaningful verification is a new
package/apply/live Telegram UX retest gate for AMN2 `6d5cf3e`.

## Next Gate

Recommended next exact named gate:

```text
P7-C010c AMN2 6d5cf3e package/apply + Mobile Telegram UX retest
```

Scope should include:

- build/upload/apply verified package for `6d5cf3e`;
- restart only loopback web/runtime as needed;
- run loopback API smoke;
- run Telegram getMe/non-polling surface smoke;
- send operator-only test payload to the operator test chat;
- manually verify iPhone/Android:
  - `.conf` import;
  - QR through in-app VPN client scanner;
  - `vpn://` fallback behavior;
- user-facing message clarity.
- iOS DefaultVPN connectivity:
  - whether `.conf` imports successfully;
  - first-connect attempt count before success/failure;
  - exact safe error class shown by the client, without secrets, if visible;
  - whether the phone is on mobile data or Wi-Fi;
  - whether Android/Windows can connect through the same endpoint at the same
    time;
  - whether a DefaultVPN-specific `.conf` template or client selection policy
    is needed.

Still forbidden unless separately opened:

- public web/API exposure;
- restore/import/reboot/provider mutation;
- write execution / installer executor;
- production user mutation outside the test scenario;
- Telegram profile/media mutation;
- pasting QR, `.conf`, import link, private key, PSK, token or secret-bearing
  screenshots into evidence.

## Release Posture

Phase 7 remains `rc_ready_paused_private_operator_lane`, but Phase 8 should not
start until the AMN2 `6d5cf3e` delivery UX is package-smoked and accepted on
real mobile devices, or a documented non-QR `.conf`-first policy is explicitly
accepted.
