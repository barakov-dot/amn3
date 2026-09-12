# Windows import acceptance — 2026-09-12

Scope: синтетические профили в Windows Sandbox, без подключения туннеля.
Это receipt локального импорта, не connectivity/quality acceptance.

## AmneziaVPN local 5.0.1.5 + PR #3113

[Сборка, SHA и история](phase16-amneziavpn-pr3113-windows-build-2026-09-09.md).
Имя Neobyatnaya.NET после полного выхода/открытия подтверждено ранее.
После перезапуска оператор создал штатную резервную копию внутри Sandbox.
Helper прочитал сохранённые данные: metadata MTU=1280; screenshot
904424ec-dfda-45a1-a41e-37eb575483e6.
Повторный импорт создал две одноимённые записи без суффикса: screenshot
005ea568-ff20-4536-bdbe-9914b8fd74fe.
Свежая резервная копия после второго импорта: Profiles found=2;
оба профиля PASS, 45 expected fields match (screenshot
258b3c7c-2071-43a9-b56e-ef9108ad1f8d).

Проверка сравнивает SHA256 значений листьев исходного native envelope с backup:
вложенный last_config декодируется, raw config разбирается по section/field,
порядок строк и крайние пробелы нормализуются. Проверены также ключи без вывода
значений. Отсутствие/изменение ожидаемых полей и лишние raw config fields — FAIL;
добавочные служебные metadata клиента разрешены. Это сравнение 45 ожидаемых
полей fixture, не всех возможных настроек приложения и не AWG3.1 traffic test.
Helper сначала отсутствовал (RED), затем проверки matching input, изменения
metadata MTU/ключа, отсутствующего ключа, duplicate field rejection прошли;
двухпрофильный synthetic backup roundtrip и syntax PASS.
Helpers и эталон остались в локальном temp/sandbox-input; raw backups, конфиги,
ключи и скриншоты в Git не добавлялись.

## AmneziaWG Windows 3.1.0 x64

[Официальный релиз](https://github.com/amnezia-vpn/amneziawg-windows-client/releases/tag/3.1.0),
asset amneziawg-amd64-3.1.0.msi, 3641344 bytes.
SHA256 a1b48ea8699cd347832a3691d832004574ef8ad65bcf887611ac8acb99b7de8b
совпал с GitHub asset digest. Authenticode Valid, Privacy Technologies OU.
Оператор установил MSI только внутри Sandbox. Хостовый MSI не запускался.

- NAME_PASS: импорт Neobyatnaya.NET.conf дал Neobyatnaya.NET.
- UI: MTU1280, адрес, DNS, AllowedIPs и endpoint соответствуют fixture;
  screenshot 0b3dae89-32e9-4a6d-a467-9c65a086eaa7.
- Редактор показывает Jc/Jmin/Jmax, S1/S2, H1-H4, адреса/MTU и key fields;
  screenshot eaa44787-2ec1-43ca-bb42-601f85b3c0ab. Полное автоматическое
  сравнение exported AmneziaWG config не выполнялось: UI/source evidence
  не называть 45-field backup PASS другого приложения.
- Повторный импорт REJECTED: tunnel name already exists; одна запись осталась,
  screenshot 15e6a453-734c-475b-afbd-4d3c6b90b279.
- После полного выхода/открытия имя и MTU1280 подтверждены оператором «да и да».
- PersistentKeepalive=0 отсутствует в редакторе по правилам сериализации ниже;
  дефект не установлен. Статус на скриншотах «Отключен»; туннель не проверялся.

### Нулевой keepalive: source trace

[go.mod релиза](https://github.com/amnezia-vpn/amneziawg-windows-client/blob/3.1.0/go.mod)
фиксирует amneziawg-windows/v3 v3.1.20260814.
[writer.go](https://github.com/amnezia-vpn/amneziawg-windows/blob/v3.1.20260814/conf/writer.go#L164):
ToWgQuick не пишет PersistentKeepalive для пустой строки, 0 или off.
Тот же файл, строки 269–273: ToUAPI преобразует пустое/off в 0 и пишет
persistent_keepalive_interval. [Parser](https://github.com/amnezia-vpn/amneziawg-windows/blob/v3.1.20260814/conf/parser.go#L466)
читает явное значение в peer.PersistentKeepalive.
Таким образом, наблюдаемое отсутствие нулевой строки объяснено исходниками;
изменять exporter или создавать issue по этому наблюдению не требуется.

## DefaultVPN и среда

DefaultVPN NOT_RUN. [Официальная документация](https://docs.amnezia.org/documentation/alternative-clients/)
указывает iOS16+; GitHub releases API 2026-09-12 вернул 0 релизов.
Наличие Windows build paths в исходниках не доказывает опубликованный Windows app.
Следующая отдельная проверка DefaultVPN требует iOS; отложенный iPhone gate
не возобновлять автоматически. Это не перенос результатов Windows на iOS.

По прямой просьбе оператора ClipboardRedirection изменён на Enable в тестовом
.wsb; добавлен guest-only Setup-Keyboard.ps1 (en-US/ru-RU, Alt+Shift).
XML и PowerShell syntax/readback конфигурации PASS; фактическая работа clipboard
и сочетания клавиш оператором отдельно не подтверждена. Networking остаётся Disable,
shared folder read-only. После добавления установщика/helpers folder уже содержит
больше четырёх файлов; исходный список в build receipt исторический.
Настройки клавиатуры хоста не менялись. Sandbox может быть закрыта после сохранения
нужных оператору синтетических материалов; закрытие в этом receipt не подтверждается.

## Следующие границы

Локальный Windows name/MTU gate закрыт в указанных пределах. DefaultVPN/iOS остаётся
NOT_RUN; #3043 по-прежнему отдельная проблема (нового upstream readback в этом run нет).
Не переключать delivery и не повторять Windows traffic/A/B на основании import PASS.
AWG2_UNTOUCHED; package016 immutable; general issuance disabled; Spain stage/install
не выполнялись. Модель не менялась, точные model/effort инструментами не определены.
