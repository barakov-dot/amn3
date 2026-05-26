# Amneziya VPN Automation

Проект для автоматического разворачивания AmneziaWG 2.0 на собственном VPS и управления пользовательскими VPN-конфигами через Telegram-бота.

## Цель

Сделать систему, которая:

- разворачивает AmneziaWG 2.0 на чистом VPS;
- создает VPN-доступы по запросу пользователя или администратора;
- выдает `.conf`, QR-код и ссылку/ключ для импорта;
- хранит сроки действия доступов;
- отключает просроченные конфиги;
- поддерживает оплату или ручную проверку перед выдачей;
- готова к расширению на несколько серверов.

## Документы

- [Техническое задание](docs/TECH_SPEC.md)
- [План реализации](docs/IMPLEMENTATION_PLAN.md)
- [Принятые решения](docs/DECISIONS.md)
- [Модель данных MVP](docs/DATA_MODEL.md)
- [Управление VPN-серверами](docs/SERVER_MANAGEMENT.md)
- [Шаблон конфигурации серверов](docs/SERVER_CONFIG_TEMPLATE.md)
- [Открытые вопросы](docs/OPEN_QUESTIONS.md)

## Рекомендуемый стек

- Python 3.12+
- aiogram 3.x
- PostgreSQL для продакшна, SQLite для локального MVP
- Docker Compose для бота и вспомогательных сервисов
- SSH/SFTP для первичного provisioning VPS
- systemd + `awg`/`awg-quick` на VPS для AmneziaWG

## Базовый сценарий

1. Администратор добавляет VPS в конфигурацию проекта.
2. Provisioning-скрипт устанавливает AmneziaWG 2.0 и настраивает firewall/NAT.
3. Пользователь пишет Telegram-боту.
4. Бот проверяет оплату или отправляет заявку администратору.
5. После подтверждения бот создает peer, назначает IP и срок действия.
6. Пользователь получает `.conf`, QR-код и импортируемую ссылку, если формат поддержан.
7. Планировщик регулярно отключает просроченные peer.

## Local Development

1. Create `.env` from `.env.example`.
2. Set `TELEGRAM_BOT_TOKEN`, `APP_SECRET_KEY`, and `ADMIN_TELEGRAM_IDS`.
3. Install dependencies.
4. Run tests with `pytest`.
5. Start the bot with `python -m app.main`.

## Backup

Create a local encrypted backup:

```powershell
python -m app.cli backup create --db data/amneziya.sqlite3 --output backups
```

Verify a backup:

```powershell
python -m app.cli backup verify --file backups/<backup-file>.tar.enc
```

Restore to a new database path:

```powershell
python -m app.cli backup restore --file backups/<backup-file>.tar.enc --target-db data/restored.sqlite3
```

The same `APP_SECRET_KEY` used when creating encrypted peer secrets is required for restore validation.
