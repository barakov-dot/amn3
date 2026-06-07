# Переезд в новый чат: Amneziya / amn2

Документ нужен, чтобы новый чат продолжал текущий проект без перечитывания длинной истории. Не начинать с нуля: открыть ту же папку, проверить ветку и продолжить от текущей карты фаз.

## 1. Точка Правды

```text
Локальная папка: C:\Users\SooL\Documents\Amneziya
GitHub: https://github.com/barakov-dot/amn2.git
Remote для production code: amn2
Рабочая ветка: codex-vps-test-prep
Последний VPS source overlay head: c92bd1a Bind web admin systemd to loopback
Последний VPS smoke status: pass, 2026-06-07 18:21 UTC
Предыдущий source overlay head: 42ffa65 Record git checkout smoke status
Controlled-prod decision: controlled-prod-ready for source overlay c92bd1a
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
- docs/AMN2_PRODUCTION_LAUNCH_GATE.ru.md
- docs/AMN2_C92_SOURCE_OVERLAY_ALIGNMENT.ru.md
- docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
- docs/API_VPS_SMOKE_EVIDENCE.ru.md
- docs/VPS_RETEST_PROTOCOL.ru.md
- docs/PRODUCTION_VPS_CHECKLIST.ru.md
- docs/LOCAL_AGENT.ru.md
- docs/AMN2_VPS_SMOKE_62FF184_RUNBOOK.ru.md

Текущий статус: source overlay `/opt/amn2` промотирован до `c92bd1a` через safe update kit, runtime сохранен (`data/`, `.env`, `servers.yml`, `venv/`), `VPS_APPLY_ENABLED=false`. Read-only API smoke на loopback `127.0.0.1:3040` прошел: `server_db_sync`, API readiness, auth, listener и audit `passed`. Web/admin systemd template подтвержден как loopback-only: `web serve --host 127.0.0.1 --port 3030`. Web/admin доступ утвержден через HTTPS reverse proxy, при этом порт API `3040` наружу не выставляется. Итоговый статус: `controlled-prod-ready` для source overlay `c92bd1a`.

Последний operator launch evidence после этого показал, что фактически работающий `/opt/amn2` в той shell-сессии все еще возвращал `.amn2_source_overlay_commit = 42ffa65`. На нем прошли backup create/verify, bot check, preflight, dry-run, API smoke 6/6, web login `200`, listeners `127.0.0.1:3030` и `127.0.0.1:3040`. Это подтверждает working runtime для `42ffa65`, но не закрывает текущий `c92bd1a` gate. Safe summary записан в `docs/API_VPS_SMOKE_EVIDENCE.ru.md` в разделе `Production Launch Gate Attempt: 2026-06-07 / 42ffa65`.

Следом source overlay был выровнен до `c92bd1a`: kit/source checksum OK, `source_update_status=passed`, `.amn2_source_overlay_commit=c92bd1a`, runtime preserved, backup create/verify прошел, preflight/dry-run прошли, API smoke 6/6 прошел. Manual web loopback check тоже прошел: старый ручной listener остановлен, новый web process поднялся на `127.0.0.1:3030`, `/login` вернул `web_login_http=200`, после cleanup listener остановлен. На текущем VPS постоянный systemd service не запускаем: этот сервер используется для ручной проверки, а service deployment переносится на другой целевой сервер.

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
c92bd1a Bind web admin systemd to loopback
42ffa65 Record git checkout smoke status
977ff2b Add VPS smoke runbook for status head
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
- Local Agent runtime summary mapper included in VPS-smoked source overlay.
- API controller-facing Local Agent runtime summary route: `/api/local-agent/runtime/summary`.
- Safe API smoke cycle, controlled-prod status visibility and loopback web-admin systemd template are included in VPS-smoked source overlay `c92bd1a`.

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
source overlay: c92bd1a Bind web admin systemd to loopback
workspace: /opt/amn2
server: local
api bind: 127.0.0.1:3040
api/auth/listener/audit: passed
web systemd template: 127.0.0.1:3030 loopback-only
status: controlled-prod-ready for source overlay c92bd1a
```

Deployment caveat:

```text
public API 3040 exposure: blocked
web/admin access: HTTPS reverse proxy approved
VPS_APPLY_ENABLED default: false
```

## 7. Главные Документы

- `docs/PROJECT_PHASE_MAP.ru.md`
- `docs/AMN2_PRODUCTION_LAUNCH_GATE.ru.md`
- `docs/AMN2_C92_SOURCE_OVERLAY_ALIGNMENT.ru.md`
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

Для будущего рабочего сервера пройти `docs/AMN2_PRODUCTION_LAUNCH_GATE.ru.md`: backup create/verify, loopback API smoke, manual web check, затем bot/web systemd и reverse proxy только на целевом сервере. На текущем validation VPS service deployment deferred.

Если VPS при проверке показывает `.amn2_source_overlay_commit = 42ffa65`, сначала выровнять source overlay до `c92bd1a` или явно подтвердить, что выбран historical `42ffa65` runtime. Не объявлять `c92bd1a` production gate закрытым по evidence от `42ffa65`.

Для выравнивания есть отдельная инструкция: `docs/AMN2_C92_SOURCE_OVERLAY_ALIGNMENT.ru.md`.

Текущий ближайший шаг после alignment: manual web check на этом VPS уже выполнен и принят. Systemd/service deployment делать позже на целевом сервере; здесь можно переходить к фиксации evidence и выбору следующего read-only controller slice.

Если VPS сейчас не трогаем: основной чат может доработать read-only controller UX и status visibility вокруг `/api/integration/status` и `/api/local-agent/runtime/summary`, но не начинать broad write API, config delivery, backup/import или Local Agent mutations без отдельного design/plan/live-gate решения.

Следующий шаг: продолжать следующий read-only controller slice или готовить отдельный design/live gate. Broad write API, config delivery, backup/import и Local Agent mutations не начинать без отдельного design/live gate.
