#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

AMN2_DIR="${AMN2_DIR:-/opt/amn2}"
AMN2_SOURCE_ZIP="${AMN2_SOURCE_ZIP:-/root/amn2-vps-update-and-smoke-kit-1c7fb78/amn2-codex-vps-test-prep-1c7fb78-source.zip}"
AMN2_EXPECTED_SOURCE_SHA="${AMN2_EXPECTED_SOURCE_SHA:-B99CBD51759076F60BE4BE11DC3F548051D1D6B2CED89641203206F5726A7BBA}"
AMN2_EXPECTED_SOURCE_COMMIT="${AMN2_EXPECTED_SOURCE_COMMIT:-1c7fb78}"

log() {
  printf '[amn2-source-update] %s\n' "$*"
}

die() {
  printf '[amn2-source-update] ERROR: %s\n' "$*" >&2
  exit 1
}

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

log "overlaying tracked source files; preserving target root metadata and service-readable source permissions"
"$PYTHON_BIN" - "$STAGING" "$AMN2_DIR" >> "$RUN_ROOT/source-update-summary.txt" <<'PY'
import os
import shutil
import stat
import sys
from pathlib import Path


staging = Path(sys.argv[1])
target = Path(sys.argv[2])
target_gid = target.stat().st_gid
copied_roots = []


def remove_existing(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def copy_item(src: Path, dst: Path) -> None:
    if src.is_dir() and not src.is_symlink():
        if dst.exists() and not dst.is_dir():
            remove_existing(dst)
        shutil.copytree(src, dst, dirs_exist_ok=True, symlinks=True)
    else:
        if dst.exists() and dst.is_dir() and not dst.is_symlink():
            remove_existing(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst, follow_symlinks=False)


def normalize_permissions(path: Path) -> None:
    if path.is_symlink():
        return
    mode = path.stat().st_mode
    try:
        os.chown(path, -1, target_gid)
    except (AttributeError, PermissionError, OSError):
        pass

    if stat.S_ISDIR(mode):
        os.chmod(path, 0o750)
    elif stat.S_ISREG(mode):
        executable = bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
        os.chmod(path, 0o750 if executable else 0o640)


for child in staging.iterdir():
    destination = target / child.name
    copy_item(child, destination)
    copied_roots.append(destination)

for root in copied_roots:
    if root.is_dir() and not root.is_symlink():
        for current_root, dirs, files in os.walk(root):
            current_path = Path(current_root)
            normalize_permissions(current_path)
            for directory in dirs:
                normalize_permissions(current_path / directory)
            for file_name in files:
                normalize_permissions(current_path / file_name)
    else:
        normalize_permissions(root)

print("permission_strategy=target-root-metadata-preserved")
print(f"copied_root_entries={len(copied_roots)}")
PY
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
