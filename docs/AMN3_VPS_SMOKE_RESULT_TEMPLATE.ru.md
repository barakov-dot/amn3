# AMN3 VPS Smoke Result Template

Шаблон заполняется после реальной проверки AMN3 Local Agent на VPS. Он нужен, чтобы решение о переходе к
`agent:clients:write` было основано на фактах: commit, runtime, состояние Local Agent, web admin, причины `degraded`,
rollback и отсутствие утечек секретов.

Не вставлять сюда raw token, приватные ключи, PSK, QR, `vpn://`, реальные client configs, содержимое `.env` целиком
или неотредактированные логи.

## 1. Metadata

```text
Date / time:
Operator:
VPS host alias:
Repository: https://github.com/barakov-dot/amn3.git
Branch: codex/local-agent-production-wiring
Commit:
Runtime path: /opt/amn2
Runtime: docker | host_systemd
Amneziya interface:
Container or systemd service:
```

## 2. Git / deploy evidence

Команды, которые должны быть выполнены на VPS:

```bash
cd /opt/amn2
git status --short --branch
git log -1 --oneline --decorate
git remote -v
./venv/bin/python -m pip show amn2
```

Результат:

```text
Commit observed:
Working tree state:
Python package editable install checked: yes | no
Unexpected files or local changes:
```

## 3. Local Agent status

Команды:

```bash
sudo systemctl status amneziya-agent --no-pager
ss -lntp | grep ':3031'
read -rsp "Local Agent raw token: " LOCAL_AGENT_RAW_TOKEN; echo
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/health
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/runtime
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN" http://127.0.0.1:3031/agent/protocols
unset LOCAL_AGENT_RAW_TOKEN
python -m app.cli agent probe --base-url http://127.0.0.1:3031
```

Заполнить:

```text
Local Agent status: online | degraded | offline | unknown
Bind check: 127.0.0.1:3031 only | other
/agent/health result:
/agent/runtime result:
/agent/protocols result:
CLI probe result:
Secret leakage observed: no | yes
```

## 4. Web admin status

Команды и ручная проверка:

```bash
curl -i http://127.0.0.1:3030/login
journalctl -u amneziya-web -n 100 --no-pager
```

В web admin открыть карточку сервера и заполнить:

```text
Web admin status: online | degraded | offline | unknown | disabled
Login endpoint reachable: yes | no
Local Agent block visible: yes | no
Base URL shown:
Runtime shown:
Protocols shown:
raw token displayed in UI: no | yes
```

## 5. Diagnostics and logs

Команды:

```bash
cd /opt/amn2
bash deploy/runtime/collect_debug_snapshot.sh
journalctl -u amneziya-agent -n 100 --no-pager
journalctl -u amneziya-web -n 100 --no-pager
tail -n 200 logs/app.log
```

Перед переносом результата в issue, чат или commit message отредактировать секреты и пути, которые раскрывают лишнее.

```text
Snapshot collected: yes | no
Logs redacted before sharing: yes | no
Errors in amneziya-agent:
Errors in amneziya-web:
Errors in app.log:
```

## 6. Degraded reasons

Если Local Agent или web admin показывает `degraded`, указать понятную причину:

```text
Degraded reasons:
- Docker socket access:
- awg command / awg dump:
- Runtime config mismatch:
- Token path / permissions:
- Controller disabled or token unreadable:
- Unknown:
```

Если причина неизвестна, это `no-go` для write API.

## 7. Security assertions

```text
raw token absent from .env: yes | no
raw token absent from logs/docs/issues: yes | no
Public 3031 port closed: yes | no
Local Agent bind is localhost only: yes | no
Write routes enabled: no | yes
LOCAL_AGENT_WRITE_ENABLED absent or false: yes | no
Private key / PSK / QR / vpn:// absent from /agent/protocols: yes | no
```

Проверочные команды:

```bash
grep -n 'LOCAL_AGENT' /opt/amn2/.env
ss -lntp | grep ':3031'
```

## 8. Rollback checked

Rollback должен быть проверен хотя бы один раз на тестовом окне, до перехода к write API.

```bash
sudo systemctl disable --now amneziya-agent
ss -lntp | grep ':3031' || true
sudo systemctl restart amneziya-web
```

Заполнить:

```text
Rollback checked: yes | no
Agent disabled cleanly:
Port 3031 closed after rollback:
Web admin survives rollback:
Env flags restored:
```

## 9. Go / no-go

```text
Go / no-go for agent:clients:write design:
Decision: go | no-go
Reason:
Required follow-ups before mutation endpoints:
Owner:
```

`go` возможен только если read-only smoke зеленый, rollback проверен, `degraded` отсутствует или объяснен, публичного
доступа к Local Agent нет, raw token не утек, а write routes все еще выключены.

`no-go` обязателен, если agent недоступен, порт `3031` слушает публично, raw token попал в `.env`/логи/UI, Docker access
непонятен, `/agent/protocols` раскрывает секреты или причина `degraded` не установлена.
