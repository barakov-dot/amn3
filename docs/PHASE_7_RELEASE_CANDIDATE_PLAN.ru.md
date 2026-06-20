# AMN2 Phase 7 Release Candidate Plan

Дата: 2026-06-20.

Название фазы: `Phase 7: Release Candidate Readiness / Clean Installer RC`.

Статус: `pre-release / release-candidate readiness`.

Текущий freeze status:
`completed-rc-ready-paused-state-c958733-no-live-action` для AMN2 `c958733`.

Режим по умолчанию:
`local-only/docs/tests/security/package-preflight/watch-only` unless an exact
named live gate is opened.

Эта фаза не открывает public launch, production mutation, config delivery,
write API, destructive install, live package apply или Telegram identity changes.

RC channel policy:

- user-facing channel: Telegram-first;
- operator web/admin channel: VPS IP plus loopback/SSH tunnel or equivalent
  private operator access;
- public web-admin exposure, DNS domain, trusted public TLS and reverse proxy
  are not required for private/operator RC.

## Источник Правды

```text
AMN2 current local head: c958733 Harden security-sensitive operations
AMN2 known-good VPS-smoked/package head: c958733 Harden security-sensitive operations
AMN2 current local RC package-ready head: c958733 Harden security-sensitive operations
Workspace/evidence repo: barakov-dot/amn3, branch master, latest pushed head;
verify with `git log -1`
AMN2 package/source repo: barakov-dot/amn2, branch codex-vps-test-prep, head c958733
Current disposable VPS: 89.185.80.166
Known-good evidence: research/amn2/phase-7-c958733-package-apply-smoke-2026-06-20.md
Latest current-state backup evidence: research/amn2/phase-7-current-state-backup-only-5501295-2026-06-20.md
Latest post-direct-clean login/backup evidence: research/amn2/phase-7-post-direct-clean-login-backup-5501295-2026-06-20.md
Latest Telegram private RC decision: research/amn2/phase-7-telegram-defer-private-rc-2026-06-20.md
Latest final RC freeze/status evidence: research/amn2/phase-7-final-rc-freeze-status-c958733-2026-06-20.md
Latest direct clean installer evidence: research/amn2/phase-7-direct-clean-installer-5501295-2026-06-20.md
Latest Telegram-first/operator-web policy: research/amn2/phase-7-telegram-first-operator-web-policy-2026-06-20.md
Latest Telegram user-flow smoke evidence: research/amn2/phase-7-telegram-token-reconciliation-user-flow-smoke-5501295-2026-06-20.md
Latest c958733 package/apply smoke evidence: research/amn2/phase-7-c958733-package-apply-smoke-2026-06-20.md
```

## Выполнено В Phase 7

- `P7-C009` c958733 package apply + loopback/Telegram/backup smoke.
  Importance: critical current-head VPS validation. Gate: exact named live VPS
  package/apply smoke on disposable VPS `89.185.80.166`. Evidence:
  `research/amn2/phase-7-c958733-package-apply-smoke-2026-06-20.md`. Result:
  closed as `completed-c958733-package-apply-loopback-telegram-backup-smoke`.
  Package/source checksums matched, source overlay became
  `c9587332d425583ed627899d7fa950756b64c4dc`, loopback web/API smoke passed,
  Telegram `getMe` and non-polling dispatcher/user-flow smoke passed, backup
  create+verify passed with artifact mode `600`, and public probes stayed
  closed.

- Final RC freeze/status pass for AMN2 `c958733`.
  Importance: critical status hygiene. Gate: docs-only/local-only; no live
  action. Evidence:
  `research/amn2/phase-7-final-rc-freeze-status-c958733-2026-06-20.md`.
  Result: closed as
  `completed-rc-ready-paused-state-c958733-no-live-action`. Phase 7 is frozen
  as `rc_ready_paused_private_operator_lane`: latest VPS-smoked/package head
  and current VPS source overlay are `c958733`; web remains loopback-only;
  public exposure and production mutation are not opened.

- Telegram-first/operator-web policy for private/operator RC.
  Importance: very important policy. Gate: docs-only/local-only. Evidence:
  `research/amn2/phase-7-telegram-first-operator-web-policy-2026-06-20.md`.
  Result: closed as
  `completed-docs-only-telegram-first-operator-web-policy`. Users are served
  through Telegram; web/admin remains operator-only by VPS IP plus loopback/SSH
  tunnel or equivalent private access. Public web-admin exposure, DNS domain,
  trusted public TLS and reverse proxy are not required for private/operator
  RC. Candidate future `P7-C008` Telegram user-flow smoke remains inactive
  until an exact named live Telegram gate is opened.

- `P7-C008a` Telegram token reconciliation and user-flow smoke for AMN2
  `5501295`. Importance: critical/user-facing. Gate: exact named secret/env
  live gate. Evidence:
  `research/amn2/phase-7-telegram-token-reconciliation-user-flow-smoke-5501295-2026-06-20.md`.
  Result: completed as `completed-getme-dispatcher-surface-no-send`. The
  earlier `P7-C008` invalid-token attempt is retained as historical evidence
  and resolved by this gate. The token was updated through operator-secret
  handoff with rollback copy and no token output, Telegram `getMe` passed, and
  non-polling bot/user-flow surface construction passed. No polling, live send,
  profile/media mutation, config payload output, write execution, public
  exposure, restore/import/reboot, provider mutation or secret-bearing output
  was performed.

- `P7-C004c` Direct clean installer execution for AMN2 `5501295`.
  Importance: critical destructive gate. Gate: explicitly opened by the
  operator for disposable VPS `89.185.80.166`; destructive clean install from
  verified `5501295` package, no provider rebuild/reboot/restore/import/public
  exposure/config delivery/Local Agent/Telegram action. Evidence:
  `research/amn2/phase-7-direct-clean-installer-5501295-2026-06-20.md`.
  Result: closed as `completed-direct-clean-install-5501295-loopback-smoke`.
  Current `/opt/amn2` was quarantined, clean `/opt/amn2` was installed from
  `5501295`, DB init passed, loopback web returned `/login=200`, API loopback
  smoke returned `VPS verdict: pass`, and public probes stayed closed. This
  supersedes the earlier `b121865` clean install + `5501295` overlay as the
  clean-installer RC evidence for the current head.

- `P7-C004d + P7-C006b` Post-direct-clean loopback admin login verification
  and backup-only create+verify for AMN2 `5501295`.
  Importance: critical + critical backup evidence. Gate: explicitly opened by
  the operator for disposable VPS `89.185.80.166`; no restore/import/reboot,
  remote backup download, provider mutation, public exposure, config delivery,
  write execution, Local Agent mutation or Telegram action. Evidence:
  `research/amn2/phase-7-post-direct-clean-login-backup-5501295-2026-06-20.md`.
  Result: closed as `completed-login-verified-backup-create-verify`. Loopback
  admin login passed after the direct clean installer RC. Backup create and
  verify passed for the clean `5501295` state; the encrypted artifact stayed on
  the VPS under
  `/opt/amn2/backups/p7-c006b-post-direct-clean-5501295-20260620T061005Z`,
  sha256
  `f8e0591db75e8ec9ce58f4fa9d71972d577e1ec103194d1943a626aa9b156b97`.
  External probes stayed closed.

- Final RC freeze/status pass for AMN2 `5501295`.
  Importance: critical status hygiene. Gate: docs-only/local-only; no live
  action. Evidence:
  `research/amn2/phase-7-final-rc-freeze-status-5501295-2026-06-20.md`.
  Result: closed as `completed-rc-ready-paused-state-no-live-action`. Phase 7
  is frozen as `rc_ready_paused_private_operator_lane`: latest
  VPS-smoked/package head and current VPS source overlay are `5501295`; web
  remains loopback-only; public exposure is not opened;
  `VPS_APPLY_ENABLED=false`; current-state backup evidence exists; known-device
  private config handoff is complete; `P7-C007` is deferred for private RC.
  Remaining approved work is residual `P7-C006`
  restore/import/download/reboot/DR/provider-restore scope only, plus
  watch-only intake.

- `P7-C007` Telegram identity/profile/media decision for private RC.
  Importance: critical gated decision. Gate: docs-only decision; no Telegram
  token use/profile/media mutation. Evidence:
  `research/amn2/phase-7-telegram-defer-private-rc-2026-06-20.md`.
  Result: closed as
  `completed-deferred-not-required-for-private-rc-no-telegram-action`. Telegram
  identity/profile/media mutation is deferred and is not required for
  private/operator RC readiness. No Telegram token use, Telegram API call, live
  bot send, profile/media mutation, media upload, credential handoff, live
  VPS/SSH command or secret-bearing output was performed. Future Telegram
  identity/profile/media work remains exact named gate only.

- `P7-C006` Current-state backup-only evidence gate for AMN2 `5501295`.
  Importance: critical gated. Gate: backup-only create+verify, explicitly
  opened by the operator for disposable VPS `89.185.80.166`; no restore, import,
  reboot, provider mutation or remote backup download. Evidence:
  `research/amn2/phase-7-current-state-backup-only-5501295-2026-06-20.md`.
  Result: closed as
  `completed-current-state-backup-only-create-verify-no-restore-import-reboot`.
  Source overlay matched `5501295`; backup create and verify passed; artifact
  stayed on the VPS under
  `/opt/amn2/backups/p7-c006-current-state-5501295-20260620T050111Z`, basename
  `amneziya-backup-20260620T050141Z.tar.enc`, bytes `218552`, sha256
  `1412e6791ba03e0f955d46e988357274a413d0afc96a2e72c1b6077624554bb2`, mode
  `600`. External probes stayed closed. No restore/import/reboot, provider
  mutation, remote backup download, service restart, public exposure, config
  delivery, write execution, Local Agent mutation, Telegram action or
  secret-bearing output was performed.

- `P7-C006a + watch-only status hygiene` Provider backup restore-point
  confirmation and watch-only status hygiene.
  Importance: important + watch-only. Gate: docs-only/provider-console
  evidence + watch-only. Evidence:
  `research/amn2/phase-7-provider-backup-restore-point-watch-hygiene-2026-06-20.md`.
  Result: closed as
  `completed-provider-console-evidence-inconclusive-watch-hygiene-no-mutation`.
  The operator-provided provider-console screenshot for VPS `89.185.80.166`
  showed backup creation success, move-to-internal-storage failure and backup
  deletion success on 2026-06-15. Provider restore-point availability is not
  confirmed and must not be treated as a restore prerequisite. No provider
  mutation, restore/import/reboot, remote backup download, live VPS/SSH command
  or secret-bearing output was performed. Watch-only release signals remain
  `amnezia-client 4.8.19.0` and `amneziawg-android 2.0.1`.

- `P7-I001 + P7-M001` Current-head release-candidate package/preflight for
  `b121865` plus known-good snapshot/runbook alignment.
  Importance: very important + important. Gate: local-only/package-preflight.
  Evidence:
  `research/amn2/phase-7-current-head-package-preflight-b121865-2026-06-14.md`.
  Result: built `dist/amn2-vps-update-and-smoke-kit-b121865.zip`, sha256
  `364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849`, from
  source zip sha256
  `D0FB561D5A12C3B2C095521C3B44923B001F49C8E94CA5C13DB1E811ABB17647`.
  AMN2 full suite: `724 passed, 1 StarletteDeprecationWarning`. AMN3 package
  tests: `4 tests OK`. At that step `0de7a77` remained the known-good VPS
  baseline; this was later superseded by `P7-C001`.

- `P7-I002 + P7-M002 + P7-I003` Clean installer RC acceptance checklist,
  package asset/runbook path verification integration and installer
  secret/input contract hardening.
  Importance: very important + important + very important. Gate:
  local-only/docs/tests/security/package-preflight. Evidence:
  `research/amn2/phase-7-clean-installer-rc-checklist-security-contract-2026-06-14.md`.
  Result: AMN2 fresh installer manifest now exposes
  `clean_installer_rc_acceptance`, package/runbook path verification for the
  `b121865` package, package-local helper default bindings and
  `secret_input_contract`. Focused RED showed `6 failed, 10 passed`; focused
  GREEN returned `16 passed`; expanded suite returned `52 passed`; regression
  verification returned `17 passed, 1 StarletteDeprecationWarning`.
  Final AMN2 full suite returned `727 passed, 1 StarletteDeprecationWarning`.

- `P7-M003 + P7-N002 + P7-S002` Multi-instance/IPAM model incorporation,
  API/docs taxonomy RC drift check and release notes skeleton.
  Importance: important + normal + simple. Gate: local-only/docs/tests.
  Evidence:
  `research/amn2/phase-7-multi-instance-taxonomy-release-notes-2026-06-14.md`.
  Result: AMN2 fresh installer manifest now exposes
  `multi_instance_ipam_rc_decision`, rendered plans include
  `multi-instance-ipam-rc-decision`, integration status exposes
  `api_docs_taxonomy_rc_drift_check`, and AMN2 docs include
  `docs/RELEASE_NOTES_RC_SKELETON.ru.md` without declaring a public release.
  Verification: RED `3 failed, 15 passed, 1 StarletteDeprecationWarning`,
  focused GREEN `18 passed, 1 StarletteDeprecationWarning`, expanded
  `56 passed, 1 StarletteDeprecationWarning`, full AMN2 suite `728 passed, 1
  StarletteDeprecationWarning`.

- `P7-N001 + P7-N003 + P7-X001` Automation intake for Phase 7, client
  compatibility watch refresh and operator copy polish for clean installer.
  Importance: normal + normal + cosmetic. Gate: local-only/docs/tests/watch-only.
  Evidence:
  `research/amn2/phase-7-automation-client-watch-copy-polish-2026-06-14.md`.
  Result: weekly upstream-refresh automations remain intake-only signals,
  AMN2 exposes `CLIENT_COMPATIBILITY_WATCH` through integration status, config
  delivery remains disabled, and clean installer prompts are Russian-first while
  stable answer values remain unchanged. Verification: RED import error for the
  new watch contract, focused GREEN `10 passed, 1 StarletteDeprecationWarning`,
  expanded `68 passed, 1 StarletteDeprecationWarning`, full AMN2 suite
  `729 passed, 1 StarletteDeprecationWarning`.

- `P7-S001` Next-chat and status hygiene.
  Importance: simple. Gate: docs-only. Evidence:
  `research/amn2/phase-7-next-chat-status-hygiene-2026-06-14.md`.
  Result: Phase 7 handoff/status/backlog/context/transfer docs now show that
  the default local-only RC readiness queue is closed. Active Phase 7 work is
  limited to named critical gates and watch-only monitoring.

- `P7-C001` Live package/apply/smoke gate for current AMN2 head.
  Importance: critical gated. Gate: live VPS package/apply/smoke, explicitly
  opened by the operator for `b121865` on disposable VPS `89.185.80.166`.
  Evidence:
  `research/amn2/phase-7-live-update-smoke-b121865-2026-06-14.md`.
  Result: package
  `dist/amn2-vps-update-and-smoke-kit-b121865.zip`, sha256
  `364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849`, was
  uploaded, checksum-verified and applied as a source overlay. Remote source
  commit is `b121865f488821f6fc471c9529fb26e5d7992515`;
  `source_update_status=passed`; loopback API smoke returned `VPS verdict:
  pass`, auth/listener/audit passed, negative auth checks were `401/403/401`,
  API listener was loopback-only on `127.0.0.1:3040`, web login returned `200`
  on loopback `127.0.0.1:3030`, and external probes to `3030`, `3040`, `80`
  and `443` returned `000`. No public exposure, config delivery, write API
  production opening, backup/import/reboot, destructive action, Telegram
  mutation, secret publication or upstream/GPL code copy was performed.

- `P7-C002 + P7-C003 + P7-C005` public/config/write preflight for `b121865`.
  Importance: critical gated. Gate: public/config/write, explicitly opened by
  the operator for disposable VPS `89.185.80.166`. Evidence:
  `research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md`.
  Result: closed as `blocked-by-preconditions`. Source overlay was
  `b121865f488821f6fc471c9529fb26e5d7992515`; web remained loopback-only on
  `127.0.0.1:3030` with loopback `/login` returning `200`; external probes to
  `3030`, `3040`, `80` and `443` returned `000`. Safe env summary showed
  `WEB_ADMIN_USERNAME=missing`, SMTP config missing, `VPS_APPLY_ENABLED=false`
  and `LOCAL_AGENT_ENABLED=false`. Public API route inventory was read-only and
  `write_api_route_count=0`. No public exposure, config delivery, write route,
  Local Agent mutation, live peer/user mutation or secret-bearing output was
  performed.

- `P7-I004` Public/config/write prerequisite split.
  Importance: very important. Gate: local-only/docs/tests. Evidence:
  `research/amn2/phase-7-public-config-write-prerequisite-split-2026-06-14.md`.
  Result: AMN2 fresh installer manifest and `/api/integration/status` now expose
  `public_config_write_prerequisite_split` with schema
  `public-config-write-prerequisite-split.v1`, status
  `blocked_by_preconditions`, three readiness tracks for `P7-C002`, `P7-C003`
  and `P7-C005`, and blocked actions for public listener changes, config
  artifact output, write route enablement, `VPS_APPLY_ENABLED=true`, Local
  Agent mutation and live peer/user mutation. Verification: RED `3 failed, 19
  passed, 1 StarletteDeprecationWarning`; focused GREEN `22 passed, 1
  StarletteDeprecationWarning`; expanded `28 passed, 1
  StarletteDeprecationWarning`.

- `P7-I005` Public exposure readiness/design.
  Importance: very important. Gate: local-only/docs/tests. Evidence:
  `research/amn2/phase-7-public-exposure-readiness-design-2026-06-14.md`.
  Result: AMN2 fresh installer manifest and `/api/integration/status` now expose
  `public_exposure_readiness_design` with schema
  `public-exposure-readiness-design.v1`, status `readiness_design_ready`, target
  gate `P7-C002`, live exposure disabled and checklists for admin credential
  contract, domain/TLS/reverse-proxy plan, firewall/listener plan, external
  probe matrix and rollback-to-loopback. Verification: RED `3 failed, 21
  passed, 1 StarletteDeprecationWarning`; focused GREEN `24 passed, 1
  StarletteDeprecationWarning`; expanded `30 passed, 1
  StarletteDeprecationWarning`.

- `P7-I006` Config delivery channel readiness.
  Importance: very important. Gate: local-only/docs/tests. Evidence:
  `research/amn2/phase-7-config-delivery-channel-readiness-2026-06-14.md`.
  Result: AMN2 fresh installer manifest and `/api/integration/status` now expose
  `config_delivery_channel_readiness` with schema
  `config-delivery-channel-readiness.v1`, status `readiness_design_ready`,
  target gate `P7-C003`, live delivery disabled and checklists for
  SMTP/operator-local channel decision, secret-safe evidence protocol, client
  import matrix, one-time delivery policy and delivery revocation story.
  API/rendered-plan views redact exact forbidden evidence marker names to
  count/policy while the local manifest keeps the full validation contract.
  Verification: RED `3 failed, 23 passed, 1 StarletteDeprecationWarning`;
  focused GREEN `26 passed, 1 StarletteDeprecationWarning`; expanded
  `32 passed, 1 StarletteDeprecationWarning`; full AMN2 suite `735 passed, 1
  StarletteDeprecationWarning`.

- `P7-I007` Write API scope/implementation decision.
  Importance: very important. Gate: local-only/docs/tests. Evidence:
  `research/amn2/phase-7-write-api-scope-decision-2026-06-14.md`.
  Result: AMN2 fresh installer manifest and `/api/integration/status` now expose
  `write_api_scope_decision` with schema `write-api-scope-decision.v1`, status
  `decision_ready`, target gate `P7-C005` and selected RC policy
  `keep_public_api_read_only_for_rc`. Write API, public write routes, Local
  Agent mutation and production peer/user mutation remain disabled; deferred
  options require `P7-C005`. Verification: RED `3 failed, 25 passed, 1
  StarletteDeprecationWarning`; focused GREEN `28 passed, 1
  StarletteDeprecationWarning`; expanded `34 passed, 1
  StarletteDeprecationWarning`; full AMN2 suite `737 passed, 1
  StarletteDeprecationWarning`.

- `P7-I008` Backup/restore/import prerequisite checklist.
  Importance: very important. Gate: local-only/docs/tests. Evidence:
  `research/amn2/phase-7-backup-restore-import-readiness-2026-06-14.md`.
  Result: AMN2 fresh installer manifest and `/api/integration/status` now expose
  `backup_restore_import_readiness` with schema
  `backup-restore-import-prerequisite-checklist.v1`, status
  `readiness_checklist_ready`, target gate `P7-C006`, live backup disabled,
  restore apply disabled, archive import disabled and reboot disabled. Required
  checklists cover backup scope, encryption/retention policy, restore preview
  safety, import source validation and disaster-recovery drill planning.
  Verification: RED `3 failed, 27 passed, 1 StarletteDeprecationWarning`;
  focused GREEN `30 passed, 1 StarletteDeprecationWarning`; expanded
  `36 passed, 1 StarletteDeprecationWarning`; full AMN2 suite `739 passed, 1
  StarletteDeprecationWarning`.

- `P7-I009` Telegram identity/profile/media prerequisite checklist.
  Importance: very important. Gate: local-only/docs/tests. Evidence:
  `research/amn2/phase-7-telegram-identity-readiness-2026-06-14.md`.
  Result: AMN2 fresh installer manifest and `/api/integration/status` now expose
  `telegram_identity_readiness` with schema
  `telegram-identity-profile-media-prerequisite-checklist.v1`, status
  `readiness_checklist_ready`, target gate `P7-C007`, Telegram API disabled,
  token use disabled, profile mutation disabled, media mutation disabled and
  live bot send disabled. Required checklists cover identity scope decision,
  credential handoff/storage policy, profile/media asset planning, operator
  preview/rollback and post-mutation relock audit. Verification: RED `3 failed,
  29 passed, 1 StarletteDeprecationWarning`; focused GREEN `32 passed, 1
  StarletteDeprecationWarning`; expanded `38 passed, 1
  StarletteDeprecationWarning`; full AMN2 suite `741 passed, 1
  StarletteDeprecationWarning`.

- `P7-I010` Release candidate gate matrix consolidation.
  Importance: very important. Gate: local-only/docs/tests. Evidence:
  `research/amn2/phase-7-rc-gate-matrix-consolidation-2026-06-14.md`.
  Result: this plan now separates completed structural local-only work,
  active critical gates, watch-only intake and inactive proposals. The RC gate
  matrix below maps every remaining `P7-C002`...`P7-C007` gate to its readiness
  source, current blocker and allowed next action. No new live gate was opened.

- `P7-S003` Final RC handoff/status compression.
  Importance: simple. Gate: docs-only. Evidence:
  `research/amn2/phase-7-final-rc-handoff-compression-2026-06-14.md`.
  Result: `docs/NEXT_CHAT_AMN2_PHASE_7_RELEASE_CANDIDATE.ru.md` was compressed
  into a short handoff with current state, approved remaining plan, RC Gate
  Matrix summary, exact named gate policy and recommendation rhythm. No live
  action or new gate was opened.

- `P7-N004 + watch-only automation/client refresh intake + named-gate dry
  checklist review + final RC notes polish`.
  Importance: normal + normal + normal + cosmetic/simple. Gate:
  local-only/docs/watch-only. Evidence:
  `research/amn2/phase-7-evidence-watch-drycheck-rcnotes-2026-06-14.md`.
  Result: added `docs/AMN2_PHASE_7_EVIDENCE_INDEX.ru.md`, recorded watch-only
  automation intake status, added named-gate dry checklist review and polished
  AMN2 RC notes skeleton so `b121865` is the latest known-good
  VPS-smoked/package baseline while public/config/write/backup/destructive and
  Telegram gates remain unopened. No live action or new gate was opened.

- `P7-S004 + watch-only intake check + operator named-gate menu review`.
  Importance: simple + normal + normal. Gate: docs-only/watch-only. Evidence:
  `research/amn2/phase-7-final-freeze-watch-menu-2026-06-14.md`.
  Result: Phase 7 local-only expansion is frozen before any named gate. The
  evidence index and next-chat handoff now show the watch-only intake check and
  an operator named-gate menu for `P7-C002`...`P7-C007`. No live action or new
  gate was opened.

- `P7-C002` Public exposure gate pre-cutover for `b121865`.
  Importance: critical gated. Gate: public exposure, explicitly opened by the
  operator for disposable VPS `89.185.80.166`. Evidence:
  `research/amn2/phase-7-public-exposure-gate-precutover-b121865-2026-06-14.md`.
  Result: closed as `blocked-by-preconditions`. Source overlay was
  `b121865f488821f6fc471c9529fb26e5d7992515`; web stayed loopback-only on
  `127.0.0.1:3030`; external probes to `3030`, `3040`, `80` and `443` returned
  `000`; reverse proxy binaries/services were absent or inactive; `ufw` was
  inactive; `WEB_ADMIN_USERNAME` was missing; public domain/base URL was
  missing; `VPS_APPLY_ENABLED=false`; `LOCAL_AGENT_ENABLED=false`. No reverse
  proxy, TLS, firewall, public listener or public API change was applied.

- `P7-C002a` Public exposure admin/domain prerequisite for `b121865`.
  Importance: critical gated prerequisite. Gate: live `.env` admin/domain
  prerequisite, explicitly opened by the operator for disposable VPS
  `89.185.80.166`. Evidence:
  `research/amn2/phase-7-public-exposure-admin-domain-prereq-b121865-2026-06-14.md`.
  Result: updated only `.env` admin/domain fields. Post-mutation safe flags
  show `WEB_ADMIN_USERNAME=present`, `WEB_ADMIN_PASSWORD_HASH=present`,
  `PUBLIC_BASE_URL=present`, `PUBLIC_DOMAIN=present`,
  `WEB_PUBLIC_BASE_URL=present`, `VPS_APPLY_ENABLED=false` and
  `LOCAL_AGENT_ENABLED=false`. Precondition verdict is
  `ready_for_operator_cutover_plan`, but `public_exposure_apply_allowed=false`.
  No service restart, reverse proxy, TLS, firewall, public listener or public
  API change was applied.

- `P7-C002b` Public exposure runtime reload and loopback login verification for
  `b121865`.
  Importance: critical gated prerequisite. Gate: live runtime reload and
  loopback login verification, explicitly opened by the operator for disposable
  VPS `89.185.80.166`. Evidence:
  `research/amn2/phase-7-public-exposure-runtime-login-verify-b121865-2026-06-18.md`.
  Result: closed as `runtime-login-verified-not-exposed`. Manual loopback
  runtime was restarted after `P7-C002a`; the first immediate HTTP probe hit a
  short pre-bind readiness window, then recovery showed web listening on
  `127.0.0.1:3030`. Final live login flow returned `GET /login=200`,
  `POST /login=303`, `Location=/` and dashboard `200`; password contract check
  matched submitted username/password to the live `.env` hash without printing
  secrets. External probes to `3030`, `3040`, `80` and `443` returned `000`.
  No reverse proxy, TLS, firewall, public listener, public API exposure, config
  delivery, write API, Local Agent mutation, backup/import/reboot, production
  peer/user mutation, destructive action, Telegram action, secret publication
  or upstream/GPL code copy was performed.

- `P7-C002` Public cutover guard for `b121865`.
  Importance: critical gated guard. Gate: public cutover, explicitly opened by
  the operator for disposable VPS `89.185.80.166`. Evidence:
  `research/amn2/phase-7-public-cutover-guard-b121865-2026-06-18.md`.
  Result: closed as `blocked-by-domain-tls-plan-not-exposed`. Guard saw source
  overlay `b121865f488821f6fc471c9529fb26e5d7992515`, web still
  loopback-only on `127.0.0.1:3030`, loopback login `200`, loopback root `303`,
  external probes to `3030`, `3040`, `80` and `443` all `000`, and
  `VPS_APPLY_ENABLED=false` / `LOCAL_AGENT_ENABLED=false`. Admin credentials
  and public URL fields were present, but `PUBLIC_BASE_URL`/`PUBLIC_DOMAIN`
  were IP-based; guard blocker was `trusted_tls_requires_dns_domain_not_ip`.
  Reverse proxy and certbot tooling were missing and no reverse proxy, TLS,
  firewall, public listener, package install, service restart, env mutation,
  public API exposure, config delivery, write API, Local Agent mutation,
  backup/import/reboot, production peer/user mutation, destructive action,
  Telegram action, secret publication or upstream/GPL code copy was performed.

- `P7-C002c + watch-only intake` DNS/domain/TLS prerequisite staging and
  watch-only upstream/client intake.
  Importance: critical gated prerequisite staging + normal watch-only. Gate:
  docs/watch-only; no live `P7-C002c` mutation. Evidence:
  `research/amn2/phase-7-dns-domain-tls-prereq-watch-intake-2026-06-18.md`.
  Result: closed as `watch-only-intake-complete-p7-c002c-input-required`.
  `P7-C002c` was not executed because an exact named live prerequisite gate and
  operator-provided DNS FQDN were not supplied. Local automation configs remain
  active; no new local automation output newer than the 2026-06-14 Phase 7
  intake evidence was found. Current official GitHub watch saw
  `amnezia-vpn/amnezia-client` release `4.8.19.0` from 2026-06-15 as a
  client-compatibility signal only. The later watch-only/status hygiene pass
  briefly recorded `amneziawg-android 2.0.0`, but the later watch-only
  correction restores current navigation to `amneziawg-android 2.0.1` latest.
  No live VPS command, SSH command, `.env` mutation, reverse proxy/TLS/firewall
  apply, public exposure, config delivery, write API, Local Agent mutation,
  backup/import/reboot, destructive action, Telegram action, secret publication
  or upstream/GPL code copy was performed.

- `P7-N005` Client compatibility watch refresh for Amnezia client `4.8.19.0`.
  Importance: normal. Gate: local-only/docs/tests/watch-only. Date:
  2026-06-18. Scope completed: activated from inactive proposal as part of the
  requested `P7-C002c + P7-N005` pair, refreshed AMN2 Phase 7 watch status
  around the official `amnezia-client` `4.8.19.0` signal and preserved the
  explicit boundary that this does not enable config delivery. Evidence:
  `research/amn2/phase-7-client-compatibility-watch-refresh-4-8-19-2026-06-18.md`.
  Result: closed as `p7-n005-complete-p7-c002c-input-required`.
  `P7-C002c` was not executed live because no exact named live prerequisite gate
  and no DNS FQDN were supplied.

- `P7-I011` IP-only exposure policy decision.
  Importance: very important. Gate: local-only/docs/status. Date: 2026-06-18.
  Scope completed: recorded the operator decision not to use a DNS domain for
  AMN2 and to keep the default access path as VPS IP + loopback web/admin over
  SSH tunnel. Evidence:
  `research/amn2/phase-7-ip-only-exposure-policy-decision-2026-06-18.md`.
  Result: closed as `completed-local-only-operator-declined-dns-domain`.
  `P7-C002c` DNS/domain/trusted TLS prerequisite branch is closed by operator
  policy. No live action was performed.

- `watch-only intake + status hygiene`.
  Importance: normal + simple. Gate: docs-only/watch-only. Date: 2026-06-18.
  Scope completed: refreshed current upstream/client watch pointers after the
  IP-only policy decision and corrected status/navigation so DNS/domain/TLS is
  not recommended as the default next path. Evidence:
  `research/amn2/phase-7-watch-only-intake-status-hygiene-2026-06-18.md`.
  Result: closed as `completed-watch-only-status-hygiene-no-live-action`.
  Current watch keeps `amnezia-client` `4.8.19.0` as a compatibility signal and
  was later corrected so current navigation keeps `amneziawg-android 2.0.1` as
  latest. No config delivery, public exposure, write API or live action was
  performed.

- `watch-only intake correction`.
  Importance: normal. Gate: docs-only/watch-only. Date: 2026-06-18. Scope
  completed: corrected the previous `amneziawg-android 2.0.0` watch wording;
  current official GitHub release-page observation keeps `amneziawg-android
  2.0.1` as latest. Evidence:
  `research/amn2/phase-7-watch-only-intake-correction-2026-06-18.md`.
  Result: closed as `completed-watch-only-correction-no-live-action`.
  No config delivery, public exposure, write API or live action was performed.

- `watch-only intake current signals`.
  Importance: normal. Gate: docs-only/watch-only. Date: 2026-06-18. Scope
  completed: refreshed current watch-only sources after the correction pass.
  Evidence:
  `research/amn2/phase-7-watch-only-intake-current-signals-2026-06-18.md`.
  Result: closed as `completed-watch-only-intake-current-signals-no-live-action`.
  Current signals remain `amnezia-client 4.8.19.0` and `amneziawg-android
  2.0.1`; PRVTPRO remains upstream idea source only and KYORESUAS remains API
  taxonomy signal only. No new AMN2 implementation task was created.

- `P7-C002e + watch-only` Public URL env reconciliation gate plus watch-only
  intake.
  Importance: important gated + normal. Gate: live `.env` mutation /
  docs-only/watch-only. Date: 2026-06-19. Scope completed: removed
  `PUBLIC_BASE_URL`, `PUBLIC_DOMAIN` and `WEB_PUBLIC_BASE_URL` from live `.env`
  on disposable VPS `89.185.80.166` after the `P7-I011` IP-only policy decision.
  Evidence:
  `research/amn2/phase-7-public-url-env-reconciliation-b121865-2026-06-19.md`.
  Result: closed as `completed-live-env-reconcile-not-exposed`. Rollback copy
  was created on VPS and must not be posted because it contains secrets. Runtime
  stayed loopback-only; external probes remained closed; no service restart,
  reverse proxy, TLS, firewall, public listener, config delivery or write API
  change was performed.

- `watch-only intake current signals`.
  Importance: normal. Gate: docs-only/watch-only. Date: 2026-06-19. Scope
  completed: refreshed current watch-only sources after `P7-C002e`. Evidence:
  `research/amn2/phase-7-watch-only-intake-current-signals-2026-06-19.md`.
  Result: closed as `completed-watch-only-intake-current-signals-no-live-action`.
  Current signals remain `amnezia-client 4.8.19.0` and `amneziawg-android
  2.0.1`; PRVTPRO remains upstream idea source only and KYORESUAS remains API
  taxonomy signal only. No new AMN2 implementation task was created.

- `P7-C002d` IP-only public exposure risk guard.
  Importance: critical gated guard. Gate: IP-only public exposure risk,
  explicitly opened by the operator for disposable VPS `89.185.80.166`. Date:
  2026-06-19. Evidence:
  `research/amn2/phase-7-ip-only-public-exposure-risk-guard-b121865-2026-06-19.md`.
  Result: closed as
  `blocked-pending-design-or-explicit-risk-acceptance-not-exposed`. Source
  overlay marker confirmed `b121865f488821f6fc471c9529fb26e5d7992515`; runtime
  stayed loopback-only on `127.0.0.1:3030`; public `3040/80/443` listeners were
  absent. Guard blockers: `ufw_inactive_for_public_exposure`,
  `no_reverse_proxy_binary_for_admin_exposure`,
  `ip_only_public_admin_has_no_trusted_dns_tls` and
  `public_admin_over_ip_requires_explicit_risk_acceptance`.
  `ip_only_public_apply_allowed=false`; no public exposure apply was performed.

- `P7-C003 + P7-C005` Config/write read-only preflight.
  Importance: critical gated readiness review. Gate: local/docs/read-only
  preflight, no config delivery and no write mutation. Date: 2026-06-19.
  Evidence:
  `research/amn2/phase-7-config-write-read-only-preflight-2026-06-19.md`.
  Result: closed as `completed-read-only-preflight-blocked-no-delivery-no-write`.
  At that time `P7-C003` was blocked by missing delivery-channel decision,
  missing SMTP config / attachment policy and no selected secret-safe
  operator-local delivery protocol. The later `P7-C003` operator-local guard
  selected `operator-local` as the current channel but left real delivery blocked
  pending target/private handoff. At that time `P7-C005` was still blocked by
  RC policy, prior `write_api_route_count=0`, `VPS_APPLY_ENABLED=false` and
  `LOCAL_AGENT_ENABLED=false`; this was later superseded by the 2026-06-20
  scoped write contour on `5501295`. No config artifact,
  SMTP/Telegram send, tokenized redeem, write route, install mutation, Local
  Agent mutation or peer/user mutation was performed.

- `P7-C003` Operator-local config delivery guard for `b121865`.
  Importance: critical gated guard. Gate: config delivery, channel
  `operator-local`, explicitly opened by the operator for disposable VPS
  `89.185.80.166`. Date: 2026-06-19. Evidence:
  `research/amn2/phase-7-config-delivery-operator-local-guard-b121865-2026-06-19.md`.
  Result: closed as
  `blocked-pending-target-and-private-handoff-no-delivery`. Source overlay marker
  confirmed `b121865f488821f6fc471c9529fb26e5d7992515`; loopback web returned
  `/login=200` and `/=303`; external probes to `3030`, `3040`, `80` and `443`
  returned `000`. Safe route inventory found five config-related web/admin
  routes and DB aggregates showed `users_count=1`, `devices_count=2`,
  `servers_count=1`. Delivery blockers: no selected target user/device, no
  selected private artifact destination, no confirmed one-time delivery and
  revocation policy, and no authorization to output config payloads in
  evidence/chat. `operator_local_delivery_apply_allowed=false`; no config
  delivery or secret output was performed.

- `P7-C003` Target inventory for operator-local handoff.
  Importance: critical gated guard support. Gate: config delivery, read-only
  target inventory. Date: 2026-06-19. Evidence:
  `research/amn2/phase-7-config-delivery-target-inventory-b121865-2026-06-19.md`.
  Result: closed as `completed-read-only-target-inventory-no-delivery`. Valid
  target pairs for the next handoff are `TARGET_USER_ID=1 TARGET_DEVICE_ID=1`
  and `TARGET_USER_ID=1 TARGET_DEVICE_ID=2`; both devices are active with
  `config_material_status=available` and `config_version=amneziawg_v2`. Runtime
  stayed loopback-only and external probes to `3030`, `3040`, `80` and `443`
  returned `000`. No config delivery or secret output was performed.

- `P7-C003` Target-specific operator-local private handoff for device 1.
  Importance: critical gated. Gate: config delivery, target-specific
  operator-local private handoff. Date: 2026-06-19. Evidence:
  `research/amn2/phase-7-config-delivery-private-handoff-device1-b121865-2026-06-19.md`.
  Result: closed as `completed-private-file-copied-secret-not-printed`.
  `TARGET_USER_ID=1` / `TARGET_DEVICE_ID=1` was rendered on the VPS to a
  root-only temp file, copied to the operator-selected local private destination
  outside the workspace and removed from the VPS. Remote/local metadata matched:
  `artifact_bytes=438`, sha256
  `7ca64dd57a7467c4817e846a11d56d861013921c1db3f6ac020f7ca355dfdb83`. No
  config payload or client secret was printed to chat/evidence.

- `P7-C003` Target-specific operator-local private handoff for device 2.
  Importance: critical gated. Gate: config delivery, target-specific
  operator-local private handoff. Date: 2026-06-19. Evidence:
  `research/amn2/phase-7-config-delivery-private-handoff-device2-b121865-2026-06-19.md`.
  Result: closed as `completed-private-file-copied-secret-not-printed`.
  `TARGET_USER_ID=1` / `TARGET_DEVICE_ID=2` was rendered on the VPS to a
  root-only temp file, copied to the operator-selected local private destination
  outside the workspace and removed from the VPS. Remote/local metadata matched:
  `artifact_bytes=438`, sha256
  `87b5a41c665b593b72740b00422416ef73dc0d7a58ca928ea52c6722c0e5cbb3`. No
  config payload or client secret was printed to chat/evidence. Together with
  device 1, both known active devices from the target inventory have completed
  private-file handoff.

- `P7-C005 + P7-C006 + P7-C007` Write/backup/Telegram read-only preflight.
  Importance: critical gated readiness review. Gate: local/docs/evidence
  read-only preflight, no write mutation, no backup/restore/import and no
  Telegram token/profile/media mutation. Date: 2026-06-19. Evidence:
  `research/amn2/phase-7-write-backup-telegram-read-only-preflight-2026-06-19.md`.
  Result: closed as `completed-read-only-preflight-no-mutation`.
  At that time `P7-C005` was still blocked by RC policy, public write routes
  disabled, `VPS_APPLY_ENABLED=false` and `LOCAL_AGENT_ENABLED=false`; this was
  later superseded by the 2026-06-20 scoped write contour on `5501295`.
  `P7-C006` remains blocked for live backup,
  restore apply, archive import, remote backup download and reboot until a
  separate exact gate. At that time `P7-C007` was blocked for Telegram
  token use, live bot send, profile/media mutation and media upload; it was
  later deferred as not required for private RC. No live action or
  secret-bearing output was performed.

- `P7-C006` Backup-only evidence gate.
  Importance: critical gated. Gate: backup-only evidence, explicitly opened by
  the operator for `b121865` on disposable VPS `89.185.80.166`; no restore,
  import, reboot or remote backup download. Date: 2026-06-19. Evidence:
  `research/amn2/phase-7-backup-only-evidence-b121865-2026-06-19.md`.
  Result: closed as
  `completed-backup-only-create-verify-no-restore-import-reboot`. First attempt
  failed because backup CLI required `APP_SECRET_KEY` in process env and SSH did
  not load `.env`; read-only diagnostic confirmed the CLI existed and skipped
  printing the forbidden-marker log. Retry loaded `APP_SECRET_KEY` only inside
  the remote Python process without printing it; backup create and verify passed.
  Artifact stayed on the VPS under `/opt/amn2/backups`, mode `600`, size
  `245860`, sha256
  `9947bf97b242e46d86cf7cbf41ed7ffb8cec8a9bae728a71f3095c86d50b73c9`. No backup
  contents, `.env`, `servers.yml`, DB rows, private keys, PSK, tokens or configs
  were printed.

- `P7-C004a` Destructive clean installer pre-cutover guard.
  Importance: critical gated. Gate: destructive pre-cutover guard, explicitly
  opened by the operator for `b121865` on disposable VPS `89.185.80.166`; no
  wipe/reinstall/apply. Date: 2026-06-19. Evidence:
  `research/amn2/phase-7-destructive-clean-installer-precutover-guard-b121865-2026-06-19.md`.
  Result: closed as `ready-for-final-destructive-stop-line-no-apply`. Local
  package/source checksums matched the `b121865` RC package, remote source
  overlay matched `b121865f488821f6fc471c9529fb26e5d7992515`, the `P7-C006`
  backup artifact was present with matching sha256, external probes stayed
  closed and `pre_cutover_blocker_count=0`. No wipe, reinstall, package apply,
  service restart, provider action, restore/import/reboot, public exposure,
  write API, Local Agent mutation, production peer/user mutation, Telegram
  action or secret-bearing output was performed.

- `P7-C004b` Destructive clean installer execution.
  Importance: critical gated. Gate: destructive clean installer execution,
  explicitly opened by the operator for `b121865` on disposable VPS
  `89.185.80.166`, with final destructive phrase entered in the PowerShell
  window. Date: 2026-06-19. Evidence:
  `research/amn2/phase-7-destructive-clean-installer-execution-b121865-2026-06-19.md`.
  Result: closed as `completed-clean-install-loopback-smoke`. The old
  `/opt/amn2` runtime path was moved to
  `/opt/amn2.pre-p7-c004b-20260619T173819Z`, clean `/opt/amn2` was installed
  from verified `b121865` package/source, `.env` and `servers.yml` were
  regenerated without printing secrets, DB initialization passed, loopback web
  returned `/login=200`, API loopback smoke returned `VPS verdict: pass`, and
  external probes to `3030`, `3040`, `80` and `443` stayed `000`. No provider
  rebuild, reboot, restore/import, remote backup download, public exposure,
  config delivery, write API, Local Agent mutation, production peer/user
  mutation, Telegram action or secret-bearing output was performed.

- `P7-C005 + P7-C006 + P7-C007` Post-clean write/backup/Telegram read-only
  rebaseline.
  Importance: critical gated readiness evidence. Gate: post-clean read-only
  rebaseline after `P7-C004b`, no write mutation, no backup create, no
  restore/import/reboot and no Telegram token/profile/media mutation. Date:
  2026-06-19. Evidence:
  `research/amn2/phase-7-post-clean-write-backup-telegram-read-only-rebaseline-b121865-2026-06-19.md`.
  Result: closed as `completed-post-clean-read-only-rebaseline-no-mutation`.
  The clean `b121865` install remained active, web stayed loopback-only on
  `127.0.0.1:3030`, public API `3040` and public `80/443` listeners were
  absent, and external probes stayed `000`. Public API route inventory returned
  `write_api_route_count=0`; backup CLI help probing was safe and created no
  backup; Telegram token presence was checked without token use/API call. No
  write API enablement, install mutation, backup/restore/import/reboot, remote
  backup download, service restart, public exposure, config delivery, Local
  Agent mutation, production peer/user mutation, Telegram action or
  secret-bearing output was performed.

- `P7-C005` Write API / install mutation gate.
  Importance: critical gated. Gate: write API / install mutation, explicitly
  opened by the operator for AMN2 `5501295` on disposable VPS `89.185.80.166`.
  Date: 2026-06-20. Evidence:
  `research/amn2/phase-7-write-install-mutation-contour-5501295-2026-06-20.md`.
  Result: closed as `completed-scoped-write-contour-smoked`. AMN2 branch
  `codex-vps-test-prep` was advanced and pushed to
  `55012958ff6b8338254f3f68dfe6779f4bc56f5d` (`Add P7 install write contour`).
  Local AMN2 full suite returned `726 passed, 1 StarletteDeprecationWarning`.
  Package `dist/amn2-vps-update-and-smoke-kit-5501295.zip` sha256
  `C03D26673AD79D9487A3ED34E9657E0DCA10EBC9BB601E429385091F1DFEF407` and source
  zip sha256 `DA7DA58E0FD8D778BD4A22471BBCD9038CC455ACD3C0538A38874215C81646D3`
  were verified. Live apply updated source overlay to `5501295`, loopback web
  restart passed, baseline API loopback smoke returned `VPS verdict: pass`,
  route inventory showed `POST /api/install/mutation-requests` with
  `write_api_route_count=1`, and scoped write route smoke passed:
  `server:read` token `403`, `install:write` token `202`,
  `write_route_status=recorded_blocked_by_vps_apply_disabled`,
  `audit_action=api_write`, `audit_safe=yes`, external probes closed. The route
  is audit-only while `VPS_APPLY_ENABLED=false`; it did not invoke an installer
  executor, package apply, service restart, public exposure, config delivery or
  Telegram action. No restore/import/reboot, Local Agent mutation,
  production peer/user mutation, public listener change or secret-bearing
  output was performed.

- Watch-only intake after critical preflights.
  Importance: watch-only. Gate: docs-only/watch-only. Date: 2026-06-19.
  Evidence:
  `research/amn2/phase-7-watch-only-intake-after-critical-preflights-2026-06-19.md`.
  Result: closed as
  `completed-watch-only-intake-after-critical-preflights-no-live-action`.
  No new local automation output, AMN2 implementation task, live gate, mutation
  or secret-bearing output was created. Known active `P7-C003` device handoffs
  are complete; `P7-C005` is now complete for the scoped write contour, while
  residual `P7-C006` scopes remain exact named gates only; `P7-C007` was later
  deferred as not required for private RC.

- Watch-only intake cycle closeout.
  Importance: watch-only. Gate: docs-only/watch-only. Date: 2026-06-19.
  Evidence:
  `research/amn2/phase-7-watch-only-intake-cycle-complete-2026-06-19.md`.
  Result: closed as `completed-watch-only-intake-cycle-complete-no-live-action`.
  Current observed client signals remain `amnezia-client 4.8.19.0` and
  `amneziawg-android 2.0.1`; PRVTPRO remains an upstream idea source only and
  KYORESUAS remains an API taxonomy signal only. No live gate, mutation,
  upstream/GPL code copy or new implementation task was created.

- `P7-S005 + P7-I012` Docs quality audit and IP-only env reconciliation plan.
  Importance: simple + very important. Gate: docs-only/status. Date:
  2026-06-18. Scope completed: audited recent Phase 7 docs/evidence changes,
  separated AMN3 workspace/evidence context from AMN2 source/package context,
  and added an inactive `P7-C002e` public URL env reconciliation proposal for
  the `.env` public URL fields left by `P7-C002a` after the later IP-only policy
  decision. Evidence:
  `research/amn2/phase-7-docs-quality-audit-ip-env-reconcile-2026-06-18.md`.
  Result: closed as `completed-docs-only-audit-with-inactive-reconcile-gate`.
  No live action or `.env` mutation was performed.

## RC Gate Matrix

Этот раздел является каноническим separation layer для Phase 7:

- completed local-only structural tasks live only in `Выполнено В Phase 7`;
- active work from the approved plan lives only in `Критичные Gated /
  Deferred` and `Watch-Only / Наблюдение`;
- candidate tasks live only in `Неактивные Структурные Предложения`;
- no candidate task becomes active without explicit operator consent.

| Gate | Readiness Source | Current Status | Allowed Next Action |
| --- | --- | --- | --- |
| `P7-C002` Public exposure | `P7-I005` readiness; pre-cutover evidence; `P7-C002a` admin/domain prerequisite evidence; `P7-C002b` runtime/login verification evidence; public cutover guard evidence; `P7-I011` IP-only policy; `P7-I012` env reconciliation plan; `P7-C002e` env reconciliation evidence; `P7-C002d` IP-only risk guard evidence; Telegram-first/operator-web policy | deferred/not required for private/operator RC; users are served through Telegram, operator web/admin remains VPS IP + loopback/SSH tunnel; public URL fields from `P7-C002a` were removed in `P7-C002e`; `P7-C002d` blocked IP-only exposure by four risk blockers | keep operator-only/watch-only; any future public web exposure requires a new exact risk-acceptance/design gate |
| `P7-C003` Config delivery | `P7-I006` config delivery channel readiness; 2026-06-19 config/write read-only preflight; 2026-06-19 operator-local guard evidence; 2026-06-19 target inventory; 2026-06-19 device 1 and device 2 private handoffs | complete for known active devices: `user_id=1/device_id=1` and `user_id=1/device_id=2` private handoffs completed without payload output; resend/revocation, SMTP/Telegram delivery, public/self-service delivery and new targets remain separate exact gates | no default next action; exact named gate only for resend/revocation/channel/new-target work |
| `P7-C004` Destructive clean installer execution | Phase 6 destructive checklist boundary; 2026-06-19 `P7-C004a` pre-cutover guard; 2026-06-19 `P7-C004b` execution evidence | completed for `b121865`: clean `/opt/amn2` install applied on disposable VPS, loopback web healthy, API loopback smoke passed, external probes closed; old runtime is root-only quarantined | no default next action; future provider rebuild, another clean install, restore/import or quarantine cleanup requires a new exact named gate |
| `P7-C005` Write API / install mutation | `P7-I007` write API scope decision; 2026-06-19 config/write read-only preflight; 2026-06-19 write/backup/Telegram read-only preflight; 2026-06-19 post-clean rebaseline; 2026-06-20 scoped write contour evidence | completed for scoped install-mutation request contour on `5501295`: `POST /api/install/mutation-requests` requires `install:write`, records safe `api_write`, returns `recorded_blocked_by_vps_apply_disabled` while `VPS_APPLY_ENABLED=false`, and does not invoke installer/apply/restart/public/config/Telegram actions | no default next action; future actual installer runner or broader write routes require a new exact named gate |
| `P7-C006` Backup/restore/import | `P7-I008` backup/restore/import readiness; 2026-06-19 write/backup/Telegram read-only preflight; 2026-06-19 backup-only evidence; 2026-06-19 post-clean rebaseline; 2026-06-20 `P7-C006a` provider-console evidence; 2026-06-20 current-state backup-only evidence for `5501295` | current-state backup create+verify complete for `5501295`; artifact stayed on VPS and was not downloaded; provider restore point not confirmed by screenshot evidence; restore apply, archive import, remote backup download, reboot, disaster-recovery drill and destructive migration remain blocked | exact named restore/import/download/reboot/drill gate only; fresh provider restore-point proof required before provider restore use |
| `P7-C007` Telegram identity/profile/media | `P7-I009` Telegram readiness checklist; 2026-06-19 write/backup/Telegram read-only preflight; 2026-06-19 post-clean rebaseline; 2026-06-20 private RC decision | deferred/not required for private RC; no Telegram token use/API call, live bot send, profile/media mutation, media upload or credential handoff performed | no default next action; future Telegram identity/profile/media work would require a new exact named Telegram gate |

## Закрыто / Не Следующий Gate

- `P7-C002` Public exposure gate.
  Importance: critical gated. Carried from Phase 6 `P6-C001`. Gate: public
  exposure. Covers domain, HTTPS, reverse proxy, public web/admin, public API,
  firewall/listener changes and public docs/OpenAPI publication. Current
  status after the 2026-06-18 public cutover guard, `P7-C002c` staging,
  `P7-I011` policy decision, 2026-06-19 `P7-C002d` risk guard and the
  2026-06-20 Telegram-first/operator-web policy:
  runtime/login is verified on loopback, web is still loopback-only, public
  `3040/80/443` listeners are absent and no reverse proxy/TLS/firewall/listener
  apply has happened. The trusted DNS-domain/TLS branch is closed because the
  operator chose IP-only AMN2 operation, and public web/admin is not required
  for private/operator RC because users are served through Telegram.
  `P7-C002d` then blocked IP-only public exposure because UFW is inactive, no
  reverse proxy binary is present, IP-only public admin has no trusted DNS/TLS
  path and explicit risk acceptance would be required. Public URL fields added
  by `P7-C002a` were removed in `P7-C002e`; readiness checklist exists in
  `P7-I005`. Default: keep operator-only/watch-only.

- `P7-C003` Config delivery gate.
  Importance: critical gated. Carried from Phase 6 `P6-C002`. Gate: config
  delivery. Covers `.conf`, QR, `vpn://`, tokenized public redeem, Telegram real
  config send and self-service download. Current status after 2026-06-19
  operator-local guard: channel is selected as `operator-local`, SMTP config is
  missing and email config attachments are unset, but actual delivery remains
  blocked until the operator selects one valid target pair
  (`TARGET_USER_ID=1 TARGET_DEVICE_ID=1` or `TARGET_USER_ID=1 TARGET_DEVICE_ID=2`),
  private artifact destination and one-time delivery/revocation policy. No
  config payload output is authorized in evidence/chat. Readiness checklist
  exists in `P7-I006`. `TARGET_USER_ID=1 TARGET_DEVICE_ID=1` and
  `TARGET_USER_ID=1 TARGET_DEVICE_ID=2` private handoffs are now complete;
  resend/revocation, SMTP/Telegram delivery, public/self-service links and new
  target devices remain separate exact gates. Default: no next action.

- `P7-C004` Destructive clean installer execution gate.
  Importance: critical gated. Carried from Phase 6 `P6-C007` and earlier
  `VPS-REBUILD-001`. Gate: destructive. Covers wipe, rebuild, reinstall,
  cleanup and provider-side destructive actions. `P7-C004a` pre-cutover guard
  completed with blocker count `0`; `P7-C004b` then completed clean install
  from verified `b121865` package/source, DB init, loopback web and API
  loopback smoke. Default: no next action. Any future provider rebuild, another
  clean install, restore/import or quarantine cleanup remains a separate exact
  named gate.

## Критичные Gated / Deferred

- `P7-C006` Backup/restore/import gate.
  Importance: critical gated. Carried from Phase 6 `P6-C004`. Gate:
  backup/restore/import. Covers encrypted backup, restore preview/apply,
  archive import and disaster recovery drill. Readiness checklist now exists in
  `P7-I008`; backup-only create+verify passed in the 2026-06-19 exact gate.
  The post-clean rebaseline kept restore/import/download/reboot disabled before
  the later `5501295` current-state backup-only gate. `P7-C006a`
  provider-console evidence was completed
  on 2026-06-20 as inconclusive: the screenshot shows backup creation success,
  move failure and backup deletion success, so no available provider restore
  point is confirmed. A fresh current-state backup-only create+verify for
  `5501295` passed on 2026-06-20 and the artifact stayed on the VPS. Restore
  apply, archive import, remote backup download, reboot, disaster-recovery
  drill, destructive migration and any provider restore use remain disabled
  until separate exact gates.

## Очень Важные

## Важные

## Нормальные

## Простые

## Косметические

## Watch-Only / Наблюдение

- Amnezia/DefaultVPN/AmneziaWG client releases.
  Importance: watch-only. Gate: watch-only. Use only as client compatibility
  signals.

- PRVTPRO/KYORESUAS upstream changes.
  Importance: watch-only/research. Gate: GPL/upstream-copy forbidden where
  applicable. Use only ideas/signals/links unless a local AMN2 candidate is
  explicitly accepted.

## Рекомендованный Следующий Шаг

```text
Локальная очередь Phase 7 закрыта. P7-C001, P7-C002, P7-C003, P7-C004 и
P7-C005 закрыты в рамках их текущих Phase 7 scopes. Current AMN2
VPS-smoked/package head: 5501295 Add P7 install write contour. Current
disposable VPS: 89.185.80.166, source overlay 5501295, web loopback-only,
external probes closed.
User-facing RC policy is Telegram-first. Operator web/admin policy is VPS IP
plus loopback/SSH tunnel; public web-admin/domain/TLS/reverse proxy is not
required for private/operator RC.

Утвержденный оставшийся план:
- residual P7-C006 Backup/restore/import scopes: exact named gate only
  для restore apply, archive import, remote backup download, reboot,
  disaster-recovery drill, destructive migration или provider restore use;
- P7-C008/P7-C008a Telegram user-flow smoke: completed after token
  reconciliation; further Telegram actions require a new exact named gate,
  especially live send, polling, config payload delivery or identity/profile
  mutation;
- watch-only intake, если не открываем live/mutation gate.

Новые local-only задачи можно выводить только как структурные предложения, не
как текущие активные задачи.
```

Latest watch-only intake after critical preflights is closed as
`completed-watch-only-intake-after-critical-preflights-no-live-action`.
Latest watch-only intake cycle is closed as
`completed-watch-only-intake-cycle-complete-no-live-action`.

## Ритм Рекомендаций

После каждой закрытой задачи:

- удалять ее из активного плана;
- выводить полный оставшийся план без нее;
- давать варианты следующего шага как одиночные, парные, тройные, четверные и
  более крупные bundles, если они связны и безопасны;
- указывать важность и gate для каждого варианта;
- разделять `утвержденный оставшийся план` и `новые структурные предложения`;
- отдельно предлагать структурные решения, если работа показала, что live gate
  блокируется отсутствующими prerequisite, отсутствующей implementation surface
  или небезопасно широким combined scope. Такие предложения оформлять как
  candidate tasks с важностью и gate: readiness split, prerequisite checklist,
  implementation decision, evidence-hygiene slice и похожие;
- не добавлять новые candidate tasks в активный план без явного согласия
  оператора.

## Неактивные Структурные Предложения

Эти пункты не входят в текущий утвержденный план. Их можно активировать только
после явного согласия оператора.

Одиночное предложение:

```text
P7-C008 Telegram user-flow smoke gate.
Importance: critical/user-facing.
Gate: exact named live Telegram gate.
Status: completed after P7-C008a token reconciliation.
Scope completed: Telegram `getMe` and non-polling bot/user-flow surface
construction without Telegram identity/profile/media mutation, live send,
public web exposure, write execution, restore/import/reboot, provider mutation
or secret-bearing evidence.

P7-C008a Telegram token reconciliation gate.
Importance: critical/user-facing prerequisite.
Gate: exact named secret/env live gate.
Status: completed.
Scope completed: operator-secret handoff for Telegram bot token, safe VPS
`.env` update with rollback copy, Telegram `getMe`, and non-polling P7-C008
smoke. No profile/media mutation, live send, config payload output, public
exposure, write execution, restore/import/reboot or provider mutation.
```

`P7-C002d` был активирован оператором и закрыт как
`blocked-pending-design-or-explicit-risk-acceptance-not-exposed`.

Парное предложение:

```text
No paired local-only proposal currently needed.
```

Тройное предложение:

```text
No triple local-only proposal currently needed.
```

Четверное и более крупное предложение:

```text
No larger local-only bundle currently needed; next substantive work is an exact named gate or watch-only intake.
```

## Требования К Доступу

Для обычной работы Phase 7 дополнительный доступ не нужен.

Просить оператора о доступе только если задача явно требует:

- VPS/SSH/PowerShell access for `P7-C001` or `P7-C004`;
- provider console access for destructive rebuild/reinstall;
- IP-only public exposure risk acceptance for any future post-`P7-C002d`
  public exposure design gate;
- payment provider credentials for commercial/payment work;
- Telegram token/profile access for any future Telegram exact gate.

## Stop Lines

Немедленно остановиться и запросить named gate, если задача требует:

- run SSH or live VPS commands;
- upload/apply a package to VPS;
- stop/restart/deploy services;
- open public `3030`, `3040`, `80`, `443`, domain, HTTPS or reverse proxy;
- emit `.conf`, QR, `vpn://`, config body or client secret;
- enable write API, Local Agent mutation, backup/import/reboot or peer/user
  mutation;
- delete, wipe, rebuild or reinstall a VPS;
- use Telegram tokens, live bot send or Telegram identity/profile mutation;
- publish secret-bearing evidence;
- copy upstream/GPL implementation code.
