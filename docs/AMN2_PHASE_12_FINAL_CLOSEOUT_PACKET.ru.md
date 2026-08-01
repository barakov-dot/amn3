# AMN2 Phase 12 — final closeout packet

Дата принятия: 2026-08-01.

## Решение

Phase 12 Spain Migration полностью принята. Spain становится primary runtime.
Повторять preflight runs 001–009, install/recovery chain, controlled reboot или
issuance Phase 12 запрещено.

## Authoritative identities

- AMN2 source: `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
- Spain operational overlay:
  `f1bf099ddb47da26a4080714376babaf5b0de92c`.
- USA production overlay:
  `0b858c5cdbc5b565cc265966a2edfe2d339d65e0`.
- Final install package SHA-256:
  `9F56EFDDBFAF8F3768112EED0B4AE3CA6A94178B7824A54FF10282FE572906D0`,
  `140093440` bytes.
- Manifest SHA-256:
  `72061B9FD7F25B9661BCA49654CA3A08E7428F44E838D13BC7FFC9D9135D36C0`.
- Executor SHA-256:
  `0A20AA67D75FDAF2AB3AE4DD59ED4AC6AA916CCCB4407A72CD6CFCEF8E335DF9`.

## Accepted live state

Final live-audit receipt SHA-256:
`B1F12A5A18871C82F855F17CDC60ABA133B542CF2B68CF049AE64E533761F0C5`.

- DB integrity `ok`; foreign-key issues `0`.
- Users `1`; active/indefinite devices `7/7`.
- Issuance requests `2`; completed/noncompleted receipts `7/0`.
- Active passports `7`.
- DB/persistent/live peers `7/7/7`, exact peer-set equality.
- AWG running; restart count `59` стабилен; container IP forwarding `1`.
- Docker/network/forward-compat/web active; forward-compat enabled.
- Ровно три approved AMN2-tagged forward rules.
- Bot inactive; web только `127.0.0.1:3031`.
- Controlled reboot persistence passed.
- `ARM-HOME ПОСЛЕ REBOOT: FULL DATA РАБОТАЕТ` подтверждено оператором.

## Config issuance

Recipient `SooL`, indefinite slots:

1. Проектор — d1.
2. Телевизор — d2.
3. ARM-HOME — d3.
4. ARM-WORK — d4.
5. NOTEBOOK — d5.
6. IPAD — d6.
7. IPHONE — d7.

Request `phase12-spain-sool-remaining-20260801-002` выдал только d4–d7.
Одноразовый `MAX_DEVICES_PER_USER=7` применялся только к issuance process;
`runtime.env` не изменялся, runtime default остаётся `5`. AWG не
перезапускался и не пересоздавался. Девять exact checksum-verified remote
staging files удалены после подтверждённого download/package.

Remaining-package receipt SHA-256:
`1B3650EBBDF47E324071C14D7FBDF4913DB182149717A0C13EC6D6B854B2D5CA`.
Double build и independent verify byte-equal. Каждый уникальный outer ZIP
содержит byte-equal `NEOBYATNAYA.NET.conf` и secret-free manifest:

- ARM-WORK d4: `4492B5BF1B33524FF62C486276702881B86B6D3F035CF55650340BA90328CC63`.
- NOTEBOOK d5: `64F2706A295C4B0FCF60C5DCDCA98E0DDA53EBE9DEE407886F27B2707FB9D337`.
- IPAD d6: `56A2F1DFE50FC3A937615F777FCE9E3E2A030C76AA412C05F166B6F171557202`.
- IPHONE d7: `377A7BC7A3D69391A20F8F99E9D08162C9D2BBEA070532654778186176BFBD50`.

Полный AmneziaVPN не выводит display name из inner filename: после импорта
оператор вручную переименовывает профиль в exact `NEOBYATNAYA.NET`. Конфиги,
peers и ключи для имени не регенерируются.

## Equality receipt постороннего Spain-сервиса

- Collector SHA-256:
  `8B49104E1DB25F9505251930CD92E18FC13A7127796705C09C1ED3C3CE8CCC54`.
- Post-remaining evidence SHA-256:
  `5C99B0E669A2B267624B534F00FC05E2F101636A7EEC9D36AA9022855A388583`.
- Equality receipt SHA-256:
  `BC9065B3FA7CAB40F5EEFEBBFD8093F2D62477E972777FE665E8D9F6028AA704`.
- Before/after entries: `154/153`.
- Persistent entries: `153`; changed persistent entries: `0`.
- Persistent before/after SHA-256:
  `F5767F361A9441DD4B5361C07DA164A3059E0D1347D5217594534797D367B7E8`.
- Volatile before/after: `1/0`.

Посторонний Spain-сервис не останавливался и не изменялся.

## USA rollback contour

USA остаётся неизменённым rollback contour на всём протяжении Phase 13, пока
не будет отдельного evidence-backed решения и exact approval. USA users,
configs и peers не переносились, не удалялись и не отключались.

## Остаток продуктового плана

### Критичные

- Эксплуатировать Spain как primary и контролировать AWG/dataplane/foreign
  equality без повторения rollout.
- Первый Phase 13 product slice: Device Passport assignment и объяснимый
  Desired/Observed/Drift на фактических семи slots.

### Очень важные

- Per-device disable/revoke и полный recipient-slot lifecycle.
- Принять постоянную quota policy: recipient/plan-specific либо новый default;
  текущий runtime default остаётся `5`.
- Privacy-safe health/support и backup/restore rehearsal.

### Важные

- Secret-safe config lifecycle и bounded fleet readiness.
- Формализовать условия и срок сохранения/вывода USA rollback contour.

### Средние

- Bot cutover, public/self-service и 60-minute monitoring — только отдельными
  design и live approvals в Phase 13.

### Простые

- Operator UX для раздачи per-slot ZIP и ручного AmneziaVPN rename.

### Косметические

- Терминология, подписи и презентационное выравнивание без изменения runtime.

## Phase 13

Точный полный первый текст нового task «ФАЗА 13 — ПРОДОЛЖЕНИЕ ДОРАБОТОК
AMN2» находится в
`docs/AMN2_PHASE_13_POST_MIGRATION_CONTINUATION_FIRST_MESSAGE.ru.md`.
