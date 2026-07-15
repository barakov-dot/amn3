# AMN2 Phase 11 current priority plan

Актуально: 2026-07-15 после исправления executable-Config binding, полного
root regression и clean security rescan для `PHASE11-RESTORE-001A`.

Этот файл задаёт текущий исполняемый порядок Phase 11. Полная продуктовая
карта и exclusions остаются в
`docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md`, а самый
новый фактический state всегда берётся из первого блока
`docs/PROJECT_STATUS_CURRENT.ru.md`.

## Текущая опорная точка

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|801f8c3|origin_sync
production_overlay=801f8c3
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

Состояние: `approved-pending-docs-commit-push-and-live-retry`. Exact approval
получен, но не consumed. Найденный Medium blocker
`P11-LEGACY-IMAGE-CONFIG-UNBOUND-001` исправлен: runtime-complete v2
связывает canonical executable Config SHA-256, `amd64/linux`, RootFS DiffIDs
и фактические layer bytes. Проверка: runtime 15 passed, recovery scoped 41
passed, полный root scope 70 passed, independent verifier 35 passed. Clean
security scan: complete coverage, 6/6 full-file receipts, 0 findings. Live
rehearsal ещё не запускался; следующий порядок — docs/status, commit, push,
затем выполнение уже одобренного gate.

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
GPT-5.6 SOL -> COMMIT_AND_PUSH_PHASE11_LEGACY_IMAGE_CONFIG_BINDING_SECURITY_FIX
```

Двойная:

```text
GPT-5.6 SOL -> COMMIT_AND_PUSH_PHASE11_LEGACY_IMAGE_CONFIG_BINDING_SECURITY_FIX -> RETRY_ALREADY_APPROVED_RESTORE_001A
```

Тройная:

```text
GPT-5.6 SOL -> COMMIT_AND_PUSH_PHASE11_LEGACY_IMAGE_CONFIG_BINDING_SECURITY_FIX -> RETRY_ALREADY_APPROVED_RESTORE_001A -> STAGING_ISOLATED_FULL_SECRET_VERIFY_AND_MANDATORY_CLEANUP
```

Четверная:

    GPT-5.6 SOL -> COMMIT_AND_PUSH_PHASE11_LEGACY_IMAGE_CONFIG_BINDING_SECURITY_FIX -> RETRY_ALREADY_APPROVED_RESTORE_001A -> STAGING_ISOLATED_FULL_SECRET_VERIFY_AND_MANDATORY_CLEANUP -> PRODUCTION_AWG_REAUDIT

Более — рекомендовано:

```text
GPT-5.6 SOL -> COMMIT_AND_PUSH_PHASE11_LEGACY_IMAGE_CONFIG_BINDING_SECURITY_FIX -> RETRY_ALREADY_APPROVED_RESTORE_001A -> STAGING_ISOLATED_FULL_SECRET_VERIFY_AND_MANDATORY_CLEANUP -> PRODUCTION_AWG_REAUDIT -> DECIDE_OLD_FALLBACK_AND_SECOND_VPS_SAFE_RETIREMENT_GATES -> IMPLEMENT_TELEGRAM_002A_LOCAL_PERSISTENT_ADMISSION_AND_UNIT_HARDENING
```
