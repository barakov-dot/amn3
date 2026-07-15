# Phase 11 RESTORE-001A: runtime-complete v2 live gate review

Date: 2026-07-14.

Amendment 2026-07-15: the exact approval was received and remains not
consumed because live execution has not started. A later sealed scan found the
Medium executable-Config binding gap P11-LEGACY-IMAGE-CONFIG-UNBOUND-001.
The gap is fixed: runtime-complete v2 now binds canonical executable Config
SHA-256, exact amd64/linux identity, ordered RootFS DiffIDs and archive layer
bytes without storing or printing raw Config values. Current verification is
runtime 15 passed, recovery scoped 41 passed, full root 70 passed and
independent verifier 35 passed. Clean rescan snapshot
codex-security-snapshot/v1:sha256:d56c7864892bdf6f024b1e701b93577a286f1f7d467d50fde2882437757ae12c
has complete coverage, six of six full-file receipts and zero findings.
Current evidence:
research/amn2/phase-11-legacy-image-config-binding-security-fix-2026-07-15.md.
The ordered next step is docs/status sync, commit and push, then the already
approved live sequence below. No live action was performed by the amendment.

Decision: `READY FOR ONE EXACT APPROVAL; LIVE EXECUTION NOT STARTED`.

This review did not contact production or staging, transfer a secret, create a
recovery ciphertext, install a package, start a container/service, or perform
restore apply. Production AWG was not stopped, restarted, recreated or changed.

## 2026-07-15 attempt 2 fail-closed addendum

After the OCI Config-path compatibility fix was committed and pushed as
`bc67919`, attempt 2 entered only the production writer. It stopped fail-closed
before ciphertext creation because the exported Docker manifest contained the
single canonical `amnezia-awg2:local` RepoTag. `docker image save` preserves
that tag even when invoked with the immutable image ID.

Production private-run cleanup passed. Mandatory runtime and compact OPS
re-audits passed: overlay `801f8c3`, web healthy, regular bot
inactive/disabled, database integrity OK, AWG running with restart count zero
and the unchanged 12-peer set; Telegram API was not called. No secret transfer
or staging mutation occurred. Approval remains `received|not_consumed`.

The minimal local fix accepts only an empty RepoTags list or the exact singleton
expected canonical reference. It rejects foreign, additional and duplicated
tags. Config path/self-hash, canonical executable Config, platform, ordered
RootFS DiffIDs and every layer-byte digest remain bound. Regression evidence:
RED 3 expected failures, GREEN 6 passed, recovery scope 48 passed and canonical
root scope 77 passed. Current evidence:
`research/amn2/phase-11-restore-001a-canonical-repotag-compatibility-fix-2026-07-15.md`.

## Why the existing canonical v1 is not sufficient

The accepted `amn2-full-recovery-v1` authenticates and verifies the production
database, environment, server registry, AWG material, container start script
and systemd units. It does not contain the AMN2 source tree, an offline Docker
image or the exact Docker recreation contract. It is therefore a valid sealed
fallback but not a clean-host runtime-complete restore artifact.

`RESTORE-001A` must require `amn2-full-recovery-v2`. Generic v1 or generic v2
verification is not live-gate evidence.

## Runtime-complete v2 contract

The writer adds three manifest-bound members:

- `host/source.tar.gz` — exact `801f8c3` Git archive;
- `container/image.tar` — offline `amnezia-awg2:local` image;
- `container/runtime.json` — canonical allowlisted Docker runtime contract.

Approved source archive evidence:

```text
source_overlay=801f8c3
source_archive_bytes=8650530
source_archive_expanded_bytes=11001389
source_archive_files=328
source_archive_sha256=6c58c33fc5b152114f651cece46cd99955758198e25e67e3c422ed5ca1f8166e
```

The independently supplied source SHA-256 is checked over the exact archive
bytes before the writer accepts them, is persisted in canonical metadata and
is covered by the encrypted bundle manifest. The RESTORE-001A verifier must be
called with both:

```text
--require-format amn2-full-recovery-v2
--expected-source-archive-sha256 6c58c33fc5b152114f651cece46cd99955758198e25e67e3c422ed5ca1f8166e
```

Its report must contain:

```text
source.verification_policy.gate_mode=restore_001a_runtime_complete_v2
source.verification_policy.required_format=amn2-full-recovery-v2
source.verification_policy.external_source_archive_sha256_verified=true
source.critical_contracts=passed
verdict=passed
```

The runtime validator requires the production-observed immutable image ID,
image reference `amnezia-awg2:local`, bridge baseline, restart policy,
privileged/capability set, UDP/30001 mapping, `/lib/modules:ro`, sysctl,
security option, entrypoint/command and safe environment keys. The offline
image config digest and each actual layer byte sequence are bound through
`rootfs.diff_ids`. Nested source gzip expansion is capped at 24 MiB before tar
metadata parsing; member count/type/path/expanded-file controls also fail
closed.

## Engineering evidence

```text
focused_postfix_tests=35_passed
root_tests=64_passed
progress_harness_tests=20_passed
progress_harness_phase11_named_slice=passed
python_compile=passed
real_801f8c3_archive_validation=passed
postfix_security_coverage=complete
postfix_security_findings=0
security_snapshot=codex-security-snapshot/v1:sha256:db1b5700bd929212e25868dbf26a90c53f917dd3a0f39b23dcb02ddaa7e66702
```

The security review covered all three production files in full. It closed the
source substitution, legacy/generic gate confusion, Docker layer substitution,
nested archive resource-limit and gate-evidence ambiguity candidates.

## Exact approved live sequence

One approval authorizes only this single transaction:

1. Recheck production overlay `801f8c3`, web/bot/write-gate baseline and AWG
   identity/running/restart-count/12-peer-set invariant read-only. Recheck the
   second VPS is the previously audited clean SSH-only host.
2. On staging only, install the minimum Docker/Python packages if absent and
   record exactly which packages/state the gate introduced. No public listener
   other than existing SSH may be opened.
3. Upload only reviewed writer/runtime/crypto helpers, the approved source
   archive, and the RSA public key to a private production run directory.
   Create one encrypted v2 bundle without stopping/restarting any production
   service. Verify its ciphertext hash, download it, remove the private
   production run directory, and recheck the AWG invariant.
4. Decrypt only in local process memory using the separate canonical private
   key. Do not write a local plaintext bundle. Require the exact v2 gate flags
   and attestation above. Retain sanitized count/hash evidence only.
5. Stream the already verified plaintext bundle over the pinned key-only SSH
   channel directly into a private staging run directory. Never print bundle,
   env, DB, config, key, PSK, token, target identity or raw secret-bearing log.
6. Reverify manifest/metadata/source/image/runtime, SQLite integrity and
   foreign keys, AWG key/peer bindings, unit structure, file modes/owners and
   bot/write-gate disabled state on staging.
7. Load the offline image and perform one bounded transient AWG start with no
   host port publication and no route to production. Verify exact image/runtime
   identity, running state and 12 restored peer bindings; do not generate a
   peer/config and do not test a client handshake.
8. Build the restored source environment and perform one bounded web start on
   staging loopback only with outbound production access blocked. Verify HTTP
   health, restored DB integrity/counts and `801f8c3`; never start or enable the
   bot and never call Telegram.
9. Stop/remove transient units and containers; remove restored plaintext,
   source, DB, env, AWG material, image and run directories. Purge only Docker
   packages/state installed by this gate. Repeat the clean-host audit: SSH-only,
   no AMN2 tree/unit/container/image/recovery artifact, no failed unit.
10. Recheck production DB/web/bot/write gates and the unchanged AWG identity,
    restart count and 12-peer set. Retain only ciphertext copies and sanitized
    receipts; promote the v2 ciphertext as canonical only after every mandatory
    receipt passes.

Any failure or mismatch stops forward execution and enters step 9 cleanup.
Cleanup and both production invariant checks are mandatory even after a failed
rehearsal. If network isolation cannot be proved, runtime start is forbidden.

## Explicitly excluded

This approval does not authorize production restore apply, production Docker
mutation, AWG stop/restart/recreate, peer/config generation or delivery,
Telegram polling/send, bot enable/start, public web/API, firewall/provider/
billing mutation, deletion of either old fallback copy/key, deletion of the
second VPS, or deletion/rotation/move of canonical recovery keys.

Old fallback retirement and provider retirement remain separate exact
destructive gates after a successful rehearsal and post-cleanup audit.

## Exact approval phrase

```text
APPROVE PHASE11_RESTORE_001A_801F8C3_RUNTIME_COMPLETE_V2_CANONICAL_BUNDLE_CREATE_VERIFY_COPY_AND_TRUSTED_DISPOSABLE_FULL_SECRET_RESTORE_WITH_STAGING_DOCKER_INSTALL_TRANSIENT_NETWORK_ISOLATED_AWG12_AND_LOOPBACK_WEB_VERIFY_MANDATORY_SECRET_RUNTIME_CLEANUP_REAUDIT_AND_PRODUCTION_AWG_UNTOUCHED
```

Until that phrase is received verbatim:

```text
restore_001a_execution=false
secret_transfer=false
production_bundle_creation=false
staging_package_or_runtime_mutation=false
old_fallback_delete=false
second_vps_provider_mutation=false
```

## 2026-07-15 attempt 1 fail-closed addendum

The exact approval was later received. After the executable-Config binding
security fix was tested, clean-scanned, committed and pushed, attempt 1 entered
only the production bundle-creation step and stopped fail-closed with sanitized
reason `image archive config digest is invalid`.

```text
attempt_1=ciphertext_not_created
production_private_run_cleanup=passed
secret_transfer=false
staging_mutation=false
approval=received|not_consumed
```

Mandatory failure-path checks then passed: the production runtime contract was
still intact, the web/bot/write-gate baseline remained unchanged, and the
compact operations audit reconfirmed database and AWG invariants. Raw image
Config, Config path, secret environment values and private target identity were
not emitted.

The next allowed work is a read-only sanitized path-shape diagnostic that
classifies the archive Config entry without printing it. No bundle retry is
allowed until the exact root cause is reproduced by a RED test, fixed
fail-closed, covered by scoped/full tests and a fresh diff/security review,
documented, committed and pushed.

AMN2 source later advanced to `6abc620` only for local canonical logo assets.
Production and this approved restore transaction remain pinned to `801f8c3`;
the logo commit does not expand or consume the restore approval.

## 2026-07-15 OCI compatibility fix addendum

The sanitized diagnostic confirmed one safe OCI Config blob and six safe OCI
layer blobs. There were no duplicate/unsafe archive members; Config self-hash,
canonical executable Config, architecture and OS all matched production, and
the diagnostic temp directory was removed.

The validator now accepts only the exact legacy `<64hex>.json` or exact OCI
`blobs/sha256/<64hex>` Config form. It still requires the selected regular file
to self-hash to the encoded digest and preserves executable Config,
architecture/OS, RootFS DiffID and every layer-byte binding.

```text
tdd_red=3_failed_expected
tdd_green=3_passed
recovery_scope=44_passed
canonical_root_inventory=73_passed
security_scan=complete|findings_0
approval=received|not_consumed
```

After docs/status, commit and push, the same exact `801f8c3` transaction may be
retried. No new or expanded approval is implied.
