# Phase 6 P6-I005 Telegram profile icon gate policy

Date: 2026-06-13.

## Decision

`P6-I005` is closed as AMN2 local-only code/tests/docs work.

Result:

- AMN2 branch `codex-vps-test-prep` advanced to `19f3422 Add Telegram profile icon gate policy`;
- AMN2 remote `amn2/codex-vps-test-prep` was updated from `0c6aa7c` to `19f3422`;
- latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`;
- `19f3422` has not been package-rebuilt or VPS-smoked;
- Telegram identity mutation remains closed until a separate named gate.

## Scope

Local-only implementation:

- added `telegram_profile_icon_apply` to the safe productization manifest;
- recorded access/support/news bot profile icon apply as blocked without `P6-I005` named Telegram identity mutation gate;
- recorded allowed default work as local image validation, local registry metadata, operator checklist drafting and safe evidence summary;
- recorded blocked actions: Bot API profile-photo mutation, BotFather/manual mutation by Codex, live bot send and Telegram token use;
- added blocked-future surface policy entries for access/support/news bot profile icon apply;
- exposed the safe gate through `/api/integration/status` and web `/integration-status`;
- updated `docs/COMMERCIAL_AND_BOT_PRODUCTIZATION_BOUNDARY.ru.md`.

## Verification

TDD red check:

```text
python -m pytest tests/services/test_productization_boundary.py tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/security/test_surface_policy.py tests/web/test_web_integration_status.py -q --basetemp tmp\pytest-p6-i005-red
6 failed, 27 passed, 1 warning
```

Expected failures:

- missing `telegram_profile_icon_apply` manifest;
- missing profile icon blocked-future surface policy entries;
- web integration status did not render the profile-icon gate.

Focused verification:

```text
python -m pytest tests/services/test_productization_boundary.py tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/security/test_surface_policy.py tests/web/test_web_integration_status.py -q --basetemp tmp\pytest-p6-i005-green
33 passed, 1 warning
```

Expanded verification:

```text
python -m pytest tests/services/test_productization_boundary.py tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py tests/services/test_bot_media.py tests/cli/test_bot_media_cli.py tests/web/test_web_integration_status.py tests/web/test_logs_settings_orders.py tests/bot/test_telegram_ux.py -q --basetemp tmp\pytest-p6-i005-expanded
83 passed, 1 warning
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
- Telegram token use;
- live bot send;
- Telegram profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

`VPS_APPLY_ENABLED=false` remains the default boundary.

## Next recommendation

`P6-M002 + P6-N002` as a paired privacy/status bundle:

- `P6-M002` Health/status polling scheduler with aggregate-only privacy boundary;
- `P6-N002` Admin analytics without per-peer/user leakage.

Default scope remains local-only/docs/tests without live probes, public exposure,
write routes, Local Agent mutations or per-peer/user leakage.
