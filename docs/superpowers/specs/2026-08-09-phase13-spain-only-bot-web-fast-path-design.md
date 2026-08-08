# AMN2 Phase 13: Spain-only fast path для переноса bot/web

## Цель

Завершить Phase 13 работающими web и Telegram-ботом на Spain. После приёмки Spain оператор самостоятельно переустановит USA сервер. Выключение, очистка, переустановка и общий retirement-аудит USA не входят в AMN2.

## Точная граница переноса

В Phase 13 переносится только то, что нужно для запуска того же Telegram-бота и обязательной web-панели на Spain:

- `TELEGRAM_BOT_TOKEN` и `ADMIN_TELEGRAM_IDS` берутся из уже принятого зашифрованного USA runtime evidence, никогда не выводятся и попадают в Spain только через checksum-bound encrypted runtime delta;
- код bot/web, шаблоны и зависимости берутся из exact AMN2 source `910539eaa8051cb1b59131d38b9fa27b9392744d`, а не копируются из изменяемой live-файловой системы USA;
- встроенные изображения bot/web, включая `app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png`, `app/bot/assets/NEOBYATNAYA-AMNZ-LANGUAGE-HEADER.png` и `app/web/static/brand-full.png`, входят в checksum-bound application package из того же exact source;
- Telegram-hosted identity, avatar и chat media сохраняются вместе с тем же bot token и не требуют отдельного копирования или изменения через Telegram API;
- текущая Spain database остаётся authoritative и не заменяется merged USA database.

Не импортируются в live Spain: USA users, plans, orders, devices, sessions, API token hashes, server credentials, VPN configs, peer/key material и canonical audit rows. Уже созданные encrypted USA/merge artifacts сохраняются как историческое evidence, но больше не являются входом live stage.

Опциональное локальное хранилище `data/bot-media-registry.json` и `data/bot-media/**` не используется текущими live bot handlers: оно относится к отдельному CLI staging workflow. Оно не требует нового USA SSH-сбора, если оператор ранее не выполнял ручные `bot-media stage/select` операции. При подтверждённом использовании этих операций потребуется отдельный узкий encrypted media-only collection gate.

## Spain bot/web stage

Перед записью выполняется свежий read-only аудит только Spain. Он обязан подтвердить web на `127.0.0.1:3031`, выключенный bot, отсутствие bot-enabled marker, current database integrity, AWG2 D1-D7 equality и foreign persistent equality.

После успешного аудита checksum-bound пакет может установить exact bot/web application bytes, встроенные media assets и encrypted runtime delta с bot token/admin IDs. Spain database не заменяется. Разрешён только bounded stop/start Spain web, если это требуется для application package. Spain bot остаётся disabled/inactive. При ошибке выполняется rollback к точному состоянию Spain до stage.

## Bot cutover

Cutover является отдельным checksum-bound gate:

1. Проверить Spain bot disabled, process zero и marker absent.
2. Остановить только USA bot service.
3. Доказать USA bot process zero.
4. Создать exact Spain bot-enabled marker и запустить Spain bot.
5. Доказать один работающий Spain bot instance и отсутствие второго экземпляра.
6. При ошибке после остановки USA выполнить fail-closed rollback к ровно одному работоспособному bot instance.

USA server, web, database, AWG и прочие службы не изменяются. Отдельный shutdown или cleanup USA не выполняется.

## Границы безопасности

- AWG3 полностью отложен в Phase 14.
- Spain AWG2, D1-D7, peers, configs, keys, firewall, forward rules и foreign service не изменяются.
- Новые VPN configs/peers не выдаются. Будущий перевыпуск конфигов не блокирует перенос bot/web.
- USA legacy database merge прекращён и не является условием запуска Spain bot/web.
- Raw database, config, token, key, SSH target/user/pin и remote stdout/stderr не выводятся.
- Каждый live gate требует свежие outcome ID, expiry, checksum binding, claim-before-network и отдельную literal approval-фразу.

## Приёмка Phase 13

- Spain web здоров и доступен только на `127.0.0.1:3031`.
- Spain database остаётся исходной authoritative database и проходит integrity/foreign-key проверку.
- Spain runtime содержит тот же bot token и утверждённый набор admin Telegram IDs без раскрытия их значений.
- Bot/web application и встроенные media assets соответствуют exact AMN2 source.
- Spain bot является единственным активным экземпляром и проходит bounded functional smoke.
- Spain D1-D7 AWG2 и foreign equality сохранены.
- USA bot process zero; иных требований к состоянию USA нет.
- Зафиксировано `USA_REINSTALL_READY=true`: AMN2 больше не зависит от USA bot/web/data, а физическую переустановку выполняет оператор.
