# Phase 8 private RC Telegram operation blocker record

Дата: 2026-06-26.

```text
record_status=completed-docs-only
private_rc_telegram_operation_gate_status=blocked-by-intermittent-ssh-transport
telegram_bot_application_failure=false
public_exposure_status=closed
config_delivery_performed=false
telegram_polling_retry_go=false
```

## Summary

The controlled Telegram operation gate did not fail because of AMN2 bot logic.
It is blocked because SSH/SCP transport is not stable enough across repeated
sessions.

Evidence:

- first operation helper upload passed;
- public probes before polling were closed;
- remote start/precheck was cut by `Connection closed`;
- resume refused to start a second polling process;
- cleanup evidence showed no AMN2 `app.main` polling process remained;
- SSH diagnostic later reproduced sequential-session closure;
- server-side ssh/auth logs showed heavy auth noise and no direct evidence for
  MaxStartups/OOM/conntrack/fatal sshd in collected windows.

## Required before retry

```text
required_next_review=PRIVATE_RC_SSH_TRANSPORT_STABILIZATION_REVIEW
telegram_operation_retry_allowed=false
```
