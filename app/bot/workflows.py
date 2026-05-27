from __future__ import annotations

from dataclasses import dataclass

from app.bot.ux import render_access_request_created
from app.db.repositories import Repository
from app.services.traffic import DeviceTrafficView, build_device_traffic_view
from app.vpn.config_versions import validate_config_version


@dataclass(frozen=True)
class AccessRequestResult:
    order_id: int
    text: str


class BotWorkflow:
    def __init__(self, *, repo: Repository, admin_telegram_ids: set[int]) -> None:
        self._repo = repo
        self._admin_telegram_ids = admin_telegram_ids

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
    ) -> AccessRequestResult:
        config_version = validate_config_version(config_version)
        user_id = self._repo.upsert_user(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        order_id = self._repo.create_order(
            user_id=user_id,
            plan_id=None,
            payment_mode="free_test",
            requested_config_version=config_version,
        )
        return AccessRequestResult(
            order_id=order_id,
            text=render_access_request_created(
                order_id=order_id,
                config_version=config_version,
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
