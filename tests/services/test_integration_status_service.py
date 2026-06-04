from __future__ import annotations

from pathlib import Path

from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.services.integration_status import build_integration_status


FORBIDDEN_MARKERS = [
    "PrivateKey",
    "PresharedKey",
    "Authorization",
    "token_hash",
    "vpn://",
    ".conf",
    "root@",
    "docker exec",
    "awg show",
]


def test_build_integration_status_reports_dry_run_gate_without_write_enablement(tmp_path: Path):
    db_path = tmp_path / "amneziya.sqlite3"
    conn = connect(db_path)
    try:
        initialize_schema(conn)
        repo = Repository(conn)
        _seed_server(repo)

        report = build_integration_status(repo)
    finally:
        conn.close()

    assert report["status"] == "dry_run_ready"
    assert report["api_baseline"]["status"] == "verified_read_only"
    assert report["api_baseline"]["stable_head"] == "55a7ed6"
    assert report["api_baseline"]["api_web_baseline_head"] == "294803e"
    assert report["api_baseline"]["write_routes_enabled"] is False
    assert report["remote_operation_gate"]["candidate_head"] == "7281254"
    assert report["remote_operation_gate"]["stable_merge_head"] == "708c98e"
    assert report["remote_operation_gate"]["phase_1"] == "dry_run_only_pass"
    assert report["remote_operation_gate"]["phase_2"] == "not_run"
    assert report["remote_operation_gate"]["write_operations_enabled"] is False
    assert report["aggregate_state"]["servers"] == 1
    assert "live peer apply/revoke" in report["blocked_lanes"]
    assert "/api/clients write CRUD" in report["blocked_lanes"]


def test_build_integration_status_contains_no_secret_or_command_markers(tmp_path: Path):
    db_path = tmp_path / "amneziya.sqlite3"
    conn = connect(db_path)
    try:
        initialize_schema(conn)
        repo = Repository(conn)
        _seed_server(repo)

        report_text = repr(build_integration_status(repo))
    finally:
        conn.close()

    for marker in FORBIDDEN_MARKERS:
        assert marker not in report_text


def _seed_server(repo: Repository) -> None:
    repo.upsert_server_config(
        name="local",
        host="127.0.0.1",
        ssh_port=22,
        endpoint_host="127.0.0.1",
        vpn_port=51820,
        vpn_network_cidr="10.8.1.0/24",
        server_address="10.8.1.1/24",
        server_public_key="public-key",
        runtime="docker",
        firewall="none",
        max_devices=100,
    )
