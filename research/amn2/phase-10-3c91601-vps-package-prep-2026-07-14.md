# AMN2 Phase 10: 3c91601 VPS package preparation

Дата: 2026-07-14.

Статус: `completed-local-package-ready-not-uploaded`.

## Source binding

```text
repository=worktrees/amn2-p7-c005-write-install
branch=codex-vps-test-prep
release_head=3c916015c10add37886370d04af70f0343f7f691
origin_head=3c916015c10add37886370d04af70f0343f7f691
origin_divergence=0_ahead_0_behind
working_tree=clean
current_vps_overlay=1c7fb78
vps_overlay_is_ancestor=true
commits_ahead_of_vps=9
```

Remote refs обновлены с включённой TLS certificate verification. Phase 10
branches `dc0ed92` и `e7f6246` уже входят в authoritative release line.
Source ZIP создан напрямую через `git archive` из verified commit; working-tree,
untracked и private files в него не входят.

## Artifacts

```text
package=dist/amn2-vps-update-and-smoke-kit-3c91601.zip
package_bytes=8800099
package_sha256=12E90EB54FCC374C84B6AA987C65E5644C4BD1B974089E81E16D00780389FB6E
package_sha256_file=dist/amn2-vps-update-and-smoke-kit-3c91601.zip.sha256.txt
source_zip=dist/amn2-vps-update-and-smoke-kit-3c91601/amn2-codex-vps-test-prep-3c91601-source.zip
source_bytes=8851519
source_sha256=5AD92A3A9D944825FEFDFEB4D56BDDBBB05390036E19E5AD197288C73812B0CB
apply_sha256=578A145E2AFE5BCC69B3730CE8C12BCE1BE368EC3B6DDD4847E94DD428D90DDA
smoke_sha256=4E49B183825603168108B227978F488A68EF31BC8BD11E2A839135CDE70E4106
```

Outer package содержит ровно пять reviewed entries: source ZIP, source
checksum, source apply tool, loopback API smoke tool и operator runbook.

## Content and security review

```text
package_entries=5
outer_names_match=true
package_content_mismatches=0
source_entries=371
source_files=328
source_dirs=43
required_missing=0
forbidden_entries=0
archive_comment_commit_match=true
source_sha_match=true
package_sha_match=true
canonical_apply_match=true
canonical_smoke_match=true
old_ecf8563_binding_count=0
shell_lf_no_bom=true
bash_syntax=passed
operator_markdown_hygiene=passed
private_key_literal_files=0
aws_key_literal_files=0
github_token_literal_files=0
telegram_token_literal_files=0
```

Delta от VPS overlay: `32 paths`, `12 added`, `20 modified`, `0 deleted`,
`4240 insertions`, `62 deletions`. Он включает plan device quotas, AWG2 H1-H4
contract hardening, read-only Drift Diagnostics, Device Passport, Enrollment
Ticket/lifecycle, authenticated web diagnostics и cascade physical-device
revoke. Public enrollment, hardware posture, MDM, drift auto-remediation и
Telegram polling не открываются.

## Extracted payload verification

Outer ZIP был извлечён в ignored `tmp`; тестировался именно packaged source,
а не исходный worktree. Read-only Git binding подтвердил exact release head.

```text
python=CPython_3.12.13
release_head_binding=3c916015c10add37886370d04af70f0343f7f691
extracted_git_status=clean
focused_impacted_suite=237_passed_1_warning
full_extracted_suite=870_passed_1_skipped_1_warning
python_compileall=passed
package_tooling_harness_markdown_tests=23_passed
orchestration_root_tests=43_passed
phase9_progress_harness_next_command=passed
phase9_progress_harness_product_diff=passed
diff_check=passed
diff_review=passed
```

Единственная warning относится к известной Starlette/httpx deprecation и не
является package или product regression. Два первоначальных harness запуска
были корректно отклонены только из-за неканонического command name; exact
registered `START_PHASE10_3C91601_VPS_PACKAGE_PREP_SLICE` прошёл без изменения
package payload.

## Boundary and next gate

Package не загружался на VPS и не применялся. Production SQLite, source,
services, users, devices, tickets, peers и configs не менялись; Telegram не
вызывался. AWG container не останавливался.

Loopback smoke tool создаёт и отзывает временные scoped API tokens, пишет safe
audit evidence и при разрешённой настройке синхронизирует server config в DB.
Поэтому следующий exact gate обязан сначала выполнить schema/smoke rehearsal
на clone DB. Запуск smoke против production DB и web restart требуют отдельного
явного scope; cascade revoke и любые peer/config действия остаются закрыты.

```text
next=RECORD_EXACT_3C91601_UPLOAD_SNAPSHOT_CLONE_DB_MIGRATION_ROLLBACK_SCOPE
launch_plan_change=false
live_upload=false
live_apply=false
```
