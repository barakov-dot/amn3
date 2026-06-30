# AMN2 Phase 9 client display-name policy refresh

Дата: 2026-06-30.
Статус: `prepared-docs-only`.

Этот документ фиксирует только безопасное обновление naming policy по
результатам operator-visible client import screenshots. Config payloads, QR
payloads, `vpn://` import URI, keys, PSK, tokens, passwords и raw logs в этот
документ не включались.

```text
source=operator_screenshots_and_manual_import_observation
scope=client_display_name_policy_only
live_actions=false
peer_creation=false
config_generation=false
config_delivery=false
public_exposure=false
```

## Decision

Целевое user-visible имя для всех Amnezia/AmneziaWG/DefGuard client apps:

```text
canonical_client_display_name=NeobyatnayaNET
display_name_suffix_policy=none
display_name_device_number_policy=none
display_name_platform_prefix_policy=none
manual_rename_target=NeobyatnayaNET
manual_rename_cyrillic_alias=НеобъятнаяNET
```

`NeobyatnayaNET` выбран как canonical target, потому что это ASCII-safe имя для
кроссплатформенного import/display контура. `НеобъятнаяNET` допускается как
ручное UI-имя на клиентах, где оператор явно хочет кириллическое отображение и
клиент его стабильно сохраняет.

## Observed Behavior

```text
android_import_observed=partial
android_observed_display_names=Сервер 1|Сервер 3
android_auto_display_name_applied=false
android_manual_rename_required=true
windows_import_observed=true
windows_auto_display_name_applied=false
windows_manual_rename_performed=true
tv_projector_import_status=pending_operator_review
```

Файлы package могут сохранять уникальные suffixes для локального различения
артефактов, но эти suffixes не являются целевым display name внутри client app:

```text
artifact_filename_suffixes_allowed=true
artifact_filename_suffixes_are_display_name=false
client_display_name_expected_same_for_all_devices=true
```

## Boundary

Это docs-only решение не пересоздает существующие configs и не открывает live
execution. Если понадобится новый package с обновленным target naming, он должен
идти отдельным exact operator gate.

```text
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
```
