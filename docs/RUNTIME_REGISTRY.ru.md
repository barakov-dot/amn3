# Runtime Registry

Этот документ фиксирует, какие runtime-зависимости нужны проекту Amneziya, где они описаны в репозитории и как быстро проверить VPS перед повторным тестом.

## Что храним в Git

В репозитории храним только легкие и проверяемые артефакты:

- `deploy/runtime/manifest.yml` - единый manifest runtime-требований;
- `deploy/runtime/check_vps.sh` - read-only проверка VPS;
- `deploy/examples/servers.host_systemd.example.yml` - пример `servers.yml` для host/systemd;
- `deploy/examples/servers.docker.example.yml` - пример `servers.yml` для Docker runtime;
- `deploy/examples/.env.production.example` - полный production-шаблон `.env` без реальных секретов;
- `deploy/examples/nginx-proxy-manager-notes.ru.md` - памятка по reverse proxy для web-панели.

## Не храним в Git

Не храним в Git:

- настоящий `.env`;
- настоящий `servers.yml`;
- SSH private keys;
- Telegram bot token;
- `APP_SECRET_KEY`;
- SQLite database;
- backup archives;
- generated client `.conf`;
- QR images;
- Docker images;
- `.venv`, `.codex_deps`, `node_modules`;
- логи с приватными данными.

Если позже понадобится закреплять тяжелые бинарные артефакты, используем GitHub Releases или отдельное хранилище, а в репозитории держим URL, версию и checksum.

## Runtime modes

### `host_systemd`

AmneziaWG работает на хосте Debian и управляется через `systemd`, `awg`, `awg-quick`.

Минимальный блок:

```yaml
runtime:
  type: host_systemd
  service_name: awg-quick@awg0
```

Read-only проверки:

```bash
command -v systemctl
command -v awg
command -v awg-quick
systemctl is-active awg-quick@awg0
awg show awg0
ss -lun
```

### `docker`

AmneziaWG работает внутри Docker-контейнера. На текущем этапе Docker runtime включен только для диагностики.

Минимальный блок:

```yaml
runtime:
  type: docker
  container_name: amnezia-awg
```

Read-only проверки:

```bash
command -v docker
docker ps --format '{{.Names}}'
docker exec amnezia-awg command -v awg
docker exec amnezia-awg awg show awg0
ss -lun
```

Live `apply-peer`, `revoke-peer` и `collect-traffic` для Docker пока заблокированы, пока мы не подтвердим постоянный путь к конфигу контейнера и безопасный способ применения peer.

## Быстрая проверка VPS

Скопировать или запустить из репозитория:

```bash
cd /opt/amn2
bash deploy/runtime/check_vps.sh
```

Для Docker runtime:

```bash
cd /opt/amn2
AMN_RUNTIME=docker AMN_CONTAINER_NAME=amnezia-awg AMN_INTERFACE=awg0 bash deploy/runtime/check_vps.sh
```

Для нестандартного порта web-панели или VPN:

```bash
AMN_WEB_PORT=3030 AMN_VPN_PORT=30001 bash deploy/runtime/check_vps.sh
```

Скрипт не устанавливает пакеты, не меняет firewall, не перезапускает сервисы и не пишет файлы. Он только читает состояние VPS и возвращает код `1`, если есть критические ошибки.

## Как актуализировать

Когда появляется новая обязательная зависимость:

1. Добавить ее в `deploy/runtime/manifest.yml`.
2. Добавить read-only проверку в `deploy/runtime/check_vps.sh`.
3. Обновить пример в `deploy/examples/`, если меняется конфигурация.
4. Обновить этот документ.
5. Добавить или обновить тест в `tests/deploy/test_runtime_registry.py`.

Так мы сохраняем знания внутри проекта, но не превращаем Git-репозиторий в склад бинарников.
