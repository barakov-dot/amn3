# Статистика трафика и выбор версии конфига

## Цель

Добавить в проект поддержку двух связанных возможностей:

- сбор и отображение статистики трафика по VPN-устройствам;
- выбор версии AmneziaWG-конфига: `amneziawg_v1_5` или `amneziawg_v2`.

Функциональность должна быть доступна и пользователю в личном кабинете Telegram-бота, и администратору при ручном создании или управлении учетками.

## Текущее состояние

Уже есть:

- поле `devices.config_version`;
- генератор клиентского конфига `amneziawg_v2`;
- модель users/devices/orders/admin_actions;
- зашифрованное хранение peer secrets;
- безопасный `server check` scaffold.

Пока нет:

- генератора `amneziawg_v1_5`;
- явного списка поддерживаемых config versions;
- выбора версии конфига пользователем;
- выбора версии конфига администратором;
- таблиц/stat snapshots для трафика;
- сервиса, который связывает peer public key с traffic counters;
- Telegram UI для просмотра статистики.

## Scope

Включено:

- зафиксировать поддерживаемые версии config format:
  - `amneziawg_v1_5`;
  - `amneziawg_v2`;
- добавить уровень выбора renderer по версии;
- добавить минимальный renderer для `amneziawg_v1_5`;
- расширить workflow создания device так, чтобы caller мог передать нужную версию;
- добавить таблицу snapshots статистики трафика;
- добавить repository/service для записи и чтения последней статистики;
- подготовить DTO/текст для отображения статистики пользователю и администратору;
- добавить fake-friendly интерфейс сбора статистики с сервера;
- покрыть новую логику тестами.

Исключено из этого инкремента:

- реальный SSH сбор статистики с production VPS;
- лимиты трафика и автоотключение по лимиту;
- платежные тарифы, зависящие от трафика;
- полноценный Telegram UI с inline-кнопками, если фундамент БД/сервисов еще не готов;
- миграционная система для production БД.

## Термины

`config_version` - версия формата клиентского VPN-конфига.

`traffic snapshot` - снимок счетчиков трафика peer на определенный момент времени.

`rx_bytes` - входящий трафик для peer.

`tx_bytes` - исходящий трафик для peer.

`total_bytes` - сумма `rx_bytes + tx_bytes`.

## Модель данных

Добавить таблицу `device_traffic_snapshots`:

```sql
CREATE TABLE IF NOT EXISTS device_traffic_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    server_id INTEGER NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    peer_public_key TEXT NOT NULL,
    rx_bytes INTEGER NOT NULL CHECK (rx_bytes >= 0),
    tx_bytes INTEGER NOT NULL CHECK (tx_bytes >= 0),
    source TEXT NOT NULL,
    collected_at TEXT NOT NULL
);
```

Индексы:

```sql
CREATE INDEX IF NOT EXISTS idx_device_traffic_device_collected
    ON device_traffic_snapshots(device_id, collected_at DESC);

CREATE INDEX IF NOT EXISTS idx_device_traffic_server_collected
    ON device_traffic_snapshots(server_id, collected_at DESC);
```

Поле `devices.config_version` уже существует. Нужно закрепить допустимые значения на уровне сервисов:

- `amneziawg_v1_5`;
- `amneziawg_v2`.

Если позже появится миграционная система, допустимые значения можно будет перенести в DB constraint или справочник.

## Генерация конфигов

Добавить общий интерфейс:

```text
render_client_config_for_version(input, config_version) -> str
```

Правила:

- `amneziawg_v2` использует текущий renderer;
- `amneziawg_v1_5` использует отдельный renderer;
- неизвестная версия дает понятную ошибку;
- версия сохраняется в `devices.config_version`;
- повторная выдача конфига должна использовать версию, сохраненную у устройства.

## Пользовательский сценарий

В личном кабинете Telegram-бота пользователь должен видеть:

- список своих устройств;
- версию конфига каждого устройства;
- срок действия;
- входящий трафик;
- исходящий трафик;
- общий трафик;
- время последнего обновления статистики.

При создании новой заявки пользователь выбирает:

1. имя устройства;
2. версию AmneziaWG:
   - AmneziaWG 1.5;
   - AmneziaWG 2.0.

Выбранная версия попадает в order/device workflow.

## Административный сценарий

Администратор при ручном создании доступа выбирает:

1. пользователя;
2. устройство или имя нового устройства;
3. срок доступа;
4. версию конфига:
   - AmneziaWG 1.5;
   - AmneziaWG 2.0.

В админском просмотре нужно показывать:

- пользователь;
- устройство;
- config version;
- status;
- expiration;
- latest traffic stats;
- last stats collection time.

## Сбор статистики

Для этого инкремента нужен интерфейс, не зависящий от реального VPS:

```text
TrafficCollector.collect(server) -> list[PeerTraffic]
```

`PeerTraffic`:

- `peer_public_key`;
- `rx_bytes`;
- `tx_bytes`;
- `collected_at`;
- `source`.

Реальный backend позже может читать `awg show` или другой AmneziaWG-compatible output. В этом инкременте достаточно fake collector для тестов и service, который сопоставляет `peer_public_key` с devices.

## Ошибки и безопасность

- Traffic collection не должен логировать private keys, PSK или full configs.
- Если peer из server output не найден в БД, snapshot не записывается, но событие можно вернуть в report как `unknown_peer`.
- Отрицательные счетчики запрещены.
- Слишком старые snapshots должны отображаться с пометкой, что статистика устарела.
- Ошибка сбора статистики не должна ломать выдачу уже существующих конфигов.

## Тестирование

Нужны тесты:

- supported config versions list;
- unknown config version rejected;
- `amneziawg_v2` path остается совместимым;
- `amneziawg_v1_5` renderer returns valid config shape;
- access service stores selected config version;
- traffic snapshot insert rejects negative counters;
- latest traffic for device returns newest snapshot;
- collector service stores stats only for known peers;
- user/admin display DTO formats bytes safely;
- backup/restore остается зеленым после schema update.

## Acceptance Criteria

- Пользовательский и админский workflow могут передать выбранную версию конфига.
- Устройство хранит выбранную `config_version`.
- Есть два renderer path: `amneziawg_v1_5` и `amneziawg_v2`.
- Есть таблица и repository для traffic snapshots.
- Последняя статистика устройства доступна для отображения в боте.
- Fake collector покрыт тестами.
- Full test suite passes.
- Документация существует на русском и английском.
