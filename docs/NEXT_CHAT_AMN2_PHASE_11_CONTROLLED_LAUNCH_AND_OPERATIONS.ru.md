# Следующий task: AMN2 Phase 11 Controlled Launch and Operations

## Current continuation override 2026-07-14

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|801f8c3|origin_sync
production_overlay=801f8c3
restore_001a_gate=reviewed_ready_awaiting_exact_approval
restore_001a_format=runtime_complete_v2|required_external_source_digest
restore_001a_security=complete_coverage|findings_0
telegram_001=completed_pass
telegram_002=hold_disabled_go_local_hardening
ops_001=completed_healthy
recovery_001=retain_old_fallback_until_restore_001a
second_vps=clean_ssh_only|keep_temporarily_for_restore_001a|independent_dr_false
next=OPERATOR_EXACT_APPROVAL_FOR_PHASE11_RESTORE_001A
```

Актуальный план по критичности:
`docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md`. Нижележащий original handoff
с `3c91601` сохранён как entry history и не должен переопределять этот блок.

Начать сообщением:

```text
AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_START
```

Copy-ready полный текст первого сообщения:
`docs/AMN2_PHASE_11_FIRST_MESSAGE.ru.md`.

## Сначала прочитать

- `docs/PROJECT_STATUS_CURRENT.ru.md` — первый control block;
- `docs/AMN2_PHASE_10_FINAL_CLOSEOUT_PACKET.ru.md`;
- `docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md`;
- `docs/AMN2_PHASE_11_FIRST_MESSAGE.ru.md`;
- этот handoff;
- `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md` — только верхние overrides;
- `research/amn2/phase-10-3c91601-existing-client-post-deploy-acceptance-2026-07-14.md`;
- `research/amn2/phase-10-upstream-lifecycle-web-diagnostics-cascade-revoke-2026-07-12.md`;
- `research/amn2/phase-10-canonical-hybrid-recovery-replacement-2026-07-14.md`.

## Current baseline

```text
active_phase=Phase 11 Controlled Launch and Operations
phase10_status=closed
amn2_branch=codex-vps-test-prep
amn2_head=3c91601
production_overlay=3c91601
web=active_enabled_http_200_loopback_only
awg=running_restart_count_0|12_peers
bot=inactive_disabled
api_3040_listener=0
write_gates=false_false
client_acceptance=passed_fresh_handshake_and_traffic
```

Phase 10 deployed Device Passport, Enrollment Ticket schema/contracts,
lifecycle, read-only drift/web diagnostics, cascade revoke, plan quota,
integration registry and Telegram read-only callbacks. New lifecycle tables are
empty until real product flows use them. Public enrollment, public API,
persistent bot runtime and live remediation are not open.

## First concrete gate

```text
GPT-5.6 SOL -> REVIEW_PHASE11_3C91601_PRIVATE_TELEGRAM_SINGLE_ADMIN_TRANSIENT_SMOKE_GATE
```

Review existing implementation/evidence first:

- `research/amn2/phase-10-private-telegram-controlled-polling-ttl-gate-review-2026-07-11.md`;
- `research/amn2/phase-10-telegram-single-admin-transient-smoke-runner-hardening-2026-07-11.md`;
- current `3c91601` bot/runtime code and tests;
- production baseline: regular bot unit inactive/disabled.

Do not start polling during review. If review passes, prepare a separate exact
live phrase for one configured-admin, message-only, internally TTL-bounded run
with safe backlog and rollback. Persistent activation is a later gate.

## Planned work map

### Now

- private Telegram single-admin transient smoke and later persistent-runtime
  decision;
- production runtime/recovery observation without stopping AWG;
- retirement decision for the old recovery bundle/key.

### Next

- Device Passport/lifecycle read-only operator UX;
- scoped private API-key integration operations;
- one-config-per-device/quota/owner-shared consistency;
- self-service Enrollment route only if explicitly required.

### Post-launch

- drift history/retention;
- gated reconciliation apply through OperationPlan;
- dynamic subnet source-of-truth/IPAM and then multi-VPS fleet work;
- restore apply single-flight/idempotency;
- published-release-triggered client reacceptance.

### Design-later

- web-admin 2FA;
- domain-zone exclusion policy;
- separate support/news bots;
- privacy-safe metrics expansion;
- OpenAPI grouping, DESIGN.md, naming and Russian-first docs polish.

Authoritative IDs, dependencies and exclusions are in
`docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md`. Historical
`ideas/*` and `transfer-backlog.md` are inputs only; deduplicate before work.

## Safety reset

```text
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
```

Phase 10 approvals are consumed. Never print configs, QR, import payloads,
private keys, PSK, tokens, passwords or raw sensitive logs. Production VPN must
remain running; any separately approved service change must restore and verify
the prior baseline and notify the operator.

## Automation

The ACTIVE `amn2-upstream-orchestrator` resolves phase dynamically from the
first project control block. Legacy three-step weekly chain is PAUSED. After
the separate Phase 11 task exists, retarget the active heartbeat to that task
or retain its explicit dynamic-retarget behavior; it must not continue the
Phase 10 plan.

## Work style

Engineering/product evidence first, tests second, diff review third, status
sync fourth, commit/push last. Report commands as `Одиночная`, `Двойная`,
`Тройная` or `Более` with `GPT-5.6 SOL` named explicitly.
