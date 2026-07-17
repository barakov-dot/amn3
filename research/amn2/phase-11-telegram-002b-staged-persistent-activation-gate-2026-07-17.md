# Phase 11 TELEGRAM-002B staged persistent activation gate — local closeout

Дата: 2026-07-17.

Статус: `READY-AWAITING-SEPARATE-EXACT-LIVE-APPROVAL`.

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
