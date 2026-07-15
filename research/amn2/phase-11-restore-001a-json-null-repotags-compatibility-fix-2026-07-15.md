# Phase 11 RESTORE-001A JSON-null RepoTags compatibility fix

Date: 2026-07-15

Status: `implemented|tested|security-reviewed-clean|ready-for-commit-push-and-approved-retry`

## Attempt 3 failure boundary

After canonical RepoTag compatibility commit `1479dc8`, the approved
RESTORE-001A gate was retried. The production writer stopped fail-closed before
ciphertext creation with sanitized reason:

```text
image archive repo tag contract is invalid
production_private_run_cleanup=passed
```

The source pin remained `801f8c3`. No bundle, secret transfer or staging
mutation occurred. Approval remains `received|not_consumed`.

Mandatory re-audits passed:

```text
runtime_contract_review=pass
image_reference=amnezia-awg2:local
image_repo_tag_count=1
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

## Sanitized diagnosis

A private temporary production diagnostic used read-only Docker inspect/save
and mandatory cleanup. It emitted no tag value, path, digest, Config value,
private target or secret. Relevant results:

```text
manifest_row_count=1
repo_tags_class=null
repo_tags_list_count=0
repo_tags_all_strings=false
archive_member_duplicate_count=0
archive_member_unsafe_count=0
config_path_class=nested_oci_blob_sha256
config_self_hash_matches_path_digest=true
layer_entry_count=6
layer_entry_exists_count=6
layer_oci_path_count=6
layer_other_path_count=0
canonical_config_equal=true
architecture_equal=true
os_equal=true
production_temp_cleanup=passed
```

## Bounded fix

The validator now distinguishes a present JSON-null value from a missing key:

```text
required=RepoTags key is present
accepted=JSON null | [] | [exact expected canonical reference]
rejected=missing | malformed | foreign | additional | duplicate
```

The expected reference remains independently pinned to the public constant
`amnezia-awg2:local`. No arbitrary tag is accepted. Archive member/path/size
limits, Config path digest, Config self-hash, executable Config SHA-256,
`amd64/linux`, ordered RootFS DiffIDs and every layer-byte SHA-256 remain
unchanged.

## TDD and verification

```text
red=3_failed_expected|validator_writer_restore
green=8_passed|null_and_canonical_acceptance|missing_foreign_additional_duplicate_rejection
recovery_scope=50_passed
canonical_root_inventory=79_passed
python_compile=passed
git_diff_check=passed
```

## Security/diff review

Independent security-focused review found no Critical, Important or Minor
issues and returned ready yes. It verified exact key/value policy, the
independent `IMAGE_REFERENCE` pin, rejection of all named negative forms,
unchanged Config/platform/RootFS/layer controls and secret-free errors.

The protected untracked
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` was not edited and must remain
excluded from staging.

## Next step

Sync status, commit and push, then retry the same approved `801f8c3` gate. Any
new mismatch remains fail-closed with mandatory cleanup and production AWG
re-audit.
