# PRIVATE_RC_TELEGRAM_OPERATION_SHORT_WINDOW_RETRY_REVIEW

Дата: 2026-06-27.

Статус: `completed-docs-only`.

Использованы существующие Phase 8 evidence:

- `PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_RESULT`;
- `PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_RESULT`;
- `PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_RESULT`;
- `PRIVATE_RC_FINAL_STATUS_REFRESH`.

Этим review live/VPS/SSH/config/Telegram/public gates не открывались.

## Verdict

```text
review_go=true
execution_gate_go=conditional-go-with-explicit-operator-approval
recommended_execution_gate=PRIVATE_RC_TELEGRAM_OPERATION_SHORT_WINDOW_RETRY_GATE
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
required_transport_model=key-based-short-window-single-session-no-scp
recommended_manual_window_seconds=120
maximum_manual_window_seconds=180
public_launch_status=not-approved
config_delivery_status=not-approved
production_rollout_status=not-approved
```

`PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_GATE` не прошел из-за SSH close
во время `manual_window_seconds=1800`. Cleanup guard после этого прошел и
доказал `final_no_polling_guard_status=passed`.

Следующий retry допустим только с новым коротким окном. Нельзя повторять
30-минутную схему.

## What this retry is allowed to prove

Short-window retry может проверить только:

- key-based SSH path;
- source head match;
- Telegram `getMe`;
- controlled polling start;
- operator `/start` flow during a short window;
- controlled polling stop;
- final no-polling guard;
- public exposure remains closed.

Он не открывает:

- config delivery;
- peer creation;
- public launch;
- production rollout;
- Telegram profile/media mutation;
- SSH hardening/firewall/provider changes.

## Required execution design

```text
manual_window_seconds_default=120
manual_window_seconds_max=180
operator_preopens_telegram_before_start=true
operator_sends_start_immediately_after_manual_window_status_started=true
single_session_allowed=true
scp_helper_upload_allowed=false
remote_temp_helper_file_allowed=false
password_fallback_allowed=false
long_ssh_sleep_allowed=false
cleanup_guard_required_on_any_ssh_close=true
```

Почему короткое окно:

- прошлый key-path retry дошел до polling start;
- failure happened during long 1800-second SSH-held manual window;
- cleanup found and stopped one leftover polling process;
- a short 120-180 second window reduces transport exposure while still enough
  for `/start` UX observation.

## Allowed actions

Inside future `PRIVATE_RC_TELEGRAM_OPERATION_SHORT_WINDOW_RETRY_GATE` allow
only:

- local public closed probes for `3030`, `3040`, `80`, `443` before and after;
- key-based SSH login using the prepared operator key;
- exactly one SSH session for remote checks, controlled polling, short manual
  window, stop and final guard;
- current runtime/source head check without package apply;
- safe env/settings checks without printing token/password values;
- Telegram `getMe`;
- start exactly one controlled Telegram bot polling process;
- allow live Telegram replies only inside approved admin/operator manual
  boundary;
- allow minimal Telegram user/chat/session DB state mutation for approved
  admin/operator chats only;
- stop bot polling at the end;
- final no-polling/no-public-exposure guard;
- safe evidence only.

## Forbidden actions

Forbidden:

- destructive VPS/provider action;
- package upload/apply;
- password fallback;
- SCP/helper upload;
- remote temp helper files;
- service start/restart/stop outside controlled polling;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation or delivery;
- peer creation;
- `.conf`, QR, `vpn://` output;
- private key/PSK/token/password output;
- DB row dump/download/copy;
- Telegram profile/media mutation;
- Telegram broadcast/mass send;
- non-admin user rollout;
- restore/import/reboot;
- provider rebuild;
- production-scale rollout;
- manual window longer than 180 seconds.

## Pass criteria

```text
key_path_preflight_status=passed
ssh_key_login_only=true
password_fallback_used=false
ssh_session_count=1
manual_window_seconds<=180
source_overlay_match=yes
telegram_get_me_status=passed
existing_bot_polling_process=absent
bot_polling_started=true
operator_start_flow_observed=passed
config_delivery_attempted=false
bot_polling_process_after=stopped
remaining_amn2_app_main_polling_process_count=0
final_no_polling_guard_status=passed
public_closed_probes_after_status=passed
secret_values_printed=false
```

## Fail criteria / stop-lines

Stop and require cleanup/no-polling guard if:

- SSH closes before planned stop/final guard;
- existing bot polling process is present before start;
- more than one polling process would be started;
- source head mismatch;
- Telegram `getMe` fails;
- public listener guard fails;
- public closed probes return non-`000`;
- config delivery is offered or clicked;
- peer/config generation would occur;
- any secret/payload would be printed;
- final no-polling guard does not pass.

## Exact copy/paste execution gate command

```text
PRIVATE_RC_TELEGRAM_OPERATION_SHORT_WINDOW_RETRY_GATE

Открыть exact gate для controlled private/operator Telegram bot operation
short-window retry.

Использовать existing Phase 8 evidence:
- PRIVATE_RC_TELEGRAM_OPERATION_SHORT_WINDOW_RETRY_REVIEW;
- PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_RESULT;
- PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_RESULT;
- PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_RESULT.

Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Manual window:
- default 120 seconds;
- maximum 180 seconds;
- operator must open Telegram before starting;
- operator sends /start immediately after manual window starts.

Allowed:
- local public closed probes for 3030, 3040, 80, 443 before and after;
- key-based SSH login using the prepared operator key;
- exactly one SSH session for remote checks, controlled polling,
  short manual window and stop/final guard;
- current runtime/source head check without package apply;
- safe env/settings checks without printing token/password values;
- Telegram getMe;
- start exactly one controlled Telegram bot polling process;
- allow live Telegram replies only inside approved admin/operator chats;
- allow minimal Telegram user/chat/session DB state mutation for approved
  admin/operator chats only;
- stop bot polling at the end;
- final no-polling/no-public-exposure guard;
- safe evidence without secret-bearing payload.

Forbidden:
- destructive VPS/provider action;
- package upload/apply;
- password fallback;
- SCP/helper upload;
- remote temp helper files;
- service start/restart/stop outside controlled polling;
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
- production-scale rollout;
- manual window longer than 180 seconds.

Stop at first failed gate and report exact blocker.
```

## Go / no-go

```text
go_for_future_exact_gate=true
go_now_without_execution_gate=false
repeat_old_1800_second_helper=false
```
