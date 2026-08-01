# Phase 13: AWG2/AWG3 readiness и client-version admission gate

Проверено: `2026-08-01T16:20:03+03:00`.

## Безопасная исходная точка

- Phase 12 Spain Migration полностью принята.
- AMN2 source: `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
- Spain operational overlay:
  `f1bf099ddb47da26a4080714376babaf5b0de92c`.
- Текущий Spain runtime и семь выданных профилей являются принятым AWG2
  baseline. Доказательств установленного AWG3 server runtime или принятой
  AWG3 config issuance на Spain нет.
- Этот документ не разрешает SSH, VPS, peer, config generation/delivery,
  firewall, Docker, Telegram или AWG mutation.

## Официальные источники

| Источник | Наблюдаемый baseline | Прямое свидетельство |
|---|---|---|
| [AmneziaVPN 5.0.0.5 release](https://github.com/amnezia-vpn/amnezia-client/releases/tag/5.0.0.5) | tag `5.0.0.5`, commit `4d28f819650a747c3aa4997b503dcf2f4259cb19`, опубликован 2026-07-26 | changelog прямо сообщает `Added AWG 3 support` |
| [Официальный AWG3 client commit](https://github.com/amnezia-vpn/amnezia-client/commit/5e9def4184f0799f9984d2bbde5d4237dc649abc) | commit `5e9def4184f0799f9984d2bbde5d4237dc649abc` от 2026-07-25 | добавлены AWG3 config fields и client runtimes `awg-go 3.0.1`, `awg-android 3.0.1`, `awg-apple 3.0.1`, `awg-windows 3.0.2` |
| [amneziawg-go v3.0.1 contract](https://github.com/amnezia-vpn/amneziawg-go/blob/v3.0.1/README.md) | tag `v3.0.1`, commit `9f5d948bc72cc554791cfe0fb91527e4acfb6b79` | `HeaderProtectionKey` обозначен как AWG3+ server-side parameter; AWG3+ также добавляет content padding и timing ranges |
| [DefaultVPN App Store](https://apps.apple.com/us/app/defaultvpn/id6744725017) | version `2.0.0`, release date `2026-07-30T15:33:05Z`, iOS 14+ | version history прямо сообщает `Added AWG 3 support` |

GitHub-репозиторий DefaultVPN не публикует GitHub Releases, поэтому для
фактически распространяемого iOS build authoritative evidence здесь является
App Store version history.

## Что является фактом, а что выводом

Наблюдаемые факты:

- новые официальные клиенты уже умеют читать AWG3-поля;
- AWG3 вводит дополнительный `HeaderProtectionKey`, который официальный
  runtime contract классифицирует как server-side и требующий одинакового
  значения на сервере и клиенте;
- текущий Spain runtime принят как AWG2 и не проходил AWG3 install/config/data
  acceptance;
- существующие семь Spain AWG2-профилей работают и не должны автоматически
  заменяться.

Вывод для AMN2:

- AMN2 готов проектировать dual-version issuance, но ещё не готов выдавать
  production AWG3-конфиги;
- AWG3 нельзя получить простым добавлением новых строк в существующий AWG2
  client config: сначала нужен совместимый server runtime и data-path evidence;
- безопасный первый вариант — оставить принятый AWG2 interface/port без
  изменений и проектировать изолированный AWG3 runtime/interface/UDP port.
  Это архитектурный вывод, а не live-разрешение; coexistence, capacity, IPAM,
  port conflict, rollback и foreign-service equality должны быть доказаны
  отдельным gate.

## Продуктовый контракт Phase 13

### Поддерживаемые новые выдачи

- Новые AMN2 issuance targets: `AWG2` и `AWG3`.
- Новую выдачу AWG1/legacy не развивать.
- Существующие legacy-профили не удалять и не отключать без отдельного
  evidence-backed решения и exact approval.
- Существующие Spain d1–d7 остаются AWG2; массового перевыпуска нет.

### Обязательный запрос перед выдачей

До выбора формата оператор или пользователь сообщает:

1. точное приложение: например, `AmneziaVPN`, `DefaultVPN` или другой клиент;
2. платформу: Android/Android TV/iOS/Windows/macOS/Linux;
3. точную версию приложения;
4. количество требуемых слотов и получателя;
5. срок: indefinite по умолчанию для локальной операторской выдачи либо
   явно заданный expiry.

Нельзя выбирать AWG3 только по названию ОС или утверждению «клиент свежий».

### Fail-closed admission

- `AmneziaVPN >= 5.0.0.5` допускается к AWG3-кандидату только на платформе и
  build, для которых отдельно подтверждены import и full-data test.
- `DefaultVPN >= 2.0.0` допускается к AWG3-кандидату на iOS только после
  отдельного real-device import/full-data test.
- Известный и проверенный AWG2 client получает AWG2.
- Неизвестная, неподтверждённая или слишком старая версия не получает
  конфиг автоматически: сначала требуется upgrade либо compatibility check.
- Пока AWG3 live gate не принят, production issuance остаётся AWG2-only.

## Минимальный AWG3 gate

1. Написать bilingual design spec для version admission, protocol capability,
   отдельного runtime/interface/port, IPAM и rollback.
2. После отдельного утверждения написать TDD implementation plan.
3. Локально реализовать typed protocol version без config/secret output:
   `AWG2` и `AWG3` не должны смешиваться в manifest, passport или receipt.
4. Добавить golden/negative tests AWG2 и AWG3, secret redaction, idempotency,
   unknown-version rejection и existing-AWG2 non-regression.
5. Подготовить отдельный checksum-bound test package и exact live approval.
6. На Spain сначала выполнить read-only capacity/IPAM/port/foreign-service
   preflight; не останавливать и не перезапускать текущий AWG2.
7. Развернуть только изолированный AWG3 candidate, затем проверить import,
   handshake, full data, reboot persistence и независимый rollback.
8. Минимальная real-device matrix: актуальный AmneziaVPN на Windows и Android,
   DefaultVPN 2.0.0+ на iOS; Android TV и standalone clients допускаются только
   после собственной подтверждённой строки compatibility matrix.
9. При rollback удалить только AWG3 candidate и доказать неизменность AWG2,
   DB, web, bot, USA contour и постороннего Spain-сервиса.

## Отдельное ограничение имени

Protocol version не решает client-visible display name. Реальный Phase 12
import показал, что полный AmneziaVPN создаёт generic server name; оператор
после импорта вручную переименовывает профиль в exact `NEOBYATNAYA.NET`.
Конфиги, peers и ключи ради имени не регенерируются.

## Решение для запуска Phase 13

Первым Phase 13 slice становится AWG2/AWG3 version admission и isolated-runtime
design gate без live mutation. Device Passport и Desired/Observed/Drift не
отменяются: protocol version, client application/version и compatibility
evidence должны стать их полями, после чего работа продолжается на фактических
семи Spain slots.

## Written design checkpoint

Design записан в
`docs/superpowers/specs/2026-08-01-amn2-phase13-awg2-awg3-version-admission-isolated-runtime-design.ru.md`
и утверждён оператором exact-фразой 2026-08-01. Документ выбирает first-class isolated
`VpnRuntimeInstance`, exact client admission, separate typed renderers и
fail-closed compatibility evidence. Отдельный TDD implementation plan записан
в
`docs/superpowers/plans/2026-08-01-amn2-phase13-awg2-awg3-version-admission-isolated-runtime.md`
и ожидает отдельного разрешения на исполнение. Ни design approval, ни plan не
разрешают implementation, package build или live mutation.

В design также добавлен отдельный USA retirement/reuse notification gate. USA
остаётся rollback contour до подтверждённых Spain stability, device
acceptance, 14-day post-mutation observation, encrypted backup, independent
restore rehearsal, replacement rollback capacity, dependency audit и
secret-safe retirement plan. Readiness notification не является approval на
shutdown, wipe или reuse.
