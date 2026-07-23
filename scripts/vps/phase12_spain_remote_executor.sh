#!/usr/bin/env bash
set -Eeuo pipefail

readonly MODE="${1:-}"
case "$MODE" in
    install|install-bound|manual-cleanup|manual-cleanup-bound|recover|rollback|verify) ;;
    *) printf '%s\n' 'unsupported_mode' >&2; exit 64 ;;
esac

readonly PYTHON_BIN="/usr/bin/python3"
readonly EXECUTOR_BUNDLE="/root/amn2-spain-phase12-executor.pyz"

[[ "$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')" == "3.12" ]] || {
    printf '%s\n' 'python_3_12_required' >&2
    exit 65
}

[[ -f "$EXECUTOR_BUNDLE" && ! -L "$EXECUTOR_BUNDLE" ]] || {
    printf '%s\n' 'executor_bundle_unavailable' >&2
    exit 66
}

exec "$PYTHON_BIN" -I -B "$EXECUTOR_BUNDLE" "$MODE" "${@:2}"
