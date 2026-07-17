# Phase 11 TELEGRAM-002B staged persistent activation gate — local closeout

Дата: 2026-07-17.

Статус: LOCAL-FIX-VERIFIED-AWAITING-COMMIT-PUSH-ORIGIN-SYNC.

## Scope and authority

Получено и исполнено только локальное approval:
`APPROVE_PHASE11_TELEGRAM_002B_STAGED_PERSISTENT_ACTIVATION_DESIGN`.

Это не live authority. В этом slice не выполнялись SSH/VPS contact, Telegram
API, `systemctl`, database write/restore, provider mutation, regular-bot
activation или AWG action. Production Telegram profile не изменялся.

## Implemented files

- `docs/superpowers/specs/2026-07-17-phase11-telegram-002b-staged-persistent-activation-design.ru.md`
  — Russian/English design and safety boundary;
- `docs/superpowers/plans/2026-07-17-phase11-telegram-002b-staged-persistent-activation.ru.md`
  — TDD implementation plan and hardening receipts;
- `scripts/vps/phase11_telegram_002b_persistent_remote.sh` — fail-closed
  `preflight`, `stage`, `accept`, `postflight` executor;
- `scripts/vps/phase11_telegram_002b_persistent_ssh_runner.ps1` — exact local
  approval, absolute trusted OpenSSH and same-byte transport;
- `tests/test_phase11_telegram_002b_activation_executor.py` — 18 static
  contract tests.

## Bound identities

```text
source_overlay=0b858c5
source_full_commit=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
remote_executor_sha256=14747241F1A0E0545CF8B96329E90708F7CC80AF639872968DA03A1783200C64
ssh_runner_sha256=4038FD648F6834AF03A1D44BCD1E0CA63B78FC41CCB48A24D9245B1166FA53B7
expected_bot=@NeobyatnayaAMNZ_bot
rollback_ttl_seconds=240
```

Hardening includes rollback arm before mutation, `ERR/HUP/INT/TERM` signal
traps, strict inactive/dead timer cancellation, compensation rollback through
accept, canonical UTF-8 Base64 confirmation transport, isolated OpenSSH trust
sources (`-F none`, `GlobalKnownHostsFile=none`, `KnownHostsCommand=none`) and
an exclusive local stage-consumed approval receipt.

## Verification evidence

```text
red_expected_failures=6
focused_green=18_passed
full_canonical=113_passed
bash_n=pass
powershell_parse=pass
whitespace_scan=pass
secret_scan=0_high_confidence_secret_matches
security_reportable_findings=0
security_coverage=complete
security_scan_dir=C:\Users\SooL\AppData\Local\Temp\codex-security-scans\VPS-OPS-LAB\phase11-telegram-002b-final-20260717T101500Z
```

Fresh static Security diff review covered all five scoped files. Earlier
pre-fix lifecycle/trust/transport candidates were rechecked and closed after
the hardening patch; the canonical final report has zero reportable findings.
The unrelated `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` remained untouched
and untracked.

## Future live sequence (not consumed)

Only after a separate exact approval may an operator run the bounded sequence:

```text
preflight -> stage (active/disabled, 240s rollback) -> one configured-admin /start -> exact wide-header confirmation -> accept (enable) -> postflight
```

The prepared phrase is literal, single-use at the local runner, and currently
unconsumed:

```text
APPROVE PHASE11_TELEGRAM_002B_REMOTE_ORCHESTRATOR_SHA_14747241F1A0E0545CF8B96329E90708F7CC80AF639872968DA03A1783200C64_0B858C5_EXACT_UNIT_ENV_TELEGRAM_PREFLIGHT_DISABLED_FIRST_STAGE_FIRST_CONFIGURED_ADMIN_SINGLE_START_WIDE_HEADER_EXACT_CONFIRM_ACCEPT_ENABLE_POSTFLIGHT_AUTOROLLBACK240_NO_BLIND_DB_RESTORE_WEB_UNTOUCHED_AND_AWG_UNTOUCHED
```

Until that phrase is separately issued, `regular_bot=inactive_disabled`,
`telegram_profile=unchanged`, `database_live_write=false`,
`provider_mutation=false`, and `awg=untouched` remain the enforced boundary.

## Preflight correction 2026-07-17

The first approved preflight reached the VPS but stopped fail-closed because
`/opt/amn2/venv/bin/python` is a normal virtual-environment symlink. The source,
unit, settings, `.env` and overlay marker bindings were present; no mutation,
stage, bot start or AWG action occurred. The executor was corrected to resolve
the interpreter with `readlink -f` and require a regular executable final
target, while retaining strict non-symlink checks for source/unit/env inputs.

```text
preflight_attempt=fail_closed|missing_venv_symlink_target_check_only
stage=false|accept=false|postflight=false
awg=untouched
new_remote_executor_sha256=3E6D42D6D7184BD7A05402585A85652C2319D1E0E9E8076217057AE5EE948881
focused_tests=19_passed
full_canonical_tests=114_passed
syntax=bash_n_pass|powershell_parse_pass
security_diff=0_new_reportable_findings
new_approval=required|old_sha_phrase_not_valid_for_changed_bytes
```

New exact phrase, not yet issued or consumed:

```text
APPROVE PHASE11_TELEGRAM_002B_REMOTE_ORCHESTRATOR_SHA_3E6D42D6D7184BD7A05402585A85652C2319D1E0E9E8076217057AE5EE948881_0B858C5_EXACT_UNIT_ENV_TELEGRAM_PREFLIGHT_DISABLED_FIRST_STAGE_FIRST_CONFIGURED_ADMIN_SINGLE_START_WIDE_HEADER_EXACT_CONFIRM_ACCEPT_ENABLE_POSTFLIGHT_AUTOROLLBACK240_NO_BLIND_DB_RESTORE_WEB_UNTOUCHED_AND_AWG_UNTOUCHED
```

## Disabled-first stage journal-ingest correction 2026-07-17

The corrected preflight passed on production. The separately approved
disabled-first stage then stopped fail-closed before operator interaction
because its single immediate journal read did not yet contain the sanitized
admission receipt. The operator did not send `/start`; accept, enable and
postflight were not entered.

A narrow read-only diagnostic proved that the required markers arrived after
the check: admission `1`, pending `1`, allowed-updates `1`, error `0`. The
rollback receipt for run `20260717T115918Z` was present, the independent
post-failure preflight passed, and the exact stale rollback timer was stopped
after verifying bot inactive/disabled and rollback service inactive. Web, DB,
Telegram backlog and AWG evidence remained unchanged.

The executor now polls only the sanitized admission receipt for at most 15
seconds and stops/resets only the current run-id-derived transient timer after
an immediate successful rollback. It does not expose raw logs and does not add
web, database, Telegram-profile or AWG mutation authority.

```text
corrected_preflight=pass
stage_run=20260717T115918Z|fail_closed_before_operator_start
operator_start=false|accept=false|enable=false|postflight=false
journal_markers=admission_1|pending_1|allowed_updates_1|errors_0
rollback_receipt=present
postfailure_preflight=pass
stale_timer=stopped_after_inactive_disabled_verification
regular_bot=inactive_disabled|process_0
awg=running|restart_0|peers_12|unchanged
new_remote_executor_sha256=FA3F979E3D2DEEB0EF2F53E97A79ECECCADCA6F853C8587A9973D192C49CEB3F
new_ssh_runner_sha256=F478A883ADE570D7A594F04B91062E1A1275467AFFE3D71877BE441D87FDA137
signal_fix=rollback_then_nonzero_exit|no_stage_or_accept_resume
signal_poc=term_exit_143|no_privileged_mutation_or_stage_pass
focused_tests=21_passed
full_canonical_tests=116_passed
syntax=bash_n_pass|powershell_parse_pass
security_diff=complete_9_of_9|former_candidates_closed|reportable_findings_0
security_scan_dir=C:\Users\SooL\AppData\Local\Temp\codex-security-scans\VPS-OPS-LAB\135955aa9fdf078708d02bf5848c030fac350db4_20260717T131800Z
new_approval=required|all_earlier_sha_phrases_invalidated
approval_phrase=WITHHELD_UNTIL_ORIGIN_SYNC
```

The exact live phrase is intentionally withheld until post-fix tests,
zero-reportable security rescan, commit, push and trusted-origin readback
succeed:

```text
approval_phrase=WITHHELD_UNTIL_TEST_SECURITY_COMMIT_PUSH_AND_ORIGIN_SYNC
```

## Stale first-admin `/start` exact-one cleanup gate

The final `2FDB...` classified preflight passed source, write-gate, web,
bot-disabled, database and AWG checks, then stopped fail-closed with
`pending_updates_nonzero`. Stage was not called, so its exclusive local receipt
was not created and the existing activation authority remains unconsumed.

A separate design and written-spec gate authorized only local engineering of a
one-update cleanup. The executor performs two identical non-advancing reads,
requires exactly one private text `/start` from the first configured admin,
advances the offset exactly once and preserves any concurrent higher update.
It sends no response and imports no workflow/handler/dispatcher path.

An exact local aiogram probe proved that `Message.content_type` is
`ContentType.TEXT`, compares equal to `"text"`, but stringifies as
`"ContentType.TEXT"`. TDD caught and corrected the initial stringification
check before live use, then rebound the runner to the changed remote bytes.

```text
classified_preflight=failed_closed|pending_updates_nonzero
activation_stage=false|receipt_absent|2fdb_authority_unconsumed
cleanup_design=d474ff6|approved
cleanup_plan=940d07c
cleanup_remote_executor_sha256=41F69F945F74647B441173B682277E0568DA81CC7F0B12EADD9BD534DB225242
cleanup_ssh_runner_sha256=D3BD76119B35155AAB922E54C2E59F50B7D9D0B23C9B5AC2268887D8ADB70A1F
cleanup_tdd=initial_red_9_failed_1_passed|remote_green_8_passed_2_deselected|aiogram_red_1_failed_9_passed|final_green_10_passed
cleanup_tests=focused_10_passed|canonical_128_passed
cleanup_syntax=bash_n_pass|powershell_parse_pass|diff_check_pass
cleanup_static_scans=forbidden_operations_0|high_confidence_secret_matches_0
cleanup_security_scan=59e7862ce73ab46179a01591f4533c8496f3b38d_20260717T183406Z
cleanup_security_snapshot=48bc1e5a1e775a2b97c75c30c83938d4fc79f07da281b328df0640c532db7564
cleanup_security=worklist_5_of_5|coverage_complete|reportable_findings_0
cleanup_live=not_run|new_exact_approval_required
cleanup_approval=prepared_in_runner|withheld_until_commit_push_origin_readback
```

Next: review final diff, commit/push/read back trusted origin, then issue the
literal SHA-bound cleanup approval from the runner. Do not send a new `/start`
until cleanup/postflight pass and a fresh activation stage explicitly returns
`awaiting_admin_start=true`. Production AWG remains untouched.

## Exact single-line receipt correction after FA3F live attempt

The literal FA3F approval was issued. Fresh production preflight passed:
overlay/source, false/false write gates, private web, SQLite integrity/FK,
Telegram identity/webhook/backlog and read-only AWG snapshot all matched the
known safe baseline. The single-use disabled-first stage then stopped
fail-closed before operator interaction with
`sanitized admission receipt missing`. The operator did not send `/start`;
accept, enable and postflight were not entered.

An independent post-failure preflight proved compensation rollback:
regular bot inactive/disabled/process 0; web active/enabled/loopback healthy;
database integrity ok, FK 0, tables 15, rows 88 and the same counts hash;
Telegram backlog 0; AWG running, restart 0, peers 12 and the same
container/peer-set hashes.

Root-cause tracing against the exact `0b858c5` source proved this was not
journald latency. `PersistentBotAdmissionResult.render()` emits one canonical
line containing admission, identity, webhook, backlog and allowed-update
fields. The verifier filtered that line but then required backlog and
allowed-update fields at the beginning of separate lines, so all 15 retries
were structurally unable to succeed.

The TDD correction now accepts exactly one complete fixed-string receipt line
with the expected public bot identity and exact state. Zero, duplicate,
partial, prefixed or suffixed lines fail; rollback/enable ordering and all
prohibited mutation boundaries remain unchanged.

```text
fa3f_preflight=pass
fa3f_stage=fail_closed_before_operator_start|sanitized_receipt_shape_mismatch
operator_start=false|accept=false|enable=false|postflight=false
postfailure_preflight=pass
regular_bot=inactive_disabled|process_0
web=active_enabled_http_ok_loopback_only
database=integrity_ok|fk_0|tables_15|rows_88|counts_hash_unchanged
telegram=identity_match|webhook_empty|backlog_0
awg=running|restart_0|peers_12|container_and_peer_set_hashes_unchanged
root_cause=producer_single_line|verifier_split_line_anchors
new_remote_executor_sha256=56BE81549B86B5DBF09AA23A8513E652F6AF344E88C131FC8EAA2D5D5403F2CE
new_ssh_runner_sha256=04DF10C9305CFA46843981A851A07B98B658A92859135A8180BCE15363F39951
tests=focused_21_passed|canonical_116_passed
syntax=bash_n_pass|powershell_parse_pass|diff_check_pass
security_diff=complete_3_of_3|reportable_findings_0
security_report=C:\Users\SooL\AppData\Local\Temp\codex-security-scans\VPS-OPS-LAB\73207d114977189974b5aacea532c5c8466f64ce_20260717T141444Z\report.md
fa3f_stage_authority=consumed_and_invalidated_by_changed_bytes
new_approval=required
approval_phrase=WITHHELD_UNTIL_TEST_SECURITY_COMMIT_PUSH_AND_ORIGIN_SYNC
```

## Unbuffered persistent receipt correction after 56BE live attempt

The exact 56BE-bound approval was received. Fresh production preflight
passed. The single-use disabled-first stage again stopped fail-closed before
operator interaction with `sanitized admission receipt missing`; `/start`,
accept, enable and postflight did not occur. An independent post-failure
preflight proved compensation rollback and the unchanged web, database,
Telegram and AWG baseline.

Evidence from the exact `0b858c5` source archive identified a second distinct
cause. `app.main` calls the default `print` receipt writer, while the systemd
unit starts Python without `-u` or `PYTHONUNBUFFERED`. Because polling remains
long-lived, the correct canonical receipt stays in the process stdout buffer
instead of reaching journald within the gate deadline.

The narrow TDD correction adds `PYTHONUNBUFFERED=1` to both the atomic env
updater and exact env validator. The existing stage snapshots the entire env
file and its metadata before mutation, and every fail-closed path restores
that snapshot. No source-overlay, Telegram-profile, web, database, provider or
AWG authority was added.

```text
sha56be_preflight=pass
sha56be_stage=fail_closed_before_operator_start|stdout_buffered
operator_start=false|accept=false|enable=false|postflight=false
postfailure_preflight=pass
regular_bot=inactive_disabled|process_0
web=active_enabled_http_ok_loopback_only
database=integrity_ok|fk_0|tables_15|rows_88|counts_hash_unchanged
telegram=identity_match|webhook_empty|backlog_0
awg=running|restart_0|peers_12|container_and_peer_set_hashes_unchanged
root_cause=default_print|no_python_unbuffered_mode|persistent_stdout_buffer
correction=PYTHONUNBUFFERED_1|atomic_env_update|exact_env_validation|rollback_protected
new_remote_executor_sha256=E407421F358703C4D6FE1825EE46EFBC4E72C3840FEBAC89F131800F30DB412F
new_ssh_runner_sha256=20944C777A5EAB534964577C8BD3F9B71C9ADAE8310E3C93F56EB70BE0EE86B5
tdd=red_1_failed_21_passed|green_22_passed
tests=focused_22_passed|canonical_117_passed
syntax=bash_n_pass|powershell_parse_pass|diff_check_pass
security_diff=complete_3_of_3|reportable_findings_0|secret_patterns_0
sha56be_stage_authority=consumed_and_invalidated_by_changed_bytes
new_approval=required
approval_phrase=WITHHELD_UNTIL_TEST_SECURITY_COMMIT_PUSH_AND_ORIGIN_SYNC
```

## Exact default-plan timestamp gate after E407 live attempt

The E407-bound approval was received. Fresh production preflight passed and
the corrected unbuffered admission receipt reached journald and passed its
exact single-line gate. The stage then stopped fail-closed before operator
interaction because the application row digest changed. `/start`, accept,
enable and postflight did not occur. Independent post-failure preflight proved
the bot inactive/disabled, unchanged counts, zero Telegram backlog and the
unchanged AWG baseline.

Exact `0b858c5` source tracing identified the deterministic write:
`create_workflow()` calls `seed_default_plans()`, whose conflict path executes
`upsert_plan()` and sets `plans.updated_at=CURRENT_TIMESTAMP` even when every
business field already matches. This metadata-only timestamp update has
already occurred; the no-blind-DB-restore contract was preserved.

The narrow TDD correction computes a canonical hash of every application row
after removing only `plans.updated_at`. Startup must preserve that hash, exact
table counts and the complete first-admin row. The resulting post-start state
is then sealed as a separate baseline, so acceptance still permits only the
reviewed mutable fields of the first configured administrator.

```text
e407_preflight=pass
e407_admission_receipt=pass|unbuffered_fix_effective
e407_stage=fail_closed_before_operator_start|default_plan_updated_at
operator_start=false|accept=false|enable=false|postflight=false
postfailure_preflight=pass
regular_bot=inactive_disabled|process_0
database=integrity_ok|fk_0|tables_15|rows_88|plan_timestamp_metadata_only
telegram=identity_match|webhook_empty|backlog_0
awg=running|restart_0|peers_12|container_and_peer_set_hashes_unchanged
startup_delta_gate=plans_updated_at_only_or_unchanged|counts_exact|first_admin_exact|staged_baseline_sealed
new_remote_executor_sha256=DF9E0BAD6359AD7F3100A7FBED5ED1223721C656086D0CADA72CA492BD10B396
new_ssh_runner_sha256=16E6F846DEB3DC52838224E277D65AA2D0059D6288C827248607A7F6E5943CED
tdd=red_1_failed_22_passed|green_23_passed
tests=focused_23_passed|canonical_118_passed
syntax=bash_n_pass|powershell_parse_pass|diff_check_pass
security_diff=complete_3_of_3|reportable_findings_0|secret_patterns_0
e407_stage_authority=consumed_and_invalidated_by_changed_bytes
new_approval=required
approval_phrase=WITHHELD_UNTIL_TEST_SECURITY_COMMIT_PUSH_AND_ORIGIN_SYNC
```
