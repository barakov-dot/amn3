from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, Request

from app.config import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.services.api_tokens import ApiTokenAuthError
from app.services.api_tokens import ApiTokenRecord
from app.services.api_tokens import authenticate_api_token
from app.services.api_tokens import hash_api_token


@dataclass(frozen=True)
class ApiAuthContext:
    token: ApiTokenRecord


def create_api_app(settings: Settings | None = None) -> FastAPI:
    actual_settings = settings or Settings()
    app = FastAPI(title="Amneziya API")
    app.state.settings = actual_settings

    @app.get("/api/servers")
    async def list_servers(
        repo: Repository = Depends(_repo),
        _auth: ApiAuthContext = Depends(_require_scope("server:read")),
    ):
        return {
            "servers": [
                _server_summary_payload(row)
                for row in repo.list_api_server_summaries()
            ],
        }

    @app.get("/api/servers/{server_name}/summary")
    async def server_summary(
        server_name: str,
        repo: Repository = Depends(_repo),
        _auth: ApiAuthContext = Depends(_require_scope("server:read")),
    ):
        row = repo.get_api_server_summary(server_name)
        if row is None:
            raise HTTPException(status_code=404, detail="server_not_found")
        return {"server": _server_summary_payload(row)}

    @app.get("/api/metrics/summary")
    async def metrics_summary(
        repo: Repository = Depends(_repo),
        _auth: ApiAuthContext = Depends(_require_scope("metrics:read")),
    ):
        summary = repo.get_api_metrics_summary()
        return {
            "users": {
                "total": summary["users_total"],
                "active": summary["users_active"],
                "blocked": summary["users_blocked"],
                "deleted": summary["users_deleted"],
            },
            "servers": {
                "total": summary["servers_total"],
                "active": summary["servers_active"],
                "degraded": summary["servers_degraded"],
                "disabled": summary["servers_disabled"],
            },
            "devices": {
                "total": summary["devices_total"],
                "active": summary["devices_active"],
                "disabled": summary["devices_disabled"],
                "revoked": summary["devices_revoked"],
            },
            "traffic": {
                "rx_bytes": summary["traffic_rx_bytes"],
                "tx_bytes": summary["traffic_tx_bytes"],
                "source": "latest_device_snapshots",
            },
        }

    return app


async def _repo(request: Request) -> AsyncIterator[Repository]:
    settings: Settings = request.app.state.settings
    conn = connect(settings.database_path)
    initialize_schema(conn)
    try:
        yield Repository(conn)
    finally:
        conn.close()


def _require_scope(required_scope: str):
    async def dependency(
        authorization: str | None = Header(default=None),
        repo: Repository = Depends(_repo),
    ) -> ApiAuthContext:
        raw_token = _extract_bearer_token(authorization)
        now = datetime.now(timezone.utc)
        row = repo.get_valid_api_token(
            token_hash=hash_api_token(raw_token),
            now=now.isoformat(),
        )
        if row is None:
            raise HTTPException(status_code=401, detail="invalid_token")

        record = _api_token_record_from_row(row)
        try:
            token = authenticate_api_token(
                raw_token,
                tokens=(record,),
                required_scope=required_scope,
                now=now,
            )
        except ApiTokenAuthError as exc:
            if exc.reason in {"missing_scope", "inactive_owner"}:
                raise HTTPException(status_code=403, detail=exc.reason) from exc
            raise HTTPException(status_code=401, detail=exc.reason) from exc

        repo.mark_api_token_used(token.token_id, now.isoformat())
        return ApiAuthContext(token=token)

    return dependency


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="missing_bearer_token")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="invalid_authorization_header")
    return token.strip()


def _api_token_record_from_row(row) -> ApiTokenRecord:
    return ApiTokenRecord(
        token_id=row["id"],
        token_hash=row["token_hash"],
        name=row["name"],
        owner_label=row["owner_label"],
        owner_user_id=row["owner_user_id"],
        owner_status=row["owner_status"],
        scopes=frozenset(json.loads(row["scopes_json"])),
        expires_at=_parse_datetime(row["expires_at"]),
        revoked_at=_parse_datetime(row["revoked_at"]),
    )


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _server_summary_payload(row) -> dict[str, object]:
    return {
        "name": row["name"],
        "status": row["status"],
        "enabled": row["status"] != "disabled",
        "configured": True,
        "runtime": row["runtime"],
        "device_counts": {
            "active": int(row["active_device_count"]),
            "total": int(row["total_device_count"]),
        },
        "health": {
            "status": row["health_status"] or "unknown",
            "latency_ms": row["health_latency_ms"],
            "checked_at": row["health_checked_at"],
            "readiness": {
                "ssh": bool(row["health_ssh_ok"]),
                "awg": bool(row["health_awg_ok"]),
                "udp_port": bool(row["health_udp_port_ok"]),
            },
        },
    }
