# Phase 10 34b3b43 private VPS source-overlay upload gate review

Date: 2026-07-11.

Decision: `APPROVE-CONDITIONAL-AWAITING-EXACT-LIVE-PHRASE`.

This review is local-only. It performed no SSH command, upload, source apply,
service restart or Telegram action.

## Inputs

```text
current_confirmed_vps_overlay=6f475e6
candidate_source=34b3b43a87fb673cb966a578d3d5e48533b541fa
package_sha256=385EAC3DC53B9E9C1EA35F168B01D545177FEC459D948239F93B4D40A64D499C
source_sha256=97D7676B9C349877A8A51C971599C0C886616E9BBB6472749C0C695209BE5179
package_status=local-verified-not-uploaded
candidate_full_tests=796_passed_1_skipped_1_warning
```

The source delta contains modified Telegram operator, repository and security
code plus three new typed operator services. It contains no deleted path and no
database schema migration.

## Review Finding

`amn2_apply_source_zip.sh` validates the source checksum, rejects forbidden
archive entries, preserves `.env`, `servers.yml`, `data` and `venv`, normalizes
permissions and runs import checks. It does not create an automatic pre-apply
backup and overlays tracked files without deleting stale tracked paths.

The gate is therefore approved only with an explicit rollback bundle created
before source apply. The bundle must remain private on the VPS and must never be
copied into repository evidence.

## Exact Allowed Scope

1. Recheck the local package SHA256.
2. Run a read-only VPS preflight confirming overlay `6f475e6`, private web
   service health, loopback listeners and both write gates false or unset.
3. Upload only the package ZIP and its SHA256 file to a private root-owned path.
4. Verify the remote package checksum before extraction.
5. Create a mode `0700` rollback directory containing:
   - mode `0600` tar archive of tracked source roots `.env.example`,
     `.gitattributes`, `.gitignore`, `README.md`, `app`, `deploy`, `docs`,
     `pyproject.toml`, `scripts` and `tests`;
   - current `.amn2_source_overlay_commit` marker when present;
   - SQLite backup made through the SQLite backup API, mode `0600`;
   - SHA256 values and a safe manifest containing paths/counts only.
6. Extract the candidate kit into a new mode `0700` directory and verify the
   source ZIP checksum.
7. Apply tracked source with `VPS_APPLY_ENABLED=false` and
   `OPERATOR_DEVICE_CREATE_ENABLED=false`.
8. Run the read-only loopback API smoke with expected commit `34b3b43`.
9. Restart only `amneziya-web.service`, then verify active state,
   `127.0.0.1:3030`, login HTTP `200` and protected routes.
10. Keep Telegram bot service stopped. No `getMe`, polling or live send belongs
    to this gate.

## Stop Criteria

Stop before apply when the current overlay is not `6f475e6`, a checksum does
not match, either write gate is enabled, the rollback bundle cannot be created
and verified, disk space is insufficient, or an unexpected public listener is
present.

Rollback after apply when source/import installation fails, API smoke fails,
authentication expectations differ, the web service does not become active,
login is not `200`, protected routes are exposed, write gates change, or any
secret-bearing output would be required.

## Rollback Scope

1. Stop only `amneziya-web.service`.
2. Remove only the reviewed tracked roots under resolved `/opt/amn2`; preserve
   `.env`, `servers.yml`, `data`, `venv`, `vps-smoke` and Git metadata.
3. Restore the tracked-source tar and prior overlay marker.
4. Run editable install and import checks from the restored source.
5. Restore the SQLite backup only if schema/data integrity changed; otherwise
   preserve the live database.
6. Start the private web service and repeat the read-only smoke with expected
   commit `6f475e6`.
7. Record safe status only. Do not publish rollback archives or secrets.

## Excluded

Telegram bot activation, Telegram token use, credential issue/rotate/revoke,
peer/user mutation, config generation/delivery, Android TV device `8` action,
public exposure, firewall/reverse-proxy/TLS change, reboot and destructive
provider action remain excluded.

## Exact Approval Phrase

```text
APPROVE PHASE10_34B3B43_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_AND_READ_ONLY_SMOKE_WITH_ROLLBACK
```

Without that phrase the result remains review-only and no live command is
authorized.
