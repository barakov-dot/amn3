# AMN2 Phase 6 Config Link And Entitlement Boundary

Дата: 2026-06-13.

Статус: `local-only-code-tests-docs-complete`.

## Scope

Закрыта paired local-only задача:

- `P6-C002-design`: short one-tap tokenized config-link boundary.
- `P6-I006`: commercial entitlement/audit boundary.

Это не открывает live config delivery. `P6-C002` как реальный config delivery
gate остается critical gated/deferred.

## AMN2 Change

AMN2 branch:

```text
codex-vps-test-prep
```

AMN2 commit:

```text
d96112c Add config link entitlement boundary
```

Pushed to:

```text
amn2/codex-vps-test-prep
```

## What Changed

Added a machine-checkable productization boundary for future tokenized config
links:

- short-link runtime disabled by default;
- real config delivery disabled by default;
- named gate: `P6-C002 Config delivery gate`;
- token material: opaque random token;
- storage: hash-at-rest only;
- raw token return policy: return once at issue time only;
- purpose: config delivery only;
- audience binding: order + user + device;
- one-time use;
- default TTL: 15 minutes;
- Telegram one-tap copy target: short link only after gate, not a long full
  import link.

Added a commercial entitlement/audit boundary:

- payment provider disabled;
- entitlement write API disabled;
- automatic activation disabled;
- config delivery decoupled from payment;
- manual operator review required;
- safe audit fields limited to entitlement/order/operator/decision/reason/time;
- raw payment payload, provider secrets, client config body, VPN import link,
  QR code, key material and Telegram identity are forbidden in audit/evidence.

Added blocked-future surface policies:

- `api.entitlements.manual_review.blocked`;
- `api.config_links.issue.blocked`;
- `public_token.config_link.redeem.blocked`.

Updated `/api/integration/status` and web `/integration-status`:

- latest VPS-smoked/package head is now `b3102db`;
- latest live smoke run is `20260613T154826Z`;
- source update run is `20260613T154511Z`;
- current local AMN2 head is ahead of latest VPS-smoked package after this
  local-only commit;
- next local recommendation is `P6-I007 interactive fresh-install
  wizard/bootstrap automation`.

## Verification

First attempted local pytest with system Python:

```text
python -m pytest ...
result: failed, pytest unavailable on system Python
```

Then attempted with `.codex_deps` on Python 3.14:

```text
result: collection failed because .codex_deps binary wheels are CPython 3.12
```

Final supported local run used bundled CPython 3.12.13:

```text
PYTHONPATH=.codex_deps python -m pytest \
  tests/services/test_productization_boundary.py \
  tests/services/test_integration_status_service.py \
  tests/api/test_api_integration_status.py \
  tests/security/test_surface_policy.py \
  tests/web/test_web_integration_status.py

result: 37 passed, 1 StarletteDeprecationWarning
```

`git diff --check` passed before commit.

## Safety Boundary

No live VPS command, SSH command, package apply/rebuild on VPS, service
restart/deploy, public exposure, real config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive VPS
action, payment provider integration, Telegram token use, live bot send,
Telegram profile mutation, secret-bearing evidence publication or upstream/GPL
code copy was performed.

`VPS_APPLY_ENABLED=false` remains the default.

## Plan Result

`P6-I006` is removed from the active/proposed Phase 6 plan as completed.

`P6-C002` remains in critical gated/deferred plan for real config delivery,
public token redeem and short-link issue/apply runtime.

Next practical recommendation:

```text
P6-I007 interactive fresh-install wizard/bootstrap automation
```

Alternative grouped recommendation:

```text
P6-I007 + P6-N001
```

Only if the operator wants the clean installer plan and public docs/API taxonomy
to be shaped together. Both remain local-only/docs/tests unless separate named
live/public gates are opened.
