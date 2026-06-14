# After Phase 6 P6-M005 multi-instance/IPAM conflict model

Дата: 2026-06-14.

Статус: `completed-amn2-local-only`.

AMN2 branch: `codex-vps-test-prep`.

AMN2 commit: `b121865 Add multi instance conflict model`.

## Scope

Implemented `P6-M005` as a local-only/docs/tests conflict model inside the
existing capability registry:

- `capability_registry.multi_instance_conflict_model`;
- status `local_conflict_model_ready`;
- gate `local-only/docs/tests`;
- live multi-instance apply disabled;
- write API required before apply: `P6-C003`;
- config delivery required before user-facing output: `P6-C002`;
- required checks for unique runtime instance IDs, listen ports, non-overlapping
  VPN CIDRs, interface names, endpoint pair review and DNS/IPv6 policy review;
- safe outputs limited to conflict report, operator notes and blocked-gate
  summary;
- blocked outputs include runtime config write, firewall change, peer migration,
  config delivery and service restart.

Added AMN2 doc:

```text
docs/MULTI_INSTANCE_IPAM_CONFLICT_MODEL.ru.md
```

## Boundaries

No live VPS command, SSH command, package rebuild/apply on VPS, service
restart/deploy, public exposure, public OpenAPI publication, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

Latest AMN2 VPS-smoked/package head remains `0de7a77`. AMN2 `b121865` is
local-only and not package-rebuilt or VPS-smoked.

## TDD evidence

RED:

```text
.\scripts\test.ps1 tests\services\test_integration_status_service.py tests\api\test_api_integration_status.py -q
result: 3 failed, 4 passed, 1 StarletteDeprecationWarning
```

Expected failures:

- missing `multi_instance_conflict_model` in service report;
- missing `multi_instance_conflict_model` in API report.

GREEN focused:

```text
.\scripts\test.ps1 tests\services\test_integration_status_service.py tests\api\test_api_integration_status.py -q
result: 7 passed, 1 StarletteDeprecationWarning
```

Expanded:

```text
.\scripts\test.ps1 tests\services\test_integration_status_service.py tests\api\test_api_integration_status.py tests\web\test_web_integration_status.py tests\services\test_fresh_install_wizard.py tests\services\test_public_productization_boundaries.py -q
result: 27 passed, 1 StarletteDeprecationWarning
```

Full AMN2:

```text
.\scripts\test.ps1 -q
result: 724 passed, 1 StarletteDeprecationWarning
```

Hygiene:

```text
git diff --check
result: passed

git diff --cached --check
result: passed
```

## Plan impact

Closed:

- `P6-M005` multi-instance/port/IPAM conflict model.

Still gated/deferred:

- `P6-C001` public exposure and public docs/OpenAPI publication;
- `P6-C002` real config delivery;
- `P6-C003` write API production;
- `P6-C004` backup/restore/import production;
- `P6-C007` destructive cleanup/reinstall;
- live VPS package apply/smoke for any head after `0de7a77`;
- Telegram identity/profile/media mutation.

## Recommendation

Next recommended step:

```text
Phase 6 final closeout + clean-installer next-phase entry + current VPS known-good snapshot/runbook
```

Alternative:

```text
pause on known-good 0de7a77 until a separate named live/public/config/destructive gate is intentionally opened
```
