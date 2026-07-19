# AMN2: чистое развёртывание на Spain VPS и admin-only выдача новых конфигураций

Дата: 2026-07-19
Статус: design approved by operator
Scope: post-release controlled operations

## 1. Решение

AMN2 разворачивается на отдельном Spain/Madrid VPS как новая чистая production-инсталляция. Существующие пользователи, устройства, peers и VPN-конфигурации с USA VPS не мигрируются. Все VPN-конфигурации на Spain создаются заново по явным заявкам оператора.

Первый production-контур выдачи является только административным: новые конфигурации получает единственный настроенный Telegram-администратор, после чего передаёт их получателям самостоятельно. Пользовательская self-service выдача, публичные ссылки и public config API не входят в этот scope.

На Spain VPS уже работает посторонний сервис. Он является жёсткой инвариантой и не должен изменяться, останавливаться или перезапускаться действиями AMN2.

## 2. Цели

- установить AMN2 и AmneziaWG на Spain VPS без воздействия на посторонний сервис;
- начать с чистой базы AMN2 и нулевого набора VPN-пользователей, устройств и peers;
- выпускать только новые, отдельно учитываемые конфигурации;
- связывать каждую конфигурацию с пользователем, физическим устройством, Spain server record и VPN peer;
- использовать фирменное имя `NEOBYATNAYA.NET` во всех новых профилях и файлах;
- выдавать secret-bearing конфигурации только настроенному Telegram-администратору;
- поддерживать последующую блокировку пользователя, отдельного устройства или конкретного peer;
- проверять фактическое применение disable/revoke в AWG runtime;
- оставить USA VPS как нетронутый rollback-контур до принятия Spain deployment;
- не выполнять удаление или деинсталляцию AMN2 с USA VPS: дальнейшую полную переустановку USA оператор выполнит самостоятельно.

## 3. Не входит в scope

- перенос или сохранение работоспособности старых USA-конфигураций;
- перенос старых users/devices/peers в новую Spain DB;
- сохранение старого USA IP в новых конфигурациях;
- публичная панель, public API или публичные config links;
- самостоятельная выдача конфигураций конечным пользователям через Telegram;
- массовая рассылка конфигураций без отдельного operator manifest;
- изменение постороннего сервиса на Spain VPS;
- удаление AMN2 или подготовка другого проекта на USA VPS;
- broad multi-VPS fleet automation.

## 4. Повторно используемый фундамент AMN2

Дизайн не создаёт заново уже существующие возможности:

- модель `user -> device -> server -> peer`;
- `config_version` и состояния `active`, `disabled`, `revoked`;
- блокировка пользователя и отдельных устройств;
- ownership-проверки Telegram;
- существующие resend/revoke/reset flows;
- централизованный `build_device_config_delivery()`;
- зашифрованное хранение peer private key и PSK;
- audit metadata без raw config и ключей;
- существующие apply/revoke adapters и runtime verification;
- Device Passport и read-only operator UX;
- operation planning, exact approval, rollback и postflight patterns.

Перед реализацией допускается только gap audit текущего AMN2 head. Новая функциональность добавляется лишь для реально отсутствующего Spain deployment или bounded admin batch orchestration.

## 5. Целевая архитектура

### 5.1 Spain runtime

Spain VPS получает отдельные:

- AMN2 source/runtime directory;
- Python virtual environment и dependency lock;
- SQLite database;
- encryption key для новой базы;
- loopback-only web service;
- persistent Telegram bot unit;
- отдельный AmneziaWG container/interface;
- systemd units, environment files и rollback state;
- pinned SSH host-key identity.

Имена контейнера, интерфейса, systemd units, каталогов, Docker network, listen ports и VPN subnet выбираются только после read-only conflict preflight.

### 5.2 Посторонний сервис

До установки фиксируется безопасный fingerprint постороннего сервиса:

- containers/images/networks/volumes без secret values;
- systemd unit state;
- listening TCP/UDP ports;
- firewall/NAT rule fingerprints;
- process/restart counters, где доступны;
- HTTP/health evidence, если у сервиса уже существует безопасная health surface.

Тот же fingerprint проверяется после каждого live этапа. AMN2 installer не получает права на произвольное удаление контейнеров, сетей, volumes, systemd units или firewall rules.

### 5.3 USA boundary

USA VPN и web остаются доступным rollback-контуром до принятия Spain. Никакое удаление не выполняется.

Если используется тот же Telegram bot token, одновременно может работать только один polling instance. Cutover выполняется disabled-first:

1. Spain bot установлен, но disabled/stopped.
2. Spain web, DB и AWG проверены независимо.
3. USA bot останавливается отдельным exact live gate без удаления файлов и данных.
4. Spain bot запускается и проходит single-instance/identity/backlog smoke.
5. При неудаче Spain bot останавливается, а USA bot возвращается в прежнее состояние.

### 5.4 SSH onboarding и private target binding

Для Spain повторно используется уже проверенный в проекте key-based SSH pattern,
но trust state другого VPS не наследуется. Одинаковый провайдер, тариф или образ
ОС не доказывает identity нового host.

Private target binding хранится только под игнорируемым каталогом:

```text
private-artifacts/post-release/spain-migration/<run_id>/target.env
```

Файл содержит только:

```text
TARGET_HOST=<private target value>
TARGET_USER=<operator-approved login>
SSH_KEY_PATH=<dedicated Spain private key path>
EXPECTED_HOST_KEY_SHA256=<out-of-band verified fingerprint>
```

Поле для SSH password запрещено. IP/login не публикуются в docs или evidence.

Если первоначально доступен только login/password, оператор один раз вводит
password непосредственно в скрытый интерактивный prompt системного OpenSSH или
использует provider web/VNC console. Через эту сессию устанавливается только
dedicated Spain public key. Password не читается runner-ом, не передаётся Codex,
не сохраняется в shell history, project `.env`, private target binding или Git.

До первого automated SSH command оператор получает host-key fingerprint через
доверенный provider console/out-of-band канал и сверяет его с локально
наблюдаемым fingerprint. `accept-new`, слепой `ssh-keyscan` и known-host entry
другого VPS не являются production trust proof.

После onboarding все runners обязаны использовать:

- абсолютный `%WINDIR%\System32\OpenSSH\ssh.exe`/`scp.exe`;
- `-F none` для изоляции ambient SSH configuration;
- отдельный Spain known-hosts file;
- `BatchMode=yes`;
- `IdentitiesOnly=yes`;
- dedicated Spain private key;
- exact target/login binding;
- fail-closed отказ при host-key mismatch или password prompt.

## 6. Чистая база и данные

Spain DB начинается только с обязательных системных данных:

- единственный настроенный web/Telegram administrator;
- Spain server record;
- policy/audit bootstrap state;
- schema/version metadata.

Пользователи и устройства создаются только из утверждённых operator manifests. Старые USA rows не импортируются.

Для каждой новой конфигурации используются существующие сущности и поля AMN2:

- user identity and status;
- device identity, platform and status;
- Device Passport;
- Spain server assignment;
- peer public identity and allocated VPN address;
- encrypted private key and PSK;
- config version;
- lifecycle timestamps;
- delivery/audit metadata.

Raw `.conf`, QR и `vpn://` не должны попадать в audit, diagnostic output, обычные backups, console output или документы проекта.

## 7. Operator manifest и naming

Минимальная заявка содержит:

- безопасное имя или метку получателя;
- метку физического устройства;
- платформу (`Android`, `Android TV`, `iOS`, `Windows` или согласованное значение);
- количество конфигураций, если для одного человека явно запрошено несколько устройств;
- необязательный срок действия или операторскую заметку без секретов.

Каждое физическое устройство получает отдельный peer и отдельную конфигурацию.

Canonical display label:

```text
NEOBYATNAYA.NET — <user label> — <device label>
```

Безопасное имя файла строится из того же значения с нормализацией недопустимых filesystem-символов. Повторяющиеся labels не должны молча перезаписывать существующий artifact или device record.

## 8. Выдача администратору

Первый production delivery channel — приватный чат текущего Telegram-администратора.

Для каждого конфига бот:

1. проверяет точное соответствие configured admin identity;
2. создаёт или находит user record;
3. создаёт отдельный device/passport record;
4. планирует peer creation;
5. применяет peer к Spain AWG;
6. проверяет observed runtime state;
7. фиксирует local lifecycle/audit state;
8. строит конфигурацию через существующий delivery builder;
9. отправляет один файл только администратору с безопасной подписью;
10. записывает `handed_to_admin` без raw payload или secret hash.

Передача администратором конечному пользователю выполняется вне AMN2. Поэтому `handed_to_admin` не означает `received_by_end_user`. В будущем эти события могут быть разделены дополнительным ручным подтверждением, но это не блокирует первый Spain launch.

## 9. Batch semantics

Если оператор запрашивает несколько конфигураций, manifest сначала проходит полный preflight:

- schema and count bounds;
- duplicate user/device labels;
- platform allowlist;
- server capacity and address availability;
- port/subnet conflicts;
- configured Telegram admin identity;
- delivery builder readiness;
- write gate disabled until exact approval.

После approval каждая конфигурация является отдельной idempotent operation. Batch не скрывает частичный результат:

- успешно созданные записи остаются учтёнными;
- при первой ошибке новые элементы не запускаются;
- failed item получает безопасный failure/audit record;
- оператор видит completed count, failed ordinal и resume point;
- повтор не создаёт duplicate peer или повторную выдачу без явного решения.

Для первого live gate используется один disposable recipient/device, а не production batch.

## 10. Блокировка и отзыв

После выдачи оператор может:

- заблокировать пользователя и все его active devices;
- отключить одно устройство;
- отозвать конкретный peer/config version;
- перевыпустить устройство как новую версию после явного решения.

Файл на устройстве физически отозвать невозможно. Успешный revoke означает, что связанный peer больше не допускается Spain AWG runtime.

Операция считается завершённой только после согласования desired и observed state:

- DB lifecycle state обновлён;
- peer отсутствует или отключён в AWG runtime;
- повторная проверка не обнаруживает активное разрешение;
- audit содержит actor, reason, operation id и безопасный результат;
- raw keys/config payload отсутствуют в output.

## 11. Ошибки и rollback

- Любой preflight failure завершает gate до mutation.
- Любой конфликт с посторонним сервисом блокирует установку.
- Неуспешная установка Spain откатывает только созданные AMN2 resources по allowlist.
- Existing unrelated resources никогда не включаются в cleanup set.
- Неуспешный bot cutover возвращает polling на USA.
- Неуспешная disposable config operation должна удалить или отозвать только disposable peer и очистить transient artifacts.
- Blind DB restore, broad Docker cleanup и firewall reset запрещены.
- AWG другого сервера или постороннего сервиса не изменяется.

## 12. Проверки и acceptance

### Local/scoped verification

- existing create/delivery/disable/revoke tests;
- canonical branding and filename tests;
- admin-only Telegram authorization and cross-user denial;
- no-secret logs, audit, errors and diagnostics;
- duplicate and partial-batch tests;
- idempotency/resume tests;
- unrelated-resource allowlist tests;
- fresh-DB bootstrap and migration tests;
- rollback and single-bot-instance tests.

### Spain read-only preflight

- pinned SSH identity;
- OS/runtime/dependency compatibility;
- ports, routes, Docker networks and VPN subnet conflicts;
- disk/memory capacity;
- unrelated-service before snapshot;
- no mutation and no secret output.

### Disposable live acceptance

- clean AMN2 install;
- loopback-only web health;
- DB integrity and foreign-key checks;
- AWG active with no production peers;
- one disposable user/device/config;
- exact `NEOBYATNAYA.NET` name visible after import;
- admin-only Telegram delivery;
- successful connection and handshake evidence;
- disable/revoke prevents further access;
- mandatory disposable cleanup;
- unrelated-service after snapshot equals before snapshot;
- USA services unchanged except the explicitly approved reversible bot stop during cutover.

## 13. Live gates

Каждый класс live mutation получает отдельную checksum-bound approval:

1. Spain read-only inventory/preflight — no mutation.
2. Spain install with unrelated-service invariants and rollback.
3. Disabled-first bot cutover.
4. One disposable config create/deliver/revoke acceptance.
5. First real operator manifest issuance.

Предыдущие Phase 10/11 approvals не переиспользуются.

## 14. Критерии готовности

Spain считается готовым к выпуску реальных конфигураций только если:

- source/package checksum совпадает с утверждённым AMN2 head;
- postоронний сервис неизменён;
- web доступен только через разрешённый private/loopback contour;
- Telegram bot identity совпадает и существует ровно один polling instance;
- новая DB проходит integrity/FK checks;
- AWG runtime healthy;
- disposable create/deliver/connect/revoke cycle полностью пройден;
- `NEOBYATNAYA.NET` naming подтверждён на реальном клиенте;
- секреты отсутствуют в evidence;
- rollback проверен или остаётся вооружённым до принятия;
- operator явно принимает Spain production contour.

## 15. English contract summary

AMN2 will be deployed as a fresh production installation on the separate Spain/Madrid VPS. No USA users, devices, peers, or VPN configurations will be migrated. The Spain database starts clean and is populated only from explicit operator manifests.

All new configurations use the canonical `NEOBYATNAYA.NET — user — device` label and are delivered only to the single configured Telegram administrator. The administrator distributes files to recipients outside AMN2. Each device has its own peer and remains linked to its user, device passport, server, version, lifecycle state, and audit history so that a user or individual device can later be disabled or revoked.

The unrelated service already running on Spain is immutable for this project. Installation and rollback may touch only allowlisted AMN2 resources. USA is retained as a rollback contour and is not deleted by Codex; only a separately approved reversible bot stop is allowed when the existing Telegram token is cut over to Spain.

Spain reuses the project's proven key-based SSH pattern but never inherits trust from another VPS. The operator may enter an initial password only in a hidden interactive OpenSSH or provider-console session to install a dedicated public key. Automation then uses a separately pinned Spain host fingerprint, isolated known-hosts, the trusted absolute Windows OpenSSH binaries, batch mode, and an exact private target binding that contains no password.

Real issuance is allowed only after a read-only Spain preflight, clean install verification, disabled-first bot cutover, and one disposable end-to-end create/deliver/connect/revoke acceptance cycle.
