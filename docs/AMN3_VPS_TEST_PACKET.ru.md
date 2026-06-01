# AMN3 VPS Test Packet

Пакет для соседнего чата `Переводим AMN на API`, где готовится тест на реальном VPS. Его задача - дать короткий
copy/paste-safe маршрут, который синхронизирован с текущей веткой AMN3 и возвращает сюда пригодный результат.

Основные документы:

- `docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md` - полный порядок smoke.
- `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md` - форма результата и Go / no-go.
- `docs/LOCAL_AGENT_VPS_SMOKE_RUNBOOK.ru.md` - расширенный runbook, если короткий checklist недостаточен.
- `docs/superpowers/plans/2026-06-01-first-vps-mutation-test.ru.md` - отдельный packet для первого
  test-only apply/revoke после `GO-1` и Phase 1-4.

## 1. Что тестируем

```text
Repository: https://github.com/barakov-dot/amn3.git
Branch: codex/local-agent-production-wiring
Runtime path on VPS: /opt/amn2
Mode: read-only Local Agent smoke
Write API: disabled
LOCAL_AGENT_WRITE_ENABLED=false
```

Проверяем только read-only поверхность:

- `/agent/health`;
- `/agent/runtime`;
- `/agent/protocols`;
- `python -m app.cli agent probe --base-url http://127.0.0.1:3031`;
- web admin block `Local Agent`;
- diagnostics snapshot;
- rollback.

`/agent/clients*` write routes не включать, не тестировать как mutation endpoints и не открывать наружу.

## 2. Команды доставки ветки на VPS

На VPS:

```bash
cd /opt/amn2
git remote -v
git fetch origin codex/local-agent-production-wiring
git switch codex/local-agent-production-wiring
git pull --ff-only origin codex/local-agent-production-wiring
git log -1 --oneline --decorate
```

Ожидание: `git log -1 --oneline --decorate` показывает последний commit из ветки
`codex/local-agent-production-wiring`, запушенной в `https://github.com/barakov-dot/amn3.git`.

После pull:

```bash
test -d venv || python3 -m venv venv
./venv/bin/python -m pip install -U pip
./venv/bin/python -m pip install -e .
```

## 3. Минимальный smoke sequence

Использовать полный маршрут из `docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md`. Короткая последовательность:

```bash
cd /opt/amn2
sudo systemctl status amneziya-agent --no-pager || true
ss -lntp | grep ':3031' || true
python -m app.cli agent probe --base-url http://127.0.0.1:3031
curl -i http://127.0.0.1:3030/login
bash deploy/runtime/collect_debug_snapshot.sh
journalctl -u amneziya-agent -n 100 --no-pager
journalctl -u amneziya-web -n 100 --no-pager
tail -n 200 logs/app.log
```

Если agent еще не установлен как systemd service, пройти sections 3-6 из
`docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md`.

## 4. Секреты и redaction

В соседний чат и обратно сюда нельзя присылать:

- raw token;
- private key;
- PSK;
- QR;
- `vpn://`;
- full client config;
- содержимое `.env` целиком;
- неотредактированные логи.

Можно присылать:

- commit hash;
- runtime type: `docker` или `host_systemd`;
- status: `online`, `degraded`, `offline`, `unknown`;
- redacted diagnostics;
- факт, что public `3031` закрыт;
- факт, что write routes выключены;
- заполненный safe summary из section 6 ниже.

## 5. Что вернуть в этот чат

После smoke заполнить `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md` или прислать безопасный summary:

```text
Commit observed:
Runtime path: /opt/amn2
Runtime type: docker | host_systemd
Local Agent status:
Bind check: 127.0.0.1:3031 only | other
Web admin Local Agent block: visible | missing
Degraded reasons:
Diagnostics collected: yes | no
Rollback checked: yes | no
raw token leakage observed: no | yes
private key / PSK / QR / vpn:// leakage observed: no | yes
write routes enabled: no | yes
Go / no-go for agent:clients:write design:
Required follow-ups:
```

`Go / no-go` должен быть `no-go`, если Local Agent недоступен, порт `3031` слушает публично, raw token попал в UI/logs,
`/agent/protocols` раскрывает private key, PSK, QR или `vpn://`, причина `degraded` неизвестна, rollback не проверен,
или write routes оказались включены.

## 6. Решение после smoke

Если результат `go`, следующий шаг - не сразу включать весь write API, а открыть первый узкий implementation slice:

- feature flag `LOCAL_AGENT_WRITE_ENABLED`;
- отдельный token scope `agent:clients:write`;
- route registration только для согласованных `/agent/clients*`;
- audit storage;
- dry-run/preflight/confirmation gate;
- tests на запрет secret leakage и read-only token bypass.

После реализации Phase 1-4 первый реальный mutation test выполнять только по
`docs/superpowers/plans/2026-06-01-first-vps-mutation-test.ru.md`.

Если результат `no-go`, сначала исправлять runtime/deploy проблему и повторять этот packet. Не переходить к mutation
endpoints до зеленого read-only VPS smoke.
