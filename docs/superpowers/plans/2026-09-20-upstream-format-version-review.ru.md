# План проверки format_version и подготовки доработки

**Цель:** определить, нужна ли правка существующего AMN2 client-specific экспорта,
и передать исполнителю конкретный scope с проверками. Документационная подготовка
выполняется сейчас; изменение экспортера и новый импорт/restore этим планом не начаты.
**Архитектура:** сначала совместимость существующего Amnezia envelope; собственный
формат AMN2 — отдельное необязательное решение. Не создавать новый parser ради
зеркалирования поведения чужого клиента.
**Технологии:** Python, JSON, qCompress/zlib, URL-safe Base64; pytest с синтетическими fixtures.
**Основание:** [реестр upstream](../../UPSTREAM_INTAKE.ru.md),
[существующая реализация](../../../research/amn2/phase16-client-import-naming-research-2026-09-08.md),
[официальный commit](https://github.com/amnezia-vpn/amnezia-client/commit/aca1b7dc5cad014a5f22f218655195fd8381cbad).
Для последующей реализации выбранного scope использовать последовательное исполнение
плана; данный файл не требует субагентов и не разрешает Git commit/push или rollout.

## Проверенный baseline

- AMN3 на момент подготовки: `85a0dbf3804531c3a857c56bedb668c24b49b558`.
  P3-карточка уже внесена рабочей задачей в этом commit; повторно не добавлять.
- AMN2 source, точечно прочитанный для локальной сверки:
  `C:/Users/SooL/Documents/amn2-phase15-local-package-bootstrap-readiness`,
  HEAD `56540e2084140e3a6277d7472c88c599d7153ccf`.
  Путь — наблюдение на 20.09.2026, не постоянная привязка; перед code work
  проверить checkout/HEAD/diff и действующий scope.
- `app/vpn/client_import_artifacts.py`: `_native_document` уже формирует JSON
  для AmneziaVPN/DefaultVPN; `build_client_import_artifact` упаковывает `vpn://`.
  Top-level `format_version` не записывается. Это наблюдение, не доказанный дефект.
- `app/vpn/config_templates.py`: `build_vpn_import_link(config_text, *, target_client=None)`
  сохраняет старый путь; явный target выбирает client-specific экспорт.
- Upstream в указанном commit принимает отсутствующую версию как `0`, поддерживает
  версии до `1`. Поэтому существующий экспорт не доказан несовместимым по этому полю.
  Это не строгая проверка типов и не гарантия всех будущих версий клиента.
- Полноценные JSON-import/restore AMN2 в этой узкой сверке не обследованы.
  Нельзя писать «у нас нет import/restore вообще» или обещать весь функционал.

## Очередь и разрешённый scope

| Шаг | Приоритет / состояние | Результат и граница |
| --- | --- | --- |
| 1. Факты и навигация | P1 / выполнено в текущем docs-only пакете | Проверены SHA, exporter, тестовые имена, legacy-семантика upstream; связаны правила и карточка |
| 2. Матрица совместимости | P3 / выполнено 2026-09-20, NO_CHANGE_REQUIRED | Вывод «изменение не нужно» либо ограниченный контракт исправления; без реальных конфигов и UI/connect |
| 3. Локальная правка при доказанной необходимости | P3 / условно, после шага 2 и scope на AMN2 | Минимальный exporter change плюс RED/GREEN; не новый универсальный importer |
| 4. Собственный формат AMN2 | P3 / отложено, отдельная потребность | Отдельная спецификация только если нужен свой import/restore |
| 5. Применение к выдаче | вне текущего scope | Client acceptance и существующие gates; не следует из успешных offline tests |

## Шаг 2: проверить существующий экспорт

- [x] Прочитать четыре конкретных файла выбранного AMN2 checkout:
  `app/vpn/client_import_artifacts.py`, `app/vpn/config_templates.py`,
  `tests/vpn/test_client_import_artifacts.py`, `docs/CLIENT_IMPORT_NAMING.md`.
  Дополнительно `tests/vpn/test_config_templates.py` и `tests/bot/test_delivery.py`
  нужны для legacy/delivery regression, а не для вывода о установленном клиенте.
- [x] Составить матрицу source-контрактов: AmneziaVPN stable 5.0.1.5;
  pinned commit #3184; DefaultVPN — отдельно по exact source/build.
  Не переносить вывод из AmneziaVPN на DefaultVPN или AmneziaWG.
- [x] Для каждого указать: missing version, `0`, `1`, будущая версия;
  где поле прочитано, как тип обрабатывается, затрагиваются ли import/export/restore.
  Проверить malformed значения отдельно: строка, boolean, null, дробь, отрицательное.
  Ничего не выдавать за свойство upstream без точного source evidence.
- [x] Проверить только синтетические artifacts: неизменность raw config/CRLF,
  имени, DNS/MTU/AWG-полей; текущий `.conf` и legacy `vpn://` не должны меняться.
- [x] Записать решение в этот план. Если missing=0 сохраняет совместимость и
  практической пользы новой версии нет, закрыть как «изменение не требуется».
  Не реализовывать собственный envelope ради закрытия карточки.

## Шаг 3: порядок минимальной реализации при подтверждённой потребности

Потенциально затронутые файлы — только перечисленные exporter/config_templates,
их тесты и `docs/CLIENT_IMPORT_NAMING.md` в разрешённом AMN2 source checkout.
Подробный code plan составляется по выбранному контракту шага 2; сейчас нельзя
зафиксировать правильное значение нового поля без матрицы целевых клиентов.

1. Сначала добавить воспроизводящий несовместимость тест к
   `tests/vpn/test_client_import_artifacts.py`. Он должен падать на текущем коде
   именно по принятому контракту, а не из-за окружения/отсутствующей зависимости.
2. Изменить только сборку документа выбранного клиента. Не добавлять field в
   `[Interface]` raw `.conf`, не переключать delivery handlers и legacy defaults.
3. Проверить новый case и существующие тесты:

   ```text
   python -m pytest tests/vpn/test_client_import_artifacts.py tests/vpn/test_config_templates.py tests/bot/test_delivery.py -q
   ```

   Команду запускать в AMN2 с его проверенным Python 3.12 окружением. Это будущая
   проверка; в текущем docs-only пакете suite не запускался.
4. Readback diff: отсутствие новых логов с payload, неизменность AWG2/legacy bytes,
   точные platform/application/version/build в выводе о совместимости.
5. Записать результат/ограничения в документацию и changelog соответствующего
   репозитория, обновить эту карточку ссылкой на evidence. Code PASS не равен
   client import PASS, connectivity/quality PASS или разрешению rollout.

## Шаг 4: только если понадобится собственный import/restore AMN2

До кода определить формат отдельно от версии AWG и upstream `config_version`.
Спецификация должна однозначно задать missing/legacy правила, диапазон версий,
строгую типизацию, лимиты JSON/decompression, unsupported/malformed outcomes,
атомарность либо явную отчётность частичного restore, migration/rollback и
сохранение неподдержанных записей. Нельзя молча выбрасывать их из backup.
Все проверки выполняются до side effects; raw payload и ключи не попадают в логи.
Не копировать GPL-код, схемы, templates или UI; совместимость исследовать по
официальному контракту и реализовывать независимо.

## Что особенно проверить при реализации

- Missing field не превращает legacy-профили в ошибку без принятого migration решения.
- Неверный тип и будущая версия не принимаются по случайному числовому приведению.
- AmneziaVPN и DefaultVPN имеют отдельные доказательства, а `.conf` остаётся raw.
- Имя, MTU, DNS и все AWG-поля сохраняются; envelope version не версия протокола.
- Restore не теряет данные молча; ошибки и repr не раскрывают secret-bearing payload.

## Передача исполнителю (история назначения; результат ниже)

Прочитай AGENTS → START_HERE → docs/UPSTREAM_INTAKE.ru.md → этот план.
P3-карточка уже существует. Исторически назначенный шаг — матрица совместимости
шага 2, когда оператор выберет эту доработку. Если по результату изменения не
нужны, зафиксируй это и закрой проверку. Для доказанного изменения согласуй
конкретный source scope и затем выполни шаг 3. Существующие Phase16 gates,
отложенные клиентские проверки и package016 не возобновляются этим handoff.
## Результат шага 2 — 2026-09-20

**Решение: NO_CHANGE_REQUIRED для format_version текущего exporter.**
Не добавлять 0/1 в существующий envelope, не менять raw .conf/legacy vpn://,
не создавать новый importer/restore. Совместимость по одному полю не означает
полную совместимость клиента, исправление MTU или разрешение выдачи.
Шаг 3 не запускается: доказанной потребности в code change нет.

### Проверенные ревизии и границы

AMN2 HEAD повторно проверен: 56540e2084140e3a6277d7472c88c599d7153ccf,
рабочее дерево чистое до/после; четыре исходных файла и целевые тесты прочитаны.
_native_document не пишет format_version, exact-key-set тест это проверяет.
AmneziaVPN stable здесь означает выбранную baseline 5.0.1.5, не новый обзор latest.
DefaultVPN: source 3cee753b9fb3658ddebdc0982036979e08c7d8ba;
версия установленного iPhone build не получена, соответствие source/build UNKNOWN.
Наблюдённый ранее NAME_PASS через vpn:// не доказывает version matrix на iPhone.

### Матрица format_version

Это source-derived вывод для отдельно взятого version gate при остальном валидном
native документе, не запуск приложений и не утверждение о полном import PASS.
«Игнорируется» означает отсутствие проверки этого поля в изученных путях.

| Значение JSON | AmneziaVPN 5.0.1.5 | AmneziaVPN #3184 | DefaultVPN pinned source |
| --- | --- | --- | --- |
| missing | игнорируется | 0, допускается | игнорируется |
| 0 | игнорируется | допускается | игнорируется |
| 1 | игнорируется | допускается | игнорируется |
| 2 (будущая версия) | игнорируется | отклоняется | игнорируется |
| строка "2" / "bad" | игнорируется | toInt default 0, допускается | игнорируется |
| true / false | игнорируется | default 0, допускается | игнорируется |
| null | игнорируется | default 0, допускается | игнорируется |
| 1.5 | игнорируется | default 0, допускается | игнорируется |
| -1 | игнорируется | -1 <= 1, допускается | игнорируется |

Число 2.0 — целое, отклоняется как 2; не смешивать его с дробным 1.5.
Матрица не распространяется на malformed JSON целиком; это типы одного поля.
Для #3184 проверены currentConfigFormatVersion=1 и QJsonValue::toInt(0) с
сравнением <=1. По документации Qt неверный тип/нецелое число возвращает default;
строгих type/lower-bound checks здесь нет. Native runtime matrix не запускалась.

### Где действует поле

- 5.0.1.5: selfhosted import/export, serverConfigUtils, secureServersRepository
  и secureQSettings не содержат format_version/FormatVersion gate.
- #3184: importController проверяет native import, QR и importConfig;
  API purchase/subscription apply проверяют перед применением. Model toJson
  (native/selfhosted admin/user/APIv2) записывает 1, поэтому export сериализует 1.
  Repository пропускает unsupported записи при загрузке и отклоняет add;
  UI restore сообщает число/факт пропуска. Это partial restore, не атомарный отказ
  всего backup; не обещать сохранность skipped записей при последующих записях.
- DefaultVPN: отдельно прочитаны ui/controllers/importController.cpp,
  exportController.cpp, ui/models/servers_model.cpp и secure_qsettings.cpp;
  version gate отсутствует, native export использует JSON/qCompress,
  restore не имеет добавленной в #3184 version-specific skip/report logic.
- Эти выводы не меняют известные отдельные MTU ограничения клиентов.

### Проверки существующего экспорта

В AMN2 выполнен один целевой прогон с синтетическими данными:
`python -m pytest tests/vpn/test_client_import_artifacts.py tests/vpn/test_config_templates.py tests/bot/test_delivery.py -q --tb=short -p no:cacheprovider`
Результат: **52 passed in 1.69s**. Python bundled runtime, PYTHONPATH указывает
на существующий .codex_deps; PYTHONDONTWRITEBYTECODE=1. Source/tests не изменялись.
Покрыты native roundtrip обоих targets, exact top-level fields без format_version,
имя, DNS/MTU, AWG3/3.1 поля, исходный raw config, CRLF, byte-compatible legacy link,
standalone .conf и delivery regression. Тесты не имитируют запуск Qt-клиента.

### Источники

- [Stable import](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/client/core/controllers/selfhosted/importController.cpp),
  соседний exportController.cpp, client/core/repositories/secureServersRepository.cpp,
  client/core/utils/serverConfigUtils.cpp и client/secureQSettings.cpp того же SHA.
- [Новый version gate](https://github.com/amnezia-vpn/amnezia-client/blob/aca1b7dc5cad014a5f22f218655195fd8381cbad/client/core/utils/serverConfigUtils.cpp),
  [diff всех затронутых путей](https://github.com/amnezia-vpn/amnezia-client/pull/3184/files).
- [DefaultVPN import](https://github.com/amnezia-vpn/DefaultVPN/blob/3cee753b9fb3658ddebdc0982036979e08c7d8ba/client/ui/controllers/importController.cpp),
  [export](https://github.com/amnezia-vpn/DefaultVPN/blob/3cee753b9fb3658ddebdc0982036979e08c7d8ba/client/ui/controllers/exportController.cpp),
  [settings](https://github.com/amnezia-vpn/DefaultVPN/blob/3cee753b9fb3658ddebdc0982036979e08c7d8ba/client/secure_qsettings.cpp).
- [Qt QJsonValue::toInt](https://doc.qt.io/qt-6/qjsonvalue.html#toInt).

### Закрытие и повторное открытие

Шаг 2 закрыт в source/offline scope. Доработка AMN2 по этому сигналу сейчас
не нужна. Возвращаться при отказе клиента от missing/0, опубликованном контракте,
требующем 1, либо подтверждённом дефекте exact target build. Тогда отдельный scope:
изменить только target-specific envelope и regression tests, после согласования
версии для каждого клиента. Собственный формат/import/restore остаётся отдельной
необязательной задачей. GPL source/schema/UI не копировались.

Изменены только документы AMN3; предыдущий незакоммиченный пакет сохранён.
Commit/push не выполнялись. Phase16, AWG2, package016, выдача, stage/install
и незавершённая DefaultVPN .conf проверка не изменены.
