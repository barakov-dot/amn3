# Следующий чат: AMN2 Phase 7 Release Candidate Readiness

Дата: 2026-06-20.

## Короткий Старт

```text
Продолжаем AMN2 Phase 7.

Phase 7: Release Candidate Readiness / Clean Installer RC.
Status: pre-release / release-candidate readiness.
Default lane: local-only/docs/tests/security/package-preflight.

Это не public launch и не production mutation lane.

Рабочая папка:
C:\Users\SooL\Documents\VPS-OPS-LAB

Источник правды:
- Current workspace/evidence repo: barakov-dot/amn3, branch master, head
  ec811cf Prepare Phase 7 transition.
- AMN2 package/source repo: barakov-dot/amn2, branch codex-vps-test-prep.
- AMN2 current/VPS-smoked/known-good/package-ready head:
  5501295 Add P7 install write contour.
- Current disposable VPS: 89.185.80.166.
- Latest live smoke evidence:
  research/amn2/phase-7-write-install-mutation-contour-5501295-2026-06-20.md.
- Latest RC gate matrix:
  research/amn2/phase-7-rc-gate-matrix-consolidation-2026-06-14.md.
- Latest handoff compression:
  research/amn2/phase-7-final-rc-handoff-compression-2026-06-14.md.
- Latest evidence index / dry checklist / RC notes polish:
  research/amn2/phase-7-evidence-watch-drycheck-rcnotes-2026-06-14.md.
- Latest final freeze / named-gate menu:
  research/amn2/phase-7-final-freeze-watch-menu-2026-06-14.md.
- Latest public exposure pre-cutover:
  research/amn2/phase-7-public-exposure-gate-precutover-b121865-2026-06-14.md.
- Latest public exposure admin/domain prerequisite:
  research/amn2/phase-7-public-exposure-admin-domain-prereq-b121865-2026-06-14.md.
- Latest public exposure runtime/login verification:
  research/amn2/phase-7-public-exposure-runtime-login-verify-b121865-2026-06-18.md.
- Latest public cutover guard:
  research/amn2/phase-7-public-cutover-guard-b121865-2026-06-18.md.
- Latest DNS/domain/TLS prerequisite staging + watch-only intake:
  research/amn2/phase-7-dns-domain-tls-prereq-watch-intake-2026-06-18.md.
- Latest client compatibility watch refresh:
  research/amn2/phase-7-client-compatibility-watch-refresh-4-8-19-2026-06-18.md.
- Latest IP-only exposure policy decision:
  research/amn2/phase-7-ip-only-exposure-policy-decision-2026-06-18.md.
- Latest watch-only intake + status hygiene:
  research/amn2/phase-7-watch-only-intake-status-hygiene-2026-06-18.md.
- Latest watch-only intake correction:
  research/amn2/phase-7-watch-only-intake-correction-2026-06-18.md.
- Latest watch-only intake current signals:
  research/amn2/phase-7-watch-only-intake-current-signals-2026-06-19.md.
- Latest docs quality audit / IP-only env reconciliation plan:
  research/amn2/phase-7-docs-quality-audit-ip-env-reconcile-2026-06-18.md.
- Latest public URL env reconciliation:
  research/amn2/phase-7-public-url-env-reconciliation-b121865-2026-06-19.md.
- Latest IP-only public exposure risk guard:
  research/amn2/phase-7-ip-only-public-exposure-risk-guard-b121865-2026-06-19.md.
- Latest config/write read-only preflight:
  research/amn2/phase-7-config-write-read-only-preflight-2026-06-19.md.
- Latest operator-local config delivery guard:
  research/amn2/phase-7-config-delivery-operator-local-guard-b121865-2026-06-19.md.
- Latest operator-local target inventory:
  research/amn2/phase-7-config-delivery-target-inventory-b121865-2026-06-19.md.
- Latest operator-local private handoff:
  research/amn2/phase-7-config-delivery-private-handoff-device1-b121865-2026-06-19.md.
- Latest operator-local private handoff device 2:
  research/amn2/phase-7-config-delivery-private-handoff-device2-b121865-2026-06-19.md.
- Latest write/backup/Telegram read-only preflight:
  research/amn2/phase-7-write-backup-telegram-read-only-preflight-2026-06-19.md.
- Latest watch-only intake after critical preflights:
  research/amn2/phase-7-watch-only-intake-after-critical-preflights-2026-06-19.md.
- Latest watch-only intake cycle closeout:
  research/amn2/phase-7-watch-only-intake-cycle-complete-2026-06-19.md.
- Latest P7-C006 backup-only evidence:
  research/amn2/phase-7-backup-only-evidence-b121865-2026-06-19.md.
- Latest P7-C004a destructive pre-cutover guard:
  research/amn2/phase-7-destructive-clean-installer-precutover-guard-b121865-2026-06-19.md.
- Latest P7-C004b destructive clean installer execution:
  research/amn2/phase-7-destructive-clean-installer-execution-b121865-2026-06-19.md.
- Latest post-clean write/backup/Telegram read-only rebaseline:
  research/amn2/phase-7-post-clean-write-backup-telegram-read-only-rebaseline-b121865-2026-06-19.md.
- Latest P7-C005 write/install contour:
  research/amn2/phase-7-write-install-mutation-contour-5501295-2026-06-20.md.
- Latest P7-C006a provider restore-point + watch hygiene:
  research/amn2/phase-7-provider-backup-restore-point-watch-hygiene-2026-06-20.md.
- Latest P7-C006 current-state backup-only evidence:
  research/amn2/phase-7-current-state-backup-only-5501295-2026-06-20.md.
- Latest P7-C007 Telegram private RC decision:
  research/amn2/phase-7-telegram-defer-private-rc-2026-06-20.md.
- Latest final RC freeze/status pass:
  research/amn2/phase-7-final-rc-freeze-status-5501295-2026-06-20.md.

Сначала прочитай:
- docs/NEXT_CHAT_AMN2_PHASE_7_RELEASE_CANDIDATE.ru.md
- docs/PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md
- docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md
- docs/AMN2_PHASE_7_EVIDENCE_INDEX.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/PROJECT_CONTEXT_IMPORT.ru.md
- research/amn2/transfer-backlog.md
- research/amn2/phase-7-rc-gate-matrix-consolidation-2026-06-14.md
- research/amn2/phase-7-live-update-smoke-b121865-2026-06-14.md
- research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md

Стартовая проверка:
1. AMN3 git status/log.
2. AMN2 git status/log.
3. Если нужна публикация/PR - GitHub connector read access.
4. Если нужны live actions - сначала запросить exact named gate.
```

## Границы Phase 7

По умолчанию разрешены только:

- local-only docs/tests/security/package-preflight;
- watch-only intake;
- evidence/status hygiene.

Запрещено без отдельного exact named gate:

- live VPS commands, SSH commands, package upload/apply/rebuild on VPS;
- service restart/deploy;
- public exposure, DNS/domain/TLS/reverse proxy/firewall/listener changes;
- config delivery, `.conf`, QR, `vpn://`, client secret output;
- write API, install mutation, Local Agent mutation;
- backup/import/reboot/restore apply;
- production peer/user mutation;
- destructive VPS/provider actions;
- Telegram token use, live bot send, identity/profile/media mutation;
- secret-bearing evidence publication;
- upstream/GPL implementation copy.

Default flags:

```text
VPS_APPLY_ENABLED=false
public_launch=not opened
production_mutation=not opened
```

## Current State

```text
AMN2 head: 5501295 Add P7 install write contour
workspace/evidence repo: barakov-dot/amn3 master ec811cf
AMN2 package/source repo: barakov-dot/amn2 codex-vps-test-prep 5501295
package status: VPS-smoked/pass for 5501295
smoke status: scoped-write-contour-smoked-pass for 5501295
public/config/write status: blocked-by-preconditions
public exposure status: operator-only-ip-loopback-ssh-tunnel
public URL env residue status: reconciled-removed-in-P7-C002e
IP-only public exposure status: blocked-in-P7-C002d-not-exposed
config/write read-only preflight status: completed-blocked-no-delivery-no-write
RC gate matrix status: completed
latest watch-only status: completed-watch-only-status-hygiene-no-live-action
latest watch-only correction: completed-watch-only-correction-no-live-action
latest watch-only intake: completed-watch-only-intake-cycle-complete-no-live-action
P7-C006 backup-only status: completed-backup-only-create-verify-no-restore-import-reboot
P7-C004a destructive pre-cutover status: ready-for-final-destructive-stop-line-no-apply
P7-C004b destructive clean installer status: completed-clean-install-loopback-smoke
post-clean write/backup/Telegram rebaseline status: completed-post-clean-read-only-rebaseline-no-mutation
P7-C005 write/install contour status: completed-scoped-write-contour-smoked
P7-C006a provider restore-point status: completed-inconclusive-no-restore-point-confirmed
P7-C006 current-state backup-only status: completed-current-state-backup-only-create-verify-no-restore-import-reboot
P7-C007 Telegram status: deferred-not-required-for-private-rc-no-telegram-action
final RC freeze status: completed-rc-ready-paused-state-no-live-action
latest docs audit status: completed-docs-only-audit-with-inactive-reconcile-gate
local-only queue: closed
local-only expansion status: frozen before named gate
active work: residual P7-C006 scopes + watch-only intake only
P7-C002 default status: blocked/not-exposed after P7-C002d
```

Latest important evidence:

- `research/amn2/phase-7-live-update-smoke-b121865-2026-06-14.md`
- `research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md`
- `research/amn2/phase-7-public-exposure-gate-precutover-b121865-2026-06-14.md`
- `research/amn2/phase-7-public-exposure-admin-domain-prereq-b121865-2026-06-14.md`
- `research/amn2/phase-7-public-exposure-runtime-login-verify-b121865-2026-06-18.md`
- `research/amn2/phase-7-public-cutover-guard-b121865-2026-06-18.md`
- `research/amn2/phase-7-dns-domain-tls-prereq-watch-intake-2026-06-18.md`
- `research/amn2/phase-7-client-compatibility-watch-refresh-4-8-19-2026-06-18.md`
- `research/amn2/phase-7-ip-only-exposure-policy-decision-2026-06-18.md`
- `research/amn2/phase-7-watch-only-intake-status-hygiene-2026-06-18.md`
- `research/amn2/phase-7-watch-only-intake-correction-2026-06-18.md`
- `research/amn2/phase-7-watch-only-intake-current-signals-2026-06-19.md`
- `research/amn2/phase-7-docs-quality-audit-ip-env-reconcile-2026-06-18.md`
- `research/amn2/phase-7-public-url-env-reconciliation-b121865-2026-06-19.md`
- `research/amn2/phase-7-ip-only-public-exposure-risk-guard-b121865-2026-06-19.md`
- `research/amn2/phase-7-config-write-read-only-preflight-2026-06-19.md`
- `research/amn2/phase-7-config-delivery-operator-local-guard-b121865-2026-06-19.md`
- `research/amn2/phase-7-config-delivery-target-inventory-b121865-2026-06-19.md`
- `research/amn2/phase-7-config-delivery-private-handoff-device1-b121865-2026-06-19.md`
- `research/amn2/phase-7-config-delivery-private-handoff-device2-b121865-2026-06-19.md`
- `research/amn2/phase-7-write-backup-telegram-read-only-preflight-2026-06-19.md`
- `research/amn2/phase-7-backup-only-evidence-b121865-2026-06-19.md`
- `research/amn2/phase-7-destructive-clean-installer-precutover-guard-b121865-2026-06-19.md`
- `research/amn2/phase-7-destructive-clean-installer-execution-b121865-2026-06-19.md`
- `research/amn2/phase-7-post-clean-write-backup-telegram-read-only-rebaseline-b121865-2026-06-19.md`
- `research/amn2/phase-7-write-install-mutation-contour-5501295-2026-06-20.md`
- `research/amn2/phase-7-provider-backup-restore-point-watch-hygiene-2026-06-20.md`
- `research/amn2/phase-7-current-state-backup-only-5501295-2026-06-20.md`
- `research/amn2/phase-7-telegram-defer-private-rc-2026-06-20.md`
- `research/amn2/phase-7-final-rc-freeze-status-5501295-2026-06-20.md`
- `research/amn2/phase-7-watch-only-intake-after-critical-preflights-2026-06-19.md`
- `research/amn2/phase-7-watch-only-intake-cycle-complete-2026-06-19.md`
- `research/amn2/phase-7-public-config-write-prerequisite-split-2026-06-14.md`
- `research/amn2/phase-7-public-exposure-readiness-design-2026-06-14.md`
- `research/amn2/phase-7-config-delivery-channel-readiness-2026-06-14.md`
- `research/amn2/phase-7-write-api-scope-decision-2026-06-14.md`
- `research/amn2/phase-7-backup-restore-import-readiness-2026-06-14.md`
- `research/amn2/phase-7-telegram-identity-readiness-2026-06-14.md`
- `research/amn2/phase-7-rc-gate-matrix-consolidation-2026-06-14.md`
- `research/amn2/phase-7-final-rc-handoff-compression-2026-06-14.md`
- `research/amn2/phase-7-evidence-watch-drycheck-rcnotes-2026-06-14.md`
- `research/amn2/phase-7-final-freeze-watch-menu-2026-06-14.md`

## Утвержденный Оставшийся План

Закрыто / не следующий gate:

- `P7-C002` Public exposure gate.
  Gate: public exposure. Current status: admin/domain prerequisites updated,
  runtime/login verified on loopback, public cutover guard blocked trusted
  domain/TLS apply, and `P7-I011` recorded the operator decision to not use a
  DNS domain for AMN2. Selected default mode is VPS IP + SSH tunnel to loopback
  web/admin. Public exposure not applied. Any future IP-only public web/admin
  exposure requires a new separate exact risk-acceptance/design gate. Public URL
  fields left by `P7-C002a` were removed in `P7-C002e`; `P7-C002d` blocked
  IP-only public exposure by four risk blockers and performed no apply. This is
  no longer the default next gate; future public exposure needs a new exact
  risk-acceptance/design gate.

- `P7-C003` Config delivery gate.
  Gate: config delivery. Known active devices from the 2026-06-19 target
  inventory were completed through operator-local private file handoff:
  `TARGET_DEVICE_ID=1` and `TARGET_DEVICE_ID=2`. No config payload or client
  secret was printed to chat/evidence. This is no longer the default next gate;
  future resend/revocation, SMTP/Telegram delivery, public/self-service links or
  new target devices require a separate exact named gate.

- `P7-C004` Destructive clean installer execution gate.
  Gate: destructive. `P7-C004a` pre-cutover guard passed, then `P7-C004b`
  completed clean install from verified `b121865` package/source, DB init,
  loopback web and API loopback smoke. This is no longer the default next gate;
  future provider rebuild, another clean install, restore/import or quarantine
  cleanup requires a separate exact named gate.

Критичные gated/deferred:

- `P7-C005 + P7-C006 + P7-C007` post-clean read-only rebaseline.
  Gate: read-only/live evidence after `P7-C004b`. Completed with clean
  `b121865` install active, web loopback-only, external probes closed,
  `write_api_route_count=0`, no backup create, no restore/import/reboot and no
  Telegram token use/API call/profile/media mutation. This was later superseded
  for `P7-C005` by the 2026-06-20 scoped write contour; `P7-C007` was later
  deferred as not required for private RC.
- `P7-C005 + P7-C006 + P7-C007` read-only preflight.
  Gate: local/docs/evidence preflight. Completed with no write mutation,
  backup/restore/import or Telegram mutation. This was later superseded for
  `P7-C005` by the scoped write contour and for `P7-C007` by the private-RC
  deferral decision; residual `P7-C006` scopes remain exact named gates only.
- Watch-only intake after critical preflights.
  Gate: docs-only/watch-only. Completed with no live action, no mutation and no
  new implementation task. Known active `P7-C003` device handoffs are complete;
  `P7-C005` is now complete for the scoped write contour; residual `P7-C006`
  remains exact-gated and `P7-C007` was later deferred for private RC.
- Watch-only intake cycle closeout.
  Gate: docs-only/watch-only. Completed with no live action, no mutation, no
  upstream/GPL code copy and no new implementation task. Current observed
  client signals remain `amnezia-client 4.8.19.0` and `amneziawg-android 2.0.1`.
- `P7-C005` Write API / install mutation gate.
  Gate: write API / production mutation. Completed for the scoped
  `install:write` contour on `5501295`: `POST /api/install/mutation-requests`
  records safe `api_write` and returns
  `recorded_blocked_by_vps_apply_disabled` while `VPS_APPLY_ENABLED=false`.
  Future actual installer runner, broader write routes or Local Agent mutation
  require a new exact named gate.
- `P7-C006` Backup/restore/import gate.
  Gate: backup/restore/import. Backup-only create+verify is complete for
  `b121865` on disposable VPS `89.185.80.166`. Post-clean rebaseline did not
  create a new backup and kept restore/import/download/reboot disabled.
  `P7-C006a` provider-console evidence is complete but inconclusive: provider
  restore-point availability is not confirmed. Current-state backup-only
  create+verify for `5501295` is complete and the artifact stayed on the VPS.
  Remaining scopes still require exact named gates: restore apply, archive
  import, remote backup download, reboot, disaster-recovery drill, destructive
  migration and provider restore use.
- `P7-C007` Telegram identity/profile/media mutation gate.
  Gate: Telegram identity. Deferred as not required for private/operator RC.
  No Telegram token use, live bot send, profile/media mutation, media upload or
  credential handoff was performed. Future Telegram work would require a new
  exact named gate.

Watch-only:

- Amnezia/DefaultVPN/AmneziaWG client releases. Current signals only:
  `amnezia-client 4.8.19.0`, `amneziawg-android 2.0.1`.
- PRVTPRO/KYORESUAS upstream changes as ideas/signals/links only.

Очень важные / важные / нормальные / простые / косметические:

- активных утвержденных local-only задач нет.

## RC Gate Matrix

Полная матрица живет в:

```text
docs/PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md
```

Сводка:

- `P7-C002` -> readiness source `P7-I005`; admin/domain prerequisites updated
  in `P7-C002a`; runtime/login verified in `P7-C002b`; public cutover guard
  blocked trusted domain/TLS apply; `P7-I011` closed the DNS/domain path by
  operator policy and selected VPS IP + SSH tunnel to loopback web/admin as
  default; `P7-I012` added env reconciliation planning; `P7-C002e` removed the
  public URL env residue; `P7-C002d` blocked IP-only public exposure with
  `ip_only_public_apply_allowed=false`. Next action: keep operator-only/
  watch-only, or use a new exact risk-acceptance/design gate if IP-only public
  exposure is still desired.
- `P7-C003` -> readiness source `P7-I006` plus 2026-06-19 read-only preflight
  and operator-local guard plus read-only target inventory; next action: exact
  named config-delivery gate only for resend/revocation, another channel or a
  new target device; known `TARGET_DEVICE_ID=1` and `2` private handoffs are
  already complete.
- `P7-C004` -> readiness source Phase 6 destructive checklist boundary;
  `P7-C004a` pre-cutover guard and `P7-C004b` execution are complete for
  `b121865`. Clean `/opt/amn2` install is active, loopback web is healthy, API
  loopback smoke passed and external probes stayed closed. Future provider
  rebuild, another clean install, restore/import or quarantine cleanup requires
  a new exact named gate.
- `P7-C005` -> readiness source `P7-I007` plus 2026-06-19 read-only preflight,
  post-clean rebaseline and 2026-06-20 scoped write contour evidence; completed
  for audit-only `install:write` request contour. Future actual installer
  execution or broader write APIs require a new exact named gate.
- `P7-C006` -> readiness source `P7-I008` plus 2026-06-19 read-only preflight,
  backup-only evidence, post-clean rebaseline and 2026-06-20 `P7-C006a`
  inconclusive provider-console evidence plus current-state backup-only
  evidence for `5501295`;
  next action: exact named backup/restore/import gate only.
- `P7-C007` -> readiness source `P7-I009` plus 2026-06-19 read-only preflight,
  post-clean rebaseline and 2026-06-20 private RC decision; deferred/not
  required for private RC. Future Telegram identity/profile/media work remains
  exact named gate only.

## Доступ И Named Gates

Для обычной Phase 7 работы дополнительный доступ не нужен.

Operator named-gate menu:

- `P7-C002` Public exposure gate is blocked/not-exposed after `P7-C002d`; do
  not reopen as the default next step.
- `P7-C003` Config delivery gate: known active devices completed private
  handoff; reopen only for resend/revocation, another delivery channel or a new
  target device.
- `P7-C004` Destructive clean installer execution gate.
  Current status: `P7-C004b` completed-clean-install-loopback-smoke for
  `b121865`; not a default next gate unless another destructive/provider action
  is intentionally opened.
- `P7-C005` Write API / install mutation gate is complete for the scoped
  audit-only contour on `5501295`; reopen only for actual installer runner,
  broader write API or Local Agent mutation.
- `P7-C006` Backup/restore/import gate.
- Future Telegram identity/profile/media mutation gate only if explicitly
  reopened.

If no exact gate is chosen, wait or repeat watch-only intake later as a fresh
cycle. The current watch-only item is closed.

## Неактивные Структурные Предложения

```text
No inactive structural proposal currently needed.
```

Для future live VPS work требовать фразу вида:

```text
Открываю <gate-id> <exact live task> для <commit> на текущем disposable VPS 89.185.80.166.
```

Для destructive clean install/reinstall:

```text
Открываю P7-C004 destructive clean installer execution gate для disposable VPS 89.185.80.166.
```

## Ритм Рекомендаций

После каждой закрытой задачи:

- выводить полный утвержденный оставшийся план;
- отдельно выводить новые структурные предложения;
- не смешивать active plan и inactive proposals;
- давать одиночные, парные, тройные, четверные и более крупные варианты
  только в блоке рекомендаций;
- указывать importance и gate;
- не активировать новые candidate tasks без явного согласия оператора.
