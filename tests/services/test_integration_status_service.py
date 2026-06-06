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


def test_build_integration_status_reports_vps_smoked_gate_without_write_enablement(tmp_path: Path):
    db_path = tmp_path / "amneziya.sqlite3"
    conn = connect(db_path)
    try:
        initialize_schema(conn)
        repo = Repository(conn)
        _seed_server(repo)

        report = build_integration_status(repo)
    finally:
        conn.close()

    assert report["status"] == "read_only_vps_smoked"
    assert report["api_baseline"]["status"] == "verified_read_only"
    assert report["api_baseline"]["stable_head"] == "1a193b9"
    assert report["api_baseline"]["api_web_baseline_head"] == "294803e"
    assert report["api_baseline"]["integration_status_head"] == "7764ae7"
    assert report["api_baseline"]["write_routes_enabled"] is False
    assert report["remote_operation_gate"]["candidate_head"] == "7281254"
    assert report["remote_operation_gate"]["stable_merge_head"] == "708c98e"
    assert report["remote_operation_gate"]["phase_1"] == "dry_run_only_pass"
    assert report["remote_operation_gate"]["phase_2"] == "verified_live"
    assert report["remote_operation_gate"]["write_operations_enabled"] is False
    assert report["controlled_prod_readiness"] == {
        "status": "runbook_published",
        "decision": "pending_operator_evidence",
        "runbook": "docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md",
    }
    assert report["aggregate_state"]["servers"] == 1
    assert "new live peer apply/revoke without separate operator confirmation" in report["blocked_lanes"]
    assert "/api/clients write CRUD" in report["blocked_lanes"]
    assert report["next_gate"] == "operator-only controlled prod readiness checklist"


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
