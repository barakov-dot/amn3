# `amn2` Transfer Backlog

Дата: 2026-06-02.

Назначение: единая очередь переноса AMNEZIYA-наработок и upstream-идей из AMN3 в production repo `amn2`.

Правило: AMN3 хранит статус, решение, plan, branch/commit/PR links и test evidence. Production-код остается в `C:\Users\SooL\Documents\Amneziya` / `barakov-dot/amn2`.

## Verified Production Baseline

Verified live `amn2` baseline:

```text
branch: codex-vps-test-prep
latest: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Текущий production head после merged API/VPS evidence transfer:

```text
5f12736 Record VPS API smoke evidence
```

В эту линию уже вошли PR #4/#5 по API token lifecycle и PR #6 по SSH host key verifier. Scoped API token storage `1fdcde5` остается важным baseline, но больше не является текущим production head.

Текущая active implementation branch для установки/API smoke:

```text
branch: codex/read-only-api-route-shell
remote branch: amn2/codex/read-only-api-route-shell
head: 2010d60 Add API VPS smoke evidence template
base: d0939d8 Merge pull request #6 from barakov-dot/codex/ssh-host-key-identity-verifier
status: merged into codex-vps-test-prep at 5f12736 after local tests and real VPS loopback API smoke
working chat: Переводим AMN на API
```

Актуализация 2026-06-03: latest real VPS API-only smoke passed на `/opt/amn2` через AMN3 operator script, `run_id=20260603T112418Z`; DB-only server config sync выполнен, preflight `skipped`, API/auth/scope/revoke/listener/audit `passed`, `VPS_APPLY_ENABLED=false`, raw token/header/hash/config/keys/PSK не публиковались. Evidence: `research/amn2/api-vps-smoke-evidence-2026-06-03.md`.

Live VPS cycle подтвержден на Docker AmneziaWG runtime:

- approve создает рабочий peer;
- config работает;
- `Working configs on server` обновляется сразу;
- `Run peer sync` подтверждает `confirmed live`;
- внешние Amnezia-created peer не удаляются;
- missing local device можно добавить на сервер;
- disable/enable работают;
- выборочное удаление устройства работает.

## Active Items

| Item | Статус | Target repo | Текущий artifact | Следующий шаг |
| --- | --- | --- | --- | --- |
| API readiness after verified live baseline | `implemented-historical-baseline` | AMN3 -> `amn2` | `research/amn2/api-readiness-audit-after-live-baseline.md`; Route/Auth matrix and read-only API shell already implemented | Использовать как historical decision source; VPS loopback API smoke для `codex/read-only-api-route-shell` passed 2026-06-02 |
| Main merge roadmap | `active-roadmap` | AMN3 -> `amn2` later | `docs/AMN2_MAIN_MERGE_ROADMAP.ru.md` | Использовать как порядок слияния API, web panel и operations |
| Local Amnezia Agent first slice | `merged-in-baseline` | `amn2` | merge PR #2, commits `3119ee6`, `ac2baa8` | Использовать как read-only baseline, не расширять до clients/configs без policy gate |
| Local Agent production wiring | `merged-in-baseline` | `amn2` | merge PR #3, head `8697b60` | Использовать как opt-in local runtime adapter boundary |
| VPS retest bundle | `verified-live-baseline` | `amn2` | commit `573c368` | Не трогать без изменения VPS apply/sync логики |
| Config defaults from `.env` | `verified-live-baseline` | `amn2` | commit `8ecb0b4` и последующие fixes | Использовать как текущий config contract |
| Docker runtime peer apply/revoke | `verified-live-baseline` | `amn2` | `codex-vps-test-prep`, tag `vps-live-cycle-verified` | Использовать как behavior contract |
| Redaction coverage | `implemented-pushed-local-gate-complete` | `amn2` | commits `75c235a`..`94ad807` | Использовать как secret-output baseline; VPS gate не нужен |
| Verified config delivery | `implemented-pushed-local-gate-complete` | `amn2` | commits `952cc49`, `4b19cd3`, `fc73929`; verified at `94ad807` | Использовать как artifact integrity baseline; VPS gate не нужен |
| Public-token safety | `implemented-pushed-local-gate-complete` | `amn2` | commit `dfe27ee`; tests `14 passed`, full suite `535 passed` | Использовать как verify/recover token baseline; VPS gate не нужен |
| Local Agent hardening | `implemented-pushed-local-gate-complete` | `amn2` | commit `c5d7eb6`; focused tests `64 passed`, full suite `536 passed` | Использовать как read-only audit/version contract; VPS gate не нужен |
| Remote operation VPS gate candidate | `prepared-pushed-awaits-real-vps-gate` | `amn2` branch + AMN3 runbook | branch `codex/remote-operation-vps-gate-prep`, head `262d70f`; runbook `research/amn2/vps-gate-remote-operation-dry-run-audit.md`; focused/docs `107 passed`, full `572 passed` | Выполнить read-only/dry-run на VPS; single apply/revoke только после отдельного подтверждения |
| VPS gate evidence/merge package | `prepared-local-docs` | AMN3 | `vps-gate-evidence-checklist.md`, `post-vps-gate-merge-decision.md`, `neighbor-chat-vps-gate-handoff.md` | Использовать сразу после real VPS gate для решения merge/PR и разблокировки соседних чатов |
| VPS install/update package | `published-updated-stable-5f12736` | AMN3 package for `amn2` | `dist/amn2-vps-install-5f12736.zip`, sha256 `CB2FBA547FD5DC50A94851BC7154D775FBD4977F09091E0F9BAE52F2DC9C2F25`; install package includes `amn2_api_loopback_smoke.sh` version `2026-06-04.1`; `dist/amn2-vps-update-and-smoke-kit-5f12736.zip`, sha256 `557C3B0C589BE98E1F5780DBBF289ACB3EB350F468BF369A6672B2A10DB2BB3C`; historical `d0939d8` package remains available | Использовать `install` для чистой установки, `update+smoke` для существующего `/opt/amn2` с сохранением `.env`/`data`/`venv`/`servers.yml`; smoke сам делает DB-only server config sync; `server preflight` запускать только как отдельный SSH/server dry-run gate |
| Docker manager safety note | `prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/docker-manager-design-note.md` | Использовать как вход для будущего implementation plan после VPS evidence |
| SSH host key enrollment design | `design-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/ssh-host-key-enrollment-design.md` | Использовать как policy gate перед VPS onboarding, web/API remote operations и app-managed host key pinning |
| SSH host key identity verifier | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/ssh-host-key-identity-verifier`, commit `dd20364`; evidence `research/amn2/ssh-host-key-verifier-implementation.md`; focused `29 passed`, full `550 passed` | Использовать как merge/cherry-pick candidate перед live VPS gate; следующий шаг - подключать к SSH-backed operations только отдельным gated slice |
| Route/Auth machine-checkable binding tests | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/route-auth-binding-tests`, commit `f9d2c79`; RED `1 import error as expected`; focused `22 passed`; full suite `549 passed` | Использовать как route/policy drift guard; VPS gate не нужен |
| Secret inventory registry | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/secret-inventory-registry`, commit `9ce42f4`; evidence `research/amn2/secret-inventory-registry-implementation.md`; RED `1 import error as expected`; focused `64 passed`; full suite `591 passed` | Использовать как machine-checkable secret baseline; route/API secret-bearing output остается отдельным gate |
| Backup/import dangerous API design | `design-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/backup-import-dangerous-api-design.md` | Использовать как gate перед backup/import web/API routes, restore preview и full backup dangerous mode |
| Backup/import policy contract | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/backup-import-policy-contract`, head `afb2702` with foundation commit `d2c160b`; evidence `research/amn2/backup-import-policy-contract-implementation.md`; RED `1 import error as expected`; focused `61 passed`; full suite `584 passed` | Использовать как no-route backup/import policy baseline; web/API full backup, restore apply и import apply остаются отдельными gates |
| Manager config export contract | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/manager-config-export-contract`, commit `4d4e7a4`; evidence `research/amn2/manager-config-export-contract-implementation.md`; focused `40 passed`, full `560 passed` | Использовать как no-route typed export adapter baseline; public/self-service endpoints, API `config:read` и Local Agent `/configs` остаются отдельными gates |
| Public/self-service config delivery policy | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/public-config-delivery-policy-contract`, commit `2ef3af7`; evidence `research/amn2/public-config-delivery-policy-contract-implementation.md`; focused `94 passed`, full `577 passed` | Использовать как no-route share-token/policy baseline; public download, self-service download, API `config:read` и Local Agent `/configs` остаются отдельными gates |
| Packaging discovery fix | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/read-only-api-route-shell`, commit `e99d5f3 Fix editable install package discovery` | Считать install/startup blocker закрытым для API smoke branch; проверять на VPS через editable install |
| KYORESUAS API integration priority | `merged-in-stable-read-only-api` | AMN3 -> `amn2` | `research/amn2/kyoresuas-api-integration-priority-plan.md`; `amn2/codex/read-only-api-route-shell`; latest evidence `research/amn2/api-vps-smoke-evidence-2026-06-03.md`; production head `5f12736` | Использовать как merged read-only API baseline; upstream code не копировать |
| Read-only API route shell | `merged-in-stable` | `amn2` | branch `codex/read-only-api-route-shell`, commits `6534ac4`, `9cccdc2`, `b37103a`, `2010d60`, `5f12736`; full suite `588 passed`; focused merge check `75 passed`; latest real VPS smoke passed `run_id=20260603T112418Z`; operator script `scripts/vps/amn2_api_loopback_smoke.sh`; update+smoke kit `dist/amn2-vps-update-and-smoke-kit-5f12736.zip` | Считать first read-only API baseline merged; дальнейшее route expansion только через отдельные gates |
| API/Web panel finish slice | `implemented-pushed-local-gate-complete-awaits-merge` | `amn2` branch + AMN3 evidence | branch `codex/api-web-panel-finish`, commit `294803e`; evidence `research/amn2/api-web-panel-finish-implementation.md`; plan `docs/superpowers/plans/2026-06-04-amn2-api-web-panel-finish.md`; VPS runbook `docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md` | Review/merge into target production head, then rebuild AMN3 VPS package and run web/API VPS test via loopback + SSH tunnel, без live apply |
| Read-only metrics privacy classification | `classification-used-by-api-shell` | AMN3 -> `amn2` | `research/amn2/read-only-metrics-privacy-classification.md` | Держать как privacy baseline для aggregate-only API; detailed client metrics остаются заблокированы |
| Local Agent runtime metadata alignment | `alignment-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/local-agent-runtime-metadata-alignment.md` | После VPS evidence писать implementation plan для controller-safe runtime summary, не clients/configs |
| API token rotation/revoke policy | `policy-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/api-token-rotation-revoke-policy.md` | Policy остается design source для route expansion и Local Agent token separation |
| API token lifecycle gate | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/api-token-lifecycle-gate`, commit `c2ba646`; stacked branch `codex/api-token-lifecycle-gate-stacked`, commit `256d0c0` поверх `codex/route-auth-binding-tests`; evidence `research/amn2/api-token-lifecycle-gate-implementation.md`; stacked focused `56 passed`, full `555 passed` | Использовать как service/repository lifecycle baseline; `/api/*` routes, `config:read`, write scopes и bearer-token route exposure остаются отдельными gates |
| Web panel safe improvements | `implemented-pushed-local-gate-complete` | `amn2` | commit `22dfc37`; RED `4 failed as expected`; focused `75 passed`; full suite `536 passed` | Использовать как operator safety wording baseline; VPS gate не нужен |
| Scoped API token storage | `implemented-pushed-local-gate-complete` | `amn2` | commit `1fdcde5`; RED `1 import error as expected`; focused `54 passed`; full suite `542 passed` | Использовать как hash-only token baseline; lifecycle gate выполнен отдельным branch `codex/api-token-lifecycle-gate`, а для очереди после route/auth binding есть stacked branch `codex/api-token-lifecycle-gate-stacked`; VPS gate не нужен |
| Public/self-service config delivery | `lab-only-until-policy` | AMN3 -> `amn2` later | `research/amn2/config-delivery-inventory.md` | Не открывать public config links до scoped token/self-service design |

## Local Agent Decision

Решение: переносить как собственную реализацию `amn2`, без копирования внешнего `kyoresuas/amnezia-api`.

Причина:

- задача совпадает с целевым продуктом: API-first управление пользователями Amnezia;
- текущий first slice уже защищен route policy, hash-only token auth, typed auth errors и no-write boundary;
- ближайший production gain - получить opt-in local runtime adapter на сервере, который controller сможет опрашивать безопасно; safety boundary для этого зафиксирован в `research/amn2/local-agent-runtime-metadata-alignment.md`;
- verified VPS baseline теперь дает реальный behavior contract для будущих write операций.

## Transfer Gates

Любая новая функция из AMN3 переходит в `amn2` только если есть:

- source/license verdict;
- current `amn2` inventory;
- risk class;
- route/auth policy;
- secret and audit decision;
- tests;
- rollback/recovery note for state-write or remote operations;
- AMN3 return note after branch/commit/PR.

## Current Priority Order

1. Считать first read-only API shell merged в stable `codex-vps-test-prep` at `5f12736`.
2. API/web-panel finish slice реализован и запушен в `amn2/codex/api-web-panel-finish` at `294803e`; local full suite `594 passed`.
3. Не расширять API route surface в этом slice: `/api/clients` write CRUD, API `config:read`, public config delivery, backup/import/reboot, public docs/metrics и detailed client metrics остаются заблокированы до отдельного решения.
4. После merge/rebase API/web-panel branch пересобрать VPS install/update package от нового production head; для web/API теста использовать `docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md`.
5. Controlled real VPS verification gate для `codex/remote-operation-vps-gate-prep` остается отдельным обязательным gate перед API/web/agent routes, которые вызывают SSH, sync peers, emit config или меняют runtime state; single test peer apply/revoke только после отдельного подтверждения.
6. Route/Auth binding tests, scoped API token lifecycle, secret inventory, public config policy and backup/import policy остаются обязательными baselines перед route expansion.
7. Domain exclusions и 2FA держать отложенными до закрытия текущих safety gates.

## Neighbor Chat Decision

`VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`:

- broad research paused;
- keep as targeted input for web-panel UX, route taxonomy, config delivery integrity and dangerous-action UX;
- no code/UI/templates/managers/scripts copied because GPL-3.0.

`VPN Ops Lab — KYORESUAS-API`:

- теперь является источником product direction для собственной `amn2` API lane;
- активная реализация идет в `amn2/codex/read-only-api-route-shell`, не через копирование upstream code;
- no broad CRUD/write API, no `config:read`, no backup/import/reboot before policy/secret/remote-write gates.

## Когда нужен новый live retest

Новый live retest обязателен, если меняется хотя бы одно из:

- peer apply/revoke;
- config template/defaults;
- IP allocation;
- peer sync classification;
- disable/enable/delete device flows;
- Docker runtime write/restart behavior.

## Route/Auth/Operation Policy Matrix Plan

Статус: `implemented-in-amn2-local-commit`.

Plan artifact:

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

Created in `amn2`:

- `app/security/surface_policy.py`
- `tests/security/test_surface_policy.py`
- `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`

Verification:

```text
tests/security/test_surface_policy.py tests/agent/test_policy.py tests/server/test_operation_runner.py tests/server/test_checks.py -v
result: 46 passed

tests/web/test_app.py tests/web/test_users.py tests/web/test_servers.py tests/web/test_email_delivery.py tests/bot/test_bot_workflows.py -v
result: 85 passed, 1 StarletteDeprecationWarning
```

Note: pytest emitted the known Windows temp cleanup `PermissionError` after successful sessions; both commands returned exit code 0.

Границы slice:

- live VPS не трогать;
- новых endpoints не добавлять;
- config/self-service API не добавлять;
- Local Agent clients/configs/backup/restore/reboot не включать;
- upstream code не копировать.

## Local Gate / Live VPS Gate

Все следующие transfer items делятся на два контура.

### Local gate

Можно выполнять и коммитить после локальных тестов:

- policy/inventory-only registry;
- redaction coverage;
- config delivery artifact tests;
- web/bot TestClient smoke;
- Local Agent read-only/auth/token hardening на fake/local runtime;
- remote operation contract tests на fake SSH/client;
- docs/status/backlog updates.

### Live VPS gate

Отдельная проверка на реальном VPS нужна только после local green, если item меняет:

- peer apply/revoke;
- disable/enable/delete;
- add missing local device to server;
- remove unknown remote peer;
- peer sync classification;
- config templates/defaults, которые попадут в рабочий client config;
- Docker AmneziaWG write/reload/restart behavior;
- real Local Agent deployment или controller-to-agent calls.

Policy matrix commit `d1d9690` остается `local-gate-complete`; live VPS gate для него не нужен.

Redaction coverage commits `75c235a`..`94ad807` также остаются `local-gate-complete`: они усиливают sanitizer, тесты и docs, но не меняют live apply/revoke/config/sync behavior.

Config delivery integrity на head `94ad807` также остается `local-gate-complete`: `.conf` UTF-8 bytes, QR payload, `vpn://` round-trip, non-ASCII fixture и secret metadata подтверждены локальными тестами; live VPS gate не нужен, пока не меняются реальные templates/defaults или apply/sync behavior.

Public-token safety commit `dfe27ee` также остается `local-gate-complete`: TTL guard, hash-only token contract, verify/recover purpose separation, expired-code rejection, generic denial/no raw token echo и no-consume failure behavior подтверждены локальными тестами. Live VPS gate не нужен, потому что slice не меняет peer apply/revoke/config/sync/runtime behavior.

Local Agent hardening commit `c5d7eb6` также остается `local-gate-complete`: `agent serve` подключает repository-backed audit sink для allowed read routes, `/agent/version` публикует runtime contract metadata, а tests подтверждают отсутствие raw bearer token в audit. Live VPS gate не нужен, потому что slice не делает real agent deployment, controller-to-agent calls, peer apply/revoke/config/sync/runtime writes.

Remote operation VPS gate branch `codex/remote-operation-vps-gate-prep` была подготовлена поверх прежнего `codex-vps-test-prep` head `d0939d8`: dry-run metadata, Runtime Registry и SSH host key verifier baseline подтверждены локально, но real VPS verification еще не запускался. Перед отдельным remote-operation VPS gate ее нужно обновить/rebase поверх нового stable head `5f12736`.

Web panel safe-improvements commit `22dfc37` также остается `local-gate-complete`: это wording/UI-test слой без изменения apply/revoke/config/sync/runtime behavior. Live VPS gate не нужен.

Scoped API token storage commit `1fdcde5` также остается `local-gate-complete`: добавлены `api_tokens` table, hash-only service contract, one-time raw token issue metadata, expiry/revoke/last-used fields, allowed first-slice scopes `server:read` и `metrics:read`, а `/api/*` routes не добавлены. Live VPS gate не нужен, потому что slice не меняет live apply/revoke/config/sync/runtime behavior.

Route/Auth binding tests commit `f9d2c79` также остается `local-gate-complete`: добавлены inventory-only route bindings, web runtime route drift tests, Local Agent blocked-future assertions и test-ref integrity check. Slice не добавляет endpoints, не меняет web/bot/agent/CLI behavior и не трогает live VPS.

Manager config export contract commit `4d4e7a4` также остается `local-gate-complete`: добавлен no-route typed export adapter для существующего `DeviceConfigDelivery`/`ConfigDeliveryPackage`, safe metadata и stable error categories. Slice не добавляет public/self-service endpoint, API `config:read`, Local Agent `/configs`, новый QR/import behavior или live VPS calls.

Public/self-service config delivery policy commit `2ef3af7` также остается `local-gate-complete`: добавлен no-route hash-only share-token/policy contract, `config_share_tokens` storage, blocked future policy entries and safe audit/backup metadata. Slice не добавляет public download route, self-service download route, API `config:read`, Local Agent `/configs`, generated config persistence, новый QR/import behavior или live VPS calls.

Backup/import policy contract head `afb2702` (foundation commit `d2c160b`) также остается `local-gate-complete`: добавлен no-route backup mode registry, secret field policy, safe manifests, restore/import preview-only contracts and blocked future `SurfacePolicy` entries. Slice не добавляет `/api/*`, web/Local Agent backup routes, restore apply, import apply или live VPS calls.

Secret inventory registry commit `9ce42f4` также остается `local-gate-complete`: добавлен machine-checkable `app.security.secret_inventory`, safe manifest, lookup/filter helpers and backup policy cross-checks. Slice не читает `.env`, не подключается к БД, не добавляет routes, secret-bearing output или live VPS calls.
