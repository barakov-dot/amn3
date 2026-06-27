# PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_REVIEW

Дата: 2026-06-27.

Статус: `completed-docs-only`.

Использованы:

- `PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_RESULT`;
- existing Phase 8 private/operator RC evidence;
- `PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_RESULT`.

Этим review live/VPS/Telegram/public gates не открывались.

## Verdict

```text
review_go=true
recommended_gate=PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_GATE
target_vps=89.185.80.166
required_transport_model=key-based-short-ssh-no-scp
purpose=prove_or_restore_no_telegram_polling
public_launch_status=not-approved
config_delivery_status=not-approved
production_rollout_status=not-approved
```

## Why this is required

`PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_GATE` reached:

```text
bot_polling_started=true
manual_window_status=started
```

Then SSH closed before the planned stop/final guard:

```text
ssh_key_path_retry_remote_exit_code=-1
exact_blocker=ssh_connection_closed_by_remote_host_during_manual_window_after_polling_started
```

Therefore the current safe status is not `passed`; it is cleanup-required
until no-polling is proven.

## Allowed actions

Inside the future
`PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_GATE`, allow only:

- local public closed probes for `3030`, `3040`, `80`, `443` before and after;
- key-based SSH login using the prepared operator key;
- read-only process classification for AMN2 Telegram polling only;
- stop only AMN2 `python -m app.main` polling process whose cwd is `/opt/amn2`;
- final no-polling guard;
- safe evidence only.

## Forbidden actions

Forbidden:

- password fallback;
- SCP/helper upload;
- package upload/apply;
- service restart/start/stop outside stopping the exact AMN2 bot polling
  process;
- public exposure;
- firewall/listener/TLS/proxy changes;
- config generation or delivery;
- peer creation;
- `.conf`, QR, `vpn://`, private key, PSK, token/password output;
- raw process list output;
- DB row dump/download/copy;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider action.

## Pass criteria

```text
key_path_preflight_status=passed
public_closed_probes_before_status=passed
ssh_key_login_only=true
password_fallback_used=false
amn2_app_main_polling_process_before_count=0_or_more
stop_only_amn2_app_main_polling_process_status=not_needed_or_stopped
remaining_amn2_app_main_polling_process_count=0
final_no_polling_guard_status=passed
public_closed_probes_after_status=passed
secret_values_printed=false
```

## Exact copy/paste gate command

```text
PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_GATE

Открыть exact gate для key-based cleanup/no-polling guard после
PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_GATE blocker.

Использовать existing Phase 8 evidence и результат:
PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_RESULT.

Target VPS: 89.185.80.166.

Allowed:
- local public closed probes for 3030, 3040, 80, 443 before and after;
- key-based SSH login using the prepared operator key;
- read-only process classification for AMN2 Telegram polling only;
- stop only AMN2 python -m app.main polling process whose cwd is /opt/amn2;
- final no-polling guard;
- safe evidence only.

Forbidden:
- password fallback;
- SCP/helper upload;
- package upload/apply;
- service restart/start/stop outside stopping the exact AMN2 bot polling process;
- public exposure;
- firewall/listener/TLS/proxy changes;
- config generation or delivery;
- peer creation;
- .conf/QR/vpn:// output;
- private key/PSK/token/password output;
- raw process list output;
- DB row dump/download/copy;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider action.

Stop at first failed guard and report exact blocker.
```

## Prepared helper

```text
helper=tmp/private_rc_telegram_operation_key_path_cleanup_guard.ps1
default_key_path=%USERPROFILE%\.ssh\amn2_private_rc_operator_ed25519
```
