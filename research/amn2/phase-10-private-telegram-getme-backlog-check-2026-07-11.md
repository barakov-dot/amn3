# Phase 10 private Telegram getMe and backlog check

Date: 2026-07-11.

Authorization consumed:

```text
APPROVE PHASE10_PRIVATE_TELEGRAM_GETME_AND_BACKLOG_CHECK_NO_POLLING
```

Result:

```text
diagnostic_result=PASS
next_gate=START_PHASE10_PRIVATE_TELEGRAM_CONTROLLED_POLLING_TTL_GATE_REVIEW
```

The approved action disabled autostart for the already inactive Telegram bot
unit and called Telegram `getMe` plus `getWebhookInfo` only. It did not start
polling, send a message, mutate a webhook, drop pending updates or expose a
token or webhook URL.

## Preflight

```text
source_overlay=34b3b43
bot_active_before=inactive
bot_enabled_before=enabled
bot_process_before=false
web_active_before=active
web_login_http_before=200
public_listener_before=false
api_listener_3040_before=false
vps_apply_enabled=false
operator_device_create_enabled=false
token_configured=true
token_shape_valid=true
admin_id_count=2
proxy_configured=false
```

The source overlay, bot identity prerequisites, dual write gates, private web
listener and process-absence guard matched the reviewed gate.

## Service Guard

`amneziya-bot.service` was inactive before the action. Its boot enablement was
removed without starting the unit.

```text
bot_active_after_disable=inactive
bot_enabled_after_disable=disabled
bot_process_after_disable=false
```

## Telegram Non-Polling Diagnostic

```text
telegram_api=ok
bot_identity=@NeobyatnayaAMNZ_bot
bot_identity_match=true
proxy_enabled=false
webhook_configured=false
pending_update_count=0
custom_certificate=false
```

No webhook URL, token, administrator ID or Telegram update payload was read
into evidence.

## Aggregate Mutation Guard

The SQLite database was opened read-only before and after the two Telegram API
methods. All aggregate counts remained unchanged.

```text
db_counts_unchanged=true
users_count=6
orders_count=8
pending_orders_count=0
devices_count=8
admin_actions_count=43
```

## Final Runtime State

```text
bot_active_final=inactive
bot_enabled_final=disabled
bot_process_final=false
web_active_final=active
web_login_http_final=200
public_listener_final=false
```

The web runtime remained healthy and private. No bot process remained after the
diagnostic.

## Decision

The non-polling gate is complete. The identity matches, no webhook is
configured, pending update count is zero and the database aggregates are
unchanged. This removes the backlog blocker but does not authorize polling.

The next allowed step is a review-only gate for a disabled-at-boot polling run
with a remote watchdog TTL, aggregate mutation guards and an unconditional
stop. Persistent service activation remains stopped.

## Excluded

Polling, persistent service activation, message sending, webhook mutation,
pending-update deletion, peer/user/config action, Android TV device `8`
action, public exposure, package apply, source change, reboot and provider
action were not performed.
