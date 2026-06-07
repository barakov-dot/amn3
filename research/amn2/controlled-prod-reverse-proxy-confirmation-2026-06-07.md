# Controlled prod reverse proxy confirmation

Дата: 2026-06-07.

Назначение: зафиксировать операторское подтверждение способа доступа к web/admin после `c8a6363` real VPS read-only smoke pass.

## Operator Confirmation

```text
web/admin access path: approved-reverse-proxy
transport: HTTPS
public API 3040 exposed: no
SSH tunnel required for web/admin: no
```

This confirmation supersedes the earlier assumption that web/admin would be checked only through SSH tunnel or direct loopback.

## Related Prior Evidence

Already recorded before this confirmation:

```text
source overlay commit: c8a6363
VPS_APPLY_ENABLED shell: false
VPS_APPLY_ENABLED .env: false
web listener: 127.0.0.1:3030 yes
login_http: 200
32d01fd rollback/update kit: present
c8a6363 update kit at check time: present
data_dir: present
env_file: present
servers_yml: present
```

Real VPS smoke evidence:

```text
research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md
run_id: 20260606T202040Z
decision: read-only-vps-smoke-pass
```

## Current Readiness Interpretation

The operator-approved reverse proxy is acceptable for controlled prod if it remains limited to the web/admin surface and the read-only API smoke port `3040` is not exposed publicly.

Still not enabled by this confirmation:

- public API exposure on `3040`;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- live `apply-peer --apply` or `revoke-peer --apply`;
- `VPS_APPLY_ENABLED=true`.

## Remaining Decision Fields

```text
recovery path known: yes
decision: controlled-prod-ready
next action: continue with read-only next slice
```

This confirmation removed the web/admin access-path blocker. Final readiness was later recorded in `research/amn2/controlled-prod-ready-2026-06-07.md`.
