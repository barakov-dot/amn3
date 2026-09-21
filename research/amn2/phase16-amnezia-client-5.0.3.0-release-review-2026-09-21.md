# AmneziaVPN 5.0.3.0: официальный выпуск и применимость к Phase16

Статус: RELEASE_VERIFIED / BOUNDED_SOURCE_REVIEW / WINDOWS_TRAFFIC_UNPROVEN.
checked_at: 2026-09-21T13:17:17+03:00 (Europe/Moscow, итоговый source/readback); исходные HTTP-запросы
выполнены в этой сессии, точное время каждого не сохранялось.

Пользователь передал [compare 5.0.1.5...5.0.3.0](https://github.com/amnezia-vpn/amnezia-client/compare/5.0.1.5...5.0.3.0).
[Официальный release API](https://api.github.com/repos/amnezia-vpn/amnezia-client/releases/tags/5.0.3.0):
tag 5.0.3.0, prerelease=false, published_at=2026-09-18T05:59:39Z,
11 assets. Кэшированное web-представление показывало Pre-release; статус принят
по свежему API, не по устаревшей плашке. Последний среди всех релизов не заявляется.

| Платформа | Что подтверждено assets |
| --- | --- |
| Windows | AmneziaVPN_5.0.3.0_windows_x64.exe |
| Linux | AmneziaVPN_5.0.3.0_linux_x64.run |
| macOS | AmneziaVPN_5.0.3.0_macos_x64.pkg |
| Android | 8 APK: Android 11+ / 9–10, каждое arm64-v8a / armeabi-v7a / x86 / x86_64 |
| iOS | В assets нет; App Store rollout/build не проверен, версия UNKNOWN |

Installers/APK не скачивались и не запускались. Release notes также отмечают
TProxy, исправления и ограничения поддержки старых ОС; platform asset не
доказывает совместимость конкретного устройства или Apple universal architecture.

[Официальный compare API](https://api.github.com/repos/amnezia-vpn/amnezia-client/compare/5.0.1.5...5.0.3.0?per_page=100):
base 7d4f3e0f5090b74903609179653d1f669d2ad08a →
head de93650a90739b87bb47a632872ea9d0adc9412f; 30 commits / 224 changed files.
Получен полный список этого диапазона, но подробный audit всех 224 files не
выполнялся. Это не продвижение weekly cursor и не полный upstream review.

## Узкая проверка Windows/импорта

- В conanfile.py на обоих точных SHA Windows pin одинаков:
  awg-windows/3.1.20260814; awg-go и awg-android также 3.1.20260814.
  recipes/awg-windows/conanfile.py отсутствует в списке изменённых файлов.
  [Base source](https://github.com/amnezia-vpn/amnezia-client/blob/7d4f3e0f5090b74903609179653d1f669d2ad08a/conanfile.py),
  [head source](https://github.com/amnezia-vpn/amnezia-client/blob/de93650a90739b87bb47a632872ea9d0adc9412f/conanfile.py).
  Это declared source dependency; фактический бинарный состав asset не проверен.
- awg-apple обновлён до 3.1.4; Xray bindings 1.3.0→1.4.0 и Android libxray
  1.0.2→1.0.3. Нельзя переносить Apple delta на Windows AWG или выводить iOS rollout.
- #3175 (a4d38b564288fcc54ec9ce03596fcc8140dc22fc) исправляет Windows certificate
  signing в release workflow; это не доказательство изменения AWG data path.
- #3115 меняет генерацию параметров новых self-hosted AWG конфигураций:
  S1–S4 получают defaultPadding=12, удалено присваивание CPA, добавлен default I1.
  Прочитаны awgInstaller.cpp и protocolConstants.h patches. Это не разрешение
  менять рабочую Spain config/профиль или причина прежнего Windows FAIL.
- #3184: importController/serverConfigUtils проверяют format_version; отсутствующее
  поле читается как 0 и допускается до currentConfigFormatVersion. Это согласуется
  с уже принятым NO_CHANGE_REQUIRED для AMN2 client-specific экспорта;
  прежние 52 offline tests не повторялись, exporters/legacy delivery не менялись.
- #3046 присутствует в commit inventory как wgshow parsing fix. Его влияние на
  конкретный Windows data path не доказано этой узкой проверкой.
- Наличие #3113 в release и эквивалентность прежнему локальному 5.0.1.5 + PR #3113
  не подтверждены отдельным ancestry/source trace. Нельзя переносить старый
  NAME/MTU PASS на новый binary без отдельной проверки.

## Решение для очереди

Релиз **уже учтён в плане**: Windows P1 получает конкретный официальный candidate
5.0.3.0 и сохранённую source delta. Windows traffic остаётся FAIL; подтверждения
AWG engine fix в просмотренной части нет. Выпуск сам по себе не разрешает повтор
kill-switch/adapter/HTTPS диагностик, установку или A/B. Следующий bounded client
scope требует конкретной новой гипотезы/отличия, критериев и отдельного approval.
Linux/macOS/Android assets учтены, но старые connectivity результаты не превращены
в проверку этих binaries. iPhone/две сети/A/B остаются отложенными.

Raw public JSON и два conanfile.py сохранены в локальном lifecycle scratch;
они не содержат приватных runtime данных. Четыре planning-файла ideas/*,
weekly automation/cursors и client monitor baseline не менялись. Новая карточка
format_version не создана. AWG2_UNTOUCHED, package016 immutable, issuance disabled.

<a id="client-store-recheck-2026-09-21"></a>

## Дополнение: сообщение об обновлении обоих клиентов

Оператор сообщил «обновились амнезиявпн и дефаултвпн». Выполнена ограниченная
проверка official release/store metadata 21.09.2026, 21:03:15–21:03:49
Europe/Moscow. Это не запуск клиентов и не полный upstream review.
Первый HTTP проход в sandbox завершился SSL transport error; повторные
read-only обращения вне sandbox успешны, проверка TLS не отключалась.

| Канал | Подтверждено | Дата выпуска |
| --- | --- | --- |
| [Amnezia GitHub latest API](https://api.github.com/repos/amnezia-vpn/amnezia-client/releases/latest) | 5.0.3.0, prerelease=false; те же 11 binary assets | 18.09.2026 05:59:39 UTC |
| [Amnezia iOS US lookup](https://itunes.apple.com/lookup?id=1600529900&country=us) / [карточка](https://apps.apple.com/us/app/amneziavpn/id1600529900) | 5.0.3, iOS >=16; notes об улучшении стабильности | 21.09.2026 06:02:14 UTC (09:02:14 МСК) |
| [Amnezia iOS RU lookup](https://itunes.apple.com/lookup?id=1600529900&country=ru) | resultCount=0 на момент запроса; не обобщать на другие регионы | — |
| [DefaultVPN RU lookup](https://itunes.apple.com/lookup?id=6744725017&country=ru) / [карточка](https://apps.apple.com/ru/app/defaultvpn/id6744725017) | 2.0.1, iOS >=16; заявлены AWG3.1 и стабильность | 24.08.2026 07:16:45 UTC |
| [DefaultVPN US lookup](https://itunes.apple.com/lookup?id=6744725017&country=us) | те же 2.0.1 и release date | 24.08.2026 07:16:45 UTC |

[DefaultVPN releases API](https://api.github.com/repos/amnezia-vpn/DefaultVPN/releases?per_page=5)
вернул пустой список. [Последние три commits default branch](https://api.github.com/repos/amnezia-vpn/DefaultVPN/commits?per_page=3):
head 3cee753b9fb3658ddebdc0982036979e08c7d8ba от 16.07.2026, прежний pinned source.
Это не полный аудит всех branches/tags/магазинов. Официальный dfvpn.com через
web extraction не дал текста с версией; отсутствие текста не является
доказательством отсутствия обновления. Более новый публичный DefaultVPN build
этими источниками **не подтверждён**; сообщение оператора сохранено как сигнал.
Запрошены фактические версии/ОС на устройствах, ответа на момент записи нет.

Прежний iOS UNKNOWN выше относится к первой проверке в 13:17. Теперь выпуск
AmneziaVPN iOS 5.0.3 в US Store подтверждён, но installed exact build/source
binding неизвестен. Версию магазина 2.0.1 DefaultVPN нельзя автоматически
приравнивать к ранее сообщённой in-app 2.0.1.1 (cb7ea0c); прежний unresolved
source mapping и отложенный manual import check остаются в
[документе поддержки](phase16-defaultvpn-2.0.1.1-compatibility-question-draft-2026-09-20.md).

Решение для Phase16: iOS release **уже учтён в плане** как официальный кандидат,
сообщение о более новом DefaultVPN — **недостаточно данных** до exact версии/ОС.
Release notes не доказывают исправления NAME/MTU/import или Windows traffic.
Вывод по области изменения: эти client releases не требуют изменения Python
locks или пересборки локального bot candidate; native DefaultVPN delivery не
включается. Старые connectivity/quality результаты не переносятся на новые builds.
Установка, ретест устройств, A/B, SSH/Telegram/service actions не выполнялись.
Client monitor baseline, четыре ideas planning-файла, weekly cursor, bot bundle
и package016 не изменены; AWG2_UNTOUCHED, general issuance disabled.

<a id="defaultvpn-202-operator-report"></a>

### Уточнение оператора: DefaultVPN 2.0.2

После проверки выше оператор ответил **«2.0.2»** на вопрос о версии DefaultVPN
после обновления. Это подтверждённое сообщение оператора о версии на устройстве,
не независимая проверка binary/source. Сигнал теперь конкретизирован:
**OPERATOR_REPORTED_VERSION=2.0.2; EXACT_BUILD_SOURCE_BINDING=UNKNOWN**.
Номер внутренней сборки, ОС и канал установки этим ответом не установлены.

Сохранённый снимок RU/US lookup показывал 2.0.1; он не опровергает сообщение
оператора и не устанавливает причину расхождения. Возможную задержку магазина
или другой канал распространения не выдавать за установленный факт. Новый
network lookup не выполнялся. При следующем отдельно разрешённом compatibility
gate учитывать сообщённую 2.0.2, а прежние observations 2.0.1.1/cb7ea0c сохранять
как исторические. Исправление import/NAME/MTU и соответствие публичному source
не доказаны; native delivery, client retest/A/B и live changes не включаются.

<a id="defaultvpn-202-store-confirmed"></a>

### DefaultVPN 2.0.2: официальный выпуск подтверждён

Оператор уточнил, что 2.0.2 видна непосредственно в карточке магазина.
Повторная проверка 21.09.2026 21:20:45 Europe/Moscow с Cache-Control: no-cache,
Pragma: no-cache и уникальным query parameter подтвердила **2.0.2 в RU и US**:

- [Точный RU lookup](https://itunes.apple.com/lookup?id=6744725017&country=ru&entity=software&limit=1&_=1790014844).
- [Точный US lookup](https://itunes.apple.com/lookup?id=6744725017&country=us&entity=software&limit=1&_=1790014844).
- currentVersionReleaseDate: **2026-09-21T17:36:20Z**, то есть **20:36:20 МСК**.
- Release notes: «Improve stability»; minimumOsVersion=16.0.

Текущая классификация: **STORE_RELEASE_VERIFIED / уже учтён в плане**.
Прежние ответы2.0.1 выше были устаревшими снимками и больше не описывают
актуальный выпуск. Web extraction карточки в этой же перепроверке показал
ещё более старую2.0.0; для current version принят свежий официальный API.
Точный слой кэширования не диагностирован. Ранее высказанное сомнение в наличии
обновления снято; сообщение оператора оказалось верным.

Привязка binary к public source и исправления NAME/MTU/import остаются отдельными
непроверенными вопросами: краткие notes не раскрывают конкретные fixes.
Для будущей compatibility-проверки учитывать DefaultVPN2.0.2 и AmneziaVPN iOS5.0.3;
автоматический ретест, включение native delivery, rebuild bot candidate,
изменения AWG2/package016/сервера этим выпуском не требуются и не выполнялись.
