# AMN2 Phase 13 — AWG2/AWG3 version admission and isolated runtime design

Дата: 2026-08-01
Статус: `written-spec-pending-operator-review`
Тип: bilingual design-only contract; Russian text is authoritative, English
contract summary follows below.

## 1. Разрешение и строгая граница

Этот документ проектирует локальный product/engineering contract. Он не
разрешает implementation, SSH, VPS, Docker, firewall, systemd, config
generation/delivery, peer mutation, reboot, Telegram или public exposure.

Нельзя останавливать, перезапускать или пересоздавать текущий Spain AWG2 для
тестов. USA нельзя отключать, очищать или перепрофилировать. Посторонний
Spain-сервис нельзя останавливать или изменять.

Следующие действия требуют отдельных решений в таком порядке:

1. operator review и утверждение этого записанного design;
2. отдельный TDD implementation plan;
3. local-only implementation и тесты;
4. checksum-bound package и read-only Spain preflight;
5. отдельное exact live approval для каждого mutation gate.

## 2. Authoritative baseline

- AMN2 source: `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
- Spain operational overlay:
  `f1bf099ddb47da26a4080714376babaf5b0de92c`.
- USA production overlay:
  `0b858c5cdbc5b565cc265966a2edfe2d339d65e0`.
- Spain является primary runtime; USA остаётся неизменённым rollback contour.
- Spain d1–d7 являются принятым AWG2 baseline и не перевыпускаются
  автоматически.
- Production AWG3 issuance закрыта: принятого Spain AWG3
  server/config/data/reboot/rollback evidence ещё нет.
- Final Phase 12 foreign equality receipt:
  `BC9065B3FA7CAB40F5EEFEBBFD8093F2D62477E972777FE665E8D9F6028AA704`.
- Persistent foreign entries: `153`; changed: `0`; stable before/after:
  `F5767F361A9441DD4B5361C07DA164A3059E0D1347D5217594534797D367B7E8`.

Официальные источники подтверждают только readiness inputs:

- [AmneziaVPN 5.0.0.5](https://github.com/amnezia-vpn/amnezia-client/releases/tag/5.0.0.5)
  заявляет AWG3 support;
- [официальный client commit](https://github.com/amnezia-vpn/amnezia-client/commit/5e9def4184f0799f9984d2bbde5d4237dc649abc)
  добавляет AWG3 fields и client runtime integration;
- [amneziawg-go v3.0.1 contract](https://github.com/amnezia-vpn/amneziawg-go/blob/v3.0.1/README.md)
  определяет `HeaderProtectionKey` как AWG3+ server-side parameter, который
  должен совпадать на сервере и клиенте;
- [DefaultVPN 2.0.0 App Store history](https://apps.apple.com/us/app/defaultvpn/id6744725017)
  заявляет AWG3 support для распространяемого iOS build.

Release claim или наличие parser fields не являются доказательством Spain
server readiness или совместимости конкретного platform/build.

## 3. Цели

1. Разделить protocol selection, client compatibility и runtime readiness.
2. Разрешать новые выдачи только для явно выбранного `AWG2` или `AWG3`.
3. Fail closed при неизвестном приложении, платформе, версии или evidence.
4. Оставить текущий Spain AWG2 и семь профилей неизменными.
5. Проектировать AWG3 как изолированный runtime instance с собственными
   interface, UDP port, CIDR/IPAM, lifecycle и rollback.
6. Связать protocol/client evidence с Device Passport, issuance receipt и
   Desired/Observed/Drift без публикации secret material.
7. Определить точный gate, после которого оператору можно сообщить, что USA
   готов к отдельному отключению и перепрофилированию.

## 4. Не-цели

- in-place upgrade текущего Spain AWG2;
- преобразование AWG2 config добавлением AWG3-полей;
- массовый reissue или migration d1–d7;
- новая AWG1/legacy issuance;
- удаление существующих legacy profiles;
- public/self-service delivery, bot cutover или broad write API;
- auto-remediation Desired/Observed/Drift;
- изменение quota default `5`;
- отключение или очистка USA в рамках Phase 13 design/implementation slice.

## 5. Рассмотренные архитектурные варианты

### A. First-class `VpnRuntimeInstance` — принято

Один физический server содержит несколько изолированных VPN runtime
instances. AWG2 и AWG3 получают отдельные identity, interface, UDP port, CIDR,
runtime state и rollback boundary.

Преимущества: корректная multi-instance/fleet модель, явные конфликты,
изолированный rollback и отсутствие ложного представления, что один host —
это два VPS. Цена — additive schema и отдельный runtime planner.

### B. Второй логический server alias на том же Spain host — отклонено

Меньше первоначальных изменений, но server inventory, capacity, foreign
equality и rollback начинают смешивать физический host и runtime instance.

### C. In-place AWG2→AWG3 — запрещено

Этот вариант затрагивает accepted AWG2, создаёт риск для d1–d7 и не даёт
независимого rollback.

## 6. Domain model

### 6.1 Protocol classification

Canonical persisted field: `protocol_version`.

Допустимые значения для новых issuance: `awg2`, `awg3`.

Исторические строки без доказанной версии сохраняют `NULL` как
`unclassified_legacy`. `NULL` не является третьим issuance target и никогда
не допускается для новой выдачи. Нельзя автоматически backfill всех старых
строк значением `awg2`.

Spain d1–d7 могут быть явно backfill как `awg2` только по принятому Phase 12
config/runtime evidence, без изменения config bytes, peers или keys.

### 6.2 Exact client identity

Admission input обязан содержать:

- `client_application`: точное нормализованное приложение;
- `client_platform`: точная платформа;
- `client_version`: точная версия/build string;
- recipient и количество slots;
- expiry policy.

Существующий `official_client_type` остаётся canonical stored application
field; новый DTO использует понятное имя `client_application` и маппится на
него. Дублирующую DB-колонку создавать не нужно.

Добавляется `client_identity_evidence_status`:

- `unknown` — историческое или технически подставленное значение;
- `operator_declared` — exact application/platform/version сообщил оператор;
- `verified` — exact row имеет принятое compatibility evidence.

Текущие hardcoded `amnezia_vpn` записи нельзя считать `verified` без
отдельного evidence. Неизвестные версии d1–d7 остаются неизвестными.

### 6.3 Compatibility evidence

`ClientCompatibilityEvidence` — append-only safe record:

| Field | Contract |
|---|---|
| `evidence_id` | stable internal ID |
| `application` | normalized exact application |
| `platform` | exact platform |
| `client_version` | exact version/build |
| `protocol_version` | `awg2` or `awg3` |
| `source_kind` | official release, runtime contract, manual import, handshake, full data, reboot |
| `status` | `claimed`, `passed`, `failed`, `superseded` |
| `observed_at` | freshness timestamp |
| `safe_reference` | source URL or secret-free receipt/hash |
| `scope` | exact build/platform limits |

Official release evidence создаёт только `claimed`. Для `verified` AWG3 row
обязательны принятые import и full-data evidence на exact platform/build.

Raw configs, keys, PSK, QR, `vpn://`, endpoints и private identifiers в этой
таблице запрещены.

### 6.4 Admission decision

`ProtocolAdmissionService` получает request, compatibility evidence и runtime
capabilities, но ничего не генерирует и не изменяет.

Результаты:

- `admitted_awg2`;
- `candidate_awg3`;
- `blocked_unknown_client`;
- `blocked_unverified_version`;
- `blocked_unsupported_platform`;
- `blocked_runtime_not_accepted`;
- `blocked_evidence_stale_or_failed`.

Rules:

1. OS или слова «последняя версия» никогда не выбирают protocol.
2. Неизвестный/unverified client не получает автоматический AWG2 fallback.
3. AWG2 допускается только для известной принятой compatibility row и
   accepted AWG2 runtime.
4. AWG3 становится issuance-eligible только при одновременном наличии
   accepted AWG3 runtime и passed exact client row.
5. До live acceptance AWG3 решение остаётся `candidate_awg3`; config
   generation закрыта.

### 6.5 Runtime instance

Новая child entity `vpn_runtime_instances`:

| Field | Contract |
|---|---|
| `runtime_instance_id` | stable generated ID |
| `server_id` | physical host parent |
| `protocol_version` | `awg2` or `awg3` |
| `runtime_version` | exact server runtime build/tag/digest |
| `interface_name` | unique on host |
| `udp_port` | unique on host |
| `vpn_cidr` | non-overlapping on host/fleet scope |
| `container_name` / `service_name` | isolated runtime identity |
| `config_path` | isolated path identity, never raw config |
| `lifecycle_state` | `planned`, `candidate`, `accepted`, `rollback_pending`, `retired` |
| `acceptance_receipt` | secret-free checksum/reference |

DB uniqueness покрывает `(server_id, interface_name)` и
`(server_id, udp_port)`. CIDR overlap проверяет один deterministic planner
внутри transaction; live observation добавляется только read-only preflight.

Текущий Spain AWG2 может получить `accepted` runtime row только через
evidence-bound migration. Создание строки не разрешает и не выполняет runtime
mutation.

### 6.6 Protocol-specific rendering

AWG2 и AWG3 используют разные typed input models и renderers. Generic template
не может принять AWG3-only fields для AWG2.

`HeaderProtectionKey` — secret-bearing server/client material. Raw value:

- хранится только через существующий encrypted/external secret boundary;
- передаётся renderer по secret reference;
- не попадает в passport, receipt, audit, logs, docs или exceptions;
- в safe evidence допускает только domain-separated fingerprint.

Timing/padding fields являются protocol config material и также не выводятся в
safe metadata целиком.

### 6.7 Passport, receipt и Desired/Observed/Drift

Device Passport расширяется следующими safe facts:

- `protocol_version`;
- `runtime_instance_id`;
- `client_identity_evidence_status`;
- `compatibility_evidence_id`;
- `compatibility_status` и `verified_at`.

Issuance receipt фиксирует protocol/runtime/evidence IDs до config generation.
Idempotent retry с изменённой application/platform/version/protocol tuple
отклоняется как fingerprint mismatch.

Desired state содержит expected protocol/runtime/peer assignment. Observed
state содержит только read-only observed runtime/protocol identity и safe peer
fingerprints. Новые drift reasons:

- `protocol_version_mismatch`;
- `runtime_instance_mismatch`;
- `compatibility_evidence_missing`;
- `compatibility_evidence_stale`;
- `runtime_not_accepted`.

Диагностика не меняет state и не запускает auto-remediation.

## 7. End-to-end data flow

1. Оператор вводит exact application, platform, version, recipient, slots и
   expiry.
2. Input normalizer не угадывает отсутствующие значения.
3. Compatibility registry находит exact evidence row.
4. Admission service проверяет protocol и accepted runtime instance.
5. До passed admission никакие keys, peers или configs не создаются.
6. Issuance request fingerprint связывает exact client/protocol/runtime tuple.
7. Protocol-specific renderer получает secret references только после admit.
8. Receipt и Passport сохраняют safe evidence IDs и fingerprints.
9. Read-only observer формирует Desired/Observed/Drift snapshot.

## 8. Isolated AWG3 live-gate sequence

Этот раздел определяет будущий порядок, но не разрешает его выполнение.

1. Local TDD implementation и existing-AWG2 non-regression.
2. Checksum-bound package с exact source/runtime identities.
3. Read-only Spain capacity, UDP port, interface, CIDR/IPAM, Docker/systemd и
   foreign-service preflight.
4. Exact live approval на создание только isolated AWG3 candidate.
5. Post-deploy equality: AWG2, DB, web, bot, USA и foreign service unchanged.
6. Real-device matrix:
   - exact AmneziaVPN build on Windows;
   - exact AmneziaVPN build on Android;
   - exact DefaultVPN build on iOS;
   - Android TV и другие clients только своей accepted row.
7. Import, handshake и full-data evidence для каждой accepted row.
8. Отдельный controlled reboot approval и persistence verification без
   остановки/пересоздания AWG2 ради теста.
9. Rollback rehearsal удаляет только AWG3 candidate и доказывает equality.
10. Production AWG3 требует нового approval и повторного accepted deployment
    после rehearsal; старое rollback approval не переиспользуется.

## 9. Failure and rollback contract

Stop lines до mutation:

- unknown/unverified client identity;
- missing/stale/failed compatibility evidence;
- occupied UDP port или interface;
- overlapping CIDR;
- ambiguous runtime ownership;
- foreign baseline mismatch;
- AWG2 baseline mismatch;
- checksum/source/runtime identity mismatch.

Rollback target всегда exact `runtime_instance_id`. Запрещены wildcard cleanup,
container family cleanup и shared path deletion. Rollback receipt доказывает:

- AWG3 candidate absent;
- AWG2 persistent/live peers unchanged;
- AWG2 restart count не изменён неожиданно;
- DB/web/bot state unchanged;
- USA not contacted or changed;
- foreign persistent equality passed.

## 10. USA retirement/reuse readiness notification gate

USA остаётся rollback contour до отдельного завершённого gate. AWG3 readiness
сама по себе не разрешает отключение USA.

Все следующие условия обязательны:

1. Spain AWG2 baseline сохраняет принятую DB/peer/runtime/foreign equality.
2. Все фактически необходимые оператору Spain devices имеют актуальное
   acceptance evidence; неизвестные client facts явно перечислены.
3. Spain прошла минимум 14 последовательных суток наблюдения после последней
   затрагивающей dataplane mutation без critical incident или unexplained
   drift. Любая новая dataplane mutation перезапускает окно.
4. Создан encrypted full recovery backup, проверены checksum, secret inventory,
   retention и documented restore inputs.
5. Full restore выполнен на отдельной trusted disposable среде либо на новом
   rollback target; простой backup без restore rehearsal недостаточен.
6. Есть rollback target, физически независимый от Spain, либо оператор отдельно
   принимает документированный риск отсутствия независимого failover. По
   умолчанию отсутствие такого target означает `not_ready`.
7. Read-only audit доказывает отсутствие активных users/configs/peers/traffic,
   DNS, monitoring, automation или recovery dependencies, которые существуют
   только на USA.
8. Подготовлен secret-safe retirement plan: backup retention, credential/key
   rotation, provider records, monitoring removal и recoverable data-erasure
   boundary.
9. Выполнен final read-only USA/Spain audit и получено отдельное exact approval
   на destructive disable/cleanup/reuse operation.

Когда пункты 1–8 подтверждены и пункт 9 готов к approval, AMN2 обязан сообщить
оператору точную фразу:

```text
USA МОЖНО БЕЗОПАСНО ОТКЛЮЧАТЬ И ПЕРЕПРОФИЛИРОВАТЬ ПОСЛЕ ОТДЕЛЬНОГО EXACT APPROVAL
```

До этой фразы состояние всегда сообщается как:

```text
USA ПОКА НЕЛЬЗЯ ОТКЛЮЧАТЬ: ROLLBACK CONTOUR ЕЩЁ НЕ ЗАМЕНЁН ИЛИ НЕ ПРИНЯТ
```

Фраза readiness не является approval на shutdown, wipe или reuse.

## 11. Security model

Основные threats и controls:

| Threat | Required control |
|---|---|
| version spoof/downgrade | exact normalized version plus evidence-bound admission |
| OS-only AWG3 selection | fail closed without exact application/build |
| forged/stale evidence | append-only IDs, timestamps, status and audit |
| AWG3 secret leakage | encrypted/external reference, fingerprints only |
| AWG2/AWG3 config mixing | separate typed models/renderers and golden negatives |
| port/interface/CIDR collision | deterministic planner plus read-only live preflight |
| rollback deletes AWG2 | exact runtime ownership and no wildcard cleanup |
| stale observations trigger writes | read-only Drift; no auto-remediation |
| premature USA retirement | mandatory readiness checklist and exact notification |

## 12. TDD acceptance inventory for the later plan

The later implementation plan must start with failing tests for:

- exact AWG2/AWG3 enum validation;
- `NULL` legacy rows rejected for new issuance;
- unknown/unverified/stale client evidence rejected before secret generation;
- official release claim alone not sufficient for AWG3 admit;
- runtime-not-accepted blocks AWG3;
- AWG2 renderer rejects every AWG3-only field;
- AWG3 renderer requires a secret reference without exposing raw material;
- exact request fingerprint and idempotent retry/mismatch behavior;
- passport/receipt protocol consistency;
- runtime port/interface/CIDR conflicts;
- existing Spain AWG2 d1–d7 non-regression;
- read-only Drift no-mutation and new reason taxonomy;
- rollback scope selects only AWG3 candidate;
- USA retirement readiness remains false when any prerequisite is absent.

No test may stop, restart or recreate current AWG2 merely to prove isolation.

## 13. Phase 13 sequencing after written-spec review

1. TDD implementation plan for version admission and local models.
2. Local-only code/tests, diff/secret/security review, docs sync, commit/push.
3. Checksum-bound isolated runtime package design and preflight.
4. Separate live gates for AWG3 candidate and real-device matrix.
5. Device Passport/Desired/Observed/Drift enrichment for actual Spain slots.
6. Separate quota policy decision: recipient/plan-specific or approved default.
7. USA retirement/reuse readiness evaluation; no automatic retirement.

---

# English contract summary

## Decision

AMN2 will model AWG2 and AWG3 as explicit protocol versions and will introduce
a first-class `VpnRuntimeInstance` below a physical server. The accepted Spain
AWG2 runtime and d1–d7 remain unchanged. AWG3 is an isolated candidate with its
own interface, UDP port, CIDR, runtime identity, evidence and rollback scope.

This specification is design-only. It authorizes no implementation or live
Spain/USA/AWG action.

## Admission contract

Every new issuance request must provide the exact client application,
platform and version/build. Protocol selection never follows from the OS or
the phrase “latest version”. Unknown, unverified, stale or failed evidence is
fail-closed and does not silently fall back to AWG2.

An official release claim creates `claimed` compatibility evidence only. AWG3
requires an accepted server runtime plus passed import and full-data evidence
for the exact client/platform/build row.

New issuance supports only `awg2` and `awg3`. Historical unclassified rows may
remain `NULL` and read-only; they are not a third issuance target. The accepted
Spain d1–d7 rows may be explicitly classified as AWG2 from Phase 12 evidence,
without changing config bytes, peers or keys.

## Runtime isolation

`vpn_runtime_instances` binds protocol version, exact runtime build, interface,
UDP port, CIDR, service/container/config identities, lifecycle state and a
secret-free acceptance receipt to one physical server. Host-local interface
and port identities are unique; CIDR overlap is rejected by one deterministic
planner and rechecked by a read-only live preflight.

AWG2 and AWG3 use different typed renderers. `HeaderProtectionKey` is
secret-bearing server/client material and may appear only through an
encrypted/external secret reference. Safe metadata contains a fingerprint,
never the raw value.

## Passport and drift

Device Passport and issuance receipts bind protocol, runtime instance, client
identity evidence and compatibility evidence before configuration generation.
Desired/Observed/Drift remains read-only and adds protocol/runtime/evidence
mismatch reasons without auto-remediation.

## Live and rollback gates

Future AWG3 work requires local TDD, a checksum-bound package, a read-only
Spain conflict/equality preflight, exact approval, isolated deployment,
Windows/Android/iOS real-device evidence, controlled reboot persistence and an
independent rollback rehearsal. Rollback targets one exact AWG3 runtime
instance and must prove that AWG2, DB, web, bot, USA and the foreign Spain
service are unchanged.

## USA retirement notification

USA remains the rollback contour until Spain stability, required device
acceptance, a 14-day post-mutation observation window, encrypted backup,
independent full restore rehearsal, replacement rollback capacity, dependency
audit and a secret-safe retirement plan have all passed. Readiness produces an
explicit notification but never authorizes shutdown, wiping or reuse; those
actions require a separate exact approval.

## Next gate

After operator review of this written specification, create a separate TDD
implementation plan. Do not implement or prepare a live package from the
design approval alone.
