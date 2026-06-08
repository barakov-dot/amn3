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
research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md
docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md
docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md
docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
research/amn2/target-server-prep-gate-2026-06-08.md
research/amn2/target-server-prep-evidence-template-2026-06-08.md
research/amn2/unified-prod-gate-handoff-2026-06-08.md
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
current amn2 git head status: read-only status visibility, VPS source-overlay-smoked
current amn2 git head evidence: research/amn2/manual-prelaunch-integration-status-2026-06-07.md
current amn2 package evidence: research/amn2/f7f6131-status-alignment-vps-package-2026-06-07.md
current amn2 VPS smoke evidence: research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md
current app-code read-only smoke slice: 62ff184 Update controlled prod status visibility
current VPS source overlay: f7f6131 Update integration status for c92 manual prelaunch
previous VPS source overlay: c92bd1a Bind web admin systemd to loopback
historical prior VPS source overlay: c8a6363 Add Local Agent runtime summary mapper
```

## Уже доказано

```text
current VPS-smoked source-overlay package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
current package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
current source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
current package status: read-only-vps-smoke-pass
last VPS read-only smoke: pass
source_update_run_id: 20260607T203721Z
api_smoke_run_id: 20260607T203730Z
latest_repeat_api_smoke_run_id: 20260607T204300Z
checked_routes: 6
routes: servers, integration_status, local_agent_runtime_summary, server_summary, metrics_summary, users_summary
route_status_codes: all 200
forbidden_markers: none
auth checks: missing bearer 401, wrong scope 403, revoked token 401
listener_status: passed
audit_status: passed
Phase 2 single disposable peer apply/revoke: verified-live on stable line
source overlay commit: f7f6131
previous source overlay commit: c92bd1a
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
previous c92 source-overlay package: dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
previous c92 source-overlay package status: read-only-vps-smoke-pass
web/admin backend template: 127.0.0.1:3030 loopback-only
status-alignment package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
status-alignment package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
status-alignment source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
status-alignment package status: read-only-vps-smoke-pass
status-alignment VPS smoke: passed
status-alignment source update run_id: 20260607T203721Z
status-alignment api smoke run_id: 20260607T203730Z
status-alignment latest repeat api smoke run_id: 20260607T204300Z
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
source overlay f7f6131 read-only-vps-smoke-pass
previous source overlay c92bd1a read-only-vps-smoke-pass
historical prior source overlay c8a6363 read-only-vps-smoke-pass
git-checkout read-only status line 62ff184 smoke-pass with checked_routes=6
amn2 current git head f7f6131 is VPS-smoked
current VPS source overlay f7f6131 is VPS-smoked
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

For current source overlay `f7f6131`, read-only VPS update/smoke passed with `api_smoke_run_id=20260607T203730Z` and a latest repeat API smoke pass `20260607T204300Z`. The previous `c92bd1a` follow-up manual runtime gate passed with operator-started web/admin and bot processes, and `f7f6131` only aligns read-only status visibility to that accepted state. `controlled-prod-ready` continues to apply inside the same operator-only boundary after these conditions were met:

- source overlay commit is `f7f6131`;
- read-only VPS smoke passed for `f7f6131`;
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

After that source-overlay proof, AMN2 advanced to `c92bd1a Bind web admin systemd to loopback`; AMN3 package `c92bd1a` passed real VPS source-overlay smoke. Route-level JSON for that run is attached: six read-only routes returned `200` with no forbidden markers. Neighboring AMN2 status work then advanced the repository branch to `f7f6131 Update integration status for c92 manual prelaunch`; AMN3 package `f7f6131` also passed read-only VPS source-overlay smoke with six read-only routes returned `200` and no forbidden markers.

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
complete controlled production launch checklist for source overlay f7f6131
keep current operator-only manual runtime boundary
prepare new target server through target-server prep gate, then use runbook only after safe precheck review
prepare unified production handoff after Phase 2 safe summary
or continue read-only controlled-prod status/recovery visibility
open a separate service-mode gate only if systemd/reverse proxy deployment becomes required
operator documentation cleanup
another read-only status/observability slice
```

Не переходить сразу к config delivery, public API writes, backup/import или Local Agent mutations.
