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
- `docs/LOCAL_AGENT_VPS_SMOKE_RUNBOOK.ru.md` - полный VPS smoke runbook.
- `docs/LOCAL_AGENT.ru.md` - архитектура Local Agent.
- `docs/PRODUCTION_VPS_CHECKLIST.ru.md` - общий production checklist.
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
4. Уточнять policy/scopes/audit/dry-run контракты в плане первого write API slice.
5. Писать только неинвазивные тесты, которые подтверждают, что write routes пока недоступны по умолчанию.

До VPS smoke не включать write routes, не добавлять реальные mutation endpoints и не делать Local Agent публичным.

### Только после реального VPS smoke

Дальше идем только после проверки на живом сервере:

1. На VPS пройти `docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md`.
2. Убедиться, что web admin видит Local Agent без raw token.
3. Зафиксировать результат smoke в docs или commit message.
4. После успешного smoke начинать первый write API slice.

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
