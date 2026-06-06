# AMN2 Project Phase Map

Дата: 2026-06-06.

Назначение: текущая карта готовых фаз `amn2` и переносимых правил для будущих API, Local Agent, hybrid и skill-направлений. Документ не открывает новые routes и не разрешает live VPS mutation.

## Точка Правды

```text
production repo: C:\Users\SooL\Documents\Amneziya
remote: https://github.com/barakov-dot/amn2.git
branch: codex-vps-test-prep
current head: c8a6363 Add Local Agent runtime summary mapper
last VPS-smoked head: 32d01fd Update integration status for controlled prod
lab repo: C:\Users\SooL\Documents\VPS-OPS-LAB
lab branch: master
```

`VPS-OPS-LAB` хранит research, runbooks, packages и evidence. Production code остается в `amn2`.

## Готовые Фазы

### 1. Product Foundation

Готово: Python package, settings, SQLite, encrypted secrets, redaction, backup/restore, Telegram bot, AmneziaWG config generation, QR, IPAM and access service.

Переносимое правило: `APP_SECRET_KEY` нельзя менять после запуска; `.conf`, QR, `vpn://`, private key и PSK всегда secret-bearing.

### 2. Web Admin And Operator UX

Готово: web login/session, users/devices/servers/orders/logs/settings, config templates, email verification/recovery, disabled devices, API readiness, API tokens and integration status pages.

Переносимое правило: operator-first UI показывает readiness/status до mutation; dangerous actions требуют confirmation и понятного recovery context.

### 3. Verified Live VPS Baseline

Готово и подтверждено: approve создает рабочий peer, config подключается, peer sync подтверждает live state, external Amnezia-created peers не удаляются автоматически, missing local device add, disable/enable and selective delete work on real VPS.

Переносимое правило: новый live retest нужен при изменениях peer apply/revoke, config templates/defaults, IP allocation, sync classification, Docker write/restart behavior.

### 4. Read-only API Shell

Готово: scoped token model, `/api/servers`, `/api/servers/{server_name}/summary`, `/api/metrics/summary`, `/api/users/summary`, `/api/integration/status`, API smoke CLI, audit and forbidden marker checks.

Переносимое правило: API расширять read-only-first, aggregate-only, scoped, audited and loopback-first. `config:read`, write scopes and public exposure stay gated.

### 5. Remote Operation Gate

Готово: operation metadata, dry-run preview, partial failure model, PSK via stdin, safe audit metadata, Phase 1 dry-run gate and Phase 2 single disposable peer live apply/sync/revoke/sync evidence.

Переносимое правило: `dry-run-only-pass` не равен broad write permission. `verified-live` покрывает только конкретную operation/evidence scope.

### 6. Local Agent Foundation

Готово: read-only `/agent/health`, `/agent/version`, `/agent/runtime`, `/agent/protocols`, hash-only bearer token, explicit scopes, audit, disabled public docs/openapi.

Переносимое правило: Local Agent является privileged runtime adapter. Не публиковать наружу и не добавлять `/agent/clients`, `/agent/configs`, backup/restore/reboot без отдельного policy/secret/audit/live gate.

### 7. Local Agent Runtime Summary

Готово: `app/agent/runtime_summary.py` строит controller-safe summary без server name, container name, interface, config path, stdout/stderr, keys, PSK, traffic or client config details.

Переносимое правило: controller-facing runtime summaries должны быть safe-by-construction и явно маркировать `write_enabled != False` как unsafe.

### 8. Packaging And Evidence

Готово: AMN3 update+smoke packages, source zip, SHA256, package manifests, smoke evidence and controlled-prod runbooks.

Переносимое правило: любой VPS-ready slice получает package, checksum, expected commit, update path, smoke path, rollback/recovery note and no-secret evidence.

## Статусы

| Статус | Что означает | Что не означает |
| --- | --- | --- |
| `local-gate-complete` | Локальные тесты/контракт пройдены без VPS writes | Можно менять production VPS без gate |
| `api-smoke-passed` | Read-only loopback API проверен на VPS | Разрешены write routes или public exposure |
| `dry-run-only-pass` | Remote-operation dry-run/read-only gate пройден | Live apply/revoke подтверждены |
| `verified-live` | Конкретная live mutation прошла с evidence | Можно расширять другие destructive surfaces |
| `controlled-prod-ready` | Operator checklist закрыт без stop conditions | Разрешен broad public SaaS mode |

## Заблокировано До Отдельных Gates

- `/api/clients` write CRUD;
- API `config:read`;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- restore/import apply;
- public docs/metrics;
- detailed per-peer/client metrics;
- Docker manager implementation;
- attach existing server auto-reconcile;
- domain exclusions;
- web-admin 2FA.

## Правила Для Следующих Доработок

1. Сначала policy/binding/secret classification, потом route.
2. Сначала local tests, потом package, потом read-only smoke, потом live gate if needed.
3. Любая write operation получает dry-run, explicit confirmation, audit, rollback and recovery story.
4. Evidence не содержит raw token/header/hash/config/private key/PSK/QR/vpn URI.
5. Upstream projects дают идеи и requirements, но код не копируется.
6. Для hybrid продукта сохранять operator-first, status-first and read-only-first архитектуру.

## Следующий Рекомендуемый Срез

Ближайшая безопасная работа после этой карты: синхронизировать controlled-prod docs and evidence, затем выбрать read-only controller-facing slice. Не начинать broad write API, public config delivery, backup/import или Local Agent mutations без отдельного design/plan/live-gate решения.
