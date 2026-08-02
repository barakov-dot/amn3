#!/usr/bin/env bash
set -eu

umask 077

EXPECTED_AWG2_FOUNDATION_SHA256='0e5a5926821d88ae4a2515f9e95cd7c3f69db52100c1a1ec74e99fb794222281'
EXPECTED_FOREIGN_RECEIPT_SHA256='bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704'
EXPECTED_FOREIGN_STABLE_SHA256='f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8'
MAX_USA_EVIDENCE_AGE_SECONDS=3600

fail() {
    printf 'stage=%s result=failed reason=%s\n' "$1" "$2" >&2
    exit 1
}

case "${1-}" in
    preflight|stage|verify-stage|rollback-stage)
        MODE=$1
        ;;
    *)
        fail unknown unsupported_mode
        ;;
esac
[ "$#" -eq 1 ] || fail "$MODE" unsupported_mode

# Task 7 deliberately has no production/live mode. A later exact gate must
# replace this local harness boundary rather than reusing an old approval.
[ "${AMN2_PHASE13_LOCAL_FAKE_HARNESS-}" = '1' ] \
    || fail "$MODE" local_fake_harness_required
FAKE_ROOT=${AMN2_PHASE13_FAKE_ROOT-}
case "$FAKE_ROOT" in
    /*|[A-Za-z]:/*) ;;
    *) fail "$MODE" local_fake_root_invalid ;;
esac
case "$FAKE_ROOT" in
    *$'\n'*|*$'\r'*) fail "$MODE" local_fake_root_invalid ;;
esac
[ -d "$FAKE_ROOT" ] && [ ! -L "$FAKE_ROOT" ] \
    || fail "$MODE" local_fake_root_invalid
FAKE_SENTINEL="$FAKE_ROOT/.amn2-phase13-local-fake-harness"
[ -f "$FAKE_SENTINEL" ] && [ ! -L "$FAKE_SENTINEL" ] \
    && [ "$(cat -- "$FAKE_SENTINEL")" = 'task7-local-only' ] \
    || fail "$MODE" local_fake_root_invalid

PACKAGE_ROOT="$FAKE_ROOT/package"
STAGE_INPUT_ROOT="$FAKE_ROOT/stage-inputs"
OBSERVED_STATE="$FAKE_ROOT/observed/state"
LIVE_DB="$FAKE_ROOT/var/lib/amn2-spain/amn2.sqlite3"
BOT_ENABLE_MARKER="$FAKE_ROOT/etc/amn2-spain/bot-enabled"
PROTECTED_ROOT="$FAKE_ROOT/var/lib/amn2-phase13-bot-web-migration"
STAGED_ROOT="$PROTECTED_ROOT/staged"

for safe_directory in \
    "$PACKAGE_ROOT" \
    "$STAGE_INPUT_ROOT" \
    "$FAKE_ROOT/observed" \
    "$FAKE_ROOT/var" \
    "$FAKE_ROOT/var/lib" \
    "$FAKE_ROOT/var/lib/amn2-spain"
do
    [ -d "$safe_directory" ] && [ ! -L "$safe_directory" ] \
        || fail "$MODE" local_fake_root_invalid
done

NOW_EPOCH=${AMN2_PHASE13_TEST_NOW_EPOCH-}
case "$NOW_EPOCH" in
    ''|*[!0-9]*) fail "$MODE" local_fake_clock_invalid ;;
esac

verify_package_and_stage_inputs() {
    python - "$PACKAGE_ROOT" "$STAGE_INPUT_ROOT" "$NOW_EPOCH" <<'PY'
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import sys


package = Path(sys.argv[1])
stage_inputs = Path(sys.argv[2])
now = datetime.fromtimestamp(int(sys.argv[3]), tz=timezone.utc)


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def regular_bytes(path: Path) -> bytes:
    metadata = os.lstat(path)
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ValueError("unsafe file")
    return path.read_bytes()


def canonical_object(path: Path) -> dict[str, object]:
    raw = regular_bytes(path)
    value = json.loads(raw)
    if not isinstance(value, dict) or canonical(value) != raw:
        raise ValueError("non-canonical json")
    return value


for root in (package, stage_inputs):
    metadata = os.lstat(root)
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ValueError("unsafe root")

direct_paths = {
    "merge_preview": "merge-preview.json",
    "merged_target_db": "merged-target.sqlite3.enc",
    "rollback_plan": "rollback-plan.json",
    "source_full_backup": "source-full-backup.enc",
    "target_before_backup": "target-before-backup.enc",
}
indirect_paths = {
    "migration-plan.json",
    "source-audit.json",
    "ssh-runner.ps1",
    "target-audit.json",
}
expected_package_files = set(direct_paths.values()) | indirect_paths | {"manifest.json"}
if {path.name for path in package.iterdir()} != expected_package_files:
    raise ValueError("package file set")

manifest = canonical_object(package / "manifest.json")
if set(manifest) != {
    "artifacts",
    "created_at",
    "expires_at",
    "live_mutation_authorized",
    "outcome_id",
    "schema",
    "source_audit_sha256",
    "source_role",
    "target_audit_sha256",
    "target_role",
}:
    raise ValueError("manifest keys")
if (
    manifest["schema"] != "amn2.phase13.bot-web-migration-manifest.v1"
    or manifest["source_role"] != "usa-source"
    or manifest["target_role"] != "spain-target"
    or manifest["live_mutation_authorized"] is not False
):
    raise ValueError("manifest contract")
expires_at = datetime.fromisoformat(str(manifest["expires_at"]).replace("Z", "+00:00"))
if expires_at.tzinfo is None or expires_at.astimezone(timezone.utc) <= now:
    raise ValueError("manifest expired")
artifacts = manifest["artifacts"]
if not isinstance(artifacts, dict) or set(artifacts) != set(direct_paths):
    raise ValueError("manifest artifact set")
for key, name in direct_paths.items():
    binding = artifacts[key]
    if not isinstance(binding, dict) or set(binding) != {"path", "sha256", "size"}:
        raise ValueError("manifest artifact binding")
    value = regular_bytes(package / name)
    if (
        binding["path"] != name
        or binding["size"] != len(value)
        or binding["sha256"] != sha256(value)
    ):
        raise ValueError("manifest artifact mismatch")
if manifest["source_audit_sha256"] != sha256(
    regular_bytes(package / "source-audit.json")
) or manifest["target_audit_sha256"] != sha256(
    regular_bytes(package / "target-audit.json")
):
    raise ValueError("audit cross binding")

rollback = canonical_object(package / "rollback-plan.json")
bindings = rollback.get("artifact_bindings")
if (
    set(rollback)
    != {
        "artifact_bindings",
        "live_mutation_authorized",
        "restore_apply_authorized",
        "schema",
    }
    or rollback["schema"]
    != "amn2.phase13.bot-web-migration-rollback-plan.v1"
    or rollback["live_mutation_authorized"] is not False
    or rollback["restore_apply_authorized"] is not False
    or not isinstance(bindings, dict)
    or set(bindings) != indirect_paths
):
    raise ValueError("rollback binding contract")
for name in indirect_paths:
    binding = bindings[name]
    value = regular_bytes(package / name)
    if (
        not isinstance(binding, dict)
        or set(binding) != {"sha256", "size"}
        or binding["size"] != len(value)
        or binding["sha256"] != sha256(value)
    ):
        raise ValueError("rollback binding mismatch")

expected_stage_files = {
    "amn2-spain-bot.service",
    "bindings.json",
    "runtime.env.delta.enc",
}
if {path.name for path in stage_inputs.iterdir()} != expected_stage_files:
    raise ValueError("stage input file set")
stage_bindings = canonical_object(stage_inputs / "bindings.json")
if (
    set(stage_bindings) != {"artifacts", "live_mutation_authorized", "schema"}
    or stage_bindings["schema"]
    != "amn2.phase13.bot-web-disabled-stage-inputs.v1"
    or stage_bindings["live_mutation_authorized"] is not False
):
    raise ValueError("stage input contract")
stage_paths = {
    "bot_unit": "amn2-spain-bot.service",
    "runtime_env_delta": "runtime.env.delta.enc",
}
stage_artifacts = stage_bindings["artifacts"]
if not isinstance(stage_artifacts, dict) or set(stage_artifacts) != set(stage_paths):
    raise ValueError("stage input artifacts")
for key, name in stage_paths.items():
    binding = stage_artifacts[key]
    value = regular_bytes(stage_inputs / name)
    if (
        not isinstance(binding, dict)
        or set(binding) != {"path", "sha256", "size"}
        or binding["path"] != name
        or binding["size"] != len(value)
        or binding["sha256"] != sha256(value)
    ):
        raise ValueError("stage input mismatch")

unit = regular_bytes(stage_inputs / "amn2-spain-bot.service").decode("utf-8")
if (
    "\nConditionPathExists=/etc/amn2-spain/bot-enabled\n" not in "\n" + unit
    or "\n[Install]\nWantedBy=multi-user.target\n" not in "\n" + unit
):
    raise ValueError("bot unit contract")
PY
}

BOT_ACTIVE='__missing__'
BOT_PROCESS_COUNT='__missing__'
BOT_ENABLE_MARKER_PRESENT='__missing__'
SPAIN_WEB_ACTIVE='__missing__'
SPAIN_WEB_LOOPBACK_ONLY='__missing__'
SPAIN_WEB_HEALTHY='__missing__'
USA_BOT_ACTIVE='__missing__'
USA_EVIDENCE_CHECKED_AT_EPOCH='__missing__'
TARGET_DB_SHA256_BEFORE='__missing__'
AWG2_FOUNDATION_SHA256='__missing__'
FOREIGN_RECEIPT_SHA256='__missing__'
FOREIGN_STABLE_SHA256='__missing__'

read_observed_state() {
    [ -f "$OBSERVED_STATE" ] && [ ! -L "$OBSERVED_STATE" ] || return 1
    while IFS='=' read -r key value; do
        [ -n "$key" ] || continue
        case "$key" in
            BOT_ACTIVE|BOT_PROCESS_COUNT|BOT_ENABLE_MARKER_PRESENT|\
            SPAIN_WEB_ACTIVE|SPAIN_WEB_LOOPBACK_ONLY|SPAIN_WEB_HEALTHY|\
            USA_BOT_ACTIVE|USA_EVIDENCE_CHECKED_AT_EPOCH|\
            TARGET_DB_SHA256_BEFORE|AWG2_FOUNDATION_SHA256|\
            FOREIGN_RECEIPT_SHA256|FOREIGN_STABLE_SHA256)
                eval "current=\${$key}"
                [ "$current" = '__missing__' ] || return 1
                printf -v "$key" '%s' "$value"
                ;;
            *) return 1 ;;
        esac
    done < "$OBSERVED_STATE"
    for value in \
        "$BOT_ACTIVE" "$BOT_PROCESS_COUNT" "$BOT_ENABLE_MARKER_PRESENT" \
        "$SPAIN_WEB_ACTIVE" "$SPAIN_WEB_LOOPBACK_ONLY" "$SPAIN_WEB_HEALTHY" \
        "$USA_BOT_ACTIVE" "$USA_EVIDENCE_CHECKED_AT_EPOCH" \
        "$TARGET_DB_SHA256_BEFORE" "$AWG2_FOUNDATION_SHA256" \
        "$FOREIGN_RECEIPT_SHA256" "$FOREIGN_STABLE_SHA256"
    do
        [ "$value" != '__missing__' ] || return 1
    done
}

sha256_file() {
    sha256sum -- "$1" | awk '{print $1}'
}

run_preflight() {
    verify_package_and_stage_inputs >/dev/null 2>&1 \
        || fail preflight package_invalid
    read_observed_state || fail preflight observation_invalid

    [ "$BOT_ACTIVE" = 'false' ] || fail preflight bot_not_disabled
    [ "$BOT_PROCESS_COUNT" = '0' ] || fail preflight bot_process_present
    [ "$BOT_ENABLE_MARKER_PRESENT" = 'false' ] \
        || fail preflight bot_marker_present
    if [ -e "$BOT_ENABLE_MARKER" ] || [ -L "$BOT_ENABLE_MARKER" ]; then
        fail preflight bot_marker_present
    fi
    [ "$SPAIN_WEB_ACTIVE" = 'true' ] && [ "$SPAIN_WEB_HEALTHY" = 'true' ] \
        || fail preflight web_not_healthy
    [ "$SPAIN_WEB_LOOPBACK_ONLY" = 'true' ] \
        || fail preflight web_not_loopback_only
    [ "$USA_BOT_ACTIVE" = 'true' ] || fail preflight usa_evidence_invalid

    case "$USA_EVIDENCE_CHECKED_AT_EPOCH" in
        ''|*[!0-9]*) fail preflight usa_evidence_invalid ;;
    esac
    evidence_age=$((NOW_EPOCH - USA_EVIDENCE_CHECKED_AT_EPOCH))
    [ "$evidence_age" -ge 0 ] && [ "$evidence_age" -le "$MAX_USA_EVIDENCE_AGE_SECONDS" ] \
        || fail preflight usa_evidence_stale

    [ "$AWG2_FOUNDATION_SHA256" = "$EXPECTED_AWG2_FOUNDATION_SHA256" ] \
        || fail preflight awg2_foundation_mismatch
    [ "$FOREIGN_RECEIPT_SHA256" = "$EXPECTED_FOREIGN_RECEIPT_SHA256" ] \
        || fail preflight foreign_foundation_mismatch
    [ "$FOREIGN_STABLE_SHA256" = "$EXPECTED_FOREIGN_STABLE_SHA256" ] \
        || fail preflight foreign_foundation_mismatch

    [ -f "$LIVE_DB" ] && [ ! -L "$LIVE_DB" ] \
        || fail preflight target_db_invalid
    printf '%s\n' "$TARGET_DB_SHA256_BEFORE" \
        | grep -Eq '^[0-9a-f]{64}$' \
        || fail preflight target_db_invalid
    [ "$(sha256_file "$LIVE_DB")" = "$TARGET_DB_SHA256_BEFORE" ] \
        || fail preflight target_db_changed
}

atomic_stage_copy() {
    source_path=$1
    destination_path=$2
    temp_path="$STAGED_ROOT/.tmp-${destination_path##*/}-$$"
    cp -- "$source_path" "$temp_path" || return 1
    chmod 0600 "$temp_path" || return 1
    mv -- "$temp_path" "$destination_path" || return 1
}

cleanup_incomplete_stage() {
    rm -f -- \
        "$STAGED_ROOT/merged-target.sqlite3.enc" \
        "$STAGED_ROOT/runtime.env.delta.enc" \
        "$STAGED_ROOT/amn2-spain-bot.service" \
        "$STAGED_ROOT"/.tmp-* 2>/dev/null || true
    rmdir -- "$STAGED_ROOT" 2>/dev/null || true
    rmdir -- "$PROTECTED_ROOT" 2>/dev/null || true
}

create_stage() {
    if [ -e "$PROTECTED_ROOT" ] || [ -L "$PROTECTED_ROOT" ]; then
        fail stage stage_root_exists
    fi
    mkdir -m 0700 -- "$PROTECTED_ROOT" || fail stage stage_write_failed
    if ! mkdir -m 0700 -- "$STAGED_ROOT" \
        || ! atomic_stage_copy \
            "$PACKAGE_ROOT/merged-target.sqlite3.enc" \
            "$STAGED_ROOT/merged-target.sqlite3.enc" \
        || ! atomic_stage_copy \
            "$STAGE_INPUT_ROOT/runtime.env.delta.enc" \
            "$STAGED_ROOT/runtime.env.delta.enc" \
        || ! atomic_stage_copy \
            "$STAGE_INPUT_ROOT/amn2-spain-bot.service" \
            "$STAGED_ROOT/amn2-spain-bot.service"
    then
        cleanup_incomplete_stage
        fail stage stage_write_failed
    fi
}

verify_staged_files() {
    python - \
        "$STAGED_ROOT" \
        "$PACKAGE_ROOT/merged-target.sqlite3.enc" \
        "$STAGE_INPUT_ROOT/runtime.env.delta.enc" \
        "$STAGE_INPUT_ROOT/amn2-spain-bot.service" <<'PY'
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
import sys


staged = Path(sys.argv[1])
sources = {
    "merged-target.sqlite3.enc": Path(sys.argv[2]),
    "runtime.env.delta.enc": Path(sys.argv[3]),
    "amn2-spain-bot.service": Path(sys.argv[4]),
}
metadata = os.lstat(staged)
if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
    raise ValueError("unsafe staged root")
if {path.name for path in staged.iterdir()} != set(sources):
    raise ValueError("staged file set")
for name, source in sources.items():
    destination = staged / name
    item = os.lstat(destination)
    if stat.S_ISLNK(item.st_mode) or not stat.S_ISREG(item.st_mode):
        raise ValueError("unsafe staged file")
    if os.name != "nt" and stat.S_IMODE(item.st_mode) != 0o600:
        raise ValueError("staged file mode")
    if hashlib.sha256(destination.read_bytes()).digest() != hashlib.sha256(
        source.read_bytes()
    ).digest():
        raise ValueError("staged file checksum")
PY
}

rollback_stage() {
    if [ ! -e "$PROTECTED_ROOT" ] && [ ! -L "$PROTECTED_ROOT" ]; then
        return 0
    fi
    [ -d "$PROTECTED_ROOT" ] && [ ! -L "$PROTECTED_ROOT" ] \
        || fail rollback-stage stage_invalid
    [ -d "$STAGED_ROOT" ] && [ ! -L "$STAGED_ROOT" ] \
        || fail rollback-stage stage_invalid
    python - "$STAGED_ROOT" <<'PY' >/dev/null 2>&1 \
        || fail rollback-stage stage_invalid
from __future__ import annotations

import os
from pathlib import Path
import stat
import sys


staged = Path(sys.argv[1])
expected = {
    "amn2-spain-bot.service",
    "merged-target.sqlite3.enc",
    "runtime.env.delta.enc",
}
paths = list(staged.iterdir())
if {path.name for path in paths} != expected:
    raise ValueError("unexpected staged content")
for path in paths:
    item = os.lstat(path)
    if stat.S_ISLNK(item.st_mode) or not stat.S_ISREG(item.st_mode):
        raise ValueError("unsafe staged content")
PY
    rm -f -- \
        "$STAGED_ROOT/merged-target.sqlite3.enc" \
        "$STAGED_ROOT/runtime.env.delta.enc" \
        "$STAGED_ROOT/amn2-spain-bot.service" \
        || fail rollback-stage stage_write_failed
    rmdir -- "$STAGED_ROOT" || fail rollback-stage stage_write_failed
    rmdir -- "$PROTECTED_ROOT" || fail rollback-stage stage_write_failed
}

case "$MODE" in
    preflight)
        run_preflight
        printf 'stage=preflight result=passed\n'
        ;;
    stage)
        run_preflight
        create_stage
        verify_staged_files >/dev/null 2>&1 || {
            cleanup_incomplete_stage
            fail stage stage_invalid
        }
        printf 'stage=stage result=passed\n'
        ;;
    verify-stage)
        run_preflight
        verify_staged_files >/dev/null 2>&1 \
            || fail verify-stage stage_invalid
        printf 'stage=verify-stage result=passed\n'
        ;;
    rollback-stage)
        rollback_stage
        printf 'stage=rollback-stage result=passed\n'
        ;;
esac
