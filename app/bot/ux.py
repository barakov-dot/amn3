from __future__ import annotations

from collections.abc import Iterable, Mapping

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.services.traffic import DeviceTrafficView
from app.vpn.config_versions import SUPPORTED_CONFIG_VERSIONS


REQUEST_CONFIG_PREFIX = "user:request_config"
MY_TRAFFIC_CALLBACK = "user:traffic"
ADMIN_PENDING_CALLBACK = "admin:pending"
ADMIN_TRAFFIC_CALLBACK = "admin:traffic"
ADMIN_APPROVE_PREFIX = "admin:approve"

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
                text="My traffic",
                callback_data=MY_TRAFFIC_CALLBACK,
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
        ]
    )


def render_start_text(*, first_name: str | None, is_admin: bool) -> str:
    greeting = f"Hello, {first_name}." if first_name else "Hello."
    role = "Admin mode is available." if is_admin else "User mode is available."
    return f"{greeting}\n{role}\nChoose an action."


def render_config_version_prompt() -> str:
    return "Choose the AmneziaWG config version for this device."


def render_access_request_created(*, order_id: int, config_version: str) -> str:
    return (
        f"Access request #{order_id} was created.\n"
        f"Requested config: {_version_label(config_version)}.\n"
        "An admin can approve it from the admin menu."
    )


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
