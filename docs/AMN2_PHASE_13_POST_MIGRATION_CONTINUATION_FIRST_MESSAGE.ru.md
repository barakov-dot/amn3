# ФАЗА 13 — ПРОДОЛЖЕНИЕ ДОРАБОТОК AMN2

Ниже приведён точный полный первый текст нового task без placeholders.

```text
AMN2_PHASE_13_POST_MIGRATION_CONTINUATION_START

Продолжаем AMN2 после полностью принятой Phase 12 Spain Migration.
Рабочая папка: C:\Users\SooL\Documents\VPS-OPS-LAB

Сначала прочитай и исполняй как обязательный contract:
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/AMN2_PHASE_12_FINAL_CLOSEOUT_PACKET.ru.md
- docs/AMN2_PHASE_12_SPAIN_OPERATOR_ADOPTION_RECEIPT.ru.md
- docs/AMN2_PHASE_13_POST_MIGRATION_CONTINUATION_FIRST_MESSAGE.ru.md
- research/amn2/phase13-awg2-awg3-readiness-gate-2026-08-01.md
- текущие ideas/priority-backlog.md и research/amn2 evidence

Phase 12 не повторять. Runs 001–009, Spain preflight, install/recovery chain,
controlled reboot, ARM-HOME full-data acceptance и config issuance закрыты.

Authoritative AMN2 source:
55dc243b8e6c6bdb57f8301b56326e4cd4072d19
Authoritative Spain operational overlay:
f1bf099ddb47da26a4080714376babaf5b0de92c
USA production overlay:
0b858c5cdbc5b565cc265966a2edfe2d339d65e0

Spain — primary runtime. USA не изменялась и остаётся rollback contour до
отдельного exact решения Phase 13; USA users/configs/peers не переносить, не
удалять и не отключать. Посторонний Spain-сервис не останавливать и не
изменять; foreign persistent equality обязательна после каждой затрагивающей
Spain операции.

Accepted Spain state: users 1; active indefinite devices 7; completed receipts
7; active passports 7; persistent/live peers 7/7 exact. Recipient SooL:
Проектор, Телевизор, ARM-HOME, ARM-WORK, NOTEBOOK, IPAD, IPHONE. AWG running,
restart count 59 stable, container net.ipv4.ip_forward=1, ровно три
AMN2-tagged forward rules, forward-compat active/enabled, bot disabled, web
только 127.0.0.1:3031. ARM-HOME full data после controlled reboot работает.
Не останавливать, не перезапускать и не пересоздавать AWG для тестов.

Финальный Phase 12 foreign equality receipt SHA-256:
BC9065B3FA7CAB40F5EEFEBBFD8093F2D62477E972777FE665E8D9F6028AA704
Persistent entries 153, changed 0, stable before/after SHA-256:
F5767F361A9441DD4B5361C07DA164A3059E0D1347D5217594534797D367B7E8

AmneziaVPN после импорта требует ручной rename профиля в exact
NEOBYATNAYA.NET; не регенерировать конфиги, peers или ключи ради имени.
Одноразовый issuance override MAX_DEVICES_PER_USER=7 не менял runtime.env;
текущий default остаётся 5. В Phase 13 отдельно принять продуктовую политику
quota: recipient/plan-specific либо новый согласованный default.

Текущий Spain runtime и семь выданных профилей — принятый AWG2 baseline.
Существующие d1–d7 не перевыпускать автоматически. Официальные AmneziaVPN
5.0.0.5 и DefaultVPN 2.0.0 уже заявляют AWG3 support, но Spain ещё не имеет
принятого AWG3 server runtime/config/data evidence. До отдельного gate
production issuance остаётся AWG2-only.

Целевая новая выдача AMN2 — AWG2 и AWG3; новую AWG1/legacy выдачу не
развивать, существующие legacy-профили не удалять. Перед каждой новой выдачей
обязательно запросить точное приложение, платформу и версию клиента. AWG3 не
выбирать только по ОС или словам «последняя версия». Unknown/unverified client
version должна fail closed до upgrade или compatibility check.

Не преобразовывать AWG2-конфиги добавлением AWG3-полей и не обновлять текущий
Spain AWG вслепую. Первый AWG3 slice проектирует отдельный version-admission
contract и изолированный runtime/interface/UDP-port candidate с собственными
IPAM, port-conflict, data, reboot и rollback gates. Текущий AWG2, USA contour и
посторонний Spain-сервис остаются нетронутыми.

North star Phase 13: safe lifecycle control plane — Device Passport,
recipient/slot assignment, explainable Desired/Observed/Drift, per-device
disable/revoke, privacy-safe health/support, backup/restore и bounded fleet
readiness. Сначала переоценить backlog по фактической Spain эксплуатации; не
копировать upstream panels и не открывать public/self-service, bot cutover или
broad write surfaces без отдельного design и exact live approval.

Первое действие без live mutation:
GPT-5.6 SOL -> REVIEW_PHASE13_AWG2_AWG3_VERSION_ADMISSION_AND_ISOLATED_RUNTIME_DESIGN_GATE -> VERIFY_CURRENT_SPAIN_AWG2_BASELINE_AND_OFFICIAL_AWG3_CONTRACTS -> WRITE_BILINGUAL_DESIGN_SPEC -> PREPARE_EXACT_DESIGN_APPROVAL_PHRASE

После утверждения AWG2/AWG3 design отдельно написать TDD implementation plan и
только затем готовить checksum-bound live gate. Device Passport и
Desired/Observed/Drift продолжить следом, добавив protocol version, client
application/version и compatibility evidence к фактическим семи Spain slots.

Работай в /GO: product/engineering evidence -> scoped tests -> diff/secret/
security review -> docs/status sync -> commit -> push -> exact live approval.
Не трогай посторонние изменения и
docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md.

Всегда заканчивай вариантами: Одиночная, Двойная, Тройная, Четверная,
Более — рекомендовано; план и остаток работ показывай по критичности:
критичные, очень важные, важные, средние, простые и косметические.
```
