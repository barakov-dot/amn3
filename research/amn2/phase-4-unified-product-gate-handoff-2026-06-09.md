# Phase 4 Unified Product Gate: handoff 2026-06-09

Дата: 2026-06-09.

Назначение: зафиксировать переход основного AMN coordination-чата из Phase 3 service-mode loopback work в Phase 4 unified product/API planning.

## Решение

```text
decision: phase4-ready
phase3_service_mode_baseline: closed
phase4_default_mode: local-read-only-product-planning
main_chat_entrypoint: docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md
target_vps_change_authorized: no
production_write_authorized: no
public_exposure_authorized: no
```

## Baseline, принятый Phase 4

```text
AMN2 source-overlay/package head: f7f6131
AMN3 checkpoint before Phase 4 packet: a205daa
target_vps_mode: service-mode web/bot active, loopback-only
web_admin_bind: 127.0.0.1:3030
operator_access: SSH local port forward, external browser only
amneziya-web: active/enabled
amneziya-bot: active/enabled
login_loopback_http: 200
public_direct_3030: closed by loopback bind
public_api_3040: absent/closed
tcp_80_443: absent
domain_https_cutover: deferred
VPS_APPLY_ENABLED: false
remaining_approved_test_peers: Neobyatnaya-AMNZ-1, Neobyatnaya-AMNZ-2
revoked_test_peers: Neobyatnaya-AMNZ-3, Neobyatnaya-AMNZ-4
web_panel_ux_review: passed-minimal-safe-summary
```

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

## Текущая private/local read-only API grouping

`P4-X001` closed the operator docs grouping for the existing six private/local read-only routes. This is only a docs/navigation grouping; it does not authorize public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, route expansion, config delivery, write routes or Local Agent mutations.

| Group | Route | Scope | Boundary |
| --- | --- | --- | --- |
| Server inventory/status | `GET /api/servers` | `server:read` | server list/status metadata only |
| Server inventory/status | `GET /api/servers/{server_name}/summary` | `server:read` | aggregate server/user/device summary only |
| Integration/service boundary | `GET /api/integration/status` | `server:read` | service-mode/read-only/API/token-boundary status only |
| Local Agent runtime summary | `GET /api/local-agent/runtime/summary` | `server:read` | controller-safe Local Agent runtime summary only |
| Aggregate metrics | `GET /api/metrics/summary` | `metrics:read` | aggregate metrics only, no peer/user detail leakage |
| Aggregate metrics | `GET /api/users/summary` | `metrics:read` | aggregate user/device counts only |

## Назначение Phase 4

Phase 4 gathers the parallel workstreams into one decision map:

- AMN2/API production line;
- target VPS service-mode state;
- PRVTPRO/Amnezia-Web-Panel research line;
- KYORESUAS/API research line;
- AMN3 evidence/backlog/runbook registry.

It is a planning and transfer gate, not a permission to run new live commands.

## Разрешенная следующая работа

- AMN3 docs/status/backlog consolidation.
- Read-only web-panel UX/product notes through the existing SSH tunnel.
- Candidate rows for PRVTPRO/KYORESUAS ideas.
- Local/read-only `amn2` plans and tests.
- Separate gate design for future live/public/write changes.

## Всё еще закрыто

- `VPS_APPLY_ENABLED=true`;
- public API `3040`;
- direct public web/admin `3030`;
- Caddy/nginx/HTTPS public cutover;
- production peer/user mutation beyond approved test peers;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- secret-bearing evidence publication.

## Закрытые и следующие slices

Закрытые slices:

1. `P4-C009` web-panel user/config visibility; evidence: `research/amn2/phase-4-web-panel-user-config-visibility-implementation-2026-06-09.md`.
2. `P4-I002` service-mode/read-only status wording; evidence: `research/amn2/phase-4-service-mode-status-wording-implementation-2026-06-09.md`.
3. route/secret gate planning; evidence: `research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md`.
4. `P4-I003` read-only API/status schema maturity design; evidence: `research/amn2/phase-4-read-only-api-status-design-2026-06-09.md`.
5. `P4-I003` AMN2 local implementation plan; plan: `docs/superpowers/plans/2026-06-09-amn2-p4-i003-read-only-api-status-schema.md`.
6. `P4-I003` AMN2 local implementation; evidence: `research/amn2/phase-4-read-only-api-status-schema-implementation-2026-06-09.md`.
7. `P4-I004` endpoint taxonomy / route-policy docs alignment; evidence: `research/amn2/phase-4-endpoint-taxonomy-route-policy-docs-implementation-2026-06-09.md`.
8. `P4-N003` aggregate metrics privacy boundary; evidence: `research/amn2/phase-4-aggregate-metrics-privacy-boundary-implementation-2026-06-09.md`.
9. `P4-I005` API token lifecycle boundary; evidence: `research/amn2/phase-4-api-token-lifecycle-boundary-implementation-2026-06-09.md`.
10. `P4-N004` bot/admin read-only labels; evidence: `research/amn2/phase-4-bot-admin-read-only-labels-implementation-2026-06-09.md`.
11. `P4-N001` docs/status drift synchronization; evidence: `research/amn2/phase-4-docs-status-drift-sync-2026-06-09.md`.
12. `P4-N002` protocol manager interface checklist; evidence: `research/amn2/phase-4-protocol-manager-interface-checklist-2026-06-09.md`.
13. `P4-X003` Russian-first operator docs polish; evidence: `research/amn2/phase-4-russian-first-operator-docs-polish-2026-06-09.md`.
14. `P4-X002` API/status/gate naming cleanup; evidence: `research/amn2/phase-4-api-status-gate-naming-cleanup-2026-06-09.md`.
15. `P4-X001` read-only API docs grouping polish; evidence: `research/amn2/phase-4-read-only-api-docs-grouping-polish-2026-06-09.md`.
16. `P4-I001` second read-only UX pass closure; evidence: `research/amn2/phase-4-p4-i001-read-only-ux-pass-closure-2026-06-10.md`.
17. `P4-NG` named gate / write API readiness charter; evidence: `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md`; plan: `docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md`.
18. `NG-C003` secrets policy, `NG-C004` go/no-go format and `NG-S003` reusable named-gate evidence template; evidence: `research/amn2/phase-4-ng-secrets-policy-go-no-go-format-2026-06-10.md`; template: `research/amn2/phase-4-ng-named-gate-evidence-template-2026-06-10.md`.
19. `NG-C005` write API live-block assertion; evidence: `research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md`.
20. `WAPI-V001` write API threat model; evidence: `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`.
21. PRVTPRO refresh 2026-06-10 candidate intake; evidence: `research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md`.
22. `P4-PRVTPRO-REFRESH-002` expiration-field contract tests; evidence: `research/amn2/phase-4-prvtpro-expiration-contract-tests-implementation-2026-06-10.md`.
23. `P4-PRVTPRO-REFRESH-001` read-only About/Version/Build status; evidence: `research/amn2/phase-4-prvtpro-build-status-implementation-2026-06-10.md`.
24. PRVTPRO local-only slices merge into AMN2 `codex-vps-test-prep`; evidence: `research/amn2/phase-4-prvtpro-local-slices-merge-2026-06-10.md`; AMN2 base head: `1508e3c4a100b76815b29f91757290f1266f813d`.
25. `P4-PRVTPRO-REFRESH-004` API taxonomy/OpenAPI grouping policy support; evidence: `research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md`.
26. `WAPI-V002` write API route taxonomy; evidence: `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`.
27. `WAPI-V003` local fake-runner contract; evidence: `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`.
28. `WAPI-V004` idempotency, locking and partial-failure model; evidence: `research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md`.

Текущий next stage:

1. `P4-NG` is active as docs-only named gate / write API readiness planning.
2. `NG-C001`, `NG-C002`, `NG-C003`, `NG-C004`, `NG-S003`, `NG-C005`, `WAPI-V001`, `WAPI-V002`, `WAPI-V003`, `WAPI-V004`, `P4-PRVTPRO-REFRESH-002`, `P4-PRVTPRO-REFRESH-001` and `P4-PRVTPRO-REFRESH-004` are closed.
3. Next recommended docs-only task is `WAPI-V005` write API audit/redaction requirements with `live_write_authorized: no`.
4. `NG-V001` read-only VPS baseline gate requires explicit operator approval and target SSH alias/host outside repo secrets.
5. Write API live work remains blocked until a separate `P4-WRITE-API-LIVE-GATE`.
6. `P4-PRVTPRO-REFRESH-002` expiration-field contract tests, `P4-PRVTPRO-REFRESH-001` read-only About/Version/Build status and `P4-PRVTPRO-REFRESH-004` docs/policy support are closed; if selecting remaining PRVTPRO-derived work, create a design boundary for `P4-PRVTPRO-REFRESH-003` before any implementation; keep GPL-3.0 code/templates/UI/managers/workflows out of AMN2.

If the selected slice requires live VPS state changes, stop and create a separate named gate first.

## Evidence links

```text
docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md
docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md
docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md
research/amn2/phase-4-web-panel-user-config-visibility-implementation-2026-06-09.md
research/amn2/phase-4-service-mode-status-wording-implementation-2026-06-09.md
research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md
research/amn2/phase-4-read-only-api-status-design-2026-06-09.md
docs/superpowers/plans/2026-06-09-amn2-p4-i003-read-only-api-status-schema.md
research/amn2/phase-4-read-only-api-status-schema-implementation-2026-06-09.md
research/amn2/phase-4-endpoint-taxonomy-route-policy-docs-implementation-2026-06-09.md
research/amn2/phase-4-aggregate-metrics-privacy-boundary-implementation-2026-06-09.md
research/amn2/phase-4-api-token-lifecycle-boundary-implementation-2026-06-09.md
research/amn2/phase-4-bot-admin-read-only-labels-implementation-2026-06-09.md
research/amn2/phase-4-russian-first-operator-docs-polish-2026-06-09.md
research/amn2/phase-4-api-status-gate-naming-cleanup-2026-06-09.md
research/amn2/phase-4-read-only-api-docs-grouping-polish-2026-06-09.md
research/amn2/phase-4-p4-i001-read-only-ux-pass-closure-2026-06-10.md
research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md
research/amn2/phase-4-ng-secrets-policy-go-no-go-format-2026-06-10.md
research/amn2/phase-4-ng-named-gate-evidence-template-2026-06-10.md
research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md
research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md
research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md
research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md
research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md
research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md
research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md
docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md
research/amn2/target-server-service-mode-authenticated-web-panel-smoke-evidence-2026-06-09.md
research/amn2/target-server-revoke-by-number-4-evidence-2026-06-09.md
research/amn2/target-server-service-mode-ssh-tunnel-access-evidence-2026-06-09.md
```

## Обращение с секретами

No `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client configs, QR payloads, `vpn://`, backup contents, public endpoint values, session cookies or full logs are included in this handoff.
