# AMN2 Phase 10 Final Closeout Packet

Дата: 2026-07-14.

## Решение

Phase 10 `Product Recovery With Harness` закрыта как
`completed-product-recovered-deployed-accepted`.

Фаза вернула проект от повторяющегося command-loop к проверяемым product
slices, интегрировала накопленное hardening, развернула authoritative source
`3c91601` на private production VPS и получила свежую client acceptance после
rollout. Открытых product/package/schema/acceptance blockers не осталось.

Следующая фаза:

```text
Phase 11 Controlled Launch and Operations
start_phrase=AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_START
entry=docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md
handoff=docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md
```

## Финальная база

```text
amn2_branch=codex-vps-test-prep
amn2_head=3c916015c10add37886370d04af70f0343f7f691
amn2_origin_sync=true
amn2_worktree_clean=true
amn3_branch=codex-spark-phase9-docs-sync
production_vps_overlay=3c91601
production_web=active_enabled_http_200_loopback_only
production_awg=running_restart_count_0
production_peer_count=12
production_peer_set=unchanged
production_bot=inactive_disabled
production_api_3040_listener=0
production_write_gates=false_false
```

## Что закрыто в Phase 10

### Product recovery and contracts

- progress harness отделяет реальный product slice от no-op/hold-loop;
- AWG2 H1-H4 принимают ASCII uint32 single/range values, проверяют bounds,
  malformed/descending/overlapping ranges и сохраняют рабочие defaults;
- cross-client standard `.conf` принят Android TV, iOS DefaultVPN и Windows
  AmneziaVPN; client-visible name следует filename stem там, где это
  поддерживает официальный клиент;
- plan/device quota admin UI и owner-shared assignment policy реализованы;
- integration API-key registry и private read-only operator surfaces
  реализованы без public/write/config scope expansion;
- Telegram admin read-only status, traffic, server and credential callbacks
  реализованы и протестированы; persistent bot runtime не включался.

### Device lifecycle differentiation

- deterministic Desired / Observed / Drift snapshot и read-only diagnosis;
- AMN2-generated stable Device Passport без hardware-attestation claims;
- show-once, hash-only, TTL, revocable, atomic Device Enrollment Ticket;
- lifecycle `issued -> claimed -> config_ready -> delivered ->
  acceptance_verified` с safe duration/failure evidence;
- authenticated read-only admin/web diagnostics;
- remote-first cascade physical-device revoke через `OperationPlan`, включая
  ticket, delivery link, assignment и remote peer cleanup;
- late acceptance/reconnect/re-observation не восстанавливают отозванный
  доступ.

### Production and recovery

- provider-side outage локализован и восстановление подтверждено живым
  handshake/traffic;
- canonical encrypted hybrid recovery bundle проверен локально;
- вторая encrypted copy сохранена на независимом removable media без private
  key;
- sanitized isolated restore rehearsal прошёл без production secrets и без
  запуска runtime;
- private package `3c91601` применён через source/SQLite snapshots, clone DB
  migration/API smoke, exact production schema checkpoint и rollback;
- первый rollout attempt доказал автоматический rollback до production
  migration, второй завершился успешно;
- после rollout получены свежие handshakes и двусторонний client traffic.

## Финальная acceptance

```text
successful_rollout_run=20260714T101632Z
post_rollout_handshake=2026-07-14T11:29:53Z
later_handshake_confirmation=2026-07-14T11:39:06Z
acceptance_rx_delta_bytes=205184
acceptance_tx_delta_bytes=7176839
peer_count=12_stable
web_downtime_during_rollout_seconds=55
client_acceptance=passed
```

Evidence:

- `research/amn2/phase-10-3c91601-private-vps-rollout-2026-07-14.md`;
- `research/amn2/phase-10-3c91601-post-deploy-acceptance-closeout-readiness-2026-07-14.md`;
- `research/amn2/phase-10-3c91601-existing-client-post-deploy-acceptance-2026-07-14.md`;
- `research/amn2/phase-10-canonical-hybrid-recovery-replacement-2026-07-14.md`;
- `research/amn2/phase-10-upstream-lifecycle-web-diagnostics-cascade-revoke-2026-07-12.md`;
- `research/amn2/phase-10-upstream-orchestrator-test-and-awg2-contract-hardening-2026-07-11.md`.

## Проверки

Последний authoritative AMN2 product head:

```text
focused_lifecycle=17_passed
focused_web_drift_security=55_passed_1_warning
focused_cascade=3_passed
expanded_affected=106_passed_1_warning
revoke_regression=20_passed
full_amn2=870_passed_1_skipped_1_warning
package_focused=237_passed_1_warning
package_full=870_passed_1_skipped_1_warning
package_tooling=23_passed
python_compile=passed
```

Final closeout verification:

```text
phase11_first_command_harness=passed
root_scoped_harness_markdown=20_passed
root_full=43_passed
fresh_authoritative_amn2_full=870_passed_1_skipped_1_warning
amn2_worktree_after_tests=clean_origin_sync
git_diff_check=passed
unsafe_true_marker_scan=0_findings
new_docs_secret_value_scan=0_findings
content_diff_review=passed
```

## Что намеренно не открыто

```text
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
```

Consumed approvals Phase 10 не переносятся в Phase 11. Любые новые live VPS,
Telegram polling/send, public exposure, config delivery/generation, peer
mutation, restore apply, provider action или destructive operation требуют
нового exact gate.

Текущая baseline остаётся private/operator-only:

- web/admin только loopback/SSH-private access;
- public API `3040`, direct public web `3030`, `80/443` cutover не открыты;
- bot inactive/disabled;
- Enrollment Ticket public/self-service route выключен;
- live drift remediation выключена;
- production API write/config smoke не выполнялся.

## Известные ограничения без блокировки closeout

- Android TV `.vpn` import может зависать; standard `.conf` является
  подтверждённым совместимым путём;
- повторная Android TV acceptance нужна только после нового published Amnezia
  Client release;
- новые Device Passport/Enrollment/lifecycle production tables пока пусты;
- один config может технически работать на нескольких личных устройствах;
  default product policy остаётся one config/peer per client device, а
  owner-shared является явным operator exception;
- production restore apply с secrets не репетировался и остаётся exact gate;
- bot code развернут, но runtime intentionally disabled.

## Перенос в Phase 11

### P0: controlled private launch

1. Controlled single-admin Telegram transient smoke gate на `3c91601`:
   message-only, exact-admin, internal TTL, safe backlog, clone-only writes,
   bot disabled at boot.
2. После transient pass отдельно решить persistent private bot service gate;
   config delivery, peer mutation и public onboarding не включать автоматически.
3. Держать production runtime, encrypted recovery rotation и provider incident
   path наблюдаемыми без остановки AWG для тестов.

### P1: operator productization

1. Device Passport/lifecycle operator UX поверх реальных данных, когда они
   появятся, без agent/posture claims.
2. Scoped API key/integration operations только на private/loopback routes;
   `config:read`, write scopes и public API требуют отдельных gates.
3. One-config-per-device default, plan quota и owner-shared exception должны
   оставаться явными и audit-safe.
4. Enrollment self-service route, rate limits и abuse controls только если
   self-service onboarding станет обязательным продуктовым требованием.

### P2: post-launch safety and scale

1. Drift history/retention и объяснимый operator UX.
2. Reconciliation apply только через `OperationPlan`, preview, approval,
   idempotency, verify и rollback.
3. Dynamic subnet source-of-truth/IPAM, затем multi-VPS placement/migration.
4. Restore apply single-flight/idempotency при повторном открытии restore gate.
5. Android/Android TV/iOS/Windows reacceptance по published release triggers.
6. Решение о retirement старого recovery bundle/key после retention review.

### P3: optional and design-later

- web-admin 2FA с recovery/lockout/rate-limit design;
- default-off Domain Zone Exclusion Policy с client compatibility matrix;
- support/news bots как отдельные tokens/runtimes без config authority;
- OpenAPI grouping, operator DESIGN.md, naming cleanup и Russian-first docs;
- privacy-safe metrics expansion без per-peer/public leakage.

### Better left upstream / excluded

WARP, SOCKS5, AdGuard, NGINX/domain automation, marketplace/templates, public
tunnels, raw config editor и broad multi-protocol parity не входят в launch
scope. PRVTPRO и KYORESUAS остаются источниками product lessons, API taxonomy
и negative learning; GPL implementation не копируется.

## Automation handoff

Проверено 2026-07-14:

- `amn2-upstream-orchestrator`: ACTIVE, weekly Sunday 10:00, prompt динамически
  читает первый control block и не привязан к Phase 10 plan;
- legacy PRVTPRO/KYORESUAS/Amnezia chain: PAUSED;
- unrelated active automations не менялись.

После создания отдельного Phase 11 task активный heartbeat нужно привязать к
новому task или оставить его dynamic-retarget behavior. До этого он обязан
читать Phase 11 control block и не продолжать старый Phase 10 plan.

## Следующая команда

В новом task начать с:

```text
AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_START
```

Первый concrete engineering gate:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_3C91601_PRIVATE_TELEGRAM_SINGLE_ADMIN_TRANSIENT_SMOKE_GATE
```
