# Следующий чат: AMN2 after Phase 6

Дата: 2026-06-14.

Статус: superseded by Phase 7 transition packet.

Для нового рабочего чата использовать:

```text
docs/NEXT_CHAT_AMN2_PHASE_7_RELEASE_CANDIDATE.ru.md
docs/PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md
research/amn2/phase-7-transition-packet-2026-06-14.md
```

Phase 7 name/status: `Release Candidate Readiness / Clean Installer RC`,
`pre-release / release-candidate readiness`. Default lane remains
local-only/docs/tests/security/package-preflight. Public launch, config
delivery, write API, live VPS/package apply, destructive installer execution
and Telegram identity mutations remain gated/deferred.

Рабочая папка:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

## Source Of Truth

```text
AMN3 repo: barakov-dot/amn3
AMN3 branch: master
AMN3 checkpoint: verify with git log -1; latest completed slice is Phase 6 final closeout

AMN2 repo: barakov-dot/amn2
AMN2 branch: codex-vps-test-prep
AMN2 current head: b121865 Add multi instance conflict model
AMN2 latest VPS-smoked head: 0de7a77 Polish fresh installer preflight planning
AMN2 latest package-ready head: 0de7a77 Polish fresh installer preflight planning
AMN2 package status: VPS-smoked/pass for 0de7a77
AMN2 smoke status: live-update-smoke-pass for 0de7a77
```

## Read First

```text
docs/NEXT_CHAT_AMN2_AFTER_PHASE_6.ru.md
docs/NEXT_CHAT_AMN2_PHASE_6_PRODUCTIZATION.ru.md
docs/PHASE_5_6_FORWARD_PLAN.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
research/amn2/transfer-backlog.md
docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md
research/amn2/phase-6-closeout-next-chat-fresh-installer-backlog-2026-06-13.md
research/amn2/after-phase-6-fresh-installer-plan-renderer-2026-06-13.md
research/amn2/after-phase-6-fresh-installer-readiness-planning-2026-06-13.md
research/amn2/after-phase-6-fresh-installer-evidence-readiness-2026-06-13.md
research/amn2/after-phase-6-public-config-gate-checklist-refresh-2026-06-13.md
research/amn2/after-phase-6-fresh-installer-copy-package-preflight-2026-06-14.md
research/amn2/after-phase-6-package-preflight-0de7a77-2026-06-14.md
research/amn2/after-phase-6-next-chat-live-gate-checklist-0de7a77-2026-06-14.md
research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md
research/amn2/after-phase-6-automation-intake-aggregation-closeout-readiness-2026-06-14.md
research/amn2/after-phase-6-installer-preflight-taxonomy-guards-2026-06-14.md
research/amn2/after-phase-6-multi-instance-ipam-conflict-model-2026-06-14.md
research/amn2/phase-6-final-closeout-known-good-snapshot-2026-06-14.md
research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-14.md
research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-14.md
research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-14.md
research/amn2/phase-6-live-update-smoke-c46f664-2026-06-13.md
research/amn2/phase-6-package-runbook-escaping-hygiene-2026-06-13.md
```

## Current Decision

```text
decision: Phase 6 default lane closed
current_mode: private/operator-only
public_self_service_launch: not opened
latest_vps_smoked_head: 0de7a77
latest_package_ready_head: 0de7a77
current_amn2_head: b121865 local-only not package-rebuilt or VPS-smoked
default_local_queue: empty
next_recommendation: Phase 6 final closeout + clean-installer next-phase entry + current VPS known-good snapshot/runbook
```

Phase 6 final closeout is completed. The default local queue is empty. The next
chat should either pause on known-good `0de7a77` or ask the operator for a
separate named gate before any live/public/config/write/destructive work.
Evidence:
`research/amn2/phase-6-final-closeout-known-good-snapshot-2026-06-14.md`.

Phase 6 produced planning/security/productization boundaries and confirmed the
current disposable VPS source overlay at `0de7a77` through read-only loopback
smoke. It did not open public launch, config delivery, write API, destructive
rebuild, backup/import/reboot, Local Agent mutations, production peer/user
mutation or Telegram identity mutation.

After that, `P6-C010` live update/smoke for `0de7a77` was completed on the
disposable VPS `89.185.80.166`. The prepared package was uploaded,
checksum-verified and extracted; source overlay updated `/opt/amn2` to
`0de7a77f3eb09d23dc2785d402bc51c2b5eb7835`; the manual web/bot runtime was
minimally restarted; read-only API smoke on temporary loopback `127.0.0.1:3040`
passed with run_id `20260614T063327Z`; final external probes returned `000`.
Evidence:
`research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md`.

After the weekly automation windows, automation intake aggregation was
completed as AMN3 local-only/docs-only work. PRVTPRO heartbeat output was
available and normalized. KYORESUAS and Amnezia final automation reports were
not visible in the current AMN2 thread or local AMN3 evidence, so they are
marked `missing-input` and supplemented only with direct public GitHub metadata
refresh. New non-live candidates are `FI-M004` package asset path preflight,
`P6-M005` multi-instance/port/IPAM conflict model and `P6-N005`
OpenAPI/taxonomy route-order drift guard. AmneziaWG Android `2.0.1` is
watch-only. Evidence:
`research/amn2/after-phase-6-automation-intake-aggregation-closeout-readiness-2026-06-14.md`.

After that, `FI-M004 + P6-N005` were completed in AMN2 commit `4cde273 Add
installer preflight taxonomy guards` as local-only code/tests/docs. This added
fresh-installer package asset path preflight, rendered
`package-asset-path-preflight` phase and a public docs/API route-order drift
guard. Full AMN2 suite returned `723 passed, 1 StarletteDeprecationWarning`.
This head is not package-rebuilt or VPS-smoked; latest VPS-smoked/package head
remains `0de7a77`. Evidence:
`research/amn2/after-phase-6-installer-preflight-taxonomy-guards-2026-06-14.md`.

After that, `P6-M005` was completed in AMN2 commit `b121865 Add multi instance
conflict model` as local-only code/tests/docs. This added
`capability_registry.multi_instance_conflict_model` and
`docs/MULTI_INSTANCE_IPAM_CONFLICT_MODEL.ru.md`; live multi-instance apply,
runtime config write, firewall change, peer migration, config delivery and
service restart remain blocked. Full AMN2 suite returned `724 passed, 1
StarletteDeprecationWarning`. This head is not package-rebuilt or VPS-smoked;
latest VPS-smoked/package head remains `0de7a77`. Evidence:
`research/amn2/after-phase-6-multi-instance-ipam-conflict-model-2026-06-14.md`.

After Phase 6, `FI-I001 + FI-I002 + FI-I003` were completed in AMN2 commit
`de635a0 Add fresh installer plan renderer` as local-only code/tests/docs. This
added versioned installer question/answer schemas, a rendered plan, secret
handoff protocol binding and the canonical `scripts/test.ps1` Windows/Codex
test wrapper. This head is not package-rebuilt or VPS-smoked.

After that, `FI-M001 + FI-M002 + FI-M003` were completed in AMN2 commit
`7416fb0 Add fresh installer readiness planning` as local-only code/tests/docs.
This added `fresh-install-readiness.v1`, target preflight matrix, runtime mode
decision and package hygiene checklist. This head is not package-rebuilt or
VPS-smoked.

After that, `FI-N001 + FI-N002 + FI-S001` were completed in AMN2 commit
`525a9cd Add fresh installer evidence readiness` as local-only code/tests/docs.
This added smoke/evidence template, report-only existing-server reconciliation
input and `docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md`. This head is not
package-rebuilt or VPS-smoked.

After that, `P6-C001 + P6-C002` docs-only checklist refresh was completed in
AMN2 commit `ff77d4c Add public config gate checklist` as local-only
code/tests/docs. This added `docs/PUBLIC_CONFIG_GATE_CHECKLIST.ru.md` and a
machine-checkable checklist artifact that keeps public exposure and config
delivery disabled unless separate named gates are opened. This head is not
package-rebuilt or VPS-smoked.

After that, `FI-X001 + current-head package preflight planning` was completed
in AMN2 commit `0de7a77 Polish fresh installer preflight planning` as local-only
code/tests/docs. This switched the fresh installer prompts to Russian-first copy
while preserving stable technical IDs, and added
`fresh-install-package-preflight.v1` planning for `ff77d4c` without package
build, live apply or live smoke. This head is not package-rebuilt or VPS-smoked.

After that, local package build/preflight for `0de7a77` was completed as AMN3
local package work. It produced `dist/amn2-vps-update-and-smoke-kit-0de7a77.zip`
and `dist/amn2-codex-vps-test-prep-0de7a77-source.zip`, with package hygiene
and test-extract passing. This did not run live apply/smoke. Latest VPS-smoked
head remains `c46f664`.

After that, next-chat handoff refresh + live gate checklist grooming for
`0de7a77` was completed as AMN3 docs-only/local-only work. It records the exact
future live gate phrase, package/source checksums, stop criteria and forbidden
surfaces for a possible `P6-C010` live apply/smoke gate. It does not open the
gate and does not run live apply/smoke.

## Safety Boundary

Allowed by default:

- AMN3 docs/status/backlog/handoff updates;
- AMN2 local-only code/tests/docs/templates;
- local fake-runner contracts;
- security review and policy work;
- package planning and local hygiene checks without altering sealed evidence
  packages.

Not allowed without separate named gate:

- live VPS commands or SSH;
- package upload/apply on VPS;
- service restart/deploy;
- public API `3040`, direct public web/admin `3030`, domain/HTTPS/reverse
  proxy/firewall changes;
- config delivery, `.conf`, QR, `vpn://`;
- `/api/clients` write CRUD;
- Local Agent mutations;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use, live bot send or profile/identity mutation;
- upstream/GPL implementation copy.

Keep `VPS_APPLY_ENABLED=false` unless a future named gate explicitly changes it.

## Remaining Plan

### Critical gated/deferred

- `P6-C001` Public exposure gate.
- `P6-C002` Config delivery gate.
- `P6-C003` Write API production gate.
- `P6-C004` Production backup/restore/import gate.
- `P6-C007` Destructive cleanup/reinstall gate.
- `VPS-REBUILD-001`, carried from earlier phases, gated/deferred.
- Local Agent write/config routes.
- Production peer/user mutation.

### Normal gated/deferred

- `P4-PRVTPRO-REFRESH-003-LIVE`, carried from Phase 4, live probes/actions
  still gated.

### Fresh installer candidates

Use `docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md`. Candidates are not active by
default. Completed after Phase 6:

```text
FI-I001 Installer question model hardening
FI-I002 Install plan renderer
FI-I003 Secret handoff checklist binding
FI-M001 Target OS/runtime preflight matrix
FI-M002 Runtime mode decision
FI-M003 Package hygiene integration
FI-N001 Smoke/evidence template
FI-N002 Existing-server reconciliation input
FI-S001 Installer docs index
P6-C001 + P6-C002 docs-only checklist refresh
FI-X001 Russian-first prompt copy polish
current-head package preflight planning for ff77d4c
local package build/preflight for 0de7a77
next-chat handoff refresh + live gate checklist grooming for 0de7a77
```

The remaining clean-installer lane is empty by default. Future package/live work
requires a separate package or live gate decision.

## Suggested Next Steps

Recommended default:

```text
Pause here. 0de7a77 is already VPS-smoked/pass on the disposable VPS.
```

Future work requires a new named gate if it touches live/public/config/write or
destructive surfaces.

```text
Possible future lanes: public/config checklist gate, destructive clean-install
gate, or a new local-only installer hardening slice.
```

## P6-C010 Live Gate Checklist

Gate status:

```text
P6-C010 live apply/smoke gate: closed as live-update-smoke-pass
target: 89.185.80.166 disposable VPS
candidate package: dist/amn2-vps-update-and-smoke-kit-0de7a77.zip
candidate package sha256: 7B6DA000DAA39DD15A4DB7C3691D0B0C24EAA20ACB1C428150C6961B01E6F85B
candidate source zip sha256: B8D0E7E2A40051AB38EDF09947977DFE5F7197CEEEE87D1523734D3C1C505295
current latest VPS-smoked head: c46f664
```

Before any live action, confirm:

- exact operator phrase names `P6-C010`, commit `0de7a77`, and target
  `89.185.80.166`;
- AMN3 head and AMN2 head are checked locally;
- package checksum and source checksum match the values above;
- target is still disposable and intended for this update;
- smoke remains loopback-only with `VPS_APPLY_ENABLED=false`;
- no public exposure/config delivery/write API/Local Agent mutation/backup or
  destructive work is being opened.

Stop if any of these occur:

- package checksum mismatch;
- package extract missing one of the five expected files;
- source overlay apply failure;
- web/bot runtime cannot be verified inside the named gate;
- listener drift exposes `3030`, `3040`, `80` or `443` unexpectedly;
- loopback API smoke fails auth/listener/audit checks;
- any secret-bearing material appears in evidence.

Do not run live/destructive work unless the operator gives a separate exact
named gate phrase.
