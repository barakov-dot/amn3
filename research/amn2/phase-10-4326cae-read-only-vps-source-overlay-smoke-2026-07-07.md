# Phase 10 AMN2 4326cae read-only VPS source-overlay smoke

Date: 2026-07-07.

Status: `read-only-vps-smoke-pass`.

Scope: exact approved source-overlay upload/smoke gate for AMN2
`codex-vps-test-prep` at `4326cae Save fresh installer recovery work`.

Target identity: operator-local SSH target, redacted from evidence.

## Decision

```text
approval_phrase: APPROVE READ_ONLY_VPS_SOURCE_OVERLAY_UPLOAD_GATE_FOR_AMN2_4326CAE
scope: read-only VPS source-overlay upload and loopback smoke
target_class: existing AMN2 VPS
AMN2_source_commit_short: 4326cae
package: dist/amn2-vps-update-and-smoke-kit-4326cae.zip
package_sha256: FEFD9D4AE91764AB9649284E26F0F303A2F43BAECD8A511B0E492E8D9315D2F1
source_sha256: 7F91506F2C652520940C79C951A3B329964956DD1E247152E34A0FB43BAAAB06
result: read-only-vps-smoke-pass
VPS_APPLY_ENABLED: false
public_exposure_changed: no
config_delivery_performed: no
write_api_enabled: no
Local_Agent_mutation: no
backup_import_reboot: no
production_peer_user_mutation: no
destructive_provider_action: no
```

## Preflight

Plain SSH attempts without an explicit identity failed with
`Permission denied`. Using the dedicated operator-local AMN2 key succeeded.

```text
ssh_status: connected
amn2_dir: present
source_overlay_commit_before: 187949bffb927a0a6d6c1f260fc0bb9ebb972447
VPS_APPLY_ENABLED: present and not published
```

## Package Upload And Verify

```text
package_upload: passed
package_sha_check: passed
source_sha_check: passed
package_extract_status: passed
package_entries: 5
```

Package entries on the target:

```text
AMN2_VPS_UPDATE_AND_SMOKE_4326cae.ru.md
amn2_apply_source_zip.sh
amn2_api_loopback_smoke.sh
amn2-codex-vps-test-prep-4326cae-source.zip
amn2-codex-vps-test-prep-4326cae-source.zip.sha256.txt
```

## Source Overlay

```text
source_update_run_id: 20260707T195143Z
source_update_status: passed
target: /opt/amn2
source_commit: 4326cae
source_sha: 7F91506F2C652520940C79C951A3B329964956DD1E247152E34A0FB43BAAAB06
safe_log_dir: /opt/amn2/vps-smoke/source-update-20260707T195143Z
source_overlay_commit_after: 4326cae
VPS_APPLY_ENABLED: false
```

## Read-Only API Smoke

```text
api_smoke_run_id: 20260707T195217Z
VPS_verdict: pass
branch/head: not a git checkout
preflight_status: skipped
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
missing_bearer_http: 401
wrong_scope_http: 403
revoked_token_http: 401
listener_status: passed
audit_status: passed
checked_routes: 6
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260707T195217Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260707T195217Z.tar.gz
```

## Listener, Audit And Sync

```text
listener_rows: 1
expected_host: 127.0.0.1
host: 127.0.0.1
loopback_only: yes
api_read_rows: 5
audit_safe: yes
server_db_sync: passed
server_name: local
runtime: docker
source_overlay_after: 4326cae
VPS_APPLY_ENABLED: false
```

## Boundary

The gate performed:

- SSH to the existing AMN2 VPS;
- package upload to `/root`;
- package and source checksum verification;
- scoped package extraction under `/root/amn2-vps-update-and-smoke-kit-4326cae`;
- source overlay update of `/opt/amn2` to AMN2 `4326cae`;
- read-only loopback API smoke on `127.0.0.1:3040`.

The gate did not perform:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- API `config:read`;
- `/api/clients` write CRUD;
- config delivery, `.conf`, QR or `vpn://`;
- public web/admin exposure;
- public API `3040`;
- domain, HTTPS, reverse proxy or firewall changes;
- Local Agent write/config mutations;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider action;
- secret-bearing evidence publication;
- Telegram token use, live bot send or Telegram profile mutation.

## Next Recommendation

Recommended next Phase 10 step:

```text
SELECT_NEXT_PHASE10_PRODUCT_SLICE_AFTER_AMN2_4326CAE_VPS_SMOKE_PASS
```

Keep config generation/delivery, peer creation and live apply gates closed until
their own exact named approval phrases are provided.
