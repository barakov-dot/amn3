from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "packaging" / "phase15-dual-protocol-bootstrap-contract"
SCRIPT = ROOT / "scripts" / "phase15_dual_protocol_package.py"
PACKAGE_ID = "phase15-dual-protocol-bootstrap-20260811-001"
SHA = "a" * 64
HEAD = "b" * 40
TOOLING_HEAD = "c" * 40
REQUIRED_ENTRY_SPECS = (
    ("source/README.md", "operator_documentation", "OPERATOR", "operator"),
    ("source/app/db/phase15_bootstrap.py", "callback_bootstrap", "APPLICATION_STAGE", "application"),
    ("source/app/main.py", "application_snapshot", "APPLICATION_STAGE", "application"),
    ("source/app/services/phase15_bootstrap.py", "callback_bootstrap", "APPLICATION_STAGE", "application"),
    ("source/app/services/telegram_callback_state.py", "callback_bootstrap", "APPLICATION_STAGE", "application"),
    ("source/requirements/phase15-runtime-py312.lock", "runtime_dependency_lock", "LOCAL_VERIFY", "application"),
    ("source/requirements/phase15-test-py312.lock", "test_dependency_lock", "LOCAL_VERIFY", "application"),
    ("source/scripts/phase15_dependency_lock.py", "dependency_lock_tool", "LOCAL_VERIFY", "application"),
    ("tooling/docs/superpowers/plans/2026-08-11-amn2-phase15-local-package-bootstrap-readiness.md", "operator_documentation", "OPERATOR", "operator"),
    ("tooling/docs/superpowers/specs/2026-08-11-amn2-phase15-local-package-bootstrap-readiness-design.ru.md", "operator_documentation", "OPERATOR", "operator"),
    ("tooling/packaging/phase15-dual-protocol-bootstrap-contract/failure-outcome.schema.json", "failure_schema", "LOCAL_VERIFY", "preflight"),
    ("tooling/packaging/phase15-dual-protocol-bootstrap-contract/package-manifest.schema.json", "contract_schema", "LOCAL_VERIFY", "none"),
    ("tooling/packaging/phase15-dual-protocol-bootstrap-contract/preflight-evidence.schema.json", "preflight_evidence_schema", "LOCAL_VERIFY", "preflight"),
    ("tooling/packaging/phase15-dual-protocol-bootstrap-contract/resource-plan.json", "resource_plan", "LOCAL_VERIFY", "awg3-runtime"),
    ("tooling/research/amn2/phase14-dual-protocol-application-readiness-receipt.md", "phase14_receipt", "LOCAL_VERIFY", "operator"),
    ("tooling/research/amn2/phase15-source-readiness-receipt.md", "phase15_source_receipt", "LOCAL_VERIFY", "operator"),
    ("tooling/scripts/phase15_dual_protocol_package.py", "package_verifier", "LOCAL_VERIFY", "none"),
    ("tooling/scripts/phase15_preflight_contract.py", "preflight_contract", "PREFLIGHT", "preflight"),
    ("tooling/scripts/vps/phase15_application_stage_remote.sh", "stage_envelope", "APPLICATION_STAGE", "application"),
    ("tooling/scripts/vps/phase15_awg3_runtime_stage_remote.sh", "stage_envelope", "AWG3_RUNTIME_STAGE", "awg3-runtime"),
    ("tooling/scripts/vps/phase15_spain_readonly_preflight_remote.sh", "readonly_collector", "PREFLIGHT", "preflight"),
    ("tooling/scripts/vps/phase15_spain_readonly_preflight_ssh_runner.ps1", "readonly_collector", "PREFLIGHT", "preflight"),
)


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
    entries = []
    for path, role, gate, rollback_role in REQUIRED_ENTRY_SPECS:
        digest = hashlib.sha256(path.encode("utf-8")).hexdigest()
        if path.endswith("phase15-runtime-py312.lock"):
            digest = "c" * 64
        elif path.endswith("phase15-test-py312.lock"):
            digest = "d" * 64
        elif path.endswith("phase14-dual-protocol-application-readiness-receipt.md"):
            digest = "d33e69b53c7397c567b16c4f1caea12af97969d9436d3e95e6038148054aa982"
        elif path.endswith("phase15-source-readiness-receipt.md"):
            digest = "f" * 64
        entries.append({
            "gate": gate,
            "mode": "0755" if path.endswith(".sh") else "0644",
            "path": path,
            "role": role,
            "rollback_role": rollback_role,
            "secret_classification": "none",
            "sha256": digest,
            "size": len(path),
        })
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
        "tooling": {
            "branch": "codex/phase15-local-package-bootstrap-readiness",
            "head": TOOLING_HEAD,
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
        "tooling",
        "receipts",
        "dependency_locks",
        "entries",
        "package_identity_sha256",
    }
    entries_schema = schema["properties"]["entries"]
    assert "x-casefold-unique-paths" not in entries_schema
    assert "x-sorted-by" not in entries_schema
    entry, closed_inventory = entries_schema["items"]["allOf"]
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
    assert entries_schema["uniqueItems"] is True
    branches = closed_inventory["oneOf"]
    fixed_paths = {
        branch["properties"]["path"]["const"]
        for branch in branches
        if "const" in branch.get("properties", {}).get("path", {})
    }
    assert fixed_paths == {item[0] for item in REQUIRED_ENTRY_SPECS}
    dynamic = next(
        branch for branch in branches
        if "pattern" in branch.get("properties", {}).get("path", {})
    )
    assert dynamic["properties"]["path"]["pattern"].startswith("^source/app/")
    assert dynamic["properties"]["role"] == {"const": "application_snapshot"}
    assert dynamic["properties"]["gate"] == {"const": "APPLICATION_STAGE"}
    assert dynamic["properties"]["rollback_role"] == {"const": "application"}
    assert dynamic["properties"]["secret_classification"] == {"const": "none"}
    path_pattern = entry["properties"]["path"]["pattern"]
    for invalid in ("source/../x", "source//x", "source/./x", "/source/x", "C:/source/x", "source\\x"):
        assert re.fullmatch(path_pattern, invalid) is None


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
    "missing_path",
    [
        "source/requirements/phase15-runtime-py312.lock",
        "tooling/packaging/phase15-dual-protocol-bootstrap-contract/resource-plan.json",
        "tooling/scripts/phase15_dual_protocol_package.py",
        "tooling/scripts/vps/phase15_spain_readonly_preflight_remote.sh",
        "tooling/scripts/vps/phase15_application_stage_remote.sh",
    ],
)
def test_manifest_validator_rejects_resigned_required_entry_omission(missing_path: str) -> None:
    package = load_package_module()
    value = manifest()
    value["entries"] = [entry for entry in value["entries"] if entry["path"] != missing_path]
    unsigned = dict(value)
    unsigned.pop("package_identity_sha256")
    value["package_identity_sha256"] = hashlib.sha256(canonical(unsigned)).hexdigest()

    with pytest.raises(package.PackageContractError, match="required package entry"):
        package.validate_manifest(value)


def test_manifest_validator_rejects_resigned_lock_and_tooling_rebinding() -> None:
    package = load_package_module()
    value = manifest()
    value["dependency_locks"]["runtime"] = dict(value["dependency_locks"]["test"])
    value["tooling"]["head"] = value["source"]["head"]
    unsigned = dict(value)
    unsigned.pop("package_identity_sha256")
    value["package_identity_sha256"] = hashlib.sha256(canonical(unsigned)).hexdigest()

    with pytest.raises(package.PackageContractError, match="exact dependency lock|tooling identity"):
        package.validate_manifest(value)


@pytest.mark.parametrize(
    "entry",
    [
        {
            "gate": "OPERATOR",
            "mode": "0644",
            "path": "tooling/extra.txt",
            "role": "operator_documentation",
            "rollback_role": "operator",
            "secret_classification": "none",
            "sha256": SHA,
            "size": 1,
        },
        {
            "gate": "OPERATOR",
            "mode": "0644",
            "path": "source/app/extra.py",
            "role": "operator_documentation",
            "rollback_role": "operator",
            "secret_classification": "none",
            "sha256": SHA,
            "size": 1,
        },
    ],
)
def test_manifest_validator_rejects_resigned_unexpected_or_misclassified_entry(
    entry: dict[str, object],
) -> None:
    package = load_package_module()
    value = manifest()
    value["entries"].append(entry)
    value["entries"].sort(key=lambda item: item["path"])
    unsigned = dict(value)
    unsigned.pop("package_identity_sha256")
    value["package_identity_sha256"] = hashlib.sha256(canonical(unsigned)).hexdigest()

    with pytest.raises(package.PackageContractError, match="unexpected package entry"):
        package.validate_manifest(value)


def test_brand_png_contract_pins_exact_approved_blobs() -> None:
    package = load_package_module()
    assert package.APPROVED_BRAND_PNGS == {
        "app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png": (
            2_950_469,
            "40acd9465dc9fda06644d2d829da996e1d9bf6c856e95298b624b31154fec791",
        ),
        "app/bot/assets/NEOBYATNAYA-AMNZ-LANGUAGE-HEADER.png": (
            2_647_131,
            "bbddfa72d1d1fc37e412d2f4a9b4124001ff91fbd641635e31a47e008fc4611f",
        ),
        "app/web/static/brand-full.png": (
            2_950_469,
            "40acd9465dc9fda06644d2d829da996e1d9bf6c856e95298b624b31154fec791",
        ),
    }


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
