# Current Override 2026-06-06

`amn2/codex-vps-test-prep` current head is `32d01fd Update integration status for controlled prod`. Current AMN3 update+smoke package `32d01fd` passed real VPS read-only smoke on 2026-06-06, `run_id=20260606T185114Z`; `1a193b9` is now historical prior VPS-smoked runtime/source.

Read-only integration status update 2026-06-06: `32d01fd` updates `/api/integration/status` to report `read_only_vps_smoked`, Phase 2 `verified_live`, and controlled-prod readiness pending without enabling write routes or write operations. AMN3 evidence is `research/amn2/integration-status-controlled-prod-update-2026-06-06.md`. The previous local-only operation-contract fast-forward remains recorded at `research/amn2/remote-partial-failure-contract-2026-06-06.md`.

```text
AMN3 package: dist/amn2-vps-update-and-smoke-kit-32d01fd.zip
sha256: BE59AF74001AC4F094C753B565A4E672194D823C4F65B6CB476F4FF01B310807
source zip: dist/amn2-codex-vps-test-prep-32d01fd-source.zip
source sha256: 034753DA7EC42ACF869519F43909EEFDC8A392A5665B2A33C935F8A058CCB99B
local verification: focused 7 passed; adjacent smoke/security 26 passed; package SHA/source SHA/no-BOM/no-forbidden-source-entry/test-extract checks passed
package evidence: research/amn2/integration-status-controlled-prod-update-2026-06-06.md
VPS result for 32d01fd: read-only-vps-smoke-pass, run_id 20260606T185114Z
VPS smoke evidence: research/amn2/integration-status-controlled-prod-update-2026-06-06.md
previous VPS-smoked runtime/source: 1a193b9, run_id 20260606T154636Z, evidence research/amn2/remote-partial-failure-contract-vps-smoke-evidence-2026-06-06.md
controlled prod readiness: readiness-prefill-recorded, operator confirmations pending
controlled prod runbook: docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
controlled prod evidence: research/amn2/controlled-prod-readiness-2026-06-06.md
previous VPS-smoked source: 568c611, run_id 20260605T162742Z, evidence research/amn2/phase-2-post-psk-stdin-vps-smoke-evidence-2026-06-05.md
docs-only cleanup: 6b5b5b7 Document stdin PSK peer apply
local-only contract merge: 1a193b9 Add remote partial failure contract
read-only integration status update: 32d01fd Update integration status for controlled prod
```

Phase 2 live single disposable test peer apply/revoke is verified-live on stable `7764ae7`; `568c611` adds safer `--preshared-key-stdin` handling and passed read-only VPS update/smoke.

```text
AMN3 evidence: research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md
result: verified-live
scope: exactly one disposable test peer apply/sync/revoke/sync
```

This does not unlock broad write API, public/self-service config delivery, API `config:read`, `/api/clients` CRUD, backup/import/reboot routes, Local Agent mutations or public web/API exposure. Older `294803e`, `7764ae7`, `568c611` and `1a193b9` package blocks below are historical evidence; `32d01fd` is the current VPS-smoked runtime/source baseline. Next gate is operator-only controlled-prod readiness, not public prod.
# VPN Ops Lab / Amneziya: импорт контекста из чатов

Дата снимка: 2026-06-02.

Обновлено: 2026-06-02 после повторного прохода по проектным чатам, пушам AMN3/`amn2`, VPS install package и активной ветке `codex/read-only-api-route-shell`.

Документ нужен для главного coordination-чата. Он собирает только рабочий контекст, который нужен для решений по `amn2`, будущему hybrid и общему Codex skill. Это не implementation plan и не разрешение на перенос функций.

## Актуализация 2026-06-02

Стабильная точка правды `amn2`:

```text
repo: C:\Users\SooL\Documents\Amneziya
branch: codex-vps-test-prep
remote branch: amn2/codex-vps-test-prep
latest committed head: 7764ae7 Cover integration status in API smoke
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
status: remote branch current after read-only API shell and API/web-panel finish merge
```

Активная рабочая ветка `amn2` для установки/API smoke:

```text
repo: C:\Users\SooL\Documents\Amneziya
branch: codex/read-only-api-route-shell
remote branch: amn2/codex/read-only-api-route-shell
latest committed head: 2010d60 Add API VPS smoke evidence template
base stable line: d0939d8 Merge pull request #6 from barakov-dot/codex/ssh-host-key-identity-verifier
status: pushed, local worktree clean, full local suite 588 passed with expected StarletteDeprecationWarning, latest real VPS API-only smoke passed run_id=20260603T112418Z
working chat: Переводим AMN на API
```

Изменения в активной API-ветке:

```text
e99d5f3 Fix editable install package discovery
6534ac4 Add read-only API route shell
9cccdc2 Add API token smoke CLI
b37103a Harden local API smoke readiness
2010d60 Add API VPS smoke evidence template
```

API shell открывает только read-only aggregate routes с scoped tokens:

```text
GET /api/servers -> server:read
GET /api/servers/{server_name}/summary -> server:read
GET /api/metrics/summary -> metrics:read
GET /api/users/summary -> metrics:read
```

Запрещено публиковать `.conf`, QR, `vpn://`, private key, PSK, endpoint host/port, SSH host/port, raw token/header/hash или detailed client metadata.

Текущая VPS-gate candidate branch для remote-operation проверки:

```text
branch: codex/remote-operation-vps-gate-prep
head: 7281254 Merge stable API web panel baseline into remote operation gate
base: d0939d8 Merge pull request #6 from barakov-dot/codex/ssh-host-key-identity-verifier
status: pushed to amn2, local tests green, awaits real VPS gate
runbook: research/amn2/vps-gate-remote-operation-dry-run-audit.md
```

Scoped API token storage/auth layer остается важным baseline, но после него в `codex-vps-test-prep` уже вошли route/auth binding, API token lifecycle и SSH host key verifier:

```text
app/services/api_tokens.py
app/db/schema.py
app/db/repositories.py
docs/API_TOKEN_POLICY.ru.md
tests/services/test_api_tokens.py
tests/db/test_repositories.py
```

Смысл: закрепить hash-only scoped API token baseline без `/api/*` routes: one-time raw token issue metadata, scopes `server:read`/`metrics:read`, expiry, revoke, last-used и safe audit metadata.

Проверка: RED `1 import error as expected`, focused security/db/services suite `54 passed`, full local suite `542 passed`, warning только `StarletteDeprecationWarning`.

Дополнительная проверка 2026-06-01: `tests/web/test_config_templates.py tests/web/test_servers.py tests/web/test_users.py -q --basetemp tmp\pytest-web-panel-safe` -> `49 passed, 1 StarletteDeprecationWarning`.

Текущая точка правды AMN3 / lab:

```text
repo: C:\Users\SooL\Documents\VPS-OPS-LAB
branch: master
remote: https://github.com/barakov-dot/amn3.git
package state reviewed in this refresh: master; verify exact current head with git log -1 after package publish
status: synchronize with origin/master after package publish
```

Последние AMN3 pushes, учтенные в координации:

```text
25e02e9 Add VPS install package
87da41d Fix VPS installer user creation fallback
7fc3aee Set KYORESUAS API integration priority
8b4cc81 Refresh project coordination state
2b845cb Make API smoke skip server preflight by default
```

Актуальный install/update package:

```text
dist/amn2-vps-install-294803e.zip
sha256: 9B561FBF9C1ACDE403CFF6DA3A49544074457D3089FF8A8D0859B0CEBBBB1501
dist/amn2-vps-update-and-smoke-kit-294803e.zip
sha256: 702BAD7EBD69F80FC75FD31648383258B6C042BD51B801BC72BE2FD125813CE2
```

Package note: current `7764ae7` update+smoke package includes `amn2_api_loopback_smoke.sh` version `2026-06-04.3`, DB-only server config sync, and 5 read-only API route checks including `/api/integration/status`. Historical `294803e` and `5f12736` packages remain available as evidence baselines.

Соседний AMN3 branch-only push, учтенный как комментарий к pre-VPS координации:

```text
branch: origin/codex/local-agent-production-wiring
head: d5f30c6 Clarify pre-VPS matrix baseline
artifact: docs/AMN3_PRE_VPS_LOCAL_STATUS_MATRIX.ru.md
status: не слито в master; не повторять соседний VPS smoke, использовать только для сверки local-only/pre-VPS boundaries
```

После verified live VPS baseline уже выполнены и записаны в AMN3:

- `d1d9690 Add route auth operation policy matrix`;
- `94ad807 Document secret-bearing delivery artifacts`;
- config delivery integrity local evidence at `94ad807`;
- `dfe27ee Harden public email token safety`;
- remote operation contract / partial-failure / dry-run-audit local-gate evidence;
- `c5d7eb6 Harden Local Agent audit contract`;
- `22dfc37 Clarify web panel operation gates`;
- `1fdcde5 Add scoped API token storage contract`;
- Route/Auth binding tests branch `f9d2c79`, merged through current production line;
- API token lifecycle gate branch `256d0c0`, merged through PR #4/#5;
- SSH host key verifier `dd20364`, merged through PR #6; later read-only API route shell moved current `amn2` head to `5f12736`, then API/web-panel finish moved current head to `294803e`;
- remote operation VPS-gate candidate `7281254`, real VPS Phase 1 read-only/dry-run passed as `dry-run-only-pass`; evidence `research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md`; Phase 2 live single disposable peer apply/revoke passed later on current stable `7764ae7`, evidence `research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md`.
- Current VPS update+smoke package `dist/amn2-vps-update-and-smoke-kit-7764ae7.zip`; historical install/update packages for `294803e` remain available as evidence baselines;
- KYORESUAS API integration priority plan;
- read-only API route shell branch `codex/read-only-api-route-shell`, real VPS loopback API smoke passed through AMN3 operator script `scripts/vps/amn2_api_loopback_smoke.sh`, then fast-forward merged into stable `codex-vps-test-prep` at `5f12736`;
- API/web-panel finish slice branch `codex/api-web-panel-finish`, full local suite `594 passed`, then fast-forward merged into stable `codex-vps-test-prep` at `294803e`; real VPS API/web-panel gate passed 2026-06-04, `run_id=20260604T102355Z`, evidence `research/amn2/api-web-panel-vps-evidence-2026-06-04.md`.

Следующий рабочий выбор:

1. Current production/API-web head is `7764ae7`; `294803e` remains historical API/web-panel gate evidence.
2. Future API expansion requires separate route/secret/remote-write gates.
3. API/web-panel VPS test для `294803e` считать пройденным: loopback API smoke + web route check, без live apply.
4. Controlled real VPS verification gate Phase 2 is now `verified-live` for exactly one disposable test peer on current stable `7764ae7`; routes that call SSH, sync peers, emit config or mutate runtime state still require their own scoped gates.

Старые блоки ниже, где `91aeb3e` указан как latest clean baseline, считать историческим контекстом verified live stage.

## Исторический снимок после verified live VPS cycle

После исходного import-снимка `amn2` прошел первый подтвержденный live VPS cycle. Точка правды на тот момент:

```text
repo: C:\Users\SooL\Documents\Amneziya
branch: codex-vps-test-prep
latest: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
status: clean, synchronized with origin/codex-vps-test-prep
```

Проверено: approve, working config, peer sync, disable/enable и выборочное удаление устройства на Docker AmneziaWG runtime. Более старые блоки ниже, где live retest еще указан как будущая проверка, считать историческим контекстом. Для текущей работы использовать `docs/NEXT_CHAT_AFTER_AMN2_VPS_LIVE.ru.md`, `docs/PROJECT_STATUS_CURRENT.ru.md`, `research/amn2/transfer-backlog.md` и `research/amn2/api-readiness-audit-after-live-baseline.md`.

AMN3 / lab:

```text
repo: C:\Users\SooL\Documents\VPS-OPS-LAB
branch: master
remote: https://github.com/barakov-dot/amn3.git
committed head: a0ccfef Expand secret inventory priority gate
origin/master: 8212281 Document amn2 live migration to lab
status: ahead 2, with local uncommitted status/audit/backlog updates
```

API-readiness audit уже выполнен, а его первый policy slice уже перенесен в `amn2`:

```text
Route/Auth/Operation Policy Matrix for current amn2 surfaces
```

После него API-направление перешло в активную собственную ветку `codex/read-only-api-route-shell`; VPS loopback API smoke passed, без расширения до write/config routes.

## Что было прочитано

Локальные Codex-чаты:

- `MAIN - VPN Ops Lab`: текущий координационный чат.
- `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`: запуск lab, правила main/deep-dive чатов, первые upstream-выводы.
- `VPN Ops Lab - KYORESUAS-API`: анализ `kyoresuas/amnezia-api`, решение не ставить upstream как есть, design spec Local Amnezia Agent.
- `VPS-тест Amneziya`: продолжение live VPS-теста `amn2`.
- `Подготовка запуска на VPS`: первый запуск на живом VPS и handoff в новый чат.
- архивный ранний чат Amneziya: исходные продуктовые решения по боту, VPS, AmneziaWG 2.0, устройствам и срокам.
- task/review-сессии 2026-05-31 по Local Amnezia Agent first slice: Task 1-5, spec compliance review, code quality review и финальный review.
- task/review/worker-сессии 2026-05-31 по Local Agent production wiring: settings, token config builder, runtime adapter, CLI commands, systemd/runbook docs, reviews and PR merge.
- live VPS transition and API-readiness lab сессии после verified `amn2` cycle.

Локальные проекты:

- `C:\Users\SooL\Documents\VPS-OPS-LAB`
- `C:\Users\SooL\Documents\Amneziya`

GitHub:

- Локальный `Amneziya` checkout указывает на `https://github.com/barakov-dot/amn2.git`.
- GitHub connector в этом сеансе вернул `404` на `barakov-dot/amn2`, поэтому текущим источником правды считаются локальный checkout, git metadata и документы в `C:\Users\SooL\Documents\Amneziya`.
- Поиск GitHub по `amneziya` дал нерелевантные одноименные репозитории, их не используем как контекст проекта.

## Главные правила проекта

AMN3 остается coordination/knowledge-направлением.

`amn2` остается production-направлением.

`vpn-ops-lab`/AMN3 остается исследовательской лабораторией, design registry и transfer gate.

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
latest commit: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Ветка `codex-vps-test-prep` сейчас синхронизирована с `origin/codex-vps-test-prep`, working tree чистый.

Ключевые новые commits/merges после старого handoff:

- `62ae49e Merge pull request #2 from barakov-dot/codex/config-delivery-artifact-integrity-isolated`
- `286b5cc Merge pull request #3 from barakov-dot/codex/local-agent-production-wiring`
- `9d15cbe Polish VPS admin sync behavior`
- `bfcdd06 Show working server configs`
- `62e8f1c Show approved configs immediately`
- `f72eb25 Clarify VPS approve sync checklist`
- `d6eda20 Document verified VPS live cycle`
- `91aeb3e Document VPS verified tag`

Local Amnezia Agent first slice и production wiring уже находятся в актуальном production baseline: foundation через PR #2, production wiring через PR #3. Не открывать повторный PR для старых Local Agent branches.

Последняя известная локальная проверка `amn2` после verified baseline:

```text
508 passed, 1 warning
```

Предупреждение: `StarletteDeprecationWarning` для `httpx` + `starlette.testclient`.

API-readiness audit focused verification:

```text
tests/agent
tests/config/test_settings.py
tests/server/test_operation_runner.py
tests/server/test_checks.py
tests/web/test_cli_web.py

109 passed, 1 warning
```

Предупреждение то же: `StarletteDeprecationWarning` из `.codex_deps`. В одном запуске после успешного pytest был ignored Windows temp cleanup `PermissionError`; exit code был 0.

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

Verified live VPS cycle уже подтвердил:

- approve заявки в Telegram создает рабочий peer;
- клиентский config подключается;
- web panel показывает working config сразу после approve;
- `Run peer sync` подтверждает live-состояние;
- внешние peer, созданные в приложении Amnezia, не удаляются и отображаются отдельно;
- missing local device можно добавить в AmneziaWG;
- `Disable VPN` и `Enable VPN` работают;
- выборочное удаление устройства работает;
- Docker runtime apply/revoke прошел живую проверку;
- AmneziaWG 2.0 template/defaults приведены к рабочему формату.

Новый live retest нужен только если меняется apply/revoke/config/sync логика, IP allocation, peer classification, disable/enable/delete или Docker runtime write/restart behavior.

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

Актуальная design queue после verified baseline:

- `codex/read-only-api-route-shell`: merged API branch, head `5f12736`, real VPS loopback smoke passed через AMN3 operator script.
- `codex/remote-operation-vps-gate-prep`: отдельный controlled VPS gate для SSH/sync/config/runtime write surfaces.
- `Route/Auth Binding`, `Scoped API Token Lifecycle`, `Secret Inventory`, `Public Config Policy`, `Backup/Import Policy`: обязательные baselines перед дальнейшим route expansion.
- `/clients` write CRUD, API `config:read`, public config delivery, backup/import/reboot и public docs/metrics остаются заблокированы до отдельного решения.
- `Domain Zone Exclusion Policy` и 2FA отложены до закрытия текущих API/VPS safety gates.
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

Текущее фактическое состояние Local Agent в `Amneziya`:

- first slice foundation merged into `codex-vps-test-prep` via PR #2;
- production wiring merged via PR #3;
- included in baseline `91aeb3e`;
- disabled by default;
- default bind `127.0.0.1`;
- hash-only token settings and CLI helper;
- read-only runtime/protocol endpoints;
- LocalCommandRuntimeAdapter for read-only runtime detection;
- example systemd unit and VPS smoke runbook were created in the production-wiring workstream.

Историческая review-заметка про brittle 401/403 text matching закрыта typed local agent auth errors.

Открытые вопросы перед расширением Local Agent:

- какой runtime state безопасно читать без Docker socket;
- как минимально детектить AmneziaWG, AmneziaWG 2.0 и Xray.
- как унифицировать audit sink с production admin actions;
- как описать clients/configs/backup/reboot как blocked routes до policy gates.

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

Текущий режим coordination: AMN3 принял состояние после live VPS stage, local-only transfer slices, VPS install package и активной read-only API ветки.

1. Current production/API-web head is `7764ae7`; `294803e` remains historical API/web-panel gate evidence.
2. Remote-operation VPS gate branch уже обновлена поверх `294803e`: `codex/remote-operation-vps-gate-prep` at `7281254`.
3. Для новых API routes начинать с отдельного route/secret/remote-write gate, не с копирования upstream code.
4. Controlled real VPS verification gate для `codex/remote-operation-vps-gate-prep` держать отдельным gate для SSH/sync/config/runtime-changing routes.
5. Для coordination-чата держать правило: любая новая идея сначала попадает в очередь с verdict, а не сразу в implementation.

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
