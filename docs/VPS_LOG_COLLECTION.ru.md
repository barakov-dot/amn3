# Сбор логов и диагностики с VPS

Этот документ нужен для быстрого обмена данными по первому живому VPS-тесту. Цель - получить один полный read-only snapshot без установки пакетов, перезапуска сервисов и изменения firewall.

## Быстрый способ

На VPS:

```bash
cd /opt/amn2
bash deploy/runtime/collect_debug_snapshot.sh
```

Для Docker-ноды:

```bash
cd /opt/amn2
AMN_RUNTIME=docker AMN_CONTAINER_NAME=amnezia-awg AMN_INTERFACE=awg0 bash deploy/runtime/collect_debug_snapshot.sh
```

Если имя сервера или путь к `servers.yml` отличается:

```bash
AMN_SERVER_NAME=debian-vps-1 AMN_SERVER_CONFIG=servers.yml bash deploy/runtime/collect_debug_snapshot.sh
```

Если нужно больше или меньше строк логов:

```bash
AMN_LOG_LINES=300 bash deploy/runtime/collect_debug_snapshot.sh
```

Скрипт печатает отчет в консоль. Если удобно сохранить в файл:

```bash
bash deploy/runtime/collect_debug_snapshot.sh > debug-snapshot.txt 2>&1
```

Перед отправкой файла все равно быстро просмотреть его глазами.

## Что собирает скрипт

`deploy/runtime/collect_debug_snapshot.sh` собирает:

- дату и базовую информацию о системе;
- `git log -1 --oneline --decorate`;
- `git status --short`;
- версию Python;
- наличие директорий `data`, `logs`, `backups`, `config_templates`;
- список ключей из `.env` без значений;
- `python -m app.cli server check --config ... --server ... --dry-run`;
- `python -m app.cli server check --config ... --server ...`;
- `bash deploy/runtime/check_vps.sh`;
- `python -m app.cli bot check-network`;
- `ss -lntp` и `ss -lun`;
- `systemctl is-active amneziya-agent`;
- `systemctl show amneziya-agent -p ActiveState -p SubState -p MainPID -p NRestarts`;
- `journalctl -u amneziya-web -n 200 --no-pager`;
- `journalctl -u amneziya-bot -n 200 --no-pager`;
- `journalctl -u amneziya-agent -n 200 --no-pager`;
- `tail -n 200 logs/app.log`.

Для Docker runtime дополнительно:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker inspect amnezia-awg --format '{{.Name}} {{.State.Status}} {{.Config.Image}} {{json .Mounts}}'
docker exec amnezia-awg awg show awg0
```

Для host/systemd runtime дополнительно:

```bash
systemctl is-active awg-quick@awg0
systemctl show awg-quick@awg0 -p ActiveState -p SubState -p MainPID -p NRestarts
awg show awg0
```

## Ручной минимальный набор

Если скрипт по какой-то причине не запускается, прислать вывод этих команд:

```bash
cd /opt/amn2
git log -1 --oneline --decorate
git status --short
python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run
python -m app.cli server check --config servers.yml --server debian-vps-1
bash deploy/runtime/check_vps.sh
sudo systemctl is-active amneziya-agent
sudo systemctl show amneziya-agent -p ActiveState -p SubState -p MainPID -p NRestarts
sudo journalctl -u amneziya-web -n 200 --no-pager
sudo journalctl -u amneziya-bot -n 200 --no-pager
sudo journalctl -u amneziya-agent -n 200 --no-pager
tail -n 200 logs/app.log
```

Для Docker-ноды добавить:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker inspect amnezia-awg --format '{{.Name}} {{.State.Status}} {{.Config.Image}} {{json .Mounts}}'
docker exec amnezia-awg awg show awg0
```

## Что скрыть перед отправкой

Скрипт автоматически пытается скрывать основные секреты, но перед отправкой все равно проверить, что в отчете нет:

- `TELEGRAM_BOT_TOKEN`;
- `APP_SECRET_KEY`;
- `WEB_ADMIN_PASSWORD_HASH`;
- `WEB_ADMIN_SESSION_SECRET`;
- `LOCAL_AGENT_TOKEN_HASH`;
- raw Local Agent Bearer token;
- `SMTP_PASSWORD`;
- `VPS_SSH_PASSWORD`;
- SSH private key;
- WireGuard/AmneziaWG `PrivateKey`;
- WireGuard/AmneziaWG `PresharedKey`;
- полного пользовательского `.conf`;
- backup archive names, если они раскрывают приватную структуру.

Public keys, IP-адреса, имена контейнеров, service status и вывод `awg show` без private/preshared keys можно присылать для диагностики.

## Чего скрипт не делает

Скрипт не выполняет:

- установку пакетов;
- изменение `ufw`/firewall;
- перезапуск systemd services;
- остановку или удаление Docker-контейнеров;
- изменение peer;
- запись в базу данных;
- создание backup.

Это диагностический read-only слой. Для исправлений ждем анализ отчета.
