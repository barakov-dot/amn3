# PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_REVIEW

Дата: 2026-06-26.

Статус: `completed-docs-only`.

Использованы существующие Phase 8 evidence:

- `PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW_REFRESH`;
- `PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_RESULT`;
- `PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_RESULT`;
- `PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_RESULT`;
- `PRIVATE_RC_FINAL_STATUS_REFRESH`.

Этим review live/VPS/config/Telegram/public gates не открывались.

## Verdict

```text
review_go=true
execution_gate_go=conditional-go-with-explicit-operator-approval
recommended_execution_gate=PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_GATE
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
required_transport_model=key-based-single-session-no-scp-lf-normalized
public_launch_status=not-approved
config_delivery_status=not-approved
production_rollout_status=not-approved
```

Старые Telegram operation helpers не повторять. Retry разрешен только как
отдельный key-path gate: один SSH-сеанс через уже установленный operator key,
без SCP/helper upload, без remote temp helper file и без password fallback.

## Why retry is now allowed conditionally

Ранее real Telegram operation был заблокирован до remote marker:

```text
telegram_operation_single_session_status=blocked-by-ssh-transport-before-remote-execution
ssh_single_session_telegram_operation_exit_code=255
telegram_polling_started=false
manual_telegram_window_started=false
telegram_application_failure=false
```

После этого оператор выполнил provider console diagnostic и key-based access
prep:

```text
provider_console_ssh_diagnostic_status=passed-minimal-manual-console-observation
provider_console_source_overlay_match=yes
provider_console_no_telegram_polling_process=true
ssh_key_based_access_prep_gate_status=passed
key_login_test_status=passed
operator_public_key_fingerprint=SHA256:cNrkGhxuCg3lHXlSC+73/qVhJQDJSbJAqBnpJcHlG8c
source_overlay_match=yes
disable_password_auth_performed=false
disable_root_login_performed=false
ssh_port_change_performed=false
firewall_change_performed=false
service_restart_performed=false
```

Это не доказывает Telegram operation, но снимает главный transport blocker
достаточно для одного controlled key-path retry.

## Allowed actions for execution gate

Разрешить только внутри
`PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_GATE`:

- local public closed probes for `3030`, `3040`, `80`, `443` before and after;
- key-based SSH login using the prepared operator key;
- exactly one SSH session for remote checks, controlled polling, timed manual
  window, stop and final guard;
- no password fallback;
- no SCP/helper upload;
- no remote temporary helper file;
- current runtime/source head check without package apply;
- safe env/settings presence checks without printing token/password values;
- Telegram `getMe`;
- start exactly one controlled Telegram bot polling process;
- allow live Telegram replies only inside approved admin/operator manual
  boundary;
- allow minimal Telegram user/chat/session DB state mutation for approved
  admin/operator chats only;
- manual operator UX check;
- stop bot polling at the end;
- final no-polling/no-public-exposure guard;
- safe evidence only.

Approved admin/operator boundary:

```text
admin_operator_count_expected=2
admin_ids_value_output_allowed=false
operator_manual_start_flow_allowed=true
partner_admin_start_flow_allowed_if_available=true
config_delivery_clicks_allowed=false
```

## Forbidden actions

Запрещено:

- destructive VPS/provider action;
- package upload/apply;
- password fallback for SSH;
- SCP/helper upload;
- remote temp helper files;
- service start/restart/stop outside the controlled polling process;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation;
- config delivery;
- peer creation;
- `.conf`, QR, `vpn://` output;
- private key/PSK/token/password output;
- DB row dump/download/copy;
- Telegram profile/media mutation;
- Telegram broadcast/mass send;
- non-admin user rollout;
- restore/import/reboot;
- provider rebuild;
- production-scale rollout.

## Pass criteria

Execution gate can be marked passed only if the helper output and operator
manual summary together prove:

```text
key_path_preflight_status=passed
ssh_key_login_only=true
password_fallback_used=false
ssh_session_count=1
scp_helper_upload_performed=false
remote_temp_helper_file_created=false
remote_stdin_bash_lf_normalization_verified=true
source_overlay_match=yes
telegram_get_me_status=passed
public_closed_probes_before_status=passed
existing_bot_polling_process=absent
bot_polling_started=true
operator_start_flow_observed=passed
partner_start_flow_observed=passed_or_not_available_explicitly_recorded
config_delivery_attempted=false
peer_creation_performed=false
bot_polling_process_after=stopped
final_no_polling_guard_status=passed
public_closed_probes_after_status=passed
secret_values_printed=false
```

If the helper completes but the operator has not reported the manual Telegram
summary, status remains `pending_operator_manual_summary`, not passed.

## Stop-lines

Stop immediately if:

- target VPS is not `89.185.80.166`;
- AMN2 source/runtime head is not
  `187949bffb927a0a6d6c1f260fc0bb9ebb972447`;
- local operator key is missing or key login fails;
- helper attempts password fallback;
- helper wants SCP/helper upload;
- helper creates a remote temporary helper file;
- public probes are not closed before polling;
- existing unknown bot polling process is present;
- more than one polling process would be started;
- bot token/settings load fails;
- bot replies outside approved admin/operator manual boundary;
- UI offers or triggers config delivery unexpectedly;
- any `.conf`, QR, `vpn://`, key, PSK, token/password would be printed;
- helper would create peer/config;
- service/package/public/firewall/TLS/proxy mutation appears;
- stop polling fails at the end;
- final public probes are not closed.

## Exact copy/paste execution gate command

```text
PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_GATE

Открыть exact gate для controlled private/operator Telegram bot operation
retry через уже доказанный key-based SSH path.

Использовать существующие Phase 8 evidence:
- PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_REVIEW;
- PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_RESULT;
- PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_RESULT;
- PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_RESULT.

Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Allowed:
- local public closed probes for 3030, 3040, 80, 443 before and after;
- key-based SSH login using the prepared operator key;
- exactly one SSH session for remote checks, controlled polling,
  timed manual operator window and stop/final guard;
- no password fallback;
- current runtime/source head check without package apply;
- safe env/settings checks without printing token/password values;
- Telegram getMe;
- start exactly one controlled Telegram bot polling process;
- allow live Telegram replies only inside approved admin/operator chats;
- allow minimal Telegram user/chat/session DB state mutation for approved
  admin/operator chats only;
- manual operator UX check;
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
- config generation or config delivery;
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

Manual UX boundary:
- operator sends /start and checks menu/admin-visible surface;
- partner admin sends /start if available;
- do not click config delivery, approve/create config, QR, vpn link, .conf or
  peer-management buttons;
- report only safe manual summary.

Stop at first failed gate and report exact blocker.
```

## Operator helper

Prepared local helper:

```text
helper=tmp/private_rc_telegram_operation_key_path_retry_gate.ps1
default_key_path=%USERPROFILE%\.ssh\amn2_private_rc_operator_ed25519
default_manual_window_seconds=1800
```

Run command:

```powershell
powershell.exe -NoExit -ExecutionPolicy Bypass -File "C:\Users\SooL\Documents\VPS-OPS-LAB\tmp\private_rc_telegram_operation_key_path_retry_gate.ps1" -ManualWindowSeconds 1800
```

## Final status handling

`PRIVATE_RC_FINAL_STATUS_REFRESH` and `NEXT_CHAT_SYNC_AND_PUSH` remain pending
until the operator provides the safe retry result plus manual summary.
