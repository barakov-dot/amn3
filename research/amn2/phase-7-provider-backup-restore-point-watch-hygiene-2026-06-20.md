# AMN2 Phase 7 P7-C006a Provider Backup Restore-Point + Watch-Only Hygiene

Дата: 2026-06-20.

Статус: `completed-provider-console-evidence-inconclusive-watch-hygiene-no-mutation`.

Scope:

- `P7-C006a` provider backup restore-point confirmation as docs-only /
  provider-console evidence.
- Watch-only status hygiene after `P7-C005` scoped write/install contour.
- No live VPS command, SSH command, restore, import, reboot, provider mutation,
  remote backup download, backup contents output, Telegram action, public
  exposure, config delivery, Local Agent mutation or secret-bearing output.

## Source Of Truth

```text
AMN2 current head: 5501295 Add P7 install write contour
AMN2 package/source repo: barakov-dot/amn2 codex-vps-test-prep 5501295
Current disposable VPS: 89.185.80.166
Latest live evidence: research/amn2/phase-7-write-install-mutation-contour-5501295-2026-06-20.md
Latest clean installer evidence: research/amn2/phase-7-destructive-clean-installer-execution-b121865-2026-06-19.md
Latest backup-only evidence: research/amn2/phase-7-backup-only-evidence-b121865-2026-06-19.md
```

## Provider Console Evidence

Operator-provided provider-console screenshot showed VPS `4s0806-Prod-USA` as
active on IP `89.185.80.166`, Ubuntu 24.04. The visible recent provider events
were:

- `Creation of the disk backup 4s0806-Prod-USA`: successfully, 2026-06-15
  14:29 UTC+03:00.
- `Move the disk backup to the internal storage`: failed, 2026-06-15 14:29
  UTC+03:00.
- `Deleting the backup of disk 4s0806-Prod-USA`: successfully, 2026-06-15
  14:29 UTC+03:00.

Conclusion:

```text
provider_console_evidence_status=inconclusive
provider_restore_point_currently_available=not_confirmed
provider_restore_point_must_not_be_used_as_restore_prerequisite=true
provider_mutation_performed=false
restore_apply_performed=false
archive_import_apply_performed=false
remote_backup_download_performed=false
reboot_performed=false
secret_values_printed=false
```

The screenshot is useful as provider-console evidence, but it does not confirm
that a provider restore point is currently available. It shows successful backup
creation, failed move to internal storage, and successful deletion. Any future
provider restore, provider snapshot use, reboot or disaster-recovery drill
still requires a separate exact named gate and fresh proof that the provider
restore point exists.

## AMN2 Backup Context

`P7-C006` backup-only create+verify already passed on 2026-06-19 for the
pre-clean `b121865` runtime. That encrypted backup artifact stayed on the VPS
and was not downloaded. `P7-C004b` then performed the clean installer run, and
`P7-C005` later overlaid/smoked `5501295`.

Post-clean read-only rebaseline confirmed no new backup was created after the
clean install. Therefore the remaining `P7-C006` scope is still exact-gated for
restore apply, archive import, remote backup download, reboot,
disaster-recovery drill or destructive migration.

## Watch-Only Intake

Official release pages checked on 2026-06-20:

- `https://github.com/amnezia-vpn/amnezia-client/releases` currently shows
  `4.8.19.0` as latest, dated 2026-06-15.
- `https://github.com/amnezia-vpn/amneziawg-android/releases` currently shows
  `2.0.1` as latest, dated 2026-06-12.

These signals do not create permission for config delivery, public exposure,
restore/import/reboot, write execution, Telegram mutation or upstream/GPL code
copy.

```text
client_watch_status=signals-only-amnezia-client-4.8.19.0-amneziawg-android-2.0.1
upstream_copy_performed=false
new_implementation_task_created=false
permission_to_open_live_gate=false
```

## Result

`P7-C006a` is closed as docs-only/provider-console evidence with an
inconclusive provider restore-point result. The active approved plan is reduced
to residual exact-gated `P7-C006` restore/import/download/reboot/DR scopes,
`P7-C007` Telegram identity/profile/media mutation, and watch-only intake.
