# PRVTPRO/Amnezia-Web-Panel: manager architecture

## Паспорт deep-dive

- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
- Дата анализа: 2026-05-30
- Область: SSH abstraction, protocol managers, lifecycle operations, remote execution, destructive operations.
- License verdict: GPL-3.0, режим `research-only`.
- Production verdict для `amn2`: изучать только идеи и требования; код, shell-flow, Dockerfile, конфиги и manager-реализации не переносить.

## Краткий вывод

Manager-слой upstream полезен как карта доменных обязанностей: общий SSH/control layer, отдельные manager-объекты на протокол или сервис, API-dispatch из `app.py`, локальное сохранение обнаруженного состояния. Это хороший reference для постановки вопросов: какие операции нужны, какие состояния надо уметь читать, какие протоколы требуют отдельного lifecycle.

Главный риск - remote execution слишком близко к shell-скриптам. Manager-ы выполняют sudo-команды, собирают Docker/iptables/config операции, меняют firewall, сети, контейнеры, файлы в `/opt/amnezia`, иногда скачивают зависимости на целевом сервере. Для `amn2` переносимая ценность не в конкретных командах, а в production-требованиях: command contract, dry-run, audit, secret redaction, host key policy, idempotency и тестируемый runner.

## Общая модель

У проекта есть центральный FastAPI слой и набор manager-ов:

- `app.py` принимает API-запросы, проверяет роль, достает server record из локального state и выбирает manager по protocol/service.
- `SSHManager` отвечает за подключение, запуск команд, sudo, upload файлов и временных скриптов.
- Protocol/service manager-ы инкапсулируют операции конкретного домена: WireGuard, AmneziaWG, Xray, Telegram MTProxy, DNS, AdGuard Home, SOCKS5.
- Результаты manager-операций затем отражаются в локальном `data.json`: protocol status, generated credentials, user connections, configs, server metadata.

Для лаборатории это удобно: код быстро показывает полный operator-flow. Для production это значит, что security boundary должен проходить не только через API guards, но и через каждую remote operation.

## SSH abstraction

`SSHManager` построен на Paramiko и дает общий набор primitives:

- подключение по password или private key;
- запуск обычной команды;
- запуск sudo-команды;
- upload файла;
- upload временного shell script и запуск его через sudo;
- удаление временного script после выполнения.

Полезная идея: вынести remote execution в один слой, чтобы все protocol manager-ы не реализовывали SSH заново.

Production-риски:

- unknown host keys принимаются автоматически через `AutoAddPolicy`;
- sudo password может попадать в shell command string;
- command logging должен быть строго отделен от secret material;
- временные scripts на удаленной машине требуют predictable cleanup и audit;
- stdout/stderr могут содержать секреты, конфиги или stack traces;
- нет видимого typed contract для команд: expected exit codes, allowed side effects, rollback note, retry policy.

Для `amn2` это должно стать не "SSH helper", а `RemoteOperationRunner` с явным contract:

- host key pinning или отдельный enrollment-flow;
- no secret in command line;
- redacted structured logs;
- dry-run support;
- audit event на каждую state-changing операцию;
- timeout, retry и cancellation policy;
- test double для unit/integration tests.

## Protocol managers

| Manager | Область | Полезный паттерн | Production-риск |
| --- | --- | --- | --- |
| `ssh_manager.py` | SSH, sudo, upload, scripts | единая точка remote execution | auto-trust host keys, password in shell string, secret logging |
| `awg_manager.py` | AmneziaWG variants, keys, obfuscation params, Docker lifecycle | protocol-specific lifecycle и helpers | firewall/sysctl/iptables mutations, Docker image lifecycle, shell scripts |
| `wireguard_manager.py` | classic WireGuard container lifecycle | общий shape install/status/config | privileged container, host networking/sysctl changes |
| `xray_manager.py` | VLESS-Reality, native/panel layout detection | attach/reconcile existing server layout | building images on target, external download during install, config writes |
| `telemt_manager.py` | Telegram MTProxy, container API, compose setup | service manager with local assets and API checks | `curl | sh`, package repo mutation, JSON through shell command |
| `dns_manager.py` | AmneziaDNS/Unbound | отдельный DNS service lifecycle | static Docker network/IP assumptions, DNS forwarding policy |
| `adguard_manager.py` | AdGuard Home modes | replacement vs side-by-side service mode | exposing ports, destructive replacement, static IP assumptions |
| `socks5_manager.py` | SOCKS5 via 3proxy | credential extraction and simple service lifecycle | plaintext proxy credentials, single-user model, exposed proxy port |

Паттерн "один manager на домен" переносим как архитектурная идея. Конкретные команды, paths, Dockerfiles, config templates и install-flow остаются заблокированы GPL-3.0 и production-рисками.

## Lifecycle operations

Повторяющийся lifecycle выглядит так:

1. Проверить доступность сервера и базовых зависимостей.
2. Подготовить host: Docker, сети, директории, firewall/sysctl.
3. Установить или пересобрать protocol container.
4. Сгенерировать keys/credentials/config.
5. Добавить или удалить user/client.
6. Прочитать статус, raw config или generated config.
7. Включить, выключить, удалить или очистить сервис.
8. Синхронизировать локальный state панели.

Для будущего дизайна важен не порядок конкретных команд, а lifecycle contract:

- operation idempotent или not idempotent;
- какие файлы и сервисы меняются;
- какие secrets создаются;
- какие проверки выполняются до изменения;
- какой recovery path есть при ошибке;
- какие события должны попасть в audit log.

## Destructive operations

Самые опасные зоны:

- очистка сервера через API: остановка и удаление контейнеров, images, networks и `/opt/amnezia`;
- uninstall protocol/container;
- raw server config save;
- firewall, iptables, sysctl и Docker network changes;
- replacement mode для DNS/AdGuard;
- remote reboot;
- backup/restore локального state с секретами;
- получение или выдача credentials/config через API.

Для `amn2` такие операции должны быть отдельным классом, а не обычными handler-ами:

- explicit confirmation;
- dry-run или plan preview;
- "what will change" summary;
- audit event до и после выполнения;
- secret redaction;
- rollback или recovery note;
- tests на отказ, partial failure и повторный запуск.

## Что полезно для `amn2`

- Command execution contract вместо свободных shell strings.
- Remote operation classes: read-only, secret-read, state-write, remote-exec, destructive.
- Dry-run-first design для install, uninstall, clear, raw config save и firewall/Docker changes.
- Manager interface checklist: `detect`, `status`, `plan`, `apply`, `rollback_note`, `audit_summary`, `test_double`.
- Host key enrollment/pinning как часть добавления сервера.
- Secret redaction policy для command logs, stderr/stdout и API errors.
- Audit event model для каждой remote operation.
- Test doubles для SSH runner и protocol manager-ов.
- Idempotency checks перед повторным запуском install/update операций.

## Что полезно для будущего гибридного проекта

- Plugin-like protocol managers: единый contract, но независимые modules для VPN, DNS, proxy и integrations.
- Protocol capability registry: какие операции поддерживает протокол, какие secrets генерирует, какие ports/networks трогает.
- Attach existing server reconciliation: распознать native layout, panel layout, existing containers, users и configs без немедленного изменения сервера.
- Service mode model: `replacement`, `side-by-side`, `disabled`, `external`.
- Background job model для долгих remote operations с progress, logs и cancel/timeout policy.
- Operator-facing "change plan" перед применением remote изменений.
- Health/status polling как отдельный read-only contract, не смешанный с install-flow.

## Что нельзя переносить как есть

- Auto-accept unknown SSH host keys в production.
- Sudo password inside shell command string.
- Логирование remote command без обязательной redaction.
- Shell command construction из runtime values без typed arguments и escaping policy.
- `curl | sh` или изменение package repositories как неявная часть manager-flow.
- Docker `latest` и pull/build на target host как production default.
- Privileged containers, firewall и sysctl mutations без dry-run, audit и recovery note.
- Static Docker network/IP assumptions без conflict detection.
- Config patching регулярными выражениями для sensitive service configs.
- API endpoints, которые возвращают service credentials без отдельного secret-read policy.

## Test-plan идеи для будущего production-дизайна

Минимальный тестовый контур для похожего manager-слоя:

- fake SSH runner записывает planned commands и не выполняет реальные изменения;
- каждая destructive operation сначала создает plan preview;
- host key mismatch блокирует выполнение до явного re-enrollment;
- sudo password не появляется в command string, logs, exceptions и audit payload;
- stdout/stderr проходят redaction перед сохранением или возвратом в API;
- manager contract tests проверяют `detect`, `status`, `plan`, `apply` и failure mapping;
- repeated install/update либо idempotent, либо возвращает понятный conflict;
- partial failure создает recovery note;
- raw config save валидируется schema/parser-ом до записи;
- firewall/Docker/network changes имеют conflict detection;
- secret-read operations требуют отдельного role/scope и создают audit event.

## Решение для lab

Статус deep-dive: `completed-first-pass`.

Для `amn2` этот upstream дает сильный список проверок перед проектированием remote operations, но не дает готовую production-архитектуру. Следующий слой анализа - feature gap: какие идеи уже можно поставить в очередь design review, какие оставить только для гибридного проекта, а какие заблокировать по лицензии или риску.

## Источники

- Репозиторий: https://github.com/PRVTPRO/Amnezia-Web-Panel
- README: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/README.md
- `app.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/app.py
- `ssh_manager.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/managers/ssh_manager.py
- `awg_manager.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/managers/awg_manager.py
- `wireguard_manager.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/managers/wireguard_manager.py
- `xray_manager.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/managers/xray_manager.py
- `telemt_manager.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/managers/telemt_manager.py
- `dns_manager.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/managers/dns_manager.py
- `adguard_manager.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/managers/adguard_manager.py
- `socks5_manager.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/managers/socks5_manager.py
- API surface deep-dive: [prvtpro-amnezia-web-panel-api-surface.md](prvtpro-amnezia-web-panel-api-surface.md)
