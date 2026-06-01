# `amn2`: основной порядок слияния API, web panel и operations

Дата: 2026-06-01.

Режим: coordination roadmap в `VPS-OPS-LAB`. Production-код `amn2` меняется только отдельными local-gate slices. Upstream code не копируется. Live VPS не трогаем без отдельного VPS gate.

## Решение по соседним чатам

### `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`

Решение: поставить на паузу широкие research-задачи, но не закрывать источник.

Почему:

- GPL-3.0 блокирует прямое копирование кода, UI, manager-flow, Dockerfile, route layout и текстов.
- Deep-dive уже дал достаточно signal для ближайших production-gates: route taxonomy, self-service, public share, API tokens, manager contract, config delivery integrity, dangerous operations.
- Дальнейшее широкое исследование PRVTPRO сейчас будет конкурировать с переносом уже понятных безопасных foundation-срезов в `amn2`.

Что остается активным:

- точечные проверки PRVTPRO issues/UX только под конкретный `amn2` slice;
- config delivery integrity требования: `.conf`, QR, `vpn://`, Android/import compatibility;
- web-panel product patterns: endpoint grouping, self-service boundary, operator status UX, dangerous-action UX.

Что ставим на паузу:

- multi-protocol dashboard как цель для ближайшего `amn2`;
- attach existing server auto-reconcile;
- DNS/AdGuard/SOCKS/MTProxy manager flows;
- raw config editing;
- destructive server clear/install/uninstall flows.

### `VPN Ops Lab — KYORESUAS-API`

Решение: держать active as API/Local-Agent architecture reference, но не как источник кода.

Почему:

- MIT снижает license friction, но production-риск выше юридического: API управляет Docker/config/secrets/reboot.
- Самая полезная идея уже совпала с `amn2`: local-only server-side agent и route policy перед client lifecycle API.
- Нельзя переносить one shared API key, публичные `/docs`/`metrics`, backup/import/reboot и Docker socket exposure как default.

Что остается активным:

- Local Agent / controller split;
- server metadata: protocols, status, capacity/load;
- client lifecycle language: active/disabled/expiresAt;
- warning list для backup/import/reboot/destructive endpoints.

Что ставим на паузу:

- установка `kyoresuas/amnezia-api` на production VPS;
- копирование Node/Fastify implementation;
- полноценный `/clients` CRUD до policy, secret и remote-write gates.

## Критически важные задачи

## Двухконтурная проверка: local gate и live VPS gate

С этого момента каждый `amn2` slice разделяется на два контура проверки.

### Local gate

Можно делать локально без live VPS:

- policy/inventory-only registry;
- redaction coverage;
- config delivery artifact tests: `.conf`, QR decode, `vpn://` round-trip;
- web/bot/TestClient smoke tests;
- Local Agent read-only/auth/token tests на fake/local runtime;
- remote operation contract tests на fake SSH/client;
- docs/status/backlog updates;
- UI wording/confirmation tests без изменения apply/revoke logic.

Local gate считается достаточным, если slice:

- не добавляет новый live write flow;
- не меняет peer apply/revoke;
- не меняет peer sync classification;
- не меняет config template/defaults;
- не меняет IP allocation;
- не меняет Docker runtime write/restart behavior.

### Live VPS gate

Проверка на реальном VPS нужна отдельно и только после local green, если slice меняет или включает:

- approve/apply peer;
- revoke/delete/disable/enable peer;
- add missing local device to server;
- remove unknown remote peer;
- peer sync classification;
- config template/defaults, которые попадают в рабочий client config;
- Docker AmneziaWG write/reload/restart behavior;
- server connection/runtime settings;
- Local Agent deployment на VPS или controller-to-agent calls к реальному host.

Live VPS gate должен быть отдельным этапом с зафиксированными командами, expected result и rollback note. Он не смешивается с обычным локальным commit.

### 1. Зафиксировать lab baseline

Статус: current.

Состав:

- `research/amn2/api-readiness-audit-after-live-baseline.md`
- `research/amn2/route-policy-matrix.md`
- `research/amn2/secret-surface-inventory.md`
- `research/amn2/remote-operations-inventory.md`
- `research/amn2/transfer-backlog.md`
- этот roadmap

Цель: чтобы следующий production plan не спорил с соседними чатами и verified live baseline.

### 2. Route/Auth/Operation Policy Matrix как первый production slice

Статус: first implementation candidate.

Правило: не добавлять новые API routes. Сначала сделать machine-checkable policy coverage для текущих surfaces.

Входит:

- web-admin routes: auth, users, servers, health, config/email delivery;
- public-token routes: email verify/recover;
- Telegram bot surfaces: admin/user config, approve, revoke/reset;
- Local Agent first-slice routes;
- CLI/remote operation classes.

Не входит:

- new `/api/*`;
- Local Agent clients/configs;
- public/self-service download;
- backup/import/reboot;
- remote-state-write runner expansion.

### 3. Secret/redaction coverage

Статус: implemented-pushed-local-gate-complete.

Цель: перед любыми API/web panel выдачами доказать, что `.conf`, QR, `vpn://`, raw tokens, token hashes, Local Agent token, command stdout/stderr и diagnostics не попадают в logs/audit/errors.

Gate: local-only. Live VPS не нужен, пока не меняется delivery/apply runtime behavior.

Production evidence:

- branch: `codex-vps-test-prep`;
- commits: `75c235a`..`94ad807`;
- focused tests: `61 passed, 1 StarletteDeprecationWarning`;
- full local suite: `528 passed, 1 StarletteDeprecationWarning`.

### 4. Config delivery integrity

Статус: implemented-pushed-local-gate-complete.

Цель: взять лучшее из PRVTPRO web-panel темы не как UI-копию, а как test/product contract:

- `.conf` byte-level UTF-8;
- QR decode equals expected payload;
- `vpn://` decode round-trip;
- non-ASCII names;
- no secret in audit/logs;
- единый export/result contract для будущих delivery surfaces.

Gate: сначала local-only. Live VPS нужен только если меняются реальные templates/defaults, которые попадут в client config на сервере.

Production evidence:

- branch: `codex-vps-test-prep`;
- existing integrity commits: `952cc49`, `4b19cd3`;
- redaction integration commit: `fc73929`;
- verified at head: `94ad807`;
- targeted tests: `16 passed`;
- full local suite: `528 passed, 1 StarletteDeprecationWarning`.

### 5. Public-token safety

Статус: implemented-pushed-local-gate-complete.

Цель: перед любыми self-service/public config links закрепить безопасный контракт публичных verify/recover кодов:

- positive TTL guard;
- hash-only storage/lookup;
- strict purpose separation между `verify_email` и `recover_config`;
- one-time/expired rejection;
- generic denial без echo сырого token;
- failed wrong-purpose/expired attempts не consume токен.

Gate: local-only. Live VPS не нужен, потому что slice не меняет peer apply/revoke/config/sync/runtime behavior.

Production evidence:

- branch: `codex-vps-test-prep`;
- commit: `dfe27ee Harden public email token safety`;
- focused tests: `14 passed, 1 StarletteDeprecationWarning`;
- full local suite: `535 passed, 1 StarletteDeprecationWarning`.

После public-token safety выполнены remote operation dry-run/audit local slice, Local Agent hardening, Web Panel Safe Improvements, Scoped API Token Storage, Manager Config Export Contract, Public/Self-service Config Delivery Policy, Backup/Import Policy Contract и Secret Inventory Registry. Следующий рекомендуемый шаг - controlled real VPS verification gate для `codex/remote-operation-vps-gate-prep` по `research/amn2/vps-gate-remote-operation-dry-run-audit.md`, потому что KYORESUAS/PRVTPRO integration candidates уже ждут реального VPS evidence.

## Важные задачи

### 6. Web panel safe improvements

Статус: implemented-pushed-local-gate-complete.

Порядок web-panel доработок:

1. Улучшить policy/test coverage существующей web panel, не меняя UX.
2. Улучшить operator status UX вокруг server health и working configs.
3. Уточнить config delivery UI language: `.conf`, QR, `vpn://` как secret-bearing artifacts.
4. Добавить safer dangerous-action wording/confirmation только для уже существующих state-changing actions.
5. OpenAPI/domain grouping позже, когда будет стабильная API surface.

Gate: local-only для wording/status/confirmation/UI tests. Live VPS нужен только если меняется apply/revoke/sync/config behavior.

Production evidence:

- branch: `codex-vps-test-prep`;
- commit: `22dfc37 Clarify web panel operation gates`;
- RED slice tests: `4 failed as expected`;
- focused slice tests: `4 passed, 1 StarletteDeprecationWarning`;
- focused web/security suite: `75 passed, 1 StarletteDeprecationWarning`;
- full local suite: `536 passed, 1 StarletteDeprecationWarning`.

Итог: server health и peer sync получили явные read-only labels, add missing local device confirmation стал VPS-gate aware, config templates page помечает `.conf`/QR/`vpn://` как secret-bearing artifacts, dangerous user/device confirmations уточняют local DB changes и live VPS writes only when `VPS_APPLY_ENABLED=true`.

Не начинать с:

- новой большой панели;
- self-service portal;
- public share links;
- multi-protocol dashboard.

### 7. Local Agent hardening

Статус: implemented-pushed-local-gate-complete; foundation уже merged в `amn2`, расширять осторожно.

Следующие безопасные шаги:

- unified production audit sink для allowed read routes - выполнено;
- version/runtime compatibility response - выполнено;
- public-safe runtime metadata - закреплено на текущем first-slice contract;
- token rotation/revoke design - подготовлен в `research/amn2/api-token-rotation-revoke-policy.md`; следующий шаг только route-connected lifecycle gate.

Production evidence:

- branch: `codex-vps-test-prep`;
- commit: `c5d7eb6 Harden Local Agent audit contract`;
- focused tests: `64 passed, 1 StarletteDeprecationWarning`;
- full local suite: `536 passed, 1 StarletteDeprecationWarning`.

Gate: local-only для auth/token/audit/runtime metadata tests. Live VPS нужен только перед реальным agent deployment или controller-to-agent calls на VPS.

Отложить:

- `GET /agent/clients`;
- `GET /agent/configs/{id}`;
- write lifecycle;
- backup/import/reboot.

### 8. Scoped API tokens

Статус: implemented-pushed-local-gate-complete для storage/auth contract; routes еще не добавлены.

Первый production slice:

- `server:read`;
- `metrics:read`;
- hash-only storage;
- one-time raw token issue metadata;
- expiry;
- revoke;
- safe audit metadata.

Запрещено в первом slice:

- `/api/*` routes;
- `config:read` до отдельного secret-read gate;
- write/destructive scopes;
- copied upstream token implementation.

Production evidence:

- branch: `codex-vps-test-prep`;
- commit: `1fdcde5 Add scoped API token storage contract`;
- RED tests: `1 import error as expected`;
- focused slice tests: `6 passed`;
- focused security/db/services suite: `54 passed`;
- full local suite: `542 passed, 1 StarletteDeprecationWarning`.

Gate: local-only. Live VPS не нужен, потому что slice не добавляет routes и не меняет peer apply/revoke/config/sync/runtime behavior.

### 9. Remote operation partial-failure contract

Статус: fresh VPS-gate candidate подготовлен и запушен; live VPS gate еще не запускался.

Выполнено локально:

- state-changing metadata contract: `codex/remote-operation-contract-metadata`, commit `57d484d`;
- approve/reset partial-failure model: `codex/remote-operation-partial-failure`, commit `0afb22a`;
- dry-run/audit metadata: историческая branch `codex/remote-operation-dry-run-audit`, commits `0313857`, `063b6c3`;
- fresh candidate поверх текущего `codex-vps-test-prep`: `codex/remote-operation-vps-gate-prep`, head `aca6663`;
- VPS gate runbook: `research/amn2/vps-gate-remote-operation-dry-run-audit.md`;
- full local suite для fresh candidate: `551 passed, 1 StarletteDeprecationWarning`.

Остается перед broader remote-state-write API:

- before/after audit;
- idempotency key или replay policy;
- resume flow;
- no secret-bearing CLI args;
- shared read-only telemetry command policy.

Gate: local-only срезы закрыли contract/partial-failure/dry-run основу. Следующий шаг - controlled real VPS verification gate на тестовом peer/device по ветке `codex/remote-operation-vps-gate-prep` перед включением broader remote-state-write в web/API/agent flow.

## Простые задачи

- Обновлять AMN3 status/backlog после каждого production slice.
- Держать manual source links на PRVTPRO/KYORESUAS как research sources.
- Перед каждым `amn2` plan явно писать: нужен ли live retest.
- Синхронизировать docs с committed branch/commit/test evidence.
- Сократить повторяющиеся handoff-фразы после стабилизации roadmap.

## Косметические задачи

- Naming cleanup: AMN3, VPS Ops Lab, `amn2`, Amneziya, future hybrid.
- Русский-first docs, English only for code/API terms.
- OpenAPI grouping как operator/developer UX.
- Dangerous action UX labels.
- UI wording для secret-bearing artifacts.

## Что переносим из PRVTPRO и KYORESUAS в `amn2`

Переносим как самостоятельные требования:

- route taxonomy and policy matrix;
- separate admin/user/public-token surfaces;
- hash-only tokens with one-time raw display;
- scoped tokens, expiry, revoke, owner inheritance;
- config delivery integrity for `.conf`, QR, `vpn://`;
- manager/export contract idea;
- dangerous operation risk classes;
- local-only API agent;
- client lifecycle vocabulary: active, disabled, expiresAt;
- server status/capacity metadata.

Не переносим:

- PRVTPRO GPL code/UI/templates/managers/scripts;
- KYORESUAS Node/Fastify implementation;
- one broad shared API key;
- public docs/metrics as default;
- direct backup/import/reboot endpoints;
- raw config editing;
- remote install/clear/uninstall flows before runner/job model.

## Recommended merge order

### Local-only merge lane

1. Policy matrix: done, local-gate-complete.
2. Redaction coverage: done, local-gate-complete.
3. Config delivery integrity: done, local-gate-complete.
4. Public-token safety: done, local-gate-complete.
5. Remote operation contract/partial-failure/dry-run metadata: done, local-gate-complete.
6. Local Agent read-only/audit/versioning hardening: done, local-gate-complete.
7. Web panel safe improvements: done, local-gate-complete.
8. Scoped API token storage/auth contract: done, local-gate-complete.
9. Manager config export contract: done in `amn2/codex/manager-config-export-contract`, local-gate-complete.
10. Public/self-service config delivery policy: done in `amn2/codex/public-config-delivery-policy-contract`, local-gate-complete.
11. Backup/import policy contract: done in `amn2/codex/backup-import-policy-contract`, local-gate-complete.
12. Secret inventory registry: done in `amn2/codex/secret-inventory-registry`, local-gate-complete.
13. Read-only metrics privacy classification: prepared in `research/amn2/read-only-metrics-privacy-classification.md`; implementation route shell still waits for VPS evidence.

### Live VPS verification lane

1. Enter this lane now if the goal is to unblock KYORESUAS/PRVTPRO integration decisions; the local API-token storage slice is complete.
2. Treat SSH host key verification as Phase 0 evidence using `research/amn2/ssh-host-key-enrollment-design.md`; if an unknown host key prompt appears, stop and verify out-of-band before continuing.
3. Use the prepared VPS test checklist `research/amn2/vps-gate-remote-operation-dry-run-audit.md` with branch/commit, commands, expected state and rollback note.
4. For `codex/remote-operation-vps-gate-prep`, start with read-only check and dry-run apply/revoke preview; single test peer apply/revoke needs separate operator confirmation.
5. Verify approve/apply, config import, working configs, peer sync, disable/enable/delete and Docker runtime behavior if touched.
6. Record VPS evidence in `research/amn2/vps-gate-evidence-checklist.md` before marking the slice `verified-live`.
7. Use `research/amn2/post-vps-gate-merge-decision.md` for merge/PR decision.
8. Do not use live VPS testing as a substitute for local policy/secret/operation tests.

### SSH host key enrollment lane

1. Design is prepared in `research/amn2/ssh-host-key-enrollment-design.md`.
2. Local-only SSH host key identity verifier implemented in `amn2/codex/ssh-host-key-identity-verifier`, commit `dd20364`: parse public host key lines, compute SHA256 fingerprints, verify match/mismatch with tests and document operator verification.
3. Next implementation should connect the verifier to SSH-backed operations as a separate gated slice.
4. Production live mode must not rely on `StrictHostKeyChecking=accept-new`; missing/mismatched pins block SSH-backed operations.

### Route/Auth machine-checkable tests lane

1. Next-gate plan is prepared in `research/amn2/route-auth-machine-checkable-tests-plan.md`.
2. First implementation should be local-only binding/drift tests over current `app/security/surface_policy.py`: web route coverage, bot action manifest, Local Agent parity, CLI/remote operation bindings and test-ref integrity.
3. No route expansion, route middleware enforcement, public config download, API `config:read` or live VPS calls belong in this slice.

### Backup/import dangerous API lane

1. Design is prepared in `research/amn2/backup-import-dangerous-api-design.md`.
2. First implementation is complete in `amn2/codex/backup-import-policy-contract`, head `afb2702` with foundation commit `d2c160b`: local-only policy registry plus restore/import preview contract, metadata export, redacted backup, encrypted full backup as explicit dangerous mode, and no target write during preview.
3. Verification: focused backup/security suite `61 passed`; full local suite `584 passed, 1 StarletteDeprecationWarning`.
4. Web/API full backup, restore apply and import apply remain blocked until route policy, secret inventory, confirmation, audit and backup-before-write gates exist.

### Manager config export contract lane

1. Design is prepared in `research/amn2/manager-config-export-contract.md`.
2. First implementation is complete in `amn2/codex/manager-config-export-contract`, commit `4d4e7a4`: local-only typed request/result/artifact objects plus an adapter from current `DeviceConfigDelivery`/`ConfigDeliveryPackage`.
3. Verification: focused config/security/delivery suite `40 passed`; full local suite `560 passed, 1 StarletteDeprecationWarning`.
4. Public/self-service config endpoints, API `config:read` and Local Agent `/configs` remain blocked until route policy, ownership/token lifecycle, audit and redaction tests exist.

### Public/self-service config delivery policy lane

1. Policy is prepared in `research/amn2/public-self-service-config-delivery-policy.md`.
2. First implementation is complete in `amn2/codex/public-config-delivery-policy-contract`, commit `2ef3af7`: no-route policy registry/share-token contract, hash-only raw token discipline, expiry, one-time/max-download, revoke cascade, audit-safe metadata and backup/restore policy tests.
3. Verification: focused config/token/security/db suite `94 passed`; full local suite `577 passed, 1 StarletteDeprecationWarning`.
4. Public download routes, self-service config download, API `config:read` and Local Agent `/configs` remain blocked until a separate route-exposure gate is implemented and verified.

### Read-only metrics/API lane

1. Privacy classification is prepared in `research/amn2/read-only-metrics-privacy-classification.md`.
2. First implementation after `verified-live` should be aggregate-only metrics/API route shell.
3. Detailed per-peer/client metrics remain blocked until separate opt-in detailed metrics policy and tests.

### Local Agent runtime metadata lane

1. Runtime metadata alignment is prepared in `research/amn2/local-agent-runtime-metadata-alignment.md`.
2. First implementation after `verified-live` should be controller-safe runtime summary.
3. `/agent/clients`, `/agent/configs` and write lifecycle remain blocked until separate token rotation/revoke and secret-read/write gates.

### Scoped API token lifecycle lane

1. Rotation/revoke policy is prepared in `research/amn2/api-token-rotation-revoke-policy.md`.
2. Local-only lifecycle gate implemented in `amn2/codex/api-token-lifecycle-gate`, commit `c2ba646`: explicit route-connected expiry helper, idempotent revoke event, create-new-then-revoke-old rotation, owner inheritance and safe metadata.
3. Stacked variant for merge order after route/auth binding is available in `amn2/codex/api-token-lifecycle-gate-stacked`, commit `256d0c0`; stacked verification: focused `56 passed`, full suite `555 passed`.
4. Next implementation should expose only read-only route shell after VPS evidence or a separate route-exposure decision.
5. `config:read`, write, remote-exec, destructive, backup/import and broad admin-equivalent bearer tokens remain blocked.

## Recommendation

Backup/import policy registry and secret inventory registry are now complete. Next recommended work is controlled real VPS verification before integrating KYORESUAS/PRVTPRO-derived operational flows. If VPS is still unavailable, keep further work to docs/test guard slices only, such as route-level audit/rate-limit policy, and avoid route/API implementation.
