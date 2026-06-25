# THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE_REVIEW

Дата: 2026-06-25.

Статус: `completed-docs-only`.

Использованы только существующие Phase 8 evidence, результат
`PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_GATE` и результат
`PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE_RETRY`.

Live/VPS/config/Telegram/public gates не открывались.

## 1. Итог review

```text
review_go=true
gate_open_go=conditional-go-when-third-party-android-phone-is-available
gate_name=THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
handoff_model=recommended_operator_mediated_private_conf_handoff
third_party_telegram_id_required=no_for_handoff_yes_only_if_order_identity_is_required_by_execution_helper
fresh_peer_limit=1
public_launch_status=not-approved
config_payload_output_allowed=false
```

GO условный: execution gate можно открывать только когда сторонний Android
телефон физически доступен и владелец телефона готов импортировать `.conf`,
включить AmneziaWG и дать безопасный результат проверки. Если телефона нет,
правильный статус: `wait-for-device`.

## 2. Target VPS и runtime baseline

Target VPS:

```text
target_vps=89.185.80.166
```

Ожидаемый AMN2 runtime/source head:

```text
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
```

Актуальные предпосылки из существующего evidence:

```text
ssh_transport_status=passed-small-read-only-commands
source_overlay_match=yes
db_runtime_status=passed-db-path-classified-with-aggregate-limitation
settings_database_resolved_path=/opt/amn2/data/amneziya.sqlite3
settings_database_exists=true
public_closed_probe_status=passed-in-last-read-only-gates
phase8_final_status=launch-ready-with-explicit-limitations
```

Ограничение DB/runtime retry остается только по aggregate counts: helper дважды
сломался на shell/SQL quoting, но DB path и DB file presence классифицированы.
Это не блокирует fresh Android handoff, если execution gate не требует DB row
dump/download и работает через штатный AMN2 runtime path.

## 3. Third-party Android boundary

Сторонний человек в этом gate:

- не становится админом;
- не получает Telegram/admin/runtime credentials;
- получает только один приватный `.conf` для своего Android устройства;
- не получает QR, `vpn://`, private key, PSK, token или пароль в чате/evidence;
- не участвует в public launch или broader rollout;
- сообщает только безопасный manual result: импортировался ли конфиг, показал ли
  AmneziaWG connected/on, и была ли попытка browser/app traffic.

Этот gate не должен менять статус public launch. Он проверяет только один fresh
per-device Android config handoff через приватную передачу файла.

## 4. Нужен ли Telegram ID третьего лица

Рекомендация: использовать `operator-mediated handoff`.

Для фактической передачи файла Telegram ID третьего лица не нужен. Оператор
получает `.conf` в private handoff директорию вне workspace и передает файл
третьему лицу приватным каналом, не публикуя содержимое.

Telegram ID третьего лица нужен только если конкретный execution helper создает
AMN2 order строго на numeric Telegram identity. В этом случае есть два
разрешенных варианта, но выбрать нужно до создания peer:

- `third_party_telegram_id_available=true`: использовать numeric Telegram ID
  третьего лица как test user/order identity;
- `third_party_telegram_id_available=false`: использовать operator-mediated
  identity, где оператор остается ответственным test owner, а устройство
  помечается как third-party Android handoff device.

Нельзя использовать ID случайного или старого тестового пользователя, если этот
человек не участвует в текущем тесте. Это особенно важно после предыдущей
путаницы с `8246155407`.

## 5. Artifact/private handoff boundary

Разрешено:

```text
private_handoff_dir=C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
artifact_type=.conf
artifact_count=1
artifact_location=outside_workspace
local_safe_metadata_allowed=filename bytes sha256 manifest
```

Запрещено:

```text
conf_payload_output_performed=false
qr_output_performed=false
vpn_import_link_output_performed=false
private_key_output_performed=false
preshared_key_output_performed=false
telegram_token_output_performed=false
password_output_performed=false
```

Передача третьему лицу должна быть приватной. В чат/evidence можно писать только
имя файла, размер, SHA256, fresh peer fingerprint и безопасные счетчики.

## 6. Android AmneziaWG pass criteria

Минимальные pass criteria на стороне Android:

```text
android_import_status=passed
android_connect_status=passed
android_traffic_attempted=true
android_traffic_source=browser_or_app
telegram_on_device_required=false
payload_screenshot_shared=false
```

Допустимые безопасные manual summaries:

```text
third_party_android_import_status=passed
third_party_android_connect_status=passed
third_party_android_browser_or_app_traffic_attempted=true
third_party_android_error_text=none
payload_screenshot_shared=false
```

Если есть ошибка, оператор принимает только текст ошибки без скриншотов с
payload, keys, QR, `vpn://` или содержимым `.conf`.

## 7. Server-side observation criteria

Execution gate должен подтвердить безопасными server-side наблюдениями:

```text
fresh_peer_found=yes
fresh_peer_limit=1
fresh_peer_expected_count_delta=1
fresh_peer_public_key_fp=present-redacted-or-short-fp
latest_handshake_after=true
endpoint_observed_after=yes
transfer_rx_delta_bytes_gt_0=true
transfer_tx_delta_bytes_gt_0=true
public_closed_probes_after_status=passed
secret_values_printed=false
```

Для baseline перед включением VPN допустимо:

```text
latest_handshake_age_s=never_or_stale
transfer_rx_bytes=baseline_value
transfer_tx_bytes=baseline_value
```

Для after snapshot после traffic должно быть видно новое рукопожатие или свежий
handshake age плюс рост счетчиков. Если Android показывает connected, но на
сервере нет handshake и нет роста счетчиков, gate считается failed с точным
блокером `server_side_handshake_not_observed`.

## 8. Stop-lines

Немедленно остановить gate, если:

- target VPS не `89.185.80.166`;
- AMN2 head не совпал с `187949bffb927a0a6d6c1f260fc0bb9ebb972447`;
- public closed probes не закрыты;
- helper собирается создать больше одного fresh peer;
- helper требует вывести `.conf`, QR, `vpn://`, private key, PSK, token или
  password;
- Telegram live send, bot polling, profile/media mutation или public exposure
  становятся частью сценария;
- предлагается package apply, service restart, restore/import/reboot, provider
  rebuild или firewall/listener/TLS/proxy change;
- используется Telegram ID человека, который не участвует в текущем тесте;
- third-party Android phone недоступен или владелец не может выполнить import,
  connect и traffic check;
- Android import/connect/traffic fails и точный safe error еще не зафиксирован.

## 9. Exact copy/paste execution gate command

Использовать только когда сторонний Android телефон реально доступен.

```text
THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE

Открыть exact gate для fresh third-party Android config handoff.

Использовать существующие Phase 8 evidence, SSH diagnostic result и
DB runtime retry result.

Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Third-party Android boundary:
- third-party Android user is not an admin/operator;
- Android phone is available for import/connect/browser-or-app traffic test;
- Telegram on Android device is not required;
- operator-mediated private handoff is accepted;
- if third-party Telegram ID is unavailable, do not use unrelated old IDs;
- create exactly one fresh per-device config only.

Allowed:
- read-only VPS precheck;
- current runtime/source head check without package apply;
- safe env presence checks without printing token/password values;
- create exactly one fresh third-party Android peer/config through AMN2
  runtime path;
- copy exactly one `.conf` artifact to private handoff destination outside
  workspace;
- server-side Android handshake/traffic observation;
- public closed probes for 3030, 3040, 80, 443;
- safe evidence with filename, bytes, SHA256, fresh peer fingerprint and
  counters only.

Forbidden:
- destructive VPS/provider action;
- package upload/apply unless separately approved;
- broad service restart;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- more than one peer/config;
- QR/vpn:// output;
- .conf payload output;
- private key/PSK/token/password output;
- Telegram live send or bot polling;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider rebuild;
- production rollout.

Private handoff destination:
C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF

Stop at first failed gate and report the exact blocker.
```

## 10. Next recommendation

Пока телефона нет:

```text
recommended_next_step=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

Когда телефон появится:

```text
recommended_next_practical_gate=THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE
```
