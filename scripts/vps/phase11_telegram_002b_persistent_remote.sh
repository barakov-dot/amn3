#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

MODE="${1:-preflight}"
RUN_ID="${2:-}"
CONFIRMATION_TOKEN="${3:-}"
CONFIRMATION=""

AMN2_DIR="/opt/amn2"
DB_PATH="$AMN2_DIR/data/amneziya.sqlite3"
ENV_PATH="$AMN2_DIR/.env"
OVERLAY_MARKER="$AMN2_DIR/.amn2_source_overlay_commit"
UNIT_SOURCE="$AMN2_DIR/deploy/systemd/amneziya-bot.service.example"
UNIT_FRAGMENT="/etc/systemd/system/amneziya-bot.service"
PYTHON_BIN="$AMN2_DIR/venv/bin/python"
BOT_UNIT="amneziya-bot.service"
WEB_UNIT="amneziya-web.service"
BOT_USER="amneziya"
BOT_GROUP="amneziya"
AWG_CONTAINER="amnezia-awg2"
AWG_INTERFACE="awg0"
STATE_BASE="/root/amn2-telegram-002b"

EXPECTED_OVERLAY="0b858c5"
SOURCE_FULL_COMMIT="0b858c5cdbc5b565cc265966a2edfe2d339d65e0"
EXPECTED_BOT_USERNAME="NeobyatnayaAMNZ_bot"
ENV_EXPECTED_BOT_USERNAME="TELEGRAM_EXPECTED_BOT_USERNAME=NeobyatnayaAMNZ_bot"
ENV_ADMISSION_TIMEOUT="TELEGRAM_ADMISSION_TIMEOUT_SECONDS=30"
ENV_POLLING_TIMEOUT="TELEGRAM_POLLING_TIMEOUT_SECONDS=20"
ENV_RUNTIME_LOCK_PATH="TELEGRAM_RUNTIME_LOCK_PATH=/run/amn2-bot/polling.lock"
UNIT_SOURCE_SHA="E0C6706B030775C9731CF3FC3A055CAE88512CF470BF2D6BFABDACD7F2F5F694"
PERSISTENT_RUNTIME_SHA="F400FE8FDA673CA6976B698365A591CEC3A373C4284721A39AEF935DF16C5A31"
APP_MAIN_SHA="C34A0F457B2242EDE138DD0B6DC1B08B860515F7BD2FADB7DF8F2B86A3F5ED31"
SYSTEMD_NOTIFY_SHA="649EA2EABBD6B18C5E489D2059D08020D64914C47B15E50EA2873AEEFA99A8A3"
SETTINGS_SHA="1DB81553DBCBF4DAFC710EFDD69C2DB0CC1A869F0754D7BB67C7ADFA3DCAC631"
EXPECTED_CONFIRMATION="CONFIRM PHASE11_TELEGRAM_002B_FIRST_ADMIN_WIDE_HEADER_RESPONSE"
ROLLBACK_TTL_SECONDS="240"

STATE_ROOT=""

log() {
  printf '[phase11-telegram-002b] %s\n' "$*"
}

die() {
  printf '[phase11-telegram-002b] ERROR: %s\n' "$*" >&2
  return 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

sha256_upper() {
  sha256sum "$1" | awk '{print toupper($1)}'
}

validate_run_id() {
  [[ "$RUN_ID" =~ ^[0-9]{8}T[0-9]{6}Z$ ]] || die "unsafe run id"
}

decode_confirmation() {
  require_cmd base64
  [[ "$CONFIRMATION_TOKEN" =~ ^[A-Za-z0-9+/=]+$ ]] \
    || die "unsafe confirmation token"
  local decoded canonical
  decoded="$(printf '%s' "$CONFIRMATION_TOKEN" | base64 --decode 2>/dev/null)" \
    || die "confirmation token decode failed"
  canonical="$(printf '%s' "$decoded" | base64 | tr -d '\r\n')" \
    || die "confirmation token canonicalization failed"
  [ "$canonical" = "$CONFIRMATION_TOKEN" ] \
    || die "non-canonical confirmation token"
  CONFIRMATION="$decoded"
}

safe_state_root() {
  local path="$1"
  case "$path" in
    "$STATE_BASE"/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]T[0-9][0-9][0-9][0-9][0-9][0-9]Z) ;;
    *) die "unsafe state root" ;;
  esac
  [ ! -L "$path" ] || die "symlinked state root refused"
}

prepare_state_base() {
  [ ! -L "$STATE_BASE" ] || die "symlinked state base refused"
  mkdir -p "$STATE_BASE"
  chown root:root "$STATE_BASE"
  chmod 700 "$STATE_BASE"
  [ "$(stat -c '%U:%G:%a' "$STATE_BASE")" = "root:root:700" ] \
    || die "state base metadata mismatch"
}

require_regular_file() {
  local path="$1"
  [ -f "$path" ] && [ ! -L "$path" ] || die "required regular file missing"
}

require_executable_file() {
  local path="$1" resolved
  [ -e "$path" ] || die "required executable missing"
  resolved="$(readlink -f -- "$path" 2>/dev/null)" \
    || die "required executable target unresolved"
  [ -f "$resolved" ] && [ -x "$resolved" ] \
    || die "required executable target invalid"
}

source_contract_check() {
  require_regular_file "$OVERLAY_MARKER"
  [ "$(tr -d '\r\n' < "$OVERLAY_MARKER")" = "$EXPECTED_OVERLAY" ] \
    || die "production overlay mismatch"

  require_regular_file "$UNIT_SOURCE"
  require_regular_file "$AMN2_DIR/app/bot/persistent_runtime.py"
  require_regular_file "$AMN2_DIR/app/main.py"
  require_regular_file "$AMN2_DIR/app/systemd_notify.py"
  require_regular_file "$AMN2_DIR/app/config/settings.py"

  [ "$(sha256_upper "$UNIT_SOURCE")" = "$UNIT_SOURCE_SHA" ] \
    || die "unit source SHA mismatch"
  [ "$(sha256_upper "$AMN2_DIR/app/bot/persistent_runtime.py")" = "$PERSISTENT_RUNTIME_SHA" ] \
    || die "persistent runtime SHA mismatch"
  [ "$(sha256_upper "$AMN2_DIR/app/main.py")" = "$APP_MAIN_SHA" ] \
    || die "app main SHA mismatch"
  [ "$(sha256_upper "$AMN2_DIR/app/systemd_notify.py")" = "$SYSTEMD_NOTIFY_SHA" ] \
    || die "systemd notifier SHA mismatch"
  [ "$(sha256_upper "$AMN2_DIR/app/config/settings.py")" = "$SETTINGS_SHA" ] \
    || die "settings SHA mismatch"

  printf 'source_overlay=%s\n' "$EXPECTED_OVERLAY"
  printf 'source_commit=%s\n' "$SOURCE_FULL_COMMIT"
  printf 'source_contract=pass\n'
}

write_gate_check() {
  "$PYTHON_BIN" - "$ENV_PATH" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
values: dict[str, str] = {}
for line in path.read_text(encoding="utf-8", errors="strict").splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        continue
    key, value = stripped.split("=", 1)
    key = key.strip()
    if key in values:
        raise SystemExit("duplicate environment key")
    values[key] = value.strip().strip('"').strip("'")

required = {
    "VPS_APPLY_ENABLED": "false",
    "OPERATOR_DEVICE_CREATE_ENABLED": "false",
}
for key, expected in required.items():
    if values.get(key, "false") != expected:
        raise SystemExit(f"unsafe write gate: {key}")
print("write_gates=false_false")
PY
}

listener_check() {
  ss -ltn | "$PYTHON_BIN" -c '
import sys
rows = [line.split() for line in sys.stdin if line.strip() and not line.startswith("State")]
local_addresses = [row[3] for row in rows if len(row) >= 4]
p3030 = [value for value in local_addresses if value.endswith(":3030")]
p3040 = [value for value in local_addresses if value.endswith(":3040")]
safe3030 = bool(p3030) and all(value.startswith("127.") or value.startswith("[::1]") for value in p3030)
if not safe3030 or p3040:
    raise SystemExit(1)
print("listeners=loopback_web_only")
'
}

web_check() {
  [ "$(systemctl is-active "$WEB_UNIT")" = "active" ] || die "web is not active"
  [ "$(systemctl is-enabled "$WEB_UNIT")" = "enabled" ] || die "web is not enabled"
  local login_code protected_code
  login_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:3030/login)"
  protected_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:3030/users)"
  [ "$login_code" = "200" ] || die "web login health mismatch"
  case "$protected_code" in 302|303|307) ;; *) die "protected web route mismatch" ;; esac
  listener_check >/dev/null
  printf 'web=active_enabled_http_ok_loopback_only\n'
}

bot_inactive_disabled_check() {
  [ "$(systemctl is-active "$BOT_UNIT" 2>/dev/null || true)" = "inactive" ] \
    || die "bot is not inactive"
  [ "$(systemctl is-enabled "$BOT_UNIT" 2>/dev/null || true)" = "disabled" ] \
    || die "bot is not disabled"
  if pgrep -f 'python.*app\.main|python.*amneziya.*bot' >/dev/null 2>&1; then
    die "bot process detected"
  fi
  printf 'bot=inactive_disabled_process_0\n'
}

bot_health_check() {
  local expected_enabled="$1"
  [ "$(systemctl is-active "$BOT_UNIT" 2>/dev/null || true)" = "active" ] \
    || die "bot is not active"
  [ "$(systemctl is-enabled "$BOT_UNIT" 2>/dev/null || true)" = "$expected_enabled" ] \
    || die "bot enablement mismatch"
  [ "$(systemctl show "$BOT_UNIT" -p ActiveState --value)" = "active" ] \
    || die "bot ActiveState mismatch"
  [ "$(systemctl show "$BOT_UNIT" -p SubState --value)" = "running" ] \
    || die "bot SubState mismatch"
  [ "$(systemctl show "$BOT_UNIT" -p Type --value)" = "notify" ] \
    || die "bot Type mismatch"
  [ "$(systemctl show "$BOT_UNIT" -p NRestarts --value)" = "0" ] \
    || die "bot restart detected"

  local main_pid control_group pid_count
  main_pid="$(systemctl show "$BOT_UNIT" -p MainPID --value)"
  [[ "$main_pid" =~ ^[1-9][0-9]*$ ]] || die "bot MainPID missing"
  control_group="$(systemctl show "$BOT_UNIT" -p ControlGroup --value)"
  [ -n "$control_group" ] && [ -f "/sys/fs/cgroup${control_group}/cgroup.procs" ] \
    || die "bot cgroup missing"
  pid_count="$(sort -u "/sys/fs/cgroup${control_group}/cgroup.procs" | wc -l | tr -d ' ')"
  [ "$pid_count" = "1" ] || die "bot cgroup is not single-process"
  printf 'bot_process=single\n'
}

wait_for_bot_ready() {
  local attempt watchdog_timestamp
  for attempt in $(seq 1 75); do
    if systemctl is-active --quiet "$BOT_UNIT" \
      && [ "$(systemctl show "$BOT_UNIT" -p SubState --value)" = "running" ] \
      && [ "$(systemctl show "$BOT_UNIT" -p NRestarts --value)" = "0" ]; then
      watchdog_timestamp="$(systemctl show "$BOT_UNIT" -p WatchdogTimestampMonotonic --value)"
      if [[ "$watchdog_timestamp" =~ ^[1-9][0-9]*$ ]]; then
        return 0
      fi
    fi
    sleep 1
  done
  return 1
}

db_snapshot() {
  "$PYTHON_BIN" - "$DB_PATH" <<'PY'
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

path = Path(sys.argv[1])
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
finally:
    conn.close()

counts_blob = json.dumps(counts, sort_keys=True, separators=(",", ":")).encode()
print(f"integrity={integrity}")
print(f"foreign_key_issues={fk}")
print(f"counts_sha256={hashlib.sha256(counts_blob).hexdigest().upper()}")
print(f"table_count={len(counts)}")
print(f"total_rows={sum(counts.values())}")
if integrity != "ok" or fk:
    raise SystemExit(1)
PY
}

write_db_application_snapshot() {
  local destination="$1"
  "$PYTHON_BIN" - "$DB_PATH" "$ENV_PATH" "$destination" <<'PY'
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

db_path = Path(sys.argv[1])
env_path = Path(sys.argv[2])
destination = Path(sys.argv[3])

values: dict[str, str] = {}
for line in env_path.read_text(encoding="utf-8", errors="strict").splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        continue
    key, value = stripped.split("=", 1)
    key = key.strip()
    if key in values:
        raise SystemExit("duplicate environment key")
    values[key] = value.strip().strip('"').strip("'")

raw_admins = values.get("ADMIN_TELEGRAM_IDS", "")
parts = [part.strip() for part in raw_admins.replace(";", ",").split(",") if part.strip()]
if not parts or not parts[0].isdigit():
    raise SystemExit("first configured administrator is unavailable")
first_admin = int(parts[0])

conn = sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
try:
    tables = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]
    all_rows: dict[str, list[dict[str, object]]] = {}
    excluding_rows: dict[str, list[dict[str, object]]] = {}
    counts: dict[str, int] = {}
    first_admin_row = None
    for table in tables:
        columns = [row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')]
        rows = [dict(row) for row in conn.execute(f'SELECT * FROM "{table}"')]
        rows.sort(key=lambda row: json.dumps(row, sort_keys=True, default=str))
        all_rows[table] = rows
        counts[table] = len(rows)
        if table == "users" and "telegram_id" in columns:
            selected = [row for row in rows if int(row["telegram_id"]) == first_admin]
            if len(selected) != 1:
                raise SystemExit("first configured administrator row mismatch")
            first_admin_row = selected[0]
            excluding_rows[table] = [
                row for row in rows if int(row["telegram_id"]) != first_admin
            ]
        else:
            excluding_rows[table] = rows
finally:
    conn.close()

def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()

payload = {
    "first_admin_telegram_id": first_admin,
    "counts": counts,
    "all_rows_sha256": hashlib.sha256(canonical(all_rows)).hexdigest().upper(),
    "application_rows_excluding_first_admin_sha256": hashlib.sha256(
        canonical(excluding_rows)
    ).hexdigest().upper(),
    "first_admin_user_row": first_admin_row,
    "first_admin_user_row_sha256": hashlib.sha256(
        canonical(first_admin_row)
    ).hexdigest().upper(),
    "first_admin_immutable_fields": [
        key
        for key in first_admin_row
        if key not in {"username", "first_name", "last_name", "updated_at"}
    ],
}
destination.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
PY
  chmod 600 "$destination"
}

verify_no_application_delta() {
  local state_root="$1" current
  current="$state_root/db-current.application.json"
  write_db_application_snapshot "$current"
  "$PYTHON_BIN" - "$state_root/db-before.application.json" "$current" <<'PY'
import json
import sys
from pathlib import Path

before = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
current = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
if before["all_rows_sha256"] != current["all_rows_sha256"] or before["counts"] != current["counts"]:
    raise SystemExit("application database changed before acceptance")
print("application_database_pre_acceptance=unchanged")
PY
}

verify_first_admin_delta() {
  local state_root="$1" current
  current="$state_root/db-after.application.json"
  write_db_application_snapshot "$current"
  "$PYTHON_BIN" - "$state_root/db-before.application.json" "$current" <<'PY'
import json
import sys
from pathlib import Path

before = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
after = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
if before["counts"] != after["counts"]:
    raise SystemExit("application table counts changed")
if before["application_rows_excluding_first_admin_sha256"] != after["application_rows_excluding_first_admin_sha256"]:
    raise SystemExit("application rows outside first administrator changed")
if before["first_admin_user_row_sha256"] == after["first_admin_user_row_sha256"]:
    raise SystemExit("first administrator acceptance row did not change")
if before["first_admin_telegram_id"] != after["first_admin_telegram_id"]:
    raise SystemExit("first administrator identity changed")
if before["first_admin_immutable_fields"] != after["first_admin_immutable_fields"]:
    raise SystemExit("first administrator schema contract changed")
for key in before["first_admin_immutable_fields"]:
    if before["first_admin_user_row"].get(key) != after["first_admin_user_row"].get(key):
        raise SystemExit("first administrator immutable field changed")
print("database_delta=first_admin_user_row_only")
PY
}

create_db_backup() {
  local destination="$1"
  "$PYTHON_BIN" - "$DB_PATH" "$destination" <<'PY'
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
  chmod 600 "$destination"
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
print(f"peer_count={len(peers)}")
print(f"peer_set_sha256={hashlib.sha256(chr(10).join(peers).encode()).hexdigest().upper()}")
')"
  printf 'container_sha256=%s\n' "$(printf '%s' "$container_id" | sha256sum | awk '{print toupper($1)}')"
  printf 'restart_count=%s\n' "$restart_count"
  printf 'running=true\n'
  printf '%s\n' "$peer_data"
}

telegram_preflight() {
  PYTHONPATH="$AMN2_DIR" "$PYTHON_BIN" - "$ENV_PATH" "$EXPECTED_BOT_USERNAME" "$BOT_USER" <<'PY'
import asyncio
import os
import pwd
import sys

from app.bot.persistent_runtime import (
    PersistentBotAdmissionConfig,
    admit_persistent_bot,
)
from app.config import Settings
from app.main import create_bot

env_path, expected_username, service_user = sys.argv[1:]

async def main() -> None:
    bot = None
    try:
        os.environ.clear()
        settings = Settings(_env_file=env_path)
        account = pwd.getpwnam(service_user)
        os.initgroups(account.pw_name, account.pw_gid)
        os.setgid(account.pw_gid)
        os.setuid(account.pw_uid)
        bot = create_bot(
            telegram_bot_token=settings.telegram_bot_token,
            telegram_proxy_url=settings.telegram_proxy_url,
        )
        result = await admit_persistent_bot(
            bot,
            PersistentBotAdmissionConfig(
                expected_bot_username=expected_username,
                timeout_seconds=30,
            ),
        )
        if result.pending_update_count != 0:
            raise RuntimeError("unexpected pending update count")
    except Exception:
        raise SystemExit("telegram_preflight=failed") from None
    finally:
        if bot is not None:
            try:
                await bot.session.close()
            except Exception:
                raise SystemExit("telegram_preflight=failed") from None
    print("telegram_preflight=pass")
    print("identity_match=true")
    print("webhook_configured=false")
    print("pending_update_count=0")
    print("ownership_probe=empty")

asyncio.run(main())
PY
}

telegram_postflight() {
  PYTHONPATH="$AMN2_DIR" "$PYTHON_BIN" - "$ENV_PATH" "$EXPECTED_BOT_USERNAME" "$BOT_USER" <<'PY'
import asyncio
import os
import pwd
import sys

from app.config import Settings
from app.main import create_bot

env_path, expected_username, service_user = sys.argv[1:]

async def main() -> None:
    bot = None
    try:
        os.environ.clear()
        settings = Settings(_env_file=env_path)
        account = pwd.getpwnam(service_user)
        os.initgroups(account.pw_name, account.pw_gid)
        os.setgid(account.pw_gid)
        os.setuid(account.pw_uid)
        bot = create_bot(
            telegram_bot_token=settings.telegram_bot_token,
            telegram_proxy_url=settings.telegram_proxy_url,
        )
        me = await bot.get_me()
        webhook = await bot.get_webhook_info()
        actual = str(getattr(me, "username", "") or "").strip()
        if actual.casefold() != expected_username.casefold():
            raise RuntimeError("identity mismatch")
        if str(getattr(webhook, "url", "") or "").strip():
            raise RuntimeError("webhook configured")
        pending = getattr(webhook, "pending_update_count", None)
        if isinstance(pending, bool) or int(pending) != 0:
            raise RuntimeError("pending update mismatch")
    except Exception:
        raise SystemExit("telegram_postflight=failed") from None
    finally:
        if bot is not None:
            try:
                await bot.session.close()
            except Exception:
                raise SystemExit("telegram_postflight=failed") from None
    print("telegram_postflight=pass")
    print("identity_match=true")
    print("webhook_configured=false")
    print("pending_update_count=0")

asyncio.run(main())
PY
}

env_contract_check() {
  "$PYTHON_BIN" - "$ENV_PATH" <<'PY'
import sys
from pathlib import Path

expected = {
    "TELEGRAM_EXPECTED_BOT_USERNAME": "NeobyatnayaAMNZ_bot",
    "TELEGRAM_ADMISSION_TIMEOUT_SECONDS": "30",
    "TELEGRAM_POLLING_TIMEOUT_SECONDS": "20",
    "TELEGRAM_RUNTIME_LOCK_PATH": "/run/amn2-bot/polling.lock",
}
values: dict[str, str] = {}
for line in Path(sys.argv[1]).read_text(encoding="utf-8", errors="strict").splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        continue
    key, value = stripped.split("=", 1)
    key = key.strip()
    if key in values:
        raise SystemExit("duplicate environment key")
    values[key] = value.strip().strip('"').strip("'")
for key, value in expected.items():
    if values.get(key) != value:
        raise SystemExit(f"persistent environment mismatch: {key}")
print("persistent_environment=exact")
PY
}

update_env_contract() {
  "$PYTHON_BIN" - "$ENV_PATH" <<'PY'
import os
import stat
import sys
from pathlib import Path

path = Path(sys.argv[1])
expected = {
    "TELEGRAM_EXPECTED_BOT_USERNAME": "NeobyatnayaAMNZ_bot",
    "TELEGRAM_ADMISSION_TIMEOUT_SECONDS": "30",
    "TELEGRAM_POLLING_TIMEOUT_SECONDS": "20",
    "TELEGRAM_RUNTIME_LOCK_PATH": "/run/amn2-bot/polling.lock",
}
metadata = path.stat()
lines = path.read_text(encoding="utf-8", errors="strict").splitlines()
seen: set[str] = set()
output: list[str] = []
for line in lines:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        output.append(line)
        continue
    key, _ = stripped.split("=", 1)
    key = key.strip()
    if key in seen:
        raise SystemExit("duplicate environment key")
    seen.add(key)
    output.append(f"{key}={expected[key]}" if key in expected else line)
for key, value in expected.items():
    if key not in seen:
        output.append(f"{key}={value}")

temporary = path.with_name(f".{path.name}.phase11-telegram-002b.tmp")
if temporary.exists() or temporary.is_symlink():
    raise SystemExit("environment temporary path already exists")
fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, stat.S_IMODE(metadata.st_mode))
try:
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(output) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.chown(temporary, metadata.st_uid, metadata.st_gid)
    os.chmod(temporary, stat.S_IMODE(metadata.st_mode))
    os.replace(temporary, path)
finally:
    if temporary.exists():
        temporary.unlink()
PY
}

unit_contract_check() {
  require_regular_file "$UNIT_FRAGMENT"
  [ "$(sha256_upper "$UNIT_FRAGMENT")" = "$UNIT_SOURCE_SHA" ] \
    || die "installed bot unit SHA mismatch"
  local unit_text
  unit_text="$(systemctl cat "$BOT_UNIT")"
  grep -Fq 'Type=notify' <<<"$unit_text" || die "bot unit notify contract missing"
  grep -Fq 'WatchdogSec=60s' <<<"$unit_text" || die "bot watchdog contract missing"
  grep -Fq 'ProtectSystem=strict' <<<"$unit_text" || die "bot filesystem sandbox missing"
  grep -Fq 'ProtectHome=true' <<<"$unit_text" || die "bot home sandbox missing"
  grep -Fq "EnvironmentFile=$ENV_PATH" <<<"$unit_text" || die "bot env binding mismatch"
  printf 'installed_unit=exact_hardened\n'
}

rollback_timer_base() {
  printf 'phase11-telegram-002b-rollback-%s' "$RUN_ID"
}

write_rollback_helper() {
  local state_root="$1" fragment_path env_uid env_gid env_mode helper
  fragment_path="$(cat "$state_root/unit-fragment-path.txt")"
  env_uid="$(cat "$state_root/env-uid.txt")"
  env_gid="$(cat "$state_root/env-gid.txt")"
  env_mode="$(cat "$state_root/env-mode.txt")"
  helper="$state_root/rollback.sh"
  cat > "$helper" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
STATE_ROOT="$state_root"
BOT_UNIT="$BOT_UNIT"
UNIT_FRAGMENT="$fragment_path"
ENV_PATH="$ENV_PATH"
ENV_UID="$env_uid"
ENV_GID="$env_gid"
ENV_MODE="$env_mode"
systemctl stop "\$BOT_UNIT" || true
systemctl disable "\$BOT_UNIT" || true
install -o root -g root -m 0644 "\$STATE_ROOT/unit.before" "\$UNIT_FRAGMENT"
install -o "\$ENV_UID" -g "\$ENV_GID" -m "\$ENV_MODE" "\$STATE_ROOT/env.before" "\$ENV_PATH"
systemctl daemon-reload
[ "\$(systemctl is-active "\$BOT_UNIT" 2>/dev/null || true)" = "inactive" ]
[ "\$(systemctl is-enabled "\$BOT_UNIT" 2>/dev/null || true)" = "disabled" ]
printf 'rollback=pass\n' > "\$STATE_ROOT/rollback.receipt"
chmod 600 "\$STATE_ROOT/rollback.receipt"
EOF
  chmod 700 "$STATE_ROOT/rollback.sh"
  chown root:root "$STATE_ROOT/rollback.sh"
}

arm_automatic_rollback() {
  local state_root="$1" timer_base
  timer_base="$(rollback_timer_base)"
  systemd-run --quiet \
    --unit="$timer_base" \
    --on-active="${ROLLBACK_TTL_SECONDS}s" \
    /bin/bash "$state_root/rollback.sh"
  printf '%s.timer\n' "$timer_base" > "$state_root/rollback-timer-unit.txt"
  printf 'rollback_timer_unit=%s.timer\n' "$timer_base"
}

rollback_current_runtime() {
  local timer_base
  [ -n "${STATE_ROOT:-}" ] && [ -x "$STATE_ROOT/rollback.sh" ] \
    || return 1
  /bin/bash "$STATE_ROOT/rollback.sh" || return 1
  timer_base="$(rollback_timer_base)"
  systemctl stop "${timer_base}.timer" >/dev/null 2>&1 || true
  systemctl reset-failed "${timer_base}.timer" "${timer_base}.service" \
    >/dev/null 2>&1 || true
}

rollback_and_exit() {
  local exit_code="$1"
  rollback_current_runtime || true
  trap - ERR HUP INT TERM
  exit "$exit_code"
}

cancel_automatic_rollback() {
  local state_root="$1" timer_unit service_unit receipt service_state
  receipt="$state_root/rollback.receipt"
  [ ! -e "$receipt" ] || die "automatic rollback already completed"
  timer_unit="$(cat "$state_root/rollback-timer-unit.txt")"
  [[ "$timer_unit" =~ ^phase11-telegram-002b-rollback-[0-9]{8}T[0-9]{6}Z\.timer$ ]] \
    || die "unsafe rollback timer unit"
  service_unit="${timer_unit%.timer}.service"
  [ "$(systemctl is-active "$timer_unit" 2>/dev/null || true)" = "active" ] \
    || die "automatic rollback timer is not armed"
  systemctl stop "$timer_unit"
  service_state="$(systemctl is-active "$service_unit" 2>/dev/null || true)"
  case "$service_state" in
    inactive|dead) ;;
    *) die "automatic rollback is already running" ;;
  esac
  [ "$(systemctl is-failed "$service_unit" 2>/dev/null || true)" != "failed" ] \
    || die "automatic rollback failed"
  [ ! -e "$receipt" ] || die "automatic rollback completed during acceptance"
  systemctl reset-failed "$timer_unit" "$service_unit" >/dev/null 2>&1 || true
  [ ! -e "$receipt" ] || die "automatic rollback completed during cancellation"
  printf 'automatic_rollback=cancelled_after_acceptance\n'
}

snapshot_runtime_inputs() {
  local state_root="$1" fragment_path
  fragment_path="$(systemctl show "$BOT_UNIT" -p FragmentPath --value)"
  [ "$fragment_path" = "$UNIT_FRAGMENT" ] \
    || die "bot unit fragment path mismatch"
  require_regular_file "$fragment_path"
  require_regular_file "$ENV_PATH"
  cp -p "$fragment_path" "$state_root/unit.before"
  cp -p "$ENV_PATH" "$state_root/env.before"
  printf '%s\n' "$fragment_path" > "$state_root/unit-fragment-path.txt"
  stat -c '%u' "$ENV_PATH" > "$state_root/env-uid.txt"
  stat -c '%g' "$ENV_PATH" > "$state_root/env-gid.txt"
  stat -c '%a' "$ENV_PATH" > "$state_root/env-mode.txt"
  printf '%s\n' "$(sha256_upper "$fragment_path")" > "$state_root/unit-before.sha256"
  printf '%s\n' "$(sha256_upper "$ENV_PATH")" > "$state_root/env-before.sha256"
  create_db_backup "$state_root/db-before.sqlite3"
  db_snapshot > "$state_root/db-before.snapshot"
  write_db_application_snapshot "$state_root/db-before.application.json"
  awg_snapshot > "$state_root/awg-before.snapshot"
  web_check > "$state_root/web-before.snapshot"
  source_contract_check > "$state_root/source-before.snapshot"
  chmod 600 "$state_root"/*
}

install_runtime_contract() {
  update_env_contract
  env_contract_check >/dev/null
  install -o root -g root -m 0644 "$UNIT_SOURCE" "$UNIT_FRAGMENT"
  systemctl daemon-reload
  unit_contract_check >/dev/null
  [ "$(systemctl is-enabled "$BOT_UNIT" 2>/dev/null || true)" = "disabled" ] \
    || die "bot must remain disabled before stage start"
}

journal_contract_check() {
  local state_root="$1" since_epoch safe_log attempt receipt_ready expected_receipt
  since_epoch="$(cat "$state_root/stage-epoch.txt")"
  safe_log="$state_root/journal-safe.snapshot"
  expected_receipt="telegram_persistent_admission=pass bot_identity=@${EXPECTED_BOT_USERNAME} webhook_configured=false pending_update_count=0 allowed_updates=message,callback_query"
  receipt_ready=0
  for attempt in $(seq 1 15); do
    journalctl -u "$BOT_UNIT" --since "@${since_epoch}" -o cat --no-pager \
      | grep -Fx -- "$expected_receipt" \
      > "$safe_log" || true
    if [ "$(grep -Fxc -- "$expected_receipt" "$safe_log" || true)" = "1" ]; then
      receipt_ready=1
      break
    fi
    sleep 1
  done
  [ "$receipt_ready" = "1" ] || die "sanitized admission receipt missing"
  [ "$(grep -Fxc -- "$expected_receipt" "$safe_log")" = "1" ] \
    || die "admission receipt count mismatch"
  if journalctl -u "$BOT_UNIT" --since "@${since_epoch}" -o cat --no-pager \
    | grep -Eiq 'traceback|telegram.*conflict|unhandled error|api\.telegram\.org/bot[0-9]'; then
    die "bot journal contains a fail-closed error marker"
  fi
  chmod 600 "$safe_log"
  printf 'admission_receipt=single_sanitized\n'
}

preflight() {
  require_cmd systemctl
  require_cmd journalctl
  require_cmd systemd-run
  require_cmd sha256sum
  require_cmd docker
  require_cmd curl
  require_cmd ss
  require_cmd readlink
  require_executable_file "$PYTHON_BIN"
  id "$BOT_USER" >/dev/null 2>&1 || die "bot service user missing"
  getent group "$BOT_GROUP" >/dev/null 2>&1 || die "bot service group missing"
  source_contract_check
  require_regular_file "$ENV_PATH"
  write_gate_check
  web_check
  bot_inactive_disabled_check
  db_snapshot
  awg_snapshot
  telegram_preflight
  local available_kb required_kb
  available_kb="$(df -Pk "$AMN2_DIR" | awk 'NR==2 {print $4}')"
  required_kb="$(( $(du -sk "$AMN2_DIR" | awk '{print $1}') + 65536 ))"
  [ "$available_kb" -ge "$required_kb" ] || die "insufficient rollback disk space"
  printf 'disk_sufficient=true\n'
  printf 'preflight=pass\n'
}

stage_activation() {
  preflight >/dev/null
  RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
  validate_run_id
  prepare_state_base
  STATE_ROOT="$STATE_BASE/$RUN_ID"
  safe_state_root "$STATE_ROOT"
  [ ! -e "$STATE_ROOT" ] || die "activation state already exists"
  mkdir "$STATE_ROOT"
  chown root:root "$STATE_ROOT"
  chmod 700 "$STATE_ROOT"
  snapshot_runtime_inputs "$STATE_ROOT"
  write_rollback_helper "$STATE_ROOT"

  date +%s > "$STATE_ROOT/stage-epoch.txt"
  printf 'staging\n' > "$STATE_ROOT/state.status"
  chmod 600 "$STATE_ROOT/stage-epoch.txt" "$STATE_ROOT/state.status"

  trap 'rollback_and_exit 1' ERR
  trap 'rollback_and_exit 129' HUP
  trap 'rollback_and_exit 130' INT
  trap 'rollback_and_exit 143' TERM
  arm_automatic_rollback "$STATE_ROOT" >/dev/null
  install_runtime_contract
  [ "$(systemctl is-enabled "$BOT_UNIT" 2>/dev/null || true)" = "disabled" ] \
    || die "bot enablement changed before start"
  systemctl start "$BOT_UNIT"
  wait_for_bot_ready || die "bot readiness/watchdog timeout"
  bot_health_check disabled >/dev/null
  journal_contract_check "$STATE_ROOT" >/dev/null
  verify_no_application_delta "$STATE_ROOT" >/dev/null
  [ "$(awg_snapshot)" = "$(cat "$STATE_ROOT/awg-before.snapshot")" ] \
    || die "AWG changed during stage"
  web_check >/dev/null
  db_snapshot >/dev/null
  printf 'staged\n' > "$STATE_ROOT/state.status"
  chmod 600 "$STATE_ROOT/state.status"
  trap - ERR HUP INT TERM

  printf 'stage=pass\n'
  printf 'run_id=%s\n' "$RUN_ID"
  printf 'bot=active_disabled\n'
  printf 'rollback_timer_unit=%s.timer\n' "$(rollback_timer_base)"
  printf 'awaiting_admin_start=true\n'
  printf 'acceptance_deadline_seconds=%s\n' "$ROLLBACK_TTL_SECONDS"
  printf 'web=active_enabled_http_ok_loopback_only\n'
  printf 'database_pre_acceptance=unchanged_integrity_ok_fk_0\n'
  printf 'awg=unchanged\n'
}

accept_activation() {
  validate_run_id
  decode_confirmation
  [ "$CONFIRMATION" = "$EXPECTED_CONFIRMATION" ] || die "exact wide-header confirmation mismatch"
  prepare_state_base
  STATE_ROOT="$STATE_BASE/$RUN_ID"
  safe_state_root "$STATE_ROOT"
  [ -d "$STATE_ROOT" ] && [ ! -L "$STATE_ROOT" ] || die "activation state missing"
  [ "$(cat "$STATE_ROOT/state.status")" = "staged" ] || die "activation state is not staged"
  [ "$(systemctl is-enabled "$BOT_UNIT" 2>/dev/null || true)" = "disabled" ] \
    || die "bot was enabled before acceptance"
  bot_health_check disabled >/dev/null
  unit_contract_check >/dev/null
  env_contract_check >/dev/null
  verify_first_admin_delta "$STATE_ROOT" >/dev/null
  journal_contract_check "$STATE_ROOT" >/dev/null
  db_snapshot > "$STATE_ROOT/db-after.snapshot"
  [ "$(awg_snapshot)" = "$(cat "$STATE_ROOT/awg-before.snapshot")" ] \
    || die "AWG changed before acceptance"
  web_check >/dev/null
  trap 'rollback_and_exit 1' ERR
  trap 'rollback_and_exit 129' HUP
  trap 'rollback_and_exit 130' INT
  trap 'rollback_and_exit 143' TERM
  cancel_automatic_rollback "$STATE_ROOT" >/dev/null
  unit_contract_check >/dev/null
  env_contract_check >/dev/null
  bot_health_check disabled >/dev/null
  systemctl enable "$BOT_UNIT" >/dev/null
  bot_health_check enabled >/dev/null
  printf 'accepted\n' > "$STATE_ROOT/state.status"
  printf '%s\n' "$RUN_ID" > "$STATE_BASE/current-accepted-run-id.txt"
  chmod 600 "$STATE_ROOT/state.status" "$STATE_BASE/current-accepted-run-id.txt"
  trap - ERR HUP INT TERM

  printf 'activation=pass\n'
  printf 'run_id=%s\n' "$RUN_ID"
  printf 'bot=active_enabled_single_instance\n'
  printf 'first_admin_start=accepted\n'
  printf 'wide_header_confirmation=exact\n'
  printf 'watchdog=healthy\n'
  printf 'database_delta=first_admin_user_row_only\n'
  printf 'web=active_enabled_http_ok_loopback_only\n'
  printf 'awg=unchanged\n'
}

postflight() {
  prepare_state_base
  require_regular_file "$STATE_BASE/current-accepted-run-id.txt"
  RUN_ID="$(tr -d '\r\n' < "$STATE_BASE/current-accepted-run-id.txt")"
  validate_run_id
  STATE_ROOT="$STATE_BASE/$RUN_ID"
  safe_state_root "$STATE_ROOT"
  [ "$(cat "$STATE_ROOT/state.status")" = "accepted" ] \
    || die "accepted activation state missing"
  source_contract_check >/dev/null
  unit_contract_check >/dev/null
  env_contract_check >/dev/null
  write_gate_check >/dev/null
  bot_health_check enabled >/dev/null
  journal_contract_check "$STATE_ROOT" >/dev/null
  telegram_postflight >/dev/null
  web_check >/dev/null
  db_snapshot >/dev/null
  [ "$(awg_snapshot)" = "$(cat "$STATE_ROOT/awg-before.snapshot")" ] \
    || die "AWG changed after activation"

  printf 'postflight=pass\n'
  printf 'run_id=%s\n' "$RUN_ID"
  printf 'source_overlay=%s\n' "$EXPECTED_OVERLAY"
  printf 'bot=active_enabled_single_instance_restart_0_watchdog_healthy\n'
  printf 'telegram=identity_match_webhook_empty_backlog_0\n'
  printf 'web=active_enabled_http_ok_loopback_only\n'
  printf 'database=integrity_ok_fk_0\n'
  printf 'awg=unchanged\n'
}

case "$MODE" in
  preflight) preflight ;;
  stage) stage_activation ;;
  accept) accept_activation ;;
  postflight) postflight ;;
  *) die "unsupported mode" ;;
esac
