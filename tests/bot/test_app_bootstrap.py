from app.main import create_workflow
from app.services.access import AccessService
from tests.server_config.test_loader import VALID_YAML


def test_create_workflow_wires_access_service_for_admin_approval(tmp_path):
    workflow = create_workflow(
        database_path=tmp_path / "app.sqlite3",
        app_secret_key="app-bootstrap-secret-value-with-more-than-32-chars",
        admin_telegram_ids={9001},
        default_vpn_network_cidr="10.8.0.0/24",
        max_devices_per_user=5,
        default_plan_days=7,
    )

    assert workflow.is_admin(9001) is True
    assert isinstance(workflow._access_service, AccessService)
    assert workflow._default_server_id is not None
    assert [plan["id"] for plan in workflow._repo.list_active_plans()] == [
        "days_3",
        "days_7",
        "days_10",
        "days_14",
        "days_30",
        "days_60",
        "days_90",
        "days_180",
    ]


def test_create_workflow_can_enable_vps_peer_apply_from_server_config(tmp_path):
    server_config_path = tmp_path / "servers.yml"
    server_config_path.write_text(
        VALID_YAML.replace("allowed_ips: 0.0.0.0/0", "allowed_ips: 0.0.0.0/0\n      server_public_key: real-server-public-key"),
        encoding="utf-8",
    )

    workflow = create_workflow(
        database_path=tmp_path / "app.sqlite3",
        app_secret_key="app-bootstrap-secret-value-with-more-than-32-chars",
        admin_telegram_ids={9001},
        default_vpn_network_cidr="10.8.0.0/24",
        max_devices_per_user=5,
        default_plan_days=7,
        vps_apply_enabled=True,
        server_config_path=server_config_path,
        server_name="debian-vps-1",
    )

    server = workflow._repo.get_server(workflow._default_server_id)
    assert workflow._access_service._peer_applier is not None
    assert server["name"] == "debian-vps-1"
    assert server["host"] == "203.0.113.10"
    assert server["endpoint_host"] == "203.0.113.10"
    assert server["vpn_port"] == 30001
    assert server["vpn_network_cidr"] == "10.8.0.0/24"
    assert server["server_address"] == "10.8.0.1"
    assert server["server_public_key"] == "real-server-public-key"
