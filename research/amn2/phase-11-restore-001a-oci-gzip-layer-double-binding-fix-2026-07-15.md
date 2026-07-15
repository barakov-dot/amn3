# Phase 11 RESTORE-001A OCI gzip layer double-binding fix

Date: 2026-07-15

Status: `implemented|tested|security-reviewed-clean|ready-for-commit-push-and-approved-retry`

## Attempt 4 failure boundary

After JSON-null RepoTags compatibility commit `9a9f31f`, the approved gate was
retried. The production writer stopped fail-closed before encryption:

```text
image archive layer digest mismatch
production_private_run_cleanup=passed
```

No bundle, secret transfer or staging mutation occurred. Source pin remained
`801f8c3`; approval remains `received|not_consumed`. Mandatory runtime and OPS
re-audits passed, including AWG running/restart zero/unchanged 12-peer set and
`telegram_api_called=false`.

## Sanitized OCI layer diagnosis

A private read-only diagnostic emitted classifications, counts and aggregate
sizes only, then cleaned its production temp directory:

```text
layer_entry_count=6
layer_entry_exists_count=6
layer_oci_path_count=6
layer_other_path_count=0
rootfs_diff_id_count=6
layer_raw_matches_path_digest_count=6
layer_raw_matches_diff_id_count=0
layer_gzip_magic_count=6
layer_gzip_decode_ok_count=6
layer_gzip_decompressed_matches_diff_id_count=6
layer_gzip_decompressed_oversize_count=0
layer_gzip_decompressed_total_bytes=26048512
layer_gzip_decompressed_max_layer_bytes=7688192
production_temp_cleanup=passed
```

No path, digest, Config value, private target or secret was printed.

## Double-binding fix

For an exact `blobs/sha256/<64 lowercase hex>` layer, the validator now:

1. hashes raw stored bytes and requires equality with the OCI blob path;
2. accepts an uncompressed blob only when that same raw hash equals DiffID;
3. otherwise requires gzip magic, stream-decompresses and hashes the
   uncompressed bytes against the ordered RootFS DiffID;
4. enforces 64 MiB decompressed per layer and 128 MiB cumulative limits.

Non-OCI legacy layers retain raw-byte DiffID validation. Config path/self-hash,
canonical executable Config, `amd64/linux`, RootFS order/count and all prior
member/path/type/size limits remain unchanged. Errors reveal no bytes, paths or
digests.

## TDD and regression evidence

```text
red=3_failed_expected|validator_writer_restore
review_red=1_failed_expected|uncaught_corrupt_deflate_zlib_error
focused=9_passed
negative=blob_path_tamper|invalid_gzip|corrupt_deflate|wrong_uncompressed_content|per_layer_limit|two_layer_cumulative_limit
recovery_scope=57_passed
canonical_root_inventory=86_passed
python_compile=passed
git_diff_check=passed
```

## Security/diff review

Initial security review found one Important issue: corrupt DEFLATE could raise
an uncaught `zlib.error`, escaping the sanitized fail-closed contract. It also
found one Minor test gap: the cumulative limit case used only one layer. TDD
reproduced the raw `zlib.error`; the validator now normalizes it to generic
`RuntimeContractError`. An end-to-end path-bound corrupt-DEFLATE test and a
true two-layer cumulative-limit test were added.

Fresh rereview result:

```text
critical=0
important=0
minor=0
ready=yes
```

Production aggregate sizes are far below both new bounds. The protected
untracked `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` remains untouched and
must stay excluded from staging.

## Next step

Sync status, commit and push, then retry the same approved `801f8c3` gate. Any
mismatch remains fail-closed with mandatory cleanup and production AWG
re-audit.
