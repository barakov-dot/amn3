# AMN2 Phase 11 current priority plan

Актуально: 2026-07-15 после решения сохранить old fallback sealed, завершения
AMN2-роли второго VPS и подготовки clean-scanned canonical-logo package.

Этот файл задаёт текущий исполняемый порядок Phase 11. Полная продуктовая
карта и exclusions остаются в
`docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md`, а самый
новый фактический state всегда берётся из первого блока
`docs/PROJECT_STATUS_CURRENT.ru.md`.

## Текущая опорная точка

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|6abc620|origin_sync
production_overlay=801f8c3
restore_001a_source_pin=801f8c3|approval_scope_unchanged
restore_001a=completed_pass|approval_consumed
web=active_enabled_loopback_only
regular_bot=inactive_disabled
write_gates=false_false
awg=running_restart_0_peers_12_set_unchanged
old_recovery_fallback=retained_sealed_without_deletion|review_by_2026-08-01
second_vps=clean_ssh_only|amn2_no_longer_needed|user_hold_through_weekend_then_repurpose
second_vps_provider=paid_until_2026-08-12_23_18_25|590_rub_month|auto_renew_enabled_observed|no_mutation
brand_001=package_ready_6abc620|security_findings_0|production_still_801f8c3
telegram_002a=local_design_gate_next|production_bot_inactive_disabled
```

## Закрыто в P0

| Критичность | ID | Результат |
|---|---|---|
| Критично | `PHASE11-TELEGRAM-001` | transient first-admin exact `/start` smoke passed; one response; production DB unchanged; cleanup passed |
| Критично | `PHASE11-TELEGRAM-002` | persistent bot activation held; regular service remains disabled; local hardening follow-up defined |
| Критично | `PHASE11-OPS-001` | bounded runtime/recovery snapshot healthy; no failed units or AMN2/Docker error rows; AWG invariant passed |
| Критично | `PHASE11-RESTORE-001A` | canonical v2 full-secret disposable restore passed; isolated AWG12 and loopback web/DB verified; cleanup and production re-audits passed |
| Критично | `PHASE11-RECOVERY-001` | old fallback retained sealed without deletion; do not open/copy/move/delete; review by 2026-08-01 |
| Очень важно | second VPS AMN2 role | AMN2 no longer needs it; host clean SSH-only; user keeps it through the weekend and then repurposes it |
| Очень важно | `PHASE11-BRAND-001` package | exact `6abc620` private overlay package built and verified; security coverage 7/7, findings 0; not deployed |

## P0/P1 — критично, выполнять следующим

### C1. `PHASE11-RESTORE-001A` canonical full-secret disposable rehearsal

Состояние:
`completed-pass|mandatory-cleanup-pass|production-unchanged`.
Exact approval consumed. Canonical v2 static verification, in-memory plaintext
stream, isolated AWG12, loopback/outbound-denied web, unchanged database и
disabled bot contracts прошли. Второй VPS после cleanup снова clean SSH-only;
production overlay `801f8c3`, web/DB и AWG invariants прошли re-audit.

История fixes, сохранившая fail-closed binding: найденный Medium blocker
`P11-LEGACY-IMAGE-CONFIG-UNBOUND-001` исправлен: runtime-complete v2
связывает canonical executable Config SHA-256, `amd64/linux`, RootFS DiffIDs
и фактические layer bytes. Проверка: runtime 15 passed, recovery scoped 41
passed, полный root scope 70 passed, independent verifier 35 passed. Clean
security scan: complete coverage, 6/6 full-file receipts, 0 findings. Fix
закоммичен/pushed в root/docs commit `280da45`.

Attempt 1 writer остановился до создания ciphertext на
`image archive config digest is invalid`. Failure-path cleanup и production
re-audits прошли. Sanitized diagnosis доказал safe OCI blob layout для Config
и шести layers. Общий validator теперь принимает только exact legacy
`<digest>.json` или OCI `blobs/sha256/<digest>`; Config self-hash, executable
Config, platform, RootFS и layer bytes остаются bound. RED 3 failed, GREEN 3
passed, recovery 44 passed, canonical root 73 passed. Clean scan: 1/1 full-file
receipt, 4 surfaces, 9 sealed artifacts, 0 findings. OCI fix committed/pushed
как `bc67919`.

Attempt 2 затем дошёл только до writer и остановился до ciphertext на
`immutable image archive unexpectedly contains repo tags`. Production
`docker image save` сохраняет единственный canonical local tag даже при export
по immutable image ID. Cleanup и обязательные runtime/OPS re-audits прошли;
AWG running/restart 0/12 peers/same set. Минимальный fix принимает только
`RepoTags=[]` или exact singleton ожидаемого canonical reference. Чужие,
дополнительные и дублированные tags остаются fail-closed; все Config/platform/
RootFS/layer bindings сохранены. RED 3 failed, GREEN 6 passed, recovery 48
passed, canonical root 77 passed. Independent security-focused review:
Critical/Important/Minor `0/0/0`, ready yes. Следующий порядок — docs/status
commit, push, затем retry в неизменном approved scope `801f8c3`.

Attempt 3 подтвердил, что archive `RepoTags` не является canonical singleton:
sanitized diagnostic доказал присутствующий key со значением JSON `null`.
Config и шесть OCI layers canonical/self-bound. Новый минимальный fix требует
наличие `RepoTags` key и принимает только `null`, `[]` или exact singleton
canonical reference; missing/malformed/foreign/additional/duplicate остаются
fail-closed. RED 3 failed, GREEN 8 passed, recovery 50 passed, canonical root
79 passed. Cleanup и re-audits снова прошли; AWG untouched. Следующий порядок
— independent security review `0/0/0`, ready yes; docs/status commit, push и
тот же approved retry.

Attempt 4 дошёл до layer bytes и остановился до ciphertext на raw-vs-DiffID
mismatch. Sanitized diagnostic доказал: 6/6 raw gzip blobs bound к OCI path
digest; 6/6 streamed decompressed layers bound к ordered RootFS DiffIDs;
expanded total 26048512, max layer 7688192. Fix сохраняет обе привязки и вводит
64 MiB per-layer/128 MiB cumulative limits; invalid gzip, wrong content, blob
path tamper и expansion fail closed. До review-fix: RED 3 failed, focused 8,
recovery 56, root 85. Initial security review нашёл uncaught `zlib.error`
и недостаточный cumulative test; оба исправлены через отдельный RED и настоящий
two-layer case. Итог: focused 9, recovery 57, root 86; rereview `0/0/0`, ready
yes. Cleanup/re-audits прошли, AWG untouched. Последующие live diagnostics
добавили строгие compatibility contracts для canonical tar root, transient
containerd loopback, legacy runtime image ID, IPv6 link-local AWG address и
canonical systemd CIDR properties. Финальный full-secret run прошёл.

- использует чистый второй VPS как trusted disposable environment;
- доказывает полный canonical offline restore path;
- не трогает production и не останавливает AWG;
- после pass разблокирует retirement старого recovery fallback;
- после cleanup убирает основную причину держать второй VPS.

### C2. `PHASE11-TELEGRAM-002A` persistent admission and unit hardening

Local product/engineering slice:

- identity/webhook/backlog admission до full dispatcher polling;
- explicit allowed updates, single-instance and bounded startup receipt;
- watchdog/liveness and non-looping restart policy;
- narrowed systemd filesystem/device/home sandbox;
- negative tests for backlog, webhook, identity, timeout and duplicate runtime;
- package/rollout leaves bot inactive and disabled.

Этот slice не включает production bot enable/start. Activation останется
отдельным exact gate после code/tests/package/security review.

### C2a. `PHASE11-BRAND-001` canonical logo production rollout

Local source завершён и pushed в `6abc620`: bot `/start`, web login/dashboard
используют один canonical PNG. Exact private overlay package подготовлен:
`dist/amn2-canonical-logo-overlay-6abc620.zip`, SHA-256
`2683420dd7a705c96490dc1878d14d208986209bf8eb1b6e1b066d31b17932f5`.
Focused tests: 26 passed; independent exact source-delta scope: 14 passed;
package/bash/ZIP/diff/toolchain checks passed. Canonical security scan: 7/7
receipts, findings 0, snapshot
`36d08ba1945558ee590e3c8d1057eeb37ad634141ae432cb070355ab242f38fb`.

Production остаётся `801f8c3`: package не uploaded и не applied. Live rollout
остаётся за exact phrase из
`docs/AMN2_PHASE_11_6ABC620_CANONICAL_LOGO_OVERLAY_GATE.ru.md`; regular bot
остаётся inactive/disabled, Telegram profile photo не меняется, AWG untouched.

### C3. Recovery fallback retention и second-VPS AMN2 handover

Old recovery fallback сохранить sealed без удаления минимум до повторного
review не позднее 2026-08-01. В текущем slice его не открывать, не копировать,
не перемещать и не удалять. Любое destructive действие остаётся отдельным
exact gate; canonical ciphertext/key и production SSH binding не трогать.

Второй VPS AMN2 больше не нужен. После `RESTORE-001A` он повторно проверен как
clean SSH-only: AMN2 tree/units/artifacts отсутствуют, Docker отсутствует,
failed units 0. Пользователь держит сервер до выходных как краткий резерв и
затем передаёт под другой функционал. Это handover, а не provider retirement:
не удалять VPS, не отменять тариф и не менять автопродление.

Перед передачей выполнить ещё один read-only clean audit. После отдельной
точной фразы допускается убрать только dedicated AMN2 staging SSH key и его
local known-host binding; remote server, production и AWG не менять.

### C4. Billing visibility — read-only завершено

Provider portal read-only показал: оплачено до `12.08.2026 23:18:25` в
provider display, текущий месячный период `590,00 RUB`, auto-renew включён.
Никаких provider/billing mutations не выполнено. Дальнейшая судьба тарифа
относится к новому пользовательскому назначению VPS, не к AMN2 handover.

## P1 — очень важно после критического recovery/bot пути

| Порядок | ID | Scope |
|---:|---|---|
| 1 | `PHASE11-DEVICE-001` | authenticated read-only Device Passport/lifecycle list/detail UX |
| 2 | `PHASE11-API-001` | private scoped API-key lane: scope, TTL, revoke, audit, loopback-only smoke |
| 3 | `PHASE11-DEVICE-002` | one-config-per-device default, quota and owner-shared exception consistency |
| 4 | `PHASE11-ENROLL-001` | deferred until explicit self-service requirement; abuse/rate-limit design first |

## P2 — важно, после P1 и named gates

1. `PHASE11-DRIFT-001` history/retention/explainable UX.
2. `PHASE11-DRIFT-002` OperationPlan preview/approve/apply/verify/rollback;
   never automatic by default.
3. `PHASE11-IPAM-001` dynamic subnet source-of-truth and conflict validation.
4. `PHASE11-FLEET-001` capacity/placement/migration only after IPAM; the
   current same-provider test VPS is not retained merely for this future item.
5. `PHASE11-RESTORE-001` product single-flight/idempotency/backup-before-write
   restore path after the `001A` operational rehearsal.
6. `PHASE11-CLIENT-001` reacceptance only on published release/security/config
   format triggers.

## P3 — нормально / design-later

- `PHASE11-AUTH-001` web-admin 2FA recovery/lockout/rate-limit design;
- `PHASE11-ROUTING-001` domain-zone exclusion policy, default-off;
- `PHASE11-BOTS-001` separate support/news identities and runtimes;
- `PHASE11-DOCS-001` OpenAPI grouping, DESIGN, naming and Russian-first polish;
- `PHASE11-METRICS-001` privacy-safe metrics retention/expansion.

## Обязательный порядок каждого engineering/live блока

```text
product_and_engineering_evidence
-> scoped_tests
-> diff_and_security_review
-> docs_and_status_sync
-> commit
-> push
```

Live/destructive/secret-bearing steps additionally require a fresh exact named
gate. Не использовать approvals из Phase 10 или уже consumed approvals Phase
11. AWG не останавливать для тестов.

## Следующая рекомендация

Одиночная:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_TELEGRAM_002A_FAIL_CLOSED_PERSISTENT_ADMISSION_DESIGN
```

Двойная:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_TELEGRAM_002A_FAIL_CLOSED_PERSISTENT_ADMISSION_DESIGN -> APPROVE_PHASE11_TELEGRAM_002A_DESIGN
```

Тройная:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_TELEGRAM_002A_FAIL_CLOSED_PERSISTENT_ADMISSION_DESIGN -> APPROVE_PHASE11_TELEGRAM_002A_DESIGN -> WRITE_AND_COMMIT_TELEGRAM_002A_DESIGN_SPEC
```

Четверная:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_TELEGRAM_002A_FAIL_CLOSED_PERSISTENT_ADMISSION_DESIGN -> APPROVE_PHASE11_TELEGRAM_002A_DESIGN -> WRITE_AND_COMMIT_TELEGRAM_002A_DESIGN_SPEC -> WRITE_TELEGRAM_002A_TDD_IMPLEMENTATION_PLAN
```

Более — рекомендовано:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_TELEGRAM_002A_FAIL_CLOSED_PERSISTENT_ADMISSION_DESIGN -> APPROVE_PHASE11_TELEGRAM_002A_DESIGN -> WRITE_AND_COMMIT_TELEGRAM_002A_DESIGN_SPEC -> WRITE_TELEGRAM_002A_TDD_IMPLEMENTATION_PLAN -> IMPLEMENT_TELEGRAM_002A_LOCAL_PERSISTENT_ADMISSION_AND_UNIT_HARDENING -> RUN_SCOPED_TESTS_DIFF_AND_SECURITY_REVIEW -> SYNC_STATUS_COMMIT_AND_PUSH -> PREPARE_6ABC620_CANONICAL_LOGO_LIVE_ROLLOUT_APPROVAL
```
