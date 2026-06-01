# `amn2` Transfer Backlog

Дата: 2026-06-01.

Назначение: единая очередь переноса AMNEZIYA-наработок и upstream-идей из AMN3 в production repo `amn2`.

Правило: AMN3 хранит статус, решение, plan, branch/commit/PR links и test evidence. Production-код остается в `C:\Users\SooL\Documents\Amneziya` / `barakov-dot/amn2`.

## Verified Production Baseline

Актуальный `amn2` baseline:

```text
branch: codex-vps-test-prep
latest: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Текущий production head после локальных transfer-срезов:

```text
1fdcde5 Add scoped API token storage contract
```

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
| API readiness after verified live baseline | `audit-complete-first-slice-selected` | AMN3 -> `amn2` later | `research/amn2/api-readiness-audit-after-live-baseline.md` | После review написать plan для Route/Auth/Operation Policy Matrix |
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
| Remote operation VPS gate candidate | `prepared-pushed-awaits-real-vps-gate` | `amn2` branch + AMN3 runbook | branch `codex/remote-operation-vps-gate-prep`, head `aca6663`; runbook `research/amn2/vps-gate-remote-operation-dry-run-audit.md`; focused `79 passed`, docs `7 passed`, full `551 passed` | Выполнить read-only/dry-run на VPS; single apply/revoke только после отдельного подтверждения |
| VPS gate evidence/merge package | `prepared-local-docs` | AMN3 | `vps-gate-evidence-checklist.md`, `post-vps-gate-merge-decision.md`, `neighbor-chat-vps-gate-handoff.md` | Использовать сразу после real VPS gate для решения merge/PR и разблокировки соседних чатов |
| Docker manager safety note | `prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/docker-manager-design-note.md` | Использовать как вход для будущего implementation plan после VPS evidence |
| SSH host key enrollment design | `design-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/ssh-host-key-enrollment-design.md` | Использовать как policy gate перед VPS onboarding, web/API remote operations и app-managed host key pinning |
| SSH host key identity verifier | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/ssh-host-key-identity-verifier`, commit `dd20364`; evidence `research/amn2/ssh-host-key-verifier-implementation.md`; focused `29 passed`, full `550 passed` | Использовать как merge/cherry-pick candidate перед live VPS gate; следующий шаг - подключать к SSH-backed operations только отдельным gated slice |
| Route/Auth machine-checkable tests plan | `plan-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/route-auth-machine-checkable-tests-plan.md` | Следующий local-only slice: binding/drift tests поверх текущего `app/security/surface_policy.py`, без route expansion |
| Backup/import dangerous API design | `design-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/backup-import-dangerous-api-design.md` | Использовать как gate перед backup/import web/API routes, restore preview и full backup dangerous mode |
| Manager config export contract | `design-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/manager-config-export-contract.md` | Использовать как gate перед protocol manager export, public/self-service config links, API `config:read` и Local Agent `/configs` |
| Public/self-service config delivery policy | `design-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/public-self-service-config-delivery-policy.md` | Использовать как gate перед share/self-service config routes; first slice только no-route policy/share-token contract |
| Read-only metrics privacy classification | `classification-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/read-only-metrics-privacy-classification.md` | После VPS evidence писать implementation plan для aggregate-only API route shell |
| Local Agent runtime metadata alignment | `alignment-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/local-agent-runtime-metadata-alignment.md` | После VPS evidence писать implementation plan для controller-safe runtime summary, не clients/configs |
| API token rotation/revoke policy | `policy-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/api-token-rotation-revoke-policy.md` | Перед route expansion закрепить expiry, revoke, rotation, owner inheritance и audit-safe lifecycle |
| Web panel safe improvements | `implemented-pushed-local-gate-complete` | `amn2` | commit `22dfc37`; RED `4 failed as expected`; focused `75 passed`; full suite `536 passed` | Использовать как operator safety wording baseline; VPS gate не нужен |
| Scoped API token storage | `implemented-pushed-local-gate-complete` | `amn2` | commit `1fdcde5`; RED `1 import error as expected`; focused `54 passed`; full suite `542 passed` | Использовать как hash-only token baseline; VPS gate не нужен |
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

1. Выполнить controlled real VPS verification gate для `codex/remote-operation-vps-gate-prep` по `research/amn2/vps-gate-remote-operation-dry-run-audit.md`, начиная с Phase 0 SSH host key verification; single test peer apply/revoke только после отдельного подтверждения.
2. Зафиксировать VPS evidence в AMN3 через `research/amn2/vps-gate-evidence-checklist.md` перед интеграционными решениями из `VPN Ops Lab — KYORESUAS-API` и `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`.
3. Merge/PR candidate branch решать по `research/amn2/post-vps-gate-merge-decision.md`.
4. Local-only SSH host key identity verifier выполнен и запушен в `amn2/codex/ssh-host-key-identity-verifier`; app-managed pinning/live SSH integration делать только отдельным gated slice перед web/API remote-operation expansion.
5. Route/Auth machine-checkable tests plan подготовлен в `research/amn2/route-auth-machine-checkable-tests-plan.md`; следующий local-only slice должен быть binding/drift tests, без route expansion.
6. Backup/import dangerous API design подготовлен в `research/amn2/backup-import-dangerous-api-design.md`; web/API backup/import routes не добавлять до policy registry и restore-preview gate.
7. Manager config export contract подготовлен в `research/amn2/manager-config-export-contract.md`; первым переносить только local-only no-route adapter/tests, без public/self-service endpoint, API `config:read` или Local Agent `/configs`.
8. Public/self-service config delivery policy подготовлен в `research/amn2/public-self-service-config-delivery-policy.md`; public routes не добавлять, первый перенос только no-route policy registry/share-token contract.
9. Docker manager safety contract уже зафиксирован в `research/amn2/docker-manager-design-note.md`; implementation plan писать только после VPS evidence.
10. Read-only clients/metrics endpoints рассматривать только после VPS evidence; privacy classification подготовлена в `research/amn2/read-only-metrics-privacy-classification.md`, Local Agent runtime metadata alignment - в `research/amn2/local-agent-runtime-metadata-alignment.md`, token lifecycle policy - в `research/amn2/api-token-rotation-revoke-policy.md`.
11. Domain exclusions и 2FA держать отложенными до закрытия текущих safety gates.

## Neighbor Chat Decision

`VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`:

- broad research paused;
- keep as targeted input for web-panel UX, route taxonomy, config delivery integrity and dangerous-action UX;
- no code/UI/templates/managers/scripts copied because GPL-3.0.

`VPN Ops Lab — KYORESUAS-API`:

- keep active as API/Local-Agent architecture reference;
- no server install, no implementation copy, no broad CRUD/write API before policy/secret/remote-write gates.

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

Remote operation VPS gate branch `codex/remote-operation-vps-gate-prep` подготовлена и запушена как fresh candidate поверх `1fdcde5`: dry-run metadata и Runtime Registry подтверждены локально, но real VPS verification еще не запускался.

Web panel safe-improvements commit `22dfc37` также остается `local-gate-complete`: это wording/UI-test слой без изменения apply/revoke/config/sync/runtime behavior. Live VPS gate не нужен.

Scoped API token storage commit `1fdcde5` также остается `local-gate-complete`: добавлены `api_tokens` table, hash-only service contract, one-time raw token issue metadata, expiry/revoke/last-used fields, allowed first-slice scopes `server:read` и `metrics:read`, а `/api/*` routes не добавлены. Live VPS gate не нужен, потому что slice не меняет live apply/revoke/config/sync/runtime behavior.
