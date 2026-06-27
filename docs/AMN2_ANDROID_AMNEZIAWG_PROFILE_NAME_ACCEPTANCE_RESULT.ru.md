# AMN2 Android AmneziaWG profile-name acceptance result

Дата: 2026-06-27.
Статус: `completed-safe-result`.
Gate: `ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`.

Этот result фиксирует только безопасное наблюдение имени профиля в Android
Amnezia app. Live/VPS/SSH/config/Telegram/public gates не открывались. Peer/config
не создавались. Config generation/delivery не выполнялись. Payloads, keys, QR,
import URI, PSK, token/password и raw logs не выводились.

## Safe Result

```text
observed_display_name=Сервер 1
expected_display_name=Neobyatnaya-AMNZ-N
observed_display_name_matches_expected=false
classification=documented_limitation
manual_rename_required=true
canonical_name_policy=Neobyatnaya-AMNZ-N
required_filename_policy=Neobyatnaya-AMNZ-N.conf
```

## Decision

`Сервер 1` считается localized `SERVER1`, то есть client display-name
compatibility limitation. Это не production naming и не pass. Для Android
Amnezia app automatic display-name из standard AmneziaWG/WireGuard-style config
считается `not-supported-or-not-proven`; fallback: manual rename profile to
`Neobyatnaya-AMNZ-N`.

## Platform Implementation Policy

```text
where_possible_implement_display_name=true
windows_amneziawg_display_name_strategy=filename_basename
windows_amneziawg_required_filename=Neobyatnaya-AMNZ-N.conf
android_display_name_strategy=manual_rename_fallback
ios_display_name_strategy=not_proven_manual_rename_fallback
```

- Windows AmneziaWG standalone: закладываем implementation через filename /
  basename. Future artifact filename должен быть `Neobyatnaya-AMNZ-N.conf`.
- Android Amnezia app: оставляем documented limitation и manual rename fallback.
- iOS Amnezia app: automatic display-name из config не доказан; до отдельного
  iOS exact gate оставляем manual rename fallback.

## Source Basis

- Official Amnezia client import logic for WireGuard/AmneziaWG config assigns
  display description through `nextAvailableServerName()`:
  https://github.com/amnezia-vpn/amnezia-client/blob/0f6847219b87e94e9948bee3f57a4d7a2465acb4/client/core/controllers/selfhosted/importController.cpp
- Official AmneziaWG Windows import logic uses config filename basename as
  imported tunnel name:
  https://github.com/amnezia-vpn/amneziawg-windows-client/blob/master/ui/tunnelspage.go

No further execution is approved by this result.
