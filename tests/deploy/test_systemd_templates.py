from pathlib import Path


def test_bot_systemd_template_uses_cli_module_and_project_paths():
    text = Path("deploy/systemd/amneziya-bot.service.example").read_text(
        encoding="utf-8"
    )

    assert "WorkingDirectory=/opt/amn2" in text
    assert "EnvironmentFile=/opt/amn2/.env" in text
    assert "ExecStart=/opt/amn2/venv/bin/python -m app.main" in text
    assert "Restart=on-failure" in text
    assert "User=amneziya" in text


def test_web_systemd_template_uses_web_cli_and_port_3030():
    text = Path("deploy/systemd/amneziya-web.service.example").read_text(
        encoding="utf-8"
    )

    assert "WorkingDirectory=/opt/amn2" in text
    assert "EnvironmentFile=/opt/amn2/.env" in text
    assert (
        "ExecStart=/opt/amn2/venv/bin/python -m app.cli web serve "
        "--host 0.0.0.0 --port 3030"
    ) in text
    assert "Restart=on-failure" in text
    assert "User=amneziya" in text


def test_agent_systemd_template_uses_localhost_agent_cli_and_runtime_access():
    text = Path("deploy/systemd/amneziya-agent.service.example").read_text(
        encoding="utf-8"
    )

    assert "WorkingDirectory=/opt/amn2" in text
    assert "EnvironmentFile=/opt/amn2/.env" in text
    assert (
        "ExecStart=/opt/amn2/venv/bin/python -m app.cli agent serve "
        "--host 127.0.0.1 --port 3031"
    ) in text
    assert "Restart=on-failure" in text
    assert "User=amneziya" in text
    assert "SupplementaryGroups=docker" in text
    assert "CapabilityBoundingSet=CAP_NET_ADMIN" in text
    assert "AmbientCapabilities=CAP_NET_ADMIN" in text
    assert "--host 0.0.0.0" not in text
