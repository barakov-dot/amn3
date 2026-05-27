from aiogram import Dispatcher

from app.bot.main import create_dispatcher


def test_create_dispatcher_returns_dispatcher():
    dispatcher = create_dispatcher()

    assert isinstance(dispatcher, Dispatcher)


def test_create_dispatcher_accepts_workflow_dependency():
    dispatcher = create_dispatcher(workflow=object())

    assert isinstance(dispatcher, Dispatcher)
    assert dispatcher["workflow"] is not None
