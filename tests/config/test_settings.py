import pytest
from pydantic import ValidationError

from app.config.settings import Settings


def test_settings_requires_app_secret_key_in_normal_mode():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            telegram_bot_token="CHANGE_ME",
            admin_telegram_ids="123",
            app_secret_key="",
        )


def test_settings_requires_telegram_bot_token():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            telegram_bot_token="",
            admin_telegram_ids="123",
            app_secret_key="test-secret",
        )


def test_settings_rejects_vpn_port_min_above_valid_range():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            telegram_bot_token="CHANGE_ME",
            app_secret_key="test-secret",
            vpn_port_min=70000,
        )


def test_settings_rejects_vpn_port_min_greater_than_max():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            telegram_bot_token="CHANGE_ME",
            app_secret_key="test-secret",
            vpn_port_min=40000,
            vpn_port_max=30000,
        )


def test_settings_parses_admin_ids_and_notice_days():
    settings = Settings(
        _env_file=None,
        telegram_bot_token="CHANGE_ME",
        admin_telegram_ids="123,456",
        app_secret_key="test-secret",
        expiration_notice_days="7,5,3,1",
    )

    assert settings.admin_ids == [123, 456]
    assert settings.notice_days == [7, 5, 3, 1]
    assert settings.default_vpn_network_cidr == "10.8.0.0/24"


def test_settings_parses_control_panel_auth_methods():
    settings = Settings(
        _env_file=None,
        telegram_bot_token="CHANGE_ME",
        admin_telegram_ids="123",
        app_secret_key="test-secret",
        control_panel_auth_methods="password,key",
        control_panel_admin_username="root-admin",
        control_panel_public_key_path="/etc/amneziya/admin.pub",
    )

    assert settings.panel_auth_methods == ["password", "key"]
    assert settings.control_panel_admin_username == "root-admin"
    assert settings.control_panel_public_key_path == "/etc/amneziya/admin.pub"


def test_settings_reads_vps_ssh_password_from_env_settings():
    settings = Settings(
        _env_file=None,
        telegram_bot_token="CHANGE_ME",
        app_secret_key="test-secret",
        vps_ssh_password="secret-password",
    )

    assert settings.vps_ssh_password == "secret-password"


def test_settings_rejects_unknown_control_panel_auth_method():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            telegram_bot_token="CHANGE_ME",
            app_secret_key="test-secret",
            control_panel_auth_methods="password,magic",
        )
