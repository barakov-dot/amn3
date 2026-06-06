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
    "new live peer apply/revoke without separate operator confirmation",
    "/api/clients write CRUD",
    "API config:read",
    "public/self-service config delivery",
    "Local Agent configs or mutations",
    "backup/import/reboot routes",
)
CURRENT_STABLE_HEAD = "1a193b9"
POST_DRY_RUN_READ_ONLY_HEAD = "7764ae7"
API_WEB_BASELINE_HEAD = "294803e"
REMOTE_OPERATION_GATE_MERGE_HEAD = "708c98e"
REMOTE_OPERATION_GATE_CANDIDATE_HEAD = "7281254"


def build_integration_status(repo: Repository) -> dict[str, Any]:
    return {
        "status": "read_only_vps_smoked",
        "summary": "Read-only API/web integration is VPS-smoked; controlled prod readiness is the next operator gate.",
        "api_baseline": {
            "status": "verified_read_only",
            "stable_head": CURRENT_STABLE_HEAD,
            "api_web_baseline_head": API_WEB_BASELINE_HEAD,
            "integration_status_head": POST_DRY_RUN_READ_ONLY_HEAD,
            "allowed_scopes": list(ALLOWED_API_SCOPES),
            "write_routes_enabled": False,
        },
        "remote_operation_gate": {
            "candidate_head": REMOTE_OPERATION_GATE_CANDIDATE_HEAD,
            "stable_merge_head": REMOTE_OPERATION_GATE_MERGE_HEAD,
            "phase_1": "dry_run_only_pass",
            "phase_2": "verified_live",
            "write_operations_enabled": False,
        },
        "controlled_prod_readiness": {
            "status": "runbook_published",
            "decision": "pending_operator_evidence",
            "runbook": "docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md",
        },
        "aggregate_state": _load_aggregate_state(repo),
        "allowed_lanes": list(ALLOWED_LANES),
        "blocked_lanes": list(BLOCKED_LANES),
        "next_gate": "operator-only controlled prod readiness checklist",
    }


def _load_aggregate_state(repo: Repository) -> dict[str, int]:
    summary = repo.get_api_metrics_summary()
    return {
        "servers": summary["servers_total"],
        "users": summary["users_total"],
        "devices": summary["devices_total"],
    }
