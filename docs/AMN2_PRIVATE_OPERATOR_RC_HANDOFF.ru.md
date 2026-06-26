# AMN2 private/operator RC handoff

Дата: 2026-06-22.

Статус:

```text
phase8_final_status=launch-ready-with-explicit-limitations
release_limitations_refresh_status=completed-2026-06-26
private_operator_rc_launch_ready=true
public_launch_status=not-approved
blocked_with_exact_remaining_blockers=false
```

Это операторская памятка для частного RC. Она использует только уже
зафиксированные Phase 8 evidence и не открывает live/destructive/config/
Telegram send/public exposure gates.

## Короткий вывод

AMN2 можно считать готовым к private/operator RC с явными ограничениями.

Готовность доказана для закрытого операторского контура:

- пользователи обслуживаются через Telegram-first продуктовую логику;
- операторский web/admin остается приватным, без публичной экспозиции;
- основной мобильный артефакт доставки - приватный `.conf`;
- Android AmneziaWG принят как рабочий мобильный кандидат внутри private/
  operator RC: P8-C001 Android phone, P8-C003 Android projector limitation и
  third-party Android phone manual + server-side proof;
- свежий запуск AMN2 на disposable VPS воспроизведен;
- backup create+verify доказан;
- public probes остались закрыты.

Это не разрешение на публичный запуск, массовую рассылку, публичный web/admin,
публичный API, restore/import, provider rebuild или production-scale rollout.

## Основание решения

### P8-C001

Fresh Android phone acceptance прошел.

Evidence:

```text
research/amn2/phase-8-p8-c001-fresh-android-config-acceptance-2026-06-21.md
```

Ключевой смысл: fresh per-device Android AmneziaWG `.conf` импортировался,
подключился и дал трафик на Android phone. Это отдельное доказательство
Android phone acceptance.

### P8-C002

Current-head package smoke прошел для AMN2 `187949b`.

Evidence:

```text
research/amn2/phase-8-p8-c002-187949b-package-apply-smoke-2026-06-21.md
```

Ключевой смысл: пакет `187949b` прошел package/apply smoke, loopback web/API,
Telegram `getMe` плюс non-polling bot surface, backup create+verify и closed
public probes. Android-compatible AWG defaults закреплены в штатном runtime/
package path.

### P8-C003

Fresh-from-zero VPS rehearsal прошел.

Evidence:

```text
research/amn2/phase-8-p8-c003-fresh-zero-rehearsal-2026-06-22.md
```

Ключевой смысл: свежий `/opt/amn2` runtime был воспроизведен на disposable VPS
`89.185.80.166`, AMN2 `187949b` применен, свежий env/DB поднят, два Telegram
bot admin подтверждены, loopback web/API и Telegram server-side smoke прошли,
backup create+verify прошел, fresh Android projector config дал handshake и
рост счетчиков.

### P8-SFINAL

Launch readiness freeze завершен.

Evidence:

```text
research/amn2/phase-8-sfinal-launch-readiness-freeze-2026-06-22.md
```

Финальный статус:

```text
launch-ready-with-explicit-limitations
```

### Android proof refresh 2026-06-26

Evidence:

```text
research/amn2/phase-8-private-rc-final-android-summary-2026-06-26.md
research/amn2/phase-8-third-party-android-traffic-observation-result-2026-06-26.md
research/amn2/phase-8-private-rc-release-limitations-refresh-2026-06-26.md
```

Ключевой смысл: Android private/operator RC proof теперь включает P8-C001
Android phone, P8-C003 Android projector с явным projector limitation и
third-party Android phone, у которого manual owner report и server-side
handshake/endpoint/rx-tx observation прошли.

## Разрешенный private/operator RC scope

Разрешено считать готовым:

- закрытый private/operator RC;
- Telegram-first продуктовый контур как основной пользовательский канал;
- операторский web/admin только приватно, без публичной экспозиции;
- `.conf`-first приватная передача конфигураций;
- Android AmneziaWG как основной мобильный кандидат;
- текущий AMN2 head `187949b` как RC runtime/package line;
- backup create+verify как доказанный режим сохранения текущего состояния.

Разрешено использовать как evidence:

- P8-C001 для Android phone acceptance;
- P8-C002 для current-head package/runtime smoke;
- P8-C003 для fresh-from-zero reproducibility;
- P8-SFINAL для финального launch readiness verdict.

## Явные ограничения

1. Public launch не approved.
2. Public web/admin/API exposure не approved.
3. Telegram live send, bot polling, profile/media mutation не выполнялись и не
   approved.
4. P8-C003 Android acceptance был на Android projector. Android phone
   acceptance остается отдельным P8-C001 evidence. Third-party Android phone
   proof дополнительно прошел manual + server-side observation, но не заменяет
   P8-C003 fresh-zero limitation.
5. QR и полный `vpn://` не являются release-primary delivery path.
6. `.conf` является release-primary handoff artifact, но содержимое `.conf`
   нельзя публиковать в чат/evidence.
7. iOS DefaultVPN остается experimental/unreliable.
8. Windows desktop принят операторским наблюдением, не свежим автоматическим
   device gate.
9. Backup create+verify доказан; restore/import DR не доказан.
10. Provider rebuild, reboot, firewall/listener changes, Cloudflare, ngrok,
    reverse proxy, TLS publication и production-scale rollout не approved.

## Стоп-линии

Без нового exact named gate не выполнять:

- VPS/provider destructive action;
- public exposure, Cloudflare, ngrok, reverse proxy, TLS, firewall/listener
  changes;
- Telegram live send/profile/media mutation или bot polling;
- `.conf`, QR, `vpn://`, private key, PSK, token, password output;
- backup restore/import/reboot;
- production peer/user mutation;
- provider rebuild;
- broader rollout.

## Следующие exact gates, если нужен более широкий запуск

### Public exposure gate

Открывать только если нужен публичный web/admin/API, домен, TLS, reverse proxy,
Cloudflare/ngrok или firewall/listener changes.

Обязательные условия:

- точный target hostname/domain;
- TLS/public URL policy;
- rollback/close plan;
- external probes до/после;
- отдельное подтверждение риска.

### Telegram live delivery gate

Открывать только если нужно реальное Telegram live send, bot polling,
profile/media mutation или пользовательская рассылка.

Обязательные условия:

- точный bot token source без вывода токена;
- target users/admins;
- что именно отправляется;
- запрет payload output в evidence;
- rollback/stop criteria.

### Config delivery gate

Открывать только если нужно создать/выдать новый production config пользователю
или устройству.

Обязательные условия:

- exact target user/device;
- private handoff destination outside workspace;
- one-time/revocation policy;
- no `.conf`/QR/`vpn://`/keys/PSK output in chat/evidence.

### Restore/import DR gate

Открывать только если нужно доказать restore/import.

Обязательные условия:

- exact backup artifact;
- restore target;
- rollback plan;
- no production overwrite without explicit destructive confirmation.

### Production rollout gate

Открывать только если частный RC превращается в более широкий rollout.

Обязательные условия:

- список target users/devices;
- delivery channel;
- peer/user mutation limits;
- support/rollback plan;
- evidence policy.

## Операторская короткая памятка

Можно говорить:

```text
AMN2 готов к private/operator RC с явными ограничениями.
```

Нельзя говорить:

```text
AMN2 готов к публичному запуску без ограничений.
```

Главная безопасная формулировка:

```text
Private/operator RC launch-ready with explicit limitations:
public exposure closed by default, Telegram live send not performed, `.conf`
is release-primary private handoff, Android phone acceptance is P8-C001,
fresh-zero rehearsal used Android projector in P8-C003, third-party Android
phone manual + server-side proof passed, restore/import is not proven.
```

## Следующее рекомендуемое действие

```text
P8-RC-OPERATOR-RUN-CHECKLIST

Use existing Phase 8 evidence only.
Do not open live/destructive/config/Telegram send/public exposure gates.
Prepare the operator run checklist for private/operator RC:
- what to check before operating;
- how to keep public exposure closed;
- where private handoff artifacts live;
- what exact gates are required for any broader action.
```
