# AMN2 fresh Android phone post-RC recheck runbook

Дата: 2026-06-22.

Статус:

```text
fresh_android_phone_post_rc_recheck_runbook_status=prepared-docs-only
gate_name=FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE
gate_opened=false
live_vps_ssh_performed=false
config_generation_performed=false
config_delivery_performed=false
telegram_live_send_performed=false
public_exposure_performed=false
secret_values_printed=false
```

Runbook готовит будущий gate на момент, когда Android phone снова будет у
оператора. Сейчас gate не открыт.

## 1. Before opening the gate

Проверить руками:

```text
android_phone_available=yes
android_phone_charged=yes
android_phone_network_available=yes
android_phone_amneziawg_available=yes
private_handoff_path_exists=yes
private_handoff_path_outside_workspace=yes
vps_ssh_password_available_privately=yes
```

Команда для private handoff path:

```powershell
Test-Path "C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF"
```

Ожидаемо:

```text
True
```

Если телефона нет, не открывать gate.

## 2. Gate opening command

Copy/paste только когда Android phone доступен:

```text
FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE

Открыть exact gate для post-RC Android phone recheck.

Использовать существующие Phase 8 evidence и session 0 result.
Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Android phone readiness:
- Android phone is physically available now.
- Android phone has AmneziaWG installed or can install it before import.
- Android phone can import a private `.conf` file.
- Android phone can generate browser/app traffic after connect.
- Telegram on-device is optional; browser/app traffic is accepted.

Private handoff boundary:
- Private local destination outside workspace:
  C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
- Do not paste `.conf`, QR, vpn://, private key, PSK, token or password into
  chat/evidence.

Allowed only:
- read-only VPS precheck;
- current runtime/source head check without package apply;
- public closed probes for 3030, 3040, 80, 443;
- create exactly one fresh Android phone peer/config through AMN2 path;
- copy exactly one `.conf` to private handoff destination outside workspace;
- read-only server-side observation of the fresh peer;
- Android phone import/connect/browser-or-app traffic acceptance;
- safe evidence without secret-bearing payload.

Forbidden:
- destructive VPS/provider action;
- package upload/apply;
- service restart;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- Telegram live send;
- bot polling;
- Telegram profile/media mutation;
- QR/vpn:// output;
- `.conf` payload output;
- private key/PSK/token/password output;
- restore/import/reboot;
- provider rebuild;
- production-scale rollout.

Stop at first failed gate and report the exact blocker.
```

## 3. Operator prompts style for future helper

PowerShell helper должен использовать правила:

```text
helper_encoding_rule=ascii_prompts_or_utf8_with_bom
url_interpolation_rule=${TargetIp}:PORT_or_$($TargetIp):PORT
parse_check_required=true
probe_url_dry_inspection_required=true
```

Если helper содержит русские prompts, сохранить `.ps1` как UTF-8 with BOM. Если
BOM не гарантирован, prompts в `.ps1` должны быть ASCII-only, а русская
инструкция остается в этом Markdown.

## 4. Safe local inputs

Параметры будущего helper-а:

```text
PrivateDestinationDir=C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
TargetOperatorTelegramId=132756019
AdminTelegramIds=132756019,93455874
TargetIp=89.185.80.166
ExpectedHead=187949bffb927a0a6d6c1f260fc0bb9ebb972447
```

`TargetOperatorTelegramId` можно заменить только если оператор явно выбирает
другой private test owner и понимает, что config будет привязан к этому
операторскому контексту.

## 5. Android phone steps during gate

Когда helper создаст и скопирует private `.conf`:

1. Удалить старые тестовые configs из AmneziaWG на телефоне, чтобы не путаться.
2. Импортировать только новый private `.conf` из
   `C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF`.
3. Не отправлять файл, QR, `vpn://`, keys, PSK или screenshots с payload в чат.
4. Включить tunnel.
5. Дождаться connected/on state.
6. Открыть browser или любое приложение, которое генерирует интернет-трафик.
7. Держать tunnel включенным до окончания server-side observation.

Что написать в чат после ручной части:

```text
android_phone_import_status=passed
android_phone_connect_status=passed
android_phone_traffic_attempted=browser_or_app
payload_screenshot_shared=false
```

Если ошибка:

```text
android_phone_import_status=failed
android_phone_error_text=<только текст ошибки, без payload>
payload_screenshot_shared=false
```

## 6. Server-side observation criteria

Baseline с VPN off:

```text
fresh_peer_found=yes
latest_handshake_age_s=never_or_old
endpoint_observed=no_or_old
```

After traffic with VPN on:

```text
fresh_peer_found=yes
endpoint_observed_after=yes
fresh_handshake_after=yes
transfer_rx_delta_bytes_gt_0=true
transfer_tx_delta_bytes_gt_0=true
```

Pass:

```text
android_phone_import_status=passed
android_phone_connect_status=passed
android_phone_traffic_status=passed
fresh_android_phone_server_counter_growth=passed
```

Fail:

```text
fresh_peer_found=no
fresh_handshake_after=no
endpoint_observed_after=no
transfer_counter_growth_missing=true
```

## 7. Stop-lines

Остановиться сразу, если:

- Android phone недоступен;
- private destination внутри workspace;
- helper пытается вывести `.conf`, QR, `vpn://`, private key, PSK, token или
  password;
- helper предлагает public exposure;
- helper предлагает package apply/restart/destructive action;
- helper предлагает Telegram live send или bot polling;
- server-side observation не видит handshake/endpoint/counter growth;
- оператор не может подтвердить import/connect/traffic без payload.

## 8. Result labels

Успешный итог:

```text
fresh_android_phone_post_rc_recheck_status=passed
phase8_private_operator_rc_mobile_confidence=post_rc_phone_rechecked
public_launch_status=not-approved-without-separate-public-gate
```

Неуспешный итог:

```text
fresh_android_phone_post_rc_recheck_status=blocked
exact_blocker=<one_exact_blocker>
next_gate_required=<specific_review_or_fix_gate>
```

## 9. Что делать после gate

Если passed:

```text
FRESH_ANDROID_PHONE_POST_RC_RECHECK_CLOSEOUT
```

Если failed:

```text
FRESH_ANDROID_PHONE_POST_RC_RECHECK_BLOCKER_ANALYSIS
```

Если телефона снова нет:

```text
ANDROID_PHONE_BLOCKER_HOLD
```
