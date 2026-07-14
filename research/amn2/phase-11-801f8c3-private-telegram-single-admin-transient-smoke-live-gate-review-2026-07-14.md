# Phase 11: 801f8c3 private Telegram transient smoke live gate review

Date: 2026-07-14.

Decision: `READY-AWAITING-EXACT-APPROVAL`.

This review inspected the corrected `801f8c3` runner, ran its scoped tests and
performed a read-only production capability preflight. It did not call the
Telegram API, start polling, send a message, create a transient unit, copy or
write SQLite, change a service, or touch AWG, peers, configs or public
listeners.

## Bound source and runtime

```text
source_branch=codex-vps-test-prep
source_commit=801f8c3406121549eb6a19150be009cfc0ea88d0
production_overlay=801f8c3
controlled_smoke_sha256=B5B5C2592F3344283FA7796D4563357CC90F5D3328116269C0DC353B677B2D2E
controlled_smoke_test_sha256=2689A28BDB4C598466EC8F118C6294F3248A10DF4A7AC6A99D2BA72BED8CE795
focused_controlled_smoke_and_bootstrap=21_passed
bot_and_settings_regression=184_passed
```

The corrected runner preserves the required trust boundary:

1. Both product write gates must be false before bot creation.
2. The selected actor must be present in `ADMIN_TELEGRAM_IDS`.
3. The production SQLite path is refused; the workflow receives only a
   process-owned mode `0600` clone inside a mode `0700` directory.
4. Bot identity must match the previously approved sanitized `getMe` identity.
5. Webhook must be absent and backlog must transition exactly `0 → 1 → 0`.
6. Polling requests only `message`, one update at a time. The only accepted
   update is exact `/start` from the selected administrator.
7. The accepted update is acknowledged only after the one `/start` response
   succeeds and the pre-ack backlog is exactly one.
8. Unexpected sender, command or additional backlog stops without an offset
   acknowledgement. No callback routes or full dispatcher are created.
9. The internal deadline is at most 120 seconds and the Telegram session is
   always closed.
10. The production logical SQLite digest is checked before and after, and the
    result does not emit the token, administrator ID, message body or config.

## Read-only production preflight

```text
preflight=pass
overlay=801f8c3
source_hash_binding=controlled_smoke_and_test_match
web=active_enabled_http_ok_loopback_only
api_3040_listener=0
regular_bot=inactive_disabled_process_0
write_gates=false_false
token_configured_shape_valid=true
configured_admin_count=2
selected_admin_binding=first_configured_private
proxy_configured=false
service_user_binding=valid_private
systemd_run_available=true
expected_bot_identity_bound=prior_sanitized_getMe_evidence
telegram_api_called=false
database_integrity=ok
database_foreign_key_issues=0
database_file_sha256=888AB7E6479354B7E354CD5262FA28D42D1A35CD29907A81A827E9821CFEF611
database_logical_sha256=C54309D1C82E006C1F59AF1BB9A792B05C020B1DF9AE0D6C26BACD3907B78C5D
database_counts_sha256=FEDD60460F70DB5DE23EB0566A68AF772C0351242A8712B37C3F19A1C53CADF1
database_tables=15
database_total_rows=88
awg_container_sha256=267BD715ED6B788FFAE1E59B3E7741ED6932756D25A00C5B7AAAC7492796C79B
awg_restart_count=0
awg_running=true
awg_peer_count=12
awg_peer_set_sha256=E42E1176843B82A748081EDDB8E45A9852C1627A13BC08B9F69A4E4C70B81BB5
run_directory_required_kb=10888
run_directory_available_kb=97328
```

The first preflight invocation used an unnecessarily fixed 100 MiB `/run`
reserve and stopped before any mutation. The review criterion was corrected to
three times the actual SQLite size plus 10 MiB; the resulting bound requirement
is 10,888 KiB and the available 97,328 KiB passes comfortably.

## Exact allowed live scope

Only after the exact phrase below, the live action may:

1. Repeat the complete read-only production preflight and refuse any source,
   runtime, database, bot, listener, write-gate or AWG mismatch.
2. Select the first ID in the existing ordered `ADMIN_TELEGRAM_IDS` value
   without printing it. The operator must use that same configured account.
3. Create one unique private runtime directory, owned by the existing bot
   service user, and create a consistent SQLite online-backup clone. Require
   mode `0700` for the directory and `0600` for the clone.
4. Prove production SQLite did not change while the clone was made.
5. Start exactly one unique transient systemd unit as the existing bot service
   user. The regular `amneziya-bot.service` remains inactive and disabled.
6. Enforce `Restart=no`, `RuntimeMaxSec=180`, `TimeoutStopSec=15`,
   `KillMode=control-group`, `UMask=0077`, `NoNewPrivileges=yes` and a writable
   path limited to the private runtime directory. The application deadline is
   120 seconds.
7. Authorize only the runner's `getMe`, `getWebhookInfo` and message-only
   `getUpdates` sequence, the operator's exact `/start`, and one bot response
   to that accepted administrator. Do not press a callback button.
8. Require the sanitized success contract: correct identity, no webhook,
   backlog `0 → 1 → 0`, exact selected-admin `/start`, callbacks false,
   production database unchanged and clone-only user registration.
9. Stop and collect the transient unit, prove its control group is gone, then
   remove the private clone/runtime directory.
10. Repeat web/listener, regular-bot, write-gate, production DB and AWG checks.

The operator should be ready to send `/start` from the first configured admin
account immediately after the transient unit reports that the bounded wait has
started. Sending from the other configured administrator is a fail-closed
unexpected update and will remain unacknowledged.

## Stop and cleanup contract

On timeout, identity/webhook/backlog/sender/command/response/session, unit,
database or runtime mismatch:

- stop only the unique transient unit and its control group;
- keep the regular bot inactive and disabled;
- never stop, restart, recreate or reconfigure AWG;
- do not acknowledge an unexpected Telegram update and do not clear backlog;
- do not restore or overwrite production SQLite automatically;
- remove the clone only after the transient unit is confirmed absent;
- retain only sanitized failure evidence and require a new decision.

## Explicit exclusions

This gate does not authorize persistent bot enable/start, callbacks, user or
device lifecycle actions beyond clone-only `/start` registration, production
database writes, schema/API smoke, peer/config generation or delivery, public
exposure, firewall/TLS changes, restore apply, reboot, provider action or AWG
service manipulation.

## Exact approval phrase

```text
APPROVE PHASE11_801F8C3_PRIVATE_TELEGRAM_FIRST_CONFIGURED_ADMIN_TRANSIENT_START_SMOKE_AND_ONE_RESPONSE_ON_CLONE_DB_TTL120_WATCHDOG180_BACKLOG_0_1_0_CLEANUP_WITH_REGULAR_BOT_DISABLED_AND_AWG_UNTOUCHED
```

The phrase has not been received or consumed. Until it is received exactly,
polling and Telegram sending remain stopped.
