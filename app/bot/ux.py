from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timezone

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.services.traffic import DeviceTrafficView
from app.vpn.config_versions import SUPPORTED_CONFIG_VERSIONS


REQUEST_CONFIG_PREFIX = "user:request_config"
REQUEST_PLAN_PREFIX = "user:request_plan"
MY_TARIFF_CALLBACK = "user:tariff"
MY_TRAFFIC_CALLBACK = "user:traffic"
MY_DEVICES_CALLBACK = "user:devices"
USER_RESEND_PREFIX = "user:resend"
USER_REVOKE_PREFIX = "user:revoke"
USER_REVOKE_CONFIRM_PREFIX = "user:revoke_confirm"
USER_RESET_DEVICES_CALLBACK = "user:reset_devices"
USER_RESET_DEVICES_CONFIRM_CALLBACK = "user:reset_devices_confirm"
ADMIN_PENDING_CALLBACK = "admin:pending"
ADMIN_TRAFFIC_CALLBACK = "admin:traffic"
ADMIN_TEMPLATES_CALLBACK = "admin:templates"
ADMIN_USERS_CALLBACK = "admin:users"
ADMIN_TEMPLATE_RESET_CALLBACK = "admin:template:reset"
ADMIN_APPROVE_PREFIX = "admin:approve"
ADMIN_RESEND_PREFIX = "admin:resend"

VERSION_LABELS = {
    "amneziawg_v1_5": "AmneziaWG 1.5",
    "amneziawg_v2": "AmneziaWG 2.0",
}


def build_main_menu(*, is_admin: bool) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text="Request config",
                callback_data=REQUEST_CONFIG_PREFIX,
            )
        ],
        [
            InlineKeyboardButton(
                text="My tariff",
                callback_data=MY_TARIFF_CALLBACK,
            )
        ],
        [
            InlineKeyboardButton(
                text="My traffic",
                callback_data=MY_TRAFFIC_CALLBACK,
            )
        ],
        [
            InlineKeyboardButton(
                text="My devices",
                callback_data=MY_DEVICES_CALLBACK,
            )
        ],
    ]
    if is_admin:
        rows.append(
            [
                InlineKeyboardButton(
                    text="Admin",
                    callback_data=ADMIN_PENDING_CALLBACK,
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_config_version_keyboard(*, prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=VERSION_LABELS[version],
                    callback_data=f"{prefix}:{version}",
                )
            ]
            for version in SUPPORTED_CONFIG_VERSIONS
        ]
    )


def build_plan_keyboard(
    *,
    config_version: str,
    plans: Iterable[Mapping[str, object]],
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=str(plan["name"]),
                    callback_data=f"{REQUEST_PLAN_PREFIX}:{config_version}:{plan['id']}",
                )
            ]
            for plan in plans
        ]
    )


def build_admin_order_keyboard(*, order_id: int) -> InlineKeyboardMarkup:
    prefix = f"{ADMIN_APPROVE_PREFIX}:{order_id}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Approve: {VERSION_LABELS[version]}",
                    callback_data=f"{prefix}:{version}",
                )
            ]
            for version in SUPPORTED_CONFIG_VERSIONS
        ]
    )


def build_admin_resend_keyboard(*, device_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Resend config",
                    callback_data=f"{ADMIN_RESEND_PREFIX}:{device_id}",
                )
            ]
        ]
    )


def build_user_device_keyboard(*, device_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Resend config",
                    callback_data=f"{USER_RESEND_PREFIX}:{device_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Delete device",
                    callback_data=f"{USER_REVOKE_PREFIX}:{device_id}",
                )
            ],
        ]
    )


def build_user_devices_reset_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Reset all devices",
                    callback_data=USER_RESET_DEVICES_CALLBACK,
                )
            ]
        ]
    )


def build_user_revoke_confirm_keyboard(*, device_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Confirm delete",
                    callback_data=f"{USER_REVOKE_CONFIRM_PREFIX}:{device_id}",
                )
            ]
        ]
    )


def build_user_reset_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Confirm reset",
                    callback_data=USER_RESET_DEVICES_CONFIRM_CALLBACK,
                )
            ]
        ]
    )


def build_admin_navigation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Pending orders",
                    callback_data=ADMIN_PENDING_CALLBACK,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Traffic",
                    callback_data=ADMIN_TRAFFIC_CALLBACK,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Templates",
                    callback_data=ADMIN_TEMPLATES_CALLBACK,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Users",
                    callback_data=ADMIN_USERS_CALLBACK,
                )
            ],
        ]
    )


def render_start_text(*, first_name: str | None, is_admin: bool) -> str:
    greeting = f"Hello, {first_name}." if first_name else "Hello."
    role = "Admin mode is available." if is_admin else "User mode is available."
    return f"{greeting}\n{role}\nChoose an action."


def render_config_version_prompt() -> str:
    return "Choose the AmneziaWG config version for this device."


def render_plan_prompt(*, config_version: str) -> str:
    return f"Choose tariff for {_version_label(config_version)}."


def render_access_request_created(
    *,
    order_id: int,
    config_version: str,
    plan_name: str | None = None,
) -> str:
    text = (
        f"Access request #{order_id} was created.\n"
        f"Requested config: {_version_label(config_version)}.\n"
    )
    if plan_name is not None:
        text += f"Plan: {plan_name}.\n"
    return text + "An admin can approve it from the admin menu."


def render_my_tariff(devices: Iterable[Mapping[str, object]], *, now: str) -> str:
    lines = ["My tariff"]
    has_devices = False
    for device in devices:
        has_devices = True
        duration_days = int(device["duration_days"])
        expires_at = str(device["expires_at"]) if device["expires_at"] is not None else None
        lines.extend(
            [
                "",
                str(device["name"]),
                f"Status: {device['status']}",
                f"Tariff: {duration_days} days",
                f"Expires: {expires_at or 'unknown'}",
                f"Days left: {_days_left(expires_at, now) if expires_at else 'unknown'}",
            ]
        )
    if not has_devices:
        lines.append("No active tariff yet.")
    return "\n".join(lines)


def render_my_devices(devices: Iterable[Mapping[str, object]], *, now: str) -> str:
    lines = ["My devices"]
    has_devices = False
    for device in devices:
        has_devices = True
        expires_at = str(device["expires_at"]) if device["expires_at"] is not None else None
        connected = bool(device.get("first_connected_at") or device.get("last_connected_at"))
        lines.extend(
            [
                "",
                f"#{device['id']} {device['name']}",
                f"Config: {_version_label(str(device['config_version']))}",
                f"Status: {device['status']}",
                f"Tariff: {int(device['duration_days'])} days",
                f"Days left: {_days_left(expires_at, now) if expires_at else 'unknown'}",
                f"Connected: {'yes' if connected else 'no'}",
            ]
        )
    if not has_devices:
        lines.append("No active devices yet.")
    return "\n".join(lines)


def render_admin_template(template_text: str) -> tuple[str, InlineKeyboardMarkup]:
    text = (
        "Config ready template\n\n"
        f"{template_text}\n\n"
        "Edit support is handled through the template workflow; reset is available below."
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Reset template",
                    callback_data=ADMIN_TEMPLATE_RESET_CALLBACK,
                )
            ]
        ]
    )
    return text, keyboard


def _days_left(expires_at: str, now: str) -> int:
    expires_dt = _parse_datetime(expires_at)
    now_dt = _parse_datetime(now)
    seconds_left = (expires_dt - now_dt).total_seconds()
    if seconds_left <= 0:
        return 0
    return int((seconds_left + 86399) // 86400)


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def render_admin_approval(
    *,
    order_id: int,
    device_id: int,
    user_telegram_id: int,
    config_version: str,
) -> str:
    return (
        f"Access request #{order_id} approved.\n"
        f"Created device #{device_id} for telegram_id={user_telegram_id}.\n"
        f"Config: {_version_label(config_version)}."
    )


def render_user_config_ready(*, config_version: str) -> str:
    return f"Your {_version_label(config_version)} VPN config is ready."


def render_user_traffic(views: Iterable[DeviceTrafficView]) -> str:
    lines = ["Your traffic"]
    has_devices = False
    for view in views:
        has_devices = True
        lines.extend(_render_device_traffic_lines(view))
    if not has_devices:
        lines.append("No active devices yet.")
    return "\n".join(lines)


def render_admin_pending_orders(orders: Iterable[Mapping[str, object]]) -> str:
    lines = ["Pending orders"]
    has_orders = False
    for order in orders:
        has_orders = True
        lines.append(
            "#"
            f"{order['id']}: "
            f"{_format_user_identity(order)} "
            f"({order['status']}, {order['created_at']})"
        )
    if not has_orders:
        lines.append("No pending orders.")
    return "\n".join(lines)


def render_admin_traffic(
    views: Iterable[DeviceTrafficView],
) -> tuple[str, InlineKeyboardMarkup]:
    lines = ["Admin traffic"]
    has_devices = False
    for view in views:
        has_devices = True
        lines.extend(_render_device_traffic_lines(view))
    if not has_devices:
        lines.append("No active devices yet.")
    return "\n".join(lines), build_admin_navigation_keyboard()


def render_admin_users(
    users: Iterable[Mapping[str, object]],
) -> tuple[str, InlineKeyboardMarkup]:
    lines = ["Admin users"]
    has_users = False
    for user in users:
        has_users = True
        lines.extend(
            [
                "",
                _format_user_identity(user),
                f"status: {user['status']}",
                f"admin: {'yes' if int(user['is_admin']) == 1 else 'no'}",
                f"active devices: {int(user['active_device_count'])}",
                f"total devices: {int(user['total_device_count'])}",
            ]
        )
    if not has_users:
        lines.append("No users yet.")
    return "\n".join(lines), build_admin_navigation_keyboard()


def parse_config_version_callback(data: str, *, prefix: str) -> str | None:
    marker = f"{prefix}:"
    if not data.startswith(marker):
        return None
    return data.removeprefix(marker)


def parse_admin_approve_callback(data: str) -> tuple[int, str] | None:
    marker = f"{ADMIN_APPROVE_PREFIX}:"
    if not data.startswith(marker):
        return None
    parts = data.removeprefix(marker).split(":", maxsplit=1)
    if len(parts) != 2:
        return None
    return int(parts[0]), parts[1]


def _render_device_traffic_lines(view: DeviceTrafficView) -> list[str]:
    lines = [
        "",
        f"{view.device_name} ({_version_label(view.config_version)})",
        f"Status: {view.status}",
        f"Connected: {'yes' if getattr(view, 'is_connected', False) else 'no'}",
    ]
    if not view.is_available:
        lines.append("No traffic data yet.")
        return lines

    lines.extend(
        [
            f"Received: {view.rx}",
            f"Sent: {view.tx}",
            f"Total: {view.total}",
            f"Updated: {view.collected_at}",
        ]
    )
    if view.is_stale:
        lines.append("Traffic data may be stale.")
    return lines


def _format_user_identity(row: Mapping[str, object]) -> str:
    username = row.get("username")
    if username:
        return f"@{username}"
    first_name = row.get("first_name")
    last_name = row.get("last_name")
    full_name = " ".join(str(part) for part in (first_name, last_name) if part)
    if full_name:
        return full_name
    return f"telegram_id={row['telegram_id']}"


def _version_label(config_version: str) -> str:
    return VERSION_LABELS.get(config_version, config_version)
