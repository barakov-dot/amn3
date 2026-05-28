import asyncio
from types import SimpleNamespace

import pytest

from app.cli import build_parser
from app.main import check_bot_network
from app.main import telegram_network_error_message


def test_cli_accepts_bot_check_network_command():
    parser = build_parser()

    args = parser.parse_args(["bot", "check-network"])

    assert args.command == "bot"
    assert args.bot_command == "check-network"


def test_check_bot_network_reports_bot_identity_and_closes_session():
    class FakeSession:
        def __init__(self):
            self.closed = False

        async def close(self):
            self.closed = True

    class FakeBot:
        def __init__(self):
            self.session = FakeSession()

        async def get_me(self):
            return SimpleNamespace(username="amn_test_bot", id=123)

    fake_bot = FakeBot()

    result = asyncio.run(
        check_bot_network(
            telegram_bot_token="123:abc",
            telegram_proxy_url="socks5://127.0.0.1:1080",
            bot_factory=lambda **_: fake_bot,
        )
    )

    assert "Telegram API: ok" in result
    assert "Bot: @amn_test_bot" in result
    assert "Proxy: enabled" in result
    assert fake_bot.session.closed is True


def test_check_bot_network_raises_actionable_error_on_network_failure():
    class FakeSession:
        async def close(self):
            pass

    class FakeBot:
        session = FakeSession()

        async def get_me(self):
            raise TimeoutError("request timeout")

    with pytest.raises(RuntimeError) as exc_info:
        asyncio.run(
            check_bot_network(
                telegram_bot_token="123:abc",
                telegram_proxy_url="socks5://proxy-user:proxy-pass@example.com:1080",
                bot_factory=lambda **_: FakeBot(),
            )
        )

    message = str(exc_info.value)
    assert "Telegram API network check failed" in message
    assert "TELEGRAM_PROXY_URL" in message
    assert "curl --socks5-hostname" in message
    assert "proxy-user:proxy-pass@example.com:1080" not in message


def test_telegram_network_error_message_includes_direct_and_proxy_hints():
    direct_message = telegram_network_error_message("")
    proxy_message = telegram_network_error_message("socks5://127.0.0.1:1080")

    assert "curl -I https://api.telegram.org" in direct_message
    assert "TELEGRAM_PROXY_URL" in direct_message
    assert "curl --socks5-hostname 127.0.0.1:1080 -I https://api.telegram.org" in proxy_message
