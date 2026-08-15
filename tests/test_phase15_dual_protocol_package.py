from __future__ import annotations

import base64

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
    run_git(tmp_path, "clone", "--no-hardlinks", str(ROOT), str(repo))
    shutil.copytree(FIXTURE, repo, dirs_exist_ok=True)
    shutil.copytree(
        ROOT / "packaging" / "phase15-dual-protocol-bootstrap-contract",
        repo / "packaging" / "phase15-dual-protocol-bootstrap-contract",
        dirs_exist_ok=True,
    )
    (repo / "scripts").mkdir(exist_ok=True)
    shutil.copy2(SCRIPT, repo / "scripts" / SCRIPT.name)
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


def resign_manifest(package, root: Path, mutate) -> dict[str, object]:
    path = root / "manifest.json"
    value = json.loads(path.read_text("utf-8"))
    mutate(value)
    unsigned = dict(value)
    unsigned.pop("package_identity_sha256")
    value["package_identity_sha256"] = hashlib.sha256(
        package.canonical_json_bytes(unsigned)
    ).hexdigest()
    path.write_bytes(package.canonical_json_bytes(value))
    return value


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
    assert manifest["tooling"] == {"branch": BRANCH, "head": head}
    assert manifest["receipts"]["phase14"]["sha256"] == PHASE14_SHA
    phase14_entry = next(
        item for item in manifest["entries"] if item["role"] == "phase14_receipt"
    )
    assert phase14_entry["sha256"] == PHASE14_SHA
    assert package.verify_package(first).package_identity_sha256 == receipt_one.package_identity_sha256


def test_materializer_reads_phase14_receipt_from_fixed_commit_not_tooling_head(tmp_path: Path) -> None:
    package = load_package_module()
    repo, _head = make_repo(tmp_path)
    receipt_path = repo / "research" / "amn2" / "phase14-dual-protocol-application-readiness-receipt.md"
    receipt_path.write_text("tampered at tooling head\n", encoding="utf-8")
    run_git(repo, "add", "research/amn2/phase14-dual-protocol-application-readiness-receipt.md")
    run_git(repo, "commit", "-m", "tamper current receipt")
    head = run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()

    output = tmp_path / "fixed-receipt"
    package.materialize_package(
        source_root=repo,
        source_head=head,
        package_id=PACKAGE_ID,
        output_root=output,
        tooling_root=repo,
    )
    manifest = json.loads((output / "manifest.json").read_text("utf-8"))
    assert manifest["tooling"]["head"] == head
    packaged = output / "tooling" / "research" / "amn2" / "phase14-dual-protocol-application-readiness-receipt.md"
    assert hashlib.sha256(packaged.read_bytes()).hexdigest() == PHASE14_SHA


def test_materializer_sanitizes_git_repository_selection_environment(tmp_path: Path, monkeypatch) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "poison.git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(tmp_path / "poison-worktree"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "poison.index"))
    monkeypatch.setenv("GIT_OBJECT_DIRECTORY", str(tmp_path / "poison-objects"))
    monkeypatch.setenv("GIT_ALTERNATE_OBJECT_DIRECTORIES", str(tmp_path / "poison-alternates"))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.bare")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "true")

    receipt = package.materialize_package(
        source_root=repo,
        source_head=head,
        package_id=PACKAGE_ID,
        output_root=tmp_path / "sanitized",
        tooling_root=repo,
    )
    assert receipt.file_count > 0


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


def test_verifier_rejects_resigned_required_entry_omission(tmp_path: Path) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    output = tmp_path / "omission"
    package.materialize_package(source_root=repo, source_head=head, package_id=PACKAGE_ID, output_root=output, tooling_root=repo)
    omitted = "tooling/packaging/phase15-dual-protocol-bootstrap-contract/resource-plan.json"
    output.joinpath(*omitted.split("/")).unlink()
    resign_manifest(package, output, lambda value: value["entries"].__setitem__(
        slice(None), [entry for entry in value["entries"] if entry["path"] != omitted]
    ))

    with pytest.raises(package.PackageContractError, match="required package entry"):
        package.verify_package(output)


def test_verifier_rejects_resigned_required_entry_rebinding(tmp_path: Path) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    output = tmp_path / "rebinding"
    package.materialize_package(source_root=repo, source_head=head, package_id=PACKAGE_ID, output_root=output, tooling_root=repo)

    def rebind(value: dict[str, object]) -> None:
        entry = next(item for item in value["entries"] if item["path"] == "tooling/scripts/phase15_dual_protocol_package.py")
        entry["role"] = "operator_documentation"

    resign_manifest(package, output, rebind)
    with pytest.raises(package.PackageContractError, match="entry contract"):
        package.verify_package(output)


def test_materializer_rejects_output_symlink_before_publication(tmp_path: Path) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    target = tmp_path / "empty-target"
    target.mkdir()
    link = tmp_path / "output-link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"directory symlink unavailable: {error}")

    with pytest.raises(package.PackageContractError, match="symlink"):
        package.materialize_package(source_root=repo, source_head=head, package_id=PACKAGE_ID, output_root=link, tooling_root=repo)
    assert link.is_symlink()
    assert not any(target.iterdir())


def test_verifier_rejects_package_root_symlink(tmp_path: Path) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    target = tmp_path / "real-package"
    package.materialize_package(source_root=repo, source_head=head, package_id=PACKAGE_ID, output_root=target, tooling_root=repo)
    link = tmp_path / "package-link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"directory symlink unavailable: {error}")

    with pytest.raises(package.PackageContractError, match="symlink"):
        package.verify_package(link)


def test_materializer_rejects_symlinked_output_ancestor(tmp_path: Path) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    linked_parent = tmp_path / "linked-parent"
    try:
        linked_parent.symlink_to(real_parent, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"directory symlink unavailable: {error}")

    with pytest.raises(package.PackageContractError, match="symlink|reparse"):
        package.materialize_package(
            source_root=repo,
            source_head=head,
            package_id=PACKAGE_ID,
            output_root=linked_parent / "package",
            tooling_root=repo,
        )
    assert not (real_parent / "package").exists()


def test_verifier_rejects_symlinked_package_ancestor(tmp_path: Path) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    package_root = real_parent / "package"
    package.materialize_package(
        source_root=repo,
        source_head=head,
        package_id=PACKAGE_ID,
        output_root=package_root,
        tooling_root=repo,
    )
    linked_parent = tmp_path / "linked-parent"
    try:
        linked_parent.symlink_to(real_parent, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"directory symlink unavailable: {error}")

    with pytest.raises(package.PackageContractError, match="symlink|reparse"):
        package.verify_package(linked_parent / "package")


@pytest.mark.parametrize(
    ("relative", "body"),
    [
        ("app/.env", b"TOKEN=synthetic-but-forbidden\n"),
        ("app/cache/state.py", b"CACHE = True\n"),
        ("app/.cache/state.py", b"CACHE = True\n"),
        ("app/__pycache__/state.pyc", b"synthetic bytecode"),
        ("app/client-qr.png", b"\x89PNG\r\n\x1a\nsynthetic-qr"),
        ("app/web/static/brand-full.png", b"\x89PNG\r\n\x1a\nsubstituted-qr"),
        ("app/leaked_key.py", b"KEY = '''-----BEGIN PRIVATE KEY-----'''\n"),
        ("app/raw_peer.py", b"PrivateKey = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=\n"),
        ("app/jwt.py", b"ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJzdWJqZWN0In0.signature0123456789'\n"),
        ("app/bearer.py", b"AUTHORIZATION = 'Bearer live_ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'\n"),
        ("app/api_key.py", b"API_TOKEN = 'live_ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'\n"),
        ("app/base64_key.py", b"PRIVATE_KEY = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='\n"),
        ("app/short_bearer.py", b"MESSAGE = 'Bearer x'\n"),
        (
            "app/structural_jwt.py",
            b"MESSAGE = 'IHsiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiJzdWJqZWN0In0.c2lnbmF0dXJl'\n",
        ),
        ("app/aws_key.py", b"AWS_ACCESS_KEY_ID = 'public-test!punctuation?1234'\n"),
        ("app/bot_token.py", b"BOT_TOKEN = 'public-test!punctuation?1234'\n"),
        ("app/dotted_token.py", b"self.api_token = 'public-test!punctuation?1234'\n"),
        ("app/dict_token.py", b"payload = {\"api_token\": \"public-test!punctuation?1234\"}\n"),
        ("app/typed_token.py", b"api_token: str = 'public-test!punctuation?1234'\n"),
        (
            "app/concatenated_token.py",
            b"API_TOKEN = (\n    'public-test!'\n    'punctuation?1234'\n)\n",
        ),
        (
            "app/sensitive_attribute.html",
            b'<input name="api_token" value="public-test!punctuation?1234">\n',
        ),
        ("app/sensitive_value.tpl", b"api_token=public-test!punctuation?1234\n"),
        ("app/unknown_sensitive_jinja.tpl", b"api_token={{ x }}\n"),
        ("app/prefixed_allowed_jinja.tpl", b"api_token=pre{{ issued_raw_token }}\n"),
        ("app/suffixed_allowed_jinja.tpl", b"api_token={{ issued_raw_token }}post\n"),
        (
            "app/sensitive_jinja_attribute.html",
            b'<input name="api_token" value="{{ x }}">\n',
        ),
        (
            "app/invalid_python_secret.py",
            b"API_TOKEN = 'public-test!punctuation?1234'\nif (\n",
        ),
        (
            "app/invalid_utf8_secret.py",
            b"API_TOKEN = 'public-test!punctuation?1234'\n# \xff\n",
        ),
        (
            "app/invalid_utf8_secret.html",
            b'<input name="api_token" value="public-test!punctuation?1234">\xff\n',
        ),
        (
            "app/invalid_utf8_secret.tpl",
            b"api_token=public-test!punctuation?1234\xff\n",
        ),
        (
            "app/invalid_utf8_secret.css",
            b":root { --api-token: public-test!punctuation?1234; }\xff\n",
        ),
        (
            "app/multiline_sensitive_assignment.tpl",
            b"api_token=\n    public-test!punctuation?1234\n",
        ),
        (
            "app/sensitive_jinja_set.tpl",
            b"{% set api_token = 'public-test!punctuation?1234' %}\n",
        ),
        (
            "app/sensitive_jinja_block_set.tpl",
            b"{% set api_token %}public-test!punctuation?1234{% endset %}\n",
        ),
        (
            "app/sensitive_inline_script.html",
            b"<script>const api_token = 'public-test!punctuation?1234';</script>\n",
        ),
        (
            "app/sensitive_semicolonless_declaration.html",
            b"<script>const api_token = 'public-test!punctuation?1234'</script>\n",
        ),
        (
            "app/sensitive_script_property.html",
            b"<script>window.session.apiToken = 'public-test!punctuation?1234';</script>\n",
        ),
        (
            "app/sensitive_semicolonless_property.html",
            b"<script>window.session.apiToken = 'public-test!punctuation?1234'</script>\n",
        ),
        (
            "app/sensitive_custom_property.css",
            b":root { --api-token: public-test!punctuation?1234; }\n",
        ),
        (
            "app/sensitive_final_custom_property.css",
            b":root { --api-token: public-test!punctuation?1234 }\n",
        ),
        (
            "app/composite_api_token.py",
            b"API_TOKEN_VALUE = 'public-test!punctuation?1234'\n",
        ),
        (
            "app/composite_jwt_secret.py",
            b"JWT_SECRET_VALUE = 'public-test!punctuation?1234'\n",
        ),
        (
            "app/composite_authorization.py",
            b"AUTHORIZATION_HEADER = 'public-test!punctuation?1234'\n",
        ),
        ("app/state.py", b"SQLite format 3\x00synthetic"),
        ("app/token.py", b"TOKEN = '123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi'\n"),
        ("app/peers/device.json", b"{}\n"),
    ],
)
def test_materializer_rejects_forbidden_secret_qr_peer_config_or_cache_material(
    tmp_path: Path, relative: str, body: bytes
) -> None:
    package = load_package_module()
    repo, _head = make_repo(tmp_path)
    target = repo.joinpath(*relative.split("/"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body)
    if relative == "app/__pycache__/state.pyc":
        run_git(repo, "add", "-f", "--", relative)
    else:
        run_git(repo, "add", relative)
    run_git(repo, "commit", "-m", "add forbidden material")
    head = run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()

    with pytest.raises(package.PackageContractError, match="forbidden"):
        package.materialize_package(source_root=repo, source_head=head, package_id=PACKAGE_ID, output_root=tmp_path / "forbidden", tooling_root=repo)


def test_materializer_rejects_excessively_nested_structural_jwt(tmp_path: Path) -> None:
    package = load_package_module()
    repo, _head = make_repo(tmp_path)
    nested_header_json = (
        b'{"alg":' + (b"[" * 3000) + b"0" + (b"]" * 3000) + b"}"
    )
    header = base64.urlsafe_b64encode(nested_header_json).rstrip(b"=")
    assert len(header) <= 8192
    payload = base64.urlsafe_b64encode(b'{"sub":"subject"}').rstrip(b"=")
    target = repo / "app" / "excessively_nested_jwt.py"
    target.write_bytes(b"MESSAGE = '" + header + b"." + payload + b".x'\n")
    run_git(repo, "add", "app/excessively_nested_jwt.py")
    run_git(repo, "commit", "-m", "add excessively nested jwt")
    head = run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()

    with pytest.raises(package.PackageContractError, match="forbidden") as error:
        package.materialize_package(
            source_root=repo,
            source_head=head,
            package_id=PACKAGE_ID,
            output_root=tmp_path / "deep-jwt",
            tooling_root=repo,
        )
    assert isinstance(error.value.__cause__, RecursionError)


def test_materializer_rejects_oversized_jwt_shaped_candidate(tmp_path: Path) -> None:
    package = load_package_module()
    repo, _head = make_repo(tmp_path)
    header = b"A" * 8193
    payload = base64.urlsafe_b64encode(b'{"sub":"subject"}').rstrip(b"=")
    target = repo / "app" / "oversized_jwt.py"
    target.write_bytes(b"MESSAGE = '" + header + b"." + payload + b".x'\n")
    run_git(repo, "add", "app/oversized_jwt.py")
    run_git(repo, "commit", "-m", "add oversized jwt candidate")
    head = run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()

    with pytest.raises(package.PackageContractError, match="forbidden"):
        package.materialize_package(
            source_root=repo,
            source_head=head,
            package_id=PACKAGE_ID,
            output_root=tmp_path / "oversized-jwt",
            tooling_root=repo,
        )


def test_materializer_rejects_excessively_deep_static_sensitive_expression(
    tmp_path: Path,
) -> None:
    package = load_package_module()
    repo, _head = make_repo(tmp_path)
    target = repo / "app" / "excessively_deep_token.py"
    target.write_bytes(
        b"API_TOKEN = " + b" + ".join([b"'x'"] * 1500) + b"\n"
    )
    run_git(repo, "add", "app/excessively_deep_token.py")
    run_git(repo, "commit", "-m", "add excessively deep token expression")
    head = run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()

    with pytest.raises(package.PackageContractError):
        package.materialize_package(
            source_root=repo,
            source_head=head,
            package_id=PACKAGE_ID,
            output_root=tmp_path / "deep-static-expression",
            tooling_root=repo,
        )


def test_materializer_allows_only_necessary_non_concrete_jinja_secret_placeholders(tmp_path: Path) -> None:
    package = load_package_module()
    repo, _head = make_repo(tmp_path)
    template = repo / "app" / "approved-secret-placeholders.tpl"
    template.write_text(
        "api_token={{ issued_raw_token }}\n"
        "csrf_token={{ csrf_token }}\n"
        "private_key={{ revealed_secrets.private_key }}\n"
        "preshared_key={{ revealed_secrets.preshared_key }}\n"
        "{% set api_token %}{{ issued_raw_token }}{% endset %}\n",
        encoding="utf-8",
    )
    run_git(repo, "add", "app/approved-secret-placeholders.tpl")
    run_git(repo, "commit", "-m", "add approved placeholders")
    head = run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()

    receipt = package.materialize_package(
        source_root=repo,
        source_head=head,
        package_id=PACKAGE_ID,
        output_root=tmp_path / "placeholders",
        tooling_root=repo,
    )
    assert receipt.file_count > 0


def test_materializer_rejects_semicolonless_sensitive_javascript_assignment_before_next_statement(
    tmp_path: Path,
) -> None:
    package = load_package_module()
    repo, _head = make_repo(tmp_path)
    target = repo / "app" / "sensitive_asi_assignment.html"
    target.write_bytes(
        b"<script>\n"
        b"const api_token = 'public-test!punctuation?1234'\n"
        b"window.bootstrapApplication()\n"
        b"</script>\n"
    )
    run_git(repo, "add", "app/sensitive_asi_assignment.html")
    run_git(repo, "commit", "-m", "add sensitive asi assignment")
    head = run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()

    with pytest.raises(package.PackageContractError, match="forbidden"):
        package.materialize_package(
            source_root=repo,
            source_head=head,
            package_id=PACKAGE_ID,
            output_root=tmp_path / "sensitive-asi-assignment",
            tooling_root=repo,
        )


@pytest.mark.parametrize(
    "expression",
    [
        b"if (api_token == 'public-test!punctuation?1234') { window.render() }",
        b"if (api_token === 'public-test!punctuation?1234') { window.render() }",
        b"consume(api_token => 'public-test!punctuation?1234')",
    ],
)
def test_materializer_allows_javascript_equality_and_arrow_operators_on_sensitive_looking_identifiers(
    tmp_path: Path, expression: bytes
) -> None:
    package = load_package_module()
    repo, _head = make_repo(tmp_path)
    target = repo / "app" / "ordinary_operator_expression.html"
    target.write_bytes(b"<script>\n" + expression + b"\n</script>\n")
    run_git(repo, "add", "app/ordinary_operator_expression.html")
    run_git(repo, "commit", "-m", "add ordinary operator expression")
    head = run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()

    receipt = package.materialize_package(
        source_root=repo,
        source_head=head,
        package_id=PACKAGE_ID,
        output_root=tmp_path / "ordinary-operator-expression",
        tooling_root=repo,
    )
    assert receipt.file_count > 0


def test_materializer_allows_ordinary_non_secret_code_and_jinja(tmp_path: Path) -> None:
    package = load_package_module()
    repo, _head = make_repo(tmp_path)
    ordinary_files = {
        "app/ordinary_code.py": (
            b"PUBLIC_ASSET_DIGEST = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$'\n"
            b"BOT_TOKEN = os.environ['BOT_TOKEN']\n"
            b"api_token: str | None = None\n"
            b"self.api_token = token_provider()\n"
            b"payload = {'api_token': token_provider()}\n"
        ),
        "app/ordinary_template.html": (
            b'<span data-display-name="{{ user.display_name }}">public-label!123456789</span>\n'
        ),
        "app/ordinary_template.tpl": b"display_label={{ user.display_name }}\n",
        "app/ordinary_block_set.tpl": (
            b"{% set display_label %}{{ user.display_name }}{% endset %}\n"
        ),
        "app/ordinary_inline_script.html": (
            b'<script>const display_label = "{{ user.display_name }}"</script>\n'
        ),
        "app/ordinary_script_properties.html": (
            b'<script>window.view.displayLabel = "{{ user.display_name }}";\n'
            b'window.view.secondaryLabel = "{{ user.secondary_name }}"</script>\n'
        ),
        "app/ordinary_style.css": (
            b":root { --display-label: {{ theme.display_label }} }\n"
        ),
    }
    for relative, body in ordinary_files.items():
        target = repo.joinpath(*relative.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        run_git(repo, "add", relative)
    run_git(repo, "commit", "-m", "add ordinary non-secret source")
    head = run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()

    receipt = package.materialize_package(
        source_root=repo,
        source_head=head,
        package_id=PACKAGE_ID,
        output_root=tmp_path / "ordinary",
        tooling_root=repo,
    )
    assert receipt.file_count > 0


def test_cli_materialize_and_verify(tmp_path: Path) -> None:
    package = load_package_module()
    repo, head = make_repo(tmp_path)
    output = tmp_path / "cli-package"
    second_output = tmp_path / "cli-package-poisoned-env"
    cli_script = repo / "scripts" / SCRIPT.name
    env = dict(os.environ)
    env.pop("PHASE15_TOOLING_ROOT", None)

    def run_materialize(destination: Path, command_env: dict[str, str]):
        return subprocess.run(
        [
            os.sys.executable,
            str(cli_script),
            "materialize",
            "--source-root",
            str(repo),
            "--source-head",
            head,
            "--package-id",
            PACKAGE_ID,
            "--output-root",
            str(destination),
        ],
        cwd=repo,
        env=command_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        )

    created = run_materialize(output, env)
    assert created.returncode == 0, created.stderr.decode("utf-8", "replace")
    poisoned = dict(env)
    poisoned["PHASE15_TOOLING_ROOT"] = str(tmp_path / "ambient-poison")
    created_poisoned = run_materialize(second_output, poisoned)
    assert created_poisoned.returncode == 0, created_poisoned.stderr.decode("utf-8", "replace")
    assert tree_hashes(output) == tree_hashes(second_output)
    verified = subprocess.run(
        [os.sys.executable, str(cli_script), "verify", "--package-root", str(output)],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert verified.returncode == 0, verified.stderr.decode("utf-8", "replace")
    assert json.loads(verified.stdout)["result"] == "verified"
