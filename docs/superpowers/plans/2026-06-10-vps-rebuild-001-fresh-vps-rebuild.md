# VPS-REBUILD-001 Fresh VPS Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to execute this plan if and only if the operator later grants final destructive approval.

**Goal:** Prepare a separate destructive named gate for a possible fresh VPS reinstall/rebuild while preserving the current safety boundary: no live action, no wipe, no public exposure, no config delivery, no write API and no secret publication before final approval.

**Architecture:** AMN3 stays the coordination/evidence repository. AMN2 remains the implementation/runtime source. `VPS-REBUILD-001` is an outer operations gate that can later authorize a controlled rebuild only after explicit retention, source, secret-transfer and final destructive decisions.

**Tech Stack:** Markdown evidence and planning docs in AMN3; future live execution, if approved, must use safe summary outputs only and must not store target secrets or target IP/host in repo artifacts.

---

## Current Status

```text
gate_id: VPS-REBUILD-001
gate_status: opened-defer-awaiting-final-destructive-approval
source_baseline: NG-V001 closed-go
preflight_mode: novice-safe snapshot-first
destructive_action_authorized: no
reinstall_authorized: no
live_commands_run: no
```

Latest source/package precheck evidence:

```text
research/amn2/vps-rebuild-001-source-package-precheck-2026-06-10.md
source_precheck_status: passed
AMN2_source_commit: 1508e3c4a100b76815b29f91757290f1266f813d
focused_local_tests: 30 passed, 1 warning
package_precheck_status: blocked_until_1508e3c_package_build
```

## Phase 1: Open Docs-Only Gate

- [x] Create `research/amn2/vps-rebuild-001-fresh-vps-rebuild-gate-2026-06-10.md`.
- [x] Record the operation class as `destructive + remote-exec + secret-read + state-write`.
- [x] Record `security_risk_decision: defer` and `go_no_go_decision: defer`.
- [x] Record that no live commands, SSH commands, package apply, restart, public exposure, config delivery, write API or production mutation is authorized.
- [x] Add the required final destructive approval phrase.

## Phase 2: Synchronize Coordination Docs

- [x] Update the current status document with the opened gate.
- [x] Update transfer backlog with the opened gate.
- [x] Update next-chat handoff with the active destructive gate plan.
- [x] Update context import with the new gate evidence.
- [x] Update candidate registry and Phase 4 handoff next decision wording.
- [x] Update the P4-NG charter to point to the new destructive gate as a separate stage, not as remaining P4-NG work.

## Phase 3: Required Decisions Before Any Live Action

- [x] Choose `data_retention_decision`:
  - `wipe_all_allowed`;
  - `preserve_snapshot_required`;
  - `export_safe_summary_only`.
- [x] Choose `snapshot_or_backup_decision`:
  - `not_required_by_operator`;
  - `provider_snapshot_required`;
  - `encrypted_backup_required`;
  - `safe_summary_only`.
- [x] Choose exact AMN2 source commit after local source precheck.
- [ ] Build and verify install/update package for `1508e3c`.
- [x] Choose secret transfer policy:
  - `operator_local_channel_only`;
  - `regenerate_on_target`;
  - `restore_from_approved_secret_store`.
- [ ] Confirm stop criteria and post-install acceptance checklist.
- [ ] Send the exact final destructive phrase:

```text
GO VPS-REBUILD-001 WIPE TARGET
```

Selected novice-safe values:

```text
data_retention_decision: preserve_snapshot_required
snapshot_or_backup_decision: provider_snapshot_required
secret_transfer_policy: regenerate_on_target_where_possible + operator_local_channel_only_for_external_secrets
install_source_commit_selected: 1508e3c4a100b76815b29f91757290f1266f813d
install_package: pending-build-and-hygiene
final_destructive_phrase: not_sent
```

## Phase 4: Blocked Until Final Destructive Approval

Do not execute this phase until every Phase 3 decision is filled and the exact final destructive phrase is received.

- [ ] Reconfirm target identity through an out-of-repo operator channel.
- [ ] Run approved pre-rebuild safe summary check, if selected.
- [ ] Execute the selected reinstall/rebuild path.
- [ ] Install only the approved AMN2 source/package.
- [ ] Restore/regenerate secrets according to the approved secret transfer policy.
- [ ] Keep web/admin loopback-only on `127.0.0.1:3030`.
- [ ] Keep public API `3040` absent/closed.
- [ ] Keep TCP `80/443` absent unless a separate public gate exists.
- [ ] Keep `VPS_APPLY_ENABLED=false`.

## Phase 5: Post-Install Acceptance Evidence

- [ ] Record only safe summary fields.
- [ ] Confirm SSH transport ok.
- [ ] Confirm `amneziya-web` active/enabled.
- [ ] Confirm `amneziya-bot` active/enabled.
- [ ] Confirm loopback `/login` HTTP `200`.
- [ ] Confirm listener `3030` loopback-only.
- [ ] Confirm public API `3040` absent/closed.
- [ ] Confirm TCP `80/443` absent unless a separate public gate changed this.
- [ ] Confirm no config delivery, write API route opening, production peer/user mutation or secret publication occurred.
- [ ] Close the gate as `go`, `no-go` or `defer` and remove it from the active plan only when closed.

## Active Remaining Plan

### Критичные

- `VPS-REBUILD-001`: fresh VPS rebuild gate, `opened-defer-awaiting-final-destructive-approval`; next required: build and verify `1508e3c` package locally, then provider snapshot confirmation.

### Очень Важные

- None.

### Важные

- None.

### Нормальные

- None.

### Простые

- None.

### Косметические

- None.

## Recommendation

Next step is not a live VPS command. Build and verify the `1508e3c` package locally, including checksum, hygiene and test extraction. Only after package evidence and provider snapshot confirmation are reviewed should the operator decide whether to send the exact final destructive phrase.
