# Runbook: AMN2 Phase 9 Android multi-device private config execution

Дата: 2026-06-28.
Статус: `prepared-docs-only`.

## Назначение

Runbook для будущего exact gate:
`ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_GATE_3_TO_5`.

Сейчас runbook не выполняется. Он описывает порядок, который можно будет
запустить только после отдельной команды approve.

## Preconditions

```text
gate_name=ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_GATE_3_TO_5
device_count=3|4|5
scope=private_operator_only
canonical_naming=Neobyatnaya-AMNZ-N
android_fallback=manual_rename
local_private_artifact_root=private-artifacts/phase9/android-multi-device/<run_id>/
local_private_artifact_root_gitignored=true
payload_output_to_chat=false
public_scope=false
```

## Порядок будущего execution

1. Оператор подтверждает exact gate и количество устройств.
2. Создается локальная приватная папка
   `private-artifacts/phase9/android-multi-device/<run_id>/`.
3. Проверяется, что `private-artifacts/` находится в `.gitignore`.
4. Проверяется рабочая ветка и текущий AMN2 commit.
5. Выполняется source/package precheck без вывода payload.
6. Если gate разрешает peer creation, peer creation выполняется только в рамках
   подтвержденного количества устройств.
7. Если gate разрешает config generation, генерируется private package только
   для operator-controlled channel.
8. Файлы сохраняются с именами `Neobyatnaya-AMNZ-N-android-01.conf` ...
   `Neobyatnaya-AMNZ-N-android-05.conf` по числу approved devices.
9. В чат возвращается только safe summary.
10. Result фиксируется по template без payload values.

## Safe summary fields

```text
run_id=YYYYMMDDTHHMMSSZ
gate_name=ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_GATE_3_TO_5
device_count=3|4|5
local_private_artifact_root=private-artifacts/phase9/android-multi-device/<run_id>/
filenames=Neobyatnaya-AMNZ-N-android-01.conf|Neobyatnaya-AMNZ-N-android-02.conf|Neobyatnaya-AMNZ-N-android-03.conf|Neobyatnaya-AMNZ-N-android-04.conf|Neobyatnaya-AMNZ-N-android-05.conf
peer_creation_performed=performed|not_performed
config_generation_performed=performed|not_performed
config_delivery_performed=performed|not_performed
payload_output_to_chat=blocked
public_exposure=blocked
secret_publication=blocked
result=pass|fail|defer
```

## Запрещено даже во время future execution

- Печатать `.conf`, QR payload, import URI, private key, PSK, tokens,
  passwords или raw logs.
- Публиковать package в git/docs/chat.
- Открывать public/self-service routes.
- Делать действия вне подтвержденного количества устройств.
- Объединять этот gate с SSH/auth/firewall/users/ports changes.

## Команда для будущего approve

```text
APPROVE_ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_GATE_3_TO_5
device_count=3|4|5
scope=private_operator_only
local_private_artifact_root=private-artifacts/phase9/android-multi-device/<run_id>/
payload_output_to_chat=blocked
```

Без этой команды runbook остается docs-only.
