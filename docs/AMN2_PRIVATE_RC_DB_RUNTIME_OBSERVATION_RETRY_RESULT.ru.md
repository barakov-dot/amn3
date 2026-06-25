# AMN2 private RC DB/runtime observation retry result

Дата: 2026-06-25.

Статус:

```text
private_rc_db_runtime_observation_retry_gate_status=passed-db-path-classified-with-aggregate-limitation
gate_name=PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE_RETRY
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
ssh_transport_diagnostic_prerequisite=passed
db_path_observation_completed=true
db_root_cause_classification=settings_db_present
db_aggregate_inventory_status=not_completed_helper_quoting_issue
public_launch_status=not-approved
```

Gate был открыт оператором явно. Выполнялись только small read-only SSH
commands. Не выполнялись package upload/apply, service start/restart/stop,
public exposure, config generation/delivery, peer creation, DB row dump,
DB download/copy, Telegram polling/live send, restore/import/reboot, provider
rebuild или secret-bearing output.

## 1. Preconditions

```text
ssh_transport_diagnostic_passed=true
ssh_transport_general_status=passed
source_overlay_expected=187949bffb927a0a6d6c1f260fc0bb9ebb972447
```

## 2. Precheck result

```text
venv_python_present=true
dotenv_present=true
servers_yml_present=true
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_match=yes
```

Safe env presence only:

```text
DATABASE_PATH_presence=present
TELEGRAM_BOT_TOKEN_presence=present
APP_SECRET_KEY_presence=present
WEB_ADMIN_USERNAME_presence=present
WEB_ADMIN_PASSWORD_HASH_presence=present
WEB_ADMIN_SESSION_SECRET_presence=present
VPS_APPLY_ENABLED_presence=present
LOCAL_AGENT_ENABLED_presence=present
WEB_ADMIN_HOST_presence=present
WEB_ADMIN_PORT_presence=present
dotenv_values_printed=false
```

## 3. DB path result

```text
settings_load_status=passed_shell_env
settings_database_path=data/amneziya.sqlite3
settings_database_path_kind=relative
settings_database_resolved_path=/opt/amn2/data/amneziya.sqlite3
settings_database_parent_exists=true
settings_database_exists=true
settings_database_bytes=147456
settings_database_mode=600
settings_secret_values_printed=false
```

DB candidates:

```text
db_candidate_count=1
db_candidate_1_path=data/amneziya.sqlite3
db_candidate_1_bytes=147456
db_candidate_1_mode=600
db_candidate_contents_printed=false
```

Classification:

```text
db_root_cause_classification=settings_db_present
previous_telegram_live_preview_db_present_false_reclassified=helper_observation_issue
```

## 4. Web process observation

```text
web_process_present=true
web_pid_311715_cwd=/opt/amn2
```

The web process environment key presence checks printed `missing` for selected
keys. This is consistent with application settings being loaded from `.env`
inside process startup rather than all relevant values remaining visible in
`/proc/<pid>/environ`.

The helper also saw transient `pgrep`/`/proc` noise for short-lived process IDs.
This is recorded as helper observation noise and not as an AMN2 blocker.

## 5. Aggregate limitation

Aggregate counts were not completed. Two aggregate attempts failed due helper
command quoting around SQL/shell pipelines over Windows SSH:

```text
first_aggregate_failure=remote_shell_sql_quoting_error
aggregate_resume_failure=remote_shell_pipeline_quoting_error
db_aggregate_inventory_status=not_completed_helper_quoting_issue
db_rows_printed=false
db_download_copy_performed=false
```

This does not change the DB path classification because DB existence, size,
mode and candidate path were already observed safely.

## 6. Public exposure and mutation guard

Before retry:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
public_closed_probes_before_status=passed
```

Final guard:

```text
package_upload_apply_performed=false
service_start_restart_stop_performed=false
public_exposure_performed=false
config_generation_performed=false
config_delivery_performed=false
peer_creation_performed=false
db_row_dump_performed=false
db_download_copy_performed=false
telegram_polling_started=false
telegram_live_send_performed=false
restore_import_reboot_performed=false
provider_rebuild_performed=false
secret_values_printed=false
```

## 7. Final interpretation

```text
db_discrepancy_status=resolved_for_path_existence
db_runtime_path_status=settings_db_present
aggregate_counts_status=not_observed_due_to_helper_quoting
private_operator_rc_status_impact=no_new_blocker_inside_current_limitations
config_delivery_status=still_not-approved-without-separate-gate
public_launch_status=not-approved
```

The previous Telegram live preview `db_present=false` should not be treated as
runtime DB absence. The DB is present at the configured runtime path.

## 8. Recommended next gates

Одиночный вариант:

```text
ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

Парный вариант:

```text
PRIVATE_RC_TELEGRAM_PARTNER_ADMIN_PREVIEW_GATE
+
FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE_REVIEW
```

Тройной вариант:

```text
PRIVATE_RC_TELEGRAM_PARTNER_ADMIN_PREVIEW_GATE
+
FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE_REVIEW
+
PRIVATE_RC_DB_AGGREGATE_COUNT_HELPER_HARDENING
```
