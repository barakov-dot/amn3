import asyncio

from aiogram import Bot

from app.bot import create_dispatcher
from app.bot.workflows import BotWorkflow
from app.config import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema


async def run() -> None:
    settings = Settings()
    conn = connect(settings.database_path)
    initialize_schema(conn)
    repo = Repository(conn)
    workflow = BotWorkflow(
        repo=repo,
        admin_telegram_ids=set(settings.admin_ids),
    )
    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = create_dispatcher(workflow=workflow)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
