# AMN2 Fresh Installer Backlog

Дата: 2026-06-20.

Назначение: зафиксировать будущий путь к чистому установщику AMN2 через
вопрос-ответ, safe defaults, preflight, dry-run and named gates. Этот документ
не разрешает зачистку текущего VPS, установку на новый VPS, live SSH, package
apply, public exposure, config delivery, write API или production mutations.

## Current Baseline

```text
AMN2 branch: codex-vps-test-prep
AMN2 current source/security-fix head: c958733 Harden security-sensitive operations
AMN2 latest VPS-smoked head: c958733 Harden security-sensitive operations
AMN2 latest local RC package-ready head: c958733 Harden security-sensitive operations
AMN2 known-good package head: c958733 Harden security-sensitive operations
AMN2 package status: VPS-smoked/pass for c958733
AMN2 next package/apply target: completed by P7-C009
AMN2 Codex Security post-fix status: completed-no-open-findings-for-c958733
AMN2 current-head RC package status: package-ready-and-vps-smoked for c958733
AMN2 public/config/write status: blocked-by-preconditions
AMN2 public exposure status: deferred-not-required-for-private-rc-not-exposed
AMN2 user channel policy: telegram-first
AMN2 operator web policy: vps-ip-loopback-ssh-tunnel-no-public-web-required
AMN2 public/config/write prerequisite split status: completed
AMN2 public exposure readiness/design status: completed
AMN2 config delivery channel readiness status: completed
AMN2 write API scope decision status: completed
AMN2 backup/restore/import readiness status: completed
AMN2 Telegram identity/profile/media readiness status: completed
AMN2 RC gate matrix consolidation status: completed
AMN2 final RC handoff/status compression status: completed
AMN2 Phase 7 evidence index / dry checklist / RC notes status: completed
AMN2 final RC freeze/status: completed-rc-ready-paused-state-c958733-no-live-action
AMN2 direct clean installer status: completed-direct-clean-install-5501295-loopback-smoke
AMN2 post-direct-clean login/backup status: completed-login-verified-backup-create-verify
AMN2 Phase 7 final freeze / named-gate menu status: completed
AMN2 P7-C002b runtime/login verification status: completed-not-exposed
AMN2 P7-C002 public cutover guard status: blocked-by-domain-tls-not-exposed
AMN2 P7-C002c DNS/domain/TLS prerequisite staging status: superseded-operator-declined-dns-domain
AMN2 P7-C002d IP-only public exposure risk guard status: blocked-not-exposed
AMN2 P7-N005 client compatibility watch refresh status: completed-no-config-delivery
AMN2 P7-I011 IP-only exposure policy status: completed-operator-declined-dns-domain
AMN2 latest watch-only/status hygiene: completed-no-live-action
AMN2 latest docs quality audit/env reconcile planning: completed-no-live-action
AMN2 latest watch-only correction: completed-no-live-action
AMN2 latest watch-only intake current signals: completed-no-live-action-2026-06-19
AMN2 latest watch-only intake after critical preflights: completed-no-live-action-2026-06-19
AMN2 latest watch-only intake cycle closeout: completed-no-live-action-2026-06-19
AMN2 latest client watch signal: amnezia-client 4.8.19.0; amneziawg-android 2.0.1; no config delivery
AMN2 public URL env residue status: reconciled-removed-in-P7-C002e
AMN2 P7-C002e public URL env reconciliation status: completed-live-env-reconcile-not-exposed
AMN2 P7-C003 + P7-C005 read-only preflight status: completed-blocked-no-delivery-no-write
AMN2 P7-C003 operator-local config delivery guard status: blocked-pending-target-and-private-handoff-no-delivery
AMN2 P7-C003 target inventory status: completed-read-only-target-inventory-no-delivery
AMN2 P7-C003 private handoff device 1 status: completed-private-file-copied-secret-not-printed
AMN2 P7-C003 private handoff device 2 status: completed-private-file-copied-secret-not-printed
AMN2 P7-C003 known active device handoff status: completed-for-device-1-and-device-2
AMN2 P7-C005 + P7-C006 + P7-C007 read-only preflight status: completed-no-mutation
AMN2 P7-C005 + P7-C006 + P7-C007 post-clean rebaseline status: completed-no-mutation-after-clean-install
AMN2 P7-C005 write/install contour status: completed-scoped-write-contour-smoked
AMN2 P7-C006 backup-only evidence status: completed-create-verify-no-restore-import-reboot
AMN2 P7-C006a provider restore-point status: completed-inconclusive-no-restore-point-confirmed
AMN2 P7-C006 current-state backup-only status: completed-create-verify-no-restore-import-reboot-for-5501295
AMN2 P7-C007 Telegram identity/profile/media status: deferred-not-required-for-private-rc-no-telegram-action
AMN2 P7-C008 Telegram user-flow smoke status: completed-after-token-reconciliation
AMN2 P7-C008a Telegram token reconciliation status: completed-getme-dispatcher-surface-no-send
AMN2 P7-C009 c958733 package/apply smoke status: completed-c958733-package-apply-loopback-telegram-backup-smoke
AMN2 P7-C004a destructive pre-cutover guard status: ready-final-stop-line-no-apply
AMN2 P7-C004b destructive clean installer status: completed-clean-install-loopback-smoke
AMN3 latest evidence slice: Phase 7 transition packet / clean installer RC entry
current working VPS: 89.185.80.166, disposable test VPS, c958733 package-applied and smoked loopback-only after P7-C009; users are Telegram-first, operator web/admin remains IP/loopback/private access
```

Relevant completed inputs:

- Codex Security post-fix validation for AMN2 `c958733` in
  `research/amn2/phase-7-codex-security-postfix-c958733-2026-06-20.md`;
  focused pytest `95 passed`, full pytest `729 passed`, post-fix scan
  `0` reportable findings. The follow-up `c958733` package/apply smoke was
  completed by `P7-C009`.
- Phase 7 `P7-C009` c958733 package apply + loopback/Telegram/backup smoke in
  `research/amn2/phase-7-c958733-package-apply-smoke-2026-06-20.md`.
  Package/source checksums matched, source overlay became
  `c9587332d425583ed627899d7fa950756b64c4dc`, loopback API smoke passed,
  Telegram `getMe` and non-polling dispatcher/user-flow smoke passed, backup
  create+verify passed with artifact mode `600`, and public probes stayed
  closed.
- Phase 7 final RC freeze/status pass for AMN2 `c958733` in
  `research/amn2/phase-7-final-rc-freeze-status-c958733-2026-06-20.md`.
  Current frozen state is `rc_ready_paused_private_operator_lane` on `c958733`;
  no live action or secret-bearing output was performed in the freeze pass.
- `P6-I007` local-only fresh-install wizard/bootstrap automation.
- `P6-C007` destructive cleanup/reinstall checklist-only boundary.
- `P6-C009` live update/smoke for `c46f664`, read-only smoke passed.
- `P6-C010` live update/smoke for `0de7a77`, read-only smoke passed.
- `P6-X003` package runbook escaping hygiene guardrail.
- `P5-C004` secret handoff protocol.
- `P5-C005` source-overlay permission preservation.
- `FI-I001 + FI-I002 + FI-I003` fresh installer question schema, rendered plan
  and secret handoff binding in AMN2 `de635a0`.
- `FI-M001 + FI-M002 + FI-M003` fresh installer target preflight matrix,
  runtime decision and package hygiene planning in AMN2 `7416fb0`.
- `FI-N001 + FI-N002 + FI-S001` fresh installer smoke/evidence template,
  existing-server reconciliation input and operator docs index in AMN2 `525a9cd`.
- `P6-C001 + P6-C002` docs-only public/config gate checklist refresh in AMN2
  `ff77d4c`.
- `FI-X001 + current-head package preflight planning` Russian-first installer
  prompts and `fresh-install-package-preflight.v1` planning in AMN2 `0de7a77`.
- `FI-M004 + P6-N005` package asset path preflight and API taxonomy route-order
  guard in AMN2 `4cde273`.
- `P6-M005` multi-instance/port/IPAM conflict model in AMN2 `b121865`.
- Local package build/preflight and P6-C010 live update/smoke for AMN2
  `0de7a77`, VPS-smoked/pass.
- Phase 6 final closeout and known-good snapshot evidence in
  `research/amn2/phase-6-final-closeout-known-good-snapshot-2026-06-14.md`.
- Phase 7 transition packet in
  `research/amn2/phase-7-transition-packet-2026-06-14.md`, with Phase name
  `Release Candidate Readiness / Clean Installer RC` and status `pre-release /
  release-candidate readiness`.
- Phase 7 `P7-I001 + P7-M001` current-head package/preflight and known-good
  alignment in
  `research/amn2/phase-7-current-head-package-preflight-b121865-2026-06-14.md`.
  Built `dist/amn2-vps-update-and-smoke-kit-b121865.zip`, package sha256
  `364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849`;
  at that step `0de7a77` remained the known-good VPS baseline, later superseded
  by `P7-C001`.
- Phase 7 `P7-I002 + P7-M002 + P7-I003` clean installer RC checklist,
  package/runbook path verification and secret/input hardening in
  `research/amn2/phase-7-clean-installer-rc-checklist-security-contract-2026-06-14.md`.
  AMN2 fresh installer manifest now exposes `clean_installer_rc_acceptance`,
  package asset paths/default bindings for `b121865`, and
  `secret_input_contract` with field-only secret-bearing answer rejection.
- Phase 7 `P7-M003 + P7-N002 + P7-S002` multi-instance/IPAM incorporation,
  API/docs taxonomy RC drift check and release notes skeleton in
  `research/amn2/phase-7-multi-instance-taxonomy-release-notes-2026-06-14.md`.
  AMN2 fresh installer manifest now exposes `multi_instance_ipam_rc_decision`,
  integration status exposes `api_docs_taxonomy_rc_drift_check`, and AMN2 docs
  include `docs/RELEASE_NOTES_RC_SKELETON.ru.md` without declaring a public
  release.
- Phase 7 `P7-N001 + P7-N003 + P7-X001` automation intake, client
  compatibility watch refresh and clean installer copy polish in
  `research/amn2/phase-7-automation-client-watch-copy-polish-2026-06-14.md`.
  Weekly upstream-refresh automations remain intake-only signals; AMN2 exposes
  `CLIENT_COMPATIBILITY_WATCH` through integration status without opening
  config delivery; clean installer prompts are Russian-first while stable answer
  values remain unchanged.
- Phase 7 `P7-S001` next-chat/status hygiene in
  `research/amn2/phase-7-next-chat-status-hygiene-2026-06-14.md`. The default
  local-only RC readiness queue is closed; active Phase 7 work is limited to
  critical named gates and watch-only monitoring.
- Phase 7 `P7-C001` live package/apply/smoke for AMN2 `b121865` in
  `research/amn2/phase-7-live-update-smoke-b121865-2026-06-14.md`. Package
  `dist/amn2-vps-update-and-smoke-kit-b121865.zip`, sha256
  `364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849`, was
  uploaded, checksum-verified and applied to disposable VPS `89.185.80.166`.
  Source overlay commit is `b121865f488821f6fc471c9529fb26e5d7992515`;
  `source_update_status=passed`; API loopback smoke returned `VPS verdict:
  pass`; auth/listener/audit passed; web loopback login returned `200`;
  external probes to `3030`, `3040`, `80` and `443` returned `000`. No public
  exposure, config delivery, write API production opening, backup/import/reboot,
  destructive action, Telegram mutation, secret publication or upstream/GPL code
  copy was performed.
- Phase 7 `P7-C005` write API / install mutation contour for AMN2 `5501295` in
  `research/amn2/phase-7-write-install-mutation-contour-5501295-2026-06-20.md`.
  AMN2 `codex-vps-test-prep` was advanced to
  `55012958ff6b8338254f3f68dfe6779f4bc56f5d`; local full suite returned
  `726 passed, 1 StarletteDeprecationWarning`; package sha256
  `C03D26673AD79D9487A3ED34E9657E0DCA10EBC9BB601E429385091F1DFEF407` and
  source zip sha256
  `DA7DA58E0FD8D778BD4A22471BBCD9038CC455ACD3C0538A38874215C81646D3` were
  verified. Live source overlay apply passed, loopback web and API smoke passed,
  and `POST /api/install/mutation-requests` was verified as scoped
  `install:write`, audit-only, blocked by `VPS_APPLY_ENABLED=false`, with safe
  `api_write` metadata and closed external probes. No actual installer executor,
  public exposure, config delivery, restore/import/reboot, Local Agent mutation,
  Telegram action or secret-bearing output was performed.
- Phase 7 `P7-C006a + watch-only status hygiene` in
  `research/amn2/phase-7-provider-backup-restore-point-watch-hygiene-2026-06-20.md`.
  Provider-console screenshot evidence for VPS `89.185.80.166` was recorded as
  inconclusive: backup creation succeeded, move to internal storage failed and
  backup deletion succeeded on 2026-06-15. Provider restore-point availability
  is not confirmed. No provider mutation, restore/import/reboot, remote backup
  download, live VPS/SSH command or secret-bearing output was performed.
- Phase 7 `P7-C006` current-state backup-only evidence for AMN2 `5501295` in
  `research/amn2/phase-7-current-state-backup-only-5501295-2026-06-20.md`.
  Backup create and verify passed; artifact stayed on the VPS, bytes `218552`,
  sha256 `1412e6791ba03e0f955d46e988357274a413d0afc96a2e72c1b6077624554bb2`.
  No restore/import/reboot, provider mutation, remote backup download, service
  restart, public exposure, config delivery, write execution, Local Agent
  mutation, Telegram action or secret-bearing output was performed.
- Phase 7 `P7-C004d + P7-C006b` post-direct-clean loopback admin login and
  backup-only evidence for AMN2 `5501295` in
  `research/amn2/phase-7-post-direct-clean-login-backup-5501295-2026-06-20.md`.
  Loopback admin login passed after the direct clean installer RC; backup
  create and verify passed for the clean `5501295` state; the encrypted
  artifact stayed on the VPS, bytes `204900`, sha256
  `f8e0591db75e8ec9ce58f4fa9d71972d577e1ec103194d1943a626aa9b156b97`. No
  restore/import/reboot, provider mutation, remote backup download, service
  restart, public exposure, config delivery, write execution, Local Agent
  mutation, Telegram action or secret-bearing output was performed.
- Phase 7 `P7-C007` Telegram identity/profile/media private RC decision in
  `research/amn2/phase-7-telegram-defer-private-rc-2026-06-20.md`.
  Telegram identity/profile/media mutation is deferred and is not required for
  private/operator RC readiness. No Telegram token use, Telegram API call, live
  bot send, profile/media mutation, media upload, credential handoff or
  secret-bearing output was performed.
- Phase 7 Telegram-first/operator-web policy in
  `research/amn2/phase-7-telegram-first-operator-web-policy-2026-06-20.md`.
  Users are served through Telegram; web/admin remains operator-only by VPS IP
  plus loopback/SSH tunnel or equivalent private access. Public web-admin
  exposure, DNS domain, trusted public TLS and reverse proxy are not required
  for private/operator RC. Future Telegram user-flow smoke is a separate exact
  named live Telegram gate and is not active by this docs-only policy.
- Phase 7 `P7-C008a` Telegram token reconciliation and user-flow smoke in
  `research/amn2/phase-7-telegram-token-reconciliation-user-flow-smoke-5501295-2026-06-20.md`.
  The earlier invalid-token `P7-C008` blocker is retained as historical
  evidence and resolved by `P7-C008a`. Token reconciliation used
  operator-secret handoff with rollback copy and no token output; Telegram
  `getMe` passed; non-polling bot/user-flow surface construction passed. No
  polling, live send, profile/media mutation, config payload output, write
  execution, public exposure, restore/import/reboot, provider mutation or
  secret-bearing output was performed.
- Phase 7 `P7-C002 + P7-C003 + P7-C005` public/config/write preflight for
  AMN2 `b121865` in
  `research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md`.
  Outcome: `blocked-by-preconditions`. Web remained loopback-only on
  `127.0.0.1:3030`; external probes to `3030`, `3040`, `80` and `443` returned
  `000`; `WEB_ADMIN_USERNAME=missing`; SMTP config missing;
  `VPS_APPLY_ENABLED=false`; `LOCAL_AGENT_ENABLED=false`; public API
  `write_api_route_count=0`. No public exposure, config delivery, write API
  route enablement, Local Agent mutation, live peer/user mutation or
  secret-bearing output was performed.
- Phase 7 `P7-C002` public exposure gate pre-cutover for AMN2 `b121865` in
  `research/amn2/phase-7-public-exposure-gate-precutover-b121865-2026-06-14.md`.
  Outcome: `blocked-by-preconditions`. Web remained loopback-only; external
  probes stayed closed; reverse proxy/TLS tooling was missing or inactive;
  `WEB_ADMIN_USERNAME` and public domain/base URL were missing. No reverse
  proxy, TLS, firewall, public listener or public API change was applied.
- Phase 7 `P7-C002a` public exposure admin/domain prerequisite for AMN2
  `b121865` in
  `research/amn2/phase-7-public-exposure-admin-domain-prereq-b121865-2026-06-14.md`.
  Outcome: `prerequisite-updated`. `.env` admin/domain fields are now present,
  but service restart, reverse proxy, TLS, firewall and public exposure were
  not applied.
- Phase 7 `P7-C002b` public exposure runtime reload and loopback login
  verification for AMN2 `b121865` in
  `research/amn2/phase-7-public-exposure-runtime-login-verify-b121865-2026-06-18.md`.
  Outcome: `runtime-login-verified-not-exposed`. Manual loopback runtime was
  restarted after `P7-C002a`; final live login flow returned `GET /login=200`,
  `POST /login=303`, `Location=/` and dashboard `200`; external probes to
  `3030`, `3040`, `80` and `443` stayed `000`. No reverse proxy, TLS,
  firewall, public listener, public API, config delivery, write API, Local
  Agent mutation, backup/import/reboot, destructive or Telegram action was
  performed.
- Phase 7 `P7-C002` public cutover guard for AMN2 `b121865` in
  `research/amn2/phase-7-public-cutover-guard-b121865-2026-06-18.md`.
  Outcome: `blocked-by-domain-tls-plan-not-exposed`. Runtime/login was already
  verified and stayed loopback-only; external probes to `3030`, `3040`, `80`
  and `443` stayed `000`; guard blocked apply because current public URL/domain
  are IP-based and trusted TLS requires a DNS domain. No package install,
  service restart, `.env` mutation, reverse proxy, TLS, firewall, public
  listener, public API, config delivery, write API, Local Agent mutation,
  backup/import/reboot, destructive or Telegram action was performed.
- Phase 7 `P7-C002c + watch-only intake` DNS/domain/TLS prerequisite staging
  and watch-only upstream/client intake in
  `research/amn2/phase-7-dns-domain-tls-prereq-watch-intake-2026-06-18.md`.
  Outcome: `watch-only-intake-complete-p7-c002c-input-required`.
  `P7-C002c` was not executed live because an exact named live prerequisite
  gate and operator-provided DNS FQDN were not supplied. This input-required
  state was later superseded by `P7-I011`: the operator declined DNS domain use
  for AMN2, so the DNS/domain/trusted TLS branch is closed. Watch-only intake
  observed `amnezia-vpn/amnezia-client` release `4.8.19.0` as a
  client-compatibility signal only. A later watch-only/status hygiene pass
  briefly recorded `amneziawg-android 2.0.0`, but the latest watch-only
  correction keeps `amneziawg-android 2.0.1` as current.
  No live VPS command, SSH command, `.env` mutation, reverse proxy, TLS,
  firewall, public exposure, config delivery, write API, Local Agent mutation,
  backup/import/reboot, destructive or Telegram action was performed.
- Phase 7 `P7-N005` client compatibility watch refresh for Amnezia client
  `4.8.19.0` in
  `research/amn2/phase-7-client-compatibility-watch-refresh-4-8-19-2026-06-18.md`.
  Outcome: `p7-n005-complete-p7-c002c-input-required`. The watch signal was
  refreshed without enabling config delivery. `P7-C002c` was not executed live
  because an exact named live prerequisite gate and operator-provided DNS FQDN
  were not supplied; this state was later superseded by `P7-I011` operator
  no-domain policy. No config artifact, QR, `vpn://`, SMTP delivery, public
  redeem route, client-secret output, Telegram config send, live VPS command,
  `.env` mutation, reverse proxy, TLS, firewall, public exposure, write API,
  Local Agent mutation, backup/import/reboot, destructive or Telegram action was
  performed.
- Phase 7 `P7-I011` IP-only exposure policy decision in
  `research/amn2/phase-7-ip-only-exposure-policy-decision-2026-06-18.md`.
  Outcome: `completed-local-only-operator-declined-dns-domain`. The operator
  decided not to use a DNS domain for AMN2 and to use only the VPS IP.
  `P7-C002c` DNS/domain/trusted TLS prerequisite is closed by policy. Selected
  default access is VPS IP + SSH tunnel to loopback web/admin
  `127.0.0.1:3030`. Public web/admin exposure, trusted TLS cutover, reverse
  proxy, firewall, public listener, public API, config delivery and write API
  remain not opened. Any future IP-only public exposure requires a separate
  exact risk-acceptance gate.
- Phase 7 watch-only intake + status hygiene in
  `research/amn2/phase-7-watch-only-intake-status-hygiene-2026-06-18.md`.
  Outcome: `completed-watch-only-status-hygiene-no-live-action`. Current watch
  keeps `amnezia-client 4.8.19.0` as a client compatibility signal and corrects
  was later superseded by watch-only correction for `amneziawg-android 2.0.1`.
  `P7-I011` remains canonical: AMN2 default access is VPS IP + SSH tunnel to
  loopback web/admin, without DNS-domain trusted TLS cutover.
- Phase 7 watch-only intake correction in
  `research/amn2/phase-7-watch-only-intake-correction-2026-06-18.md`.
  Outcome: `completed-watch-only-correction-no-live-action`. It corrects the
  previous `amneziawg-android 2.0.0` wording and keeps `amneziawg-android 2.0.1`
  as the current watch-only client compatibility signal.
- Phase 7 watch-only intake current signals in
  `research/amn2/phase-7-watch-only-intake-current-signals-2026-06-18.md`.
  Outcome: `completed-watch-only-intake-current-signals-no-live-action`.
  Current signals remain `amnezia-client 4.8.19.0` and `amneziawg-android
  2.0.1`; PRVTPRO/KYORESUAS remain upstream/API signals only. No new AMN2
  implementation task was created.
- Phase 7 `P7-S005 + P7-I012` docs quality audit and IP-only env reconciliation
  planning in
  `research/amn2/phase-7-docs-quality-audit-ip-env-reconcile-2026-06-18.md`.
  Outcome: `completed-docs-only-audit-with-inactive-reconcile-gate`. Current
  workspace is AMN3 evidence repo `barakov-dot/amn3` on `master`; AMN2
  package/source truth remains `barakov-dot/amn2` `codex-vps-test-prep` at
  `b121865`. Public URL fields left by `P7-C002a` were treated as inert
  prerequisite residue after `P7-I011`; this was later reconciled in `P7-C002e`.
- Phase 7 `P7-C002e + watch-only` public URL env reconciliation in
  `research/amn2/phase-7-public-url-env-reconciliation-b121865-2026-06-19.md`.
  Outcome: `completed-live-env-reconcile-not-exposed`. Removed
  `PUBLIC_BASE_URL`, `PUBLIC_DOMAIN` and `WEB_PUBLIC_BASE_URL` from live `.env`
  on disposable VPS `89.185.80.166`; rollback copy created on VPS and must not
  be posted. Runtime stayed loopback-only and external probes remained closed.
- Phase 7 watch-only intake current signals in
  `research/amn2/phase-7-watch-only-intake-current-signals-2026-06-19.md`.
  Outcome: `completed-watch-only-intake-current-signals-no-live-action`.
  Current signals remain `amnezia-client 4.8.19.0` and `amneziawg-android
  2.0.1`; PRVTPRO/KYORESUAS remain upstream/API signals only. No new AMN2
  implementation task was created.
- Phase 7 `P7-C002d` IP-only public exposure risk guard in
  `research/amn2/phase-7-ip-only-public-exposure-risk-guard-b121865-2026-06-19.md`.
  Outcome: `blocked-pending-design-or-explicit-risk-acceptance-not-exposed`.
  Source overlay marker confirmed `b121865`; runtime stayed loopback-only;
  public `3040/80/443` listeners were absent. Guard blockers: UFW inactive, no
  reverse proxy binary, no trusted DNS/TLS path for IP-only admin and explicit
  risk acceptance requirement. No public exposure apply was performed.
- Phase 7 `P7-C003 + P7-C005` config/write read-only preflight in
  `research/amn2/phase-7-config-write-read-only-preflight-2026-06-19.md`.
  Outcome: `completed-read-only-preflight-blocked-no-delivery-no-write`.
  At that time `P7-C003` was blocked by missing delivery channel decision,
  missing SMTP config / attachment policy and no selected secret-safe
  operator-local delivery policy. `P7-C005` was also still blocked by read-only
  RC policy, prior `write_api_route_count=0`, `VPS_APPLY_ENABLED=false` and
  `LOCAL_AGENT_ENABLED=false`; this was later superseded by the 2026-06-20
  scoped write contour on `5501295`. No config delivery was performed.
- Phase 7 `P7-C003` operator-local config delivery guard in
  `research/amn2/phase-7-config-delivery-operator-local-guard-b121865-2026-06-19.md`.
  Outcome: `blocked-pending-target-and-private-handoff-no-delivery`. Channel is
  selected as `operator-local`; SMTP remains missing. Loopback/admin readiness
  and safe route/DB aggregate evidence were collected, but actual config
  delivery remains blocked until target user/device, private artifact destination
  and one-time delivery/revocation policy are selected. No config artifact or
  client secret output was performed.
- Phase 7 `P7-C003` target inventory for operator-local handoff in
  `research/amn2/phase-7-config-delivery-target-inventory-b121865-2026-06-19.md`.
  Outcome: `completed-read-only-target-inventory-no-delivery`. Valid target
  pairs are `TARGET_USER_ID=1 TARGET_DEVICE_ID=1` and
  `TARGET_USER_ID=1 TARGET_DEVICE_ID=2`; both devices are active with available
  config material. No config artifact or client secret output was performed.
- Phase 7 `P7-C003` private operator-local handoff for
  `TARGET_USER_ID=1 TARGET_DEVICE_ID=1` in
  `research/amn2/phase-7-config-delivery-private-handoff-device1-b121865-2026-06-19.md`.
  Outcome: `completed-private-file-copied-secret-not-printed`. The private file
  was copied to the operator-selected local destination outside the workspace,
  remote temp artifact was removed and bytes/hash matched. No config payload or
  client secret was printed to chat/evidence.
- Phase 7 `P7-C003` private operator-local handoff for
  `TARGET_USER_ID=1 TARGET_DEVICE_ID=2` in
  `research/amn2/phase-7-config-delivery-private-handoff-device2-b121865-2026-06-19.md`.
  Outcome: `completed-private-file-copied-secret-not-printed`. The private file
  was copied to the operator-selected local destination outside the workspace,
  remote temp artifact was removed and bytes/hash matched. Together with device
  1, both known active devices from the target inventory have completed private
  handoff. No config payload or client secret was printed to chat/evidence.
- Phase 7 `P7-C005 + P7-C006 + P7-C007` write/backup/Telegram read-only
  preflight in
  `research/amn2/phase-7-write-backup-telegram-read-only-preflight-2026-06-19.md`.
  Outcome: `completed-read-only-preflight-no-mutation`. Write API remains
  read-only for RC, backup/restore/import remains apply-blocked and Telegram
  identity/profile/media remains mutation-blocked. No live action or
  secret-bearing output was performed.
- Phase 7 `P7-C005 + P7-C006 + P7-C007` post-clean read-only rebaseline in
  `research/amn2/phase-7-post-clean-write-backup-telegram-read-only-rebaseline-b121865-2026-06-19.md`.
  Outcome: `completed-post-clean-read-only-rebaseline-no-mutation`. After
  `P7-C004b`, clean `b121865` stayed loopback-only, external probes stayed
  closed, public API route inventory returned `write_api_route_count=0`, backup
  help probing was safe without backup create and Telegram token presence was
  checked without token use/API call. This was later superseded for `P7-C005`
  by the 2026-06-20 scoped write contour; residual restore/import/reboot and
  Telegram mutation scopes remain separate exact gates.
- Phase 7 `P7-C006` backup-only evidence gate in
  `research/amn2/phase-7-backup-only-evidence-b121865-2026-06-19.md`.
  Outcome: `completed-backup-only-create-verify-no-restore-import-reboot`.
  Backup create and verify passed; the backup artifact stayed on the VPS and
  was not downloaded. Restore/import/reboot/destructive scopes remain separate
  exact gates.
- Phase 7 `P7-C004a` destructive clean installer pre-cutover guard in
  `research/amn2/phase-7-destructive-clean-installer-precutover-guard-b121865-2026-06-19.md`.
  Outcome: `ready-for-final-destructive-stop-line-no-apply`. Package/source and
  backup prerequisite checks passed with blocker count `0`; no wipe/reinstall/
  apply was performed.
- Phase 7 `P7-C004b` destructive clean installer execution in
  `research/amn2/phase-7-destructive-clean-installer-execution-b121865-2026-06-19.md`.
  Outcome: `completed-clean-install-loopback-smoke`. Old `/opt/amn2` was moved
  to root-only quarantine, clean `/opt/amn2` was installed from verified
  `b121865` package/source, DB initialization passed, loopback web returned
  `/login=200`, API loopback smoke returned `VPS verdict: pass`, and external
  probes stayed closed. No provider rebuild, reboot, restore/import, public
  exposure, config delivery, write API, Local Agent mutation, Telegram action or
  secret-bearing output was performed.
- Phase 7 watch-only intake after critical preflights in
  `research/amn2/phase-7-watch-only-intake-after-critical-preflights-2026-06-19.md`.
  Outcome: `completed-watch-only-intake-after-critical-preflights-no-live-action`.
  Known active `P7-C003` handoffs are complete; `P7-C005` was later completed
  for the scoped write contour, residual `P7-C006` scopes remain separate exact
  named gates only, and `P7-C007` was later deferred as not required for private
  RC.
- Phase 7 watch-only intake cycle closeout in
  `research/amn2/phase-7-watch-only-intake-cycle-complete-2026-06-19.md`.
  Outcome: `completed-watch-only-intake-cycle-complete-no-live-action`.
  Current observed client signals remain `amnezia-client 4.8.19.0` and
  `amneziawg-android 2.0.1`; no new AMN2 implementation task was created.
- Phase 7 `P7-I004` public/config/write prerequisite split in
  `research/amn2/phase-7-public-config-write-prerequisite-split-2026-06-14.md`.
  AMN2 fresh installer manifest and `/api/integration/status` now expose
  `public_config_write_prerequisite_split` with three readiness tracks:
  `P7-C002` public exposure readiness, `P7-C003` config delivery channel
  readiness and `P7-C005` write API scope decision. Combined
  `P7-C002 + P7-C003 + P7-C005` should not be retried as one live enablement
  step.
- Phase 7 `P7-I005` public exposure readiness/design in
  `research/amn2/phase-7-public-exposure-readiness-design-2026-06-14.md`. AMN2
  fresh installer manifest and `/api/integration/status` now expose
  `public_exposure_readiness_design` with checklists for admin credential
  contract, domain/TLS/reverse-proxy plan, firewall/listener plan, external
  probe matrix and rollback-to-loopback. No live public exposure was performed.
- Phase 7 `P7-I006` config delivery channel readiness in
  `research/amn2/phase-7-config-delivery-channel-readiness-2026-06-14.md`.
  AMN2 fresh installer manifest and `/api/integration/status` now expose
  `config_delivery_channel_readiness` with checklists for SMTP/operator-local
  channel decision, secret-safe evidence protocol, client import matrix,
  one-time delivery policy and delivery revocation story. API/rendered-plan
  views redact exact forbidden evidence marker names to count/policy while the
  local manifest keeps the full validation contract. No live config delivery
  was performed.
- Phase 7 `P7-I007` write API scope/implementation decision in
  `research/amn2/phase-7-write-api-scope-decision-2026-06-14.md`. AMN2 fresh
  installer manifest and `/api/integration/status` now expose
  `write_api_scope_decision` with selected RC policy
  `keep_public_api_read_only_for_rc`. Write API, public write routes, Local
  Agent mutation and production peer/user mutation remain disabled; deferred
  options require `P7-C005`. No write API enablement was performed.
- Phase 7 `P7-I008` backup/restore/import prerequisite checklist in
  `research/amn2/phase-7-backup-restore-import-readiness-2026-06-14.md`. AMN2
  fresh installer manifest and `/api/integration/status` now expose
  `backup_restore_import_readiness` with live backup, restore apply, archive
  import and reboot disabled. No backup create, restore apply, archive import
  apply or reboot was performed.
- Phase 7 `P7-I009` Telegram identity/profile/media prerequisite checklist in
  `research/amn2/phase-7-telegram-identity-readiness-2026-06-14.md`. AMN2
  fresh installer manifest and `/api/integration/status` now expose
  `telegram_identity_readiness` with Telegram API, token use, profile mutation,
  media mutation and live bot send disabled. No Telegram token use, live bot
  send, profile mutation or media upload was performed.
- Phase 7 `P7-I010` RC gate matrix consolidation in
  `research/amn2/phase-7-rc-gate-matrix-consolidation-2026-06-14.md`. AMN3
  Phase 7 plan now maps each remaining `P7-C002`...`P7-C007` gate to readiness
  source, current blocker/status and allowed next action. No new gate was
  opened.
- Phase 7 `P7-S003` final RC handoff/status compression in
  `research/amn2/phase-7-final-rc-handoff-compression-2026-06-14.md`. The
  Phase 7 next-chat handoff is now compact and separates current state,
  approved remaining plan, RC Gate Matrix and inactive proposals. No new gate
  was opened.
- Phase 7 `P7-N004 + watch-only intake + named-gate dry checklist + RC notes
  polish` in
  `research/amn2/phase-7-evidence-watch-drycheck-rcnotes-2026-06-14.md`. Added
  `docs/AMN2_PHASE_7_EVIDENCE_INDEX.ru.md`; upstream automations remain
  watch-only; named-gate dry checklist is recorded; AMN2 RC notes skeleton now
  reflects `b121865` as latest known-good VPS-smoked/package baseline. No new
  gate was opened.
- Phase 7 `P7-S004 + watch-only intake check + operator named-gate menu review`
  in `research/amn2/phase-7-final-freeze-watch-menu-2026-06-14.md`. Phase 7
  local-only expansion is frozen before any named gate; next substantive step
  is exact named gate or watch-only intake only.

## Backlog Status

All items below are candidates. None are active by default.

### Critical gated/deferred

- `FI-C001` Destructive clean install execution gate.
  Maps to `P6-C007`. Requires exact named destructive phrase, target decision,
  retention/data-loss acceptance, stop criteria, package choice, rollback story
  and second confirmation.

- `FI-C002` Public exposure cutover gate.
  Maps to `P6-C001`. Required before domain, HTTPS, reverse proxy, public web,
  public API or firewall/listener changes.

- `FI-C003` Config delivery enablement gate.
  Maps to `P6-C002`. Required before `.conf`, QR, `vpn://`, public token redeem,
  Telegram real config delivery or self-service download.

- `FI-C004` Write API/install mutation gate.
  Maps to `P6-C003`, Local Agent write/config routes and production peer/user
  mutation. Required before `/api/clients` CRUD, peer sync/apply/revoke,
  server config rewrite or automated live install changes.

- `FI-C005` Backup/restore/import gate.
  Maps to `P6-C004`. Required before archive import, restore apply, reboot,
  destructive migration or disaster recovery drill on a live target.

### Very important local-only

Completed:

- `FI-I001` Installer question model hardening.
  Extend the existing `P6-I007` wizard with explicit answer schema versions,
  validation groups and stop-line explanations. Completed in AMN2 `de635a0`.

- `FI-I002` Install plan renderer.
  Generate a redacted, operator-readable install plan from answers, including
  package choice, secrets needed through operator-local channel, expected
  listeners and smoke steps. Completed in AMN2 `de635a0`.

- `FI-I003` Secret handoff checklist binding.
  Bind the installer plan to `docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md` so raw
  tokens, `.env`, `servers.yml`, client configs, QR and `vpn://` never enter
  AMN3 evidence. Completed in AMN2 `de635a0`.

### Important local-only

Completed:

- `FI-M001` Target OS/runtime preflight matrix.
  Define read-only checks for Ubuntu version, Python runtime, Docker, ports,
  disk, time sync and package prerequisites. Live execution requires a named
  read-only diagnostic gate. Completed in AMN2 `7416fb0`.

- `FI-M002` Runtime mode decision.
  Keep manual runtime vs systemd vs reverse proxy as an explicit answer. No
  service enable/restart by default. Completed in AMN2 `7416fb0`.

- `FI-M003` Package hygiene integration.
  Include `scripts/check_markdown_hygiene.py`, source zip checksum, forbidden
  source entries, shell LF/no-BOM and operator runbook checks in future package
  builds. Do not rewrite already-smoked evidence packages. Completed in AMN2
  `7416fb0`.

### Normal local-only

Completed:

- `FI-N001` Smoke/evidence template.
  Reuse read-only loopback smoke, auth/listener/audit summary, external closed
  probes and no-secret evidence review. Completed in AMN2 `525a9cd`.

- `FI-N002` Existing-server reconciliation input.
  Reuse report-only reconciliation before any clean install. No auto-fix,
  import, peer creation/removal or config overwrite. Completed in AMN2 `525a9cd`.

### Simple/cosmetic

Completed:

- `FI-S001` Installer docs index.
  Create a short operator index linking wizard, destructive checklist, secret
  handoff, package hygiene and smoke evidence rules. Completed in AMN2 `525a9cd`.

- `FI-X001` Russian-first prompt copy polish.
  Keep prompts short, direct and safe, while preserving stable technical IDs.
  Completed in AMN2 `0de7a77`.

## Recommended Order

1. Pause on known-good `b121865` unless the operator intentionally opens a
   named gate.
2. Treat `0de7a77` as the previous known-good baseline and keep its evidence for
   rollback/history comparison only.
3. Do not retry `P7-C002 + P7-C003 + P7-C005` as one live enablement step until
   public exposure, config delivery channel and write API surface prerequisites
   are split and prepared.
4. Treat the default local-only RC readiness queue as closed. Continue only
   with a separate exact named gate or watch-only monitoring.

## Hard Stop Lines

Stop and require a separate named gate if any step would:

- run SSH or live VPS commands;
- upload/apply a package to a VPS;
- stop/restart/deploy services;
- open public `3030`, `3040`, `80`, `443`, domain, HTTPS or reverse proxy;
- emit `.conf`, QR, `vpn://`, config body or client secret;
- enable write API, Local Agent mutation, backup/import/reboot or peer/user
  mutation;
- delete, wipe, rebuild or reinstall a VPS;
- use Telegram tokens, live bot send or Telegram identity/profile mutation;
- publish secret-bearing evidence;
- copy upstream/GPL implementation code.
