# Phase 10 plan device quota admin UI

Date: 2026-07-11.

Status: `completed-code-tested-reviewed-pushed-local-only`.

## Product Evidence

AMN2 commit `ecf8563` adds the first operator UI for the existing
`plans.max_devices` enforcement:

- authenticated `GET /plans` lists active and inactive plans;
- the page shows the global `MAX_DEVICES_PER_USER`, configured plan quota, and
  the effective minimum used by order approval;
- `POST /plans/{plan_id}/device-quota` accepts a positive integer or an empty
  value;
- an empty value stores `NULL` and restores the global fallback;
- the write is session-authenticated, CSRF-protected, validated, transactional,
  and recorded as `web_plan_device_quota_update` in `admin_actions`;
- the route has the explicit `web.plans.device_quota_update` surface policy and
  belongs to the named Phase 10 plan quota write contour;
- no user, order, device, peer, VPN config, Telegram runtime, or VPS state is
  changed by this local slice.

The client contract remains one dedicated peer and one `.conf` per physical
device. `owner_shared` remains an admin-only exception and is not used to
implement a customer device quota.

## Verification

```text
new quota tests: 6 passed, 1 warning
expanded access/web regression: 69 passed, 1 warning
final security/quota scope: 38 passed, 1 warning
full suite: 829 passed, 1 skipped, 1 warning
git diff --check: passed
diff review: passed, no blocking findings
```

The full suite initially exposed the two new routes missing from the runtime
binding registry and then the new behavior missing from the strict allowlist.
Both guards were fixed explicitly; the final full run is green.

## Runtime Boundary

```text
AMN2 branch=codex-vps-test-prep
AMN2 product commit=ecf8563
AMN2 push=done
VPS overlay=1c7fb78
ecf8563 package=false
ecf8563 upload=false
configured VPS plan quota rows=0
global fallback=active
```

## Next Step

```text
START_PHASE10_ECF8563_VPS_PACKAGE_PREP_SLICE
```

Package preparation must reproduce focused and full tests from the extracted
source. Upload, service restart, and live quota configuration remain separate
controlled actions.
