# AMN2 VPS Update And Smoke Kit 3c91601

Date: 2026-07-14.

Purpose: private source-overlay candidate for `amn2/codex-vps-test-prep`
commit `3c91601 Cascade physical device revocation`. Package preparation does
not authorize upload, source apply, database migration, service restart,
device revoke, config or peer action, or Telegram bot polling.

```text
source_commit=3c916015c10add37886370d04af70f0343f7f691
previous_vps_overlay=1c7fb78
source_zip=amn2-codex-vps-test-prep-3c91601-source.zip
source_zip_sha256=5AD92A3A9D944825FEFDFEB4D56BDDBBB05390036E19E5AD197288C73812B0CB
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
telegram_bot_runtime=inactive_disabled_not_started
drift_auto_remediation=false
public_enrollment_route=false
live_cascade_revoke=false
offline_editable_install=fail_closed_exact_diagnostic_fallback
```

## Included source delta

The candidate advances the production overlay by nine commits and contains:

- authenticated plan device-quota administration;
- AWG2 H1-H4 uint32/range and non-overlap validation;
- deterministic read-only Desired / Observed / Drift diagnostics;
- stable generated Device Passport identities;
- hash-only, TTL, atomic Device Enrollment Tickets and lifecycle evidence;
- authenticated read-only web diagnostics;
- OperationPlan-based physical-device cascade revoke with stale-access guards.

These capabilities do not open public enrollment, drift auto-remediation,
hardware attestation, MDM, broad protocol parity or Telegram polling.

## Boundaries

The source overlay preserves `.env`, `servers.yml`, `data` and `venv`. Both
product-write flags must remain false during package verification. No plan
quota write, ticket claim, credential issue/rotate/revoke, physical-device
revoke, peer/config generation or delivery, Telegram API request or listener
exposure is authorized by this package.

The apply tool forces pip into no-index mode. It accepts the exact known
missing-`setuptools>=69` offline build-isolation diagnostic only after imports
resolve directly to `/opt/amn2/app/__init__.py`; all other failures remain
fatal.

Before production apply, the exact rollout gate must create source and SQLite
snapshots, run schema initialization and read-only diagnostics against a cloned
database, define automatic rollback, and prove that the AWG container remains
running. Only a web-service restart may be considered, and only when required
by the source-overlay apply.

## Future source-overlay gate

Only after a separate exact approval:

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-3c91601.zip.sha256.txt
test ! -e /root/amn2-vps-update-and-smoke-kit-3c91601
mkdir -m 700 /root/amn2-vps-update-and-smoke-kit-3c91601
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-3c91601.zip /root/amn2-vps-update-and-smoke-kit-3c91601
cd /root/amn2-vps-update-and-smoke-kit-3c91601
sha256sum -c amn2-codex-vps-test-prep-3c91601-source.zip.sha256.txt
export VPS_APPLY_ENABLED=false
export OPERATOR_DEVICE_CREATE_ENABLED=false
export AMN2_DIR=/opt/amn2
export AMN2_SOURCE_ZIP=/root/amn2-vps-update-and-smoke-kit-3c91601/amn2-codex-vps-test-prep-3c91601-source.zip
export AMN2_EXPECTED_SOURCE_SHA=5AD92A3A9D944825FEFDFEB4D56BDDBBB05390036E19E5AD197288C73812B0CB
export AMN2_EXPECTED_SOURCE_COMMIT=3c91601
bash ./amn2_apply_source_zip.sh
```

Any upload, source apply, database migration, web restart, API token smoke,
live revoke or Telegram runtime action remains a separate named gate. Return
only safe summaries; never publish environment files, tokens, authorization
headers, token hashes, administrator IDs, private keys, PSK, `.conf`, QR or
`vpn://` payloads.
