# Phase 11: 801f8c3 private Telegram overlay package preparation

Date: 2026-07-14.

Status: `completed-local-package-ready-not-uploaded`.

## Trigger

```text
GPT-5.6 SOL -> PREPARE_PHASE11_801F8C3_PRIVATE_TELEGRAM_SMOKE_OVERLAY_PACKAGE_AND_ROLLOUT_GATE
```

## Source binding

```text
repository=worktrees/amn2-p7-c005-write-install
branch=codex-vps-test-prep
release_head=801f8c3406121549eb6a19150be009cfc0ea88d0
origin_head=801f8c3406121549eb6a19150be009cfc0ea88d0
origin_divergence=0_ahead_0_behind
working_tree=clean
current_production_overlay=3c91601
delta_paths=2
delta_insertions=54
delta_deletions=1
```

The exact source archive was generated with `git archive` from commit
`801f8c3`. Its ZIP comment contains the full release commit. Untracked,
working-tree and private files are not present.

The production delta is limited to:

```text
app/bot/controlled_smoke.py
tests/bot/test_controlled_smoke.py
```

There is no schema, API, web, systemd, peer, config or migration delta.

## Artifacts

```text
package=dist/amn2-private-telegram-smoke-overlay-801f8c3.zip
package_bytes=8794194
package_sha256=693DF74192E55A2231F45C0ADF153B745C7D2AF8EDEDA67830D02CB620A4C3FF
package_sha256_file=dist/amn2-private-telegram-smoke-overlay-801f8c3.zip.sha256.txt
source_zip=dist/amn2-private-telegram-smoke-overlay-801f8c3/amn2-codex-vps-test-prep-801f8c3-source.zip
source_bytes=8851677
source_entries=371
source_sha256=B332CB1DCFB85768ACE0DF78E038B955F7C853989CF1C67CDE0233FA51EBD6C3
apply_sha256=85AE2C0E5A1E949529342AF2939A577AE23B3924653A344E1E77465B898E56AF
runbook_sha256=923DBB704BDDF464DEB1D3037703B58AF8B102CFCC3A174509A05FB3FB4B42CC
```

The outer archive contains exactly four root entries: the source ZIP, source
checksum, checksum-bound apply tool and operator runbook. The Phase 10 API
smoke tool is intentionally excluded because this change has no API/schema
delta and that tool would introduce irrelevant clone writes.

## Package and security review

```text
outer_entries=4
outer_names_match=true
outer_sha_match=true
source_sha_match=true
source_archive_comment_match=true
source_zip_test=passed
required_missing=0
forbidden_entries=0
canonical_apply_binding_only=true
apply_lf_no_bom=true
bash_syntax=passed
runbook_markdown_hygiene=passed
private_key_literal_files=0
aws_key_literal_files=0
github_token_literal_files=0
new_or_unclassified_telegram_token_literals=0
```

A deliberately broad scan found two identical token-shaped examples in the
English and Russian beginner guides. Their values were never printed. Both
files are unchanged from production overlay `3c91601`; the examples are
identical, low-entropy documentation placeholders and are not part of the
`801f8c3` delta. They are recorded explicitly instead of being misreported as
new credentials.

The packaged apply tool is byte-equivalent to the canonical reviewed tool
after normalizing only three bindings: source path, source SHA-256 and expected
commit.

## Extracted-payload verification

The outer package and source ZIP were extracted to new ignored verification
directories. Tests ran against the extracted packaged source, not the AMN2
worktree:

```text
packaged_controlled_smoke_and_bootstrap=21_passed
packaged_bot_and_settings=184_passed
packaged_compileall=passed
apply_tool_harness_markdown_root=23_passed
phase9_progress_harness=passed
git_diff_check=passed
```

The first content verifier correctly stopped, but its initial forbidden-path
check matched the outer `tmp` verification directory rather than relative ZIP
paths. The corrected fail-closed check used paths relative to the source root
and passed with zero forbidden entries. A second verifier issue was also
closed: PowerShell now explicitly checks external-process exit status rather
than treating a Python nonzero result as success.

## Rollback and runtime boundary

Because the package contains a full tracked-source archive, the future live
gate must briefly stop only `amneziya-web.service` before applying files. This
avoids overlaying a full source tree under a running Python process even though
the functional delta does not touch web code.

The future gate must create a tracked-source snapshot, overlay-marker backup
and SQLite backup before apply. It must not initialize schema, run API smoke or
write production SQLite. After source apply, it starts only the web service and
rechecks database logical invariants, private listeners, regular bot disabled
state and AWG continuity.

AWG must never be stopped, restarted, recreated or reconfigured. Production
overlay remains `3c91601`; no VPS/SSH/Telegram action occurred during package
preparation.

## Next command

```text
GPT-5.6 SOL -> REVIEW_PHASE11_801F8C3_PRIVATE_OVERLAY_ROLLOUT_GATE_AND_PREPARE_EXACT_APPROVAL
```

That review must bind the package commit and all four artifact hashes, define
preflight, source/SQLite snapshot, offline apply, verification and automatic
rollback, and prepare—but not execute—the separate exact live approval phrase.
