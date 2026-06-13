# Project Operating System Template

Назначение: чистый каркас проектной памяти для нового проекта. Заполнять в
первый день проекта и обновлять после каждого закрытого slice.

## Источник правды

```text
Project name:
Working folder:
Primary repo:
Primary branch:
Secondary repos:
Current checkpoint:
Latest deployed/smoked checkpoint:
Package/release status:
```

## Цель проекта

- Product goal:
- Primary users/operators:
- Non-goals:
- Success criteria:

## Safety Boundaries

Allowed by default:

- local-only code/docs/tests;
- read-only inspection;
- fake-runner/dry-run contracts;
- security review and threat modeling;
- status/backlog/handoff updates.

Not allowed without a named gate:

- live infrastructure commands;
- deploy/restart/package apply;
- public exposure;
- secret/config delivery;
- write API or production data mutation;
- backup/restore/import apply;
- destructive provider/resource actions;
- identity/token mutations;
- copying code with incompatible license constraints.

## Active Plan

Use this priority scale in every status document:

### Критичные

- `ID` Task title. Importance/gate:

### Очень важные

- `ID` Task title. Importance/gate:

### Важные

- `ID` Task title. Importance/gate:

### Нормальные

- `ID` Task title. Importance/gate:

### Простые

- `ID` Task title. Importance/gate:

### Косметические

- `ID` Task title. Importance/gate:

## Standing Rules

- After closing a task, remove it from the active plan.
- Always print the remaining plan after closing a task.
- Always provide the next recommendation.
- Suggest single, pair and triple bundles when useful.
- If a useful new idea appears during execution, add it to the active plan under
  the priority scale and state which bucket it was added to.
- Mark carried work as `carried from Phase N` and preserve its gate.
- Keep live/destructive/write/public/config actions behind named gates.

## Verification Policy

For every implementation slice record:

- RED result, if tests were added;
- focused GREEN result;
- expanded regression result;
- lint/format/whitespace result;
- commit id;
- push target;
- skipped checks and why.

## Evidence Policy

Every closed slice should leave:

- evidence file path;
- changed repos/branches/commits;
- verification output summary;
- safety statement;
- active-plan cleanup;
- next recommendation.

## Decision Log

```text
Date:
Decision:
Reason:
Scope:
Not authorized:
Evidence:
```

## Release/Deploy State

Track these separately:

- local branch head;
- package-ready head;
- latest deployed/smoked head;
- public-ready status;
- rollback/recovery path.

## Next Chat Packet

Keep a short handoff that includes:

- working folder;
- source-of-truth files;
- current heads;
- safety boundaries;
- active plan;
- last closed task;
- next recommendation.
