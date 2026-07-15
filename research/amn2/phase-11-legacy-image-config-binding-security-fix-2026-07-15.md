# Phase 11 legacy Docker image executable-config binding security fix

Date: 2026-07-15.

Decision: SECURITY BLOCKER FIXED; CLEAN DIFF SCAN PASSED; LIVE RESTORE NOT YET RETRIED.

## Blocker

The sealed pre-fix scan validated P11-LEGACY-IMAGE-CONFIG-UNBOUND-001:
the runtime-complete v2 verifier bound RootFS DiffIDs and layer bytes but did
not bind non-RootFS executable Docker image Config. A synthetic Healthcheck
change with identical RootFS was therefore accepted. The finding was Medium,
high confidence, and blocked the approved RESTORE-001A retry.

## Remediation

The runtime contract keeps schema amn2-awg-runtime-v2 and now records only:

- SHA-256 of canonical daemon-inspected executable Config;
- exact amd64 architecture;
- exact linux OS;
- the existing immutable image ID, reference and ordered RootFS DiffIDs.

The independent offline verifier recomputes the canonical executable Config
digest from image.tar, verifies architecture and OS, and retains config-file,
RootFS and per-layer digest validation. Raw image Config values are not stored
in runtime.json, reports or error text. Legacy daemon image IDs remain accepted
only when the full executable-config and filesystem identity matches.

## Production compatibility evidence

An approval-bounded read-only diagnostic compared the current production
daemon image Config and exported archive Config without printing values.
Canonical Config, architecture and OS matched; production temporary material
was removed. Production AWG and the regular bot were untouched.

## Verification

    tdd_red=changed_config_same_rootfs_was_accepted
    runtime_validator_tests=15_passed
    recovery_scoped_tests=41_passed
    root_full_tests=70_passed
    independent_verifier_pair=35_passed
    git_diff_check=passed_with_only_existing_crlf_conversion_warnings

The original sealed PoC now fails at the strengthened mandatory function
boundary. Adapted low-level and full runtime-complete-v2 regressions prove the
actual executable-config mismatch is rejected.

## Clean security rescan

    scan_id=1f480ae_fix_20260715T075110Z
    snapshot=codex-security-snapshot/v1:sha256:d56c7864892bdf6f024b1e701b93577a286f1f7d467d50fde2882437757ae12c
    coverage=complete
    full_file_receipts=6_of_6
    reportable_findings=0
    sealed_artifacts=5

The scan covered the writer, independent verifier, runtime/image validator and
their three directly supporting regression files. The unrelated user-owned
docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md was explicitly excluded.

## Live and destructive boundary

No production or staging VPS command, source upload, bundle creation, secret
transfer, Docker install/load/start, restore apply, service restart, Telegram
call, AWG mutation, old fallback deletion, provider deletion or key cleanup was
performed by this fix slice.

The existing exact RESTORE-001A approval is received but not consumed. The next
ordered step is docs/status sync, commit and push, followed by the already
approved live rehearsal with mandatory cleanup and production AWG re-audit.
Old fallback deletion and second-VPS retirement remain later separate exact
destructive gates.
