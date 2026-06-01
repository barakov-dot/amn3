# AMN3 Next Chat Handoff

Этот handoff нужен, чтобы следующий чат внутри VPS Ops Lab продолжил текущую
линию AMN3 без возврата к старому `amn2` контексту.

## 1. Текущая цель

Собираем собственный качественный продукт вокруг Amneziya:

- web admin и Telegram bot управляют пользователями и устройствами;
- Local Agent стоит на VPS Amneziya и дает read-only runtime/status API;
- следующий этап после VPS smoke - первый безопасный write API для управления
  users/devices/peers;
- код чужих проектов не копируем, используем их только как источник анализа и
  продуктовых решений.

## 2. Git и рабочая папка

Локальный worktree:

```text
C:\Users\SooL\Documents\Amneziya\.codex_deps\worktrees\local-agent-production-wiring
```

Целевой приватный GitHub repository:

```text
https://github.com/barakov-dot/amn3.git
```

Интеграционная ветка:

```text
codex/local-agent-production-wiring
```

Baseline, который уже содержит Local Agent в web admin:

```text
fdc471a Show Local Agent health in web admin
```

Перед работой проверить:

```powershell
git status --short --branch
git log -5 --oneline --decorate
git remote -v
```

Если ветка еще не опубликована в `amn3`, использовать команды из
`docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md`.

## 3. Что уже сделано в текущей ветке

- hardened runtime detection для Local Agent;
- безопасные defaults и env hygiene;
- systemd template для `amneziya-agent`;
- diagnostics snapshot с redaction;
- VPS smoke runbook;
- read-only Local Agent client;
- CLI `agent probe`;
- web admin блок `Local Agent` на server detail/server health;
- локальный contract layer будущего write API без endpoints: `app/agent/write_contracts.py`;
- safety tests для contract layer и заблокированных write routes: `tests/agent/test_write_contracts.py`;
- controller settings:
  - `LOCAL_AGENT_CONTROLLER_ENABLED`;
  - `LOCAL_AGENT_CONTROLLER_BASE_URL`;
  - `LOCAL_AGENT_CONTROLLER_TOKEN_PATH`.

## 4. Главные документы

- `docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md` - короткий маршрут для
  текущего переноса AMN3 на VPS.
- `docs/AMN3_VPS_TEST_PACKET.ru.md` - короткий пакет для соседнего чата `Переводим AMN на API`,
  где готовится реальный VPS smoke.
- `docs/AMN3_LOCAL_RELEASE_GATE.ru.md` - локальный gate перед VPS: write routes закрыты,
  `LOCAL_AGENT_WRITE_ENABLED=false`, read-only token без `agent:clients:write`.
- `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md` - карта перехода после `go` в VPS smoke:
  evidence intake -> write policy -> endpoints -> controller client -> web admin -> first mutation test.
- `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md` - шаблон отчета после реального VPS smoke: commit, runtime,
  Local Agent, web admin, degraded reasons, rollback и Go / no-go.
- `docs/LOCAL_AGENT_VPS_SMOKE_RUNBOOK.ru.md` - полный VPS smoke runbook.
- `docs/LOCAL_AGENT.ru.md` - архитектура Local Agent.
- `docs/PRODUCTION_VPS_CHECKLIST.ru.md` - общий production checklist.
- `docs/AMN3_KYORESUAS_API_ANALYSIS.ru.md` - анализ `kyoresuas/amnezia-api` как источника идей для AMN3 user/client API без копирования кода.
- `docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md` - локальная матрица future `agent:clients:write` операций, scopes и error contracts без включения routes.
- `docs/AMN3_WRITE_API_UX_FLOW.ru.md` - UX/API flow первого write-среза для web admin, Telegram bot и CLI:
  dry-run -> confirmation -> apply/revoke -> audit -> rollback.
- `docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md` - audit contract для будущих write operations: actor surfaces,
  result states, redaction rules и storage note.
- `docs/AMN3_WRITE_AUDIT_STORAGE_DECISION.ru.md` - ADR по хранению future write audit events:
  authoritative SQLite table `local_agent_write_audit_events`, JSONL только fallback/export.
- `docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md` - future settings contract для
  `LOCAL_AGENT_WRITE_ENABLED=true`, отдельного write token set и запрета `agent:clients:write` в read-only token.
- `docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md` - code-ready TDD-план
  future settings/config slice для dedicated write token set после `GO-1`.
- `docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md` - code-ready TDD-план
  будущей таблицы `local_agent_write_audit_events` и repository methods после `GO-1`.
- `docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md` - code-ready TDD-план
  Local Agent runtime adapter для peer dry-run/apply/revoke после `GO-1`.
- `docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md` - code-ready TDD-план
  guarded `/agent/clients*` endpoints после `GO-1`.
- `docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md` - code-ready TDD-план
  controller-side Local Agent write client для web admin/CLI после `GO-1`.
- `docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md` - contract для dry-run reference, confirmation nonce,
  expiry и `preflight_required`.
- `docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md` - модель `user_id` / `device_id` / `client_id` /
  `peer_public_key` для будущего write API без открытия mutation routes.
- `docs/WEB_PANEL_AND_BOT_SETUP.ru.md` - web/bot запуск и эксплуатация.
- `docs/VPS_RETEST_PROTOCOL.ru.md` - повторяемый VPS retest.
- `docs/VPS_LOG_COLLECTION.ru.md` - сбор логов и диагностики.

## 5. Как проверять локально

В этом окружении tests запускаются через bundled Python и `.codex_deps`:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/deploy/test_runtime_registry.py -v
```

Focused проверка Local Agent contracts:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_write_contracts.py tests/agent/test_policy.py -v
```

Короткая команда, которую ищут docs tests:

```powershell
python -m pytest tests/deploy/test_runtime_registry.py
```

Перед завершением любого slice:

```powershell
git diff --check
git status --short --branch
```

## 6. Ближайший порядок работы

### Локально до реального VPS smoke

Можно продолжать без VPS:

1. Опубликовать или доставить ветку `codex/local-agent-production-wiring` в `barakov-dot/amn3`, когда GitHub credentials будут готовы.
2. Держать актуальными `docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md` и этот handoff.
3. Анализировать идеи `kyoresuas/amnezia-api` для user API без копирования кода.
4. Использовать `docs/AMN3_KYORESUAS_API_ANALYSIS.ru.md` для уточнения policy/scopes/audit/dry-run контрактов в плане первого write API slice.
5. Держать `docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md` синхронизированным с `app/agent/write_policy_matrix.py`.
6. Держать `docs/AMN3_WRITE_API_UX_FLOW.ru.md` синхронизированным с policy matrix и будущими surface flows.
7. Держать `docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md` синхронизированным с `app/agent/write_audit.py`.
8. Держать `docs/AMN3_WRITE_AUDIT_STORAGE_DECISION.ru.md` синхронизированным с audit model и post-VPS map.
9. Держать `docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md` синхронизированным с settings/config tests.
10. Держать `docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md` готовым к исполнению после `GO-1`.
11. Держать `docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md` готовым к исполнению после `GO-1`.
12. Держать `docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md` готовым к исполнению после `GO-1`.
13. Держать `docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md` готовым к исполнению после `GO-1`.
14. Держать `docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md` готовым к исполнению после `GO-1`.
15. Держать `docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md` синхронизированным с `app/agent/write_confirmation.py`.
16. Держать `docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md` синхронизированным с UX, audit и preflight contracts.
17. Перед передачей на VPS проходить `docs/AMN3_LOCAL_RELEASE_GATE.ru.md`.
18. Писать только неинвазивные тесты, которые подтверждают, что write routes пока недоступны по умолчанию.

До VPS smoke не включать write routes, не добавлять реальные mutation endpoints и не делать Local Agent публичным.

### Только после реального VPS smoke

Дальше идем только после проверки на живом сервере:

1. Для соседнего чата использовать `docs/AMN3_VPS_TEST_PACKET.ru.md`.
2. На VPS пройти `docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md`.
3. Заполнить `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`.
4. При `go` идти по `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`.
5. Убедиться, что web admin видит Local Agent без raw token.
6. Зафиксировать результат smoke в docs или commit message.
7. После успешного smoke начинать первый write API slice.

План первого write API slice: `docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md`.

## 7. Правила write API

Write API делаем только после зеленого read-only smoke.

Обязательные элементы первого write slice:

- route policy matrix;
- explicit scopes;
- audit log на каждую операцию;
- dry-run/preflight перед mutation;
- redaction секретов;
- rollback path;
- тесты на запрет secret leakage.

Первый write API должен быть узким: create/disable/enable device или peer, без
массовых операций и без публичного root API.
