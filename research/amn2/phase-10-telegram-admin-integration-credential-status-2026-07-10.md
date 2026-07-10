# Phase 10 Telegram admin integration credential status

Date: 2026-07-10.

Status: `completed-code-tested-pushed-local-only`.

## Product Result

```text
amn2_base=4cf93f8
amn2_commit=34b3b43
branch=codex-vps-test-prep
push=completed
callback=ADMIN_INTEGRATIONS_CALLBACK
authorization=telegram_admin_and_workflow_is_admin
data_source=list_api_tokens_for_admin
typed_allowlist=name|owner_label|integration_kind|purpose|scopes|lifecycle|expires_at|last_used_at|created_at
excluded=token_id|owner_user_id|raw_token|token_hash|revoke_reason|rotation_lineage
lifecycle=revoked|expired|rotation-due|active
mutations=none
audit_action=bot_admin_integrations_read
surface_policy=bot.admin.integrations_secret_adjacent_read
```

The Telegram admin menu now exposes a localized integration credential
lifecycle view. It uses the existing hash-free registry query and an additional
typed allowlist. The callback provides no issue, rotate or revoke action.

## Verification

```text
RED=missing_operator_credential_status_service|missing_handler
focused=140_passed
expanded=241_passed_1_warning
full=796_passed_1_skipped_1_warning
diff_check=passed
cached_diff_check=passed
progress_harness_tests=12_passed
progress_harness_scope=product_and_docs_passed
```

The skip and warning are the existing Windows POSIX-permission skip and
FastAPI/Starlette TestClient deprecation warning.

## Boundary

No raw token or token hash was read or rendered. No credential issue, rotation
or revoke, Telegram bot startup, live Telegram send, VPS/SSH command, package
upload, source overlay, service restart, peer/config action, Android TV action
or public exposure was performed. VPS remains on `6f475e6`; `34b3b43` is Git-only.

Android TV device `8` remains pending physical acceptance and does not block
this local-only lane. PRVTPRO and KYORESUAS remain product signals only; no
upstream code or secrets were copied.

## Next Engineering Slice

```text
START_PHASE10_34B3B43_VPS_PACKAGE_PREP_SLICE
```

Build and verify a private source/update package for current AMN2 head before
any separate upload, bot runtime or live Telegram gate.
