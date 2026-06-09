# Current Override 2026-06-09

Phase 4 main-chat handoff is prepared at `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`, with research note `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md`. Phase 4 accepts the Phase 3 service-mode loopback baseline as closed and starts as a local/read-only unified product gate for AMN2/API, target VPS, PRVTPRO/Web Panel and KYORESUAS/API coordination. It does not authorize new live commands, public exposure, config delivery, write CRUD, Local Agent mutations, backup/import/reboot or production peer/user mutation.

Phase 4 first local-only slice `P4-C009` web-panel user/config visibility was implemented locally on 2026-06-09. Evidence: `research/amn2/phase-4-web-panel-user-config-visibility-implementation-2026-06-09.md`. Root cause: `/users` lists local AMN2 DB users/devices only; live VPS peers created outside AMN2 are surfaced through server peer-sync/read-only inventory, not automatic user/config backfill. Local AMN2 tests passed focused verification with `26 passed, 1 warning`; no live VPS commands or write/config/token/sync/apply/revoke/backup/import/reboot actions were performed.

Phase 4 second local-only slice `P4-I002` service-mode/read-only status wording was implemented locally on 2026-06-09. Evidence: `research/amn2/phase-4-service-mode-status-wording-implementation-2026-06-09.md`. AMN2 branch `codex/phase-4-service-mode-status-wording`, commit `83f6d28`, updates `/integration-status` to report `service_mode_loopback_ready` and show a `Service-mode boundary` panel for loopback-only web/admin `127.0.0.1:3030`, SSH tunnel access, absent/closed public API `3040`, absent TCP `80/443`, deferred domain/HTTPS cutover and `VPS_APPLY_ENABLED=false`. Focused verification passed with `7 passed, 1 warning`; no live VPS commands or write/config/token/sync/apply/revoke/backup/import/reboot actions were performed. Next decision: run `P4-I001` second read-only UX pass only if more page-level evidence is needed; otherwise continue route/secret gate planning.

Latest target VPS current mode: Phase 3 service-mode web/bot is enabled and active, but only as loopback/tunnel operation. Web/admin listens on `127.0.0.1:3030`, operator access is SSH tunnel only, no domain is planned, Caddy/HTTPS public cutover is deferred indefinitely, direct/public `3030` is closed by loopback bind, public API `3040` is absent/closed, TCP `80/443` are absent, and target `.env` explicitly keeps `VPS_APPLY_ENABLED=false`. Current peer scope is `live_peer_count=2`: `Neobyatnaya-AMNZ-1` and `Neobyatnaya-AMNZ-2` remain approved test peers; `Neobyatnaya-AMNZ-3` and `Neobyatnaya-AMNZ-4` are revoked. Web-panel unauth smoke and authenticated read-only overview smoke passed; no POST/write/config delivery/token issue/revoke/sync was performed. This does not unlock API route expansion, API `config:read`, `/api/clients` write CRUD, public config delivery, Local Agent mutations, backup/import/reboot, public API `3040`, public web/admin `3030`, Caddy/HTTPS or production peer writes.

Service-mode web-panel read-only UX review passed on 2026-06-09 as `passed-minimal-safe-summary`. Evidence: `research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md`. Operator confirmed service baseline, reviewed authenticated overview pages through SSH tunnel, and reported no write/config delivery/API token issue-revoke/sync-health/backup-import-reboot actions and no secrets published. Detailed page-by-page UX findings were not returned.

Target VPS Phase 3A.1 phone live test peer gate passed on 2026-06-09. One operator-approved test peer for phone/desktop client testing is intentionally left enabled. The first live apply attempt failed before remote mutation because the local test VPN IP input was invalid; verification showed no partial peer in persistent config or live interface and peer count remained `0`. After selecting a free VPN IP without publishing it, repeat dry-run apply/revoke passed, live apply passed, client config was regenerated from live AWG2 parameters with absent `I1`-`I5` fields removed, and client handshake/RX/TX passed. Final safe snapshot: `live_peer_count=1`, TCP `3030/3040` absent, `VPS_APPLY_ENABLED=false`, service-mode not enabled. Evidence: `research/amn2/target-server-phone-live-test-peer-evidence-2026-06-09.md`.

Target VPS Phase 3A.2 test peers batch gate passed on 2026-06-09. Three additional operator-approved test-zone peers were created and left enabled; secret-bearing configs/QRs were generated and downloaded through a private operator channel and were not published to chat or GitHub. Final safe snapshot: `live_peer_count=4`, TCP `3030/3040` absent, `VPS_APPLY_ENABLED=false`, service-mode not enabled. Evidence: `research/amn2/target-server-test-peers-batch-evidence-2026-06-09.md`.

Target VPS Phase 3B.0 service-mode read-only precheck passed on 2026-06-09. Source overlay remains `f7f6131`, Docker runtime is running, `live_peer_count=4`, TCP `3030/3040` are absent, `VPS_APPLY_ENABLED=false`, web/bot service templates are present, web template binds `127.0.0.1:3030`, required bot/web secrets are present as markers only, and no `amneziya-web`/`amneziya-bot` systemd unit is installed, enabled or active. A named peer activity sample for `Neobyatnaya-AMNZ-1..4` returned `not-yet` at that moment. Evidence: `research/amn2/target-server-service-mode-precheck-evidence-2026-06-09.md`.

Target VPS Phase 3A critical manual-mode cleanup passed on 2026-06-09. Before cleanup, the target remained at `live_peer_count=4`, TCP `3030/3040` absent, `VPS_APPLY_ENABLED=false`, and the four named test peers sampled as `not-yet`. Secret-bearing delivery artifacts from the phone/test peer gate directories and root delivery archive location were removed: client `.conf`, QR/PNG and delivery archive files now count `0`. Monitoring key files were intentionally retained so the four test peers can still be checked by friendly number. Post-cleanup control confirmed `live_peer_count=4`, TCP `3030/3040` absent and `VPS_APPLY_ENABLED=false`. Evidence: `research/amn2/target-server-manual-mode-critical-cleanup-evidence-2026-06-09.md`.

Target VPS Phase 3A protocol identity check passed on 2026-06-09 after the operator reported that imported client configs did not visibly advertise "Amnezia 2.0". The downloaded config metadata for `Neobyatnaya-AMNZ` and `Neobyatnaya-AMNZ-2..4` shows all 11 core AmneziaWG fields present and `I1`-`I5` absent; live server config metadata matches the same shape. Numbered peer monitoring showed `Neobyatnaya-AMNZ-2=connected-with-traffic`, while `1`, `3` and `4` were `not-yet` at that sample. This supports UI/label ambiguity rather than a wrong plain-WireGuard or Amnezia 1/1.5 export. No regenerate/re-delivery gate is required on this evidence alone. Evidence: `research/amn2/target-server-protocol-identity-and-numbered-peer-evidence-2026-06-09.md`.

Target VPS Phase 3A manual-runtime field test reached `partial-pass` on 2026-06-09. A read-only numbered live snapshot during real usage showed `live_peer_count=4`, TCP `3030/3040` absent, `VPS_APPLY_ENABLED=false`, and `connected_with_traffic_count=3`: `Neobyatnaya-AMNZ-1`, `-2` and `-3` were `connected-with-traffic`, while `-4` remained `not-yet`. This proves live manual-runtime connectivity for three of four approved test peers. Evidence: `research/amn2/target-server-manual-mode-field-test-evidence-2026-06-09.md`.

Target VPS Phase 3A revoke-by-number runbook is prepared but not executed. It documents a safe dry-run and explicit-confirmation live revoke flow for exactly one `Neobyatnaya-AMNZ-N` test peer, with numbered key resolution, pre/post peer count checks, `3030/3040` checks, and `VPS_APPLY_ENABLED=false` reset. It does not authorize any revoke by default. Runbook: `docs/AMN2_MANUAL_MODE_REVOKE_BY_NUMBER_RUNBOOK.ru.md`.

Target VPS Phase 3A revoke-by-number gate for `Neobyatnaya-AMNZ-3` passed on 2026-06-09. Dry-run confirmed the target was present in persistent config and live interface, had `connected-with-traffic`, and advertised the expected remote-state-write/container-restart markers. Live revoke removed only `Neobyatnaya-AMNZ-3` from persistent and live state: `live_peer_count` changed from `4` to `3`, `target_in_persistent_after=no`, `target_in_live_after=no`, TCP `3030/3040` remained absent, and `VPS_APPLY_ENABLED` was reset to `false`. Evidence: `research/amn2/target-server-revoke-by-number-3-evidence-2026-06-09.md`.

Post-revoke numbered snapshot kept the same safe state: `live_peer_count=3`, TCP `3030/3040` absent, `VPS_APPLY_ENABLED=false`, `Neobyatnaya-AMNZ-3=not-found-on-server`, and remaining peers `1`, `2`, `4` were initially `not-yet` pending fresh reconnect after Docker restart. A later reconnect snapshot after user activity showed `Neobyatnaya-AMNZ-1=traffic-seen`, `Neobyatnaya-AMNZ-2=traffic-seen`, `Neobyatnaya-AMNZ-3=not-found-on-server`, and `Neobyatnaya-AMNZ-4=not-yet`. This proves manual reconnect/traffic for two remaining peers after the #3 revoke; automatic reconnect remains unproven unless a separate disruption test is approved.

Target VPS Phase 3 revoke-by-number gate for unused `Neobyatnaya-AMNZ-4` passed on 2026-06-09. Dry-run confirmed #4 was present in persistent and live state with `target_status_before=not-yet`, and advertised the expected remote-state-write/container-restart markers. Live revoke removed #4 from both persistent config and live interface: `live_peer_count` changed from `3` to `2`, `target_in_persistent_after=no`, `target_in_live_after=no`, web/bot remained active, loopback `/login` returned `200`, TCP `3030` remained loopback-only, TCP `80`, `443` and `3040` remained absent, and `VPS_APPLY_ENABLED` was reset to false with explicit `.env` false. Evidence: `research/amn2/target-server-revoke-by-number-4-evidence-2026-06-09.md`.

Post-revoke #4 numbered snapshot confirmed `live_peer_count=2`, web/bot active, loopback `/login=200`, TCP `3030` loopback-only, TCP `80/443/3040` absent and explicit `.env` `VPS_APPLY_ENABLED=false`. `Neobyatnaya-AMNZ-3` and `Neobyatnaya-AMNZ-4` were `not-found-on-server`; `Neobyatnaya-AMNZ-1` and `-2` were `not-yet` in this immediate sample pending client reconnect after the Docker/AWG restart, with earlier Phase 3 evidence already showing traffic for both.

Target VPS Phase 3B0 service-mode preflight completed read-only on 2026-06-09 as `needs-fix-before-B1`. Good: source overlay `f7f6131`, Docker runtime running, `live_peer_count=3`, TCP `3030/3040` absent, `VPS_APPLY_ENABLED=false`, web/bot templates present, web template binds `127.0.0.1:3030`, no systemd units installed/enabled/active, imports pass. Blockers before `systemctl enable --now`: the `amneziya` service user/group is absent while templates use `User=amneziya`; effective settings show `WEB_ADMIN_ENABLED=False`; `ADMIN_TELEGRAM_IDS` is absent; reverse proxy choice is undecided for any later HTTPS cutover. Evidence: `research/amn2/target-server-service-mode-b0-preflight-evidence-2026-06-09.md`.

Target VPS Phase 3B0.1 prep and B0 repeat completed on 2026-06-09. B0.1 created the `amneziya` service user, set `.env` group/mode for that service group, enabled web/admin in effective settings on loopback, preserved `VPS_APPLY_ENABLED=false`, set admin Telegram IDs privately on the VPS, and fixed `/opt/amn2` group access so the service user can read app/venv/env and write data/logs. No systemd unit was installed or started, and reverse proxy was unchanged. Repeated B0 is now `ready-for-B1-loopback-systemd`: `live_peer_count=3`, TCP `3030/3040` absent, templates good, no units installed/active, settings as `amneziya` pass, imports pass. Evidence: `research/amn2/target-server-service-mode-b0-1-prep-and-repeat-evidence-2026-06-09.md`.

Target VPS Phase 3B1 loopback-only systemd gate passed on 2026-06-09 after a short readiness investigation. Initial B1 installed/enabled `amneziya-web` and `amneziya-bot` and both units were active, but the immediate web probe returned `curl_rc_7` with `tcp_3030_after=absent`, so B1 was treated as `needs-investigation`. Follow-up bounded diagnostics showed both units enabled/active with `Result=success`, `NRestarts=0`, web listening on `127.0.0.1:3030`, `/login` returning `200`, TCP `3040` absent, reverse proxy unchanged, and `VPS_APPLY_ENABLED=false`. Evidence: `research/amn2/target-server-service-mode-b1-loopback-systemd-evidence-2026-06-09.md`.

Target VPS Phase 3B2.0 reverse proxy preflight completed read-only on 2026-06-09. Web/bot systemd remained enabled/active, loopback `/login` returned `200`, TCP `3030` was loopback-only, TCP `3040` absent, TCP `80/443` absent, nginx/Caddy/certbot were not installed, no Docker proxy candidate was running, UFW was inactive, no writes were performed and reverse proxy remained unchanged. Evidence: `research/amn2/target-server-service-mode-b2-0-reverse-proxy-preflight-evidence-2026-06-09.md`.

Target VPS Phase 3B2.1 reverse proxy readiness completed read-only on 2026-06-09 as `blocked-before-public-cutover`. Web/bot remained enabled/active, loopback `/login` returned `200`, TCP `3030` remained loopback-only, TCP `3040`, `80` and `443` remained absent, and Caddy/nginx/certbot package candidates were available. The selected public host syntax was valid, but DNS returned no A/AAAA records from the VPS and therefore could not be proven to point at the target route source. The read-only check also did not prove an explicit `.env` `VPS_APPLY_ENABLED=false` line, so a small baseline-fix gate is required before Caddy/HTTPS. Evidence: `research/amn2/target-server-service-mode-b2-1-reverse-proxy-readiness-evidence-2026-06-09.md`.

Target VPS no-domain service-mode access path selected on 2026-06-09. The operator confirmed that current access is IP-only and no domain is available, so public HTTPS reverse proxy cutover is deferred. The selected safe access path is SSH local port forwarding from the operator workstation to loopback web/admin `127.0.0.1:3030`, opened in an external browser rather than Codex preview. Evidence: `research/amn2/target-server-service-mode-no-domain-ssh-tunnel-decision-2026-06-09.md`; runbook: `docs/AMN2_SERVICE_MODE_SSH_TUNNEL_ACCESS_RUNBOOK.ru.md`.

Target VPS no-domain SSH tunnel access passed on 2026-06-09. The operator opened the web/admin panel through an SSH local port forward in an external browser. Control snapshot confirmed `amneziya-web=active`, `amneziya-bot=active`, loopback `/login=200`, remote `3030` loopback-only, remote `3040` absent, and explicit `.env` `VPS_APPLY_ENABLED=false`. Evidence: `research/amn2/target-server-service-mode-ssh-tunnel-access-evidence-2026-06-09.md`.

Target VPS web-panel tunnel smoke passed read-only on 2026-06-09. Through the SSH local port forward, `/login` returned HTTP `200` with a login form and password field, `/` redirected to `/login`, sampled protected GET routes redirected to `/login` with HTTP `303`, the login response contained no obvious secret/error markers, and local `127.0.0.1:3040` did not accept a connection. No credentials were submitted, no POST route was called, no config delivery was requested, and no write operation was performed. Evidence: `research/amn2/target-server-service-mode-web-panel-tunnel-smoke-evidence-2026-06-09.md`.

Target VPS second Telegram admin ID add passed on 2026-06-09. One additional Telegram admin ID was added privately on the VPS, leaving configured admin count at `2` without publishing raw IDs. `VPS_APPLY_ENABLED=false` remained explicit in `.env`. After restarting `amneziya-bot` and `amneziya-web`, loopback `/login` had a short readiness window and then returned `200`; final state was bot/web active, TCP `3030` loopback-only and TCP `3040` absent. Evidence: `research/amn2/target-server-service-mode-admin-telegram-id-add-evidence-2026-06-09.md`.

Target VPS second admin bot read-only check was skipped by operator decision on 2026-06-09 to save time. The second admin ID remains configured and counted, but this record does not independently prove that the second admin opened `/start`, saw admin mode, or opened read-only bot admin sections. Evidence: `research/amn2/target-server-service-mode-second-admin-bot-check-decision-2026-06-09.md`.

Target VPS authenticated web-panel tunnel smoke passed read-only on 2026-06-09. The operator logged into the web/admin panel through the SSH local port forward in an external browser and sampled overview GET pages only. `/`, `/users`, `/servers`, `/orders`, `/logs`, `/settings`, `/config-templates`, `/api-readiness`, `/integration-status`, `/api-tokens` and `/devices/disabled` all returned HTTP `200` without redirect. No POST route was called, no settings were saved, no token was issued/revoked, no sync/health operation was run, and no config delivery was requested. Evidence: `research/amn2/target-server-service-mode-authenticated-web-panel-smoke-evidence-2026-06-09.md`.

Target VPS Phase 3 final safety snapshot passed on 2026-06-09 with source-overlay git metadata unavailable in that specific check. Runtime remained Docker with `live_peer_count=3`; `Neobyatnaya-AMNZ-1` and `-2` were `traffic-seen`, `-3` was `not-found-on-server`, and `-4` was `not-yet`. Web/bot systemd units were enabled/active, loopback `/login` returned `200`, TCP `3030` was loopback-only, TCP `80`, `443` and `3040` were absent, explicit `.env` `VPS_APPLY_ENABLED=false` was present, production write surfaces/config delivery remained closed, and reverse proxy/public HTTPS remained disabled. Evidence: `research/amn2/target-server-phase3-final-safety-snapshot-evidence-2026-06-09.md`.

This still does not execute HTTPS reverse proxy/public cutover, public API `3040`, direct public web/admin `3030`, production peer/user mutation beyond the two remaining approved test peers, API `config:read`, `/api/clients` write CRUD, public/self-service config delivery, Local Agent write/config mutations, backup/import/reboot routes, or secret-bearing evidence publication. B2 reverse proxy/public HTTPS remains a separate explicit gate.

# Historical Override 2026-06-07

`amn2/codex-vps-test-prep` VPS-smoked source overlay is now `f7f6131 Update integration status for c92 manual prelaunch`. The app-code read-only slice `62ff184 Update controlled prod status visibility` first passed real VPS git-checkout smoke on `/opt/amn2-git`, then AMN3 package `42ffa65` was applied to `/opt/amn2` through the safe source-overlay update flow and passed read-only loopback API smoke on 2026-06-07. The safety follow-up package `c92bd1a` passed source-overlay update/read-only loopback smoke on `/opt/amn2`, and the status-alignment package `f7f6131` has now also passed read-only loopback smoke.

The current VPS production source overlay is now `f7f6131 Update integration status for c92 manual prelaunch`. Previous source overlay `c92bd1a Bind web admin systemd to loopback` remains the web-admin loopback/manual-runtime baseline from 2026-06-07. `42ffa65 Record git checkout smoke status` remains historical status-visibility smoke baseline from 2026-06-07. `c8a6363 Add Local Agent runtime summary mapper` remains historical smoke-passed baseline from 2026-06-06. Current evidence: `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`; prior c92 source-overlay evidence: `research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md`; prior 42 source-overlay evidence: `research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md`; prior git-checkout evidence: `research/amn2/controlled-prod-status-visibility-git-checkout-smoke-2026-06-07.md`.

Latest AMN2 repository head and current proven `/opt/amn2` source overlay are both `f7f6131`. This remains read-only status visibility only; it does not unlock write/API/config/backup/agent/service-mode gates. Evidence: `research/amn2/manual-prelaunch-integration-status-2026-06-07.md` and `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`.

AMN3 update+smoke kit for `f7f6131` is now `read-only-vps-smoke-pass`. It aligned `/api/integration/status` and the web integration status page with the accepted manual-runtime state and kept `VPS_APPLY_ENABLED=false`.

Repeat confirmation: the same `42ffa65` source overlay passed another read-only loopback API smoke with `run_id=20260607T165807Z`, `checked_routes=6`, auth `401/403/401`, listener passed and audit passed. Evidence: `research/amn2/controlled-prod-status-visibility-vps-repeat-smoke-2026-06-07.md`.

Post-smoke safety follow-up is now complete for the read-only gate. Purpose: keep web/admin backend on `127.0.0.1:3030` for approved HTTPS reverse proxy mode before controlled production launch. This does not open public API `3040`, direct public web/admin `3030`, API `config:read`, `/api/clients` write CRUD, public/self-service config delivery, Local Agent mutations, backup/import/reboot, or new live peer operations.

Validation VPS manual runtime gate also passed after the `c92bd1a` smoke: backup create/verify passed, safe preflight passed, API smoke-cycle summary passed with six read-only routes, manual web and bot processes are present, `/login` returned `200`, web/admin is loopback-only on `127.0.0.1:3030`, direct public web `3030` is not exposed, public API `3040` is not exposed, `systemd` is not used, and `VPS_APPLY_ENABLED=false`.

```text
dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
package sha256: EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12
source zip: dist/amn2-codex-vps-test-prep-c92bd1a-source.zip
source sha256: 272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2
status: read-only-vps-smoke-pass
source_update_run_id: 20260607T182118Z
api_smoke_run_id: 20260607T182131Z
checked_routes: 6
routes: servers, integration_status, local_agent_runtime_summary, server_summary, metrics_summary, users_summary
route_status_codes: all 200
forbidden_markers: none
listener: 127.0.0.1:3040 loopback-only
auth: missing bearer 401, wrong scope 403, revoked token 401
audit: safe
web systemd template: ExecStart uses web serve --host 127.0.0.1 --port 3030
operator doc: dist/amn2-vps-update-and-smoke-kit-c92bd1a/AMN2_VPS_UPDATE_AND_SMOKE_c92bd1a.ru.md
package evidence: research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md
VPS smoke evidence: research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md
manual prelaunch evidence: research/amn2/c92bd1a-manual-prelaunch-evidence-2026-06-07.md
latest AMN2 repository head: f7f6131 Update integration status for c92 manual prelaunch
latest AMN2 head status: read-only status visibility, VPS source-overlay-smoked
latest AMN2 head evidence: research/amn2/manual-prelaunch-integration-status-2026-06-07.md
status-alignment package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
status-alignment package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
status-alignment source zip: dist/amn2-codex-vps-test-prep-f7f6131-source.zip
status-alignment source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
status-alignment package status: read-only-vps-smoke-pass
status-alignment VPS smoke: passed
status-alignment source update run_id: 20260607T203721Z
status-alignment api smoke run_id: 20260607T203730Z
status-alignment latest repeat api smoke run_id: 20260607T204300Z
status-alignment smoke evidence: research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md
status-alignment operator doc: dist/amn2-vps-update-and-smoke-kit-f7f6131/AMN2_VPS_UPDATE_AND_SMOKE_f7f6131.ru.md
status-alignment evidence: research/amn2/f7f6131-status-alignment-vps-package-2026-06-07.md
manual runtime status: passed
manual runtime mode: manual
systemd web/bot: not-used
web process: present
bot process: present
web login: 200
web direct public 3030: no
api public 3040: no
backup verified: backups/amneziya-backup-20260607T195851Z.tar.enc
api smoke cycle: passed, checked_routes=6, forbidden_markers_count=0
VPS_APPLY_ENABLED: false
```

AMN3 source-overlay gate result:

```text
dist/amn2-vps-update-and-smoke-kit-42ffa65.zip
package sha256: 5B43B467E014E87FEC1E49E8D9A8B7A2FBF841541BE88FDC6768097806240E39
source zip: dist/amn2-codex-vps-test-prep-42ffa65-source.zip
source sha256: 8A5B83D9AB95BE4230AAC221CE0321A37EF37E4E4B6EAB5EDECAE3C98A944829
status: read-only-vps-smoke-pass
source_update_run_id: 20260607T165559Z
api_smoke_run_id: 20260607T165625Z
latest_repeat_api_smoke_run_id: 20260607T165807Z
checked_routes: 6
listener: 127.0.0.1:3040 loopback-only
auth: missing bearer 401, wrong scope 403, revoked token 401
audit: safe
operator doc: dist/amn2-vps-update-and-smoke-kit-42ffa65/AMN2_VPS_UPDATE_AND_SMOKE_42ffa65.ru.md
package evidence: research/amn2/controlled-prod-status-visibility-vps-package-2026-06-07.md
VPS smoke evidence: research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md
```

New target VPS bootstrap 2026-06-08 first passed as `partial-pass`: base OS packages, Docker runtime with no containers, `/opt/amn2` venv, `f7f6131` source overlay, Python dependencies, DB schema init, partial loopback API `/api/servers` probe with token revoke, and encrypted backup create/verify passed. Evidence: `research/amn2/target-server-bootstrap-evidence-2026-06-08.md`.

Target VPS AWG2 runtime gate 2026-06-09 is now `read-only-smoke-pass`: `amnezia-awg2` Docker runtime was built and started, real target `servers.yml` was created on the VPS through a secret-safe channel, AMN2 loader accepted it, and official read-only API loopback smoke passed with `run_id=20260609T043158Z`, `checked_routes=6`, auth `401/403/401`, listener passed and audit passed. Evidence: `research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md`.

Target VPS live peer gate 2026-06-09 is now `verified-live`: exactly one disposable test peer passed dry-run apply/revoke, live apply/sync/revoke/sync, ended with peer count `0`, and post-gate read-only API loopback smoke passed with `run_id=20260609T045546Z`, `checked_routes=6`. Evidence: `research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md`.

Target VPS manual web/bot gate 2026-06-09 is now `passed`: Telegram bot token is present on the VPS and `bot check-network` passed for `@NeobyatnayaAMNZ_bot`; web admin password hash and session secret are present; a temporary manual web/admin process returned `/login` HTTP `200` on `127.0.0.1:3030`, then was stopped. Final snapshot: AWG2 container running, peer count `0`, TCP `3030` absent, TCP `3040` absent. Evidence: `research/amn2/target-server-manual-web-bot-evidence-2026-06-09.md`.

Next gate: keep the new target VPS as verified for the remote peer apply/revoke primitive and manual web/bot readiness, then choose the next layer deliberately: stay in manual runtime mode for product/API work, or run a separate service-mode gate if `systemd`/HTTPS reverse proxy deployment is desired. This still does not unlock public API `3040`, direct public web/admin `3030`, API `config:read`, `/api/clients` write CRUD, public/self-service config delivery, Local Agent mutations, backup/import/reboot, or production peer operations.

# Historical Override 2026-06-06

Historical 2026-06-06 source-overlay head was `c8a6363 Add Local Agent runtime summary mapper`. AMN3 update+smoke package for that source overlay is `c8a6363` and passed real VPS read-only smoke on 2026-06-06, `run_id=20260606T202040Z`. `32d01fd` is now the historical prior VPS-smoked runtime/source, `run_id=20260606T185114Z`; `1a193b9` is the previous historical runtime/source before that.

Read-only integration status update 2026-06-06: `32d01fd` updates `/api/integration/status` to report `read_only_vps_smoked`, Phase 2 `verified_live`, and controlled-prod readiness pending without enabling write routes or write operations. AMN3 evidence is `research/amn2/integration-status-controlled-prod-update-2026-06-06.md`. The previous local-only operation-contract fast-forward remains recorded at `research/amn2/remote-partial-failure-contract-2026-06-06.md`.

Local Agent runtime summary 2026-06-06: local-only AMN2 feature branch `codex/local-agent-runtime-summary` was created from `32d01fd`, verified locally, fast-forward merged into `codex-vps-test-prep`, pushed at `c8a6363 Add Local Agent runtime summary mapper`, packaged, and read-only VPS-smoked. It adds only a pure controller-safe mapper and focused tests; no API route, web route, CLI command or live write operation. Evidence is `research/amn2/local-agent-runtime-summary-implementation-2026-06-06.md` and `research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md`.

```text
AMN3 package for historical 2026-06-06 source overlay: dist/amn2-vps-update-and-smoke-kit-c8a6363.zip
sha256: 027ECC1BAD7321FCCD61A4CCCA3AC9F06AAA9AC6A3D7115B4813253D19C2CFBF
source zip: dist/amn2-codex-vps-test-prep-c8a6363-source.zip
source sha256: E1E198979D988B3A5AA038CF732B8DCDBE854C48A6D381FADBA05BFDEE0251C6
package evidence: research/amn2/local-agent-runtime-summary-vps-package-2026-06-06.md
package status: read-only-vps-smoke-pass
local verification: focused 7 passed; adjacent smoke/security 26 passed; package SHA/source SHA/no-BOM/no-forbidden-source-entry/test-extract checks passed
package evidence: research/amn2/local-agent-runtime-summary-vps-package-2026-06-06.md
VPS result for c8a6363: read-only-vps-smoke-pass, run_id 20260606T202040Z
VPS smoke evidence: research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md
previous VPS-smoked runtime/source: 32d01fd, run_id 20260606T185114Z, evidence research/amn2/integration-status-controlled-prod-update-2026-06-06.md
previous VPS-smoked runtime/source: 1a193b9, run_id 20260606T154636Z, evidence research/amn2/remote-partial-failure-contract-vps-smoke-evidence-2026-06-06.md
controlled prod readiness: controlled-prod-ready
controlled prod access path: approved HTTPS reverse proxy; public API 3040 not exposed
controlled prod recovery path: known
controlled prod runbook: docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
controlled prod evidence: research/amn2/controlled-prod-readiness-2026-06-06.md
controlled prod reverse proxy confirmation: research/amn2/controlled-prod-reverse-proxy-confirmation-2026-06-07.md
controlled prod final decision: research/amn2/controlled-prod-ready-2026-06-07.md
controlled prod next chat: docs/NEXT_CHAT_AMN2_CONTROLLED_PROD_DECISION.ru.md
previous VPS-smoked source: 568c611, run_id 20260605T162742Z, evidence research/amn2/phase-2-post-psk-stdin-vps-smoke-evidence-2026-06-05.md
docs-only cleanup: 6b5b5b7 Document stdin PSK peer apply
local-only contract merge: 1a193b9 Add remote partial failure contract
read-only integration status update: 32d01fd Update integration status for controlled prod
stable Local Agent runtime summary merge: c8a6363 Add Local Agent runtime summary mapper
```

Phase 2 live single disposable test peer apply/revoke is verified-live on stable `7764ae7`; `568c611` adds safer `--preshared-key-stdin` handling and passed read-only VPS update/smoke.

```text
AMN3 evidence: research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md
result: verified-live
scope: exactly one disposable test peer apply/sync/revoke/sync
```

This does not unlock broad write API, public/self-service config delivery, API `config:read`, `/api/clients` CRUD, backup/import/reboot routes, Local Agent mutations or public web/API exposure. Older `c92bd1a`, `42ffa65`, `c8a6363`, `32d01fd`, `294803e`, `7764ae7`, `568c611` and `1a193b9` package blocks below are historical evidence; `f7f6131` is the current VPS-smoked runtime/source baseline.
# Текущее состояние проекта

Дата: 2026-06-02.

Этот snapshot фиксирует текущее состояние после verified live VPS cycle, серии local-only hardening slices в `amn2`, сборки VPS install package и перехода API-направления в активную ветку `codex/read-only-api-route-shell`.

## Что учтено при обновлении

Проанализированы локальные Codex-сессии проекта с `VPS-OPS-LAB` и `Amneziya`, включая:

- ранний Amneziya planning/provisioning чат;
- `Подготовка запуска на VPS`;
- `VPS-тест Amneziya`;
- `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`;
- `VPN Ops Lab - KYORESUAS-API`;
- task/review-чаты Local Amnezia Agent first slice;
- task/review-чаты Local Agent production wiring;
- live VPS completion / verified tag / migration-to-lab чаты;
- Route/Auth/Operation Policy Matrix task/review;
- Redaction Coverage task/review;
- Config Delivery Integrity evidence;
- Public Token Safety task/review;
- Remote Operation contract / partial-failure / dry-run-audit slices;
- Local Agent hardening task/review;
- Web Panel Safe Improvements task/review;
- Scoped API Token Storage task/review;
- Route/Auth Binding Tests, API Token Lifecycle Gate and SSH Host Key Verifier task/review;
- VPS install package / installer fallback fix;
- KYORESUAS API priority plan и последующую ветку read-only API route shell;
- pre-VPS matrix comments from `codex/local-agent-production-wiring`;
- текущий `MAIN - VPN Ops Lab` coordination chat.

Нерелевантные сессии из других рабочих папок, например `ISP-NEW`, не включались в состояние этого проекта.

## AMN3 / VPS Ops Lab

Локальный checkout:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

GitHub remote:

```text
https://github.com/barakov-dot/amn3.git
```

Текущая ветка:

```text
master
```

AMN3 package state reviewed in this status refresh:

```text
master; verify exact current head with git log -1 after package publish
```

`master` должен быть синхронизирован с `origin/master` после каждого package publish.

Последние AMN3 pushes, учтенные в этом snapshot:

```text
25e02e9 Add VPS install package
87da41d Fix VPS installer user creation fallback
7fc3aee Set KYORESUAS API integration priority
8b4cc81 Refresh project coordination state
2b845cb Make API smoke skip server preflight by default
```

Актуальный install/update package для стабильного `amn2` baseline `294803e`:

```text
dist/amn2-vps-install-294803e.zip
sha256: 9B561FBF9C1ACDE403CFF6DA3A49544074457D3089FF8A8D0859B0CEBBBB1501
dist/amn2-vps-update-and-smoke-kit-294803e.zip
sha256: 702BAD7EBD69F80FC75FD31648383258B6C042BD51B801BC72BE2FD125813CE2
```

Package note: install/update packages include `amn2_api_loopback_smoke.sh` version `2026-06-04.2`; the package contains the merged API/web-panel slice (`API readiness` and `API tokens` web-admin pages), performs DB-only server config sync from `servers.yml` into SQLite before route smoke, and keeps `server preflight` as a separate SSH/server dry-run gate, not the API smoke path.

Дополнительный соседний AMN3 push, который не слит в `master`, но учтен в этом snapshot:

```text
origin/codex/local-agent-production-wiring -> d5f30c6 Clarify pre-VPS matrix baseline
artifact: docs/AMN3_PRE_VPS_LOCAL_STATUS_MATRIX.ru.md
status: branch-only pre-VPS matrix; использовать как комментарий/сверку, не как production gate
```

AMN3 является coordination/knowledge repo: research, design specs, implementation plans, transfer notes и gate для переноса идей в production.

Production-код остается в `amn2`.

## Production baseline: `amn2`

Локальный checkout:

```text
C:\Users\SooL\Documents\Amneziya
```

GitHub remote:

```text
https://github.com/barakov-dot/amn2.git
```

Стабильная production baseline ветка:

```text
codex-vps-test-prep
```

Актуальный head:

```text
294803e Add API readiness and token web pages
```

Стабильная baseline-ветка `amn2/codex-vps-test-prep` теперь содержит проверенный live VPS behavior contract, merged read-only API route shell и web-admin API readiness/token lifecycle pages.

Текущая активная рабочая ветка `Amneziya` для установки/API debug:

```text
codex/read-only-api-route-shell
head: 2010d60 Add API VPS smoke evidence template
remote: amn2/codex/read-only-api-route-shell
status: merged into `codex-vps-test-prep` at `5f12736`, local worktree clean
```

Эту ветку использовали в чате `Переводим AMN на API` для VPS install/update smoke и исправления ошибок. Актуальный real VPS loopback API-only smoke прошел 2026-06-03 с `run_id=20260603T112418Z`: DB-only server config sync выполнен, preflight `skipped`, API/auth/scope/revoke/listener/audit `passed`, `VPS_APPLY_ENABLED=false`, raw token/header/hash/config/keys/PSK не публиковались. Evidence: `research/amn2/api-vps-smoke-evidence-2026-06-03.md`. Предыдущий historical pass 2026-06-02 остается в `research/amn2/api-vps-smoke-evidence-2026-06-02.md`. После evidence ветка fast-forward merged в stable `codex-vps-test-prep` и запушена как production head `5f12736`. Главный coordination-chat не должен открывать параллельную API-реализацию; следующий API/web-panel slice `API readiness/status` + `API token lifecycle` UI выполнен в `amn2/codex/api-web-panel-finish`, затем fast-forward merged в stable `codex-vps-test-prep` и запушен как production head `294803e`.

После scoped API token storage в `codex-vps-test-prep` уже вошли Route/Auth Binding Tests, API Token Lifecycle Gate и SSH Host Key Verifier через PR #4, PR #5 и PR #6. Эти срезы остаются local-gate-complete: без новых live VPS calls, без включения remote writes и без расширения `/api/*` routes до отдельного gate.

Проверенная stable-точка live VPS cycle:

```text
vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Основной handoff production-репозитория:

```text
docs/NEXT_CHAT_HANDOFF.ru.md
```

Последние зафиксированные local-only проверки по свежим gate-срезам `amn2`:

```text
Route/Auth Binding Tests: focused 22 passed; full 549 passed
API Token Lifecycle Gate stacked: focused 56 passed; full 555 passed
SSH Host Key Verifier: focused 29 passed; full 550 passed
Remote Operation VPS-gate candidate: focused 71 passed; full 603 passed; VPS Phase 2 verified-live on current stable `7764ae7`
Post dry-run read-only integration status: focused 31 passed; full 610 passed
Secret Inventory Registry: focused 64 passed; full 591 passed
Read-only API route shell: full 588 passed
```

Ожидаемое предупреждение: `StarletteDeprecationWarning` от `httpx` / `starlette.testclient`.

## Verified live VPS cycle

На живом VPS подтверждено:

- approve заявки в Telegram создает рабочий peer;
- клиентский config подключается;
- web panel показывает working config сразу после approve;
- `Run peer sync` подтверждает live-состояние;
- внешние peer, созданные в приложении Amnezia, не удаляются и отображаются отдельно;
- missing local device можно добавить в AmneziaWG;
- `Disable VPN` и `Enable VPN` работают;
- выборочное удаление устройства работает;
- Docker runtime apply/revoke прошел живую проверку;
- AmneziaWG 2.0 template/defaults приведены к рабочему формату.

Это закрывает прежний пункт `live VPS retest` как основной риск. Новый retest нужен только после изменений в apply/revoke/config/sync логике.

## Что продолжаем теперь

API-readiness audit выполнен в AMN3:

```text
research/amn2/api-readiness-audit-after-live-baseline.md
```

Основной порядок слияния API, web panel и operations зафиксирован:

```text
docs/AMN2_MAIN_MERGE_ROADMAP.ru.md
```

Первый выбранный safe slice уже перенесен в `amn2`:

```text
Route/Auth/Operation Policy Matrix for current amn2 surfaces
```

Смысл slice: не добавлять новый production API сразу, а сначала сделать machine-checkable policy/contract для текущих web, bot, Local Agent и remote-operation surfaces: actors, auth, risk class, secret class, audit, idempotency, dry-run/apply, rollback/recovery и live-retest trigger.

Этот slice остался без live VPS calls, без новых config/API/write endpoints и без копирования upstream code.

После него локально выполнены и запушены в `amn2` следующие local-only / candidate slices:

- Redaction Coverage: `94ad807 Document secret-bearing delivery artifacts`;
- Config Delivery Integrity evidence: verified at `94ad807`;
- Public Token Safety: `dfe27ee Harden public email token safety`;
- Remote Operation state-changing contract / partial-failure / dry-run-audit: VPS-gate candidate `codex/remote-operation-vps-gate-prep` updated on top of `294803e`, head `7281254`, runbook `research/amn2/vps-gate-remote-operation-dry-run-audit.md`, package `dist/amn2-remote-operation-vps-gate-7281254-update-kit.zip`;
- Local Agent Hardening: `c5d7eb6 Harden Local Agent audit contract`;
- Web Panel Safe Improvements: `22dfc37 Clarify web panel operation gates`;
- Scoped API Token Storage: `1fdcde5 Add scoped API token storage contract`.
- Route/Auth Binding Tests: branch `amn2/codex/route-auth-binding-tests`, commit `f9d2c79 Bind route inventory to surface policies`.
- API Token Lifecycle Gate: branch `amn2/codex/api-token-lifecycle-gate-stacked`, commit `256d0c0 Add API token lifecycle gate`.
- SSH Host Key Identity Verifier: branch `amn2/codex/ssh-host-key-identity-verifier`, commit `dd20364 Add SSH host key verifier`, merged to `codex-vps-test-prep` via PR #6; later read-only API route shell fast-forward moved current production head to `5f12736`.
- Manager Config Export Contract: branch `amn2/codex/manager-config-export-contract`, commit `4d4e7a4 Add manager config export contract`; local-only no-route typed export adapter, без public/self-service endpoint, API `config:read` и Local Agent `/configs`.
- Public/Self-service Config Delivery Policy: branch `amn2/codex/public-config-delivery-policy-contract`, commit `2ef3af7 Add config share policy contract`; local-only no-route share-token/policy contract, без public download route, self-service download route, API `config:read` и Local Agent `/configs`.
- Backup/Import Policy Contract: branch `amn2/codex/backup-import-policy-contract`, head `afb2702 Tighten backup import preview type contract` with foundation commit `d2c160b`; local-only no-route backup mode registry, secret field policy and restore/import preview contract, без web/API backup routes, restore apply, import apply или live VPS calls.
- Secret Inventory Registry: branch `amn2/codex/secret-inventory-registry`, commit `9ce42f4 Add secret inventory registry`; local-only machine-checkable secret inventory, без `.env` чтения, DB access, routes, secret-bearing output или live VPS calls.
- Packaging discovery fix: branch `amn2/codex/read-only-api-route-shell`, commit `e99d5f3 Fix editable install package discovery`; исправляет editable install/package discovery перед VPS install package smoke.
- Read-only API route shell: branch `amn2/codex/read-only-api-route-shell`, commits `6534ac4`, `9cccdc2`, `b37103a`, `2010d60`, `5f12736`; добавлены loopback-safe read-only `/api/*` routes, token smoke CLI, local API smoke readiness, `amn2/docs/API_VPS_SMOKE_EVIDENCE.ru.md`, AMN3 operator script `scripts/vps/amn2_api_loopback_smoke.sh` и update+smoke kit `dist/amn2-vps-update-and-smoke-kit-5f12736.zip`; full local suite `588 passed`, expected `StarletteDeprecationWarning`; latest real VPS API-only smoke passed 2026-06-03, `run_id=20260603T112418Z`, evidence `research/amn2/api-vps-smoke-evidence-2026-06-03.md`; fast-forward merged into `codex-vps-test-prep` at production head `5f12736`.
- Post Dry-Run Read-Only Integration Status: branch `amn2/codex/post-dry-run-read-only-integration`, commit `55a7ed6 Add post dry-run integration status`; добавлены web-admin `/integration-status`, API `GET /api/integration/status` под `server:read`, общий local-only `integration_status` service, route policy/binding tests и `docs/API_TOKEN_POLICY.ru.md` update; focused `31 passed`, full `610 passed`; Phase 2 live single disposable peer apply/revoke passed later on current stable `7764ae7`.

Решение по соседним чатам:

- `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`: широкие research-задачи поставить на паузу; оставить как targeted-input для web-panel UX, config delivery integrity, route taxonomy, scoped API tokens и dangerous-action patterns.
- `VPN Ops Lab — KYORESUAS-API`: уже переведен из reference-only в собственную `amn2` implementation lane на ветке `codex/read-only-api-route-shell`; upstream code не копируем, `/clients` write CRUD, `config:read`, backup/import/reboot не открываем.
- `Переводим AMN на API`: использовать как рабочий чат для установки на сервер, loopback API smoke и исправления ошибок по ветке `codex/read-only-api-route-shell`.
- Соседние направления, которые требуют SSH/sync/config/runtime writes, все еще можно переводить к интеграционным решениям только после controlled real VPS evidence: сначала read-only/dry-run, затем single peer apply/revoke по отдельному подтверждению.

## Что не делать первым

Не расширять production API за пределы уже сделанного read-only aggregate route shell.

Не копировать upstream code.

Не трогать live VPS из lab-чата.

Не считать старые заметки `implemented-needs-live-retest` актуальными: они исторические, live baseline уже подтвержден.

## Связанные документы

Главный migration handoff:

```text
docs/NEXT_CHAT_AFTER_AMN2_VPS_LIVE.ru.md
```

API/upstream start:

```text
docs/NEXT_CHAT_KYORESUAS_API.ru.md
research/upstreams/kyoresuas-amnezia-api.md
```

`amn2` transfer context:

```text
research/amn2/README.md
research/amn2/transfer-backlog.md
research/amn2/remote-operations-inventory.md
research/amn2/config-delivery-inventory.md
research/amn2/route-auth-machine-checkable-tests-plan.md
research/amn2/backup-import-dangerous-api-design.md
research/amn2/manager-config-export-contract.md
research/amn2/manager-config-export-contract-implementation.md
research/amn2/public-self-service-config-delivery-policy.md
research/amn2/public-config-delivery-policy-contract-implementation.md
research/amn2/backup-import-policy-contract-implementation.md
research/amn2/secret-inventory-registry-implementation.md
research/amn2/kyoresuas-api-integration-priority-plan.md
amn2/docs/API_VPS_SMOKE_EVIDENCE.ru.md
amn2/docs/API_TOKEN_POLICY.ru.md
```

Pre-VPS support package:

```text
research/amn2/vps-gate-evidence-checklist.md
research/amn2/post-vps-gate-merge-decision.md
research/amn2/docker-manager-design-note.md
research/amn2/ssh-host-key-enrollment-design.md
research/amn2/neighbor-chat-vps-gate-handoff.md
research/amn2/read-only-metrics-privacy-classification.md
research/amn2/local-agent-runtime-metadata-alignment.md
research/amn2/api-token-rotation-revoke-policy.md
research/amn2/post-dry-run-read-only-integration-implementation.md
```

Existing unification design:

```text
docs/superpowers/specs/2026-05-31-amn3-amneziya-unification-design.md
```

## Local Agent baseline status

Local Agent first slice:

```text
status: merged into codex-vps-test-prep via PR #2
commits: 3119ee6, ac2baa8
```

Local Agent production wiring:

```text
status: merged into codex-vps-test-prep via PR #3
head: 8697b60 Document Local Agent production wiring
```

Локальная проверка показала, что эти commits уже содержались в production baseline после `91aeb3e`. Позднее Local Agent получил hardening commit `c5d7eb6`: repository-backed audit sink для allowed read routes, safe `/agent/version` metadata и тесты, что raw bearer token не попадает в audit. Runtime metadata boundary для будущего controller summary зафиксирован в `research/amn2/local-agent-runtime-metadata-alignment.md`; token lifecycle boundary - в `research/amn2/api-token-rotation-revoke-policy.md`, а local-only lifecycle gate выполнен в `amn2/codex/api-token-lifecycle-gate-stacked`, commit `256d0c0`. Следующий Local Agent slice не должен добавлять clients/configs/write routes.

## Рекомендуемый порядок

1. Не открывать второй параллельный API shell: read-only API route shell уже прошел local suite, real VPS loopback smoke и fast-forward merge в stable `codex-vps-test-prep`.
2. API/web-panel implementation slice выполнен, запушен, fast-forward merged в `codex-vps-test-prep` и повторно проверен на stable checkout: commit `294803e Add API readiness and token web pages`; focused `39 passed`, full `594 passed`.
3. VPS API/web-panel gate для production head `294803e` пройден 2026-06-04: API loopback smoke `run_id=20260604T102355Z`, `server_db_sync_status=passed`, API/auth/scope/revoke/listener/audit `passed`, web-admin `API readiness` и `API tokens` routes доступны. Evidence: `research/amn2/api-web-panel-vps-evidence-2026-06-04.md`.
4. Remote-operation VPS gate branch обновлена поверх stable head `294803e`: `codex/remote-operation-vps-gate-prep`, head `7281254`; focused `71 passed`, full `603 passed`; AMN3 package `dist/amn2-remote-operation-vps-gate-7281254-update-kit.zip`.
5. Controlled real VPS verification gate Phase 1 для `codex/remote-operation-vps-gate-prep` пройден 2026-06-04 как `dry-run-only-pass`: API sanity, read-only server check, traffic dry-run, apply-peer dry-run metadata и revoke-peer dry-run metadata passed. Evidence: `research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md`.
6. Controlled real VPS verification gate Phase 2 пройден 2026-06-05 на current stable `7764ae7` как `verified-live` для ровно одного disposable test peer apply/sync/revoke/sync. Evidence: `research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md`.
7. Любой API/web/agent route, который вызывает SSH, syncs peers, emits config или меняет runtime state, остается отдельным gated slice; Phase 2 не открывает broad write lifecycle.
7. Route/Auth binding tests, scoped API token lifecycle, secret inventory, public config policy and backup/import policy остаются обязательными baselines перед дальнейшим route expansion.
8. `/clients` write CRUD, API `config:read`, public config delivery, backup/import/reboot, public docs/metrics, domain exclusions и 2FA не открывать до отдельного решения.

## Route/Auth/Operation Policy Matrix Plan

Статус: `implemented-in-amn2-local-commit`.

Новый AMN3 artifact:

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

Создано в `amn2`:

- `app/security/surface_policy.py`
- `tests/security/test_surface_policy.py`
- `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`

Проверка:

```text
focused policy/agent/server tests: 46 passed
web/bot smoke tests: 85 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Новые API endpoints не добавлялись. Новые write/config delivery flows не включались.

Обновленный порядок:

1. `amn2` commit `d1d9690` запушен в remote branch `codex-vps-test-prep`.
2. Следующий local-only slice выбран и выполнен: redaction coverage.
3. Следующий local-only slice проверен: config delivery integrity.

## Redaction Coverage Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
94ad807 Document secret-bearing delivery artifacts
```

Production commits:

```text
75c235a Expand redaction primitive coverage
fc73929 Add config delivery redaction coverage
f62d5d6 Harden config email audit coverage
eb735e2 Harden remote output redaction coverage
94ad807 Document secret-bearing delivery artifacts
```

Проверка:

```text
focused redaction/security/delivery/remote/docs tests: 61 passed, 1 StarletteDeprecationWarning
full local suite: 528 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не меняет live apply/revoke/config/sync behavior, поэтому VPS gate не нужен.

## Config Delivery Integrity Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head used for verification:

```text
94ad807 Document secret-bearing delivery artifacts
```

Relevant production commits already present in branch:

```text
952cc49 Add config delivery artifact metadata
4b19cd3 Add config delivery utf8 artifact tests
fc73929 Add config delivery redaction coverage
```

Проверка:

```text
tests/bot/test_delivery.py tests/services/test_config_delivery.py tests/vpn/test_config_templates.py -v
result: 16 passed

full local suite at same head: 528 passed, 1 StarletteDeprecationWarning
```

Покрыто: `.conf` UTF-8 bytes, QR payload equality, `vpn://` round-trip, non-ASCII fixture, `client-config-secret` metadata and redaction behavior for text diagnostics.

Live VPS не трогался. Slice не меняет live templates/defaults или apply/sync behavior, поэтому VPS gate не нужен.

## Public Token Safety Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
dfe27ee Harden public email token safety
```

Покрыто:

- `create_email_token` теперь отклоняет `ttl_minutes <= 0`;
- raw token хранится/сравнивается через hash-only contract;
- public verify/recover tokens не взаимозаменяемы по `purpose`;
- expired verify/recover codes отклоняются;
- denial response не возвращает сырой token;
- wrong-purpose/expired tokens не consumed.

Проверка:

```text
tests/services/test_email_tokens.py tests/web/test_email_delivery.py -q --basetemp tmp\pytest-public-token
result: 14 passed, 1 StarletteDeprecationWarning

full local suite:
535 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не меняет peer apply/revoke/config/sync/runtime behavior, поэтому VPS gate не нужен.

## Local Agent Hardening Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
c5d7eb6 Harden Local Agent audit contract
```

Покрыто:

- `agent serve` подключает repository-backed audit sink;
- allowed read routes пишут `local_agent_read` в `admin_actions`;
- audit metadata содержит route, scope, risk class, token id/owner и result без raw bearer token;
- `/agent/version` отдает `runtime_contract_version`, `first_slice_routes` и `write_enabled=false`;
- first-slice boundary остается без `/agent/clients`, `/agent/configs`, backup/restore/reboot и write lifecycle.

Проверка:

```text
RED:
tests/agent/test_api.py::test_health_and_version_return_secret_free_metadata
tests/agent/test_cli.py::test_run_agent_server_records_allowed_read_audit_in_database
result: 2 failed as expected

focused agent/security tests:
64 passed, 1 StarletteDeprecationWarning

full local suite:
536 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice меняет локальный agent audit/version contract и docs, но не делает real agent deployment, controller-to-agent calls, peer apply/revoke/config/sync/runtime writes; VPS gate не нужен.

## Web Panel Safe Improvements Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
22dfc37 Clarify web panel operation gates
```

Покрыто:

- server health action помечен как read-only: stores health status only, no VPS changes;
- peer sync action помечен как read-only compare: does not add or remove peers;
- add missing local device confirmation явно говорит, что это live VPS write и должен идти через VPS gate;
- config templates page помечает real `.conf`, QR и `vpn://` payloads как secret-bearing delivery artifacts;
- user/device dangerous confirmations уточняют local DB status/data changes и VPS write только при `VPS_APPLY_ENABLED=true`.

Проверка:

```text
RED:
tests/web/test_servers.py::test_server_detail_shows_config_health_and_actions
tests/web/test_servers.py::test_server_sync_run_displays_peer_inventory_report
tests/web/test_config_templates.py::test_config_templates_page_lists_versions_placeholders_and_safe_preview
tests/web/test_users.py::test_user_detail_marks_dangerous_actions_with_confirmation
result: 4 failed as expected

GREEN focused slice:
same 4 tests
result: 4 passed, 1 StarletteDeprecationWarning

focused web/security suite:
tests/web/test_servers.py tests/web/test_users.py tests/web/test_config_templates.py tests/web/test_email_delivery.py tests/security/test_surface_policy.py
result: 75 passed, 1 StarletteDeprecationWarning

full local suite:
536 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice меняет UI wording/templates и web tests, но не меняет peer apply/revoke/config/sync/runtime behavior; VPS gate не нужен.

## Scoped API Token Storage Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
1fdcde5 Add scoped API token storage contract
```

Покрыто:

- `app.services.api_tokens` добавляет hash-only API token contract;
- raw token возвращается только через `ApiTokenIssue.raw_token` в момент выдачи;
- safe metadata содержит `raw_token_display=one-time` и не содержит raw token/hash;
- first-slice scopes ограничены `server:read` и `metrics:read`;
- `config:read`, write scopes и destructive scopes отклоняются;
- `api_tokens` table хранит `token_hash`, sorted `scopes_json`, owner metadata, `expires_at`, `revoked_at`, `last_used_at`;
- auth проверяет token exists, not revoked, not expired, required scope;
- docs фиксируют, что `/api/*` routes не добавлены.

Проверка:

```text
RED:
tests/services/test_api_tokens.py
tests/db/test_repositories.py::test_api_token_lifecycle_stores_hash_scopes_and_revoke_state
result: 1 import error as expected

GREEN focused slice:
tests/services/test_api_tokens.py
tests/db/test_repositories.py::test_api_token_lifecycle_stores_hash_scopes_and_revoke_state
result: 6 passed

focused security/db/services suite:
tests/services/test_api_tokens.py tests/db/test_repositories.py tests/agent/test_auth.py tests/security/test_surface_policy.py tests/test_file_hygiene.py
result: 54 passed

full local suite:
542 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice добавляет local storage/auth contract и docs, но не добавляет API routes, не делает peer apply/revoke/config/sync/runtime writes и не читает live VPS; VPS gate для самого slice не нужен.

## Manager Config Export Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/manager-config-export-contract
```

Production commit:

```text
4d4e7a4 Add manager config export contract
```

Покрыто:

- local-only `ConfigExportRequest` / `ConfigExportResult` / `ConfigExportArtifact` contract;
- adapter from current `DeviceConfigDelivery` / `ConfigDeliveryPackage`;
- typed artifacts for `.conf`, QR payload/PNG, `vpn://` import URI and delivery message;
- safe metadata boundary без raw `.conf`, QR payload, QR PNG/base64, `vpn://`, private key и PSK;
- safe categories for unsupported artifact, unsupported target client and exporter signature mismatch.

Проверка:

```text
focused config/security/delivery suite:
40 passed

full local suite:
560 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не добавляет public/self-service config endpoint, `/api/*` route, API `config:read`, Local Agent `/configs`, новые QR/import behavior или storage raw config в БД; VPS gate для самого slice не нужен.

## Public/Self-service Config Delivery Policy Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
2ef3af7 Add config share policy contract
```

Покрыто:

- local-only hash-only share-token lifecycle and policy service;
- `config_share_tokens` table and repository create/auth lookup/use/revoke contract;
- blocked future `SurfacePolicy` entries for self-service and public share config download;
- required expiry, purpose `config_share`, resource binding, one-time/max-download denial, revoke and generic public denial;
- safe audit metadata and redacted backup metadata with `restore-disabled`.

Проверка:

```text
focused config/token/security/db suite:
94 passed

full local suite:
577 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не добавляет public download route, self-service config download route, `/api/*`, API `config:read`, Local Agent `/configs`, generated config persistence, новые QR/import behavior или live VPS calls; VPS gate для самого slice не нужен.

## Backup/Import Policy Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/backup-import-policy-contract
```

Production head:

```text
afb2702 Tighten backup import preview type contract
```

Покрыто:

- local-only backup mode registry для `metadata-export`, `redacted-backup` и `encrypted-full-backup`;
- secret field policy для token hashes, peer private key, PSK, admin password hash, `.conf`, QR payload/PNG и `vpn://`;
- safe policy manifest без raw secret values;
- restore/import preview-only contract with `apply_allowed=false` and `side_effects=[]`;
- blocked future `SurfacePolicy` entries для backup/export, restore preview/apply и import preview/apply.

Проверка:

```text
RED:
tests/backup/test_backup_policy.py tests/security/test_surface_policy.py
result: 1 import error as expected

focused backup/security/agent suite:
61 passed

full local suite:
584 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не добавляет web/API backup routes, Local Agent `/backup` или `/restore`, restore apply, import apply, backup-before-write mutation или live VPS calls; VPS gate для самого slice не нужен.

## Secret Inventory Registry Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/secret-inventory-registry
```

Production commit:

```text
9ce42f4 Add secret inventory registry
```

Покрыто:

- `app.security.secret_inventory` как machine-checkable registry secret-bearing state;
- `SecretInventoryEntry` с secret class, storage surface, backup/restore defaults, route exposure и safe metadata policy;
- lookup/filter helpers;
- safe manifest без secret values;
- cross-check, что backup policy secret sources покрыты inventory.

Проверка:

```text
RED:
tests/security/test_secret_inventory.py
result: 1 import error as expected

focused security/backup/token suite:
64 passed

full local suite:
591 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не читает `.env`, не подключается к БД, не добавляет routes, secret-bearing output, backup export, restore/import apply или live VPS calls; VPS gate для самого slice не нужен.

## Remote Operation Dry-run/Audit Slice

Статус: `implemented-pushed-local-gate-complete`.

Production worktree:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-vps-gate-prep
```

Production branch:

```text
codex/remote-operation-vps-gate-prep
```

Production commits:

```text
c249bd0 Add state-changing operation metadata
8af6b5e Add remote partial failure model
b7a12ca Add remote operation dry-run metadata
aca6663 Add VPS gate handoff for remote ops
262d70f Merge current VPS test prep into remote operation gate
7281254 Merge stable API web panel baseline into remote operation gate
```

Покрыто:

- `RemoteOperationRunner.plan()` возвращает `consistency_status=dry-run` для state-changing операций без SSH;
- `OperationPlan.to_safe_metadata()` не публикует command strings и redacts audit/rollback/idempotency metadata;
- `apply-peer` и `revoke-peer` dry-run preview показывает operation ID, risk class, side effects и rollback note без PSK/private config;
- `docs/RUNTIME_REGISTRY.ru.md` и `docs/RUNTIME_REGISTRY.en.md` фиксируют local gate перед real VPS.

Проверка:

```text
focused remote-operation/runtime tests: 71 passed, 1 PytestCacheWarning
full local suite: 603 passed, 1 warning
```

Real VPS Phase 1 read-only/dry-run gate пройден 2026-06-04 как `dry-run-only-pass`: source overlay `7281254` verified, API loopback sanity passed, read-only server check passed, traffic dry-run passed, apply/revoke dry-run metadata passed. Live `--apply`/`--revoke --apply` не запускались. Evidence: `research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md`.

## Local Gate / Live VPS Gate

Новый порядок проверки разделен на два контура.

Локально можно делать:

- policy/inventory-only registry;
- redaction coverage;
- config delivery artifact tests;
- web/bot smoke через TestClient;
- Local Agent read-only/auth/token hardening на fake/local runtime;
- scoped API token storage/auth tests без `/api/*` routes;
- remote operation contracts на fake SSH;
- docs/status/backlog updates.

На real VPS проверяем только после локально зеленого slice, если он меняет:

- peer apply/revoke;
- disable/enable/delete;
- add missing local device;
- remove unknown remote peer;
- peer sync classification;
- config templates/defaults, которые попадут в рабочий client config;
- Docker AmneziaWG write/reload/restart behavior;
- реальный Local Agent deployment или controller-to-agent calls.

Следующий рекомендуемый шаг для текущего git head `c8a6363`: продолжить только read-only next slice после `controlled-prod-ready`. Phase 2 single disposable peer apply/revoke уже verified-live, а `c8a6363` уже прошел real VPS read-only smoke; write lifecycle, config delivery API, Local Agent mutation routes, backup/import/reboot и public API `3040` остаются заблокированы до отдельных gates.
