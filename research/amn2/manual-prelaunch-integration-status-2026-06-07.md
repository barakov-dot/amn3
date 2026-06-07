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

This update does not supersede the current VPS-smoked source overlay:

```text
current proven VPS source overlay: c92bd1a
latest AMN2 repository head: f7f6131
f7f6131 package status: package-prepared
f7f6131 VPS source-overlay smoke: not run in this evidence
next safe step: apply f7f6131 read-only update+smoke kit with VPS_APPLY_ENABLED=false
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
