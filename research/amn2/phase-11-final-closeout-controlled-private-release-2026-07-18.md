# Phase 11 final closeout and controlled private release evidence

Дата: 2026-07-18.

Статус: `PHASE11-RELEASE-001` ready for conditional declaration by
`closeout_commit=this_commit`; effective only after trusted-origin readback.

## Scope

Этот slice является documentation/evidence closeout. Он не выполняет SSH к
production или second VPS, не вызывает Telegram API, не отправляет сообщения,
не повторяет `/start`, cleanup, stage, accept, rollout или restore, не меняет
provider, web, database и AWG.

## Source and branch receipts

```text
amn2_path=worktrees/amn2-p7-c005-write-install
amn2_branch=codex-vps-test-prep
amn2_head=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
amn2_upstream=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
amn2_clean=true
amn2_origin_sync=true
amn3_branch=codex-spark-phase9-docs-sync
amn3_pre_closeout_head=24dde6e9d49c565a4beebe47ac91fddb79b990e9
forbidden_user_file=docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md|untouched_out_of_scope
```

## Accepted production evidence

```text
production_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
telegram_run_id=20260717T192602Z
telegram_activation=pass
stability_elapsed=66m13s
final_postflight=pass
bot=active_enabled_single_instance_restart_0_watchdog_healthy
telegram=identity_match_webhook_empty_backlog_0
web=active_enabled_http_ok_loopback_only
database=integrity_ok_fk_0
database_delta=only_expected_first_admin_row
awg=unchanged_running_restart_0_peer_set_unchanged
release_mode=private_operator_only
public_web_api_config_delivery=false_false_false
config_generation_peer_creation=false_false
write_gates=false_false
self_service_enrollment=false
current_replayable_live_authority=0
```

Эти receipts уже были приняты и записаны в
`research/amn2/phase-11-telegram-002b-staged-persistent-activation-gate-2026-07-17.md`.
Closeout не создаёт новый live authority и не расширяет их scope.

## Release-blocker reconciliation

Phase 10 rollout/acceptance закрыты и не повторялись. Phase 11 P0 gates для
transient Telegram smoke, runtime/recovery evidence, disposable full-secret
restore rehearsal, recovery retention decision, combined branding/Telegram
hardening rollout, persistent activation и stability observation закрыты.

Единственный remaining blocker был `PHASE11-RELEASE-001`. Он проходит при
одновременном выполнении следующих условий:

1. authoritative source/branch pins совпадают с receipts выше;
2. final progress/full tests проходят;
3. changed-file diff и secret scan чисты;
4. complete Codex Security diff review даёт `0` reportable findings;
5. closeout commit pushed и exact readback совпадает с trusted origin.

## Non-blocking safety work

- Old fallback остаётся sealed без open/copy/move/delete до review не позднее
  2026-08-01.
- Second VPS AMN2 больше не нужен; отдельный read-only audit выполняется только
  перед фактическим пользовательским repurpose.
- Future bot VPS-write mode требует отдельного exact SSH/unit gate.
- P1–P3 product roadmap не повышен до launch-blocker.

## Automation receipt

Read-only local automation inspection после stability closeout подтвердил:

```text
amn2-upstream-orchestrator=ACTIVE|target_current_task|weekly_original_contract
amnezia-weekly-upstream-refresh=PAUSED
prvtpro-weekly-upstream-refresh=PAUSED
weekly-kyoresuas-upstream-refresh=PAUSED
```

## Sanitized command/result ledger

Все команды ниже read-only. Они не печатают prompt automation, credentials,
approval phrases, Telegram identifiers, config payloads или private logs.

### AMN2 source integrity

```powershell
git -C worktrees/amn2-p7-c005-write-install branch --show-current
git -C worktrees/amn2-p7-c005-write-install rev-parse HEAD
git -C worktrees/amn2-p7-c005-write-install rev-parse '@{upstream}'
git -C worktrees/amn2-p7-c005-write-install status --porcelain
```

```text
result_branch=codex-vps-test-prep
result_head=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
result_upstream=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
result_status_rows=0
result=pass|clean|origin_sync
```

### AMN3 branch integrity before closeout commit

```powershell
git branch --show-current
git rev-parse HEAD
git rev-parse origin/codex-spark-phase9-docs-sync
git status --short
```

```text
result_branch=codex-spark-phase9-docs-sync
result_head=24dde6e9d49c565a4beebe47ac91fddb79b990e9
result_origin_pre_closeout=24dde6e9d49c565a4beebe47ac91fddb79b990e9
result_intended_paths=8
result_forbidden_baseline=untracked_out_of_scope
branch_integrity=pass
```

The eight intended closeout paths are the implementation plan, canonical
packet, research ledger and five authoritative Phase 11 status/handoff files.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` is explicitly excluded.

### Test and diff verification

```powershell
python -m pytest tests/test_phase9_progress_harness.py -q
python -m pytest tests -q
git diff --check
```

```text
progress_harness_tests=20_passed
root_full_tests=128_passed
git_diff_check=pass
```

### Secret and stale-authority verification

```powershell
$paths=@(
'docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md',
'docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md',
'docs/AMN2_PHASE_11_FINAL_CLOSEOUT_PACKET.ru.md',
'docs/AMN2_PHASE_11_FIRST_MESSAGE.ru.md',
'docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md',
'docs/PROJECT_STATUS_CURRENT.ru.md',
'docs/superpowers/plans/2026-07-18-phase11-final-closeout-controlled-private-release.ru.md',
'research/amn2/phase-11-final-closeout-controlled-private-release-2026-07-18.md'
)
rg -l --pcre2 '(?i)(?:api[_-]?key|secret|token|password)\s*[:=]\s*["'']?[A-Za-z0-9_\-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{20,}' $paths
```

Result: `matches_0`.

Current-authority scan uses only each authoritative top block plus the three
new full files; historical blocks are excluded by their exact first boundary:

```powershell
$source = @'
from pathlib import Path
sections={
'docs/AMN2_PHASE_11_FIRST_MESSAGE.ru.md':'\n---\n',
'docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md':'## Current execution override',
'docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md':'## Текущий P0 override',
'docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md':'## Current continuation override',
'docs/PROJECT_STATUS_CURRENT.ru.md':'# Предыдущий override',
}
texts=[Path(p).read_text(encoding='utf-8').split(b,1)[0] for p,b in sections.items()]
for p in ('docs/AMN2_PHASE_11_FINAL_CLOSEOUT_PACKET.ru.md','docs/superpowers/plans/2026-07-18-phase11-final-closeout-controlled-private-release.ru.md'):
    texts.append(Path(p).read_text(encoding='utf-8'))
research=Path('research/amn2/phase-11-final-closeout-controlled-private-release-2026-07-18.md').read_text(encoding='utf-8')
texts.append(research.split('## Sanitized command/result ledger',1)[0])
patterns=('APPROVE PHASE','AUTHORIZE ','SEND_LITERAL','RUN_BOUNDED_ROLLOUT','REVIEW_PHASE11_0B858C5','START_PHASE11_RESTORE_001A')
print(sum(t.count(p) for t in texts for p in patterns))
'@
$source | python -
```

Result: `current_replayable_live_authority=0`.

### Security-diff verification

```powershell
python C:\Users\SooL\.codex\plugins\cache\openai-curated-remote\codex-security\0.1.11\scripts\finalize_scan_contract.py --scan-dir C:\Users\SooL\AppData\Local\Temp\codex-security-scans\VPS-OPS-LAB\24dde6e9d49c565a4beebe47ac91fddb79b990e9_20260718T050216Z --source-root C:\Users\SooL\Documents\VPS-OPS-LAB
```

```text
scan_id=24dde6e9d49c565a4beebe47ac91fddb79b990e9_20260718T050216Z
deep_review=8_of_8
coverage=complete
deferred=0
reportable_findings=0_after_byte_binding_remediation_and_full_recheck
```

### Automation semantic readback

```powershell
$autoFiles=@(
'C:\Users\SooL\.codex\automations\amn2-upstream-orchestrator\automation.toml',
'C:\Users\SooL\.codex\automations\amnezia-weekly-upstream-refresh\automation.toml',
'C:\Users\SooL\.codex\automations\prvtpro-weekly-upstream-refresh\automation.toml',
'C:\Users\SooL\.codex\automations\weekly-kyoresuas-upstream-refresh\automation.toml'
)
Select-String -LiteralPath $autoFiles -Pattern '^(id|kind|name|status|rrule|target_thread_id) = '
```

```text
amn2-upstream-orchestrator=ACTIVE|target_019f60c5-514d-76d3-b162-fc47d800e788|weekly_sunday_10_00
amnezia-weekly-upstream-refresh=PAUSED
prvtpro-weekly-upstream-refresh=PAUSED
weekly-kyoresuas-upstream-refresh=PAUSED
result=pass|original_orchestrator_restored|legacy_chain_paused
```

## Required final verification

```text
phase9_progress_harness_tests=20_passed
root_full_tests=128_passed
branch_integrity=pass|branch_codex-spark-phase9-docs-sync|base_24dde6e9d49c565a4beebe47ac91fddb79b990e9|intended_paths_8
diff_check=pass
baseline_in_diff=false
secret_scan_high_confidence=0
current_replayable_live_authority=0
security_diff=complete|reportable_findings_0
security_scan_id=24dde6e9d49c565a4beebe47ac91fddb79b990e9_20260718T050216Z
security_byte_binding=sealed_manifest_snapshot_equals_index_digest_equals_commit_tree_digest
closeout_commit=this_commit
origin_readback=local_closeout_sha_must_equal_origin/codex-spark-phase9-docs-sync_before_declaration
```

Если один из этих receipts, включая `branch_integrity=pass`, не
подтверждается, declaration withheld и packet остаётся недействующим. Любое
изменение intended path после scan или любой повторный `git add` аннулирует
byte-binding receipt и требует полного rescan/rebind до commit.

## Decision

После exact origin readback финальный operator result может объявить:

```text
AMN2_PHASE11_CONTROLLED_PRIVATE_RELEASE=DECLARED
```

Release остаётся private/operator-only; AWG untouched.
