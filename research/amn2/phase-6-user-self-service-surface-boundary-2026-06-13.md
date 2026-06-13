# Phase 6 P6-I002 User self-service surface separated from admin surface

Date: 2026-06-13.

## Decision

`P6-I002` is closed as AMN2 local-only code/tests/docs work.

Result:

- AMN2 branch `codex-vps-test-prep` advanced to `b676e1b Add self-service surface boundary`;
- AMN2 remote `amn2/codex-vps-test-prep` was updated from `0b3ac1f` to `b676e1b`;
- latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`;
- `b676e1b` has not been package-rebuilt or VPS-smoked;
- Phase 6 public/self-service launch remains `no-go` until separate named gates.

## Scope

Local-only implementation:

- added `self-service` as a distinct `SurfaceName` in `app/security/surface_policy.py`;
- recorded future `/self-service` dashboard as `blocked-future`;
- recorded future `/self-service/devices/{device_id}/config` as `blocked-future` and secret-bearing, gated by `P6-C001` and `P6-C002`;
- recorded future `/self-service/devices/{device_id}/revoke` as `blocked-future` and production mutation, gated by `P6-C001` and `P6-C003`;
- required future self-service policies to use separate self-service auth and own-account/device boundaries instead of `web-admin` actor/auth;
- added binding tests proving no `/self-service*` route is mounted in the current web/admin app;
- updated `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`.

## Verification

TDD red check:

```text
python -m pytest tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py -q --basetemp tmp\pytest-p6-i002-red
4 failed, 23 passed
```

Expected failures:

- missing `self_service.dashboard.blocked`;
- missing `self_service.config_delivery.blocked`;
- missing `self_service.device_revoke.blocked`;
- no `self-service` surface entries;
- no blocked future `/self-service*` policy routes.

Focused verification:

```text
python -m pytest tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py -q --basetemp tmp\pytest-p6-i002-surface
27 passed
```

Expanded verification:

```text
python -m pytest tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py tests/api/test_app.py tests/web/test_api_tokens.py tests/web/test_operator_ui_p5_o002.py -q --basetemp tmp\pytest-p6-i002-expanded
43 passed, 1 warning
```

Hygiene:

```text
git diff --check
passed
git diff --cached --check
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

No `/self-service*` runtime route was added. `VPS_APPLY_ENABLED=false` remains the default boundary.

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

`P6-I003` Payments/manual approval boundary if commercial access is enabled, as local-only/docs/tests planning without opening public, payment processor, config, write or live gates.
