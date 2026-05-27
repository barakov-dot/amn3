from aiogram import Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message

from app.bot.handlers import (
    handle_admin_approve,
    handle_admin_pending,
    handle_admin_resend_config,
    handle_admin_reset_template,
    handle_admin_template,
    handle_config_request,
    handle_my_traffic,
    handle_request_config_prompt,
    handle_start,
)
from app.bot.ux import (
    ADMIN_APPROVE_PREFIX,
    ADMIN_PENDING_CALLBACK,
    ADMIN_RESEND_PREFIX,
    ADMIN_TEMPLATE_RESET_CALLBACK,
    ADMIN_TEMPLATES_CALLBACK,
    MY_TRAFFIC_CALLBACK,
    REQUEST_CONFIG_PREFIX,
)


def create_dispatcher(*, workflow=None) -> Dispatcher:
    router = Router()

    @router.message(CommandStart())
    async def start(message: Message) -> None:
        if workflow is None:
            await message.answer("Amneziya VPN")
            return
        await handle_start(message, workflow=workflow)

    @router.callback_query(F.data == REQUEST_CONFIG_PREFIX)
    async def request_config(callback: CallbackQuery) -> None:
        await handle_request_config_prompt(callback)

    @router.callback_query(F.data.startswith(f"{REQUEST_CONFIG_PREFIX}:"))
    async def request_config_version(callback: CallbackQuery) -> None:
        await handle_config_request(callback, workflow=workflow)

    @router.callback_query(F.data == MY_TRAFFIC_CALLBACK)
    async def my_traffic(callback: CallbackQuery) -> None:
        await handle_my_traffic(callback, workflow=workflow)

    @router.callback_query(F.data == ADMIN_PENDING_CALLBACK)
    async def admin_pending(callback: CallbackQuery) -> None:
        await handle_admin_pending(callback, workflow=workflow)

    @router.callback_query(F.data == ADMIN_TEMPLATES_CALLBACK)
    async def admin_template(callback: CallbackQuery) -> None:
        await handle_admin_template(callback, workflow=workflow)

    @router.callback_query(F.data == ADMIN_TEMPLATE_RESET_CALLBACK)
    async def admin_template_reset(callback: CallbackQuery) -> None:
        await handle_admin_reset_template(callback, workflow=workflow)

    @router.callback_query(F.data.startswith(f"{ADMIN_RESEND_PREFIX}:"))
    async def admin_resend(callback: CallbackQuery) -> None:
        await handle_admin_resend_config(callback, workflow=workflow)

    @router.callback_query(F.data.startswith(f"{ADMIN_APPROVE_PREFIX}:"))
    async def admin_approve(callback: CallbackQuery) -> None:
        await handle_admin_approve(callback, workflow=workflow)

    dispatcher = Dispatcher()
    dispatcher["workflow"] = workflow
    dispatcher.include_router(router)
    return dispatcher
