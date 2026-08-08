# AMN2 Phase 13: Spain-only fast path для переноса bot/web

## Цель

Завершить Phase 13 работающими web и Telegram-ботом на Spain. После приёмки Spain оператор самостоятельно переустановит USA сервер. Выключение, очистка, переустановка и общий retirement-аудит USA не входят в AMN2.

## Принятое основание данных

- Используются уже полученные checksum-bound зашифрованные USA source backup, Spain target-before backup, deterministic merge preview и encrypted merged database.
- Повторный сбор bot/web/database с USA не выполняется.
- Неизменяемые merge receipts и SHA-256 заменяют live USA readiness audit в Spain stage gate.
- Неоднозначные USA legacy orders остаются только в зашифрованном архиве и не импортируются в Spain.

## Spain web/data stage

Перед записью выполняется свежий read-only аудит только Spain. Он обязан подтвердить соответствие Spain target-before baseline, web на `127.0.0.1:3031`, выключенный bot, отсутствие bot-enabled marker, AWG2 D1-D7 equality и foreign persistent equality.

После успешного аудита checksum-bound пакет может выполнить disabled stage и атомарно применить проверенную merged database. Разрешён только bounded stop/start Spain web. Spain bot остаётся disabled/inactive. При ошибке выполняется rollback к точному target-before состоянию.

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
- Raw database, config, token, key, SSH target/user/pin и remote stdout/stderr не выводятся.
- Каждый live gate требует свежие outcome ID, expiry, checksum binding, claim-before-network и отдельную literal approval-фразу.

## Приёмка Phase 13

- Spain web здоров и доступен только на `127.0.0.1:3031`.
- Spain database integrity и foreign keys проходят проверку; migration ledger присутствует.
- Spain bot является единственным активным экземпляром и проходит bounded functional smoke.
- Spain D1-D7 AWG2 и foreign equality сохранены.
- USA bot process zero; иных требований к состоянию USA нет.
- Зафиксировано `USA_REINSTALL_READY=true`: AMN2 больше не зависит от USA bot/web/data, а физическую переустановку выполняет оператор.
