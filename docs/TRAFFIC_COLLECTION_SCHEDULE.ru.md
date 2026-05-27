# Traffic Collection Schedule

Сбор трафика выполняется командой:

```bash
python -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
```

Команда читает `awg show awg0 dump`, сохраняет snapshots в БД и обновляет
`first_connected_at` / `last_connected_at`.

## Проверка перед расписанием

```bash
python -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3 --dry-run
python -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
```

## Вариант cron

Открыть crontab:

```bash
crontab -e
```

Добавить запуск каждые 5 минут:

```cron
*/5 * * * * cd /opt/amn2 && /usr/bin/python3 -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3 >> logs/traffic.log 2>&1
```

## Вариант systemd timer

`/etc/systemd/system/amneziya-traffic.service`:

```ini
[Unit]
Description=Collect Amneziya traffic

[Service]
Type=oneshot
WorkingDirectory=/opt/amn2
ExecStart=/usr/bin/python3 -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
```

`/etc/systemd/system/amneziya-traffic.timer`:

```ini
[Unit]
Description=Run Amneziya traffic collection every 5 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Unit=amneziya-traffic.service

[Install]
WantedBy=timers.target
```

Включить:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now amneziya-traffic.timer
sudo systemctl list-timers amneziya-traffic.timer
```

## Проверка результата

```bash
sudo systemctl status amneziya-traffic.service
tail -n 100 logs/traffic.log
```

В боте проверить разделы `Мой трафик` и админский `Трафик`.
