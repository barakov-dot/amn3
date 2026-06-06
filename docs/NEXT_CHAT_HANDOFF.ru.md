# Переезд в новый чат: Amneziya / amn2

Документ нужен, чтобы новый чат продолжал текущий проект без перечитывания длинной истории. Не начинать с нуля: открыть ту же папку, проверить ветку и продолжить от текущей карты фаз.

## 1. Точка Правды

```text
Локальная папка: C:\Users\SooL\Documents\Amneziya
GitHub: https://github.com/barakov-dot/amn2.git
Remote для production code: amn2
Рабочая ветка: codex-vps-test-prep
Текущий head: c8a6363 Add Local Agent runtime summary mapper
Последний VPS-smoked head: 32d01fd Update integration status for controlled prod
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

Текущий статус: read-only API/web integration уже VPS-smoked на 32d01fd; текущий head c8a6363 добавляет local-only Local Agent runtime summary mapper и package-ready, но сам head еще не является VPS-smoked baseline.

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

Верхний commit на момент этого handoff:

```text
c8a6363 Add Local Agent runtime summary mapper
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
- Local Agent runtime summary mapper at `c8a6363`.

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

Последний VPS-smoked baseline:

```text
32d01fd Update integration status for controlled prod
run_id: 20260606T185114Z
status: read-only VPS smoke pass
```

Текущий `c8a6363`:

```text
status: package-ready-not-vps-smoked
scope: local-only runtime summary mapper
VPS smoke required only if accepting c8a6363 as new VPS source/package baseline
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

Если оператор готов к VPS-проверке: выполнить read-only update/smoke для `c8a6363` package и затем controlled-prod readiness decision по `docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md`.

Если VPS сейчас не трогаем: следующий инженерный slice должен оставаться read-only, policy-bound and no-secret. Не начинать broad write API, config delivery, backup/import или Local Agent mutations без отдельного design/plan/live-gate решения.
