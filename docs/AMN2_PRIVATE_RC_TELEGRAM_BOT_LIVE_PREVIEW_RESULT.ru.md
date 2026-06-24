# AMN2 private RC Telegram bot live preview result

Дата: 2026-06-24.

Статус:

```text
private_rc_telegram_bot_live_preview_gate_status=passed-with-manual-operator-observation
gate_name=PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE
target_vps=89.185.80.166
run_id=20260624T184735Z
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
operator_start_flow_observed=passed
partner_start_flow_observed=not_reported
phase8_final_status=launch-ready-with-explicit-limitations
public_launch_status=not-approved
```

Gate был открыт оператором явно. Выполнялся узкий private/operator Telegram bot
live preview: controlled polling, ручная проверка `/start` оператором,
остановка polling и финальные guards. Не выполнялись package apply, broad
service restart, public exposure, config generation/delivery, peer creation,
Telegram profile/media mutation, restore/import/reboot, provider rebuild или
secret-bearing output.

## 1. Что было выполнено

Разрешенный контур:

```text
read_only_vps_precheck_allowed=true
source_head_check_without_package_apply_allowed=true
safe_env_presence_check_allowed=true
public_closed_probes_allowed=true
controlled_bot_polling_allowed=true
manual_operator_ux_observation_allowed=true
stop_polling_guard_allowed=true
safe_evidence_without_payload=true
```

Фактически выполнено:

- dry probe URL inspection;
- external closed probes до polling;
- upload remote helper only;
- read-only runtime/source precheck;
- safe env/settings presence checks without secret values;
- Telegram `getMe` precheck;
- exactly one controlled Telegram bot polling process;
- manual operator `/start` UX observation;
- controlled stop of bot polling;
- final no-polling guard;
- external closed probes после polling;
- remote helper cleanup.

## 2. Target/runtime result

```text
target_vps_expected=89.185.80.166
opt_amn2_present=true
venv_python_present=true
dotenv_present=true
servers_yml_present=true
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_expected_full=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_match=yes
package_upload_apply_performed=false
broad_service_restart_performed=false
```

Runtime observation:

```text
db_present=false
```

This is recorded as a helper/runtime observation for this live preview gate.
The gate did not require DB row inspection for pass because the manual
operator `/start` flow passed and no config delivery, peer creation or
secret-bearing output occurred.

## 3. Safe env/admin result

```text
TELEGRAM_BOT_TOKEN_presence=present
APP_SECRET_KEY_presence=present
WEB_ADMIN_USERNAME_presence=present
WEB_ADMIN_PASSWORD_HASH_presence=present
WEB_ADMIN_SESSION_SECRET_presence=present
settings_load_status=passed
telegram_token_present=True
telegram_proxy_configured=False
web_admin_host=127.0.0.1
web_admin_port=3030
vps_apply_enabled=False
local_agent_enabled=False
admin_telegram_ids_present=True
admin_telegram_ids_count_actual=2
admin_telegram_ids_value_printed=false
secret_values_printed=false
```

Only presence and count markers were printed. Token, passwords and admin ID
list were not printed in helper output.

## 4. Public exposure closed result

Before polling:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
public_closed_probes_before_status=passed
```

After polling:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
public_closed_probes_after_status=passed
public_exposure_performed=false
```

## 5. Telegram result

Precheck:

```text
telegram_get_me_status=passed
telegram_getme_exit_code=0
bot_identity_present=yes
telegram_proxy_status=checked
```

Controlled polling:

```text
existing_bot_polling_process=absent
bot_polling_started=true
bot_polling_pid_recorded=true
telegram_live_replies_limited_to_admin_test_chats=operator_manual_boundary
config_delivery_performed=false
secret_values_printed=false
remote_start_status=passed
remote_start_exit_code=0
```

Manual operator observation:

```text
operator_start_flow_observed=passed
partner_start_flow_observed=not_reported
config_delivery_attempted=not_reported_by_operator
payload_screenshot_shared=false
unexpected_error_text=not_reported
```

Stop guard:

```text
bot_polling_stop_attempted=true
bot_polling_process_after=stopped
unexpected_bot_polling_process_after=absent
remote_stop_status=passed
remote_stop_exit_code=0
```

## 6. Final mutation/output guard

```text
package_upload_apply_performed=false
broad_service_restart_performed=false
public_exposure_performed=false
config_generation_performed=false
config_delivery_performed=false
peer_creation_performed=false
telegram_profile_media_mutation_performed=false
restore_import_reboot_performed=false
provider_rebuild_performed=false
secret_values_printed=false
```

## 7. Helper issues observed

Observed and fixed before successful run:

```text
helper_relative_tmp_path_issue=observed
helper_relative_tmp_path_fix=$PSScriptRoot_based_tmp_dir
helper_parse_check_after_fix=passed
helper_diff_check_after_fix=passed
```

The first attempt failed before SSH/VPS work because the helper resolved
`tmp` relative to the caller directory `C:\Users\SooL`. The helper was fixed to
resolve its temp directory from `$PSScriptRoot`.

Observed during successful run:

```text
db_present=false
```

This should be rechecked before any future DB-dependent live preview or
config-delivery gate.

## 8. Что доказано

Доказано:

- target/runtime source head matched AMN2 `187949b`;
- Telegram API `getMe` worked;
- exactly one controlled polling process could start;
- bot replied to operator `/start` during the live preview;
- polling was stopped at the end;
- public probes stayed closed before and after;
- no config generation/delivery, peer creation, package apply, broad restart,
  profile/media mutation, restore/import/reboot, provider rebuild or
  secret-bearing output occurred.

## 9. Что не доказано

Не доказано:

- production Telegram bot operation;
- partner/admin `/start` observation;
- non-admin denial behavior;
- config delivery automation;
- public launch readiness;
- public web/admin/API exposure;
- Android phone post-RC acceptance;
- restore/import DR;
- provider rebuild;
- production-scale rollout.

## 10. Final verdict

```text
private_rc_telegram_bot_live_preview_gate_status=passed-with-manual-operator-observation
private_operator_rc_bot_confidence=higher
public_launch_status=not-approved
config_delivery_status=not-approved
next_recommended_state=stay-private-operator-rc-or-open-next-exact-gate
```
