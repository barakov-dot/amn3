# AMN2 private RC DB/runtime observation result

Дата: 2026-06-24.

Статус:

```text
private_rc_db_runtime_observation_gate_status=blocked-by-ssh-transport-before-observation
gate_name=PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
remote_observation_started=false
db_runtime_observation_completed=false
db_root_cause_classification=not_observed
public_launch_status=not-approved
```

Gate был открыт оператором явно как read-only DB/runtime observation. Два
независимых helper-а остановились до remote observation, потому что SSH
соединение закрывалось сервером до первого remote precheck output.

## 1. Что успело выполниться

Первый helper:

```text
run_id=20260624T190511Z
dry_probe_url_inspection=passed
public_closed_probes_before_status=passed
remote_observation_started=false
ssh_error=Connection closed by 89.185.80.166 port 22
```

Resume helper:

```text
run_id=20260624T190840Z
dry_probe_url_inspection=passed
public_closed_probes_before_status=passed
remote_precheck_started=false
ssh_error=Connection closed by 89.185.80.166 port 22
```

External probes before observation remained closed:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

`curl` printed transport errors such as empty reply or TLS handshake failure,
but the probe code remained `000`, which is consistent with closed public
exposure for this gate.

## 2. What was not observed

Not observed:

```text
source_overlay_match=not_observed
settings_database_path=not_observed
settings_database_resolved_path=not_observed
settings_database_exists=not_observed
db_candidate_count=not_observed
web_process_cwd=not_observed
db_aggregate_inventory_status=not_observed
db_root_cause_classification=not_observed
```

The earlier discrepancy remains unresolved:

```text
private_rc_operator_run_gate_db_present=true
private_rc_telegram_bot_live_preview_db_present=false
db_discrepancy_status=unresolved_due_to_ssh_transport_blocker
```

## 3. Final mutation/output guard

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
telegram_profile_media_mutation_performed=false
restore_import_reboot_performed=false
provider_rebuild_performed=false
secret_values_printed=false
```

## 4. Exact blocker

```text
exact_blocker=ssh_transport_closed_before_remote_precheck
blocker_layer=ssh_transport_or_server_session_policy
amn2_db_runtime_root_cause_found=false
```

This is not evidence that the DB is missing. It only proves that this gate
could not observe DB/runtime state because SSH closed before command execution.

## 5. Recommended next gates

Одиночный вариант:

```text
PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_REVIEW
```

Парный вариант:

```text
PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_REVIEW
+
PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE_RETRY_PLAN
```

Тройной вариант:

```text
PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_REVIEW
+
PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE_RETRY_PLAN
+
ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

Do not retry DB/runtime observation again until the SSH transport blocker is
reviewed or the operator explicitly opens a retry gate with adjusted SSH method.
