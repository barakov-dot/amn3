#!/usr/bin/env bash
set -Eeuo pipefail

CURRENT_STAGE="bootstrap"

emit_failure() {
    local rc="${1:-1}"
    case "$CURRENT_STAGE" in
        bootstrap|host_identity|platform|capacity|candidate_inventory|listeners|network_state|firewall|systemd_inventory|systemd_unit_content|systemd_cgroup_ports|render) ;;
        *) CURRENT_STAGE="bootstrap" ;;
    esac
    if [[ ! "$rc" =~ ^[0-9]+$ ]] || (( rc < 1 || rc > 255 )); then
        rc=1
    fi
    trap - ERR
    printf 'AMN2_PHASE12_RESOURCE_CONFIRMATION_FAILURE_V1|stage=%s|exit=%s\n' "$CURRENT_STAGE" "$rc"
    exit "$rc"
}

trap 'emit_failure "$?"' ERR

sha256_text() {
    printf '%s' "$1" | sha256sum | cut -d' ' -f1
}

safe_atom() {
    printf '%s' "$1" | tr -cd 'A-Za-z0-9._:+-'
}

assert_render_dependency() {
    [[ "$(bool_command "$1")" == "true" ]] || emit_failure "$2"
}

safe_cgroup_path() {
    local path="$1" segment
    local -a segments
    [[ "$path" == /* && "$path" != *'|'* && "$path" != *$'\n'* && "$path" != *$'\r'* ]] || return 1
    IFS='/' read -r -a segments < <(printf '%s\n' "$path")
    for segment in "${segments[@]}"; do
        [[ "$segment" != ".." ]] || return 1
        [[ "$segment" != *[[:cntrl:]]* ]] || return 1
    done
}

parse_proc_cgroup_path() {
    local text="$1" hierarchy controllers path extra controller
    local v2_path="" v2_count=0 v1_path="" v1_count=0
    local -a controller_list
    while IFS=: read -r hierarchy controllers path extra; do
        if [[ -z "$hierarchy$controllers$path${extra:-}" ]]; then
            continue
        fi
        [[ -n "$hierarchy$controllers$path" && -z "${extra:-}" ]] || return 1
        if [[ "$hierarchy" == "0" && -z "$controllers" ]]; then
            safe_cgroup_path "$path" || return 1
            v2_path="$path"
            ((v2_count += 1))
            continue
        fi
        IFS=',' read -r -a controller_list < <(printf '%s\n' "$controllers")
        for controller in "${controller_list[@]}"; do
            if [[ "$controller" == "name=systemd" ]]; then
                safe_cgroup_path "$path" || return 1
                v1_path="$path"
                ((v1_count += 1))
            fi
        done
    done < <(printf '%s\n' "$text")
    if (( v2_count == 1 )); then
        printf '%s\n' "$v2_path"
        return 0
    fi
    if (( v2_count == 0 && v1_count == 1 )); then
        printf '%s\n' "$v1_path"
        return 0
    fi
    return 1
}

read_proc_starttime() {
    local stat_file="$1" stat_text stat_tail
    local -a stat_fields
    [[ -r "$stat_file" ]] || return 1
    IFS= read -r stat_text < "$stat_file" || return 1
    [[ "$stat_text" == *') '* ]] || return 1
    stat_tail="${stat_text##*) }"
    read -r -a stat_fields < <(printf '%s\n' "$stat_tail")
    (( ${#stat_fields[@]} >= 20 )) || return 1
    [[ "${stat_fields[19]}" =~ ^[0-9]+$ ]] || return 1
    printf '%s\n' "${stat_fields[19]}"
}

resolve_unit_cgroup() {
    local unit_name="$1" active_state="$2" proc_root="$3"
    local control_group main_pid main_pid_after canonical_id proc_file proc_stat_file
    local proc_cgroup_text proc_cgroup_text_after starttime_before starttime_after resolved
    RESOLVED_BOUND_PORT_STATUS=""
    RESOLVED_CONTROL_GROUP=""
    control_group="$(systemctl show "$unit_name" --property=ControlGroup --value)"
    if [[ -n "$control_group" ]]; then
        safe_cgroup_path "$control_group" || emit_failure 73
        RESOLVED_BOUND_PORT_STATUS="cgroup_complete"
        RESOLVED_CONTROL_GROUP="$control_group"
        return 0
    fi
    main_pid="$(systemctl show "$unit_name" --property=MainPID --value)"
    [[ "$main_pid" =~ ^(0|[1-9][0-9]*)$ ]] || emit_failure 71
    (( main_pid <= 4194304 )) || emit_failure 71
    if (( main_pid == 0 )); then
        if [[ "$active_state" == "active" ]]; then
            RESOLVED_BOUND_PORT_STATUS="active_exited_no_live_process"
        else
            RESOLVED_BOUND_PORT_STATUS="no_cgroup"
        fi
        return 0
    fi
    proc_file="$proc_root/$main_pid/cgroup"
    proc_stat_file="$proc_root/$main_pid/stat"
    starttime_before="$(read_proc_starttime "$proc_stat_file")" || emit_failure 72
    proc_cgroup_text="$(<"$proc_file")" || emit_failure 72
    resolved="$(parse_proc_cgroup_path "$proc_cgroup_text")" || emit_failure 73
    canonical_id="$(systemctl show "$unit_name" --property=Id --value)"
    [[ "$canonical_id" =~ ^[A-Za-z0-9_.@:-]+\.service$ ]] || emit_failure 74
    case "$resolved" in
        */"$canonical_id"|*/"$canonical_id"/*) ;;
        *) emit_failure 74 ;;
    esac
    starttime_after="$(read_proc_starttime "$proc_stat_file")" || emit_failure 72
    proc_cgroup_text_after="$(<"$proc_file")" || emit_failure 72
    main_pid_after="$(systemctl show "$unit_name" --property=MainPID --value)"
    [[ "$main_pid_after" =~ ^(0|[1-9][0-9]*)$ ]] || emit_failure 71
    if [[ "$main_pid_after" != "$main_pid" || "$starttime_after" != "$starttime_before" ||
          "$proc_cgroup_text_after" != "$proc_cgroup_text" ]]; then
        emit_failure 74
    fi
    RESOLVED_BOUND_PORT_STATUS="mainpid_cgroup_complete"
    RESOLVED_CONTROL_GROUP="$resolved"
}

bool_command() {
    if [[ -n "$(command -v "$1")" ]]; then printf true; else printf false; fi
}

silent_probe() {
    "$@" >/dev/null 2>&1
}

is_target_unit() {
    case "$1" in
        amneziya-web.service|amneziya-bot.service) return 0 ;;
        *) return 1 ;;
    esac
}

COLLECTED_UNIT_PORTS=""
CGROUP_PORTS_SUBREASON=""
STABLE_CGROUP_PID_COUNT=0
declare -A STABLE_CGROUP_PID_SET=()

collect_stable_cgroup_pids() {
    local control_group="$1" cgroup_root="$2" pass pid cgroup_file
    local -A first_set=() second_set=()
    local -a cgroup_files
    STABLE_CGROUP_PID_SET=()
    STABLE_CGROUP_PID_COUNT=0
    [[ -n "$control_group" ]] || return 0
    shopt -s globstar nullglob
    cgroup_files=("${cgroup_root}${control_group}"/**/cgroup.procs)
    shopt -u globstar nullglob
    (( ${#cgroup_files[@]} > 0 )) || return 1
    for pass in first second; do
        for cgroup_file in "${cgroup_files[@]}"; do
            [[ -r "$cgroup_file" ]] || return 1
            while IFS= read -r pid; do
                [[ "$pid" =~ ^[1-9][0-9]*$ ]] || return 1
                (( pid <= 4194304 )) || return 1
                if [[ "$pass" == "first" ]]; then first_set["$pid"]=1; else second_set["$pid"]=1; fi
            done < "$cgroup_file"
        done
    done
    (( ${#first_set[@]} == ${#second_set[@]} )) || return 1
    for pid in "${!first_set[@]}"; do
        [[ -n "${second_set[$pid]+present}" ]] || return 1
        STABLE_CGROUP_PID_SET["$pid"]=1
    done
    STABLE_CGROUP_PID_COUNT=${#STABLE_CGROUP_PID_SET[@]}
}

collect_ports_for_cgroup_once() {
    local control_group="$1" cgroup_root="$2" proc_root="$3"
    local pid fd target inode pid_socket_inodes all_hex_ports pid_hex_ports hex_port socket_table
    local decimal_port normalized_ports candidate_port
    local -A observed_ports=() port_pid_set=()
    COLLECTED_UNIT_PORTS=""
    CGROUP_PORTS_SUBREASON=""
    if ! collect_stable_cgroup_pids "$control_group" "$cgroup_root"; then
        CGROUP_PORTS_SUBREASON="cgroup_procs"
        return 1
    fi
    for pid in "${!STABLE_CGROUP_PID_SET[@]}"; do port_pid_set["$pid"]=1; done
    all_hex_ports=""
    if (( ${#port_pid_set[@]} == 0 )); then
        return 0
    fi
    for pid in "${!port_pid_set[@]}"; do
        if [[ ! -r "$proc_root/$pid/fd" || ! -x "$proc_root/$pid/fd" ]]; then
            CGROUP_PORTS_SUBREASON="fd_directory"
            return 1
        fi
        pid_socket_inodes=""
        shopt -s nullglob
        for fd in "$proc_root/$pid/fd"/*; do
            if ! target="$(readlink "$fd")"; then
                shopt -u nullglob
                CGROUP_PORTS_SUBREASON="fd_readlink"
                return 1
            fi
            if [[ "$target" =~ ^socket:\[([0-9]+)\]$ ]]; then
                inode="${BASH_REMATCH[1]}"
                pid_socket_inodes+="$inode"$'\n'
            fi
        done
        shopt -u nullglob
        [[ -n "$pid_socket_inodes" ]] || continue
        for socket_table in "$proc_root/$pid/net/tcp" "$proc_root/$pid/net/tcp6" "$proc_root/$pid/net/udp" "$proc_root/$pid/net/udp6"; do
            if [[ ! -r "$socket_table" ]]; then
                CGROUP_PORTS_SUBREASON="socket_table"
                return 1
            fi
        done
        if ! pid_hex_ports="$(awk -v wanted="$pid_socket_inodes" '
            BEGIN {
                count=split(wanted, values, "\n")
                for (i=1; i<=count; i++) if (values[i] != "") inode[values[i]]=1
            }
            $10 in inode && (FILENAME ~ /\/udp/ || $4 == "0A") {
                split($2, local_endpoint, ":")
                if (local_endpoint[2] != "0000") print local_endpoint[2]
            }
        ' "$proc_root/$pid/net/tcp" "$proc_root/$pid/net/tcp6" "$proc_root/$pid/net/udp" "$proc_root/$pid/net/udp6")"; then
            CGROUP_PORTS_SUBREASON="socket_parse"
            return 1
        fi
        all_hex_ports+="$pid_hex_ports"$'\n'
    done
    if ! collect_stable_cgroup_pids "$control_group" "$cgroup_root" ||
       (( ${#STABLE_CGROUP_PID_SET[@]} != ${#port_pid_set[@]} )); then
        CGROUP_PORTS_SUBREASON="pid"
        return 1
    fi
    for pid in "${!port_pid_set[@]}"; do
        if [[ -z "${STABLE_CGROUP_PID_SET[$pid]+present}" ]]; then
            CGROUP_PORTS_SUBREASON="pid"
            return 1
        fi
    done
    while read -r hex_port; do
        [[ -n "$hex_port" ]] || continue
        if [[ ! "$hex_port" =~ ^[0-9A-Fa-f]{4}$ ]] ||
           ! decimal_port="$(printf '%d' "0x$hex_port")"; then
            CGROUP_PORTS_SUBREASON="socket_parse"
            return 1
        fi
        observed_ports["$decimal_port"]=1
    done < <(printf '%s\n' "$all_hex_ports")
    normalized_ports=""
    for ((candidate_port=1; candidate_port<=65535; candidate_port++)); do
        if [[ -n "${observed_ports[$candidate_port]+present}" ]]; then
            if [[ -n "$normalized_ports" ]]; then normalized_ports+=","; fi
            normalized_ports+="$candidate_port"
        fi
    done
    COLLECTED_UNIT_PORTS="$normalized_ports"
}

collect_ports_for_cgroup() {
    local fd_readlink_attempt
    for fd_readlink_attempt in 1 2; do
        if collect_ports_for_cgroup_once "$@"; then
            return 0
        fi
        if [[ "$CGROUP_PORTS_SUBREASON" != "fd_readlink" || "$fd_readlink_attempt" == "2" ]]; then
            return 1
        fi
    done
    return 1
}

DESCENDANT_PID_COUNT=0

collect_descendant_pid_diagnostic() {
    local control_group="$1" cgroup_root="$2"
    collect_stable_cgroup_pids "$control_group" "$cgroup_root" || emit_failure 99
    DESCENDANT_PID_COUNT=$STABLE_CGROUP_PID_COUNT
}

# === COLLECTOR MAIN ===
[[ "$#" -eq 0 ]] || { printf '%s\n' '{"error":"arguments_not_supported"}'; exit 64; }
readonly EXPECTED_MODE_JSON='"mode":"read_only_resource_confirmation"'

CURRENT_STAGE="bootstrap"
for dependency in sha256sum cut tr awk uname getconf python3 df ss ip systemctl nft; do
    [[ "$(bool_command "$dependency")" == "true" ]] || emit_failure 87
done

CURRENT_STAGE="host_identity"
[[ -r /etc/machine-id && -r /proc/sys/kernel/random/boot_id ]] || emit_failure 88
machine_id_sha256="$(sha256_text "$(</etc/machine-id)")"
boot_id_sha256="$(sha256_text "$(</proc/sys/kernel/random/boot_id)")"

CURRENT_STAGE="platform"
kernel_system="$(safe_atom "$(uname -s)")"
kernel_release="$(safe_atom "$(uname -r)")"
architecture="$(uname -m)"
case "$architecture" in
    x86_64|amd64) architecture="x86_64" ;;
    *) emit_failure 89 ;;
esac
python_version="$(python3 -I -B -c 'import platform; print(platform.python_version())')"
python_soabi="$(python3 -I -B -c 'import sysconfig; print(sysconfig.get_config_var("SOABI") or "")')"
[[ -n "$python_soabi" ]] || emit_failure 90
glibc_version="$(getconf GNU_LIBC_VERSION | awk '{print $2}')"

CURRENT_STAGE="capacity"
mem_available_kib="$(awk '/^MemAvailable:/ {print $2; exit}' /proc/meminfo)"
[[ "$mem_available_kib" =~ ^[0-9]+$ ]] || emit_failure 92
mem_available_bytes=$((mem_available_kib * 1024))
filesystem_rows=""
for filesystem_path in / /opt /etc /var /run; do
    filesystem_values="$(df -B1 --output=avail,iavail "$filesystem_path" | awk 'NR==2 {print $1 "|" $2}')"
    [[ "$filesystem_values" =~ ^[0-9]+\|[0-9]+$ ]] || emit_failure 93
    filesystem_rows+="$filesystem_path|$filesystem_values"$'\n'
done

CURRENT_STAGE="candidate_inventory"
candidate_path_rows=""
for candidate_path in /opt/amn2-spain-package /opt/amn2-spain /etc/amn2-spain /var/lib/amn2-spain /var/lib/amn2-spain-docker /var/lib/amn2-spain-phase12-audit; do
    if [[ -e "$candidate_path" || -L "$candidate_path" ]]; then exists=true; else exists=false; fi
    candidate_path_rows+="$candidate_path|$exists"$'\n'
done
[[ -r /etc/passwd && -r /etc/group ]] || emit_failure 95
if awk -F: '$1 == "amn2-spain" {found=1} END {exit(found ? 0 : 1)}' /etc/passwd; then user_exists=true; else user_exists=false; fi
if awk -F: '$1 == "amn2-spain" {found=1} END {exit(found ? 0 : 1)}' /etc/group; then group_exists=true; else group_exists=false; fi
if awk -F: '$3 == "61212" {found=1} END {exit(found ? 0 : 1)}' /etc/passwd; then uid_exists=true; else uid_exists=false; fi
if awk -F: '$3 == "61212" {found=1} END {exit(found ? 0 : 1)}' /etc/group; then gid_exists=true; else gid_exists=false; fi
candidate_unit_rows=""
for candidate_unit in amn2-spain-web.service amn2-spain-bot.service amn2-spain-docker.service amn2-spain-network.service amn2-spain-forward-compat.service; do
    load_state="$(systemctl show "$candidate_unit" --property=LoadState --value 2>/dev/null)"
    if [[ "$load_state" == "not-found" || -z "$load_state" ]]; then exists=false; else exists=true; fi
    candidate_unit_rows+="$candidate_unit|$exists"$'\n'
done
if docker_binary_path="$(command -v docker 2>/dev/null)" && [[ -n "$docker_binary_path" ]]; then
    docker_binary_present=true
else
    docker_binary_present=false
fi
unset docker_binary_path
potential_socket_present=false
for potential_socket in /run/docker.sock /var/run/docker.sock; do
    if [[ -e "$potential_socket" || -L "$potential_socket" ]]; then
        potential_socket_present=true
    fi
done
daemon_process_present=false
shopt -s nullglob
for comm_file in /proc/[0-9]*/comm; do
    IFS= read -r process_name < "$comm_file" || emit_failure 94
    case "$process_name" in
        dockerd|containerd|docker-proxy) daemon_process_present=true ;;
    esac
done
shopt -u nullglob
docker_observation_safe=true
container_exists=false
container_collision_unknown=false
network_exists=false
network_collision_unknown=false
if [[ "$docker_binary_present" == "true" || "$potential_socket_present" == "true" || "$daemon_process_present" == "true" ]]; then
    docker_observation_safe=false
    container_collision_unknown=true
    network_collision_unknown=true
fi
if silent_probe ip link show dev amn2spbr0; then bridge_exists=true; else bridge_exists=false; fi
if silent_probe ip link show dev awgsp0; then interface_exists=true; else interface_exists=false; fi
if [[ -e /run/amn2-spain-docker/docker.sock || -L /run/amn2-spain-docker/docker.sock ]]; then socket_exists=true; else socket_exists=false; fi
if [[ -e /run/amn2-spain-docker || -L /run/amn2-spain-docker ]]; then runtime_directory_exists=true; else runtime_directory_exists=false; fi

CURRENT_STAGE="listeners"
listener_rows="$(ss -H -lntu | awk '
    $1 == "tcp" || $1 == "udp" {
        endpoint=$5; port=endpoint; sub(/^.*:/, "", port)
        address=endpoint; sub(/:[^:]*$/, "", address)
        gsub(/^\[/, "", address); gsub(/\]$/, "", address)
        if (port ~ /^[0-9]+$/) print $1 "|" address "|" port
    }
')"

CURRENT_STAGE="network_state"
address_json="$(ip -j address show)"
route4_json="$(ip -j -4 route show table all)"
route6_json="$(ip -j -6 route show table all)"
python3 -I -B -c 'import json,sys; [json.loads(value) for value in sys.argv[1:]]' "$address_json" "$route4_json" "$route6_json"

CURRENT_STAGE="firewall"
nft_raw="$(nft list ruleset)"
nft_json_first="$(nft -j list ruleset)"
nft_json_second="$(nft -j list ruleset)"
nft_raw_sha256="$(sha256_text "$nft_raw")"
nft_rule_count="$(printf '%s\n' "$nft_raw" | awk '/^[[:space:]]*(ip|ip6|tcp|udp|iif|oif|ct|counter|accept|drop|reject)/ {n++} END {print n+0}')"
nft_structured_sha256="$(python3 -I -B -c 'import hashlib,json,sys; v=json.loads(sys.argv[1]); b=json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode(); print(hashlib.sha256(b).hexdigest())' "$nft_json_first")"
nft_semantic_sha256_first="$(python3 -I -B -c 'import hashlib,json,sys
def clean(value):
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items() if key not in ("handle", "packets", "bytes")}
    if isinstance(value, list):
        return [clean(item) for item in value]
    return value
value=clean(json.loads(sys.argv[1])); data=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode(); print(hashlib.sha256(data).hexdigest())' "$nft_json_first")"
nft_semantic_sha256_second="$(python3 -I -B -c 'import hashlib,json,sys
def clean(value):
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items() if key not in ("handle", "packets", "bytes")}
    if isinstance(value, list):
        return [clean(item) for item in value]
    return value
value=clean(json.loads(sys.argv[1])); data=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode(); print(hashlib.sha256(data).hexdigest())' "$nft_json_second")"
[[ "$nft_semantic_sha256_first" == "$nft_semantic_sha256_second" ]] || emit_failure 96

CURRENT_STAGE="systemd_inventory"
systemd_rows=""
cgroup_diagnostic_rows=""
systemd_base_rows="$(systemctl list-units --type=service --all --no-legend --no-pager | awk '$1 ~ /\.service$/ {print $1 "|" $3 "|" $4}')"
while IFS='|' read -r unit_name active_state sub_state; do
    [[ -n "$unit_name" ]] || continue
    restart_count="$(systemctl show "$unit_name" --property=NRestarts --value)"
    [[ "$restart_count" =~ ^[0-9]+$ ]] || emit_failure 66
    CURRENT_STAGE="systemd_unit_content"
    unit_content="$(systemctl cat "$unit_name" --no-pager)"
    unit_content_sha="$(sha256_text "$unit_content")"
    unset unit_content
    CURRENT_STAGE="systemd_inventory"
    resolve_unit_cgroup "$unit_name" "$active_state" /proc
    bound_port_status="$RESOLVED_BOUND_PORT_STATUS"
    control_group="$RESOLVED_CONTROL_GROUP"
    unit_ports=""
    if [[ -n "$control_group" ]]; then
        CURRENT_STAGE="systemd_cgroup_ports"
        if ! collect_ports_for_cgroup "$control_group" /sys/fs/cgroup /proc; then
            case "$CGROUP_PORTS_SUBREASON" in
                cgroup_procs) emit_failure 75 ;;
                pid) emit_failure 76 ;;
                fd_directory) emit_failure 77 ;;
                fd_readlink) emit_failure 78 ;;
                socket_table) emit_failure 79 ;;
                socket_parse) emit_failure 80 ;;
                *) emit_failure 1 ;;
            esac
        fi
        unit_ports="$COLLECTED_UNIT_PORTS"
    fi
    collect_descendant_pid_diagnostic "$control_group" /sys/fs/cgroup
    cgroup_diagnostic_rows+="$unit_name|$DESCENDANT_PID_COUNT|true"$'\n'
    systemd_rows+="$unit_name|$active_state|$sub_state|$restart_count|$unit_content_sha|$unit_ports|exact|$bound_port_status"$'\n'
    CURRENT_STAGE="systemd_inventory"
done < <(printf '%s\n' "$systemd_base_rows")

CURRENT_STAGE="render"
export machine_id_sha256 boot_id_sha256 kernel_system kernel_release architecture
export python_version python_soabi glibc_version mem_available_bytes filesystem_rows
export candidate_path_rows user_exists group_exists uid_exists gid_exists candidate_unit_rows docker_binary_present
export potential_socket_present daemon_process_present docker_observation_safe
export container_exists container_collision_unknown network_exists network_collision_unknown
export bridge_exists interface_exists socket_exists
export runtime_directory_exists listener_rows address_json route4_json route6_json nft_raw_sha256
export nft_rule_count nft_structured_sha256 nft_semantic_sha256_first nft_json_first systemd_rows cgroup_diagnostic_rows
python3 -I -B -c '
import hashlib
import json
import os
import re

def boolean(name):
    value = os.environ[name]
    if value not in ("true", "false"):
        raise ValueError(name)
    return value == "true"

def rows(name):
    return [line for line in os.environ.get(name, "").splitlines() if line]

def text_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()

os_release = {}
with open("/etc/os-release", encoding="utf-8") as handle:
    for line in handle:
        if "=" not in line:
            continue
        key, value = line.rstrip("\n").split("=", 1)
        if key in ("ID", "VERSION_ID"):
            os_release[key] = value.strip(chr(34))
if set(os_release) != {"ID", "VERSION_ID"}:
    raise ValueError("os_release")

filesystems = []
for line in rows("filesystem_rows"):
    path, available_bytes, available_inodes = line.split("|", 2)
    filesystems.append({"path": path, "available_bytes": int(available_bytes), "available_inodes": int(available_inodes)})

addresses = []
for link in json.loads(os.environ["address_json"]):
    interface = str(link.get("ifname", ""))
    for info in link.get("addr_info", []):
        family = str(info.get("family", ""))
        if family not in ("inet", "inet6"):
            continue
        addresses.append({
            "interface": interface,
            "family": family,
            "address": str(info.get("local", "")),
            "prefix_length": int(info.get("prefixlen", 0)),
            "scope": str(info.get("scope", "")),
        })
addresses.sort(key=lambda item: (item["interface"], item["family"], item["address"], item["prefix_length"], item["scope"]))

routes = []
for family, variable in (("inet", "route4_json"), ("inet6", "route6_json")):
  for route in json.loads(os.environ[variable]):
    multipath = []
    for hop in route.get("multipath", []):
        multipath.append({"gateway": str(hop.get("gateway", "")), "interface": str(hop.get("dev", "")), "weight": int(hop.get("weight", 1))})
    multipath.sort(key=lambda item: (item["interface"], item["gateway"], item["weight"]))
    routes.append({
        "family": family,
        "destination": str(route.get("dst", "default")),
        "gateway": str(route.get("gateway", "")),
        "interface": str(route.get("dev", "")),
        "table": str(route.get("table", "main")),
        "protocol": str(route.get("protocol", "")),
        "scope": str(route.get("scope", "")),
        "type": str(route.get("type", "unicast")),
        "multipath": multipath,
    })
routes.sort(key=lambda item: (
    item["family"], item["destination"], item["gateway"], item["interface"],
    item["table"], item["protocol"], item["scope"], item["type"],
    json.dumps(item["multipath"], sort_keys=True, separators=(",", ":")),
))

fingerprint = []
for line in rows("systemd_rows"):
    unit_name, active_state, sub_state, restart_count, unit_sha, unit_ports, content_status, port_status = line.split("|", 7)
    if unit_name in ("amneziya-web.service", "amneziya-bot.service"):
        continue
    fingerprint.append({
        "kind": "unit",
        "name_sha256": text_hash(unit_name),
        "image_or_unit_sha256": unit_sha,
        "active_state": re.sub(r"[^A-Za-z0-9._:+-]", "", active_state + ":" + sub_state),
        "restart_count": int(restart_count),
        "bound_port_set": [int(value) for value in unit_ports.split(",") if value],
        "unit_content_status": content_status,
        "bound_port_status": port_status,
    })

cgroup_diagnostics = []
for line in rows("cgroup_diagnostic_rows"):
    unit_name, descendant_pid_count, stable = line.split("|", 2)
    cgroup_diagnostics.append({"unit_sha256": text_hash(unit_name), "descendant_pid_count": int(descendant_pid_count), "pid_set_stable": stable == "true"})

evidence = {
    "schema": "amn2.phase12-spain-resource-confirmation.v1",
    "mode": "read_only_resource_confirmation",
    "host_identity": {
        "machine_id_sha256": os.environ["machine_id_sha256"],
        "boot_id_sha256": os.environ["boot_id_sha256"],
    },
    "platform": {
        "kernel": {"system": os.environ["kernel_system"], "release": os.environ["kernel_release"]},
        "os_release": {"id": os_release["ID"], "version_id": os_release["VERSION_ID"]},
        "architecture": os.environ["architecture"],
        "python3": {"version": os.environ["python_version"], "soabi": os.environ["python_soabi"]},
        "glibc_version": os.environ["glibc_version"],
    },
    "capacity": {"mem_available_bytes": int(os.environ["mem_available_bytes"]), "filesystems": filesystems},
    "candidates": {
        "paths": [{"path": line.split("|", 1)[0], "exists": line.endswith("|true")} for line in rows("candidate_path_rows")],
        "identities": {
            "user_name": "amn2-spain", "user_exists": boolean("user_exists"),
            "user_id": 61212, "uid_exists": boolean("uid_exists"),
            "group_name": "amn2-spain", "group_exists": boolean("group_exists"),
            "group_id": 61212, "gid_exists": boolean("gid_exists"),
        },
        "units": [{"name": line.split("|", 1)[0], "exists": line.endswith("|true")} for line in rows("candidate_unit_rows")],
        "docker": {
            "binary_present": boolean("docker_binary_present"),
            "potential_socket_present": boolean("potential_socket_present"),
            "daemon_process_present": boolean("daemon_process_present"),
            "observation_safe": boolean("docker_observation_safe"),
            "container_name": "amn2-spain-awg",
            "container_exists": boolean("container_exists"),
            "container_collision_unknown": boolean("container_collision_unknown"),
            "network_name": "amn2-spain-net",
            "network_exists": boolean("network_exists"),
            "network_collision_unknown": boolean("network_collision_unknown"),
        },
        "network": {"bridge_name": "amn2spbr0", "bridge_exists": boolean("bridge_exists"), "interface_name": "awgsp0", "interface_exists": boolean("interface_exists")},
        "sockets": [{"path": "/run/amn2-spain-docker/docker.sock", "exists": boolean("socket_exists")}],
        "runtime_directories": [{"path": "/run/amn2-spain-docker", "exists": boolean("runtime_directory_exists")}],
    },
    "listening_sockets": [
        {"protocol": protocol, "address": address, "port": int(port)}
        for protocol, address, port in (line.split("|", 2) for line in rows("listener_rows"))
    ],
    "network_state": {"addresses": addresses, "routes": routes},
    "systemd": {"present": True, "unit_count": len(rows("systemd_rows"))},
    "cgroup_diagnostics": cgroup_diagnostics,
    "firewall": {
        "backend": "nft",
        "raw_sha256": os.environ["nft_raw_sha256"],
        "raw_rule_count": int(os.environ["nft_rule_count"]),
        "structured_snapshot_sha256": os.environ["nft_structured_sha256"],
        "semantic_sha256": os.environ["nft_semantic_sha256_first"],
        "stability_observations": 2,
        "stable": True,
        "structured_snapshot": json.loads(os.environ["nft_json_first"]),
    },
    "unrelated_service_fingerprint": fingerprint,
}
print(json.dumps(evidence, separators=(",", ":"), ensure_ascii=True))
'
