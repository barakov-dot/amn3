# AMN2 Phase 11 First Message

## Final closeout override 2026-07-18

`PHASE11-RELEASE-001` прошёл полный closeout gate. Phase 11 закрывается как
`completed-controlled-private-release` commit-условием
`closeout_commit=this_commit`: declaration действует только после tests,
complete security-diff review с findings `0`, equality sealed scan snapshot с
index и commit tree, push и exact trusted-origin readback.

Authoritative AMN2 source и production overlay:
`0b858c5cdbc5b565cc265966a2edfe2d339d65e0`. Persistent private bot принят
после run `20260717T192602Z` и `66m13s` stability pass; bot/Telegram/web/DB
healthy, database `integrity_ok|fk_0|only_expected_first_admin_row_delta`, AWG
`unchanged|running|restart_0|peer_set_unchanged`. Не повторять `/start`,
cleanup, stage, accept, rollout, restore или Phase 10 acceptance.

Release остаётся private/operator-only. Public web/API/config delivery,
write gates, config/peer generation и self-service enrollment закрыты. Old
fallback остаётся sealed до review не позднее 2026-08-01; second-VPS read-only
handover audit выполняется только непосредственно перед пользовательским
repurpose. Оба пункта не блокируют release при соблюдении contracts.

Canonical packet:
`docs/AMN2_PHASE_11_FINAL_CLOSEOUT_PACKET.ru.md`.

Следующая рекомендуемая команда после подтверждённого origin readback:

```text
GPT-5.6 SOL -> REVIEW_POST_RELEASE_DEVICE_001_READ_ONLY_OPERATOR_UX_SCOPE
```

---

## Continuation override 2026-07-16

`PHASE11-TELEGRAM-002A` local persistent admission/unit hardening завершён,
clean-scanned и pushed: AMN2 source `08c56f2`, origin sync, clean. Production
остаётся `801f8c3`; regular bot inactive/disabled, Telegram API/profile,
production web/DB, VPS/provider и AWG не менялись.

Следующий package должен быть combined descendant `08c56f2`, уже содержащим
canonical logo и Telegram hardening. Старый logo-only package `6abc620` не
выкатывать отдельно как текущий candidate. Второй VPS AMN2 больше не нужен;
пользователь держит его до выходных и затем передаёт под другой функционал.

Текущая рекомендуемая команда:

```text
GPT-5.6 SOL -> PREPARE_PHASE11_08C56F2_COMBINED_LOGO_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_PACKAGE_AND_ROLLOUT_GATE
```

---

## Prior continuation override 2026-07-15

`PHASE11-RESTORE-001A` passed. Old recovery fallback retained sealed without
deletion. Второй VPS AMN2 больше не нужен: clean SSH-only, пользователь держит
его до выходных и затем передаёт под другой функционал; provider mutation не
выполнять. Canonical logo source `6abc620` packaged and clean-scanned, но
production остаётся `801f8c3`; bot inactive/disabled, Telegram profile
unchanged, AWG untouched.

Текущая рекомендуемая команда:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_TELEGRAM_002A_FAIL_CLOSED_PERSISTENT_ADMISSION_DESIGN
```

---

## Prior continuation override 2026-07-14

`PHASE11-RESTORE-001A` gate review завершён: runtime-complete v2 tooling,
tests, security review и mandatory cleanup contract готовы. Live execution,
secret transfer и staging mutation не начинались. Точное approval находится в
первом блоке `docs/PROJECT_STATUS_CURRENT.ru.md`; до него production AWG и
второй VPS не менять.

Текущая рекомендуемая команда:

```text
GPT-5.6 SOL -> START_PHASE11_RESTORE_001A_RUNTIME_COMPLETE_V2_LIVE_GATE_SLICE -> RUN_SCOPED_TESTS_FOR_SELECTED_SLICE
```

---

## Prior continuation override 2026-07-14

Для продолжения уже начатой Phase 11 сначала прочитать
`docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md` и первый блок
`docs/PROJECT_STATUS_CURRENT.ru.md`. Текущий AMN2 source/production overlay —
`801f8c3`, а не исходный entry baseline `3c91601`.

`TELEGRAM-001`, решение `TELEGRAM-002`, `OPS-001`, `RECOVERY-001` и аудит
второго VPS закрыты. Persistent bot остаётся inactive/disabled. Старый
recovery fallback сохранён sealed. Чистый второй VPS удерживается временно для
`RESTORE-001A`, не считается независимым DR и не нужен текущему production P0.

Текущее первое действие без polling, restore apply и provider mutation:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_RESTORE_001A_CANONICAL_FULL_SECRET_DISPOSABLE_REHEARSAL_GATE
```

Этот текст отправляется целиком первым сообщением в новом task того же проекта.

---

AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_START

Продолжаем AMN2 в новой Phase 11 `Controlled Launch and Operations`.
Phase 10 официально закрыта, повторно открывать её задачи или acceptance не
нужно.

Рабочая папка:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

Authoritative repositories:

```text
AMN3/docs repo:
branch=codex-spark-phase9-docs-sync
phase10_closeout_commit=dc2d5ca
start_from=current_origin_branch_head_containing_relocation_packet

AMN2 source worktree:
path=C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-p7-c005-write-install
branch=codex-vps-test-prep
head=3c91601
origin_sync=true
```

Перед работой проверь `git status`, обнови remote refs и сравни local/remote
heads. Не переключай ветки вслепую, не делай reset и не откатывай посторонние
пользовательские изменения.

Сначала прочитай:

1. `docs/PROJECT_STATUS_CURRENT.ru.md` — первый control block.
2. `docs/AMN2_PHASE_10_FINAL_CLOSEOUT_PACKET.ru.md`.
3. `docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md`.
4. `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`.
5. `research/amn2/phase-10-final-closeout-phase11-handoff-2026-07-14.md`.
6. `research/amn2/phase-10-3c91601-existing-client-post-deploy-acceptance-2026-07-14.md`.
7. `research/amn2/phase-10-upstream-lifecycle-web-diagnostics-cascade-revoke-2026-07-12.md`.
8. `research/amn2/phase-10-canonical-hybrid-recovery-replacement-2026-07-14.md`.

Current production baseline:

```text
vps_overlay=3c91601
web=active_enabled_http_200_loopback_only
awg=running_restart_count_0
peer_count=12
bot=inactive_disabled
public_api_3040=false
write_gates=false_false
post_rollout_client_acceptance=passed
fresh_handshake=2026-07-14T11:29:53Z
accepted_traffic=rx_205184|tx_7176839
```

Phase 10 delivered and deployed:

- AWG2 contract hardening;
- plan/device quota and owner-shared policy;
- integration API-key registry and private read-only surfaces;
- Telegram read-only admin callbacks and transient single-admin smoke runner;
- Desired / Observed / Drift diagnostics;
- Device Passport and Enrollment Ticket contracts/schema;
- lifecycle evidence and cascade physical-device revoke;
- canonical encrypted recovery copy and sanitized restore rehearsal;
- private package rollout with verified rollback and client acceptance.

Do not claim hardware attestation, MDM, tamper resistance or endpoint posture:
AMN2 does not have a trusted endpoint agent.

Operator requirements:

- Work as `GPT-5.6 SOL` for this phase.
- Continue end-to-end without unnecessary pauses or repeated questions.
- Do not run hundreds of identical no-op cycles; every cycle must be a distinct
  product slice, engineering verification or exact risk gate.
- Product/engineering evidence first, scoped tests second, diff/security review
  third, docs/status sync fourth, commit and push last.
- Push every completed logical result. Never leave completed work only local.
- Do not touch unrelated user changes. In particular, leave
  `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` untouched unless explicitly
  requested.
- Use `scripts/phase9_progress_harness.py` and
  `tests/test_phase9_progress_harness.py` as the mandatory progress harness.
- After each result show the next plan as `Одиночная`, `Двойная`, `Тройная`,
  `Четверная` and `Более — рекомендовано`; every exact command starts with
  `GPT-5.6 SOL`.
- Prefer doing all discoverable/local work yourself. Ask for manual action only
  when a physical client/device or external operator console is unavoidable.

Production service rule:

- Never stop the production VPN for tests.
- If an exact gate changes a service state, restore the previous state,
  reverify it and explicitly notify the operator.
- Existing configs are actively used; AWG continuity has priority.

Phase 11 safety reset:

```text
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
```

All Phase 10 approvals are consumed. Any new VPS/SSH mutation, Telegram
polling/send, public exposure, config generation/delivery, peer mutation,
restore apply, provider or destructive action needs a new exact named gate.
Read-only checks must still be scoped and secret-safe.

Never print `.conf` contents, QR/import payloads, private keys, PSK, tokens,
passwords, target-private identifiers or raw sensitive logs.

Product policy:

- Default: one client config/peer per physical client device.
- Owner-shared multi-device use is an explicit operator exception, not the
  default client tariff behavior.
- Enrollment Ticket does not block launch while self-service onboarding is not
  required.
- Public web/admin, public API and public config delivery remain closed.

Phase 11 ordered plan:

```text
P0:
PHASE11-TELEGRAM-001 controlled single-admin transient smoke gate
PHASE11-TELEGRAM-002 persistent private bot runtime decision after smoke
PHASE11-OPS-001 compact runtime/recovery health evidence
PHASE11-RECOVERY-001 old recovery bundle/key retirement decision

P1:
PHASE11-DEVICE-001 Device Passport/lifecycle read-only operator UX
PHASE11-API-001 private scoped API-key integration lane
PHASE11-DEVICE-002 one-config-per-device/quota/owner-shared consistency
PHASE11-ENROLL-001 self-service enrollment only after explicit requirement

P2:
PHASE11-DRIFT-001 drift history/retention and explainable UX
PHASE11-DRIFT-002 gated remediation through OperationPlan
PHASE11-IPAM-001 dynamic subnet source-of-truth/IPAM
PHASE11-FLEET-001 multi-VPS capacity/placement/migration after IPAM
PHASE11-RESTORE-001 restore single-flight/idempotency when apply reopens
PHASE11-CLIENT-001 published-release-triggered client reacceptance

P3:
PHASE11-AUTH-001 web-admin 2FA design
PHASE11-ROUTING-001 domain-zone exclusion policy
PHASE11-BOTS-001 separate support/news bot identities and runtimes
PHASE11-DOCS-001 OpenAPI/DESIGN/naming/Russian-first docs
PHASE11-METRICS-001 privacy-safe metrics expansion
```

Use PRVTPRO and KYORESUAS as product/API/negative-learning sources and Amnezia
repositories as client/protocol truth. Design independently; do not copy GPL
code, templates, scripts, workflows or product identity. Do not add WARP,
SOCKS5, AdGuard, NGINX/domain automation, marketplace, public tunnels, raw
config editor or broad multi-protocol parity to launch scope.

Automation handoff:

- `amn2-upstream-orchestrator` is ACTIVE and resolves the active phase from the
  first control block.
- Legacy PRVTPRO/KYORESUAS/Amnezia three-step chain is PAUSED.
- Once this new task exists, inspect the active heartbeat and retarget it to
  this task when supported; otherwise preserve explicit dynamic-retarget
  behavior. Do not let it continue a Phase 10 plan.

First action, review only; do not start polling yet:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_3C91601_PRIVATE_TELEGRAM_SINGLE_ADMIN_TRANSIENT_SMOKE_GATE
```

Review current `3c91601` implementation, tests, production bot-disabled
baseline, configured-admin identity, clone-vs-production writes, internal TTL,
backlog/watchdog and rollback. If the review passes, prepare a separate exact
live approval phrase. Persistent bot activation remains a later gate.

---
