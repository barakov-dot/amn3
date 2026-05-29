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
