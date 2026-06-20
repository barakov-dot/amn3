# AMN2 Phase 7 Telegram Token Reconciliation And User-Flow Smoke

Date: 2026-06-20.

Status: `completed-getme-dispatcher-surface-no-send`.

Gate: `P7-C008a Telegram token reconciliation`.

Target:

```text
VPS: 89.185.80.166
AMN2 source overlay: 55012958ff6b8338254f3f68dfe6779f4bc56f5d
AMN2 short head: 5501295
Transcript: tmp/p7-c008a-telegram-token-reconciliation-5501295-20260620T104506Z.log
```

Allowed by the named gate:

- SSH/PowerShell;
- operator-secret handoff for the Telegram bot token;
- safe VPS `.env` update with rollback copy;
- Telegram `getMe` API check;
- non-polling bot dispatcher/user-flow surface smoke.

Explicitly out of scope:

- Telegram identity/profile/media mutation;
- live Telegram send;
- config delivery payload output;
- public web exposure;
- write execution;
- restore/import/reboot;
- provider mutation;
- secret-bearing evidence.

## Boundary

```text
opened_gate=P7-C008a
scope=secret-env-token-reconciliation-plus-getme-non-polling-user-flow-smoke
telegram_token_secret_handoff_performed=true
telegram_token_value_printed=false
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
venv_python_present=true
dotenv_present=true
servers_yml_present=true
db_present=true
web_runtime=/opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
listener=127.0.0.1:3030
```

Safe env flags before and after reconciliation:

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

Secret-safe mutation evidence:

```text
env_update_status=passed
rollback_copy_created_on_vps=true
telegram_token_value_printed=false
service_restart_performed=false
secret_values_printed=false
```

Safe DB aggregate inventory before and after smoke:

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

## Telegram API And User-Flow Surface

```text
settings_load_status=passed
telegram_token_present=True
telegram_proxy_configured=False
vps_apply_enabled=False
secret_values_printed=false
telegram_get_me_status=passed
telegram_api_status=ok
bot_identity_present=yes
bot_identity_safe=@NeobyatnayaAMNZ_bot
telegram_proxy_status=disabled
bot_dispatcher_construct_status=passed
bot_router_count=1
bot_message_handler_count=4
bot_callback_handler_count=18
user_flow_callback_surface_count=11
admin_flow_callback_surface_count=6
bot_polling_started=false
telegram_live_send_performed=false
config_delivery_payload_output_performed=false
secret_values_printed=false
telegram_smoke_exit_code=0
```

The smoke verifies the Telegram user-facing integration surface without
starting polling, sending messages, delivering config payloads or mutating
Telegram profile/media state.

## Final Guard

```text
telegram_token_reconciled=true
telegram_token_value_printed=false
telegram_token_used_for_get_me=true
telegram_api_called=true
telegram_get_me_passed=true
bot_dispatcher_constructed=true
bot_polling_started=false
telegram_live_send_performed=false
telegram_identity_profile_media_mutation_performed=false
telegram_media_upload_performed=false
public_exposure_performed=false
public_listener_change_performed=false
config_delivery_payload_output_performed=false
write_execution_performed=false
write_api_enablement_performed=false
restore_apply_performed=false
archive_import_apply_performed=false
reboot_performed=false
provider_action_performed=false
remote_backup_download_performed=false
service_restart_performed=false
local_agent_mutation_performed=false
production_peer_user_mutation_performed=false
secret_values_printed=false
p7_c008a_telegram_token_reconciliation_status=completed_getme_dispatcher_surface_no_send
p7_c008_telegram_user_flow_smoke_status=completed_after_token_reconciliation
remote_safe_evidence_dir=/opt/amn2/vps-smoke/p7-c008a-telegram-token-reconciliation-20260620T104506Z
```

## External Closed Probes

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Conclusion

`P7-C008a` reconciled the Telegram bot token safely and completed the
user-flow smoke without live send, polling, config payload output, public
exposure, write execution, restore/import/reboot or provider mutation.

The earlier `P7-C008` invalid-token blocker is closed by this evidence. The
Telegram-first user channel is now live-smoked at the API/surface level for the
private/operator RC boundary.
