from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "packaging" / "phase15-dual-protocol-bootstrap-contract"
SCRIPT = ROOT / "scripts" / "phase15_dual_protocol_package.py"
PACKAGE_ID = "phase15-dual-protocol-bootstrap-20260811-001"
SHA = "a" * 64
HEAD = "b" * 40


def load_package_module():
    if not SCRIPT.is_file():
        pytest.fail("Phase 15 package implementation is missing")
    spec = importlib.util.spec_from_file_location("phase15_package", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def manifest() -> dict[str, object]:
    entries = [
        {
            "gate": "LOCAL_VERIFY",
            "mode": "0644",
            "path": "source/app/main.py",
            "role": "application_snapshot",
            "rollback_role": "application",
            "secret_classification": "none",
            "sha256": SHA,
            "size": 1,
        },
        {
            "gate": "LOCAL_VERIFY",
            "mode": "0644",
            "path": "source/requirements/phase15-runtime-py312.lock",
            "role": "runtime_dependency_lock",
            "rollback_role": "application",
            "secret_classification": "none",
            "sha256": "c" * 64,
            "size": 2,
        },
        {
            "gate": "LOCAL_VERIFY",
            "mode": "0644",
            "path": "source/requirements/phase15-test-py312.lock",
            "role": "test_dependency_lock",
            "rollback_role": "application",
            "secret_classification": "none",
            "sha256": "d" * 64,
            "size": 2,
        },
        {
            "gate": "LOCAL_VERIFY",
            "mode": "0644",
            "path": "tooling/research/amn2/phase14-dual-protocol-application-readiness-receipt.md",
            "role": "phase14_receipt",
            "rollback_role": "operator",
            "secret_classification": "none",
            "sha256": "d33e69b53c7397c567b16c4f1caea12af97969d9436d3e95e6038148054aa982",
            "size": 3,
        },
        {
            "gate": "LOCAL_VERIFY",
            "mode": "0644",
            "path": "tooling/research/amn2/phase15-source-readiness-receipt.md",
            "role": "phase15_source_receipt",
            "rollback_role": "operator",
            "secret_classification": "none",
            "sha256": "f" * 64,
            "size": 4,
        },
    ]
    value: dict[str, object] = {
        "dependency_locks": {
            "runtime": {
                "path": "source/requirements/phase15-runtime-py312.lock",
                "sha256": "c" * 64,
            },
            "test": {
                "path": "source/requirements/phase15-test-py312.lock",
                "sha256": "d" * 64,
            },
        },
        "entries": entries,
        "package_id": PACKAGE_ID,
        "package_identity_sha256": "e" * 64,
        "receipts": {
            "phase14": {
                "commit": "4e1052c079e1e25031a6c80f4dae1763e457ca48",
                "path": "research/amn2/phase14-dual-protocol-application-readiness-receipt.md",
                "sha256": "d33e69b53c7397c567b16c4f1caea12af97969d9436d3e95e6038148054aa982",
            },
            "phase15_source": {
                "path": "research/amn2/phase15-source-readiness-receipt.md",
                "sha256": "f" * 64,
            },
        },
        "schema": "amn2.phase15.package-manifest.v1",
        "source": {
            "branch": "codex/phase15-local-package-bootstrap-readiness",
            "head": HEAD,
        },
    }
    unsigned = dict(value)
    unsigned.pop("package_identity_sha256")
    value["package_identity_sha256"] = hashlib.sha256(canonical(unsigned)).hexdigest()
    return value


def test_contract_bundle_is_independent_canonical_and_complete() -> None:
    package = load_package_module()
    expected = {
        "package-manifest.schema.json": "amn2.phase15.package-manifest.v1",
        "preflight-evidence.schema.json": "amn2.phase15.readonly-preflight-evidence.v1",
        "failure-outcome.schema.json": "amn2.phase15.readonly-preflight-failure.v1",
    }
    for name, schema_id in expected.items():
        raw = (CONTRACT_ROOT / name).read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf")
        value = json.loads(raw.decode("utf-8"))
        assert raw == canonical(value)
        assert value["$id"] == schema_id
        assert "phase13" not in raw.decode("utf-8").casefold()
        assert value["additionalProperties"] is False

    resource_raw = (CONTRACT_ROOT / "resource-plan.json").read_bytes()
    resource_plan = json.loads(resource_raw.decode("utf-8"))
    assert resource_raw == canonical(resource_plan)
    assert resource_plan == package.RESOURCE_PLAN


def test_manifest_schema_requires_all_identity_and_entry_contracts() -> None:
    schema = json.loads((CONTRACT_ROOT / "package-manifest.schema.json").read_text("utf-8"))
    assert set(schema["required"]) == {
        "schema",
        "package_id",
        "source",
        "receipts",
        "dependency_locks",
        "entries",
        "package_identity_sha256",
    }
    entry = schema["properties"]["entries"]["items"]
    assert set(entry["required"]) == {
        "path",
        "size",
        "sha256",
        "role",
        "mode",
        "secret_classification",
        "gate",
        "rollback_role",
    }
    assert "secret" not in entry["properties"]["secret_classification"]["enum"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value["entries"].append(copy.deepcopy(value["entries"][0])),
        lambda value: value["entries"].append(
            {**copy.deepcopy(value["entries"][0]), "path": "SOURCE/App/Main.py"}
        ),
        lambda value: value["entries"][0].__setitem__("path", "source\\app\\main.py"),
        lambda value: value["entries"][0].__setitem__("path", "C:/source/app/main.py"),
        lambda value: value["entries"][0].__setitem__("path", "source/../app/main.py"),
        lambda value: value["entries"].reverse(),
        lambda value: value["entries"][0].pop("sha256"),
        lambda value: value["entries"][0].__setitem__("secret_classification", "secret"),
        lambda value: value["entries"][0].__setitem__(
            "path", "tooling/packaging/phase13-awg3-preflight/manifest.json"
        ),
    ],
)
def test_manifest_validator_rejects_unsafe_or_stale_inventory(mutate) -> None:
    package = load_package_module()
    value = manifest()
    mutate(value)
    with pytest.raises(package.PackageContractError):
        package.validate_manifest(value, verify_identity=False)


def test_manifest_validator_rejects_sorted_case_colliding_paths() -> None:
    package = load_package_module()
    value = manifest()
    colliding = copy.deepcopy(value["entries"][0])
    colliding["path"] = "source/App/main.py"
    value["entries"].append(colliding)
    value["entries"].sort(key=lambda entry: entry["path"])

    with pytest.raises(package.PackageContractError, match="case-colliding"):
        package.validate_manifest(value, verify_identity=False)


@pytest.mark.parametrize(
    "raw",
    [
        b'\xef\xbb\xbf{"a":1}\n',
        b'{"a":"\xff"}\n',
        b'{"a":1, "b":2}\n',
        b'{"a":1,"a":2}\n',
    ],
)
def test_strict_json_loader_rejects_bom_non_utf8_noncanonical_and_duplicates(raw: bytes) -> None:
    package = load_package_module()
    with pytest.raises(package.PackageContractError):
        package.load_canonical_json(raw, label="fixture")


def test_resource_plan_reserves_only_future_awg3_contour() -> None:
    package = load_package_module()
    assert package.RESOURCE_PLAN == {
        "awg2_resources_unchanged": True,
        "future_only": True,
        "package_id": PACKAGE_ID,
        "resources": {
            "bridge": "amn2sp3br0",
            "config_path": "/var/lib/amn2-spain/awg3/awg3.conf",
            "container": "amn2-spain-awg3",
            "container_cidr": "172.29.252.0/28",
            "interface": "awg3",
            "server_address": "10.212.13.1/24",
            "service": "amn2-spain-awg3.service",
            "state_root": "/var/lib/amn2-spain/awg3",
            "udp_port": 30002,
            "vpn_cidr": "10.212.13.0/24",
        },
        "schema": "amn2.phase15.resource-plan.v1",
    }
