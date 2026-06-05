# `amn2` / AMN3: готовые фазы и переносимые правила

Дата: 2026-06-05.

Назначение: собрать готовые фазы всего проекта в один рабочий snapshot и выделить наработки, которые нужно учитывать в дальнейшем развитии `amn2`, будущего hybrid-проекта и общего Codex skill по VPN/control-panel системам.

Этот документ не открывает новые production routes и не разрешает live VPS mutation. Он фиксирует уже подтвержденные границы, evidence и правила переноса.

## Текущая точка правды

Production repo:

```text
C:\Users\SooL\Documents\Amneziya
branch: codex-vps-test-prep
head: 7764ae7 Cover integration status in API smoke
```

Lab / coordination repo:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
branch: master
```

Текущие закрытые этапы:

```text
Phase 1 read-only/API/web-panel baseline
status: closed
amn2 head: 7764ae7
evidence: research/amn2/phase-1-closeout-2026-06-04.md
package: dist/amn2-vps-update-and-smoke-kit-7764ae7.zip

Phase 2 live single test peer apply/revoke
status: verified-live
amn2 head: 7764ae7
evidence: research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md
scope: exactly one disposable test peer apply/sync/revoke/sync
```

Следующие опасные поверхности:

```text
status: still blocked behind separate gates
surfaces: broad write API, public config delivery, API config:read, /api/clients CRUD, backup/import/reboot, Local Agent mutations, public web/API exposure
```

## Готовые фазы

### 1. Lab foundation and upstream governance

Готово:

- AMN3 закреплен как research/coordination lab, production-код остается в `amn2`;
- PRVTPRO/Amnezia-Web-Panel классифицирован как GPL-3.0 `research-only` источник;
- KYORESUAS/Amnezia API использован как product-direction для собственной `amn2` read-only API lane, без копирования кода;
- transfer gate стал обязательным: license, benefit, risk, architecture fit, tests, recovery/rollback, evidence.

Что переносить дальше:

- любые upstream-сигналы переводить в требования и тест-планы, а не в копирование implementation;
- каждый внешний проект получать карточку: license verdict, usable ideas, blocked copying, required gates.

### 2. Verified live VPS baseline

Готово и подтверждено на живом VPS:

- approve заявки создает рабочий peer;
- client config подключается;
- web panel показывает working config после approve;
- peer sync подтверждает live-состояние;
- external Amnezia-created peers не удаляются автоматически;
- missing local device можно добавить на сервер;
- disable/enable работает;
- selective device delete работает;
- Docker AmneziaWG apply/revoke behavior подтвержден.

Что переносить дальше:

- это behavior contract для всех будущих remote-write изменений;
- новый live retest нужен при изменениях peer apply/revoke, config templates/defaults, IP allocation, sync classification, Docker write/restart behavior.

### 3. Local safety foundation

Готово local-gate-complete:

- route/auth/operation policy matrix;
- route/auth binding and drift tests;
- secret/redaction coverage;
- config delivery integrity для `.conf`, QR, `vpn://`, UTF-8 и non-ASCII;
- public token safety: hash-only, purpose separation, expiry, generic denial;
- scoped API token storage and lifecycle: scopes, expiry, revoke, rotation, owner inheritance;
- Local Agent read-only hardening: audit/version contract, no raw bearer token in audit;
- SSH host key identity verifier;
- secret inventory registry;
- backup/import policy contract;
- manager config export contract;
- public/self-service config delivery policy contract;
- web panel dangerous-action wording.

Что переносить дальше:

- перед любым новым route сначала обновлять policy/binding tests;
- `.conf`, QR, `vpn://`, raw token, token hash, backup, Local Agent credential и command output всегда считать secret-bearing;
- backup/import, public config delivery and config-read routes не открывать без отдельного secret-read gate.

### 4. Read-only API route shell

Готово:

- собственная `amn2` API lane реализована без копирования KYORESUAS code;
- read-only loopback-safe `/api/*` routes добавлены с scoped token model;
- token smoke CLI и API smoke readiness добавлены;
- real VPS loopback API smoke passed 2026-06-03;
- branch fast-forward merged into stable `codex-vps-test-prep` at `5f12736`.

Что переносить дальше:

- API расширять только read-only-first и local/loopback-first;
- public exposure, write scopes, `config:read`, `/api/clients` CRUD и detailed per-client metrics остаются отдельными gates.

### 5. API/Web Panel Phase 1

Готово:

- API readiness web-admin page;
- API token lifecycle web-admin page;
- API/web-panel VPS gate passed 2026-06-04 for `294803e`;
- `GET /api/integration/status` and web-admin `/integration-status`;
- `api smoke-check` покрывает integration status;
- Phase 1 closeout закрыт на `7764ae7`.

Verification:

```text
focused: 39 passed
full: 610 passed
```

Что переносить дальше:

- operator-facing status surfaces полезны до write lifecycle;
- status route должен быть read-only, policy-bound и не раскрывать secrets;
- API smoke должен проверять только read-only routes, а SSH/server preflight оставаться отдельным gate.

### 6. Remote-operation dry-run gate

Готово:

- state-changing operation metadata;
- partial-failure model;
- dry-run/audit metadata;
- `apply-peer --dry-run` and `revoke-peer --dry-run` safe metadata;
- remote-operation candidate updated on stable API/web-panel baseline at `7281254`;
- real VPS Phase 1 read-only/dry-run gate passed as `dry-run-only-pass`.
- real VPS Phase 2 single disposable peer apply/sync/revoke/sync passed on current stable `7764ae7` as `verified-live`.

Не готово:

- any broad API/web/agent route that invokes SSH, syncs peers, emits config or mutates runtime state.

Что переносить дальше:

- `dry-run-only-pass` является самостоятельным безопасным статусом, но больше не является текущим результатом Phase 2;
- Phase 2 `verified-live` покрывает ровно один disposable test peer и не открывает broad write/API/config/agent surfaces;
- broad write integration нельзя разблокировать на основании одного scoped disposable-peer evidence.

### 7. Packaging and operator evidence

Готово:

- source zip package с SHA256;
- update+smoke kit с operator doc;
- expected source commit;
- update scripts preserve `.env`, `data`, `venv`, `servers.yml`;
- smoke performs DB-only server config sync before API route checks;
- forbidden entries/package hygiene verification;
- no-secret evidence discipline.

Что переносить дальше:

- любой VPS-ready slice должен иметь package, checksum, expected commit, update path, smoke path, rollback/recovery note;
- evidence должна фиксировать pass/fail без raw token, header, token hash, config, private key, PSK, QR payload или `vpn://`.

## Статусы, которые нельзя смешивать

| Статус | Что означает | Что не означает |
| --- | --- | --- |
| `local-gate-complete` | Код/контракт проверен локально, без VPS writes | Можно запускать на production VPS без отдельного gate |
| `api-smoke-passed` | Read-only loopback API проверен на VPS | Разрешены write routes или public exposure |
| `dry-run-only-pass` | Read-only/dry-run remote-operation gate прошел | Live apply/revoke подтверждены |
| `verified-live` | Конкретная live mutation прошла с rollback/evidence | Можно расширять другие destructive surfaces без gate |
| `phase-closeout` | Фаза закрыта с package/evidence | Следующая фаза разрешена автоматически |

## Что заблокировано до отдельных gates

- `/api/clients` write CRUD;
- API `config:read`;
- public/self-service config delivery;
- Local Agent `/agent/clients`, `/agent/configs` и write lifecycle;
- backup/import web/API routes;
- restore/import apply;
- reboot/destructive endpoints;
- public docs/metrics;
- detailed per-peer/client metrics;
- Docker manager implementation;
- attach existing server auto-reconcile;
- domain zone exclusions;
- web-admin 2FA.

## Наработки для будущего hybrid

Использовать как архитектурные правила:

- operator-first panel: status/readiness before mutation;
- dense admin UX вместо marketing UI;
- route taxonomy and risk classes as product language;
- scoped integration tokens instead of broad API key;
- local-only or loopback-first API agent;
- config delivery as secret-read, not ordinary file download;
- dry-run -> confirmation -> apply -> audit -> rollback as required write flow;
- background jobs only after operation contract, timeout, cancellation and final audit summary;
- existing server reconciliation only through read-only detect and redacted preview first.

## Наработки для общего Codex skill

Добавить в skill как общие правила:

1. Начинать VPN/control-panel upstream с license verdict и copying boundary.
2. Разделять идеи, architecture pattern, UX signal и implementation code.
3. Для каждого route/action фиксировать actor, auth method, role, scope, risk class, secret class, side effects, audit, test refs.
4. Всегда отделять local gate от live VPS gate.
5. Вводить `dry-run-only-pass` как отдельный статус, не равный `verified-live`.
6. Read-only/API/status surfaces можно развивать раньше write lifecycle, если они aggregate-only, scoped, audited and no-secret.
7. VPS package должен иметь source zip, checksum, expected commit, update script, smoke script, rollback note and no-secret evidence.
8. Evidence не должна содержать raw token/header/hash/config/private key/PSK/QR/vpn URI.
9. Любой write route должен пройти dry-run, explicit confirmation, audit, rollback and recovery story.
10. Phase closeout должен фиксировать package, tests, evidence, blocked surfaces and next gate.

## Следующая рекомендуемая работа

Не начинать новый write implementation в этом чате.

Ближайшая безопасная работа:

1. перенести правила этого документа в общий Codex skill;
2. использовать Phase 2 live single test peer apply/revoke evidence как scoped `verified-live`, не как blanket-разрешение на destructive surfaces;
3. для следующих write/runtime slices требовать отдельный gate;
4. для следующей production-функции сначала сделать design/plan с явным ответом: нужен ли live VPS gate.
