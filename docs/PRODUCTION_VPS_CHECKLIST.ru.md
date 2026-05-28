# Production VPS Checklist

Короткий путь перед первым тестом на живом VPS.

## 1. Получить код

```bash
git clone -b codex-vps-test-prep https://github.com/barakov-dot/amn2.git
cd amn2
```

## 2. Подготовить Python-окружение

На новом VPS:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

Если проект уже был склонирован ранее и нужно получить свежие изменения:

```bash
git pull
source venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

## 3. Подготовить `.env`

```bash
cp .env.example .env
```

Заполнить минимум:

```env
TELEGRAM_BOT_TOKEN=CHANGE_ME_TOKEN_FROM_BOTFATHER
TELEGRAM_PROXY_URL=
APP_SECRET_KEY=CHANGE_ME_GENERATED_RANDOM_SECRET_32_PLUS_CHARS
ADMIN_TELEGRAM_IDS=CHANGE_ME_ADMIN_TELEGRAM_IDS
VPS_APPLY_ENABLED=false
SERVER_CONFIG_PATH=servers.yml
SERVER_NAME=debian-vps-1
```

Если VPS не открывает `https://api.telegram.org` напрямую, указать SOCKS5 proxy:

```env
TELEGRAM_PROXY_URL=socks5://127.0.0.1:1080
```

Перед запуском бота проверить доступ через тот же proxy:

```bash
curl --socks5-hostname 127.0.0.1:1080 -I https://api.telegram.org
python -m app.cli bot check-network
```

`APP_SECRET_KEY` сохранить отдельно. Потеря ключа означает потерю доступа к
зашифрованным peer-секретам.

## 4. Шаблоны и выдача конфига

Текущие варианты получения конфига пользователем:

- Telegram-сообщение по шаблону `config_ready`;
- вложенный `.conf` файл;
- QR-код;
- повторная отправка пользователем из своих устройств;
- повторная отправка администратором;
- аварийная отправка raw config text, если файл/QR не ушли после создания устройства.

В доработке web-панели добавляется отдельный шаблон клиентского `.conf` по версиям
`amneziawg_v1_5` и `amneziawg_v2`, а также ссылка вида `vpn://...`.
После реализации держать VPS-правки шаблонов во внешней директории:

```env
CLIENT_CONFIG_TEMPLATE_DIR=config_templates
```

Шаблон содержит постоянные строки конфига и placeholders для переменных значений
пользователя/устройства. `.conf` файл остается каноническим способом доставки,
пока `vpn://` импорт не проверен на реальном AmneziaVPN-клиенте.

## 5. Подготовить `servers.yml`

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

## 6. Локальная проверка

```bash
python -m pytest tests
python -m app.cli server preflight --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
```

## 7. Безопасные VPS dry-run

```bash
python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run
python -m app.cli server apply-peer --config servers.yml --server debian-vps-1 --public-key PEER_PUBLIC_KEY --preshared-key PEER_PSK --vpn-ip 10.8.0.2 --dry-run
python -m app.cli server revoke-peer --config servers.yml --server debian-vps-1 --public-key PEER_PUBLIC_KEY --dry-run
python -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3 --dry-run
```

## 8. Первый живой тест

Сначала выполнить read-only check:

```bash
python -m app.cli server check --config servers.yml --server debian-vps-1
```

Если check успешен, можно вручную проверить `apply-peer --apply` на тестовом peer.
Только после этого включать:

```env
VPS_APPLY_ENABLED=true
```

## 9. Backup

```bash
python -m app.cli backup create --db data/amneziya.sqlite3 --output backups
python -m app.cli backup verify --file backups/<backup-file>.tar.enc
```

Перед переносом на другой сервер обязательно сохранить `.env`, `servers.yml` и
backup-файл отдельно от репозитория.
