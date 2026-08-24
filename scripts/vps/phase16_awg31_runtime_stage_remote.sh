#!/usr/bin/env bash
set -Eeuo pipefail

package_id='phase16-awg3-family-3-1-spain-pilot-20260824-003'
required_gate='AWG31_RUNTIME_STAGE'
runtime_identity='docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d'
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
    canonical = json.dumps(claim, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n"
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
config_source="${PHASE16_AWG31_CONFIG_SOURCE:-}"
ledger_path="${PHASE16_STAGE_LEDGER:-}"
expected_package_root='/var/lib/amn2-phase16/package'
expected_config_source='/var/lib/amn2-phase16/input/awg3.conf'
expected_ledger_path='/var/lib/amn2-phase16/stage/awg31-runtime.json'

if [[ -z "$package_root" || -z "$config_source" || -z "$ledger_path" ]]; then
    printf '%s\n' 'stage_inputs_required' >&2
    exit 66
fi
if [[ "$package_root" != "$expected_package_root" || "$config_source" != "$expected_config_source" || "$ledger_path" != "$expected_ledger_path" ]]; then
    printf '%s\n' 'stage_inputs_invalid' >&2
    exit 67
fi

state_root='/var/lib/amn2-spain/awg3'
config_path="${state_root}/awg3.conf"
unit_path='/etc/systemd/system/amn2-spain-awg3.service'
container_name='amn2-spain-awg3'
network_name='amn2sp3'
bridge_name='amn2sp3br0'
created_state=false
created_unit=false
created_network=false

rollback_awg31_stage() {
    local status=$?
    trap - ERR
    if [[ "$created_unit" == true ]]; then
        /usr/bin/systemctl stop amn2-spain-awg3.service >/dev/null 2>&1 || true
        /usr/bin/rm -f "$unit_path"
        /usr/bin/systemctl daemon-reload >/dev/null 2>&1 || true
    fi
    /usr/bin/docker rm -f "$container_name" >/dev/null 2>&1 || true
    if [[ "$created_network" == true ]]; then
        /usr/bin/docker network rm "$network_name" >/dev/null 2>&1 || true
    fi
    if [[ "$created_state" == true && -d "$state_root" ]]; then
        /usr/bin/rm -rf --one-file-system "$state_root"
    fi
    printf '%s\n' 'awg31_runtime_stage_rolled_back' >&2
    exit "$status"
}
trap rollback_awg31_stage ERR

consume_stage_claim() {
    /usr/bin/python3 -I -B - "$claim_path" <<'PHASE16_CONSUME_PY'
import datetime, json, os, sys, tempfile
path = sys.argv[1]
with open(path, "rb") as stream:
    value = json.load(stream)
value["status"] = "consumed"
value["consumed_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
descriptor, temporary = tempfile.mkstemp(prefix=".phase16-claim-", dir=os.path.dirname(os.path.abspath(path)))
try:
    os.write(descriptor, raw)
    os.fsync(descriptor)
finally:
    os.close(descriptor)
os.replace(temporary, path)
PHASE16_CONSUME_PY
}

validate_runtime_config() {
    [[ -f "$config_source" && ! -L "$config_source" ]]
    local mode
    mode="$(/usr/bin/stat -c '%a' "$config_source")"
    [[ "$mode" == 400 || "$mode" == 600 ]]
    ! /usr/bin/grep -Eq '^\[Peer\][[:space:]]*$' "$config_source"
    /usr/bin/grep -Eq '^ListenPort[[:space:]]*=[[:space:]]*30002[[:space:]]*$' "$config_source"
    /usr/bin/grep -Eq '^RandomTrailers[[:space:]]*=[[:space:]]*on[[:space:]]*$' "$config_source"
    /usr/bin/grep -Eq '^DisableCookies[[:space:]]*=[[:space:]]*on[[:space:]]*$' "$config_source"
}

verify_runtime_capabilities() {
    /usr/bin/docker run --rm "$runtime_identity" /bin/sh -ec \
        '/bin/grep -a -q random_trailers /usr/bin/amneziawg-go && /bin/grep -a -q disable_cookies /usr/bin/amneziawg-go'
}

write_runtime_unit() {
    /usr/bin/install -m 0644 /dev/stdin "$unit_path" <<PHASE16_UNIT
[Unit]
Description=AMN2 Spain isolated AWG 3.1 runtime
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=simple
ExecStartPre=-/usr/bin/docker rm -f ${container_name}
ExecStart=/usr/bin/docker run --rm --name ${container_name} --network ${network_name} --ip 172.29.252.2 --cap-add NET_ADMIN --device /dev/net/tun -v ${config_path}:/etc/amneziawg/awg3.conf:ro -p 30002:30002/udp ${runtime_identity} /usr/bin/amneziawg-go -f awg3
ExecStartPost=/usr/bin/docker exec ${container_name} /usr/bin/awg setconf awg3 /etc/amneziawg/awg3.conf
ExecStartPost=/usr/bin/docker exec ${container_name} /sbin/ip address add 10.212.13.1/24 dev awg3
ExecStartPost=/usr/bin/docker exec ${container_name} /sbin/ip link set awg3 up
ExecStartPost=/usr/bin/docker exec ${container_name} /sbin/iptables -t nat -A POSTROUTING -s 10.212.13.0/24 -o eth0 -j MASQUERADE
ExecStop=-/usr/bin/docker stop -t 10 ${container_name}
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
PHASE16_UNIT
    created_unit=true
}

write_stage_ledger() {
    /usr/bin/install -d -m 0700 "$(dirname "$ledger_path")"
    /usr/bin/python3 -I -B - "$ledger_path" "$package_id" "$package_identity" "$runtime_identity" "$state_hash" <<'PHASE16_LEDGER_PY'
import json, os, sys, tempfile
path, package_id, package_identity, runtime_identity, state_hash = sys.argv[1:]
value = {"created_resources": ["amn2-spain-awg3.service", "amn2-spain-awg3", "amn2sp3", "/var/lib/amn2-spain/awg3"], "general_issuance_enabled": False, "package_id": package_id, "package_identity_sha256": package_identity, "rollback_scope": ["awg31-created-resources"], "runtime_identity": runtime_identity, "state_sha256": state_hash, "status": "staged"}
raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
descriptor, temporary = tempfile.mkstemp(prefix=".runtime-ledger-", dir=os.path.dirname(path))
try:
    os.write(descriptor, raw)
    os.fsync(descriptor)
finally:
    os.close(descriptor)
os.replace(temporary, path)
PHASE16_LEDGER_PY
}

[[ -f "$package_root/manifest.json" ]]
validate_runtime_config
consume_stage_claim
/usr/bin/docker pull "$runtime_identity"
verify_runtime_capabilities
[[ ! -e "$state_root" && ! -e "$unit_path" ]]
[[ -z "$(/usr/bin/docker ps -a --filter "name=^/${container_name}$" --format '{{.ID}}')" ]]
/usr/bin/install -d -m 0700 "$state_root"
created_state=true
/usr/bin/install -m 0600 "$config_source" "$config_path"
/usr/bin/docker network create --driver bridge --subnet 172.29.252.0/28 --opt "com.docker.network.bridge.name=${bridge_name}" "$network_name" >/dev/null
created_network=true
write_runtime_unit
/usr/bin/systemctl daemon-reload
/usr/bin/systemctl start amn2-spain-awg3.service
/usr/bin/systemctl is-active --quiet amn2-spain-awg3.service
/usr/bin/docker exec "$container_name" /usr/bin/awg show awg3 >/dev/null
write_stage_ledger
trap - ERR
printf '%s\n' '{"general_issuance_enabled":false,"result":"awg31_runtime_staged"}'
