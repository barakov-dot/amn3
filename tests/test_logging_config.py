import logging

from app.logging_config import configure_logging


def test_configure_logging_writes_redacted_file(tmp_path):
    log_path = tmp_path / "app.log"
    logger = configure_logging(
        enabled=True,
        level="INFO",
        log_path=log_path,
    )

    logger.info("TELEGRAM_PROXY_URL=socks5://user:pass@example.com:1080")

    text = log_path.read_text(encoding="utf-8")
    assert "user:pass@example.com" not in text
    assert "[REDACTED]" in text


def test_configure_logging_can_disable_file_logging(tmp_path):
    log_path = tmp_path / "app.log"
    logger = configure_logging(
        enabled=False,
        level="INFO",
        log_path=log_path,
    )

    logger.info("hello")

    assert not log_path.exists()


def test_configure_logging_strips_level(tmp_path):
    logger = configure_logging(
        enabled=False,
        level=" info ",
        log_path=tmp_path / "app.log",
    )

    assert logger.level == logging.INFO


def test_configure_logging_closes_existing_handlers(tmp_path):
    logger = configure_logging(
        enabled=True,
        level="INFO",
        log_path=tmp_path / "first.log",
    )
    file_handler = next(
        handler
        for handler in logger.handlers
        if isinstance(handler, logging.FileHandler)
    )

    configure_logging(
        enabled=False,
        level="INFO",
        log_path=tmp_path / "second.log",
    )

    assert file_handler.stream is None
