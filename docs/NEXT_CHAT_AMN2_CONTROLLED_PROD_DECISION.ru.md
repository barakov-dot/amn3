# NEXT CHAT: AMN2 Controlled Prod Decision

Дата: 2026-06-06.

Цель документа: исторически передать operator-only решение по controlled prod readiness для текущего `amn2/codex-vps-test-prep` baseline. Решение уже принято: `controlled-prod-ready`.

Это не разрешение на public prod, live peer mutations, API write routes, config delivery, Local Agent mutations, backup/import/reboot или публикацию secret-bearing evidence.

## Сначала прочитать

```text
docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
research/amn2/controlled-prod-readiness-2026-06-06.md
research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md
research/amn2/integration-status-controlled-prod-update-2026-06-06.md
research/amn2/controlled-prod-reverse-proxy-confirmation-2026-06-07.md
research/amn2/controlled-prod-ready-2026-06-07.md
research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md
research/amn2/controlled-prod-status-visibility-vps-repeat-smoke-2026-06-07.md
research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md
research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md
research/amn2/c92bd1a-manual-prelaunch-evidence-2026-06-07.md
research/amn2/manual-prelaunch-integration-status-2026-06-07.md
research/amn2/f7f6131-status-alignment-vps-package-2026-06-07.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
research/amn2/transfer-backlog.md
```

## Текущая точка

```text
repo AMN3: C:\Users\SooL\Documents\VPS-OPS-LAB
branch AMN3: master
AMN3 prefill evidence commit: e214fc9 Prefill controlled prod readiness
latest AMN3 commit: verify with git log -1

repo amn2: C:\Users\SooL\Documents\Amneziya
branch amn2: codex-vps-test-prep
current amn2 git head: f7f6131 Update integration status for c92 manual prelaunch
current amn2 git head status: read-only status visibility, package-prepared, not yet VPS source-overlay-smoked
current amn2 git head evidence: research/amn2/manual-prelaunch-integration-status-2026-06-07.md
current amn2 package-prepared evidence: research/amn2/f7f6131-status-alignment-vps-package-2026-06-07.md
current app-code read-only smoke slice: 62ff184 Update controlled prod status visibility
current VPS source overlay: c92bd1a Bind web admin systemd to loopback
previous VPS source overlay: 42ffa65 Record git checkout smoke status
historical prior VPS source overlay: c8a6363 Add Local Agent runtime summary mapper
```

## Уже доказано

```text
current VPS-smoked source-overlay package: dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
current package sha256: EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12
current source sha256: 272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2
current package status: read-only-vps-smoke-pass
last VPS read-only smoke: pass
source_update_run_id: 20260607T182118Z
api_smoke_run_id: 20260607T182131Z
checked_routes: 6
routes: servers, integration_status, local_agent_runtime_summary, server_summary, metrics_summary, users_summary
route_status_codes: all 200
forbidden_markers: none
auth checks: missing bearer 401, wrong scope 403, revoked token 401
listener_status: passed
audit_status: passed
Phase 2 single disposable peer apply/revoke: verified-live on stable line
source overlay commit: c92bd1a
previous source overlay commit: 42ffa65
VPS_APPLY_ENABLED shell/env: false
web/admin access path: approved-reverse-proxy over HTTPS
public API 3040 exposed: no
web listener: 127.0.0.1:3030
login_http: 200
rollback/current kits and data/.env/servers.yml: present
recovery path known: yes
decision: controlled-prod-ready
post-decision git-checkout smoke: 62ff184 read-only gate passed on /opt/amn2-git
post-decision documentation/status head: 42ffa65
prior source-overlay package: dist/amn2-vps-update-and-smoke-kit-42ffa65.zip
prior source-overlay package status: read-only-vps-smoke-pass
current source-overlay package: dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
current source-overlay package status: read-only-vps-smoke-pass
web/admin backend template: 127.0.0.1:3030 loopback-only
status-alignment package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
status-alignment package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
status-alignment source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
status-alignment package status: package-prepared
status-alignment VPS smoke: pending
manual runtime mode: manual
systemd web/bot: not-used
manual web process: present
manual bot process: present
manual web login: 200
direct public web 3030: no
public API 3040: no
manual runtime backup: backups/amneziya-backup-20260607T195851Z.tar.enc verified
manual runtime API smoke cycle: passed, checked_routes=6, forbidden_markers_count=0
```

## Текущий статус

```text
source overlay c92bd1a read-only-vps-smoke-pass
previous source overlay 42ffa65 read-only-vps-smoke-pass
historical prior source overlay c8a6363 read-only-vps-smoke-pass
git-checkout read-only status line 62ff184 smoke-pass with checked_routes=6
amn2 current git head f7f6131 is package-prepared, not yet VPS-smoked
current VPS source overlay c92bd1a is VPS-smoked
32d01fd is historical prior VPS-smoked source
controlled-prod-readiness: controlled-prod-ready
manual-runtime-validation: passed
```

## Operator Decision Packet

Recorded safe decision packet:

```text
integration status safe fields: ok via read-only smoke
host key prompt: not applicable for web/admin reverse-proxy access
recovery path known: yes
decision: controlled-prod-ready
next action: continue with read-only next slice
```

## Decision Rules

For current source overlay `c92bd1a`, read-only VPS update/smoke passed with `api_smoke_run_id=20260607T182131Z`, and the follow-up manual runtime gate passed with operator-started web/admin and bot processes. `controlled-prod-ready` continues to apply inside the same operator-only boundary after these conditions were met:

- source overlay commit is `c92bd1a`;
- read-only VPS smoke passed for `c92bd1a`;
- web/admin access path is operator-approved HTTPS reverse proxy;
- public API port `3040` is not exposed;
- `VPS_APPLY_ENABLED` default is `false`;
- host key prompt is absent/verified when SSH is used, or not applicable for web/admin reverse-proxy access;
- recovery path is known;
- current runtime mode is manual and `systemd` is not used;
- manual web/admin and bot processes are present;
- direct public `3030` and public API `3040` exposure are not present;
- no stop condition is present;
- no secret-bearing evidence was pasted.

`32d01fd` can be discussed only as the previous baseline, not as the current git head.

After the original `c8a6363` decision, AMN2 advanced locally to git head `42ffa65`; the app-code read-only slice `62ff184` passed a separate git-checkout smoke on `/opt/amn2-git` with six read-only routes, then source-overlay promotion to `/opt/amn2` passed through the AMN3 update/smoke kit.

After that source-overlay proof, AMN2 advanced to `c92bd1a Bind web admin systemd to loopback`; AMN3 package `c92bd1a` passed real VPS source-overlay smoke. Route-level JSON for that run is now attached: six read-only routes returned `200` with no forbidden markers. Neighboring AMN2 status work then advanced the repository branch to `f7f6131 Update integration status for c92 manual prelaunch`; AMN3 now has a prepared `f7f6131` update+smoke kit, but that commit is not yet the VPS source overlay.

`needs-fix` would be required if smoke/auth/listener/audit/checksum/access-path/host-key/evidence hygiene failed.

`defer-prod` would be appropriate if the system were healthy but operator recovery/access conditions were not ready. The recorded decision is `controlled-prod-ready`.

## Остается запрещено без отдельного подтверждения

- `VPS_APPLY_ENABLED=true`;
- `apply-peer --apply`;
- `revoke-peer --apply`;
- public web/API exposure;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- full logs, `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR, `vpn://` links.

## После controlled-prod-ready

Следующий safe implementation slice должен оставаться read-only:

```text
complete controlled production launch checklist for source overlay c92bd1a
keep current operator-only manual runtime boundary
apply f7f6131 status-alignment package with VPS_APPLY_ENABLED=false and repeat read-only smoke
or continue read-only controlled-prod status/recovery visibility
open a separate service-mode gate only if systemd/reverse proxy deployment becomes required
operator documentation cleanup
another read-only status/observability slice
```

Не переходить сразу к config delivery, public API writes, backup/import или Local Agent mutations.
