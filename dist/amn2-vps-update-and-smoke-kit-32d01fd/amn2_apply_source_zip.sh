#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

AMN2_DIR="${AMN2_DIR:-/opt/amn2}"
AMN2_SOURCE_ZIP="${AMN2_SOURCE_ZIP:-/root/amn2-vps-update-and-smoke-kit-32d01fd/amn2-codex-vps-test-prep-32d01fd-source.zip}"
AMN2_EXPECTED_SOURCE_SHA="${AMN2_EXPECTED_SOURCE_SHA:-034753DA7EC42ACF869519F43909EEFDC8A392A5665B2A33C935F8A058CCB99B}"
AMN2_EXPECTED_SOURCE_COMMIT="${AMN2_EXPECTED_SOURCE_COMMIT:-32d01fd}"

log() {
  printf '[amn2-source-update] %s\n' "$*"
}

die() {
  printf '[amn2-source-update] ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

require_cmd tar

[ -d "$AMN2_DIR" ] || die "AMN2_DIR does not exist: $AMN2_DIR"
[ -f "$AMN2_SOURCE_ZIP" ] || die "AMN2_SOURCE_ZIP does not exist: $AMN2_SOURCE_ZIP"

if [ -x "$AMN2_DIR/venv/bin/python" ]; then
  PYTHON_BIN="$AMN2_DIR/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  die "python not found"
fi

ACTUAL_SHA="$("$PYTHON_BIN" - "$AMN2_SOURCE_ZIP" <<'PY'
import hashlib
import sys
from pathlib import Path

print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest().upper())
PY
)"

if [ "$ACTUAL_SHA" != "$AMN2_EXPECTED_SOURCE_SHA" ]; then
  die "source zip SHA256 mismatch: actual=$ACTUAL_SHA expected=$AMN2_EXPECTED_SOURCE_SHA"
fi

RUN_ID="$(date -u '+%Y%m%dT%H%M%SZ')"
RUN_ROOT="${AMN2_UPDATE_LOG_DIR:-$AMN2_DIR/vps-smoke/source-update-$RUN_ID}"
STAGING="$RUN_ROOT/source"
mkdir -p "$STAGING"
chmod 700 "$RUN_ROOT"

log "target: $AMN2_DIR"
log "source zip: $AMN2_SOURCE_ZIP"
log "source sha: $ACTUAL_SHA"
log "work dir: $RUN_ROOT"

"$PYTHON_BIN" - "$AMN2_SOURCE_ZIP" > "$RUN_ROOT/source-zip-check.txt" <<'PY'
import sys
import zipfile
from pathlib import PurePosixPath

zip_path = sys.argv[1]
forbidden_exact = {
    ".env",
    "server.yml",
    "servers.yml",
}
forbidden_prefixes = (
    ".git/",
    "data/",
    "venv/",
    ".venv/",
    "logs/",
    "tmp/",
    "__pycache__/",
    ".pytest_cache/",
)
forbidden_suffixes = (
    ".sqlite3",
    ".db",
    ".key",
    ".pem",
)

with zipfile.ZipFile(zip_path) as archive:
    names = archive.namelist()

bad = []
for name in names:
    normalized = str(PurePosixPath(name))
    if normalized in forbidden_exact:
        bad.append(normalized)
    if any(normalized.startswith(prefix) for prefix in forbidden_prefixes):
        bad.append(normalized)
    if any(normalized.endswith(suffix) for suffix in forbidden_suffixes):
        bad.append(normalized)

print(f"entry_count={len(names)}")
print(f"forbidden_entries={len(bad)}")
for entry in bad:
    print(entry)
if bad:
    raise SystemExit(1)
PY

"$PYTHON_BIN" -m zipfile -e "$AMN2_SOURCE_ZIP" "$STAGING"

if [ ! -f "$STAGING/app/api/app.py" ]; then
  die "source zip does not contain app/api/app.py"
fi
if [ ! -f "$STAGING/app/services/api_smoke.py" ]; then
  die "source zip does not contain app/services/api_smoke.py"
fi
if [ ! -f "$STAGING/app/services/integration_status.py" ]; then
  die "source zip does not contain app/services/integration_status.py"
fi

{
  printf 'run_id=%s\n' "$RUN_ID"
  printf 'target=%s\n' "$AMN2_DIR"
  printf 'source_zip=%s\n' "$AMN2_SOURCE_ZIP"
  printf 'source_sha=%s\n' "$ACTUAL_SHA"
  printf 'expected_commit=%s\n' "$AMN2_EXPECTED_SOURCE_COMMIT"
  printf 'python=%s\n' "$("$PYTHON_BIN" --version 2>&1)"
} > "$RUN_ROOT/source-update-summary.txt"

if [ -f "$AMN2_DIR/.env" ]; then
  printf '.env: preserved\n' >> "$RUN_ROOT/source-update-summary.txt"
fi
if [ -d "$AMN2_DIR/data" ]; then
  printf 'data/: preserved\n' >> "$RUN_ROOT/source-update-summary.txt"
fi
if [ -d "$AMN2_DIR/venv" ]; then
  printf 'venv/: preserved\n' >> "$RUN_ROOT/source-update-summary.txt"
fi
if [ -f "$AMN2_DIR/servers.yml" ]; then
  printf 'servers.yml: preserved\n' >> "$RUN_ROOT/source-update-summary.txt"
fi

log "overlaying tracked source files; .env/data/venv/servers.yml are not present in source zip"
tar -C "$STAGING" -cf - . | tar -C "$AMN2_DIR" -xf -
printf '%s\n' "$AMN2_EXPECTED_SOURCE_COMMIT" > "$AMN2_DIR/.amn2_source_overlay_commit"

cd "$AMN2_DIR"
"$PYTHON_BIN" -m pip install -e . > "$RUN_ROOT/pip-install-editable.txt" 2>&1

"$PYTHON_BIN" - <<'PY' > "$RUN_ROOT/source-import-check.txt"
import importlib

for module in ("fastapi", "uvicorn", "app.cli", "app.api.app", "app.services.api_smoke", "app.services.integration_status"):
    importlib.import_module(module)
    print(f"{module}: ok")
PY

cat <<EOF | tee -a "$RUN_ROOT/source-update-summary.txt"
source_update_status=passed
target=$AMN2_DIR
source_commit=$AMN2_EXPECTED_SOURCE_COMMIT
safe_log_dir=$RUN_ROOT
next=run ./amn2_api_loopback_smoke.sh from $AMN2_DIR
EOF
