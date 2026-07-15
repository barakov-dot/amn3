# Phase 11 RESTORE-001A canonical RepoTag compatibility fix

Date: 2026-07-15

Status: `implemented|tested|security-reviewed-clean|ready-for-commit-push-and-approved-retry`

## Attempt 2 failure boundary

After OCI Config-path compatibility commit `bc67919`, the already approved
RESTORE-001A gate was retried. The production writer stopped fail-closed before
ciphertext creation with sanitized reason:

```text
immutable image archive unexpectedly contains repo tags
production_private_run_cleanup=passed
```

The writer validates the offline image archive before encryption, so no bundle
was created. No secret transfer or staging mutation occurred. The source pin
remained `801f8c3` and the exact approval remains `received|not_consumed`.

Mandatory read-only re-audits passed:

```text
runtime_contract_review=pass
image_reference=amnezia-awg2:local
image_repo_tag_count=1
image_repo_digest_count=1
image_has_pullable_reference=true
container_running=true
container_restart_count=0
ops_001_health=pass
overlay=801f8c3
web=active_enabled|result_success|restarts_0
regular_bot=inactive_disabled_process_0
database_integrity=ok
awg_running=true
awg_restart_count=0
awg_peer_count=12
telegram_api_called=false
```

Raw inspect data, Config values, private target data and secrets were not
printed. Production services and AWG were not stopped, restarted, recreated or
changed.

## Root cause and bounded fix

Production `docker image save` preserves the single canonical local RepoTag in
`manifest.json` even when the export command uses the immutable image ID. The
archive content itself remains bound by the already verified Config and layer
digests.

The common image validator now accepts exactly either:

```text
RepoTags=[]
RepoTags=[expected canonical image reference]
```

It rejects foreign, additional and duplicate tags. The expected reference is
already constrained to the canonical public constant `amnezia-awg2:local`.
This change does not accept arbitrary references and does not replace any
content identity check.

The following controls remain unchanged: archive path normalization, member
type/duplicate/size limits, Config path digest extraction, Config self-hash,
canonical executable Config SHA-256, `amd64/linux`, ordered RootFS DiffIDs,
referenced layer presence/count and every layer-byte SHA-256.

## TDD and regression evidence

```text
red=3_failed_expected|validator_writer_restore
green=6_passed|canonical_acceptance_and_foreign_additional_duplicate_rejection
recovery_scope=48_passed
canonical_root_inventory=77_passed
python_compile=passed
git_diff_check=passed
```

## Security/diff review

An independent security-focused full-diff review confirmed:

```text
critical=0
important=0
minor=0
ready_to_merge=yes
```

The review specifically verified that `expected_reference` remains pinned to
the canonical `IMAGE_REFERENCE`, malformed/missing/foreign/additional/duplicate
RepoTags fail closed, errors remain secret-free, and none of the Config,
platform, RootFS or layer-byte bindings changed.

The protected untracked
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` was not edited and must remain
excluded from staging.

## Next step

Commit and push this tested/reviewed slice, then retry the same approved
`801f8c3` RESTORE-001A gate. Any new mismatch must again stop fail-closed with
mandatory cleanup and production AWG re-audit.
