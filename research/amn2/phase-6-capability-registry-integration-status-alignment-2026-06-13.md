# Phase 6 P6-M001 + P6-N003 Capability registry and integration status alignment

Date: 2026-06-13.

## Decision

`P6-M001` and `P6-N003` are closed together as AMN2 local-only code/tests/docs work.

Result:

- AMN2 branch `codex-vps-test-prep` advanced to `3118b43 Make integration status source head dynamic`;
- AMN2 remote `amn2/codex-vps-test-prep` was updated from `b676e1b` to `3118b43`;
- latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`;
- `3118b43` has not been package-rebuilt or VPS-smoked;
- Phase 6 public/self-service launch remains `no-go` until separate named gates.

Implementation commits:

- `4bb7364 Align integration status capability registry`;
- `3118b43 Make integration status source head dynamic`.

## Scope

Local-only implementation:

- aligned `/api/integration/status` and web `/integration-status` to Phase 6 current-head reality;
- added `source_checkpoint` with:
  - runtime current branch head read from local git when available, with `unknown` fallback outside a git checkout;
  - latest VPS-smoked/package head `2215761`;
  - package status for branch head `not_package_rebuilt_not_vps_smoked`;
  - public/self-service closed;
  - `VPS_APPLY_ENABLED=false`;
- added safe `capability_registry`;
- recorded current implemented capability as `single_server_operator_control` for `amneziawg` on `docker`;
- recorded future `wireguard` and `xray` protocol managers as `blocked_future`;
- kept no-upstream-code-copy license boundary explicit;
- updated web integration status rendering;
- updated `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`.

## Verification

TDD red check:

```text
python -m pytest tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/web/test_web_integration_status.py -q --basetemp tmp\pytest-p6-m001-n003-red
3 failed, 5 passed, 1 warning
```

Expected failures:

- old `manual_prelaunch_ready` status still present;
- old `c92bd1a`/`7764ae7` integration constants still present;
- missing Phase 6 source checkpoint/capability registry rendering.

Focused verification after the dynamic source-head fix:

```text
python -m pytest tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/web/test_web_integration_status.py -q --basetemp tmp\pytest-p6-m001-n003-dynamic
8 passed, 1 warning
```

Expanded verification:

```text
python -m pytest tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/api/test_app.py tests/web/test_web_integration_status.py tests/web/test_operator_ui_p5_o002.py tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py -q --basetemp tmp\pytest-p6-m001-n003-expanded2
46 passed, 1 warning
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

No protocol manager was implemented. `VPS_APPLY_ENABLED=false` remains the default boundary.

## Remaining gates

This does not open:

- `P6-C001` Public exposure gate;
- `P6-C002` Config delivery gate;
- `P6-C003` Write API production gate;
- `P6-C004` Production backup/restore/import gate;
- Local Agent write/config routes;
- production peer/user mutation;
- public/self-service API or web access;
- protocol manager implementation gates.

## Next recommendation

`P6-I003` Payments/manual approval boundary if commercial access is enabled, as local-only/docs/tests planning without opening public, payment processor, config, write or live gates.
