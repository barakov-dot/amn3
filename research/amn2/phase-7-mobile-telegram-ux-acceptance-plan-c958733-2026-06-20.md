# Phase 7 P7-C010a Mobile Telegram UX acceptance plan for c958733

Date: 2026-06-20.

Status: `completed-mobile-telegram-ux-acceptance-plan-no-live-action`.

Scope: local-only test plan for real-device Telegram-first UX acceptance before
Phase 8. This plan prepares `P7-C010b` but does not open it.

No live VPS/SSH command, Telegram token use/API call/live send, config delivery
payload output, QR/config/import-link generation, public exposure, write
execution, restore/import/reboot, provider mutation, Local Agent mutation or
secret-bearing evidence was performed.

## Reason

Phase 7 reached `rc_ready_paused_private_operator_lane` for AMN2 `c958733`, but
the Telegram-first user channel still needs real-device acceptance. The operator
reported that:

- one-click copy improvements have not yet been verified on the phones;
- QR code import/readability previously failed on both iPhone and Android.

Because Telegram is the intended user-facing channel, real-device Telegram UX is
a release blocker before Phase 8 controlled private launch.

## Gate Split

`P7-C010a` is this local-only planning/evidence step.

`P7-C010b` must be a separate exact named live gate if opened. It may allow:

- Telegram live send only to the operator test chat;
- test-only config/QR/import-link payload only for the selected test identity;
- operator manual checks on iPhone and Android;
- secret-safe pass/fail evidence without pasting QR, `.conf`, import links,
  private keys, PSK, tokens or cookies.

`P7-C010b` must not imply public web/API exposure, provider mutation,
restore/import/reboot, write execution, production user mutation outside the
test scenario, Telegram profile/media mutation or secret-bearing evidence.

## Acceptance Matrix

| Surface | iPhone | Android | Pass condition |
| --- | --- | --- | --- |
| Telegram message layout | pending | pending | Buttons and text are readable, not clipped, and the primary action is clear. |
| One-click copy link | pending | pending | User can copy the intended link/config import value with one tap or the clearest platform-native fallback. |
| QR readability from Telegram image | pending | pending | Device camera or target VPN client can read the QR without zoom/crop hacks. |
| QR readability after opening image full-screen | pending | pending | Full-screen image remains readable and not blurred/compressed beyond use. |
| Fallback `.conf` import | pending | pending | User can import the private config through the fallback path when QR fails. |
| Secret-safe UX | pending | pending | No private key, PSK, raw token or secret-bearing config is exposed in public/evidence channels. |
| Recovery/help text | pending | pending | If QR/copy fails, user sees a clear next action. |

## QR Failure Hypotheses To Check

- QR quiet zone is too small or removed by Telegram preview/cropping.
- QR bitmap is rendered too small for dense AmneziaWG config payloads.
- Telegram image compression or scaling blurs modules.
- Contrast, background or alpha handling reduces scanner reliability.
- Payload is too large for practical QR density; fallback file/import link may
  be the primary mobile path.
- The client expects a different import scheme or raw `.conf` content shape.
- iOS and Android clients handle Telegram media/download permissions
  differently.

## P7-C010b Evidence Rules

Allowed evidence:

- device class: `iphone` / `android`;
- Telegram client/version if the operator chooses to record it;
- target VPN client/version if available;
- pass/fail for each acceptance matrix row;
- safe screenshots only if all secret-bearing payloads are redacted or absent;
- artifact hashes/sizes only for generated test files, if needed.

Forbidden evidence:

- QR image containing a real config;
- `.conf` file contents;
- import links;
- private keys, PSK, tokens, cookies or raw Telegram payloads;
- unredacted screenshots containing secret-bearing config material.

## Recommended Next Exact Gate Text

```text
Открываю P7-C010b Mobile Telegram UX live acceptance gate для AMN2 c958733 на
disposable VPS 89.185.80.166.

Разрешаю Telegram live send только в мой operator test chat и только для
test-only user/device payload, чтобы проверить на реальных устройствах:
- iPhone Telegram + VPN client import;
- Android Telegram + VPN client import;
- one-click copy;
- QR readability in Telegram preview/full-screen;
- fallback .conf import.

Запрещено: public web/API exposure, restore/import/reboot, provider mutation,
write execution, production user mutation вне тестового сценария, Telegram
profile/media mutation и публикация QR/.conf/import-link/private key/PSK/token
в evidence или чат.
```

## Current Phase 7 Status Adjustment

Phase 7 remains `rc_ready_paused_private_operator_lane`, but Phase 8 should not
start until `P7-C010b` is either:

- passed on real devices; or
- explicitly deferred with a documented non-QR fallback policy.
