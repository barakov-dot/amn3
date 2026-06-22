# AMN2 private RC session 0 closeout

Дата: 2026-06-22.

Статус:

```text
private_rc_session_0_closeout_status=completed-docs-only
private_rc_operator_run_gate_status=passed
phase8_private_operator_rc_session_0_status=passed-read-only
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
```

Этот closeout использует результат `PRIVATE_RC_OPERATOR_RUN_GATE`. Он не
открывает live/VPS/config/Telegram/public gates и не выполняет новых
операций.

## 1. Final passed-read-only status

Первая private/operator RC-сессия закрыта как read-only passed.

```text
gate_name=PRIVATE_RC_OPERATOR_RUN_GATE
target_vps=89.185.80.166
run_id=20260622T200016Z
private_rc_operator_run_gate_status=passed
phase8_private_operator_rc_session_0_status=passed-read-only
source_overlay_match=yes
web_login_loopback_http=200
api_loopback_health_status=not-running-no-start-performed
public_listener_guard_status=passed
telegram_get_me_status=passed
external_probe_3030=000
external_probe_3040=000
external_probe_80=000
external_probe_443=000
```

Итоговая формулировка:

```text
AMN2 прошел первую private/operator RC session 0 в read-only режиме.
Public launch по-прежнему не одобрен.
Следующее расширение требует отдельного exact named gate.
```

## 2. Что доказано

Доказано:

- target VPS совпал с `89.185.80.166`;
- AMN2 runtime/source head совпал с
  `187949bffb927a0a6d6c1f260fc0bb9ebb972447`;
- `/opt/amn2`, venv, `.env`, `servers.yml` и DB присутствуют;
- package apply не выполнялся;
- service restart не выполнялся;
- web/admin слушает loopback-only на `127.0.0.1:3030`;
- loopback web health вернул `200`;
- API listener не запущен и не стартовал в рамках gate;
- public listener guard прошел;
- external probes к `3030`, `3040`, `80`, `443` вернули `000`;
- Telegram `getMe` прошел для `@NeobyatnayaAMNZ_bot`;
- bot polling не стартовал;
- Telegram live send не выполнялся;
- Telegram profile/media mutation не выполнялась;
- config generation/delivery не выполнялись;
- secret-bearing payload не выводился;
- admin IDs не печатались, печатались только count/presence markers.

## 3. Что не доказано

Не доказано:

- public launch readiness;
- public web/admin/API exposure;
- Telegram live delivery;
- bot polling;
- config delivery automation;
- fresh Android phone post-RC acceptance;
- QR или полный `vpn://` как release-primary;
- iOS DefaultVPN release acceptance;
- backup restore/import DR;
- provider rebuild;
- production-scale rollout.

Эти пункты остаются за отдельными exact gates.

## 4. Helper issues на будущее

Зафиксированные проблемы helper-а:

```text
helper_encoding_issue=windows_powershell_5_1_mojibake_for_utf8_without_bom
helper_external_probe_url_issue=powershell_interpreted_$TargetIp:3030_as_scoped_variable
```

Impact:

- русские подсказки в Windows PowerShell 5.1 отобразились mojibake;
- initial external probes сформировали malformed URLs вида `http:///...`;
- external probes были корректно повторены вручную с `${TargetIp}` и прошли
  `000/000/000/000`.

Правило для будущих helper scripts:

- использовать ASCII prompts либо сохранять PowerShell scripts в UTF-8 with
  BOM;
- в interpolated URLs использовать `${TargetIp}:PORT`;
- не смешивать русские prompts и Windows PowerShell 5.1 без BOM;
- перед выдачей helper-а прогонять parse check и probe URL dry inspection.

## 5. Stop-lines после session 0

Без нового exact named gate нельзя:

- выполнять live VPS/SSH command;
- выполнять package upload/apply;
- перезапускать сервисы;
- открывать public exposure;
- менять firewall/listener/TLS/reverse proxy/Cloudflare/ngrok;
- генерировать или доставлять config;
- выводить `.conf`, QR, `vpn://`, private key, PSK, token или password;
- выполнять Telegram live send;
- запускать bot polling;
- менять Telegram profile/media;
- выполнять restore/import/reboot;
- выполнять provider rebuild;
- менять production peer/user;
- начинать broader rollout.

## 6. Next exact gates menu

### Safe/operator lane

```text
WAIT_FOR_OPERATOR_REQUEST
PRIVATE_RC_NEXT_CHAT_SYNC
PRIVATE_RC_SESSION_0_EVIDENCE_REVIEW
```

### Mobile/client lane

```text
FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE_REVIEW
FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE
```

### Delivery lane

```text
CONFIG_DELIVERY_GATE_REVIEW
CONFIG_DELIVERY_GATE
TELEGRAM_LIVE_DELIVERY_GATE_REVIEW
TELEGRAM_LIVE_DELIVERY_GATE
```

### Reliability/launch lane

```text
RESTORE_IMPORT_DR_GATE_REVIEW
RESTORE_IMPORT_DR_GATE
PUBLIC_EXPOSURE_GATE_REVIEW
PUBLIC_EXPOSURE_GATE
PRODUCTION_ROLLOUT_GATE_REVIEW
PRODUCTION_ROLLOUT_GATE
```

## 7. Следующие варианты

### Одиночный вариант

Рекомендую как safest next step:

```text
PRIVATE_RC_NEXT_CHAT_SYNC

Использовать существующие Phase 8 evidence и результат PRIVATE_RC_OPERATOR_RUN_GATE.
Не открывать live/VPS/config/Telegram/public gates.
Подготовить короткий next-chat handoff после session 0:
- final passed-read-only status;
- latest pushed heads;
- что доказано/не доказано;
- stop-lines;
- next exact gates menu.
В конце дать следующую рекомендацию.
```

### Двойной вариант

Если нужен следующий практический клиентский шаг, но без открытия live gate:

```text
FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE_REVIEW
+
FRESH_ANDROID_PHONE_POST_RC_RECHECK_PLAN

Использовать существующие Phase 8 evidence.
Не открывать live/VPS/config/Telegram/public gates.
Подготовить review и план fresh Android phone post-RC recheck:
- какие inputs нужны;
- какой телефон/устройство;
- что будет pass/fail;
- какие payload boundaries;
- какие stop-lines.
В конце дать go/no-go и copy/paste команду открытия gate.
```

### Тройной вариант

Если оператор хочет планировать broader launch, но пока без execution:

```text
RESTORE_IMPORT_DR_GATE_REVIEW
+
CONFIG_DELIVERY_GATE_REVIEW
+
PUBLIC_EXPOSURE_GATE_REVIEW

Использовать существующие Phase 8 evidence.
Не выполнять live/VPS/config/Telegram/public действия.
Подготовить три отдельных review/proposal:
- restore/import DR;
- controlled config delivery;
- public exposure.
Разделить gates, stop-lines и pass/fail criteria.
Не смешивать их в один запуск.
```

## 8. Итоговая рекомендация

```text
recommended_next_step=PRIVATE_RC_NEXT_CHAT_SYNC
reason=session_0_passed_and_next_chat_should_start_from_clean_current_truth
```
