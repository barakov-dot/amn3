# AMN2 Phase 11 Controlled Launch and Operations Entry

Дата: 2026-07-14.

## Назначение

Phase 11 переводит проверенную private/operator production baseline в
контролируемую эксплуатацию и последовательно развивает web/API/Telegram и
device lifecycle, не открывая public/self-service/write/config gates молча.

Это не generic VPN panel и не broad protocol expansion. North star AMN2:
безопасный lifecycle доступа пользователя и физического устройства с
объяснимым состоянием, audit, recovery и точными mutation gates.

## Entry baseline

```text
phase10_status=closed
amn2_branch=codex-vps-test-prep
amn2_head=3c91601
amn2_origin_sync=true
production_overlay=3c91601
web=active_enabled_http_200_loopback_only
awg=running_restart_count_0|12_peers
bot=inactive_disabled
api_3040_listener=0
write_gates=false_false
post_rollout_client_acceptance=passed
recovery=hybrid_encrypted_copy_and_sanitized_rehearsal_passed
```

## Сначала прочитать

1. `docs/PROJECT_STATUS_CURRENT.ru.md` — только первый control block является
   текущим решением.
2. `docs/AMN2_PHASE_10_FINAL_CLOSEOUT_PACKET.ru.md`.
3. `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`.
4. `docs/AMN2_PHASE_11_FIRST_MESSAGE.ru.md` — operator requirements и
   copy-ready migration contract.
5. `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md` — новые верхние overrides;
   старые записи являются историей.
6. `research/amn2/phase-10-3c91601-existing-client-post-deploy-acceptance-2026-07-14.md`.
7. `research/amn2/phase-10-upstream-lifecycle-web-diagnostics-cascade-revoke-2026-07-12.md`.
8. `research/amn2/phase-10-canonical-hybrid-recovery-replacement-2026-07-14.md`.
9. `ideas/priority-backlog.md`, `ideas/candidates-for-amn2.md`,
   `ideas/candidates-for-hybrid.md`, `ideas/rejected.md` — reference-only;
   deduplicate against current code/evidence before selecting work.

## Operating rule

1. Product slice или проверяемая engineering verification сначала.
2. Scoped tests вторыми.
3. Diff/security review третьими.
4. Docs/status sync только после evidence.
5. Commit и push каждого логического результата.
6. Никаких повторных no-op/hold loops.
7. Production VPN не останавливать для тестов; если service state всё же
   меняется по exact gate, вернуть baseline, проверить и уведомить оператора.

Обязательный progress harness остаётся:

- `scripts/phase9_progress_harness.py`;
- `tests/test_phase9_progress_harness.py`.

## Stop-lines Phase 11

```text
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
```

Все approvals Phase 10 consumed и не действуют в Phase 11. Read-only или live
gate должен называться заново и ограничиваться exact scope.

## Ordered backlog

### P0 Controlled private launch

1. `PHASE11-TELEGRAM-001`: review и затем отдельный exact gate для existing
   single-admin transient smoke runner на production overlay `3c91601`.
2. `PHASE11-TELEGRAM-002`: persistent private bot service decision только
   после transient pass; disabled-at-boot rollback, watchdog и backlog guard.
3. `PHASE11-OPS-001`: compact runtime/recovery health evidence без постоянного
   raw telemetry и без остановки AWG.
4. `PHASE11-RECOVERY-001`: retention/retirement decision для предыдущего
   recovery bundle/key; canonical hybrid copy не удалять до решения.

### P1 Operator productization

1. `PHASE11-DEVICE-001`: Device Passport/lifecycle list/detail UX на
   authenticated read-only operator surface.
2. `PHASE11-API-001`: private scoped API-key integration lane; route policy,
   TTL/revoke/audit и loopback-only smoke.
3. `PHASE11-DEVICE-002`: one-config-per-device default, quota and owner-shared
   exception UX/audit consistency.
4. `PHASE11-ENROLL-001`: self-service Enrollment Ticket route only after an
   explicit product requirement, with rate limits and abuse controls.

### P2 Post-launch safety and scale

1. `PHASE11-DRIFT-001`: drift history/retention and explainable operator UX.
2. `PHASE11-DRIFT-002`: gated remediation via OperationPlan preview/approve/
   apply/verify/rollback; never automatic by default.
3. `PHASE11-IPAM-001`: dynamic subnet source-of-truth, CIDR/reserved-address
   validation and conflict model.
4. `PHASE11-FLEET-001`: multi-VPS capacity, placement and migration only after
   IPAM/source-of-truth.
5. `PHASE11-RESTORE-001`: restore apply single-flight, idempotency token,
   backup-before-write, verify and rollback when restore apply reopens.
6. `PHASE11-CLIENT-001`: client compatibility reacceptance only on published
   release/security/config-format triggers.

### P3 Design-later

- `PHASE11-AUTH-001`: web-admin 2FA recovery/lockout/rate-limit design;
- `PHASE11-ROUTING-001`: Domain Zone Exclusion Policy, default-off;
- `PHASE11-BOTS-001`: support/news bots as separate identities and runtimes;
- `PHASE11-DOCS-001`: OpenAPI grouping, DESIGN.md, naming cleanup and
  Russian-first operator docs;
- `PHASE11-METRICS-001`: privacy-safe metrics retention and expansion.

## Explicit exclusions

Do not add WARP, SOCKS5, AdGuard, NGINX/domain automation,
marketplace/templates, public tunnels, raw config editor, public admin or broad
multi-protocol parity as Phase 11 launch work without a new product decision.

Do not claim hardware attestation, MDM, tamper resistance or endpoint posture
without a trusted AMN2 endpoint agent.

## Upstream intelligence

`amn2-upstream-orchestrator` remains the one ACTIVE read-only weekly source.
It must derive the active phase from `PROJECT_STATUS_CURRENT`, deduplicate
against `3c91601`, and treat PRVTPRO/KYORESUAS/Amnezia/Headscale/NetBox signals
as independent design lessons. No GPL code/template/workflow copying.

## First command

```text
GPT-5.6 SOL -> REVIEW_PHASE11_3C91601_PRIVATE_TELEGRAM_SINGLE_ADMIN_TRANSIENT_SMOKE_GATE
```

Expected result: exact go/stop decision, clone-vs-production write boundary,
configured-admin identity check, TTL/watchdog/rollback scope and proof that the
regular bot unit remains disabled until a separately approved runtime action.
