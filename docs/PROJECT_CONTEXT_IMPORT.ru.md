# Текущий override 2026-06-09

After Phase 6 `FI-M004 + P6-N005` is closed as AMN2 local-only code/tests/docs.
Evidence:
`research/amn2/after-phase-6-installer-preflight-taxonomy-guards-2026-06-14.md`.
AMN2 current head is `4cde273 Add installer preflight taxonomy guards`, pushed
to `amn2/codex-vps-test-prep`. The slice adds fresh-installer package asset
path preflight, a rendered `package-asset-path-preflight` phase and a public
docs/API route-order drift guard. Verification: RED `3 failed, 15 passed`,
focused `18 passed`, expanded `26 passed, 1 StarletteDeprecationWarning`, full
AMN2 suite `723 passed, 1 StarletteDeprecationWarning`, `git diff --check` and
staged check passed. No live VPS command, SSH command, package rebuild/apply on
VPS, service restart/deploy, public exposure, public OpenAPI publication,
config delivery, write API, Local Agent mutation, backup/import/reboot,
production peer/user mutation, destructive action, Telegram action, secret
publication or upstream/GPL code copy was performed. Latest VPS-smoked/package
head remains `0de7a77`; AMN2 `4cde273` is local-only and not
package-rebuilt/VPS-smoked. Next recommendation: Phase 6 final closeout +
clean-installer next-phase entry + current VPS known-good snapshot/runbook.

After Phase 6 automation intake aggregation + closeout readiness review is
closed as AMN3 local-only/docs-only work. Evidence:
`research/amn2/after-phase-6-automation-intake-aggregation-closeout-readiness-2026-06-14.md`.
PRVTPRO heartbeat output was available and normalized into
`research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-14.md`.
KYORESUAS and Amnezia final automation reports were not found in the current
AMN2 thread or local AMN3 evidence, so they are explicitly marked
`missing-input`; direct public GitHub metadata refresh produced
`research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-14.md` and
`research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-14.md`.
New non-live candidates: `FI-M004` package asset path preflight
(`package/preflight only`), `P6-M005` multi-instance/port/IPAM conflict model
(`local-only/docs/tests`) and `P6-N005` OpenAPI/taxonomy route-order drift guard
(`local-only/docs/tests`). AmneziaWG Android `2.0.1` is watch-only. Phase 6 can
proceed to final closeout; optional pre-closeout bundle is `FI-M004 + P6-N005`.
No live VPS command, SSH command, package rebuild/apply on VPS, service
restart/deploy, public exposure, config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive
action, Telegram action, secret publication or upstream/GPL code copy was
performed.

The underlying automation intake plan remains in
`docs/AMN2_AUTOMATION_INTAKE_AGGREGATION_PLAN.ru.md`. It records the three
weekly upstream-refresh automations as separate scout/aggregator heartbeats:
PRVTPRO at Sunday 10:00, KYORESUAS at 11:00 and Amnezia aggregator at 12:00.

Phase 6 `P6-C010` live update/smoke for AMN2 `0de7a77` is closed as
`live-update-smoke-pass` on disposable VPS `89.185.80.166`. Evidence:
`research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md`. Package
`dist/amn2-vps-update-and-smoke-kit-0de7a77.zip`, sha256
`7B6DA000DAA39DD15A4DB7C3691D0B0C24EAA20ACB1C428150C6961B01E6F85B`, was
uploaded, remote checksum-verified and extracted. Source overlay updated
`/opt/amn2` to `0de7a77f3eb09d23dc2785d402bc51c2b5eb7835`; source update
run_id `20260614T062734Z` passed. The existing manual web/bot runtime was
minimally restarted; web remained loopback-only on `127.0.0.1:3030`. Read-only
operator API smoke used temporary loopback `127.0.0.1:3040` and passed with
run_id `20260614T063327Z`, auth/listener/audit `passed`, and negative auth
checks `401/403/401`. Final listener snapshot showed only `127.0.0.1:3030`;
external probes to `3030`, `3040`, `80` and `443` returned `000`.
`VPS_APPLY_ENABLED=false` remained explicit. No public exposure change, config
delivery, write API production opening, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive
cleanup/reinstall, provider-side destructive action, Telegram identity/profile
mutation, live bot send by Codex, secret-bearing evidence publication or
upstream/GPL code copy was performed. Latest VPS-smoked/package head is now
`0de7a77`.

After Phase 6 next-chat handoff refresh + live gate checklist grooming for
`0de7a77` is closed as AMN3 docs-only/local-only work. Evidence:
`research/amn2/after-phase-6-next-chat-live-gate-checklist-0de7a77-2026-06-14.md`.
The handoff now records `0de7a77` as package-ready-not-vps-smoked, `c46f664` as
latest VPS-smoked head, the exact future gate phrase
`Открываю P6-C010 live apply/smoke gate для 0de7a77 на текущем disposable VPS 89.185.80.166.`,
the package/source checksums, stop criteria and forbidden surfaces. No live VPS,
SSH, package upload/apply, service restart/deploy, public exposure, config
delivery, write API, Local Agent mutation, backup/import/reboot, production
peer/user mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed. Next recommendation: open `P6-C010` only
with the exact named gate phrase if the operator chooses; otherwise pause with
`0de7a77` package-ready-not-vps-smoked.

After Phase 6 local package build/preflight for `0de7a77` is closed as AMN3
local package work. Evidence:
`research/amn2/after-phase-6-package-preflight-0de7a77-2026-06-14.md`. Built
`dist/amn2-vps-update-and-smoke-kit-0de7a77.zip`, sha256
`7B6DA000DAA39DD15A4DB7C3691D0B0C24EAA20ACB1C428150C6961B01E6F85B`, from
source zip `dist/amn2-codex-vps-test-prep-0de7a77-source.zip`, sha256
`B8D0E7E2A40051AB38EDF09947977DFE5F7197CEEEE87D1523734D3C1C505295`. Package
hygiene passed with `kit_entries=5`, `source_entries=342`,
`forbidden_source_entries=0`, shell scripts LF/no-BOM, operator doc markdown
hygiene, package checksum and test-extract. Verification: full AMN2 suite `721
passed, 1 StarletteDeprecationWarning`; AMN3 package/apply-script and markdown
hygiene tests `4 tests OK`; `git diff --check` passed. No live VPS command,
SSH command, package upload/apply on VPS, service restart/deploy, public
exposure, config delivery, write API, Local Agent mutation, backup/import/reboot,
production peer/user mutation, destructive action, Telegram action, secret
publication or upstream/GPL code copy was performed. AMN2 `0de7a77` is
package-ready-not-vps-smoked; latest VPS-smoked head remains `c46f664`. Next
recommendation: next-chat handoff refresh, or a separate named live apply/smoke
gate for `0de7a77` if the operator chooses.

After Phase 6 `FI-X001 + current-head package preflight planning` is closed as
AMN2 local-only code/tests/docs. Evidence:
`research/amn2/after-phase-6-fresh-installer-copy-package-preflight-2026-06-14.md`.
AMN2 current branch head is `0de7a77 Polish fresh installer preflight planning`,
pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains
`c46f664 Add public taxonomy cleanup checklist`. The slice switches fresh
installer prompt copy to Russian-first while preserving stable technical IDs and
adds `fresh-install-package-preflight.v1` planning for `ff77d4c` with package
build, live apply and live smoke disabled by default. Verification: RED `3
failed, 9 passed`, focused `12 passed`, full `721 passed, 1
StarletteDeprecationWarning`, `git diff --check` and staged checks passed. No
live VPS, SSH, package apply/rebuild, service restart/deploy, public exposure,
config delivery, write API, Local Agent mutation, backup/import/reboot,
production peer/user mutation, destructive action, Telegram action, secret
publication or upstream/GPL code copy was performed. Next recommendation: local
package build/preflight for `0de7a77` without live apply/smoke, or a separate
named live gate if the operator chooses.

After Phase 6 `P6-C001 + P6-C002` docs-only checklist refresh is closed as
AMN2 local-only code/tests/docs. Evidence:
`research/amn2/after-phase-6-public-config-gate-checklist-refresh-2026-06-13.md`.
AMN2 current branch head is `ff77d4c Add public config gate checklist`, pushed
to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains
`c46f664 Add public taxonomy cleanup checklist`. The slice adds
`docs/PUBLIC_CONFIG_GATE_CHECKLIST.ru.md` and a machine-checkable checklist
artifact that keeps `public_exposure_enabled=false` and
`config_delivery_enabled=false` unless separate named gates are opened.
Verification: focused `4 passed`, full `720 passed, 1
StarletteDeprecationWarning`, `git diff --check` passed. No live VPS, SSH,
package apply/rebuild, service restart/deploy, public exposure, config
delivery, write API, Local Agent mutation, backup/import/reboot, production
peer/user mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed. `P6-C001` and `P6-C002` remain critical
gated/deferred for actual public exposure and actual config delivery. Next
recommendation: `FI-X001 + current-head package preflight planning for ff77d4c`
as local-only docs/tests/package hygiene, without live apply.

After Phase 6 `FI-N001 + FI-N002 + FI-S001` fresh installer evidence readiness
is closed as AMN2 local-only code/tests/docs. Evidence:
`research/amn2/after-phase-6-fresh-installer-evidence-readiness-2026-06-13.md`.
AMN2 current branch head is `525a9cd Add fresh installer evidence readiness`,
pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains
`c46f664 Add public taxonomy cleanup checklist`. The slice adds
`fresh-install-evidence.v1`, smoke/evidence template, report-only
existing-server reconciliation input and `docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md`.
Verification: RED `3 failed, 8 passed`, focused `13 passed`, full `719 passed,
1 StarletteDeprecationWarning`, `git diff --check` and staged check passed. No
live VPS, SSH, live smoke execution, package apply/rebuild, service
restart/deploy, public exposure, config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive
action, Telegram action, secret publication or upstream/GPL code copy was
performed. Next operator-requested item: `P6-C001 + P6-C002` docs-only checklist
refresh without opening public/config gates.

After Phase 6 `FI-M001 + FI-M002 + FI-M003` fresh installer readiness planning
is closed as AMN2 local-only code/tests/docs. Evidence:
`research/amn2/after-phase-6-fresh-installer-readiness-planning-2026-06-13.md`.
AMN2 current branch head is `7416fb0 Add fresh installer readiness planning`,
pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains
`c46f664 Add public taxonomy cleanup checklist`. The slice adds
`fresh-install-readiness.v1`, target preflight matrix, runtime mode decision
and package hygiene checklist to the existing fresh installer plan. Verification:
RED `2 failed, 6 passed`, focused `10 passed`, full `716 passed, 1
StarletteDeprecationWarning`, `git diff --check` and staged check passed. No
live VPS, SSH, target diagnostic execution, package apply/rebuild, service
restart/deploy, public exposure, config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive
action, Telegram action, secret publication or upstream/GPL code copy was
performed. Next recommendation: `FI-N001 + FI-N002 + FI-S001` local-only.

After Phase 6 `FI-I001 + FI-I002 + FI-I003` fresh installer question model,
plan renderer and secret handoff binding are closed as AMN2 local-only
code/tests/docs. Evidence:
`research/amn2/after-phase-6-fresh-installer-plan-renderer-2026-06-13.md`.
AMN2 current branch head is `de635a0 Add fresh installer plan renderer`, pushed
to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains
`c46f664 Add public taxonomy cleanup checklist`. The slice adds
`build_fresh_install_manifest()`, `fresh-install-plan.v1`, rendered plan phases,
named-gate mapping, `docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md`, and
`scripts/test.ps1` as the canonical Windows/Codex Desktop CPython 3.12 test
wrapper. Verification: RED missing manifest/doc tests, focused `8 passed`,
full AMN2 suite `714 passed, 1 StarletteDeprecationWarning`, `git diff
--cached --check` passed. No live VPS, SSH, package apply/rebuild, service
restart/deploy, public exposure, config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive
action, Telegram action, secret publication or upstream/GPL code copy was
performed. Next recommendation: `FI-M001 + FI-M002 + FI-M003` local-only.

Phase 6 `P6-S004` closeout packet + next-chat handoff + fresh installer backlog grooming is closed as AMN3 docs-only work. Evidence: `research/amn2/phase-6-closeout-next-chat-fresh-installer-backlog-2026-06-13.md`. Added `docs/NEXT_CHAT_AMN2_AFTER_PHASE_6.ru.md` as the next active handoff after Phase 6 and `docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md` as a gated candidate backlog for the future clean installer. Phase 6 default lane is closed; public/self-service launch remains not opened. Remaining work is gated/deferred: `P6-C001`, `P6-C002`, `P6-C003`, `P6-C004`, `P6-C007`, `VPS-REBUILD-001`, Local Agent write/config routes, production peer/user mutation and carried `P4-PRVTPRO-REFRESH-003-LIVE`. Its recommended local-only bundle `FI-I001 + FI-I002 + FI-I003` was completed after Phase 6 in AMN2 `de635a0`; the current recommendation is `FI-M001 + FI-M002 + FI-M003`. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive action, Telegram action, secret publication or upstream/GPL code copy was performed.

Phase 6 `P6-X003` package runbook escaping hygiene is closed as AMN3 local-only docs/tooling hygiene. Evidence: `research/amn2/phase-6-package-runbook-escaping-hygiene-2026-06-13.md`. Added `scripts/check_markdown_hygiene.py` and `tests/test_markdown_hygiene.py` to catch accidental ASCII control characters in generated Markdown/operator docs, especially PowerShell backtick escape accidents such as `U+0008`, `U+0007` and `U+000B`. Verification: RED `python -m unittest tests.test_markdown_hygiene` failed while the tool was missing; GREEN returned `2 tests OK`; diagnostic run against the already-smoked unpacked `c46f664` operator doc failed with five expected findings. The already-smoked `dist/amn2-vps-update-and-smoke-kit-c46f664.zip` artifact was not rebuilt, repacked or altered. No live VPS command, SSH command, package apply, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive action, Telegram action, secret publication or upstream/GPL code copy was performed. `P6-X003` is removed from active Phase 6 plan.

Phase 6 `P6-C009` live update/smoke for AMN2 `c46f664` is closed as `live-update-smoke-pass`. Evidence: `research/amn2/phase-6-live-update-smoke-c46f664-2026-06-13.md`; package preflight evidence: `research/amn2/phase-6-current-head-package-preflight-c46f664-2026-06-13.md`. Built and applied `dist/amn2-vps-update-and-smoke-kit-c46f664.zip`, sha256 `5C952103B3435E1D30AF7CF0A70C40BC027885F1E860C31089DD4ACA3E8347EE`, from source zip `dist/amn2-codex-vps-test-prep-c46f664-source.zip`, sha256 `5A92EA9BD5B60626F120B5367A02EDDCB742ECF5E6C4FCB8444151BFEB18B248`. Source overlay updated `/opt/amn2` from `b3102db250da7ca9aef78ca095602187d0efc462` to `c46f664762d7774756b88db8d4e1ebc038b20bb5`; source update run_id `20260613T173232Z` passed; manual web/bot runtime was restarted with web bound to `127.0.0.1:3030`; read-only API smoke run_id `20260613T173738Z` passed with auth/listener/audit `passed`. Final remote listener snapshot showed only `127.0.0.1:3030`, with `3040/80/443` absent; external probes returned `000`; `VPS_APPLY_ENABLED=false` remained explicit. No config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, public exposure change, Telegram token use by Codex, live bot send, Telegram identity mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-C009` is removed from active Phase 6 plan. Latest VPS-smoked/package head is now `c46f664`. Follow-up added: `P6-X003` package runbook escaping hygiene.

Phase 6 `P6-C008` current-head package refresh/preflight for AMN2 `c46f664` is closed as AMN3 local package work with current-head smoke plan and named live gate checklist. Evidence: `research/amn2/phase-6-current-head-package-preflight-c46f664-2026-06-13.md`. Built `dist/amn2-vps-update-and-smoke-kit-c46f664.zip`, package sha256 `5C952103B3435E1D30AF7CF0A70C40BC027885F1E860C31089DD4ACA3E8347EE`; source zip `dist/amn2-codex-vps-test-prep-c46f664-source.zip`, source sha256 `5A92EA9BD5B60626F120B5367A02EDDCB742ECF5E6C4FCB8444151BFEB18B248`. Package hygiene passed with `kit_entries=5`, `source_entries=337`, `forbidden_source_entries=0`, shell scripts LF/no-BOM and commit bindings present; AMN2 focused suite returned `11 passed, 1 StarletteDeprecationWarning`; AMN2 toolchain check passed; AMN3 apply-script regression returned `2 tests OK`. `c46f664` is package-ready locally and not VPS-smoked; latest VPS-smoked/package head remains `b3102db`. Future live apply/smoke is tracked as `P6-C009` and requires exact separate named gate phrase: `Открываю P6-C009 live apply/smoke gate для c46f664 на текущем disposable VPS 89.185.80.166.` No live VPS command, SSH command, package upload/apply on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, Telegram token use, live bot send, Telegram identity mutation, secret-bearing evidence publication or upstream/GPL code copy was performed.

Phase 6 `P6-N001` public docs/API taxonomy and `P6-C007` checklist-only are closed as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-public-taxonomy-cleanup-checklist-2026-06-13.md`. AMN2 current branch head is `c46f664 Add public taxonomy cleanup checklist`, pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `b3102db Add client compatibility delivery boundary`, live-update-smoke-pass. The slice adds `app.services.public_productization_boundaries`, docs `docs/PUBLIC_DOCS_API_TAXONOMY.ru.md` and `docs/DESTRUCTIVE_CLEANUP_GATE_CHECKLIST.ru.md`, and API/web integration-status visibility. Public docs/API publication remains disabled and requires `P6-C001`; destructive cleanup/reinstall execution remains disabled and requires a separate named `P6-C007` gate with retention/data-loss decision, stop criteria and second confirmation. Verification: focused `11 passed, 1 StarletteDeprecationWarning`, security/hygiene `26 passed`, toolchain check passed, `git diff --check` passed. `P6-N001` is complete; `P6-C007` remains critical gated/deferred. Next recommendation: `P6-C008` current-head package refresh/preflight for `c46f664`, or a separately named live/public/destructive gate if the operator chooses.

Phase 6 `P6-I007` fresh-install wizard/bootstrap automation is closed as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-fresh-install-wizard-boundary-2026-06-13.md`. AMN2 current branch head is `60d2570 Add fresh install wizard boundary`, pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `b3102db Add client compatibility delivery boundary`, live-update-smoke-pass. The slice adds a local-only question-and-answer clean installer plan service, `install wizard`/`install plan` CLI commands, `docs/FRESH_INSTALL_WIZARD.ru.md` and integration status visibility. It does not execute install, cleanup, SSH, live VPS commands, public exposure, config delivery or write API; gated `yes` answers become stop-lines for `P6-C001`, `P6-C002`, `P6-C003` and `P6-C007`. Verification: focused `14 passed, 1 StarletteDeprecationWarning`, security/hygiene `26 passed`, toolchain check passed, `git diff --check` passed. `P6-I007` is complete; `P6-C007` remains critical gated/deferred. Its next recommendation was completed by `P6-N001` + `P6-C007` checklist-only.

Phase 6 `P6-C002-design` + `P6-I006` config-link/entitlement boundary is closed as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-config-link-entitlement-boundary-2026-06-13.md`. AMN2 current branch head is `d96112c Add config link entitlement boundary`, pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `b3102db Add client compatibility delivery boundary`, live-update-smoke-pass. The slice records a tokenized short config-link model without enabling real config delivery, public redeem, token issue runtime or secret-bearing output; records commercial entitlement/audit without payment provider, write API, automatic activation or config delivery on payment; adds blocked-future route policy entries for entitlement manual review, config-link issue and public token redeem; and updates API/web integration status. Verification: `37 passed, 1 StarletteDeprecationWarning` on bundled CPython 3.12.13, plus `git diff --check` passed. `P6-I006` is complete; `P6-C002` remains critical gated/deferred for actual config delivery and live/public token behavior. Next recommendation: `P6-I007` interactive fresh-install wizard/bootstrap automation as local-only docs/tests/code.

Phase 6 operator proposal added `P6-I007` Interactive fresh-install wizard/bootstrap automation as a very-important local-only task and `P6-C007` Destructive cleanup/reinstall gate for the current working VPS as critical gated/deferred work. The current working server was identified by the operator as `89.185.80.166`. `P6-I007` should build the future clean-install path through question-and-answer prompts, safe defaults, preflight validation, dry-run output, operator-provided secrets and no live/destructive execution by default. `P6-C007` must not run until the operator explicitly decides to assemble/test the clean installer, and must require a separate named destructive gate, explicit retention/data-loss decision and stop criteria. No live VPS command, SSH command, cleanup, reinstall, package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, Telegram action, secret publication or upstream/GPL code copy was performed by adding this plan item.

Phase 6 `P6-C006` live update/smoke for AMN2 `b3102db` is closed as `live-update-smoke-pass`. Evidence: `research/amn2/phase-6-live-update-smoke-b3102db-2026-06-13.md`; package preflight evidence: `research/amn2/phase-6-final-vps-refresh-package-b3102db-2026-06-13.md`. Built and applied `dist/amn2-vps-update-and-smoke-kit-b3102db.zip`, sha256 `B4C3FF33FD0A721C97A83EA8AF08D5E5B6EA5E8D1862EEB63494E8842D56A21B`, from source zip `dist/amn2-codex-vps-test-prep-b3102db-source.zip`, sha256 `72342DB625D53AE2F6B68835A1FC4E080684A4A1E9018E791820899BB9A09778`. Source overlay updated `/opt/amn2` from `2215761` to `b3102db250da7ca9aef78ca095602187d0efc462`; source update run_id `20260613T154511Z` passed; manual web/bot runtime was restarted with web bound to `127.0.0.1:3030`; read-only API smoke run_id `20260613T154826Z` passed with auth/listener/audit `passed`. A first smoke attempt was blocked because the default server name `debian-vps-1` was absent and this target uses `local`; the successful smoke explicitly used `AMN2_SERVER_NAME=local`. Final remote listener snapshot showed only `127.0.0.1:3030`, with `3040/80/443` absent; external probes returned `000`; `VPS_APPLY_ENABLED=false` remained explicit. No config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, public exposure change, Telegram token use by Codex, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-C006` is removed from active Phase 6 plan. Next recommendation: `P6-C002 + P6-I006` as local-only design/implementation for short one-tap tokenized config-link boundary plus commercial entitlement/audit boundary.

Phase 6 `P6-M004` iOS AmneziaWG import/connectivity diagnostic boundary, `P6-X001` Public product copy polish and `P6-X002` Brand/media consistency are now closed as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-client-compatibility-copy-boundary-2026-06-13.md`. AMN2 current branch head is `b3102db Add client compatibility delivery boundary`, pushed to `amn2/codex-vps-test-prep`; this head is now also the latest VPS-smoked/package head after `P6-C006`. The slice adds explicit client roles for iOS DefaultVPN as the primary RF-available iOS path, iOS AmneziaWG/Apple as an installed/legacy path, and Android AmneziaWG as a separate supported path; aligns Telegram delivery copy, web Config templates copy, API/web `/integration-status`, README and setup docs; keeps `.conf` as the first fallback; and records short one-tap tokenized config delivery links as part of `P6-C002`. Verification: RED client/status tests, focused `26 passed, 1 warning`, expanded `290 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. No config delivery, write API, public exposure, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-M004`, `P6-X001` and `P6-X002` are removed from active Phase 6 plan.

Phase 6 field diagnostic on 2026-06-13 added `P6-M004` iOS AmneziaWG import/connectivity diagnostic boundary as an important active task and `P6-C006` Final VPS package refresh/apply gate as critical gated/deferred work. Evidence: `research/amn2/phase-6-ios-amneziawg-field-diagnostic-2026-06-13.md`. Local-only review of the user-provided iPhone AmneziaWG log/screenshots showed the existing profile starts the tunnel and sends handshake traffic, but receives zero bytes, keeps `last_handshake_time_sec=0`, and times out after 12 seconds on the observed 2026-06-13 attempts. This points more toward reachability/live server/UDP/firewall/endpoint-port/server-key/peer-applied-state than local config syntax, but proof requires a separate named live diagnostic gate. A separate reported issue remains: new QR/`vpn://` import is not accepted by the iPhone AmneziaWG app. `P6-M004` must distinguish iOS DefaultVPN as the primary RF-available path, iOS AmneziaWG as an installed/legacy-client path, and Android AmneziaWG as a separate supported-client path. `P6-C006` is reserved for the end of Phase 6: package rebuild/apply, service restart, live bot verification and VPS smoke only after explicit named approval. No live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. Its next recommendation was completed by `P6-M004` + `P6-X001` + `P6-X002`.

Phase 6 `P6-N004` Aggregate telemetry retention/redaction policy and `P6-S002` Recurring upstream refresh incorporation are now closed as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-telemetry-retention-upstream-refresh-2026-06-13.md`. AMN2 current branch head is `a9f53d7 Add telemetry retention refresh policy`, pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `a9f53d7` is not package-rebuilt or VPS-smoked. The slice adds a retention/redaction and upstream refresh incorporation manifest, keeps raw telemetry export and upstream refresh live actions blocked, records weekly watcher outputs as candidate rows/evidence only, and exposes the safe boundary through integration status. Verification: RED `1 error, 1 warning`, focused `11 passed, 1 warning`, expanded `68 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. No live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-N004` and `P6-S002` are removed from active Phase 6 plan. Its next recommendation was completed by `P6-M004` + `P6-X001` + `P6-X002`; `P6-N001` remains conditional on public docs approval.

Phase 6 `P6-S003` Project operating system extraction template is now closed as AMN3 docs-only work. Evidence: `research/amn2/phase-6-project-operating-system-template-2026-06-13.md`. Created reusable clean-project templates `docs/templates/PROJECT_OPERATING_SYSTEM_TEMPLATE.ru.md` and `docs/templates/NEXT_PROJECT_BOOTSTRAP.ru.md` with source-of-truth fields, safety boundaries, priority active plan, standing rules, verification/evidence policy, decision log, release/deploy state and next-chat bootstrap. No AMN2 runtime code or gated action was performed. `P6-S003` is removed from active Phase 6 plan. Its next recommendation was completed by `P6-N004` + `P6-S002`.

Phase 6 `P6-M003` attach-existing-server reconciliation boundary and `P6-S001` release checklist/changelog are now closed as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-reconciliation-release-boundary-2026-06-13.md`. AMN2 current branch head is `3e1f4cc Add reconciliation release boundary`, pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `3e1f4cc` is not package-rebuilt or VPS-smoked. The slice adds a report-only attach-existing-server reconciliation and release checklist manifest, keeps live reconciliation, local device creation, peer removal, server config overwrite, package apply/rebuild on VPS, public exposure, config delivery, write API, Local Agent mutation and production peer/user mutation blocked, and exposes the safe boundary through integration status. Verification: RED `1 error, 1 warning`, focused `11 passed, 1 warning`, expanded `81 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. No live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-M003` and `P6-S001` are removed from active Phase 6 plan. Standing-rule addition: `P6-N004` Aggregate telemetry retention/redaction policy is added as a normal-priority Phase 6 task. Its next recommendation was refined to `P6-N004 + P6-S002`.

Phase 6 `P6-M002` health/status polling scheduler boundary and `P6-N002` admin analytics privacy boundary are now closed as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-privacy-status-analytics-boundary-2026-06-13.md`. AMN2 current branch head is `8f4ac6a Add privacy status analytics boundary`, pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `8f4ac6a` is not package-rebuilt or VPS-smoked. The slice adds a machine-checkable aggregate-only privacy/status manifest, keeps live probes, raw command output, endpoint export, per-peer health fields and per-user/per-peer analytics detail blocked, sanitizes API integration-status sensitive marker-name lists to counts, and exposes the safe boundary through integration status. Verification: RED `1 error, 1 warning`, focused `33 passed, 1 warning`, expanded `65 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. No live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-M002` and `P6-N002` are removed from active Phase 6 plan. Its next recommendation was completed by `P6-M003` + `P6-S001`.

Phase 6 `P6-I005` Telegram bot profile/icon apply gates are now closed as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-telegram-profile-icon-gate-policy-2026-06-13.md`. AMN2 current branch head is `19f3422 Add Telegram profile icon gate policy`, pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `19f3422` is not package-rebuilt or VPS-smoked. The slice adds a safe profile-icon apply gate manifest for access/support/news bots, records allowed default work as local validation/registry/checklist/safe evidence only, keeps Telegram API profile mutation, BotFather/manual mutation by Codex, live bot send and Telegram token use blocked, adds blocked-future surface policy entries, and exposes the safe gate through integration status. Verification: RED `6 failed, 27 passed, 1 warning`, focused `33 passed, 1 warning`, expanded `83 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. No live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-I005` is removed from active Phase 6 plan. Its next recommendation was completed by `P6-M002` + `P6-N002`.

Phase 6 `P6-I003` payments/manual approval boundary and `P6-I004` support/news bot production split are now closed as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-commercial-bot-productization-boundary-2026-06-13.md`. AMN2 current branch head is `0c6aa7c Add commercial bot productization boundary`, pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `0c6aa7c` is not package-rebuilt or VPS-smoked. The slice adds a safe productization manifest, keeps payment processor/webhook/automatic entitlement/config delivery on payment blocked, records manual approval as required, records future support/news bots as blocked-future with separate token/runtime requirements, adds blocked-future surface policy entries, and exposes the safe boundary through integration status. Verification: RED `1 error, 1 warning`, focused `29 passed, 1 warning`, expanded `81 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. No live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-I003` and `P6-I004` are removed from active Phase 6 plan. Proposed candidate: `P6-I006` Commercial entitlement/audit boundary, not active until accepted. Next recommendation: `P6-I005` Telegram bot profile/icon apply gates as local-only/docs/tests planning without Telegram identity mutation, live bot send, config/write/public/live gates.

Phase 6 `P6-M001` multi-server/multi-protocol capability registry and `P6-N003` integration status current-head alignment are now closed as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-capability-registry-integration-status-alignment-2026-06-13.md`. AMN2 current branch head is `3118b43 Make integration status source head dynamic`, pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `3118b43` is not package-rebuilt or VPS-smoked. The slice adds a safe capability registry to `/api/integration/status` and web `/integration-status`, records current implemented capability as single-server operator control for `amneziawg` on Docker, keeps future `wireguard`/`xray` protocol managers blocked-future with no upstream/GPL code copy, and separates current branch head from latest VPS-smoked/package head via local git with `unknown` fallback outside a checkout. Verification: RED `3 failed, 5 passed, 1 warning`, focused `8 passed, 1 warning`, expanded `46 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. No live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-M001` and `P6-N003` are removed from active Phase 6 plan. Next recommendation: `P6-I003` Payments/manual approval boundary if commercial access is enabled as local-only/docs/tests planning without opening public/payment-processor/config/write/live gates.

Phase 6 `P6-I002` user self-service surface separation is now closed as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-user-self-service-surface-boundary-2026-06-13.md`. AMN2 current branch head is `b676e1b Add self-service surface boundary`, pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `b676e1b` is not package-rebuilt or VPS-smoked. The slice adds `self-service` as a separate blocked-future surface, records future `/self-service` dashboard/config-delivery/device-revoke policy entries, requires separate self-service auth and own-account/device boundaries, and verifies no `/self-service*` routes are mounted in the current web/admin app. Verification: RED `4 failed, 23 passed`, focused `27 passed`, expanded `43 passed, 1 warning`, AMN2 `git diff --check` and staged check passed. No live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-I002` is removed from active Phase 6 plan. Next recommendation: `P6-I003` Payments/manual approval boundary if commercial access is enabled as local-only/docs/tests planning without opening public/payment-processor/config/write/live gates.

Phase 6 `P6-I001` scoped API tokens production implementation is now closed as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-scoped-api-tokens-production-implementation-2026-06-13.md`. AMN2 current branch head is `0b3ac1f Add API token production policy`, pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `0b3ac1f` is not package-rebuilt or VPS-smoked. The slice adds a machine-checkable production token policy manifest, keeps route token scopes to `server:read`/`metrics:read`, blocks future config/write/backup/Local Agent scopes, enforces a 30-day max TTL for route-connected tokens, aligns the disabled web/admin token form with that TTL and updates `docs/API_TOKEN_POLICY.ru.md`. Verification: focused `18 passed, 1 warning`, expanded `59 passed, 1 warning`, AMN2 `git diff --check` passed. No live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-I001` is removed from active Phase 6 plan. Its next recommendation was completed by `P6-I002`.

Phase 6 `P6-C005` production security review gate is closed as local/docs/security review. Evidence: `research/amn2/phase-6-production-security-review-gate-2026-06-13.md`. Decision: `production-security-review-complete-for-planning`; public/self-service launch remains `no-go` until separate named gates. AMN2 latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`; `VPS_APPLY_ENABLED=false` remains default. Focused AMN2 local security regression suite on CPython 3.12.13 returned `98 passed, 1 warning`. No live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-C005` is removed from active Phase 6 plan. New follow-up: `P6-N003` Integration status current-head alignment, normal local-only code/tests/docs.

Phase 4 main-chat handoff is now prepared:

```text
Phase 5 active handoff: docs/NEXT_CHAT_AMN2_PHASE_5_OPERATOR_PILOT.ru.md
Phase 5 explanation: operator-only pilot; default work is local-only/docs/tests/checklists; live/write/config/public/destructive actions require named gates.
entrypoint: docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md
research note: research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md
AMN3 Phase 4 coordination checkpoint before P4-N001 sync: 113c5ed Record Phase 4 bot admin read-only labels
Phase 4 completed local/default sequence: P4-C009, P4-I002, route/secret gate planning, P4-I003 design/plan/implementation, P4-I004, P4-N003, P4-I005, P4-N004, P4-N001 docs/status sync, P4-N002 protocol manager interface checklist, P4-X003 Russian-first operator docs polish, P4-X002 API/status/gate naming cleanup, P4-X001 read-only API docs grouping polish, P4-I001 second read-only UX pass closure
Phase 4 next stage: P4-NG Named Gate / Write API Readiness is active as docs-only planning; plan docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md; charter research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md
Phase 4 closed since P4-NG start: NG-C001 named gate charter, NG-C002 safety boundary restatement, NG-C003 secrets policy, NG-C004 go/no-go format, NG-S003 reusable named-gate evidence template, NG-C005 write API live-block assertion, WAPI-V001 write API threat model, WAPI-V002 write API route taxonomy, WAPI-V003 local fake-runner contract, WAPI-V004 idempotency/locking/partial-failure model, WAPI-V005 write API audit/redaction requirements, WAPI-I004 operation status model, WAPI-I003 scoped write-token model, WAPI-I002 config delivery decoupling, WAPI-I001 /api/clients design without live CRUD, WAPI-I005 web-panel gated action labels, NG-N003 operation queue design after write API contract, NG-N002 health/status polling design, NG-N001 attach-existing-server read-only reconciliation gate design, NG-N004 candidate registry update after every gate decision, NG-S001 status/transfer synchronization, NG-S002 next-chat handoff synchronization, NG-S004 visible active plan maintenance, NG-X003 stale wording cleanup, NG-X001 gate naming consistency, NG-X002 Russian-first operator wording polish, NG-SC001 Codex Security VPS risk checkpoint, P4-PRVTPRO-REFRESH-004 API taxonomy/OpenAPI grouping policy support, P4-DEVICE-SEQUENCE-EXTERNAL-IMPORT bot/admin device sequence and external-only backfill, P4-AMNEZIA-REFRESH-002 client import compatibility matrix, P4-BOT-ONBOARDING-001 bot onboarding language/header, P5-I003 runtime/toolchain standardization, P5-I002 external-only backfill rehearsal, P5-I004 operator-only smoke checklist, P5-M003 AMN3 evidence discipline, P5-M001 support/news bot asset inventory, P5-M005 bot media asset upload/apply boundary, P5-M004 web/admin header asset boundary, P5-M002 client config delivery QA, P5-M006 Telegram import link copy affordance, P5-N002 web-panel service-mode copy polish, P5-X002 bot labels and captions polish, P5-X001 Russian-first microtexts polish, P5-S002 active-plan stale recommendation cleanup, P5-C002 VPS retention decision, P5-C001 current-head package rebuild, P5-C003 live rollout for de25576, P5-C005 source-overlay permission preservation, P5-C004 secret handoff protocol, P5-N001 operator docs cleanup, P5-N003 client/platform compatibility refresh, P4-PRVTPRO-REFRESH-003 server status/latency UX boundary, P5-C006 current-head package rebuild for dd0dd44, P5-L002 bot media local registry, P5-L001 read-only status/latency display, P5-C008 current-head package rebuild for 9bff807, P5-S003 carried-items active-plan cleanup, P5-C007 live update/smoke for 9bff807, P5-O001 operator-only post-update UI smoke for 9bff807, P5-O002 web-admin gated-action and Russian-first UX cleanup, P5-C009 current-head package rebuild for 2215761, P5-C010 live update/smoke for 2215761, P5-D001 operator-only pilot acceptance and Phase 6 entry decision
P4-NG template: research/amn2/phase-4-ng-named-gate-evidence-template-2026-06-10.md
Phase 5/6 forward plan: docs/PHASE_5_6_FORWARD_PLAN.ru.md
Phase 5 next-chat handoff: docs/NEXT_CHAT_AMN2_PHASE_5_OPERATOR_PILOT.ru.md
Phase 6 next-chat handoff: docs/NEXT_CHAT_AMN2_PHASE_6_PRODUCTIZATION.ru.md
P4-NG write live-block evidence: research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md
P4-NG write API threat model evidence: research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md
P4-NG write API route taxonomy evidence: research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md
P4-NG local fake-runner contract evidence: research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md
P4-NG idempotency/locking/partial-failure model evidence: research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md
P4-NG write API audit/redaction requirements evidence: research/amn2/phase-4-wapi-v005-write-api-audit-redaction-requirements-2026-06-10.md
P4-NG operation status model evidence: research/amn2/phase-4-wapi-i004-operation-status-model-2026-06-10.md
P4-NG scoped write-token model evidence: research/amn2/phase-4-wapi-i003-scoped-write-token-model-2026-06-10.md
P4-NG config delivery decoupling evidence: research/amn2/phase-4-wapi-i002-config-delivery-decoupling-2026-06-10.md
P4-NG /api/clients design evidence: research/amn2/phase-4-wapi-i001-clients-design-without-live-crud-2026-06-10.md
P4-NG web-panel gated action labels evidence: research/amn2/phase-4-wapi-i005-web-panel-gated-action-labels-2026-06-10.md
P4-NG stale wording cleanup evidence: research/amn2/phase-4-ng-x003-stale-wording-cleanup-2026-06-10.md
P4-NG gate naming consistency evidence: research/amn2/phase-4-ng-x001-gate-naming-consistency-2026-06-10.md
P4-NG Russian-first operator wording evidence: research/amn2/phase-4-ng-x002-russian-first-operator-wording-polish-2026-06-10.md
P4-NG Codex Security VPS risk checkpoint evidence: research/amn2/phase-4-ng-sc001-codex-security-vps-risk-checkpoint-2026-06-10.md
P4-NG NG-V001 read-only VPS baseline gate opening evidence: research/amn2/phase-4-ng-v001-read-only-vps-baseline-gate-2026-06-10.md
P4-NG default docs-only cosmetic queue: closed after NG-X002; NG-SC001 security checkpoint is closed; NG-V001 is closed-go
P4-NG live/write/destructive status: NG-V001 read-only VPS baseline passed safe summary checks; write API live work remains blocked until separate P4-NG-WRITE-API-LIVE-GATE; destructive VPS rebuild gate VPS-REBUILD-001 remains defer; package build/hygiene evidence research/amn2/vps-rebuild-001-package-build-hygiene-2026-06-10.md built historical dist/amn2-vps-update-and-smoke-kit-1508e3c.zip; Phase 5 P5-C001 rebuilt the package from AMN2 de2557639cd3853e6973002be3cab24033d2f722 as dist/amn2-vps-update-and-smoke-kit-de25576.zip with sha256 B35D176F871ADB3B4CFDD3EC8D55B9BC5DF972E537038345B2E66899CFD21F87 and source sha256 CFF46C44CFB8F321DEB88CE64A0F5D2154CFC02CD3931CF9955DDC466615B8CC; Phase 5 P5-C003 applied that package to the disposable test VPS, source overlay run_id 20260612T054750Z passed, read-only API smoke run_id 20260612T054913Z passed, and web/bot services are active after service permission repair. Phase 5 P5-C005 fixed the future source-overlay apply-script template so rebuilt kits preserve target-root metadata and service-readable source permissions. Phase 5 P5-C006 rebuilt the current package from AMN2 dd0dd442f0f25c1113accdc625dd16a96059eba4 as dist/amn2-vps-update-and-smoke-kit-dd0dd44.zip with sha256 BB510BEABEB5ACCB7394C09F43EA7288BB08FC1352CCD35DA5AFF781E1B48E6D and source sha256 E29DFD7B64727BC75C677EDE2B897C6C972AB25243FD7713B767ABE1E29E2BD1; status was package-ready-not-vps-smoked, but it was superseded as current-head package evidence because AMN2 advanced to 9bff807. Phase 5 P5-L002/P5-L001 completed AMN2 local-only bot media registry and cached read-only status display at 9bff807. Phase 5 P5-C008 rebuilt the current package from AMN2 9bff807a1d8fcceb833c1ef864064d2af6aaaff1 as dist/amn2-vps-update-and-smoke-kit-9bff807.zip with sha256 882619B665B93CF4D6EFAB7977F7AE968F032C08C74CCFDA19A6B06BD629FAF9 and source sha256 5109C0FD7FBF40BB2F48C7476015E8BD4CCCF3AF54CAD702160488B0CE898AFD; status at rebuild time was package-ready-not-vps-smoked. Phase 5 P5-C007 applied that package to the disposable test VPS, source overlay run_id 20260612T180725Z passed, read-only API smoke run_id 20260612T184701Z passed, web/bot services are active after restart, and remote listener snapshot remained 3030 loopback-only with 3040/80/443 absent as remote listeners. Phase 5 P5-C009 then rebuilt the package from AMN2 221576169a84bbf662114c564e83c41fba0091b5; Phase 5 P5-C010 applied that package to the disposable test VPS, source overlay run_id 20260613T045004Z passed, read-only API smoke run_id 20260613T045107Z passed, web/bot services are active after restart, and remote listener snapshot remained 3030 loopback-only with 3040/80/443 absent as remote listeners. Phase 5 P5-C004 created the secret handoff protocol: regenerate on target where possible, external secrets only through operator local/private channel, safe summaries only. Phase 5 P5-N001 removed stale active operator-doc references to already closed gate slices and refreshed the Phase 5 plan/handoff/status/backlog trail. Phase 5 P5-C002 records the current target as a disposable test VPS with no important project data to preserve; no public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation or destructive provider action was opened by P5-C003/P5-C005/P5-C004/P5-N001/P5-C006/P5-L002/P5-L001/P5-C008/P5-C007/P5-C009/P5-C010.
PRVTPRO refresh 2026-06-10: research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md
PRVTPRO AMN2 local-only order: P4-PRVTPRO-REFRESH-002 expiration-field contract tests completed in AMN2 commit b2eceeb111a0a27e41daf7b9ae7c79b5a0195e51; P4-PRVTPRO-REFRESH-001 read-only About/Version/Build status completed in AMN2 commit dc7966628e490da018f55fafe0fc559b44cc1dfa; both merged into AMN2 codex-vps-test-prep at 1508e3c4a100b76815b29f91757290f1266f813d; P4-PRVTPRO-REFRESH-004 API taxonomy/OpenAPI grouping completed as AMN3 docs-only policy support in research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md; P4-PRVTPRO-REFRESH-003 read-only server status/latency UX is closed as carried from Phase 4: design boundary closed in AMN3 and local cached display implemented by P5-L001; live probes/actions remain gated
PRVTPRO hybrid-only: HYB-PRVTPRO-REFRESH-001 AdGuard Home, HYB-PRVTPRO-REFRESH-002 SOCKS5 manager, HYB-PRVTPRO-REFRESH-003 Xray migration/attach existing install, HYB-PRVTPRO-REFRESH-004 multi-protocol capability registry
PRVTPRO negative controls: GPL-3.0 research-only; no code/templates/UI/manager implementations/workflows copied; no admin-equivalent Bearer token model; no public panel/config delivery/reboot/backup/import/server cleanup without separate named gate
AMN2 source-overlay/package head: c46f664 Add public taxonomy cleanup checklist (VPS-smoked in P6-C009)
AMN2 current branch head: 525a9cd Add fresh installer evidence readiness (local-only, not package-rebuilt/VPS-smoked)
AMN2 latest VPS-smoked package: dist/amn2-vps-update-and-smoke-kit-c46f664.zip, sha256 5C952103B3435E1D30AF7CF0A70C40BC027885F1E860C31089DD4ACA3E8347EE, live-update-smoke-pass
AMN2 package/smoke status for c46f664: live-update-smoke-pass; source zip dist/amn2-codex-vps-test-prep-c46f664-source.zip sha256 5A92EA9BD5B60626F120B5367A02EDDCB742ECF5E6C4FCB8444151BFEB18B248; evidence research/amn2/phase-6-live-update-smoke-c46f664-2026-06-13.md
AMN2 bot config delivery localization: research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-11.md and research/amn2/phase-4-bot-config-delivery-localization-2026-06-11.md; no live bot restart/deploy or real config delivery performed by Codex
AMN2 device sequence/external import visibility: research/amn2/phase-4-device-sequence-external-import-2026-06-11.md; new bot-approved device names continue as `Neobyatnaya-AMNZ-N` with default seed `4`, old externally-created test peers can be imported as `external_only`, and config resend/secrets/email-config stay blocked when original client private key is unavailable
AMN2 client compatibility matrix: research/amn2/phase-4-amnezia-client-compatibility-matrix-2026-06-11.md; `.conf` remains reliable fallback, DefaultVPN QR is not universal, AmneziaVPN platform constraints are tracked, and bot app-links guidance is safe/local-only
AMN2 bot onboarding language/header: research/amn2/phase-4-bot-onboarding-language-header-2026-06-11.md; `/start` sends supplied `NEOBYATNAYA-AMNZ-BOT.png`, shows Russian/English language choice, persists `users.locale` with Russian default, and does not deploy/restart the live bot
AMN2 runtime/toolchain standardization: research/amn2/phase-5-runtime-toolchain-standardization-2026-06-11.md; CPython 3.12.x is pinned as supported local runtime, `python -m app.toolchain check` is available, one `.venv` per worktree is required, and Python 3.14 remains a separate future upgrade gate
AMN2 external-only backfill rehearsal: research/amn2/phase-5-external-only-backfill-rehearsal-2026-06-11.md; old externally issued test devices can be rehearsed from JSON with `device backfill-external`, dry-run does not mutate the DB copy, apply writes only to an operator-selected local DB copy, and all imported rows remain `external_only`
AMN2 operator-only smoke checklist: docs/AMN2_OPERATOR_ONLY_SMOKE_CHECKLIST.ru.md and research/amn2/phase-5-operator-only-smoke-checklist-2026-06-11.md; covers web/admin loopback, bot dry/local behavior, six read-only API routes and no-public-exposure evidence without authorizing live/write/config/public/destructive actions
AMN3 Phase 5 evidence discipline: docs/AMN3_PHASE5_EVIDENCE_DISCIPLINE.ru.md and research/amn2/phase-5-amn3-evidence-discipline-2026-06-11.md; each Phase 5 slice must leave evidence, status/backlog/forward-plan/next-chat/context sync, active-plan cleanup, safe evidence policy and an open next recommendation
AMN2 support/news bot asset inventory: docs/AMN2_SUPPORT_NEWS_BOT_ASSET_INVENTORY.ru.md and research/amn2/phase-5-support-news-bot-asset-inventory-2026-06-11.md; current access bot keeps only `NEOBYATNAYA-AMNZ-BOT.png`, while support/news/admin asset filenames remain planning-only and require separate token/runtime/design gates before any implementation; bot media is split into local/runtime header images and Telegram profile icons, where profile icon apply is live Telegram identity mutation and needs a named gate
AMN2 bot media asset upload/apply boundary: docs/AMN2_BOT_MEDIA_ASSET_UPLOAD_BOUNDARY.ru.md and research/amn2/phase-5-bot-media-asset-upload-boundary-2026-06-11.md; recommended future path is operator-only local validation/registry first, with profile icon apply through Telegram API or manual operator action blocked until a named Telegram identity gate
AMN2 web/admin header asset boundary: docs/AMN2_WEB_ADMIN_HEADER_ASSET_BOUNDARY.ru.md and research/amn2/phase-5-web-admin-header-asset-boundary-2026-06-11.md; `NEOBYATNAYA-AMNZ-ADMIN-PANEL.png` is scoped only to the web/admin product surface, not bot runtime, and active Russian plans should keep stable IDs with Russian-first task titles
AMN2 client config delivery QA: docs/AMN2_CLIENT_CONFIG_DELIVERY_QA.ru.md and research/amn2/phase-5-client-config-delivery-qa-2026-06-11.md; safe Android/iOS/Desktop Telegram review is docs-only/local-only, `.conf` remains reliable fallback, QR/`vpn://` remain secret-bearing, and the operator requirement is one-tap clipboard copy for the import link; plain text selection is only a temporary fallback, and follow-up `P5-M006` completed the bounded local copy affordance.
AMN2 Telegram import link copy affordance: research/amn2/phase-5-telegram-import-link-copy-2026-06-11.md; AMN2 commit `ad6aa1b` adds a `Скопировать ссылку` inline copy button for exact full `vpn://` links that fit Telegram copy-text limits, keeps over-limit raw links on visible-text plus `.conf`/QR fallback, and does not open config-delivery/public/self-service gates
AMN2 web-panel service-mode/external-only copy: research/amn2/phase-5-web-panel-service-mode-copy-2026-06-11.md; AMN2 commit `17454e9` clarifies operator-only boundary, read-only server actions and external-only device limits in web/admin copy without route/action/delivery changes
AMN2 bot labels/captions polish: research/amn2/phase-5-bot-labels-captions-2026-06-11.md; AMN2 commit `fed832c` clarifies `.conf`, QR and `vpn://` delivery captions/messages without changing delivery behavior
AMN2 Russian-first microtexts polish: research/amn2/phase-5-russian-first-microtexts-2026-06-11.md; AMN2 commit `de25576` translates visible bot/admin and web-panel boundary microtexts while preserving technical IDs and delivery behavior
AMN3 active-plan stale recommendation cleanup: research/amn2/phase-5-active-plan-stale-recommendation-cleanup-2026-06-12.md; `P5-S002` closed, simple/cosmetic active groups are empty, and the next move must be an explicit conditional/gated operator choice rather than automatic default local-only continuation
AMN3 VPS retention decision: research/amn2/phase-5-vps-retention-disposable-test-server-2026-06-12.md; `P5-C002` closed for current disposable test VPS, no important project data to preserve; its next recommendation was completed by `P5-C001`
AMN3 current-head package rebuild: research/amn2/phase-5-current-head-package-rebuild-2026-06-12.md; `P5-C001` closed as local package rebuild from AMN2 `de25576`, package `dist/amn2-vps-update-and-smoke-kit-de25576.zip` sha256 `B35D176F871ADB3B4CFDD3EC8D55B9BC5DF972E537038345B2E66899CFD21F87`, source sha256 `CFF46C44CFB8F321DEB88CE64A0F5D2154CFC02CD3931CF9955DDC466615B8CC`, status `package-ready-not-vps-smoked`; its next recommendation was completed by `P5-C003`
AMN3 live rollout: research/amn2/phase-5-live-rollout-de25576-2026-06-12.md; `P5-C003` closed for disposable test VPS, source overlay and read-only API smoke passed, web/bot active after permission repair, public `3040/80/443` absent, its next recommendation was completed by `P5-C005`
AMN3 source-overlay permission preservation: research/amn2/phase-5-source-overlay-permission-preservation-2026-06-12.md; `P5-C005` closed as local package tooling/test fix, `scripts/vps/amn2_apply_source_zip.sh` now preserves target-root metadata, uses service-readable source permissions and has regression coverage; its next recommendation was completed by `P5-C004`
AMN3 secret handoff protocol: docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md and research/amn2/phase-5-secret-handoff-protocol-2026-06-12.md; `P5-C004` closed as docs-only protocol for Telegram token, web secret, server config and bootstrap values, with operator-local channel only, safe summary fields and stop lines; its next recommendation was completed by `P5-N001`
AMN3 operator docs cleanup: research/amn2/phase-5-operator-docs-cleanup-2026-06-12.md; `P5-N001` closed as docs-only cleanup that removed stale active references to already closed gate slices and refreshed the Phase 5 handoff/status/context/backlog trail; its next recommendation was completed by `P5-N003`
AMN2 client/platform compatibility refresh: research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-12.md and research/amn2/phase-5-client-platform-compatibility-refresh-2026-06-12.md; `P5-N003` closed in AMN2 commit `dd0dd44`, updating Linux guidance to generic Linux x64 tar available while not promising distro-specific packages; its next recommendation was completed by `P4-PRVTPRO-REFRESH-003`
AMN2 read-only server status/latency UX boundary: docs/AMN2_READ_ONLY_SERVER_STATUS_LATENCY_UX_BOUNDARY.ru.md and research/amn2/phase-5-prvtpro-server-status-latency-boundary-2026-06-12.md; carried-from-Phase-4 `P4-PRVTPRO-REFRESH-003` closed in Phase 5: design boundary closed as AMN3 docs-only, local cached display implemented by `P5-L001`, live probes/actions remain gated
AMN3 current-head package rebuild for dd0dd44: research/amn2/phase-5-current-head-package-rebuild-dd0dd44-2026-06-12.md; `P5-C006` closed as local package rebuild from AMN2 `dd0dd44`, package `dist/amn2-vps-update-and-smoke-kit-dd0dd44.zip` sha256 `BB510BEABEB5ACCB7394C09F43EA7288BB08FC1352CCD35DA5AFF781E1B48E6D`, source sha256 `E29DFD7B64727BC75C677EDE2B897C6C972AB25243FD7713B767ABE1E29E2BD1`, status `package-ready-not-vps-smoked`; now superseded as current-head package evidence by AMN2 `9bff807`
AMN2 local bot media and read-only status summaries: research/amn2/phase-5-local-bot-media-and-status-summaries-2026-06-12.md; `P5-L002` and `P5-L001` closed in AMN2 commit `9bff807`, focused final `71 passed, 1 warning`, full final `671 passed, 1 warning`; its package rebuild requirement was completed by `P5-C008`
AMN3 current-head package rebuild for 9bff807: research/amn2/phase-5-current-head-package-rebuild-9bff807-2026-06-12.md; `P5-C008` closed as local package rebuild from AMN2 `9bff807`, package `dist/amn2-vps-update-and-smoke-kit-9bff807.zip` sha256 `882619B665B93CF4D6EFAB7977F7AE968F032C08C74CCFDA19A6B06BD629FAF9`, source sha256 `5109C0FD7FBF40BB2F48C7476015E8BD4CCCF3AF54CAD702160488B0CE898AFD`, status at rebuild time `package-ready-not-vps-smoked`; its VPS-path recommendation was completed by `P5-C007`
AMN3 live update/smoke for 9bff807: research/amn2/phase-5-live-update-smoke-9bff807-2026-06-12.md; `P5-C007` closed as live update/smoke on the disposable test VPS, source overlay run_id `20260612T180725Z`, read-only API smoke run_id `20260612T184701Z`, web/bot active after restart, remote listener `3030` loopback-only and `3040/80/443` absent as remote listeners; no config delivery/write API/public exposure change
AMN3 operator-only post-update UI smoke for 9bff807: research/amn2/phase-5-operator-post-update-ui-smoke-9bff807-2026-06-12.md; `P5-O001` closed as named-gate UI smoke with decision `needs-fix`; authenticated GET navigation through the operator SSH local port forward loaded the checked web/admin routes, no write/config/token/public/destructive action was performed, and its findings were addressed locally by `P5-O002`
AMN2 web-admin gated-action and Russian-first UX cleanup: research/amn2/phase-5-web-admin-gated-action-russian-ux-2026-06-12.md; `P5-O002` closed in AMN2 commit `2215761`, making the sampled web/admin UI use `AmneziyaDA`, Russian-first headings/navigation, centered two-line dashboard counts and disabled named-gate create/token/template write affordances; focused P5-O002 `4 passed, 1 warning`, expanded web regression `90 passed, 1 warning`; its package rebuild recommendation was completed by `P5-C009`
AMN3 current-head package rebuild for 2215761: research/amn2/phase-5-current-head-package-rebuild-2215761-2026-06-13.md; `P5-C009` closed as local package rebuild from AMN2 `2215761`, package `dist/amn2-vps-update-and-smoke-kit-2215761.zip` sha256 `6C360E8005E117EC59DD2829E9C4E9D2F36B5070275CD989D9D51A0675CF8B44`, source sha256 `825D1EF34F8DF11C0DB12B7A3DCDAE8FE79F04A8C56113CBA9CAEA3ECDBCC38B`, status at rebuild time `package-ready-not-vps-smoked`; its live update/smoke recommendation was completed by `P5-C010`
AMN3 live update/smoke for 2215761: research/amn2/phase-5-live-update-smoke-2215761-2026-06-13.md; `P5-C010` closed on the disposable test VPS as `live-update-smoke-pass`, source overlay run_id `20260613T045004Z` passed, read-only API smoke run_id `20260613T045107Z` passed, web/bot services are active after restart, remote listener snapshot remained `127.0.0.1:3030` only with `3040/80/443` absent, and `VPS_APPLY_ENABLED=false` remained explicit. Next recommendation is `P5-D001` operator-only pilot acceptance and Phase 6 entry decision.
AMN3 operator-only pilot acceptance: research/amn2/phase-5-operator-pilot-acceptance-phase-6-entry-2026-06-13.md; `P5-D001` closed as docs-only decision, `operator-only-pilot-accepted`, Phase 5 default queue empty, Phase 6 `planning-ready only`, and `docs/NEXT_CHAT_AMN2_PHASE_6_PRODUCTIZATION.ru.md` created. Next recommendation is `P6-C005` Production security review gate as local/docs/security review; public exposure, config delivery, write API, backup/import/reboot, Local Agent write/config routes, destructive rebuild and production peer/user mutation remain not executed and gated.
Deferred gated items not executed: `VPS-REBUILD-001`, write API, config delivery, public exposure and `P4-PRVTPRO-REFRESH-003-LIVE` probes/actions. Safe PRVTPRO design/local display is closed, but live probes/actions are not done.
AMN3 carried-items cleanup: research/amn2/phase-5-carried-items-active-plan-cleanup-2026-06-12.md; `P5-S003` closed as docs-only cleanup so carried Phase 4 items remain visible with source phase/gate labels but are not active pending work
Phase 5 handoff/automation sync: docs/NEXT_CHAT_AMN2_PHASE_5_OPERATOR_PILOT.ru.md; existing heartbeat automations `amnezia-weekly-upstream-refresh`, `prvtpro-weekly-upstream-refresh` and `weekly-kyoresuas-upstream-refresh` were updated to Phase 5 prompts without creating duplicates; in this Phase 5 thread, only `amnezia-weekly-upstream-refresh` was retargeted because the app rejected multiple active heartbeat automations on one thread
target VPS mode: service-mode web/bot active, loopback-only
operator access: SSH local port forward to 127.0.0.1:3030, external browser only
public/direct 3030: closed by loopback bind
public API 3040: absent/closed
TCP 80/443: absent
domain/Caddy/HTTPS public cutover: deferred
VPS_APPLY_ENABLED: false
remaining approved test peers: Neobyatnaya-AMNZ-1, Neobyatnaya-AMNZ-2
revoked test peers: Neobyatnaya-AMNZ-3, Neobyatnaya-AMNZ-4
```

Use Phase 4 as the unified product/API planning gate. Do not reopen Phase 3 service-mode loopback as pending. Do not run live VPS commands from the main chat by default. PRVTPRO/Web Panel and KYORESUAS/API outputs enter as candidate rows first; any public API, direct public web/admin, HTTPS reverse proxy, config delivery, write CRUD, Local Agent mutation, backup/import/reboot or production peer mutation requires a separate named gate. `P4-I001` is closed as not needed now; do not reopen a second private-panel UX pass by default.

Use P4-NG as the active gate-first stage. It starts with docs-only gate policy and does not authorize SSH, VPS sampling, public exposure, write API, config delivery or production mutation by itself.

Current private/local read-only API grouping after `P4-X001`: server inventory/status (`GET /api/servers`, `GET /api/servers/{server_name}/summary`), integration/service boundary (`GET /api/integration/status`), Local Agent runtime summary (`GET /api/local-agent/runtime/summary`) and aggregate metrics (`GET /api/metrics/summary`, `GET /api/users/summary`). This is docs/navigation grouping only; it does not authorize public OpenAPI/docs exposure, route expansion, config delivery or write routes.

# Historical Override 2026-06-07

`amn2/codex-vps-test-prep` VPS-smoked source overlay is `f7f6131 Update integration status for c92 manual prelaunch`. The app-code read-only slice `62ff184 Update controlled prod status visibility` passed real VPS git-checkout smoke on `/opt/amn2-git`, then the `42ffa65` AMN3 package was applied to `/opt/amn2` through safe source-overlay update and passed read-only loopback API smoke. The controlled production safety follow-up `c92bd1a` passed safe source-overlay update and read-only API smoke on `/opt/amn2`; the status-alignment follow-up `f7f6131` has now also passed read-only loopback API smoke. Previous source overlay `c92bd1a Bind web admin systemd to loopback` remains the web-admin loopback/manual-runtime baseline; `42ffa65 Record git checkout smoke status` remains historical status-visibility baseline; `c8a6363 Add Local Agent runtime summary mapper` remains historical smoke-passed baseline.

Repeat confirmation 2026-06-07: the same `42ffa65` source overlay passed another read-only loopback API smoke with `run_id=20260607T165807Z`, `checked_routes=6`, auth `401/403/401`, listener passed and audit passed. Evidence: `research/amn2/controlled-prod-status-visibility-vps-repeat-smoke-2026-06-07.md`.

This update comes from neighboring AMN2 docs/commits after the `c8a6363` package work. It changes the coordination state, not the safety boundary: no public API `3040`, no API `config:read`, no `/api/clients` write CRUD, no public/self-service config delivery, no Local Agent mutations, no backup/import/reboot, and no new live peer operations.

Latest local AMN2 head and latest proven VPS-smoked source overlay are now `f7f6131 Update integration status for c92 manual prelaunch`. Evidence: `research/amn2/manual-prelaunch-integration-status-2026-06-07.md`; package evidence: `research/amn2/f7f6131-status-alignment-vps-package-2026-06-07.md`; smoke evidence: `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`. AMN3 package and source-overlay smoke evidence:

```text
dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
sha256: EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12
source sha256: 272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2
latest AMN2 repository head: f7f6131 Update integration status for c92 manual prelaunch
latest AMN2 head status: read-only status visibility, VPS source-overlay-smoked
status-alignment package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
status-alignment package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
status-alignment source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
status-alignment package status: read-only-vps-smoke-pass
status-alignment VPS smoke: passed
status-alignment source update run_id: 20260607T203721Z
status-alignment api smoke run_id: 20260607T203730Z
status-alignment latest repeat api smoke run_id: 20260607T204300Z
status: read-only-vps-smoke-pass
source_update_run_id: 20260607T182118Z
api_smoke_run_id: 20260607T182131Z
checked_routes: 6
routes: servers, integration_status, local_agent_runtime_summary, server_summary, metrics_summary, users_summary
route_status_codes: all 200
forbidden_markers: none
evidence: research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md
smoke evidence: research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md
```

Purpose of the c92 baseline: make the web/admin systemd backend listen on `127.0.0.1:3030` for approved HTTPS reverse proxy mode before controlled production launch. Current VPS-smoked source overlay is now `f7f6131`.

Manual runtime follow-up on validation VPS `mirror`: backup create/verify passed, safe preflight passed, API smoke-cycle summary passed with six read-only routes, manual web and bot processes are present, manual web `/login` returned `200` on `127.0.0.1:3030`, direct public web `3030` is not exposed, public API `3040` is not exposed, `systemd` is not used, and `VPS_APPLY_ENABLED=false`. Evidence: `research/amn2/c92bd1a-manual-prelaunch-evidence-2026-06-07.md`.

Previous AMN3 source-overlay update kit result:

```text
dist/amn2-vps-update-and-smoke-kit-42ffa65.zip
sha256: 5B43B467E014E87FEC1E49E8D9A8B7A2FBF841541BE88FDC6768097806240E39
source sha256: 8A5B83D9AB95BE4230AAC221CE0321A37EF37E4E4B6EAB5EDECAE3C98A944829
status: read-only-vps-smoke-pass
source_update_run_id: 20260607T165559Z
api_smoke_run_id: 20260607T165625Z
latest_repeat_api_smoke_run_id: 20260607T165807Z
checked_routes: 6
listener: 127.0.0.1:3040 loopback-only
evidence: research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md
```

New target VPS bootstrap 2026-06-08 first passed as `partial-pass`: base OS packages, Docker runtime with no containers, `/opt/amn2` venv, `f7f6131` source overlay, Python dependencies, DB schema init, partial loopback API `/api/servers` probe with token revoke, and encrypted backup create/verify passed. Evidence: `research/amn2/target-server-bootstrap-evidence-2026-06-08.md`.

Target VPS AWG2 runtime gate 2026-06-09 is now `read-only-smoke-pass`: `amnezia-awg2` Docker runtime was built and started, real target `servers.yml` was created on the VPS through a secret-safe channel, AMN2 loader accepted it, and official read-only API loopback smoke passed with `run_id=20260609T043158Z`, `checked_routes=6`, auth `401/403/401`, listener passed and audit passed. Evidence: `research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md`.

Target VPS live peer gate 2026-06-09 is now `verified-live`: exactly one disposable test peer passed dry-run apply/revoke, live apply/sync/revoke/sync, ended with peer count `0`, and post-gate read-only API loopback smoke passed with `run_id=20260609T045546Z`, `checked_routes=6`. Evidence: `research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md`.

Target VPS manual web/bot gate 2026-06-09 is now `passed`: bot network readiness passed for `@NeobyatnayaAMNZ_bot`, web admin password/session secret are present, temporary manual web/admin `/login` returned HTTP `200` on loopback `127.0.0.1:3030`, and cleanup left TCP `3030`/`3040` absent with AWG2 running and peer count `0`. Evidence: `research/amn2/target-server-manual-web-bot-evidence-2026-06-09.md`.

Next gate is either staying in manual runtime mode for product/API work, or a separate service-mode gate only if `systemd`/HTTPS reverse proxy deployment becomes required. For consolidating AMN2/API, Phase 2 live gate and PRVTPRO/Web Panel work, use `docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md` and `research/amn2/unified-prod-gate-handoff-2026-06-08.md`; production peer commands and broader write surfaces still require dedicated gates and safe summaries.

# Historical Override 2026-06-06

Historical 2026-06-06 source-overlay head was `c8a6363 Add Local Agent runtime summary mapper`. AMN3 update+smoke package for that source overlay is `c8a6363` and passed real VPS read-only smoke on 2026-06-06, `run_id=20260606T202040Z`. `32d01fd` is now the historical prior VPS-smoked runtime/source, `run_id=20260606T185114Z`; `1a193b9` is the previous historical runtime/source before that.

Read-only integration status update 2026-06-06: `32d01fd` updates `/api/integration/status` to report `read_only_vps_smoked`, Phase 2 `verified_live`, and controlled-prod readiness pending without enabling write routes or write operations. AMN3 evidence is `research/amn2/integration-status-controlled-prod-update-2026-06-06.md`. The previous local-only operation-contract fast-forward remains recorded at `research/amn2/remote-partial-failure-contract-2026-06-06.md`.

```text
AMN3 package for historical 2026-06-06 source overlay: dist/amn2-vps-update-and-smoke-kit-c8a6363.zip
sha256: 027ECC1BAD7321FCCD61A4CCCA3AC9F06AAA9AC6A3D7115B4813253D19C2CFBF
source zip: dist/amn2-codex-vps-test-prep-c8a6363-source.zip
source sha256: E1E198979D988B3A5AA038CF732B8DCDBE854C48A6D381FADBA05BFDEE0251C6
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
```

Phase 2 live single disposable test peer apply/revoke is verified-live on stable `7764ae7`; `568c611` adds safer `--preshared-key-stdin` handling and passed read-only VPS update/smoke.

```text
AMN3 evidence: research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md
result: verified-live
scope: exactly one disposable test peer apply/sync/revoke/sync
```

This does not unlock broad write API, public/self-service config delivery, API `config:read`, `/api/clients` CRUD, backup/import/reboot routes, Local Agent mutations or public web/API exposure. Older `c92bd1a`, `42ffa65`, `c8a6363`, `32d01fd`, `294803e`, `7764ae7`, `568c611` and `1a193b9` package blocks below are historical evidence; `f7f6131` is the current VPS-smoked runtime/source baseline.
# VPN Ops Lab / Amneziya: импорт контекста из чатов

Дата снимка: 2026-06-02.

Обновлено: 2026-06-02 после повторного прохода по проектным чатам, пушам AMN3/`amn2`, VPS install package и активной ветке `codex/read-only-api-route-shell`.

Документ нужен для главного coordination-чата. Он собирает только рабочий контекст, который нужен для решений по `amn2`, будущему hybrid и общему Codex skill. Это не implementation plan и не разрешение на перенос функций.

## Актуализация 2026-06-02

Стабильная точка правды `amn2`:

```text
repo: C:\Users\SooL\Documents\Amneziya
branch: codex-vps-test-prep
remote branch: amn2/codex-vps-test-prep
latest committed head: 7764ae7 Cover integration status in API smoke
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
status: remote branch current after read-only API shell and API/web-panel finish merge
```

Активная рабочая ветка `amn2` для установки/API smoke:

```text
repo: C:\Users\SooL\Documents\Amneziya
branch: codex/read-only-api-route-shell
remote branch: amn2/codex/read-only-api-route-shell
latest committed head: 2010d60 Add API VPS smoke evidence template
base stable line: d0939d8 Merge pull request #6 from barakov-dot/codex/ssh-host-key-identity-verifier
status: pushed, local worktree clean, full local suite 588 passed with expected StarletteDeprecationWarning, latest real VPS API-only smoke passed run_id=20260603T112418Z
working chat: Переводим AMN на API
```

Изменения в активной API-ветке:

```text
e99d5f3 Fix editable install package discovery
6534ac4 Add read-only API route shell
9cccdc2 Add API token smoke CLI
b37103a Harden local API smoke readiness
2010d60 Add API VPS smoke evidence template
```

API shell открывает только read-only aggregate routes с scoped tokens:

```text
GET /api/servers -> server:read
GET /api/servers/{server_name}/summary -> server:read
GET /api/metrics/summary -> metrics:read
GET /api/users/summary -> metrics:read
```

Запрещено публиковать `.conf`, QR, `vpn://`, private key, PSK, endpoint host/port, SSH host/port, raw token/header/hash или detailed client metadata.

Текущая VPS-gate candidate branch для remote-operation проверки:

```text
branch: codex/remote-operation-vps-gate-prep
head: 7281254 Merge stable API web panel baseline into remote operation gate
base: d0939d8 Merge pull request #6 from barakov-dot/codex/ssh-host-key-identity-verifier
status: pushed to amn2, local tests green, awaits real VPS gate
runbook: research/amn2/vps-gate-remote-operation-dry-run-audit.md
```

Scoped API token storage/auth layer остается важным baseline, но после него в `codex-vps-test-prep` уже вошли route/auth binding, API token lifecycle и SSH host key verifier:

```text
app/services/api_tokens.py
app/db/schema.py
app/db/repositories.py
docs/API_TOKEN_POLICY.ru.md
tests/services/test_api_tokens.py
tests/db/test_repositories.py
```

Смысл: закрепить hash-only scoped API token baseline без `/api/*` routes: one-time raw token issue metadata, scopes `server:read`/`metrics:read`, expiry, revoke, last-used и safe audit metadata.

Проверка: RED `1 import error as expected`, focused security/db/services suite `54 passed`, full local suite `542 passed`, warning только `StarletteDeprecationWarning`.

Дополнительная проверка 2026-06-01: `tests/web/test_config_templates.py tests/web/test_servers.py tests/web/test_users.py -q --basetemp tmp\pytest-web-panel-safe` -> `49 passed, 1 StarletteDeprecationWarning`.

Текущая точка правды AMN3 / lab:

```text
repo: C:\Users\SooL\Documents\VPS-OPS-LAB
branch: master
remote: https://github.com/barakov-dot/amn3.git
package state reviewed in this refresh: master; verify exact current head with git log -1 after package publish
status: synchronize with origin/master after package publish
```

Последние AMN3 pushes, учтенные в координации:

```text
25e02e9 Add VPS install package
87da41d Fix VPS installer user creation fallback
7fc3aee Set KYORESUAS API integration priority
8b4cc81 Refresh project coordination state
2b845cb Make API smoke skip server preflight by default
```

Актуальный install/update package:

```text
dist/amn2-vps-install-294803e.zip
sha256: 9B561FBF9C1ACDE403CFF6DA3A49544074457D3089FF8A8D0859B0CEBBBB1501
dist/amn2-vps-update-and-smoke-kit-294803e.zip
sha256: 702BAD7EBD69F80FC75FD31648383258B6C042BD51B801BC72BE2FD125813CE2
```

Package note: current `7764ae7` update+smoke package includes `amn2_api_loopback_smoke.sh` version `2026-06-04.3`, DB-only server config sync, and 5 read-only API route checks including `/api/integration/status`. Historical `294803e` and `5f12736` packages remain available as evidence baselines.

Соседний AMN3 branch-only push, учтенный как комментарий к pre-VPS координации:

```text
branch: origin/codex/local-agent-production-wiring
head: d5f30c6 Clarify pre-VPS matrix baseline
artifact: docs/AMN3_PRE_VPS_LOCAL_STATUS_MATRIX.ru.md
status: не слито в master; не повторять соседний VPS smoke, использовать только для сверки local-only/pre-VPS boundaries
```

После verified live VPS baseline уже выполнены и записаны в AMN3:

- `d1d9690 Add route auth operation policy matrix`;
- `94ad807 Document secret-bearing delivery artifacts`;
- config delivery integrity local evidence at `94ad807`;
- `dfe27ee Harden public email token safety`;
- remote operation contract / partial-failure / dry-run-audit local-gate evidence;
- `c5d7eb6 Harden Local Agent audit contract`;
- `22dfc37 Clarify web panel operation gates`;
- `1fdcde5 Add scoped API token storage contract`;
- Route/Auth binding tests branch `f9d2c79`, merged through current production line;
- API token lifecycle gate branch `256d0c0`, merged through PR #4/#5;
- SSH host key verifier `dd20364`, merged through PR #6; later read-only API route shell moved current `amn2` head to `5f12736`, then API/web-panel finish moved current head to `294803e`;
- remote operation VPS-gate candidate `7281254`, real VPS Phase 1 read-only/dry-run passed as `dry-run-only-pass`; evidence `research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md`; Phase 2 live single disposable peer apply/revoke passed later on current stable `7764ae7`, evidence `research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md`.
- Current VPS update+smoke package `dist/amn2-vps-update-and-smoke-kit-7764ae7.zip`; historical install/update packages for `294803e` remain available as evidence baselines;
- KYORESUAS API integration priority plan;
- read-only API route shell branch `codex/read-only-api-route-shell`, real VPS loopback API smoke passed through AMN3 operator script `scripts/vps/amn2_api_loopback_smoke.sh`, then fast-forward merged into stable `codex-vps-test-prep` at `5f12736`;
- API/web-panel finish slice branch `codex/api-web-panel-finish`, full local suite `594 passed`, then fast-forward merged into stable `codex-vps-test-prep` at `294803e`; real VPS API/web-panel gate passed 2026-06-04, `run_id=20260604T102355Z`, evidence `research/amn2/api-web-panel-vps-evidence-2026-06-04.md`.

Следующий рабочий выбор:

1. Current production/API-web head is `7764ae7`; `294803e` remains historical API/web-panel gate evidence.
2. Future API expansion requires separate route/secret/remote-write gates.
3. API/web-panel VPS test для `294803e` считать пройденным: loopback API smoke + web route check, без live apply.
4. Controlled real VPS verification gate Phase 2 is now `verified-live` for exactly one disposable test peer on current stable `7764ae7`; routes that call SSH, sync peers, emit config or mutate runtime state still require their own scoped gates.

Старые блоки ниже, где `91aeb3e` указан как latest clean baseline, считать историческим контекстом verified live stage.

## Исторический снимок после verified live VPS cycle

После исходного import-снимка `amn2` прошел первый подтвержденный live VPS cycle. Точка правды на тот момент:

```text
repo: C:\Users\SooL\Documents\Amneziya
branch: codex-vps-test-prep
latest: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
status: clean, synchronized with origin/codex-vps-test-prep
```

Проверено: approve, working config, peer sync, disable/enable и выборочное удаление устройства на Docker AmneziaWG runtime. Более старые блоки ниже, где live retest еще указан как будущая проверка, считать историческим контекстом. Для текущей работы использовать `docs/NEXT_CHAT_AFTER_AMN2_VPS_LIVE.ru.md`, `docs/PROJECT_STATUS_CURRENT.ru.md`, `research/amn2/transfer-backlog.md` и `research/amn2/api-readiness-audit-after-live-baseline.md`.

AMN3 / lab:

```text
repo: C:\Users\SooL\Documents\VPS-OPS-LAB
branch: master
remote: https://github.com/barakov-dot/amn3.git
committed head: a0ccfef Expand secret inventory priority gate
origin/master: 8212281 Document amn2 live migration to lab
status: ahead 2, with local uncommitted status/audit/backlog updates
```

API-readiness audit уже выполнен, а его первый policy slice уже перенесен в `amn2`:

```text
Route/Auth/Operation Policy Matrix for current amn2 surfaces
```

После него API-направление перешло в активную собственную ветку `codex/read-only-api-route-shell`; VPS loopback API smoke passed, без расширения до write/config routes.

## Что было прочитано

Локальные Codex-чаты:

- `MAIN - VPN Ops Lab`: текущий координационный чат.
- `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`: запуск lab, правила main/deep-dive чатов, первые upstream-выводы.
- `VPN Ops Lab - KYORESUAS-API`: анализ `kyoresuas/amnezia-api`, решение не ставить upstream как есть, design spec Local Amnezia Agent.
- `VPS-тест Amneziya`: продолжение live VPS-теста `amn2`.
- `Подготовка запуска на VPS`: первый запуск на живом VPS и handoff в новый чат.
- архивный ранний чат Amneziya: исходные продуктовые решения по боту, VPS, AmneziaWG 2.0, устройствам и срокам.
- task/review-сессии 2026-05-31 по Local Amnezia Agent first slice: Task 1-5, spec compliance review, code quality review и финальный review.
- task/review/worker-сессии 2026-05-31 по Local Agent production wiring: settings, token config builder, runtime adapter, CLI commands, systemd/runbook docs, reviews and PR merge.
- live VPS transition and API-readiness lab сессии после verified `amn2` cycle.

Локальные проекты:

- `C:\Users\SooL\Documents\VPS-OPS-LAB`
- `C:\Users\SooL\Documents\Amneziya`

GitHub:

- Локальный `Amneziya` checkout указывает на `https://github.com/barakov-dot/amn2.git`.
- GitHub connector в этом сеансе вернул `404` на `barakov-dot/amn2`, поэтому текущим источником правды считаются локальный checkout, git metadata и документы в `C:\Users\SooL\Documents\Amneziya`.
- Поиск GitHub по `amneziya` дал нерелевантные одноименные репозитории, их не используем как контекст проекта.

## Главные правила проекта

AMN3 остается coordination/knowledge-направлением.

`amn2` остается production-направлением.

`vpn-ops-lab`/AMN3 остается исследовательской лабораторией, design registry и transfer gate.

Код из внешних проектов не копируем. Идея может перейти из lab в `amn2` только после проверки:

- лицензии;
- практической пользы;
- operational/security рисков;
- архитектурной совместимости;
- тестового плана;
- rollback/recovery модели, если есть state-write или remote operations.

Статусы решений для coordination:

- `переносим в design`;
- `готовим implementation plan`;
- `оставляем в lab`;
- `hybrid-only`;
- `нужен deep dive`;
- `отклоняем`;
- `blocked-by-license`;
- `blocked-by-risk`.

## Текущий `amn2` baseline

Локальная папка:

```text
C:\Users\SooL\Documents\Amneziya
```

Git:

```text
branch: codex-vps-test-prep
origin: https://github.com/barakov-dot/amn2.git
latest commit: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Ветка `codex-vps-test-prep` сейчас синхронизирована с `origin/codex-vps-test-prep`, working tree чистый.

Ключевые новые commits/merges после старого handoff:

- `62ae49e Merge pull request #2 from barakov-dot/codex/config-delivery-artifact-integrity-isolated`
- `286b5cc Merge pull request #3 from barakov-dot/codex/local-agent-production-wiring`
- `9d15cbe Polish VPS admin sync behavior`
- `bfcdd06 Show working server configs`
- `62e8f1c Show approved configs immediately`
- `f72eb25 Clarify VPS approve sync checklist`
- `d6eda20 Document verified VPS live cycle`
- `91aeb3e Document VPS verified tag`

Local Amnezia Agent first slice и production wiring уже находятся в актуальном production baseline: foundation через PR #2, production wiring через PR #3. Не открывать повторный PR для старых Local Agent branches.

Последняя известная локальная проверка `amn2` после verified baseline:

```text
508 passed, 1 warning
```

Предупреждение: `StarletteDeprecationWarning` для `httpx` + `starlette.testclient`.

API-readiness audit focused verification:

```text
tests/agent
tests/config/test_settings.py
tests/server/test_operation_runner.py
tests/server/test_checks.py
tests/web/test_cli_web.py

109 passed, 1 warning
```

Предупреждение то же: `StarletteDeprecationWarning` из `.codex_deps`. В одном запуске после успешного pytest был ignored Windows temp cleanup `PermissionError`; exit code был 0.

## Продуктовые решения Amneziya / `amn2`

Первый контур:

- собственный VPS;
- Debian;
- AmneziaWG 2.0;
- Telegram-бот отдельно от VPN-сервера;
- один VPN-сервер в MVP, но архитектура должна поддержать несколько серверов позже;
- бесплатный тестовый режим с ручным подтверждением администратором;
- платежный слой позже, через абстракцию;
- один пользователь может иметь несколько устройств;
- каждое устройство имеет отдельный peer, IP, ключи и срок;
- лимит MVP: до 5 устройств на пользователя;
- сроки доступа: 3, 7, 10, 14, 30, 60, 90, 180 дней и произвольный срок;
- уведомления до окончания: 7, 5, 3, 1 день.

Runtime-решение из ранних документов: предпочтительный MVP-path был `systemd` + `awg/awg-quick` на Debian host без Docker. Но текущий live VPS фактически работает через Docker runtime Amnezia:

- container: `amnezia-awg2`;
- persistent config: `/opt/amnezia/awg/awg0.conf`;
- live network: `10.8.1.0/24`.

Это значит, что текущая практика `amn2` должна учитывать оба runtime: желаемый host/systemd и реально тестируемый Docker backend.

## Текущее состояние функций `amn2`

Уже реализованы и зафиксированы в handoff:

- Telegram bot и web admin panel;
- web panel на порту `3030`;
- пользователи, серверы, заявки, логи, настройки;
- config templates и `vpn://` preview;
- server health и VPS readiness;
- peer sync в карточке сервера;
- peer, созданные в приложении Amnezia, можно помечать как `Созданы в Amnezia`;
- локальные устройства без peer можно добавлять в Amnezia;
- выборочное удаление устройства у пользователя;
- `Disable VPN` удаляет peer из AmneziaWG, но оставляет устройство `disabled` в базе;
- `Enable VPN` возвращает `disabled` peer с тем же IP/public key/PSK;
- private key и PSK хранятся encrypted и показываются только через `Show secrets` с audit;
- опасные web-действия требуют browser confirm;
- failed VPS operations пишутся в `admin_actions` с redacted error;
- email config/recovery теперь всегда требуют подтвержденный `email_verified_at`.
- добавлен `VPS retest bundle`: CLI-команда `python -m app.cli server retest-plan ...` и блок `VPS retest bundle` в карточке сервера с командами повторной проверки;
- добавлены настраиваемые defaults клиентского AmneziaWG-конфига через `.env`: `CLIENT_DNS`, `CLIENT_ALLOWED_IPS`, `CLIENT_PERSISTENT_KEEPALIVE`, `CLIENT_AWG_JC`, `CLIENT_AWG_JMIN`, `CLIENT_AWG_JMAX`, `CLIENT_AWG_S1`, `CLIENT_AWG_S2`, `CLIENT_AWG_H1`...`CLIENT_AWG_H4`.

Verified live VPS cycle уже подтвердил:

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

Новый live retest нужен только если меняется apply/revoke/config/sync логика, IP allocation, peer classification, disable/enable/delete или Docker runtime write/restart behavior.

## `amn2` inventories в lab

В `research/amn2/` уже есть read-only inventories:

- auth/security;
- route/auth surface;
- secret surface;
- config delivery;
- remote operations;
- decision log.

Ключевое решение: web-admin 2FA поставлена на паузу 2026-05-30. Сейчас не пишем implementation plan для 2FA и не меняем production-код под TOTP/MFA. Следующий фокус: route/config delivery policy, remote operations, secret handling.

## Upstream deep dives

### PRVTPRO/Amnezia-Web-Panel

License verdict: GPL-3.0, только `research-only` / самостоятельное проектирование идей.

Полезные сигналы:

- API tokens;
- self-service endpoints;
- public sharing;
- OpenAPI/taxonomy по доменам;
- route policy matrix;
- safe SSH/sudo policy;
- RemoteOperationRunner;
- command execution contract;
- dry-run-first operations;
- audit events;
- host key enrollment;
- manager interface checklist.

Для hybrid:

- attach existing server;
- multi-protocol dashboard;
- manager architecture per protocol;
- Telegram integration;
- sensitive config delivery;
- operator backup/restore;
- protocol capability registry;
- plugin-like protocol managers;
- existing server reconciliation;
- background remote jobs.

Нельзя переносить как код: route layout, manager scripts, Dockerfile, config templates, UI.

### wg-easy/wg-easy

License verdict: AGPL-3.0-only, только самостоятельная реализация идей.

Полезные сигналы:

- focused WireGuard-first UX;
- public-safe client read models;
- client expiration;
- metrics surface;
- metrics privacy policy;
- scoped metrics token;
- permission wrapper with required resource check;
- forced setup/bootstrap flow;
- operational docs and migration guide;
- migration/import wizard.

Ограничения: ideas only; не копировать код, UI, API implementation или docs.

### kyoresuas/amnezia-api

License verdict: MIT, но для `amn2` все равно `idea-only`.

Primary verdict:

- для `amn2`: `high-signal design candidate`, не источник кода;
- для hybrid: `strong architecture reference`;
- как готовую установку на production Amnezia прямо сейчас не берем;
- upstream не копируем, потому что важнее собственный безопасный contract.

Полезная идея: Local Amnezia API agent рядом с Amnezia runtime вместо постоянного внешнего SSH control plane.

Главные риски upstream:

- Docker socket почти равен host compromise;
- один `x-api-key` без scopes;
- `/docs` и `/metrics` выглядят публичными относительно auth middleware;
- backup содержит secret-bearing state;
- import/reboot/delete destructive без отдельной policy;
- нет явного audit и dry-run/preview;
- shell execution через `child_process.exec` без выделенного command allowlist/redaction layer;
- нет полноценного тестового контура кроме CI lint/build.

## Текущая design queue для `amn2`

Актуальная design queue после verified baseline:

- `codex/read-only-api-route-shell`: merged API branch, head `5f12736`, real VPS loopback smoke passed через AMN3 operator script.
- `codex/remote-operation-vps-gate-prep`: отдельный controlled VPS gate для SSH/sync/config/runtime write surfaces.
- `Route/Auth Binding`, `Scoped API Token Lifecycle`, `Secret Inventory`, `Public Config Policy`, `Backup/Import Policy`: обязательные baselines перед дальнейшим route expansion.
- `/clients` write CRUD, API `config:read`, public config delivery, backup/import/reboot и public docs/metrics остаются заблокированы до отдельного решения.
- `Domain Zone Exclusion Policy` и 2FA отложены до закрытия текущих API/VPS safety gates.
- `Config delivery policy table`: actor, gate, risk class, output, audit, tests.

Пауза:

- `Web-admin 2FA`.

## Local Amnezia Agent: текущее решение

Решения из design spec:

- не устанавливаем `kyoresuas/amnezia-api` как есть;
- не копируем upstream-код;
- agent = привилегированный runtime adapter, а не публичная admin API;
- стартуем read-only;
- backup/import/reboot откладываем;
- route policy обязательна до реализации;
- secret inventory обязательна до config delivery.

First safe slice по design spec:

- package `app/agent`;
- route policy matrix;
- hash-only scoped bearer tokens;
- fake runtime adapter;
- FastAPI app factory;
- endpoints: `/agent/health`, `/agent/version`, `/agent/runtime`, `/agent/protocols`;
- public docs/openapi disabled for agent app;
- audit events for read routes;
- tests for policy/auth/runtime/API;
- no configs, QR, `vpn://`, backup, import, reboot, Docker mutation or write operations.

Текущее фактическое состояние Local Agent в `Amneziya`:

- first slice foundation merged into `codex-vps-test-prep` via PR #2;
- production wiring merged via PR #3;
- included in baseline `91aeb3e`;
- disabled by default;
- default bind `127.0.0.1`;
- hash-only token settings and CLI helper;
- read-only runtime/protocol endpoints;
- LocalCommandRuntimeAdapter for read-only runtime detection;
- example systemd unit and VPS smoke runbook were created in the production-wiring workstream.

Историческая review-заметка про brittle 401/403 text matching закрыта typed local agent auth errors.

Открытые вопросы перед расширением Local Agent:

- какой runtime state безопасно читать без Docker socket;
- как минимально детектить AmneziaWG, AmneziaWG 2.0 и Xray.
- как унифицировать audit sink с production admin actions;
- как описать clients/configs/backup/reboot как blocked routes до policy gates.

## Очередь hybrid

Кандидаты для будущего hybrid:

- per-server API agent;
- multi-server balancing metadata;
- unified protocol adapter contract;
- attach existing server / reconciliation;
- multi-protocol dashboard;
- protocol capability registry;
- plugin-like protocol managers;
- domain-aware split routing;
- background remote jobs;
- migration/import wizard;
- operational docs system;
- observability baseline;
- account security baseline.

## Очередь общего Codex skill

Нужно усилить skill анализа VPN/control-panel upstream:

- license verdict first;
- отделять `architecture idea` от `code implementation`;
- для GPL/AGPL по умолчанию `research-only`;
- проверять auth methods, route guards, roles, ownership checks;
- классифицировать endpoints как `read-only`, `secret-read`, `state-write`, `remote-exec`, `destructive`;
- проверять Docker socket, sudo, systemd, host filesystem, VPN config paths;
- защищены ли `/docs`, `/metrics`, `/health`, backup/import;
- есть ли scoped tokens, expiry, revoke, rotation, audit, rate limit;
- считать `.conf`, QR и `vpn://` secret-bearing;
- проверять redacted backup, dry-run/preview, recovery note;
- искать secret leakage в logs/errors/metrics;
- проверять lock/queue для concurrent config writes;
- требовать staging/runtime tests, а не только lint/build.

## Ближайшие рабочие развилки

Текущий режим coordination: AMN3 принял состояние после live VPS stage, local-only transfer slices, VPS install package и активной read-only API ветки.

1. Current production/API-web head is `7764ae7`; `294803e` remains historical API/web-panel gate evidence.
2. Remote-operation VPS gate branch уже обновлена поверх `294803e`: `codex/remote-operation-vps-gate-prep` at `7281254`.
3. Для новых API routes начинать с отдельного route/secret/remote-write gate, не с копирования upstream code.
4. Controlled real VPS verification gate для `codex/remote-operation-vps-gate-prep` держать отдельным gate для SSH/sync/config/runtime-changing routes.
5. Для coordination-чата держать правило: любая новая идея сначала попадает в очередь с verdict, а не сразу в implementation.
6. Latest AMN2 local/integration head is `de25576` after `P5-X001` Russian-first microtexts polish; CPython 3.12.x remains the supported local runtime, Python 3.14 remains a separate future upgrade gate.

## Источники в workspace

VPN Ops Lab:

- `README.md`
- `ideas/candidates-for-amn2.md`
- `ideas/candidates-for-hybrid.md`
- `ideas/add-to-skill.md`
- `research/amn2/README.md`
- `research/amn2/decisions.md`
- `research/upstreams/kyoresuas-amnezia-api.md`
- `docs/superpowers/specs/2026-05-31-local-amnezia-agent-design.md`
- `docs/superpowers/plans/2026-05-31-local-amnezia-agent-first-slice.md`
- `docs/superpowers/specs/2026-05-30-design-specs-index-amn2-transfer-checklist.md`

Amneziya / `amn2`:

- `docs/NEXT_CHAT_HANDOFF.ru.md`
- `docs/DECISIONS.ru.md`
- `docs/WEB_PANEL_AND_BOT_SETUP.ru.md`
- `docs/VPS_RETEST_PROTOCOL.ru.md`
- `docs/VPS_LOG_COLLECTION.ru.md`
- `docs/PRODUCTION_VPS_CHECKLIST.ru.md`
- `docs/SERVER_CONFIG_TEMPLATE.ru.md`
- `docs/RUNTIME_REGISTRY.ru.md`
- `docs/RUNTIME_TOOLCHAIN.ru.md`
