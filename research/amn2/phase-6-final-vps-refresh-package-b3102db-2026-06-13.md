# Phase 6 P6-C006 final VPS refresh package preflight for b3102db

Date: 2026-06-13.

Status: `package-ready-not-vps-smoked`.

This is the local package/preflight part of `P6-C006` only. The live VPS
apply/restart/smoke part remains gated and was not executed.

## Source

```text
AMN2 repo: barakov-dot/amn2
AMN2 branch: codex-vps-test-prep
AMN2 commit: b3102db250da7ca9aef78ca095602187d0efc462
AMN2 subject: Add client compatibility delivery boundary
previous latest VPS-smoked/package head: 2215761 Polish operator web admin UX
```

## Artifacts

```text
source zip:
dist/amn2-codex-vps-test-prep-b3102db-source.zip

source sha256:
72342DB625D53AE2F6B68835A1FC4E080684A4A1E9018E791820899BB9A09778

package:
dist/amn2-vps-update-and-smoke-kit-b3102db.zip

package sha256:
B4C3FF33FD0A721C97A83EA8AF08D5E5B6EA5E8D1862EEB63494E8842D56A21B

package directory:
dist/amn2-vps-update-and-smoke-kit-b3102db/
```

The package contains:

```text
AMN2_VPS_UPDATE_AND_SMOKE_b3102db.ru.md
amn2_api_loopback_smoke.sh
amn2_apply_source_zip.sh
amn2-codex-vps-test-prep-b3102db-source.zip
amn2-codex-vps-test-prep-b3102db-source.zip.sha256.txt
```

## Verification

Local package verification passed:

```text
package_verification=passed
source_sha=72342DB625D53AE2F6B68835A1FC4E080684A4A1E9018E791820899BB9A09778
kit_sha=B4C3FF33FD0A721C97A83EA8AF08D5E5B6EA5E8D1862EEB63494E8842D56A21B
kit_entries=5
source_entries=329
forbidden_source_entries=0
shell_scripts=LF/no-BOM
apply_script_commit_binding=b3102db250da7ca9aef78ca095602187d0efc462
smoke_script_expected_commit=b3102db
```

Required package/source entries were present, including the API/web/bot delivery,
integration status, build status, client compatibility and focused regression
test files.

`python -m app.toolchain check` initially failed under system Python `3.14.3`,
as expected for this project gate. The same check passed under bundled CPython
`3.12.13`:

```text
AMN2 toolchain ok: CPython 3.12.x.
```

Focused pytest was attempted with bundled CPython `3.12.13`, but that runtime
does not include `pytest`:

```text
No module named pytest
```

Therefore this evidence records fresh package verification plus fresh toolchain
verification. It does not claim a fresh pytest pass for this package-preflight
step. The immediately preceding AMN2 implementation slice for `b3102db` already
recorded focused and expanded local test passes in
`research/amn2/phase-6-client-compatibility-copy-boundary-2026-06-13.md`.

## Boundary

Not executed:

- live VPS command;
- SSH command;
- package upload/apply on VPS;
- source overlay on VPS;
- service restart/deploy;
- live bot verification or send;
- public exposure;
- config delivery, `.conf`, QR or `vpn://` delivery;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use or Telegram identity/profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

`VPS_APPLY_ENABLED=false` remains the required default for the future loopback
smoke.

## Decision

`b3102db` is now package-ready locally, but not VPS-smoked.

The latest VPS-smoked/package head remains:

```text
2215761 Polish operator web admin UX
```

The remaining `P6-C006` live path requires a separate explicit named gate, for
example:

```text
Открываю P6-C006 live apply/smoke gate для b3102db на текущем disposable VPS.
```

After that gate, the expected live sequence is package upload/checksum/extract,
source overlay, read-only loopback API smoke, web/bot runtime verification and
safe evidence capture. It still must not open config delivery, write API, public
exposure, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive VPS action or Telegram identity mutation.
