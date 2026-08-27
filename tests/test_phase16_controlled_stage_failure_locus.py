from __future__ import annotations

from contextlib import ExitStack
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[1]
COORDINATOR = ROOT / "scripts/vps/phase16_controlled_stage_coordinator.py"
DIGEST = "4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d"
MILESTONES = [
    "transaction_created", "package_verified", "request_bound",
    "awg2_before_captured", "package_installed", "claims_issued",
    "application_entry", "application_complete", "runtime_entry",
    "runtime_complete", "awg2_after_captured", "awg2_equality_confirmed",
    "coordinator_outcome_written", "transaction_outcome_written",
]


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def load_coordinator():
    spec = importlib.util.spec_from_file_location("phase16_failure_locus_test", COORDINATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LocalStageHarness:
    """Real coordinator and files; only OS commands and fixed remote roots are faked."""

    def __init__(self, module, root: Path, scenario: str = "success") -> None:
        self.module, self.root, self.scenario = module, root, scenario
        self.commands: list[list[str]] = []
        self.snapshot_count = 0
        self.write_failed = False
        self.paths = {
            "PACKAGE_ROOT": root / "package",
            "TRANSACTION_ROOT": root / "transactions",
            "APPLICATION_RELEASE": root / "release",
            "APPLICATION_LEDGER": root / "application.json",
            "RUNTIME_LEDGER": root / "runtime.json",
            "COORDINATOR_LEDGER": root / "coordinator.json",
            "RUNTIME_STATE_ROOT": root / "runtime-state",
            "RUNTIME_UNIT_PATH": root / "runtime.service",
        }
        self.backup = root / "preserved-backup"
        self.transaction = self.paths["TRANSACTION_ROOT"] / "phase16-local-test-015"
        self.header, self.archive = self.frame()

    def frame(self):
        coordinator_bytes = COORDINATOR.read_bytes()
        files = {
            "tooling/scripts/vps/phase16_controlled_stage_coordinator.py": coordinator_bytes,
            "tooling/scripts/vps/phase16_application_stage_remote.sh": b"application fixture\n",
            "tooling/scripts/vps/phase16_awg31_runtime_stage_remote.sh": b"runtime fixture\n",
        }
        manifest = {
            "entries": [
                {"gate": "CONTROLLED_STAGE", "mode": "0644", "path": name,
                 "role": "stage_coordinator", "rollback_role": "coordinator",
                 "secret_classification": "non_secret", "sha256": hashlib.sha256(body).hexdigest(),
                 "size": len(body)}
                for name, body in sorted(files.items())
            ],
            "package_id": self.module.PACKAGE_ID,
        }
        manifest["package_identity_sha256"] = hashlib.sha256(canonical(manifest)).hexdigest()
        manifest_bytes = canonical(manifest)
        request = {
            "approval_sha256": "a" * 64,
            "expected_current_state_sha256": "b" * 64,
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "package_id": self.module.PACKAGE_ID,
            "package_identity_sha256": manifest["package_identity_sha256"],
            "rollback_scope_sha256": self.module.rollback_scope_sha256(),
            "schema": "amn2.phase16.controlled-stage-request.v1",
            "transaction_id": "phase16-local-test-015",
        }
        approval = (
            "/APPROVE PHASE16 SPAIN APPLICATION_AND_AWG31_STAGE "
            f"PACKAGE_{request['package_id']} IDENTITY_{request['package_identity_sha256']} "
            f"MANIFEST_SHA256_{request['manifest_sha256']} "
            f"STATE_{request['expected_current_state_sha256']} "
            f"ROLLBACK_SCOPE_SHA256_{request['rollback_scope_sha256']} "
            "TRANSACTION_phase16-local-test-015 MANDATORY_ROLLBACK_ON_FAILURE AWG2_UNTOUCHED"
        )
        request["approval_sha256"] = hashlib.sha256(approval.encode("ascii")).hexdigest()
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w") as package:
            package.writestr("manifest.json", manifest_bytes)
            for name, body in files.items():
                package.writestr(name, body)
        return {
            "approval": approval, "request": request,
            "coordinator_sha256": hashlib.sha256(coordinator_bytes).hexdigest(),
        }, archive.getvalue()

    def process(self, arguments, **kwargs):
        args = list(arguments)
        self.commands.append(args)
        stdout, stderr, code = b"", b"", 0
        if args[0] == "/usr/bin/bash":
            env = kwargs["env"]
            claim_path = Path(env["PHASE16_STAGE_CLAIM_FILE"])
            claim = json.loads(claim_path.read_bytes())
            claim.update(status="consumed", consumed_at=claim["issued_at"])
            claim_path.write_bytes(canonical(claim))
            if env["PHASE16_FUTURE_GATE"] == "APPLICATION_STAGE":
                self.backup.write_bytes(b"keep this backup")
                self.paths["APPLICATION_RELEASE"].mkdir()
                self.paths["APPLICATION_LEDGER"].write_bytes(b"{}\n")
                stdout = b'{"general_issuance_enabled":false,"result":"application_staged"}\n'
            elif self.scenario == "runtime_stage":
                code, stderr = 1, b"synthetic-raw-runtime-detail\n"
            else:
                self.paths["RUNTIME_STATE_ROOT"].mkdir()
                self.paths["RUNTIME_UNIT_PATH"].write_bytes(b"unit fixture\n")
                self.paths["RUNTIME_LEDGER"].write_bytes(canonical({"runtime_image_created": False}))
                stdout = b'{"general_issuance_enabled":false,"result":"awg31_runtime_staged"}\n'
        elif args[:2] == ["/usr/bin/systemctl", "is-active"]:
            self.snapshot_count += 1
            stdout = b"active\n"
            if self.snapshot_count == 2 and self.scenario in {"awg2_after", "rollback_error"}:
                code, stderr = 1, b"synthetic-raw-owner-detail\n"
        elif args[:2] == ["/usr/bin/systemctl", "stop"]:
            if self.scenario == "rollback_error":
                raise OSError("synthetic-raw-rollback-detail")
        elif args == ["/usr/bin/systemctl", "daemon-reload"]:
            pass
        elif args[:3] == [
            "/opt/amn2-spain/docker/bin/docker", "--host",
            "unix:///run/amn2-spain-docker/docker.sock",
        ]:
            operation = args[3:]
            if operation[0] == "inspect":
                stdout = b"container-id|true|0\n"
            elif operation[0] == "exec":
                stdout = b"peer-fixture\n"
                if self.snapshot_count == 2 and self.scenario == "awg2_equality":
                    stdout = b"different-peer-fixture\n"
            elif operation[:2] in (["rm", "-f"], ["network", "rm"], ["image", "rm"]):
                pass
            elif operation[:2] == ["image", "ls"]:
                stdout = b""
            else:
                raise AssertionError("unexpected simulated Docker operation")
        else:
            raise AssertionError("unexpected simulated OS command")
        return subprocess.CompletedProcess(args, code, stdout, stderr)

    def __enter__(self):
        self.stack = ExitStack()
        # The remote coordinator is Linux-only: emulate binary POSIX writes on Windows.
        original_open = os.open
        self.stack.enter_context(patch.object(
            self.module.os, "open",
            side_effect=lambda path, flags, *args, **kwargs: original_open(
                path, flags | getattr(os, "O_BINARY", 0), *args, **kwargs,
            ),
        ))
        for name, value in self.paths.items():
            self.stack.enter_context(patch.object(self.module, name, value, create=True))
        remote_paths = {
            "/etc/systemd/system/amn2-spain-awg3.service": self.paths["RUNTIME_UNIT_PATH"],
            "/var/lib/amn2-spain/awg3": self.paths["RUNTIME_STATE_ROOT"],
        }
        self.stack.enter_context(patch.object(
            self.module, "Path", side_effect=lambda value: remote_paths.get(str(value), Path(value)),
        ))
        self.stack.enter_context(patch.object(
            self.module, "PHASE16_EMBEDDED_SOURCE_SHA256",
            self.header["coordinator_sha256"], create=True,
        ))
        self.stack.enter_context(patch.object(
            self.module, "_safe_base", side_effect=lambda: self.paths["TRANSACTION_ROOT"].mkdir(exist_ok=True),
        ))
        self.stack.enter_context(patch.object(self.module.subprocess, "run", side_effect=self.process))
        original = self.module._atomic_json

        def atomic(path, value):
            target = (
                self.scenario == "coordinator_outcome" and path == self.paths["COORDINATOR_LEDGER"]
                or self.scenario == "transaction_outcome" and path == self.transaction / "outcome.json"
                or self.scenario == "milestone_write" and path == self.transaction / "milestones.json"
                and value["last_completed_milestone"] == "runtime_complete"
            )
            if target and not self.write_failed:
                self.write_failed = True
                raise OSError("synthetic-raw-write-detail")
            original(path, value)

        self.stack.enter_context(patch.object(self.module, "_atomic_json", side_effect=atomic))
        return self

    def __exit__(self, *args):
        self.stack.close()

    def execute(self):
        return self.module.execute_stage(self.header, self.archive)

    def failure(self):
        return json.loads((self.transaction / "failure-locus.json").read_bytes())


class ControlledStageFailureLocusTest(unittest.TestCase):
    def setUp(self):
        self.module = load_coordinator()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_consumed_claim_proves_entry_only_and_requires_exact_binding(self):
        with LocalStageHarness(self.module, self.root) as run:
            expected = self.module.build_stage_claim(
                run.header["request"], gate="AWG31_RUNTIME_STAGE", script_bytes=b"fixture\n",
                issued_at="2026-08-27T10:00:00Z", expires_at="2026-08-27T10:05:00Z",
            )
            path = self.root / "claim.json"
            path.write_bytes(canonical(expected))
            self.assertEqual(self.module.classify_claim_entry(path, expected), "issued_not_entered")
            consumed = dict(expected, status="consumed", consumed_at="2026-08-27T10:00:01Z")
            path.write_bytes(canonical(consumed))
            self.assertEqual(self.module.classify_claim_entry(path, expected), "consumed_entry_only")
            for change in ({"manifest_sha256": "d" * 64}, {"extra": "detail"}, {"consumed_at": None}):
                path.write_bytes(canonical(dict(consumed, **change)))
                self.assertEqual(self.module.classify_claim_entry(path, expected), "invalid")
            self.assertEqual(self.module.classify_claim_entry(self.root / "missing", expected), "unavailable")

    def test_runtime_image_class_uses_successful_inventory_not_daemon_error_text(self):
        rows = [
            (0, b"", b"", "absent"),
            (0, f"amneziavpn/amneziawg-go@sha256:{DIGEST}\n".encode(), b"", "present_baseline_unknown"),
            (0, f"docker.io/amneziavpn/amneziawg-go@sha256:{DIGEST}\n".encode(), b"", "present_baseline_unknown"),
            (0, b"<none>@<none>\n", b"", "absent"),
            (0, b"other/image@sha256:" + b"a" * 64 + b"\n", b"", "absent"),
            (0, b"amneziavpn/amneziawg-go@<none>\n", b"", "absent"),
            (1, b"", b"Error: No such image\n", "query_failed"),
            (0, b"", b"warning\n", "query_failed"),
            (0, b"malformed", b"", "query_failed"),
            (0, f"amneziavpn/amneziawg-go@sha256:{DIGEST}\ninvalid\n".encode(), b"", "query_failed"),
            (0, b"x" * 8193, b"", "query_failed"),
        ]
        for code, stdout, stderr, expected in rows:
            with self.subTest(expected=expected, code=code, length=len(stdout)):
                self.assertEqual(self.module.classify_runtime_image_query(code, stdout, stderr), expected)

    def test_stage_process_failures_have_closed_classes_without_raw_text(self):
        rows = [
            (subprocess.CompletedProcess([], 1, b"raw-stdout\n", b"raw-stderr"), "process_exit"),
            (subprocess.CompletedProcess([], 0, b"ok\n", b"raw-stderr"), "stderr_not_empty"),
            (subprocess.CompletedProcess([], 0, b"raw-stdout", b""), "stdout_shape"),
            (subprocess.CompletedProcess([], 0, b"x" * 8193, b""), "output_bound"),
            (subprocess.TimeoutExpired("raw-command", 3, output=b"raw-stdout"), "timeout"),
            (OSError("raw-os-detail"), "os_error"),
        ]
        for process, expected in rows:
            with self.subTest(expected=expected), patch.object(
                self.module.subprocess, "run", **({"side_effect": process} if isinstance(process, Exception) else {"return_value": process}),
            ):
                with self.assertRaises(Exception) as observed:
                    self.module._run_stage(Path("script"), Path("claim"), "AWG31_RUNTIME_STAGE", {
                        "expected_current_state_sha256": "a" * 64,
                        "manifest_sha256": "b" * 64, "package_identity_sha256": "c" * 64,
                        "rollback_scope_sha256": "d" * 64,
                    })
                self.assertEqual(self.module.classify_stage_failure(observed.exception), expected)

    def assert_failure_is_safe(self, run, failure):
        self.assertEqual(set(failure), {
            "application_claim_entry", "completed_milestones", "failure_class", "failure_locus",
            "general_issuance_enabled", "last_completed_milestone", "manifest_sha256",
            "package_id", "package_identity_sha256", "raw_output_persisted", "rollback_milestones",
            "rollback_scope_sha256", "rollback_status", "runtime_claim_entry", "runtime_image",
            "schema", "state_sha256", "transaction_id",
        })
        self.assertEqual(failure["schema"], "amn2.phase16.controlled-stage-failure-locus.v1")
        self.assertEqual(failure["manifest_sha256"], run.header["request"]["manifest_sha256"])
        self.assertEqual(failure["package_identity_sha256"], run.header["request"]["package_identity_sha256"])
        self.assertEqual(failure["state_sha256"], "b" * 64)
        self.assertFalse(failure["raw_output_persisted"])
        self.assertFalse(failure["general_issuance_enabled"])
        self.assertEqual(failure["runtime_image"], "absent")
        raw = (run.transaction / "failure-locus.json").read_bytes()
        self.assertEqual(raw, canonical(failure))
        self.assertNotIn(b"synthetic-raw", raw)
        self.assertTrue(run.backup.exists())
        self.assertFalse(run.paths["PACKAGE_ROOT"].exists())
        self.assertFalse(run.paths["APPLICATION_RELEASE"].exists())
        self.assertFalse(run.paths["APPLICATION_LEDGER"].exists())
        self.assertEqual(json.loads((run.transaction / "outcome.json").read_bytes())["result"], "rolled_back")

    def test_runtime_claim_consumption_never_becomes_runtime_completion(self):
        with LocalStageHarness(self.module, self.root, "runtime_stage") as run:
            with self.assertRaises(Exception):
                run.execute()
            failure = run.failure()
            self.assert_failure_is_safe(run, failure)
            self.assertEqual(failure["failure_locus"], "runtime_stage")
            self.assertEqual(failure["failure_class"], "process_exit")
            self.assertEqual(failure["completed_milestones"], MILESTONES[:9])
            self.assertEqual(failure["last_completed_milestone"], "runtime_entry")
            self.assertEqual(failure["application_claim_entry"], "consumed_entry_only")
            self.assertEqual(failure["runtime_claim_entry"], "consumed_entry_only")
            self.assertNotIn("runtime_complete", failure["completed_milestones"])
            self.assertEqual(failure["rollback_status"], "attempts_completed_unverified")
            self.assertEqual(failure["rollback_milestones"], ["rollback_started", "rollback_attempts_completed"])

    def test_post_runtime_failures_identify_the_exact_completed_boundary(self):
        for scenario, locus, last in [
            ("awg2_after", "awg2_after_snapshot", "runtime_complete"),
            ("awg2_equality", "awg2_equality", "awg2_after_captured"),
            ("coordinator_outcome", "coordinator_outcome_publication", "awg2_equality_confirmed"),
            ("transaction_outcome", "transaction_outcome_publication", "coordinator_outcome_written"),
            ("milestone_write", "milestone_publication", "runtime_complete"),
        ]:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                with LocalStageHarness(self.module, Path(temporary), scenario) as run:
                    with self.assertRaises(Exception):
                        run.execute()
                    failure = run.failure()
                    self.assert_failure_is_safe(run, failure)
                    self.assertEqual(failure["failure_locus"], locus)
                    self.assertEqual(failure["last_completed_milestone"], last)
                    self.assertEqual(failure["completed_milestones"], MILESTONES[:MILESTONES.index(last) + 1])
                    self.assertIn(["/usr/bin/systemctl", "stop", "amn2-spain-awg3.service"], run.commands)
                    self.assertFalse(run.paths["RUNTIME_STATE_ROOT"].exists())
                    self.assertFalse(run.paths["RUNTIME_UNIT_PATH"].exists())

    def test_rollback_failure_is_reported_and_does_not_skip_other_cleanup(self):
        with LocalStageHarness(self.module, self.root, "rollback_error") as run:
            with self.assertRaises(Exception):
                run.execute()
            failure = run.failure()
            self.assert_failure_is_safe(run, failure)
            self.assertEqual(failure["failure_locus"], "awg2_after_snapshot")
            self.assertEqual(failure["rollback_status"], "attempt_failed")
            self.assertEqual(failure["rollback_milestones"], ["rollback_started"])
            self.assertIn(["/usr/bin/systemctl", "daemon-reload"], run.commands)
            self.assertFalse(run.paths["RUNTIME_STATE_ROOT"].exists())

    def test_success_records_full_milestones_without_failure_or_rollback(self):
        with LocalStageHarness(self.module, self.root) as run:
            self.assertEqual(run.execute()["result"], "application_and_awg31_staged")
            progress = json.loads((run.transaction / "milestones.json").read_bytes())
            self.assertEqual(progress["schema"], "amn2.phase16.controlled-stage-milestones.v1")
            self.assertEqual(progress["completed_milestones"], MILESTONES)
            self.assertEqual(progress["last_completed_milestone"], "transaction_outcome_written")
            self.assertFalse((run.transaction / "failure-locus.json").exists())
            self.assertNotIn(["/usr/bin/systemctl", "stop", "amn2-spain-awg3.service"], run.commands)
            before = (run.transaction / "milestones.json").read_bytes()
            count = len(run.commands)
            with self.assertRaisesRegex(self.module.StageCoordinatorError, "stage target exists"):
                run.execute()
            self.assertEqual(len(run.commands), count)
            self.assertEqual((run.transaction / "milestones.json").read_bytes(), before)

    def test_milestone_builder_rejects_unallowlisted_or_out_of_order_values(self):
        with LocalStageHarness(self.module, self.root) as run:
            for milestones in (["raw-sensitive-detail"], ["runtime_complete"], MILESTONES[:2] + ["runtime_complete"]):
                with self.subTest(milestones=milestones), self.assertRaises(self.module.StageCoordinatorError):
                    self.module.build_milestone_document(run.header["request"], milestones)

    def test_main_failure_envelope_stays_fixed_and_has_no_raw_diagnostics(self):
        output = io.BytesIO()
        with LocalStageHarness(self.module, self.root, "runtime_stage") as run, patch.object(
            self.module, "_read_frame", return_value=(run.header, run.archive),
        ), patch.object(self.module.sys, "stdout") as stdout:
            stdout.buffer = output
            self.assertEqual(self.module.main(), 70)
        self.assertEqual(output.getvalue(), canonical({
            "general_issuance_enabled": False, "package_id": self.module.PACKAGE_ID,
            "result": "stage_failed_and_rollback_attempted",
            "schema": "amn2.phase16.controlled-stage-outcome.v1",
        }))


if __name__ == "__main__":
    unittest.main()
