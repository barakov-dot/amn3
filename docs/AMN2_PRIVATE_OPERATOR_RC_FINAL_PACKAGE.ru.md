# AMN2 private/operator RC final package

Дата: 2026-06-22.

Статус:

```text
final_package_status=prepared-docs-only
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
blocked_with_exact_remaining_blockers=false
```

Этот документ является финальным индексом private/operator RC package. Он
использует только существующие Phase 8 evidence и не открывает live,
destructive, config delivery, Telegram send или public exposure gates.

## 1. Финальный вывод

AMN2 готов к private/operator RC с явными ограничениями.

Короткая формулировка:

```text
Private/operator RC launch-ready with explicit limitations.
Public launch is not approved.
```

Практическая формулировка для оператора:

```text
AMN2 можно запускать в закрытом private/operator RC режиме:
operator web/admin остается приватным, public exposure закрыта,
основной handoff-артефакт - приватный .conf,
Android AmneziaWG принят как основной мобильный кандидат,
а любые расширения требуют отдельного exact named gate.
```

## 2. Основные документы пакета

### Операторская памятка

```text
docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md
```

Назначение:

- финальный статус;
- разрешенный private/operator RC scope;
- явные ограничения;
- стоп-линии;
- future gates для расширения.

### Операторский чеклист

```text
docs/AMN2_PRIVATE_OPERATOR_RC_RUN_CHECKLIST.ru.md
```

Назначение:

- что проверить перед работой;
- как держать public exposure закрытой;
- где находятся private handoff artifacts;
- Telegram/config delivery/backup boundaries;
- какие gates нужны для broader action.

## 3. Evidence chain

### P8-C001

```text
research/amn2/phase-8-p8-c001-fresh-android-config-acceptance-2026-06-21.md
```

Доказательство:

- fresh Android phone `.conf` acceptance;
- import/connect/traffic passed;
- reconnect sanity passed;
- no payload output;
- no public exposure;
- no Telegram live send.

### P8-C002

```text
research/amn2/phase-8-p8-c002-187949b-package-apply-smoke-2026-06-21.md
```

Доказательство:

- AMN2 `187949b` package/current-head smoke;
- source overlay match;
- compatible AWG defaults persisted;
- loopback web/API smoke passed;
- Telegram `getMe` plus non-polling bot surface passed;
- backup create+verify passed;
- public probes stayed closed.

### P8-C003

```text
research/amn2/phase-8-p8-c003-fresh-zero-rehearsal-2026-06-22.md
```

Доказательство:

- fresh `/opt/amn2` runtime rehearsal passed;
- source overlay `187949b` matched;
- fresh env/DB init passed;
- two Telegram bot admins verified without printing IDs;
- loopback web/API passed;
- Telegram server-side smoke passed;
- backup create+verify passed;
- private `.conf` handoff completed outside workspace;
- Android projector traffic observation passed;
- public probes stayed closed.

### P8-SFINAL

```text
research/amn2/phase-8-sfinal-launch-readiness-freeze-2026-06-22.md
```

Доказательство:

- final verdict recorded;
- private/operator RC ready;
- public launch not approved;
- exact limitations recorded;
- no new live action in freeze.

### RC handoff

```text
research/amn2/phase-8-rc-handoff-2026-06-22.md
```

Доказательство:

- operator-facing handoff prepared;
- allowed scope and stop-lines recorded;
- future exact gates listed.

### RC run checklist

```text
research/amn2/phase-8-rc-operator-run-checklist-2026-06-22.md
```

Доказательство:

- operator run checklist prepared;
- private handoff location recorded safely;
- public exposure, Telegram, config delivery and backup boundaries recorded.

## 4. Разрешенный RC scope

Разрешено:

- закрытый private/operator RC;
- Telegram-first продуктовая логика;
- private operator web/admin access only;
- `.conf`-first private handoff;
- Android AmneziaWG как основной мобильный кандидат;
- AMN2 `187949b` как текущая RC runtime/package line;
- backup create+verify как доказанный backup режим;
- docs/operator coordination без live gates.

Не разрешено этим пакетом:

- public launch;
- public web/admin/API;
- live Telegram send;
- bot polling;
- Telegram profile/media mutation;
- production config delivery;
- restore/import;
- provider rebuild;
- production-scale rollout.

## 5. Явные ограничения

```text
public_launch_status=not-approved
public_exposure_status=closed-by-default
telegram_live_send_status=not-performed
telegram_bot_polling_status=not-performed
fresh_android_phone_acceptance_source=P8-C001
fresh_zero_android_acceptance_device=P8-C003_android_projector
config_delivery_primary_artifact=.conf
qr_release_primary=false
full_vpn_uri_release_primary=false
ios_defaultvpn_status=experimental_unreliable
restore_import_status=not-proven
secret_payload_output_status=not-performed
```

Главное ограничение по Android:

- P8-C001 доказал Android phone acceptance.
- P8-C003 fresh-zero acceptance использовал Android projector.
- Нельзя выдавать P8-C003 за fresh-zero Android phone test.

## 6. Private handoff artifacts

Private handoff root:

```text
C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
```

P8-C003 private handoff run:

```text
C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF\p8-c003-20260622T051333Z
```

Правило:

```text
private handoff artifacts stay outside AMN3 workspace/evidence repo
```

Нельзя переносить в AMN3:

- `.conf`;
- QR;
- `vpn://`;
- private key;
- PSK;
- token;
- password;
- screenshots с payload.

## 7. Stop-lines

Без нового exact named gate нельзя:

- live VPS/SSH command;
- destructive VPS/provider action;
- package upload/apply;
- service restart;
- public exposure;
- firewall/listener changes;
- Cloudflare/ngrok/reverse proxy/TLS publication;
- Telegram live send;
- bot polling;
- Telegram profile/media mutation;
- config delivery;
- config payload output;
- backup restore/import/reboot;
- production peer/user mutation;
- provider rebuild;
- broader rollout.

## 8. Future exact gates

| Если нужно | Открыть gate |
| --- | --- |
| Публичный web/admin/API | `PUBLIC-EXPOSURE-GATE` |
| Telegram live send или bot polling | `TELEGRAM-LIVE-DELIVERY-GATE` |
| Новый config для пользователя/устройства | `CONFIG-DELIVERY-GATE` |
| Restore/import/reboot | `RESTORE-IMPORT-DR-GATE` |
| Production rollout | `PRODUCTION-ROLLOUT-GATE` |
| Provider rebuild | `PROVIDER-REBUILD-GATE` |
| Firewall/listener/TLS/reverse proxy | `PUBLIC-EXPOSURE-GATE` |

## 9. Минимальный старт для следующего оператора

```text
AMN2 Phase 8 is closed for private/operator RC:
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved

Read first:
docs/AMN2_PRIVATE_OPERATOR_RC_FINAL_PACKAGE.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_RUN_CHECKLIST.ru.md
research/amn2/phase-8-sfinal-launch-readiness-freeze-2026-06-22.md

Default mode:
docs/operator coordination only.

Do not open live/destructive/config/Telegram/public actions without a fresh
exact named gate.
```

## 10. Следующее рекомендуемое задание

```text
P8-RC-CLOSEOUT

Use existing Phase 8 evidence only.
Do not open live/destructive/config/Telegram send/public exposure gates.
Prepare a final closeout note:
- final private/operator RC status;
- pushed heads;
- package index;
- next-chat starting point;
- no remaining blockers inside listed limitations.
```
