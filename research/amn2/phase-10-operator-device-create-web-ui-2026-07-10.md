# Phase 10 operator device create web UI

Date: 2026-07-10.

Status: `completed-code-pushed-local-gate`.

## Source

```text
base=e7f6246
branch=codex-vps-test-prep
commit=466e0bc
subject=Add operator device web workflow
push=completed
```

## Product Result

The private web-admin user detail page now includes an operator device creation
form. It uses the existing CLI orchestration and
`AccessService.create_operator_device(...)`; no second peer/device creation
implementation was added.

The form provides server, device name, duration, config version and explicit
`local|remote-ssh` execution target. Dry-run performs no database, peer or
artifact mutation. Apply requires:

```text
authenticated web-admin session
valid CSRF token
active explicit owner
configured authorized ADMIN_TELEGRAM_IDS actor
VPS_APPLY_ENABLED=true
OPERATOR_DEVICE_CREATE_ENABLED=true
exact one-device confirmation
```

The new `OPERATOR_DEVICE_CREATE_ENABLED` setting defaults to `false`, so a broad
VPS apply window cannot silently enable this route. The config artifact path is
generated server-side under the database runtime directory. HTML returns safe
metadata only and never includes config text, private key or PSK.

Remote-applied/local-failed results return fixed HTTP `409` text and structured
redacted web audit metadata; recovery text is not reflected to the client. The
route is bound to surface policy `web.devices.create_operator` as operator-only
remote execution with live retest required.

## Verification

```text
RED=5 expected failures for missing form route and DI hooks
focused_initial=5 passed, 1 warning
focused_settings=45 passed, 1 warning
expanded=99 passed, 1 skipped, 1 warning
security_policy=38 passed, 1 warning
full_initial=770 passed, 1 skipped, 2 expected policy-binding failures, 1 warning
full_final=772 passed, 1 skipped, 1 warning
final_security_web_hygiene=41 passed, 1 warning
toolchain=AMN2 toolchain ok CPython 3.12.x
diff_check=passed
cached_diff_check=passed
```

The skipped test is the POSIX `0600` assertion on Windows. The warning is the
known FastAPI/Starlette test-client deprecation warning.

## Boundary

No VPS command, SSH command, package build/upload/apply, source overlay, service
restart, peer/user mutation, config generation/delivery, public exposure,
Telegram action or secret publication was performed by this product slice.

The current VPS overlay remains `e7f6246`. Commit `466e0bc` is pushed but not
packaged or deployed. Android TV import/connect and device `8` acceptance remain
`pending_physical_device`.

## Next Step

```text
START_PHASE10_466E0BC_VPS_PACKAGE_PREP_SLICE
```

After package verification, upload/source-overlay and any web service activation
must remain separately reviewed live gates. The following product lane is the
scoped integration/API-key registry, then the Telegram operator workflow.
