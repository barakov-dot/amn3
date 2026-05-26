from aiogram import Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message


def create_dispatcher() -> Dispatcher:
    router = Router()

    @router.message(CommandStart())
    async def start(message: Message) -> None:
        await message.answer("Amneziya VPN")

    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    return dispatcher
