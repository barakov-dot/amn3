# `amn2` Transfer Backlog

## Current override 2026-07-14

Phase 10 закрыта на AMN2/VPS head `3c91601`; historical queue ниже не является
активным списком и должна дедуплицироваться против текущего кода/evidence.
Authoritative Phase 11 backlog, IDs и зависимости:

- `docs/AMN2_PHASE_10_FINAL_CLOSEOUT_PACKET.ru.md`;
- `docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md`;
- `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`;
- первый control block `docs/PROJECT_STATUS_CURRENT.ru.md`.

Не предлагать старые completed package/API/client gates повторно.

Phase 7 P7-C010f Windows desktop path acceptance record 2026-06-20: completed
as `completed-windows-desktop-path-accepted-operator-observation-no-live-action`.
Evidence
`research/amn2/phase-7-windows-desktop-path-acceptance-2026-06-20.md`.
Operator observation: the previously issued Windows configuration works clearly
on Windows desktop. This accepts the desktop path as evidence that the AMN2
server/base profile is not globally broken, but it does not close mobile
acceptance: iPhone DefaultVPN remains experimental/unreliable, QR remains
non-primary, full `vpn://` one-click copy remains impractical for real payload
length, and Android AmneziaWG is still pending. No live VPS/SSH, Telegram
action, config/QR/import-link output, restore/import/reboot, provider mutation,
write execution or secret-bearing evidence was performed.

Phase 7 Codex Security post-fix validation 2026-06-20: completed as
`completed-post-fix-security-validation-no-open-findings` for AMN2 `c958733`.
Evidence
`research/amn2/phase-7-codex-security-postfix-c958733-2026-06-20.md`.
AMN2 `codex-vps-test-prep` was pushed from `5501295` to
`c9587332d425583ed627899d7fa950756b64c4dc` after hardening security-sensitive
operations: CLI live peer mutations now require `VPS_APPLY_ENABLED=true`;
Telegram admin delivery failure fallback no longer sends secret-bearing config
payloads/import links; SMTP STARTTLS uses an explicit verifying context; backup
artifacts are chmodded to `0600`; debug snapshot port greps validate numeric
ports and avoid `bash -lc` string execution. Focused pytest passed with
`95 passed`; full pytest passed with `729 passed`; Codex Security post-fix scan
`b9106c1d-1f68-493a-91a6-2698303da56e` completed with `0` reportable findings.
No live VPS action was performed. Next exact gate should build/apply/smoke a
`c958733` package on disposable VPS `89.185.80.166`, because live runtime
evidence remains on `5501295`.

Phase 7 P7-C008a Telegram token reconciliation and user-flow smoke 2026-06-20:
completed as `completed-getme-dispatcher-surface-no-send` for AMN2 `5501295`
on disposable VPS `89.185.80.166`. Evidence
`research/amn2/phase-7-telegram-token-reconciliation-user-flow-smoke-5501295-2026-06-20.md`.
The earlier invalid-token `P7-C008` blocker is retained as historical evidence
in `research/amn2/phase-7-telegram-user-flow-smoke-token-invalid-5501295-2026-06-20.md`
and is resolved by `P7-C008a`. Token reconciliation used operator-secret handoff
with rollback copy and no token output; Telegram `getMe` passed; the
non-polling bot/user-flow surface was constructed. No polling, live Telegram
send, identity/profile/media mutation, config delivery payload output, write
execution, public exposure, restore/import/reboot, provider mutation or
secret-bearing output was performed. External probes stayed closed.

Phase 7 Telegram-first/operator-web policy 2026-06-20: completed as
`completed-docs-only-telegram-first-operator-web-policy`. Evidence
`research/amn2/phase-7-telegram-first-operator-web-policy-2026-06-20.md`.
Decision: AMN2 private/operator RC uses Telegram as the user-facing channel and
keeps web/admin operator-only by VPS IP plus loopback/SSH tunnel or equivalent
private access. Public web-admin exposure, DNS domain, trusted public TLS and
reverse proxy are not required for private/operator RC. `P7-C002` is
deferred/not required for private RC; `P7-C007` Telegram identity/profile/media
remains deferred. Future Telegram user-flow smoke is a separate exact named
live Telegram gate. No live VPS/SSH command, public exposure, Telegram token
use/API call/live send/profile/media mutation or secret-bearing output was
performed.

Phase 7 P7-C004d + P7-C006b post-direct-clean login and backup 2026-06-20:
completed as `completed-login-verified-backup-create-verify` for AMN2
`5501295` on disposable VPS `89.185.80.166`. Evidence
`research/amn2/phase-7-post-direct-clean-login-backup-5501295-2026-06-20.md`.
Loopback admin login passed after direct clean install; backup create and verify
passed for the current clean state; artifact stayed on the VPS under
`/opt/amn2/backups/p7-c006b-post-direct-clean-5501295-20260620T061005Z`,
basename `amneziya-backup-20260620T061102Z.tar.enc`, bytes `204900`, sha256
`f8e0591db75e8ec9ce58f4fa9d71972d577e1ec103194d1943a626aa9b156b97`, mode
`644`. External probes stayed closed. No restore/import/reboot, provider
mutation, remote backup download, service restart, public exposure, config
delivery, write execution, Local Agent mutation, production peer/user mutation,
Telegram action or secret-bearing output was performed. Residual `P7-C006`
restore/import/download/reboot/DR/provider-restore scopes remain exact named
gates only.

Phase 7 P7-C004c direct clean installer execution 2026-06-20: completed as
`completed-direct-clean-install-5501295-loopback-smoke` for AMN2 `5501295` on
disposable VPS `89.185.80.166`. Evidence
`research/amn2/phase-7-direct-clean-installer-5501295-2026-06-20.md`. Verified
`5501295` package/source was uploaded and checked, current `/opt/amn2` was
quarantined at `/opt/amn2.pre-p7-c004c-20260620T054656Z`, clean `/opt/amn2`
was installed, DB init passed, loopback web returned `/login=200`, API
loopback smoke returned `VPS verdict: pass` with run_id `20260620T054813Z`,
and public probes to `3030`, `3040`, `80` and `443` stayed `000`. No provider
rebuild, reboot, restore/import, remote backup download, public exposure,
config delivery, write API enablement, Local Agent mutation, production
peer/user mutation, Telegram action or secret-bearing output was performed.
This closes the direct clean-installer RC gap for current head `5501295`.

Phase 7 final RC freeze/status pass 2026-06-20: completed as
`completed-rc-ready-paused-state-no-live-action` for AMN2 `5501295`. Evidence
`research/amn2/phase-7-final-rc-freeze-status-5501295-2026-06-20.md`. Frozen
state is `rc_ready_paused_private_operator_lane`: latest VPS-smoked/package
head and current VPS source overlay are `5501295`; web/admin is loopback-only;
public exposure is not opened; `VPS_APPLY_ENABLED=false`; scoped
`install:write` is audit-only and blocked by apply-disabled; current-state
backup create+verify exists; known-device operator-local private handoff is
complete; Telegram identity/profile/media is deferred for private RC. No live
VPS/SSH command, package apply, service restart, public exposure, config
delivery, write execution, restore/import/reboot, provider mutation, Local
Agent mutation, Telegram action or secret-bearing output was performed.
Remaining approved work: residual `P7-C006` restore/import/download/reboot/DR/
provider-restore scopes only, plus watch-only intake.

Phase 7 P7-C007 Telegram identity/profile/media decision 2026-06-20:
completed as `completed-deferred-not-required-for-private-rc-no-telegram-action`.
Evidence `research/amn2/phase-7-telegram-defer-private-rc-2026-06-20.md`.
Telegram identity/profile/media mutation is deferred and is not required for
private/operator RC readiness. No Telegram token use, Telegram API call, live
bot send, profile/media mutation, media upload, credential handoff, live
VPS/SSH command or secret-bearing output was performed. Future Telegram
identity/profile/media work would require a new exact named gate. Remaining
approved Phase 7 work is residual `P7-C006`
restore/import/download/reboot/DR/provider-restore scope only, plus watch-only
intake.

Phase 7 P7-C006 current-state backup-only evidence 2026-06-20: completed as
`completed-current-state-backup-only-create-verify-no-restore-import-reboot`
for AMN2 `5501295` on disposable VPS `89.185.80.166`. Evidence
`research/amn2/phase-7-current-state-backup-only-5501295-2026-06-20.md`.
Source overlay matched `5501295`; backup create and verify passed; artifact
stayed on the VPS under
`/opt/amn2/backups/p7-c006-current-state-5501295-20260620T050111Z`, basename
`amneziya-backup-20260620T050141Z.tar.enc`, bytes `218552`, sha256
`1412e6791ba03e0f955d46e988357274a413d0afc96a2e72c1b6077624554bb2`, mode
`600`. External probes stayed closed. No restore/import/reboot, provider
mutation, remote backup download, service restart, public exposure, config
delivery, write execution, Local Agent mutation, Telegram action or
secret-bearing output was performed. Remaining exact gates are residual
`P7-C006` restore/import/download/reboot/DR/provider-restore scopes only.

Phase 7 P7-C006a + watch-only status hygiene 2026-06-20: completed as
`completed-provider-console-evidence-inconclusive-watch-hygiene-no-mutation`.
Evidence
`research/amn2/phase-7-provider-backup-restore-point-watch-hygiene-2026-06-20.md`.
The operator-provided provider-console screenshot for VPS `89.185.80.166`
showed backup creation success, move-to-internal-storage failure and backup
deletion success on 2026-06-15. Provider restore-point availability is not
confirmed and must not be treated as a restore prerequisite. No provider
mutation, restore/import/reboot, remote backup download, live VPS/SSH command or
secret-bearing output was performed. Watch-only release signals remain
`amnezia-client 4.8.19.0` and `amneziawg-android 2.0.1`; no live gate,
mutation, upstream/GPL code copy or new implementation task was created.
Remaining approved Phase 7 exact gates are residual `P7-C006`
restore/import/download/reboot/DR scopes and `P7-C007`.

Phase 7 P7-C005 write API / install mutation gate 2026-06-20: completed as
`completed-scoped-write-contour-smoked` for AMN2 `5501295` on disposable VPS
`89.185.80.166`. Evidence
`research/amn2/phase-7-write-install-mutation-contour-5501295-2026-06-20.md`.
AMN2 `codex-vps-test-prep` was advanced and pushed to
`55012958ff6b8338254f3f68dfe6779f4bc56f5d` (`Add P7 install write contour`).
Local full suite returned `726 passed, 1 StarletteDeprecationWarning`; package
`dist/amn2-vps-update-and-smoke-kit-5501295.zip` sha256
`C03D26673AD79D9487A3ED34E9657E0DCA10EBC9BB601E429385091F1DFEF407` and source
zip sha256 `DA7DA58E0FD8D778BD4A22471BBCD9038CC455ACD3C0538A38874215C81646D3`
were verified. Live apply updated source overlay from `b121865` to `5501295`,
loopback web restart passed, baseline API smoke passed, and the scoped write
route smoke passed with `server_read_token_post_http=403`,
`install_write_token_post_http=202`, status
`recorded_blocked_by_vps_apply_disabled`, `audit_safe=yes` and external probes
closed. The route is audit-only while `VPS_APPLY_ENABLED=false`; no actual
installer executor, public exposure, config delivery, restore/import/reboot,
Local Agent mutation, Telegram action or secret-bearing output was performed.
Remaining approved Phase 7 live/mutation gates are residual `P7-C006` scopes
and `P7-C007`; `P7-C006a` was later closed as inconclusive docs-only evidence.

Phase 7 P7-C005 + P7-C006 + P7-C007 post-clean read-only rebaseline
2026-06-19: completed as
`completed-post-clean-read-only-rebaseline-no-mutation` for AMN2 `b121865` on
disposable VPS `89.185.80.166`. Evidence
`research/amn2/phase-7-post-clean-write-backup-telegram-read-only-rebaseline-b121865-2026-06-19.md`.
The clean `P7-C004b` install remained active with source overlay
`b121865f488821f6fc471c9529fb26e5d7992515`, loopback web on
`127.0.0.1:3030`, no persistent public API listener on `3040`, no public
`80/443` listeners and external probes returning `000`. Public API route
inventory returned ten GET routes and `write_api_route_count=0`; web/admin
route inventory was inspected without invoking write routes. Clean DB aggregate
counts were users `0`, devices `0`, servers `1`, API tokens `2` and admin
actions `6`. Backup help probing was safe, no backup was created, quarantined
backup files remained in the old runtime quarantine, and Telegram token
presence was checked without printing or using the token. No write API
enablement, install mutation, backup create, restore apply, archive import,
remote backup download, reboot, service restart, public exposure, config
delivery, Local Agent mutation, production peer/user mutation, Telegram API
call/profile/media/send action, secret publication or upstream/GPL code copy
was performed. `P7-C005` was later completed for the scoped write contour,
residual `P7-C006` scopes remain separate exact named gates only, and
`P7-C007` was later deferred as not required for private RC. `P7-C006a`
provider restore-point confirmation was later completed as inconclusive
docs-only evidence.

Phase 7 P7-C004b destructive clean installer execution 2026-06-19: completed
as `completed-clean-install-loopback-smoke` for AMN2 `b121865` on disposable
VPS `89.185.80.166`. Evidence
`research/amn2/phase-7-destructive-clean-installer-execution-b121865-2026-06-19.md`.
The operator opened the exact destructive gate and entered the final
destructive phrase. The old `/opt/amn2` was moved to
`/opt/amn2.pre-p7-c004b-20260619T173819Z`; clean `/opt/amn2` was installed from
the verified `b121865` package/source; `.env` and `servers.yml` were regenerated
without printing secrets; DB initialization passed; loopback web returned
`/login=200`; API loopback smoke returned `VPS verdict: pass`; external probes
to `3030`, `3040`, `80` and `443` stayed `000`. No provider rebuild, reboot,
restore/import, remote backup download, public exposure, config delivery, write
API, Local Agent mutation, production peer/user mutation, Telegram action or
secret-bearing output was performed. This was later superseded by `P7-C005`
scoped write contour completion, current-state `P7-C006` backup evidence, and
the private-RC Telegram deferral decision; residual `P7-C006` scopes require
exact named gates only.

Phase 7 P7-C004a destructive clean installer pre-cutover guard 2026-06-19: completed as `ready-for-final-destructive-stop-line-no-apply` for AMN2 `b121865` on disposable VPS `89.185.80.166`. Evidence `research/amn2/phase-7-destructive-clean-installer-precutover-guard-b121865-2026-06-19.md`. Local package/source checksums matched, remote source overlay matched `b121865f488821f6fc471c9529fb26e5d7992515`, the `P7-C006` backup artifact was present with matching sha256, external probes stayed closed and `pre_cutover_blocker_count=0`. No wipe, reinstall, package apply, service restart, provider action, restore/import/reboot, public exposure, write API, Local Agent mutation, production peer/user mutation, Telegram action or secret-bearing output was performed. This pre-cutover guard was later followed by `P7-C004b`, which completed clean install + loopback smoke.

Phase 7 P7-C006 backup-only evidence gate 2026-06-19: completed as `completed-backup-only-create-verify-no-restore-import-reboot` for AMN2 `b121865` on disposable VPS `89.185.80.166`. Evidence `research/amn2/phase-7-backup-only-evidence-b121865-2026-06-19.md`. First attempt failed because backup CLI required `APP_SECRET_KEY` in process env and SSH did not load `.env`; read-only diagnostic confirmed CLI support and did not print the forbidden-marker log. Retry loaded `APP_SECRET_KEY` only inside the remote Python process without printing it; backup create and verify passed. Artifact stayed on the VPS and was not downloaded. No restore apply, archive import, reboot, destructive migration, public exposure, write API, Local Agent mutation, production peer/user mutation, Telegram action or secret-bearing output was performed. Remaining P7-C006 scopes require separate exact gates.

Phase 7 watch-only intake cycle closeout 2026-06-19: completed as
`completed-watch-only-intake-cycle-complete-no-live-action`. Evidence
`research/amn2/phase-7-watch-only-intake-cycle-complete-2026-06-19.md`.
Current observed client signals remain `amnezia-client 4.8.19.0` and
`amneziawg-android 2.0.1`; PRVTPRO remains an upstream idea source only and
KYORESUAS remains an API taxonomy signal only. No live action, mutation,
upstream/GPL code copy or new implementation task was created.

Phase 7 watch-only intake after critical preflights 2026-06-19: completed as
`completed-watch-only-intake-after-critical-preflights-no-live-action`. Evidence
`research/amn2/phase-7-watch-only-intake-after-critical-preflights-2026-06-19.md`.
It reviewed local evidence after `P7-C003` known-device private handoffs and the
`P7-C005 + P7-C006 + P7-C007` read-only preflight. No new local automation
output, live gate, mutation, secret-bearing output or implementation task was
created. `P7-C005` is now complete for the scoped write contour; residual
`P7-C006` scopes remain separate exact named gates only, and `P7-C007` was
later deferred as not required for private RC.

Phase 7 P7-C005 + P7-C006 + P7-C007 write/backup/Telegram read-only preflight
2026-06-19: completed as `completed-read-only-preflight-no-mutation`. Evidence
`research/amn2/phase-7-write-backup-telegram-read-only-preflight-2026-06-19.md`.
This pass reviewed existing local readiness evidence only; no live VPS/SSH
command or external API call was run. At that time `P7-C005` was still blocked
by read-only RC policy and disabled write/Local Agent mutation; this was later
superseded by the 2026-06-20 scoped write contour on `5501295`. `P7-C006`
remains blocked for live backup, restore apply, archive import, remote backup
download and reboot. At that time `P7-C007` was blocked for Telegram token use,
live bot send, profile/media mutation and media upload; it was later deferred
as not required for private RC. No backup archive create, restore/import apply,
Telegram action, secret publication or upstream/GPL code copy was performed.

Phase 7 P7-C003 target-specific operator-local private handoff for
`TARGET_USER_ID=1` / `TARGET_DEVICE_ID=2` 2026-06-19: completed as
`completed-private-file-copied-secret-not-printed` on disposable VPS
`89.185.80.166`. Evidence
`research/amn2/phase-7-config-delivery-private-handoff-device2-b121865-2026-06-19.md`.
The config was rendered on the VPS, copied to the operator-selected local
private destination outside the workspace and removed from the VPS. Remote/local
metadata matched: `artifact_bytes=438`, sha256
`87b5a41c665b593b72740b00422416ef73dc0d7a58ca928ea52c6722c0e5cbb3`. No config
payload, `.conf` contents, QR, `vpn://` payload or client secret was printed to
chat/evidence. No SMTP/Telegram send, public config link issue/redeem, write API
enablement, install mutation, Local Agent mutation, `.env` mutation, service
restart, public exposure, secret publication or upstream/GPL code copy was
performed. Together with device 1, both known active target devices from the
2026-06-19 inventory have completed private-file handoff. Resend/revocation,
SMTP/Telegram delivery, public/self-service links and new target devices remain
separate exact gates.

Phase 7 P7-C003 target-specific operator-local private handoff for
`TARGET_USER_ID=1` / `TARGET_DEVICE_ID=1` 2026-06-19: completed as
`completed-private-file-copied-secret-not-printed` on disposable VPS
`89.185.80.166`. Evidence
`research/amn2/phase-7-config-delivery-private-handoff-device1-b121865-2026-06-19.md`.
The config was rendered on the VPS, copied to the operator-selected local
private destination outside the workspace and removed from the VPS. Remote/local
metadata matched: `artifact_bytes=438`, sha256
`7ca64dd57a7467c4817e846a11d56d861013921c1db3f6ac020f7ca355dfdb83`. No config
payload, `.conf` contents, QR, `vpn://` payload or client secret was printed to
chat/evidence. No SMTP/Telegram send, public config link issue/redeem, write API
enablement, install mutation, Local Agent mutation, `.env` mutation, service
restart, public exposure, secret publication or upstream/GPL code copy was
performed. `TARGET_DEVICE_ID=2`, resend/revocation, SMTP/Telegram delivery and
public/self-service links remain separate exact gates.

Phase 7 P7-C003 target inventory for operator-local handoff 2026-06-19:
completed as `completed-read-only-target-inventory-no-delivery` on disposable VPS
`89.185.80.166`. Evidence
`research/amn2/phase-7-config-delivery-target-inventory-b121865-2026-06-19.md`.
Safe inventory found valid target pairs
`TARGET_USER_ID=1 TARGET_DEVICE_ID=1` and
`TARGET_USER_ID=1 TARGET_DEVICE_ID=2`; both devices are active with
`config_material_status=available` and `config_version=amneziawg_v2`. Runtime
stayed loopback-only and public probes remained closed. No config delivery,
`.conf`/QR/`vpn://` output, client secret output, SMTP/Telegram send, write API
enablement, install mutation, Local Agent mutation, `.env` mutation, service
restart, public exposure, secret publication or upstream/GPL code copy was
performed.

Phase 7 P7-C003 operator-local config delivery guard 2026-06-19: completed as
`blocked-pending-target-and-private-handoff-no-delivery` on disposable VPS
`89.185.80.166`. Evidence
`research/amn2/phase-7-config-delivery-operator-local-guard-b121865-2026-06-19.md`.
Source overlay marker confirmed `b121865f488821f6fc471c9529fb26e5d7992515`.
Channel is selected as `operator-local`; SMTP remains missing. Loopback web
checks returned `/login=200` and `/=303`; external probes to `3030`, `3040`,
`80` and `443` returned `000`. Route inventory found five config-related
web/admin routes and DB aggregate counts were collected without outputting
config artifacts. Actual delivery remains blocked until exact target user/device,
private artifact destination and one-time delivery/revocation policy are
selected. No config delivery, `.conf`/QR/`vpn://` output, client secret output,
SMTP/Telegram send, public config link issue/redeem, write API enablement,
install mutation, Local Agent mutation, `.env` mutation, service restart, public
exposure, secret publication or upstream/GPL code copy was performed.

Phase 7 P7-C003 + P7-C005 config/write read-only preflight 2026-06-19:
completed as `completed-read-only-preflight-blocked-no-delivery-no-write`.
Evidence
`research/amn2/phase-7-config-write-read-only-preflight-2026-06-19.md`.
No live VPS/SSH command was run. `P7-C003` remains blocked by missing delivery
channel decision, missing SMTP config / attachment policy and no selected
secret-safe operator-local delivery policy. At that time `P7-C005` was still
blocked by read-only RC policy, prior `write_api_route_count=0`,
`VPS_APPLY_ENABLED=false` and `LOCAL_AGENT_ENABLED=false`; this was later
superseded by the 2026-06-20 scoped write contour on `5501295`. No config
delivery, `.conf`/QR/`vpn://` output, SMTP/Telegram config send, tokenized
redeem, Local Agent mutation, peer/user mutation, secret publication or
upstream/GPL code copy was performed.

Phase 7 P7-C002d IP-only public exposure risk guard 2026-06-19: completed as
`blocked-pending-design-or-explicit-risk-acceptance-not-exposed` on disposable
VPS `89.185.80.166`. Evidence
`research/amn2/phase-7-ip-only-public-exposure-risk-guard-b121865-2026-06-19.md`.
Source overlay marker confirmed `b121865f488821f6fc471c9529fb26e5d7992515`.
Runtime stayed loopback-only on `127.0.0.1:3030`; public `3040/80/443`
listeners were absent. Blockers: `ufw_inactive_for_public_exposure`,
`no_reverse_proxy_binary_for_admin_exposure`,
`ip_only_public_admin_has_no_trusted_dns_tls` and
`public_admin_over_ip_requires_explicit_risk_acceptance`.
`ip_only_public_apply_allowed=false`. No service restart, `.env` mutation,
package install, reverse proxy/TLS/firewall apply, public listener change,
public exposure, config delivery, write API, Local Agent mutation,
backup/import/reboot, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

Phase 7 watch-only intake current signals 2026-06-19: completed as docs-only/
watch-only work. Evidence
`research/amn2/phase-7-watch-only-intake-current-signals-2026-06-19.md`.
Current official watch remains `amnezia-vpn/amnezia-client` `4.8.19.0` and
`amneziawg-android` `2.0.1`. PRVTPRO remains upstream idea source only with no
GPL code copy; KYORESUAS remains API taxonomy signal only. Local automation
configs for `prvtpro-weekly-upstream-refresh`, `weekly-kyoresuas-upstream-refresh`
and `amnezia-weekly-upstream-refresh` remain present and unchanged since
2026-06-14; no new local automation output was found. No new AMN2 implementation
task was created. No live VPS command, SSH command, `.env` mutation, package
install, service restart, reverse proxy/TLS/firewall apply, public listener
change, public exposure, config delivery, write API, Local Agent mutation,
backup/import/reboot, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

Phase 7 P7-C002e + watch-only Public URL env reconciliation gate 2026-06-19:
completed as `completed-live-env-reconcile-not-exposed` on disposable VPS
`89.185.80.166`. Evidence
`research/amn2/phase-7-public-url-env-reconciliation-b121865-2026-06-19.md`.
Remote source overlay remains `b121865f488821f6fc471c9529fb26e5d7992515`.
`PUBLIC_BASE_URL`, `PUBLIC_DOMAIN` and `WEB_PUBLIC_BASE_URL` were removed from
live `.env`; safe summary shows each removed once. A rollback copy was created
on VPS and must not be posted because it contains secrets. Post-state safe flags:
`APP_SECRET_KEY=present`, `WEB_ADMIN_USERNAME=present`,
`WEB_ADMIN_PASSWORD_HASH=present`, `WEB_ADMIN_SESSION_SECRET=present`,
`PUBLIC_BASE_URL=missing`, `PUBLIC_DOMAIN=missing`,
`WEB_PUBLIC_BASE_URL=missing`, `VPS_APPLY_ENABLED=false`,
`LOCAL_AGENT_ENABLED=false`. Runtime stayed loopback-only: loopback `/login=200`,
root `/=303`, listener `127.0.0.1:3030`, no listener on `3040`; external probes
to `3030`, `3040`, `80` and `443` returned `000`. No service restart, reverse
proxy, TLS, firewall, public listener, public web/API exposure, config delivery,
write API, Local Agent mutation, backup/import/reboot, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.
The settings probe `app.settings` failure is classified as a verifier-path issue:
remote package has no `app.settings`; runtime probes passed.

Phase 7 watch-only intake current signals 2026-06-18: completed as docs-only/
watch-only work. Evidence
`research/amn2/phase-7-watch-only-intake-current-signals-2026-06-18.md`.
Current official watch remains `amnezia-vpn/amnezia-client` `4.8.19.0` and
`amneziawg-android` `2.0.1`. PRVTPRO remains upstream idea source only with no
GPL code copy; KYORESUAS remains API taxonomy signal only. Local automation
configs for `prvtpro-weekly-upstream-refresh`, `weekly-kyoresuas-upstream-refresh`
and `amnezia-weekly-upstream-refresh` remain present and unchanged since
2026-06-14; no new local automation output was found. No new AMN2 implementation
task was created. No live VPS command, SSH command, `.env` mutation, package
install, service restart, reverse proxy/TLS/firewall apply, public listener
change, public exposure, config delivery, write API, Local Agent mutation,
backup/import/reboot, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

Phase 7 watch-only intake correction 2026-06-18: completed as docs-only/
watch-only work. Evidence
`research/amn2/phase-7-watch-only-intake-correction-2026-06-18.md`. This pass
corrects the watch-only/status hygiene wording that previously recorded obsolete
`amneziawg-android 2.0.0`. Current official GitHub watch keeps
`amnezia-vpn/amnezia-client` `4.8.19.0` and
`amneziawg-android` `2.0.1` as watch-only client compatibility signals. No live
VPS command, SSH command, `.env` mutation, package install, service restart,
reverse proxy/TLS/firewall apply, public listener change, public exposure,
config delivery, write API, Local Agent mutation, backup/import/reboot,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed.

Phase 7 P7-S005 + P7-I012 docs quality audit and IP-only env reconciliation
planning 2026-06-18: completed as docs-only/status work. Evidence
`research/amn2/phase-7-docs-quality-audit-ip-env-reconcile-2026-06-18.md`.
The current workspace is AMN3 evidence repo `barakov-dot/amn3` on `master` at
latest pushed `master`; AMN2 package/source truth remains `barakov-dot/amn2`
`codex-vps-test-prep` at `b121865`. Public URL fields left in live `.env` by
`P7-C002a` are now explicitly treated as inert prerequisite residue after the
later IP-only policy decision. New inactive proposal: `P7-C002e Public URL env
reconciliation gate`, important gated, live `.env` hygiene only, no public
listener/reverse proxy/TLS/firewall/config delivery. No live VPS command, SSH
command, `.env` mutation, package install, service restart, reverse proxy/TLS/
firewall apply, public listener change, public exposure, config delivery, write
API, Local Agent mutation, backup/import/reboot, destructive action, Telegram
action, secret publication or upstream/GPL code copy was performed.

Phase 7 watch-only intake + status hygiene 2026-06-18: completed as
docs-only/watch-only work. Evidence
`research/amn2/phase-7-watch-only-intake-status-hygiene-2026-06-18.md`.
Current official GitHub watch keeps `amnezia-vpn/amnezia-client` `4.8.19.0` as
a client compatibility signal. Its temporary `amneziawg-android 2.0.0` wording
is superseded by the later correction evidence, and current status/navigation
keeps `amneziawg-android 2.0.1` as latest. PRVTPRO remains
upstream idea source only with no GPL code copy; KYORESUAS remains API taxonomy
signal only. Local automation configs remain present and watch-only; no new
automation-generated output newer than the 2026-06-14 Phase 7 intake evidence
was found in the local workspace. `P7-I011` remains canonical: AMN2 uses VPS IP
+ SSH tunnel to loopback web/admin by default, without DNS-domain trusted TLS
cutover. No live VPS command, SSH command, `.env` mutation, package install,
service restart, reverse proxy/TLS/firewall apply, public listener change,
public exposure, config delivery, write API, Local Agent mutation, backup/import/
reboot, destructive action, Telegram action, secret publication or upstream/GPL
code copy was performed.

Phase 7 P7-I011 IP-only exposure policy decision 2026-06-18: completed as
local-only/docs/status work. Evidence
`research/amn2/phase-7-ip-only-exposure-policy-decision-2026-06-18.md`. The
operator explicitly decided not to use a DNS domain for AMN2 and to use only the
VPS IP. Therefore `P7-C002c` DNS/domain/trusted TLS prerequisite is closed as
`operator_declined_dns_domain`. The selected default access policy is VPS IP for
SSH/operator targeting plus loopback web/admin `127.0.0.1:3030` through SSH
tunnel. Public web/admin exposure, trusted TLS cutover, reverse proxy, firewall,
public listener, public API, config delivery and write API remain not opened.
Any future IP-only public web/admin exposure requires a separate exact named
risk-acceptance gate. No live VPS command, SSH command, `.env` mutation, package
install, service restart, reverse proxy/TLS/firewall apply, public listener
change, config delivery, write API, Local Agent mutation, backup/import/reboot,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed.

Phase 7 P7-N005 client compatibility watch refresh for Amnezia client 4.8.19.0
2026-06-18: activated from the requested `P7-C002c + P7-N005` pair and
completed as local-only/docs/tests/watch-only work. Evidence
`research/amn2/phase-7-client-compatibility-watch-refresh-4-8-19-2026-06-18.md`.
`P7-C002c` was not executed live because an exact named live prerequisite gate
and operator-provided DNS FQDN were not supplied; this state was later
superseded by `P7-I011` operator no-domain policy. Current official GitHub
watch keeps `amnezia-vpn/amnezia-client` release `4.8.19.0` as the latest
client-compatibility signal; a later watch-only/status hygiene pass corrected
current `amneziawg-android` wording, and the latest correction keeps `2.0.1`. No
config artifact, QR, `vpn://`, SMTP delivery, public redeem
route, client-secret output, Telegram config send, live VPS command, SSH
command, `.env` mutation, reverse proxy/TLS/firewall apply, public exposure,
write API, Local Agent mutation, backup/import/reboot, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.

Phase 7 P7-C002c + watch-only intake 2026-06-18: DNS/domain/TLS prerequisite
staging and watch-only upstream/client intake completed as
`watch-only-intake-complete-p7-c002c-input-required`. Evidence
`research/amn2/phase-7-dns-domain-tls-prereq-watch-intake-2026-06-18.md`.
`P7-C002c` was not executed live because an exact named live prerequisite gate
and operator-provided DNS FQDN were not supplied. Historical gate phrase at the
time:
`Открываю P7-C002c DNS/domain/TLS prerequisite gate для b121865 на текущем disposable VPS 89.185.80.166.`
Historical inputs at the time: DNS FQDN, HTTPS
`PUBLIC_BASE_URL`, `PUBLIC_DOMAIN`, TLS mode, reverse-proxy kind and
rollback-to-loopback target. Current watch-only intake observed
`amnezia-vpn/amnezia-client` release `4.8.19.0` as a client-compatibility
signal only. A later watch-only/status hygiene pass corrected current
`amneziawg-android` latest-release endpoint observation back to `2.0.1`. Local
upstream-refresh automation configs remain active, with no newer local
automation output found.
No live VPS command, SSH command, `.env` mutation, reverse proxy/TLS/firewall
apply, public exposure, config delivery, write API, Local Agent mutation,
backup/import/reboot, destructive action, Telegram action, secret publication
or upstream/GPL code copy was performed. This DNS-domain input-required state
was later superseded by `P7-I011` operator no-domain policy.

Phase 7 P7-C002 public cutover gate for AMN2 b121865 2026-06-18: opened by
the operator and stopped by read-only guard as
`blocked-by-domain-tls-plan-not-exposed` on disposable VPS `89.185.80.166`.
Evidence `research/amn2/phase-7-public-cutover-guard-b121865-2026-06-18.md`.
Remote source overlay remains `b121865f488821f6fc471c9529fb26e5d7992515`; web
stayed loopback-only on `127.0.0.1:3030`; loopback `/login` returned `200`;
loopback root returned `303`; external probes to `3030`, `3040`, `80` and
`443` returned `000`. Admin credentials and public URL fields were present, but
`PUBLIC_BASE_URL`/`PUBLIC_DOMAIN` were IP-based; guard blocker:
`trusted_tls_requires_dns_domain_not_ip`. Reverse proxy and certbot tooling were
missing. No package install, service restart, `.env` mutation, reverse proxy
apply, TLS issue, firewall change, public listener change, public web/API
exposure, config delivery, write API enablement, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.
`P7-I011` later closed the DNS/domain path by operator policy; `P7-C002d` was
later opened and blocked IP-only exposure. Next default action is
operator-only/watch-only unless a new post-`P7-C002d` risk-design gate is
explicitly opened.

Phase 7 P7-C002b public exposure runtime reload and loopback login verification
for AMN2 b121865 2026-06-18: opened by the operator and completed as
`runtime-login-verified-not-exposed` on disposable VPS `89.185.80.166`.
Evidence
`research/amn2/phase-7-public-exposure-runtime-login-verify-b121865-2026-06-18.md`.
Remote source overlay remains `b121865f488821f6fc471c9529fb26e5d7992515`.
Manual loopback runtime was restarted after `P7-C002a`; the first immediate
HTTP probe hit a short pre-bind readiness window, then recovery showed web
listening on `127.0.0.1:3030`. Final live login flow returned
`GET /login=200`, `POST /login=303`, `Location=/` and dashboard `200`.
Password contract check matched the submitted username/password to the live
`.env` hash without printing secrets. External probes to `3030`, `3040`, `80`
and `443` returned `000`. No reverse proxy apply, TLS issue, firewall change,
public listener change, public web/API exposure, config delivery, write API
enablement, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed. `P7-C002` remains a critical named gate
for a separate exact public cutover gate only.

Phase 7 P7-C002a public exposure admin/domain prerequisite for AMN2 b121865
2026-06-14: opened by the operator and completed as live `.env` admin/domain
prerequisite mutation on disposable VPS `89.185.80.166`. Evidence
`research/amn2/phase-7-public-exposure-admin-domain-prereq-b121865-2026-06-14.md`.
Remote source overlay was `b121865f488821f6fc471c9529fb26e5d7992515`.
Pre-mutation flags showed `WEB_ADMIN_USERNAME=missing`, public base/domain URL
missing and `WEB_ADMIN_PASSWORD_HASH=present`. The gate updated only `.env`
admin/domain fields; post-mutation flags showed `WEB_ADMIN_USERNAME=present`,
`WEB_ADMIN_PASSWORD_HASH=present`, `PUBLIC_BASE_URL=present`,
`PUBLIC_DOMAIN=present`, `WEB_PUBLIC_BASE_URL=present`, `VPS_APPLY_ENABLED=false`
and `LOCAL_AGENT_ENABLED=false`. Verdict:
`public_exposure_precondition_status=ready_for_operator_cutover_plan`, with
`public_exposure_apply_allowed=false`. No service restart, reverse proxy apply,
TLS certificate issue, firewall change, public listener change, public web/API
exposure, config delivery, write API enablement, backup/import/reboot,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed.

Phase 7 P7-C002 public exposure gate for AMN2 b121865 2026-06-14: opened by
the operator and completed as read-only pre-cutover on disposable VPS
`89.185.80.166`, outcome `blocked-by-preconditions`. Evidence
`research/amn2/phase-7-public-exposure-gate-precutover-b121865-2026-06-14.md`.
Remote source overlay was `b121865f488821f6fc471c9529fb26e5d7992515`; web
remained loopback-only on `127.0.0.1:3030`; external probes to `3030`, `3040`,
`80` and `443` returned `000`; reverse proxy binaries/services were absent or
inactive; `ufw` was inactive; `WEB_ADMIN_USERNAME=missing`; public domain/base
URL was missing; `VPS_APPLY_ENABLED=false`; `LOCAL_AGENT_ENABLED=false`. No
reverse proxy install/apply, TLS certificate issue, firewall change, public
listener change, public web/admin exposure, public API exposure, config
delivery, write API enablement, Local Agent mutation, backup/import/reboot,
production peer/user mutation, destructive action, Telegram action, secret
publication or upstream/GPL code copy was performed. Later `P7-C002a` supplied
admin/domain prerequisites and `P7-C002b` verified runtime/login on loopback;
actual public cutover remains a separate critical named gate.

Phase 7 P7-S004 + watch-only intake check + operator named-gate menu review
2026-06-14: completed as docs-only/watch-only work. Evidence
`research/amn2/phase-7-final-freeze-watch-menu-2026-06-14.md`. Phase 7
local-only expansion is now frozen before any named gate. The evidence index
and next-chat handoff show the watch-only intake check and an operator
named-gate menu for `P7-C002`...`P7-C007`. No live VPS command, SSH command,
package upload/apply/rebuild on VPS, service restart/deploy, public exposure,
config delivery, write API enablement, Local Agent mutation, backup/import/
reboot, production peer/user mutation, destructive action, Telegram token use,
live bot send, Telegram profile/media mutation, secret publication or
upstream/GPL code copy was performed.

Phase 7 P7-N004 + watch-only automation/client refresh intake + named-gate dry
checklist review + final RC notes polish 2026-06-14: completed as
local-only/docs/watch-only work. Evidence
`research/amn2/phase-7-evidence-watch-drycheck-rcnotes-2026-06-14.md`. Added
`docs/AMN2_PHASE_7_EVIDENCE_INDEX.ru.md`, recorded that upstream automations
remain watch-only intake, added named-gate dry checklist review and polished
AMN2 `docs/RELEASE_NOTES_RC_SKELETON.ru.md` so `b121865` is the latest
known-good VPS-smoked/package baseline while public/config/write/backup/
destructive/Telegram gates remain unopened. No live VPS command, SSH command,
package upload/apply/rebuild on VPS, service restart/deploy, public exposure,
config delivery, write API enablement, Local Agent mutation, backup/import/
reboot, production peer/user mutation, destructive action, Telegram token use,
live bot send, Telegram profile/media mutation, secret publication or
upstream/GPL code copy was performed.

Phase 7 P7-S003 final RC handoff/status compression 2026-06-14: completed as
AMN3 docs-only work. Evidence
`research/amn2/phase-7-final-rc-handoff-compression-2026-06-14.md`.
`docs/NEXT_CHAT_AMN2_PHASE_7_RELEASE_CANDIDATE.ru.md` is now a compact handoff
with short start block, current state, approved remaining plan, RC Gate Matrix
summary, exact named gate policy and recommendation rhythm. No live VPS
command, SSH command, package upload/apply/rebuild on VPS, service
restart/deploy, public exposure, config delivery, write API enablement, Local
Agent mutation, backup/import/reboot, production peer/user mutation,
destructive action, Telegram token use, live bot send, Telegram profile/media
mutation, secret publication or upstream/GPL code copy was performed.
`P7-S003` is removed from the active Phase 7 plan.

Phase 7 P7-I010 release candidate gate matrix consolidation 2026-06-14:
completed as AMN3 local-only docs/tests work. Evidence
`research/amn2/phase-7-rc-gate-matrix-consolidation-2026-06-14.md`.
`docs/PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md` now contains `RC Gate Matrix`,
which separates completed local-only structural tasks, active critical named
gates, watch-only intake and inactive structural proposals. The matrix maps
`P7-C002`...`P7-C007` to readiness source, current blocker/status and allowed
next action. No live VPS command, SSH command, package upload/apply/rebuild on
VPS, service restart/deploy, public exposure, config delivery, write API
enablement, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram token use, live bot send, Telegram
profile/media mutation, secret publication or upstream/GPL code copy was
performed. `P7-I010` is removed from the active Phase 7 plan.

Phase 7 P7-I009 Telegram identity/profile/media prerequisite checklist
2026-06-14: completed as AMN2 local-only code/tests/docs and AMN3
evidence/status work. Evidence
`research/amn2/phase-7-telegram-identity-readiness-2026-06-14.md`. AMN2 fresh
installer manifest and `/api/integration/status` now expose
`telegram_identity_readiness` with schema
`telegram-identity-profile-media-prerequisite-checklist.v1`, status
`readiness_checklist_ready`, target gate `P7-C007`, Telegram API disabled,
token use disabled, profile mutation disabled, media mutation disabled and live
bot send disabled. Required checklists cover identity scope decision,
credential handoff/storage policy, profile/media asset planning, operator
preview/rollback and post-mutation relock audit. TDD: RED focused `3 failed, 29
passed, 1 StarletteDeprecationWarning`; GREEN focused `32 passed, 1
StarletteDeprecationWarning`; expanded `38 passed, 1 StarletteDeprecationWarning`;
full AMN2 suite `741 passed, 1 StarletteDeprecationWarning`. No live VPS
command, SSH command, package upload/apply/rebuild on VPS, service
restart/deploy, public exposure, config delivery, write API enablement, Local
Agent mutation, backup/import/reboot, production peer/user mutation,
destructive action, Telegram token use, live bot send, Telegram profile/media
mutation, secret publication or upstream/GPL code copy was performed. `P7-I009`
is removed from the active Phase 7 plan.

Phase 7 P7-I008 backup/restore/import prerequisite checklist 2026-06-14:
completed as AMN2 local-only code/tests/docs and AMN3 evidence/status work.
Evidence `research/amn2/phase-7-backup-restore-import-readiness-2026-06-14.md`.
AMN2 fresh installer manifest and `/api/integration/status` now expose
`backup_restore_import_readiness` with schema
`backup-restore-import-prerequisite-checklist.v1`, status
`readiness_checklist_ready`, target gate `P7-C006`, live backup disabled,
restore apply disabled, archive import disabled and reboot disabled. Required
checklists cover backup scope, encryption/retention policy, restore preview
safety, import source validation and disaster-recovery drill planning. TDD: RED
focused `3 failed, 27 passed, 1 StarletteDeprecationWarning`; GREEN focused
`30 passed, 1 StarletteDeprecationWarning`; expanded `36 passed, 1
StarletteDeprecationWarning`; full AMN2 suite `739 passed, 1
StarletteDeprecationWarning`. No live VPS command, SSH command, package
upload/apply/rebuild on VPS, service restart/deploy, public exposure,
config delivery, write API enablement, Local Agent mutation, backup archive
create, restore apply, archive import apply, reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed. `P7-I008` is removed from the active
Phase 7 plan.

Phase 7 P7-I007 write API scope/implementation decision 2026-06-14: completed
as AMN2 local-only code/tests/docs and AMN3 evidence/status work. Evidence
`research/amn2/phase-7-write-api-scope-decision-2026-06-14.md`. AMN2 fresh
installer manifest and `/api/integration/status` now expose
`write_api_scope_decision` with schema `write-api-scope-decision.v1`, status
`decision_ready`, target gate `P7-C005` and selected RC policy
`keep_public_api_read_only_for_rc`. Write API, public write routes, Local Agent
mutation and production peer/user mutation remain disabled; deferred options
require `P7-C005`. TDD: RED focused `3 failed, 25 passed, 1
StarletteDeprecationWarning`; GREEN focused `28 passed, 1
StarletteDeprecationWarning`; expanded `34 passed, 1 StarletteDeprecationWarning`;
full AMN2 suite `737 passed, 1 StarletteDeprecationWarning`. No live VPS
command, SSH command, package
upload/apply/rebuild on VPS, service restart/deploy, public exposure, config
delivery, write API enablement, Local Agent mutation, backup/import/reboot,
production peer/user mutation, destructive action, Telegram action, secret
publication or upstream/GPL code copy was performed. `P7-I007` is removed from
the active Phase 7 plan.

Phase 7 P7-I006 config delivery channel readiness 2026-06-14: completed as
AMN2 local-only code/tests/docs and AMN3 evidence/status work. Evidence
`research/amn2/phase-7-config-delivery-channel-readiness-2026-06-14.md`. AMN2
fresh installer manifest and `/api/integration/status` now expose
`config_delivery_channel_readiness` with schema
`config-delivery-channel-readiness.v1`, status `readiness_design_ready`, target
gate `P7-C003`, live delivery disabled and checklists for SMTP/operator-local
channel decision, secret-safe evidence protocol, client import matrix, one-time
delivery policy and delivery revocation story. API/rendered-plan views redact
exact forbidden evidence marker names to count/policy while the local manifest
keeps the full validation contract. TDD: RED focused `3 failed, 23 passed, 1
StarletteDeprecationWarning`; GREEN focused `26 passed, 1
StarletteDeprecationWarning`; expanded `32 passed, 1 StarletteDeprecationWarning`;
full AMN2 suite `735 passed, 1 StarletteDeprecationWarning`. No live VPS
command, SSH command, package upload/apply/rebuild on VPS, service
restart/deploy, public exposure, config delivery, write API enablement, Local
Agent mutation, backup/import/reboot, production peer/user mutation,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed. `P7-I006` is removed from the active Phase 7 plan.

Phase 7 P7-I005 public exposure readiness/design 2026-06-14: completed as AMN2
local-only code/tests/docs and AMN3 evidence/status work. Evidence
`research/amn2/phase-7-public-exposure-readiness-design-2026-06-14.md`. AMN2
fresh installer manifest and `/api/integration/status` now expose
`public_exposure_readiness_design` with schema
`public-exposure-readiness-design.v1`, status `readiness_design_ready`, target
gate `P7-C002`, live exposure disabled and checklists for admin credential
contract, domain/TLS/reverse-proxy plan, firewall/listener plan, external probe
matrix and rollback-to-loopback. Blocked actions remain public listener change,
firewall apply, reverse proxy apply, TLS certificate issue, public OpenAPI
publication and direct public API `3040`. TDD: RED focused `3 failed, 21
passed, 1 StarletteDeprecationWarning`; GREEN focused `24 passed, 1
StarletteDeprecationWarning`; expanded `30 passed, 1 StarletteDeprecationWarning`.
No live VPS command, SSH command, package upload/apply/rebuild on VPS, service
restart/deploy, public exposure, config delivery, write API enablement, Local
Agent mutation, backup/import/reboot, production peer/user mutation,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed. `P7-I005` is removed from the active Phase 7 plan.

Phase 7 P7-I004 public/config/write prerequisite split 2026-06-14: completed
as AMN2 local-only code/tests/docs and AMN3 evidence/status work. Evidence
`research/amn2/phase-7-public-config-write-prerequisite-split-2026-06-14.md`.
AMN2 fresh installer manifest and `/api/integration/status` now expose
`public_config_write_prerequisite_split` with schema
`public-config-write-prerequisite-split.v1`, status
`blocked_by_preconditions`, source evidence
`research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md`,
and three readiness tracks: `P7-C002` public exposure readiness, `P7-C003`
config delivery channel readiness and `P7-C005` write API scope decision.
Blocked actions remain public listener changes, domain/TLS/reverse proxy apply,
config artifact output, write route enablement, `VPS_APPLY_ENABLED=true`, Local
Agent mutation and live peer/user mutation. TDD: RED focused `3 failed, 19
passed, 1 StarletteDeprecationWarning`; GREEN focused `22 passed, 1
StarletteDeprecationWarning`; expanded `28 passed, 1 StarletteDeprecationWarning`.
No live VPS command, SSH command, package upload/apply/rebuild on VPS, service
restart/deploy, public exposure, config delivery, write API enablement, Local
Agent mutation, backup/import/reboot, production peer/user mutation,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed. `P7-I004` is removed from the active Phase 7 plan.

Phase 7 P7-C002 + P7-C003 + P7-C005 public/config/write preflight for AMN2
b121865 2026-06-14: completed on disposable VPS `89.185.80.166` as
`blocked-by-preconditions`. Evidence
`research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md`.
Remote source overlay was `b121865f488821f6fc471c9529fb26e5d7992515`; web
remained loopback-only on `127.0.0.1:3030`; loopback `/login` returned `200`;
external probes to `3030`, `3040`, `80` and `443` returned `000`. Safe env
summary showed `WEB_ADMIN_USERNAME=missing`, SMTP config missing,
`VPS_APPLY_ENABLED=false` and `LOCAL_AGENT_ENABLED=false`. Public API route
inventory was read-only with `write_api_route_count=0`; web admin local
operator write/config routes were inventoried but not invoked. Gate did not
perform public exposure, domain/TLS/reverse proxy/firewall change, public
OpenAPI publication, config delivery, `.conf`, QR, `vpn://`, write API route
enablement, `/api/clients` CRUD, Local Agent mutation, `VPS_APPLY_ENABLED=true`,
live peer/user mutation, backup/import/reboot, destructive action,
secret-bearing evidence publication or upstream/GPL code copy. This historical
preflight was later superseded for `P7-C005` by the 2026-06-20 scoped write
contour on `5501295`; `P7-C002` and future `P7-C003` scopes remain separate
exact gates with explicit blockers.

Phase 7 P7-C001 live package/apply/smoke for AMN2 b121865 2026-06-14:
completed on disposable VPS `89.185.80.166` as `live-update-smoke-pass`.
Evidence `research/amn2/phase-7-live-update-smoke-b121865-2026-06-14.md`.
Package `dist/amn2-vps-update-and-smoke-kit-b121865.zip`, sha256
`364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849`, was
uploaded, remote checksum-verified and applied as a source overlay. Remote
source commit is `b121865f488821f6fc471c9529fb26e5d7992515`;
`source_update_status=passed`; API loopback smoke returned `VPS verdict: pass`;
auth/listener/audit passed; negative auth checks returned `401/403/401`; API
listener was loopback-only on `127.0.0.1:3040`; web login returned `200` on
loopback `127.0.0.1:3030`; external probes to `3030`, `3040`, `80` and `443`
returned `000`. `P7-C001` is removed from the active Phase 7 plan. Latest
VPS-smoked/package head is now `b121865`; previous known-good `0de7a77` remains
history/rollback evidence. Gate did not perform public exposure, config
delivery, write API production opening, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive action,
Telegram identity/profile/media mutation, secret-bearing evidence publication
or upstream/GPL code copy.

Phase 7 P7-S001 next-chat/status hygiene 2026-06-14: completed as AMN3
docs-only work. Evidence
`research/amn2/phase-7-next-chat-status-hygiene-2026-06-14.md`. Phase 7
handoff/status/backlog/context/transfer docs showed that the default local-only
RC readiness queue was closed. After `P7-C001`, active Phase 7 work is limited
to critical named gates `P7-C002` through `P7-C007` and watch-only monitoring.
No live VPS command, SSH command, package upload/apply on VPS, service
restart/deploy, public exposure, public OpenAPI publication, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

Phase 7 P7-N001 + P7-N003 + P7-X001 automation intake, client compatibility
watch refresh and clean installer operator copy polish 2026-06-14: completed
as AMN2 local-only code/tests/docs and AMN3 evidence/status work. Evidence
`research/amn2/phase-7-automation-client-watch-copy-polish-2026-06-14.md`.
Weekly upstream-refresh automations remain intake-only signals; AMN2 now
exposes `CLIENT_COMPATIBILITY_WATCH` through integration status without opening
config delivery; clean installer prompts are Russian-first while stable answer
values remain unchanged. TDD: RED focused returned one expected import error,
GREEN focused `10 passed, 1 StarletteDeprecationWarning`, expanded `68 passed,
1 StarletteDeprecationWarning`, final full AMN2 suite `729 passed, 1
StarletteDeprecationWarning`. No live VPS command, SSH command, package
upload/apply on VPS, service restart/deploy, public exposure, public OpenAPI
publication, config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.

Phase 7 P7-M003 + P7-N002 + P7-S002 multi-instance/IPAM incorporation,
API/docs taxonomy RC drift check and release notes skeleton 2026-06-14:
completed as AMN2 local-only code/tests/docs and AMN3 evidence/status work.
Evidence
`research/amn2/phase-7-multi-instance-taxonomy-release-notes-2026-06-14.md`.
AMN2 fresh installer now exposes `multi_instance_ipam_rc_decision`, rendered
plans include `multi-instance-ipam-rc-decision`, integration status exposes
`api_docs_taxonomy_rc_drift_check`, and AMN2 docs include
`docs/RELEASE_NOTES_RC_SKELETON.ru.md` without declaring a public release.
TDD: RED focused `3 failed, 15 passed, 1 StarletteDeprecationWarning`, GREEN
focused `18 passed, 1 StarletteDeprecationWarning`, expanded `56 passed, 1
StarletteDeprecationWarning`, final full AMN2 suite `728 passed, 1
StarletteDeprecationWarning`. No live VPS command, SSH command, package
upload/apply on VPS, service restart/deploy, public exposure, public OpenAPI
publication, config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.

Phase 7 P7-I002 + P7-M002 + P7-I003 clean installer RC checklist/security
contract 2026-06-14: completed as AMN2 local-only code/tests/docs and AMN3
evidence/status work. Evidence
`research/amn2/phase-7-clean-installer-rc-checklist-security-contract-2026-06-14.md`.
AMN2 fresh installer now exposes `clean_installer_rc_acceptance` schema
`clean-installer-rc-acceptance.v1`, Phase 7 stop-lines/gate IDs, package
asset/runbook path verification for the `b121865` package, package-local helper
default binding checks and `secret_input_contract` with field-only
secret-bearing answer rejection. TDD: RED focused `6 failed, 10 passed`, GREEN
focused `16 passed`, expanded `52 passed`, regression verification `17 passed,
1 StarletteDeprecationWarning`, final full AMN2 suite `727 passed, 1
StarletteDeprecationWarning`. A full-suite regression was found and fixed: safe
metadata category names initially contained forbidden marker words `private` and
`authorization`; category names were changed without weakening the
integration-status forbidden-marker test. No live VPS command, SSH command,
package upload/apply on VPS, service restart/deploy, public exposure, public
OpenAPI publication, config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.

Phase 7 P7-I001 + P7-M001 current-head package/preflight for AMN2 b121865
2026-06-14: completed as AMN3 local-only package/preflight work. Evidence
`research/amn2/phase-7-current-head-package-preflight-b121865-2026-06-14.md`.
Built `dist/amn2-vps-update-and-smoke-kit-b121865.zip`, sha256
`364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849`, from source
zip `dist/amn2-codex-vps-test-prep-b121865-source.zip`, sha256
`D0FB561D5A12C3B2C095521C3B44923B001F49C8E94CA5C13DB1E811ABB17647`. Package
hygiene passed with `kit_entries=5`, `source_entries=300`,
`forbidden_source_entries=0`, shell scripts LF/no-BOM, operator doc markdown
hygiene, checksum files and test-extract. Verification: AMN2 focused RC suite
`56 passed, 1 StarletteDeprecationWarning`, full AMN2 suite `724 passed, 1
StarletteDeprecationWarning`, AMN3 package/apply-script and markdown hygiene
tests `4 tests OK`. Package-local helper defaults are bound to the `b121865`
source zip, source SHA256 and expected commit. At that step known-good
VPS-smoked/package baseline remained `0de7a77`; this was later superseded by
`P7-C001`. No live VPS command, SSH command,
package upload/apply on VPS, service restart/deploy, public exposure, public
OpenAPI publication, config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.

After Phase 6 automation intake audit + upstream refresh aggregation plan
2026-06-14: completed as AMN3 local-only/docs-only work. Evidence
`research/amn2/after-phase-6-automation-intake-audit-plan-2026-06-14.md`.
Created `docs/AMN2_AUTOMATION_INTAKE_AGGREGATION_PLAN.ru.md` to normalize
weekly upstream-refresh outputs before Phase 6 final closeout. The plan keeps
PRVTPRO, KYORESUAS and Amnezia as separate heartbeat automations, records the
current AMN2 thread as the decision lane, defines the required intake card,
priority/gate labels and `missing-input` handling, and says not to close Phase 6
final closeout until automation intake evidence exists. Slice не выполнял live
VPS command, SSH command, package rebuild/apply on VPS, service restart/deploy,
public exposure, config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive action,
Telegram action, secret-bearing evidence publication or upstream/GPL code copy.

Phase 6 P6-C010 live update/smoke for AMN2 0de7a77 2026-06-14: completed on
the disposable test VPS `89.185.80.166` as `live-update-smoke-pass`. Evidence
`research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md`. Package
`dist/amn2-vps-update-and-smoke-kit-0de7a77.zip`, sha256
`7B6DA000DAA39DD15A4DB7C3691D0B0C24EAA20ACB1C428150C6961B01E6F85B`, was
uploaded, checksum-verified and extracted. Source overlay updated `/opt/amn2`
to `0de7a77f3eb09d23dc2785d402bc51c2b5eb7835`; source update run_id
`20260614T062734Z` passed. The manual web/bot runtime was minimally restarted
and web remained bound to `127.0.0.1:3030`. Read-only API smoke on temporary
loopback `127.0.0.1:3040` passed with run_id `20260614T063327Z`,
auth/listener/audit `passed`, and negative auth checks `401/403/401`. Final
listener snapshot showed only `127.0.0.1:3030`, with `3040/80/443` absent;
external probes returned `000`; `VPS_APPLY_ENABLED=false` remained explicit.
Gate не выполнял public exposure change, config delivery, write API production
opening, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive cleanup/reinstall, provider-side destructive action,
Telegram identity/profile mutation, live bot send by Codex, secret-bearing
evidence publication or upstream/GPL code copy. `P6-C010` removed from active
Phase 6 plan. Latest VPS-smoked/package head is now `0de7a77`.

After Phase 6 next-chat handoff refresh + live gate checklist grooming for
0de7a77 2026-06-14: completed as AMN3 docs-only/local-only work. Evidence
`research/amn2/after-phase-6-next-chat-live-gate-checklist-0de7a77-2026-06-14.md`.
The handoff now records `0de7a77` as package-ready-not-vps-smoked, `c46f664` as
latest VPS-smoked head, the exact future gate phrase
`Открываю P6-C010 live apply/smoke gate для 0de7a77 на текущем disposable VPS 89.185.80.166.`,
package/source checksums, stop criteria and forbidden surfaces. Slice не
выполнял live VPS command, SSH command, package upload/apply on VPS, service
restart/deploy, public exposure, real config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive VPS
action, Telegram token use, live bot send, Telegram identity/profile mutation,
secret-bearing evidence publication or upstream/GPL code copy. `P6-C010`
remains closed until the exact named gate phrase is given.

After Phase 6 local package build/preflight for 0de7a77 2026-06-14: completed
as AMN3 local package work. Evidence
`research/amn2/after-phase-6-package-preflight-0de7a77-2026-06-14.md`. Built
`dist/amn2-vps-update-and-smoke-kit-0de7a77.zip`, sha256
`7B6DA000DAA39DD15A4DB7C3691D0B0C24EAA20ACB1C428150C6961B01E6F85B`, from
source zip `dist/amn2-codex-vps-test-prep-0de7a77-source.zip`, sha256
`B8D0E7E2A40051AB38EDF09947977DFE5F7197CEEEE87D1523734D3C1C505295`. Package
hygiene passed with `kit_entries=5`, `source_entries=342`,
`forbidden_source_entries=0`, shell scripts LF/no-BOM, operator doc markdown
hygiene, package checksum and test-extract. Verification: full AMN2 suite `721
passed, 1 StarletteDeprecationWarning`; AMN3 package/apply-script and markdown
hygiene tests `4 tests OK`; `git diff --check` passed. Slice не выполнял live
VPS command, SSH command, package upload/apply on VPS, service restart/deploy,
public exposure, real config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive VPS action,
Telegram token use, live bot send, Telegram identity/profile mutation,
secret-bearing evidence publication or upstream/GPL code copy. AMN2 `0de7a77`
is package-ready-not-vps-smoked; latest VPS-smoked head remains `c46f664`. Next
recommendation: next-chat handoff refresh, or a separate named live apply/smoke
gate for `0de7a77` if the operator chooses.

After Phase 6 FI-X001 + current-head package preflight planning 2026-06-14:
completed as AMN2 local-only code/tests/docs in commit `0de7a77 Polish fresh
installer preflight planning`, pushed to `amn2/codex-vps-test-prep`. Evidence
`research/amn2/after-phase-6-fresh-installer-copy-package-preflight-2026-06-14.md`.
The slice changes fresh installer prompts to Russian-first copy while preserving
stable technical IDs, adds `fresh-install-package-preflight.v1`, records target
preflight head `ff77d4c`, latest VPS-smoked head `c46f664`, and keeps package
build, live apply and live smoke disabled by default. Verification: RED `3
failed, 9 passed`, focused `12 passed`, full AMN2 suite `721 passed, 1
StarletteDeprecationWarning`, `git diff --check` and staged checks passed. Slice
не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service
restart/deploy, public exposure, real config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive VPS
action, Telegram token use, live bot send, Telegram identity/profile mutation,
secret-bearing evidence publication or upstream/GPL code copy. Latest
VPS-smoked/package head remains `c46f664`; AMN2 `0de7a77` is local-only and not
package-rebuilt/VPS-smoked. Next recommendation: local package build/preflight
for `0de7a77` without live apply/smoke, or a separate named live gate if the
operator chooses.

After Phase 6 P6-C001 + P6-C002 docs-only checklist refresh 2026-06-13:
completed as AMN2 local-only code/tests/docs in commit `ff77d4c Add public
config gate checklist`, pushed to `amn2/codex-vps-test-prep`. Evidence
`research/amn2/after-phase-6-public-config-gate-checklist-refresh-2026-06-13.md`.
The slice adds `docs/PUBLIC_CONFIG_GATE_CHECKLIST.ru.md` and
`build_public_config_gate_checklist()`, keeps `public_exposure_enabled=false`
and `config_delivery_enabled=false`, and blocks public listener exposure, public
OpenAPI publication, short config-link issue/redeem, QR, VPN import link,
`.conf`, Telegram live config send and Local Agent config mutation without the
correct named gate. Verification: focused `4 passed`, full AMN2 suite `720
passed, 1 StarletteDeprecationWarning`, `git diff --check` passed. Slice не
выполнял live VPS command, SSH command, package apply/rebuild on VPS, service
restart/deploy, public exposure, real config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive VPS
action, Telegram token use, live bot send, Telegram identity/profile mutation,
secret-bearing evidence publication or upstream/GPL code copy. `P6-C001` and
`P6-C002` remain critical gated/deferred for actual public exposure and actual
config delivery. Latest VPS-smoked/package head remains `c46f664`; AMN2
`ff77d4c` is local-only and not package-rebuilt/VPS-smoked. Next recommendation:
`FI-X001 + current-head package preflight planning for ff77d4c` as local-only
docs/tests/package hygiene, without live apply.

After Phase 6 FI-N001 + FI-N002 + FI-S001 fresh installer evidence readiness
2026-06-13: completed as AMN2 local-only code/tests/docs in commit `525a9cd
Add fresh installer evidence readiness`, pushed to `amn2/codex-vps-test-prep`.
Evidence `research/amn2/after-phase-6-fresh-installer-evidence-readiness-2026-06-13.md`.
The slice adds `fresh-install-evidence.v1`, smoke/evidence template,
report-only existing-server reconciliation input and
`docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md`. Verification: RED `3 failed, 8
passed`, focused `13 passed`, full AMN2 suite `719 passed, 1
StarletteDeprecationWarning`, `git diff --check` and staged check passed. Slice
не выполнял live VPS command, SSH command, live smoke execution, package
apply/rebuild on VPS, service restart/deploy, public exposure, real config
delivery, write API, Local Agent mutation, backup/import/reboot, production
peer/user mutation, destructive VPS action, Telegram token use, live bot send,
Telegram identity/profile mutation, secret-bearing evidence publication or
upstream/GPL code copy. `FI-N001`, `FI-N002` and `FI-S001` removed from the
active recommendation. Latest VPS-smoked/package head remains `c46f664`; AMN2
`525a9cd` is local-only and not package-rebuilt/VPS-smoked. Next
operator-requested item: `P6-C001 + P6-C002` docs-only checklist refresh,
without opening public/config gates.

After Phase 6 FI-M001 + FI-M002 + FI-M003 fresh installer readiness planning
2026-06-13: completed as AMN2 local-only code/tests/docs in commit `7416fb0
Add fresh installer readiness planning`, pushed to `amn2/codex-vps-test-prep`.
Evidence `research/amn2/after-phase-6-fresh-installer-readiness-planning-2026-06-13.md`.
The slice adds `fresh-install-readiness.v1`, target preflight matrix, runtime
mode decision and package hygiene checklist to the existing fresh installer
plan. Verification: RED `2 failed, 6 passed`, focused `10 passed`, full AMN2
suite `716 passed, 1 StarletteDeprecationWarning`, `git diff --check` and staged
check passed. Slice не выполнял live VPS command, SSH command, target diagnostic
execution, package apply/rebuild on VPS, service restart/deploy, public
exposure, real config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive VPS action,
Telegram token use, live bot send, Telegram identity/profile mutation,
secret-bearing evidence publication or upstream/GPL code copy. `FI-M001`,
`FI-M002` and `FI-M003` removed from the active recommendation. Latest
VPS-smoked/package head remains `c46f664`; AMN2 `7416fb0` is local-only and not
package-rebuilt/VPS-smoked. Next recommendation: `FI-N001 + FI-N002 + FI-S001`
as local-only docs/test evidence readiness.

After Phase 6 FI-I001 + FI-I002 + FI-I003 fresh installer plan renderer
2026-06-13: completed as AMN2 local-only code/tests/docs in commit `de635a0
Add fresh installer plan renderer`, pushed to `amn2/codex-vps-test-prep`.
Evidence `research/amn2/after-phase-6-fresh-installer-plan-renderer-2026-06-13.md`.
The slice adds `build_fresh_install_manifest()`, versioned question/answer
schemas, `fresh-install-plan.v1`, rendered plan phases, required named-gate
mapping for `P6-C001`/`P6-C002`/`P6-C003`/`P6-C007`, secret handoff protocol
binding and the Windows/Codex Desktop `scripts/test.ps1` runner. Verification:
RED missing manifest/doc tests, focused `8 passed`, full AMN2 suite `714 passed,
1 StarletteDeprecationWarning`, `git diff --cached --check` passed. Slice не
выполнял live VPS command, SSH command, package apply/rebuild on VPS, service
restart/deploy, public exposure, real config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive VPS
action, Telegram token use, live bot send, Telegram identity/profile mutation,
secret-bearing evidence publication or upstream/GPL code copy. `FI-I001`,
`FI-I002` and `FI-I003` removed from the active recommendation. Latest
VPS-smoked/package head remains `c46f664`; AMN2 `de635a0` is local-only and not
package-rebuilt/VPS-smoked. Next recommendation: `FI-M001 + FI-M002 + FI-M003`
as local-only preflight/runtime/package planning.

Phase 6 P6-S004 closeout packet + next-chat handoff + fresh installer backlog grooming 2026-06-13: completed as AMN3 docs-only work. Evidence `research/amn2/phase-6-closeout-next-chat-fresh-installer-backlog-2026-06-13.md`. Added `docs/NEXT_CHAT_AMN2_AFTER_PHASE_6.ru.md` and `docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md`, synchronized Phase 6 handoff/status/context/backlog, closed the Phase 6 default lane and organized future clean-installer work under candidate `FI-*` IDs. Public/self-service launch remains not opened; remaining work is gated/deferred: `P6-C001`, `P6-C002`, `P6-C003`, `P6-C004`, `P6-C007`, `VPS-REBUILD-001`, Local Agent write/config routes, production peer/user mutation and carried `P4-PRVTPRO-REFRESH-003-LIVE`. Its recommended local-only bundle `FI-I001 + FI-I002 + FI-I003` was completed after Phase 6 in AMN2 `de635a0`; the current recommendation is `FI-M001 + FI-M002 + FI-M003`. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, Telegram token use, live bot send, Telegram identity mutation, secret-bearing evidence publication or upstream/GPL code copy.

Phase 6 P6-X003 package runbook escaping hygiene 2026-06-13: completed as AMN3 local-only docs/tooling hygiene. Evidence `research/amn2/phase-6-package-runbook-escaping-hygiene-2026-06-13.md`. Added `scripts/check_markdown_hygiene.py` and `tests/test_markdown_hygiene.py` to catch accidental ASCII control characters in generated Markdown/operator docs, including PowerShell backtick escape accidents. Verification: RED `python -m unittest tests.test_markdown_hygiene` failed while the tool was missing; GREEN returned `2 tests OK`; diagnostic run against the already-smoked unpacked `c46f664` operator doc failed with five expected findings. The already-smoked `c46f664` zip/package artifact was not rebuilt, repacked or altered. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, Telegram token use, live bot send, Telegram identity mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-X003` removed from active Phase 6 plan.

Phase 6 P6-C009 live update/smoke for AMN2 c46f664 2026-06-13: completed on the disposable test VPS as `live-update-smoke-pass`. Evidence `research/amn2/phase-6-live-update-smoke-c46f664-2026-06-13.md`; package preflight evidence `research/amn2/phase-6-current-head-package-preflight-c46f664-2026-06-13.md`. Package upload/checksum/extract passed; source overlay updated `/opt/amn2` from `b3102db250da7ca9aef78ca095602187d0efc462` to `c46f664762d7774756b88db8d4e1ebc038b20bb5`; source update run_id `20260613T173232Z` passed; manual web/bot runtime was restarted with web bound to `127.0.0.1:3030`; read-only API smoke run_id `20260613T173738Z` passed with auth/listener/audit `passed`. Final remote listener snapshot showed only `127.0.0.1:3030`, with `3040/80/443` absent; external probes returned `000`; `VPS_APPLY_ENABLED=false` remained explicit. Gate не выполнял config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, public exposure change, Telegram token use by Codex, live bot send, Telegram identity mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-C009` removed from active Phase 6 plan. Latest VPS-smoked/package head is now `c46f664`. Follow-up added: `P6-X003` package runbook escaping hygiene.

Phase 6 P6-C008 current-head package refresh/preflight for AMN2 c46f664 2026-06-13: completed as AMN3 local package work with current-head smoke plan and named live gate checklist. Evidence `research/amn2/phase-6-current-head-package-preflight-c46f664-2026-06-13.md`. Built `dist/amn2-vps-update-and-smoke-kit-c46f664.zip`, package sha256 `5C952103B3435E1D30AF7CF0A70C40BC027885F1E860C31089DD4ACA3E8347EE`, from source zip `dist/amn2-codex-vps-test-prep-c46f664-source.zip`, source sha256 `5A92EA9BD5B60626F120B5367A02EDDCB742ECF5E6C4FCB8444151BFEB18B248`. Package hygiene passed with `kit_entries=5`, `source_entries=337`, `forbidden_source_entries=0`, shell scripts LF/no-BOM and commit bindings present; AMN2 focused suite returned `11 passed, 1 StarletteDeprecationWarning`; AMN2 toolchain check passed; AMN3 apply-script regression returned `2 tests OK`. Slice не выполнял live VPS command, SSH command, package upload/apply on VPS, source overlay on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, Telegram token use, live bot send, Telegram identity mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-C008` removed from active Phase 6 plan. `c46f664` is package-ready locally and not VPS-smoked; latest VPS-smoked/package head remains `b3102db`. Future live apply/smoke is tracked as `P6-C009`, critical gated/deferred, requiring exact phrase: `Открываю P6-C009 live apply/smoke gate для c46f664 на текущем disposable VPS 89.185.80.166.`

Phase 6 P6-N001 public docs/API taxonomy + P6-C007 checklist-only 2026-06-13: completed as AMN2 local-only code/tests/docs in commit `c46f664 Add public taxonomy cleanup checklist`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-6-public-taxonomy-cleanup-checklist-2026-06-13.md`. The slice adds `app.services.public_productization_boundaries`, docs `docs/PUBLIC_DOCS_API_TAXONOMY.ru.md` and `docs/DESTRUCTIVE_CLEANUP_GATE_CHECKLIST.ru.md`, and API/web integration-status visibility. Public docs/API publication flags remain disabled and require `P6-C001`; destructive cleanup/reinstall execution flags remain disabled and require a separate named `P6-C007` gate with retention/data-loss decision, stop criteria and second confirmation. Verification: focused `11 passed, 1 StarletteDeprecationWarning`, security/hygiene `26 passed`, toolchain check passed, `git diff --check` and staged check passed. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, real config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, payment provider integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-N001` removed from active Phase 6 plan. `P6-C007` remains critical gated/deferred. AMN2 current head `c46f664` is local-only and not package-rebuilt/VPS-smoked; latest VPS-smoked/package head remains `b3102db`. Next recommendation: `P6-C008` current-head package refresh/preflight for `c46f664`, or a separately named live/public/destructive gate if the operator chooses.

Phase 6 P6-I007 fresh-install wizard/bootstrap automation 2026-06-13: completed as AMN2 local-only code/tests/docs in commit `60d2570 Add fresh install wizard boundary`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-6-fresh-install-wizard-boundary-2026-06-13.md`. The slice adds `app.services.fresh_install_wizard`, CLI commands `install wizard` and `install plan`, docs `docs/FRESH_INSTALL_WIZARD.ru.md`, and API/web integration-status visibility. Wizard output is `local_only_dry_run`; public/config/write/destructive `yes` answers become stop-lines for `P6-C001`, `P6-C002`, `P6-C003` and `P6-C007`; live VPS commands, SSH, package apply, restart/deploy, public exposure, real config delivery, write API, Local Agent mutation, backup/restore/import apply, production peer/user mutation, destructive cleanup and Telegram identity mutation remain disabled. Verification: RED `2 import errors as expected`, focused `14 passed, 1 StarletteDeprecationWarning`, security/hygiene `26 passed`, toolchain check passed, `git diff --check` and staged check passed. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, real config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, payment provider integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-I007` removed from active Phase 6 plan. `P6-C007` remains critical gated/deferred. AMN2 current head `60d2570` is local-only and not package-rebuilt/VPS-smoked; latest VPS-smoked/package head remains `b3102db`. Its next recommendation was completed by `P6-N001` + `P6-C007` checklist-only.

Phase 6 P6-C002-design + P6-I006 config-link/entitlement boundary 2026-06-13: completed as AMN2 local-only code/tests/docs in commit `d96112c Add config link entitlement boundary`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-6-config-link-entitlement-boundary-2026-06-13.md`. The slice adds a tokenized config-link boundary with real runtime/config delivery disabled by default, opaque random token, hash-at-rest storage, return-once raw token rule, purpose/audience binding, one-time 15 minute TTL and Telegram one-tap copy constraints; adds commercial entitlement/audit boundary with payment provider disabled, entitlement write API disabled, automatic activation disabled, config delivery decoupled from payment and manual review required; adds blocked-future policies for `api.entitlements.manual_review.blocked`, `api.config_links.issue.blocked` and `public_token.config_link.redeem.blocked`; updates API/web integration status to latest VPS-smoked head `b3102db` and next local recommendation `P6-I007`. Verification: initial system Python run failed because pytest was unavailable, Python 3.14 with `.codex_deps` failed because binary wheels target CPython 3.12, final bundled CPython 3.12.13 run returned `37 passed, 1 StarletteDeprecationWarning`; `git diff --check` passed. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, real config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, payment provider integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-I006` removed from active/proposed Phase 6 plan. `P6-C002` remains critical gated/deferred for real config delivery, public token redeem, token issue runtime and secret-bearing config output. AMN2 current head `d96112c` is local-only and not package-rebuilt/VPS-smoked; latest VPS-smoked/package head remains `b3102db`.

Phase 6 operator proposal 2026-06-13: added `P6-I007` Interactive fresh-install wizard/bootstrap automation as a very-important local-only task and `P6-C007` Destructive cleanup/reinstall gate for the current working VPS as critical gated/deferred work. The current working server was identified by the operator as `89.185.80.166`. `P6-I007` should create a future clean-install path through question-and-answer prompts, safe defaults, preflight validation, dry-run output, operator-provided secrets and no live/destructive execution by default. `P6-C007` must not run until the operator explicitly decides to assemble/test the clean installer, and must require a separate named destructive gate, explicit retention/data-loss decision and stop criteria. No live VPS command, SSH command, cleanup, reinstall, package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, Telegram action, secret publication or upstream/GPL code copy was performed by adding this plan item.

Phase 6 P6-C006 live update/smoke for AMN2 b3102db 2026-06-13: completed on the disposable test VPS as `live-update-smoke-pass`. Evidence `research/amn2/phase-6-live-update-smoke-b3102db-2026-06-13.md`; package preflight evidence `research/amn2/phase-6-final-vps-refresh-package-b3102db-2026-06-13.md`. Package upload/checksum/extract passed; source overlay updated `/opt/amn2` from `2215761` to `b3102db250da7ca9aef78ca095602187d0efc462`; source update run_id `20260613T154511Z` passed; manual web/bot runtime was restarted with web bound to `127.0.0.1:3030`; read-only API smoke run_id `20260613T154826Z` passed with auth/listener/audit `passed`. A first smoke attempt was blocked because the default server name `debian-vps-1` was absent and this target uses `local`; the successful smoke explicitly used `AMN2_SERVER_NAME=local`. Final remote listener snapshot showed only `127.0.0.1:3030`, with `3040/80/443` absent; external probes returned `000`; `VPS_APPLY_ENABLED=false` remained explicit. Gate не выполнял config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, public exposure change, Telegram token use by Codex, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-C006` removed from active Phase 6 plan. Next recommendation: `P6-C002 + P6-I006` as local-only design/implementation for short one-tap tokenized config-link boundary plus commercial entitlement/audit boundary.

Phase 6 P6-C006 final VPS package refresh local preflight for AMN2 b3102db 2026-06-13: completed locally as package work and later superseded by the same-day `P6-C006` live update/smoke pass. Evidence `research/amn2/phase-6-final-vps-refresh-package-b3102db-2026-06-13.md`. Built `dist/amn2-vps-update-and-smoke-kit-b3102db.zip` from AMN2 `b3102db250da7ca9aef78ca095602187d0efc462`; package sha256 `B4C3FF33FD0A721C97A83EA8AF08D5E5B6EA5E8D1862EEB63494E8842D56A21B`; source zip `dist/amn2-codex-vps-test-prep-b3102db-source.zip`; source sha256 `72342DB625D53AE2F6B68835A1FC4E080684A4A1E9018E791820899BB9A09778`. Verification: package hygiene/test-extract passed with `package_entries=5`, `source_entries=329`, required entries present, forbidden source entries absent, shell scripts LF/no-BOM and commit bindings present; CPython 3.12.13 toolchain check passed. Fresh pytest was not run in this package step because the available CPython 3.12 bundled runtime lacks pytest. Status at preflight time was `package-ready-not-vps-smoked`; current status is `live-update-smoke-pass` in `research/amn2/phase-6-live-update-smoke-b3102db-2026-06-13.md`. Slice не выполнял live VPS command, SSH command, package upload/apply on VPS, source overlay, service restart/deploy, live bot verification/send, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy.

Phase 6 P6-N004 Aggregate telemetry retention/redaction policy + P6-S002 Recurring upstream refresh incorporation 2026-06-13: completed as AMN2 local-only code/tests/docs in commit `a9f53d7 Add telemetry retention refresh policy`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-6-telemetry-retention-upstream-refresh-2026-06-13.md`. The slice adds `app.services.telemetry_retention_policy`, `docs/TELEMETRY_RETENTION_POLICY.ru.md`, integration status/web presentation, blocked lanes for raw telemetry export and upstream refresh live actions without named gates, and advances integration status `next_gate` to `P6-N001 public docs/API taxonomy if approved`. Verification: RED `1 error, 1 warning`, focused `11 passed, 1 warning`, expanded `68 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`; `a9f53d7` is not package-rebuilt or VPS-smoked. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-N004` and `P6-S002` removed from active Phase 6 plan. Next recommendation: `P6-X001 + P6-X002` as local-only/docs/tests copy/brand consistency work; `P6-N001` remains conditional on public docs approval.

Phase 6 P6-S003 Project operating system extraction template 2026-06-13: completed as AMN3 docs-only work. Evidence `research/amn2/phase-6-project-operating-system-template-2026-06-13.md`. Created `docs/templates/PROJECT_OPERATING_SYSTEM_TEMPLATE.ru.md` and `docs/templates/NEXT_PROJECT_BOOTSTRAP.ru.md` as reusable clean-project templates for source-of-truth fields, safety boundaries, priority active plan, standing rules, verification/evidence policy, decision log, release/deploy state and next-chat bootstrap. No AMN2 runtime code or gated action was performed. `P6-S003` removed from active Phase 6 plan. Its next recommendation was completed by `P6-N004` + `P6-S002`.

Phase 6 P6-M003 attach-existing-server reconciliation boundary + P6-S001 release checklist/changelog 2026-06-13: completed as AMN2 local-only code/tests/docs in commit `3e1f4cc Add reconciliation release boundary`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-6-reconciliation-release-boundary-2026-06-13.md`. The slice adds `app.services.reconciliation_release_boundary`, `docs/RECONCILIATION_RELEASE_CHECKLIST.ru.md`, report-only integration status/web presentation, blocked lanes for reconciliation apply and release/package/public launch without named gates, and advances integration status `next_gate` to `P6-N004`. Verification: RED `1 error, 1 warning`, focused `11 passed, 1 warning`, expanded `81 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`; `3e1f4cc` is not package-rebuilt or VPS-smoked. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-M003` and `P6-S001` removed from active Phase 6 plan. Standing-rule addition: `P6-N004` Aggregate telemetry retention/redaction policy added as normal priority. Its next recommendation was refined to `P6-N004 + P6-S002`.

Phase 6 P6-M002 health/status polling scheduler boundary + P6-N002 admin analytics privacy boundary 2026-06-13: completed as AMN2 local-only code/tests/docs in commit `8f4ac6a Add privacy status analytics boundary`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-6-privacy-status-analytics-boundary-2026-06-13.md`. The slice adds `app.services.privacy_status_boundary`, `docs/PRIVACY_STATUS_ANALYTICS_BOUNDARY.ru.md`, aggregate-only integration status/web presentation, API sanitization of sensitive marker-name lists to counts, and blocked-future surface policy entries for health polling run and per-user/per-peer analytics detail routes. Verification: RED `1 error, 1 warning`, focused `33 passed, 1 warning`, expanded `65 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`; `8f4ac6a` is not package-rebuilt or VPS-smoked. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-M002` and `P6-N002` removed from active Phase 6 plan. Its next recommendation was completed by `P6-M003` + `P6-S001`.

Phase 6 P6-I005 Telegram bot profile/icon apply gates 2026-06-13: completed as AMN2 local-only code/tests/docs in commit `19f3422 Add Telegram profile icon gate policy`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-6-telegram-profile-icon-gate-policy-2026-06-13.md`. The slice adds `telegram_profile_icon_apply` to the safe productization manifest, records access/support/news bot profile icon apply as blocked without `P6-I005` named Telegram identity mutation gate, records allowed default work as local image validation/local registry metadata/operator checklist drafting/safe evidence summary, adds blocked-future surface policy entries, and exposes the safe gate through `/api/integration/status` and web `/integration-status`. Verification: RED `6 failed, 27 passed, 1 warning`, focused `33 passed, 1 warning`, expanded `83 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`; `19f3422` is not package-rebuilt or VPS-smoked. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-I005` removed from active Phase 6 plan. Its next recommendation was completed by `P6-M002` + `P6-N002`.

Phase 6 P6-I003 payments/manual approval boundary + P6-I004 support/news bot production split 2026-06-13: completed as AMN2 local-only code/tests/docs in commit `0c6aa7c Add commercial bot productization boundary`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-6-commercial-bot-productization-boundary-2026-06-13.md`. The slice adds `app.services.productization_boundary`, keeps payment processor/webhook/automatic entitlement/config delivery on payment blocked, records manual approval as required, records future support/news bots as blocked-future with separate token/runtime requirements, adds blocked-future surface policy entries, and exposes the safe boundary through `/api/integration/status` and web `/integration-status`. Verification: RED `1 error, 1 warning`, focused `29 passed, 1 warning`, expanded `81 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`; `0c6aa7c` is not package-rebuilt or VPS-smoked. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-I003` and `P6-I004` removed from active Phase 6 plan. Proposed candidate: `P6-I006` Commercial entitlement/audit boundary, not active until accepted. Next recommendation: `P6-I005` Telegram bot profile/icon apply gates as local-only/docs/tests planning without Telegram identity mutation, live bot send, config/write/public/live gates.

Phase 6 P6-M001 multi-server/multi-protocol capability registry + P6-N003 integration status current-head alignment 2026-06-13: completed as AMN2 local-only code/tests/docs in commits `4bb7364 Align integration status capability registry` and `3118b43 Make integration status source head dynamic`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-6-capability-registry-integration-status-alignment-2026-06-13.md`. The slice adds a safe `capability_registry` to `/api/integration/status` and web `/integration-status`, records current implemented capability as single-server operator control for `amneziawg` on Docker, keeps future `wireguard` and `xray` protocol managers blocked-future with no upstream/GPL code copy, and separates current branch head from latest VPS-smoked/package head through local git with `unknown` fallback outside a checkout. Verification: RED `3 failed, 5 passed, 1 warning`, focused integration-status suite `8 passed, 1 warning`, expanded API/web/security suite `46 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`; `3118b43` is not package-rebuilt or VPS-smoked. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-M001` and `P6-N003` removed from active Phase 6 plan. Next recommendation: `P6-I003` Payments/manual approval boundary if commercial access is enabled as local-only/docs/tests planning without opening public/payment-processor/config/write/live gates.

Phase 6 P6-I002 user self-service surface separation 2026-06-13: completed as AMN2 local-only code/tests/docs in commit `b676e1b Add self-service surface boundary`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-6-user-self-service-surface-boundary-2026-06-13.md`. The slice adds `self-service` as a distinct blocked-future surface, records future `/self-service` dashboard/config-delivery/device-revoke policy entries, requires separate self-service auth and own-account/device boundaries, and verifies no `/self-service*` route is mounted in the current web/admin app. Verification: RED `4 failed, 23 passed`, focused surface suite `27 passed`, expanded surface/API/web suite `43 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`; `b676e1b` is not package-rebuilt or VPS-smoked. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-I002` removed from active Phase 6 plan. Next recommendation: `P6-I003` Payments/manual approval boundary if commercial access is enabled as local-only/docs/tests planning without opening public/payment-processor/config/write/live gates.

Phase 6 P6-I001 scoped API tokens production implementation 2026-06-13: completed as AMN2 local-only code/tests/docs in commit `0b3ac1f Add API token production policy`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-6-scoped-api-tokens-production-implementation-2026-06-13.md`. The slice adds a machine-checkable production token policy manifest, keeps route-connected API token scopes limited to `server:read` and `metrics:read`, records blocked production/future scopes (`config:read`, `server:write`, `clients:write`, `local-agent:write`, `backup:read`, `backup:restore`), enforces 30-day max TTL for route-connected tokens, aligns the disabled web/admin token form with that same TTL, and updates AMN2 token policy docs. Verification: focused token/web suite `18 passed, 1 warning`, expanded token/API/security suite `59 passed, 1 warning`, and AMN2 `git diff --check` passed. Latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`; `0b3ac1f` is not package-rebuilt or VPS-smoked. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-I001` removed from active Phase 6 plan. Its next recommendation was completed by `P6-I002`.

Phase 6 P6-C005 production security review gate 2026-06-13: completed as AMN3 local/docs/security review with focused AMN2 local security regression. Evidence `research/amn2/phase-6-production-security-review-gate-2026-06-13.md`. Decision `production-security-review-complete-for-planning`: Phase 6 planning can continue, but public/self-service launch remains `no-go` until separate named gates. Reviewed public exposure, read-only API/scoped tokens, web/admin state changes, config delivery, Local Agent, backup/restore/import, Telegram bot identity/media, logs/audit/evidence and upstream/license boundary. AMN2 focused security suite on CPython 3.12.13 returned `98 passed, 1 warning`. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. `P6-C005` removed from active Phase 6 plan. Follow-up added: `P6-N003` Integration status current-head alignment, normal local-only code/tests/docs, because AMN2 `app/services/integration_status.py` still carries historical c92/7764/7281254 status constants while current branch/package distinction is `b676e1b` branch head and `2215761` latest VPS-smoked package head.

Phase 3 service-mode target VPS update 2026-06-09: AMN3 commit `bc00b77 Record Phase 3 service mode evidence` is the current evidence/runbook checkpoint. Target VPS web/bot service-mode is enabled and active, but only loopback/tunnel: web/admin binds `127.0.0.1:3030`, operator access is SSH tunnel only, no domain is planned, Caddy/HTTPS public cutover is deferred indefinitely, public/direct `3030` is closed by loopback bind, public API `3040` is absent/closed, TCP `80/443` are absent, and `.env` explicitly keeps `VPS_APPLY_ENABLED=false`. Current peer scope is `live_peer_count=2`: `Neobyatnaya-AMNZ-1` and `-2` remain approved test peers; `-3` and `-4` are revoked. Web-panel unauth smoke and authenticated read-only smoke passed. This does not unlock API route expansion, API `config:read`, `/api/clients` write CRUD, public config delivery, Local Agent mutations, backup/import/reboot, public API `3040`, Caddy/HTTPS or production peer writes.

Phase 4 unified product gate 2026-06-09: main-chat entrypoint prepared at `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`; research note `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md`. Phase 4 accepts Phase 3 service-mode loopback as closed baseline and starts as local/read-only product/API coordination for AMN2, target VPS, PRVTPRO/Web Panel and KYORESUAS/API work. The default local-only implementation queue is now closed after `P4-I001` closure; minimal docs/status/registry maintenance remains. Live commands, public exposure, config delivery, write CRUD, Local Agent mutations, backup/import/reboot and production peer/user mutation still require separate named gates.

Phase 5 P5-I004 operator-only smoke checklist 2026-06-11: completed as AMN3 docs-only/local-only. Checklist `docs/AMN2_OPERATOR_ONLY_SMOKE_CHECKLIST.ru.md`; evidence `research/amn2/phase-5-operator-only-smoke-checklist-2026-06-11.md`. It defines safe checklist fields and stop lines for web/admin loopback, bot dry/local behavior, six private/local read-only API routes and no-public-exposure checks. It does not authorize live VPS commands, SSH commands, deploy/restart/package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation or destructive VPS actions. Its next recommendation was completed by `P5-M003` AMN3 evidence discipline.

Phase 5 P5-M003 AMN3 evidence discipline 2026-06-11: completed as AMN3 docs-only/local-only. Discipline doc `docs/AMN3_PHASE5_EVIDENCE_DISCIPLINE.ru.md`; evidence `research/amn2/phase-5-amn3-evidence-discipline-2026-06-11.md`. It makes the Phase 5 closeout packet explicit: evidence file, status/backlog/forward-plan/next-chat/context sync, active-plan cleanup, safe evidence policy, verification minimums and next recommendation. It does not authorize live VPS commands, SSH commands, deploy/restart/package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation or destructive VPS actions. Its next recommendation was completed by `P5-M001` Support/news bot asset inventory.

Phase 5 P5-M001 support/news bot asset inventory 2026-06-11: completed as AMN3 docs-only/local-only. Inventory `docs/AMN2_SUPPORT_NEWS_BOT_ASSET_INVENTORY.ru.md`; evidence `research/amn2/phase-5-support-news-bot-asset-inventory-2026-06-11.md`. It records current access-bot ownership of `NEOBYATNAYA-AMNZ-BOT.png`, treats `NEOBYATNAYA-AMNZ-SUPPORT-BOT.png` and `NEOBYATNAYA-AMNZ-NEWS-BOT.png` as planning-only future separate bot assets, and keeps `NEOBYATNAYA-AMNZ-ADMIN-PANEL.png` for the separate `P5-M004` web/admin boundary. Future support/news bots require separate Telegram tokens, runtime decisions, command boundaries, local tests and named gates before any live/user-facing behavior. Bot media is split into AMN2 runtime header images and Telegram profile icons/avatars; future header upload can be local-only operator registry work, while profile icon apply is live Telegram identity mutation and needs a named gate. It does not authorize AMN2 runtime code, asset copy, live Telegram sends, bot profile icon/avatar mutation, live VPS commands, SSH commands, deploy/restart/package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation or destructive VPS actions. Its next recommendation was completed by `P5-M005` Bot media asset upload/apply boundary.

Phase 5 P5-M005 bot media asset upload/apply boundary 2026-06-11: completed as AMN3 docs-only/local-only. Boundary `docs/AMN2_BOT_MEDIA_ASSET_UPLOAD_BOUNDARY.ru.md`; evidence `research/amn2/phase-5-bot-media-asset-upload-boundary-2026-06-11.md`. It defines future operator-only local validation/registry for access/support/news bot media, separates local `start_header` assets from Telegram `profile_icon` identity, and keeps any Bot API or manual profile-icon apply behind a named Telegram identity gate. It does not authorize AMN2 runtime code, upload handler, web route, CLI command, asset copy, Telegram API call, Telegram token use, live bot send, bot profile icon/avatar mutation, live VPS commands, SSH commands, deploy/restart/package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation or destructive VPS actions. Its next recommendation was completed by `P5-M004` Граница ассета шапки веб-панели.

Phase 5 P5-M004 web/admin header asset boundary 2026-06-11: completed as AMN3 docs-only/local-only. Boundary `docs/AMN2_WEB_ADMIN_HEADER_ASSET_BOUNDARY.ru.md`; evidence `research/amn2/phase-5-web-admin-header-asset-boundary-2026-06-11.md`. It scopes `NEOBYATNAYA-AMNZ-ADMIN-PANEL.png` to the web/admin product surface only, excludes current access bot, future support/news bots and Telegram profile icons, and records the Russian-first planning convention: keep stable technical IDs, use Russian human-readable task titles in active Russian plans. It does not authorize AMN2 runtime code, asset copy, upload handler, static route, template change, web/admin runtime change, public exposure, live VPS commands, SSH commands, deploy/restart/package apply, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation or destructive VPS actions. Its next recommendation was completed by `P5-M002` QA клиентских инструкций доставки конфигурации.

Phase 5 P5-M002 client config delivery QA 2026-06-11: completed as AMN3 docs-only/local-only. QA doc `docs/AMN2_CLIENT_CONFIG_DELIVERY_QA.ru.md`; evidence `research/amn2/phase-5-client-config-delivery-qa-2026-06-11.md`. It defines safe review for Telegram `.conf`, QR and `vpn://` delivery instructions on Android/iOS/Desktop, records `.conf` as reliable fallback and treats QR/`vpn://` as secret-bearing. It also records the operator requirement that the import link may be sent as a separate message but must be copied to clipboard with one tap; current AMN2 plain text link delivery was not considered sufficient. It does not authorize AMN2 runtime code, bot handler/keyboard/template changes, live Telegram send, Telegram token use, real config delivery, live VPS commands, SSH commands, deploy/restart/package apply, public exposure, config delivery route, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation or destructive VPS actions. Its next recommendation was completed by `P5-M006`.

Phase 5 P5-M006 Telegram import link copy affordance 2026-06-11: completed as AMN2 local-only implementation in commit `ad6aa1b`, fast-forwarded and pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-5-telegram-import-link-copy-2026-06-11.md`. The bot keeps the `vpn://` import link as a separate message and adds an inline `Скопировать ссылку` button only when the exact full link fits Telegram copy-text payload limits; over-limit raw links keep visible text plus `.conf`/QR fallback and do not get a misleading copy button. Verification: RED `3 failed, 40 passed`; focused `43 passed`; bot/config `108 passed`; full AMN2 suite `664 passed, 1 warning`; `git diff --check` passed. Slice не выполнял live Telegram send, Telegram token use, real config delivery, live VPS commands, SSH commands, deploy/restart/package apply, public exposure, config delivery route, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS actions or upstream/GPL code copy. Its next recommendation was completed by `P5-N002`.

Phase 5 P5-N002 web-panel service-mode/external-only copy polish 2026-06-11: completed as AMN2 local-only implementation in commit `17454e9`, fast-forwarded and pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-5-web-panel-service-mode-copy-2026-06-11.md`. The web panel now clarifies operator-only boundary on `/integration-status`, read-only health/sync action notes on `/servers/{id}`, and external-only device limitations on `/users/{id}` without changing routes, actions, permissions, config generation or delivery behavior. Verification: RED `3 failed, 1 passed, 1 warning`; focused `4 passed, 1 warning`; web slice `47 passed, 1 warning`; full AMN2 suite `664 passed, 1 warning`; `git diff --check` passed. Slice не выполнял live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, real config delivery, Telegram send, Telegram token use, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive VPS actions or upstream/GPL code copy. Its next recommendation was completed by `P5-X002`.

Phase 5 P5-X002 bot labels and captions 2026-06-11: completed as AMN2 local-only implementation in commit `fed832c`, fast-forwarded and pushed to `amn2/codex-vps-test-prep` as part of the `de25576` update. Evidence `research/amn2/phase-5-bot-labels-captions-2026-06-11.md`. The bot delivery copy now labels the `.conf` file, QR `vpn://` payload and separate `vpn://` import link consistently in Russian-first wording without changing config generation, QR payloads, Telegram keyboard behavior or delivery transport. Verification: RED `2 failed, 6 passed`; focused `43 passed`; bot suite `105 passed`; combined final full AMN2 suite at `de25576` `664 passed, 1 warning`; `git diff --check` passed. Slice не выполнял live Telegram send, Telegram token use, real config delivery, live VPS commands, SSH commands, deploy/restart/package apply, public exposure, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS actions or upstream/GPL code copy. Its next recommendation was completed by `P5-X001`.

Phase 5 P5-X001 Russian-first microtexts 2026-06-11: completed as AMN2 local-only implementation in commit `de25576`, fast-forwarded and pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-5-russian-first-microtexts-2026-06-11.md`. The slice translates the most visible bot/admin template, bot tariff/device duration and web-panel operator-boundary microtexts to Russian-first wording while preserving stable technical IDs and user-provided tariff names. Verification: RED `7 failed, 23 passed, 1 warning`; focused `30 passed, 1 warning`; bot/web slice `152 passed, 1 warning`; full AMN2 suite `664 passed, 1 warning`; `git diff --check` passed. Slice не выполнял live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, real config delivery, Telegram send, Telegram token use, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive VPS actions or upstream/GPL code copy. Its next recommendation was completed by `P5-S002`.

Phase 5 P5-S002 active-plan stale recommendation cleanup 2026-06-12: completed as AMN3 docs-only housekeeping. Evidence `research/amn2/phase-5-active-plan-stale-recommendation-cleanup-2026-06-12.md`. The slice removes stale active-plan/recommendation pointers after `P5-X002`/`P5-X001`, marks simple and cosmetic active groups as empty, and leaves only conditional/gated Phase 5 work. Verification: stale recommendation scan produced no active stale matches after cleanup; `git diff --check` passed. Slice не выполнял AMN2 runtime/code/test/template/database changes, live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, real config delivery, Telegram send, Telegram token use, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive VPS actions or upstream/GPL code copy. Its later conditional path was completed through `P5-C002`, `P5-C001`, `P5-C003`, `P5-C005`, `P5-C004` and `P5-N001`.

Phase 5 P5-C002 VPS retention decision 2026-06-12: completed as AMN3 docs-only decision record. Evidence `research/amn2/phase-5-vps-retention-disposable-test-server-2026-06-12.md`. The operator clarified that the current target server is a disposable test VPS created for testing with Codex/project completion, has no important data to preserve, and may lose current state inside an explicitly opened named gate. This closes the retention/snapshot blocker for the current test VPS, but does not authorize live VPS commands, SSH, package apply, service restart/deploy, wipe/reinstall, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot or production peer/user mutation by itself. Its next recommendation was completed by `P5-C001`.

Phase 5 P5-C001 current-head package rebuild 2026-06-12: completed as AMN3 local-only package work. Evidence `research/amn2/phase-5-current-head-package-rebuild-2026-06-12.md`. Built `dist/amn2-vps-update-and-smoke-kit-de25576.zip` from AMN2 `de2557639cd3853e6973002be3cab24033d2f722`; package sha256 `B35D176F871ADB3B4CFDD3EC8D55B9BC5DF972E537038345B2E66899CFD21F87`; source zip `dist/amn2-codex-vps-test-prep-de25576-source.zip`; source sha256 `CFF46C44CFB8F321DEB88CE64A0F5D2154CFC02CD3931CF9955DDC466615B8CC`. Verification: `python -m app.toolchain check` passed, full AMN2 suite `664 passed, 1 warning`, package hygiene/test-extract passed with `package_entries=5`, `source_entries=313`, `forbidden_source_entries=0`, `text_bom_check=passed`, `shell_script_crlf_check=passed`. Status was `package-ready-not-vps-smoked`; its next recommendation was completed by `P5-C003`.

Phase 5 P5-C003 live rollout for AMN2 de25576 2026-06-12: completed on the disposable test VPS. Evidence `research/amn2/phase-5-live-rollout-de25576-2026-06-12.md`. Package upload and checksum passed, source overlay updated `/opt/amn2` from `f7f6131` to `de2557639cd3853e6973002be3cab24033d2f722`, read-only API smoke passed with run_id `20260612T054913Z`, and web/bot services are active with loopback `/login` returning `200`. Public exposure did not change: final listener sample showed only `127.0.0.1:3030`; `3040`, `80` and `443` were absent after smoke. `VPS_APPLY_ENABLED=false` remained explicit. Findings: this target needs `AMN2_SERVER_NAME=local` for smoke, and the inherited source-overlay apply script temporarily clobbered service-mode permissions to `root:root 700`; live permissions were repaired to `root:amneziya` service values. No config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action or secret-bearing evidence publication was performed. Its next recommendation was completed by `P5-C005`.

Phase 5 P5-C005 source-overlay permission preservation 2026-06-12: completed as AMN3 local package tooling/test fix. Evidence `research/amn2/phase-5-source-overlay-permission-preservation-2026-06-12.md`. `scripts/vps/amn2_apply_source_zip.sh` no longer tars staging `.` into the target; it overlays staging children with Python, preserves target-root metadata, normalizes copied source dirs/files to service-readable group permissions and records `permission_strategy=target-root-metadata-preserved`. Added `tests/test_amn2_apply_source_zip.py`; final verification `python -m unittest discover -s tests -p test_amn2_apply_source_zip.py -v` returned `2 passed`. The historical `dist/amn2-vps-update-and-smoke-kit-de25576.zip` remains the P5-C003 evidence artifact; the corrected-script rebuild requirement was later satisfied by `P5-C006` for AMN2 `dd0dd44`. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS actions or upstream/GPL code copy. Its next recommendation was completed by `P5-C004`.

Phase 5 P5-C004 secret handoff protocol 2026-06-12: completed as AMN3 docs-only protocol work. Protocol `docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md`; evidence `research/amn2/phase-5-secret-handoff-protocol-2026-06-12.md`. It defines `regenerate_on_target_where_possible + operator_local_channel_only_for_external_secrets`, secret classes, allowed/forbidden channels, safe summary fields, `.env`/`servers.yml` private-file boundaries, stop lines and related named gates. `docs/AMN2_FRESH_DEPLOY_FROM_ZERO_RUNBOOK.ru.md` now points the fresh-deploy operator secrets/defaults section to this protocol. Slice не выполнял AMN2 runtime code changes, live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS actions, Telegram token use, live bot send, Telegram profile mutation or upstream/GPL code copy. Its next recommendation was completed by `P5-N001`.

Phase 5 P5-N001 operator docs cleanup 2026-06-12: completed as AMN3 docs-only housekeeping. Evidence `research/amn2/phase-5-operator-docs-cleanup-2026-06-12.md`. The slice removed stale active references to already closed Phase 5 gate slices, refreshed operator smoke/evidence rules, forward plan, next-chat handoff, current status, context import and transfer backlog, and leaves `P5-N001` out of the active plan. Slice не выполнял AMN2 runtime code changes, live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS actions, Telegram token use, live bot send, Telegram profile mutation or upstream/GPL code copy. Its next recommendation was completed by `P5-N003`.

Phase 5 P5-N003 client/platform compatibility refresh 2026-06-12: completed as AMN2 local-only plus AMN3 evidence work. Upstream note `research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-12.md`; evidence `research/amn2/phase-5-client-platform-compatibility-refresh-2026-06-12.md`. AMN2 commit `dd0dd44 Refresh client platform guidance` updates the machine-checkable client compatibility matrix, bot delivery guidance tests and web/bot setup docs after current upstream release metadata showed generic Linux x64 tar assets. AMN2 now says Linux x64 tar is available while distro-specific Linux packages are not promised. Focused verification: RED `2 failed, 3 passed`; GREEN compatibility/bot delivery `13 passed`; git hygiene passed; pushed to `amn2/codex-vps-test-prep`. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS actions, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. Its next recommendation was completed by `P4-PRVTPRO-REFRESH-003`.

Phase 5 carried item P4-PRVTPRO-REFRESH-003 server status/latency UX boundary 2026-06-12: closed as a carried item from Phase 4. Boundary `docs/AMN2_READ_ONLY_SERVER_STATUS_LATENCY_UX_BOUNDARY.ru.md`; evidence `research/amn2/phase-5-prvtpro-server-status-latency-boundary-2026-06-12.md`. The AMN3 docs-only design boundary was completed first, and the safe local cached display was later implemented by `P5-L001` in AMN2 `9bff807`. Live probes, SSH, health/sync actions, public exposure, config delivery, write API, Local Agent mutation, raw logs and secret/user/peer fields remain behind separate gates. Slice не выполнял AMN2 runtime code changes, live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS actions, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code/UI/template/workflow/manager copy. Its next recommendation was completed by `P5-C006`.

Phase 5 P5-C006 current-head package rebuild for AMN2 dd0dd44 2026-06-12: completed as AMN3 local package work. Evidence `research/amn2/phase-5-current-head-package-rebuild-dd0dd44-2026-06-12.md`. Built `dist/amn2-vps-update-and-smoke-kit-dd0dd44.zip` from AMN2 `dd0dd442f0f25c1113accdc625dd16a96059eba4`; package sha256 `BB510BEABEB5ACCB7394C09F43EA7288BB08FC1352CCD35DA5AFF781E1B48E6D`; source zip `dist/amn2-codex-vps-test-prep-dd0dd44-source.zip`; source sha256 `E29DFD7B64727BC75C677EDE2B897C6C972AB25243FD7713B767ABE1E29E2BD1`. Verification: `python -m app.toolchain check` passed, full AMN2 suite `664 passed, 1 warning`, `git diff --check` passed, package hygiene/test-extract passed with `package_entries=5`, `source_files=271`, required entries present, forbidden source entries absent and shell scripts LF/no-BOM. The kit was tightened so apply uses the full source commit binding and the runbook explicitly says it does not authorize live VPS apply. Status was `package-ready-not-vps-smoked`; latest VPS-smoked source overlay remains `de25576`. This package is now superseded as current-head package evidence because AMN2 advanced to `9bff807`. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, source overlay, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS actions, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. Its local alternatives were completed by `P5-L002` and `P5-L001`; its current-head rebuild requirement was later satisfied by `P5-C008`.

Phase 5 P5-L002 bot media local registry and P5-L001 read-only status/latency display 2026-06-12: completed as AMN2 local-only implementation in commit `9bff807 Add local bot media and status summaries`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-5-local-bot-media-and-status-summaries-2026-06-12.md`. `P5-L002` adds `app.services.bot_media` and `python -m app.cli bot-media validate/stage/select/manifest` for access/support/news bot media, with local `start_header` runtime selection and `profile_icon` staged-for-operator metadata only. `P5-L001` adds a private web/admin `Read-only server summary` from cached `server_health_checks` DB data only. Verification: RED checks failed as expected; focused final suite `71 passed, 1 warning`; full AMN2 suite `671 passed, 1 warning`; git hygiene passed. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS actions, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. Its package rebuild requirement was completed by `P5-C008`.

Phase 5 P5-C008 current-head package rebuild for AMN2 9bff807 2026-06-12: completed as AMN3 local package work. Evidence `research/amn2/phase-5-current-head-package-rebuild-9bff807-2026-06-12.md`. Built `dist/amn2-vps-update-and-smoke-kit-9bff807.zip` from AMN2 `9bff807a1d8fcceb833c1ef864064d2af6aaaff1`; package sha256 `882619B665B93CF4D6EFAB7977F7AE968F032C08C74CCFDA19A6B06BD629FAF9`; source zip `dist/amn2-codex-vps-test-prep-9bff807-source.zip`; source sha256 `5109C0FD7FBF40BB2F48C7476015E8BD4CCCF3AF54CAD702160488B0CE898AFD`. Verification: initial system Python toolchain check failed on Python 3.14.3 as expected; CPython 3.12.13 toolchain check passed; full AMN2 suite `671 passed, 1 warning`; AMN2 `git diff --check` passed; package hygiene/test-extract passed with `package_entries=5`, `source_files=274`, required entries present, forbidden source entries absent, shell scripts LF/no-BOM and commit bindings present. Status at rebuild time was `package-ready-not-vps-smoked`; this was later superseded by `P5-C007` live update/smoke for the same AMN2 head. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, source overlay, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS actions, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. Next recommendation was completed by `P5-C007`.

Phase 5 P5-C007 live update/smoke for AMN2 9bff807 2026-06-12: completed on the disposable test VPS. Evidence `research/amn2/phase-5-live-update-smoke-9bff807-2026-06-12.md`. Package upload/checksum/extract passed, source overlay updated `/opt/amn2` from `de25576` to `9bff807a1d8fcceb833c1ef864064d2af6aaaff1`, read-only API smoke passed with run_id `20260612T184701Z`, and web/bot services are active after restart with loopback `/login` returning `200`. Final remote listener snapshot showed only `127.0.0.1:3030`; `3040`, `80` and `443` were absent as remote listeners. `VPS_APPLY_ENABLED=false` remained explicit. Findings: intermittent SSH banner exchange timeouts/refusals required waits between attempts; immediate post-restart web readiness needed a repeat check after ten seconds; external HTTP probes for public `3030/3040` timed out, and public TCP/HTTP-80 behavior appeared outside AMN2 because remote `ss` showed no `80/443` listener. No config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, public exposure change or secret-bearing evidence publication was performed. Its next recommendation was completed by `P5-O001`.

Phase 5 P5-O001 operator-only post-update UI smoke for AMN2 9bff807 2026-06-12: completed as a named gate with decision `needs-fix`. Evidence `research/amn2/phase-5-operator-post-update-ui-smoke-9bff807-2026-06-12.md`. The operator manually authenticated through an SSH local port forward and Codex sampled authenticated GET navigation for `/`, `/users`, `/servers`, `/orders`, `/logs`, `/settings`, `/config-templates`, `/api-readiness`, `/integration-status`, `/api-tokens` and `/devices/disabled`. No write action, config delivery, token issue/revoke, Local Agent mutation, package apply/rebuild, service restart/deploy, public exposure change, backup/import/reboot, Telegram action or secret-bearing evidence publication was performed. Findings: authenticated web/admin still exposes create/write/config/token controls during operator-only smoke, including user/server creation, token issue and config-template save/reset affordances; visible menu/section/table copy remains mixed Russian/English; resource/user display should use `AmneziyaDA` as the resource name with the user shown below it; dashboard summary cards should center the numeric count and entity label in a two-line layout. Its next recommendation was completed by `P5-O002`.

Phase 5 P5-O002 web-admin gated-action and Russian-first UX cleanup 2026-06-12: completed as AMN2 local-only implementation/test work in commit `2215761 Polish operator web admin UX`, pushed to `amn2/codex-vps-test-prep`. Evidence `research/amn2/phase-5-web-admin-gated-action-russian-ux-2026-06-12.md`. The slice changes the web/admin brand/title suffix to `AmneziyaDA`, aligns the sampled authenticated web/admin menu and pages Russian-first, centers dashboard summary cards as two-line count/entity labels, removes active user/server create links from operator-only list pages, and disables token issue/revoke plus config-template save/reset controls with named-gate notes. Verification: focused P5-O002 `4 passed, 1 warning`; expanded web regression `90 passed, 1 warning`; AMN2 `git diff --check` and staged `git diff --cached --check` passed; temporary local browser smoke on `127.0.0.1:13031` confirmed login, Russian-first headings, `1|пользователь`, `1|сервер`, `1|заявка`, `1|устройство`, no active `/users/new` or `/servers/new` links, and disabled token/template submit buttons. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, source overlay, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS actions, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. Its next recommendation was completed by `P5-C009`.

Phase 5 P5-C009 current-head package rebuild for AMN2 2215761 2026-06-13: completed as AMN3 local package work. Evidence `research/amn2/phase-5-current-head-package-rebuild-2215761-2026-06-13.md`. Built `dist/amn2-vps-update-and-smoke-kit-2215761.zip` from AMN2 `221576169a84bbf662114c564e83c41fba0091b5`; package sha256 `6C360E8005E117EC59DD2829E9C4E9D2F36B5070275CD989D9D51A0675CF8B44`; source zip `dist/amn2-codex-vps-test-prep-2215761-source.zip`; source sha256 `825D1EF34F8DF11C0DB12B7A3DCDAE8FE79F04A8C56113CBA9CAEA3ECDBCC38B`. Verification: initial system Python toolchain check failed on Python 3.14.3 as expected; CPython 3.12.13 toolchain check passed; full AMN2 suite `675 passed, 1 warning`; AMN2 `git diff --check` passed; package hygiene/test-extract passed with `package_entries=5`, `source_files=275`, required entries present, forbidden source entries absent, shell scripts LF/no-BOM and commit bindings present. Status at rebuild time was `package-ready-not-vps-smoked`; this was later superseded by `P5-C010` live update/smoke for the same AMN2 head. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, source overlay, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS actions, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. Next recommendation was completed by `P5-C010`. Deferred gated items not executed: `VPS-REBUILD-001`, write API, config delivery, public exposure and `P4-PRVTPRO-REFRESH-003-LIVE` probes/actions.

Phase 5 P5-C010 live update/smoke for AMN2 2215761 2026-06-13: completed on the disposable test VPS. Evidence `research/amn2/phase-5-live-update-smoke-2215761-2026-06-13.md`. Package upload/checksum/extract passed; source overlay updated `/opt/amn2` from `9bff807a1d8fcceb833c1ef864064d2af6aaaff1` to `221576169a84bbf662114c564e83c41fba0091b5`; source overlay run_id `20260613T045004Z` passed; read-only API smoke run_id `20260613T045107Z` passed with `VPS verdict: pass`; web/bot services are active after restart; loopback `/login` returns `200`; final remote listener snapshot shows only `127.0.0.1:3030` and `3040/80/443` absent; `VPS_APPLY_ENABLED=false` remained explicit. Gate не выполнял config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, public exposure change, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. Its next recommendation was completed by `P5-D001`. Deferred gated items still not executed: `VPS-REBUILD-001`, write API, config delivery, public exposure and `P4-PRVTPRO-REFRESH-003-LIVE` probes/actions.

Phase 5 P5-D001 operator-only pilot acceptance and Phase 6 entry decision 2026-06-13: completed as AMN3 docs-only decision work. Evidence `research/amn2/phase-5-operator-pilot-acceptance-phase-6-entry-2026-06-13.md`; Phase 6 handoff `docs/NEXT_CHAT_AMN2_PHASE_6_PRODUCTIZATION.ru.md`. Decision `operator-only-pilot-accepted`: AMN2 `2215761` is current branch head and latest VPS-smoked package/source head; Phase 5 default queue is empty; Phase 6 is `planning-ready only` and does not open live public/self-service work by itself. Slice не выполнял live VPS command, SSH command, package apply/rebuild on VPS, source overlay, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy. Next recommendation is `P6-C005` Production security review gate as local/docs/security review. Deferred gated items still not executed: `VPS-REBUILD-001`, write API, config delivery, public exposure, backup/import/reboot, Local Agent write/config routes, production peer/user mutation and `P4-PRVTPRO-REFRESH-003-LIVE` probes/actions.

Phase 5 P5-S003 carried-items active-plan cleanup 2026-06-12: completed as AMN3 docs-only housekeeping. Evidence `research/amn2/phase-5-carried-items-active-plan-cleanup-2026-06-12.md`. Closed carried items remain visible with source phase, status, importance and gate labels, but no longer read like active pending work. `P4-PRVTPRO-REFRESH-003` is consistently described as carried from Phase 4 and closed in Phase 5: AMN3 design boundary closed first, local cached display implemented by `P5-L001`, and live probes/actions remain separately gated. Slice не выполнял AMN2 runtime/code/test/template/database changes, live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, config delivery, Telegram send, Telegram token use, Telegram profile mutation, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive VPS actions or upstream/GPL code copy. Its VPS-path recommendation was completed by `P5-C007`.

KYORESUAS upstream refresh 2026-06-10: GitHub `main` was rechecked at `ffdc78c` / tree `ffdc78cf4e6f653322c6df251df10a7d7274a887`; note `research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-10.md`. Useful new signals are operation serialization, safer config writes, client lifecycle wording, QR/`vpn://` import compatibility, rate-limit/hardening and setup resilience. Decision remains unchanged: no upstream code/service copy, no public API `3040`, no `/api/clients` write CRUD, no config delivery, no backup/import/reboot. These signals were used as docs-only inputs for `WAPI-V001`, `WAPI-V002`, `WAPI-V003`, `WAPI-V004`, `WAPI-V005`, `WAPI-I004`, `WAPI-I003`, `WAPI-I002`, `WAPI-I001`, `WAPI-I005`, `NG-N003`, `NG-N002`, `NG-N001`, `NG-N004`, `NG-S001`, `NG-S002`, `NG-S004`, `NG-X003` and `NG-X001`; очередь default docs-only cosmetic закрыта; следующий безопасный шаг требует отдельного explicit decision.

PRVTPRO upstream refresh 2026-06-10: GitHub `main` was rechecked at `7f062abc2c76bbe19eb7daafdf1191d6c26ff19a`; note `research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md`. Useful AMN2 Phase 4 signals are expiration/lifecycle contract tests, read-only About/Version/Build status, read-only server status/latency UX and API taxonomy/OpenAPI grouping as docs/policy support. Hybrid-only signals are AdGuard Home integration, SOCKS5 service manager, Xray migration/attach existing install and multi-protocol capability registry. Decision remains unchanged: PRVTPRO is GPL-3.0 research-only; no code, templates, UI, manager implementations or workflows are copied; no admin-equivalent Bearer token model, public panel, config delivery, reboot, backup, import or server cleanup is opened without a separate named gate. `P4-PRVTPRO-REFRESH-002` expiration-field contract tests and `P4-PRVTPRO-REFRESH-001` read-only About/Version/Build status are completed as AMN2 local-only and merged into `amn2/codex-vps-test-prep` at `1508e3c4a100b76815b29f91757290f1266f813d`; evidence: `research/amn2/phase-4-prvtpro-local-slices-merge-2026-06-10.md`. `P4-PRVTPRO-REFRESH-004` API taxonomy/OpenAPI grouping was completed as AMN3 docs-only policy support; evidence: `research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md`. `P4-PRVTPRO-REFRESH-003` is closed as a carried item from Phase 4: design boundary evidence `research/amn2/phase-5-prvtpro-server-status-latency-boundary-2026-06-12.md`, local cached display implementation by `P5-L001` in AMN2 `9bff807`, and live probes/actions remain separately gated.

Phase 4 candidate registry 2026-06-09: created `research/amn2/phase-4-candidate-registry-2026-06-09.md`. It classifies AMN2/API, target VPS, PRVTPRO/Web Panel and KYORESUAS/API candidates by priority (`critical`, `important`, `normal`, `cosmetic`) and gate class (`local-only`, `requires VPS gate`, `blocked until separate write/config/public gate`). The registry was updated with `P4-C009` after the operator reported that created test accounts/configurations were not visible in the web-panel users/configurations area. The initial local-only/default sequence now has `P4-C009`, `P4-I002`, route/secret gate planning, `P4-I003` design/implementation, `P4-I004` endpoint taxonomy docs, `P4-N003` aggregate metrics privacy boundary, `P4-I005` API token lifecycle boundary, `P4-N004` bot/admin read-only labels, `P4-N001` docs/status drift synchronization, `P4-N002` protocol manager interface checklist, `P4-X003` Russian-first operator docs polish, `P4-X002` API/status/gate naming cleanup, `P4-X001` read-only API docs grouping polish and `P4-I001` second read-only UX pass closure completed. Remaining default-mode work is minimal docs/status/registry maintenance only; any VPS/live/public/write/config work needs a separate named gate/decision.

Phase 4 start plan 2026-06-09: created `docs/superpowers/plans/2026-06-09-amn2-phase-4-start.md`. It records current GitHub/AMN2 checkout access checks, defines the `P4-VPS-ACCESS-READONLY-2026-06-09` gate shape for future SSH access verification, and breaks Phase 4 startup into critical, important, medium, minimal and cosmetic tasks. The plan was updated so the first AMN2 local-only slice investigates the web-panel user/config visibility gap before wording polish. GitHub connector currently shows `pull=true`, `push=false` for `barakov-dot/amn3` and `barakov-dot/amn2`, while local `git fetch --dry-run` and `git push --dry-run` passed for both active remotes. VPS login was not run because the target host/alias is intentionally not stored in the repo.

Phase 4 P4-C009 web-panel user/config visibility 2026-06-09: implemented locally in AMN2 branch `codex/phase-4-web-panel-user-config-visibility`; evidence `research/amn2/phase-4-web-panel-user-config-visibility-implementation-2026-06-09.md`. Root cause: `/users` lists local AMN2 database users/devices only, while live VPS peers created outside AMN2 are visible through server peer-sync/read-only inventory, not automatic user/config backfill. AMN2 change clarifies this boundary in `users.html` and adds a regression test. Verification: RED test failed as expected before the template change; focused verification passed with `26 passed, 1 warning`; `git diff --check` passed. No live VPS commands, write/config/token/sync/apply/revoke/backup/import/reboot or public exposure changes were performed. Next recommended local-only slice is `P4-I002` service-mode/read-only status wording.

Phase 4 P4-I002 service-mode/read-only status wording 2026-06-09: implemented locally in AMN2 branch `codex/phase-4-service-mode-status-wording`, commit `83f6d28 Show service mode status boundary`, stacked on `a73e845` from P4-C009. Evidence: `research/amn2/phase-4-service-mode-status-wording-implementation-2026-06-09.md`. AMN2 `/integration-status` now reports `service_mode_loopback_ready`, shows a `Service-mode boundary` panel, and makes loopback-only web/admin `127.0.0.1:3030`, SSH-tunnel-only operator access, absent/closed public API `3040`, absent TCP `80/443`, deferred domain/HTTPS cutover and `VPS_APPLY_ENABLED=false` visible. Verification: RED showed stale manual-prelaunch wording and missing boundary; focused verification passed with `7 passed, 1 warning`; `git diff --check` passed. No live VPS commands, write/config/token/sync/apply/revoke/backup/import/reboot or public exposure changes were performed. Historical next-step note was superseded by later route/secret work and `P4-I001` closure.

Phase 4 route/secret gate planning 2026-06-09: completed as AMN3 docs-only gate plan `research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md`; execution plan `docs/superpowers/plans/2026-06-09-amn2-route-secret-gate-planning.md`. It consolidates existing AMN2 local-gate baselines (`f9d2c79`, `9ce42f4`, `256d0c0`, `2ef3af7`, `4d4e7a4`, `afb2702`, `83f6d28`) into a mandatory proposal/checklist before future route expansion. It classifies read-only aggregate/status, write peer/user lifecycle, secret-read config delivery, public/self-service delivery, Local Agent configs/mutations, backup/import/reboot and public exposure/cutover. This does not authorize AMN2 code changes, new routes, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot or live VPS commands.

Phase 4 P4-I003 read-only API/status design 2026-06-09: completed as AMN3 docs-only candidate-specific design `research/amn2/phase-4-read-only-api-status-design-2026-06-09.md`; execution plan `docs/superpowers/plans/2026-06-09-amn2-read-only-api-status-design.md`. It binds the next safe AMN2 local slice to the existing six read-only API routes (`/api/servers`, `/api/servers/{server_name}/summary`, `/api/integration/status`, `/api/local-agent/runtime/summary`, `/api/metrics/summary`, `/api/users/summary`) and scopes future work to schema/docs/tests, safe audit assertions, forbidden-marker checks and `checked_routes=6`. No AMN2 code, live VPS command, public listener, config delivery, `/api/clients` CRUD, Local Agent mutation, token lifecycle action, backup/import/reboot or production peer/user mutation was performed.

Phase 4 P4-I003 AMN2 implementation plan 2026-06-09: completed as AMN3 docs-only execution plan `docs/superpowers/plans/2026-06-09-amn2-p4-i003-read-only-api-status-schema.md`. The plan defines AMN2 branch `codex/phase-4-read-only-api-status-schema` and limits execution to `API_RUNTIME_ROUTE_BINDINGS`, runtime route drift tests, read-only API/status contract tests, safe audit assertions and AMN2 policy docs. It does not authorize AMN2 implementation by itself, live VPS commands, new routes, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation.

Phase 4 P4-I003 read-only API/status schema implementation 2026-06-09: completed locally in AMN2 branch `codex/phase-4-read-only-api-status-schema`, commit `b71b8f4 Lock read-only API status contract`; evidence `research/amn2/phase-4-read-only-api-status-schema-implementation-2026-06-09.md`. The slice adds `API_RUNTIME_ROUTE_BINDINGS`, runtime route drift coverage, read-only API/status contract tests, updated service-mode API status expectations and AMN2 policy docs. Verification: RED failed as expected on missing `API_RUNTIME_ROUTE_BINDINGS`; focused final verification passed with `56 passed, 1 warning`; `git diff --check` passed. No live VPS commands, new routes, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation were performed.

Phase 4 P4-I004 endpoint taxonomy / route-policy docs alignment 2026-06-09: completed locally in AMN2 branch `codex/phase-4-endpoint-taxonomy-route-policy-docs`, commit `acf39f8 Add API endpoint taxonomy docs`; evidence `research/amn2/phase-4-endpoint-taxonomy-route-policy-docs-implementation-2026-06-09.md`. The slice adds private/local taxonomy docs for the current six read-only `/api/*` routes, links route/auth and token policy docs, and keeps public OpenAPI/docs exposure gated. Verification: `git diff --check` passed, forbidden enabled-marker scan passed with no matches, focused policy/contract regression passed with `33 passed, 1 warning`. No live VPS commands, runtime route changes, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation were performed.

Phase 4 P4-N003 aggregate metrics privacy boundary 2026-06-09: completed locally in AMN2 branch `codex/phase-4-aggregate-metrics-privacy-boundary`, commit `8b6aef8 Show aggregate metrics privacy boundary`; evidence `research/amn2/phase-4-aggregate-metrics-privacy-boundary-implementation-2026-06-09.md`. The slice adds an additive safe `privacy` marker to `GET /api/metrics/summary` (`aggregate_only=true`, no per-peer fields, no per-user fields, no public exposure) and updates local tests/docs. Verification: RED failed on the missing privacy marker as expected; final extended verification passed with `50 passed, 1 warning`; `git diff --check` and marker scan passed. No live VPS commands, route count changes, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation were performed.

Phase 4 P4-I005 API token lifecycle boundary 2026-06-09: completed locally in AMN2 branch `codex/phase-4-api-token-lifecycle-boundary`, commit `22061ea Show API token lifecycle boundary`; evidence `research/amn2/phase-4-api-token-lifecycle-boundary-implementation-2026-06-09.md`. The slice adds an additive safe `api_token_lifecycle_boundary` marker to `GET /api/integration/status` and updates local tests/docs. Verification: RED failed on the missing lifecycle marker as expected; final extended focused regression passed with `59 passed, 1 warning`; `git diff --check` and marker scan passed. No live VPS commands, route count changes, token issue/revoke/rotate API routes, production token mutation, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot or production peer/user mutation were performed.

Phase 4 P4-N004 bot/admin read-only labels 2026-06-09: completed locally in AMN2 branch `codex/phase-4-bot-admin-read-only-labels`, commit `c9829b7 Clarify bot admin read-only labels`; evidence `research/amn2/phase-4-bot-admin-read-only-labels-implementation-2026-06-09.md`. The slice adds service-mode/gated boundary labels to web admin navigation, local/live inventory wording to users/servers empty states, and aggregate/local labels to bot admin list views. Verification: RED failed on missing labels as expected; final extended regression passed with `238 passed, 1 warning`; `git diff --check` and marker scan passed. No live VPS commands, route changes, callback changes, POST behavior changes, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token issue/revoke/rotate API routes or production peer/user mutation were performed.

Phase 4 P4-N001 docs/status drift synchronization 2026-06-09: completed as AMN3 docs-only/local-only evidence `research/amn2/phase-4-docs-status-drift-sync-2026-06-09.md`. The sync aligned the active candidate registry, transfer backlog, current status, next-chat packet, Phase 4 handoff, active plan and context import after `P4-N004`; older next-step notes in prior evidence files were retained as historical chronology instead of being rewritten. No AMN2 code, live VPS commands, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token lifecycle API operations or production peer/user mutation were performed. Next recommended local-only slice is `P4-N002` protocol manager interface checklist.

Phase 4 P4-N002 protocol manager interface checklist 2026-06-09: completed as AMN3 docs-only/local-only evidence `research/amn2/phase-4-protocol-manager-interface-checklist-2026-06-09.md`. The checklist maps PRVTPRO manager-architecture ideas onto existing AMN2 `RemoteOperation`/`OperationPlan`, partial-failure and `ConfigExportResult` baselines, with explicit capability, gate, test, license and non-action boundaries. No AMN2 code, live VPS commands, manager implementation, route expansion, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token lifecycle API operations or production peer/user mutation were performed. Historical next-step note was superseded by later `P4-X003`, `P4-X002`, `P4-X001` and `P4-I001` closure.

Phase 4 P4-X003 Russian-first operator docs polish 2026-06-09: completed as AMN3 docs-only/local-only evidence `research/amn2/phase-4-russian-first-operator-docs-polish-2026-06-09.md`. The polish updates active Phase 4 operator-facing handoff/status/plan headings and copy-paste next-chat wording to Russian-first style while preserving technical IDs, route names, gates, file paths and safety boundaries. No AMN2 code, live VPS commands, route expansion, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token lifecycle API operations or production peer/user mutation were performed. Historical next-step note was superseded by later `P4-X002`, `P4-X001` and `P4-I001` closure.

Phase 4 P4-X002 API/status/gate naming cleanup 2026-06-09: completed as AMN3 docs-only/local-only evidence `research/amn2/phase-4-api-status-gate-naming-cleanup-2026-06-09.md`. The cleanup defines active meanings for `service-mode`, `loopback-only`, `SSH tunnel`, `local-only`, `read-only`, `requires VPS gate`, `blocked`, `deferred`, `public exposure` and `config delivery` while preserving technical IDs, route names, gates, file paths and safety boundaries. No AMN2 code, live VPS commands, route expansion, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token lifecycle API operations or production peer/user mutation were performed. Follow-up `P4-X001` was selected and completed next.

Phase 4 P4-X001 read-only API docs grouping polish 2026-06-09: completed as AMN3 docs-only/local-only evidence `research/amn2/phase-4-read-only-api-docs-grouping-polish-2026-06-09.md`. The polish groups the existing six private/local read-only routes into server inventory/status (`GET /api/servers`, `GET /api/servers/{server_name}/summary`), integration/service boundary (`GET /api/integration/status`), Local Agent runtime summary (`GET /api/local-agent/runtime/summary`) and aggregate metrics (`GET /api/metrics/summary`, `GET /api/users/summary`). It does not authorize public OpenAPI/docs exposure, route expansion, public API `3040`, direct public web/admin `3030`, config delivery, write routes, Local Agent mutations or live VPS work. Follow-up `P4-I001` closure was selected and completed next.

Phase 4 P4-I001 second read-only UX pass closure 2026-06-10: completed as AMN3 docs-only decision evidence `research/amn2/phase-4-p4-i001-read-only-ux-pass-closure-2026-06-10.md`. The second private-panel UX pass was not run, and no new page-level findings were collected; the operator chose to close it as not needed now so Phase 4 does not keep returning to the optional fallback. Existing service-mode UX evidence plus `P4-C009`, `P4-I002`, `P4-N004`, `P4-X003`, `P4-X002` and `P4-X001` are sufficient for the current boundary. No AMN2 code, live VPS commands, SSH-tunnel browser review, public exposure, config delivery, write CRUD, Local Agent mutations, backup/import/reboot, token issue/revoke/rotate API routes or production peer/user mutation were performed. Default local-only implementation queue is now closed except minimal maintenance.

Phase 4 P4-NG named gate / write API readiness 2026-06-10: started as AMN3 docs-only planning. Plan: `docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md`; charter/evidence: `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md`. Closed and removed from the active plan: `NG-C001` named gate charter and `NG-C002` safety boundary restatement. Follow-up `NG-C003` and `NG-C004` were selected and completed next. No AMN2 code, live VPS command, SSH command, route expansion, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was performed. `NG-V001` read-only VPS baseline gate later gained the `NG-SC001` Codex Security checkpoint and was closed as `go`; write API live work remains blocked until a separate `P4-NG-WRITE-API-LIVE-GATE`.

Phase 4 NG-C003/NG-C004 secrets policy and go/no-go format 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-secrets-policy-go-no-go-format-2026-06-10.md`. Reusable template: `research/amn2/phase-4-ng-named-gate-evidence-template-2026-06-10.md`. `NG-S003` was also closed because creating the reusable named-gate evidence template is required for `NG-C003` and `NG-C004`. Gate evidence is now limited to boolean/status summaries and safe aggregate counts; forbidden fields include `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, password/session secrets, keys, PSK, peer public keys, `.conf`, QR, `vpn://`, backup contents, endpoint values, cookies, full logs and secret-bearing command output. Every gate must end with `go_no_go_decision: go | no-go | defer`. No AMN2 code, live VPS command, SSH command, public exposure, config delivery, write CRUD, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `NG-C005` was selected and completed next.

Phase 4 NG-C005 write API live-block assertion 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md`. It records `live_write_authorized: no`, keeps `/api/clients` write CRUD, peer apply/revoke/sync, config delivery, token issue/revoke/rotate routes, Local Agent mutations, backup/import/reboot, public exposure and production peer/user mutation blocked, and requires every future write API slice to state its live-write status explicitly. The selected next docs-only task was `WAPI-V001` write API threat model with `live_write_authorized: no`. No AMN2 code, live VPS command, SSH command, route expansion, public exposure, config delivery, write CRUD, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.

Phase 4 WAPI-V001 write API threat model 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`. It defines protected assets, trust boundaries, threat classes and required tests before any future write API implementation. Key risk areas are accidental live mutation, scope escalation, config secret leakage, token lifecycle bypass, replay/duplicates, concurrent operations, local/remote partial failure, audit/log leakage, public exposure creep, Local Agent confused-deputy behavior, destructive operation smuggling, operation status leakage and upstream license boundary drift. The KYORESUAS refresh signals are explicitly carried as operation lock/serialization, atomic config write, `active|disabled` plus `expiresAt` lifecycle wording, QR/`vpn://` secret-read tests, rate-limit/Helmet-style public hardening and setup resilience, with no upstream code copied. `live_write_authorized: no` remains in force. Follow-up `WAPI-V002` was selected and completed next. No AMN2 code, live VPS command, SSH command, route expansion, public exposure, config delivery, write CRUD, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.

Phase 4 WAPI-V002 write API route taxonomy 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`. It classifies future route groups, candidate route names, route classes, minimal scopes, side effects, named gates and required tests before any AMN2 implementation planning. Candidate names are planning placeholders only; no runtime route, OpenAPI artifact, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, live VPS command or production mutation was added. Follow-up `WAPI-V003` was selected and completed next.

Phase 4 WAPI-V003 local fake-runner contract 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`. It defines future fake-runner inputs, outputs, operation intents, deterministic failure modes, audit-safe metadata and RED test requirements without adding runner code, runtime routes, live VPS commands, config delivery, `/api/clients` CRUD or production mutation. Follow-up `WAPI-V004` was selected and completed next.

Phase 4 WAPI-V004 idempotency, locking and partial-failure model 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md`. It defines required idempotency keys, safe request fingerprints, per-target lock scopes, retry behavior, conflict statuses and partial-failure vocabulary for future write API/fake-runner work. Historical VPS evidence is used only as status vocabulary input: Phase 1 `dry-run-only-pass`, Phase 2 single disposable peer `verified-live`, and Phase 3 service-mode loopback baseline do not authorize new live/write actions. No AMN2 code, runner code, runtime route, live VPS command, config delivery, `/api/clients` CRUD or production mutation was added. Follow-up `WAPI-V005` was selected and completed next.

Phase 4 WAPI-V005 write API audit/redaction requirements 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-v005-write-api-audit-redaction-requirements-2026-06-10.md`. It defines required safe audit fields, forbidden secret-bearing fields, redaction rules, event types, audit failure behavior and RED test requirements before any write API route, fake-runner or audit schema implementation. Historical VPS evidence may be referenced only as safe labels/status vocabulary, not as command output, endpoint data, full logs or current live permission. No AMN2 code, audit schema implementation, runner code, runtime route, live VPS command, config delivery, `/api/clients` CRUD or production mutation was added. Follow-up `WAPI-I004` was selected and completed next.

Phase 4 WAPI-I004 operation status model 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-i004-operation-status-model-2026-06-10.md`. It defines safe operation status fields, canonical statuses, reason codes, transition rules, visibility tiers, UI label guidance and RED test requirements before any operation records, status routes, web labels or queue implementation. Historical VPS evidence may appear only as safe status labels such as `dry_run_only_pass`, `verified_live_single_disposable_peer` and `service_mode_loopback_baseline`; it does not authorize current live/write actions. No AMN2 code, status schema implementation, operation queue, runner code, runtime route, live VPS command, config delivery, `/api/clients` CRUD or production mutation was added. Follow-up `WAPI-I003` was selected and completed next.

Phase 4 WAPI-I003 scoped write-token model 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-i003-scoped-write-token-model-2026-06-10.md`. It defines future minimal scope classes, proposed scoped write/config/operation permissions, forbidden broad scope patterns, safe token lifecycle boundaries, audit/status binding and RED test requirements before any write API auth, token checks, route or operation planning implementation. Historical VPS evidence does not grant write scopes, config scopes or live-runner permission. No AMN2 code, token issue/revoke route, token storage change, runner code, runtime route, live VPS command, config delivery, `/api/clients` CRUD or production mutation was added. Follow-up `WAPI-I002` was selected and completed next.

Phase 4 WAPI-I002 config delivery decoupling 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-i002-config-delivery-decoupling-2026-06-10.md`. It defines future client/peer creation as safe operation/client metadata only and keeps `.conf`, QR, `vpn://`, archives, share/download links and public/self-service config delivery behind separate config/public gates. It also binds future `/api/clients` design to explicit `config_delivery_blocked`/`secret_read_gate_required` status and audit reason codes. No AMN2 code, config delivery route, token issue/revoke route, runner code, runtime route, live VPS command, config generation, `/api/clients` CRUD or production mutation was added. Follow-up `WAPI-I001` was selected and completed next.

Phase 4 WAPI-I001 `/api/clients` design without live CRUD 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-i001-clients-design-without-live-crud-2026-06-10.md`. It defines future client list/detail/create/update/disable/revoke route contracts as planning placeholders only, safe client metadata fields, forbidden secret-bearing fields, idempotency/lock requirements, scope rules, audit/status binding and RED test requirements. Runtime `/api/clients` routes, write CRUD, fake-runner code, operation queue, config delivery and live peer mutation remain absent/blocked. No AMN2 code, live VPS command, SSH command, public exposure, Local Agent mutation, backup/import/reboot or production mutation was added. Follow-up `WAPI-I005` was selected and completed next.

Phase 4 WAPI-I005 web-panel gated action labels 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-wapi-i005-web-panel-gated-action-labels-2026-06-10.md`. It defines future panel label vocabulary and interaction rules for read-only metadata, local operation planning, dry-run, blocked/deferred named gates, config delivery blocks, live-write blocks, public exposure blocks and destructive-operation blocks. Labels are not authorization and do not change behavior. No AMN2 code, template change, route behavior change, runtime route, `/api/clients` CRUD, fake-runner code, operation queue, config delivery, live VPS command, public exposure or production mutation was added. Follow-up `NG-N003` was selected and completed next.

Phase 4 NG-N003 operation queue design after write API contract 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-n003-operation-queue-design-2026-06-10.md`. It defines future queue/cancel/retry/status semantics, safe queue fields, forbidden secret-bearing fields, lifecycle boundaries, idempotency/lock rules, retry/cancel constraints, visibility limits, panel label mapping and RED test requirements. No AMN2 code, runtime route, queue implementation, worker implementation, `/api/clients` CRUD, config delivery, live VPS command, public exposure or production mutation was added. Follow-up `NG-N002` was selected and completed next.

Phase 4 NG-N002 health/status polling design 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-n002-health-status-polling-design-2026-06-10.md`. It defines future polling tiers, safe aggregate status fields, forbidden peer/user/secret leakage fields, status vocabulary, staleness behavior, route boundary, operation queue binding and RED test requirements. No AMN2 code, runtime route, polling scheduler, collector, worker, real target polling, config delivery, live VPS command, public exposure or production mutation was added. Follow-up `NG-N001` was selected and completed next.

Phase 4 NG-N001 attach-existing-server read-only reconciliation gate design 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-n001-attach-existing-server-read-only-reconciliation-gate-design-2026-06-10.md`. It defines future read-only reconciliation phases, safe report fields, forbidden secret/peer/user leakage fields, attach/backfill boundaries, conflict handling, health/status binding, operation queue binding and RED test requirements. No AMN2 code, runtime route, reconciliation implementation, attach/import/backfill implementation, real target detection, config delivery, live VPS command, public exposure or production mutation was added. Follow-up `NG-N004` was selected and completed next.

Phase 4 NG-N004 candidate registry update after every gate decision 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-n004-candidate-registry-update-2026-06-10.md`. It synchronized `P4-N006` operation queue/background jobs with `NG-N003`, verified `P4-I007` health/status polling remains bound to `NG-N002`, and verified `P4-N005` attach-existing-server reconciliation remains bound to `NG-N001`. No AMN2 code, runtime route, candidate implementation, reconciliation implementation, attach/import/backfill implementation, operation queue implementation, polling scheduler, collector, worker, config delivery, live VPS command, public exposure or production mutation was added. Follow-up `NG-S001` was selected and completed next.

Phase 4 NG-S001 status/transfer synchronization 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-s001-status-transfer-sync-2026-06-10.md`. It synchronized `docs/PROJECT_STATUS_CURRENT.ru.md` and this transfer backlog after the closed normal P4-NG queue, and kept the active recommendation aligned to remaining simple handoff work. No AMN2 code, runtime route, implementation, route change, config delivery, live VPS command, public exposure or production mutation was added. Follow-ups `NG-S002` and `NG-S004` were selected and completed next.

Phase 4 NG-S002 next-chat handoff synchronization and NG-S004 visible active plan maintenance 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-s002-next-chat-handoff-sync-2026-06-10.md` and `research/amn2/phase-4-ng-s004-visible-active-plan-maintenance-2026-06-10.md`. They synchronized the next-chat handoff packet and removed closed simple tasks from the visible active plan. No AMN2 code, runtime route, implementation, route change, config delivery, live VPS command, public exposure or production mutation was added. Follow-up `NG-X003` was selected and completed next.

Phase 4 NG-X003 stale wording cleanup 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-x003-stale-wording-cleanup-2026-06-10.md`. It removed stale active-next references after the simple-task closure and updated the visible next recommendation to `NG-X001` gate naming consistency. No AMN2 code, runtime route, implementation, route change, config delivery, live VPS command, public exposure or production mutation was added. Follow-up `NG-X001` was selected and completed next.

Phase 4 NG-X001 gate naming consistency 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-x001-gate-naming-consistency-2026-06-10.md`. It aligned stage-level P4-NG gate labels to `P4-NG-*` and kept task ids, route names, branch names, file paths and historical candidate ids unchanged. No AMN2 code, runtime route, implementation, route change, config delivery, live VPS command, public exposure or production mutation was added. Follow-up `NG-X002` was selected and completed next.

Phase 4 NG-X002 Russian-first operator wording polish 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-x002-russian-first-operator-wording-polish-2026-06-10.md`. It made active P4-NG operator-facing headings and next-step wording Russian-first while preserving technical ids, routes, gate names, file paths and candidate ids. No AMN2 code, runtime route, implementation, route change, config delivery, live VPS command, public exposure or production mutation was added. Очередь default docs-only cosmetic теперь закрыта; `NG-V001` later gained the `NG-SC001` Codex Security preflight and was closed as `go`.

Phase 4 NG-SC001 Codex Security VPS risk checkpoint 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-ng-sc001-codex-security-vps-risk-checkpoint-2026-06-10.md`. It adds `Codex Security` threat-model review as a required risk checkpoint before `NG-V001` or any future destructive VPS rebuild gate, with `security_risk_decision: go | no-go | defer`, protected assets, trust boundaries, read-only baseline risks, fresh-rebuild risks and severity calibration. No AMN2 code, runtime route, implementation, route change, SSH/live VPS command, reinstall/rebuild, package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot or production mutation was added. `NG-V001` was later closed as `go`; destructive rebuild is now tracked by separate `VPS-REBUILD-001` and remains blocked until final destructive approval.

Phase 4 NG-V001 read-only VPS baseline gate 2026-06-10: completed as `go` evidence `research/amn2/phase-4-ng-v001-read-only-vps-baseline-gate-2026-06-10.md`. Safe summary confirms SSH transport ok, `amneziya-web` and `amneziya-bot` active/enabled, loopback `/login` HTTP 200, listener `3030` loopback-only, public API `3040` absent, TCP `80/443` absent, `VPS_APPLY_ENABLED=false` and no secret-bearing evidence publication. No package apply, service restart/enable/disable, firewall/reverse proxy edit, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or fresh VPS rebuild was performed. `NG-V001` is removed from the active plan; destructive rebuild is now tracked by separate `VPS-REBUILD-001` as `defer` with no destructive action authorized.

Phase 4 VPS-REBUILD-001 fresh VPS rebuild gate 2026-06-10: opened as AMN3 docs-only preflight evidence `research/amn2/vps-rebuild-001-fresh-vps-rebuild-gate-2026-06-10.md`; plan `docs/superpowers/plans/2026-06-10-vps-rebuild-001-fresh-vps-rebuild.md`. Status is `opened-defer-awaiting-final-destructive-approval`; `security_risk_decision: defer`; `go_no_go_decision: defer`. Novice-safe preflight selected `data_retention_decision=preserve_snapshot_required`, `snapshot_or_backup_decision=provider_snapshot_required`, and `secret_transfer_policy=regenerate_on_target_where_possible + operator_local_channel_only_for_external_secrets`; source candidate is `1508e3c4a100b76815b29f91757290f1266f813d`; package is `dist/amn2-vps-update-and-smoke-kit-1508e3c.zip`; final destructive phrase is `not_sent`. No live VPS command, SSH command, wipe, reinstall, package apply, service stop/restart/enable/disable, firewall/reverse proxy edit, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or secret publication was performed. Any destructive action remains blocked until retention-path decision, stop-criteria review and exact final phrase `GO VPS-REBUILD-001 WIPE TARGET`.

Phase 4 VPS-REBUILD-001 source/package precheck 2026-06-10: completed locally as evidence `research/amn2/vps-rebuild-001-source-package-precheck-2026-06-10.md`. AMN2 source candidate is `1508e3c4a100b76815b29f91757290f1266f813d`; focused local tests passed with `30 passed, 1 warning`; AMN2 remained clean. At source-precheck time, package build was still pending; later `research/amn2/vps-rebuild-001-package-build-hygiene-2026-06-10.md` superseded that package-pending state. Neighboring branches are candidate inputs only and must not be silently merged into the first rebuild package. No live VPS command, SSH command, package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or secret publication was performed.

Phase 4 VPS-REBUILD-001 package build/hygiene 2026-06-10: completed locally as evidence `research/amn2/vps-rebuild-001-package-build-hygiene-2026-06-10.md`. Built `dist/amn2-vps-update-and-smoke-kit-1508e3c.zip`, sha256 `03C51891AF83B9BD2B435AF5F77EEBBAE0DC7289CD107803DE7FB9877C4BFDA3`, and source zip `dist/amn2-codex-vps-test-prep-1508e3c-source.zip`, sha256 `0F4BBD72651FC99197C857093C24AAC9F3927EC9F5B7B7C364B1A312032EF15E`. Package hygiene/test-extract passed and status is only `package-ready-not-vps-smoked`. No live VPS command, SSH command, package apply, wipe/reinstall, service change, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or secret publication was performed. Remaining blockers before final destructive approval: retention-path decision and stop-criteria review.

Phase 4 VPS-FRESH-DEPLOY-001 clean server readiness 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/vps-fresh-deploy-001-readiness-checklist-2026-06-10.md` with plan `docs/superpowers/plans/2026-06-10-vps-fresh-deploy-001-readiness.md`. Result is `fresh_deploy_possible_from_repo_package=yes-with-operator-provided-secrets`, `bare_os_deploy_smoked=no`, `current_vps_disposable_decision=not-set`, `data_loss_acceptance_required_before_wipe=yes`, `delete_actions_planned=no`, `destructive_action_authorized=no`. It clarifies that AMN2 source/package readiness can continue without waiting for provider backup, but current target secrets, local DB/runtime state, peer config material and provider backup history are not rebuildable from repo/package alone. No live VPS command, SSH command, provider action by Codex, wipe/reinstall, package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or secret publication was performed. Remaining decision before destructive work: choose retention path, review stop criteria and require exact final destructive phrase.

Phase 4 VPS-FRESH-DEPLOY-002 clean Ubuntu runbook 2026-06-11: completed as AMN3 docs-only evidence `research/amn2/vps-fresh-deploy-002-clean-ubuntu-runbook-2026-06-11.md`, runbook `docs/AMN2_FRESH_DEPLOY_FROM_ZERO_RUNBOOK.ru.md`, plan `docs/superpowers/plans/2026-06-11-vps-fresh-deploy-002-clean-ubuntu-runbook.md`. It updates the clean deploy instructions for current `1508e3c` package/source, no-domain service-mode, loopback web/admin, SSH tunnel access and `VPS_APPLY_ENABLED=false`. It separates rebuildable app/service-mode state from operator-required secrets, local DB/runtime state, Amnezia keys/peers/configs and provider backup history. No live VPS command, SSH command, provider action by Codex, wipe/reinstall, package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or secret publication was performed.

Phase 4 VPS-REBUILD-001 provider snapshot confirmation 2026-06-10: opened as docs-only operator-confirmation step evidence `research/amn2/vps-rebuild-001-provider-snapshot-confirmation-2026-06-10.md`. Current status is `provider_snapshot_confirmation=defer`; `provider_backup_plan_enabled=yes`; `backup_frequency=monthly`; `backup_created_now=unknown`; `backup_restorable=yes_after_backup_created`; `delete_actions_planned=no`. Codex performed no provider portal action, live VPS command or SSH command. The operator enabled a monthly backup plan, but a created/restorable backup was not confirmed yet, and no deletion is planned. No package apply, wipe/reinstall, service change, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or secret publication was performed.

Phase 4 P4-PRVTPRO-REFRESH-004 API taxonomy/OpenAPI grouping policy support 2026-06-10: completed as AMN3 docs-only evidence `research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md`. It records the PRVTPRO grouping signal as taxonomy policy support while keeping the active private/local read-only API surface exactly six routes, with no generated OpenAPI artifact, public docs exposure, route expansion, config delivery, write API, Local Agent mutation or live VPS work. `WAPI-V002` later used this policy baseline and was also closed. The PRVTPRO-derived item `P4-PRVTPRO-REFRESH-003` was later closed as a carried Phase 4 item: design boundary in AMN3, local cached display by `P5-L001`, live probes/actions still gated.

Service-mode web-panel read-only UX review prep 2026-06-09: next safe local/operator task is a private-panel UX/product review through SSH tunnel using `docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_CHECKLIST.ru.md`, safe return template `docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_EVIDENCE_TEMPLATE.ru.md`, evidence note `research/amn2/service-mode-web-panel-read-only-ux-review-2026-06-09.md` and template note `research/amn2/service-mode-web-panel-read-only-ux-review-evidence-template-2026-06-09.md`. Scope is GET/navigation/labels/empty states/warnings only; no POST/write/config delivery/API token issue/revoke/sync/health/backup/import/reboot/public exposure.

Service-mode web-panel read-only UX review evidence 2026-06-09: passed as `passed-minimal-safe-summary`. Evidence: `research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md`. Operator confirmed baseline (`amneziya-web=active`, `amneziya-bot=active`, loopback `/login=200`, TCP `3030` loopback-only, TCP `3040`/`80`/`443` absent, `VPS_APPLY_ENABLED=false`), then reported authenticated overview review `ok` with no write/config delivery/API token issue-revoke/sync-health/backup-import-reboot actions and no secrets published. Detailed page-by-page UX findings were not returned; collect them in a second pass only if needed.

Status-visibility update 2026-06-07: `amn2/codex-vps-test-prep` advanced to `42ffa65 Record git checkout smoke status`. The app-code read-only smoke slice is `62ff184 Update controlled prod status visibility`, which passed real VPS git-checkout smoke on `/opt/amn2-git` with `checked_routes=6`; AMN3 package `42ffa65` then passed safe source-overlay update/read-only smoke on `/opt/amn2`. That source overlay is now the previous status-visibility baseline, original `api_smoke_run_id=20260607T165625Z`, latest repeat `api_smoke_run_id=20260607T165807Z`. `c8a6363` is historical prior VPS-smoked runtime/source, `run_id=20260606T202040Z`; `32d01fd` and `1a193b9` are older historical baselines.

Follow-up 2026-06-07: `amn2/codex-vps-test-prep` advanced to `c92bd1a Bind web admin systemd to loopback` and the AMN3 package passed safe source-overlay update/read-only smoke on `/opt/amn2`. This is a controlled production launch safety slice: web/admin systemd template uses `127.0.0.1:3030` by default for the approved HTTPS reverse proxy mode. Package: `dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip`, sha256 `EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12`; evidence `research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md` and `research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md`.

Manual runtime 2026-06-07: validation VPS `mirror` passed backup create/verify, safe preflight, API smoke-cycle summary with six read-only routes, manual web `/login` check on `127.0.0.1:3030`, and manual bot runtime check. `systemd` is not used in the current operator mode; direct public web `3030` and public API `3040` are not exposed. Evidence: `research/amn2/c92bd1a-manual-prelaunch-evidence-2026-06-07.md`.

Neighboring AMN2 status follow-up 2026-06-07: `amn2/codex-vps-test-prep` advanced to `f7f6131 Update integration status for c92 manual prelaunch`. This is a read-only status-visibility update to `/api/integration/status` and web `/integration-status`; it has now passed source-overlay update/read-only smoke on `/opt/amn2`. Evidence: `research/amn2/manual-prelaunch-integration-status-2026-06-07.md` and `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`.

Status-alignment package 2026-06-07: AMN3 update+smoke kit for `f7f6131` passed real VPS read-only smoke. Package: `dist/amn2-vps-update-and-smoke-kit-f7f6131.zip`, sha256 `19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282`; source sha256 `720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1`; package evidence `research/amn2/f7f6131-status-alignment-vps-package-2026-06-07.md`; smoke evidence `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`; `source_update_run_id=20260607T203721Z`, `api_smoke_run_id=20260607T203730Z`, `latest_repeat_api_smoke_run_id=20260607T204300Z`, `checked_routes=6`.

Target-server prep 2026-06-08: validation VPS source overlay should remain untouched after `f7f6131` pass. The new rented VPS starts a separate target-server prep gate using `docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md`; detailed runbook `docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md` is used only after safe precheck review, with evidence note `research/amn2/target-server-prep-gate-2026-06-08.md` and safe evidence template `research/amn2/target-server-prep-evidence-template-2026-06-08.md`. This gate covers bootstrap, read-only preflight, API loopback smoke, manual web/admin check and backup verify. Historical note: at this prep stage, service-mode `systemd`/reverse proxy was still a separate explicit decision; Phase 3 later enabled only loopback web/bot service-mode, while reverse proxy/public cutover remains separate.

Target-server bootstrap 2026-06-08: new target VPS partial bootstrap passed. Evidence: `research/amn2/target-server-bootstrap-evidence-2026-06-08.md`. Completed: base packages, Docker runtime installed with no containers, `/opt/amn2` venv, `f7f6131` source overlay, Python dependency install, CLI import, DB schema init, partial loopback API probe for `/api/servers` with token revoke and `forbidden_markers_count=0`, encrypted backup create/verify.

Target-server AWG2 runtime 2026-06-09: new target VPS runtime gate passed. Evidence: `research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md`. Completed: `amnezia-awg2` Docker runtime built/started, `awg0` up, UDP `30001` listening, self-SSH for AMN2 local Docker operations passed, real target `servers.yml` created on the VPS and accepted by AMN2 loader, full read-only API loopback smoke passed with `run_id=20260609T043158Z`, `checked_routes=6`. Live peer apply/revoke remains a separate explicit gate.

Target-server live peer gate 2026-06-09: new target VPS is now `verified-live` for the remote peer apply/revoke primitive. Evidence: `research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md`. Completed: exactly one disposable test peer, `--preshared-key-stdin`, dry-run apply/revoke, live apply/sync/revoke/sync, final peer count `0`, post-gate read-only API smoke `run_id=20260609T045546Z`, `checked_routes=6`. Production peer mutation, public API, config delivery and broader write surfaces remain closed.

Target-server manual web/bot gate 2026-06-09: new target VPS passed manual readiness for bot and web/admin without service-mode. Evidence: `research/amn2/target-server-manual-web-bot-evidence-2026-06-09.md`. Completed: Telegram bot token present on VPS, `bot check-network` passed for `@NeobyatnayaAMNZ_bot`, web admin password hash and session secret present, temporary manual web/admin `/login` returned `200` on `127.0.0.1:3030`, cleanup left TCP `3030`/`3040` absent, AWG2 running and peer count `0`. Service-mode, reverse proxy/public HTTPS cutover, public API, config delivery and broader write surfaces remain closed.

Phase 3A.1 phone live test peer gate 2026-06-09: new target VPS now has one operator-approved phone/desktop test peer left enabled. Evidence: `research/amn2/target-server-phone-live-test-peer-evidence-2026-06-09.md`. Completed: initial failed apply left no remote mutation, free VPN IP was selected without publishing it, repeat dry-run apply/revoke passed, live apply passed, client config was regenerated from live AWG2 parameters with absent `I1`-`I5` fields removed, handshake/RX/TX passed, final peer count is `1`, TCP `3030`/`3040` remain absent, and `VPS_APPLY_ENABLED=false`. Service-mode, reverse proxy/public HTTPS cutover, public API, public/self-service config delivery and production peer/user mutation beyond this single test peer remain closed.

Phase 3A.2 test peers batch gate 2026-06-09: three additional operator-approved test-zone peers were created and left enabled. Evidence: `research/amn2/target-server-test-peers-batch-evidence-2026-06-09.md`. Completed: secret-bearing configs/QRs were generated and downloaded through a private operator channel, final peer count is `4`, TCP `3030`/`3040` remain absent, and `VPS_APPLY_ENABLED=false`. Per-client handshake for those three additional users remains a manual follow-up if needed. Service-mode, reverse proxy/public HTTPS cutover, public API, public/self-service config delivery and production peer/user mutation beyond the four approved test peers remain closed.

Phase 3B.0 service-mode read-only precheck 2026-06-09: target VPS is ready for an explicit service-mode decision but service-mode remains disabled. Evidence: `research/amn2/target-server-service-mode-precheck-evidence-2026-06-09.md`. Completed: source overlay `f7f6131` confirmed, Docker runtime running, peer count `4`, TCP `3030`/`3040` absent, `VPS_APPLY_ENABLED=false`, web/bot systemd templates present with web loopback bind, required bot/web secrets present as markers only, and no `amneziya-web`/`amneziya-bot` systemd unit installed/enabled/active. A named peer activity sample for `Neobyatnaya-AMNZ-1..4` returned `not-yet` at that moment. Next action requires an explicit operator choice: stay in manual runtime mode or open a separate service-mode gate for systemd plus HTTPS reverse proxy.

Phase 3A critical manual-mode cleanup 2026-06-09: secret-bearing delivery artifacts were removed after the four test configs had been downloaded privately. Evidence: `research/amn2/target-server-manual-mode-critical-cleanup-evidence-2026-06-09.md`. Completed: pre-cleanup baseline confirmed peer count `4`, TCP `3030`/`3040` absent and `VPS_APPLY_ENABLED=false`; `.conf`, QR/PNG and delivery archive files were removed from the checked gate locations; post-cleanup control confirmed delivery artifacts `0`, peer count `4`, TCP `3030`/`3040` absent and `VPS_APPLY_ENABLED=false`. Monitoring key files were retained for numbered peer checks without printing keys.

Phase 3A protocol identity and numbered peer check 2026-06-09: after the operator reported that imported configs did not visibly advertise "Amnezia 2.0", the downloaded config metadata and live server config metadata were checked without publishing secret values. Evidence: `research/amn2/target-server-protocol-identity-and-numbered-peer-evidence-2026-06-09.md`. Completed: all four downloaded config metadata samples show 11 core AmneziaWG fields and `0` `I1`-`I5` fields; live server metadata matches 11 core AmneziaWG fields and `0` `I1`-`I5` fields; numbered peer status showed `Neobyatnaya-AMNZ-2=connected-with-traffic`, while `1`, `3` and `4` were `not-yet`. Current conclusion: UI/label ambiguity rather than a wrong plain-WireGuard or Amnezia 1/1.5 export. No regenerate/re-delivery gate is required on this evidence alone.

Phase 3A manual-runtime field test 2026-06-09: read-only numbered live snapshot reached `partial-pass` with three of four approved test peers connected with traffic. Evidence: `research/amn2/target-server-manual-mode-field-test-evidence-2026-06-09.md`. Completed: peer count remained `4`, TCP `3030`/`3040` absent, `VPS_APPLY_ENABLED=false`; `Neobyatnaya-AMNZ-1`, `-2` and `-3` were `connected-with-traffic`, while `-4` remained `not-yet`. This proves real manual-runtime field connectivity for three numbered profiles. Remaining A follow-up: resample `-4` when online and prepare revoke-by-number before expanding the test group.

Phase 3A revoke-by-number runbook 2026-06-09: prepared but not executed. Runbook: `docs/AMN2_MANUAL_MODE_REVOKE_BY_NUMBER_RUNBOOK.ru.md`. It covers safe dry-run and explicit-confirmation live revoke for exactly one `Neobyatnaya-AMNZ-N` test peer, with numbered key resolution, target-present checks, dry-run metadata markers, post-revoke persistent/live absence checks, peer count delta, `3030`/`3040` checks and `VPS_APPLY_ENABLED=false` reset. It does not authorize a revoke by default.

Phase 3A revoke-by-number gate for `Neobyatnaya-AMNZ-3` 2026-06-09: passed. Evidence: `research/amn2/target-server-revoke-by-number-3-evidence-2026-06-09.md`. Completed: dry-run confirmed target present in persistent and live state with `connected-with-traffic`; live revoke removed the target from both persistent config and live interface; live peer count changed from `4` to `3`; TCP `3030`/`3040` remained absent; `VPS_APPLY_ENABLED` was reset to `false`. Immediate post-revoke sample showed remaining peers as `not-yet`, expected after Docker container restart until clients reconnect.

Post-revoke numbered snapshots 2026-06-09: safe state remained stable after the revoke gate. Initial snapshot: peer count `3`, TCP `3030`/`3040` absent, `VPS_APPLY_ENABLED=false`, `Neobyatnaya-AMNZ-3=not-found-on-server`, remaining peers `1`, `2`, `4` still `not-yet` pending fresh reconnect. Later reconnect snapshot after user activity: `Neobyatnaya-AMNZ-1=traffic-seen`, `Neobyatnaya-AMNZ-2=traffic-seen`, `Neobyatnaya-AMNZ-3=not-found-on-server`, `Neobyatnaya-AMNZ-4=not-yet`, with peer count still `3` and TCP `3030`/`3040` absent. This proves manual reconnect/traffic for two remaining peers after the #3 revoke; automatic reconnect remains unproven unless a separate disruption test is approved.

Phase 3 revoke-by-number gate for unused `Neobyatnaya-AMNZ-4` 2026-06-09: passed. Evidence: `research/amn2/target-server-revoke-by-number-4-evidence-2026-06-09.md`. Completed: dry-run confirmed #4 present in persistent/live state with `target_status_before=not-yet`; live revoke removed #4 from both persistent config and live interface; live peer count changed from `3` to `2`; web/bot remained active; loopback `/login` returned `200`; TCP `3030` remained loopback-only; TCP `80/443/3040` absent; `VPS_APPLY_ENABLED` reset false and explicit `.env` false confirmed. Remaining approved test peers are now #1 and #2.

Post-revoke #4 numbered snapshot 2026-06-09: passed. Evidence is included in `research/amn2/target-server-revoke-by-number-4-evidence-2026-06-09.md`. Peer count remained `2`, #3/#4 were `not-found-on-server`, #1/#2 were `not-yet` pending reconnect after the Docker/AWG restart, web/bot active, `/login` loopback `200`, TCP `3030` loopback-only, TCP `80/443/3040` absent and explicit `.env` `VPS_APPLY_ENABLED=false`.

Phase 3B0 service-mode preflight 2026-06-09: completed read-only as `needs-fix-before-B1`. Evidence: `research/amn2/target-server-service-mode-b0-preflight-evidence-2026-06-09.md`. Completed: source overlay `f7f6131`, Docker runtime running, peer count `3`, TCP `3030`/`3040` absent, `VPS_APPLY_ENABLED=false`, web/bot templates present, web template loopback-only, no systemd units installed/enabled/active, web/bot imports pass, no writes performed. Blockers before B1: service user/group `amneziya` missing while templates use `User=amneziya`; effective settings show `WEB_ADMIN_ENABLED=False`; `ADMIN_TELEGRAM_IDS` absent; reverse proxy choice undecided for any later HTTPS cutover.

Phase 3B0.1 service-mode prep and B0 repeat 2026-06-09: completed as `ready-for-B1-loopback-systemd`. Evidence: `research/amn2/target-server-service-mode-b0-1-prep-and-repeat-evidence-2026-06-09.md`. Completed: private admin Telegram ID was supplied on the VPS after one blocked attempt; service user `amneziya` was created; `.env` group/mode set for that service group; web/admin effective settings enabled on loopback; `VPS_APPLY_ENABLED=false` preserved; `/opt/amn2` group permissions fixed so the service user can read app/venv/env and write data/logs. No systemd unit installed or started; reverse proxy unchanged. Repeated B0 shows peer count `3`, TCP `3030`/`3040` absent, templates good, no units installed/active, settings as `amneziya` pass, imports pass. Next action requires separate B1 approval for loopback-only systemd.

Phase 3B1 loopback-only systemd gate 2026-06-09: passed after bounded readiness investigation. Evidence: `research/amn2/target-server-service-mode-b1-loopback-systemd-evidence-2026-06-09.md`. Completed: `amneziya-web` and `amneziya-bot` unit files installed, enabled and active; initial immediate probe saw `curl_rc_7` and absent `3030`, so B1 was held as `needs-investigation`; follow-up diagnostics showed both units active with `Result=success`, `NRestarts=0`, web listening on `127.0.0.1:3030`, `/login` returning `200`, TCP `3040` absent, reverse proxy unchanged and `VPS_APPLY_ENABLED=false`. HTTPS reverse proxy/public cutover remains a separate B2 gate.

Phase 3B2.0 reverse proxy preflight 2026-06-09: completed read-only as `passed-ready-for-choice`. Evidence: `research/amn2/target-server-service-mode-b2-0-reverse-proxy-preflight-evidence-2026-06-09.md`. Completed: web/bot systemd still enabled/active, loopback `/login` `200`, TCP `3030` loopback-only, TCP `3040` absent, TCP `80/443` absent, nginx/Caddy/certbot not installed, no Docker proxy candidate running, UFW inactive, no writes performed. Next B2 step requires domain/package readiness and explicit proxy path selection.

Phase 3B2.1 reverse proxy readiness 2026-06-09: completed read-only as `blocked-before-public-cutover`. Evidence: `research/amn2/target-server-service-mode-b2-1-reverse-proxy-readiness-evidence-2026-06-09.md`. Completed: web/bot systemd remained enabled/active, loopback `/login` `200`, TCP `3030` loopback-only, TCP `3040`, `80` and `443` absent, package candidates for Caddy/nginx/certbot available, and no writes performed. Blockers: selected public host did not resolve from the VPS (`dns_a_count=0`, `dns_aaaa_count=0`) and `.env` did not prove an explicit `VPS_APPLY_ENABLED=false` line. Next step is a small baseline/DNS fix gate, then repeat B2.1 before any Caddy/HTTPS cutover.

No-domain service-mode access decision 2026-06-09: selected SSH local port forwarding instead of public HTTPS cutover because no domain is available. Evidence: `research/amn2/target-server-service-mode-no-domain-ssh-tunnel-decision-2026-06-09.md`; runbook: `docs/AMN2_SERVICE_MODE_SSH_TUNNEL_ACCESS_RUNBOOK.ru.md`. The panel remains loopback-only on the VPS and should be opened from the operator workstation through an SSH tunnel in an external browser, not Codex preview. Reverse proxy/public HTTPS remains deferred until a domain exists and B2.1 is green.

No-domain SSH tunnel access 2026-06-09: passed. Evidence: `research/amn2/target-server-service-mode-ssh-tunnel-access-evidence-2026-06-09.md`. The operator opened the web/admin panel through an SSH local port forward in an external browser; post-open control confirmed web/bot active, loopback `/login` `200`, remote `3030` loopback-only, remote `3040` absent and explicit `.env` `VPS_APPLY_ENABLED=false`. Public HTTPS/reverse proxy remains deferred.

Web-panel tunnel smoke 2026-06-09: passed read-only. Evidence: `research/amn2/target-server-service-mode-web-panel-tunnel-smoke-evidence-2026-06-09.md`. Through the SSH local port forward, `/login` returned `200`, `/` redirected to `/login`, sampled protected GET routes redirected to `/login`, local `127.0.0.1:3040` did not connect, and no POST/write/config delivery was performed. Public HTTPS/reverse proxy remains deferred until a domain exists and B2.1 is green.

Second Telegram admin ID add 2026-06-09: passed. Evidence: `research/amn2/target-server-service-mode-admin-telegram-id-add-evidence-2026-06-09.md`. One additional Telegram admin ID was added privately on the VPS; configured admin count is now `2`, raw IDs were not recorded, `VPS_APPLY_ENABLED=false` remained explicit, bot/web are active, TCP `3030` loopback-only and TCP `3040` absent. Web `/login` returned `200` after a short restart readiness window.

Second admin bot read-only check 2026-06-09: skipped by operator decision to save time. Evidence: `research/amn2/target-server-service-mode-second-admin-bot-check-decision-2026-06-09.md`. The configured admin count remains `2`, but this record does not independently prove the second admin Telegram UI path.

Authenticated web-panel tunnel smoke 2026-06-09: passed read-only. Evidence: `research/amn2/target-server-service-mode-authenticated-web-panel-smoke-evidence-2026-06-09.md`. After login through the SSH local port forward, sampled overview GET pages returned HTTP `200` without redirect. No POST/write/token issue/revoke/sync/health/config-delivery operation was performed. Public HTTPS/reverse proxy remains deferred until a domain exists and B2.1 is green.

Read-only web-panel UX review checklist 2026-06-09: prepared as a docs-only next slice. Checklist: `docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_CHECKLIST.ru.md`; planning note: `research/amn2/service-mode-web-panel-read-only-ux-review-2026-06-09.md`; result evidence: `research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md`. Scope is private operator panel UX/product review through SSH tunnel only: overview pages, navigation, empty states, labels, warnings and copy. POST/write actions, token issue/revoke, sync/health operations, config delivery, backup/import/reboot, public `3030/3040`, reverse proxy and production peer/user mutation remain closed.

Phase 3 final safety snapshot 2026-06-09: passed with source-overlay git metadata unavailable in that specific check. Evidence: `research/amn2/target-server-phase3-final-safety-snapshot-evidence-2026-06-09.md`. Runtime Docker remained running with peer count `3`; numbered status was `Neobyatnaya-AMNZ-1/-2=traffic-seen`, `-3=not-found-on-server`, `-4=not-yet`; web/bot units enabled/active; `/login` loopback `200`; TCP `3030` loopback-only; TCP `80/443/3040` absent; explicit `.env` `VPS_APPLY_ENABLED=false`; production write surfaces/config delivery not opened; reverse proxy/public HTTPS not enabled. Follow-up after this snapshot: bot admin read-only check was skipped by operator, and #4 was later revoked as unused.

Phase 3 handoff 2026-06-09: new chat packet prepared at `docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md`. Next decision: remain in manual runtime mode or run a separate service-mode gate for web/bot `systemd` plus HTTPS reverse proxy. This handoff does not unlock public API `3040`, direct public web/admin `3030`, production peer mutations, config delivery, Local Agent mutations or backup/import/reboot.

Unified prod gate handoff 2026-06-08: prepare a future single decision chat after the active Phase 2 live gate returns a safe summary. Use `docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md` and evidence note `research/amn2/unified-prod-gate-handoff-2026-06-08.md`. Until then, live VPS commands remain owned by the Phase 2 chat; this AMN2/API chat stays integration dispatcher; PRVTPRO/Web Panel remains a candidate source, not a direct production-change source.

`42ffa65` VPS smoke 2026-06-07: source update preserved `.env`, `data/`, `venv/` and `servers.yml`; read-only API smoke passed with `checked_routes=6`, auth 401/403/401, listener `127.0.0.1:3040` loopback-only, audit safe, server DB sync passed. Repeat read-only smoke for the same source overlay also passed with `run_id=20260607T165807Z`. Evidence: `research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md`; repeat evidence: `research/amn2/controlled-prod-status-visibility-vps-repeat-smoke-2026-06-07.md`.

`c8a6363` VPS smoke 2026-06-06: local package SHA/source SHA and source hygiene checks passed, then operator real VPS update/smoke passed with `VPS verdict: pass`. Evidence: `research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md`. The earlier preflight blocker is preserved as historical context at `research/amn2/c8a6363-vps-smoke-preflight-2026-06-06.md`.

Controlled prod decision 2026-06-07: web/admin access is through an operator-approved HTTPS reverse proxy, public API port `3040` is not exposed, recovery artifacts are present, and the final decision is `controlled-prod-ready`. Evidence: `research/amn2/controlled-prod-ready-2026-06-07.md`; access-path confirmation: `research/amn2/controlled-prod-reverse-proxy-confirmation-2026-06-07.md`.

Read-only integration status update 2026-06-06: `32d01fd` updates `/api/integration/status` to report `read_only_vps_smoked`, Phase 2 `verified_live`, and controlled-prod readiness pending without enabling write routes or write operations. AMN3 evidence is `research/amn2/integration-status-controlled-prod-update-2026-06-06.md`. The previous local-only operation-contract fast-forward remains recorded at `research/amn2/remote-partial-failure-contract-2026-06-06.md`.

```text
AMN3 package: dist/amn2-vps-update-and-smoke-kit-32d01fd.zip
sha256: BE59AF74001AC4F094C753B565A4E672194D823C4F65B6CB476F4FF01B310807
source zip: dist/amn2-codex-vps-test-prep-32d01fd-source.zip
source sha256: 034753DA7EC42ACF869519F43909EEFDC8A392A5665B2A33C935F8A058CCB99B
current source-overlay package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
current source-overlay package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
current source-overlay source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
current source-overlay package status: read-only-vps-smoke-pass
local verification: focused deploy tests 11 passed; package SHA/source SHA/no-BOM/no-CRLF/no-forbidden-source-entry/test-extract checks passed
package evidence: research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md
VPS result for c92bd1a: read-only-vps-smoke-pass, run_id 20260607T182131Z, checked_routes=6
VPS smoke evidence: research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md
previous VPS-smoked runtime/source: 42ffa65, promotion run_id 20260607T165625Z, repeat run_id 20260607T165807Z, evidence research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md
previous VPS-smoked runtime/source: 1a193b9, run_id 20260606T154636Z, evidence research/amn2/remote-partial-failure-contract-vps-smoke-evidence-2026-06-06.md
controlled prod readiness: controlled-prod-ready
manual runtime validation: passed; systemd not-used; web_process present; bot_process present; public 3030/3040 no
current AMN2 git head: f7f6131 Update integration status for c92 manual prelaunch
current AMN2 git head status: read-only status visibility, VPS source-overlay-smoked
current AMN2 git head evidence: research/amn2/manual-prelaunch-integration-status-2026-06-07.md
status-alignment package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
status-alignment package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
status-alignment source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
status-alignment package status: read-only-vps-smoke-pass
status-alignment VPS smoke: passed, run_id 20260607T203730Z, latest_repeat_api_smoke_run_id 20260607T204300Z, checked_routes=6
current app-code read-only smoke slice: 62ff184 Update controlled prod status visibility
current VPS-smoked package/source: f7f6131, run_id 20260607T203730Z, latest_repeat_api_smoke_run_id 20260607T204300Z, checked_routes=6
git-checkout VPS smoke: 62ff184 pass on /opt/amn2-git, checked_routes=6
source-overlay package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
source-overlay package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
source-overlay source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
source-overlay package status: read-only-vps-smoke-pass
controlled prod runbook: docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
controlled prod evidence: research/amn2/controlled-prod-readiness-2026-06-06.md
controlled prod next chat: docs/NEXT_CHAT_AMN2_CONTROLLED_PROD_DECISION.ru.md
previous VPS-smoked source: 568c611, run_id 20260605T162742Z, evidence research/amn2/phase-2-post-psk-stdin-vps-smoke-evidence-2026-06-05.md
docs-only cleanup: 6b5b5b7 Document stdin PSK peer apply
local-only contract merge: 1a193b9 Add remote partial failure contract
read-only integration status update: 32d01fd Update integration status for controlled prod
```

Актуализация 2026-06-05: Phase 2 live single disposable test peer apply/revoke gate пройден на current stable `amn2/codex-vps-test-prep` head `7764ae7 Cover integration status in API smoke`.

```text
AMN3 evidence: research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md
result: verified-live
scope: exactly one disposable test peer apply/revoke, no production peer
```

Актуализация 2026-06-04: Phase 1 read-only/API/web-panel baseline закрыт на `amn2/codex-vps-test-prep` head `7764ae7 Cover integration status in API smoke`.

```text
AMN3 evidence: research/amn2/phase-1-closeout-2026-06-04.md
current update+smoke kit: dist/amn2-vps-update-and-smoke-kit-7764ae7.zip
sha256: 832E1B1F6516A02E0D6AA45672B8FF526DF15D27117D2063CE45F9966825A66A
```

Phase 2 live single test peer apply/revoke now has `verified-live` evidence for exactly one disposable peer. Старые строки `294803e` ниже остаются historical API/web-panel evidence.

Дата: 2026-06-02.

Назначение: единая очередь переноса AMNEZIYA-наработок и upstream-идей из AMN3 в production repo `amn2`.

Правило: AMN3 хранит статус, решение, plan, branch/commit/PR links и test evidence. Production-код остается в `C:\Users\SooL\Documents\Amneziya` / `barakov-dot/amn2`.

## Verified Production Baseline

Verified live `amn2` baseline:

```text
branch: codex-vps-test-prep
latest: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Текущий production head после merged API/VPS evidence transfer:

```text
5f12736 Record VPS API smoke evidence
```

В эту линию уже вошли PR #4/#5 по API token lifecycle и PR #6 по SSH host key verifier. Scoped API token storage `1fdcde5` остается важным baseline, но больше не является текущим production head.

Текущая active implementation branch для установки/API smoke:

```text
branch: codex/read-only-api-route-shell
remote branch: amn2/codex/read-only-api-route-shell
head: 2010d60 Add API VPS smoke evidence template
base: d0939d8 Merge pull request #6 from barakov-dot/codex/ssh-host-key-identity-verifier
status: merged into codex-vps-test-prep at 5f12736 after local tests and real VPS loopback API smoke
working chat: Переводим AMN на API
```

Актуализация 2026-06-03: latest real VPS API-only smoke passed на `/opt/amn2` через AMN3 operator script, `run_id=20260603T112418Z`; DB-only server config sync выполнен, preflight `skipped`, API/auth/scope/revoke/listener/audit `passed`, `VPS_APPLY_ENABLED=false`, raw token/header/hash/config/keys/PSK не публиковались. Evidence: `research/amn2/api-vps-smoke-evidence-2026-06-03.md`.

Live VPS cycle подтвержден на Docker AmneziaWG runtime:

- approve создает рабочий peer;
- config работает;
- `Working configs on server` обновляется сразу;
- `Run peer sync` подтверждает `confirmed live`;
- внешние Amnezia-created peer не удаляются;
- missing local device можно добавить на сервер;
- disable/enable работают;
- выборочное удаление устройства работает.

## Active Items

| Item | Статус | Target repo | Текущий artifact | Следующий шаг |
| --- | --- | --- | --- | --- |
| API readiness after verified live baseline | `implemented-historical-baseline` | AMN3 -> `amn2` | `research/amn2/api-readiness-audit-after-live-baseline.md`; Route/Auth matrix and read-only API shell already implemented | Использовать как historical decision source; VPS loopback API smoke для `codex/read-only-api-route-shell` passed 2026-06-02 |
| Main merge roadmap | `active-roadmap` | AMN3 -> `amn2` later | `docs/AMN2_MAIN_MERGE_ROADMAP.ru.md` | Использовать как порядок слияния API, web panel и operations |
| Local Amnezia Agent first slice | `merged-in-baseline` | `amn2` | merge PR #2, commits `3119ee6`, `ac2baa8` | Использовать как read-only baseline, не расширять до clients/configs без policy gate |
| Local Agent production wiring | `merged-in-baseline` | `amn2` | merge PR #3, head `8697b60` | Использовать как opt-in local runtime adapter boundary |
| VPS retest bundle | `verified-live-baseline` | `amn2` | commit `573c368` | Не трогать без изменения VPS apply/sync логики |
| Config defaults from `.env` | `verified-live-baseline` | `amn2` | commit `8ecb0b4` и последующие fixes | Использовать как текущий config contract |
| Docker runtime peer apply/revoke | `verified-live-baseline` | `amn2` | `codex-vps-test-prep`, tag `vps-live-cycle-verified` | Использовать как behavior contract |
| Redaction coverage | `implemented-pushed-local-gate-complete` | `amn2` | commits `75c235a`..`94ad807` | Использовать как secret-output baseline; VPS gate не нужен |
| Verified config delivery | `implemented-pushed-local-gate-complete` | `amn2` | commits `952cc49`, `4b19cd3`, `fc73929`; verified at `94ad807` | Использовать как artifact integrity baseline; VPS gate не нужен |
| Public-token safety | `implemented-pushed-local-gate-complete` | `amn2` | commit `dfe27ee`; tests `14 passed`, full suite `535 passed` | Использовать как verify/recover token baseline; VPS gate не нужен |
| Local Agent hardening | `implemented-pushed-local-gate-complete` | `amn2` | commit `c5d7eb6`; focused tests `64 passed`, full suite `536 passed` | Использовать как read-only audit/version contract; VPS gate не нужен |
| Remote operation VPS gate candidate | `verified-live-on-current-stable` | `amn2` branch + AMN3 evidence | historical branch `codex/remote-operation-vps-gate-prep`, head `7281254`, is merged into stable via `708c98e` and is ancestor of `7764ae7`; current Phase 2 evidence `research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md`; read-only baseline package `dist/amn2-vps-update-and-smoke-kit-7764ae7.zip`, sha256 `832E1B1F6516A02E0D6AA45672B8FF526DF15D27117D2063CE45F9966825A66A` | Phase 2 live single disposable peer apply/sync/revoke/sync passed; keep broad write/API/config/backup/agent mutation surfaces behind separate gates |
| VPS gate evidence/merge package | `verified-live-evidence-recorded` | AMN3 | `phase-2-live-vps-gate-evidence-2026-06-05.md`, `remote-operation-vps-gate-evidence-2026-06-04.md`, `vps-gate-evidence-checklist.md`, `post-vps-gate-merge-decision.md`, `neighbor-chat-vps-gate-handoff.md` | Use result `verified-live` for exactly one disposable test peer; broad write integration remains blocked behind route/secret/remote-write gates |
| Post dry-run read-only integration status | `phase-1-closeout-pushed` | `amn2` stable branch + AMN3 evidence | branch `codex/post-dry-run-read-only-integration`, commits `55a7ed6`, `7764ae7`; evidence `research/amn2/post-dry-run-read-only-integration-implementation.md`, `research/amn2/phase-1-closeout-2026-06-04.md`; focused `39 passed`, full `610 passed` | Read-only API/web status surface готов и включен в API smoke; Phase 2 live apply/revoke вынести в отдельный чат/gate |
| VPS install/update package | `read-only-vps-smoke-pass-f7f6131` | AMN3 package for `amn2` | source-overlay update+smoke kit `dist/amn2-vps-update-and-smoke-kit-f7f6131.zip`, sha256 `19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282`; source `dist/amn2-codex-vps-test-prep-f7f6131-source.zip`, sha256 `720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1`; package evidence `research/amn2/f7f6131-status-alignment-vps-package-2026-06-07.md`; VPS smoke evidence `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`; previous c92 VPS-smoked kit `dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip`, `run_id=20260607T182131Z` | `f7f6131` is the current VPS-smoked runtime/source baseline. Keep `VPS_APPLY_ENABLED=false`; live write remains a separate gate |
| Controlled prod readiness | `controlled-prod-ready-manual-runtime-pass` | AMN3 operator gate | `docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md`; handoff `docs/NEXT_CHAT_AMN2_CONTROLLED_PROD_DECISION.ru.md`; readiness evidence `research/amn2/controlled-prod-readiness-2026-06-06.md`; reverse proxy confirmation `research/amn2/controlled-prod-reverse-proxy-confirmation-2026-06-07.md`; final decision `research/amn2/controlled-prod-ready-2026-06-07.md`; current VPS-smoked package/source `f7f6131`, read-only VPS smoke `run_id=20260607T203730Z`, latest repeat API smoke `20260607T204300Z`, `checked_routes=6`; manual runtime evidence `research/amn2/c92bd1a-manual-prelaunch-evidence-2026-06-07.md`; web/admin systemd template confirmed loopback-only at previous c92 baseline and status-aligned at f7 | Validation VPS manual runtime passed: web/admin and bot are operator-started manually, `systemd` is not used, direct public `3030`/`3040` exposure is no. This is not public API `3040`, not broad write/API/config/backup/agent surfaces |
| Controlled prod status visibility | `source-overlay-vps-smoke-pass` | `amn2` stable branch + AMN3 evidence | VPS-smoked AMN2 head `42ffa65`; app-code smoke slice `62ff184`; git-checkout evidence `research/amn2/controlled-prod-status-visibility-git-checkout-smoke-2026-06-07.md`; source-overlay evidence `research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md`; AMN2 source docs `docs/API_VPS_SMOKE_EVIDENCE.ru.md` and `docs/AMN2_VPS_SMOKE_62FF184_RUNBOOK.ru.md` | Promotion completed for read-only status visibility. Current git head later advanced to `f7f6131`; no write/config/backup/agent mutation unlock |
| Controlled prod status visibility package | `read-only-vps-smoke-pass` | AMN3 package for `amn2` | `dist/amn2-vps-update-and-smoke-kit-42ffa65.zip`, sha256 `5B43B467E014E87FEC1E49E8D9A8B7A2FBF841541BE88FDC6768097806240E39`; source sha256 `8A5B83D9AB95BE4230AAC221CE0321A37EF37E4E4B6EAB5EDECAE3C98A944829`; package evidence `research/amn2/controlled-prod-status-visibility-vps-package-2026-06-07.md`; smoke evidence `research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md` | Operator can rerun read-only smoke with `VPS_APPLY_ENABLED=false`; `/opt/amn2` is promoted to `42ffa65` |
| Web-admin loopback systemd package | `manual-runtime-pass-systemd-not-used` | AMN3 package for `amn2` | AMN2 head `c92bd1a`; `dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip`, sha256 `EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12`; source sha256 `272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2`; package evidence `research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md`; smoke evidence `research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md`; manual runtime evidence `research/amn2/c92bd1a-manual-prelaunch-evidence-2026-06-07.md` | Source-overlay update/smoke and manual web/bot runtime checks passed; `systemd` is not used in current operator mode. Keep backend on `127.0.0.1:3030`, API `3040` loopback-only |
| Docker manager safety note | `prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/docker-manager-design-note.md` | Использовать как вход для будущего implementation plan после VPS evidence |
| SSH host key enrollment design | `design-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/ssh-host-key-enrollment-design.md` | Использовать как policy gate перед VPS onboarding, web/API remote operations и app-managed host key pinning |
| SSH host key identity verifier | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/ssh-host-key-identity-verifier`, commit `dd20364`; evidence `research/amn2/ssh-host-key-verifier-implementation.md`; focused `29 passed`, full `550 passed` | Использовать как merge/cherry-pick candidate перед live VPS gate; следующий шаг - подключать к SSH-backed operations только отдельным gated slice |
| Route/Auth machine-checkable binding tests | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/route-auth-binding-tests`, commit `f9d2c79`; RED `1 import error as expected`; focused `22 passed`; full suite `549 passed` | Использовать как route/policy drift guard; VPS gate не нужен |
| Secret inventory registry | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/secret-inventory-registry`, commit `9ce42f4`; evidence `research/amn2/secret-inventory-registry-implementation.md`; RED `1 import error as expected`; focused `64 passed`; full suite `591 passed` | Использовать как machine-checkable secret baseline; route/API secret-bearing output остается отдельным gate |
| Backup/import dangerous API design | `design-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/backup-import-dangerous-api-design.md` | Использовать как gate перед backup/import web/API routes, restore preview и full backup dangerous mode |
| Backup/import policy contract | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/backup-import-policy-contract`, head `afb2702` with foundation commit `d2c160b`; evidence `research/amn2/backup-import-policy-contract-implementation.md`; RED `1 import error as expected`; focused `61 passed`; full suite `584 passed` | Использовать как no-route backup/import policy baseline; web/API full backup, restore apply и import apply остаются отдельными gates |
| Manager config export contract | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/manager-config-export-contract`, commit `4d4e7a4`; evidence `research/amn2/manager-config-export-contract-implementation.md`; focused `40 passed`, full `560 passed` | Использовать как no-route typed export adapter baseline; public/self-service endpoints, API `config:read` и Local Agent `/configs` остаются отдельными gates |
| Public/self-service config delivery policy | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/public-config-delivery-policy-contract`, commit `2ef3af7`; evidence `research/amn2/public-config-delivery-policy-contract-implementation.md`; focused `94 passed`, full `577 passed` | Использовать как no-route share-token/policy baseline; public download, self-service download, API `config:read` и Local Agent `/configs` остаются отдельными gates |
| Packaging discovery fix | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/read-only-api-route-shell`, commit `e99d5f3 Fix editable install package discovery` | Считать install/startup blocker закрытым для API smoke branch; проверять на VPS через editable install |
| KYORESUAS API integration priority | `merged-in-stable-read-only-api` | AMN3 -> `amn2` | `research/amn2/kyoresuas-api-integration-priority-plan.md`; `amn2/codex/read-only-api-route-shell`; latest evidence `research/amn2/api-vps-smoke-evidence-2026-06-03.md`; production head `5f12736` | Использовать как merged read-only API baseline; upstream code не копировать |
| Read-only API route shell | `merged-in-stable` | `amn2` | branch `codex/read-only-api-route-shell`, commits `6534ac4`, `9cccdc2`, `b37103a`, `2010d60`, `5f12736`; full suite `588 passed`; focused merge check `75 passed`; latest real VPS smoke passed `run_id=20260603T112418Z`; operator script `scripts/vps/amn2_api_loopback_smoke.sh`; update+smoke kit `dist/amn2-vps-update-and-smoke-kit-5f12736.zip` | Считать first read-only API baseline merged; дальнейшее route expansion только через отдельные gates |
| API/Web panel finish slice | `verified-real-vps-api-web-panel-read-only` | `amn2` stable branch + AMN3 evidence | branch `codex/api-web-panel-finish`, commit `294803e`; fast-forward merged into `codex-vps-test-prep`; local evidence `research/amn2/api-web-panel-finish-implementation.md`; real VPS evidence `research/amn2/api-web-panel-vps-evidence-2026-06-04.md`; package `dist/amn2-vps-update-and-smoke-kit-294803e.zip`; API loopback smoke `run_id=20260604T102355Z` | Считать API readiness/API tokens web slice verified on real VPS for read-only gate; route/API expansion and remote-write operations remain closed |
| Read-only metrics privacy classification | `classification-used-by-api-shell` | AMN3 -> `amn2` | `research/amn2/read-only-metrics-privacy-classification.md` | Держать как privacy baseline для aggregate-only API; detailed client metrics остаются заблокированы |
| Local Agent runtime metadata alignment | `merged-stable-read-only-vps-smoked` | `amn2` stable branch + AMN3 evidence | `amn2/codex-vps-test-prep` at `c8a6363`; branch `amn2/codex/local-agent-runtime-summary`; `research/amn2/local-agent-runtime-metadata-alignment.md`; `docs/superpowers/specs/2026-06-06-local-agent-runtime-summary-design.md`; `docs/superpowers/plans/2026-06-06-local-agent-runtime-summary.md`; `research/amn2/local-agent-runtime-summary-implementation-2026-06-06.md`; VPS evidence `research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md` | Mapper-only controller-safe runtime summary merged into stable and read-only VPS-smoked; no clients/configs, no API route, no VPS write command; mutation surfaces remain separate gates |
| API token rotation/revoke policy | `policy-prepared-local-docs` | AMN3 -> `amn2` later | `research/amn2/api-token-rotation-revoke-policy.md` | Policy остается design source для route expansion и Local Agent token separation |
| API token lifecycle gate | `implemented-pushed-local-gate-complete` | `amn2` | branch `codex/api-token-lifecycle-gate`, commit `c2ba646`; stacked branch `codex/api-token-lifecycle-gate-stacked`, commit `256d0c0` поверх `codex/route-auth-binding-tests`; evidence `research/amn2/api-token-lifecycle-gate-implementation.md`; stacked focused `56 passed`, full `555 passed` | Использовать как service/repository lifecycle baseline; `/api/*` routes, `config:read`, write scopes и bearer-token route exposure остаются отдельными gates |
| Web panel safe improvements | `implemented-pushed-local-gate-complete` | `amn2` | commit `22dfc37`; RED `4 failed as expected`; focused `75 passed`; full suite `536 passed` | Использовать как operator safety wording baseline; VPS gate не нужен |
| Scoped API token storage | `implemented-pushed-local-gate-complete` | `amn2` | commit `1fdcde5`; RED `1 import error as expected`; focused `54 passed`; full suite `542 passed` | Использовать как hash-only token baseline; lifecycle gate выполнен отдельным branch `codex/api-token-lifecycle-gate`, а для очереди после route/auth binding есть stacked branch `codex/api-token-lifecycle-gate-stacked`; VPS gate не нужен |
| Public/self-service config delivery | `lab-only-until-policy` | AMN3 -> `amn2` later | `research/amn2/config-delivery-inventory.md` | Не открывать public config links до scoped token/self-service design |

## Local Agent Decision

Решение: переносить как собственную реализацию `amn2`, без копирования внешнего `kyoresuas/amnezia-api`.

Причина:

- задача совпадает с целевым продуктом: API-first управление пользователями Amnezia;
- текущий first slice уже защищен route policy, hash-only token auth, typed auth errors и no-write boundary;
- ближайший production gain - получить opt-in local runtime adapter на сервере, который controller сможет опрашивать безопасно; safety boundary для этого зафиксирован в `research/amn2/local-agent-runtime-metadata-alignment.md`;
- verified VPS baseline теперь дает реальный behavior contract для будущих write операций.

## Transfer Gates

Любая новая функция из AMN3 переходит в `amn2` только если есть:

- source/license verdict;
- current `amn2` inventory;
- risk class;
- route/auth policy;
- secret and audit decision;
- tests;
- rollback/recovery note for state-write or remote operations;
- AMN3 return note after branch/commit/PR.

## Current Priority Order

1. Считать first read-only API shell merged в stable `codex-vps-test-prep` at `5f12736`.
2. API/web-panel finish slice реализован, fast-forward merged в stable `codex-vps-test-prep` at `294803e`; Phase 1 read-only integration status follow-up pushed at `7764ae7`; local full suite `610 passed`.
3. Не расширять API route surface в этом slice: `/api/clients` write CRUD, API `config:read`, public config delivery, backup/import/reboot, public docs/metrics и detailed client metrics остаются заблокированы до отдельного решения.
4. VPS API/web-panel gate для production head `294803e` пройден: API loopback smoke `run_id=20260604T102355Z`, web-admin route check passed; evidence `research/amn2/api-web-panel-vps-evidence-2026-06-04.md`.
5. Controlled real VPS verification gate Phase 2 пройден на current stable `7764ae7` как `verified-live` для ровно одного disposable test peer apply/sync/revoke/sync; API/web/agent routes, которые вызывают SSH, sync peers, emit config или меняют runtime state, все равно остаются отдельными gated slices.
6. Post dry-run read-only integration status реализован в `amn2/codex/post-dry-run-read-only-integration` at `55a7ed6`, затем закрыт follow-up `7764ae7`, который добавляет `/api/integration/status` в API smoke; это только API/web visibility, без live writes. Phase 2 live apply/revoke вынести в отдельный чат/gate.
7. Route/Auth binding tests, scoped API token lifecycle, secret inventory, public config policy and backup/import policy остаются обязательными baselines перед route expansion.
8. Domain exclusions и 2FA держать отложенными до закрытия текущих safety gates.

## Neighbor Chat Decision

`VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`:

- broad research paused;
- keep as targeted input for web-panel UX, route taxonomy, config delivery integrity and dangerous-action UX;
- no code/UI/templates/managers/scripts copied because GPL-3.0.

`VPN Ops Lab — KYORESUAS-API`:

- теперь является источником product direction для собственной `amn2` API lane;
- активная реализация идет в `amn2/codex/read-only-api-route-shell`, не через копирование upstream code;
- no broad CRUD/write API, no `config:read`, no backup/import/reboot before policy/secret/remote-write gates.

## Когда нужен новый live retest

Новый live retest обязателен, если меняется хотя бы одно из:

- peer apply/revoke;
- config template/defaults;
- IP allocation;
- peer sync classification;
- disable/enable/delete device flows;
- Docker runtime write/restart behavior.

## Route/Auth/Operation Policy Matrix Plan

Статус: `implemented-in-amn2-local-commit`.

Plan artifact:

```text
docs/superpowers/plans/2026-05-31-amn2-route-auth-operation-policy-matrix.md
```

Production branch:

```text
codex-vps-test-prep
```

Production commit:

```text
d1d9690 Add route auth operation policy matrix
```

Created in `amn2`:

- `app/security/surface_policy.py`
- `tests/security/test_surface_policy.py`
- `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`

Verification:

```text
tests/security/test_surface_policy.py tests/agent/test_policy.py tests/server/test_operation_runner.py tests/server/test_checks.py -v
result: 46 passed

tests/web/test_app.py tests/web/test_users.py tests/web/test_servers.py tests/web/test_email_delivery.py tests/bot/test_bot_workflows.py -v
result: 85 passed, 1 StarletteDeprecationWarning
```

Note: pytest emitted the known Windows temp cleanup `PermissionError` after successful sessions; both commands returned exit code 0.

Границы slice:

- live VPS не трогать;
- новых endpoints не добавлять;
- config/self-service API не добавлять;
- Local Agent clients/configs/backup/restore/reboot не включать;
- upstream code не копировать.

## Local Gate / Live VPS Gate

Все следующие transfer items делятся на два контура.

### Local gate

Можно выполнять и коммитить после локальных тестов:

- policy/inventory-only registry;
- redaction coverage;
- config delivery artifact tests;
- web/bot TestClient smoke;
- Local Agent read-only/auth/token hardening на fake/local runtime;
- remote operation contract tests на fake SSH/client;
- docs/status/backlog updates.

### Live VPS gate

Отдельная проверка на реальном VPS нужна только после local green, если item меняет:

- peer apply/revoke;
- disable/enable/delete;
- add missing local device to server;
- remove unknown remote peer;
- peer sync classification;
- config templates/defaults, которые попадут в рабочий client config;
- Docker AmneziaWG write/reload/restart behavior;
- real Local Agent deployment или controller-to-agent calls.

Policy matrix commit `d1d9690` остается `local-gate-complete`; live VPS gate для него не нужен.

Redaction coverage commits `75c235a`..`94ad807` также остаются `local-gate-complete`: они усиливают sanitizer, тесты и docs, но не меняют live apply/revoke/config/sync behavior.

Config delivery integrity на head `94ad807` также остается `local-gate-complete`: `.conf` UTF-8 bytes, QR payload, `vpn://` round-trip, non-ASCII fixture и secret metadata подтверждены локальными тестами; live VPS gate не нужен, пока не меняются реальные templates/defaults или apply/sync behavior.

Public-token safety commit `dfe27ee` также остается `local-gate-complete`: TTL guard, hash-only token contract, verify/recover purpose separation, expired-code rejection, generic denial/no raw token echo и no-consume failure behavior подтверждены локальными тестами. Live VPS gate не нужен, потому что slice не меняет peer apply/revoke/config/sync/runtime behavior.

Local Agent hardening commit `c5d7eb6` также остается `local-gate-complete`: `agent serve` подключает repository-backed audit sink для allowed read routes, `/agent/version` публикует runtime contract metadata, а tests подтверждают отсутствие raw bearer token в audit. Live VPS gate не нужен, потому что slice не делает real agent deployment, controller-to-agent calls, peer apply/revoke/config/sync/runtime writes.

Remote operation VPS gate branch `codex/remote-operation-vps-gate-prep` обновлена поверх stable head `294803e` и запушена как `7281254`: dry-run metadata, Runtime Registry, SSH host key verifier baseline и API/web-panel baseline подтверждены локально. Real VPS Phase 1 read-only/dry-run verification пройден 2026-06-04 как `dry-run-only-pass`; Phase 2 live single disposable peer apply/revoke пройден 2026-06-05 на current stable `7764ae7` как `verified-live`.

Web panel safe-improvements commit `22dfc37` также остается `local-gate-complete`: это wording/UI-test слой без изменения apply/revoke/config/sync/runtime behavior. Live VPS gate не нужен.

Scoped API token storage commit `1fdcde5` также остается `local-gate-complete`: добавлены `api_tokens` table, hash-only service contract, one-time raw token issue metadata, expiry/revoke/last-used fields, allowed first-slice scopes `server:read` и `metrics:read`, а `/api/*` routes не добавлены. Live VPS gate не нужен, потому что slice не меняет live apply/revoke/config/sync/runtime behavior.

Route/Auth binding tests commit `f9d2c79` также остается `local-gate-complete`: добавлены inventory-only route bindings, web runtime route drift tests, Local Agent blocked-future assertions и test-ref integrity check. Slice не добавляет endpoints, не меняет web/bot/agent/CLI behavior и не трогает live VPS.

Manager config export contract commit `4d4e7a4` также остается `local-gate-complete`: добавлен no-route typed export adapter для существующего `DeviceConfigDelivery`/`ConfigDeliveryPackage`, safe metadata и stable error categories. Slice не добавляет public/self-service endpoint, API `config:read`, Local Agent `/configs`, новый QR/import behavior или live VPS calls.

Public/self-service config delivery policy commit `2ef3af7` также остается `local-gate-complete`: добавлен no-route hash-only share-token/policy contract, `config_share_tokens` storage, blocked future policy entries and safe audit/backup metadata. Slice не добавляет public download route, self-service download route, API `config:read`, Local Agent `/configs`, generated config persistence, новый QR/import behavior или live VPS calls.

Backup/import policy contract head `afb2702` (foundation commit `d2c160b`) также остается `local-gate-complete`: добавлен no-route backup mode registry, secret field policy, safe manifests, restore/import preview-only contracts and blocked future `SurfacePolicy` entries. Slice не добавляет `/api/*`, web/Local Agent backup routes, restore apply, import apply или live VPS calls.

Secret inventory registry commit `9ce42f4` также остается `local-gate-complete`: добавлен machine-checkable `app.security.secret_inventory`, safe manifest, lookup/filter helpers and backup policy cross-checks. Slice не читает `.env`, не подключается к БД, не добавляет routes, secret-bearing output или live VPS calls.

Bot config delivery localization commit `908cafc` также остается `local-gate-complete`: Telegram config delivery стал Russian-first, `vpn://` и app links отправляются отдельными сообщениями, filenames строятся от device name, initial default name `Neobyatnaya-AMNZ-{order_id}` был позднее superseded by device-sequence slice `59bc266`, QR caption больше не обещает universal DefaultVPN in-app QR compatibility. Full local AMN2 suite: `630 passed, 1 warning`. Slice не выполнял live bot deploy/restart, real config delivery by Codex, live VPS commands, production peer/user mutation, public exposure or upstream code copy.

Device sequence/external import visibility commit `59bc266` также остается `local-gate-complete`: новые bot-approved devices получают сквозные names `Neobyatnaya-AMNZ-N` с default seed `4`, so the next fresh local DB issue is `Neobyatnaya-AMNZ-5`; existing test peers can be backfilled through local external-only import so bot and web/admin user detail see them without pretending config material is recoverable. External-only rows block resend, secrets reveal and email-config because original client private key/config material is unavailable. Focused local suite: `171 passed, 1 warning`; full local AMN2 suite: `644 passed, 1 warning`. Slice не выполнял live bot deploy/restart, real config delivery by Codex, live VPS commands, production peer/user mutation, public exposure, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or upstream code copy. Перед любым VPS package apply/rebuild нужно пересобрать package from selected current AMN2 head and rerun source/package precheck because previous rebuild package was built from `1508e3c`.

Amnezia client compatibility matrix commit `d2e234f` также остается `local-gate-complete`: добавлен machine-checkable `app.vpn.client_compatibility` для `.conf`, `vpn://`, QR `vpn://` payload, DefaultVPN reliability, standalone AmneziaWG clients and current AmneziaVPN platform constraints; bot app-links message now includes safe Russian compatibility guidance without raw config material. Evidence: `research/amn2/phase-4-amnezia-client-compatibility-matrix-2026-06-11.md`. Focused local suite: `69 passed`; full local AMN2 suite: `650 passed, 1 warning`. Slice не выполнял live bot deploy/restart, real config delivery by Codex, live VPS commands, production peer/user mutation, public exposure, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or upstream code copy. Its bot asset check found no bot-specific header image or `/start` language selector at that time; this was superseded by the later bot onboarding slice `137d471`. Перед любым VPS package apply/rebuild нужно пересобрать package from selected current AMN2 head and rerun source/package precheck because previous rebuild package was built from `1508e3c`.

Bot onboarding language/header commit `137d471` также остается `local-gate-complete`: текущий access bot получил supplied `NEOBYATNAYA-AMNZ-BOT.png`, `/start` sends the header as a Telegram photo, shows `🌐 Выберите язык / Choose your language:` with `🇷🇺 Русский` and `🇬🇧 English`, persists `users.locale` with Russian default and renders the selected main-menu locale. Evidence: `research/amn2/phase-4-bot-onboarding-language-header-2026-06-11.md`. Focused local suite: `5 passed`; full local AMN2 suite: `654 passed, 1 warning`. Support/news/admin images were recorded for future planning only and were not enabled in the current bot runtime. Slice не выполнял live bot deploy/restart, real config delivery by Codex, live VPS commands, production peer/user mutation, public exposure, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or upstream code copy. Перед любым VPS package apply/rebuild нужно пересобрать package from selected current AMN2 head `137d471` and rerun source/package precheck because previous rebuild package was built from `1508e3c`.

Runtime/toolchain standardization commit `578d91e` также остается `local-gate-complete`: AMN2 now pins supported Python to `>=3.12,<3.13`, adds `app.toolchain` and `python -m app.toolchain check`, documents CPython 3.12.x bootstrap in `docs/RUNTIME_TOOLCHAIN.ru.md`, and requires one local `.venv` per worktree instead of reusing a neighboring worktree interpreter. Evidence: `research/amn2/phase-5-runtime-toolchain-standardization-2026-06-11.md`. Focused local suite: `4 passed`; runtime/hygiene regression: `19 passed`; full local AMN2 suite: `658 passed, 1 warning`. Slice не выполнял live VPS commands, SSH commands, service restart, deploy, package apply, production peer/user mutation, public exposure, `/api/clients` CRUD, config delivery, Local Agent mutation, backup/import/reboot, destructive provider action or upstream code copy. This head was superseded by later local-only commits `23f18ef`, `ad6aa1b`, `17454e9`, `fed832c` and `de25576`; before any VPS package apply/rebuild, rebuild from the selected current AMN2 head and rerun source/package precheck because previous rebuild package was built from `1508e3c`.

External-only backfill rehearsal commit `23f18ef` также остается `local-gate-complete`: AMN2 now adds `device backfill-external` for JSON-based rehearsal of old externally issued test devices on a local DB copy. Dry-run does not create or mutate `--db-copy`; apply writes only to the operator-selected DB copy; imported devices remain `config_material_status=external_only`; config resend remains unavailable; secret-bearing input fields are rejected before any DB write. Evidence: `research/amn2/phase-5-external-only-backfill-rehearsal-2026-06-11.md`. Focused local suite: `6 passed`; related bot/web/config suite: `58 passed, 1 warning`; full local AMN2 suite: `662 passed, 1 warning`. Slice не выполнял live VPS commands, SSH commands, service restart, deploy, package apply, production peer/user mutation, public exposure, `/api/clients` CRUD, config delivery, Local Agent mutation, backup/import/reboot, destructive provider action or upstream code copy. This head was superseded by later local-only commits `ad6aa1b`, `17454e9`, `fed832c` and `de25576`; before any VPS package apply/rebuild, rebuild from the selected current AMN2 head and rerun source/package precheck because previous rebuild package was built from `1508e3c`.

Phase 5 operator-only handoff 2026-06-11: prepared `docs/NEXT_CHAT_AMN2_PHASE_5_OPERATOR_PILOT.ru.md` as the active next-chat entry point. It carried remaining Phase 4 conditional directions into Phase 5 with priorities: `P4-PRVTPRO-REFRESH-003` as normal/design-boundary-first at handoff time, write API/config delivery/public exposure as critical gated work, and `VPS-REBUILD-001` as separate destructive `defer`. `P4-PRVTPRO-REFRESH-003` was later closed in Phase 5 through the AMN3 design boundary and `P5-L001` local cached display; `P5-S003` keeps it visible as closed carried history, not active work. Existing heartbeat automations `amnezia-weekly-upstream-refresh`, `prvtpro-weekly-upstream-refresh` and `weekly-kyoresuas-upstream-refresh` were updated to Phase 5 prompts without creating duplicates. In the Phase 5 thread, `amnezia-weekly-upstream-refresh` was retargeted successfully; the app rejected attaching the other two active heartbeat automations to the same thread, so `prvtpro-weekly-upstream-refresh` and `weekly-kyoresuas-upstream-refresh` keep their existing thread bindings unless the operator chooses a separate consolidation policy.

After Phase 6 automation intake aggregation 2026-06-14: completed as AMN3 local-only/docs-only evidence `research/amn2/after-phase-6-automation-intake-aggregation-closeout-readiness-2026-06-14.md`. PRVTPRO heartbeat output was available and normalized into `research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-14.md`. KYORESUAS and Amnezia final automation reports were not found in the current AMN2 thread or local AMN3 evidence, so they are explicitly marked `missing-input`; direct public GitHub metadata refresh produced `research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-14.md` and `research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-14.md`. Added candidates `FI-M004` package asset path preflight (`package/preflight only`), `P6-M005` multi-instance/port/IPAM conflict model (`local-only/docs/tests`) and `P6-N005` OpenAPI/taxonomy route-order drift guard (`local-only/docs/tests`). AmneziaWG Android `2.0.1` remains watch-only. No live VPS command, SSH command, package rebuild/apply on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive action, Telegram action, secret publication or upstream/GPL code copy was performed. Closeout readiness decision: Phase 6 can proceed to final closeout; optional pre-closeout bundle is `FI-M004 + P6-N005`.

After Phase 6 `FI-M004 + P6-N005` 2026-06-14: completed as AMN2 local-only code/tests/docs evidence `research/amn2/after-phase-6-installer-preflight-taxonomy-guards-2026-06-14.md`. AMN2 branch `codex-vps-test-prep` advanced to `4cde273 Add installer preflight taxonomy guards`, adding fresh-installer package asset path preflight and public docs/API route-order drift guard. Verification returned RED `3 failed, 15 passed`, focused `18 passed`, expanded `26 passed, 1 StarletteDeprecationWarning`, full AMN2 suite `723 passed, 1 StarletteDeprecationWarning`, `git diff --check` and staged check passed. No live VPS command, SSH command, package rebuild/apply on VPS, service restart/deploy, public exposure, public OpenAPI publication, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive action, Telegram action, secret publication or upstream/GPL code copy was performed. Latest VPS-smoked/package head remains `0de7a77`; `4cde273` is local-only and not package-rebuilt/VPS-smoked.

After Phase 6 `P6-M005` 2026-06-14: completed as AMN2 local-only code/tests/docs evidence `research/amn2/after-phase-6-multi-instance-ipam-conflict-model-2026-06-14.md`. AMN2 branch `codex-vps-test-prep` advanced to `b121865 Add multi instance conflict model`, adding `capability_registry.multi_instance_conflict_model` and `docs/MULTI_INSTANCE_IPAM_CONFLICT_MODEL.ru.md`. Verification returned RED `3 failed, 4 passed, 1 StarletteDeprecationWarning`, focused `7 passed, 1 StarletteDeprecationWarning`, expanded `27 passed, 1 StarletteDeprecationWarning`, full AMN2 suite `724 passed, 1 StarletteDeprecationWarning`, `git diff --check` and staged check passed. No live VPS command, SSH command, package rebuild/apply on VPS, service restart/deploy, public exposure, public OpenAPI publication, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive action, Telegram action, secret publication or upstream/GPL code copy was performed. Latest VPS-smoked/package head remains `0de7a77`; `b121865` is local-only and not package-rebuilt/VPS-smoked.

Phase 6 final closeout 2026-06-14: completed as AMN3 docs-only/local-only evidence `research/amn2/phase-6-final-closeout-known-good-snapshot-2026-06-14.md`. Decision: Phase 6 default lane is closed, default local queue is empty and the project remains private/operator-only. AMN2 current head is `b121865 Add multi instance conflict model`; latest VPS-smoked/package head remains `0de7a77 Polish fresh installer preflight planning` on disposable VPS `89.185.80.166`. Any future live update from `0de7a77` to `b121865` requires a separate named live package/apply/smoke gate. Remaining public/config/write/backup/destructive/Local Agent/Telegram identity gates are deferred and not active. No live VPS command, SSH command, package rebuild/apply on VPS, service restart/deploy, public exposure, public OpenAPI publication, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive action, Telegram action, secret publication or upstream/GPL code copy was performed.

Phase 7 transition packet 2026-06-14: prepared as AMN3 docs-only/local-only evidence `research/amn2/phase-7-transition-packet-2026-06-14.md`. Phase name/status: `Release Candidate Readiness / Clean Installer RC`, `pre-release / release-candidate readiness`. Added `docs/NEXT_CHAT_AMN2_PHASE_7_RELEASE_CANDIDATE.ru.md` and `docs/PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md`. Carried deferred gates into Phase 7 as `P7-C001` through `P7-C007`, with default lane local-only/docs/tests/security/package-preflight. No VPS/SSH/PowerShell/provider/Telegram/payment access is needed by default. Weekly upstream-refresh automations were updated to Phase 7 context. No live VPS command, SSH command, package rebuild/apply on VPS, service restart/deploy, public exposure, public OpenAPI publication, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive action, Telegram action, secret publication or upstream/GPL code copy was performed.

## Post Dry-Run Read-Only Integration Status

Статус: `implemented-pushed-local-gate-complete`.

Plan artifact:

```text
docs/superpowers/plans/2026-06-04-amn2-post-dry-run-read-only-integration.md
```

Implementation:

```text
branch: codex/post-dry-run-read-only-integration
commit: 55a7ed6 Add post dry-run integration status
follow-up: 7764ae7 Cover integration status in API smoke
evidence: research/amn2/post-dry-run-read-only-integration-implementation.md
focused: 39 passed
full: 610 passed
```

Решение: после real VPS Phase 1 `dry-run-only-pass` не переходить к Phase 2 live apply/revoke по умолчанию. Реализован local-only read-only integration status surface: web-admin `/integration-status`, API `GET /api/integration/status`, общий local `integration_status` service, route policy/binding tests и AMN3 evidence. Slice не добавляет `/api/clients`, `config:read`, public/self-service config delivery, Local Agent mutations, SSH writes, Docker writes, peer apply/revoke, backup/import/reboot routes или detailed per-peer metrics.
