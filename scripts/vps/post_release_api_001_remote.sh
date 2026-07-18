#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

MODE="${1:-}"

AMN2_DIR="/opt/amn2"
ENV_PATH="$AMN2_DIR/.env"
DB_PATH="$AMN2_DIR/data/amneziya.sqlite3"
OVERLAY_MARKER="$AMN2_DIR/.amn2_source_overlay_commit"
PYTHON_BIN="$AMN2_DIR/venv/bin/python"
STATE_BASE="/root/amn2-post-release-api-001"
BOT_UNIT="amneziya-bot.service"
WEB_UNIT="amneziya-web.service"
AWG_CONTAINER="amnezia-awg2"
AWG_INTERFACE="awg0"

EXPECTED_OVERLAY="0b858c5"
SOURCE_FULL_COMMIT="0b858c5cdbc5b565cc265966a2edfe2d339d65e0"
CLI_SHA="D77EADBE04A8B7FD6C3F75BC21E4F5FF7937CBF258DDC648D8F9ADAE0D0E5F86"
API_APP_SHA="CB2B27B476674D2396BE5867F15A857CF8DD1B4989F8AA8FDEFD4F761F7BF536"
SETTINGS_SHA="1DB81553DBCBF4DAFC710EFDD69C2DB0CC1A869F0754D7BB67C7ADFA3DCAC631"
SCHEMA_SHA="D2FCB0892B0233B34182206BC14B5D3257C2EDCDDC2DB884606A48C12B0A959B"
REPOSITORIES_SHA="997A3F615210A57CDF993F76D144F6C47B443C1749709EEA5B034F0AD6CBD72D"
API_TOKENS_SHA="B7FDFEAFD9B0621D1B6450B3C64A9E34DF3F095C5E22C5D2ED68E46EB7879A06"
API_SMOKE_SHA="6F5404AD33A1C48F15405085D660CD0122F3BBCCF648801B79E58217AE8DB267"
RUN_TTL_SECONDS="180"

STATE_ROOT=""
CLONE_PATH=""
API_PID=""
WATCHDOG_PID=""
CLEANUP_RAN="0"

die() {
  printf 'api_001_gate=failed reason=gate_rejected\n' >&2
  return 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die
}

require_regular_file() {
  local path="$1"
  [ -f "$path" ] && [ ! -L "$path" ] || die
}

require_executable_file() {
  local path="$1" resolved
  [ -e "$path" ] || die
  resolved="$(readlink -f -- "$path" 2>/dev/null)" || die
  [ -f "$resolved" ] && [ -x "$resolved" ] || die
}

sha256_upper() {
  sha256sum "$1" | awk '{print toupper($1)}'
}

source_contract_check() {
  require_regular_file "$OVERLAY_MARKER"
  [ "$(tr -d '\r\n' < "$OVERLAY_MARKER")" = "$EXPECTED_OVERLAY" ] || die

  local relative expected
  while IFS='|' read -r relative expected; do
    require_regular_file "$AMN2_DIR/$relative"
    [ "$(sha256_upper "$AMN2_DIR/$relative")" = "$expected" ] || die
  done <<EOF
app/cli.py|$CLI_SHA
app/api/app.py|$API_APP_SHA
app/config/settings.py|$SETTINGS_SHA
app/db/schema.py|$SCHEMA_SHA
app/db/repositories.py|$REPOSITORIES_SHA
app/services/api_tokens.py|$API_TOKENS_SHA
app/services/api_smoke.py|$API_SMOKE_SHA
EOF

  printf 'source_overlay=%s\n' "$EXPECTED_OVERLAY"
  printf 'source_commit=%s\n' "$SOURCE_FULL_COMMIT"
  printf 'source_contract=pass\n'
}

write_gate_check() {
  require_regular_file "$ENV_PATH"
  "$PYTHON_BIN" - "$ENV_PATH" <<'PY'
import sys
from pathlib import Path

values: dict[str, str] = {}
for line in Path(sys.argv[1]).read_text(encoding="utf-8", errors="strict").splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        continue
    key, value = stripped.split("=", 1)
    key = key.strip()
    if key in values:
        raise SystemExit(1)
    values[key] = value.strip().strip('"').strip("'")
required = {
    "VPS_APPLY_ENABLED": "false",
    "OPERATOR_DEVICE_CREATE_ENABLED": "false",
}
if any(values.get(key, "false") != expected for key, expected in required.items()):
    raise SystemExit(1)
print("write_gates=false_false")
PY
}

production_api_fingerprint() {
  "$PYTHON_BIN" - "$DB_PATH" <<'PY'
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

path = Path(sys.argv[1])
conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
try:
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_key_issues = len(conn.execute("PRAGMA foreign_key_check").fetchall())
    tokens = [dict(row) for row in conn.execute("SELECT * FROM api_tokens ORDER BY id")]
    actions = [
        dict(row)
        for row in conn.execute(
            "SELECT * FROM admin_actions "
            "WHERE action IN ('api_read', 'api_write') ORDER BY id"
        )
    ]
finally:
    conn.close()
if integrity != "ok" or foreign_key_issues:
    raise SystemExit(1)
canonical = json.dumps(
    {"tokens": tokens, "actions": actions},
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
print(f"integrity={integrity}")
print(f"foreign_key_issues={foreign_key_issues}")
print(f"api_fingerprint_sha256={hashlib.sha256(canonical).hexdigest().upper()}")
PY
}

listener_3040_absent() {
  ss -ltnH | "$PYTHON_BIN" -c '
import sys
listeners = []
for line in sys.stdin:
    fields = line.split()
    if len(fields) >= 4 and fields[3].rsplit(":", 1)[-1] == "3040":
        listeners.append(fields[3])
if listeners:
    raise SystemExit(1)
print("listener_3040_absent=pass")
'
}

listener_3040_exact() {
  ss -ltnH | "$PYTHON_BIN" -c '
import sys
listeners = []
for line in sys.stdin:
    fields = line.split()
    if len(fields) >= 4 and fields[3].rsplit(":", 1)[-1] == "3040":
        listeners.append(fields[3])
if listeners != ["127.0.0.1:3040"]:
    raise SystemExit(1)
print("listener_3040=ipv4_loopback_only")
'
}

bot_snapshot() {
  local active enabled pid restarts fragment process_count command_line
  local watchdog_usec watchdog_timestamp
  active="$(systemctl is-active "$BOT_UNIT")"
  enabled="$(systemctl is-enabled "$BOT_UNIT")"
  [ "$active" = "active" ] || die
  [ "$enabled" = "enabled" ] || die
  pid="$(systemctl show "$BOT_UNIT" --property=MainPID --value)"
  restarts="$(systemctl show "$BOT_UNIT" --property=NRestarts --value)"
  fragment="$(systemctl show "$BOT_UNIT" --property=FragmentPath --value)"
  watchdog_usec="$(systemctl show "$BOT_UNIT" --property=WatchdogUSec --value)"
  watchdog_timestamp="$(systemctl show "$BOT_UNIT" --property=WatchdogTimestampMonotonic --value)"
  [[ "$pid" =~ ^[1-9][0-9]*$ ]] || die
  [[ "$restarts" =~ ^[0-9]+$ ]] || die
  [[ "$watchdog_timestamp" =~ ^[1-9][0-9]*$ ]] || die
  [ -n "$watchdog_usec" ] && [ "$watchdog_usec" != "0" ] && [ "$watchdog_usec" != "infinity" ] || die
  [ "$fragment" = "/etc/systemd/system/$BOT_UNIT" ] || die
  [ -r "/proc/$pid/cmdline" ] || die
  command_line="$(tr '\0' ' ' < "/proc/$pid/cmdline")"
  case "$command_line" in *"/opt/amn2/venv/bin/python"*"app.main"*) ;; *) die ;; esac
  process_count="$(pgrep -f '/opt/amn2/venv/bin/python.*app\.main' | wc -l | tr -d ' ')"
  [ "$process_count" = "1" ] || die
  printf 'active=%s\n' "$active"
  printf 'enabled=%s\n' "$enabled"
  printf 'main_pid=%s\n' "$pid"
  printf 'restart_count=%s\n' "$restarts"
  printf 'process_count=1\n'
  printf 'watchdog=healthy\n'
}

web_snapshot() {
  local active enabled pid restarts login_code protected_code listener_data
  active="$(systemctl is-active "$WEB_UNIT")"
  enabled="$(systemctl is-enabled "$WEB_UNIT")"
  [ "$active" = "active" ] || die
  [ "$enabled" = "enabled" ] || die
  pid="$(systemctl show "$WEB_UNIT" --property=MainPID --value)"
  restarts="$(systemctl show "$WEB_UNIT" --property=NRestarts --value)"
  [[ "$pid" =~ ^[1-9][0-9]*$ ]] || die
  [[ "$restarts" =~ ^[0-9]+$ ]] || die
  login_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:3030/login)"
  protected_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:3030/users)"
  [ "$login_code" = "200" ] || die
  case "$protected_code" in 302|303|307) ;; *) die ;; esac
  listener_data="$(ss -ltnH | "$PYTHON_BIN" -c '
import sys
values = []
for line in sys.stdin:
    fields = line.split()
    if len(fields) >= 4 and fields[3].rsplit(":", 1)[-1] == "3030":
        values.append(fields[3])
if values != ["127.0.0.1:3030"]:
    raise SystemExit(1)
print("listener=127.0.0.1:3030")
')" || die
  printf 'active=%s\n' "$active"
  printf 'enabled=%s\n' "$enabled"
  printf 'main_pid=%s\n' "$pid"
  printf 'restart_count=%s\n' "$restarts"
  printf 'login=200\n'
  printf 'protected=redirect\n'
  printf '%s\n' "$listener_data"
}

awg_snapshot() {
  local container_id restart_count running config_json peer_data
  container_id="$(docker inspect --format '{{.Id}}' "$AWG_CONTAINER")"
  restart_count="$(docker inspect --format '{{.RestartCount}}' "$AWG_CONTAINER")"
  running="$(docker inspect --format '{{.State.Running}}' "$AWG_CONTAINER")"
  config_json="$(docker inspect --format '{{json .Config}}|{{json .HostConfig}}' "$AWG_CONTAINER")"
  [ "$running" = "true" ] || die
  [[ "$restart_count" =~ ^[0-9]+$ ]] || die
  peer_data="$(docker exec "$AWG_CONTAINER" awg show "$AWG_INTERFACE" dump | "$PYTHON_BIN" -c '
import hashlib
import sys
lines = [line.rstrip("\n") for line in sys.stdin if line.strip()]
if not lines:
    raise SystemExit(1)
peers = sorted(line.split("\t", 1)[0] for line in lines[1:])
print(f"peer_count={len(peers)}")
print(f"peer_set_sha256={hashlib.sha256(chr(10).join(peers).encode()).hexdigest().upper()}")
')" || die
  printf 'container_sha256=%s\n' "$(printf '%s' "$container_id" | sha256sum | awk '{print toupper($1)}')"
  printf 'container_config_sha256=%s\n' "$(printf '%s' "$config_json" | sha256sum | awk '{print toupper($1)}')"
  printf 'restart_count=%s\n' "$restart_count"
  printf 'running=true\n'
  printf '%s\n' "$peer_data"
}

disk_capacity_check() {
  local db_bytes free_bytes required_bytes
  db_bytes="$(stat -c '%s' "$DB_PATH")"
  free_bytes="$(df -PB1 "$(dirname "$DB_PATH")" | awk 'NR==2 {print $4}')"
  [[ "$db_bytes" =~ ^[1-9][0-9]*$ ]] || die
  [[ "$free_bytes" =~ ^[1-9][0-9]*$ ]] || die
  required_bytes=$((db_bytes * 4 + 67108864))
  [ "$free_bytes" -ge "$required_bytes" ] || die
  printf 'clone_capacity=pass\n'
}

common_preflight() {
  local command_name
  for command_name in awk curl date df docker env install kill pgrep readlink \
    setsid sha256sum sleep ss stat systemctl tr wc seq; do
    require_cmd "$command_name"
  done
  require_executable_file "$PYTHON_BIN"
  require_regular_file "$DB_PATH"
  source_contract_check
  write_gate_check
  production_api_fingerprint >/dev/null
  listener_3040_absent >/dev/null
  bot_snapshot >/dev/null
  web_snapshot >/dev/null
  awg_snapshot >/dev/null
  disk_capacity_check >/dev/null
}

create_clone() {
  local run_id
  run_id="$(date -u +%Y%m%dT%H%M%SZ)-$$"
  STATE_ROOT="$STATE_BASE/$run_id"
  case "$STATE_ROOT" in "$STATE_BASE"/20[0-9][0-9][0-1][0-9][0-3][0-9]T*-*) ;; *) die ;; esac
  install -d -m 0700 "$STATE_ROOT"
  CLONE_PATH="$STATE_ROOT/amneziya-clone.sqlite3"
  "$PYTHON_BIN" - "$DB_PATH" "$CLONE_PATH" <<'PY'
import os
import sqlite3
import sys
from pathlib import Path

source_path = Path(sys.argv[1])
clone_path = Path(sys.argv[2])
source = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
destination = sqlite3.connect(clone_path)
try:
    with destination:
        source.backup(destination)
    integrity = destination.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_key_issues = len(destination.execute("PRAGMA foreign_key_check").fetchall())
finally:
    destination.close()
    source.close()
os.chmod(clone_path, 0o600)
if integrity != "ok" or foreign_key_issues:
    raise SystemExit(1)
PY
  require_regular_file "$CLONE_PATH"
  [ "$(stat -c '%U:%G:%a' "$CLONE_PATH")" = "root:root:600" ] || die
}

start_transient_api() {
  (
    cd "$AMN2_DIR"
    exec setsid env \
      DATABASE_PATH="$CLONE_PATH" \
      VPS_APPLY_ENABLED=false \
      OPERATOR_DEVICE_CREATE_ENABLED=false \
      PYTHONPATH="$AMN2_DIR" \
      "$PYTHON_BIN" -m app.cli api serve --host 127.0.0.1 --port 3040 \
      >"$STATE_ROOT/api.stdout" 2>"$STATE_ROOT/api.stderr"
  ) &
  API_PID="$!"
  printf '%s\n' "$API_PID" >"$STATE_ROOT/api.pid"
  (
    sleep "$RUN_TTL_SECONDS"
    if kill -0 "$API_PID" 2>/dev/null; then
      kill -- "-$API_PID" 2>/dev/null || true
    fi
  ) &
  WATCHDOG_PID="$!"
  printf '%s\n' "$WATCHDOG_PID" >"$STATE_ROOT/watchdog.pid"

  local attempt
  for attempt in $(seq 1 50); do
    kill -0 "$API_PID" 2>/dev/null || die
    if listener_3040_exact >/dev/null 2>&1; then
      printf 'transient_api=ipv4_loopback_only\n'
      return 0
    fi
    sleep 0.2
  done
  die
}

run_smoke() {
  local missing_code invalid_code server_name expires_at
  missing_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 \
    http://127.0.0.1:3040/api/servers)"
  invalid_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 \
    -H 'Authorization: Bearer invalid-probe' \
    http://127.0.0.1:3040/api/servers)"
  [ "$missing_code" = "401" ] || die
  [ "$invalid_code" = "401" ] || die
  printf 'missing_bearer=401\n'
  printf 'invalid_bearer=401\n'

  PYTHONPATH="$AMN2_DIR" "$PYTHON_BIN" - "$CLONE_PATH" <<'PY'
import secrets
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

from app.db.repositories import Repository
from app.services.api_tokens import create_route_api_token, revoke_api_token

db_path = sys.argv[1]
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
repo = Repository(conn)
now = datetime.now(timezone.utc)
expires_at = now + timedelta(days=1)
issues = []

def request_status(path: str, raw_token: str) -> int:
    request = urllib.request.Request(
        "http://127.0.0.1:3040" + path,
        headers={"Authorization": "Bearer " + raw_token},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)

try:
    server = create_route_api_token(
        repo,
        name="api-001-server-scope-probe",
        owner_label="api-001",
        scopes={"server:read"},
        expires_at=expires_at,
        raw_token=secrets.token_urlsafe(32),
    )
    issues.append(server)
    metrics = create_route_api_token(
        repo,
        name="api-001-metrics-scope-probe",
        owner_label="api-001",
        scopes={"metrics:read"},
        expires_at=expires_at,
        raw_token=secrets.token_urlsafe(32),
    )
    issues.append(metrics)
    if request_status("/api/metrics/summary", server.raw_token) != 403:
        raise SystemExit(1)
    if request_status("/api/servers", metrics.raw_token) != 403:
        raise SystemExit(1)
finally:
    for issue in issues:
        revoke_api_token(
            repo,
            token_id=issue.token_id,
            revoked_at=datetime.now(timezone.utc),
            reason="scope-probe-complete",
        )
    if issues:
        conn.executemany("DELETE FROM api_tokens WHERE id = ?", [(item.token_id,) for item in issues])
        conn.commit()
    conn.close()
print("server_scope_metrics=403")
print("metrics_scope_server=403")
PY

  "$PYTHON_BIN" - "$CLONE_PATH" "$STATE_ROOT/smoke.before" <<'PY'
import json
import sqlite3
import sys

conn = sqlite3.connect(sys.argv[1])
try:
    token_count = conn.execute("SELECT COUNT(*) FROM api_tokens").fetchone()[0]
    api_read_count = conn.execute(
        "SELECT COUNT(*) FROM admin_actions WHERE action = 'api_read'"
    ).fetchone()[0]
    api_write_count = conn.execute(
        "SELECT COUNT(*) FROM admin_actions WHERE action = 'api_write'"
    ).fetchone()[0]
    max_action_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM admin_actions").fetchone()[0]
finally:
    conn.close()
with open(sys.argv[2], "w", encoding="utf-8") as stream:
    json.dump(
        {
            "token_count": token_count,
            "api_read_count": api_read_count,
            "api_write_count": api_write_count,
            "max_action_id": max_action_id,
        },
        stream,
        sort_keys=True,
    )
PY

  server_name="$("$PYTHON_BIN" - "$CLONE_PATH" <<'PY'
import sqlite3
import sys

conn = sqlite3.connect(sys.argv[1])
try:
    rows = conn.execute(
        "SELECT name FROM servers WHERE status != 'disabled' ORDER BY id LIMIT 2"
    ).fetchall()
finally:
    conn.close()
if len(rows) != 1 or not str(rows[0][0]).strip():
    raise SystemExit(1)
print(str(rows[0][0]).strip())
PY
)" || die
  expires_at="$(date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%S+00:00')"
  (
    cd "$AMN2_DIR"
    PYTHONPATH="$AMN2_DIR" "$PYTHON_BIN" -m app.cli api smoke-cycle \
      --db "$CLONE_PATH" \
      --base-url http://127.0.0.1:3040 \
      --server-name "$server_name" \
      --name post-release-api-001 \
      --owner-label api-001 \
      --expires-at "$expires_at" \
      --timeout 5 \
      >"$STATE_ROOT/smoke.json"
  )

  "$PYTHON_BIN" - "$CLONE_PATH" "$STATE_ROOT/smoke.before" "$STATE_ROOT/smoke.json" <<'PY'
import json
import sqlite3
import sys

db_path, before_path, smoke_path = sys.argv[1:]
with open(before_path, encoding="utf-8") as stream:
    before = json.load(stream)
with open(smoke_path, encoding="utf-8") as stream:
    smoke = json.load(stream)
if smoke.get("action") != "api_smoke_cycle.completed" or smoke.get("status") != "passed":
    raise SystemExit(1)
if smoke.get("smoke", {}).get("checked_routes") != 6:
    raise SystemExit(1)
if smoke.get("revoke", {}).get("status") != "revoked":
    raise SystemExit(1)
token_id = smoke.get("token", {}).get("token_id")
if not isinstance(token_id, str) or not token_id:
    raise SystemExit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
try:
    token_count = conn.execute("SELECT COUNT(*) FROM api_tokens").fetchone()[0]
    api_read_count = conn.execute(
        "SELECT COUNT(*) FROM admin_actions WHERE action = 'api_read'"
    ).fetchone()[0]
    api_write_count = conn.execute(
        "SELECT COUNT(*) FROM admin_actions WHERE action = 'api_write'"
    ).fetchone()[0]
    token = conn.execute(
        "SELECT revoked_at, revoke_reason, last_used_at FROM api_tokens WHERE id = ?",
        (token_id,),
    ).fetchone()
    rows = conn.execute(
        "SELECT metadata_json FROM admin_actions WHERE id > ? AND action = 'api_read' ORDER BY id",
        (before["max_action_id"],),
    ).fetchall()
finally:
    conn.close()
if token_count - before["token_count"] != 1:
    raise SystemExit(1)
if api_read_count - before["api_read_count"] != 6:
    raise SystemExit(1)
if api_write_count - before["api_write_count"] != 0:
    raise SystemExit(1)
if token is None or not token["revoked_at"] or token["revoke_reason"] != "smoke-complete" or not token["last_used_at"]:
    raise SystemExit(1)
paths = [json.loads(row["metadata_json"])["path"] for row in rows]
expected = [
    "/api/servers",
    "/api/integration/status",
    "/api/local-agent/runtime/summary",
    "/api/servers/{server_name}/summary",
    "/api/metrics/summary",
    "/api/users/summary",
]
if paths != expected:
    raise SystemExit(1)
serialized = json.dumps(smoke, sort_keys=True)
if (
    "Authorization" in serialized
    or "token_hash" in serialized
    or "raw_token" in smoke.get("token", {})
):
    raise SystemExit(1)
print("checked_routes=6")
print("api_read_count=6")
print("api_write_count=0")
print("last_used_at=present")
print("revoked_at=present")
PY
}

mandatory_cleanup() {
  local original_rc=$? cleanup_rc=0
  if [ "$CLEANUP_RAN" = "1" ]; then
    return "$original_rc"
  fi
  CLEANUP_RAN="1"
  set +e

  if [ -n "$WATCHDOG_PID" ] && [[ "$WATCHDOG_PID" =~ ^[1-9][0-9]*$ ]]; then
    kill "$WATCHDOG_PID" 2>/dev/null
    wait "$WATCHDOG_PID" 2>/dev/null
    WATCHDOG_PID=""
  fi
  if [ -n "$API_PID" ] && [[ "$API_PID" =~ ^[1-9][0-9]*$ ]]; then
    kill -- "-$API_PID" 2>/dev/null
    wait "$API_PID" 2>/dev/null
    API_PID=""
  fi
  listener_3040_absent >/dev/null 2>&1 || cleanup_rc=1

  if [ -n "$CLONE_PATH" ]; then
    rm -f -- "$CLONE_PATH" "$CLONE_PATH-wal" "$CLONE_PATH-shm" || cleanup_rc=1
  fi
  if [ -n "$STATE_ROOT" ] && [ -d "$STATE_ROOT" ]; then
    postflight || cleanup_rc=1
    case "$STATE_ROOT" in
      "$STATE_BASE"/20[0-9][0-9][0-1][0-9][0-3][0-9]T*-*)
        rm -rf -- "$STATE_ROOT" || cleanup_rc=1
        ;;
      *)
        cleanup_rc=1
        ;;
    esac
  fi

  if [ "$original_rc" -ne 0 ] || [ "$cleanup_rc" -ne 0 ]; then
    return 1
  fi
  return 0
}

postflight() {
  [ -n "$STATE_ROOT" ] && [ -d "$STATE_ROOT" ] || return 1
  [ -z "$CLONE_PATH" ] || [ ! -e "$CLONE_PATH" ] || return 1
  listener_3040_absent >/dev/null || return 1
  bot_snapshot >"$STATE_ROOT/bot.after" || return 1
  web_snapshot >"$STATE_ROOT/web.after" || return 1
  production_api_fingerprint >"$STATE_ROOT/db.after" || return 1
  awg_snapshot >"$STATE_ROOT/awg.after" || return 1
  cmp -s "$STATE_ROOT/bot.before" "$STATE_ROOT/bot.after" || return 1
  cmp -s "$STATE_ROOT/web.before" "$STATE_ROOT/web.after" || return 1
  cmp -s "$STATE_ROOT/db.before" "$STATE_ROOT/db.after" || return 1
  cmp -s "$STATE_ROOT/awg.before" "$STATE_ROOT/awg.after" || return 1
  return 0
}

preflight() {
  common_preflight
  printf 'post_release_api_001_preflight=pass\n'
  printf 'production_api_3040=absent\n'
  printf 'production_db_bot_web_awg=observed_unchanged\n'
}

run_gate() {
  common_preflight
  trap mandatory_cleanup EXIT
  trap 'mandatory_cleanup; exit 129' HUP
  trap 'mandatory_cleanup; exit 130' INT
  trap 'mandatory_cleanup; exit 143' TERM

  create_clone
  bot_snapshot >"$STATE_ROOT/bot.before"
  web_snapshot >"$STATE_ROOT/web.before"
  production_api_fingerprint >"$STATE_ROOT/db.before"
  awg_snapshot >"$STATE_ROOT/awg.before"
  start_transient_api
  run_smoke
  mandatory_cleanup
  trap - EXIT HUP INT TERM
  [ ! -e "$STATE_ROOT" ] || die
  printf 'post_release_api_001_run=pass\n'
  printf 'cleanup=listener_0_process_0_clone_0_state_0\n'
  printf 'production_db_bot_web_awg=unchanged\n'
}

case "$MODE" in
  preflight)
    preflight
    ;;
  run)
    run_gate
    ;;
  *)
    die
    ;;
esac
