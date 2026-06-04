# Текущее состояние проекта

Дата: 2026-06-02.

Этот snapshot фиксирует текущее состояние после verified live VPS cycle, серии local-only hardening slices в `amn2`, сборки VPS install package и перехода API-направления в активную ветку `codex/read-only-api-route-shell`.

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
- Scoped API Token Storage task/review;
- Route/Auth Binding Tests, API Token Lifecycle Gate and SSH Host Key Verifier task/review;
- VPS install package / installer fallback fix;
- KYORESUAS API priority plan и последующую ветку read-only API route shell;
- pre-VPS matrix comments from `codex/local-agent-production-wiring`;
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

AMN3 package state reviewed in this status refresh:

```text
master; verify exact current head with git log -1 after package publish
```

`master` должен быть синхронизирован с `origin/master` после каждого package publish.

Последние AMN3 pushes, учтенные в этом snapshot:

```text
25e02e9 Add VPS install package
87da41d Fix VPS installer user creation fallback
7fc3aee Set KYORESUAS API integration priority
8b4cc81 Refresh project coordination state
2b845cb Make API smoke skip server preflight by default
```

Актуальный install/update package для стабильного `amn2` baseline `5f12736`:

```text
dist/amn2-vps-install-5f12736.zip
sha256: CB2FBA547FD5DC50A94851BC7154D775FBD4977F09091E0F9BAE52F2DC9C2F25
dist/amn2-vps-update-and-smoke-kit-5f12736.zip
sha256: 557C3B0C589BE98E1F5780DBBF289ACB3EB350F468BF369A6672B2A10DB2BB3C
```

Package hotfix note: install/update packages include `amn2_api_loopback_smoke.sh` version `2026-06-04.1`; the script performs DB-only server config sync from `servers.yml` into SQLite before route smoke and keeps `server preflight` as a separate SSH/server dry-run gate, not the API smoke path.

Дополнительный соседний AMN3 push, который не слит в `master`, но учтен в этом snapshot:

```text
origin/codex/local-agent-production-wiring -> d5f30c6 Clarify pre-VPS matrix baseline
artifact: docs/AMN3_PRE_VPS_LOCAL_STATUS_MATRIX.ru.md
status: branch-only pre-VPS matrix; использовать как комментарий/сверку, не как production gate
```

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

Стабильная production baseline ветка:

```text
codex-vps-test-prep
```

Актуальный head:

```text
5f12736 Record VPS API smoke evidence
```

Стабильная baseline-ветка `amn2/codex-vps-test-prep` теперь содержит проверенный live VPS behavior contract и merged read-only API route shell.

Текущая активная рабочая ветка `Amneziya` для установки/API debug:

```text
codex/read-only-api-route-shell
head: 2010d60 Add API VPS smoke evidence template
remote: amn2/codex/read-only-api-route-shell
status: merged into `codex-vps-test-prep` at `5f12736`, local worktree clean
```

Эту ветку использовали в чате `Переводим AMN на API` для VPS install/update smoke и исправления ошибок. Актуальный real VPS loopback API-only smoke прошел 2026-06-03 с `run_id=20260603T112418Z`: DB-only server config sync выполнен, preflight `skipped`, API/auth/scope/revoke/listener/audit `passed`, `VPS_APPLY_ENABLED=false`, raw token/header/hash/config/keys/PSK не публиковались. Evidence: `research/amn2/api-vps-smoke-evidence-2026-06-03.md`. Предыдущий historical pass 2026-06-02 остается в `research/amn2/api-vps-smoke-evidence-2026-06-02.md`. После evidence ветка fast-forward merged в stable `codex-vps-test-prep` и запушена как production head `5f12736`. Главный coordination-chat не должен открывать параллельную API-реализацию; следующий допустимый API/web-panel slice - web-admin-only `API readiness/status` и `API token lifecycle` UI по `docs/superpowers/plans/2026-06-04-amn2-api-web-panel-finish.md`.

После scoped API token storage в `codex-vps-test-prep` уже вошли Route/Auth Binding Tests, API Token Lifecycle Gate и SSH Host Key Verifier через PR #4, PR #5 и PR #6. Эти срезы остаются local-gate-complete: без новых live VPS calls, без включения remote writes и без расширения `/api/*` routes до отдельного gate.

Проверенная stable-точка live VPS cycle:

```text
vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Основной handoff production-репозитория:

```text
docs/NEXT_CHAT_HANDOFF.ru.md
```

Последние зафиксированные local-only проверки по свежим gate-срезам `amn2`:

```text
Route/Auth Binding Tests: focused 22 passed; full 549 passed
API Token Lifecycle Gate stacked: focused 56 passed; full 555 passed
SSH Host Key Verifier: focused 29 passed; full 550 passed
Remote Operation VPS-gate candidate: focused/docs 107 passed; full 572 passed
Secret Inventory Registry: focused 64 passed; full 591 passed
Read-only API route shell: full 588 passed
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

После него локально выполнены и запушены в `amn2` следующие local-only / candidate slices:

- Redaction Coverage: `94ad807 Document secret-bearing delivery artifacts`;
- Config Delivery Integrity evidence: verified at `94ad807`;
- Public Token Safety: `dfe27ee Harden public email token safety`;
- Remote Operation state-changing contract / partial-failure / dry-run-audit: fresh VPS-gate candidate `codex/remote-operation-vps-gate-prep` prepared on top of `d0939d8`, head `262d70f`, runbook `research/amn2/vps-gate-remote-operation-dry-run-audit.md`;
- Local Agent Hardening: `c5d7eb6 Harden Local Agent audit contract`;
- Web Panel Safe Improvements: `22dfc37 Clarify web panel operation gates`;
- Scoped API Token Storage: `1fdcde5 Add scoped API token storage contract`.
- Route/Auth Binding Tests: branch `amn2/codex/route-auth-binding-tests`, commit `f9d2c79 Bind route inventory to surface policies`.
- API Token Lifecycle Gate: branch `amn2/codex/api-token-lifecycle-gate-stacked`, commit `256d0c0 Add API token lifecycle gate`.
- SSH Host Key Identity Verifier: branch `amn2/codex/ssh-host-key-identity-verifier`, commit `dd20364 Add SSH host key verifier`, merged to `codex-vps-test-prep` via PR #6; later read-only API route shell fast-forward moved current production head to `5f12736`.
- Manager Config Export Contract: branch `amn2/codex/manager-config-export-contract`, commit `4d4e7a4 Add manager config export contract`; local-only no-route typed export adapter, без public/self-service endpoint, API `config:read` и Local Agent `/configs`.
- Public/Self-service Config Delivery Policy: branch `amn2/codex/public-config-delivery-policy-contract`, commit `2ef3af7 Add config share policy contract`; local-only no-route share-token/policy contract, без public download route, self-service download route, API `config:read` и Local Agent `/configs`.
- Backup/Import Policy Contract: branch `amn2/codex/backup-import-policy-contract`, head `afb2702 Tighten backup import preview type contract` with foundation commit `d2c160b`; local-only no-route backup mode registry, secret field policy and restore/import preview contract, без web/API backup routes, restore apply, import apply или live VPS calls.
- Secret Inventory Registry: branch `amn2/codex/secret-inventory-registry`, commit `9ce42f4 Add secret inventory registry`; local-only machine-checkable secret inventory, без `.env` чтения, DB access, routes, secret-bearing output или live VPS calls.
- Packaging discovery fix: branch `amn2/codex/read-only-api-route-shell`, commit `e99d5f3 Fix editable install package discovery`; исправляет editable install/package discovery перед VPS install package smoke.
- Read-only API route shell: branch `amn2/codex/read-only-api-route-shell`, commits `6534ac4`, `9cccdc2`, `b37103a`, `2010d60`, `5f12736`; добавлены loopback-safe read-only `/api/*` routes, token smoke CLI, local API smoke readiness, `amn2/docs/API_VPS_SMOKE_EVIDENCE.ru.md`, AMN3 operator script `scripts/vps/amn2_api_loopback_smoke.sh` и update+smoke kit `dist/amn2-vps-update-and-smoke-kit-5f12736.zip`; full local suite `588 passed`, expected `StarletteDeprecationWarning`; latest real VPS API-only smoke passed 2026-06-03, `run_id=20260603T112418Z`, evidence `research/amn2/api-vps-smoke-evidence-2026-06-03.md`; fast-forward merged into `codex-vps-test-prep` at production head `5f12736`.

Решение по соседним чатам:

- `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`: широкие research-задачи поставить на паузу; оставить как targeted-input для web-panel UX, config delivery integrity, route taxonomy, scoped API tokens и dangerous-action patterns.
- `VPN Ops Lab — KYORESUAS-API`: уже переведен из reference-only в собственную `amn2` implementation lane на ветке `codex/read-only-api-route-shell`; upstream code не копируем, `/clients` write CRUD, `config:read`, backup/import/reboot не открываем.
- `Переводим AMN на API`: использовать как рабочий чат для установки на сервер, loopback API smoke и исправления ошибок по ветке `codex/read-only-api-route-shell`.
- Соседние направления, которые требуют SSH/sync/config/runtime writes, все еще можно переводить к интеграционным решениям только после controlled real VPS evidence: сначала read-only/dry-run, затем single peer apply/revoke по отдельному подтверждению.

## Что не делать первым

Не расширять production API за пределы уже сделанного read-only aggregate route shell.

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
research/amn2/route-auth-machine-checkable-tests-plan.md
research/amn2/backup-import-dangerous-api-design.md
research/amn2/manager-config-export-contract.md
research/amn2/manager-config-export-contract-implementation.md
research/amn2/public-self-service-config-delivery-policy.md
research/amn2/public-config-delivery-policy-contract-implementation.md
research/amn2/backup-import-policy-contract-implementation.md
research/amn2/secret-inventory-registry-implementation.md
research/amn2/kyoresuas-api-integration-priority-plan.md
amn2/docs/API_VPS_SMOKE_EVIDENCE.ru.md
amn2/docs/API_TOKEN_POLICY.ru.md
```

Pre-VPS support package:

```text
research/amn2/vps-gate-evidence-checklist.md
research/amn2/post-vps-gate-merge-decision.md
research/amn2/docker-manager-design-note.md
research/amn2/ssh-host-key-enrollment-design.md
research/amn2/neighbor-chat-vps-gate-handoff.md
research/amn2/read-only-metrics-privacy-classification.md
research/amn2/local-agent-runtime-metadata-alignment.md
research/amn2/api-token-rotation-revoke-policy.md
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

Локальная проверка показала, что эти commits уже содержались в production baseline после `91aeb3e`. Позднее Local Agent получил hardening commit `c5d7eb6`: repository-backed audit sink для allowed read routes, safe `/agent/version` metadata и тесты, что raw bearer token не попадает в audit. Runtime metadata boundary для будущего controller summary зафиксирован в `research/amn2/local-agent-runtime-metadata-alignment.md`; token lifecycle boundary - в `research/amn2/api-token-rotation-revoke-policy.md`, а local-only lifecycle gate выполнен в `amn2/codex/api-token-lifecycle-gate-stacked`, commit `256d0c0`. Следующий Local Agent slice не должен добавлять clients/configs/write routes.

## Рекомендуемый порядок

1. Не открывать второй параллельный API shell: read-only API route shell уже прошел local suite, real VPS loopback smoke и fast-forward merge в stable `codex-vps-test-prep`.
2. Следующий допустимый API/web-panel implementation slice: web-admin-only `API readiness/status` и `API token lifecycle` UI по `docs/superpowers/plans/2026-06-04-amn2-api-web-panel-finish.md`.
3. Новый VPS install/update package собран от production head `5f12736`; старый install package `d0939d8` остается историческим baseline package. Для будущего API/web-panel VPS теста использовать `docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md`.
4. Перед отдельным remote-operation VPS gate обновить/rebase `codex/remote-operation-vps-gate-prep` поверх нового stable head `5f12736`.
5. Controlled real VPS verification gate для `codex/remote-operation-vps-gate-prep` остается отдельным обязательным gate перед любым API/web/agent route, который вызывает SSH, syncs peers, emits config или меняет runtime state.
6. Route/Auth binding tests, scoped API token lifecycle, secret inventory, public config policy and backup/import policy остаются обязательными baselines перед дальнейшим route expansion.
7. `/clients` write CRUD, API `config:read`, public config delivery, backup/import/reboot, public docs/metrics, domain exclusions и 2FA не открывать до отдельного решения.

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

## Scoped API Token Storage Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
1fdcde5 Add scoped API token storage contract
```

Покрыто:

- `app.services.api_tokens` добавляет hash-only API token contract;
- raw token возвращается только через `ApiTokenIssue.raw_token` в момент выдачи;
- safe metadata содержит `raw_token_display=one-time` и не содержит raw token/hash;
- first-slice scopes ограничены `server:read` и `metrics:read`;
- `config:read`, write scopes и destructive scopes отклоняются;
- `api_tokens` table хранит `token_hash`, sorted `scopes_json`, owner metadata, `expires_at`, `revoked_at`, `last_used_at`;
- auth проверяет token exists, not revoked, not expired, required scope;
- docs фиксируют, что `/api/*` routes не добавлены.

Проверка:

```text
RED:
tests/services/test_api_tokens.py
tests/db/test_repositories.py::test_api_token_lifecycle_stores_hash_scopes_and_revoke_state
result: 1 import error as expected

GREEN focused slice:
tests/services/test_api_tokens.py
tests/db/test_repositories.py::test_api_token_lifecycle_stores_hash_scopes_and_revoke_state
result: 6 passed

focused security/db/services suite:
tests/services/test_api_tokens.py tests/db/test_repositories.py tests/agent/test_auth.py tests/security/test_surface_policy.py tests/test_file_hygiene.py
result: 54 passed

full local suite:
542 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice добавляет local storage/auth contract и docs, но не добавляет API routes, не делает peer apply/revoke/config/sync/runtime writes и не читает live VPS; VPS gate для самого slice не нужен.

## Manager Config Export Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/manager-config-export-contract
```

Production commit:

```text
4d4e7a4 Add manager config export contract
```

Покрыто:

- local-only `ConfigExportRequest` / `ConfigExportResult` / `ConfigExportArtifact` contract;
- adapter from current `DeviceConfigDelivery` / `ConfigDeliveryPackage`;
- typed artifacts for `.conf`, QR payload/PNG, `vpn://` import URI and delivery message;
- safe metadata boundary без raw `.conf`, QR payload, QR PNG/base64, `vpn://`, private key и PSK;
- safe categories for unsupported artifact, unsupported target client and exporter signature mismatch.

Проверка:

```text
focused config/security/delivery suite:
40 passed

full local suite:
560 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не добавляет public/self-service config endpoint, `/api/*` route, API `config:read`, Local Agent `/configs`, новые QR/import behavior или storage raw config в БД; VPS gate для самого slice не нужен.

## Public/Self-service Config Delivery Policy Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
2ef3af7 Add config share policy contract
```

Покрыто:

- local-only hash-only share-token lifecycle and policy service;
- `config_share_tokens` table and repository create/auth lookup/use/revoke contract;
- blocked future `SurfacePolicy` entries for self-service and public share config download;
- required expiry, purpose `config_share`, resource binding, one-time/max-download denial, revoke and generic public denial;
- safe audit metadata and redacted backup metadata with `restore-disabled`.

Проверка:

```text
focused config/token/security/db suite:
94 passed

full local suite:
577 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не добавляет public download route, self-service config download route, `/api/*`, API `config:read`, Local Agent `/configs`, generated config persistence, новые QR/import behavior или live VPS calls; VPS gate для самого slice не нужен.

## Backup/Import Policy Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/backup-import-policy-contract
```

Production head:

```text
afb2702 Tighten backup import preview type contract
```

Покрыто:

- local-only backup mode registry для `metadata-export`, `redacted-backup` и `encrypted-full-backup`;
- secret field policy для token hashes, peer private key, PSK, admin password hash, `.conf`, QR payload/PNG и `vpn://`;
- safe policy manifest без raw secret values;
- restore/import preview-only contract with `apply_allowed=false` and `side_effects=[]`;
- blocked future `SurfacePolicy` entries для backup/export, restore preview/apply и import preview/apply.

Проверка:

```text
RED:
tests/backup/test_backup_policy.py tests/security/test_surface_policy.py
result: 1 import error as expected

focused backup/security/agent suite:
61 passed

full local suite:
584 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не добавляет web/API backup routes, Local Agent `/backup` или `/restore`, restore apply, import apply, backup-before-write mutation или live VPS calls; VPS gate для самого slice не нужен.

## Secret Inventory Registry Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/secret-inventory-registry
```

Production commit:

```text
9ce42f4 Add secret inventory registry
```

Покрыто:

- `app.security.secret_inventory` как machine-checkable registry secret-bearing state;
- `SecretInventoryEntry` с secret class, storage surface, backup/restore defaults, route exposure и safe metadata policy;
- lookup/filter helpers;
- safe manifest без secret values;
- cross-check, что backup policy secret sources покрыты inventory.

Проверка:

```text
RED:
tests/security/test_secret_inventory.py
result: 1 import error as expected

focused security/backup/token suite:
64 passed

full local suite:
591 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не читает `.env`, не подключается к БД, не добавляет routes, secret-bearing output, backup export, restore/import apply или live VPS calls; VPS gate для самого slice не нужен.

## Remote Operation Dry-run/Audit Slice

Статус: `implemented-pushed-local-gate-complete`.

Production worktree:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-vps-gate-prep
```

Production branch:

```text
codex/remote-operation-vps-gate-prep
```

Production commits:

```text
c249bd0 Add state-changing operation metadata
8af6b5e Add remote partial failure model
b7a12ca Add remote operation dry-run metadata
aca6663 Add VPS gate handoff for remote ops
262d70f Merge current VPS test prep into remote operation gate
```

Покрыто:

- `RemoteOperationRunner.plan()` возвращает `consistency_status=dry-run` для state-changing операций без SSH;
- `OperationPlan.to_safe_metadata()` не публикует command strings и redacts audit/rollback/idempotency metadata;
- `apply-peer` и `revoke-peer` dry-run preview показывает operation ID, risk class, side effects и rollback note без PSK/private config;
- `docs/RUNTIME_REGISTRY.ru.md` и `docs/RUNTIME_REGISTRY.en.md` фиксируют local gate перед real VPS.

Проверка:

```text
focused server/security/policy/docs tests: 107 passed, 1 PytestCacheWarning
runtime registry docs tests: 7 passed
full local suite: 572 passed, 2 warnings
```

Live VPS не трогался. Candidate branch уже запушена в `amn2`; следующий шаг - отдельный controlled real VPS verification gate по `research/amn2/vps-gate-remote-operation-dry-run-audit.md`, начиная с read-only/dry-run подтверждения.

## Local Gate / Live VPS Gate

Новый порядок проверки разделен на два контура.

Локально можно делать:

- policy/inventory-only registry;
- redaction coverage;
- config delivery artifact tests;
- web/bot smoke через TestClient;
- Local Agent read-only/auth/token hardening на fake/local runtime;
- scoped API token storage/auth tests без `/api/*` routes;
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

Следующий рекомендуемый шаг теперь не очередной local-only feature slice, а controlled real VPS verification gate для ветки `codex/remote-operation-vps-gate-prep`: read-only check, dry-run apply/revoke preview, затем single test peer apply/revoke только после отдельного разрешения. Это нужно, чтобы параллельные KYORESUAS/PRVTPRO интеграционные задачи не пошли в main project без реального VPS evidence.
