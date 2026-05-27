# Traffic Collection Schedule

Traffic collection runs with:

```bash
python -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
```

The command reads `awg show awg0 dump`, stores snapshots in the database, and
updates `first_connected_at` / `last_connected_at`.

## Check Before Scheduling

```bash
python -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3 --dry-run
python -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
```

## cron Option

Open crontab:

```bash
crontab -e
```

Run every 5 minutes:

```cron
*/5 * * * * cd /opt/amn2 && /usr/bin/python3 -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3 >> logs/traffic.log 2>&1
```

## systemd Timer Option

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

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now amneziya-traffic.timer
sudo systemctl list-timers amneziya-traffic.timer
```

## Verify

```bash
sudo systemctl status amneziya-traffic.service
tail -n 100 logs/traffic.log
```

In the bot, check `My traffic` and admin `Traffic`.
