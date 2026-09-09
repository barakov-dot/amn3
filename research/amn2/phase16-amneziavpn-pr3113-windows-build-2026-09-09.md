# Windows-сборка MTU fix — 2026-09-09

Статус: BUILD_PASS_PACKAGE_PASS_NOT_LAUNCHED. Оператор разрешил установку
инструментов и сборку: одна попытка и максимум два цикла исправлений.
Выполнена одна попытка configure/build; циклов исправления ошибок — 0.
Это receipt сборки, не новый execution plan, не runtime/import acceptance.

## Изменения среды

- Microsoft Visual Studio Build Tools 2022 17.14.40 (17.14.37628.2), workload
  Microsoft.VisualStudio.Workload.VCTools с recommended-компонентами/Windows SDK.
  Установка через winget, SHA установщика проверен winget. --quiet --wait --norestart.
  vswhere после установки: isComplete=true, isRebootRequired=false.
- MSVC compiler 19.44.35228; SDK 10.0.26100.0.
- Отдельный venv: aqtinstall 3.3.0, Conan 2.28.0, CMake 3.31.10, Ninja 1.13.2.
- Qt 6.10.1 win64_msvc2022_64, qtremoteobjects/qt5compat/qtshadertools;
  установлен aqt из Qt archive, qmake -query QT_VERSION = 6.10.1.
- Qt/venv/Conan cache находятся в отдельной папке ниже. PATH менялся в процессах
  runner, не через setx. Conan global.conf только в отдельном CONAN_HOME,
  tools.build:jobs=2; compile --parallel 2. Глобальные Python/Conan проекты не менялись.
- Свободное место: до установки около 267 ГБ, после сборки около 253 ГБ,
  до создания ZIP. Разница включает систему и кеши; это не точный размер установки.

## Исходники и команды

Source directory:
C:/Users/SooL/AppData/Local/Temp/amnezia-build-ae071415bbbc433f93d5a94249907b8a

Source HEAD: 7d4f3e0f5090b74903609179653d1f669d2ad08a.
Единственный tracked diff — client/core/controllers/selfhosted/importController.cpp,
[патч #3113](amnezia-pr3113-preserve-mtu.patch), upstream head
 a39f1c374ed760f886c62741d5645fd1c39c6630. Apple submodule не загружался;
qtkeychain, SortFilterProxyModel, qtgamepad — pinned submodules исходного HEAD.

Tool/build directory:
C:/Users/SooL/AppData/Local/Temp/amnezia-toolchain-20260909

В этой папке: build-once.cmd, package-local.cmd, tool-versions.txt,
pip-install.log, qt-install.log, build-attempt-1.log, package-local.log.
Логи локальные; в Git не добавлялись.

Конфигурация: Ninja, Release, Qt prefix 6.10.1/msvc2022_64,
CONAN_INSTALL_BUILD_CONFIGURATIONS=Release. Conan получил доступные prebuilts;
OpenSSL 3.6.2 собран локально. Предупреждения Perl о C.UTF-8 и отсутствие optional
Vulkan headers не помешали сборке. Никакие критерии не ослаблялись.

Сборка: 282 Ninja steps, importController.cpp.obj скомпилирован, клиент и служба
скомпонованы; runner exit 0. Повторная компиляция не запускалась.
Локальная упаковка: cmake --install с --component AmneziaVPN и точным --prefix
в папку tool/build directory/bundle; exit 0. Это копирование файлов/Qt deployment,
не системная установка VPN. Правила CMake проверены перед выполнением.
Скопированные post_install.cmd/post_uninstall.cmd НЕ запускались.

## Артефакт и проверка

ZIP:
C:/Users/SooL/AppData/Local/Temp/amnezia-toolchain-20260909/AmneziaVPN-5.0.1.5-pr3113-x64-local-test.zip

Размер: 114097571 bytes.
SHA256: 6cca2e00fc90ad2372748efd04f07d3813715f8e70d5b3efa4759f101b703a03.
ZIP CRC check PASS; SHA клиентского exe в архиве совпал с manifest.
Архив содержит READ-ME-FIRST.ru.txt и SHA256SUMS.json.

| Файл | Размер | SHA256 |
| --- | --- | --- |
| AmneziaVPN.exe | 4527616 | C5B79938FFA20A560A4E84788C860BA68FC189E0B5C7D105A0D1E736D93219F3 |
| AmneziaVPN-service.exe | 472064 | EFBF8B7E4C315B3DBE7432F6402EE8C2E4D639373502D5213EEB572AC2EE1C17 |

PE machine обоих файлов = 8664 (x64). Build и bundle SHA совпадают.
Это локальная сборка, не официальный релиз. Native import, UI startup, подключения,
подписки/API и фактический MTU адаптера этой сборкой не проверялись.

## Граница следующего шага

Нужна отдельная Windows-среда для ручного synthetic import acceptance. Отдельная
папка exe не изолирует application settings, single-instance/IPC и службу от
рабочей AmneziaVPN. Не запускать candidate под рабочим профилем до решения изоляции.
Не заменять Program Files и не запускать post_install ради проверки имени/MTU.
Проверка должна подтвердить description и last_config.mtu=1280 после импорта.

На этом этапе не запускались собранные exe, VPN-service installer или VPN drivers.
Рабочие профили не читались и не правились; AWG2_UNTOUCHED, package016 immutable,
general issuance disabled; Spain stage/install/SSH отсутствуют. Build Tools/SDK
добавлены в систему по разрешению оператора; это не утверждение о полном аудите ОС.
Комментарий upstream остаётся непубликованным (ранее GitHub integration HTTP 403).
