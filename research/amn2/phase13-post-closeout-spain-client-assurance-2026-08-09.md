# Phase 13 Post-Closeout Spain Client Assurance — 2026-08-09

Статус: `PASS_WITH_PERFORMANCE_WARNING`.

## Принятый scope

- `PHASE13_FORMALLY_SEALED=true`
- `USA_REINSTALL_READY=true`
- `PHASE14_NOT_STARTED=true`
- `AWG3_PHASE=14`
- `LIVE_MUTATION=false`
- `RAW_CONFIG_PERSISTED=false`
- `RAW_SECRET_PERSISTED=false`
- `RAW_REMOTE_LOG_PERSISTED=false`

Проверялся только уже выданный accepted ARM-HOME operator profile на Spain.
Новые config, peer, QR, VPN payload, key и server mutation не создавались.
MTU `1280` не устранил симптом и не является accepted profile; оператор
сохраняет исходный accepted profile.

## Operator и local evidence

Оператор подтвердил, что Telegram и сайты фактически работают через Spain.

Secret-safe local read-only checks подтвердили:

- `TUNNEL_ROUTE_DNS_STABLE=true`;
- `WINDOWS_PROXY_DISABLED=true`;
- `REALISTIC_15_SECOND_SITE_CHECKS=6_OF_6`;
- `REALISTIC_15_SECOND_TELEGRAM_CHECKS=6_OF_6`;
- `TELEGRAM_MAX_CONNECT_SECONDS_APPROX=7.3`;
- `TELEGRAM_MAX_TTFB_SECONDS_APPROX=9.2`;
- `SUSTAINED_TRANSFER_BYTES=2097152`;
- `SUSTAINED_TRANSFER_COMPLETED=true`;
- `SUSTAINED_TRANSFER_DURATION_SECONDS_APPROX=8.9`;
- `SUSTAINED_TRANSFER_SPEED_KIB_PER_SECOND_APPROX=231`.

Короткие `2.5–5` second probes могут ложно классифицировать медленное
установление соединения как failure. Оператор наблюдал периодические задержки
открытия и краткие Codex reconnect, но tunnel drop не доказан. Это
`PERFORMANCE_WARNING`, а не Phase 13 blocker.

## Negative controls

- SSH, config generation/delivery, peer creation, package build, deploy,
  service action и client settings mutation не выполнялись;
- AWG не останавливался, не перезапускался, не пересоздавался и не обновлялся;
- Spain D1–D7, configs, keys, firewall/forward rules и foreign service не
  изменялись;
- USA shutdown, cleanup, reuse и provider mutation не выполнялись;
- config content, config SHA, private key, PSK, endpoint, address, target
  identifier и raw log не сохранялись и не выводились.

## Решение

Phase 13 не переоткрывается. Наблюдение о connection latency/reconnect
переносится в Phase 14 как non-blocking read-only diagnostic candidate. Оно не
разрешает новый MTU/config/peer/server change без отдельно доказанного root
cause и не блокирует отдельный Phase 14 start gate.
