# AMN2 Phase 12 Spain Migration — first message

Copy the block below as the first message in a new Codex task:

```text
AMN2_PHASE_12_SPAIN_MIGRATION_START

Продолжаем AMN2: Phase 12 Spain Migration.
Рабочая папка: C:\Users\SooL\Documents\VPS-OPS-LAB

Сначала прочитай и исполняй как обязательный contract:
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/AMN2_PHASE_11_FINAL_CLOSEOUT_PACKET.ru.md
- docs/POST_RELEASE_SPAIN_PREFLIGHT_RUN_009_SUCCESS_EVIDENCE.ru.md
- docs/AMN2_PHASE_12_SPAIN_MIGRATION_ENTRY.ru.md
- docs/NEXT_CHAT_AMN2_PHASE_12_SPAIN_MIGRATION.ru.md
- docs/superpowers/specs/2026-07-19-spain-fresh-admin-config-issuance-design.ru.md
- docs/superpowers/plans/2026-07-19-spain-fresh-admin-config-issuance.md

Phase 11 и Spain read-only preflight закрыты. Runs 001–009 не повторять.
Spain preflight 009 passed; evidence SHA-256:
8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8.

AMN2 source: 55dc243b8e6c6bdb57f8301b56326e4cd4072d19.
USA production overlay: 0b858c5cdbc5b565cc265966a2edfe2d339d65e0.
Spain имеет посторонний сервис: не изменять; fingerprint до/после обязан
совпасть. Заняты TCP 22/53/443/8080/10050 и UDP 53/443. Docker отсутствует.

Делаем fresh install и clean DB. Старые USA configs/users/peers не переносим и
не удаляем. USA остаётся rollback contour. Не останавливай AWG для тестов.
Новые конфиги: NEOBYATNAYA.NET — recipient — slot/device. Device может быть
неизвестен; допускаются несколько активных slots одному получателю; default
expiry indefinite, срок задаётся только явно. Я передаю список получателей и
количество одним сообщением, конфиги раздаю самостоятельно.

Работай в /GO режиме до каждого отдельного exact live approval:
product/engineering evidence -> scoped/full tests -> diff/security review ->
docs/status sync -> commit -> push -> exact approval.
Не трогай посторонние изменения и
docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md.

Первое действие без SSH/mutation:
GPT-5.6 SOL -> REVIEW_PHASE12_SPAIN_CONFLICT_FREE_RESOURCE_AND_INSTALL_ROLLBACK_DESIGN -> PREPARE_CHECKSUM_BOUND_INSTALL_PACKAGE_WITH_UNRELATED_FINGERPRINT_EQUALITY

Всегда заканчивай вариантами: Одиночная, Двойная, Тройная, Четверная,
Более — рекомендовано; план показывай по критичности.
```
