#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

MODE="${1:-preflight}"
AMN2_DIR="/opt/amn2"
DB_PATH="$AMN2_DIR/data/amneziya.sqlite3"
OVERLAY_MARKER="$AMN2_DIR/.amn2_source_overlay_commit"
EXPECTED_OVERLAY="801f8c3"
CANDIDATE_COMMIT="0b858c5"
SOURCE_FULL_COMMIT="0b858c5cdbc5b565cc265966a2edfe2d339d65e0"
PACKAGE_NAME="amn2-combined-overlay-0b858c5.zip"
CHECKSUM_NAME="$PACKAGE_NAME.sha256.txt"
PACKAGE_PATH="/root/$PACKAGE_NAME"
CHECKSUM_PATH="/root/$CHECKSUM_NAME"
PACKAGE_SHA="7866BDD9FEBE1D6EEA701B37A6E4206A8267766A56993F3C02A0C7B30C394B54"
SOURCE_SHA="E03F13FD6A7BB5CBC5FCEE7179F395EA8C2864EBCEAB01BC351C5904F3CFF975"
APPLY_SHA="016403379F46BA6024B0570B9EC7E757EC9055297B4B89794B871EE80C706314"
RUNBOOK_SHA="1483870B8C0A1DDAAA5C2B4A69FD2650B970C95BD70654FF54FEAEF602303F8A"
SOURCE_ENTRY_COUNT="383"
CANONICAL_LOGO_SHA="40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791"
LANGUAGE_HEADER_SHA="BBDDFA72D1D1FC37E412D2F4A9B4124001FF91FBD641635E31A47E008FC4611F"
AWG_CONTAINER="amnezia-awg2"
AWG_INTERFACE="awg0"
WEB_UNIT="amneziya-web.service"
BOT_UNIT="amneziya-bot.service"
TRACKED=(.env.example .gitattributes .gitignore README.md app deploy docs pyproject.toml scripts tests)

RUN_ID=""
CANDIDATE_ROOT=""
ROLLBACK_ROOT=""
WEB_STOPPED=0
SOURCE_APPLIED=0
ROLLBACK_ARMED=0

log() {
  printf '[phase11-0b858c5] %s\n' "$*"
}

die() {
  printf '[phase11-0b858c5] ERROR: %s\n' "$*" >&2
  return 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

safe_dir() {
  local path="$1"
  local prefix="$2"
  case "$path" in
    "$prefix"/*) ;;
    *) die "unsafe path outside approved root" ;;
  esac
  [ ! -L "$path" ] || die "symlinked approved path refused"
}

prepare_private_root() {
  local path="$1"
  [ ! -L "$path" ] || die "symlinked private root refused"
  mkdir -p "$path"
  chown root:root "$path"
  chmod 700 "$path"
  [ "$(stat -c '%U:%G:%a' "$path")" = "root:root:700" ] || die "private root metadata mismatch"
}

write_gate_check() {
  "$PYTHON_BIN" - "$AMN2_DIR/.env" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
values = {}
for line in path.read_text(encoding="utf-8", errors="strict").splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        continue
    key, value = stripped.split("=", 1)
    values[key.strip()] = value.strip().strip('"').strip("'")

required = {
    "VPS_APPLY_ENABLED": "false",
    "OPERATOR_DEVICE_CREATE_ENABLED": "false",
}
for key, expected in required.items():
    actual = values.get(key, "false")
    if actual != expected:
        raise SystemExit(f"unsafe write gate: {key}")
print("write_gates=false_false")
PY
}

db_snapshot() {
  "$PYTHON_BIN" - "$DB_PATH" <<'PY'
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

path = Path(sys.argv[1])
file_sha = hashlib.sha256(path.read_bytes()).hexdigest().upper()
conn = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
try:
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    fk = len(conn.execute("PRAGMA foreign_key_check").fetchall())
    tables = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]
    counts = {
        name: int(conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0])
        for name in tables
    }
    logical = hashlib.sha256()
    for statement in conn.iterdump():
        logical.update(statement.encode("utf-8"))
        logical.update(b"\n")
finally:
    conn.close()

counts_blob = json.dumps(counts, sort_keys=True, separators=(",", ":")).encode()
print(f"integrity={integrity}")
print(f"foreign_key_issues={fk}")
print(f"file_sha256={file_sha}")
print(f"logical_sha256={logical.hexdigest().upper()}")
print(f"counts_sha256={hashlib.sha256(counts_blob).hexdigest().upper()}")
print(f"table_count={len(counts)}")
print(f"total_rows={sum(counts.values())}")
if integrity != "ok" or fk:
    raise SystemExit(1)
PY
}

awg_snapshot() {
  local container_id restart_count running peer_data
  container_id="$(docker inspect --format '{{.Id}}' "$AWG_CONTAINER")"
  restart_count="$(docker inspect --format '{{.RestartCount}}' "$AWG_CONTAINER")"
  running="$(docker inspect --format '{{.State.Running}}' "$AWG_CONTAINER")"
  [ "$running" = "true" ] || die "AWG container is not running"
  peer_data="$(docker exec "$AWG_CONTAINER" awg show "$AWG_INTERFACE" dump | "$PYTHON_BIN" -c '
import hashlib
import sys
lines = [line.rstrip("\n") for line in sys.stdin if line.strip()]
peers = sorted(line.split("\t", 1)[0] for line in lines[1:])
payload = "\n".join(peers).encode()
print(f"peer_count={len(peers)}")
print(f"peer_set_sha256={hashlib.sha256(payload).hexdigest().upper()}")
')"
  printf 'container_sha256=%s\n' "$(printf '%s' "$container_id" | sha256sum | awk '{print toupper($1)}')"
  printf 'restart_count=%s\n' "$restart_count"
  printf 'running=true\n'
  printf '%s\n' "$peer_data"
}

bot_unit_env_snapshot() {
  local unit_text fragment_path
  unit_text="$(systemctl cat "$BOT_UNIT")"
  grep -Fq "EnvironmentFile=$AMN2_DIR/.env" <<<"$unit_text" || die "bot EnvironmentFile binding mismatch"
  fragment_path="$(systemctl show "$BOT_UNIT" -p FragmentPath --value)"
  [ -n "$fragment_path" ] && [ -f "$fragment_path" ] || die "bot unit fragment missing"
  [ -f "$AMN2_DIR/.env" ] || die "bot environment file missing"
  printf 'active=%s\n' "$(systemctl is-active "$BOT_UNIT" 2>/dev/null || true)"
  printf 'enabled=%s\n' "$(systemctl is-enabled "$BOT_UNIT" 2>/dev/null || true)"
  printf 'unit_cat_sha256=%s\n' "$(printf '%s' "$unit_text" | sha256sum | awk '{print toupper($1)}')"
  printf 'unit_fragment_sha256=%s\n' "$(sha256sum "$fragment_path" | awk '{print toupper($1)}')"
  printf 'environment_sha256=%s\n' "$(sha256sum "$AMN2_DIR/.env" | awk '{print toupper($1)}')"
}

listener_check() {
  ss -ltn | "$PYTHON_BIN" -c '
import sys
rows = [line.split() for line in sys.stdin if line.strip() and not line.startswith("State")]
locals_ = [row[3] for row in rows if len(row) >= 4]
p3030 = [value for value in locals_ if value.endswith(":3030")]
p3040 = [value for value in locals_ if value.endswith(":3040")]
safe3030 = bool(p3030) and all(value.startswith("127.") or value.startswith("[::1]") for value in p3030)
print(f"listener_3030_rows={len(p3030)}")
print(f"listener_3030_loopback_only={str(safe3030).lower()}")
print(f"listener_3040_rows={len(p3040)}")
if not safe3030 or p3040:
    raise SystemExit(1)
'
}

runtime_check() {
  [ "$(systemctl is-active "$WEB_UNIT")" = "active" ] || die "web not active"
  [ "$(systemctl is-enabled "$WEB_UNIT")" = "enabled" ] || die "web not enabled"
  [ "$(systemctl is-active "$BOT_UNIT" 2>/dev/null || true)" = "inactive" ] || die "bot unexpectedly active"
  [ "$(systemctl is-enabled "$BOT_UNIT" 2>/dev/null || true)" = "disabled" ] || die "bot unexpectedly enabled"
  if pgrep -f 'python.*app\.main|python.*amneziya.*bot' >/dev/null 2>&1; then
    die "bot process detected"
  fi
  local login_code protected_code
  login_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:3030/login)"
  protected_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:3030/users)"
  [ "$login_code" = "200" ] || die "web login HTTP mismatch"
  case "$protected_code" in 302|303|307) ;; *) die "protected route redirect mismatch" ;; esac
  listener_check >/dev/null
  write_gate_check >/dev/null
}

wait_for_web() {
  local attempt
  for attempt in $(seq 1 30); do
    if systemctl is-active --quiet "$WEB_UNIT" \
      && curl -fsS -o /dev/null --max-time 2 http://127.0.0.1:3030/login; then
      return 0
    fi
    sleep 1
  done
  return 1
}

source_manifest() {
  "$PYTHON_BIN" - "$AMN2_DIR" "${TRACKED[@]}" <<'PY'
import hashlib
import os
import sys
from pathlib import Path

root = Path(sys.argv[1])
entries = []
for rel in sys.argv[2:]:
    path = root / rel
    if not path.exists() and not path.is_symlink():
        raise SystemExit(f"missing tracked root: {rel}")
    candidates = [path]
    if path.is_dir() and not path.is_symlink():
        candidates.extend(sorted(path.rglob("*")))
    for candidate in candidates:
        relative_path = candidate.relative_to(root)
        relative = relative_path.as_posix()
        parts = relative_path.parts
        if (
            "__pycache__" in parts
            or ".pytest_cache" in parts
            or any(part.endswith(".egg-info") for part in parts)
            or candidate.suffix in {".pyc", ".pyo"}
        ):
            continue
        if candidate.is_symlink():
            digest = hashlib.sha256(os.readlink(candidate).encode()).hexdigest().upper()
            entries.append(f"L {relative} {digest}")
        elif candidate.is_file():
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest().upper()
            entries.append(f"F {relative} {digest}")
print("\n".join(sorted(entries)))
PY
}

source_contract_check() {
  "$PYTHON_BIN" - "$AMN2_DIR" "$CANONICAL_LOGO_SHA" "$LANGUAGE_HEADER_SHA" <<'PY'
import hashlib
import sys
from pathlib import Path

root = Path(sys.argv[1])
logo_sha = sys.argv[2]
header_sha = sys.argv[3]
bot_logo = root / "app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png"
web_logo = root / "app/web/static/brand-full.png"
header = root / "app/bot/assets/NEOBYATNAYA-AMNZ-LANGUAGE-HEADER.png"
old_jpg = root / "app/web/static/brand-full.jpg"

for path, expected in ((bot_logo, logo_sha), (web_logo, logo_sha), (header, header_sha)):
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest().upper()
    if digest != expected or not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"asset binding mismatch: {path.name}")
if bot_logo.read_bytes() != web_logo.read_bytes():
    raise SystemExit("bot and web logo bytes differ")
if old_jpg.exists():
    raise SystemExit("obsolete web JPG remains")
for name in ("login.html", "dashboard.html"):
    text = (root / "app/web/templates" / name).read_text(encoding="utf-8")
    if "/static/brand-full.png" not in text or "brand-full.jpg" in text:
        raise SystemExit(f"template logo path mismatch: {name}")
pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
if '"app.bot" = ["assets/*.png"]' not in pyproject:
    raise SystemExit("bot package-data binding missing")
assets_py = (root / "app/bot/assets.py").read_text(encoding="utf-8")
if '"NEOBYATNAYA-AMNZ-LANGUAGE-HEADER.png"' not in assets_py:
    raise SystemExit("wide language header binding missing")
print("source_asset_contract=pass")
PY
}

import_check() {
  PYTHONPATH="$AMN2_DIR" "$PYTHON_BIN" - "$AMN2_DIR" <<'PY'
import importlib
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
for name in ("app", "app.bot.assets", "app.bot.persistent_runtime", "app.main"):
    module = importlib.import_module(name)
    path = Path(module.__file__).resolve()
    if root not in path.parents:
        raise SystemExit(f"import escaped source root: {name}")
print("source_imports=pass")
PY
}

served_logo_check() {
  [ "$(curl -fsS --max-time 5 http://127.0.0.1:3030/static/brand-full.png | sha256sum | awk '{print toupper($1)}')" = "$CANONICAL_LOGO_SHA" ] \
    || die "served logo SHA mismatch"
}

extract_and_verify_package() {
  "$PYTHON_BIN" - "$PACKAGE_PATH" "$CANDIDATE_ROOT" "$SOURCE_FULL_COMMIT" "$SOURCE_ENTRY_COUNT" "$SOURCE_SHA" "$CANONICAL_LOGO_SHA" "$LANGUAGE_HEADER_SHA" <<'PY'
import hashlib
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

package = Path(sys.argv[1])
target = Path(sys.argv[2])
full_commit = sys.argv[3]
entry_count = int(sys.argv[4])
source_sha = sys.argv[5]
logo_sha = sys.argv[6]
header_sha = sys.argv[7]
outer_expected = {
    "AMN2_COMBINED_OVERLAY_0b858c5.ru.md",
    "amn2_apply_source_zip.sh",
    "amn2-codex-vps-test-prep-0b858c5-source.zip",
    "amn2-codex-vps-test-prep-0b858c5-source.zip.sha256.txt",
}

def unsafe(info: zipfile.ZipInfo) -> bool:
    path = PurePosixPath(info.filename)
    return path.is_absolute() or ".." in path.parts or "\\" in info.filename

def symlink(info: zipfile.ZipInfo) -> bool:
    return stat.S_ISLNK((info.external_attr >> 16) & 0xFFFF)

with zipfile.ZipFile(package) as archive:
    infos = archive.infolist()
    names = {info.filename for info in infos}
    if names != outer_expected or archive.testzip() is not None:
        raise SystemExit("outer package contract mismatch")
    if any(unsafe(info) or symlink(info) for info in infos):
        raise SystemExit("unsafe outer package entry")
    archive.extractall(target)

source_zip = target / "amn2-codex-vps-test-prep-0b858c5-source.zip"
if hashlib.sha256(source_zip.read_bytes()).hexdigest().upper() != source_sha:
    raise SystemExit("source ZIP SHA mismatch")
receipt = (target / "amn2-codex-vps-test-prep-0b858c5-source.zip.sha256.txt").read_text(encoding="utf-8").split()[0].upper()
if receipt != source_sha:
    raise SystemExit("source checksum receipt mismatch")

with zipfile.ZipFile(source_zip) as source:
    infos = source.infolist()
    names = {info.filename for info in infos}
    if source.comment.decode("ascii") != full_commit:
        raise SystemExit("source archive commit mismatch")
    if len(infos) != entry_count or source.testzip() is not None:
        raise SystemExit("source archive count/integrity mismatch")
    if any(unsafe(info) or symlink(info) for info in infos):
        raise SystemExit("unsafe source archive entry")
    forbidden_exact = {".env", "servers.yml"}
    forbidden_prefixes = ("data/", "venv/", ".git/")
    forbidden_suffixes = (".key", ".pem", ".p12", ".pfx", ".sqlite", ".sqlite3", ".db")
    for name in names:
        lowered = name.lower()
        if name in forbidden_exact or name.startswith(forbidden_prefixes) or lowered.endswith(forbidden_suffixes):
            raise SystemExit(f"forbidden source entry: {name}")
    bot_name = "app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png"
    web_name = "app/web/static/brand-full.png"
    header_name = "app/bot/assets/NEOBYATNAYA-AMNZ-LANGUAGE-HEADER.png"
    if "app/web/static/brand-full.jpg" in names:
        raise SystemExit("obsolete JPG present in source archive")
    bot = source.read(bot_name)
    web = source.read(web_name)
    header = source.read(header_name)
    if hashlib.sha256(bot).hexdigest().upper() != logo_sha or bot != web:
        raise SystemExit("canonical logo archive binding mismatch")
    if hashlib.sha256(header).hexdigest().upper() != header_sha:
        raise SystemExit("wide header archive binding mismatch")
    pyproject = source.read("pyproject.toml").decode("utf-8")
    if '"app.bot" = ["assets/*.png"]' not in pyproject:
        raise SystemExit("archive package-data binding missing")
print("package_contract=pass")
PY
}

verify_source_delta() {
  "$PYTHON_BIN" - "$ROLLBACK_ROOT/source-before.manifest" "$ROLLBACK_ROOT/source-after.manifest" <<'PY'
import sys
from pathlib import Path

def load(path):
    rows = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        kind, name, digest = line.split(" ", 2)
        rows[name] = (kind, digest)
    return rows

before = load(sys.argv[1])
after = load(sys.argv[2])
changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
expected = sorted([
    ".env.example",
    "app/bot/assets.py",
    "app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png",
    "app/bot/assets/NEOBYATNAYA-AMNZ-LANGUAGE-HEADER.png",
    "app/bot/handlers.py",
    "app/bot/persistent_runtime.py",
    "app/config/settings.py",
    "app/main.py",
    "app/systemd_notify.py",
    "app/web/static/brand-full.jpg",
    "app/web/static/brand-full.png",
    "app/web/templates/dashboard.html",
    "app/web/templates/login.html",
    "deploy/runtime/manifest.yml",
    "deploy/systemd/amneziya-bot.service.example",
    "docs/superpowers/plans/2026-07-15-phase11-telegram-002a-persistent-admission-unit-hardening.md",
    "docs/superpowers/plans/2026-07-16-phase11-language-selection-wide-header.en.md",
    "docs/superpowers/plans/2026-07-16-phase11-language-selection-wide-header.ru.md",
    "docs/superpowers/specs/2026-07-15-phase11-telegram-002a-persistent-admission-unit-hardening-design.md",
    "docs/superpowers/specs/2026-07-16-phase11-language-selection-wide-header-design.en.md",
    "docs/superpowers/specs/2026-07-16-phase11-language-selection-wide-header-design.ru.md",
    "pyproject.toml",
    "tests/bot/test_app_bootstrap.py",
    "tests/bot/test_bot_assets.py",
    "tests/bot/test_bot_handlers.py",
    "tests/bot/test_persistent_runtime.py",
    "tests/config/test_settings.py",
    "tests/deploy/test_runtime_registry.py",
    "tests/deploy/test_systemd_templates.py",
    "tests/test_systemd_notify.py",
    "tests/web/test_app.py",
])
if changed != expected:
    raise SystemExit("unexpected source delta: " + ",".join(changed))
print("source_delta_exact=true")
PY
}

preflight() {
  require_cmd docker
  require_cmd systemctl
  require_cmd curl
  require_cmd ss
  require_cmd tar
  require_cmd sha256sum
  require_cmd stat
  [ -d "$AMN2_DIR" ] || die "AMN2 directory missing"
  [ -f "$DB_PATH" ] || die "production database missing"
  [ -f "$OVERLAY_MARKER" ] || die "overlay marker missing"
  local overlay
  overlay="$(tr -d '\r\n' < "$OVERLAY_MARKER")"
  [ "$overlay" = "$EXPECTED_OVERLAY" ] || die "production overlay mismatch"
  PYTHON_BIN="$AMN2_DIR/venv/bin/python"
  [ -x "$PYTHON_BIN" ] || die "production Python missing"
  write_gate_check >/dev/null
  runtime_check
  local db_state awg_state bot_state available_kb
  db_state="$(db_snapshot)"
  awg_state="$(awg_snapshot)"
  bot_state="$(bot_unit_env_snapshot)"
  grep -Fqx 'integrity=ok' <<<"$db_state" || die "database integrity failed"
  grep -Fqx 'foreign_key_issues=0' <<<"$db_state" || die "database foreign keys failed"
  grep -Fqx 'running=true' <<<"$awg_state" || die "AWG not running"
  grep -Fqx 'active=inactive' <<<"$bot_state" || die "bot active state changed"
  grep -Fqx 'enabled=disabled' <<<"$bot_state" || die "bot enable state changed"
  available_kb="$(df -Pk /root | awk 'NR==2 {print $4}')"
  [ "$available_kb" -ge 200000 ] || die "insufficient disk"
  if [ "$EXPECTED_OVERLAY" = "$CANDIDATE_COMMIT" ]; then
    source_contract_check >/dev/null
    import_check >/dev/null
    served_logo_check
  fi
  printf 'preflight=pass\n'
  printf 'overlay=%s\n' "$overlay"
  printf 'web=active_enabled_http_ok_loopback_only\n'
  printf 'bot=inactive_disabled_process_0_unit_env_bound\n'
  printf 'write_gates=false_false\n'
  printf '%s\n' "$db_state"
  printf '%s\n' "$awg_state"
  printf 'disk_required_kb=200000\n'
  printf 'disk_sufficient=true\n'
}

rollback() {
  trap - ERR
  set +e
  local rollback_status="pass"
  log "rollback started"
  if [ "$WEB_STOPPED" = "0" ]; then
    systemctl stop "$WEB_UNIT" >/dev/null 2>&1 || rollback_status="failed"
    WEB_STOPPED=1
  fi
  if [ "$SOURCE_APPLIED" = "1" ] && [ -f "$ROLLBACK_ROOT/source-before.tar.gz" ]; then
    local rel resolved current_db before_db
    for rel in "${TRACKED[@]}"; do
      resolved="$AMN2_DIR/$rel"
      case "$resolved" in "$AMN2_DIR"/*) ;; *) rollback_status="failed"; continue ;; esac
      rm -rf -- "$resolved" || rollback_status="failed"
    done
    tar -xzpf "$ROLLBACK_ROOT/source-before.tar.gz" -C "$AMN2_DIR" || rollback_status="failed"
    if [ -f "$ROLLBACK_ROOT/overlay-before.txt" ]; then
      cp -p "$ROLLBACK_ROOT/overlay-before.txt" "$OVERLAY_MARKER" || rollback_status="failed"
    fi
    current_db="$(db_snapshot 2>/dev/null || true)"
    before_db="$(cat "$ROLLBACK_ROOT/db-before.snapshot" 2>/dev/null || true)"
    if [ -n "$before_db" ] && [ "$current_db" != "$before_db" ] && [ -f "$ROLLBACK_ROOT/db-before.sqlite3" ]; then
      cp -p "$ROLLBACK_ROOT/db-before.sqlite3" "$DB_PATH.rollback-tmp" || rollback_status="failed"
      chown --reference="$DB_PATH" "$DB_PATH.rollback-tmp" 2>/dev/null || true
      chmod --reference="$DB_PATH" "$DB_PATH.rollback-tmp" 2>/dev/null || true
      mv -f "$DB_PATH.rollback-tmp" "$DB_PATH" || rollback_status="failed"
    fi
  fi
  systemctl start "$WEB_UNIT" >/dev/null 2>&1 || rollback_status="failed"
  WEB_STOPPED=0
  wait_for_web >/dev/null 2>&1 || rollback_status="failed"
  runtime_check >/dev/null 2>&1 || rollback_status="failed"
  if [ -f "$ROLLBACK_ROOT/db-before.snapshot" ]; then
    [ "$(db_snapshot 2>/dev/null)" = "$(cat "$ROLLBACK_ROOT/db-before.snapshot")" ] || rollback_status="failed"
  fi
  if [ -f "$ROLLBACK_ROOT/awg-before.snapshot" ]; then
    [ "$(awg_snapshot 2>/dev/null)" = "$(cat "$ROLLBACK_ROOT/awg-before.snapshot")" ] || rollback_status="failed"
  fi
  if [ -f "$ROLLBACK_ROOT/bot-unit-env-before.snapshot" ]; then
    [ "$(bot_unit_env_snapshot 2>/dev/null)" = "$(cat "$ROLLBACK_ROOT/bot-unit-env-before.snapshot")" ] || rollback_status="failed"
  fi
  printf 'rollout=rollback-%s\n' "$rollback_status"
  printf 'rollback_run_id=%s\n' "$RUN_ID"
  exit 1
}

on_error() {
  local code=$?
  if [ "$ROLLBACK_ARMED" = "1" ]; then
    rollback
  fi
  exit "$code"
}

apply_rollout() {
  preflight
  [ -f "$PACKAGE_PATH" ] || die "uploaded package missing"
  [ -f "$CHECKSUM_PATH" ] || die "uploaded checksum missing"
  [ "$(stat -c '%U:%G:%a' "$PACKAGE_PATH")" = "root:root:600" ] || die "package metadata mismatch"
  [ "$(stat -c '%U:%G:%a' "$CHECKSUM_PATH")" = "root:root:600" ] || die "checksum metadata mismatch"
  [ "$(sha256sum "$PACKAGE_PATH" | awk '{print toupper($1)}')" = "$PACKAGE_SHA" ] || die "outer package SHA mismatch"
  [ "$(awk 'NR==1 {print toupper($1)}' "$CHECKSUM_PATH")" = "$PACKAGE_SHA" ] || die "outer checksum receipt mismatch"

  RUN_ID="$(date -u '+%Y%m%dT%H%M%SZ')"
  CANDIDATE_ROOT="/root/amn2-candidates/0b858c5-$RUN_ID"
  ROLLBACK_ROOT="/root/amn2-rollbacks/0b858c5-$RUN_ID"
  safe_dir "$CANDIDATE_ROOT" "/root/amn2-candidates"
  safe_dir "$ROLLBACK_ROOT" "/root/amn2-rollbacks"
  [ ! -e "$CANDIDATE_ROOT" ] || die "candidate path collision"
  [ ! -e "$ROLLBACK_ROOT" ] || die "rollback path collision"
  prepare_private_root /root/amn2-candidates
  prepare_private_root /root/amn2-rollbacks
  mkdir -m 700 "$CANDIDATE_ROOT" "$ROLLBACK_ROOT"

  PYTHON_BIN="$AMN2_DIR/venv/bin/python"
  extract_and_verify_package
  [ "$(sha256sum "$CANDIDATE_ROOT/amn2_apply_source_zip.sh" | awk '{print toupper($1)}')" = "$APPLY_SHA" ] || die "apply helper SHA mismatch"
  [ "$(sha256sum "$CANDIDATE_ROOT/AMN2_COMBINED_OVERLAY_0b858c5.ru.md" | awk '{print toupper($1)}')" = "$RUNBOOK_SHA" ] || die "runbook SHA mismatch"

  ROLLBACK_ARMED=1
  trap on_error ERR
  systemctl stop "$WEB_UNIT"
  WEB_STOPPED=1
  [ "$(systemctl is-active "$WEB_UNIT" 2>/dev/null || true)" != "active" ] || die "web failed to stop"

  awg_snapshot > "$ROLLBACK_ROOT/awg-before.snapshot"
  db_snapshot > "$ROLLBACK_ROOT/db-before.snapshot"
  bot_unit_env_snapshot > "$ROLLBACK_ROOT/bot-unit-env-before.snapshot"
  source_manifest > "$ROLLBACK_ROOT/source-before.manifest"
  tar -czpf "$ROLLBACK_ROOT/source-before.tar.gz" -C "$AMN2_DIR" "${TRACKED[@]}"
  cp -p "$OVERLAY_MARKER" "$ROLLBACK_ROOT/overlay-before.txt"
  "$PYTHON_BIN" - "$DB_PATH" "$ROLLBACK_ROOT/db-before.sqlite3" <<'PY'
import sqlite3
import sys

source = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
target = sqlite3.connect(sys.argv[2])
try:
    source.backup(target)
finally:
    target.close()
    source.close()
PY
  chmod 600 "$ROLLBACK_ROOT"/*
  [ "$(awg_snapshot)" = "$(cat "$ROLLBACK_ROOT/awg-before.snapshot")" ] || die "AWG changed during snapshot"
  [ "$(db_snapshot)" = "$(cat "$ROLLBACK_ROOT/db-before.snapshot")" ] || die "database changed during snapshot"
  [ "$(bot_unit_env_snapshot)" = "$(cat "$ROLLBACK_ROOT/bot-unit-env-before.snapshot")" ] || die "bot unit/env changed during snapshot"

  SOURCE_APPLIED=1
  VPS_APPLY_ENABLED=false \
  OPERATOR_DEVICE_CREATE_ENABLED=false \
  PIP_NO_INDEX=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  AMN2_DIR="$AMN2_DIR" \
  AMN2_SOURCE_ZIP="$CANDIDATE_ROOT/amn2-codex-vps-test-prep-0b858c5-source.zip" \
  AMN2_EXPECTED_SOURCE_SHA="$SOURCE_SHA" \
  AMN2_EXPECTED_SOURCE_COMMIT="$CANDIDATE_COMMIT" \
  AMN2_UPDATE_LOG_DIR="$ROLLBACK_ROOT/apply-log" \
  bash "$CANDIDATE_ROOT/amn2_apply_source_zip.sh" > "$ROLLBACK_ROOT/apply-safe.log" 2>&1
  [ "$(tr -d '\r\n' < "$OVERLAY_MARKER")" = "$CANDIDATE_COMMIT" ] || die "overlay marker mismatch after apply"
  rm -f -- "$AMN2_DIR/app/web/static/brand-full.jpg"
  source_contract_check > "$ROLLBACK_ROOT/source-contract-check.txt"
  import_check > "$ROLLBACK_ROOT/import-check.txt"
  source_manifest > "$ROLLBACK_ROOT/source-after.manifest"
  verify_source_delta
  [ "$(db_snapshot)" = "$(cat "$ROLLBACK_ROOT/db-before.snapshot")" ] || die "production database changed during apply"
  [ "$(awg_snapshot)" = "$(cat "$ROLLBACK_ROOT/awg-before.snapshot")" ] || die "AWG changed during apply"
  [ "$(bot_unit_env_snapshot)" = "$(cat "$ROLLBACK_ROOT/bot-unit-env-before.snapshot")" ] || die "bot unit/env changed during apply"

  systemctl start "$WEB_UNIT"
  WEB_STOPPED=0
  wait_for_web || die "web readiness timeout"
  runtime_check
  source_contract_check >/dev/null
  import_check >/dev/null
  served_logo_check
  [ "$(db_snapshot)" = "$(cat "$ROLLBACK_ROOT/db-before.snapshot")" ] || die "production database changed after web start"
  [ "$(awg_snapshot)" = "$(cat "$ROLLBACK_ROOT/awg-before.snapshot")" ] || die "AWG changed after web start"
  [ "$(bot_unit_env_snapshot)" = "$(cat "$ROLLBACK_ROOT/bot-unit-env-before.snapshot")" ] || die "bot unit/env changed after web start"

  printf 'rollout=pass\n'
  printf 'run_id=%s\n' "$RUN_ID"
  printf 'source_overlay=%s\n' "$CANDIDATE_COMMIT"
  printf 'web=active_enabled_http_ok_loopback_only\n'
  printf 'bot=inactive_disabled_process_0_unit_env_unchanged\n'
  printf 'assets=canonical_square_and_wide_language_header_verified\n'
  printf 'telegram_profile_photo=unchanged\n'
  printf 'database=unchanged_integrity_ok_fk_0\n'
  printf 'awg=running_restart_peer_set_unchanged\n'
  printf 'rollback_bundle=retained_verified\n'

  safe_dir "$CANDIDATE_ROOT" "/root/amn2-candidates"
  rm -rf -- "$CANDIDATE_ROOT"
  rm -f -- "$PACKAGE_PATH" "$CHECKSUM_PATH"
  trap - ERR
  ROLLBACK_ARMED=0
}

case "$MODE" in
  preflight) preflight ;;
  postflight) EXPECTED_OVERLAY="$CANDIDATE_COMMIT"; preflight ;;
  apply) apply_rollout ;;
  *) die "unsupported mode" ;;
esac
