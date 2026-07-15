# Phase 11 RESTORE-001A OCI Config-path compatibility fix

Date: 2026-07-15

Status: `implemented|verified|clean-security-scan|ready-for-commit-push-and-approved-retry`

## Failure and sanitized diagnosis

`RESTORE-001A` attempt 1 stopped fail-closed before ciphertext creation with
sanitized error `image archive config digest is invalid`. Production temp
cleanup passed; no secret transfer or staging mutation occurred. Runtime and
operations re-audits passed after the failure.

A later read-only diagnostic used only `docker inspect` and `docker image save`
in a private temporary production directory with mandatory trap cleanup. It
reported only classifications and booleans:

```text
manifest_rows=1
archive_member_duplicates=0
archive_member_unsafe=0
config_path_class=nested_oci_blob_sha256
config_path_normalization_safe=true
config_entry_regular=true
config_self_hash_matches_path_digest=true
layers=6|oci_paths_6|legacy_paths_0|other_paths_0|all_entries_present
canonical_executable_config_equal=true
architecture=amd64|equal_and_supported
os=linux|equal_and_supported
config_values_printed=false
production_temp_cleanup=passed
```

No actual Config path/digest/value, raw environment, secret, private target or
secret-bearing log row was emitted. AWG and services were not mutated.

## Root cause

The common recovery validator accepted only the legacy Docker Config filename
form `<64hex>.json`. Production `docker image save` emitted the equally
content-addressed OCI form `blobs/sha256/<64hex>`. All downstream executable
Config, platform, RootFS and layer-byte evidence was valid but unreachable
because the validator rejected the safe OCI filename first.

## Minimal fix

`scripts/phase11_recovery_runtime.py` now derives the Config content digest
from exactly one of two full-match forms:

```text
legacy=<64 lowercase hex>.json
oci=blobs/sha256/<64 lowercase hex>
```

All existing controls remain unchanged: safe path normalization, regular-file
and duplicate checks, Config self-hash, canonical executable Config hash,
`amd64/linux`, ordered RootFS DiffIDs, referenced layer count and every layer
byte digest. There is no fallback suffix search, basename lookup, case folding,
raw path output or permissive arbitrary nested path.

## TDD and verification

```text
red=3_failed|runtime_writer_restore_consumers|expected_config_digest_error
green=3_passed
recovery_scope=44_passed
canonical_root_inventory=73_passed
python_compile=passed
git_diff_check=passed
```

A broad unscoped `pytest -q` from the workspace root was intentionally not used
as evidence because it collected duplicate historical package/worktree test
trees and produced import-mismatch collection errors. The canonical explicit
root inventory is the seven tracked files under `tests/` and passed 73/73.

## Security review

The sealed Codex Security local-diff scan recorded complete coverage, one full
runtime-file receipt, four reviewed surfaces, nine sealed artifacts, zero
deferred rows and zero findings.

```text
snapshot=codex-security-snapshot/v1:sha256:b051261c4bf7061c72ffcd31b1f04d9da3b77bc3de4e54dfbbd325055dc69cc2
findings=0
```

## Live boundary and next step

This fix/verification slice did not create a bundle, transfer secrets, mutate
staging, restart services, call Telegram, change production overlay, or
stop/restart/recreate AWG. The exact `RESTORE-001A` approval remains
`received|not_consumed` and pinned to `801f8c3`. After docs/status, commit and
push, the same gate may be retried without expanding its approved scope.
