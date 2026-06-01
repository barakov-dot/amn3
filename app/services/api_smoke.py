from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


FORBIDDEN_API_RESPONSE_MARKERS = (
    "PrivateKey",
    "PresharedKey",
    "vpn://",
    "token_hash",
    "raw-token",
    "raw token",
    "peer_public_key",
    "server_public_key",
    "ssh_port",
    "endpoint_host",
    "Authorization",
    ".conf",
)


def find_forbidden_api_response_markers(payload: object) -> list[str]:
    text = _serialize_payload(payload).lower()
    return [
        marker
        for marker in FORBIDDEN_API_RESPONSE_MARKERS
        if marker.lower() in text
    ]


def validate_api_smoke_responses(
    responses: Mapping[str, Mapping[str, Any]],
) -> dict[str, object]:
    routes = []
    failed = False
    for name, response in responses.items():
        status_code = int(response["status_code"])
        forbidden_markers = find_forbidden_api_response_markers(response.get("body"))
        if status_code != 200 or forbidden_markers:
            failed = True
        routes.append(
            {
                "name": name,
                "status_code": status_code,
                "forbidden_markers": forbidden_markers,
            }
        )

    return {
        "status": "failed" if failed else "passed",
        "checked_routes": len(routes),
        "routes": routes,
    }


def _serialize_payload(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
