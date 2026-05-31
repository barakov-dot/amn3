# Local Agent VPS smoke runbook

Цель этого runbook - быстро и безопасно проверить Local Agent на реальном VPS
Amneziya без открытия публичного API и без write operations.

## 0. Предусловия

- Проект уже лежит на VPS в `/opt/amn2`.
- Python environment проекта готов или может быть создан в `/opt/amn2/venv`.
- Файл `/opt/amn2/.env` существует или будет создан из `.env.example`.
- `servers.yml` описывает реальный runtime: `host_systemd` или `docker`.
- Agent не публикуется наружу: `LOCAL_AGENT_HOST=127.0.0.1`.

## 1. Проверить код и зависимости

```bash
cd /opt/amn2
git status --short
git log -1 --oneline --decorate
test -d venv || python3 -m venv venv
./venv/bin/python -m pip install -e .
test -f .env || cp .env.example .env
```

Если branch с Local Agent еще не перенесен на VPS, сначала доставить код тем
же способом, которым проект обычно обновляется. Не менять production `.env`
вслепую и не перетирать существующий `servers.yml`.

## 2. Создать raw token и hash

Сгенерировать raw token:

```bash
./venv/bin/python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Сохранить raw token в password manager. В `.env` его не записывать.

Сгенерировать hash интерактивно, чтобы raw token не попал в shell history:

```bash
./venv/bin/python -m app.cli agent hash-token
```

Вставить raw token два раза. Команда напечатает значение вида:

```text
sha256:<generated-hash>
```

## 3. Включить Local Agent в `.env`

В `/opt/amn2/.env` должны быть такие значения:

```env
LOCAL_AGENT_ENABLED=true
LOCAL_AGENT_HOST=127.0.0.1
LOCAL_AGENT_PORT=3031
LOCAL_AGENT_TOKEN_ID=local-controller
LOCAL_AGENT_TOKEN_HASH=sha256:<generated-hash>
LOCAL_AGENT_TOKEN_OWNER=local-controller
LOCAL_AGENT_TOKEN_SCOPES=agent:health,agent:read,agent:protocols:read
LOCAL_AGENT_TOKEN_EXPIRES_AT=
```

Проверить, что raw token не записан в `.env`:

```bash
grep -n 'LOCAL_AGENT' .env
```

## 4. Быстрый ручной запуск

Перед systemd можно запустить agent вручную:

```bash
./venv/bin/python -m app.cli agent serve --host 127.0.0.1 --port 3031
```

Во втором SSH-сеансе выполнить smoke-запросы:

```bash
read -rsp "Local Agent raw token: " LOCAL_AGENT_RAW_TOKEN; echo
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/health
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/runtime
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/protocols
unset LOCAL_AGENT_RAW_TOKEN
```

Или через штатный read-only controller client:

```bash
./venv/bin/python -m app.cli agent probe --base-url http://127.0.0.1:3031
```

Команда попросит raw token интерактивно и не требует передавать его через shell
history.

Успешный минимум:

- `/agent/health` отвечает `ok`;
- `/agent/runtime` возвращает `running`, `stopped`, `degraded` или `unknown`;
- `/agent/protocols` не содержит private keys, PSK, QR, `vpn://` и client configs.

Если Docker недоступен или `awg dump` не читается, ожидаемый статус - `degraded`,
а не `stopped`.

## 5. Установка systemd service

```bash
sudo install -m 0644 deploy/systemd/amneziya-agent.service.example /etc/systemd/system/amneziya-agent.service
sudo systemctl daemon-reload
sudo systemctl enable --now amneziya-agent
sudo systemctl status amneziya-agent --no-pager
```

Проверить, что agent слушает только localhost:

```bash
ss -lntp | grep ':3031'
```

Если используется Docker runtime, сначала проверить доступ пользователя
`amneziya` к Docker socket. Только после этого раскомментировать
`SupplementaryGroups=docker` в `/etc/systemd/system/amneziya-agent.service`,
выполнить `sudo systemctl daemon-reload` и `sudo systemctl restart amneziya-agent`.

## 6. Smoke после systemd

```bash
read -rsp "Local Agent raw token: " LOCAL_AGENT_RAW_TOKEN; echo
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/health
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/runtime
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/protocols
unset LOCAL_AGENT_RAW_TOKEN
```

Собрать диагностический snapshot:

```bash
bash deploy/runtime/collect_debug_snapshot.sh
```

## 7. Проверка с рабочей машины через SSH tunnel

На рабочей машине:

```bash
ssh -N -L 3031:127.0.0.1:3031 amneziya@VPS_HOST
```

В другом локальном терминале:

```bash
read -rsp "Local Agent raw token: " LOCAL_AGENT_RAW_TOKEN; echo
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/health
unset LOCAL_AGENT_RAW_TOKEN
```

Или:

```bash
python -m app.cli agent probe --base-url http://127.0.0.1:3031
```

Порт `3031` на firewall VPS не открывать. Для первого production режима доступ
только через localhost, SSH tunnel или будущий controller-side transport.

## 8. Быстрый rollback

Отключить service:

```bash
sudo systemctl disable --now amneziya-agent
```

В `.env` вернуть:

```env
LOCAL_AGENT_ENABLED=false
```

Затем проверить, что порт закрыт:

```bash
ss -lntp | grep ':3031' || true
```

## 9. Что не делаем в smoke

- Не открываем bind на внешний адрес.
- Не добавляем write/config/backup routes.
- Не сохраняем raw token в `.env`, docs, issue, chat или shell history.
- Не включаем Docker access без отдельной проверки пользователя `amneziya`.
- Не считаем `degraded` ошибкой API; это сигнал, что runtime надо разобрать отдельно.
