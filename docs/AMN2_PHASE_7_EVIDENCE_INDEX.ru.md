# AMN2 Phase 7 Evidence Index

Дата: 2026-06-20.

Статус: local-only evidence index.

Этот индекс не открывает live VPS, SSH, public exposure, config delivery, write
API, Local Agent mutation, backup/import/reboot, destructive execution или
Telegram identity/profile/media mutation.

## Phase 8 Addendum

- `phase-8-rc-wait-exact-named-gate-2026-06-22.md` - docs-only explicit wait
  state evidence. Wait document:
  `docs/AMN2_PRIVATE_OPERATOR_RC_WAIT_EXACT_GATE.ru.md`. It records the
  Russian operator command `ОЖИДАНИЕ_ТОЧНОГО_ИМЕНОВАННОГО_GATE`, keeps AMN2 at
  private/operator RC `launch-ready-with-explicit-limitations`, and requires a
  fresh explicit named gate for any live/config/Telegram/public/destructive
  action. No live/destructive/config/Telegram/public action or secret-bearing
  output was performed.
- `phase-8-rc-ready-hold-2026-06-22.md` - docs-only ready hold evidence.
  Hold document: `docs/AMN2_PRIVATE_OPERATOR_RC_READY_HOLD.ru.md`. It holds
  AMN2 at private/operator RC `launch-ready-with-explicit-limitations`, with
  public launch not approved and no remaining blockers inside listed
  limitations. No live/destructive/config/Telegram/public action or
  secret-bearing output was performed.
- `phase-8-rc-closeout-2026-06-22.md` - docs-only private/operator RC
  closeout evidence. Closeout:
  `docs/AMN2_PRIVATE_OPERATOR_RC_CLOSEOUT.ru.md`. It records final
  private/operator RC status, pushed heads at closeout start, package index,
  next-chat starting point, explicit limitations and
  `remaining_blockers_inside_listed_limitations=none`. No live/destructive/
  config/Telegram/public action or secret-bearing output was performed.
- `phase-8-rc-final-package-2026-06-22.md` - docs-only final private/operator
  RC package evidence. Package index:
  `docs/AMN2_PRIVATE_OPERATOR_RC_FINAL_PACKAGE.ru.md`. It points to the handoff
  document, run checklist, evidence chain, limitations and future exact gates.
  No live/destructive/config/Telegram/public action or secret-bearing output
  was performed.
- `phase-8-rc-operator-run-checklist-2026-06-22.md` - docs-only
  private/operator RC run checklist evidence. Checklist:
  `docs/AMN2_PRIVATE_OPERATOR_RC_RUN_CHECKLIST.ru.md`. It records what to check
  before operating, how to keep public exposure closed, where private handoff
  artifacts live, Telegram/config delivery/backup boundaries and future exact
  gates for broader action. No live/destructive/config/Telegram/public action
  or secret-bearing output was performed.
- `phase-8-rc-handoff-2026-06-22.md` - docs-only private/operator RC handoff
  evidence. Operator-facing handoff:
  `docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md`. It carries forward
  `launch-ready-with-explicit-limitations`, records allowed private/operator RC
  scope, exact limitations, stop-lines and future exact gates for public
  exposure, Telegram live delivery, config delivery, restore/import DR and
  production rollout. No live/destructive/config/Telegram/public action or
  secret-bearing output was performed.
- `phase-8-sfinal-launch-readiness-freeze-2026-06-22.md` - `P8-SFINAL`
  launch readiness freeze using existing evidence only; final Phase 8 status is
  `launch-ready-with-explicit-limitations` for private/operator RC,
  `public_launch_status=not-approved`, and
  `blocked_with_exact_remaining_blockers=false`. The freeze records the exact
  limitations: `P8-C003` used an Android projector while Android phone
  acceptance remains separate `P8-C001` evidence; public exposure stays closed;
  Telegram live send/profile/media mutation and bot polling were not performed;
  `.conf` is release-primary while QR/full `vpn://` are not; iOS DefaultVPN
  remains experimental/unreliable; backup create+verify passed but
  restore/import is not proven. No live/destructive/config/Telegram/public
  action or secret-bearing output was performed in the freeze.
- `phase-8-p8-c003-fresh-zero-rehearsal-2026-06-22.md` - `P8-C003`
  fresh-from-zero VPS rehearsal for AMN2 `187949b` on disposable VPS
  `89.185.80.166`; destructive clean install of `/opt/amn2`, source overlay
  match, fresh env/DB init, two-admin bot config verification, loopback web/API
  smoke, Telegram `getMe` plus non-polling bot surface smoke, one fresh Android
  projector private `.conf` handoff, backup create+verify and closed public
  probes all passed. Fresh projector peer `d0ab128d6801` showed endpoint
  `yes`, fresh handshake and positive traffic deltas
  `rx_delta=622084/tx_delta=9004751`. No public exposure, Telegram live send,
  bot polling, restore/import/reboot, provider mutation, QR/`vpn://`, key/PSK,
  token/password or config payload output was performed. Phase 8 launch gate is
  now `fresh-from-zero-rehearsal-passed-awaiting-final-freeze`; next exact gate
  is `P8-SFINAL launch readiness freeze`.

## Current Truth

```text
AMN2 head: 471bca8 Downgrade DefaultVPN iOS compatibility
AMN2 security-fix head: c958733 Harden security-sensitive operations
latest VPS-smoked/package head: 6d5cf3e Make Telegram config delivery conf-first
Phase 8 AMN2 current-fixes head: 187949b Persist Android-compatible AWG defaults
Phase 8 latest VPS-applied/package-smoked head: 187949b Persist Android-compatible AWG defaults
Phase 8 final status: launch-ready-with-explicit-limitations
Phase 8 launch gate status: closed-for-private-operator-rc-with-limitations
Phase 8 operator handoff status: completed-private-operator-rc-handoff-docs-only
Phase 8 operator run checklist status: completed-private-operator-rc-run-checklist-docs-only
Phase 8 final package status: completed-private-operator-rc-final-package-docs-only
Phase 8 closeout status: completed-private-operator-rc-closeout-docs-only
Phase 8 ready hold status: active-private-operator-rc-ready-hold-docs-only
Phase 8 wait exact gate status: active-wait-exact-named-gate-docs-only
Phase 8 recommended next state: ожидать-явный-именованный-gate
workspace/evidence repo: barakov-dot/amn3 master latest pushed head; verify with git log -1
AMN2 package/source repo: barakov-dot/amn2 codex-vps-test-prep 471bca8
latest Codex Security post-fix scan: completed on c958733 with 0 reportable findings
next VPS package/apply target: completed by P7-C009
public/config/write status: blocked-by-preconditions
public exposure status: deferred-not-required-for-private-rc-not-exposed
user_channel_policy: telegram-first
operator_web_policy: vps-ip-loopback-ssh-tunnel-no-public-web-required
public_url_env_residue_status: reconciled-removed-in-P7-C002e
ip_only_public_exposure_status: blocked-in-P7-C002d-not-exposed
config_write_read_only_preflight_status: completed-blocked-no-delivery-no-write
operator_local_config_delivery_guard_status: blocked-pending-target-and-private-handoff-no-delivery
operator_local_config_target_inventory_status: completed-read-only-target-inventory-no-delivery
operator_local_private_handoff_device1_status: completed-private-file-copied-secret-not-printed
operator_local_private_handoff_device2_status: completed-private-file-copied-secret-not-printed
P7-C003 known-target private handoff status: completed-for-device-1-and-device-2
write_backup_telegram_read_only_preflight_status: completed-read-only-preflight-no-mutation
post_clean_write_backup_telegram_rebaseline_status: completed-post-clean-read-only-rebaseline-no-mutation
p7_c005_write_install_contour_status: completed-scoped-write-contour-smoked
p7_c006_backup_only_status: completed-backup-only-create-verify-no-restore-import-reboot
p7_c006a_provider_restore_point_status: completed-inconclusive-no-restore-point-confirmed
p7_c006_current_state_backup_status: completed-current-state-backup-only-create-verify-no-restore-import-reboot
p7_c007_telegram_status: deferred-not-required-for-private-rc-no-telegram-action
p7_c008_telegram_user_flow_smoke_status: completed-after-token-reconciliation
p7_c008a_telegram_token_reconciliation_status: completed-getme-dispatcher-surface-no-send
p7_c010_mobile_telegram_ux_acceptance_status: planned-pending-live-real-device-acceptance
p7_c010a_mobile_telegram_ux_plan_status: completed-mobile-telegram-ux-acceptance-plan-no-live-action
p7_c010b_mobile_telegram_ux_live_acceptance_status: failed-real-device-ux-copy-qr-and-ios-first-connect
p7_c010b_conf_first_fix_status: package-smoked-mobile-retest-failed-qr-and-ios-defaultvpn
p7_c010c_6d5cf3e_package_apply_smoke_status: completed-package-apply-loopback-telegram-backup-smoke
p7_c010c_mobile_retest_status: failed-qr-and-ios-defaultvpn-functional-connectivity
p7_c010d_client_compatibility_status: completed-defaultvpn-ios-downgraded-no-live-apply
p7_c010f_windows_desktop_path_status: completed-windows-desktop-path-accepted-operator-observation-no-live-action
final_rc_freeze_status: completed-rc-ready-paused-state-c958733-no-live-action
s_final_next_chat_handoff_status: completed-s-final-next-chat-handoff-c958733-no-live-action
p7_c004c_direct_clean_installer_status: completed-direct-clean-install-5501295-loopback-smoke
p7_c004d_c006b_post_direct_clean_login_backup_status: completed-login-verified-backup-create-verify
codex_security_postfix_status: completed-post-fix-security-validation-no-open-findings
p7_c009_c958733_package_apply_smoke_status: completed-c958733-package-apply-loopback-telegram-backup-smoke
p7_c004a_destructive_pre_cutover_status: ready-for-final-destructive-stop-line-no-apply
P7-C004b clean install status: completed-clean-install-loopback-smoke
latest_watch_only_after_critical_preflights: completed-watch-only-intake-after-critical-preflights-no-live-action
latest_watch_only_cycle: completed-watch-only-intake-cycle-complete-no-live-action
approved active work: residual P7-C006 scopes and watch-only intake
P7-C002 default status: deferred-not-required-for-private-rc-not-exposed
latest Telegram user-flow smoke: completed after P7-C008a token reconciliation
latest_watch_only_status: completed-watch-only-status-hygiene-no-live-action
latest_watch_only_intake: completed-watch-only-intake-cycle-complete-no-live-action
local-only expansion status: frozen before named gate
```

## Core Evidence

- `phase-7-windows-desktop-path-acceptance-2026-06-20.md` - `P7-C010f`
  docs-only Windows desktop path acceptance record; operator reports that the
  previously issued Windows config works clearly. This accepts the desktop path
  as operator observation evidence, but does not close mobile acceptance:
  iPhone DefaultVPN remains experimental/unreliable, QR remains non-primary and
  Android AmneziaWG is still pending. No live action or secret-bearing output
  was performed.
- `phase-7-ios-android-client-compatibility-diagnostic-471bca8-2026-06-20.md` -
  `P7-C010d` compatibility diagnostic after mobile UX retest; AMN2
  `471bca8` downgrades DefaultVPN iOS to experimental/unreliable and updates
  install guidance. No live package apply was performed in this step.
- `phase-7-mobile-telegram-ux-failure-conf-first-fix-6d5cf3e-2026-06-20.md` -
  `P7-C010b` real-device Telegram UX failure analysis and AMN2 code fix
  `6d5cf3e`; records that full `vpn://` one-click copy and QR deep-link import
  are not reliable release paths, changes delivery to `.conf`-first and marks
  the next step as package/apply plus real-device retest. No new live package
  apply was performed in this evidence step.
- `phase-7-mobile-telegram-ux-acceptance-plan-c958733-2026-06-20.md` -
  `P7-C010a` local-only mobile Telegram UX acceptance plan for AMN2 `c958733`;
  records the release-blocking real-device checks for one-click copy, QR
  readability on iPhone/Android and fallback `.conf` import before Phase 8. No
  live action or secret-bearing output was performed.
- `phase-7-s-final-next-chat-handoff-c958733-2026-06-20.md` - S-final
  next-chat handoff for AMN2 `c958733`; captures current truth, next-chat
  opening text, exact-gate menu and stop-lines for the
  `rc_ready_paused_private_operator_lane`. No live action or secret-bearing
  output was performed.
- `phase-7-codex-security-postfix-c958733-2026-06-20.md` - Codex Security
  post-fix validation for AMN2 `c958733`; fixed CLI `VPS_APPLY_ENABLED` bypass,
  Telegram delivery fallback config leak, SMTP STARTTLS context, backup
  artifact mode and debug snapshot shell boundary; focused pytest `95 passed`,
  full pytest `729 passed`, and post-fix Codex Security scan completed with `0`
  reportable findings. No live VPS action was performed in that step; the
  follow-up VPS package/apply smoke was later completed by `P7-C009`.
- `phase-7-c958733-package-apply-smoke-2026-06-20.md` - `P7-C009`
  package/apply and smoke gate for AMN2 `c958733` on disposable VPS
  `89.185.80.166`; package/source checksums matched, source overlay applied to
  `c9587332d425583ed627899d7fa950756b64c4dc`, loopback web restart passed,
  loopback API smoke returned `VPS verdict: pass`, Telegram `getMe` and
  non-polling dispatcher/user-flow smoke passed, backup create+verify passed
  with artifact mode `600`, and public probes to `3030`, `3040`, `80` and
  `443` stayed `000`. No public exposure, config delivery payload output, write
  execution, restore/import/reboot/download, provider mutation, Local Agent
  mutation, Telegram polling/live send/profile/media mutation or secret-bearing
  output was performed.
- `phase-7-final-rc-freeze-status-c958733-2026-06-20.md` - final Phase 7 RC
  freeze/status pass for AMN2 `c958733`; status
  `completed-rc-ready-paused-state-c958733-no-live-action`, frozen state
  `rc_ready_paused_private_operator_lane`; no live action or secret-bearing
  output.
- `phase-7-final-rc-freeze-status-5501295-2026-06-20.md` - final Phase 7 RC
  freeze/status pass for AMN2 `5501295`; status
  `completed-rc-ready-paused-state-no-live-action`, frozen state
  `rc_ready_paused_private_operator_lane`; no live action or secret-bearing
  output.
- `phase-7-direct-clean-installer-5501295-2026-06-20.md` - `P7-C004c` direct
  destructive clean installer pass for AMN2 `5501295` on disposable VPS
  `89.185.80.166`; clean install, DB init, loopback web and API smoke passed;
  public probes stayed closed.
- `phase-7-post-direct-clean-login-backup-5501295-2026-06-20.md` -
  `P7-C004d + P7-C006b` post-direct-clean loopback admin login verification
  plus backup-only create/verify for AMN2 `5501295`; login passed, encrypted
  backup artifact stayed on the VPS, public probes stayed closed, and no
  restore/import/reboot/download/public/config/write/Local Agent/Telegram/
  provider mutation was performed.
- `phase-7-telegram-first-operator-web-policy-2026-06-20.md` -
  docs-only policy decision: users are served through the Telegram-first
  channel, web/admin remains operator-only by VPS IP plus loopback/SSH tunnel,
  and public web-admin/domain/TLS/reverse-proxy exposure is not required for
  private/operator RC.
- `phase-7-telegram-user-flow-smoke-token-invalid-5501295-2026-06-20.md` -
  `P7-C008` Telegram user-flow smoke attempt; source/runtime checks passed but
  Telegram `getMe` failed with `TokenValidationError` because the VPS token is
  invalid. Resolved by `P7-C008a`.
- `phase-7-telegram-token-reconciliation-user-flow-smoke-5501295-2026-06-20.md` -
  `P7-C008a` token reconciliation and user-flow smoke; token updated through
  operator-secret handoff with rollback copy, Telegram `getMe` passed, and
  non-polling bot/user-flow surface construction passed. No polling, live send,
  profile/media mutation, config payload output, write execution, public
  exposure, restore/import/reboot, provider mutation or secret-bearing output.
- `phase-7-transition-packet-2026-06-14.md` - Phase 7 entry packet.
- `phase-7-current-head-package-preflight-b121865-2026-06-14.md` - local
  package/preflight for `b121865`.
- `phase-7-live-update-smoke-b121865-2026-06-14.md` - live package/apply/smoke
  pass for `b121865` on disposable VPS `89.185.80.166`.
- `phase-7-public-config-write-preflight-b121865-2026-06-14.md` -
  public/config/write read-only preflight, closed as `blocked-by-preconditions`.
- `phase-7-public-exposure-gate-precutover-b121865-2026-06-14.md` -
  `P7-C002` public exposure pre-cutover, closed as `blocked-by-preconditions`.
- `phase-7-public-exposure-admin-domain-prereq-b121865-2026-06-14.md` -
  `P7-C002a` admin/domain prerequisite update, closed as `prerequisite-updated`.
- `phase-7-public-exposure-runtime-login-verify-b121865-2026-06-18.md` -
  `P7-C002b` runtime reload and loopback login verification, closed as
  `runtime-login-verified-not-exposed`.
- `phase-7-public-cutover-guard-b121865-2026-06-18.md` - `P7-C002`
  public cutover guard, closed as `blocked-by-domain-tls-plan-not-exposed`.
- `phase-7-dns-domain-tls-prereq-watch-intake-2026-06-18.md` -
  `P7-C002c` input-required staging plus watch-only intake; no live prerequisite
  mutation was performed; later superseded by `P7-I011` no-domain policy.
- `phase-7-client-compatibility-watch-refresh-4-8-19-2026-06-18.md` -
  `P7-N005` client compatibility watch refresh for Amnezia client `4.8.19.0`;
  `P7-C002c` stayed input-required because no DNS FQDN / exact live gate was
  supplied; later superseded by `P7-I011` no-domain policy.
- `phase-7-ip-only-exposure-policy-decision-2026-06-18.md` - `P7-I011`
  IP-only exposure policy decision; operator declined DNS domain use for AMN2
  and selected VPS IP + loopback web/admin over SSH tunnel as the default mode.
- `phase-7-watch-only-intake-status-hygiene-2026-06-18.md` - watch-only intake
  plus status hygiene after `P7-I011`; keeps `amnezia-client 4.8.19.0` as a
  compatibility signal; its temporary `amneziawg-android 2.0.0` wording is
  superseded by the later correction evidence.
- `phase-7-watch-only-intake-correction-2026-06-18.md` - watch-only correction;
  current status/navigation keeps `amnezia-client 4.8.19.0` and
  `amneziawg-android 2.0.1` as watch-only client compatibility signals.
- `phase-7-watch-only-intake-current-signals-2026-06-18.md` - current
  watch-only intake after correction; signals remain `amnezia-client 4.8.19.0`
  and `amneziawg-android 2.0.1`, with PRVTPRO/KYORESUAS retained as upstream
  signals only.
- `phase-7-docs-quality-audit-ip-env-reconcile-2026-06-18.md` - docs quality
  audit after reduced-reasoning Phase 7 edits; separates AMN3 workspace/evidence
  context from AMN2 source/package context and adds inactive `P7-C002e` public
  URL env reconciliation planning.
- `phase-7-public-url-env-reconciliation-b121865-2026-06-19.md` - `P7-C002e`
  live public URL env reconciliation for `b121865`; removed
  `PUBLIC_BASE_URL`, `PUBLIC_DOMAIN` and `WEB_PUBLIC_BASE_URL`, created VPS
  rollback copy and confirmed no public exposure was applied.
- `phase-7-watch-only-intake-current-signals-2026-06-19.md` - current
  watch-only intake after `P7-C002e`; signals remain `amnezia-client 4.8.19.0`
  and `amneziawg-android 2.0.1`, with PRVTPRO/KYORESUAS retained as upstream
  signals only.
- `phase-7-ip-only-public-exposure-risk-guard-b121865-2026-06-19.md` -
  `P7-C002d` IP-only public exposure risk guard; blocked by UFW inactive, no
  reverse proxy binary, no trusted DNS/TLS path for IP-only admin and explicit
  risk acceptance requirement; no public exposure apply was performed.
- `phase-7-config-write-read-only-preflight-2026-06-19.md` - grouped
  `P7-C003 + P7-C005` read-only preflight; confirms config delivery is blocked
  by missing channel/SMTP/secret-safe delivery decision and write/install
  mutation is blocked by read-only RC policy, prior `write_api_route_count=0`,
  `VPS_APPLY_ENABLED=false` and `LOCAL_AGENT_ENABLED=false`.
- `phase-7-config-delivery-operator-local-guard-b121865-2026-06-19.md` -
  `P7-C003` operator-local config delivery guard; channel selected as
  `operator-local`, loopback web healthy, public probes closed, route inventory
  and DB aggregate counts collected, actual delivery blocked until target
  user/device, private artifact destination and one-time/revocation policy are
  selected; no config payload or secret output was performed.
- `phase-7-config-delivery-target-inventory-b121865-2026-06-19.md` -
  `P7-C003` read-only target inventory; valid next target pairs are
  `TARGET_USER_ID=1 TARGET_DEVICE_ID=1` or
  `TARGET_USER_ID=1 TARGET_DEVICE_ID=2`; both devices are active with
  `config_material_status=available`; no config delivery or secret output was
  performed.
- `phase-7-config-delivery-private-handoff-device1-b121865-2026-06-19.md` -
  `P7-C003` target-specific operator-local private handoff for
  `TARGET_USER_ID=1` / `TARGET_DEVICE_ID=1`; private file copied to the
  operator-selected local destination outside the workspace; bytes/hash matched
  and remote temp artifact was removed; no config payload or client secret was
  printed to chat/evidence.
- `phase-7-config-delivery-private-handoff-device2-b121865-2026-06-19.md` -
  `P7-C003` target-specific operator-local private handoff for
  `TARGET_USER_ID=1` / `TARGET_DEVICE_ID=2`; private file copied to the
  operator-selected local destination outside the workspace; bytes/hash matched
  and remote temp artifact was removed; no config payload or client secret was
  printed to chat/evidence. Together with device 1, both known active devices
  from the target inventory have completed private-file handoff.
- `phase-7-write-backup-telegram-read-only-preflight-2026-06-19.md` -
  `P7-C005 + P7-C006 + P7-C007` read-only preflight; at that time write API
  remained read-only for RC, backup/restore/import remained apply-blocked, and
  Telegram identity/profile/media remained mutation-blocked. This was later
  superseded for `P7-C005` by the 2026-06-20 scoped write contour. No live
  action, mutation or secret-bearing output was performed in the read-only
  preflight.
- `phase-7-post-clean-write-backup-telegram-read-only-rebaseline-b121865-2026-06-19.md`
  - `P7-C005 + P7-C006 + P7-C007` post-clean read-only rebaseline after
  `P7-C004b`; clean `b121865` install stayed loopback-only, public API route
  inventory remained read-only with `write_api_route_count=0`, backup help was
  safe without backup create, Telegram token presence was checked without token
  use/API call, and external probes stayed closed.
- `phase-7-backup-only-evidence-b121865-2026-06-19.md` - `P7-C006`
  backup-only evidence on disposable VPS `89.185.80.166`; backup create and
  verify passed after env propagation root cause was identified; no restore,
  import, reboot, remote backup download or backup contents output.
- `phase-7-destructive-clean-installer-precutover-guard-b121865-2026-06-19.md`
  - `P7-C004a` destructive clean installer pre-cutover guard; package/source and
  backup prerequisite matched, blocker count was zero, and no wipe/reinstall/apply
  was performed.
- `phase-7-destructive-clean-installer-execution-b121865-2026-06-19.md` -
  `P7-C004b` destructive clean installer execution; operator provided exact
  destructive gate and final phrase, old `/opt/amn2` was moved to root-only
  quarantine, clean `b121865` install was applied, DB initialized, loopback web
  started, API loopback smoke passed and external probes stayed closed. No
  provider rebuild, reboot, restore/import, public exposure, config delivery,
  write API, Local Agent mutation, production peer/user mutation, Telegram
  action or secret-bearing output was performed.
- `phase-7-watch-only-intake-after-critical-preflights-2026-06-19.md` -
  watch-only intake after `P7-C003` known-device handoffs and
  `P7-C005 + P7-C006 + P7-C007` read-only preflight; no live action, mutation or
  new implementation task was created.
- `phase-7-watch-only-intake-cycle-complete-2026-06-19.md` - current
  watch-only intake cycle closeout; observed client signals remain
  `amnezia-client 4.8.19.0` and `amneziawg-android 2.0.1`; no live action,
  mutation, upstream/GPL code copy or new implementation task was created.
- `phase-7-write-install-mutation-contour-5501295-2026-06-20.md` - `P7-C005`
  scoped write/install mutation contour; AMN2 `codex-vps-test-prep` was
  advanced to `5501295`, package/source checksums were verified, live source
  overlay apply and baseline API smoke passed, `POST
  /api/install/mutation-requests` required `install:write`, returned
  `recorded_blocked_by_vps_apply_disabled` while `VPS_APPLY_ENABLED=false`,
  recorded safe `api_write` audit metadata and kept external probes closed.
  No actual installer executor, public exposure, config delivery,
  restore/import/reboot, Local Agent mutation, Telegram action or
  secret-bearing output was performed.
- `phase-7-provider-backup-restore-point-watch-hygiene-2026-06-20.md` -
  `P7-C006a` provider backup restore-point confirmation plus watch-only status
  hygiene; operator screenshot evidence was inconclusive because it showed
  backup creation success, move-to-internal-storage failure and backup deletion
  success, so provider restore-point availability is not confirmed. No provider
  mutation, restore/import/reboot, remote backup download, live VPS/SSH command
  or secret-bearing output was performed.
- `phase-7-current-state-backup-only-5501295-2026-06-20.md` - `P7-C006`
  current-state backup-only evidence for AMN2 `5501295`; backup create and
  verify passed, artifact stayed on the VPS under
  `/opt/amn2/backups/p7-c006-current-state-5501295-20260620T050111Z`, sha256
  `1412e6791ba03e0f955d46e988357274a413d0afc96a2e72c1b6077624554bb2`, and no
  restore/import/reboot/provider mutation/remote download or secret output was
  performed.
- `phase-7-telegram-defer-private-rc-2026-06-20.md` - `P7-C007` Telegram
  identity/profile/media decision; deferred as not required for private/operator
  RC, with no Telegram token use, API call, live bot send, profile/media
  mutation, media upload, credential handoff or secret output.

## Readiness Evidence

- `phase-7-clean-installer-rc-checklist-security-contract-2026-06-14.md` -
  clean installer RC checklist, asset path verification and secret/input
  contract.
- `phase-7-multi-instance-taxonomy-release-notes-2026-06-14.md` -
  multi-instance/IPAM incorporation, API/docs taxonomy drift check and release
  notes skeleton.
- `phase-7-automation-client-watch-copy-polish-2026-06-14.md` - automation
  intake, client watch refresh and operator copy polish.
- `phase-7-public-config-write-prerequisite-split-2026-06-14.md` - split
  combined public/config/write preflight into separate readiness tracks.
- `phase-7-public-exposure-readiness-design-2026-06-14.md` - `P7-C002`
  public exposure readiness.
- `phase-7-config-delivery-channel-readiness-2026-06-14.md` - `P7-C003`
  config delivery channel readiness.
- `phase-7-write-api-scope-decision-2026-06-14.md` - `P7-C005` write API scope
  decision; RC policy keeps public API read-only.
- `phase-7-backup-restore-import-readiness-2026-06-14.md` - `P7-C006`
  backup/restore/import readiness.
- `phase-7-backup-only-evidence-b121865-2026-06-19.md` - `P7-C006`
  backup-only create/verify evidence.
- `phase-7-destructive-clean-installer-precutover-guard-b121865-2026-06-19.md`
  - `P7-C004a` pre-cutover guard before final destructive stop-line.
- `phase-7-destructive-clean-installer-execution-b121865-2026-06-19.md` -
  `P7-C004b` clean installer execution and loopback smoke evidence.
- `phase-7-telegram-identity-readiness-2026-06-14.md` - `P7-C007` Telegram
  identity/profile/media readiness.

## Handoff / Navigation Evidence

- `phase-7-next-chat-status-hygiene-2026-06-14.md` - first next-chat/status
  hygiene pass.
- `phase-7-rc-gate-matrix-consolidation-2026-06-14.md` - RC Gate Matrix
  consolidation.
- `phase-7-final-rc-handoff-compression-2026-06-14.md` - compact next-chat
  handoff.

## Watch-Only Intake Status

Automation IDs remain watch-only intake signals:

- `prvtpro-weekly-upstream-refresh` - Sunday 10:00.
- `weekly-kyoresuas-upstream-refresh` - Sunday 11:00.
- `amnezia-weekly-upstream-refresh` - Sunday 12:00.

Current Phase 7 treatment:

- use reports only as upstream/client compatibility signals;
- do not copy upstream/GPL implementation code;
- do not infer permission for live/public/config/write/destructive/Telegram
  actions from automation output;
- missing or inaccessible reports must be marked `missing-input`, not invented.

Current watch-only check:

```text
automation_chain_status=expected-active
latest_known_phase7_intake=phase-7-automation-client-watch-copy-polish-2026-06-14.md
latest_watch_only_intake=phase-7-watch-only-intake-cycle-complete-2026-06-19.md
client_watch_status=signals-only-amnezia-client-4.8.19.0-amneziawg-android-2.0.1
provider_restore_point_status=not-confirmed-by-P7-C006a
current_state_backup_status=completed-for-5501295
permission_to_open_live_gate=false
```

## Current-Fixes State Drift

- `phase-7-state-drift-clean-worktree-2026-06-21.md` - local-only guard after
  manual upstream-refresh and mobile VPN debugging; confirms Phase 7 fixes must
  continue from clean AMN2 worktree
  `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current` on
  `471bca8 Downgrade DefaultVPN iOS compatibility`, while the older
  `C:\Users\SooL\Documents\Amneziya` checkout is behind by four commits and
  dirty. No live VPS/SSH, package apply, config delivery, Telegram action,
  restore/import/reboot, provider mutation, write execution or secret-bearing
  output was performed.
- `phase-7-android-acceptance-contract-471bca8-2026-06-21.md` - local-only
  AMN2 code/tests slice from clean worktree `471bca8`; Android AmneziaWG remains
  a supported candidate but is now machine-marked
  `pending_real_device_acceptance` and `release_primary_allowed=false`, QR and
  full `vpn://` are not release-primary, and Windows desktop remains accepted
  only by operator observation. Focused verification: `9 passed`; syntax
  verification passed. No live VPS/SSH, package apply, config delivery,
  Telegram action, restore/import/reboot, provider mutation, write execution or
  secret-bearing output was performed.
- `phase-7-mobile-dataplane-closeout-c011f2-2026-06-21.md` - `P7-C011f2`
  read-only live AWG handshake observation and operator Android observation;
  confirms the live dataplane on UDP `30001` is working and that old matched
  config `Neobyatnaya-AMNZ.conf`/peer `a6a551084fad` is active with fresh
  handshake and growing transfer counters. The old matched configs are
  diagnostic proof only, not release delivery artifacts. Phase 8 entry is
  `phase8-prep-ready`, but launch remains blocked until fresh per-device
  Android config acceptance. No config payload, key, PSK, QR, `vpn://`, token,
  container/config mutation, Telegram send, restore/import/reboot, provider
  mutation, write execution or public exposure was performed.

## Operator Named-Gate Menu

Choose exactly one exact named gate before any live/public/config/write/
backup/destructive/Telegram action:

- `P7-C002` Public exposure gate.
  Latest prerequisite updates made admin/domain fields present in `.env` and
  verified loopback runtime/login. Public cutover guard blocked apply because
  current public URL/domain are IP-based and trusted TLS requires a DNS domain.
  Operator later declined DNS domain use for AMN2 in `P7-I011`; the selected
  default mode is VPS IP + SSH tunnel to loopback web/admin. The 2026-06-20
  Telegram-first/operator-web policy makes public web-admin exposure not
  required for private/operator RC because users are served through Telegram.
  `P7-C002e` removed the IP-based public URL residue from live `.env`.
  `P7-C002d` then blocked IP-only public exposure by four risk blockers and
  performed no reverse proxy, TLS, firewall or public listener apply. Any
  future IP-only public web/admin exposure requires a new separate exact
  risk-acceptance/design gate.
- `P7-C003` Config delivery gate.
  Opens only the explicitly named config delivery channel scope. Latest
  operator-local guard selected `operator-local` as the practical channel but
  keeps real delivery blocked until the exact target user/device, private
  artifact destination and one-time/revocation policy are selected. Latest
  read-only target inventory found valid pairs `1/1` and `1/2`; both are now
  completed through private file handoff. Any resend/revocation, SMTP/Telegram
  delivery, public/self-service config link or new target device still requires
  a separate exact named gate. Evidence and chat must not contain config payloads
  or client secrets.
- `P7-C004` Destructive clean installer execution gate.
  `P7-C004b` is complete for `b121865` on disposable VPS `89.185.80.166` as
  clean install + loopback smoke. Any future destructive provider rebuild,
  another clean install, restore/import or quarantine cleanup remains a separate
  exact named gate.
- `P7-C005` Write API / install mutation gate.
  Completed for the scoped audit-only `install:write` contour on `5501295`.
  Future actual installer runner, broader write API routes or Local Agent
  mutation require a new exact named gate.
- `P7-C006` Backup/restore/import gate.
  Opens only the explicitly named backup/restore/import scope. Latest read-only
  and post-clean rebaseline evidence keeps restore apply, archive import, remote
  backup download and reboot disabled. Current-state backup-only create/verify
  evidence now exists for `5501295`; provider restore-point evidence remains
  inconclusive and provider restore use requires a separate exact gate.
- `P7-C007` Telegram identity/profile/media mutation gate.
  Deferred as not required for private/operator RC. Future Telegram token use,
  live bot send, profile/media mutation, media upload or credential handoff
  remains exact named gate only.

If no exact gate is chosen, continue with watch-only intake only.

## Named-Gate Dry Checklist Review

Before any exact named gate, verify:

- gate phrase exactly names the gate and target;
- target commit/head is explicit;
- allowed actions are narrower than the gate boundary;
- rollback/stop criteria are stated;
- evidence destination is safe and secret-free;
- no secret-bearing payload will be pasted into AMN3 evidence;
- `VPS_APPLY_ENABLED` stays false unless the named gate explicitly requires and
  authorizes changing it;
- any live command waits for operator confirmation and password entry flow.

## Final RC Notes Status

AMN2 release notes skeleton is still pre-release material. It may cite
`b121865` as VPS-smoked/pass after `P7-C001`, but it must not claim public
release, public exposure, config delivery, write API, backup/import,
destructive execution or Telegram mutation.
