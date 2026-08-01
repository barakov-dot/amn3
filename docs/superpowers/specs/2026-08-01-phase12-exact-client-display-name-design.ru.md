# Phase 12 — exact `NEOBYATNAYA.NET` client display name correction / Точное имя в клиенте

## Решение / Decision

Каждый уже выданный slot получает отдельный уникально названный ZIP-архив.
Внутри архива находится ровно один исходный config-файл под точным именем
`NEOBYATNAYA.NET.conf`. Байты config не изменяются. Recipient, slot, device,
device ID и исходный SHA-256 остаются во внешнем package manifest и имени
архива, но не добавляются к имени внутреннего `.conf`.

Each already issued slot receives one uniquely named ZIP archive. The archive
contains exactly one original config file named `NEOBYATNAYA.NET.conf`. Config
bytes remain unchanged. Recipient, slot, device, device ID, and the original
SHA-256 remain in the outer package manifest and archive name, but are not
appended to the inner `.conf` filename.

## Рассмотренные варианты / Considered approaches

1. **Уникальный ZIP на slot — выбран.** Исключает collision между несколькими
   slots, сохраняет точное inner filename и даёт проверяемый outer identity.
2. Уникальная директория на slot с одинаковым inner filename. Технически
   корректно, но хуже переносится и легче случайно смешивается оператором.
3. Переименовать raw `.conf` в одно общее имя. Отклонено: три файла столкнутся
   в одной директории и потеряют очевидную slot identity.

## Authoritative input / Авторитетный вход

- Request: `phase12-spain-sool-test-20260730-001`.
- Recipient: `SooL`.
- Existing devices: `Проектор`, `Телевизор`, `ARM-HOME`.
- Source directory:
  `private-artifacts/phase12-spain-config-issuance-20260730/configs`.
- Existing generated config bytes are immutable inputs. The correction must
  not call issuance, key generation, peer apply, revoke, or database writes.

## Package contract / Контракт пакета

Для каждого manifest item формируется один архив:

`NEOBYATNAYA.NET--SooL--<safe-device>--d<device-id>.zip`

В архиве допускаются только:

- `NEOBYATNAYA.NET.conf` — byte-equal соответствующему existing config;
- `package-manifest.json` — canonical UTF-8 JSON без secret config material.

Manifest schema: `amn2.phase12-client-display-package.v1`. Required fields:
`request_id`, `recipient_label`, `device_label`, `device_id`, `slot_identity`,
`inner_filename`, `config_sha256`, `config_bytes`, `archive_filename`.
`inner_filename` всегда exact `NEOBYATNAYA.NET.conf`. `slot_identity` и
`archive_filename` уникальны в batch. Manifest не содержит private key, PSK,
config text, QR или import URI.

ZIP создаётся детерминированно: фиксированная timestamp, stable entry order,
UTF-8 names, `ZIP_STORED`, explicit regular-file modes. Existing source file
не переименовывается и не удаляется.

## Collision and failure policy / Collision и ошибки

- duplicate recipient/device/device-ID/slot identity — fail closed;
- missing or unexpected source config — fail closed;
- existing output archive or output directory — fail closed;
- source SHA/size drift during read — fail closed;
- any archive member other than the two allowed members — verification fail;
- any inner config byte difference — verification fail;
- logs and receipts may contain only paths, sizes, identities and hashes;
  config bytes and secret-like lines are never printed.

## Client acceptance / Приёмка в AmneziaVPN

Оператор извлекает один selected archive и импортирует его единственный
`NEOBYATNAYA.NET.conf` в реальный AmneziaVPN. Приёмка требует двух визуальных
подтверждений:

1. большой заголовок профиля — exact `NEOBYATNAYA.NET`;
2. строка в списке серверов — exact `NEOBYATNAYA.NET`.

Ни recipient, ни device, ни slot, ни `d<id>` не должны появляться в этих двух
display surfaces. Первый real-client check выполняется на одном архиве;
остальные пакеты принимаются по тому же byte/name contract.

## Tests and evidence / Тесты и доказательства

- RED/GREEN tests для exact inner filename, byte equality, unique outer names,
  deterministic archives, collision rejection, overwrite rejection и
  secret-free manifest;
- package verifier повторно открывает каждый ZIP и сверяет inner bytes с
  immutable source SHA-256;
- scoped tests, затем полный repository test suite;
- `git diff --check`, secret-pattern review и manual security diff review;
- Phase 12 status, adoption receipt и Phase 13 handoff синхронизируются только
  с hashes/metadata, без secret config material.

## Non-goals / Вне scope

- regeneration или replacement ключей, peers и configs;
- изменение Spain DB, AWG container или live peer set;
- выдача `ARM-WORK`, `NOTEBOOK`, `IPAD`, `IPHONE`;
- Spain reboot до отдельного exact controlled-reboot approval;
- изменение foreign Spain service или USA rollback contour.
