# AMN2 Phase 7 Final RC Freeze Status For c958733

Date: 2026-06-20.

Status: `completed-rc-ready-paused-state-c958733-no-live-action`.

Scope:

- Final Phase 7 RC freeze/status pass for AMN2 `c958733`.
- Docs/status/evidence consolidation only.
- No live VPS command, SSH command, package upload/apply, service restart,
  public exposure, config delivery, write execution, restore/import/reboot,
  provider mutation, Local Agent mutation, Telegram action or secret-bearing
  output.

## Frozen RC Truth

```text
phase=Phase 7 Release Candidate Readiness / Clean Installer RC
rc_state=rc_ready_paused_private_operator_lane
amn2_head=c958733 Harden security-sensitive operations
amn2_full_commit=c9587332d425583ed627899d7fa950756b64c4dc
amn2_branch=codex-vps-test-prep
vps=89.185.80.166
latest_vps_smoked_package_head=c958733 Harden security-sensitive operations
current_vps_source_overlay=c9587332d425583ed627899d7fa950756b64c4dc
web_runtime=loopback_only_127_0_0_1_3030
public_exposure=not_opened
public_api_exposure=not_opened
vps_apply_enabled=false
production_mutation=not_opened
user_channel_policy=telegram_first
operator_web_policy=vps_ip_loopback_ssh_tunnel_private_access
telegram_identity_profile_media=deferred_not_required_for_private_rc
```

## Evidence Anchors

- Current live/package smoke:
  `research/amn2/phase-7-c958733-package-apply-smoke-2026-06-20.md`.
- Codex Security post-fix validation:
  `research/amn2/phase-7-codex-security-postfix-c958733-2026-06-20.md`.
- Current-state backup/create+verify mode evidence:
  `research/amn2/phase-7-c958733-package-apply-smoke-2026-06-20.md`
  (`backup_artifact_mode=600`).
- Prior direct clean installer execution:
  `research/amn2/phase-7-direct-clean-installer-5501295-2026-06-20.md`.
- Prior post-direct-clean loopback login + backup:
  `research/amn2/phase-7-post-direct-clean-login-backup-5501295-2026-06-20.md`.
- Known-device operator-local config handoffs:
  `research/amn2/phase-7-config-delivery-private-handoff-device1-b121865-2026-06-19.md`
  and
  `research/amn2/phase-7-config-delivery-private-handoff-device2-b121865-2026-06-19.md`.
- Telegram-first/operator-web policy:
  `research/amn2/phase-7-telegram-first-operator-web-policy-2026-06-20.md`.
- Telegram token/user-flow smoke:
  `research/amn2/phase-7-telegram-token-reconciliation-user-flow-smoke-5501295-2026-06-20.md`
  and the follow-up `P7-C009` `getMe`/dispatcher smoke in the current package
  smoke evidence.
- Public exposure/IP-only decision:
  `research/amn2/phase-7-ip-only-exposure-policy-decision-2026-06-18.md`
  and
  `research/amn2/phase-7-ip-only-public-exposure-risk-guard-b121865-2026-06-19.md`.
- Telegram private RC decision:
  `research/amn2/phase-7-telegram-defer-private-rc-2026-06-20.md`.

## Freeze Verdict

```text
rc_freeze_status=ready_paused_c958733
local_only_queue=closed
known_good_vps_smoked_head=c958733
security_postfix_validation=passed_no_open_findings
package_apply_smoke=passed_for_c958733
loopback_api_smoke=passed
telegram_getme_dispatcher_smoke=passed_no_polling_no_send
backup_create_verify=passed_artifact_mode_600
scoped_write_contour=passed_audit_only_blocked_by_vps_apply_disabled
known_device_config_delivery=completed_operator_local_private_file_for_device_1_and_2
public_exposure=blocked_not_exposed_operator_ip_ssh_tunnel_default
telegram_c007=deferred_not_required_for_private_rc
watch_only_client_signals=amnezia_client_4_8_19_0_amneziawg_android_2_0_1
secret_values_printed=false
```

## Release Posture

AMN2 is now in a private/operator RC-ready paused state on the `c958733` head:

- GitHub AMN2 branch `codex-vps-test-prep` is pushed at `c958733`.
- AMN3 evidence/status repo records the `c958733` package artifacts and VPS
  smoke evidence.
- Disposable VPS `89.185.80.166` is loopback-only for web/admin.
- User-facing channel is Telegram-first.
- Operator web/admin remains private by VPS IP plus loopback/SSH tunnel or
  equivalent private access.
- Public launch, public web/admin exposure, public API exposure and production
  mutation are not opened.

## Remaining Stop-Lines

The RC is paused, not publicly launched. The following still require separate
exact named gates:

- Residual `P7-C006` restore/import/download/reboot/DR/provider-restore scopes.
- Any actual installer runner execution beyond the audit-only
  `install:write` contour.
- Any public exposure, reverse proxy, TLS, firewall or listener change.
- Any new config delivery target, resend, revocation drill, SMTP/Telegram
  delivery or public/self-service config link.
- Any Local Agent mutation or production peer/user mutation.
- Any Telegram polling, live bot send, profile/media mutation or credential
  handoff.
- Any provider restore, provider rebuild, destructive migration or backup
  archive download.

## Next Recommendation

Default next action: keep the project in
`rc_ready_paused_private_operator_lane` and continue only watch-only intake
unless the operator opens a specific exact named gate.

Most likely useful follow-up before a real public/prod launch: provider
restore-point confirmation or a separate disaster-recovery restore/import drill,
but only after a fresh provider restore-point proof and a separate
restore/import/reboot approval.
