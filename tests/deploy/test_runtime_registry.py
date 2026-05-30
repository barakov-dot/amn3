from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_runtime_manifest_describes_supported_modes_and_git_policy():
    manifest_path = ROOT / "deploy/runtime/manifest.yml"

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == 1
    assert manifest["project"] == "amn2"
    assert set(manifest["runtime_modes"]) == {"host_systemd", "docker"}
    assert "docker" in manifest["runtime_modes"]["docker"]["required_commands"]
    assert "awg" in manifest["runtime_modes"]["host_systemd"]["required_commands"]
    assert "data" in manifest["common"]["project_dirs"]
    assert "config_templates" in manifest["common"]["project_dirs"]
    assert ".env" in manifest["git_policy"]["never_store"]
    assert "servers.yml" in manifest["git_policy"]["never_store"]


def test_runtime_checker_is_read_only_and_knows_both_runtimes():
    checker_path = ROOT / "deploy/runtime/check_vps.sh"

    text = checker_path.read_text(encoding="utf-8")

    assert "AMN_RUNTIME" in text
    assert "host_systemd" in text
    assert "docker" in text
    assert "docker ps --format '{{.Names}}'" in text
    assert 'docker exec "$AMN_CONTAINER_NAME" awg show "$AMN_INTERFACE"' in text
    assert "systemctl is-active" in text
    for mutating in ("apt install", "systemctl restart", "docker rm", "rm -", "ufw allow"):
        assert mutating not in text


def test_runtime_examples_are_parseable_and_cover_host_and_docker():
    host_path = ROOT / "deploy/examples/servers.host_systemd.example.yml"
    docker_path = ROOT / "deploy/examples/servers.docker.example.yml"

    host = yaml.safe_load(host_path.read_text(encoding="utf-8"))
    docker = yaml.safe_load(docker_path.read_text(encoding="utf-8"))

    assert host["servers"][0]["runtime"] == {
        "type": "host_systemd",
        "service_name": "awg-quick@awg0",
    }
    assert docker["servers"][0]["runtime"] == {
        "type": "docker",
        "container_name": "amnezia-awg",
    }
    assert host["servers"][0]["vpn"]["port"] == 30001
    assert docker["servers"][0]["vpn"]["interface"] == "awg0"


def test_runtime_docs_point_to_manifest_checker_and_examples():
    doc_path = ROOT / "docs/RUNTIME_REGISTRY.ru.md"

    text = doc_path.read_text(encoding="utf-8")

    assert "deploy/runtime/manifest.yml" in text
    assert "deploy/runtime/check_vps.sh" in text
    assert "deploy/examples/servers.docker.example.yml" in text
    assert "Не храним в Git" in text
