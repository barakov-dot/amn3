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
        r"([\"']?(?:(?:[A-Z0-9_]*"
        r"(?:PASSWORD_HASH|PASSWORD|TOKEN|SECRET|PRIVATE_KEY)"
        r"[A-Z0-9_]*)|TELEGRAM_PROXY_URL|SMTP_USERNAME|external_payment_id)"
        r"[\"']?\s*[:=]\s*)(?:"
        r"([\"'])[\s\S]*?\2"
        r"|[^\s,}]+)",
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
