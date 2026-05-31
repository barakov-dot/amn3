# VPN Ops Lab / Amneziya: импорт контекста из чатов

Дата снимка: 2026-05-31.

Обновлено: 2026-05-31 после task/review-сессий по Local Amnezia Agent first slice и новых коммитов `amn2`.

Документ нужен для главного coordination-чата. Он собирает только рабочий контекст, который нужен для решений по `amn2`, будущему hybrid и общему Codex skill. Это не implementation plan и не разрешение на перенос функций.

## Что было прочитано

Локальные Codex-чаты:

- `MAIN - VPN Ops Lab`: текущий координационный чат.
- `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`: запуск lab, правила main/deep-dive чатов, первые upstream-выводы.
- `VPN Ops Lab - KYORESUAS-API`: анализ `kyoresuas/amnezia-api`, решение не ставить upstream как есть, design spec Local Amnezia Agent.
- `VPS-тест Amneziya`: продолжение live VPS-теста `amn2`.
- `Подготовка запуска на VPS`: первый запуск на живом VPS и handoff в новый чат.
- архивный ранний чат Amneziya: исходные продуктовые решения по боту, VPS, AmneziaWG 2.0, устройствам и срокам.
- task/review-сессии 2026-05-31 по Local Amnezia Agent first slice: Task 1-5, spec compliance review, code quality review и финальный review.

Локальные проекты:

- `C:\Users\SooL\Documents\VPS-OPS-LAB`
- `C:\Users\SooL\Documents\Amneziya`

GitHub:

- Локальный `Amneziya` checkout указывает на `https://github.com/barakov-dot/amn2.git`.
- GitHub connector в этом сеансе вернул `404` на `barakov-dot/amn2`, поэтому текущим источником правды считаются локальный checkout, git metadata и документы в `C:\Users\SooL\Documents\Amneziya`.
- Поиск GitHub по `amneziya` дал нерелевантные одноименные репозитории, их не используем как контекст проекта.

## Главные правила проекта

`amn2` остается production-направлением.

`vpn-ops-lab` остается исследовательской лабораторией.

Код из внешних проектов не копируем. Идея может перейти из lab в `amn2` только после проверки:

- лицензии;
- практической пользы;
- operational/security рисков;
- архитектурной совместимости;
- тестового плана;
- rollback/recovery модели, если есть state-write или remote operations.

Статусы решений для coordination:

- `переносим в design`;
- `готовим implementation plan`;
- `оставляем в lab`;
- `hybrid-only`;
- `нужен deep dive`;
- `отклоняем`;
- `blocked-by-license`;
- `blocked-by-risk`.

## Текущий `amn2` baseline

Локальная папка:

```text
C:\Users\SooL\Documents\Amneziya
```

Git:

```text
branch: codex-vps-test-prep
origin: https://github.com/barakov-dot/amn2.git
latest local commit: 8ecb0b4 Add configurable client config defaults
```

Последние новые коммиты в `amn2`:

- `573c368 Add VPS retest bundle`
- `8ecb0b4 Add configurable client config defaults`

Сейчас ветка `codex-vps-test-prep` синхронизирована с `origin/codex-vps-test-prep`.

Важно: в рабочем дереве `Amneziya` есть незакоммиченный Local Amnezia Agent first slice:

- `app/agent/`
- `tests/agent/`
- `docs/LOCAL_AGENT.ru.md`

Эти файлы не закоммичены. Не смешивать их с VPS retest/config-defaults работой без отдельного решения.

Последний известный полный прогон тестов из handoff:

```text
432 passed, 1 warning
```

Предупреждение: `StarletteDeprecationWarning` для `httpx` + `starlette.testclient`.

Последний focused прогон Local Agent tests в текущей рабочей копии:

```text
33 passed, 1 warning
```

Предупреждение то же: `StarletteDeprecationWarning` из `.codex_deps`.

## Продуктовые решения Amneziya / `amn2`

Первый контур:

- собственный VPS;
- Debian;
- AmneziaWG 2.0;
- Telegram-бот отдельно от VPN-сервера;
- один VPN-сервер в MVP, но архитектура должна поддержать несколько серверов позже;
- бесплатный тестовый режим с ручным подтверждением администратором;
- платежный слой позже, через абстракцию;
- один пользователь может иметь несколько устройств;
- каждое устройство имеет отдельный peer, IP, ключи и срок;
- лимит MVP: до 5 устройств на пользователя;
- сроки доступа: 3, 7, 10, 14, 30, 60, 90, 180 дней и произвольный срок;
- уведомления до окончания: 7, 5, 3, 1 день.

Runtime-решение из ранних документов: предпочтительный MVP-path был `systemd` + `awg/awg-quick` на Debian host без Docker. Но текущий live VPS фактически работает через Docker runtime Amnezia:

- container: `amnezia-awg2`;
- persistent config: `/opt/amnezia/awg/awg0.conf`;
- live network: `10.8.1.0/24`.

Это значит, что текущая практика `amn2` должна учитывать оба runtime: желаемый host/systemd и реально тестируемый Docker backend.

## Текущее состояние функций `amn2`

Уже реализованы и зафиксированы в handoff:

- Telegram bot и web admin panel;
- web panel на порту `3030`;
- пользователи, серверы, заявки, логи, настройки;
- config templates и `vpn://` preview;
- server health и VPS readiness;
- peer sync в карточке сервера;
- peer, созданные в приложении Amnezia, можно помечать как `Созданы в Amnezia`;
- локальные устройства без peer можно добавлять в Amnezia;
- выборочное удаление устройства у пользователя;
- `Disable VPN` удаляет peer из AmneziaWG, но оставляет устройство `disabled` в базе;
- `Enable VPN` возвращает `disabled` peer с тем же IP/public key/PSK;
- private key и PSK хранятся encrypted и показываются только через `Show secrets` с audit;
- опасные web-действия требуют browser confirm;
- failed VPS operations пишутся в `admin_actions` с redacted error;
- email config/recovery теперь всегда требуют подтвержденный `email_verified_at`.
- добавлен `VPS retest bundle`: CLI-команда `python -m app.cli server retest-plan ...` и блок `VPS retest bundle` в карточке сервера с командами повторной проверки;
- добавлены настраиваемые defaults клиентского AmneziaWG-конфига через `.env`: `CLIENT_DNS`, `CLIENT_ALLOWED_IPS`, `CLIENT_PERSISTENT_KEEPALIVE`, `CLIENT_AWG_JC`, `CLIENT_AWG_JMIN`, `CLIENT_AWG_JMAX`, `CLIENT_AWG_S1`, `CLIENT_AWG_S2`, `CLIENT_AWG_H1`...`CLIENT_AWG_H4`.

Текущий live VPS retest должен проверить:

- на VPS установлен последний коммит `8ecb0b4 Add configurable client config defaults`;
- `server retest-plan` печатает безопасный порядок проверки и не меняет VPS;
- новый клиент получает следующий IP после live peer из `/opt/amnezia/awg/awg0.conf`;
- для текущего снимка следующий ожидаемый IP: `10.8.1.3`;
- `Disable VPN` и `Enable VPN` реально работают на Docker runtime;
- внешние peer из приложения Amnezia не удаляются, а помечаются как `Созданы в Amnezia`;
- если `PeerApplyError` повторится, разбирать по строке `Details` и failed audit event.
- client config defaults из `.env` реально попадают в выдаваемые `.conf`, QR/`vpn://` preview и bot/email delivery без изменения уникальных keys/IP.

## `amn2` inventories в lab

В `research/amn2/` уже есть read-only inventories:

- auth/security;
- route/auth surface;
- secret surface;
- config delivery;
- remote operations;
- decision log.

Ключевое решение: web-admin 2FA поставлена на паузу 2026-05-30. Сейчас не пишем implementation plan для 2FA и не меняем production-код под TOTP/MFA. Следующий фокус: route/config delivery policy, remote operations, secret handling.

## Upstream deep dives

### PRVTPRO/Amnezia-Web-Panel

License verdict: GPL-3.0, только `research-only` / самостоятельное проектирование идей.

Полезные сигналы:

- API tokens;
- self-service endpoints;
- public sharing;
- OpenAPI/taxonomy по доменам;
- route policy matrix;
- safe SSH/sudo policy;
- RemoteOperationRunner;
- command execution contract;
- dry-run-first operations;
- audit events;
- host key enrollment;
- manager interface checklist.

Для hybrid:

- attach existing server;
- multi-protocol dashboard;
- manager architecture per protocol;
- Telegram integration;
- sensitive config delivery;
- operator backup/restore;
- protocol capability registry;
- plugin-like protocol managers;
- existing server reconciliation;
- background remote jobs.

Нельзя переносить как код: route layout, manager scripts, Dockerfile, config templates, UI.

### wg-easy/wg-easy

License verdict: AGPL-3.0-only, только самостоятельная реализация идей.

Полезные сигналы:

- focused WireGuard-first UX;
- public-safe client read models;
- client expiration;
- metrics surface;
- metrics privacy policy;
- scoped metrics token;
- permission wrapper with required resource check;
- forced setup/bootstrap flow;
- operational docs and migration guide;
- migration/import wizard.

Ограничения: ideas only; не копировать код, UI, API implementation или docs.

### kyoresuas/amnezia-api

License verdict: MIT, но для `amn2` все равно `idea-only`.

Primary verdict:

- для `amn2`: `high-signal design candidate`, не источник кода;
- для hybrid: `strong architecture reference`;
- как готовую установку на production Amnezia прямо сейчас не берем;
- upstream не копируем, потому что важнее собственный безопасный contract.

Полезная идея: Local Amnezia API agent рядом с Amnezia runtime вместо постоянного внешнего SSH control plane.

Главные риски upstream:

- Docker socket почти равен host compromise;
- один `x-api-key` без scopes;
- `/docs` и `/metrics` выглядят публичными относительно auth middleware;
- backup содержит secret-bearing state;
- import/reboot/delete destructive без отдельной policy;
- нет явного audit и dry-run/preview;
- shell execution через `child_process.exec` без выделенного command allowlist/redaction layer;
- нет полноценного тестового контура кроме CI lint/build.

## Текущая design queue для `amn2`

Ближайшие кандидаты:

- `RemoteOperationRunner`: design готов к review; first slice plan уже есть.
- `Local Amnezia Agent`: design spec готов; first slice implementation plan подготовлен.
- `Route Policy Matrix`: нужен как gate для новых endpoints.
- `Scoped API Tokens`: нужен для integration/agent/metrics, но после route policy.
- `Secret Inventory + Backup Policy`: foundational gate для backup/config/token work.
- `Public/Self-service Config Delivery`: `.conf`, QR и `vpn://` считать `secret-read`.
- `Domain Zone Exclusion Policy`: новый design candidate, но требует отдельного spec; настоящий bypass возможен только на клиенте.
- `Config delivery policy table`: actor, gate, risk class, output, audit, tests.

Пауза:

- `Web-admin 2FA`.

## Local Amnezia Agent: текущее решение

Решения из design spec:

- не устанавливаем `kyoresuas/amnezia-api` как есть;
- не копируем upstream-код;
- agent = привилегированный runtime adapter, а не публичная admin API;
- стартуем read-only;
- backup/import/reboot откладываем;
- route policy обязательна до реализации;
- secret inventory обязательна до config delivery.

First safe slice по design spec:

- package `app/agent`;
- route policy matrix;
- hash-only scoped bearer tokens;
- fake runtime adapter;
- FastAPI app factory;
- endpoints: `/agent/health`, `/agent/version`, `/agent/runtime`, `/agent/protocols`;
- public docs/openapi disabled for agent app;
- audit events for read routes;
- tests for policy/auth/runtime/API;
- no configs, QR, `vpn://`, backup, import, reboot, Docker mutation or write operations.

Текущее фактическое состояние first slice в `Amneziya`:

- Task 1 policy matrix: реализован, reviews approved.
- Task 2 scoped token auth: реализован; code review сначала нашел naive datetime issue, затем fix approved.
- Task 3 runtime snapshot/fake adapter: реализован, reviews approved.
- Task 4 protected read-only FastAPI API: реализован, reviews approved.
- Task 5 docs: `docs/LOCAL_AGENT.ru.md` создан.
- Финальный review complete slice: approved, без blocking findings.
- Последний локальный focused test: `33 passed, 1 warning`.
- Не закоммичено: `app/agent/`, `tests/agent/`, `docs/LOCAL_AGENT.ru.md`.

Неблокирующая review-заметка: в `app/agent/api.py` 401/403 сейчас различаются по тексту `AgentAuthError` и слову `scope`; позже лучше заменить на typed auth error reason.

Открытые вопросы перед implementation:

- agent живет внутри `amn2`, рядом с ним или отдельным пакетом;
- первый канал controller-agent: localhost, SSH tunnel, private WireGuard network или mTLS;
- какой runtime state безопасно читать без Docker socket;
- как минимально детектить AmneziaWG, AmneziaWG 2.0 и Xray.

## Очередь hybrid

Кандидаты для будущего hybrid:

- per-server API agent;
- multi-server balancing metadata;
- unified protocol adapter contract;
- attach existing server / reconciliation;
- multi-protocol dashboard;
- protocol capability registry;
- plugin-like protocol managers;
- domain-aware split routing;
- background remote jobs;
- migration/import wizard;
- operational docs system;
- observability baseline;
- account security baseline.

## Очередь общего Codex skill

Нужно усилить skill анализа VPN/control-panel upstream:

- license verdict first;
- отделять `architecture idea` от `code implementation`;
- для GPL/AGPL по умолчанию `research-only`;
- проверять auth methods, route guards, roles, ownership checks;
- классифицировать endpoints как `read-only`, `secret-read`, `state-write`, `remote-exec`, `destructive`;
- проверять Docker socket, sudo, systemd, host filesystem, VPN config paths;
- защищены ли `/docs`, `/metrics`, `/health`, backup/import;
- есть ли scoped tokens, expiry, revoke, rotation, audit, rate limit;
- считать `.conf`, QR и `vpn://` secret-bearing;
- проверять redacted backup, dry-run/preview, recovery note;
- искать secret leakage в logs/errors/metrics;
- проверять lock/queue для concurrent config writes;
- требовать staging/runtime tests, а не только lint/build.

## Ближайшие рабочие развилки

Текущий режим coordination: состояние проекта внесено, дальнейшая активная работа временно продолжается в deep-dive чате `VPN Ops Lab - KYORESUAS-API`.

Main coordination должен принимать от KYORESUAS/API-чата новые выводы и обновлять:

- `research/upstreams/kyoresuas-amnezia-api*.md`;
- `ideas/candidates-for-amn2.md`;
- `ideas/candidates-for-hybrid.md`;
- `ideas/add-to-skill.md`;
- решение по Local Amnezia Agent / API surface / install-runtime / auth-secrets.

0. Сначала решить судьбу незакоммиченного Local Agent first slice.

Рекомендованный безопасный git-маршрут из review-чата:

- не использовать старую ветку `codex/local-amnezia-agent-first-slice`, потому что она отстала от `codex-vps-test-prep`;
- создать свежую ветку от текущего `8ecb0b4`, например `codex/local-agent-first-slice`;
- stage только `app/agent/`, `tests/agent/`, `docs/LOCAL_AGENT.ru.md`;
- закоммитить `Add local Amnezia agent first slice`;
- прогнать `tests/agent`, затем связанные regression tests.

1. Затем стабилизировать live VPS retest в `amn2`.

Это практический путь: подтвердить peer sync, `Созданы в Amnezia`, `Добавить в Amnezia`, выборочное удаление устройства, disable/enable, email verification и Docker runtime behavior.

2. После retest review выбрать, продолжаем ли `RemoteOperationRunner first slice` или расширяем `Local Amnezia Agent`.

RemoteOperationRunner ближе к текущему `amn2` VPS flow. Local Agent ближе к будущему API-first управлению Amnezia. Первый read-only slice Local Agent уже реализован локально, но еще не интегрирован через commit/PR.

3. Для `kyoresuas/amnezia-api` можно продолжить три deep-dive карточки:

- API surface и route policy;
- install/runtime hardening;
- auth/secrets.

4. Для coordination-чата держать правило: любая новая идея сначала попадает в очередь с verdict, а не сразу в implementation.

## Источники в workspace

VPN Ops Lab:

- `README.md`
- `ideas/candidates-for-amn2.md`
- `ideas/candidates-for-hybrid.md`
- `ideas/add-to-skill.md`
- `research/amn2/README.md`
- `research/amn2/decisions.md`
- `research/upstreams/kyoresuas-amnezia-api.md`
- `docs/superpowers/specs/2026-05-31-local-amnezia-agent-design.md`
- `docs/superpowers/plans/2026-05-31-local-amnezia-agent-first-slice.md`
- `docs/superpowers/specs/2026-05-30-design-specs-index-amn2-transfer-checklist.md`

Amneziya / `amn2`:

- `docs/NEXT_CHAT_HANDOFF.ru.md`
- `docs/DECISIONS.ru.md`
- `docs/WEB_PANEL_AND_BOT_SETUP.ru.md`
- `docs/VPS_RETEST_PROTOCOL.ru.md`
- `docs/VPS_LOG_COLLECTION.ru.md`
- `docs/PRODUCTION_VPS_CHECKLIST.ru.md`
- `docs/SERVER_CONFIG_TEMPLATE.ru.md`
- `docs/RUNTIME_REGISTRY.ru.md`
