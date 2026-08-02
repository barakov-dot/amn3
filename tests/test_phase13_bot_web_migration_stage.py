from __future__ import annotations

from configparser import ConfigParser
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
BOT_UNIT = ROOT / "packaging/phase12-spain/units/amn2-spain-bot.service"
STAGE = ROOT / "scripts/vps/phase13_bot_web_migration_stage_remote.sh"
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
PROTECTED_RELATIVE = Path("var/lib/amn2-phase13-bot-web-migration")
STAGED_NAMES = {
    "amn2-spain-bot.service",
    "merged-target.sqlite3.enc",
    "runtime.env.delta.enc",
}
AWG2_FOUNDATION_SHA256 = "0e5a5926821d88ae4a2515f9e95cd7c3f69db52100c1a1ec74e99fb794222281"
FOREIGN_RECEIPT_SHA256 = "bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704"
FOREIGN_STABLE_SHA256 = "f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8"
NOW_EPOCH = 1785675600


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_stage_fixture(root: Path) -> None:
    (root / ".amn2-phase13-local-fake-harness").write_bytes(b"task7-local-only\n")
    package = root / "package"
    package.mkdir(parents=True)

    indirect = {
        "migration-plan.json": canonical(
            {
                "live_mutation_authorized": False,
                "migration_id": "bot-web-migration-stage-001",
                "schema": "amn2.phase13.bot-web-migration-plan.v1",
            }
        ),
        "source-audit.json": canonical({"role": "usa-source"}),
        "ssh-runner.ps1": b"# reviewed fixture; no network action\n",
        "target-audit.json": canonical({"role": "spain-target"}),
    }
    rollback = canonical(
        {
            "artifact_bindings": {
                name: {"sha256": sha256(value), "size": len(value)}
                for name, value in sorted(indirect.items())
            },
            "live_mutation_authorized": False,
            "restore_apply_authorized": False,
            "schema": "amn2.phase13.bot-web-migration-rollback-plan.v1",
        }
    )
    direct = {
        "source-full-backup.enc": b"sealed-source-backup",
        "target-before-backup.enc": b"sealed-target-before-backup",
        "merged-target.sqlite3.enc": b"sealed-merged-target-database",
        "merge-preview.json": canonical(
            {
                "apply_allowed": True,
                "live_mutation_authorized": False,
                "usable_secret_records_imported": 0,
            }
        ),
        "rollback-plan.json": rollback,
    }
    for name, value in {**indirect, **direct}.items():
        (package / name).write_bytes(value)

    manifest = {
        "artifacts": {
            key: {
                "path": name,
                "sha256": sha256(direct[name]),
                "size": len(direct[name]),
            }
            for key, name in {
                "merge_preview": "merge-preview.json",
                "merged_target_db": "merged-target.sqlite3.enc",
                "rollback_plan": "rollback-plan.json",
                "source_full_backup": "source-full-backup.enc",
                "target_before_backup": "target-before-backup.enc",
            }.items()
        },
        "created_at": "2026-08-02T12:00:00Z",
        "expires_at": "2099-08-03T12:00:00Z",
        "live_mutation_authorized": False,
        "outcome_id": "bot-web-migration-stage-001",
        "schema": "amn2.phase13.bot-web-migration-manifest.v1",
        "source_audit_sha256": sha256(indirect["source-audit.json"]),
        "source_role": "usa-source",
        "target_audit_sha256": sha256(indirect["target-audit.json"]),
        "target_role": "spain-target",
    }
    (package / "manifest.json").write_bytes(canonical(manifest))

    stage_inputs = root / "stage-inputs"
    stage_inputs.mkdir()
    stage_values = {
        "amn2-spain-bot.service": BOT_UNIT.read_bytes(),
        "runtime.env.delta.enc": b"sealed-runtime-environment-delta",
    }
    for name, value in stage_values.items():
        (stage_inputs / name).write_bytes(value)
    bindings = {
        "artifacts": {
            "bot_unit": {
                "path": "amn2-spain-bot.service",
                "sha256": sha256(stage_values["amn2-spain-bot.service"]),
                "size": len(stage_values["amn2-spain-bot.service"]),
            },
            "runtime_env_delta": {
                "path": "runtime.env.delta.enc",
                "sha256": sha256(stage_values["runtime.env.delta.enc"]),
                "size": len(stage_values["runtime.env.delta.enc"]),
            },
        },
        "live_mutation_authorized": False,
        "schema": "amn2.phase13.bot-web-disabled-stage-inputs.v1",
    }
    (stage_inputs / "bindings.json").write_bytes(canonical(bindings))

    live_db = root / "var/lib/amn2-spain/amn2.sqlite3"
    live_db.parent.mkdir(parents=True)
    live_db.write_bytes(b"accepted-spain-target-database")
    observed = root / "observed"
    observed.mkdir()
    (observed / "state").write_text(
        "\n".join(
            (
                "BOT_ACTIVE=false",
                "BOT_PROCESS_COUNT=0",
                "BOT_ENABLE_MARKER_PRESENT=false",
                "SPAIN_WEB_ACTIVE=true",
                "SPAIN_WEB_LOOPBACK_ONLY=true",
                "SPAIN_WEB_HEALTHY=true",
                "USA_BOT_ACTIVE=true",
                f"USA_EVIDENCE_CHECKED_AT_EPOCH={NOW_EPOCH - 60}",
                f"TARGET_DB_SHA256_BEFORE={sha256(live_db.read_bytes())}",
                f"AWG2_FOUNDATION_SHA256={AWG2_FOUNDATION_SHA256}",
                f"FOREIGN_RECEIPT_SHA256={FOREIGN_RECEIPT_SHA256}",
                f"FOREIGN_STABLE_SHA256={FOREIGN_STABLE_SHA256}",
                "",
            )
        ),
        encoding="utf-8",
        newline="\n",
    )


def run_stage(root: Path, mode: str) -> subprocess.CompletedProcess[str]:
    assert BASH.is_file(), "Git Bash is required for the local fake harness"
    environment = os.environ.copy()
    environment.update(
        {
            "AMN2_PHASE13_LOCAL_FAKE_HARNESS": "1",
            "AMN2_PHASE13_FAKE_ROOT": root.resolve().as_posix(),
            "AMN2_PHASE13_TEST_NOW_EPOCH": str(NOW_EPOCH),
            "PATH": str(Path(sys.executable).parent)
            + os.pathsep
            + environment.get("PATH", ""),
        }
    )
    return subprocess.run(
        [str(BASH), STAGE.resolve().as_posix(), mode],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
        check=False,
    )


def replace_observation(root: Path, key: str, value: str) -> None:
    path = root / "observed/state"
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text(
        "\n".join(
            f"{key}={value}" if line.startswith(f"{key}=") else line
            for line in lines
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def test_bot_unit_is_persistable_only_while_marker_gate_is_present() -> None:
    unit = ConfigParser(interpolation=None)
    unit.optionxform = str
    unit.read_string(BOT_UNIT.read_text(encoding="utf-8"))

    assert unit["Unit"]["ConditionPathExists"] == "/etc/amn2-spain/bot-enabled"
    assert unit["Install"]["WantedBy"] == "multi-user.target"


def test_preflight_verifies_all_bindings_without_creating_stage(tmp_path: Path) -> None:
    write_stage_fixture(tmp_path)
    live_before = (tmp_path / "var/lib/amn2-spain/amn2.sqlite3").read_bytes()

    result = run_stage(tmp_path, "preflight")

    assert result.returncode == 0, result.stderr
    assert result.stdout == "stage=preflight result=passed\n"
    assert not (tmp_path / PROTECTED_RELATIVE).exists()
    assert (tmp_path / "var/lib/amn2-spain/amn2.sqlite3").read_bytes() == live_before


def test_stage_writes_only_three_disabled_artifacts_and_preserves_live_state(
    tmp_path: Path,
) -> None:
    write_stage_fixture(tmp_path)
    live_db = tmp_path / "var/lib/amn2-spain/amn2.sqlite3"
    live_before = live_db.read_bytes()

    result = run_stage(tmp_path, "stage")

    assert result.returncode == 0, result.stderr
    assert result.stdout == "stage=stage result=passed\n"
    staged = tmp_path / PROTECTED_RELATIVE / "staged"
    assert {path.name for path in staged.iterdir()} == STAGED_NAMES
    assert (staged / "merged-target.sqlite3.enc").read_bytes() == (
        tmp_path / "package/merged-target.sqlite3.enc"
    ).read_bytes()
    assert (staged / "runtime.env.delta.enc").read_bytes() == (
        tmp_path / "stage-inputs/runtime.env.delta.enc"
    ).read_bytes()
    assert (staged / "amn2-spain-bot.service").read_bytes() == BOT_UNIT.read_bytes()
    if os.name != "nt":
        assert all(
            stat.S_IMODE(path.stat().st_mode) == 0o600 for path in staged.iterdir()
        )
    assert live_db.read_bytes() == live_before
    assert not (tmp_path / "etc/amn2-spain/bot-enabled").exists()


@pytest.mark.parametrize(
    ("key", "value", "reason"),
    [
        ("BOT_ACTIVE", "true", "bot_not_disabled"),
        ("BOT_PROCESS_COUNT", "1", "bot_process_present"),
        ("BOT_ENABLE_MARKER_PRESENT", "true", "bot_marker_present"),
        ("SPAIN_WEB_ACTIVE", "false", "web_not_healthy"),
        ("SPAIN_WEB_LOOPBACK_ONLY", "false", "web_not_loopback_only"),
        ("SPAIN_WEB_HEALTHY", "false", "web_not_healthy"),
        ("USA_BOT_ACTIVE", "false", "usa_evidence_invalid"),
        (
            "USA_EVIDENCE_CHECKED_AT_EPOCH",
            str(NOW_EPOCH - 3601),
            "usa_evidence_stale",
        ),
        ("AWG2_FOUNDATION_SHA256", "0" * 64, "awg2_foundation_mismatch"),
        ("FOREIGN_RECEIPT_SHA256", "0" * 64, "foreign_foundation_mismatch"),
        ("FOREIGN_STABLE_SHA256", "0" * 64, "foreign_foundation_mismatch"),
    ],
)
def test_preflight_fails_closed_for_unsafe_observation(
    tmp_path: Path, key: str, value: str, reason: str
) -> None:
    write_stage_fixture(tmp_path)
    replace_observation(tmp_path, key, value)

    result = run_stage(tmp_path, "preflight")

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr == f"stage=preflight result=failed reason={reason}\n"
    assert not (tmp_path / PROTECTED_RELATIVE).exists()


def test_preflight_rejects_actual_marker_even_if_observation_claims_absent(
    tmp_path: Path,
) -> None:
    write_stage_fixture(tmp_path)
    marker = tmp_path / "etc/amn2-spain/bot-enabled"
    marker.parent.mkdir(parents=True)
    marker.write_bytes(b"")

    result = run_stage(tmp_path, "preflight")

    assert result.returncode != 0
    assert result.stderr == "stage=preflight result=failed reason=bot_marker_present\n"
    assert not (tmp_path / PROTECTED_RELATIVE).exists()


def test_preflight_rejects_package_checksum_mismatch(tmp_path: Path) -> None:
    write_stage_fixture(tmp_path)
    (tmp_path / "package/merged-target.sqlite3.enc").write_bytes(b"tampered")

    result = run_stage(tmp_path, "preflight")

    assert result.returncode != 0
    assert result.stderr == "stage=preflight result=failed reason=package_invalid\n"
    assert not (tmp_path / PROTECTED_RELATIVE).exists()


def test_preflight_requires_exact_local_fake_harness_sentinel(tmp_path: Path) -> None:
    write_stage_fixture(tmp_path)
    (tmp_path / ".amn2-phase13-local-fake-harness").unlink()

    result = run_stage(tmp_path, "preflight")

    assert result.returncode != 0
    assert result.stderr == (
        "stage=preflight result=failed reason=local_fake_root_invalid\n"
    )
    assert not (tmp_path / PROTECTED_RELATIVE).exists()


def test_stage_rejects_symlinked_protected_parent(tmp_path: Path) -> None:
    write_stage_fixture(tmp_path)
    original_var = tmp_path / "var"
    redirected_var = tmp_path / "redirected-var"
    original_var.rename(redirected_var)
    try:
        original_var.symlink_to(redirected_var, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlink creation unavailable")

    result = run_stage(tmp_path, "stage")

    assert result.returncode != 0
    assert result.stderr == "stage=stage result=failed reason=local_fake_root_invalid\n"
    assert not (redirected_var / "lib/amn2-phase13-bot-web-migration").exists()


def test_preflight_rejects_manifest_to_audit_cross_binding_mismatch(
    tmp_path: Path,
) -> None:
    write_stage_fixture(tmp_path)
    manifest_path = tmp_path / "package/manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["source_audit_sha256"] = "0" * 64
    manifest_path.write_bytes(canonical(manifest))

    result = run_stage(tmp_path, "preflight")

    assert result.returncode != 0
    assert result.stderr == "stage=preflight result=failed reason=package_invalid\n"
    assert not (tmp_path / PROTECTED_RELATIVE).exists()


def test_stage_is_create_new_and_does_not_overwrite_existing_root(
    tmp_path: Path,
) -> None:
    write_stage_fixture(tmp_path)
    protected = tmp_path / PROTECTED_RELATIVE
    protected.mkdir(parents=True)
    sentinel = protected / "sentinel"
    sentinel.write_bytes(b"preserve")

    result = run_stage(tmp_path, "stage")

    assert result.returncode != 0
    assert result.stderr == "stage=stage result=failed reason=stage_root_exists\n"
    assert sentinel.read_bytes() == b"preserve"


def test_verify_stage_detects_tampering_without_touching_live_database(
    tmp_path: Path,
) -> None:
    write_stage_fixture(tmp_path)
    live_db = tmp_path / "var/lib/amn2-spain/amn2.sqlite3"
    live_before = live_db.read_bytes()
    assert run_stage(tmp_path, "stage").returncode == 0
    (tmp_path / PROTECTED_RELATIVE / "staged/runtime.env.delta.enc").write_bytes(
        b"tampered"
    )

    result = run_stage(tmp_path, "verify-stage")

    assert result.returncode != 0
    assert result.stderr == "stage=verify-stage result=failed reason=stage_invalid\n"
    assert live_db.read_bytes() == live_before
    assert not (tmp_path / "etc/amn2-spain/bot-enabled").exists()


def test_rollback_stage_removes_only_known_stage_root(tmp_path: Path) -> None:
    write_stage_fixture(tmp_path)
    live_db = tmp_path / "var/lib/amn2-spain/amn2.sqlite3"
    live_before = live_db.read_bytes()
    assert run_stage(tmp_path, "stage").returncode == 0

    result = run_stage(tmp_path, "rollback-stage")

    assert result.returncode == 0, result.stderr
    assert result.stdout == "stage=rollback-stage result=passed\n"
    assert not (tmp_path / PROTECTED_RELATIVE).exists()
    assert live_db.read_bytes() == live_before
    assert not (tmp_path / "etc/amn2-spain/bot-enabled").exists()


def test_rollback_stage_refuses_unknown_content(tmp_path: Path) -> None:
    write_stage_fixture(tmp_path)
    assert run_stage(tmp_path, "stage").returncode == 0
    unknown = tmp_path / PROTECTED_RELATIVE / "staged/unknown"
    unknown.write_bytes(b"preserve")

    result = run_stage(tmp_path, "rollback-stage")

    assert result.returncode != 0
    assert result.stderr == "stage=rollback-stage result=failed reason=stage_invalid\n"
    assert unknown.read_bytes() == b"preserve"


def test_unknown_mode_is_rejected_before_any_write(tmp_path: Path) -> None:
    write_stage_fixture(tmp_path)

    result = run_stage(tmp_path, "apply")

    assert result.returncode != 0
    assert result.stderr == "stage=unknown result=failed reason=unsupported_mode\n"
    assert not (tmp_path / PROTECTED_RELATIVE).exists()
