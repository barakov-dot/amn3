#!/usr/bin/env bash
set -Eeuo pipefail

package_id='phase15-dual-protocol-bootstrap-20260811-001'
required_gate='AWG3_RUNTIME_STAGE'
python_executable="${PHASE15_PYTHON:-python3}"

fail_closed() {
    "$python_executable" -c 'import sys; sys.stderr.write(sys.argv[1] + "\n")' "$1"
    exit "$2"
}

claim_path="${PHASE15_STAGE_CLAIM_FILE:-}"
[[ -n "$claim_path" ]] || fail_closed 'claim_required' 64
[[ -f "$claim_path" ]] || fail_closed 'claim_required' 64
[[ "${PHASE15_PACKAGE_ID:-}" == "$package_id" ]] || fail_closed 'claim_invalid' 65
[[ "${PHASE15_FUTURE_GATE:-}" == "$required_gate" ]] || fail_closed 'claim_invalid' 65
[[ "${PHASE15_EXPECTED_CURRENT_STATE_SHA256:-}" =~ ^[0-9a-f]{64}$ ]] || fail_closed 'claim_invalid' 65

if ! "$python_executable" -c '
import datetime
import hashlib
import json
import pathlib
import re
import sys

claim_path, script_path, package_id, gate, state_hash = sys.argv[1:]
try:
    raw = pathlib.Path(claim_path).read_bytes()
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
    valid = valid and claim["schema"] == "amn2.phase15.stage-claim.v1"
    valid = valid and claim["package_id"] == package_id and claim["future_gate"] == gate
    valid = valid and claim["expected_current_state_sha256"] == state_hash
    valid = valid and claim["status"] == "issued" and claim["consumed_at"] is None
    valid = valid and isinstance(claim["claim_id"], str) and bool(claim["claim_id"])
    valid = valid and re.fullmatch(r"[0-9a-f]{64}", claim["stage_script_sha256"]) is not None
    script_hash = hashlib.sha256(pathlib.Path(script_path).read_bytes()).hexdigest()
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
raise SystemExit(0 if valid else 1)
' "$claim_path" "$0" "$package_id" "$required_gate" "$PHASE15_EXPECTED_CURRENT_STATE_SHA256"; then
    fail_closed 'claim_invalid' 65
fi

fail_closed 'stage_inert_in_phase15' 78
