# Phase 11: persistent private Telegram bot service decision for 801f8c3

Date: 2026-07-14.

Decision: `HOLD-DISABLED; GO-LOCAL-HARDENING`.

The successful `PHASE11-TELEGRAM-001` transient smoke proves the private bot
identity, first configured administrator, exact `/start`, one response and the
bounded backlog transition on a private clone. It does not prove that the
ordinary persistent service is safe to enable against production SQLite. The
installed `amneziya-bot.service` must remain inactive and disabled.

This review was read-only. It did not call the Telegram API, start polling,
enable or start the bot service, change SQLite, restart a service, modify a
peer/config/listener, or stop/restart/recreate AWG.

## Bound state

```text
source_branch=codex-vps-test-prep
source_commit=801f8c3406121549eb6a19150be009cfc0ea88d0
production_overlay=801f8c3
regular_bot=inactive_disabled_process_0
web=active_enabled_http_ok_loopback_only
write_gates=false_false
configured_admin_count=2
telegram_api_called=false
database_integrity=ok
database_foreign_key_issues=0
database_tables=15
database_total_rows=88
awg=running_restart_0_peers_12_set_unchanged
scoped_bot_settings_systemd_tests=186_passed
tooling_and_docs_tests=43_passed
diff_check=passed
scoped_security_review=0_findings
```

Production SQLite file, logical and table-count digests match the accepted
post-smoke baseline. The transient state file and private clone/run directory
are absent. AWG retains restart count zero and the accepted 12-peer set digest.

## Why persistent activation remains closed

The ordinary service executes `/opt/amn2/venv/bin/python -m app.main`.
`app.main.run()` constructs the production workflow and the complete bot
dispatcher, then enters `dispatcher.start_polling(bot)` directly. Unlike the
controlled transient runner, this path has no persistent startup contract for:

- expected bot identity;
- absent webhook;
- explicit safe backlog classification before polling;
- fail-closed handling of a non-empty or ambiguous backlog;
- a bounded startup deadline and a durable startup receipt;
- explicit `allowed_updates` binding for the full message/callback surface.

The full dispatcher registers callback and administrative mutation routes. The
false product write gates correctly block live VPS apply and operator device
creation, but they do not make the bot read-only: normal workflows can upsert
users, set locale, create orders, record administrator actions, approve orders,
change templates and perform other production SQLite writes. The service user
has read/write access to the mode `0600` production database.

The effective persistent unit has `Restart=on-failure`, `RestartSec=5`, default
start limiting of five starts per ten seconds, `RuntimeMaxSec=infinity` and no
application watchdog notification. Its sandbox is materially weaker than the
accepted transient unit: `PrivateDevices=no`, `ProtectSystem=no` and
`ProtectHome=no`. Automatic restart can therefore re-enter polling without the
transient identity/webhook/backlog admission checks.

## Required local hardening slice

`PHASE11-TELEGRAM-002A` may proceed locally only. It must produce code, tests,
unit template and an evidence-backed rollout gate with all of these properties:

1. A persistent startup admission function verifies the expected private bot
   identity, webhook absence and an explicit backlog policy before the full
   dispatcher can poll. It must never silently drop pending updates.
2. The complete dispatcher binds an explicit reviewed update set and preserves
   fail-closed authorization for every administrative callback/command.
3. Single-instance ownership, bounded startup timeout and a sanitized startup
   receipt are testable without exposing token, administrator IDs, messages,
   webhook URL or config material.
4. Liveness/watchdog behaviour is explicit and testable. Restart and rate-limit
   policy must not create a tight polling/replay loop.
5. The unit uses a narrowed filesystem/device/home sandbox and grants write
   access only to the paths the persistent workflow actually needs.
6. Tests cover webhook present, backlog empty/non-empty/ambiguous, identity
   mismatch, Telegram timeout, duplicate instance, restart admission and
   graceful stop.
7. Package rollout leaves the regular bot inactive and disabled. Persistent
   activation requires a later exact named live gate with disabled-at-boot
   rollback and complete DB/web/AWG pre/post invariants.

No production activation approval phrase is prepared by this decision.

## Scoped verification

```text
.venv/Scripts/python.exe -m pytest tests/bot tests/config/test_settings.py tests/deploy/test_systemd_templates.py -q
186 passed in 16.89s
```

The read-only production review also repeated the accepted web/listener,
environment, SQLite and AWG checks and a post-transient cleanup audit. All
passed without a Telegram API request.

The final three-path documentation/evidence diff passed whitespace review and
a scoped sensitive-literal/security review. It contains no target address,
token, administrator ID, private key, PSK, config/import payload or raw log.

## Next ordered action

Proceed with `PHASE11-OPS-001` compact runtime/recovery health evidence. The
recommended product follow-up after the P0 evidence/retention sequence is
`PHASE11-TELEGRAM-002A` local persistent admission and unit hardening; it is not
a production bot start.
