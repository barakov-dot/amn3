# Phase 2 Post-PSK-stdin VPS Smoke Evidence 2026-06-05

Purpose: record the real VPS read-only update/smoke after PR #8 merged safer `--preshared-key-stdin` handling into `amn2/codex-vps-test-prep`.

## Scope

```text
amn2 branch: codex-vps-test-prep
amn2 head: 568c611 Merge pull request #8 from barakov-dot/codex/preshared-key-stdin
source zip: dist/amn2-codex-vps-test-prep-568c611-source.zip
source sha256: 30319240D2D887239A3D57417A6777CBD7AFE34D97093831609939822C92B243
VPS_APPLY_ENABLED: false
live apply/revoke: not run
```

No `.env`, `servers.yml`, raw API token, Authorization header, token hash, private key, PSK, raw peer public key, full config, QR payload, `vpn://` link or full log was published.

## Update

Operator downloaded `amn2-vps-update-and-smoke-kit-568c611.zip` from public AMN3 `master` and verified package checksum before extraction.

The source zip checksum passed:

```text
amn2-codex-vps-test-prep-568c611-source.zip: OK
```

The update script emitted a first-line shell warning caused by a UTF-8 BOM in the generated kit script, then continued and completed successfully:

```text
source_update_status=passed
target=/opt/amn2
source_commit=568c611
safe_log_dir=/opt/amn2/vps-smoke/source-update-20260605T162708Z
next=run ./amn2_api_loopback_smoke.sh from /opt/amn2
```

AMN3 follow-up removed the BOM from generated kit shell/doc files and republished the same source zip unchanged; current package SHA is recorded in the status docs.

## Runtime Confirmation

```text
.amn2_source_overlay_commit: 568c611
app_cli_file: /opt/amn2/app/cli.py
smoke_paths: ['servers', 'integration_status', 'server_summary', 'metrics_summary', 'users_summary']
```

## API Loopback Smoke

```text
run_id: 20260605T162742Z
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260605T162742Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260605T162742Z.tar.gz
```

Safe summary:

```text
VPS verdict: pass
branch/head:
  not a git checkout
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
```

## Result

Status: `read-only-vps-smoke-pass` for stable `568c611`.

This confirms the post-PSK-stdin stable source can be overlaid on `/opt/amn2` and passes the read-only API smoke with `VPS_APPLY_ENABLED=false`.

This does not unlock broad write API, public/self-service config delivery, API `config:read`, `/api/clients` CRUD, backup/import/reboot routes, Local Agent mutations or public web/API exposure.
