# AMN2 private RC operator run gate proposal

Дата: 2026-06-22.

Статус:

```text
operator_run_gate_proposal_status=prepared-not-opened
gate_name=PRIVATE_RC_OPERATOR_RUN_GATE
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
```

Этот proposal готовит exact gate для первой реальной private/operator
RC-сессии. Он не открывает gate и не выполняет live/VPS/config/Telegram/public
действия.

## 1. Назначение gate

`PRIVATE_RC_OPERATOR_RUN_GATE` нужен для короткой контролируемой операторской
сессии, которая подтверждает private/operator RC режим без public exposure,
без config delivery и без Telegram live delivery.

## 2. Разрешено внутри gate

Разрешить только:

```text
read_only_vps_observation_allowed=true
loopback_web_api_health_allowed=true
telegram_getme_allowed=true
telegram_live_send_allowed=false
bot_polling_allowed=false
public_exposure_allowed=false
config_delivery_allowed=false
package_apply_allowed=false
service_restart_allowed=false
restore_import_allowed=false
provider_rebuild_allowed=false
secret_payload_output_allowed=false
```

## 3. Pass criteria

Gate считается passed, если:

- target VPS подтвержден как `89.185.80.166`;
- runtime/package line соответствует AMN2 `187949b`;
- web/admin/API остаются private/loopback-only;
- external probes к `3030`, `3040`, `80`, `443` остаются closed;
- Telegram `getMe` проходит, если token доступен приватно;
- bot polling не стартовал;
- Telegram live send не выполнялся;
- config delivery не выполнялась;
- secret-bearing payload не выводился;
- evidence содержит только safe metadata.

## 4. Stop-lines

Остановиться сразу, если:

- target VPS не `89.185.80.166`;
- runtime head не соответствует ожидаемому AMN2 `187949b`;
- обнаружена public exposure;
- требуется service restart или package apply;
- требуется config delivery;
- требуется Telegram live send;
- требуется bot polling;
- требуется вывод `.conf`, QR, `vpn://`, private key, PSK, token или password;
- требуется restore/import/reboot;
- требуется provider rebuild;
- возникает любой failed smoke или ambiguous evidence.

## 5. Copy/paste команда открытия gate

```text
PRIVATE_RC_OPERATOR_RUN_GATE

Открыть exact gate для первой private/operator RC-сессии.

Использовать существующие Phase 8 evidence.
Target VPS: 89.185.80.166.
Expected AMN2 runtime/package head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.
AMN3 evidence head at proposal time:
799ff79 Record wait for operator request.

Разрешено только:
- read-only VPS observation;
- loopback web/API health check;
- Telegram getMe без live send, без polling, без profile/media mutation;
- external closed probes для 3030, 3040, 80, 443;
- safe evidence без secret-bearing payload.

Запрещено:
- destructive VPS/provider action;
- package upload/apply;
- service restart;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation или config delivery;
- .conf/QR/vpn:// output;
- private key/PSK/token/password output;
- Telegram live send;
- bot polling;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider rebuild;
- production peer/user mutation;
- broader rollout.

Stop at first failed gate and report the exact blocker.
```

## 6. Go/no-go

```text
operator_run_gate_proposal_go=true
operator_run_gate_opened=false
reason=proposal_is_docs_only_and_contains_stop_lines
```

Решение: proposal готов к операторскому review. Gate не открыт.
