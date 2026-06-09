# Phase 4 Unified Product Gate Handoff 2026-06-09

Дата: 2026-06-09.

Назначение: зафиксировать переход основного AMN coordination-чата из Phase 3 service-mode loopback work в Phase 4 unified product/API planning.

## Decision

```text
decision: phase4-ready
phase3_service_mode_baseline: closed
phase4_default_mode: local-read-only-product-planning
main_chat_entrypoint: docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md
target_vps_change_authorized: no
production_write_authorized: no
public_exposure_authorized: no
```

## Baseline Accepted By Phase 4

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

## Phase 4 Purpose

Phase 4 gathers the parallel workstreams into one decision map:

- AMN2/API production line;
- target VPS service-mode state;
- PRVTPRO/Amnezia-Web-Panel research line;
- KYORESUAS/API research line;
- AMN3 evidence/backlog/runbook registry.

It is a planning and transfer gate, not a permission to run new live commands.

## Allowed Next Work

- AMN3 docs/status/backlog consolidation.
- Read-only web-panel UX/product notes through the existing SSH tunnel.
- Candidate rows for PRVTPRO/KYORESUAS ideas.
- Local/read-only `amn2` plans and tests.
- Separate gate design for future live/public/write changes.

## Still Closed

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

## Next Recommended Slice

Completed first local-only slice:

1. `P4-C009` web-panel user/config visibility; evidence: `research/amn2/phase-4-web-panel-user-config-visibility-implementation-2026-06-09.md`.
2. `P4-I002` service-mode/read-only status wording; evidence: `research/amn2/phase-4-service-mode-status-wording-implementation-2026-06-09.md`.
3. route/secret gate planning; evidence: `research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md`.

Continue Phase 4 with:

1. `P4-I001` detailed read-only web-panel UX pass only if more page-level evidence is needed;
2. one candidate-specific API expansion design against the route/secret gate plan.

If the selected slice requires live VPS state changes, stop and create a separate named gate first.

## Evidence Links

```text
docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md
docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md
docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md
research/amn2/phase-4-web-panel-user-config-visibility-implementation-2026-06-09.md
research/amn2/phase-4-service-mode-status-wording-implementation-2026-06-09.md
research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md
research/amn2/target-server-service-mode-authenticated-web-panel-smoke-evidence-2026-06-09.md
research/amn2/target-server-revoke-by-number-4-evidence-2026-06-09.md
research/amn2/target-server-service-mode-ssh-tunnel-access-evidence-2026-06-09.md
```

## Secret Handling

No `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client configs, QR payloads, `vpn://`, backup contents, public endpoint values, session cookies or full logs are included in this handoff.
