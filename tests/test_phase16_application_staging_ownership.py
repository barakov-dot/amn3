"""Run the real application shell stage against temporary, non-secret fixtures.

Only fixed target paths, Python, and Windows-inapplicable POSIX modes are adapted. No SSH, Docker,
systemd, real database, protected profile, or immutable package is accessed.
"""
from __future__ import annotations

from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/vps/phase16_application_stage_remote.sh"
SUPPORT = ROOT / "scripts/vps/phase16_stage_support.py"
PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-016"
BASH = Path(r"C:\Program Files\Git\bin\bash.exe") if os.name == "nt" else Path("/bin/bash")


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


class ApplicationStagingOwnershipTest(unittest.TestCase):
    def setUp(self):
        if not BASH.is_file():
            self.fail("An existing Bash is required; do not install one automatically")
        temporary = tempfile.TemporaryDirectory(prefix="phase16-staging-ownership-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.package = self.base / "fixture"
        self.release = self.base / "releases" / PACKAGE_ID
        self.staging = Path(str(self.release) + ".staging")
        self.database = self.base / "fixture.sqlite3"
        self.backup = self.base / "backups" / (("c" * 64) + ".sqlite3")
        self.ledger = self.base / "stage" / "application.json"
        self.claim = self.base / "claim.json"
        self.script = self.base / "application-stage.sh"
        (self.package / "source/app").mkdir(parents=True)
        (self.package / "source/app/main.py").write_text("value = 42\n", encoding="utf-8")
        (self.package / "manifest.json").write_text("{}\n", encoding="ascii")
        helper = self.package / "tooling/scripts/vps/phase16_stage_support.py"
        helper.parent.mkdir(parents=True)
        shutil.copyfile(SUPPORT, helper)
        with closing(sqlite3.connect(self.database)) as database:
            with database:
                database.execute("CREATE TABLE fixture (value TEXT)")
                database.execute("INSERT INTO fixture VALUES ('preserve')")

        source = SOURCE.read_text(encoding="utf-8")
        replacements = {
            "/var/lib/amn2-phase16/stage/application.json": self.ledger.as_posix(),
            "/var/lib/amn2-phase16/rollback/application": (self.base / "backups").as_posix(),
            "/var/lib/amn2-phase16/package": self.package.as_posix(),
            "/var/lib/amn2-spain/amn2.sqlite3": self.database.as_posix(),
            "/opt/amn2-spain/releases": (self.base / "releases").as_posix(),
            "/usr/bin/python3": shlex.quote(Path(sys.executable).as_posix()),
        }
        for old, new in replacements.items():
            source = source.replace(old, new)
        if os.name == "nt":
            # Git Bash chmod is not supported by this managed Windows temp ACL.
            # Keep directory creation semantics real; POSIX modes are not tested.
            source = source.replace("/usr/bin/install -d -m 0700", "/usr/bin/mkdir -p")
            source = source.replace("/usr/bin/install -d -m 0750", "/usr/bin/mkdir -p")
            source = source.replace("/usr/bin/mkdir -m 0750", "/usr/bin/mkdir")
        self.script.write_text(source, encoding="utf-8", newline="\n")
        self.claim.write_bytes(canonical({
            "claim_id": "offline-staging-ownership",
            "consumed_at": None,
            "expected_current_state_sha256": "c" * 64,
            "expires_at": "2099-01-01T00:00:00Z",
            "future_gate": "APPLICATION_STAGE",
            "issued_at": "2025-01-01T00:00:00Z",
            "manifest_sha256": "d" * 64,
            "package_id": PACKAGE_ID,
            "package_identity_sha256": "e" * 64,
            "rollback_scope_sha256": "f" * 64,
            "schema": "amn2.phase16.stage-claim.v1",
            "stage_script_sha256": hashlib.sha256(self.script.read_bytes()).hexdigest(),
            "status": "issued",
        }))

    def execute(self):
        # Do not inherit any live Phase16 target settings or shell startup hooks.
        env = {key: value for key, value in os.environ.items()
               if not key.upper().startswith("PHASE16_")
               and key.upper() not in {"BASH_ENV", "ENV", "SHELLOPTS", "BASHOPTS"}
               and not key.startswith("BASH_FUNC_")}
        env.update({
            "LANG": "C",
            "LC_ALL": "C",
            "PHASE16_STAGE_CLAIM_FILE": self.claim.as_posix(),
            "PHASE16_EXPECTED_CURRENT_STATE_SHA256": "c" * 64,
            "PHASE16_FUTURE_GATE": "APPLICATION_STAGE",
            "PHASE16_MANIFEST_SHA256": "d" * 64,
            "PHASE16_PACKAGE_ID": PACKAGE_ID,
            "PHASE16_PACKAGE_IDENTITY_SHA256": "e" * 64,
            "PHASE16_ROLLBACK_SCOPE_SHA256": "f" * 64,
            "PHASE16_PACKAGE_ROOT": self.package.as_posix(),
            "PHASE16_APPLICATION_RELEASE_ROOT": self.release.as_posix(),
            "PHASE16_DATABASE_PATH": self.database.as_posix(),
            "PHASE16_STAGE_LEDGER": self.ledger.as_posix(),
        })
        return subprocess.run(
            [str(BASH), "--noprofile", "--norc", self.script.as_posix()],
            cwd=self.base, env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=15,
        )

    def assert_stage_failed(self, result):
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("application_stage_rolled_back", result.stderr)
        self.assertFalse(self.ledger.exists())

    def test_preexisting_staging_survives_rejected_snapshot(self):
        self.staging.mkdir(parents=True)
        marker = self.staging / "previous-attempt.txt"
        marker.write_bytes(b"keep previous staging\n")
        result = self.execute()
        self.assert_stage_failed(result)
        self.assertTrue(self.backup.is_file(), result.stderr)
        self.assertTrue(marker.is_file(), "rollback deleted preexisting staging")
        self.assertEqual(marker.read_bytes(), b"keep previous staging\n")
        self.assertFalse(self.release.exists())

    def test_preexisting_staging_survives_failure_before_snapshot(self):
        self.staging.mkdir(parents=True)
        marker = self.staging / "previous-attempt.txt"
        marker.write_bytes(b"keep early-failure staging\n")
        self.database.unlink()
        result = self.execute()
        self.assert_stage_failed(result)
        self.assertTrue(marker.is_file(), "early failure deleted unowned staging")
        self.assertEqual(marker.read_bytes(), b"keep early-failure staging\n")

    def test_owned_staging_is_removed_after_compile_failure_and_backup_survives(self):
        (self.package / "source/app/main.py").write_text("def broken(:\n", encoding="ascii")
        result = self.execute()
        self.assert_stage_failed(result)
        self.assertIn("SyntaxError", result.stdout)
        self.assertFalse(self.staging.exists())
        self.assertFalse(self.release.exists())
        self.assertTrue(self.backup.is_file(), result.stderr)
        with closing(sqlite3.connect(self.backup)) as backup:
            self.assertEqual(backup.execute("SELECT value FROM fixture").fetchall(), [("preserve",)])

    def test_success_publishes_release_and_removes_staging_name(self):
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout)["result"], "application_staged")
        self.assertEqual((self.release / "app/main.py").read_text(), "value = 42\n")
        self.assertFalse(self.staging.exists())
        self.assertEqual(json.loads(self.ledger.read_bytes())["status"], "staged")

    def test_preexisting_release_is_preserved(self):
        self.release.mkdir(parents=True)
        marker = self.release / "previous-release.txt"
        marker.write_bytes(b"keep previous release\n")
        result = self.execute()
        self.assert_stage_failed(result)
        self.assertEqual(marker.read_bytes(), b"keep previous release\n")
        self.assertFalse(self.staging.exists())


if __name__ == "__main__":
    unittest.main()
