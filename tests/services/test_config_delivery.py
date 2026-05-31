from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.security.crypto import SecretBox
from app.services.config_delivery import build_device_config_delivery
import app.vpn.amneziawg_v2.config as awg_config


def test_device_config_delivery_uses_client_config_defaults(tmp_path):
    conn = connect(tmp_path / "delivery.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    secret_box = SecretBox.from_app_secret("test-secret-for-config-delivery-123456")
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    device_id = repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="phone",
        duration_days=7,
        vpn_ip="10.8.0.2",
        peer_public_key="client-public",
        peer_private_key_encrypted=secret_box.encrypt_text("client-private"),
        preshared_key_encrypted=secret_box.encrypt_text("client-psk"),
        config_version="amneziawg_v2",
    )

    result = build_device_config_delivery(
        repo=repo,
        secret_box=secret_box,
        device=repo.get_device(device_id),
        client_config_defaults=awg_config.ClientConfigDefaults(
            dns="9.9.9.9",
            allowed_ips="10.0.0.0/8",
            persistent_keepalive=15,
            jc=8,
            jmin=12,
            jmax=42,
            s1=11,
            s2=22,
            h1=101,
            h2=202,
            h3=303,
            h4=404,
        ),
    )

    assert "DNS = 9.9.9.9" in result.config_text
    assert "AllowedIPs = 10.0.0.0/8" in result.config_text
    assert "PersistentKeepalive = 15" in result.config_text
    assert "Jc = 8" in result.config_text
    assert "Jmin = 12" in result.config_text
    assert "Jmax = 42" in result.config_text
    assert "S1 = 11" in result.config_text
    assert "S2 = 22" in result.config_text
    assert "H1 = 101" in result.config_text
    assert "H2 = 202" in result.config_text
    assert "H3 = 303" in result.config_text
    assert "H4 = 404" in result.config_text
