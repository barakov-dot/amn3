from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.bot.delivery import (
    CONFIG_READY_TEMPLATE_KEY,
    DEFAULT_CONFIG_READY_TEMPLATE,
    ConfigDeliveryPackage,
    build_config_delivery,
)
from app.db.repositories import Repository
from app.security.crypto import SecretBox
from app.vpn.amneziawg_v2.config import ClientConfigDefaults, ClientConfigInput
from app.vpn.config_versions import render_client_config_for_version


@dataclass(frozen=True)
class DeviceConfigDelivery:
    device_id: int
    user_telegram_id: int
    config_text: str
    delivery: ConfigDeliveryPackage


def build_device_config_delivery(
    *,
    repo: Repository,
    secret_box: SecretBox,
    device: Any,
    client_config_template_dir: str | None = None,
    client_dns: str = "8.8.8.8, 8.8.4.4",
    client_allowed_ips: str = "0.0.0.0/0, ::/0",
    client_config_defaults: ClientConfigDefaults | None = None,
) -> DeviceConfigDelivery:
    user = repo.get_user(int(device["user_id"]))
    server = repo.get_server(int(device["server_id"]))
    private_key = secret_box.decrypt_text(device["peer_private_key_encrypted"])
    preshared_key = secret_box.decrypt_text(device["preshared_key_encrypted"])
    config_version = str(device["config_version"])
    defaults = client_config_defaults or ClientConfigDefaults(
        dns=client_dns,
        allowed_ips=client_allowed_ips,
    )
    config_text = render_client_config_for_version(
        ClientConfigInput(
            private_key=private_key,
            address=f"{device['vpn_ip']}/32",
            dns=defaults.dns,
            server_public_key=str(server["server_public_key"]),
            preshared_key=preshared_key,
            endpoint=f"{server['endpoint_host']}:{server['vpn_port']}",
            allowed_ips=defaults.allowed_ips,
            persistent_keepalive=defaults.persistent_keepalive,
            jc=defaults.jc,
            jmin=defaults.jmin,
            jmax=defaults.jmax,
            s1=defaults.s1,
            s2=defaults.s2,
            s3=defaults.s3,
            s4=defaults.s4,
            h1=defaults.h1,
            h2=defaults.h2,
            h3=defaults.h3,
            h4=defaults.h4,
            i1=defaults.i1,
            i2=defaults.i2,
            i3=defaults.i3,
            i4=defaults.i4,
            i5=defaults.i5,
        ),
        config_version,
        template_dir=client_config_template_dir,
    )
    template_text = repo.get_message_template(
        CONFIG_READY_TEMPLATE_KEY,
        default_text=DEFAULT_CONFIG_READY_TEMPLATE,
    )
    delivery = build_config_delivery(
        device_id=int(device["id"]),
        device_name=str(device["name"]),
        config_version=config_version,
        config_text=config_text,
        template_text=template_text,
    )
    return DeviceConfigDelivery(
        device_id=int(device["id"]),
        user_telegram_id=int(user["telegram_id"]),
        config_text=config_text,
        delivery=delivery,
    )
