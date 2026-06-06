# Переезд в новый чат: Amneziya / amn2

Документ нужен, чтобы новый чат продолжал текущий проект без перечитывания длинной истории. Не начинать с нуля: открыть ту же папку, проверить ветку и продолжить от текущей карты фаз.

## 1. Точка Правды

```text
Локальная папка: C:\Users\SooL\Documents\Amneziya
GitHub: https://github.com/barakov-dot/amn2.git
Remote для production code: amn2
Рабочая ветка: codex-vps-test-prep
Последний VPS-smoked app-code head: 64a6750 Document controlled prod readiness
Последний VPS smoke status: api-smoke-passed with token-hygiene exception
Controlled-prod decision: defer-prod until previous chat-exposed token is revoked or expired
Стабильный verified live VPS tag: vps-live-cycle-verified -> d6eda20
Lab/coordination repo: C:\Users\SooL\Documents\VPS-OPS-LAB
```

`origin` в этом checkout может указывать на AMN3/lab. Production push делать в `amn2`.

## 2. Первый Текст Для Нового Чата

```text
Продолжаем проект Amneziya / amn2.

Репозиторий: https://github.com/barakov-dot/amn2.git
Ветка: codex-vps-test-prep
Локальная папка: C:\Users\SooL\Documents\Amneziya
Стартовые документы:
- docs/NEXT_CHAT_HANDOFF.ru.md
- docs/PROJECT_PHASE_MAP.ru.md
- docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
- docs/API_VPS_SMOKE_EVIDENCE.ru.md
- docs/VPS_RETEST_PROTOCOL.ru.md
- docs/PRODUCTION_VPS_CHECKLIST.ru.md
- docs/LOCAL_AGENT.ru.md

Текущий статус: app-code baseline `64a6750` прошел read-only API smoke на VPS `/opt/amn2-git` через loopback `127.0.0.1:3040`, пять read-only routes вернули 200, forbidden markers пустые. Новый smoke token отозван. Предыдущий raw token был опубликован в чате и по решению оператора пока не отозван; поэтому итоговый статус `api-smoke-passed`, но не полный `controlled-prod-ready`.

Следующий локальный срез после этого evidence: `/api/local-agent/runtime/summary` добавлен как controller-facing read-only route под `server:read`. Он не дергает Local Agent по сети и не выдает host/port/token/container/interface/config path. Следующий VPS smoke для текущего head должен ожидать `checked_routes: 6`.

Цель следующего этапа: не открывать broad write API, а закрыть controlled-prod readiness или выбрать следующий read-only controller-facing slice.
```

## 3. Быстрая Проверка

```powershell
cd C:\Users\SooL\Documents\Amneziya
git status --short --branch
git log -8 --oneline --decorate
git remote -v
```

Ожидаемая ветка:

```text
## codex-vps-test-prep...amn2/codex-vps-test-prep
```

В `git log -8` должен быть текущий documentation/evidence commit поверх app-code baseline:

```text
64a6750 Document controlled prod readiness
```

## 4. Что Уже Готово

- Telegram bot и web-admin panel для управления AmneziaWG-доступом.
- Verified live VPS cycle: approve, working config, sync, disable/enable and selective delete.
- Docker runtime apply/revoke behavior and restart boundary.
- Route/Auth/Operation policy matrix and binding tests.
- Redaction, secret inventory, API token lifecycle and SSH host key verifier.
- Read-only scoped `/api/*` route shell with audit and smoke-check.
- API readiness, API tokens and integration status web pages.
- Remote-operation dry-run metadata, partial failure model and PSK stdin path.
- Phase 2 single disposable peer live apply/sync/revoke/sync evidence.
- Local Agent first slice: read-only `/agent/*`, hash-only token and audit.
- Local Agent runtime summary mapper included in VPS-smoked app-code baseline `64a6750`.
- API controller-facing Local Agent runtime summary route: `/api/local-agent/runtime/summary`.

## 5. Что Не Открыто

До отдельных gates остаются заблокированы:

- `/api/clients` write CRUD;
- API `config:read`;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- public web/API exposure;
- broad live peer mutation API;
- full logs or secret-bearing evidence in GitHub/chat.

## 6. VPS Статус

Последний VPS-smoked app-code baseline:

```text
64a6750 Document controlled prod readiness
workspace: /opt/amn2-git
server: local
api bind: 127.0.0.1:3040
checked_routes: 5
route status codes: 200
forbidden_markers: []
status: api-smoke-passed
```

Readiness caveat:

```text
previous chat-exposed token: not revoked by operator decision
reported expiry: 2026-06-13T20:37:39+00:00
controlled-prod decision: defer-prod until token is revoked or expired
```

## 7. Главные Документы

- `docs/PROJECT_PHASE_MAP.ru.md`
- `docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md`
- `docs/API_TOKEN_POLICY.ru.md`
- `docs/API_VPS_SMOKE_EVIDENCE.ru.md`
- `docs/LOCAL_AGENT.ru.md`
- `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`
- `docs/RUNTIME_REGISTRY.ru.md`
- `docs/VPS_RETEST_PROTOCOL.ru.md`
- `docs/PRODUCTION_VPS_CHECKLIST.ru.md`
- `docs/WEB_PANEL_AND_BOT_SETUP.ru.md`

## 8. Рекомендуемый Следующий Шаг

Если оператор готов закрыть controlled-prod readiness: зафиксировать revoke/expiry предыдущего chat-exposed token и обновить `docs/API_VPS_SMOKE_EVIDENCE.ru.md`.

Если VPS сейчас не трогаем: основной чат может доработать read-only controller UX вокруг `/api/local-agent/runtime/summary`, но не начинать broad write API, config delivery, backup/import или Local Agent mutations без отдельного design/plan/live-gate решения.
