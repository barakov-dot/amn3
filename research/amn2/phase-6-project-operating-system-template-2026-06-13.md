# Phase 6 project operating system extraction template

Date: 2026-06-13.

## Scope

Closed:

- `P6-S003` Project operating system extraction template.

This was completed as AMN3 docs-only work. It extracts the project-memory method
used in AMN2/AMN3 into clean templates for a future project.

## Created

```text
docs/templates/PROJECT_OPERATING_SYSTEM_TEMPLATE.ru.md
docs/templates/NEXT_PROJECT_BOOTSTRAP.ru.md
```

## Contents

- source-of-truth fields;
- project goal and non-goals;
- safety boundaries;
- priority-scale active plan;
- standing rules for task closeout and new idea capture;
- verification and evidence policy;
- decision log;
- release/deploy state distinctions;
- next-chat bootstrap packet for a new project.

## Safety

Not performed:

- AMN2 runtime code change;
- live VPS command;
- SSH command;
- package apply/rebuild on VPS;
- service restart/deploy;
- public exposure;
- config delivery;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- payment processor integration;
- Telegram token use;
- live bot send;
- Telegram profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

## Closeout

`P6-S003` is removed from the active Phase 6 plan.

Next recommendation remains `P6-N004 + P6-S002` together as local-only/docs/tests.
