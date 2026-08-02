#!/usr/bin/env bash
set -Eeuo pipefail

readonly SCHEMA="amn2.phase13.awg3-readonly-preflight.v1"
readonly FAILURE_STAGES='bootstrap candidate_sockets candidate_links candidate_addresses_routes candidate_docker candidate_systemd candidate_paths awg2_projection foreign_projection render'
readonly CANDIDATE_UDP_PORT="30002"
readonly CANDIDATE_INTERFACE="awg3"
readonly CANDIDATE_BRIDGE="amn2sp3br0"
readonly CANDIDATE_VPN_CIDR="10.212.13.0/24"
readonly CANDIDATE_CONTAINER_CIDR="172.29.252.0/28"
readonly SYSTEM_DOCKER="/usr/bin/docker"
readonly SPAIN_DOCKER="/opt/amn2-spain/docker/bin/docker"
readonly SPAIN_DOCKER_HOST="unix:///run/amn2-spain-docker/docker.sock"
readonly ACCEPTED_AWG2_CONTAINER="amn2-spain-awg"
readonly ACCEPTED_AWG2_INTERFACE="awg0"
readonly ACCEPTED_AWG2_DB="/var/lib/amn2-spain/amn2.sqlite3"
readonly ACCEPTED_AWG2_WEB_UNIT="amn2-spain-web.service"
readonly ACCEPTED_AWG2_BOT_UNIT="amn2-spain-bot.service"
readonly ACCEPTED_AWG2_FORWARD_UNIT="amn2-spain-forward-compat.service"
readonly ACCEPTED_AWG2_ACTIVE_UNITS="amn2-spain-docker.service amn2-spain-network.service ${ACCEPTED_AWG2_FORWARD_UNIT} ${ACCEPTED_AWG2_WEB_UNIT}"
readonly ACCEPTED_AWG2_UDP_PORT=30001
readonly ACCEPTED_AWG2_VPN_CIDR=10.212.12.0/24
readonly ACCEPTED_AWG2_BRIDGE=amn2spbr0
readonly ACCEPTED_FOREIGN_ENTRIES=153
readonly ACCEPTED_FOREIGN_SHA256=f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8
readonly ACCEPTED_FOREIGN_RECEIPT_SHA256=bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704
readonly FORWARD_RULE_COMMENT_1="amn2_spain:compat-forward-dnat"
readonly FORWARD_RULE_COMMENT_2="amn2_spain:compat-forward-outbound"
readonly FORWARD_RULE_COMMENT_3="amn2_spain:compat-forward-return"
readonly FORWARD_RULE_COMMENTS="${FORWARD_RULE_COMMENT_1} ${FORWARD_RULE_COMMENT_2} ${FORWARD_RULE_COMMENT_3}"

emit_failure() {
    local stage=${1-}
    local exit_code=${2-70}
    local allowed
    for allowed in ${FAILURE_STAGES}; do
        if [[ ${stage} == "${allowed}" ]]; then
            printf 'AMN2_PHASE13_AWG3_PREFLIGHT_FAILURE_V1|stage=%s|exit=%s\n' "${stage}" "${exit_code}"
            return 0
        fi
    done
    printf 'AMN2_PHASE13_AWG3_PREFLIGHT_FAILURE_V1|stage=bootstrap|exit=70\n'
}

classify_udp_port() {
    local candidate=${1-}
    local observed=${2-}
    local status=${3-exact}
    local port
    if [[ ${status} != exact || ! ${candidate} =~ ^[0-9]+$ ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    IFS=',' read -r -a ports <<< "${observed}"
    for port in "${ports[@]}"; do
        if [[ -n ${port} && ${port} == "${candidate}" ]]; then
            printf 'udp_port_conflict\n'
            return 71
        fi
        if [[ -n ${port} && ! ${port} =~ ^[0-9]+$ ]]; then
            printf 'observation_ambiguous\n'
            return 72
        fi
    done
    return 0
}

classify_name_collision() {
    local reason=${1-}
    local candidate=${2-}
    local observed=${3-}
    local status=${4-exact}
    local name
    if [[ ${status} != exact || -z ${candidate} ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    IFS=',' read -r -a names <<< "${observed}"
    for name in "${names[@]}"; do
        if [[ -n ${name} && ${name} == "${candidate}" ]]; then
            printf '%s\n' "${reason}"
            return 71
        fi
    done
    return 0
}

ipv4_to_int() {
    local address=${1-}
    local a b c d extra
    IFS='.' read -r a b c d extra <<< "${address}"
    if [[ -n ${extra-} || ! ${a-} =~ ^[0-9]+$ || ! ${b-} =~ ^[0-9]+$ || ! ${c-} =~ ^[0-9]+$ || ! ${d-} =~ ^[0-9]+$ ]]; then
        return 1
    fi
    if (( 255 < a || 255 < b || 255 < c || 255 < d )); then
        return 1
    fi
    printf '%u\n' "$(( (a << 24) + (b << 16) + (c << 8) + d ))"
}

cidr_bounds() {
    local cidr=${1-}
    local address prefix extra address_int mask network broadcast
    IFS='/' read -r address prefix extra <<< "${cidr}"
    if [[ -n ${extra-} || ! ${prefix-} =~ ^[0-9]+$ ]] || (( prefix < 0 || 32 < prefix )); then
        return 1
    fi
    if ! address_int=$(ipv4_to_int "${address}"); then
        return 1
    fi
    if (( prefix == 0 )); then
        mask=0
    else
        mask=$(( (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF ))
    fi
    network=$(( address_int & mask ))
    broadcast=$(( network | (0xFFFFFFFF ^ mask) ))
    printf '%u %u\n' "${network}" "${broadcast}"
}

cidr_overlap() {
    local first=${1-}
    local second=${2-}
    local first_start first_end second_start second_end first_bounds second_bounds
    if ! first_bounds=$(cidr_bounds "${first}"); then
        return 2
    fi
    read -r first_start first_end <<< "${first_bounds}"
    if ! second_bounds=$(cidr_bounds "${second}"); then
        return 2
    fi
    read -r second_start second_end <<< "${second_bounds}"
    if (( first_start <= second_end && second_start <= first_end )); then
        return 0
    fi
    return 1
}

classify_cidr_set() {
    local reason=${1-}
    local candidate=${2-}
    local observed=${3-}
    local status=${4-exact}
    local cidr overlap_rc
    local candidate_bounds
    if [[ ${status} != exact ]] || ! candidate_bounds=$(cidr_bounds "${candidate}"); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    IFS=',' read -r -a cidrs <<< "${observed}"
    for cidr in "${cidrs[@]}"; do
        if [[ -z ${cidr} ]]; then
            continue
        fi
        set +e
        cidr_overlap "${candidate}" "${cidr}"
        overlap_rc=$?
        set -e
        if (( overlap_rc == 0 )); then
            printf '%s\n' "${reason}"
            return 71
        fi
        if (( overlap_rc == 2 )); then
            printf 'observation_ambiguous\n'
            return 72
        fi
    done
    return 0
}

classify_existence() {
    local reason=${1-}
    local state=${2-}
    case ${state} in
        absent)
            return 0
            ;;
        present|symlink)
            printf '%s\n' "${reason}"
            return 71
            ;;
        *)
            printf 'observation_ambiguous\n'
            return 72
            ;;
    esac
}

validate_awg2_projection() {
    local port=${1-}
    local cidr=${2-}
    local bridge=${3-}
    local persistent_peers=${4-}
    local live_peers=${5-}
    local restart_count=${6-}
    local forward_rules=${7-}
    local web_local_only=${8-}
    local bot_disabled=${9-}
    local persistent_peer_set_sha256=${10-}
    local live_peer_set_sha256=${11-}
    if [[ ${port} != 30001 ||
          ${cidr} != "10.212.12.0/24" ||
          ${bridge} != "amn2spbr0" ||
          ${persistent_peers} != 7 || ${live_peers} != 7 ||
          ${restart_count} != 59 || ${forward_rules} != 3 ||
          ${web_local_only} != true || ${bot_disabled} != true ||
          ! ${persistent_peer_set_sha256} =~ ^[0-9a-f]{64}$ ||
          ${persistent_peer_set_sha256} != "${live_peer_set_sha256}" ]]; then
        printf 'awg2_equality_mismatch\n'
        return 70
    fi
    return 0
}

validate_foreign_projection() {
    local entries=${1-}
    local stable_sha256=${2-}
    local changed=${3-}
    local equality=${4-}
    local receipt_sha256=${5-}
    if [[ ${entries} != 153 ||
          ${stable_sha256} != "f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8" ||
          ${changed} != 0 || ${equality} != true ||
          ${receipt_sha256} != "bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704" ]]; then
        printf 'foreign_equality_mismatch\n'
        return 69
    fi
    return 0
}

normalize_peer_projection() {
    local value=${1-}
    local line normalized duplicates count digest
    if [[ -z ${value} ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    while IFS= read -r line; do
        if [[ ! ${line} =~ ^[A-Za-z0-9+/]{43}=$ ]]; then
            printf 'observation_ambiguous\n'
            return 72
        fi
    done <<< "${value}"
    normalized=$(printf '%s\n' "${value}" | LC_ALL=C sort)
    duplicates=$(printf '%s\n' "${normalized}" | uniq -d)
    if [[ -n ${duplicates} ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    count=$(printf '%s\n' "${normalized}" | awk 'NF {count++} END {print count+0}')
    digest=$(printf '%s\n' "${normalized}" | sha256sum | cut -d' ' -f1)
    if [[ ! ${count} =~ ^[0-9]+$ || ! ${digest} =~ ^[0-9a-f]{64}$ ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    printf '%s|%s\n' "${count}" "${digest}"
}

validate_awg2_container_stability() {
    local before=${1-}
    local after=${2-}
    local before_running before_restart before_pid before_extra
    local after_running after_restart after_pid after_extra
    IFS='|' read -r before_running before_restart before_pid before_extra <<< "${before}"
    IFS='|' read -r after_running after_restart after_pid after_extra <<< "${after}"
    if [[ ${before_running} != true || ${after_running} != true ||
          ! ${before_restart} =~ ^[0-9]+$ || ! ${after_restart} =~ ^[0-9]+$ ||
          ! ${before_pid} =~ ^[1-9][0-9]{0,9}$ || ! ${after_pid} =~ ^[1-9][0-9]{0,9}$ ||
          -n ${before_extra} || -n ${after_extra} || ${before} != "${after}" ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    return 0
}

build_foreign_stable_receipt() {
    local rows=${1-}
    local python_executable=${2-/usr/bin/python3}
    local receipt
    if [[ -z ${rows} ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if receipt=$("${python_executable}" -c '
import hashlib, json, re, sys
try:
    rows = []
    seen = set()
    for raw in sys.argv[1].splitlines():
        parts = raw.split("|")
        if len(parts) != 6:
            raise ValueError("row")
        kind, name_hash, content_hash, active_state, unit_status, bound_status = parts
        if kind not in {"container", "unit"}:
            raise ValueError("kind")
        if re.fullmatch(r"[0-9a-f]{64}", name_hash) is None or re.fullmatch(r"[0-9a-f]{64}", content_hash) is None:
            raise ValueError("hash")
        identity = (kind, name_hash)
        if identity in seen:
            raise ValueError("duplicate")
        seen.add(identity)
        if re.fullmatch(r"[A-Za-z0-9_.:+-]+", active_state) is None:
            raise ValueError("state")
        row = {
            "active_state": active_state,
            "image_or_unit_sha256": content_hash,
            "kind": kind,
            "name_sha256": name_hash,
        }
        if kind == "unit":
            if unit_status != "exact" or re.fullmatch(r"[A-Za-z0-9_.:+-]+", bound_status) is None:
                raise ValueError("unit")
            row["unit_content_status"] = unit_status
            row["bound_port_status"] = bound_status
        elif unit_status or bound_status:
            raise ValueError("container")
        rows.append(row)
    if not rows:
        raise ValueError("empty")
    rows.sort(key=lambda item: (item["kind"], item["name_sha256"]))
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
    print(f"{len(rows)}|{hashlib.sha256(payload).hexdigest()}")
except Exception:
    raise SystemExit(72)
' "${rows}"); then
        printf '%s\n' "${receipt}"
        return 0
    fi
    printf 'observation_ambiguous\n'
    return 72
}

hash_text() {
    printf '%s' "${1-}" | sha256sum | cut -d' ' -f1
}

system_docker() {
    "${SYSTEM_DOCKER}" "$@"
}

spain_docker() {
    "${SPAIN_DOCKER}" -H "${SPAIN_DOCKER_HOST}" "$@"
}

observe_db_peer_projection() {
    local raw
    if [[ ! -r ${ACCEPTED_AWG2_DB} ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! raw=$(/usr/bin/python3 -c '
import sqlite3, sys
path = sys.argv[1]
connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
try:
    connection.execute("PRAGMA query_only=ON")
    rows = connection.execute(
        "SELECT peer_public_key FROM devices WHERE status = ? ORDER BY peer_public_key",
        ("active",),
    ).fetchall()
    for row in rows:
        if len(row) != 1 or not isinstance(row[0], str):
            raise ValueError("peer row")
        print(row[0])
finally:
    connection.close()
' "${ACCEPTED_AWG2_DB}"); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    normalize_peer_projection "${raw}"
}

observe_live_peer_projection() {
    local pid=${1-}
    local raw
    if [[ ! ${pid} =~ ^[1-9][0-9]{0,9}$ ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! raw=$(/usr/bin/nsenter \
        --target "${pid}" --mount --net --pid \
        "--root=/proc/${pid}/root" --wd=/ \
        /usr/bin/awg show "${ACCEPTED_AWG2_INTERFACE}" peers); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    normalize_peer_projection "${raw}"
}

observe_awg2_projection() {
    local inspect inspect_after running restart_count pid
    local bridge_view container_links container_sockets container_forward route_view
    local persistent_projection live_projection persistent_count persistent_hash
    local live_count live_hash web_view web_matches bot_active bot_enabled
    local unit unit_active unit_enabled nft_view comment comment_count forward_count=0

    if [[ ! -x ${SPAIN_DOCKER} || ! -x /usr/bin/nsenter || ! -x /usr/bin/python3 ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! inspect=$(spain_docker inspect --format '{{.State.Running}}|{{.RestartCount}}|{{.State.Pid}}' "${ACCEPTED_AWG2_CONTAINER}"); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    IFS='|' read -r running restart_count pid <<< "${inspect}"
    if [[ ${running} != true || ! ${restart_count} =~ ^[0-9]+$ || ! ${pid} =~ ^[1-9][0-9]{0,9}$ ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! bridge_view=$(/usr/sbin/ip -o link show dev "${ACCEPTED_AWG2_BRIDGE}"); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if [[ -z ${bridge_view} ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! route_view=$(/usr/sbin/ip -o route show "${ACCEPTED_AWG2_VPN_CIDR}"); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! grep -Eq "^${ACCEPTED_AWG2_VPN_CIDR} .* dev ${ACCEPTED_AWG2_BRIDGE}( |$)" <<< "${route_view}"; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! container_links=$(/usr/bin/nsenter "--net=/proc/${pid}/ns/net" /usr/sbin/ip -o link show dev "${ACCEPTED_AWG2_INTERFACE}"); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if [[ -z ${container_links} ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! container_sockets=$(/usr/bin/nsenter "--net=/proc/${pid}/ns/net" /usr/bin/ss -H -lnu); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! awk -v port="${ACCEPTED_AWG2_UDP_PORT}" '{for (i=1;i<=NF;i++) if ($i ~ (":" port "$") ) found=1} END {exit found ? 0 : 1}' <<< "${container_sockets}"; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! container_forward=$(/usr/bin/nsenter "--net=/proc/${pid}/ns/net" /usr/sbin/sysctl -n net.ipv4.ip_forward); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if [[ ${container_forward} != 1 ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! persistent_projection=$(observe_db_peer_projection); then
        return 72
    fi
    if ! live_projection=$(observe_live_peer_projection "${pid}"); then
        return 72
    fi
    IFS='|' read -r persistent_count persistent_hash <<< "${persistent_projection}"
    IFS='|' read -r live_count live_hash <<< "${live_projection}"

    if ! web_view=$(/usr/bin/ss -H -lnt); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    web_matches=$(awk '{for (i=1;i<=NF;i++) if ($i ~ /:3031$/) print $i}' <<< "${web_view}")
    if [[ ${web_matches} != 127.0.0.1:3031 ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! bot_active=$(/usr/bin/systemctl show "${ACCEPTED_AWG2_BOT_UNIT}" --property=ActiveState --value) ||
       ! bot_enabled=$(/usr/bin/systemctl show "${ACCEPTED_AWG2_BOT_UNIT}" --property=UnitFileState --value); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if [[ ${bot_active} != inactive || ${bot_enabled} != disabled ]]; then
        printf 'observation_ambiguous\n'
        return 72
    fi
    for unit in ${ACCEPTED_AWG2_ACTIVE_UNITS}; do
        if ! unit_active=$(/usr/bin/systemctl show "${unit}" --property=ActiveState --value) ||
           ! unit_enabled=$(/usr/bin/systemctl show "${unit}" --property=UnitFileState --value); then
            printf 'observation_ambiguous\n'
            return 72
        fi
        if [[ ${unit_active} != active || ${unit_enabled} != enabled ]]; then
            printf 'observation_ambiguous\n'
            return 72
        fi
    done
    if ! nft_view=$(/usr/sbin/nft -j list chain ip filter FORWARD); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    for comment in ${FORWARD_RULE_COMMENTS}; do
        if ! comment_count=$(/usr/bin/python3 -c '
import json, sys
try:
    value = json.loads(sys.stdin.read())
    count = 0
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            if current.get("comment") == sys.argv[1]:
                count += 1
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    print(count)
except Exception:
    raise SystemExit(72)
' "${comment}" <<< "${nft_view}"); then
            printf 'observation_ambiguous\n'
            return 72
        fi
        if [[ ${comment_count} != 1 ]]; then
            printf 'observation_ambiguous\n'
            return 72
        fi
        ((forward_count += 1))
    done
    if ! inspect_after=$(spain_docker inspect --format '{{.State.Running}}|{{.RestartCount}}|{{.State.Pid}}' "${ACCEPTED_AWG2_CONTAINER}"); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    if ! validate_awg2_container_stability "${inspect}" "${inspect_after}"; then
        return 72
    fi
    printf '%s|%s|%s|%s|%s|%s|%s|true|true|%s|%s\n' \
        "${ACCEPTED_AWG2_UDP_PORT}" "${ACCEPTED_AWG2_VPN_CIDR}" "${ACCEPTED_AWG2_BRIDGE}" \
        "${persistent_count}" "${live_count}" "${restart_count}" "${forward_count}" \
        "${persistent_hash}" "${live_hash}"
}

is_foreign_projection_excluded() {
    local kind=${1-}
    local name=${2-}
    if [[ ${kind} == container ]]; then
        [[ ${name} == amnezia-awg2 || ${name} == "${ACCEPTED_AWG2_CONTAINER}" || ${name} == amn2-spain-awg3 ]]
        return
    fi
    case ${name} in
        amneziya-web.service|amneziya-bot.service|\
        amn2-spain-web.service|amn2-spain-bot.service|amn2-spain-docker.service|\
        amn2-spain-network.service|amn2-spain-forward-compat.service|amn2-spain-awg3.service)
            return 0
            ;;
    esac
    return 1
}

foreign_unit_bound_status() {
    local unit=${1-}
    local active_state=${2-}
    local control_group main_pid canonical_id proc_value
    if ! control_group=$(/usr/bin/systemctl show "${unit}" --property=ControlGroup --value); then
        return 72
    fi
    if [[ -n ${control_group} ]]; then
        printf 'cgroup_complete\n'
        return 0
    fi
    if ! main_pid=$(/usr/bin/systemctl show "${unit}" --property=MainPID --value); then
        return 72
    fi
    if [[ ! ${main_pid} =~ ^[0-9]+$ ]]; then
        return 72
    fi
    if [[ ${main_pid} == 0 ]]; then
        if [[ ${active_state} == active ]]; then
            printf 'active_exited_no_live_process\n'
        else
            printf 'no_cgroup\n'
        fi
        return 0
    fi
    if [[ ! -r /proc/${main_pid}/cgroup ]]; then
        return 72
    fi
    if ! canonical_id=$(/usr/bin/systemctl show "${unit}" --property=Id --value); then
        return 72
    fi
    if ! proc_value=$(/usr/bin/cat "/proc/${main_pid}/cgroup"); then
        return 72
    fi
    if [[ ${proc_value} != *"/${canonical_id}"* && ${proc_value} != *"/${canonical_id}/"* ]]; then
        return 72
    fi
    printf 'mainpid_cgroup_complete\n'
}

observe_foreign_projection() {
    local docker_rows systemd_rows rows=''
    local name image state unit active_state sub_state unit_content bound_status
    local receipt count digest changed equality
    if ! docker_rows=$(system_docker ps -a --format '{{.Names}}|{{.Image}}|{{.State}}'); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    while IFS='|' read -r name image state; do
        [[ -z ${name} ]] && continue
        is_foreign_projection_excluded container "${name}" && continue
        if [[ ! ${state} =~ ^[A-Za-z0-9_.:+-]+$ ]]; then
            printf 'observation_ambiguous\n'
            return 72
        fi
        rows+="container|$(hash_text "${name}")|$(hash_text "${image}")|${state}||"$'\n'
    done <<< "${docker_rows}"
    if ! systemd_rows=$(/usr/bin/systemctl list-units --type=service --all --no-legend --no-pager); then
        printf 'observation_ambiguous\n'
        return 72
    fi
    while read -r unit _load active_state sub_state _rest; do
        [[ -z ${unit} || ${unit} != *.service ]] && continue
        is_foreign_projection_excluded unit "${unit}" && continue
        if ! unit_content=$(/usr/bin/systemctl cat "${unit}" --no-pager); then
            printf 'observation_ambiguous\n'
            return 72
        fi
        if ! bound_status=$(foreign_unit_bound_status "${unit}" "${active_state}"); then
            printf 'observation_ambiguous\n'
            return 72
        fi
        rows+="unit|$(hash_text "${unit}")|$(hash_text "${unit_content}")|${active_state}:${sub_state}|exact|${bound_status}"$'\n'
        unit_content=''
    done <<< "${systemd_rows}"
    if ! receipt=$(build_foreign_stable_receipt "${rows%$'\n'}" /usr/bin/python3); then
        return 72
    fi
    IFS='|' read -r count digest <<< "${receipt}"
    changed=1
    equality=false
    if [[ ${count} == "${ACCEPTED_FOREIGN_ENTRIES}" && ${digest} == "${ACCEPTED_FOREIGN_SHA256}" ]]; then
        changed=0
        equality=true
    fi
    printf '%s|%s|%s|%s|%s\n' "${count}" "${digest}" "${changed}" "${equality}" "${ACCEPTED_FOREIGN_RECEIPT_SHA256}"
}

require_command() {
    local location
    location=$(command -v "$1")
    [[ -n ${location} ]]
}

csv_from_lines() {
    local value=${1-}
    local result=''
    local line
    while IFS= read -r line; do
        [[ -z ${line} ]] && continue
        if [[ -n ${result} ]]; then
            result+=','
        fi
        result+="${line}"
    done <<< "${value}"
    printf '%s\n' "${result}"
}

sha256_lines() {
    local value=${1-}
    printf '%s\n' "${value}" | LC_ALL=C sort -u | sha256sum | cut -d' ' -f1
}

is_sha256() {
    [[ ${1-} =~ ^[0-9a-f]{64}$ ]]
}

validate_bootstrap_bindings() {
    local value
    if [[ ! ${AMN2_PHASE13_OUTCOME_ID-} =~ ^[a-z0-9][a-z0-9-]{2,63}$ ]]; then
        return 1
    fi
    for value in \
        "${AMN2_PHASE13_MANIFEST_SHA256-}" \
        "${AMN2_PHASE13_RUNNER_SHA256-}" \
        "${AMN2_PHASE13_COLLECTOR_SHA256-}" \
        "${AMN2_PHASE13_SCHEMA_SHA256-}" \
        "${AMN2_PHASE13_FOUNDATION_SHA256-}"; do
        is_sha256 "${value}" || return 1
    done
}

observe_path_state() {
    local path=${1-}
    if [[ -L ${path} ]]; then
        printf 'symlink\n'
    elif [[ -e ${path} ]]; then
        if [[ -r ${path} ]]; then
            printf 'present\n'
        else
            printf 'unreadable\n'
        fi
    else
        printf 'absent\n'
    fi
}

render_evidence() {
    local observed_udp_ports=${1-}
    local observed_links=${2-}
    local observed_cidrs=${3-}
    local peer_set_sha256=${4-}
    local checked_at socket_sha link_sha cidr_sha docker_sha systemd_sha path_sha
    checked_at=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    socket_sha=$(sha256_lines "${observed_udp_ports}")
    link_sha=$(sha256_lines "${observed_links}")
    cidr_sha=$(sha256_lines "${observed_cidrs}")
    docker_sha=$(sha256_lines "${AMN2_PHASE13_DOCKER_OBSERVATION-}")
    systemd_sha=$(sha256_lines "${AMN2_PHASE13_SYSTEMD_OBSERVATION-}")
    path_sha=$(sha256_lines "${AMN2_PHASE13_PATH_OBSERVATION-}")
    printf '{"awg2_equality":{"bot_disabled":true,"container_equal":true,"equal":true,"forward_rule_count":3,"interface_equal":true,"live_peers":7,"peer_set_sha256":"%s","persistent_peers":7,"restart_count":59,"service_equal":true,"udp_port_equal":true,"vpn_cidr_route_equal":true,"web_listener_equal":true},"candidate_resources":[{"declared_value":"30002","observation_sha256":"%s","resource":"udp_port","state":"free"},{"declared_value":"awg3","observation_sha256":"%s","resource":"interface","state":"absent"},{"declared_value":"amn2sp3br0","observation_sha256":"%s","resource":"bridge","state":"absent"},{"declared_value":"10.212.13.0/24","observation_sha256":"%s","resource":"vpn_cidr","state":"free"},{"declared_value":"172.29.252.0/28","observation_sha256":"%s","resource":"container_cidr","state":"free"},{"declared_value":"amn2-spain-awg3","observation_sha256":"%s","resource":"container","state":"absent"},{"declared_value":"amn2-spain-awg3.service","observation_sha256":"%s","resource":"service","state":"absent"},{"declared_value":"/var/lib/amn2-spain/awg3","observation_sha256":"%s","resource":"state_path","state":"absent"}],"checked_at":"%s","collector_sha256":"%s","decision":"pass","foreign_equality":{"changed":0,"equal":true,"equality_receipt_sha256":"%s","persistent_entries":153,"stable_sha256":"%s"},"manifest_sha256":"%s","outcome_id":"%s","phase12_foundation_sha256":"%s","runner_sha256":"%s","safety_receipt":{"container_action_attempted":false,"firewall_action_attempted":false,"mutation_attempted":false,"raw_output_persisted":false,"raw_peer_identifiers_emitted":false,"remote_file_written":false,"secret_bearing_config_accessed":false,"service_action_attempted":false},"schema":"amn2.phase13.awg3-readonly-preflight.v1","schema_sha256":"%s","source_head":"ff115b63ca1329640ca13ae0a502d155f99b456b","stop_reasons":[]}\n' \
        "${peer_set_sha256}" "${socket_sha}" "${link_sha}" "${link_sha}" "${cidr_sha}" \
        "${cidr_sha}" "${docker_sha}" "${systemd_sha}" "${path_sha}" "${checked_at}" \
        "${AMN2_PHASE13_COLLECTOR_SHA256}" "${ACCEPTED_FOREIGN_RECEIPT_SHA256}" \
        "${ACCEPTED_FOREIGN_SHA256}" "${AMN2_PHASE13_MANIFEST_SHA256}" \
        "${AMN2_PHASE13_OUTCOME_ID}" "${AMN2_PHASE13_FOUNDATION_SHA256}" \
        "${AMN2_PHASE13_RUNNER_SHA256}" "${AMN2_PHASE13_SCHEMA_SHA256}"
}

main() {
    local mode=${1-}
    local stage=bootstrap
    local udp_lines udp_ports link_lines links address_lines route_lines cidrs
    local docker_names docker_network_ids docker_network_id docker_subnets
    local spain_docker_names spain_docker_network_ids spain_docker_network_id
    local systemd_units path_state peer_set_sha256 classification
    local observed_persistent observed_live observed_restart observed_forward
    local observed_web observed_bot observed_foreign_entries observed_foreign_sha
    local observed_foreign_changed observed_foreign_equal
    local awg2_observation foreign_observation live_peer_set_sha256 foreign_receipt_sha256
    local _awg2_port _awg2_cidr _awg2_bridge
    local rc

    if [[ $# != 1 || ${mode} != preflight ]]; then
        emit_failure bootstrap 64
        return 64
    fi
    if ! validate_bootstrap_bindings; then
        emit_failure bootstrap 64
        return 64
    fi
    if [[ ! -x ${SYSTEM_DOCKER} ]]; then
        emit_failure bootstrap 73
        return 73
    fi
    for required in ss ip systemctl sha256sum cut sort date awk grep uniq wc tr python3 nsenter nft; do
        if ! require_command "${required}"; then
            emit_failure bootstrap 73
            return 73
        fi
    done

    stage=candidate_sockets
    if ! udp_lines=$(ss -H -lnu); then
        emit_failure "${stage}" 72
        return 72
    fi
    udp_ports=$(printf '%s\n' "${udp_lines}" | awk '{value=$5; sub(/^.*:/,"",value); if (value ~ /^[0-9]+$/) print value}' | LC_ALL=C sort -nu)
    udp_ports=$(csv_from_lines "${udp_ports}")
    set +e
    classification=$(classify_udp_port "${CANDIDATE_UDP_PORT}" "${udp_ports}" exact)
    rc=$?
    set -e
    if (( rc != 0 )); then
        emit_failure "${stage}" "${rc}"
        return "${rc}"
    fi
    stage=candidate_links
    if ! link_lines=$(ip -o link show); then
        emit_failure "${stage}" 72
        return 72
    fi
    links=$(printf '%s\n' "${link_lines}" | awk -F': ' '{name=$2; sub(/@.*/,"",name); print name}' | LC_ALL=C sort -u)
    links=$(csv_from_lines "${links}")
    for candidate in "${CANDIDATE_INTERFACE}" "${CANDIDATE_BRIDGE}"; do
        set +e
        if [[ ${candidate} == "${CANDIDATE_INTERFACE}" ]]; then
            classification=$(classify_name_collision interface_conflict "${candidate}" "${links}" exact)
        else
            classification=$(classify_name_collision bridge_conflict "${candidate}" "${links}" exact)
        fi
        rc=$?
        set -e
        if (( rc != 0 )); then
            emit_failure "${stage}" "${rc}"
            return "${rc}"
        fi
    done

    stage=candidate_addresses_routes
    if ! address_lines=$(ip -o -4 address show); then
        emit_failure "${stage}" 72
        return 72
    fi
    if ! route_lines=$(ip -o -4 route show table all); then
        emit_failure "${stage}" 72
        return 72
    fi
    cidrs=$(printf '%s\n%s\n' "${address_lines}" "${route_lines}" | awk '{for (i=1;i<=NF;i++) if ($i ~ /^[0-9]+(\.[0-9]+){3}\/[0-9]+$/) print $i}' | LC_ALL=C sort -u)
    cidrs=$(csv_from_lines "${cidrs}")
    for candidate in "${CANDIDATE_VPN_CIDR}" "${CANDIDATE_CONTAINER_CIDR}"; do
        set +e
        if [[ ${candidate} == "${CANDIDATE_VPN_CIDR}" ]]; then
            classification=$(classify_cidr_set vpn_cidr_conflict "${candidate}" "${cidrs}" exact)
        else
            classification=$(classify_cidr_set container_cidr_conflict "${candidate}" "${cidrs}" exact)
        fi
        rc=$?
        set -e
        if (( rc != 0 )); then
            emit_failure "${stage}" "${rc}"
            return "${rc}"
        fi
    done

    stage=candidate_docker
    if ! docker_names=$(system_docker ps -a --format '{{.Names}}'); then
        emit_failure "${stage}" 72
        return 72
    fi
    if [[ ! -x ${SPAIN_DOCKER} ]] || ! spain_docker_names=$(spain_docker ps -a --format '{{.Names}}'); then
        emit_failure "${stage}" 72
        return 72
    fi
    docker_names+=$'\n'"${spain_docker_names}"
    set +e
    classification=$(classify_name_collision container_conflict amn2-spain-awg3 "$(csv_from_lines "${docker_names}")" exact)
    rc=$?
    set -e
    if (( rc != 0 )); then
        emit_failure "${stage}" "${rc}"
        return "${rc}"
    fi
    if ! docker_network_ids=$(system_docker network ls -q); then
        emit_failure "${stage}" 72
        return 72
    fi
    if ! spain_docker_network_ids=$(spain_docker network ls -q); then
        emit_failure "${stage}" 72
        return 72
    fi
    docker_subnets=''
    while IFS= read -r docker_network_id; do
        [[ -z ${docker_network_id} ]] && continue
        if ! classification=$(system_docker network inspect --format '{{range .IPAM.Config}}{{println .Subnet}}{{end}}' "${docker_network_id}"); then
            emit_failure "${stage}" 72
            return 72
        fi
        if [[ -n ${classification} ]]; then
            docker_subnets+="${classification}"$'\n'
        fi
    done <<< "${docker_network_ids}"
    while IFS= read -r spain_docker_network_id; do
        [[ -z ${spain_docker_network_id} ]] && continue
        if ! classification=$(spain_docker network inspect --format '{{range .IPAM.Config}}{{println .Subnet}}{{end}}' "${spain_docker_network_id}"); then
            emit_failure "${stage}" 72
            return 72
        fi
        if [[ -n ${classification} ]]; then
            docker_subnets+="${classification}"$'\n'
        fi
    done <<< "${spain_docker_network_ids}"
    set +e
    classification=$(classify_cidr_set container_cidr_conflict "${CANDIDATE_CONTAINER_CIDR}" "$(csv_from_lines "${docker_subnets}")" exact)
    rc=$?
    set -e
    if (( rc != 0 )); then
        emit_failure "${stage}" "${rc}"
        return "${rc}"
    fi
    AMN2_PHASE13_DOCKER_OBSERVATION=${docker_names}

    stage=candidate_systemd
    if ! systemd_units=$(systemctl list-unit-files --type=service --no-legend --no-pager); then
        emit_failure "${stage}" 72
        return 72
    fi
    set +e
    classification=$(classify_name_collision service_conflict amn2-spain-awg3.service "$(printf '%s\n' "${systemd_units}" | awk '{print $1}' | csv_from_lines)" exact)
    rc=$?
    set -e
    if (( rc != 0 )); then
        emit_failure "${stage}" "${rc}"
        return "${rc}"
    fi
    AMN2_PHASE13_SYSTEMD_OBSERVATION=${systemd_units}

    stage=candidate_paths
    AMN2_PHASE13_PATH_OBSERVATION=''
    for candidate_path in /var/lib/amn2-spain/awg3 /var/lib/amn2-spain/awg3/awg3.conf /etc/systemd/system/amn2-spain-awg3.service; do
        path_state=$(observe_path_state "${candidate_path}")
        AMN2_PHASE13_PATH_OBSERVATION+="${candidate_path}:${path_state};"
        set +e
        classification=$(classify_existence path_conflict "${path_state}")
        rc=$?
        set -e
        if (( rc != 0 )); then
            emit_failure "${stage}" "${rc}"
            return "${rc}"
        fi
    done

    stage=awg2_projection
    set +e
    awg2_observation=$(observe_awg2_projection)
    rc=$?
    set -e
    if (( rc != 0 )); then
        emit_failure "${stage}" 72
        return 72
    fi
    IFS='|' read -r _awg2_port _awg2_cidr _awg2_bridge \
        observed_persistent observed_live observed_restart observed_forward \
        observed_web observed_bot peer_set_sha256 live_peer_set_sha256 <<< "${awg2_observation}"
    set +e
    classification=$(validate_awg2_projection \
        "${_awg2_port}" "${_awg2_cidr}" "${_awg2_bridge}" \
        "${observed_persistent}" "${observed_live}" \
        "${observed_restart}" "${observed_forward}" "${observed_web}" "${observed_bot}" \
        "${peer_set_sha256}" "${live_peer_set_sha256}")
    rc=$?
    set -e
    if (( rc != 0 )); then
        emit_failure "${stage}" "${rc}"
        return "${rc}"
    fi

    stage=foreign_projection
    set +e
    foreign_observation=$(observe_foreign_projection)
    rc=$?
    set -e
    if (( rc != 0 )); then
        emit_failure "${stage}" 72
        return 72
    fi
    IFS='|' read -r observed_foreign_entries observed_foreign_sha \
        observed_foreign_changed observed_foreign_equal foreign_receipt_sha256 <<< "${foreign_observation}"
    set +e
    classification=$(validate_foreign_projection \
        "${observed_foreign_entries}" "${observed_foreign_sha}" \
        "${observed_foreign_changed}" "${observed_foreign_equal}" \
        "${foreign_receipt_sha256}")
    rc=$?
    set -e
    if (( rc != 0 )); then
        emit_failure "${stage}" "${rc}"
        return "${rc}"
    fi

    stage=render
    render_evidence "${udp_ports}" "${links}" "${cidrs}" "${peer_set_sha256}"
}

if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
    main "$@"
fi
