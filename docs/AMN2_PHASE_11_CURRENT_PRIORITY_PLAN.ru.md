# AMN2 Phase 11 current priority plan

Актуально: 2026-07-15 после fail-closed attempt 4, sanitized OCI gzip layer
diagnosis и double-binding TDD fix. Attempts 1-4 не создали ciphertext;
approval остаётся not consumed.

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
web=active_enabled_loopback_only
regular_bot=inactive_disabled
write_gates=false_false
awg=running_restart_0_peers_12_set_unchanged
old_recovery_fallback=retained_sealed_conditionally
second_vps=clean_ssh_only|temporary_restore_001a_role
```

## Закрыто в P0

| Критичность | ID | Результат |
|---|---|---|
| Критично | `PHASE11-TELEGRAM-001` | transient first-admin exact `/start` smoke passed; one response; production DB unchanged; cleanup passed |
| Критично | `PHASE11-TELEGRAM-002` | persistent bot activation held; regular service remains disabled; local hardening follow-up defined |
| Критично | `PHASE11-OPS-001` | bounded runtime/recovery snapshot healthy; no failed units or AMN2/Docker error rows; AWG invariant passed |
| Критично | `PHASE11-RECOVERY-001` | old bundle/key retained sealed until canonical full-secret restore rehearsal; no deletion |
| Очень важно | second VPS retention audit | clean SSH-only host retained temporarily for `RESTORE-001A`; not production DR or long-term fleet |

## P0 — критично, выполнять следующим

### C1. `PHASE11-RESTORE-001A` canonical full-secret disposable rehearsal

Состояние:
`attempt-4-failed-closed|oci-gzip-double-binding-fix-verified|security-docs-commit-push-then-retry`.
Exact approval получен, но не consumed. Найденный Medium blocker
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
yes. Cleanup/re-audits прошли, AWG untouched. Следующий порядок — docs/status
commit/push и approved retry.

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
используют один canonical PNG; security scan clean. Production всё ещё
`801f8c3`, поэтому новый logo не deployed. Не менять production overlay до
завершения или явного пересмотра pin `RESTORE-001A`. После него подготовить
отдельный package/rollout gate без bot start/enable. Telegram profile photo —
отдельная live identity mutation и требует другого exact gate.

### C3. Recovery and second-VPS retirement gates

Только после `RESTORE-001A=pass`:

1. Exact destructive gate на удаление двух старых ciphertext copies, receipts
   и старого symmetric key.
2. Повторный clean audit второго VPS.
3. Exact provider retirement gate.
4. После provider deletion — локальное удаление только staging SSH key и его
   known-host binding.

Canonical ciphertext/key и production SSH binding не трогать.

### C4. Billing cutoff visibility

До provider renewal получить точную дату/стоимость read-only из кабинета или
от оператора. Если `RESTORE-001A` не согласован до cutoff, не продлевать второй
VPS молча: подготовить retirement либо явное one-cycle extension decision.

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
GPT-5.6 SOL -> COMMIT_PUSH_PHASE11_RESTORE_001A_OCI_CONFIG_PATH_COMPATIBILITY_FIX
```

Двойная:

```text
GPT-5.6 SOL -> COMMIT_PUSH_PHASE11_RESTORE_001A_OCI_CONFIG_PATH_COMPATIBILITY_FIX -> RETRY_ALREADY_APPROVED_RESTORE_001A
```

Тройная:

```text
GPT-5.6 SOL -> COMMIT_PUSH_PHASE11_RESTORE_001A_OCI_CONFIG_PATH_COMPATIBILITY_FIX -> RETRY_ALREADY_APPROVED_RESTORE_001A -> STAGING_ISOLATED_FULL_SECRET_VERIFY_AND_MANDATORY_CLEANUP
```

Четверная:

    GPT-5.6 SOL -> COMMIT_PUSH_PHASE11_RESTORE_001A_OCI_CONFIG_PATH_COMPATIBILITY_FIX -> RETRY_ALREADY_APPROVED_RESTORE_001A -> STAGING_ISOLATED_FULL_SECRET_VERIFY_AND_MANDATORY_CLEANUP -> PRODUCTION_AWG_REAUDIT

Более — рекомендовано:

```text
GPT-5.6 SOL -> COMMIT_PUSH_PHASE11_RESTORE_001A_OCI_CONFIG_PATH_COMPATIBILITY_FIX -> RETRY_ALREADY_APPROVED_RESTORE_001A -> STAGING_ISOLATED_FULL_SECRET_VERIFY_AND_MANDATORY_CLEANUP -> PRODUCTION_AWG_REAUDIT -> DECIDE_OLD_FALLBACK_AND_SECOND_VPS_SAFE_RETIREMENT_GATES -> PREPARE_6ABC620_CANONICAL_LOGO_PRIVATE_OVERLAY_ROLLOUT_GATE -> IMPLEMENT_TELEGRAM_002A_LOCAL_PERSISTENT_ADMISSION_AND_UNIT_HARDENING
```
