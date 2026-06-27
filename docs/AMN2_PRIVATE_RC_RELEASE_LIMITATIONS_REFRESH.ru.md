# PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH

Дата: 2026-06-27.

Статус: `completed-docs-only`.

Использованы существующие Phase 8 evidence, `PRIVATE_RC_FINAL_ANDROID_SUMMARY`,
результаты third-party Android handoff/manual/server-side observation и
`PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_RESULT`.

Live/VPS/config/Telegram/public gates не открывались.

## Итог refresh

```text
release_limitations_refresh_status=completed-docs-only
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
android_private_operator_rc_proof=complete-with-explicit-limitations
telegram_private_operator_rc_proof=passed-private-operator-no-config-delivery
public_launch_status=not-approved
public_exposure_status=closed-by-default
telegram_live_config_delivery_status=not-approved
config_delivery_status=not-approved
peer_creation_status=not-approved
production_rollout_status=not-approved
next_action_requires_exact_named_gate=true
hold_status=active
```

Формулировка private/operator RC после refresh:

```text
AMN2 готов к закрытому private/operator RC с явными ограничениями.
Android proof внутри private/operator RC усилен: P8-C001 Android phone,
P8-C003 Android projector fresh-zero limitation, и third-party Android phone
manual + server-side proof.
Public launch, public exposure, Telegram live config delivery,
public/self-service config delivery и broader rollout не approved.
Telegram private/operator `/start` operation доказан отдельно через
no-long-SSH retry без config delivery и без публичной экспозиции.
```

## Что изменилось относительно RC package от 2026-06-22

Обновлена формулировка Android confidence, Telegram private/operator operation
proof и ограничений.

Было:

```text
fresh_android_phone_acceptance_source=P8-C001
fresh_zero_android_acceptance_device=P8-C003_android_projector
```

Теперь:

```text
fresh_android_phone_acceptance_source=P8-C001
fresh_zero_android_acceptance_device=P8-C003_android_projector
third_party_android_phone_proof=passed-manual-and-server-side
android_private_operator_rc_proof=complete-with-explicit-limitations
telegram_private_operator_rc_proof=passed-private-operator-no-config-delivery
```

`P8-C003` по-прежнему нельзя выдавать за Android phone evidence. Это projector
evidence. Новое third-party Android phone evidence закрывает дополнительную
практическую проверку phone `.conf` handoff/import/connect/traffic.

## Android proof после refresh

```text
p8_c001_android_phone_status=passed
p8_c001_fresh_peer_public_key_fp=594ba96e4f90
p8_c003_android_projector_status=passed-with-projector-limitation
p8_c003_fresh_peer_public_key_fp=d0ab128d6801
third_party_android_phone_status=passed-manual-and-server-side
third_party_android_fresh_peer_public_key_fp=49e456e4edcb
third_party_android_latest_handshake_age_s=23
third_party_android_endpoint_observed=yes
third_party_android_transfer_rx_bytes=55600508
third_party_android_transfer_tx_bytes=132476207
```

## Telegram proof после refresh

```text
telegram_no_long_ssh_retry_status=passed
telegram_get_me_status=passed
bot_identity_safe=@NeobyatnayaAMNZ_bot
bot_polling_started=true
ssh_session_open_during_manual_window=false
operator_start_flow_observed=passed
partner_start_flow_observed=passed
config_delivery_attempted=false
remaining_amn2_app_main_polling_process_count=0
final_no_polling_guard_status=passed
telegram_real_operation_status=passed-private-operator-no-config-delivery
```

## Ограничения, которые НЕ сняты

```text
public_launch_status=not-approved
public_web_admin_api_status=not-approved
public_exposure_status=closed-by-default
telegram_live_send_status=not-approved
telegram_bot_polling_status=not-approved-as-persistent-mode
telegram_live_config_delivery_status=not-approved
public_self_service_config_delivery_status=not-approved
config_generation_without_exact_gate=not-approved
new_peer_creation_without_exact_gate=not-approved
qr_release_primary=false
full_vpn_uri_release_primary=false
ios_defaultvpn_status=experimental_unreliable
restore_import_status=not-proven
provider_rebuild_status=not-proven
production_scale_rollout_status=not-approved
```

## Разрешенный private/operator RC scope после refresh

Разрешено считать готовым:

- закрытый private/operator RC;
- private/operator web/admin без public exposure;
- `.conf`-first private handoff внутри явно открытых gates;
- Android AmneziaWG как основной мобильный кандидат внутри RC;
- private/operator Telegram `/start` flow без config delivery;
- AMN2 `187949b` как текущая RC runtime/package line;
- Telegram `getMe` и controlled private preview evidence как уже доказанные
  ограниченные проверки;
- backup create+verify как доказанный режим сохранения текущего состояния;
- docs/operator coordination без live gates.

Не разрешено этим refresh:

- public launch;
- public web/admin/API;
- Telegram live config delivery;
- bot polling как постоянный режим;
- Telegram profile/media mutation;
- public/self-service config delivery;
- создание новых peer/config без exact gate;
- restore/import;
- provider rebuild;
- production-scale rollout.

## Stop-lines

Без нового exact named gate нельзя:

- выполнять live VPS/SSH command;
- выполнять package upload/apply;
- запускать, останавливать или перезапускать сервисы;
- открывать public exposure;
- менять firewall/listener/TLS/reverse proxy/Cloudflare/ngrok;
- создавать peer/config;
- доставлять config;
- выводить `.conf`, QR, `vpn://`, private key, PSK, token/password;
- запускать Telegram polling/live send;
- менять Telegram profile/media;
- выполнять restore/import/reboot;
- выполнять provider rebuild;
- начинать broader rollout.

## Обновленные документы

```text
docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_FINAL_PACKAGE.ru.md
docs/AMN2_PRIVATE_RC_FINAL_ANDROID_SUMMARY.ru.md
docs/AMN2_PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_RESULT.ru.md
docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md
docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md
docs/NEXT_CHAT_AMN2_PRIVATE_RC_SESSION_0.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
```

## Hold

После refresh AMN2 снова остается в режиме ожидания:

```text
hold_gate=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
hold_status=active
next_action_requires_exact_named_gate=true
recommended_next_step=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```
