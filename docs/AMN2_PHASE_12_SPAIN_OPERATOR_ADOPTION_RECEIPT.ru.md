# AMN2 Phase 12 — Spain operator adoption receipt

Дата фиксации: 2026-07-30.

## Итог

Spain runtime установлен и принят в операторский контур после точечного
исправления sandbox прав `amn2-spain-network.service`. Live smoke и equality
прошли. До полного закрытия Phase 12 остаётся только выдать 1–2 свежих
конфигурации и подтвердить подключение на реальном устройстве.

## Authoritative identities

- AMN2 source: `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
- USA production overlay и rollback contour:
  `0b858c5cdbc5b565cc265966a2edfe2d339d65e0`.
- Final local Spain package:
  SHA-256 `9F56EFDDBFAF8F3768112EED0B4AE3CA6A94178B7824A54FF10282FE572906D0`,
  `140093440` bytes.
- Manifest:
  SHA-256 `72061B9FD7F25B9661BCA49654CA3A08E7428F44E838D13BC7FFC9D9135D36C0`.
- Executor:
  SHA-256 `0A20AA67D75FDAF2AB3AE4DD59ED4AC6AA916CCCB4407A72CD6CFCEF8E335DF9`,
  `161269` bytes.
- Network unit:
  SHA-256 `C40D0C2C7440CE73A1104AF79D4267DC1A0EA86346407D7E2B9D1F3B4E164D4B`,
  `1057` bytes.
- Resource plan:
  SHA-256 `8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43`.

Package и executor собраны дважды byte-equal. Package verification и
descriptor-bound offline extraction прошли; извлечённый network unit совпадает
с live-approved SHA-256.

## Transaction audit

State-machine transaction
`4d64f73c80cce3ed0522e04569f6469641c9f1f5a65ca28742d68e9435a0f1be`
исторически остаётся `manual_recovery_required`. Это состояние не
переписывалось и не выдаётся за штатный success.

- transaction SHA-256:
  `5D160E67A9A223DCA396F52246CDF905056842BCDD2D1C283E87254C9E7B9E1D`;
- recovery capsule SHA-256:
  `0B78CC9A6B30F6D20EBE1C2679186D645CD5E76195200278499DCE4817012D6D`;
- network failure receipt SHA-256:
  `669E2B772A476193359CF4B5C1B2B6D22B90E148D93FD35A120937B883A66E84`.

Корневая причина: network unit имел только `CAP_NET_ADMIN`, но должен был
создать ledger в каталоге `/var/lib/amn2-spain` с UID/GID `61212` и mode
`0750`. Byte-approved unit содержит `SupplementaryGroups=amn2-spain` и
`CAP_DAC_OVERRIDE` вместе с `CAP_NET_ADMIN` в `CapabilityBoundingSet` и
`AmbientCapabilities`; sandbox-ограничения `ProtectSystem=strict` и
`ReadWritePaths` сохранены. Старый unit сохранён на Spain как
`/root/amn2-spain-network.service.pre-dac-fix`.

## Live acceptance

- `amn2-spain-docker.service`: active/running, enabled.
- `amn2-spain-network.service`: active/exited, enabled.
- `amn2-spain-web.service`: active/running, enabled.
- `amn2-spain-bot.service`: inactive/dead, static.
- Web listener: только `127.0.0.1:3031`.
- `/` возвращает redirect на `/login`; `/login` возвращает HTTP 200.
- `VPS_APPLY_ENABLED=false`.
- Clean DB: все проверенные AMN2 таблицы содержат `0` строк.
- Peers: `0`.
- AWG: container running, interface up, UDP listen port `30001`.
- Route: `10.212.12.0/24 via 172.29.251.2 dev amn2spbr0`.
- AWG не перезапускался и не пересоздавался после успешного запуска.
- Retained `/opt/amn2-spain-package` отсутствует.

## Foreign equality

- baseline evidence SHA-256:
  `BBC652D244CCF9C581FC9D369A114BF5AE6457E531C7A2B8F450AFF9C402E101`;
- post-cleanup evidence SHA-256:
  `A2B4622670DF7CE3898ACB151419640ABE1746EFF055089EBE075FCE0FFADCE4`;
- persistent entries: `150`;
- persistent before/after SHA-256:
  `3DA96B893428858FD3DDC705E19E41A87877E0F98C09B1A40DDE6E96B6346D61`;
- persistent equality: `true`;
- volatile before/after: `0/2`;
- post-only allowlisted entries:
  `amn2-spain-web.service`, `amn2-spain-network.service`;
- final equality receipt SHA-256:
  `5D5A1B8DE749E70940938D3CA4F854E58823E8B676C348131A48175E653F0836`.

Посторонний Spain-сервис не останавливался и не изменялся. USA data не
переносились и не удалялись.

## Незакрытый операторский gate

Нужен список получателей и количество fresh slots для выдачи 1–2 тестовых
конфигураций. Формат имени: `NEOBYATNAYA.NET — recipient — slot/device`;
device может быть `unknown`; expiry по умолчанию indefinite. После проверки
подключения на реальном устройстве можно оформить final closeout Phase 12.

На момент финальной локальной синхронизации SSH к Spain дважды завершился до
аутентификации (`connect timeout`, затем `banner exchange timeout`). Поэтому
новый authoritative package `9F56…` локально полностью проверен, но обновление
remote artifact cache с предыдущего package `EF772…` не подтверждено. Это не
влияет на уже работающий live unit: его SHA-256 подтверждён отдельно.
