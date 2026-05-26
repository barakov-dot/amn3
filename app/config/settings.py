from functools import cached_property

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")
    app_secret_key: str = Field(alias="APP_SECRET_KEY")
    admin_telegram_ids: str = Field(default="", alias="ADMIN_TELEGRAM_IDS")
    access_mode: str = Field(default="free_test", alias="ACCESS_MODE")
    free_test_requires_approval: bool = Field(default=True, alias="FREE_TEST_REQUIRES_APPROVAL")
    default_plan_days: int = Field(default=7, alias="DEFAULT_PLAN_DAYS")
    max_devices_per_user: int = Field(default=5, alias="MAX_DEVICES_PER_USER")
    client_dns: str = Field(default="1.1.1.1", alias="CLIENT_DNS")
    client_allowed_ips: str = Field(default="0.0.0.0/0", alias="CLIENT_ALLOWED_IPS")
    expiration_notice_days: str = Field(default="7,5,3,1", alias="EXPIRATION_NOTICE_DAYS")
    vpn_port_min: int = Field(default=30001, alias="VPN_PORT_MIN")
    vpn_port_max: int = Field(default=65535, alias="VPN_PORT_MAX")
    vpn_server_runtime: str = Field(default="host_systemd", alias="VPN_SERVER_RUNTIME")
    default_vpn_network_cidr: str = Field(default="10.8.0.0/24", alias="DEFAULT_VPN_NETWORK_CIDR")
    database_path: str = Field(default="data/amneziya.sqlite3", alias="DATABASE_PATH")

    @field_validator("telegram_bot_token", "app_secret_key")
    @classmethod
    def require_non_blank_secret(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("required setting cannot be blank")
        return value

    @model_validator(mode="after")
    def validate_vpn_port_bounds(self) -> "Settings":
        if not 1 <= self.vpn_port_min <= 65535:
            raise ValueError("VPN_PORT_MIN must be in 1..65535")
        if not 1 <= self.vpn_port_max <= 65535:
            raise ValueError("VPN_PORT_MAX must be in 1..65535")
        if self.vpn_port_min > self.vpn_port_max:
            raise ValueError("VPN_PORT_MIN must be less than or equal to VPN_PORT_MAX")
        return self

    @cached_property
    def admin_ids(self) -> list[int]:
        if not self.admin_telegram_ids.strip():
            return []
        return [int(part.strip()) for part in self.admin_telegram_ids.split(",") if part.strip()]

    @cached_property
    def notice_days(self) -> list[int]:
        return [int(part.strip()) for part in self.expiration_notice_days.split(",") if part.strip()]
