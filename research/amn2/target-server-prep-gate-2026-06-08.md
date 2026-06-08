# Target server prep gate 2026-06-08

Дата: 2026-06-08.

Назначение: зафиксировать новый docs-only/read-only slice для подготовки отдельного целевого VPS после validation smoke `f7f6131`.

## Baseline

```text
current AMN2 head: f7f6131 Update integration status for c92 manual prelaunch
current AMN3 package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
package status: read-only-vps-smoke-pass
source_update_run_id: 20260607T203721Z
api_smoke_run_id: 20260607T203730Z
latest_repeat_api_smoke_run_id: 20260607T204300Z
validation VPS mode: manual runtime
systemd on validation VPS: not used
public 3030/3040: no
```

## Scope

Этот slice только готовит целевой сервер к будущему gate:

- фиксирует минимальные требования к VPS;
- задает safe precheck summary;
- сохраняет правило: web/admin backend `127.0.0.1:3030`, API smoke `127.0.0.1:3040`;
- отделяет source-overlay read-only smoke от service-mode deployment;
- запрещает публикацию secret-bearing evidence.

## Artifacts

```text
gate: docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md
runbook after safe precheck: docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md
safe evidence template: research/amn2/target-server-prep-evidence-template-2026-06-08.md
target repo: AMN3 / VPS-OPS-LAB
production code changes: none
AMN2 code changes: none
```

## Still Blocked

- `VPS_APPLY_ENABLED=true`;
- live peer apply/revoke;
- public API `3040`;
- direct public web/admin `3030`;
- service-mode `systemd`/reverse proxy deployment without separate gate;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config routes;
- backup/import/reboot routes;
- raw tokens, Authorization headers, token hashes, `.env`, `servers.yml`, private keys, PSK, `.conf`, QR, `vpn://`, backup contents or full logs.

## Next Evidence Expected

Safe operator summary from the new target server:

```text
target_server_prep_status:
os:
kernel:
arch:
python:
curl:
sha256sum:
ss:
amn2_loopback_listeners:
ufw_status_summary:
dns_or_admin_domain_ready:
https_reverse_proxy_ready:
direct_public_3030: no
public_api_3040: no
VPS_APPLY_ENABLED: false/not-set
next_requested_gate:
```

No secrets are required for Codex.
