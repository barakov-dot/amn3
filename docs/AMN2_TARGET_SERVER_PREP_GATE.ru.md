# AMN2 Target Server Prep Gate

Дата: 2026-06-08.

Назначение: безопасно подготовить новый целевой VPS для следующего AMN2 gate, не включая service mode, не открывая public API и не передавая секреты в чат или GitHub.

Этот документ является read-only/status/docs slice. Он не заменяет `docs/AMN2_PRODUCTION_LAUNCH_GATE.ru.md` и не разрешает `systemd`/reverse proxy deployment сам по себе.

## Текущая Точка Правды

```text
current AMN2 source overlay/package: f7f6131 Update integration status for c92 manual prelaunch
package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
latest VPS smoke: read-only-vps-smoke-pass
source_update_run_id: 20260607T203721Z
api_smoke_run_id: 20260607T203730Z
latest_repeat_api_smoke_run_id: 20260607T204300Z
allowed current work: target server preparation, read-only/status/docs
blocked: write/API/config/backup/agent/service-mode gates
```

## Что Подготовить При Аренде VPS

Минимальный профиль:

- Debian 12 или Ubuntu 22.04/24.04 LTS;
- root/operator shell доступ через провайдера или ваш SSH-клиент для ручного выполнения команд;
- 2 GB RAM минимум, лучше 4 GB;
- 20+ GB disk;
- публичный IPv4, если VPN endpoint должен быть доступен клиентам;
- возможность настроить DNS и HTTPS reverse proxy для web/admin;
- возможность закрыть direct public `3030/tcp` и `3040/tcp`;
- возможность открыть только нужные внешние порты: HTTPS `443/tcp`, при необходимости `80/tcp` для ACME, и VPN transport port по отдельному решению.

Важно: Codex не нужен root password, SSH private key, bot token, `.env`, `servers.yml` целиком или backup. Все действия можно выполнять вручную по runbook, а сюда возвращать только safe summary.

## Предварительная Сетевая Граница

Сразу закладываем такую модель:

```text
web/admin backend: 127.0.0.1:3030
web/admin public access: HTTPS reverse proxy only
API smoke backend: 127.0.0.1:3040
public API 3040: no
direct public web 3030: no
VPS_APPLY_ENABLED: false
service mode: not enabled until separate gate
```

Не открывать наружу:

- `3030/tcp`;
- `3040/tcp`;
- Local Agent ports;
- debug/log endpoints;
- database/filesystem paths.

## Что Можно Делать До Отдельного Service Gate

Разрешено:

- арендовать VPS и выбрать OS;
- подготовить DNS/домен для будущего HTTPS reverse proxy;
- установить базовые пакеты OS;
- создать рабочий каталог `/opt/amn2`;
- подготовить Python venv;
- загрузить AMN3 update/smoke kit `f7f6131`;
- выполнить checksum verification;
- применить source overlay с `VPS_APPLY_ENABLED=false`;
- выполнить read-only API loopback smoke;
- подготовить `.env` локально на VPS, не публикуя его содержимое;
- проверить, что `3030` и `3040` не доступны публично;
- собрать safe summary.

Запрещено без отдельного подтверждения:

- `VPS_APPLY_ENABLED=true`;
- `apply-peer --apply` или `revoke-peer --apply`;
- public API exposure;
- direct public web/admin `3030`;
- включать `systemd` web/bot services;
- включать HTTPS reverse proxy как production path;
- добавлять API `config:read`, write CRUD, backup/import/reboot routes;
- включать Local Agent write/config routes;
- публиковать raw token, Authorization header, token hash, `.env`, `servers.yml`, PrivateKey, PresharedKey, `.conf`, QR, `vpn://`, full logs или backup contents.

## Safe Precheck Команды

На новом VPS можно выполнить и вернуть только итоговые строки:

```bash
echo "== os =="
hostnamectl | sed -n 's/^ *Operating System:/os:/p; s/^ *Kernel:/kernel:/p; s/^ *Architecture:/arch:/p'

echo "== python =="
python3 --version || true

echo "== required commands =="
for c in curl sha256sum python3 ss; do
  command -v "$c" >/dev/null 2>&1 && echo "$c=present" || echo "$c=missing"
done

echo "== listeners safe =="
ss -ltnp | grep -E ':3030|:3040' || echo "amn2_loopback_listeners=absent"

echo "== firewall note =="
command -v ufw >/dev/null 2>&1 && ufw status || echo "ufw=not-installed-or-not-used"
```

Не возвращать публичный IP, SSH details, provider console URL, токены или `.env`.

## Target Server Source Overlay Gate

Когда сервер готов к первому read-only AMN2 gate, использовать текущий пакет:

Для текущего опубликованного AMN3 kit использовать raw URL без GitHub token и без Authorization header:

```bash
cd /root

curl -fL -o amn2-vps-update-and-smoke-kit-f7f6131.zip \
  https://github.com/barakov-dot/amn3/raw/master/dist/amn2-vps-update-and-smoke-kit-f7f6131.zip

curl -fL -o amn2-vps-update-and-smoke-kit-f7f6131.zip.sha256.txt \
  https://raw.githubusercontent.com/barakov-dot/amn3/master/dist/amn2-vps-update-and-smoke-kit-f7f6131.zip.sha256.txt

sha256sum -c amn2-vps-update-and-smoke-kit-f7f6131.zip.sha256.txt
```

Если скачивание недоступно, остановиться и вернуться в чат с safe summary. Не вводить GitHub token в команды из чата и не публиковать Authorization header.

Дальше применять только после отдельного сообщения в чат, чтобы мы проверили precheck и не смешали target server gate с validation VPS.

## Safe Summary Для Возврата

После precheck вернуть только:

```text
target_server_prep_status:
os:
kernel:
arch:
python:
curl:
sha256sum:
ss:
amn2_loopback_listeners:
ufw_status_summary:
dns_or_admin_domain_ready: yes/no
https_reverse_proxy_ready: yes/no/not-yet
direct_public_3030: no
public_api_3040: no
VPS_APPLY_ENABLED: false/not-set
next_requested_gate: source-overlay-read-only-smoke | service-mode-gate | docs-only
```

Если что-то не готово, достаточно написать `not-yet`. Не нужно исправлять всё в одном заходе.

## Decision

Новый сервер можно считать подготовленным к следующему read-only gate только если:

- OS и Python доступны;
- checksum tooling доступен;
- прямой public `3030/3040` не открыт;
- выбран способ будущего HTTPS reverse proxy, но production service mode еще не включен;
- оператор понимает, что secrets не публикуются;
- следующий шаг явно выбран как read-only source-overlay smoke или отдельный service-mode gate.
