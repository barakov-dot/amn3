# Следующий чат: AMN2 Phase 4 Unified Product Gate

Дата: 2026-06-09.

Рабочая папка нового основного чата:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

Назначение: перевести основной coordination-чат в Phase 4 после закрытого Phase 3 service-mode baseline. Phase 4 не является новым live-write gate. Это единый контур для продукта, API, web-panel UX, PRVTPRO/KYORESUAS intake и подготовки следующих безопасных `amn2` slices.

## Текущая точка правды

```text
AMN3 repo: C:\Users\SooL\Documents\VPS-OPS-LAB
AMN3 remote: https://github.com/barakov-dot/amn3.git
AMN3 branch: master
AMN3 checkpoint before this Phase 4 packet: a205daa Record web panel UX review evidence

AMN2 repo: C:\Users\SooL\Documents\Amneziya
AMN2 remote: https://github.com/barakov-dot/amn2.git
AMN2 branch: codex-vps-test-prep
AMN2 source-overlay/package head: f7f6131 Update integration status for c92 manual prelaunch

target VPS mode: service-mode web/bot active, loopback-only
operator access: SSH local port forward to 127.0.0.1:3030, external browser only
web/admin bind: 127.0.0.1:3030
amneziya-web: active/enabled
amneziya-bot: active/enabled
loopback login: 200
public/direct 3030: closed by loopback bind
public API 3040: absent/closed
TCP 80/443: absent
domain/Caddy/HTTPS public cutover: deferred, no domain planned
VPS_APPLY_ENABLED: false
peer scope: two remaining approved test peers
revoked peers: Neobyatnaya-AMNZ-3, Neobyatnaya-AMNZ-4
```

Phase 3 service-mode loopback is considered closed as a baseline. Do not reopen manual-vs-service-mode as an unresolved question unless new evidence contradicts this state.

## Термины Phase 4

- `service-mode`: web/bot работают как сервисы, но это не означает public exposure.
- `loopback-only`: listener доступен только на `127.0.0.1`.
- `SSH tunnel`: единственный operator access path к private web/admin.
- `local-only`: разрешены только локальные docs/tests/templates/code changes без live VPS commands и без runtime mutation.
- `read-only`: разрешено только чтение/навигация/aggregate/status evidence; POST/write/config/sync/apply/revoke не входят.
- `requires VPS gate`: нужен отдельный named gate даже для read-only live sampling.
- `blocked until separate write/config/public gate`: нельзя выполнять в Phase 4 default mode.
- `deferred`: не выбран сейчас; может быть пересмотрен позже, но не дает permission.
- `public exposure`: public API `3040`, direct public web/admin `3030`, domain/Caddy/HTTPS cutover, public docs/metrics exposure.
- `config delivery`: `.conf`, QR, `vpn://`, generated config archives, share/download links and any secret-bearing config output.

## Что такое Phase 4

Phase 4 is the unified product/planning gate after the service-mode loopback pass:

- consolidate AMN2/API, target VPS, PRVTPRO/Web Panel and KYORESUAS/API work into one decision map;
- convert external-project ideas into candidate rows before any `amn2` implementation;
- prepare local/read-only `amn2` slices first;
- keep live mutations and public exposure behind separate named gates;
- keep the main chat from issuing ad hoc commands against the VPS.

## Текущая private/local read-only API grouping

P4-X001 closed the docs grouping polish for the existing six private/local read-only routes. This is documentation/navigation only, not public OpenAPI/docs exposure and not route expansion.

| Group | Route | Scope | Boundary |
| --- | --- | --- | --- |
| Server inventory/status | `GET /api/servers` | `server:read` | server list/status metadata only |
| Server inventory/status | `GET /api/servers/{server_name}/summary` | `server:read` | aggregate server/user/device summary only |
| Integration/service boundary | `GET /api/integration/status` | `server:read` | service-mode/read-only/API/token-boundary status only |
| Local Agent runtime summary | `GET /api/local-agent/runtime/summary` | `server:read` | controller-safe Local Agent runtime summary only |
| Aggregate metrics | `GET /api/metrics/summary` | `metrics:read` | aggregate metrics only, no peer/user detail leakage |
| Aggregate metrics | `GET /api/users/summary` | `metrics:read` | aggregate user/device counts only |

## Что Phase 4 не разрешает

Phase 4 does not authorize:

- `VPS_APPLY_ENABLED=true`;
- public API `3040`;
- direct public web/admin `3030`;
- Caddy/nginx/HTTPS public cutover;
- production peer/user mutation beyond the two approved test peers;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- secret-bearing evidence publication.

Any item above requires a separate explicit gate, safe summary and rollback/recovery note.

## Новый этап P4-NG

`P4-NG` starts after the default local-only Phase 4 queue was closed. It is the Named Gate / Write API Readiness stage.

Docs:

- plan: `docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md`;
- charter/evidence: `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md`;
- write API live-block evidence: `research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md`;
- write API threat model evidence: `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`;
- write API route taxonomy evidence: `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`;
- local fake-runner contract evidence: `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`.
- idempotency/locking/partial-failure model evidence: `research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md`.
- write API audit/redaction requirements evidence: `research/amn2/phase-4-wapi-v005-write-api-audit-redaction-requirements-2026-06-10.md`.
- operation status model evidence: `research/amn2/phase-4-wapi-i004-operation-status-model-2026-06-10.md`.
- scoped write-token model evidence: `research/amn2/phase-4-wapi-i003-scoped-write-token-model-2026-06-10.md`.
- config delivery decoupling evidence: `research/amn2/phase-4-wapi-i002-config-delivery-decoupling-2026-06-10.md`.
- `/api/clients` design evidence: `research/amn2/phase-4-wapi-i001-clients-design-without-live-crud-2026-06-10.md`.
- web-panel gated action labels evidence: `research/amn2/phase-4-wapi-i005-web-panel-gated-action-labels-2026-06-10.md`.
- stale wording cleanup evidence: `research/amn2/phase-4-ng-x003-stale-wording-cleanup-2026-06-10.md`.
- gate naming consistency evidence: `research/amn2/phase-4-ng-x001-gate-naming-consistency-2026-06-10.md`.
- Russian-first operator wording evidence: `research/amn2/phase-4-ng-x002-russian-first-operator-wording-polish-2026-06-10.md`.
- Codex Security VPS risk checkpoint evidence: `research/amn2/phase-4-ng-sc001-codex-security-vps-risk-checkpoint-2026-06-10.md`.
- NG-V001 read-only VPS baseline gate opening evidence: `research/amn2/phase-4-ng-v001-read-only-vps-baseline-gate-2026-06-10.md`.

Closed in or alongside this stage:

- `NG-C001` named gate charter;
- `NG-C002` safety boundary restatement.
- `NG-C003` secrets policy for gate outputs;
- `NG-C004` go/no-go format for all gates;
- `NG-S003` reusable named-gate evidence template;
- `NG-C005` write API live-block assertion;
- `WAPI-V001` write API threat model;
- `WAPI-V002` write API route taxonomy;
- `WAPI-V003` local fake-runner contract;
- `WAPI-V004` idempotency, locking and partial-failure model;
- `WAPI-V005` write API audit/redaction requirements;
- `WAPI-I004` operation status model;
- `WAPI-I003` scoped write-token model;
- `WAPI-I002` config delivery decoupling;
- `WAPI-I001` `/api/clients` design without live CRUD;
- `WAPI-I005` web-panel gated action labels;
- `NG-N003` operation queue design after write API contract;
- `NG-N002` health/status polling design;
- `NG-N001` attach-existing-server read-only reconciliation gate design;
- `NG-N004` candidate registry update after every gate decision;
- `NG-S001` status/transfer synchronization;
- `NG-S002` next-chat handoff synchronization;
- `NG-S004` visible active plan maintenance;
- `NG-X003` stale wording cleanup;
- `NG-X001` gate naming consistency;
- `NG-X002` Russian-first operator wording polish;
- `NG-SC001` Codex Security VPS risk checkpoint;
- `P4-PRVTPRO-REFRESH-004` API taxonomy/OpenAPI grouping policy support.

Следующее решение:

- очередь default docs-only cosmetic закрыта;
- `NG-V001` read-only VPS baseline gate закрыт как `go`;
- активных P4-NG задач больше нет.

`NG-V001` does not authorize adjacent live/write/config/public/destructive work. Write API live work remains blocked until a separate `P4-NG-WRITE-API-LIVE-GATE`; destructive VPS rebuild is now tracked by separate `VPS-REBUILD-001` and remains blocked until final destructive approval; selected WAPI work remains docs-only/local-only with `live_write_authorized: no`.

## Обязательное чтение

Start with:

```text
docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md
research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md
research/amn2/transfer-backlog.md
research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md
research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md
```

Historical Phase 3 evidence is linked from `docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md`; do not paste full logs or secret-bearing runtime files into the new chat.

## Рабочие линии Phase 4

### Линия A. Status и handoff

Разрешено:

- docs/status/backlog updates in AMN3;
- safe summaries only;
- one-copy context packet for the main chat;
- cross-linking PRVTPRO/KYORESUAS/AMN2 evidence.

Закрыто:

- live VPS commands;
- new package apply;
- new peer write operation;
- secret-bearing artifacts.

### Линия B. Web Panel UX/Product Review

Разрешено:

- read-only review through SSH tunnel;
- page labels, navigation, empty states, warnings and safety copy;
- candidate rows for local UI wording/navigation improvements;
- local tests and docs for safe read-only improvements.

Текущее evidence:

```text
review_status: ok
routes_reviewed: ok
authenticated_overview_ok: ok
write_actions_called: no
config_delivery_requested: no
api_token_issue_revoke_called: no
sync_or_health_actions_called: no
backup_import_reboot_called: no
secrets_published: no
result: passed-minimal-safe-summary
```

Важное ограничение: детальные page-by-page UX findings не были возвращены. `P4-I001` was later closed as not needed now; do not reopen a second UX pass by default. If future page-level evidence becomes necessary, create a fresh explicit decision/gate first and use `docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_EVIDENCE_TEMPLATE.ru.md`.

### Линия C. PRVTPRO и KYORESUAS candidate intake

Перед любой работой в `amn2` использовать такой формат candidate row:

```text
candidate_id:
source:
feature_area:
user_value:
AMN2_fit:
license_boundary:
risk_class:
secret_surface:
remote_write_surface:
test_plan:
required_gate:
recommendation: accept | defer | reject | research
```

Базовые границы:

- PRVTPRO/Amnezia-Web-Panel is GPL-3.0: research-only, no code/UI/templates/scripts/managers copied.
- PRVTPRO refresh 2026-06-10 AMN2 order: `P4-PRVTPRO-REFRESH-002` expiration-field contract tests and `P4-PRVTPRO-REFRESH-001` read-only About/Version/Build status are closed and merged into AMN2 `codex-vps-test-prep` at `1508e3c4a100b76815b29f91757290f1266f813d`; `P4-PRVTPRO-REFRESH-004` API taxonomy/OpenAPI grouping is closed as AMN3 docs-only policy support in `research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md`; remaining PRVTPRO-derived order is `P4-PRVTPRO-REFRESH-003` read-only server status/latency UX only after design boundary.
- PRVTPRO hybrid-only backlog: `HYB-PRVTPRO-REFRESH-001` AdGuard Home integration, `HYB-PRVTPRO-REFRESH-002` SOCKS5 service manager, `HYB-PRVTPRO-REFRESH-003` Xray migration/attach existing install, `HYB-PRVTPRO-REFRESH-004` multi-protocol capability registry.
- PRVTPRO negative controls: do not transfer upstream Bearer-token model as admin-equivalent access to all admin endpoints; do not open public panel, config delivery, reboot, backup, import or server cleanup without a separate named gate.
- KYORESUAS/API is used as product/architecture signal: own AMN2 implementation, no direct production install.
- Any secret-bearing config delivery, write API or remote mutation candidate stays blocked until a named gate exists.

### Линия D. Подготовка AMN2 local/read-only slices

Default local-only implementation queue is closed after `P4-I001` closure. Safe work in this line is now limited to explicit `P4-NG` planning or a newly approved local-only design slice.

Безопасные next actions:

- очередь default docs-only cosmetic закрыта;
- `P4-PRVTPRO-REFRESH-003` design boundary only, before any server status/latency UX implementation;
- docs-only write API design after explicit selection and threat model alignment;
- candidate registry maintenance for PRVTPRO/KYORESUAS ideas;
- route/auth/secret policy checks before future route expansion.

Не запускать live operations из этой линии. Если выбран `amn2` code change, создать отдельную ветку/план в repo `amn2` и держать первый slice local/read-only, если отдельно не утверждено другое.

### Линия E. Будущие live gates

Открывать отдельный named gate только когда Phase 4 выбирает live operation. Gate должен включать:

```text
gate_name:
target_vps:
operation_class:
allowed_actions:
blocked_actions:
preflight:
rollback:
safe_summary_fields:
secrets_policy:
go_no_go_decision:
```

Примеры, для которых нужен отдельный gate:

- production peer apply/revoke;
- public HTTPS reverse proxy;
- public API exposure;
- config delivery expansion;
- Local Agent deployment/mutations;
- backup/import/reboot.

## Текущие шаги Phase 4

1. Confirm this Phase 4 handoff is the main chat entry point.
2. Keep target VPS unchanged: web/bot active, web/admin loopback-only, SSH tunnel access only.
3. Treat `P4-C009` web-panel user/config visibility as the completed first local-only slice; evidence: `research/amn2/phase-4-web-panel-user-config-visibility-implementation-2026-06-09.md`.
4. Treat `P4-I002` service-mode/read-only status wording as the completed second local-only slice; evidence: `research/amn2/phase-4-service-mode-status-wording-implementation-2026-06-09.md`.
5. Treat route/secret gate planning as completed docs-only; evidence: `research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md`.
6. Treat `P4-I003` read-only API/status schema maturity design as completed docs-only; evidence: `research/amn2/phase-4-read-only-api-status-design-2026-06-09.md`.
7. Treat the AMN2 local implementation plan for `P4-I003` as completed docs-only; plan: `docs/superpowers/plans/2026-06-09-amn2-p4-i003-read-only-api-status-schema.md`.
8. Treat `P4-I003` AMN2 local implementation as completed; evidence: `research/amn2/phase-4-read-only-api-status-schema-implementation-2026-06-09.md`.
9. Treat `P4-I004` endpoint taxonomy / route-policy docs alignment as completed; evidence: `research/amn2/phase-4-endpoint-taxonomy-route-policy-docs-implementation-2026-06-09.md`.
10. Treat `P4-N003` aggregate metrics privacy boundary as completed; evidence: `research/amn2/phase-4-aggregate-metrics-privacy-boundary-implementation-2026-06-09.md`.
11. Treat `P4-I005` API token lifecycle boundary as completed; evidence: `research/amn2/phase-4-api-token-lifecycle-boundary-implementation-2026-06-09.md`.
12. Treat `P4-N004` bot/admin read-only labels as completed; evidence: `research/amn2/phase-4-bot-admin-read-only-labels-implementation-2026-06-09.md`.
13. Treat `P4-N001` docs/status drift synchronization as completed; evidence: `research/amn2/phase-4-docs-status-drift-sync-2026-06-09.md`.
14. Treat `P4-N002` protocol manager interface checklist as completed; evidence: `research/amn2/phase-4-protocol-manager-interface-checklist-2026-06-09.md`.
15. Treat `P4-X003` Russian-first operator docs polish as completed; evidence: `research/amn2/phase-4-russian-first-operator-docs-polish-2026-06-09.md`.
16. Treat `P4-X002` API/status/gate naming cleanup as completed; evidence: `research/amn2/phase-4-api-status-gate-naming-cleanup-2026-06-09.md`.
17. Treat `P4-X001` read-only API docs grouping polish as completed; evidence: `research/amn2/phase-4-read-only-api-docs-grouping-polish-2026-06-09.md`.
18. Treat `P4-I001` second read-only UX pass as closed/not needed now; evidence: `research/amn2/phase-4-p4-i001-read-only-ux-pass-closure-2026-06-10.md`.
19. Treat the default local-only Phase 4 implementation queue as closed except minimal maintenance.
20. Treat `P4-NG` named gate / write API readiness charter as started docs-only; evidence: `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md`.
21. Treat `P4-PRVTPRO-REFRESH-002` expiration-field contract tests as closed; evidence: `research/amn2/phase-4-prvtpro-expiration-contract-tests-implementation-2026-06-10.md`.
22. Treat `P4-PRVTPRO-REFRESH-001` read-only About/Version/Build status as closed; evidence: `research/amn2/phase-4-prvtpro-build-status-implementation-2026-06-10.md`.
23. Treat PRVTPRO local slices merge as closed; evidence: `research/amn2/phase-4-prvtpro-local-slices-merge-2026-06-10.md`; AMN2 base head: `1508e3c4a100b76815b29f91757290f1266f813d`.
24. Treat `P4-PRVTPRO-REFRESH-004` API taxonomy/OpenAPI grouping policy support as closed; evidence: `research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md`.
25. Treat `WAPI-V002` write API route taxonomy as closed; evidence: `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`.
26. Treat `WAPI-V003` local fake-runner contract as closed; evidence: `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`.
27. Treat `WAPI-V004` idempotency, locking and partial-failure model as closed; evidence: `research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md`.
28. Treat `WAPI-V005` write API audit/redaction requirements as closed; evidence: `research/amn2/phase-4-wapi-v005-write-api-audit-redaction-requirements-2026-06-10.md`.
29. Treat `WAPI-I004` operation status model as closed; evidence: `research/amn2/phase-4-wapi-i004-operation-status-model-2026-06-10.md`.
30. Treat `WAPI-I003` scoped write-token model as closed; evidence: `research/amn2/phase-4-wapi-i003-scoped-write-token-model-2026-06-10.md`.
31. Treat `WAPI-I002` config delivery decoupling as closed; evidence: `research/amn2/phase-4-wapi-i002-config-delivery-decoupling-2026-06-10.md`.
32. Treat `WAPI-I001` `/api/clients` design without live CRUD as closed; evidence: `research/amn2/phase-4-wapi-i001-clients-design-without-live-crud-2026-06-10.md`.
33. Treat `WAPI-I005` web-panel gated action labels as closed; evidence: `research/amn2/phase-4-wapi-i005-web-panel-gated-action-labels-2026-06-10.md`.
34. Treat `NG-N003` operation queue design after write API contract as closed; evidence: `research/amn2/phase-4-ng-n003-operation-queue-design-2026-06-10.md`.
35. Treat `NG-N002` health/status polling design as closed; evidence: `research/amn2/phase-4-ng-n002-health-status-polling-design-2026-06-10.md`.
36. Treat `NG-N001` attach-existing-server read-only reconciliation gate design as closed; evidence: `research/amn2/phase-4-ng-n001-attach-existing-server-read-only-reconciliation-gate-design-2026-06-10.md`.
37. Treat `NG-N004` candidate registry update after every gate decision as closed; evidence: `research/amn2/phase-4-ng-n004-candidate-registry-update-2026-06-10.md`.
38. Treat `NG-S001` status/transfer synchronization as closed; evidence: `research/amn2/phase-4-ng-s001-status-transfer-sync-2026-06-10.md`.
39. Treat `NG-S002` next-chat handoff synchronization as closed; evidence: `research/amn2/phase-4-ng-s002-next-chat-handoff-sync-2026-06-10.md`.
40. Treat `NG-S004` visible active plan maintenance as closed; evidence: `research/amn2/phase-4-ng-s004-visible-active-plan-maintenance-2026-06-10.md`.
41. Treat `NG-X003` stale wording cleanup as closed; evidence: `research/amn2/phase-4-ng-x003-stale-wording-cleanup-2026-06-10.md`.
42. Treat `NG-X001` gate naming consistency as closed; evidence: `research/amn2/phase-4-ng-x001-gate-naming-consistency-2026-06-10.md`.
43. Treat `NG-X002` Russian-first operator wording polish as closed; evidence: `research/amn2/phase-4-ng-x002-russian-first-operator-wording-polish-2026-06-10.md`.
44. Treat `NG-SC001` Codex Security VPS risk checkpoint as closed; evidence: `research/amn2/phase-4-ng-sc001-codex-security-vps-risk-checkpoint-2026-06-10.md`.
45. Treat `NG-V001` read-only VPS baseline gate as closed/go; evidence: `research/amn2/phase-4-ng-v001-read-only-vps-baseline-gate-2026-06-10.md`.
46. If a live/public/write/config/destructive action is proposed outside the allowed NG-V001 read-only scope, stop and create a separate named gate first.

## Сообщение для копирования в основной чат

```text
Работаем в C:\Users\SooL\Documents\VPS-OPS-LAB.

Новый этап: AMN2 Phase 4 Unified Product Gate.

Сначала прочитай:
- docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/PROJECT_CONTEXT_IMPORT.ru.md
- docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
- docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md
- research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md
- research/amn2/transfer-backlog.md
- research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md

Текущая точка:
- AMN2 source-overlay/package head: f7f6131
- AMN3 checkpoint before Phase 4 packet: a205daa
- target VPS: service-mode web/bot active, web/admin только 127.0.0.1:3030
- operator access: SSH tunnel + внешний browser
- public/direct 3030: closed by loopback bind
- public API 3040: absent/closed
- TCP 80/443: absent
- domain/Caddy/HTTPS public cutover: отсутствует и не планируется
- VPS_APPLY_ENABLED=false
- оставшиеся approved test peers: Neobyatnaya-AMNZ-1 и Neobyatnaya-AMNZ-2
- Neobyatnaya-AMNZ-3 и Neobyatnaya-AMNZ-4 revoked

Задача Phase 4:
1. Не повторять Phase 3 как незакрытый вопрос.
2. Свести AMN2/API, target VPS, PRVTPRO/Web Panel и KYORESUAS/API в одну decision map.
3. Готовить только local/read-only slices по умолчанию.
4. PRVTPRO/KYORESUAS идеи заносить как candidate rows, не переносить код напрямую.
5. Любой public API, direct public web/admin, HTTPS reverse proxy, config delivery, write CRUD, Local Agent mutation, backup/import/reboot или production peer mutation запускать только отдельным named gate.

Не публиковать:
.env, servers.yml, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, .conf, QR, vpn://, backup contents, session cookies, public endpoint values или full logs.

Закрытый первый slice:
- P4-C009 web-panel user/config visibility, local-only.

Закрытый второй slice:
- P4-I002 service-mode/read-only status wording, local-only.

Закрытый route/secret planning:
- research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md

Закрытый P4-I003 design:
- research/amn2/phase-4-read-only-api-status-design-2026-06-09.md

Закрытый P4-I003 implementation plan:
- docs/superpowers/plans/2026-06-09-amn2-p4-i003-read-only-api-status-schema.md

Закрытый P4-I003 implementation:
- research/amn2/phase-4-read-only-api-status-schema-implementation-2026-06-09.md

Закрытый P4-I004 endpoint taxonomy:
- research/amn2/phase-4-endpoint-taxonomy-route-policy-docs-implementation-2026-06-09.md

Закрытый P4-N003 aggregate metrics privacy boundary:
- research/amn2/phase-4-aggregate-metrics-privacy-boundary-implementation-2026-06-09.md

Закрытый P4-I005 API token lifecycle boundary:
- research/amn2/phase-4-api-token-lifecycle-boundary-implementation-2026-06-09.md

Закрытый P4-N004 bot/admin read-only labels:
- research/amn2/phase-4-bot-admin-read-only-labels-implementation-2026-06-09.md

Закрытый P4-N001 docs/status drift synchronization:
- research/amn2/phase-4-docs-status-drift-sync-2026-06-09.md

Закрытый P4-N002 protocol manager interface checklist:
- research/amn2/phase-4-protocol-manager-interface-checklist-2026-06-09.md

Закрытый P4-X003 Russian-first operator docs polish:
- research/amn2/phase-4-russian-first-operator-docs-polish-2026-06-09.md

Закрытый P4-X002 API/status/gate naming cleanup:
- research/amn2/phase-4-api-status-gate-naming-cleanup-2026-06-09.md

Закрытый P4-X001 read-only API docs grouping polish:
- research/amn2/phase-4-read-only-api-docs-grouping-polish-2026-06-09.md

Закрытый P4-I001 second read-only UX pass decision:
- research/amn2/phase-4-p4-i001-read-only-ux-pass-closure-2026-06-10.md
- second UX pass was not run; operator decision is to close it as not needed now.

Закрытый WAPI-I002 config delivery decoupling:
- research/amn2/phase-4-wapi-i002-config-delivery-decoupling-2026-06-10.md
- client/peer creation must not return `.conf`, QR, `vpn://`, archives, share/download links or other secret-bearing config artifacts.

Закрытый WAPI-I001 /api/clients design without live CRUD:
- research/amn2/phase-4-wapi-i001-clients-design-without-live-crud-2026-06-10.md
- candidate `/api/clients` routes remain planning placeholders only; no runtime CRUD, config delivery or live peer mutation is authorized.

Закрытый WAPI-I005 web-panel gated action labels:
- research/amn2/phase-4-wapi-i005-web-panel-gated-action-labels-2026-06-10.md
- future panel labels must distinguish read-only metadata, local planning, dry-run, blocked named gates, config delivery blocks and live-write blocks without changing behavior.

Закрытый NG-N003 operation queue design:
- research/amn2/phase-4-ng-n003-operation-queue-design-2026-06-10.md
- future queue/cancel/retry/status semantics remain docs-only; no queue implementation, worker, runtime route, live write or config delivery is authorized.

Закрытый NG-N002 health/status polling design:
- research/amn2/phase-4-ng-n002-health-status-polling-design-2026-06-10.md
- future polling remains aggregate-only and stale-aware; no scheduler, collector, runtime route, live target polling, peer/user leakage or write/config action is authorized.

Закрытый NG-N001 attach-existing-server reconciliation design:
- research/amn2/phase-4-ng-n001-attach-existing-server-read-only-reconciliation-gate-design-2026-06-10.md
- future reconciliation remains report-only; no attach, import, backfill, real target detection, route change, live write or config delivery is authorized.

Закрытый NG-N004 candidate registry update:
- research/amn2/phase-4-ng-n004-candidate-registry-update-2026-06-10.md
- candidate registry now links P4-N006 to NG-N003, P4-I007 to NG-N002 and P4-N005 to NG-N001 while keeping implementation/live/write/config gates closed.

Закрытый NG-S001 status/transfer synchronization:
- research/amn2/phase-4-ng-s001-status-transfer-sync-2026-06-10.md
- PROJECT_STATUS_CURRENT and transfer-backlog are current after the closed normal P4-NG queue.

Закрытые NG-S002 / NG-S004:
- research/amn2/phase-4-ng-s002-next-chat-handoff-sync-2026-06-10.md
- research/amn2/phase-4-ng-s004-visible-active-plan-maintenance-2026-06-10.md
- next-chat packet and visible active plan are current; no simple docs-only tasks remain active.

Закрытый NG-X003 stale wording cleanup:
- research/amn2/phase-4-ng-x003-stale-wording-cleanup-2026-06-10.md
- stale active-next wording cleaned up; NG-X003 is no longer an active recommendation.

Закрытый NG-X001 gate naming consistency:
- research/amn2/phase-4-ng-x001-gate-naming-consistency-2026-06-10.md
- stage-level gate labels now use P4-NG-*; no live/write/config/public authorization was added.

Закрытый NG-X002 Russian-first operator wording polish:
- research/amn2/phase-4-ng-x002-russian-first-operator-wording-polish-2026-06-10.md
- active P4-NG operator-facing headings and next-step wording are Russian-first; technical ids/routes/gate names were not changed.

Закрытый NG-SC001 Codex Security VPS risk checkpoint:
- research/amn2/phase-4-ng-sc001-codex-security-vps-risk-checkpoint-2026-06-10.md
- Codex Security threat-model checkpoint is now required before NG-V001 or any future destructive VPS rebuild gate; it does not authorize SSH, live commands, reinstall/rebuild, public exposure, write/config actions or production mutation.

Закрытый NG-V001 read-only VPS baseline gate:
- research/amn2/phase-4-ng-v001-read-only-vps-baseline-gate-2026-06-10.md
- status: closed-go; SSH transport ok, web/bot active/enabled, loopback login 200, 3030 loopback-only, 3040/80/443 absent, VPS_APPLY_ENABLED=false, no secret-bearing evidence.

Открытый VPS-REBUILD-001 fresh VPS rebuild gate:
- research/amn2/vps-rebuild-001-fresh-vps-rebuild-gate-2026-06-10.md
- plan: docs/superpowers/plans/2026-06-10-vps-rebuild-001-fresh-vps-rebuild.md
- status: opened-defer-awaiting-final-destructive-approval; security_risk_decision=defer; go_no_go_decision=defer.
- novice-safe preflight: preserve provider snapshot first, precheck AMN2 source/package locally, regenerate target secrets where possible, pass external secrets only through operator local channel.
- source/package precheck: research/amn2/vps-rebuild-001-source-package-precheck-2026-06-10.md; source candidate `1508e3c4a100b76815b29f91757290f1266f813d`; focused local tests `30 passed, 1 warning`.
- package build/hygiene: research/amn2/vps-rebuild-001-package-build-hygiene-2026-06-10.md; package `dist/amn2-vps-update-and-smoke-kit-1508e3c.zip`, sha256 `03C51891AF83B9BD2B435AF5F77EEBBAE0DC7289CD107803DE7FB9877C4BFDA3`; source zip sha256 `0F4BBD72651FC99197C857093C24AAC9F3927EC9F5B7B7C364B1A312032EF15E`; status `package-ready-not-vps-smoked`.
- provider snapshot/backup confirmation: research/amn2/vps-rebuild-001-provider-snapshot-confirmation-2026-06-10.md; status `defer`; monthly backup plan enabled, created/restorable backup not yet confirmed, delete actions not planned; Codex did not access provider panel or run live/SSH commands.
- destructive_action_authorized=no; reinstall_authorized=no; no live/SSH command, wipe, package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or secret publication.

Текущая private/local read-only API grouping:
- Server inventory/status: GET /api/servers, GET /api/servers/{server_name}/summary.
- Integration/service boundary: GET /api/integration/status.
- Local Agent runtime summary: GET /api/local-agent/runtime/summary.
- Aggregate metrics: GET /api/metrics/summary, GET /api/users/summary.
- Scope split: server:read for server/integration/local-agent summary, metrics:read for aggregate metrics/users summary.
- This does not authorize public OpenAPI/docs exposure, route expansion, config delivery or write routes.

Следующее решение:
- P4-NG is active as docs-only named gate / write API readiness planning;
- NG-C001, NG-C002, NG-C003, NG-C004, NG-S003, NG-C005, WAPI-V001, WAPI-V002, WAPI-V003, WAPI-V004, WAPI-V005, WAPI-I004, WAPI-I003, WAPI-I002, WAPI-I001, WAPI-I005, NG-N003, NG-N002, NG-N001, NG-N004, NG-S001, NG-S002, NG-S004, NG-X003, NG-X001, NG-X002, NG-SC001, P4-PRVTPRO-REFRESH-002, P4-PRVTPRO-REFRESH-001 and P4-PRVTPRO-REFRESH-004 are closed;
- очередь default docs-only cosmetic закрыта; NG-V001 закрыт как go; активных P4-NG задач больше нет;
- активная критичная задача отдельного destructive stage: VPS-REBUILD-001, defer-awaiting-final-destructive-approval; source/package precheck and package build/hygiene completed; backup plan enabled but created/restorable backup not confirmed; no delete actions planned; next required: provider answer or visible created backup, then stop-criteria review;
- любое другое VPS/live/public/write/config/destructive направление сначала требует отдельный named gate/decision.
```
