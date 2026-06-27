# HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_HARDENING

Дата: 2026-06-27.

Статус: `completed-docs-only`.

Live/VPS/SSH/Telegram/public gates этим hardening не открывались.

## Problem

Два Telegram operation helper-а держали SSH-сеанс во время manual window:

```text
old_key_path_retry_manual_window_seconds=1800
old_key_path_retry_result=ssh_closed_during_manual_window_after_polling_started
cleanup_guard_result=passed
short_window_retry_manual_window_seconds=120_to_180
```

Short-window design снижает риск, но все еще удерживает SSH-сессию во время
manual window. Следующий helper-hardening должен убрать эту зависимость.

## Target design

Будущий no-long-SSH helper должен:

- использовать key-based SSH only;
- выполнять только короткие SSH-команды;
- не держать SSH-сессию во время manual Telegram window;
- запускать controlled polling с remote self-stop watchdog;
- задавать remote TTL, например `180` секунд максимум;
- после local manual window делать отдельный short SSH final guard;
- при любом сбое делать отдельный cleanup/no-polling guard;
- не использовать SCP/helper upload;
- не создавать remote temp helper files;
- не печатать secrets/payloads/raw process list.

## Proposed flow

```text
step_1_local_public_closed_probes=3030_3040_80_443
step_2_short_ssh_precheck=head_settings_getme_no_polling_guard
step_3_short_ssh_start_polling_with_remote_ttl
step_4_local_manual_window_no_ssh_open
step_5_short_ssh_final_stop_and_no_polling_guard
step_6_local_public_closed_probes=3030_3040_80_443
```

## Remote TTL rule

Remote start command must launch polling with a watchdog that stops it without
needing the original SSH session to remain open:

```text
remote_polling_ttl_seconds_default=120
remote_polling_ttl_seconds_max=180
remote_watchdog_required=true
local_manual_window_can_end_without_open_ssh=true
```

The helper must still run final guard after local manual window. If final guard
cannot run, cleanup/no-polling guard becomes mandatory.

## Stop-lines

No-long-SSH hardening must not:

- open public exposure;
- generate or deliver config;
- create peer;
- upload package/apply source;
- restart services broadly;
- change firewall/sshd/auth/users/keys;
- output `.conf`, QR, `vpn://`, private key, PSK, token/password;
- print raw process list, raw logs, DB rows;
- mutate Telegram profile/media;
- perform restore/import/reboot/provider action.

## Acceptance criteria

```text
helper_uses_key_based_ssh_only=true
password_fallback_used=false
long_ssh_manual_window_used=false
remote_polling_ttl_configured=true
remote_polling_ttl_seconds<=180
local_manual_window_without_open_ssh=true
final_no_polling_guard_required=true
cleanup_guard_required_on_failure=true
scp_helper_upload_performed=false
remote_temp_helper_file_created=false
secret_values_printed=false
```

## Next exact gate

This document does not open execution. Future implementation/review should use:

```text
HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_IMPLEMENTATION_REVIEW
```

Then, if approved:

```text
PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_GATE
```
