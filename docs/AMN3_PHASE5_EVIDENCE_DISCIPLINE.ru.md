# AMN3 Phase 5 Evidence Discipline

Дата: 2026-06-11.

Назначение: зафиксировать обязательный AMN3 closeout packet для Phase 5 Operator-Only Pilot. Каждый local/docs/test/checklist slice, named gate, operator evidence intake or future live pilot step должен оставлять проверяемый след: evidence file, status/backlog sync, active-plan cleanup and next recommendation.

Этот документ не открывает live VPS commands, SSH commands, deploy/restart/package apply, public exposure, config delivery, write API, Local Agent mutations, backup/import/reboot, production peer/user mutation or destructive VPS actions. Он описывает только дисциплину доказательств и синхронизации.

## Scope Classes

```text
docs_only: AMN3 docs/status/backlog/handoff/candidate updates only
local_only_amn2: AMN2 code/tests/docs/templates without live VPS or secret output
operator_evidence_intake: operator supplies safe summaries or redacted observations
named_gate_preflight: explicit gate design/approval/evidence before any live target check
named_gate_result: completed gate with go/no-go/defer result
blocked_or_deferred: task cannot proceed without separate gate or operator decision
```

Every evidence file must name its scope class. If the scope class is unclear, use `blocked_or_deferred` and do not proceed.

## Required Closeout Packet

Before marking any Phase 5 task closed, all applicable items must be true:

- one evidence file exists under `research/amn2/`;
- `docs/PROJECT_STATUS_CURRENT.ru.md` records the result near the top;
- `research/amn2/transfer-backlog.md` records the result if it affects active AMN2/Phase 5 direction;
- `docs/PHASE_5_6_FORWARD_PLAN.ru.md` removes the task from the active plan and moves it to closed work;
- `docs/NEXT_CHAT_AMN2_PHASE_5_OPERATOR_PILOT.ru.md` removes the task from the active plan and updates the next recommendation;
- `docs/PROJECT_CONTEXT_IMPORT.ru.md` records the latest summary if the next chat needs it;
- related idea/candidate docs are updated only when they contain stale next-step wording;
- verification commands are listed with actual result, or explicitly marked `not_run` with reason;
- no secret-bearing evidence is pasted into AMN3, GitHub or chat;
- the next recommendation is a still-open item.

If any required file is intentionally not touched, the evidence file must say why.

## Evidence File Naming

Use stable, searchable names:

```text
research/amn2/phase-5-<task-slug>-YYYY-MM-DD.md
research/amn2/<named-gate-id>-<short-slug>-YYYY-MM-DD.md
research/upstreams/<upstream-slug>-refresh-YYYY-MM-DD.md
```

Examples:

```text
research/amn2/phase-5-operator-only-smoke-checklist-2026-06-11.md
research/amn2/phase-5-amn3-evidence-discipline-2026-06-11.md
research/amn2/p5-c003-live-rollout-named-gate-YYYY-MM-DD.md
```

## Evidence File Minimum Fields

Each Phase 5 evidence file should include:

```text
task_id:
task_name:
date:
scope_class:
source_of_truth:
changed_files:
verification:
safety_boundary:
blocked_actions:
secrets_policy:
active_plan_update:
next_recommendation:
```

For AMN2 local-only implementation slices, add:

```text
AMN2 branch:
AMN2 commit:
tests_red:
tests_green:
full_suite:
git_checks:
push_status:
live_vps_touched: no
```

For AMN3 docs-only slices, add:

```text
AMN3 commit:
docs_updated:
tests_not_run_reason:
git_checks:
push_status:
```

For named gates, add:

```text
gate_name:
operator_approval:
allowed_actions:
go_no_go_decision: go | no-go | defer
safe_summary_fields:
stop_conditions:
```

## Secret And Output Policy

Never store or paste:

```text
.env values or raw .env
raw servers.yml
raw tokens
Authorization headers
token hashes
web password hash
session secret
private keys
PSK
peer public keys
client .conf
QR payloads or QR images
vpn:// links
backup contents
public endpoint values
session cookies
full logs
secret-bearing command output
```

Allowed evidence form is safe summary only:

```text
present
absent
passed
failed
not_checked
redacted
count_only
loopback_only
closed
deferred
```

If operator-provided output contains forbidden fields, do not quote it. Convert it to a safe summary and record `raw_output_not_stored: yes`.

## Active Plan Rules

After every closed task:

- remove the task from active Phase 5 plan sections;
- keep it in closed/history sections with evidence link;
- keep carried-from-Phase-4 labels for inherited gated items;
- do not remove a gated item merely because a checklist or design exists;
- keep `VPS-REBUILD-001` as `defer` until retention path, stop criteria and exact final destructive phrase are accepted;
- keep `P5-C001`/`P5-C002`/`P5-C003`/`P5-C004` active until their named gate or decision is actually closed;
- update the next recommendation to an open, safe item.

## Verification Rules

For docs-only slices, minimum verification:

```text
git diff --check
git diff --cached --check before commit
rg stale task id / next recommendation scan
git status --short --branch
```

For AMN2 local-only code/tests slices, minimum verification:

```text
focused RED result
focused GREEN result
related regression tests
full suite if blast radius justifies it
git diff --check
git diff --cached --check before commit
```

For named gates, verification must match the approved gate and must not expand by convenience.

## Stop Conditions

Stop and record `decision: defer` or `no-go` if:

- the task needs live VPS commands without a named gate;
- approval is ambiguous;
- safe evidence cannot be produced without secrets;
- the next required action would publish config, QR, `vpn://`, keys, tokens or full logs;
- a plan tries to treat historical VPS-smoked evidence as permission for new writes;
- a completed checklist is being used as authorization for deploy/restart/package apply/public exposure/write/config/destructive action.

## Closeout Template

```text
task_id:
scope_class:
result:
evidence_file:
docs_updated:
verification:
tests_not_run_reason:
safety:
active_plan_removed:
remaining_active_plan:
next_recommendation:
commit:
push_status:
```

This template belongs in the final evidence file and can be summarized in chat after verification.
