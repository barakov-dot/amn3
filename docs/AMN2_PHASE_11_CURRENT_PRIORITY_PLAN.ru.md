# AMN2 Phase 11 current priority plan

Актуально: 2026-07-16 после завершения и push
`PHASE11-BRAND-002` wide language-selection header на source `0b858c5`.

Этот файл задаёт текущий исполняемый порядок Phase 11. Полная продуктовая
карта и exclusions остаются в
`docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md`, а самый
новый фактический state всегда берётся из первого блока
`docs/PROJECT_STATUS_CURRENT.ru.md`.

## Текущая опорная точка

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|0b858c5cdbc5b565cc265966a2edfe2d339d65e0|origin_sync|clean
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
brand_001=integrated_in_descendant_0b858c5|square_assets_preserved|old_logo_only_package_superseded_as_combined_candidate|production_still_801f8c3
brand_002=wide_language_selection_header_complete|source_0b858c5|png_1672x941|sha256_bbddfa72d1d1fc37e412d2f4a9b4124001ff91fbd641635e31a47e008fc4611f|clean_security_findings_0|production_not_deployed
telegram_002a=local_implementation_complete|contained_in_source_0b858c5|scoped_113|full_915_passed_1_skipped|clean_security_15_of_15_findings_0|production_bot_inactive_disabled
next=prepare_0b858c5_combined_private_overlay_package_and_exact_rollout_gate
```

## Закрыто в P0

| Критичность | ID | Результат |
|---|---|---|
| Критично | `PHASE11-TELEGRAM-001` | transient first-admin exact `/start` smoke passed; one response; production DB unchanged; cleanup passed |
| Критично | `PHASE11-TELEGRAM-002` | persistent bot activation held; regular service remains disabled; local hardening follow-up completed in `08c56f2` and is contained in source `0b858c5` |
| Критично | `PHASE11-TELEGRAM-002A` | local fail-closed admission/unit hardening complete and pushed; contained in `0b858c5`; scoped 113, full 915/1 skipped; clean scan 15/15, findings 0; no live activation |
| Критично | `PHASE11-OPS-001` | bounded runtime/recovery snapshot healthy; no failed units or AMN2/Docker error rows; AWG invariant passed |
| Критично | `PHASE11-RESTORE-001A` | canonical v2 full-secret disposable restore passed; isolated AWG12 and loopback web/DB verified; cleanup and production re-audits passed |
| Критично | `PHASE11-RECOVERY-001` | old fallback retained sealed without deletion; do not open/copy/move/delete; review by 2026-08-01 |
| Очень важно | second VPS AMN2 role | AMN2 no longer needs it; host clean SSH-only; user keeps it through the weekend and then repurposes it |
| Очень важно | `PHASE11-BRAND-001` source | canonical square logo is contained in descendant `0b858c5`; old `6abc620` package remains not deployed and is no longer the current combined candidate |
| Очень важно | `PHASE11-BRAND-002` source | exact 1672x941 language-selection header integrated and pushed in `0b858c5`; `/start` role-specific usage and text-only fallback verified; square assets unchanged; no live activation |

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

Состояние: `completed-local|08c56f2|origin-sync|production-not-activated`.

- fail-closed identity/webhook/backlog/poll-ownership admission и repeated
  pre-poll state check;
- explicit `message,callback_query`, process-lifetime lock и update-task
  concurrency limit `8`;
- один overall pre-poll timeout до 120 seconds, systemd
  `TimeoutStartSec=135s`, readiness/watchdog и bounded restart policy;
- narrowed filesystem/device/home sandbox, stable sanitized failures;
- RED 3 expected failures, GREEN 14; scoped 113, full 915 passed/1 skipped;
- clean security scan 15/15 receipts, findings 0.

Production bot enable/start, Telegram API/profile, VPS, web/DB и AWG не
затронуты. Activation остаётся отдельным exact gate после нового combined
package/rollout. Перед будущим VPS-write mode обязателен tested
service-readable non-home SSH key/known-hosts path при сохранении
`ProtectHome=true`.

### C2a. Combined `0b858c5` production package and rollout

Canonical square-logo commit `6abc620` и Telegram hardening commit `08c56f2`
теперь являются предками source `0b858c5`, который добавляет отдельный wide
language-selection header. Старый logo-only ZIP остаётся валидным historical
artifact, но не является текущим production candidate. Нужно собрать новый
exact combined package на `0b858c5`, связать source digest/apply/runbook/
rollback, повторить package tests и clean security review.

Production остаётся `801f8c3`: новый package ещё не создан, не uploaded и не
applied. Первый live transaction должен обновить source/web assets с regular
bot всё ещё inactive/disabled. Отдельный следующий gate уже после postflight
может устанавливать/admit/start persistent bot. Telegram profile photo и AWG
не входят ни в один из этих gates.

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

## Остаток Phase 11 по критичности

### Критичные

1. `PHASE11-PACKAGE-0B858C5`: собрать новый combined private overlay из exact
   `0b858c5`, включающий canonical square logo, wide language-selection header
   и Telegram hardening; проверить checksum, состав, source binding, apply и
   rollback.
   Результат — copy-ready пакет; production пока не меняется.
2. `PHASE11-ROLLOUT-0B858C5`: отдельным exact gate применить combined source
   overlay, перезапустив только private web при snapshot/rollback. Regular bot
   остаётся inactive/disabled; AWG не останавливать и не перезапускать.
3. `PHASE11-TELEGRAM-002B`: только после postflight rollout отдельным exact
   gate установить unit/env contract, выполнить live admission и запустить
   один persistent bot. Проверить identity, webhook empty, backlog 0,
   single-instance, readiness/watchdog и rollback; AWG untouched.
4. `PHASE11-SECOND-VPS-HANDOVER`: перед пользовательской передачей выполнить
   финальный read-only clean audit. Dedicated AMN2 staging key и local
   known-host binding удалять только по отдельной точной фразе; provider/VPS не
   удалять. AMN2 уже не нуждается в этом VPS.
5. `PHASE11-RECOVERY-001`: old fallback оставить sealed; до review не позднее
   2026-08-01 не открывать, не копировать, не перемещать и не удалять.

### Очень важно

1. `PHASE11-TELEGRAM-SSH-PREREQ`: до bot VPS-write mode вынести SSH key и
   known-hosts в service-readable non-home path, проверить права и сохранить
   `ProtectHome=true`.
2. `PHASE11-DEVICE-001`: authenticated read-only Device Passport/lifecycle
   list/detail UX — оператор видит состояние устройства без live mutation.
3. `PHASE11-API-001`: private scoped API-key lane со scope, TTL, revoke, audit
   и loopback-only smoke.
4. `PHASE11-DEVICE-002`: согласовать one-config-per-device default, quota и
   owner-shared exception во всех bot/web/API путях.
5. `PHASE11-ENROLL-001`: открывать self-service Enrollment только при явной
   продуктовой потребности; сначала abuse/rate-limit design.

### Важно

1. `PHASE11-DRIFT-001`: история, retention и объяснимый operator UX.
2. `PHASE11-DRIFT-002`: `OperationPlan` preview/approve/apply/verify/rollback;
   автоматический apply по умолчанию запрещён.
3. `PHASE11-RESTORE-001`: product restore с single-flight, idempotency,
   backup-before-write, verify и rollback на базе успешного `001A` rehearsal.
4. `PHASE11-CLIENT-001`: reacceptance только при опубликованном release,
   security или config-format trigger; baseline-файл не менять без такого
   события.

### Средней критичности

1. `PHASE11-IPAM-001`: dynamic subnet source-of-truth, reserved-address и
   conflict validation.
2. `PHASE11-FLEET-001`: capacity/placement/migration только после IPAM.
   Текущий второй VPS для этого не удерживается и будет перепрофилирован.
3. `PHASE11-AUTH-001`: web-admin 2FA, recovery, lockout и rate-limit design.
4. `PHASE11-ROUTING-001`: domain-zone exclusion policy, default-off.

### Простые доработки

1. `PHASE11-BOTS-001`: описать отдельные identities/runtimes для support/news
   bots без смешивания с production admin bot.
2. `PHASE11-DOCS-001`: OpenAPI grouping, `DESIGN.md`, naming и Russian-first
   operator docs.
3. `PHASE11-METRICS-001`: privacy-safe metrics retention/expansion без raw
   long-term telemetry.
4. Дополнить activation/recovery runbooks короткими operator checklist после
   фактического combined rollout.

### Косметические доработки

1. Telegram profile photo применить вручную через отдельный identity gate;
   это не часть source rollout или bot activation.
2. Решить, нужен ли облегчённый PNG/thumbnail и отдельная C2PA/metadata policy
   для brand assets. Exact wide source сохраняет provenance metadata; текущая
   security-проверка чистая, а удаление metadata не входит в functional slice.
3. Выравнять оставшиеся UI labels, русские формулировки и brand spacing после
   functional acceptance, не смешивая это с security/live gates.

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
GPT-5.6 SOL -> PREPARE_PHASE11_0B858C5_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_PACKAGE_AND_ROLLOUT_GATE
```

Двойная:

```text
GPT-5.6 SOL -> PREPARE_PHASE11_0B858C5_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_PACKAGE_AND_ROLLOUT_GATE -> VERIFY_PHASE11_0B858C5_PACKAGE_CHECKSUM_CONTENTS_SOURCE_BINDING_AND_ROLLBACK_CONTRACT
```

Тройная:

```text
GPT-5.6 SOL -> PREPARE_PHASE11_0B858C5_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_PACKAGE_AND_ROLLOUT_GATE -> VERIFY_PHASE11_0B858C5_PACKAGE_CHECKSUM_CONTENTS_SOURCE_BINDING_AND_ROLLBACK_CONTRACT -> RUN_PHASE11_0B858C5_SCOPED_PACKAGE_TESTS_DIFF_AND_CLEAN_SECURITY_REVIEW
```

Четверная:

```text
GPT-5.6 SOL -> PREPARE_PHASE11_0B858C5_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_PACKAGE_AND_ROLLOUT_GATE -> VERIFY_PHASE11_0B858C5_PACKAGE_CHECKSUM_CONTENTS_SOURCE_BINDING_AND_ROLLBACK_CONTRACT -> RUN_PHASE11_0B858C5_SCOPED_PACKAGE_TESTS_DIFF_AND_CLEAN_SECURITY_REVIEW -> SYNC_PHASE11_0B858C5_PACKAGE_GATE_STATUS_COMMIT_AND_PUSH
```

Более — рекомендовано:

```text
GPT-5.6 SOL -> PREPARE_PHASE11_0B858C5_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_PACKAGE_AND_ROLLOUT_GATE -> VERIFY_PHASE11_0B858C5_PACKAGE_CHECKSUM_CONTENTS_SOURCE_BINDING_AND_ROLLBACK_CONTRACT -> RUN_PHASE11_0B858C5_SCOPED_PACKAGE_TESTS_DIFF_AND_CLEAN_SECURITY_REVIEW -> SYNC_PHASE11_0B858C5_PACKAGE_GATE_STATUS_COMMIT_AND_PUSH -> PREPARE_EXACT_PHASE11_0B858C5_PRIVATE_OVERLAY_APPROVAL_PHRASE_WITH_REGULAR_BOT_DISABLED_AND_AWG_UNTOUCHED
```
