# Manual prelaunch integration status update

Дата: 2026-06-07.

Назначение: зафиксировать safe summary соседнего AMN2 status-visibility follow-up после manual runtime/prelaunch gate.

## AMN2 Head

```text
repo: C:\Users\SooL\Documents\Amneziya
branch: codex-vps-test-prep
remote branch: amn2/codex-vps-test-prep
head: f7f6131 Update integration status for c92 manual prelaunch
previous source-overlay package head: c92bd1a Bind web admin systemd to loopback
```

## Scope

`f7f6131` updates read-only controller-facing status only:

```text
surface: /api/integration/status
surface: web /integration-status
status label: manual_prelaunch_ready
source_overlay_head_reported: c92bd1a
manual_validation_lane: included
write_routes_enabled: false
public_api_exposed: false
```

Files changed in AMN2:

```text
app/services/integration_status.py
app/web/templates/integration_status.html
docs/NEXT_CHAT_HANDOFF.ru.md
tests/api/test_api_integration_status.py
tests/services/test_integration_status_service.py
tests/web/test_web_integration_status.py
```

## Boundary

This read-only status update is now the current VPS-smoked source overlay:

```text
previous proven VPS source overlay: c92bd1a
current proven VPS source overlay: f7f6131
latest AMN2 repository head: f7f6131
f7f6131 package status: read-only-vps-smoke-pass
f7f6131 source update run_id: 20260607T203721Z
f7f6131 API smoke run_id: 20260607T203730Z
f7f6131 latest repeat API smoke run_id: 20260607T204300Z
f7f6131 VPS source-overlay smoke: passed
next safe step: keep manual-runtime boundary; open service-mode gate only by separate decision
```

Still blocked without a separate gate:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040` exposure;
- direct public web/admin `3030` exposure;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- secret-bearing evidence or full logs.
