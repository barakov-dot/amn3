# Web-admin loopback systemd VPS package

Дата: 2026-06-07.

Назначение: зафиксировать AMN3 update/smoke kit для AMN2 head `c92bd1a Bind web admin systemd to loopback`. Это safety follow-up перед controlled production launch: web/admin systemd template теперь запускает backend только на `127.0.0.1:3030`, чтобы соответствовать approved HTTPS reverse proxy режиму и не открывать direct public `3030`.

## AMN2 Change

```text
AMN2 branch: codex-vps-test-prep
AMN2 commit: c92bd1a Bind web admin systemd to loopback
previous VPS-smoked source overlay: 42ffa65 Record git checkout smoke status
package status: package-ready-not-vps-smoked
```

Scope:

- `deploy/systemd/amneziya-web.service.example` теперь использует `--host 127.0.0.1 --port 3030`;
- production launch/checklist/setup docs обновлены под loopback backend + HTTPS reverse proxy;
- тест systemd template запрещает `--host 0.0.0.0`.

Это не меняет API routes, API scopes, peer apply/revoke logic, config delivery, backup/import или Local Agent mutation surfaces.

## Package

```text
dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
package sha256: EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12
source zip: dist/amn2-codex-vps-test-prep-c92bd1a-source.zip
source sha256: 272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2
operator doc: dist/amn2-vps-update-and-smoke-kit-c92bd1a/AMN2_VPS_UPDATE_AND_SMOKE_c92bd1a.ru.md
```

## Local Verification

AMN2 focused tests:

```text
tests/deploy/test_systemd_templates.py
tests/deploy/test_runtime_registry.py
result: 11 passed
```

Package hygiene:

```text
source_sha=passed 272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2
kit_sha=passed EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12
source_entries=298
forbidden_source_entries=none
required_source_entries=present
web_template_loopback=passed
kit_entries=5
required_kit_entries=present
text_hygiene=passed
test_extract=passed
```

## Safety Boundary

This package does not authorize:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040` exposure;
- direct public web/admin `3030` exposure;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- publishing `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR payloads, `vpn://` links or full logs.

## Next Gate

Operator-only next step:

```text
Download/update with dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
Run source overlay update on /opt/amn2 with VPS_APPLY_ENABLED=false
Run read-only API loopback smoke
Verify web systemd template/installed unit uses 127.0.0.1:3030
Return only safe summary evidence
```

Until that pass is returned, the current VPS-smoked source overlay remains `42ffa65`.
