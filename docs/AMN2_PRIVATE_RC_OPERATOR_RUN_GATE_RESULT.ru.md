# AMN2 private RC operator run gate result

Дата: 2026-06-22.

Статус:

```text
private_rc_operator_run_gate_status=passed
phase8_private_operator_rc_session_0_status=passed-read-only
gate_name=PRIVATE_RC_OPERATOR_RUN_GATE
target_vps=89.185.80.166
run_id=20260622T200016Z
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
```

Этот результат фиксирует первую private/operator RC session 0. Gate был открыт
оператором явно. Выполнялись только разрешенные read-only действия. Не
выполнялись package apply, service restart, config delivery, Telegram live
send, bot polling, public exposure, restore/import/reboot, provider rebuild
или production peer/user mutation.

## 1. Что было выполнено

Разрешенный контур:

```text
read_only_vps_observation_allowed=true
loopback_web_api_health_allowed=true
telegram_getme_allowed=true
external_closed_probes_allowed=true
safe_evidence_without_payload=true
```

Фактически выполнено:

- read-only VPS observation;
- current runtime/source head check without package apply;
- loopback web health check;
- loopback API observation without service start;
- Telegram `getMe` without live send, polling or profile/media mutation;
- safe DB aggregate inventory;
- external closed probes;
- final mutation/output guard.

## 2. Target/runtime result

```text
target_vps_expected=89.185.80.166
target_vps_observed=89.185.80.166
target_vps_match=yes
opt_amn2_present=true
venv_python_present=true
dotenv_present=true
servers_yml_present=true
db_present=true
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_expected_full=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_expected_short=187949b
source_overlay_match=yes
package_apply_performed=false
service_restart_performed=false
```

## 3. Safe env/admin result

```text
TELEGRAM_BOT_TOKEN_presence=present
APP_SECRET_KEY_presence=present
WEB_ADMIN_USERNAME_presence=present
WEB_ADMIN_PASSWORD_HASH_presence=present
WEB_ADMIN_SESSION_SECRET_presence=present
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
WEB_ADMIN_HOST=127.0.0.1
WEB_ADMIN_PORT=3030
SERVER_NAME=local
admin_telegram_ids_present=True
admin_telegram_ids_count_actual=2
operator_admin_pair_present=yes
admin_telegram_ids_value_printed=false
secret_values_printed=false
```

Only presence and counts were printed. Secret values and admin IDs were not
printed.

## 4. Listener/public exposure result

Observed listener summary:

```text
loopback_web_process_present=true
web_listener=127.0.0.1:3030
ssh_public_listener_present=true
public_listener_violation=no
public_listener_guard_status=passed
```

Loopback web health:

```text
web_login_loopback_http=200
loopback_web_health_status=passed
```

Loopback API observation:

```text
api_loopback_listener_present=false
api_loopback_health_status=not-running-no-start-performed
api_service_start_performed=false
```

External closed probes after correcting helper URL interpolation:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## 5. Telegram getMe result

```text
settings_load_status=passed
telegram_token_present=True
telegram_proxy_configured=False
telegram_token_value_printed=false
secret_values_printed=false
telegram_get_me_status=passed
telegram_api_status=ok
bot_identity_present=yes
bot_identity_safe=@NeobyatnayaAMNZ_bot
telegram_proxy_status=disabled
bot_polling_started=false
telegram_live_send_performed=false
telegram_profile_media_mutation_performed=false
telegram_media_upload_performed=false
config_delivery_payload_output_performed=false
telegram_getme_exit_code=0
```

This proves only Telegram API `getMe` reachability and bot identity surface. It
does not prove Telegram live send, polling or config delivery.

## 6. Safe DB aggregate inventory

```text
db_present=True
db_bytes=147456
users_count=1
devices_count=1
servers_count=1
api_tokens_count=2
admin_actions_count=7
db_rows_printed=false
```

## 7. Final mutation/output guard

```text
destructive_action_performed=false
package_upload_apply_performed=false
service_restart_performed=false
public_exposure_performed=false
config_generation_performed=false
config_delivery_performed=false
telegram_live_send_performed=false
bot_polling_started=false
telegram_profile_media_mutation_performed=false
restore_import_reboot_performed=false
provider_rebuild_performed=false
production_peer_user_mutation_performed=false
secret_values_printed=false
private_rc_operator_run_remote_status=passed
remote_private_rc_operator_run_exit_code=0
```

## 8. Helper issues observed

Two helper issues were observed and must be avoided in future helper scripts:

```text
helper_encoding_issue=windows_powershell_5_1_mojibake_for_utf8_without_bom
helper_external_probe_url_issue=powershell_interpreted_$TargetIp:3030_as_scoped_variable
```

Impact:

- Russian helper prompts were displayed as mojibake in Windows PowerShell.
- Initial local external probes printed malformed URLs: `http:///...`.
- External probes were rerun manually with `${TargetIp}` interpolation and
  passed as `000/000/000/000`.

Future helper rule:

- use ASCII operator prompts or save PowerShell scripts with UTF-8 BOM;
- use `${TargetIp}:3030`, `${TargetIp}:3040`, `${TargetIp}:80` and
  `${TargetIp}:443` inside interpolated strings.

## 9. What this gate proves

This gate proves:

- private/operator RC session 0 can run read-only;
- target/runtime source matches expected AMN2 `187949b`;
- web/admin remains loopback-only;
- public probes stayed closed;
- Telegram `getMe` works without live send or polling;
- no config delivery or secret-bearing output occurred;
- no package apply, restart or mutation occurred.

## 10. What this gate does not prove

This gate does not prove:

- public launch readiness;
- public web/admin/API exposure;
- Telegram live delivery;
- bot polling;
- config delivery automation;
- fresh Android phone post-RC acceptance;
- restore/import DR;
- provider rebuild;
- production-scale rollout.

## 11. Final verdict

```text
private_rc_operator_run_gate_status=passed
phase8_private_operator_rc_session_0_status=passed-read-only
public_launch_status=not-approved
next_recommended_state=stay-private-operator-rc-or-open-next-exact-gate
```
