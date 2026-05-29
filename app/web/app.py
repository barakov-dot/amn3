from __future__ import annotations

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
from app.db.schema import initialize_schema
from app.web.auth import check_password
from app.web.auth import generate_csrf_token
from app.web.auth import require_web_admin_config
from app.web.auth import verify_csrf_token


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
SESSION_AUTH_KEY = "web_admin_authenticated"

templates = Jinja2Templates(directory=TEMPLATE_DIR)


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
