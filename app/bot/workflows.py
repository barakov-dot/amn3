from __future__ import annotations

from dataclasses import dataclass

from app.bot.delivery import (
    CONFIG_READY_TEMPLATE_KEY,
    DEFAULT_CONFIG_READY_TEMPLATE,
    ConfigDeliveryPackage,
    build_config_delivery,
)
from app.bot.ux import render_access_request_created, render_admin_approval, render_user_config_ready
from app.db.repositories import Repository
from app.security.crypto import SecretBox
from app.services.access import AccessService
from app.services.traffic import DeviceTrafficView, build_device_traffic_view
from app.vpn.amneziawg_v2.config import ClientConfigInput
from app.vpn.config_versions import validate_config_version
from app.vpn.config_versions import render_client_config_for_version


@dataclass(frozen=True)
class AccessRequestResult:
    order_id: int
    text: str


@dataclass(frozen=True)
class ApprovalResult:
    device_id: int
    user_telegram_id: int
    admin_text: str
    user_text: str
    config_text: str
    delivery: ConfigDeliveryPackage


@dataclass(frozen=True)
class ResendResult:
    device_id: int
    user_telegram_id: int
    config_text: str
    delivery: ConfigDeliveryPackage


class BotWorkflow:
    def __init__(
        self,
        *,
        repo: Repository,
        admin_telegram_ids: set[int],
        access_service: AccessService | None = None,
        default_server_id: int | None = None,
        secret_box: SecretBox | None = None,
    ) -> None:
        self._repo = repo
        self._admin_telegram_ids = admin_telegram_ids
        self._access_service = access_service
        self._default_server_id = default_server_id
        self._secret_box = secret_box

    def is_admin(self, telegram_id: int) -> bool:
        return telegram_id in self._admin_telegram_ids

    def request_access(
        self,
        *,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        config_version: str,
        plan_id: str | None = None,
    ) -> AccessRequestResult:
        config_version = validate_config_version(config_version)
        plan = self._repo.get_plan(plan_id) if plan_id is not None else None
        user_id = self._repo.upsert_user(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        order_id = self._repo.create_order(
            user_id=user_id,
            plan_id=plan_id,
            payment_mode="free_test",
            requested_config_version=config_version,
        )
        return AccessRequestResult(
            order_id=order_id,
            text=render_access_request_created(
                order_id=order_id,
                config_version=config_version,
                plan_name=str(plan["name"]) if plan is not None else None,
            ),
        )

    def build_user_traffic_views(
        self,
        *,
        telegram_id: int,
        now: str | None = None,
    ) -> list[DeviceTrafficView]:
        user = self._repo.get_user_by_telegram_id(telegram_id)
        if user is None:
            return []
        return [
            build_device_traffic_view(
                device,
                self._repo.get_latest_device_traffic(int(device["id"])),
                now=now,
            )
            for device in self._repo.list_user_devices(int(user["id"]))
        ]

    def build_admin_traffic_views(
        self,
        *,
        admin_telegram_id: int,
        now: str | None = None,
    ) -> list[DeviceTrafficView]:
        if not self.is_admin(admin_telegram_id):
            return []
        return [
            build_device_traffic_view(
                device,
                self._repo.get_latest_device_traffic(int(device["id"])),
                now=now,
            )
            for device in self._repo.list_active_devices_with_users()
        ]

    def list_pending_orders(self, *, admin_telegram_id: int):
        if not self.is_admin(admin_telegram_id):
            return []
        return self._repo.list_pending_orders()

    def approve_order(
        self,
        *,
        admin_telegram_id: int,
        order_id: int,
        config_version: str,
    ) -> ApprovalResult | None:
        if not self.is_admin(admin_telegram_id):
            return None
        if self._access_service is None or self._default_server_id is None:
            raise RuntimeError("Access approval workflow is not configured")

        order = self._repo.get_order(order_id)
        user = self._repo.get_user(int(order["user_id"]))
        result = self._access_service.approve_order(
            order_id,
            self._default_server_id,
            _default_device_name(order_id),
            admin_telegram_id=admin_telegram_id,
            config_version=config_version,
        )
        template_text = self._repo.get_message_template(
            CONFIG_READY_TEMPLATE_KEY,
            default_text=DEFAULT_CONFIG_READY_TEMPLATE,
        )
        delivery = build_config_delivery(
            device_id=result.device_id,
            config_version=config_version,
            config_text=result.config_text,
            template_text=template_text,
        )
        return ApprovalResult(
            device_id=result.device_id,
            user_telegram_id=int(user["telegram_id"]),
            admin_text=render_admin_approval(
                order_id=order_id,
                device_id=result.device_id,
                user_telegram_id=int(user["telegram_id"]),
                config_version=config_version,
            ),
            user_text=render_user_config_ready(config_version=config_version),
            config_text=result.config_text,
            delivery=delivery,
        )

    def get_config_ready_template(self, *, admin_telegram_id: int) -> str | None:
        if not self.is_admin(admin_telegram_id):
            return None
        return self._repo.get_message_template(
            CONFIG_READY_TEMPLATE_KEY,
            default_text=DEFAULT_CONFIG_READY_TEMPLATE,
        )

    def set_config_ready_template(self, *, admin_telegram_id: int, text: str) -> bool:
        if not self.is_admin(admin_telegram_id):
            return False
        self._repo.set_message_template(CONFIG_READY_TEMPLATE_KEY, text)
        return True

    def reset_config_ready_template(self, *, admin_telegram_id: int) -> bool:
        if not self.is_admin(admin_telegram_id):
            return False
        self._repo.set_message_template(
            CONFIG_READY_TEMPLATE_KEY,
            DEFAULT_CONFIG_READY_TEMPLATE,
        )
        return True

    def build_resend_delivery(
        self,
        *,
        admin_telegram_id: int,
        device_id: int,
    ) -> ResendResult | None:
        if not self.is_admin(admin_telegram_id):
            return None
        if self._secret_box is None:
            raise RuntimeError("Config resend workflow is not configured")

        device = self._repo.get_device(device_id)
        user = self._repo.get_user(int(device["user_id"]))
        server = self._repo.get_server(int(device["server_id"]))
        private_key = self._secret_box.decrypt_text(device["peer_private_key_encrypted"])
        preshared_key = self._secret_box.decrypt_text(device["preshared_key_encrypted"])
        config_version = str(device["config_version"])
        config_text = render_client_config_for_version(
            ClientConfigInput(
                private_key=private_key,
                address=f"{device['vpn_ip']}/32",
                dns="1.1.1.1",
                server_public_key=str(server["server_public_key"]),
                preshared_key=preshared_key,
                endpoint=f"{server['endpoint_host']}:{server['vpn_port']}",
                allowed_ips="0.0.0.0/0",
                persistent_keepalive=25,
                jc=4,
                jmin=40,
                jmax=70,
                s1=0,
                s2=0,
                h1=1,
                h2=2,
                h3=3,
                h4=4,
            ),
            config_version,
        )
        template_text = self._repo.get_message_template(
            CONFIG_READY_TEMPLATE_KEY,
            default_text=DEFAULT_CONFIG_READY_TEMPLATE,
        )
        delivery = build_config_delivery(
            device_id=device_id,
            config_version=config_version,
            config_text=config_text,
            template_text=template_text,
        )
        return ResendResult(
            device_id=device_id,
            user_telegram_id=int(user["telegram_id"]),
            config_text=config_text,
            delivery=delivery,
        )


def _default_device_name(order_id: int) -> str:
    return f"device-{order_id}"
