# AMN2 private/operator RC session 0 plan

Дата: 2026-06-22.

Статус:

```text
session_0_plan_status=prepared-docs-only
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
wait_operator_request_status=active-docs-only
```

Этот план использует только существующие Phase 8 evidence. Он не открывает
live/VPS/config/Telegram/public gates и не является разрешением на запуск
операторской RC-сессии.

## 1. Цель session 0

Цель:

```text
подготовить первую контролируемую private/operator RC-сессию без расширения
scope за пределы уже зафиксированного Phase 8 private/operator RC статуса
```

Session 0 должна быть короткой операторской проверкой, а не новым запуском
продукта наружу.

Она нужна, чтобы оператор мог безопасно подтвердить:

- текущие документы и evidence понятны;
- public exposure остается закрытой;
- операторский контур не требует public web/admin/API;
- Telegram остается server-side/non-polling до отдельного gate;
- config delivery остается закрытым до отдельного gate;
- private handoff artifacts остаются вне workspace;
- любые расширения упираются в named gates.

## 2. Что доказывает session 0

При открытии будущего `PRIVATE_RC_OPERATOR_RUN_GATE` session 0 может доказать:

- оператор работает в правильном private/operator RC scope;
- текущий AMN2 head/package line совпадает с Phase 8 evidence;
- public probes остаются закрытыми;
- web/admin/API используются только в приватном операторском контуре;
- Telegram bot token может быть проверен через безопасный `getMe` без live
  send и без polling;
- secret-bearing payload не попадает в chat/evidence;
- stop-lines срабатывают до config delivery, public exposure, restore/import
  или broader rollout.

## 3. Что session 0 не доказывает

Session 0 не доказывает:

- public launch readiness;
- public web/admin/API exposure;
- Telegram live delivery;
- bot polling;
- production config delivery automation;
- QR или полный `vpn://` как release-primary;
- iOS DefaultVPN acceptance;
- backup restore/import DR;
- provider rebuild;
- production-scale rollout.

## 4. Inputs перед открытием gate

Перед реальным открытием `PRIVATE_RC_OPERATOR_RUN_GATE` оператор должен
подтвердить:

```text
target_vps=89.185.80.166
amn2_runtime_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
amn3_evidence_head_at_plan_time=799ff79 Record wait for operator request
public_exposure_must_remain_closed=true
config_delivery_allowed=false
telegram_live_send_allowed=false
bot_polling_allowed=false
restore_import_allowed=false
provider_rebuild_allowed=false
secret_payload_output_allowed=false
```

Операторские private inputs:

- доступ к VPS SSH password или приватному SSH способу;
- Telegram bot token доступен приватно только если gate включает `getMe`;
- web/admin private credentials доступны приватно, если оператор будет входить
  через приватный web/admin контур;
- private handoff directory остается вне workspace:
  `C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF`.

## 5. Разрешенный контур будущего gate

В будущем `PRIVATE_RC_OPERATOR_RUN_GATE` разрешить только:

- read-only live VPS observation;
- проверку текущего source/runtime head без package apply;
- проверку loopback web/admin/API health без public exposure;
- безопасный Telegram `getMe` без send/polling/profile/media mutation;
- external closed probes к `3030`, `3040`, `80`, `443`;
- проверку, что private handoff artifacts не попали в workspace;
- формирование safe evidence без payload.

## 6. Запрещено в session 0

Даже внутри будущего operator run gate нельзя:

- destructive VPS/provider action;
- package upload/apply;
- service restart;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- public exposure;
- Telegram live send;
- bot polling;
- Telegram profile/media mutation;
- config generation или config delivery;
- вывод `.conf`, QR, `vpn://`, private key, PSK, token или password;
- backup restore/import/reboot;
- provider rebuild;
- production peer/user mutation;
- broader rollout.

## 7. Session 0 checklist

До live части:

- прочитать `docs/AMN2_PRIVATE_OPERATOR_RC_CLOSEOUT.ru.md`;
- прочитать `docs/AMN2_PRIVATE_OPERATOR_RC_WAIT_OPERATOR_REQUEST.ru.md`;
- подтвердить, что оператор открывает именно `PRIVATE_RC_OPERATOR_RUN_GATE`;
- подтвердить, что это не config delivery и не Telegram live delivery;
- подтвердить, что public exposure остается closed-by-default.

Во время будущего gate:

- получить read-only runtime summary;
- получить loopback-only health summary;
- получить Telegram `getMe` safe status, если token доступен приватно;
- получить external closed probes;
- записать safe evidence;
- остановиться при первом failed gate.

После gate:

- обновить docs/evidence;
- записать pass/fail;
- не переходить к config delivery без отдельного gate;
- не переходить к public exposure без отдельного gate.

## 8. Go/no-go по плану

```text
private_rc_session_0_plan_go=true
reason=plan_is_docs_only_and_gate_proposal_is_separate
live_action_opened=false
```

План можно использовать для подготовки реального gate. Сам план не разрешает
запуск live-действий.

## 9. Следующий gate proposal

Для открытия реальной operator run session использовать:

```text
docs/AMN2_PRIVATE_RC_OPERATOR_RUN_GATE_PROPOSAL.ru.md
```
