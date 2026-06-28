# AMN2 Phase 9 Android multi-device private config execution result template

Дата: 2026-06-28.
Назначение: safe result template для exact gate
`ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_GATE_3_TO_5`.

```text
run_id=YYYYMMDDTHHMMSSZ
gate_name=ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_GATE_3_TO_5
operator=operator_code
device_count=3|4|5
scope=private_operator_only
source_commit=<short_hash>
branch=<branch_name>
local_private_artifact_root=private-artifacts/phase9/android-multi-device/<run_id>/
local_private_artifact_root_gitignored=true
```

```text
filename_01=Neobyatnaya-AMNZ-N-android-01.conf
filename_02=Neobyatnaya-AMNZ-N-android-02.conf
filename_03=Neobyatnaya-AMNZ-N-android-03.conf
filename_04=Neobyatnaya-AMNZ-N-android-04.conf|not_used
filename_05=Neobyatnaya-AMNZ-N-android-05.conf|not_used
filename_count_matches_device_count=matched|mismatch
```

```text
peer_creation_performed=performed|not_performed
config_generation_performed=performed|not_performed
config_delivery_performed=performed|not_performed
operator_private_channel_used=used|not_used
public_exposure=blocked
self_service_scope=blocked
payload_output_to_chat=blocked
payload_output_to_docs=blocked
payload_output_to_git=blocked
```

```text
conf_payload_printed=blocked
qr_payload_printed=blocked
vpn_uri_printed=blocked
private_key_printed=blocked
psk_printed=blocked
token_printed=blocked
password_printed=blocked
raw_logs_printed=blocked
```

```text
canonical_naming=Neobyatnaya-AMNZ-N
windows_policy=Neobyatnaya-AMNZ-N.conf -> Neobyatnaya-AMNZ-N
android_status=DOCUMENTED_LIMITATION
android_fallback=manual_rename
ios_status=not_proven/manual_rename_fallback
```

```text
result=pass|fail|defer
failure_reason=none|device_count_out_of_scope|gate_not_confirmed|secret_publication|public_scope_attempted|execution_error
next_action=hold|manual_operator_install|prepare_safe_status_sync|open_targeted_debug_gate
```

## Notes

Заполнять только safe summary. Не вставлять configs, QR, import URI, keys, PSK,
tokens, passwords или raw logs.
