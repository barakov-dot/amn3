#!/usr/bin/env bash
set -Eeuo pipefail

package_id='phase16-awg3-family-3-1-spain-pilot-20260824-010'
required_gate='APPLICATION_STAGE'
claim_path="${PHASE16_STAGE_CLAIM_FILE:-}"
state_hash="${PHASE16_EXPECTED_CURRENT_STATE_SHA256:-}"
manifest_hash="${PHASE16_MANIFEST_SHA256:-}"
package_identity="${PHASE16_PACKAGE_IDENTITY_SHA256:-}"
rollback_hash="${PHASE16_ROLLBACK_SCOPE_SHA256:-}"
supplied_package_id="${PHASE16_PACKAGE_ID:-}"
supplied_gate="${PHASE16_FUTURE_GATE:-}"

/usr/bin/python3 -I -B - "$claim_path" "$0" "$package_id" "$required_gate" "$state_hash" "$manifest_hash" "$package_identity" "$rollback_hash" "$supplied_package_id" "$supplied_gate" <<'PHASE16_STAGE_PY'
import datetime
import hashlib
import json
import os
import re
import stat
import sys

MAX_CLAIM_BYTES = 8192
MAX_SCRIPT_BYTES = 1048576

def stop(reason, code):
    sys.stderr.buffer.write(reason.encode("ascii") + b"\n")
    raise SystemExit(code)

def read_regular_bounded(path, maximum_bytes):
    before = os.lstat(path)
    if not stat.S_ISREG(before.st_mode) or before.st_size < 1:
        raise ValueError("regular bounded file")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise ValueError("file identity")
        raw = os.read(descriptor, maximum_bytes + 1)
        if not raw or len(raw) > maximum_bytes or os.read(descriptor, 1):
            raise ValueError("file size")
        return raw
    finally:
        os.close(descriptor)

(
    claim_path, script_path, package_id, gate, state_hash, manifest_hash,
    package_identity, rollback_hash, supplied_package_id, supplied_gate,
) = sys.argv[1:]
if not claim_path:
    stop("claim_required", 64)
try:
    raw = read_regular_bounded(claim_path, MAX_CLAIM_BYTES)
    def exact_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate key")
            value[key] = item
        return value
    claim = json.loads(raw.decode("utf-8"), object_pairs_hook=exact_object)
    canonical = json.dumps(
        claim, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8") + b"\n"
    exact = {
        "claim_id", "consumed_at", "expected_current_state_sha256", "expires_at",
        "future_gate", "issued_at", "manifest_sha256", "package_id",
        "package_identity_sha256", "rollback_scope_sha256", "schema",
        "stage_script_sha256", "status",
    }
    sha = r"[0-9a-f]{64}"
    valid = isinstance(claim, dict) and canonical == raw and set(claim) == exact
    valid = valid and supplied_package_id == package_id and supplied_gate == gate
    valid = valid and all(re.fullmatch(sha, value) for value in (state_hash, manifest_hash, package_identity, rollback_hash))
    valid = valid and claim["schema"] == "amn2.phase16.stage-claim.v1"
    valid = valid and claim["package_id"] == package_id and claim["future_gate"] == gate
    valid = valid and claim["expected_current_state_sha256"] == state_hash
    valid = valid and claim["manifest_sha256"] == manifest_hash
    valid = valid and claim["package_identity_sha256"] == package_identity
    valid = valid and claim["rollback_scope_sha256"] == rollback_hash
    valid = valid and claim["status"] == "issued" and claim["consumed_at"] is None
    valid = valid and isinstance(claim["claim_id"], str) and re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", claim["claim_id"])
    script_hash = hashlib.sha256(read_regular_bounded(script_path, MAX_SCRIPT_BYTES)).hexdigest()
    valid = valid and claim["stage_script_sha256"] == script_hash
    def timestamp(value):
        if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value) is None:
            raise ValueError("timestamp")
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    issued = timestamp(claim["issued_at"])
    expires = timestamp(claim["expires_at"])
    now = datetime.datetime.now(datetime.timezone.utc)
    valid = valid and issued <= now < expires and issued < expires
except (OSError, UnicodeError, ValueError, TypeError, KeyError, json.JSONDecodeError):
    valid = False
if not valid:
    stop("claim_invalid", 65)
PHASE16_STAGE_PY

package_root="${PHASE16_PACKAGE_ROOT:-}"
release_root="${PHASE16_APPLICATION_RELEASE_ROOT:-}"
database_path="${PHASE16_DATABASE_PATH:-}"
ledger_path="${PHASE16_STAGE_LEDGER:-}"
expected_package_root='/var/lib/amn2-phase16/package'
expected_release_root="/opt/amn2-spain/releases/${package_id}"
expected_database_path='/var/lib/amn2-spain/amn2.db'
expected_ledger_path='/var/lib/amn2-phase16/stage/application.json'

if [[ -z "$package_root" || -z "$release_root" || -z "$database_path" || -z "$ledger_path" ]]; then
    printf '%s\n' 'stage_inputs_required' >&2
    exit 66
fi
if [[ "$package_root" != "$expected_package_root" || "$release_root" != "$expected_release_root" || "$database_path" != "$expected_database_path" || "$ledger_path" != "$expected_ledger_path" ]]; then
    printf '%s\n' 'stage_inputs_invalid' >&2
    exit 67
fi

backup_path="/var/lib/amn2-phase16/rollback/application/${state_hash}.sqlite3"
staging_root="${release_root}.staging"
release_created=false

rollback_application_stage() {
    local status=$?
    trap - ERR
    if [[ "$release_created" == true && -d "$release_root" ]]; then
        /usr/bin/rm -rf --one-file-system "$release_root"
    fi
    if [[ -d "$staging_root" ]]; then
        /usr/bin/rm -rf --one-file-system "$staging_root"
    fi
    printf '%s\n' 'application_stage_rolled_back' >&2
    exit "$status"
}
trap rollback_application_stage ERR

create_checksum_bound_db_backup() {
    [[ -f "$database_path" && ! -L "$database_path" ]]
    /usr/bin/install -d -m 0700 "$(dirname "$backup_path")"
    [[ ! -e "$backup_path" ]]
    /usr/bin/sqlite3 "$database_path" ".backup '$backup_path'"
    /usr/bin/chmod 0600 "$backup_path"
    /usr/bin/sha256sum "$backup_path" >/dev/null
}

consume_stage_claim() {
    /usr/bin/python3 -I -B - "$claim_path" <<'PHASE16_CONSUME_PY'
import datetime, json, os, sys, tempfile
path = sys.argv[1]
with open(path, "rb") as stream:
    value = json.load(stream)
value["status"] = "consumed"
value["consumed_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
directory = os.path.dirname(os.path.abspath(path))
descriptor, temporary = tempfile.mkstemp(prefix=".phase16-claim-", dir=directory)
try:
    os.write(descriptor, raw)
    os.fsync(descriptor)
finally:
    os.close(descriptor)
os.replace(temporary, path)
PHASE16_CONSUME_PY
}

stage_application_snapshot() {
    [[ -f "$package_root/manifest.json" && -d "$package_root/source/app" ]]
    [[ ! -e "$release_root" && ! -e "$staging_root" ]]
    /usr/bin/install -d -m 0750 "$staging_root"
    /usr/bin/cp -a "$package_root/source/." "$staging_root/"
    /usr/bin/python3 -I -B -m compileall -q "$staging_root/app"
    /usr/bin/mv "$staging_root" "$release_root"
    release_created=true
}

write_stage_ledger() {
    /usr/bin/install -d -m 0700 "$(dirname "$ledger_path")"
    /usr/bin/python3 -I -B - "$ledger_path" "$release_root" "$backup_path" "$package_id" "$package_identity" "$state_hash" <<'PHASE16_LEDGER_PY'
import json, os, sys, tempfile
path, release, backup, package_id, package_identity, state_hash = sys.argv[1:]
value = {"application_release": release, "backup": backup, "package_id": package_id, "package_identity_sha256": package_identity, "rollback_scope": ["application_release"], "state_sha256": state_hash, "status": "staged"}
raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
descriptor, temporary = tempfile.mkstemp(prefix=".application-ledger-", dir=os.path.dirname(path))
try:
    os.write(descriptor, raw)
    os.fsync(descriptor)
finally:
    os.close(descriptor)
os.replace(temporary, path)
PHASE16_LEDGER_PY
}

consume_stage_claim
create_checksum_bound_db_backup
stage_application_snapshot
write_stage_ledger
trap - ERR
printf '%s\n' '{"general_issuance_enabled":false,"result":"application_staged"}'
