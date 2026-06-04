from __future__ import annotations

from typing import Any

from app.db.repositories import Repository


ALLOWED_API_SCOPES = ("metrics:read", "server:read")
ALLOWED_LANES = (
    "read-only API status",
    "aggregate metrics",
    "web evidence UX",
    "API token lifecycle administration",
)
BLOCKED_LANES = (
    "live peer apply/revoke",
    "/api/clients write CRUD",
    "API config:read",
    "public/self-service config delivery",
    "Local Agent configs or mutations",
    "backup/import/reboot routes",
)


def build_integration_status(repo: Repository) -> dict[str, Any]:
    return {
        "status": "dry_run_ready",
        "summary": "Read-only API/web integration is available; remote writes require a separate live gate.",
        "api_baseline": {
            "status": "verified_read_only",
            "stable_head": "708c98e",
            "api_web_baseline_head": "294803e",
            "allowed_scopes": list(ALLOWED_API_SCOPES),
            "write_routes_enabled": False,
        },
        "remote_operation_gate": {
            "candidate_head": "7281254",
            "stable_merge_head": "708c98e",
            "phase_1": "dry_run_only_pass",
            "phase_2": "not_run",
            "write_operations_enabled": False,
        },
        "aggregate_state": _load_aggregate_state(repo),
        "allowed_lanes": list(ALLOWED_LANES),
        "blocked_lanes": list(BLOCKED_LANES),
        "next_gate": "single test peer live apply/revoke requires separate operator confirmation",
    }


def _load_aggregate_state(repo: Repository) -> dict[str, int]:
    summary = repo.get_api_metrics_summary()
    return {
        "servers": summary["servers_total"],
        "users": summary["users_total"],
        "devices": summary["devices_total"],
    }
