# AMN2 Phase 7 Telegram User-Flow Smoke Attempt

Date: 2026-06-20.

Status: `blocked-by-invalid-telegram-token`.

Gate: `P7-C008 Telegram user-flow smoke`.

Target:

```text
VPS: 89.185.80.166
AMN2 source overlay: 55012958ff6b8338254f3f68dfe6779f4bc56f5d
AMN2 short head: 5501295
Transcript: tmp/p7-c008-telegram-user-flow-smoke-5501295-20260620T103604Z.log
```

Allowed by the named gate:

- SSH/PowerShell;
- Telegram token use/API call;
- loopback/bot runtime smoke for the user-facing Telegram flow.

Explicitly out of scope:

- Telegram identity/profile/media mutation;
- public web exposure;
- config delivery payload output;
- write execution;
- restore/import/reboot;
- provider mutation;
- secret-bearing evidence.

## Boundary

```text
opened_gate=P7-C008
scope=telegram-api-getme-plus-non-polling-bot-user-flow-surface
telegram_token_use_allowed=true
telegram_api_call_allowed=true
telegram_get_me_allowed=true
telegram_polling_started=false
telegram_live_send_performed=false
telegram_identity_profile_media_mutation_performed=false
telegram_media_upload_performed=false
public_exposure_performed=false
public_listener_change_performed=false
config_delivery_payload_output_performed=false
write_execution_performed=false
restore_apply_performed=false
archive_import_apply_performed=false
reboot_performed=false
provider_action_performed=false
local_agent_mutation_performed=false
secret_values_printed=false
```

## Runtime State

```text
source_overlay_commit=55012958ff6b8338254f3f68dfe6779f4bc56f5d
source_overlay_match=yes
opt_amn2_present=true
venv_python_present=true
dotenv_present=true
servers_yml_present=true
db_present=true
web_runtime=/opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
listener=127.0.0.1:3030
```

Safe env flags:

```text
TELEGRAM_BOT_TOKEN_presence=present
APP_SECRET_KEY_presence=present
WEB_ADMIN_USERNAME_presence=present
WEB_ADMIN_PASSWORD_HASH_presence=present
WEB_ADMIN_SESSION_SECRET_presence=present
TELEGRAM_PROXY_URL_presence=missing
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
secret_values_printed=false
```

Safe DB aggregate inventory before smoke:

```text
db_present=True
db_bytes=147456
users_count=0
devices_count=0
servers_count=1
api_tokens_count=2
admin_actions_count=6
db_rows_printed=false
```

## Telegram API Result

`Settings` loaded and the token was present, but Telegram Bot API rejected it:

```text
settings_load_status=passed
telegram_token_present=True
telegram_proxy_configured=False
vps_apply_enabled=False
secret_values_printed=false
telegram_get_me_status=failed
telegram_error_type=TokenValidationError
telegram_error_safe=Token is invalid!
telegram_smoke_exit_code=20
p7_c008_telegram_smoke_status=failed
remote_p7_c008_exit_code=20
```

Interpretation:

- the current VPS `.env` contains a Telegram bot token value;
- that value is not accepted by Telegram as a valid bot token;
- the smoke did not reach polling, live send, profile/media mutation, config
  delivery or any write execution;
- this is a prerequisite/configuration blocker, not evidence of a product code
  regression.

## External Closed Probes

Collected after the failed smoke attempt:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Conclusion

`P7-C008` is blocked by an invalid Telegram bot token on the VPS.

Next required action:

```text
P7-C008a Telegram token reconciliation gate.
Gate: exact named secret/env live gate.
Scope: operator-secret handoff for TELEGRAM_BOT_TOKEN, update VPS .env safely,
verify token with getMe, and rerun P7-C008 non-polling smoke.
Out of scope: Telegram identity/profile/media mutation, live send, config
payload output, public exposure, write execution, restore/import/reboot and
provider mutation.
```

Resolution:

```text
resolved_by=P7-C008a
resolution_evidence=research/amn2/phase-7-telegram-token-reconciliation-user-flow-smoke-5501295-2026-06-20.md
p7_c008_telegram_user_flow_smoke_status=completed_after_token_reconciliation
```

The invalid-token blocker is closed by the follow-up reconciliation evidence.
