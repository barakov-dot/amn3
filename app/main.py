import asyncio

from aiogram import Bot

from app.bot import create_dispatcher
from app.config import Settings


async def run() -> None:
    settings = Settings()
    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = create_dispatcher()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
