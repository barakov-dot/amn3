#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

MODE="${1:-}"

AMN2_DIR="/opt/amn2"
DB_PATH="$AMN2_DIR/data/amneziya.sqlite3"
ENV_PATH="$AMN2_DIR/.env"
OVERLAY_MARKER="$AMN2_DIR/.amn2_source_overlay_commit"
UNIT_SOURCE="$AMN2_DIR/deploy/systemd/amneziya-bot.service.example"
PYTHON_BIN="$AMN2_DIR/venv/bin/python"
BOT_UNIT="amneziya-bot.service"
WEB_UNIT="amneziya-web.service"
BOT_USER="amneziya"
BOT_GROUP="amneziya"
AWG_CONTAINER="amnezia-awg2"
AWG_INTERFACE="awg0"
STATE_BASE="/root/amn2-telegram-002b-stale-start"

EXPECTED_OVERLAY="0b858c5"
SOURCE_FULL_COMMIT="0b858c5cdbc5b565cc265966a2edfe2d339d65e0"
EXPECTED_BOT_USERNAME="NeobyatnayaAMNZ_bot"
UNIT_SOURCE_SHA="E0C6706B030775C9731CF3FC3A055CAE88512CF470BF2D6BFABDACD7F2F5F694"
PERSISTENT_RUNTIME_SHA="F400FE8FDA673CA6976B698365A591CEC3A373C4284721A39AEF935DF16C5A31"
APP_MAIN_SHA="C34A0F457B2242EDE138DD0B6DC1B08B860515F7BD2FADB7DF8F2B86A3F5ED31"
SYSTEMD_NOTIFY_SHA="649EA2EABBD6B18C5E489D2059D08020D64914C47B15E50EA2873AEEFA99A8A3"
SETTINGS_SHA="1DB81553DBCBF4DAFC710EFDD69C2DB0CC1A869F0754D7BB67C7ADFA3DCAC631"

die() {
  printf 'cleanup_gate=failed reason=cleanup_rejected\n' >&2
  return 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die
}

sha256_upper() {
  sha256sum "$1" | awk '{print toupper($1)}'
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

source_contract_check() {
  require_regular_file "$OVERLAY_MARKER"
  [ "$(tr -d '\r\n' < "$OVERLAY_MARKER")" = "$EXPECTED_OVERLAY" ] || die

  require_regular_file "$UNIT_SOURCE"
  require_regular_file "$AMN2_DIR/app/bot/persistent_runtime.py"
  require_regular_file "$AMN2_DIR/app/main.py"
  require_regular_file "$AMN2_DIR/app/systemd_notify.py"
  require_regular_file "$AMN2_DIR/app/config/settings.py"

  [ "$(sha256_upper "$UNIT_SOURCE")" = "$UNIT_SOURCE_SHA" ] || die
  [ "$(sha256_upper "$AMN2_DIR/app/bot/persistent_runtime.py")" = "$PERSISTENT_RUNTIME_SHA" ] || die
  [ "$(sha256_upper "$AMN2_DIR/app/main.py")" = "$APP_MAIN_SHA" ] || die
  [ "$(sha256_upper "$AMN2_DIR/app/systemd_notify.py")" = "$SYSTEMD_NOTIFY_SHA" ] || die
  [ "$(sha256_upper "$AMN2_DIR/app/config/settings.py")" = "$SETTINGS_SHA" ] || die

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
  [ "$(systemctl is-active "$WEB_UNIT")" = "active" ] || die
  [ "$(systemctl is-enabled "$WEB_UNIT")" = "enabled" ] || die
  local login_code protected_code
  login_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:3030/login)"
  protected_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:3030/users)"
  [ "$login_code" = "200" ] || die
  case "$protected_code" in 302|303|307) ;; *) die ;; esac
  listener_check >/dev/null
  printf 'web=active_enabled_http_ok_loopback_only\n'
}

bot_inactive_disabled_check() {
  [ "$(systemctl is-active "$BOT_UNIT" 2>/dev/null || true)" = "inactive" ] || die
  [ "$(systemctl is-enabled "$BOT_UNIT" 2>/dev/null || true)" = "disabled" ] || die
  if pgrep -f 'python.*app\.main|python.*amneziya.*bot' >/dev/null 2>&1; then
    die
  fi
  printf 'bot=inactive_disabled_process_0\n'
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
    logical = hashlib.sha256()
    for statement in conn.iterdump():
        logical.update(statement.encode("utf-8"))
        logical.update(b"\n")
finally:
    conn.close()

counts_blob = json.dumps(counts, sort_keys=True, separators=(",", ":")).encode()
print(f"integrity={integrity}")
print(f"foreign_key_issues={fk}")
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
  [ "$running" = "true" ] || die
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

telegram_queue_gate() {
  local action="$1"
  PYTHONPATH="$AMN2_DIR" "$PYTHON_BIN" - "$ENV_PATH" "$EXPECTED_BOT_USERNAME" "$BOT_USER" "$action" <<'PY'
import asyncio
import os
import pwd
import sys

from aiogram.exceptions import TelegramAPIError

from app.config import Settings
from app.main import create_bot

env_path, expected_username, service_user, action = sys.argv[1:]


class CleanupRejected(RuntimeError):
    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category = category


def pending_count(webhook) -> int:
    raw = getattr(webhook, "pending_update_count", None)
    if isinstance(raw, bool):
        raise CleanupRejected("pending_count_not_one")
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise CleanupRejected("pending_count_not_one") from None
    if value != 1:
        raise CleanupRejected("pending_count_not_one")
    return value


async def inspect_one(bot, first_admin: int) -> int:
    updates = await bot.get_updates(limit=2, timeout=0)
    if len(updates) != 1:
        raise CleanupRejected("update_count_not_one")
    update = updates[0]
    update_id = getattr(update, "update_id", None)
    if not isinstance(update_id, int) or isinstance(update_id, bool) or update_id < 0:
        raise CleanupRejected("update_shape_invalid")
    message = getattr(update, "message", None)
    if message is None or getattr(message, "from_user", None) is None:
        raise CleanupRejected("update_shape_invalid")
    disallowed_update_fields = (
        "edited_message",
        "channel_post",
        "edited_channel_post",
        "business_connection",
        "business_message",
        "edited_business_message",
        "deleted_business_messages",
        "message_reaction",
        "message_reaction_count",
        "inline_query",
        "chosen_inline_result",
        "callback_query",
        "shipping_query",
        "pre_checkout_query",
        "poll",
        "poll_answer",
        "my_chat_member",
        "chat_member",
        "chat_join_request",
        "chat_boost",
        "removed_chat_boost",
    )
    if any(getattr(update, field, None) is not None for field in disallowed_update_fields):
        raise CleanupRejected("update_shape_invalid")
    if getattr(message, "content_type", None) != "text":
        raise CleanupRejected("update_shape_invalid")
    if getattr(message, "chat", None) is None or message.chat.type != "private":
        raise CleanupRejected("chat_not_private")
    try:
        sender_id = int(message.from_user.id)
        chat_id = int(message.chat.id)
    except (TypeError, ValueError):
        raise CleanupRejected("update_shape_invalid") from None
    if sender_id != first_admin:
        raise CleanupRejected("actor_mismatch")
    if chat_id != first_admin:
        raise CleanupRejected("actor_mismatch")
    text = str(getattr(message, "text", "") or "").strip()
    if text != "/start":
        raise CleanupRejected("command_mismatch")
    return update_id


async def main(cleanup: bool) -> None:
    bot = None
    try:
        async with asyncio.timeout(30):
            os.environ.clear()
            settings = Settings(_env_file=env_path)
            if settings.vps_apply_enabled or settings.operator_device_create_enabled:
                raise CleanupRejected("cleanup_rejected")
            admin_ids = [int(value) for value in settings.admin_ids]
            if (
                not admin_ids
                or any(value <= 0 for value in admin_ids)
                or len(set(admin_ids)) != len(admin_ids)
            ):
                raise CleanupRejected("cleanup_rejected")
            first_admin = admin_ids[0]
            account = pwd.getpwnam(service_user)
            os.initgroups(account.pw_name, account.pw_gid)
            os.setgid(account.pw_gid)
            os.setuid(account.pw_uid)
            bot = create_bot(
                telegram_bot_token=settings.telegram_bot_token,
                telegram_proxy_url=settings.telegram_proxy_url,
            )
            me = await bot.get_me()
            actual = str(getattr(me, "username", "") or "").strip()
            if actual.casefold() != expected_username.casefold():
                raise CleanupRejected("identity_mismatch")
            webhook = await bot.get_webhook_info()
            if str(getattr(webhook, "url", "") or "").strip():
                raise CleanupRejected("webhook_configured")
            pending_count(webhook)
            first_update_id = await inspect_one(bot, first_admin)
            webhook = await bot.get_webhook_info()
            if str(getattr(webhook, "url", "") or "").strip():
                raise CleanupRejected("webhook_configured")
            pending_count(webhook)
            second_update_id = await inspect_one(bot, first_admin)
            if first_update_id != second_update_id:
                raise CleanupRejected("update_changed_before_ack")
            if not cleanup:
                print("telegram_cleanup_preflight=pass")
                return
            concurrent = await bot.get_updates(
                offset=second_update_id + 1,
                limit=1,
                timeout=0,
            )
            final_webhook = await bot.get_webhook_info()
            if str(getattr(final_webhook, "url", "") or "").strip():
                raise CleanupRejected("webhook_configured")
            final_pending = int(
                getattr(final_webhook, "pending_update_count", 0) or 0
            )
            if concurrent or final_pending != 0:
                raise CleanupRejected("concurrent_update_detected")
            print("telegram_cleanup_acknowledgement=pass")
    except CleanupRejected as exc:
        raise SystemExit(f"telegram_cleanup=failed reason={exc.category}") from None
    except TimeoutError:
        raise SystemExit("telegram_cleanup=failed reason=cleanup_timeout") from None
    except (OSError, TelegramAPIError):
        raise SystemExit("telegram_cleanup=failed reason=network_failure") from None
    except Exception:
        raise SystemExit("telegram_cleanup=failed reason=cleanup_rejected") from None
    finally:
        if bot is not None:
            try:
                await bot.session.close()
            except Exception:
                raise SystemExit(
                    "telegram_cleanup=failed reason=cleanup_rejected"
                ) from None


asyncio.run(main(action == "cleanup"))
PY
}

common_preflight() {
  require_cmd systemctl
  require_cmd sha256sum
  require_cmd docker
  require_cmd curl
  require_cmd ss
  require_cmd readlink
  require_cmd pgrep
  require_cmd mktemp
  require_cmd cmp
  require_executable_file "$PYTHON_BIN"
  id "$BOT_USER" >/dev/null 2>&1 || die
  getent group "$BOT_GROUP" >/dev/null 2>&1 || die
  source_contract_check
  require_regular_file "$ENV_PATH"
  require_regular_file "$DB_PATH"
  write_gate_check
  web_check
  bot_inactive_disabled_check
  db_snapshot
  awg_snapshot
}

preflight() {
  common_preflight
  telegram_queue_gate preflight
  printf 'preflight=pass\n'
}

cleanup_stale_start() {
  common_preflight >/dev/null
  [ ! -L "$STATE_BASE" ] || die
  mkdir -p "$STATE_BASE"
  chown root:root "$STATE_BASE"
  chmod 700 "$STATE_BASE"
  [ "$(stat -c '%U:%G:%a' "$STATE_BASE")" = "root:root:700" ] || die

  local state_root queue_result
  state_root="$(mktemp -d "$STATE_BASE/run.XXXXXXXX")"
  chown root:root "$state_root"
  chmod 700 "$state_root"
  db_snapshot >"$state_root/db.before"
  awg_snapshot >"$state_root/awg.before"
  chmod 600 "$state_root/db.before" "$state_root/awg.before"

  queue_result="$(telegram_queue_gate cleanup)"
  [ "$queue_result" = "telegram_cleanup_acknowledgement=pass" ] || die

  source_contract_check >/dev/null
  write_gate_check >/dev/null
  bot_inactive_disabled_check >/dev/null
  web_check >/dev/null
  db_snapshot >"$state_root/db.after"
  awg_snapshot >"$state_root/awg.after"
  chmod 600 "$state_root/db.after" "$state_root/awg.after"
  cmp -s "$state_root/db.before" "$state_root/db.after" || die
  cmp -s "$state_root/awg.before" "$state_root/awg.after" || die

  rm -f -- \
    "$state_root/db.before" \
    "$state_root/awg.before" \
    "$state_root/db.after" \
    "$state_root/awg.after"
  rmdir -- "$state_root"

  printf 'telegram_cleanup=pass acknowledged_update=first_configured_admin_exact_private_start_only\n'
  printf 'pending_update_count=0\n'
  printf 'production_database=unchanged_integrity_ok_fk_0\n'
  printf 'web=active_enabled_http_ok_loopback_only\n'
  printf 'regular_bot=inactive_disabled_process_0\n'
  printf 'awg=running_restart_0_peer_set_unchanged\n'
}

case "$MODE" in
  preflight)
    preflight
    ;;
  cleanup)
    cleanup_stale_start
    ;;
  *)
    die
    ;;
esac
