#!/usr/bin/env bash
set -Eeuo pipefail

package_id='phase15-dual-protocol-bootstrap-20260811-001'
required_gate='APPLICATION_STAGE'
claim_path="${PHASE15_STAGE_CLAIM_FILE:-}"
supplied_package_id="${PHASE15_PACKAGE_ID:-}"
supplied_gate="${PHASE15_FUTURE_GATE:-}"
state_hash="${PHASE15_EXPECTED_CURRENT_STATE_SHA256:-}"

exec -c /usr/bin/python3 -I -B - "$claim_path" "$0" "$package_id" "$required_gate" "$state_hash" "$supplied_package_id" "$supplied_gate" <<'PHASE15_STAGE_PY'
import datetime
import hashlib
import json
import os
import re
import stat
import sys

MAX_CLAIM_BYTES = 4096
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
        chunks = bytearray()
        while len(chunks) < maximum_bytes + 1:
            chunk = os.read(descriptor, min(4096, maximum_bytes + 1 - len(chunks)))
            if not chunk:
                break
            chunks.extend(chunk)
        if not chunks or maximum_bytes < len(chunks):
            raise ValueError("file size")
        return bytes(chunks)
    finally:
        os.close(descriptor)

claim_path, script_path, package_id, gate, state_hash, supplied_package_id, supplied_gate = sys.argv[1:]
if not claim_path:
    stop("claim_required", 64)
try:
    raw = read_regular_bounded(claim_path, MAX_CLAIM_BYTES)
except FileNotFoundError:
    stop("claim_required", 64)
except (OSError, ValueError):
    stop("claim_invalid", 65)

try:
    def exact_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result
    claim = json.loads(raw.decode("utf-8"), object_pairs_hook=exact_object)
    canonical = json.dumps(claim, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n"
    exact = {
        "claim_id", "consumed_at", "expected_current_state_sha256", "expires_at",
        "future_gate", "issued_at", "package_id", "schema", "stage_script_sha256", "status",
    }
    valid = isinstance(claim, dict) and canonical == raw and set(claim) == exact
    valid = valid and supplied_package_id == package_id and supplied_gate == gate
    valid = valid and re.fullmatch(r"[0-9a-f]{64}", state_hash) is not None
    valid = valid and claim["schema"] == "amn2.phase15.stage-claim.v1"
    valid = valid and claim["package_id"] == package_id and claim["future_gate"] == gate
    valid = valid and claim["expected_current_state_sha256"] == state_hash
    valid = valid and claim["status"] == "issued" and claim["consumed_at"] is None
    valid = valid and isinstance(claim["claim_id"], str) and re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", claim["claim_id"]) is not None
    valid = valid and re.fullmatch(r"[0-9a-f]{64}", claim["stage_script_sha256"]) is not None
    script_hash = hashlib.sha256(read_regular_bounded(script_path, MAX_SCRIPT_BYTES)).hexdigest()
    valid = valid and claim["stage_script_sha256"] == script_hash
    def timestamp(value):
        if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value) is None:
            raise ValueError("timestamp")
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    issued = timestamp(claim["issued_at"])
    expires = timestamp(claim["expires_at"])
    now = datetime.datetime.now(datetime.timezone.utc)
    valid = valid and issued <= now and now < expires and issued < expires
except (OSError, UnicodeError, ValueError, TypeError, KeyError, json.JSONDecodeError):
    valid = False
if not valid:
    stop("claim_invalid", 65)
stop("stage_inert_in_phase15", 78)
PHASE15_STAGE_PY
