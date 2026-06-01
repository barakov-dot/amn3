# Установка `amn2` на VPS из пакета

Пакет собран из production-репозитория:

```text
repo: C:\Users\SooL\Documents\Amneziya
branch: codex-vps-test-prep
commit: d0939d8 Merge pull request #6 from barakov-dot/codex/ssh-host-key-identity-verifier
```

Архив с исходниками:

```text
amn2-source-d0939d8.zip
```

В пакет намеренно не включены `.env`, `.git`, `tmp`, `.pytest_cache`, логи,
локальная БД, backup-файлы и другие рабочие секреты. Все реальные значения
нужно задать на VPS вручную.

## 1. Скопировать пакет на VPS

Системные предпосылки:

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip
```

Пакет не содержит offline wheelhouse для Python-зависимостей: `pip install -e .`
будет ставить зависимости из PyPI или из настроенного вами package mirror.

Пример с локальной машины:

```bash
scp amn2-source-d0939d8.zip INSTALL_ON_VPS.ru.md install_on_vps.sh root@YOUR_VPS:/root/amn2-install/
```

На VPS:

```bash
cd /root/amn2-install
chmod +x install_on_vps.sh
sudo ./install_on_vps.sh
```

По умолчанию helper ставит проект в `/opt/amn2` и отказывается продолжать, если
там уже есть файлы. Для осознанной перезаписи можно передать `--force`:

```bash
sudo ./install_on_vps.sh --force
```

## 2. Настроить `.env`

После распаковки:

```bash
cd /opt/amn2
sudo cp deploy/examples/.env.production.example .env
sudo nano .env
```

Минимально заполнить:

```env
TELEGRAM_BOT_TOKEN=...
APP_SECRET_KEY=...
ADMIN_TELEGRAM_IDS=...
DATABASE_PATH=data/amneziya.sqlite3
SERVER_CONFIG_PATH=servers.yml
SERVER_NAME=debian-vps-1
VPS_APPLY_ENABLED=false
WEB_ADMIN_ENABLED=true
WEB_ADMIN_HOST=0.0.0.0
WEB_ADMIN_PORT=3030
WEB_ADMIN_USERNAME=admin
WEB_ADMIN_PASSWORD_HASH=...
WEB_ADMIN_SESSION_SECRET=...
WEB_ADMIN_SESSION_COOKIE_SECURE=false
```

Важно: для первого запуска держать `VPS_APPLY_ENABLED=false`. Включать live
apply только после read-only/dry-run проверок.

Сгенерировать hash пароля web-панели:

```bash
cd /opt/amn2
source venv/bin/activate
python -m app.cli web hash-password
```

Сгенерировать session secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 3. Настроить `servers.yml`

Выбрать пример под runtime:

```bash
cd /opt/amn2
sudo cp deploy/examples/servers.docker.example.yml servers.yml
# или:
sudo cp deploy/examples/servers.host_systemd.example.yml servers.yml
sudo nano servers.yml
```

Перед первым SSH/live действием отдельно проверить host key:

```bash
ssh-keyscan -p 22 YOUR_VPS_HOST > host-key.txt
ssh-keygen -lf host-key.txt -E sha256
```

Fingerprint сверить вне SSH-сессии: через панель провайдера, rescue console,
заранее сохраненный pin или другой доверенный канал. Если ключ неизвестен или
не совпадает, live SSH-backed операции не запускать.

## 4. Проверить локальный запуск на VPS

```bash
cd /opt/amn2
source venv/bin/activate
python -m app.cli bot check-network
python -m app.cli server preflight --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run
```

Запуск web-панели вручную:

```bash
python -m app.cli web serve --host 0.0.0.0 --port 3030
```

Запуск Telegram-бота вручную:

```bash
python -m app.main
```

## 5. Включить systemd только после ручной проверки

```bash
sudo cp deploy/systemd/amneziya-web.service.example /etc/systemd/system/amneziya-web.service
sudo cp deploy/systemd/amneziya-bot.service.example /etc/systemd/system/amneziya-bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now amneziya-web
sudo systemctl enable --now amneziya-bot
sudo systemctl status amneziya-web --no-pager
sudo systemctl status amneziya-bot --no-pager
```

Логи:

```bash
sudo journalctl -u amneziya-web -n 200 --no-pager
sudo journalctl -u amneziya-bot -n 200 --no-pager
```

## 6. Что не делать первым шагом

- Не включать `VPS_APPLY_ENABLED=true` до dry-run/read-only gate.
- Не хранить raw web password, Telegram token, private key или PSK в shell
  history.
- Не публиковать web-панель `:3030` в интернет без firewall, reverse proxy,
  HTTPS или SSH tunnel.
- Не запускать `apply-peer --apply` или `revoke-peer --apply` без отдельного
  операторского подтверждения.
