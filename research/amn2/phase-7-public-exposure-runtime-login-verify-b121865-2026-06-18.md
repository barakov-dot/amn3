# AMN2 Phase 7 Public Exposure Runtime/Login Verification

Дата: 2026-06-18.

Gate: `P7-C002b` runtime reload and loopback login verification.

Статус: `runtime-login-verified-not-exposed`.

Target: disposable VPS `89.185.80.166`.

AMN2 source overlay:

```text
b121865f488821f6fc471c9529fb26e5d7992515
```

Связанные предыдущие evidence:

- `research/amn2/phase-7-public-exposure-gate-precutover-b121865-2026-06-14.md`
- `research/amn2/phase-7-public-exposure-admin-domain-prereq-b121865-2026-06-14.md`

## Operator Gate

Оператор открыл узкий live gate:

```text
Открываю P7-C002b runtime reload and loopback login verification gate для b121865 на текущем disposable VPS 89.185.80.166.
```

Разрешенная область:

- перечитать live `.env` через manual loopback runtime restart;
- проверить web login только через `127.0.0.1:3030`;
- проверить, что внешние public probes остаются закрытыми.

Запрещенная область:

- reverse proxy apply;
- TLS/certbot apply;
- firewall/listener public change;
- direct public `3030`/`3040` exposure;
- config delivery;
- write API / install mutation;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- Telegram action;
- secret-bearing evidence publication.

## Transcript Inputs

Локальные transcript-файлы:

```text
tmp/p7-c002b-runtime-reload-login-verify-20260614T183848Z.log
tmp/p7-c002b-runtime-recovery-check-20260614T184249Z.log
tmp/p7-c002b-login-only-verify-20260614T184512Z.log
tmp/p7-c002b-password-contract-check-20260614T184853Z.log
tmp/p7-c002b-login-divergence-check-20260618T051158Z.log
```

Пароли, password hash и session secret не включены в evidence.

## Initial Reload Attempt

`P7-C002b runtime reload and loopback login verification` перезапустил только
manual loopback runtime:

```text
runtime_reload_status=attempted
service_restart_performed=true
reverse_proxy_apply_performed=false
firewall_apply_performed=false
tls_apply_performed=false
public_listener_change_performed=false
```

После restart были видны процессы:

```text
166198 /opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
166199 /opt/amn2/venv/bin/python -m app.main
```

Первичная HTTP-проверка попала в короткое окно до bind web listener и вернула
`Connection refused`:

```text
web_root_loopback_http=000
web_login_loopback_http=000
ConnectionRefusedError: [Errno 111] Connection refused
```

Интерпретация: первичный fail был readiness/timing issue после restart, а не
доказательство падения web runtime.

## Recovery Check

Read-only recovery check показал, что runtime поднялся и слушает только
loopback:

```text
166198 /opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
166199 /opt/amn2/venv/bin/python -m app.main
LISTEN 0 2048 127.0.0.1:3030 0.0.0.0:* users:(("python",pid=166198,fd=6))
web_login_loopback_http=200
```

Safe settings check:

```text
settings_load_status=passed
web_admin_username_present=True
web_admin_password_hash_present=True
```

Local external probes remained closed:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Password Contract Check

Read-only password contract check showed that the operator-submitted username
and password matched the live `.env` contract:

```text
web_admin_username_present=True
web_admin_password_hash_present=True
submitted_username_matches_env=yes
submitted_password_matches_hash=yes
secret_values_printed=false
```

No restart, `.env` mutation, reverse proxy, TLS, firewall or public listener
change was performed.

## Final Live Login Flow

Final read-only divergence check on 2026-06-18 showed the live web flow passes:

```text
login_get_http=200
login_get_has_csrf=yes
login_get_set_cookie=yes
login_cookie_names=session
login_post_http=303
login_post_location=/
login_post_has_invalid_credentials=no
login_post_has_stale_form=no
login_post_set_cookie=yes
dashboard_after_login_http=200
dashboard_after_login_location=none
dashboard_after_login_has_login_form=no
secret_values_printed=false
```

Runtime/listener snapshot:

```text
166198 Sun Jun 14 11:39:53 2026 /opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
166199 Sun Jun 14 11:39:53 2026 /opt/amn2/venv/bin/python -m app.main
LISTEN 0 2048 127.0.0.1:3030 0.0.0.0:* users:(("python",pid=166198,fd=6))
```

Standalone `.env` contract check:

```text
settings_username_matches_submitted=yes
settings_password_matches_submitted=yes
settings_cookie_secure=True
secret_values_printed=false
```

External probes remained closed:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

Mutation status:

```text
service_restart_performed=false
env_mutation_performed=false
reverse_proxy_apply_performed=false
firewall_apply_performed=false
tls_apply_performed=false
public_listener_change_performed=false
```

## Verdict

`P7-C002b` закрыт как `runtime-login-verified-not-exposed`.

Итог:

- AMN2 source overlay remains `b121865f488821f6fc471c9529fb26e5d7992515`;
- admin/domain prerequisites from `P7-C002a` are present in `.env`;
- manual loopback runtime loaded the admin credential contract;
- loopback login succeeds;
- web remains bound to `127.0.0.1:3030`;
- external probes to `3030`, `3040`, `80` and `443` remain closed;
- no public exposure was applied.

`P7-C002` remains a critical named gate for any actual public cutover. The next
allowed public-exposure action is a separate exact named public cutover gate
covering reverse proxy/TLS/firewall/listener changes and rollback-to-loopback.
