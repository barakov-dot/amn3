# AMN2 private RC DB/runtime observation review

Дата: 2026-06-24.

Статус:

```text
private_rc_db_runtime_observation_review_status=completed-docs-only
gate_name=PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE
gate_opened=false
live_vps_ssh_performed=false
telegram_polling_started=false
telegram_live_send_performed=false
config_generation_performed=false
config_delivery_performed=false
public_exposure_performed=false
secret_values_printed=false
```

Этот review использует только существующие Phase 8 evidence и private RC live
preview result. Он не открывает live/VPS/config/Telegram/public gates.

## 1. Причина review

В `PRIVATE_RC_OPERATOR_RUN_GATE` от 2026-06-22 DB aggregate inventory видел:

```text
db_present=true
db_bytes=147456
users_count=1
devices_count=1
servers_count=1
api_tokens_count=2
admin_actions_count=7
```

В `PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE` от 2026-06-24 helper увидел:

```text
db_present=false
```

При этом live preview прошел по своему узкому критерию: Telegram `getMe`
прошел, controlled polling стартовал, операторский `/start` прошел, polling был
остановлен, public probes остались закрытыми, config delivery и peer creation
не выполнялись.

## 2. Рабочие гипотезы

`db_present=false` в live preview может означать одно из безопасно проверяемых
read-only состояний:

- runtime ожидает DB по пути, который отличается от пути, проверенного helper;
- DB была создана/использована через settings path, но helper проверял не тот
  filesystem path;
- DB отсутствует в текущем `/opt/amn2`, но web process живет с другим cwd или
  другим env;
- DB path зависит от переменных окружения или default settings;
- DB была не нужна для `/start` preview из-за lazy/init behavior, но это нужно
  подтвердить отдельно;
- helper logic мог печатать `db_present=false` из-за слишком узкой проверки.

Этот review не делает вывода о root cause. Он готовит отдельный read-only gate
для сбора evidence.

## 3. Цель будущего gate

ЦЕЛЬ:
понять, где фактически находится DB/runtime state в private RC runtime, почему
Telegram live preview helper увидел `db_present=false`, и есть ли блокер для
следующих DB-dependent gates.

Что доказывает:

- target VPS и AMN2 head соответствуют ожидаемым;
- какие DB paths существуют в `/opt/amn2` и runtime settings;
- видит ли web process тот же `.env`, cwd и runtime path;
- можно ли безопасно получить DB aggregate inventory без строк и секретов;
- не требуется ли поправка helper path logic перед следующими gates.

Что не доказывает:

- production DB migration readiness;
- restore/import DR;
- config delivery;
- public launch readiness;
- Telegram production operation;
- Android phone acceptance;
- provider rebuild readiness.

Влияние на близость запуска:

```text
private_operator_rc_runtime_confidence_after_pass=higher
db_dependent_gate_confidence_after_pass=higher
public_launch_status_after_pass=still_not_approved_without_separate_public_gate
config_delivery_status_after_pass=still_not_approved_without_separate_config_gate
```

Следующий gate если passed:

```text
ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

или конкретный DB-dependent gate, если оператор его явно запросит.

Stop-line если failed:
остановиться на первом failed sub-gate, зафиксировать exact blocker и не
компенсировать failure package apply, service restart, public exposure,
config delivery, Telegram polling/live send, restore/import, provider action
или broader rollout без нового exact named gate.

## 4. Target VPS review

```text
target_vps=89.185.80.166
target_review=passed
```

Основание:

- `PRIVATE_RC_OPERATOR_RUN_GATE` подтвердил `target_vps_match=yes`;
- `PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE` успешно подключился к тому же
  target VPS;
- corrected external probes в обоих контурах сохраняли public exposure closed.

## 5. Expected AMN2 head review

```text
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
expected_amn2_head_review=passed
```

Основание:

- `P8-C002` package/current-head smoke passed на `187949b`;
- `P8-C003` fresh-from-zero rehearsal использовал `187949b`;
- `PRIVATE_RC_OPERATOR_RUN_GATE` подтвердил `source_overlay_match=yes`;
- `PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE` подтвердил `source_overlay_match=yes`.

## 6. Что можно проверить read-only

Allowed read-only checks внутри будущего gate:

- `target_vps` identity marker;
- `/opt/amn2` existence and source overlay marker;
- `.env` presence only, without printing values;
- DB path candidates by filename and size only;
- settings-derived DB URL/path with secret redaction;
- process list for web process and cwd/env path fingerprints only;
- safe DB aggregate counts through app repository if DB exists;
- file owner/mode/size/mtime for DB candidates;
- loopback web health only if already running, without service start/restart;
- external closed probes for `3030`, `3040`, `80`, `443`;
- final mutation/output guard.

Forbidden checks:

- printing `.env` values;
- printing DB rows;
- dumping schema with sensitive data;
- copying/downloading DB;
- starting/stopping/restarting services;
- package upload/apply;
- DB migration/write;
- Telegram polling/live send;
- config generation/delivery;
- public exposure changes.

## 7. Allowed actions

Allowed only inside future `PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE`:

- read-only VPS observation;
- current runtime/source head check without package apply;
- safe env presence checks without printing token/password values;
- DB path/cwd/process observation without row dump;
- DB aggregate inventory if DB path exists;
- loopback web health without service start/restart;
- public closed probes for `3030`, `3040`, `80`, `443`;
- safe evidence without secret-bearing payload.

Not allowed:

- destructive VPS/provider action;
- package upload/apply;
- service start/restart/stop;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation or config delivery;
- peer creation or peer/user production mutation;
- `.conf`, QR, `vpn://`, private key, PSK, token/password output;
- Telegram polling or live send;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider rebuild;
- production rollout.

Review:

```text
allowed_actions_review=passed
read_only_boundary_review=passed
db_secret_boundary_review=passed
public_exposure_boundary_review=passed
telegram_boundary_review=passed
```

## 8. Pass/fail criteria

Gate passes if all are true:

```text
target_vps_match=yes
source_overlay_match=yes
dotenv_presence_checked_without_values=true
db_path_observation_completed=true
db_root_cause_classification=path_mismatch_or_present_or_absent_explained
db_rows_printed=false
secret_values_printed=false
package_upload_apply_performed=false
service_restart_performed=false
telegram_polling_started=false
telegram_live_send_performed=false
config_generation_performed=false
config_delivery_performed=false
public_closed_probes_status=passed
```

Gate fails on any one:

```text
target_vps_mismatch=true
source_overlay_mismatch=true
secret_value_printed=true
db_row_dump_performed=true
package_apply_performed=true
service_restart_performed=true
telegram_polling_started=true
config_generation_or_delivery_performed=true
public_probe_not_closed=true
db_path_observation_inconclusive=true
```

## 9. GO / NO-GO

```text
review_go=true
gate_open_go=conditional-go-with-explicit-operator-approval
operator_can_open_gate_now=true
```

Причина:
gate является read-only VPS observation и не требует Android phone или Telegram
live action. Но он все равно использует VPS SSH, поэтому требует отдельного
явного открытия оператором.

## 10. Copy/paste command для открытия gate

```text
PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE

Открыть exact gate для private/operator DB/runtime read-only observation.

Использовать существующие Phase 8 evidence и private RC live preview result.
Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Allowed:
- read-only VPS observation;
- current runtime/source head check without package apply;
- safe env presence checks without printing token/password values;
- DB path/cwd/process observation without DB row dump;
- settings-derived DB path observation with secret redaction;
- DB aggregate inventory if DB exists;
- loopback web health only if already running, without service start/restart;
- public closed probes for 3030, 3040, 80, 443;
- safe evidence without secret-bearing payload.

Forbidden:
- destructive VPS/provider action;
- package upload/apply;
- service start/restart/stop;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation or config delivery;
- peer creation;
- .conf/QR/vpn:// output;
- private key/PSK/token/password output;
- DB row dump or DB download/copy;
- Telegram polling or live send;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider rebuild;
- production rollout.

Stop at first failed gate and report the exact blocker.
```
