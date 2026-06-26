# Phase 8 private RC SSH transport stabilization review

Дата: 2026-06-26.

Статус:

```text
review_status=completed-docs-only
gate_name=PRIVATE_RC_SSH_TRANSPORT_STABILIZATION_REVIEW
target_vps=89.185.80.166
current_blocker=intermittent-ssh-scp-transport-close-during-repeated-sessions
recommended_next_gate=PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE
telegram_operation_retry_go=false
public_exposure_status=closed
```

## Inputs

- `docs/AMN2_PRIVATE_RC_SSH_SERVER_LOG_DIAGNOSTIC_RESULT.ru.md`
- `docs/AMN2_PRIVATE_RC_TELEGRAM_OPERATION_BLOCKER_RECORD.ru.md`
- `docs/AMN2_HELPER_STYLE_HARDENING.ru.md`

## Decision

Use a single SSH session for the next diagnostic instead of repeated SSH/SCP
sessions. Do not retry Telegram operation yet.

```text
selected_path=single-session-read-only-diagnostic
mutating_actions_allowed=false
scp_upload_allowed=false
telegram_polling_allowed=false
config_delivery_allowed=false
```

## Alternatives

```text
provider_console_review=PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_REVIEW
auth_noise_review=PRIVATE_RC_SSH_AUTH_NOISE_MITIGATION_REVIEW
backoff_only_policy=available_but_not_root_cause_fix
```

## Next

```text
PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE
```
