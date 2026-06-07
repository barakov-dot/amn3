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
    "manual validation VPS evidence",
)
BLOCKED_LANES = (
    "new live peer apply/revoke without separate operator confirmation",
    "/api/clients write CRUD",
    "API config:read",
    "public/self-service config delivery",
    "Local Agent configs or mutations",
    "backup/import/reboot routes",
    "public API 3040 exposure",
    "systemd/reverse proxy deployment on validation VPS",
)
CURRENT_STABLE_HEAD = "c92bd1a"
PREVIOUS_STABLE_HEAD = "42ffa65"
POST_DRY_RUN_READ_ONLY_HEAD = "7764ae7"
API_WEB_BASELINE_HEAD = "c92bd1a"
REMOTE_OPERATION_GATE_MERGE_HEAD = "708c98e"
REMOTE_OPERATION_GATE_CANDIDATE_HEAD = "7281254"
CONTROLLED_PROD_SMOKE_RUN_ID = "20260607T195044Z"
CONTROLLED_PROD_SOURCE_UPDATE_RUN_ID = "20260607T194406Z"
CURRENT_LOCAL_READ_ONLY_HEAD = "c92bd1a"
CURRENT_LOCAL_READ_ONLY_SMOKE_STATUS = "passed"
CURRENT_LOCAL_READ_ONLY_SMOKE_CHECKED_ROUTES = 6


def build_integration_status(repo: Repository) -> dict[str, Any]:
    return {
        "status": "manual_prelaunch_ready",
        "summary": (
            "Manual prelaunch validation passed for VPS source overlay c92bd1a. "
            "Systemd and reverse proxy deployment are deferred to the target server."
        ),
        "api_baseline": {
            "status": "manual_prelaunch_ready",
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
            "status": "manual_prelaunch_ready",
            "decision": "manual-prelaunch-pass-systemd-deferred",
            "runbook": "docs/AMN2_C92_SOURCE_OVERLAY_ALIGNMENT.ru.md",
            "source_overlay_head": CURRENT_STABLE_HEAD,
            "vps_smoke_run_id": CONTROLLED_PROD_SMOKE_RUN_ID,
            "source_update_run_id": CONTROLLED_PROD_SOURCE_UPDATE_RUN_ID,
            "web_admin_access": "manual_loopback_validation",
            "manual_web_check": "passed",
            "service_deployment": "deferred_target_server",
            "api_listener": "127.0.0.1:3040_loopback_only",
            "vps_apply_enabled_default": False,
            "recovery_path": "known",
        },
        "local_read_only_extension": {
            "head": CURRENT_LOCAL_READ_ONLY_HEAD,
            "status": "manual_prelaunch_passed",
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
        "next_gate": "Repeat gate on target server before systemd/reverse proxy",
    }


def _load_aggregate_state(repo: Repository) -> dict[str, int]:
    summary = repo.get_api_metrics_summary()
    return {
        "servers": summary["servers_total"],
        "users": summary["users_total"],
        "devices": summary["devices_total"],
    }
