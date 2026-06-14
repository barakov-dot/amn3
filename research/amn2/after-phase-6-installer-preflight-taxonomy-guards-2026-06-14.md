# After Phase 6 FI-M004 + P6-N005 installer preflight and taxonomy guards

Дата: 2026-06-14.

Статус: `completed-amn2-local-only`.

AMN2 branch: `codex-vps-test-prep`.

AMN2 commit: `4cde273 Add installer preflight taxonomy guards`.

Source candidates:

- `FI-M004` package asset path preflight;
- `P6-N005` OpenAPI/taxonomy route-order drift guard.

## Scope

Implemented a short pre-closeout local-only bundle:

- fresh installer package preflight now includes `asset_path_preflight` as a
  required package/preflight-only check;
- rendered fresh-install plans include a `package-asset-path-preflight` phase;
- package asset path preflight records required checks for operator-kit files,
  generated runbook paths, package archive manifest paths, source zip manifest
  paths and secret-free asset manifest policy;
- public docs/API taxonomy boundary now includes a deterministic route-order
  drift guard;
- taxonomy docs record `P6-N005` as `local-only/docs/tests`.

## Boundaries

No live VPS command, SSH command, package rebuild/apply on VPS, service
restart/deploy, public exposure, public OpenAPI publication, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

Latest AMN2 VPS-smoked/package head remains `0de7a77`. AMN2 `4cde273` is
local-only and not package-rebuilt or VPS-smoked.

## TDD evidence

RED:

```text
.\scripts\test.ps1 tests\services\test_fresh_install_wizard.py tests\services\test_public_productization_boundaries.py -q
result: 3 failed, 15 passed
```

Expected failures:

- missing `asset_path_preflight`;
- missing `package-asset-path-preflight`;
- missing `route_order_drift_guard`.

GREEN focused:

```text
.\scripts\test.ps1 tests\services\test_fresh_install_wizard.py tests\services\test_public_productization_boundaries.py -q
result: 18 passed
```

Expanded:

```text
.\scripts\test.ps1 tests\services\test_fresh_install_wizard.py tests\services\test_public_productization_boundaries.py tests\services\test_integration_status_service.py tests\api\test_api_integration_status.py tests\web\test_web_integration_status.py -q
result: 26 passed, 1 StarletteDeprecationWarning
```

Full AMN2:

```text
.\scripts\test.ps1 -q
result: 723 passed, 1 StarletteDeprecationWarning
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

- `FI-M004` package asset path preflight;
- `P6-N005` OpenAPI/taxonomy route-order drift guard.

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
P6-M005 alone as local-only/docs/tests if we want multi-instance/port/IPAM conflict model before closeout
```
