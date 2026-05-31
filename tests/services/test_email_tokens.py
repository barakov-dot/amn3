from datetime import datetime
from datetime import timezone

import pytest

from app.services.email_tokens import create_email_token
from app.services.email_tokens import hash_email_token


def test_create_email_token_hashes_raw_token_and_uses_positive_ttl():
    now = datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc)

    token = create_email_token(ttl_minutes=30, now=now)

    assert token.raw_token
    assert token.token_hash == hash_email_token(token.raw_token)
    assert token.token_hash != token.raw_token
    assert token.expires_at == "2026-06-01T12:30:00Z"


@pytest.mark.parametrize("ttl_minutes", [0, -1])
def test_create_email_token_rejects_non_positive_ttl(ttl_minutes: int):
    with pytest.raises(ValueError, match="ttl"):
        create_email_token(ttl_minutes=ttl_minutes)
