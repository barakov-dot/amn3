import json

from app.services.api_smoke import find_forbidden_api_response_markers
from app.services.api_smoke import validate_api_smoke_responses


def test_api_smoke_finds_forbidden_response_markers_without_echoing_payload():
    payload = {
        "server": {
            "name": "local",
            "ssh_port": 22,
            "endpoint_host": "203.0.113.10",
            "link": "vpn://secret-import-link",
            "token_hash": "sha256:secret",
            "PrivateKey": "secret-private-key",
        }
    }

    markers = find_forbidden_api_response_markers(payload)
    report = validate_api_smoke_responses(
        {
            "server_summary": {
                "status_code": 200,
                "body": payload,
            }
        }
    )

    assert markers == [
        "PrivateKey",
        "vpn://",
        "token_hash",
        "ssh_port",
        "endpoint_host",
    ]
    assert report["status"] == "failed"
    assert report["routes"] == [
        {
            "name": "server_summary",
            "status_code": 200,
            "forbidden_markers": [
                "PrivateKey",
                "vpn://",
                "token_hash",
                "ssh_port",
                "endpoint_host",
            ],
        }
    ]
    assert "secret-private-key" not in json.dumps(report)
    assert "secret-import-link" not in json.dumps(report)


def test_api_smoke_passes_clean_aggregate_responses():
    report = validate_api_smoke_responses(
        {
            "servers": {
                "status_code": 200,
                "body": {"servers": [{"name": "local", "device_counts": {"total": 2}}],
                },
            },
            "metrics": {
                "status_code": 200,
                "body": {"users": {"total": 1}, "traffic": {"rx_bytes": 0}},
            },
        }
    )

    assert report == {
        "status": "passed",
        "checked_routes": 2,
        "routes": [
            {"name": "servers", "status_code": 200, "forbidden_markers": []},
            {"name": "metrics", "status_code": 200, "forbidden_markers": []},
        ],
    }
