# Phase 5 P5-M006 Telegram import link copy affordance

Date: 2026-06-11.

Status: `completed-amn2-local-only`.

## Summary

`P5-M006` was completed as an AMN2 local-only implementation slice.

AMN2 branch and commit:

```text
branch: codex/telegram-copy-import-link
commit: ad6aa1b Add Telegram import link copy button
source-of-truth branch: codex-vps-test-prep
push: 23f18ef..ad6aa1b codex-vps-test-prep -> codex-vps-test-prep
```

Changed AMN2 files:

- `app/bot/delivery.py`
- `app/bot/handlers.py`
- `tests/bot/test_delivery.py`
- `tests/bot/test_bot_handlers.py`

## Behavior

The bot still sends the `vpn://` import link as a separate Telegram message.

For links that fit Telegram Bot API `CopyTextButton.text`, AMN2 now attaches an inline button named `Скопировать ссылку`. The button copies the exact full `vpn://` text carried by the delivery package.

For links that exceed the supported copy-text limit, AMN2 does not attach the copy button and does not claim one-tap copy behavior. The raw link remains visible in the separate message, with `.conf` and QR artifacts preserved as fallback delivery artifacts.

This keeps the operator clarification intact: sending the link separately is acceptable, but plain-text selection is only a fallback. Universal one-tap copy for full raw `vpn://` links remains blocked when the encoded config exceeds the Bot API copy-text limit and requires a separate config-delivery design gate, such as a short tokenized link, Telegram Web App clipboard flow, or other secret-bearing delivery surface.

## Inputs

AMN3 QA baseline:

- `docs/AMN2_CLIENT_CONFIG_DELIVERY_QA.ru.md`
- `research/amn2/phase-5-client-config-delivery-qa-2026-06-11.md`

External reference checked:

- Telegram Bot API `InlineKeyboardButton.copy_text`: `https://core.telegram.org/bots/api#inlinekeyboardbutton`.
- Telegram Bot API `CopyTextButton.text`: `https://core.telegram.org/bots/api#copytextbutton`.

## Safety Boundary

No live Telegram send was performed.
No Telegram token was used.
No real config, QR, `vpn://`, private key, PSK or endpoint was published.
No live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed.

The slice changed local AMN2 bot delivery code and local tests only.

## Verification

RED before implementation:

```text
tests/bot/test_delivery.py tests/bot/test_bot_handlers.py -q
result: 3 failed, 40 passed
expected failures:
- missing delivery copy-button metadata
- import-link message had no copy markup
```

GREEN after implementation:

```text
tests/bot/test_delivery.py tests/bot/test_bot_handlers.py -q
result: 43 passed

tests/bot tests/services/test_config_delivery.py -q
result: 108 passed

python -m pytest -q
result: 664 passed, 1 warning

git diff --check
result: passed
```

AMN2 final state:

```text
branch: codex-vps-test-prep
head: ad6aa1b Add Telegram import link copy button
working tree: clean
remote: amn2/codex-vps-test-prep at ad6aa1b
```

## Decision

`P5-M006` is closed as an AMN2 local-only feasibility/implementation slice.

The implemented path is safe and bounded: it provides one-tap copy only when the exact full import link fits Telegram's copy-text payload. It deliberately leaves over-limit raw `vpn://` links without a copy button instead of truncating or promising unsupported behavior.

Next safe local-only recommendation: `P5-N002` Полировка текста веб-панели для service-mode и external-only устройств.
