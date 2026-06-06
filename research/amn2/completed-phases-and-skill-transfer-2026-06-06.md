# `amn2` / AMN3: готовые фазы и переносимые правила

Дата: 2026-06-06.

Назначение: обновить общий snapshot готовых фаз проекта после свежих наработок в `amn2` и AMN3, чтобы дальнейшие доработки не опирались на устаревшую картину от 2026-06-05.

Документ фиксирует только подтвержденные границы, evidence и правила переноса. Он не открывает новые production routes, не разрешает public exposure и не превращает scoped live evidence в общее разрешение на write/destructive операции.

## Текущая точка правды

Production repo:

```text
C:\Users\SooL\Documents\Amneziya
branch: codex-vps-test-prep
current head: c8a6363 Add Local Agent runtime summary mapper
```

Lab / coordination repo:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
branch: master
current head: 8f613c8 Publish c8a6363 VPS update package
```

Текущий пакет по git head:

```text
source commit: c8a6363
status: read-only-vps-smoke-pass
package: dist/amn2-vps-update-and-smoke-kit-c8a6363.zip
package sha256: 027ECC1BAD7321FCCD61A4CCCA3AC9F06AAA9AC6A3D7115B4813253D19C2CFBF
source zip: dist/amn2-codex-vps-test-prep-c8a6363-source.zip
source sha256: E1E198979D988B3A5AA038CF732B8DCDBE854C48A6D381FADBA05BFDEE0251C6
```

Последний VPS-smoked runtime/source:

```text
source commit: c8a6363
status: read-only-vps-smoke-pass
run_id: 20260606T202040Z
decision: passed
```

Важно: `c8a6363` уже является текущим `amn2` head и последним подтвержденным на VPS runtime/source. `32d01fd` остается historical prior VPS-smoked baseline.

## Готовые фазы

### 1. Lab foundation and upstream governance

Готово:

- AMN3 закреплен как research/coordination lab, production-код остается в `amn2`;
- PRVTPRO/Amnezia-Web-Panel классифицирован как GPL-3.0 `research-only` источник;
- KYORESUAS/Amnezia API использован как product-direction для собственной `amn2` read-only API lane, без копирования кода;
- transfer gate стал обязательным: license, benefit, risk, architecture fit, tests, recovery/rollback, evidence.

Правило переноса:

- любые upstream-сигналы переводить в требования, тест-планы и архитектурные решения, а не в копирование implementation;
- для каждого внешнего проекта вести карточку: license verdict, usable ideas, blocked copying, required gates.

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

Правило переноса:

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

Правило переноса:

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

Правило переноса:

- API расширять только read-only-first и local/loopback-first;
- public exposure, write scopes, `config:read`, `/api/clients` CRUD и detailed per-client metrics остаются отдельными gates.

### 5. API/Web Panel Phase 1

Готово:

- API readiness web-admin page;
- API token lifecycle web-admin page;
- API/web-panel VPS gate passed 2026-06-04 for `294803e`;
- `GET /api/integration/status` and web-admin `/integration-status`;
- `api smoke-check` покрывает integration status;
- Phase 1 closeout закрыт на `7764ae7`;
- later integration status updated for controlled-prod context at `32d01fd`.

Verification snapshots:

```text
7764ae7 focused: 39 passed
7764ae7 full: 610 passed
32d01fd read-only VPS smoke: passed, run_id 20260606T185114Z
c8a6363 read-only VPS smoke: passed, run_id 20260606T202040Z
```

Правило переноса:

- operator-facing status surfaces полезны до write lifecycle;
- status route должен быть read-only, policy-bound и не раскрывать secrets;
- API smoke должен проверять только read-only routes, а SSH/server preflight оставаться отдельным gate.

### 6. Remote-operation dry-run and scoped live gate

Готово:

- state-changing operation metadata;
- partial-failure model;
- dry-run/audit metadata;
- `apply-peer --dry-run` and `revoke-peer --dry-run` safe metadata;
- remote-operation candidate updated on stable API/web-panel baseline at `7281254`;
- real VPS Phase 1 read-only/dry-run gate passed as `dry-run-only-pass`;
- real VPS Phase 2 single disposable peer apply/sync/revoke/sync passed as `verified-live`.

Уточнение после свежих фаз:

- `verified-live` покрывает ровно один disposable test peer apply/revoke path;
- broad write API, web write, Local Agent mutations, config delivery, backup/import and destructive operations не открыты;
- current head `c8a6363` не меняет этот live-write scope и прошел read-only VPS smoke.

Правило переноса:

- `dry-run-only-pass` является самостоятельным безопасным статусом, но не равен `verified-live`;
- `verified-live` всегда должен указывать точный scope, commit, run/evidence и rollback result;
- broad write integration нельзя разблокировать на основании одного scoped disposable-peer evidence.

### 7. Preshared key stdin hardening

Готово:

- `--preshared-key-stdin` добавлен как безопасный путь передачи PSK для CLI;
- `--preshared-key` оставлен только как compatibility path;
- docs явно рекомендуют stdin mode;
- VPS read-only smoke подтвердил обновленный runtime/source line.

Правило переноса:

- secret-bearing CLI arguments считать рискованными даже при локальном запуске;
- для PSK, private key, API token, backup password и similar secrets предпочитать stdin, env file with protected permissions или external secret store;
- evidence и docs не должны показывать raw PSK, token, header, config body, QR payload или `vpn://`.

### 8. Remote partial-failure contract

Готово:

- remote peer apply/revoke flow получил явный partial-failure contract;
- runtime operation output разделяет success, partial failure, recovery note and safe audit metadata;
- bot/workflow/server operation paths согласованы с контрактом;
- VPS read-only smoke для этой линии прошел до controlled-prod readiness prefill.

Правило переноса:

- для любой операции между local metadata, file write, sync/restart and audit нужен partial-failure model;
- recovery note должен быть полезным оператору, но без secrets;
- tests должны покрывать не только happy path, но и split-brain/partial apply cases.

### 9. Controlled prod readiness prefill

Готово:

- подготовлен controlled-prod readiness runbook;
- зафиксирована цель: operator-only controlled prod, не public SaaS;
- собраны pending confirmations для реального VPS;
- stop conditions and blocked surfaces описаны отдельно.

Текущий статус:

```text
status: readiness-prefill-recorded; operator-confirmations-pending
last VPS-smoked source: c8a6363
previous VPS-smoked source: 32d01fd
```

Операторские подтверждения еще нужны:

- source overlay на VPS соответствует целевому commit;
- read-only smoke для target commit passed;
- web/admin access path operator-only;
- `VPS_APPLY_ENABLED=false` по умолчанию;
- SSH host key prompt/identity проверены;
- recovery path понятен;
- decision recorded as `controlled-prod-ready`, `needs-fix` or `defer-prod`.

Правило переноса:

- controlled-prod-ready нельзя объявлять по одному локальному test pass или package-ready status;
- для каждого target commit отдельно различать current git head, package-ready head и last VPS-smoked runtime/source.

### 10. Local Agent runtime summary mapper

Готово:

- local-only mapper/service добавлен в `app/agent/runtime_summary.py`;
- tests добавлены в `tests/agent/test_runtime_summary.py`;
- focused verification: `3 passed`;
- adjacent regression: `37 passed, 1 warning`;
- full suite: `619 passed, 1 warning`;
- merged into AMN2 stable line at `c8a6363`;
- AMN3 package prepared and read-only VPS-smoked for `c8a6363`.

Не открыто:

- no API route;
- no web route;
- no CLI command;
- no Local Agent mutation;
- no live VPS write operation.

Правило переноса:

- для Local Agent сначала делать controller-safe mapper/read model, потом route, потом UI, потом live/runtime gate;
- local-only mapper можно считать готовым для кодовой линии, но не VPS-smoked runtime, пока не пройдет отдельный update/smoke.

### 11. Packaging and operator evidence

Готово:

- source zip package с SHA256;
- update+smoke kit с operator doc;
- expected source commit;
- update scripts preserve `.env`, `data`, `venv`, `servers.yml`;
- smoke performs DB-only server config sync before API route checks;
- forbidden entries/package hygiene verification;
- no-secret evidence discipline.

Свежий пример:

```text
commit: c8a6363
package status: read-only-vps-smoke-pass
package hygiene: passed
source entries: 294
forbidden source entries: none
required entries: present
```

Правило переноса:

- любой VPS-ready slice должен иметь package, checksum, expected commit, update path, smoke path, rollback/recovery note;
- evidence должна фиксировать pass/fail без raw token, header, token hash, config, private key, PSK, QR payload или `vpn://`.

## Статусы, которые нельзя смешивать

| Статус | Что означает | Что не означает |
| --- | --- | --- |
| `local-gate-complete` | Код/контракт проверен локально, без VPS writes | Можно запускать на production VPS без отдельного gate |
| `package-ready-not-vps-smoked` | Пакет собран, checksum/package hygiene прошли | Этот commit уже работает на VPS |
| `read-only-vps-smoke-pass` | Read-only loopback/API route smoke прошел на VPS | Разрешены write routes или public exposure |
| `dry-run-only-pass` | Read-only/dry-run remote-operation gate прошел | Live apply/revoke подтверждены |
| `verified-live` | Конкретная live mutation прошла с rollback/evidence | Можно расширять другие destructive surfaces без gate |
| `controlled-prod-readiness-pending` | Runbook/evidence собраны, но операторские подтверждения не закрыты | Controlled prod готов |
| `controlled-prod-ready` | Target commit проверен на VPS и операторские условия закрыты | Public/self-service SaaS разрешен автоматически |

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
- domain zone exclusions / VPN bypass policy;
- web-admin 2FA;
- broad public web/API exposure.

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
- existing server reconciliation only through read-only detect and redacted preview first;
- package-ready, VPS-smoked and prod-ready statuses показывать отдельно.

## Наработки для общего Codex skill

Добавить в skill как общие правила:

1. Начинать VPN/control-panel upstream с license verdict и copying boundary.
2. Разделять идеи, architecture pattern, UX signal и implementation code.
3. Для каждого route/action фиксировать actor, auth method, role, scope, risk class, secret class, side effects, audit, test refs.
4. Всегда отделять local gate от live VPS gate.
5. Отдельно различать current git head, package-ready head and last VPS-smoked runtime/source.
6. Вводить `dry-run-only-pass` как отдельный статус, не равный `verified-live`.
7. `verified-live` всегда должен иметь точный scope и не давать blanket-разрешение другим write/destructive surfaces.
8. Read-only/API/status surfaces можно развивать раньше write lifecycle, если они aggregate-only, scoped, audited and no-secret.
9. VPS package должен иметь source zip, checksum, expected commit, update script, smoke script, rollback note and no-secret evidence.
10. Evidence не должна содержать raw token/header/hash/config/private key/PSK/QR/vpn URI.
11. Secret-bearing CLI values передавать через stdin/protected channel, а не через обычные command arguments.
12. Любой write route должен пройти dry-run, explicit confirmation, audit, rollback and recovery story.
13. Controlled prod readiness должен закрываться по target commit, а не по общему ощущению готовности.
14. Local Agent начинать с safe mapper/read model before routes, UI and mutation surfaces.
15. Phase closeout должен фиксировать package, tests, evidence, blocked surfaces and next gate.

## Следующая рекомендуемая работа

Не начинать новый write implementation до operator-only controlled-prod decision:

1. пройти operator-only controlled-prod readiness;
2. зафиксировать `controlled-prod-ready`, `needs-fix` или `defer-prod`;
3. новые runtime/write/API/config функции начинать только через отдельный design gate.
