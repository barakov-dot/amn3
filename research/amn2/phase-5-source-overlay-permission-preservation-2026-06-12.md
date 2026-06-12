# Phase 5 P5-C005 Source-Overlay Permission Preservation

Date: 2026-06-12

Status: completed-local-tooling-fix

Scope:

- AMN3 local package tooling and tests only.
- No AMN2 runtime code change.
- No package rebuild or package apply.
- No live VPS command, SSH command, deploy/restart, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action or secret-bearing evidence publication.

## Reason

`P5-C003` proved the `de25576` rollout on the disposable test VPS, but the inherited `amn2_apply_source_zip.sh` temporarily broke service-mode permissions. The script streamed a tar archive rooted at `.` from a staging directory created under `umask 077`:

```text
tar -C "$STAGING" -cf - . | tar -C "$AMN2_DIR" -xf -
```

That pattern can transfer staging-root metadata onto `/opt/amn2` and leave service-mode paths too restrictive for the `amneziya` systemd user. The live gate repaired permissions manually; this local follow-up removes the need for that repair in future rebuilt kits.

## Changes

Changed:

- `scripts/vps/amn2_apply_source_zip.sh`
- `tests/test_amn2_apply_source_zip.py`
- operator status/runbook docs

The apply script now overlays staging children with Python instead of tarring `.` into the target. The target root directory metadata is preserved. Copied source entries are normalized for service mode:

- copied directories: group-readable/executable;
- regular files: group-readable;
- executable files: executable for owner/group;
- copied entries inherit the target directory group where `os.chown` is available.

The script records:

```text
permission_strategy=target-root-metadata-preserved
copied_root_entries=<count>
```

The historical package `dist/amn2-vps-update-and-smoke-kit-de25576.zip` remains the immutable evidence artifact for `P5-C003`. Do not reuse it for a future source apply; rebuild a new kit from the corrected `scripts/vps/amn2_apply_source_zip.sh`.

## Verification

RED:

```text
python -m unittest discover -s tests -p test_amn2_apply_source_zip.py -v
result: 1 failed, 1 passed
expected failure: dangerous root-entry tar overlay pattern was still present
```

Additional RED:

```text
python -m unittest discover -s tests -p test_amn2_apply_source_zip.py -v
result: 1 failed, 1 passed
expected failure: obsolete `require_cmd tar` dependency was still present after the Python overlay replacement
```

GREEN:

```text
python -m unittest discover -s tests -p test_amn2_apply_source_zip.py -v
result: 2 passed
```

The live regression test uses a temporary local fake target through Git Bash. It verifies that the apply script completes, preserves the target directory mode, leaves `.env` and `data/` present, writes `.amn2_source_overlay_commit`, and keeps copied source entries group-readable. It does not contact the VPS.

## Next Recommendation

`P5-C004` Secret handoff protocol: document the operator-local channel for Telegram token, web secret, server config and bootstrap values before any future fresh secret/server setup.
