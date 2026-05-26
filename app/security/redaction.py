import re
from typing import Any


PATTERNS = [
    re.compile(
        r"\[Interface\][\s\S]*?\[Peer\][\s\S]*?(?=\n\s*\n|\Z)",
        re.IGNORECASE,
    ),
    re.compile(r"\[Interface\][\s\S]*?(?=\n\s*\n|\Z)", re.IGNORECASE),
    re.compile(r"(/bot)[^/\s]+", re.IGNORECASE),
    re.compile(
        r"([\"']?(?:TELEGRAM_BOT_TOKEN|APP_SECRET_KEY|external_payment_id)[\"']?\s*[:=]\s*)"
        r"([\"'])?[^\"'\s,}]+([\"'])?",
        re.IGNORECASE,
    ),
    re.compile(
        r"((?:PrivateKey|PresharedKey)\s*[:=]\s*)[^\s]+",
        re.IGNORECASE,
    ),
]


def redact(value: Any) -> str:
    text = str(value)
    for pattern in PATTERNS:
        text = pattern.sub(
            lambda match: f"{match.group(1) if match.lastindex else ''}[REDACTED]",
            text,
        )
    return text
