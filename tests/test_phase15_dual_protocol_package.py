from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase15_dual_protocol_package.py"
FIXTURE = ROOT / "tests" / "fixtures" / "phase15_dual_protocol_package" / "source-tree"
PACKAGE_ID = "phase15-dual-protocol-bootstrap-20260811-001"
BRANCH = "codex/phase15-local-package-bootstrap-readiness"
PHASE14_SHA = "d33e69b53c7397c567b16c4f1caea12af97969d9436d3e95e6038148054aa982"


def load_package_module():
    if not SCRIPT.is_file():
        pytest.fail("Phase 15 package implementation is missing")
    spec = importlib.util.spec_from_file_location("phase15_package", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_git(root: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout


def make_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    shutil.copytree(FIXTURE, repo)
    shutil.copytree(
        ROOT / "packaging" / "phase15-dual-protocol-bootstrap-contract",
        repo / "packaging" / "phase15-dual-protocol-bootstrap-contract",
    )
    (repo / "scripts").mkdir(exist_ok=True)
    shutil.copy2(SCRIPT, repo / "scripts" / SCRIPT.name)
    phase14 = run_git(
        ROOT,
        "show",
        "4e1052c079e1e25031a6c80f4dae1763e457ca48:research/amn2/phase14-dual-protocol-application-readiness-receipt.md",
    )
    receipt = repo / "research" / "amn2" / "phase14-dual-protocol-application-readiness-receipt.md"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_bytes(phase14)

    run_git(repo, "init", "-b", BRANCH)
    run_git(repo, "config", "user.name", "Phase15 Fixture")
    run_git(repo, "config", "user.email", "phase15-fixture@example.invalid")
    run_git(repo, "add", ".")
    for relative in (
        "scripts/vps/phase15_application_stage_remote.sh",
        "scripts/vps/phase15_awg3_runtime_stage_remote.sh",
        "scripts/vps/phase15_spain_readonly_preflight_remote.sh",
    ):
        run_git(repo, "update-index", "--chmod=+x", relative)
    run_git(repo, "commit", "-m", "fixture")
    head = run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()
    return repo, head


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_materialization_is_deterministic_and_uses_canonical_receipt_blob(tmp_path: Path) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    first = tmp_path / "one"
    second = tmp_path / "two"

    receipt_one = package.materialize_package(
        source_root=repo,
        source_head=head,
        package_id=PACKAGE_ID,
        output_root=first,
        tooling_root=repo,
    )
    receipt_two = package.materialize_package(
        source_root=repo,
        source_head=head,
        package_id=PACKAGE_ID,
        output_root=second,
        tooling_root=repo,
    )

    assert receipt_one.package_identity_sha256 == receipt_two.package_identity_sha256
    assert tree_hashes(first) == tree_hashes(second)
    manifest_raw = (first / "manifest.json").read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    assert manifest_raw == package.canonical_json_bytes(manifest)
    assert manifest["source"] == {"branch": BRANCH, "head": head}
    assert manifest["receipts"]["phase14"]["sha256"] == PHASE14_SHA
    phase14_entry = next(
        item for item in manifest["entries"] if item["role"] == "phase14_receipt"
    )
    assert phase14_entry["sha256"] == PHASE14_SHA
    assert package.verify_package(first).package_identity_sha256 == receipt_one.package_identity_sha256


def test_materializer_refuses_dirty_or_mismatched_source(tmp_path: Path) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    (repo / "app" / "main.py").write_text("DIRTY = True\n", encoding="utf-8")
    with pytest.raises(package.PackageContractError, match="clean"):
        package.materialize_package(
            source_root=repo,
            source_head=head,
            package_id=PACKAGE_ID,
            output_root=tmp_path / "dirty",
            tooling_root=repo,
        )
    assert not (tmp_path / "dirty").exists()

    run_git(repo, "restore", "app/main.py")
    with pytest.raises(package.PackageContractError, match="source head"):
        package.materialize_package(
            source_root=repo,
            source_head="0" * 40,
            package_id=PACKAGE_ID,
            output_root=tmp_path / "wrong-head",
            tooling_root=repo,
        )


def test_materializer_refuses_nonempty_output_wrong_id_and_unclassified_file(tmp_path: Path) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    output = tmp_path / "occupied"
    output.mkdir()
    (output / "keep.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(package.PackageContractError, match="non-empty"):
        package.materialize_package(
            source_root=repo,
            source_head=head,
            package_id=PACKAGE_ID,
            output_root=output,
            tooling_root=repo,
        )
    with pytest.raises(package.PackageContractError, match="package id"):
        package.materialize_package(
            source_root=repo,
            source_head=head,
            package_id="phase13-stale",
            output_root=tmp_path / "wrong-id",
            tooling_root=repo,
        )

    unknown = repo / "app" / "payload.exe"
    unknown.write_bytes(b"MZ synthetic fixture")
    run_git(repo, "add", "app/payload.exe")
    run_git(repo, "commit", "-m", "add unclassified")
    new_head = run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()
    with pytest.raises(package.PackageContractError, match="unclassified"):
        package.materialize_package(
            source_root=repo,
            source_head=new_head,
            package_id=PACKAGE_ID,
            output_root=tmp_path / "unknown",
            tooling_root=repo,
        )


def test_verifier_detects_file_and_manifest_mutation(tmp_path: Path) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    output = tmp_path / "package"
    package.materialize_package(
        source_root=repo,
        source_head=head,
        package_id=PACKAGE_ID,
        output_root=output,
        tooling_root=repo,
    )
    target = output / "source" / "app" / "main.py"
    original = target.read_bytes()
    target.write_bytes(original + b"# mutation\n")
    with pytest.raises(package.PackageContractError, match="checksum"):
        package.verify_package(output)
    target.write_bytes(original)
    assert package.verify_package(output).package_identity_sha256

    manifest_path = output / "manifest.json"
    manifest_path.write_bytes(b"\xef\xbb\xbf" + manifest_path.read_bytes())
    with pytest.raises(package.PackageContractError):
        package.verify_package(output)


def test_cli_materialize_and_verify(tmp_path: Path) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    output = tmp_path / "cli-package"
    env = dict(os.environ)
    env["PHASE15_TOOLING_ROOT"] = str(repo)
    created = subprocess.run(
        [
            os.sys.executable,
            str(SCRIPT),
            "materialize",
            "--source-root",
            str(repo),
            "--source-head",
            head,
            "--package-id",
            PACKAGE_ID,
            "--output-root",
            str(output),
        ],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert created.returncode == 0, created.stderr.decode("utf-8", "replace")
    verified = subprocess.run(
        [os.sys.executable, str(SCRIPT), "verify", "--package-root", str(output)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert verified.returncode == 0, verified.stderr.decode("utf-8", "replace")
    assert json.loads(verified.stdout)["result"] == "verified"
