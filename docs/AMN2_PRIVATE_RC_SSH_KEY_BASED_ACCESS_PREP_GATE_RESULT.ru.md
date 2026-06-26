# PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_RESULT

Дата: 2026-06-26.

Статус: `passed`.

Gate выполнен после provider-console diagnostic result. Private key, password,
token и полный `authorized_keys` не выводились и не сохранялись в evidence.

## Safe result

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

## No-mutation guard

```text
disable_password_auth_performed=false
disable_root_login_performed=false
ssh_port_change_performed=false
firewall_change_performed=false
service_restart_performed=false
public_exposure_performed=false
secret_values_printed=false
```

## Interpretation

Key-based SSH access is now proven for the operator key path. This does not
approve SSH hardening. Password/root auth, SSH port, firewall and service state
were not changed.

Real Telegram operation remains not proven after the earlier SSH transport
blocker. Because key-login now passes, the next safe step is a review for a
key-path Telegram operation retry, not immediate live polling.

## Recommended next

```text
recommended_next_review=PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_REVIEW
telegram_operation_retry_go=false_until_review
ssh_auth_hardening_go=false_until_separate_hardening_gate
```
