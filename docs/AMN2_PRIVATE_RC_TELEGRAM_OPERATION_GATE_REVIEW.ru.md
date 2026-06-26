# PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW

Дата: 2026-06-26.

Статус: `completed-docs-only`.

Использованы существующие Phase 8 evidence, private RC final status snapshot,
Telegram live preview result, DB runtime retry result и release limitations
refresh.

Live/VPS/config/Telegram/public gates не открывались.

## Review verdict

```text
review_go=true
execution_gate_go=conditional-go-with-explicit-operator-approval
recommended_next_gate=PRIVATE_RC_TELEGRAM_OPERATION_GATE
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
allowed_live_scope=controlled-private-operator-telegram-operation
public_launch_status=not-approved
config_delivery_status=not-approved
production_rollout_status=not-approved
```

Открывать execution gate можно только если оператор осознанно хочет реальный
controlled Telegram bot polling для закрытого private/operator RC. Этот review
не запускает polling и не выполняет VPS/Telegram live действия.

## Основание

Уже доказано:

```text
telegram_getme=passed
private_rc_telegram_bot_live_preview_status=passed-with-manual-operator-observation
operator_start_flow_observed=passed
bot_polling_start_stop_preview=passed
bot_polling_process_after=stopped
public_closed_probes_before_after=passed
db_path_classification=passed-db-path-classified-with-aggregate-limitation
android_private_operator_rc_proof=complete-with-explicit-limitations
```

Предыдущий live preview был узким и успешным, но это не постоянная эксплуатация:

```text
preview_gate=PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE
preview_run_id=20260624T184735Z
partner_start_flow_observed=not_reported
config_delivery_performed=false
peer_creation_performed=false
public_exposure_performed=false
```

## Allowed actions for execution gate

Разрешить только внутри будущего `PRIVATE_RC_TELEGRAM_OPERATION_GATE`:

- read-only VPS/runtime/source precheck;
- expected AMN2 head check without package apply;
- safe env presence checks without printing token/password values;
- DB path existence and aggregate-safe precheck without row dump/download;
- public closed probes for `3030`, `3040`, `80`, `443`;
- Telegram `getMe`;
- start exactly one controlled bot polling process;
- allow live Telegram replies only to approved admin/operator chats;
- allow minimal DB mutation caused by Telegram user/chat/session state for
  approved admin/operator chats only;
- manual operator UX check;
- stop polling at the end unless operator explicitly approves a separate
  persistent operation gate;
- final no-unexpected-polling/no-public-exposure guard;
- safe evidence only.

Approved admin/operator boundary:

```text
admin_operator_count_expected=2
operator_admin_pair_expected=true
admin_ids_value_output_allowed=false
```

Known private operator IDs are not printed into helper output/evidence; only
presence/count and pair-match status are allowed.

## Forbidden actions

Запрещено:

- destructive VPS/provider action;
- package upload/apply;
- broad service restart;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation;
- config delivery;
- peer creation;
- `.conf`, QR, `vpn://` output;
- private key/PSK/token/password output;
- Telegram profile/media mutation;
- Telegram broadcast/mass send;
- non-admin user rollout;
- restore/import/reboot;
- provider rebuild;
- production-scale rollout;
- DB row dump/download/copy.

## DB/runtime note

DB state was clarified after the earlier live preview:

```text
previous_preview_db_present=false
db_runtime_retry_status=passed-db-path-classified-with-aggregate-limitation
settings_database_resolved_path=/opt/amn2/data/amneziya.sqlite3
settings_database_exists=true
db_aggregate_counts_status=not_observed_due_to_helper_quoting
```

Execution gate should not depend on DB row dumps. It may do safe path/existence
or aggregate-count precheck if implemented safely, but must stop before dumping
rows or copying DB.

## Pass criteria

Execution gate passes only if:

```text
target_vps_match=yes
source_overlay_match=yes
telegram_get_me_status=passed
public_closed_probes_before_status=passed
exactly_one_bot_polling_process_started=true
operator_start_flow_observed=passed
partner_start_flow_observed=passed_or_not_available_explicitly_recorded
config_delivery_attempted=false
peer_creation_performed=false
public_closed_probes_after_status=passed
bot_polling_process_after=stopped
unexpected_bot_polling_process_after=absent
secret_values_printed=false
```

If operator explicitly wants persistent bot operation later, that is a different
gate. This review only prepares a controlled start/manual-check/stop operation
gate.

## Fail criteria / stop-lines

Stop immediately if:

- target VPS is not `89.185.80.166`;
- AMN2 source/runtime head is not
  `187949bffb927a0a6d6c1f260fc0bb9ebb972447`;
- public probes are not closed before polling;
- existing unknown bot polling process is present;
- more than one polling process would be started;
- bot token/settings load fails;
- bot replies to non-approved chats/users during test;
- UI offers or triggers config delivery unexpectedly;
- any `.conf`, QR, `vpn://`, key, PSK, token/password would be printed;
- helper would create peer/config;
- service/package/public/firewall/TLS/proxy mutation appears;
- stop polling fails at the end;
- final public probes are not closed.

## Manual operator checklist

During execution gate:

```text
operator_start_flow_observed=<passed|failed>
partner_start_flow_observed=<passed|not_available_explicitly_recorded|failed>
config_delivery_attempted=false
payload_screenshot_shared=false
unexpected_error_text=<none|safe_text_only>
```

Do not click config delivery, approve/create config, QR, `vpn://`, `.conf` or
peer-management buttons during this operation review execution.

## Exact copy/paste execution gate command

```text
PRIVATE_RC_TELEGRAM_OPERATION_GATE

Открыть exact gate для controlled private/operator Telegram bot operation.

Использовать существующие Phase 8 evidence, final status snapshot,
PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW и release limitations refresh.

Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Allowed:
- read-only VPS/runtime/source precheck;
- current runtime/source head check without package apply;
- safe env presence checks without printing token/password values;
- DB path/existence or aggregate-safe precheck without DB row dump/download;
- public closed probes for 3030, 3040, 80, 443;
- Telegram getMe;
- start exactly one controlled Telegram bot polling process;
- allow live Telegram replies only to approved admin/operator chats;
- allow minimal Telegram user/chat/session DB state mutation for approved
  admin/operator chats only;
- manual operator UX check;
- stop bot polling at the end;
- final no-polling/no-public-exposure guard;
- safe evidence without secret-bearing payload.

Forbidden:
- destructive VPS/provider action;
- package upload/apply;
- broad service restart;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation or config delivery;
- peer creation;
- .conf/QR/vpn:// output;
- private key/PSK/token/password output;
- Telegram profile/media mutation;
- Telegram broadcast/mass send;
- non-admin user rollout;
- restore/import/reboot;
- provider rebuild;
- production-scale rollout;
- DB row dump/download/copy.

Manual UX boundary:
- operator sends /start and checks menu/admin-visible surface;
- partner admin sends /start if available;
- do not click config delivery, approve/create config, QR, vpn link, .conf or
  peer-management buttons;
- report only safe manual summary.

Stop at first failed gate and report exact blocker.
```

## Recommendation

```text
recommended_next_step=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
recommended_execution_gate=PRIVATE_RC_TELEGRAM_OPERATION_GATE
execution_gate_open_requires_explicit_operator_request=true
```
