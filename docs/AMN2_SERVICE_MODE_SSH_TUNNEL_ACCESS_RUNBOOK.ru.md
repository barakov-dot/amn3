# AMN2 Service-Mode SSH Tunnel Access Runbook

Дата: 2026-06-09.

Назначение: безопасно открыть web/admin панель service-mode без домена и без публичного reverse proxy. Доступ выполняется через SSH local port forward на `127.0.0.1:3030`.

Этот runbook не открывает public API `3040`, не открывает прямой public web/admin `3030`, не включает HTTPS reverse proxy, не выполняет production peer/user writes, не включает public/self-service config delivery и не разрешает Local Agent mutations.

## Preconditions

Ожидаемое состояние перед tunnel-доступом:

```text
amneziya-web: enabled/active
amneziya-bot: enabled/active
web bind: 127.0.0.1:3030
web /login loopback: 200
tcp_3030: present-loopback
tcp_3040: absent
reverse proxy: not installed / not changed
public HTTPS cutover: deferred until a domain exists
```

## VPS Baseline Check

На VPS перед tunnel-сессией:

```bash
cd /opt/amn2

echo "phase3_no_domain_tunnel_baseline=started"

if sudo grep -q '^VPS_APPLY_ENABLED=' /opt/amn2/.env; then
  sudo sed -i 's/^VPS_APPLY_ENABLED=.*/VPS_APPLY_ENABLED=false/' /opt/amn2/.env
else
  printf '\nVPS_APPLY_ENABLED=false\n' | sudo tee -a /opt/amn2/.env >/dev/null
fi

sudo chgrp amneziya /opt/amn2/.env
sudo chmod 0640 /opt/amn2/.env

echo "VPS_APPLY_ENABLED_file_false: $(sudo grep -q '^VPS_APPLY_ENABLED=false$' /opt/amn2/.env && echo yes || echo no)"
echo "amneziya-web_active: $(systemctl is-active amneziya-web 2>/dev/null || true)"
echo "amneziya-bot_active: $(systemctl is-active amneziya-bot 2>/dev/null || true)"
echo "web_login_loopback_http: $(curl -sS -o /dev/null -w '%{http_code}' http://127.0.0.1:3030/login 2>/dev/null || echo curl-failed)"
echo "tcp_3030_loopback: $(ss -ltnH '( sport = :3030 )' 2>/dev/null | grep -q '127.0.0.1:3030' && echo yes || echo no)"
echo "tcp_3040_absent: $(ss -ltnH '( sport = :3040 )' 2>/dev/null | grep -q . && echo no || echo yes)"
echo "phase3_no_domain_tunnel_baseline=done"
```

Публиковать raw `.env`, токены, hashes, ключи, endpoint values или полные логи нельзя.

## PowerShell Tunnel

В отдельном PowerShell-окне на компьютере оператора:

```powershell
ssh -N -L 127.0.0.1:3030:127.0.0.1:3030 root@ТВОЙ_VPS_IP
```

Окно должно оставаться открытым, пока нужна панель. Закрытие окна или `Ctrl+C` останавливает tunnel.

Если локальный порт `3030` занят:

```powershell
ssh -N -L 127.0.0.1:13030:127.0.0.1:3030 root@ТВОЙ_VPS_IP
```

## Browser

Открывать обычный внешний браузер, не Codex preview:

```powershell
Start-Process "http://127.0.0.1:3030/login"
```

Если использовался запасной локальный порт:

```powershell
Start-Process "http://127.0.0.1:13030/login"
```

## Troubleshooting

```text
bind: Address already in use
```

Локальный порт занят. Использовать вариант с `13030`.

```text
channel ... open failed: connect failed
```

Туннель поднялся, но remote web на `127.0.0.1:3030` недоступен. Проверить `amneziya-web` и loopback `/login` на VPS.

```text
Страница не открывается в Codex preview
```

Это не blocker. Открывать URL в обычном браузере через `Start-Process` или вручную в адресной строке.

## Exit State

После tunnel-доступа ожидаем:

```text
reverse_proxy_changed: no
public_https_cutover: no
tcp_3030_remote: present-loopback
tcp_3040_remote: absent
VPS_APPLY_ENABLED_file_false: yes
```
