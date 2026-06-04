# `amn2`: KYORESUAS-derived API integration priority plan

Дата: 2026-06-01.

Актуализация 2026-06-03: первый read-only API route shell реализован в `amn2/codex/read-only-api-route-shell`, latest real VPS API-only smoke passed (`run_id=20260603T112418Z`, DB-only server config sync выполнен, preflight `skipped`, API/auth/scope/revoke/listener/audit `passed`, `VPS_APPLY_ENABLED=false`) и fast-forward merged в stable `codex-vps-test-prep` at `5f12736 Record VPS API smoke evidence`. Этот документ теперь является исходным priority decision и safety boundary; текущий следующий gate - не повторная локальная реализация, а отдельные route/secret/remote-write gates для любого расширения API.

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

## Priority status

### Critical

1. `done-local`: Fix `amn2` packaging discovery so VPS installs can use `pip install -e .` - commit `e99d5f3`.
2. `done-local`: Write and implement the read-only aggregate API route shell plan - commits `6534ac4`, `9cccdc2`, `b37103a`, `2010d60`.
3. `done-vps-gate`: Finish real VPS loopback API smoke evidence with secrets redacted - latest AMN3 evidence `research/amn2/api-vps-smoke-evidence-2026-06-03.md`.

### Important

4. `done-local`: Add route policy entries for the new API endpoints.
5. `done-local`: Bind endpoints to scoped API token auth and prove `server:read` cannot access `metrics:read`.
6. `done-local`: Add no-secret response/audit tests for every endpoint.

### Simple

7. `done-local`: Document safe smoke flow with placeholder tokens only.
8. `done-after-vps-smoke`: Update AMN3 transfer evidence after VPS smoke.

### Cosmetic

9. `defer`: OpenAPI/docs grouping after a separate docs exposure decision.
10. `defer`: Naming cleanup for API terms only if route behavior changes.

## Implemented plan artifact

Implementation plan:

```text
docs/superpowers/plans/2026-06-01-amn2-read-only-api-route-shell.md
```

Implemented in `amn2/codex/read-only-api-route-shell` and merged into `codex-vps-test-prep` at `5f12736`. Do not start another API implementation branch from AMN3; future API work starts from this stable read-only baseline and requires separate gates for write/config/remote-changing surfaces.
