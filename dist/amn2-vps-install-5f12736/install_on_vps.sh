#!/usr/bin/env bash
set -euo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH:-}"

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVE="${PACKAGE_DIR}/amn2-source-5f12736.zip"
SMOKE_SCRIPT="${PACKAGE_DIR}/amn2_api_loopback_smoke.sh"
INSTALL_DIR="${INSTALL_DIR:-/opt/amn2}"
SERVICE_USER="${SERVICE_USER:-amneziya}"
FORCE="false"

if [[ "${1:-}" == "--force" ]]; then
  FORCE="true"
fi

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo ./install_on_vps.sh"
  exit 1
fi

if [[ ! -f "${ARCHIVE}" ]]; then
  echo "Archive not found: ${ARCHIVE}"
  exit 1
fi

if [[ ! -f "${SMOKE_SCRIPT}" ]]; then
  echo "Smoke script not found: ${SMOKE_SCRIPT}"
  exit 1
fi

if [[ -e "${INSTALL_DIR}" && "${FORCE}" != "true" ]]; then
  echo "${INSTALL_DIR} already exists. Re-run with --force only after backup."
  exit 1
fi

command -v python3 >/dev/null || {
  echo "python3 is required. Install Python 3.12+ first."
  exit 1
}

if ! python3 - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 12) else 1)
PY
then
  echo "Python 3.12+ is required."
  exit 1
fi

create_service_user() {
  if command -v useradd >/dev/null 2>&1; then
    useradd --system --create-home --shell "$(nologin_shell)" "${SERVICE_USER}"
    return
  fi
  if command -v adduser >/dev/null 2>&1; then
    adduser --system --home "/home/${SERVICE_USER}" --shell "$(nologin_shell)" --group "${SERVICE_USER}"
    return
  fi
  echo "Cannot create service user: neither useradd nor adduser is available."
  echo "On Debian/Ubuntu install it first: apt update && apt install -y passwd adduser"
  exit 1
}

nologin_shell() {
  if [[ -x /usr/sbin/nologin ]]; then
    echo /usr/sbin/nologin
  elif [[ -x /sbin/nologin ]]; then
    echo /sbin/nologin
  else
    echo /bin/false
  fi
}

if ! id "${SERVICE_USER}" >/dev/null 2>&1; then
  create_service_user
fi

rm -rf "${INSTALL_DIR}.new"
mkdir -p "${INSTALL_DIR}.new"

python3 - <<PY
from pathlib import Path
from zipfile import ZipFile

archive = Path("${ARCHIVE}")
target = Path("${INSTALL_DIR}.new")
with ZipFile(archive) as zf:
    zf.extractall(target)
PY

if [[ ! -d "${INSTALL_DIR}.new/amn2" ]]; then
  echo "Unexpected archive layout: expected amn2/ prefix."
  exit 1
fi

if [[ -e "${INSTALL_DIR}" ]]; then
  mv "${INSTALL_DIR}" "${INSTALL_DIR}.backup.$(date +%Y%m%d%H%M%S)"
fi
mv "${INSTALL_DIR}.new/amn2" "${INSTALL_DIR}"
rm -rf "${INSTALL_DIR}.new"

cd "${INSTALL_DIR}"
python3 -m venv venv
venv/bin/python -m pip install -U pip
venv/bin/python -m pip install -e .

mkdir -p data logs backups config_templates

if [[ ! -f ".env" ]]; then
  cp deploy/examples/.env.production.example .env
fi
if [[ ! -f "servers.yml" ]]; then
  cp deploy/examples/servers.docker.example.yml servers.yml
fi

install -m 700 "${SMOKE_SCRIPT}" "${INSTALL_DIR}/amn2_api_loopback_smoke.sh"

chown -R "${SERVICE_USER}:${SERVICE_USER}" "${INSTALL_DIR}"
chmod 600 "${INSTALL_DIR}/.env" || true

cat <<EOF
Installed to ${INSTALL_DIR}.

Next steps:
1. Edit ${INSTALL_DIR}/.env and ${INSTALL_DIR}/servers.yml.
2. Keep VPS_APPLY_ENABLED=false for first loopback API smoke.
3. Run API-only smoke; do not run server preflight for this check:
   cd ${INSTALL_DIR}
   source venv/bin/activate
   export VPS_APPLY_ENABLED=false
   export AMN2_RUN_PREFLIGHT=0
   export AMN2_SERVER_NAME=local
   bash ./amn2_api_loopback_smoke.sh
4. Run bot/network/server SSH dry-run checks only as a separate operator gate.
EOF
