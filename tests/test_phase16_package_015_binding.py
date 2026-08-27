from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-015"
PREVIOUS_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-014"
PREVIOUS = ROOT / "packaging" / PREVIOUS_ID
CONTRACT = ROOT / "packaging/phase16-awg3-family-3-1-spain-pilot-contract"


def load(relative: str):
    spec = importlib.util.spec_from_file_location("phase16_binding_test", ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Package015BindingTest(unittest.TestCase):
    def test_active_bindings_are_revision_015(self):
        package = load("scripts/phase16_awg31_package.py")
        self.assertEqual(package.PACKAGE_ID, PACKAGE_ID)
        self.assertEqual(package.TOOLING_BRANCH, "codex/phase16-awg3-family-3-1-spain-pilot-015")
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

    def test_package_014_all_original_bytes_remain_immutable(self):
        manifest_bytes = (PREVIOUS / "manifest.json").read_bytes()
        self.assertEqual(hashlib.sha256(manifest_bytes).hexdigest(), "844499afb51ca4cd5eacc8a395c003aabba39ffd02723ae4e95e4d28105b6cb1")
        manifest = json.loads(manifest_bytes)
        self.assertEqual(manifest["package_identity_sha256"], "d741006c3b0d788700020a93ac02a3bb5f35a1ec89d9497902ef7c8ac5726f19")
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
            "packaging/phase16-awg3-family-3-1-spain-pilot-contract/resource-plan.json",
        ):
            current = (ROOT / path).read_bytes().replace(PACKAGE_ID.encode(), PREVIOUS_ID.encode())
            self.assertEqual(current, (PREVIOUS / "tooling" / path).read_bytes(), path)
        # The frozen 015 runner remains original; mutable runner exit/stdin fixes
        # have executable regression coverage instead of a source-byte equality.
        runner_path = "scripts/vps/phase16_controlled_stage_ssh_runner.ps1"
        frozen_runner = ROOT / "packaging" / PACKAGE_ID / "tooling" / runner_path
        self.assertEqual(
            frozen_runner.read_bytes().replace(PACKAGE_ID.encode(), PREVIOUS_ID.encode()),
            (PREVIOUS / "tooling" / runner_path).read_bytes(),
        )

    def test_python_and_powershell_bind_the_same_exact_rollback_scope(self):
        scope = {
            "application_ledger": "/var/lib/amn2-phase16/stage/application.json",
            "application_release": "/opt/amn2-spain/releases/phase16-awg3-family-3-1-spain-pilot-20260824-015",
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
