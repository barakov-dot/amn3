# Phase 4 bot config delivery localization and DefaultVPN UX fix

Дата: 2026-06-11.

Статус: `implemented-pushed-local-gate-complete`.

AMN2:

```text
repo: https://github.com/barakov-dot/amn2
baseline branch: codex-vps-test-prep
feature branch: codex/bot-russian-config-delivery
commit: 908cafc Localize bot config delivery
```

Upstream reference:

- `research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-11.md`

## Причина

Live Telegram screenshot review showed that config delivery was English-first:

- admin approval text was English;
- user config-ready text was English;
- `.conf` caption was `VPN config file`;
- QR caption was `VPN config QR code`;
- default config message embedded app links in one long block;
- config file name used generic `amneziya-device-N.conf`;
- DefaultVPN QR behavior was not clear to the user.

## Что изменено в AMN2

- Default config-ready template is Russian-first.
- Admin approval and user config-ready messages are Russian-first.
- File and QR captions are Russian-first.
- Bot sends `vpn://` import link as a separate Telegram message.
- Bot sends app links as a separate Telegram message.
- Config/QR filenames are built from device name with safe ASCII fallback.
- New approved devices created by the bot use `Neobyatnaya-AMNZ-{order_id}` as default device name.
- QR payload now follows the visible `vpn://` import link instead of raw config text.
- Message text explicitly tells DefaultVPN users to use attached `.conf` as the reliable fallback if the in-app QR scanner does not accept the QR.
- Existing read-only `/about` web route was added to surface route bindings as a read-only view exemption after full-suite drift detection.

## Проверка

```text
focused bot/config delivery:
tests/bot/test_delivery.py
tests/services/test_config_delivery.py
tests/bot/test_bot_workflows.py
tests/bot/test_bot_handlers.py
result: 62 passed

email delivery regression:
tests/services/test_email_delivery.py
tests/web/test_email_delivery.py
result: 15 passed, 1 StarletteDeprecationWarning

full AMN2 suite:
python -m pytest
result: 630 passed, 1 StarletteDeprecationWarning

git diff --check:
passed
```

Runtime used for tests:

```text
Python: bundled Codex Python 3.12.13
PYTHONPATH: bundled Codex python packages + C:\Users\SooL\Documents\Amneziya\.codex_deps + current AMN2 worktree
```

System Python 3.14 was not used for final verification because existing binary dependencies in `.codex_deps` failed to import under that ABI.

## Safety boundary

No live VPS commands were run.
No SSH command was run.
No live bot restart/deploy was performed.
No real config was delivered by Codex.
No production user/peer was mutated.
No public API `3040`, direct public web/admin `3030`, domain/Caddy/HTTPS cutover, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or token issue/revoke route was added.
No upstream GPL/source code was copied.

## Operational note

AMN2 `codex-vps-test-prep` now points to `908cafc`, while earlier VPS rebuild package evidence was built from `1508e3c`. Before any future VPS package apply or rebuild, rebuild the package from the current selected AMN2 head and rerun source/package precheck.

## Recommendation

Next safe local-only slice: `P4-AMNEZIA-REFRESH-002` client import compatibility matrix. It should document and test expected behavior separately for `.conf`, `vpn://`, QR image payload and future native `.vpn`/Amnezia JSON formats without using real secrets or copying upstream code.
