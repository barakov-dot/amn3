# Phase 4 Amnezia client compatibility matrix

Дата: 2026-06-11.

## Summary

`P4-AMNEZIA-REFRESH-002` completed as a safe AMN2 local-only slice.

AMN2 branch `codex/amnezia-client-compatibility-matrix`, commit `d2e234f Add Amnezia client compatibility matrix`, was pushed to `amn2` and fast-forwarded into `amn2/codex-vps-test-prep`.

## Inputs

- `research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-11.md`;
- live Telegram screenshots from the operator showing current bot language/header UX;
- AMN2 bot/config delivery state after commits `908cafc` and `59bc266`.

## Implemented

- Added machine-checkable client/import compatibility matrix in `app.vpn.client_compatibility`.
- Covered current AMN2 delivery artifacts:
  - `.conf` file;
  - separate `vpn://` import link;
  - QR image containing `vpn://` payload.
- Marked `.conf` as the reliable fallback, especially for DefaultVPN.
- Marked DefaultVPN QR import as `unreliable`, not universal.
- Included current AmneziaVPN release/platform constraints:
  - Android 9+;
  - Android 7/8 temporarily unavailable;
  - macOS 13+;
  - macOS 10.15-12 temporarily unavailable;
  - Linux GUI dependencies required;
  - Debian 12 / Ubuntu 22.04.x builds temporarily unavailable.
- Bot app-links message now includes short Russian compatibility guidance without raw config material.
- Updated `docs/WEB_PANEL_AND_BOT_SETUP.ru.md` with the compatibility rules.

## Bot header/language asset check

The AMN2 repository currently has no bot-specific header/banner asset and no `/start` language-selection flow matching the operator screenshot.

Observed AMN2 state:

- `DEFAULT_LOCALE = "ru"`;
- English texts exist as fallback;
- `/start` currently renders the main menu directly;
- only `app/web/static/brand-full.jpg` was found as an image asset, and it belongs to the web panel static assets.

Future bot onboarding work should be a separate local-only slice with explicit bot assets:

- start/header image;
- language-selection inline keyboard;
- default Russian selection;
- persistent user locale if/when needed;
- separate assets for support bot and news bot later.

## Verification

RED checks:

- `tests/vpn/test_client_compatibility.py` initially failed because `app.vpn.client_compatibility` did not exist.
- `tests/bot/test_delivery.py::test_app_links_text_includes_client_compatibility_guidance` initially failed because app links text had URLs only and no compatibility guidance.

GREEN checks:

```text
tests/vpn/test_client_compatibility.py: 5 passed
tests/bot/test_delivery.py: 6 passed
focused suite: 69 passed
full AMN2 suite: 650 passed, 1 warning
```

The warning is the existing Starlette TestClient deprecation warning.

## Safety

No live VPS command, SSH command, service restart, deploy, real config delivery by Codex, production peer/user mutation, public exposure, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or upstream code copy was performed.

The new compatibility matrix is local docs/tests/bot-copy support. It does not add routes, write behavior, public delivery or new secret-bearing artifact formats.

Native `.vpn` / Amnezia JSON delivery remains blocked until a separate config-delivery design gate.

## Follow-up recommendation

Next safe local-only product slice: bot onboarding language/header assets, based on the operator screenshot, after the operator provides the bot image assets if they are not already available outside AMN2.

Runtime/toolchain note: AMN2 tests should continue to run under Python 3.12 for now because existing binary dependencies are built for 3.12. A future Python 3.14/system runtime upgrade should be a separate controlled toolchain task with dependency rebuild and full-suite verification.
