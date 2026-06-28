# AMN2 Phase 9 Android multi-device private config execution gate review

Дата: 2026-06-28.
Статус: `prepared-docs-only-review`.

## Назначение

Подготовить exact gate для private/operator generation package на 3-5 Android
устройств.

Этот review не открывает выполнение. Он только фиксирует, какие условия должны
быть подтверждены оператором перед реальной генерацией private configs.

## Gate

```text
gate_name=ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_GATE_3_TO_5
scope=private_operator_android_devices
device_count_min=3
device_count_max=5
public_scope=false
self_service_scope=false
external_delivery_scope=false
local_private_artifact_root=private-artifacts/phase9/android-multi-device/<run_id>/
local_private_artifact_root_gitignored=true
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
```

## Что разрешено сейчас

- Docs-only review этого gate.
- Подготовка runbook и result template.
- Синхронизация status/matrix/next-chat.
- Safe scan и `git diff --check`.

## Что запрещено сейчас

- Генерация реальных client configs.
- Создание peer-ов.
- Доставка `.conf`, QR или import URI.
- SSH/VPS/Telegram/public действия.
- Вывод payload, keys, PSK, tokens, passwords или raw logs.

## Локальная приватная папка будущего package

Будущие private config artifacts должны лежать только локально и вне git:

```text
private-artifacts/phase9/android-multi-device/<run_id>/
```

Папка `private-artifacts/` должна быть в `.gitignore`. В docs/git можно
фиксировать только путь и safe summary, но не содержимое.

## Naming будущих 3-5 configs

Для Android multi-device package используются уникальные filename suffixes при
сохранении canonical base:

```text
Neobyatnaya-AMNZ-N-android-01.conf
Neobyatnaya-AMNZ-N-android-02.conf
Neobyatnaya-AMNZ-N-android-03.conf
Neobyatnaya-AMNZ-N-android-04.conf
Neobyatnaya-AMNZ-N-android-05.conf
```

Если approved device count меньше 5, используются только первые N имен. Эти
имена относятся к локальным filenames/package artifacts. Android display-name
limitation остается прежним: если клиент показывает `Сервер 1`, это documented
client display-name compatibility gap с `manual_rename` fallback.

## Условия для будущего approve

Перед открытием execution operator должен явно подтвердить:

```text
approved_gate=ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_GATE_3_TO_5
approved_device_count=3|4|5
approved_scope=private_operator_only
approved_local_private_artifact_root=private-artifacts/phase9/android-multi-device/<run_id>/
approved_generation=confirmed_at_future_gate
approved_peer_creation=confirmed_at_future_gate|not_confirmed
approved_delivery_channel=operator_private_channel_only
approved_payload_output_to_chat=blocked
approved_public_exposure=blocked
```

Если хотя бы один пункт не подтвержден, execution остается закрытым.

## Pass criteria будущего execution

- Количество устройств строго 3-5.
- Naming policy: `Neobyatnaya-AMNZ-N`.
- Windows filename policy не ломается: `Neobyatnaya-AMNZ-N.conf`.
- Android display-name limitation остается documented: `Сервер 1` допускается
  только как client display-name compatibility gap с `manual_rename` fallback.
- В публичный чат, docs или git не попадают config payloads, QR payloads,
  import URI, keys, PSK, tokens, passwords или raw logs.
- Результат фиксируется только safe summary.

## Fail criteria

- Попытка выполнить generation без точного approve.
- Количество устройств меньше 3 или больше 5.
- Public/self-service scope.
- Payload/secret output в чат/docs/git.
- Peer/config action без подтвержденного exact gate.

## Stop-lines

```text
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
```
