import json
from pathlib import Path

from app.cli import build_parser, run_device_import_external
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema


def test_cli_accepts_device_import_external_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "device",
            "import-external",
            "--db",
            "data/amneziya.sqlite3",
            "--telegram-id",
            "1001",
            "--name",
            "Neobyatnaya-AMNZ-4",
            "--vpn-ip",
            "10.8.0.44",
            "--peer-public-key",
            "external-peer-4",
            "--status",
            "revoked",
            "--revoked-at",
            "2026-06-09T10:00:00Z",
            "--revoke-reason",
            "phase3_test_revoked",
        ]
    )

    assert args.command == "device"
    assert args.device_command == "import-external"
    assert args.telegram_id == 1001
    assert args.name == "Neobyatnaya-AMNZ-4"
    assert args.status == "revoked"


def test_run_device_import_external_creates_safe_external_only_record(tmp_path: Path):
    db_path = tmp_path / "amneziya.sqlite3"

    output = run_device_import_external(
        db_path=db_path,
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
        server_name="local",
        server_network_cidr="10.8.0.0/24",
        name="Neobyatnaya-AMNZ-4",
        duration_days=30,
        vpn_ip="10.8.0.44",
        peer_public_key="external-peer-4",
        config_version="amneziawg_v2",
        status="revoked",
        expires_at=None,
        revoked_at="2026-06-09T10:00:00Z",
        revoke_reason="phase3_test_revoked",
        pretty=True,
    )

    payload = json.loads(output)
    assert payload["device"]["name"] == "Neobyatnaya-AMNZ-4"
    assert payload["device"]["status"] == "revoked"
    assert payload["device"]["config_material_status"] == "external_only"
    assert payload["delivery"]["config_resend_available"] is False
    assert "peer_public_key" not in output
    assert "private" not in output.lower()
    assert "preshared" not in output.lower()

    conn = connect(db_path)
    initialize_schema(conn)
    repo = Repository(conn)
    device = repo.get_device(payload["device"]["id"])
    assert device["name"] == "Neobyatnaya-AMNZ-4"
    assert device["config_material_status"] == "external_only"
