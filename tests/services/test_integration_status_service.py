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


def test_build_integration_status_reports_controlled_prod_without_write_enablement(tmp_path: Path):
    db_path = tmp_path / "amneziya.sqlite3"
    conn = connect(db_path)
    try:
        initialize_schema(conn)
        repo = Repository(conn)
        _seed_server(repo)

        report = build_integration_status(repo)
    finally:
        conn.close()

    assert report["status"] == "controlled_prod_ready"
    assert report["api_baseline"]["status"] == "controlled_prod_ready"
    assert report["api_baseline"]["stable_head"] == "c8a6363"
    assert report["api_baseline"]["api_web_baseline_head"] == "294803e"
    assert report["api_baseline"]["integration_status_head"] == "7764ae7"
    assert report["api_baseline"]["write_routes_enabled"] is False
    assert report["api_baseline"]["public_api_exposed"] is False
    assert report["remote_operation_gate"]["candidate_head"] == "7281254"
    assert report["remote_operation_gate"]["stable_merge_head"] == "708c98e"
    assert report["remote_operation_gate"]["phase_1"] == "dry_run_only_pass"
    assert report["remote_operation_gate"]["phase_2"] == "verified_live"
    assert report["remote_operation_gate"]["write_operations_enabled"] is False
    assert report["controlled_prod_readiness"]["status"] == "ready"
    assert report["controlled_prod_readiness"]["decision"] == "controlled-prod-ready"
    assert report["controlled_prod_readiness"]["source_overlay_head"] == "c8a6363"
    assert report["controlled_prod_readiness"]["vps_smoke_run_id"] == "20260606T202040Z"
    assert report["controlled_prod_readiness"]["web_admin_access"] == "https_reverse_proxy"
    assert report["controlled_prod_readiness"]["api_listener"] == "127.0.0.1:3040_loopback_only"
    assert report["controlled_prod_readiness"]["vps_apply_enabled_default"] is False
    assert report["local_read_only_extension"]["head"] == "62ff184"
    assert report["local_read_only_extension"]["status"] == "requires_fresh_vps_smoke"
    assert report["aggregate_state"]["servers"] == 1
    assert "new live peer apply/revoke without separate operator confirmation" in report["blocked_lanes"]
    assert "/api/clients write CRUD" in report["blocked_lanes"]
    assert report["next_gate"] == "VPS smoke current read-only head before source overlay update"


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


def test_controlled_prod_runbook_reference_exists(tmp_path: Path):
    db_path = tmp_path / "amneziya.sqlite3"
    conn = connect(db_path)
    try:
        initialize_schema(conn)
        repo = Repository(conn)
        _seed_server(repo)

        report = build_integration_status(repo)
    finally:
        conn.close()

    runbook_path = Path(report["controlled_prod_readiness"]["runbook"])
    assert runbook_path.exists()


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
