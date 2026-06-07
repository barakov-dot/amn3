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
current amn2 git head: 42ffa65 Record git checkout smoke status
current app-code read-only smoke slice: 62ff184 Update controlled prod status visibility
current VPS source overlay: 42ffa65 Record git checkout smoke status
previous VPS source overlay: c8a6363 Add Local Agent runtime summary mapper
```

## Уже доказано

```text
current VPS-smoked source-overlay package: dist/amn2-vps-update-and-smoke-kit-42ffa65.zip
current package sha256: 5B43B467E014E87FEC1E49E8D9A8B7A2FBF841541BE88FDC6768097806240E39
current source sha256: 8A5B83D9AB95BE4230AAC221CE0321A37EF37E4E4B6EAB5EDECAE3C98A944829
current package status: read-only-vps-smoke-pass
last VPS read-only smoke: pass
last VPS run_id: 20260607T165625Z
checked_routes: 6
routes: servers, integration_status, local_agent_runtime_summary, server_summary, metrics_summary, users_summary
auth checks: missing bearer 401, wrong scope 403, revoked token 401
listener_status: passed
audit_status: passed
forbidden_markers: none in returned route evidence
Phase 2 single disposable peer apply/revoke: verified-live on stable line
source overlay commit: 42ffa65
previous source overlay commit: c8a6363
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
source-overlay package: dist/amn2-vps-update-and-smoke-kit-42ffa65.zip
source-overlay package sha256: 5B43B467E014E87FEC1E49E8D9A8B7A2FBF841541BE88FDC6768097806240E39
source sha256: 8A5B83D9AB95BE4230AAC221CE0321A37EF37E4E4B6EAB5EDECAE3C98A944829
source-overlay package status: read-only-vps-smoke-pass
```

## Текущий статус

```text
source overlay 42ffa65 read-only-vps-smoke-pass
previous source overlay c8a6363 read-only-vps-smoke-pass
git-checkout read-only status line 62ff184 smoke-pass with checked_routes=6
amn2 current git head 42ffa65 records that status
32d01fd is historical prior VPS-smoked source
controlled-prod-readiness: controlled-prod-ready
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

For current source overlay `42ffa65`, read-only VPS update/smoke passed with `run_id=20260607T165625Z`. `controlled-prod-ready` continues to apply inside the same operator-only boundary after these conditions were met:

- source overlay commit is `42ffa65`;
- read-only VPS smoke passed for `42ffa65`;
- web/admin access path is operator-approved HTTPS reverse proxy;
- public API port `3040` is not exposed;
- `VPS_APPLY_ENABLED` default is `false`;
- host key prompt is absent/verified when SSH is used, or not applicable for web/admin reverse-proxy access;
- recovery path is known;
- no stop condition is present;
- no secret-bearing evidence was pasted.

`32d01fd` can be discussed only as the previous baseline, not as the current git head.

After the original `c8a6363` decision, AMN2 advanced locally to git head `42ffa65`; the app-code read-only slice `62ff184` passed a separate git-checkout smoke on `/opt/amn2-git` with six read-only routes, then source-overlay promotion to `/opt/amn2` passed through the AMN3 update/smoke kit.

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
complete controlled production launch checklist for source overlay 42ffa65
or continue read-only controlled-prod status/recovery visibility
operator documentation cleanup
another read-only status/observability slice
```

Не переходить сразу к config delivery, public API writes, backup/import или Local Agent mutations.
