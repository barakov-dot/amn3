import copy
import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "packaging" / "phase13-bot-web-migration"


class ContractError(ValueError):
    pass


def load_schema(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_ROOT / name).read_text(encoding="utf-8"))


def validate(value: object, schema: dict[str, object], *, path: str = "$") -> None:
    """Small test-only JSON Schema subset for the strict contracts in Task 1."""
    if "const" in schema and value != schema["const"]:
        raise ContractError(f"{path}: const")
    if "enum" in schema and value not in schema["enum"]:
        raise ContractError(f"{path}: enum")
    if schema.get("type") == "object":
        if not isinstance(value, dict):
            raise ContractError(f"{path}: object")
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise ContractError(f"{path}: required {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = set(value) - set(properties)
            if unknown:
                raise ContractError(f"{path}: additional {sorted(unknown)[0]}")
        for key, nested in properties.items():
            if key in value:
                validate(value[key], nested, path=f"{path}.{key}")
        return
    if schema.get("type") == "array":
        if not isinstance(value, list):
            raise ContractError(f"{path}: array")
        if len(value) < schema.get("minItems", 0):
            raise ContractError(f"{path}: minItems")
        items = schema.get("items")
        if isinstance(items, dict):
            for index, item in enumerate(value):
                validate(item, items, path=f"{path}[{index}]")
        return
    if schema.get("type") == "string":
        if not isinstance(value, str):
            raise ContractError(f"{path}: string")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            raise ContractError(f"{path}: pattern")
        return
    if schema.get("type") == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            raise ContractError(f"{path}: integer")
        if value < schema.get("minimum", value):
            raise ContractError(f"{path}: minimum")
        return
    if schema.get("type") == "boolean" and not isinstance(value, bool):
        raise ContractError(f"{path}: boolean")


def assert_every_object_is_closed(value: object) -> None:
    if isinstance(value, dict):
        if value.get("type") == "object":
            assert value["additionalProperties"] is False
        for nested in value.values():
            assert_every_object_is_closed(nested)
    elif isinstance(value, list):
        for nested in value:
            assert_every_object_is_closed(nested)


def safety_receipt() -> dict[str, bool]:
    return {
        "mutation_attempted": False,
        "raw_output_persisted": False,
        "secret_bearing_data_persisted": False,
    }


def valid_audit_payload() -> dict[str, object]:
    return {
        "schema": "amn2.phase13.bot-web-audit.v1",
        "role": "usa-source",
        "checked_at": "2026-08-02T12:00:00Z",
        "services": {
            "web_active": True,
            "bot_active": True,
            "web_loopback_only": True,
        },
        "database": {
            "integrity_ok": True,
            "foreign_key_violations": 0,
            "table_count": 15,
            "schema_sha256": "a" * 64,
            "counts_sha256": "b" * 64,
        },
        "environment": {
            "telegram_bot_token_present": True,
            "app_secret_present": True,
            "web_password_hash_present": True,
            "session_secret_present": True,
        },
        "required_artifacts": {
            "database_readable": True,
            "environment_reference_proof_available": True,
        },
        "safety_receipt": safety_receipt(),
    }


def artifact(path: str, sha256: str) -> dict[str, object]:
    return {"path": path, "size": 1, "sha256": sha256}


def valid_manifest() -> dict[str, object]:
    return {
        "schema": "amn2.phase13.bot-web-migration-manifest.v1",
        "outcome_id": "bot-web-migration-001",
        "created_at": "2026-08-02T12:00:00Z",
        "expires_at": "2026-08-03T12:00:00Z",
        "source_role": "usa-source",
        "target_role": "spain-target",
        "source_audit_sha256": "c" * 64,
        "target_audit_sha256": "d" * 64,
        "artifacts": {
            "source_full_backup": artifact("source-full-backup.enc", "e" * 64),
            "target_before_backup": artifact("target-before-backup.enc", "f" * 64),
            "merged_target_db": artifact("merged-target.sqlite3.enc", "0" * 64),
            "merge_preview": artifact("merge-preview.json", "1" * 64),
            "rollback_plan": artifact("rollback-plan.json", "2" * 64),
        },
        "live_mutation_authorized": False,
    }


def valid_migration_plan() -> dict[str, object]:
    return {
        "schema": "amn2.phase13.bot-web-migration-plan.v1",
        "migration_id": "bot-web-migration-001",
        "source_role": "usa-source",
        "target_role": "spain-target",
        "source_audit_sha256": "3" * 64,
        "target_audit_sha256": "4" * 64,
        "preserve_target_app_secrets": True,
        "api_tokens_reissue_required": 12,
        "usable_secret_records_imported": 0,
        "live_mutation_authorized": False,
    }


def valid_failure_payload() -> dict[str, object]:
    return {
        "schema": "amn2.phase13.bot-web-migration-failure.v1",
        "outcome_id": "bot-web-migration-001",
        "checked_at": "2026-08-02T12:00:00Z",
        "stage": "backup",
        "reason_code": "checksum_mismatch",
        "decision": "stop",
        "safety_receipt": safety_receipt(),
    }


@pytest.mark.parametrize(
(
    "schema_name",
    "payload_factory",
),
[
    ("audit-evidence.schema.json", valid_audit_payload),
    ("migration-plan.schema.json", valid_migration_plan),
    ("manifest.schema.json", valid_manifest),
    ("failure-evidence.schema.json", valid_failure_payload),
],
)
def test_all_phase13_bot_web_schemas_are_closed_and_validate_their_contracts(
    schema_name: str, payload_factory
) -> None:
    schema = load_schema(schema_name)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert_every_object_is_closed(schema)
    validate(payload_factory(), schema)


def test_audit_schema_rejects_raw_secret_and_identifier_fields() -> None:
    payload = valid_audit_payload()
    payload["telegram_bot_token"] = "forbidden"

    with pytest.raises(ContractError, match="additional telegram_bot_token"):
        validate(payload, load_schema("audit-evidence.schema.json"))

    identifier = valid_audit_payload()
    identifier["telegram_admin_identifier"] = "forbidden"
    with pytest.raises(ContractError, match="additional telegram_admin_identifier"):
        validate(identifier, load_schema("audit-evidence.schema.json"))


def test_manifest_requires_every_bound_artifact_sha256() -> None:
    payload = valid_manifest()
    del payload["artifacts"]["merged_target_db"]

    with pytest.raises(ContractError, match="required merged_target_db"):
        validate(payload, load_schema("manifest.schema.json"))

    invalid_hash = copy.deepcopy(valid_manifest())
    invalid_hash["artifacts"]["merged_target_db"]["sha256"] = "A" * 64
    with pytest.raises(ContractError, match="pattern"):
        validate(invalid_hash, load_schema("manifest.schema.json"))
