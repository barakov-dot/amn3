# AMN2 private RC Telegram bot live preview runbook

Дата: 2026-06-24.

Статус:

```text
private_rc_telegram_bot_live_preview_runbook_status=prepared-docs-only
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

Runbook готовит будущий live Telegram preview gate. Сейчас polling не
запускается.

## 1. Before opening the gate

Оператор должен подтвердить:

```text
vps_ssh_access_available_privately=yes
telegram_operator_account_available=yes
telegram_partner_account_available=yes_or_not_available
bot_token_available_on_vps=yes
target_vps=89.185.80.166
expected_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
```

Подсказка:
если напарник недоступен, gate может пройти с limitation
`partner_start_flow_observed=not_available_explicitly_recorded`, но тогда это
не доказывает live UX для второго админа.

## 2. Gate opening command

Copy/paste:

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

## 3. Helper style requirements

Future PowerShell helper must follow:

```text
helper_encoding_rule=ascii_prompts_or_utf8_with_bom
url_interpolation_rule=${TargetIp}:PORT_or_$($TargetIp):PORT
parse_check_required=true
probe_url_dry_inspection_required=true
```

If `.ps1` is UTF-8 without BOM, prompts must be ASCII-only. Russian operator
instructions stay in this Markdown.

## 4. Safe expected helper prompts

Для будущего helper-а использовать copy-only значения без labels:

```text
Type PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_CONFIRMED:
PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_CONFIRMED

Type READ_ONLY_PLUS_CONTROLLED_BOT_POLLING_CONFIRMED:
READ_ONLY_PLUS_CONTROLLED_BOT_POLLING_CONFIRMED

Type NO_CONFIG_DELIVERY_NO_PUBLIC_EXPOSURE_CONFIRMED:
NO_CONFIG_DELIVERY_NO_PUBLIC_EXPOSURE_CONFIRMED

Type STOP_BOT_POLLING_AT_END_CONFIRMED:
STOP_BOT_POLLING_AT_END_CONFIRMED
```

## 5. Manual Telegram UX steps

После controlled polling start:

1. Оператор открывает `@NeobyatnayaAMNZ_bot`.
2. Оператор отправляет `/start`.
3. Оператор смотрит header/language/main menu/admin-visible surface.
4. Оператор не нажимает delivery/approve/config buttons.
5. Если напарник доступен, напарник отправляет `/start` и смотрит тот же
   базовый UX.
6. Если бот предлагает config delivery, QR, `vpn://` или `.conf`, остановиться
   и зафиксировать `config_delivery_attempted=true`.
7. После ручной проверки оператор пишет в чат только safe summary.

Safe summary после ручной части:

```text
operator_start_flow_observed=passed
partner_start_flow_observed=passed
config_delivery_attempted=false
payload_screenshot_shared=false
unexpected_error_text=none
```

Если напарник недоступен:

```text
operator_start_flow_observed=passed
partner_start_flow_observed=not_available_explicitly_recorded
config_delivery_attempted=false
payload_screenshot_shared=false
```

Если есть ошибка:

```text
operator_start_flow_observed=failed
unexpected_error_text=<только текст ошибки, без token/config/payload>
payload_screenshot_shared=false
```

## 6. Server-side observation criteria

Before polling:

```text
target_vps_match=yes
source_overlay_match=yes
telegram_get_me_status=passed
admin_telegram_ids_count_actual=2
public_closed_probes_status_before=passed
bot_polling_process_before=absent_or_known_safe
```

During polling:

```text
bot_polling_started=true
telegram_live_replies_limited_to_admin_test_chats=true
config_delivery_performed=false
secret_values_printed=false
```

After stop:

```text
bot_polling_stop_attempted=true
bot_polling_process_after=stopped
public_closed_probes_status_after=passed
telegram_profile_media_mutation_performed=false
```

## 7. DB mutation boundary

Allowed:

```text
telegram_user_chat_state_for_admin_test_chats=allowed
admin_actions_safe_audit_for_preview=allowed
```

Evidence:

```text
users_count_before=<integer>
users_count_after=<integer>
devices_count_before=<integer>
devices_count_after=<integer>
db_rows_printed=false
```

Forbidden:

```text
new_peer_creation=forbidden
config_material_creation=forbidden
bulk_user_mutation=forbidden
```

## 8. Public exposure closed probes

Expected before and after:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

If any probe is not `000`, stop and report exact blocker.

## 9. Pass/fail labels

Pass:

```text
private_rc_telegram_bot_live_preview_status=passed
operator_start_flow_observed=passed
partner_start_flow_observed=passed_or_not_available_explicitly_recorded
config_delivery_performed=false
bot_polling_process_after=stopped
public_exposure_performed=false
```

Fail:

```text
private_rc_telegram_bot_live_preview_status=blocked
exact_blocker=<one_exact_blocker>
next_gate_required=<specific_review_or_fix_gate>
```

## 10. Stop-lines

Остановиться сразу, если:

- target/source head mismatch;
- Telegram token missing;
- admin count не равен `2`;
- bot polling уже запущен неизвестным процессом;
- bot polling не стартует;
- бот отвечает неразрешенному чату;
- бот предлагает или выполняет config delivery;
- выводится token/config/private key/PSK/password;
- public probe становится open;
- bot polling не удается остановить.

## 11. Что делать после gate

Если passed:

```text
PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_CLOSEOUT
```

Если failed:

```text
PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_BLOCKER_ANALYSIS
```

Если оператор не открывает live gate:

```text
ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```
