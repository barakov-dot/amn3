#!/usr/bin/env bash
set -u

AMN_PROJECT_DIR="${AMN_PROJECT_DIR:-/opt/amn2}"
AMN_RUNTIME="${AMN_RUNTIME:-host_systemd}"
AMN_INTERFACE="${AMN_INTERFACE:-awg0}"
AMN_SERVICE_NAME="${AMN_SERVICE_NAME:-awg-quick@${AMN_INTERFACE}}"
AMN_CONTAINER_NAME="${AMN_CONTAINER_NAME:-amnezia-awg}"
AMN_VPN_PORT="${AMN_VPN_PORT:-30001}"
AMN_WEB_PORT="${AMN_WEB_PORT:-3030}"

ERRORS=0
WARNINGS=0

info() {
    printf '[INFO] %s\n' "$1"
}

ok() {
    printf '[OK] %s\n' "$1"
}

warn() {
    WARNINGS=$((WARNINGS + 1))
    printf '[WARN] %s\n' "$1"
}

error() {
    ERRORS=$((ERRORS + 1))
    printf '[ERROR] %s\n' "$1"
}

has_command() {
    command -v "$1" >/dev/null 2>&1
}

require_command() {
    if has_command "$1"; then
        ok "command is available: $1"
    else
        error "command is missing: $1"
    fi
}

optional_command() {
    if has_command "$1"; then
        ok "optional command is available: $1"
    else
        warn "optional command is missing: $1"
    fi
}

check_project_dir() {
    local relative_path="$1"
    local full_path="${AMN_PROJECT_DIR}/${relative_path}"
    if [ -d "$full_path" ]; then
        ok "directory exists: $full_path"
    else
        warn "directory is missing: $full_path"
    fi
}

check_udp_port() {
    if ! has_command ss; then
        warn "cannot inspect UDP sockets because ss is missing"
        return
    fi
    if ss -lun | grep -Eq "[:.]${AMN_VPN_PORT}[[:space:]]"; then
        ok "UDP port is visible: ${AMN_VPN_PORT}"
    else
        warn "UDP port is not visible: ${AMN_VPN_PORT}"
    fi
}

check_web_port() {
    if ! has_command ss; then
        warn "cannot inspect TCP sockets because ss is missing"
        return
    fi
    if ss -lnt | grep -Eq "[:.]${AMN_WEB_PORT}[[:space:]]"; then
        ok "web admin TCP port is listening: ${AMN_WEB_PORT}"
    else
        warn "web admin TCP port is not listening: ${AMN_WEB_PORT}"
    fi
}

check_host_systemd_runtime() {
    require_command systemctl
    require_command awg
    require_command awg-quick

    if has_command systemctl; then
        if systemctl is-active "$AMN_SERVICE_NAME" >/dev/null 2>&1; then
            ok "systemd service is active: $AMN_SERVICE_NAME"
        else
            warn "systemd service is not active: $AMN_SERVICE_NAME"
        fi
    fi

    if has_command awg; then
        if awg show "$AMN_INTERFACE" >/dev/null 2>&1; then
            ok "awg interface is readable: $AMN_INTERFACE"
        else
            warn "awg interface is not readable: $AMN_INTERFACE"
        fi
    fi
}

check_docker_runtime() {
    require_command docker

    if ! has_command docker; then
        return
    fi

    if docker ps --format '{{.Names}}' | grep -Fxq "$AMN_CONTAINER_NAME"; then
        ok "Docker container is running: $AMN_CONTAINER_NAME"
    else
        error "Docker container is not running: $AMN_CONTAINER_NAME"
    fi

    if docker exec "$AMN_CONTAINER_NAME" command -v awg >/dev/null 2>&1; then
        ok "awg is available inside container: $AMN_CONTAINER_NAME"
    else
        warn "awg is not available inside container: $AMN_CONTAINER_NAME"
    fi

    if docker exec "$AMN_CONTAINER_NAME" awg show "$AMN_INTERFACE" >/dev/null 2>&1; then
        ok "awg interface is readable inside container: $AMN_INTERFACE"
    else
        warn "awg interface is not readable inside container: $AMN_INTERFACE"
    fi
}

main() {
    info "Amneziya runtime check"
    info "project_dir=${AMN_PROJECT_DIR}"
    info "runtime=${AMN_RUNTIME}"
    info "interface=${AMN_INTERFACE}"
    info "vpn_udp_port=${AMN_VPN_PORT}"
    info "web_tcp_port=${AMN_WEB_PORT}"

    require_command python3
    require_command git
    require_command ss
    optional_command curl
    optional_command journalctl
    optional_command sshpass

    check_project_dir data
    check_project_dir logs
    check_project_dir backups
    check_project_dir config_templates

    case "$AMN_RUNTIME" in
        host_systemd)
            check_host_systemd_runtime
            ;;
        docker)
            check_docker_runtime
            ;;
        *)
            error "unsupported AMN_RUNTIME: $AMN_RUNTIME"
            ;;
    esac

    check_udp_port
    check_web_port

    info "warnings=${WARNINGS}"
    info "errors=${ERRORS}"
    if [ "$ERRORS" -gt 0 ]; then
        exit 1
    fi
}

main "$@"
