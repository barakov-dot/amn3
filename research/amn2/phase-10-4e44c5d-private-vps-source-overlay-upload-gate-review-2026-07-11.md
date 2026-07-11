# Phase 10 4e44c5d private VPS source-overlay upload gate review

Date: 2026-07-11.

Decision: `APPROVE-CONDITIONAL-AWAITING-EXACT-LIVE-PHRASE`.

This review performed local package/code inspection and read-only VPS
preflight only. It did not upload or extract a package, change source, stop or
restart a service, call the Telegram API, run polling or mutate a peer/device.

```text
phase9_progress_harness=14_passed|docs_only_review_scope_passed
```

## Inputs

```text
current_vps_overlay=34b3b43
candidate_source=4e44c5d36f64d01f2d1afae5c6fd72e37c3dc22d
package_sha256=28447A7385A24BC01221DED073FAE1B4C6E583BBD6824F64E4D2DF4D0B294F13
source_sha256=4E34EB736775749467BDD5E0DA20758F46B8F10224871091C96778E960A040FA
package_status=local-verified-pushed-not-uploaded
candidate_full_tests=810_passed_1_skipped_1_warning
```

The source delta from `34b3b43` contains two added files and two modified
files:

```text
A app/bot/controlled_smoke.py
M app/cli.py
M app/main.py
A tests/bot/test_controlled_smoke.py
```

There is no deleted path and no database schema migration. This is compatible
with the source overlay mechanism, which copies tracked roots but does not
remove stale files.

## Read-Only VPS Preflight

```text
source_overlay=34b3b43
web_active=active
web_enabled=enabled
web_login_http=200
web_loopback_listener=true
public_3030_3040_listener=false
api_3040_listener=false
bot_active=inactive
bot_enabled=disabled
bot_process=false
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
db_integrity=ok
users_count=6
orders_count=8
devices_count=8
admin_actions_count=43
root_free_bytes=3268530176
project_size_bytes=163254213
db_size_bytes=159744
rollback_root=present_0700_root_root
candidate_remote_present=false
venv_python=3.12.3
required_tools=present
```

The private package, one source snapshot, SQLite backups and temporary clone
fit comfortably in the available root filesystem space.

## Android TV Pre-Acceptance Baseline

```text
device8_exists=true
device8_name=Neobyatnaya-AMNZ-N-android-tv-01
device8_status=active
device8_config_version=amneziawg_v2
device8_config_material_status=available
configured_server_name=local
configured_runtime=docker
configured_container=amnezia-awg2
container_status=running
device8_peer_runtime_present=true
runtime_peer_count=13
device8_handshake_present=false
device8_rx_bytes=0
device8_tx_bytes=0
```

`local` is the configured AMN2 server label for the running local Docker
container, not a different VPS. Device `8` is consistently linked to that
server and its peer is present in the live container. The remaining proof is
the physical Android TV import/connect handshake and traffic test.

Private client artifact:

```text
private-artifacts/phase10/android-tv-single/20260707T200605Z/Neobyatnaya-AMNZ-N-android-tv-01.conf
```

The file content was not printed. If Android displays `Сервер 1`, manual rename
remains the accepted client-side fallback; server-side naming and peer mapping
are already consistent.

## Review Findings

`amn2_apply_source_zip.sh` validates the source checksum, rejects forbidden
archive entries, preserves `.env`, `servers.yml`, `data` and `venv`, normalizes
permissions and performs editable-install/import checks. It does not create an
automatic pre-apply source or SQLite backup.

`amn2_api_loopback_smoke.sh` creates and revokes temporary API tokens and writes
read-audit events. It must not run against the production database in this
gate. The reviewed scope binds both `DATABASE_PATH` and `AMN2_DB` to a private
SQLite clone and verifies the production logical database digest before and
after.

The editable install must use `PIP_NO_INDEX=1` and
`PIP_DISABLE_PIP_VERSION_CHECK=1`, preventing an unexpected dependency
download during source activation.

## Exact Allowed Live Scope

Only after the exact phrase below:

1. Recheck local package SHA256 and this read-only VPS baseline.
2. Upload only the package ZIP and checksum file to `/root`, mode `0600`.
3. Verify the remote outer checksum before extraction.
4. Create a unique mode `0700` rollback directory under
   `/root/amn2-rollbacks`.
5. Stop only `amneziya-web.service`; keep the bot inactive and disabled.
6. With web and bot stopped, create and verify:
   - mode `0600` tar snapshot of `.env.example`, `.gitattributes`,
     `.gitignore`, `README.md`, `app`, `deploy`, `docs`, `pyproject.toml`,
     `scripts` and `tests`;
   - prior `.amn2_source_overlay_commit` marker;
   - mode `0600` SQLite backup through the SQLite backup API;
   - safe path/count/SHA256 manifest only.
7. Extract the package into a new mode `0700` directory and verify the source
   checksum and expected commit binding.
8. Apply source with both write gates false, `PIP_NO_INDEX=1` and expected
   source `4e44c5d`.
9. Verify imports plus `bot controlled-start-smoke --help`; do not call the
   Telegram API.
10. Make a separate private mode `0600` SQLite clone from the frozen production
    DB. Run the loopback API smoke as `amneziya` with both `DATABASE_PATH` and
    `AMN2_DB` bound to that clone, loopback port `3040` only.
11. Confirm the production logical DB digest and aggregate counts are unchanged.
12. Start only `amneziya-web.service`; verify active state, login HTTP `200`,
    protected route behavior, loopback `127.0.0.1:3030`, closed public
    `3030/3040` listeners and bot process absence.
13. Preserve private rollback/evidence material; remove only the verified
    temporary smoke clone after success.

## Stop And Rollback Criteria

Stop before apply on overlay mismatch, checksum mismatch, enabled write gate,
active bot, unexpected listener, insufficient disk, rollback creation or
verification failure, candidate path collision, or package binding mismatch.

Rollback after apply on install/import failure, API clone-smoke failure,
production DB digest change, web startup/login/auth/listener failure, write-gate
change, bot activation or secret-bearing output requirement.

Rollback sequence:

1. Stop the private web service and any temporary API process.
2. Remove only the reviewed tracked roots from resolved `/opt/amn2`; preserve
   `.env`, `servers.yml`, `data`, `venv`, `vps-smoke` and Git metadata.
3. Restore the tracked-source tar and prior overlay marker.
4. Restore the SQLite backup if its logical digest changed.
5. Run offline editable install and import checks from restored source.
6. Start the web service and repeat private web/listener checks for overlay
   `34b3b43`.
7. Keep the bot inactive and disabled; record safe status only.

## Excluded

Telegram `getMe`, polling, live send, persistent bot activation, credential
issue/rotation outside the disposable clone, production peer/user/device
mutation, config generation/delivery, Android TV device `8` mutation, public
exposure, firewall/reverse-proxy/TLS change, reboot and provider action remain
excluded.

## Exact Approval Phrase

```text
APPROVE PHASE10_4E44C5D_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_AND_CLONE_DB_API_WEB_SMOKE_WITH_ROLLBACK
```

Without that phrase the decision remains review-only and no live upload or
apply is authorized.
