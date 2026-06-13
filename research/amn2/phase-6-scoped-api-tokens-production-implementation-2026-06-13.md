# Phase 6 P6-I001 Scoped API tokens production implementation

Date: 2026-06-13.

## Decision

`P6-I001` is closed as AMN2 local-only code/tests/docs work.

Result:

- AMN2 branch `codex-vps-test-prep` advanced to `0b3ac1f Add API token production policy`;
- AMN2 remote `amn2/codex-vps-test-prep` was updated from `2215761` to `0b3ac1f`;
- latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`;
- `0b3ac1f` has not been package-rebuilt or VPS-smoked;
- Phase 6 public/self-service launch remains `no-go` until separate named gates.

## Scope

Local-only implementation:

- added a machine-checkable `ApiTokenProductionPolicy`;
- kept allowed route-connected API token scopes to `server:read` and `metrics:read`;
- recorded blocked production scopes: `config:read`, `server:write`, `clients:write`, `local-agent:write`, `backup:read`, `backup:restore`;
- added a production route-token TTL limit: `API_TOKEN_PRODUCTION_MAX_TTL_DAYS=30`;
- added a rotation notice constant: `API_TOKEN_PRODUCTION_ROTATION_NOTICE_DAYS=7`;
- made `create_route_api_token()` reject expiry beyond the production TTL;
- kept raw token display one-time only and safe metadata free of raw token/hash values;
- aligned the disabled web/admin API token form max value with the same TTL policy;
- updated `docs/API_TOKEN_POLICY.ru.md`.

## Verification

TDD red check:

```text
tests/services/test_api_tokens.py failed during collection before implementation:
ImportError: cannot import name 'API_TOKEN_PRODUCTION_MAX_TTL_DAYS'
```

Focused verification:

```text
python -m pytest tests/services/test_api_tokens.py tests/web/test_api_tokens.py -q --basetemp tmp\pytest-p6-i001-token-web
18 passed, 1 warning
```

Expanded verification:

```text
python -m pytest tests/services/test_api_tokens.py tests/web/test_api_tokens.py tests/api/test_cli_tokens.py tests/api/test_app.py tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py -q --basetemp tmp\pytest-p6-i001-expanded
59 passed, 1 warning
```

Hygiene:

```text
git diff --check
passed
```

Known warning:

```text
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
```

## Safety boundary

This slice did not perform:

- live VPS command;
- SSH command against target VPS;
- package apply/rebuild on VPS;
- service restart/deploy;
- public exposure;
- config delivery, `.conf`, QR or `vpn://`;
- write API route or `/api/clients` CRUD;
- Local Agent mutation or config route;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use, live bot send or Telegram profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

`VPS_APPLY_ENABLED=false` remains the default boundary.

## Remaining gates

This does not open:

- `P6-C001` Public exposure gate;
- `P6-C002` Config delivery gate;
- `P6-C003` Write API production gate;
- `P6-C004` Production backup/restore/import gate;
- Local Agent write/config routes;
- production peer/user mutation;
- public/self-service API or web access.

## Next recommendation

`P6-I002` User self-service surface separated from admin surface as local-only/docs/tests planning, without opening public exposure, config delivery, write API or live gates.
