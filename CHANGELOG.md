# Журнал изменений AMN3 / VPS-OPS-LAB

Ведётся с 2026-09-13. Предыдущие записи ниже восстановлены по указанным receipts
и Git, это не полная история проекта. Даты — даты действий/подтверждений;
записи не означают deployment или новую выдачу. Текущая очередь — в
[плане Phase16](docs/superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md).

## 2026-09-20
- Синхронизирован DefaultVPN: NAME_PASS через vpn:// подтверждён скриншотом
  16.09, .conf и параметры остаются открытыми. В [чеклисте](research/amn2/phase16-client-import-acceptance-checklist-2026-09-09.md)
  подготовлен короткий вечерний сценарий без повторения paste/Windows проверок
  и без изменения рабочего профиля «Испания».
- Старый .conf в Temp отсутствовал; синтетическая fixture восстановлена в
  отдельной папке Downloads из ранее проверенного native ключа, 417 bytes,
  SHA256/readback и параметры проверены. В Git payload/ключи не добавлены.
- Read-only upstream на 20.09 14:40 MSK: #3043 без новых ответов, #3113 открыт
  и не слит. Ссылки/diff документации проверены; code/тесты повторно не запускались.

- Выполнен шаг 2 [format_version review](docs/superpowers/plans/2026-09-20-upstream-format-version-review.ru.md):
  NO_CHANGE_REQUIRED для текущего exporter. Записана матрица missing/0/1/future
  и malformed типов, source/build границы DefaultVPN. Целевые 52 offline tests
  PASS; exporter/legacy/delivery не менялись. Новый importer/restore не создаётся.


- По запросу оператора оформлены [реестр upstream](docs/UPSTREAM_INTAKE.ru.md)
  и [план format_version](docs/superpowers/plans/2026-09-20-upstream-format-version-review.ru.md),
  добавлены переходы из AGENTS/START_HERE и существующей P3-карточки.
  Уточнено: native exporter уже существует, missing version upstream принимает
  как 0; несовместимость не доказана. Первым идёт проверка применимости.
- Исправлены границы выводов weekly: неполные issues/PR/AWG coverage и 161-commit
  диапазон Panel не считаются полностью проверенными; IPv6 DNS не приравнивается
  к двух-IPv4 fix, а pooled SSH не является основанием отклонять event-loop isolation.
- Проверка пакета: адресный readback, локальные ссылки, diff/whitespace;
  runtime/code/tests, Phase16 gates, package016 и общая выдача не изменяются.
  Запись документации выполняется штатным apply_patch с одобренным повышением
  доступа; неисправность sandbox ACL этим не объявляется устранённой.

- В [кандидаты AMN2](ideas/candidates-for-amn2.md) добавлен отдельный P3 design
  candidate по upstream PR #3184: версионирование собственного JSON/envelope,
  отказ до side effects, import/restore tests и redaction. GitHub merge SHA и
  diff проверены. Это planning-only, не реализация или изменение Phase16.
- Проверка: readback и diff/whitespace; существующие профили, форматы, выдача
  и серверы не изменены. DefaultVPN .conf test остаётся незавершённым.

## 2026-09-13

### Правила и документация

- Создан этот журнал, добавлена навигация из START_HERE. В AGENTS.md введено
  обязательное обновление changelog в том же commit для существенных изменений
  кода, настроек, правил, инструкций и результатов проверок. Исключение для
  правок без изменения смысла требует явного обоснования в commit body.
- Проверка: readback, staged diff/whitespace и локальные ссылки. Изменения
  только документационные; автоматический commit/CI gate не установлен.

## 2026-09-12 — ретроспективно

### Проверено: импорт Windows

- AmneziaVPN local 5.0.1.5 + PR #3113: имя Neobyatnaya.NET и metadata MTU1280
  сохраняются; в backup двух профилей совпали 45 ожидаемых полей каждого.
  Повторный импорт создаёт одноимённый дубль.
- AmneziaWG official 3.1.0 x64: имя и MTU1280 сохраняются после полного выхода;
  UI-параметры проверены, одноимённый повторный импорт отклоняется. Пропуск
  PersistentKeepalive=0 объяснён официальным serializer, исправление не требуется.
- DefaultVPN остаётся NOT_RUN на iOS. Windows import PASS не закрывает Windows
  traffic FAIL/quality FAIL и не переключает delivery. AWG2_UNTOUCHED.
- По просьбе оператора в тестовом .wsb включён clipboard и добавлена guest-only
  настройка EN/RU Alt+Shift. Статические проверки PASS; фактическая работа обоих
  механизмов отдельно не подтверждена.
- Evidence: [receipt](research/amn2/phase16-windows-import-acceptance-2026-09-12.md),
  commit `4447dc4`; push в согласованную ветку подтверждён readback SHA в задаче.

## 2026-09-11 — ретроспективно

### Проверено: начальный импорт в Sandbox

- Исправленная сборка AmneziaVPN запущена в offline Sandbox; правильное имя
  сохранилось после полного открытия, отдельный MTU1280 подтверждён в preview.
  Полная проверка backup выполнена позже, см. 2026-09-12.
- Evidence: [build/import receipt](research/amn2/phase16-amneziavpn-pr3113-windows-build-2026-09-09.md),
  commit `78e8815`.

## 2026-09-09 — ретроспективно

### Подготовлено: локальная сборка

- Собрана AmneziaVPN 5.0.1.5 с upstream MTU fix PR #3113. Одна попытка сборки,
  0 циклов исправлений; ZIP CRC и SHA проверены. Build Tools/SDK установлены
  по разрешению, Qt/Conan/Python изолированы по каталогам.
- Подготовлен offline Sandbox launcher. Рабочий VPN не заменён; service installer
  candidate на хосте не запускался. Сам build PASS не означал import/traffic PASS.
- Evidence: [receipt и SHA](research/amn2/phase16-amneziavpn-pr3113-windows-build-2026-09-09.md),
  commits `fe31852`, `5560e5d`.
