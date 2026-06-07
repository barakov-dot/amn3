from __future__ import annotations

from typing import Any

from app.db.repositories import Repository


ALLOWED_API_SCOPES = ("metrics:read", "server:read")
ALLOWED_LANES = (
    "read-only API status",
    "aggregate metrics",
    "web evidence UX",
    "API token lifecycle administration",
    "controlled prod status visibility",
    "Local Agent runtime summary visibility",
)
BLOCKED_LANES = (
    "new live peer apply/revoke without separate operator confirmation",
    "/api/clients write CRUD",
    "API config:read",
    "public/self-service config delivery",
    "Local Agent configs or mutations",
    "backup/import/reboot routes",
    "public API 3040 exposure",
)
CURRENT_STABLE_HEAD = "42ffa65"
PREVIOUS_STABLE_HEAD = "c8a6363"
POST_DRY_RUN_READ_ONLY_HEAD = "7764ae7"
API_WEB_BASELINE_HEAD = "294803e"
REMOTE_OPERATION_GATE_MERGE_HEAD = "708c98e"
REMOTE_OPERATION_GATE_CANDIDATE_HEAD = "7281254"
CONTROLLED_PROD_SMOKE_RUN_ID = "20260607T150923Z"
CURRENT_LOCAL_READ_ONLY_HEAD = "42ffa65"
CURRENT_LOCAL_READ_ONLY_SMOKE_STATUS = "passed"
CURRENT_LOCAL_READ_ONLY_SMOKE_CHECKED_ROUTES = 6


def build_integration_status(repo: Repository) -> dict[str, Any]:
    return {
        "status": "controlled_prod_ready",
        "summary": (
            "Controlled prod is approved for VPS source overlay 42ffa65 after "
            "safe source overlay update and read-only loopback smoke on /opt/amn2."
        ),
        "api_baseline": {
            "status": "controlled_prod_ready",
            "stable_head": CURRENT_STABLE_HEAD,
            "previous_stable_head": PREVIOUS_STABLE_HEAD,
            "api_web_baseline_head": API_WEB_BASELINE_HEAD,
            "integration_status_head": POST_DRY_RUN_READ_ONLY_HEAD,
            "allowed_scopes": list(ALLOWED_API_SCOPES),
            "write_routes_enabled": False,
            "public_api_exposed": False,
        },
        "remote_operation_gate": {
            "candidate_head": REMOTE_OPERATION_GATE_CANDIDATE_HEAD,
            "stable_merge_head": REMOTE_OPERATION_GATE_MERGE_HEAD,
            "phase_1": "dry_run_only_pass",
            "phase_2": "verified_live",
            "write_operations_enabled": False,
        },
        "controlled_prod_readiness": {
            "status": "ready",
            "decision": "controlled-prod-ready",
            "runbook": "docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md",
            "source_overlay_head": CURRENT_STABLE_HEAD,
            "vps_smoke_run_id": CONTROLLED_PROD_SMOKE_RUN_ID,
            "web_admin_access": "https_reverse_proxy",
            "api_listener": "127.0.0.1:3040_loopback_only",
            "vps_apply_enabled_default": False,
            "recovery_path": "known",
        },
        "local_read_only_extension": {
            "head": CURRENT_LOCAL_READ_ONLY_HEAD,
            "status": "source_overlay_smoke_passed",
            "vps_smoke_status": CURRENT_LOCAL_READ_ONLY_SMOKE_STATUS,
            "checked_routes": CURRENT_LOCAL_READ_ONLY_SMOKE_CHECKED_ROUTES,
            "workspace": "source_overlay",
            "token_lifecycle": "revoked",
            "safe_routes": [
                "/api/local-agent/runtime/summary",
            ],
        },
        "aggregate_state": _load_aggregate_state(repo),
        "allowed_lanes": list(ALLOWED_LANES),
        "blocked_lanes": list(BLOCKED_LANES),
        "next_gate": "Choose next read-only controller slice",
    }


def _load_aggregate_state(repo: Repository) -> dict[str, int]:
    summary = repo.get_api_metrics_summary()
    return {
        "servers": summary["servers_total"],
        "users": summary["users_total"],
        "devices": summary["devices_total"],
    }
