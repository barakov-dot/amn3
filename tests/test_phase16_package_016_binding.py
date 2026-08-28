from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-016"
PREVIOUS_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-015"
PREVIOUS = ROOT / "packaging" / PREVIOUS_ID
CONTRACT = ROOT / "packaging/phase16-awg3-family-3-1-spain-pilot-contract"


def load(relative: str):
    spec = importlib.util.spec_from_file_location("phase16_binding_test", ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Package016BindingTest(unittest.TestCase):
    def test_manifest_admission_is_revision_016_bound(self):
        package = load("scripts/phase16_awg31_package.py")
        previous = json.loads((PREVIOUS / "manifest.json").read_bytes())
        # An in-memory admission fixture, not a package or published manifest.
        current = json.loads(json.dumps(previous))
        current["package_id"] = PACKAGE_ID
        current["tooling"]["branch"] = "codex/phase16-awg3-family-3-1-spain-pilot-016"
        unsigned = dict(current)
        unsigned.pop("package_identity_sha256")
        raw = (json.dumps(unsigned, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
        current["package_identity_sha256"] = hashlib.sha256(raw).hexdigest()
        try:
            accepted = package.validate_manifest(current)
        except package.PackageContractError as error:
            self.fail(f"valid revision-016 admission fixture was rejected: {error}")
        self.assertEqual(accepted["package_id"], PACKAGE_ID)
        with self.assertRaisesRegex(package.PackageContractError, "manifest package identity"):
            package.validate_manifest(previous)
        current["package_identity_sha256"] = "0" * 64
        with self.assertRaisesRegex(package.PackageContractError, "package identity mismatch"):
            package.validate_manifest(current)

    def test_active_bindings_are_revision_016(self):
        package = load("scripts/phase16_awg31_package.py")
        self.assertEqual(package.PACKAGE_ID, PACKAGE_ID)
        self.assertEqual(package.TOOLING_BRANCH, "codex/phase16-awg3-family-3-1-spain-pilot-016")
        self.assertEqual(package.SOURCE_BRANCH, "codex/phase16-awg3-family-3-1-spain-pilot")
        for path in (
            "scripts/phase16_preflight_contract.py",
            "scripts/vps/phase16_stage_support.py",
            "scripts/vps/phase16_controlled_stage_coordinator.py",
        ):
            self.assertEqual(load(path).PACKAGE_ID, PACKAGE_ID)
        for name in ("package-manifest.schema.json", "preflight-evidence.schema.json", "failure-outcome.schema.json"):
            document = json.loads((CONTRACT / name).read_bytes())
            self.assertEqual(document["properties"]["package_id"]["const"], PACKAGE_ID)
        manifest_schema = json.loads((CONTRACT / "package-manifest.schema.json").read_bytes())
        self.assertEqual(manifest_schema["properties"]["tooling"]["properties"]["branch"]["const"], package.TOOLING_BRANCH)
        self.assertEqual(json.loads((CONTRACT / "resource-plan.json").read_bytes()), package.RESOURCE_PLAN)
        # These are declarative package bindings, not assertions about implementation shape.
        for path, pattern in (
            ("scripts/vps/phase16_application_stage_remote.sh", r"^package_id='([^']+)'$"),
            ("scripts/vps/phase16_awg31_runtime_stage_remote.sh", r"^package_id='([^']+)'$"),
            ("scripts/vps/phase16_spain_readonly_preflight_remote.sh", r'^PACKAGE_ID = "([^"]+)"$'),
            ("scripts/vps/phase16_spain_readonly_preflight_ssh_runner.ps1", r"^\$script:Phase16PackageId = '([^']+)'$"),
            ("scripts/vps/phase16_controlled_stage_ssh_runner.ps1", r"^\$script:Phase16ControlledStagePackageId = '([^']+)'$"),
        ):
            self.assertEqual(re.findall(pattern, (ROOT / path).read_text(encoding="utf-8"), re.M), [PACKAGE_ID])

    def test_package_015_all_original_bytes_remain_immutable(self):
        manifest_bytes = (PREVIOUS / "manifest.json").read_bytes()
        self.assertEqual(hashlib.sha256(manifest_bytes).hexdigest(), "f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74")
        manifest = json.loads(manifest_bytes)
        self.assertEqual(manifest["package_identity_sha256"], "7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509")
        self.assertEqual(len(manifest["entries"]), 171)
        expected = {"manifest.json"}
        for entry in manifest["entries"]:
            expected.add(entry["path"])
            body = (PREVIOUS / entry["path"]).read_bytes()
            self.assertEqual(len(body), entry["size"])
            self.assertEqual(hashlib.sha256(body).hexdigest(), entry["sha256"])
        self.assertEqual({path.relative_to(PREVIOUS).as_posix() for path in PREVIOUS.rglob("*") if path.is_file()}, expected)

    def test_preflight_awg2_and_runtime_contracts_change_only_package_binding(self):
        for path in (
            "scripts/phase16_preflight_contract.py",
            "scripts/vps/phase16_spain_readonly_preflight_remote.sh",
            "scripts/vps/phase16_spain_readonly_preflight_ssh_runner.ps1",
            "scripts/vps/phase16_application_stage_remote.sh",
            "scripts/vps/phase16_awg31_runtime_stage_remote.sh",
            "scripts/vps/phase16_stage_support.py",
            "scripts/vps/phase16_controlled_stage_coordinator.py",
            "packaging/phase16-awg3-family-3-1-spain-pilot-contract/resource-plan.json",
        ):
            current = (ROOT / path).read_bytes().replace(PACKAGE_ID.encode(), PREVIOUS_ID.encode())
            self.assertEqual(current, (PREVIOUS / "tooling" / path).read_bytes(), path)

    def test_packaged_runner_changes_only_package_binding_from_approved_commit(self):
        # Exact approved bytes from 392cc339, not the older immutable 015 runner.
        # Historical package binding belongs to the frozen artifact, not local
        # source that may receive separately authorized, unpackaged diagnostics.
        current = (ROOT / "packaging" / PACKAGE_ID / "tooling/scripts/vps/phase16_controlled_stage_ssh_runner.ps1").read_bytes()
        normalized = current.replace(PACKAGE_ID.encode(), PREVIOUS_ID.encode())
        self.assertEqual(
            hashlib.sha256(normalized).hexdigest(),
            "fbdeda5f061eda91e8ca835e5b7c95b1233c4e6698ef497b33374ab353711635",
        )

    def test_python_and_powershell_bind_the_same_exact_rollback_scope(self):
        scope = {
            "application_ledger": "/var/lib/amn2-phase16/stage/application.json",
            "application_release": "/opt/amn2-spain/releases/phase16-awg3-family-3-1-spain-pilot-20260824-016",
            "backup_policy": "preserve_checksum_bound_sqlite_backup",
            "coordinator_ledger": "/var/lib/amn2-phase16/stage/coordinator.json",
            "package_root": "/var/lib/amn2-phase16/package",
            "runtime_ledger": "/var/lib/amn2-phase16/stage/awg31-runtime.json",
            "runtime_resources": [
                "/etc/systemd/system/amn2-spain-awg3.service", "/var/lib/amn2-spain/awg3",
                "container:amn2-spain-awg3", "network:amn2sp3",
            ],
            "schema": "amn2.phase16.controlled-stage-rollback-scope.v1",
        }
        raw = (json.dumps(scope, sort_keys=True, separators=(",", ":")) + "\n").encode()
        expected = hashlib.sha256(raw).hexdigest()
        coordinator = load("scripts/vps/phase16_controlled_stage_coordinator.py")
        self.assertEqual(coordinator.ROLLBACK_SCOPE, scope)
        self.assertEqual(coordinator.rollback_scope_sha256(), expected)
        runner = ROOT / "scripts/vps/phase16_controlled_stage_ssh_runner.ps1"
        command = f". '{str(runner).replace(chr(39), chr(39) * 2)}'\n"
        command += "[Console]::Out.Write((Get-Phase16CanonicalJsonSha256 -Value (Get-Phase16ControlledStageRollbackScope)))"
        result = subprocess.run(
            [r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True, text=True, check=False, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, expected)


if __name__ == "__main__":
    unittest.main()
