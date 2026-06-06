# Переезд в новый чат: Amneziya / amn2

Документ нужен, чтобы новый чат продолжал текущий проект без перечитывания длинной истории. Не начинать с нуля: открыть ту же папку, проверить ветку и продолжить от текущей карты фаз.

## 1. Точка Правды

```text
Локальная папка: C:\Users\SooL\Documents\Amneziya
GitHub: https://github.com/barakov-dot/amn2.git
Remote для production code: amn2
Рабочая ветка: codex-vps-test-prep
Последний VPS source overlay head: c8a6363 Add Local Agent runtime summary mapper
Последний VPS smoke status: pass, run_id 20260606T202040Z
Текущий read-only head: 62ff184 Update controlled prod status visibility
Текущий read-only VPS smoke: pass on /opt/amn2-git, checked_routes=6, 2026-06-06 21:41 UTC
Controlled-prod decision: controlled-prod-ready for source overlay c8a6363
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
- docs/AMN2_VPS_SMOKE_62FF184_RUNBOOK.ru.md

Текущий статус: source overlay `c8a6363` прошел read-only API smoke на VPS `/opt/amn2` через loopback `127.0.0.1:3040`, пять read-only routes вернули 200, forbidden markers пустые, auth/listener/audit checks passed. Web/admin доступ утвержден через HTTPS reverse proxy, при этом порт API `3040` наружу не выставляется. Итоговый статус: `controlled-prod-ready` для source overlay `c8a6363`.

Дополнительный read-only gate: head `62ff184` прошел VPS smoke на git-managed checkout `/opt/amn2-git` через `python -m app.cli api smoke-cycle`: `checked_routes=6`, все routes `200`, forbidden markers пустые, временный token отозван автоматически. Это подтверждает read-only API head, но не утверждает, что source overlay `/opt/amn2` уже заменен на `62ff184`.

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
62ff184 Update controlled prod status visibility
465444a Add safe API smoke cycle
8f0be19 Add Local Agent runtime summary API route
c8a6363 Add Local Agent runtime summary mapper
```

## 4. Что Уже Готово

- Telegram bot и web-admin panel для управления AmneziaWG-доступом.
- Verified live VPS cycle: approve, working config, sync, disable/enable and selective delete.
- Docker runtime apply/revoke behavior and restart boundary.
- Route/Auth/Operation policy matrix and binding tests.
- Redaction, secret inventory, API token lifecycle and SSH host key verifier.
- Read-only scoped `/api/*` route shell with audit, smoke-check and safe smoke-cycle.
- API readiness, API tokens and integration status web pages.
- Remote-operation dry-run metadata, partial failure model and PSK stdin path.
- Phase 2 single disposable peer live apply/sync/revoke/sync evidence.
- Local Agent first slice: read-only `/agent/*`, hash-only token and audit.
- Local Agent runtime summary mapper included in VPS-smoked source overlay `c8a6363`.
- API controller-facing Local Agent runtime summary route: `/api/local-agent/runtime/summary`.
- Safe API smoke cycle and controlled-prod status visibility are included in head `62ff184`; git-checkout VPS smoke passed with 6 routes, source overlay promotion remains a separate step.

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
source overlay: c8a6363 Add Local Agent runtime summary mapper
local head: 62ff184 Update controlled prod status visibility
latest git-checkout smoke workspace: /opt/amn2-git
server: local
api bind: 127.0.0.1:3040
checked_routes: 6
route status codes: 200
forbidden_markers: []
status: 62ff184 read-only git-checkout VPS smoke passed
```

Deployment caveat:

```text
source overlay c8a6363: controlled-prod-ready
head 62ff184: VPS smoke passed on /opt/amn2-git, source overlay promotion still separate
public API 3040 exposure: blocked
web/admin access: HTTPS reverse proxy approved
VPS_APPLY_ENABLED default: false
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

Если VPS сейчас не трогаем: основной чат может доработать read-only controller UX и status visibility вокруг `/api/integration/status` и `/api/local-agent/runtime/summary`, но не начинать broad write API, config delivery, backup/import или Local Agent mutations без отдельного design/plan/live-gate решения.

Следующий шаг: либо промотировать `62ff184` через safe source overlay update flow и повторно подтвердить `/opt/amn2`, либо продолжать следующий read-only controller slice. Broad write API, config delivery, backup/import и Local Agent mutations не начинать без отдельного design/live gate.
