# AMN2 private RC Telegram partner admin preview review

Дата: 2026-06-25.

Статус:

```text
private_rc_telegram_partner_admin_preview_review_status=completed-docs-only
gate_name=PRIVATE_RC_TELEGRAM_PARTNER_ADMIN_PREVIEW_GATE
gate_opened=false
live_vps_ssh_performed=false
telegram_polling_started=false
telegram_live_send_performed=false
config_generation_performed=false
config_delivery_performed=false
public_exposure_performed=false
secret_values_printed=false
```

Этот review использует существующие Phase 8 evidence и private RC Telegram bot
live preview result. Он не открывает live/VPS/config/Telegram/public gates.

## 1. Почему нужен этот gate

`PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE` прошел с операторским `/start`:

```text
operator_start_flow_observed=passed
partner_start_flow_observed=not_reported
bot_polling_started=true
bot_polling_process_after=stopped
config_delivery_performed=false
public_exposure_performed=false
secret_values_printed=false
```

Для полного admin-pair confidence можно отдельно подтвердить, что второй админ
также видит ожидаемый Telegram UX без config delivery.

## 2. Цель gate

ЦЕЛЬ:
узко проверить partner/admin Telegram `/start` и базовую navigation/admin
surface для второго админа без config delivery, peer creation и public exposure.

Что доказывает:

- второй admin/operator chat может получить live bot response;
- admin-pair boundary работает в реальном Telegram UX;
- bot polling can start/stop under controlled preview;
- public exposure remains closed;
- config delivery remains closed.

Что не доказывает:

- production bot operation;
- non-admin denial behavior;
- config delivery;
- public launch;
- DB runtime discrepancy;
- Android phone acceptance;
- restore/import DR.

## 3. Preconditions

Required before opening future gate:

```text
partner_admin_available=true
partner_admin_can_send_start=true
operator_can_watch_power_shell=true
config_delivery_not_requested=true
payload_screenshot_shared=false
```

If partner is not available:

```text
gate_open_go=no-go-until-partner-admin-available
```

## 4. Allowed actions

Allowed only inside future `PRIVATE_RC_TELEGRAM_PARTNER_ADMIN_PREVIEW_GATE`:

- read-only VPS precheck if SSH transport works;
- safe env/admin count presence checks without values;
- public closed probes before/after;
- start exactly one controlled Telegram bot polling process;
- allow live Telegram replies only to the two admin/operator test chats;
- partner sends `/start`;
- operator optionally sends `/start` only as control;
- manual UX observation;
- stop polling at the end;
- final no-polling/no-public-exposure guard.

Forbidden:

- config generation/delivery;
- clicking/requesting `.conf`, QR, `vpn://`, approve, create config or peer actions;
- peer creation;
- package upload/apply;
- service restart except the controlled polling process itself;
- public exposure changes;
- Telegram profile/media mutation;
- DB row dump/download;
- restore/import/reboot;
- provider rebuild;
- production rollout;
- secret output.

## 5. Pass/fail criteria

Pass if all true:

```text
partner_admin_available=true
bot_polling_started=true
partner_start_flow_observed=passed
config_delivery_attempted=false
payload_screenshot_shared=false
bot_polling_process_after=stopped
public_closed_probes_after_status=passed
secret_values_printed=false
```

Fail if any true:

```text
partner_admin_not_available=true
bot_polling_start_failed=true
partner_start_flow_failed=true
config_delivery_attempted=true
secret_payload_output_detected=true
bot_polling_stop_failed=true
public_probe_not_closed=true
```

## 6. Stop-lines

Stop immediately if:

```text
config_delivery_button_clicked_or_requested=true
bot_offers_unexpected_config_delivery=true
non_admin_chat_gets_reply_inside_gate=true
secret_payload_visible_in_evidence=true
public_probe_not_closed=true
bot_polling_stop_failed=true
```

Do not compensate with package apply, restart, public exposure, config delivery,
restore/import, provider action or broader rollout.

## 7. GO / NO-GO

```text
review_go=true
gate_open_go=conditional-no-go-until-partner-admin-available
operator_can_open_gate_now=false_unless_partner_available
```

Причина:
этот gate имеет смысл только когда второй админ реально доступен и готов
отправить `/start`. Android phone для него не нужен.

## 8. Copy/paste command

```text
PRIVATE_RC_TELEGRAM_PARTNER_ADMIN_PREVIEW_GATE

Открыть exact gate для private/operator Telegram partner admin live preview.

Использовать существующие Phase 8 evidence и private RC Telegram bot live preview result.
Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Private readiness:
- partner/admin 93455874 is available and can send /start;
- operator/admin 132756019 is available for control observation;
- no screenshots with payload will be posted;
- config delivery will not be requested.

Allowed:
- read-only VPS precheck if SSH transport works;
- safe env/admin count checks without printing token/password/admin ID values;
- public closed probes for 3030, 3040, 80, 443;
- start exactly one controlled Telegram bot polling process;
- allow live Telegram replies only to operator/admin test chats;
- partner/admin sends /start;
- optional operator/admin /start control check;
- manual UX observation;
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
- DB row dump or DB download/copy;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider rebuild;
- production rollout.

Stop at first failed gate and report the exact blocker.
```
