# Emergency Restore Checklist

Короткий сценарий аварийного переноса сервиса на новый сервер.

## Что должно быть сохранено заранее

- `.env` с тем же `APP_SECRET_KEY`;
- `servers.yml` или новый файл для нового VPS;
- последний backup-файл из `backups/`;
- доступ к GitHub-репозиторию;
- доступ к Telegram bot token.

Без исходного `APP_SECRET_KEY` зашифрованные peer private keys и PSK нельзя
расшифровать.

## 1. Поднять новый VPS

Установить Python 3.12+, Git и системные зависимости AmneziaWG. До проверки
держать `VPS_APPLY_ENABLED=false`.

## 2. Получить проект

```bash
git clone -b codex-vps-test-prep https://github.com/barakov-dot/amn2.git
cd amn2
```

## 3. Восстановить локальные файлы

```bash
cp /secure-copy/.env .env
cp /secure-copy/servers.yml servers.yml
```

Проверить:

```env
APP_SECRET_KEY=тот_же_ключ_что_при_backup
TELEGRAM_BOT_TOKEN=токен_бота
ADMIN_TELEGRAM_IDS=telegram_id_админов
VPS_APPLY_ENABLED=false
```

## 4. Восстановить базу

```bash
python -m app.cli backup verify --file backups/<backup-file>.tar.enc
python -m app.cli backup restore --file backups/<backup-file>.tar.enc --target-db data/amneziya.sqlite3 --force
```

## 5. Проверить сервер

```bash
python -m app.cli server preflight --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run
python -m app.cli server check --config servers.yml --server debian-vps-1
```

## 6. Вернуть выдачу конфигов

После успешного live check и тестового `apply-peer --dry-run` включить:

```env
VPS_APPLY_ENABLED=true
```

Затем перезапустить бота.

## 7. Проверить клиентов

- запросить тестовую заявку;
- одобрить ее админом;
- импортировать конфиг в клиент;
- проверить подключение;
- выполнить `collect-traffic`;
- проверить трафик в боте.
