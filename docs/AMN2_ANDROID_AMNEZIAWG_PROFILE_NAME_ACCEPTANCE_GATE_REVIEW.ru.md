# AMN2 Android AmneziaWG profile-name acceptance — docs-only review

Дата: 2026-06-27.
Модель: ChatGPT 5.3-Spark (docs-only).
Статус: `completed-docs-only-review`.

Ключевой вводной блок уже принят на уровне `AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW`:

- canonical naming: `Neobyatnaya-AMNZ-N`
- display-name issue: `SERVER1` после импортa (Android App display-name compatibility gap)
- next exact gate: `ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`

Этот документ не открывает live/VPS/SSH/config/Telegram/public execution gate.
Config generation/delivery не выполнялись. Peer/config не создавались. VPS, auth,
firewall, users, keys и ports не менялись. Никаких secret-bearing payloads,
keys, tokens, `.conf`, QR, `vpn://`, PSK, password или raw logs не выводилось.

## Решение

```text
review_name=AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE_REVIEW
review_status=passed
scope=docs-only
execution_go=false
future_exact_gate_required=true
exact_named_gate=ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
canonical_name_policy=Neobyatnaya-AMNZ-N
filename_policy=Neobyatnaya-AMNZ-N.conf
server1_is_not_accepted_as_final_name=true
server1_classification=app_display_name_product_compatibility_gap
```

Решение этого review-only шага:

- подтвердить, что Android `SERVER1` рассматривается как наблюдение по client-display-name
  compatibility, а не как готовый production naming;
- зафиксировать, что реальная проверка `SERVER1/Neobyatnaya-AMNZ-N` в UI приложения
  должна выполняться только через отдельный exact named gate;
- не расширять public/public self-service routes до подтверждения этого gate;
- передать 5.5-ready product-compatibility decision в future execution scope без
  изменения naming contract.

## Что считаем проходом

```text
canonical_generated_name_match=true
canonical_filename_match=true
display_name_test_scope_defined=true
safe_summary_only=true
payloads_publication=false
peer_creation=false
secret_value_printed=false
```

## Что считается fail до exact gate

- `execution_go=false` при отсутствии explicit named gate.
- `Neobyatnaya-AMNZ-N` не используется на artifacts/filename.
- `SERVER1` принимается как разрешённое итоговое имя без fallback/compatibility decision.
- любые попытки публикации raw payload / `.conf` / QR / `vpn://` в чат или лог.
- запуск любого live-config workflow, peer creation или public/self-service delivery.

## Дальше

- Используем этот review как вход для runbook.
- Для реального наблюдения и принятия результата открывать только
  `ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE` в отдельном exact gate.
- После exact gate результаты записывать в
  `AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT_TEMPLATE.ru.md`.
