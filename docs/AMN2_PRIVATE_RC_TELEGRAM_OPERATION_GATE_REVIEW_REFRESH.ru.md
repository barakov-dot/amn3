# PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW_REFRESH

Дата: 2026-06-26.

Статус: `completed-docs-only`.

Использованы существующие Phase 8 evidence:

- `PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW`;
- `PRIVATE_RC_TELEGRAM_OPERATION_BLOCKER_RECORD`;
- `PRIVATE_RC_SSH_TRANSPORT_STABILIZATION_REVIEW`;
- `PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_RESULT`;
- `AMN2_HELPER_STYLE_HARDENING`.

Live/VPS/SSH/config/Telegram/public gates этим refresh не открывались.

## Refresh verdict

```text
review_refresh_go=true
old_execution_helper_retry_go=false
new_execution_gate_go=conditional-go-with-explicit-operator-approval
recommended_next_gate=PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_GATE
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
required_transport_model=single-session-no-scp-lf-normalized
public_launch_status=not-approved
config_delivery_status=not-approved
production_rollout_status=not-approved
```

Старый `PRIVATE_RC_TELEGRAM_OPERATION_GATE` helper нельзя повторять. Он
использовал SCP/helper upload и несколько SSH/SCP-сессий, что уже привело к
intermittent SSH/SCP close. Новый execution gate должен быть отдельным exact
gate с single-session/no-SCP дизайном.

## Что изменилось после первого review

Было:

```text
recommended_execution_gate=PRIVATE_RC_TELEGRAM_OPERATION_GATE
transport_model=multi-session-plus-helper-upload
```

Теперь:

```text
recommended_execution_gate=PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_GATE
transport_model=single-session-no-scp-lf-normalized
scp_helper_upload_allowed=false
remote_temp_helper_file_allowed=false
remote_stdin_bash_lf_normalization_required=true
```

## Основание

Уже доказано:

```text
telegram_getme=passed
private_rc_telegram_bot_live_preview_status=passed-with-manual-operator-observation
operator_start_flow_observed=passed
bot_polling_start_stop_preview=passed
public_closed_probes_before_after=passed
android_private_operator_rc_proof=complete-with-explicit-limitations
ssh_single_session_diagnostic=passed-with-helper-crlf-exit-issue
single_session_strategy_status=validated
source_overlay_match=yes
no_telegram_polling_process=true
public_closed_probes_before_status=passed
public_closed_probes_after_manual_status=passed
```

Первый Telegram operation attempt не доказал bot failure:

```text
first_operation_attempt_status=blocked-by-intermittent-ssh-transport
telegram_bot_application_failure=false
config_delivery_performed=false
peer_creation_performed=false
public_exposure_status=closed
```

## Required execution design

Будущий execution gate должен:

- выполнять local public closed probes до SSH-сеанса;
- открыть один SSH-сеанс;
- в этом одном SSH-сеансе сделать read-only precheck;
- в этом же SSH-сеансе запустить controlled polling;
- дать оператору ручное окно проверки `/start`;
- в этом же SSH-сеансе остановить polling;
- в этом же SSH-сеансе выполнить final no-polling guard;
- после завершения выполнить local public closed probes;
- не использовать SCP/helper upload;
- не создавать remote temp helper files;
- нормализовать remote bash text в LF перед передачей в `ssh ... bash -s`;
- не печатать raw process list, raw auth logs, tokens, configs, DB rows,
  `.conf`, QR, `vpn://`, private key или PSK.

## Allowed actions for next execution gate

Разрешить только внутри будущего
`PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_GATE`:

- local public closed probes for `3030`, `3040`, `80`, `443`;
- exactly one SSH login/session;
- current runtime/source head check without package apply;
- safe env presence checks without printing token/password values;
- Telegram `getMe`;
- start exactly one controlled Telegram bot polling process;
- allow live Telegram replies only to approved admin/operator chats;
- allow minimal Telegram user/chat/session DB state mutation for approved
  admin/operator chats only;
- manual operator UX check;
- stop bot polling at the end;
- final no-polling/no-public-exposure guard;
- safe evidence only.

Approved admin/operator boundary:

```text
admin_operator_count_expected=2
operator_admin_pair_expected=true
admin_ids_value_output_allowed=false
```

## Forbidden actions

Запрещено:

- destructive VPS/provider action;
- package upload/apply;
- SCP/helper upload;
- remote temp helper files;
- broad service restart;
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

Execution gate passes only if:

```text
target_vps_match=yes
ssh_session_count=1
scp_helper_upload_performed=false
remote_temp_helper_file_created=false
remote_stdin_bash_lf_normalization_verified=true
source_overlay_match=yes
telegram_get_me_status=passed
public_closed_probes_before_status=passed
exactly_one_bot_polling_process_started=true
operator_start_flow_observed=passed
partner_start_flow_observed=passed_or_not_available_explicitly_recorded
config_delivery_attempted=false
peer_creation_performed=false
bot_polling_process_after=stopped
unexpected_bot_polling_process_after=absent
public_closed_probes_after_status=passed
secret_values_printed=false
```

## Fail criteria / stop-lines

Stop immediately if:

- target VPS is not `89.185.80.166`;
- AMN2 source/runtime head is not
  `187949bffb927a0a6d6c1f260fc0bb9ebb972447`;
- helper wants SCP/helper upload;
- helper creates remote temp helper file;
- helper does not LF-normalize stdin bash;
- public probes are not closed before polling;
- existing unknown bot polling process is present;
- more than one polling process would be started;
- bot token/settings load fails;
- bot replies to non-approved chats/users during test;
- UI offers or triggers config delivery unexpectedly;
- any `.conf`, QR, `vpn://`, key, PSK, token/password would be printed;
- helper would create peer/config;
- service/package/public/firewall/TLS/proxy mutation appears;
- stop polling fails at the end;
- final public probes are not closed.

## Exact copy/paste execution gate command

```text
PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_GATE

Открыть exact gate для controlled private/operator Telegram bot operation
через single-session/no-SCP transport.

Использовать существующие Phase 8 evidence:
- PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW_REFRESH;
- PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_RESULT;
- PRIVATE_RC_TELEGRAM_OPERATION_BLOCKER_RECORD.

Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Allowed:
- local public closed probes for 3030, 3040, 80, 443 before and after;
- exactly one SSH login/session for remote checks, controlled polling,
  manual operator window and stop/final guard;
- current runtime/source head check without package apply;
- safe env presence checks without printing token/password values;
- Telegram getMe;
- start exactly one controlled Telegram bot polling process;
- allow live Telegram replies only to approved admin/operator chats;
- allow minimal Telegram user/chat/session DB state mutation for approved
  admin/operator chats only;
- manual operator UX check;
- stop bot polling at the end;
- final no-polling/no-public-exposure guard;
- safe evidence without secret-bearing payload.

Forbidden:
- destructive VPS/provider action;
- package upload/apply;
- SCP/helper upload;
- remote temp helper files;
- broad service restart;
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

## Recommendation

```text
recommended_next_step=PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_GATE
old_private_rc_telegram_operation_gate_retry_go=false
```

Если оператор не хочет live Telegram polling прямо сейчас:

```text
recommended_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```
