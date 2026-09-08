# Phase 16: имя при импорте и подготовленные работы

Дата: 2026-09-08. Статус: SOURCE_RESEARCH_COMPLETE_IMPLEMENTATION_NOT_STARTED.
Основание: запрос оператора подготовить полезные работы в ожидании #3043 и найти
автоматическое именование для AmneziaVPN, AmneziaWG и DefaultVPN.
Baseline: 8391412315d4dadff2c47d2fb5a287c0b523e1d0. Только локальное чтение и
официальные публичные источники; реальные профили, raw logs и production не читались.
Это результат исследования и предложения scope, не второй execution plan.
[Текущий план](../../docs/superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md).

## Целевое отображение

По новому образцу оператора: `Neobyatnaya.NET`, с точкой, без номера устройства.
[Прежняя политика](../../docs/AMN2_PHASE_9_CLIENT_DISPLAY_NAME_POLICY_REFRESH.ru.md)
задавала `NeobyatnayaNET` без точки. Это точное расхождение требований, а не
доказательство выполненного изменения генератора. Историческая запись сохранена.
Имя подключения, внутренний device/peer ID и имя хранимого артефакта различаются.
Подпись протокола под именем определяется клиентом; её не следует подделывать.

## Матрица приложений

| Приложение | Путь к автоматическому имени | Что подтверждено и что ещё нет |
| --- | --- | --- |
| AmneziaVPN | Поле `description` верхнего уровня Amnezia JSON со значением `Neobyatnaya.NET`; JSON упаковывается штатным форматом `vpn://` | Stable 5.0.1.5: JSON сохраняется при импорте, модель получает имя из description. Raw WG/AWG .conf получает очередное Server N; переименование .conf не решает этот путь. Фактический импорт нового артефакта не выполнялся |
| AmneziaWG Android | Файл `Neobyatnaya.NET.conf`; импорт использует basename без .conf | Проверен официальный master. Имя из 15 символов проходит правило 1–15 ASCII-символов с разрешённой точкой. Это проверка исходника, не установленной версии |
| AmneziaWG iOS/macOS | Файл `Neobyatnaya.NET.conf`; basename передаётся парсеру как имя | Проверен официальный master; фактический импорт не выполнялся |
| AmneziaWG Windows | Файл `Neobyatnaya.NET.conf`; basename передаётся FromWgQuickWithUnknownEncoding | Проверен официальный master и pinned dependency v3.1.20260814: точка разрешена, длина до 32. Фактический импорт не выполнялся |
| DefaultVPN iOS | Кандидат: тот же Amnezia JSON / vpn:// с description | Официальный dev сохраняет description, UI/model использует его; raw .conf получает очередное имя. Соответствие опубликованного dev установленной App Store-сборке не установлено, нужен отдельный import acceptance |

Фрагмент метаданных, НЕ готовый конфиг:

```json
{"description":"Neobyatnaya.NET"}
```

Это поле Amnezia JSON, не директива [Interface]. Добавление `Name = ...`,
`description = ...` или комментария в raw .conf не является найденным решением
для AmneziaVPN/DefaultVPN. Смена расширения .conf на .vpn не преобразует формат.
Штатная сериализация Amnezia использует qCompress и URL-safe Base64 с vpn://;
полный protocol/container payload должен соответствовать целевому клиенту.

Для AmneziaWG file import выбран как подтверждённый путь именования. Raw QR
не несёт имени файла; автоматическое имя из такого QR здесь не подтверждено.
Для AmneziaVPN QR должен нести родной формат; для DefaultVPN поддержка конкретного
QR-flow не подтверждена. Не обещать универсальный QR для всех трёх приложений.
Совпадение имён при повторном импорте требует отдельного решения без автоматической
перезаписи существующего туннеля. Один peer не использовать одновременно в клиентах.

## Существенная граница совместимости

В DefaultVPN dev `processAmneziaConfig` присваивает импортированному WG/AWG
значение MTU по умолчанию (строки 749–770). Это наблюдение об исходнике, не
подтверждённый дефект установленного приложения. Упаковка имени не доказывает
сохранение MTU 1280 или остальных AWG 3.1-полей; изменение пути импорта требует
проверки всех параметров, а не только красивого заголовка.

Локальный [minimal pilot](../../scripts/vps/phase16_awg31_minimal_pilot.py)
создаёт server.conf/windows.conf и не формирует description/vpn://. Его имена
участвуют в проверках и bindings; переименовывать retained pilot/package нельзя.
Производственный экспорт AMN2 в этом scope не обследован. Поэтому причина имени
в конкретном уже выданном конфиге не установлена без проверки разрешённых metadata.

## Что можно сделать пока ждём #3043

1. **Первым — ограниченный naming/export scope.** Уточнить точный mutable export
   entrypoint в разрешённом репозитории, отделить внутренние имена от display name.
   Для AmneziaVPN/DefaultVPN подготовить клиентский Amnezia envelope; для AmneziaWG
   задать download basename. Один набор offline fixtures проверяет точное имя,
   отсутствие добавленных server-admin credentials, неизменность protocol fields,
   отказ на неподдерживаемых полях и collision policy. Реальные ключи, профили,
   Telegram, production, package016 и выдача исключены. До соответствующего
   разрешения на AMN2 не переходить в соседний production-репозиторий.
2. **Независимо — локальная совместимость recovery parser.** По завершённому
   [R1](phase16-recovery-helper-compatibility-review-2026-09-08.md) создать новую
   локальную версию validator/parser для rollback_failed/recovery_required и
   допустимых milestones; неизвестные/противоречивые combinations отвергать.
   Один offline TDD-набор. Старый driver/collector/receipts сохранить. Это не
   runner, ownership/quiescence proof или разрешение recovery/live inventory.
3. **Позднее — import acceptance без подключения**, в отдельно разрешённой
   клиентской среде: точное имя, round-trip metadata, сохранение параметров и
   повторный импорт. Для DefaultVPN сначала установить версию/связь со source.
   Это не просьба повторить отложенные iPhone/две сети/A/B и не Windows traffic test.

Эти scopes подготовлены, код и реальные конфиги не изменены. DNS bridge STOP;
quality/A/B и iPhone/две сети отложены; integration/acceptance/closeout не закрыты.
Сохраняем завершённые stage-защиты, R1 и документационную оптимизацию без повтора.

## Обращение разработчикам

Найден открытый [issue #1834: Profile name on import](https://github.com/amnezia-vpn/amnezia-client/issues/1834).
В [комментарии](https://github.com/amnezia-vpn/amnezia-client/issues/1834#issuecomment-3302413406)
предложен Amnezia JSON/vpn://. Автор имеет author_association=NONE, поэтому это
не выдаётся за ответ maintainer; вывод выше подтверждён чтением исходников.
Новый тикет не создан: существует точный дубль и найден штатный путь.
Если корректный envelope теряет description в конкретной release-сборке,
следующий шаг — воспроизводимое дополнение к #1834 с версией и безопасной fixture.
Вопрос MTU/DefaultVPN требует отдельного воспроизведения до bug report.
#3043 относится к Windows traffic; его не смешиваем с именованием и не дублируем.

## Официальные источники и версии

- [AmneziaVPN stable 5.0.1.5 import](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/core/controllers/selfhosted/importController.cpp): 164–175, 207, 379–389, 616–619.
- [AmneziaVPN native model](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/core/models/selfhosted/nativeServerConfig.cpp): 84–110; selfHostedUserServerConfig использует такое же поле.
- [AmneziaVPN export](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/core/controllers/selfhosted/exportController.cpp): qCompress, generateVpnUrl.
- [DefaultVPN import](https://github.com/amnezia-vpn/DefaultVPN/blob/3cee753b9fb3658ddebdc0982036979e08c7d8ba/client/ui/controllers/importController.cpp): 154–198, 314–324, 531–533, 749–770.
- [DefaultVPN model](https://github.com/amnezia-vpn/DefaultVPN/blob/3cee753b9fb3658ddebdc0982036979e08c7d8ba/client/ui/models/servers_model.cpp): description и отображение.
- [AmneziaWG Android importer](https://github.com/amnezia-vpn/amneziawg-android/blob/5c16489e2cd9ed3a0a7a27c7445bba5238132f86/ui/src/main/java/org/amnezia/awg/util/TunnelImporter.kt); [правило имени](https://github.com/amnezia-vpn/amneziawg-android/blob/5c16489e2cd9ed3a0a7a27c7445bba5238132f86/tunnel/src/main/java/org/amnezia/awg/backend/Tunnel.java).
- [AmneziaWG Apple importer](https://github.com/amnezia-vpn/amneziawg-apple/blob/9d5ee60edefa95b933a738dd7cda671dd18021fc/Sources/WireGuardApp/UI/TunnelImporter.swift).
- [AmneziaWG Windows importer](https://github.com/amnezia-vpn/amneziawg-windows-client/blob/800416d673d83ed90ede02ca2ccd3683fe107d12/ui/tunnelspage.go): 354–387; [правило имени dependency](https://github.com/amnezia-vpn/amneziawg-windows/blob/v3.1.20260814/conf/name.go).
- [Официальные форматы](https://docs.amnezia.org/documentation/supported-configuration-formats/), [передача доступа](https://docs.amnezia.org/documentation/instructions/share-connection/), [альтернативные клиенты](https://docs.amnezia.org/documentation/alternative-clients/), [DefaultVPN](https://dfvpn.com/).

Охват: относящиеся к вопросу официальные docs, stable AmneziaVPN, опубликованные
исходники трёх клиентов и поиск issues. Это не утверждение о прочтении всех
репозиториев организации, всех веток или проверке бинарных сборок.
AWG2_UNTOUCHED; package016 immutable; SSH/stage/install/push/issuance не выполнялись.
