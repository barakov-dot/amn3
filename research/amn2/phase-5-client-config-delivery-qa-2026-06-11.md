# Phase 5 P5-M002 client config delivery QA

Date: 2026-06-11.

Status: `completed-docs-only-local-only`.

## Summary

`P5-M002` was completed as an AMN3 docs-only/local-only QA slice.

Created:

- `docs/AMN2_CLIENT_CONFIG_DELIVERY_QA.ru.md`

The checklist covers safe review of AMN2 client delivery instructions for `.conf`, QR, `vpn://`, Android, iOS and Desktop without publishing real secrets or running live delivery.

## Inputs

AMN2 source of truth:

```text
repo: barakov-dot/amn2
branch: codex-vps-test-prep
current head recorded by AMN3: 23f18ef Add external-only backfill rehearsal
```

AMN2 files inspected through GitHub connector read access:

- `app/bot/delivery.py`
- `app/bot/handlers.py`
- `app/vpn/client_compatibility.py`
- `app/vpn/config_templates.py`
- `tests/bot/test_delivery.py`
- `docs/WEB_PANEL_AND_BOT_SETUP.ru.md`

Existing AMN3 inputs:

- `research/amn2/config-delivery-inventory.md`
- `research/amn2/phase-4-bot-config-delivery-localization-2026-06-11.md`
- `research/amn2/phase-4-amnezia-client-compatibility-matrix-2026-06-11.md`
- `research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-11.md`
- `docs/AMN2_OPERATOR_ONLY_SMOKE_CHECKLIST.ru.md`

External reference checked:

- Telegram Bot API `InlineKeyboardButton.copy_text`: `https://core.telegram.org/bots/api#inlinekeyboardbutton`.
- Telegram Bot API `CopyTextButton`: `https://core.telegram.org/bots/api#copytextbutton`.

## Findings

Current AMN2 delivery behavior:

- bot delivery sends the main Russian-first config-ready message;
- `vpn://` is sent as a separate text message;
- app links are sent as a separate text message;
- `.conf` is attached with Russian caption;
- QR image contains the `vpn://` import link;
- `.conf` remains the reliable fallback;
- compatibility guidance does not promise universal DefaultVPN QR support.

Copy-to-clipboard requirement:

- Operator clarification: the bot may send the config import link as a separate message, but the important UX requirement is that a single tap copies that link to the clipboard.
- Current AMN2 does not satisfy this as a proven behavior because the import link is sent as plain message text without an inline copy button.
- Telegram Bot API supports `InlineKeyboardButton.copy_text`, but `CopyTextButton.text` is documented as 1-256 characters.
- AMN2 `vpn://` currently encodes the full UTF-8 `.conf` as URL-safe base64, so real import links are expected to exceed 256 characters.
- Therefore one-tap copy of the full raw `vpn://` link is a required follow-up, but it needs a separate local-only feasibility/implementation slice before it can be promised in user-facing copy.

## Safety Boundary

No AMN2 runtime code was changed.
No bot handler, template, keyboard, delivery package, config generator or tests were changed.
No live Telegram send was performed.
No Telegram token was used.
No real config, QR, `vpn://`, private key, PSK or endpoint was published.
No live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, production peer/user mutation, `/api/clients` CRUD, config delivery, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed.

## Verification

Verification for this AMN3 docs-only slice:

```text
git diff --check: passed
stale active P5-M002/P5-M004 scan: no active-plan/current-next stale matches
historical P5-M006 recommendation scan at P5-M002 closeout: present in forward plan, next-chat handoff, current status, transfer backlog and candidate queue
git diff --cached --check: passed
```

AMN2 local test suite was not run because this slice does not change AMN2 code. Current AMN2 full local suite remains the previously recorded `662 passed, 1 warning` for head `23f18ef`.

## Decision

`P5-M002` is closed as docs-only/local-only QA preparation. It does not treat plain text selection as an acceptable final UX for the operator's copy requirement.

Follow-up status: `P5-M006` Одно нажатие для копирования import-ссылки в Telegram was completed later on 2026-06-11 as AMN2 commit `ad6aa1b`. Evidence: `research/amn2/phase-5-telegram-import-link-copy-2026-06-11.md`.
