# Production VPS Checklist

Короткий путь перед первым тестом на живом VPS.

## 1. Получить код

```bash
git clone -b codex-vps-test-prep https://github.com/barakov-dot/amn2.git
cd amn2
```

## 2. Подготовить `.env`

```bash
cp .env.example .env
```

Заполнить минимум:

```env
TELEGRAM_BOT_TOKEN=...
APP_SECRET_KEY=...
ADMIN_TELEGRAM_IDS=...
VPS_APPLY_ENABLED=false
SERVER_CONFIG_PATH=servers.yml
SERVER_NAME=debian-vps-1
```

`APP_SECRET_KEY` сохранить отдельно. Потеря ключа означает потерю доступа к
зашифрованным peer-секретам.

## 3. Подготовить `servers.yml`

Файл не коммитить. Обязательные значения:

```yaml
ssh.host: VPS IP или домен
ssh.user: root или другой пользователь
ssh.auth.type: key или password
vpn.endpoint_host: публичный IP или домен
vpn.port: фиксированный UDP-порт, например 30001
vpn.network_cidr: 10.8.0.0/24
vpn.server_address: 10.8.0.1/24
vpn.server_public_key: public key сервера AmneziaWG
```

## 4. Локальная проверка

```bash
python -m pytest tests
python -m app.cli server preflight --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
```

## 5. Безопасные VPS dry-run

```bash
python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run
python -m app.cli server apply-peer --config servers.yml --server debian-vps-1 --public-key PEER_PUBLIC_KEY --preshared-key PEER_PSK --vpn-ip 10.8.0.2 --dry-run
python -m app.cli server revoke-peer --config servers.yml --server debian-vps-1 --public-key PEER_PUBLIC_KEY --dry-run
python -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3 --dry-run
```

## 6. Первый живой тест

Сначала выполнить read-only check:

```bash
python -m app.cli server check --config servers.yml --server debian-vps-1
```

Если check успешен, можно вручную проверить `apply-peer --apply` на тестовом peer.
Только после этого включать:

```env
VPS_APPLY_ENABLED=true
```

## 7. Backup

```bash
python -m app.cli backup create --db data/amneziya.sqlite3 --output backups
python -m app.cli backup verify --file backups/<backup-file>.tar.enc
```

Перед переносом на другой сервер обязательно сохранить `.env`, `servers.yml` и
backup-файл отдельно от репозитория.
