#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

MODE="${1:-}"
EXPECTED_TARGET_FINGERPRINT="${2:-}"

AMN2_DIR="/opt/amn2"
ENV_PATH="$AMN2_DIR/.env"
DB_PATH="$AMN2_DIR/data/amneziya.sqlite3"
OVERLAY_MARKER="$AMN2_DIR/.amn2_source_overlay_commit"
PYTHON_BIN="$AMN2_DIR/venv/bin/python"
ASSET_PATH="$AMN2_DIR/app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png"
TARGET_PATH="/root/.config/amn2/telegram-group-icon-001/target.json"
STATE_BASE="/root/amn2-telegram-group-icon-001"
BOT_UNIT="amneziya-bot.service"
WEB_UNIT="amneziya-web.service"
AWG_CONTAINER="amnezia-awg2"
AWG_INTERFACE="awg0"

EXPECTED_OVERLAY="0b858c5"
SOURCE_FULL_COMMIT="0b858c5cdbc5b565cc265966a2edfe2d339d65e0"
EXPECTED_BOT_USERNAME="NeobyatnayaAMNZ_bot"
ASSET_SHA="40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791"
ASSET_WIDTH="1254"
ASSET_HEIGHT="1254"
APP_MAIN_SHA="C34A0F457B2242EDE138DD0B6DC1B08B860515F7BD2FADB7DF8F2B86A3F5ED31"
SETTINGS_SHA="1DB81553DBCBF4DAFC710EFDD69C2DB0CC1A869F0754D7BB67C7ADFA3DCAC631"
ROLLBACK_TTL_SECONDS="240"

die() {
  printf 'telegram_group_icon_gate=failed reason=gate_rejected\n' >&2
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
  require_regular_file "$AMN2_DIR/app/main.py"
  require_regular_file "$AMN2_DIR/app/config/settings.py"
  [ "$(sha256_upper "$AMN2_DIR/app/main.py")" = "$APP_MAIN_SHA" ] || die
  [ "$(sha256_upper "$AMN2_DIR/app/config/settings.py")" = "$SETTINGS_SHA" ] || die
  printf 'source_overlay=%s\n' "$EXPECTED_OVERLAY"
  printf 'source_commit=%s\n' "$SOURCE_FULL_COMMIT"
  printf 'source_contract=pass\n'
}

asset_contract_check() {
  require_regular_file "$ASSET_PATH"
  [ "$(sha256_upper "$ASSET_PATH")" = "$ASSET_SHA" ] || die
  "$PYTHON_BIN" - "$ASSET_PATH" "$ASSET_WIDTH" "$ASSET_HEIGHT" <<'PY'
import struct
import sys
from pathlib import Path

path = Path(sys.argv[1])
expected_width = int(sys.argv[2])
expected_height = int(sys.argv[3])
with path.open("rb") as stream:
    header = stream.read(24)
if (
    len(header) != 24
    or header[:8] != b"\x89PNG\r\n\x1a\n"
    or header[12:16] != b"IHDR"
):
    raise SystemExit("PNG signature or IHDR mismatch")
width, height = struct.unpack(">II", header[16:24])
if (width, height) != (expected_width, expected_height):
    raise SystemExit("PNG signature or IHDR mismatch")
print("asset_contract=pass")
PY
}

target_contract_check() {
  require_regular_file "$TARGET_PATH"
  [ "$(stat -c '%U:%G:%a' "$TARGET_PATH")" = "root:root:600" ] || die
  "$PYTHON_BIN" - "$TARGET_PATH" "$EXPECTED_TARGET_FINGERPRINT" <<'PY'
import hashlib
import json
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
expected_fingerprint = sys.argv[2]
try:
    payload = json.loads(path.read_text(encoding="utf-8", errors="strict"))
except (OSError, UnicodeError, json.JSONDecodeError):
    raise SystemExit(1) from None
if not isinstance(payload, dict):
    raise SystemExit(1)
if set(payload) != {"chat_id", "expected_title", "expected_type"}:
    raise SystemExit(1)
chat_id = payload["chat_id"]
expected_title = payload["expected_title"]
expected_type = payload["expected_type"]
valid_id = (
    isinstance(chat_id, int)
    and not isinstance(chat_id, bool)
    and chat_id < 0
) or (
    isinstance(chat_id, str)
    and re.fullmatch(r"@[A-Za-z][A-Za-z0-9_]{4,31}", chat_id) is not None
)
if not valid_id:
    raise SystemExit(1)
if not isinstance(expected_title, str) or not expected_title.strip():
    raise SystemExit(1)
if expected_title != expected_title.strip() or len(expected_title) > 255:
    raise SystemExit(1)
if expected_type not in {"group", "supergroup"}:
    raise SystemExit(1)
canonical = json.dumps(
    payload,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
digest = hashlib.sha256(b"TELEGRAM-GROUP-ICON-001\0" + canonical).hexdigest().upper()
if expected_fingerprint and digest != expected_fingerprint:
    raise SystemExit(1)
print(f"target_chat_fingerprint={digest}")
PY
}

write_gate_check() {
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

bot_snapshot() {
  local active enabled pid restarts fragment process_count command_line
  active="$(systemctl is-active "$BOT_UNIT")"
  enabled="$(systemctl is-enabled "$BOT_UNIT")"
  [ "$active" = "active" ] || die
  [ "$enabled" = "enabled" ] || die
  pid="$(systemctl show "$BOT_UNIT" --property=MainPID --value)"
  restarts="$(systemctl show "$BOT_UNIT" --property=NRestarts --value)"
  fragment="$(systemctl show "$BOT_UNIT" --property=FragmentPath --value)"
  [[ "$pid" =~ ^[1-9][0-9]*$ ]] || die
  [[ "$restarts" =~ ^[0-9]+$ ]] || die
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

telegram_action() {
  local action="$1" state_root="${2:-}" target_input="$TARGET_PATH"
  if [ -n "$state_root" ] && [ -f "$state_root/target.json" ]; then
    target_input="$state_root/target.json"
  fi
  PYTHONPATH="$AMN2_DIR" "$PYTHON_BIN" - \
    "$action" "$ENV_PATH" "$target_input" "$EXPECTED_TARGET_FINGERPRINT" \
    "$EXPECTED_BOT_USERNAME" "$ASSET_PATH" "$state_root" <<'PY'
import asyncio
import hashlib
import json
import os
import sys
from pathlib import Path

from aiogram.exceptions import TelegramAPIError
from aiogram.types import FSInputFile

from app.config import Settings
from app.main import create_bot

(
    action,
    env_path,
    target_path,
    expected_fingerprint,
    expected_username,
    asset_path,
    state_root_raw,
) = sys.argv[1:]
state_root = Path(state_root_raw) if state_root_raw else None


class GateRejected(RuntimeError):
    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category = category


def load_target() -> tuple[int | str, str, str]:
    try:
        payload = json.loads(Path(target_path).read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise GateRejected("gate_rejected") from None
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256(b"TELEGRAM-GROUP-ICON-001\0" + canonical).hexdigest().upper()
    if digest != expected_fingerprint:
        raise GateRejected("target_mismatch")
    return payload["chat_id"], payload["expected_title"], payload["expected_type"]


def enum_value(value) -> str:
    return str(getattr(value, "value", value) or "")


async def telegram_contract(bot, chat_id, expected_title, expected_type):
    me = await bot.get_me()
    actual_username = str(getattr(me, "username", "") or "").strip()
    if actual_username.casefold() != expected_username.casefold():
        raise GateRejected("identity_mismatch")
    webhook = await bot.get_webhook_info()
    if str(getattr(webhook, "url", "") or "").strip():
        raise GateRejected("webhook_configured")
    raw_pending = getattr(webhook, "pending_update_count", 0)
    if isinstance(raw_pending, bool):
        raise GateRejected("pending_updates_nonzero")
    try:
        pending_update_count = int(raw_pending or 0)
    except (TypeError, ValueError):
        raise GateRejected("pending_updates_nonzero") from None
    if pending_update_count != 0:
        raise GateRejected("pending_updates_nonzero")
    chat = await bot.get_chat(chat_id)
    if isinstance(chat_id, int):
        try:
            if int(getattr(chat, "id", 0)) != chat_id:
                raise GateRejected("target_mismatch")
        except (TypeError, ValueError):
            raise GateRejected("target_mismatch") from None
    else:
        actual_chat_username = str(getattr(chat, "username", "") or "")
        if actual_chat_username.casefold() != chat_id[1:].casefold():
            raise GateRejected("target_mismatch")
    if str(getattr(chat, "title", "") or "") != expected_title:
        raise GateRejected("title_mismatch")
    if enum_value(getattr(chat, "type", None)) != expected_type:
        raise GateRejected("type_mismatch")
    member = await bot.get_chat_member(chat_id, me.id)
    if enum_value(getattr(member, "status", None)) != "administrator":
        raise GateRejected("permission_denied")
    if getattr(member, "can_change_info", False) is not True:
        raise GateRejected("permission_denied")
    return chat


async def snapshot_current_photo(bot, chat_id, chat, snapshot_path, metadata_path):
    photo = getattr(chat, "photo", None)
    if photo is None:
        snapshot_status = "no_existing_photo"
        previous_unique_id = ""
        receipt = metadata_path.parent / "no_existing_photo.receipt"
        receipt.write_text("no_existing_photo\n", encoding="utf-8")
        os.chmod(receipt, 0o600)
    else:
        big_file_id = str(getattr(photo, "big_file_id", "") or "")
        previous_unique_id = str(getattr(photo, "big_file_unique_id", "") or "")
        if not big_file_id or not previous_unique_id:
            raise GateRejected("photo_snapshot_failed")
        telegram_file = await bot.get_file(big_file_id)
        remote_file_path = str(getattr(telegram_file, "file_path", "") or "")
        if not remote_file_path:
            raise GateRejected("photo_snapshot_failed")
        await bot.download_file(remote_file_path, destination=snapshot_path)
        if not snapshot_path.is_file() or snapshot_path.is_symlink():
            raise GateRejected("photo_snapshot_failed")
        os.chmod(snapshot_path, 0o600)
        snapshot_status = "existing_photo"
    metadata_path.write_text(
        json.dumps(
            {
                "snapshot_status": snapshot_status,
                "previous_unique_id": previous_unique_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    os.chmod(metadata_path, 0o600)
    print(f"photo_snapshot={snapshot_status}")


async def apply_photo(bot, chat_id):
    result = await bot.set_chat_photo(chat_id=chat_id, photo=FSInputFile(asset_path))
    if result is not True:
        raise GateRejected("photo_apply_failed")


async def rollback_photo(bot, chat_id, snapshot_path, metadata):
    if metadata["snapshot_status"] == "existing_photo":
        if not snapshot_path.is_file() or snapshot_path.is_symlink():
            raise GateRejected("photo_rollback_failed")
        result = await bot.set_chat_photo(
            chat_id=chat_id,
            photo=FSInputFile(snapshot_path),
        )
    elif metadata["snapshot_status"] == "no_existing_photo":
        result = await bot.delete_chat_photo(chat_id=chat_id)
    else:
        raise GateRejected("photo_rollback_failed")
    if result is not True:
        raise GateRejected("photo_rollback_failed")


async def main() -> None:
    bot = None
    try:
        async with asyncio.timeout(45):
            os.environ.clear()
            chat_id, expected_title, expected_type = load_target()
            settings = Settings(_env_file=env_path)
            if settings.vps_apply_enabled or settings.operator_device_create_enabled:
                raise GateRejected("gate_rejected")
            bot = create_bot(
                telegram_bot_token=settings.telegram_bot_token,
                telegram_proxy_url=settings.telegram_proxy_url,
            )
            chat = await telegram_contract(bot, chat_id, expected_title, expected_type)
            if action == "preflight":
                print("telegram_group_icon_preflight=pass")
                return
            if state_root is None or not state_root.is_dir() or state_root.is_symlink():
                raise GateRejected("gate_rejected")
            snapshot_path = state_root / "previous-photo.bin"
            metadata_path = state_root / "photo-state.json"
            if action == "snapshot":
                await snapshot_current_photo(
                    bot,
                    chat_id,
                    chat,
                    snapshot_path,
                    metadata_path,
                )
                return
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                raise GateRejected("gate_rejected") from None
            if action == "apply":
                await apply_photo(bot, chat_id)
                print("set_chat_photo=pass calls=1")
                return
            if action == "postflight":
                post_chat = await telegram_contract(
                    bot,
                    chat_id,
                    expected_title,
                    expected_type,
                )
                post_photo = getattr(post_chat, "photo", None)
                post_unique_id = str(
                    getattr(post_photo, "big_file_unique_id", "") or ""
                )
                if not post_unique_id or post_unique_id == metadata["previous_unique_id"]:
                    raise GateRejected("photo_postflight_failed")
                print("telegram_group_icon_postflight=pass photo_changed=true")
                return
            if action == "rollback":
                await rollback_photo(bot, chat_id, snapshot_path, metadata)
                print("telegram_group_icon_rollback=pass")
                return
            raise GateRejected("gate_rejected")
    except GateRejected as exc:
        raise SystemExit(
            f"telegram_group_icon_gate=failed reason={exc.category}"
        ) from None
    except TimeoutError:
        raise SystemExit(
            "telegram_group_icon_gate=failed reason=operation_timeout"
        ) from None
    except (OSError, TelegramAPIError):
        category = {
            "snapshot": "photo_snapshot_failed",
            "apply": "photo_apply_failed",
            "postflight": "photo_postflight_failed",
            "rollback": "photo_rollback_failed",
        }.get(action, "network_failure")
        raise SystemExit(f"telegram_group_icon_gate=failed reason={category}") from None
    except Exception:
        raise SystemExit(
            "telegram_group_icon_gate=failed reason=gate_rejected"
        ) from None
    finally:
        if bot is not None:
            try:
                await bot.session.close()
            except Exception:
                raise SystemExit(
                    "telegram_group_icon_gate=failed reason=gate_rejected"
                ) from None


asyncio.run(main())
PY
}

write_rollback_helper() {
  local state_root="$1"
  cat >"$state_root/rollback.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
state_root="${1:-}"
case "$state_root" in
  /root/amn2-telegram-group-icon-001/run.*) ;;
  *) exit 1 ;;
esac
[ -d "$state_root" ] && [ ! -L "$state_root" ] || exit 1
PYTHONPATH=/opt/amn2 /opt/amn2/venv/bin/python - "$state_root" <<'PY'
import asyncio
import json
import os
import sys
from pathlib import Path

from aiogram.types import FSInputFile

from app.config import Settings
from app.main import create_bot

state_root = Path(sys.argv[1])
target_path = state_root / "target.json"
env_path = "/opt/amn2/.env"
expected_username = "NeobyatnayaAMNZ_bot"


def enum_value(value) -> str:
    return str(getattr(value, "value", value) or "")


async def restore() -> None:
    os.environ.clear()
    payload = json.loads(target_path.read_text(encoding="utf-8", errors="strict"))
    metadata = json.loads(
        (state_root / "photo-state.json").read_text(encoding="utf-8", errors="strict")
    )
    settings = Settings(_env_file=env_path)
    bot = create_bot(
        telegram_bot_token=settings.telegram_bot_token,
        telegram_proxy_url=settings.telegram_proxy_url,
    )
    try:
        me = await bot.get_me()
        actual_username = str(getattr(me, "username", "") or "").strip()
        if actual_username.casefold() != expected_username.casefold():
            raise RuntimeError("rollback rejected")
        chat = await bot.get_chat(payload["chat_id"])
        if isinstance(payload["chat_id"], int):
            if int(getattr(chat, "id", 0)) != payload["chat_id"]:
                raise RuntimeError("rollback rejected")
        else:
            actual_chat_username = str(getattr(chat, "username", "") or "")
            if actual_chat_username.casefold() != payload["chat_id"][1:].casefold():
                raise RuntimeError("rollback rejected")
        if str(getattr(chat, "title", "") or "") != payload["expected_title"]:
            raise RuntimeError("rollback rejected")
        if enum_value(getattr(chat, "type", None)) != payload["expected_type"]:
            raise RuntimeError("rollback rejected")
        member = await bot.get_chat_member(payload["chat_id"], me.id)
        if enum_value(getattr(member, "status", None)) != "administrator":
            raise RuntimeError("rollback rejected")
        if getattr(member, "can_change_info", False) is not True:
            raise RuntimeError("rollback rejected")
        if metadata["snapshot_status"] == "existing_photo":
            snapshot = state_root / "previous-photo.bin"
            if not snapshot.is_file() or snapshot.is_symlink():
                raise RuntimeError("rollback rejected")
            result = await bot.set_chat_photo(
                chat_id=payload["chat_id"],
                photo=FSInputFile(snapshot),
            )
        elif metadata["snapshot_status"] == "no_existing_photo":
            result = await bot.delete_chat_photo(chat_id=payload["chat_id"])
        else:
            raise RuntimeError("rollback rejected")
        if result is not True:
            raise RuntimeError("rollback rejected")
    finally:
        await bot.session.close()


async def bounded_restore() -> None:
    async with asyncio.timeout(60):
        await restore()


try:
    asyncio.run(bounded_restore())
except Exception:
    raise SystemExit(
        "telegram_group_icon_rollback=failed reason=photo_rollback_failed"
    ) from None
PY
printf 'telegram_group_icon_rollback=pass\n' >"$state_root/rollback.receipt"
chmod 600 "$state_root/rollback.receipt"
SH
  chmod 700 "$state_root/rollback.sh"
}

arm_automatic_rollback() {
  local state_root="$1" timer_base
  timer_base="amn2-group-icon-$(basename "$state_root" | tr -cd 'A-Za-z0-9_.-')"
  printf '%s\n' "$timer_base" >"$state_root/timer-base"
  chmod 600 "$state_root/timer-base"
  systemd-run \
    --quiet \
    --unit "$timer_base" \
    --on-active="${ROLLBACK_TTL_SECONDS}s" \
    --property=Type=oneshot \
    "$state_root/rollback.sh" "$state_root"
  [ "$(systemctl is-active "${timer_base}.timer")" = "active" ] || die
}

cancel_automatic_rollback() {
  local state_root="$1" timer_base service_state
  timer_base="$(tr -d '\r\n' < "$state_root/timer-base")"
  [ ! -e "$state_root/rollback.receipt" ] || die
  service_state="$(systemctl is-active "${timer_base}.service" 2>/dev/null || true)"
  case "$service_state" in inactive|dead|unknown) ;; *) die ;; esac
  systemctl stop "${timer_base}.timer"
  [ "$(systemctl is-active "${timer_base}.timer" 2>/dev/null || true)" = "inactive" ] || die
  service_state="$(systemctl is-active "${timer_base}.service" 2>/dev/null || true)"
  case "$service_state" in inactive|dead|unknown) ;; *) die ;; esac
  [ ! -e "$state_root/rollback.receipt" ] || die
}

disarm_rollback_timer() {
  local state_root="$1" timer_base service_state
  timer_base="$(tr -d '\r\n' < "$state_root/timer-base")"
  systemctl stop "${timer_base}.timer" >/dev/null 2>&1 || true
  [ "$(systemctl is-active "${timer_base}.timer" 2>/dev/null || true)" = "inactive" ] || return 1
  service_state="$(systemctl is-active "${timer_base}.service" 2>/dev/null || true)"
  case "$service_state" in inactive|dead|unknown) ;; *) return 1 ;; esac
}

cleanup_private_state() {
  local state_root="$1"
  rm -f -- \
    "$state_root/previous-photo.bin" \
    "$state_root/no_existing_photo.receipt" \
    "$state_root/photo-state.json" \
    "$state_root/target.json" \
    "$state_root/rollback.sh" \
    "$state_root/rollback.receipt" \
    "$state_root/timer-base" \
    "$state_root/bot.before" \
    "$state_root/bot.after" \
    "$state_root/db.before" \
    "$state_root/db.after" \
    "$state_root/awg.before" \
    "$state_root/awg.after"
  rmdir -- "$state_root"
  [ ! -e "$state_root" ] || die
}

CURRENT_STATE_ROOT=""

rollback_current() {
  [ -n "$CURRENT_STATE_ROOT" ] || return 0
  [ -x "$CURRENT_STATE_ROOT/rollback.sh" ] || return 1
  "$CURRENT_STATE_ROOT/rollback.sh" "$CURRENT_STATE_ROOT" >/dev/null
  [ -f "$CURRENT_STATE_ROOT/rollback.receipt" ] || return 1
}

rollback_and_exit() {
  local exit_code="$1"
  trap - ERR HUP INT TERM
  if disarm_rollback_timer "$CURRENT_STATE_ROOT" && rollback_current; then
    cleanup_private_state "$CURRENT_STATE_ROOT" || true
  else
    printf 'telegram_group_icon_gate=failed reason=photo_rollback_failed\n' >&2
  fi
  exit "$exit_code"
}

common_preflight() {
  require_cmd systemctl
  require_cmd systemd-run
  require_cmd sha256sum
  require_cmd docker
  require_cmd curl
  require_cmd ss
  require_cmd readlink
  require_cmd pgrep
  require_cmd mktemp
  require_cmd cmp
  require_cmd cp
  require_cmd stat
  require_executable_file "$PYTHON_BIN"
  source_contract_check
  require_regular_file "$ENV_PATH"
  require_regular_file "$DB_PATH"
  write_gate_check
  asset_contract_check
  target_contract_check
  bot_snapshot >/dev/null
  web_check
  db_snapshot >/dev/null
  awg_snapshot >/dev/null
}

fingerprint_target() {
  [ -z "$EXPECTED_TARGET_FINGERPRINT" ] || die
  require_executable_file "$PYTHON_BIN"
  target_contract_check
  printf 'telegram_api_called=false\n'
}

preflight() {
  [[ "$EXPECTED_TARGET_FINGERPRINT" =~ ^[A-F0-9]{64}$ ]] || die
  common_preflight >/dev/null
  telegram_action preflight ""
  printf 'preflight=pass\n'
  printf 'messages_sent=0\n'
  printf 'production_awg=untouched\n'
}

apply_group_icon() {
  [[ "$EXPECTED_TARGET_FINGERPRINT" =~ ^[A-F0-9]{64}$ ]] || die
  common_preflight >/dev/null
  [ ! -L "$STATE_BASE" ] || die
  mkdir -p "$STATE_BASE"
  chown root:root "$STATE_BASE"
  chmod 700 "$STATE_BASE"
  [ "$(stat -c '%U:%G:%a' "$STATE_BASE")" = "root:root:700" ] || die

  local state_root
  state_root="$(mktemp -d "$STATE_BASE/run.XXXXXXXX")"
  chown root:root "$state_root"
  chmod 700 "$state_root"
  CURRENT_STATE_ROOT="$state_root"

  cp -- "$TARGET_PATH" "$state_root/target.json"
  chown root:root "$state_root/target.json"
  chmod 600 "$state_root/target.json"
  [ "$(stat -c '%U:%G:%a' "$state_root/target.json")" = "root:root:600" ] || die

  bot_snapshot >"$state_root/bot.before"
  db_snapshot >"$state_root/db.before"
  awg_snapshot >"$state_root/awg.before"
  chmod 600 "$state_root/bot.before" "$state_root/db.before" "$state_root/awg.before"

  telegram_action snapshot "$state_root"
  write_rollback_helper "$state_root"
  arm_automatic_rollback "$state_root"
  trap 'rollback_and_exit 1' ERR
  trap 'rollback_and_exit 129' HUP
  trap 'rollback_and_exit 130' INT
  trap 'rollback_and_exit 143' TERM

  telegram_action apply "$state_root"
  telegram_action postflight "$state_root"

  source_contract_check >/dev/null
  write_gate_check >/dev/null
  asset_contract_check >/dev/null
  target_contract_check >/dev/null
  web_check >/dev/null
  bot_snapshot >"$state_root/bot.after"
  db_snapshot >"$state_root/db.after"
  awg_snapshot >"$state_root/awg.after"
  chmod 600 "$state_root/bot.after" "$state_root/db.after" "$state_root/awg.after"
  cmp -s "$state_root/bot.before" "$state_root/bot.after" || die
  cmp -s "$state_root/db.before" "$state_root/db.after" || die
  cmp -s "$state_root/awg.before" "$state_root/awg.after" || die

  cancel_automatic_rollback "$state_root"
  trap - ERR HUP INT TERM
  cleanup_private_state "$state_root"
  CURRENT_STATE_ROOT=""

  printf 'telegram_group_icon=pass\n'
  printf 'target_chat_fingerprint=%s\n' "$EXPECTED_TARGET_FINGERPRINT"
  printf 'asset_sha256=%s\n' "$ASSET_SHA"
  printf 'set_chat_photo_calls=1\n'
  printf 'postflight_photo_changed=true\n'
  printf 'messages_sent=0\n'
  printf 'bot_service=active_enabled_single_instance_restart_unchanged\n'
  printf 'database=unchanged\n'
  printf 'web=unchanged\n'
  printf 'awg=untouched\n'
  printf 'private_temp_cleanup=pass\n'
}

case "$MODE" in
  fingerprint)
    fingerprint_target
    ;;
  preflight)
    preflight
    ;;
  apply)
    apply_group_icon
    ;;
  *)
    die
    ;;
esac
