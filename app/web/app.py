from __future__ import annotations

import json
import sqlite3
import re
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi import Form
from fastapi import Request
from fastapi.responses import PlainTextResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from app.config.settings import Settings
from app.bot.delivery import CONFIG_READY_TEMPLATE_KEY, DEFAULT_CONFIG_READY_TEMPLATE
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.repositories import SERVER_STATUSES
from app.db.repositories import USER_STATUSES
from app.db.schema import initialize_schema
from app.security.crypto import SecretBox
from app.security.redaction import redact
from app.server.peer_apply import PeerApplyError
from app.server.peer_apply import ServerConfigPeerApplier
from app.server.ssh import SystemSshClient
from app.server_config.loader import ConfigError
from app.server_config.loader import load_server_config
from app.server_config.loader import select_server
from app.services.config_delivery import build_device_config_delivery
from app.services.email_delivery import EmailDeliveryService
from app.services.email_delivery import EmailSender
from app.services.email_delivery import build_smtp_sender
from app.services.email_tokens import create_email_token
from app.services.email_tokens import hash_email_token
from app.services.email_tokens import utc_now_iso
from app.services.peer_inventory import AwgDumpPeerInventoryCollector
from app.services.peer_inventory import PeerInventoryService
from app.web.auth import check_password
from app.web.auth import generate_csrf_token
from app.web.auth import require_web_admin_config
from app.web.auth import verify_csrf_token
from app.web.logs import read_log_tail
from app.web.server_health import HealthSummary
from app.web.server_health import run_server_health_check
from app.vpn.amneziawg_v2.config import ClientConfigInput
from app.vpn.config_templates import (
    AVAILABLE_CLIENT_CONFIG_PLACEHOLDERS,
    ConfigTemplateError,
    build_vpn_import_link,
    client_config_template_source,
    render_client_config_from_template,
)
from app.vpn.config_versions import SUPPORTED_CONFIG_VERSIONS


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
SESSION_AUTH_KEY = "web_admin_authenticated"
SECRET_CONFIG_LINE_RE = re.compile(
    r"^(\s*(?:PrivateKey|PresharedKey)\s*[:=]\s*).+$",
    re.IGNORECASE | re.MULTILINE,
)

templates = Jinja2Templates(directory=TEMPLATE_DIR)

SETTINGS_SECTIONS = {
    "Core": [
        "telegram_bot_token",
        "telegram_proxy_url",
        "app_secret_key",
        "admin_telegram_ids",
        "access_mode",
        "free_test_requires_approval",
        "default_plan_days",
        "max_devices_per_user",
        "expiration_notice_days",
        "database_path",
    ],
    "Web admin": [
        "web_admin_enabled",
        "web_admin_host",
        "web_admin_port",
        "web_admin_username",
        "web_admin_password_hash",
        "web_admin_session_secret",
        "web_admin_session_cookie_secure",
    ],
    "Logging": [
        "app_log_enabled",
        "app_log_level",
        "app_log_max_lines",
        "app_log_path",
    ],
    "Email": [
        "email_delivery_enabled",
        "smtp_host",
        "smtp_port",
        "smtp_username",
        "smtp_password",
        "smtp_from",
        "smtp_use_tls",
        "email_require_verification",
        "email_recovery_token_ttl_minutes",
        "email_config_attachments_enabled",
    ],
    "VPS": [
        "vps_apply_enabled",
        "vps_ssh_password",
        "server_config_path",
        "server_name",
        "vpn_port_min",
        "vpn_port_max",
        "vpn_server_runtime",
        "default_vpn_network_cidr",
        "client_config_template_dir",
        "client_dns",
        "client_allowed_ips",
    ],
    "Control panel": [
        "control_panel_auth_methods",
        "control_panel_admin_username",
        "control_panel_password_hash",
        "control_panel_public_key_path",
    ],
}

PATH_SETTING_FIELDS = {
    "app_log_path",
    "control_panel_public_key_path",
    "database_path",
    "server_config_path",
    "client_config_template_dir",
}


def create_web_app(
    settings: Settings | None = None,
    *,
    email_sender: EmailSender | None = None,
) -> FastAPI:
    actual_settings = settings or Settings()
    require_web_admin_config(
        password_hash=actual_settings.web_admin_password_hash,
        session_secret=actual_settings.web_admin_session_secret,
    )

    app = FastAPI(title="Amneziya Web Admin")
    app.state.settings = actual_settings
    app.state.email_sender = email_sender or build_smtp_sender(
        host=actual_settings.smtp_host,
        port=actual_settings.smtp_port,
        username=actual_settings.smtp_username,
        password=actual_settings.smtp_password,
        use_tls=actual_settings.smtp_use_tls,
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=actual_settings.web_admin_session_secret,
        same_site="lax",
        https_only=actual_settings.web_admin_session_cookie_secure,
    )
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/login")
    async def login_form(request: Request):
        if _is_authenticated(request):
            return RedirectResponse("/", status_code=303)
        return templates.TemplateResponse(
            request,
            "login.html",
            _template_context(
                request,
                title="Вход",
                error=None,
                username="",
                authenticated=False,
            ),
        )

    @app.post("/login")
    async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        csrf_token: str = Form(""),
    ):
        if not verify_csrf_token(request.session, csrf_token):
            request.session.pop(SESSION_AUTH_KEY, None)
            request.session.pop("web_admin_username", None)
            return templates.TemplateResponse(
                request,
                "login.html",
                _template_context(
                    request,
                    title="Вход",
                    error="Сессия формы устарела. Обновите страницу и попробуйте снова.",
                    username=username,
                    authenticated=False,
                ),
                status_code=400,
            )

        if username == actual_settings.web_admin_username and check_password(
            password,
            actual_settings.web_admin_password_hash,
        ):
            request.session[SESSION_AUTH_KEY] = True
            request.session["web_admin_username"] = actual_settings.web_admin_username
            return RedirectResponse("/", status_code=303)

        request.session.pop(SESSION_AUTH_KEY, None)
        request.session.pop("web_admin_username", None)
        return templates.TemplateResponse(
            request,
            "login.html",
            _template_context(
                request,
                title="Вход",
                error="Неверное имя пользователя или пароль",
                username=username,
                authenticated=False,
            ),
            status_code=200,
        )

    @app.get("/")
    async def dashboard(request: Request):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        dashboard_data = _load_dashboard(actual_settings)
        return templates.TemplateResponse(
            request,
            "dashboard.html",
            _template_context(
                request,
                title="Панель управления",
                authenticated=True,
                **dashboard_data,
            ),
        )

    @app.get("/orders")
    async def orders_index(request: Request):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        orders = _load_orders(actual_settings)
        return templates.TemplateResponse(
            request,
            "orders.html",
            _template_context(
                request,
                title="Orders",
                authenticated=True,
                orders=orders,
            ),
        )

    @app.get("/logs")
    async def logs_index(request: Request):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        log_lines = []
        if actual_settings.app_log_enabled:
            log_lines = read_log_tail(
                actual_settings.app_log_path,
                actual_settings.app_log_max_lines,
            )
        return templates.TemplateResponse(
            request,
            "logs.html",
            _template_context(
                request,
                title="Application logs",
                authenticated=True,
                log_enabled=actual_settings.app_log_enabled,
                log_level=actual_settings.app_log_level,
                log_path=_display_setting_value(
                    "APP_LOG_PATH",
                    actual_settings.app_log_path,
                    is_path=True,
                ),
                log_max_lines=actual_settings.app_log_max_lines,
                log_lines=log_lines,
            ),
        )

    @app.get("/settings")
    async def settings_index(request: Request):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            request,
            "settings.html",
            _template_context(
                request,
                title="Settings",
                authenticated=True,
                settings_sections=_load_settings_sections(actual_settings),
            ),
        )

    @app.get("/config-templates")
    async def config_templates_index(request: Request):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            request,
            "config_templates.html",
            _template_context(
                request,
                title="Config templates",
                authenticated=True,
                template_dir_name=_display_setting_value(
                    "CLIENT_CONFIG_TEMPLATE_DIR",
                    actual_settings.client_config_template_dir,
                    is_path=True,
                ),
                config_templates=_load_client_config_template_views(actual_settings),
                config_placeholders=[
                    f"{{{name}}}" for name in AVAILABLE_CLIENT_CONFIG_PLACEHOLDERS
                ],
                delivery_template={
                    "key": CONFIG_READY_TEMPLATE_KEY,
                    "placeholders": _delivery_template_placeholders(),
                    "preview": DEFAULT_CONFIG_READY_TEMPLATE,
                },
            ),
        )

    @app.get("/users")
    async def users_index(request: Request):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        users = _load_users(actual_settings)
        return templates.TemplateResponse(
            request,
            "users.html",
            _template_context(
                request,
                title="Users",
                authenticated=True,
                users=users,
            ),
        )

    @app.get("/users/new")
    async def new_user_form(request: Request):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            request,
            "user_form.html",
            _template_context(
                request,
                title="New user",
                authenticated=True,
                action_url="/users/new",
                submit_label="Create user",
                user=_blank_user_form(),
                statuses=sorted(USER_STATUSES),
            ),
        )

    @app.post("/users/new")
    async def create_user(
        request: Request,
        telegram_id: int = Form(...),
        username: str = Form(""),
        first_name: str = Form(""),
        last_name: str = Form(""),
        email: str = Form(""),
        status: str = Form("active"),
        is_admin: str | None = Form(None),
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            payload = _user_payload(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                status=status,
                is_admin=is_admin,
            )
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    user_id = repo.create_user_for_admin(**payload)
                    _record_web_user_action(
                        repo,
                        actual_settings,
                        request,
                        action="web_user_create",
                        target_user_id=user_id,
                        metadata={"telegram_id": telegram_id},
                    )
        except (sqlite3.IntegrityError, ValueError) as exc:
            return PlainTextResponse(str(exc), status_code=400)

        return RedirectResponse(f"/users/{user_id}", status_code=303)

    @app.get("/users/{user_id}")
    async def user_detail(request: Request, user_id: int):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        try:
            detail = _load_user_detail(actual_settings, user_id)
        except LookupError:
            return PlainTextResponse("User not found", status_code=404)

        return templates.TemplateResponse(
            request,
            "user_detail.html",
            _template_context(
                request,
                title=f"User {user_id}",
                authenticated=True,
                **detail,
            ),
        )

    @app.post("/users/{user_id}/email/verify/start")
    async def start_email_verification(
        request: Request,
        user_id: int,
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)
        if not actual_settings.email_delivery_enabled:
            return PlainTextResponse("Email delivery is disabled", status_code=400)

        try:
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    user = _row_to_dict(repo.get_user(user_id))
                    email = _required_user_email(user)
                    token = create_email_token(
                        ttl_minutes=actual_settings.email_recovery_token_ttl_minutes,
                    )
                    repo.create_email_recovery_token(
                        user_id=user_id,
                        email=email,
                        token_hash=token.token_hash,
                        purpose="verify_email",
                        expires_at=token.expires_at,
                    )
                    metadata = _email_service(request).send_verification_email(
                        to_address=email,
                        user_id=user_id,
                        token=token.raw_token,
                    )
                    _record_web_user_action(
                        repo,
                        actual_settings,
                        request,
                        action="web_email_verify_start",
                        target_user_id=user_id,
                        metadata=metadata,
                    )
        except LookupError:
            return PlainTextResponse("User not found", status_code=404)
        except ValueError as exc:
            return PlainTextResponse(str(exc), status_code=400)

        return RedirectResponse(f"/users/{user_id}", status_code=303)

    @app.get("/email/verify")
    async def verify_email_form(request: Request):
        return templates.TemplateResponse(
            request,
            "email_result.html",
            _template_context(
                request,
                title="Verify email",
                authenticated=_is_authenticated(request),
                heading="Verify email",
                message="Enter the one-time verification code from the email.",
                form_action="/email/verify",
                token_label="Verification code",
                submit_label="Verify email",
            ),
        )

    @app.post("/email/verify")
    async def verify_email(request: Request, token: str = Form("")):
        if not token:
            return PlainTextResponse("Verification code is invalid or expired", status_code=400)
        try:
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    token_row = repo.get_valid_email_recovery_token(
                        token_hash=hash_email_token(token),
                        purpose="verify_email",
                        now=utc_now_iso(),
                    )
                    if token_row is None:
                        return PlainTextResponse(
                            "Verification code is invalid or expired",
                            status_code=400,
                        )
                    user = repo.get_user(int(token_row["user_id"]))
                    if user["email"] != token_row["email"]:
                        return PlainTextResponse(
                            "Verification code is invalid or expired",
                            status_code=400,
                        )
                    repo.mark_user_email_verified(int(user["id"]), utc_now_iso())
                    if not repo.mark_email_recovery_token_used(
                        int(token_row["id"]),
                        utc_now_iso(),
                    ):
                        return PlainTextResponse(
                            "Verification code is invalid or expired",
                            status_code=400,
                        )
        except LookupError:
            return PlainTextResponse("Verification code is invalid or expired", status_code=400)

        return templates.TemplateResponse(
            request,
            "email_result.html",
            _template_context(
                request,
                title="Email verified",
                authenticated=_is_authenticated(request),
                heading="Email verified",
                message="Email verified. You can close this page.",
            ),
        )

    @app.post("/users/{user_id}/devices/{device_id}/email-config")
    async def send_device_config_email(
        request: Request,
        user_id: int,
        device_id: int,
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)
        if not actual_settings.email_delivery_enabled:
            return PlainTextResponse("Email delivery is disabled", status_code=400)

        try:
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    user = _row_to_dict(repo.get_user(user_id))
                    email = _required_user_email(user)
                    if actual_settings.email_require_verification and not user["email_verified_at"]:
                        return PlainTextResponse("Email is not verified", status_code=400)
                    device = repo.get_user_device(user_id=user_id, device_id=device_id)
                    if device is None:
                        return PlainTextResponse("Device not found", status_code=404)
                    result = build_device_config_delivery(
                        repo=repo,
                        secret_box=SecretBox.from_app_secret(actual_settings.app_secret_key),
                        device=device,
                        client_config_template_dir=actual_settings.client_config_template_dir,
                        client_dns=actual_settings.client_dns,
                        client_allowed_ips=actual_settings.client_allowed_ips,
                    )
                    metadata = _email_service(request).send_config_email(
                        to_address=email,
                        user_id=user_id,
                        device_id=device_id,
                        delivery=result.delivery,
                    )
                    _record_web_user_action(
                        repo,
                        actual_settings,
                        request,
                        action="web_email_config_send",
                        target_user_id=user_id,
                        target_device_id=device_id,
                        metadata=metadata,
                    )
        except LookupError:
            return PlainTextResponse("User not found", status_code=404)
        except ValueError as exc:
            return PlainTextResponse(str(exc), status_code=400)

        return RedirectResponse(f"/users/{user_id}", status_code=303)

    @app.post("/users/{user_id}/devices/{device_id}/email-recovery/start")
    async def start_device_config_recovery(
        request: Request,
        user_id: int,
        device_id: int,
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)
        if not actual_settings.email_delivery_enabled:
            return PlainTextResponse("Email delivery is disabled", status_code=400)

        try:
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    user = _row_to_dict(repo.get_user(user_id))
                    email = _required_user_email(user)
                    if not user["email_verified_at"]:
                        return PlainTextResponse("Email is not verified", status_code=400)
                    if repo.get_user_device(user_id=user_id, device_id=device_id) is None:
                        return PlainTextResponse("Device not found", status_code=404)
                    token = create_email_token(
                        ttl_minutes=actual_settings.email_recovery_token_ttl_minutes,
                    )
                    repo.create_email_recovery_token(
                        user_id=user_id,
                        email=email,
                        token_hash=token.token_hash,
                        purpose="recover_config",
                        expires_at=token.expires_at,
                        device_id=device_id,
                    )
                    metadata = _email_service(request).send_recovery_start_email(
                        to_address=email,
                        user_id=user_id,
                        device_id=device_id,
                        token=token.raw_token,
                    )
                    _record_web_user_action(
                        repo,
                        actual_settings,
                        request,
                        action="web_email_recovery_start",
                        target_user_id=user_id,
                        target_device_id=device_id,
                        metadata=metadata,
                    )
        except LookupError:
            return PlainTextResponse("User not found", status_code=404)
        except ValueError as exc:
            return PlainTextResponse(str(exc), status_code=400)

        return RedirectResponse(f"/users/{user_id}", status_code=303)

    @app.get("/email/recover")
    async def recover_device_config_form(request: Request):
        if not actual_settings.email_delivery_enabled:
            return PlainTextResponse("Email delivery is disabled", status_code=400)
        return templates.TemplateResponse(
            request,
            "email_result.html",
            _template_context(
                request,
                title="Recover config",
                authenticated=_is_authenticated(request),
                heading="Recover config",
                message="Enter the one-time recovery code from the email.",
                form_action="/email/recover",
                token_label="Recovery code",
                submit_label="Send config email",
            ),
        )

    @app.post("/email/recover")
    async def recover_device_config(request: Request, token: str = Form("")):
        if not actual_settings.email_delivery_enabled:
            return PlainTextResponse("Email delivery is disabled", status_code=400)
        if not token:
            return PlainTextResponse("Recovery code is invalid or expired", status_code=400)
        try:
            send_to_address = ""
            send_user_id = 0
            send_device_id = 0
            send_delivery = None
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    token_row = repo.get_valid_email_recovery_token(
                        token_hash=hash_email_token(token),
                        purpose="recover_config",
                        now=utc_now_iso(),
                    )
                    if token_row is None:
                        return PlainTextResponse(
                            "Recovery code is invalid or expired",
                            status_code=400,
                        )
                    user = _row_to_dict(repo.get_user(int(token_row["user_id"])))
                    if user["email"] != token_row["email"] or not user["email_verified_at"]:
                        return PlainTextResponse(
                            "Recovery code is invalid or expired",
                            status_code=400,
                        )
                    device = repo.get_user_device(
                        user_id=int(user["id"]),
                        device_id=int(token_row["device_id"]),
                    )
                    if device is None:
                        return PlainTextResponse(
                            "Recovery code is invalid or expired",
                            status_code=400,
                        )
                    result = build_device_config_delivery(
                        repo=repo,
                        secret_box=SecretBox.from_app_secret(actual_settings.app_secret_key),
                        device=device,
                        client_config_template_dir=actual_settings.client_config_template_dir,
                        client_dns=actual_settings.client_dns,
                        client_allowed_ips=actual_settings.client_allowed_ips,
                    )
                    if not repo.mark_email_recovery_token_used(
                        int(token_row["id"]),
                        utc_now_iso(),
                    ):
                        return PlainTextResponse(
                            "Recovery code is invalid or expired",
                            status_code=400,
                        )
                    send_to_address = str(token_row["email"])
                    send_user_id = int(user["id"])
                    send_device_id = int(device["id"])
                    send_delivery = result.delivery
            if send_delivery is None:
                return PlainTextResponse("Recovery code is invalid or expired", status_code=400)
            _email_service(request).send_config_email(
                to_address=send_to_address,
                user_id=send_user_id,
                device_id=send_device_id,
                delivery=send_delivery,
            )
        except (LookupError, ValueError):
            return PlainTextResponse("Recovery code is invalid or expired", status_code=400)

        return templates.TemplateResponse(
            request,
            "email_result.html",
            _template_context(
                request,
                title="Config recovery email sent",
                authenticated=_is_authenticated(request),
                heading="Config recovery email sent",
                message="Config recovery email sent. You can close this page.",
            ),
        )

    @app.get("/users/{user_id}/edit")
    async def edit_user_form(request: Request, user_id: int):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        try:
            with _open_repository(actual_settings) as (repo, _conn):
                user = _row_to_dict(repo.get_user(user_id))
        except LookupError:
            return PlainTextResponse("User not found", status_code=404)

        return templates.TemplateResponse(
            request,
            "user_form.html",
            _template_context(
                request,
                title=f"Edit user {user_id}",
                authenticated=True,
                action_url=f"/users/{user_id}/edit",
                submit_label="Save changes",
                user=user,
                statuses=sorted(USER_STATUSES),
            ),
        )

    @app.post("/users/{user_id}/edit")
    async def update_user(
        request: Request,
        user_id: int,
        telegram_id: int = Form(...),
        username: str = Form(""),
        first_name: str = Form(""),
        last_name: str = Form(""),
        email: str = Form(""),
        status: str = Form("active"),
        is_admin: str | None = Form(None),
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            payload = _user_payload(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                status=status,
                is_admin=is_admin,
            )
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    repo.update_user_for_admin(user_id=user_id, **payload)
                    _record_web_user_action(
                        repo,
                        actual_settings,
                        request,
                        action="web_user_update",
                        target_user_id=user_id,
                        metadata={"telegram_id": telegram_id},
                    )
        except LookupError:
            return PlainTextResponse("User not found", status_code=404)
        except (sqlite3.IntegrityError, ValueError) as exc:
            return PlainTextResponse(str(exc), status_code=400)

        return RedirectResponse(f"/users/{user_id}", status_code=303)

    @app.post("/users/{user_id}/block")
    async def block_user(
        request: Request,
        user_id: int,
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            _set_user_status_with_action(
                actual_settings,
                request,
                user_id=user_id,
                status="blocked",
                action="web_user_block",
            )
        except LookupError:
            return PlainTextResponse("User not found", status_code=404)

        return RedirectResponse(f"/users/{user_id}", status_code=303)

    @app.post("/users/{user_id}/delete")
    async def delete_user(
        request: Request,
        user_id: int,
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            _set_user_status_with_action(
                actual_settings,
                request,
                user_id=user_id,
                status="deleted",
                action="web_user_delete",
            )
        except LookupError:
            return PlainTextResponse("User not found", status_code=404)

        return RedirectResponse(f"/users/{user_id}", status_code=303)

    @app.post("/users/{user_id}/disable-vpn")
    async def disable_user_vpn(
        request: Request,
        user_id: int,
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            _disable_user_vpn(actual_settings, request, user_id)
        except LookupError:
            return PlainTextResponse("User not found", status_code=404)
        except (ConfigError, PeerApplyError, ValueError) as exc:
            return PlainTextResponse(str(exc), status_code=400)

        return RedirectResponse(f"/users/{user_id}", status_code=303)

    @app.post("/users/{user_id}/destroy")
    async def destroy_user(
        request: Request,
        user_id: int,
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            _destroy_user(actual_settings, request, user_id)
        except LookupError:
            return PlainTextResponse("User not found", status_code=404)
        except (ConfigError, PeerApplyError, ValueError) as exc:
            return PlainTextResponse(str(exc), status_code=400)

        return RedirectResponse("/users", status_code=303)

    @app.get("/servers")
    async def servers_index(request: Request):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        servers = _load_servers(actual_settings)
        return templates.TemplateResponse(
            request,
            "servers.html",
            _template_context(
                request,
                title="Servers",
                authenticated=True,
                servers=servers,
            ),
        )

    @app.get("/servers/new")
    async def new_server_form(request: Request):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            request,
            "server_form.html",
            _template_context(
                request,
                title="New server",
                authenticated=True,
                action_url="/servers/new",
                submit_label="Create server",
                server=_blank_server_form(),
                statuses=sorted(SERVER_STATUSES),
            ),
        )

    @app.post("/servers/new")
    async def create_server(
        request: Request,
        name: str = Form(...),
        host: str = Form(...),
        ssh_port: int = Form(...),
        endpoint_host: str = Form(...),
        vpn_port: int = Form(...),
        vpn_network_cidr: str = Form(...),
        server_address: str = Form(...),
        server_public_key: str = Form(""),
        runtime: str = Form(...),
        firewall: str = Form(...),
        status: str = Form("active"),
        max_devices: int = Form(...),
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            payload = _server_payload(
                name=name,
                host=host,
                ssh_port=ssh_port,
                endpoint_host=endpoint_host,
                vpn_port=vpn_port,
                vpn_network_cidr=vpn_network_cidr,
                server_address=server_address,
                server_public_key=server_public_key,
                runtime=runtime,
                firewall=firewall,
                status=status,
                max_devices=max_devices,
            )
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    server_id = repo.create_server_for_admin(**payload)
                    _record_web_server_action(
                        repo,
                        actual_settings,
                        request,
                        action="web_server_create",
                        server_id=server_id,
                        metadata={"name": payload["name"]},
                    )
        except (sqlite3.IntegrityError, ValueError) as exc:
            return PlainTextResponse(str(exc), status_code=400)

        return RedirectResponse(f"/servers/{server_id}", status_code=303)

    @app.get("/servers/{server_id}")
    async def server_detail(request: Request, server_id: int):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        try:
            detail = _load_server_detail(actual_settings, server_id)
        except LookupError:
            return PlainTextResponse("Server not found", status_code=404)

        return templates.TemplateResponse(
            request,
            "server_detail.html",
            _template_context(
                request,
                title=f"Server {server_id}",
                authenticated=True,
                peer_sync=_load_peer_sync_from_session(request, server_id),
                **detail,
            ),
        )

    @app.post("/servers/{server_id}/sync/run")
    async def run_server_peer_sync(
        request: Request,
        server_id: int,
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            report = _collect_server_peer_sync(actual_settings, server_id)
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    _record_web_server_action(
                        repo,
                        actual_settings,
                        request,
                        action="web_server_peer_sync_run",
                        server_id=server_id,
                        metadata={
                            "known_count": report["known_count"],
                            "unknown_count": report["unknown_count"],
                            "missing_count": report["missing_count"],
                        },
                    )
        except LookupError:
            return PlainTextResponse("Server not found", status_code=404)
        except (ConfigError, ValueError) as exc:
            report = _empty_peer_sync_report(error=str(exc))

        request.session[_peer_sync_session_key(server_id)] = json.dumps(report)
        return RedirectResponse(f"/servers/{server_id}", status_code=303)

    @app.post("/servers/{server_id}/unknown-peers/ignore")
    async def ignore_unknown_remote_peer(
        request: Request,
        server_id: int,
        peer_public_key: str = Form(...),
        allowed_ips: str = Form(""),
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    repo.ignore_remote_peer(
                        server_id=server_id,
                        peer_public_key=peer_public_key,
                        allowed_ips=allowed_ips,
                    )
                    _record_web_server_action(
                        repo,
                        actual_settings,
                        request,
                        action="web_server_peer_ignore",
                        server_id=server_id,
                        metadata={
                            "peer_public_key": peer_public_key,
                            "allowed_ips": allowed_ips,
                        },
                    )
        except LookupError:
            return PlainTextResponse("Server not found", status_code=404)

        request.session.pop(_peer_sync_session_key(server_id), None)
        return RedirectResponse(f"/servers/{server_id}", status_code=303)

    @app.post("/servers/{server_id}/unknown-peers/remove")
    async def remove_unknown_remote_peer(
        request: Request,
        server_id: int,
        peer_public_key: str = Form(...),
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            _remove_unknown_remote_peer(actual_settings, server_id, peer_public_key)
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    repo.get_server(server_id)
                    _record_web_server_action(
                        repo,
                        actual_settings,
                        request,
                        action="web_server_peer_remove",
                        server_id=server_id,
                        metadata={"peer_public_key": peer_public_key},
                    )
        except LookupError:
            return PlainTextResponse("Server not found", status_code=404)
        except (ConfigError, PeerApplyError, ValueError) as exc:
            return PlainTextResponse(str(exc), status_code=400)

        request.session.pop(_peer_sync_session_key(server_id), None)
        return RedirectResponse(f"/servers/{server_id}", status_code=303)

    @app.get("/servers/{server_id}/edit")
    async def edit_server_form(request: Request, server_id: int):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        try:
            with _open_repository(actual_settings) as (repo, _conn):
                server = _row_to_dict(repo.get_server(server_id))
        except LookupError:
            return PlainTextResponse("Server not found", status_code=404)

        return templates.TemplateResponse(
            request,
            "server_form.html",
            _template_context(
                request,
                title=f"Edit server {server_id}",
                authenticated=True,
                action_url=f"/servers/{server_id}/edit",
                submit_label="Save changes",
                server=server,
                statuses=sorted(SERVER_STATUSES),
            ),
        )

    @app.post("/servers/{server_id}/edit")
    async def update_server(
        request: Request,
        server_id: int,
        name: str = Form(...),
        host: str = Form(...),
        ssh_port: int = Form(...),
        endpoint_host: str = Form(...),
        vpn_port: int = Form(...),
        vpn_network_cidr: str = Form(...),
        server_address: str = Form(...),
        server_public_key: str = Form(""),
        runtime: str = Form(...),
        firewall: str = Form(...),
        status: str = Form("active"),
        max_devices: int = Form(...),
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            payload = _server_payload(
                name=name,
                host=host,
                ssh_port=ssh_port,
                endpoint_host=endpoint_host,
                vpn_port=vpn_port,
                vpn_network_cidr=vpn_network_cidr,
                server_address=server_address,
                server_public_key=server_public_key,
                runtime=runtime,
                firewall=firewall,
                status=status,
                max_devices=max_devices,
            )
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    repo.update_server_for_admin(
                        server_id=server_id,
                        **payload,
                    )
                    _record_web_server_action(
                        repo,
                        actual_settings,
                        request,
                        action="web_server_update",
                        server_id=server_id,
                        metadata={"name": payload["name"]},
                    )
        except LookupError:
            return PlainTextResponse("Server not found", status_code=404)
        except (sqlite3.IntegrityError, ValueError) as exc:
            return PlainTextResponse(str(exc), status_code=400)

        return RedirectResponse(f"/servers/{server_id}", status_code=303)

    @app.post("/servers/{server_id}/disable")
    async def disable_server(
        request: Request,
        server_id: int,
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    repo.set_server_status_for_admin(server_id, "disabled")
                    _record_web_server_action(
                        repo,
                        actual_settings,
                        request,
                        action="web_server_disable",
                        server_id=server_id,
                        metadata={"status": "disabled"},
                    )
        except LookupError:
            return PlainTextResponse("Server not found", status_code=404)

        return RedirectResponse(f"/servers/{server_id}", status_code=303)

    @app.get("/servers/{server_id}/health")
    async def server_health(request: Request, server_id: int):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)

        try:
            detail = _load_server_detail(actual_settings, server_id)
        except LookupError:
            return PlainTextResponse("Server not found", status_code=404)

        return templates.TemplateResponse(
            request,
            "server_health.html",
            _template_context(
                request,
                title=f"Server {server_id} health",
                authenticated=True,
                **detail,
            ),
        )

    @app.post("/servers/{server_id}/health/run")
    async def run_server_health(
        request: Request,
        server_id: int,
        csrf_token: str = Form(""),
    ):
        if not _is_authenticated(request):
            return RedirectResponse("/login", status_code=303)
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)

        try:
            with _open_repository(actual_settings) as (repo, _conn):
                server = _row_to_dict(repo.get_server(server_id))
        except LookupError:
            return PlainTextResponse("Server not found", status_code=404)

        summary = run_server_health_check(actual_settings, str(server["name"]))
        try:
            with _open_repository(actual_settings) as (repo, _conn):
                with repo.transaction():
                    repo.get_server(server_id)
                    _record_health_summary(repo, server_id, summary)
                    _record_web_server_action(
                        repo,
                        actual_settings,
                        request,
                        action="web_server_health_run",
                        server_id=server_id,
                        metadata={
                            "operation_id": summary.operation_id,
                            "risk_class": summary.risk_class,
                            "consistency_status": summary.consistency_status,
                            "status": summary.status,
                            "error": summary.error,
                        },
                    )
        except LookupError:
            return PlainTextResponse("Server not found", status_code=404)

        return RedirectResponse(f"/servers/{server_id}/health", status_code=303)

    @app.post("/logout")
    async def logout(request: Request, csrf_token: str = Form("")):
        if not verify_csrf_token(request.session, csrf_token):
            return PlainTextResponse("Invalid CSRF token", status_code=403)
        request.session.clear()
        return RedirectResponse("/login", status_code=303)

    return app


def _is_authenticated(request: Request) -> bool:
    return request.session.get(SESSION_AUTH_KEY) is True


def _template_context(request: Request, **context: Any) -> dict[str, Any]:
    base_context = {
        "request": request,
        "settings": request.app.state.settings,
        "csrf_token": generate_csrf_token(request.session),
    }
    base_context.update(context)
    return base_context


@contextmanager
def _open_repository(settings: Settings) -> Iterator[tuple[Repository, Any]]:
    conn = connect(settings.database_path)
    try:
        initialize_schema(conn)
        yield Repository(conn), conn
    finally:
        conn.close()


def _load_dashboard(settings: Settings) -> dict[str, Any]:
    with _open_repository(settings) as (repo, conn):
        user_count = _count_rows(conn, "SELECT COUNT(*) AS count FROM users")
        server_count = _count_rows(conn, "SELECT COUNT(*) AS count FROM servers")
        pending_order_count = _count_rows(
            conn,
            """
            SELECT COUNT(*) AS count
            FROM orders
            WHERE status IN ('manual_review', 'approved')
              AND device_id IS NULL
            """,
        )
        active_device_count = _count_rows(
            conn,
            "SELECT COUNT(*) AS count FROM devices WHERE status = 'active'",
        )
        users = [_row_to_dict(row) for row in repo.list_users_for_admin(limit=5)]
        servers = [_row_to_dict(row) for row in repo.list_servers_for_admin(limit=5)]
        pending_orders = [_row_to_dict(row) for row in repo.list_pending_orders(limit=5)]
        active_devices = [
            _row_to_dict(row) for row in repo.list_active_devices_with_users(limit=5)
        ]

    return {
        "metrics": [
            {
                "label": "Пользователи",
                "value": user_count,
                "caption": _plural_ru(user_count, "пользователь", "пользователя", "пользователей"),
            },
            {
                "label": "Серверы",
                "value": server_count,
                "caption": _plural_ru(server_count, "сервер", "сервера", "серверов"),
            },
            {
                "label": "Заявки",
                "value": pending_order_count,
                "caption": _plural_ru(pending_order_count, "заявка", "заявки", "заявок"),
            },
            {
                "label": "Активные устройства",
                "value": active_device_count,
                "caption": _plural_ru(active_device_count, "устройство", "устройства", "устройств"),
            },
        ],
        "users": users,
        "servers": servers,
        "pending_orders": pending_orders,
        "active_devices": active_devices,
    }


def _load_users(settings: Settings) -> list[dict[str, Any]]:
    with _open_repository(settings) as (repo, _conn):
        return [_row_to_dict(row) for row in repo.list_users_for_admin(limit=500)]


def _load_servers(settings: Settings) -> list[dict[str, Any]]:
    with _open_repository(settings) as (repo, _conn):
        return [_row_to_dict(row) for row in repo.list_servers_for_admin(limit=500)]


def _load_orders(settings: Settings) -> list[dict[str, Any]]:
    with _open_repository(settings) as (repo, _conn):
        return [_row_to_dict(row) for row in repo.list_orders_for_admin(limit=200)]


def _load_settings_sections(settings: Settings) -> list[dict[str, Any]]:
    sections = [
        {
            "title": section_title,
            "items": [
                _setting_entry(settings, field_name)
                for field_name in field_names
            ],
        }
        for section_title, field_names in SETTINGS_SECTIONS.items()
    ]
    grouped_fields = {
        field_name
        for field_names in SETTINGS_SECTIONS.values()
        for field_name in field_names
    }
    other_fields = [
        field_name
        for field_name in Settings.model_fields
        if field_name not in grouped_fields
    ]
    if other_fields:
        sections.append(
            {
                "title": "Other",
                "items": [_setting_entry(settings, field_name) for field_name in other_fields],
            }
        )
    return sections


def _load_client_config_template_views(settings: Settings) -> list[dict[str, str]]:
    sample = _sample_client_config_input()
    template_dir = settings.client_config_template_dir
    views: list[dict[str, str]] = []
    for config_version in SUPPORTED_CONFIG_VERSIONS:
        try:
            preview = render_client_config_from_template(
                sample,
                config_version,
                template_dir=template_dir,
            )
            safe_preview = _safe_config_preview(preview)
            vpn_import_link = build_vpn_import_link(safe_preview)
            error = ""
        except ConfigTemplateError as exc:
            safe_preview = ""
            vpn_import_link = ""
            error = str(exc)
        views.append(
            {
                "version": config_version,
                "filename": f"{config_version}.conf.tpl",
                "source": client_config_template_source(config_version, template_dir),
                "preview": safe_preview,
                "vpn_import_link": vpn_import_link,
                "error": error,
            }
        )
    return views


def _sample_client_config_input() -> ClientConfigInput:
    return ClientConfigInput(
        private_key="sample-client-private-key",
        address="10.8.0.2/32",
        dns="1.1.1.1",
        server_public_key="sample-server-public-key",
        preshared_key="sample-preshared-key",
        endpoint="vpn.example.com:30001",
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
    )


def _safe_config_preview(config_text: str) -> str:
    return SECRET_CONFIG_LINE_RE.sub(r"\1<sample-secret>", config_text)


def _delivery_template_placeholders() -> list[str]:
    return [
        "{device_id}",
        "{config_version}",
        "{config_version_label}",
        "{vpn_link}",
        "{android_amnezia}",
        "{android_amneziawg}",
        "{ios_russia_defaultvpn}",
        "{windows_amneziawg}",
        "{defaultvpn_github}",
    ]


def _setting_entry(settings: Settings, field_name: str) -> dict[str, str]:
    field = Settings.model_fields[field_name]
    alias = str(field.alias or field_name).upper()
    value = getattr(settings, field_name)
    return {
        "name": alias,
        "value": _display_setting_value(
            alias,
            value,
            is_path=field_name in PATH_SETTING_FIELDS,
        ),
    }


def _display_setting_value(name: str, value: Any, *, is_path: bool = False) -> str:
    if is_path and str(value):
        value = Path(str(value)).name
    redacted = redact(f"{name}={value}")
    return redacted.split("=", maxsplit=1)[1] if "=" in redacted else redacted


def _load_user_detail(settings: Settings, user_id: int) -> dict[str, Any]:
    with _open_repository(settings) as (repo, _conn):
        user = _row_to_dict(repo.get_user_for_admin(user_id))
        devices = [
            _row_to_dict(row) for row in repo.list_user_devices_for_admin(user_id)
        ]
        orders = [_row_to_dict(row) for row in repo.list_user_orders_for_admin(user_id)]
        admin_actions = [
            _row_to_dict(row) for row in repo.list_admin_actions_for_target_user(user_id)
        ]
    return {
        "user": user,
        "devices": devices,
        "orders": orders,
        "admin_actions": admin_actions,
    }


def _load_server_detail(settings: Settings, server_id: int) -> dict[str, Any]:
    with _open_repository(settings) as (repo, _conn):
        server = _row_to_dict(repo.get_server_for_admin(server_id))
        latest_health = repo.get_latest_server_health(server_id)
    return {
        "server": server,
        "latest_health": (
            _row_to_dict(latest_health) if latest_health is not None else None
        ),
    }


def _collect_server_peer_sync(settings: Settings, server_id: int) -> dict[str, Any]:
    with _open_repository(settings) as (repo, _conn):
        server = _load_configured_server(settings, repo, server_id)
        report = PeerInventoryService(repo).compare(
            server_id,
            AwgDumpPeerInventoryCollector(
                interface=server.vpn.interface,
                container_name=server.runtime.container_name
                if server.runtime.type == "docker"
                else None,
                ssh_client=SystemSshClient(
                    server,
                    password=settings.vps_ssh_password or None,
                ),
            ),
        )
        ignored_keys = repo.list_ignored_remote_peer_keys(server_id)
    unknown_peers = [
        peer
        for peer in report.unknown_remote_peers
        if peer.peer_public_key not in ignored_keys
    ]
    return {
        "known_count": len(report.known_remote_peers),
        "unknown_count": len(unknown_peers),
        "missing_count": len(report.missing_local_peers),
        "ignored_count": len(ignored_keys),
        "unknown_peers": [
            {
                "peer_public_key": peer.peer_public_key,
                "allowed_ips": peer.allowed_ips,
            }
            for peer in unknown_peers
        ],
        "missing_peers": [
            {
                "device_id": peer.device_id,
                "device_name": peer.device_name,
                "peer_public_key": peer.peer_public_key,
                "vpn_ip": peer.vpn_ip,
            }
            for peer in report.missing_local_peers
        ],
        "error": "",
    }


def _empty_peer_sync_report(*, error: str) -> dict[str, Any]:
    return {
        "known_count": 0,
        "unknown_count": 0,
        "missing_count": 0,
        "ignored_count": 0,
        "unknown_peers": [],
        "missing_peers": [],
        "error": error,
    }


def _remove_unknown_remote_peer(
    settings: Settings,
    server_id: int,
    peer_public_key: str,
) -> None:
    if not settings.vps_apply_enabled:
        raise ValueError("VPS_APPLY_ENABLED must be true before removing peers from VPN")
    with _open_repository(settings) as (repo, _conn):
        server = _load_configured_server(settings, repo, server_id)
    applier = ServerConfigPeerApplier(
        server,
        password=settings.vps_ssh_password or None,
    )
    applier.remove_peer(server=server, peer_public_key=peer_public_key)


def _load_configured_server(settings: Settings, repo: Repository, server_id: int):
    server_row = _row_to_dict(repo.get_server(server_id))
    config = load_server_config(Path(settings.server_config_path))
    return select_server(config, str(server_row["name"]))


def _load_peer_sync_from_session(request: Request, server_id: int) -> dict[str, Any] | None:
    raw = request.session.get(_peer_sync_session_key(server_id))
    if not isinstance(raw, str):
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _peer_sync_session_key(server_id: int) -> str:
    return f"server_peer_sync:{server_id}"


def _blank_user_form() -> dict[str, Any]:
    return {
        "telegram_id": "",
        "username": "",
        "first_name": "",
        "last_name": "",
        "email": "",
        "status": "active",
        "is_admin": 0,
    }


def _blank_server_form() -> dict[str, Any]:
    return {
        "name": "",
        "host": "",
        "ssh_port": 22,
        "endpoint_host": "",
        "vpn_port": 30001,
        "vpn_network_cidr": "10.8.0.0/24",
        "server_address": "10.8.0.1/24",
        "server_public_key": "",
        "runtime": "host_systemd",
        "firewall": "ufw",
        "status": "active",
        "max_devices": 254,
    }


def _user_payload(
    *,
    telegram_id: int,
    username: str,
    first_name: str,
    last_name: str,
    email: str,
    status: str,
    is_admin: str | None,
) -> dict[str, Any]:
    if status not in USER_STATUSES:
        raise ValueError(f"unsupported user status: {status}")
    return {
        "telegram_id": telegram_id,
        "username": _optional_text(username),
        "first_name": _optional_text(first_name),
        "last_name": _optional_text(last_name),
        "email": _optional_text(email),
        "status": status,
        "is_admin": _is_checked(is_admin),
    }


def _server_payload(
    *,
    name: str,
    host: str,
    ssh_port: int,
    endpoint_host: str,
    vpn_port: int,
    vpn_network_cidr: str,
    server_address: str,
    server_public_key: str,
    runtime: str,
    firewall: str,
    status: str,
    max_devices: int,
) -> dict[str, Any]:
    _validate_port("ssh_port", ssh_port)
    _validate_port("vpn_port", vpn_port)
    if max_devices < 0:
        raise ValueError("max_devices must be non-negative")
    if status not in SERVER_STATUSES:
        raise ValueError(f"unsupported server status: {status}")
    return {
        "name": _required_text(name, "name"),
        "host": _required_text(host, "host"),
        "ssh_port": ssh_port,
        "endpoint_host": _required_text(endpoint_host, "endpoint_host"),
        "vpn_port": vpn_port,
        "vpn_network_cidr": _required_text(
            vpn_network_cidr,
            "vpn_network_cidr",
        ),
        "server_address": _required_text(server_address, "server_address"),
        "server_public_key": _optional_text(server_public_key) or "",
        "runtime": _required_text(runtime, "runtime"),
        "firewall": _required_text(firewall, "firewall"),
        "status": status,
        "max_devices": max_devices,
    }


def _required_text(value: str, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} is required")
    return stripped


def _validate_port(field_name: str, value: int) -> None:
    if not 1 <= value <= 65535:
        raise ValueError(f"{field_name} must be in 1..65535")


def _optional_text(value: str) -> str | None:
    stripped = value.strip()
    return stripped or None


def _is_checked(value: str | None) -> bool:
    return value is not None and value.lower() in {"1", "true", "yes", "on"}


def _set_user_status_with_action(
    settings: Settings,
    request: Request,
    *,
    user_id: int,
    status: str,
    action: str,
) -> None:
    with _open_repository(settings) as (repo, _conn):
        with repo.transaction():
            repo.get_user(user_id)
            repo.set_user_status_for_admin(user_id, status)
            _record_web_user_action(
                repo,
                settings,
                request,
                action=action,
                target_user_id=user_id,
                metadata={"status": status},
            )


def _disable_user_vpn(settings: Settings, request: Request, user_id: int) -> int:
    with _open_repository(settings) as (repo, _conn):
        user = _row_to_dict(repo.get_user(user_id))
        devices = [_row_to_dict(row) for row in repo.list_user_devices_for_vpn_removal(user_id)]

    _revoke_devices_from_vpn(settings, devices)
    revoked_at = utc_now_iso()
    with _open_repository(settings) as (repo, _conn):
        with repo.transaction():
            revoked_count = repo.revoke_user_devices(
                user_id,
                reason="web_disable_vpn",
                revoked_at=revoked_at,
            )
            repo.set_user_status_for_admin(user_id, "blocked")
            _record_web_user_action(
                repo,
                settings,
                request,
                action="web_user_disable_vpn",
                target_user_id=user_id,
                metadata={
                    "telegram_id": user["telegram_id"],
                    "status": "blocked",
                    "revoked_device_count": revoked_count,
                },
            )
    return revoked_count


def _destroy_user(settings: Settings, request: Request, user_id: int) -> None:
    with _open_repository(settings) as (repo, _conn):
        user = _row_to_dict(repo.get_user(user_id))
        devices = [_row_to_dict(row) for row in repo.list_user_devices_for_vpn_removal(user_id)]

    _revoke_devices_from_vpn(settings, devices)
    with _open_repository(settings) as (repo, _conn):
        with repo.transaction():
            repo.hard_delete_user_for_admin(user_id)
            repo.record_admin_action(
                admin_telegram_id=_web_admin_actor_id(settings),
                action="web_user_destroy",
                metadata={
                    "source": "web_admin",
                    "web_admin_username": str(
                        request.session.get("web_admin_username", "")
                    ),
                    "deleted_user_id": user_id,
                    "telegram_id": user["telegram_id"],
                    "revoked_device_count": len(devices),
                },
            )


def _revoke_devices_from_vpn(settings: Settings, devices: list[dict[str, Any]]) -> None:
    if not devices:
        return
    if not settings.vps_apply_enabled:
        raise ValueError("VPS_APPLY_ENABLED must be true before removing peers from VPN")

    config = load_server_config(Path(settings.server_config_path))
    servers_by_name = {server.name: server for server in config.servers}
    appliers: dict[str, ServerConfigPeerApplier] = {}
    for device in devices:
        server_name = str(device["server_name"])
        server = servers_by_name.get(server_name)
        if server is None:
            available = ", ".join(sorted(servers_by_name)) or "<none>"
            raise ConfigError(
                f"Server '{server_name}' not found in {settings.server_config_path}. "
                f"Available: {available}"
            )
        applier = appliers.get(server_name)
        if applier is None:
            applier = ServerConfigPeerApplier(
                server,
                password=settings.vps_ssh_password or None,
            )
            appliers[server_name] = applier
        applier.remove_peer(
            server=server,
            peer_public_key=str(device["peer_public_key"]),
        )


def _email_service(request: Request) -> EmailDeliveryService:
    settings = request.app.state.settings
    return EmailDeliveryService(
        sender=request.app.state.email_sender,
        from_address=settings.smtp_from,
        base_url=str(request.base_url),
        attach_config=settings.email_config_attachments_enabled,
    )


def _required_user_email(user: dict[str, Any]) -> str:
    email = str(user.get("email") or "").strip()
    if not email:
        raise ValueError("User email is required")
    return email


def _record_web_user_action(
    repo: Repository,
    settings: Settings,
    request: Request,
    *,
    action: str,
    target_user_id: int,
    target_device_id: int | None = None,
    metadata: dict[str, Any],
) -> None:
    full_metadata = {
        "source": "web_admin",
        "web_admin_username": str(request.session.get("web_admin_username", "")),
    }
    full_metadata.update(metadata)
    repo.record_admin_action(
        admin_telegram_id=_web_admin_actor_id(settings),
        action=action,
        target_user_id=target_user_id,
        target_device_id=target_device_id,
        metadata=full_metadata,
    )


def _record_web_server_action(
    repo: Repository,
    settings: Settings,
    request: Request,
    *,
    action: str,
    server_id: int,
    metadata: dict[str, Any],
) -> None:
    full_metadata = {
        "source": "web_admin",
        "web_admin_username": str(request.session.get("web_admin_username", "")),
        "server_id": server_id,
    }
    full_metadata.update(metadata)
    repo.record_admin_action(
        admin_telegram_id=_web_admin_actor_id(settings),
        action=action,
        metadata=full_metadata,
    )


def _record_health_summary(
    repo: Repository,
    server_id: int,
    summary: HealthSummary,
) -> int:
    return repo.record_server_health(
        server_id=server_id,
        status=summary.status,
        latency_ms=summary.latency_ms,
        ssh_ok=summary.ssh_ok,
        awg_ok=summary.awg_ok,
        udp_port_ok=summary.udp_port_ok,
        error=summary.error,
    )


def _web_admin_actor_id(settings: Settings) -> int:
    return settings.admin_ids[0] if settings.admin_ids else 0


def _count_rows(conn: Any, query: str) -> int:
    row = conn.execute(query).fetchone()
    return int(row["count"])


def _row_to_dict(row: Any) -> dict[str, Any]:
    return dict(row)


def _plural_ru(count: int, one: str, few: str, many: str) -> str:
    if count % 10 == 1 and count % 100 != 11:
        noun = one
    elif 2 <= count % 10 <= 4 and not 12 <= count % 100 <= 14:
        noun = few
    else:
        noun = many
    return f"{count} {noun}"
