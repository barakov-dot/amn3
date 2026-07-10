# Phase 10 integration API key registry

Date: 2026-07-10.

Status: `completed-code-tested-pushed-local-gate`.

## Fresh Upstream Review

```text
kyoresuas_amnezia_api_main=96a1f54c5942f7d8572e743ac90a018b60ce483a
kyoresuas_delta_since_2026_06_14=none
prvtpro_amnezia_web_panel_previous=a62f958_v1.4.4
prvtpro_amnezia_web_panel_current=dd8bda3_v1.5.0
prvtpro_release_date=2026-07-09
```

KYORESUAS remains the taxonomy signal for a typed API shared by a panel, bot,
billing and multi-server controller. PRVTPRO v1.5.0 adds current product signals
for one-time API tokens, admin bot workflows, multi-instance management,
protocol backup/migration, NGINX/TLS and WARP.

Accepted as independent AMN2 requirements:

- typed integration identity for monitoring, operator automation, Telegram bot
  and web panel;
- explicit credential purpose;
- one-time raw token display and hash-only storage;
- private operator issue, rotation and revoke workflow;
- owner/scopes/expiry/lineage/audit preservation;
- future Telegram operator and multi-instance/IPAM product candidates.

Rejected or deferred:

- PRVTPRO GPL code, templates, styles, managers and workflow implementation;
- admin-equivalent bearer access to every route;
- public tunnels, raw config editor and public config sharing;
- backup/restore apply, WARP, NGINX mutation, billing and secret-read scopes;
- KYORESUAS single shared `x-api-key` model.

## Product Result

```text
amn2_base=3ed20ab
amn2_commit=6f475e6
branch=codex-vps-test-prep
push=completed
schema=integration_kind|purpose
allowed_kinds=monitoring|operator_automation|telegram_bot|web_panel
private_web_registry=implemented
issue=typed_purpose_scoped_expiring_one_time_raw
rotate=preserve_owner_kind_purpose_scopes_create_new_revoke_old
revoke=idempotent_safe_metadata
statuses=active|rotation-due|expired|revoked
legacy_migration=operator_automation|legacy-api-access
surface_policy=web.api_tokens.rotate_bound
```

No raw token, token hash, Authorization header, config payload, private key or
PSK is stored in safe web lists or audit metadata.

## Verification

```text
RED=import_error_API_TOKEN_INTEGRATION_KINDS
scoped=73_passed_1_warning
expanded_initial=385_passed_3_expected_stale_expectations_1_warning
expanded_final=388_passed_1_warning
full=774_passed_1_skipped_1_warning
diff_check=passed
cached_diff_check=passed
```

The skip is the existing POSIX-only permission assertion on Windows. The
warning is the existing FastAPI/Starlette TestClient deprecation warning.

## Boundary

At product-code closure this slice performed no VPS/SSH command, package upload,
source overlay, service restart, peer/config action, Android TV action, public
exposure or live Telegram action. The later approved activation gate packaged,
smoked and promoted private loopback overlay `6f475e6`; evidence is
`research/amn2/phase-10-6f475e6-vps-source-overlay-web-activation-2026-07-10.md`.

Android TV device `8` remains
`server-side-prepared-awaiting-device-acceptance`; import/connect, handshake
and traffic verification remain pending physical access.

## Next Product Slice

```text
START_PHASE10_TELEGRAM_OPERATOR_READ_ONLY_STATUS_SLICE
```

Add a local-only, service-backed Telegram operator status workflow with
authorization, safe aggregate output and tests. Do not start the live bot or
open Telegram/public/VPS write gates in that slice.
