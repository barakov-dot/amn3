# AMN2 helper SSH transport hardening (Phase 9)

Date: 2026-06-27.
Model: `Codex-Spark`.
Type: docs-only evidence summary.

## Input evidence

- `docs/AMN2_HELPER_STYLE_HARDENING.ru.md`
- `docs/AMN2_HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_HARDENING.ru.md`
- `docs/AMN2_HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_IMPLEMENTATION_REVIEW.ru.md`
- `docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md`

## Result

`AMN2_HELPER_SSH_TRANSPORT_HARDENING` prepared and completed as docs-only.

```text
ssh_transport_hardening=completed
live_steps_opened=false
key_findings=single-session_preference + short-ssh + no-remote-temp-helper + lf-normalization
status=passed-docs-only
next_gate_ready=true
```

## Guidance extracted

1. single-session SSH preferred for multi-check live gates, where operationally possible.
2. remote side scripts must be LF-normalized before `ssh ... bash -s`.
3. no SCP, no temp remote helper files, no remote temp artifacts.
4. raw process lists and raw logs prohibited in helper logs.
5. if exit wrapper masks successful remote status, do controlled cleanup path.

## Stop-lines (restated)

No-live-action from this hardening package:

```text
public_exposure=false
config_delivery=false
peer_creation=false
package_apply=false
service_restart_outside_named_gate=false
firewall_sshd_auth_keys_users_change=false
restore_import_reboot=false
provider_rebuild=false
telegram_profile_media_mutation=false
secret_payload_output=false
```

## Suggested placement in next hardening chain

After this hardening, use:

- `HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_HARDENING` already prepared;
- `TELEGRAM_OPERATION_RUNBOOK_POLISH` as companion playbook update;
- `AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH` to keep scope aligned.
