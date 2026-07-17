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
