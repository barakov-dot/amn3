import asyncio
from pathlib import Path

from aiogram import Bot

from app.bot import create_dispatcher
from app.bot.workflows import BotWorkflow
from app.config import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.security.crypto import SecretBox
from app.server.peer_apply import ServerConfigPeerApplier
from app.server_config.loader import load_server_config, select_server
from app.services.access import AccessService


async def run() -> None:
    settings = Settings()
    workflow = create_workflow(
        database_path=settings.database_path,
        app_secret_key=settings.app_secret_key,
        admin_telegram_ids=set(settings.admin_ids),
        default_vpn_network_cidr=settings.default_vpn_network_cidr,
        max_devices_per_user=settings.max_devices_per_user,
        default_plan_days=settings.default_plan_days,
        vps_apply_enabled=settings.vps_apply_enabled,
        server_config_path=settings.server_config_path,
        server_name=settings.server_name,
    )
    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = create_dispatcher(workflow=workflow)
    await dispatcher.start_polling(bot)


def create_workflow(
    *,
    database_path: str | Path,
    app_secret_key: str,
    admin_telegram_ids: set[int],
    default_vpn_network_cidr: str,
    max_devices_per_user: int,
    default_plan_days: int,
    vps_apply_enabled: bool = False,
    server_config_path: str | Path = "servers.yml",
    server_name: str = "debian-vps-1",
) -> BotWorkflow:
    conn = connect(database_path)
    initialize_schema(conn)
    repo = Repository(conn)
    repo.seed_default_plans()
    default_server_id = repo.ensure_default_server(
        name="local",
        network_cidr=default_vpn_network_cidr,
    )
    peer_applier = None
    if vps_apply_enabled:
        server_config = select_server(load_server_config(server_config_path), server_name)
        peer_applier = ServerConfigPeerApplier(server_config)

    access_service = AccessService(
        repo=repo,
        secret_box=SecretBox.from_app_secret(app_secret_key),
        max_devices_per_user=max_devices_per_user,
        duration_days=default_plan_days,
        peer_applier=peer_applier,
    )
    secret_box = SecretBox.from_app_secret(app_secret_key)
    workflow = BotWorkflow(
        repo=repo,
        admin_telegram_ids=admin_telegram_ids,
        access_service=access_service,
        default_server_id=default_server_id,
        secret_box=secret_box,
    )
    return workflow


if __name__ == "__main__":
    asyncio.run(run())
