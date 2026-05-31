# AMN3 Local Agent VPS Smoke Checklist

Для соседнего чата `Переводим AMN на API` использовать короткий пакет `docs/AMN3_VPS_TEST_PACKET.ru.md`.
Результат реального VPS smoke фиксировать в `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`.

Короткий маршрут для первого переноса текущей Local Agent наработки в приватный
репозиторий `barakov-dot/amn3` и проверки на живом сервере Amneziya.

Этот документ не заменяет полный runbook `docs/LOCAL_AGENT_VPS_SMOKE_RUNBOOK.ru.md`.
Он фиксирует быстрый порядок именно для текущей интеграционной ветки.

## 0. Что проверяем

- GitHub target: `https://github.com/barakov-dot/amn3.git`.
- Интеграционная ветка: `codex/local-agent-production-wiring`.
- Минимальный функциональный baseline: `fdc471a Show Local Agent health in web admin`.
- Серверный путь остается `/opt/amn2`, потому что systemd templates, env paths и
  существующие VPS-документы уже завязаны на этот runtime path.
- Первый режим только read-only: health, runtime, protocols.
- Agent слушает только `127.0.0.1:3031`; внешний порт `3031` не открывать.

## 1. Подготовить push в AMN3 с рабочей машины

В локальном worktree:

```powershell
cd C:\Users\SooL\Documents\Amneziya\.codex_deps\worktrees\local-agent-production-wiring
git status --short --branch
git log -3 --oneline --decorate
git remote -v
```

Если `origin` еще указывает на `amn2`, сохранить старый remote и назначить `amn3`
как основной:

```powershell
git remote rename origin amn2
git remote add origin https://github.com/barakov-dot/amn3.git
git remote -v
```

Первый push ветки:

```powershell
git push -u origin codex/local-agent-production-wiring
```

После успешного `-u` следующие публикации этой ветки идут обычным:

```powershell
git push
```

## 2. Получить ветку на VPS

На VPS:

```bash
cd /opt/amn2
git remote -v
git fetch origin codex/local-agent-production-wiring
git switch codex/local-agent-production-wiring
git pull --ff-only origin codex/local-agent-production-wiring
git log -1 --oneline --decorate
```

Ожидание: `git log -1` показывает `fdc471a` или более новый коммит этой же ветки.

Обновить Python package:

```bash
test -d venv || python3 -m venv venv
./venv/bin/python -m pip install -U pip
./venv/bin/python -m pip install -e .
```

## 3. Создать Local Agent token безопасно

Сгенерировать raw token и сохранить его в password manager:

```bash
./venv/bin/python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Записать raw token только в отдельный файл на VPS:

```bash
sudo install -d -m 0750 -o amneziya -g amneziya /opt/amn2/secrets
sudo install -m 0600 -o amneziya -g amneziya /dev/null /opt/amn2/secrets/local-agent.token
read -rsp "Local Agent raw token: " LOCAL_AGENT_RAW_TOKEN; echo
printf '%s\n' "$LOCAL_AGENT_RAW_TOKEN" | sudo tee /opt/amn2/secrets/local-agent.token >/dev/null
unset LOCAL_AGENT_RAW_TOKEN
```

Сгенерировать hash для `.env`:

```bash
./venv/bin/python -m app.cli agent hash-token
```

Команда интерактивно попросит raw token и выведет `sha256:<generated-hash>`.
В `.env` записывается только hash, не raw token.

## 4. Включить agent и controller probe в `.env`

В `/opt/amn2/.env`:

```env
LOCAL_AGENT_ENABLED=true
LOCAL_AGENT_HOST=127.0.0.1
LOCAL_AGENT_PORT=3031
LOCAL_AGENT_TOKEN_ID=local-controller
LOCAL_AGENT_TOKEN_HASH=sha256:<generated-hash>
LOCAL_AGENT_TOKEN_OWNER=local-controller
LOCAL_AGENT_TOKEN_SCOPES=agent:health,agent:read,agent:protocols:read
LOCAL_AGENT_TOKEN_EXPIRES_AT=
LOCAL_AGENT_CONTROLLER_ENABLED=true
LOCAL_AGENT_CONTROLLER_BASE_URL=http://127.0.0.1:3031
LOCAL_AGENT_CONTROLLER_TOKEN_PATH=/opt/amn2/secrets/local-agent.token
```

Проверить, что raw token не попал в `.env`:

```bash
grep -n 'LOCAL_AGENT' /opt/amn2/.env
```

## 5. Проверить agent вручную до systemd

В первом SSH-сеансе:

```bash
cd /opt/amn2
./venv/bin/python -m app.cli agent serve --host 127.0.0.1 --port 3031
```

Во втором SSH-сеансе:

```bash
cd /opt/amn2
read -rsp "Local Agent raw token: " LOCAL_AGENT_RAW_TOKEN; echo
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/health
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/runtime
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/protocols
unset LOCAL_AGENT_RAW_TOKEN
```

Проверить штатный read-only client:

```bash
python -m app.cli agent probe --base-url http://127.0.0.1:3031
```

Ожидание:

- `/agent/health` отвечает `ok`;
- `/agent/runtime` возвращает `running`, `stopped`, `degraded` или `unknown`;
- `/agent/protocols` не содержит private key, PSK, QR, `vpn://` или client config.

## 6. Установить systemd service

```bash
cd /opt/amn2
sudo install -m 0644 deploy/systemd/amneziya-agent.service.example /etc/systemd/system/amneziya-agent.service
sudo systemctl daemon-reload
sudo systemctl enable --now amneziya-agent
sudo systemctl status amneziya-agent --no-pager
ss -lntp | grep ':3031'
```

Ожидание: bind только на `127.0.0.1:3031`.

Если runtime Docker и agent возвращает `degraded` из-за Docker socket, сначала
проверить доступ пользователя:

```bash
sudo -u amneziya docker ps
```

`SupplementaryGroups=docker` включать только после осознанного решения, потому
что доступ к Docker socket является привилегированным.

## 7. Проверить web admin integration

Перезапустить web service:

```bash
cd /opt/amn2
sudo systemctl restart amneziya-web
sudo systemctl status amneziya-web --no-pager
curl -i http://127.0.0.1:3030/login
```

В web admin открыть карточку сервера. Ожидаемый минимум:

- блок `Local Agent` отображается;
- status `online`, `degraded`, `offline`, `unknown` или `disabled` понятен;
- base URL равен `http://127.0.0.1:3031`;
- runtime показывает `docker` или `host_systemd`;
- protocols показывают `amneziawg`, interface/container и количество clients;
- raw token нигде не отображается.

## 8. Собрать диагностический snapshot

```bash
cd /opt/amn2
bash deploy/runtime/collect_debug_snapshot.sh
journalctl -u amneziya-agent -n 100 --no-pager
journalctl -u amneziya-web -n 100 --no-pager
tail -n 200 logs/app.log
```

Перед отправкой логов наружу проверить, что секреты отредактированы.

## 9. Быстрый rollback

```bash
sudo systemctl disable --now amneziya-agent
```

В `/opt/amn2/.env` вернуть:

```env
LOCAL_AGENT_ENABLED=false
LOCAL_AGENT_CONTROLLER_ENABLED=false
```

Перезапустить web:

```bash
sudo systemctl restart amneziya-web
ss -lntp | grep ':3031' || true
```

## 10. Go / no-go для следующего этапа

Перед решением заполнить `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`: commit, Runtime, Local Agent status,
Web admin status, Degraded reasons, Rollback checked и финальный Go / no-go.

Переходить к write API для пользователей можно только если:

- agent стабильно отвечает через localhost;
- web admin видит Local Agent без raw token;
- `degraded` понятен и документирован, если Docker/runtime доступ ограничен;
- rollback проверен;
- ветка опубликована в `barakov-dot/amn3` или есть другой воспроизводимый способ
  доставить тот же commit на VPS.
