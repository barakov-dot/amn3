# kyoresuas/amnezia-api

## Паспорт

- Репозиторий: https://github.com/kyoresuas/amnezia-api
- Дата первичного анализа: 2026-05-31
- Тип проекта: server-installed REST API для управления Amnezia VPN runtime.
- Основной стек: Node.js, TypeScript, Fastify, Swagger/OpenAPI, Docker CLI, PM2/Docker Compose, nginx setup script.
- Поддерживаемые протоколы: AmneziaWG, AmneziaWG 2.0, Xray.
- Лицензия: MIT.
- Статус для `amn2`: сильный research candidate для API/user-management дизайна, но без копирования кода.
- Статус для будущего гибридного проекта: high-signal reference для node-agent/API поверх нескольких VPN runtime.

## Актуализация 2026-06-10

Свежая проверка GitHub `main` зафиксирована отдельно: [kyoresuas/amnezia-api GitHub refresh 2026-06-10](kyoresuas-amnezia-api-github-watch-2026-06-10.md).

```text
latest_commit: ffdc78c refactor: устойчивость записи конфигов, валидация и чистка кода
latest_commit_date_utc: 2026-06-02T21:02:25Z
latest_tree_sha: ffdc78cf4e6f653322c6df251df10a7d7274a887
```

Новые полезные сигналы для AMN2: in-process write serialization, safer config write pattern, `active|disabled` + `expiresAt` lifecycle vocabulary, QR/`vpn://` compatibility work, rate-limit/Helmet hardening signals and setup/deploy resilience. Это усиливает текущий `P4-NG` / `WAPI-V001` threat model, но не меняет запрет на копирование кода, установку upstream service, public API `3040`, config delivery, `/api/clients` write CRUD, backup/import/reboot или production peer writes.

Одна старая оценка ниже требует уточнения: в первичном проходе rate-limit не был найден как отдельный production gate, но свежий upstream уже содержит Fastify rate-limit hardening. Для AMN2 это становится обязательным пунктом будущего public/self-service/config/token gate, а не разрешением открывать маршруты.

## Краткое описание

`amnezia-api` превращает локальное управление установленной Amnezia в HTTP API. Проект ставится на тот же сервер, где уже работают Amnezia Docker-контейнеры, и через API дает операции для клиентов, конфигов, статуса сервера, метрик, backup/import и reboot.

Для нашей текущей задачи это очень близкий сигнал: не внешняя панель по SSH, а локальный API-агент на сервере Amnezia. Внешняя панель, Telegram-бот, billing или orchestrator могут говорить с этим агентом через `x-api-key` и не заходить вручную на VPS.

## Лицензия и ограничения

В репозитории указан `LICENSE` с MIT License, README также заявляет MIT.

Первичный license verdict:

- идеи можно изучать и переносить как самостоятельный дизайн;
- код юридически permissive, но по правилам VPN Ops Lab в `amn2` его не копируем;
- если когда-нибудь появится причина использовать фрагменты реализации, нужен отдельный license/dependency review и сохранение copyright notice;
- для production-переноса важнее не лицензия, а security/operational gate: API управляет VPN-пользователями, секретами, контейнерами и reboot сервера.

## Архитектура и стек

Приложение запускается как Fastify API с TypeScript-схемами, Swagger UI на `/docs`, Prometheus metrics plugin и DI через Awilix. Маршруты собраны вокруг двух доменов:

- `/clients` - список, создание, обновление, QR, удаление;
- `/server` - статус, нагрузка, backup/import, reboot.

Runtime-модель:

- `src/services/clients` выбирает protocol service по `protocol`;
- отдельные сервисы есть для AmneziaWG, AmneziaWG 2.0 и Xray;
- AmneziaWG/AmneziaWG2 управляются через `docker exec ... sh -lc ...`, чтение/запись конфигов и `wg/awg syncconf`;
- Xray управляется через чтение/запись `server.json` и restart контейнера;
- Docker deployment пробрасывает `/var/run/docker.sock` внутрь API-контейнера;
- PM2 deployment запускает API на хосте и использует локальный Docker CLI;
- setup script умеет генерировать `.env`, API key, определять протоколы по контейнерам, поднимать nginx и настраивать Xray stats.

Это не remote SSH model. Это local control-plane agent, которому нужен доступ к Docker и файлам внутри Amnezia containers.

## API surface

README и controllers показывают следующий публичный contract:

| Risk class | Endpoint | Назначение |
| --- | --- | --- |
| `read-only` | `GET /clients` | список клиентов, peers, traffic, handshake/status |
| `secret-read` + `state-write` | `POST /clients` | создать клиента и вернуть `vpn://` config |
| `state-write` | `PATCH /clients` | изменить status/expiresAt, фактически включить/отключить peer |
| `secret-read` | `POST /clients/qr` | превратить config в QR data URI |
| `destructive` | `DELETE /clients` | удалить клиента из table/config |
| `read-only` | `GET /server` | статус сервера, протоколы, лимиты |
| `read-only` | `GET /server/load` | CPU/RAM/disk/network/Docker stats |
| `secret-read` | `GET /server/backup` | выгрузить полный backup конфигов и ключевых материалов |
| `destructive` + `secret-write` | `POST /server/backup` | импортировать backup и перезаписать runtime state |
| `destructive` + `remote-exec` | `POST /server/reboot` | выполнить `sudo reboot` |
| `read-only` | `GET /healthz` | healthcheck |
| `read-only` | `GET /metrics` | Prometheus metrics |

Auth model сейчас простая: почти все бизнес-маршруты защищены header `x-api-key`. `/healthz`, `/metrics` и `/docs` не требуют этого preHandler. Отдельных ролей, scopes, expiry, rotation, audit events и rate limit в первом проходе не найдено.

## Функции

Сильные функции для изучения:

- единый client API поверх AmneziaWG, AmneziaWG 2.0 и Xray;
- создание пользователя с немедленной выдачей `vpn://` import config;
- QR generation в формате, который рассчитан на Amnezia client;
- pause/resume пользователя без удаления ключа;
- `expiresAt` и cron-задача, которая отключает просроченных клиентов;
- server status с `region`, `weight`, `maxPeers`, `totalPeers` и protocols;
- basic load metrics и Docker container stats;
- backup/import server state через API;
- dual deployment story: PM2 или Docker Compose.

Особенно полезен product signal: API сразу думает не только о CRUD peers, но и о routing между несколькими серверами через `SERVER_REGION`, `SERVER_WEIGHT`, `SERVER_MAX_PEERS`.

## UX и operator flow

UX здесь в основном API-first:

- внешний продукт может создать клиента одним запросом и сразу получить импортируемый config;
- пользовательский доступ можно поставить на паузу и вернуть без пересоздания конфига;
- expiration работает как billing/trial primitive;
- Swagger UI снижает порог интеграции;
- `/server` дает минимальную модель для балансировки между нодами;
- `/server/load` дает оператору инфраструктурное состояние без SSH.

Для `amn2` это полезнее как backend/operator UX, чем как готовый user-facing интерфейс.

## Production-подходы

Позитивные сигналы:

- Dockerfile использует multi-stage build;
- runtime container запускается не root-пользователем;
- Docker Compose биндет API на `127.0.0.1:4001`;
- есть healthcheck;
- setup script генерирует API key вместо сохранения `change-me`;
- CI делает lint и build на Node 20/22;
- setup поддерживает PM2 startup и Docker Compose;
- есть Swagger/OpenAPI-схемы и i18n ответов.

Ограничения для production:

- Docker mode дает API-контейнеру доступ к `/var/run/docker.sock`, что фактически равно высокому контролю над host;
- setup nginx открывает HTTP/80 без TLS-by-default;
- auth - один shared API key без scopes, expiry, rotate/revoke и owner inheritance;
- `/metrics` и `/docs` выглядят публичными относительно auth middleware;
- CORS настроен как `origin: true`;
- backup отдает secret-bearing state: WireGuard config, PSK, clientsTable, Xray private key/short id;
- import backup перезаписывает состояние без redacted preview, dry-run, confirmation, audit и rollback note;
- reboot endpoint destructive, но не имеет отдельного destructive scope/confirmation;
- shell execution построен на `child_process.exec`, command allowlist и redaction layer не выделены;
- нет полноценного тестового контура, найден только CI lint/build.

## Риски

- `docker.sock` делает compromise API почти compromise host.
- `x-api-key` без scopes превращает любой интеграционный токен в admin-equivalent доступ.
- `GET /server/backup` является высокорисковым `secret-read`: там есть материалы, достаточные для восстановления/клонирования VPN state.
- `POST /server/backup`, `DELETE /clients`, `POST /server/reboot` требуют отдельного destructive policy.
- Выдача `vpn://` и QR должна считаться выдачей секрета, даже если private key не виден человеку как обычная строка.
- Metrics и server load могут раскрывать activity metadata, container names, traffic и косвенно пользовательскую активность.
- Операции create/delete/update пишут несколько состояний: config file, clientsTable, live sync/restart. Нужен contract для partial failure.
- Нет явного audit log для state-changing операций.
- Нет explicit lock/queue для параллельных writes в один config/clientsTable.
- Setup script делает удобный bootstrap, но одновременно меняет систему: apt packages, Docker, nginx, ufw, PM2/systemd.

## Полезные идеи для `amn2`

- Локальный API-agent на сервере Amnezia как альтернатива постоянному SSH control plane.
- Route policy matrix для `/clients` и `/server` до реализации: actor, auth method, risk class, side effect, audit, tests.
- Client lifecycle primitive: active/disabled, `expiresAt`, cleanup task, без немедленного удаления ключей.
- Secret-safe config delivery: `vpn://`, QR и file config как единый `secret-read` класс.
- Protocol service abstraction: `createClient`, `getClients`, `updateClient`, `deleteClient`, `exportBackup`, `importBackup`.
- Server inventory endpoint: `region`, `weight`, `maxPeers`, `totalPeers`, protocols.
- Metrics/load endpoint, но только после privacy policy и scoped token.
- Backup/import API как будущая возможность, но только через redacted/full modes, encryption и validation.

Перед переносом в `amn2` обязательны:

- scoped tokens вместо одного shared key;
- local-only bind по умолчанию и явная reverse proxy/TLS story;
- destructive operation confirmations или separate scopes;
- audit events до/после state changes;
- dry-run/preview для import/delete/reboot и любых host/container изменений;
- partial-failure model и recovery note;
- tests на forbidden access, secret leakage, concurrent writes и failed apply.

## Полезные идеи для будущего гибридного проекта

- Node-agent per VPN server, управляемый внешней панелью.
- Multi-server balancing через server metadata: region, weight, max peers, load.
- Единый API contract поверх AmneziaWG, AmneziaWG 2.0, Xray и будущих runtimes.
- External integrations: Telegram bot, billing, support tooling через stable API.
- Agent/controller split: серверный агент держит опасные Docker/file операции локально, центральная панель получает ограниченный integration surface.
- Background job model для import/reconcile/restart, потому что часть операций не должна быть sync HTTP request.

## Идеи для общего Codex skill

Добавить checklist для server-installed API wrappers:

- есть ли доступ к Docker socket, systemd, sudo, host filesystem или VPN secret paths;
- какие endpoints являются `read-only`, `secret-read`, `state-write`, `remote-exec`, `destructive`;
- защищены ли `/docs`, `/metrics`, `/health`, backup и import endpoints;
- есть ли scoped tokens, expiry, revoke, rotation, rate limit и audit;
- есть ли redacted backup по умолчанию;
- есть ли dry-run/preview и recovery note перед import/delete/reboot;
- не попадают ли config, QR, `vpn://`, private key, PSK, API key в logs/errors/metrics;
- есть ли lock/queue для конфигов, которые пишутся несколькими handlers;
- есть ли staging/test plan для реального VPN runtime.

## Решение

`kyoresuas/amnezia-api` стоит держать как high-priority upstream для нашей текущей темы "управление пользователями Amnezia по API".

Primary verdict:

- для `amn2`: `high-signal design candidate`, не источник кода;
- для hybrid: `strong architecture reference`;
- для server install на production Amnezia прямо сейчас: только после отдельного staging-прогона, threat model и hardening plan;
- для копирования кода: не нужно, даже при MIT, потому что важнее спроектировать свой безопасный contract.

## Следующие шаги

- Сделать отдельный deep-dive по API surface и route policy matrix.
- Сделать отдельный deep-dive по install/runtime hardening: Docker socket, nginx, TLS, local bind, PM2/systemd.
- Сделать отдельный deep-dive по auth/secrets: API key, backup, `vpn://`, QR, metrics, logs.
- Сравнить с текущим `amn2` remote operations inventory и решить, нужен ли `LocalAmneziaAgent` design spec.

## Источники

- Репозиторий: https://github.com/kyoresuas/amnezia-api
- README: https://github.com/kyoresuas/amnezia-api/blob/main/README.md
- LICENSE: https://github.com/kyoresuas/amnezia-api/blob/main/LICENSE
- `package.json`: https://github.com/kyoresuas/amnezia-api/blob/main/package.json
- `docker-compose.yml`: https://github.com/kyoresuas/amnezia-api/blob/main/docker-compose.yml
- `Dockerfile`: https://github.com/kyoresuas/amnezia-api/blob/main/Dockerfile
- `.env.example`: https://github.com/kyoresuas/amnezia-api/blob/main/.env.example
- `src/controllers/clients.controllers.ts`: https://github.com/kyoresuas/amnezia-api/blob/main/src/controllers/clients.controllers.ts
- `src/controllers/server.controllers.ts`: https://github.com/kyoresuas/amnezia-api/blob/main/src/controllers/server.controllers.ts
- `src/middleware/auth/auth.middleware.ts`: https://github.com/kyoresuas/amnezia-api/blob/main/src/middleware/auth/auth.middleware.ts
- `src/services/clients/clients.service.ts`: https://github.com/kyoresuas/amnezia-api/blob/main/src/services/clients/clients.service.ts
- `src/services/amneziaWg/amneziaWg.service.ts`: https://github.com/kyoresuas/amnezia-api/blob/main/src/services/amneziaWg/amneziaWg.service.ts
- `src/services/amneziaWg2/amneziaWg2.service.ts`: https://github.com/kyoresuas/amnezia-api/blob/main/src/services/amneziaWg2/amneziaWg2.service.ts
- `src/services/xray/xray.service.ts`: https://github.com/kyoresuas/amnezia-api/blob/main/src/services/xray/xray.service.ts
- `src/services/server/server.service.ts`: https://github.com/kyoresuas/amnezia-api/blob/main/src/services/server/server.service.ts
- `src/helpers/*Connection.ts`: https://github.com/kyoresuas/amnezia-api/tree/main/src/helpers
- `scripts/setup.sh`: https://github.com/kyoresuas/amnezia-api/blob/main/scripts/setup.sh
- CI workflow: https://github.com/kyoresuas/amnezia-api/blob/main/.github/workflows/ci.yml
