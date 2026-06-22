# AMN2 private/operator RC run checklist

Дата: 2026-06-22.

Статус:

```text
checklist_status=prepared-docs-only
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
```

Этот чеклист предназначен для частного/операторского RC. Он не открывает live
VPS, destructive, config delivery, Telegram send или public exposure gates.

## 1. Перед началом работы

Проверить текущий статус:

```text
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
blocked_with_exact_remaining_blockers=false
```

Проверить, что оператор понимает ограничения:

- это частный/операторский RC, не публичный запуск;
- публичный web/admin/API не открыт;
- Telegram live send и bot polling не выполнялись;
- `.conf` является основным приватным handoff-артефактом;
- QR и полный `vpn://` не являются release-primary;
- iOS DefaultVPN остается experimental/unreliable;
- restore/import DR не доказан.

Проверить исходные документы:

```text
docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md
research/amn2/phase-8-sfinal-launch-readiness-freeze-2026-06-22.md
research/amn2/phase-8-p8-c003-fresh-zero-rehearsal-2026-06-22.md
research/amn2/phase-8-p8-c002-187949b-package-apply-smoke-2026-06-21.md
research/amn2/phase-8-p8-c001-fresh-android-config-acceptance-2026-06-21.md
```

## 2. Что можно делать в этом RC

Разрешенный контур:

- вести частный/операторский RC;
- использовать Telegram-first продуктовую логику как основной пользовательский
  канал;
- держать operator web/admin приватным;
- использовать `.conf`-first private handoff;
- считать Android AmneziaWG основным мобильным кандидатом;
- считать AMN2 `187949b` текущей RC runtime/package line;
- опираться на backup create+verify evidence.

Без нового точного gate можно делать только docs/operator coordination:

- читать evidence;
- готовить инструкции;
- сверять ограничения;
- планировать будущие gates;
- оформлять handoff/checklist/status.

## 3. Чего нельзя делать без нового точного gate

Запрещено без отдельного exact named gate:

- live VPS/SSH команды;
- destructive VPS/provider действия;
- package upload/apply;
- service restart;
- public exposure;
- firewall/listener changes;
- Cloudflare, ngrok, reverse proxy, TLS publication;
- Telegram live send;
- bot polling;
- Telegram profile/media mutation;
- config delivery;
- вывод `.conf`, QR, `vpn://`, private key, PSK, token или password;
- backup restore/import/reboot;
- production peer/user mutation;
- provider rebuild;
- broader rollout.

## 4. Где находятся private handoff artifacts

Private handoff directory outside workspace:

```text
C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
```

P8-C003 private run directory:

```text
C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF\p8-c003-20260622T051333Z
```

В этом каталоге могут лежать secret-bearing artifacts. Их нельзя:

- коммитить в AMN3;
- вставлять в чат;
- копировать в evidence;
- пересылать как screenshots;
- публиковать как QR/`vpn://`/raw `.conf`.

Разрешено ссылаться только на безопасные metadata:

- имя файла;
- размер;
- sha256;
- факт private handoff;
- redacted path.

## 5. Как держать public exposure закрытой

Операторский принцип:

```text
public_exposure_status=closed-by-default
```

Не делать:

- не открывать порт `3030` наружу;
- не открывать порт `3040` наружу;
- не включать reverse proxy;
- не добавлять Cloudflare/ngrok;
- не менять firewall/listener;
- не публиковать web/admin URL.

Допустимый операторский доступ:

- loopback;
- SSH tunnel;
- другой явно приватный операторский доступ без public exposure.

Если нужна публичная экспозиция, остановиться и открыть отдельный gate:

```text
PUBLIC-EXPOSURE-GATE
```

## 6. Как работать с Telegram

Текущий доказанный статус:

```text
telegram_first_runtime_status=server-side-getme-and-non-polling-smoke-passed
telegram_live_send_status=not-performed
telegram_bot_polling_status=not-performed
```

Без нового gate нельзя:

- запускать bot polling;
- отправлять live messages;
- мутировать profile/media;
- отправлять config payload;
- отправлять QR/`vpn://`/raw `.conf`.

Если нужно реально включить Telegram live operation, открыть отдельный gate:

```text
TELEGRAM-LIVE-DELIVERY-GATE
```

Минимальные inputs для такого gate:

- что именно запускается;
- кому отправляется;
- как исключается payload output в evidence;
- как остановить отправку;
- что считать pass/fail.

## 7. Как работать с config delivery

Текущая RC policy:

```text
config_delivery_primary_artifact=.conf
config_delivery_channel=private_handoff_only
qr_release_primary=false
full_vpn_uri_release_primary=false
```

Без нового gate нельзя:

- создавать новый production config;
- выдавать config новому пользователю;
- пересылать `.conf`;
- показывать QR;
- выводить `vpn://`;
- печатать private key/PSK.

Если нужен новый config delivery, открыть отдельный gate:

```text
CONFIG-DELIVERY-GATE
```

Минимальные inputs:

- точный пользователь;
- точное устройство;
- private destination outside workspace;
- one-time/revocation policy;
- запрет payload output.

## 8. Как работать с backup/restore

Доказано:

```text
backup_create_status=passed
backup_verify_status=passed
backup_artifact_mode=600
```

Не доказано:

```text
restore_import_status=not-proven
```

Без нового gate нельзя:

- restore apply;
- archive import;
- reboot;
- overwrite production state;
- provider restore.

Если нужен restore/import, открыть отдельный gate:

```text
RESTORE-IMPORT-DR-GATE
```

## 9. Перед каждой операторской сессией

Проверить вручную:

- текущая цель сессии не требует live/destructive/config/Telegram/public gate;
- публичная экспозиция не открывается;
- не планируется вывод secret-bearing payload;
- private handoff artifacts остаются вне workspace;
- если нужно действие шире docs/operator coordination, сначала формулируется
  exact named gate.

Короткая безопасная формулировка:

```text
Работаем в private/operator RC scope. Public exposure closed by default.
Config payloads не выводим. Live Telegram не запускаем. Restore/import не
делаем. Любое расширение только через отдельный exact named gate.
```

## 10. После операторской сессии

Если была только docs/operator coordination:

- обновить status/handoff docs;
- не прикладывать secret-bearing artifacts;
- не переносить private handoff файлы в AMN3;
- зафиксировать, что live gates не открывались.

Если был открыт отдельный gate:

- записать gate name;
- записать target;
- записать pass/fail;
- записать exact blocker если failed;
- записать stop-lines;
- не включать секреты и payload.

## 11. Таблица будущих gates

| Нужное действие | Требуемый gate |
| --- | --- |
| Публичный web/admin/API | `PUBLIC-EXPOSURE-GATE` |
| Telegram live send или bot polling | `TELEGRAM-LIVE-DELIVERY-GATE` |
| Новый config для пользователя/устройства | `CONFIG-DELIVERY-GATE` |
| Restore/import/reboot | `RESTORE-IMPORT-DR-GATE` |
| Production rollout | `PRODUCTION-ROLLOUT-GATE` |
| Provider rebuild | `PROVIDER-REBUILD-GATE` |
| Firewall/listener/TLS/reverse proxy | `PUBLIC-EXPOSURE-GATE` |

## 12. Следующее рекомендуемое задание

```text
P8-RC-FINAL-PACKAGE

Use existing Phase 8 evidence only.
Do not open live/destructive/config/Telegram send/public exposure gates.
Prepare the final private/operator RC package index:
- handoff document;
- run checklist;
- evidence list;
- limitations;
- exact future gates.
```
