import pytest

from app.server.checks import CommandPolicyError, ensure_read_only_command


def test_policy_allows_known_read_only_commands():
    ensure_read_only_command("cat /etc/os-release")
    ensure_read_only_command("command -v awg")
    ensure_read_only_command("systemctl is-active awg-quick@awg0")
    ensure_read_only_command("ss -lun")


@pytest.mark.parametrize(
    "command",
    [
        "apt install amneziawg",
        "systemctl start awg-quick@awg0",
        "ufw allow 30001/udp",
        "rm /tmp/file",
        "cat /etc/os-release > out.txt",
        "sed -i s/a/b/ file",
    ],
)
def test_policy_rejects_mutating_commands(command):
    with pytest.raises(CommandPolicyError):
        ensure_read_only_command(command)
