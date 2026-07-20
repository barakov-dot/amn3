#!/usr/bin/env bash
set -euo pipefail

readonly MODE="${1:-}"
[[ "$MODE" == "preflight" ]] || { printf '%s\n' '{"error":"unsupported_mode"}'; exit 64; }

sha256_text() {
    printf '%s' "$1" | sha256sum | cut -d' ' -f1
}

safe_atom() {
    printf '%s' "$1" | tr -cd 'A-Za-z0-9._:+-'
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

ports_for_cgroup() {
    local control_group="$1"
    local cgroup_file="/sys/fs/cgroup${control_group}/cgroup.procs"
    local pid fd target inode pid_socket_inodes all_hex_ports pid_hex_ports hex_port cgroup_pids socket_table
    [[ -r "$cgroup_file" ]] || return 1
    all_hex_ports=""
    cgroup_pids="$(awk '{print $1}' "$cgroup_file")" || return 1
    while read -r pid; do
        [[ "$pid" =~ ^[0-9]+$ ]] || return 1
        [[ -r "/proc/$pid/fd" && -x "/proc/$pid/fd" ]] || return 1
        pid_socket_inodes=""
        shopt -s nullglob
        for fd in "/proc/$pid/fd"/*; do
            target="$(readlink "$fd")" || return 1
            if [[ "$target" =~ ^socket:\[([0-9]+)\]$ ]]; then
                inode="${BASH_REMATCH[1]}"
                pid_socket_inodes+="$inode"$'\n'
            fi
        done
        shopt -u nullglob
        [[ -n "$pid_socket_inodes" ]] || continue
        for socket_table in "/proc/$pid/net/tcp" "/proc/$pid/net/tcp6" "/proc/$pid/net/udp" "/proc/$pid/net/udp6"; do
            [[ -r "$socket_table" ]] || return 1
        done
        pid_hex_ports="$(awk -v wanted="$pid_socket_inodes" '
            BEGIN {
                count=split(wanted, values, "\n")
                for (i=1; i<=count; i++) if (values[i] != "") inode[values[i]]=1
            }
            $10 in inode && (FILENAME ~ /\/udp/ || $4 == "0A") {
                split($2, local_endpoint, ":")
                if (local_endpoint[2] != "0000") print local_endpoint[2]
            }
        ' "/proc/$pid/net/tcp" "/proc/$pid/net/tcp6" "/proc/$pid/net/udp" "/proc/$pid/net/udp6")" || return 1
        all_hex_ports+="$pid_hex_ports"$'\n'
    done <<< "$cgroup_pids"
    while read -r hex_port; do
        [[ -n "$hex_port" ]] || continue
        printf '%d\n' "0x$hex_port"
    done <<< "$all_hex_ports" | sort -nu | paste -sd, -
}

kernel_name="$(safe_atom "$(uname -s)")"
kernel_release="$(safe_atom "$(uname -r)")"
cpu_count="$(getconf _NPROCESSORS_ONLN)"
memory_kib="$(awk '/^MemTotal:/ {print $2; exit}' /proc/meminfo)"
disk_bytes="$(df -B1 --output=size / | awk 'NR==2 {print $1}')"
clock_utc="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

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
    exit 68
fi

ssh_policy=""
if [[ -n "$(command -v sshd)" ]]; then
    ssh_policy="$(sshd -T | awk '
        $1 == "pubkeyauthentication" || $1 == "permitrootlogin" ||
        $1 == "maxauthtries" || $1 == "allowtcpforwarding" ||
        $1 == "x11forwarding" {print $1 "|" $2}
    ' | sort -u)"
else
    exit 69
fi
[[ -n "$ssh_policy" ]] || exit 70

docker_rows=""
if [[ -n "$(command -v docker)" ]]; then
    docker_base_rows="$(docker ps -a --format '{{.Names}}|{{.Image}}|{{.State}}|{{.Ports}}')"
    while IFS='|' read -r container_name image_name active_state port_text; do
        [[ -n "$container_name" ]] || continue
        restart_count="$(docker inspect --format '{{.RestartCount}}' "$container_name")"
        [[ "$restart_count" =~ ^[0-9]+$ ]] || exit 65
        docker_rows+="$container_name|$image_name|$active_state|$port_text|$restart_count"$'\n'
    done <<< "$docker_base_rows"
fi

systemd_rows=""
if [[ -n "$(command -v systemctl)" ]]; then
    systemd_base_rows="$(systemctl list-units --type=service --all --no-legend --no-pager | awk '$1 ~ /\.service$/ {print $1 "|" $3 "|" $4}')"
    while IFS='|' read -r unit_name active_state sub_state; do
        [[ -n "$unit_name" ]] || continue
        restart_count="$(systemctl show "$unit_name" --property=NRestarts --value)"
        [[ "$restart_count" =~ ^[0-9]+$ ]] || exit 66
        unit_content="$(systemctl cat "$unit_name" --no-pager)"
        unit_content_sha="$(sha256_text "$unit_content")"
        unset unit_content
        unit_ports=""
        control_group="$(systemctl show "$unit_name" --property=ControlGroup --value)"
        if [[ -n "$control_group" ]]; then
            unit_ports="$(ports_for_cgroup "$control_group")"
            bound_port_status="cgroup_complete"
        elif [[ "$active_state" == "active" ]]; then
            exit 67
        else
            bound_port_status="no_cgroup"
        fi
        systemd_rows+="$unit_name|$active_state|$sub_state|$restart_count|$unit_content_sha|$unit_ports|exact|$bound_port_status"$'\n'
    done <<< "$systemd_base_rows"
fi

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
