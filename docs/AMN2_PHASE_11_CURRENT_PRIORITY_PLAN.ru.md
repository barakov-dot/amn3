# AMN2 Phase 11 current priority plan

Актуально: 2026-07-17 после live pass
`PHASE11-ROLLOUT-0B858C5` combined private overlay.

Этот файл задаёт текущий исполняемый порядок Phase 11. Полная продуктовая
карта и exclusions остаются в
`docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md`, а самый
новый фактический state всегда берётся из первого блока
`docs/PROJECT_STATUS_CURRENT.ru.md`.

## Текущая опорная точка

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|0b858c5cdbc5b565cc265966a2edfe2d339d65e0|origin_sync|clean
production_overlay=0b858c5|verified
restore_001a_source_pin=801f8c3|approval_scope_unchanged
restore_001a=completed_pass|approval_consumed
web=active_enabled_loopback_only
regular_bot=inactive_disabled
write_gates=false_false
awg=running_restart_0_peers_12_set_unchanged
old_recovery_fallback=retained_sealed_without_deletion|review_by_2026-08-01
second_vps=clean_ssh_only|amn2_no_longer_needed|user_hold_through_weekend_then_repurpose
second_vps_provider=paid_until_2026-08-12_23_18_25|590_rub_month|auto_renew_enabled_observed|no_mutation
brand_001=production_verified_0b858c5|canonical_square_logo_served|old_logo_only_package_superseded
brand_002=production_source_verified_0b858c5|png_1672x941|sha256_bbddfa72d1d1fc37e412d2f4a9b4124001ff91fbd641635e31a47e008fc4611f|telegram_profile_unchanged
telegram_002a=production_source_present_0b858c5|local_hardening_verified|regular_bot_inactive_disabled|activation_separate_002b_gate
package_0b858c5=uploaded_applied_verified|outer_sha256_7866bdd9febe1d6eea701b37a6e4206a8267766a56993f3c02a0c7b30c394b54|source_sha256_e03f13fd6a7bb5cbc5fcee7179f395ea8c2864ebceab01bc351c5904f3cff975|run_20260717T081340Z
package_0b858c5_verification=outer_4|source_383|delta_31|forbidden_0|unsafe_0|symlinks_0|scoped_5|full_918_passed_1_skipped|clean_security_7_of_7_surfaces_5_findings_0
rollout_0b858c5=pass|web_private_healthy|db_unchanged|bot_inactive_disabled|awg_restart_0_peers_12_set_unchanged|rollback_retained_verified
next=review_telegram_002b_persistent_bot_activation_gate_without_activation
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
| Критично | `PHASE11-PACKAGE-0B858C5` | exact combined overlay prepared, verified, pushed, uploaded and applied in run `20260717T081340Z`; independent postflight passed |
| Критично | `PHASE11-ROLLOUT-0B858C5` | production overlay `0b858c5`; private web healthy; square/wide assets verified; database unchanged; bot inactive/disabled; AWG running/restart 0/12 peers/same set; rollback retained verified |
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

Exact combined package подготовлен и проверен:
`dist/amn2-combined-overlay-0b858c5.zip`, SHA-256
`7866BDD9FEBE1D6EEA701B37A6E4206A8267766A56993F3C02A0C7B30C394B54`.
Внутренний exact Git archive source `0b858c5` имеет SHA-256
`E03F13FD6A7BB5CBC5FCEE7179F395EA8C2864EBCEAB01BC351C5904F3CFF975`.
Outer `4`, source `383`, delta `31`; forbidden/unsafe/symlink `0/0/0`.
Scoped tests `5 passed`, полный AMN2 `918 passed, 1 skipped`; sealed security
scan `7/7` receipts, `5` surfaces, findings `0`.

Production переведён с `801f8c3` на `0b858c5` в bounded run
`20260717T081340Z`. Exact package receipt, source delta и assets прошли;
independent postflight подтвердил private healthy web, неизменную database,
regular bot inactive/disabled и AWG running/restart 0/12 peers/same set.
Rollback bundle retained/verified и не понадобился. Установка/admission/start
persistent bot остаётся отдельным `PHASE11-TELEGRAM-002B` gate. Telegram
profile photo и AWG не входят в этот gate.

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

1. `PHASE11-TELEGRAM-002B`: после подтверждённого postflight rollout отдельным exact
   gate установить unit/env contract, выполнить live admission и запустить
   один persistent bot. Проверить identity, webhook empty, backlog 0,
   single-instance, readiness/watchdog и rollback; AWG untouched.
2. `PHASE11-SECOND-VPS-HANDOVER`: перед пользовательской передачей выполнить
   финальный read-only clean audit. Dedicated AMN2 staging key и local
   known-host binding удалять только по отдельной точной фразе; provider/VPS не
   удалять. AMN2 уже не нуждается в этом VPS.
3. `PHASE11-RECOVERY-001`: old fallback оставить sealed; до review не позднее
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
GPT-5.6 SOL -> REVIEW_PHASE11_0B858C5_COMBINED_PRIVATE_OVERLAY_LIVE_GATE
```

Двойная:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_0B858C5_COMBINED_PRIVATE_OVERLAY_LIVE_GATE -> PREPARE_EXACT_PHASE11_0B858C5_COMBINED_PRIVATE_OVERLAY_APPROVAL_PHRASE
```

Тройная:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_0B858C5_COMBINED_PRIVATE_OVERLAY_LIVE_GATE -> PREPARE_EXACT_PHASE11_0B858C5_COMBINED_PRIVATE_OVERLAY_APPROVAL_PHRASE -> AFTER_APPROVAL_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_AND_AWG_UNTOUCHED
```

Четверная:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_0B858C5_COMBINED_PRIVATE_OVERLAY_LIVE_GATE -> PREPARE_EXACT_PHASE11_0B858C5_COMBINED_PRIVATE_OVERLAY_APPROVAL_PHRASE -> AFTER_APPROVAL_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_AND_AWG_UNTOUCHED -> SYNC_PHASE11_0B858C5_ROLLOUT_STATUS_COMMIT_AND_PUSH
```

Более — рекомендовано:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_0B858C5_COMBINED_PRIVATE_OVERLAY_LIVE_GATE -> PREPARE_EXACT_PHASE11_0B858C5_COMBINED_PRIVATE_OVERLAY_APPROVAL_PHRASE -> AFTER_APPROVAL_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_AND_AWG_UNTOUCHED -> SYNC_PHASE11_0B858C5_ROLLOUT_STATUS_COMMIT_AND_PUSH -> AFTER_POSTFLIGHT_REVIEW_PHASE11_TELEGRAM_002B_PERSISTENT_BOT_ACTIVATION_GATE
```

## TELEGRAM-002B staged persistent activation — local implementation closeout

`TELEGRAM-002B` design/TDD/local executor завершены и origin-ready; live
activation не выполнена. Remote SHA:
`14747241F1A0E0545CF8B96329E90708F7CC80AF639872968DA03A1783200C64`.
Focused `18 passed`, canonical `113 passed`, Bash/PowerShell parse pass,
fresh complete Security diff review `0 reportable findings`.

Критичный следующий gate — отдельная exact live approval для bounded
`preflight -> stage -> first-admin /start -> accept -> postflight`. До него
regular bot остаётся inactive/disabled, Telegram profile и production DB не
трогаются, AWG не останавливается и не изменяется.

Copy-ready, ещё не потреблённая phrase:

```text
APPROVE_PHASE11_TELEGRAM_002B_REMOTE_ORCHESTRATOR_SHA_14747241F1A0E0545CF8B96329E90708F7CC80AF639872968DA03A1783200C64_0B858C5_EXACT_UNIT_ENV_TELEGRAM_PREFLIGHT_DISABLED_FIRST_STAGE_FIRST_CONFIGURED_ADMIN_SINGLE_START_WIDE_HEADER_EXACT_CONFIRM_ACCEPT_ENABLE_POSTFLIGHT_AUTOROLLBACK240_NO_BLIND_DB_RESTORE_WEB_UNTOUCHED_AND_AWG_UNTOUCHED
```

Evidence: `research/amn2/phase-11-telegram-002b-staged-persistent-activation-gate-2026-07-17.md`.

## TELEGRAM-002B preflight correction override

Первый exact preflight дошёл до VPS, но fail-closed остановился на ожидаемом
venv symlink `/opt/amn2/venv/bin/python`: source/unit/env bindings присутствуют,
stage/accept не выполнялись. Локальный executor теперь разрешает только
`readlink -f`-resolved regular executable target для Python; остальные inputs
остаются strict non-symlink. Новый remote SHA:
`3E6D42D6D7184BD7A05402585A85652C2319D1E0E9E8076217057AE5EE948881`.

До новой literal approval-фразы live gate остановлен; AWG и regular bot
остаются без изменений.

```text
APPROVE PHASE11_TELEGRAM_002B_REMOTE_ORCHESTRATOR_SHA_3E6D42D6D7184BD7A05402585A85652C2319D1E0E9E8076217057AE5EE948881_0B858C5_EXACT_UNIT_ENV_TELEGRAM_PREFLIGHT_DISABLED_FIRST_STAGE_FIRST_CONFIGURED_ADMIN_SINGLE_START_WIDE_HEADER_EXACT_CONFIRM_ACCEPT_ENABLE_POSTFLIGHT_AUTOROLLBACK240_NO_BLIND_DB_RESTORE_WEB_UNTOUCHED_AND_AWG_UNTOUCHED
```

## TELEGRAM-002B journal-ingest correction override

Preflight с SHA `3E6D42...` прошёл. Disabled-first stage
`20260717T115918Z` остановился fail-closed до `/start`: единичная проверка
journald опередила появление очищенного admission receipt. Последующая
read-only диагностика нашла exact marker counts `1/1/1`, errors `0`;
rollback receipt и повторный безопасный preflight подтверждены. Бот остался
inactive/disabled, stale timer остановлен после проверки, AWG не изменялся.

Исправление добавляет максимум 15 секунд bounded polling только очищенного
receipt и снимает exact run-id timer после немедленного успешного rollback.
Security review дополнительно закрыл signal-continuation: после rollback
executor обязан завершиться nonzero и не продолжать stage/accept. Новый
remote SHA:
`FA3F979E3D2DEEB0EF2F53E97A79ECECCADCA6F853C8587A9973D192C49CEB3F`.
Все прежние SHA-bound approval-фразы недействительны.

Post-fix receipts: focused `21 passed`, canonical `116 passed`, Bash and
PowerShell syntax pass, TERM compensation exits `143` before privileged
stage continuation. Fresh Security rescan closed all `9/9` rows and both
former candidates with `0 reportable findings`. Exact phrase remains
withheld until commit, push and origin readback.

```text
approval_phrase=WITHHELD_UNTIL_TEST_SECURITY_COMMIT_PUSH_AND_ORIGIN_SYNC
```

## TELEGRAM-002B exact single-line receipt correction override

FA3F fresh preflight прошёл на production. Single-use disabled-first stage
остановился fail-closed до `/start` с
`sanitized admission receipt missing`; accept/enable/postflight не
выполнялись. Независимый повторный preflight подтвердил rollback: regular bot
inactive/disabled/process 0, web healthy, DB `15/88` с прежним counts hash,
Telegram backlog 0, AWG running/restart 0/peers 12 с прежними container и
peer-set hashes.

Root cause: `0b858c5` runtime выводит все admission-поля одной канонической
строкой, а verifier ошибочно искал backlog/allowed-updates в начале отдельных
строк. Новый verifier принимает ровно одну полную fixed-string строку и
fail-closed отклоняет 0, 2+, partial, prefixed и suffixed receipts.

```text
phase11_telegram_002b_fa3f_preflight=pass
phase11_telegram_002b_fa3f_stage=fail_closed_before_operator_start|receipt_shape_mismatch
phase11_telegram_002b_operator_start=false|accept=false|enable=false|postflight=false
phase11_telegram_002b_postfailure_preflight=pass
phase11_telegram_002b_regular_bot=inactive_disabled|process_0
phase11_telegram_002b_awg=running|restart_0|peers_12|hashes_unchanged
phase11_telegram_002b_new_remote_sha256=56BE81549B86B5DBF09AA23A8513E652F6AF344E88C131FC8EAA2D5D5403F2CE
phase11_telegram_002b_new_runner_sha256=04DF10C9305CFA46843981A851A07B98B658A92859135A8180BCE15363F39951
phase11_telegram_002b_tests=focused_21_passed|canonical_116_passed|syntax_pass|diff_check_pass
phase11_telegram_002b_security=complete_3_of_3|reportable_findings_0
phase11_telegram_002b_fa3f_authority=consumed_and_invalidated
phase11_telegram_002b_new_approval=required
approval_phrase=WITHHELD_UNTIL_TEST_SECURITY_COMMIT_PUSH_AND_ORIGIN_SYNC
```

Критичный release blocker остаётся тем же: после origin sync получить новую
literal SHA-bound approval, повторить `preflight -> stage -> /start -> exact
wide-header confirmation -> accept -> postflight`, затем провести
60-минутное наблюдение. AWG не останавливать и не изменять.
