# Phase 8 evidence: SSH key-based access prep gate result

Date: 2026-06-26.

Status: `passed`.

No private key, password, token, config payload, full `authorized_keys`, QR,
`vpn://`, PSK or DB rows are recorded here.

## Safe output

```text
gate_name=PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE
target_vps=89.185.80.166
run_id=20260626T193124Z
local_operator_key_created=true
operator_public_key_fingerprint=SHA256:cNrkGhxuCg3lHXlSC+73/qVhJQDJSbJAqBnpJcHlG8c
operator_public_key_value_printed=false
private_key_output_performed=false
operator_public_key_shape=accepted
authorized_keys_append_count=1
operator_public_key_already_present=false
authorized_keys_mode=600
ssh_dir_mode=700
authorized_keys_full_contents_printed=false
key_based_access_prep_status=operator_public_key_installed_or_already_present
ssh_append_public_key_exit_code=0
key_login_test_status=passed
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_match=yes
ssh_key_login_test_exit_code=0
private_rc_ssh_key_based_access_prep_gate_status=passed
```

## Guards

```text
disable_password_auth_performed=false
disable_root_login_performed=false
ssh_port_change_performed=false
firewall_change_performed=false
service_restart_performed=false
public_exposure_performed=false
secret_values_printed=false
```

## Classification

```text
key_based_access_path_status=passed
ssh_hardening_status=not-approved
telegram_operation_retry_go=false_until_review
recommended_next_review=PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_REVIEW
```
