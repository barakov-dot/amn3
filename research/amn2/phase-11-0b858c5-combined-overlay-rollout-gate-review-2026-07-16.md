# Phase 11 `0b858c5` combined overlay live gate review

Date: 2026-07-16.

Decision: `READY-AWAITING-EXACT-APPROVAL`.

The operator approved proceeding with the ordered review/preparation chain.
The message did not contain the exact named live approval phrase required by
the committed package gate, so this review did not contact the VPS, upload or
extract the package, stop/start a service, write SQLite, call Telegram, mutate
a provider/peer/config or perform any AWG action.

## Bound inputs

```text
production_overlay=801f8c3
candidate_source=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
source_branch=codex-vps-test-prep|origin_sync|clean
package=dist/amn2-combined-overlay-0b858c5.zip
package_bytes=9220155
package_sha256=7866BDD9FEBE1D6EEA701B37A6E4206A8267766A56993F3C02A0C7B30C394B54
source_zip_sha256=E03F13FD6A7BB5CBC5FCEE7179F395EA8C2864EBCEAB01BC351C5904F3CFF975
outer_entries=4
source_entries=383
source_delta_paths=31
source_deleted_path=app/web/static/brand-full.jpg
schema_delta=none
canonical_square_logo_sha256=40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791
wide_language_header_sha256=BBDDFA72D1D1FC37E412D2F4A9B4124001FF91FBD641635E31A47E008FC4611F
remote_executor_sha256=A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72
ssh_runner_sha256=A699DC14971FAD59FC1A4020B08248C63F8A7C798816365485F7EBCF9663D362
approval_validation=ordinal_full_string_equality_before_transport
```

## Fresh local verification

- outer/source hashes, exact four-entry allowlist, full source commit comment,
  `383` inner entries and archive integrity passed;
- unsafe and symlink entries are both zero;
- square bot/web assets are byte-identical and match the canonical hash;
- wide language header matches its exact hash;
- obsolete JPG is absent from the source archive and package-data declaration
  is present;
- Git HEAD equals trusted origin, the delta contains exactly `31` paths, the
  only deletion is the obsolete JPG and no schema delta exists;
- executor TDD: `3` expected RED failures for missing executors, then
  `3 passed` after the minimal implementation;
- combined executor/apply/markdown scoped suite: `10 passed`;
- Bash and PowerShell syntax checks passed.

Security review identified and fixed the approval-substring ambiguity before
any live contact. A dedicated test first failed because the runner accepted no
approval input. The runner now requires the complete phrase as a mandatory
parameter and performs ordinal full-string equality before resolving the
SSH target, reading transport inputs or starting SCP/SSH.

The rollback path also re-computes and compares the complete database snapshot
after any restore and web recovery. A mismatch marks rollback failed instead
of reporting a successful recovery without database proof.

## Prepared executor contract

The local PowerShell runner uses only the existing pinned production SSH key
and strict known-host binding, redacts the target from output and uploads only
the bound package plus checksum. It validates the local package hash before
SCP.

The remote Bash executor has only `preflight`, `upload`, `apply` and
`postflight` orchestration modes. Before apply it requires production overlay
`801f8c3`, both write gates false, private web healthy, regular bot
inactive/disabled/process zero, SQLite integrity/FK zero, sufficient disk and
an unchanged running AWG snapshot.

After exact package/source/helper/runbook verification it creates unique
mode-0700 candidate and rollback roots. With only web stopped, the rollback
bundle receives tracked source, overlay marker, SQLite backup/snapshot, source
manifest, AWG snapshot and hashes of the installed bot unit plus `/opt/amn2/.env`.
The apply runs offline, removes only stale tracked `brand-full.jpg`, verifies
the exact 31-path delta, imports, both image contracts and the served square
logo, then starts only web.

Any package/source/snapshot/apply/import/asset/database/web/bot/AWG mismatch
after rollback arming restores tracked source and overlay marker, restores
SQLite only if it changed, starts only web and re-proves the bot and AWG
invariants. The executor contains no AWG mutation, bot activation or Telegram
API operation.

## Exact approval phrase

Prepared and not consumed:

```text
APPROVE PHASE11_0B858C5_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_TELEGRAM_PROFILE_UNCHANGED_AND_AWG_UNTOUCHED
```

Only an operator message exactly equal to that phrase opens VPS/SSH preflight,
upload and the bounded source transaction. Quoted, prefixed, suffixed,
symbolic, negated or substring forms do not qualify. The local runner repeats
the same ordinal full-string equality check before any transport action. The
approval does not authorize persistent bot installation/enable/start, Telegram
calls/profile mutation, schema writes, public exposure, provider action,
recovery-artifact mutation, peer/config mutation or any AWG service/config
action.

## Post-fix trusted transport review — 2026-07-17

The local runner was hardened after the scoped security review reported three
medium/P2 unqualified executable-resolution paths. `ssh.exe` and `scp.exe` are
now bound to absolute `%WINDIR%\System32\OpenSSH` paths, both files are
required before transport, and the shared process helper rejects any
non-absolute or outside-root executable path.

```text
runner_sha256=A699DC14971FAD59FC1A4020B08248C63F8A7C798816365485F7EBCF9663D362
remote_executor_sha256=A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72
focused_tests=9_passed
canonical_tests=95_passed
bare_transport_calls=0
trusted_transport_calls=3
postfix_security_rescan=pass
live_rollout=false
awg_untouched=true
```

The previously prepared approval phrase is superseded by the runner change
and must not be used. A fresh non-reusable phrase will be issued only after
the intentional commit/push and origin verification. No upload, apply,
rollback, bot activation or Telegram operation is authorized by this local
hardening result.
