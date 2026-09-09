# AmneziaVPN 5.0.1.5: имя и MTU после синтетического импорта

Дата: 2026-09-09. Приложение: AmneziaVPN на Windows x64; AmneziaWG здесь протокол,
не отдельное приложение. Импорт выполнен оператором вручную.

## Наблюдения

- После импорта .vpn имя на главном экране точно Neobyatnaya.NET: NAME_PASS.
- Предпросмотр: raw config содержит MTU = 1280, отдельное last_config.mtu — 1376.
- После сохранения просмотр параметров продолжает показывать raw MTU = 1280.
- В исходном синтетическом артефакте оба поля были 1280 (проверены при создании).
- Оператор сообщил случайное нажатие подключения. Поэтому весь ручной сеанс
  нельзя обозначать connected=false или строго выполненным без попытки соединения.
  Успешное соединение, handshake и фактический MTU адаптера не подтверждены.
- Конфиг синтетический, endpoint 192.0.2.1; production-профили не исследовались.
  Значения тестовых ключей и screenshots с ними в Git не копируются.

## Прослеженный официальный путь

Все ссылки закреплены на commit 7d4f3e0f5090b74903609179653d1f669d2ad08a.
Это source trace; исполняемый бинарник не пересобирался и не инструментировался.

1. [importController.cpp](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/core/controllers/selfhosted/importController.cpp#L750): processAmneziaConfig безусловно записывает defaultMtu в JSON last_config.mtu.
2. [protocolConstants.h](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/core/utils/constants/protocolConstants.h#L172): AWG defaultMtu на Windows — 1376; Android/iOS/MACOS_NE — 1280.
3. [awgProtocolConfig.cpp](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/core/models/protocols/awgProtocolConfig.cpp#L355): модель читает отдельное mtu; toJson записывает его отдельно от nativeConfig.
4. [configuratorBase.cpp](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/core/configurators/configuratorBase.cpp#L30): обработка локальных настроек заменяет DNS placeholders в nativeConfig, не извлекает из него MTU. AWG наследует WireguardConfigurator, который делегирует этому методу.
5. [connectionController.cpp](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/core/controllers/connectionController.cpp#L281): получает clientConfig JSON и передаёт его как protocol config data; default подставляется лишь при пустом mtu.
6. [localsocketcontroller.cpp](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/mozilla/localsocketcontroller.cpp#L157): activate формирует deviceMTU из отдельного поля mtu.
7. [daemon.cpp](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/daemon/daemon.cpp#L255): читает строку deviceMTU в m_deviceMTU; fallback 1420 только при отсутствии/нуле; Windows clamp только для значений ниже 1280. Значение 1376 сохраняется.
8. [interfaceconfig.cpp](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/daemon/interfaceconfig.cpp#L103): toWgConf пишет MTU из m_deviceMTU.
9. [wireguardutilswindows.cpp](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/platforms/windows/daemon/wireguardutilswindows.cpp#L97): передаёт результат toWgConf в m_tunnel.start; перед запуском удаляет Peer-секцию, не Interface с MTU.

Вывод: в прослеженном пути Windows native import значение 1376 имеет приоритет
над MTU = 1280 в отображаемом raw config. Это не только различие отображения:
именно 1376 формируется для запуска службы. Фактическое применение на адаптере
в случайной попытке оператора не измерено. Причина исторического #3043 не доказана:
в прежнем отдельном Windows run уже наблюдался MTU 1280.

## Последствия для экспорта

Именование в AmneziaVPN подтверждено; сохранность MTU для native envelope — FAIL
на этапе импорта. Ранее выделенное только для DefaultVPN ограничение относится
также к проверенному AmneziaVPN. Старый research следует читать с этим уточнением.
Не включать новый export в delivery как полностью совместимый.

Raw .conf импорт в исходнике сохраняет явно заданный MTU, но даёт Server N:
это возможный компромисс с ручным переименованием, не проверенный обход для выдачи.
Следующая ограниченная работа — подготовить воспроизведение MTU для upstream,
проверить существующие issues перед публикацией. Повтор подключения не нужен.
Другие приложения, AWG3.1 и повторный импорт этим тестом не приняты.

AWG2_UNTOUCHED; package016 immutable; general issuance disabled; stage/install отсутствуют.

## Исправление и upstream — 2026-09-09

Найден уже открытый точечный [PR #3113](https://github.com/amnezia-vpn/amnezia-client/pull/3113),
head a39f1c374ed760f886c62741d5645fd1c39c6630, OPEN / NOT MERGED.
Авторский патч сохраняет непустой MTU; отсутствующий, пустой и whitespace-only
MTU получает прежний default. [PR #3065](https://github.com/amnezia-vpn/amnezia-client/pull/3065)
также содержит guard, дополнительно меняет глобальные defaults. Новый дубль не создан.

[Сохранённый патч #3113](amnezia-pr3113-preserve-mtu.patch) получен через GitHub API;
авторство upstream, не наша новая реализация. SHA256:
DFC0AC37F8B332D59DBAE50328D4C81BB6657B690D7F8B3A33C4A72A72D0C16C.
Применён только к временной копии официального importController.cpp 5.0.1.5:
git apply --check PASS; git apply PASS; guard проверен после применения.
Сборка и native regression tests NOT_RUN: Qt/compiler не найдены в PATH.
Установленный бинарник не изменён; это проверенная применимость патча, не client fix acceptance.

В AMN2 исправлено compatibility_note: теперь явно сообщает о 5.0.1.5 Windows,
замене MTU на 1376 и невозможности исправить клиент сериализацией экспортера.
Целевой RED 1 expected failure; итоговый набор export/config_templates/bot_delivery
52 PASS. Формат, legacy delivery, реальные конфиги и issuance не изменены.

Попытка добавить воспроизведение в #3113 через GitHub connector отклонена HTTP 403
Resource not accessible by integration. Комментарий НЕ опубликован. Это ограничение
прав интеграции GitHub, не auto-review rejection и не отказ разработчиков.
[Текст для публикации](phase16-pr3113-comment-draft-2026-09-09.md).
