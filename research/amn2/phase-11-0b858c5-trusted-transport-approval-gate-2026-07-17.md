# Phase 11 `0b858c5` trusted transport approval gate

Date: 2026-07-17.

Decision: `READY-AWAITING-EXACT-APPROVAL`.

The trusted transport hardening is committed locally and the new approval
phrase is prepared but not consumed. This document authorizes no VPS, SSH,
upload, apply, rollback, Telegram, bot, database, provider or AWG action.

## Bound local inputs

```text
remote_executor_sha256=A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72
ssh_runner_sha256=654154AFF81425DE610817C9FF05FB2D976B2EA3A7843C9FC8F566269C94A6BE
trusted_transport=%WINDIR%/System32/OpenSSH|ssh_absolute|scp_absolute|helper_fail_closed
focused_tests=9_passed
canonical_tests=95_passed
postfix_security_rescan=bare_calls_0|trusted_calls_3|pass
origin_sync=previous_hardening_commit_pushed|approval_gate_local_followup
```

## Exact approval phrase

The only accepted phrase for a later bounded live gate is the following
literal string:

```text
APPROVE PHASE11_0B858C5_REMOTE_ORCHESTRATOR_SHA_A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72_TRUSTED_OPENSSH_ABSOLUTE_PATH_BOUND_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_TELEGRAM_PROFILE_UNCHANGED_AND_AWG_UNTOUCHED
```

Quoted, prefixed, suffixed, abbreviated or substring variants must fail
closed. The phrase does not authorize persistent Telegram-002B activation,
profile media mutation, schema writes, provider actions or any AWG service,
peer or configuration change.

## Stop line

Remain at `READY-AWAITING-EXACT-APPROVAL` until a separate operator message is
received. Do not run the runner merely to test the phrase; no live target is
contacted by this gate preparation.
