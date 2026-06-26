# Phase 8 evidence: SSH key-based access prep gate package

Date: 2026-06-26.

Status: `prepared-pending-provider-console-result-and-private-inputs`.

No live VPS/SSH/provider/config/Telegram/public action was performed by Codex
while preparing this package.

## Artifact

```text
runbook=docs/AMN2_PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_RUNBOOK.ru.md
gate_name=PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE
target_vps=89.185.80.166
```

## Boundary

```text
append_one_operator_public_key_only=true
disable_password_auth_allowed=false
disable_root_login_allowed=false
ssh_port_change_allowed=false
firewall_change_allowed=false
service_restart_allowed=false
private_key_output_allowed=false
password_output_allowed=false
full_authorized_keys_output_allowed=false
```

## Status

```text
execution_status=pending_provider_console_result_and_operator_public_key
secret_values_printed=false
```
