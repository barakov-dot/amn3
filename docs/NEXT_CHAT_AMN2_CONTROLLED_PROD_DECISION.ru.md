# NEXT CHAT: AMN2 Controlled Prod Decision

Дата: 2026-06-06.

Цель следующего чата: принять operator-only решение по controlled prod readiness для текущего `amn2/codex-vps-test-prep` baseline.

Это не разрешение на public prod, live peer mutations, API write routes, config delivery, Local Agent mutations, backup/import/reboot или публикацию secret-bearing evidence.

## Сначала прочитать

```text
docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
research/amn2/controlled-prod-readiness-2026-06-06.md
research/amn2/integration-status-controlled-prod-update-2026-06-06.md
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
current amn2 head: 32d01fd Update integration status for controlled prod
```

## Уже доказано

```text
package: dist/amn2-vps-update-and-smoke-kit-32d01fd.zip
package sha256: BE59AF74001AC4F094C753B565A4E672194D823C4F65B6CB476F4FF01B310807
source sha256: 034753DA7EC42ACF869519F43909EEFDC8A392A5665B2A33C935F8A058CCB99B
VPS read-only smoke: pass
run_id: 20260606T185114Z
checked_routes: 5
routes: servers, integration_status, server_summary, metrics_summary, users_summary
auth checks: missing bearer 401, wrong scope 403, revoked token 401
listener_status: passed
audit_status: passed
forbidden_markers: none in returned route evidence
Phase 2 single disposable peer apply/revoke: verified-live on stable line
```

## Текущий статус

```text
32d01fd read-only-vps-smoke-pass
controlled-prod-readiness: operator confirmations pending
```

## Что нужно от оператора

Вернуть только безопасный decision packet:

```text
source overlay commit: 32d01fd | other
integration status safe fields: ok | not checked | needs-fix
web/admin access path: loopback | ssh-tunnel | private-network | approved-reverse-proxy | other
VPS_APPLY_ENABLED default: false | other
host key prompt: none | verified-out-of-band | unexpected
recovery path known: yes | no
decision: controlled-prod-ready | needs-fix | defer-prod
next action:
```

## Decision Rules

`controlled-prod-ready` можно записать только если:

- source overlay commit is `32d01fd`;
- web/admin access path is operator-only;
- `VPS_APPLY_ENABLED` default is `false`;
- host key prompt is absent or verified out-of-band;
- recovery path is known;
- no stop condition is present;
- no secret-bearing evidence was pasted.

`needs-fix` обязателен при smoke/auth/listener/audit/checksum/access-path/host-key/evidence hygiene failure.

`defer-prod` подходит, если система здорова, но операторские условия доступа или recovery пока не готовы.

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
controller-safe Local Agent runtime summary
```

Design source:

```text
research/amn2/local-agent-runtime-metadata-alignment.md
```

Не переходить сразу к config delivery, public API writes, backup/import или Local Agent mutations.
