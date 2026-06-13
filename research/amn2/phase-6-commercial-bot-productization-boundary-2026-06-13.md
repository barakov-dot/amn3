# Phase 6 P6-I003 + P6-I004 Commercial and bot productization boundary

Date: 2026-06-13.

## Decision

`P6-I003` and `P6-I004` are closed together as AMN2 local-only code/tests/docs work.

Result:

- AMN2 branch `codex-vps-test-prep` advanced to `0c6aa7c Add commercial bot productization boundary`;
- AMN2 remote `amn2/codex-vps-test-prep` was updated from `3118b43` to `0c6aa7c`;
- latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`;
- `0c6aa7c` has not been package-rebuilt or VPS-smoked;
- payment processor, public/config/write/live gates remain closed.

## Scope

Local-only implementation:

- added `app.services.productization_boundary` as a safe productization manifest;
- recorded commercial access as manual-approval-only;
- kept payment processor, payment webhook, automatic entitlement and config delivery on payment blocked;
- recorded current access bot as the only runtime owning access/config behavior;
- recorded future support/news bots as blocked-future and requiring separate tokens/runtimes;
- added blocked-future surface policy entries for payment webhook, entitlement activation and support/news bot runtimes;
- exposed the safe productization boundary through `/api/integration/status` and web `/integration-status`;
- added `docs/COMMERCIAL_AND_BOT_PRODUCTIZATION_BOUNDARY.ru.md`.

## Verification

TDD red check:

```text
python -m pytest tests/services/test_productization_boundary.py tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/security/test_surface_policy.py -q --basetemp tmp\pytest-p6-i003-i004-red2
1 error, 1 warning
```

Expected failure:

- missing `app.services.productization_boundary`.

Focused verification:

```text
python -m pytest tests/services/test_productization_boundary.py tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/security/test_surface_policy.py -q --basetemp tmp\pytest-p6-i003-i004-green
29 passed, 1 warning
```

Expanded verification:

```text
python -m pytest tests/services/test_productization_boundary.py tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py tests/services/test_bot_media.py tests/cli/test_bot_media_cli.py tests/web/test_web_integration_status.py tests/web/test_logs_settings_orders.py tests/bot/test_telegram_ux.py -q --basetemp tmp\pytest-p6-i003-i004-expanded2
81 passed, 1 warning
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
- payment processor integration or external payment call;
- Telegram token use, live bot send or Telegram profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

No support/news bot runtime was started. No payment route was mounted.
`VPS_APPLY_ENABLED=false` remains the default boundary.

## Follow-up candidate

Candidate discovered during implementation:

- `P6-I006` Commercial entitlement/audit boundary: define entitlement records,
  manual review reason codes and safe audit fields before any payment provider
  integration.

This candidate is proposed but not active until explicitly accepted.

## Next recommendation

`P6-I005` Telegram bot profile/icon apply gates for access/support/news bots,
as local-only/docs/tests planning without opening Telegram identity mutation,
live bot send, config, write, public or live VPS gates.
