# AMN2 private RC Telegram bot live preview gate review

Дата: 2026-06-24.

Статус:

```text
private_rc_telegram_bot_live_preview_review_status=completed-docs-only
gate_name=PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE
gate_opened=false
live_vps_ssh_performed=false
telegram_polling_started=false
telegram_live_send_performed=false
config_generation_performed=false
config_delivery_performed=false
public_exposure_performed=false
secret_values_printed=false
```

Этот review использует только существующие Phase 8 evidence и session 0 result.
Он не открывает live/VPS/config/Telegram/public gates.

## 1. Цель gate

ЦЕЛЬ:
узко включить Telegram bot live preview для private/operator RC, чтобы оператор
и напарник могли посмотреть реальное Telegram-first UX без public exposure и без
config delivery.

Что доказывает:

- bot polling можно запустить контролируемо в private/operator RC runtime;
- бот отвечает в live Telegram только операторским test chats;
- admin/operator UX можно вручную посмотреть;
- bot polling можно остановить в конце gate;
- public web/API exposure остается закрытым;
- config generation/delivery, QR, `vpn://`, keys/PSK/token/password output не
  выполняются.

Что не доказывает:

- production Telegram operation;
- public launch readiness;
- Telegram config delivery;
- payment/support production workflows;
- bot profile/media mutation;
- Android phone acceptance;
- restore/import DR;
- provider rebuild;
- production-scale rollout.

Влияние на близость запуска:

```text
private_operator_rc_bot_confidence_after_pass=higher
public_launch_status_after_pass=still_not_approved_without_separate_public_gate
config_delivery_status_after_pass=still_not_approved_without_separate_config_gate
```

Следующий gate если passed:

```text
PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_CLOSEOUT
```

или `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`, если оператор не открывает следующий gate.

Stop-line если failed:
остановиться на первом failed sub-gate, зафиксировать exact blocker и не
компенсировать failure package apply, service restart, public exposure, config
delivery, Telegram profile/media mutation, restore/import, provider action или
broader rollout без нового exact named gate.

## 2. Target VPS review

```text
target_vps=89.185.80.166
target_review=passed
```

Основание:

- `PRIVATE_RC_OPERATOR_RUN_GATE` подтвердил `target_vps_match=yes`;
- public listener guard passed;
- corrected external probes для `3030`, `3040`, `80`, `443` вернули `000`.

## 3. Expected AMN2 head review

```text
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
expected_amn2_head_review=passed
```

Основание:

- `P8-C002` package/current-head smoke passed на `187949b`;
- `P8-C003` fresh-from-zero rehearsal использовал `187949b`;
- `PRIVATE_RC_OPERATOR_RUN_GATE` подтвердил `source_overlay_match=yes`.

## 4. Existing Telegram evidence

Server-side Telegram checks already passed:

```text
telegram_get_me_status=passed
telegram_api_status=ok
bot_identity_safe=@NeobyatnayaAMNZ_bot
telegram_proxy_status=disabled
bot_dispatcher_construct_status=passed
bot_router_count=1
bot_message_handler_count=4
bot_callback_handler_count=18
user_flow_callback_surface_count=11
admin_flow_callback_surface_count=6
bot_polling_started=false
telegram_live_send_performed=false
telegram_profile_media_mutation_performed=false
config_delivery_payload_output_performed=false
secret_values_printed=false
```

Admin/operator boundary:

```text
admin_telegram_ids_present=true
admin_telegram_ids_count_actual=2
operator_admin_pair_present=yes
admin_telegram_ids_value_printed=false
```

## 5. Allowed actions review

Allowed only inside future `PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE`:

- read-only VPS precheck;
- current runtime/source head check without package apply;
- safe env presence checks without printing token/password values;
- public closed probes for `3030`, `3040`, `80`, `443`;
- start exactly one controlled Telegram bot polling process;
- allow live Telegram replies only in operator/admin test chats;
- allow minimal Telegram user/chat DB state mutation for the two admin/operator
  test chats;
- manual operator UX observation;
- stop bot polling at the end;
- final no-polling/no-public-exposure guard;
- safe evidence without secret-bearing payload.

Not allowed:

- destructive VPS/provider action;
- package upload/apply;
- broad service restart;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation;
- config delivery;
- peer/user production mutation outside the two test chats;
- `.conf`, QR, `vpn://`, private key, PSK, token/password output;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider rebuild;
- production-scale rollout.

Review:

```text
allowed_actions_review=passed
telegram_live_scope_review=passed
config_delivery_boundary_review=passed
public_exposure_boundary_review=passed
db_mutation_boundary_review=passed
```

## 6. Allowed Telegram actions

Allowed operator actions during live preview:

- send `/start` from operator account;
- send `/start` from partner/admin account if available;
- press non-delivery navigation buttons;
- inspect language/header/menu/admin surfaces;
- stop immediately if bot offers or attempts config delivery without a separate
  explicit gate.

Forbidden operator actions during live preview:

- request/create/approve config;
- click buttons that generate or deliver `.conf`, QR, `vpn://`, keys or PSK;
- paste token, config payload or screenshots with payload into chat/evidence;
- mutate bot profile/photo/media through BotFather or Telegram API.

## 7. Allowed admin/operator IDs

Gate scope is limited to the two configured bot admins:

```text
admin_telegram_ids_count_expected=2
operator_admin_pair_required=true
admin_telegram_ids_value_printed=false
```

For operator convenience only, the known private test admins are:

```text
operator_telegram_id=132756019
partner_telegram_id=93455874
```

Evidence must continue to print only count/presence markers, not the ID list,
unless the operator explicitly asks to record IDs in a non-secret planning doc.

## 8. DB mutation boundary

Allowed DB mutations:

```text
telegram_user_chat_state_for_admin_test_chats=allowed
admin_actions_safe_audit_for_preview=allowed
```

Forbidden DB mutations:

```text
new_peer_creation=forbidden
config_material_creation=forbidden
production_user_rollout=forbidden
bulk_user_mutation=forbidden
```

Pass evidence should use aggregate counts only:

```text
users_count_before=<integer>
users_count_after=<integer>
devices_count_before=<integer>
devices_count_after=<integer>
db_rows_printed=false
```

## 9. Polling start/stop criteria

Start criteria:

```text
target_vps_match=yes
source_overlay_match=yes
telegram_token_present=true
admin_telegram_ids_count_actual=2
public_closed_probes_status=passed
existing_bot_polling_process_absent_or_known_safe=true
```

Run criteria:

```text
bot_polling_started=true
telegram_live_replies_limited_to_admin_test_chats=true
config_delivery_performed=false
secret_values_printed=false
```

Stop criteria:

```text
bot_polling_stop_attempted=true
bot_polling_process_after=stopped
public_closed_probes_status_after=passed
telegram_profile_media_mutation_performed=false
```

## 10. Public exposure closed criteria

Public probes must remain closed before and after:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

PowerShell helper must use `${TargetIp}:PORT` URL interpolation and pass dry URL
inspection before operator handoff.

## 11. Pass/fail criteria

Gate passes only if all are true:

```text
target_vps_match=yes
source_overlay_match=yes
telegram_get_me_status=passed
admin_telegram_ids_count_actual=2
bot_polling_started=true
operator_start_flow_observed=passed
partner_start_flow_observed=passed_or_not_available_explicitly_recorded
config_delivery_performed=false
secret_values_printed=false
telegram_profile_media_mutation_performed=false
bot_polling_process_after=stopped
public_closed_probes_status_after=passed
```

Gate fails on any one:

```text
telegram_token_missing=true
admin_telegram_ids_count_actual_not_2=true
bot_polling_start_failed=true
bot_replies_to_non_admin_unapproved_chat=true
config_delivery_attempted=true
secret_payload_output_detected=true
public_probe_not_closed=true
bot_polling_stop_failed=true
```

## 12. GO / NO-GO

```text
review_go=true
gate_open_go=conditional-go-with-explicit-operator-approval
operator_can_open_gate_now=true
```

Причина:
телефон Android для этого gate не нужен. Gate является live Telegram action,
поэтому его нельзя выполнять без отдельного явного открытия оператором.

## 13. Copy/paste command для открытия gate

```text
PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE

Открыть exact gate для private/operator Telegram bot live preview.

Использовать существующие Phase 8 evidence и session 0 result.
Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Allowed:
- read-only VPS precheck;
- current runtime/source head check without package apply;
- safe env presence checks without printing token/password values;
- public closed probes for 3030, 3040, 80, 443;
- start exactly one controlled Telegram bot polling process;
- allow live Telegram replies only to operator/admin test chats:
  132756019,93455874;
- allow minimal Telegram user/chat DB state mutation for these test chats only;
- manual operator UX observation;
- stop bot polling at the end;
- final no-polling/no-public-exposure guard;
- safe evidence without secret-bearing payload.

Forbidden:
- destructive VPS/provider action;
- package upload/apply;
- broad service restart;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation or config delivery;
- peer creation;
- .conf/QR/vpn:// output;
- private key/PSK/token/password output;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider rebuild;
- production rollout.

Stop at first failed gate and report the exact blocker.
```
