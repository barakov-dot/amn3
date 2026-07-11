# Phase 10 private Telegram controlled polling TTL gate review

Date: 2026-07-11.

Decision:

```text
direct_app_main_polling=STOP
transient_single_admin_clone_db_smoke=HOLD-UNTIL-HARDENING
local_hardening_slice=APPROVE
persistent_service_activation=STOP
```

This gate performed local engineering verification and a read-only VPS
preflight. It did not call the Telegram Bot API, start polling, change a
service, send a message or mutate VPS data.

## Engineering Finding

`app.main.run()` creates the complete production dispatcher and calls
`dispatcher.start_polling(bot)` without an internal deadline, sender allowlist
or update-type restriction. The dispatcher includes both message commands and
all user/admin callback routes.

The `/start` route is not database read-only. It calls
`BotWorkflow.register_user()`, which uses `Repository.upsert_user()` and updates
the existing user's identity fields and `updated_at`. Running the current unit
against the production database therefore cannot satisfy the reviewed
mutation boundary even if an external watchdog stops it after 180 seconds.

An outer TTL alone also cannot prevent an unrelated message or callback that
arrives during the window from being consumed by the full dispatcher.

Focused verification:

```text
pytest_scope=tests/bot/test_app_bootstrap.py|tests/bot/test_bot_factory.py|tests/bot/test_bot_handlers.py::test_handle_start_sends_header_and_language_choices_with_russian_default
pytest_result=12_passed
```

## Read-Only VPS Preflight

```text
source_overlay=34b3b43
bot_active=inactive
bot_enabled=disabled
bot_process=false
web_active=active
web_login_http=200
systemd_version=255
systemd_run_available=true
timeout_available=true
project_mode_owner=0750:root:amneziya
db_mode_owner=0600:amneziya:amneziya
db_integrity=ok
users_count=6
orders_count=8
devices_count=8
admin_actions_count=43
```

The VPS can support a transient systemd unit with `RuntimeMaxSec`, but the
application-level restrictions must exist before that capability is used.

## Required Hardening Slice

The next local-only product slice must add a dedicated controlled-smoke runner
instead of reusing `app.main` unchanged. Its contract is:

1. Require one Telegram administrator ID and reject IDs absent from
   `ADMIN_TELEGRAM_IDS`.
2. Refuse the production SQLite path and run the workflow only against a
   private SQLite backup clone.
3. Recheck bot identity, webhook absence and zero pending updates immediately
   before waiting for the operator message.
4. Request message updates only, one at a time, with an internal deadline no
   greater than 120 seconds.
5. Accept exactly `/start` from the selected administrator. Stop without
   acknowledging an unexpected first update.
6. Do not register or consume callback-query routes during the smoke.
7. Acknowledge only the accepted update after its response succeeds, then
   exit.
8. Emit only identity/status/count evidence; never emit token, administrator
   ID, webhook URL, message body, user row or config material.

The runner needs unit tests for administrator validation, production DB path
rejection, webhook/backlog rejection, unexpected-update preservation, exact
`/start` acceptance, clone-only mutation, timeout and redacted output.

## Prepared Future Runtime Scope

After the hardening is tested, pushed, packaged and uploaded under its own
source-overlay gate, a separate live approval may authorize:

- regular `amneziya-bot.service` remains disabled and inactive;
- a unique transient unit uses `Restart=no`, `RuntimeMaxSec=180`,
  `TimeoutStopSec=15` and `KillMode=control-group`;
- the hardened runner has its own 120-second internal deadline;
- a mode `0600` SQLite clone in a mode `0700` private run directory is used;
- the operator sends `/start` only from the selected configured admin account
  and does not press buttons;
- both write gates remain false;
- production DB checksum/aggregates, web health and private listeners are
  checked before and after;
- the transient unit is stopped and absent before temporary material is
  removed.

Stop immediately on identity mismatch, webhook configuration, nonzero backlog,
unexpected update, wrong sender, wrong command, production DB change, bot unit
enablement, public listener, write-gate change, timeout or secret-bearing
output. Do not clear Telegram updates or restore the production DB
automatically; preserve evidence and require a new decision.

## Result

`APPROVE_OR_STOP` resolves to `STOP` for direct polling of the current
`34b3b43` runtime. The safe next action is the approved local-only hardening
slice:

```text
START_PHASE10_TELEGRAM_SINGLE_ADMIN_TRANSIENT_SMOKE_RUNNER_HARDENING_SLICE
```

Android TV device `8` remains pending only for the separate physical
`IMPORT_CONNECT` and handshake/traffic verification. This Telegram decision
does not block that device test.
