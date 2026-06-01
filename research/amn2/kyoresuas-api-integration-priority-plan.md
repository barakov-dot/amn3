# `amn2`: KYORESUAS-derived API integration priority plan

Дата: 2026-06-01.

Назначение: зафиксировать новый приоритет после успешной установки `amn2` на VPS: API integration становится главной product lane, но переносится как собственный `amn2` contract без копирования `kyoresuas/amnezia-api` implementation.

## Decision

`VPN Ops Lab — KYORESUAS-API` остается high-priority API architecture reference. Ближайшая цель `amn2` - не полный `/clients` CRUD, а первый безопасный read-only API route shell для controller/integration usage.

Первый API slice:

```text
read-only aggregate server/API summary
```

Почему не write API первым:

- KYORESUAS показывает полезную форму API, но его broad `x-api-key`, public `/docs`/`metrics`, backup/import/reboot and Docker socket exposure нельзя переносить как default.
- `amn2` уже имеет scoped API token storage/lifecycle, route/auth bindings, secret/redaction gates and privacy classification.
- Read-only aggregate route shell дает integration value без secret-read, config delivery, peer mutation или Docker restart.

## Entry conditions

Перед API implementation:

- VPS package install completed.
- Web and bot can start manually or have a recorded startup error to fix.
- `VPS_APPLY_ENABLED=false`.
- `bot check-network`, `server preflight`, `server check --dry-run` have been attempted and redacted results are known.
- `pyproject.toml` packaging discovery bug is fixed in `amn2`, so `pip install -e .` works in a clean venv.

For the first read-only API shell, Phase 2 live `apply-peer --apply` is not required because the slice must not call live mutation paths. Any API route that calls SSH, syncs peers, emits config, or changes runtime state still requires a separate VPS gate.

## First slice scope

Allowed:

- FastAPI `/api/*` route shell with explicit route policy entries.
- Bearer/scoped token auth using existing `api_tokens` service contract.
- `server:read` route for server aliases/status/readiness metadata.
- `metrics:read` route for aggregate counts/totals only.
- No-secret JSON response tests.
- No raw token in logs/audit/errors.

Candidate endpoints:

```text
GET /api/servers
GET /api/servers/{server_name}/summary
GET /api/metrics/summary
```

Default response must be aggregate-only:

- server alias;
- configured/enabled flags;
- runtime kind;
- latest local health/readiness flags if available;
- aggregate user/device/peer counts;
- aggregate traffic totals only if already available without per-peer labels.

Forbidden in first slice:

- `/api/clients` create/update/delete;
- API `config:read`;
- `.conf`, QR, `vpn://`, private key, PSK;
- backup/import/reboot;
- public unauthenticated `/docs` or `/metrics`;
- raw SSH command output;
- Docker socket/control operations;
- KYORESUAS Node/Fastify code copy.

## Priority split

### Critical

1. Fix `amn2` packaging discovery so VPS installs can use `pip install -e .`.
2. Finish VPS manual startup/preflight evidence with secrets redacted.
3. Write implementation plan for read-only aggregate API route shell.

### Important

4. Add route policy entries for the new API endpoints before route code.
5. Bind endpoints to scoped API token auth and prove `server:read` cannot access `metrics:read`.
6. Add no-secret response/audit tests for every endpoint.

### Simple

7. Document example safe `curl` commands with placeholder tokens only.
8. Update AMN3 transfer evidence after the branch is pushed.

### Cosmetic

9. OpenAPI/docs grouping after route behavior is stable.
10. Naming cleanup for API terms: server summary, metrics summary, controller-safe fields.

## Next plan artifact

Next implementation plan should be:

```text
docs/superpowers/plans/2026-06-01-amn2-read-only-api-route-shell.md
```

It should be implemented in `amn2` on a separate branch after the packaging fix and VPS startup/preflight evidence are recorded.
