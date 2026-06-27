# HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_IMPLEMENTATION_REVIEW

Дата: 2026-06-27.

Статус: `completed-docs-only`.

Использованы существующие Phase 8 evidence:

- `HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_HARDENING`;
- `PRIVATE_RC_TELEGRAM_OPERATION_SHORT_WINDOW_RETRY_RESULT`;
- `PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_RESULT`;
- `PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_RESULT`.

Этим review live/VPS/SSH/Telegram/public gates не открывались.

## Verdict

```text
implementation_review_go=true
execution_gate_go=conditional-go-with-explicit-operator-run
recommended_execution_gate=PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_GATE
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
transport_model=key-based-short-ssh-commands-no-open-ssh-during-manual-window
remote_polling_ttl_seconds_default=120
remote_polling_ttl_seconds_max=180
public_launch_status=not-approved
config_delivery_status=not-approved
production_rollout_status=not-approved
```

## Why this implementation exists

Previous retry modes failed in two different SSH shapes:

```text
key_path_1800_retry=ssh_closed_during_manual_window_after_polling_started
cleanup_guard_after_1800_retry=passed
short_window_retry=ssh_closed_before_remote_marker
short_window_polling_started=false_by_evidence
```

The no-long-SSH helper changes the shape:

```text
precheck_ssh=short
start_polling_ssh=short
manual_window=local_no_ssh_open
final_guard_ssh=short
remote_watchdog_ttl_required=true
```

This cannot eliminate SSH transport noise, but it prevents a long-held SSH
session from being the thing that keeps polling alive.

## Required helper behavior

The prepared helper must:

- use key-based SSH only;
- reject password fallback;
- use no SCP/helper upload;
- create no remote temporary helper file;
- run local public closed probes before and after;
- run a short remote precheck:
  - source head check;
  - safe settings/env presence;
  - public listener guard;
  - no existing AMN2 `app.main` polling guard;
  - Telegram `getMe`;
- run a short remote start:
  - start exactly one controlled `python -m app.main`;
  - start a remote watchdog with TTL `<=180` seconds;
  - return immediately after confirming polling started;
- run local manual window with no SSH session open;
- run a short remote final guard:
  - stop only AMN2 `python -m app.main` if still running;
  - require `remaining_amn2_app_main_polling_process_count=0`;
  - require public listener guard passed;
- print only safe evidence.

## Stop-lines

Stop immediately if:

- key preflight fails;
- public probes before start are not closed;
- source head mismatch;
- settings/getMe fails;
- an existing AMN2 bot polling process is present before start;
- start command cannot confirm exactly one controlled polling process;
- remote watchdog cannot be started;
- final no-polling guard fails;
- public probes after finish are not closed;
- any config/payload/secret would be printed.

If SSH closes after polling start and before final guard, do not retry. Run
`PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_GATE`.

## Exact copy/paste execution gate command

```text
PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_GATE

Открыть exact gate для controlled private/operator Telegram bot operation
retry без удержания SSH во время manual Telegram window.

Использовать existing Phase 8 evidence:
- HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_IMPLEMENTATION_REVIEW;
- HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_HARDENING;
- PRIVATE_RC_TELEGRAM_OPERATION_SHORT_WINDOW_RETRY_RESULT;
- PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_RESULT;
- PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_RESULT.

Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Allowed:
- local public closed probes for 3030, 3040, 80, 443 before and after;
- key-based SSH only using prepared operator key;
- short SSH precheck;
- short SSH controlled polling start with remote self-stop watchdog;
- local manual Telegram window while no SSH session is open;
- short SSH final stop/no-polling guard;
- Telegram getMe;
- allow live Telegram replies only inside approved admin/operator chats;
- allow minimal Telegram user/chat/session DB state mutation for approved
  admin/operator chats only;
- safe evidence without secret-bearing payload.

Forbidden:
- destructive VPS/provider action;
- package upload/apply;
- password fallback;
- SCP/helper upload;
- remote temp helper files;
- broad service restart;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation or delivery;
- peer creation;
- .conf/QR/vpn:// output;
- private key/PSK/token/password output;
- DB row dump/download/copy;
- Telegram profile/media mutation;
- Telegram broadcast/mass send;
- non-admin user rollout;
- restore/import/reboot;
- provider rebuild;
- production-scale rollout.

Stop at first failed gate and report exact blocker.
```

## Prepared helper

```text
helper=tmp/private_rc_telegram_operation_no_long_ssh_retry_gate.ps1
default_manual_window_seconds=120
default_remote_polling_ttl_seconds=150
maximum_remote_polling_ttl_seconds=180
```

## Go / no-go

```text
go_for_future_exact_gate=true
go_without_operator_run=false
repeat_old_long_ssh_helpers=false
```
