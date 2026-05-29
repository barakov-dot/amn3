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
from app.db.repositories import USER_STATUSES
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
