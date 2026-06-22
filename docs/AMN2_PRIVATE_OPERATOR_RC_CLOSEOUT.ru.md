# AMN2 private/operator RC closeout

Дата: 2026-06-22.

Статус:

```text
closeout_status=completed-docs-only
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
blocked_with_exact_remaining_blockers=false
remaining_blockers_inside_listed_limitations=none
```

Этот closeout использует только существующие Phase 8 evidence. Он не открывает
live, destructive, config delivery, Telegram send или public exposure gates.

## 1. Финальный private/operator RC статус

AMN2 можно запускать как закрытый private/operator RC с явными ограничениями.

Разрешенная формулировка:

```text
private/operator RC launch-ready with explicit limitations
```

Не разрешенная формулировка:

```text
public launch ready
```

Итог:

- private/operator RC готов в пределах зафиксированного scope;
- public launch не одобрен;
- внутри перечисленных ограничений нет оставшихся blockers;
- любые расширения требуют отдельного exact named gate.

## 2. Pushed heads и runtime/package line

```text
amn3_evidence_head_before_closeout=5f4f145 Add private operator RC final package
amn2_current_fixes_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447 Persist Android-compatible AWG defaults
latest_vps_applied_package_smoked_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
package_name=dist/amn2-vps-update-and-smoke-kit-187949b.zip
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
target_vps_used_for_phase8=89.185.80.166
```

Финальный AMN3 closeout head фиксируется самим commit/push, который добавляет
этот документ. После push его нужно смотреть командой:

```powershell
git log -1 --oneline --decorate
```

## 3. Package index

Финальный индекс private/operator RC package:

```text
docs/AMN2_PRIVATE_OPERATOR_RC_FINAL_PACKAGE.ru.md
```

Операторские документы:

```text
docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_RUN_CHECKLIST.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_CLOSEOUT.ru.md
```

Основной evidence chain:

```text
research/amn2/phase-8-p8-c001-fresh-android-config-acceptance-2026-06-21.md
research/amn2/phase-8-p8-c002-187949b-package-apply-smoke-2026-06-21.md
research/amn2/phase-8-p8-c003-fresh-zero-rehearsal-2026-06-22.md
research/amn2/phase-8-sfinal-launch-readiness-freeze-2026-06-22.md
research/amn2/phase-8-rc-handoff-2026-06-22.md
research/amn2/phase-8-rc-operator-run-checklist-2026-06-22.md
research/amn2/phase-8-rc-final-package-2026-06-22.md
research/amn2/phase-8-rc-closeout-2026-06-22.md
```

## 4. Next-chat starting point

В новом чате начинать с:

```text
docs/AMN2_PRIVATE_OPERATOR_RC_CLOSEOUT.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_FINAL_PACKAGE.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_RUN_CHECKLIST.ru.md
docs/NEXT_CHAT_AMN2_PHASE_8_PREP.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
```

Короткий старт для следующего чата:

```text
Продолжаем AMN2 после Phase 8 private/operator RC closeout.

Final status: launch-ready-with-explicit-limitations.
Private/operator RC launch-ready: true.
Public launch: not approved.
Remaining blockers inside listed private/operator RC limitations: none.

Use existing Phase 8 evidence first.
Do not open live/destructive/config/Telegram send/public exposure gates
without a fresh exact named gate.
```

## 5. Явные ограничения, внутри которых blockers не осталось

```text
public_launch_status=not-approved
public_exposure_status=closed-by-default
telegram_live_send_status=not-performed
telegram_bot_polling_status=not-performed
fresh_android_phone_acceptance_source=P8-C001
fresh_zero_android_acceptance_device=P8-C003_android_projector
config_delivery_primary_artifact=.conf
qr_release_primary=false
full_vpn_uri_release_primary=false
ios_defaultvpn_status=experimental_unreliable
backup_create_verify_status=passed
restore_import_status=not-proven
secret_payload_output_status=not-performed
```

Главное Android-уточнение:

- `P8-C001` доказал fresh Android phone acceptance.
- `P8-C003` fresh-from-zero rehearsal использовал Android projector с
  browser/app traffic.
- Нельзя выдавать `P8-C003` за fresh-zero Android phone acceptance.

## 6. Что закрыто для private/operator RC

Закрыто:

- fresh per-device Android phone acceptance через `P8-C001`;
- package/current-head smoke для AMN2 `187949b` через `P8-C002`;
- compatible AWG defaults persistence через обычный runtime/package path;
- fresh-from-zero `/opt/amn2` rehearsal через `P8-C003`;
- two-admin bot config verification без вывода admin IDs;
- Telegram `getMe` plus non-polling dispatcher/user-flow smoke;
- backup create+verify;
- private `.conf` handoff outside workspace;
- public probes stayed closed;
- final launch readiness freeze;
- operator handoff;
- operator run checklist;
- final package index.

## 7. Что не закрыто и требует отдельного gate

Не закрыто этим closeout:

- public web/admin/API exposure;
- domain/TLS/reverse proxy/Cloudflare/ngrok publication;
- Telegram live send;
- bot polling;
- Telegram profile/media mutation;
- production config delivery automation;
- QR or full `vpn://` as release-primary;
- iOS DefaultVPN release acceptance;
- backup restore/import DR;
- provider rebuild;
- production-scale rollout.

## 8. Stop-lines

Без нового exact named gate нельзя:

- live VPS/SSH command;
- destructive VPS/provider action;
- package upload/apply;
- service restart;
- public exposure;
- firewall/listener changes;
- config delivery;
- `.conf`, QR, `vpn://`, private key, PSK, token or password output;
- Telegram live send;
- bot polling;
- Telegram profile/media mutation;
- backup restore/import/reboot;
- production peer/user mutation;
- provider rebuild;
- broader rollout.

## 9. Следующие exact gates, если нужен более широкий запуск

```text
PUBLIC-EXPOSURE-GATE
TELEGRAM-LIVE-DELIVERY-GATE
CONFIG-DELIVERY-GATE
RESTORE-IMPORT-DR-GATE
PRODUCTION-ROLLOUT-GATE
PROVIDER-REBUILD-GATE
FRESH-ANDROID-PHONE-POST-RC-RECHECK-GATE
```

## 10. Рекомендованная команда следующего шага

Если оператор не запрашивает более широкий запуск, следующий шаг - удерживать
статус без новых live-gates:

```text
P8-RC-READY-HOLD

Use existing Phase 8 evidence only.
Do not open live/destructive/config/Telegram send/public exposure gates.
Hold AMN2 at private/operator RC launch-ready-with-explicit-limitations.
Open a new exact named gate only if operator requests real RC operation,
config delivery, Telegram live send, public exposure, restore/import,
provider rebuild or broader rollout.
```
