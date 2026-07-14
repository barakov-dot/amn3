# Phase 11: 801f8c3 private overlay rollout gate review

Date: 2026-07-14.

Decision: `READY-AWAITING-EXACT-APPROVAL`.

This review prepares the exact private source-overlay gate. It did not contact
the VPS, upload a package, stop a service, write SQLite, call Telegram or
change AWG, peers, configs or public listeners.

## Bound inputs

```text
candidate_source=801f8c3406121549eb6a19150be009cfc0ea88d0
expected_current_production_overlay=3c91601
package=dist/amn2-private-telegram-smoke-overlay-801f8c3.zip
package_sha256=693DF74192E55A2231F45C0ADF153B745C7D2AF8EDEDA67830D02CB620A4C3FF
source_sha256=B332CB1DCFB85768ACE0DF78E038B955F7C853989CF1C67CDE0233FA51EBD6C3
apply_sha256=85AE2C0E5A1E949529342AF2939A577AE23B3924653A344E1E77465B898E56AF
runbook_sha256=923DBB704BDDF464DEB1D3037703B58AF8B102CFCC3A174509A05FB3FB4B42CC
package_review_commit=4166dd6
package_remote=https://github.com/barakov-dot/amn3.git
package_branch=codex-spark-phase9-docs-sync
package_entries=4
source_entries=371
```

The exact functional delta from production overlay `3c91601` is two modified
paths, 54 insertions and one deletion. It adds the pre-ack backlog guard and its
regression test. There is no schema, API, web, service-unit, config or peer
delta.

## Required read-only preflight

Before any upload or service action, require all of the following:

1. Re-fetch the package from commit `4166dd6` and verify the outer checksum,
   exact four-entry content, source archive commit comment and every bound
   artifact hash.
2. Confirm production overlay exactly `3c91601` and refuse any unknown source
   state, reused candidate/rollback path or symlinked path.
3. Require both product write gates false.
4. Require `amneziya-web.service` active/enabled, login HTTP `200`, protected
   route redirect and loopback-only `127.0.0.1:3030`.
5. Require no API listener on `3040` and no public `3030/3040` listener.
6. Require `amneziya-bot.service` inactive/disabled with no bot process.
7. Require production SQLite integrity `ok`, zero foreign-key issues and record
   safe file/logical digests plus existing table counts.
8. Require `amnezia-awg2` running with restart count zero in the preflight
   window. Record container identity, peer count and a safe peer-public-key-set
   digest without emitting any key.
9. Require sufficient disk for unique mode `0700` candidate and rollback
   directories plus the source and SQLite snapshots.

Stop before upload on any mismatch. This read-only preflight must not start the
bot, poll Telegram or stop AWG.

## Exact allowed live scope

Only after receiving the exact phrase below:

1. Upload only the bound package ZIP and checksum file to `/root`, mode `0600`.
   Verify the outer checksum remotely before extraction.
2. Create unique mode `0700` candidate and rollback directories. Refuse path
   reuse, symlinks, unexpected owners or resolved paths outside the approved
   `/root` roots.
3. Extract the package and verify exact outer names, source checksum, apply
   checksum, runbook checksum and source commit binding.
4. Stop only `amneziya-web.service`. Immediately reconfirm AWG running state,
   restart count and peer-set digest; keep the regular bot inactive/disabled.
5. With web writers frozen, create and verify in the rollback directory:
   - a mode `0600` tracked-source snapshot of `.env.example`, `.gitattributes`,
     `.gitignore`, `README.md`, `app`, `deploy`, `docs`, `pyproject.toml`,
     `scripts` and `tests`;
   - the prior overlay marker and safe metadata;
   - a mode `0600` SQLite backup made through the SQLite backup API;
   - a secret-free manifest of paths, modes, sizes and SHA-256 values.
6. Reconfirm production SQLite file/logical digests and counts before apply.
7. Run the bound source apply tool offline with `VPS_APPLY_ENABLED=false`,
   `OPERATOR_DEVICE_CREATE_ENABLED=false`, `PIP_NO_INDEX=1` and
   `PIP_DISABLE_PIP_VERSION_CHECK=1`.
8. Verify active imports resolve to `/opt/amn2`, overlay marker `801f8c3`, and
   the exact expected two-path functional delta. Do not initialize schema or
   run API smoke.
9. Require production SQLite byte/logical digests, integrity, foreign keys and
   table counts unchanged. Any database change is a rollback condition.
10. Start only `amneziya-web.service`. Require active/enabled state, login HTTP
    `200`, protected redirect, loopback-only listener, no API listener, both
    write gates false and no bot process.
11. Reconfirm AWG running, original container identity, restart count, peer
    count and safe peer-set digest. Natural handshake/traffic counters are
    observational and are not required to remain equal.
12. Retain the verified rollback bundle and sanitized evidence. Remove only
    the verified disposable candidate and upload copies after success.

The expected web interruption is limited to snapshot and offline source apply.
The production VPN must continue serving existing peers throughout.

## Automatic rollback

Rollback after web stop on any snapshot, checksum, apply, import, overlay,
database, web, listener, bot-state or AWG invariant failure:

1. Stop only the web service if it was restarted.
2. Terminate only candidate-owned helper processes.
3. Restore the exact tracked-source snapshot and previous overlay marker.
4. If the production SQLite digest changed unexpectedly, restore the verified
   SQLite backup atomically; otherwise leave SQLite untouched.
5. Run restored-source import checks offline.
6. Start the web service and repeat its login/auth/listener checks.
7. Require AWG still running with its original container identity, restart
   count, peer count and peer-set digest; keep the bot inactive/disabled.
8. Retain rollback material and report only sanitized evidence.

Rollback must never stop, restart, recreate or reconfigure the AWG container.
If AWG itself becomes unhealthy, stop this rollout and use the existing
production-runtime recovery procedure rather than manipulating AWG here.

## Explicit exclusions

This gate does not authorize:

- schema initialization or migration;
- API token or API loopback smoke;
- Telegram API calls, polling, sending or transient unit creation;
- persistent bot enable/start;
- user, device, ticket, lifecycle, plan or audit writes;
- peer mutation, config generation/delivery or revoke;
- public exposure, firewall, TLS or reverse-proxy changes;
- reboot, restore apply, provider actions or client acceptance repetition.

The later transient Telegram smoke remains a separate exact gate after the
production overlay is verified as `801f8c3`.

## Verification before gate publication

```text
packaged_focused_tests=21_passed
packaged_bot_settings_tests=184_passed
packaged_compileall=passed
package_tooling_harness_markdown=23_passed
phase9_progress_harness=passed
package_hash_recheck=passed
diff_check=passed
live_effect=none
```

## Exact approval phrase

```text
APPROVE PHASE11_801F8C3_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_AWG_UNTOUCHED
```

The phrase has not been received or consumed. Without the exact phrase, no
VPS/SSH/upload/service action is authorized.
