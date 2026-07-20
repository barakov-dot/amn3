#!/usr/bin/env bash
set -Eeuo pipefail

CURRENT_STAGE="bootstrap"

emit_failure() {
    local rc="${1:-1}"
    case "$CURRENT_STAGE" in
        bootstrap|os_kernel|capacity|sockets|firewall|ssh_policy|docker_inventory|systemd_inventory|systemd_unit_content|systemd_cgroup_ports|render) ;;
        *) CURRENT_STAGE="bootstrap" ;;
    esac
    if [[ ! "$rc" =~ ^[0-9]+$ ]] || (( rc < 1 || rc > 255 )); then
        rc=1
    fi
    trap - ERR
    printf 'AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=%s|exit=%s\n' "$CURRENT_STAGE" "$rc"
    exit "$rc"
}

trap 'emit_failure "$?"' ERR

readonly MODE="${1:-}"
[[ "$MODE" == "preflight" ]] || { printf '%s\n' '{"error":"unsupported_mode"}'; exit 64; }

sha256_text() {
    printf '%s' "$1" | sha256sum | cut -d' ' -f1
}

safe_atom() {
    printf '%s' "$1" | tr -cd 'A-Za-z0-9._:+-'
}

safe_cgroup_path() {
    local path="$1" segment
    local -a segments
    [[ "$path" == /* && "$path" != *'|'* && "$path" != *$'\n'* && "$path" != *$'\r'* ]] || return 1
    IFS='/' read -r -a segments <<< "$path"
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
        IFS=',' read -r -a controller_list <<< "$controllers"
        for controller in "${controller_list[@]}"; do
            if [[ "$controller" == "name=systemd" ]]; then
                safe_cgroup_path "$path" || return 1
                v1_path="$path"
                ((v1_count += 1))
            fi
        done
    done <<< "$text"
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
    read -r -a stat_fields <<< "$stat_tail"
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

is_target_container() {
    case "$1" in
        amnezia-awg2) return 0 ;;
        *) return 1 ;;
    esac
}

is_target_unit() {
    case "$1" in
        amneziya-web.service|amneziya-bot.service) return 0 ;;
        *) return 1 ;;
    esac
}

COLLECTED_UNIT_PORTS=""
CGROUP_PORTS_SUBREASON=""

collect_ports_for_cgroup() {
    local control_group="$1" cgroup_root="$2" proc_root="$3"
    local cgroup_file="${cgroup_root}${control_group}/cgroup.procs"
    local pid fd target inode pid_socket_inodes all_hex_ports pid_hex_ports hex_port cgroup_pids socket_table
    local decimal_port decimal_ports normalized_ports
    COLLECTED_UNIT_PORTS=""
    CGROUP_PORTS_SUBREASON=""
    if [[ ! -r "$cgroup_file" ]]; then
        CGROUP_PORTS_SUBREASON="cgroup_procs"
        return 1
    fi
    all_hex_ports=""
    if ! cgroup_pids="$(awk '{print $1}' "$cgroup_file")"; then
        CGROUP_PORTS_SUBREASON="cgroup_procs"
        return 1
    fi
    if [[ -z "$cgroup_pids" ]]; then
        return 0
    fi
    while read -r pid; do
        if [[ ! "$pid" =~ ^[0-9]+$ ]]; then
            CGROUP_PORTS_SUBREASON="pid"
            return 1
        fi
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
    done <<< "$cgroup_pids"
    decimal_ports=""
    while read -r hex_port; do
        [[ -n "$hex_port" ]] || continue
        if [[ ! "$hex_port" =~ ^[0-9A-Fa-f]{4}$ ]] ||
           ! decimal_port="$(printf '%d' "0x$hex_port")"; then
            CGROUP_PORTS_SUBREASON="socket_parse"
            return 1
        fi
        decimal_ports+="$decimal_port"$'\n'
    done <<< "$all_hex_ports"
    if ! normalized_ports="$(printf '%s' "$decimal_ports" | sort -nu | paste -sd, -)"; then
        CGROUP_PORTS_SUBREASON="socket_parse"
        return 1
    fi
    COLLECTED_UNIT_PORTS="$normalized_ports"
}

CURRENT_STAGE="os_kernel"
kernel_name="$(safe_atom "$(uname -s)")"
kernel_release="$(safe_atom "$(uname -r)")"
CURRENT_STAGE="capacity"
cpu_count="$(getconf _NPROCESSORS_ONLN)"
memory_kib="$(awk '/^MemTotal:/ {print $2; exit}' /proc/meminfo)"
disk_bytes="$(df -B1 --output=size / | awk 'NR==2 {print $1}')"
clock_utc="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

CURRENT_STAGE="sockets"
socket_rows="$(ss -H -lntu | awk '
    function scope_of(a) {
        gsub(/^\[/, "", a); gsub(/\]$/, "", a)
        if (a == "*" || a == "0.0.0.0" || a == "::") return "wildcard"
        if (a == "127.0.0.1" || a == "::1") return "loopback"
        if (a ~ /^10\./ || a ~ /^192\.168\./ || a ~ /^172\.(1[6-9]|2[0-9]|3[01])\./ || a ~ /^f[cd]/) return "private"
        if (a ~ /^169\.254\./ || a ~ /^fe80:/) return "linklocal"
        return "public"
    }
    $1 == "tcp" || $1 == "udp" {
        endpoint=$5; port=endpoint; sub(/^.*:/, "", port)
        address=endpoint; sub(/:[^:]*$/, "", address)
        if (port ~ /^[0-9]+$/) print $1 "|" scope_of(address) "|" port
    }
' | sort -u)"

CURRENT_STAGE="firewall"
firewall_backend="none"
firewall_digest="$(sha256_text none)"
firewall_rule_count=0
if [[ -n "$(command -v nft)" ]]; then
    firewall_backend="nft"
    firewall_view="$(nft list ruleset 2>/dev/null)"
    firewall_digest="$(sha256_text "$firewall_view")"
    firewall_rule_count="$(printf '%s\n' "$firewall_view" | awk '/^[[:space:]]*(ip|ip6|tcp|udp|iif|oif|ct|counter|accept|drop|reject)/ {n++} END {print n+0}')"
elif [[ -n "$(command -v iptables-save)" ]]; then
    firewall_backend="iptables"
    firewall_view="$(iptables-save)"
    firewall_digest="$(sha256_text "$firewall_view")"
    firewall_rule_count="$(printf '%s\n' "$firewall_view" | awk '/^-A / {n++} END {print n+0}')"
else
    emit_failure 68
fi

CURRENT_STAGE="ssh_policy"
ssh_policy=""
if [[ -n "$(command -v sshd)" ]]; then
    ssh_policy="$(sshd -T | awk '
        $1 == "pubkeyauthentication" || $1 == "permitrootlogin" ||
        $1 == "maxauthtries" || $1 == "allowtcpforwarding" ||
        $1 == "x11forwarding" {print $1 "|" $2}
    ' | sort -u)"
else
    emit_failure 69
fi
[[ -n "$ssh_policy" ]] || emit_failure 70

CURRENT_STAGE="docker_inventory"
docker_rows=""
if [[ -n "$(command -v docker)" ]]; then
    docker_base_rows="$(docker ps -a --format '{{.Names}}|{{.Image}}|{{.State}}|{{.Ports}}')"
    while IFS='|' read -r container_name image_name active_state port_text; do
        [[ -n "$container_name" ]] || continue
        restart_count="$(docker inspect --format '{{.RestartCount}}' "$container_name")"
        [[ "$restart_count" =~ ^[0-9]+$ ]] || emit_failure 65
        docker_rows+="$container_name|$image_name|$active_state|$port_text|$restart_count"$'\n'
    done <<< "$docker_base_rows"
fi

CURRENT_STAGE="systemd_inventory"
systemd_rows=""
if [[ -n "$(command -v systemctl)" ]]; then
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
                    "cgroup_procs") emit_failure 75 ;;
                    "pid") emit_failure 76 ;;
                    "fd_directory") emit_failure 77 ;;
                    "fd_readlink") emit_failure 78 ;;
                    "socket_table") emit_failure 79 ;;
                    "socket_parse") emit_failure 80 ;;
                    *) emit_failure 1 ;;
                esac
            fi
            unit_ports="$COLLECTED_UNIT_PORTS"
        fi
        systemd_rows+="$unit_name|$active_state|$sub_state|$restart_count|$unit_content_sha|$unit_ports|exact|$bound_port_status"$'\n'
        CURRENT_STAGE="systemd_inventory"
    done <<< "$systemd_base_rows"
fi

CURRENT_STAGE="render"
printf '%s' '{"schema":"amn2.spain-readonly-preflight.v1"'
printf ',"mode":"preflight"'
printf ',"os_kernel":{"system":"%s","release":"%s"}' "$kernel_name" "$kernel_release"
printf ',"capacity":{"cpu_logical":%s,"memory_kib":%s,"root_disk_bytes":%s}' "$cpu_count" "$memory_kib" "$disk_bytes"
printf ',"clock":{"utc":"%s"}' "$clock_utc"

printf ',"listening_sockets":['
first=1
while IFS='|' read -r protocol scope port; do
    [[ -n "$protocol" ]] || continue
    [[ $first -eq 1 ]] || printf ','
    first=0
    printf '{"protocol":"%s","scope":"%s","port":%s}' "$protocol" "$scope" "$port"
done <<< "$socket_rows"
printf ']'

printf ',"docker":{"present":%s,"containers":[' "$(bool_command docker)"
first=1
while IFS='|' read -r container_name image_name active_state port_text restart_count; do
    [[ -n "$container_name" ]] || continue
    name_hash="$(sha256_text "$container_name")"
    image_hash="$(sha256_text "$image_name")"
    port_set="$(printf '%s' "$port_text" | awk -F',' '{for(i=1;i<=NF;i++){v=$i; sub(/^.*:/,"",v); sub(/->.*$/,"",v); sub(/\/.*/,"",v); if(v~/^[0-9]+$/) print v}}' | sort -nu | paste -sd, -)"
    [[ $first -eq 1 ]] || printf ','
    first=0
    printf '{"name_sha256":"%s","image_sha256":"%s","active_state":"%s","bound_port_set":[%s]}' "$name_hash" "$image_hash" "$(safe_atom "$active_state")" "$port_set"
done <<< "$docker_rows"
printf ']}'

printf ',"systemd":{"present":%s,"units":[' "$(bool_command systemctl)"
first=1
while IFS='|' read -r unit_name active_state sub_state restart_count unit_content_sha unit_ports unit_content_status bound_port_status; do
    [[ -n "$unit_name" ]] || continue
    [[ $first -eq 1 ]] || printf ','
    first=0
    printf '{"unit_sha256":"%s","active_state":"%s","sub_state":"%s"}' "$(sha256_text "$unit_name")" "$(safe_atom "$active_state")" "$(safe_atom "$sub_state")"
done <<< "$systemd_rows"
printf ']}'

printf ',"firewall":{"backend":"%s","rules_sha256":"%s","rule_count":%s}' "$firewall_backend" "$firewall_digest" "$firewall_rule_count"
printf ',"ssh_effective_policy":['
first=1
while IFS='|' read -r policy_name policy_value; do
    [[ -n "$policy_name" ]] || continue
    [[ $first -eq 1 ]] || printf ','
    first=0
    printf '{"name":"%s","value":"%s"}' "$(safe_atom "$policy_name")" "$(safe_atom "$policy_value")"
done <<< "$ssh_policy"
printf ']'

printf ',"package_presence":{'
first=1
for package_name in bash python3 docker systemctl ss nft iptables sshd; do
    [[ $first -eq 1 ]] || printf ','
    first=0
    printf '"%s":%s' "$package_name" "$(bool_command "$package_name")"
done
printf '}'

printf ',"unrelated_service_fingerprint":['
first=1
while IFS='|' read -r container_name image_name active_state port_text restart_count; do
    [[ -n "$container_name" ]] || continue
    is_target_container "$container_name" && continue
    port_set="$(printf '%s' "$port_text" | awk -F',' '{for(i=1;i<=NF;i++){v=$i; sub(/^.*:/,"",v); sub(/->.*$/,"",v); sub(/\/.*/,"",v); if(v~/^[0-9]+$/) print v}}' | sort -nu | paste -sd, -)"
    [[ $first -eq 1 ]] || printf ','
    first=0
    printf '{"kind":"container","name_sha256":"%s","image_or_unit_sha256":"%s","active_state":"%s","restart_count":%s,"bound_port_set":[%s]}' "$(sha256_text "$container_name")" "$(sha256_text "$image_name")" "$(safe_atom "$active_state")" "$restart_count" "$port_set"
done <<< "$docker_rows"
while IFS='|' read -r unit_name active_state sub_state restart_count unit_content_sha unit_ports unit_content_status bound_port_status; do
    [[ -n "$unit_name" ]] || continue
    is_target_unit "$unit_name" && continue
    [[ $first -eq 1 ]] || printf ','
    first=0
    printf '{"kind":"unit","name_sha256":"%s","image_or_unit_sha256":"%s","active_state":"%s","restart_count":%s,"bound_port_set":[%s],"unit_content_status":"%s","bound_port_status":"%s"}' "$(sha256_text "$unit_name")" "$unit_content_sha" "$(safe_atom "$active_state:$sub_state")" "$restart_count" "$unit_ports" "$unit_content_status" "$bound_port_status"
done <<< "$systemd_rows"
printf ']}\n'
