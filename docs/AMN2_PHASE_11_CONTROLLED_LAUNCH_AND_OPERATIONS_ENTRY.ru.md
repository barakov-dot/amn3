# AMN2 Phase 11 Controlled Launch and Operations Entry

## Current execution override 2026-07-17 after TELEGRAM-002B stability pass

`PHASE11-TELEGRAM-002B` live activation and real 60-minute stability window
passed on production overlay `0b858c5`. Run `20260717T192602Z` accepted one
fresh first-admin `/start` with exact wide-header confirmation. Final read-only
postflight at `2026-07-17T20:32Z`, more than 66 minutes after activation,
confirmed one active/enabled bot instance, restart `0`, healthy watchdog,
matching Telegram identity, empty webhook/backlog, healthy loopback-only web,
database integrity/FK pass and unchanged AWG.

No repeat `/start`, stage, accept or cleanup is required. The only current
release-critical work is `PHASE11-RELEASE-001`: seal the Phase 11 closeout and
make the private release-readiness decision. Second-VPS clean handover audit is
required only immediately before the user's repurpose action and does not block
release. Old fallback remains sealed without deletion until review no later
than 2026-08-01 and also does not block release while retained.

Future bot VPS-write functionality still requires a separate exact gate and a
service-readable non-home SSH key/known-hosts proof with `ProtectHome=true`;
the currently accepted read-only persistent runtime does not open that mode.
AWG remains untouched.

Дата: 2026-07-17.

## Previous execution override 2026-07-16 after TELEGRAM-002A local hardening

`PHASE11-TELEGRAM-002A` реализован, clean-scanned и pushed как AMN2 source
`08c56f2beff65145380fdb3736d94c0709a2b33a`. Identity/webhook/backlog/poll
ownership checks, повторный pre-poll state check, process-lifetime lock,
allowed updates, concurrency limit `8`, один overall startup budget, systemd
readiness/watchdog/restart limits и sandbox подтверждены TDD. Scoped tests:
113 passed; полный source suite: 915 passed, 1 skipped; clean security scan:
15/15 receipts, findings 0.

Это local-only result. Production остаётся `801f8c3`, regular bot
inactive/disabled, Telegram API/profile, production web/DB, оба VPS и AWG не
изменялись. Следующий critical шаг — подготовить новый combined private
overlay package на exact `08c56f2` (он уже содержит canonical logo), проверить
contents/checksum/rollback и только затем вынести отдельный exact rollout gate.
Старый logo-only package `6abc620` не считать текущим combined candidate.

Перед будущим bot VPS-write activation сохранить `ProtectHome=true` и отдельно
доказать service-readable non-home SSH key/known-hosts path. Второй VPS AMN2
уже не нужен; до пользовательского handover остаётся read-only audit и только
отдельно approved cleanup dedicated staging key/known-host binding.

Дата: 2026-07-16.

## Previous execution override 2026-07-15 after recovery/VPS/logo package decisions

Old recovery fallback остаётся sealed без удаления до повторного review не
позднее 2026-08-01. Второй VPS AMN2 больше не нужен: он clean SSH-only,
пользователь держит его до выходных и затем передаёт под другой функционал;
provider deletion/cancel/renewal mutation не является AMN2-задачей. Перед
handover остаётся финальный read-only audit и, по отдельному exact approval,
удаление только dedicated staging SSH key и local known-host binding.

Canonical-logo private overlay package для source `6abc620` подготовлен и
clean-scanned, но не uploaded/applied; production остаётся `801f8c3`, regular
bot inactive/disabled, Telegram profile unchanged, AWG untouched. Текущий
engineering priority — design gate, затем TDD implementation
`PHASE11-TELEGRAM-002A`.

Дата: 2026-07-15.

## Previous execution override 2026-07-15

Текущий исполняемый порядок после успешного `PHASE11-RESTORE-001A` находится в
`docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md`. Production overlay и AMN2
production source остаются `801f8c3`. Canonical full-secret disposable rehearsal
прошёл; mandatory cleanup вернул второй VPS в clean SSH-only state, production
AWG остался running/restart 0/12 peers. Следующие critical решения — отдельные
retirement gates для старого fallback и второго VPS. Persistent bot остаётся
disabled до `TELEGRAM-002A` hardening и последующего exact activation gate.

Дата: 2026-07-15.

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
