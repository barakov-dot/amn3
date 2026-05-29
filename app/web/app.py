from __future__ import annotations

import sqlite3
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
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.repositories import SERVER_STATUSES
from app.db.repositories import USER_STATUSES
from app.db.schema import initialize_schema
from app.security.redaction import redact
from app.web.auth import check_password
from app.web.auth import generate_csrf_token
from app.web.auth import require_web_admin_config
from app.web.auth import verify_csrf_token
from app.web.logs import read_log_tail
from app.web.server_health import HealthSummary
from app.web.server_health import run_server_health_check


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
SESSION_AUTH_KEY = "web_admin_authenticated"

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


def create_web_app(settings: Settings | None = None) -> FastAPI:
    actual_settings = settings or Settings()
    require_web_admin_config(
        password_hash=actual_settings.web_admin_password_hash,
        session_secret=actual_settings.web_admin_session_secret,
    )

    app = FastAPI(title="Amneziya Web Admin")
    app.state.settings = actual_settings
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
                **detail,
            ),
        )

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


def _record_web_user_action(
    repo: Repository,
    settings: Settings,
    request: Request,
    *,
    action: str,
    target_user_id: int,
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
