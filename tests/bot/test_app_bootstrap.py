from app.main import create_workflow
from app.services.access import AccessService


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
