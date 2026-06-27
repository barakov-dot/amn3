# AMN2 Android AmneziaWG profile-name acceptance result template

Дата: 2026-06-27.
Назначение: фиксировать результат exact gate
`ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`.

```text
run_id=YYYYMMDDTHHMMSSZ
operator=имя_или_код_оператора
gate_name=ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
target_vps=89.185.80.166
execution_model=operator-controlled-device

input_artifact_source=canonical_generated_name
expected_name=Neobyatnaya-AMNZ-N
expected_filename=Neobyatnaya-AMNZ-N.conf
observed_display_name=SERVER1|Neobyatnaya-AMNZ-N|other
observed_display_name_matches_expected=true|false
manual_rename_performed=true|false
manual_rename_required=true|false
import_attempt_count=1
import_result=passed|failed|deferred

scope_control=one-device-only
peer_creation_performed=false
config_generation_performed=false
config_delivery_performed=false
vpn_uri_printed=false
qr_payload_printed=false
conf_payload_printed=false
private_key_printed=false
psk_printed=false
token_printed=false
password_printed=false
raw_logs_printed=false
```

```text
decision=pass|fail|defer
next_action=accept_to_naming_contract|open_compatibility_gap_ticket|defer_to_next_model
```

```text
notes=<кратко_про_почему_не_совпало>
stop_lines_triggered=<none|config_delivery_attempted|peer_creation_attempted|public_exposure_performed|secret_publication>
```
