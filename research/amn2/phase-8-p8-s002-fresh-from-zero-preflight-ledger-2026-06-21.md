# Phase 8 P8-S002 fresh-from-zero preflight ledger

Date: 2026-06-21.

Status: `completed-fresh-from-zero-preflight-ledger-docs-only-no-live-action`.

Scope: docs-only/package-preflight ledger for the future `P8-C003
fresh-from-zero VPS rehearsal gate`. No live VPS/SSH command, package upload,
source apply, service restart, destructive clean/install action, public
exposure, config delivery, Telegram API call/live send, write execution,
backup restore/import/reboot, provider mutation, production peer/user mutation
or secret-bearing output was performed.

## Source Of Truth

AMN3/evidence workspace:

```text
path=C:\Users\SooL\Documents\VPS-OPS-LAB
branch=master
head=0d93807 Record Phase 8 launch readiness gates
status=clean
```

AMN2 current-fixes worktree:

```text
path=C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current
branch=codex/phase7-current-fixes
head=187949b Persist Android-compatible AWG defaults
remote=amn2/codex/phase7-current-fixes
status=clean
```

Target disposable VPS:

```text
target_vps=89.185.80.166
target_role=disposable
```

Latest passed gates:

```text
p8_c001_status=passed-fresh-per-device-android-acceptance-with-reconnect-sanity
p8_c002_status=passed-package-current-head-smoke-compatible-awg-defaults-persisted
latest_vps_applied_package_smoked_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
phase8_launch_gate_status=blocked-until-fresh-from-zero-vps-rehearsal
private_operator_rc_distance_to_launch=92_percent
```

Package inputs for `P8-C003`:

```text
package=dist/amn2-vps-update-and-smoke-kit-187949b.zip
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
package_bytes=8708274
source_zip=dist/amn2-codex-phase7-current-fixes-187949b-source.zip
source_sha256=649EF03461555B13D8C4AF59709CEEC49F2300C395F69DCA982DF15732409313
source_bytes=8757958
```

## Criticality Ledger

### Критичные

Одиночные задачи:

1. Open exact destructive `P8-C003` gate with target VPS and wipe/install
   consent.
2. Run fresh-from-zero rehearsal on the disposable VPS.
3. Record `P8-SFINAL` launch readiness freeze after `P8-C003`.

Парные задачи:

1. Confirm target disposable VPS plus package SHA.
2. Fresh install/apply plus loopback smoke.
3. Fresh Android acceptance plus backup verify.

Тройные задачи:

1. Clean install plus package apply plus API smoke.
2. Android import/connect/traffic plus AWG counter observation plus no-payload
   evidence.
3. Backup verify plus external probes closed plus final mutation guard.

Четыре и более за раз:

1. Full `P8-C003` run: destructive fresh install, package apply, web/API smoke,
   Telegram getMe/non-polling smoke, one fresh Android config acceptance,
   backup create/verify, closed external probes and final evidence.

### Очень важные

Одиночные задачи:

1. Verify `187949b` package/source SHA before upload.
2. Prepare private safe env values outside chat/evidence.
3. Confirm Android test device availability before starting the mobile slice.

Парные задачи:

1. Runbook dry-check plus operator prompt copy/paste review.
2. Telegram `getMe` plus non-polling dispatcher/user-flow smoke.
3. Status docs plus next-chat handoff update after the rehearsal.

Тройные задачи:

1. Package hygiene plus source overlay check plus runtime settings check.
2. Web login plus API auth smoke plus audit/listener smoke.
3. AMN2 head check plus AMN3 evidence commit plus final clean status.

Четыре и более за раз:

1. Safe runtime proof bundle: settings load, web login, API auth/audit/listener,
   Telegram surface, backup verify and closed probes.

### Важные

Одиночные задачи:

1. Update `docs/PROJECT_STATUS_CURRENT.ru.md`.
2. Update `docs/NEXT_CHAT_AMN2_PHASE_8_PREP.ru.md`.
3. Update `docs/PROJECT_CONTEXT_IMPORT.ru.md`.

Парные задачи:

1. Evidence writeup plus `git diff --check`.
2. Backup artifact metadata plus safe inventory.
3. Android reconnect sanity plus counter delta note if the device is available.

Тройные задачи:

1. Status docs plus context import plus next-chat handoff.
2. Evidence file plus package manifest plus SHA notes.
3. Git status AMN2 plus git status AMN3 plus pushed heads.

Четыре и более за раз:

1. Full documentation closure: evidence, status override, context import,
   next-chat handoff, source/package head notes and final blocker statement.

### Простые

Одиночные задачи:

1. Verify current branch/head.
2. Verify package files exist.
3. Verify public probes are closed during the gate.

Парные задачи:

1. `git status` plus `git log -1`.
2. SHA file check plus package file presence.
3. Transcript path note plus run id note.

Тройные задачи:

1. File existence plus SHA presence plus package size note.
2. Local helper parse check plus prompt text check plus transcript path check.
3. Old blocker scan plus stale head scan plus next gate scan.

Четыре и более за раз:

1. Read-only sanity sweep: branch/head, package SHA files, package sizes,
   current status docs, stale blocker phrases and forbidden payload scan.

### Косметические

Одиночные задачи:

1. Remove stale `next P8-C002` wording.
2. Align `P8-C003` naming across docs.
3. Remove EOF blank lines.

Парные задачи:

1. Handoff wording polish plus stop-line wording polish.
2. Distance-to-launch wording plus limitations wording.
3. Evidence headings plus result blocks.

Тройные задачи:

1. Consistent `P8-C003` naming plus status wording plus next gate wording.
2. Russian wording polish plus no-payload reminders plus copy/paste prompts.
3. Evidence ordering plus docs links plus stale phrase cleanup.

Четыре и более за раз:

1. Final editorial pass across status, context, next-chat and Phase 8 evidence
   after live evidence is recorded.

## Readiness Checklist Before Opening P8-C003

All items below must be true before starting any destructive/live action:

```text
operator_explicit_destructive_gate_opened=false
target_vps_confirmed_disposable=true
target_vps=89.185.80.166
package_sha256_known=true
source_sha256_known=true
amn2_head_pushed=true
amn3_evidence_head_pushed=true
safe_env_values_available_privately=operator_must_confirm
telegram_token_available_privately=operator_must_confirm
web_admin_credentials_available_privately=operator_must_confirm
android_test_device_available=operator_must_confirm
private_handoff_destination_outside_workspace=operator_must_confirm
public_exposure_required=false
restore_import_required=false
old_configs_allowed_as_release_artifacts=false
payload_output_allowed=false
```

The `false` value for `operator_explicit_destructive_gate_opened` is
intentional: this ledger does not open `P8-C003`.

## P8-C003 Pass Criteria

`P8-C003` can pass only if all of these are recorded without secret-bearing
payload:

```text
fresh_install_status=passed
package_sha256_match=yes
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_match=yes
fresh_env_db_init_status=passed
loopback_web_status=passed
loopback_api_smoke_status=passed
telegram_get_me_status=passed
telegram_polling_started=false
telegram_live_send_performed=false
fresh_android_import_status=passed
fresh_android_connect_status=passed
fresh_android_traffic_status=passed
fresh_android_server_counter_growth=passed
backup_create_status=passed
backup_verify_status=passed
backup_artifact_mode=600
public_3030_probe=000
public_3040_probe=000
public_80_probe=000
public_443_probe=000
secret_values_printed=false
config_payload_output_performed=false
```

## Stop Lines

Stop immediately if any of these occurs:

- package or source SHA mismatch;
- source overlay does not match `187949b`;
- safe env/DB initialization fails;
- loopback web/API smoke fails;
- Telegram `getMe` fails or polling/live send starts unexpectedly;
- fresh Android import, connect, traffic or server counter observation fails;
- backup create/verify fails or artifact mode is not `600`;
- any public probe opens unexpectedly;
- any `.conf`, QR, `vpn://`, private key, PSK, token or secret-bearing payload
  is about to be printed into chat/evidence;
- the operator cannot confirm the target VPS is disposable before destructive
  action.

## Result

`P8-S002` is complete as a docs-only preflight ledger. The next action is not
to run destructive work automatically. The next action is to review the
separate `P8-C003` destructive gate proposal and open the exact gate only if
the operator accepts its target, scope and stop-lines.
