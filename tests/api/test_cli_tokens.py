import json
from pathlib import Path

from app.cli import build_parser
from app.cli import run_api_token_issue
from app.cli import run_api_token_revoke
from app.db.connection import connect
from app.db.schema import initialize_schema
from app.services.api_tokens import hash_api_token


def test_cli_accepts_api_token_issue_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "api",
            "token",
            "issue",
            "--db",
            "data/amneziya.sqlite3",
            "--name",
            "VPS smoke",
            "--owner-label",
            "ops",
            "--scope",
            "server:read",
            "--scope",
            "metrics:read",
            "--expires-at",
            "2026-06-08T10:00:00+00:00",
        ]
    )

    assert args.command == "api"
    assert args.api_command == "token"
    assert args.api_token_command == "issue"
    assert args.db == "data/amneziya.sqlite3"
    assert args.name == "VPS smoke"
    assert args.owner_label == "ops"
    assert args.scopes == ["server:read", "metrics:read"]
    assert args.expires_at == "2026-06-08T10:00:00+00:00"


def test_cli_accepts_api_token_revoke_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "api",
            "token",
            "revoke",
            "--db",
            "data/amneziya.sqlite3",
            "--token-id",
            "api_token_1",
            "--reason",
            "smoke-complete",
        ]
    )

    assert args.command == "api"
    assert args.api_command == "token"
    assert args.api_token_command == "revoke"
    assert args.db == "data/amneziya.sqlite3"
    assert args.token_id == "api_token_1"
    assert args.reason == "smoke-complete"


def test_run_api_token_issue_stores_hash_and_outputs_raw_token_once(tmp_path: Path):
    db_path = tmp_path / "amneziya.sqlite3"

    result = json.loads(
        run_api_token_issue(
            db_path=db_path,
            name="VPS smoke",
            owner_label="ops",
            scopes=["server:read", "metrics:read"],
            expires_at="2026-06-08T10:00:00+00:00",
            raw_token="raw-api-token",
        )
    )

    assert result == {
        "action": "api_token.issued",
        "token_id": result["token_id"],
        "name": "VPS smoke",
        "owner_label": "ops",
        "scopes": ["metrics:read", "server:read"],
        "expires_at": "2026-06-08T10:00:00+00:00",
        "raw_token_display": "one-time",
        "raw_token": "raw-api-token",
    }
    assert "token_hash" not in result

    conn = connect(db_path)
    try:
        initialize_schema(conn)
        row = conn.execute(
            "SELECT * FROM api_tokens WHERE id = ?",
            (result["token_id"],),
        ).fetchone()
    finally:
        conn.close()

    assert row is not None
    assert row["name"] == "VPS smoke"
    assert row["owner_label"] == "ops"
    assert row["scopes_json"] == '["metrics:read", "server:read"]'
    assert row["expires_at"] == "2026-06-08T10:00:00+00:00"
    assert row["token_hash"] == hash_api_token("raw-api-token")
    assert "raw-api-token" not in str(dict(row))


def test_run_api_token_revoke_marks_token_without_secret_output(tmp_path: Path):
    db_path = tmp_path / "amneziya.sqlite3"
    issue = json.loads(
        run_api_token_issue(
            db_path=db_path,
            name="VPS smoke",
            owner_label="ops",
            scopes=["server:read"],
            expires_at="2026-06-08T10:00:00+00:00",
            raw_token="raw-api-token",
        )
    )

    revoked = json.loads(
        run_api_token_revoke(
            db_path=db_path,
            token_id=issue["token_id"],
            reason="smoke-complete",
            revoked_at="2026-06-01T12:00:00+00:00",
        )
    )
    repeated = json.loads(
        run_api_token_revoke(
            db_path=db_path,
            token_id=issue["token_id"],
            reason="smoke-complete",
            revoked_at="2026-06-01T12:05:00+00:00",
        )
    )

    assert revoked == {
        "action": "api_token.revoked",
        "token_id": issue["token_id"],
        "status": "revoked",
        "reason": "smoke-complete",
        "revoked_at": "2026-06-01T12:00:00+00:00",
        "rotated_from_token_id": None,
    }
    assert repeated["status"] == "already-revoked-or-missing"
    assert "raw-api-token" not in json.dumps(revoked)
    assert "token_hash" not in json.dumps(revoked)

    conn = connect(db_path)
    try:
        initialize_schema(conn)
        row = conn.execute(
            "SELECT revoked_at, revoke_reason FROM api_tokens WHERE id = ?",
            (issue["token_id"],),
        ).fetchone()
    finally:
        conn.close()

    assert row["revoked_at"] == "2026-06-01T12:00:00+00:00"
    assert row["revoke_reason"] == "smoke-complete"
