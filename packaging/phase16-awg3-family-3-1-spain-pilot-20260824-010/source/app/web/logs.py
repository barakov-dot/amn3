from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

from app.security.redaction import redact

MAX_LOG_TAIL_LINES = 1000


def read_log_tail(path: str | Path, max_lines: Any) -> list[str]:
    try:
        limit = int(max_lines)
    except (OverflowError, TypeError, ValueError):
        return []
    if limit < 1:
        return []
    limit = min(limit, MAX_LOG_TAIL_LINES)

    try:
        with Path(path).open("r", encoding="utf-8", errors="replace") as handle:
            lines = deque(handle, maxlen=limit)
    except (OSError, ValueError):
        return []

    redacted_text = redact("".join(lines))
    return redacted_text.splitlines()
