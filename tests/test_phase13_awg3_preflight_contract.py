import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "packaging" / "phase13-awg3-preflight"
FOUNDATION_PATH = ARTIFACT_ROOT / "phase12-equality-foundation.json"
MANIFEST_SCHEMA = ARTIFACT_ROOT / "manifest.schema.json"
EVIDENCE_SCHEMA = ARTIFACT_ROOT / "evidence.schema.json"
FAILURE_SCHEMA = ARTIFACT_ROOT / "failure-evidence.schema.json"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_every_object_is_closed(value: object) -> None:
    if isinstance(value, dict):
        if value.get("type") == "object":
            assert value["additionalProperties"] is False
        for nested in value.values():
            assert_every_object_is_closed(nested)
    elif isinstance(value, list):
        for nested in value:
            assert_every_object_is_closed(nested)


def test_phase12_foundation_contains_exact_accepted_safe_facts():
    foundation = load_json(FOUNDATION_PATH)

    assert foundation == {
        "schema": "amn2.phase13.phase12-equality-foundation.v1",
        "source_head": "ff115b63ca1329640ca13ae0a502d155f99b456b",
        "foreign": {
            "persistent_entries": 153,
            "stable_sha256": (
                "f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8"
            ),
            "equality_receipt_sha256": (
                "bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704"
            ),
        },
        "awg2": {
            "udp_port": 30001,
            "vpn_cidr": "10.212.12.0/24",
            "route_device": "amn2spbr0",
            "persistent_peers": 7,
            "live_peers": 7,
            "restart_count": 59,
            "forward_rule_count": 3,
            "web_listener": "127.0.0.1:3031",
            "bot_enabled": False,
        },
    }


def test_all_phase13_schemas_are_recursively_closed_objects():
    for path in (MANIFEST_SCHEMA, EVIDENCE_SCHEMA, FAILURE_SCHEMA):
        schema = load_json(path)

        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert schema["required"]
        assert_every_object_is_closed(schema)


def test_manifest_schema_requires_exact_fail_closed_contract():
    schema = load_json(MANIFEST_SCHEMA)

    assert set(schema["required"]) == {
        "schema",
        "outcome_id",
        "created_at",
        "expires_at",
        "target_role",
        "source_base",
        "source_head",
        "spain_overlay",
        "candidate",
        "artifacts",
        "foundation_sha256",
        "allowed_command_families",
        "forbidden_actions",
        "max_attempts",
        "remote_write_allowed",
        "package_build_allowed",
        "live_action_authorized",
    }
    assert schema["properties"]["schema"] == {
        "const": "amn2.phase13.awg3-readonly-preflight-manifest.v1"
    }
    assert schema["properties"]["target_role"] == {"const": "spain-primary"}
    assert schema["properties"]["source_base"] == {
        "const": "55dc243b8e6c6bdb57f8301b56326e4cd4072d19"
    }
    assert schema["properties"]["source_head"] == {
        "const": "ff115b63ca1329640ca13ae0a502d155f99b456b"
    }
    assert schema["properties"]["spain_overlay"] == {
        "const": "f1bf099ddb47da26a4080714376babaf5b0de92c"
    }
    assert schema["properties"]["max_attempts"] == {"const": 1}
    assert schema["properties"]["remote_write_allowed"] == {"const": False}
    assert schema["properties"]["package_build_allowed"] == {"const": False}
    assert schema["properties"]["live_action_authorized"] == {"const": False}
