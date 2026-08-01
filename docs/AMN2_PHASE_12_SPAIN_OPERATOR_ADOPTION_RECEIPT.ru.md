# AMN2 Phase 12 — Spain operator adoption receipt

## Final acceptance override

Phase 12 is accepted. Controlled reboot persistence and ARM-HOME full data
passed. Final live audit receipt SHA-256:
`B1F12A5A18871C82F855F17CDC60ABA133B542CF2B68CF049AE64E533761F0C5`.
It proves users `1`, active/indefinite devices `7/7`, completed/noncompleted
receipts `7/0`, active passports `7`, request 002 completed receipts `4`, DB
integrity `ok`, foreign-key issues `0`, and exact DB/persistent/live peer sets
`7/7/7`. AWG is running with stable restart count `59`; container forwarding
is `1`; Docker/network/forward-compat/web are active, bot is inactive, and web
is loopback-only. Exactly one instance of each approved tagged rule exists.

Final foreign equality receipt SHA-256:
`BC9065B3FA7CAB40F5EEFEBBFD8093F2D62477E972777FE665E8D9F6028AA704`.
Persistent entries `153`, changed `0`, stable before/after SHA-256
`F5767F361A9441DD4B5361C07DA164A3059E0D1347D5217594534797D367B7E8`;
volatile `1/0`. Nine exact request-002 staging files were checksum-verified and
removed after download. Foreign service and USA data were not mutated.

The accepted slot set for `SooL` is `Проектор`, `Телевизор`, `ARM-HOME`,
`ARM-WORK`, `NOTEBOOK`, `IPAD`, `IPHONE`, all indefinite. The final four were
issued with a one-time process-only quota override to `7`; runtime default
remains `5`. AmneziaVPN requires manual rename to exact `NEOBYATNAYA.NET`.

Authoritative source/Spain overlay:
`55dc243b8e6c6bdb57f8301b56326e4cd4072d19` /
`f1bf099ddb47da26a4080714376babaf5b0de92c`. USA overlay
`0b858c5cdbc5b565cc265966a2edfe2d339d65e0` remains rollback.

Дата фиксации: 2026-08-01.

## Реальный результат client display-name

ARM-HOME импортирован в полный Windows-клиент AmneziaVPN. Автоматический
результат: `Server 2`, то есть exact filename не управляет display name этого
клиента. Оператор вручную переименовал server в `NEOBYATNAYA.NET` и подтвердил
connected screen с exact большим заголовком. Итог:

- `automatic_import_name=failed`;
- `manual_rename=passed`;
- `config_peer_key_regeneration=false`;
- `live_spain_mutation=false`.

Corrected receipt v2 SHA-256:
`66E4ACCABAA7600EAB00A1BA207F04813C46CBFFD09948F617F049FFF6BF4F0F`;
strategy: `manual_rename_required`. Следующий gate — controlled reboot.

## Historical exact-filename packaging

Три existing config artifacts переупакованы byte-for-byte без regeneration
ключей/peers/configs и без изменения DB/live Spain. Каждый уникальный per-slot
ZIP содержит exact `NEOBYATNAYA.NET.conf` и secret-free
`package-manifest.json`. Package receipt SHA-256:
`2A0375F8D14ED76FA5799E466A6F533D8833CB459530DB03D832AE535BE9C3BC`.

- `SooL/Проектор/d1`: archive SHA-256
  `7E097939F42299BD78961A80D857447F5BB646CEE24F782989D135DE065844EF`;
- `SooL/Телевизор/d2`: archive SHA-256
  `6F7F8C55FA92F6745713701954AA7929BFABA3D1AFB5647003EB07BAB8E89377`;
- `SooL/ARM-HOME/d3`: archive SHA-256
  `844B8AD650A3A70F5AA672CEDC44C1AB0B42A580971215C11D09D697BE93E207`.

Build/independent verify доказали exact inner filename, unique outer identities
и byte equality всех трёх 477-byte configs. Tests: focused `7 passed`, Phase 12
`378 passed, 5 skipped`, tracked repository full `587 passed, 5 skipped`.
Остаётся real AmneziaVPN import: big header и servers list должны показать
exact `NEOBYATNAYA.NET` без suffix. После этого выполняется отдельно
разрешённый controlled reboot persistence test; reboot ещё не выполнялся.

## Итог

Spain runtime установлен и принят в операторский контур после точечного
исправления sandbox прав `amn2-spain-network.service`. Live smoke и equality
прошли. Три fresh-конфигурации выданы recipient `SooL`; ARM-HOME full data
прошёл. До полного закрытия Phase 12 остаются exact display-name import и
controlled reboot persistence confirmation.

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
- Fresh DB до первой выдачи: все проверенные AMN2 таблицы содержали `0` строк.
- После выдачи: users `1`, active devices `3`, completed receipts `3`, failed
  receipts `0`, persistent/live peers `3/3`.
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

## Fresh config issuance

- Request: `phase12-spain-sool-test-20260730-001`, status `completed`.
- Recipient: `SooL`.
- Devices: `Проектор`, `Телевизор`, `ARM-HOME`.
- Expiry: indefinite для всех трёх.
- Persistent/live peer sets: exact equal; SHA-256
  `E111BFDAFD17D3762EC9C1AC03557B469F6AE5FE0A06A68F9A9C52138B7C08EA`.
- AWG container restart count после выдачи: `0`.
- Три local artifacts проверены byte-for-byte и сохранены в private-artifacts;
  их содержимое и ключи в docs/git не публикуются.
- Восемь exact временных `/root` staging/artifact files удалены после
  подтверждённого скачивания; runtime, DB и peers при cleanup не менялись.

Свежий post-issuance collector SHA-256:
`4705B22EC68A0EA2820BDE82E41DB8D364EBD41D884A2A3D080FFE214CBC4D8D`;
evidence SHA-256:
`60EB160C333BD08F778908A4D046A4841F2E5EF0464E7E52248A94833D2D041B`.
Equality относительно принятого post-cleanup evidence:

- persistent entries: `152`;
- changed persistent entries: `0`;
- persistent before/after SHA-256:
  `93076664864CB4E9A61E011CA074BD515016D3D08855C97FFB1BBB2932ED270D`;
- volatile before/after: `0/0`;
- receipt SHA-256:
  `B012368C6A18EAEE6930024CCF01988A23616B9DF6B9232ACDA1E153648D5392`.

## Незакрытый операторский gate

Импортировать один из трёх выданных конфигов и подтвердить реальное
подключение. Рекомендованный первый тест — `ARM-HOME`. После подтверждения
можно оформить final closeout Phase 12. `ARM-WORK`, `NOTEBOOK`, `IPAD`,
`IPHONE` до успешного теста не создаются.

После двух временных SSH transport timeout соединение восстановилось. Remote
artifact cache обновлён checksum-bound delta из предыдущего package `EF772…`
и подтверждён полным readback:

- `/root/amn2-spain-phase12-install.tar`:
  `9F56EFDDBFAF8F3768112EED0B4AE3CA6A94178B7824A54FF10282FE572906D0`,
  `140093440` bytes;
- `/root/amn2-spain-phase12-executor.pyz`:
  `0A20AA67D75FDAF2AB3AE4DD59ED4AC6AA916CCCB4407A72CD6CFCEF8E335DF9`,
  `161269` bytes.

После cache replacement Docker/network/web остались active, bot — inactive;
service restart/recreate не выполнялся.
