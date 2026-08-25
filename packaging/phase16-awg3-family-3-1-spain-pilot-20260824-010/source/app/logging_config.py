from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.security.redaction import redact


class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        rendered = super().format(record)
        return redact(rendered)


def configure_logging(
    *,
    enabled: bool,
    level: str,
    log_path: str | Path,
) -> logging.Logger:
    logger = logging.getLogger("amneziya")
    logger.setLevel(getattr(logging, level.strip().upper()))
    for handler in logger.handlers:
        handler.close()
    logger.handlers.clear()
    logger.propagate = False

    formatter = RedactingFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    if enabled:
        path = Path(log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            path,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
