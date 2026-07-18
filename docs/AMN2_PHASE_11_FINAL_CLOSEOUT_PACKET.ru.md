# AMN2 Phase 11 Final Closeout Packet

Дата: 2026-07-18.

## Решение

`PHASE11-RELEASE-001` закрывает Phase 11 как
`completed-controlled-private-release`. Решение становится действующим после
того, как commit, содержащий этот packet (`closeout_commit=this_commit`),
успешно пройдёт tests, complete security-diff review, push и exact trusted
origin readback. Итоговый operator result обязан указать разрешённый SHA.

Release остаётся private/operator-only. Он не открывает public web/API,
config generation/delivery, peer creation, write gates, self-service
enrollment, provider mutations или bot VPS-write mode.

## Authoritative release baseline

```text
phase=AMN2 Phase 11 Controlled Launch and Operations
phase_status=completed-controlled-private-release
release_gate=PHASE11-RELEASE-001|pass_after_this_commit_origin_readback
closeout_commit=this_commit
amn2_branch=codex-vps-test-prep
amn2_source=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
amn2_origin_sync=true
amn2_worktree_clean=true
amn3_branch=codex-spark-phase9-docs-sync
production_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
release_mode=controlled_private_operator_only
public_web_api_config_delivery=false_false_false
config_generation_peer_creation=false_false
write_gates=false_false
self_service_enrollment=false
```

## Production acceptance retained

Последний разрешённый live gate — `PHASE11-TELEGRAM-002B`, run
`20260717T192602Z`. Exact first configured administrator подтвердил новый wide
language header. Accept и независимый postflight прошли, затем реальное окно
стабильности длилось `66m13s`.

```text
telegram_002b=activation_and_stability_pass
telegram_run_id=20260717T192602Z
bot=active_enabled_single_instance|restart_0|watchdog_healthy
telegram=identity_match|webhook_empty|backlog_0
web=active_enabled_http_ok_loopback_only
database=integrity_ok|fk_0|only_expected_first_admin_row_delta
awg=unchanged|running|restart_0|peer_set_unchanged
repeat_start_cleanup_stage_accept_rollout=prohibited_not_required
```

Closeout не повторяет live checks, `/start`, cleanup, stage, accept, rollout,
restore или Phase 10 acceptance. Он использует уже принятые receipts и не
меняет VPS, Telegram API/profile, provider, web, database или AWG.

## Закрытые launch gates

| Gate | Итог |
|---|---|
| Phase 10 production rollout/acceptance | закрыто ранее; не переоткрывалось |
| `PHASE11-TELEGRAM-001` transient smoke | pass, exact single admin, bounded cleanup |
| `PHASE11-OPS-001` runtime/recovery health | pass |
| `PHASE11-RESTORE-001A` full-secret disposable rehearsal | pass с mandatory cleanup и production re-audit |
| `PHASE11-RECOVERY-001` fallback decision | retain sealed without deletion |
| `PHASE11-BRAND-001/002` | canonical square logo и wide language header приняты в `0b858c5` |
| `PHASE11-ROLLOUT-0B858C5` | package/apply/postflight pass, rollback retained, AWG unchanged |
| `PHASE11-TELEGRAM-002A` | fail-closed admission/unit hardening deployed |
| `PHASE11-TELEGRAM-002B` | persistent activation и 66-minute stability pass |
| `PHASE11-RELEASE-001` | pass после final tests/security/push/origin readback |

Открытых blockers для controlled private release нет при выполнении
финального origin condition этого packet.

## Safety holds без блокировки release

### Old recovery fallback

До review не позднее 2026-08-01 fallback остаётся sealed. Не открывать, не
копировать, не перемещать и не удалять. Пока этот retention contract
соблюдается, он не является release blocker.

### Второй VPS

AMN2 больше не нуждается во втором VPS. Пользователь держит его временно и
передаст под другой функционал. Непосредственно перед repurpose требуется
отдельный read-only clean handover audit. Provider/VPS mutation, удаление
dedicated key или known-host binding требуют отдельной точной authority и не
входят в этот closeout.

### Future Telegram VPS-write mode

Текущий persistent bot принят только в существующем private read-only режиме.
Перед будущим VPS-write mode требуется отдельный exact gate и проверенный
service-readable non-home SSH key/known-hosts contract при сохранении
`ProtectHome=true`.

## Final verification contract

До commit обязательны:

```text
progress_harness_tests=20_passed
root_full_tests=128_passed
branch_integrity=pass|current_branch_codex-spark-phase9-docs-sync|pre_closeout_base_24dde6e9d49c565a4beebe47ac91fddb79b990e9|intended_paths_8|forbidden_baseline_excluded
git_diff_check=passed
forbidden_baseline_in_diff=false
high_confidence_secret_matches=0
current_replayable_live_authority=0
security_diff_coverage=complete
security_diff_reportable_findings=0
security_scan_id=24dde6e9d49c565a4beebe47ac91fddb79b990e9_20260718T050216Z
security_byte_binding=sealed_manifest_snapshot_equals_index_digest_equals_commit_tree_digest
```

После commit обязательны push, fetch/readback и точное равенство local SHA и
`origin/codex-spark-phase9-docs-sync`. Если любой пункт, включая
`branch_integrity=pass` или `security_byte_binding`, не выполнен, значение
`phase_status` выше не вступает в силу и release не объявляется. Любое изменение
одного из восьми intended paths после scan требует полного rescan; повторный
`git add` аннулирует index-binding receipt до новой проверки.

## Automation state

```text
amn2_upstream_orchestrator=ACTIVE|current_task|original_weekly_contract
legacy_amnezia_upstream=PAUSED
legacy_prvtpro_upstream=PAUSED
legacy_kyoresuas_upstream=PAUSED
```

## Post-release roadmap

P1–P3 product items сохраняются как post-release backlog и не являются
launch blockers без отдельного решения повысить их критичность:

- очень важно: `DEVICE-001`, `API-001`, `DEVICE-002`, `ENROLL-001`, future
  `TELEGRAM-SSH-PREREQ`;
- важно: `DRIFT-001/002`, productized `RESTORE-001`, trigger-only
  `CLIENT-001`;
- средне: `IPAM-001`, затем `FLEET-001`, `AUTH-001`, `ROUTING-001`;
- просто: `BOTS-001`, `DOCS-001`, `METRICS-001`, compact operator runbooks;
- косметика: Telegram profile photo gate, optional light PNG/C2PA policy,
  UI labels и brand spacing.

Любое продолжение product engineering после closeout должно начинаться новым
явно выбранным slice, а не повторением Phase 11 live approvals.

## Declaration

При успешном trusted-origin readback этого commit итоговая декларация:

```text
AMN2_PHASE11_CONTROLLED_PRIVATE_RELEASE=DECLARED
```

AWG continuity и private/operator-only boundaries остаются обязательными.
