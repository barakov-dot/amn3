# Дизайн Server Check

## Цель

Добавить первый безопасный шаг интеграции с VPS: `server check`.

Команда читает `servers.yml`, выбирает один настроенный VPS, подключается по SSH и запускает read-only проверки, которые помогают понять, готов ли сервер к управлению AmneziaWG.

Команда не должна изменять VPS.

## Scope

Включено:

- parse and validate `servers.yml`;
- select server by name;
- represent SSH settings without logging secrets;
- SSH client abstraction для тестов без реального VPS;
- read-only checks:
  - SSH connectivity;
  - OS release;
  - Debian detection;
  - systemd availability;
  - `awg`;
  - `awg-quick`;
  - `ufw`;
  - VPN interface status;
  - UDP port visibility command.
- structured report with `ok`, `warning`, `error`;
- CLI command:

```powershell
python -m app.cli server check --config servers.yml --server debian-vps-1
```

Исключено:

- installing packages;
- enabling IP forwarding;
- opening firewall ports;
- creating or editing AmneziaWG config;
- adding or revoking peers;
- writing to VPS;
- uploading files;
- interactive questions.

## Архитектура

```text
app/server_config/
  models.py
  loader.py
app/server/
  checks.py
  report.py
  ssh.py
```

`server_config.models` содержит dataclasses для server config.

`server_config.loader` читает YAML и валидирует обязательные fields.

`server.ssh` задает interface SSH client. Реальный backend добавляется после тестирования check logic.

`server.checks` оркестрирует read-only checks.

`server.report` форматирует safe structured output.

## Safety

Все команды проходят через allowlist. Mutating commands вроде `apt install`, `systemctl start`, `ufw allow`, `rm`, shell redirects и pipes запрещены.

## Testing

Тесты используют fake SSH client и проверяют:

- successful Debian readiness report;
- missing `awg`/`awg-quick` as warning;
- report redaction;
- command policy rejection for mutating commands;
- CLI parser accepts `server check`.

## Acceptance Criteria

- Check runner can be tested without real VPS.
- No command can bypass read-only policy.
- CLI shape is stable.
- Report redacts secrets.
- Full test suite passes.
