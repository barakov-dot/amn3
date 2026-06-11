# Amnezia VPN / DefaultVPN upstream refresh 2026-06-11

Дата: 2026-06-11.

Источник:

- GitHub organization: https://github.com/amnezia-vpn
- GitHub API repo list: https://api.github.com/orgs/amnezia-vpn/repos?per_page=100&sort=updated
- `amnezia-vpn/amnezia-client`: https://github.com/amnezia-vpn/amnezia-client
- `amnezia-vpn/DefaultVPN`: https://github.com/amnezia-vpn/DefaultVPN
- `amnezia-vpn/amneziawg-android`: https://github.com/amnezia-vpn/amneziawg-android
- `amnezia-vpn/amneziawg-apple`: https://github.com/amnezia-vpn/amneziawg-apple

Лицензия/граница:

- upstream code не копировался;
- сведения ниже используются только как product/API/UX compatibility signals;
- любые реализации в AMN2 должны оставаться самостоятельными и покрываться локальными тестами.

## Свежесть upstream

На момент проверки GitHub API показывал:

- `amnezia-vpn/amnezia-client`: default branch `dev`, `pushed_at=2026-06-11T04:48:30Z`;
- `amnezia-vpn/DefaultVPN`: default branch `dev`, fork, `pushed_at=2026-06-11T04:16:05Z`;
- `amnezia-vpn/amneziawg-android`: default branch `master`, `pushed_at=2026-06-09T00:03:29Z`;
- `amnezia-vpn/amneziawg-windows`: default branch `master`, `pushed_at=2026-06-09T00:14:59Z`;
- `amnezia-vpn/amneziawg-apple`: default branch `master`, `pushed_at=2026-06-09T00:10:33Z`.

## Import/QR signals

Проверенные reference-файлы:

- `amnezia-client/client/core/controllers/selfhosted/importController.cpp`;
- `amnezia-client/client/android/src/org/amnezia/vpn/ImportConfigActivity.kt`;
- `DefaultVPN/client/ui/controllers/importController.cpp`;
- `DefaultVPN/client/android/AndroidManifest.xml`;
- `DefaultVPN/client/ios/app/Info.plist.in`;
- `DefaultVPN/client/ui/qml/Pages2/PageSetupWizardConfigSource.qml`;
- `DefaultVPN/client/ui/qml/Pages2/PageSetupWizardQrReader.qml`;
- `amneziawg-android/ui/src/main/java/org/amnezia/awg/util/TunnelImporter.kt`;
- `amneziawg-apple/Sources/WireGuardApp/UI/TunnelImporter.swift`;
- `amneziawg-apple/Sources/WireGuardApp/UI/iOS/ViewController/QRScanViewController.swift`.

Выводы для AMN2:

- `vpn://` является отдельным import channel и должен быть удобен для ручного копирования/открытия, а не прятаться внутри длинного сообщения.
- `.conf` файл остается самым надежным fallback channel для DefaultVPN/AWG import.
- QR-поток в DefaultVPN не надо считать эквивалентным file/import-link потоку; UX не должен обещать, что встроенный QR-сканер DefaultVPN примет любой AMN2 QR.
- Если AMN2 отправляет QR, caption должен описывать payload честно. Для текущего bot fix QR кодирует `vpn://` import-ссылку, а сообщение явно оставляет fallback на `.conf` и отдельную ссылку.
- Ссылки на приложения лучше отправлять отдельным Telegram-сообщением, по одной ссылке на строку/блок, чтобы пользователь мог копировать их без выделения большого общего текста.

## Product candidates

```text
candidate_id: P4-AMNEZIA-REFRESH-001
priority: important
source: amnezia-vpn/amnezia-client + DefaultVPN import UX; live bot screenshots 2026-06-11
feature_area: Telegram bot config delivery UX
user_value: Russian-first config delivery, readable filenames, separate import/app links, safer DefaultVPN fallback text
AMN2_fit: completed local-only AMN2 slice
license_boundary: no upstream code copied
risk_class: secret-bearing delivery UX, no live delivery performed by Codex
secret_surface: `.conf`, QR, `vpn://` remain client-config-secret artifacts
remote_write_surface: none
required_gate: local-only for code/tests; live deploy/restart requires separate operator deploy decision
status: completed in AMN2 commit 908cafc Localize bot config delivery
```

```text
candidate_id: P4-AMNEZIA-REFRESH-002
priority: important
source: amnezia-vpn/amnezia-client, DefaultVPN, AmneziaWG Android/Apple import paths
feature_area: client import compatibility matrix
user_value: prevents promising QR/vpn/file behavior that a target client does not actually support
AMN2_fit: strong as docs/tests around existing delivery artifacts
license_boundary: independent tests/docs only
risk_class: secret-adjacent local tests
secret_surface: no raw real configs in evidence; fixtures only
remote_write_surface: none
required_gate: local-only
recommendation: next safe local-only slice before changing QR/native `.vpn` behavior again
```

```text
candidate_id: P4-AMNEZIA-REFRESH-003
priority: normal
source: DefaultVPN native share/config pages and `.vpn` document type
feature_area: DefaultVPN-native `.vpn` / Amnezia JSON delivery study
user_value: may give better DefaultVPN QR/share compatibility later
AMN2_fit: possible but not default Phase 4 work
license_boundary: no upstream code copied; own format contract required
risk_class: config delivery / secret-read
secret_surface: native config artifacts would be client-config-secret
remote_write_surface: none by itself
required_gate: blocked until separate config-delivery design gate
recommendation: defer until compatibility matrix is written and accepted
```

## Negative controls

- No upstream source/templates/UI/workflows copied.
- No public panel/API exposure.
- No live VPS commands.
- No live bot restart/deploy.
- No production user/peer mutation.
- No secret-bearing evidence stored in AMN3.
- No assumption that QR compatibility is universal across AmneziaVPN, DefaultVPN and standalone AmneziaWG clients.
