# Локальная операторская выдача бессрочных неназначенных access slots

Дата: 2026-07-20

Статус: written design, ожидает review оператора
Утверждённый design authority:
`APPROVE_LOCAL_OPERATOR_CONFIG_DEFAULT_INDEFINITE_WITH_EXPLICIT_OPTIONAL_EXPIRY_AND_MULTI_UNASSIGNED_SLOTS_DESIGN`

## 1. Цель

AMN2 должен позволять оператору через локальный CLI заранее выпустить одному
получателю несколько независимых конфигов, даже если физические устройства и
платформы ещё неизвестны. Все такие конфиги активны сразу после применения,
по умолчанию бессрочны и независимо отключаются или отзываются.

Этот workflow не требует web-admin для выпуска. Web и bot позже читают те же
безопасные записи БД, но не получают новый public/self-service write surface.

## 2. Утверждённый пользовательский сценарий

Оператор сообщает получателя и количество, например:

```text
Получатель: Иван
Количество: 4
Срок: бессрочно
```

После dry-run и отдельного live approval создаются четыре независимых peer и
четыре private config artifacts:

```text
NEOBYATNAYA.NET-Ivan-01.conf
NEOBYATNAYA.NET-Ivan-02.conf
NEOBYATNAYA.NET-Ivan-03.conf
NEOBYATNAYA.NET-Ivan-04.conf
```

Получатель сам решает, какой файл установить на какое устройство. AMN2 не
утверждает, что знает или доказал физическое устройство. Поздняя операторская
привязка к Device Passport допустима, но необязательна.

## 3. Основные продуктовые решения

### 3.1 Access slot не равен Physical Device Passport

Существующая строка `devices` технически хранит VPN credential/peer и остаётся
локальной точкой управления access lifecycle. Для нового режима она считается
`access slot`, пока не появилась достоверная операторская информация об
устройстве.

Новый `assignment_mode=recipient_unassigned` означает:

- peer создан и может быть `active`, `disabled` или `revoked`;
- `device_passports` row отсутствует;
- platform, client type и physical-device identity не выдумываются;
- один конфиг может быть скопирован пользователем на несколько endpoint, и
  AMN2 без собственного доверенного endpoint agent не может это запретить или
  считать аппаратно подтверждённым назначением;
- такой slot учитывается в лимите активных доступов получателя.

Существующие `dedicated_device` и `owner_shared` semantics не изменяются.

### 3.2 Expiry policy

Для локального `admin-config issue-manifest` отсутствие срока означает:

```text
duration_days=null
expires_at=null
expiry_policy=indefinite
```

Нельзя молча подставлять прежние 30 дней. Срок появляется только при явном
указании одного из взаимоисключающих значений:

- `duration_days`: положительное целое число, отсчёт от момента apply;
- `expires_at`: валидная будущая UTC datetime.

Root-level policy применяется ко всей партии, item-level policy может её
переопределить. Одновременные `duration_days` и `expires_at` запрещены.
Тарифные, order и bot flows сохраняют свои существующие сроковые контракты.

В `devices` хранится явный `expiry_policy` со значениями `duration`,
`absolute` или `indefinite`. Это не позволяет выводить бессрочность только из
случайного `NULL` и делает status/admin projection однозначной. Существующие
строки мигрируют как `duration`; новый operator batch без срока записывает
`indefinite`; explicit UTC deadline записывает `absolute`.

`indefinite` не означает неотзываемый: manual disable/revoke остаются
обязательными независимыми операциями.

### 3.3 Multi-slot manifest

Manifest поддерживает два режима item:

1. `recipient_unassigned`: обязательны `recipient_label` и `quantity`; поля
   физического устройства и платформы отсутствуют.
2. `dedicated_device`: сохраняется совместимый путь с явными
   `recipient_label`, `device_label` и `platform`.

Пример нового безопасного input:

```json
{
  "request_id": "spain-initial-issuance-001",
  "server": "Spain-Madrid",
  "expiry": {"kind": "indefinite"},
  "items": [
    {
      "mode": "recipient_unassigned",
      "recipient_label": "Иван",
      "quantity": 4
    }
  ]
}
```

`quantity` находится в диапазоне `1..100`, а сумма развёрнутых slots во всей
заявке — `1..100`. Canonical validation полностью разворачивает manifest до
remote или DB mutation. Нормализованные дубликаты, превышение лимита,
неподдерживаемые поля, конфликт expiry и server mismatch закрывают всю заявку.

## 4. Имена и последовательность

Filename строится из бренда, operator recipient label и стабильного порядкового
номера. Транслитерация и Windows-safe ограничения повторяют текущий
`config_identity` contract.

Последовательность выбирается под DB transaction и не переиспользует уже
занятые номера получателя. Внутри одного request каждому развёрнутому slot
соответствует стабильный `item_index` и `slot_sequence`.

Повтор с тем же `request_id` и теми же canonical bytes возвращает прежние
receipts и не создаёт peer повторно. Изменение quantity, recipient, expiry,
server или mode при прежнем `request_id` отклоняется до mutation.

## 5. Состояние данных и миграция

### 5.1 `devices`

Необходимо:

- добавить `recipient_unassigned` в CHECK `assignment_mode`;
- добавить `expiry_policy` с CHECK `duration|absolute|indefinite`;
- добавить nullable `config_fingerprint` формата `sha256:<64 hex>`; для всех
  новых locally generated slots он обязателен, но legacy/external-only строки
  могут остаться `NULL`;
- разрешить `duration_days IS NULL` и согласовать три состояния: `duration`
  требует положительный `duration_days` и вычисленный `expires_at`, `absolute`
  требует `duration_days IS NULL` и явный `expires_at`, `indefinite` требует
  оба значения `NULL`;
- применять default `indefinite` ко всем режимам локального operator batch,
  включая `dedicated_device`, если срок не указан явно;
- сохранить `status='active'` после успешного peer apply;
- хранить slot display name/sequence без заявления о physical device.

Миграция должна пересоздать SQLite table атомарно, сохранить все существующие
строки и индексы и пройти `foreign_key_check`. Существующие положительные
`duration_days` и `expires_at` не переписываются и получают
`expiry_policy='duration'`.

### 5.2 Issuance requests и receipts

Receipt completion для `recipient_unassigned` требует:

- `recipient_user_id`, `device_id` и `config_filename`;
- `passport_device_id IS NULL`;
- `assignment_mode='recipient_unassigned'` и стабильный `slot_sequence`;
- безопасный `config_fingerprint` доступен через связанную access-slot запись;
- отсутствие raw config, private key и PSK в receipt/audit JSON.

Для `dedicated_device` прежнее требование `passport_device_id IS NOT NULL`
сохраняется. Request fingerprint включает canonical expanded slots и expiry.

### 5.3 Device Passport

При первичной unassigned issuance паспорт не создаётся. Опциональная поздняя
привязка:

- требует существующий active/disabled, но не revoked slot;
- принимает явные device label, platform, official client type и import method;
- идемпотентна по отдельному assignment request id;
- создаёт ровно один passport, связанный с существующим local `device_id`;
- использует сохранённый безопасный `config_fingerprint`, не читая raw `.conf`
  и не выводя encrypted secrets;
- не меняет уже переданный filename или cryptographic peer identity;
- повтор с конфликтующими сведениями закрывается без перезаписи.

Исправление ошибочной поздней привязки не входит в первый MVP и требует
отдельной audited rebind/revoke policy.

## 6. Apply flow

```text
load manifest
  -> strict canonical validation and expansion
  -> dry-run plan without DB/VPS mutation
  -> exact live write gate
  -> configured-admin admission
  -> full-batch quota and collision preflight
  -> create/reuse recipient
  -> for each stable slot: allocate IP and keys
  -> apply one peer to selected server
  -> persist access slot and receipt
  -> write private config artifact create-new
  -> record redacted admin audit
  -> return safe receipt summary
```

Dry-run показывает request id, server, получателей, expanded slot count,
filename preview, expiry policy и ожидаемые quota deltas. Он не генерирует
ключи, не создаёт файлы и не обращается к VPS.

## 7. Partial failure и rollback boundary

Текущий peer lifecycle допускает состояние remote-applied/local-failed.
Новый workflow сохраняет fail-closed последовательное выполнение:

- полный admission/preflight выполняется до первого peer;
- при ошибке текущий slot получает безопасный partial-failure receipt;
- последующие slots не запускаются;
- уже завершённые slots не создаются повторно при resume;
- blind DB restore и массовое удаление peers запрещены;
- recovery action строится по точному operation id и observed peer state;
- raw config material не включается в error/audit output.

Автоматический rollback ранее успешно созданных slots всей партии не
выполняется: это могло бы удалить уже переданный доступ. Оператор получает
completed/failed границу и отдельно решает resume либо revoke.

## 8. Disable и revoke

Каждый slot управляется независимо через существующий local device/access id:

- `disable` убирает или блокирует peer согласно существующему mutation contract,
  сохраняя запись и audit;
- `revoke` является терминальным, сохраняет reason/time и не разрешает позднюю
  assignment;
- действия по одному slot не меняют остальные slots того же получателя;
- бессрочный slot остаётся active до disable/revoke, а не до фонового expiry.

## 9. Secret и delivery boundary

- `.conf` создаются только как private create-new artifacts вне Git;
- CLI JSON содержит filename и безопасные IDs, но не config payload;
- private key, PSK, raw config, SSH password и target-private data не попадают
  в Git, logs, receipts, audit или status docs;
- повторная доставка использует существующий secret-safe handoff contract;
- public/self-service generation остаётся закрытой;
- все live peer mutations требуют отдельного exact gate после Spain install.

## 10. Acceptance criteria

1. Manifest с одним получателем и `quantity=4` dry-run разворачивается в четыре
   стабильных filename без mutation.
2. Apply создаёт четыре разных peer, IP, encrypted secrets, receipts и private
   artifacts, все с `expires_at/duration_days = NULL`.
3. Ни один unassigned slot не создаёт Device Passport.
4. Четыре slots учитываются как четыре активных доступа и не обходят quota.
5. Повтор идентичного request не создаёт пятый peer или второй artifact.
6. Изменённый повтор fail-closed до DB/VPS mutation.
7. Явный `duration_days` и явный `expires_at` работают; их конфликт отклоняется.
8. Disable/revoke одного slot не влияет на остальные три.
9. Поздняя assignment создаёт один passport без смены peer/filename; conflicting
   replay отклоняется.
10. Existing dedicated-device, plan, order, bot, backup/restore и migrations
    проходят regression tests без изменения сроковой семантики.
11. Safe output и security scan не содержат config/private/PSK material.

## 11. Не входит в scope

- автоматическое определение физического устройства;
- hardware attestation, MDM или собственный endpoint agent;
- запрет копирования одного `.conf` на несколько устройств;
- public config generation;
- изменение тарифных сроков и bot purchase flow;
- live Spain install, preflight или peer generation в design/spec задаче;
- миграция старых USA peer/config;
- автоматический rebind ошибочно назначенного паспорта.

## 12. English contract summary

The local operator batch workflow may issue multiple immediately active VPN
access slots to one named recipient before any physical device or platform is
known. Operator-issued configs are indefinite by default (`expires_at` and
`duration_days` are null); expiry exists only when explicitly specified per
batch or item. Each slot is independently disableable and revocable.

An unassigned access slot is not a Device Passport. No passport is created and
no endpoint facts are inferred during issuance. A later explicit, idempotent
operator assignment may attach exactly one passport to the existing access
record without rotating the peer or renaming the already delivered file.

The manifest expands quantity deterministically, validates the entire batch
before mutation, reserves stable numbered filenames, enforces quota, and binds
replay to canonical recipient/server/expiry/slot inputs. Dry-run is mutation
free. Apply remains configured-admin-only and exact-live-gate-protected. Raw
configs and cryptographic secrets remain private artifacts and never enter Git,
safe JSON, receipts, audit metadata, or status documentation.
