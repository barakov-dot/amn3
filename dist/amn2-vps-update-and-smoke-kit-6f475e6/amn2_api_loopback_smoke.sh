#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

AMN2_DIR="${AMN2_DIR:-/opt/amn2}"
AMN2_DB="${AMN2_DB:-data/amneziya.sqlite3}"
AMN2_CONFIG="${AMN2_CONFIG:-servers.yml}"
AMN2_SERVER_NAME="${AMN2_SERVER_NAME:-debian-vps-1}"
AMN2_API_HOST="${AMN2_API_HOST:-127.0.0.1}"
AMN2_API_PORT="${AMN2_API_PORT:-3040}"
AMN2_OWNER_LABEL="${AMN2_OWNER_LABEL:-ops}"
AMN2_TOKEN_TTL_DAYS="${AMN2_TOKEN_TTL_DAYS:-7}"
AMN2_CURL_TIMEOUT="${AMN2_CURL_TIMEOUT:-5}"
AMN2_RUN_PREFLIGHT="${AMN2_RUN_PREFLIGHT:-0}"
AMN2_REQUIRE_PREFLIGHT="${AMN2_REQUIRE_PREFLIGHT:-0}"
AMN2_SYNC_SERVER_CONFIG="${AMN2_SYNC_SERVER_CONFIG:-1}"
AMN2_REQUIRE_SERVER_DB_SYNC="${AMN2_REQUIRE_SERVER_DB_SYNC:-0}"
AMN2_EXPECTED_COMMIT="${AMN2_EXPECTED_COMMIT:-6f475e6}"
AMN2_ALLOW_EXISTING_API="${AMN2_ALLOW_EXISTING_API:-0}"
AMN2_SMOKE_SCRIPT_VERSION="2026-06-04.3"

API_PID=""
TOKEN_ID=""
API_TOKEN=""
TOKEN_REVOKED="0"
WRONG_TOKEN_ID=""
WRONG_TOKEN=""
WRONG_TOKEN_REVOKED="0"
ISSUE_RAW_FILE=""
WRONG_ISSUE_RAW_FILE=""

log() {
  printf '[amn2-api-smoke] %s\n' "$*"
}

die() {
  printf '[amn2-api-smoke] ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

json_field() {
  local json_path="$1"
  local field="$2"
  "$PYTHON_BIN" - "$json_path" "$field" <<'PY'
import json
import sys

path, field = sys.argv[1], sys.argv[2]
with open(path, "r", encoding="utf-8") as handle:
    payload = json.load(handle)
value = payload.get(field)
if value is None:
    raise SystemExit(f"missing JSON field: {field}")
print(value)
PY
}

write_safe_issue_json() {
  local input_path="$1"
  local output_path="$2"
  "$PYTHON_BIN" - "$input_path" > "$output_path" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    payload = json.load(handle)
payload.pop("raw_token", None)
payload.pop("token_hash", None)
payload.pop("Authorization", None)
print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
PY
}

http_code() {
  curl -s -o /dev/null -w '%{http_code}' --max-time "$AMN2_CURL_TIMEOUT" "$@" 2>/dev/null
}

revoke_token() {
  local token_id="$1"
  local output_path="$2"
  if [ -z "$token_id" ]; then
    return 0
  fi
  "$PYTHON_BIN" -m app.cli api token revoke \
    --db "$AMN2_DB" \
    --token-id "$token_id" \
    --reason smoke-complete \
    --pretty > "$output_path" 2>&1 || true
}

cleanup() {
  local exit_code=$?
  if [ "$WRONG_TOKEN_REVOKED" = "0" ] && [ -n "$WRONG_TOKEN_ID" ]; then
    revoke_token "$WRONG_TOKEN_ID" "$RUN_DIR/wrong-scope-token-revoke-safe.json"
  fi
  if [ "$TOKEN_REVOKED" = "0" ] && [ -n "$TOKEN_ID" ]; then
    revoke_token "$TOKEN_ID" "$RUN_DIR/token-revoke-safe.json"
  fi
  if [ -n "$API_PID" ] && kill -0 "$API_PID" >/dev/null 2>&1; then
    kill "$API_PID" >/dev/null 2>&1 || true
    wait "$API_PID" >/dev/null 2>&1 || true
  fi
  rm -f "$ISSUE_RAW_FILE" "$WRONG_ISSUE_RAW_FILE"
  unset API_TOKEN WRONG_TOKEN
  exit "$exit_code"
}

[ -d "$AMN2_DIR" ] || die "AMN2_DIR does not exist: $AMN2_DIR"
cd "$AMN2_DIR"

RUN_ID="$(date -u '+%Y%m%dT%H%M%SZ')"
AMN2_LOG_ROOT="${AMN2_LOG_DIR:-$AMN2_DIR/vps-smoke}"
RUN_DIR="$AMN2_LOG_ROOT/api-loopback-$RUN_ID"
mkdir -p "$RUN_DIR"
chmod 700 "$RUN_DIR"

trap cleanup EXIT

require_cmd curl
require_cmd tar

if [ "$AMN2_API_HOST" != "127.0.0.1" ]; then
  die "AMN2_API_HOST must stay 127.0.0.1 for this gate"
fi

if [ -x "$AMN2_DIR/venv/bin/python" ]; then
  PYTHON_BIN="$AMN2_DIR/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  die "python not found"
fi

export VPS_APPLY_ENABLED="${VPS_APPLY_ENABLED:-false}"
if [ "$VPS_APPLY_ENABLED" != "false" ]; then
  die "VPS_APPLY_ENABLED must be false for read-only API smoke"
fi

if [ -f ".env" ]; then
  DOTENV_APPLY_STATUS="$("$PYTHON_BIN" - <<'PY'
from pathlib import Path

status = "unset"
for line in Path(".env").read_text(encoding="utf-8", errors="replace").splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        continue
    key, value = stripped.split("=", 1)
    if key.strip() == "VPS_APPLY_ENABLED":
        status = "safe" if value.strip().strip('"').strip("'") == "false" else "unsafe"
print(status)
PY
)"
  if [ "$DOTENV_APPLY_STATUS" = "unsafe" ]; then
    die ".env contains VPS_APPLY_ENABLED with a non-false value"
  fi
fi

BASE_URL="http://${AMN2_API_HOST}:${AMN2_API_PORT}"
if command -v ss >/dev/null 2>&1; then
  ss -ltn > "$RUN_DIR/pre-existing-listeners.txt" 2>&1 || true
  if "$PYTHON_BIN" - "$RUN_DIR/pre-existing-listeners.txt" "$AMN2_API_PORT" <<'PY'
import sys

path, port = sys.argv[1], sys.argv[2]
for line in open(path, encoding="utf-8", errors="replace"):
    if f":{port}" in line:
        raise SystemExit(0)
raise SystemExit(1)
PY
  then
    if [ "$AMN2_ALLOW_EXISTING_API" != "1" ]; then
      die "port $AMN2_API_PORT is already listening; stop the old API process or set AMN2_ALLOW_EXISTING_API=1 intentionally"
    fi
  fi
fi

EXPIRY="$("$PYTHON_BIN" - "$AMN2_TOKEN_TTL_DAYS" <<'PY'
from datetime import datetime, timedelta, timezone
import sys

days = int(sys.argv[1])
print((datetime.now(timezone.utc) + timedelta(days=days)).isoformat(timespec="seconds"))
PY
)"

log "workspace: $AMN2_DIR"
log "server name: $AMN2_SERVER_NAME"
log "api bind: $BASE_URL"
log "script version: $AMN2_SMOKE_SCRIPT_VERSION"
if command -v sha256sum >/dev/null 2>&1; then
  log "script sha256: $(sha256sum "$0" | awk '{print $1}')"
fi
log "safe evidence dir: $RUN_DIR"

{
  printf 'run_id=%s\n' "$RUN_ID"
  printf 'amn2_dir=%s\n' "$AMN2_DIR"
  printf 'db_path=%s\n' "$AMN2_DB"
  printf 'server_name=%s\n' "$AMN2_SERVER_NAME"
  printf 'api_bind=%s\n' "$BASE_URL"
  printf 'script_version=%s\n' "$AMN2_SMOKE_SCRIPT_VERSION"
  if command -v sha256sum >/dev/null 2>&1; then
    printf 'script_sha256=%s\n' "$(sha256sum "$0" | awk '{print $1}')"
  fi
  printf 'python=%s\n' "$("$PYTHON_BIN" --version 2>&1)"
  printf 'vps_apply_enabled=false\n'
} > "$RUN_DIR/context.txt"

if [ -d ".git" ] && command -v git >/dev/null 2>&1; then
  git status --short --branch > "$RUN_DIR/git-status.txt" 2>&1 || true
  git log -1 --oneline --decorate > "$RUN_DIR/git-head.txt" 2>&1 || true
  CURRENT_COMMIT="$(git rev-parse --short HEAD 2>/dev/null || true)"
  if [ -n "$AMN2_EXPECTED_COMMIT" ] && [ -n "$CURRENT_COMMIT" ]; then
    case "$CURRENT_COMMIT" in
      "$AMN2_EXPECTED_COMMIT"*) printf 'expected_commit_match=yes\n' > "$RUN_DIR/git-expected-commit.txt" ;;
      *) printf 'expected_commit_match=no\nactual=%s\nexpected=%s\n' "$CURRENT_COMMIT" "$AMN2_EXPECTED_COMMIT" > "$RUN_DIR/git-expected-commit.txt" ;;
    esac
  fi
else
  printf 'not a git checkout\n' > "$RUN_DIR/git-status.txt"
  printf 'not a git checkout\n' > "$RUN_DIR/git-head.txt"
fi
if [ -f ".amn2_source_overlay_commit" ]; then
  printf 'source_overlay_commit=%s\n' "$(cat .amn2_source_overlay_commit)" > "$RUN_DIR/source-overlay.txt"
fi

if ! "$PYTHON_BIN" - <<'PY' > "$RUN_DIR/python-imports.txt" 2>&1
import importlib

for module in ("fastapi", "uvicorn", "app.cli", "app.api.app"):
    importlib.import_module(module)
    print(f"{module}: ok")
PY
then
  {
    printf 'VPS verdict: blocked\n'
    printf 'blocker: amn2 source does not contain the read-only API route shell or dependencies are not installed\n'
    printf 'expected branch/commit: codex-vps-test-prep / %s\n' "$AMN2_EXPECTED_COMMIT"
    printf 'safe_evidence_dir: %s\n' "$RUN_DIR"
    printf 'next: update /opt/amn2 to the API source package, run python -m pip install -e ., then rerun this smoke script\n'
  } > "$RUN_DIR/api-smoke-safe-summary.txt"
  cat "$RUN_DIR/api-smoke-safe-summary.txt"
  exit 3
fi

PREFLIGHT_STATUS="skipped"
if [ "$AMN2_RUN_PREFLIGHT" = "1" ] || { [ "$AMN2_RUN_PREFLIGHT" = "auto" ] && [ -f "$AMN2_CONFIG" ]; }; then
  PREFLIGHT_STATUS="passed"
  if ! "$PYTHON_BIN" -m app.cli server preflight \
    --config "$AMN2_CONFIG" \
    --server "$AMN2_SERVER_NAME" \
    --db "$AMN2_DB" > "$RUN_DIR/server-preflight.txt" 2>&1; then
    PREFLIGHT_STATUS="failed"
  fi
  if ! "$PYTHON_BIN" -m app.cli server check \
    --config "$AMN2_CONFIG" \
    --server "$AMN2_SERVER_NAME" \
    --dry-run > "$RUN_DIR/server-check-dry-run.txt" 2>&1; then
    PREFLIGHT_STATUS="failed"
  fi
  if [ "$PREFLIGHT_STATUS" = "failed" ] && [ "$AMN2_REQUIRE_PREFLIGHT" = "1" ]; then
    die "preflight failed; see $RUN_DIR/server-preflight.txt"
  fi
fi

SERVER_DB_SYNC_STATUS="skipped"
printf 'server_db_sync=skipped\nreason=not_run\n' > "$RUN_DIR/server-db-sync.txt"
if [ "$AMN2_SYNC_SERVER_CONFIG" = "1" ] && [ -f "$AMN2_CONFIG" ]; then
  SERVER_DB_SYNC_STATUS="passed"
  if ! "$PYTHON_BIN" - "$AMN2_CONFIG" "$AMN2_SERVER_NAME" "$AMN2_DB" > "$RUN_DIR/server-db-sync.txt" 2>&1 <<'PY'
from pathlib import Path
import sys

from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.server_config.loader import load_server_config, select_server

config_path = Path(sys.argv[1])
server_name = sys.argv[2]
db_path = Path(sys.argv[3])

config = load_server_config(config_path)
server = select_server(config, server_name)
db_path.parent.mkdir(parents=True, exist_ok=True)
conn = connect(db_path)
try:
    initialize_schema(conn)
    repo = Repository(conn)
    server_id = repo.upsert_server_config(
        name=server.name,
        host=server.ssh.host,
        ssh_port=server.ssh.port,
        endpoint_host=server.vpn.endpoint_host,
        vpn_port=int(server.vpn.port),
        vpn_network_cidr=server.vpn.network_cidr,
        server_address=server.vpn.server_address,
        server_public_key=server.vpn.server_public_key or "",
        runtime=server.runtime.type,
        firewall=server.firewall.provider,
        max_devices=server.vpn.max_devices,
    )
    row = conn.execute(
        "SELECT id, name, status, runtime FROM servers WHERE id = ?",
        (server_id,),
    ).fetchone()
finally:
    conn.close()

print("server_db_sync=passed")
print(f"id={row['id']}")
print(f"name={row['name']}")
print(f"status={row['status']}")
print(f"runtime={row['runtime']}")
PY
  then
    SERVER_DB_SYNC_STATUS="failed"
  fi
  if [ "$SERVER_DB_SYNC_STATUS" = "failed" ]; then
    {
      printf 'VPS verdict: blocked\n'
      printf 'blocker: server config DB-only sync failed before API smoke\n'
      printf 'server_db_sync_status: failed\n'
      printf 'safe_evidence_dir: %s\n' "$RUN_DIR"
      printf 'next: fix %s placeholders/server name, then rerun this smoke script\n' "$AMN2_CONFIG"
    } > "$RUN_DIR/api-smoke-safe-summary.txt"
    cat "$RUN_DIR/api-smoke-safe-summary.txt"
    exit 4
  fi
elif [ "$AMN2_REQUIRE_SERVER_DB_SYNC" = "1" ]; then
  {
    printf 'VPS verdict: blocked\n'
    printf 'blocker: server config DB-only sync was required but %s was not found\n' "$AMN2_CONFIG"
    printf 'server_db_sync_status: skipped\n'
    printf 'safe_evidence_dir: %s\n' "$RUN_DIR"
  } > "$RUN_DIR/api-smoke-safe-summary.txt"
  cat "$RUN_DIR/api-smoke-safe-summary.txt"
  exit 4
fi

ISSUE_RAW_FILE="$(mktemp "$RUN_DIR/.api-token-issue.XXXXXX.json")"
"$PYTHON_BIN" -m app.cli api token issue \
  --db "$AMN2_DB" \
  --name "vps-loopback-smoke-${RUN_ID}" \
  --owner-label "$AMN2_OWNER_LABEL" \
  --scope server:read \
  --scope metrics:read \
  --expires-at "$EXPIRY" \
  --pretty > "$ISSUE_RAW_FILE"
TOKEN_ID="$(json_field "$ISSUE_RAW_FILE" token_id)"
API_TOKEN="$(json_field "$ISSUE_RAW_FILE" raw_token)"
write_safe_issue_json "$ISSUE_RAW_FILE" "$RUN_DIR/token-issue-safe.json"

"$PYTHON_BIN" -m app.cli api serve \
  --host "$AMN2_API_HOST" \
  --port "$AMN2_API_PORT" > "$RUN_DIR/api-server.log" 2>&1 &
API_PID="$!"

READY_STATUS="failed"
for _ in $(seq 1 40); do
  CODE="$(http_code "$BASE_URL/api/servers" || true)"
  if [ "$CODE" != "000" ] && [ -n "$CODE" ]; then
    READY_STATUS="passed"
    break
  fi
  sleep 0.5
done
[ "$READY_STATUS" = "passed" ] || die "API server did not become reachable on loopback"

LISTENER_STATUS="unknown"
if command -v ss >/dev/null 2>&1; then
  ss -ltnp > "$RUN_DIR/listeners.txt" 2>&1 || ss -ltn > "$RUN_DIR/listeners.txt" 2>&1 || true
  "$PYTHON_BIN" - "$RUN_DIR/listeners.txt" "$AMN2_API_PORT" "$API_PID" "$AMN2_API_HOST" > "$RUN_DIR/api-listener-evidence.txt" <<'PY'
import sys

path, port, api_pid, expected_host = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
matches = [line for line in lines if f":{port}" in line]

def local_address(line: str) -> str:
    parts = line.split(None, 5)
    if len(parts) < 4 or parts[0] == "State":
        return ""
    return parts[3]

def host_part(local: str) -> str:
    if not local:
        return ""
    if local.startswith("[") and "]:" in local:
        return local[1:].split("]:", 1)[0]
    if ":" in local:
        return local.rsplit(":", 1)[0]
    return local

def is_loopback(host: str) -> bool:
    normalized = host.strip("[]")
    return (
        normalized == expected_host
        or normalized == "localhost"
        or normalized == "::1"
        or normalized.startswith("127.")
        or normalized.startswith("::ffff:127.")
    )

def is_wildcard(host: str) -> bool:
    normalized = host.strip("[]")
    return normalized in {"", "*", "0.0.0.0", "::", ":::"}

parsed = []
unsafe = []
for line in matches:
    local = local_address(line)
    host = host_part(local)
    pid_match = f"pid={api_pid}" in line
    parsed.append((line, host, pid_match))
    if is_wildcard(host) and (pid_match or "users:(" not in line):
        unsafe.append(line)
    elif not is_loopback(host) and pid_match:
        unsafe.append(line)

print(f"listener_rows={len(matches)}")
print(f"api_pid={api_pid}")
print(f"expected_host={expected_host}")
for line, host, pid_match in parsed:
    print(f"host={host or '<unknown>'} pid_match={'yes' if pid_match else 'no'} row={line}")
print(f"loopback_only={'no' if unsafe else 'yes'}")
if unsafe:
    print("unsafe_listener_rows:")
    for line in unsafe:
        print(line)
PY
  if grep -q 'loopback_only=no' "$RUN_DIR/api-listener-evidence.txt"; then
    LISTENER_STATUS="failed"
  else
    LISTENER_STATUS="passed"
  fi
else
  printf 'ss command unavailable; bind enforced by api serve args: %s\n' "$BASE_URL" > "$RUN_DIR/api-listener-evidence.txt"
  LISTENER_STATUS="passed"
fi

MISSING_CODE="$(http_code "$BASE_URL/api/servers" || true)"

WRONG_ISSUE_RAW_FILE="$(mktemp "$RUN_DIR/.api-token-wrong-scope.XXXXXX.json")"
"$PYTHON_BIN" -m app.cli api token issue \
  --db "$AMN2_DB" \
  --name "vps-wrong-scope-${RUN_ID}" \
  --owner-label "$AMN2_OWNER_LABEL" \
  --scope server:read \
  --expires-at "$EXPIRY" \
  --pretty > "$WRONG_ISSUE_RAW_FILE"
WRONG_TOKEN_ID="$(json_field "$WRONG_ISSUE_RAW_FILE" token_id)"
WRONG_TOKEN="$(json_field "$WRONG_ISSUE_RAW_FILE" raw_token)"
write_safe_issue_json "$WRONG_ISSUE_RAW_FILE" "$RUN_DIR/wrong-scope-token-issue-safe.json"
WRONG_SCOPE_CODE="$(http_code -H "Authorization: Bearer ${WRONG_TOKEN}" "$BASE_URL/api/metrics/summary" || true)"
revoke_token "$WRONG_TOKEN_ID" "$RUN_DIR/wrong-scope-token-revoke-safe.json"
WRONG_TOKEN_REVOKED="1"
unset WRONG_TOKEN

"$PYTHON_BIN" -m app.cli api smoke-check \
  --base-url "$BASE_URL" \
  --token "$API_TOKEN" \
  --server-name "$AMN2_SERVER_NAME" \
  --pretty > "$RUN_DIR/api-smoke-result.json"
SMOKE_STATUS="$(json_field "$RUN_DIR/api-smoke-result.json" status)"

revoke_token "$TOKEN_ID" "$RUN_DIR/token-revoke-safe.json"
TOKEN_REVOKED="1"
REVOKED_CODE="$(http_code -H "Authorization: Bearer ${API_TOKEN}" "$BASE_URL/api/servers" || true)"
unset API_TOKEN

"$PYTHON_BIN" - "$AMN2_DB" > "$RUN_DIR/api-audit-evidence.txt" <<'PY'
import json
import sqlite3
import sys

db_path = sys.argv[1]
forbidden = (
    "raw_token",
    "Authorization",
    "token_hash",
    ".conf",
    "vpn://",
    "PrivateKey",
    "PresharedKey",
)
try:
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT action, metadata_json FROM admin_actions "
        "WHERE action='api_read' ORDER BY id DESC LIMIT 5"
    ).fetchall()
finally:
    try:
        conn.close()
    except Exception:
        pass

print(f"api_read_rows={len(rows)}")
all_safe = True
for index, (action, metadata_json) in enumerate(rows, start=1):
    text = metadata_json or ""
    markers = [marker for marker in forbidden if marker.lower() in text.lower()]
    if markers:
        all_safe = False
    try:
        keys = sorted(json.loads(text).keys())
    except Exception:
        keys = ["<invalid-json>"]
        all_safe = False
    print(f"row_{index}: action={action} keys={','.join(keys)} forbidden_markers={','.join(markers) or 'none'}")
print(f"audit_safe={'yes' if all_safe and rows else 'no'}")
PY

AUDIT_STATUS="failed"
if grep -q '^audit_safe=yes$' "$RUN_DIR/api-audit-evidence.txt"; then
  AUDIT_STATUS="passed"
fi

AUTH_STATUS="failed"
if [ "$MISSING_CODE" = "401" ] && [ "$WRONG_SCOPE_CODE" = "403" ] && [ "$REVOKED_CODE" = "401" ]; then
  AUTH_STATUS="passed"
fi

{
  printf 'auth_status=%s\n' "$AUTH_STATUS"
  printf 'missing_bearer_expected=401\n'
  printf 'missing_bearer_actual=%s\n' "$MISSING_CODE"
  printf 'wrong_scope_expected=403\n'
  printf 'wrong_scope_actual=%s\n' "$WRONG_SCOPE_CODE"
  printf 'revoked_token_expected=401\n'
  printf 'revoked_token_actual=%s\n' "$REVOKED_CODE"
} > "$RUN_DIR/api-auth-evidence.txt"

VERDICT="pass"
if [ "$SMOKE_STATUS" != "passed" ] || [ "$AUTH_STATUS" != "passed" ] || [ "$LISTENER_STATUS" != "passed" ] || [ "$AUDIT_STATUS" != "passed" ]; then
  VERDICT="blocked"
fi

{
  printf 'VPS verdict: %s\n' "$VERDICT"
  printf 'run_id: %s\n' "$RUN_ID"
  printf 'branch/head:\n'
  sed 's/^/  /' "$RUN_DIR/git-head.txt" 2>/dev/null || true
  printf 'preflight_status: %s\n' "$PREFLIGHT_STATUS"
  printf 'server_db_sync_status: %s\n' "$SERVER_DB_SYNC_STATUS"
  printf 'api_ready_status: %s\n' "$READY_STATUS"
  printf 'api_smoke_status: %s\n' "$SMOKE_STATUS"
  printf 'auth_status: %s\n' "$AUTH_STATUS"
  printf 'missing_bearer_http: %s\n' "$MISSING_CODE"
  printf 'wrong_scope_http: %s\n' "$WRONG_SCOPE_CODE"
  printf 'revoked_token_http: %s\n' "$REVOKED_CODE"
  printf 'listener_status: %s\n' "$LISTENER_STATUS"
  printf 'audit_status: %s\n' "$AUDIT_STATUS"
  printf 'safe_evidence_dir: %s\n' "$RUN_DIR"
  printf 'safe_bundle: %s/api-loopback-safe-evidence-%s.tar.gz\n' "$AMN2_LOG_ROOT" "$RUN_ID"
  printf '\nDo not send api-server.log unless manually redacted.\n'
} > "$RUN_DIR/api-smoke-safe-summary.txt"

SAFE_BUNDLE="$AMN2_LOG_ROOT/api-loopback-safe-evidence-${RUN_ID}.tar.gz"
tar -czf "$SAFE_BUNDLE" -C "$RUN_DIR" \
  context.txt \
  git-status.txt \
  git-head.txt \
  git-expected-commit.txt \
  python-imports.txt \
  token-issue-safe.json \
  wrong-scope-token-issue-safe.json \
  wrong-scope-token-revoke-safe.json \
  token-revoke-safe.json \
  api-smoke-result.json \
  api-auth-evidence.txt \
  api-listener-evidence.txt \
  api-audit-evidence.txt \
  server-db-sync.txt \
  api-smoke-safe-summary.txt \
  server-preflight.txt \
  server-check-dry-run.txt 2>/dev/null || \
tar -czf "$SAFE_BUNDLE" -C "$RUN_DIR" \
  context.txt \
  git-status.txt \
  git-head.txt \
  python-imports.txt \
  token-issue-safe.json \
  wrong-scope-token-issue-safe.json \
  wrong-scope-token-revoke-safe.json \
  token-revoke-safe.json \
  api-smoke-result.json \
  api-auth-evidence.txt \
  api-listener-evidence.txt \
  api-audit-evidence.txt \
  server-db-sync.txt \
  api-smoke-safe-summary.txt

cat "$RUN_DIR/api-smoke-safe-summary.txt"

if [ "$VERDICT" != "pass" ]; then
  exit 2
fi
