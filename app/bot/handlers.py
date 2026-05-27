from __future__ import annotations

from app.bot.ux import (
    ADMIN_APPROVE_PREFIX,
    ADMIN_PENDING_CALLBACK,
    MY_TRAFFIC_CALLBACK,
    REQUEST_CONFIG_PREFIX,
    build_config_version_keyboard,
    build_admin_order_keyboard,
    build_main_menu,
    parse_admin_approve_callback,
    parse_config_version_callback,
    render_admin_pending_orders,
    render_config_version_prompt,
    render_start_text,
    render_user_traffic,
)


async def handle_start(message, *, workflow) -> None:
    user = message.from_user
    await message.answer(
        render_start_text(
            first_name=user.first_name,
            is_admin=workflow.is_admin(int(user.id)),
        ),
        reply_markup=build_main_menu(is_admin=workflow.is_admin(int(user.id))),
    )


async def handle_request_config_prompt(callback) -> None:
    await callback.message.answer(
        render_config_version_prompt(),
        reply_markup=build_config_version_keyboard(prefix=REQUEST_CONFIG_PREFIX),
    )
    await callback.answer()


async def handle_config_request(callback, *, workflow) -> None:
    config_version = parse_config_version_callback(
        str(callback.data),
        prefix=REQUEST_CONFIG_PREFIX,
    )
    if config_version is None:
        await callback.message.answer("Unknown config request.")
        await callback.answer()
        return

    user = callback.from_user
    result = workflow.request_access(
        telegram_id=int(user.id),
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        config_version=config_version,
    )
    await callback.message.answer(result.text)
    await callback.answer()


async def handle_my_traffic(callback, *, workflow) -> None:
    views = workflow.build_user_traffic_views(telegram_id=int(callback.from_user.id))
    await callback.message.answer(render_user_traffic(views))
    await callback.answer()


async def handle_admin_pending(callback, *, workflow) -> None:
    admin_telegram_id = int(callback.from_user.id)
    if not workflow.is_admin(admin_telegram_id):
        await callback.message.answer("Admin access required.")
        await callback.answer()
        return

    orders = workflow.list_pending_orders(admin_telegram_id=admin_telegram_id)
    await callback.message.answer(render_admin_pending_orders(orders))
    for order in orders:
        await callback.message.answer(
            f"Order #{order['id']}",
            reply_markup=build_admin_order_keyboard(order_id=int(order["id"])),
        )
    await callback.answer()


async def handle_admin_approve(callback, *, workflow) -> None:
    admin_telegram_id = int(callback.from_user.id)
    parsed = parse_admin_approve_callback(str(callback.data))
    if parsed is None:
        await callback.message.answer("Unknown admin approval request.")
        await callback.answer()
        return
    if not workflow.is_admin(admin_telegram_id):
        await callback.message.answer("Admin access required.")
        await callback.answer()
        return

    order_id, config_version = parsed
    result = workflow.approve_order(
        admin_telegram_id=admin_telegram_id,
        order_id=order_id,
        config_version=config_version,
    )
    if result is None:
        await callback.message.answer("Admin access required.")
        await callback.answer()
        return

    await callback.message.answer(result.admin_text)
    await callback.message.answer(result.config_text)
    await callback.answer()


def is_request_config_callback(data: str) -> bool:
    return data == REQUEST_CONFIG_PREFIX


def is_config_version_callback(data: str) -> bool:
    return data.startswith(f"{REQUEST_CONFIG_PREFIX}:")


def is_my_traffic_callback(data: str) -> bool:
    return data == MY_TRAFFIC_CALLBACK


def is_admin_pending_callback(data: str) -> bool:
    return data == ADMIN_PENDING_CALLBACK


def is_admin_approve_callback(data: str) -> bool:
    return data.startswith(f"{ADMIN_APPROVE_PREFIX}:")
