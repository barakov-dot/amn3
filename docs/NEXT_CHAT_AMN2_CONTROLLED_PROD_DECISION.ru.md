# NEXT CHAT: AMN2 Controlled Prod Decision

Дата: 2026-06-06.

Цель следующего чата: принять operator-only решение по controlled prod readiness для текущего `amn2/codex-vps-test-prep` baseline.

Это не разрешение на public prod, live peer mutations, API write routes, config delivery, Local Agent mutations, backup/import/reboot или публикацию secret-bearing evidence.

## Сначала прочитать

```text
docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
research/amn2/controlled-prod-readiness-2026-06-06.md
research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md
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
current amn2 head: c8a6363 Add Local Agent runtime summary mapper
```

## Уже доказано

```text
current package: dist/amn2-vps-update-and-smoke-kit-c8a6363.zip
current package sha256: 027ECC1BAD7321FCCD61A4CCCA3AC9F06AAA9AC6A3D7115B4813253D19C2CFBF
current source sha256: E1E198979D988B3A5AA038CF732B8DCDBE854C48A6D381FADBA05BFDEE0251C6
current package status: read-only-vps-smoke-pass
last VPS read-only smoke: pass
last VPS run_id: 20260606T202040Z
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
c8a6363 read-only-vps-smoke-pass
32d01fd is historical prior VPS-smoked source
controlled-prod-readiness: operator confirmations pending
```

## Что нужно от оператора

Вернуть только безопасный decision packet:

```text
source overlay commit: c8a6363 | 32d01fd | other
integration status safe fields: ok | not checked | needs-fix
web/admin access path: loopback | ssh-tunnel | private-network | approved-reverse-proxy | other
VPS_APPLY_ENABLED default: false | other
host key prompt: none | verified-out-of-band | unexpected
recovery path known: yes | no
decision: controlled-prod-ready | needs-fix | defer-prod
next action:
```

## Decision Rules

For current `c8a6363`, read-only VPS update/smoke already passed with `run_id=20260606T202040Z`. `controlled-prod-ready` for current head can be recorded only if:

- source overlay commit is `c8a6363`;
- read-only VPS smoke passed for `c8a6363`;
- web/admin access path is operator-only;
- `VPS_APPLY_ENABLED` default is `false`;
- host key prompt is absent or verified out-of-band;
- recovery path is known;
- no stop condition is present;
- no secret-bearing evidence was pasted.

`32d01fd` can be discussed only as the previous baseline, not as the current git head.

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
