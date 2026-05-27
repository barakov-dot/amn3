from aiogram import Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message

from app.bot.handlers import (
    handle_admin_pending,
    handle_config_request,
    handle_my_traffic,
    handle_request_config_prompt,
    handle_start,
)
from app.bot.ux import ADMIN_PENDING_CALLBACK, MY_TRAFFIC_CALLBACK, REQUEST_CONFIG_PREFIX


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

    dispatcher = Dispatcher()
    dispatcher["workflow"] = workflow
    dispatcher.include_router(router)
    return dispatcher
