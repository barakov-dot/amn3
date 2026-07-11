# Phase 10 private Telegram bot runtime gate review

Date: 2026-07-11.

Decision:

```text
non_polling_identity_backlog_diagnostic=APPROVE-CONDITIONAL
controlled_polling=HOLD-UNTIL-PENDING-COUNT-ZERO-AND-SEPARATE-APPROVAL
persistent_service_activation=STOP
```

This review performed safe VPS readiness checks only. It did not call the
Telegram Bot API, start polling, send a message, change the service state or
print a token.

## Runtime Readiness

```text
source_overlay=34b3b43
bot_unit_load_state=loaded
bot_unit_template_match=true
bot_unit_mode=0640
bot_service_user=amneziya
bot_service_group=amneziya
bot_service_active=inactive
bot_service_enabled=enabled
bot_process_present=false
restart_policy=on-failure
restart_seconds=5
restart_count=0
env_mode=0640
env_owner=root:amneziya
token_configured=true
token_shape_valid=true
admin_id_count=2
proxy_configured=false
app_secret_configured=true
database_readable=true
server_config_readable=true
telegram_dns_ok=true
telegram_tls_ok=true
VPS_APPLY_ENABLED=safe
OPERATOR_DEVICE_CREATE_ENABLED=safe
```

No token value, admin ID, database row or config payload was returned.

## Code Review

`python -m app.cli bot check-network` performs only Telegram `getMe` and closes
the session. `app.main.run()` calls `dispatcher.start_polling(bot)` directly.
It does not inspect `getWebhookInfo`, enforce an empty pending-update queue or
set a `drop_pending_updates` policy.

The installed unit is enabled even though it is inactive. A future reboot or
manual dependency action could therefore start polling before this gate is
completed. Persistent activation is not approved in this state.

## Safe Aggregate Baseline

```text
users_count=6
orders_count=8
pending_orders_count=0
devices_count=8
admin_actions_count=43
```

Counts are recorded only for later rollback comparison. No rows or identities
were read into evidence.

## Approved Next Diagnostic

After a separate exact phrase, the allowed non-polling sequence is:

1. Reconfirm overlay `34b3b43`, both write gates safe and bot inactive.
2. Disable the already inactive bot unit to close accidental reboot start.
3. Call Telegram `getMe` and `getWebhookInfo` only.
4. Return bot identity, webhook-configured boolean and pending-update count;
   never return token or webhook URL.
5. Keep the bot service stopped and disabled.

If the webhook is configured or pending-update count is nonzero, stop. Do not
delete a webhook or drop pending updates without another explicit decision.

Exact phrase:

```text
APPROVE PHASE10_PRIVATE_TELEGRAM_GETME_AND_BACKLOG_CHECK_NO_POLLING
```

## Future Controlled Polling Scope

Controlled polling remains held. If the non-polling diagnostic proves no
webhook and zero pending updates, a later gate may allow:

- SQLite backup through the backup API and aggregate counts before start;
- service disabled at boot;
- one controlled polling process with remote watchdog TTL at most 180 seconds;
- operator `/start` only from approved admin test chat;
- no approve/config/request/reset/delete buttons;
- final `systemctl stop`, process-absent guard and public-closed probes;
- aggregate count comparison and DB restore only on forbidden mutation;
- no persistent `enable --now`.

## Rollback And Stop Criteria

Stop immediately on token failure, identity mismatch, webhook configured,
pending updates, unexpected existing polling, public listener, enabled write
gate, admin count mismatch, service flapping or secret-bearing output.

Runtime rollback is `systemctl stop`, disable the unit, verify no polling
process, preserve source overlay `34b3b43`, and restore the pre-poll SQLite
backup only if forbidden DB mutation occurred. Source rollback is not required
for a bot-only runtime failure.

## Excluded

Live polling, persistent service activation, live send, pending-update drop,
webhook mutation, Telegram profile/media mutation, credential issue/rotation,
peer/user/config action, Android TV device `8` action, public exposure, package
apply, source change, reboot and provider action remain excluded.
