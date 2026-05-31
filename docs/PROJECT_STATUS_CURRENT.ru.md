# Текущее состояние проекта

Дата: 2026-06-01.

Этот snapshot фиксирует текущее состояние после verified live VPS cycle, серии local-only hardening slices в `amn2` и синхронизации AMN3 с GitHub.

## Что учтено при обновлении

Проанализированы локальные Codex-сессии проекта с `VPS-OPS-LAB` и `Amneziya`, включая:

- ранний Amneziya planning/provisioning чат;
- `Подготовка запуска на VPS`;
- `VPS-тест Amneziya`;
- `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`;
- `VPN Ops Lab - KYORESUAS-API`;
- task/review-чаты Local Amnezia Agent first slice;
- task/review-чаты Local Agent production wiring;
- live VPS completion / verified tag / migration-to-lab чаты;
- Route/Auth/Operation Policy Matrix task/review;
- Redaction Coverage task/review;
- Config Delivery Integrity evidence;
- Public Token Safety task/review;
- Remote Operation contract / partial-failure / dry-run-audit slices;
- Local Agent hardening task/review;
- Web Panel Safe Improvements task/review;
- текущий `MAIN - VPN Ops Lab` coordination chat.

Нерелевантные сессии из других рабочих папок, например `ISP-NEW`, не включались в состояние этого проекта.

## AMN3 / VPS Ops Lab

Локальный checkout:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

GitHub remote:

```text
https://github.com/barakov-dot/amn3.git
```

Текущая ветка:

```text
master
```

Committed head lab before this status update:

```text
1a00be8 Record web panel safety slice
```

`master` синхронизирован с `origin/master`.

AMN3 является coordination/knowledge repo: research, design specs, implementation plans, transfer notes и gate для переноса идей в production.

Production-код остается в `amn2`.

## Production baseline: `amn2`

Локальный checkout:

```text
C:\Users\SooL\Documents\Amneziya
```

GitHub remote:

```text
https://github.com/barakov-dot/amn2.git
```

Текущая production-ветка:

```text
codex-vps-test-prep
```

Актуальный head:

```text
22dfc37 Clarify web panel operation gates
```

Текущий local worktree `Amneziya` после web-panel safe-improvements commit должен оставаться чистым и синхронизированным с `amn2/codex-vps-test-prep`.

Последний web-panel slice добавил operator wording для secret-bearing delivery artifacts, read-only server actions и VPS write gate confirmations без изменения write behavior.

Проверенная stable-точка live VPS cycle:

```text
vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Основной handoff production-репозитория:

```text
docs/NEXT_CHAT_HANDOFF.ru.md
```

Последняя локальная проверка `amn2`:

```text
536 passed, 1 warning
```

Ожидаемое предупреждение: `StarletteDeprecationWarning` от `httpx` / `starlette.testclient`.

## Verified live VPS cycle

На живом VPS подтверждено:

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

Это закрывает прежний пункт `live VPS retest` как основной риск. Новый retest нужен только после изменений в apply/revoke/config/sync логике.

## Что продолжаем теперь

API-readiness audit выполнен в AMN3:

```text
research/amn2/api-readiness-audit-after-live-baseline.md
```

Основной порядок слияния API, web panel и operations зафиксирован:

```text
docs/AMN2_MAIN_MERGE_ROADMAP.ru.md
```

Первый выбранный safe slice уже перенесен в `amn2`:

```text
Route/Auth/Operation Policy Matrix for current amn2 surfaces
```

Смысл slice: не добавлять новый production API сразу, а сначала сделать machine-checkable policy/contract для текущих web, bot, Local Agent и remote-operation surfaces: actors, auth, risk class, secret class, audit, idempotency, dry-run/apply, rollback/recovery и live-retest trigger.

Этот slice остался без live VPS calls, без новых config/API/write endpoints и без копирования upstream code.

После него локально выполнены и запушены в `amn2/codex-vps-test-prep` следующие local-only slices:

- Redaction Coverage: `94ad807 Document secret-bearing delivery artifacts`;
- Config Delivery Integrity evidence: verified at `94ad807`;
- Public Token Safety: `dfe27ee Harden public email token safety`;
- Remote Operation state-changing contract / partial-failure / dry-run-audit: local branches and AMN3 evidence recorded, dry-run/audit branch `codex/remote-operation-dry-run-audit` commits `0313857`, `063b6c3`;
- Local Agent Hardening: `c5d7eb6 Harden Local Agent audit contract`;
- Web Panel Safe Improvements: `22dfc37 Clarify web panel operation gates`.

Решение по соседним чатам:

- `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`: широкие research-задачи поставить на паузу; оставить как targeted-input для web-panel UX, config delivery integrity, route taxonomy и dangerous-action patterns.
- `VPN Ops Lab — KYORESUAS-API`: оставить active reference для Local Agent/API architecture; не устанавливать, не копировать и не переносить CRUD/write API до policy/secret/remote-write gates.

## Что не делать первым

Не писать production API сразу.

Не копировать upstream code.

Не трогать live VPS из lab-чата.

Не считать старые заметки `implemented-needs-live-retest` актуальными: они исторические, live baseline уже подтвержден.

## Связанные документы

Главный migration handoff:

```text
docs/NEXT_CHAT_AFTER_AMN2_VPS_LIVE.ru.md
```

API/upstream start:

```text
docs/NEXT_CHAT_KYORESUAS_API.ru.md
research/upstreams/kyoresuas-amnezia-api.md
```

`amn2` transfer context:

```text
research/amn2/README.md
research/amn2/transfer-backlog.md
research/amn2/remote-operations-inventory.md
research/amn2/config-delivery-inventory.md
```

Existing unification design:

```text
docs/superpowers/specs/2026-05-31-amn3-amneziya-unification-design.md
```

## Local Agent baseline status

Local Agent first slice:

```text
status: merged into codex-vps-test-prep via PR #2
commits: 3119ee6, ac2baa8
```

Local Agent production wiring:

```text
status: merged into codex-vps-test-prep via PR #3
head: 8697b60 Document Local Agent production wiring
```

Локальная проверка показала, что эти commits уже содержались в production baseline после `91aeb3e`. Позднее Local Agent получил hardening commit `c5d7eb6`: repository-backed audit sink для allowed read routes, safe `/agent/version` metadata и тесты, что raw bearer token не попадает в audit. Следующий Local Agent slice не должен добавлять clients/configs/write routes; сначала нужны token rotation/revoke design и scoped token policy.

## Рекомендуемый порядок

1. Следующий local-only slice: scoped API tokens design/storage tests, включая token rotation/revoke contract, без новых broad API write routes.
2. Альтернатива после отдельного подтверждения оператора: controlled real VPS verification gate для `codex/remote-operation-dry-run-audit`.
3. До live Docker apply/revoke описать Docker manager: persistent config path, backup, reload/apply semantics и rollback note.
4. Read-only clients/metrics endpoints держать после scoped token/privacy review.
5. Public/self-service config links, domain exclusions и 2FA не возвращать в работу до закрытия текущих safety gates.

## Route/Auth/Operation Policy Matrix Plan

Статус: `implemented-in-amn2-local-commit`.

Новый AMN3 artifact:

```text
docs/superpowers/plans/2026-05-31-amn2-route-auth-operation-policy-matrix.md
```

Production branch:

```text
codex-vps-test-prep
```

Production commit:

```text
d1d9690 Add route auth operation policy matrix
```

Создано в `amn2`:

- `app/security/surface_policy.py`
- `tests/security/test_surface_policy.py`
- `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`

Проверка:

```text
focused policy/agent/server tests: 46 passed
web/bot smoke tests: 85 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Новые API endpoints не добавлялись. Новые write/config delivery flows не включались.

Обновленный порядок:

1. `amn2` commit `d1d9690` запушен в remote branch `codex-vps-test-prep`.
2. Следующий local-only slice выбран и выполнен: redaction coverage.
3. Следующий local-only slice проверен: config delivery integrity.

## Redaction Coverage Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
94ad807 Document secret-bearing delivery artifacts
```

Production commits:

```text
75c235a Expand redaction primitive coverage
fc73929 Add config delivery redaction coverage
f62d5d6 Harden config email audit coverage
eb735e2 Harden remote output redaction coverage
94ad807 Document secret-bearing delivery artifacts
```

Проверка:

```text
focused redaction/security/delivery/remote/docs tests: 61 passed, 1 StarletteDeprecationWarning
full local suite: 528 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не меняет live apply/revoke/config/sync behavior, поэтому VPS gate не нужен.

## Config Delivery Integrity Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head used for verification:

```text
94ad807 Document secret-bearing delivery artifacts
```

Relevant production commits already present in branch:

```text
952cc49 Add config delivery artifact metadata
4b19cd3 Add config delivery utf8 artifact tests
fc73929 Add config delivery redaction coverage
```

Проверка:

```text
tests/bot/test_delivery.py tests/services/test_config_delivery.py tests/vpn/test_config_templates.py -v
result: 16 passed

full local suite at same head: 528 passed, 1 StarletteDeprecationWarning
```

Покрыто: `.conf` UTF-8 bytes, QR payload equality, `vpn://` round-trip, non-ASCII fixture, `client-config-secret` metadata and redaction behavior for text diagnostics.

Live VPS не трогался. Slice не меняет live templates/defaults или apply/sync behavior, поэтому VPS gate не нужен.

## Public Token Safety Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
dfe27ee Harden public email token safety
```

Покрыто:

- `create_email_token` теперь отклоняет `ttl_minutes <= 0`;
- raw token хранится/сравнивается через hash-only contract;
- public verify/recover tokens не взаимозаменяемы по `purpose`;
- expired verify/recover codes отклоняются;
- denial response не возвращает сырой token;
- wrong-purpose/expired tokens не consumed.

Проверка:

```text
tests/services/test_email_tokens.py tests/web/test_email_delivery.py -q --basetemp tmp\pytest-public-token
result: 14 passed, 1 StarletteDeprecationWarning

full local suite:
535 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не меняет peer apply/revoke/config/sync/runtime behavior, поэтому VPS gate не нужен.

## Local Agent Hardening Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
c5d7eb6 Harden Local Agent audit contract
```

Покрыто:

- `agent serve` подключает repository-backed audit sink;
- allowed read routes пишут `local_agent_read` в `admin_actions`;
- audit metadata содержит route, scope, risk class, token id/owner и result без raw bearer token;
- `/agent/version` отдает `runtime_contract_version`, `first_slice_routes` и `write_enabled=false`;
- first-slice boundary остается без `/agent/clients`, `/agent/configs`, backup/restore/reboot и write lifecycle.

Проверка:

```text
RED:
tests/agent/test_api.py::test_health_and_version_return_secret_free_metadata
tests/agent/test_cli.py::test_run_agent_server_records_allowed_read_audit_in_database
result: 2 failed as expected

focused agent/security tests:
64 passed, 1 StarletteDeprecationWarning

full local suite:
536 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice меняет локальный agent audit/version contract и docs, но не делает real agent deployment, controller-to-agent calls, peer apply/revoke/config/sync/runtime writes; VPS gate не нужен.

## Web Panel Safe Improvements Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
22dfc37 Clarify web panel operation gates
```

Покрыто:

- server health action помечен как read-only: stores health status only, no VPS changes;
- peer sync action помечен как read-only compare: does not add or remove peers;
- add missing local device confirmation явно говорит, что это live VPS write и должен идти через VPS gate;
- config templates page помечает real `.conf`, QR и `vpn://` payloads как secret-bearing delivery artifacts;
- user/device dangerous confirmations уточняют local DB status/data changes и VPS write только при `VPS_APPLY_ENABLED=true`.

Проверка:

```text
RED:
tests/web/test_servers.py::test_server_detail_shows_config_health_and_actions
tests/web/test_servers.py::test_server_sync_run_displays_peer_inventory_report
tests/web/test_config_templates.py::test_config_templates_page_lists_versions_placeholders_and_safe_preview
tests/web/test_users.py::test_user_detail_marks_dangerous_actions_with_confirmation
result: 4 failed as expected

GREEN focused slice:
same 4 tests
result: 4 passed, 1 StarletteDeprecationWarning

focused web/security suite:
tests/web/test_servers.py tests/web/test_users.py tests/web/test_config_templates.py tests/web/test_email_delivery.py tests/security/test_surface_policy.py
result: 75 passed, 1 StarletteDeprecationWarning

full local suite:
536 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice меняет UI wording/templates и web tests, но не меняет peer apply/revoke/config/sync/runtime behavior; VPS gate не нужен.

## Remote Operation Dry-run/Audit Slice

Статус: `implemented-pushed-local-gate-complete`.

Production worktree:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-remote-operation-contract-metadata
```

Production branch:

```text
codex/remote-operation-dry-run-audit
```

Production commits:

```text
0313857 Add remote operation dry-run metadata
063b6c3 Document remote operation local gate
```

Покрыто:

- `RemoteOperationRunner.plan()` возвращает `consistency_status=dry-run` для state-changing операций без SSH;
- `OperationPlan.to_safe_metadata()` не публикует command strings и redacts audit/rollback/idempotency metadata;
- `apply-peer` и `revoke-peer` dry-run preview показывает operation ID, risk class, side effects и rollback note без PSK/private config;
- `docs/RUNTIME_REGISTRY.ru.md` и `docs/RUNTIME_REGISTRY.en.md` фиксируют local gate перед real VPS.

Проверка:

```text
focused server/security/web tests: 79 passed, 1 StarletteDeprecationWarning
runtime registry docs tests: 7 passed
full local suite: 522 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice меняет dry-run/audit metadata и документацию; следующий шаг - отдельный controlled real VPS verification gate, начиная с read-only/dry-run подтверждения.

## Local Gate / Live VPS Gate

Новый порядок проверки разделен на два контура.

Локально можно делать:

- policy/inventory-only registry;
- redaction coverage;
- config delivery artifact tests;
- web/bot smoke через TestClient;
- Local Agent read-only/auth/token hardening на fake/local runtime;
- remote operation contracts на fake SSH;
- docs/status/backlog updates.

На real VPS проверяем только после локально зеленого slice, если он меняет:

- peer apply/revoke;
- disable/enable/delete;
- add missing local device;
- remove unknown remote peer;
- peer sync classification;
- config templates/defaults, которые попадут в рабочий client config;
- Docker AmneziaWG write/reload/restart behavior;
- реальный Local Agent deployment или controller-to-agent calls.

Следующий рекомендуемый local-only шаг: scoped API tokens design/storage tests - hash-only token storage, one-time raw token display, scopes, expiry, revoke/rotation and audit metadata без новых broad write endpoints. Отдельная альтернатива после подтверждения оператора: controlled real VPS verification gate для remote-operation dry-run/audit ветки; single test peer apply/revoke выполнять только после отдельного разрешения.
