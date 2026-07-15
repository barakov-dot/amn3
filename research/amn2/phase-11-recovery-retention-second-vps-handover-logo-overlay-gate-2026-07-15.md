# Phase 11 recovery retention, second-VPS handover and logo-overlay gate

Date: 2026-07-15.

Status: `local-evidence-and-package-prepared|no-live-mutation`.

## RECOVERY-001 old fallback decision

Decision: `RETAIN SEALED WITHOUT DELETION IN THIS SLICE`.

`PHASE11-RESTORE-001A` proved the canonical runtime-complete v2 full-secret
restore path, so the legacy bundle/key is no longer the primary or required
restore path. The operator selected retention without deletion for this pass.
The old ciphertext copies, receipts and separate symmetric key remain sealed;
their contents were not opened, copied, moved or deleted. Canonical artifacts
and their separate key were not changed.

This is bounded risk acceptance, not an indefinite recommendation. Review the
legacy inventory again no later than 2026-08-01 and prepare a separate exact
destructive deletion gate when the operator chooses to retire it. No future
production/logo/bot action implicitly authorizes deletion.

## Second VPS result and operator decision

The 2026-07-15 read-only SSH audit passed: Ubuntu 24.04, key-only SSH, UFW
default deny, TCP 22 only, no UDP listener, no AMN2 tree/unit/container,
Docker absent, no recovery/AMN2 artifact-name match and no failed units. It
contacted neither production nor provider control state and transferred no
secret.

The authorized 4VPS cabinet was inspected read-only. The Zurich `SW-cx01`
instance is paid through `2026-08-12 23:18:25` as displayed by the provider;
the one-month price shown is `590.00 RUB` and auto-renew is enabled. No switch,
payment, renewal, cancellation or delete control was used.

The operator clarified that this VPS will be kept through the weekend and
then handed to another function. Therefore AMN2 provider retirement is not
recommended or prepared. AMN2 only needs a final clean audit and, after the
handover is confirmed, a separate exact local cleanup of the dedicated staging
SSH key and its known-host binding.

## Canonical logo overlay package

Prepared tracked artifacts:

```text
package=dist/amn2-canonical-logo-overlay-6abc620.zip
package_sha256=2683420DD7A705C96490DC1878D14D208986209BF8EB1B6E1B066D31B17932F5
source_zip_sha256=4BED630024AD58B2E6B7111E172A18CF934262E4BB32DAD7A2787CFFFA4607A4
source_archive_comment=6abc620bc583ddd55490a25633516f2db8e50309
source_archive_entries=371
outer_entries=4
forbidden_entries=0
canonical_logo_sha256=40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791
```

The package is an exact `git archive` of `6abc620`, with a checksum-bound
apply helper and Russian rollout contract. The future wrapper is prepared in
ignored local `tmp/phase11_6abc620_logo_remote_rollout.sh` and
`tmp/phase11_6abc620_logo_ssh_runner.ps1`; neither was executed.

Local package verification passed: both shell files parsed with `bash -n`,
outer entries matched the exact allowlist, source ZIP integrity/comment/full
commit binding passed, both canonical PNGs were byte-identical, obsolete JPG
was absent from source and forbidden secret/runtime entries were zero.

## Safety boundary

No production SSH, upload, package extraction/apply, web stop/start, bot
start/enable, Telegram API/profile mutation, DB write, config/peer mutation,
public exposure, provider mutation or AWG stop/restart/recreate occurred.

Next order: scoped package/source tests, diff/security review, status sync,
commit and push; only then present the prepared exact logo live approval.
