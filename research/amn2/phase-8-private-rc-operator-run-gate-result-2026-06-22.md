# Phase 8 private RC operator run gate result

Дата: 2026-06-22.

Статус: `passed-read-only`.

Scope: `PRIVATE_RC_OPERATOR_RUN_GATE` was opened by the operator for the first
private/operator RC session. Only read-only VPS observation, runtime/source
head check, loopback web/API health observation, Telegram `getMe` and external
closed probes were performed. Package upload/apply, service restart, public
exposure, config generation/delivery, Telegram live send, bot polling, Telegram
profile/media mutation, backup restore/import/reboot, provider rebuild,
production peer/user mutation and secret-bearing output were not performed.

## Produced artifact

```text
docs/AMN2_PRIVATE_RC_OPERATOR_RUN_GATE_RESULT.ru.md
```

## Run identity

```text
gate_name=PRIVATE_RC_OPERATOR_RUN_GATE
run_id=20260622T200016Z
target_vps=89.185.80.166
utc=2026-06-22T20:01:17Z
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
```

## Result summary

```text
target_vps_match=yes
source_overlay_match=yes
web_login_loopback_http=200
loopback_web_health_status=passed
api_loopback_listener_present=false
api_loopback_health_status=not-running-no-start-performed
public_listener_guard_status=passed
telegram_get_me_status=passed
telegram_getme_exit_code=0
external_probe_3030=000
external_probe_3040=000
external_probe_80=000
external_probe_443=000
private_rc_operator_run_remote_status=passed
private_rc_operator_run_gate_status=passed
phase8_private_operator_rc_session_0_status=passed-read-only
```

## Mutation/output guard

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
```

## Helper issues

```text
helper_encoding_issue=windows_powershell_5_1_mojibake_for_utf8_without_bom
helper_external_probe_url_issue=powershell_interpreted_$TargetIp:3030_as_scoped_variable
corrected_external_probes_status=passed
```

Future helper scripts should either use ASCII operator prompts or be saved with
UTF-8 BOM, and should use `${TargetIp}:PORT` in interpolated URL strings.

## Verdict

```text
private_rc_operator_run_gate_status=passed
phase8_private_operator_rc_session_0_status=passed-read-only
public_launch_status=not-approved
next_recommended_state=stay-private-operator-rc-or-open-next-exact-gate
```
