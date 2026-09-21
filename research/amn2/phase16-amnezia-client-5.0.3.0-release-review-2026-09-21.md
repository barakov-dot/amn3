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
